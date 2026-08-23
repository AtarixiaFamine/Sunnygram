# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The TCP connection MTProto rides on.

Deliberately dumb: it opens a socket, frames what goes out and unframes what
comes in, and reports when it breaks. Reconnecting, backing off and migrating
between datacenters belong to the network layer above, which can see enough to
decide whether reconnecting is even the right answer.

The socket may be reached through a proxy and the stream may be obfuscated, but
neither changes what this is. A tunnel is dealt with before the first frame and
then forgotten; obfuscation is a cipher wrapped around the framing, below
everything that knows what a packet is.
"""

from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Self

from ..errors import TransportClosed, TransportError
from . import obfuscation
from .codec import Codec, Intermediate, PaddedIntermediate, Reader
from .obfuscation import Obfuscation
from .proxy import Proxy, open_through

__all__ = ["TCPTransport"]


class TCPTransport:
    """One TCP connection to one datacenter."""

    __slots__ = (
        "_codec",
        "_reader",
        "_writer",
        "_timeout",
        "_sending",
        "_proxy",
        "_dc_id",
        "_obfuscated",
        "_scrambler",
    )

    def __init__(
        self,
        codec: Codec | None = None,
        *,
        timeout: float = 15.0,
        proxy: Proxy | None = None,
        dc_id: int = 0,
        obfuscated: bool = False,
    ) -> None:
        # A dd secret is the proxy saying which framing it will accept, so it
        # decides this rather than the caller. Handing it anything else is a
        # connection that opens and then goes quiet, with nothing said about why.
        if proxy is not None and proxy.padded:
            codec = PaddedIntermediate()
        self._codec = Intermediate() if codec is None else codec
        self._timeout = timeout
        self._proxy = proxy
        self._dc_id = dc_id
        # An MTProxy is always obfuscated, since that is what it speaks. A
        # direct connection can be, and it is worth it where the plain shape of
        # MTProto is itself the thing being noticed.
        self._obfuscated = obfuscated or (proxy is not None and proxy.kind == "mtproto")
        self._scrambler: Obfuscation | None = None
        self._reader: Reader | None = None
        self._writer: asyncio.StreamWriter | None = None
        # Frames must not interleave. One byte written out of order and the
        # stream is unrecoverable, so writers queue up here.
        self._sending = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self, host: str, port: int) -> None:
        if self._writer is not None:
            raise TransportError("this transport is already connected")

        if self._proxy is not None:
            reader, writer = await open_through(
                self._proxy, host, port, timeout=self._timeout
            )
        else:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), self._timeout
                )
            except (OSError, asyncio.TimeoutError) as exc:
                raise TransportError(f"could not connect to {host}:{port}") from exc

        self._writer = writer
        try:
            await self._announce(reader, writer)
        except BaseException:
            self._writer = None
            writer.close()
            raise

    async def _announce(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Tell the other end which framing this connection speaks.

        In the clear that is the framing's own opening bytes. Obfuscated it is
        the handshake instead, which carries the same choice as a tag inside it
        and is the last thing on this connection that is not encrypted.
        """
        if not self._obfuscated:
            self._reader = reader
            if self._codec.init:
                writer.write(self._codec.init)
                await writer.drain()
            return

        secret = self._proxy.secret if self._proxy is not None else b""
        scrambler = obfuscation.start(
            self._codec.tag, dc_id=self._dc_id, secret=secret
        )
        self._scrambler = scrambler
        self._reader = scrambler.wrap(reader)
        writer.write(scrambler.header)
        await writer.drain()

    async def send(self, payload: bytes) -> None:
        writer = self._writer
        if writer is None:
            raise TransportClosed("the transport is not connected")
        # Framing happens under the lock instead of before it. Both the full
        # codec's sequence number and the obfuscation keystream advance once per
        # frame and have to advance in the order the frames reach the wire, so
        # building a frame and writing it cannot be two separately ordered steps.
        async with self._sending:
            frame = self._codec.encode(payload)
            if self._scrambler is not None:
                frame = self._scrambler.encrypt(frame)
            try:
                writer.write(frame)
                await writer.drain()
            except OSError as exc:
                raise TransportClosed("the connection dropped while sending") from exc

    async def receive(self) -> bytes:
        if self._reader is None:
            raise TransportClosed("the transport is not connected")
        return await self._codec.decode(self._reader)

    async def close(self) -> None:
        writer, self._writer, self._reader = self._writer, None, None
        # The keystream belongs to this socket. Keeping it would resume a
        # cipher the far end has forgotten.
        self._scrambler = None
        if writer is None:
            return
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            # Already gone from the other side, which is what we wanted anyway.
            pass

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()
