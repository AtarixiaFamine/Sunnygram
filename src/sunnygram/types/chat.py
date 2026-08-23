# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Where a message happened.

Telegram has four things a conversation can be and calls them by three
different names on the wire: a user, a small group, a supergroup and a
broadcast channel, spelled as User, Chat and Channel with a flag deciding which
of the last two a Channel is. This is all four with one word for each.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..raw import types
from ..storage import PeerKind

__all__ = ["Chat"]


@dataclass(frozen=True, slots=True)
class Chat:
    """A conversation, whoever or whatever is on the other side of it."""

    id: int
    kind: PeerKind
    title: str | None = None
    username: str | None = None
    members: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        return f"Chat({self.kind.value} {self.id}, {self.title or 'no title'})"

    @property
    def is_private(self) -> bool:
        """Whether this is one person talking to another."""
        return self.kind.is_user

    @property
    def is_group(self) -> bool:
        """Whether people talk here, small group or supergroup alike."""
        return self.kind in (PeerKind.CHAT, PeerKind.SUPERGROUP)

    @property
    def is_channel(self) -> bool:
        """Whether this is a broadcast, where only admins post."""
        return self.kind is PeerKind.CHANNEL

    @classmethod
    def of_peer(
        cls, peer: Any, users: dict[int, Any], chats: dict[int, Any]
    ) -> Chat | None:
        """The chat a Peer names, out of what came alongside it.

        A Peer is an id and which of the three id spaces it is in, and nothing
        else, so it only becomes a chat with the users and chats the same
        answer carried.
        """
        if isinstance(peer, types.PeerUser):
            return cls.from_raw(users.get(peer.user_id))
        if isinstance(peer, types.PeerChat):
            return cls.from_raw(chats.get(peer.chat_id))
        if isinstance(peer, types.PeerChannel):
            return cls.from_raw(chats.get(peer.channel_id))
        return None

    @classmethod
    def from_raw(cls, peer: Any) -> Chat | None:
        """Wrap whatever a chat arrived as."""
        if isinstance(peer, types.User):
            # Read straight off the raw user instead of wrapping one first.
            # This runs for every private message that arrives, and the four
            # fields below are all a chat wants, so building a whole User to
            # read them and then dropping it was the most repeated piece of
            # wasted work on the incoming path.
            name = " ".join(part for part in (peer.first_name, peer.last_name) if part)
            return cls(
                id=peer.id,
                kind=PeerKind.BOT if peer.bot else PeerKind.USER,
                title=name or None,
                username=peer.username,
                raw=peer,
            )
        if isinstance(peer, types.Chat):
            return cls(
                id=peer.id,
                kind=PeerKind.CHAT,
                title=peer.title,
                members=peer.participants_count,
                raw=peer,
            )
        if isinstance(peer, types.ChatForbidden):
            return cls(id=peer.id, kind=PeerKind.CHAT, title=peer.title, raw=peer)
        if isinstance(peer, types.Channel):
            return cls(
                id=peer.id,
                kind=PeerKind.SUPERGROUP if peer.megagroup else PeerKind.CHANNEL,
                title=peer.title,
                username=peer.username,
                members=peer.participants_count or 0,
                raw=peer,
            )
        if isinstance(peer, types.ChannelForbidden):
            return cls(
                id=peer.id,
                kind=PeerKind.SUPERGROUP if peer.megagroup else PeerKind.CHANNEL,
                title=peer.title,
                raw=peer,
            )
        return None
