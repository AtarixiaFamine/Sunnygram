# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Proving you know the password without sending it.

Telegram's second factor is SRP, so the password itself never leaves the
machine. What goes to the server is a public value and a proof, and the server
can check the proof against a verifier it stored when the password was set,
without ever having held the password.

Two parts. The first turns the password into a number: two salted hashes and a
hundred thousand rounds of PBKDF2, which makes guessing expensive for
anyone who steals the verifier. The second is the exchange itself, which is
ordinary SRP-6a over the same 2048-bit group the authorization handshake uses,
with Telegram's own choice of what goes into each hash.

Everything wide is hashed as exactly 256 big-endian bytes. That padding is not
cosmetic: without it a value with leading zeroes hashes differently on the two
sides and the proof simply fails, which is the classic way to get this wrong.

The whole module is slow on purpose, PBKDF2 most of all. Call it off the event
loop (rule P1).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from .auth_key import DH_PRIME_BITS, check_dh_parameters

__all__ = ["SRPParameters", "SRPProof", "password_hash", "srp_proof"]

_SIZE = DH_PRIME_BITS // 8
_ITERATIONS = 100_000


@dataclass(frozen=True, slots=True)
class SRPParameters:
    """The group and the salts the server is using for this account.

    Straight out of account.getPassword. The salts belong to the password: they
    were chosen when it was set and are needed to arrive at the same number
    again.
    """

    salt1: bytes
    salt2: bytes
    g: int
    p: bytes


@dataclass(frozen=True, slots=True)
class SRPProof:
    """What the server is sent: a public value and a proof of the password."""

    a: bytes
    m1: bytes

    def __repr__(self) -> str:
        # Neither field is the password, but neither is worth a log either.
        return "SRPProof(<redacted>)"


def _pad(value: int | bytes) -> bytes:
    """A number as the fixed-width big-endian bytes every hash here expects."""
    if isinstance(value, int):
        return value.to_bytes(_SIZE, "big")
    return value.rjust(_SIZE, b"\0")


def _h(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def _salted(data: bytes, salt: bytes) -> bytes:
    """SH: the salt on both sides of what is being hashed."""
    return _h(salt, data, salt)


def password_hash(password: str, salt1: bytes, salt2: bytes) -> bytes:
    """Turn a password into the 32 bytes SRP treats as the secret.

    Two salted hashes to mix the salts in, then PBKDF2 to make each guess
    expensive, then a third salted hash. Telegram calls this PH2, and it is also
    what a client computes when setting a new password, so it is worth having on
    its own.
    """
    inner = _salted(_salted(password.encode(), salt1), salt2)
    stretched = hashlib.pbkdf2_hmac("sha512", inner, salt1, _ITERATIONS)
    return _salted(stretched, salt2)


def srp_proof(
    password: str,
    parameters: SRPParameters,
    server_b: bytes,
    *,
    secret: int | None = None,
) -> SRPProof:
    """Answer the server's challenge for one password attempt.

    secret is our random exponent and exists so a test can pin the exchange to
    known numbers. Leave it alone everywhere else: reusing one across attempts
    would give away more than a single exchange should.
    """
    prime = int.from_bytes(parameters.p, "big")
    g_b = int.from_bytes(server_b, "big")
    a = secrets.randbits(DH_PRIME_BITS) if secret is None else secret
    g_a = pow(parameters.g, a, prime)

    # The group is the server's choice, so it gets the same scrutiny as the one
    # in the authorization handshake, and both public values are checked before
    # either is used for anything.
    check_dh_parameters(parameters.g, prime, g_b, g_a)

    x = int.from_bytes(
        password_hash(password, parameters.salt1, parameters.salt2), "big"
    )
    v = pow(parameters.g, x, prime)
    k = int.from_bytes(_h(_pad(parameters.p), _pad(parameters.g)), "big")
    u = int.from_bytes(_h(_pad(g_a), _pad(g_b)), "big")

    # The verifier the server holds, subtracted out. Everything after this is
    # only reachable by someone who knows the password. The modulo is what the
    # specification writes as "add p back if it went negative".
    k_v = k * v % prime
    t = (g_b - k_v) % prime
    shared = pow(t, a + u * x, prime)

    m1 = _h(
        _xor(_h(_pad(parameters.p)), _h(_pad(parameters.g))),
        _h(parameters.salt1),
        _h(parameters.salt2),
        _pad(g_a),
        _pad(g_b),
        _h(_pad(shared)),
    )
    return SRPProof(a=_pad(g_a), m1=m1)


def _xor(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))
