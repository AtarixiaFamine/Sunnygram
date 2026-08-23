"""Inline mode: building results, and answering a query with them.

Two halves. Building a result is pure and is checked directly, because the
awkward part is that Telegram spells a result four different ways and which one
is right follows from what the caller passed rather than from what they said.
Answering is driven against a scripted datacenter, so what is checked is the
call that really went out.

The rule this file is most careful about is the one that costs a person a
loading spinner forever: a query must be answered, an empty answer is a real
answer, and more results than Telegram takes is refused here with a sentence
rather than on the wire with an error code.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, RecordingServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import bots
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState
from sunnygram.types import Button, InlineResult, keyboard

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
QUERY = 4242


def a_document() -> types.Document:
    return types.Document(
        id=10,
        access_hash=20,
        file_reference=b"ref",
        date=1700000000,
        mime_type="application/pdf",
        size=1024,
        dc_id=2,
        attributes=[],
    )


def a_photo() -> types.Photo:
    return types.Photo(
        id=30,
        access_hash=40,
        file_reference=b"ref",
        date=1700000000,
        sizes=[],
        dc_id=2,
    )


class TestBuildingResults:
    def test_an_article_is_a_row_of_text(self):
        built = InlineResult.article("Rome", "Rome is the capital").to_raw()
        assert isinstance(built, types.InputBotInlineResult)
        assert built.type == "article"
        assert built.title == "Rome"
        assert isinstance(built.send_message, types.InputBotInlineMessageText)
        assert built.send_message.message == "Rome is the capital"

    def test_the_text_sent_is_not_the_text_shown(self):
        # The whole reason an article has both: the list shows a title and a
        # description, and picking it sends something else entirely.
        built = InlineResult.article(
            "Rome", "the message", description="the description"
        ).to_raw()
        assert built.description == "the description"
        assert built.send_message.message == "the message"

    def test_a_photo_telegram_already_holds(self):
        built = InlineResult.photo(a_photo(), caption="nice").to_raw()
        assert isinstance(built, types.InputBotInlineResultPhoto)
        assert built.photo.id == 30
        # A file carries a caption rather than a message, which Telegram spells
        # as a different constructor.
        assert isinstance(built.send_message, types.InputBotInlineMessageMediaAuto)
        assert built.send_message.message == "nice"

    def test_a_photo_on_the_web(self):
        built = InlineResult.photo("https://example.com/cat.jpg").to_raw()
        assert isinstance(built, types.InputBotInlineResult)
        assert built.type == "photo"
        assert built.content is not None
        assert built.content.url == "https://example.com/cat.jpg"

    def test_a_document_telegram_already_holds(self):
        built = InlineResult.document(a_document(), title="The paper").to_raw()
        assert isinstance(built, types.InputBotInlineResultDocument)
        assert built.document.id == 10
        assert built.title == "The paper"

    def test_an_mp4_is_offered_as_the_animation_clients_want(self):
        built = InlineResult.animation("https://example.com/loop.mp4").to_raw()
        assert built.type == "mpeg4_gif"
        assert built.content.mime_type == "video/mp4"

    def test_a_real_gif_is_offered_as_one(self):
        built = InlineResult.animation("https://example.com/loop.gif").to_raw()
        assert built.type == "gif"
        assert built.content.mime_type == "image/gif"

    def test_a_location_carries_a_point_rather_than_a_message(self):
        built = InlineResult.location(41.9, 12.5, "Rome").to_raw()
        assert isinstance(built.send_message, types.InputBotInlineMessageMediaGeo)
        assert built.send_message.geo_point.lat == pytest.approx(41.9)

    def test_a_live_location_says_how_long_it_lives(self):
        built = InlineResult.location(41.9, 12.5, "Rome", live_period=600).to_raw()
        assert built.send_message.period == 600

    def test_a_venue_is_a_point_with_an_address(self):
        built = InlineResult.venue(41.9, 12.5, "The place", "A street").to_raw()
        assert isinstance(built.send_message, types.InputBotInlineMessageMediaVenue)
        assert built.send_message.address == "A street"

    def test_a_contact_is_a_phone_number(self):
        built = InlineResult.contact("+3900", "Some").to_raw()
        assert isinstance(built.send_message, types.InputBotInlineMessageMediaContact)
        assert built.send_message.phone_number == "+3900"

    def test_a_game_has_its_own_constructor(self):
        built = InlineResult.game("chess").to_raw()
        assert isinstance(built, types.InputBotInlineResultGame)
        assert built.short_name == "chess"

    def test_a_sticker_has_to_be_one_telegram_holds(self):
        # There is no web form for a sticker, and saying so here beats a
        # server error that does not explain itself.
        with pytest.raises(ValueError, match="already holds"):
            InlineResult.sticker("https://example.com/sticker.webp")

    def test_something_that_is_neither_a_file_nor_a_link(self):
        with pytest.raises(SunnygramError, match="not a file Telegram already holds"):
            InlineResult.photo(object()).to_raw()

    def test_a_keyboard_goes_under_the_message_that_is_sent(self):
        rows = keyboard([Button.callback("More", "more")])
        built = InlineResult.article("Rome", "text", reply_markup=rows).to_raw()
        assert built.send_message.reply_markup is rows

    def test_results_are_named_apart_when_the_caller_does_not_name_them(self):
        made = [InlineResult.article("a", "a").id for _ in range(50)]
        assert len(set(made)) == 50

    def test_a_caller_naming_one_gets_that_name_back(self):
        # The id is what comes back on the chosen-result update, so a program
        # counting what people pick names its own.
        assert InlineResult.article("a", "a", id="rome").to_raw().id == "rome"

    def test_the_message_is_styled_when_the_answer_is_sent(self):
        # Not when the result is built: the parse mode belongs to the client,
        # and a result is usually built before there is one in hand.
        def style(text: str) -> tuple[str, list[Any]]:
            return text.upper(), [types.MessageEntityBold(offset=0, length=4)]

        built = InlineResult.article("t", "bold").to_raw(style)
        assert built.send_message.message == "BOLD"
        assert built.send_message.entities is not None

    def test_entities_given_by_hand_are_left_alone(self):
        def style(text: str) -> tuple[str, list[Any]]:
            raise AssertionError("this should not be reached")

        result = InlineResult.article("t", "already styled")
        result.entities = [types.MessageEntityBold(offset=0, length=7)]
        assert result.to_raw(style).send_message.message == "already styled"


class TestTheOtherFileKinds:
    def test_a_video(self):
        built = InlineResult.video(a_document(), title="The clip").to_raw()
        assert isinstance(built, types.InputBotInlineResultDocument)
        assert built.type == "video" and built.title == "The clip"

    def test_an_audio_file(self):
        built = InlineResult.audio(a_document(), title="The song").to_raw()
        assert built.type == "audio"

    def test_a_voice_note(self):
        built = InlineResult.voice(a_document()).to_raw()
        assert built.type == "voice"

    def test_a_sticker_telegram_holds(self):
        built = InlineResult.sticker(a_document()).to_raw()
        assert built.type == "sticker"
        assert built.document.id == 10

    def test_a_video_on_the_web(self):
        built = InlineResult.video("https://example.com/clip.mp4").to_raw()
        assert isinstance(built, types.InputBotInlineResult)
        assert built.content.mime_type == "video/mp4"

    def test_a_result_says_what_it_is(self):
        assert "article" in repr(InlineResult.article("Rome", "text"))


class TestActingThroughTheClient:
    class Acting:
        def __init__(self) -> None:
            self.calls: list[Any] = []

        async def answer_inline_query(
            self, query_id: int, results: list[Any], **options: Any
        ) -> bool:
            self.calls.append(("answer", query_id, results, options))
            return True

        async def edit_inline_message(
            self, inline_id: Any, text: str, **options: Any
        ) -> bool:
            self.calls.append(("edit", inline_id, text))
            return True

        async def edit_inline_markup(self, inline_id: Any, markup: Any) -> bool:
            self.calls.append(("markup", inline_id, markup))
            return True

    async def test_a_query_answers_through_its_client(self):
        from sunnygram.types import InlineQuery

        acting = self.Acting()
        asked = InlineQuery(id=7, text="cats", client=acting)
        results = [InlineResult.article("Rome", "text")]
        assert await asked.answer(results, cache_time=0) is True
        what, query_id, sent, options = acting.calls[0]
        assert (what, query_id) == ("answer", 7)
        assert sent == results
        assert options["cache_time"] == 0

    async def test_a_chosen_result_edits_the_message_it_sent(self):
        from sunnygram.types import ChosenResult

        acting = self.Acting()
        inline_id = types.InputBotInlineMessageID(dc_id=2, id=5, access_hash=6)
        chosen = ChosenResult(id="r", inline_id=inline_id, client=acting)
        await chosen.edit("changed")
        await chosen.edit_markup(None)
        assert [one[0] for one in acting.calls] == ["edit", "markup"]
        assert acting.calls[0][1] is inline_id

    async def test_a_chosen_result_bound_to_nothing_says_so(self):
        from sunnygram.types import ChosenResult

        inline_id = types.InputBotInlineMessageID(dc_id=2, id=5, access_hash=6)
        chosen = ChosenResult(id="r", inline_id=inline_id)
        with pytest.raises(SunnygramError, match="not bound to a client"):
            await chosen.edit("changed")


class TestAnsweringAQuery:
    async def test_the_results_reach_the_wire(self):
        async with live() as (invoker, server):
            answered = await bots.answer_inline_query(
                invoker,
                QUERY,
                [InlineResult.article("Rome", "text", id="rome").to_raw()],
                cache_time=0,
            )
        assert answered is True
        call = server.only(functions.messages.SetInlineBotResults)
        assert call.query_id == QUERY
        assert [one.id for one in call.results] == ["rome"]
        assert call.cache_time == 0

    async def test_an_empty_answer_is_a_real_answer(self):
        # The rule: a query held open is a person looking at a panel that never
        # finishes loading, so having nothing to offer is still answered.
        async with live() as (invoker, server):
            await bots.answer_inline_query(invoker, QUERY, [])
        assert server.only(functions.messages.SetInlineBotResults).results == []

    async def test_more_results_than_telegram_takes_is_refused_here(self):
        results = [
            InlineResult.article("a", "a", id=str(n)).to_raw() for n in range(51)
        ]
        async with live() as (invoker, server):
            with pytest.raises(ValueError, match="at most 50"):
                await bots.answer_inline_query(invoker, QUERY, results)
        assert server.all(functions.messages.SetInlineBotResults) == []

    async def test_the_paging_cursor_travels(self):
        async with live() as (invoker, server):
            await bots.answer_inline_query(invoker, QUERY, [], next_offset="30")
        assert server.only(functions.messages.SetInlineBotResults).next_offset == "30"

    async def test_no_cursor_means_this_is_everything(self):
        async with live() as (invoker, server):
            await bots.answer_inline_query(invoker, QUERY, [])
        assert server.only(functions.messages.SetInlineBotResults).next_offset is None

    async def test_the_switch_to_private_button(self):
        async with live() as (invoker, server):
            await bots.answer_inline_query(
                invoker, QUERY, [], switch_pm="Log in first", start_parameter="login"
            )
        switch = server.only(functions.messages.SetInlineBotResults).switch_pm
        assert switch.text == "Log in first"
        assert switch.start_param == "login"

    async def test_gallery_and_private_travel_as_flags(self):
        async with live() as (invoker, server):
            await bots.answer_inline_query(
                invoker, QUERY, [], gallery=True, private=True
            )
        call = server.only(functions.messages.SetInlineBotResults)
        assert call.gallery and call.private


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


@asynccontextmanager
async def live() -> AsyncIterator[tuple[Invoker, RecordingServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    invoker = Invoker(
        MemoryStorage(session),
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=10.0,
        rate_limit=False,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = RecordingServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve_all())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
