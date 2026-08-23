# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the stats namespace.

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


class GetBroadcastStats(TLFunction["base.stats.BroadcastStats"]):
    """The TL function stats.getBroadcastStats#ab42441a, answered with stats.BroadcastStats."""

    __slots__ = ("dark", "channel",)

    ID = 0xAB42441A
    QUALNAME = "functions.stats.GetBroadcastStats"
    RESULT = "stats.BroadcastStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        channel: base.InputChannel,
    ) -> None:
        self.dark = dark
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        channel = r.read_object()
        self = cls.__new__(cls)
        self.dark = dark
        self.channel = channel
        return self


class LoadAsyncGraph(TLFunction["base.StatsGraph"]):
    """The TL function stats.loadAsyncGraph#621d5fa0, answered with StatsGraph."""

    __slots__ = ("token", "x",)

    ID = 0x621D5FA0
    QUALNAME = "functions.stats.LoadAsyncGraph"
    RESULT = "StatsGraph"

    def __init__(
        self,
        *,
        token: str,
        x: int | None = None,
    ) -> None:
        self.token = token
        self.x = x

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.x is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.token)
        if self.x is not None:
            w.write_long(self.x)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        token = r.read_string()
        x = r.read_long() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.token = token
        self.x = x
        return self


class GetMegagroupStats(TLFunction["base.stats.MegagroupStats"]):
    """The TL function stats.getMegagroupStats#dcdf8607, answered with stats.MegagroupStats."""

    __slots__ = ("dark", "channel",)

    ID = 0xDCDF8607
    QUALNAME = "functions.stats.GetMegagroupStats"
    RESULT = "stats.MegagroupStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        channel: base.InputChannel,
    ) -> None:
        self.dark = dark
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        channel = r.read_object()
        self = cls.__new__(cls)
        self.dark = dark
        self.channel = channel
        return self


class GetMessagePublicForwards(TLFunction["base.stats.PublicForwards"]):
    """The TL function stats.getMessagePublicForwards#5f150144, answered with stats.PublicForwards."""

    __slots__ = ("channel", "msg_id", "offset", "limit",)

    ID = 0x5F150144
    QUALNAME = "functions.stats.GetMessagePublicForwards"
    RESULT = "stats.PublicForwards"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
        msg_id: int,
        offset: str,
        limit: int,
    ) -> None:
        self.channel = channel
        self.msg_id = msg_id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)
        w.write_int(self.msg_id)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        msg_id = r.read_int()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.channel = channel
        self.msg_id = msg_id
        self.offset = offset
        self.limit = limit
        return self


class GetMessageStats(TLFunction["base.stats.MessageStats"]):
    """The TL function stats.getMessageStats#b6e0a3f5, answered with stats.MessageStats."""

    __slots__ = ("dark", "channel", "msg_id",)

    ID = 0xB6E0A3F5
    QUALNAME = "functions.stats.GetMessageStats"
    RESULT = "stats.MessageStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        channel: base.InputChannel,
        msg_id: int,
    ) -> None:
        self.dark = dark
        self.channel = channel
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        channel = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.dark = dark
        self.channel = channel
        self.msg_id = msg_id
        return self


class GetStoryStats(TLFunction["base.stats.StoryStats"]):
    """The TL function stats.getStoryStats#374fef40, answered with stats.StoryStats."""

    __slots__ = ("dark", "peer", "id",)

    ID = 0x374FEF40
    QUALNAME = "functions.stats.GetStoryStats"
    RESULT = "stats.StoryStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        peer: base.InputPeer,
        id: int,
    ) -> None:
        self.dark = dark
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        peer = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.dark = dark
        self.peer = peer
        self.id = id
        return self


class GetStoryPublicForwards(TLFunction["base.stats.PublicForwards"]):
    """The TL function stats.getStoryPublicForwards#a6437ef6, answered with stats.PublicForwards."""

    __slots__ = ("peer", "id", "offset", "limit",)

    ID = 0xA6437EF6
    QUALNAME = "functions.stats.GetStoryPublicForwards"
    RESULT = "stats.PublicForwards"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        offset: str,
        limit: int,
    ) -> None:
        self.peer = peer
        self.id = id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.offset = offset
        self.limit = limit
        return self


class GetPollStats(TLFunction["base.stats.PollStats"]):
    """The TL function stats.getPollStats#c27dfa68, answered with stats.PollStats."""

    __slots__ = ("dark", "peer", "msg_id",)

    ID = 0xC27DFA68
    QUALNAME = "functions.stats.GetPollStats"
    RESULT = "stats.PollStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.dark = dark
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.dark = dark
        self.peer = peer
        self.msg_id = msg_id
        return self
