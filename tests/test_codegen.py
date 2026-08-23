"""Guards on the generated wire layer.

Five things are checked: that the vendored schema and error table are the ones
the pin names, that both committed trees are exactly what their generators
produce, that our reading of the schema still agrees with Telegram's own
constructor ids, and that the generated classes actually survive a round trip.

Nothing here reaches the network. Whether a newer layer exists upstream is a
question for codegen/refresh.py --check, and not one a test run should depend
on the answer to.
"""

from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from zlib import crc32

import pytest

from sunnygram.errors import TLSerializationError
from sunnygram.raw import LAYER, functions, types
from sunnygram.raw.all import CONSTRUCTORS, find
from sunnygram.tl import TLObject, TLReader, TLWriter

REPO = Path(__file__).resolve().parents[1]
RAW_DIR = REPO / "src" / "sunnygram" / "raw"
ERRORS_FILE = REPO / "src" / "sunnygram" / "errors" / "generated.py"
sys.path.insert(0, str(REPO / "codegen"))

import gen_errors  # noqa: E402
import gen_tl  # noqa: E402
import overrides  # noqa: E402
import parser as schema  # noqa: E402
import refresh  # noqa: E402


class TestPin:
    """That the layer we say we speak is the one we generated from."""

    def test_the_vendored_schema_is_what_the_pin_records(self):
        # A .tl edited by hand, or a record left behind by one, would otherwise
        # surface as constructor ids a server rejects for no visible reason.
        record = json.loads(
            (schema.SCHEMA_DIR / "version.json").read_text(encoding="utf-8")
        )
        assert sorted(record["files"]) == sorted(refresh.FILES)
        for name, expected in record["files"].items():
            text = (schema.SCHEMA_DIR / name).read_text(encoding="utf-8")
            assert sha256(text.encode()).hexdigest() == expected["sha256"], name
            assert text.count("\n") + 1 == expected["lines"], name

    def test_the_vendored_error_table_is_what_the_pin_records(self):
        # Same reasoning as the schema, for the other thing that is vendored.
        # An error table edited by hand would show up as a class Telegram has
        # never heard of, raised for a message no server sends.
        record = json.loads(
            (schema.SCHEMA_DIR / "version.json").read_text(encoding="utf-8")
        )["errors"]
        text = gen_errors.ERRORS_FILE.read_text(encoding="utf-8")
        assert sha256(text.encode()).hexdigest() == record["sha256"]
        table = json.loads(text)
        assert sum(len(names) for names in table["errors"].values()) == record["count"]
        assert table["layer"] == record["layer"]

    def test_the_generated_layer_is_the_pinned_one(self):
        # LAYER goes out in invokeWithLayer on every connection, so it saying
        # something other than what these constructors came from is the one
        # mismatch a server cannot forgive.
        record = json.loads(
            (schema.SCHEMA_DIR / "version.json").read_text(encoding="utf-8")
        )
        api = (schema.SCHEMA_DIR / "api.tl").read_text(encoding="utf-8")
        assert refresh.find_layer(api) == record["layer"]
        assert LAYER == record["layer"]


