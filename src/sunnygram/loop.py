# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Choosing the fastest event loop this machine has.

Every byte the library moves crosses the event loop twice, once as a read and
once as a write, with the timers, futures and task switches of every call in
flight on top. asyncio's own loop is pure Python around a selector; uvloop is
libuv, the same event loop node runs on, wrapped in Cython. Swapping one for the
other changes nothing about what this library does, and is worth a large
multiple on the part of a program waiting on a socket, which for a Telegram
client is most of it.

The ladder, the same shape as the one in crypto/accel.py:

1. uvloop, everywhere it builds, meaning Linux and macOS.
2. winloop, the same libuv for Windows, where uvloop has never shipped a wheel.
   Its api mirrors uvloop's, so this rung and the one above are one code path
   with a different import.
3. asyncio's own loop, which is always there.

Nothing is installed at import. A library that calls uvloop.install() on import
has replaced the event loop of a program that may have opened one already or
chosen its own. Importing sunnygram detects, records what it found, and waits
to be asked.

Client.run is what asks, being the only place in the library that creates a loop
instead of joining one. A program running its own loop keeps it, and can opt in
with new_event_loop:

    import asyncio
    from sunnygram import loop

    with asyncio.Runner(loop_factory=loop.new_event_loop) as runner:
        runner.run(main())
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

__all__ = ["LOOP_BACKEND", "describe", "loop_factory", "new_event_loop"]

LoopFactory = Callable[[], asyncio.AbstractEventLoop]


def _detect() -> tuple[str, LoopFactory | None]:
    # Both of these are optional and neither is importable on every platform, so
    # the whole detection is two guarded imports and a default that always
    # works. uvloop first: where both are installed it is the one that is
    # actually maintained against libuv upstream.
    try:
        import uvloop
    except ImportError:
        pass
    else:
        factory: Any = uvloop.new_event_loop
        return "uvloop", factory
    try:
        import winloop
    except ImportError:
        pass
    else:
        factory = winloop.new_event_loop
        return "winloop", factory
    return "asyncio", None


LOOP_BACKEND, _FACTORY = _detect()
"""Which of the three rungs this process got, as a name fit to print."""


def loop_factory() -> LoopFactory | None:
    """The fastest loop factory available, or None for asyncio's own.

    None rather than asyncio.new_event_loop because that is what
    asyncio.Runner wants for its default, and because the difference between
    "nothing faster is installed" and "something asked for the plain one" is
    worth keeping visible at the call site.
    """
    return _FACTORY


def new_event_loop() -> asyncio.AbstractEventLoop:
    """A new loop, the fastest kind available.

    For a program that runs its own loop and wants what Client.run would have
    picked. Never installed as a policy, only handed out: a loop someone asked
    for is theirs to close.
    """
    if _FACTORY is None:
        return asyncio.new_event_loop()
    return _FACTORY()


def describe() -> str:
    """One line saying which loop is in use, for a diagnostic or a bug report.

    Worth printing next to crypto.describe() when a program is slower than it
    should be, since between them those two lines are most of the answer.
    """
    if LOOP_BACKEND == "asyncio":
        return "loop: asyncio (pip install uvloop for a faster one)"
    return f"loop: {LOOP_BACKEND}"
