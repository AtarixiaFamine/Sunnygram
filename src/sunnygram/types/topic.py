# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""One thread of a forum.

A topic is a message that other messages hang off, so its id is a message id
and the thing it says about itself, the title and the icon, lives on that
message instead of anywhere separate. What is kept here is what a program
actually asks about a topic: what it is called, whether it is still open, and
how much in it has not been read.

The general topic, id 1, is the one every forum starts with. It has no opening
message, which is why nothing here assumes one exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..raw import types
from .message import Message

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["Topic"]


@dataclass(frozen=True, slots=True)
class Topic:
    """A thread in a forum, as someone reading it sees it."""

    id: int
    title: str
    chat_id: int = 0
    closed: bool = False
    pinned: bool = False
    hidden: bool = False
    mine: bool = False
    unread: int = 0
    unread_mentions: int = 0
    top_message: Message | None = None
    icon_emoji_id: int | None = None
    icon_color: int = 0
    date: int = 0
    raw: Any = None
    client: Any = None

    def __repr__(self) -> str:
        state = " (closed)" if self.closed else ""
        return f"Topic({self.id}, {self.title!r}{state})"

    async def send(self, text: str, **options: Any) -> Message:
        """Say something in this topic."""
        client: Client = self.client
        return await client.send_message(
            self.chat_id, text, topic=self.id, **options
        )

    async def close(self) -> Any:
        """Stop anybody but an administrator posting here."""
        client: Client = self.client
        return await client.close_topic(self.chat_id, self.id)

    async def reopen(self) -> Any:
        """Let people post here again."""
        client: Client = self.client
        return await client.reopen_topic(self.chat_id, self.id)

    async def delete(self) -> int:
        """Delete this topic and everything in it."""
        client: Client = self.client
        return await client.delete_topic(self.chat_id, self.id)

    @classmethod
    def from_raw(
        cls,
        topic: Any,
        *,
        chat_id: int = 0,
        users: dict[int, Any] | None = None,
        chats: dict[int, Any] | None = None,
        messages: dict[int, Any] | None = None,
        client: Any = None,
    ) -> Topic | None:
        """Wrap a topic, with the messages that came on the same page.

        A deleted topic arrives as a different constructor carrying only an id,
        and there is nothing to wrap in that, so it comes back as nothing.
        """
        if not isinstance(topic, types.ForumTopic):
            return None
        return cls(
            id=topic.id,
            title=topic.title,
            chat_id=chat_id or _chat_of(topic.peer),
            closed=bool(topic.closed),
            pinned=bool(topic.pinned),
            hidden=bool(topic.hidden),
            mine=bool(topic.my),
            unread=topic.unread_count,
            unread_mentions=topic.unread_mentions_count,
            top_message=Message.from_raw(
                (messages or {}).get(topic.top_message),
                users=users or {},
                chats=chats or {},
                client=client,
            ),
            icon_emoji_id=topic.icon_emoji_id,
            icon_color=topic.icon_color,
            date=topic.date,
            raw=topic,
            client=client,
        )


def _chat_of(peer: Any) -> int:
    for field in ("channel_id", "chat_id", "user_id"):
        found = getattr(peer, field, None)
        if isinstance(found, int):
            return found
    return 0
