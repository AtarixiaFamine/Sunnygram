# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the phone namespace.

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


class GetCallConfig(TLFunction["base.DataJSON"]):
    """The TL function phone.getCallConfig#55451fa9, answered with DataJSON."""

    __slots__ = ()

    ID = 0x55451FA9
    QUALNAME = "functions.phone.GetCallConfig"
    RESULT = "DataJSON"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RequestCall(TLFunction["base.phone.PhoneCall"]):
    """The TL function phone.requestCall#42ff96ed, answered with phone.PhoneCall."""

    __slots__ = ("video", "user_id", "random_id", "g_a_hash", "protocol",)

    ID = 0x42FF96ED
    QUALNAME = "functions.phone.RequestCall"
    RESULT = "phone.PhoneCall"

    def __init__(
        self,
        *,
        video: bool = False,
        user_id: base.InputUser,
        random_id: int,
        g_a_hash: bytes,
        protocol: base.PhoneCallProtocol,
    ) -> None:
        self.video = video
        self.user_id = user_id
        self.random_id = random_id
        self.g_a_hash = g_a_hash
        self.protocol = protocol

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.video:
            flags |= 1 << 0
        w.write_int(flags)
        self.user_id.write(w)
        w.write_int(self.random_id)
        w.write_bytes(self.g_a_hash)
        self.protocol.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        video = bool(flags & (1 << 0))
        user_id = r.read_object()
        random_id = r.read_int()
        g_a_hash = r.read_bytes()
        protocol = r.read_object()
        self = cls.__new__(cls)
        self.video = video
        self.user_id = user_id
        self.random_id = random_id
        self.g_a_hash = g_a_hash
        self.protocol = protocol
        return self


class AcceptCall(TLFunction["base.phone.PhoneCall"]):
    """The TL function phone.acceptCall#3bd2b4a0, answered with phone.PhoneCall."""

    __slots__ = ("peer", "g_b", "protocol",)

    ID = 0x3BD2B4A0
    QUALNAME = "functions.phone.AcceptCall"
    RESULT = "phone.PhoneCall"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
        g_b: bytes,
        protocol: base.PhoneCallProtocol,
    ) -> None:
        self.peer = peer
        self.g_b = g_b
        self.protocol = protocol

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bytes(self.g_b)
        self.protocol.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        g_b = r.read_bytes()
        protocol = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.g_b = g_b
        self.protocol = protocol
        return self


class ConfirmCall(TLFunction["base.phone.PhoneCall"]):
    """The TL function phone.confirmCall#2efe1722, answered with phone.PhoneCall."""

    __slots__ = ("peer", "g_a", "key_fingerprint", "protocol",)

    ID = 0x2EFE1722
    QUALNAME = "functions.phone.ConfirmCall"
    RESULT = "phone.PhoneCall"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
        g_a: bytes,
        key_fingerprint: int,
        protocol: base.PhoneCallProtocol,
    ) -> None:
        self.peer = peer
        self.g_a = g_a
        self.key_fingerprint = key_fingerprint
        self.protocol = protocol

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bytes(self.g_a)
        w.write_long(self.key_fingerprint)
        self.protocol.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        g_a = r.read_bytes()
        key_fingerprint = r.read_long()
        protocol = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.g_a = g_a
        self.key_fingerprint = key_fingerprint
        self.protocol = protocol
        return self


