"""Reading what Telethon and Pyrogram wrote.

Everything here is checked against the real thing, and then frozen. The session
schemas below were taken from Telethon 1.34 and 1.44 and from Pyrogram 2.2.23
by creating a session with each and reading back what it had written; the file
ids were produced by Pyrogram's own encoder. Freezing them is what keeps this
suite offline (rule H4) while still testing against formats nobody here made up.

Two things are being checked, and the second is the one that bites. The obvious
one is that the fields come out with the values that went in. The other is that
a peer id survives the trip: both libraries write Bot API style ids, where the
sign carries the kind and a channel is offset by a trillion, and a reader that
takes those at face value produces a cache full of peers that cannot be reached.
"""

from __future__ import annotations

import base64
import sqlite3
import struct
from pathlib import Path

import pytest

from sunnygram.migrate import (
    MigrationError,
    adopt_session,
    read_file_id,
    read_pyrogram_session,
    read_session,
    read_telethon_session,
)
from sunnygram.methods import existing_media
from sunnygram.raw import types
from sunnygram.storage import MemoryStorage, PeerKind, storage_for as _storage_for

KEY = bytes(range(256))

# Telethon 1.44. Version 1.34 is the same without tmp_auth_key, which is why
# the reader asks for the three columns it needs rather than for the row.
TELETHON_SCHEMA = """
CREATE TABLE version (version integer primary key);
CREATE TABLE sessions (
    dc_id integer primary key, server_address text, port integer,
    auth_key blob, takeout_id integer, tmp_auth_key blob);
CREATE TABLE entities (
    id integer primary key, hash integer not null, username text,
    phone integer, name text, date integer);
CREATE TABLE sent_files (
    md5_digest blob, file_size integer, type integer, id integer, hash integer,
    primary key(md5_digest, file_size, type));
CREATE TABLE update_state (
    id integer primary key, pts integer, qts integer, date integer, seq integer);
"""

# Pyrogram 2.2.23. Usernames moved to a table of their own once a peer could
# have several; the older shape below keeps one on the peer row.
PYROGRAM_SCHEMA = """
CREATE TABLE sessions (
    dc_id INTEGER PRIMARY KEY, server_address TEXT, port INTEGER, api_id INTEGER,
    test_mode INTEGER, auth_key BLOB, date INTEGER NOT NULL, user_id INTEGER,
    is_bot INTEGER);
CREATE TABLE peers (
    id INTEGER PRIMARY KEY, access_hash INTEGER, type INTEGER NOT NULL,
    phone_number TEXT, last_update_on INTEGER NOT NULL DEFAULT 0);
CREATE TABLE usernames (id INTEGER, username TEXT);
CREATE TABLE update_state (
    id INTEGER PRIMARY KEY, pts INTEGER, qts INTEGER, date INTEGER, seq INTEGER);
CREATE TABLE version (number INTEGER PRIMARY KEY);
"""

OLD_PYROGRAM_SCHEMA = """
CREATE TABLE sessions (
    dc_id INTEGER PRIMARY KEY, test_mode INTEGER, auth_key BLOB,
    date INTEGER NOT NULL, user_id INTEGER, is_bot INTEGER);
CREATE TABLE peers (
    id INTEGER PRIMARY KEY, access_hash INTEGER, type INTEGER NOT NULL,
    username TEXT, phone_number TEXT, last_update_on INTEGER NOT NULL DEFAULT 0);
CREATE TABLE update_state (
    id INTEGER PRIMARY KEY, pts INTEGER, qts INTEGER, date INTEGER, seq INTEGER);
"""

# Written by Telethon 1.44's StringSession.save over the key above, at dc 2.
TELETHON_STRING = (
    "1ApWapzMBuwABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx"
    "MjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlq"
    "a2xtbm9wcXJzdHV2d3h5ent8fX5_gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp-goaKj"
    "pKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2-v8DBwsPExcbHyMnKy8zNzs_Q0dLT1NXW19jZ2tvc"
    "3d7f4OHi4-Tl5ufo6err7O3u7_Dx8vP09fb3-Pn6-_z9_v8="
)

# Written by Pyrogram 2.2.23's export_session_string: dc 4, api_id 12345,
# user 777000, not a bot, production.
PYROGRAM_STRING = (
    "BAAAMDkAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy"
    "MzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWpr"
    "bG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOk"
    "paanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd"
    "3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_wAAAAAAC9soAA"
)

