# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Reading what another library wrote down.

Two things stop someone trying Sunnygram on a project that already works, and
neither is about the library being any good. The first is the session: an
authorization key is the account, so without a way to read the one they already
have, trying Sunnygram means logging in again, which for a user account means a
code and possibly a second factor, and no one does that on a whim. The second is
their database: a project that has been running a while has a column full of
file ids, and if those cannot be read they are dead weight and every file has to
be uploaded again.

Both are the same shape of problem and both are finite, so both are solved here.
Nothing in this module is used by the library itself; it exists so that the cost
of trying Sunnygram is one line instead of an afternoon.

Two things it deliberately does not do. It does not write another library's
formats, because a one-way door is honest and a two-way one invites keeping a
project half-migrated for ever. And it does not delete or move anything it
reads: the file it was pointed at is left exactly as it was found, so going back
is always possible.

One caution worth reading before using any of this. An authorization key is one
session as far as Telegram is concerned, so two programs holding the same key
are one client with two heads. Running the old program and the new one at the
same time will work, in the sense that neither will break, and both will see
every update and each will think it is alone. Migrate, then stop the old one.
"""

from __future__ import annotations

import base64
import sqlite3
import struct
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any

from .errors import SunnygramError
from .peers import unmark_id
from .raw import base, types
from .storage import (
    PeerKind,
    PeerRecord,
    PeerStore,
    SessionState,
    Storage,
    UpdateState,
    storage_for,
)

__all__ = [
    "ForeignFileId",
    "ImportedSession",
    "MigrationError",
    "adopt_session",
    "as_media",
    "read_file_id",
    "read_foreign_file_id",
    "read_pyrogram_session",
    "read_session",
    "read_telethon_session",
]

AUTH_KEY_SIZE = 256

# Telethon writes a version character in front and then urlsafe base64 of
# dc_id, the server address, the port and the key. The address is four bytes or
# sixteen, which is the only thing that changes the length, so the length is
# what says which.
_TELETHON_VERSION = "1"
_TELETHON_IPV4 = ">B4sH256s"
_TELETHON_IPV6 = ">B16sH256s"

# Pyrogram has had three spellings of its session string, and they are told
# apart by length because none of them carries a version. Oldest first: a
# 32-bit user id, then a 64-bit one, then the current one which also carries
# the api_id.
_PYROGRAM_STRINGS = {
    351: (">B?256sI?", ("dc_id", "test_mode", "auth_key", "user_id", "is_bot")),
    356: (">B?256sQ?", ("dc_id", "test_mode", "auth_key", "user_id", "is_bot")),
    362: (
        ">BI?256sQ?",
        ("dc_id", "api_id", "test_mode", "auth_key", "user_id", "is_bot"),
    ),
}

# What Pyrogram calls the kinds of peer, across the versions that have spelled
# them differently. Secret chats have no place here: Sunnygram does not speak
# that protocol, so a row naming one is skipped, not half-imported.
_PYROGRAM_KINDS = {
    "user": PeerKind.USER,
    "bot": PeerKind.BOT,
    "chat": PeerKind.CHAT,
    "group": PeerKind.CHAT,
    "channel": PeerKind.CHANNEL,
    "supergroup": PeerKind.CHANNEL,
    "forum": PeerKind.CHANNEL,
    "direct": PeerKind.CHANNEL,
    "monoforum": PeerKind.CHANNEL,
}

# The test datacenters, by the addresses the other libraries write into their
# session files. A session that names one of these belongs to the test network,
# and starting it as a production session fails later and confusingly.
_TEST_ADDRESSES = frozenset(
    {"149.154.167.40", "149.154.175.10", "149.154.167.40:443", "2001:b28:f23d:f001::e"}
)


class MigrationError(SunnygramError):
    """Something another library wrote could not be read.

    Kept separate from the storage errors because the cause is almost always
    the wrong file instead of a broken one: a session belonging to a library
    this does not know, or a path that is a database of something else.
    """


@dataclass(frozen=True, slots=True)
class ImportedSession:
    """What another library's session turned out to be holding.

    The state is the part that matters and is enough on its own: the same
    authorization key means the same session, so a client built on this is
    already logged in. The peers are a bonus that is worth having, since they
    are the access hashes the old program had learned, and without them a
    migrated project cannot name a chat it only knows by id until it meets it
    again.
    """

    state: SessionState
    peers: tuple[PeerRecord, ...] = ()
    source: str = "unknown"
    api_id: int = 0

    def __repr__(self) -> str:
        # The state redacts itself; nothing is added here that would not (S2).
        return (
            f"ImportedSession(source={self.source!r}, peers={len(self.peers)}, "
            f"{self.state!r})"
        )


def read_session(where: str | Path, *, test_mode: bool | None = None) -> ImportedSession:
    """Read a session from either library, working out which it is.

    Takes a path to a session file or the session string itself. Which library
    wrote it is decided by looking, not by asking, because the two formats are
    unmistakable and a caller who has to know already knows too much.
    """
    text = str(where)
    if _looks_like_a_string(text):
        if text.startswith(_TELETHON_VERSION) and len(text) in (353, 365):
            return read_telethon_session(text, test_mode=test_mode)
        if len(text) in _PYROGRAM_STRINGS:
            return read_pyrogram_session(text, test_mode=test_mode)
        raise MigrationError(
            f"this is {len(text)} characters, which is not the length of any "
            "session string Telethon or Pyrogram writes"
        )

    path = Path(where)
    if not path.exists():
        raise MigrationError(f"there is no session at {path}")
    tables = _tables(path)
    if "entities" in tables or "sent_files" in tables:
        return read_telethon_session(path, test_mode=test_mode)
    if "peers" in tables:
        return read_pyrogram_session(path, test_mode=test_mode)
    raise MigrationError(
        f"{path} is a database, but not one Telethon or Pyrogram wrote: it has "
        f"{sorted(tables) or 'no tables'}"
    )


def read_telethon_session(
    where: str | Path, *, test_mode: bool | None = None
) -> ImportedSession:
    """Read a Telethon session file or StringSession.

    Telethon keeps no user id and no bot flag, so those come out zero and False
    and are filled in by the first call the client makes. It does keep the
    update counters and the entities it has met, and both are worth having: the
    counters save a full catch-up on the first run, and the entities are the
    access hashes without which a chat known only by id cannot be named.
    """
    if _looks_like_a_string(str(where)):
        return _telethon_string(str(where), test_mode)

    path = Path(where)
    with _opened(path) as db:
        row = _one(db, "SELECT dc_id, server_address, auth_key FROM sessions")
        if row is None:
            raise MigrationError(f"{path} holds no session row")
        dc_id, address, key = row
        state = SessionState(
            dc_id=int(dc_id),
            test_mode=_test_network(address, test_mode),
        )
        state.set_auth_key(int(dc_id), _key(key, path))
        state.updates = _telethon_updates(db)
        peers = _telethon_entities(db)
    return ImportedSession(state=state, peers=peers, source="telethon")


def read_pyrogram_session(
    where: str | Path, *, test_mode: bool | None = None
) -> ImportedSession:
    """Read a Pyrogram or Kurigram session file or session string.

    Pyrogram does keep the user id and the bot flag, so a session read from one
    comes out already knowing who it is. Kurigram writes the same formats and is
    read by the same code.
    """
    if _looks_like_a_string(str(where)):
        return _pyrogram_string(str(where), test_mode)

    path = Path(where)
    with _opened(path) as db:
        row = _one(
            db,
            "SELECT dc_id, test_mode, auth_key, user_id, is_bot, api_id FROM sessions",
            fallback="SELECT dc_id, test_mode, auth_key, user_id, is_bot FROM sessions",
        )
        if row is None:
            raise MigrationError(f"{path} holds no session row")
        dc_id, stored_test, key, user_id, is_bot = row[:5]
        api_id = int(row[5]) if len(row) > 5 and row[5] else 0
        state = SessionState(
            dc_id=int(dc_id),
            test_mode=bool(stored_test) if test_mode is None else test_mode,
            user_id=int(user_id or 0),
            is_bot=bool(is_bot),
        )
        state.set_auth_key(int(dc_id), _key(key, path))
        state.updates = _pyrogram_updates(db)
        peers = _pyrogram_peers(db)
    return ImportedSession(
        state=state, peers=peers, source="pyrogram", api_id=api_id
    )


async def adopt_session(
    imported: ImportedSession,
    storage: str | PathLike[str] | Storage,
    *,
    peers: bool = True,
) -> None:
    """Write an imported session into a Sunnygram storage, and close it.

    Names the destination the way `Client` does, so `adopt_session(imported,
    "account")` and `Client("account")` are the same file. A `Storage` that is
    already built is used as it is, for a caller that wants somewhere other
    than a file on disk.

    The storage is opened and closed here because that is the whole job: this
    runs once, before there is a client, and leaving an open handle behind for
    the caller to remember would be a worse API than doing both ends of it.
    """
    into = storage_for(storage)
    await into.open()
    try:
        await into.save(imported.state)
        if peers and imported.peers and isinstance(into, PeerStore):
            await into.put_peers(imported.peers)
    finally:
        await into.close()


# ------------------------------------------------------------------ sessions


def _telethon_string(text: str, test_mode: bool | None) -> ImportedSession:
    if not text.startswith(_TELETHON_VERSION):
        raise MigrationError(
            f"a Telethon session string starts with {_TELETHON_VERSION!r}, "
            f"this one starts with {text[:1]!r}"
        )
    body = _unbase64(text[1:])
    if len(body) == struct.calcsize(_TELETHON_IPV4):
        layout = _TELETHON_IPV4
    elif len(body) == struct.calcsize(_TELETHON_IPV6):
        layout = _TELETHON_IPV6
    else:
        raise MigrationError(
            f"a Telethon session string decodes to 263 or 275 bytes, this one "
            f"decodes to {len(body)}"
        )
    dc_id, _address, _port, key = struct.unpack(layout, body)
    state = SessionState(dc_id=dc_id, test_mode=bool(test_mode))
    state.set_auth_key(dc_id, _key(key, "the session string"))
    return ImportedSession(state=state, source="telethon")


def _pyrogram_string(text: str, test_mode: bool | None) -> ImportedSession:
    layout = _PYROGRAM_STRINGS.get(len(text))
    if layout is None:
        raise MigrationError(
            f"a Pyrogram session string is {sorted(_PYROGRAM_STRINGS)} characters, "
            f"this one is {len(text)}"
        )
    packing, names = layout
    fields = dict(zip(names, struct.unpack(packing, _unbase64(text))))
    dc_id = int(fields["dc_id"])
    state = SessionState(
        dc_id=dc_id,
        test_mode=bool(fields["test_mode"]) if test_mode is None else test_mode,
        user_id=int(fields["user_id"]),
        is_bot=bool(fields["is_bot"]),
    )
    state.set_auth_key(dc_id, _key(fields["auth_key"], "the session string"))
    return ImportedSession(
        state=state, source="pyrogram", api_id=int(fields.get("api_id", 0))
    )


def _telethon_updates(db: sqlite3.Connection) -> UpdateState:
    row = _one(db, "SELECT pts, qts, date, seq FROM update_state")
    if row is None:
        return UpdateState()
    pts, qts, date, seq = (int(value or 0) for value in row)
    return UpdateState(pts=pts, qts=qts, date=date, seq=seq)


def _pyrogram_updates(db: sqlite3.Connection) -> UpdateState:
    row = _one(db, "SELECT pts, qts, date, seq FROM update_state")
    if row is None:
        return UpdateState()
    pts, qts, date, seq = (int(value or 0) for value in row)
    return UpdateState(pts=pts, qts=qts, date=date, seq=seq)


def _telethon_entities(db: sqlite3.Connection) -> tuple[PeerRecord, ...]:
    rows = _all(db, "SELECT id, hash, username, phone FROM entities")
    records = []
    for marked, access_hash, username, phone in rows:
        record = _record(marked, access_hash, username, phone)
        if record is not None:
            records.append(record)
    return tuple(records)


def _pyrogram_peers(db: sqlite3.Connection) -> tuple[PeerRecord, ...]:
    # Newer Pyrogram moved usernames into a table of their own, since a peer may
    # have several. Older versions keep one on the peer row.
    rows = _all(
        db,
        "SELECT id, access_hash, type, phone_number, username FROM peers",
        fallback="SELECT id, access_hash, type, phone_number FROM peers",
    )
    extra = _usernames(db)
    records = []
    for row in rows:
        marked, access_hash, kind, phone = row[:4]
        spelled = str(kind or "")
        if spelled == "secret_chat" or spelled not in _PYROGRAM_KINDS:
            continue
        names = extra.get(int(marked), ())
        if not names and len(row) > 4 and row[4]:
            names = (str(row[4]),)
        record = _record(
            marked, access_hash, None, phone, kind=_PYROGRAM_KINDS[spelled]
        )
        if record is not None:
            records.append(
                PeerRecord(
                    id=record.id,
                    kind=record.kind,
                    access_hash=record.access_hash,
                    usernames=tuple(name.lower() for name in names),
                    phone=record.phone,
                )
            )
    return tuple(records)


def _usernames(db: sqlite3.Connection) -> dict[int, tuple[str, ...]]:
    rows = _all(db, "SELECT id, username FROM usernames", missing_is_empty=True)
    found: dict[int, list[str]] = {}
    for peer_id, username in rows:
        if username:
            found.setdefault(int(peer_id), []).append(str(username))
    return {peer_id: tuple(names) for peer_id, names in found.items()}


def _record(
    marked: Any,
    access_hash: Any,
    username: Any,
    phone: Any,
    *,
    kind: PeerKind | None = None,
) -> PeerRecord | None:
    """One row from either library, in Sunnygram's shape.

    Both of them write Bot API style ids, where the sign says what kind of peer
    it is, so the id has to be read back before it means anything to the
    protocol. A row naming a kind the sign cannot carry keeps the kind it was
    told, since that one is better informed.
    """
    try:
        peer_id, implied = unmark_id(int(marked))
    except (TypeError, ValueError):
        return None
    if peer_id <= 0:
        return None
    return PeerRecord(
        id=peer_id,
        kind=kind or implied,
        access_hash=int(access_hash or 0),
        usernames=(str(username).lower(),) if username else (),
        phone=str(phone) if phone else None,
    )


# --------------------------------------------------------------- file ids


@dataclass(frozen=True, slots=True)
class ForeignFileId:
    """A Pyrogram or Bot API file id, once it has been read.

    The fields are the ones that survive the trip: which datacenter holds it,
    the pair of numbers that name it there, and the reference that proves we
    were shown it. What kind of thing it is comes back as Pyrogram spells it,
    because that is the only vocabulary the string carries.
    """

    kind: str
    dc_id: int
    media_id: int
    access_hash: int
    file_reference: bytes = b""
    version: tuple[int, int] = (0, 0)
    url: str | None = None
    extra: dict[str, int] = field(default_factory=dict)

    @property
    def is_photo(self) -> bool:
        return self.kind == "photo"

    @property
    def is_document(self) -> bool:
        return self.kind == "document"

    @property
    def sendable(self) -> bool:
        """Whether this names something that can be sent on again.

        A photo or a document can. A thumbnail, a profile picture or a wallpaper
        cannot: those are places inside a file instead of a file someone may
        post, and Telegram has nothing to send them as.
        """
        return self.url is None and self.kind in ("photo", "document")


# Pyrogram's numbering of what a file is. Only the split into photos and
# documents matters here, because that is the split Telegram's own input types
# make, but the names are kept so an unsendable one can say what it was.
_FILE_TYPES = {
    0: "thumbnail",
    1: "chat_photo",
    2: "photo",
    3: "voice",
    4: "video",
    5: "document",
    6: "encrypted",
    7: "temp",
    8: "sticker",
    9: "audio",
    10: "animation",
    11: "encrypted_thumbnail",
    12: "wallpaper",
    13: "video_note",
    14: "secure_raw",
    15: "secure",
    16: "background",
    17: "document_as_file",
}

# The ones stored as photos rather than as documents, which is what decides
# both how the rest of the string is laid out and which input type it becomes.
_PHOTO_TYPES = frozenset({0, 1, 2, 11, 12})

_WEB_LOCATION_FLAG = 1 << 24
_FILE_REFERENCE_FLAG = 1 << 25

# The newest layout anybody writes is 4. Reading a version above this would be
# guessing at a layout, so the ceiling is a little above it and no further.
_NEWEST_VERSION = 8


def read_file_id(file_id: str) -> ForeignFileId:
    """Read a Pyrogram or Bot API file id.

    One way on purpose. Sunnygram writes its own references, which say where
    they came from so they can renew themselves, and being able to write this
    format as well would mostly be a way to stay half-migrated. Reading it means
    a project's existing column of file ids keeps working, which is the part
    that actually costs money to replace.
    """
    raw = _rle_decode(_unbase64(file_id))
    if len(raw) < 4:
        raise MigrationError("this is too short to be a file id")

    major = raw[-1]
    if not 2 <= major <= _NEWEST_VERSION:
        # Checked before anything is read off it. Most of what reaches here and
        # is not a file id is a path someone passed to a function that takes
        # either, and a version no one has ever written is the cheapest way to
        # say so before the layout is guessed at.
        raise MigrationError(
            f"version {major} is not a file id version this knows about"
        )
    minor = raw[-2] if major >= 4 else 0
    body = raw[:-2] if major >= 4 else raw[:-1]

    reader = _Cursor(body, file_id)
    packed, dc_id = reader.unpack("<ii")
    has_web = bool(packed & _WEB_LOCATION_FLAG)
    has_reference = bool(packed & _FILE_REFERENCE_FLAG)
    number = packed & ~_WEB_LOCATION_FLAG & ~_FILE_REFERENCE_FLAG
    named = _FILE_TYPES.get(number)
    if named is None:
        raise MigrationError(f"{number} is not a kind of file this knows about")

    if has_web:
        url = reader.string()
        (access_hash,) = reader.unpack("<q")
        return ForeignFileId(
            kind=named,
            dc_id=dc_id,
            media_id=0,
            access_hash=access_hash,
            version=(major, minor),
            url=url,
        )

    reference = reader.bytestring() if has_reference else b""
    media_id, access_hash = reader.unpack("<qq")
    kind = "photo" if number in _PHOTO_TYPES else "document"
    if number in (0, 1, 11, 12):
        # A thumbnail, a profile picture or a wallpaper: stored as a photo but
        # not a thing anybody can post, so it keeps its own name and will be
        # refused by as_media instead of becoming a broken send.
        kind = named
    return ForeignFileId(
        kind=kind,
        dc_id=dc_id,
        media_id=media_id,
        access_hash=access_hash,
        file_reference=reference,
        version=(major, minor),
    )


def as_media(file_id: str | ForeignFileId) -> base.InputMedia:
    """Turn a Pyrogram file id into something send_media understands.

    The whole point of reading one: a stored id becomes a message with no
    upload and no download in between. What comes back is the same input media
    Sunnygram's own references produce, so everything downstream of this knows
    nothing about where it came from.
    """
    read = read_file_id(file_id) if isinstance(file_id, str) else file_id
    if read.url is not None:
        raise MigrationError(
            "this file id names a file on the web rather than one Telegram "
            "holds, and there is nothing to send it as"
        )
    if not read.sendable:
        raise MigrationError(
            f"this file id names a {read.kind}, which is a place inside a file "
            "rather than a file that can be sent"
        )
    if read.is_photo:
        return types.InputMediaPhoto(
            id=types.InputPhoto(
                id=read.media_id,
                access_hash=read.access_hash,
                file_reference=read.file_reference,
            )
        )
    return types.InputMediaDocument(
        id=types.InputDocument(
            id=read.media_id,
            access_hash=read.access_hash,
            file_reference=read.file_reference,
        )
    )


def read_foreign_file_id(text: str) -> base.InputMedia | None:
    """as_media, for a caller that is holding either a file id or a path.

    The distinction that matters: a string that is not a file id at all comes
    back as nothing, because it is probably a path and the caller is about to
    open it. A string that really is a file id but names something unsendable
    still raises, because at that point there is no other reading of what the
    caller meant, and quietly treating it as a filename would be a much worse
    error message than the true one.
    """
    try:
        read = read_file_id(text)
    except MigrationError:
        return None
    return as_media(read)


class _Cursor:
    """A place in a decoded file id, with the bounds checks that go with it.

    Server data, or near enough: a file id arrives from a database someone else
    filled, so a truncated one has to say so instead of raise something from
    the middle of struct (rule S3).
    """

    __slots__ = ("_data", "_at", "_what")

    def __init__(self, data: bytes, what: str) -> None:
        self._data = data
        self._at = 0
        self._what = what

    def take(self, count: int) -> bytes:
        if count < 0 or self._at + count > len(self._data):
            raise MigrationError(
                f"{self._what[:16]}... ends in the middle of itself"
            )
        piece = self._data[self._at : self._at + count]
        self._at += count
        return piece

    def unpack(self, layout: str) -> tuple[int, ...]:
        return struct.unpack(layout, self.take(struct.calcsize(layout)))

    def bytestring(self) -> bytes:
        """A TL string, which is what a file reference is written as."""
        first = self.take(1)[0]
        if first <= 253:
            length, padding = first, (-(first + 1)) % 4
        else:
            length = int.from_bytes(self.take(3), "little")
            padding = (-length) % 4
        value = self.take(length)
        self.take(padding)
        return value

    def string(self) -> str:
        return self.bytestring().decode("utf-8", "replace")


# ------------------------------------------------------------------ helpers


def _rle_decode(data: bytes) -> bytes:
    """Undo the run-length trick file ids use to squeeze out zero bytes.

    A zero says the next byte is how many zeroes there really were. It exists
    because the middle of a file id is mostly zeroes and the string is meant to
    be short enough to paste.
    """
    out = bytearray()
    zero = False
    for byte in data:
        if not byte:
            zero = True
            continue
        if zero:
            out.extend(b"\x00" * byte)
            zero = False
        else:
            out.append(byte)
    return bytes(out)


def _unbase64(text: str) -> bytes:
    """Decode url-safe base64 that may or may not have been padded."""
    try:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (ValueError, TypeError) as bad:
        raise MigrationError("this is not valid base64") from bad


def _key(value: Any, where: Any) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise MigrationError(f"the authorization key in {where} is not bytes")
    key = bytes(value)
    if len(key) != AUTH_KEY_SIZE:
        raise MigrationError(
            f"an authorization key is {AUTH_KEY_SIZE} bytes and the one in "
            f"{where} is {len(key)}, so this is not a session this can read"
        )
    return key


def _looks_like_a_string(text: str) -> bool:
    """Whether this is a session string, not a path to a file.

    A session string is long, has no separators, and is base64. A path is not
    all three, and the one case that could be confused, a very long filename,
    is not one anybody has.
    """
    if len(text) < 300 or any(mark in text for mark in "/\\ .:"):
        return False
    return all(
        letter.isalnum() or letter in "-_=" for letter in text
    )


def _test_network(address: Any, told: bool | None) -> bool:
    if told is not None:
        return told
    return str(address or "") in _TEST_ADDRESSES


@contextmanager
def _opened(path: Path) -> Iterator[sqlite3.Connection]:
    """Open someone else's session file without writing to it.

    Read-only through a uri, because the file belongs to a program that may
    still be running and this has no business changing it, or leaving a journal
    beside it.

    Closing is done here instead of by a plain `with` on the connection,
    because sqlite3's own context manager commits a transaction and does not
    close anything, which leaves a handle on a file this promised not to touch.
    """
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as bad:
        raise MigrationError(f"{path} could not be opened: {bad}") from bad
    try:
        yield db
    finally:
        db.close()


def _tables(path: Path) -> set[str]:
    with _opened(path) as db:
        try:
            rows = db.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        except sqlite3.DatabaseError as bad:
            raise MigrationError(f"{path} is not a database: {bad}") from bad
    return {str(name) for (name,) in rows}


def _one(
    db: sqlite3.Connection, query: str, *, fallback: str | None = None
) -> tuple[Any, ...] | None:
    rows = _all(db, query, fallback=fallback)
    return rows[0] if rows else None


def _all(
    db: sqlite3.Connection,
    query: str,
    *,
    fallback: str | None = None,
    missing_is_empty: bool = False,
) -> list[tuple[Any, ...]]:
    """Run a query, falling back to an older schema's spelling of it.

    Both libraries have added columns over the years and neither renumbers its
    schema in a way that can be read from outside, so the way to find out which
    version wrote a file is to ask it for the newer columns and see.
    """
    try:
        return list(db.execute(query).fetchall())
    except sqlite3.DatabaseError:
        if fallback is not None:
            try:
                return list(db.execute(fallback).fetchall())
            except sqlite3.DatabaseError:
                pass
        if missing_is_empty:
            return []
        raise
