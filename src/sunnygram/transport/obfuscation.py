# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""obfuscated2, the stream cipher an MTProxy speaks.

An ordinary MTProto connection announces itself: the first bytes on the wire say
which framing follows, the packet lengths have a recognisable shape, and the
handshake is the same every time. Obfuscation removes all of that by putting the
whole byte stream, framing included, under AES-CTR with a key both ends derive
from sixty-four random bytes the client sends first.

Those sixty-four bytes are the only thing that ever travels in the clear, and
even they are half scrambled: the last eight are sent encrypted, so the framing
tag inside them is not readable either. The rest looks like noise because it is
noise.

The server derives its side by reading the same bytes backwards, so what the
client encrypts with, the server decrypts with. An MTProxy adds a shared secret
into both key derivations, which stops anyone who is not holding it from
speaking to the proxy at all.

This layer sits below the framing and above the socket. Nothing above it knows
it is here, and it never sees a packet, only bytes.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from hashlib import sha256

from ..crypto.accel import StreamCipher, new_ctr
from ..errors import TransportError
from .codec import Reader

__all__ = ["ObfuscatedReader", "Obfuscation", "start"]

# Openings a middlebox would mistake for something else. The first four bytes
# must not read as an HTTP verb or as a TLS record header, and must not collide
# with a framing tag, because a server reading an unobfuscated connection would
# take any of those at face value. A first byte of 0xef would be the abridged
# framing announcing itself, which is the same problem one byte earlier.
_RESERVED_OPENINGS = frozenset(
    {
        b"HEAD",
        b"POST",
        b"GET ",
        b"OPTI",
        b"\xdd\xdd\xdd\xdd",
        b"\xee\xee\xee\xee",
        b"\x16\x03\x01\x02",
    }
)

# Where the handshake bytes are put to work. The layout is fixed by the
# protocol: keys in the middle, the framing tag and the datacenter at the end.
_KEY = slice(8, 40)
_IV = slice(40, 56)
_MIRROR = slice(8, 56)
_TAG = slice(56, 60)
_DC = slice(60, 62)

HEADER_SIZE = 64


@dataclass(frozen=True, slots=True)
class Obfuscation:
    """One obfuscated stream: what to send first, and the two ciphers.

    The ciphers carry the keystream position, so one of these belongs to one
    connection and cannot be reused after a reconnect.
    """

    header: bytes
    outgoing: StreamCipher
    incoming: StreamCipher

    def encrypt(self, data: bytes) -> bytes:
        """Scramble bytes on their way out."""
        return self.outgoing.apply(data)

    def wrap(self, reader: Reader) -> ObfuscatedReader:
        """Put a reader behind the incoming cipher."""
        return ObfuscatedReader(reader, self.incoming)


class ObfuscatedReader:
    """A reader that unscrambles whatever the one below it hands back.

    CTR is a plain keystream, so this works only because the codec above reads
    the stream strictly in order and never skips: every byte that arrives must
    pass through here exactly once, in the order it was sent.
    """

    __slots__ = ("_reader", "_cipher")

    def __init__(self, reader: Reader, cipher: StreamCipher) -> None:
        self._reader = reader
        self._cipher = cipher

    async def readexactly(self, count: int, /) -> bytes:
        return self._cipher.apply(await self._reader.readexactly(count))


def _opening() -> bytearray:
    """Sixty-four random bytes that no middlebox will read as something else."""
    while True:
        candidate = bytearray(secrets.token_bytes(HEADER_SIZE))
        if candidate[0] == 0xEF:
            continue
        if bytes(candidate[:4]) in _RESERVED_OPENINGS:
            continue
        if candidate[4:8] == b"\x00\x00\x00\x00":
            continue
        return candidate


def start(tag: bytes, *, dc_id: int = 0, secret: bytes = b"") -> Obfuscation:
    """Begin an obfuscated stream for a framing, and possibly for a proxy.

    tag is the framing's four-byte identifier. A framing without one cannot be
    obfuscated, because there would be nothing to put in the handshake saying
    what follows, and the full framing is the one in that position.

    dc_id is only read by a proxy, which needs to know where to forward to;
    connecting directly it is ignored and can be left at zero. A negative id
    means a test datacenter, which is why it is written signed.

    secret is the MTProxy shared secret. Without one this is still obfuscation,
    just no one's in particular, which a direct connection wants.
    """
    if len(tag) != 4:
        raise TransportError("this framing has no tag, so it cannot be obfuscated")

    opening = _opening()
    opening[_TAG] = tag
    opening[_DC] = dc_id.to_bytes(2, "little", signed=True)

    out_key, out_iv = bytes(opening[_KEY]), bytes(opening[_IV])
    # The server reads the same window backwards for its own direction, so the
    # client's incoming keys are the mirror of what it sends with.
    mirror = bytes(opening[_MIRROR])[::-1]
    in_key, in_iv = mirror[:32], mirror[32:48]
    if secret:
        out_key = sha256(out_key + secret).digest()
        in_key = sha256(in_key + secret).digest()

    outgoing = new_ctr(out_key, out_iv)
    incoming = new_ctr(in_key, in_iv)

    # The handshake goes out with its own tail encrypted, which both hides the
    # framing tag and advances the keystream by exactly the header, the same
    # sixty-four bytes the server will skip on its side.
    scrambled = outgoing.apply(bytes(opening))
    header = bytes(opening[:56]) + scrambled[56:HEADER_SIZE]
    return Obfuscation(header=header, outgoing=outgoing, incoming=incoming)
