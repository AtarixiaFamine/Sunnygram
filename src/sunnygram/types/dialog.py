# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""One row of the conversation list.

A dialog is not a chat. It is this account's relationship with one: where the
unread count is, whether it is muted, whether it is pinned to the top, and
which message was the last one. Telegram keeps the two apart because the chat
is the same for everybody in it and the dialog is not, and keeping them apart
here means a Chat means the same thing wherever it came from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..raw import types
from .chat import Chat
from .message import Message

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["Dialog"]


@dataclass(frozen=True, slots=True)
class Dialog:
    """A conversation as it appears in the list of them."""

    chat: Chat
    top_message: Message | None = None
    unread: int = 0
    unread_mentions: int = 0
    pinned: bool = False
    muted: bool = False
    raw: Any = None
    client: Any = None

    def __repr__(self) -> str:
        unread = f", {self.unread} unread" if self.unread else ""
        return f"Dialog({self.chat.title or self.chat.id}{unread})"

    async def send(self, text: str, **options: Any) -> Message:
        """Say something here."""
        client: Client = self.client
        return await client.send_message(self.chat.id, text, **options)

    async def read(self) -> None:
        """Mark everything in it as read."""
        client: Client = self.client
        await client.read_history(self.chat.id)

    @classmethod
    def from_raw(
        cls,
        dialog: Any,
        *,
        users: dict[int, Any] | None = None,
        chats: dict[int, Any] | None = None,
        messages: dict[int, Any] | None = None,
        client: Any = None,
    ) -> Dialog | None:
        """Wrap a dialog, with everything the same page carried.

        The last message is looked up by id among the messages that came with
        it instead of fetched, which is why this takes them: the answer that
        carries the dialogs carries their last messages too, and going back for
        one would be a round trip per row.
        """
        if not isinstance(dialog, types.Dialog):
            return None
        known_users = users or {}
        known_chats = chats or {}

        chat = _chat_of(dialog.peer, known_users, known_chats)
        if chat is None:
            return None
        return cls(
            chat=chat,
            top_message=Message.from_raw(
                (messages or {}).get(dialog.top_message),
                users=known_users,
                chats=known_chats,
                client=client,
            ),
            unread=dialog.unread_count,
            unread_mentions=dialog.unread_mentions_count,
            pinned=bool(dialog.pinned),
            # Telegram spells a mute as a time to stay muted until, and uses a
            # date far in the future for one with no end. Anything still to
            # come is muted now, which is the question anybody is asking.
            muted=_muted(dialog.notify_settings),
            raw=dialog,
            client=client,
        )


def _chat_of(peer: Any, users: dict[int, Any], chats: dict[int, Any]) -> Chat | None:
    if isinstance(peer, types.PeerUser):
        return Chat.from_raw(users.get(peer.user_id))
    if isinstance(peer, types.PeerChat):
        return Chat.from_raw(chats.get(peer.chat_id))
    if isinstance(peer, types.PeerChannel):
        return Chat.from_raw(chats.get(peer.channel_id))
    return None


def _muted(settings: Any) -> bool:
    from time import time

    until = getattr(settings, "mute_until", None)
    return isinstance(until, int) and until > time()
