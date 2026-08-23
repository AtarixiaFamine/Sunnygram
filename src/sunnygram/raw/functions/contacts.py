# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the contacts namespace.

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


class GetContactIDs(TLFunction["list[int]"]):
    """The TL function contacts.getContactIDs#7adc669d, answered with Vector<int>."""

    __slots__ = ("hash",)

    ID = 0x7ADC669D
    QUALNAME = "functions.contacts.GetContactIDs"
    RESULT = "Vector<int>"

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


class GetStatuses(TLFunction["list[base.ContactStatus]"]):
    """The TL function contacts.getStatuses#c4a353ee, answered with Vector<ContactStatus>."""

    __slots__ = ()

    ID = 0xC4A353EE
    QUALNAME = "functions.contacts.GetStatuses"
    RESULT = "Vector<ContactStatus>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetContacts(TLFunction["base.contacts.Contacts"]):
    """The TL function contacts.getContacts#5dd69e12, answered with contacts.Contacts."""

    __slots__ = ("hash",)

    ID = 0x5DD69E12
    QUALNAME = "functions.contacts.GetContacts"
    RESULT = "contacts.Contacts"

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


class ImportContacts(TLFunction["base.contacts.ImportedContacts"]):
    """The TL function contacts.importContacts#2c800be5, answered with contacts.ImportedContacts."""

    __slots__ = ("contacts",)

    ID = 0x2C800BE5
    QUALNAME = "functions.contacts.ImportContacts"
    RESULT = "contacts.ImportedContacts"

    def __init__(
        self,
        *,
        contacts: list[base.InputContact],
    ) -> None:
        self.contacts = contacts

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.contacts)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        contacts = r.read_vector()
        self = cls.__new__(cls)
        self.contacts = contacts
        return self


class DeleteContacts(TLFunction["base.Updates"]):
    """The TL function contacts.deleteContacts#096a0e00, answered with Updates."""

    __slots__ = ("id",)

    ID = 0x096A0E00
    QUALNAME = "functions.contacts.DeleteContacts"
    RESULT = "Updates"

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


class DeleteByPhones(TLFunction["bool"]):
    """The TL function contacts.deleteByPhones#1013fd9e, answered with Bool."""

    __slots__ = ("phones",)

    ID = 0x1013FD9E
    QUALNAME = "functions.contacts.DeleteByPhones"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phones: list[str],
    ) -> None:
        self.phones = phones

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.phones, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phones = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.phones = phones
        return self


class Block(TLFunction["bool"]):
    """The TL function contacts.block#2e2e8734, answered with Bool."""

    __slots__ = ("my_stories_from", "id",)

    ID = 0x2E2E8734
    QUALNAME = "functions.contacts.Block"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        my_stories_from: bool = False,
        id: base.InputPeer,
    ) -> None:
        self.my_stories_from = my_stories_from
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.my_stories_from:
            flags |= 1 << 0
        w.write_int(flags)
        self.id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        my_stories_from = bool(flags & (1 << 0))
        id = r.read_object()
        self = cls.__new__(cls)
        self.my_stories_from = my_stories_from
        self.id = id
        return self


class Unblock(TLFunction["bool"]):
    """The TL function contacts.unblock#b550d328, answered with Bool."""

    __slots__ = ("my_stories_from", "id",)

    ID = 0xB550D328
    QUALNAME = "functions.contacts.Unblock"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        my_stories_from: bool = False,
        id: base.InputPeer,
    ) -> None:
        self.my_stories_from = my_stories_from
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.my_stories_from:
            flags |= 1 << 0
        w.write_int(flags)
        self.id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        my_stories_from = bool(flags & (1 << 0))
        id = r.read_object()
        self = cls.__new__(cls)
        self.my_stories_from = my_stories_from
        self.id = id
        return self


class GetBlocked(TLFunction["base.contacts.Blocked"]):
    """The TL function contacts.getBlocked#9a868f80, answered with contacts.Blocked."""

    __slots__ = ("my_stories_from", "offset", "limit",)

    ID = 0x9A868F80
    QUALNAME = "functions.contacts.GetBlocked"
    RESULT = "contacts.Blocked"

    def __init__(
        self,
        *,
        my_stories_from: bool = False,
        offset: int,
        limit: int,
    ) -> None:
        self.my_stories_from = my_stories_from
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.my_stories_from:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        my_stories_from = bool(flags & (1 << 0))
        offset = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.my_stories_from = my_stories_from
        self.offset = offset
        self.limit = limit
        return self


