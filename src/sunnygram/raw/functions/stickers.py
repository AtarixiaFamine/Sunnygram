# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the stickers namespace.

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


class CreateStickerSet(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.createStickerSet#9021ab67, answered with messages.StickerSet."""

    __slots__ = ("masks", "emojis", "text_color", "user_id", "title", "short_name", "thumb", "stickers", "software",)

    ID = 0x9021AB67
    QUALNAME = "functions.stickers.CreateStickerSet"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        masks: bool = False,
        emojis: bool = False,
        text_color: bool = False,
        user_id: base.InputUser,
        title: str,
        short_name: str,
        thumb: base.InputDocument | None = None,
        stickers: list[base.InputStickerSetItem],
        software: str | None = None,
    ) -> None:
        self.masks = masks
        self.emojis = emojis
        self.text_color = text_color
        self.user_id = user_id
        self.title = title
        self.short_name = short_name
        self.thumb = thumb
        self.stickers = stickers
        self.software = software

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.masks:
            flags |= 1 << 0
        if self.emojis:
            flags |= 1 << 5
        if self.text_color:
            flags |= 1 << 6
        if self.thumb is not None:
            flags |= 1 << 2
        if self.software is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.user_id.write(w)
        w.write_string(self.title)
        w.write_string(self.short_name)
        if self.thumb is not None:
            self.thumb.write(w)
        w.write_vector(self.stickers)
        if self.software is not None:
            w.write_string(self.software)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        masks = bool(flags & (1 << 0))
        emojis = bool(flags & (1 << 5))
        text_color = bool(flags & (1 << 6))
        user_id = r.read_object()
        title = r.read_string()
        short_name = r.read_string()
        thumb = r.read_object() if flags & (1 << 2) else None
        stickers = r.read_vector()
        software = r.read_string() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.masks = masks
        self.emojis = emojis
        self.text_color = text_color
        self.user_id = user_id
        self.title = title
        self.short_name = short_name
        self.thumb = thumb
        self.stickers = stickers
        self.software = software
        return self


class RemoveStickerFromSet(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.removeStickerFromSet#f7760f51, answered with messages.StickerSet."""

    __slots__ = ("sticker",)

    ID = 0xF7760F51
    QUALNAME = "functions.stickers.RemoveStickerFromSet"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        sticker: base.InputDocument,
    ) -> None:
        self.sticker = sticker

    def write_body(self, w: TLWriter) -> None:
        self.sticker.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sticker = r.read_object()
        self = cls.__new__(cls)
        self.sticker = sticker
        return self


class ChangeStickerPosition(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.changeStickerPosition#ffb6d4ca, answered with messages.StickerSet."""

    __slots__ = ("sticker", "position",)

    ID = 0xFFB6D4CA
    QUALNAME = "functions.stickers.ChangeStickerPosition"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        sticker: base.InputDocument,
        position: int,
    ) -> None:
        self.sticker = sticker
        self.position = position

    def write_body(self, w: TLWriter) -> None:
        self.sticker.write(w)
        w.write_int(self.position)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sticker = r.read_object()
        position = r.read_int()
        self = cls.__new__(cls)
        self.sticker = sticker
        self.position = position
        return self


class AddStickerToSet(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.addStickerToSet#8653febe, answered with messages.StickerSet."""

    __slots__ = ("stickerset", "sticker",)

    ID = 0x8653FEBE
    QUALNAME = "functions.stickers.AddStickerToSet"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
        sticker: base.InputStickerSetItem,
    ) -> None:
        self.stickerset = stickerset
        self.sticker = sticker

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)
        self.sticker.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        sticker = r.read_object()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        self.sticker = sticker
        return self


