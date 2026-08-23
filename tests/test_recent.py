"""Answering a reply without asking the server what it answers.

Three things can supply the message being replied to, and they are tried in that
order: the other messages that came in the same answer, the quote the reply
header carries, and what the client has lately seen go past. Only when all three
come up empty is there a call, and these check that the first three work, since
the fourth is the one everybody already has.
"""

from __future__ import annotations

from typing import Any

from sunnygram.client import Client
from sunnygram.raw import types
from sunnygram.recent import RecentMessages
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.types import Message

ME = 777000
OTHER = 1001


def a_user(id: int = OTHER) -> types.User:
    return types.User(id=id, access_hash=id * 3, first_name="Pavel", username="durov")


def a_message(
    id: int = 1,
    text: str = "hello",
    *,
    reply_to: Any = None,
    media: Any = None,
) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=OTHER),
        date=1700000000,
        message=text,
        media=media,
        reply_to=reply_to,
    )


def wrap(raw: types.Message, **options: Any) -> Message:
    found = Message.from_raw(
        raw, users={OTHER: a_user()}, chats={}, **options
    )
    assert found is not None
    return found


def a_client(**options: Any) -> Client:
    return Client(
        MemoryStorage(SessionState(dc_id=2, user_id=ME)),
        api_id=12345,
        api_hash="0" * 32,
        **options,
    )


class TestTheCache:
    def test_what_goes_in_comes_out(self):
        held = RecentMessages()
        held.remember(wrap(a_message(5, "five")))
        assert held.get(OTHER, 5).text == "five"
        assert held.hits == 1

    def test_something_never_seen_is_a_miss(self):
        held = RecentMessages()
        assert held.get(OTHER, 99) is None
        assert held.misses == 1

    def test_the_oldest_goes_when_it_is_full(self):
        held = RecentMessages(limit=3)
        for id in range(1, 5):
            held.remember(wrap(a_message(id)))
        assert len(held) == 3
        assert held.get(OTHER, 1) is None
        assert held.get(OTHER, 4) is not None

    def test_reading_one_keeps_it(self):
        held = RecentMessages(limit=2)
        held.remember(wrap(a_message(1)))
        held.remember(wrap(a_message(2)))
        held.get(OTHER, 1)
        held.remember(wrap(a_message(3)))
        # Two was the least recently used by then, not one.
        assert held.get(OTHER, 1) is not None
        assert held.get(OTHER, 2) is None

    def test_a_limit_of_nothing_holds_nothing(self):
        held = RecentMessages(limit=0)
        held.remember(wrap(a_message(1)))
        assert len(held) == 0

    def test_a_message_with_nothing_naming_a_chat_is_not_stored(self):
        held = RecentMessages()
        held.remember(Message(id=1))
        assert len(held) == 0

    def test_a_message_with_only_a_raw_peer_still_counts(self):
        # What a send answers with: the id is in the message and there was no
        # user or chat alongside it to build a Chat out of.
        held = RecentMessages()
        bare = Message.from_raw(a_message(9, "just sent"))
        assert bare is not None and bare.chat is None
        held.remember(bare)
        assert held.get(OTHER, 9) is not None

    def test_it_says_what_it_is_holding(self):
        held = RecentMessages()
        held.remember(wrap(a_message(1)))
        assert "1/1000 held" in repr(held)

    def test_letting_go(self):
        held = RecentMessages()
        held.remember(wrap(a_message(1)))
        held.forget(OTHER, 1)
        held.remember(wrap(a_message(2)))
        held.clear()
        assert len(held) == 0


class TestRepliesInTheSameAnswer:
    def test_a_reply_is_tied_to_what_it_answers(self):
        page = {1: a_message(1, "the question")}
        reply = wrap(
            a_message(2, "the answer", reply_to=types.MessageReplyHeader(reply_to_msg_id=1)),
            replies=page,
        )
        assert reply.reply_to_id == 1
        assert reply.reply_to_message is not None
        assert reply.reply_to_message.text == "the question"
        assert not reply.reply_to_message.partial

    def test_a_reply_to_something_not_on_the_page_is_left_open(self):
        reply = wrap(
            a_message(2, "answer", reply_to=types.MessageReplyHeader(reply_to_msg_id=1)),
            replies={},
        )
        assert reply.reply_to_id == 1
        assert reply.reply_to_message is None

    def test_a_message_that_answers_nothing_has_nothing(self):
        assert wrap(a_message(1)).reply_to_message is None


class TestQuotedReplies:
    def test_a_quote_becomes_an_outline(self):
        quoted = wrap(
            a_message(
                2,
                "answer",
                reply_to=types.MessageReplyHeader(
                    reply_to_msg_id=1, quote=True, quote_text="the bit selected"
                ),
            )
        )
        assert quoted.reply_to_message is not None
        assert quoted.reply_to_message.text == "the bit selected"
        # An outline, because a quote is part of the other message rather than
        # all of it, and anything reading its text should know that.
        assert quoted.reply_to_message.partial

    def test_the_media_a_quote_carries_is_enough_to_download(self):
        carried = types.MessageMediaDocument(
            document=types.Document(
                id=1,
                access_hash=2,
                file_reference=b"\x00",
                date=0,
                mime_type="audio/mpeg",
                size=10,
                dc_id=2,
                attributes=[],
            )
        )
        quoted = wrap(
            a_message(
                2,
                "answer",
                reply_to=types.MessageReplyHeader(
                    reply_to_msg_id=1, reply_media=carried
                ),
            )
        )
        assert quoted.reply_to_message is not None
        assert quoted.reply_to_message.has_media

    def test_a_bare_reply_header_carries_no_outline(self):
        bare = wrap(
            a_message(2, "answer", reply_to=types.MessageReplyHeader(reply_to_msg_id=1))
        )
        assert bare.reply_to_message is None


class TestThroughTheClient:
    def test_a_message_is_written_down_as_it_is_wrapped(self):
        client = a_client()
        client.wrap_message(a_message(1, "first"), users={OTHER: a_user()})
        assert client.recent.get(OTHER, 1) is not None

    def test_a_reply_finds_what_it_answers_in_the_cache(self):
        client = a_client()
        client.wrap_message(a_message(1, "the question"), users={OTHER: a_user()})
        reply = client.wrap_message(
            a_message(
                2, "answer", reply_to=types.MessageReplyHeader(reply_to_msg_id=1)
            ),
            users={OTHER: a_user()},
        )
        assert reply is not None
        assert reply.reply_to_message is not None
        assert reply.reply_to_message.text == "the question"

    def test_the_cache_beats_an_outline(self):
        client = a_client()
        client.wrap_message(a_message(1, "the whole thing"), users={OTHER: a_user()})
        reply = client.wrap_message(
            a_message(
                2,
                "answer",
                reply_to=types.MessageReplyHeader(
                    reply_to_msg_id=1, quote=True, quote_text="the bit"
                ),
            ),
            users={OTHER: a_user()},
        )
        assert reply is not None
        assert reply.reply_to_message is not None
        assert reply.reply_to_message.text == "the whole thing"
        assert not reply.reply_to_message.partial

    def test_turning_the_cache_off(self):
        client = a_client(message_cache=0)
        client.wrap_message(a_message(1), users={OTHER: a_user()})
        assert len(client.recent) == 0
