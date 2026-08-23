"""Messages queued for later.

Scheduling is one optional field on the calls that already exist, so most of
what is worth testing is the shape around it: that a datetime becomes the
timestamp Telegram wants, that WHEN_ONLINE survives the conversion instead of
being read as a date in 2038, and that the message comes back at all. That last
one is the part that would have broken quietly: a scheduled send is answered
with a different update from an ordinary one, so the code that finds our
message among the updates has to know about both.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator

from mtproto_server import AUTH_KEY, RecordingServer, Wire
from sunnygram.methods import (
    WHEN_ONLINE,
    delete_scheduled_messages,
    get_scheduled_messages,
    schedule_at,
    scheduled_history,
    send_scheduled_messages,
    send_message,
)
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000


def a_message(id: int, text: str = "later") -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=ME),
        date=1700000000,
        message=text,
        out=True,
    )


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


@asynccontextmanager
async def live() -> AsyncIterator[tuple[Invoker, RecordingServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    invoker = Invoker(
        MemoryStorage(session),
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
        rate_limit=False,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = RecordingServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve_all())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()


class TestSayingWhen:
    """schedule_at, which is the whole of the conversion."""

    def test_nothing_stays_nothing(self):
        assert schedule_at(None) is None

    def test_a_timestamp_passes_through(self):
        assert schedule_at(1893456000) == 1893456000

    def test_an_aware_datetime_becomes_its_timestamp(self):
        when = datetime(2030, 1, 1, 9, 0, tzinfo=timezone.utc)
        assert schedule_at(when) == int(when.timestamp())

    def test_a_naive_datetime_is_read_as_local_time(self):
        """Which is what somebody writing a wall-clock time means by it."""
        when = datetime(2030, 1, 1, 9, 0)
        assert schedule_at(when) == int(when.astimezone().timestamp())

    def test_when_online_is_not_converted(self):
        """The one value that is a flag wearing a timestamp's clothes.

        Reading it as a date and converting it would schedule the message for
        the far future instead of for the next time they appear, and nothing
        would look wrong until the message failed to arrive.
        """
        assert schedule_at(WHEN_ONLINE) == WHEN_ONLINE
        assert WHEN_ONLINE == 0x7FFFFFFE


class TestScheduledSend:
    async def test_the_date_goes_out_on_the_call(self):
        async with live() as (invoker, server):
            when = datetime(2030, 6, 1, 12, 0, tzinfo=timezone.utc)
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateMessageID(id=42, random_id=query.random_id),
                    types.UpdateNewScheduledMessage(message=a_message(42)),
                ],
                users=[],
                chats=[],
                date=1700000000,
                seq=0,
            )
            await send_message(
                invoker, types.InputPeerSelf(), "later", schedule_date=when
            )
            sent = server.only(functions.messages.SendMessage)
            assert sent.schedule_date == int(when.timestamp())

    async def test_an_unscheduled_send_carries_no_date(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateMessageID(id=7, random_id=query.random_id),
                    types.UpdateNewMessage(
                        message=a_message(7), pts=2, pts_count=1
                    ),
                ],
                users=[],
                chats=[],
                date=1700000000,
                seq=0,
            )
            await send_message(invoker, types.InputPeerSelf(), "now")
            assert server.only(functions.messages.SendMessage).schedule_date is None

    async def test_the_queued_message_comes_back(self):
        """The regression this file exists for.

        A scheduled send is answered with updateNewScheduledMessage, not with
        updateNewMessage. Before this was read, the send raised as though the
        server had answered with nothing, which is the worst kind of wrong: the
        message really was queued, and the caller was told it had failed.
        """
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateMessageID(id=99, random_id=query.random_id),
                    types.UpdateNewScheduledMessage(
                        message=a_message(99, "queued")
                    ),
                ],
                users=[],
                chats=[],
                date=1700000000,
                seq=0,
            )
            sent = await send_message(
                invoker,
                types.InputPeerSelf(),
                "queued",
                schedule_date=WHEN_ONLINE,
            )
            assert isinstance(sent, types.Message)
            assert sent.id == 99
            assert sent.message == "queued"

    async def test_a_relative_time_works_the_ordinary_way(self):
        """No timedelta support is needed, since datetime already does it."""
        async with live() as (invoker, server):
            when = datetime.now(timezone.utc) + timedelta(hours=2)
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateMessageID(id=1, random_id=query.random_id),
                    types.UpdateNewScheduledMessage(message=a_message(1)),
                ],
                users=[],
                chats=[],
                date=1700000000,
                seq=0,
            )
            await send_message(
                invoker, types.InputPeerSelf(), "soon", schedule_date=when
            )
            sent = server.only(functions.messages.SendMessage)
            assert sent.schedule_date == int(when.timestamp())


class TestManagingTheQueue:
    async def test_the_whole_queue_is_one_call(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.Messages(
                messages=[a_message(1), a_message(2)], topics=[], chats=[], users=[]
            )
            answer = await scheduled_history(invoker, types.InputPeerSelf())
            assert len(answer.messages) == 2
            server.only(functions.messages.GetScheduledHistory)

    async def test_particular_ones_are_asked_for_by_id(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.Messages(
                messages=[a_message(4)], topics=[], chats=[], users=[]
            )
            await get_scheduled_messages(invoker, types.InputPeerSelf(), [4, 5])
            asked = server.only(functions.messages.GetScheduledMessages)
            assert asked.id == [4, 5]

    async def test_sending_now_names_the_queued_ids(self):
        async with live() as (invoker, server):
            await send_scheduled_messages(invoker, types.InputPeerSelf(), [11, 12])
            asked = server.only(functions.messages.SendScheduledMessages)
            assert asked.id == [11, 12]

    async def test_deleting_names_the_queued_ids(self):
        async with live() as (invoker, server):
            await delete_scheduled_messages(invoker, types.InputPeerSelf(), [13])
            asked = server.only(functions.messages.DeleteScheduledMessages)
            assert asked.id == [13]


class TestTheEvent:
    def test_a_queued_message_is_its_own_kind(self):
        """Not "message": nobody has received it, and we are the ones who
        queued it. A message handler firing here would be wrong."""
        from sunnygram.dispatcher import KINDS, _READINGS

        kind, _ = _READINGS[types.UpdateNewScheduledMessage]
        assert kind == "scheduled"
        assert "scheduled" in KINDS
