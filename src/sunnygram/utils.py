# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Small helpers with no layer of their own."""

from __future__ import annotations

__all__ = ["signed"]


def signed(value: int, bits: int) -> int:
    """A fixed-width bit pattern as the signed integer TL reads back.

    TL has no unsigned types, but the things that fill its wide ones are
    opaque: nonces, session ids, salts, access hashes. Those get generated from
    a random source, which produces unsigned values, and then come back off the
    wire signed. Anything that holds on to one and later compares it has to
    settle on a single spelling, or the comparison fails for exactly the values
    with their top bit set, which is half of them.
    """
    span = 1 << bits
    value &= span - 1
    return value - span if value >= span >> 1 else value
