# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Remembering how to name people and chats.

MTProto names a peer with two numbers. The id is public and stable and is what
everything else refers to. The access hash is neither: it is issued to this
account for this peer, it is meaningless to anybody else, and there is no call
that simply returns one. A client learns hashes by being told them, in passing,
alongside almost every answer the server gives, and a client that does not write
them down cannot send a message to someone it saw a minute ago.

So this is not an optimization. It is the difference between being able to reach
a peer and not. What makes it also an optimization is rule P4: a peer that has
been seen once never costs a round trip again, because the lookup is a dict hit
in front of a bounded LRU in front of the session file.

One rule here is a correctness rule instead of a caching one. Some users and
channels arrive as *min* constructors, which means the server sent an outline of
someone it thinks we do not need the full story about. Their access hash is not
usable outside the exact context it arrived in, so a min peer is never learned.
Caching one would produce a hash that works today, in that chat, and fails
everywhere else, which is far worse than not knowing the peer at all.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ..errors import PeerNotFound
from ..raw import types
from ..storage import PeerKind, PeerRecord, PeerStore

if TYPE_CHECKING:
    # Annotations only. The abstract types have no runtime form, and importing
    # the module that names them would load the API schema at import time,
    # which is the thing rule P7 exists to stop.
    from ..raw import base

__all__ = [
    "PeerCache",
    "input_peer_for",
    "normalize_phone",
    "normalize_username",
    "record_for",
]

# How many peers to keep in memory. Each is a handful of fields, so this is
# cheap, and anything past it is one sqlite read away instead of gone.
CAPACITY = 10_000

# How many learned peers to let pile up before a background flush is worth
# doing. Update traffic carries the same handful of people over and over, so
# writing every one of them through would be a disk write per message.
FLUSH_EVERY = 64


# What people paste in front of a username, in the order a link stacks them:
# scheme, then host, then the at-sign someone typed anyway. www. is in here
# because a link copied from a desktop browser carries it and the name behind
# it is the same account. Every one of these contains a character from the
# guard in normalize_username below, which is what lets a bare name skip them.
_LINK_PREFIXES = ("https://", "http://", "www.", "t.me/", "telegram.me/", "@")

# What tells a decorated name from a bare one, and what a link puts after the
# name. A name holding none of these is already what it normalizes to.
_DECORATION = ("/", "?", ".", "@")


def normalize_username(username: str) -> str:
    """The spelling a username is stored and looked up under.

    Usernames are case insensitive and people paste them with an @, a t.me
    prefix, or both. Everything that reaches the cache has been through here,
    so a lookup only ever has to compare one form.
    """
    # Lowered once, up front, rather than per prefix. This runs for every peer
    # in every users vector on the update path, which made seven throwaway
    # copies of the same string the most repeated allocation in the client.
    name = username.strip().lower()
    # A name off the wire is bare, and a name with a link around it was typed by
    # a person once. Deciding which in four scans keeps the first case, which is
    # every peer in every users vector, from walking the whole list below.
    if "." not in name and "/" not in name and "@" not in name and "?" not in name:
        return name
    for prefix in _LINK_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix) :]
    # A link can carry a path or a query after the name.
    for separator in ("/", "?"):
        name = name.split(separator, 1)[0]
    return name


def normalize_phone(phone: str | None) -> str | None:
    """A phone number as digits, which is how Telegram spells them."""
    if phone is None:
        return None
    digits = "".join(character for character in phone if character.isdigit())
    return digits or None


def _usernames_of(peer: Any) -> tuple[str, ...]:
    """Every name this peer currently answers to.

    Accounts can hold several usernames now, only some of them active, plus the
    original single one. An inactive name routes nowhere, so it is left out
    rather than stored and later used to reach the wrong account.
    """
    names: list[str] = []
    legacy = getattr(peer, "username", None)
    if isinstance(legacy, str) and legacy:
        names.append(normalize_username(legacy))
    for entry in getattr(peer, "usernames", None) or ():
        if isinstance(entry, types.Username) and entry.active and entry.username:
            name = normalize_username(entry.username)
            if name not in names:
                names.append(name)
    return tuple(names)


