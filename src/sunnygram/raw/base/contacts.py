# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the contacts namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import contacts as types_contacts

    Blocked = (
        types_contacts.Blocked
        | types_contacts.BlockedSlice
    )

    ContactBirthdays = types_contacts.ContactBirthdays

    Contacts = (
        types_contacts.ContactsNotModified
        | types_contacts.Contacts
    )

    Found = types_contacts.Found

    ImportedContacts = types_contacts.ImportedContacts

    ResolvedPeer = types_contacts.ResolvedPeer

    SponsoredPeers = (
        types_contacts.SponsoredPeersEmpty
        | types_contacts.SponsoredPeers
    )

    TopPeers = (
        types_contacts.TopPeersNotModified
        | types_contacts.TopPeers
        | types_contacts.TopPeersDisabled
    )
