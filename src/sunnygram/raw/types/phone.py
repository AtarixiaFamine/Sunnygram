# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the phone namespace.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class PhoneCall(TLObject):
    """The TL type phone.phoneCall#ec82e140, a form of phone.PhoneCall."""

    __slots__ = ("phone_call", "users",)

    ID = 0xEC82E140
    QUALNAME = "types.phone.PhoneCall"

    def __init__(
        self,
        *,
        phone_call: base.PhoneCall,
        users: list[base.User],
    ) -> None:
        self.phone_call = phone_call
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.phone_call.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_call = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.phone_call = phone_call
        self.users = users
        return self


class GroupCall(TLObject):
    """The TL type phone.groupCall#9e727aad, a form of phone.GroupCall."""

    __slots__ = ("call", "participants", "participants_next_offset", "chats", "users",)

    ID = 0x9E727AAD
    QUALNAME = "types.phone.GroupCall"

    def __init__(
        self,
        *,
        call: base.GroupCall,
        participants: list[base.GroupCallParticipant],
        participants_next_offset: str,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.call = call
        self.participants = participants
        self.participants_next_offset = participants_next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.call.write(w)
        w.write_vector(self.participants)
        w.write_string(self.participants_next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        call = r.read_object()
        participants = r.read_vector()
        participants_next_offset = r.read_string()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.call = call
        self.participants = participants
        self.participants_next_offset = participants_next_offset
        self.chats = chats
        self.users = users
        return self


class GroupParticipants(TLObject):
    """The TL type phone.groupParticipants#f47751b6, a form of phone.GroupParticipants."""

    __slots__ = ("count", "participants", "next_offset", "chats", "users", "version",)

    ID = 0xF47751B6
    QUALNAME = "types.phone.GroupParticipants"

    def __init__(
        self,
        *,
        count: int,
        participants: list[base.GroupCallParticipant],
        next_offset: str,
        chats: list[base.Chat],
        users: list[base.User],
        version: int,
    ) -> None:
        self.count = count
        self.participants = participants
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        self.version = version

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.participants)
        w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        w.write_int(self.version)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        participants = r.read_vector()
        next_offset = r.read_string()
        chats = r.read_vector()
        users = r.read_vector()
        version = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        self.participants = participants
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        self.version = version
        return self


class JoinAsPeers(TLObject):
    """The TL type phone.joinAsPeers#afe5623f, a form of phone.JoinAsPeers."""

    __slots__ = ("peers", "chats", "users",)

    ID = 0xAFE5623F
    QUALNAME = "types.phone.JoinAsPeers"

    def __init__(
        self,
        *,
        peers: list[base.Peer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.peers = peers
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.peers)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peers = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.peers = peers
        self.chats = chats
        self.users = users
        return self


class ExportedGroupCallInvite(TLObject):
    """The TL type phone.exportedGroupCallInvite#204bd158, a form of phone.ExportedGroupCallInvite."""

    __slots__ = ("link",)

    ID = 0x204BD158
    QUALNAME = "types.phone.ExportedGroupCallInvite"

    def __init__(
        self,
        *,
        link: str,
    ) -> None:
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.link)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        link = r.read_string()
        self = cls.__new__(cls)
        self.link = link
        return self


class GroupCallStreamChannels(TLObject):
    """The TL type phone.groupCallStreamChannels#d0e482b2, a form of phone.GroupCallStreamChannels."""

    __slots__ = ("channels",)

    ID = 0xD0E482B2
    QUALNAME = "types.phone.GroupCallStreamChannels"

    def __init__(
        self,
        *,
        channels: list[base.GroupCallStreamChannel],
    ) -> None:
        self.channels = channels

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.channels)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channels = r.read_vector()
        self = cls.__new__(cls)
        self.channels = channels
        return self


class GroupCallStreamRtmpUrl(TLObject):
    """The TL type phone.groupCallStreamRtmpUrl#2dbf3432, a form of phone.GroupCallStreamRtmpUrl."""

    __slots__ = ("url", "key",)

    ID = 0x2DBF3432
    QUALNAME = "types.phone.GroupCallStreamRtmpUrl"

    def __init__(
        self,
        *,
        url: str,
        key: str,
    ) -> None:
        self.url = url
        self.key = key

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)
        w.write_string(self.key)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        key = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        self.key = key
        return self


class GroupCallStars(TLObject):
    """The TL type phone.groupCallStars#9d1dbd26, a form of phone.GroupCallStars."""

    __slots__ = ("total_stars", "top_donors", "chats", "users",)

    ID = 0x9D1DBD26
    QUALNAME = "types.phone.GroupCallStars"

    def __init__(
        self,
        *,
        total_stars: int,
        top_donors: list[base.GroupCallDonor],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.total_stars = total_stars
        self.top_donors = top_donors
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.total_stars)
        w.write_vector(self.top_donors)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        total_stars = r.read_long()
        top_donors = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.total_stars = total_stars
        self.top_donors = top_donors
        self.chats = chats
        self.users = users
        return self