def record_for(peer: Any) -> PeerRecord | None:
    """What to remember about one user or chat, or None if there is nothing.

    None covers three cases that look different and mean the same thing: an
    empty constructor, which carries an id and no way to use it; a min
    constructor, whose hash belongs to a context instead of to us; and a user
    the server sent without a hash at all.
    """
    if isinstance(peer, types.User):
        if peer.min or peer.access_hash is None:
            return None
        return PeerRecord(
            id=peer.id,
            kind=PeerKind.BOT if peer.bot else PeerKind.USER,
            access_hash=peer.access_hash,
            usernames=_usernames_of(peer),
            phone=normalize_phone(peer.phone),
        )

    if isinstance(peer, types.Channel):
        if peer.min or peer.access_hash is None:
            return None
        return PeerRecord(
            id=peer.id,
            kind=PeerKind.SUPERGROUP if peer.megagroup else PeerKind.CHANNEL,
            access_hash=peer.access_hash,
            usernames=_usernames_of(peer),
        )

    if isinstance(peer, types.ChannelForbidden):
        # Being thrown out of a channel does not make it unnameable, and the
        # hash still works for the calls that are left, such as leaving it.
        return PeerRecord(
            id=peer.id,
            kind=PeerKind.SUPERGROUP if peer.megagroup else PeerKind.CHANNEL,
            access_hash=peer.access_hash,
        )

    if isinstance(peer, (types.Chat, types.ChatForbidden)):
        # A basic group is addressed by id alone, so there is no hash to miss.
        return PeerRecord(id=peer.id, kind=PeerKind.CHAT)

    return None


def input_peer_for(record: PeerRecord) -> base.InputPeer:
    """The way to name this peer in a call."""
    if record.kind.is_user:
        return types.InputPeerUser(
            user_id=record.id, access_hash=record.access_hash
        )
    if record.kind.is_channel:
        return types.InputPeerChannel(
            channel_id=record.id, access_hash=record.access_hash
        )
    return types.InputPeerChat(chat_id=record.id)


