# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the updates namespace.

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


class GetState(TLFunction["base.updates.State"]):
    """The TL function updates.getState#edd4882a, answered with updates.State."""

    __slots__ = ()

    ID = 0xEDD4882A
    QUALNAME = "functions.updates.GetState"
    RESULT = "updates.State"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetDifference(TLFunction["base.updates.Difference"]):
    """The TL function updates.getDifference#19c2f763, answered with updates.Difference."""

    __slots__ = ("pts", "pts_limit", "pts_total_limit", "date", "qts", "qts_limit",)

    ID = 0x19C2F763
    QUALNAME = "functions.updates.GetDifference"
    RESULT = "updates.Difference"

    def __init__(
        self,
        *,
        pts: int,
        pts_limit: int | None = None,
        pts_total_limit: int | None = None,
        date: int,
        qts: int,
        qts_limit: int | None = None,
    ) -> None:
        self.pts = pts
        self.pts_limit = pts_limit
        self.pts_total_limit = pts_total_limit
        self.date = date
        self.qts = qts
        self.qts_limit = qts_limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pts_limit is not None:
            flags |= 1 << 1
        if self.pts_total_limit is not None:
            flags |= 1 << 0
        if self.qts_limit is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.pts)
        if self.pts_limit is not None:
            w.write_int(self.pts_limit)
        if self.pts_total_limit is not None:
            w.write_int(self.pts_total_limit)
        w.write_int(self.date)
        w.write_int(self.qts)
        if self.qts_limit is not None:
            w.write_int(self.qts_limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pts = r.read_int()
        pts_limit = r.read_int() if flags & (1 << 1) else None
        pts_total_limit = r.read_int() if flags & (1 << 0) else None
        date = r.read_int()
        qts = r.read_int()
        qts_limit = r.read_int() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.pts = pts
        self.pts_limit = pts_limit
        self.pts_total_limit = pts_total_limit
        self.date = date
        self.qts = qts
        self.qts_limit = qts_limit
        return self


class GetChannelDifference(TLFunction["base.updates.ChannelDifference"]):
    """The TL function updates.getChannelDifference#03173d78, answered with updates.ChannelDifference."""

    __slots__ = ("force", "channel", "filter", "pts", "limit",)

    ID = 0x03173D78
    QUALNAME = "functions.updates.GetChannelDifference"
    RESULT = "updates.ChannelDifference"

    def __init__(
        self,
        *,
        force: bool = False,
        channel: base.InputChannel,
        filter: base.ChannelMessagesFilter,
        pts: int,
        limit: int,
    ) -> None:
        self.force = force
        self.channel = channel
        self.filter = filter
        self.pts = pts
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.force:
            flags |= 1 << 0
        w.write_int(flags)
        self.channel.write(w)
        self.filter.write(w)
        w.write_int(self.pts)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        force = bool(flags & (1 << 0))
        channel = r.read_object()
        filter = r.read_object()
        pts = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.force = force
        self.channel = channel
        self.filter = filter
        self.pts = pts
        self.limit = limit
        return self
