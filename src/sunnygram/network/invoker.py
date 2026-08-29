# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A session that outlives any one connection.

The connection below this is deliberately fragile: when its socket breaks it
ends every waiting call and stays down, because it has no way to know where to
reconnect to or which key to use. This is the layer that does know. It holds the
storage, so it can find the key for a datacenter or negotiate and keep a new
one, and it holds the decision about which datacenter is home, so it can follow
the server when it says the account lives somewhere else.

Two things a caller gets from that. A call survives a connection dropping
underneath it, and a call made to the wrong datacenter arrives at the right one.
Both are bounded: a server that keeps redirecting or a socket that keeps
breaking gives up instead of spinning.

Reusing a stored key starts a session with no idea what time the server thinks
it is, and MTProto message ids are timestamps, so the first exchange on one is
also a clock synchronization: our first id may well be refused, and the message
saying so is what sets the clock straight. A machine whose clock is badly out
therefore costs a round trip and nothing else.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Self, cast

from ..errors import (
    ChannelInvalid,
    ChatIdInvalid,
    InternalError,
    NetworkMigrate,
    PeerIdInvalid,
    PhoneMigrate,
    SunnygramError,
    Timeout,
    TransportError,
    UserIdInvalid,
    UserMigrate,
)
from ..crypto import PublicKey
from ..peers import PeerCache
from ..raw import functions, types
from ..session import Session
from ..storage import MemoryStorage, PeerStore, SessionState, Storage
from ..tl import TLFunction, TLObject, TLResult
from ..transport import Codec, Proxy, TCPTransport
from .config import cdn_address, cdn_keys
from .connection import ClientInfo, Connection, Stream
from .datacenter import Address, address_for
from .handshake import create_auth_key
from .limiter import RateLimiter

__all__ = ["Connector", "Invoker"]

_log = logging.getLogger(__name__)

# How a datacenter gets reached. The default opens a TCP connection to it, and
# anything else that can carry frames goes here instead: a proxy, an obfuscated
# wrapper, or a pair of queues standing in for a network.
Connector = Callable[[Address], Awaitable[Stream]]

# The errors that mean this account is answered by another datacenter. The file
# and stats ones are deliberately not here: they name where one resource lives,
# not where the account does, and moving home over them would be wrong.
_HOME_MIGRATE = (PhoneMigrate, NetworkMigrate, UserMigrate)

# The server having a moment instead of refusing: the 500 and -503 families,
# which is RPC_CALL_FAIL, WORKER_BUSY_TOO_LONG_RETRY, MSGID_DECREASE_RETRY, a
# timed-out internal call, and the rest of the names Telegram uses for "not
# right now". Every long-lived program meets these; none of them says anything
# is wrong with the call, and the remedy for all of them is to ask again.
# Written as the two hand-written roots rather than as a list of names, so that
# a name added to Telegram's table since the last refresh still lands in the
# right half by inheritance.
_TRANSIENT = (InternalError, Timeout)

# The refusals that mean "the peer you named is not one I will accept". Every
# one of them can be caused by an access hash that has stopped working, and a
# hash that has stopped working is kept in the session file, so without this it
# would go on being wrong on every run until someone deleted the file. They are
# not retried, because the call cannot be repaired without resolving the peer
# again, and that is the caller's next mention of them instead of this one.
_BAD_PEER = (
    PeerIdInvalid,
    ChannelInvalid,
    UserIdInvalid,
    ChatIdInvalid,
)

# How many times a call is worth sending again, and how long to wait between,
# doubling up to the ceiling.
MAX_ATTEMPTS = 4
BACKOFF = 0.5
MAX_BACKOFF = 8.0

UPDATES_QUEUE = 512


@dataclass(frozen=True, slots=True)
class _Cdn:
    """What it takes to reach one CDN datacenter, once it has been looked up."""

    address: Address
    keys: tuple[PublicKey, ...]

# How many connections a datacenter may have for bulk work, on top of the one
# that carries ordinary calls. Telegram meters a connection instead of an
# account, so a file split across several arrives several times sooner; past a
# handful the gain flattens and the account starts to look like a swarm.
BULK_CONNECTIONS = 4


