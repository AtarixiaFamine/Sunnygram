"""The TL codec: round trips, the wire format itself, and hostile input."""

from __future__ import annotations

import gzip
import struct

import pytest
from conftest import Point

from sunnygram.errors import (
    TLDeserializationError,
    TLSerializationError,
    UnknownConstructorError,
)
from sunnygram.tl import (
    BOOL_TRUE,
    GZIP_PACKED,
    VECTOR,
    TLObject,
    TLReader,
    TLWriter,
    read_answer,
    resolve_constructor,
    set_constructor_resolver,
)
from sunnygram.tl import core


class TestPrimitives:
    def test_int_round_trip(self):
        w = TLWriter()
        w.write_int(0)
        w.write_int(-1)
        w.write_int(2147483647)
        w.write_int(4294967295, signed=False)
        r = TLReader(w.getvalue())
        assert r.read_int() == 0
        assert r.read_int() == -1
        assert r.read_int() == 2147483647
        assert r.read_int(signed=False) == 4294967295
        assert r.remaining == 0

    def test_int_is_little_endian(self):
        w = TLWriter()
        w.write_int(1)
        assert w.getvalue() == b"\x01\x00\x00\x00"

    def test_long_round_trip(self):
        w = TLWriter()
        w.write_long(-9223372036854775808)
        w.write_long(9223372036854775807)
        r = TLReader(w.getvalue())
        assert r.read_long() == -9223372036854775808
        assert r.read_long() == 9223372036854775807

    def test_double_round_trip(self):
        w = TLWriter()
        w.write_double(-0.5)
        assert TLReader(w.getvalue()).read_double() == -0.5

    def test_wide_ints_round_trip(self):
        w = TLWriter()
        w.write_int128(-1)
        w.write_int128(2**126)
        w.write_int256(2**254)
        r = TLReader(w.getvalue())
        assert r.read_int128() == -1
        assert r.read_int128() == 2**126
        assert r.read_int256() == 2**254

    def test_bool_round_trip(self):
        w = TLWriter()
        w.write_bool(True)
        w.write_bool(False)
        r = TLReader(w.getvalue())
        assert r.read_bool() is True
        assert r.read_bool() is False

    def test_raw_bytes_are_not_padded(self):
        w = TLWriter()
        w.write_raw(b"abc")
        assert w.getvalue() == b"abc"
        assert TLReader(b"abc").read_raw(3) == b"abc"

    def test_position_tracking(self):
        r = TLReader(b"\x01\x00\x00\x00\x02\x00\x00\x00")
        assert (r.pos, r.remaining) == (0, 8)
        r.read_int()
        assert (r.pos, r.remaining) == (4, 4)

    def test_oversized_int_refuses_to_serialize(self):
        with pytest.raises(TLSerializationError):
            TLWriter().write_int(2**31)
        with pytest.raises(TLSerializationError):
            TLWriter().write_long(2**64)
        with pytest.raises(TLSerializationError):
            TLWriter().write_int128(2**128)
        with pytest.raises(TLSerializationError):
            TLWriter().write_int256(2**256)

    @pytest.mark.parametrize(
        "write,bits",
        [
            (TLWriter.write_long, 64),
            (TLWriter.write_int128, 128),
            (TLWriter.write_int256, 256),
        ],
    )
    def test_a_wide_value_may_be_spelled_either_way(self, write, bits):
        # These carry ids, salts and nonces, which come from a random source
        # unsigned and come back off the wire signed. Both name the same bytes.
        for unsigned in (1 << (bits - 1), (1 << bits) - 1, (1 << bits) - 12345):
            signed_form = unsigned - (1 << bits)
            one, other = TLWriter(), TLWriter()
            write(one, unsigned)
            write(other, signed_form)
            assert one.getvalue() == other.getvalue()


