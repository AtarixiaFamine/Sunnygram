# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the photos namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class Photos(TLObject):
    """The TL type photos.photos#8dca6aa5, a form of photos.Photos."""

    __slots__ = ("photos", "users",)

    ID = 0x8DCA6AA5
    QUALNAME = "types.photos.Photos"

    def __init__(
        self,
        *,
        photos: list[base.Photo],
        users: list[base.User],
    ) -> None:
        self.photos = photos
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.photos)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        photos = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.photos = photos
        self.users = users
        return self


class PhotosSlice(TLObject):
    """The TL type photos.photosSlice#15051f54, a form of photos.Photos."""

    __slots__ = ("count", "photos", "users",)

    ID = 0x15051F54
    QUALNAME = "types.photos.PhotosSlice"

    def __init__(
        self,
        *,
        count: int,
        photos: list[base.Photo],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.photos = photos
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.photos)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        photos = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.photos = photos
        self.users = users
        return self


class Photo(TLObject):
    """The TL type photos.photo#20212ca8, a form of photos.Photo."""

    __slots__ = ("photo", "users",)

    ID = 0x20212CA8
    QUALNAME = "types.photos.Photo"

    def __init__(
        self,
        *,
        photo: base.Photo,
        users: list[base.User],
    ) -> None:
        self.photo = photo
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.photo.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        photo = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.photo = photo
        self.users = users
        return self
