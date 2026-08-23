# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Telegram's server public keys, and the RSA step of the handshake.

The handshake encrypts exactly one block to a server key, so all the RSA needed
here is a modular exponentiation plus enough DER to read a key. Padding is not
this module's business: MTProto builds its own block, and which scheme applies
belongs with the handshake.

Both keys below come from Telegram Desktop's source and were checked against
TDLib's independent copy, which agrees byte for byte. Refreshing them means
repeating that check, not editing base64 by hand.

Checking the bytes is not enough on its own, though, and this cost a release:
the two were byte-perfect and labelled the wrong way round, so every handshake
with a real datacenter asked for the test key and was refused. Which blob is
which is pinned in tests/test_crypto_rsa.py against the fingerprint a live
production datacenter asks for, because that is the one property no amount of
comparing keys to each other can establish.

A CDN datacenter is named by a different key again, one that is not built in
anywhere: it arrives in the answer to help.getCdnConfig, as PEM text, and is the
only key a handshake with that datacenter may accept. from_pem reads those.

Fingerprints are computed, not written down. A key is named by the low
64 bits of a SHA1 over the bare type rsa_public_key n:string e:string, with n
and e as plain big-endian byte strings. A key damaged in transit would simply
never match anything a server offers.
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Self

from ..errors import SecurityError
from ..tl import TLWriter

__all__ = ["PRODUCTION_KEYS", "TEST_KEYS", "PublicKey", "select_key"]

_PRODUCTION = (
    "MIIBCgKCAQEA6LszBcC1LGzyr992NzE0ieY+BSaOW622Aa9Bd4ZHLl+TuFQ4lo4g5nKa"
    "MBwK/BIb9xUfg0Q29/2mgIR6Zr9krM7HjuIcCzFvDtr+L0GQjae9H0pRB2OO62cECs5H"
    "KhT5DZ98K33vmWiLowc621dQuwKWSQKjWf50XYFw42h21P2KXUGyp2y/+aEyZ+uVgLLQ"
    "bRA1dEjSDZ2iGRy12Mk5gpYc397aYp438fsJoHIgJ2lgMv5h7WY9t6N/byY9Nw9p21Og"
    "3AoXSL2q/2IJ1WRUhebgAdGVMlV1fkuOQoEzR7EdpqtQD9Cs5+bfo3Nhmcyvk5ftB0Wk"
    "J9z6bNZ7yxrP8wIDAQAB"
)
_TEST = (
    "MIIBCgKCAQEAyMEdY1aR+sCR3ZSJrtztKTKqigvO/vBfqACJLZtS7QMgCGXJ6XIRyy7m"
    "x66W0/sOFa7/1mAZtEoIokDP3ShoqF4fVNb6XeqgQfaUHd8wJpDWHcR2OFwvplUUI1PL"
    "TktZ9uW2WE23b+ixNwJjJGwBDJPQEQFBE+vfmH0JP503wr5INS1poWg/j25sIWeYPHYe"
    "OrFp/eXaqhISP6G+q2IeTaWTXpwZj4LzXq5YOpk4bYEQ6mvRq7D1aHWfYmlEGepfaYR8"
    "Q0YqvvhYtMte3ITnuSJs171+GDqpdKcSwHnd6FudwGO4pcCOj4WcDuXc2CTHgH8gFTNh"
    "p/Y8/SpDOhvn9QIDAQAB"
)


@dataclass(frozen=True, slots=True)
class PublicKey:
    """One server key, with the fingerprint a server uses to ask for it."""

    modulus: int
    exponent: int
    fingerprint: int

    @classmethod
    def from_base64(cls, body: str) -> Self:
        modulus, exponent = _parse_pkcs1(base64.b64decode(body))
        return cls(modulus, exponent, _fingerprint(modulus, exponent))

    @classmethod
    def from_pem(cls, text: str) -> Self:
        """Read a key out of the PEM text a server hands over.

        Both spellings are accepted: the bare PKCS#1 one Telegram sends, and
        the wrapped SubjectPublicKeyInfo one, since a key copied out of another
        tool is as likely to be in that.
        """
        return cls.from_base64(_strip_pem(text))

    @property
    def size(self) -> int:
        """The block size in bytes, which is the width of the modulus."""
        return (self.modulus.bit_length() + 7) // 8

    def encrypt(self, block: bytes) -> bytes:
        """Raw textbook RSA, since MTProto pads the block itself."""
        if len(block) > self.size:
            raise ValueError(f"a {len(block)} byte block will not fit this key")
        value = int.from_bytes(block, "big")
        if value >= self.modulus:
            raise ValueError("the block is not smaller than the modulus")
        return pow(value, self.exponent, self.modulus).to_bytes(self.size, "big")


