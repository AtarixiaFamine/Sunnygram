"""Takeout sessions and folders.

Two unrelated features sharing a file because each is small and both are about
an account's own arrangement of itself rather than about messages.

The takeout half has one thing in it worth guarding properly: a takeout that
has not been approved yet is refused with an error that subclasses Flood, and
the connection layer sleeps through FloodWait automatically. If those two ever
met, a program asking for an export would silently block for hours inside one
call instead of being told a person has to approve something.
"""

from __future__ import annotations

import pytest

from mtproto_server import recording
from sunnygram.errors import Flood, FloodWait, TakeoutInitDelay
from sunnygram.methods import (
    Takeout,
    build_folder,
    delete_folder,
    finish_takeout,
    get_folders,
    init_takeout,
    reorder_folders,
    save_folder,
)
from sunnygram.raw import functions, types
from sunnygram.types import Folder


def a_filter(id: int, title: str = "Work", **flags: object) -> types.DialogFilter:
    return types.DialogFilter(
        id=id,
        title=types.TextWithEntities(text=title, entities=[]),
        pinned_peers=[],
        include_peers=[types.InputPeerUser(user_id=5, access_hash=1)],
        exclude_peers=[],
        **flags,
    )


class TestTheApprovalError:
    """No server needed: this is about the class tree, and it is load-bearing."""

    def test_a_takeout_delay_is_not_a_flood_wait(self):
        assert issubclass(TakeoutInitDelay, Flood)
        assert not issubclass(TakeoutInitDelay, FloodWait)

    def test_so_the_automatic_wait_cannot_swallow_it(self):
        """The connection sleeps through FloodWait and nothing else.

        A takeout delay is a person being asked to approve an export in another
        client, which is hours. Sleeping through it would look like one call
        hanging for ever with nothing said.
        """
        delay = TakeoutInitDelay(420, "TAKEOUT_INIT_DELAY_86400", value=86400)
        assert not isinstance(delay, FloodWait)
        assert delay.seconds == 86400


class TestOpeningATakeout:
    async def test_the_flags_asked_for_go_out(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.account.Takeout(id=99)
            got = await init_takeout(
                invoker, message_users=True, files=True, file_max_size=1024
            )
            assert got == 99
            asked = server.only(functions.account.InitTakeoutSession)
            assert asked.message_users is True
            assert asked.files is True
            assert asked.file_max_size == 1024
            assert asked.contacts is False

    async def test_every_call_inside_one_is_wrapped(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.Config(
                date=0,
                expires=0,
                test_mode=False,
                this_dc=2,
                dc_options=[],
                dc_txt_domain_name="",
                chat_size_max=0,
                megagroup_size_max=0,
                forwarded_count_max=0,
                online_update_period_ms=0,
                offline_blur_timeout_ms=0,
                offline_idle_timeout_ms=0,
                online_cloud_timeout_ms=0,
                notify_cloud_delay_ms=0,
                notify_default_delay_ms=0,
                push_chat_period_ms=0,
                push_chat_limit=0,
                edit_time_limit=0,
                revoke_time_limit=0,
                revoke_pm_time_limit=0,
                rating_e_decay=0,
                stickers_recent_limit=0,
                channels_read_media_period=0,
                call_receive_timeout_ms=0,
                call_ring_timeout_ms=0,
                call_connect_timeout_ms=0,
                call_packet_timeout_ms=0,
                me_url_prefix="",
                caption_length_max=0,
                message_length_max=0,
                webfile_dc_id=4,
            )
            export = Takeout(invoker, 77)
            await export.invoke(functions.help.GetConfig())
            wrapped = server.only(functions.InvokeWithTakeout)
            assert wrapped.takeout_id == 77
            assert isinstance(wrapped.query, functions.help.GetConfig)

    async def test_finishing_goes_out_inside_the_session_it_closes(self):
        """Which is how the server knows which one is meant."""
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await finish_takeout(invoker, 5, success=False)
            wrapped = server.only(functions.InvokeWithTakeout)
            assert wrapped.takeout_id == 5
            assert isinstance(wrapped.query, functions.account.FinishTakeoutSession)
            assert wrapped.query.success is False

    async def test_leaving_the_block_normally_reports_success(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            async with Takeout(invoker, 8):
                pass
            assert server.only(functions.InvokeWithTakeout).query.success is True

    async def test_leaving_it_by_raising_says_the_export_failed(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            with pytest.raises(ZeroDivisionError):
                async with Takeout(invoker, 8):
                    raise ZeroDivisionError
            assert server.only(functions.InvokeWithTakeout).query.success is False

    async def test_a_finished_session_refuses_to_be_used(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            export = Takeout(invoker, 3)
            await export.finish()
            with pytest.raises(RuntimeError, match="finished"):
                await export.invoke(functions.help.GetConfig())


class TestFolders:
    async def test_the_unfiltered_view_is_not_a_folder(self):
        """dialogFilterDefault comes back alongside the real ones and is not
        one: it has no id and nothing to say."""
        assert Folder.from_raw(types.DialogFilterDefault()) is None

    async def test_a_folder_reads_its_title_out_of_styled_text(self):
        """The title stopped being a plain string a few layers ago."""
        wrapped = Folder.from_raw(a_filter(2, "Family"))
        assert wrapped is not None
        assert wrapped.title == "Family"
        assert wrapped.id == 2
        assert wrapped.shared is False
        assert wrapped.editable is True

    async def test_a_shared_folder_says_it_is_not_ours_to_change(self):
        raw = types.DialogFilterChatlist(
            id=9,
            title=types.TextWithEntities(text="Shared", entities=[]),
            pinned_peers=[],
            include_peers=[],
        )
        wrapped = Folder.from_raw(raw)
        assert wrapped is not None
        assert wrapped.shared is True
        assert wrapped.editable is False
        assert wrapped.excluded == ()

    async def test_reading_them_leaves_the_default_out(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.messages.DialogFilters(
                filters=[types.DialogFilterDefault(), a_filter(1)]
            )
            raw = await get_folders(invoker)
            assert len(raw) == 2
            kept = [one for one in (Folder.from_raw(x) for x in raw) if one is not None]
            assert [one.id for one in kept] == [1]

    async def test_building_one_resolves_every_chat_it_names(self):
        async with recording() as (invoker, server):
            built = await build_folder(
                invoker,
                4,
                "Work",
                include=[types.InputPeerSelf()],
                groups=True,
                exclude_muted=True,
            )
            assert isinstance(built, types.DialogFilter)
            assert built.id == 4
            assert built.title.text == "Work"
            assert built.groups is True
            assert built.exclude_muted is True
            assert len(built.include_peers) == 1

    async def test_saving_sends_the_filter(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await save_folder(invoker, 4, a_filter(4))
            asked = server.only(functions.messages.UpdateDialogFilter)
            assert asked.id == 4
            assert asked.filter is not None

    async def test_deleting_is_saving_nothing_under_the_id(self):
        """Telegram has no delete call. This is the whole of it."""
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await delete_folder(invoker, 4)
            asked = server.only(functions.messages.UpdateDialogFilter)
            assert asked.id == 4
            assert asked.filter is None

    async def test_reordering_sends_the_order(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await reorder_folders(invoker, [3, 1, 2])
            assert server.only(functions.messages.UpdateDialogFiltersOrder).order == [
                3,
                1,
                2,
            ]