class TestByteStrings:
    @pytest.mark.parametrize("length", [0, 1, 2, 3, 4, 7, 8, 100, 253, 254, 255, 1000])
    def test_round_trip_and_alignment(self, length):
        value = bytes(range(256)) * 4
        value = value[:length]
        w = TLWriter()
        w.write_bytes(value)
        encoded = w.getvalue()
        assert len(encoded) % 4 == 0
        assert TLReader(encoded).read_bytes() == value

    def test_short_form_for_253_bytes(self):
        w = TLWriter()
        w.write_bytes(b"x" * 253)
        assert w.getvalue()[0] == 253

    def test_long_form_past_253_bytes(self):
        w = TLWriter()
        w.write_bytes(b"x" * 254)
        encoded = w.getvalue()
        assert encoded[0] == 254
        assert int.from_bytes(encoded[1:4], "little") == 254

    def test_two_strings_stay_aligned(self):
        w = TLWriter()
        w.write_bytes(b"ab")
        w.write_bytes(b"cde")
        r = TLReader(w.getvalue())
        assert r.read_bytes() == b"ab"
        assert r.read_bytes() == b"cde"

    def test_string_round_trip(self):
        w = TLWriter()
        w.write_string("ciao \U0001f31e")
        assert TLReader(w.getvalue()).read_string() == "ciao \U0001f31e"

    def test_invalid_utf8_fails_closed(self):
        w = TLWriter()
        w.write_bytes(b"\xff\xfe")
        with pytest.raises(TLDeserializationError):
            TLReader(w.getvalue()).read_string()

    def test_reserved_length_prefix_is_rejected(self):
        with pytest.raises(TLDeserializationError):
            TLReader(b"\xff\x00\x00\x00").read_bytes()

    def test_length_past_the_buffer_is_rejected(self):
        with pytest.raises(TLDeserializationError):
            TLReader(b"\x40abc").read_bytes()

    def test_long_form_length_past_the_buffer_is_rejected(self):
        payload = b"\xfe" + (10**6).to_bytes(3, "little") + b"abc"
        with pytest.raises(TLDeserializationError):
            TLReader(payload).read_bytes()


class TestVectors:
    def test_typed_vector_round_trip(self):
        w = TLWriter()
        w.write_vector([1, 2, 3], TLWriter.write_long)
        r = TLReader(w.getvalue())
        assert r.read_vector(TLReader.read_long) == [1, 2, 3]

    def test_boxed_vector_round_trip(self):
        w = TLWriter()
        w.write_vector([Point(1, 2), Point(3, 4)])
        r = TLReader(w.getvalue())
        assert r.read_vector() == [Point(1, 2), Point(3, 4)]

    def test_empty_vector(self):
        w = TLWriter()
        w.write_vector([], TLWriter.write_int)
        assert TLReader(w.getvalue()).read_vector(TLReader.read_int) == []

    def test_vector_of_bools(self):
        w = TLWriter()
        w.write_vector([True, False])
        assert TLReader(w.getvalue()).read_object() == [True, False]

    def test_wrong_constructor_is_rejected(self):
        w = TLWriter()
        w.write_int(BOOL_TRUE, signed=False)
        with pytest.raises(TLDeserializationError):
            TLReader(w.getvalue()).read_vector()

    def test_impossible_count_is_rejected(self):
        w = TLWriter()
        w.write_int(VECTOR, signed=False)
        w.write_int(10**8)
        w.write_int(1)
        with pytest.raises(TLDeserializationError, match="items"):
            TLReader(w.getvalue()).read_vector(TLReader.read_int)

    def test_negative_count_is_rejected(self):
        w = TLWriter()
        w.write_int(VECTOR, signed=False)
        w.write_int(-1)
        with pytest.raises(TLDeserializationError):
            TLReader(w.getvalue()).read_vector(TLReader.read_int)

    @pytest.mark.parametrize(
        "reader, writer, values",
        [
            (TLReader.read_int, TLWriter.write_int, [-2**31, -1, 0, 7, 2**31 - 1]),
            (TLReader.read_long, TLWriter.write_long, [-(2**63), 0, 2**63 - 1]),
            (TLReader.read_double, TLWriter.write_double, [-1.5, 0.0, 3.25]),
        ],
    )
    @pytest.mark.parametrize("repeats", [0, 1, 2, 500])
    def test_a_vector_of_one_primitive_reads_whole(self, reader, writer, values, repeats):
        # These take the one-struct-call path instead of one read per item, so
        # the edges of every width are worth going over: the path is only a fast
        # path if it agrees with the slow one everywhere.
        wanted = (values * repeats)[: len(values) * repeats]
        w = TLWriter()
        w.write_vector(wanted, writer)
        assert TLReader(w.getvalue()).read_vector(reader) == wanted

    def test_a_truncated_primitive_vector_still_raises(self):
        w = TLWriter()
        w.write_vector([1, 2, 3], TLWriter.write_long)
        truncated = w.getvalue()[:-6]
        with pytest.raises(TLDeserializationError, match="truncated"):
            TLReader(truncated).read_vector(TLReader.read_long)

    def test_a_vector_of_bytes_is_not_taken_for_a_fixed_width_one(self):
        w = TLWriter()
        w.write_vector([b"a", b"bb", b"ccc"], TLWriter.write_bytes)
        assert TLReader(w.getvalue()).read_vector(TLReader.read_bytes) == [
            b"a",
            b"bb",
            b"ccc",
        ]


