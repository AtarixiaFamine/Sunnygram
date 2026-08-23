# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Inline mode: answering what someone is still typing.

A person types the bot's name in any chat and then a query, and every keystroke
reaches the bot as an update. The bot answers with a list of things they could
send, the client draws them, and if one is picked it is sent by the person
instead of by the bot. That is what makes inline mode worth having: the bot
works in chats it is not in.

Two updates make the round trip. The query arrives, and the answer to it is a
list of results. Then, if the bot asked to be told, the chosen one arrives as
well, which is how a program counts what people actually pick.

This file faces both ways, the same way buttons.py does. InlineQuery and
ChosenResult describe what arrived; InlineResult describes what is about to be
sent. A result is written as one of the factories below instead of as a
constructor, because Telegram spells a result four different ways depending on
whether the file is one it already holds, one on the web, a game, or nothing at
all, and which of the four is being built follows from what the caller passed.

The rule that governs all of it: a query must be answered. Telegram holds it
open until something answers, and every client draws that as a panel that never
finishes loading. An answer with no results is a valid answer and is what a bot
sends when it has nothing to offer.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..raw import base, types
from .user import User

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["ChosenResult", "InlineQuery", "InlineResult"]

# What Telegram takes in one answer. Anything past this is refused on the wire,
# and paging is what next_offset is for.
MAX_RESULTS = 50

# How long a client may reuse an answer without asking again. Telegram's own
# default is five minutes, and a bot whose results depend on the moment should
# say zero rather than leave this.
CACHE_TIME = 300

# A result id travels back on the chosen-result update, so it is the program's
# way of naming its own results. This is what one gets when the caller has no
# name of their own for it.
ID_BYTES = 8

# Turning a piece of text into the text and the entities to draw over it. The
# client passes its own, since the parse mode is the client's business and a
# result is built long before there is one.
Style = Callable[[str], tuple[str, list[Any]]]

# Where the query was typed, in the six ways Telegram distinguishes. A bot
# answers differently in a group than in its own chat often enough that this is
# worth a word instead of a constructor.
_WHERE: dict[type, str] = {
    types.InlineQueryPeerTypeSameBotPM: "same_bot",
    types.InlineQueryPeerTypePM: "private",
    types.InlineQueryPeerTypeBotPM: "bot",
    types.InlineQueryPeerTypeChat: "group",
    types.InlineQueryPeerTypeMegagroup: "supergroup",
    types.InlineQueryPeerTypeBroadcast: "channel",
}


