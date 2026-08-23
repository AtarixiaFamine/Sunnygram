# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Working out what to ask for, and where.

A file on Telegram is not named by a URL. It is named by a location, which is
four or five numbers, plus the datacenter that holds it, and the two travel
separately: the location comes out of a document or a photo, and the datacenter
is a field on that same object, not anything the location knows.

The awkward part is the file reference. It is a short-lived token, baked into
the location, that says this account is allowed to ask for this file right now.
It goes stale in about an hour, and the only way to get a fresh one is to fetch
whatever carried the file again: the message, the profile, the sticker set. So a
location is not a durable handle, and code that stores one and comes back
tomorrow will be told so.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..raw import types

if TYPE_CHECKING:
    from ..raw import base

__all__ = ["FileSource", "locate"]


@dataclass(frozen=True, slots=True)
class FileSource:
    """Everything needed to fetch one file, and nothing else.

    size is what the server said the file is, and zero when nothing said. The
    download engine can work either way, but only a known size lets it ask for
    several pieces at once, so a source with no size is fetched in order.
    """

    location: base.InputFileLocation
    dc_id: int
    size: int = 0
    name: str | None = None

    def __repr__(self) -> str:
        return (
            f"FileSource({type(self.location).__name__}, dc={self.dc_id}, "
            f"size={self.size}, name={self.name!r})"
        )


def locate(what: Any, *, thumb: str | None = None) -> FileSource:
    """Find the file inside whatever the caller happens to be holding.

    Takes a message, the media off one, a document, a photo, or the portable
    reference string file_ref hands back, and unwraps until it reaches
    something with a location. thumb picks a particular size instead of the
    largest one, which for a document means one of its thumbnails and for a
    photo means one of its renditions.
    """
    if isinstance(what, FileSource):
        return what

    # A friendly Message instead of the one off the wire. The same file is
    # inside either way, and unwrapping here rather than making callers do it
    # is what lets a handler write download(message).
    carried = getattr(what, "raw", None)
    if isinstance(carried, types.Message):
        what = carried

    if isinstance(what, str):
        # A portable reference, which is a file written down. Imported here
        # instead of at the top because ref.py is built on this module, and
        # the two only meet at this one line.
        from .ref import decode_ref

        return decode_ref(what).source

    if isinstance(what, types.Message):
        if what.media is None:
            raise SunnygramError("this message carries no file")
        return locate(what.media, thumb=thumb)

    if isinstance(what, types.MessageMediaDocument):
        if what.document is None:
            raise SunnygramError("this media has no document, perhaps it expired")
        return locate(what.document, thumb=thumb)

    if isinstance(what, types.MessageMediaPhoto):
        if what.photo is None:
            raise SunnygramError("this media has no photo, perhaps it expired")
        return locate(what.photo, thumb=thumb)

    if isinstance(what, types.Document):
        return _from_document(what, thumb)

    if isinstance(what, types.Photo):
        return _from_photo(what, thumb)

    raise SunnygramError(f"there is no file in a {type(what).__name__}")


def _from_document(document: types.Document, thumb: str | None) -> FileSource:
    size = document.size
    if thumb is not None:
        size = _thumb_size(document.thumbs or [], thumb)
    return FileSource(
        location=types.InputDocumentFileLocation(
            id=document.id,
            access_hash=document.access_hash,
            file_reference=document.file_reference,
            thumb_size=thumb or "",
        ),
        dc_id=document.dc_id,
        size=size,
        name=_filename(document),
    )


def _from_photo(photo: types.Photo, thumb: str | None) -> FileSource:
    chosen = _largest(photo.sizes) if thumb is None else _named(photo.sizes, thumb)
    return FileSource(
        location=types.InputPhotoFileLocation(
            id=photo.id,
            access_hash=photo.access_hash,
            file_reference=photo.file_reference,
            thumb_size=chosen.type,
        ),
        dc_id=photo.dc_id,
        size=_size_of(chosen),
        name=f"photo_{photo.id}.jpg",
    )


def _largest(sizes: list[Any]) -> Any:
    """The biggest rendition that is actually a file.

    Some of them are not: a stripped size is a couple of hundred bytes of
    preview carried inline, and a path size is an outline for a sticker. Asking
    the server for either is asking for something it does not have.
    """
    downloadable = [size for size in sizes if _size_of(size) or _is_fetchable(size)]
    if not downloadable:
        raise SunnygramError("this photo has no size that can be downloaded")
    return max(downloadable, key=_size_of)


def _named(sizes: list[Any], thumb: str) -> Any:
    for size in sizes:
        if getattr(size, "type", None) == thumb:
            return size
    available = ", ".join(sorted(str(getattr(s, "type", "?")) for s in sizes))
    raise SunnygramError(f"this photo has no size {thumb!r}. It has: {available}")


def _is_fetchable(size: Any) -> bool:
    return isinstance(size, (types.PhotoSize, types.PhotoSizeProgressive))


def _size_of(size: Any) -> int:
    if isinstance(size, types.PhotoSize):
        return size.size
    if isinstance(size, types.PhotoSizeProgressive):
        # Progressive JPEG, sent as a series of ever more detailed prefixes.
        # The last number is the whole thing.
        return max(size.sizes) if size.sizes else 0
    return 0


def _thumb_size(thumbs: list[Any], wanted: str) -> int:
    for size in thumbs:
        if getattr(size, "type", None) == wanted:
            return _size_of(size)
    return 0


def _filename(document: types.Document) -> str | None:
    for attribute in document.attributes:
        if isinstance(attribute, types.DocumentAttributeFilename):
            return attribute.file_name
    return None
