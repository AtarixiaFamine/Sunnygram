# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the smsjobs namespace.

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


class EligibleToJoin(TLObject):
    """The TL type smsjobs.eligibleToJoin#dc8b44cf, a form of smsjobs.EligibilityToJoin."""

    __slots__ = ("terms_url", "monthly_sent_sms",)

    ID = 0xDC8B44CF
    QUALNAME = "types.smsjobs.EligibleToJoin"

    def __init__(
        self,
        *,
        terms_url: str,
        monthly_sent_sms: int,
    ) -> None:
        self.terms_url = terms_url
        self.monthly_sent_sms = monthly_sent_sms

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.terms_url)
        w.write_int(self.monthly_sent_sms)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        terms_url = r.read_string()
        monthly_sent_sms = r.read_int()
        self = cls.__new__(cls)
        self.terms_url = terms_url
        self.monthly_sent_sms = monthly_sent_sms
        return self


class Status(TLObject):
    """The TL type smsjobs.status#2aee9191, a form of smsjobs.Status."""

    __slots__ = ("allow_international", "recent_sent", "recent_since", "recent_remains", "total_sent", "total_since", "last_gift_slug", "terms_url",)

    ID = 0x2AEE9191
    QUALNAME = "types.smsjobs.Status"

    def __init__(
        self,
        *,
        allow_international: bool = False,
        recent_sent: int,
        recent_since: int,
        recent_remains: int,
        total_sent: int,
        total_since: int,
        last_gift_slug: str | None = None,
        terms_url: str,
    ) -> None:
        self.allow_international = allow_international
        self.recent_sent = recent_sent
        self.recent_since = recent_since
        self.recent_remains = recent_remains
        self.total_sent = total_sent
        self.total_since = total_since
        self.last_gift_slug = last_gift_slug
        self.terms_url = terms_url

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.allow_international:
            flags |= 1 << 0
        if self.last_gift_slug is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_int(self.recent_sent)
        w.write_int(self.recent_since)
        w.write_int(self.recent_remains)
        w.write_int(self.total_sent)
        w.write_int(self.total_since)
        if self.last_gift_slug is not None:
            w.write_string(self.last_gift_slug)
        w.write_string(self.terms_url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        allow_international = bool(flags & (1 << 0))
        recent_sent = r.read_int()
        recent_since = r.read_int()
        recent_remains = r.read_int()
        total_sent = r.read_int()
        total_since = r.read_int()
        last_gift_slug = r.read_string() if flags & (1 << 1) else None
        terms_url = r.read_string()
        self = cls.__new__(cls)
        self.allow_international = allow_international
        self.recent_sent = recent_sent
        self.recent_since = recent_since
        self.recent_remains = recent_remains
        self.total_sent = total_sent
        self.total_since = total_since
        self.last_gift_slug = last_gift_slug
        self.terms_url = terms_url
        return self
