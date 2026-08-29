# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The binary codec for Telegram's Type Language.

Everything on the wire is TL: a little-endian format built from a handful of
primitives, where an object is a four byte constructor id followed by its
fields. This module is the hand-written half of layer 0. The constructors
themselves live in the generated raw package and read and write themselves
through the reader and writer defined here.

Reading is deliberately strict. The bytes come off a socket, so a length that
runs past the end of the buffer, a vector claiming more items than could
possibly fit, or a constructor no one knows raises instead of guessing.

Three conventions the generated code depends on:

* write() emits the constructor id and then the body, so writing an object
  always produces its boxed form. A generated class implements write_body and
  inherits write.
* read() is called after the id has already been consumed, because the reader
  needs the id to pick the class in the first place. So read and write_body are
  the two halves that line up.
* A few schema fields are bare: no constructor id, and for a vector no vector id
  either. That is what the boxed argument on the vector methods is for.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, Self, TypeVar

from ..errors import (
    TLDeserializationError,
    TLSerializationError,
    UnknownConstructorError,
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

Buffer = bytes | bytearray | memoryview

# What a function is answered with. A generated function names its own result
# as this parameter, so invoking one returns that type instead of Any.
#
# Covariant because the parameter is only ever something a call gives back. A
# function answered with Bool really is a function answered with an object, and
# without this a caller that widens what it does with the answer, bool(...)
# being the common one, cannot pass its own request in.
TLResult = TypeVar("TLResult", covariant=True)

BOOL_TRUE = 0x997275B5
BOOL_FALSE = 0xBC799737
VECTOR = 0x1CB5C415
GZIP_PACKED = 0x3072CFA1

# A compressed payload that expands past this is treated as hostile, not
# decompressed. Real traffic stays far below it: the largest legitimate blobs
# are difference batches and file chunks.
MAX_UNPACKED_SIZE = 64 * 1024 * 1024

_INT = struct.Struct("<i")
_UINT = struct.Struct("<I")
_LONG = struct.Struct("<q")
_DOUBLE = struct.Struct("<d")


class TLReader:
    """A cursor over a buffer of TL encoded bytes.

    Every read is bounds-checked before it touches the buffer, so a malformed
    or truncated payload raises TLDeserializationError instead of returning
    something half-built.
    """

    __slots__ = ("_data", "_pos", "_end")

    def __init__(self, data: Buffer) -> None:
        self._data = memoryview(data)
        self._pos = 0
        self._end = len(self._data)

    @property
    def pos(self) -> int:
        """How many bytes have been consumed so far."""
        return self._pos

    @property
    def remaining(self) -> int:
        """How many bytes are left to read."""
        return self._end - self._pos

    def _take(self, count: int) -> int:
        """Reserve count bytes and return the offset they start at."""
        pos = self._pos
        end = pos + count
        if count < 0 or end > self._end:
            raise TLDeserializationError(
                f"truncated payload: wanted {count} bytes at offset {pos}, "
                f"{self._end - pos} available"
            )
        self._pos = end
        return pos

    # The three fixed-width readers below do their own bounds check instead of
    # going through _take. It is the same check spelled out, and it reads worse,
    # but reading an int is the single most frequent thing this library does: a
    # message of any size is a hundred of them, so the call it saves is worth
    # more here than the tidiness is.
    def read_int(self, signed: bool = True) -> int:
        pos = self._pos
        end = pos + 4
        if end > self._end:
            raise TLDeserializationError(
                f"truncated payload: wanted 4 bytes at offset {pos}, "
                f"{self._end - pos} available"
            )
        self._pos = end
        value: int = (_INT if signed else _UINT).unpack_from(self._data, pos)[0]
        return value

    def read_long(self) -> int:
        pos = self._pos
        end = pos + 8
        if end > self._end:
            raise TLDeserializationError(
                f"truncated payload: wanted 8 bytes at offset {pos}, "
                f"{self._end - pos} available"
            )
        self._pos = end
        value: int = _LONG.unpack_from(self._data, pos)[0]
        return value

    def read_double(self) -> float:
        pos = self._pos
        end = pos + 8
        if end > self._end:
            raise TLDeserializationError(
                f"truncated payload: wanted 8 bytes at offset {pos}, "
                f"{self._end - pos} available"
            )
        self._pos = end
        value: float = _DOUBLE.unpack_from(self._data, pos)[0]
        return value

    def read_int128(self) -> int:
        pos = self._take(16)
        return int.from_bytes(self._data[pos : pos + 16], "little", signed=True)

    def read_int256(self) -> int:
        pos = self._take(32)
        return int.from_bytes(self._data[pos : pos + 32], "little", signed=True)

    def read_raw(self, count: int) -> bytes:
        """Read count bytes with no length prefix and no padding."""
        pos = self._take(count)
        # tobytes rather than bytes(), which builds a memoryview for the slice
        # and then copies out of it. Same answer, one object instead of two.
        return self._data[pos : pos + count].tobytes()

    def read_bytes(self) -> bytes:
        """Read a length-prefixed byte string, padded to a four byte boundary."""
        length = self._data[self._take(1)]
        if length == 254:
            pos = self._take(3)
            length = int.from_bytes(self._data[pos : pos + 3], "little")
            padding = -length % 4
        elif length == 255:
            raise TLDeserializationError("0xff is not a valid TL length prefix")
        else:
            padding = -(length + 1) % 4
        pos = self._take(length + padding)
        return self._data[pos : pos + length].tobytes()

    def read_string(self) -> str:
        data = self.read_bytes()
        try:
            return data.decode()
        except UnicodeDecodeError as exc:
            raise TLDeserializationError("string is not valid utf-8") from exc

    def read_bool(self) -> bool:
        value = self.read_int(signed=False)
        if value == BOOL_TRUE:
            return True
        if value == BOOL_FALSE:
            return False
        raise TLDeserializationError(f"expected a Bool, got 0x{value:08x}")

    def read_vector(
        self,
        item: Callable[[TLReader], Any] | None = None,
        *,
        boxed: bool = True,
    ) -> list[Any]:
        """Read a vector.

        item reads one element and defaults to reading a boxed object, so a
        vector of longs is read with TLReader.read_long and a vector of some
        generated type with that type's read. Pass boxed=False for the bare
        spelling, which carries no vector constructor id.
        """
        if boxed:
            constructor_id = self.read_int(signed=False)
            if constructor_id != VECTOR:
                raise TLDeserializationError(
                    f"expected a Vector, got 0x{constructor_id:08x}"
                )
        return self._read_vector_body(item)

    def _read_vector_body(self, item: Callable[[TLReader], Any] | None) -> list[Any]:
        count = self.read_int()
        # Every TL value is at least four bytes, so a count past that ratio can
        # never be honest. Checking it here keeps a bogus length from having us
        # build a huge list before the buffer runs out.
        if count < 0 or count > self.remaining // 4:
            raise TLDeserializationError(
                f"vector claims {count} items but only {self.remaining} bytes remain"
            )
        code = _BULK.get(item)
        if code is not None:
            # A vector of one fixed-width primitive has a layout that is known
            # from the count, so the whole run comes out of one struct call
            # instead of one Python call per item. Measured about 10x on a
            # thousand longs and level at four, which is the end that matters:
            # the common vector is a handful of ids and pays nothing either way.
            # The bounds check is the same one, done once over the whole span
            # rather than per item, so rule S3 is unchanged.
            letter, width = code
            pos = self._take(count * width)
            return list(struct.unpack_from(f"<{count}{letter}", self._data, pos))
        read = TLReader.read_object if item is None else item
        return [read(self) for _ in range(count)]

    def read_object(self) -> Any:
        """Read a boxed value: a constructor id followed by its body."""
        pos = self._pos
        end = pos + 4
        if end > self._end:
            raise TLDeserializationError(
                f"truncated payload: wanted 4 bytes at offset {pos}, "
                f"{self._end - pos} available"
            )
        self._pos = end
        constructor_id: int = _UINT.unpack_from(self._data, pos)[0]
        if constructor_id == VECTOR:
            return self._read_vector_body(None)
        if constructor_id == BOOL_TRUE:
            return True
        if constructor_id == BOOL_FALSE:
            return False
        if constructor_id == GZIP_PACKED:
            return TLReader(unpack_gzip(self.read_bytes())).read_object()
        # The table is consulted here instead of through resolve_constructor,
        # which is kept for the miss. Every object after the first of its type
        # is a hit, and this runs once per object on the wire. The four checks
        # above still come first: they are what says these ids are the codec's
        # and not a class's, whatever a later schema might name.
        cls = _constructors.get(constructor_id)
        if cls is None:
            cls = resolve_constructor(constructor_id)
        return cls.read(self)


# The item readers a vector can be read in one piece with, and the struct
# letter and width for each. Keyed by the function itself because that is what
# the generated code passes: a vector of longs is read_vector(TLReader.read_long)
# and nothing else has to know about this. read_bytes and read_string are absent
# on purpose, since neither is fixed width.
_BULK: dict[Any, tuple[str, int]] = {
    TLReader.read_int: ("i", 4),
    TLReader.read_long: ("q", 8),
    TLReader.read_double: ("d", 8),
}


class TLWriter:
    """A growing buffer that TL values are appended to.

    One bytearray is reused for a whole message so serializing an object with
    many fields does not build an intermediate bytes object per field.
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        self._buf = bytearray()

    def __len__(self) -> int:
        return len(self._buf)

    def getvalue(self) -> bytes:
        return bytes(self._buf)

    def write_int(self, value: int, signed: bool = True) -> None:
        try:
            self._buf += (_INT if signed else _UINT).pack(value)
        except struct.error as exc:
            raise TLSerializationError(f"{value} does not fit in a TL int") from exc

    def write_long(self, value: int) -> None:
        self._write_wide(value, 8)

    def write_double(self, value: float) -> None:
        self._buf += _DOUBLE.pack(value)

    def write_int128(self, value: int) -> None:
        self._write_wide(value, 16)

    def write_int256(self, value: int) -> None:
        self._write_wide(value, 32)

    def _write_wide(self, value: int, size: int) -> None:
        """Write a long, int128 or int256, in either spelling.

        These carry ids, salts, nonces and hashes: opaque patterns that get
        generated unsigned and read back signed. Both name the same bytes, so
        both are accepted, and only a value too wide to be either is refused.
        """
        width = size * 8
        if not -(1 << (width - 1)) <= value < (1 << width):
            raise TLSerializationError(f"{value} does not fit in a TL int{width}")
        self._buf += (value & ((1 << width) - 1)).to_bytes(size, "little")

    def write_raw(self, value: Buffer) -> None:
        """Append bytes as they are, with no length prefix and no padding."""
        self._buf += value

    def write_bytes(self, value: Buffer) -> None:
        """Append a length-prefixed byte string, padded to a four byte boundary."""
        length = len(value)
        if length <= 253:
            self._buf.append(length)
            padding = -(length + 1) % 4
        elif length <= 0xFFFFFF:
            self._buf.append(254)
            self._buf += length.to_bytes(3, "little")
            padding = -length % 4
        else:
            raise TLSerializationError(
                f"byte string of {length} bytes exceeds the TL length limit"
            )
        self._buf += value
        self._buf += bytes(padding)

    def write_string(self, value: str) -> None:
        self.write_bytes(value.encode())

    def write_bool(self, value: bool) -> None:
        self.write_int(BOOL_TRUE if value else BOOL_FALSE, signed=False)

    def write_vector(
        self,
        values: list[Any] | tuple[Any, ...],
        item: Callable[[TLWriter, Any], None] | None = None,
        *,
        boxed: bool = True,
    ) -> None:
        """Write a vector.

        item writes one element and mirrors the reader's argument: pass
        TLWriter.write_long for a vector of longs, or leave it out to write
        each element boxed. boxed=False omits the vector constructor id.
        """
        if boxed:
            self.write_int(VECTOR, signed=False)
        self.write_int(len(values))
        write = TLWriter.write_object if item is None else item
        for value in values:
            write(self, value)

    def write_object(self, value: Any) -> None:
        """Write a boxed value: a TL object or a Bool."""
        if isinstance(value, TLObject):
            value.write(self)
        elif isinstance(value, bool):
            self.write_bool(value)
        else:
            raise TLSerializationError(
                f"{type(value).__name__} is not a boxed TL value"
            )


_constructors: dict[int, type[TLObject]] = {}
_resolver: Callable[[int], type[TLObject] | None] | None = None


class TLObject:
    """Base class for every TL constructor and function.

    Subclasses set ID to their constructor id and implement the two halves of
    the codec. Defining a subclass with an id registers it, so a hand-written
    type is readable the moment its module is imported.
    """

    __slots__ = ()

    ID: ClassVar[int] = 0
    QUALNAME: ClassVar[str] = "TLObject"

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.ID:
            _constructors[cls.ID] = cls

    def _fields(self) -> Iterator[tuple[str, Any]]:
        for cls in reversed(type(self).__mro__):
            for name in getattr(cls, "__slots__", ()):
                yield name, getattr(self, name)

    def __repr__(self) -> str:
        # Defined once here rather than generated onto thousands of classes.
        fields = ", ".join(f"{name}={value!r}" for name, value in self._fields())
        return f"{type(self).__name__}({fields})"

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return all(
            value == getattr(other, name) for name, value in self._fields()
        )

    def __hash__(self) -> int:
        # Defining __eq__ drops the inherited __hash__, which would leave every
        # constructor in the generated layer unhashable: no set of peers, no
        # dict keyed by a message. Hashing on the type and the fields that can
        # be hashed keeps it consistent with __eq__, since two equal objects
        # agree on all of them. A field that is itself a list, which is what a
        # vector deserializes to, is skipped instead of converted: it would
        # cost a copy on every hash, and the fields left are more than enough
        # to spread the buckets.
        return hash(
            (type(self),)
            + tuple(
                value
                for _, value in self._fields()
                if isinstance(value, (int, str, bytes, bool, float, type(None)))
            )
        )

    def write(self, w: TLWriter) -> None:
        """Append this object boxed: constructor id, then body."""
        w.write_int(self.ID, signed=False)
        self.write_body(w)

    def write_body(self, w: TLWriter) -> None:
        """Append this object's fields, with no constructor id."""
        raise NotImplementedError

    @classmethod
    def read(cls, r: TLReader) -> Self:
        """Read this object's body. The constructor id is already consumed."""
        raise NotImplementedError

    def to_bytes(self) -> bytes:
        w = TLWriter()
        self.write(w)
        return w.getvalue()

    @classmethod
    def from_bytes(cls, data: Buffer) -> Self:
        r = TLReader(data)
        constructor_id = r.read_int(signed=False)
        if constructor_id != cls.ID:
            raise TLDeserializationError(
                f"expected {cls.QUALNAME} (0x{cls.ID:08x}), "
                f"got 0x{constructor_id:08x}"
            )
        return cls.read(r)


class TLFunction(TLObject, Generic[TLResult]):
    """Base class for the TL functions, the things a client can invoke.

    The parameter is what the server answers with, so a generated function is
    declared as TLFunction["base.Config"] and invoking it gives back a Config
    instead of Any. That is the whole reason this class is generic: the schema
    knows every function's result, and there is no reason for a caller to be
    told less than the schema knows.

    RESULT names the same type as a string. It stays because it is the runtime
    spelling of the fact, readable without a type checker, and the docs use it.

    Subscripting is free at runtime. A type checker reads the Generic base and
    resolves the parameter, while the override below hands back the class
    itself, so building a thousand generated classes allocates no typing
    machinery and importing the raw package stays as cheap as rule P7 wants.
    The parameter is a forward reference to raw.base, which exists only for
    type checkers, so evaluating it would fail in any case.
    """

    __slots__ = ()

    RESULT: ClassVar[str] = ""

    if not TYPE_CHECKING:

        def __class_getitem__(cls, item: Any) -> Any:
            return cls


# The two answer shapes the bytes cannot describe on their own. Every other
# vector an RPC answers with holds boxed elements, which say what they are; a
# Vector<int> or a Vector<long> is the vector id followed by bare numbers.
_BARE_RESULTS: dict[str, Callable[[TLReader], Any]] = {
    "Vector<int>": TLReader.read_int,
    "Vector<long>": TLReader.read_long,
}


def read_answer(reader: TLReader, result: str) -> Any:
    """Read what a call answered with, told what to expect.

    Almost every answer describes itself: the constructor id comes first and
    the reader looks it up, which is why nothing else in the codec needs to
    know what was asked. Two results do not describe themselves. A Vector<int>
    or Vector<long> is the vector id and then bare numbers, and read as though
    those were boxed the number three is an unknown constructor 0x00000003.

    So the answer is read with the called function's RESULT in hand. That is
    the only thing that knows, and it costs nothing: every other result goes
    down the ordinary path.
    """
    item = _BARE_RESULTS.get(result)
    if item is None:
        return reader.read_object()
    constructor_id = reader.read_int(signed=False)
    if constructor_id == GZIP_PACKED:
        return read_answer(TLReader(unpack_gzip(reader.read_bytes())), result)
    if constructor_id != VECTOR:
        raise TLDeserializationError(
            f"expected a vector for {result}, got 0x{constructor_id:08x}"
        )
    return reader.read_vector(item, boxed=False)


def set_constructor_resolver(
    resolver: Callable[[int], type[TLObject] | None] | None,
) -> None:
    """Install the fallback used when an id has no imported class yet.

    The generated raw package holds thousands of constructors, so importing it
    eagerly would make importing sunnygram expensive. Instead it registers a
    resolver that imports the one module an id needs, and the result is cached.
    """
    global _resolver
    _resolver = resolver


def resolve_constructor(constructor_id: int) -> type[TLObject]:
    """Find the class for a constructor id, or raise if nothing claims it."""
    cls = _constructors.get(constructor_id)
    if cls is None and _resolver is not None:
        cls = _resolver(constructor_id)
        if cls is not None:
            _constructors[constructor_id] = cls
    if cls is None:
        raise UnknownConstructorError(constructor_id)
    return cls


def unpack_gzip(data: bytes) -> bytes:
    """Inflate a gzip_packed payload, refusing anything absurdly large."""
    engine = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        unpacked = engine.decompress(data, MAX_UNPACKED_SIZE)
    except zlib.error as exc:
        raise TLDeserializationError("gzip_packed payload is not valid gzip") from exc
    if engine.unconsumed_tail:
        raise TLDeserializationError(
            f"gzip_packed payload expands past {MAX_UNPACKED_SIZE} bytes"
        )
    return unpacked
