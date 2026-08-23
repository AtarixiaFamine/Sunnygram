# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A button being pressed, and the things you want to do about it.

This is the other half of a keyboard. A bot puts buttons under a message, and
when someone presses one the bot is told: who pressed it, which message it was
under, and the payload that button was built with. Telegram then waits. Until
the press is answered the client shows a spinner on the button, so answering is
not optional politeness, it is what makes the button stop spinning.

There are two shapes of it and the difference is where the message lives. An
ordinary press names a chat and a message id, and the message can be edited the
way any message is. A press on a message that an inline query produced names
neither, because that message belongs to no chat this bot can see: it carries an
opaque id issued by one particular datacenter, and editing it means talking to
that datacenter instead of to home. Both arrive here as the same object, and
which one it is is the difference between chat being set and inline_id being
set.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..raw import types
from .chat import Chat
from .user import User

if TYPE_CHECKING:
    from ..client import Client
    from .message import Message

__all__ = ["CallbackQuery"]


@dataclass(slots=True)
class CallbackQuery:
    """One press of an inline button."""

    id: int
    sender: User | None = None
    chat: Chat | None = None
    message_id: int = 0
    data: bytes | None = None
    game: str | None = None
    chat_instance: int = 0
    inline_id: Any = None
    raw: Any = None
    client: Any = None

    # Left here by the filters that work them out, the same way a message
    # carries what a command filter found. Declared rather than attached on the
    # fly because this is a slotted class.
    match: Any = None

    def __repr__(self) -> str:
        who = self.sender.username or self.sender.id if self.sender else "somebody"
        return f"CallbackQuery({who} pressed {self.text or self.data!r})"

    @property
    def text(self) -> str:
        """The payload as text, which is how nearly every bot writes one.

        Payloads are bytes on the wire and a program almost always puts a short
        string in them, so this is the form handlers and filters read. A
        payload that is not text at all reads as empty instead of raising,
        since a filter asking about it is not the place to find that out.
        """
        if not self.data:
            return ""
        try:
            return self.data.decode()
        except UnicodeDecodeError:
            return ""

    @property
    def chat_id(self) -> int | None:
        """Which chat the press came from, even when nothing named the chat.

        The same shape as Message.chat_id and for the same reason: chat is
        built out of the users and chats an update carried, and an update that
        carried none of them still has the peer inside it. A press on an inline
        message has no chat at all and answers None, which is the honest answer
        instead of a zero that would compare equal to something.
        """
        if self.chat is not None:
            return self.chat.id
        peer = getattr(self.raw, "peer", None)
        for named in ("user_id", "chat_id", "channel_id"):
            found = getattr(peer, named, None)
            if isinstance(found, int):
                return found
        return None

    @property
    def is_inline(self) -> bool:
        """Whether the message this was pressed on came from an inline query."""
        return self.inline_id is not None

    async def answer(
        self,
        text: str = "",
        *,
        alert: bool = False,
        url: str | None = None,
        cache_time: int = 0,
    ) -> None:
        """Stop the spinner, and optionally say something while doing it.

        Nothing at all is a valid answer and is what a bot sends when the real
        reply is an edit to the message. text puts a notice along the top of
        the screen; alert makes it a box they have to dismiss instead.

        cache_time lets the client answer the same press itself for that many
        seconds without asking again, which is worth setting for a button whose
        answer cannot change.
        """
        await self._acting().answer_callback_query(
            self.id, text, alert=alert, url=url, cache_time=cache_time
        )

    async def edit(self, text: str, **options: Any) -> Message | None:
        """Rewrite the message this button is under.

        The usual way to answer a press: the message becomes the new state and
        the buttons change with it. An inline message answers with nothing,
        because Telegram says only whether the edit went through.
        """
        if self.inline_id is not None:
            await self._acting().edit_inline_message(self.inline_id, text, **options)
            return None
        return await self._acting().edit_message(
            self._peer(), self.message_id, text, **options
        )

    async def edit_markup(self, markup: Any = None) -> Message | None:
        """Change the buttons and leave the text alone, or take them away.

        Passing nothing removes the keyboard, which a bot does with a
        one-shot menu once it has been used.
        """
        if self.inline_id is not None:
            await self._acting().edit_inline_markup(self.inline_id, markup)
            return None
        return await self._acting().edit_markup(
            self._peer(), self.message_id, markup
        )

    async def get_message(self) -> Message:
        """Fetch the message this button is under.

        Costs a call. An inline message cannot be fetched at all: it has no
        chat to fetch it from, which is why editing one takes the opaque id
        rather than a message.
        """
        if self.inline_id is not None:
            raise SunnygramError(
                "this button is on an inline message, which has no chat to "
                "fetch it from. Edit it with edit or edit_markup instead"
            )
        found = await self._acting().get_messages(self._peer(), [self.message_id])
        if not found:
            raise SunnygramError(
                f"message {self.message_id} is not there any more, so the "
                "button was pressed on something that has since been deleted"
            )
        return found[0]

    async def reply(self, text: str, **options: Any) -> Message:
        """Say something new in the chat, as a reply to the message pressed."""
        options.setdefault("reply_to", self.message_id)
        return await self._acting().send_message(self._peer(), text, **options)

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this callback query is not bound to a client, so it cannot "
                "act on its own"
            )
        client: Client = self.client
        return client

    def _peer(self) -> Any:
        peer = getattr(self.raw, "peer", None)
        if peer is None:
            raise SunnygramError("this callback query does not name a chat")
        return peer

    @classmethod
    def from_raw(
        cls,
        update: Any,
        *,
        users: dict[int, Any] | None = None,
        chats: dict[int, Any] | None = None,
        client: Any = None,
    ) -> CallbackQuery | None:
        """Wrap a press off the wire, with whatever came alongside it."""
        inline = isinstance(update, types.UpdateInlineBotCallbackQuery)
        if not inline and not isinstance(update, types.UpdateBotCallbackQuery):
            return None
        known_users = users or {}
        known_chats = chats or {}
        return cls(
            id=update.query_id,
            sender=User.from_raw(known_users.get(update.user_id)),
            chat=(
                None
                if inline
                else Chat.of_peer(update.peer, known_users, known_chats)
            ),
            message_id=0 if inline else update.msg_id,
            data=update.data,
            game=update.game_short_name,
            chat_instance=update.chat_instance,
            inline_id=update.msg_id if inline else None,
            raw=update,
            client=client,
        )
