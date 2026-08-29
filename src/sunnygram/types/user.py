# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A person or a bot, in the shape a program wants them.

The generated user constructor has fifty fields, most of them flags no one
reads. This is the dozen that get used, with the raw one kept alongside for the
times that is not enough.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..raw import types

__all__ = ["User"]


@dataclass(frozen=True, slots=True)
class User:
    """Someone with an account."""

    id: int
    is_bot: bool = False
    is_self: bool = False
    is_premium: bool = False
    is_verified: bool = False
    is_deleted: bool = False
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone: str | None = None
    raw: Any = None

    def __repr__(self) -> str:
        what = "bot" if self.is_bot else "user"
        name = self.username and f"@{self.username}"
        return f"User({what} {self.id}, {name or self.full_name or 'no name'})"

    @property
    def full_name(self) -> str:
        """First and last together, or whichever of them there is."""
        return " ".join(
            part for part in (self.first_name, self.last_name) if part
        )

    @property
    def marked_id(self) -> int:
        """The same id, for code that stores peers without knowing the kind.

        A person's id is already unambiguous, so this is the id itself. It is
        here so that anything holding either a Chat or a User can write down
        one number without asking which it is holding.
        """
        return self.id

    @property
    def mention(self) -> str:
        """A markdown link that names this person even without a username."""
        label = self.full_name or self.username or str(self.id)
        return f"[{label}](tg://user?id={self.id})"

    @classmethod
    def from_raw(cls, user: Any) -> User | None:
        """Wrap a user off the wire, or answer None for one with nothing in it."""
        if not isinstance(user, types.User):
            return None
        return cls(
            id=user.id,
            is_bot=bool(user.bot),
            is_self=bool(user.self_),
            is_premium=bool(user.premium),
            is_verified=bool(user.verified),
            is_deleted=bool(user.deleted),
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            phone=user.phone,
            raw=user,
        )
