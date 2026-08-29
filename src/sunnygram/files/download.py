# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Getting a file back out of Telegram.

Downloading has four complications that uploading does not, and all of them are
about the file not being where or what the caller thinks.

The first is the datacenter. A file lives where it was uploaded, which is often
not where the account lives, so fetching one means talking to another datacenter
and signing in to it first. The invoker does that part; here it is a matter of
passing the right dc_id and believing the server when it says the file has moved.

The second is the file reference, the token inside a location that says this
account may ask for this file now. It expires, and when it does the only cure is
to fetch whatever carried the file again. Nothing in this layer can do that on
its own, since it does not know where the file came from, so the caller may hand
in a refresh: something that goes and gets a fresh source.

The third is that a popular file is not held by Telegram at all. It is held by a
content delivery network, encrypted, and the datacenter answers a request for
one by handing over a key and pointing somewhere else. Following that lives in
cdn.py; here it is a matter of noticing the redirect and fetching through it
from then on.

The fourth is that the pieces come back in whatever order they were asked for.
Asking for one at a time makes a transfer a series of round trips, so several go
out at once, which means a place to put a piece that arrives out of order. When
the size is known that is a preallocated buffer or a seek on the file; when it
is not, the pieces have to be fetched in order, because the only way to learn
where a file ends is to reach the end of it.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

from ..errors import FileMigrate, FileTooLarge, RPCError, SunnygramError
from ..network import Invoker
from ..raw import functions, types
from .cdn import CdnSession, is_stale_token
from .location import FileSource, locate
from .parts import DOWNLOAD_CHUNK, WORKERS, check_download_chunk, in_parallel

__all__ = ["Progress", "Refresh", "download_file", "stream_file"]

Progress = Callable[[int, int], None]

# Asked for a source with a fresh file reference when the one in hand has gone
# stale. Nothing else can do this: only the caller knows where the file came
# from and how to look it up again.
Refresh = Callable[[], Awaitable[Any]]

# What the server says when the token inside a location has aged out. It is not
# an error about the file, which is still there, so it is worth telling apart.
_STALE_REFERENCE = "FILE_REFERENCE_EXPIRED"

# How many times to accept being told the reference is stale before giving up.
# One refresh should be enough; a second means something else is wrong.
_MAX_REFRESHES = 2


async def download_file(
    invoker: Invoker,
    source: Any,
    *,
    into: str | os.PathLike[str] | None = None,
    chunk_size: int = DOWNLOAD_CHUNK,
    workers: int = WORKERS,
    progress: Progress | None = None,
    refresh: Refresh | None = None,
    limit: int = 0,
    cdn: bool = True,
) -> bytes | Path:
    """Fetch a file, into memory or onto disk.

    The source is a message, the media off one, a document, a photo, or a
    FileSource that locate has already worked out. into names a file to write
    to and makes the answer that path; leaving it out makes the answer the bytes
    themselves, which is what a thumbnail or a small document usually wants.

    limit refuses anything bigger than it, before fetching instead of after,
    for a program that is downloading something it did not choose.

    cdn says whether to accept being sent to a content delivery network for a
    popular file, which is faster nearly everywhere and is what every other
    client does. Turning it off keeps the whole transfer inside Telegram, at
    the price of the datacenter having to serve it itself.
    """
    check_download_chunk(chunk_size)
    found = locate(source)
    if limit and found.size and found.size > limit:
        raise FileTooLarge(
            f"this file is {found.size} bytes and the limit given was {limit}"
        )

    state = _Fetcher(invoker, found, refresh, cdn=cdn)
    if into is None:
        return await _into_memory(state, chunk_size, workers, progress, limit)
    return await _into_file(state, Path(into), chunk_size, workers, progress, limit)


