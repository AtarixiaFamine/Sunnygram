# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Deciding which updates a handler wants.

A filter is a question asked of what arrived, and questions combine. & is both,
| is either, ~ is not, and the result is another filter, so a handler's
condition reads as one line instead of four lines of ifs at the top of the
callback:

    @client.on_message(filters.private & filters.text & ~filters.outgoing)

Writing one is a function taking what arrived and answering true or false. It
may be async when deciding needs the network.

Most of these are written for messages, and not all of them answer about
anything else. Which ones apply to what, since the alternative is finding out
from a handler that never runs:

    text, media, photo, video, audio, voice, document, sticker, service,
    forwarded, reply, outgoing, incoming    a message, and nothing else
    user, chat, me, bot, private, group, channel   anything that says who and
                                                   where: a message, a press
    regex, command                          anything with text, which includes
                                            a press, whose text is its payload
    data                                    a press
    query                                   an inline query

A filter asked about something it has no opinion on says no. It does not raise,
because a filter runs on updates its own handler never sees, so one that raised
would report a fault about an update nobody wanted. No is the honest answer to
"is this a photo" when the thing is a typing notification.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Awaitable, Callable
from typing import Any

from .raw import types

__all__ = [
    "Filter",
    "audio",
    "bot",
    "channel",
    "chat",
    "command",
    "data",
    "document",
    "everything",
    "forwarded",
    "group",
    "incoming",
    "make",
    "me",
    "media",
    "nothing",
    "outgoing",
    "photo",
    "private",
    "query",
    "regex",
    "reply",
    "service",
    "sticker",
    "text",
    "user",
    "video",
    "voice",
]

# What a filter is asked about. Any rather than Message because a handler can
# be given a dozen other things and the filters about who and where answer for
# most of them: the duck typing was always real, and only the annotation was
# claiming otherwise.
Predicate = Callable[[Any, Any], bool | Awaitable[bool]]


class Filter:
    """A question about what arrived, which combines with other questions."""

    __slots__ = ("_test", "_name")

    def __init__(self, test: Predicate, name: str = "filter") -> None:
        self._test = test
        self._name = name

    def __repr__(self) -> str:
        return self._name

    async def __call__(self, client: Any, event: Any) -> bool:
        answer = self._test(client, event)
        if inspect.isawaitable(answer):
            return bool(await answer)
        return bool(answer)

    def __and__(self, other: Filter) -> Filter:
        async def both(client: Any, event: Any) -> bool:
            return await self(client, event) and await other(client, event)

        return Filter(both, f"({self._name} & {other._name})")

    def __or__(self, other: Filter) -> Filter:
        async def either(client: Any, event: Any) -> bool:
            return await self(client, event) or await other(client, event)

        return Filter(either, f"({self._name} | {other._name})")

    def __invert__(self) -> Filter:
        async def negated(client: Any, event: Any) -> bool:
            return not await self(client, event)

        return Filter(negated, f"~{self._name}")


def make(test: Predicate, name: str | None = None) -> Filter:
    """Build a filter out of a function, sync or async.

    A filter written here is the program's own, so it is not wrapped in the
    guard the built-in ones have: one that raises is a fault in the program and
    is reported as one instead of quietly counting as a no.
    """
    return Filter(test, name or str(getattr(test, "__name__", "filter")))


def _simple(name: str, test: Callable[[Any], bool]) -> Filter:
    """A built-in filter, which answers no about things it cannot read.

    Every one of these reads fields off whatever it was handed, and half of
    them only exist on a message. Asking one about a typing notification is not
    a fault to report, it is a question with an obvious answer, so a missing
    field is no instead of an exception on an update no one asked for.
    """

    def guarded(client: Any, event: Any) -> bool:
        try:
            return test(event)
        except AttributeError:
            return False

    return Filter(guarded, name)


def _leave(event: Any, name: str, value: Any) -> None:
    """Put what a filter worked out where the handler will look for it.

    A message has somewhere to keep a command and a match; most of the other
    shapes keep only the match, and a few keep neither because they are frozen
    records with nothing to say about text. Whether the pieces can be left
    behind does not change the answer to the question, so this does not fail.
    """
    try:
        setattr(event, name, value)
    except AttributeError:
        pass


everything = _simple("everything", lambda message: True)
nothing = _simple("nothing", lambda message: False)

text = _simple("text", lambda message: bool(message.text) and not message.service)
service = _simple("service", lambda message: message.service)
media = _simple("media", lambda message: message.has_media)
reply = _simple("reply", lambda message: message.reply_to_id is not None)
forwarded = _simple(
    "forwarded", lambda message: getattr(message.raw, "fwd_from", None) is not None
)

outgoing = _simple("outgoing", lambda message: message.outgoing)
incoming = _simple("incoming", lambda message: not message.outgoing)
me = _simple("me", lambda message: bool(message.sender and message.sender.is_self))
bot = _simple("bot", lambda message: bool(message.sender and message.sender.is_bot))

private = _simple(
    "private", lambda message: bool(message.chat and message.chat.is_private)
)
group = _simple("group", lambda message: bool(message.chat and message.chat.is_group))
channel = _simple(
    "channel", lambda message: bool(message.chat and message.chat.is_channel)
)


def _media_is(name: str, *kinds: type) -> Filter:
    def test(message: Any) -> bool:
        return isinstance(message.media, kinds)

    return _simple(name, test)


photo = _media_is("photo", types.MessageMediaPhoto)


