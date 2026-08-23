"""Stories: posting them, reading them, and the placeholder problem.

Two things here are worth a test rather than a glance. The first is privacy: a
story is sent with a required list of rules, an empty list means nobody, and so
the failure mode of forgetting is a story that posts successfully and is seen
by no one. The second is that a list of stories routinely contains things that
are not stories, because Telegram sends a placeholder where one is hidden from
this account and another where one has been deleted.
"""

from __future__ import annotations

import pytest

from mtproto_server import recording
from sunnygram.errors import SunnygramError
from sunnygram.methods import (
    AUDIENCES,
    audience,
    delete_stories,
    edit_story,
    get_stories,
    pin_stories,
    read_stories,
    send_story,
)
from sunnygram.raw import functions, types
from sunnygram.types import Story

PHOTO = types.InputMediaUploadedPhoto(
    file=types.InputFile(id=1, parts=1, name="s.jpg", md5_checksum="")
)


def a_story(id: int, caption: str = "hi", views: int = 0) -> types.StoryItem:
    return types.StoryItem(
        id=id,
        date=1700000000,
        expire_date=1700086400,
        caption=caption,
        media=types.MessageMediaEmpty(),
        views=types.StoryViews(views_count=views),
    )


class TestWhoCanSeeIt:
    @pytest.mark.parametrize("who", AUDIENCES)
    def test_every_named_audience_builds(self, who):
        assert isinstance(audience(who), list)

    def test_everyone_is_the_allow_all_rule(self):
        rules = audience("everyone")
        assert len(rules) == 1
        assert isinstance(rules[0], types.InputPrivacyValueAllowAll)

    def test_nobody_is_an_empty_list(self):
        """Which is also what forgetting to say produces on the wire.

        Naming it is the point of this function: the caller who wants nobody
        gets it deliberately, and the caller who says nothing gets everyone.
        """
        assert audience("nobody") == []

    def test_an_unknown_audience_is_refused_rather_than_guessed(self):
        with pytest.raises(ValueError, match="audience must be one of"):
            audience("friends-of-friends")


class TestPosting:
    async def test_the_default_audience_is_everyone_not_nobody(self):
        async with recording() as (invoker, server):
            await send_story(invoker, types.InputPeerSelf(), PHOTO)
            sent = server.only(functions.stories.SendStory)
            assert len(sent.privacy_rules) == 1
            assert isinstance(sent.privacy_rules[0], types.InputPrivacyValueAllowAll)

    async def test_an_audience_by_name_goes_out_as_its_rule(self):
        async with recording() as (invoker, server):
            await send_story(
                invoker, types.InputPeerSelf(), PHOTO, privacy="close_friends"
            )
            sent = server.only(functions.stories.SendStory)
            assert isinstance(
                sent.privacy_rules[0], types.InputPrivacyValueAllowCloseFriends
            )

    async def test_rules_can_be_given_directly(self):
        async with recording() as (invoker, server):
            given = [types.InputPrivacyValueAllowContacts()]
            await send_story(invoker, types.InputPeerSelf(), PHOTO, privacy=given)
            sent = server.only(functions.stories.SendStory)
            assert isinstance(
                sent.privacy_rules[0], types.InputPrivacyValueAllowContacts
            )

    async def test_a_period_telegram_does_not_allow_is_refused_here(self):
        """Rather than sent and rejected, which costs a round trip to learn."""
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="period must be one of"):
                await send_story(
                    invoker, types.InputPeerSelf(), PHOTO, period=3600
                )
            assert server.queries == []

    async def test_an_allowed_period_goes_out(self):
        async with recording() as (invoker, server):
            await send_story(
                invoker, types.InputPeerSelf(), PHOTO, period=48 * 3600
            )
            assert server.only(functions.stories.SendStory).period == 48 * 3600

    async def test_every_story_carries_a_fresh_random_id(self):
        async with recording() as (invoker, server):
            await send_story(invoker, types.InputPeerSelf(), PHOTO)
            await send_story(invoker, types.InputPeerSelf(), PHOTO)
            ids = [one.random_id for one in server.all(functions.stories.SendStory)]
            assert len(set(ids)) == 2
            assert all(-(2**63) <= value < 2**63 for value in ids)


class TestChanging:
    async def test_editing_nothing_is_refused_before_it_is_sent(self):
        async with recording() as (invoker, server):
            with pytest.raises(SunnygramError, match="needs media, a caption"):
                await edit_story(invoker, types.InputPeerSelf(), 1)
            assert server.queries == []

    async def test_editing_a_caption_leaves_the_media_alone(self):
        async with recording() as (invoker, server):
            await edit_story(invoker, types.InputPeerSelf(), 4, caption="new")
            asked = server.only(functions.stories.EditStory)
            assert asked.caption == "new"
            assert asked.media is None
            assert asked.id == 4

    async def test_deleting_answers_with_what_went(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: [3, 4]
            assert await delete_stories(invoker, types.InputPeerSelf(), [3, 4, 5]) == [
                3,
                4,
            ]

    async def test_pinning_says_which_way(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: [1]
            await pin_stories(invoker, types.InputPeerSelf(), [1], pinned=False)
            assert server.only(functions.stories.TogglePinned).pinned is False

    async def test_reading_marks_up_to_an_id(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: [1, 2]
            await read_stories(invoker, types.InputPeerSelf(), 9)
            assert server.only(functions.stories.ReadStories).max_id == 9

    async def test_fetching_by_id_asks_for_those_ids(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.stories.Stories(
                count=1, stories=[a_story(6)], chats=[], users=[]
            )
            answer = await get_stories(invoker, types.InputPeerSelf(), [6])
            assert len(answer.stories) == 1
            assert server.only(functions.stories.GetStoriesByID).id == [6]


class TestThePlaceholders:
    """The three constructors, only one of which is a story."""

    def test_a_real_story_reads_its_fields(self):
        wrapped = Story.from_raw(a_story(1, "caption", views=12))
        assert wrapped is not None
        assert wrapped.id == 1
        assert wrapped.caption == "caption"
        assert wrapped.views == 12
        assert wrapped.available is True
        assert wrapped.has_media is True

    def test_a_hidden_story_is_a_placeholder_that_says_so(self):
        raw = types.StoryItemSkipped(id=2, date=1, expire_date=2, close_friends=True)
        wrapped = Story.from_raw(raw)
        assert wrapped is not None
        assert wrapped.id == 2
        assert wrapped.available is False
        assert wrapped.close_friends is True
        assert wrapped.has_media is False

    def test_a_deleted_story_is_nothing_at_all(self):
        """An object with every field empty would be a worse answer."""
        assert Story.from_raw(types.StoryItemDeleted(id=3)) is None

    def test_anything_else_is_not_a_story(self):
        assert Story.from_raw(None) is None
        assert Story.from_raw(types.MessageMediaEmpty()) is None


class TestTheEvent:
    def test_a_story_update_has_its_own_kind(self):
        from sunnygram.dispatcher import KINDS, _READINGS

        kind, _ = _READINGS[types.UpdateStory]
        assert kind == "story"
        assert "story" in KINDS
