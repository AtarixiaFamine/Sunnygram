"""Sending a message, and finding the one that was sent.

The call answers with updates rather than with a message, so most of what is
tested here is the finding: matching our random id to the message id the server
gave it, and assembling the message ourselves when the server sends the
shorthand instead of the real thing.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import random_id, send_message
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.updates import UpdateManager

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000


def a_message(id: int, text: str, peer: Any = None) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=ME) if peer is None else peer,
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


class SendServer(ScriptedServer):
    """A datacenter that accepts messages and says what it made of them."""

    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.sent: list[functions.messages.SendMessage] = []
        self.answer_with: Any = None
        self.next_id = 555

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            if isinstance(query, functions.messages.SendMessage):
                self.sent.append(query)
                await self.answer(request.msg_id, self._made_of(query))
            elif isinstance(query, functions.updates.GetState):
                await self.answer(
                    request.msg_id,
                    types.updates.State(
                        pts=100, qts=0, date=1700000000, seq=10, unread_count=0
                    ),
                )
            else:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")

    def _made_of(self, query: functions.messages.SendMessage) -> Any:
        if self.answer_with is not None:
            answer, self.answer_with = self.answer_with, None
            if callable(answer):
                return answer(query)
            return answer
        return types.Updates(
            updates=[
                types.UpdateMessageID(id=self.next_id, random_id=query.random_id),
                types.UpdateNewMessage(
                    message=a_message(self.next_id, query.message),
                    pts=101,
                    pts_count=1,
                ),
            ],
            users=[],
            chats=[],
            date=1700000000,
            seq=11,
        )


@asynccontextmanager
async def live() -> AsyncIterator[tuple[Invoker, SendServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    invoker = Invoker(
        MemoryStorage(session),
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = SendServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()


class TestSending:
    async def test_the_message_the_server_made_comes_back(self):
        async with live() as (invoker, server):
            sent = await send_message(invoker, types.InputPeerSelf(), "hello")
            assert isinstance(sent, types.Message)
            assert sent.id == 555
            assert sent.message == "hello"

    async def test_every_message_carries_a_fresh_random_id(self):
        async with live() as (invoker, server):
            await send_message(invoker, types.InputPeerSelf(), "one")
            await send_message(invoker, types.InputPeerSelf(), "two")
            ids = [call.random_id for call in server.sent]
            assert len(set(ids)) == 2
            assert all(-(2**63) <= value < 2**63 for value in ids)

    async def test_an_empty_message_is_refused_before_it_is_sent(self):
        async with live() as (invoker, server):
            with pytest.raises(ValueError, match="something in it"):
                await send_message(invoker, types.InputPeerSelf(), "")
            assert server.sent == []

    async def test_a_reply_says_what_it_replies_to(self):
        async with live() as (invoker, server):
            await send_message(invoker, types.InputPeerSelf(), "hi", reply_to=9)
            assert server.sent[0].reply_to.reply_to_msg_id == 9

    async def test_the_flags_go_out(self):
        async with live() as (invoker, server):
            await send_message(
                invoker, types.InputPeerSelf(), "hi", silent=True, no_webpage=True
            )
            assert server.sent[0].silent is True
            assert server.sent[0].no_webpage is True

    async def test_our_message_is_picked_out_of_a_busy_answer(self):
        # The same container can carry somebody else's message. Matching on the
        # random id we chose is what keeps the right one.
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateNewMessage(
                        message=a_message(900, "somebody else"), pts=100, pts_count=1
                    ),
                    types.UpdateMessageID(id=901, random_id=query.random_id),
                    types.UpdateNewMessage(
                        message=a_message(901, query.message), pts=101, pts_count=1
                    ),
                ],
                users=[],
                chats=[],
                date=1700000000,
                seq=11,
            )
            sent = await send_message(invoker, types.InputPeerSelf(), "ours")
            assert (sent.id, sent.message) == (901, "ours")

    async def test_an_answer_with_no_message_in_it_says_so(self):
        async with live() as (invoker, server):
            server.answer_with = types.Updates(
                updates=[], users=[], chats=[], date=1, seq=0
            )
            with pytest.raises(SunnygramError, match="no message in it"):
                await send_message(invoker, types.InputPeerSelf(), "hi")


class TestShorthand:
    async def test_the_message_is_assembled_from_what_we_know(self):
        # updateShortSentMessage carries the id and the date and nothing else,
        # because the server knows we already have the rest: we wrote it.
        async with live() as (invoker, server):
            server.answer_with = types.UpdateShortSentMessage(
                id=42, pts=101, pts_count=1, date=1700000005, out=True
            )
            sent = await send_message(invoker, types.InputPeerSelf(), "written here")
            assert sent.id == 42
            assert sent.message == "written here"
            assert sent.date == 1700000005
            assert sent.out is True
            assert sent.peer_id == types.PeerUser(user_id=ME)
            assert sent.from_id == types.PeerUser(user_id=ME)

    async def test_the_peer_it_was_addressed_to_is_kept(self):
        async with live() as (invoker, server):
            server.answer_with = types.UpdateShortSentMessage(
                id=42, pts=101, pts_count=1, date=1, out=True
            )
            sent = await send_message(
                invoker,
                types.InputPeerChannel(channel_id=55, access_hash=9),
                "to a channel",
            )
            assert sent.peer_id == types.PeerChannel(channel_id=55)

    async def test_a_reply_survives_the_shorthand(self):
        async with live() as (invoker, server):
            server.answer_with = types.UpdateShortSentMessage(
                id=42, pts=101, pts_count=1, date=1, out=True
            )
            sent = await send_message(
                invoker, types.InputPeerSelf(), "an answer", reply_to=7
            )
            assert sent.reply_to.reply_to_msg_id == 7

    async def test_a_peer_that_names_nobody_is_refused(self):
        async with live() as (invoker, server):
            server.answer_with = types.UpdateShortSentMessage(
                id=42, pts=101, pts_count=1, date=1, out=True
            )
            with pytest.raises(SunnygramError, match="does not name a peer"):
                await send_message(invoker, types.InputPeerEmpty(), "nowhere")


class TestKeepingTheStateStraight:
    async def test_the_answer_moves_the_counters(self):
        # The updates a call answers with count exactly as much as the ones that
        # arrive on their own, and only the manager is allowed to apply them.
        async with live() as (invoker, server):
            manager = UpdateManager(invoker)
            await manager.start()
            assert manager.state.pts == 100

            sent = await send_message(
                invoker, types.InputPeerSelf(), "hi", updates=manager
            )
            assert sent.id == 555
            assert manager.state.pts == 101
            event = await asyncio.wait_for(manager.events.get(), 5)
            assert event.update.message.id == 555
            await manager.stop()

    async def test_the_same_message_is_not_delivered_twice(self):
        # The server also pushes the update it just answered with. The counter
        # is what makes the second copy a duplicate rather than a new message.
        async with live() as (invoker, server):
            manager = UpdateManager(invoker)
            await manager.start()
            await send_message(invoker, types.InputPeerSelf(), "hi", updates=manager)
            await asyncio.wait_for(manager.events.get(), 5)

            await server.send(
                types.Updates(
                    updates=[
                        types.UpdateNewMessage(
                            message=a_message(555, "hi"), pts=101, pts_count=1
                        )
                    ],
                    users=[],
                    chats=[],
                    date=1700000000,
                    seq=11,
                )
            )
            await asyncio.sleep(0.05)
            assert manager.events.empty()
            assert manager.state.pts == 101
            await manager.stop()

    async def test_without_a_manager_nothing_moves(self):
        async with live() as (invoker, server):
            await send_message(invoker, types.InputPeerSelf(), "hi")
            assert invoker.state.updates.pts == 0


def test_random_ids_do_not_repeat():
    assert len({random_id() for _ in range(1000)}) == 1000
