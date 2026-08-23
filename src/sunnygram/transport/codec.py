# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""How MTProto packets are framed on a TCP connection.

Nothing above this layer is self-describing, so the framing is what decides
where one packet ends and the next begins. Telegram defines four and all four
are here. Intermediate is the plain one, four bytes of length and then the
payload. Full spends eight more bytes per packet on a sequence number and a
checksum, which catches a corrupted or reordered stream by itself. Abridged
spends one byte instead of four wherever the packet is small enough. Padded
intermediate is intermediate with a few random bytes on the end, which is what
an MTProxy asks for, since without it the packet lengths are readable off the
wire by anyone watching.

Whichever it is the server can answer with a negative error code instead of a
packet, usually before the connection has done anything, and that is a different
thing from a malformed stream: one means the server said no, the other means we
can no longer tell where a packet starts.

The full codec counts packets, so one codec instance belongs to one connection.
"""

from __future__ import annotations

import asyncio
import secrets
from typing import ClassVar, Protocol
from zlib import crc32

from ..errors import MalformedFrame, TransportClosed, TransportRejected

__all__ = [
    "Abridged",
    "Codec",
    "Full",
    "Intermediate",
    "MAX_PACKET_SIZE",
    "PaddedIntermediate",
    "Reader",
]

# Server data is untrusted, so a length is not permission to allocate. The
# largest real packets are file chunks and difference batches, far under this.
MAX_PACKET_SIZE = 16 * 1024 * 1024


class Reader(Protocol):
    """The one method a codec needs, which asyncio's StreamReader already has."""

    async def readexactly(self, count: int, /) -> bytes: ...


async def _read(reader: Reader, count: int) -> bytes:
    try:
        return await reader.readexactly(count)
    except (asyncio.IncompleteReadError, OSError) as exc:
        raise TransportClosed("the connection ended mid-packet") from exc


def _check_payload_length(length: int, minimum: int = 0) -> None:
    if length < minimum or length % 4 or length > MAX_PACKET_SIZE:
        raise MalformedFrame(f"a packet cannot be {length} bytes long")


def _check_frame_length(length: int, minimum: int = 0) -> None:
    """The same check for a framing whose length includes padding.

    Padding is what makes the length not a multiple of four, so a padded frame
    cannot be held to that and only the bounds are left.
    """
    if length < minimum or length > MAX_PACKET_SIZE:
        raise MalformedFrame(f"a packet cannot be {length} bytes long")


async def _rejection(reader: Reader) -> TransportRejected:
    """Read the code out of the four-byte packet that carries one.

    Every framing spells a refusal the same way, as a payload of exactly four
    bytes holding a negative number. No real MTProto message is that short, so
    the length alone identifies it.
    """
    return TransportRejected(int.from_bytes(await _read(reader, 4), "little", signed=True))


class Codec:
    """A packet framing."""

    __slots__ = ()

    # Sent once when the connection opens, to tell the server which framing
    # this connection will use.
    init: ClassVar[bytes] = b""

    # The same choice as a four-byte tag, which is how it is spelled inside an
    # obfuscated handshake rather than on its own in front of the stream. A
    # framing with no tag cannot be obfuscated.
    tag: ClassVar[bytes] = b""

    def encode(self, payload: bytes) -> bytes:
        """Wrap one payload into a frame."""
        raise NotImplementedError

    async def decode(self, reader: Reader) -> bytes:
        """Pull exactly one frame and hand back its payload."""
        raise NotImplementedError


class Intermediate(Codec):
    """Four bytes of little-endian length, then that many bytes of payload."""

    __slots__ = ()

    init = b"\xee\xee\xee\xee"
    tag = b"\xee\xee\xee\xee"

    def encode(self, payload: bytes) -> bytes:
        _check_payload_length(len(payload))
        return len(payload).to_bytes(4, "little") + payload

    async def decode(self, reader: Reader) -> bytes:
        length = int.from_bytes(await _read(reader, 4), "little", signed=True)
        if length < 0:
            raise TransportRejected(length)
        if length == 4:
            raise await _rejection(reader)
        _check_payload_length(length)
        return await _read(reader, length)


