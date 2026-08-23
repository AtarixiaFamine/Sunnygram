# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the premium namespace.

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


class BoostsList(TLObject):
    """The TL type premium.boostsList#86f8613c, a form of premium.BoostsList."""

    __slots__ = ("count", "boosts", "next_offset", "users",)

    ID = 0x86F8613C
    QUALNAME = "types.premium.BoostsList"

    def __init__(
        self,
        *,
        count: int,
        boosts: list[base.Boost],
        next_offset: str | None = None,
        users: list[base.User],
    ) -> None:
        self.count = count
        self.boosts = boosts
        self.next_offset = next_offset
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.boosts)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        boosts = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.boosts = boosts
        self.next_offset = next_offset
        self.users = users
        return self


class MyBoosts(TLObject):
    """The TL type premium.myBoosts#9ae228e2, a form of premium.MyBoosts."""

    __slots__ = ("my_boosts", "chats", "users",)

    ID = 0x9AE228E2
    QUALNAME = "types.premium.MyBoosts"

    def __init__(
        self,
        *,
        my_boosts: list[base.MyBoost],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.my_boosts = my_boosts
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.my_boosts)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        my_boosts = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.my_boosts = my_boosts
        self.chats = chats
        self.users = users
        return self


class BoostsStatus(TLObject):
    """The TL type premium.boostsStatus#4959427a, a form of premium.BoostsStatus."""

    __slots__ = ("my_boost", "level", "current_level_boosts", "boosts", "gift_boosts", "next_level_boosts", "premium_audience", "boost_url", "prepaid_giveaways", "my_boost_slots",)

    ID = 0x4959427A
    QUALNAME = "types.premium.BoostsStatus"

    def __init__(
        self,
        *,
        my_boost: bool = False,
        level: int,
        current_level_boosts: int,
        boosts: int,
        gift_boosts: int | None = None,
        next_level_boosts: int | None = None,
        premium_audience: base.StatsPercentValue | None = None,
        boost_url: str,
        prepaid_giveaways: list[base.PrepaidGiveaway] | None = None,
        my_boost_slots: list[int] | None = None,
    ) -> None:
        self.my_boost = my_boost
        self.level = level
        self.current_level_boosts = current_level_boosts
        self.boosts = boosts
        self.gift_boosts = gift_boosts
        self.next_level_boosts = next_level_boosts
        self.premium_audience = premium_audience
        self.boost_url = boost_url
        self.prepaid_giveaways = prepaid_giveaways
        self.my_boost_slots = my_boost_slots

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.my_boost:
            flags |= 1 << 2
        if self.gift_boosts is not None:
            flags |= 1 << 4
        if self.next_level_boosts is not None:
            flags |= 1 << 0
        if self.premium_audience is not None:
            flags |= 1 << 1
        if self.prepaid_giveaways is not None:
            flags |= 1 << 3
        if self.my_boost_slots is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.level)
        w.write_int(self.current_level_boosts)
        w.write_int(self.boosts)
        if self.gift_boosts is not None:
            w.write_int(self.gift_boosts)
        if self.next_level_boosts is not None:
            w.write_int(self.next_level_boosts)
        if self.premium_audience is not None:
            self.premium_audience.write(w)
        w.write_string(self.boost_url)
        if self.prepaid_giveaways is not None:
            w.write_vector(self.prepaid_giveaways)
        if self.my_boost_slots is not None:
            w.write_vector(self.my_boost_slots, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        my_boost = bool(flags & (1 << 2))
        level = r.read_int()
        current_level_boosts = r.read_int()
        boosts = r.read_int()
        gift_boosts = r.read_int() if flags & (1 << 4) else None
        next_level_boosts = r.read_int() if flags & (1 << 0) else None
        premium_audience = r.read_object() if flags & (1 << 1) else None
        boost_url = r.read_string()
        prepaid_giveaways = r.read_vector() if flags & (1 << 3) else None
        my_boost_slots = r.read_vector(TLReader.read_int) if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.my_boost = my_boost
        self.level = level
        self.current_level_boosts = current_level_boosts
        self.boosts = boosts
        self.gift_boosts = gift_boosts
        self.next_level_boosts = next_level_boosts
        self.premium_audience = premium_audience
        self.boost_url = boost_url
        self.prepaid_giveaways = prepaid_giveaways
        self.my_boost_slots = my_boost_slots
        return self
