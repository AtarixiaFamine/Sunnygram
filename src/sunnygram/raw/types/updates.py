# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the updates namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

import struct

from typing import TYPE_CHECKING, Self

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


_PACK_State = struct.Struct("<iiiii")


class State(TLObject):
    """The TL type updates.state#a56c2a3e, a form of updates.State."""

    __slots__ = ("pts", "qts", "date", "seq", "unread_count",)

    ID = 0xA56C2A3E
    QUALNAME = "types.updates.State"

    def __init__(
        self,
        *,
        pts: int,
        qts: int,
        date: int,
        seq: int,
        unread_count: int,
    ) -> None:
        self.pts = pts
        self.qts = qts
        self.date = date
        self.seq = seq
        self.unread_count = unread_count

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_State.pack(self.pts, self.qts, self.date, self.seq, self.unread_count))
        except struct.error:
            w.write_int(self.pts)
            w.write_int(self.qts)
            w.write_int(self.date)
            w.write_int(self.seq)
            w.write_int(self.unread_count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pts = r.read_int()
        qts = r.read_int()
        date = r.read_int()
        seq = r.read_int()
        unread_count = r.read_int()
        self = cls.__new__(cls)
        self.pts = pts
        self.qts = qts
        self.date = date
        self.seq = seq
        self.unread_count = unread_count
        return self


_PACK_DifferenceEmpty = struct.Struct("<ii")


class DifferenceEmpty(TLObject):
    """The TL type updates.differenceEmpty#5d75a138, a form of updates.Difference."""

    __slots__ = ("date", "seq",)

    ID = 0x5D75A138
    QUALNAME = "types.updates.DifferenceEmpty"

    def __init__(
        self,
        *,
        date: int,
        seq: int,
    ) -> None:
        self.date = date
        self.seq = seq

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_DifferenceEmpty.pack(self.date, self.seq))
        except struct.error:
            w.write_int(self.date)
            w.write_int(self.seq)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        date = r.read_int()
        seq = r.read_int()
        self = cls.__new__(cls)
        self.date = date
        self.seq = seq
        return self


class Difference(TLObject):
    """The TL type updates.difference#00f49ca0, a form of updates.Difference."""

    __slots__ = ("new_messages", "new_encrypted_messages", "other_updates", "chats", "users", "state",)

    ID = 0x00F49CA0
    QUALNAME = "types.updates.Difference"

    def __init__(
        self,
        *,
        new_messages: list[base.Message],
        new_encrypted_messages: list[base.EncryptedMessage],
        other_updates: list[base.Update],
        chats: list[base.Chat],
        users: list[base.User],
        state: base.updates.State,
    ) -> None:
        self.new_messages = new_messages
        self.new_encrypted_messages = new_encrypted_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users
        self.state = state

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.new_messages)
        w.write_vector(self.new_encrypted_messages)
        w.write_vector(self.other_updates)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        self.state.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        new_messages = r.read_vector()
        new_encrypted_messages = r.read_vector()
        other_updates = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        state = r.read_object()
        self = cls.__new__(cls)
        self.new_messages = new_messages
        self.new_encrypted_messages = new_encrypted_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users
        self.state = state
        return self


class DifferenceSlice(TLObject):
    """The TL type updates.differenceSlice#a8fb1981, a form of updates.Difference."""

    __slots__ = ("new_messages", "new_encrypted_messages", "other_updates", "chats", "users", "intermediate_state",)

    ID = 0xA8FB1981
    QUALNAME = "types.updates.DifferenceSlice"

    def __init__(
        self,
        *,
        new_messages: list[base.Message],
        new_encrypted_messages: list[base.EncryptedMessage],
        other_updates: list[base.Update],
        chats: list[base.Chat],
        users: list[base.User],
        intermediate_state: base.updates.State,
    ) -> None:
        self.new_messages = new_messages
        self.new_encrypted_messages = new_encrypted_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users
        self.intermediate_state = intermediate_state

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.new_messages)
        w.write_vector(self.new_encrypted_messages)
        w.write_vector(self.other_updates)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        self.intermediate_state.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        new_messages = r.read_vector()
        new_encrypted_messages = r.read_vector()
        other_updates = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        intermediate_state = r.read_object()
        self = cls.__new__(cls)
        self.new_messages = new_messages
        self.new_encrypted_messages = new_encrypted_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users
        self.intermediate_state = intermediate_state
        return self