class TestDrift:
    def test_committed_tree_matches_the_generator(self):
        produced = gen_tl.build()
        on_disk = {
            path.relative_to(RAW_DIR).as_posix(): path.read_text(encoding="utf-8")
            for path in RAW_DIR.rglob("*.py")
        }
        assert sorted(on_disk) == sorted(produced), "the set of modules changed"
        stale = [name for name in produced if on_disk[name] != produced[name]]
        assert not stale, f"regenerate: {stale}"

    def test_every_generated_module_imports(self):
        for path in sorted(RAW_DIR.rglob("*.py")):
            relative = path.relative_to(RAW_DIR).with_suffix("")
            parts = [part for part in relative.parts if part != "__init__"]
            import_module(".".join(["sunnygram", "raw", *parts]))

    def test_the_table_covers_every_definition(self):
        expected = sum(
            1
            for definition in schema.parse_all()
            if definition.name not in overrides.EXCLUDED
        )
        assert len(CONSTRUCTORS) == expected

    def test_committed_error_tree_matches_the_generator(self):
        produced = gen_errors.emit(gen_errors.collect())
        assert ERRORS_FILE.read_text(encoding="utf-8") == produced, "regenerate errors"

    def test_every_documented_error_reaches_a_class(self):
        # The point of generating this at all: a name Telegram publishes and a
        # lookup that answers with a plain status code would be a class nobody
        # can catch, which is exactly what this replaced.
        from sunnygram.errors import RPCError, rpc_error

        table = json.loads(gen_errors.ERRORS_FILE.read_text(encoding="utf-8"))
        for code, errors in table["errors"].items():
            for name in errors:
                message = name.replace("%d", "7")
                error = rpc_error(int(code), message)
                assert type(error) is not RPCError, name
                assert error.__class__.__doc__, name
                if "%d" in name:
                    assert error.value == 7, name


class TestConstructorIds:
    def test_declared_ids_reproduce_from_the_schema(self):
        wrong = sorted(
            definition.name
            for definition in schema.parse_all()
            if definition.declared_id is not None
            and crc32(definition.signature.encode()) != definition.declared_id
            and definition.name not in overrides.ID_EXCEPTIONS
        )
        assert not wrong

    def test_every_recorded_exception_is_still_needed(self):
        still_wrong = {
            definition.name
            for definition in schema.parse_all()
            if definition.declared_id is not None
            and crc32(definition.signature.encode()) != definition.declared_id
        }
        assert overrides.ID_EXCEPTIONS <= still_wrong

    def test_classes_carry_the_id_they_are_filed_under(self):
        for constructor_id in list(CONSTRUCTORS)[::97]:
            found = find(constructor_id)
            assert found is not None
            assert found.ID == constructor_id

    def test_unknown_id_is_not_invented(self):
        assert find(0xDEADBEEF) is None


