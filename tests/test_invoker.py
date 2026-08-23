"""The session that outlives its connections.

The datacenters here are queues, handed out by a connector the invoker is given
instead of the one that opens sockets. That is the whole point of the seam: a
test can refuse a connection, break one halfway through a call, or answer from a
different datacenter than the one that was asked, and watch what the invoker
does about it.

The storage is real. Which key ends up in it, and when, is half of what these
tests are checking.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, NEAREST, ScriptedServer, Wire, a_call
from sunnygram.errors import (
    BadRequest,
    FileMigrate,
    SunnygramError,
    Timeout,
    TransportClosed,
)
from sunnygram.network import Address, ClientInfo, Invoker, address_for
from sunnygram.network.handshake import AuthKey
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345)
OTHER_KEY = bytes(range(255, -1, -1))


class Network:
    """A fake network: every connection attempt gets its own pair of queues."""

    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []
        self.refuse = 0

    async def connect(self, where: Address) -> Wire:
        if self.refuse:
            self.refuse -= 1
            raise TransportClosed(f"nothing is listening on {where.host}")
        wire = Wire()
        self.wires.append((where, wire))
        return wire

    @property
    def latest(self) -> Wire:
        return self.wires[-1][1]

    @property
    def datacenters(self) -> list[int]:
        """Which datacenters were reached, in the order they were reached."""
        return [where.dc_id for where, _ in self.wires]


def seeded(dc_id: int = 2, keys: dict[int, bytes] | None = None) -> MemoryStorage:
    """A storage that already knows a key, so no handshake is needed."""
    state = SessionState(dc_id=dc_id)
    for where, key in (keys or {dc_id: AUTH_KEY}).items():
        state.set_auth_key(where, key)
    return MemoryStorage(state)


@asynccontextmanager
async def live(
    storage: MemoryStorage | None = None, **options: Any
) -> AsyncIterator[tuple[Invoker, Network]]:
    """A started invoker and the network it is connected through."""
    network = Network()
    options.setdefault("ping_interval", None)
    options.setdefault("backoff", 0.01)
    invoker = Invoker(
        seeded() if storage is None else storage,
        client=CLIENT,
        connector=network.connect,
        **options,
    )
    await invoker.start()
    try:
        yield invoker, network
    finally:
        await invoker.close()


def server_for(invoker: Invoker, network: Network, **options: Any) -> ScriptedServer:
    """The datacenter on the other end of the invoker's current connection."""
    connection = invoker.connection
    assert connection is not None
    return ScriptedServer(network.latest, connection.session, **options)


class TestStarting:
    async def test_it_connects_to_the_datacenter_the_session_names(self):
        async with live(seeded(dc_id=4, keys={4: AUTH_KEY})) as (invoker, network):
            assert network.datacenters == [4]
            assert invoker.state.dc_id == 4

    async def test_a_stored_key_is_used_rather_than_negotiated(self):
        async with live() as (invoker, network):
            server = server_for(invoker, network)
            call = asyncio.create_task(invoker.invoke(a_call()))
            request = await asyncio.wait_for(server.take(), 5)
            # Only a connection already holding the key could have been read.
            await server.answer(request.msg_id, NEAREST)
            assert (await call).country == "IT"

    async def test_a_missing_key_is_negotiated_and_kept(self, monkeypatch):
        import sunnygram.network.invoker as module

        async def handshake(wire, *, dc_id, test=False, keys=None):
            return AuthKey(key=AUTH_KEY, salt=7, time_offset=0.0)

        monkeypatch.setattr(module, "create_auth_key", handshake)
        storage = MemoryStorage()
        async with live(storage) as (invoker, _network):
            assert invoker.state.auth_key(2) == AUTH_KEY
        # And it reached the storage, so the next run costs no round trips.
        assert (await storage.load()).auth_key(2) == AUTH_KEY

    async def test_starting_twice_is_refused(self):
        async with live() as (invoker, _network):
            with pytest.raises(SunnygramError, match="already started"):
                await invoker.start()

    async def test_invoking_before_starting_is_refused(self):
        invoker = Invoker(seeded(), client=CLIENT, connector=Network().connect)
        with pytest.raises(SunnygramError, match="not been started"):
            await invoker.invoke(a_call())

    async def test_a_session_from_the_other_network_is_refused(self):
        state = SessionState(dc_id=2, test_mode=True)
        state.set_auth_key(2, AUTH_KEY)
        network = Network()
        invoker = Invoker(
            MemoryStorage(state), client=CLIENT, connector=network.connect
        )
        with pytest.raises(SunnygramError, match="test network"):
            await invoker.start()

    async def test_a_fresh_session_takes_the_network_it_is_given(self, monkeypatch):
        import sunnygram.network.invoker as module

        async def handshake(wire, *, dc_id, test=False, keys=None):
            assert test is True, "the handshake was told the wrong network"
            return AuthKey(key=AUTH_KEY, salt=0, time_offset=0.0)

        monkeypatch.setattr(module, "create_auth_key", handshake)
        async with live(MemoryStorage(), test_mode=True) as (invoker, network):
            assert invoker.state.test_mode is True
            # The test datacenters are a different table of addresses.
            assert network.wires[0][0] == address_for(2, test=True)
            assert network.wires[0][0] != address_for(2)


