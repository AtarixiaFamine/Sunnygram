# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""One string that names a file, and can be written down.

Everything else in this package names a file with an object: a document off a
message, a photo out of an answer, a location built from either. That is fine
inside one program and useless the moment the file has to outlive it. A queue,
a database row, a config file and a log line all want a string, and building one
by hand means picking apart a constructor and putting it back together later,
which is a module every program that stores files ends up writing.

So Sunnygram writes it once. A reference is the four things a file is named by,
packed and encoded: which datacenter holds it, its id, the access hash this
account was issued for it, and the file reference token. Give one back and it
can be sent anywhere or downloaded again, with no upload, no download, and
usually no call at all in between.

The one perishable part is the token. The id and the access hash are good for as
long as the file exists; the token goes stale after an hour or so, and the only
cure is to fetch whatever carried the file again. A reference made from a
message remembers which message that was, so it can do that for itself, which is
the difference between a string that works tomorrow and one that does not. Pass
origin=False to leave that out, for a reference that is going somewhere the chat
it came from should not go.
"""

from __future__ import annotations

import base64
import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from zlib import crc32

from ..errors import SunnygramError
from ..peers import mark_peer
from ..raw import types
from .location import FileSource, locate

if TYPE_CHECKING:
    from ..raw import base

__all__ = ["FileRef", "decode_ref", "file_ref", "parse_ref"]

# What version of the packing this is. A reference carries it, so a future
# format can be told apart from this one instead of being misread as it.
VERSION = 1

DOCUMENT = 1
PHOTO = 2

_HAS_SIZE = 1 << 0
_HAS_THUMB = 1 << 1
_HAS_NAME = 1 << 2
_HAS_ORIGIN = 1 << 3

# version, kind, datacenter, flags, then the two numbers that name the file.
_HEAD = struct.Struct("<BBBBqq")
_SIZE = struct.Struct("<Q")
_ORIGIN = struct.Struct("<qi")
_CHECK = struct.Struct("<I")

# A file reference token is a couple of dozen bytes. The length is written in
# one, which is plenty and is also the bound that keeps a malformed string from
# claiming a megabyte (rule S3).
_MAX_PART = 255


@dataclass(frozen=True, slots=True)
class FileRef:
    """A file, named portably: everything needed to fetch or resend it."""

    kind: int
    id: int
    access_hash: int
    file_reference: bytes
    dc_id: int
    size: int = 0
    thumb: str = ""
    name: str | None = None
    origin: tuple[int, int] | None = None

    def __repr__(self) -> str:
        what = "photo" if self.kind == PHOTO else "document"
        return f"FileRef({what} {self.id}, dc={self.dc_id}, size={self.size})"

    @property
    def is_photo(self) -> bool:
        return self.kind == PHOTO

    @property
    def input(self) -> Any:
        """The file as the protocol names it, for anything taking one."""
        if self.kind == PHOTO:
            return types.InputPhoto(
                id=self.id,
                access_hash=self.access_hash,
                file_reference=self.file_reference,
            )
        return types.InputDocument(
            id=self.id,
            access_hash=self.access_hash,
            file_reference=self.file_reference,
        )

    @property
    def media(self) -> base.InputMedia:
        """The file as something a send call can carry."""
        if self.kind == PHOTO:
            return types.InputMediaPhoto(id=self.input)
        return types.InputMediaDocument(id=self.input)

    @property
    def source(self) -> FileSource:
        """The file as something the download engine can fetch."""
        if self.kind == PHOTO:
            location: base.InputFileLocation = types.InputPhotoFileLocation(
                id=self.id,
                access_hash=self.access_hash,
                file_reference=self.file_reference,
                thumb_size=self.thumb,
            )
        else:
            location = types.InputDocumentFileLocation(
                id=self.id,
                access_hash=self.access_hash,
                file_reference=self.file_reference,
                thumb_size=self.thumb,
            )
        return FileSource(
            location=location, dc_id=self.dc_id, size=self.size, name=self.name
        )

    def encode(self) -> str:
        """Pack this back into the string form."""
        flags = 0
        if self.size:
            flags |= _HAS_SIZE
        if self.thumb:
            flags |= _HAS_THUMB
        if self.name:
            flags |= _HAS_NAME
        if self.origin is not None:
            flags |= _HAS_ORIGIN

        packed = bytearray(
            _HEAD.pack(
                VERSION, self.kind, self.dc_id, flags, self.id, self.access_hash
            )
        )
        packed += _part(self.file_reference, "file reference")
        if self.size:
            packed += _SIZE.pack(self.size)
        if self.thumb:
            packed += _part(self.thumb.encode(), "thumbnail size")
        if self.name:
            packed += _part(self.name.encode(), "file name")
        if self.origin is not None:
            packed += _ORIGIN.pack(*self.origin)
        packed += _CHECK.pack(crc32(bytes(packed)))
        return base64.urlsafe_b64encode(bytes(packed)).rstrip(b"=").decode()

    def __str__(self) -> str:
        return self.encode()


def file_ref(what: Any, *, thumb: str | None = None, origin: bool = True) -> str:
    """The portable reference for whatever file the caller is holding.

    Takes the same things locate does: a message, the media off one, a document
    or a photo. thumb names a particular rendition instead of the largest,
    which is how to write down a thumbnail on its own.

    A message also says where it came from, and that is packed in so the
    reference can refresh its own token later. Pass origin=False to leave it
    out.
    """
    source = locate(what, thumb=thumb)
    where = source.location
    if isinstance(where, types.InputPhotoFileLocation):
        kind = PHOTO
    elif isinstance(where, types.InputDocumentFileLocation):
        kind = DOCUMENT
    else:
        raise SunnygramError(
            f"{type(where).__name__} is not a file that can be written down. "
            f"Only documents and photos have a reference"
        )
    return FileRef(
        kind=kind,
        id=where.id,
        access_hash=where.access_hash,
        file_reference=where.file_reference,
        dc_id=source.dc_id,
        size=source.size,
        thumb=where.thumb_size or "",
        name=source.name,
        origin=_origin_of(what) if origin else None,
    ).encode()


def decode_ref(text: str) -> FileRef:
    """Read a reference back, or say why this is not one.

    Everything about the string is checked before anything is believed: the
    length, the version, the checksum, and that each part is inside what was
    written down. A reference that has been truncated in a database column or
    had a character eaten by a URL fails here rather than becoming a request
    for some other file (rule S3).
    """
    found = parse_ref(text)
    if found is None:
        raise SunnygramError(
            f"{text[:24]!r} is not a Sunnygram file reference. One is what "
            f"file_ref hands back, and it does not survive being edited"
        )
    return found


def parse_ref(text: str) -> FileRef | None:
    """The same, answering None instead of raising, for a caller that is guessing.

    This is what makes a string usable anywhere a file is: send_media and
    download can be handed one without a program having to say which of the two
    kinds of string it is holding.
    """
    if not isinstance(text, str) or not text:
        return None
    try:
        packed = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (ValueError, TypeError):
        return None
    if len(packed) < _HEAD.size + 1 + _CHECK.size:
        return None
    body, check = packed[: -_CHECK.size], packed[-_CHECK.size :]
    if _CHECK.unpack(check)[0] != crc32(body):
        return None

    version, kind, dc_id, flags, id, access_hash = _HEAD.unpack_from(body)
    if version != VERSION or kind not in (DOCUMENT, PHOTO):
        return None

    reader = _Reader(body, _HEAD.size)
    try:
        token = reader.part()
        size = reader.take(_SIZE)[0] if flags & _HAS_SIZE else 0
        thumb = reader.text() if flags & _HAS_THUMB else ""
        name = reader.text() if flags & _HAS_NAME else None
        origin = reader.take(_ORIGIN) if flags & _HAS_ORIGIN else None
    except (ValueError, struct.error, UnicodeDecodeError):
        return None
    if not reader.done:
        return None

    return FileRef(
        kind=kind,
        id=id,
        access_hash=access_hash,
        file_reference=token,
        dc_id=dc_id,
        size=size,
        thumb=thumb,
        name=name,
        origin=origin,
    )


class _Reader:
    """Reads the variable part, refusing to read past what is there."""

    __slots__ = ("_body", "_at")

    def __init__(self, body: bytes, at: int) -> None:
        self._body = body
        self._at = at

    @property
    def done(self) -> bool:
        return self._at == len(self._body)

    def part(self) -> bytes:
        length = self._body[self._at]
        start = self._at + 1
        if start + length > len(self._body):
            raise ValueError("this reference claims more than it carries")
        self._at = start + length
        return self._body[start : self._at]

    def text(self) -> str:
        return self.part().decode()

    def take(self, shape: struct.Struct) -> tuple[Any, ...]:
        if self._at + shape.size > len(self._body):
            raise ValueError("this reference claims more than it carries")
        found = shape.unpack_from(self._body, self._at)
        self._at += shape.size
        return found


def _origin_of(what: Any) -> tuple[int, int] | None:
    """Which message this file came from, spelled so it can be looked up again.

    The chat is marked the Bot API way, since that is one number instead of an
    id and a kind, and it is what resolve takes back.
    """
    message = getattr(what, "raw", what)
    if not isinstance(message, types.Message):
        return None
    marked = mark_peer(message.peer_id)
    if marked is None:
        return None
    return marked, message.id


def _part(value: bytes, what: str) -> bytes:
    """One piece with its length in front, which is what bounds the reader."""
    if len(value) > _MAX_PART:
        raise SunnygramError(
            f"this {what} is {len(value)} bytes, which is more than a "
            f"reference can carry"
        )
    return bytes((len(value),)) + value
