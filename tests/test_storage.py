"""The three places a session can be kept.

They are meant to be interchangeable, so most of what follows runs against all
three from one set of tests. What is specific to a backend is what is worth
saying about it separately: that a file is created private, that a string
refuses to be read by a version that would misunderstand it.
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode

import pytest

from sunnygram.storage import (
    MemoryStorage,
    SQLiteStorage,
    SessionState,
    StringStorage,
    UpdateState,
    decode_session,
    encode_session,
)
from sunnygram.storage.sqlite import SCHEMA_VERSION
from sunnygram.storage.string import VERSION

KEY = bytes(range(256))
OTHER_KEY = bytes(range(255, -1, -1))


def a_session() -> SessionState:
    state = SessionState(dc_id=4, test_mode=False, user_id=777000, is_bot=False)
    state.set_auth_key(4, KEY)
    return state


@pytest.fixture(params=["memory", "sqlite", "string"])
async def storage(request, tmp_path):
    """One of each backend, so the shared behaviour is tested three times.

    Closed on the way out. The sqlite one holds a real file handle, and one
    left open is reported whenever the garbage collector gets round to it,
    which is somewhere else entirely and looks like that test's fault.
    """
    if request.param == "memory":
        made = MemoryStorage()
    elif request.param == "sqlite":
        made = SQLiteStorage(tmp_path / "session.db")
    else:
        made = StringStorage()
    try:
        yield made
    finally:
        await made.close()


class TestEveryBackend:
    async def test_an_empty_one_reads_back_a_fresh_session(self, storage):
        state = await storage.load()
        assert state == SessionState()
        assert not state.authorized
        assert state.auth_key() is None

    async def test_what_goes_in_comes_out(self, storage):
        await storage.save(a_session())
        state = await storage.load()
        assert state.dc_id == 4
        assert state.user_id == 777000
        assert state.is_bot is False
        assert state.auth_key() == KEY
        assert state.authorized

    async def test_saving_again_replaces(self, storage):
        await storage.save(a_session())
        second = SessionState(dc_id=1, test_mode=True, user_id=42, is_bot=True)
        second.set_auth_key(1, OTHER_KEY)
        await storage.save(second)
        state = await storage.load()
        assert (state.dc_id, state.user_id, state.is_bot) == (1, 42, True)
        assert state.test_mode is True
        assert state.auth_key() == OTHER_KEY

    async def test_deleting_leaves_nothing(self, storage):
        await storage.save(a_session())
        await storage.delete()
        assert await storage.load() == SessionState()

    async def test_a_loaded_session_is_not_the_stored_one(self, storage):
        # Changing what load handed back must not change what is stored, or the
        # backends would disagree with each other about when a save happened.
        await storage.save(a_session())
        state = await storage.load()
        state.user_id = 99
        state.set_auth_key(4, OTHER_KEY)
        again = await storage.load()
        assert again.user_id == 777000
        assert again.auth_key() == KEY

    async def test_it_can_be_used_as_a_context_manager(self, storage):
        async with storage as opened:
            await opened.save(a_session())
        assert (await storage.load()).user_id == 777000


class TestSessionState:
    def test_keys_are_per_datacenter(self):
        state = SessionState(dc_id=2)
        state.set_auth_key(2, KEY)
        state.set_auth_key(5, OTHER_KEY)
        assert state.auth_key() == KEY
        assert state.auth_key(5) == OTHER_KEY
        assert state.auth_key(1) is None

    def test_a_key_of_the_wrong_size_is_refused(self):
        with pytest.raises(ValueError, match="256 bytes"):
            SessionState().set_auth_key(2, bytes(128))

    def test_a_key_can_be_forgotten(self):
        state = SessionState()
        state.set_auth_key(2, KEY)
        state.set_auth_key(2, None)
        assert state.auth_key(2) is None

    def test_the_key_never_stringifies(self):
        state = a_session()
        text = repr(state)
        assert KEY[:8].hex() not in text
        assert str(list(KEY[:8])) not in text
        # It still says which datacenters have one, which is not a secret.
        assert "keys_for=[4]" in text


class TestStringSession:
    def test_a_round_trip(self):
        text = encode_session(a_session())
        state = decode_session(text)
        assert state == a_session()

    def test_it_is_printable_and_has_no_padding(self):
        text = encode_session(a_session())
        assert text.isascii() and "=" not in text
        assert len(text) == 356

    def test_the_flags_survive(self):
        state = SessionState(dc_id=1, test_mode=True, user_id=-5, is_bot=True)
        state.set_auth_key(1, KEY)
        back = decode_session(encode_session(state))
        assert (back.test_mode, back.is_bot, back.user_id) == (True, True, -5)

    def test_a_session_with_no_key_cannot_be_exported(self):
        with pytest.raises(ValueError, match="nothing to export"):
            encode_session(SessionState())

    def test_only_the_home_key_travels(self):
        state = a_session()
        state.set_auth_key(1, OTHER_KEY)
        assert decode_session(encode_session(state)).auth_keys == {4: KEY}

    @pytest.mark.parametrize(
        "text", ["", "nonsense", "!!!!", "AAAA", "x" * 400]
    )
    def test_something_that_is_not_a_session_is_refused(self, text):
        with pytest.raises(ValueError):
            decode_session(text)

    def test_a_newer_version_is_refused_rather_than_misread(self):
        packed = bytearray(urlsafe_b64decode(encode_session(a_session())))
        packed[0] = VERSION + 1
        with pytest.raises(ValueError, match="version"):
            decode_session(urlsafe_b64encode(bytes(packed)).decode())

    def test_whitespace_around_it_is_forgiven(self):
        text = encode_session(a_session())
        assert decode_session(f"  {text}\n") == a_session()

    async def test_the_storage_exports_what_it_holds(self):
        storage = StringStorage()
        await storage.save(a_session())
        assert decode_session(storage.export()) == a_session()

    async def test_a_storage_can_be_built_from_a_string(self):
        text = encode_session(a_session())
        assert (await StringStorage(text).load()) == a_session()

    def test_a_bad_string_fails_at_construction(self):
        with pytest.raises(ValueError):
            StringStorage("not a session")

    def test_it_never_stringifies_the_key(self):
        text = repr(StringStorage(encode_session(a_session())))
        assert KEY[:8].hex() not in text

    def test_the_update_state_does_not_travel(self):
        # A pts per channel has no bound, and this has to stay one line a person
        # can paste. A session restored from a string asks the server where the
        # stream is instead.
        state = a_session()
        state.updates = UpdateState(pts=100, qts=5, date=17, seq=7, channels={-1: 3})
        restored = decode_session(encode_session(state))
        assert not restored.updates.known
        assert restored.updates.channels == {}


class TestUpdateStateEverywhere:
    async def test_a_fresh_session_does_not_know_where_the_stream_is(self, storage):
        assert not (await storage.load()).updates.known

    async def test_the_common_state_is_kept(self, storage):
        state = a_session()
        state.updates = UpdateState(pts=100, qts=5, date=1700000000, seq=7)
        await storage.save(state)
        kept = (await storage.load()).updates
        assert (kept.pts, kept.qts, kept.date, kept.seq) == (100, 5, 1700000000, 7)
        assert kept.known

    async def test_the_state_is_copied_out_like_everything_else(self, storage):
        await storage.save(a_session())
        loaded = await storage.load()
        loaded.updates.pts = 500
        assert (await storage.load()).updates.pts == 0


class TestSQLiteSession:
    async def test_a_pts_per_channel_is_kept(self, tmp_path):
        state = a_session()
        state.updates.channels = {-1001: 40, -1002: 12}
        async with SQLiteStorage(tmp_path / "session.db") as storage:
            await storage.save(state)
            assert (await storage.load()).updates.channels == {-1001: 40, -1002: 12}

    async def test_a_channel_we_left_stops_being_tracked(self, tmp_path):
        async with SQLiteStorage(tmp_path / "session.db") as storage:
            state = a_session()
            state.updates.channels = {-1001: 40, -1002: 12}
            await storage.save(state)
            del state.updates.channels[-1002]
            await storage.save(state)
            assert (await storage.load()).updates.channels == {-1001: 40}

    async def test_a_file_from_the_older_schema_gains_the_new_tables(self, tmp_path):
        # The update state went into tables of its own precisely so this works
        # by opening the file rather than by migrating it.
        path = tmp_path / "session.db"
        db = sqlite3.connect(path)
        try:
            db.executescript(
                "CREATE TABLE session (id INTEGER PRIMARY KEY CHECK (id = 1),"
                " dc_id INTEGER NOT NULL, test_mode INTEGER NOT NULL,"
                " user_id INTEGER NOT NULL, is_bot INTEGER NOT NULL);"
                "CREATE TABLE auth_keys (dc_id INTEGER PRIMARY KEY, key BLOB NOT NULL);"
                "INSERT INTO session VALUES (1, 4, 0, 777000, 0);"
                "PRAGMA user_version = 1;"
            )
            db.execute("INSERT INTO auth_keys VALUES (4, ?)", (KEY,))
            db.commit()
        finally:
            db.close()

        async with SQLiteStorage(path) as storage:
            state = await storage.load()
            assert state.user_id == 777000
            assert state.auth_key() == KEY
            assert not state.updates.known
            state.updates.pts = 55
            await storage.save(state)
            assert (await storage.load()).updates.pts == 55

    async def test_the_file_is_created(self, tmp_path):
        storage = SQLiteStorage(tmp_path / "session.db")
        assert not storage.path.exists()
        await storage.save(a_session())
        assert storage.path.exists()
        await storage.close()

    @pytest.mark.skipif(sys.platform == "win32", reason="permission bits differ")
    async def test_the_file_is_private(self, tmp_path):
        storage = SQLiteStorage(tmp_path / "session.db")
        await storage.open()
        assert (os.stat(storage.path).st_mode & 0o077) == 0
        await storage.close()

    async def test_it_survives_being_reopened(self, tmp_path):
        path = tmp_path / "session.db"
        async with SQLiteStorage(path) as storage:
            await storage.save(a_session())
        async with SQLiteStorage(path) as reopened:
            assert (await reopened.load()).auth_key() == KEY

    async def test_keys_for_several_datacenters_are_kept(self, tmp_path):
        state = a_session()
        state.set_auth_key(1, OTHER_KEY)
        async with SQLiteStorage(tmp_path / "session.db") as storage:
            await storage.save(state)
            assert (await storage.load()).auth_keys == {1: OTHER_KEY, 4: KEY}

    async def test_a_dropped_key_leaves_the_file(self, tmp_path):
        path = tmp_path / "session.db"
        async with SQLiteStorage(path) as storage:
            state = a_session()
            state.set_auth_key(1, OTHER_KEY)
            await storage.save(state)
            state.set_auth_key(1, None)
            await storage.save(state)
            assert (await storage.load()).auth_keys == {4: KEY}

    async def test_dropping_a_key_takes_it_out_of_the_bytes(self, tmp_path):
        # The path a logout actually takes: it clears the keys and saves, rather
        # than deleting the session, so this is the one that has to erase.
        path = tmp_path / "session.db"
        async with SQLiteStorage(path) as storage:
            state = a_session()
            await storage.save(state)
            assert KEY in path.read_bytes()
            state.auth_keys.clear()
            await storage.save(state)
            assert KEY not in path.read_bytes()

    async def test_a_logout_takes_the_key_out_of_the_bytes(self, tmp_path):
        # secure_delete plus the vacuum, so the key is gone from the file and
        # not merely unreferenced by it.
        path = tmp_path / "session.db"
        async with SQLiteStorage(path) as storage:
            await storage.save(a_session())
            assert KEY in path.read_bytes()
            await storage.delete()
        assert KEY not in path.read_bytes()

    async def test_the_schema_is_versioned(self, tmp_path):
        path = tmp_path / "session.db"
        async with SQLiteStorage(path) as storage:
            await storage.save(a_session())
        db = sqlite3.connect(path)
        try:
            assert db.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        finally:
            db.close()

    async def test_closing_twice_is_safe(self, tmp_path):
        storage = SQLiteStorage(tmp_path / "session.db")
        await storage.open()
        await storage.close()
        await storage.close()
        # And it opens again on demand rather than staying broken.
        assert await storage.load() == SessionState()
        await storage.close()

    async def test_concurrent_use_does_not_trip_over_itself(self, tmp_path):
        async with SQLiteStorage(tmp_path / "session.db") as storage:
            await asyncio.gather(*(storage.save(a_session()) for _ in range(8)))
            results = await asyncio.gather(*(storage.load() for _ in range(8)))
        assert all(state.auth_key() == KEY for state in results)
