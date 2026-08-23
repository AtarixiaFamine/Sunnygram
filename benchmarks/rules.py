"""The claims ARCHITECTURE.md makes with a number in them, measured on demand.

A rule that quotes a ratio is a promise, and a promise nothing re-checks is a
comment. P3 says the shape of the generated codec is worth about 1.7x; that
number was true when it was measured and until this file existed nothing could
tell whether it still was. Run it before a release, by hand, for the reason the
README next door gives: a number measured on a busy runner is worse than no
number.

What P3 claims is two decisions taken together:

  1. A generated `read` builds its object with `cls.__new__` and direct slot
     assignment instead of calling `__init__`, which skips a Python call and
     the keyword binding that goes with it. That saves the same amount however
     many fields the object has.
  2. The fixed-width readers spell their bounds check out in line instead of
     calling `_take`, because reading an int is the most frequent thing this
     library does. That saves one call per field, so it scales with the width
     of the object.

Because the second scales and the first does not, there is no single ratio, and
keeping that honest is what this harness is for. So it sweeps the width. The
narrow end is `updates.State`, a real generated type read on every catch-up:
five fixed-width fields and no flags, so the twin below is exactly it with the
two decisions reversed and nothing else changed. The rest of the sweep is
generated, because a faithful twin of `Message` would mean hand-writing
forty-nine fields of flags and vectors and would stop being the same object.

Which end matters is the part worth reading off the result. The median generated
type has two fields, but `Message` is 49, `User` is 51 and `Channel` is 50, and
between them those are most of what a running program actually reads. The wide
end is the real one.

P8 is the writing side, and it is a plainer claim: a constructor whose fields
are all fixed-width and none of them conditional is laid out by one struct call
instead of one method call per field. The twin there is the constructor as it
was generated before that existed.

Alternating medians, for the reason benchmarks/README.md gives.
"""

from __future__ import annotations

import statistics
import time
from typing import Any, Self

from sunnygram.raw import types
from sunnygram.raw.types.updates import State
from sunnygram.tl import TLObject, TLReader, TLWriter
from sunnygram.tl.core import _INT, _LONG, _UINT

PASSES = 5

# One reader over many objects, which is what a message off the wire is. A
# reader built per object adds a constant to both sides of every ratio here and
# quietly pulls all of them towards 1.00x: measured that way the wide end reads
# 1.28x instead of 1.70x, and the difference is the benchmark, not the code.
PER_BUFFER = 50

REAL_WIDTHS = "Message is 49 fields, User 51, Channel 50"


class SlowReader(TLReader):
    """The reader P3 decided against: every read goes back through `_take`.

    The same check with the same error, one Python call further away. It is the
    tidier of the two, which is why the rule has to say what the untidiness
    buys.
    """

    def read_int(self, signed: bool = True) -> int:
        pos = self._take(4)
        value: int = (_INT if signed else _UINT).unpack_from(self._data, pos)[0]
        return value

    def read_long(self) -> int:
        pos = self._take(8)
        value: int = _LONG.unpack_from(self._data, pos)[0]
        return value


