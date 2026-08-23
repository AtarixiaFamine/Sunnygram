"""Splitting the handshake's semiprime."""

from __future__ import annotations

import pytest

from sunnygram.crypto import factorize

PRIMES = [65537, 1000003, 999999937, 1000000007, 1000000009, 2147483647]


class TestFactorize:
    @pytest.mark.parametrize("left", PRIMES)
    @pytest.mark.parametrize("right", PRIMES)
    def test_recovers_both_factors(self, left, right):
        if left == right:
            return
        smaller, larger = sorted((left, right))
        assert factorize(left * right) == (smaller, larger)

    def test_the_worked_example_from_the_docs(self):
        # The pq, p and q printed in Telegram's own sample handshake.
        assert factorize(3358800871349344843) == (1786331737, 1880278339)

    def test_a_telegram_sized_semiprime(self):
        # Around 61 bits, which is the neighbourhood the server picks from.
        pq = 2147483647 * 1000000007
        assert pq.bit_length() >= 60
        p, q = factorize(pq)
        assert p * q == pq
        assert p < q

    def test_smaller_factor_comes_first(self):
        for _ in range(20):
            p, q = factorize(1000003 * 2147483647)
            assert p < q

    def test_even_numbers_take_the_short_path(self):
        assert factorize(2 * 999999937) == (2, 999999937)

    def test_too_small_to_split(self):
        for value in (0, 1, 2, 3):
            with pytest.raises(ValueError, match="too small"):
                factorize(value)

    def test_gives_up_on_a_prime(self):
        # The server is not supposed to send one, so this is about refusing to
        # spin forever rather than about the answer.
        with pytest.raises(ValueError, match="may not be a semiprime"):
            factorize(1000000007, attempts=2)
