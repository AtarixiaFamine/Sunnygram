"""The server keys and the RSA step.

The vendored keys are checked for shape rather than against a written-down
fingerprint: the fingerprint is derived from the key, so writing one down would
only restate what the code computes. The arithmetic is pinned with the textbook
key instead, which is small enough to decrypt inside the test.
"""

from __future__ import annotations

import pytest

from sunnygram.crypto import PRODUCTION_KEYS, TEST_KEYS, PublicKey, select_key
from sunnygram.crypto.rsa import _big_endian, _parse_pkcs1
from sunnygram.errors import SecurityError

# n = 61 * 53, e = 17, d = 2753. The worked example from every RSA writeup,
# used here because it can be undone without a private key of Telegram's.
TEXTBOOK = PublicKey(modulus=3233, exponent=17, fingerprint=0)
TEXTBOOK_PRIVATE = 2753

# Telegram's pre-2021 server key, retired but not forgotten: its fingerprint is
# published, which makes it the one key whose fingerprint can be checked
# against a number we did not compute ourselves. Getting the modulus encoding
# wrong (a DER-style leading zero, say) changes this and nothing else, so it is
# the only thing standing between a subtle mistake and a handshake that fails
# against every server for no visible reason.
RETIRED_KEY = (
    "MIIBCgKCAQEAwVACPi9w23mF3tBkdZz+zwrzKOaaQdr01vAbU4E1pvkfj4sqDsm6ly"
    "DONS789sVoD/xCS9Y0hkkC3gtL1tSfTlgCMOOul9lcixlEKzwKENj1Yz/s7daSan9t"
    "qw3bfUV/nqgbhGX81v/+7RFAEd+RwFnK7a+XYl9sluzHRyVVaTTveB2GazTwEfzk2D"
    "WgkBluml8OREmvfraX3bkHZJTKX4EQSjBbbdJ2ZXIsRrYOXfaA+xayEGB+8hdlLmAj"
    "bCVfaigxX0CDqWeR1yFL9kwd9P0NsZRPsmoqVwMbMu7mStFai6aIhc3nSlv8kg9qv1"
    "m6XHVQY3PnEw+QQtqSIXklHwIDAQAB"
)
RETIRED_FINGERPRINT = 0xC3B42B026CE86B21

# What a live production datacenter actually asks for. Observed on 2026-08-20
# against dc 2, which offered exactly these three and nothing else:
#
#   0xd09d1d85de64fd85, 0x0bc35f3509f7b7a5, 0xc3b42b026ce86b21
#
# The last of those is RETIRED_FINGERPRINT above, which is what makes the list
# self-evidently a production one rather than a test datacenter's.
#
# This number is here because every other test in this file passes whichever
# way round the two vendored keys are labelled, and they WERE the wrong way
# round: the handshake asked for the test key on every production connection
# and no server has ever agreed to one. Nothing offline could see it. The
# scripted server in the suite generates its own keypair and offers its own
# fingerprint, so which of ours is called production never came up.
LIVE_PRODUCTION_FINGERPRINT = 0xD09D1D85DE64FD85


class TestVendoredKeys:
    @pytest.mark.parametrize("key", [*PRODUCTION_KEYS, *TEST_KEYS])
    def test_shape(self, key):
        assert key.modulus.bit_length() == 2048
        assert key.size == 256
        assert key.exponent == 65537

    def test_the_two_keys_are_different(self):
        assert PRODUCTION_KEYS[0].modulus != TEST_KEYS[0].modulus
        assert PRODUCTION_KEYS[0].fingerprint != TEST_KEYS[0].fingerprint

    def test_fingerprints_fit_in_a_tl_long(self):
        for key in (*PRODUCTION_KEYS, *TEST_KEYS):
            assert -(2**63) <= key.fingerprint < 2**63

    def test_fingerprint_follows_the_key(self):
        rebuilt = PublicKey.from_base64(
            _base64_of(PRODUCTION_KEYS[0].modulus, PRODUCTION_KEYS[0].exponent)
        )
        assert rebuilt.fingerprint == PRODUCTION_KEYS[0].fingerprint

    def test_reproduces_the_published_fingerprint(self):
        retired = PublicKey.from_base64(RETIRED_KEY)
        assert retired.modulus.bit_length() == 2048
        assert retired.fingerprint & 0xFFFFFFFFFFFFFFFF == RETIRED_FINGERPRINT

    def test_the_production_key_is_the_one_production_asks_for(self):
        # The label is load-bearing and nothing else here checks it. Getting it
        # wrong costs every connection to real Telegram and no test at all.
        found = PRODUCTION_KEYS[0].fingerprint & 0xFFFFFFFFFFFFFFFF
        assert found == LIVE_PRODUCTION_FINGERPRINT

    def test_the_test_key_is_not_the_production_one(self):
        # Stated separately from test_the_two_keys_are_different, which passes
        # just as happily when the two are swapped.
        found = TEST_KEYS[0].fingerprint & 0xFFFFFFFFFFFFFFFF
        assert found != LIVE_PRODUCTION_FINGERPRINT


