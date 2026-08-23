"""The authorization key handshake.

The padding scheme is checked by undoing it exactly the way a server would,
step for step, which is the only way to be sure of it without a server. The
parameter checks are exercised against the prime from Telegram's own worked
example, so a mistranscription would show up as a failed primality test rather
than a quietly passing one.
"""

from __future__ import annotations

import hashlib

import pytest

from sunnygram.crypto import (
    DH_PRIME_BITS,
    MAX_INNER_DATA,
    PRODUCTION_KEYS,
    check_dh_parameters,
    derive_auth_key,
    generate_b,
    ige256_decrypt,
    new_nonce_hash,
    pad_block,
    rsa_pad,
    server_salt,
    temp_key_iv,
    unwrap_answer,
    wrap_client_data,
)
from sunnygram.errors import SecurityError

# From the sample handshake in the docs, with the TL string header (fe000100)
# stripped off the front. A safe 2048-bit prime, used with g = 3.
DOCUMENTED_PRIME = int(
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
DOCUMENTED_G = 3

SERVER_NONCE = 0x63248F6748214EAB8A2F4CC876E11974
NEW_NONCE = 0x3B4C5D6E7F8091A2B3C4D5E6F708192A3B4C5D6E7F8091A2B3C4D5E6F708192A


class TestRsaPad:
    def test_a_server_can_undo_it(self):
        inner = b"pretend this is a serialized p_q_inner_data" + bytes(30)
        block = pad_block(inner)
        assert len(block) == 256

        # Everything below is the server's side of the scheme, in order.
        hidden_key, encrypted = block[:32], block[32:]
        assert len(encrypted) == 224
        aes_key = bytes(
            a ^ b for a, b in zip(hidden_key, hashlib.sha256(encrypted).digest())
        )
        with_hash = ige256_decrypt(encrypted, aes_key, bytes(32))
        padded = with_hash[:192][::-1]

        assert with_hash[192:] == hashlib.sha256(aes_key + padded).digest()
        assert padded[: len(inner)] == inner
        assert len(padded) == 192

    def test_every_block_is_different(self):
        inner = b"same data every time"
        assert pad_block(inner) != pad_block(inner)

    def test_refuses_data_that_will_not_fit(self):
        assert pad_block(bytes(MAX_INNER_DATA))
        with pytest.raises(ValueError, match="over the 144"):
            pad_block(bytes(MAX_INNER_DATA + 1))

    def test_encrypting_produces_a_whole_block(self):
        encrypted = rsa_pad(b"inner data", PRODUCTION_KEYS[0])
        assert len(encrypted) == 256

    def test_gives_up_rather_than_looping_forever(self):
        # A tiny modulus that nothing will ever fit under.
        impossible = PRODUCTION_KEYS[0].__class__(modulus=3, exponent=1, fingerprint=0)
        with pytest.raises(SecurityError, match="below the modulus"):
            rsa_pad(b"inner data", impossible, attempts=3)


class TestTempKey:
    def test_sizes(self):
        key, iv = temp_key_iv(SERVER_NONCE, NEW_NONCE)
        assert len(key) == 32
        assert len(iv) == 32

    def test_is_deterministic_but_follows_both_nonces(self):
        base = temp_key_iv(SERVER_NONCE, NEW_NONCE)
        assert base == temp_key_iv(SERVER_NONCE, NEW_NONCE)
        assert base != temp_key_iv(SERVER_NONCE + 1, NEW_NONCE)
        assert base != temp_key_iv(SERVER_NONCE, NEW_NONCE + 1)

    def test_the_iv_ends_with_the_start_of_the_new_nonce(self):
        # A structural property of the documented layout, independent of how
        # the hashes are put together.
        _, iv = temp_key_iv(SERVER_NONCE, NEW_NONCE)
        assert iv[-4:] == NEW_NONCE.to_bytes(32, "little")[:4]

    def test_signed_and_unsigned_nonces_mean_the_same_thing(self):
        # The codec reads int128 signed; anything generating a nonce produces
        # unsigned bits. Both spell the same wire bytes.
        unsigned = 0xF0248F6748214EAB8A2F4CC876E11974
        signed = unsigned - (1 << 128)
        assert temp_key_iv(unsigned, NEW_NONCE) == temp_key_iv(signed, NEW_NONCE)

    def test_refuses_a_nonce_that_does_not_fit(self):
        with pytest.raises(ValueError, match="int128 nonce"):
            temp_key_iv(1 << 128, NEW_NONCE)


class TestParameterChecks:
    def test_accepts_the_documented_parameters(self):
        assert DOCUMENTED_PRIME.bit_length() == DH_PRIME_BITS
        g_a = pow(DOCUMENTED_G, 12345, DOCUMENTED_PRIME)
        check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME, g_a)

    def test_refuses_a_prime_of_the_wrong_size(self):
        with pytest.raises(SecurityError, match="bits"):
            check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME >> 1)

    def test_refuses_a_generator_outside_the_allowed_set(self):
        for g in (0, 1, 8, 11):
            with pytest.raises(SecurityError, match="not one of 2 to 7"):
                check_dh_parameters(g, DOCUMENTED_PRIME)

    def test_refuses_a_generator_the_prime_does_not_suit(self):
        # The documented prime goes with g = 3, so g = 2 wants p mod 8 == 7.
        assert DOCUMENTED_PRIME % 8 != 7
        with pytest.raises(SecurityError, match="condition for g=2"):
            check_dh_parameters(2, DOCUMENTED_PRIME)

    def test_refuses_a_prime_that_is_not_safe(self):
        # Same size and still passes the g = 3 remainder test, but composite.
        fake = DOCUMENTED_PRIME - 6
        assert fake.bit_length() == DH_PRIME_BITS
        assert fake % 3 == 2
        with pytest.raises(SecurityError, match="not a safe prime"):
            check_dh_parameters(DOCUMENTED_G, fake)

    @pytest.mark.parametrize(
        "power",
        [
            1,
            2,
            (1 << (DH_PRIME_BITS - 64)) - 1,
            DOCUMENTED_PRIME - 1,
            DOCUMENTED_PRIME - 2,
        ],
    )
    def test_refuses_a_public_value_near_the_edges(self, power):
        with pytest.raises(SecurityError):
            check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME, power)

    def test_checks_every_public_value_it_is_given(self):
        good = pow(DOCUMENTED_G, 999, DOCUMENTED_PRIME)
        with pytest.raises(SecurityError):
            check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME, good, 1)

    def test_remembers_a_prime_it_already_verified(self):
        # The second call must not repeat the primality test, which is the
        # slowest thing in the library.
        import time

        check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME)
        start = time.perf_counter()
        check_dh_parameters(DOCUMENTED_G, DOCUMENTED_PRIME)
        assert time.perf_counter() - start < 0.05


