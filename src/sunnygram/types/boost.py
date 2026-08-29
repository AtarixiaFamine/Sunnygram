# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Where a chat stands on the boost ladder.

Telegram answers this as five separate counters and leaves the arithmetic to
the reader, and the arithmetic is the part everybody wants: how many more are
needed. The answer is not the difference between two of them, because the count
the next level needs is measured from zero rather than from the current level,
and reading it the obvious way is off by the boosts already spent.

next_level_boosts is also absent rather than zero at the top of the ladder, so
a chat that cannot go higher is a chat where needed says nothing instead of
saying none.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

__all__ = ["Boost", "BoostStatus"]


@dataclass(frozen=True, slots=True)
class BoostStatus:
    """A chat's level, and what the next one would take."""

    level: int = 0
    boosts: int = 0
    current_level_boosts: int = 0
    next_level_boosts: int | None = None
    gift_boosts: int = 0
    mine: bool = False
    my_slots: tuple[int, ...] = ()
    url: str = ""
    premium_percent: float = 0.0
    raw: Any = None

    def __repr__(self) -> str:
        needed = self.needed
        remaining = f", {needed} to go" if needed is not None else ", at the top"
        return f"BoostStatus(level {self.level}, {self.boosts} boosts{remaining})"

    @property
    def needed(self) -> int | None:
        """How many more boosts the next level takes, or nothing at the top."""
        if self.next_level_boosts is None:
            return None
        return max(0, self.next_level_boosts - self.boosts)

    @property
    def progress(self) -> float:
        """How far through the current level, from 0.0 to 1.0.

        A chat that cannot go higher is finished, so it reads 1.0 rather than
        dividing by a number that is not there.
        """
        if self.next_level_boosts is None:
            return 1.0
        span = self.next_level_boosts - self.current_level_boosts
        if span <= 0:
            return 1.0
        done = self.boosts - self.current_level_boosts
        return min(1.0, max(0.0, done / span))

    @classmethod
    def from_raw(cls, status: Any) -> BoostStatus:
        """Wrap what premium.getBoostsStatus answered with."""
        percent = getattr(status, "premium_audience", None)
        return cls(
            level=getattr(status, "level", 0) or 0,
            boosts=getattr(status, "boosts", 0) or 0,
            current_level_boosts=getattr(status, "current_level_boosts", 0) or 0,
            next_level_boosts=getattr(status, "next_level_boosts", None),
            gift_boosts=getattr(status, "gift_boosts", 0) or 0,
            mine=bool(getattr(status, "my_boost", False)),
            my_slots=tuple(getattr(status, "my_boost_slots", None) or ()),
            url=getattr(status, "boost_url", "") or "",
            premium_percent=float(getattr(percent, "part", 0.0) or 0.0),
            raw=status,
        )


@dataclass(frozen=True, slots=True)
class Boost:
    """One boost lent to a chat, and when it comes back."""

    id: str = ""
    user_id: int | None = None
    date: datetime | None = None
    expires: datetime | None = None
    gift: bool = False
    giveaway: bool = False
    unclaimed: bool = False
    multiplier: int = 1
    stars: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        who = self.user_id if self.user_id is not None else "unclaimed"
        return f"Boost({who}, x{self.multiplier})"

    @classmethod
    def from_raw(cls, boost: Any) -> Boost:
        """Wrap one entry out of a boost list."""
        return cls(
            id=getattr(boost, "id", "") or "",
            user_id=getattr(boost, "user_id", None),
            date=_moment(getattr(boost, "date", 0)),
            expires=_moment(getattr(boost, "expires", 0)),
            gift=bool(getattr(boost, "gift", False)),
            giveaway=bool(getattr(boost, "giveaway", False)),
            unclaimed=bool(getattr(boost, "unclaimed", False)),
            # Absent means one, not none: a boost is at least itself.
            multiplier=getattr(boost, "multiplier", None) or 1,
            stars=getattr(boost, "stars", None) or 0,
            raw=boost,
        )


def _moment(stamp: int | None) -> datetime | None:
    """A unix time as a datetime, and nothing for the zero Telegram uses."""
    if not stamp:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc)