class Search(TLFunction["base.contacts.Found"]):
    """The TL function contacts.search#05f58d0f, answered with contacts.Found."""

    __slots__ = ("broadcasts", "bots", "q", "limit",)

    ID = 0x05F58D0F
    QUALNAME = "functions.contacts.Search"
    RESULT = "contacts.Found"

    def __init__(
        self,
        *,
        broadcasts: bool = False,
        bots: bool = False,
        q: str,
        limit: int,
    ) -> None:
        self.broadcasts = broadcasts
        self.bots = bots
        self.q = q
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.broadcasts:
            flags |= 1 << 0
        if self.bots:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.q)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        broadcasts = bool(flags & (1 << 0))
        bots = bool(flags & (1 << 1))
        q = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.broadcasts = broadcasts
        self.bots = bots
        self.q = q
        self.limit = limit
        return self


class ResolveUsername(TLFunction["base.contacts.ResolvedPeer"]):
    """The TL function contacts.resolveUsername#725afbbc, answered with contacts.ResolvedPeer."""

    __slots__ = ("username", "referer",)

    ID = 0x725AFBBC
    QUALNAME = "functions.contacts.ResolveUsername"
    RESULT = "contacts.ResolvedPeer"

    def __init__(
        self,
        *,
        username: str,
        referer: str | None = None,
    ) -> None:
        self.username = username
        self.referer = referer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.referer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.username)
        if self.referer is not None:
            w.write_string(self.referer)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        username = r.read_string()
        referer = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.username = username
        self.referer = referer
        return self


class GetTopPeers(TLFunction["base.contacts.TopPeers"]):
    """The TL function contacts.getTopPeers#973478b6, answered with contacts.TopPeers."""

    __slots__ = ("correspondents", "bots_pm", "bots_inline", "phone_calls", "forward_users", "forward_chats", "groups", "channels", "bots_app", "bots_guestchat", "offset", "limit", "hash",)

    ID = 0x973478B6
    QUALNAME = "functions.contacts.GetTopPeers"
    RESULT = "contacts.TopPeers"

    def __init__(
        self,
        *,
        correspondents: bool = False,
        bots_pm: bool = False,
        bots_inline: bool = False,
        phone_calls: bool = False,
        forward_users: bool = False,
        forward_chats: bool = False,
        groups: bool = False,
        channels: bool = False,
        bots_app: bool = False,
        bots_guestchat: bool = False,
        offset: int,
        limit: int,
        hash: int,
    ) -> None:
        self.correspondents = correspondents
        self.bots_pm = bots_pm
        self.bots_inline = bots_inline
        self.phone_calls = phone_calls
        self.forward_users = forward_users
        self.forward_chats = forward_chats
        self.groups = groups
        self.channels = channels
        self.bots_app = bots_app
        self.bots_guestchat = bots_guestchat
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.correspondents:
            flags |= 1 << 0
        if self.bots_pm:
            flags |= 1 << 1
        if self.bots_inline:
            flags |= 1 << 2
        if self.phone_calls:
            flags |= 1 << 3
        if self.forward_users:
            flags |= 1 << 4
        if self.forward_chats:
            flags |= 1 << 5
        if self.groups:
            flags |= 1 << 10
        if self.channels:
            flags |= 1 << 15
        if self.bots_app:
            flags |= 1 << 16
        if self.bots_guestchat:
            flags |= 1 << 17
        w.write_int(flags)
        w.write_int(self.offset)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        correspondents = bool(flags & (1 << 0))
        bots_pm = bool(flags & (1 << 1))
        bots_inline = bool(flags & (1 << 2))
        phone_calls = bool(flags & (1 << 3))
        forward_users = bool(flags & (1 << 4))
        forward_chats = bool(flags & (1 << 5))
        groups = bool(flags & (1 << 10))
        channels = bool(flags & (1 << 15))
        bots_app = bool(flags & (1 << 16))
        bots_guestchat = bool(flags & (1 << 17))
        offset = r.read_int()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.correspondents = correspondents
        self.bots_pm = bots_pm
        self.bots_inline = bots_inline
        self.phone_calls = phone_calls
        self.forward_users = forward_users
        self.forward_chats = forward_chats
        self.groups = groups
        self.channels = channels
        self.bots_app = bots_app
        self.bots_guestchat = bots_guestchat
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class ResetTopPeerRating(TLFunction["bool"]):
    """The TL function contacts.resetTopPeerRating#1ae373ac, answered with Bool."""

    __slots__ = ("category", "peer",)

    ID = 0x1AE373AC
    QUALNAME = "functions.contacts.ResetTopPeerRating"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        category: base.TopPeerCategory,
        peer: base.InputPeer,
    ) -> None:
        self.category = category
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.category.write(w)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        category = r.read_object()
        peer = r.read_object()
        self = cls.__new__(cls)
        self.category = category
        self.peer = peer
        return self


