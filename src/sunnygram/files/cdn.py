# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Fetching a file from a CDN datacenter instead of from Telegram.

Popular files do not come from Telegram. They come from a content delivery
network Telegram rents, which is closer to more people and cheaper to run, and
which Telegram deliberately does not trust. The whole shape of this follows from
that one decision.

The CDN never sees the file. What it holds is a blob encrypted with a key it was
never given, and what a client gets back is that blob: the key and the starting
counter arrive from the real datacenter, in the redirect, and the decryption
happens here. The CDN also never learns whose file it is: no authorization is
exported to it, and the only name for the file it is ever told is a token that
means nothing anywhere else.

That leaves one thing the CDN could still do, which is hand back the wrong
bytes, and it is why this module is stricter than the rest of the download path.
The real datacenter publishes a SHA-256 for every block of the file, and nothing
here returns a byte that has not been hashed and compared. A caller who asks for
a range that does not line up with those blocks gets the blocks around it
fetched and checked whole, because the alternative is verifying part of a hash,
which is not verifying anything.

The last wrinkle is that a CDN is a cache, and a cache can miss. When it does it
says so instead of answering, and the cure is to ask the real datacenter to
push the file over again and then ask a second time.
"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Sequence

from ..crypto import new_ctr, off_loop
from ..errors import RPCError, SecurityError, SunnygramError
from ..network import Invoker
from ..raw import functions, types
from .parts import check_download_chunk

__all__ = ["CdnSession", "is_stale_token"]

# What the server says when the token in hand is no longer one it knows. The
# file is still there; the way we were told to ask for it is not.
STALE_TOKEN = "FILE_TOKEN_INVALID"

# How many times to accept being told the CDN has not got the file yet. Each
# round asks the real datacenter to push it over, which it does at once, so a
# third refusal means something other than a cold cache.
MAX_REUPLOADS = 3

# The block size to assume when a redirect arrives carrying no hashes at all and
# the first getCdnFileHashes has not happened yet. Only used to decide how much
# to ask for, never to decide what to verify.
DEFAULT_BLOCK = 128 * 1024


