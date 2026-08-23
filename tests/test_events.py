"""Every kind of event a handler can ask for, and the wrapper it arrives as.

The dispatcher's job here is narrow and easy to get subtly wrong: one update
becomes one reading, that reading goes to the handlers that asked for that kind
and to nobody else, and the wrapper reads the right fields off the right
constructor. Telegram spells several of these two or three different ways for
what is the same event to a program, so most of what follows is one test per
spelling.

Two of these are about what must not happen. The table and the list of kinds
must not drift apart, because a kind in one and not the other is a decorator
that quietly never fires. And a reading nobody asked for must not be built,
because wrapping a message costs about what decoding it did and a program with
one inline handler has no reason to pay it for every message in every chat.
"""

from __future__ import annotations

from typing import Any

import pytest

from sunnygram import filters
from sunnygram.dispatcher import KINDS, _READINGS, Dispatcher, Handler
from sunnygram.raw import types
from sunnygram.storage import PeerKind
from sunnygram.peers import mark_id
from sunnygram.types import (
    Blocked,
    ChosenResult,
    DeletedMessages,
    InlineQuery,
    JoinRequest,
    MemberStatus,
    MemberUpdate,
    Poll,
    PollVote,
    ReactionUpdate,
    Status,
    Stopped,
    Typing,
)
from sunnygram.updates import Event

CHANNEL = 1234
MARKED_CHANNEL = mark_id(CHANNEL, PeerKind.CHANNEL)
THEM = 1001
DATE = 1700000000


def somebody(user_id: int = THEM, username: str = "someone") -> types.User:
    return types.User(id=user_id, first_name="Some", username=username)


def an_event(update: Any, *, users: dict[int, Any] | None = None) -> Event:
    return Event(update=update, users=users or {}, chats={})


async def caught(update: Any, kind: str, **event: Any) -> list[Any]:
    """Feed one update and hand back what a handler for that kind was given."""
    seen: list[Any] = []

    async def callback(client: Any, value: Any) -> None:
        seen.append(value)

    dispatcher = Dispatcher()
    dispatcher.add(Handler(callback=callback, kind=kind))  # type: ignore[arg-type]
    await dispatcher.feed(None, an_event(update, **event))
    return seen


class TestTheTableAndTheKinds:
    def test_every_kind_the_table_produces_is_a_kind(self):
        # A kind in the table and not in the Literal is a decorator that cannot
        # be written; one in the Literal with nothing producing it is a handler
        # that never fires. Both are silent, so they are checked rather than
        # remembered.
        assert {kind for kind, _ in _READINGS.values()} <= set(KINDS)

    def test_every_kind_is_produced_by_something(self):
        # raw and album are the two that no single update produces: raw is
        # every update, and an album is several messages noticed together.
        produced = {kind for kind, _ in _READINGS.values()} | {"raw", "album"}
        assert produced == set(KINDS)

    def test_the_client_has_a_decorator_for_each_one(self):
        # Every kind is reachable by a decorator, so none of them is a kind
        # only add_handler can ask for. The one name that is not on_<kind> is
        # the press, which was called on_callback_query before there were
        # enough kinds for a rule about it.
        from sunnygram.client import Client

        named = {"callback": "on_callback_query"}
        missing = [
            kind
            for kind in KINDS
            if kind not in ("raw", "album")
            and not hasattr(Client, named.get(kind, f"on_{kind}"))
        ]
        assert missing == []


