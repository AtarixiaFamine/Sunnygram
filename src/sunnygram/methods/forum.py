# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Topics, which are how a big group stops being one conversation.

A forum is a supergroup with the forum flag turned on. Everything in it belongs
to a topic, and a topic is not a new kind of object on the wire: it is the
message that opened it, and belonging to one is spelled as replying to that
message. That is why sending into a topic goes through the same reply field as
answering someone, and why a topic id is a message id.

The one exception is the topic every forum starts with, the general one, which
has id 1 and was never opened by anybody. It cannot be deleted and it is the
only one that can be hidden, which the server enforces instead of this module.

Turning the flag on is a separate call from any of this, needs the rights to
change the group, and is refused outright for a group below the member count
Telegram requires.
"""

from __future__ import annotations

import secrets
from collections.abc import AsyncIterator
from typing import Any

from ..network import Invoker
from ..peers import Target, as_channel, resolve
from ..raw import functions, types

__all__ = [
    "GENERAL_TOPIC",
    "create_topic",
    "delete_topic",
    "edit_topic",
    "iter_topic_pages",
    "pin_topic",
    "reorder_topics",
    "toggle_forum",
    "topics_by_id",
]

# The topic a forum is born with, which everything sent without a topic lands
# in. It has no opening message, so it is the one id here that is not one.
GENERAL_TOPIC = 1

# What Telegram answers with at once, whatever is asked for above it.
TOPIC_BATCH = 100


async def iter_topic_pages(
    invoker: Invoker,
    peer: Target,
    *,
    query: str = "",
    limit: int = 100,
    batch: int = TOPIC_BATCH,
) -> AsyncIterator[Any]:
    """The topics in a forum, a page at a time.

    The cursor is three things again: the date and id of the last topic's most
    recent message, and the topic's own id. Pinned topics come first however
    the rest are ordered, which is the server's doing and not something a
    cursor can express, so a page is taken as it arrives.
    """
    offset_date = 0
    offset_id = 0
    offset_topic = 0
    seen = 0

    while seen < limit:
        page = await invoker.invoke(
            functions.messages.GetForumTopics(
                peer=await resolve(invoker, peer),
                q=query or None,
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=min(batch, limit - seen),
            )
        )
        topics = list(getattr(page, "topics", ()))
        if not topics:
            return
        yield page
        seen += len(topics)

        last = topics[-1]
        if not isinstance(last, types.ForumTopic):
            # A deleted topic carries nothing to page from, so there is no
            # honest way to ask for what comes after it.
            return
        messages = {
            message.id: message for message in getattr(page, "messages", ())
        }
        top = messages.get(last.top_message)
        offset_date = getattr(top, "date", offset_date)
        offset_id = last.top_message
        offset_topic = last.id
        if len(topics) < batch:
            return


async def topics_by_id(invoker: Invoker, peer: Target, ids: list[int]) -> Any:
    """Particular topics, by id, with the messages that opened them."""
    return await invoker.invoke(
        functions.messages.GetForumTopicsByID(
            peer=await resolve(invoker, peer), topics=ids
        )
    )


async def create_topic(
    invoker: Invoker,
    peer: Target,
    title: str,
    *,
    icon_color: int | None = None,
    icon_emoji_id: int | None = None,
    send_as: Target | None = None,
) -> Any:
    """Open a topic, and answer with the updates that made it.

    The new topic's id is the id of the message this creates, which is the one
    thing worth knowing about how forums are built: there is no separate id
    space. icon_color is one of the six Telegram allows and is ignored when a
    custom emoji is given, since that replaces the icon instead of tinting it.
    """
    if not title:
        raise ValueError("a topic needs a title")
    return await invoker.invoke(
        functions.messages.CreateForumTopic(
            peer=await resolve(invoker, peer),
            title=title,
            icon_color=icon_color,
            icon_emoji_id=icon_emoji_id,
            random_id=int.from_bytes(secrets.token_bytes(8), "little", signed=True),
            send_as=None if send_as is None else await resolve(invoker, send_as),
        )
    )


async def edit_topic(
    invoker: Invoker,
    peer: Target,
    topic_id: int,
    *,
    title: str | None = None,
    icon_emoji_id: int | None = None,
    closed: bool | None = None,
    hidden: bool | None = None,
) -> Any:
    """Change a topic, leaving out whatever is not being changed.

    Closing one stops anybody but an administrator posting in it. Hiding one
    takes it off the list without deleting anything, and only the general topic
    can be hidden.
    """
    if all(one is None for one in (title, icon_emoji_id, closed, hidden)):
        raise ValueError("this asks to change nothing about the topic")
    return await invoker.invoke(
        functions.messages.EditForumTopic(
            peer=await resolve(invoker, peer),
            topic_id=topic_id,
            title=title,
            icon_emoji_id=icon_emoji_id,
            closed=closed,
            hidden=hidden,
        )
    )


async def pin_topic(
    invoker: Invoker, peer: Target, topic_id: int, *, pinned: bool = True
) -> Any:
    """Hold a topic at the top of the list, or let it go."""
    return await invoker.invoke(
        functions.messages.UpdatePinnedForumTopic(
            peer=await resolve(invoker, peer), topic_id=topic_id, pinned=pinned
        )
    )


async def reorder_topics(
    invoker: Invoker, peer: Target, order: list[int], *, force: bool = False
) -> Any:
    """Put the pinned topics in a given order, first in the list first.

    force says that topics left out of the list are to be unpinned, rather than
    left pinned in whatever order they were.
    """
    return await invoker.invoke(
        functions.messages.ReorderPinnedForumTopics(
            peer=await resolve(invoker, peer), order=order, force=force
        )
    )


async def delete_topic(
    invoker: Invoker, peer: Target, topic_id: int, *, rounds: int = 100
) -> int:
    """Delete a topic and everything in it, and say how much went.

    Telegram deletes a history a slice at a time and answers with how far it
    got, so this asks again until it says nothing is left. rounds is a ceiling
    on that, since a topic being written to as fast as it is deleted would
    otherwise never end.
    """
    where = await resolve(invoker, peer)
    removed = 0
    for _ in range(rounds):
        affected = await invoker.invoke(
            functions.messages.DeleteTopicHistory(peer=where, top_msg_id=topic_id)
        )
        removed += getattr(affected, "pts_count", 0)
        if not getattr(affected, "offset", 0):
            break
    return removed


async def toggle_forum(
    invoker: Invoker, peer: Target, enabled: bool, *, tabs: bool = False
) -> Any:
    """Turn topics on or off for a supergroup.

    Telegram refuses this for a group with too few members, and turning it off
    does not delete the topics: everything that was in one moves back into the
    single conversation the group used to be.
    """
    return await invoker.invoke(
        functions.channels.ToggleForum(
            channel=as_channel(await resolve(invoker, peer)),
            enabled=enabled,
            tabs=tabs,
        )
    )
