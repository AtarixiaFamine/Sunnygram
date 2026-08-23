# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the communities namespace.

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


class Create(TLFunction["base.Updates"]):
    """The TL function communities.create#a63859ec, answered with Updates."""

    __slots__ = ("hidden", "title", "about", "peer",)

    ID = 0xA63859EC
    QUALNAME = "functions.communities.Create"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        hidden: bool = False,
        title: str,
        about: str | None = None,
        peer: base.InputPeer,
    ) -> None:
        self.hidden = hidden
        self.title = title
        self.about = about
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.hidden:
            flags |= 1 << 1
        if self.about is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.title)
        if self.about is not None:
            w.write_string(self.about)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hidden = bool(flags & (1 << 1))
        title = r.read_string()
        about = r.read_string() if flags & (1 << 0) else None
        peer = r.read_object()
        self = cls.__new__(cls)
        self.hidden = hidden
        self.title = title
        self.about = about
        self.peer = peer
        return self


class TogglePeerLink(TLFunction["bool"]):
    """The TL function communities.togglePeerLink#736dcfea, answered with Bool."""

    __slots__ = ("visible", "hidden", "deleted", "community", "peer",)

    ID = 0x736DCFEA
    QUALNAME = "functions.communities.TogglePeerLink"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        visible: bool = False,
        hidden: bool = False,
        deleted: bool = False,
        community: base.InputChannel,
        peer: base.InputPeer,
    ) -> None:
        self.visible = visible
        self.hidden = hidden
        self.deleted = deleted
        self.community = community
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.visible:
            flags |= 1 << 0
        if self.hidden:
            flags |= 1 << 1
        if self.deleted:
            flags |= 1 << 2
        w.write_int(flags)
        self.community.write(w)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        visible = bool(flags & (1 << 0))
        hidden = bool(flags & (1 << 1))
        deleted = bool(flags & (1 << 2))
        community = r.read_object()
        peer = r.read_object()
        self = cls.__new__(cls)
        self.visible = visible
        self.hidden = hidden
        self.deleted = deleted
        self.community = community
        self.peer = peer
        return self


class GetJoinedCommunities(TLFunction["base.messages.Chats"]):
    """The TL function communities.getJoinedCommunities#a663e830, answered with messages.Chats."""

    __slots__ = ()

    ID = 0xA663E830
    QUALNAME = "functions.communities.GetJoinedCommunities"
    RESULT = "messages.Chats"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ToggleCommunityCollapsedInDialogs(TLFunction["base.Updates"]):
    """The TL function communities.toggleCommunityCollapsedInDialogs#d766e3ea, answered with Updates."""

    __slots__ = ("collapsed", "community",)

    ID = 0xD766E3EA
    QUALNAME = "functions.communities.ToggleCommunityCollapsedInDialogs"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        collapsed: bool = False,
        community: base.InputChannel,
    ) -> None:
        self.collapsed = collapsed
        self.community = community

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.collapsed:
            flags |= 1 << 0
        w.write_int(flags)
        self.community.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        collapsed = bool(flags & (1 << 0))
        community = r.read_object()
        self = cls.__new__(cls)
        self.collapsed = collapsed
        self.community = community
        return self


class GetPeerLinkRequests(TLFunction["base.communities.PeerLinkRequests"]):
    """The TL function communities.getPeerLinkRequests#93773344, answered with communities.PeerLinkRequests."""

    __slots__ = ("community", "offset", "limit",)

    ID = 0x93773344
    QUALNAME = "functions.communities.GetPeerLinkRequests"
    RESULT = "communities.PeerLinkRequests"

    def __init__(
        self,
        *,
        community: base.InputChannel,
        offset: str,
        limit: int,
    ) -> None:
        self.community = community
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.community.write(w)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        community = r.read_object()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.community = community
        self.offset = offset
        self.limit = limit
        return self


class TogglePeerLinkRequestApproval(TLFunction["bool"]):
    """The TL function communities.togglePeerLinkRequestApproval#8c8219a8, answered with Bool."""

    __slots__ = ("reject", "community", "peer",)

    ID = 0x8C8219A8
    QUALNAME = "functions.communities.TogglePeerLinkRequestApproval"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        reject: bool = False,
        community: base.InputChannel,
        peer: base.InputPeer,
    ) -> None:
        self.reject = reject
        self.community = community
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reject:
            flags |= 1 << 0
        w.write_int(flags)
        self.community.write(w)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reject = bool(flags & (1 << 0))
        community = r.read_object()
        peer = r.read_object()
        self = cls.__new__(cls)
        self.reject = reject
        self.community = community
        self.peer = peer
        return self


class ToggleAllPeerLinkRequestApproval(TLFunction["bool"]):
    """The TL function communities.toggleAllPeerLinkRequestApproval#bfe3dd3d, answered with Bool."""

    __slots__ = ("reject", "community",)

    ID = 0xBFE3DD3D
    QUALNAME = "functions.communities.ToggleAllPeerLinkRequestApproval"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        reject: bool = False,
        community: base.InputChannel,
    ) -> None:
        self.reject = reject
        self.community = community

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reject:
            flags |= 1 << 0
        w.write_int(flags)
        self.community.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reject = bool(flags & (1 << 0))
        community = r.read_object()
        self = cls.__new__(cls)
        self.reject = reject
        self.community = community
        return self


class ToggleParticipantBanned(TLFunction["bool"]):
    """The TL function communities.toggleParticipantBanned#9967ad0f, answered with Bool."""

    __slots__ = ("unban", "community", "participant",)

    ID = 0x9967AD0F
    QUALNAME = "functions.communities.ToggleParticipantBanned"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        unban: bool = False,
        community: base.InputChannel,
        participant: base.InputPeer,
    ) -> None:
        self.unban = unban
        self.community = community
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.unban:
            flags |= 1 << 0
        w.write_int(flags)
        self.community.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        unban = bool(flags & (1 << 0))
        community = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.unban = unban
        self.community = community
        self.participant = participant
        return self


class GetParticipantJoinedChats(TLFunction["base.communities.ParticipantJoinedChats"]):
    """The TL function communities.getParticipantJoinedChats#f87eabab, answered with communities.ParticipantJoinedChats."""

    __slots__ = ("community", "participant",)

    ID = 0xF87EABAB
    QUALNAME = "functions.communities.GetParticipantJoinedChats"
    RESULT = "communities.ParticipantJoinedChats"

    def __init__(
        self,
        *,
        community: base.InputChannel,
        participant: base.InputPeer,
    ) -> None:
        self.community = community
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        self.community.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        community = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.community = community
        self.participant = participant
        return self
