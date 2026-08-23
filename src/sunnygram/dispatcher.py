# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Getting an update to the code that wants it.

An update arrives as a raw constructor with ids in it. A program wants a message
it can answer. In between sits this: turn the update into the friendly shape,
ask each handler's filter whether it wants it, and call the ones that do.

Handlers live in numbered groups and run in group order, and within a group in
the order they were added. Every handler that matches runs, which lets two
independent features live in one program without either knowing about the other.
A handler that wants the last word raises StopPropagation.

The other behaviour is available: first_match stops a group after the first
handler in it whose filter said yes. It suits handlers that are a list of
commands, where two matching one message is a mistake. It is off by default
because the failure it produces is silent, and a handler that never runs is
harder to find than one that runs twice.

A handler that raises does not stop the stream, but it is said out loud. Nothing
above this layer will ever see that exception, so an unhandled one is logged
with its traceback under the sunnygram logger, which reaches stderr with no
logging configured at all. Set on_error to take it over.

Dispatch is sequential on purpose. Updates arrive in an order that means
something, two messages in the same chat above all, and handing them to tasks
would throw that away. A handler with slow work to do should start its own task
and let the stream carry on.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal, get_args

from .errors import SunnygramError
from .filters import Filter
from .raw import types
from .types import (
    Blocked,
    CallbackQuery,
    ChosenResult,
    DeletedMessages,
    InlineQuery,
    JoinRequest,
    MemberUpdate,
    Message,
    Poll,
    PollVote,
    PreCheckoutQuery,
    ReactionUpdate,
    ShippingQuery,
    Status,
    Story,
    Stopped,
    Typing,
)
from .updates import Event

__all__ = [
    "KINDS",
    "AlbumCollector",
    "Dispatcher",
    "Handler",
    "Kind",
    "Listening",
    "StopPropagation",
]

_log = logging.getLogger(__name__)

Callback = Callable[[Any, Any], Awaitable[None]]

# Every kind of reading a handler can ask for. Spelled as a Literal rather than
# as str because the failure it prevents is the silent one: a handler
# registered for "calback" is not an error anywhere, it is a handler that never
# runs, and finding that takes an afternoon. With this, mypy says so.
Kind = Literal[
    "raw",
    "message",
    "edited",
    "scheduled",
    "album",
    "callback",
    "inline_query",
    "chosen_result",
    "chat_member",
    "join_request",
    "deleted",
    "reaction",
    "poll",
    "poll_vote",
    "shipping",
    "pre_checkout",
    "story",
    "status",
    "typing",
    "blocked",
    "stopped",
]

# The same list at runtime, for anything that has to check a kind it was handed
# instead of one it was written with.
KINDS: tuple[str, ...] = get_args(Kind)

# How long to wait for the rest of an album after a part of one arrives. The
# parts are sent in one call and arrive together, so this only has to cover the
# gap between updates on the same connection, and a wait long enough to be felt
# is worse than occasionally splitting a group.
ALBUM_WAIT = 0.3

# Bounds on what is held while waiting (rule P6). Ten is what Telegram allows in
# a group, and a client seeing many groups at once is a client being flooded.
ALBUM_PARTS = 10
ALBUM_GROUPS = 64

# How many questions may be outstanding at once (rule P6). A conversation holds
# a slot only while it is actually waiting, so this is the number of people
# being asked something at the same moment, not the number of chats a program
# knows. A program that reaches this is either very popular or has a leak, and
# the difference is worth having to say out loud instead of discovering as
# memory.
LISTENING = 256


class StopPropagation(Exception):
    """Raised by a handler that wants nothing after it to run."""


@dataclass(slots=True)
class Handler:
    """One callback, what it wants, and when it runs."""

    callback: Callback
    kind: Kind = "message"
    filters: Filter | None = None
    group: int = 0

    def __repr__(self) -> str:
        name = getattr(self.callback, "__name__", "callback")
        return f"Handler({name} on {self.kind}, group {self.group})"


@dataclass(slots=True)
class Listening:
    """One question waiting for its answer.

    A handler is a standing offer to deal with anything of a kind. This is the
    other shape a program wants: one thing, from one chat, once, at a point in
    the code that already knows what it asked. It is usually called a
    conversation, it is a common thing to want, and the
    reason it is worth having natively is that everything it needs is already
    here, one field at a time.

    The future is what the asking coroutine is waiting on. The deadline is not
    enforced here: whoever is waiting owns it, so a question that is never
    answered is cancelled by its own waiter and takes its record out on the way
    past. That keeps the table the size of the questions actually outstanding
    without anything having to sweep it.
    """

    chat_id: int
    kind: Kind
    filters: Filter | None
    future: asyncio.Future[Any]
    exclusive: bool = True

    def __repr__(self) -> str:
        return f"Listening(chat {self.chat_id}, {self.kind})"


