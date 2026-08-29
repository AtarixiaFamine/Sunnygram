"""This round's change to the receive path, measured against what it replaced.

Putting a container in counter order saves a round trip that was being spent on
nothing, and that round trip is worth more than any number here. What these
measure is the price of the saving, because it is paid on every container
whether or not that one was out of order, and a fix that costs more than the
fault is not a fix.

Three shapes of the same loop:

* unordered, the shape before this round: each update judged where the server
  put it, with its counter worked out inside the judging.
* ordered, counter worked out twice: put in order first, then the counter worked
  out again to judge with. The obvious spelling, and the one this round rejected.
* ordered, counter handed on, which ships: the ordering passes each update's
  counter to the judging, because deciding which counter an update moves is
  several times the cost of the ordering itself.

The three are run several times over, alternating each pass, so that a machine
that speeds up or slows down during the run cannot be mistaken for a result. The
number reported is the median.

What is timed is the judging loop and nothing around it: no delivery, no queue,
no peers learned, no awaiting. That is the part the three shapes spell
differently, and isolating it is the only way to see them apart, but it means
these percentages are the ordering's share of its own loop rather than of a
whole container's journey. The receive path around it dilutes all three.

The other change this round, a vector of one primitive read in one struct call,
is a numbered rule and is measured by rules.py under P3 instead of here.
"""

from __future__ import annotations

import statistics
import time
from typing import Any, Callable

from sunnygram.raw import types
from sunnygram.storage import UpdateState
from sunnygram.updates.manager import _in_counter_order
from sunnygram.updates.state import Counter, Verdict, apply, counter_of, judge

PASSES = 7

PEER = types.PeerUser(user_id=7)


def a_message(pts: int) -> Any:
    """One message, which moves pts by one."""
    return types.UpdateNewMessage(
        message=types.Message(
            id=pts, peer_id=PEER, from_id=PEER, date=1700000000, message="hello"
        ),
        pts=pts,
        pts_count=1,
    )


def a_receipt(pts: int) -> Any:
    """A read receipt, which moves nothing and carries the pts it leaves behind.

    This is the update the server routinely sends ahead of the message it
    acknowledges, and the reason any of this exists.
    """
    return types.UpdateReadHistoryInbox(
        peer=PEER, max_id=pts, still_unread_count=0, pts=pts, pts_count=0
    )


def in_order(pairs: int) -> list[Any]:
    """A container the server sent in the order things happened."""
    updates: list[Any] = []
    for pts in range(101, 101 + pairs):
        updates.append(a_message(pts))
        updates.append(a_receipt(pts))
    return updates


def out_of_order(pairs: int) -> list[Any]:
    """The same container with every receipt ahead of its message.

    Both carry the same pts, so read in that order the receipt lands short of
    its own counter and is indistinguishable from a gap.
    """
    updates: list[Any] = []
    for pts in range(101, 101 + pairs):
        updates.append(a_receipt(pts))
        updates.append(a_message(pts))
    return updates


def settle(state: UpdateState, counter: Counter | None) -> int:
    """The judging half of _one, answering whether this one read as a gap.

    A gap is the expensive verdict: in the manager it goes and fetches a
    difference before anything else in the container is looked at. Delivery is
    left out on purpose, being the same work in all three shapes and nothing
    that would tell them apart.
    """
    if counter is None:
        return 0
    verdict = judge(state, counter)
    if verdict is Verdict.GAP:
        return 1
    if verdict is Verdict.APPLY:
        apply(state, counter)
    return 0


def a_state() -> UpdateState:
    return UpdateState(pts=100, date=1700000000)


def unordered(updates: list[Any]) -> int:
    state = a_state()
    gaps = 0
    for update in updates:
        gaps += settle(state, counter_of(update))
    return gaps


def ordered_counter_twice(updates: list[Any]) -> int:
    state = a_state()
    gaps = 0
    for update, _ in _in_counter_order(updates):
        gaps += settle(state, counter_of(update))
    return gaps


def ordered_counter_once(updates: list[Any]) -> int:
    state = a_state()
    gaps = 0
    for update, counter in _in_counter_order(updates):
        gaps += settle(state, counter)
    return gaps


def rate(work: Callable[[], Any], rounds: int) -> float:
    work()
    start = time.perf_counter()
    for _ in range(rounds):
        work()
    return rounds / (time.perf_counter() - start)


def report(name: str, before: list[float], after: list[float]) -> None:
    was, now = statistics.median(before), statistics.median(after)
    print(
        f"  {name:<36} {was:>9,.0f}/s -> {now:>9,.0f}/s   "
        f"{(now - was) / was * 100:+.0f}%"
    )


def bench(label: str, updates: list[Any]) -> None:
    rounds = max(20000 // len(updates), 20)
    base: list[float] = []
    twice: list[float] = []
    once: list[float] = []
    for _ in range(PASSES):
        base.append(rate(lambda: unordered(updates), rounds))
        twice.append(rate(lambda: ordered_counter_twice(updates), rounds))
        once.append(rate(lambda: ordered_counter_once(updates), rounds))
    print(f"\n  {label}, {len(updates)} updates")
    report("ordering, counter worked out twice", base, twice)
    report("ordering, counter handed on", base, once)


def correctness() -> None:
    """The point of the round, before any of it is timed.

    Nothing is lost either way, which is why this went unnoticed for so long.
    What the unordered shape costs is a getDifference per receipt that arrived
    ahead of its message, asked under the lock everything else waits on, and
    answered with nothing to say.
    """
    for pairs in (1, 5, 50):
        assert unordered(out_of_order(pairs)) == pairs
        assert ordered_counter_once(out_of_order(pairs)) == 0
        assert ordered_counter_twice(out_of_order(pairs)) == 0
        # A container the server already sent in order never paid this.
        assert unordered(in_order(pairs)) == 0
        assert ordered_counter_once(in_order(pairs)) == 0


if __name__ == "__main__":
    correctness()
    print(f"median of {PASSES} alternating passes, against the unordered shape")
    print("\n== one container judged all the way through ==")
    for label, make in (("in order", in_order), ("out of order", out_of_order)):
        for pairs in (1, 5, 50):
            bench(label, make(pairs))
