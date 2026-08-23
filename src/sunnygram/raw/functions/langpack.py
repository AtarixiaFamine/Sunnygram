# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the langpack namespace.

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
    from .. import base  # noqa: F401


class GetLangPack(TLFunction["base.LangPackDifference"]):
    """The TL function langpack.getLangPack#f2f2330a, answered with LangPackDifference."""

    __slots__ = ("lang_pack", "lang_code",)

    ID = 0xF2F2330A
    QUALNAME = "functions.langpack.GetLangPack"
    RESULT = "LangPackDifference"

    def __init__(
        self,
        *,
        lang_pack: str,
        lang_code: str,
    ) -> None:
        self.lang_pack = lang_pack
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_pack)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_pack = r.read_string()
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        return self


class GetStrings(TLFunction["list[base.LangPackString]"]):
    """The TL function langpack.getStrings#efea3803, answered with Vector<LangPackString>."""

    __slots__ = ("lang_pack", "lang_code", "keys",)

    ID = 0xEFEA3803
    QUALNAME = "functions.langpack.GetStrings"
    RESULT = "Vector<LangPackString>"

    def __init__(
        self,
        *,
        lang_pack: str,
        lang_code: str,
        keys: list[str],
    ) -> None:
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.keys = keys

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_pack)
        w.write_string(self.lang_code)
        w.write_vector(self.keys, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_pack = r.read_string()
        lang_code = r.read_string()
        keys = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.keys = keys
        return self


class GetDifference(TLFunction["base.LangPackDifference"]):
    """The TL function langpack.getDifference#cd984aa5, answered with LangPackDifference."""

    __slots__ = ("lang_pack", "lang_code", "from_version",)

    ID = 0xCD984AA5
    QUALNAME = "functions.langpack.GetDifference"
    RESULT = "LangPackDifference"

    def __init__(
        self,
        *,
        lang_pack: str,
        lang_code: str,
        from_version: int,
    ) -> None:
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.from_version = from_version

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_pack)
        w.write_string(self.lang_code)
        w.write_int(self.from_version)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_pack = r.read_string()
        lang_code = r.read_string()
        from_version = r.read_int()
        self = cls.__new__(cls)
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.from_version = from_version
        return self


class GetLanguages(TLFunction["list[base.LangPackLanguage]"]):
    """The TL function langpack.getLanguages#42c6978f, answered with Vector<LangPackLanguage>."""

    __slots__ = ("lang_pack",)

    ID = 0x42C6978F
    QUALNAME = "functions.langpack.GetLanguages"
    RESULT = "Vector<LangPackLanguage>"

    def __init__(
        self,
        *,
        lang_pack: str,
    ) -> None:
        self.lang_pack = lang_pack

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_pack)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_pack = r.read_string()
        self = cls.__new__(cls)
        self.lang_pack = lang_pack
        return self


class GetLanguage(TLFunction["base.LangPackLanguage"]):
    """The TL function langpack.getLanguage#6a596502, answered with LangPackLanguage."""

    __slots__ = ("lang_pack", "lang_code",)

    ID = 0x6A596502
    QUALNAME = "functions.langpack.GetLanguage"
    RESULT = "LangPackLanguage"

    def __init__(
        self,
        *,
        lang_pack: str,
        lang_code: str,
    ) -> None:
        self.lang_pack = lang_pack
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_pack)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_pack = r.read_string()
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        return self
