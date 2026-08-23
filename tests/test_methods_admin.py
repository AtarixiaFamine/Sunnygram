"""Running a chat.

Two things are worth testing here and they are different. The rights types are
pure and are checked directly, because the one thing that can go wrong with them
is the inversion, and getting that backwards silences a chat. The methods are
driven against a scripted datacenter that records what arrived, because the one
thing that can go wrong with them is building the wrong call for the kind of
chat they were handed, and that is only visible on the wire.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import admin
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.types import AdminRights, Member, MemberStatus, Permissions

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
SUPERGROUP = types.InputPeerChannel(channel_id=7007, access_hash=21)
BASIC = types.InputPeerChat(chat_id=5005)
SOMEBODY = types.InputPeerUser(user_id=1001, access_hash=3003)


class TestAdminRights:
    def test_nothing_is_granted_by_default(self):
        assert AdminRights().granted == ()
        assert all(
            not getattr(AdminRights().to_raw(), name)
            for name in ("ban_users", "delete_messages", "add_admins")
        )

    def test_a_preset_says_what_it_grants(self):
        rights = AdminRights.moderator()
        assert "ban_users" in rights.granted
        assert "add_admins" not in rights.granted

    def test_everything_stops_short_of_anonymity(self):
        rights = AdminRights.everything()
        assert rights.add_admins and rights.ban_users
        assert not rights.anonymous

    def test_they_map_straight_across(self):
        raw = AdminRights(ban_users=True, pin_messages=True).to_raw()
        assert raw.ban_users and raw.pin_messages
        assert not raw.add_admins

    def test_reading_one_back(self):
        raw = types.ChatAdminRights(delete_messages=True, invite_users=True)
        rights = AdminRights.from_raw(raw)
        assert rights.granted == ("delete_messages", "invite_users")

    def test_they_do_not_mutate(self):
        rights = AdminRights.moderator()
        changed = rights.with_(add_admins=True)
        assert changed.add_admins
        assert not rights.add_admins

    def test_it_says_what_it_is(self):
        assert repr(AdminRights()) == "AdminRights(nothing)"
        assert "ban_users" in repr(AdminRights.moderator())


class TestPermissions:
    def test_everything_is_allowed_by_default(self):
        assert Permissions().denied == ()

    def test_the_flags_are_inverted_on_the_way_out(self):
        # The whole reason this type exists. Allowed here is not-banned there.
        raw = Permissions().to_raw()
        assert not raw.send_messages
        assert not raw.view_messages
        assert not raw.send_photos

    def test_denying_one_thing(self):
        raw = Permissions(send_media=False).to_raw()
        assert raw.send_media
        assert not raw.send_messages

    def test_read_only_leaves_only_reading(self):
        rights = Permissions.read_only()
        assert rights.view_messages
        assert not rights.send_messages
        raw = rights.to_raw()
        assert not raw.view_messages
        assert raw.send_messages

    def test_none_takes_the_chat_away_too(self):
        raw = Permissions.none().to_raw()
        assert raw.view_messages and raw.send_messages

    def test_reading_one_back_inverts_again(self):
        raw = types.ChatBannedRights(until_date=0, send_media=True, send_polls=True)
        rights = Permissions.from_raw(raw)
        assert not rights.send_media and not rights.send_polls
        assert rights.send_messages

    def test_a_round_trip_is_the_same_set(self):
        original = Permissions(send_media=False, pin_messages=False)
        assert Permissions.from_raw(original.to_raw()) == original

    def test_forever_is_zero_rather_than_missing(self):
        assert Permissions().to_raw().until_date == 0
        assert Permissions().to_raw(until=1800000000).until_date == 1800000000

    def test_it_says_what_it_denies(self):
        assert repr(Permissions()) == "Permissions(everything allowed denied)"
        assert "send_media" in repr(Permissions(send_media=False))


class TestPromoting:
    async def test_it_names_the_person_and_the_powers(self):
        async with live() as (invoker, server):
            await admin.promote(
                invoker, SUPERGROUP, SOMEBODY, AdminRights.moderator(), title="mod"
            )
        call = server.only(functions.channels.EditAdmin)
        assert call.channel.channel_id == 7007
        assert call.user_id.user_id == 1001
        assert call.rank == "mod"
        assert call.admin_rights.ban_users and not call.admin_rights.add_admins

    async def test_demoting_grants_nothing(self):
        async with live() as (invoker, server):
            await admin.demote(invoker, SUPERGROUP, SOMEBODY)
        call = server.only(functions.channels.EditAdmin)
        assert not any(
            getattr(call.admin_rights, name)
            for name in ("ban_users", "delete_messages", "add_admins", "change_info")
        )

    async def test_a_basic_group_says_so_rather_than_failing_oddly(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="supergroup or a channel"):
                await admin.promote(invoker, BASIC, SOMEBODY)


class TestRestricting:
    async def test_restricting_sends_the_inverted_flags(self):
        async with live() as (invoker, server):
            await admin.restrict_member(
                invoker, SUPERGROUP, SOMEBODY, Permissions(send_media=False)
            )
        call = server.only(functions.channels.EditBanned)
        assert call.banned_rights.send_media
        assert not call.banned_rights.send_messages

    async def test_a_ban_takes_the_chat_away(self):
        async with live() as (invoker, server):
            await admin.ban_member(invoker, SUPERGROUP, SOMEBODY)
        call = server.only(functions.channels.EditBanned)
        assert call.banned_rights.view_messages

    async def test_a_ban_can_end(self):
        async with live() as (invoker, server):
            await admin.ban_member(invoker, SUPERGROUP, SOMEBODY, until=1800000000)
        assert server.only(functions.channels.EditBanned).banned_rights.until_date == (
            1800000000
        )

    async def test_unbanning_lifts_everything(self):
        async with live() as (invoker, server):
            await admin.unban_member(invoker, SUPERGROUP, SOMEBODY)
        rights = server.only(functions.channels.EditBanned).banned_rights
        assert not rights.view_messages and not rights.send_messages

    async def test_kicking_a_supergroup_member_is_a_ban_then_an_unban(self):
        async with live() as (invoker, server):
            await admin.kick_member(invoker, SUPERGROUP, SOMEBODY)
        calls = server.all(functions.channels.EditBanned)
        assert len(calls) == 2
        assert calls[0].banned_rights.view_messages
        assert not calls[1].banned_rights.view_messages

    async def test_kicking_from_a_basic_group_has_its_own_call(self):
        async with live() as (invoker, server):
            await admin.kick_member(invoker, BASIC, SOMEBODY)
        assert server.only(functions.messages.DeleteChatUser).chat_id == 5005
        assert not server.all(functions.channels.EditBanned)


class TestTheChatItself:
    async def test_renaming_a_supergroup(self):
        async with live() as (invoker, server):
            await admin.set_chat_title(invoker, SUPERGROUP, "New name")
        assert server.only(functions.channels.EditTitle).title == "New name"

    async def test_renaming_a_basic_group_takes_the_other_call(self):
        async with live() as (invoker, server):
            await admin.set_chat_title(invoker, BASIC, "New name")
        assert server.only(functions.messages.EditChatTitle).chat_id == 5005

    async def test_removing_a_photo_is_its_own_constructor(self):
        async with live() as (invoker, server):
            await admin.set_chat_photo(invoker, SUPERGROUP, None)
        call = server.only(functions.channels.EditPhoto)
        assert isinstance(call.photo, types.InputChatPhotoEmpty)

    async def test_the_description_takes_a_plain_peer(self):
        async with live() as (invoker, server):
            await admin.set_chat_description(invoker, SUPERGROUP, "About us")
        call = server.only(functions.messages.EditChatAbout)
        assert call.about == "About us"
        assert isinstance(call.peer, types.InputPeerChannel)

    async def test_default_permissions_are_inverted_too(self):
        async with live() as (invoker, server):
            await admin.set_chat_permissions(
                invoker, SUPERGROUP, Permissions(send_polls=False)
            )
        rights = server.only(functions.messages.EditChatDefaultBannedRights)
        assert rights.banned_rights.send_polls
        assert not rights.banned_rights.send_messages

    async def test_slow_mode_passes_the_number_through(self):
        async with live() as (invoker, server):
            await admin.set_slow_mode(invoker, SUPERGROUP, 30)
        assert server.only(functions.channels.ToggleSlowMode).seconds == 30

    async def test_slow_mode_needs_a_supergroup(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="slow mode"):
                await admin.set_slow_mode(invoker, BASIC, 30)


class TestMakingAndUnmaking:
    async def test_a_group_carries_its_members(self):
        async with live() as (invoker, server):
            await admin.create_group(invoker, "Ours", [SOMEBODY])
        call = server.only(functions.messages.CreateChat)
        assert call.title == "Ours"
        assert call.users[0].user_id == 1001

    async def test_a_broadcast_is_not_a_megagroup(self):
        async with live() as (invoker, server):
            await admin.create_channel(invoker, "News", about="Daily")
        call = server.only(functions.channels.CreateChannel)
        assert call.broadcast and not call.megagroup
        assert call.about == "Daily"

    async def test_a_supergroup_is_the_same_call_the_other_way(self):
        async with live() as (invoker, server):
            await admin.create_channel(invoker, "Chat", megagroup=True)
        call = server.only(functions.channels.CreateChannel)
        assert call.megagroup and not call.broadcast

    async def test_a_forum_is_a_supergroup_with_a_flag(self):
        async with live() as (invoker, server):
            await admin.create_channel(invoker, "Forum", forum=True)
        call = server.only(functions.channels.CreateChannel)
        assert call.forum and call.megagroup and not call.broadcast

    async def test_deleting_picks_the_call_by_kind(self):
        async with live() as (invoker, server):
            await admin.delete_chat(invoker, BASIC)
        assert server.only(functions.messages.DeleteChat).chat_id == 5005

        async with live() as (invoker, server):
            await admin.delete_chat(invoker, SUPERGROUP)
        assert server.only(functions.channels.DeleteChannel).channel.channel_id == 7007


class TestMembersAndLinks:
    async def test_adding_to_a_supergroup_takes_the_whole_list(self):
        async with live() as (invoker, server):
            await admin.add_chat_members(invoker, SUPERGROUP, [SOMEBODY, SOMEBODY])
        assert len(server.only(functions.channels.InviteToChannel).users) == 2

    async def test_a_basic_group_takes_one_at_a_time(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="one person at a time"):
                await admin.add_chat_members(invoker, BASIC, [SOMEBODY, SOMEBODY])

    async def test_a_basic_group_add_carries_the_history_limit(self):
        async with live() as (invoker, server):
            await admin.add_chat_members(
                invoker, BASIC, [SOMEBODY], forward_limit=50
            )
        assert server.only(functions.messages.AddChatUser).fwd_limit == 50

    async def test_an_invite_link_with_no_limits_sends_none_rather_than_zero(self):
        async with live() as (invoker, server):
            await admin.export_invite_link(invoker, SUPERGROUP)
        call = server.only(functions.messages.ExportChatInvite)
        assert call.expire_date is None and call.usage_limit is None

    async def test_an_invite_link_with_limits(self):
        async with live() as (invoker, server):
            await admin.export_invite_link(
                invoker, SUPERGROUP, title="press", expires=1800000000, usage_limit=5
            )
        call = server.only(functions.messages.ExportChatInvite)
        assert (call.title, call.expire_date, call.usage_limit) == (
            "press",
            1800000000,
            5,
        )

    async def test_the_two_kinds_of_link_are_not_mixed(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="usage limit"):
                await admin.export_invite_link(
                    invoker, SUPERGROUP, request_needed=True, usage_limit=5
                )

    async def test_revoking_says_so(self):
        async with live() as (invoker, server):
            await admin.revoke_invite_link(invoker, SUPERGROUP, "https://t.me/+abc")
        call = server.only(functions.messages.EditExportedChatInvite)
        assert call.revoked and call.link == "https://t.me/+abc"

    async def test_a_join_request_can_go_either_way(self):
        async with live() as (invoker, server):
            await admin.approve_join_request(invoker, SUPERGROUP, SOMEBODY)
            await admin.approve_join_request(
                invoker, SUPERGROUP, SOMEBODY, approved=False
            )
        calls = server.all(functions.messages.HideChatJoinRequest)
        assert [call.approved for call in calls] == [True, False]

    async def test_the_whole_queue_is_one_call_rather_than_a_loop(self):
        # A week of requests answered one at a time is that many calls and the
        # flood wait that comes with them, which is why this call exists.
        async with live() as (invoker, server):
            await admin.approve_all_join_requests(invoker, SUPERGROUP)
        call = server.only(functions.messages.HideAllChatJoinRequests)
        assert call.approved is True
        assert call.link is None

    async def test_the_whole_queue_can_be_narrowed_to_one_link(self):
        async with live() as (invoker, server):
            await admin.approve_all_join_requests(
                invoker, SUPERGROUP, approved=False, link="https://t.me/+abc"
            )
        call = server.only(functions.messages.HideAllChatJoinRequests)
        assert call.approved is False
        assert call.link == "https://t.me/+abc"


class TestAdminLog:
    async def test_it_pages_backwards_through_ids(self):
        async with live() as (invoker, server):
            server.answer_with = _log_page
            pages = [
                page
                async for page in admin.iter_admin_log(
                    invoker, SUPERGROUP, limit=6, batch=3
                )
            ]
        assert len(pages) == 2
        calls = server.all(functions.channels.GetAdminLog)
        # The second page starts below the last id of the first, rather than at
        # an offset that would shift while the log is being written to.
        assert calls[0].max_id == 0
        assert calls[1].max_id == calls[0].limit

    async def test_it_stops_when_the_log_runs_out(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.channels.AdminLogResults(
                events=[], chats=[], users=[]
            )
            pages = [
                page async for page in admin.iter_admin_log(invoker, SUPERGROUP)
            ]
        assert pages == []


def _log_page(query: functions.channels.GetAdminLog) -> Any:
    start = query.max_id or 0
    return types.channels.AdminLogResults(
        events=[
            types.ChannelAdminLogEvent(
                id=start + index + 1,
                date=1700000000,
                user_id=1001,
                action=types.ChannelAdminLogEventActionChangeTitle(
                    prev_value="a", new_value="b"
                ),
            )
            for index in range(query.limit)
        ],
        chats=[],
        users=[],
    )


class TestMember:
    """The nine constructors, collapsed to the six standings anybody asks about."""

    def test_a_creator_holds_everything(self):
        member = Member.from_raw(
            types.ChannelParticipantCreator(
                user_id=1001, admin_rights=types.ChatAdminRights()
            )
        )
        assert member.status is MemberStatus.CREATOR
        assert member.is_admin and member.present
        # Said in full rather than read off the rights, which a creator's are
        # not: Telegram sends them empty and means the opposite.
        assert member.rights is not None and member.rights.add_admins

    def test_an_admin_holds_what_was_granted(self):
        member = Member.from_raw(
            types.ChannelParticipantAdmin(
                user_id=1001,
                promoted_by=ME,
                date=1700000000,
                admin_rights=types.ChatAdminRights(ban_users=True),
                rank="mod",
            )
        )
        assert member.status is MemberStatus.ADMIN
        assert member.is_admin
        assert member.rights is not None and member.rights.ban_users
        assert not member.rights.add_admins
        assert member.title == "mod"
        assert member.promoted_by == ME

    def test_a_plain_member_holds_nothing(self):
        member = Member.from_raw(types.ChannelParticipant(user_id=1001, date=0))
        assert member.status is MemberStatus.MEMBER
        assert not member.is_admin
        assert member.present
        assert member.rights is None

    def test_restricted_and_banned_are_told_apart_by_being_there(self):
        # One constructor for both, and the flag is the whole difference.
        restricted = Member.from_raw(
            types.ChannelParticipantBanned(
                peer=types.PeerUser(user_id=1001),
                kicked_by=ME,
                date=0,
                banned_rights=types.ChatBannedRights(
                    until_date=0, send_photos=True
                ),
            )
        )
        assert restricted.status is MemberStatus.RESTRICTED
        assert restricted.present
        assert restricted.permissions is not None
        assert not restricted.permissions.send_photos

        banned = Member.from_raw(
            types.ChannelParticipantBanned(
                peer=types.PeerUser(user_id=1001),
                left=True,
                kicked_by=ME,
                date=0,
                banned_rights=types.ChatBannedRights(until_date=0),
            )
        )
        assert banned.status is MemberStatus.BANNED
        assert not banned.present

    def test_somebody_who_left(self):
        member = Member.from_raw(
            types.ChannelParticipantLeft(peer=types.PeerUser(user_id=1001))
        )
        assert member.status is MemberStatus.LEFT
        assert not member.present
        assert member.user_id == 1001

    def test_a_basic_group_says_the_same_things_differently(self):
        assert (
            Member.from_raw(
                types.ChatParticipantCreator(user_id=1001)
            ).status
            is MemberStatus.CREATOR
        )
        assert (
            Member.from_raw(
                types.ChatParticipantAdmin(user_id=1001, inviter_id=ME, date=0)
            ).status
            is MemberStatus.ADMIN
        )
        assert (
            Member.from_raw(
                types.ChatParticipant(user_id=1001, inviter_id=ME, date=0)
            ).status
            is MemberStatus.MEMBER
        )


class TestGetMember:
    async def test_a_channel_is_asked_directly(self):
        def answer(query: Any) -> Any:
            return types.channels.ChannelParticipant(
                participant=types.ChannelParticipant(user_id=1001, date=0),
                chats=[],
                users=[],
            )

        async with live() as (invoker, server):
            server.answer_with = answer
            found = await admin.get_member(invoker, SUPERGROUP, SOMEBODY)
        assert isinstance(found, types.ChannelParticipant)
        assert server.only(functions.channels.GetParticipant)

    async def test_a_basic_group_is_picked_out_of_the_whole_membership(self):
        # There is no call for one member of a basic group, so the only way to
        # answer is to fetch all of them. Cheap, for the size one is allowed.
        def answer(query: Any) -> Any:
            return types.messages.ChatFull(
                full_chat=types.ChatFull(
                    id=5005,
                    about="",
                    participants=types.ChatParticipants(
                        chat_id=5005,
                        participants=[
                            types.ChatParticipant(
                                user_id=2002, inviter_id=ME, date=0
                            ),
                            types.ChatParticipantAdmin(
                                user_id=1001, inviter_id=ME, date=0
                            ),
                        ],
                        version=1,
                    ),
                    notify_settings=types.PeerNotifySettings(),
                ),
                chats=[],
                users=[],
            )

        async with live() as (invoker, server):
            server.answer_with = answer
            found = await admin.get_member(invoker, BASIC, SOMEBODY)
        assert isinstance(found, types.ChatParticipantAdmin)
        assert found.user_id == 1001
        assert server.only(functions.messages.GetFullChat)

    async def test_somebody_not_in_a_basic_group_is_nothing_rather_than_an_error(self):
        def answer(query: Any) -> Any:
            return types.messages.ChatFull(
                full_chat=types.ChatFull(
                    id=5005,
                    about="",
                    participants=types.ChatParticipants(
                        chat_id=5005, participants=[], version=1
                    ),
                    notify_settings=types.PeerNotifySettings(),
                ),
                chats=[],
                users=[],
            )

        async with live() as (invoker, server):
            server.answer_with = answer
            assert await admin.get_member(invoker, BASIC, SOMEBODY) is None


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


class RecordingServer(ScriptedServer):
    """A datacenter that writes down every call and agrees with all of them.

    Answering with an empty Updates is enough for everything here: none of
    these methods reads the answer, they only build the call, and the call is
    what is being checked.
    """

    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.seen: list[Any] = []
        self.answer_with: Any = None

    async def serve(self) -> None:
        while True:
            request = await self.take()
            self.seen.append(request.query)
            await self.answer(request.msg_id, self._answer(request.query))

    def _answer(self, query: Any) -> Any:
        if self.answer_with is not None:
            return self.answer_with(query)
        return types.Updates(
            updates=[], users=[], chats=[], date=1700000000, seq=0
        )

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
