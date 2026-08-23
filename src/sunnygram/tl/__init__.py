# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The hand-written TL codec.

The generated constructors in the raw package are built on top of this.
"""

from __future__ import annotations

from .core import (
    BOOL_FALSE,
    BOOL_TRUE,
    GZIP_PACKED,
    VECTOR,
    Buffer,
    TLFunction,
    TLObject,
    TLReader,
    TLResult,
    TLWriter,
    read_answer,
    resolve_constructor,
    set_constructor_resolver,
    unpack_gzip,
)

__all__ = [
    "BOOL_FALSE",
    "BOOL_TRUE",
    "GZIP_PACKED",
    "VECTOR",
    "Buffer",
    "TLFunction",
    "TLObject",
    "TLReader",
    "TLResult",
    "TLWriter",
    "read_answer",
    "resolve_constructor",
    "set_constructor_resolver",
    "unpack_gzip",
]