# Pyrogram's own encoder produced every one of these. The trailing columns are
# what it says they decode to.
FILE_IDS = [
    # (file id, dc, media id, access hash, reference hex, kind)
    (
        "BQACAgIAAwwBAgMEBQYHCAkKCwwABJBStFbo1FABTt68gBoghB4E",
        2,
        5824535677187035136,
        -8926105321221501439,
        "0102030405060708090a0b0c",
        "document",
    ),
    (
        "CAACAgIAAwwBAgMEBQYHCAkKCwwABJBStFbo1FABTt68gBoghB4E",
        2,
        5824535677187035136,
        -8926105321221501439,
        "0102030405060708090a0b0c",
        "document",
    ),
    (
        "AgACAgQAAwMAAQECFYHpffQQIhGISwe2oCVL8gAIAQADAgADeAAHHgQ",
        4,
        1234567890123456789,
        -987654321098765432,
        "000102",
        "photo",
    ),
    ("BQADAQADKgAHYwAHHgADBAADHgQ", 1, 42, 99, "", "document"),
    (
        "BQACAgUAAwj__________wAD_____________________x4E",
        5,
        -1,
        -1,
        "ffffffffffffffff",
        "document",
    ),
]


def _build(path: Path, schema: str, rows: dict[str, list[tuple]]) -> Path:
    db = sqlite3.connect(path)
    db.executescript(schema)
    for table, values in rows.items():
        if not values:
            continue
        marks = ", ".join("?" * len(values[0]))
        db.executemany(f"INSERT INTO {table} VALUES ({marks})", values)
    db.commit()
    db.close()
    return path


@pytest.fixture
def telethon(tmp_path: Path) -> Path:
    return _build(
        tmp_path / "telethon.session",
        TELETHON_SCHEMA,
        {
            "sessions": [(2, "149.154.167.51", 443, KEY, None, None)],
            "update_state": [(0, 1234, 56, 1700000000, 78)],
            # Marked ids, exactly as Telethon writes them.
            "entities": [
                (111, 999, "someone", 39123, "A", 0),
                (-1000000000222, 888, "achannel", None, "C", 0),
                (-333, 0, None, None, "G", 0),
            ],
        },
    )


@pytest.fixture
def pyrogram(tmp_path: Path) -> Path:
    return _build(
        tmp_path / "pyrogram.session",
        PYROGRAM_SCHEMA,
        {
            "sessions": [(4, None, None, 12345, 0, KEY, 0, 777000, 0)],
            "update_state": [(0, 1234, 56, 1700000000, 78)],
            "peers": [
                (111, 999, "user", "39123", 0),
                (-1000000000222, 888, "channel", None, 0),
                (-333, 0, "chat", None, 0),
            ],
            "usernames": [(111, "someone"), (-1000000000222, "achannel")],
        },
    )


class TestTelethonSessions:
    def test_the_key_and_the_datacenter_come_across(self, telethon):
        imported = read_session(telethon)
        assert imported.source == "telethon"
        assert imported.state.dc_id == 2
        assert imported.state.auth_key(2) == KEY

    def test_the_update_counters_come_across(self, telethon):
        # Worth having on its own: without them the first run fetches the whole
        # difference, and with them it starts where the old program stopped.
        updates = read_session(telethon).state.updates
        assert (updates.pts, updates.qts, updates.date, updates.seq) == (
            1234,
            56,
            1700000000,
            78,
        )

    def test_a_marked_id_is_read_back_to_a_real_one(self, telethon):
        # The trap. Telethon writes Bot API ids, so a channel is stored a
        # trillion below zero and a group is stored negative. Taking those at
        # face value gives a cache of peers that cannot be reached.
        peers = {peer.id: peer for peer in read_session(telethon).peers}
        assert set(peers) == {111, 222, 333}
        assert peers[111].kind is PeerKind.USER
        assert peers[222].kind is PeerKind.CHANNEL
        assert peers[333].kind is PeerKind.CHAT

    def test_the_access_hashes_come_across(self, telethon):
        peers = {peer.id: peer for peer in read_session(telethon).peers}
        assert peers[111].access_hash == 999
        assert peers[222].access_hash == 888
        # A basic group has no access hash, and zero is the right value there
        # rather than a missing one.
        assert peers[333].access_hash == 0

    def test_what_a_peer_can_be_named_by_comes_across(self, telethon):
        peers = {peer.id: peer for peer in read_session(telethon).peers}
        assert peers[111].usernames == ("someone",)
        assert peers[111].phone == "39123"
        assert peers[222].usernames == ("achannel",)

    def test_a_string_session_carries_the_key(self):
        imported = read_session(TELETHON_STRING)
        assert imported.source == "telethon"
        assert imported.state.dc_id == 2
        assert imported.state.auth_key(2) == KEY

    def test_a_string_session_carries_no_peers(self):
        # Telethon's string is one line by design, so it holds a key and a
        # datacenter and nothing else. Saying so beats appearing to lose them.
        assert read_session(TELETHON_STRING).peers == ()

    def test_a_session_file_is_not_written_to(self, telethon):
        before = telethon.read_bytes()
        read_session(telethon)
        assert telethon.read_bytes() == before
        assert not (telethon.parent / "telethon.session-journal").exists()