class ReceivedCall(TLFunction["bool"]):
    """The TL function phone.receivedCall#17d54f61, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0x17D54F61
    QUALNAME = "functions.phone.ReceivedCall"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class DiscardCall(TLFunction["base.Updates"]):
    """The TL function phone.discardCall#b2cbc1c0, answered with Updates."""

    __slots__ = ("video", "peer", "duration", "reason", "connection_id",)

    ID = 0xB2CBC1C0
    QUALNAME = "functions.phone.DiscardCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        video: bool = False,
        peer: base.InputPhoneCall,
        duration: int,
        reason: base.PhoneCallDiscardReason,
        connection_id: int,
    ) -> None:
        self.video = video
        self.peer = peer
        self.duration = duration
        self.reason = reason
        self.connection_id = connection_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.video:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.duration)
        self.reason.write(w)
        w.write_long(self.connection_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        video = bool(flags & (1 << 0))
        peer = r.read_object()
        duration = r.read_int()
        reason = r.read_object()
        connection_id = r.read_long()
        self = cls.__new__(cls)
        self.video = video
        self.peer = peer
        self.duration = duration
        self.reason = reason
        self.connection_id = connection_id
        return self


class SetCallRating(TLFunction["base.Updates"]):
    """The TL function phone.setCallRating#59ead627, answered with Updates."""

    __slots__ = ("user_initiative", "peer", "rating", "comment",)

    ID = 0x59EAD627
    QUALNAME = "functions.phone.SetCallRating"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        user_initiative: bool = False,
        peer: base.InputPhoneCall,
        rating: int,
        comment: str,
    ) -> None:
        self.user_initiative = user_initiative
        self.peer = peer
        self.rating = rating
        self.comment = comment

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.user_initiative:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.rating)
        w.write_string(self.comment)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        user_initiative = bool(flags & (1 << 0))
        peer = r.read_object()
        rating = r.read_int()
        comment = r.read_string()
        self = cls.__new__(cls)
        self.user_initiative = user_initiative
        self.peer = peer
        self.rating = rating
        self.comment = comment
        return self


class SaveCallDebug(TLFunction["bool"]):
    """The TL function phone.saveCallDebug#277add7e, answered with Bool."""

    __slots__ = ("peer", "debug",)

    ID = 0x277ADD7E
    QUALNAME = "functions.phone.SaveCallDebug"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
        debug: base.DataJSON,
    ) -> None:
        self.peer = peer
        self.debug = debug

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.debug.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        debug = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.debug = debug
        return self


class SendSignalingData(TLFunction["bool"]):
    """The TL function phone.sendSignalingData#ff7a9383, answered with Bool."""

    __slots__ = ("peer", "data",)

    ID = 0xFF7A9383
    QUALNAME = "functions.phone.SendSignalingData"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
        data: bytes,
    ) -> None:
        self.peer = peer
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bytes(self.data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        data = r.read_bytes()
        self = cls.__new__(cls)
        self.peer = peer
        self.data = data
        return self


class CreateGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.createGroupCall#48cdc6d8, answered with Updates."""

    __slots__ = ("rtmp_stream", "peer", "random_id", "title", "schedule_date",)

    ID = 0x48CDC6D8
    QUALNAME = "functions.phone.CreateGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        rtmp_stream: bool = False,
        peer: base.InputPeer,
        random_id: int,
        title: str | None = None,
        schedule_date: int | None = None,
    ) -> None:
        self.rtmp_stream = rtmp_stream
        self.peer = peer
        self.random_id = random_id
        self.title = title
        self.schedule_date = schedule_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.rtmp_stream:
            flags |= 1 << 2
        if self.title is not None:
            flags |= 1 << 0
        if self.schedule_date is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.random_id)
        if self.title is not None:
            w.write_string(self.title)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        rtmp_stream = bool(flags & (1 << 2))
        peer = r.read_object()
        random_id = r.read_int()
        title = r.read_string() if flags & (1 << 0) else None
        schedule_date = r.read_int() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.rtmp_stream = rtmp_stream
        self.peer = peer
        self.random_id = random_id
        self.title = title
        self.schedule_date = schedule_date
        return self


class JoinGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.joinGroupCall#8fb53057, answered with Updates."""

    __slots__ = ("muted", "video_stopped", "call", "join_as", "invite_hash", "public_key", "block", "params",)

    ID = 0x8FB53057
    QUALNAME = "functions.phone.JoinGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        muted: bool = False,
        video_stopped: bool = False,
        call: base.InputGroupCall,
        join_as: base.InputPeer,
        invite_hash: str | None = None,
        public_key: int | None = None,
        block: bytes | None = None,
        params: base.DataJSON,
    ) -> None:
        self.muted = muted
        self.video_stopped = video_stopped
        self.call = call
        self.join_as = join_as
        self.invite_hash = invite_hash
        self.public_key = public_key
        self.block = block
        self.params = params

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.muted:
            flags |= 1 << 0
        if self.video_stopped:
            flags |= 1 << 2
        if self.invite_hash is not None:
            flags |= 1 << 1
        if self.public_key is not None:
            flags |= 1 << 3
        if self.block is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.call.write(w)
        self.join_as.write(w)
        if self.invite_hash is not None:
            w.write_string(self.invite_hash)
        if self.public_key is not None:
            w.write_int256(self.public_key)
        if self.block is not None:
            w.write_bytes(self.block)
        self.params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        muted = bool(flags & (1 << 0))
        video_stopped = bool(flags & (1 << 2))
        call = r.read_object()
        join_as = r.read_object()
        invite_hash = r.read_string() if flags & (1 << 1) else None
        public_key = r.read_int256() if flags & (1 << 3) else None
        block = r.read_bytes() if flags & (1 << 3) else None
        params = r.read_object()
        self = cls.__new__(cls)
        self.muted = muted
        self.video_stopped = video_stopped
        self.call = call
        self.join_as = join_as
        self.invite_hash = invite_hash
        self.public_key = public_key
        self.block = block
        self.params = params
        return self


class LeaveGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.leaveGroupCall#500377f9, answered with Updates."""

    __slots__ = ("call", "source",)

    ID = 0x500377F9
    QUALNAME = "functions.phone.LeaveGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        source: int,
    ) -> None:
        self.call = call
        self.source = source

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_int(self.source)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        source = r.read_int()
        self = cls.__new__(cls)
        self.call = call
        self.source = source
        return self


class InviteToGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.inviteToGroupCall#7b393160, answered with Updates."""

    __slots__ = ("call", "users",)

    ID = 0x7B393160
    QUALNAME = "functions.phone.InviteToGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        users: list[base.InputUser],
    ) -> None:
        self.call = call
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.call = call
        self.users = users
        return self


class DiscardGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.discardGroupCall#7a777135, answered with Updates."""

    __slots__ = ("call",)

    ID = 0x7A777135
    QUALNAME = "functions.phone.DiscardGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
    ) -> None:
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        return self


class ToggleGroupCallSettings(TLFunction["base.Updates"]):
    """The TL function phone.toggleGroupCallSettings#974392f2, answered with Updates."""

    __slots__ = ("reset_invite_hash", "call", "join_muted", "messages_enabled", "send_paid_messages_stars",)

    ID = 0x974392F2
    QUALNAME = "functions.phone.ToggleGroupCallSettings"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        reset_invite_hash: bool = False,
        call: base.InputGroupCall,
        join_muted: bool | None = None,
        messages_enabled: bool | None = None,
        send_paid_messages_stars: int | None = None,
    ) -> None:
        self.reset_invite_hash = reset_invite_hash
        self.call = call
        self.join_muted = join_muted
        self.messages_enabled = messages_enabled
        self.send_paid_messages_stars = send_paid_messages_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reset_invite_hash:
            flags |= 1 << 1
        if self.join_muted is not None:
            flags |= 1 << 0
        if self.messages_enabled is not None:
            flags |= 1 << 2
        if self.send_paid_messages_stars is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.call.write(w)
        if self.join_muted is not None:
            w.write_bool(self.join_muted)
        if self.messages_enabled is not None:
            w.write_bool(self.messages_enabled)
        if self.send_paid_messages_stars is not None:
            w.write_long(self.send_paid_messages_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reset_invite_hash = bool(flags & (1 << 1))
        call = r.read_object()
        join_muted = r.read_bool() if flags & (1 << 0) else None
        messages_enabled = r.read_bool() if flags & (1 << 2) else None
        send_paid_messages_stars = r.read_long() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.reset_invite_hash = reset_invite_hash
        self.call = call
        self.join_muted = join_muted
        self.messages_enabled = messages_enabled
        self.send_paid_messages_stars = send_paid_messages_stars
        return self


class GetGroupCall(TLFunction["base.phone.GroupCall"]):
    """The TL function phone.getGroupCall#041845db, answered with phone.GroupCall."""

    __slots__ = ("call", "limit",)

    ID = 0x041845DB
    QUALNAME = "functions.phone.GetGroupCall"
    RESULT = "phone.GroupCall"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        limit: int,
    ) -> None:
        self.call = call
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.call = call
        self.limit = limit
        return self


