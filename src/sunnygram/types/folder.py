# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The folders a person has sorted their chats into.

Telegram calls these dialog filters, which is what they are underneath: a
folder is not a place a chat is kept but a rule for which chats to show. A chat
can be in several, and being in one does not move it anywhere.

Two shapes come back and they are worth telling apart. An ordinary folder is
this account's own and can be changed. A chatlist is a folder someone shared
as a link and this account added; it has no exclude rules, because the person
who made it decides what is in it. Both are Folder here, and shared says which.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..raw import types

__all__ = ["Folder"]


@dataclass(frozen=True, slots=True)
class Folder:
    """One folder, as the account has it set up."""

    id: int
    title: str
    shared: bool = False
    emoticon: str | None = None
    contacts: bool = False
    non_contacts: bool = False
    groups: bool = False
    broadcasts: bool = False
    bots: bool = False
    exclude_muted: bool = False
    exclude_read: bool = False
    exclude_archived: bool = False
    pinned: tuple[Any, ...] = field(default_factory=tuple)
    included: tuple[Any, ...] = field(default_factory=tuple)
    excluded: tuple[Any, ...] = field(default_factory=tuple)
    raw: Any = None

    def __repr__(self) -> str:
        kind = "shared " if self.shared else ""
        return f"Folder({self.id}, {self.title!r}, {kind}{len(self.included)} chats)"

    @property
    def editable(self) -> bool:
        """Whether this account decides what is in it.

        A folder someone else shared is not: its contents belong to whoever
        published the link, and trying to change one is refused by the server
        instead of quietly ignored.
        """
        return not self.shared

    @classmethod
    def from_raw(cls, raw: Any) -> Folder | None:
        """Wrap a dialogFilter or a dialogFilterChatlist.

        dialogFilterDefault is the unfiltered view instead of a folder, so it
        comes back as None and is left out of the list. It has no id and
        nothing to say.

        The title has been styled text rather than a plain string since layer
        204 or thereabouts, so the text is read out of it here and the styling
        is left in raw for anybody who wants it.
        """
        if isinstance(raw, types.DialogFilterDefault):
            return None
        if not isinstance(raw, (types.DialogFilter, types.DialogFilterChatlist)):
            return None
        shared = isinstance(raw, types.DialogFilterChatlist)
        title = raw.title
        return cls(
            id=raw.id,
            title=title.text if isinstance(title, types.TextWithEntities) else str(title),
            shared=shared,
            emoticon=raw.emoticon,
            contacts=getattr(raw, "contacts", False),
            non_contacts=getattr(raw, "non_contacts", False),
            groups=getattr(raw, "groups", False),
            broadcasts=getattr(raw, "broadcasts", False),
            bots=getattr(raw, "bots", False),
            exclude_muted=getattr(raw, "exclude_muted", False),
            exclude_read=getattr(raw, "exclude_read", False),
            exclude_archived=getattr(raw, "exclude_archived", False),
            pinned=tuple(raw.pinned_peers),
            included=tuple(raw.include_peers),
            excluded=tuple(getattr(raw, "exclude_peers", ()) or ()),
            raw=raw,
        )