class TestSelection:
    def test_picks_the_key_a_server_asked_for(self):
        wanted = PRODUCTION_KEYS[0].fingerprint
        assert select_key([123, wanted]) is PRODUCTION_KEYS[0]

    def test_picks_a_test_key_only_when_asked(self):
        wanted = TEST_KEYS[0].fingerprint
        assert select_key([wanted], test=True) is TEST_KEYS[0]
        with pytest.raises(SecurityError):
            select_key([wanted])

    def test_refuses_when_nothing_matches(self):
        with pytest.raises(SecurityError, match="no key we know"):
            select_key([1, 2, 3])

    def test_refuses_an_empty_offer(self):
        with pytest.raises(SecurityError):
            select_key([])


class TestEncryption:
    def test_matches_the_textbook_example(self):
        encrypted = TEXTBOOK.encrypt((65).to_bytes(2, "big"))
        assert int.from_bytes(encrypted, "big") == 2790

    def test_survives_a_round_trip_through_the_private_key(self):
        for message in (1, 42, 65, 3232):
            encrypted = TEXTBOOK.encrypt(message.to_bytes(2, "big"))
            recovered = pow(
                int.from_bytes(encrypted, "big"), TEXTBOOK_PRIVATE, TEXTBOOK.modulus
            )
            assert recovered == message

    def test_output_is_always_a_whole_block(self):
        key = PRODUCTION_KEYS[0]
        assert len(key.encrypt(b"\x01")) == 256
        assert len(key.encrypt(b"\x00" * 200)) == 256

    def test_refuses_a_block_that_does_not_fit(self):
        with pytest.raises(ValueError, match="will not fit"):
            PRODUCTION_KEYS[0].encrypt(bytes(257))
        with pytest.raises(ValueError, match="not smaller than the modulus"):
            PRODUCTION_KEYS[0].encrypt(b"\xff" * 256)


class TestDer:
    def test_rejects_something_that_is_not_a_sequence(self):
        with pytest.raises(ValueError, match="not a DER sequence"):
            _parse_pkcs1(b"\x02\x01\x01")
        with pytest.raises(ValueError, match="not a DER sequence"):
            _parse_pkcs1(b"")

    def test_rejects_a_sequence_of_the_wrong_thing(self):
        with pytest.raises(ValueError, match="DER integer"):
            _parse_pkcs1(b"\x30\x03\x04\x01\x00")

    def test_the_hashed_form_carries_no_sign_padding(self):
        # A TL string of bytes, not a DER integer: no leading zero even when
        # the top bit is set.
        assert _big_endian(0xFF) == b"\xff"
        assert _big_endian(0x7F) == b"\x7f"
        assert _big_endian(65537) == b"\x01\x00\x01"
        assert _big_endian(0) == b"\x00"
        assert len(_big_endian(PRODUCTION_KEYS[0].modulus)) == 256


def _base64_of(modulus: int, exponent: int) -> str:
    """Re-encode a key as PKCS#1 base64, to prove the reader and the shape agree."""
    import base64

    def integer(value: int) -> bytes:
        # A DER integer does need the sign padding the fingerprint form omits.
        payload = _big_endian(value)
        if payload[0] & 0x80:
            payload = b"\x00" + payload
        return b"\x02" + _length(len(payload)) + payload

    def _length(size: int) -> bytes:
        if size < 0x80:
            return bytes([size])
        raw = size.to_bytes((size.bit_length() + 7) // 8, "big")
        return bytes([0x80 | len(raw)]) + raw

    body = integer(modulus) + integer(exponent)
    return base64.b64encode(b"\x30" + _length(len(body)) + body).decode()