class GetGroupParticipants(TLFunction["base.phone.GroupParticipants"]):
    """The TL function phone.getGroupParticipants#c558d8ab, answered with phone.GroupParticipants."""

    __slots__ = ("call", "ids", "sources", "offset", "limit",)

    ID = 0xC558D8AB
    QUALNAME = "functions.phone.GetGroupParticipants"
    RESULT = "phone.GroupParticipants"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        ids: list[base.InputPeer],
        sources: list[int],
        offset: str,
        limit: int,
    ) -> None:
        self.call = call
        self.ids = ids
        self.sources = sources
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_vector(self.ids)
        w.write_vector(self.sources, TLWriter.write_int)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        ids = r.read_vector()
        sources = r.read_vector(TLReader.read_int)
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.call = call
        self.ids = ids
        self.sources = sources
        self.offset = offset
        self.limit = limit
        return self


class CheckGroupCall(TLFunction["list[int]"]):
    """The TL function phone.checkGroupCall#b59cf977, answered with Vector<int>."""

    __slots__ = ("call", "sources",)

    ID = 0xB59CF977
    QUALNAME = "functions.phone.CheckGroupCall"
    RESULT = "Vector<int>"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        sources: list[int],
    ) -> None:
        self.call = call
        self.sources = sources

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_vector(self.sources, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        sources = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.call = call
        self.sources = sources
        return self


class ToggleGroupCallRecord(TLFunction["base.Updates"]):
    """The TL function phone.toggleGroupCallRecord#f128c708, answered with Updates."""

    __slots__ = ("start", "video", "call", "title", "video_portrait",)

    ID = 0xF128C708
    QUALNAME = "functions.phone.ToggleGroupCallRecord"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        start: bool = False,
        video: bool = False,
        call: base.InputGroupCall,
        title: str | None = None,
        video_portrait: bool | None = None,
    ) -> None:
        self.start = start
        self.video = video
        self.call = call
        self.title = title
        self.video_portrait = video_portrait

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.start:
            flags |= 1 << 0
        if self.video:
            flags |= 1 << 2
        if self.title is not None:
            flags |= 1 << 1
        if self.video_portrait is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.call.write(w)
        if self.title is not None:
            w.write_string(self.title)
        if self.video_portrait is not None:
            w.write_bool(self.video_portrait)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        start = bool(flags & (1 << 0))
        video = bool(flags & (1 << 2))
        call = r.read_object()
        title = r.read_string() if flags & (1 << 1) else None
        video_portrait = r.read_bool() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.start = start
        self.video = video
        self.call = call
        self.title = title
        self.video_portrait = video_portrait
        return self


class EditGroupCallParticipant(TLFunction["base.Updates"]):
    """The TL function phone.editGroupCallParticipant#a5273abf, answered with Updates."""

    __slots__ = ("call", "participant", "muted", "volume", "raise_hand", "video_stopped", "video_paused", "presentation_paused",)

    ID = 0xA5273ABF
    QUALNAME = "functions.phone.EditGroupCallParticipant"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        participant: base.InputPeer,
        muted: bool | None = None,
        volume: int | None = None,
        raise_hand: bool | None = None,
        video_stopped: bool | None = None,
        video_paused: bool | None = None,
        presentation_paused: bool | None = None,
    ) -> None:
        self.call = call
        self.participant = participant
        self.muted = muted
        self.volume = volume
        self.raise_hand = raise_hand
        self.video_stopped = video_stopped
        self.video_paused = video_paused
        self.presentation_paused = presentation_paused

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.muted is not None:
            flags |= 1 << 0
        if self.volume is not None:
            flags |= 1 << 1
        if self.raise_hand is not None:
            flags |= 1 << 2
        if self.video_stopped is not None:
            flags |= 1 << 3
        if self.video_paused is not None:
            flags |= 1 << 4
        if self.presentation_paused is not None:
            flags |= 1 << 5
        w.write_int(flags)
        self.call.write(w)
        self.participant.write(w)
        if self.muted is not None:
            w.write_bool(self.muted)
        if self.volume is not None:
            w.write_int(self.volume)
        if self.raise_hand is not None:
            w.write_bool(self.raise_hand)
        if self.video_stopped is not None:
            w.write_bool(self.video_stopped)
        if self.video_paused is not None:
            w.write_bool(self.video_paused)
        if self.presentation_paused is not None:
            w.write_bool(self.presentation_paused)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        call = r.read_object()
        participant = r.read_object()
        muted = r.read_bool() if flags & (1 << 0) else None
        volume = r.read_int() if flags & (1 << 1) else None
        raise_hand = r.read_bool() if flags & (1 << 2) else None
        video_stopped = r.read_bool() if flags & (1 << 3) else None
        video_paused = r.read_bool() if flags & (1 << 4) else None
        presentation_paused = r.read_bool() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.call = call
        self.participant = participant
        self.muted = muted
        self.volume = volume
        self.raise_hand = raise_hand
        self.video_stopped = video_stopped
        self.video_paused = video_paused
        self.presentation_paused = presentation_paused
        return self


