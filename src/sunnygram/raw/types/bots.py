# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the bots namespace.

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


class BotInfo(TLObject):
    """The TL type bots.botInfo#e8a775b0, a form of bots.BotInfo."""

    __slots__ = ("name", "about", "description",)

    ID = 0xE8A775B0
    QUALNAME = "types.bots.BotInfo"

    def __init__(
        self,
        *,
        name: str,
        about: str,
        description: str,
    ) -> None:
        self.name = name
        self.about = about
        self.description = description

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.name)
        w.write_string(self.about)
        w.write_string(self.description)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        name = r.read_string()
        about = r.read_string()
        description = r.read_string()
        self = cls.__new__(cls)
        self.name = name
        self.about = about
        self.description = description
        return self


class PopularAppBots(TLObject):
    """The TL type bots.popularAppBots#1991b13b, a form of bots.PopularAppBots."""

    __slots__ = ("next_offset", "users",)

    ID = 0x1991B13B
    QUALNAME = "types.bots.PopularAppBots"

    def __init__(
        self,
        *,
        next_offset: str | None = None,
        users: list[base.User],
    ) -> None:
        self.next_offset = next_offset
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        next_offset = r.read_string() if flags & (1 << 0) else None
        users = r.read_vector()
        self = cls.__new__(cls)
        self.next_offset = next_offset
        self.users = users
        return self


class PreviewInfo(TLObject):
    """The TL type bots.previewInfo#0ca71d64, a form of bots.PreviewInfo."""

    __slots__ = ("media", "lang_codes",)

    ID = 0x0CA71D64
    QUALNAME = "types.bots.PreviewInfo"

    def __init__(
        self,
        *,
        media: list[base.BotPreviewMedia],
        lang_codes: list[str],
    ) -> None:
        self.media = media
        self.lang_codes = lang_codes

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.media)
        w.write_vector(self.lang_codes, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        media = r.read_vector()
        lang_codes = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.media = media
        self.lang_codes = lang_codes
        return self


class ExportedBotToken(TLObject):
    """The TL type bots.exportedBotToken#3c60b621, a form of bots.ExportedBotToken."""

    __slots__ = ("token",)

    ID = 0x3C60B621
    QUALNAME = "types.bots.ExportedBotToken"

    def __init__(
        self,
        *,
        token: str,
    ) -> None:
        self.token = token

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        token = r.read_string()
        self = cls.__new__(cls)
        self.token = token
        return self


class RequestedButton(TLObject):
    """The TL type bots.requestedButton#f13bbcd7, a form of bots.RequestedButton."""

    __slots__ = ("webapp_req_id",)

    ID = 0xF13BBCD7
    QUALNAME = "types.bots.RequestedButton"

    def __init__(
        self,
        *,
        webapp_req_id: str,
    ) -> None:
        self.webapp_req_id = webapp_req_id

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.webapp_req_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        webapp_req_id = r.read_string()
        self = cls.__new__(cls)
        self.webapp_req_id = webapp_req_id
        return self


class AccessSettings(TLObject):
    """The TL type bots.accessSettings#dd1fbf93, a form of bots.AccessSettings."""

    __slots__ = ("restricted", "add_users",)

    ID = 0xDD1FBF93
    QUALNAME = "types.bots.AccessSettings"

    def __init__(
        self,
        *,
        restricted: bool = False,
        add_users: list[base.User] | None = None,
    ) -> None:
        self.restricted = restricted
        self.add_users = add_users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.restricted:
            flags |= 1 << 0
        if self.add_users is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.add_users is not None:
            w.write_vector(self.add_users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        restricted = bool(flags & (1 << 0))
        add_users = r.read_vector() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.restricted = restricted
        self.add_users = add_users
        return self