def _big_endian(value: int) -> bytes:
    """A number as the plain big-endian bytes the fingerprint hashes.

    No leading zero, even when the top bit is set. This is a TL string of
    bytes, not a DER integer, so there is no sign to preserve. Getting this
    wrong changes every fingerprint, which is why the retired key and its
    published fingerprint are pinned in the tests.
    """
    return value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")


def _fingerprint(modulus: int, exponent: int) -> int:
    writer = TLWriter()
    writer.write_bytes(_big_endian(modulus))
    writer.write_bytes(_big_endian(exponent))
    digest = hashlib.sha1(writer.getvalue()).digest()
    return int.from_bytes(digest[-8:], "little", signed=True)


def _read_length(der: bytes, offset: int) -> tuple[int, int]:
    length = der[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7F
        length = int.from_bytes(der[offset : offset + count], "big")
        offset += count
    return length, offset


def _read_integer(der: bytes, offset: int) -> tuple[int, int]:
    if der[offset] != 0x02:
        raise ValueError(f"expected a DER integer at offset {offset}")
    length, offset = _read_length(der, offset + 1)
    return int.from_bytes(der[offset : offset + length], "big"), offset + length


def _parse_pkcs1(der: bytes) -> tuple[int, int]:
    """Read a PKCS#1 RSAPublicKey, which is a sequence of two integers.

    A SubjectPublicKeyInfo is that same sequence wrapped in another one, behind
    an algorithm identifier and a bit string, so the wrapper is peeled off here
    instead of in a second parser.
    """
    if not der or der[0] != 0x30:
        raise ValueError("not a DER sequence")
    _, offset = _read_length(der, 1)
    if der[offset : offset + 1] == b"\x30":
        return _parse_pkcs1(_unwrap_spki(der, offset))
    modulus, offset = _read_integer(der, offset)
    exponent, _ = _read_integer(der, offset)
    return modulus, exponent


def _unwrap_spki(der: bytes, offset: int) -> bytes:
    """The PKCS#1 key inside a SubjectPublicKeyInfo.

    The outer sequence holds the algorithm, which is skipped whole, then a bit
    string whose first byte counts the unused bits at the end. That count is
    zero for a key, and anything else is not one.
    """
    algorithm, offset = _read_length(der, offset + 1)
    offset += algorithm
    if der[offset] != 0x03:
        raise ValueError("expected a DER bit string holding the key")
    length, offset = _read_length(der, offset + 1)
    if der[offset] != 0x00:
        raise ValueError("the key bit string does not end on a byte boundary")
    return der[offset + 1 : offset + length]


def _strip_pem(text: str) -> str:
    """The base64 body of a PEM block, without its header and footer."""
    lines = [line.strip() for line in text.strip().splitlines()]
    body = [line for line in lines if line and not line.startswith("-----")]
    if not body:
        raise ValueError("this PEM text holds no key")
    return "".join(body)


PRODUCTION_KEYS: Sequence[PublicKey] = (PublicKey.from_base64(_PRODUCTION),)
TEST_KEYS: Sequence[PublicKey] = (PublicKey.from_base64(_TEST),)


def select_key(
    offered: Iterable[int],
    *,
    test: bool = False,
    keys: Sequence[PublicKey] | None = None,
) -> PublicKey:
    """Pick the key a server asked for, out of the ones we carry.

    keys narrows what counts as ours, which a CDN datacenter needs: it
    is named by a key from help.getCdnConfig and by nothing else, so offering
    it the built-in ones would be accepting the wrong server.
    """
    known = keys if keys is not None else (TEST_KEYS if test else PRODUCTION_KEYS)
    wanted = list(offered)
    for fingerprint in wanted:
        for key in known:
            if key.fingerprint == fingerprint:
                return key
    raise SecurityError(
        "the server offered no key we know: "
        + ", ".join(f"0x{f & 0xFFFFFFFFFFFFFFFF:016x}" for f in wanted)
    )
