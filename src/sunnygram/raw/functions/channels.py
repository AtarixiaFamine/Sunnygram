# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the channels namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class ReadHistory(TLFunction["bool"]):
    """The TL function channels.readHistory#cc104937, answered with Bool."""

    __slots__ = ("channel", "max_id",)

    ID = 0xCC104937
    QUALNAME = "functions.channels.ReadHistory"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        max_id: int,
    ) -> None:
        self.channel = channel
        self.max_id = max_id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        max_id = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.max_id = max_id
        return self


class DeleteMessages(TLFunction["base.messages.AffectedMessages"]):
    """The TL function channels.deleteMessages#84c1fd4e, answered with messages.AffectedMessages."""

    __slots__ = ("channel", "id",)

    ID = 0x84C1FD4E
    QUALNAME = "functions.channels.DeleteMessages"
    RESULT = "messages.AffectedMessages"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        id: list[int],
    ) -> None:
        self.channel = channel
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.channel = channel
        self.id = id
        return self


class ReportSpam(TLFunction["bool"]):
    """The TL function channels.reportSpam#f44a8315, answered with Bool."""

    __slots__ = ("channel", "participant", "id",)

    ID = 0xF44A8315
    QUALNAME = "functions.channels.ReportSpam"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        participant: base.InputPeer,
        id: list[int],
    ) -> None:
        self.channel = channel
        self.participant = participant
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.participant.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        participant = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.channel = channel
        self.participant = participant
        self.id = id
        return self


class GetMessages(TLFunction["base.messages.Messages"]):
    """The TL function channels.getMessages#ad8c9a23, answered with messages.Messages."""

    __slots__ = ("channel", "id",)

    ID = 0xAD8C9A23
    QUALNAME = "functions.channels.GetMessages"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        id: list[base.InputMessage],
    ) -> None:
        self.channel = channel
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_vector(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        id = r.read_vector()
        self = cls.__new__(cls)
        self.channel = channel
        self.id = id
        return self


class GetParticipants(TLFunction["base.channels.ChannelParticipants"]):
    """The TL function channels.getParticipants#77ced9d0, answered with channels.ChannelParticipants."""

    __slots__ = ("channel", "filter", "offset", "limit", "hash",)

    ID = 0x77CED9D0
    QUALNAME = "functions.channels.GetParticipants"
    RESULT = "channels.ChannelParticipants"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        filter: base.ChannelParticipantsFilter,
        offset: int,
        limit: int,
        hash: int,
    ) -> None:
        self.channel = channel
        self.filter = filter
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.filter.write(w)
        w.write_int(self.offset)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        filter = r.read_object()
        offset = r.read_int()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.channel = channel
        self.filter = filter
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class GetParticipant(TLFunction["base.channels.ChannelParticipant"]):
    """The TL function channels.getParticipant#a0ab6cc6, answered with channels.ChannelParticipant."""

    __slots__ = ("channel", "participant",)

    ID = 0xA0AB6CC6
    QUALNAME = "functions.channels.GetParticipant"
    RESULT = "channels.ChannelParticipant"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        participant: base.InputPeer,
    ) -> None:
        self.channel = channel
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.participant = participant
        return self


class GetChannels(TLFunction["base.messages.Chats"]):
    """The TL function channels.getChannels#0a7f6bbb, answered with messages.Chats."""

    __slots__ = ("id",)

    ID = 0x0A7F6BBB
    QUALNAME = "functions.channels.GetChannels"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        id: list[base.InputChannel],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector()
        self = cls.__new__(cls)
        self.id = id
        return self