class Invoker:
    """A session held open across connections and datacenters.

    Owns the storage and the current connection. Start it, invoke through it,
    close it; what happens in between to the socket is its problem, not
    the caller's.
    """

    __slots__ = (
        "_storage",
        "_client",
        "_state",
        "_connection",
        "_ipv6",
        "_connect",
        "_updates",
        "_peers",
        "_elsewhere",
        "_pools",
        "_bulk",
        "_busy",
        "_authorized",
        "_cdn",
        "_cdn_lock",
        "_attempts",
        "_backoff",
        "_limiter",
        "_lock",
        "_started",
        "_options",
        "_lost_updates",
    )

    def __init__(
        self,
        storage: Storage,
        *,
        client: ClientInfo,
        test_mode: bool = False,
        ipv6: bool = False,
        codec: Codec | None = None,
        connector: Connector | None = None,
        proxy: Proxy | None = None,
        obfuscated: bool = False,
        rate_limit: bool | RateLimiter = True,
        attempts: int = MAX_ATTEMPTS,
        backoff: float = BACKOFF,
        updates_queue: int = UPDATES_QUEUE,
        bulk_connections: int = BULK_CONNECTIONS,
        **options: Any,
    ) -> None:
        self._storage = storage
        self._client = client
        self._ipv6 = ipv6
        self._connect = (
            _tcp(codec, proxy=proxy, obfuscated=obfuscated, test=test_mode)
            if connector is None
            else connector
        )
        # Checked rather than trusted, because a call that is never attempted
        # leaves the loop below with nothing to raise, and the failure that
        # comes out of that says nothing about what was actually wrong.
        if attempts < 1:
            raise ValueError("a call has to be attempted at least once")
        if backoff < 0:
            raise ValueError("a backoff cannot be negative")
        self._attempts = attempts
        self._backoff = backoff
        # On unless turned off. An account is worth more than the throughput
        # that turning it off buys, so the default is the safe one (rule S4).
        self._limiter = _limiter_for(rate_limit)
        self._options = options
        self._state = SessionState(test_mode=test_mode)
        self._connection: Connection | None = None
        # One queue for the whole session, handed to each connection in turn.
        self._updates: asyncio.Queue[TLObject] = asyncio.Queue(updates_queue)
        # A backend that cannot keep peers still gets a cache, it just forgets
        # them when the process ends. Better than making the peer layer
        # optional and every call above it check whether it is there.
        self._peers = PeerCache(
            storage if isinstance(storage, PeerStore) else MemoryStorage()
        )
        # Connections to datacenters that are not home. Files live wherever
        # they were uploaded, so reaching one means talking to another
        # datacenter without moving the account to it.
        self._elsewhere: dict[int, Connection] = {}
        # Connections kept for work that is worth spreading, per datacenter.
        # Separate from the one above so that a file being pulled through four
        # sockets never delays a ping or an ordinary call.
        self._pools: dict[int, list[Connection]] = {}
        self._bulk = max(0, bulk_connections)
        # How many transfer calls are in hand for each datacenter right now,
        # which is what the pool is sized against. Counted instead of measured
        # from the connections themselves: a call that has been given a
        # connection but has not reached the wire yet is still demand, and a
        # pool that cannot see it never grows on a fast link.
        self._busy: dict[int, int] = {}
        self._authorized: set[int] = set()
        # CDN datacenters this session has looked up. Being in here is what
        # tells the rest of the invoker that a number is a CDN instead of one
        # of Telegram's own: it is reached at an address the config gave, it is
        # named by its own key, and it is never signed in to.
        self._cdn: dict[int, _Cdn] = {}
        # Its own lock, because looking a CDN up means making calls, and those
        # calls go through the machinery the connection lock guards.
        self._cdn_lock = asyncio.Lock()
        # Reconnecting and migrating both replace the connection, and two calls
        # noticing the same break must not each build one.
        self._lock = asyncio.Lock()
        self._started = False
        # Updates thrown away by connections that have since been replaced. The
        # live one keeps its own count, so the two together are what the update
        # layer reads, and a reconnect must not make the total go backwards.
        self._lost_updates = 0

    def __repr__(self) -> str:
        where = "not started" if not self._started else f"dc={self._state.dc_id}"
        return f"Invoker({where}, {self._storage!r})"

    @property
    def state(self) -> SessionState:
        """The session as it stands. Change it and call save."""
        return self._state

    @property
    def client(self) -> ClientInfo:
        """The application this session belongs to."""
        return self._client

    @property
    def updates(self) -> asyncio.Queue[TLObject]:
        """Everything the server sent that answered no call, across reconnects."""
        return self._updates

    @property
    def dropped_updates(self) -> int:
        """How many updates were thrown away because no one was draining them.

        Counted across connections rather than per connection, so that replacing
        one does not reset it. The update layer watches this: a number that has
        moved means something never arrived, and the only way to find out what
        it was is to ask for a difference.
        """
        live = self._connection.dropped_updates if self._connection is not None else 0
        return self._lost_updates + live

    @property
    def limiter(self) -> RateLimiter | None:
        """The pacing in force, or nothing if it was turned off.

        Worth reading instead of only setting. Its waited counter says how long
        this program has spent being held back, which is the honest measure of
        whether it is asking for more than the account can safely give.
        """
        return self._limiter

    @property
    def peers(self) -> PeerCache:
        """Who this session knows how to name, and how to look one up."""
        return self._peers

    @property
    def started(self) -> bool:
        """Whether this invoker has been started and not yet closed."""
        return self._started

    @property
    def open_connections(self) -> int:
        """How many sockets this session is holding open, everywhere."""
        return (
            (1 if self._connection is not None else 0)
            + len(self._elsewhere)
            + sum(len(pool) for pool in self._pools.values())
        )

    @property
    def connection(self) -> Connection | None:
        """The connection in use, if there is one right now."""
        return self._connection

    async def start(self) -> SessionState:
        """Load the session and connect to whichever datacenter is home."""
        if self._started:
            raise SunnygramError("this invoker is already started")
        await self._storage.open()
        stored = await self._storage.load()
        if stored.auth_keys or stored.authorized:
            # A session that has been used before decides for itself which
            # network it belongs to. Being asked for the other one is a mistake
            # worth naming instead of quietly honoring.
            if stored.test_mode != self._state.test_mode:
                raise SunnygramError(
                    "this session belongs to the "
                    f"{'test' if stored.test_mode else 'production'} network and "
                    f"was opened as {'test' if self._state.test_mode else 'production'}"
                )
            self._state = stored
        else:
            self._state.dc_id = stored.dc_id
        self._started = True
        await self._reconnect()
        return self._state

    async def save(self) -> None:
        """Write the session down as it stands."""
        await self._storage.save(self._state)

    async def close(self) -> None:
        """Put every connection down and let go of the storage."""
        async with self._lock:
            connection, self._connection = self._connection, None
            elsewhere, self._elsewhere = self._elsewhere, {}
            pools, self._pools = self._pools, {}
            self._authorized.clear()
            self._cdn.clear()
            if connection is not None:
                self._retire(connection)
                await connection.close()
            for other in elsewhere.values():
                await other.close()
            for pool in pools.values():
                for held in pool:
                    await held.close()
        self._started = False
        # Whatever was learned and not yet written goes down now, while there
        # is still a storage open to write it to.
        await self._peers.flush()
        await self._storage.close()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def invoke(
        self,
        request: TLFunction[TLResult],
        *,
        dc_id: int | None = None,
        bulk: bool = False,
        timeout: float | None = None,
    ) -> TLResult:
        """Call a TL function, following the server and the network as needed.

        The answer is typed as whatever the function says it is answered with,
        so nothing above this has to guess or assert what came back.

        A dropped connection is rebuilt and the call is sent again, and so is a
        call the server turned down with one of its "not right now" errors. That
        is safe for anything the server deduplicates, which is what random_id is
        for on the calls where it matters, and it is what makes a long-running
        program survive both a network that comes and goes and a datacenter
        having a bad minute.

        dc_id sends the call somewhere other than home, which is what files
        need: a document lives in the datacenter it was uploaded to, and
        fetching it must not move the account there. The first call to another
        datacenter signs in to it by exporting the authorization from home.

        bulk says this call is part of a transfer and should go through the
        connections kept for those. Telegram meters a connection rather than an
        account, so several of them move a file several times faster, and
        keeping that traffic off the main connection is what stops a download
        from delaying everything else. It is only right for calls whose order
        does not matter, which is why it is asked for instead of assumed.
        """
        if not self._started:
            raise SunnygramError("this invoker has not been started")

        # Before the attempt loop instead of inside it, because a retry is the
        # same call arriving late and paying for it twice would slow a shaky
        # network down for no reason (rule S4).
        if self._limiter is not None:
            await self._limiter.hold(request, bulk=bulk)

        target = self._state.dc_id if dc_id is None else dc_id
        spread = bulk and bool(self._bulk)
        if spread:
            self._busy[target] = self._busy.get(target, 0) + 1
        try:
            return cast(TLResult, await self._attempt(request, target, spread, timeout))
        finally:
            if spread:
                self._busy[target] -= 1

    async def _attempt(
        self,
        request: TLFunction[Any],
        target: int,
        spread: bool,
        timeout: float | None,
    ) -> Any:
        """The call itself, and everything worth trying again."""
        last: BaseException | None = None
        for attempt in range(self._attempts):
            connection: Connection | None = None
            try:
                # Opening the connection is inside the attempt too. A network
                # that is not there yet is the same kind of problem as one that
                # went away mid-call, and waiting a moment fixes both.
                connection = await self._live_at(target, bulk=spread)
                answer = await connection.invoke(request, timeout=timeout)
                await self._absorb_peers(answer)
                return answer
            except _HOME_MIGRATE as migrate:
                if target != self._state.dc_id:
                    # Somewhere that is not home saying the account lives
                    # elsewhere says nothing about where home is.
                    raise
                # Not a failed attempt in spirit, but still counted: a server
                # that keeps redirecting has to stop somewhere.
                last = migrate
                await self.migrate(migrate.dc_id)
                target = self._state.dc_id
            except _BAD_PEER as refused:
                # Not retried and not swallowed: the call still fails, and the
                # caller still sees why. What this does is stop it failing for
                # ever. The hash we named the peer with is the most likely
                # reason the server said no, and it is on disk, so the next run
                # would name them exactly the same wrong way.
                await self._forget_named_peers(request, refused)
                raise
            except _TRANSIENT as hiccup:
                # Nothing is broken: the connection is fine and the call is not
                # wrong, the server just could not do it this second. Waiting a
                # moment and asking again is the whole remedy, and doing it here
                # is what stops every caller in every program from having to
                # write the same loop around every call.
                last = hiccup
                _log.info(
                    "dc %d could not do %s just now (%s), asking again",
                    target,
                    request.QUALNAME,
                    hiccup,
                )
                if attempt + 1 < self._attempts:
                    await asyncio.sleep(min(self._backoff * 2**attempt, MAX_BACKOFF))
            except TransportError as broken:
                last = broken
                _log.info(
                    "the connection to dc %d broke during %s (%s), rebuilding it",
                    target,
                    request.QUALNAME,
                    broken,
                )
                await self._forget(connection, target)
                if attempt + 1 < self._attempts:
                    await asyncio.sleep(min(self._backoff * 2**attempt, MAX_BACKOFF))

        assert last is not None
        _log.warning(
            "giving up on %s after %d attempts: %s",
            request.QUALNAME,
            self._attempts,
            last,
        )
        raise last

    async def migrate(self, dc_id: int) -> None:
        """Move home to another datacenter and connect there.

        Each datacenter issues its own authorization key, so moving before
        logging in simply means negotiating another one. Moving an account that
        is already logged in is the login-time path this was written for; a call
        that merely has to happen somewhere else takes dc_id on invoke instead
        and leaves home where it is.
        """
        if dc_id == self._state.dc_id and self._connection is not None:
            return
        _log.info("this account is answered by dc %d, moving home there", dc_id)
        self._state.dc_id = dc_id
        await self.save()
        await self._reconnect()

    async def prepare_cdn(self, dc_id: int) -> None:
        """Find out where a CDN datacenter is, before anything is sent to it.

        Called with the number out of a CDN redirect. Two questions go to the
        datacenter we are already talking to: where that number lives, which
        only help.getConfig knows, and which public key names it, which only
        help.getCdnConfig knows. From then on invoke(dc_id=...) reaches it like
        anywhere else, except that no authorization is exported to it, because
        it holds none and asking would tell it who we are.

        Idempotent, and asked for rather than done automatically: a number that
        has not been through here is treated as one of Telegram's own.
        """
        if dc_id in self._cdn:
            return
        async with self._cdn_lock:
            if dc_id in self._cdn:
                return
            config = await self.invoke(functions.help.GetConfig())
            if not isinstance(config, types.Config):
                raise SunnygramError(
                    f"expected a config, got {type(config).__name__}"
                )
            keys = await self.invoke(functions.help.GetCdnConfig())
            if not isinstance(keys, types.CdnConfig):
                raise SunnygramError(
                    f"expected a CDN config, got {type(keys).__name__}"
                )
            self._cdn[dc_id] = _Cdn(
                cdn_address(config.dc_options, dc_id, ipv6=self._ipv6),
                cdn_keys(keys, dc_id),
            )

    def is_cdn(self, dc_id: int) -> bool:
        """Whether this number has been looked up as a CDN datacenter."""
        return dc_id in self._cdn

    async def _absorb_peers(self, answer: Any) -> None:
        """Learn the people and chats an answer happened to carry.

        Nearly every call that touches a chat answers with the users and chats
        it mentions, precisely so a client can know who they are. Taking them
        here instead of in each method is what makes the cache fill itself:
        history, dialogs, a member list and a sent message all pay in without
        knowing this layer exists.
        """
        users = getattr(answer, "users", None)
        chats = getattr(answer, "chats", None)
        learned = 0
        if isinstance(users, list):
            learned += self._peers.learn(*users)
        if isinstance(chats, list):
            learned += self._peers.learn(*chats)
        if learned:
            await self._peers.flush(force=False)

    async def _live(self) -> Connection:
        """The current connection, rebuilt first if it is not usable."""
        connection = self._connection
        if connection is None or not connection.running:
            await self._reconnect()
            connection = self._connection
        assert connection is not None
        return connection

    async def _live_at(self, dc_id: int, *, bulk: bool = False) -> Connection:
        """A usable connection to one datacenter, for one call."""
        if bulk and self._bulk:
            return await self._from_pool(dc_id)
        return await self._main_at(dc_id)

    async def _from_pool(self, dc_id: int) -> Connection:
        """One of the connections kept for transfers, opening another if needed.

        The pool grows to match how many transfer calls are in hand at once,
        and no further: one file part at a time keeps using one connection,
        four workers end up with four. Whichever connection has the least
        outstanding takes the call, so a slow answer on one does not hold up
        the next.
        """
        # The account has to be known here before anything is sent, and the
        # main connection is what does that.
        await self._main_at(dc_id)

        pool = self._pools.setdefault(dc_id, [])
        pool[:] = [held for held in pool if held.running]
        wanted = min(self._bulk, max(1, self._busy.get(dc_id, 1)))
        if len(pool) < wanted:
            async with self._lock:
                # Checked again under the lock: several parts starting together
                # would otherwise each open the same missing connection.
                if len(pool) < wanted:
                    fresh = await self._open(dc_id)
                    pool.append(fresh)
                    return fresh
        if not pool:
            return await self._main_at(dc_id)
        return min(pool, key=lambda held: held.in_flight)

    async def _main_at(self, dc_id: int) -> Connection:
        """The connection that carries ordinary calls to one datacenter."""
        if dc_id == self._state.dc_id:
            return await self._live()

        connection = self._elsewhere.get(dc_id)
        if connection is None or not connection.running:
            async with self._lock:
                # Checked again under the lock: two file parts starting at once
                # must not each open a connection to the same place.
                stale = self._elsewhere.pop(dc_id, None)
                if stale is not None and stale.running:
                    self._elsewhere[dc_id] = stale
                    connection = stale
                else:
                    if stale is not None:
                        await stale.close()
                        self._authorized.discard(dc_id)
                    self._elsewhere[dc_id] = connection = await self._open(dc_id)
        await self._sign_in_at(dc_id)
        return connection

    async def _sign_in_at(self, dc_id: int) -> None:
        """Make an account known to a datacenter it has never spoken to.

        A key negotiated with another datacenter is a stranger there: it can
        speak the protocol but it is no one. Home issues a short-lived
        authorization for it, which the other end imports, and from then on the
        two are the same account. A session that has not logged in has nothing
        to export and needs none of this.

        A CDN datacenter is the exception that proves the rule. It is not
        Telegram, it holds no accounts, and the whole point of the arrangement
        is that it never learns whose file it is handing over, so nothing is
        exported to one.
        """
        if not self._state.authorized or dc_id in self._authorized:
            return
        if dc_id in self._cdn:
            return
        # Recorded before the calls instead of after, because importing is
        # itself a call to this datacenter and would otherwise come straight
        # back here.
        self._authorized.add(dc_id)
        try:
            exported = await self.invoke(
                functions.auth.ExportAuthorization(dc_id=dc_id)
            )
            if not isinstance(exported, types.auth.ExportedAuthorization):
                raise SunnygramError(
                    f"expected an exported authorization, got "
                    f"{type(exported).__name__}"
                )
            await self.invoke(
                functions.auth.ImportAuthorization(
                    id=exported.id, bytes=exported.bytes
                ),
                dc_id=dc_id,
            )
        except BaseException:
            self._authorized.discard(dc_id)
            raise

    async def _forget_named_peers(self, request: TLObject, refused: Exception) -> None:
        """Drop whatever peers a refused call named, so the next one re-resolves.

        Says so through the logger rather than doing it quietly (rule C3): a
        cache that silently discarded things would be indistinguishable from a
        cache that never learned them, and the first question anybody asks when
        a program starts making an extra call is what changed.
        """
        for peer_id in sorted(_peers_named_in(request)):
            if await self._peers.forget(peer_id):
                _log.warning(
                    "%s was refused with %s, so the access hash held for peer "
                    "%d has been dropped: naming them again resolves them "
                    "afresh instead of failing the same way",
                    request.QUALNAME,
                    type(refused).__name__,
                    peer_id,
                )

    async def _forget(self, broken: Connection | None, dc_id: int) -> None:
        """Put down the connection a call died on, whichever one it was.

        A pooled connection breaking costs only itself: it leaves the pool and
        the next call opens another. The main one breaking costs the sign-in
        with it, since a new key would have to be introduced to the datacenter
        all over again.
        """
        async with self._lock:
            pool = self._pools.get(dc_id)
            if broken is not None and pool is not None and broken in pool:
                pool.remove(broken)
                await broken.close()
                return
            if dc_id != self._state.dc_id:
                connection = self._elsewhere.pop(dc_id, None)
                self._authorized.discard(dc_id)
            else:
                connection, self._connection = self._connection, None
                self._retire(connection)
        if connection is not None:
            await connection.close()

    def _retire(self, connection: Connection | None) -> None:
        """Keep what a connection lost before letting go of it.

        Only the home connection feeds updates, and it is the one being replaced
        whenever this matters. Its count of thrown-away updates has to survive
        it, or a reconnect would hide the very losses the reconnect caused.
        """
        if connection is not None:
            self._lost_updates += connection.dropped_updates

    async def _reconnect(self) -> None:
        async with self._lock:
            old, self._connection = self._connection, None
            if old is not None:
                self._retire(old)
                await old.close()
            self._connection = await self._open(self._state.dc_id, updates=True)

    async def _open(self, dc_id: int, *, updates: bool = False) -> Connection:
        """Build a connection to a datacenter, with a key for it.

        Only home feeds the shared updates queue. Another datacenter holds the
        same account once the authorization is imported, so it may well have
        something to say, but the update state machine counts one stream and
        two of them arriving would be a gap that is not there.

        A CDN datacenter is reached at the address its config entry gave and
        has to prove itself with the key that came with it, so neither the
        built-in address table nor the built-in keys apply.
        """
        cdn = self._cdn.get(dc_id)
        _log.debug("opening a connection to dc %d", dc_id)
        where = (
            cdn.address
            if cdn is not None
            else address_for(dc_id, test=self._state.test_mode, ipv6=self._ipv6)
        )
        transport = await self._connect(where)
        try:
            key = self._state.auth_key(dc_id)
            if key is None:
                _log.info("negotiating an authorization key with dc %d", dc_id)
                negotiated = await create_auth_key(
                    transport,
                    dc_id=dc_id,
                    test=self._state.test_mode,
                    keys=cdn.keys if cdn is not None else None,
                )
                self._state.set_auth_key(dc_id, negotiated.key)
                await self.save()
                session = Session(
                    negotiated.key,
                    salt=negotiated.salt,
                    time_offset=negotiated.time_offset,
                )
            else:
                # A stored key comes with no salt: the first call gets a
                # bad_server_salt and the connection adopts the current one,
                # which is the same path an expired salt takes anyway.
                session = Session(key)
            connection = Connection(
                transport,
                session,
                dc_id=dc_id,
                client=self._client,
                updates=self._updates if updates else None,
                **self._options,
            )
            await connection.start()
        except BaseException:
            await transport.close()
            raise
        return connection


