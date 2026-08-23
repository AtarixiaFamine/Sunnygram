# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the stickers namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import Self

from ...tl import TLObject, TLReader, TLWriter


class SuggestedShortName(TLObject):
    """The TL type stickers.suggestedShortName#85fea03f, a form of stickers.SuggestedShortName."""

    __slots__ = ("short_name",)

    ID = 0x85FEA03F
    QUALNAME = "types.stickers.SuggestedShortName"

    def __init__(
        self,
        *,
        short_name: str,
    ) -> None:
        self.short_name = short_name

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.short_name)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        short_name = r.read_string()
        self = cls.__new__(cls)
        self.short_name = short_name
        return self
