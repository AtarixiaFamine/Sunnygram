# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the folders namespace.

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


class EditPeerFolders(TLFunction["base.Updates"]):
    """The TL function folders.editPeerFolders#6847d0ab, answered with Updates."""

    __slots__ = ("folder_peers",)

    ID = 0x6847D0AB
    QUALNAME = "functions.folders.EditPeerFolders"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        folder_peers: list[base.InputFolderPeer],
    ) -> None:
        self.folder_peers = folder_peers

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.folder_peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        folder_peers = r.read_vector()
        self = cls.__new__(cls)
        self.folder_peers = folder_peers
        return self
