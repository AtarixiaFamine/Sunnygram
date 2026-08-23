# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A message, and the things you want to do to one.

The wrapper exists for two reasons. The first is that a raw message is a hundred
fields and a program wants six of them. The second is the one that matters: a
raw message is inert. It knows its own id and the id of the chat it is in, and
that is not enough to answer it, because answering means naming the chat to the
server, and naming a chat means an access hash the message does not carry. So a
message that arrives here is bound to the client that received it, and from then
on reply and delete and download are questions it can answer for itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..parser import unparse
from ..raw import types
from .buttons import buttons_of
from .chat import Chat
from .user import User

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["Message"]


@dataclass(slots=True)
class Message:
    """One message, and what can be done about it."""

    id: int
    chat: Chat | None = None
    sender: User | None = None
    date: datetime | None = None
    text: str = ""
    entities: list[Any] = field(default_factory=list)
    media: Any = None
    reply_to_id: int | None = None
    outgoing: bool = False
    service: bool = False
    raw: Any = None
    client: Any = None

    # The message this one answers, when it can be had without asking for it.
    # Filled from whatever came in the same answer, from the quote the reply
    # header carries, or from what the client has lately seen. None means only
    # that nothing here knew it, which is what get_reply is for.
    reply_to_message: Message | None = None

    # Whether this is an outline instead of the message itself. A quoted reply
    # carries the part of the other message that was selected and the media it
    # had, which is enough to act on and is not the whole thing, so anything
    # reading text off one should know which it is holding.
    partial: bool = False

    # Filled in by the filters that work them out, so a handler reads them
    # instead of parsing the text a second time. Declared here rather than
    # attached on the fly because this is a slotted class, which is worth
    # keeping: a busy chat makes a great many of these.
    command: str | None = None
    arguments: list[str] = field(default_factory=list)
    match: Any = None

    def __repr__(self) -> str:
        where = self.chat.title if self.chat else "somewhere"
        body = self.text if len(self.text) <= 30 else self.text[:27] + "..."
        return f"Message({self.id} in {where!r}: {body!r})"

    @property
    def markdown(self) -> str:
        """The text with its formatting written back in as markdown."""
        return unparse(self.text, self.entities, "markdown")

    @property
    def html(self) -> str:
        """The text with its formatting written back in as HTML."""
        return unparse(self.text, self.entities, "html")

    @property
    def payment(self) -> Any:
        """The payment this service message reports, if it reports one.

        A successful payment arrives as a service message instead of as an
        update of its own, so this is where a bot finds out it was paid. Only
        the bot that sold the thing gets the reading carrying the charge id,
        which a refund needs.
        """
        from .payments import SuccessfulPayment

        return SuccessfulPayment.from_raw(getattr(self.raw, "action", None))

    @property
    def has_media(self) -> bool:
        return self.media is not None

    @property
    def chat_id(self) -> int | None:
        """Which chat this is in, by id, even when nothing named the chat.

        A message that arrives alongside an answer comes with the users and
        chats that answer carried, and chat is the friendly form of that. A
        message the server made of something we just sent often arrives with
        none of them, so there is an id inside it and nothing to build a Chat
        out of. Everything that only needs the id works either way.
        """
        if self.chat is not None:
            return self.chat.id
        peer = getattr(self.raw, "peer_id", None)
        for named in ("user_id", "chat_id", "channel_id"):
            found = getattr(peer, named, None)
            if isinstance(found, int):
                return found
        return None

    @property
    def buttons(self) -> list[list[Any]]:
        """The rows of inline buttons under this message, if it has any."""
        return buttons_of(self)

    @property
    def file_ref(self) -> str:
        """This message's file, as one string that can be written down.

        The portable form: put it in a database, hand it to another process,
        and sending the same file later costs one call with no upload and no
        download. It names where the message came from as well, so the token
        inside it can be renewed when it goes stale.
        """
        from ..files import file_ref

        return file_ref(self)

    @property
    def album_id(self) -> int | None:
        """Which album this message is part of, if it is part of one.

        An album is not one message carrying several files. It is several
        messages that share this id, which the clients then draw as one block,
        so a photo in an album arrives here on its own like any other.
        """
        found = getattr(self.raw, "grouped_id", None)
        return found if isinstance(found, int) else None

    async def react(self, reaction: Any = None, **options: Any) -> None:
        """React to this message, or clear this account's reactions on it."""
        await self._acting().react(self._peer(), self.id, reaction, **options)

    async def copy_to(self, target: Any, **options: Any) -> Message:
        """Send this message on without saying where it came from.

        The difference from forward_to is what the other side sees: a forward
        carries the original author's name, and this does not.
        """
        return await self._acting().copy_message(target, self, **options)

    async def vote(self, *options: int) -> Any:
        """Answer the poll this message carries, by answer position."""
        if not isinstance(self.media, types.MessageMediaPoll):
            raise SunnygramError("this message carries no poll")
        return await self._acting().vote(self._peer(), self.id, *options)

    async def reply(self, text: str, **options: Any) -> Message:
        """Answer this message in its own chat, as a reply to it."""
        options.setdefault("reply_to", self.id)
        return await self._acting().send_message(self._peer(), text, **options)

    async def respond(self, text: str, **options: Any) -> Message:
        """Say something in the same chat, without replying to anything."""
        return await self._acting().send_message(self._peer(), text, **options)

    async def reply_file(self, file: Any, **options: Any) -> Message:
        """Answer this message with a file, as a reply to it.

        The kind is worked out from the name, so a .mp4 arrives playable and a
        .jpg as a photo. Pass kind= to overrule that.
        """
        options.setdefault("reply_to", self.id)
        return await self._acting().send_file(self._peer(), file, **options)

    async def reply_album(self, files: Any, **options: Any) -> list[Message]:
        """Answer this message with several files as one group."""
        options.setdefault("reply_to", self.id)
        return await self._acting().send_album(self._peer(), files, **options)

    async def reply_media(self, media: Any, **options: Any) -> Message:
        """Answer with a file Telegram already holds, uploading nothing.

        reply_file is for bytes that have to go up. This is for a file that is
        already there: what another message carries, or what a program wrote
        down after sending it once. Passing one of those to reply_file would
        try to upload the reference itself.
        """
        options.setdefault("reply_to", self.id)
        return await self._acting().send_media(self._peer(), media, **options)

    async def edit(self, text: str, **options: Any) -> Message:
        """Rewrite this message, which only works on one of ours."""
        return await self._acting().edit_message(
            self._peer(), self.id, text, **options
        )

    async def edit_media(self, media: Any, **options: Any) -> Message:
        """Replace the file this message carries with another one."""
        return await self._acting().edit_media(
            self._peer(), self.id, media, **options
        )

    async def edit_markup(self, markup: Any = None) -> Message:
        """Change the buttons under this message, or take them away."""
        return await self._acting().edit_markup(self._peer(), self.id, markup)

    async def get_reply(self) -> Message | None:
        """The message this one answers, fetched only if it has to be.

        Nearly always it does not: the message being replied to came past this
        client a moment ago and is already on reply_to_message, and the
        quoted kind of reply carries an outline of it in the update itself.
        Both are answered from here without a call. What is left is an old
        message someone scrolled up to, and that costs one.

        An outline is not enough for this, so a quote is exchanged here for the
        message it was taken from.
        """
        if self.reply_to_id is None:
            return None
        known = self.reply_to_message
        if known is not None and not known.partial:
            return known
        found = await self._acting().get_messages(
            self._reply_peer(), [self.reply_to_id]
        )
        if not found:
            return known
        self.reply_to_message = found[0]
        return found[0]

    async def delete(self, *, everywhere: bool = True) -> None:
        """Take this message back."""
        await self._acting().delete_messages(
            self._peer(), [self.id], everywhere=everywhere
        )

    async def forward_to(self, target: Any) -> None:
        """Send this message on to someone else."""
        await self._acting().forward_messages(target, self._peer(), [self.id])

    async def download(self, **options: Any) -> Any:
        """Fetch whatever file this message carries.

        The message goes down instead of the media off it, so that a file
        reference which has gone stale can be renewed: the message is what
        renews it, and the media on its own does not say which message that
        was.
        """
        if self.media is None:
            raise SunnygramError("this message carries no file")
        return await self._acting().download(self, **options)

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this message is not bound to a client, so it cannot act on "
                "its own. Messages that arrive through a client are bound; one "
                "built by hand has to be sent through the client instead"
            )
        client: Client = self.client
        return client

    def _peer(self) -> Any:
        if self.chat is not None:
            return self.chat.id
        # The raw peer, which names the chat perfectly well and is what resolve
        # takes when there was nothing alongside the message to build a Chat
        # from. That is the ordinary case for a message we have just sent.
        peer = getattr(self.raw, "peer_id", None)
        if peer is None:
            raise SunnygramError("this message does not say which chat it is in")
        return peer

    def _reply_peer(self) -> Any:
        """Where the message being answered lives, which is usually here.

        Usually, not always: a quoted reply can answer a message in another
        chat, and the reply header says which. Fetching it from this chat would
        find some unrelated message with the same id.
        """
        elsewhere = getattr(self.raw, "reply_to", None)
        found = getattr(elsewhere, "reply_to_peer_id", None)
        return self._peer() if found is None else found

    @classmethod
    def from_raw(
        cls,
        message: Any,
        *,
        users: dict[int, Any] | None = None,
        chats: dict[int, Any] | None = None,
        replies: dict[int, Any] | None = None,
        client: Any = None,
    ) -> Message | None:
        """Wrap a message off the wire, with whatever came alongside it.

        The users and chats are the ones the same answer carried. They are what
        turns the ids inside a message into people and places, which is why
        every call that returns messages returns them too.

        replies is the same idea one step further: the other messages in the
        same answer, so that a reply to one of them is tied to it here rather
        than fetched later. A page of history usually contains both halves of a
        conversation, and pairing them up costs a dict lookup.
        """
        if not isinstance(message, (types.Message, types.MessageService)):
            return None
        known_users = users or {}
        known_chats = chats or {}

        chat = Chat.of_peer(message.peer_id, known_users, known_chats)
        sender = None
        if isinstance(message.from_id, types.PeerUser):
            sender = User.from_raw(known_users.get(message.from_id.user_id))
        elif message.from_id is None and chat is not None and chat.is_private:
            # A private message with no sender is from whoever is not us, and
            # the chat says who that is.
            sender = User.from_raw(known_users.get(chat.id))

        if isinstance(message, types.Message):
            body = message.message or ""
            styled = list(message.entities or ())
            media = message.media
        else:
            # A service message is a note about the chat, not something
            # someone wrote: someone joined, the title changed, a call ended.
            body, styled, media = "", [], None
        header = message.reply_to
        answers = getattr(header, "reply_to_msg_id", None)
        return cls(
            id=message.id,
            chat=chat,
            sender=sender,
            date=datetime.fromtimestamp(message.date, timezone.utc),
            text=body,
            entities=styled,
            media=media,
            reply_to_id=answers,
            reply_to_message=(
                None
                if answers is None
                else cls._answered(
                    header, answers, chat, known_users, known_chats, replies, client
                )
            ),
            outgoing=bool(message.out),
            service=not isinstance(message, types.Message),
            raw=message,
            client=client,
        )

    @classmethod
    def _answered(
        cls,
        header: Any,
        answers: int,
        chat: Chat | None,
        users: dict[int, Any],
        chats: dict[int, Any],
        replies: dict[int, Any] | None,
        client: Any,
    ) -> Message | None:
        """The message being replied to, if this answer already carried it.

        Two ways it can have. The first is the whole message arriving in the
        same answer, which is what a page of history usually looks like. The
        second is a quoted reply, where the header carries the part of the
        other message that was selected and the media it had, and that is an
        outline instead of the message: enough to download what it carried or
        read what was quoted, not enough to trust as its text.
        """
        if replies is not None:
            found = replies.get(answers)
            if found is not None:
                # No replies of its own: a reply chain is a chain, and
                # following it here would walk it as far as the page goes.
                return cls.from_raw(found, users=users, chats=chats, client=client)

        quoted = getattr(header, "quote_text", None)
        carried = getattr(header, "reply_media", None)
        if not quoted and carried is None:
            return None
        return cls(
            id=answers,
            chat=Chat.of_peer(getattr(header, "reply_to_peer_id", None), users, chats)
            or chat,
            text=quoted or "",
            entities=list(getattr(header, "quote_entities", None) or ()),
            media=carried,
            partial=True,
            raw=header,
            client=client,
        )
