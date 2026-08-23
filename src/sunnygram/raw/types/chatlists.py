# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the chatlists namespace.

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


class ExportedChatlistInvite(TLObject):
    """The TL type chatlists.exportedChatlistInvite#10e6e3a6, a form of chatlists.ExportedChatlistInvite."""

    __slots__ = ("filter", "invite",)

    ID = 0x10E6E3A6
    QUALNAME = "types.chatlists.ExportedChatlistInvite"

    def __init__(
        self,
        *,
        filter: base.DialogFilter,
        invite: base.ExportedChatlistInvite,
    ) -> None:
        self.filter = filter
        self.invite = invite

    def write_body(self, w: TLWriter) -> None:
        self.filter.write(w)
        self.invite.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        filter = r.read_object()
        invite = r.read_object()
        self = cls.__new__(cls)
        self.filter = filter
        self.invite = invite
        return self


class ExportedInvites(TLObject):
    """The TL type chatlists.exportedInvites#10ab6dc7, a form of chatlists.ExportedInvites."""

    __slots__ = ("invites", "chats", "users",)

    ID = 0x10AB6DC7
    QUALNAME = "types.chatlists.ExportedInvites"

    def __init__(
        self,
        *,
        invites: list[base.ExportedChatlistInvite],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.invites = invites
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.invites)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        invites = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.invites = invites
        self.chats = chats
        self.users = users
        return self


class ChatlistInviteAlready(TLObject):
    """The TL type chatlists.chatlistInviteAlready#fa87f659, a form of chatlists.ChatlistInvite."""

    __slots__ = ("filter_id", "missing_peers", "already_peers", "chats", "users",)

    ID = 0xFA87F659
    QUALNAME = "types.chatlists.ChatlistInviteAlready"

    def __init__(
        self,
        *,
        filter_id: int,
        missing_peers: list[base.Peer],
        already_peers: list[base.Peer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.filter_id = filter_id
        self.missing_peers = missing_peers
        self.already_peers = already_peers
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.filter_id)
        w.write_vector(self.missing_peers)
        w.write_vector(self.already_peers)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        filter_id = r.read_int()
        missing_peers = r.read_vector()
        already_peers = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.filter_id = filter_id
        self.missing_peers = missing_peers
        self.already_peers = already_peers
        self.chats = chats
        self.users = users
        return self


class ChatlistInvite(TLObject):
    """The TL type chatlists.chatlistInvite#f10ece2f, a form of chatlists.ChatlistInvite."""

    __slots__ = ("title_noanimate", "title", "emoticon", "peers", "chats", "users",)

    ID = 0xF10ECE2F
    QUALNAME = "types.chatlists.ChatlistInvite"

    def __init__(
        self,
        *,
        title_noanimate: bool = False,
        title: base.TextWithEntities,
        emoticon: str | None = None,
        peers: list[base.Peer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.title_noanimate = title_noanimate
        self.title = title
        self.emoticon = emoticon
        self.peers = peers
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title_noanimate:
            flags |= 1 << 1
        if self.emoticon is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.title.write(w)
        if self.emoticon is not None:
            w.write_string(self.emoticon)
        w.write_vector(self.peers)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        title_noanimate = bool(flags & (1 << 1))
        title = r.read_object()
        emoticon = r.read_string() if flags & (1 << 0) else None
        peers = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.title_noanimate = title_noanimate
        self.title = title
        self.emoticon = emoticon
        self.peers = peers
        self.chats = chats
        self.users = users
        return self


class ChatlistUpdates(TLObject):
    """The TL type chatlists.chatlistUpdates#93bd878d, a form of chatlists.ChatlistUpdates."""

    __slots__ = ("missing_peers", "chats", "users",)

    ID = 0x93BD878D
    QUALNAME = "types.chatlists.ChatlistUpdates"

    def __init__(
        self,
        *,
        missing_peers: list[base.Peer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.missing_peers = missing_peers
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.missing_peers)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        missing_peers = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.missing_peers = missing_peers
        self.chats = chats
        self.users = users
        return self
