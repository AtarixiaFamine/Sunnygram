# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the users namespace.

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


class UserFull(TLObject):
    """The TL type users.userFull#3b6d152e, a form of users.UserFull."""

    __slots__ = ("full_user", "chats", "users",)

    ID = 0x3B6D152E
    QUALNAME = "types.users.UserFull"

    def __init__(
        self,
        *,
        full_user: base.UserFull,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.full_user = full_user
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.full_user.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        full_user = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.full_user = full_user
        self.chats = chats
        self.users = users
        return self


class Users(TLObject):
    """The TL type users.users#62d706b8, a form of users.Users."""

    __slots__ = ("users",)

    ID = 0x62D706B8
    QUALNAME = "types.users.Users"

    def __init__(
        self,
        *,
        users: list[base.User],
    ) -> None:
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        users = r.read_vector()
        self = cls.__new__(cls)
        self.users = users
        return self


class UsersSlice(TLObject):
    """The TL type users.usersSlice#315a4974, a form of users.Users."""

    __slots__ = ("count", "users",)

    ID = 0x315A4974
    QUALNAME = "types.users.UsersSlice"

    def __init__(
        self,
        *,
        count: int,
        users: list[base.User],
    ) -> None:
        self.count = count
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.users = users
        return self


class SavedMusicNotModified(TLObject):
    """The TL type users.savedMusicNotModified#e3878aa4, a form of users.SavedMusic."""

    __slots__ = ("count",)

    ID = 0xE3878AA4
    QUALNAME = "types.users.SavedMusicNotModified"

    def __init__(
        self,
        *,
        count: int,
    ) -> None:
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        return self


class SavedMusic(TLObject):
    """The TL type users.savedMusic#34a2f297, a form of users.SavedMusic."""

    __slots__ = ("count", "documents",)

    ID = 0x34A2F297
    QUALNAME = "types.users.SavedMusic"

    def __init__(
        self,
        *,
        count: int,
        documents: list[base.Document],
    ) -> None:
        self.count = count
        self.documents = documents

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.documents)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        documents = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.documents = documents
        return self