class AlbumCollector:
    """Puts the parts of an album back together.

    Telegram sends an album as several ordinary messages that happen to share a
    group id, so a handler wanting the block rather than the pieces has to wait
    for the pieces to stop arriving. There is no marker for the last one, which
    is why this is a short silence instead of a count: the only thing that says
    an album is complete is nothing else turning up.

    The parts still reach message handlers on their own. Nothing is swallowed
    here, so a program written before albums existed keeps working and a
    program that wants them asks for them.
    """

    __slots__ = ("_wait", "_emit", "_parts", "_timers", "_dropped")

    def __init__(
        self,
        emit: Callable[[list[Message]], Awaitable[None]],
        *,
        wait: float = ALBUM_WAIT,
    ) -> None:
        self._wait = wait
        self._emit = emit
        self._parts: dict[int, list[Message]] = {}
        self._timers: dict[int, asyncio.Task[None]] = {}
        self._dropped = 0

    def __repr__(self) -> str:
        return f"AlbumCollector({len(self._parts)} waiting, {self._dropped} dropped)"

    @property
    def dropped(self) -> int:
        """Parts thrown away because too many arrived at once."""
        return self._dropped

    def add(self, message: Message) -> None:
        """Take one part, and restart the clock for its group."""
        group = message.album_id
        if group is None:
            return
        if group not in self._parts and len(self._parts) >= ALBUM_GROUPS:
            self._dropped += 1
            return

        held = self._parts.setdefault(group, [])
        if len(held) >= ALBUM_PARTS:
            self._dropped += 1
            return
        held.append(message)

        waiting = self._timers.get(group)
        if waiting is not None:
            waiting.cancel()
        self._timers[group] = asyncio.create_task(self._after_the_silence(group))

    async def _after_the_silence(self, group: int) -> None:
        try:
            await asyncio.sleep(self._wait)
        except asyncio.CancelledError:
            # Another part arrived, so this group is someone else's clock now.
            return
        parts = self._parts.pop(group, [])
        self._timers.pop(group, None)
        if parts:
            await self._emit(sorted(parts, key=lambda part: part.id))

    def close(self) -> None:
        """Stop waiting for anything, and let go of what is held."""
        for waiting in self._timers.values():
            waiting.cancel()
        self._timers.clear()
        self._parts.clear()


