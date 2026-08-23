# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the aicompose namespace.

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


class CreateTone(TLFunction["base.AiComposeTone"]):
    """The TL function aicompose.createTone#4aa83913, answered with AiComposeTone."""

    __slots__ = ("display_author", "emoji_id", "title", "prompt",)

    ID = 0x4AA83913
    QUALNAME = "functions.aicompose.CreateTone"
    RESULT = "AiComposeTone"

    def __init__(
        self,
        *,
        display_author: bool = False,
        emoji_id: int,
        title: str,
        prompt: str,
    ) -> None:
        self.display_author = display_author
        self.emoji_id = emoji_id
        self.title = title
        self.prompt = prompt

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.display_author:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.emoji_id)
        w.write_string(self.title)
        w.write_string(self.prompt)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        display_author = bool(flags & (1 << 0))
        emoji_id = r.read_long()
        title = r.read_string()
        prompt = r.read_string()
        self = cls.__new__(cls)
        self.display_author = display_author
        self.emoji_id = emoji_id
        self.title = title
        self.prompt = prompt
        return self


class UpdateTone(TLFunction["base.AiComposeTone"]):
    """The TL function aicompose.updateTone#903bcf59, answered with AiComposeTone."""

    __slots__ = ("tone", "display_author", "emoji_id", "title", "prompt",)

    ID = 0x903BCF59
    QUALNAME = "functions.aicompose.UpdateTone"
    RESULT = "AiComposeTone"

    def __init__(
        self,
        *,
        tone: base.InputAiComposeTone,
        display_author: bool | None = None,
        emoji_id: int | None = None,
        title: str | None = None,
        prompt: str | None = None,
    ) -> None:
        self.tone = tone
        self.display_author = display_author
        self.emoji_id = emoji_id
        self.title = title
        self.prompt = prompt

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.display_author is not None:
            flags |= 1 << 0
        if self.emoji_id is not None:
            flags |= 1 << 1
        if self.title is not None:
            flags |= 1 << 2
        if self.prompt is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.tone.write(w)
        if self.display_author is not None:
            w.write_bool(self.display_author)
        if self.emoji_id is not None:
            w.write_long(self.emoji_id)
        if self.title is not None:
            w.write_string(self.title)
        if self.prompt is not None:
            w.write_string(self.prompt)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        tone = r.read_object()
        display_author = r.read_bool() if flags & (1 << 0) else None
        emoji_id = r.read_long() if flags & (1 << 1) else None
        title = r.read_string() if flags & (1 << 2) else None
        prompt = r.read_string() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.tone = tone
        self.display_author = display_author
        self.emoji_id = emoji_id
        self.title = title
        self.prompt = prompt
        return self


class SaveTone(TLFunction["bool"]):
    """The TL function aicompose.saveTone#1782cbb1, answered with Bool."""

    __slots__ = ("tone", "unsave",)

    ID = 0x1782CBB1
    QUALNAME = "functions.aicompose.SaveTone"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        tone: base.InputAiComposeTone,
        unsave: bool,
    ) -> None:
        self.tone = tone
        self.unsave = unsave

    def write_body(self, w: TLWriter) -> None:
        self.tone.write(w)
        w.write_bool(self.unsave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tone = r.read_object()
        unsave = r.read_bool()
        self = cls.__new__(cls)
        self.tone = tone
        self.unsave = unsave
        return self


class DeleteTone(TLFunction["bool"]):
    """The TL function aicompose.deleteTone#dd39316a, answered with Bool."""

    __slots__ = ("tone",)

    ID = 0xDD39316A
    QUALNAME = "functions.aicompose.DeleteTone"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        tone: base.InputAiComposeTone,
    ) -> None:
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        self.tone.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tone = r.read_object()
        self = cls.__new__(cls)
        self.tone = tone
        return self


class GetTone(TLFunction["base.aicompose.Tones"]):
    """The TL function aicompose.getTone#b2e8ba03, answered with aicompose.Tones."""

    __slots__ = ("tone",)

    ID = 0xB2E8BA03
    QUALNAME = "functions.aicompose.GetTone"
    RESULT = "aicompose.Tones"

    def __init__(
        self,
        *,
        tone: base.InputAiComposeTone,
    ) -> None:
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        self.tone.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tone = r.read_object()
        self = cls.__new__(cls)
        self.tone = tone
        return self


class GetTones(TLFunction["base.aicompose.Tones"]):
    """The TL function aicompose.getTones#abd59201, answered with aicompose.Tones."""

    __slots__ = ("hash",)

    ID = 0xABD59201
    QUALNAME = "functions.aicompose.GetTones"
    RESULT = "aicompose.Tones"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetToneExample(TLFunction["base.AiComposeToneExample"]):
    """The TL function aicompose.getToneExample#d1b4ab14, answered with AiComposeToneExample."""

    __slots__ = ("tone", "num",)

    ID = 0xD1B4AB14
    QUALNAME = "functions.aicompose.GetToneExample"
    RESULT = "AiComposeToneExample"

    def __init__(
        self,
        *,
        tone: base.InputAiComposeTone,
        num: int,
    ) -> None:
        self.tone = tone
        self.num = num

    def write_body(self, w: TLWriter) -> None:
        self.tone.write(w)
        w.write_int(self.num)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tone = r.read_object()
        num = r.read_int()
        self = cls.__new__(cls)
        self.tone = tone
        self.num = num
        return self