class TestObjects:
    def test_write_emits_the_constructor_id_first(self):
        assert Point(1, 2).to_bytes()[:4] == struct.pack("<I", Point.ID)

    def test_boxed_round_trip(self):
        assert TLReader(Point(7, 8).to_bytes()).read_object() == Point(7, 8)

    def test_from_bytes_checks_the_id(self):
        assert Point.from_bytes(Point(1, 2).to_bytes()) == Point(1, 2)
        with pytest.raises(TLDeserializationError):
            Point.from_bytes(struct.pack("<Iii", 0xDEADBEEF, 1, 2))

    def test_nested_objects(self):
        w = TLWriter()
        w.write_vector([Point(1, 2)])
        w.write_object(Point(3, 4))
        r = TLReader(w.getvalue())
        assert r.read_vector() == [Point(1, 2)]
        assert r.read_object() == Point(3, 4)

    def test_defining_a_subclass_registers_it(self):
        assert resolve_constructor(Point.ID) is Point

    def test_unknown_constructor_is_rejected(self):
        with pytest.raises(UnknownConstructorError) as info:
            TLReader(struct.pack("<I", 0xDEADBEEF)).read_object()
        assert info.value.constructor_id == 0xDEADBEEF

    def test_resolver_fills_in_and_is_cached(self):
        calls = []

        def resolver(constructor_id):
            calls.append(constructor_id)
            return Point if constructor_id == 0x0BADF00D else None

        set_constructor_resolver(resolver)
        try:
            assert resolve_constructor(0x0BADF00D) is Point
            assert resolve_constructor(0x0BADF00D) is Point
            assert calls == [0x0BADF00D]
            with pytest.raises(UnknownConstructorError):
                resolve_constructor(0x0BADCAFE)
        finally:
            set_constructor_resolver(None)
            core._constructors.pop(0x0BADF00D, None)

    def test_unboxed_value_refuses_to_serialize(self):
        with pytest.raises(TLSerializationError):
            TLWriter().write_object(42)

    def test_base_class_has_no_codec(self):
        with pytest.raises(NotImplementedError):
            TLObject().write(TLWriter())
        with pytest.raises(NotImplementedError):
            TLObject.read(TLReader(b""))


class TestGzipPacked:
    def _packed(self, payload: bytes) -> bytes:
        w = TLWriter()
        w.write_int(GZIP_PACKED, signed=False)
        w.write_bytes(gzip.compress(payload))
        return w.getvalue()

    def test_unpacked_transparently(self):
        packed = self._packed(Point(9, 10).to_bytes())
        assert TLReader(packed).read_object() == Point(9, 10)

    def test_garbage_is_rejected(self):
        w = TLWriter()
        w.write_int(GZIP_PACKED, signed=False)
        w.write_bytes(b"not gzip at all")
        with pytest.raises(TLDeserializationError):
            TLReader(w.getvalue()).read_object()

    def test_oversized_expansion_is_rejected(self, monkeypatch):
        monkeypatch.setattr(core, "MAX_UNPACKED_SIZE", 64)
        packed = self._packed(bytes(4096))
        with pytest.raises(TLDeserializationError, match="expands past"):
            TLReader(packed).read_object()