class EditGroupCallTitle(TLFunction["base.Updates"]):
    """The TL function phone.editGroupCallTitle#1ca6ac0a, answered with Updates."""

    __slots__ = ("call", "title",)

    ID = 0x1CA6AC0A
    QUALNAME = "functions.phone.EditGroupCallTitle"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        title: str,
    ) -> None:
        self.call = call
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        title = r.read_string()
        self = cls.__new__(cls)
        self.call = call
        self.title = title
        return self


class GetGroupCallJoinAs(TLFunction["base.phone.JoinAsPeers"]):
    """The TL function phone.getGroupCallJoinAs#ef7c213a, answered with phone.JoinAsPeers."""

    __slots__ = ("peer",)

    ID = 0xEF7C213A
    QUALNAME = "functions.phone.GetGroupCallJoinAs"
    RESULT = "phone.JoinAsPeers"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class ExportGroupCallInvite(TLFunction["base.phone.ExportedGroupCallInvite"]):
    """The TL function phone.exportGroupCallInvite#e6aa647f, answered with phone.ExportedGroupCallInvite."""

    __slots__ = ("can_self_unmute", "call",)

    ID = 0xE6AA647F
    QUALNAME = "functions.phone.ExportGroupCallInvite"
    RESULT = "phone.ExportedGroupCallInvite"

    def __init__(
        self,
        *,
        can_self_unmute: bool = False,
        call: base.InputGroupCall,
    ) -> None:
        self.can_self_unmute = can_self_unmute
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.can_self_unmute:
            flags |= 1 << 0
        w.write_int(flags)
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        can_self_unmute = bool(flags & (1 << 0))
        call = r.read_object()
        self = cls.__new__(cls)
        self.can_self_unmute = can_self_unmute
        self.call = call
        return self


class ToggleGroupCallStartSubscription(TLFunction["base.Updates"]):
    """The TL function phone.toggleGroupCallStartSubscription#219c34e6, answered with Updates."""

    __slots__ = ("call", "subscribed",)

    ID = 0x219C34E6
    QUALNAME = "functions.phone.ToggleGroupCallStartSubscription"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        subscribed: bool,
    ) -> None:
        self.call = call
        self.subscribed = subscribed

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_bool(self.subscribed)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        subscribed = r.read_bool()
        self = cls.__new__(cls)
        self.call = call
        self.subscribed = subscribed
        return self


class StartScheduledGroupCall(TLFunction["base.Updates"]):
    """The TL function phone.startScheduledGroupCall#5680e342, answered with Updates."""

    __slots__ = ("call",)

    ID = 0x5680E342
    QUALNAME = "functions.phone.StartScheduledGroupCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
    ) -> None:
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        return self


class SaveDefaultGroupCallJoinAs(TLFunction["bool"]):
    """The TL function phone.saveDefaultGroupCallJoinAs#575e1f8c, answered with Bool."""

    __slots__ = ("peer", "join_as",)

    ID = 0x575E1F8C
    QUALNAME = "functions.phone.SaveDefaultGroupCallJoinAs"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        join_as: base.InputPeer,
    ) -> None:
        self.peer = peer
        self.join_as = join_as

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.join_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        join_as = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.join_as = join_as
        return self