class TestNothingIsBuiltUnasked:
    async def test_a_message_is_not_wrapped_for_a_program_that_wants_queries(self):
        wrapped: list[Any] = []

        class Counting:
            def wrap_message(self, raw: Any, **rest: Any) -> Any:
                wrapped.append(raw)
                return None

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=_nothing, kind="inline_query"))
        message = types.Message(
            id=1, peer_id=types.PeerUser(user_id=THEM), date=DATE, message="hi"
        )
        await dispatcher.feed(
            Counting(),
            an_event(types.UpdateNewMessage(message=message, pts=1, pts_count=1)),
        )
        assert wrapped == []

    async def test_an_update_whose_reading_comes_to_nothing_is_dropped(self):
        # A deleted message arrives as an empty one, which wraps to nothing.
        # Offering that around would hand handlers a None to guard against.
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=callback, kind="message"))
        await dispatcher.feed(
            None,
            an_event(
                types.UpdateNewMessage(
                    message=types.MessageEmpty(id=3), pts=1, pts_count=1
                )
            ),
        )
        assert seen == []
        assert dispatcher.errors == 0

    async def test_an_update_with_no_friendly_reading_still_reaches_raw(self):
        # Telegram has hundreds of update types and far fewer friendly readings, so the
        # escape hatch is the normal way to meet most of them.
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=callback, kind="raw"))
        dispatcher.add(Handler(callback=callback, kind="message"))
        await dispatcher.feed(
            None, an_event(types.UpdateDraftMessage(peer=types.PeerUser(user_id=THEM), draft=types.DraftMessageEmpty()))
        )
        assert [type(one).__name__ for one in seen] == ["Event"]

    async def test_and_is_wrapped_for_a_program_that_wants_messages(self):
        wrapped: list[Any] = []

        class Counting:
            def wrap_message(self, raw: Any, **rest: Any) -> Any:
                wrapped.append(raw)
                return None

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=_nothing, kind="message"))
        message = types.Message(
            id=1, peer_id=types.PeerUser(user_id=THEM), date=DATE, message="hi"
        )
        await dispatcher.feed(
            Counting(),
            an_event(types.UpdateNewMessage(message=message, pts=1, pts_count=1)),
        )
        assert len(wrapped) == 1


class TestInlineQueries:
    def a_query(self, text: str = "cats", **rest: Any) -> types.UpdateBotInlineQuery:
        return types.UpdateBotInlineQuery(
            query_id=42,
            user_id=THEM,
            query=text,
            offset=rest.pop("offset", ""),
            peer_type=rest.pop("peer_type", None),
        )

    async def test_a_query_reaches_an_inline_handler(self):
        seen = await caught(
            self.a_query(), "inline_query", users={THEM: somebody()}
        )
        assert len(seen) == 1
        asked = seen[0]
        assert isinstance(asked, InlineQuery)
        assert asked.id == 42
        assert asked.text == "cats"
        assert asked.sender is not None and asked.sender.username == "someone"

    async def test_where_it_was_typed_is_a_word(self):
        seen = await caught(
            self.a_query(peer_type=types.InlineQueryPeerTypeMegagroup()),
            "inline_query",
        )
        assert seen[0].where == "supergroup"

    async def test_a_query_with_no_peer_type_says_nothing_about_where(self):
        seen = await caught(self.a_query(), "inline_query")
        assert seen[0].where == ""

    async def test_the_offset_is_carried_for_paging(self):
        seen = await caught(self.a_query(offset="30"), "inline_query")
        assert seen[0].offset == "30"

    async def test_a_message_handler_does_not_see_one(self):
        seen = await caught(self.a_query(), "message")
        assert seen == []

    async def test_the_query_filter_reads_what_was_typed(self):
        found: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            found.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=callback,
                kind="inline_query",
                filters=filters.query("weather"),
            )
        )
        await dispatcher.feed(None, an_event(self.a_query("cats")))
        await dispatcher.feed(None, an_event(self.a_query("Weather in Rome")))
        assert [one.text for one in found] == ["Weather in Rome"]

    async def test_the_empty_query_is_its_own_question(self):
        found: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            found.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=callback, kind="inline_query", filters=filters.query(empty=True)
            )
        )
        await dispatcher.feed(None, an_event(self.a_query("cats")))
        await dispatcher.feed(None, an_event(self.a_query("")))
        assert [one.text for one in found] == [""]

    async def test_naming_nothing_matches_every_query(self):
        # The catch-all a bot needs, because a query that reaches no handler is
        # a query nothing answers, and that is a panel loading forever.
        found: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            found.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=callback, kind="inline_query", filters=filters.query())
        )
        await dispatcher.feed(None, an_event(self.a_query("anything at all")))
        assert [one.text for one in found] == ["anything at all"]

    async def test_regex_works_on_a_query_too(self):
        found: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            found.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=callback,
                kind="inline_query",
                filters=filters.regex(r"^page (\d+)$"),
            )
        )
        await dispatcher.feed(None, an_event(self.a_query("page 7")))
        assert found[0].match.group(1) == "7"

    async def test_a_query_with_no_client_says_so_rather_than_failing_oddly(self):
        asked = InlineQuery(id=1)
        with pytest.raises(Exception, match="not bound to a client"):
            await asked.answer([])