class PeerCache:
    """Everything this session knows about how to reach people.

    Two layers: a bounded LRU in memory, and whatever the storage backend keeps
    between runs. Learning is synchronous and cheap, because it happens on the
    path every incoming update takes and must never wait for a disk. Writing to
    the backend happens in batches, when someone asks.
    """

    __slots__ = (
        "_store",
        "_capacity",
        "_flush_every",
        "_peers",
        "_usernames",
        "_phones",
        "_dirty",
        "_hits",
        "_misses",
    )

    def __init__(
        self,
        store: PeerStore,
        *,
        capacity: int = CAPACITY,
        flush_every: int = FLUSH_EVERY,
    ) -> None:
        if capacity < 1:
            raise ValueError("a cache that holds nothing is not a cache")
        self._store = store
        self._capacity = capacity
        self._flush_every = max(1, flush_every)
        self._peers: OrderedDict[int, PeerRecord] = OrderedDict()
        self._usernames: dict[str, int] = {}
        self._phones: dict[str, int] = {}
        self._dirty: dict[int, PeerRecord] = {}
        self._hits = 0
        self._misses = 0

    def __repr__(self) -> str:
        return (
            f"PeerCache(known={len(self._peers)}, pending={len(self._dirty)}, "
            f"hits={self._hits}, misses={self._misses})"
        )

    @property
    def size(self) -> int:
        """How many peers are in memory right now."""
        return len(self._peers)

    @property
    def pending(self) -> int:
        """How many learned peers have not reached the storage yet."""
        return len(self._dirty)

    @property
    def hits(self) -> int:
        """Lookups answered without touching the storage or the network."""
        return self._hits

    @property
    def misses(self) -> int:
        """Lookups that had to go further than memory."""
        return self._misses

    def kind_of(self, peer_id: int) -> PeerKind | None:
        """What sort of peer this id belongs to, if this session has met it.

        Memory only, and no round trip: a caller asking this is deciding which
        call to make, and a lookup that went to the network to find out would
        cost more than the call it is choosing between. Nothing for an id the
        session has not seen, which is the honest answer rather than a guess.
        """
        record = self._peers.get(peer_id)
        return record.kind if record is not None else None

    def learn(self, *peers: Any) -> int:
        """Take note of whatever users and chats have just arrived.

        Called with the users and chats vectors that come attached to almost
        every answer and every update container. Returns how many were worth
        remembering, which is fewer than were passed whenever some of them were
        min or empty.

        Synchronous on purpose. This sits on the update path, and an update path
        that awaits a disk is an update path that falls behind.
        """
        learned = 0
        for peer in peers:
            record = record_for(peer)
            if record is None:
                continue
            known = self._peers.get(record.id)
            if known == record:
                # Nothing new. Still counts as being seen, so it moves to the
                # young end of the LRU instead of being left to age out.
                self._peers.move_to_end(record.id)
                continue
            self._remember(record)
            self._dirty[record.id] = record
            learned += 1
        return learned

    def learn_all(self, peers: Iterable[Any]) -> int:
        """The same, for a vector that is already a sequence."""
        return self.learn(*peers)

    async def flush(self, *, force: bool = True) -> int:
        """Write what has been learned to the storage, and say how much.

        force is what separates the two callers. Anything shutting down or about
        to need the peers on disk asks for all of it; the update loop asks
        without forcing, which writes only once a batch has built up.
        """
        if not self._dirty:
            return 0
        if not force and len(self._dirty) < self._flush_every:
            return 0

        batch = self._dirty
        self._dirty = {}
        try:
            await self._store.put_peers(list(batch.values()))
        except Exception:
            # Whatever did not get written is still only in memory, and memory
            # is bounded. Putting it back means the next flush tries again
            # rather than the peer being quietly lost at eviction.
            for peer_id, record in batch.items():
                self._dirty.setdefault(peer_id, record)
            raise
        return len(batch)

    async def get(self, peer_id: int) -> PeerRecord | None:
        """What is known about this id, from memory or from the storage."""
        record = self._peers.get(peer_id)
        if record is not None:
            self._peers.move_to_end(peer_id)
            self._hits += 1
            return record

        self._misses += 1
        stored = await self._store.peer_by_id(peer_id)
        if stored is not None:
            self._remember(stored)
        return stored

    async def by_username(self, username: str) -> PeerRecord | None:
        """Whoever answers to this name, if this session has seen them."""
        name = normalize_username(username)
        if not name:
            return None
        peer_id = self._usernames.get(name)
        if peer_id is not None:
            record = self._peers.get(peer_id)
            if record is not None:
                self._peers.move_to_end(peer_id)
                self._hits += 1
                return record

        self._misses += 1
        stored = await self._store.peer_by_username(name)
        if stored is not None:
            self._remember(stored)
        return stored

    async def by_phone(self, phone: str) -> PeerRecord | None:
        """Whoever this number belongs to, if this session has seen them."""
        digits = normalize_phone(phone)
        if digits is None:
            return None
        peer_id = self._phones.get(digits)
        if peer_id is not None:
            record = self._peers.get(peer_id)
            if record is not None:
                self._peers.move_to_end(peer_id)
                self._hits += 1
                return record

        self._misses += 1
        stored = await self._store.peer_by_phone(digits)
        if stored is not None:
            self._remember(stored)
        return stored

    async def input_peer(self, peer_id: int) -> base.InputPeer:
        """Name this id in a call, or say plainly that it cannot be named."""
        record = await self.get(peer_id)
        if record is None:
            raise PeerNotFound(
                f"nothing is known about the peer {peer_id}. Resolve them by "
                "username once, or reach them from a chat or an update they "
                "appear in, and the hash is kept from then on"
            )
        return input_peer_for(record)

    async def forget(self, peer_id: int) -> bool:
        """Drop one peer everywhere, and say whether anything was there.

        The reason a peer is dropped is that the server would not accept the
        access hash we had for it, and a hash that is wrong is worse than no
        hash at all: with none, the next mention of that peer resolves again
        and works, while with a wrong one every call about them fails for as
        long as the session file lasts. So this reaches the storage as well as
        memory, and the pending batch too, which would otherwise write the bad
        record back out on the next flush.
        """
        self._dirty.pop(peer_id, None)
        record = self._peers.pop(peer_id, None)
        if record is not None:
            self._forget_lookups(record)
        dropped = await self._store.drop_peer(peer_id)
        return dropped or record is not None

    async def clear(self) -> None:
        """Forget everything, here and in the storage."""
        self._peers.clear()
        self._usernames.clear()
        self._phones.clear()
        self._dirty.clear()
        await self._store.clear_peers()

    def _remember(self, record: PeerRecord) -> None:
        """Put a record in memory, with its lookups, and evict if it is time."""
        old = self._peers.get(record.id)
        if old is not None:
            self._forget_lookups(old)

        self._peers[record.id] = record
        self._peers.move_to_end(record.id)
        for name in record.usernames:
            self._usernames[name] = record.id
        if record.phone is not None:
            self._phones[record.phone] = record.id

        while len(self._peers) > self._capacity:
            # Oldest out first (rule P6). Nothing is lost by this: a peer that
            # has not been written down yet is held by the pending batch as
            # well, so eviction costs it a lookup and never the record.
            _, evicted = self._peers.popitem(last=False)
            self._forget_lookups(evicted)

    def _forget_lookups(self, record: PeerRecord) -> None:
        for name in record.usernames:
            if self._usernames.get(name) == record.id:
                del self._usernames[name]
        if record.phone is not None and self._phones.get(record.phone) == record.id:
            del self._phones[record.phone]