_WALK_DEPTH = 8


def _peers_named_in(request: object) -> set[int]:
    """Every peer id a request refers to, however deeply it is buried.

    A call names its peer in a different field in every method, and sometimes
    in a list of them or inside a nested object, so this walks instead of
    looking in one place. Bounded by depth because the cost of the walk should
    not depend on how big the thing being sent is, and a file part is a large
    thing being sent.
    """
    found: set[int] = set()
    _walk_for_peers(request, found, 0)
    return found


def _walk_for_peers(value: object, found: set[int], depth: int) -> None:
    if depth > _WALK_DEPTH:
        return
    if isinstance(value, (types.InputPeerUser, types.InputUser)):
        found.add(value.user_id)
        return
    if isinstance(value, (types.InputPeerChannel, types.InputChannel)):
        found.add(value.channel_id)
        return
    # InputPeerChat carries no access hash, so it has nothing that can go stale
    # and nothing worth dropping. Nor do the Self and Empty forms.
    if isinstance(value, (list, tuple)):
        for item in value:
            _walk_for_peers(item, found, depth + 1)
        return
    if isinstance(value, TLObject):
        for name in getattr(type(value), "__slots__", ()):
            _walk_for_peers(getattr(value, name, None), found, depth + 1)


def _limiter_for(asked: bool | RateLimiter) -> RateLimiter | None:
    """What rate_limit=... means: a limiter, the default one, or none at all."""
    if isinstance(asked, RateLimiter):
        return asked
    return RateLimiter() if asked else None


def _tcp(
    codec: Codec | None,
    *,
    proxy: Proxy | None = None,
    obfuscated: bool = False,
    test: bool = False,
) -> Connector:
    """The default way to reach a datacenter: open a socket to it.

    Through a proxy the socket goes to the proxy instead, and an MTProxy needs
    to be told which datacenter this is, since it forwards by id instead of by
    the address that was dialled. A test datacenter is spelled as a negative id
    there, which is the only place in the library where that is true.
    """

    async def connect(where: Address) -> Stream:
        transport = TCPTransport(
            codec,
            proxy=proxy,
            dc_id=-where.dc_id if test else where.dc_id,
            obfuscated=obfuscated,
        )
        await transport.connect(where.host, where.port)
        return transport

    return connect