class TestLaziness:
    def test_importing_sunnygram_does_not_load_the_generated_layer(self):
        code = (
            "import sys, sunnygram; "
            "print(sorted(m for m in sys.modules if m.startswith('sunnygram.raw')))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert result.stdout.strip() == "[]"

    def test_opening_a_connection_does_not_load_the_api_schema(self):
        # What the split of the namespace-less definitions is for. A connection
        # speaks forty service constructors; the API ones that used to sit in
        # the same module are thirteen hundred, and compiling them cost the
        # better part of a second to reach the handful in use (rule P7).
        code = (
            "import sys\n"
            "from sunnygram.network import Connection\n"
            "print([m for m in sys.modules if m.startswith('sunnygram.raw')])\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert set(ast.literal_eval(result.stdout)) == {
            "sunnygram.raw",
            "sunnygram.raw.types",
            "sunnygram.raw.types.mtproto",
            "sunnygram.raw.functions",
            "sunnygram.raw.functions.mtproto",
        }

    def test_knowing_how_to_reach_a_peer_is_not_knowing_every_type(self):
        # The peer layer names a dozen generated classes. Naming one of them at
        # import time would load the module that holds all thirteen hundred, so
        # it waits until somebody actually resolves somebody (rule P7).
        code = (
            "import sys\n"
            "import sunnygram.peers\n"
            "print([m for m in sys.modules if m.startswith('sunnygram.raw')])\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert "sunnygram.raw.types._root" not in set(ast.literal_eval(result.stdout))

    def test_the_resolver_reaches_a_type_nobody_imported(self):
        code = (
            "import sunnygram\n"
            "from sunnygram.tl import TLReader\n"
            "payload = bytes.fromhex('73ad33d4') + (1).to_bytes(4, 'little')"
            " + (2).to_bytes(4, 'little')\n"
            "print(TLReader(payload).read_object())\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert result.stdout.strip() == "IpPort(ipv4=1, port=2)"


class TestRoundTrip:
    def test_a_vector_of_primitives(self):
        original = types.mtproto.ResPQ(
            nonce=1,
            server_nonce=2,
            pq=b"\x17\xed\x48\x94\x1a\x08\xf9\x81",
            server_public_key_fingerprints=[-1, 2**62],
        )
        assert _round_trip(original) == original

    def test_binary_blobs_declared_as_string(self):
        # A prime product is not utf-8, so this field has to come back as bytes
        # even though mtproto.tl calls it a string.
        assert types.mtproto.ResPQ.__init__.__annotations__["pq"] == "bytes"
        original = functions.mtproto.ReqDHParams(
            nonce=1,
            server_nonce=2,
            p=b"\xff\xfe",
            q=b"\x00\x01",
            public_key_fingerprint=7,
            encrypted_data=b"\x80" * 32,
        )
        assert _round_trip(original) == original

    def test_flags_present_and_absent(self):
        full = types.DcOption(
            ipv6=True,
            media_only=True,
            id=2,
            ip_address="149.154.167.51",
            port=443,
            secret=b"\x01\x02",
        )
        assert _round_trip(full) == full
        bare = types.DcOption(id=2, ip_address="149.154.167.51", port=443)
        restored = _round_trip(bare)
        assert restored == bare
        assert restored.secret is None
        assert restored.ipv6 is False

    def test_a_bare_vector_of_bare_objects(self):
        original = types.mtproto.FutureSalts(
            req_msg_id=1,
            now=2,
            salts=[types.mtproto.FutureSalt(valid_since=3, valid_until=4, salt=5)],
        )
        # Neither the vector nor its items carry a constructor id here, which is
        # the whole point of the bare spelling: 4 + 8 + 4 + 4 + 16 bytes.
        assert len(original.to_bytes()) == 36
        assert _round_trip(original) == original

    def test_a_bare_vector_of_boxed_objects(self):
        original = types.mtproto.AccessPointRule(
            phone_prefix_rules=b"1,7 900",
            dc_id=2,
            ips=[types.mtproto.IpPort(ipv4=1, port=443)],
        )
        assert _round_trip(original) == original

    def test_a_boxed_vector_of_boxed_objects(self):
        original = types.ChatParticipants(
            chat_id=10,
            participants=[
                types.ChatParticipant(user_id=1, inviter_id=2, date=3),
                types.ChatParticipant(user_id=4, inviter_id=5, date=6, rank="boss"),
            ],
            version=1,
        )
        assert _round_trip(original) == original

    def test_a_function_wrapping_another(self):
        inner = functions.mtproto.ReqPqMulti(nonce=99)
        original = functions.InvokeWithLayer(layer=228, query=inner)
        restored = _round_trip(original)
        assert isinstance(restored, functions.InvokeWithLayer)
        assert restored.query == inner

    def test_a_namespaced_type(self):
        original = types.updates.State(pts=1, qts=2, date=3, seq=4, unread_count=5)
        assert _round_trip(original) == original

    @pytest.mark.parametrize("optionals", [True, False])
    def test_every_plain_constructor_survives(self, optionals):
        checked = 0
        for constructor_id, (module_name, class_name) in CONSTRUCTORS.items():
            cls = getattr(import_module(f"sunnygram.raw.{module_name}"), class_name)
            original = _plain_instance(cls, optionals)
            if original is None:
                continue
            assert _round_trip(original) == original, cls.QUALNAME
            assert original.ID == constructor_id
            checked += 1
        # Guard the guard: a refactor that quietly stopped building instances
        # would otherwise leave this test passing on nothing. Around 1150 of the
        # constructors are built purely from primitives.
        assert checked > 1000


def _round_trip(original: TLObject) -> TLObject:
    reader = TLReader(original.to_bytes())
    restored = reader.read_object()
    assert reader.remaining == 0, f"{type(original).__name__} left bytes behind"
    assert isinstance(restored, TLObject)
    return restored


_SAMPLES: dict[str, object] = {
    "int": 1,
    "float": 0.5,
    "str": "sample",
    "bytes": b"sample",
    "bool": True,
}


def _plain_instance(cls: type[TLObject], optionals: bool) -> TLObject | None:
    """An instance of cls, or None if its fields are not all primitives.

    Anything referring to another TL type is left to the hand-written cases
    above, which can pick a sensible form for it.
    """
    initializer = cls.__dict__.get("__init__")
    if initializer is None:
        return cls()
    arguments: dict[str, object] = {}
    for name, parameter in inspect.signature(initializer).parameters.items():
        if name == "self":
            continue
        annotation = str(parameter.annotation)
        skippable = annotation.endswith(" | None") or parameter.default is False
        if skippable and not optionals:
            continue
        value = _sample(annotation.removesuffix(" | None"))
        if value is None:
            return None
        arguments[name] = value
    return cls(**arguments)


def _sample(annotation: str) -> object | None:
    if annotation in _SAMPLES:
        return _SAMPLES[annotation]
    if annotation.startswith("list[") and annotation[5:-1] in _SAMPLES:
        return [_SAMPLES[annotation[5:-1]]]
    return None


class TestThePackedWriteBody:
    """The one-call body for constructors whose layout is fixed.

    It is generated as a fast path with the field-by-field writing kept
    underneath, because struct is stricter than this library is: write_long
    takes an id or a hash in either spelling, signed or unsigned, and struct's
    q refuses anything past 2**63. Access hashes really are generated up there,
    so the fallback is not a formality, and a test that only used small numbers
    would never once run it.
    """

    def test_the_hot_constructors_got_it(self):
        # Not an implementation detail worth pinning in general, but these four
        # are named on nearly every outgoing call, so losing the fast path on
        # them is losing most of what it was for.
        from sunnygram.raw.types import _root

        for named in ("InputPeerUser", "InputPeerChannel", "InputUser", "InputChannel"):
            packed = getattr(_root, f"_PACK_{named}")
            assert packed.format == "<qq", named

    def test_an_ordinary_value_round_trips(self):
        original = types.InputPeerUser(user_id=777000, access_hash=-98765)
        assert _round_trip(original) == original

    def test_an_unsigned_hash_takes_the_fallback_and_is_still_right(self):
        # 2**64 - 12345 is what an access hash looks like when whatever made it
        # treated it as unsigned. struct.pack("<q") raises on it; _write_wide
        # has always accepted it, and the bytes are the same either way.
        unsigned = (1 << 64) - 12345
        one = types.InputPeerUser(user_id=777000, access_hash=unsigned)

        writer = TLWriter()
        one.write_body(writer)
        written = bytes(writer.getvalue())
        assert len(written) == 16

        # Reading gives the signed spelling of the same bytes, which is what
        # this library has always done and what the peer cache stores.
        back = types.InputPeerUser.read(TLReader(written))
        assert back.user_id == 777000
        assert back.access_hash == unsigned - (1 << 64)

    def test_the_two_paths_write_the_same_bytes(self):
        # The fallback is only correct if it is the same layout. Comparing a
        # value that packs against the same value written a field at a time is
        # the only thing that says so.
        one = types.InputPeerUser(user_id=777000, access_hash=-98765)

        fast = TLWriter()
        one.write_body(fast)

        slow = TLWriter()
        slow.write_long(one.user_id)
        slow.write_long(one.access_hash)

        assert bytes(fast.getvalue()) == bytes(slow.getvalue())

    def test_a_value_too_wide_for_either_still_refuses(self):
        # The fallback must not turn a bad value into a silently truncated one.
        one = types.InputPeerUser(user_id=777000, access_hash=1 << 70)
        with pytest.raises(TLSerializationError, match="int64"):
            one.write_body(TLWriter())

    def test_an_int_that_does_not_fit_still_refuses(self):
        one = types.UpdateChannelMessageViews(channel_id=1, id=2, views=1 << 40)
        with pytest.raises(TLSerializationError, match="TL int"):
            one.write_body(TLWriter())
