# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the fragment namespace.

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


class CollectibleInfo(TLObject):
    """The TL type fragment.collectibleInfo#6ebdff91, a form of fragment.CollectibleInfo."""

    __slots__ = ("purchase_date", "currency", "amount", "crypto_currency", "crypto_amount", "url",)

    ID = 0x6EBDFF91
    QUALNAME = "types.fragment.CollectibleInfo"

    def __init__(
        self,
        *,
        purchase_date: int,
        currency: str,
        amount: int,
        crypto_currency: str,
        crypto_amount: int,
        url: str,
    ) -> None:
        self.purchase_date = purchase_date
        self.currency = currency
        self.amount = amount
        self.crypto_currency = crypto_currency
        self.crypto_amount = crypto_amount
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.purchase_date)
        w.write_string(self.currency)
        w.write_long(self.amount)
        w.write_string(self.crypto_currency)
        w.write_long(self.crypto_amount)
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        purchase_date = r.read_int()
        currency = r.read_string()
        amount = r.read_long()
        crypto_currency = r.read_string()
        crypto_amount = r.read_long()
        url = r.read_string()
        self = cls.__new__(cls)
        self.purchase_date = purchase_date
        self.currency = currency
        self.amount = amount
        self.crypto_currency = crypto_currency
        self.crypto_amount = crypto_amount
        self.url = url
        return self
