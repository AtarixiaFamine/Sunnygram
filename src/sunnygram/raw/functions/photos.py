# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the photos namespace.

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

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class UpdateProfilePhoto(TLFunction["base.photos.Photo"]):
    """The TL function photos.updateProfilePhoto#09e82039, answered with photos.Photo."""

    __slots__ = ("fallback", "bot", "id",)

    ID = 0x09E82039
    QUALNAME = "functions.photos.UpdateProfilePhoto"
    RESULT = "photos.Photo"

    def __init__(
        self,
        *,
        fallback: bool = False,
        bot: base.InputUser | None = None,
        id: base.InputPhoto,
    ) -> None:
        self.fallback = fallback
        self.bot = bot
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.fallback:
            flags |= 1 << 0
        if self.bot is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.bot is not None:
            self.bot.write(w)
        self.id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        fallback = bool(flags & (1 << 0))
        bot = r.read_object() if flags & (1 << 1) else None
        id = r.read_object()
        self = cls.__new__(cls)
        self.fallback = fallback
        self.bot = bot
        self.id = id
        return self


class UploadProfilePhoto(TLFunction["base.photos.Photo"]):
    """The TL function photos.uploadProfilePhoto#0388a3b5, answered with photos.Photo."""

    __slots__ = ("fallback", "bot", "file", "video", "video_start_ts", "video_emoji_markup",)

    ID = 0x0388A3B5
    QUALNAME = "functions.photos.UploadProfilePhoto"
    RESULT = "photos.Photo"

    def __init__(
        self,
        *,
        fallback: bool = False,
        bot: base.InputUser | None = None,
        file: base.InputFile | None = None,
        video: base.InputFile | None = None,
        video_start_ts: float | None = None,
        video_emoji_markup: base.VideoSize | None = None,
    ) -> None:
        self.fallback = fallback
        self.bot = bot
        self.file = file
        self.video = video
        self.video_start_ts = video_start_ts
        self.video_emoji_markup = video_emoji_markup

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.fallback:
            flags |= 1 << 3
        if self.bot is not None:
            flags |= 1 << 5
        if self.file is not None:
            flags |= 1 << 0
        if self.video is not None:
            flags |= 1 << 1
        if self.video_start_ts is not None:
            flags |= 1 << 2
        if self.video_emoji_markup is not None:
            flags |= 1 << 4
        w.write_int(flags)
        if self.bot is not None:
            self.bot.write(w)
        if self.file is not None:
            self.file.write(w)
        if self.video is not None:
            self.video.write(w)
        if self.video_start_ts is not None:
            w.write_double(self.video_start_ts)
        if self.video_emoji_markup is not None:
            self.video_emoji_markup.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        fallback = bool(flags & (1 << 3))
        bot = r.read_object() if flags & (1 << 5) else None
        file = r.read_object() if flags & (1 << 0) else None
        video = r.read_object() if flags & (1 << 1) else None
        video_start_ts = r.read_double() if flags & (1 << 2) else None
        video_emoji_markup = r.read_object() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.fallback = fallback
        self.bot = bot
        self.file = file
        self.video = video
        self.video_start_ts = video_start_ts
        self.video_emoji_markup = video_emoji_markup
        return self


class DeletePhotos(TLFunction["list[int]"]):
    """The TL function photos.deletePhotos#87cf7f2f, answered with Vector<long>."""

    __slots__ = ("id",)

    ID = 0x87CF7F2F
    QUALNAME = "functions.photos.DeletePhotos"
    RESULT = "Vector<long>"

    def __init__(
        self,
        *,
        id: list[base.InputPhoto],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector()
        self = cls.__new__(cls)
        self.id = id
        return self


class GetUserPhotos(TLFunction["base.photos.Photos"]):
    """The TL function photos.getUserPhotos#91cd32a8, answered with photos.Photos."""

    __slots__ = ("user_id", "offset", "max_id", "limit",)

    ID = 0x91CD32A8
    QUALNAME = "functions.photos.GetUserPhotos"
    RESULT = "photos.Photos"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        offset: int,
        max_id: int,
        limit: int,
    ) -> None:
        self.user_id = user_id
        self.offset = offset
        self.max_id = max_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_int(self.offset)
        w.write_long(self.max_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        offset = r.read_int()
        max_id = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.offset = offset
        self.max_id = max_id
        self.limit = limit
        return self


class UploadContactProfilePhoto(TLFunction["base.photos.Photo"]):
    """The TL function photos.uploadContactProfilePhoto#e14c4a71, answered with photos.Photo."""

    __slots__ = ("suggest", "save", "user_id", "file", "video", "video_start_ts", "video_emoji_markup",)

    ID = 0xE14C4A71
    QUALNAME = "functions.photos.UploadContactProfilePhoto"
    RESULT = "photos.Photo"

    def __init__(
        self,
        *,
        suggest: bool = False,
        save: bool = False,
        user_id: base.InputUser,
        file: base.InputFile | None = None,
        video: base.InputFile | None = None,
        video_start_ts: float | None = None,
        video_emoji_markup: base.VideoSize | None = None,
    ) -> None:
        self.suggest = suggest
        self.save = save
        self.user_id = user_id
        self.file = file
        self.video = video
        self.video_start_ts = video_start_ts
        self.video_emoji_markup = video_emoji_markup

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.suggest:
            flags |= 1 << 3
        if self.save:
            flags |= 1 << 4
        if self.file is not None:
            flags |= 1 << 0
        if self.video is not None:
            flags |= 1 << 1
        if self.video_start_ts is not None:
            flags |= 1 << 2
        if self.video_emoji_markup is not None:
            flags |= 1 << 5
        w.write_int(flags)
        self.user_id.write(w)
        if self.file is not None:
            self.file.write(w)
        if self.video is not None:
            self.video.write(w)
        if self.video_start_ts is not None:
            w.write_double(self.video_start_ts)
        if self.video_emoji_markup is not None:
            self.video_emoji_markup.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        suggest = bool(flags & (1 << 3))
        save = bool(flags & (1 << 4))
        user_id = r.read_object()
        file = r.read_object() if flags & (1 << 0) else None
        video = r.read_object() if flags & (1 << 1) else None
        video_start_ts = r.read_double() if flags & (1 << 2) else None
        video_emoji_markup = r.read_object() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.suggest = suggest
        self.save = save
        self.user_id = user_id
        self.file = file
        self.video = video
        self.video_start_ts = video_start_ts
        self.video_emoji_markup = video_emoji_markup
        return self