class GetFullChannel(TLFunction["base.messages.ChatFull"]):
    """The TL function channels.getFullChannel#08736a09, answered with messages.ChatFull."""

    __slots__ = ("channel",)

    ID = 0x08736A09
    QUALNAME = "functions.channels.GetFullChannel"
    RESULT = "messages.ChatFull"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class CreateChannel(TLFunction["base.Updates"]):
    """The TL function channels.createChannel#91006707, answered with Updates."""

    __slots__ = ("broadcast", "megagroup", "for_import", "forum", "title", "about", "geo_point", "address", "ttl_period",)

    ID = 0x91006707
    QUALNAME = "functions.channels.CreateChannel"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        broadcast: bool = False,
        megagroup: bool = False,
        for_import: bool = False,
        forum: bool = False,
        title: str,
        about: str,
        geo_point: base.InputGeoPoint | None = None,
        address: str | None = None,
        ttl_period: int | None = None,
    ) -> None:
        self.broadcast = broadcast
        self.megagroup = megagroup
        self.for_import = for_import
        self.forum = forum
        self.title = title
        self.about = about
        self.geo_point = geo_point
        self.address = address
        self.ttl_period = ttl_period

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.broadcast:
            flags |= 1 << 0
        if self.megagroup:
            flags |= 1 << 1
        if self.for_import:
            flags |= 1 << 3
        if self.forum:
            flags |= 1 << 5
        if self.geo_point is not None:
            flags |= 1 << 2
        if self.address is not None:
            flags |= 1 << 2
        if self.ttl_period is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_string(self.title)
        w.write_string(self.about)
        if self.geo_point is not None:
            self.geo_point.write(w)
        if self.address is not None:
            w.write_string(self.address)
        if self.ttl_period is not None:
            w.write_int(self.ttl_period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        broadcast = bool(flags & (1 << 0))
        megagroup = bool(flags & (1 << 1))
        for_import = bool(flags & (1 << 3))
        forum = bool(flags & (1 << 5))
        title = r.read_string()
        about = r.read_string()
        geo_point = r.read_object() if flags & (1 << 2) else None
        address = r.read_string() if flags & (1 << 2) else None
        ttl_period = r.read_int() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.broadcast = broadcast
        self.megagroup = megagroup
        self.for_import = for_import
        self.forum = forum
        self.title = title
        self.about = about
        self.geo_point = geo_point
        self.address = address
        self.ttl_period = ttl_period
        return self


class EditAdmin(TLFunction["base.Updates"]):
    """The TL function channels.editAdmin#9a98ad68, answered with Updates."""

    __slots__ = ("channel", "user_id", "admin_rights", "rank",)

    ID = 0x9A98AD68
    QUALNAME = "functions.channels.EditAdmin"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        user_id: base.InputUser,
        admin_rights: base.ChatAdminRights,
        rank: str | None = None,
    ) -> None:
        self.channel = channel
        self.user_id = user_id
        self.admin_rights = admin_rights
        self.rank = rank

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.rank is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        self.user_id.write(w)
        self.admin_rights.write(w)
        if self.rank is not None:
            w.write_string(self.rank)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        channel = r.read_object()
        user_id = r.read_object()
        admin_rights = r.read_object()
        rank = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.channel = channel
        self.user_id = user_id
        self.admin_rights = admin_rights
        self.rank = rank
        return self


class EditTitle(TLFunction["base.Updates"]):
    """The TL function channels.editTitle#566decd0, answered with Updates."""

    __slots__ = ("channel", "title",)

    ID = 0x566DECD0
    QUALNAME = "functions.channels.EditTitle"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        title: str,
    ) -> None:
        self.channel = channel
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        title = r.read_string()
        self = cls.__new__(cls)
        self.channel = channel
        self.title = title
        return self


class EditPhoto(TLFunction["base.Updates"]):
    """The TL function channels.editPhoto#f12e57c9, answered with Updates."""

    __slots__ = ("channel", "photo",)

    ID = 0xF12E57C9
    QUALNAME = "functions.channels.EditPhoto"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        photo: base.InputChatPhoto,
    ) -> None:
        self.channel = channel
        self.photo = photo

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.photo.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        photo = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.photo = photo
        return self


class CheckUsername(TLFunction["bool"]):
    """The TL function channels.checkUsername#10e6bd2c, answered with Bool."""

    __slots__ = ("channel", "username",)

    ID = 0x10E6BD2C
    QUALNAME = "functions.channels.CheckUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        username: str,
    ) -> None:
        self.channel = channel
        self.username = username

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_string(self.username)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        username = r.read_string()
        self = cls.__new__(cls)
        self.channel = channel
        self.username = username
        return self


class UpdateUsername(TLFunction["bool"]):
    """The TL function channels.updateUsername#3514b3de, answered with Bool."""

    __slots__ = ("channel", "username",)

    ID = 0x3514B3DE
    QUALNAME = "functions.channels.UpdateUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        username: str,
    ) -> None:
        self.channel = channel
        self.username = username

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_string(self.username)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        username = r.read_string()
        self = cls.__new__(cls)
        self.channel = channel
        self.username = username
        return self


