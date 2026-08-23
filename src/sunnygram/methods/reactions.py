# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Reacting to a message, and seeing who else did.

One call does all three things, which is not obvious from its name. Sending a
reaction sets the whole list of this account's reactions on that message, so
adding a second one means sending both, and removing them all means sending an
empty list. There is no separate call for taking one back.

A reaction is either an emoji or a custom one, and the second is a document id
, not a character. Both are accepted here in the form a caller has: a
string is an emoji, an integer is a custom one.
"""

from __future__ import annotations

from typing import Any

from ..network import Invoker
from ..peers import Target, resolve
from ..raw import base, functions, types

__all__ = ["available_reactions", "get_reactions", "send_reaction", "as_reaction"]


def as_reaction(reaction: str | int | base.Reaction) -> base.Reaction:
    """Whatever names a reaction, as the protocol spells it.

    A string is an emoji, an integer is a custom emoji's document id, and
    anything already a Reaction goes straight through.
    """
    if isinstance(reaction, str):
        return types.ReactionEmoji(emoticon=reaction)
    if isinstance(reaction, int):
        return types.ReactionCustomEmoji(document_id=reaction)
    return reaction


async def send_reaction(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    reaction: str | int | base.Reaction | list[str | int | base.Reaction] | None = None,
    *,
    big: bool = False,
    recent: bool = True,
) -> Any:
    """Set this account's reactions on a message, replacing whatever was there.

    Passing nothing takes every reaction back, since the call sets the list
    instead of adding to it. Passing several is how a premium account reacts
    more than once; an ordinary one is refused by the server, not here, because
    which accounts may is not something a client can know.

    big asks the other clients to play the large animation, which is what
    happens when someone holds the button instead of tapping it. recent puts
    the emoji at the front of this account's own recently-used list.
    """
    where = await resolve(invoker, peer)
    if reaction is None:
        chosen: list[base.Reaction] = []
    elif isinstance(reaction, list):
        chosen = [as_reaction(one) for one in reaction]
    else:
        chosen = [as_reaction(reaction)]

    return await invoker.invoke(
        functions.messages.SendReaction(
            peer=where,
            msg_id=message_id,
            reaction=chosen or None,
            big=big,
            add_to_recent=recent and bool(chosen),
        )
    )


async def get_reactions(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    *,
    reaction: str | int | base.Reaction | None = None,
    limit: int = 100,
) -> Any:
    """Who reacted to a message, and with what.

    Naming a reaction narrows it to the people who used that one. Only a chat
    small enough for Telegram to bother keeping the list answers at all; a
    large channel gives counts and no names.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.GetMessageReactionsList(
            peer=where,
            id=message_id,
            reaction=None if reaction is None else as_reaction(reaction),
            limit=limit,
        )
    )


async def available_reactions(invoker: Invoker) -> Any:
    """Every reaction Telegram currently offers, with its animations.

    Worth caching. The list changes rarely and the answer is large, which is
    why the call takes a hash and answers with nothing at all when the copy
    already held is current.
    """
    return await invoker.invoke(functions.messages.GetAvailableReactions(hash=0))
