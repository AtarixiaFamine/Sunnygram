# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Creating an authorization key.

The handshake is a Diffie-Hellman exchange wrapped in one RSA-encrypted block.
This module is the arithmetic half of it: building that block, deriving the
temporary keys, checking what the server sent back, and turning the shared
secret into an auth key. Deciding what to send when belongs upstairs, which
keeps all of this pure and testable without a socket.

Every step here follows core.telegram.org/mtproto/auth_key and was checked
against TDLib's implementation, which is the reference in practice.

The checks in check_dh_parameters are the security of the whole connection.
A server that hands over a prime that is not safe, or a g_a near the edges of
the group, can force a shared secret with little entropy. Everything is
verified before the key is used, and a failure is fatal instead of a retry.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections import OrderedDict
from collections.abc import Callable

from ..errors import SecurityError
from .accel import ige256_encrypt
from .rsa import PublicKey

__all__ = [
    "DH_PRIME_BITS",
    "MAX_INNER_DATA",
    "check_dh_parameters",
    "derive_auth_key",
    "generate_b",
    "new_nonce_hash",
    "pad_block",
    "rsa_pad",
    "server_salt",
    "temp_key_iv",
    "unwrap_answer",
    "wrap_client_data",
]

DH_PRIME_BITS = 2048

# The inner data is padded out to 192 bytes, and the RSA block holds that plus
# a 32 byte hash and a 32 byte disguised key.
MAX_INNER_DATA = 144
_PADDED_SIZE = 192
_BLOCK_SIZE = 256

# g is only ever one of these, and each carries a condition on the prime that
# proves g generates a large enough subgroup. Quadratic reciprocity turns each
# one into a cheap remainder check.
_G_CONDITIONS: dict[int, Callable[[int], bool]] = {
    2: lambda prime: prime % 8 == 7,
    3: lambda prime: prime % 3 == 2,
    4: lambda prime: True,
    5: lambda prime: prime % 5 in (1, 4),
    6: lambda prime: prime % 24 in (19, 23),
    7: lambda prime: prime % 7 in (3, 5, 6),
}

_SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251,
)

# Verifying a safe prime costs a noticeable slice of a second, and a server
# sends the same one every time, so the answer is remembered. Bounded, because
# everything that grows is bounded (rule P6).
_CHECKED_PRIMES: OrderedDict[int, bool] = OrderedDict()
_CHECKED_PRIMES_LIMIT = 8


def _nonce_bytes(value: int, size: int) -> bytes:
    """A nonce back in the little-endian form it arrived in.

    A nonce is an opaque bit pattern, not a quantity. The codec reads int128
    and int256 as signed, while anything generating one reaches for unsigned
    random bits, so the value is masked to width and both spellings of the same
    wire bytes land in the same place.
    """
    width = size * 8
    if not -(1 << (width - 1)) <= value < (1 << width):
        raise ValueError(f"{value} does not fit in an int{width} nonce")
    return (value & ((1 << width) - 1)).to_bytes(size, "little")


def pad_block(data: bytes) -> bytes:
    """Wrap the inner data into the 256 byte block RSA takes.

    Telegram calls this RSA_PAD. It exists because textbook RSA over a
    predictable block would be forgeable, so the payload is padded, reversed,
    bound to a random key by a hash, encrypted with that key, and finally the
    key itself is hidden behind a hash of the ciphertext. The server undoes it
    in the same order.
    """
    if len(data) > MAX_INNER_DATA:
        raise ValueError(
            f"the inner data is {len(data)} bytes, over the {MAX_INNER_DATA} limit"
        )
    padded = data + secrets.token_bytes(_PADDED_SIZE - len(data))
    aes_key = secrets.token_bytes(32)
    # The hash covers the payload the right way round, and only then is the
    # payload reversed. Order matters: the server reverses before hashing.
    with_hash = padded[::-1] + hashlib.sha256(aes_key + padded).digest()
    encrypted = ige256_encrypt(with_hash, aes_key, bytes(32))
    disguise = hashlib.sha256(encrypted).digest()
    hidden_key = bytes(a ^ b for a, b in zip(aes_key, disguise))
    return hidden_key + encrypted


def rsa_pad(data: bytes, key: PublicKey, *, attempts: int = 64) -> bytes:
    """Build a padded block that fits under the modulus, and encrypt it.

    A block is a uniform 256 byte number, so now and then it lands above the
    modulus and has to be rebuilt. That is expected, not an error.
    """
    for _ in range(attempts):
        block = pad_block(data)
        if int.from_bytes(block, "big") < key.modulus:
            return key.encrypt(block)
    raise SecurityError("could not build a padded block below the modulus")


def temp_key_iv(server_nonce: int, new_nonce: int) -> tuple[bytes, bytes]:
    """The throwaway AES key and iv that protect the DH exchange itself.

    Both sides can derive these from the nonces: they
    protect the exchange from a passive watcher, not from the server.
    """
    server = _nonce_bytes(server_nonce, 16)
    new = _nonce_bytes(new_nonce, 32)
    first = hashlib.sha1(new + server).digest()
    second = hashlib.sha1(server + new).digest()
    third = hashlib.sha1(new + new).digest()
    return first + second[:12], second[12:20] + third + new[:4]