class TestChosenResults:
    async def test_a_chosen_result_reaches_its_handler(self):
        seen = await caught(
            types.UpdateBotInlineSend(
                user_id=THEM, query="cats", id="result-3", msg_id=None
            ),
            "chosen_result",
            users={THEM: somebody()},
        )
        chosen = seen[0]
        assert isinstance(chosen, ChosenResult)
        assert chosen.id == "result-3"
        assert chosen.text == "cats"
        assert chosen.editable is False

    async def test_one_with_a_keyboard_can_be_edited(self):
        seen = await caught(
            types.UpdateBotInlineSend(
                user_id=THEM,
                query="cats",
                id="r",
                msg_id=types.InputBotInlineMessageID(dc_id=2, id=5, access_hash=6),
            ),
            "chosen_result",
        )
        assert seen[0].editable is True

    async def test_one_without_a_keyboard_says_why_it_cannot_be(self):
        chosen = ChosenResult(id="r", client=object())
        with pytest.raises(Exception, match="issued no id for the message"):
            await chosen.edit("later")


class TestChatMembers:
    def a_change(self, before: Any, after: Any, **rest: Any) -> Any:
        return types.UpdateChannelParticipant(
            channel_id=CHANNEL,
            date=DATE,
            actor_id=rest.pop("actor", THEM),
            user_id=THEM,
            prev_participant=before,
            new_participant=after,
            invite=rest.pop("invite", None),
            qts=7,
        )

    def member(self) -> Any:
        return types.ChannelParticipant(user_id=THEM, date=DATE)

    def admin(self) -> Any:
        return types.ChannelParticipantAdmin(
            user_id=THEM,
            promoted_by=999,
            date=DATE,
            admin_rights=types.ChatAdminRights(ban_users=True),
        )

    def banned(self) -> Any:
        return types.ChannelParticipantBanned(
            left=True,
            peer=types.PeerUser(user_id=THEM),
            kicked_by=999,
            date=DATE,
            banned_rights=types.ChatBannedRights(until_date=0, view_messages=True),
        )

    async def test_somebody_joining(self):
        seen = await caught(self.a_change(None, self.member()), "chat_member")
        change = seen[0]
        assert isinstance(change, MemberUpdate)
        assert change.joined and change.what == "joined"
        assert change.by_self is True

    async def test_somebody_being_added_is_not_somebody_joining_alone(self):
        seen = await caught(
            self.a_change(None, self.member(), actor=999), "chat_member"
        )
        assert seen[0].joined and seen[0].by_self is False

    async def test_somebody_leaving(self):
        seen = await caught(self.a_change(self.member(), None), "chat_member")
        assert seen[0].left and seen[0].what == "left"

    async def test_somebody_being_banned_is_said_as_banned(self):
        seen = await caught(self.a_change(self.member(), self.banned()), "chat_member")
        change = seen[0]
        assert change.banned and change.what == "banned"
        assert change.left is True
        assert change.status is MemberStatus.BANNED

    async def test_somebody_being_promoted(self):
        seen = await caught(self.a_change(self.member(), self.admin()), "chat_member")
        assert seen[0].promoted and seen[0].what == "promoted"

    async def test_somebody_being_demoted(self):
        seen = await caught(self.a_change(self.admin(), self.member()), "chat_member")
        assert seen[0].demoted and seen[0].what == "demoted"

    async def test_the_invite_link_they_came_in_through(self):
        invite = types.ChatInviteExported(
            link="https://t.me/+abc", admin_id=999, date=DATE
        )
        seen = await caught(
            self.a_change(None, self.member(), invite=invite), "chat_member"
        )
        assert seen[0].invite_link == "https://t.me/+abc"

    async def test_the_chat_is_named_the_way_resolve_takes_it_back(self):
        # The trap this closes: a bare channel id is a valid user id, so a
        # greeter answering into update.chat_id would write to a stranger.
        seen = await caught(self.a_change(None, self.member()), "chat_member")
        assert seen[0].chat_id == MARKED_CHANNEL

    async def test_a_basic_group_is_the_same_event(self):
        seen = await caught(
            types.UpdateChatParticipant(
                chat_id=55,
                date=DATE,
                actor_id=THEM,
                user_id=THEM,
                prev_participant=None,
                new_participant=types.ChatParticipant(
                    user_id=THEM, inviter_id=THEM, date=DATE
                ),
                invite=None,
                qts=8,
            ),
            "chat_member",
        )
        assert seen[0].joined
        assert seen[0].chat_id == mark_id(55, PeerKind.CHAT)


