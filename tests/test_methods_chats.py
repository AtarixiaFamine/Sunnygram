"""Chats, the people in them, and the paging that is the whole point.

Telegram answers every list a slice at a time and the shape of "where I got to"
is different for each. That bookkeeping is what these modules exist for, so it
is what is tested: that the cursor for the next page is built out of the right
three things, that a page with nothing on it ends the walk, and that the kind of
chat picks the call.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import chats, users
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
SUPERGROUP = types.InputPeerChannel(channel_id=7007, access_hash=21)
BASIC = types.InputPeerChat(chat_id=5005)
SOMEBODY = types.InputPeerUser(user_id=1001, access_hash=3003)


class TestInviteLinks:
    @pytest.mark.parametrize(
        "link",
        [
            "https://t.me/joinchat/AAAAAA",
            "http://t.me/joinchat/AAAAAA",
            "t.me/joinchat/AAAAAA",
            "https://t.me/+AAAAAA",
            "t.me/+AAAAAA",
            "+AAAAAA",
        ],
    )
    async def test_every_spelling_of_a_link_is_an_import(self, link):
        async with live() as (invoker, server):
            await chats.join_chat(invoker, link)
        assert server.only(functions.messages.ImportChatInvite).hash == "AAAAAA"

    async def test_a_username_is_not_an_invite(self):
        async with live() as (invoker, server):
            await chats.join_chat(invoker, SUPERGROUP)
        assert server.only(functions.channels.JoinChannel)


class TestLeaving:
    async def test_a_basic_group_removes_this_account_by_name(self):
        async with live() as (invoker, server):
            await chats.leave_chat(invoker, BASIC)
        call = server.only(functions.messages.DeleteChatUser)
        assert call.chat_id == 5005
        assert isinstance(call.user_id, types.InputUserSelf)

    async def test_a_channel_has_its_own_call(self):
        async with live() as (invoker, server):
            await chats.leave_chat(invoker, SUPERGROUP)
        assert server.only(functions.channels.LeaveChannel)


class TestChatInfo:
    async def test_a_basic_group(self):
        async with live() as (invoker, server):
            server.answer_with = _full_chat
            await chats.chat_info(invoker, BASIC)
        assert server.only(functions.messages.GetFullChat).chat_id == 5005

    async def test_a_channel(self):
        async with live() as (invoker, server):
            server.answer_with = _full_chat
            await chats.chat_info(invoker, SUPERGROUP)
        assert server.only(functions.channels.GetFullChannel)

    async def test_a_person_is_not_a_chat(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="is a person rather than a chat"):
                await chats.chat_info(invoker, SOMEBODY)


class TestDialogPaging:
    async def test_the_cursor_is_the_date_the_id_and_the_peer(self):
        async with live() as (invoker, server):
            server.answer_with = _dialog_pages(total=4, each=2)
            pages = [
                page async for page in chats.iter_dialog_pages(invoker, limit=4, batch=2)
            ]
        assert len(pages) == 2
        calls = server.all(functions.messages.GetDialogs)
        assert calls[0].offset_date == 0
        assert isinstance(calls[0].offset_peer, types.InputPeerEmpty)
        # Passing only the id, which looks like it ought to work, walks a chat
        # rather than the list of them.
        assert calls[1].offset_date and calls[1].offset_id
        assert isinstance(calls[1].offset_peer, types.InputPeerUser)

    async def test_an_empty_page_ends_the_walk(self):
        async with live() as (invoker, server):
            server.answer_with = _dialog_pages(total=0, each=2)
            pages = [page async for page in chats.iter_dialog_pages(invoker)]
        assert pages == []
        assert len(server.all(functions.messages.GetDialogs)) == 1

    async def test_the_unsliced_answer_is_the_whole_list(self):
        # messages.dialogs rather than dialogsSlice means there is no more,
        # however many came back.
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.Dialogs(
                dialogs=[_dialog(1)],
                messages=[_message(1)],
                chats=[],
                users=[_user()],
            )
            pages = [
                page async for page in chats.iter_dialog_pages(invoker, limit=100)
            ]
        assert len(pages) == 1
        assert len(server.all(functions.messages.GetDialogs)) == 1

    async def test_the_limit_is_not_overshot(self):
        async with live() as (invoker, server):
            server.answer_with = _dialog_pages(total=10, each=2)
            pages = [
                page async for page in chats.iter_dialog_pages(invoker, limit=3, batch=2)
            ]
        assert sum(len(page.dialogs) for page in pages) <= 4
        assert server.all(functions.messages.GetDialogs)[-1].limit == 1


class TestParticipantPaging:
    async def test_a_basic_group_is_not_paged_at_all(self):
        async with live() as (invoker, server):
            server.answer_with = _full_chat
            pages = [
                page async for page in chats.iter_participant_pages(invoker, BASIC)
            ]
        assert len(pages) == 1
        assert server.only(functions.messages.GetFullChat)

    async def test_a_channel_pages_by_offset(self):
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=2)
            pages = [
                page
                async for page in chats.iter_participant_pages(
                    invoker, SUPERGROUP, limit=4, batch=2
                )
            ]
        assert len(pages) == 2
        assert [call.offset for call in server.all(functions.channels.GetParticipants)] == [
            0,
            2,
        ]

    async def test_a_search_term_narrows_it(self):
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=0)
            [
                page
                async for page in chats.iter_participant_pages(
                    invoker, SUPERGROUP, query="pavel"
                )
            ]
        chosen = server.only(functions.channels.GetParticipants).filter
        assert isinstance(chosen, types.ChannelParticipantsSearch)
        assert chosen.q == "pavel"

    async def test_no_search_term_asks_for_the_recent_ones(self):
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=0)
            [
                page
                async for page in chats.iter_participant_pages(invoker, SUPERGROUP)
            ]
        assert isinstance(
            server.only(functions.channels.GetParticipants).filter,
            types.ChannelParticipantsRecent,
        )

    @pytest.mark.parametrize(
        ("word", "wanted"),
        [
            ("admins", types.ChannelParticipantsAdmins),
            ("bots", types.ChannelParticipantsBots),
            ("banned", types.ChannelParticipantsKicked),
            ("restricted", types.ChannelParticipantsBanned),
            ("contacts", types.ChannelParticipantsContacts),
        ],
    )
    async def test_a_word_asks_for_that_sort_of_member(self, word, wanted):
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=0)
            [
                page
                async for page in chats.iter_participant_pages(
                    invoker, SUPERGROUP, kind=word
                )
            ]
        assert isinstance(server.only(functions.channels.GetParticipants).filter, wanted)

    async def test_banned_and_restricted_are_the_readable_way_round(self):
        """Telegram's two names for these are the opposite of what they read as.

        Its "kicked" is someone thrown out and its "banned" is someone still in
        the chat but silenced, so the words here are swapped on purpose and this
        is the test that says so.
        """
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=0)
            [
                page
                async for page in chats.iter_participant_pages(
                    invoker, SUPERGROUP, kind="banned"
                )
            ]
            thrown_out = server.only(functions.channels.GetParticipants).filter
        assert isinstance(thrown_out, types.ChannelParticipantsKicked)

    async def test_a_search_term_reaches_a_filter_that_takes_one(self):
        async with live() as (invoker, server):
            server.answer_with = _participant_pages(each=0)
            [
                page
                async for page in chats.iter_participant_pages(
                    invoker, SUPERGROUP, kind="banned", query="pavel"
                )
            ]
        chosen = server.only(functions.channels.GetParticipants).filter
        assert chosen.q == "pavel"


class TestUsers:
    async def test_blocking_and_unblocking(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: True
            assert await users.block_user(invoker, SOMEBODY)
            assert await users.unblock_user(invoker, SOMEBODY)
        assert server.only(functions.contacts.Block)
        assert server.only(functions.contacts.Unblock)

    async def test_only_the_named_fields_change(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: _user()
            await users.update_profile(invoker, first_name="Pavel")
        call = server.only(functions.account.UpdateProfile)
        assert call.first_name == "Pavel"
        assert call.last_name is None and call.about is None

    async def test_clearing_a_field_is_an_empty_string(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: _user()
            await users.update_profile(invoker, about="")
        assert server.only(functions.account.UpdateProfile).about == ""


def _user(id: int = 1001) -> types.User:
    return types.User(id=id, access_hash=id * 3, first_name="Pavel")


def _message(id: int) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=1001),
        date=1700000000 + id,
        message="hi",
    )


def _dialog(top: int) -> types.Dialog:
    return types.Dialog(
        peer=types.PeerUser(user_id=1001),
        top_message=top,
        read_inbox_max_id=0,
        read_outbox_max_id=0,
        unread_count=0,
        unread_mentions_count=0,
        unread_reactions_count=0,
        unread_poll_votes_count=0,
        notify_settings=types.PeerNotifySettings(),
    )


def _dialog_pages(*, total: int, each: int):
    """A server that hands out dialogs a slice at a time until they run out."""
    handed = [0]

    def answer(query: Any) -> Any:
        if not isinstance(query, functions.messages.GetDialogs):
            return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        left = max(0, total - handed[0])
        count = min(each, query.limit, left)
        ids = [handed[0] + index + 1 for index in range(count)]
        handed[0] += count
        return types.messages.DialogsSlice(
            count=total,
            dialogs=[_dialog(id) for id in ids],
            messages=[_message(id) for id in ids],
            chats=[],
            users=[_user()],
        )

    return answer


def _participant_pages(*, each: int):
    handed = [0]

    def answer(query: Any) -> Any:
        if not isinstance(query, functions.channels.GetParticipants):
            return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        count = min(each, query.limit)
        handed[0] += count
        return types.channels.ChannelParticipants(
            count=10,
            participants=[
                types.ChannelParticipant(user_id=index, date=0)
                for index in range(count)
            ],
            chats=[],
            users=[_user()],
        )

    return answer


def _full_chat(query: Any) -> Any:
    if isinstance(query, functions.messages.GetFullChat):
        return types.messages.ChatFull(
            full_chat=types.ChatFull(
                id=5005,
                about="",
                participants=types.ChatParticipantsForbidden(chat_id=5005),
                notify_settings=types.PeerNotifySettings(),
            ),
            chats=[],
            users=[],
        )
    if isinstance(query, functions.channels.GetFullChannel):
        return types.messages.ChatFull(
            full_chat=types.ChannelFull(
                id=7007,
                about="",
                read_inbox_max_id=0,
                read_outbox_max_id=0,
                unread_count=0,
                chat_photo=types.PhotoEmpty(id=0),
                notify_settings=types.PeerNotifySettings(),
                bot_info=[],
                pts=1,
            ),
            chats=[],
            users=[],
        )
    return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)


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
