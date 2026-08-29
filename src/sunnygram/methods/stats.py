# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""What a channel or group is doing, in numbers.

Telegram keeps statistics for a channel and for a supergroup, and answers them
with two different calls carrying two different shapes. Which one a chat needs
comes down to what kind of chat it is, so that choice is made here rather than
by the caller.

Two things are worth knowing before reading a number out of any of this. The
counters arrive as a value paired with the value from the period before, which
is what makes growth readable without keeping your own history, and that pair is
what wrap turns into a Trend. The graphs do not arrive at all: a graph comes back
as a token to ask for separately, because Telegram builds them on demand, so
load_graph is a second call and not an oversight.

Statistics exist only past a size Telegram picks and does not publish. Below it
the server refuses, which is not a fault in the call.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ..network import Invoker
from ..peers import Target, as_channel, resolve
from ..raw import functions, types
from ..storage import PeerKind

__all__ = [
    "chat_stats",
    "iter_public_forward_pages",
    "load_graph",
    "message_stats",
    "story_stats",
]

FORWARD_BATCH = 100


async def chat_stats(invoker: Invoker, peer: Target, *, dark: bool = False) -> Any:
    """Everything Telegram counts about a channel or a supergroup.

    A channel answers with followers, views, shares and reactions; a supergroup
    with members, messages, viewers and posters. Picking the call that fits is
    what this is for, since asking a supergroup the channel question is an
    error rather than an empty answer.

    dark asks for graphs styled for a dark background, which changes nothing
    about the numbers.
    """
    where = await resolve(invoker, peer)
    if not isinstance(where, types.InputPeerChannel):
        raise TypeError("statistics are kept for channels and supergroups only")

    channel = as_channel(where)
    if invoker.peers.kind_of(where.channel_id) is PeerKind.SUPERGROUP:
        return await invoker.invoke(
            functions.stats.GetMegagroupStats(channel=channel, dark=dark)
        )
    return await invoker.invoke(
        functions.stats.GetBroadcastStats(channel=channel, dark=dark)
    )


async def message_stats(
    invoker: Invoker, peer: Target, message_id: int, *, dark: bool = False
) -> Any:
    """Views and reactions for one post, as two graphs."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stats.GetMessageStats(
            channel=as_channel(where), msg_id=message_id, dark=dark
        )
    )


async def story_stats(
    invoker: Invoker, peer: Target, story_id: int, *, dark: bool = False
) -> Any:
    """Views and reactions for one story, as two graphs."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stats.GetStoryStats(peer=where, id=story_id, dark=dark)
    )


async def load_graph(invoker: Invoker, token: str, *, x: int = 0) -> Any:
    """Fetch a graph the statistics only handed back a token for.

    Every graph in an answer above is either the data itself or a promise of
    it. A promise carries a token, and this is what turns one into the other.
    x asks for the detail behind a single point on a graph that offers it.
    """
    return await invoker.invoke(
        functions.stats.LoadAsyncGraph(token=token, x=x or None)
    )


async def iter_public_forward_pages(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    *,
    limit: int = 100,
    batch: int = FORWARD_BATCH,
) -> AsyncIterator[Any]:
    """Where a post was forwarded to publicly, a page at a time.

    A forward is a message in another public chat or a story that reposted it,
    and both arrive in the same list, which is why the pages come back whole
    rather than as one kind of thing.

    The cursor here is a string the server hands back rather than a number, so
    the paging is followed by repeating what it said and stopping when it stops
    saying anything.
    """
    where = await resolve(invoker, peer)
    channel = as_channel(where)
    offset = ""
    taken = 0
    while taken < limit:
        page = await invoker.invoke(
            functions.stats.GetMessagePublicForwards(
                channel=channel,
                msg_id=message_id,
                offset=offset,
                limit=min(batch, limit - taken),
            )
        )
        found = list(getattr(page, "forwards", ()) or ())
        if not found:
            return
        yield page
        taken += len(found)
        following = getattr(page, "next_offset", None)
        if not following or following == offset:
            return
        offset = following
