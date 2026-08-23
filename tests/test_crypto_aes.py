"""AES and the two modes MTProto uses.

The block cipher is pinned to the FIPS-197 known answers. The modes are checked
against their own definitions, spelled out here byte by byte, so a mistake in
the fast paths cannot hide behind the same mistake in the test.
"""

from __future__ import annotations

import os

import pytest
from conftest import xor

from sunnygram.crypto import (
    AES,
    BACKEND,
    CTR,
    ige256_decrypt,
    ige256_decrypt_python,
    ige256_encrypt,
    ige256_encrypt_python,
)

PLAIN_BLOCK = bytes.fromhex("00112233445566778899aabbccddeeff")

FIPS_197 = [
    (
        bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
        bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a"),
    ),
    (
        bytes.fromhex("000102030405060708090a0b0c0d0e0f1011121314151617"),
        bytes.fromhex("dda97ca4864cdfe06eaf70a0ec0d7191"),
    ),
    (
        bytes.fromhex(
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
        ),
        bytes.fromhex("8ea2b7ca516745bfeafc49904b496089"),
    ),
]

KEY = bytes(range(32))
IGE_IV = bytes(range(32, 64))
CTR_IV = bytes(range(16))


class TestBlockCipher:
    @pytest.mark.parametrize("key,expected", FIPS_197)
    def test_encrypt_matches_fips_197(self, key, expected):
        assert AES(key).encrypt_block(PLAIN_BLOCK) == expected

    @pytest.mark.parametrize("key,ciphertext", FIPS_197)
    def test_decrypt_matches_fips_197(self, key, ciphertext):
        assert AES(key).decrypt_block(ciphertext) == PLAIN_BLOCK

    def test_bad_key_length(self):
        with pytest.raises(ValueError):
            AES(bytes(20))

    def test_bad_block_length(self):
        cipher = AES(KEY)
        with pytest.raises(ValueError):
            cipher.encrypt_block(bytes(15))
        with pytest.raises(ValueError):
            cipher.decrypt_block(bytes(17))


class TestIge:
    def test_round_trip(self):
        data = os.urandom(64)
        assert ige256_decrypt(ige256_encrypt(data, KEY, IGE_IV), KEY, IGE_IV) == data

    def test_encryption_matches_the_definition(self):
        data = os.urandom(48)
        cipher = AES(KEY)
        previous_cipher, previous_plain = IGE_IV[:16], IGE_IV[16:]
        expected = b""
        for offset in range(0, len(data), 16):
            block = data[offset : offset + 16]
            current = xor(
                cipher.encrypt_block(xor(block, previous_cipher)), previous_plain
            )
            expected += current
            previous_cipher, previous_plain = current, block
        assert ige256_encrypt_python(data, KEY, IGE_IV) == expected

    def test_decryption_matches_the_definition(self):
        data = os.urandom(48)
        cipher = AES(KEY)
        previous_cipher, previous_plain = IGE_IV[:16], IGE_IV[16:]
        expected = b""
        for offset in range(0, len(data), 16):
            block = data[offset : offset + 16]
            plain = xor(
                cipher.decrypt_block(xor(block, previous_plain)), previous_cipher
            )
            expected += plain
            previous_cipher, previous_plain = block, plain
        assert ige256_decrypt_python(data, KEY, IGE_IV) == expected

    def test_every_block_depends_on_the_one_before(self):
        first = ige256_encrypt_python(bytes(32), KEY, IGE_IV)
        assert first[:16] != first[16:]

    def test_partial_block_is_refused(self):
        with pytest.raises(ValueError):
            ige256_encrypt_python(bytes(24), KEY, IGE_IV)

    def test_wrong_key_or_iv_size_is_refused(self):
        with pytest.raises(ValueError):
            ige256_encrypt_python(bytes(16), bytes(16), IGE_IV)
        with pytest.raises(ValueError):
            ige256_encrypt_python(bytes(16), KEY, bytes(16))

    @pytest.mark.skipif(BACKEND == "python", reason="no native backend installed")
    def test_native_backend_agrees_with_python(self):
        data = os.urandom(96)
        assert ige256_encrypt(data, KEY, IGE_IV) == ige256_encrypt_python(
            data, KEY, IGE_IV
        )
        assert ige256_decrypt(data, KEY, IGE_IV) == ige256_decrypt_python(
            data, KEY, IGE_IV
        )


class TestCtr:
    def test_keystream_is_the_encrypted_counter(self):
        cipher = AES(KEY)
        counter = int.from_bytes(CTR_IV, "big")
        expected = b""
        for _ in range(4):
            expected += cipher.encrypt_block(counter.to_bytes(16, "big"))
            counter += 1
        # Applying counter mode to zeros hands back the raw keystream.
        assert CTR(KEY, CTR_IV).apply(bytes(64)) == expected

    def test_symmetric(self):
        data = os.urandom(100)
        encrypted = CTR(KEY, CTR_IV).encrypt(data)
        assert encrypted != data
        assert CTR(KEY, CTR_IV).decrypt(encrypted) == data

    def test_resumes_inside_a_block(self):
        data = os.urandom(100)
        one_shot = CTR(KEY, CTR_IV).apply(data)
        cipher = CTR(KEY, CTR_IV)
        streamed = b"".join(
            cipher.apply(chunk)
            for chunk in (data[:5], data[5:20], data[20:64], data[64:])
        )
        assert streamed == one_shot

    def test_leading_zero_bytes_survive(self):
        data = bytes(8) + os.urandom(8)
        assert len(CTR(KEY, CTR_IV).apply(data)) == 16

    def test_empty_input(self):
        assert CTR(KEY, CTR_IV).apply(b"") == b""

    def test_bad_iv_length(self):
        with pytest.raises(ValueError):
            CTR(KEY, bytes(8))
