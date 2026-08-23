"""Rule S2: secrets never stringify.

An auth key, an api_hash or a session string reaching a log is not a bug that
degrades anything, it is the account handed to whoever reads the log, and it
happens through the most ordinary line a program can contain. Every class that
holds one therefore writes its own repr, and this is what keeps that true.

Two halves, and the second is the one that matters in a year. The first puts a
canary through every object in the library known to hold secret material and
fails if it comes out the other side. The second is structural: it walks the
package looking for any class with a field whose name says it holds a secret,
and insists that class writes its own repr rather than inheriting one that
would print it. That half fails for a class nobody has thought about yet, which
is the only kind that is going to go wrong.

The generated raw layer is out of scope on purpose. Its objects are what the
server said, they share one repr defined on TLObject, and the rule as written
covers auth keys and session material rather than every byte Telegram sends.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import pkgutil

import pytest

import sunnygram
from sunnygram.crypto import srp
from sunnygram.network import ClientInfo
from sunnygram.session import Session
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.storage.string import StringStorage

# Distinctive enough that finding it in a string cannot be a coincidence, and
# 256 bytes so it is a real auth key everywhere one is required.
CANARY_KEY = bytes(range(256))
CANARY_HASH = "d3adbeefcafef00dd3adbeefcafef00d"

# Field and slot names that say a thing holds secret material. A salt is not
# here: it is public, both ends derive it from nonces, and it appears in the
# clear on the wire.
SECRET_NAMES = frozenset(
    {"auth_key", "auth_keys", "_auth_key", "api_hash", "_key", "password", "m1"}
)

# Modules that are the generated surface rather than the hand-written one.
GENERATED = ("sunnygram.raw", "sunnygram.errors.generated")


def _spellings(value: object) -> list[str]:
    """Every way a program might accidentally turn this into text."""
    return [repr(value), str(value), f"{value}", "%s" % (value,), format(value)]


def _leaks(value: object) -> str | None:
    """The first spelling of this object that gives a secret away."""
    needles = (
        CANARY_KEY.hex(),
        CANARY_HASH,
        str(list(CANARY_KEY[:8])),
        repr(CANARY_KEY[:16]),
    )
    for text in _spellings(value):
        for needle in needles:
            if needle in text:
                return text
    return None


def _session_state() -> SessionState:
    state = SessionState(dc_id=2, user_id=777000)
    state.set_auth_key(2, CANARY_KEY)
    return state


def _secret_holders() -> list[tuple[str, object]]:
    """One of everything in the library that is holding something private."""
    state = _session_state()
    portable = StringStorage()
    portable._state = _session_state()
    return [
        ("SessionState", state),
        ("MemoryStorage", MemoryStorage(_session_state())),
        ("StringStorage", portable),
        ("Session", Session(CANARY_KEY)),
        ("ClientInfo", ClientInfo(api_id=12345, api_hash=CANARY_HASH)),
        (
            "SRPProof",
            srp.SRPProof(a=CANARY_KEY[:32], m1=CANARY_KEY[32:64]),
        ),
    ]


class TestNothingHoldingASecretPrintsIt:
    @pytest.mark.parametrize(
        "name,holder", _secret_holders(), ids=[n for n, _ in _secret_holders()]
    )
    def test_a_secret_never_reaches_a_string(self, name, holder):
        leaked = _leaks(holder)
        assert leaked is None, f"{name} printed its secret: {leaked}"

    def test_the_canary_would_actually_be_caught(self):
        # The guard above is only worth having if it can fail, and a redaction
        # test that cannot detect a leak is the thing it is meant to prevent.
        class Careless:
            def __repr__(self) -> str:
                return f"Careless(auth_key={CANARY_KEY.hex()})"

        assert _leaks(Careless()) is not None

    def test_an_exception_about_a_session_does_not_carry_it(self):
        state = _session_state()
        try:
            raise ValueError(f"could not use the session {state!r}")
        except ValueError as exc:
            assert _leaks(exc) is None


def _hand_written_classes():
    """Every class defined in the hand-written half of the package."""
    for module in pkgutil.walk_packages(sunnygram.__path__, "sunnygram."):
        name = module.name
        if name.startswith(GENERATED):
            continue
        try:
            loaded = importlib.import_module(name)
        except Exception:  # pragma: no cover - a module that will not import
            continue
        for _, cls in inspect.getmembers(loaded, inspect.isclass):
            if cls.__module__ == name:
                yield cls


def _secret_fields(cls: type) -> set[str]:
    """The names on this class that say it is holding something private."""
    names: set[str] = set()
    for slot in getattr(cls, "__slots__", ()) or ():
        if slot in SECRET_NAMES:
            names.add(slot)
    if dataclasses.is_dataclass(cls):
        for entry in dataclasses.fields(cls):
            if entry.name in SECRET_NAMES:
                names.add(entry.name)
    for annotation in getattr(cls, "__annotations__", {}):
        if annotation in SECRET_NAMES:
            names.add(annotation)
    return names


def _repr_is_safe(cls: type) -> bool:
    """Whether turning one of these into text can print what it is holding.

    Three cases. The default repr from object names the type and an address and
    nothing else, so it is safe. A repr the class wrote itself is safe, because
    someone decided what goes in it. Anything else is not: a dataclass is handed
    one that prints every field, and a repr inherited from a base that prints
    its fields does the same thing a level up. Both are the leak, so both fail.
    """
    if cls.__repr__ is object.__repr__:
        return True
    own = cls.__dict__.get("__repr__")
    if own is None:
        return False
    # A dataclass-generated repr is built by dataclasses.__create_fn__, which
    # is the only place that name comes from.
    return "__create_fn__" not in getattr(own, "__qualname__", "")


class TestEveryClassHoldingASecretRedactsItself:
    """The half that catches a class nobody has written a test for yet."""

    def test_the_sweep_finds_the_classes_it_is_meant_to(self):
        # A structural guard that silently matches nothing passes for ever.
        found = {
            cls.__name__ for cls in _hand_written_classes() if _secret_fields(cls)
        }
        assert {"SessionState", "Session", "ClientInfo"} <= found, found

    def test_no_class_holding_a_secret_inherits_a_repr_that_prints_it(self):
        careless = [
            f"{cls.__module__}.{cls.__name__} holds {sorted(_secret_fields(cls))}"
            for cls in _hand_written_classes()
            if _secret_fields(cls) and not _repr_is_safe(cls)
        ]
        assert not careless, (
            "these classes hold secret material and do not write their own "
            "repr, so the default one will print it (rule S2): "
            + "; ".join(sorted(careless))
        )