class JoinChannel(TLFunction["base.messages.ChatInviteJoinResult"]):
    """The TL function channels.joinChannel#7f6a1e22, answered with messages.ChatInviteJoinResult."""

    __slots__ = ("channel",)

    ID = 0x7F6A1E22
    QUALNAME = "functions.channels.JoinChannel"
    RESULT = "messages.ChatInviteJoinResult"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class LeaveChannel(TLFunction["base.Updates"]):
    """The TL function channels.leaveChannel#f836aa95, answered with Updates."""

    __slots__ = ("channel",)

    ID = 0xF836AA95
    QUALNAME = "functions.channels.LeaveChannel"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class InviteToChannel(TLFunction["base.messages.InvitedUsers"]):
    """The TL function channels.inviteToChannel#c9e33d54, answered with messages.InvitedUsers."""

    __slots__ = ("channel", "users",)

    ID = 0xC9E33D54
    QUALNAME = "functions.channels.InviteToChannel"
    RESULT = "messages.InvitedUsers"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        users: list[base.InputUser],
    ) -> None:
        self.channel = channel
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.channel = channel
        self.users = users
        return self


class DeleteChannel(TLFunction["base.Updates"]):
    """The TL function channels.deleteChannel#c0111fe3, answered with Updates."""

    __slots__ = ("channel",)

    ID = 0xC0111FE3
    QUALNAME = "functions.channels.DeleteChannel"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class ExportMessageLink(TLFunction["base.ExportedMessageLink"]):
    """The TL function channels.exportMessageLink#e63fadeb, answered with ExportedMessageLink."""

    __slots__ = ("grouped", "thread", "channel", "id",)

    ID = 0xE63FADEB
    QUALNAME = "functions.channels.ExportMessageLink"
    RESULT = "ExportedMessageLink"

    def __init__(
        self,
        *,
        grouped: bool = False,
        thread: bool = False,
        channel: base.InputChannel,
        id: int,
    ) -> None:
        self.grouped = grouped
        self.thread = thread
        self.channel = channel
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.grouped:
            flags |= 1 << 0
        if self.thread:
            flags |= 1 << 1
        w.write_int(flags)
        self.channel.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        grouped = bool(flags & (1 << 0))
        thread = bool(flags & (1 << 1))
        channel = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.grouped = grouped
        self.thread = thread
        self.channel = channel
        self.id = id
        return self


class ToggleSignatures(TLFunction["base.Updates"]):
    """The TL function channels.toggleSignatures#418d549c, answered with Updates."""

    __slots__ = ("signatures_enabled", "profiles_enabled", "channel",)

    ID = 0x418D549C
    QUALNAME = "functions.channels.ToggleSignatures"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        signatures_enabled: bool = False,
        profiles_enabled: bool = False,
        channel: base.InputChannel,
    ) -> None:
        self.signatures_enabled = signatures_enabled
        self.profiles_enabled = profiles_enabled
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.signatures_enabled:
            flags |= 1 << 0
        if self.profiles_enabled:
            flags |= 1 << 1
        w.write_int(flags)
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        signatures_enabled = bool(flags & (1 << 0))
        profiles_enabled = bool(flags & (1 << 1))
        channel = r.read_object()
        self = cls.__new__(cls)
        self.signatures_enabled = signatures_enabled
        self.profiles_enabled = profiles_enabled
        self.channel = channel
        return self


class GetAdminedPublicChannels(TLFunction["base.messages.Chats"]):
    """The TL function channels.getAdminedPublicChannels#f8b036af, answered with messages.Chats."""

    __slots__ = ("by_location", "check_limit", "for_personal", "for_community_peer",)

    ID = 0xF8B036AF
    QUALNAME = "functions.channels.GetAdminedPublicChannels"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        by_location: bool = False,
        check_limit: bool = False,
        for_personal: bool = False,
        for_community_peer: bool = False,
    ) -> None:
        self.by_location = by_location
        self.check_limit = check_limit
        self.for_personal = for_personal
        self.for_community_peer = for_community_peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.by_location:
            flags |= 1 << 0
        if self.check_limit:
            flags |= 1 << 1
        if self.for_personal:
            flags |= 1 << 2
        if self.for_community_peer:
            flags |= 1 << 3
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        by_location = bool(flags & (1 << 0))
        check_limit = bool(flags & (1 << 1))
        for_personal = bool(flags & (1 << 2))
        for_community_peer = bool(flags & (1 << 3))
        self = cls.__new__(cls)
        self.by_location = by_location
        self.check_limit = check_limit
        self.for_personal = for_personal
        self.for_community_peer = for_community_peer
        return self


