# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the fragment namespace.

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


class GetCollectibleInfo(TLFunction["base.fragment.CollectibleInfo"]):
    """The TL function fragment.getCollectibleInfo#be1e85ba, answered with fragment.CollectibleInfo."""

    __slots__ = ("collectible",)

    ID = 0xBE1E85BA
    QUALNAME = "functions.fragment.GetCollectibleInfo"
    RESULT = "fragment.CollectibleInfo"

    def __init__(
        self,
        *,
        collectible: base.InputCollectible,
    ) -> None:
        self.collectible = collectible

    def write_body(self, w: TLWriter) -> None:
        self.collectible.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        collectible = r.read_object()
        self = cls.__new__(cls)
        self.collectible = collectible
        return self
