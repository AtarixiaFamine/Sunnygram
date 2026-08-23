"""MTProto 2.0 key derivation.

The interesting part is which slices of the auth key each step reads, so rather
than restate the offsets the tests find them: flip one byte at a time and see
what moves. If a slice ever drifts, the sensitive range changes and these fail.
"""

from __future__ import annotations

import hashlib

import pytest

from sunnygram.crypto import (
    auth_key_id,
    compute_msg_key,
    derive_key_iv,
    verify_msg_key,
)
from sunnygram.errors import SecurityError

AUTH_KEY = bytes(range(256))
PLAINTEXT = b"a plaintext that is a multiple of four bytes long"


def flipped(data: bytes, index: int) -> bytes:
    changed = bytearray(data)
    changed[index] ^= 0xFF
    return bytes(changed)


class TestAuthKeyId:
    def test_is_the_tail_of_the_sha1(self):
        assert auth_key_id(AUTH_KEY) == hashlib.sha1(AUTH_KEY).digest()[-8:]
        assert len(auth_key_id(AUTH_KEY)) == 8

    def test_rejects_a_key_of_the_wrong_size(self):
        with pytest.raises(ValueError, match="256 bytes"):
            auth_key_id(bytes(255))


class TestMsgKey:
    def test_size_and_determinism(self):
        first = compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=True)
        assert len(first) == 16
        assert first == compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=True)

    def test_directions_differ(self):
        assert compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=True) != compute_msg_key(
            AUTH_KEY, PLAINTEXT, outgoing=False
        )

    def test_follows_the_plaintext(self):
        assert compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=True) != compute_msg_key(
            AUTH_KEY, PLAINTEXT + b"\x00\x00\x00\x00", outgoing=True
        )

    @pytest.mark.parametrize(
        "outgoing,sensitive", [(True, range(88, 120)), (False, range(96, 128))]
    )
    def test_reads_exactly_one_slice_of_the_auth_key(self, outgoing, sensitive):
        base = compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=outgoing)
        expected = set(sensitive)
        for index in range(256):
            moved = (
                compute_msg_key(flipped(AUTH_KEY, index), PLAINTEXT, outgoing=outgoing)
                != base
            )
            assert moved == (index in expected), index


class TestKeyAndIv:
    def test_sizes(self):
        key, iv = derive_key_iv(AUTH_KEY, bytes(16), outgoing=True)
        assert len(key) == 32
        assert len(iv) == 32
        assert key != iv

    def test_directions_differ(self):
        assert derive_key_iv(AUTH_KEY, bytes(16), outgoing=True) != derive_key_iv(
            AUTH_KEY, bytes(16), outgoing=False
        )

    def test_follows_the_message_key(self):
        assert derive_key_iv(AUTH_KEY, bytes(16), outgoing=True) != derive_key_iv(
            AUTH_KEY, b"\x01" * 16, outgoing=True
        )

    @pytest.mark.parametrize(
        "outgoing,sensitive",
        [
            (True, set(range(0, 36)) | set(range(40, 76))),
            (False, set(range(8, 44)) | set(range(48, 84))),
        ],
    )
    def test_reads_exactly_two_slices_of_the_auth_key(self, outgoing, sensitive):
        msg_key = bytes(range(16))
        base = derive_key_iv(AUTH_KEY, msg_key, outgoing=outgoing)
        for index in range(256):
            moved = (
                derive_key_iv(flipped(AUTH_KEY, index), msg_key, outgoing=outgoing)
                != base
            )
            assert moved == (index in sensitive), index

    def test_rejects_a_message_key_of_the_wrong_size(self):
        with pytest.raises(ValueError, match="16 bytes"):
            derive_key_iv(AUTH_KEY, bytes(15), outgoing=True)


class TestVerification:
    def test_accepts_a_matching_body(self):
        msg_key = compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=False)
        verify_msg_key(AUTH_KEY, PLAINTEXT, msg_key, outgoing=False)

    def test_refuses_a_substituted_body(self):
        msg_key = compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=False)
        with pytest.raises(SecurityError):
            verify_msg_key(AUTH_KEY, PLAINTEXT + b"\x00" * 4, msg_key, outgoing=False)

    def test_refuses_a_body_from_the_other_direction(self):
        msg_key = compute_msg_key(AUTH_KEY, PLAINTEXT, outgoing=True)
        with pytest.raises(SecurityError):
            verify_msg_key(AUTH_KEY, PLAINTEXT, msg_key, outgoing=False)
