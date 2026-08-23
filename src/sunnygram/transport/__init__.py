# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The TCP connection, the framings it can speak, and how it gets out."""

from __future__ import annotations

from .codec import (
    MAX_PACKET_SIZE,
    Abridged,
    Codec,
    Full,
    Intermediate,
    PaddedIntermediate,
    Reader,
)
from .obfuscation import Obfuscation
from .proxy import Proxy
from .tcp import TCPTransport

__all__ = [
    "MAX_PACKET_SIZE",
    "Abridged",
    "Codec",
    "Full",
    "Intermediate",
    "Obfuscation",
    "PaddedIntermediate",
    "Proxy",
    "Reader",
    "TCPTransport",
]
