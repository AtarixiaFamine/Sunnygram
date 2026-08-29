# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Boosts, which are how a channel earns the things Telegram gates by level.

A Premium account holds a small number of boost slots and lends them out, one
chat at a time. Enough of them and a channel goes up a level, which is what
unlocks custom emoji, a wallpaper, more stories a day, and the rest of what
Telegram hands out by level rather than by payment.

Two things separate this from the other counting in the library. A boost is
lent rather than given, so every one of them expires and comes back, and the
slots are the account's rather than the chat's: which ones are already spent is
answered by my_boosts and not by asking any particular chat.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any

from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import functions

__all__ = [
    "apply_boost",
    "boosts_status",
    "iter_boost_pages",
    "my_boosts",
    "user_boosts",
]

BOOST_BATCH = 100


async def boosts_status(invoker: Invoker, peer: Target) -> Any:
    """What level a chat is at, and how far the next one is.

    The answer carries the current level, the boosts behind it, the number the
    next level needs, and the link that lets somebody spend a slot on it.
    """
    return await invoker.invoke(
        functions.premium.GetBoostsStatus(peer=await resolve(invoker, peer))
    )


async def my_boosts(invoker: Invoker) -> Any:
    """This account's boost slots, and what each one is lent to right now.

    A slot that is free says so, and one that is spent names the chat and the
    date it comes back, which is what makes it possible to ask for a slot back
    before spending it somewhere else.
    """
    return await invoker.invoke(functions.premium.GetMyBoosts())


async def apply_boost(
    invoker: Invoker, peer: Target, *, slots: Sequence[int] | None = None
) -> Any:
    """Lend this chat one of the account's boost slots.

    Naming no slots lets the server pick, which is what a person clicking the
    button in an official client does. Naming them is for moving several at
    once, and the numbers come from my_boosts.
    """
    return await invoker.invoke(
        functions.premium.ApplyBoost(
            peer=await resolve(invoker, peer),
            slots=list(slots) if slots else None,
        )
    )


async def user_boosts(invoker: Invoker, peer: Target, user: Target) -> Any:
    """Which of one person's slots are lent to this chat.

    An administrator's question rather than a member's: it is answered for a
    chat this account can see the boost list of.
    """
    return await invoker.invoke(
        functions.premium.GetUserBoosts(
            peer=await resolve(invoker, peer),
            user_id=as_user(await resolve(invoker, user)),
        )
    )


async def iter_boost_pages(
    invoker: Invoker,
    peer: Target,
    *,
    limit: int = 100,
    gifts: bool = False,
    batch: int = BOOST_BATCH,
) -> AsyncIterator[Any]:
    """Who is boosting a chat, a page at a time.

    gifts narrows it to the ones that came from a giveaway or a gift rather
    than from somebody spending their own slot. Paged by a string cursor the
    server hands back, so the end is where it stops handing one back.
    """
    where = await resolve(invoker, peer)
    offset = ""
    taken = 0
    while taken < limit:
        page = await invoker.invoke(
            functions.premium.GetBoostsList(
                peer=where,
                gifts=gifts,
                offset=offset,
                limit=min(batch, limit - taken),
            )
        )
        found = list(getattr(page, "boosts", ()) or ())
        if not found:
            return
        yield page
        taken += len(found)
        following = getattr(page, "next_offset", None)
        if not following or following == offset:
            return
        offset = following