class TestPyrogramSessions:
    def test_it_knows_who_it_is(self, pyrogram):
        # The difference from Telethon: Pyrogram keeps the user id and the bot
        # flag, so a session read from one is already authorized.
        imported = read_session(pyrogram)
        assert imported.source == "pyrogram"
        assert imported.state.dc_id == 4
        assert imported.state.user_id == 777000
        assert imported.state.is_bot is False
        assert imported.state.authorized
        assert imported.api_id == 12345

    def test_the_key_and_counters_come_across(self, pyrogram):
        imported = read_session(pyrogram)
        assert imported.state.auth_key(4) == KEY
        assert imported.state.updates.pts == 1234

    def test_peers_come_across_unmarked(self, pyrogram):
        peers = {peer.id: peer for peer in read_session(pyrogram).peers}
        assert set(peers) == {111, 222, 333}
        assert peers[222].kind is PeerKind.CHANNEL
        assert peers[222].access_hash == 888
        assert peers[111].usernames == ("someone",)

    def test_a_peer_with_several_usernames_keeps_them_all(self, tmp_path):
        path = _build(
            tmp_path / "many.session",
            PYROGRAM_SCHEMA,
            {
                "sessions": [(2, None, None, 1, 0, KEY, 0, 1, 0)],
                "peers": [(-1000000000222, 888, "channel", None, 0)],
                "usernames": [(-1000000000222, "one"), (-1000000000222, "two")],
            },
        )
        (peer,) = read_session(path).peers
        assert peer.usernames == ("one", "two")

    def test_an_older_layout_is_read_too(self, tmp_path):
        # Older Pyrogram kept one username on the peer row and had no api_id.
        # Both are asked for and both are allowed to be missing.
        path = _build(
            tmp_path / "old.session",
            OLD_PYROGRAM_SCHEMA,
            {
                "sessions": [(2, 0, KEY, 0, 555, 1)],
                "peers": [(111, 999, "user", "someone", None, 0)],
            },
        )
        imported = read_session(path)
        assert imported.state.user_id == 555
        assert imported.state.is_bot is True
        assert imported.api_id == 0
        (peer,) = imported.peers
        assert peer.usernames == ("someone",)

    def test_a_secret_chat_is_skipped_rather_than_half_imported(self, tmp_path):
        path = _build(
            tmp_path / "secret.session",
            PYROGRAM_SCHEMA,
            {
                "sessions": [(2, None, None, 1, 0, KEY, 0, 1, 0)],
                "peers": [(111, 999, "user", None, 0), (-2000000000444, 7, "secret_chat", None, 0)],
            },
        )
        assert [peer.id for peer in read_session(path).peers] == [111]

    def test_the_current_string_session_is_read(self):
        imported = read_session(PYROGRAM_STRING)
        assert imported.source == "pyrogram"
        assert imported.state.dc_id == 4
        assert imported.state.user_id == 777000
        assert imported.state.auth_key(4) == KEY
        assert imported.api_id == 12345

    @pytest.mark.parametrize(
        "layout, values",
        [
            (">B?256sI?", (2, False, KEY, 777000, False)),
            (">B?256sQ?", (2, False, KEY, 777000, False)),
        ],
    )
    def test_the_older_string_sessions_are_read(self, layout, values):
        # Neither old format carries a version, so length is the only thing
        # that tells the three apart. That is worth a test each.
        text = base64.urlsafe_b64encode(struct.pack(layout, *values)).decode().rstrip("=")
        imported = read_session(text)
        assert imported.state.dc_id == 2
        assert imported.state.user_id == 777000
        assert imported.state.auth_key(2) == KEY


class TestRefusing:
    def test_a_database_of_something_else_says_so(self, tmp_path):
        path = _build(tmp_path / "other.db", "CREATE TABLE cats (name text);", {})
        with pytest.raises(MigrationError, match="not one Telethon or Pyrogram wrote"):
            read_session(path)

    def test_a_path_that_is_not_there_says_so(self, tmp_path):
        with pytest.raises(MigrationError, match="no session at"):
            read_session(tmp_path / "nothing.session")

    def test_a_key_of_the_wrong_length_is_refused(self, tmp_path):
        # A row that parses but holds sixteen bytes where a key belongs is not
        # a session, and finding out at the handshake would be much worse.
        path = _build(
            tmp_path / "short.session",
            PYROGRAM_SCHEMA,
            {"sessions": [(2, None, None, 1, 0, b"\x00" * 16, 0, 1, 0)]},
        )
        with pytest.raises(MigrationError, match="256 bytes"):
            read_session(path)

    def test_a_string_of_no_known_length_says_so(self):
        with pytest.raises(MigrationError, match="not the length of any"):
            read_session("A" * 400)

    def test_a_telethon_string_of_the_wrong_version_says_so(self):
        with pytest.raises(MigrationError, match="starts with"):
            read_telethon_session("9" + "A" * 352)