async def stream_file(
    invoker: Invoker,
    source: Any,
    *,
    offset: int = 0,
    length: int = 0,
    chunk_size: int = DOWNLOAD_CHUNK,
    progress: Progress | None = None,
    refresh: Refresh | None = None,
    cdn: bool = True,
) -> AsyncIterator[bytes]:
    """Hand a file over a piece at a time, in order, from wherever it is asked.

    download_file answers with the whole thing, which is what most callers want
    and is why it fetches several pieces at once. This is for the ones that do
    not: serving a video to something that is going to play it, feeding a
    decoder, answering a range request, looking at the first kilobyte of
    something enormous. None of those want the file, they want the front of it,
    and waiting for the back is the whole cost.

    offset and length are the byte range, the same pair an HTTP range asks in,
    and both are in whole bytes. Telegram only answers on a chunk boundary, so
    an offset in the middle of one starts from the boundary below and the head
    of the first piece is dropped here rather than being the caller's problem.
    length of zero means to the end.

    One piece is in flight at a time, and that is the trade this makes rather
    than an oversight: pieces have to be handed over in order, so fetching
    ahead only helps if they are held, and holding them is the thing the caller
    came here to avoid.
    """
    check_download_chunk(chunk_size)
    if offset < 0 or length < 0:
        raise ValueError("a byte range is not negative")
    found = locate(source)
    state = _Fetcher(invoker, found, refresh, cdn=cdn)

    skip = offset % chunk_size
    sent = 0
    async for _, piece in _in_order(state, chunk_size, progress, 0, offset - skip):
        if skip:
            piece, skip = piece[skip:], 0
        if length and sent + len(piece) > length:
            piece = piece[: length - sent]
        if piece:
            yield piece
            sent += len(piece)
        if length and sent >= length:
            return


async def _into_memory(
    state: _Fetcher,
    chunk_size: int,
    workers: int,
    progress: Progress | None,
    limit: int,
) -> bytes:
    size = state.size
    if not size:
        return b"".join(
            [piece async for _, piece in _in_order(state, chunk_size, progress, limit)]
        )

    buffer = bytearray(size)
    def put(offset: int, piece: bytes) -> None:
        buffer[offset : offset + len(piece)] = piece

    await _in_pieces(state, chunk_size, workers, progress, put)
    return bytes(buffer)


async def _into_file(
    state: _Fetcher,
    path: Path,
    chunk_size: int,
    workers: int,
    progress: Progress | None,
    limit: int,
) -> Path:
    handle = path.open("wb")
    try:
        if not state.size:
            async for _, piece in _in_order(state, chunk_size, progress, limit):
                await asyncio.to_thread(handle.write, piece)
            return path

        writing = asyncio.Lock()

        def put(offset: int, piece: bytes) -> None:
            handle.seek(offset)
            handle.write(piece)

        async def put_off_loop(offset: int, piece: bytes) -> None:
            # One handle, one position, so the seek and the write belong
            # together. A disk write blocks, so it happens in a thread.
            async with writing:
                await asyncio.to_thread(put, offset, piece)

        await _in_pieces(state, chunk_size, workers, progress, put_off_loop)
        return path
    finally:
        handle.close()


async def _in_pieces(
    state: _Fetcher,
    chunk_size: int,
    workers: int,
    progress: Progress | None,
    put: Any,
) -> None:
    """Fetch a file of known length, several pieces at once."""
    size = state.size
    offsets = iter(range(0, size, chunk_size))
    handing_out = asyncio.Lock()
    done = 0

    async def worker() -> None:
        nonlocal done
        while True:
            async with handing_out:
                offset = next(offsets, None)
            if offset is None:
                return
            piece = await state.fetch(offset, chunk_size)
            if not piece:
                continue
            outcome = put(offset, piece)
            if outcome is not None:
                await outcome
            done += len(piece)
            if progress is not None:
                progress(min(done, size), size)

    await in_parallel(worker, workers)


async def _in_order(
    state: _Fetcher,
    chunk_size: int,
    progress: Progress | None,
    limit: int,
    start: int = 0,
) -> Any:
    """Fetch a file whose length no one knows, one piece after another.

    The end is where a piece comes back shorter than it was asked for, so
    there is nothing to be gained by asking for two at once: the second might
    be past the end and there would be no way to tell that from a gap.
    """
    offset = start
    while True:
        piece = await state.fetch(offset, chunk_size)
        if piece:
            # Refused before it is handed over rather than after. A caller
            # writing to a file has already written whatever it was given, so
            # checking afterwards would leave a whole chunk past the limit on
            # disk before saying the limit was reached.
            if limit and offset + len(piece) > limit:
                raise FileTooLarge(
                    f"this file is past the {limit} byte limit given and its "
                    "size was not known in advance"
                )
            yield offset, piece
            offset += len(piece)
            if progress is not None:
                progress(offset, 0)
        if len(piece) < chunk_size:
            return


