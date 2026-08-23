"""Topics, and the one idea that makes them work.

A topic is the message that opened it. Everything odd about this part of the
API follows from that: a topic id is a message id, being in a topic is spelled
as replying, and a forum's first topic has no opening message and so is the one
that breaks the rule. That is what these tests pin, along with the paging
cursor, which is three things again and easy to get wrong in a way that quietly
loops.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.methods import forum, messages
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.types import Topic

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
FORUM = types.InputPeerChannel(channel_id=7007, access_hash=21)


def a_topic(id: int, *, title: str = "General", closed: bool = False) -> types.ForumTopic:
    return types.ForumTopic(
        id=id,
        date=1700000000,
        peer=types.PeerChannel(channel_id=7007),
        title=title,
        icon_color=0x6FB9F0,
        top_message=id + 10,
        read_inbox_max_id=0,
        read_outbox_max_id=0,
        unread_count=3,
        unread_mentions_count=1,
        unread_reactions_count=0,
        unread_poll_votes_count=0,
        from_id=types.PeerUser(user_id=ME),
        notify_settings=types.PeerNotifySettings(),
        closed=closed,
    )


def a_message(id: int) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerChannel(channel_id=7007),
        date=1700000000 + id,
        message=f"message {id}",
    )


def _topic_pages(total: int, each: int) -> Any:
    """Answer getForumTopics with a slice at a time, ending when they run out."""
    handed = 0

    def answer(query: Any) -> Any:
        nonlocal handed
        if not isinstance(query, functions.messages.GetForumTopics):
            return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        left = max(0, total - handed)
        count = min(each, query.limit, left)
        topics = [a_topic(handed + n + 1) for n in range(count)]
        handed += count
        return types.messages.ForumTopics(
            count=total,
            topics=topics,
            messages=[a_message(topic.top_message) for topic in topics],
            chats=[],
            users=[],
            pts=1,
        )

    return answer


class TestWhereAMessageGoes:
    """The reply field, which says both who is being answered and where."""

    def test_neither_is_no_header_at_all(self):
        assert messages.reply_header(None, None) is None

    def test_a_topic_on_its_own_is_a_reply_to_the_topic(self):
        header = messages.reply_header(None, 42)
        assert header.reply_to_msg_id == 42
        assert header.top_msg_id is None

    def test_a_reply_inside_a_topic_names_both(self):
        header = messages.reply_header(99, 42)
        assert header.reply_to_msg_id == 99
        assert header.top_msg_id == 42

    def test_a_plain_reply_names_no_topic(self):
        header = messages.reply_header(99)
        assert header.reply_to_msg_id == 99
        assert header.top_msg_id is None

    async def test_sending_into_a_topic_goes_through_that_field(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.Updates(
                updates=[
                    types.UpdateMessageID(id=5, random_id=query.random_id),
                    types.UpdateNewChannelMessage(
                        message=a_message(5), pts=1, pts_count=1
                    ),
                ],
                users=[],
                chats=[],
                date=0,
                seq=0,
            )
            await messages.send_message(invoker, FORUM, "hello", topic=42)
        sent = server.only(functions.messages.SendMessage)
        assert sent.reply_to.reply_to_msg_id == 42


class TestPaging:
    async def test_the_cursor_is_the_topic_and_its_last_message(self):
        async with live() as (invoker, server):
            server.answer_with = _topic_pages(total=4, each=2)
            pages = [
                page
                async for page in forum.iter_topic_pages(
                    invoker, FORUM, limit=4, batch=2
                )
            ]
        assert len(pages) == 2
        calls = server.all(functions.messages.GetForumTopics)
        assert (calls[0].offset_topic, calls[0].offset_id) == (0, 0)
        # The second page starts after the last topic of the first, named by
        # its own id and by the message it was last active on.
        assert calls[1].offset_topic == 2
        assert calls[1].offset_id == 12
        assert calls[1].offset_date == 1700000000 + 12

    async def test_an_empty_page_ends_the_walk(self):
        async with live() as (invoker, server):
            server.answer_with = _topic_pages(total=0, each=2)
            pages = [page async for page in forum.iter_topic_pages(invoker, FORUM)]
        assert pages == []
        assert len(server.all(functions.messages.GetForumTopics)) == 1

    async def test_a_short_page_is_the_last_one(self):
        async with live() as (invoker, server):
            server.answer_with = _topic_pages(total=3, each=100)
            pages = [
                page
                async for page in forum.iter_topic_pages(
                    invoker, FORUM, limit=100, batch=100
                )
            ]
        assert len(pages) == 1
        assert len(server.all(functions.messages.GetForumTopics)) == 1

    async def test_the_limit_is_not_overshot(self):
        async with live() as (invoker, server):
            server.answer_with = _topic_pages(total=10, each=2)
            pages = [
                page
                async for page in forum.iter_topic_pages(
                    invoker, FORUM, limit=3, batch=2
                )
            ]
        assert sum(len(page.topics) for page in pages) <= 4
        assert server.all(functions.messages.GetForumTopics)[-1].limit == 1

    async def test_a_page_ending_in_a_deleted_topic_stops(self):
        # A deleted topic carries no date and no message, so there is nothing
        # to build the next cursor out of. Asking again with the old one would
        # hand back the same page for ever.
        def answer(query: Any) -> Any:
            return types.messages.ForumTopics(
                count=99,
                topics=[a_topic(1), types.ForumTopicDeleted(id=2)],
                messages=[a_message(11)],
                chats=[],
                users=[],
                pts=1,
            )

        async with live() as (invoker, server):
            server.answer_with = answer
            pages = [
                page
                async for page in forum.iter_topic_pages(
                    invoker, FORUM, limit=100, batch=2
                )
            ]
        assert len(pages) == 1
        assert len(server.all(functions.messages.GetForumTopics)) == 1

    async def test_a_search_is_passed_along(self):
        async with live() as (invoker, server):
            server.answer_with = _topic_pages(total=0, each=2)
            async for _ in forum.iter_topic_pages(invoker, FORUM, query="bugs"):
                pass
        assert server.only(functions.messages.GetForumTopics).q == "bugs"


class TestChangingATopic:
    async def test_creating_one_carries_a_random_id(self):
        async with live() as (invoker, server):
            await forum.create_topic(invoker, FORUM, "Bugs", icon_color=0x6FB9F0)
        call = server.only(functions.messages.CreateForumTopic)
        assert call.title == "Bugs"
        assert call.random_id != 0

    async def test_a_topic_needs_a_title(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="needs a title"):
                await forum.create_topic(invoker, FORUM, "")

    async def test_editing_nothing_is_refused_before_the_call(self):
        async with live() as (invoker, server):
            with pytest.raises(ValueError, match="change nothing"):
                await forum.edit_topic(invoker, FORUM, 42)
        assert not server.all(functions.messages.EditForumTopic)

    async def test_closing_sets_only_the_one_field(self):
        async with live() as (invoker, server):
            await forum.edit_topic(invoker, FORUM, 42, closed=True)
        call = server.only(functions.messages.EditForumTopic)
        assert call.closed is True
        assert call.title is None and call.hidden is None

    async def test_pinning_says_which_topic(self):
        async with live() as (invoker, server):
            await forum.pin_topic(invoker, FORUM, 42)
        call = server.only(functions.messages.UpdatePinnedForumTopic)
        assert (call.topic_id, call.pinned) == (42, True)

    async def test_reordering_takes_the_pinned_ones_in_order(self):
        async with live() as (invoker, server):
            await forum.reorder_topics(invoker, FORUM, [3, 1, 2], force=True)
        call = server.only(functions.messages.ReorderPinnedForumTopics)
        assert call.order == [3, 1, 2] and call.force is True

    async def test_turning_a_group_into_a_forum(self):
        async with live() as (invoker, server):
            await forum.toggle_forum(invoker, FORUM, True)
        assert server.only(functions.channels.ToggleForum).enabled is True


class TestDeleting:
    """A history goes a slice at a time, and the caller should not have to know."""

    async def test_it_keeps_asking_until_nothing_is_left(self):
        rounds = iter([300, 200, 0])

        def answer(query: Any) -> Any:
            return types.messages.AffectedHistory(
                pts=1, pts_count=100, offset=next(rounds)
            )

        async with live() as (invoker, server):
            server.answer_with = answer
            removed = await forum.delete_topic(invoker, FORUM, 42)
        assert len(server.all(functions.messages.DeleteTopicHistory)) == 3
        assert removed == 300

    async def test_a_topic_being_written_to_does_not_loop_forever(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.AffectedHistory(
                pts=1, pts_count=1, offset=999
            )
            await forum.delete_topic(invoker, FORUM, 42, rounds=3)
        assert len(server.all(functions.messages.DeleteTopicHistory)) == 3


class TestWrapping:
    """What a program actually holds, rather than what came off the wire."""

    def test_a_topic_carries_its_thread_and_its_unread(self):
        wrapped = Topic.from_raw(
            a_topic(42, title="Bugs"),
            messages={52: a_message(52)},
        )
        assert wrapped is not None
        assert (wrapped.id, wrapped.title) == (42, "Bugs")
        assert wrapped.chat_id == 7007
        assert wrapped.unread == 3
        assert wrapped.top_message is not None
        assert wrapped.top_message.id == 52

    def test_a_closed_topic_says_so_in_its_repr(self):
        wrapped = Topic.from_raw(a_topic(42, closed=True))
        assert wrapped is not None and "closed" in repr(wrapped)

    def test_a_deleted_topic_is_nothing_to_wrap(self):
        assert Topic.from_raw(types.ForumTopicDeleted(id=42)) is None

    def test_the_general_topic_is_the_one_every_forum_has(self):
        assert forum.GENERAL_TOPIC == 1


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


class RecordingServer(ScriptedServer):
    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.seen: list[Any] = []
        self.answer_with: Any = None

    async def serve(self) -> None:
        while True:
            request = await self.take()
            self.seen.append(request.query)
            try:
                made = (
                    self.answer_with(request.query)
                    if self.answer_with is not None
                    else types.Updates(
                        updates=[], users=[], chats=[], date=1700000000, seq=0
                    )
                )
            except Exception as failure:
                await self.refuse(request.msg_id, 500, f"SCRIPT_FAILED: {failure!r}")
                continue
            await self.answer(request.msg_id, made)

    def all(self, kind: type) -> list[Any]:
        return [query for query in self.seen if isinstance(query, kind)]

    def only(self, kind: type) -> Any:
        found = self.all(kind)
        assert len(found) == 1, f"expected one {kind.__name__}, got {len(found)}"
        return found[0]


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
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
