"""The update manager, fed by a datacenter that can lie about the order.

The interesting behaviour is not "an update arrives and is delivered". It is
what happens when one does not: a counter that skips, a container out of
sequence, a channel that moved on further than a difference can describe. So
most of what follows is the server withholding something and the manager
noticing.

Two things are asserted throughout. Nothing is delivered twice, and nothing is
delivered out of order, which together are the whole promise of this layer.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState, UpdateState
from sunnygram.updates import UpdateManager

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)


def message(id: int = 1, text: str = "hi", peer: Any = None) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=7) if peer is None else peer,
        date=1700000000,
        message=text,
    )


def new_message(pts: int, *, id: int = 1, text: str = "hi") -> types.UpdateNewMessage:
    return types.UpdateNewMessage(message=message(id, text), pts=pts, pts_count=1)


def _channel(id: int = 55, access_hash: int = 999) -> types.Channel:
    return types.Channel(
        id=id,
        access_hash=access_hash,
        title="A channel",
        photo=types.ChatPhotoEmpty(),
        date=0,
    )


def _channel_message(*, pts: int, id: int = 1, channel: int = 55) -> Any:
    return types.UpdateNewChannelMessage(
        message=message(id, "in the channel", types.PeerChannel(channel_id=channel)),
        pts=pts,
        pts_count=1,
    )


def container(*updates: Any, seq: int = 0, date: int = 1700000000, users=(), chats=()):
    return types.Updates(
        updates=list(updates),
        users=list(users),
        chats=list(chats),
        date=date,
        seq=seq,
    )


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


class UpdateServer(ScriptedServer):
    """A datacenter that answers the calls the update layer makes."""

    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.state = types.updates.State(
            pts=100, qts=0, date=1700000000, seq=10, unread_count=0
        )
        self.differences: list[Any] = []
        self.channel_differences: list[Any] = []
        self.asked: list[Any] = []
        self.refuse_differences = False
        self.ignore_differences = False
        # How to turn down a channel difference, as (code, name), or nothing to
        # answer it properly.
        self.refuse_channel_differences: tuple[int, str] | None = None

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            self.asked.append(query)
            if isinstance(query, functions.updates.GetState):
                await self.answer(request.msg_id, self.state)
            elif isinstance(query, functions.updates.GetDifference):
                if self.ignore_differences:
                    continue
                if self.refuse_differences:
                    await self.refuse(request.msg_id, 500, "INTERNAL")
                else:
                    await self.answer(request.msg_id, self._next_difference())
            elif isinstance(query, functions.updates.GetChannelDifference):
                if self.refuse_channel_differences is not None:
                    code, name = self.refuse_channel_differences
                    await self.refuse(request.msg_id, code, name)
                else:
                    await self.answer(request.msg_id, self._next_channel_difference())
            elif isinstance(query, functions.messages.SendMessage):
                await self.answer(request.msg_id, self.sent(query))
            else:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")

    def sent(self, query: Any) -> Any:
        """What sendMessage answers with, unless a test replaced it."""
        return container(
            types.UpdateMessageID(id=555, random_id=query.random_id),
            types.UpdateNewMessage(
                message=message(555, query.message), pts=101, pts_count=1
            ),
            seq=11,
        )

    def _next_difference(self) -> Any:
        if self.differences:
            return self.differences.pop(0)
        return types.updates.DifferenceEmpty(date=self.state.date, seq=self.state.seq)

    def _next_channel_difference(self) -> Any:
        if self.channel_differences:
            return self.channel_differences.pop(0)
        return types.updates.ChannelDifferenceEmpty(final=True, pts=1, timeout=None)

    @property
    def difference_calls(self) -> int:
        return sum(
            1
            for call in self.asked
            if isinstance(call, functions.updates.GetDifference)
        )


@asynccontextmanager
async def live(
    state: UpdateState | None = None,
    *,
    timeout: float = 5.0,
    updates_queue: int = 512,
    **options: Any,
) -> AsyncIterator[tuple[UpdateManager, UpdateServer, Invoker]]:
    """A started manager, the datacenter it talks to, and the invoker between."""
    session = SessionState(dc_id=2, user_id=777000)
    session.set_auth_key(2, AUTH_KEY)
    if state is not None:
        session.updates = state

    network = Network()
    invoker = Invoker(
        MemoryStorage(session),
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=timeout,
        updates_queue=updates_queue,
        # A refusal the invoker retries should not cost this suite its wall
        # clock: the retrying is its own tests' business, not these.
        backoff=0.01,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = UpdateServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    manager = UpdateManager(invoker, **options)
    try:
        yield manager, server, invoker
    finally:
        await manager.stop()
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()


async def drain(manager: UpdateManager, count: int, timeout: float = 5.0) -> list[Any]:
    """Wait for exactly this many events, and say so if they do not come."""
    events = []
    for _ in range(count):
        events.append(await asyncio.wait_for(manager.events.get(), timeout))
    return events


class TestStarting:
    async def test_a_session_that_knows_nothing_asks_where_the_stream_is(self):
        async with live() as (manager, server, invoker):
            await manager.start()
            assert manager.state.pts == 100
            assert manager.state.seq == 10
            assert isinstance(server.asked[0], functions.updates.GetState)

    async def test_where_it_got_to_is_written_down(self):
        async with live() as (manager, server, invoker):
            await manager.start()
            assert (await invoker._storage.load()).updates.pts == 100

    async def test_a_session_that_knows_asks_for_what_it_missed(self):
        async with live(UpdateState(pts=50, date=1, seq=2)) as (manager, server, _):
            await manager.start()
            assert isinstance(server.asked[0], functions.updates.GetDifference)
            assert server.asked[0].pts == 50

    async def test_catching_up_can_be_skipped(self):
        async with live(UpdateState(pts=50, date=1, seq=2)) as (manager, server, _):
            await manager.start(catch_up=False)
            assert server.asked == []
            assert manager.state.pts == 50

    async def test_starting_twice_is_refused(self):
        async with live() as (manager, server, _):
            await manager.start()
            with pytest.raises(SunnygramError, match="already running"):
                await manager.start()


class TestInOrder:
    async def test_an_update_in_sequence_is_delivered(self):
        async with live() as (manager, server, _):
            await manager.start()
            await server.send(container(new_message(101), seq=11))
            (event,) = await drain(manager, 1)
            assert event.update.message.message == "hi"
            assert manager.state.pts == 101

    async def test_the_same_update_twice_is_delivered_once(self):
        async with live() as (manager, server, _):
            await manager.start()
            await server.send(container(new_message(101), seq=11))
            await server.send(container(new_message(101), seq=11))
            await server.send(container(new_message(102), seq=12))
            events = await drain(manager, 2)
            assert [event.update.message.pts for event in []] == []
            assert [event.update.pts for event in events] == [101, 102]
            assert manager.events.empty()

    async def test_the_users_an_update_names_come_with_it(self):
        async with live() as (manager, server, _):
            await manager.start()
            ada = types.User(id=7, first_name="Ada")
            await server.send(container(new_message(101), seq=11, users=[ada]))
            (event,) = await drain(manager, 1)
            assert event.users[7].first_name == "Ada"

    async def test_an_update_with_nothing_to_order_is_delivered_as_it_is(self):
        async with live() as (manager, server, _):
            await manager.start()
            await server.send(
                types.UpdateShort(
                    update=types.UpdateUserTyping(
                        user_id=7, action=types.SendMessageTypingAction()
                    ),
                    date=1700000001,
                )
            )
            (event,) = await drain(manager, 1)
            assert isinstance(event.update, types.UpdateUserTyping)
            # It moved no counter, because it stands for nothing that repeats.
            assert manager.state.pts == 100

    async def test_a_short_message_is_understood(self):
        async with live() as (manager, server, _):
            await manager.start()
            await server.send(
                types.UpdateShortMessage(
                    id=9, user_id=7, message="hi", pts=101, pts_count=1, date=1
                )
            )
            (event,) = await drain(manager, 1)
            assert isinstance(event.update, types.UpdateShortMessage)
            assert manager.state.pts == 101


class TestGaps:
    async def test_a_missing_update_is_fetched_as_a_difference(self):
        async with live() as (manager, server, _):
            await manager.start()
            server.differences.append(
                types.updates.Difference(
                    new_messages=[message(2, "the one we missed")],
                    new_encrypted_messages=[],
                    other_updates=[],
                    chats=[],
                    users=[],
                    state=types.updates.State(
                        pts=105, qts=0, date=1700000002, seq=12, unread_count=0
                    ),
                )
            )
            # pts 105 with a count of one, from 100: four updates never arrived.
            await server.send(container(new_message(105), seq=11))
            (event,) = await drain(manager, 1)
            assert event.update.message.message == "the one we missed"
            assert manager.state.pts == 105
            assert server.difference_calls == 1

    async def test_a_difference_in_slices_is_followed_to_the_end(self):
        async with live() as (manager, server, _):
            await manager.start()
            server.differences.append(
                types.updates.DifferenceSlice(
                    new_messages=[message(2, "first half")],
                    new_encrypted_messages=[],
                    other_updates=[],
                    chats=[],
                    users=[],
                    intermediate_state=types.updates.State(
                        pts=103, qts=0, date=1, seq=11, unread_count=0
                    ),
                )
            )
            server.differences.append(
                types.updates.Difference(
                    new_messages=[message(3, "second half")],
                    new_encrypted_messages=[],
                    other_updates=[],
                    chats=[],
                    users=[],
                    state=types.updates.State(
                        pts=105, qts=0, date=1, seq=12, unread_count=0
                    ),
                )
            )
            await manager.catch_up()
            events = await drain(manager, 2)
            assert [event.update.message.message for event in events] == [
                "first half",
                "second half",
            ]
            assert manager.state.pts == 105
            assert server.difference_calls == 2

    async def test_a_container_out_of_sequence_is_a_gap(self):
        async with live() as (manager, server, _):
            await manager.start()
            # seq 20 where 11 was expected, so something never arrived.
            await server.send(container(new_message(101), seq=20))
            await asyncio.wait_for(_until(lambda: server.difference_calls == 1), 5)

    async def test_being_told_it_is_too_long_fetches_everything(self):
        async with live() as (manager, server, _):
            await manager.start()
            await server.send(types.UpdatesTooLong())
            await asyncio.wait_for(_until(lambda: server.difference_calls == 1), 5)

    async def test_too_far_behind_takes_the_counter_and_moves_on(self):
        async with live() as (manager, server, _):
            await manager.start()
            server.differences.append(types.updates.DifferenceTooLong(pts=9000))
            await manager.catch_up()
            assert manager.state.pts == 9000

    async def test_one_gap_does_not_start_a_second_fetch(self):
        # Applying a difference delivers updates, and one of those could look
        # like another gap. Asking twice for the same thing would loop.
        async with live() as (manager, server, _):
            await manager.start()
            server.differences.append(
                types.updates.Difference(
                    new_messages=[],
                    new_encrypted_messages=[],
                    other_updates=[new_message(9999)],
                    chats=[],
                    users=[],
                    state=types.updates.State(
                        pts=110, qts=0, date=1, seq=12, unread_count=0
                    ),
                )
            )
            await server.send(container(new_message(200), seq=11))
            await drain(manager, 1)
            assert server.difference_calls == 1


class TestContainerOrder:
    """Rule: a container is judged in the order its counters say, not wire order.

    Telegram routinely puts an update carrying pts_count=0 ahead of the one that
    actually advanced the counter, and both carry the same pts. Judged as they
    arrive, the first of the pair lands short of its own pts and is
    indistinguishable from a gap, so the manager would fetch a difference that
    has nothing to tell it.
    """

    async def test_a_read_receipt_ahead_of_its_message_is_not_a_gap(self):
        async with live() as (manager, server, _):
            await manager.start()
            receipt = types.UpdateReadHistoryInbox(
                peer=types.PeerUser(user_id=7),
                max_id=1,
                still_unread_count=0,
                pts=101,
                pts_count=0,
            )
            await server.send(container(receipt, new_message(101), seq=11))
            events = await drain(manager, 2)
            assert [type(event.update) for event in events] == [
                types.UpdateNewMessage,
                types.UpdateReadHistoryInbox,
            ]
            assert manager.state.pts == 101
            assert server.difference_calls == 0

    async def test_two_streams_in_one_container_do_not_reorder_each_other(self):
        state = UpdateState(pts=100, date=1700000000, seq=10, channels={55: 4})
        async with live(state) as (manager, server, _):
            await manager.start(catch_up=False)
            # The channel is far behind the common stream in raw pts, so sorting
            # the container as a whole would drag it to the front.
            await server.send(
                container(new_message(101), _channel_message(pts=5), seq=11)
            )
            events = await drain(manager, 2)
            assert [type(event.update) for event in events] == [
                types.UpdateNewMessage,
                types.UpdateNewChannelMessage,
            ]
            assert server.difference_calls == 0


class TestGoingQuiet:
    async def test_a_stream_that_stops_is_caught_up_on_anyway(self):
        async with live(idle_catch_up=0.05) as (manager, server, _):
            await manager.start()
            assert server.difference_calls == 0
            # Nothing is sent at all. The socket is fine and the counters have
            # nothing to notice, which is exactly the fault this covers.
            await asyncio.wait_for(_until(lambda: server.difference_calls > 0), 5)
            assert manager.resyncs >= 1

    async def test_an_update_arriving_puts_the_silence_back_to_zero(self):
        async with live(idle_catch_up=0.4) as (manager, server, _):
            await manager.start()
            for pts in range(101, 106):
                await server.send(container(new_message(pts), seq=0))
                await asyncio.sleep(0.1)
            await drain(manager, 5)
            # Half a second of traffic, none of it more than a tenth of a second
            # apart, so the watchdog should never have fired.
            assert server.difference_calls == 0

    async def test_it_can_be_turned_off(self):
        async with live(idle_catch_up=0) as (manager, server, _):
            await manager.start()
            await asyncio.sleep(0.15)
            assert server.difference_calls == 0


class TestTheOtherCounter:
    """qts, and the sixteen kinds of update that moved it with nothing looking.

    Everything in this file is about pts, which is the counter messages move,
    because that was the counter anything was listening to. The one that covers
    a member joining, a join request arriving, a vote being cast and a reaction
    being added is qts, and it was being read for secret chats only.

    The fault that made is the quiet kind. Nothing was lost and nothing arrived
    out of order, so nothing looked wrong: the mark simply stayed where it was
    while the server's moved, and every resync therefore asked the server to
    say again everything since a point the account had long gone past. The
    server obliged. A moderation handler would have banned twice.
    """

    def _member_change(self, qts: int) -> Any:
        return types.UpdateChannelParticipant(
            channel_id=55, date=1700000000, actor_id=1, user_id=7, qts=qts
        )

    async def test_a_member_change_moves_the_qts(self):
        async with live(UpdateState(pts=100, qts=5, date=1, seq=10)) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            await server.send(container(self._member_change(qts=6), seq=11))
            (event,) = await drain(manager, 1)
            assert isinstance(event.update, types.UpdateChannelParticipant)
            assert manager.state.qts == 6

    async def test_the_next_difference_asks_from_where_the_qts_got_to(self):
        # The assertion the bug was really about. Delivering the update was
        # never the problem; asking for it again afterwards was.
        async with live(UpdateState(pts=100, qts=5, date=1, seq=10)) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            await server.send(container(self._member_change(qts=6), seq=11))
            await drain(manager, 1)

            await server.send(types.UpdatesTooLong())
            await asyncio.wait_for(_until(lambda: server.difference_calls == 1), 5)
            asked = next(
                call
                for call in server.asked
                if isinstance(call, functions.updates.GetDifference)
            )
            assert asked.qts == 6

    async def test_a_qts_update_already_seen_is_not_delivered_again(self):
        async with live(UpdateState(pts=100, qts=5, date=1, seq=10)) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            await server.send(container(self._member_change(qts=6), seq=11))
            await server.send(container(self._member_change(qts=6), seq=12))
            await server.send(container(self._member_change(qts=7), seq=13))
            events = await drain(manager, 2)
            assert [event.update.qts for event in events] == [6, 7]
            assert manager.events.empty()

    async def test_a_missing_qts_update_is_a_gap_like_any_other(self):
        async with live(UpdateState(pts=100, qts=5, date=1, seq=10)) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            # 6 never arrived, so 7 is past a gap and has to be asked about.
            await server.send(container(self._member_change(qts=7), seq=11))
            await asyncio.wait_for(_until(lambda: server.difference_calls == 1), 5)


class TestChannels:
    async def test_a_channel_counts_on_its_own(self):
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            await server.send(
                container(
                    types.UpdateNewChannelMessage(
                        message=message(1, "in a channel", types.PeerChannel(channel_id=55)),
                        pts=5,
                        pts_count=1,
                    ),
                    seq=11,
                )
            )
            (event,) = await drain(manager, 1)
            assert event.update.message.message == "in a channel"
            assert manager.state.channels[55] == 5
            assert manager.state.pts == 100

    async def test_a_gap_in_a_channel_asks_about_that_channel(self):
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            channel = types.Channel(
                id=55,
                access_hash=999,
                title="A channel",
                photo=types.ChatPhotoEmpty(),
                date=0,
            )
            server.channel_differences.append(
                types.updates.ChannelDifference(
                    final=True,
                    pts=40,
                    timeout=None,
                    new_messages=[message(3, "missed in the channel")],
                    other_updates=[],
                    chats=[],
                    users=[],
                )
            )
            # The chat comes with the container, which is where the access hash
            # to ask about it with comes from.
            await server.send(
                container(
                    types.UpdateNewChannelMessage(
                        message=message(1, "later", types.PeerChannel(channel_id=55)),
                        pts=40,
                        pts_count=1,
                    ),
                    seq=11,
                    chats=[channel],
                )
            )
            (event,) = await drain(manager, 1)
            assert event.update.message.message == "missed in the channel"
            assert manager.state.channels[55] == 40
            asked = [
                call
                for call in server.asked
                if isinstance(call, functions.updates.GetChannelDifference)
            ]
            assert asked and asked[0].channel.access_hash == 999

    async def test_a_channel_we_cannot_name_is_forgotten_rather_than_stuck(self):
        # Without an access hash there is nothing to ask with, and keeping the
        # counter would read every later update from it as the same gap.
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            await server.send(
                container(
                    types.UpdateNewChannelMessage(
                        message=message(1, "far ahead", types.PeerChannel(channel_id=55)),
                        pts=40,
                        pts_count=1,
                    ),
                    seq=11,
                )
            )
            await asyncio.wait_for(_until(lambda: 55 not in manager.state.channels), 5)

    async def test_a_wait_does_not_cost_a_channel_its_place(self):
        # FLOOD_WAIT on a difference is a moment, not a verdict. Forgetting the
        # counter over one means the channel silently stops being followed, and
        # the account has done nothing wrong to deserve it.
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            server.refuse_channel_differences = (420, "FLOOD_WAIT_600")
            await server.send(
                container(
                    _channel_message(pts=40),
                    seq=11,
                    chats=[_channel()],
                )
            )
            await asyncio.wait_for(_until(lambda: manager.failures == 1), 5)
            assert manager.state.channels[55] == 4
            assert manager.running

    async def test_a_channel_that_refuses_us_is_forgotten(self):
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            server.refuse_channel_differences = (400, "CHANNEL_PRIVATE")
            await server.send(
                container(
                    _channel_message(pts=40),
                    seq=11,
                    chats=[_channel()],
                )
            )
            await asyncio.wait_for(_until(lambda: 55 not in manager.state.channels), 5)
            assert manager.failures == 0

    async def test_a_channel_told_it_is_too_long_takes_the_dialog_pts(self):
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            channel = types.Channel(
                id=55,
                access_hash=999,
                title="A channel",
                photo=types.ChatPhotoEmpty(),
                date=0,
            )
            server.channel_differences.append(
                types.updates.ChannelDifferenceTooLong(
                    final=True,
                    timeout=None,
                    dialog=types.Dialog(
                        peer=types.PeerChannel(channel_id=55),
                        top_message=9,
                        read_inbox_max_id=0,
                        read_outbox_max_id=0,
                        unread_count=0,
                        unread_mentions_count=0,
                        unread_reactions_count=0,
                        unread_poll_votes_count=0,
                        notify_settings=types.PeerNotifySettings(),
                        pts=777,
                    ),
                    messages=[],
                    chats=[channel],
                    users=[],
                )
            )
            # The pts the update carries is deliberately not the one we hold:
            # a test where the two agree cannot tell the two apart, and telling
            # them apart is the whole point of the ones below.
            await server.send(
                container(
                    types.UpdateChannelTooLong(channel_id=55, pts=900),
                    seq=11,
                    chats=[channel],
                )
            )
            await asyncio.wait_for(
                _until(lambda: manager.state.channels.get(55) == 777), 5
            )

    async def test_a_channel_told_it_is_too_long_asks_from_our_own_mark(self):
        # The pts on updateChannelTooLong is the channel's latest on the server,
        # which is where the gap ends. Asking from it means asking what changed
        # since the newest thing there is, and the empty answer to that is
        # indistinguishable from having caught up, so the gap is not closed but
        # erased. The cursor has to be our own mark.
        async with live(UpdateState(pts=100, date=1, seq=10, channels={55: 4})) as (
            manager,
            server,
            _,
        ):
            await manager.start(catch_up=False)
            server.channel_differences.append(
                types.updates.ChannelDifferenceEmpty(final=True, pts=900, timeout=None)
            )
            await server.send(
                container(
                    types.UpdateChannelTooLong(channel_id=55, pts=900),
                    seq=11,
                    chats=[_channel()],
                )
            )
            await asyncio.wait_for(
                _until(
                    lambda: any(
                        isinstance(q, functions.updates.GetChannelDifference)
                        for q in server.asked
                    )
                ),
                5,
            )
            asked = [
                q
                for q in server.asked
                if isinstance(q, functions.updates.GetChannelDifference)
            ]
            assert asked[0].pts == 4, (
                f"asked from {asked[0].pts}, which is the server's own mark, so "
                "everything between 4 and 900 is skipped rather than fetched"
            )

    async def test_a_channel_never_followed_adopts_the_mark_it_is_given(self):
        # Nothing stored for this channel, so there is no gap to read: the
        # server's own mark becomes ours and no difference is asked for at all.
        async with live(UpdateState(pts=100, date=1, seq=10)) as (manager, server, _):
            await manager.start(catch_up=False)
            await server.send(
                container(
                    types.UpdateChannelTooLong(channel_id=55, pts=900),
                    seq=11,
                    chats=[_channel()],
                )
            )
            await asyncio.wait_for(
                _until(lambda: manager.state.channels.get(55) == 900), 5
            )
            assert not [
                q
                for q in server.asked
                if isinstance(q, functions.updates.GetChannelDifference)
            ]


class TestDelivery:
    async def test_events_are_dropped_rather_than_blocking_the_session(self):
        async with live(events_queue=1) as (manager, server, _):
            await manager.start()
            for pts in range(101, 105):
                await server.send(container(new_message(pts), seq=0))
            await asyncio.wait_for(_until(lambda: manager.dropped_events == 3), 5)
            assert manager.state.pts == 104

    async def test_a_refused_difference_leaves_the_stream_running(self):
        async with live() as (manager, server, _):
            await manager.start()
            # The gap stays standing, and the next update to notice it asks
            # again, rather than the stream ending here for good. The refusal is
            # a 500, which the invoker underneath asks again about a few times
            # before giving up, so the count is read rather than predicted.
            server.refuse_differences = True
            await server.send(container(new_message(500), seq=11))
            await asyncio.wait_for(_until(lambda: manager.failures == 1), 5)
            assert manager.running
            gave_up_after = server.difference_calls

            server.refuse_differences = False
            await server.send(container(new_message(501), seq=12))
            await asyncio.wait_for(
                _until(lambda: server.difference_calls > gave_up_after), 5
            )

    async def test_a_difference_that_never_comes_back_leaves_it_running(self):
        # A timeout is not an RPC error and not a transport error, so it is the
        # one that quietly ended the stream before this test existed.
        async with live(timeout=0.1) as (manager, server, _):
            await manager.start()
            server.ignore_differences = True
            await server.send(container(new_message(500), seq=11))
            await asyncio.wait_for(_until(lambda: manager.failures == 1), 5)
            assert manager.running


class TestRecovering:
    """The two ways updates go missing without any counter noticing."""

    async def test_a_session_the_server_started_asks_what_was_missed(self):
        # A rebuilt connection gets a new session, and updates are counted per
        # session, so everything that arrived while the socket was down went to
        # a session that no longer exists. Without this the stream looks healthy
        # and is quietly missing whatever happened during the outage.
        async with live(UpdateState(pts=50, date=1, seq=2)) as (
            manager,
            server,
            invoker,
        ):
            await manager.start(catch_up=False)
            assert server.difference_calls == 0

            await invoker.updates.put(
                types.mtproto.NewSessionCreated(
                    first_msg_id=1, unique_id=2, server_salt=3
                )
            )
            await asyncio.wait_for(_until(lambda: server.difference_calls == 1), 5)
            assert manager.resyncs == 1

    async def test_updates_thrown_away_are_asked_for_again(self):
        async with live(UpdateState(pts=50, date=1, seq=2), updates_queue=1) as (
            manager,
            server,
            invoker,
        ):
            await manager.start(catch_up=False)
            # Holding the lock stops the drain, so the queue between it and the
            # connection fills and the connection starts dropping, which is the
            # situation a program too slow to keep up creates for itself.
            async with manager._lock:
                for pts in range(51, 60):
                    await server.send(container(new_message(pts), seq=0))
                await asyncio.wait_for(_until(lambda: invoker.dropped_updates > 0), 5)

            await asyncio.wait_for(_until(lambda: manager.resyncs == 1), 5)
            assert server.difference_calls >= 1

    async def test_what_was_dropped_before_anyone_listened_is_not_a_loss(self):
        async with live(UpdateState(pts=50, date=1, seq=2), updates_queue=1) as (
            manager,
            server,
            invoker,
        ):
            for pts in range(51, 60):
                await server.send(container(new_message(pts), seq=0))
            await asyncio.wait_for(_until(lambda: invoker.dropped_updates > 0), 5)

            # Nothing had been applied yet, so there is no hole to fill: the
            # manager starts level with whatever the connection threw away.
            await manager.start(catch_up=False)
            await asyncio.sleep(0.1)
            assert manager.resyncs == 0


async def _until(condition, timeout: float = 5.0) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not condition():
        if loop.time() > deadline:
            raise AssertionError("it never got there")
        await asyncio.sleep(0.01)
