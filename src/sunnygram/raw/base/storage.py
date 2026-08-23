# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the storage namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import storage as types_storage

    FileType = (
        types_storage.FileUnknown
        | types_storage.FilePartial
        | types_storage.FileJpeg
        | types_storage.FileGif
        | types_storage.FilePng
        | types_storage.FilePdf
        | types_storage.FileMp3
        | types_storage.FileMov
        | types_storage.FileMp4
        | types_storage.FileWebp
    )