class DifferenceTooLong(TLObject):
    """The TL type updates.differenceTooLong#4afe8f6d, a form of updates.Difference."""

    __slots__ = ("pts",)

    ID = 0x4AFE8F6D
    QUALNAME = "types.updates.DifferenceTooLong"

    def __init__(
        self,
        *,
        pts: int,
    ) -> None:
        self.pts = pts

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.pts)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pts = r.read_int()
        self = cls.__new__(cls)
        self.pts = pts
        return self


class ChannelDifferenceEmpty(TLObject):
    """The TL type updates.channelDifferenceEmpty#3e11affb, a form of updates.ChannelDifference."""

    __slots__ = ("final", "pts", "timeout",)

    ID = 0x3E11AFFB
    QUALNAME = "types.updates.ChannelDifferenceEmpty"

    def __init__(
        self,
        *,
        final: bool = False,
        pts: int,
        timeout: int | None = None,
    ) -> None:
        self.final = final
        self.pts = pts
        self.timeout = timeout

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.final:
            flags |= 1 << 0
        if self.timeout is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_int(self.pts)
        if self.timeout is not None:
            w.write_int(self.timeout)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        final = bool(flags & (1 << 0))
        pts = r.read_int()
        timeout = r.read_int() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.final = final
        self.pts = pts
        self.timeout = timeout
        return self


class ChannelDifferenceTooLong(TLObject):
    """The TL type updates.channelDifferenceTooLong#a4bcc6fe, a form of updates.ChannelDifference."""

    __slots__ = ("final", "timeout", "dialog", "messages", "chats", "users",)

    ID = 0xA4BCC6FE
    QUALNAME = "types.updates.ChannelDifferenceTooLong"

    def __init__(
        self,
        *,
        final: bool = False,
        timeout: int | None = None,
        dialog: base.Dialog,
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.final = final
        self.timeout = timeout
        self.dialog = dialog
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.final:
            flags |= 1 << 0
        if self.timeout is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.timeout is not None:
            w.write_int(self.timeout)
        self.dialog.write(w)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        final = bool(flags & (1 << 0))
        timeout = r.read_int() if flags & (1 << 1) else None
        dialog = r.read_object()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.final = final
        self.timeout = timeout
        self.dialog = dialog
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class ChannelDifference(TLObject):
    """The TL type updates.channelDifference#2064674e, a form of updates.ChannelDifference."""

    __slots__ = ("final", "pts", "timeout", "new_messages", "other_updates", "chats", "users",)

    ID = 0x2064674E
    QUALNAME = "types.updates.ChannelDifference"

    def __init__(
        self,
        *,
        final: bool = False,
        pts: int,
        timeout: int | None = None,
        new_messages: list[base.Message],
        other_updates: list[base.Update],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.final = final
        self.pts = pts
        self.timeout = timeout
        self.new_messages = new_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.final:
            flags |= 1 << 0
        if self.timeout is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_int(self.pts)
        if self.timeout is not None:
            w.write_int(self.timeout)
        w.write_vector(self.new_messages)
        w.write_vector(self.other_updates)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        final = bool(flags & (1 << 0))
        pts = r.read_int()
        timeout = r.read_int() if flags & (1 << 1) else None
        new_messages = r.read_vector()
        other_updates = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.final = final
        self.pts = pts
        self.timeout = timeout
        self.new_messages = new_messages
        self.other_updates = other_updates
        self.chats = chats
        self.users = users
        return self
