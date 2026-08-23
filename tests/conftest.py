"""Shared scaffolding for the offline test suite."""

from __future__ import annotations

from typing import Self

from sunnygram.tl import TLObject, TLReader, TLWriter


def xor(left: bytes, right: bytes) -> bytes:
    """Byte-wise xor, kept independent of how the library does it."""
    return bytes(a ^ b for a, b in zip(left, right))


class Point(TLObject):
    """A toy constructor, enough to exercise boxing and nesting."""

    ID = 0x50494E54
    QUALNAME = "Point"

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.x)
        w.write_int(self.y)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        return cls(r.read_int(), r.read_int())