class TestJoinRequests:
    def a_request(self) -> Any:
        return types.UpdateBotChatInviteRequester(
            peer=types.PeerChannel(channel_id=CHANNEL),
            date=DATE,
            user_id=THEM,
            about="let me in please",
            invite=types.ChatInviteExported(
                link="https://t.me/+xyz", admin_id=999, date=DATE
            ),
            qts=9,
        )

    async def test_a_request_reaches_its_handler(self):
        seen = await caught(
            self.a_request(), "join_request", users={THEM: somebody()}
        )
        asked = seen[0]
        assert isinstance(asked, JoinRequest)
        assert asked.chat_id == MARKED_CHANNEL
        assert asked.about == "let me in please"
        assert asked.invite_link == "https://t.me/+xyz"
        assert asked.sender is not None and asked.sender.username == "someone"

    async def test_approving_and_declining_are_the_same_call_either_way(self):
        called: list[Any] = []

        class Acting:
            async def approve_join_request(
                self, peer: Any, user: Any, *, approved: bool = True
            ) -> None:
                called.append((peer, user, approved))

        asked = JoinRequest(chat_id=MARKED_CHANNEL, user_id=THEM, client=Acting())
        await asked.approve()
        await asked.decline()
        assert called == [
            (MARKED_CHANNEL, THEM, True),
            (MARKED_CHANNEL, THEM, False),
        ]


class TestDeletedMessages:
    async def test_a_channel_deletion_says_where(self):
        seen = await caught(
            types.UpdateDeleteChannelMessages(
                channel_id=CHANNEL, messages=[4, 5], pts=1, pts_count=2
            ),
            "deleted",
        )
        gone = seen[0]
        assert isinstance(gone, DeletedMessages)
        assert gone.ids == (4, 5)
        assert gone.located and gone.chat_id == MARKED_CHANNEL

    async def test_an_ordinary_deletion_does_not_pretend_to(self):
        # Telegram genuinely does not say which chat, so this says so rather
        # than handing back a plausible wrong number.
        seen = await caught(
            types.UpdateDeleteMessages(messages=[9], pts=1, pts_count=1), "deleted"
        )
        assert seen[0].ids == (9,)
        assert seen[0].located is False
        assert seen[0].chat_id == 0


class TestReactions:
    async def test_the_totals_reading_a_user_account_gets(self):
        seen = await caught(
            types.UpdateMessageReactions(
                peer=types.PeerChannel(channel_id=CHANNEL),
                msg_id=12,
                reactions=types.MessageReactions(
                    results=[
                        types.ReactionCount(
                            reaction=types.ReactionEmoji(emoticon="👍"), count=4
                        ),
                        types.ReactionCount(
                            reaction=types.ReactionCustomEmoji(document_id=99),
                            count=1,
                            chosen_order=0,
                        ),
                    ]
                ),
            ),
            "reaction",
        )
        change = seen[0]
        assert isinstance(change, ReactionUpdate)
        assert change.by_person is False
        assert change.counts == {"👍": 4, 99: 1}
        assert change.total == 5
        assert change.mine == (99,)

    async def test_the_one_person_reading_a_bot_gets(self):
        seen = await caught(
            types.UpdateBotMessageReaction(
                peer=types.PeerChannel(channel_id=CHANNEL),
                msg_id=12,
                date=DATE,
                actor=types.PeerUser(user_id=THEM),
                old_reactions=[types.ReactionEmoji(emoticon="👍")],
                new_reactions=[types.ReactionEmoji(emoticon="❤")],
                qts=3,
            ),
            "reaction",
        )
        change = seen[0]
        assert change.by_person is True
        assert change.actor_id == mark_id(THEM, PeerKind.USER)
        assert change.added == ("❤",)
        assert change.removed == ("👍",)

    async def test_the_bot_totals_reading_is_totals_too(self):
        seen = await caught(
            types.UpdateBotMessageReactions(
                peer=types.PeerChannel(channel_id=CHANNEL),
                msg_id=12,
                date=DATE,
                reactions=[
                    types.ReactionCount(
                        reaction=types.ReactionEmoji(emoticon="🔥"), count=2
                    )
                ],
                qts=4,
            ),
            "reaction",
        )
        assert seen[0].by_person is False
        assert seen[0].counts == {"🔥": 2}

    async def test_a_paid_reaction_is_named_rather_than_invented(self):
        seen = await caught(
            types.UpdateBotMessageReactions(
                peer=types.PeerChannel(channel_id=CHANNEL),
                msg_id=1,
                date=DATE,
                reactions=[
                    types.ReactionCount(reaction=types.ReactionPaid(), count=3)
                ],
                qts=5,
            ),
            "reaction",
        )
        assert seen[0].counts == {"paid": 3}


