# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the upload namespace.

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


class SaveFilePart(TLFunction["bool"]):
    """The TL function upload.saveFilePart#b304a621, answered with Bool."""

    __slots__ = ("file_id", "file_part", "bytes",)

    ID = 0xB304A621
    QUALNAME = "functions.upload.SaveFilePart"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        file_id: int,
        file_part: int,
        bytes: bytes,
    ) -> None:
        self.file_id = file_id
        self.file_part = file_part
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.file_id)
        w.write_int(self.file_part)
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file_id = r.read_long()
        file_part = r.read_int()
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.file_id = file_id
        self.file_part = file_part
        self.bytes = bytes
        return self


class GetFile(TLFunction["base.upload.File"]):
    """The TL function upload.getFile#be5335be, answered with upload.File."""

    __slots__ = ("precise", "cdn_supported", "location", "offset", "limit",)

    ID = 0xBE5335BE
    QUALNAME = "functions.upload.GetFile"
    RESULT = "upload.File"

    def __init__(
        self,
        *,
        precise: bool = False,
        cdn_supported: bool = False,
        location: base.InputFileLocation,
        offset: int,
        limit: int,
    ) -> None:
        self.precise = precise
        self.cdn_supported = cdn_supported
        self.location = location
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.precise:
            flags |= 1 << 0
        if self.cdn_supported:
            flags |= 1 << 1
        w.write_int(flags)
        self.location.write(w)
        w.write_long(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        precise = bool(flags & (1 << 0))
        cdn_supported = bool(flags & (1 << 1))
        location = r.read_object()
        offset = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.precise = precise
        self.cdn_supported = cdn_supported
        self.location = location
        self.offset = offset
        self.limit = limit
        return self


class SaveBigFilePart(TLFunction["bool"]):
    """The TL function upload.saveBigFilePart#de7b673d, answered with Bool."""

    __slots__ = ("file_id", "file_part", "file_total_parts", "bytes",)

    ID = 0xDE7B673D
    QUALNAME = "functions.upload.SaveBigFilePart"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        file_id: int,
        file_part: int,
        file_total_parts: int,
        bytes: bytes,
    ) -> None:
        self.file_id = file_id
        self.file_part = file_part
        self.file_total_parts = file_total_parts
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.file_id)
        w.write_int(self.file_part)
        w.write_int(self.file_total_parts)
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file_id = r.read_long()
        file_part = r.read_int()
        file_total_parts = r.read_int()
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.file_id = file_id
        self.file_part = file_part
        self.file_total_parts = file_total_parts
        self.bytes = bytes
        return self


class GetWebFile(TLFunction["base.upload.WebFile"]):
    """The TL function upload.getWebFile#24e6818d, answered with upload.WebFile."""

    __slots__ = ("location", "offset", "limit",)

    ID = 0x24E6818D
    QUALNAME = "functions.upload.GetWebFile"
    RESULT = "upload.WebFile"

    def __init__(
        self,
        *,
        location: base.InputWebFileLocation,
        offset: int,
        limit: int,
    ) -> None:
        self.location = location
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.location.write(w)
        w.write_int(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        location = r.read_object()
        offset = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.location = location
        self.offset = offset
        self.limit = limit
        return self


class GetCdnFile(TLFunction["base.upload.CdnFile"]):
    """The TL function upload.getCdnFile#395f69da, answered with upload.CdnFile."""

    __slots__ = ("file_token", "offset", "limit",)

    ID = 0x395F69DA
    QUALNAME = "functions.upload.GetCdnFile"
    RESULT = "upload.CdnFile"

    def __init__(
        self,
        *,
        file_token: bytes,
        offset: int,
        limit: int,
    ) -> None:
        self.file_token = file_token
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.file_token)
        w.write_long(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file_token = r.read_bytes()
        offset = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.file_token = file_token
        self.offset = offset
        self.limit = limit
        return self


class ReuploadCdnFile(TLFunction["list[base.FileHash]"]):
    """The TL function upload.reuploadCdnFile#9b2754a8, answered with Vector<FileHash>."""

    __slots__ = ("file_token", "request_token",)

    ID = 0x9B2754A8
    QUALNAME = "functions.upload.ReuploadCdnFile"
    RESULT = "Vector<FileHash>"

    def __init__(
        self,
        *,
        file_token: bytes,
        request_token: bytes,
    ) -> None:
        self.file_token = file_token
        self.request_token = request_token

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.file_token)
        w.write_bytes(self.request_token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file_token = r.read_bytes()
        request_token = r.read_bytes()
        self = cls.__new__(cls)
        self.file_token = file_token
        self.request_token = request_token
        return self


class GetCdnFileHashes(TLFunction["list[base.FileHash]"]):
    """The TL function upload.getCdnFileHashes#91dc3f31, answered with Vector<FileHash>."""

    __slots__ = ("file_token", "offset",)

    ID = 0x91DC3F31
    QUALNAME = "functions.upload.GetCdnFileHashes"
    RESULT = "Vector<FileHash>"

    def __init__(
        self,
        *,
        file_token: bytes,
        offset: int,
    ) -> None:
        self.file_token = file_token
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.file_token)
        w.write_long(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file_token = r.read_bytes()
        offset = r.read_long()
        self = cls.__new__(cls)
        self.file_token = file_token
        self.offset = offset
        return self


class GetFileHashes(TLFunction["list[base.FileHash]"]):
    """The TL function upload.getFileHashes#9156982a, answered with Vector<FileHash>."""

    __slots__ = ("location", "offset",)

    ID = 0x9156982A
    QUALNAME = "functions.upload.GetFileHashes"
    RESULT = "Vector<FileHash>"

    def __init__(
        self,
        *,
        location: base.InputFileLocation,
        offset: int,
    ) -> None:
        self.location = location
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        self.location.write(w)
        w.write_long(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        location = r.read_object()
        offset = r.read_long()
        self = cls.__new__(cls)
        self.location = location
        self.offset = offset
        return self