class SlowState(TLObject):
    """`updates.State` as it would be generated without decision 1.

    Byte for byte the same on the wire. The only difference is that `read`
    hands its fields to `__init__` rather than assigning them.
    """

    __slots__ = ("pts", "qts", "date", "seq", "unread_count")

    ID = State.ID
    QUALNAME = "types.updates.SlowState"

    def __init__(
        self, *, pts: int, qts: int, date: int, seq: int, unread_count: int
    ) -> None:
        self.pts = pts
        self.qts = qts
        self.date = date
        self.seq = seq
        self.unread_count = unread_count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.pts)
        w.write_int(self.qts)
        w.write_int(self.date)
        w.write_int(self.seq)
        w.write_int(self.unread_count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        return cls(
            pts=r.read_int(),
            qts=r.read_int(),
            date=r.read_int(),
            seq=r.read_int(),
            unread_count=r.read_int(),
        )


# The two shapes, spelled the way gen_tl.py emits them, so that widening the
# sweep changes the number of fields and nothing else. Generating them is the
# only way to keep that true: a hand-written pair at four widths is four
# chances to make them differ somewhere that is not the thing under test.
_TEMPLATE = """
class Fast(TLObject):
    __slots__ = ({slots},)
    ID = 0x1
    QUALNAME = 'Fast'

    def __init__(self, *, {params}) -> None:
{assigns}

    def write_body(self, w):
{writes}

    @classmethod
    def read(cls, r):
{reads}
        self = cls.__new__(cls)
{sets}
        return self


class Slow(TLObject):
    __slots__ = ({slots},)
    ID = 0x1
    QUALNAME = 'Slow'

    def __init__(self, *, {params}) -> None:
{assigns}

    def write_body(self, w):
{writes}

    @classmethod
    def read(cls, r):
        return cls(
{kwargs}
        )
"""


def a_pair(width: int) -> tuple[type[Any], type[Any]]:
    """Two classes of `width` int fields, differing only in P3's two decisions."""
    fields = [f"f{index}" for index in range(width)]
    source = _TEMPLATE.format(
        slots=", ".join(repr(name) for name in fields),
        params=", ".join(f"{name}: int" for name in fields),
        assigns="\n".join(f"        self.{name} = {name}" for name in fields),
        writes="\n".join(f"        w.write_int(self.{name})" for name in fields),
        reads="\n".join(f"        {name} = r.read_int()" for name in fields),
        sets="\n".join(f"        self.{name} = {name}" for name in fields),
        kwargs="\n".join(f"            {name}=r.read_int()," for name in fields),
    )
    namespace: dict[str, Any] = {"TLObject": TLObject}
    exec(source, namespace)
    return namespace["Fast"], namespace["Slow"]


def a_buffer(cls: type[Any], width: int) -> bytes:
    w = TLWriter()
    one = cls(**{f"f{index}": index * 7 for index in range(width)})
    for _ in range(PER_BUFFER):
        one.write_body(w)
    return bytes(w.getvalue())


def a_state_buffer() -> bytes:
    w = TLWriter()
    one = State(pts=41236, qts=17, date=1700000000, seq=904, unread_count=3)
    for _ in range(PER_BUFFER):
        one.write_body(w)
    return bytes(w.getvalue())


def rate(work: Any, rounds: int) -> float:
    work()
    start = time.perf_counter()
    for _ in range(rounds):
        work()
    return rounds / (time.perf_counter() - start)


def compare(name: str, old: Any, new: Any, rounds: int) -> float:
    before: list[float] = []
    after: list[float] = []
    for _ in range(PASSES):
        before.append(rate(old, rounds) * PER_BUFFER)
        after.append(rate(new, rounds) * PER_BUFFER)
    was, now = statistics.median(before), statistics.median(after)
    ratio = now / was
    print(f"  {name:<40} {was:>12,.0f}/s -> {now:>12,.0f}/s   {ratio:>4.2f}x")
    return ratio


def bench_the_real_one() -> float:
    """updates.State: five fields, the narrow end, and the only exact twin."""
    payload = a_state_buffer()

    def slow() -> Any:
        reader = SlowReader(payload)
        return [SlowState.read(reader) for _ in range(PER_BUFFER)]

    def fast() -> Any:
        reader = TLReader(payload)
        return [State.read(reader) for _ in range(PER_BUFFER)]

    return compare("updates.State, 5 fields, the real one", slow, fast, 2000)


def bench_the_sweep() -> dict[int, float]:
    found: dict[int, float] = {}
    for width in (5, 12, 30, 50):
        fast_cls, slow_cls = a_pair(width)
        payload = a_buffer(fast_cls, width)
        rounds = max(20, int(600_000 / (width * PER_BUFFER)))

        def slow(cls: Any = slow_cls, buffer: bytes = payload) -> Any:
            reader = SlowReader(buffer)
            return [cls.read(reader) for _ in range(PER_BUFFER)]

        def fast(cls: Any = fast_cls, buffer: bytes = payload) -> Any:
            reader = TLReader(buffer)
            return [cls.read(reader) for _ in range(PER_BUFFER)]

        note = ", where Message and User sit" if width == 50 else ""
        found[width] = compare(f"{width} int fields{note}", slow, fast, rounds)
    return found


# ---------------------------------------------------------------- P8, writing


_WRITE_TEMPLATE = """
class Apart(TLObject):
    __slots__ = ({slots},)
    ID = 0x1
    QUALNAME = 'Apart'

    def __init__(self, *, {params}) -> None:
{assigns}

    def write_body(self, w):
{writes}
"""


def a_twin(one: Any, writers: tuple[str, ...]) -> Any:
    """The same constructor as it was generated before the packed body.

    Built rather than reached for, and this is the one place in this file where
    that took two goes. The obvious way to measure the old path is to make the
    packer refuse, since the fallback is right there in the same method. It is
    also wrong: raising and catching an exception costs more than the writing
    does, so measured that way the fast path looked 8.7x faster instead of
    4.4x, and the difference was the measurement. A twin with only the
    field-by-field body has nothing extra in it.
    """
    fields = [name for name in type(one).__slots__]
    source = _WRITE_TEMPLATE.format(
        slots=", ".join(repr(name) for name in fields),
        params=", ".join(f"{name}: int" for name in fields),
        assigns="\n".join(f"        self.{name} = {name}" for name in fields),
        writes="\n".join(
            f"        w.{writer}(self.{name})"
            for name, writer in zip(fields, writers, strict=True)
        ),
    )
    namespace: dict[str, Any] = {"TLObject": TLObject}
    exec(source, namespace)
    twin: Any = namespace["Apart"]
    return twin(**{name: getattr(one, name) for name in fields})


def bench_the_write_path() -> dict[str, float]:
    """What the packed write_body is worth, against writing a field at a time.

    inputPeerUser is the one that matters: two longs, and it is written on
    nearly every outgoing call, because nearly every call names a peer. pong is
    there because the protocol's own housekeeping is packed too, and the two
    int cases because ints are a call closer to the buffer than longs are, so
    they are the smaller half of the win.
    """
    long_pair = ("write_long", "write_long")
    found: dict[str, float] = {}
    cases = (
        (
            "inputPeerUser, 2 longs",
            types.InputPeerUser(user_id=777000, access_hash=-9),
            long_pair,
        ),
        ("pong, 2 longs", types.mtproto.Pong(msg_id=1, ping_id=2), long_pair),
        (
            "messageEntityBold, 2 ints",
            types.MessageEntityBold(offset=3, length=9),
            ("write_int", "write_int"),
        ),
        (
            "updates.State, 5 ints",
            State(pts=41236, qts=17, date=1700000000, seq=904, unread_count=3),
            ("write_int",) * 5,
        ),
    )
    for name, one, writers in cases:
        apart = a_twin(one, writers)

        def slow(twin: Any = apart) -> Any:
            w = TLWriter()
            for _ in range(PER_BUFFER):
                twin.write_body(w)
            return w

        def fast(packed: Any = one) -> Any:
            w = TLWriter()
            for _ in range(PER_BUFFER):
                packed.write_body(w)
            return w

        if bytes(slow().getvalue()) != bytes(fast().getvalue()):
            raise SystemExit(f"the two write paths disagree on {name}")
        found[name] = compare(name, slow, fast, 4000)
    return found


def check_the_twins_agree() -> None:
    """A twin that reads something different is measuring the wrong thing.

    Cheap, and it is exactly the mistake that makes a benchmark fast by making
    it wrong.
    """
    payload = a_state_buffer()
    quick, slow = TLReader(payload), SlowReader(payload)
    for _ in range(PER_BUFFER):
        one, other = State.read(quick), SlowState.read(slow)
        for field in State.__slots__:
            assert getattr(one, field) == getattr(other, field), field

    fast_cls, slow_cls = a_pair(12)
    payload = a_buffer(fast_cls, 12)
    quick, slow = TLReader(payload), SlowReader(payload)
    for _ in range(PER_BUFFER):
        one, other = fast_cls.read(quick), slow_cls.read(slow)
        for field in fast_cls.__slots__:
            assert getattr(one, field) == getattr(other, field), field


if __name__ == "__main__":
    check_the_twins_agree()
    print(f"median of {PASSES} alternating passes, one reader per {PER_BUFFER}\n")
    print("== P3: what the shape of the generated codec is worth ==")
    bench_the_real_one()
    swept = bench_the_sweep()
    print()
    print("== P8: the packed write body ==")
    written = bench_the_write_path()
    print(
        f"\n  P3 quotes about 1.7x, and that is the wide end: {REAL_WIDTHS}.\n"
        f"  This run measured {swept[50]:.2f}x there and {swept[5]:.2f}x on a five\n"
        "  field object. A release that moves either end by more than a few\n"
        "  percent has changed something the rule describes, and the rule has\n"
        "  to move with it."
    )
    packed = written["inputPeerUser, 2 longs"]
    print()
    print(f"  P8: writing inputPeerUser is {packed:.2f}x what it was, and it is")
    print("  written on nearly every outgoing call, because nearly every call")
    print("  names a peer.")