class EditBanned(TLFunction["base.Updates"]):
    """The TL function channels.editBanned#96e6cd81, answered with Updates."""

    __slots__ = ("channel", "participant", "banned_rights",)

    ID = 0x96E6CD81
    QUALNAME = "functions.channels.EditBanned"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        participant: base.InputPeer,
        banned_rights: base.ChatBannedRights,
    ) -> None:
        self.channel = channel
        self.participant = participant
        self.banned_rights = banned_rights

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.participant.write(w)
        self.banned_rights.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        participant = r.read_object()
        banned_rights = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.participant = participant
        self.banned_rights = banned_rights
        return self


class GetAdminLog(TLFunction["base.channels.AdminLogResults"]):
    """The TL function channels.getAdminLog#33ddf480, answered with channels.AdminLogResults."""

    __slots__ = ("channel", "q", "events_filter", "admins", "max_id", "min_id", "limit",)

    ID = 0x33DDF480
    QUALNAME = "functions.channels.GetAdminLog"
    RESULT = "channels.AdminLogResults"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        q: str,
        events_filter: base.ChannelAdminLogEventsFilter | None = None,
        admins: list[base.InputUser] | None = None,
        max_id: int,
        min_id: int,
        limit: int,
    ) -> None:
        self.channel = channel
        self.q = q
        self.events_filter = events_filter
        self.admins = admins
        self.max_id = max_id
        self.min_id = min_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.events_filter is not None:
            flags |= 1 << 0
        if self.admins is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.channel.write(w)
        w.write_string(self.q)
        if self.events_filter is not None:
            self.events_filter.write(w)
        if self.admins is not None:
            w.write_vector(self.admins)
        w.write_long(self.max_id)
        w.write_long(self.min_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        channel = r.read_object()
        q = r.read_string()
        events_filter = r.read_object() if flags & (1 << 0) else None
        admins = r.read_vector() if flags & (1 << 1) else None
        max_id = r.read_long()
        min_id = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.q = q
        self.events_filter = events_filter
        self.admins = admins
        self.max_id = max_id
        self.min_id = min_id
        self.limit = limit
        return self


class SetStickers(TLFunction["bool"]):
    """The TL function channels.setStickers#ea8ca4f9, answered with Bool."""

    __slots__ = ("channel", "stickerset",)

    ID = 0xEA8CA4F9
    QUALNAME = "functions.channels.SetStickers"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        stickerset: base.InputStickerSet,
    ) -> None:
        self.channel = channel
        self.stickerset = stickerset

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.stickerset.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        stickerset = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.stickerset = stickerset
        return self


class ReadMessageContents(TLFunction["bool"]):
    """The TL function channels.readMessageContents#eab5dc38, answered with Bool."""

    __slots__ = ("channel", "id",)

    ID = 0xEAB5DC38
    QUALNAME = "functions.channels.ReadMessageContents"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        id: list[int],
    ) -> None:
        self.channel = channel
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.channel = channel
        self.id = id
        return self


class DeleteHistory(TLFunction["base.Updates"]):
    """The TL function channels.deleteHistory#9baa9647, answered with Updates."""

    __slots__ = ("for_everyone", "channel", "max_id",)

    ID = 0x9BAA9647
    QUALNAME = "functions.channels.DeleteHistory"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        for_everyone: bool = False,
        channel: base.InputChannel,
        max_id: int,
    ) -> None:
        self.for_everyone = for_everyone
        self.channel = channel
        self.max_id = max_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_everyone:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        w.write_int(self.max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_everyone = bool(flags & (1 << 0))
        channel = r.read_object()
        max_id = r.read_int()
        self = cls.__new__(cls)
        self.for_everyone = for_everyone
        self.channel = channel
        self.max_id = max_id
        return self


class TogglePreHistoryHidden(TLFunction["base.Updates"]):
    """The TL function channels.togglePreHistoryHidden#eabbb94c, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0xEABBB94C
    QUALNAME = "functions.channels.TogglePreHistoryHidden"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class GetLeftChannels(TLFunction["base.messages.Chats"]):
    """The TL function channels.getLeftChannels#8341ecc0, answered with messages.Chats."""

    __slots__ = ("offset",)

    ID = 0x8341ECC0
    QUALNAME = "functions.channels.GetLeftChannels"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        offset: int,
    ) -> None:
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offset = r.read_int()
        self = cls.__new__(cls)
        self.offset = offset
        return self


