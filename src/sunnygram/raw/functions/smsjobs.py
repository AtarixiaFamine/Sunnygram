# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the smsjobs namespace.

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
    from .. import base  # noqa: F401


class IsEligibleToJoin(TLFunction["base.smsjobs.EligibilityToJoin"]):
    """The TL function smsjobs.isEligibleToJoin#0edc39d0, answered with smsjobs.EligibilityToJoin."""

    __slots__ = ()

    ID = 0x0EDC39D0
    QUALNAME = "functions.smsjobs.IsEligibleToJoin"
    RESULT = "smsjobs.EligibilityToJoin"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Join(TLFunction["bool"]):
    """The TL function smsjobs.join#a74ece2d, answered with Bool."""

    __slots__ = ()

    ID = 0xA74ECE2D
    QUALNAME = "functions.smsjobs.Join"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Leave(TLFunction["bool"]):
    """The TL function smsjobs.leave#9898ad73, answered with Bool."""

    __slots__ = ()

    ID = 0x9898AD73
    QUALNAME = "functions.smsjobs.Leave"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UpdateSettings(TLFunction["bool"]):
    """The TL function smsjobs.updateSettings#093fa0bf, answered with Bool."""

    __slots__ = ("allow_international",)

    ID = 0x093FA0BF
    QUALNAME = "functions.smsjobs.UpdateSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        allow_international: bool = False,
    ) -> None:
        self.allow_international = allow_international

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.allow_international:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        allow_international = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.allow_international = allow_international
        return self


class GetStatus(TLFunction["base.smsjobs.Status"]):
    """The TL function smsjobs.getStatus#10a698e8, answered with smsjobs.Status."""

    __slots__ = ()

    ID = 0x10A698E8
    QUALNAME = "functions.smsjobs.GetStatus"
    RESULT = "smsjobs.Status"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSmsJob(TLFunction["base.SmsJob"]):
    """The TL function smsjobs.getSmsJob#778d902f, answered with SmsJob."""

    __slots__ = ("job_id",)

    ID = 0x778D902F
    QUALNAME = "functions.smsjobs.GetSmsJob"
    RESULT = "SmsJob"

    def __init__(
        self,
        *,
        job_id: str,
    ) -> None:
        self.job_id = job_id

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.job_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        job_id = r.read_string()
        self = cls.__new__(cls)
        self.job_id = job_id
        return self


class FinishJob(TLFunction["bool"]):
    """The TL function smsjobs.finishJob#4f1ebf24, answered with Bool."""

    __slots__ = ("job_id", "error",)

    ID = 0x4F1EBF24
    QUALNAME = "functions.smsjobs.FinishJob"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        job_id: str,
        error: str | None = None,
    ) -> None:
        self.job_id = job_id
        self.error = error

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.error is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.job_id)
        if self.error is not None:
            w.write_string(self.error)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        job_id = r.read_string()
        error = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.job_id = job_id
        self.error = error
        return self