class SetStickerSetThumb(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.setStickerSetThumb#a76a5392, answered with messages.StickerSet."""

    __slots__ = ("stickerset", "thumb", "thumb_document_id",)

    ID = 0xA76A5392
    QUALNAME = "functions.stickers.SetStickerSetThumb"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
        thumb: base.InputDocument | None = None,
        thumb_document_id: int | None = None,
    ) -> None:
        self.stickerset = stickerset
        self.thumb = thumb
        self.thumb_document_id = thumb_document_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.thumb is not None:
            flags |= 1 << 0
        if self.thumb_document_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.stickerset.write(w)
        if self.thumb is not None:
            self.thumb.write(w)
        if self.thumb_document_id is not None:
            w.write_long(self.thumb_document_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        stickerset = r.read_object()
        thumb = r.read_object() if flags & (1 << 0) else None
        thumb_document_id = r.read_long() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.stickerset = stickerset
        self.thumb = thumb
        self.thumb_document_id = thumb_document_id
        return self


class CheckShortName(TLFunction["bool"]):
    """The TL function stickers.checkShortName#284b3639, answered with Bool."""

    __slots__ = ("short_name",)

    ID = 0x284B3639
    QUALNAME = "functions.stickers.CheckShortName"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        short_name: str,
    ) -> None:
        self.short_name = short_name

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.short_name)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        short_name = r.read_string()
        self = cls.__new__(cls)
        self.short_name = short_name
        return self


class SuggestShortName(TLFunction["base.stickers.SuggestedShortName"]):
    """The TL function stickers.suggestShortName#4dafc503, answered with stickers.SuggestedShortName."""

    __slots__ = ("title",)

    ID = 0x4DAFC503
    QUALNAME = "functions.stickers.SuggestShortName"
    RESULT = "stickers.SuggestedShortName"

    def __init__(
        self,
        *,
        title: str,
    ) -> None:
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        title = r.read_string()
        self = cls.__new__(cls)
        self.title = title
        return self


class ChangeSticker(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.changeSticker#f5537ebc, answered with messages.StickerSet."""

    __slots__ = ("sticker", "emoji", "mask_coords", "keywords",)

    ID = 0xF5537EBC
    QUALNAME = "functions.stickers.ChangeSticker"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        sticker: base.InputDocument,
        emoji: str | None = None,
        mask_coords: base.MaskCoords | None = None,
        keywords: str | None = None,
    ) -> None:
        self.sticker = sticker
        self.emoji = emoji
        self.mask_coords = mask_coords
        self.keywords = keywords

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.emoji is not None:
            flags |= 1 << 0
        if self.mask_coords is not None:
            flags |= 1 << 1
        if self.keywords is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.sticker.write(w)
        if self.emoji is not None:
            w.write_string(self.emoji)
        if self.mask_coords is not None:
            self.mask_coords.write(w)
        if self.keywords is not None:
            w.write_string(self.keywords)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        sticker = r.read_object()
        emoji = r.read_string() if flags & (1 << 0) else None
        mask_coords = r.read_object() if flags & (1 << 1) else None
        keywords = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.sticker = sticker
        self.emoji = emoji
        self.mask_coords = mask_coords
        self.keywords = keywords
        return self


class RenameStickerSet(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.renameStickerSet#124b1c00, answered with messages.StickerSet."""

    __slots__ = ("stickerset", "title",)

    ID = 0x124B1C00
    QUALNAME = "functions.stickers.RenameStickerSet"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
        title: str,
    ) -> None:
        self.stickerset = stickerset
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)
        w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        title = r.read_string()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        self.title = title
        return self


class DeleteStickerSet(TLFunction["bool"]):
    """The TL function stickers.deleteStickerSet#87704394, answered with Bool."""

    __slots__ = ("stickerset",)

    ID = 0x87704394
    QUALNAME = "functions.stickers.DeleteStickerSet"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
    ) -> None:
        self.stickerset = stickerset

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        return self


class ReplaceSticker(TLFunction["base.messages.StickerSet"]):
    """The TL function stickers.replaceSticker#4696459a, answered with messages.StickerSet."""

    __slots__ = ("sticker", "new_sticker",)

    ID = 0x4696459A
    QUALNAME = "functions.stickers.ReplaceSticker"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        sticker: base.InputDocument,
        new_sticker: base.InputStickerSetItem,
    ) -> None:
        self.sticker = sticker
        self.new_sticker = new_sticker

    def write_body(self, w: TLWriter) -> None:
        self.sticker.write(w)
        self.new_sticker.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sticker = r.read_object()
        new_sticker = r.read_object()
        self = cls.__new__(cls)
        self.sticker = sticker
        self.new_sticker = new_sticker
        return self
