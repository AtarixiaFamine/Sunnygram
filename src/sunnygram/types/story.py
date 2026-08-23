# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A story: something posted to be seen for a day and then not.

Three constructors arrive where a story is expected and only one of them is a
story you can read. The other two are placeholders: skipped means it is there
but this account is not being shown the contents, and deleted means it is gone
and only the id is left. Telling them apart matters, because a list of stories
routinely contains all three and treating a placeholder as a story is how a
program ends up showing an empty card.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..raw import types

__all__ = ["Story"]


@dataclass(frozen=True, slots=True)
class Story:
    """One story, or a placeholder saying one is there."""

    id: int
    date: int = 0
    expires: int = 0
    caption: str = ""
    available: bool = True
    pinned: bool = False
    public: bool = False
    close_friends: bool = False
    contacts: bool = False
    outgoing: bool = False
    edited: bool = False
    views: int = 0
    media: Any = None
    entities: tuple[Any, ...] = field(default_factory=tuple)
    raw: Any = None

    def __repr__(self) -> str:
        if not self.available:
            return f"Story({self.id}, not shown)"
        text = f" {self.caption[:20]!r}" if self.caption else ""
        return f"Story({self.id},{text} {self.views} views)"

    @property
    def has_media(self) -> bool:
        return self.media is not None

    @classmethod
    def from_raw(cls, raw: Any) -> Story | None:
        """Wrap a storyItem, or a skipped one as a placeholder.

        A deleted story is None: there is nothing left of it but an id, and
        handing back an object whose every field is empty would be a worse
        answer than saying it is not there.
        """
        if isinstance(raw, types.StoryItemSkipped):
            return cls(
                id=raw.id,
                date=raw.date,
                expires=raw.expire_date,
                available=False,
                close_friends=raw.close_friends,
                raw=raw,
            )
        if not isinstance(raw, types.StoryItem):
            return None
        views = raw.views
        return cls(
            id=raw.id,
            date=raw.date,
            expires=raw.expire_date,
            caption=raw.caption or "",
            pinned=raw.pinned,
            public=raw.public,
            close_friends=raw.close_friends,
            contacts=raw.contacts,
            outgoing=raw.out,
            edited=raw.edited,
            views=views.views_count if isinstance(views, types.StoryViews) else 0,
            media=raw.media,
            entities=tuple(raw.entities or ()),
            raw=raw,
        )