class JoinGroupCallPresentation(TLFunction["base.Updates"]):
    """The TL function phone.joinGroupCallPresentation#cbea6bc4, answered with Updates."""

    __slots__ = ("call", "params",)

    ID = 0xCBEA6BC4
    QUALNAME = "functions.phone.JoinGroupCallPresentation"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        params: base.DataJSON,
    ) -> None:
        self.call = call
        self.params = params

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        self.params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        params = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        self.params = params
        return self


class LeaveGroupCallPresentation(TLFunction["base.Updates"]):
    """The TL function phone.leaveGroupCallPresentation#1c50d144, answered with Updates."""

    __slots__ = ("call",)

    ID = 0x1C50D144
    QUALNAME = "functions.phone.LeaveGroupCallPresentation"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
    ) -> None:
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        return self


class GetGroupCallStreamChannels(TLFunction["base.phone.GroupCallStreamChannels"]):
    """The TL function phone.getGroupCallStreamChannels#1ab21940, answered with phone.GroupCallStreamChannels."""

    __slots__ = ("call",)

    ID = 0x1AB21940
    QUALNAME = "functions.phone.GetGroupCallStreamChannels"
    RESULT = "phone.GroupCallStreamChannels"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
    ) -> None:
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        return self


class GetGroupCallStreamRtmpUrl(TLFunction["base.phone.GroupCallStreamRtmpUrl"]):
    """The TL function phone.getGroupCallStreamRtmpUrl#5af4c73a, answered with phone.GroupCallStreamRtmpUrl."""

    __slots__ = ("live_story", "peer", "revoke",)

    ID = 0x5AF4C73A
    QUALNAME = "functions.phone.GetGroupCallStreamRtmpUrl"
    RESULT = "phone.GroupCallStreamRtmpUrl"

    def __init__(
        self,
        *,
        live_story: bool = False,
        peer: base.InputPeer,
        revoke: bool,
    ) -> None:
        self.live_story = live_story
        self.peer = peer
        self.revoke = revoke

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.live_story:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_bool(self.revoke)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        live_story = bool(flags & (1 << 0))
        peer = r.read_object()
        revoke = r.read_bool()
        self = cls.__new__(cls)
        self.live_story = live_story
        self.peer = peer
        self.revoke = revoke
        return self


class SaveCallLog(TLFunction["bool"]):
    """The TL function phone.saveCallLog#41248786, answered with Bool."""

    __slots__ = ("peer", "file",)

    ID = 0x41248786
    QUALNAME = "functions.phone.SaveCallLog"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPhoneCall,
        file: base.InputFile,
    ) -> None:
        self.peer = peer
        self.file = file

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.file.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        file = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.file = file
        return self


class CreateConferenceCall(TLFunction["base.Updates"]):
    """The TL function phone.createConferenceCall#7d0444bb, answered with Updates."""

    __slots__ = ("muted", "video_stopped", "join", "random_id", "public_key", "block", "params",)

    ID = 0x7D0444BB
    QUALNAME = "functions.phone.CreateConferenceCall"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        muted: bool = False,
        video_stopped: bool = False,
        join: bool = False,
        random_id: int,
        public_key: int | None = None,
        block: bytes | None = None,
        params: base.DataJSON | None = None,
    ) -> None:
        self.muted = muted
        self.video_stopped = video_stopped
        self.join = join
        self.random_id = random_id
        self.public_key = public_key
        self.block = block
        self.params = params

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.muted:
            flags |= 1 << 0
        if self.video_stopped:
            flags |= 1 << 2
        if self.join:
            flags |= 1 << 3
        if self.public_key is not None:
            flags |= 1 << 3
        if self.block is not None:
            flags |= 1 << 3
        if self.params is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_int(self.random_id)
        if self.public_key is not None:
            w.write_int256(self.public_key)
        if self.block is not None:
            w.write_bytes(self.block)
        if self.params is not None:
            self.params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        muted = bool(flags & (1 << 0))
        video_stopped = bool(flags & (1 << 2))
        join = bool(flags & (1 << 3))
        random_id = r.read_int()
        public_key = r.read_int256() if flags & (1 << 3) else None
        block = r.read_bytes() if flags & (1 << 3) else None
        params = r.read_object() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.muted = muted
        self.video_stopped = video_stopped
        self.join = join
        self.random_id = random_id
        self.public_key = public_key
        self.block = block
        self.params = params
        return self