class TestPolls:
    def a_poll(self, *, with_poll: bool = True, **rest: Any) -> Any:
        poll = types.Poll(
            id=77,
            hash=0,
            question=types.TextWithEntities(text="Lunch?", entities=[]),
            answers=[
                types.PollAnswer(
                    text=types.TextWithEntities(text="Yes", entities=[]),
                    option=b"\x00",
                ),
                types.PollAnswer(
                    text=types.TextWithEntities(text="No", entities=[]),
                    option=b"\x01",
                ),
            ],
            public_voters=True,
        )
        return types.UpdateMessagePoll(
            poll_id=77,
            poll=poll if with_poll else None,
            results=types.PollResults(
                results=[
                    types.PollAnswerVoters(option=b"\x00", voters=3),
                    types.PollAnswerVoters(option=b"\x01", voters=1),
                ],
                total_voters=4,
            ),
            peer=rest.pop("peer", None),
            msg_id=rest.pop("msg_id", None),
        )

    async def test_a_poll_with_the_question_in_it(self):
        seen = await caught(self.a_poll(), "poll")
        poll = seen[0]
        assert isinstance(poll, Poll)
        assert poll.known and poll.question == "Lunch?"
        assert [one.text for one in poll.answers] == ["Yes", "No"]
        assert [one.voters for one in poll.answers] == [3, 1]
        assert poll.total_voters == 4
        assert poll.anonymous is False

    async def test_the_usual_case_where_only_the_results_arrive(self):
        seen = await caught(self.a_poll(with_poll=False), "poll")
        poll = seen[0]
        assert poll.known is False
        assert poll.total_voters == 4
        # The votes are still readable, by position, which is what a program
        # counting them wants.
        assert [(one.position, one.voters) for one in poll.answers] == [(0, 3), (1, 1)]

    async def test_the_winner_and_a_tie(self):
        seen = await caught(self.a_poll(), "poll")
        assert seen[0].winner is not None and seen[0].winner.text == "Yes"

    async def test_a_poll_that_did_not_say_where_it_is_says_so(self):
        seen = await caught(self.a_poll(), "poll")
        assert seen[0].located is False
        with pytest.raises(Exception, match="did not say which message"):
            await seen[0].close()

    async def test_a_poll_that_did_say_where_it_is(self):
        seen = await caught(
            self.a_poll(peer=types.PeerChannel(channel_id=CHANNEL), msg_id=5), "poll"
        )
        assert seen[0].located
        assert (seen[0].chat_id, seen[0].message_id) == (MARKED_CHANNEL, 5)

    async def test_a_vote_reaches_its_own_handler(self):
        seen = await caught(
            types.UpdateMessagePollVote(
                poll_id=77,
                peer=types.PeerUser(user_id=THEM),
                options=[b"\x01"],
                positions=[1],
                qts=6,
            ),
            "poll_vote",
        )
        vote = seen[0]
        assert isinstance(vote, PollVote)
        assert vote.poll_id == 77
        assert vote.options == (1,)
        assert vote.retracted is False

    async def test_a_vote_read_off_the_option_bytes_when_it_has_to_be(self):
        seen = await caught(
            types.UpdateMessagePollVote(
                poll_id=77,
                peer=types.PeerUser(user_id=THEM),
                options=[b"\x02"],
                positions=[],
                qts=6,
            ),
            "poll_vote",
        )
        assert seen[0].options == (2,)

    async def test_taking_a_vote_back(self):
        seen = await caught(
            types.UpdateMessagePollVote(
                poll_id=77,
                peer=types.PeerUser(user_id=THEM),
                options=[],
                positions=[],
                qts=6,
            ),
            "poll_vote",
        )
        assert seen[0].retracted is True