class GetGroupsForDiscussion(TLFunction["base.messages.Chats"]):
    """The TL function channels.getGroupsForDiscussion#f5dad378, answered with messages.Chats."""

    __slots__ = ()

    ID = 0xF5DAD378
    QUALNAME = "functions.channels.GetGroupsForDiscussion"
    RESULT = "messages.Chats"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetDiscussionGroup(TLFunction["bool"]):
    """The TL function channels.setDiscussionGroup#40582bb2, answered with Bool."""

    __slots__ = ("broadcast", "group",)

    ID = 0x40582BB2
    QUALNAME = "functions.channels.SetDiscussionGroup"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        broadcast: base.InputChannel,
        group: base.InputChannel,
    ) -> None:
        self.broadcast = broadcast
        self.group = group

    def write_body(self, w: TLWriter) -> None:
        self.broadcast.write(w)
        self.group.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        broadcast = r.read_object()
        group = r.read_object()
        self = cls.__new__(cls)
        self.broadcast = broadcast
        self.group = group
        return self


class EditLocation(TLFunction["bool"]):
    """The TL function channels.editLocation#58e63f6d, answered with Bool."""

    __slots__ = ("channel", "geo_point", "address",)

    ID = 0x58E63F6D
    QUALNAME = "functions.channels.EditLocation"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        geo_point: base.InputGeoPoint,
        address: str,
    ) -> None:
        self.channel = channel
        self.geo_point = geo_point
        self.address = address

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.geo_point.write(w)
        w.write_string(self.address)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        geo_point = r.read_object()
        address = r.read_string()
        self = cls.__new__(cls)
        self.channel = channel
        self.geo_point = geo_point
        self.address = address
        return self


class ToggleSlowMode(TLFunction["base.Updates"]):
    """The TL function channels.toggleSlowMode#edd49ef0, answered with Updates."""

    __slots__ = ("channel", "seconds",)

    ID = 0xEDD49EF0
    QUALNAME = "functions.channels.ToggleSlowMode"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        seconds: int,
    ) -> None:
        self.channel = channel
        self.seconds = seconds

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.seconds)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        seconds = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.seconds = seconds
        return self


class GetInactiveChannels(TLFunction["base.messages.InactiveChats"]):
    """The TL function channels.getInactiveChannels#11e831ee, answered with messages.InactiveChats."""

    __slots__ = ()

    ID = 0x11E831EE
    QUALNAME = "functions.channels.GetInactiveChannels"
    RESULT = "messages.InactiveChats"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ConvertToGigagroup(TLFunction["base.Updates"]):
    """The TL function channels.convertToGigagroup#0b290c69, answered with Updates."""

    __slots__ = ("channel",)

    ID = 0x0B290C69
    QUALNAME = "functions.channels.ConvertToGigagroup"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class GetSendAs(TLFunction["base.channels.SendAsPeers"]):
    """The TL function channels.getSendAs#e785a43f, answered with channels.SendAsPeers."""

    __slots__ = ("for_paid_reactions", "for_live_stories", "peer",)

    ID = 0xE785A43F
    QUALNAME = "functions.channels.GetSendAs"
    RESULT = "channels.SendAsPeers"

    def __init__(
        self,
        *,
        for_paid_reactions: bool = False,
        for_live_stories: bool = False,
        peer: base.InputPeer,
    ) -> None:
        self.for_paid_reactions = for_paid_reactions
        self.for_live_stories = for_live_stories
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_paid_reactions:
            flags |= 1 << 0
        if self.for_live_stories:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_paid_reactions = bool(flags & (1 << 0))
        for_live_stories = bool(flags & (1 << 1))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.for_paid_reactions = for_paid_reactions
        self.for_live_stories = for_live_stories
        self.peer = peer
        return self


