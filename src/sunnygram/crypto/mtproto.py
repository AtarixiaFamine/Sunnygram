# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""MTProto 2.0 key derivation.

Every encrypted message carries a msg_key, which does two jobs: it seeds the
AES key and iv for that one message, and it is the integrity check, because it
is a hash of the plaintext under a slice of the auth key that only the two ends
know. Decrypting therefore means deriving, decrypting, then recomputing the
msg_key over what came out and refusing anything that does not match.

The two directions derive from different slices of the auth key, so a message
cannot be reflected back at whoever sent it.
"""

from __future__ import annotations

import hashlib
import hmac

from ..errors import SecurityError

__all__ = [
    "AUTH_KEY_SIZE",
    "auth_key_id",
    "compute_msg_key",
    "derive_key_iv",
    "verify_msg_key",
]

AUTH_KEY_SIZE = 256

# The offset into the auth key that separates the two directions. Client to
# server reads from the start, server to client from eight bytes in.
_OUTGOING = 0
_INCOMING = 8


def _check_auth_key(auth_key: bytes) -> None:
    if len(auth_key) != AUTH_KEY_SIZE:
        raise ValueError(
            f"an auth key is {AUTH_KEY_SIZE} bytes, got {len(auth_key)}"
        )


def auth_key_id(auth_key: bytes) -> bytes:
    """The eight bytes that name this key, sent in front of every message."""
    _check_auth_key(auth_key)
    return hashlib.sha1(auth_key).digest()[-8:]


def compute_msg_key(auth_key: bytes, plaintext: bytes, *, outgoing: bool) -> bytes:
    """The sixteen byte key for one message, taken from the middle of a hash."""
    _check_auth_key(auth_key)
    offset = _OUTGOING if outgoing else _INCOMING
    whole = hashlib.sha256(auth_key[88 + offset : 120 + offset] + plaintext).digest()
    return whole[8:24]


def derive_key_iv(
    auth_key: bytes, msg_key: bytes, *, outgoing: bool
) -> tuple[bytes, bytes]:
    """The AES key and iv for one message.

    Both are woven from two hashes so that neither can be recovered from the
    other, and both change with every message because msg_key does.
    """
    _check_auth_key(auth_key)
    if len(msg_key) != 16:
        raise ValueError(f"a message key is 16 bytes, got {len(msg_key)}")
    offset = _OUTGOING if outgoing else _INCOMING
    first = hashlib.sha256(msg_key + auth_key[offset : 36 + offset]).digest()
    second = hashlib.sha256(auth_key[40 + offset : 76 + offset] + msg_key).digest()
    key = first[0:8] + second[8:24] + first[24:32]
    iv = second[0:8] + first[8:24] + second[24:32]
    return key, iv


def verify_msg_key(
    auth_key: bytes, plaintext: bytes, msg_key: bytes, *, outgoing: bool
) -> None:
    """Check a decrypted body against the key that came with it.

    Compared in constant time (rule S6): this is the check that stands between
    us and someone feeding us a body of their choosing.
    """
    expected = compute_msg_key(auth_key, plaintext, outgoing=outgoing)
    if not hmac.compare_digest(expected, msg_key):
        raise SecurityError("the message key does not match the decrypted body")