class TestTheSmallOnes:
    async def test_somebody_coming_online(self):
        seen = await caught(
            types.UpdateUserStatus(
                user_id=THEM, status=types.UserStatusOnline(expires=DATE + 60)
            ),
            "status",
        )
        standing = seen[0]
        assert isinstance(standing, Status)
        assert standing.online and standing.status == "online"
        assert standing.expires == DATE + 60

    async def test_somebody_having_been_here(self):
        seen = await caught(
            types.UpdateUserStatus(
                user_id=THEM, status=types.UserStatusOffline(was_online=DATE)
            ),
            "status",
        )
        assert seen[0].status == "offline" and seen[0].last_seen == DATE

    async def test_the_vague_ones_carry_no_time(self):
        seen = await caught(
            types.UpdateUserStatus(user_id=THEM, status=types.UserStatusLastWeek()),
            "status",
        )
        assert seen[0].status == "last_week"
        assert (seen[0].expires, seen[0].last_seen) == (0, 0)

    async def test_typing_in_a_private_chat(self):
        seen = await caught(
            types.UpdateUserTyping(
                user_id=THEM, action=types.SendMessageTypingAction()
            ),
            "typing",
        )
        doing = seen[0]
        assert isinstance(doing, Typing)
        assert doing.doing == "typing"
        assert doing.chat_id == doing.user_id == mark_id(THEM, PeerKind.USER)

    async def test_doing_something_else_in_a_channel(self):
        seen = await caught(
            types.UpdateChannelUserTyping(
                channel_id=CHANNEL,
                from_id=types.PeerUser(user_id=THEM),
                action=types.SendMessageUploadVideoAction(progress=40),
                top_msg_id=3,
            ),
            "typing",
        )
        doing = seen[0]
        assert doing.doing == "upload_video"
        assert doing.progress == 40
        assert doing.chat_id == MARKED_CHANNEL
        assert doing.topic_id == 3

    async def test_typing_in_a_basic_group(self):
        seen = await caught(
            types.UpdateChatUserTyping(
                chat_id=55,
                from_id=types.PeerUser(user_id=THEM),
                action=types.SendMessageChooseStickerAction(),
            ),
            "typing",
        )
        assert seen[0].doing == "choose_sticker"
        assert seen[0].chat_id == mark_id(55, PeerKind.CHAT)

    async def test_being_blocked(self):
        seen = await caught(
            types.UpdatePeerBlocked(
                peer_id=types.PeerUser(user_id=THEM), blocked=True
            ),
            "blocked",
        )
        assert isinstance(seen[0], Blocked)
        assert seen[0].blocked and seen[0].user_id == mark_id(THEM, PeerKind.USER)

    async def test_a_bot_being_stopped_and_restarted(self):
        stopped = await caught(
            types.UpdateBotStopped(user_id=THEM, date=DATE, stopped=True, qts=1),
            "stopped",
        )
        restarted = await caught(
            types.UpdateBotStopped(user_id=THEM, date=DATE, stopped=False, qts=2),
            "stopped",
        )
        assert isinstance(stopped[0], Stopped)
        assert stopped[0].stopped is True
        assert restarted[0].stopped is False


