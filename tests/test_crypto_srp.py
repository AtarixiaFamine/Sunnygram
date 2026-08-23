"""SRP, checked against a server that holds a verifier and does the other half.

There are no published vectors for Telegram's variant, so the test is the same
shape as the handshake one: the server side is implemented here, from the
specification rather than from our own code, and the two have to agree. It
stores a verifier the way Telegram does when a password is set, issues a
challenge from it, and recomputes M1 from its own side of the exchange.

That catches the mistakes this algorithm actually invites. Every wide value is
hashed as 256 bytes, so an unpadded one still produces a proof, just not the
same proof, and only a test that computes M1 independently notices.
"""

from __future__ import annotations

import hashlib
import secrets

import pytest

from sunnygram.crypto import SRPParameters, password_hash, srp_proof
from sunnygram.errors import SecurityError

# Telegram's own 2048-bit SRP group, which is the one every account uses.
PRIME = int(
    "C71CAEB9C6B1C9048E6C522F70F13F73980D40238E3E21C14934D037563D930F"
    "48198A0AA7C14058229493D22530F4DBFA336F6E0AC925139543AED44CCE7C37"
    "20FD51F69458705AC68CD4FE6B6B13ABDC9746512969328454F18FAF8C595F64"
    "2477FE96BB2A941D5BCD1D4AC8CC49880708FA9B378E3C4F3A9060BEE67CF9A4"
    "A4A695811051907E162753B56B0F6B410DBA74D8A84B2A14B3144E0EF1284754"
    "FD17ED950D5965B4B9DD46582DB1178D169C6BC465B0D6FF9CA3928FEF5B9AE4"
    "E418FC15E83EBEA0F87FA9FF5EED70050DED2849F47BF959D956850CE929851F"
    "0D8115F635B105EE2E4E15D04B2454BF6F4FADF034B10403119CD8E3B92FCC5B",
    16,
)
G = 3
SIZE = 256


def pad(value: int | bytes) -> bytes:
    if isinstance(value, int):
        return value.to_bytes(SIZE, "big")
    return value.rjust(SIZE, b"\0")


def sha256(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def parameters(salt1: bytes = b"\x01" * 8, salt2: bytes = b"\x02" * 16) -> SRPParameters:
    return SRPParameters(salt1=salt1, salt2=salt2, g=G, p=pad(PRIME))


class Server:
    """The account side: it knows the verifier, never the password."""

    def __init__(self, password: str, params: SRPParameters) -> None:
        # Written from the specification, deliberately not by calling ours.
        first = sha256(params.salt1, password.encode(), params.salt1)
        second = sha256(params.salt2, first, params.salt2)
        stretched = hashlib.pbkdf2_hmac("sha512", second, params.salt1, 100_000)
        x = int.from_bytes(sha256(params.salt2, stretched, params.salt2), "big")

        self.params = params
        self.verifier = pow(params.g, x, PRIME)
        self.b = secrets.randbits(2048)
        self.k = int.from_bytes(sha256(pad(PRIME), pad(params.g)), "big")

    @property
    def challenge(self) -> bytes:
        """srp_B, which is the verifier and a fresh secret mixed together."""
        return pad((self.k * self.verifier + pow(self.params.g, self.b, PRIME)) % PRIME)

    def expected_m1(self, client_a: bytes) -> bytes:
        """What the client's proof has to come out as, from this side."""
        g_a = int.from_bytes(client_a, "big")
        u = int.from_bytes(sha256(pad(g_a), self.challenge), "big")
        shared = pow(g_a * pow(self.verifier, u, PRIME), self.b, PRIME)
        return sha256(
            bytes(
                a ^ b
                for a, b in zip(
                    sha256(pad(PRIME)), sha256(pad(self.params.g))
                )
            ),
            sha256(self.params.salt1),
            sha256(self.params.salt2),
            pad(g_a),
            self.challenge,
            sha256(pad(shared)),
        )


class TestPasswordHash:
    def test_the_salts_change_the_result(self):
        first = password_hash("hunter2", b"\x01" * 8, b"\x02" * 8)
        second = password_hash("hunter2", b"\x01" * 8, b"\x03" * 8)
        assert first != second
        assert len(first) == 32

    def test_the_password_changes_the_result(self):
        salts = (b"\x01" * 8, b"\x02" * 8)
        assert password_hash("hunter2", *salts) != password_hash("hunter3", *salts)

    def test_it_is_deterministic(self):
        salts = (b"\x01" * 8, b"\x02" * 8)
        assert password_hash("hunter2", *salts) == password_hash("hunter2", *salts)

    def test_a_password_is_utf8_not_bytes(self):
        # Non-ascii passwords are ordinary, and the encoding has to be the one
        # every other client uses or the proof will not match.
        salts = (b"\x01" * 8, b"\x02" * 8)
        assert password_hash("pässwörd", *salts) == password_hash(
            "pässwörd", *salts
        )


class TestProof:
    def test_the_server_accepts_the_proof(self):
        params = parameters()
        server = Server("hunter2", params)
        proof = srp_proof("hunter2", params, server.challenge)
        assert proof.m1 == server.expected_m1(proof.a)

    def test_a_wrong_password_does_not_prove_anything(self):
        params = parameters()
        server = Server("hunter2", params)
        proof = srp_proof("hunter3", params, server.challenge)
        assert proof.m1 != server.expected_m1(proof.a)

    def test_every_attempt_uses_a_fresh_secret(self):
        params = parameters()
        server = Server("hunter2", params)
        first = srp_proof("hunter2", params, server.challenge)
        second = srp_proof("hunter2", params, server.challenge)
        assert first.a != second.a
        assert first.m1 != second.m1

    def test_a_pinned_exchange_is_reproducible(self):
        params = parameters()
        server = Server("hunter2", params)
        challenge = server.challenge
        first = srp_proof("hunter2", params, challenge, secret=12345)
        second = srp_proof("hunter2", params, challenge, secret=12345)
        assert first == second
        assert first.m1 == server.expected_m1(first.a)

    def test_the_public_value_is_full_width(self):
        params = parameters()
        server = Server("hunter2", params)
        assert len(srp_proof("hunter2", params, server.challenge).a) == 256

    def test_the_salts_have_to_be_the_accounts_own(self):
        server = Server("hunter2", parameters())
        # Same password, different salts, so a different secret and no proof.
        wrong = parameters(salt1=b"\x09" * 8, salt2=b"\x08" * 16)
        proof = srp_proof("hunter2", wrong, server.challenge)
        assert proof.m1 != server.expected_m1(proof.a)

    def test_a_challenge_outside_the_group_is_refused(self):
        params = parameters()
        with pytest.raises(SecurityError):
            srp_proof("hunter2", params, pad(1))
        with pytest.raises(SecurityError):
            srp_proof("hunter2", params, pad(PRIME - 1))

    def test_a_group_that_is_not_telegrams_is_refused(self):
        # The server chooses p and g, so they get the same scrutiny the
        # authorization handshake gives them.
        composite = SRPParameters(
            salt1=b"\x01" * 8, salt2=b"\x02" * 8, g=G, p=pad(PRIME - 2)
        )
        with pytest.raises(SecurityError):
            srp_proof("hunter2", composite, pad(2**2000))

    def test_the_proof_never_stringifies(self):
        params = parameters()
        server = Server("hunter2", params)
        proof = srp_proof("hunter2", params, server.challenge)
        assert proof.a.hex()[:16] not in repr(proof)
        assert "redacted" in repr(proof)
