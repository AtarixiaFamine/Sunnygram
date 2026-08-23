# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Where the datacenters are.

These are the addresses to fall back on, not the truth. A client connects to one
of them, asks help.getConfig, and from then on uses the list the server gave
back, which is the only one that knows about new datacenters and media-only
addresses. The built-in list only has to be good enough to ask the question.

Taken from Telegram Desktop's built-in list instead of from memory, because a
wrong address here looks exactly like a network outage.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Address",
    "PRODUCTION",
    "PRODUCTION_IPV6",
    "TEST",
    "TEST_IPV6",
    "address_for",
]


@dataclass(frozen=True, slots=True)
class Address:
    """One place to reach one datacenter."""

    dc_id: int
    host: str
    port: int = 443


PRODUCTION: tuple[Address, ...] = (
    Address(1, "149.154.175.50"),
    Address(2, "149.154.167.51"),
    Address(2, "95.161.76.100"),
    Address(3, "149.154.175.100"),
    Address(4, "149.154.167.91"),
    Address(5, "149.154.171.5"),
)

PRODUCTION_IPV6: tuple[Address, ...] = (
    Address(1, "2001:0b28:f23d:f001:0000:0000:0000:000a"),
    Address(2, "2001:067c:04e8:f002:0000:0000:0000:000a"),
    Address(3, "2001:0b28:f23d:f003:0000:0000:0000:000a"),
    Address(4, "2001:067c:04e8:f004:0000:0000:0000:000a"),
    Address(5, "2001:0b28:f23f:f005:0000:0000:0000:000a"),
)

TEST: tuple[Address, ...] = (
    Address(1, "149.154.175.10"),
    Address(2, "149.154.167.40"),
    Address(3, "149.154.175.117"),
)

TEST_IPV6: tuple[Address, ...] = (
    Address(1, "2001:0b28:f23d:f001:0000:0000:0000:000e"),
    Address(2, "2001:067c:04e8:f002:0000:0000:0000:000e"),
    Address(3, "2001:0b28:f23d:f003:0000:0000:0000:000e"),
)


def address_for(dc_id: int, *, test: bool = False, ipv6: bool = False) -> Address:
    """The built-in address for a datacenter."""
    if test:
        table = TEST_IPV6 if ipv6 else TEST
    else:
        table = PRODUCTION_IPV6 if ipv6 else PRODUCTION
    for address in table:
        if address.dc_id == dc_id:
            return address
    known = sorted({candidate.dc_id for candidate in table})
    raise LookupError(f"no built-in address for DC {dc_id}; there are {known}")