class TestMigration:
    async def test_it_follows_the_account_to_another_datacenter(self):
        storage = seeded(keys={2: AUTH_KEY, 4: AUTH_KEY})
        async with live(storage) as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            first = server_for(invoker, network)
            request = await asyncio.wait_for(first.take(), 5)
            await first.refuse(request.msg_id, 303, "PHONE_MIGRATE_4")

            # The invoker opens a connection to DC 4 and asks again there.
            await _until(lambda: len(network.wires) == 2)
            second = server_for(invoker, network)
            again = await asyncio.wait_for(second.take(), 5)
            await second.answer(again.msg_id, NEAREST)
            assert (await asyncio.wait_for(call, 5)).country == "IT"
            assert network.datacenters == [2, 4]
            assert invoker.state.dc_id == 4

    async def test_a_datacenter_we_have_never_met_gets_its_own_key(
        self, monkeypatch
    ):
        # Keys are per datacenter, so following a migration to one we have no
        # key for costs a handshake before anything can be asked there.
        import sunnygram.network.invoker as module

        negotiated = []

        async def handshake(wire, *, dc_id, test=False, keys=None):
            negotiated.append(dc_id)
            return AuthKey(key=OTHER_KEY, salt=0, time_offset=0.0)

        monkeypatch.setattr(module, "create_auth_key", handshake)
        storage = seeded()
        async with live(storage) as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            first = server_for(invoker, network)
            request = await asyncio.wait_for(first.take(), 5)
            await first.refuse(request.msg_id, 303, "PHONE_MIGRATE_4")

            await _until(lambda: len(network.wires) == 2)
            second = server_for(invoker, network, auth_key=OTHER_KEY)
            again = await asyncio.wait_for(second.take(), 5)
            await second.answer(again.msg_id, NEAREST)
            await asyncio.wait_for(call, 5)

        assert negotiated == [4]
        stored = await storage.load()
        assert stored.auth_keys == {2: AUTH_KEY, 4: OTHER_KEY}

    async def test_the_new_home_is_written_down(self):
        storage = seeded(keys={2: AUTH_KEY, 4: OTHER_KEY})
        async with live(storage) as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            first = server_for(invoker, network)
            request = await asyncio.wait_for(first.take(), 5)
            await first.refuse(request.msg_id, 303, "USER_MIGRATE_4")
            await _until(lambda: len(network.wires) == 2)
            # The key for DC 4 was already known, so it was used as it was.
            second = server_for(invoker, network, auth_key=OTHER_KEY)
            again = await asyncio.wait_for(second.take(), 5)
            await second.answer(again.msg_id, NEAREST)
            await asyncio.wait_for(call, 5)
        assert (await storage.load()).dc_id == 4

    async def test_a_file_that_lives_elsewhere_does_not_move_home(self):
        # FILE_MIGRATE names where one file is, not where the account is, so
        # following it would take the session to the wrong datacenter.
        async with live() as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            server = server_for(invoker, network)
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 303, "FILE_MIGRATE_5")
            with pytest.raises(FileMigrate) as info:
                await asyncio.wait_for(call, 5)
            assert info.value.dc_id == 5
            assert invoker.state.dc_id == 2
            assert network.datacenters == [2]

    async def test_migrating_where_we_already_are_changes_nothing(self):
        async with live() as (invoker, network):
            await invoker.migrate(2)
            assert network.datacenters == [2]


