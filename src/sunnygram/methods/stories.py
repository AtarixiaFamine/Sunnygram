# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Posting and reading stories.

The part that catches people out is privacy. stories.sendStory takes a required
vector of privacy rules, and an empty one is not "the default", it is "no one",
so a story posted without thinking about this is posted to an audience of none
and looks like it silently failed. That is why privacy here is a word with a
default rather than a list someone has to remember to fill in.
"""

from __future__ import annotations

from typing import Any

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, resolve
from ..raw import base, functions, types
from ..updates import UpdateManager
from .messages import random_id

__all__ = [
    "AUDIENCES",
    "audience",
    "delete_stories",
    "edit_story",
    "get_peer_stories",
    "get_stories",
    "pin_stories",
    "pinned_stories",
    "read_stories",
    "send_story",
    "stories_archive",
    "story_views",
]

# How long a story stays up, in seconds. Telegram allows these and refuses
# anything else, so a wrong number is a rejected call instead of a rounded one.
PERIODS = (6 * 3600, 12 * 3600, 24 * 3600, 48 * 3600)

# Who gets to see a story, spelled the way a person would say it.
AUDIENCES = ("everyone", "contacts", "close_friends", "nobody")


def audience(who: str) -> list[base.InputPrivacyRule]:
    """The privacy rules for one of the named audiences.

    Telegram's model is a list of allow and disallow rules, which is more than
    most callers want to think about. These four cover what the official
    clients offer; anything finer is a list of rules passed directly.
    """
    if who == "everyone":
        return [types.InputPrivacyValueAllowAll()]
    if who == "contacts":
        return [types.InputPrivacyValueAllowContacts()]
    if who == "close_friends":
        return [types.InputPrivacyValueAllowCloseFriends()]
    if who == "nobody":
        # An empty rule list, which is what "no one" is on the wire. Spelling
        # it out here is the point: it is also what you get by forgetting.
        return []
    raise ValueError(f"audience must be one of {AUDIENCES}, not {who!r}")


async def send_story(
    invoker: Invoker,
    peer: Target,
    media: base.InputMedia,
    *,
    caption: str = "",
    entities: list[base.MessageEntity] | None = None,
    privacy: str | list[base.InputPrivacyRule] = "everyone",
    pinned: bool = False,
    noforwards: bool = False,
    period: int | None = None,
    updates: UpdateManager | None = None,
) -> Any:
    """Post a story, and answer with the updates the server made of it.

    The media is already-uploaded bytes described as a photo or a video, which
    is what methods/media.py builds, the same as for a message.

    privacy is one of everyone, contacts, close_friends or no one, or a list of
    rules for anything finer. pinned keeps the story on the profile after it
    expires, which Telegram calls saving it to a profile.

    period is how long it stays up and has to be one of 6, 12, 24 or 48 hours
    in seconds. Leaving it alone takes Telegram's default of a day.
    """
    if period is not None and period not in PERIODS:
        raise ValueError(f"period must be one of {PERIODS} seconds, not {period}")
    rules = audience(privacy) if isinstance(privacy, str) else list(privacy)
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.stories.SendStory(
            peer=where,
            media=media,
            privacy_rules=rules,
            random_id=random_id(),
            caption=caption or None,
            entities=entities or None,
            pinned=pinned,
            noforwards=noforwards,
            period=period,
        )
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def edit_story(
    invoker: Invoker,
    peer: Target,
    story_id: int,
    *,
    media: base.InputMedia | None = None,
    caption: str | None = None,
    entities: list[base.MessageEntity] | None = None,
    privacy: str | list[base.InputPrivacyRule] | None = None,
    updates: UpdateManager | None = None,
) -> Any:
    """Change a story that is already up.

    Everything is optional and only what is given is touched, so editing the
    caption leaves the media alone. Passing nothing at all is refused here
    instead of sent, since the server would take it and do nothing.
    """
    if media is None and caption is None and privacy is None:
        raise SunnygramError("editing a story needs media, a caption or privacy")
    # caption and entities share flag bit 1 on this call, unlike sendStory
    # where they have one each. Writing the caption without the entities sets
    # the bit and then writes one of the two fields, which produces a request
    # no reader can parse and a call that hangs rather than fails. So the
    # entities always travel with the caption, empty if there are none.
    styled = list(entities or []) if caption is not None else None
    rules = (
        None
        if privacy is None
        else (audience(privacy) if isinstance(privacy, str) else list(privacy))
    )
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.stories.EditStory(
            peer=where,
            id=story_id,
            media=media,
            caption=caption,
            entities=styled,
            privacy_rules=rules,
        )
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def delete_stories(invoker: Invoker, peer: Target, ids: list[int]) -> list[int]:
    """Take stories down. Answers with the ids that were actually removed."""
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.stories.DeleteStories(peer=where, id=list(ids))
    )
    return list(answer)


async def pin_stories(
    invoker: Invoker, peer: Target, ids: list[int], *, pinned: bool = True
) -> list[int]:
    """Keep stories on the profile after they expire, or stop keeping them."""
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.stories.TogglePinned(peer=where, id=list(ids), pinned=pinned)
    )
    return list(answer)


async def get_stories(invoker: Invoker, peer: Target, ids: list[int]) -> Any:
    """Particular stories by id."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stories.GetStoriesByID(peer=where, id=list(ids))
    )


async def get_peer_stories(invoker: Invoker, peer: Target) -> Any:
    """Whatever one account currently has up."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(functions.stories.GetPeerStories(peer=where))


async def pinned_stories(
    invoker: Invoker, peer: Target, *, offset_id: int = 0, limit: int = 100
) -> Any:
    """The stories an account has kept on its profile."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stories.GetPinnedStories(
            peer=where, offset_id=offset_id, limit=limit
        )
    )


async def stories_archive(
    invoker: Invoker, peer: Target, *, offset_id: int = 0, limit: int = 100
) -> Any:
    """Our own expired stories, which only we can see."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stories.GetStoriesArchive(
            peer=where, offset_id=offset_id, limit=limit
        )
    )


async def read_stories(invoker: Invoker, peer: Target, max_id: int) -> list[int]:
    """Mark everything up to a story as seen."""
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.stories.ReadStories(peer=where, max_id=max_id)
    )
    return list(answer)


async def story_views(invoker: Invoker, peer: Target, ids: list[int]) -> Any:
    """Who has seen our stories, and how many."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.stories.GetStoriesViews(peer=where, id=list(ids))
    )
