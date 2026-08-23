# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A session kept in a file, which is what most programs want.

One small sqlite database: a row for the session, a row per datacenter key, and
the peer cache, which is the part with real lookups and the reason this is a
database instead of a flat file. The other reason is that a half-written
session file is a login lost.

Two things this does that a plain file would not. The database is opened with
secure_delete, so a key removed by a logout is overwritten instead of left in a
free page, and the file is created readable only by its owner, because anyone
who can read it is the account. The second is a best effort: on Windows the
permission bits do not mean the same thing, and nothing here pretends otherwise.

Every call goes through a worker thread. sqlite blocks, and the event loop has a
connection to read (rule P1).
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path

from .base import PeerKind, PeerRecord, PeerStore, SessionState, Storage

__all__ = ["SQLiteStorage"]

SCHEMA_VERSION = 3

# The update state lives in tables of its own rather than as columns on session.
# A file written by an older build then gains them by being opened, with no
# migration to write and nothing to get wrong.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS session (
    id        INTEGER PRIMARY KEY CHECK (id = 1),
    dc_id     INTEGER NOT NULL,
    test_mode INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    is_bot    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_keys (
    dc_id INTEGER PRIMARY KEY,
    key   BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS update_state (
    id   INTEGER PRIMARY KEY CHECK (id = 1),
    pts  INTEGER NOT NULL,
    qts  INTEGER NOT NULL,
    date INTEGER NOT NULL,
    seq  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS channel_pts (
    channel_id INTEGER PRIMARY KEY,
    pts        INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS peers (
    id          INTEGER PRIMARY KEY,
    kind        TEXT NOT NULL,
    access_hash INTEGER NOT NULL,
    phone       TEXT
);
CREATE TABLE IF NOT EXISTS peer_usernames (
    username TEXT PRIMARY KEY,
    peer_id  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS peers_by_phone ON peers (phone) WHERE phone IS NOT NULL;
CREATE INDEX IF NOT EXISTS usernames_by_peer ON peer_usernames (peer_id);
"""


class SQLiteStorage(Storage, PeerStore):
    """A session kept in a file on disk."""

    __slots__ = ("_path", "_db", "_lock")

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path)
        self._db: sqlite3.Connection | None = None
        # One connection, one caller at a time. The worker thread changes from
        # call to call, which sqlite only tolerates if the calls do not overlap.
        self._lock = asyncio.Lock()

    def __repr__(self) -> str:
        return f"SQLiteStorage({str(self._path)!r})"

    @property
    def path(self) -> Path:
        """Where the session file is."""
        return self._path

    async def open(self) -> None:
        if self._db is not None:
            return
        async with self._lock:
            if self._db is None:
                self._db = await asyncio.to_thread(self._connect)

    def _connect(self) -> sqlite3.Connection:
        fresh = not self._path.exists()
        # The worker thread is not always the same one, so the connection has to
        # be allowed to move between them. The lock is what keeps that safe.
        db = sqlite3.connect(self._path, check_same_thread=False)
        if fresh:
            _restrict(self._path)
        db.execute("PRAGMA secure_delete = ON")
        db.executescript(_SCHEMA)
        db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        db.commit()
        return db

    async def close(self) -> None:
        async with self._lock:
            db, self._db = self._db, None
            if db is not None:
                await asyncio.to_thread(db.close)

    async def load(self) -> SessionState:
        async with self._held() as db:
            return await asyncio.to_thread(_load, db)

    async def save(self, state: SessionState) -> None:
        async with self._held() as db:
            await asyncio.to_thread(_save, db, state)

    async def delete(self) -> None:
        async with self._held() as db:
            await asyncio.to_thread(_delete, db)

    async def put_peers(self, peers: Sequence[PeerRecord]) -> None:
        if not peers:
            return
        async with self._held() as db:
            await asyncio.to_thread(_put_peers, db, peers)

    async def peer_by_id(self, peer_id: int) -> PeerRecord | None:
        async with self._held() as db:
            return await asyncio.to_thread(_peer_by_id, db, peer_id)

    async def peer_by_username(self, username: str) -> PeerRecord | None:
        async with self._held() as db:
            return await asyncio.to_thread(_peer_by_username, db, username)

    async def peer_by_phone(self, phone: str) -> PeerRecord | None:
        async with self._held() as db:
            return await asyncio.to_thread(_peer_by_phone, db, phone)

    async def peer_count(self) -> int:
        async with self._held() as db:
            return await asyncio.to_thread(_peer_count, db)

    async def drop_peer(self, peer_id: int) -> bool:
        async with self._held() as db:
            return await asyncio.to_thread(_drop_peer, db, peer_id)

    async def clear_peers(self) -> None:
        async with self._held() as db:
            await asyncio.to_thread(_clear_peers, db)

    @asynccontextmanager
    async def _held(self) -> AsyncIterator[sqlite3.Connection]:
        """The connection, opened if it was not, and ours for the duration."""
        await self.open()
        async with self._lock:
            db = self._db
            if db is None:
                raise RuntimeError("this storage was closed while it was in use")
            yield db


def _restrict(path: Path) -> None:
    """Make a new session file readable only by its owner, where that means
    something."""
    try:
        path.touch(mode=0o600, exist_ok=True)
        os.chmod(path, 0o600)
    except OSError:
        # A filesystem that does not carry permissions. Nothing to do, and not
        # a reason to refuse to run.
        pass


def _load(db: sqlite3.Connection) -> SessionState:
    row = db.execute(
        "SELECT dc_id, test_mode, user_id, is_bot FROM session WHERE id = 1"
    ).fetchone()
    state = SessionState()
    if row is not None:
        state.dc_id = row[0]
        state.test_mode = bool(row[1])
        state.user_id = row[2]
        state.is_bot = bool(row[3])
    for dc_id, key in db.execute("SELECT dc_id, key FROM auth_keys"):
        state.set_auth_key(dc_id, key)

    row = db.execute(
        "SELECT pts, qts, date, seq FROM update_state WHERE id = 1"
    ).fetchone()
    if row is not None:
        state.updates.pts, state.updates.qts = row[0], row[1]
        state.updates.date, state.updates.seq = row[2], row[3]
    state.updates.channels = dict(db.execute("SELECT channel_id, pts FROM channel_pts"))
    return state


def _save(db: sqlite3.Connection, state: SessionState) -> None:
    db.execute(
        "INSERT INTO session (id, dc_id, test_mode, user_id, is_bot)"
        " VALUES (1, ?, ?, ?, ?)"
        " ON CONFLICT (id) DO UPDATE SET"
        " dc_id = excluded.dc_id, test_mode = excluded.test_mode,"
        " user_id = excluded.user_id, is_bot = excluded.is_bot",
        (state.dc_id, int(state.test_mode), state.user_id, int(state.is_bot)),
    )
    # Replaced wholesale instead of merged: a key the caller dropped is a key
    # that has to leave the file too.
    db.execute("DELETE FROM auth_keys")
    db.executemany(
        "INSERT INTO auth_keys (dc_id, key) VALUES (?, ?)",
        sorted(state.auth_keys.items()),
    )

    updates = state.updates
    db.execute(
        "INSERT INTO update_state (id, pts, qts, date, seq) VALUES (1, ?, ?, ?, ?)"
        " ON CONFLICT (id) DO UPDATE SET"
        " pts = excluded.pts, qts = excluded.qts,"
        " date = excluded.date, seq = excluded.seq",
        (updates.pts, updates.qts, updates.date, updates.seq),
    )
    # Channels come and go, so this is replaced instead of merged, the same way
    # the keys are.
    db.execute("DELETE FROM channel_pts")
    db.executemany(
        "INSERT INTO channel_pts (channel_id, pts) VALUES (?, ?)",
        sorted(updates.channels.items()),
    )
    db.commit()


def _put_peers(db: sqlite3.Connection, peers: Sequence[PeerRecord]) -> None:
    db.executemany(
        "INSERT INTO peers (id, kind, access_hash, phone) VALUES (?, ?, ?, ?)"
        " ON CONFLICT (id) DO UPDATE SET"
        " kind = excluded.kind, access_hash = excluded.access_hash,"
        " phone = excluded.phone",
        [(p.id, str(p.kind), p.access_hash, p.phone) for p in peers],
    )
    # Usernames are replaced per peer, not merged. A name given up is a
    # name someone else can take, and a stale row would send messages to the
    # wrong account, which is the worst thing this cache could do.
    db.executemany(
        "DELETE FROM peer_usernames WHERE peer_id = ?", [(p.id,) for p in peers]
    )
    db.executemany(
        "INSERT INTO peer_usernames (username, peer_id) VALUES (?, ?)"
        " ON CONFLICT (username) DO UPDATE SET peer_id = excluded.peer_id",
        [(name, p.id) for p in peers for name in p.usernames],
    )
    db.commit()


def _row_to_peer(row: tuple[int, str, int, str | None], names: list[str]) -> PeerRecord:
    return PeerRecord(
        id=row[0],
        kind=PeerKind(row[1]),
        access_hash=row[2],
        usernames=tuple(names),
        phone=row[3],
    )


def _peer_with_names(
    db: sqlite3.Connection, row: tuple[int, str, int, str | None] | None
) -> PeerRecord | None:
    if row is None:
        return None
    names = [
        name
        for (name,) in db.execute(
            "SELECT username FROM peer_usernames WHERE peer_id = ?", (row[0],)
        )
    ]
    return _row_to_peer(row, names)


def _peer_by_id(db: sqlite3.Connection, peer_id: int) -> PeerRecord | None:
    row = db.execute(
        "SELECT id, kind, access_hash, phone FROM peers WHERE id = ?", (peer_id,)
    ).fetchone()
    return _peer_with_names(db, row)


def _peer_by_username(db: sqlite3.Connection, username: str) -> PeerRecord | None:
    row = db.execute(
        "SELECT p.id, p.kind, p.access_hash, p.phone FROM peers p"
        " JOIN peer_usernames u ON u.peer_id = p.id WHERE u.username = ?",
        (username,),
    ).fetchone()
    return _peer_with_names(db, row)


def _peer_by_phone(db: sqlite3.Connection, phone: str) -> PeerRecord | None:
    row = db.execute(
        "SELECT id, kind, access_hash, phone FROM peers WHERE phone = ?", (phone,)
    ).fetchone()
    return _peer_with_names(db, row)


def _peer_count(db: sqlite3.Connection) -> int:
    count: int = db.execute("SELECT COUNT(*) FROM peers").fetchone()[0]
    return count


def _drop_peer(db: sqlite3.Connection, peer_id: int) -> bool:
    # The usernames go with it. Leaving them would keep a name pointing at a
    # peer that is no longer here, which is the same wrong answer the drop was
    # meant to remove.
    removed = db.execute("DELETE FROM peers WHERE id = ?", (peer_id,)).rowcount
    db.execute("DELETE FROM peer_usernames WHERE peer_id = ?", (peer_id,))
    db.commit()
    return bool(removed)


def _clear_peers(db: sqlite3.Connection) -> None:
    db.execute("DELETE FROM peers")
    db.execute("DELETE FROM peer_usernames")
    db.commit()


def _delete(db: sqlite3.Connection) -> None:
    db.execute("DELETE FROM session")
    db.execute("DELETE FROM auth_keys")
    db.execute("DELETE FROM update_state")
    db.execute("DELETE FROM channel_pts")
    db.execute("DELETE FROM peers")
    db.execute("DELETE FROM peer_usernames")
    db.commit()
    # secure_delete only zeroes pages as they are freed, so this is what gets
    # the key out of the file instead of merely unreferenced.
    db.execute("VACUUM")