class TestReconnecting:
    async def test_a_broken_connection_is_rebuilt_and_the_call_retried(self):
        async with live() as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            first = server_for(invoker, network)
            await asyncio.wait_for(first.take(), 5)
            first.wire.break_it()

            await _until(lambda: len(network.wires) == 2)
            second = server_for(invoker, network)
            again = await asyncio.wait_for(second.take(), 5)
            await second.answer(again.msg_id, NEAREST)
            assert (await asyncio.wait_for(call, 5)).country == "IT"

    async def test_a_server_having_a_moment_is_asked_again(self):
        # The 500 family is not a refusal, it is "not right now". Passing it up
        # makes every caller in every program write the same retry loop, and
        # most of them never do, which is why a busy hour on Telegram's side
        # reads to a user as the library being broken.
        async with live() as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            server = server_for(invoker, network)
            first = await asyncio.wait_for(server.take(), 5)
            await server.refuse(first.msg_id, 500, "RPC_CALL_FAIL")

            again = await asyncio.wait_for(server.take(), 5)
            await server.answer(again.msg_id, NEAREST)
            assert (await asyncio.wait_for(call, 5)).country == "IT"
            # The connection was never the problem, so it was not rebuilt.
            assert len(network.wires) == 1

    async def test_a_server_that_keeps_saying_no_gives_up(self):
        async with live(attempts=3) as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            server = server_for(invoker, network)
            for _ in range(3):
                request = await asyncio.wait_for(server.take(), 5)
                await server.refuse(request.msg_id, -503, "Timeout")
            with pytest.raises(Timeout):
                await asyncio.wait_for(call, 5)

    async def test_a_refusal_that_is_our_fault_is_not_retried(self):
        async with live() as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            server = server_for(invoker, network)
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 400, "PEER_ID_INVALID")
            with pytest.raises(BadRequest):
                await asyncio.wait_for(call, 5)

    async def test_it_stops_trying_eventually(self):
        network = Network()
        invoker = Invoker(
            seeded(),
            client=CLIENT,
            connector=network.connect,
            attempts=3,
            backoff=0.01,
            ping_interval=None,
        )
        await invoker.start()
        try:
            network.refuse = 99
            invoker.connection.session  # the first connection exists
            network.latest.break_it()
            with pytest.raises(TransportClosed):
                await asyncio.wait_for(invoker.invoke(a_call()), 5)
        finally:
            await invoker.close()

    async def test_a_connection_that_cannot_be_opened_at_all_says_so(self):
        network = Network()
        network.refuse = 1
        invoker = Invoker(seeded(), client=CLIENT, connector=network.connect)
        with pytest.raises(TransportClosed, match="nothing is listening"):
            await invoker.start()

    async def test_updates_survive_a_reconnect(self):
        async with live() as (invoker, network):
            first = server_for(invoker, network)
            await first.send(
                types.UpdateShort(update=types.UpdateDcOptions(dc_options=[]), date=1)
            )
            assert await asyncio.wait_for(invoker.updates.get(), 5)

            call = asyncio.create_task(invoker.invoke(a_call()))
            await asyncio.wait_for(first.take(), 5)
            first.wire.break_it()
            await _until(lambda: len(network.wires) == 2)

            second = server_for(invoker, network)
            request = await asyncio.wait_for(second.take(), 5)
            await second.send(
                types.UpdateShort(update=types.UpdateDcOptions(dc_options=[]), date=2)
            )
            await second.answer(request.msg_id, NEAREST)
            await asyncio.wait_for(call, 5)
            # The same queue, so nothing had to be re-subscribed to.
            assert (await asyncio.wait_for(invoker.updates.get(), 5)).date == 2

    async def test_the_new_connection_introduces_itself_again(self):
        # A new session on the server means initConnection has to be said again,
        # which is the connection's rule and has to survive being replaced.
        async with live() as (invoker, network):
            call = asyncio.create_task(invoker.invoke(a_call()))
            first = server_for(invoker, network)
            request = await asyncio.wait_for(first.take(), 5)
            assert isinstance(request.body, functions.InvokeWithLayer)
            first.wire.break_it()

            await _until(lambda: len(network.wires) == 2)
            second = server_for(invoker, network)
            again = await asyncio.wait_for(second.take(), 5)
            assert isinstance(again.body, functions.InvokeWithLayer)
            await second.answer(again.msg_id, NEAREST)
            await asyncio.wait_for(call, 5)


