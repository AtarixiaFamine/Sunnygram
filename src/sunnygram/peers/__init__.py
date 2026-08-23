# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Knowing who is who: the access hashes, and how to look one up.

The cache holds what the session has learned, the resolver turns whatever a
caller wrote into something the server understands. Together they are what
makes send_message(invoker, "@durov", ...) possible at all, since the protocol
itself has no idea what a username is once the call is being built.
"""

from __future__ import annotations

from .cache import (
    PeerCache,
    input_peer_for,
    normalize_phone,
    normalize_username,
    record_for,
)
from .resolver import (
    Target,
    as_channel,
    as_user,
    mark_id,
    mark_peer,
    resolve,
    resolve_phone,
    resolve_username,
    unmark_id,
)

__all__ = [
    "PeerCache",
    "Target",
    "as_channel",
    "as_user",
    "input_peer_for",
    "mark_id",
    "mark_peer",
    "normalize_phone",
    "normalize_username",
    "record_for",
    "resolve",
    "resolve_phone",
    "resolve_username",
    "unmark_id",
]
