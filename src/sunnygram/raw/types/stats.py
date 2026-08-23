# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the stats namespace.

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


class BroadcastStats(TLObject):
    """The TL type stats.broadcastStats#396ca5fc, a form of stats.BroadcastStats."""

    __slots__ = ("period", "followers", "views_per_post", "shares_per_post", "reactions_per_post", "views_per_story", "shares_per_story", "reactions_per_story", "enabled_notifications", "growth_graph", "followers_graph", "mute_graph", "top_hours_graph", "interactions_graph", "iv_interactions_graph", "views_by_source_graph", "new_followers_by_source_graph", "languages_graph", "reactions_by_emotion_graph", "story_interactions_graph", "story_reactions_by_emotion_graph", "recent_posts_interactions",)

    ID = 0x396CA5FC
    QUALNAME = "types.stats.BroadcastStats"

    def __init__(
        self,
        *,
        period: base.StatsDateRangeDays,
        followers: base.StatsAbsValueAndPrev,
        views_per_post: base.StatsAbsValueAndPrev,
        shares_per_post: base.StatsAbsValueAndPrev,
        reactions_per_post: base.StatsAbsValueAndPrev,
        views_per_story: base.StatsAbsValueAndPrev,
        shares_per_story: base.StatsAbsValueAndPrev,
        reactions_per_story: base.StatsAbsValueAndPrev,
        enabled_notifications: base.StatsPercentValue,
        growth_graph: base.StatsGraph,
        followers_graph: base.StatsGraph,
        mute_graph: base.StatsGraph,
        top_hours_graph: base.StatsGraph,
        interactions_graph: base.StatsGraph,
        iv_interactions_graph: base.StatsGraph,
        views_by_source_graph: base.StatsGraph,
        new_followers_by_source_graph: base.StatsGraph,
        languages_graph: base.StatsGraph,
        reactions_by_emotion_graph: base.StatsGraph,
        story_interactions_graph: base.StatsGraph,
        story_reactions_by_emotion_graph: base.StatsGraph,
        recent_posts_interactions: list[base.PostInteractionCounters],
    ) -> None:
        self.period = period
        self.followers = followers
        self.views_per_post = views_per_post
        self.shares_per_post = shares_per_post
        self.reactions_per_post = reactions_per_post
        self.views_per_story = views_per_story
        self.shares_per_story = shares_per_story
        self.reactions_per_story = reactions_per_story
        self.enabled_notifications = enabled_notifications
        self.growth_graph = growth_graph
        self.followers_graph = followers_graph
        self.mute_graph = mute_graph
        self.top_hours_graph = top_hours_graph
        self.interactions_graph = interactions_graph
        self.iv_interactions_graph = iv_interactions_graph
        self.views_by_source_graph = views_by_source_graph
        self.new_followers_by_source_graph = new_followers_by_source_graph
        self.languages_graph = languages_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph
        self.story_interactions_graph = story_interactions_graph
        self.story_reactions_by_emotion_graph = story_reactions_by_emotion_graph
        self.recent_posts_interactions = recent_posts_interactions

    def write_body(self, w: TLWriter) -> None:
        self.period.write(w)
        self.followers.write(w)
        self.views_per_post.write(w)
        self.shares_per_post.write(w)
        self.reactions_per_post.write(w)
        self.views_per_story.write(w)
        self.shares_per_story.write(w)
        self.reactions_per_story.write(w)
        self.enabled_notifications.write(w)
        self.growth_graph.write(w)
        self.followers_graph.write(w)
        self.mute_graph.write(w)
        self.top_hours_graph.write(w)
        self.interactions_graph.write(w)
        self.iv_interactions_graph.write(w)
        self.views_by_source_graph.write(w)
        self.new_followers_by_source_graph.write(w)
        self.languages_graph.write(w)
        self.reactions_by_emotion_graph.write(w)
        self.story_interactions_graph.write(w)
        self.story_reactions_by_emotion_graph.write(w)
        w.write_vector(self.recent_posts_interactions)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        period = r.read_object()
        followers = r.read_object()
        views_per_post = r.read_object()
        shares_per_post = r.read_object()
        reactions_per_post = r.read_object()
        views_per_story = r.read_object()
        shares_per_story = r.read_object()
        reactions_per_story = r.read_object()
        enabled_notifications = r.read_object()
        growth_graph = r.read_object()
        followers_graph = r.read_object()
        mute_graph = r.read_object()
        top_hours_graph = r.read_object()
        interactions_graph = r.read_object()
        iv_interactions_graph = r.read_object()
        views_by_source_graph = r.read_object()
        new_followers_by_source_graph = r.read_object()
        languages_graph = r.read_object()
        reactions_by_emotion_graph = r.read_object()
        story_interactions_graph = r.read_object()
        story_reactions_by_emotion_graph = r.read_object()
        recent_posts_interactions = r.read_vector()
        self = cls.__new__(cls)
        self.period = period
        self.followers = followers
        self.views_per_post = views_per_post
        self.shares_per_post = shares_per_post
        self.reactions_per_post = reactions_per_post
        self.views_per_story = views_per_story
        self.shares_per_story = shares_per_story
        self.reactions_per_story = reactions_per_story
        self.enabled_notifications = enabled_notifications
        self.growth_graph = growth_graph
        self.followers_graph = followers_graph
        self.mute_graph = mute_graph
        self.top_hours_graph = top_hours_graph
        self.interactions_graph = interactions_graph
        self.iv_interactions_graph = iv_interactions_graph
        self.views_by_source_graph = views_by_source_graph
        self.new_followers_by_source_graph = new_followers_by_source_graph
        self.languages_graph = languages_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph
        self.story_interactions_graph = story_interactions_graph
        self.story_reactions_by_emotion_graph = story_reactions_by_emotion_graph
        self.recent_posts_interactions = recent_posts_interactions
        return self