class TestActingOnWhatArrived:
    """The wrappers that can do something, doing it through a stub client."""

    class Acting:
        def __init__(self) -> None:
            self.calls: list[Any] = []

        async def close_poll(self, chat_id: int, message_id: int) -> None:
            self.calls.append(("close", chat_id, message_id))

        async def vote(self, chat_id: int, message_id: int, *positions: int) -> str:
            self.calls.append(("vote", chat_id, message_id, positions))
            return "voted"

        async def get_poll(self, chat_id: int, message_id: int) -> str:
            self.calls.append(("get", chat_id, message_id))
            return "results"

        async def get_messages(self, chat_id: int, ids: list[int]) -> list[Any]:
            self.calls.append(("messages", chat_id, tuple(ids)))
            return ["the message"]

    async def test_a_located_poll_can_be_closed_voted_in_and_refreshed(self):
        acting = self.Acting()
        poll = Poll(id=1, chat_id=MARKED_CHANNEL, message_id=5, client=acting)
        await poll.close()
        assert await poll.vote(0, 2) == "voted"
        assert await poll.refresh() == "results"
        assert acting.calls == [
            ("close", MARKED_CHANNEL, 5),
            ("vote", MARKED_CHANNEL, 5, (0, 2)),
            ("get", MARKED_CHANNEL, 5),
        ]

    async def test_a_poll_bound_to_nothing_says_so(self):
        poll = Poll(id=1, chat_id=MARKED_CHANNEL, message_id=5)
        with pytest.raises(Exception, match="not bound to a client"):
            await poll.close()

    async def test_the_message_a_reaction_is_on_can_be_fetched(self):
        acting = self.Acting()
        change = ReactionUpdate(
            chat_id=MARKED_CHANNEL, message_id=12, client=acting
        )
        assert await change.get_message() == "the message"
        assert acting.calls == [("messages", MARKED_CHANNEL, (12,))]

    async def test_a_reaction_on_a_message_that_is_gone(self):
        class Empty(self.Acting):
            async def get_messages(self, chat_id: int, ids: list[int]) -> list[Any]:
                return []

        change = ReactionUpdate(chat_id=MARKED_CHANNEL, message_id=12, client=Empty())
        with pytest.raises(Exception, match="not there any more"):
            await change.get_message()

    async def test_a_reaction_bound_to_nothing_says_so(self):
        with pytest.raises(Exception, match="not bound to a client"):
            await ReactionUpdate(chat_id=1, message_id=2).get_message()

    async def test_a_join_request_bound_to_nothing_says_so(self):
        with pytest.raises(Exception, match="not bound to a client"):
            await JoinRequest(chat_id=1, user_id=THEM).approve()

    async def test_a_reaction_nobody_can_name_reads_as_nothing(self):
        # reactionEmpty is a real constructor and carries nothing at all.
        # Guessing a name for it would put it in the same namespace as an emoji
        # somebody really sent.
        seen = await caught(
            types.UpdateBotMessageReactions(
                peer=types.PeerChannel(channel_id=CHANNEL),
                msg_id=1,
                date=DATE,
                reactions=[
                    types.ReactionCount(reaction=types.ReactionEmpty(), count=1)
                ],
                qts=5,
            ),
            "reaction",
        )
        assert seen[0].counts == {"": 1}


class TestReadingAPollFurther:
    def a_poll(self, *counts: int) -> Poll:
        from sunnygram.types import PollAnswer

        return Poll(
            id=1,
            question="?",
            answers=tuple(
                PollAnswer(position=n, text=str(n), voters=count, correct=count == 9)
                for n, count in enumerate(counts)
            ),
        )

    def test_a_tie_has_no_winner(self):
        # A tie is a real outcome, and picking a side of it quietly is the kind
        # of thing that is found out much later.
        assert self.a_poll(3, 3).winner is None

    def test_a_poll_with_no_answers_yet_has_no_winner(self):
        assert Poll(id=1).winner is None

    def test_the_right_answer_of_a_quiz(self):
        poll = self.a_poll(1, 9)
        assert poll.correct is not None and poll.correct.position == 1

    def test_a_poll_that_is_not_a_quiz_has_no_right_answer(self):
        assert self.a_poll(1, 2).correct is None