class Abridged(Codec):
    """One byte of length wherever the packet is small enough for one.

    The length counts four-byte words instead of bytes, which lets it
    fit in a byte at all: 127 words is 508 bytes, and anything above that spends
    a marker and three more. Worth having on a link where the packets are small
    and frequent, which is most of them once a session is up.
    """

    __slots__ = ()

    init = b"\xef"
    tag = b"\xef\xef\xef\xef"

    LONG: ClassVar[int] = 0x7F

    def encode(self, payload: bytes) -> bytes:
        _check_payload_length(len(payload))
        words = len(payload) // 4
        if words < self.LONG:
            return bytes((words,)) + payload
        return b"\x7f" + words.to_bytes(3, "little") + payload

    async def decode(self, reader: Reader) -> bytes:
        first = (await _read(reader, 1))[0]
        words = (
            int.from_bytes(await _read(reader, 3), "little")
            if first == self.LONG
            else first
        )
        length = words * 4
        if length == 4:
            raise await _rejection(reader)
        _check_payload_length(length)
        return await _read(reader, length)


class PaddedIntermediate(Codec):
    """Intermediate with up to three random bytes on the end of every packet.

    The padding is the whole point: without it every packet length is readable
    off the stream by anyone watching it, and MTProto's own lengths are
    distinctive enough to identify the protocol from them alone. This is the
    framing an MTProxy asks for.

    Nothing has to be counted to undo it. An MTProto payload is always a whole
    number of four-byte words, so whatever the frame length leaves over four is
    exactly how much padding to drop.
    """

    __slots__ = ()

    init = b"\xdd\xdd\xdd\xdd"
    tag = b"\xdd\xdd\xdd\xdd"

    def encode(self, payload: bytes) -> bytes:
        _check_payload_length(len(payload))
        padding = secrets.token_bytes(secrets.randbelow(4))
        return (
            (len(payload) + len(padding)).to_bytes(4, "little") + payload + padding
        )

    async def decode(self, reader: Reader) -> bytes:
        length = int.from_bytes(await _read(reader, 4), "little", signed=True)
        if length < 0:
            raise TransportRejected(length)
        if length == 4:
            raise await _rejection(reader)
        _check_frame_length(length)
        frame = await _read(reader, length)
        return frame[: length - length % 4]


class Full(Codec):
    """Length and sequence number in front, crc32 behind.

    The length counts the whole frame, so a payload of n bytes travels as n+12.
    Both sequence numbers start at zero and count packets, not bytes.
    """

    __slots__ = ("_sent", "_received")

    init = b""

    def __init__(self) -> None:
        self._sent = 0
        self._received = 0

    def encode(self, payload: bytes) -> bytes:
        _check_payload_length(len(payload))
        head = (len(payload) + 12).to_bytes(4, "little") + self._sent.to_bytes(
            4, "little"
        )
        self._sent += 1
        frame = head + payload
        return frame + crc32(frame).to_bytes(4, "little")

    async def decode(self, reader: Reader) -> bytes:
        head = await _read(reader, 4)
        length = int.from_bytes(head, "little", signed=True)
        if length < 0:
            raise TransportRejected(length)
        _check_payload_length(length, minimum=12)

        rest = await _read(reader, length - 4)
        payload = rest[4:-4]
        # crc32 covers everything but itself, so a truncated or flipped byte
        # anywhere in the frame shows up here.
        if int.from_bytes(rest[-4:], "little") != crc32(head + rest[:-4]):
            raise MalformedFrame("the checksum does not match the frame")

        sequence = int.from_bytes(rest[:4], "little")
        if sequence != self._received:
            raise MalformedFrame(
                f"expected packet {self._received} but the server sent {sequence}"
            )
        self._received += 1
        return payload