class MegagroupStats(TLObject):
    """The TL type stats.megagroupStats#ef7ff916, a form of stats.MegagroupStats."""

    __slots__ = ("period", "members", "messages", "viewers", "posters", "growth_graph", "members_graph", "new_members_by_source_graph", "languages_graph", "messages_graph", "actions_graph", "top_hours_graph", "weekdays_graph", "top_posters", "top_admins", "top_inviters", "users",)

    ID = 0xEF7FF916
    QUALNAME = "types.stats.MegagroupStats"

    def __init__(
        self,
        *,
        period: base.StatsDateRangeDays,
        members: base.StatsAbsValueAndPrev,
        messages: base.StatsAbsValueAndPrev,
        viewers: base.StatsAbsValueAndPrev,
        posters: base.StatsAbsValueAndPrev,
        growth_graph: base.StatsGraph,
        members_graph: base.StatsGraph,
        new_members_by_source_graph: base.StatsGraph,
        languages_graph: base.StatsGraph,
        messages_graph: base.StatsGraph,
        actions_graph: base.StatsGraph,
        top_hours_graph: base.StatsGraph,
        weekdays_graph: base.StatsGraph,
        top_posters: list[base.StatsGroupTopPoster],
        top_admins: list[base.StatsGroupTopAdmin],
        top_inviters: list[base.StatsGroupTopInviter],
        users: list[base.User],
    ) -> None:
        self.period = period
        self.members = members
        self.messages = messages
        self.viewers = viewers
        self.posters = posters
        self.growth_graph = growth_graph
        self.members_graph = members_graph
        self.new_members_by_source_graph = new_members_by_source_graph
        self.languages_graph = languages_graph
        self.messages_graph = messages_graph
        self.actions_graph = actions_graph
        self.top_hours_graph = top_hours_graph
        self.weekdays_graph = weekdays_graph
        self.top_posters = top_posters
        self.top_admins = top_admins
        self.top_inviters = top_inviters
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.period.write(w)
        self.members.write(w)
        self.messages.write(w)
        self.viewers.write(w)
        self.posters.write(w)
        self.growth_graph.write(w)
        self.members_graph.write(w)
        self.new_members_by_source_graph.write(w)
        self.languages_graph.write(w)
        self.messages_graph.write(w)
        self.actions_graph.write(w)
        self.top_hours_graph.write(w)
        self.weekdays_graph.write(w)
        w.write_vector(self.top_posters)
        w.write_vector(self.top_admins)
        w.write_vector(self.top_inviters)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        period = r.read_object()
        members = r.read_object()
        messages = r.read_object()
        viewers = r.read_object()
        posters = r.read_object()
        growth_graph = r.read_object()
        members_graph = r.read_object()
        new_members_by_source_graph = r.read_object()
        languages_graph = r.read_object()
        messages_graph = r.read_object()
        actions_graph = r.read_object()
        top_hours_graph = r.read_object()
        weekdays_graph = r.read_object()
        top_posters = r.read_vector()
        top_admins = r.read_vector()
        top_inviters = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.period = period
        self.members = members
        self.messages = messages
        self.viewers = viewers
        self.posters = posters
        self.growth_graph = growth_graph
        self.members_graph = members_graph
        self.new_members_by_source_graph = new_members_by_source_graph
        self.languages_graph = languages_graph
        self.messages_graph = messages_graph
        self.actions_graph = actions_graph
        self.top_hours_graph = top_hours_graph
        self.weekdays_graph = weekdays_graph
        self.top_posters = top_posters
        self.top_admins = top_admins
        self.top_inviters = top_inviters
        self.users = users
        return self