@dataclass(slots=True)
class Dispatcher:
    """The handlers a client holds, and the routing that feeds them."""

    handlers: list[Handler] = field(default_factory=list)
    errors: int = 0
    on_error: Callable[[BaseException, Handler], Any] | None = None
    albums: AlbumCollector | None = None
    first_match: bool = False
    # The handlers that could want each kind of reading, worked out once when
    # the list changes instead of walked in full on every update. A program
    # with a hundred commands and a raw watcher offers three readings per
    # update, and without this every one of them walks all hundred and one.
    _index: dict[str, tuple[Handler, ...]] = field(default_factory=dict, repr=False)
    _indexed: int = field(default=-1, repr=False)
    # The questions outstanding, oldest first, so two asks about the same chat
    # are answered in the order they were asked.
    _listening: list[Listening] = field(default_factory=list, repr=False)

    def add(self, handler: Handler) -> Handler:
        """Register a handler, keeping the list in the order it will run in."""
        self.handlers.append(handler)
        self.handlers.sort(key=lambda held: held.group)
        self._indexed = -1
        return handler

    def remove(self, handler: Handler) -> None:
        """Take a handler out again."""
        if handler in self.handlers:
            self.handlers.remove(handler)
            self._indexed = -1

    @property
    def listening(self) -> int:
        """How many questions are waiting for an answer right now."""
        return len(self._listening)

    def listen(
        self,
        chat_id: int,
        *,
        kind: Kind = "message",
        filters: Filter | None = None,
        exclusive: bool = True,
    ) -> Listening:
        """Wait for the next thing of a kind from one chat.

        Returns the record rather than the future, because the caller has to be
        able to take it out again when it stops waiting, and a caller that only
        held the future would have no way to.
        """
        if len(self._listening) >= LISTENING:
            raise SunnygramError(
                f"{LISTENING} questions are already waiting for an answer. "
                "Something is asking and not being answered; a conversation "
                "holds a place only while it waits, so this many at once is a "
                "leak rather than a busy program"
            )
        waiting = Listening(
            chat_id=chat_id,
            kind=kind,
            filters=filters,
            future=asyncio.get_running_loop().create_future(),
            exclusive=exclusive,
        )
        self._listening.append(waiting)
        return waiting

    def stop_listening(self, waiting: Listening) -> None:
        """Take a question out of the table, answered or not."""
        if waiting in self._listening:
            self._listening.remove(waiting)
        if not waiting.future.done():
            waiting.future.cancel()

    async def _answered(self, client: Any, kind: Kind, value: Any) -> bool:
        """Give this to whoever asked for it, and say whether anybody had.

        Consulted before the handlers, which is the part that has to be a
        decision instead of an accident: a message that answers a question is
        not also offered to ordinary handlers, because a program that asked
        "what should I call you" does not want its command router to see the
        name. That is what asking a question almost always means, and
        exclusive=False is there for the case that wants both.
        """
        if not self._listening:
            return False
        if getattr(value, "outgoing", False):
            # Our own message, coming back as the update the server makes of
            # every send. Answering a question with it would mean `ask` returned
            # the question: the send happens while the wait is already in place,
            # by design, so this is not an edge case but the ordinary path.
            return False
        chat_id = _chat_of(value)
        if chat_id is None:
            return False

        for waiting in list(self._listening):
            if waiting.kind != kind or waiting.chat_id != chat_id:
                continue
            if waiting.future.done():
                # Cancelled by its waiter a moment ago and not yet taken out.
                self._listening.remove(waiting)
                continue
            if waiting.filters is not None and not await waiting.filters(client, value):
                continue
            self._listening.remove(waiting)
            waiting.future.set_result(value)
            return waiting.exclusive
        return False

    def _wanting(self, kind: Kind) -> tuple[Handler, ...]:
        """The handlers registered for one kind of reading, in running order.

        The length is what says whether the index is still good. add and remove
        say so themselves, and the length catches the other way the list can
        change, which is someone reaching for the public field and appending to
        it. Cheaper than rebuilding, and it means the field stays honest rather
        than becoming a trap.
        """
        if self._indexed != len(self.handlers):
            index: dict[str, list[Handler]] = {}
            for handler in self.handlers:
                index.setdefault(handler.kind, []).append(handler)
            self._index = {name: tuple(held) for name, held in index.items()}
            self._indexed = len(self.handlers)
        return self._index.get(kind, ())

    async def feed(self, client: Any, event: Event) -> None:
        """Turn one update into something friendly and offer it around.

        The raw reading first in every case, so a program can watch everything
        and still act on the friendly shape the easy way, and then the friendly
        reading if this update has one.

        The friendly one is built only when someone asked for that kind.
        Wrapping a message costs about as much as decoding it did, and a
        program with one inline handler in it has no reason to pay that for
        every message that goes past. _wanting already knows who asked, so
        asking it first is the whole of the saving.
        """
        try:
            await self._offer(client, "raw", event)

            found = _READINGS.get(type(event.update))
            if found is None:
                return
            kind, build = found
            # The collector is the other thing that wants a message, and it
            # wants one whether or not any message handler exists, since an
            # album handler is registered for a different kind. A question
            # waiting for an answer is the third, and it is the reason this is
            # not simply "does anybody handle this kind": a program can be
            # waiting for a reply without having a single message handler in
            # it, and building nothing would leave it waiting for ever.
            if (
                not self._wanting(kind)
                and not self._listening
                and not (kind == "message" and self.albums is not None)
            ):
                return

            value = build(event, client)
            if value is None:
                return
            if kind == "message" and self.albums is not None:
                # Held as well as offered, not instead: the part is a message
                # like any other and the album is a second thing to say about
                # it, which arrives once the rest have stopped coming.
                self.albums.add(value)
            if await self._answered(client, kind, value):
                return
            await self._offer(client, kind, value)
        except StopPropagation:
            return

    def collect_albums(self, *, wait: float = ALBUM_WAIT) -> AlbumCollector:
        """Start putting albums back together, so album handlers can fire."""
        if self.albums is None:
            self.albums = AlbumCollector(self._album_arrived, wait=wait)
        return self.albums

    def close(self) -> None:
        """Let go of anything held between updates."""
        if self.albums is not None:
            self.albums.close()
        # Anybody still waiting is waiting for an update stream that has
        # stopped. Cancelling says so where they are waiting; leaving the
        # futures alone would hang them until their own timeout, with no
        # explanation and no client left to give one.
        for waiting in self._listening:
            if not waiting.future.done():
                waiting.future.cancel()
        self._listening.clear()

    async def _album_arrived(self, parts: list[Message]) -> None:
        client = parts[0].client
        try:
            await self._offer(client, "album", parts)
        except StopPropagation:
            return

    async def _offer(self, client: Any, kind: Kind, value: Any) -> None:
        # A filter answers questions about a message, and an album is a list of
        # them, so the filter is asked about the first: it is the part that
        # carries the caption, which is what a filter on an album is usually
        # looking at.
        asked = value[0] if kind == "album" else value
        # One reading, one kind of handler. A raw handler is not offered the
        # friendly reading as well as the raw one: it asked for the update as
        # it came, it is given that once, and the message inside it goes to the
        # handlers that asked for a message.
        answered: int | None = None
        for handler in self._wanting(kind):
            if self.first_match and answered == handler.group:
                # Someone earlier in this group has already taken it.
                continue
            try:
                if handler.filters is not None and not await handler.filters(
                    client, asked
                ):
                    continue
                # Counted as answered before it runs instead of after, so a
                # handler that matched and then failed still owns the update:
                # falling through to the next one would handle it twice, which
                # is the opposite of what asking for first_match meant.
                answered = handler.group
                await handler.callback(client, value)
            except StopPropagation:
                raise
            except asyncio.CancelledError:
                raise
            except Exception as failure:
                # One handler going wrong is not the others' problem, and it is
                # certainly not the update stream's: swallowing it here is what
                # keeps a typo in one feature from ending the program. A filter
                # is inside this for the same reason, and it is the more
                # important half: a filter runs on updates its handler never
                # sees, so one that raises would end the stream over a message
                # no one wanted.
                self.errors += 1
                if self.on_error is not None:
                    await _maybe(self.on_error(failure, handler))
                else:
                    # Swallowed is not the same as hidden. Nothing above this
                    # will ever see the exception, so if it is not said here it
                    # is not said anywhere, and a handler that quietly does
                    # nothing is the hardest kind of fault to find. Logging
                    # rather than printing leaves a program free to route or
                    # silence it, and an error reaches stderr on its own with
                    # no logging set up at all, which is the case that matters.
                    _log.exception(
                        "the %s handler %s raised",
                        handler.kind,
                        _name_of(handler.callback),
                        exc_info=failure,
                    )