class DeleteParticipantHistory(TLFunction["base.messages.AffectedHistory"]):
    """The TL function channels.deleteParticipantHistory#367544db, answered with messages.AffectedHistory."""

    __slots__ = ("channel", "participant",)

    ID = 0x367544DB
    QUALNAME = "functions.channels.DeleteParticipantHistory"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        participant: base.InputPeer,
    ) -> None:
        self.channel = channel
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.participant = participant
        return self


class ToggleJoinToSend(TLFunction["base.Updates"]):
    """The TL function channels.toggleJoinToSend#e4cb9580, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0xE4CB9580
    QUALNAME = "functions.channels.ToggleJoinToSend"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class ToggleJoinRequest(TLFunction["base.Updates"]):
    """The TL function channels.toggleJoinRequest#0ecc2618, answered with Updates."""

    __slots__ = ("apply_to_invites", "channel", "enabled", "guard_bot",)

    ID = 0x0ECC2618
    QUALNAME = "functions.channels.ToggleJoinRequest"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        apply_to_invites: bool = False,
        channel: base.InputChannel,
        enabled: bool,
        guard_bot: base.InputUser | None = None,
    ) -> None:
        self.apply_to_invites = apply_to_invites
        self.channel = channel
        self.enabled = enabled
        self.guard_bot = guard_bot

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.apply_to_invites:
            flags |= 1 << 1
        if self.guard_bot is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        w.write_bool(self.enabled)
        if self.guard_bot is not None:
            self.guard_bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        apply_to_invites = bool(flags & (1 << 1))
        channel = r.read_object()
        enabled = r.read_bool()
        guard_bot = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.apply_to_invites = apply_to_invites
        self.channel = channel
        self.enabled = enabled
        self.guard_bot = guard_bot
        return self


class ReorderUsernames(TLFunction["bool"]):
    """The TL function channels.reorderUsernames#b45ced1d, answered with Bool."""

    __slots__ = ("channel", "order",)

    ID = 0xB45CED1D
    QUALNAME = "functions.channels.ReorderUsernames"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        order: list[str],
    ) -> None:
        self.channel = channel
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_vector(self.order, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        order = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.channel = channel
        self.order = order
        return self


class ToggleUsername(TLFunction["bool"]):
    """The TL function channels.toggleUsername#50f24105, answered with Bool."""

    __slots__ = ("channel", "username", "active",)

    ID = 0x50F24105
    QUALNAME = "functions.channels.ToggleUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        username: str,
        active: bool,
    ) -> None:
        self.channel = channel
        self.username = username
        self.active = active

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_string(self.username)
        w.write_bool(self.active)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        username = r.read_string()
        active = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.username = username
        self.active = active
        return self


class DeactivateAllUsernames(TLFunction["bool"]):
    """The TL function channels.deactivateAllUsernames#0a245dd3, answered with Bool."""

    __slots__ = ("channel",)

    ID = 0x0A245DD3
    QUALNAME = "functions.channels.DeactivateAllUsernames"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class ToggleForum(TLFunction["base.Updates"]):
    """The TL function channels.toggleForum#3ff75734, answered with Updates."""

    __slots__ = ("channel", "enabled", "tabs",)

    ID = 0x3FF75734
    QUALNAME = "functions.channels.ToggleForum"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
        tabs: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled
        self.tabs = tabs

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)
        w.write_bool(self.tabs)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        tabs = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        self.tabs = tabs
        return self


class ToggleAntiSpam(TLFunction["base.Updates"]):
    """The TL function channels.toggleAntiSpam#68f3e4eb, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0x68F3E4EB
    QUALNAME = "functions.channels.ToggleAntiSpam"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class ReportAntiSpamFalsePositive(TLFunction["bool"]):
    """The TL function channels.reportAntiSpamFalsePositive#a850a693, answered with Bool."""

    __slots__ = ("channel", "msg_id",)

    ID = 0xA850A693
    QUALNAME = "functions.channels.ReportAntiSpamFalsePositive"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        msg_id: int,
    ) -> None:
        self.channel = channel
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.msg_id = msg_id
        return self