class CdnSession:
    """One file, on the CDN it was redirected to.

    Built from the redirect and shared by every worker on that file, which is
    what lets one of them learn a hash or fix a cold cache for all of them.
    """

    __slots__ = (
        "_invoker",
        "_origin",
        "_dc_id",
        "_token",
        "_key",
        "_iv",
        "_hashes",
        "_lock",
        "_ready",
    )

    def __init__(
        self, invoker: Invoker, redirect: types.upload.FileCdnRedirect, origin: int
    ) -> None:
        if len(redirect.encryption_key) != 32:
            raise SecurityError(
                "a CDN redirect carried a "
                f"{len(redirect.encryption_key)} byte key, not a 256 bit one"
            )
        if len(redirect.encryption_iv) != 16:
            raise SecurityError(
                "a CDN redirect carried a "
                f"{len(redirect.encryption_iv)} byte counter, not a 128 bit one"
            )
        self._invoker = invoker
        # Where the file really lives. Two calls still go there: the one that
        # asks for more hashes and the one that asks for a push.
        self._origin = origin
        self._dc_id = redirect.dc_id
        self._token = redirect.file_token
        self._key = redirect.encryption_key
        self._iv = redirect.encryption_iv
        # Offset to expected SHA-256, learned from the redirect and topped up
        # as the download moves through the file.
        self._hashes: dict[int, types.FileHash] = {}
        self._learn(redirect.file_hashes)
        self._lock = asyncio.Lock()
        self._ready = False

    def __repr__(self) -> str:
        # The key decrypts this file and the token names it, so neither is
        # written down here (rule S2). What is left is what a diagnostic
        # actually wants: which CDN, and how much of the file we can check.
        return f"CdnSession(dc={self._dc_id}, hashes={len(self._hashes)})"

    @property
    def dc_id(self) -> int:
        """The CDN datacenter this file is being taken from."""
        return self._dc_id

    @property
    def block(self) -> int:
        """How much of the file one published hash covers.

        Read off the hashes themselves rather than assumed, since it is the
        server's choice, and taken as the largest of them, since the last block
        of a file is a short one. It is what a request gets rounded out to,
        because a block is the smallest thing that can be checked.
        """
        if not self._hashes:
            return DEFAULT_BLOCK
        return max(known.limit for known in self._hashes.values())

    async def _block_size(self) -> int:
        """The block size, asking Telegram for hashes if none have arrived yet.

        A redirect does not have to carry any, and guessing wrong here means
        asking the CDN for the wrong amount and throwing most of it away. So
        the first hashes are fetched before the first byte instead of after.
        """
        if not self._hashes:
            await self._more_hashes(0)
        return self.block

    async def fetch(self, offset: int, limit: int) -> bytes:
        """One piece of the file, decrypted and checked.

        The bytes handed back are exactly the ones asked for. Getting them may
        mean fetching a little more, when the range asked for starts or ends
        inside a block, since a block is what a hash covers. That only happens
        to a caller who chose pieces smaller than the blocks Telegram publishes
        for the file, which is no one by default.
        """
        block = await self._block_size()
        end = offset + limit
        if offset % block == 0 and limit % block == 0:
            return await self._verified(offset, limit)

        check_download_chunk(block)
        start = offset - offset % block
        # Whole blocks, one call each, so that no request straddles a megabyte
        # boundary and every one of them is a size the server accepts.
        pieces = []
        for at in range(start, end + (-end % block), block):
            piece = await self._verified(at, block)
            pieces.append(piece)
            if len(piece) < block:
                # The end of the file, which is where the last block stops
                # being a full one.
                break
        whole = b"".join(pieces)
        return whole[offset - start : offset - start + limit]

    async def _verified(self, offset: int, limit: int) -> bytes:
        """A block-aligned range, decrypted and hashed before it is returned."""
        raw = await self._encrypted(offset, limit)
        if not raw:
            return b""
        plain = await _decrypt(self._key, self._iv, offset, raw)
        await self._check(offset, plain)
        return plain

    async def _encrypted(self, offset: int, limit: int) -> bytes:
        """The CDN's answer, with a cold cache warmed up if that is the problem."""
        for _ in range(MAX_REUPLOADS):
            await self._reachable()
            answer = await self._invoker.invoke(
                functions.upload.GetCdnFile(
                    file_token=self._token, offset=offset, limit=limit
                ),
                dc_id=self._dc_id,
                bulk=True,
            )
            if isinstance(answer, types.upload.CdnFile):
                return answer.bytes
            if isinstance(answer, types.upload.CdnFileReuploadNeeded):
                await self._push(answer.request_token)
                continue
            raise SunnygramError(
                f"expected a CDN file, got {type(answer).__name__}"
            )
        raise SunnygramError(
            f"CDN datacenter {self._dc_id} kept saying it has not got this file, "
            f"after being asked {MAX_REUPLOADS} times to have it sent over"
        )

    async def _reachable(self) -> None:
        """Look the CDN datacenter up, once, before anything is sent to it."""
        if self._ready:
            return
        async with self._lock:
            if self._ready:
                return
            await self._invoker.prepare_cdn(self._dc_id)
            self._ready = True

    async def _push(self, request_token: bytes) -> None:
        """Ask the real datacenter to put the file on the CDN.

        The answer is a set of hashes for what it pushed, which is worth
        keeping: it saves asking for them separately a moment later.
        """
        pushed = await self._invoker.invoke(
            functions.upload.ReuploadCdnFile(
                file_token=self._token, request_token=request_token
            ),
            dc_id=self._origin,
        )
        if isinstance(pushed, list):
            self._learn(pushed)

    async def _check(self, offset: int, plain: bytes) -> None:
        """Compare every block of this piece against what Telegram published.

        Nothing gets past here unhashed. A block the server has not published a
        hash for is fetched instead of waved through, and a piece that ends
        mid-block is a piece we should not have asked for, which is a bug here
        rather than anything the CDN did.
        """
        end = offset + len(plain)
        at = offset
        while at < end:
            known = self._hashes.get(at)
            if known is None:
                await self._more_hashes(at)
                known = self._hashes.get(at)
            if known is None:
                raise SecurityError(
                    f"Telegram published no hash covering offset {at} of this "
                    "file, so there is no way to tell what the CDN sent back "
                    "from what it should have sent"
                )
            if known.limit <= 0:
                raise SecurityError(
                    f"the hash Telegram published for offset {at} covers "
                    f"{known.limit} bytes, which cannot be right"
                )
            piece = plain[at - offset : at - offset + known.limit]
            if len(piece) < known.limit:
                raise SecurityError(
                    f"the hash at offset {at} covers {known.limit} bytes and "
                    f"the CDN sent {len(piece)}, so the rest of that block "
                    "would go unchecked"
                )
            digest = await off_loop(len(piece), _sha256, piece)
            if digest != known.hash:
                raise SecurityError(
                    f"the CDN sent back {len(piece)} bytes at offset {at} that "
                    "are not what Telegram says belongs there"
                )
            at += known.limit

    async def _more_hashes(self, offset: int) -> None:
        """Ask the real datacenter what the file should look like from here on."""
        async with self._lock:
            if offset in self._hashes:
                return
            more = await self._invoker.invoke(
                functions.upload.GetCdnFileHashes(
                    file_token=self._token, offset=offset
                ),
                dc_id=self._origin,
            )
            if isinstance(more, list):
                self._learn(more)

    def _learn(self, hashes: Sequence[types.FileHash]) -> None:
        for known in hashes:
            if isinstance(known, types.FileHash):
                self._hashes[known.offset] = known


def is_stale_token(refused: RPCError) -> bool:
    """Whether this refusal means the redirect has to be asked for again."""
    return refused.message == STALE_TOKEN


async def _decrypt(key: bytes, iv: bytes, offset: int, data: bytes) -> bytes:
    """Undo the CDN's encryption for one piece of a file.

    AES-256 in counter mode, with the counter set to where in the file this
    piece starts: the last four bytes of the counter block are replaced with
    the offset divided by sixteen, which is the block number. That is what lets
    a piece from the middle of a file be decrypted without the ones before it,
    and it is also why an offset that is not a multiple of sixteen cannot be
    decrypted at all.
    """
    if offset % 16:
        raise SunnygramError(
            f"a CDN piece has to start on a 16 byte boundary, {offset} does not"
        )
    counter = iv[:12] + (offset // 16).to_bytes(4, "big")
    cipher = new_ctr(key, counter)
    return await off_loop(len(data), cipher.apply, data)


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()