class TestTheyAllSayWhatTheyAre:
    """The reprs, which is what a log line and a debugger show."""

    def test_a_member_update(self):
        change = MemberUpdate(chat_id=MARKED_CHANNEL, user_id=THEM)
        assert "changed" in repr(change)

    def test_a_join_request(self):
        assert str(THEM) in repr(JoinRequest(chat_id=1, user_id=THEM))

    def test_a_reaction_both_ways(self):
        assert "->" in repr(
            ReactionUpdate(chat_id=1, message_id=2, reading="person", after=("👍",))
        )
        assert "👍" in repr(
            ReactionUpdate(chat_id=1, message_id=2, counts={"👍": 2})
        )

    def test_a_poll_an_answer_and_a_vote(self):
        from sunnygram.types import PollAnswer

        assert "closed" in repr(Poll(id=1, closed=True))
        assert "3 votes" in repr(PollAnswer(position=0, text="Yes", voters=3))
        assert "77" in repr(PollVote(poll_id=77, voter_id=THEM, options=(0,)))

    def test_the_small_ones(self):
        assert "2" in repr(DeletedMessages(ids=(1, 2)))
        assert "online" in repr(Status(user_id=THEM, status="online"))
        assert "typing" in repr(Typing(chat_id=1, user_id=THEM))
        assert "unblocked" in repr(Blocked(user_id=THEM, blocked=False))
        assert "restarted" in repr(Stopped(user_id=THEM, stopped=False))
        assert "InlineQuery" in repr(InlineQuery(id=1, text="x"))
        assert "ChosenResult" in repr(ChosenResult(id="r"))


class TestTheWrongUpdateIsNotWrapped:
    """Every from_raw says no to something it was not built for.

    They are reached through the table, which only ever hands each the update
    it is for, but they are public and a program reading raw updates may call
    one directly. Answering nothing beats a confusing AttributeError.
    """

    def test_each_wrapper_refuses_a_stranger(self):
        stranger = types.UpdateNewMessage(
            message=types.Message(
                id=1, peer_id=types.PeerUser(user_id=THEM), date=DATE, message="hi"
            ),
            pts=1,
            pts_count=1,
        )
        assert InlineQuery.from_raw(stranger) is None
        assert ChosenResult.from_raw(stranger) is None
        assert MemberUpdate.from_raw(stranger) is None
        assert JoinRequest.from_raw(stranger) is None
        assert DeletedMessages.from_raw(stranger) is None
        assert ReactionUpdate.from_raw(stranger) is None
        assert Poll.from_raw(stranger) is None
        assert PollVote.from_raw(stranger) is None
        assert Status.from_raw(stranger) is None
        assert Typing.from_raw(stranger) is None
        assert Blocked.from_raw(stranger) is None
        assert Stopped.from_raw(stranger) is None


class TestFiltersAnswerAboutWhatTheyCan:
    async def test_a_message_filter_asked_about_a_typing_notification_says_no(self):
        # It must not raise: a filter runs on updates its own handler never
        # sees, so one that raised here would report a fault about an update
        # nobody wanted, and the audit round already fixed that once.
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=callback, kind="typing", filters=filters.photo)
        )
        await dispatcher.feed(
            None,
            an_event(
                types.UpdateUserTyping(
                    user_id=THEM, action=types.SendMessageTypingAction()
                )
            ),
        )
        assert seen == []
        assert dispatcher.errors == 0

    async def test_a_command_typed_into_an_inline_query_still_matches(self):
        # An inline query has text and nowhere to keep a command, and being
        # unable to leave the pieces must not change the answer to the
        # question. This is the shape that really produces that: a frozen
        # record has no text at all, so it never gets this far.
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=callback,
                kind="inline_query",
                filters=filters.command("start"),
            )
        )
        await dispatcher.feed(
            None,
            an_event(
                types.UpdateBotInlineQuery(
                    query_id=1, user_id=THEM, query="/start now", offset=""
                )
            ),
        )
        assert [one.text for one in seen] == ["/start now"]
        assert dispatcher.errors == 0

    async def test_a_query_filter_asked_about_something_with_no_text(self):
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=callback, kind="stopped", filters=filters.query())
        )
        await dispatcher.feed(
            None,
            an_event(
                types.UpdateBotStopped(user_id=THEM, date=DATE, stopped=True, qts=1)
            ),
        )
        assert seen == []
        assert dispatcher.errors == 0

    async def test_the_command_filter_leaves_nothing_where_it_cannot(self):
        # A frozen record has nowhere to keep the pieces, and that must not
        # change the answer to the question or end the stream.
        seen: list[Any] = []

        async def callback(client: Any, value: Any) -> None:
            seen.append(value)

        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=callback, kind="typing", filters=filters.command("start")
            )
        )
        await dispatcher.feed(
            None,
            an_event(
                types.UpdateUserTyping(
                    user_id=THEM, action=types.SendMessageTypingAction()
                )
            ),
        )
        assert seen == []
        assert dispatcher.errors == 0


async def _nothing(client: Any, value: Any) -> None:
    return None