class ToggleParticipantsHidden(TLFunction["base.Updates"]):
    """The TL function channels.toggleParticipantsHidden#6a6e7854, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0x6A6E7854
    QUALNAME = "functions.channels.ToggleParticipantsHidden"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class UpdateColor(TLFunction["base.Updates"]):
    """The TL function channels.updateColor#d8aa3671, answered with Updates."""

    __slots__ = ("for_profile", "channel", "color", "background_emoji_id",)

    ID = 0xD8AA3671
    QUALNAME = "functions.channels.UpdateColor"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        for_profile: bool = False,
        channel: base.InputChannel,
        color: int | None = None,
        background_emoji_id: int | None = None,
    ) -> None:
        self.for_profile = for_profile
        self.channel = channel
        self.color = color
        self.background_emoji_id = background_emoji_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_profile:
            flags |= 1 << 1
        if self.color is not None:
            flags |= 1 << 2
        if self.background_emoji_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        if self.color is not None:
            w.write_int(self.color)
        if self.background_emoji_id is not None:
            w.write_long(self.background_emoji_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_profile = bool(flags & (1 << 1))
        channel = r.read_object()
        color = r.read_int() if flags & (1 << 2) else None
        background_emoji_id = r.read_long() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.for_profile = for_profile
        self.channel = channel
        self.color = color
        self.background_emoji_id = background_emoji_id
        return self


class ToggleViewForumAsMessages(TLFunction["base.Updates"]):
    """The TL function channels.toggleViewForumAsMessages#9738bb15, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0x9738BB15
    QUALNAME = "functions.channels.ToggleViewForumAsMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class GetChannelRecommendations(TLFunction["base.messages.Chats"]):
    """The TL function channels.getChannelRecommendations#25a71742, answered with messages.Chats."""

    __slots__ = ("channel",)

    ID = 0x25A71742
    QUALNAME = "functions.channels.GetChannelRecommendations"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        channel: base.InputChannel | None = None,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.channel is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.channel is not None:
            self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        channel = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.channel = channel
        return self


class UpdateEmojiStatus(TLFunction["base.Updates"]):
    """The TL function channels.updateEmojiStatus#f0d3e6a8, answered with Updates."""

    __slots__ = ("channel", "emoji_status",)

    ID = 0xF0D3E6A8
    QUALNAME = "functions.channels.UpdateEmojiStatus"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        emoji_status: base.EmojiStatus,
    ) -> None:
        self.channel = channel
        self.emoji_status = emoji_status

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.emoji_status.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        emoji_status = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.emoji_status = emoji_status
        return self


class SetBoostsToUnblockRestrictions(TLFunction["base.Updates"]):
    """The TL function channels.setBoostsToUnblockRestrictions#ad399cee, answered with Updates."""

    __slots__ = ("channel", "boosts",)

    ID = 0xAD399CEE
    QUALNAME = "functions.channels.SetBoostsToUnblockRestrictions"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        boosts: int,
    ) -> None:
        self.channel = channel
        self.boosts = boosts

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.boosts)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        boosts = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.boosts = boosts
        return self


class SetEmojiStickers(TLFunction["bool"]):
    """The TL function channels.setEmojiStickers#3cd930b7, answered with Bool."""

    __slots__ = ("channel", "stickerset",)

    ID = 0x3CD930B7
    QUALNAME = "functions.channels.SetEmojiStickers"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        stickerset: base.InputStickerSet,
    ) -> None:
        self.channel = channel
        self.stickerset = stickerset

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.stickerset.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        stickerset = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.stickerset = stickerset
        return self


class RestrictSponsoredMessages(TLFunction["base.Updates"]):
    """The TL function channels.restrictSponsoredMessages#9ae91519, answered with Updates."""

    __slots__ = ("channel", "restricted",)

    ID = 0x9AE91519
    QUALNAME = "functions.channels.RestrictSponsoredMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        restricted: bool,
    ) -> None:
        self.channel = channel
        self.restricted = restricted

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.restricted)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        restricted = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.restricted = restricted
        return self