class DeleteConferenceCallParticipants(TLFunction["base.Updates"]):
    """The TL function phone.deleteConferenceCallParticipants#8ca60525, answered with Updates."""

    __slots__ = ("only_left", "kick", "call", "ids", "block",)

    ID = 0x8CA60525
    QUALNAME = "functions.phone.DeleteConferenceCallParticipants"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        only_left: bool = False,
        kick: bool = False,
        call: base.InputGroupCall,
        ids: list[int],
        block: bytes,
    ) -> None:
        self.only_left = only_left
        self.kick = kick
        self.call = call
        self.ids = ids
        self.block = block

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.only_left:
            flags |= 1 << 0
        if self.kick:
            flags |= 1 << 1
        w.write_int(flags)
        self.call.write(w)
        w.write_vector(self.ids, TLWriter.write_long)
        w.write_bytes(self.block)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        only_left = bool(flags & (1 << 0))
        kick = bool(flags & (1 << 1))
        call = r.read_object()
        ids = r.read_vector(TLReader.read_long)
        block = r.read_bytes()
        self = cls.__new__(cls)
        self.only_left = only_left
        self.kick = kick
        self.call = call
        self.ids = ids
        self.block = block
        return self


class SendConferenceCallBroadcast(TLFunction["base.Updates"]):
    """The TL function phone.sendConferenceCallBroadcast#c6701900, answered with Updates."""

    __slots__ = ("call", "block",)

    ID = 0xC6701900
    QUALNAME = "functions.phone.SendConferenceCallBroadcast"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        block: bytes,
    ) -> None:
        self.call = call
        self.block = block

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_bytes(self.block)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        block = r.read_bytes()
        self = cls.__new__(cls)
        self.call = call
        self.block = block
        return self


class InviteConferenceCallParticipant(TLFunction["base.Updates"]):
    """The TL function phone.inviteConferenceCallParticipant#bcf22685, answered with Updates."""

    __slots__ = ("video", "call", "user_id",)

    ID = 0xBCF22685
    QUALNAME = "functions.phone.InviteConferenceCallParticipant"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        video: bool = False,
        call: base.InputGroupCall,
        user_id: base.InputUser,
    ) -> None:
        self.video = video
        self.call = call
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.video:
            flags |= 1 << 0
        w.write_int(flags)
        self.call.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        video = bool(flags & (1 << 0))
        call = r.read_object()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.video = video
        self.call = call
        self.user_id = user_id
        return self


class DeclineConferenceCallInvite(TLFunction["base.Updates"]):
    """The TL function phone.declineConferenceCallInvite#3c479971, answered with Updates."""

    __slots__ = ("msg_id",)

    ID = 0x3C479971
    QUALNAME = "functions.phone.DeclineConferenceCallInvite"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        msg_id: int,
    ) -> None:
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.msg_id = msg_id
        return self


