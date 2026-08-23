# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the channels namespace.

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


class ChannelParticipants(TLObject):
    """The TL type channels.channelParticipants#9ab0feaf, a form of channels.ChannelParticipants."""

    __slots__ = ("count", "participants", "chats", "users",)

    ID = 0x9AB0FEAF
    QUALNAME = "types.channels.ChannelParticipants"

    def __init__(
        self,
        *,
        count: int,
        participants: list[base.ChannelParticipant],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.participants = participants
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.participants)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        participants = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.participants = participants
        self.chats = chats
        self.users = users
        return self


class ChannelParticipantsNotModified(TLObject):
    """The TL type channels.channelParticipantsNotModified#f0173fe9, a form of channels.ChannelParticipants."""

    __slots__ = ()

    ID = 0xF0173FE9
    QUALNAME = "types.channels.ChannelParticipantsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ChannelParticipant(TLObject):
    """The TL type channels.channelParticipant#dfb80317, a form of channels.ChannelParticipant."""

    __slots__ = ("participant", "chats", "users",)

    ID = 0xDFB80317
    QUALNAME = "types.channels.ChannelParticipant"

    def __init__(
        self,
        *,
        participant: base.ChannelParticipant,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.participant = participant
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.participant.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        participant = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.participant = participant
        self.chats = chats
        self.users = users
        return self


class AdminLogResults(TLObject):
    """The TL type channels.adminLogResults#ed8af74d, a form of channels.AdminLogResults."""

    __slots__ = ("events", "chats", "users",)

    ID = 0xED8AF74D
    QUALNAME = "types.channels.AdminLogResults"

    def __init__(
        self,
        *,
        events: list[base.ChannelAdminLogEvent],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.events = events
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.events)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        events = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.events = events
        self.chats = chats
        self.users = users
        return self


class SendAsPeers(TLObject):
    """The TL type channels.sendAsPeers#f496b0c6, a form of channels.SendAsPeers."""

    __slots__ = ("peers", "chats", "users",)

    ID = 0xF496B0C6
    QUALNAME = "types.channels.SendAsPeers"

    def __init__(
        self,
        *,
        peers: list[base.SendAsPeer],
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


class SponsoredMessageReportResultChooseOption(TLObject):
    """The TL type channels.sponsoredMessageReportResultChooseOption#846f9e42, a form of channels.SponsoredMessageReportResult."""

    __slots__ = ("title", "options",)

    ID = 0x846F9E42
    QUALNAME = "types.channels.SponsoredMessageReportResultChooseOption"

    def __init__(
        self,
        *,
        title: str,
        options: list[base.SponsoredMessageReportOption],
    ) -> None:
        self.title = title
        self.options = options

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.title)
        w.write_vector(self.options)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        title = r.read_string()
        options = r.read_vector()
        self = cls.__new__(cls)
        self.title = title
        self.options = options
        return self


class SponsoredMessageReportResultAdsHidden(TLObject):
    """The TL type channels.sponsoredMessageReportResultAdsHidden#3e3bcf2f, a form of channels.SponsoredMessageReportResult."""

    __slots__ = ()

    ID = 0x3E3BCF2F
    QUALNAME = "types.channels.SponsoredMessageReportResultAdsHidden"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SponsoredMessageReportResultReported(TLObject):
    """The TL type channels.sponsoredMessageReportResultReported#ad798849, a form of channels.SponsoredMessageReportResult."""

    __slots__ = ()

    ID = 0xAD798849
    QUALNAME = "types.channels.SponsoredMessageReportResultReported"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self
