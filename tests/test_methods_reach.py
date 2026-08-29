"""The four surfaces that used to be reachable only through invoke.

Statistics, boosts, shared folders and sticker sets. What is worth testing in
each is not that a call goes out, which is nearly free to get right, but the
decisions the wrapping makes on the caller's behalf: which of two calls a chat
needs, how a cursor that is a string rather than a number is followed, whether
a flag pair is turned into one word, and the arithmetic Telegram leaves to the
reader and everybody gets wrong.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.methods import boosts, chatlists, stats, stickers
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, PeerKind, PeerRecord, SessionState
from sunnygram.types import BoostStatus

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
CHANNEL = types.InputPeerChannel(channel_id=7007, access_hash=21)
BASIC = types.InputPeerChat(chat_id=5005)
SOMEBODY = types.InputPeerUser(user_id=1001, access_hash=3003)


class TestWhichStatsCall:
    async def test_a_broadcast_channel_is_asked_the_channel_question(self):
        async with live() as (invoker, server):
            invoker.peers._remember(PeerRecord(id=7007, kind=PeerKind.CHANNEL))
            await stats.chat_stats(invoker, CHANNEL)
        assert server.only(functions.stats.GetBroadcastStats)
        assert not server.all(functions.stats.GetMegagroupStats)

    async def test_a_supergroup_is_asked_the_group_question(self):
        """The whole reason chat_stats exists: the two are different calls."""
        async with live() as (invoker, server):
            invoker.peers._remember(PeerRecord(id=7007, kind=PeerKind.SUPERGROUP))
            await stats.chat_stats(invoker, CHANNEL)
        assert server.only(functions.stats.GetMegagroupStats)
        assert not server.all(functions.stats.GetBroadcastStats)

    async def test_a_basic_group_has_no_statistics_at_all(self):
        async with live() as (invoker, _):
            with pytest.raises(TypeError, match="channels and supergroups only"):
                await stats.chat_stats(invoker, BASIC)

    async def test_dark_reaches_the_wire(self):
        async with live() as (invoker, server):
            invoker.peers._remember(PeerRecord(id=7007, kind=PeerKind.CHANNEL))
            await stats.chat_stats(invoker, CHANNEL, dark=True)
        assert server.only(functions.stats.GetBroadcastStats).dark is True


class TestStringCursors:
    """Both of these page by a string the server hands back, not by an offset."""

    async def test_public_forwards_follow_the_cursor_the_server_gives(self):
        async with live() as (invoker, server):
            server.answer_with = _forward_pages(["second", None])
            pages = [
                page
                async for page in stats.iter_public_forward_pages(
                    invoker, CHANNEL, 42, limit=100, batch=1
                )
            ]
        assert len(pages) == 2
        assert [
            call.offset for call in server.all(functions.stats.GetMessagePublicForwards)
        ] == ["", "second"]

    async def test_a_cursor_that_repeats_itself_ends_the_walk(self):
        """A server that keeps saying the same place would page for ever."""
        async with live() as (invoker, server):
            server.answer_with = _forward_pages(["stuck", "stuck", "stuck"])
            pages = [
                page
                async for page in stats.iter_public_forward_pages(
                    invoker, CHANNEL, 42, limit=100, batch=1
                )
            ]
        assert len(pages) == 2

    async def test_boosts_page_by_the_same_kind_of_cursor(self):
        async with live() as (invoker, server):
            server.answer_with = _boost_pages(["more", None])
            pages = [
                page
                async for page in boosts.iter_boost_pages(
                    invoker, CHANNEL, limit=100, batch=1
                )
            ]
        assert len(pages) == 2
        assert [
            call.offset for call in server.all(functions.premium.GetBoostsList)
        ] == ["", "more"]

    async def test_gifts_narrows_the_boost_list(self):
        async with live() as (invoker, server):
            server.answer_with = _boost_pages([None])
            [
                page
                async for page in boosts.iter_boost_pages(invoker, CHANNEL, gifts=True)
            ]
        assert server.only(functions.premium.GetBoostsList).gifts is True


class TestBoostArithmetic:
    def test_needed_counts_from_zero_not_from_the_current_level(self):
        """The trap this type exists for.

        Telegram measures the next level from zero, so the boosts still needed
        are not next_level_boosts minus current_level_boosts. Reading it that
        way is off by everything already spent.
        """
        status = BoostStatus(
            level=3, boosts=47, current_level_boosts=25, next_level_boosts=50
        )
        assert status.needed == 3
        assert status.needed != status.next_level_boosts - status.current_level_boosts

    def test_the_top_of_the_ladder_says_nothing_rather_than_none(self):
        status = BoostStatus(level=10, boosts=900, current_level_boosts=800)
        assert status.needed is None
        assert status.progress == 1.0

    def test_progress_is_across_the_current_level(self):
        status = BoostStatus(
            level=1, boosts=30, current_level_boosts=20, next_level_boosts=40
        )
        assert status.progress == pytest.approx(0.5)

    def test_a_level_already_overshot_does_not_read_past_one(self):
        status = BoostStatus(
            level=1, boosts=99, current_level_boosts=20, next_level_boosts=40
        )
        assert status.progress == 1.0

    def test_wrapping_an_answer_keeps_the_raw_one(self):
        raw = types.premium.BoostsStatus(
            level=2,
            current_level_boosts=10,
            boosts=15,
            next_level_boosts=25,
            boost_url="https://t.me/boost?c=1",
            my_boost=True,
            my_boost_slots=[3, 4],
        )
        status = BoostStatus.from_raw(raw)
        assert status.needed == 10
        assert status.my_slots == (3, 4)
        assert status.mine is True
        assert status.raw is raw


class TestSharedFolders:
    async def test_a_folder_is_named_by_its_id(self):
        async with live() as (invoker, server):
            await chatlists.export_folder_link(
                invoker, 7, title="Reading", peers=[CHANNEL]
            )
        sent = server.only(functions.chatlists.ExportChatlistInvite)
        assert sent.chatlist.filter_id == 7
        assert sent.title == "Reading"

    async def test_leaving_takes_no_chats_unless_asked(self):
        """Leaving chats is the half that cannot be undone quietly."""
        async with live() as (invoker, server):
            await chatlists.leave_folder(invoker, 7)
        assert server.only(functions.chatlists.LeaveChatlist).peers == []

    async def test_editing_a_link_leaves_out_what_was_not_given(self):
        async with live() as (invoker, server):
            await chatlists.edit_folder_link(invoker, 7, "abc", title="New")
        sent = server.only(functions.chatlists.EditExportedInvite)
        assert sent.title == "New"
        assert sent.peers is None


class TestStickerSets:
    async def test_a_set_is_named_by_its_short_name_however_it_is_written(self):
        async with live() as (invoker, server):
            await stickers.rename_sticker_set(invoker, "@Mine ", "Better")
        sent = server.only(functions.stickers.RenameStickerSet)
        assert sent.stickerset.short_name == "Mine"

    @pytest.mark.parametrize(
        ("word", "masks", "emojis"),
        [("regular", False, False), ("mask", True, False), ("emoji", False, True)],
    )
    async def test_one_word_becomes_telegrams_two_flags(self, word, masks, emojis):
        """The schema spells this as two independent flags. It is one choice."""
        async with live() as (invoker, server):
            await stickers.create_sticker_set(
                invoker,
                SOMEBODY,
                title="A set",
                short_name="a_set",
                stickers=[_item()],
                kind=word,
            )
        sent = server.only(functions.stickers.CreateStickerSet)
        assert (sent.masks, sent.emojis) == (masks, emojis)

    async def test_a_set_cannot_be_created_empty(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="cannot be created empty"):
                await stickers.create_sticker_set(
                    invoker, SOMEBODY, title="A set", short_name="a_set", stickers=[]
                )

    async def test_keywords_go_out_as_the_one_string_the_wire_wants(self):
        item = stickers.sticker_item(
            _document(), "🙂", keywords=["happy", "smile"]
        )
        assert item.keywords == "happy,smile"

    async def test_no_keywords_is_absent_rather_than_empty(self):
        assert stickers.sticker_item(_document(), "🙂").keywords is None

    async def test_a_free_short_name_answers_yes_or_no(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: True
            assert await stickers.short_name_free(invoker, "unused_name") is True


# --------------------------------------------------------------------- helpers


def _document() -> Any:
    return types.InputDocument(id=1, access_hash=2, file_reference=b"")


def _item() -> Any:
    return stickers.sticker_item(_document(), "🙂")


def _forward_pages(cursors: list[str | None]):
    handed = [0]

    def answer(query: Any) -> Any:
        if not isinstance(query, functions.stats.GetMessagePublicForwards):
            return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        step = handed[0]
        handed[0] += 1
        if step >= len(cursors):
            return types.stats.PublicForwards(
                count=0, forwards=[], chats=[], users=[]
            )
        return types.stats.PublicForwards(
            count=9,
            forwards=[types.PublicForwardStory(peer=CHANNEL, story=_story())],
            next_offset=cursors[step],
            chats=[],
            users=[],
        )

    return answer


def _story() -> Any:
    return types.StoryItemDeleted(id=1)


def _boost_pages(cursors: list[str | None]):
    handed = [0]

    def answer(query: Any) -> Any:
        if not isinstance(query, functions.premium.GetBoostsList):
            return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
        step = handed[0]
        handed[0] += 1
        if step >= len(cursors):
            return types.premium.BoostsList(count=0, boosts=[], users=[])
        return types.premium.BoostsList(
            count=9,
            boosts=[types.Boost(id="b", date=0, expires=0)],
            next_offset=cursors[step],
            users=[],
        )

    return answer


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
        assert found, f"no {kind.__name__} was sent"
        return found[0]


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
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