@dataclass(slots=True)
class InlineResult:
    """One thing a bot offers in answer to an inline query.

    Built by the factories below instead of by hand: each of them knows which
    of Telegram's four result constructors it needs and what has to travel with
    it. What they have in common is the message, which gets sent if
    this result is the one picked, and which is not built until the answer goes
    out because the parse mode belongs to the client rather than to the result.
    """

    kind: str = "article"
    id: str = ""
    title: str = ""
    description: str = ""
    url: str = ""
    thumb: Any = None
    content: Any = None
    media: Any = None
    game_name: str = ""
    text: str = ""
    entities: list[Any] | None = None
    no_webpage: bool = False
    reply_markup: Any = None
    # A ready InputBotInlineMessage, which takes over from text entirely. The
    # location, venue and contact factories set it, and it is also the way to
    # send something this file has no factory for.
    message: Any = None

    def __repr__(self) -> str:
        return f"InlineResult({self.kind} {self.id!r}, {self.title or self.text!r})"

    @classmethod
    def article(
        cls,
        title: str,
        text: str,
        *,
        description: str = "",
        url: str = "",
        thumb: str = "",
        id: str = "",
        no_webpage: bool = False,
        reply_markup: Any = None,
    ) -> InlineResult:
        """A row of text, which is what most bots answer with.

        The title and description are what the person reads in the list; text
        is the message they send by picking it, and the two have no reason to
        be the same. A url is shown as where the article came from and is not
        opened by picking it.
        """
        return cls(
            kind="article",
            id=id or _an_id(),
            title=title,
            description=description,
            url=url,
            thumb=_web(thumb, "image/jpeg"),
            text=text,
            no_webpage=no_webpage,
            reply_markup=reply_markup,
        )

    @classmethod
    def photo(
        cls,
        photo: Any,
        *,
        caption: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A photo, either one Telegram holds or one on the web.

        Anything send_media takes is a photo it already holds: a Photo off a
        message, an InputPhoto, a portable file reference, a foreign file id.
        A http link is the other case, and Telegram fetches it itself when the
        result is picked, so the link has to still work then.

        A photo Telegram already holds carries no title or description, because
        its own constructor has nowhere to put them.
        """
        return cls._file(
            "photo", photo, caption, thumb, id, reply_markup, mime="image/jpeg"
        )

    @classmethod
    def animation(
        cls,
        animation: Any,
        *,
        caption: str = "",
        title: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A soundless looping video, which is what a gif is here.

        Telegram tells the two web forms apart by what is being served: a real
        gif is a gif, and an mp4 with no sound is what every client actually
        wants, so a link ending in mp4 is offered as that.
        """
        mime = "video/mp4" if _looks_like(animation, ".mp4") else "image/gif"
        kind = "mpeg4_gif" if mime == "video/mp4" else "gif"
        return cls._file(
            kind,
            animation,
            caption,
            thumb,
            id,
            reply_markup,
            mime=mime,
            title=title,
        )

    @classmethod
    def video(
        cls,
        video: Any,
        *,
        caption: str = "",
        title: str = "",
        description: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A video, held or on the web."""
        return cls._file(
            "video",
            video,
            caption,
            thumb,
            id,
            reply_markup,
            mime="video/mp4",
            title=title,
            description=description,
        )

    @classmethod
    def audio(
        cls,
        audio: Any,
        *,
        caption: str = "",
        title: str = "",
        description: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A song or any other audio file."""
        return cls._file(
            "audio",
            audio,
            caption,
            thumb,
            id,
            reply_markup,
            mime="audio/mpeg",
            title=title,
            description=description,
        )

    @classmethod
    def voice(
        cls,
        voice: Any,
        *,
        caption: str = "",
        title: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A voice note, which is an audio file drawn as a waveform."""
        return cls._file(
            "voice",
            voice,
            caption,
            "",
            id,
            reply_markup,
            mime="audio/ogg",
            title=title,
        )

    @classmethod
    def document(
        cls,
        document: Any,
        *,
        caption: str = "",
        title: str = "",
        description: str = "",
        thumb: str = "",
        mime: str = "application/octet-stream",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """Any file at all, which is what everything that is not a photo is.

        The mime type only matters for the web form, where Telegram has nothing
        but the link to go on. Telegram allows pdf and zip there and nothing
        else, which is its rule instead of this one.
        """
        return cls._file(
            "document",
            document,
            caption,
            thumb,
            id,
            reply_markup,
            mime=mime,
            title=title,
            description=description,
        )

    @classmethod
    def sticker(
        cls, sticker: Any, *, id: str = "", reply_markup: Any = None
    ) -> InlineResult:
        """A sticker, which has to be one Telegram already holds.

        There is no web form for this one: a sticker is a document in a set and
        a link to an image is not one.
        """
        result = cls._file("sticker", sticker, "", "", id, reply_markup, mime="")
        if result.media is None:
            raise ValueError(
                "a sticker result has to name a sticker Telegram already "
                "holds, since there is no web form for one"
            )
        return result

    @classmethod
    def location(
        cls,
        latitude: float,
        longitude: float,
        title: str,
        *,
        live_period: int = 0,
        heading: int = 0,
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A point on the map.

        live_period turns it into a location that keeps updating for that many
        seconds, which is what sharing your position looks like.
        """
        return cls(
            kind="geo",
            id=id or _an_id(),
            title=title,
            thumb=_web(thumb, "image/jpeg"),
            reply_markup=reply_markup,
            message=types.InputBotInlineMessageMediaGeo(
                geo_point=types.InputGeoPoint(lat=latitude, long=longitude),
                period=live_period or None,
                heading=heading or None,
                reply_markup=reply_markup,
            ),
        )

    @classmethod
    def venue(
        cls,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        *,
        provider: str = "",
        venue_id: str = "",
        venue_type: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """A place, which is a point on the map with a name and a street."""
        return cls(
            kind="venue",
            id=id or _an_id(),
            title=title,
            description=address,
            thumb=_web(thumb, "image/jpeg"),
            reply_markup=reply_markup,
            message=types.InputBotInlineMessageMediaVenue(
                geo_point=types.InputGeoPoint(lat=latitude, long=longitude),
                title=title,
                address=address,
                provider=provider,
                venue_id=venue_id,
                venue_type=venue_type,
                reply_markup=reply_markup,
            ),
        )

    @classmethod
    def contact(
        cls,
        phone: str,
        first_name: str,
        *,
        last_name: str = "",
        vcard: str = "",
        thumb: str = "",
        id: str = "",
        reply_markup: Any = None,
    ) -> InlineResult:
        """Someone's phone number, as a contact card."""
        return cls(
            kind="contact",
            id=id or _an_id(),
            title=" ".join(part for part in (first_name, last_name) if part),
            description=phone,
            thumb=_web(thumb, "image/jpeg"),
            reply_markup=reply_markup,
            message=types.InputBotInlineMessageMediaContact(
                phone_number=phone,
                first_name=first_name,
                last_name=last_name,
                vcard=vcard,
                reply_markup=reply_markup,
            ),
        )

    @classmethod
    def game(
        cls, short_name: str, *, id: str = "", reply_markup: Any = None
    ) -> InlineResult:
        """One of the bot's games, by the short name it was registered with."""
        return cls(
            kind="game",
            id=id or _an_id(),
            game_name=short_name,
            reply_markup=reply_markup,
        )

    def to_raw(self, style: Style | None = None) -> base.InputBotInlineResult:
        """This result as the protocol spells it.

        Four constructors, and which one is right follows from what the result
        carries: a game is its own, a photo Telegram holds is its own, any
        other file it holds is the document one, and everything else, web forms
        included, is the general one.
        """
        sent = self.message if self.message is not None else self._sent(style)

        if self.game_name:
            return types.InputBotInlineResultGame(
                id=self.id, short_name=self.game_name, send_message=sent
            )

        held = self._held()
        if isinstance(held, types.InputPhoto):
            return types.InputBotInlineResultPhoto(
                id=self.id, type=self.kind, photo=held, send_message=sent
            )
        if isinstance(held, types.InputDocument):
            return types.InputBotInlineResultDocument(
                id=self.id,
                type=self.kind,
                title=self.title or None,
                description=self.description or None,
                document=held,
                send_message=sent,
            )
        return types.InputBotInlineResult(
            id=self.id,
            type=self.kind,
            title=self.title or None,
            description=self.description or None,
            url=self.url or None,
            thumb=self.thumb,
            content=self.content,
            send_message=sent,
        )

    @classmethod
    def _file(
        cls,
        kind: str,
        file: Any,
        caption: str,
        thumb: str,
        id: str,
        reply_markup: Any,
        *,
        mime: str,
        title: str = "",
        description: str = "",
    ) -> InlineResult:
        """The shared half of every result that carries a file.

        A http link is a web result and anything else is meant to be something
        Telegram already holds, which is worked out at to_raw time so that a
        result stays a description instead of becoming a call.
        """
        web = isinstance(file, str) and file.startswith(("http://", "https://"))
        return cls(
            kind=kind,
            id=id or _an_id(),
            title=title,
            description=description,
            url=file if web and kind == "photo" else "",
            thumb=_web(thumb, "image/jpeg"),
            content=_web(file, mime) if web else None,
            media=None if web else file,
            text=caption,
            reply_markup=reply_markup,
        )

    def _held(self) -> Any:
        """The file this names, if it is one Telegram already holds.

        Recognising the shapes a caller may have is what methods/attachments.py
        does for every send, and doing it again here would be the same code
        with its own bugs. It is imported at call time, not at the top
        because methods/ is built on types/ and the other direction would be a
        circle.
        """
        if self.media is None:
            return None

        from ..methods.attachments import existing_media

        found = existing_media(self.media)
        if isinstance(found, (types.InputMediaPhoto, types.InputMediaDocument)):
            return found.id
        raise SunnygramError(
            f"{self.media!r} is not a file Telegram already holds and not a "
            "http link either, so there is nothing to offer for it"
        )

    def _sent(self, style: Style | None) -> base.InputBotInlineMessage:
        """The message this result sends when it is the one picked."""
        text, entities = self._styled(style)
        if self.media is not None or self.content is not None:
            # A file carries a caption instead of a message, and Telegram
            # spells that difference as a different constructor.
            return types.InputBotInlineMessageMediaAuto(
                message=text,
                entities=entities or None,
                reply_markup=self.reply_markup,
            )
        return types.InputBotInlineMessageText(
            message=text,
            entities=entities or None,
            no_webpage=self.no_webpage,
            reply_markup=self.reply_markup,
        )

    def _styled(self, style: Style | None) -> tuple[str, list[Any]]:
        if self.entities is not None:
            return self.text, list(self.entities)
        if style is None:
            return self.text, []
        return style(self.text)


@dataclass(slots=True)
class InlineQuery:
    """What someone has typed after the bot's name, so far."""

    id: int
    sender: User | None = None
    text: str = ""
    offset: str = ""
    where: str = ""
    geo: Any = None
    raw: Any = None
    client: Any = None

    # Left here by the filters that work it out, the same way a message carries
    # what a command filter found. Declared instead of attached on the fly
    # because this is a slotted class.
    match: Any = None

    def __repr__(self) -> str:
        who = self.sender.username or self.sender.id if self.sender else "somebody"
        return f"InlineQuery({who} typing {self.text!r})"

    async def answer(
        self,
        results: list[InlineResult | Any],
        *,
        cache_time: int = CACHE_TIME,
        gallery: bool = False,
        private: bool = False,
        next_offset: str = "",
        switch_pm: str = "",
        start_parameter: str = "",
        parse_mode: str | None = "",
    ) -> bool:
        """Offer these results, which stops the client loading.

        Answering is not optional. Telegram holds the query open until the bot
        says something about it, and until then the person sees a panel that
        never finishes. An empty list is a complete answer and is what a bot
        sends when it has nothing for that query.

        gallery draws the results as a grid of pictures rather than as a list
        of rows. private means the answer was built for this one person and
        must not be cached for anybody else, which matters the moment a result
        depends on who asked. next_offset is the cursor the next query in the
        same session arrives with, and is how a long list is paged: hand back
        where this page ended and the client asks for the rest by scrolling.

        switch_pm puts a button above the results that takes the person into
        the bot's own chat, carrying start_parameter with them. That is how a
        bot that needs setting up first says so, instead of answering with an
        apology it has no way to act on.
        """
        answered: bool = await self._acting().answer_inline_query(
            self.id,
            results,
            cache_time=cache_time,
            gallery=gallery,
            private=private,
            next_offset=next_offset,
            switch_pm=switch_pm,
            start_parameter=start_parameter,
            parse_mode=parse_mode,
        )
        return answered

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this inline query is not bound to a client, so it cannot be "
                "answered on its own"
            )
        client: Client = self.client
        return client

    @classmethod
    def from_raw(
        cls,
        update: Any,
        *,
        users: dict[int, Any] | None = None,
        client: Any = None,
    ) -> InlineQuery | None:
        """Wrap a query off the wire, with whoever came alongside it."""
        if not isinstance(update, types.UpdateBotInlineQuery):
            return None
        known = users or {}
        return cls(
            id=update.query_id,
            sender=User.from_raw(known.get(update.user_id)),
            text=update.query,
            offset=update.offset,
            where=_WHERE.get(type(update.peer_type), ""),
            geo=update.geo,
            raw=update,
            client=client,
        )


@dataclass(slots=True)
class ChosenResult:
    """Which result someone picked, and what they had typed to find it.

    Only bots that asked for this are told, and asking is a setting on the bot
    instead of a call: BotFather calls it inline feedback. Telegram samples it
    for busy bots, so this is a statistic, not a receipt, and a program
    that has to know something happened should learn it from the message.
    """

    id: str
    sender: User | None = None
    text: str = ""
    inline_id: Any = None
    geo: Any = None
    raw: Any = None
    client: Any = None

    match: Any = None

    def __repr__(self) -> str:
        who = self.sender.username or self.sender.id if self.sender else "somebody"
        return f"ChosenResult({who} picked {self.id!r})"

    @property
    def editable(self) -> bool:
        """Whether the message that was sent can still be rewritten.

        Only if the result carried an inline keyboard. Telegram issues an id
        for that message so the buttons under it can be answered, and with no
        buttons there is nothing to answer and no id, so the message is gone
        from the bot's reach the moment it is sent.
        """
        return self.inline_id is not None

    async def edit(self, text: str, **options: Any) -> None:
        """Rewrite the message this result sent."""
        # The id is checked before the client is reached for, so the reason a
        # result cannot be edited wins over the more general complaint about
        # not being bound to anything.
        inline_id = self._editable()
        await self._acting().edit_inline_message(inline_id, text, **options)

    async def edit_markup(self, markup: Any = None) -> None:
        """Change the buttons under the message this result sent."""
        inline_id = self._editable()
        await self._acting().edit_inline_markup(inline_id, markup)

    def _editable(self) -> Any:
        if self.inline_id is None:
            raise SunnygramError(
                "this result was sent without an inline keyboard, so Telegram "
                "issued no id for the message and it cannot be edited. Give "
                "the result a reply_markup if it has to be editable later"
            )
        return self.inline_id

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this chosen result is not bound to a client, so it cannot act "
                "on its own"
            )
        client: Client = self.client
        return client

    @classmethod
    def from_raw(
        cls,
        update: Any,
        *,
        users: dict[int, Any] | None = None,
        client: Any = None,
    ) -> ChosenResult | None:
        """Wrap a chosen result off the wire."""
        if not isinstance(update, types.UpdateBotInlineSend):
            return None
        known = users or {}
        return cls(
            id=update.id,
            sender=User.from_raw(known.get(update.user_id)),
            text=update.query,
            inline_id=update.msg_id,
            geo=update.geo,
            raw=update,
            client=client,
        )


def _an_id() -> str:
    """A name for a result the caller did not name.

    The id comes back on the chosen-result update, so a program that wants to
    know which of its results people pick should pass its own. This exists so
    that one which does not still sends something unique, since Telegram
    refuses an answer with two results sharing an id.
    """
    return secrets.token_hex(ID_BYTES)


def _web(url: str, mime: str) -> Any:
    """A link Telegram will fetch for itself, or nothing if there is no link."""
    if not url:
        return None
    return types.InputWebDocument(url=url, size=0, mime_type=mime, attributes=[])


def _looks_like(file: Any, suffix: str) -> bool:
    return isinstance(file, str) and file.lower().split("?")[0].endswith(suffix)