def _message_of(event: Event, client: Any) -> Any:
    return _wrap(client, getattr(event.update, "message", None), event)


def _press_of(event: Event, client: Any) -> Any:
    return CallbackQuery.from_raw(
        event.update, users=event.users, chats=event.chats, client=client
    )


def _query_of(event: Event, client: Any) -> Any:
    return InlineQuery.from_raw(event.update, users=event.users, client=client)


def _chosen_of(event: Event, client: Any) -> Any:
    return ChosenResult.from_raw(event.update, users=event.users, client=client)


def _member_of(event: Event, client: Any) -> Any:
    return MemberUpdate.from_raw(event.update)


def _request_of(event: Event, client: Any) -> Any:
    return JoinRequest.from_raw(event.update, users=event.users, client=client)


def _deleted_of(event: Event, client: Any) -> Any:
    return DeletedMessages.from_raw(event.update)


def _reaction_of(event: Event, client: Any) -> Any:
    return ReactionUpdate.from_raw(event.update, client=client)


def _poll_of(event: Event, client: Any) -> Any:
    return Poll.from_raw(event.update, client=client)


def _vote_of(event: Event, client: Any) -> Any:
    return PollVote.from_raw(event.update)


def _status_of(event: Event, client: Any) -> Any:
    return Status.from_raw(event.update)


def _shipping_of(event: Event, client: Any) -> Any:
    return ShippingQuery.from_raw(event.update, client=client)


def _checkout_of(event: Event, client: Any) -> Any:
    return PreCheckoutQuery.from_raw(event.update, client=client)


def _story_of(event: Event, client: Any) -> Any:
    return Story.from_raw(getattr(event.update, "story", None))


def _typing_of(event: Event, client: Any) -> Any:
    return Typing.from_raw(event.update)


def _blocked_of(event: Event, client: Any) -> Any:
    return Blocked.from_raw(event.update)