class TestAnswerEnvelope:
    def test_our_half_comes_back_out_of_its_envelope(self):
        for length in (0, 1, 15, 16, 17, 100):
            data = bytes(range(256))[:length]
            wrapped = wrap_client_data(data)
            assert len(wrapped) % 16 == 0
            assert unwrap_answer(wrapped) == data

    def test_padding_never_reaches_a_whole_block(self):
        for length in range(40):
            wrapped = wrap_client_data(bytes(length))
            assert 0 <= len(wrapped) - 20 - length < 16

    def test_refuses_an_answer_that_was_tampered_with(self):
        wrapped = bytearray(wrap_client_data(b"server_DH_inner_data goes here"))
        wrapped[30] ^= 0xFF
        with pytest.raises(SecurityError, match="does not match its own hash"):
            unwrap_answer(bytes(wrapped))

    def test_refuses_an_answer_with_a_rewritten_hash(self):
        wrapped = bytearray(wrap_client_data(b"server_DH_inner_data goes here"))
        wrapped[0] ^= 0xFF
        with pytest.raises(SecurityError):
            unwrap_answer(bytes(wrapped))

    def test_refuses_something_that_is_not_whole_blocks(self):
        with pytest.raises(SecurityError, match="whole number of blocks"):
            unwrap_answer(bytes(30))
        with pytest.raises(SecurityError):
            unwrap_answer(b"")


class TestSharedSecret:
    def test_both_sides_reach_the_same_key(self):
        a = generate_b()
        b = generate_b()
        g_a = pow(DOCUMENTED_G, a, DOCUMENTED_PRIME)
        g_b = pow(DOCUMENTED_G, b, DOCUMENTED_PRIME)
        ours = derive_auth_key(g_a, b, DOCUMENTED_PRIME)
        theirs = derive_auth_key(g_b, a, DOCUMENTED_PRIME)
        assert ours == theirs
        assert len(ours) == 256

    def test_secret_exponents_are_full_size_and_fresh(self):
        exponents = {generate_b() for _ in range(8)}
        assert len(exponents) == 8
        assert all(value.bit_length() > DH_PRIME_BITS - 32 for value in exponents)

    def test_a_short_key_is_still_padded_to_256_bytes(self):
        assert len(derive_auth_key(1, 5, DOCUMENTED_PRIME)) == 256


class TestNonceHash:
    def test_the_three_answers_hash_differently(self):
        auth_key = bytes(range(256))
        hashes = {new_nonce_hash(NEW_NONCE, auth_key, n) for n in (1, 2, 3)}
        assert len(hashes) == 3

    def test_follows_the_key(self):
        assert new_nonce_hash(NEW_NONCE, bytes(256), 1) != new_nonce_hash(
            NEW_NONCE, bytes(range(256)), 1
        )

    def test_fits_an_int128(self):
        value = new_nonce_hash(NEW_NONCE, bytes(256), 1)
        assert -(2**127) <= value < 2**127

    def test_refuses_a_number_that_is_not_an_answer(self):
        with pytest.raises(ValueError, match="1, 2 or 3"):
            new_nonce_hash(NEW_NONCE, bytes(256), 4)


class TestServerSalt:
    def test_is_the_two_nonces_folded_together(self):
        salt = server_salt(NEW_NONCE, SERVER_NONCE)
        assert -(2**63) <= salt < 2**63

    def test_follows_both_nonces(self):
        base = server_salt(NEW_NONCE, SERVER_NONCE)
        assert base != server_salt(NEW_NONCE + 1, SERVER_NONCE)
        assert base != server_salt(NEW_NONCE, SERVER_NONCE + 1)