class _Fetcher:
    """One file's worth of asking, with the things that can go wrong.

    Holds the location because a refresh replaces it, the datacenter because
    the server can say the file is somewhere else, and the CDN session because
    the server can say the file is not its to serve. All three are shared by
    every worker on the same file: one of them being told
    the reference is stale, or being redirected, fixes it for all of them.
    """

    __slots__ = (
        "_invoker",
        "_source",
        "_refresh",
        "_lock",
        "_refreshes",
        "_cdn",
        "_wants_cdn",
        "_deciding",
        "_decided",
    )

    def __init__(
        self,
        invoker: Invoker,
        source: FileSource,
        refresh: Refresh | None,
        *,
        cdn: bool = True,
    ) -> None:
        self._invoker = invoker
        self._source = source
        self._refresh = refresh
        self._lock = asyncio.Lock()
        self._refreshes = 0
        self._wants_cdn = cdn
        self._cdn: CdnSession | None = None
        # Whether anything has come back yet. Until it has, no one knows where
        # this file is really being served from.
        self._deciding = asyncio.Lock()
        self._decided = False

    @property
    def size(self) -> int:
        """What the file was said to be, or zero if nothing said."""
        return self._source.size

    async def fetch(self, offset: int, limit: int) -> bytes:
        """One piece, with the first one asked for on its own.

        What comes back for the first piece is what says whether this file is
        Telegram's to serve or a CDN's, and workers that all ask at the same
        moment would all be redirected separately and pay for it. One asks,
        the rest find out, and from then on they run together.
        """
        if self._decided:
            return await self._ask(offset, limit)
        async with self._deciding:
            if not self._decided:
                try:
                    return await self._ask(offset, limit)
                finally:
                    self._decided = True
        return await self._ask(offset, limit)

    async def _ask(self, offset: int, limit: int) -> bytes:
        """One piece, retrying whatever is worth retrying."""
        while True:
            source = self._source
            cdn = self._cdn
            try:
                if cdn is not None:
                    return await cdn.fetch(offset, limit)
                answer = await self._invoker.invoke(
                    functions.upload.GetFile(
                        location=source.location,
                        offset=offset,
                        limit=limit,
                        cdn_supported=self._wants_cdn,
                    ),
                    dc_id=source.dc_id,
                    # Through the transfer connections instead of the main
                    # one. Pieces are asked for in whatever order suits, so
                    # nothing here depends on them arriving in it.
                    bulk=True,
                )
            except FileMigrate as moved:
                # The file is not where its owner said. Believed once and
                # remembered, so the other workers do not each find out.
                async with self._lock:
                    if self._source.dc_id == source.dc_id:
                        self._source = _moved(self._source, moved.dc_id)
                continue
            except RPCError as refused:
                if cdn is not None and is_stale_token(refused):
                    # The way we were told to ask the CDN has aged out. The
                    # file has not, so the redirect is simply asked for again.
                    await self._forget_cdn(cdn)
                    continue
                if refused.message != _STALE_REFERENCE:
                    raise
                await self._renew(source)
                continue

            if isinstance(answer, types.upload.File):
                return answer.bytes
            if isinstance(answer, types.upload.FileCdnRedirect):
                async with self._lock:
                    if self._cdn is None:
                        self._cdn = CdnSession(
                            self._invoker, answer, source.dc_id
                        )
                continue
            raise SunnygramError(
                f"expected a file, got {type(answer).__name__}"
            )

    async def _forget_cdn(self, stale: CdnSession) -> None:
        """Drop a CDN session whose token the server no longer knows.

        The next piece asks the datacenter again and is redirected again, with
        a token that works. Counted against the same budget as a stale file
        reference, since a server handing out tokens that are already dead is
        the same kind of loop.
        """
        async with self._lock:
            if self._cdn is not stale:
                return
            self._refreshes += 1
            if self._refreshes > _MAX_REFRESHES:
                raise SunnygramError(
                    "the CDN token expired again straight after being issued, "
                    "so asking for another is not producing a usable one"
                )
            self._cdn = None

    async def _renew(self, stale: FileSource) -> None:
        """Get a location that works again, or explain why there is none."""
        async with self._lock:
            if self._source is not stale:
                # Someone else already did it while this call was waiting.
                return
            if self._refresh is None:
                raise SunnygramError(
                    "this file reference has expired and no refresh was given. "
                    "Fetch whatever carried the file again, and pass refresh so "
                    "the download can do it for itself next time"
                )
            self._refreshes += 1
            if self._refreshes > _MAX_REFRESHES:
                raise SunnygramError(
                    "this file reference expired again straight after being "
                    "refreshed, so refreshing is not producing a usable one"
                )
            self._source = locate(await self._refresh())


def _moved(source: FileSource, dc_id: int) -> FileSource:
    return FileSource(
        location=source.location,
        dc_id=dc_id,
        size=source.size,
        name=source.name,
    )