def _stopped_of(event: Event, client: Any) -> Any:
    return Stopped.from_raw(event.update)


# Which friendly reading each update has, and how to build it. A table rather
# than a chain of isinstance checks: adding a kind is a row, and the lookup
# stops being linear in the number of kinds, which mattered the moment there
# were more than five of them.
#
# Keyed on the exact type because every update off the wire is exactly one
# generated constructor. Nothing subclasses them, so there is no family here
# that a chain would catch and a lookup would miss.
_READINGS: dict[type, tuple[Kind, Callable[[Event, Any], Any]]] = {
    types.UpdateNewMessage: ("message", _message_of),
    types.UpdateNewChannelMessage: ("message", _message_of),
    types.UpdateEditMessage: ("edited", _message_of),
    types.UpdateEditChannelMessage: ("edited", _message_of),
    # A message queued instead of sent. It is a message in every other way,
    # so it is wrapped the same, but it is deliberately its own kind: a
    # message handler firing for something no one has received yet would be
    # wrong, and the account's own client is what queued it.
    types.UpdateNewScheduledMessage: ("scheduled", _message_of),
    # A press on a message in a chat and a press on one an inline query
    # produced. They differ in how the message is named and in nothing else,
    # so they are one kind here.
    types.UpdateBotCallbackQuery: ("callback", _press_of),
    types.UpdateInlineBotCallbackQuery: ("callback", _press_of),
    types.UpdateBotInlineQuery: ("inline_query", _query_of),
    types.UpdateBotInlineSend: ("chosen_result", _chosen_of),
    types.UpdateChatParticipant: ("chat_member", _member_of),
    types.UpdateChannelParticipant: ("chat_member", _member_of),
    types.UpdateBotChatInviteRequester: ("join_request", _request_of),
    types.UpdateDeleteMessages: ("deleted", _deleted_of),
    types.UpdateDeleteChannelMessages: ("deleted", _deleted_of),
    types.UpdateMessageReactions: ("reaction", _reaction_of),
    types.UpdateBotMessageReaction: ("reaction", _reaction_of),
    types.UpdateBotMessageReactions: ("reaction", _reaction_of),
    types.UpdateMessagePoll: ("poll", _poll_of),
    types.UpdateMessagePollVote: ("poll_vote", _vote_of),
    # Money. Both are questions with a deadline instead of notifications,
    # which is why each arrives as something that can answer itself.
    types.UpdateBotShippingQuery: ("shipping", _shipping_of),
    types.UpdateBotPrecheckoutQuery: ("pre_checkout", _checkout_of),
    types.UpdateStory: ("story", _story_of),
    types.UpdateUserStatus: ("status", _status_of),
    types.UpdateUserTyping: ("typing", _typing_of),
    types.UpdateChatUserTyping: ("typing", _typing_of),
    types.UpdateChannelUserTyping: ("typing", _typing_of),
    types.UpdatePeerBlocked: ("blocked", _blocked_of),
    types.UpdateBotStopped: ("stopped", _stopped_of),
}


def _wrap(client: Any, raw: Any, event: Event) -> Message | None:
    """One message off an update, wrapped by the client when there is one.

    The client's wrapping does two things this cannot: it ties a reply to the
    message being answered when that message is already known, and it writes
    this one down so the next reply to it is known too. A dispatcher driven on
    its own still produces a message, without either.
    """
    if client is None:
        return Message.from_raw(raw, users=event.users, chats=event.chats)
    wrapped: Message | None = client.wrap_message(
        raw, users=event.users, chats=event.chats
    )
    return wrapped


def _chat_of(value: Any) -> int | None:
    """Which chat a reading came from, or None if it did not come from one.

    Asked of the reading rather than worked out per kind, because both of the
    readings a wait can be answered by already answer it, and they answer it in
    the case that matters here: an update carrying no users or chats still has
    the peer inside it, so chat may be None while chat_id is not. A reading
    with no chat at all, an inline press among them, says None and matches
    nothing, which is the honest answer instead of the silent one.
    """
    found = getattr(value, "chat_id", None)
    return found if isinstance(found, int) else None


def _name_of(callback: Any) -> str:
    """What to call a handler in a log line, however it was written."""
    return getattr(callback, "__qualname__", None) or repr(callback)


async def _maybe(value: Any) -> Any:
    if asyncio.iscoroutine(value) or isinstance(value, asyncio.Future):
        return await value
    return value
