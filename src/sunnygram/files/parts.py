# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""How a file is cut up, and how the pieces are carried at once.

Telegram does not let a client choose freely here. An upload part has to be a
multiple of a kilobyte and has to divide half a megabyte, and a download has to
ask for a multiple of four kilobytes that divides a megabyte, at an offset that
is also a multiple of four kilobytes, without straddling a megabyte boundary.
The rules read like arbitrary arithmetic and are not: they are what lets the
server address any piece of any file without keeping a per-client cursor.

Both defaults are half a megabyte, which is the largest either side allows and
therefore the fewest round trips.

The other thing here is the shape of doing several at once. Latency, not
bandwidth, is what makes a transfer slow: one part at a time over a link with
sixty milliseconds of round trip spends most of its life waiting. Several in
flight fixes that, and the only care needed is that a failure stops the rest
instead of leaving them running behind a raised exception.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

__all__ = [
    "MAX_PARTS",
    "UPLOAD_PART",
    "DOWNLOAD_CHUNK",
    "WORKERS",
    "check_download_chunk",
    "check_upload_part",
    "in_parallel",
]

UPLOAD_PART = 512 * 1024
DOWNLOAD_CHUNK = 512 * 1024

# Where a file stops being sent as one and starts being sent as a big one, which
# is a different call and a different input file at the end of it.
BIG_FILE = 10 * 1024 * 1024

# Telegram counts parts in a signed int but stops caring long before that. Four
# gigabytes in half megabyte parts is eight thousand, which is the largest file
# any account can send, so anything past this is a file that cannot be uploaded
# at all rather than one that needs different arithmetic.
MAX_PARTS = 8000

# How many pieces to keep in flight. Enough to cover the round trip, few enough
# that a transfer does not look like a flood.
WORKERS = 4


def check_upload_part(part_size: int) -> int:
    """Refuse an upload part size the server would refuse, and say why."""
    if part_size <= 0 or part_size % 1024:
        raise ValueError(
            f"an upload part is a whole number of kilobytes, got {part_size}"
        )
    if (512 * 1024) % part_size:
        raise ValueError(
            f"an upload part has to divide 524288 bytes evenly, {part_size} does not"
        )
    return part_size


def check_download_chunk(chunk: int) -> int:
    """Refuse a download chunk size the server would refuse, and say why."""
    if chunk <= 0 or chunk % 4096:
        raise ValueError(
            f"a download asks for a multiple of 4096 bytes, got {chunk}"
        )
    if (1024 * 1024) % chunk:
        raise ValueError(
            f"a download chunk has to divide 1048576 bytes evenly, {chunk} does not"
        )
    return chunk


async def in_parallel(
    work: Callable[[], Coroutine[Any, Any, None]], workers: int
) -> None:
    """Run the same worker several times over, and stop them all if one fails.

    gather on its own would raise the first failure and leave the others going,
    which for a transfer means parts still being sent after the caller has been
    told it went wrong. The exception that comes out is the original one rather
    than a group, because the caller wants to catch FloodWait, not unwrap it.
    """
    if workers < 1:
        raise ValueError("a transfer needs at least one worker")
    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(work()) for _ in range(workers)
    ]
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
