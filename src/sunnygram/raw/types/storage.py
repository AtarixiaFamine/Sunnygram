# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the storage namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import Self

from ...tl import TLObject, TLReader, TLWriter


class FileUnknown(TLObject):
    """The TL type storage.fileUnknown#aa963b05, a form of storage.FileType."""

    __slots__ = ()

    ID = 0xAA963B05
    QUALNAME = "types.storage.FileUnknown"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FilePartial(TLObject):
    """The TL type storage.filePartial#40bc6f52, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x40BC6F52
    QUALNAME = "types.storage.FilePartial"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileJpeg(TLObject):
    """The TL type storage.fileJpeg#007efe0e, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x007EFE0E
    QUALNAME = "types.storage.FileJpeg"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileGif(TLObject):
    """The TL type storage.fileGif#cae1aadf, a form of storage.FileType."""

    __slots__ = ()

    ID = 0xCAE1AADF
    QUALNAME = "types.storage.FileGif"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FilePng(TLObject):
    """The TL type storage.filePng#0a4f63c0, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x0A4F63C0
    QUALNAME = "types.storage.FilePng"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FilePdf(TLObject):
    """The TL type storage.filePdf#ae1e508d, a form of storage.FileType."""

    __slots__ = ()

    ID = 0xAE1E508D
    QUALNAME = "types.storage.FilePdf"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileMp3(TLObject):
    """The TL type storage.fileMp3#528a0677, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x528A0677
    QUALNAME = "types.storage.FileMp3"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileMov(TLObject):
    """The TL type storage.fileMov#4b09ebbc, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x4B09EBBC
    QUALNAME = "types.storage.FileMov"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileMp4(TLObject):
    """The TL type storage.fileMp4#b3cea0e4, a form of storage.FileType."""

    __slots__ = ()

    ID = 0xB3CEA0E4
    QUALNAME = "types.storage.FileMp4"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FileWebp(TLObject):
    """The TL type storage.fileWebp#1081464c, a form of storage.FileType."""

    __slots__ = ()

    ID = 0x1081464C
    QUALNAME = "types.storage.FileWebp"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self