def _document_with(name: str, attribute: type | None) -> Filter:
    """A document filter, told apart by the attributes Telegram hangs on one.

    Everything that is not a photo is a document, and what kind of document it
    is lives in the attribute list: a video has a video attribute, a voice note
    has an audio attribute with the voice flag on. That is why these read as
    they do rather than as a type check.
    """

    def test(message: Any) -> bool:
        if not isinstance(message.media, types.MessageMediaDocument):
            return False
        document = message.media.document
        if not isinstance(document, types.Document):
            return False
        if attribute is None:
            return True
        for held in document.attributes:
            if not isinstance(held, attribute):
                continue
            if isinstance(held, types.DocumentAttributeAudio):
                # A voice note and a song are the same attribute with one
                # flag between them.
                if name == "voice":
                    return bool(held.voice)
                if name == "audio":
                    return not held.voice
            return True
        return False

    return _simple(name, test)


document = _document_with("document", None)
video = _document_with("video", types.DocumentAttributeVideo)
audio = _document_with("audio", types.DocumentAttributeAudio)
voice = _document_with("voice", types.DocumentAttributeAudio)
sticker = _document_with("sticker", types.DocumentAttributeSticker)


def command(
    name: str | list[str], *, prefixes: str = "/", to_me: bool = False
) -> Filter:
    """Messages that start with a command, with the arguments split out.

    A match leaves the pieces on the message as command and arguments, so a
    handler reads them instead of parsing the text again. to_me limits it to
    the form addressed to a particular bot, which is what a command in a group
    looks like when more than one bot is in it.
    """
    wanted = {name} if isinstance(name, str) else set(name)

    def test(client: Any, event: Any) -> bool:
        body = getattr(event, "text", None)
        if not body or body[0] not in prefixes:
            return False
        head, _, rest = body[1:].partition(" ")
        spoken, _, addressed = head.partition("@")
        if spoken.lower() not in {word.lower() for word in wanted}:
            return False
        if to_me and not addressed:
            return False
        # Left on the message instead of returned, since a filter can only
        # answer yes or no and the handler wants the pieces either way.
        _leave(event, "command", spoken)
        _leave(event, "arguments", rest.split() if rest else [])
        return True

    return Filter(test, f"command({sorted(wanted)})")


def data(*payloads: str, prefix: str = "") -> Filter:
    """Button presses carrying one of these payloads, or starting with a prefix.

    The payload is what the button was built with, so this is how a handler
    says which button it is for. Naming payloads matches them exactly; a prefix
    matches anything starting with it, which is how a bot packs an argument in
    after a separator and reads it back off the press.
    """
    wanted = set(payloads)

    def test(client: Any, press: Any) -> bool:
        found = getattr(press, "text", "")
        if not found:
            return False
        if wanted and found in wanted:
            return True
        return bool(prefix) and found.startswith(prefix)

    return Filter(test, f"data({sorted(wanted) or prefix!r})")


def regex(pattern: str | re.Pattern[str], *, flags: int = 0) -> Filter:
    """Text that matches, with the match left on what was asked about.

    Works on anything that has text: a message, a button press whose text is
    the payload it was built with, an inline query whose text is what is being
    typed. The match object is left on it, so a handler reads the groups
    rather than running the pattern a second time.
    """
    compiled = re.compile(pattern, flags) if isinstance(pattern, str) else pattern

    def test(client: Any, event: Any) -> bool:
        body = getattr(event, "text", None)
        if not body:
            return False
        found = compiled.search(body)
        if found is None:
            return False
        _leave(event, "match", found)
        return True

    return Filter(test, f"regex({compiled.pattern!r})")


def query(*starts: str, empty: bool = False) -> Filter:
    """Inline queries, by what has been typed so far.

    Naming nothing matches every query, which is how a bot answers whatever
    someone types. Naming words matches a query beginning with any of them,
    case insensitively, which is how one bot offers several kinds of answer
    from one place.

    empty is the other question worth asking, and it is a different one: it
    matches the query with nothing typed after the bot's name yet, which is the
    panel a person sees before they have said what they want. That is where a
    bot puts its suggestions, and a handler for it should be separate from the
    one that searches, since searching for the empty string is not what
    anybody meant.
    """
    wanted = tuple(word.lower() for word in starts)

    def test(client: Any, asked: Any) -> bool:
        body = getattr(asked, "text", None)
        if not isinstance(body, str):
            return False
        if empty:
            return not body.strip()
        if not wanted:
            return True
        return body.lower().startswith(wanted)

    return Filter(test, f"query({list(wanted) or ('empty' if empty else 'any')})")


def user(*who: int | str) -> Filter:
    """Messages from any of these people, by id or by username."""
    ids = {one for one in who if isinstance(one, int)}
    names = {one.lstrip("@").lower() for one in who if isinstance(one, str)}

    def test(message: Any) -> bool:
        sender = message.sender
        if sender is None:
            return False
        if sender.id in ids:
            return True
        return bool(sender.username and sender.username.lower() in names)

    return _simple(f"user({sorted(ids | names, key=str)})", test)


def chat(*where: int | str) -> Filter:
    """Messages in any of these chats, by id or by username."""
    ids = {one for one in where if isinstance(one, int)}
    names = {one.lstrip("@").lower() for one in where if isinstance(one, str)}

    def test(message: Any) -> bool:
        found = message.chat
        if found is None:
            return False
        if found.id in ids:
            return True
        return bool(found.username and found.username.lower() in names)

    return _simple(f"chat({sorted(ids | names, key=str)})", test)
