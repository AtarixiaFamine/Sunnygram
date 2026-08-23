# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the users namespace.

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


class GetUsers(TLFunction["list[base.User]"]):
    """The TL function users.getUsers#0d91a548, answered with Vector<User>."""

    __slots__ = ("id",)

    ID = 0x0D91A548
    QUALNAME = "functions.users.GetUsers"
    RESULT = "Vector<User>"

    def __init__(
        self,
        *,
        id: list[base.InputUser],
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


class GetFullUser(TLFunction["base.users.UserFull"]):
    """The TL function users.getFullUser#b60f5918, answered with users.UserFull."""

    __slots__ = ("id",)

    ID = 0xB60F5918
    QUALNAME = "functions.users.GetFullUser"
    RESULT = "users.UserFull"

    def __init__(
        self,
        *,
        id: base.InputUser,
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        self = cls.__new__(cls)
        self.id = id
        return self


class SetSecureValueErrors(TLFunction["bool"]):
    """The TL function users.setSecureValueErrors#90c894b5, answered with Bool."""

    __slots__ = ("id", "errors",)

    ID = 0x90C894B5
    QUALNAME = "functions.users.SetSecureValueErrors"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.InputUser,
        errors: list[base.SecureValueError],
    ) -> None:
        self.id = id
        self.errors = errors

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_vector(self.errors)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        errors = r.read_vector()
        self = cls.__new__(cls)
        self.id = id
        self.errors = errors
        return self


class GetRequirementsToContact(TLFunction["list[base.RequirementToContact]"]):
    """The TL function users.getRequirementsToContact#d89a83a3, answered with Vector<RequirementToContact>."""

    __slots__ = ("id",)

    ID = 0xD89A83A3
    QUALNAME = "functions.users.GetRequirementsToContact"
    RESULT = "Vector<RequirementToContact>"

    def __init__(
        self,
        *,
        id: list[base.InputUser],
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


class GetSavedMusic(TLFunction["base.users.SavedMusic"]):
    """The TL function users.getSavedMusic#788d7fe3, answered with users.SavedMusic."""

    __slots__ = ("id", "offset", "limit", "hash",)

    ID = 0x788D7FE3
    QUALNAME = "functions.users.GetSavedMusic"
    RESULT = "users.SavedMusic"

    def __init__(
        self,
        *,
        id: base.InputUser,
        offset: int,
        limit: int,
        hash: int,
    ) -> None:
        self.id = id
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_int(self.offset)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        offset = r.read_int()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.id = id
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class GetSavedMusicByID(TLFunction["base.users.SavedMusic"]):
    """The TL function users.getSavedMusicByID#7573a4e9, answered with users.SavedMusic."""

    __slots__ = ("id", "documents",)

    ID = 0x7573A4E9
    QUALNAME = "functions.users.GetSavedMusicByID"
    RESULT = "users.SavedMusic"

    def __init__(
        self,
        *,
        id: base.InputUser,
        documents: list[base.InputDocument],
    ) -> None:
        self.id = id
        self.documents = documents

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_vector(self.documents)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        documents = r.read_vector()
        self = cls.__new__(cls)
        self.id = id
        self.documents = documents
        return self


class SuggestBirthday(TLFunction["base.Updates"]):
    """The TL function users.suggestBirthday#fc533372, answered with Updates."""

    __slots__ = ("id", "birthday",)

    ID = 0xFC533372
    QUALNAME = "functions.users.SuggestBirthday"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        id: base.InputUser,
        birthday: base.Birthday,
    ) -> None:
        self.id = id
        self.birthday = birthday

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        self.birthday.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        birthday = r.read_object()
        self = cls.__new__(cls)
        self.id = id
        self.birthday = birthday
        return self
