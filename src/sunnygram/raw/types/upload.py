# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the upload namespace.

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


class File(TLObject):
    """The TL type upload.file#096a18d5, a form of upload.File."""

    __slots__ = ("type", "mtime", "bytes",)

    ID = 0x096A18D5
    QUALNAME = "types.upload.File"

    def __init__(
        self,
        *,
        type: base.storage.FileType,
        mtime: int,
        bytes: bytes,
    ) -> None:
        self.type = type
        self.mtime = mtime
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        self.type.write(w)
        w.write_int(self.mtime)
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        type = r.read_object()
        mtime = r.read_int()
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.type = type
        self.mtime = mtime
        self.bytes = bytes
        return self


class FileCdnRedirect(TLObject):
    """The TL type upload.fileCdnRedirect#f18cda44, a form of upload.File."""

    __slots__ = ("dc_id", "file_token", "encryption_key", "encryption_iv", "file_hashes",)

    ID = 0xF18CDA44
    QUALNAME = "types.upload.FileCdnRedirect"

    def __init__(
        self,
        *,
        dc_id: int,
        file_token: bytes,
        encryption_key: bytes,
        encryption_iv: bytes,
        file_hashes: list[base.FileHash],
    ) -> None:
        self.dc_id = dc_id
        self.file_token = file_token
        self.encryption_key = encryption_key
        self.encryption_iv = encryption_iv
        self.file_hashes = file_hashes

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.dc_id)
        w.write_bytes(self.file_token)
        w.write_bytes(self.encryption_key)
        w.write_bytes(self.encryption_iv)
        w.write_vector(self.file_hashes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dc_id = r.read_int()
        file_token = r.read_bytes()
        encryption_key = r.read_bytes()
        encryption_iv = r.read_bytes()
        file_hashes = r.read_vector()
        self = cls.__new__(cls)
        self.dc_id = dc_id
        self.file_token = file_token
        self.encryption_key = encryption_key
        self.encryption_iv = encryption_iv
        self.file_hashes = file_hashes
        return self


class WebFile(TLObject):
    """The TL type upload.webFile#21e753bc, a form of upload.WebFile."""

    __slots__ = ("size", "mime_type", "file_type", "mtime", "bytes",)

    ID = 0x21E753BC
    QUALNAME = "types.upload.WebFile"

    def __init__(
        self,
        *,
        size: int,
        mime_type: str,
        file_type: base.storage.FileType,
        mtime: int,
        bytes: bytes,
    ) -> None:
        self.size = size
        self.mime_type = mime_type
        self.file_type = file_type
        self.mtime = mtime
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.size)
        w.write_string(self.mime_type)
        self.file_type.write(w)
        w.write_int(self.mtime)
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        size = r.read_int()
        mime_type = r.read_string()
        file_type = r.read_object()
        mtime = r.read_int()
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.size = size
        self.mime_type = mime_type
        self.file_type = file_type
        self.mtime = mtime
        self.bytes = bytes
        return self


class CdnFileReuploadNeeded(TLObject):
    """The TL type upload.cdnFileReuploadNeeded#eea8e46e, a form of upload.CdnFile."""

    __slots__ = ("request_token",)

    ID = 0xEEA8E46E
    QUALNAME = "types.upload.CdnFileReuploadNeeded"

    def __init__(
        self,
        *,
        request_token: bytes,
    ) -> None:
        self.request_token = request_token

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.request_token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        request_token = r.read_bytes()
        self = cls.__new__(cls)
        self.request_token = request_token
        return self


class CdnFile(TLObject):
    """The TL type upload.cdnFile#a99fca4f, a form of upload.CdnFile."""

    __slots__ = ("bytes",)

    ID = 0xA99FCA4F
    QUALNAME = "types.upload.CdnFile"

    def __init__(
        self,
        *,
        bytes: bytes,
    ) -> None:
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.bytes = bytes
        return self
