# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the communities namespace.

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


class PeerLinkRequests(TLObject):
    """The TL type communities.peerLinkRequests#2244afad, a form of communities.PeerLinkRequests."""

    __slots__ = ("total_count", "requests", "next_offset", "chats", "users",)

    ID = 0x2244AFAD
    QUALNAME = "types.communities.PeerLinkRequests"

    def __init__(
        self,
        *,
        total_count: int,
        requests: list[base.CommunityPeerRequest],
        next_offset: str | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.total_count = total_count
        self.requests = requests
        self.next_offset = next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.total_count)
        w.write_vector(self.requests)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        total_count = r.read_int()
        requests = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.total_count = total_count
        self.requests = requests
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        return self


class ParticipantJoinedChats(TLObject):
    """The TL type communities.participantJoinedChats#8d78512a, a form of communities.ParticipantJoinedChats."""

    __slots__ = ("creator_chat_ids", "joined_chat_ids", "chats", "users",)

    ID = 0x8D78512A
    QUALNAME = "types.communities.ParticipantJoinedChats"

    def __init__(
        self,
        *,
        creator_chat_ids: list[int],
        joined_chat_ids: list[int],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.creator_chat_ids = creator_chat_ids
        self.joined_chat_ids = joined_chat_ids
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.creator_chat_ids, TLWriter.write_long)
        w.write_vector(self.joined_chat_ids, TLWriter.write_long)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        creator_chat_ids = r.read_vector(TLReader.read_long)
        joined_chat_ids = r.read_vector(TLReader.read_long)
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.creator_chat_ids = creator_chat_ids
        self.joined_chat_ids = joined_chat_ids
        self.chats = chats
        self.users = users
        return self
