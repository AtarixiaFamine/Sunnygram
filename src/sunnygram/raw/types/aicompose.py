# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the aicompose namespace.

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


class TonesNotModified(TLObject):
    """The TL type aicompose.tonesNotModified#c1f46103, a form of aicompose.Tones."""

    __slots__ = ()

    ID = 0xC1F46103
    QUALNAME = "types.aicompose.TonesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Tones(TLObject):
    """The TL type aicompose.tones#6c9d0efe, a form of aicompose.Tones."""

    __slots__ = ("hash", "tones", "users",)

    ID = 0x6C9D0EFE
    QUALNAME = "types.aicompose.Tones"

    def __init__(
        self,
        *,
        hash: int,
        tones: list[base.AiComposeTone],
        users: list[base.User],
    ) -> None:
        self.hash = hash
        self.tones = tones
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.tones)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        tones = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.tones = tones
        self.users = users
        return self
