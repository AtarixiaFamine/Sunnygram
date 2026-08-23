"""The connection loop, driven by a datacenter that answers back.

The server here shares the auth key and packs with the direction flipped, which
is what a real one does with the other half of the key. So every test below goes
through the whole encrypted path: the envelope, the session checks, containers,
gzip, and the routing that gets an answer back to the caller who asked for it.

Nothing opens a socket. The transport is a pair of queues, which is the only
reason a test can hold a connection at a chosen moment and decide what happens
next.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import (
    AUTH_KEY,
    NEAREST,
    NEW_SALT,
    SALT,
    ScriptedServer,
    Wire,
    a_call,
    rpc_result,
)
from sunnygram.errors import (
    BadMessage,
    BadRequest,
    FloodWait,
    TransportClosed,
    TransportError,
)
from sunnygram.network import ClientInfo, Connection
from sunnygram.network.connection import MAX_RESENDS
from sunnygram.raw import LAYER, functions, types
from sunnygram.session import Session, signed_long


async def fence(connection: Connection, server: ScriptedServer) -> None:
    """One full round trip, proving everything sent before it was handled.

    Frames are read in order, so a call that has its answer is also a promise
    that whatever the server pushed earlier has already been through the reader.
    """
    call = asyncio.create_task(connection.invoke(a_call()))
    request = await asyncio.wait_for(server.take(), 5)
    await server.answer(request.msg_id, NEAREST)
    await asyncio.wait_for(call, 5)


@asynccontextmanager
async def live(**options: Any) -> AsyncIterator[tuple[Connection, ScriptedServer]]:
    """A started connection and the server on the other end of it."""
    wire = Wire()
    session = Session(AUTH_KEY, salt=SALT)
    server = ScriptedServer(wire, session)
    options.setdefault("ping_interval", None)
    connection = Connection(wire, session, dc_id=2, **options)
    await connection.start()
    try:
        yield connection, server
    finally:
        await connection.close()


class TestRouting:
    async def test_an_answer_reaches_the_caller(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            assert isinstance(request.query, functions.help.GetNearestDc)
            await server.answer(request.msg_id, NEAREST)
            assert (await call).country == "IT"

    async def test_answers_out_of_order_still_find_their_callers(self):
        async with live() as (connection, server):
            first = asyncio.create_task(connection.invoke(functions.help.GetConfig()))
            second = asyncio.create_task(connection.invoke(a_call()))
            one, two = await server.take(), await server.take()
            assert isinstance(one.query, functions.help.GetConfig)
            # Answered the other way round, so only req_msg_id can be sorting it.
            await server.answer(two.msg_id, NEAREST)
            await server.answer(one.msg_id, types.NearestDc(
                country="FR", this_dc=4, nearest_dc=4
            ))
            assert (await second).country == "IT"
            assert (await first).country == "FR"

    async def test_a_container_of_answers_is_unwrapped(self):
        async with live() as (connection, server):
            first = asyncio.create_task(connection.invoke(a_call()))
            second = asyncio.create_task(connection.invoke(a_call()))
            one, two = await server.take(), await server.take()
            await server.container(
                rpc_result(one.msg_id, NEAREST),
                rpc_result(two.msg_id, types.NearestDc(
                    country="DE", this_dc=2, nearest_dc=2
                )),
            )
            assert (await first).country == "IT"
            assert (await second).country == "DE"

    async def test_a_gzipped_answer_is_expanded(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.answer(request.msg_id, NEAREST, packed=True)
            assert (await call).country == "IT"

    async def test_a_pong_reaches_the_caller_that_pinged(self):
        # A pong is not an rpc_result: it names the ping's own message id.
        async with live() as (connection, server):
            call = asyncio.create_task(
                connection.invoke(functions.mtproto.Ping(ping_id=7))
            )
            request = await server.take()
            assert request.seq_no % 2 == 0, "a ping is not content-related"
            await server.send(types.mtproto.Pong(msg_id=request.msg_id, ping_id=7))
            assert (await call).ping_id == 7

    async def test_future_salts_reach_the_caller(self):
        async with live() as (connection, server):
            call = asyncio.create_task(
                connection.invoke(functions.mtproto.GetFutureSalts(num=1))
            )
            request = await server.take()
            await server.send(
                types.mtproto.FutureSalts(
                    req_msg_id=request.msg_id,
                    now=0,
                    salts=[
                        types.mtproto.FutureSalt(
                            valid_since=0, valid_until=1, salt=NEW_SALT
                        )
                    ],
                )
            )
            assert (await call).salts[0].salt == NEW_SALT

    async def test_an_answer_nobody_waits_for_is_dropped(self):
        async with live() as (connection, server):
            await server.answer(12345, NEAREST)
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.answer(request.msg_id, NEAREST)
            assert await call
            assert connection.running


class TestErrors:
    async def test_a_refusal_arrives_as_a_typed_error(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.refuse(request.msg_id, 400, "CHAT_ID_INVALID")
            with pytest.raises(BadRequest) as info:
                await call
            assert info.value.code == 400
            # The error says which call it came from, which the server never said.
            assert "GetNearestDc" in str(info.value)

    async def test_a_long_flood_wait_is_the_callers_problem(self):
        async with live(flood_threshold=1.0) as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.refuse(request.msg_id, 420, "FLOOD_WAIT_300")
            with pytest.raises(FloodWait) as info:
                await call
            assert info.value.seconds == 300

    async def test_a_short_flood_wait_is_waited_out(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            await server.refuse(first.msg_id, 420, "FLOOD_WAIT_1")
            # The same call comes round again, under a new id.
            second = await asyncio.wait_for(server.take(), 5)
            assert second.msg_id != first.msg_id
            await server.answer(second.msg_id, NEAREST)
            assert (await call).country == "IT"

    async def test_a_call_that_is_never_answered_gives_up(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call(), timeout=0.05))
            await server.take()
            with pytest.raises(TimeoutError):
                await call
            # And it stops waiting rather than holding a slot for ever.
            assert connection.running
            await fence(connection, server)


class TestRecovery:
    async def test_a_stale_salt_is_replaced_and_the_call_resent(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            await server.send(
                types.mtproto.BadServerSalt(
                    bad_msg_id=first.msg_id,
                    bad_msg_seqno=first.seq_no,
                    error_code=48,
                    new_server_salt=NEW_SALT,
                ),
                seq_no=0,
            )
            second = await asyncio.wait_for(server.take(), 5)
            assert second.msg_id != first.msg_id
            assert connection.session.salt == signed_long(NEW_SALT)
            await server.answer(second.msg_id, NEAREST)
            assert (await call).country == "IT"

    async def test_a_clock_complaint_moves_our_clock_and_resends(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            # Dated inside the session's own time window, since a wider gap is
            # not something the connection is allowed to believe.
            await server.push(
                types.mtproto.BadMsgNotification(
                    bad_msg_id=first.msg_id,
                    bad_msg_seqno=first.seq_no,
                    error_code=16,
                ).to_bytes(),
                seq_no=0,
                msg_id=(int(time.time() + 20) << 32) | 1,
            )
            second = await asyncio.wait_for(server.take(), 5)
            assert 15 < connection.session.time_offset < 25
            await server.answer(second.msg_id, NEAREST)
            assert await call

    async def test_a_sequence_complaint_costs_the_session(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            before = connection.session.session_id
            await server.send(
                types.mtproto.BadMsgNotification(
                    bad_msg_id=first.msg_id,
                    bad_msg_seqno=first.seq_no,
                    error_code=33,
                ),
                seq_no=0,
            )
            second = await asyncio.wait_for(server.take(), 5)
            assert connection.session.session_id != before
            assert second.seq_no == 1, "the new session counts from the start"
            await server.answer(second.msg_id, NEAREST)
            assert await call

    async def test_a_complaint_with_no_remedy_reaches_the_caller(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.send(
                types.mtproto.BadMsgNotification(
                    bad_msg_id=request.msg_id,
                    bad_msg_seqno=request.seq_no,
                    error_code=18,
                ),
                seq_no=0,
            )
            with pytest.raises(BadMessage) as info:
                await call
            assert info.value.code == 18
            assert "divisible by four" in str(info.value)

    async def test_a_correction_that_never_settles_is_given_up_on(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            # A server that answers every correction with the same complaint. The
            # call is resent its allowance of times and then stops.
            for _ in range(MAX_RESENDS + 1):
                request = await asyncio.wait_for(server.take(), 5)
                await server.send(
                    types.mtproto.BadServerSalt(
                        bad_msg_id=request.msg_id,
                        bad_msg_seqno=request.seq_no,
                        error_code=48,
                        new_server_salt=NEW_SALT,
                    ),
                    seq_no=0,
                )
            with pytest.raises(TransportError, match="without the server accepting"):
                await asyncio.wait_for(call, 5)


class TestSessionMessages:
    async def test_a_new_session_is_adopted_and_reported(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            await server.send(
                types.mtproto.NewSessionCreated(
                    first_msg_id=request.msg_id, unique_id=1, server_salt=NEW_SALT
                )
            )
            reported = await asyncio.wait_for(connection.updates.get(), 5)
            assert isinstance(reported, types.mtproto.NewSessionCreated)
            assert connection.session.salt == signed_long(NEW_SALT)
            # Nothing was resent: a message that may already have run must not
            # run twice, so the call waits for its own answer.
            await server.answer(request.msg_id, NEAREST)
            assert await call

    async def test_an_update_lands_on_the_queue(self):
        async with live() as (connection, server):
            update = types.UpdateShort(
                update=types.UpdateDcOptions(dc_options=[]), date=1
            )
            await server.send(update)
            assert await asyncio.wait_for(connection.updates.get(), 5) == update

    async def test_the_queue_drops_the_newest_when_nobody_drains_it(self):
        async with live(updates_queue=1) as (connection, server):
            for index in range(3):
                await server.send(
                    types.UpdateShort(
                        update=types.UpdateDcOptions(dc_options=[]), date=index
                    )
                )
            await fence(connection, server)
            assert connection.updates.qsize() == 1
            assert connection.dropped_updates == 2

    async def test_something_we_cannot_read_does_not_end_the_connection(self):
        async with live() as (connection, server):
            # A constructor from a layer newer than the one we generated from.
            await server.push((0xDEADBEEF).to_bytes(4, "little"))
            await fence(connection, server)
            assert connection.unknown_constructors == 1
            assert connection.running


class TestAcknowledgements:
    async def test_content_from_the_server_is_acknowledged(self):
        async with live() as (connection, server):
            update = types.UpdateShort(
                update=types.UpdateDcOptions(dc_options=[]), date=1
            )
            msg_id = await server.send(update, seq_no=1)
            assert msg_id in await asyncio.wait_for(server.take_ack(), 5)

    async def test_housekeeping_is_not_acknowledged(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            salt_msg = await server.push(
                types.mtproto.BadServerSalt(
                    bad_msg_id=request.msg_id,
                    bad_msg_seqno=request.seq_no,
                    error_code=48,
                    new_server_salt=NEW_SALT,
                ).to_bytes(),
                seq_no=0,
            )
            resent = await asyncio.wait_for(server.take(), 5)
            answer = await server.answer(resent.msg_id, NEAREST)
            await call
            batch = await asyncio.wait_for(server.take_ack(), 5)
            assert answer in batch
            assert salt_msg not in batch

    async def test_acknowledgements_travel_together(self):
        async with live() as (connection, server):
            sent = [
                await server.send(
                    types.UpdateShort(
                        update=types.UpdateDcOptions(dc_options=[]), date=index
                    )
                )
                for index in range(4)
            ]
            batch = await asyncio.wait_for(server.take_ack(), 5)
            assert sorted(batch) == sorted(sent)


class TestIntroduction:
    async def test_the_first_call_says_who_is_calling(self):
        async with live(client=ClientInfo(api_id=12345, app_version="7.7")) as (
            connection,
            server,
        ):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            assert isinstance(first.body, functions.InvokeWithLayer)
            assert first.body.layer == LAYER
            init = first.body.query
            assert isinstance(init, functions.InitConnection)
            assert (init.api_id, init.app_version) == (12345, "7.7")
            assert isinstance(first.query, functions.help.GetNearestDc)
            await server.answer(first.msg_id, NEAREST)
            await call

            # And only the first: the server remembers for the rest of the session.
            second = asyncio.create_task(connection.invoke(a_call()))
            request = await server.take()
            assert isinstance(request.body, functions.help.GetNearestDc)
            await server.answer(request.msg_id, NEAREST)
            await second

    async def test_a_new_session_is_introduced_again(self):
        async with live(client=ClientInfo(api_id=12345)) as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await server.take()
            assert isinstance(first.body, functions.InvokeWithLayer)
            await server.send(
                types.mtproto.BadMsgNotification(
                    bad_msg_id=first.msg_id, bad_msg_seqno=first.seq_no, error_code=33
                ),
                seq_no=0,
            )
            # The session it introduced itself to is gone, so it says it again.
            resent = await asyncio.wait_for(server.take(), 5)
            assert isinstance(resent.body, functions.InvokeWithLayer)
            await server.answer(resent.msg_id, NEAREST)
            assert await call


class TestLifecycle:
    async def test_a_dropped_connection_ends_the_calls_waiting_on_it(self):
        async with live() as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            await server.take()
            server.wire.break_it()
            with pytest.raises(TransportClosed):
                await asyncio.wait_for(call, 5)
            assert not connection.running

    async def test_a_call_after_the_connection_broke_says_why(self):
        async with live() as (connection, server):
            server.wire.break_it()
            for _ in range(50):
                if not connection.running:
                    break
                await asyncio.sleep(0.01)
            with pytest.raises(TransportClosed, match="mid-packet"):
                await connection.invoke(a_call())

    async def test_closing_is_safe_to_repeat(self):
        async with live() as (connection, _server):
            await connection.close()
            await connection.close()
            assert not connection.running
            with pytest.raises(TransportClosed):
                await connection.invoke(a_call())

    async def test_starting_twice_is_refused(self):
        async with live() as (connection, _server):
            with pytest.raises(TransportError, match="already running"):
                await connection.start()

    async def test_only_so_many_calls_are_in_flight_at_once(self):
        async with live(max_in_flight=1) as (connection, server):
            first = asyncio.create_task(connection.invoke(a_call()))
            second = asyncio.create_task(connection.invoke(a_call()))
            waiting = await server.take()
            # The second call is holding at the cap, so nothing else went out.
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(server.take(), 0.1)
            await server.answer(waiting.msg_id, NEAREST)
            assert await first
            # The slot came free, so the second call went out after all.
            released = await asyncio.wait_for(server.take(), 5)
            await server.answer(released.msg_id, NEAREST)
            assert await second

    async def test_being_told_it_was_never_introduced_introduces_itself_again(self):
        # Telegram moves a session between its own machines and the new one has
        # never heard of us. The introduction goes out once and then stops, so
        # nothing above this layer could fix it: every later call would be
        # refused for the same reason and the session would be finished.
        async with live(client=ClientInfo(api_id=12345)) as (connection, server):
            call = asyncio.create_task(connection.invoke(a_call()))
            first = await asyncio.wait_for(server.take(), 5)
            assert isinstance(first.body, functions.InvokeWithLayer)
            await server.refuse(first.msg_id, 400, "CONNECTION_NOT_INITED")

            again = await asyncio.wait_for(server.take(), 5)
            assert isinstance(again.body, functions.InvokeWithLayer)
            assert again.query == a_call()
            await server.answer(again.msg_id, NEAREST)
            assert (await asyncio.wait_for(call, 5)).country == "IT"

    async def test_a_connection_never_stringifies_the_key(self):
        async with live() as (connection, _server):
            text = repr(connection)
            assert AUTH_KEY[:8].hex() not in text
            assert "dc=2" in text and "running" in text

    async def test_the_keepalive_ping_goes_out(self):
        async with live(ping_interval=0.01) as (connection, server):
            request = await asyncio.wait_for(server.take(), 5)
            assert isinstance(request.body, functions.mtproto.PingDelayDisconnect)
            assert request.body.disconnect_delay > 0
            await server.send(
                types.mtproto.Pong(msg_id=request.msg_id, ping_id=request.body.ping_id)
            )
            assert connection.running

    async def test_a_ping_that_is_never_answered_ends_the_connection(self):
        # The half-open socket: everything we write is accepted by the operating
        # system and nothing will ever come back. No read fails, no write fails,
        # and before this the program simply went quiet for good.
        async with live(ping_interval=0.01, pong_timeout=0.2) as (connection, server):
            # A call already in flight when the connection dies is told, rather
            # than waiting out its own timeout for an answer nobody will send.
            waiting = asyncio.create_task(connection.invoke(a_call()))
            with pytest.raises(TransportClosed, match="did not answer a ping"):
                await asyncio.wait_for(waiting, 5)
            assert not connection.running

    async def test_a_dead_connection_refuses_new_calls_at_once(self):
        async with live(ping_interval=0.01, pong_timeout=0.2) as (connection, server):
            await asyncio.wait_for(server.take(), 5)
            await _until(lambda: not connection.running)
            with pytest.raises(TransportClosed, match="not running"):
                await connection.invoke(a_call())

    async def test_the_ping_still_goes_out_on_a_saturated_connection(self):
        # The in-flight cap bounds a program's own work. A ping is not that: it
        # is what notices the connection has died, and queueing it behind the
        # content would switch the detector off exactly when a full connection
        # makes an unnoticed stall most expensive. The call below is never
        # answered, so the only slot stays taken for the whole test.
        async with live(max_in_flight=1, ping_interval=0.01) as (connection, server):
            stuck = asyncio.create_task(connection.invoke(a_call()))
            first = await asyncio.wait_for(server.take(), 5)
            assert not isinstance(first.body, functions.mtproto.PingDelayDisconnect)

            request = await asyncio.wait_for(server.take(), 5)
            assert isinstance(request.body, functions.mtproto.PingDelayDisconnect), (
                "the keepalive queued behind a call holding the only in-flight "
                "slot, so a connection that died here would never be noticed"
            )
            await server.send(
                types.mtproto.Pong(msg_id=request.msg_id, ping_id=request.body.ping_id)
            )
            assert connection.running
            stuck.cancel()

    async def test_an_answered_ping_keeps_the_connection(self):
        async with live(ping_interval=0.05, pong_timeout=0.5) as (connection, server):
            for _ in range(3):
                request = await asyncio.wait_for(server.take(), 5)
                await server.send(
                    types.mtproto.Pong(
                        msg_id=request.msg_id, ping_id=request.body.ping_id
                    )
                )
            assert connection.running


async def _until(condition, timeout: float = 5.0) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not condition():
        if loop.time() > deadline:
            raise AssertionError("it never got there")
        await asyncio.sleep(0.01)
