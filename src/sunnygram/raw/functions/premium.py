# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the premium namespace.

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


class GetBoostsList(TLFunction["base.premium.BoostsList"]):
    """The TL function premium.getBoostsList#60f67660, answered with premium.BoostsList."""

    __slots__ = ("gifts", "peer", "offset", "limit",)

    ID = 0x60F67660
    QUALNAME = "functions.premium.GetBoostsList"
    RESULT = "premium.BoostsList"

    def __init__(
        self,
        *,
        gifts: bool = False,
        peer: base.InputPeer,
        offset: str,
        limit: int,
    ) -> None:
        self.gifts = gifts
        self.peer = peer
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.gifts:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        gifts = bool(flags & (1 << 0))
        peer = r.read_object()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.gifts = gifts
        self.peer = peer
        self.offset = offset
        self.limit = limit
        return self


class GetMyBoosts(TLFunction["base.premium.MyBoosts"]):
    """The TL function premium.getMyBoosts#0be77b4a, answered with premium.MyBoosts."""

    __slots__ = ()

    ID = 0x0BE77B4A
    QUALNAME = "functions.premium.GetMyBoosts"
    RESULT = "premium.MyBoosts"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ApplyBoost(TLFunction["base.premium.MyBoosts"]):
    """The TL function premium.applyBoost#6b7da746, answered with premium.MyBoosts."""

    __slots__ = ("slots", "peer",)

    ID = 0x6B7DA746
    QUALNAME = "functions.premium.ApplyBoost"
    RESULT = "premium.MyBoosts"

    def __init__(
        self,
        *,
        slots: list[int] | None = None,
        peer: base.InputPeer,
    ) -> None:
        self.slots = slots
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.slots is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.slots is not None:
            w.write_vector(self.slots, TLWriter.write_int)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        slots = r.read_vector(TLReader.read_int) if flags & (1 << 0) else None
        peer = r.read_object()
        self = cls.__new__(cls)
        self.slots = slots
        self.peer = peer
        return self


class GetBoostsStatus(TLFunction["base.premium.BoostsStatus"]):
    """The TL function premium.getBoostsStatus#042f1f61, answered with premium.BoostsStatus."""

    __slots__ = ("peer",)

    ID = 0x042F1F61
    QUALNAME = "functions.premium.GetBoostsStatus"
    RESULT = "premium.BoostsStatus"

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


class GetUserBoosts(TLFunction["base.premium.BoostsList"]):
    """The TL function premium.getUserBoosts#39854d1f, answered with premium.BoostsList."""

    __slots__ = ("peer", "user_id",)

    ID = 0x39854D1F
    QUALNAME = "functions.premium.GetUserBoosts"
    RESULT = "premium.BoostsList"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        user_id: base.InputUser,
    ) -> None:
        self.peer = peer
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.user_id = user_id
        return self