class GetGroupCallChainBlocks(TLFunction["base.Updates"]):
    """The TL function phone.getGroupCallChainBlocks#ee9f88a6, answered with Updates."""

    __slots__ = ("call", "sub_chain_id", "offset", "limit",)

    ID = 0xEE9F88A6
    QUALNAME = "functions.phone.GetGroupCallChainBlocks"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        sub_chain_id: int,
        offset: int,
        limit: int,
    ) -> None:
        self.call = call
        self.sub_chain_id = sub_chain_id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_int(self.sub_chain_id)
        w.write_int(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        sub_chain_id = r.read_int()
        offset = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.call = call
        self.sub_chain_id = sub_chain_id
        self.offset = offset
        self.limit = limit
        return self


class SendGroupCallMessage(TLFunction["base.Updates"]):
    """The TL function phone.sendGroupCallMessage#b1d11410, answered with Updates."""

    __slots__ = ("call", "random_id", "message", "allow_paid_stars", "send_as",)

    ID = 0xB1D11410
    QUALNAME = "functions.phone.SendGroupCallMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        random_id: int,
        message: base.TextWithEntities,
        allow_paid_stars: int | None = None,
        send_as: base.InputPeer | None = None,
    ) -> None:
        self.call = call
        self.random_id = random_id
        self.message = message
        self.allow_paid_stars = allow_paid_stars
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.allow_paid_stars is not None:
            flags |= 1 << 0
        if self.send_as is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.call.write(w)
        w.write_long(self.random_id)
        self.message.write(w)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)
        if self.send_as is not None:
            self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        call = r.read_object()
        random_id = r.read_long()
        message = r.read_object()
        allow_paid_stars = r.read_long() if flags & (1 << 0) else None
        send_as = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.call = call
        self.random_id = random_id
        self.message = message
        self.allow_paid_stars = allow_paid_stars
        self.send_as = send_as
        return self


class SendGroupCallEncryptedMessage(TLFunction["bool"]):
    """The TL function phone.sendGroupCallEncryptedMessage#e5afa56d, answered with Bool."""

    __slots__ = ("call", "encrypted_message",)

    ID = 0xE5AFA56D
    QUALNAME = "functions.phone.SendGroupCallEncryptedMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        encrypted_message: bytes,
    ) -> None:
        self.call = call
        self.encrypted_message = encrypted_message

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_bytes(self.encrypted_message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        encrypted_message = r.read_bytes()
        self = cls.__new__(cls)
        self.call = call
        self.encrypted_message = encrypted_message
        return self


class DeleteGroupCallMessages(TLFunction["base.Updates"]):
    """The TL function phone.deleteGroupCallMessages#f64f54f7, answered with Updates."""

    __slots__ = ("report_spam", "call", "messages",)

    ID = 0xF64F54F7
    QUALNAME = "functions.phone.DeleteGroupCallMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        report_spam: bool = False,
        call: base.InputGroupCall,
        messages: list[int],
    ) -> None:
        self.report_spam = report_spam
        self.call = call
        self.messages = messages

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.report_spam:
            flags |= 1 << 0
        w.write_int(flags)
        self.call.write(w)
        w.write_vector(self.messages, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        report_spam = bool(flags & (1 << 0))
        call = r.read_object()
        messages = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.report_spam = report_spam
        self.call = call
        self.messages = messages
        return self


class DeleteGroupCallParticipantMessages(TLFunction["base.Updates"]):
    """The TL function phone.deleteGroupCallParticipantMessages#1dbfeca0, answered with Updates."""

    __slots__ = ("report_spam", "call", "participant",)

    ID = 0x1DBFECA0
    QUALNAME = "functions.phone.DeleteGroupCallParticipantMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        report_spam: bool = False,
        call: base.InputGroupCall,
        participant: base.InputPeer,
    ) -> None:
        self.report_spam = report_spam
        self.call = call
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.report_spam:
            flags |= 1 << 0
        w.write_int(flags)
        self.call.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        report_spam = bool(flags & (1 << 0))
        call = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.report_spam = report_spam
        self.call = call
        self.participant = participant
        return self


class GetGroupCallStars(TLFunction["base.phone.GroupCallStars"]):
    """The TL function phone.getGroupCallStars#6f636302, answered with phone.GroupCallStars."""

    __slots__ = ("call",)

    ID = 0x6F636302
    QUALNAME = "functions.phone.GetGroupCallStars"
    RESULT = "phone.GroupCallStars"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
    ) -> None:
        self.call = call

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        return self


class SaveDefaultSendAs(TLFunction["bool"]):
    """The TL function phone.saveDefaultSendAs#4167add1, answered with Bool."""

    __slots__ = ("call", "send_as",)

    ID = 0x4167ADD1
    QUALNAME = "functions.phone.SaveDefaultSendAs"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        call: base.InputGroupCall,
        send_as: base.InputPeer,
    ) -> None:
        self.call = call
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        send_as = r.read_object()
        self = cls.__new__(cls)
        self.call = call
        self.send_as = send_as
        return self