class ResetSaved(TLFunction["bool"]):
    """The TL function contacts.resetSaved#879537f1, answered with Bool."""

    __slots__ = ()

    ID = 0x879537F1
    QUALNAME = "functions.contacts.ResetSaved"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSaved(TLFunction["list[base.SavedContact]"]):
    """The TL function contacts.getSaved#82f1e39f, answered with Vector<SavedContact>."""

    __slots__ = ()

    ID = 0x82F1E39F
    QUALNAME = "functions.contacts.GetSaved"
    RESULT = "Vector<SavedContact>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ToggleTopPeers(TLFunction["bool"]):
    """The TL function contacts.toggleTopPeers#8514bdda, answered with Bool."""

    __slots__ = ("enabled",)

    ID = 0x8514BDDA
    QUALNAME = "functions.contacts.ToggleTopPeers"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        enabled: bool,
    ) -> None:
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.enabled = enabled
        return self


class AddContact(TLFunction["base.Updates"]):
    """The TL function contacts.addContact#d9ba2e54, answered with Updates."""

    __slots__ = ("add_phone_privacy_exception", "id", "first_name", "last_name", "phone", "note",)

    ID = 0xD9BA2E54
    QUALNAME = "functions.contacts.AddContact"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        add_phone_privacy_exception: bool = False,
        id: base.InputUser,
        first_name: str,
        last_name: str,
        phone: str,
        note: base.TextWithEntities | None = None,
    ) -> None:
        self.add_phone_privacy_exception = add_phone_privacy_exception
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.note = note

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.add_phone_privacy_exception:
            flags |= 1 << 0
        if self.note is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.id.write(w)
        w.write_string(self.first_name)
        w.write_string(self.last_name)
        w.write_string(self.phone)
        if self.note is not None:
            self.note.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        add_phone_privacy_exception = bool(flags & (1 << 0))
        id = r.read_object()
        first_name = r.read_string()
        last_name = r.read_string()
        phone = r.read_string()
        note = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.add_phone_privacy_exception = add_phone_privacy_exception
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.note = note
        return self


class AcceptContact(TLFunction["base.Updates"]):
    """The TL function contacts.acceptContact#f831a20f, answered with Updates."""

    __slots__ = ("id",)

    ID = 0xF831A20F
    QUALNAME = "functions.contacts.AcceptContact"
    RESULT = "Updates"

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


class GetLocated(TLFunction["base.Updates"]):
    """The TL function contacts.getLocated#d348bc44, answered with Updates."""

    __slots__ = ("background", "geo_point", "self_expires",)

    ID = 0xD348BC44
    QUALNAME = "functions.contacts.GetLocated"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        background: bool = False,
        geo_point: base.InputGeoPoint,
        self_expires: int | None = None,
    ) -> None:
        self.background = background
        self.geo_point = geo_point
        self.self_expires = self_expires

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.background:
            flags |= 1 << 1
        if self.self_expires is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.geo_point.write(w)
        if self.self_expires is not None:
            w.write_int(self.self_expires)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        background = bool(flags & (1 << 1))
        geo_point = r.read_object()
        self_expires = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.background = background
        self.geo_point = geo_point
        self.self_expires = self_expires
        return self


