# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Getting a file to Telegram.

Uploading is done blind. The parts go up one call at a time under an id the
client invents, nothing acknowledges that a file exists, and there is no handle
to hold: what comes back is an input file, which is only meaningful when handed
straight to whatever is going to send it. Until that happens the parts sit on
the server unattached, and if the program stops there they are simply forgotten.

Two paths, and the file's size chooses. Under ten megabytes a file goes up with
an md5 of the whole thing, which lets the server recognize a file it already has
and skip storing it twice. Over that it goes as a big file, where every part
declares the total so the server can assemble without knowing the length in
advance, and no md5 is sent because computing one would mean reading a
multi-gigabyte file twice.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

from ..errors import UploadRefused
from ..network import Invoker
from ..raw import functions, types
from .parts import (
    BIG_FILE,
    MAX_PARTS,
    UPLOAD_PART,
    WORKERS,
    check_upload_part,
    in_parallel,
)

if TYPE_CHECKING:
    from ..raw import base

__all__ = ["Progress", "upload_file"]

# Told how far along a transfer is, as bytes done and bytes total. Total is
# zero when nothing knows it, which for an upload never happens.
Progress = Callable[[int, int], None]


async def upload_file(
    invoker: Invoker,
    source: str | os.PathLike[str] | bytes | bytearray | BinaryIO,
    *,
    name: str | None = None,
    part_size: int = UPLOAD_PART,
    workers: int = WORKERS,
    progress: Progress | None = None,
) -> base.InputFile:
    """Send a file up, and return the handle for attaching it to something.

    The source is a path, the bytes themselves, or anything with a read method.
    The answer is only good for one send, and only for a while: hand it to the
    call that posts the message rather than keeping it.

    name is what the file will be called on the other side, and defaults to the
    name on disk, or to the id when there is nothing to take it from.
    """
    check_upload_part(part_size)
    data, size, given_name = _open(source)
    try:
        if size <= 0:
            # Telegram has nowhere to put a file of no bytes: an upload of no
            # parts is refused, and one empty part makes a document that
            # nothing will accept. Better said here than three calls later.
            raise ValueError("there is nothing in this file to upload")
        if size > MAX_PARTS * part_size:
            raise ValueError(
                f"{size} bytes is more than {MAX_PARTS} parts of {part_size}, "
                "which is more than Telegram accepts in one file"
            )
    except BaseException:
        if data is not source and hasattr(data, "close"):
            data.close()
        raise

    file_id = int.from_bytes(secrets.token_bytes(8), "little", signed=True)
    total = max(1, -(-size // part_size))
    big = size > BIG_FILE
    # An md5 is only worth having on the path that sends one, and computing it
    # here means the bytes are read once whether they came from memory or a
    # disk.
    digest = None if big else hashlib.md5()

    try:
        sent = await _send_parts(
            invoker,
            data,
            file_id=file_id,
            size=size,
            total=total,
            part_size=part_size,
            big=big,
            digest=digest,
            workers=workers,
            progress=progress,
        )
    finally:
        if data is not source and hasattr(data, "close"):
            data.close()

    if big:
        return types.InputFileBig(
            id=file_id, parts=sent, name=name or given_name or str(file_id)
        )
    assert digest is not None
    return types.InputFile(
        id=file_id,
        parts=sent,
        name=name or given_name or str(file_id),
        md5_checksum=digest.hexdigest(),
    )


def _open(source: Any) -> tuple[Any, int, str | None]:
    """The source as something to read from, how long it is, and what it is called."""
    if isinstance(source, (bytes, bytearray)):
        return bytes(source), len(source), None
    if isinstance(source, (str, os.PathLike)):
        path = Path(source)
        return path.open("rb"), path.stat().st_size, path.name
    if hasattr(source, "read"):
        # A file object of some kind. Its length has to come from seeking,
        # since the upload has to declare a part count up front.
        here = source.tell()
        size = source.seek(0, os.SEEK_END) - here
        source.seek(here)
        return source, size, getattr(source, "name", None)
    raise TypeError(f"there is nothing to upload in a {type(source).__name__}")


async def _send_parts(
    invoker: Invoker,
    data: Any,
    *,
    file_id: int,
    size: int,
    total: int,
    part_size: int,
    big: bool,
    digest: Any,
    workers: int,
    progress: Progress | None,
) -> int:
    """Cut the source up and put the pieces on the wire, several at a time."""
    reading = asyncio.Lock()
    done = 0
    index = 0
    at = 0

    def read_next() -> tuple[int, bytes] | None:
        """One part, in order. Called under the lock, off the loop for a file."""
        nonlocal index, at
        if isinstance(data, bytes):
            if at >= size:
                return None
            chunk = data[at : at + part_size]
        else:
            chunk = data.read(part_size)
            if not chunk:
                return None
        taken, at = index, at + len(chunk)
        index += 1
        if digest is not None:
            digest.update(chunk)
        return taken, chunk

    async def worker() -> None:
        nonlocal done
        while True:
            async with reading:
                # The read and the md5 both happen here, in order, because both
                # are about the file as a whole instead of about one part. A
                # disk read is blocking, so it goes to a thread; bytes already
                # in memory are not worth the hop.
                if isinstance(data, bytes):
                    item = read_next()
                else:
                    item = await asyncio.to_thread(read_next)
            if item is None:
                return
            number, chunk = item
            if big:
                call: Any = functions.upload.SaveBigFilePart(
                    file_id=file_id,
                    file_part=number,
                    file_total_parts=total,
                    bytes=chunk,
                )
            else:
                call = functions.upload.SaveFilePart(
                    file_id=file_id, file_part=number, bytes=chunk
                )
            # Through the transfer connections. Parts carry their own number,
            # so the server assembles them whatever order they land in.
            if await invoker.invoke(call, bulk=True) is not True:
                raise UploadRefused(number)
            done += len(chunk)
            if progress is not None:
                progress(done, size)

    await in_parallel(worker, workers)
    return index
