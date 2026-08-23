# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The envelope every MTProto message travels in.

There are two. Before there is an auth key, messages go in the clear with a
zero key id in front, which is how the handshake talks. Afterwards everything
is wrapped in the encrypted form: the key id, the message key, and an AES-IGE
blob whose plaintext carries the salt, the session, the id, the sequence number
and the body.

Reading the encrypted form has a strict order. The message key is verified
against the decrypted bytes before a single field inside them is believed,
because until that check passes the plaintext is whatever an attacker wanted it
to be. Only then are the lengths read, and they are bounds-checked too: a
length that does not fit inside what was actually decrypted is a forgery, not a
short read.
"""

from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass

from ..crypto import (
    auth_key_id,
    compute_msg_key,
    derive_key_iv,
    ige256_decrypt,
    ige256_encrypt,
    verify_msg_key,
)
from ..errors import SecurityError
from ..tl import GZIP_PACKED, TLReader, unpack_gzip
from ..utils import signed

__all__ = [
    "CONTAINER_ID",
    "HEADER_SIZE",
    "RPC_RESULT_ID",
    "MAX_PADDING",
    "MIN_PADDING",
    "Message",
    "pack_encrypted",
    "pack_plaintext",
    "signed_long",
    "unpack_encrypted",
    "unpack_plaintext",
    "unwrap_container",
]

# Three constructors the schema comments out because they cannot be generated:
# a container holds bare messages with no ids of their own, and a result holds
# whatever the call it answers returns.
CONTAINER_ID = 0x73F1F8DC
RPC_RESULT_ID = 0xF35C6D01

# A message inside a container costs at least this much: id, sequence number,
# length, and a constructor for the body.
_SMALLEST_MESSAGE = 8 + 4 + 4 + 4

# salt, session id, message id, sequence number, body length.
HEADER_SIZE = 8 + 8 + 8 + 4 + 4

# The protocol requires at least twelve bytes of padding, so the tail of the
# plaintext is never predictable, and allows up to a kilobyte of it.
MIN_PADDING = 12
MAX_PADDING = 1024

_PLAINTEXT_HEADER = 8 + 8 + 4


@dataclass(frozen=True, slots=True)
class Message:
    """One message inside an envelope."""

    msg_id: int
    seq_no: int
    body: bytes


def _long(value: int) -> bytes:
    """Eight little-endian bytes, whichever way the value was spelled.

    Salts and session ids are opaque 64-bit patterns that arrive signed from
    the codec and get generated unsigned, so both are accepted.
    """
    return (value & ((1 << 64) - 1)).to_bytes(8, "little")


def signed_long(value: int) -> int:
    """A 64-bit pattern as the signed integer TL reads back."""
    return signed(value, 64)


def pack_plaintext(msg_id: int, body: bytes) -> bytes:
    """Wrap a message for a connection that has no key yet."""
    return bytes(8) + _long(msg_id) + len(body).to_bytes(4, "little") + body


def unpack_plaintext(frame: bytes) -> tuple[int, bytes]:
    """Read a keyless message, returning its id and body."""
    if len(frame) < _PLAINTEXT_HEADER:
        raise SecurityError(f"a message cannot be {len(frame)} bytes long")
    if frame[:8] != bytes(8):
        raise SecurityError("this message is encrypted, not plaintext")
    msg_id = int.from_bytes(frame[8:16], "little", signed=True)
    length = int.from_bytes(frame[16:20], "little", signed=True)
    if length < 0 or length % 4 or _PLAINTEXT_HEADER + length != len(frame):
        raise SecurityError(
            f"the body claims {length} bytes but the message holds "
            f"{len(frame) - _PLAINTEXT_HEADER}"
        )
    return msg_id, frame[_PLAINTEXT_HEADER:]


def pack_encrypted(
    auth_key: bytes,
    salt: int,
    session_id: int,
    message: Message,
    *,
    outgoing: bool = True,
) -> bytes:
    """Wrap and encrypt a message under an auth key.

    outgoing means the message travels from client to server, which decides
    which half of the auth key keys it. A client packs with the default and
    unpacks with outgoing=False; anything standing in for a server flips both.
    """
    header = (
        _long(salt)
        + _long(session_id)
        + _long(message.msg_id)
        + message.seq_no.to_bytes(4, "little")
        + len(message.body).to_bytes(4, "little")
    )
    # The header is already a whole number of blocks, so the padding only has
    # to square up the body, and then reach the twelve byte minimum.
    padding = -len(message.body) % 16
    if padding < MIN_PADDING:
        padding += 16
    plaintext = header + message.body + secrets.token_bytes(padding)

    msg_key = compute_msg_key(auth_key, plaintext, outgoing=outgoing)
    key, iv = derive_key_iv(auth_key, msg_key, outgoing=outgoing)
    return auth_key_id(auth_key) + msg_key + ige256_encrypt(plaintext, key, iv)


def unpack_encrypted(
    auth_key: bytes, frame: bytes, *, outgoing: bool = False
) -> tuple[int, Message]:
    """Decrypt and validate a message, returning the session id and the message.

    Everything here is a check the security guidelines ask for, in the order
    they have to happen in. See pack_encrypted for what outgoing means.
    """
    if len(frame) <= 24 or (len(frame) - 24) % 16:
        raise SecurityError(f"a {len(frame)} byte frame is not a whole envelope")
    if not hmac.compare_digest(frame[:8], auth_key_id(auth_key)):
        raise SecurityError("this message was encrypted to a different key")

    msg_key = frame[8:24]
    key, iv = derive_key_iv(auth_key, msg_key, outgoing=outgoing)
    plaintext = ige256_decrypt(frame[24:], key, iv)
    # Nothing below this line would be safe to read before this call returns.
    verify_msg_key(auth_key, plaintext, msg_key, outgoing=outgoing)

    if len(plaintext) < HEADER_SIZE:
        raise SecurityError("the decrypted message is too short to hold a header")
    session_id = int.from_bytes(plaintext[8:16], "little", signed=True)
    msg_id = int.from_bytes(plaintext[16:24], "little", signed=True)
    seq_no = int.from_bytes(plaintext[24:28], "little")
    length = int.from_bytes(plaintext[28:32], "little", signed=True)

    available = len(plaintext) - HEADER_SIZE
    if length < 0 or length % 4 or length > available:
        raise SecurityError(
            f"the body claims {length} bytes of the {available} decrypted"
        )
    padding = available - length
    if not MIN_PADDING <= padding <= MAX_PADDING:
        raise SecurityError(f"{padding} bytes of padding is outside the allowed range")

    return session_id, Message(
        msg_id, seq_no, plaintext[HEADER_SIZE : HEADER_SIZE + length]
    )


def unwrap_container(message: Message) -> list[Message]:
    """Flatten one decrypted message into the messages it really carries.

    A server is free to bundle several answers into one container to save round
    trips, and to gzip a body that compresses well. Both are unwrapped here so
    everything above sees a plain list of messages.

    The container and the bare messages inside it are the constructors the
    schema leaves commented out, because a container holds messages with no
    constructor id of their own and so cannot be generated. Containers do not
    nest, so this does not recurse.
    """
    body = message.body
    if _peek(body) == GZIP_PACKED:
        reader = TLReader(body)
        reader.read_int(signed=False)
        body = unpack_gzip(reader.read_bytes())

    if _peek(body) != CONTAINER_ID:
        return [Message(message.msg_id, message.seq_no, body)]

    reader = TLReader(body)
    reader.read_int(signed=False)
    count = reader.read_int()
    if count < 0 or count > reader.remaining // _SMALLEST_MESSAGE:
        raise SecurityError(
            f"a container of {len(body)} bytes cannot hold {count} messages"
        )

    held = []
    for _ in range(count):
        msg_id = reader.read_long()
        seq_no = reader.read_int()
        size = reader.read_int()
        if size < 4 or size % 4 or size > reader.remaining:
            raise SecurityError(f"a message inside a container cannot be {size} bytes")
        held.append(Message(msg_id, seq_no, reader.read_raw(size)))
    return held


def _peek(body: bytes) -> int | None:
    """The constructor id at the front of a body, if there is room for one."""
    if len(body) < 4:
        return None
    return int.from_bytes(body[:4], "little")
