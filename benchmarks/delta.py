"""This round's two changes, measured against the code they replaced.

Both are run several times over, alternating between the old and the new
implementation each pass, so that a machine that speeds up or slows down during
the run cannot be mistaken for a result. The number reported is the median.
"""

from __future__ import annotations

import asyncio
import statistics
import time
from typing import Any

from sunnygram import filters as sfilters
from sunnygram.dispatcher import Dispatcher, Handler
from sunnygram.raw import types
from sunnygram.storage import PeerKind
from sunnygram.types import Message
from sunnygram.types.chat import Chat
from sunnygram.types.user import User
from sunnygram.updates import Event

PASSES = 7

RAW = types.Message(
    id=1,
    peer_id=types.PeerUser(user_id=7),
    from_id=types.PeerUser(user_id=7),
    date=1700000000,
    message="/start hello there",
)
USERS = {7: types.User(id=7, first_name="Someone", last_name="Here", access_hash=99)}


def rate(work, rounds: int) -> float:
    work()
    start = time.perf_counter()
    for _ in range(rounds):
        work()
    return rounds / (time.perf_counter() - start)


def rate_async(loop, make_coro, rounds: int) -> float:
    async def run() -> float:
        await make_coro()
        start = time.perf_counter()
        for _ in range(rounds):
            await make_coro()
        return rounds / (time.perf_counter() - start)

    return loop.run_until_complete(run())


def report(name: str, before: list[float], after: list[float]) -> None:
    was, now = statistics.median(before), statistics.median(after)
    print(
        f"  {name:<34} {was:>10,.0f}/s -> {now:>10,.0f}/s   "
        f"{1e6 / was:>6.2f}us -> {1e6 / now:>5.2f}us   {(now - was) / was * 100:+.0f}%"
    )


# ------------------------------------------------------- wrapping a message

NEW_CHAT = Chat.from_raw.__func__


def old_chat_from_raw(cls, peer):
    """Last round: build a whole User in order to read four fields off it."""
    if isinstance(peer, types.User):
        wrapped = User.from_raw(peer)
        if wrapped is None:
            return None
        return cls(
            id=wrapped.id,
            kind=PeerKind.BOT if wrapped.is_bot else PeerKind.USER,
            title=wrapped.full_name or None,
            username=wrapped.username,
            raw=peer,
        )
    return NEW_CHAT(cls, peer)


def bench_wrapping() -> None:
    def wrap() -> Any:
        return Message.from_raw(RAW, users=USERS, chats={})

    before: list[float] = []
    after: list[float] = []
    for _ in range(PASSES):
        Chat.from_raw = classmethod(old_chat_from_raw)
        before.append(rate(wrap, 20000))
        Chat.from_raw = classmethod(NEW_CHAT)
        after.append(rate(wrap, 20000))
    report("Message.from_raw", before, after)


# ------------------------------------------------------------ the dispatcher


async def nothing(client, value):
    return None


class FakeClient:
    def wrap_message(self, raw, *, users, chats):
        return Message.from_raw(raw, users=users, chats=chats)


def an_event() -> Event:
    return Event(
        types.UpdateNewMessage(message=RAW, pts=1, pts_count=1), users=USERS, chats={}
    )


class OldDispatcher(Dispatcher):
    """Last round: copy the whole handler list per reading and scan it all."""

    def _wanting(self, kind: str) -> tuple[Handler, ...]:
        return tuple(held for held in list(self.handlers) if held.kind == kind)


def a_set(cls, commands: int, callbacks: int, raws: int) -> Dispatcher:
    dispatcher = cls()
    for _ in range(raws):
        dispatcher.add(Handler(nothing, kind="raw"))
    for _ in range(callbacks):
        dispatcher.add(Handler(nothing, kind="callback"))
    for index in range(commands):
        dispatcher.add(
            Handler(nothing, kind="message", filters=sfilters.command(f"c{index}"))
        )
    return dispatcher


def bench_dispatch() -> None:
    loop = asyncio.new_event_loop()
    client = FakeClient()
    for commands, callbacks, raws in ((5, 5, 2), (40, 20, 2), (100, 50, 5)):
        before: list[float] = []
        after: list[float] = []
        old = a_set(OldDispatcher, commands, callbacks, raws)
        new = a_set(Dispatcher, commands, callbacks, raws)
        for _ in range(PASSES):
            before.append(rate_async(loop, lambda: old.feed(client, an_event()), 3000))
            after.append(rate_async(loop, lambda: new.feed(client, an_event()), 3000))
        total = commands + callbacks + raws
        report(f"feed, {total} handlers", before, after)
    loop.close()


if __name__ == "__main__":
    print(f"median of {PASSES} alternating passes\n")
    print("== wrapping an arrived message ==")
    bench_wrapping()
    print("\n== one update fed all the way through ==")
    bench_dispatch()