def _is_probable_prime(value: int, rounds: int = 32) -> bool:
    """Miller-Rabin. Thirty-two rounds leaves a worse chance than a hash collision."""
    if value < 2:
        return False
    for small in _SMALL_PRIMES:
        if value == small:
            return True
        if value % small == 0:
            return False

    odd = value - 1
    twos = 0
    while not odd & 1:
        odd >>= 1
        twos += 1

    for _ in range(rounds):
        witness = 2 + secrets.randbelow(value - 3)
        residue = pow(witness, odd, value)
        if residue in (1, value - 1):
            continue
        for _ in range(twos - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


def _is_safe_prime(prime: int) -> bool:
    """Both p and (p-1)/2 prime, which makes the group hard to break."""
    remembered = _CHECKED_PRIMES.get(prime)
    if remembered is not None:
        _CHECKED_PRIMES.move_to_end(prime)
        return remembered

    verdict = _is_probable_prime(prime) and _is_probable_prime((prime - 1) // 2)
    _CHECKED_PRIMES[prime] = verdict
    if len(_CHECKED_PRIMES) > _CHECKED_PRIMES_LIMIT:
        _CHECKED_PRIMES.popitem(last=False)
    return verdict


def check_dh_parameters(g: int, dh_prime: int, *powers: int) -> None:
    """Verify everything the server chose, before anything is derived from it.

    powers are the public values in play, g_a from the server and g_b once we
    have it. Both get the same treatment.

    This runs a primality test on a 2048-bit number the first time it sees one,
    which takes long enough to matter. Call it off the event loop (rule P1);
    repeats are answered from cache.
    """
    if dh_prime.bit_length() != DH_PRIME_BITS:
        raise SecurityError(
            f"dh_prime is {dh_prime.bit_length()} bits, not {DH_PRIME_BITS}"
        )
    condition = _G_CONDITIONS.get(g)
    if condition is None:
        raise SecurityError(f"g is {g}, which is not one of 2 to 7")
    if not condition(dh_prime):
        raise SecurityError(f"dh_prime does not satisfy the condition for g={g}")
    if not _is_safe_prime(dh_prime):
        raise SecurityError("dh_prime is not a safe prime")

    # Away from the edges of the group, so the shared secret cannot be forced
    # into a small set of possibilities.
    floor = 1 << (DH_PRIME_BITS - 64)
    ceiling = dh_prime - floor
    if not 1 < g < dh_prime - 1:
        raise SecurityError("g is not inside the group")
    for power in powers:
        if not 1 < power < dh_prime - 1:
            raise SecurityError("a public value is not inside the group")
        if not floor <= power <= ceiling:
            raise SecurityError("a public value sits too close to the edge of the group")


def wrap_client_data(data: bytes) -> bytes:
    """Put our DH half in the envelope the server expects.

    A SHA1 in front and random padding behind, out to a whole AES block.
    """
    body = hashlib.sha1(data).digest() + data
    return body + secrets.token_bytes(-len(body) % 16)


def unwrap_answer(plaintext: bytes) -> bytes:
    """Take the server's DH half out of its envelope, checking the hash.

    The envelope is SHA1(answer) + answer + up to 15 random bytes, and the
    length of answer is nowhere in it. Rather than parse the payload to find
    out, every allowed padding length is tried and only the one whose hash
    matches is accepted, so the hash remains the sole thing being trusted.

    Required by Telegram's security guidelines: an answer that does not match
    its hash is discarded instead of parsed.
    """
    if len(plaintext) < 20 or len(plaintext) % 16:
        raise SecurityError(
            f"the encrypted answer is {len(plaintext)} bytes, "
            "which is not a whole number of blocks holding a hash"
        )
    expected = plaintext[:20]
    body = plaintext[20:]
    for padding in range(16):
        candidate = body[: len(body) - padding]
        if hmac.compare_digest(hashlib.sha1(candidate).digest(), expected):
            return candidate
    raise SecurityError("the server's answer does not match its own hash")


def generate_b() -> int:
    """Our secret exponent, freshly random for every handshake."""
    return secrets.randbits(DH_PRIME_BITS)


def derive_auth_key(g_a: int, b: int, dh_prime: int) -> bytes:
    """The shared secret, as the 256 bytes every later message is keyed from."""
    return pow(g_a, b, dh_prime).to_bytes(256, "big")


def new_nonce_hash(new_nonce: int, auth_key: bytes, number: int) -> int:
    """The value the server echoes to prove it derived the same key.

    number is 1, 2 or 3, matching the ok, retry and fail answers, so a reply
    to one cannot be replayed as a reply to another.
    """
    if number not in (1, 2, 3):
        raise ValueError(f"the nonce hash number is 1, 2 or 3, not {number}")
    auxiliary = hashlib.sha1(auth_key).digest()[:8]
    digest = hashlib.sha1(
        _nonce_bytes(new_nonce, 32) + bytes([number]) + auxiliary
    ).digest()
    return int.from_bytes(digest[4:20], "little", signed=True)


def server_salt(new_nonce: int, server_nonce: int) -> int:
    """The first salt, which both sides can work out from the nonces."""
    new = _nonce_bytes(new_nonce, 32)[:8]
    server = _nonce_bytes(server_nonce, 16)[:8]
    return int.from_bytes(
        bytes(a ^ b for a, b in zip(new, server)), "little", signed=True
    )
