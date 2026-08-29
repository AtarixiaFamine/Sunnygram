"""Deciding who gets an update, and putting albums back together.

The dispatcher's contract is small and easy to break by accident: every handler
that matches runs, in group order, one handler failing does not stop the others,
and StopPropagation stops everything after it. The album collector is the one
piece with a clock in it, so its tests wait on real time with a wait short
enough not to be felt.

Two of these are about what must not happen. A filter that raises must not end
the update stream, because a filter runs on updates its own handler never sees,
so one bad filter would otherwise take down every feature in the program. And
first_match, when it is asked for, must stop a group after the handler that
matched rather than after the one that succeeded.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import pytest

from sunnygram import filters
from sunnygram.errors import SunnygramError
from sunnygram.dispatcher import (
    ALBUM_GROUPS,
    ALBUM_PARTS,
    AlbumCollector,
    Dispatcher,
    Handler,
    StopPropagation,
)
from sunnygram.raw import types
from sunnygram.types import CallbackQuery, Message
from sunnygram.updates import Event

WAIT = 0.02


def a_message(id: int = 1, *, group: int | None = None, text: str = "hi") -> Message:
    raw = types.Message(
        id=id,
        peer_id=types.PeerUser(user_id=1001),
        date=1700000000,
        message=text,
        grouped_id=group,
    )
    wrapped = Message.from_raw(raw, users={}, chats={}, client=None)
    assert wrapped is not None
    return wrapped


def an_event(message: Message) -> Event:
    return Event(
        update=types.UpdateNewMessage(message=message.raw, pts=1, pts_count=1),
        users={},
        chats={},
    )


def a_press(data: bytes = b"yes", message_id: int = 7) -> Event:
    return Event(
        update=types.UpdateBotCallbackQuery(
            query_id=555,
            user_id=1001,
            peer=types.PeerUser(user_id=1001),
            msg_id=message_id,
            chat_instance=99,
            data=data,
        ),
        users={},
        chats={},
    )


def recorder(into: list[Any], *, fail: bool = False, stop: bool = False):
    async def callback(client: Any, value: Any) -> None:
        into.append(value)
        if fail:
            raise RuntimeError("this handler is broken")
        if stop:
            raise StopPropagation

    return callback


class TestRouting:
    async def test_every_matching_handler_runs(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen)))
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 2

    async def test_groups_run_in_order(self):
        order: list[int] = []

        def numbered(which: int):
            async def callback(client: Any, value: Any) -> None:
                order.append(which)

            return callback

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=numbered(2), group=2))
        dispatcher.add(Handler(callback=numbered(0), group=0))
        dispatcher.add(Handler(callback=numbered(1), group=1))
        await dispatcher.feed(None, an_event(a_message()))
        assert order == [0, 1, 2]

    async def test_a_filter_that_says_no(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), filters=filters.nothing))
        await dispatcher.feed(None, an_event(a_message()))
        assert seen == []

    async def test_stop_propagation_ends_the_update(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen, stop=True), group=0))
        dispatcher.add(Handler(callback=recorder(seen), group=1))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_one_broken_handler_does_not_stop_the_rest(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen, fail=True), group=0))
        dispatcher.add(Handler(callback=recorder(seen), group=1))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 2
        assert dispatcher.errors == 1

    async def test_a_failure_nobody_took_over_is_still_said_out_loud(self, caplog):
        # The fault this prevents: a handler raises, the stream carries on, and
        # the program appears to be ignoring messages with nothing anywhere to
        # say why. Nothing above the dispatcher ever sees the exception, so if
        # it is not reported here it is not reported at all.
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder([], fail=True)))
        with caplog.at_level(logging.ERROR, logger="sunnygram.dispatcher"):
            await dispatcher.feed(None, an_event(a_message()))
        assert dispatcher.errors == 1
        assert "message handler" in caplog.text
        assert "RuntimeError" in caplog.text

    async def test_a_failure_that_was_taken_over_is_not_also_logged(self, caplog):
        async def on_error(failure: BaseException, handler: Handler) -> None:
            return None

        dispatcher = Dispatcher(on_error=on_error)
        dispatcher.add(Handler(callback=recorder([], fail=True)))
        with caplog.at_level(logging.ERROR, logger="sunnygram.dispatcher"):
            await dispatcher.feed(None, an_event(a_message()))
        assert caplog.text == ""

    async def test_a_failure_can_be_reported(self):
        told: list[Any] = []

        async def on_error(failure: BaseException, handler: Handler) -> None:
            told.append((type(failure), handler.kind))

        dispatcher = Dispatcher(on_error=on_error)
        dispatcher.add(Handler(callback=recorder([], fail=True)))
        await dispatcher.feed(None, an_event(a_message()))
        assert told == [(RuntimeError, "message")]

    async def test_a_handler_appended_to_the_list_by_hand_still_runs(self):
        # handlers is a public field, and the index built over it is an
        # optimisation rather than a second source of truth. Somebody reaching
        # for the list directly must not end up with a handler that never fires.
        seen: list[Any] = []
        dispatcher = Dispatcher()
        await dispatcher.feed(None, an_event(a_message()))
        dispatcher.handlers.append(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_a_handler_removed_stops_running(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        handler = dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        dispatcher.remove(handler)
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_a_raw_handler_sees_the_update_as_well(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="raw"))
        await dispatcher.feed(None, an_event(a_message()))
        assert any(isinstance(one, Event) for one in seen)

    async def test_a_raw_handler_sees_it_once(self):
        # One update, one call. A raw handler asked for the update as it came,
        # so being given the message inside it as well would be a second call
        # with something it never asked for, and reading event.update off it
        # would raise on every message the program ever sees.
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="raw"))
        await dispatcher.feed(None, an_event(a_message()))
        assert [type(one).__name__ for one in seen] == ["Event"]

    async def test_a_raw_handler_sees_a_press_once_too(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="raw"))
        await dispatcher.feed(None, a_press())
        assert [type(one).__name__ for one in seen] == ["Event"]

    async def test_an_edited_handler_does_not_see_new_messages(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="edited"))
        await dispatcher.feed(None, an_event(a_message()))
        assert seen == []

    def test_a_handler_can_be_taken_out(self):
        dispatcher = Dispatcher()
        handler = dispatcher.add(Handler(callback=recorder([])))
        dispatcher.remove(handler)
        assert dispatcher.handlers == []
        # Removing one that is not there is not an error.
        dispatcher.remove(handler)

    def test_a_handler_says_what_it_is(self):
        async def echo(client: Any, message: Any) -> None:
            pass

        assert "echo on message" in repr(Handler(callback=echo))


class TestFilterFailures:
    async def test_a_filter_that_raises_does_not_end_the_stream(self):
        def broken(client: Any, message: Any) -> bool:
            raise RuntimeError("this filter is broken")

        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=recorder([]), filters=filters.make(broken), group=0)
        )
        dispatcher.add(Handler(callback=recorder(seen), group=1))
        await dispatcher.feed(None, an_event(a_message()))
        assert dispatcher.errors == 1
        # The point: everything after it still ran.
        assert len(seen) == 1

    async def test_the_failure_is_reported_like_any_other(self):
        told: list[Any] = []

        async def on_error(failure: BaseException, handler: Handler) -> None:
            told.append(type(failure))

        def broken(client: Any, message: Any) -> bool:
            raise ValueError("no")

        dispatcher = Dispatcher(on_error=on_error)
        dispatcher.add(Handler(callback=recorder([]), filters=filters.make(broken)))
        await dispatcher.feed(None, an_event(a_message()))
        assert told == [ValueError]


class TestCancellation:
    async def test_a_cancelled_handler_is_not_swallowed_as_a_failure(self):
        # Cancellation is the program being shut down, not a handler going
        # wrong. Counting it as an error and carrying on would leave the pump
        # running through a stop, which is the one exception that must pass.
        async def cancelled(client: Any, value: Any) -> None:
            raise asyncio.CancelledError

        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=cancelled))
        with pytest.raises(asyncio.CancelledError):
            await dispatcher.feed(None, an_event(a_message()))
        assert dispatcher.errors == 0


class TestFirstMatchWins:
    async def test_only_the_first_in_a_group_runs(self):
        seen: list[Any] = []
        dispatcher = Dispatcher(first_match=True)
        dispatcher.add(Handler(callback=recorder(seen)))
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_a_handler_whose_filter_said_no_does_not_count(self):
        seen: list[Any] = []
        dispatcher = Dispatcher(first_match=True)
        dispatcher.add(Handler(callback=recorder([]), filters=filters.nothing))
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_every_group_still_gets_a_turn(self):
        order: list[int] = []

        def numbered(which: int):
            async def callback(client: Any, value: Any) -> None:
                order.append(which)

            return callback

        dispatcher = Dispatcher(first_match=True)
        dispatcher.add(Handler(callback=numbered(0), group=0))
        dispatcher.add(Handler(callback=numbered(0), group=0))
        dispatcher.add(Handler(callback=numbered(1), group=1))
        await dispatcher.feed(None, an_event(a_message()))
        assert order == [0, 1]

    async def test_a_handler_that_matched_and_failed_still_owns_it(self):
        seen: list[Any] = []
        dispatcher = Dispatcher(first_match=True)
        dispatcher.add(Handler(callback=recorder(seen, fail=True)))
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        # Handling it twice because the first attempt went wrong is the
        # opposite of what asking for first_match meant.
        assert len(seen) == 1
        assert dispatcher.errors == 1

    async def test_everything_still_runs_by_default(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen)))
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 2


class TestButtonPresses:
    async def test_a_press_reaches_a_callback_handler(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="callback"))
        await dispatcher.feed(None, a_press())
        assert len(seen) == 1
        assert isinstance(seen[0], CallbackQuery)
        assert seen[0].text == "yes"
        assert seen[0].message_id == 7

    async def test_a_message_handler_does_not_see_one(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen)))
        await dispatcher.feed(None, a_press())
        assert seen == []

    async def test_a_raw_handler_sees_it_as_it_came(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="raw"))
        await dispatcher.feed(None, a_press())
        assert isinstance(seen[0], Event)

    async def test_a_filter_on_the_payload(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=recorder(seen), kind="callback", filters=filters.data("no")
            )
        )
        await dispatcher.feed(None, a_press(b"yes"))
        await dispatcher.feed(None, a_press(b"no"))
        assert len(seen) == 1

    async def test_a_prefix_filter_carries_an_argument(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=recorder(seen),
                kind="callback",
                filters=filters.data(prefix="page:"),
            )
        )
        await dispatcher.feed(None, a_press(b"page:3"))
        await dispatcher.feed(None, a_press(b"other"))
        assert [one.text for one in seen] == ["page:3"]

    async def test_regex_reads_the_payload_as_text(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(
                callback=recorder(seen),
                kind="callback",
                filters=filters.regex(r"^page:(\d+)$"),
            )
        )
        await dispatcher.feed(None, a_press(b"page:12"))
        assert seen[0].match.group(1) == "12"

    async def test_an_inline_press_says_it_has_no_chat(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="callback"))
        await dispatcher.feed(
            None,
            Event(
                update=types.UpdateInlineBotCallbackQuery(
                    query_id=1,
                    user_id=1001,
                    msg_id=types.InputBotInlineMessageID(
                        dc_id=2, id=5, access_hash=6
                    ),
                    chat_instance=9,
                    data=b"x",
                ),
                users={},
                chats={},
            ),
        )
        assert seen[0].is_inline
        assert seen[0].chat is None

    async def test_a_payload_that_is_not_text_reads_as_empty(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=recorder(seen), kind="callback"))
        await dispatcher.feed(None, a_press(b"\xff\xfe"))
        assert seen[0].text == ""
        assert seen[0].data == b"\xff\xfe"


class TestAlbumCollecting:
    async def test_the_parts_arrive_as_one(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        for id in (3, 1, 2):
            collector.add(a_message(id, group=77))
        await asyncio.sleep(WAIT * 5)
        assert [message.id for message in got[0]] == [1, 2, 3]

    async def test_a_message_with_no_group_is_not_an_album(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        collector.add(a_message(1))
        await asyncio.sleep(WAIT * 5)
        assert got == []

    async def test_two_albums_at_once_stay_apart(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        collector.add(a_message(1, group=77))
        collector.add(a_message(2, group=88))
        collector.add(a_message(3, group=77))
        await asyncio.sleep(WAIT * 5)
        assert sorted(len(one) for one in got) == [1, 2]

    async def test_a_late_part_restarts_the_clock(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        collector.add(a_message(1, group=77))
        await asyncio.sleep(WAIT / 2)
        collector.add(a_message(2, group=77))
        await asyncio.sleep(WAIT * 5)
        assert len(got) == 1 and len(got[0]) == 2

    async def test_more_parts_than_an_album_holds_are_dropped(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        for id in range(ALBUM_PARTS + 5):
            collector.add(a_message(id, group=77))
        await asyncio.sleep(WAIT * 5)
        assert len(got[0]) == ALBUM_PARTS
        assert collector.dropped == 5

    async def test_more_groups_than_it_will_hold(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        for group in range(ALBUM_GROUPS + 3):
            collector.add(a_message(1, group=group))
        assert collector.dropped == 3
        collector.close()

    async def test_closing_lets_go_of_everything(self):
        got: list[list[Message]] = []
        collector = AlbumCollector(_into(got), wait=WAIT)
        collector.add(a_message(1, group=77))
        collector.close()
        await asyncio.sleep(WAIT * 5)
        assert got == []

    def test_it_says_what_it_is_holding(self):
        assert "waiting" in repr(AlbumCollector(_into([]), wait=WAIT))


class TestAlbumsThroughTheDispatcher:
    async def test_an_album_handler_gets_the_whole_block(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.collect_albums(wait=WAIT)
        dispatcher.add(Handler(callback=recorder(seen), kind="album"))
        for id in (1, 2):
            await dispatcher.feed(None, an_event(a_message(id, group=77)))
        await asyncio.sleep(WAIT * 5)
        assert len(seen) == 1
        assert [message.id for message in seen[0]] == [1, 2]
        dispatcher.close()

    async def test_the_parts_still_reach_message_handlers(self):
        parts: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.collect_albums(wait=WAIT)
        dispatcher.add(Handler(callback=recorder(parts)))
        for id in (1, 2):
            await dispatcher.feed(None, an_event(a_message(id, group=77)))
        await asyncio.sleep(WAIT * 5)
        # An album is several messages, so a program written before albums
        # existed keeps seeing them.
        assert len(parts) == 2
        dispatcher.close()

    async def test_a_filter_on_an_album_is_asked_about_the_first_part(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.collect_albums(wait=WAIT)
        dispatcher.add(
            Handler(
                callback=recorder(seen),
                kind="album",
                filters=filters.make(
                    lambda client, message: message.text == "caption"
                ),
            )
        )
        await dispatcher.feed(None, an_event(a_message(1, group=77, text="caption")))
        await dispatcher.feed(None, an_event(a_message(2, group=77, text="")))
        await asyncio.sleep(WAIT * 5)
        assert len(seen) == 1
        dispatcher.close()

    async def test_a_raw_handler_is_not_given_a_list(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.collect_albums(wait=WAIT)
        dispatcher.add(Handler(callback=recorder(seen), kind="raw"))
        dispatcher.add(Handler(callback=recorder([]), kind="album"))
        await dispatcher.feed(None, an_event(a_message(1, group=77)))
        await asyncio.sleep(WAIT * 5)
        assert not any(isinstance(one, list) for one in seen)
        dispatcher.close()

    async def test_an_album_handler_can_stop_the_ones_after_it(self):
        # An album arrives on its own, after the silence, rather than inside a
        # feed, so StopPropagation out of one has its own place to be caught.
        # Without it the exception would take down the collector's timer task.
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.collect_albums(wait=WAIT)
        dispatcher.add(Handler(callback=recorder(seen, stop=True), kind="album"))
        dispatcher.add(Handler(callback=recorder(seen), kind="album", group=1))
        await dispatcher.feed(None, an_event(a_message(1, group=77)))
        await asyncio.sleep(WAIT * 5)
        assert len(seen) == 1
        assert dispatcher.errors == 0
        dispatcher.close()

    async def test_nothing_is_collected_until_somebody_asks(self):
        dispatcher = Dispatcher()
        await dispatcher.feed(None, an_event(a_message(1, group=77)))
        assert dispatcher.albums is None

    async def test_asking_twice_keeps_the_same_collector(self):
        dispatcher = Dispatcher()
        first = dispatcher.collect_albums(wait=WAIT)
        assert dispatcher.collect_albums(wait=WAIT) is first
        dispatcher.close()


def _into(collected: list[list[Message]]):
    async def emit(parts: list[Message]) -> None:
        collected.append(parts)

    return emit


@pytest.mark.parametrize("group", [None, 0])
def test_a_message_knows_which_album_it_is_in(group):
    # Zero is not a group id Telegram uses, but it must not read as "no album"
    # by accident either, which is why this checks the field rather than truth.
    assert a_message(1, group=group).album_id == group


class TestWaitingForAnAnswer:
    """The listener table conversations are built on.

    Three things have to hold, and each of them fails silently if it does not.
    An answered question must not also reach the handlers, or a command router
    sees somebody's name as a command. A question nobody answers must let go of
    its place, or the bounded table fills with waits that ended long ago. And a
    reading must still be built when the only thing interested is a wait, or a
    program with no message handler at all waits for ever for a message that
    arrived and was thrown away.
    """

    async def test_a_wait_is_answered_by_the_next_message_from_that_chat(self):
        dispatcher = Dispatcher()
        waiting = dispatcher.listen(1001)
        await dispatcher.feed(None, an_event(a_message(text="here I am")))
        assert waiting.future.done()
        assert waiting.future.result().text == "here I am"

    async def test_an_answer_does_not_also_reach_the_handlers(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(recorder(seen), kind="message"))
        dispatcher.listen(1001)
        await dispatcher.feed(None, an_event(a_message()))
        assert seen == []

    async def test_unless_the_wait_said_it_should(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(recorder(seen), kind="message"))
        dispatcher.listen(1001, exclusive=False)
        await dispatcher.feed(None, an_event(a_message()))
        assert len(seen) == 1

    async def test_a_message_from_elsewhere_is_not_an_answer(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(recorder(seen), kind="message"))
        waiting = dispatcher.listen(2002)
        await dispatcher.feed(None, an_event(a_message()))
        assert not waiting.future.done()
        # And it went where it would have gone anyway.
        assert len(seen) == 1

    async def test_a_filter_decides_what_counts_as_an_answer(self):
        dispatcher = Dispatcher()
        waiting = dispatcher.listen(1001, filters=filters.text & filters.command("ok"))
        await dispatcher.feed(None, an_event(a_message(text="nope")))
        assert not waiting.future.done()
        await dispatcher.feed(None, an_event(a_message(text="/ok")))
        assert waiting.future.done()

    async def test_the_reading_is_built_even_with_no_handler_for_it(self):
        # The saving that skips wrapping a message nobody asked for must not
        # skip one somebody is waiting for. Without this the wait never ends
        # and there is nothing anywhere to say why.
        dispatcher = Dispatcher()
        assert dispatcher.handlers == []
        waiting = dispatcher.listen(1001)
        await dispatcher.feed(None, an_event(a_message()))
        assert waiting.future.done()

    async def test_two_waits_on_one_chat_are_answered_oldest_first(self):
        dispatcher = Dispatcher()
        first = dispatcher.listen(1001)
        second = dispatcher.listen(1001)
        await dispatcher.feed(None, an_event(a_message(text="one")))
        assert first.future.result().text == "one"
        assert not second.future.done()
        await dispatcher.feed(None, an_event(a_message(text="two")))
        assert second.future.result().text == "two"

    async def test_a_press_can_be_waited_for_too(self):
        dispatcher = Dispatcher()
        waiting = dispatcher.listen(1001, kind="callback")
        await dispatcher.feed(None, a_press())
        assert isinstance(waiting.future.result(), CallbackQuery)

    async def test_stopping_takes_the_place_back(self):
        dispatcher = Dispatcher()
        waiting = dispatcher.listen(1001)
        assert dispatcher.listening == 1
        dispatcher.stop_listening(waiting)
        assert dispatcher.listening == 0
        assert waiting.future.cancelled()

    async def test_the_table_is_bounded(self):
        from sunnygram.dispatcher import LISTENING

        dispatcher = Dispatcher()
        for _ in range(LISTENING):
            dispatcher.listen(1001)
        with pytest.raises(SunnygramError, match="waiting for an answer"):
            dispatcher.listen(1001)

    async def test_closing_releases_anybody_still_waiting(self):
        # A client that stopped is a client whose updates have stopped, so a
        # wait that carried on would hang until its own timeout with no
        # explanation and nothing left to answer it.
        dispatcher = Dispatcher()
        waiting = dispatcher.listen(1001)
        dispatcher.close()
        assert waiting.future.cancelled()
        assert dispatcher.listening == 0

    async def test_a_wait_that_was_cancelled_is_stepped_over(self):
        # The waiter cancels its own future on the way out, and the record may
        # still be in the table when the next message arrives. It must not be
        # treated as an answer, and it must not stop the message reaching the
        # wait behind it.
        dispatcher = Dispatcher()
        stale = dispatcher.listen(1001)
        live = dispatcher.listen(1001)
        stale.future.cancel()
        await dispatcher.feed(None, an_event(a_message(text="mine")))
        assert live.future.result().text == "mine"


class TestWhatAFilterMayAnswerWith:
    """A predicate can be sync or async and need not answer with a bool.

    Filter.__call__ settles the plain True and False in front, because that is
    what nearly every filter answers and asking inspect whether one is
    awaitable costs more than the rest of the filter does. These are the three
    ways through it, so the shortcut cannot quietly swallow the other two.
    """

    async def test_a_plain_bool_is_answered_as_it_is(self):
        assert await filters.make(lambda client, event: True)(None, None) is True
        assert await filters.make(lambda client, event: False)(None, None) is False

    async def test_an_async_predicate_is_awaited(self):
        async def slow(client: Any, event: Any) -> bool:
            await asyncio.sleep(0)
            return True

        async def slow_no(client: Any, event: Any) -> bool:
            await asyncio.sleep(0)
            return False

        assert await filters.make(slow)(None, None) is True
        assert await filters.make(slow_no)(None, None) is False

    async def test_something_merely_truthy_still_counts(self):
        assert await filters.make(lambda client, event: "yes")(None, None) is True
        assert await filters.make(lambda client, event: [])(None, None) is False
        assert await filters.make(lambda client, event: None)(None, None) is False

    async def test_an_async_predicate_composes_with_a_sync_one(self):
        async def slow(client: Any, event: Any) -> bool:
            await asyncio.sleep(0)
            return True

        both = filters.make(slow) & filters.make(lambda client, event: True)
        either = filters.make(slow) | filters.make(lambda client, event: False)
        assert await both(None, None) is True
        assert await either(None, None) is True
        assert await (~filters.make(slow))(None, None) is False