class TestAdopting:
    async def test_an_imported_session_lands_in_a_storage(self, pyrogram):
        storage = MemoryStorage()
        await adopt_session(read_pyrogram_session(pyrogram), storage)
        await storage.open()
        try:
            state = await storage.load()
            assert state.auth_key(4) == KEY
            assert state.user_id == 777000
            assert (await storage.peer_by_id(222)).access_hash == 888
        finally:
            await storage.close()

    async def test_a_path_lands_where_the_client_would_look(self, pyrogram, tmp_path):
        # The two-line migration in the README names a session as a string, and
        # so does Client. If those two spellings disagreed by so much as the
        # .session suffix, adopt_session would write a file the client never
        # opens, and the symptom would be being asked to log in again, which
        # looks exactly like the importer not working at all.
        named = tmp_path / "account"
        await adopt_session(read_pyrogram_session(pyrogram), named)

        opened = _storage_for(named)
        await opened.open()
        try:
            assert (await opened.load()).auth_key(4) == KEY
        finally:
            await opened.close()
        assert (tmp_path / "account.session").exists()

    async def test_a_storage_that_is_already_built_is_used_as_it_is(self, pyrogram):
        given = MemoryStorage()
        await adopt_session(read_pyrogram_session(pyrogram), given)
        await given.open()
        try:
            assert (await given.load()).auth_key(4) == KEY
        finally:
            await given.close()

    async def test_the_peers_can_be_left_behind(self, pyrogram):
        storage = MemoryStorage()
        await adopt_session(read_pyrogram_session(pyrogram), storage, peers=False)
        await storage.open()
        try:
            assert await storage.peer_by_id(222) is None
        finally:
            await storage.close()


class TestFileIds:
    @pytest.mark.parametrize("file_id, dc, media_id, access_hash, reference, kind", FILE_IDS)
    def test_pyrograms_own_output_reads_back(
        self, file_id, dc, media_id, access_hash, reference, kind
    ):
        read = read_file_id(file_id)
        assert read.dc_id == dc
        assert read.media_id == media_id
        assert read.access_hash == access_hash
        assert read.file_reference.hex() == reference
        assert read.kind == kind

    def test_a_document_becomes_something_sendable(self):
        media = existing_media(FILE_IDS[0][0])
        assert isinstance(media, types.InputMediaDocument)
        assert media.id.id == FILE_IDS[0][2]
        assert media.id.access_hash == FILE_IDS[0][3]
        assert media.id.file_reference.hex() == FILE_IDS[0][4]

    def test_a_photo_becomes_something_sendable(self):
        media = existing_media(FILE_IDS[2][0])
        assert isinstance(media, types.InputMediaPhoto)
        assert media.id.id == FILE_IDS[2][2]

    @pytest.mark.parametrize(
        "text", ["photo.jpg", "a/path/to/file.mp4", "", "hello", "C:\\files\\x.png"]
    )
    def test_a_path_is_still_a_path(self, text):
        # The contract existing_media has to keep: anything that is not one of
        # these comes back as nothing, so a caller can offer a file id or a
        # filename without knowing which it was given.
        assert existing_media(text) is None

    def test_a_thumbnail_is_refused_rather_than_sent_wrong(self):
        # A thumbnail is a place inside a file, not a file anybody can post.
        # Telegram has nothing to send it as, so saying so beats a send that
        # fails on the wire for a reason nobody can read.
        thumbnail = read_file_id(FILE_IDS[2][0])
        assert thumbnail.sendable
        with pytest.raises(MigrationError, match="place inside a file"):
            from sunnygram.migrate import ForeignFileId, as_media

            as_media(ForeignFileId(kind="thumbnail", dc_id=2, media_id=1, access_hash=2))

    def test_a_truncated_file_id_says_so_rather_than_raising_from_struct(self):
        # Somebody else's database filled this column, so a half-copied value
        # has to fail as a bad file id (rule S3).
        whole = base64.urlsafe_b64decode(FILE_IDS[0][0] + "==")
        cut = base64.urlsafe_b64encode(whole[:9]).decode().rstrip("=")
        with pytest.raises(MigrationError):
            read_file_id(cut)
