# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A session that lives only as long as the process does.

The right choice for a test, for a one-off script, and for anything that gets
its key from somewhere else and has nowhere to put it. It is also the base the
string session builds on, since a string session is a memory session that knows
how to spell itself.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from .base import PeerRecord, PeerStore, SessionState, Storage

__all__ = ["MemoryStorage"]


class MemoryStorage(Storage, PeerStore):
    """A session kept in a variable."""

    __slots__ = ("_state", "_peers", "_usernames", "_phones")

    def __init__(self, state: SessionState | None = None) -> None:
        self._state = SessionState() if state is None else state
        self._peers: dict[int, PeerRecord] = {}
        self._usernames: dict[str, int] = {}
        self._phones: dict[str, int] = {}

    def __repr__(self) -> str:
        return f"MemoryStorage({self._state!r})"

    async def load(self) -> SessionState:
        # A copy, so a caller holding the result cannot change what is stored
        # without saying so through save. The file backends behave that way by
        # nature, and the three have to be interchangeable.
        return deepcopy(self._state)

    async def save(self, state: SessionState) -> None:
        self._state = deepcopy(state)

    async def delete(self) -> None:
        self._state = SessionState()
        await self.clear_peers()

    async def put_peers(self, peers: Sequence[PeerRecord]) -> None:
        for peer in peers:
            # A peer that has been renamed leaves its old spellings behind,
            # which would otherwise go on pointing at it for ever.
            old = self._peers.get(peer.id)
            if old is not None:
                for name in old.usernames:
                    self._usernames.pop(name, None)
                if old.phone is not None:
                    self._phones.pop(old.phone, None)

            self._peers[peer.id] = peer
            for name in peer.usernames:
                self._usernames[name] = peer.id
            if peer.phone is not None:
                self._phones[peer.phone] = peer.id

    async def peer_by_id(self, peer_id: int) -> PeerRecord | None:
        return self._peers.get(peer_id)

    async def peer_by_username(self, username: str) -> PeerRecord | None:
        peer_id = self._usernames.get(username)
        return None if peer_id is None else self._peers.get(peer_id)

    async def peer_by_phone(self, phone: str) -> PeerRecord | None:
        peer_id = self._phones.get(phone)
        return None if peer_id is None else self._peers.get(peer_id)

    async def peer_count(self) -> int:
        return len(self._peers)

    async def drop_peer(self, peer_id: int) -> bool:
        record = self._peers.pop(peer_id, None)
        if record is None:
            return False
        for name in record.usernames:
            if self._usernames.get(name) == peer_id:
                del self._usernames[name]
        if record.phone is not None and self._phones.get(record.phone) == peer_id:
            del self._phones[record.phone]
        return True

    async def clear_peers(self) -> None:
        self._peers.clear()
        self._usernames.clear()
        self._phones.clear()
