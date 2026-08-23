# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the contacts namespace.

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


class ContactsNotModified(TLObject):
    """The TL type contacts.contactsNotModified#b74ba9d2, a form of contacts.Contacts."""

    __slots__ = ()

    ID = 0xB74BA9D2
    QUALNAME = "types.contacts.ContactsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Contacts(TLObject):
    """The TL type contacts.contacts#eae87e42, a form of contacts.Contacts."""

    __slots__ = ("contacts", "saved_count", "users",)

    ID = 0xEAE87E42
    QUALNAME = "types.contacts.Contacts"

    def __init__(
        self,
        *,
        contacts: list[base.Contact],
        saved_count: int,
        users: list[base.User],
    ) -> None:
        self.contacts = contacts
        self.saved_count = saved_count
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.contacts)
        w.write_int(self.saved_count)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        contacts = r.read_vector()
        saved_count = r.read_int()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.contacts = contacts
        self.saved_count = saved_count
        self.users = users
        return self


class ImportedContacts(TLObject):
    """The TL type contacts.importedContacts#77d01c3b, a form of contacts.ImportedContacts."""

    __slots__ = ("imported", "popular_invites", "retry_contacts", "users",)

    ID = 0x77D01C3B
    QUALNAME = "types.contacts.ImportedContacts"

    def __init__(
        self,
        *,
        imported: list[base.ImportedContact],
        popular_invites: list[base.PopularContact],
        retry_contacts: list[int],
        users: list[base.User],
    ) -> None:
        self.imported = imported
        self.popular_invites = popular_invites
        self.retry_contacts = retry_contacts
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.imported)
        w.write_vector(self.popular_invites)
        w.write_vector(self.retry_contacts, TLWriter.write_long)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        imported = r.read_vector()
        popular_invites = r.read_vector()
        retry_contacts = r.read_vector(TLReader.read_long)
        users = r.read_vector()
        self = cls.__new__(cls)
        self.imported = imported
        self.popular_invites = popular_invites
        self.retry_contacts = retry_contacts
        self.users = users
        return self


class Blocked(TLObject):
    """The TL type contacts.blocked#0ade1591, a form of contacts.Blocked."""

    __slots__ = ("blocked", "chats", "users",)

    ID = 0x0ADE1591
    QUALNAME = "types.contacts.Blocked"

    def __init__(
        self,
        *,
        blocked: list[base.PeerBlocked],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.blocked = blocked
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.blocked)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        blocked = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.blocked = blocked
        self.chats = chats
        self.users = users
        return self


class BlockedSlice(TLObject):
    """The TL type contacts.blockedSlice#e1664194, a form of contacts.Blocked."""

    __slots__ = ("count", "blocked", "chats", "users",)

    ID = 0xE1664194
    QUALNAME = "types.contacts.BlockedSlice"

    def __init__(
        self,
        *,
        count: int,
        blocked: list[base.PeerBlocked],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.blocked = blocked
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.blocked)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        blocked = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.blocked = blocked
        self.chats = chats
        self.users = users
        return self


class Found(TLObject):
    """The TL type contacts.found#b3134d9d, a form of contacts.Found."""

    __slots__ = ("my_results", "results", "chats", "users",)

    ID = 0xB3134D9D
    QUALNAME = "types.contacts.Found"

    def __init__(
        self,
        *,
        my_results: list[base.Peer],
        results: list[base.Peer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.my_results = my_results
        self.results = results
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.my_results)
        w.write_vector(self.results)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        my_results = r.read_vector()
        results = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.my_results = my_results
        self.results = results
        self.chats = chats
        self.users = users
        return self


class ResolvedPeer(TLObject):
    """The TL type contacts.resolvedPeer#7f077ad9, a form of contacts.ResolvedPeer."""

    __slots__ = ("peer", "chats", "users",)

    ID = 0x7F077AD9
    QUALNAME = "types.contacts.ResolvedPeer"

    def __init__(
        self,
        *,
        peer: base.Peer,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.peer = peer
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.chats = chats
        self.users = users
        return self


class TopPeersNotModified(TLObject):
    """The TL type contacts.topPeersNotModified#de266ef5, a form of contacts.TopPeers."""

    __slots__ = ()

    ID = 0xDE266EF5
    QUALNAME = "types.contacts.TopPeersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class TopPeers(TLObject):
    """The TL type contacts.topPeers#70b772a8, a form of contacts.TopPeers."""

    __slots__ = ("categories", "chats", "users",)

    ID = 0x70B772A8
    QUALNAME = "types.contacts.TopPeers"

    def __init__(
        self,
        *,
        categories: list[base.TopPeerCategoryPeers],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.categories = categories
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.categories)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        categories = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.categories = categories
        self.chats = chats
        self.users = users
        return self


class TopPeersDisabled(TLObject):
    """The TL type contacts.topPeersDisabled#b52c939d, a form of contacts.TopPeers."""

    __slots__ = ()

    ID = 0xB52C939D
    QUALNAME = "types.contacts.TopPeersDisabled"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ContactBirthdays(TLObject):
    """The TL type contacts.contactBirthdays#114ff30d, a form of contacts.ContactBirthdays."""

    __slots__ = ("contacts", "users",)

    ID = 0x114FF30D
    QUALNAME = "types.contacts.ContactBirthdays"

    def __init__(
        self,
        *,
        contacts: list[base.ContactBirthday],
        users: list[base.User],
    ) -> None:
        self.contacts = contacts
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.contacts)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        contacts = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.contacts = contacts
        self.users = users
        return self


class SponsoredPeersEmpty(TLObject):
    """The TL type contacts.sponsoredPeersEmpty#ea32b4b1, a form of contacts.SponsoredPeers."""

    __slots__ = ()

    ID = 0xEA32B4B1
    QUALNAME = "types.contacts.SponsoredPeersEmpty"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SponsoredPeers(TLObject):
    """The TL type contacts.sponsoredPeers#eb032884, a form of contacts.SponsoredPeers."""

    __slots__ = ("peers", "chats", "users",)

    ID = 0xEB032884
    QUALNAME = "types.contacts.SponsoredPeers"

    def __init__(
        self,
        *,
        peers: list[base.SponsoredPeer],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.peers = peers
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.peers)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peers = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.peers = peers
        self.chats = chats
        self.users = users
        return self