class TestLifecycle:
    async def test_saving_writes_the_session_down(self):
        storage = seeded()
        async with live(storage) as (invoker, _network):
            invoker.state.user_id = 777000
            invoker.state.is_bot = True
            await invoker.save()
        stored = await storage.load()
        assert stored.user_id == 777000
        assert stored.is_bot is True

    async def test_closing_puts_the_connection_down(self):
        network = Network()
        invoker = Invoker(
            seeded(), client=CLIENT, connector=network.connect, ping_interval=None
        )
        await invoker.start()
        await invoker.close()
        assert invoker.connection is None
        assert network.latest.closed
        with pytest.raises(SunnygramError, match="not been started"):
            await invoker.invoke(a_call())

    async def test_it_never_stringifies_the_key(self):
        async with live() as (invoker, _network):
            text = repr(invoker)
            assert AUTH_KEY[:8].hex() not in text
            assert "dc=2" in text


async def _until(condition, timeout: float = 5.0) -> None:
    """Wait for something the invoker does on its own, in its own time."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not condition():
        if loop.time() > deadline:
            raise AssertionError("the invoker never got there")
        await asyncio.sleep(0.01)


class TestAPeerTheServerWillNotAccept:
    """What happens to a cached access hash the server has stopped accepting.

    This is the failure the peer cache exists to make invisible and the one it
    can turn into a permanent fault: the hash lives in the session file, so a
    hash that has gone wrong is wrong again on the next run and on every run
    after it, and every call naming that peer fails the same way for ever. The
    remedy is to stop believing it, which is only true if it reaches the store
    as well as memory.
    """

    async def a_known_peer(self, invoker: Invoker) -> None:
        invoker.peers.learn(
            types.User(id=7, access_hash=1111, first_name="Someone", username="someone")
        )
        await invoker.peers.flush()

    async def test_the_hash_is_dropped_when_the_server_refuses_the_peer(self):
        storage = seeded()
        async with live(storage) as (invoker, network):
            await self.a_known_peer(invoker)
            assert await storage.peer_by_id(7) is not None

            server = server_for(invoker, network)
            named = types.InputPeerUser(user_id=7, access_hash=1111)
            call = asyncio.create_task(
                invoker.invoke(
                    functions.messages.SendMessage(
                        peer=named, message="hello", random_id=1
                    )
                )
            )
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 400, "PEER_ID_INVALID")

            with pytest.raises(BadRequest):
                await asyncio.wait_for(call, 5)

            # Both ends of it. Memory alone would come back wrong next run.
            assert await invoker.peers.get(7) is None
            assert await storage.peer_by_id(7) is None
            assert await storage.peer_by_username("someone") is None

    async def test_it_is_not_retried_and_the_caller_still_sees_why(self):
        # Dropping the peer is a repair for next time, not for this call: the
        # request in hand still names the peer the way the server refused, so
        # sending it again would only be refused again.
        storage = seeded()
        async with live(storage) as (invoker, network):
            await self.a_known_peer(invoker)
            server = server_for(invoker, network)
            call = asyncio.create_task(
                invoker.invoke(
                    functions.messages.SendMessage(
                        peer=types.InputPeerUser(user_id=7, access_hash=1111),
                        message="hello",
                        random_id=1,
                    )
                )
            )
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 400, "PEER_ID_INVALID")
            with pytest.raises(BadRequest, match="PEER_ID_INVALID"):
                await asyncio.wait_for(call, 5)

            # Nothing else went out. A second copy arriving here would mean the
            # call had been sent again with the hash the server just refused.
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(server.take(), 0.2)

    async def test_every_peer_the_call_named_goes(self):
        # A forward names two, and either of them could be the one the server
        # objected to, so both are suspect. Keeping the wrong one would leave
        # the fault in place while looking like it had been handled.
        storage = seeded()
        async with live(storage) as (invoker, network):
            invoker.peers.learn(
                types.User(id=7, access_hash=1111, first_name="Someone"),
                types.Channel(
                    id=99, access_hash=2222, title="Somewhere", photo=None, date=0
                ),
            )
            await invoker.peers.flush()

            server = server_for(invoker, network)
            call = asyncio.create_task(
                invoker.invoke(
                    functions.messages.ForwardMessages(
                        from_peer=types.InputPeerChannel(channel_id=99, access_hash=2222),
                        to_peer=types.InputPeerUser(user_id=7, access_hash=1111),
                        id=[1],
                        random_id=[1],
                    )
                )
            )
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 400, "CHANNEL_INVALID")
            with pytest.raises(BadRequest):
                await asyncio.wait_for(call, 5)

            assert await storage.peer_by_id(7) is None
            assert await storage.peer_by_id(99) is None

    async def test_an_unrelated_refusal_leaves_the_cache_alone(self):
        # The other half of the rule. A cache that dropped a peer whenever any
        # call failed would turn every ordinary refusal into an extra lookup,
        # and would eventually empty itself on a program that makes mistakes.
        storage = seeded()
        async with live(storage) as (invoker, network):
            await self.a_known_peer(invoker)
            server = server_for(invoker, network)
            call = asyncio.create_task(
                invoker.invoke(
                    functions.messages.SendMessage(
                        peer=types.InputPeerUser(user_id=7, access_hash=1111),
                        message="hello",
                        random_id=1,
                    )
                )
            )
            request = await asyncio.wait_for(server.take(), 5)
            await server.refuse(request.msg_id, 400, "MESSAGE_EMPTY")
            with pytest.raises(BadRequest):
                await asyncio.wait_for(call, 5)
            assert await storage.peer_by_id(7) is not None

    async def test_it_says_so_rather_than_dropping_quietly(self, caplog):
        # Rule C3. A cache that discards silently is indistinguishable from one
        # that never learned, and the extra call it causes has no explanation.
        storage = seeded()
        async with live(storage) as (invoker, network):
            await self.a_known_peer(invoker)
            server = server_for(invoker, network)
            with caplog.at_level("WARNING", logger="sunnygram.network.invoker"):
                call = asyncio.create_task(
                    invoker.invoke(
                        functions.messages.SendMessage(
                            peer=types.InputPeerUser(user_id=7, access_hash=1111),
                            message="hello",
                            random_id=1,
                        )
                    )
                )
                request = await asyncio.wait_for(server.take(), 5)
                await server.refuse(request.msg_id, 400, "PEER_ID_INVALID")
                with pytest.raises(BadRequest):
                    await asyncio.wait_for(call, 5)

        said = "\n".join(record.getMessage() for record in caplog.records)
        assert "PeerIdInvalid" in said
        assert "7" in said
