# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""What a session is, and where it can be kept.

A session is a small amount of state that has to outlive the process: which
datacenter is home, the authorization key for it, and who the key belongs to.
Losing it means logging in again, and logging in repeatedly is exactly what
Telegram treats as suspicious, so keeping it is not a convenience.

The interface is deliberately coarse. The whole thing is loaded once when a
client starts and written back when something about it changes, which is rarely.
The peer cache is the exception, and it has its own interface here: it is large,
it grows a row at a time, and it is read by one key at a time instead of
wholesale, so it would be wrong to fold it into the load-and-save shape.

Everything is async because one of the backends touches a disk, and a disk must
not be touched from the event loop (rule P1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import TracebackType
from typing import Self

from ..crypto import AUTH_KEY_SIZE

__all__ = [
    "PeerKind",
    "PeerRecord",
    "PeerStore",
    "SessionState",
    "Storage",
    "UpdateState",
]


@dataclass(slots=True)
class UpdateState:
    """How far through the stream of updates this session has read.

    Four numbers for the account as a whole and one per channel. They are the
    difference between reconnecting and picking up where we left off, and
    reconnecting and being told everything that ever happened, so they are worth
    keeping even though they can always be fetched again.

    Nothing here is a secret, but everything here is a correctness problem: a
    pts that is ahead of what was really applied silently loses messages.
    """

    pts: int = 0
    qts: int = 0
    date: int = 0
    seq: int = 0
    channels: dict[int, int] = field(default_factory=dict)

    @property
    def known(self) -> bool:
        """Whether this session has ever been told where the stream is."""
        return self.pts != 0 or self.date != 0


@dataclass(slots=True)
class SessionState:
    """Everything about a session that has to survive a restart.

    The keys are per datacenter because each one issues its own, and a client
    that has been to more than one datacenter for files or a migration holds
    several. dc_id names the one that is home: the one that answers for the
    account.
    """

    dc_id: int = 2
    test_mode: bool = False
    user_id: int = 0
    is_bot: bool = False
    auth_keys: dict[int, bytes] = field(default_factory=dict)
    updates: UpdateState = field(default_factory=UpdateState)

    def __repr__(self) -> str:
        # Never a key, not even its length in a way that identifies it (rule S2).
        return (
            f"SessionState(dc_id={self.dc_id}, test_mode={self.test_mode}, "
            f"user_id={self.user_id}, is_bot={self.is_bot}, "
            f"keys_for={sorted(self.auth_keys)}, pts={self.updates.pts})"
        )

    @property
    def authorized(self) -> bool:
        """Whether this session has been through a login."""
        return self.user_id != 0

    def auth_key(self, dc_id: int | None = None) -> bytes | None:
        """The key for a datacenter, or None if there has never been one."""
        return self.auth_keys.get(self.dc_id if dc_id is None else dc_id)

    def set_auth_key(self, dc_id: int, key: bytes | None) -> None:
        """Record or forget the key for a datacenter."""
        if key is None:
            self.auth_keys.pop(dc_id, None)
            return
        if len(key) != AUTH_KEY_SIZE:
            raise ValueError(f"an auth key is {AUTH_KEY_SIZE} bytes, got {len(key)}")
        self.auth_keys[dc_id] = key


class PeerKind(StrEnum):
    """What sort of thing a peer is.

    The distinction that matters to the protocol is only three ways, since that
    is how many kinds of input peer there are. The other two are kept because
    they are free to record and a caller usually wants to know: whether the user
    on the other end is a person or a bot, and whether a channel is a broadcast
    or a group people talk in.
    """

    USER = "user"
    BOT = "bot"
    CHAT = "chat"
    CHANNEL = "channel"
    SUPERGROUP = "supergroup"

    @property
    def is_user(self) -> bool:
        return self in (PeerKind.USER, PeerKind.BOT)

    @property
    def is_channel(self) -> bool:
        return self in (PeerKind.CHANNEL, PeerKind.SUPERGROUP)


@dataclass(frozen=True, slots=True)
class PeerRecord:
    """What has to be remembered about a peer to be able to name it again.

    Almost nothing, deliberately. This is a cache for reaching people, not a
    model of them: an id, the hash that goes with it, and the two things a
    person might type instead of an id. Names, photos and the rest belong to
    whatever fetched them.

    A basic group has no access hash at all, so zero there is not a missing
    value, it is the right one.
    """

    id: int
    kind: PeerKind
    access_hash: int = 0
    usernames: tuple[str, ...] = ()
    phone: str | None = None

    @property
    def username(self) -> str | None:
        """The first username, for the common case of there being one."""
        return self.usernames[0] if self.usernames else None


class PeerStore:
    """Where a peer cache keeps what it has learned.

    Separate from Storage because it is used differently: written a handful of
    rows at a time as peers arrive, and read one key at a time when someone
    names a peer. A backend is free to implement both, and the ones that ship
    with Sunnygram do.

    Usernames and phone numbers arrive here already normalized by the cache
    above, so an implementation can compare them as it stores them.
    """

    __slots__ = ()

    async def put_peers(self, peers: Sequence[PeerRecord]) -> None:
        """Write these peers down, replacing any earlier record of them."""
        raise NotImplementedError

    async def peer_by_id(self, peer_id: int) -> PeerRecord | None:
        raise NotImplementedError

    async def peer_by_username(self, username: str) -> PeerRecord | None:
        raise NotImplementedError

    async def peer_by_phone(self, phone: str) -> PeerRecord | None:
        raise NotImplementedError

    async def peer_count(self) -> int:
        """How many peers are on record. Mostly here for tests and for docs."""
        raise NotImplementedError

    async def drop_peer(self, peer_id: int) -> bool:
        """Forget one peer, and say whether there was one.

        Here rather than only in memory because the reason a peer gets dropped
        is that its access hash stopped working, and a hash that is wrong in
        the file is wrong again on the next run. Forgetting it anywhere but
        here would fix a program until it restarted.
        """
        raise NotImplementedError

    async def clear_peers(self) -> None:
        """Forget every peer. A logout ends here along with the key."""
        raise NotImplementedError


class Storage:
    """Somewhere a session can be kept.

    Subclasses decide what that means: memory, a file, a string you carry
    around. All three are interchangeable, which lets a program be
    written once and moved between them.
    """

    __slots__ = ()

    async def open(self) -> None:
        """Get ready to be read from. Called once, before load."""

    async def load(self) -> SessionState:
        """Read the session back, or a fresh one if nothing was ever saved."""
        raise NotImplementedError

    async def save(self, state: SessionState) -> None:
        """Write the session down, replacing whatever was there."""
        raise NotImplementedError

    async def delete(self) -> None:
        """Forget the session entirely. Logging out ends here."""
        raise NotImplementedError

    async def close(self) -> None:
        """Let go of whatever open handle this backend holds."""

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()
