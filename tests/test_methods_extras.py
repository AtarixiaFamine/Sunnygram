"""Albums, polls, reactions, and the rest of what a message can be.

The builders are pure and are checked directly. The album is the one worth
driving against a server, because sending one is three steps rather than a call
and the middle step is the one everybody forgets: an uploaded file has to be
registered before it can go in a group.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import albums, attachments, messages, reactions
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
WHERE = types.InputPeerUser(user_id=1001, access_hash=3003)


def uploaded_photo() -> types.InputMediaUploadedPhoto:
    return types.InputMediaUploadedPhoto(
        file=types.InputFile(id=1, parts=1, name="a.jpg", md5_checksum="")
    )


def uploaded_document() -> types.InputMediaUploadedDocument:
    return types.InputMediaUploadedDocument(
        file=types.InputFile(id=2, parts=1, name="a.pdf", md5_checksum=""),
        mime_type="application/pdf",
        attributes=[],
    )


class TestPolls:
    def test_the_answers_are_numbered_from_zero(self):
        made = attachments.as_poll("Which?", ["A", "B", "C"])
        assert [answer.option for answer in made.poll.answers] == [
            b"\x00",
            b"\x01",
            b"\x02",
        ]

    def test_the_texts_survive(self):
        made = attachments.as_poll("Which?", ["A", "B"])
        assert made.poll.question.text == "Which?"
        assert [answer.text.text for answer in made.poll.answers] == ["A", "B"]

    def test_naming_a_correct_answer_makes_it_a_quiz(self):
        made = attachments.as_poll("Which?", ["A", "B"], correct=1)
        assert made.poll.quiz
        assert made.correct_answers == [1]

    def test_a_quiz_without_an_answer_is_refused(self):
        with pytest.raises(ValueError, match="which answer is the right one"):
            attachments.as_poll("Which?", ["A", "B"], quiz=True)

    def test_an_answer_that_is_not_there(self):
        with pytest.raises(ValueError, match="not one of the 2"):
            attachments.as_poll("Which?", ["A", "B"], correct=5)

    def test_an_explanation_needs_a_quiz(self):
        with pytest.raises(ValueError, match="only a quiz has an explanation"):
            attachments.as_poll("Which?", ["A", "B"], explanation="because")

    def test_too_many_answers(self):
        with pytest.raises(ValueError, match="at most 12"):
            attachments.as_poll("Which?", [str(n) for n in range(13)])

    def test_no_answers_at_all(self):
        with pytest.raises(ValueError, match="needs some answers"):
            attachments.as_poll("Which?", [])

    def test_anonymous_by_default(self):
        assert not attachments.as_poll("Q", ["A"]).poll.public_voters
        assert attachments.as_poll("Q", ["A"], anonymous=False).poll.public_voters

    def test_a_position_is_one_byte(self):
        assert attachments.option_bytes(3) == b"\x03"
        with pytest.raises(ValueError, match="not a poll answer position"):
            attachments.option_bytes(-1)

    async def test_voting_sends_positions_as_bytes(self):
        async with live() as (invoker, server):
            await messages.vote_poll(invoker, WHERE, 7, [0, 2])
        call = server.only(functions.messages.SendVote)
        assert call.options == [b"\x00", b"\x02"]
        assert call.msg_id == 7

    async def test_retracting_a_vote_sends_nothing(self):
        async with live() as (invoker, server):
            await messages.vote_poll(invoker, WHERE, 7, [])
        assert server.only(functions.messages.SendVote).options == []

    async def test_closing_edits_the_message_with_a_closed_poll(self):
        async with live() as (invoker, server):
            await messages.close_poll(invoker, WHERE, 7)
        call = server.only(functions.messages.EditMessage)
        assert call.id == 7
        assert call.media.poll.closed
        # The question is not sent again: that would be a second poll rather
        # than this one ending.
        assert call.media.poll.answers == []


class TestOtherAttachments:
    def test_dice_take_a_name_or_the_emoji(self):
        assert attachments.as_dice("dice").emoticon == "\N{GAME DIE}"
        assert attachments.as_dice("slots").emoticon == "\N{SLOT MACHINE}"
        assert attachments.as_dice("\N{BOWLING}").emoticon == "\N{BOWLING}"

    def test_a_location_is_a_point(self):
        made = attachments.as_location(51.5, -0.12)
        assert (made.geo_point.lat, made.geo_point.long) == (51.5, -0.12)

    def test_a_venue_is_a_point_with_a_name(self):
        made = attachments.as_venue(51.5, -0.12, "Somewhere", "1 Road")
        assert made.title == "Somewhere" and made.address == "1 Road"
        assert made.geo_point.lat == 51.5

    def test_a_contact_carries_the_name(self):
        made = attachments.as_contact("+441234", "Pavel", last_name="D")
        assert (made.phone_number, made.first_name, made.last_name) == (
            "+441234",
            "Pavel",
            "D",
        )

    def test_pointing_at_a_document(self):
        document = types.Document(
            id=9,
            access_hash=8,
            file_reference=b"ref",
            date=0,
            mime_type="image/webp",
            size=10,
            dc_id=2,
            attributes=[],
        )
        made = attachments.as_document(document)
        assert made.id.id == 9 and made.id.file_reference == b"ref"

    def test_an_input_media_passes_straight_through(self):
        already = types.InputMediaDocument(
            id=types.InputDocument(id=1, access_hash=2, file_reference=b"")
        )
        assert attachments.as_document(already) is already

    def test_something_that_is_not_a_document(self):
        with pytest.raises(TypeError, match="not a document"):
            attachments.as_document("a string")


class TestReactions:
    def test_a_string_is_an_emoji(self):
        assert reactions.as_reaction("\N{THUMBS UP SIGN}").emoticon == (
            "\N{THUMBS UP SIGN}"
        )

    def test_a_number_is_a_custom_emoji(self):
        assert reactions.as_reaction(555).document_id == 555

    async def test_reacting_sets_the_whole_list(self):
        async with live() as (invoker, server):
            await reactions.send_reaction(invoker, WHERE, 7, "\N{THUMBS UP SIGN}")
        call = server.only(functions.messages.SendReaction)
        assert len(call.reaction) == 1
        assert call.msg_id == 7
        assert call.add_to_recent

    async def test_reacting_with_nothing_clears(self):
        async with live() as (invoker, server):
            await reactions.send_reaction(invoker, WHERE, 7, None)
        call = server.only(functions.messages.SendReaction)
        assert call.reaction is None
        # Clearing must not push an emoji into the recently-used list.
        assert not call.add_to_recent

    async def test_several_reactions_at_once(self):
        async with live() as (invoker, server):
            await reactions.send_reaction(invoker, WHERE, 7, ["a", 5])
        call = server.only(functions.messages.SendReaction)
        assert [type(one).__name__ for one in call.reaction] == [
            "ReactionEmoji",
            "ReactionCustomEmoji",
        ]


class TestAlbums:
    def test_a_photo_and_a_document_cannot_share_one(self):
        with pytest.raises(ValueError, match="cannot share one album"):
            albums.check_album([uploaded_photo(), uploaded_document()])

    def test_too_many_files(self):
        with pytest.raises(ValueError, match="at most 10"):
            albums.check_album([uploaded_photo() for _ in range(11)])

    def test_an_empty_album(self):
        with pytest.raises(ValueError, match="needs something in it"):
            albums.check_album([])

    async def test_every_file_is_registered_before_it_is_sent(self):
        async with live() as (invoker, server):
            server.answer_with = _album_answers
            await albums.send_album(
                invoker, WHERE, [uploaded_photo(), uploaded_photo()]
            )
        # The step everybody forgets: sendMultiMedia will not take an uploaded
        # file, only something the server has already seen.
        assert len(server.all(functions.messages.UploadMedia)) == 2
        parts = server.only(functions.messages.SendMultiMedia).multi_media
        assert all(
            isinstance(part.media, types.InputMediaPhoto) for part in parts
        )

    async def test_something_already_registered_costs_no_call(self):
        already = types.InputMediaDocument(
            id=types.InputDocument(id=1, access_hash=2, file_reference=b"")
        )
        async with live() as (invoker, server):
            server.answer_with = _album_answers
            await albums.send_album(invoker, WHERE, [already, already])
        assert not server.all(functions.messages.UploadMedia)

    async def test_every_part_gets_its_own_random_id(self):
        async with live() as (invoker, server):
            server.answer_with = _album_answers
            await albums.send_album(
                invoker, WHERE, [uploaded_photo() for _ in range(3)]
            )
        parts = server.only(functions.messages.SendMultiMedia).multi_media
        assert len({part.random_id for part in parts}) == 3

    async def test_captions_line_up_with_files(self):
        async with live() as (invoker, server):
            server.answer_with = _album_answers
            await albums.send_album(
                invoker,
                WHERE,
                [uploaded_photo(), uploaded_photo()],
                captions=[("first", []), ("second", [])],
            )
        parts = server.only(functions.messages.SendMultiMedia).multi_media
        assert [part.message for part in parts] == ["first", "second"]

    async def test_the_wrong_number_of_captions(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="one caption per file"):
                await albums.send_album(
                    invoker,
                    WHERE,
                    [uploaded_photo(), uploaded_photo()],
                    captions=[("only one", [])],
                )

    async def test_the_messages_come_back_in_order(self):
        async with live() as (invoker, server):
            server.answer_with = _album_answers
            sent = await albums.send_album(
                invoker, WHERE, [uploaded_photo() for _ in range(3)]
            )
        assert [message.id for message in sent] == sorted(
            message.id for message in sent
        )
        assert len(sent) == 3

    async def test_a_server_that_describes_fewer_than_were_sent(self):
        async with live() as (invoker, server):
            server.answer_with = _one_message_short
            with pytest.raises(SunnygramError, match="described"):
                await albums.send_album(
                    invoker, WHERE, [uploaded_photo(), uploaded_photo()]
                )


def _album_answers(query: Any) -> Any:
    if isinstance(query, functions.messages.UploadMedia):
        return types.MessageMediaPhoto(
            photo=types.Photo(
                id=42,
                access_hash=43,
                file_reference=b"ref",
                date=0,
                sizes=[],
                dc_id=2,
            )
        )
    if isinstance(query, functions.messages.SendMultiMedia):
        return _sent(query.multi_media)
    return types.Updates(updates=[], users=[], chats=[], date=0, seq=0)


def _one_message_short(query: Any) -> Any:
    if isinstance(query, functions.messages.SendMultiMedia):
        return _sent(query.multi_media[:1])
    return _album_answers(query)


def _sent(parts: list[Any]) -> types.Updates:
    updates: list[Any] = []
    for index, part in enumerate(parts):
        message_id = 500 + index
        updates.append(
            types.UpdateMessageID(id=message_id, random_id=part.random_id)
        )
        updates.append(
            types.UpdateNewMessage(
                message=types.Message(
                    id=message_id,
                    peer_id=types.PeerUser(user_id=1001),
                    date=1700000000,
                    message=part.message,
                    grouped_id=999,
                ),
                pts=100 + index,
                pts_count=1,
            )
        )
    return types.Updates(
        updates=updates, users=[], chats=[], date=1700000000, seq=0
    )


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


class RecordingServer(ScriptedServer):
    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.seen: list[Any] = []
        self.answer_with: Any = None

    async def serve(self) -> None:
        while True:
            request = await self.take()
            self.seen.append(request.query)
            try:
                made = (
                    self.answer_with(request.query)
                    if self.answer_with is not None
                    else types.Updates(
                        updates=[], users=[], chats=[], date=1700000000, seq=0
                    )
                )
            except Exception as failure:
                # A scripted answer that raises would otherwise take this task
                # down quietly and leave the caller waiting out its timeout, so
                # the mistake comes back as an error the test can read.
                await self.refuse(request.msg_id, 500, f"SCRIPT_FAILED: {failure!r}")
                continue
            await self.answer(request.msg_id, made)

    def all(self, kind: type) -> list[Any]:
        return [query for query in self.seen if isinstance(query, kind)]

    def only(self, kind: type) -> Any:
        found = self.all(kind)
        assert len(found) == 1, f"expected one {kind.__name__}, got {len(found)}"
        return found[0]


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
        timeout=5.0,
        rate_limit=False,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = RecordingServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