class MessageStats(TLObject):
    """The TL type stats.messageStats#7fe91c14, a form of stats.MessageStats."""

    __slots__ = ("views_graph", "reactions_by_emotion_graph",)

    ID = 0x7FE91C14
    QUALNAME = "types.stats.MessageStats"

    def __init__(
        self,
        *,
        views_graph: base.StatsGraph,
        reactions_by_emotion_graph: base.StatsGraph,
    ) -> None:
        self.views_graph = views_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph

    def write_body(self, w: TLWriter) -> None:
        self.views_graph.write(w)
        self.reactions_by_emotion_graph.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        views_graph = r.read_object()
        reactions_by_emotion_graph = r.read_object()
        self = cls.__new__(cls)
        self.views_graph = views_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph
        return self


class StoryStats(TLObject):
    """The TL type stats.storyStats#50cd067c, a form of stats.StoryStats."""

    __slots__ = ("views_graph", "reactions_by_emotion_graph",)

    ID = 0x50CD067C
    QUALNAME = "types.stats.StoryStats"

    def __init__(
        self,
        *,
        views_graph: base.StatsGraph,
        reactions_by_emotion_graph: base.StatsGraph,
    ) -> None:
        self.views_graph = views_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph

    def write_body(self, w: TLWriter) -> None:
        self.views_graph.write(w)
        self.reactions_by_emotion_graph.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        views_graph = r.read_object()
        reactions_by_emotion_graph = r.read_object()
        self = cls.__new__(cls)
        self.views_graph = views_graph
        self.reactions_by_emotion_graph = reactions_by_emotion_graph
        return self


class PublicForwards(TLObject):
    """The TL type stats.publicForwards#93037e20, a form of stats.PublicForwards."""

    __slots__ = ("count", "forwards", "next_offset", "chats", "users",)

    ID = 0x93037E20
    QUALNAME = "types.stats.PublicForwards"

    def __init__(
        self,
        *,
        count: int,
        forwards: list[base.PublicForward],
        next_offset: str | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.forwards = forwards
        self.next_offset = next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.forwards)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        forwards = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.forwards = forwards
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        return self


class PollStats(TLObject):
    """The TL type stats.pollStats#2999beed, a form of stats.PollStats."""

    __slots__ = ("votes_graph",)

    ID = 0x2999BEED
    QUALNAME = "types.stats.PollStats"

    def __init__(
        self,
        *,
        votes_graph: base.StatsGraph,
    ) -> None:
        self.votes_graph = votes_graph

    def write_body(self, w: TLWriter) -> None:
        self.votes_graph.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        votes_graph = r.read_object()
        self = cls.__new__(cls)
        self.votes_graph = votes_graph
        return self
