# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the chatlists namespace.

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


class ExportChatlistInvite(TLFunction["base.chatlists.ExportedChatlistInvite"]):
    """The TL function chatlists.exportChatlistInvite#8472478e, answered with chatlists.ExportedChatlistInvite."""

    __slots__ = ("chatlist", "title", "peers",)

    ID = 0x8472478E
    QUALNAME = "functions.chatlists.ExportChatlistInvite"
    RESULT = "chatlists.ExportedChatlistInvite"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
        title: str,
        peers: list[base.InputPeer],
    ) -> None:
        self.chatlist = chatlist
        self.title = title
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)
        w.write_string(self.title)
        w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        title = r.read_string()
        peers = r.read_vector()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        self.title = title
        self.peers = peers
        return self


class DeleteExportedInvite(TLFunction["bool"]):
    """The TL function chatlists.deleteExportedInvite#719c5c5e, answered with Bool."""

    __slots__ = ("chatlist", "slug",)

    ID = 0x719C5C5E
    QUALNAME = "functions.chatlists.DeleteExportedInvite"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
        slug: str,
    ) -> None:
        self.chatlist = chatlist
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        slug = r.read_string()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        self.slug = slug
        return self


class EditExportedInvite(TLFunction["base.ExportedChatlistInvite"]):
    """The TL function chatlists.editExportedInvite#653db63d, answered with ExportedChatlistInvite."""

    __slots__ = ("chatlist", "slug", "title", "peers",)

    ID = 0x653DB63D
    QUALNAME = "functions.chatlists.EditExportedInvite"
    RESULT = "ExportedChatlistInvite"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
        slug: str,
        title: str | None = None,
        peers: list[base.InputPeer] | None = None,
    ) -> None:
        self.chatlist = chatlist
        self.slug = slug
        self.title = title
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title is not None:
            flags |= 1 << 1
        if self.peers is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.chatlist.write(w)
        w.write_string(self.slug)
        if self.title is not None:
            w.write_string(self.title)
        if self.peers is not None:
            w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        chatlist = r.read_object()
        slug = r.read_string()
        title = r.read_string() if flags & (1 << 1) else None
        peers = r.read_vector() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.chatlist = chatlist
        self.slug = slug
        self.title = title
        self.peers = peers
        return self


class GetExportedInvites(TLFunction["base.chatlists.ExportedInvites"]):
    """The TL function chatlists.getExportedInvites#ce03da83, answered with chatlists.ExportedInvites."""

    __slots__ = ("chatlist",)

    ID = 0xCE03DA83
    QUALNAME = "functions.chatlists.GetExportedInvites"
    RESULT = "chatlists.ExportedInvites"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
    ) -> None:
        self.chatlist = chatlist

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        return self


class CheckChatlistInvite(TLFunction["base.chatlists.ChatlistInvite"]):
    """The TL function chatlists.checkChatlistInvite#41c10fff, answered with chatlists.ChatlistInvite."""

    __slots__ = ("slug",)

    ID = 0x41C10FFF
    QUALNAME = "functions.chatlists.CheckChatlistInvite"
    RESULT = "chatlists.ChatlistInvite"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class JoinChatlistInvite(TLFunction["base.Updates"]):
    """The TL function chatlists.joinChatlistInvite#a6b1e39a, answered with Updates."""

    __slots__ = ("slug", "peers",)

    ID = 0xA6B1E39A
    QUALNAME = "functions.chatlists.JoinChatlistInvite"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        slug: str,
        peers: list[base.InputPeer],
    ) -> None:
        self.slug = slug
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)
        w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        peers = r.read_vector()
        self = cls.__new__(cls)
        self.slug = slug
        self.peers = peers
        return self


class GetChatlistUpdates(TLFunction["base.chatlists.ChatlistUpdates"]):
    """The TL function chatlists.getChatlistUpdates#89419521, answered with chatlists.ChatlistUpdates."""

    __slots__ = ("chatlist",)

    ID = 0x89419521
    QUALNAME = "functions.chatlists.GetChatlistUpdates"
    RESULT = "chatlists.ChatlistUpdates"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
    ) -> None:
        self.chatlist = chatlist

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        return self


class JoinChatlistUpdates(TLFunction["base.Updates"]):
    """The TL function chatlists.joinChatlistUpdates#e089f8f5, answered with Updates."""

    __slots__ = ("chatlist", "peers",)

    ID = 0xE089F8F5
    QUALNAME = "functions.chatlists.JoinChatlistUpdates"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
        peers: list[base.InputPeer],
    ) -> None:
        self.chatlist = chatlist
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)
        w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        peers = r.read_vector()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        self.peers = peers
        return self


class HideChatlistUpdates(TLFunction["bool"]):
    """The TL function chatlists.hideChatlistUpdates#66e486fb, answered with Bool."""

    __slots__ = ("chatlist",)

    ID = 0x66E486FB
    QUALNAME = "functions.chatlists.HideChatlistUpdates"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
    ) -> None:
        self.chatlist = chatlist

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        return self


class GetLeaveChatlistSuggestions(TLFunction["list[base.Peer]"]):
    """The TL function chatlists.getLeaveChatlistSuggestions#fdbcd714, answered with Vector<Peer>."""

    __slots__ = ("chatlist",)

    ID = 0xFDBCD714
    QUALNAME = "functions.chatlists.GetLeaveChatlistSuggestions"
    RESULT = "Vector<Peer>"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
    ) -> None:
        self.chatlist = chatlist

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        return self


class LeaveChatlist(TLFunction["base.Updates"]):
    """The TL function chatlists.leaveChatlist#74fae13a, answered with Updates."""

    __slots__ = ("chatlist", "peers",)

    ID = 0x74FAE13A
    QUALNAME = "functions.chatlists.LeaveChatlist"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        chatlist: base.InputChatlist,
        peers: list[base.InputPeer],
    ) -> None:
        self.chatlist = chatlist
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        self.chatlist.write(w)
        w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chatlist = r.read_object()
        peers = r.read_vector()
        self = cls.__new__(cls)
        self.chatlist = chatlist
        self.peers = peers
        return self
