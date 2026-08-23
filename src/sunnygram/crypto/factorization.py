# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Splitting the semiprime the server sends during the handshake.

Telegram answers the first handshake message with pq, a product of two primes,
and expects both factors back. It is a small proof of work, sized so a real
client barely notices and a flood of fake ones does not.

Brent's improvement on Pollard's rho does it in well under a millisecond at the
sizes Telegram uses, which is around 63 bits.
"""

from __future__ import annotations

import secrets
from math import gcd

__all__ = ["factorize"]


def factorize(pq: int, *, attempts: int = 64) -> tuple[int, int]:
    """Split pq into its two factors, smaller one first.

    The number comes from the server, so a value that is not a semiprime would
    otherwise spin forever. After enough fruitless restarts this gives up
    instead.
    """
    if pq < 4:
        raise ValueError(f"{pq} is too small to be a product of two primes")
    if pq % 2 == 0:
        return 2, pq // 2

    for _ in range(attempts):
        factor = _rho(pq)
        if factor is not None:
            other = pq // factor
            return (factor, other) if factor < other else (other, factor)
    raise ValueError(f"could not factor {pq}, which may not be a semiprime")


def _rho(pq: int) -> int | None:
    """One run of Brent's cycle finding, or None if this seed led nowhere.

    The seeds only steer the search, but rule S1 says randomness comes from
    secrets everywhere, with no exceptions to argue about later.
    """
    y = 1 + secrets.randbelow(pq - 1)
    c = 1 + secrets.randbelow(pq - 1)
    m = 1 + secrets.randbelow(pq - 1)
    divisor = 1
    product = 1
    steps = 1
    x = trail = y

    while divisor == 1:
        x = y
        for _ in range(steps):
            y = (y * y + c) % pq
        done = 0
        while done < steps and divisor == 1:
            trail = y
            for _ in range(min(m, steps - done)):
                y = (y * y + c) % pq
                product = product * abs(x - y) % pq
            divisor = gcd(product, pq)
            done += m
        steps *= 2

    if divisor == pq:
        # The batched gcd swallowed the factor, so walk back over the last
        # stretch one step at a time to find where it appeared.
        divisor = 1
        while divisor == 1:
            trail = (trail * trail + c) % pq
            divisor = gcd(abs(x - trail), pq)

    return None if divisor == pq else divisor