class TestHashing:
    """Defining __eq__ drops the inherited __hash__, and a whole generated layer
    that cannot go in a set is a surprise nobody should have to discover."""

    def test_a_constructor_can_go_in_a_set(self):
        assert len({Point(1, 2), Point(1, 2), Point(3, 4)}) == 2

    def test_a_constructor_can_key_a_dict(self):
        seen = {Point(1, 2): "first"}
        seen[Point(1, 2)] = "second"
        assert seen == {Point(1, 2): "second"}

    def test_equal_objects_hash_alike(self):
        assert hash(Point(7, 8)) == hash(Point(7, 8))

    def test_a_vector_field_does_not_make_it_unhashable(self):
        # A vector deserializes to a list, which is unhashable. Skipping those
        # fields is what keeps every constructor carrying one usable in a set,
        # at the cost of two objects differing only in a vector colliding.

        class WithVector(TLObject):
            ID = 0x57495456
            QUALNAME = "WithVector"

            __slots__ = ("items", "label")

            def __init__(self, items: list[int], label: str) -> None:
                self.items = items
                self.label = label

        assert hash(WithVector([1, 2, 3], "a")) == hash(WithVector([9], "a"))
        assert WithVector([1, 2, 3], "a") != WithVector([9], "a")


class TestReadingAnAnswer:
    """The two results whose bytes do not say what they are.

    Every other answer starts with a constructor id the reader can look up. A
    Vector<int> is the vector id and then bare numbers, so read as boxed
    objects the number three is "unknown constructor 0x00000003". This was
    latent for as long as nothing called one of the handful of methods that
    answer this way, which is the shape of fault this suite exists to refuse.
    """

    def _vector_of_ints(self, values):
        writer = TLWriter()
        writer.write_vector(values, TLWriter.write_int)
        return writer.getvalue()

    def test_a_vector_of_ints_read_without_being_told_fails(self):
        # The fault itself, so the fix is pinned to a real failure rather than
        # to an assertion that would pass either way.
        reader = TLReader(self._vector_of_ints([3, 4]))
        with pytest.raises(UnknownConstructorError):
            reader.read_object()

    def test_a_vector_of_ints_read_with_its_result_works(self):
        reader = TLReader(self._vector_of_ints([3, 4, 5]))
        assert read_answer(reader, "Vector<int>") == [3, 4, 5]

    def test_an_empty_one_is_an_empty_list(self):
        reader = TLReader(self._vector_of_ints([]))
        assert read_answer(reader, "Vector<int>") == []

    def test_a_vector_of_longs_too(self):
        writer = TLWriter()
        writer.write_vector([2**40, -1], TLWriter.write_long)
        assert read_answer(TLReader(writer.getvalue()), "Vector<long>") == [2**40, -1]

    def test_a_gzipped_one_is_unpacked_first(self):
        packed = TLWriter()
        packed.write_int(GZIP_PACKED, signed=False)
        packed.write_bytes(gzip.compress(self._vector_of_ints([1, 2])))
        assert read_answer(TLReader(packed.getvalue()), "Vector<int>") == [1, 2]

    def test_something_that_is_not_a_vector_says_so(self):
        writer = TLWriter()
        writer.write_int(BOOL_TRUE, signed=False)
        with pytest.raises(TLDeserializationError, match="expected a vector"):
            read_answer(TLReader(writer.getvalue()), "Vector<int>")

    def test_every_other_result_goes_the_ordinary_way(self):
        """A boxed vector of objects is not this case and must not become it."""
        writer = TLWriter()
        writer.write_vector([Point(1, 2)])
        assert read_answer(TLReader(writer.getvalue()), "Vector<Point>") == [Point(1, 2)]

    def test_and_so_does_a_plain_object(self):
        assert read_answer(TLReader(Point(3, 4).to_bytes()), "Point") == Point(3, 4)