class BlockFromReplies(TLFunction["base.Updates"]):
    """The TL function contacts.blockFromReplies#29a8962c, answered with Updates."""

    __slots__ = ("delete_message", "delete_history", "report_spam", "msg_id",)

    ID = 0x29A8962C
    QUALNAME = "functions.contacts.BlockFromReplies"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        delete_message: bool = False,
        delete_history: bool = False,
        report_spam: bool = False,
        msg_id: int,
    ) -> None:
        self.delete_message = delete_message
        self.delete_history = delete_history
        self.report_spam = report_spam
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.delete_message:
            flags |= 1 << 0
        if self.delete_history:
            flags |= 1 << 1
        if self.report_spam:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        delete_message = bool(flags & (1 << 0))
        delete_history = bool(flags & (1 << 1))
        report_spam = bool(flags & (1 << 2))
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.delete_message = delete_message
        self.delete_history = delete_history
        self.report_spam = report_spam
        self.msg_id = msg_id
        return self


class ResolvePhone(TLFunction["base.contacts.ResolvedPeer"]):
    """The TL function contacts.resolvePhone#8af94344, answered with contacts.ResolvedPeer."""

    __slots__ = ("phone",)

    ID = 0x8AF94344
    QUALNAME = "functions.contacts.ResolvePhone"
    RESULT = "contacts.ResolvedPeer"

    def __init__(
        self,
        *,
        phone: str,
    ) -> None:
        self.phone = phone

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone = r.read_string()
        self = cls.__new__(cls)
        self.phone = phone
        return self


class ExportContactToken(TLFunction["base.ExportedContactToken"]):
    """The TL function contacts.exportContactToken#f8654027, answered with ExportedContactToken."""

    __slots__ = ()

    ID = 0xF8654027
    QUALNAME = "functions.contacts.ExportContactToken"
    RESULT = "ExportedContactToken"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ImportContactToken(TLFunction["base.User"]):
    """The TL function contacts.importContactToken#13005788, answered with User."""

    __slots__ = ("token",)

    ID = 0x13005788
    QUALNAME = "functions.contacts.ImportContactToken"
    RESULT = "User"

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


class EditCloseFriends(TLFunction["bool"]):
    """The TL function contacts.editCloseFriends#ba6705f0, answered with Bool."""

    __slots__ = ("id",)

    ID = 0xBA6705F0
    QUALNAME = "functions.contacts.EditCloseFriends"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: list[int],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.id = id
        return self


class SetBlocked(TLFunction["bool"]):
    """The TL function contacts.setBlocked#94c65c76, answered with Bool."""

    __slots__ = ("my_stories_from", "id", "limit",)

    ID = 0x94C65C76
    QUALNAME = "functions.contacts.SetBlocked"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        my_stories_from: bool = False,
        id: list[base.InputPeer],
        limit: int,
    ) -> None:
        self.my_stories_from = my_stories_from
        self.id = id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.my_stories_from:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        my_stories_from = bool(flags & (1 << 0))
        id = r.read_vector()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.my_stories_from = my_stories_from
        self.id = id
        self.limit = limit
        return self


class GetBirthdays(TLFunction["base.contacts.ContactBirthdays"]):
    """The TL function contacts.getBirthdays#daeda864, answered with contacts.ContactBirthdays."""

    __slots__ = ()

    ID = 0xDAEDA864
    QUALNAME = "functions.contacts.GetBirthdays"
    RESULT = "contacts.ContactBirthdays"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSponsoredPeers(TLFunction["base.contacts.SponsoredPeers"]):
    """The TL function contacts.getSponsoredPeers#b6c8c393, answered with contacts.SponsoredPeers."""

    __slots__ = ("q",)

    ID = 0xB6C8C393
    QUALNAME = "functions.contacts.GetSponsoredPeers"
    RESULT = "contacts.SponsoredPeers"

    def __init__(
        self,
        *,
        q: str,
    ) -> None:
        self.q = q

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.q)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        q = r.read_string()
        self = cls.__new__(cls)
        self.q = q
        return self


class UpdateContactNote(TLFunction["bool"]):
    """The TL function contacts.updateContactNote#139f63fb, answered with Bool."""

    __slots__ = ("id", "note",)

    ID = 0x139F63FB
    QUALNAME = "functions.contacts.UpdateContactNote"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.InputUser,
        note: base.TextWithEntities,
    ) -> None:
        self.id = id
        self.note = note

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        self.note.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        note = r.read_object()
        self = cls.__new__(cls)
        self.id = id
        self.note = note
        return self