class SearchPosts(TLFunction["base.messages.Messages"]):
    """The TL function channels.searchPosts#f2c4f24d, answered with messages.Messages."""

    __slots__ = ("hashtag", "query", "offset_rate", "offset_peer", "offset_id", "limit", "allow_paid_stars",)

    ID = 0xF2C4F24D
    QUALNAME = "functions.channels.SearchPosts"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        hashtag: str | None = None,
        query: str | None = None,
        offset_rate: int,
        offset_peer: base.InputPeer,
        offset_id: int,
        limit: int,
        allow_paid_stars: int | None = None,
    ) -> None:
        self.hashtag = hashtag
        self.query = query
        self.offset_rate = offset_rate
        self.offset_peer = offset_peer
        self.offset_id = offset_id
        self.limit = limit
        self.allow_paid_stars = allow_paid_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.hashtag is not None:
            flags |= 1 << 0
        if self.query is not None:
            flags |= 1 << 1
        if self.allow_paid_stars is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.hashtag is not None:
            w.write_string(self.hashtag)
        if self.query is not None:
            w.write_string(self.query)
        w.write_int(self.offset_rate)
        self.offset_peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.limit)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hashtag = r.read_string() if flags & (1 << 0) else None
        query = r.read_string() if flags & (1 << 1) else None
        offset_rate = r.read_int()
        offset_peer = r.read_object()
        offset_id = r.read_int()
        limit = r.read_int()
        allow_paid_stars = r.read_long() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.hashtag = hashtag
        self.query = query
        self.offset_rate = offset_rate
        self.offset_peer = offset_peer
        self.offset_id = offset_id
        self.limit = limit
        self.allow_paid_stars = allow_paid_stars
        return self


class UpdatePaidMessagesPrice(TLFunction["base.Updates"]):
    """The TL function channels.updatePaidMessagesPrice#4b12327b, answered with Updates."""

    __slots__ = ("broadcast_messages_allowed", "channel", "send_paid_messages_stars",)

    ID = 0x4B12327B
    QUALNAME = "functions.channels.UpdatePaidMessagesPrice"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        broadcast_messages_allowed: bool = False,
        channel: base.InputChannel,
        send_paid_messages_stars: int,
    ) -> None:
        self.broadcast_messages_allowed = broadcast_messages_allowed
        self.channel = channel
        self.send_paid_messages_stars = send_paid_messages_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.broadcast_messages_allowed:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        w.write_long(self.send_paid_messages_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        broadcast_messages_allowed = bool(flags & (1 << 0))
        channel = r.read_object()
        send_paid_messages_stars = r.read_long()
        self = cls.__new__(cls)
        self.broadcast_messages_allowed = broadcast_messages_allowed
        self.channel = channel
        self.send_paid_messages_stars = send_paid_messages_stars
        return self


class ToggleAutotranslation(TLFunction["base.Updates"]):
    """The TL function channels.toggleAutotranslation#167fc0a1, answered with Updates."""

    __slots__ = ("channel", "enabled",)

    ID = 0x167FC0A1
    QUALNAME = "functions.channels.ToggleAutotranslation"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        enabled: bool,
    ) -> None:
        self.channel = channel
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.channel = channel
        self.enabled = enabled
        return self


class GetMessageAuthor(TLFunction["base.User"]):
    """The TL function channels.getMessageAuthor#ece2a0e6, answered with User."""

    __slots__ = ("channel", "id",)

    ID = 0xECE2A0E6
    QUALNAME = "functions.channels.GetMessageAuthor"
    RESULT = "User"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        id: int,
    ) -> None:
        self.channel = channel
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.id = id
        return self


class CheckSearchPostsFlood(TLFunction["base.SearchPostsFlood"]):
    """The TL function channels.checkSearchPostsFlood#22567115, answered with SearchPostsFlood."""

    __slots__ = ("query",)

    ID = 0x22567115
    QUALNAME = "functions.channels.CheckSearchPostsFlood"
    RESULT = "SearchPostsFlood"

    def __init__(
        self,
        *,
        query: str | None = None,
    ) -> None:
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.query is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.query is not None:
            w.write_string(self.query)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        query = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.query = query
        return self


class SetMainProfileTab(TLFunction["bool"]):
    """The TL function channels.setMainProfileTab#3583fcb1, answered with Bool."""

    __slots__ = ("channel", "tab",)

    ID = 0x3583FCB1
    QUALNAME = "functions.channels.SetMainProfileTab"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        tab: base.ProfileTab,
    ) -> None:
        self.channel = channel
        self.tab = tab

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        self.tab.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        tab = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        self.tab = tab
        return self
