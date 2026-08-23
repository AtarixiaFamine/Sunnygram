# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Where a session is kept between runs."""

from __future__ import annotations

import os

from .base import (
    PeerKind,
    PeerRecord,
    PeerStore,
    SessionState,
    Storage,
    UpdateState,
)
from .memory import MemoryStorage
from .sqlite import SQLiteStorage
from .string import StringStorage, decode_session, encode_session

__all__ = [
    "MemoryStorage",
    "PeerKind",
    "PeerRecord",
    "PeerStore",
    "SQLiteStorage",
    "SessionState",
    "Storage",
    "StringStorage",
    "UpdateState",
    "decode_session",
    "encode_session",
    "storage_for",
]


def storage_for(session: str | os.PathLike[str] | Storage) -> Storage:
    """What to keep a session in, from however it was named.

    Lives here instead of on the client because two places name a session and
    they have to agree: `Client("account")` opens `account.session`, so
    `adopt_session` writing to a path spelled the same way has to reach the
    same file. Splitting this in two would mean a migration that wrote
    somewhere the client never looks, and the symptom of that is being asked to
    log in again, which is indistinguishable from the importer not working.
    """
    if isinstance(session, Storage):
        return session
    name = str(session)
    if name in (":memory:", ""):
        return MemoryStorage()
    return SQLiteStorage(name if name.endswith(".session") else f"{name}.session")
