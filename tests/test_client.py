"""The client, and the three things it is made of.

Filters answer questions about a message, the dispatcher decides who gets one,
and the client turns an update off the wire into a message a handler can answer.
The end of this file is the part worth having: a server pushes a message, a
handler written the way anybody would write one receives it, replies, and the
reply is checked on the other side.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram import filters
from sunnygram.client import Client, compose
from sunnygram.dispatcher import Dispatcher, Handler, StopPropagation
from sunnygram.errors import NoAnswer, RPCError, SunnygramError
from sunnygram.network import Address
from sunnygram.raw import functions, types
from sunnygram.types import MemberStatus
from sunnygram.storage import MemoryStorage, PeerKind, SessionState
from sunnygram.types import (
    Button,
    CallbackQuery,
    Chat,
    Message,
    User,
    keyboard,
)
from sunnygram.updates import IDLE_CATCH_UP, Event

ME = 777000
OTHER = 1001
GROUP = 5005
CHANNEL = 7007


def a_user(id: int = OTHER, **flags: Any) -> types.User:
    return types.User(
        id=id,
        access_hash=id * 3,
        first_name=flags.pop("first_name", "Pavel"),
        last_name=flags.pop("last_name", None),
        username=flags.pop("username", "durov"),
        **flags,
    )


def a_group(id: int = GROUP) -> types.Chat:
    return types.Chat(
        id=id,
        title="A group",
        photo=types.ChatPhotoEmpty(),
        participants_count=3,
        date=0,
        version=1,
    )


def a_channel(id: int = CHANNEL, *, megagroup: bool = False) -> types.Channel:
    return types.Channel(
        id=id,
        access_hash=id * 3,
        title="A channel",
        username="news",
        photo=types.ChatPhotoEmpty(),
        date=0,
        megagroup=megagroup,
    )


def a_message(
    id: int = 1,
    text: str = "hello",
    *,
    peer: Any = None,
    from_id: Any = None,
    out: bool = False,
    media: Any = None,
    entities: list[Any] | None = None,
) -> types.Message:
    return types.Message(
        id=id,
        peer_id=peer or types.PeerUser(user_id=OTHER),
        from_id=from_id,
        date=1700000000,
        message=text,
        out=out,
        media=media,
        entities=entities,
    )


def a_document_media(reference: bytes = b"ref") -> types.MessageMediaDocument:
    return types.MessageMediaDocument(
        document=types.Document(
            id=90210,
            access_hash=4242,
            file_reference=reference,
            date=0,
            mime_type="audio/mpeg",
            size=1234,
            dc_id=2,
            attributes=[types.DocumentAttributeFilename(file_name="song.mp3")],
        )
    )


def wrap(
    message: types.Message | None = None,
    *,
    users: list[Any] | None = None,
    chats: list[Any] | None = None,
    client: Any = None,
) -> Message:
    found = Message.from_raw(
        message or a_message(),
        users={user.id: user for user in (users or [a_user()])},
        chats={chat.id: chat for chat in (chats or [])},
        client=client,
    )
    assert found is not None
    return found


class Pretend:
    """A stand-in for a client, which is all compose asks anything to be."""

    def __init__(self, name: str, log: list[str], *, fails: bool = False) -> None:
        self.name = name
        self.log = log
        self.fails = fails

    async def start(self, **_options: Any) -> None:
        if self.fails:
            raise SunnygramError(f"{self.name} could not start")
        self.log.append(f"start {self.name}")

    async def stop(self) -> None:
        self.log.append(f"stop {self.name}")


class TestComposing:
    """Several clients on one loop. compose makes the loop, so no async here."""

    def test_they_start_in_order_and_stop_in_reverse(self):
        log: list[str] = []

        class Interrupts(Pretend):
            async def start(self, **options: Any) -> None:
                await super().start(**options)
                # Stand in for the person pressing ctrl-c, once everything is up.
                task = asyncio.current_task()
                assert task is not None
                asyncio.get_running_loop().call_later(0.02, task.cancel)

        compose([Pretend("a", log), Pretend("b", log), Interrupts("c", log)])
        assert log == [
            "start a",
            "start b",
            "start c",
            "stop c",
            "stop b",
            "stop a",
        ]

    def test_one_that_cannot_start_stops_the_ones_that_did(self):
        log: list[str] = []
        with pytest.raises(SunnygramError, match="could not start"):
            compose([Pretend("a", log), Pretend("b", log, fails=True), Pretend("c", log)])
        # b never started so it is not stopped, and c was never reached.
        assert log == ["start a", "stop a"]


class TestBuildingOne:
    """Options the client holds for something underneath it."""

    def a_client(self, **options: Any) -> Client:
        return Client(MemoryStorage(), api_id=1, api_hash="hash", **options)

    def test_the_silence_the_watchdog_waits_out_is_the_managers_own(self):
        assert self.a_client().updates.idle_catch_up == IDLE_CATCH_UP

    def test_and_it_can_be_moved_or_turned_off_from_here(self):
        assert self.a_client(idle_catch_up=60).updates.idle_catch_up == 60
        assert self.a_client(idle_catch_up=0).updates.idle_catch_up == 0


class TestWrapping:
    def test_a_message_carries_the_useful_parts(self):
        message = wrap(a_message(7, "hi there"))
        assert message.id == 7
        assert message.text == "hi there"
        assert message.chat is not None and message.chat.is_private
        assert message.sender is not None and message.sender.username == "durov"
        assert message.date == datetime.fromtimestamp(1700000000, timezone.utc)

    def test_a_group_message_knows_both_who_and_where(self):
        message = wrap(
            a_message(peer=types.PeerChat(chat_id=GROUP), from_id=types.PeerUser(user_id=OTHER)),
            chats=[a_group()],
        )
        assert message.chat is not None and message.chat.is_group
        assert message.chat.title == "A group"
        assert message.sender is not None and message.sender.id == OTHER

    def test_a_channel_is_not_a_group(self):
        message = wrap(
            a_message(peer=types.PeerChannel(channel_id=CHANNEL)), chats=[a_channel()]
        )
        assert message.chat is not None
        assert message.chat.is_channel
        assert not message.chat.is_group

    def test_a_supergroup_is_a_group(self):
        message = wrap(
            a_message(peer=types.PeerChannel(channel_id=CHANNEL)),
            chats=[a_channel(megagroup=True)],
        )
        assert message.chat is not None and message.chat.is_group

    def test_a_service_message_has_no_text(self):
        service = types.MessageService(
            id=3,
            peer_id=types.PeerChat(chat_id=GROUP),
            date=0,
            action=types.MessageActionChatJoinedByLink(inviter_id=OTHER),
        )
        message = Message.from_raw(service, chats={GROUP: a_group()})
        assert message is not None
        assert message.service and message.text == ""

    def test_formatting_comes_back_out(self):
        message = wrap(
            a_message(text="bold", entities=[types.MessageEntityBold(offset=0, length=4)])
        )
        assert message.markdown == "**bold**"
        assert message.html == "<b>bold</b>"

    def test_a_user_reads_nicely(self):
        wrapped = User.from_raw(a_user(last_name="Durov"))
        assert wrapped is not None
        assert wrapped.full_name == "Pavel Durov"
        assert wrapped.mention == f"[Pavel Durov](tg://user?id={OTHER})"

    def test_a_chat_from_a_user_is_private(self):
        chat = Chat.from_raw(a_user())
        assert chat is not None and chat.kind is PeerKind.USER and chat.is_private

    def test_nothing_useful_wraps_to_nothing(self):
        assert Message.from_raw(types.UpdateNewMessage(message=a_message(), pts=1, pts_count=1)) is None
        assert User.from_raw(types.UserEmpty(id=1)) is None
        assert Chat.from_raw(None) is None


class TestFilters:
    async def test_text_and_media(self):
        assert await filters.text(None, wrap())
        assert not await filters.media(None, wrap())
        with_photo = wrap(a_message(media=types.MessageMediaPhoto()))
        assert await filters.media(None, with_photo)
        assert await filters.photo(None, with_photo)

    async def test_where_it_happened(self):
        private = wrap()
        assert await filters.private(None, private)
        assert not await filters.group(None, private)
        in_group = wrap(
            a_message(peer=types.PeerChat(chat_id=GROUP)), chats=[a_group()]
        )
        assert await filters.group(None, in_group)

    async def test_which_way_it_went(self):
        assert await filters.incoming(None, wrap())
        assert await filters.outgoing(None, wrap(a_message(out=True)))

    async def test_and_or_not(self):
        message = wrap()
        assert await (filters.text & filters.private)(None, message)
        assert not await (filters.text & filters.outgoing)(None, message)
        assert await (filters.outgoing | filters.text)(None, message)
        assert await (~filters.outgoing)(None, message)

    async def test_a_filter_reads_as_what_it_is(self):
        assert repr(filters.text & ~filters.outgoing) == "(text & ~outgoing)"

    async def test_a_command_leaves_its_pieces_behind(self):
        message = wrap(a_message(text="/ban 30 spamming"))
        assert await filters.command("ban")(None, message)
        assert message.command == "ban"
        assert message.arguments == ["30", "spamming"]

    async def test_a_command_can_be_addressed(self):
        message = wrap(a_message(text="/ban@mybot someone"))
        assert await filters.command("ban", to_me=True)(None, message)
        assert not await filters.command("ban", to_me=True)(
            None, wrap(a_message(text="/ban someone"))
        )

    async def test_a_command_is_not_a_word_that_starts_with_one(self):
        assert not await filters.command("ban")(None, wrap(a_message(text="/banana")))

    async def test_regex_leaves_the_match_behind(self):
        message = wrap(a_message(text="order 66 please"))
        assert await filters.regex(r"order (\d+)")(None, message)
        assert message.match.group(1) == "66"

    async def test_by_who_and_by_where(self):
        message = wrap()
        assert await filters.user(OTHER)(None, message)
        assert await filters.user("@durov")(None, message)
        assert not await filters.user(12345)(None, message)
        assert await filters.chat(OTHER)(None, message)

    async def test_one_of_your_own_can_be_async(self):
        async def slow(client: Any, message: Message) -> bool:
            await asyncio.sleep(0)
            return message.text == "hello"

        assert await filters.make(slow)(None, wrap())


class TestDispatching:
    async def test_a_handler_gets_what_it_asked_for(self):
        seen: list[Message] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=lambda client, m: _record(seen, m), filters=filters.text)
        )
        await dispatcher.feed(None, _event())
        assert len(seen) == 1 and seen[0].text == "hello"

    async def test_a_filter_that_says_no_keeps_it_away(self):
        seen: list[Message] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=lambda client, m: _record(seen, m), filters=filters.outgoing)
        )
        await dispatcher.feed(None, _event())
        assert seen == []

    async def test_groups_run_in_order_and_everybody_runs(self):
        order: list[str] = []
        dispatcher = Dispatcher()
        dispatcher.add(
            Handler(callback=lambda c, m: _note(order, "second"), group=1)
        )
        dispatcher.add(Handler(callback=lambda c, m: _note(order, "first"), group=0))
        dispatcher.add(Handler(callback=lambda c, m: _note(order, "also first")))
        await dispatcher.feed(None, _event())
        assert order == ["first", "also first", "second"]

    async def test_stopping_means_stopping(self):
        order: list[str] = []
        dispatcher = Dispatcher()

        async def halt(client: Any, message: Message) -> None:
            order.append("halt")
            raise StopPropagation

        dispatcher.add(Handler(callback=halt, group=0))
        dispatcher.add(Handler(callback=lambda c, m: _note(order, "never"), group=1))
        await dispatcher.feed(None, _event())
        assert order == ["halt"]

    async def test_one_handler_failing_does_not_stop_the_rest(self):
        order: list[str] = []
        failures: list[BaseException] = []
        dispatcher = Dispatcher()
        dispatcher.on_error = lambda failure, handler: failures.append(failure)

        async def broken(client: Any, message: Message) -> None:
            raise ValueError("a typo in one feature")

        dispatcher.add(Handler(callback=broken, group=0))
        dispatcher.add(Handler(callback=lambda c, m: _note(order, "still ran"), group=1))
        await dispatcher.feed(None, _event())
        assert order == ["still ran"]
        assert dispatcher.errors == 1
        assert isinstance(failures[0], ValueError)

    async def test_a_raw_handler_sees_everything(self):
        seen: list[Any] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=lambda c, e: _record(seen, e), kind="raw"))
        await dispatcher.feed(None, Event(types.UpdateUserTyping(user_id=OTHER, action=types.SendMessageTypingAction())))
        assert len(seen) == 1
        assert isinstance(seen[0], Event)

    async def test_an_edit_is_not_a_new_message(self):
        seen: list[str] = []
        dispatcher = Dispatcher()
        dispatcher.add(Handler(callback=lambda c, m: _note(seen, "new"), kind="message"))
        dispatcher.add(Handler(callback=lambda c, m: _note(seen, "edited"), kind="edited"))
        await dispatcher.feed(
            None,
            Event(
                types.UpdateEditMessage(message=a_message(), pts=1, pts_count=1),
                users={OTHER: a_user()},
            ),
        )
        assert seen == ["edited"]


async def _until(condition: Any, timeout: float = 5.0) -> None:
    """Wait for something the client does in its own time."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not condition():
        if loop.time() > deadline:
            raise AssertionError("the client never got there")
        await asyncio.sleep(0.01)


async def _record(into: list[Any], value: Any) -> None:
    into.append(value)


async def _note(into: list[str], value: str) -> None:
    into.append(value)


def _event() -> Event:
    return Event(
        types.UpdateNewMessage(message=a_message(), pts=1, pts_count=1),
        users={OTHER: a_user()},
    )


def a_forum_topic(id: int, *, title: str = "Bugs") -> types.ForumTopic:
    return types.ForumTopic(
        id=id,
        date=1700000000,
        peer=types.PeerChannel(channel_id=CHANNEL),
        title=title,
        icon_color=0x6FB9F0,
        top_message=id,
        read_inbox_max_id=0,
        read_outbox_max_id=0,
        unread_count=0,
        unread_mentions_count=0,
        unread_reactions_count=0,
        unread_poll_votes_count=0,
        from_id=types.PeerUser(user_id=ME),
        notify_settings=types.PeerNotifySettings(),
    )


def _forum_topics(query: Any) -> Any:
    """The topics a forum has, or the particular ones that were asked for."""
    wanted = getattr(query, "topics", None) or [10, 20]
    topics = [a_forum_topic(id, title=f"Topic {id}") for id in wanted]
    return types.messages.ForumTopics(
        count=len(topics),
        topics=topics,
        messages=[a_message(topic.id, f"opened {topic.id}") for topic in topics],
        chats=[a_channel(megagroup=True)],
        users=[a_user()],
        pts=1,
    )


class ClientServer(ScriptedServer):
    """Enough of a datacenter to sign in, send, and be answered."""

    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.sent: list[Any] = []
        self.asked: list[Any] = []
        self.parts: list[Any] = []
        self.registered: list[Any] = []
        self.edited: list[Any] = []
        self.next_id = 500
        # Pushed updates have to walk the counter forward one at a time, or
        # the second one is judged as something already seen and dropped.
        self.next_pts = 2
        # How many of the next sendMedia calls to refuse the way the server
        # does when the token inside a file reference has aged out. One, and a
        # client that renews and tries again gets through; more than the client
        # will retry, and it does not.
        self.stale_sends = 0
        # Whether messages fetched by id carry a file, which is what a client
        # renewing a stale reference has to find in them.
        self.messages_carry_media = False
        # A message that has been deleted since whatever referred to it was
        # written down, which is what a stale file reference runs into.
        self.messages_are_gone = False
        # Answer a send with updateShortSentMessage instead of a full Updates,
        # which is what a real datacenter does for a private chat and what this
        # server did not do for a long time. The difference is the whole reason
        # a sent message could not be edited: the shorthand names no chat.
        self.sends_are_short = False

    def only(self, kind: type) -> list[Any]:
        """Every call of one kind that reached this server."""
        return [call for call in self.asked if isinstance(call, kind)]

    def _album(self, parts: list[Any]) -> types.Updates:
        """What a datacenter answers a multi-media send with: one id update and
        one message per part, sharing a group id."""
        updates: list[Any] = []
        for part in parts:
            self.next_id += 1
            updates.append(
                types.UpdateMessageID(id=self.next_id, random_id=part.random_id)
            )
            updates.append(
                types.UpdateNewMessage(
                    message=a_message(self.next_id, part.message, out=True),
                    pts=self._next_pts(),
                    pts_count=1,
                )
            )
        return types.Updates(
            updates=updates, users=[a_user()], chats=[], date=1700000000, seq=0
        )

    def _next_pts(self) -> int:
        """The next update counter, for anything that moves the stream on.

        One counter for every update this server produces, pushed or answered.
        The client drops an update whose pts it has already passed, which is
        correct of it and makes two sources of the number a trap.
        """
        pts, self.next_pts = self.next_pts, self.next_pts + 1
        return pts

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            self.asked.append(query)
            if isinstance(query, functions.updates.GetState):
                await self.answer(
                    request.msg_id,
                    types.updates.State(
                        pts=1, qts=0, date=1700000000, seq=1, unread_count=0
                    ),
                )
            elif isinstance(query, functions.users.GetUsers):
                await self.answer(request.msg_id, [a_user(ME, username="me", self_=True)])
            elif isinstance(query, functions.contacts.ResolveUsername):
                await self.answer(
                    request.msg_id,
                    types.contacts.ResolvedPeer(
                        peer=types.PeerUser(user_id=OTHER), chats=[], users=[a_user()]
                    ),
                )
            elif isinstance(query, functions.messages.SendMessage):
                self.sent.append(query)
                self.next_id += 1
                if self.sends_are_short:
                    await self.answer(
                        request.msg_id,
                        types.UpdateShortSentMessage(
                            id=self.next_id,
                            pts=self._next_pts(),
                            pts_count=1,
                            date=1700000000,
                            out=True,
                        ),
                    )
                    continue
                await self.answer(
                    request.msg_id,
                    types.Updates(
                        updates=[
                            types.UpdateMessageID(
                                id=self.next_id, random_id=query.random_id
                            ),
                            types.UpdateNewMessage(
                                message=a_message(
                                    self.next_id, query.message, out=True,
                                    entities=query.entities,
                                ),
                                # From the same counter push_message draws
                                # from. A fixed number here collided with the
                                # first pushed update, which the client then
                                # judged as one it had already seen and
                                # dropped: a test that sent something and then
                                # pushed a reply waited for ever, and the
                                # server was the one in the wrong.
                                pts=self._next_pts(),
                                pts_count=1,
                            ),
                        ],
                        users=[a_user()],
                        chats=[],
                        date=1700000000,
                        seq=0,
                    ),
                )
            elif isinstance(query, functions.messages.GetHistory):
                await self.answer(
                    request.msg_id,
                    types.messages.Messages(
                        messages=[
                            a_message(id, f"old {id}")
                            for id in range(query.offset_id - 1 if query.offset_id else 9, 0, -1)
                        ][: query.limit],
                        topics=[],
                        chats=[],
                        users=[a_user()],
                    ),
                )
            elif isinstance(query, functions.messages.SendMedia):
                self.sent.append(query)
                if self.stale_sends:
                    self.stale_sends -= 1
                    await self.refuse(request.msg_id, 400, "FILE_REFERENCE_EXPIRED")
                    continue
                self.next_id += 1
                await self.answer(
                    request.msg_id,
                    types.Updates(
                        updates=[
                            types.UpdateMessageID(
                                id=self.next_id, random_id=query.random_id
                            ),
                            types.UpdateNewMessage(
                                message=a_message(
                                    self.next_id,
                                    query.message,
                                    out=True,
                                    media=types.MessageMediaEmpty(),
                                ),
                                pts=2,
                                pts_count=1,
                            ),
                        ],
                        users=[a_user()],
                        chats=[],
                        date=1700000000,
                        seq=0,
                    ),
                )
            elif isinstance(query, functions.upload.SaveFilePart):
                self.parts.append(query)
                await self.answer(request.msg_id, True)
            elif isinstance(query, functions.messages.UploadMedia):
                self.registered.append(query)
                await self.answer(request.msg_id, a_document_media())
            elif isinstance(query, functions.messages.SendMultiMedia):
                self.sent.append(query)
                await self.answer(request.msg_id, self._album(query.multi_media))
            elif isinstance(query, functions.messages.GetMessages):
                await self.answer(
                    request.msg_id,
                    types.messages.Messages(
                        messages=[]
                        if self.messages_are_gone
                        else [
                            a_message(
                                one.id,
                                f"message {one.id}",
                                media=a_document_media(b"fresh")
                                if self.messages_carry_media
                                else None,
                            )
                            for one in query.id
                        ],
                        topics=[],
                        chats=[],
                        users=[a_user()],
                    ),
                )
            elif isinstance(query, functions.messages.EditMessage):
                self.edited.append(query)
                await self.answer(
                    request.msg_id,
                    types.Updates(
                        updates=[
                            types.UpdateEditMessage(
                                message=a_message(
                                    query.id, query.message or "edited", out=True
                                ),
                                pts=2,
                                pts_count=1,
                            )
                        ],
                        users=[a_user()],
                        chats=[],
                        date=1700000000,
                        seq=0,
                    ),
                )
            elif isinstance(
                query,
                (
                    functions.messages.SetBotCallbackAnswer,
                    functions.messages.EditInlineBotMessage,
                ),
            ):
                await self.answer(request.msg_id, True)
            elif isinstance(query, functions.messages.Search):
                start = query.offset_id or 20
                await self.answer(
                    request.msg_id,
                    types.messages.Messages(
                        messages=[
                            a_message(id, f"found {id}")
                            for id in range(start - 1, 0, -1)
                        ][: query.limit],
                        topics=[],
                        chats=[],
                        users=[a_user()],
                    ),
                )
            elif isinstance(query, functions.messages.GetDialogs):
                await self.answer(request.msg_id, self._dialogs(query))
            elif isinstance(query, functions.channels.GetParticipants):
                if isinstance(query.filter, types.ChannelParticipantsAdmins):
                    standing: Any = types.ChannelParticipantCreator(
                        user_id=OTHER,
                        admin_rights=types.ChatAdminRights(),
                        rank="founder",
                    )
                else:
                    standing = types.ChannelParticipant(user_id=OTHER, date=0)
                await self.answer(
                    request.msg_id,
                    types.channels.ChannelParticipants(
                        count=1,
                        participants=[standing] if query.offset == 0 else [],
                        chats=[],
                        users=[a_user()] if query.offset == 0 else [],
                    ),
                )
            elif isinstance(query, functions.users.GetFullUser):
                await self.answer(
                    request.msg_id,
                    types.users.UserFull(
                        full_user=types.UserFull(
                            id=OTHER,
                            settings=types.PeerSettings(),
                            notify_settings=types.PeerNotifySettings(),
                            about="a bio",
                            common_chats_count=0,
                        ),
                        chats=[],
                        users=[a_user()],
                    ),
                )
            elif isinstance(query, functions.channels.GetFullChannel):
                await self.answer(
                    request.msg_id,
                    types.messages.ChatFull(
                        full_chat=types.ChannelFull(
                            id=CHANNEL,
                            about="a channel",
                            read_inbox_max_id=0,
                            read_outbox_max_id=0,
                            unread_count=0,
                            chat_photo=types.PhotoEmpty(id=0),
                            notify_settings=types.PeerNotifySettings(),
                            bot_info=[],
                            pts=1,
                        ),
                        chats=[a_channel()],
                        users=[],
                    ),
                )
            elif isinstance(query, functions.contacts.GetContacts):
                await self.answer(
                    request.msg_id,
                    types.contacts.Contacts(
                        contacts=[types.Contact(user_id=OTHER, mutual=True)],
                        saved_count=1,
                        users=[a_user()],
                    ),
                )
            elif isinstance(
                query,
                (
                    functions.messages.DeleteMessages,
                    functions.channels.DeleteMessages,
                ),
            ):
                # Both spellings answer the same shape, which is the point: a
                # channel counts its own messages and takes the other call.
                await self.answer(
                    request.msg_id,
                    types.messages.AffectedMessages(
                        pts=self.next_pts, pts_count=len(query.id)
                    ),
                )
            elif isinstance(query, functions.account.UpdateProfile):
                await self.answer(
                    request.msg_id,
                    a_user(ME, username="me", self_=True, first_name=query.first_name),
                )
            elif isinstance(
                query,
                (
                    functions.messages.GetForumTopics,
                    functions.messages.GetForumTopicsByID,
                ),
            ):
                await self.answer(request.msg_id, _forum_topics(query))
            elif isinstance(query, functions.messages.CreateForumTopic):
                self.next_id += 1
                await self.answer(
                    request.msg_id,
                    types.Updates(
                        updates=[
                            types.UpdateMessageID(
                                id=self.next_id, random_id=query.random_id
                            )
                        ],
                        users=[],
                        chats=[],
                        date=1700000000,
                        seq=0,
                    ),
                )
            elif isinstance(
                query,
                (
                    functions.messages.ReadHistory,
                    functions.channels.ReadHistory,
                    functions.messages.EditForumTopic,
                    functions.messages.UpdatePinnedForumTopic,
                    functions.messages.UpdatePinnedMessage,
                    functions.messages.UnpinAllMessages,
                    functions.messages.SetTyping,
                    functions.contacts.Block,
                    functions.contacts.Unblock,
                    functions.channels.JoinChannel,
                    functions.channels.LeaveChannel,
                ),
            ):
                # None of these answer with anything worth building: a bool, or
                # updates nobody in these tests is reading. What is being tested
                # is that the right call went out with the right arguments.
                await self.answer(request.msg_id, self._acknowledge(query))
            else:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")

    def _acknowledge(self, query: Any) -> Any:
        if isinstance(
            query,
            (
                functions.messages.ReadHistory,
                functions.contacts.Block,
                functions.contacts.Unblock,
            ),
        ):
            return True
        return types.Updates(
            updates=[], users=[], chats=[], date=1700000000, seq=0
        )

    def _dialogs(self, query: functions.messages.GetDialogs) -> Any:
        """One page of dialogs, walking backwards the way the real one does."""
        start = query.offset_id - 1 if query.offset_id else 9
        ids = list(range(start, 0, -1))[: query.limit]
        if not ids:
            return types.messages.Dialogs(
                dialogs=[], messages=[], chats=[], users=[a_user()]
            )
        return types.messages.DialogsSlice(
            count=9,
            dialogs=[
                types.Dialog(
                    peer=types.PeerUser(user_id=OTHER),
                    top_message=id,
                    read_inbox_max_id=0,
                    read_outbox_max_id=0,
                    unread_count=id,
                    unread_mentions_count=0,
                    unread_reactions_count=0,
                    unread_poll_votes_count=0,
                    notify_settings=types.PeerNotifySettings(),
                )
                for id in ids
            ],
            messages=[a_message(id, f"last {id}") for id in ids],
            chats=[],
            users=[a_user()],
        )

    async def push_message(
        self, text: str, message_id: int = 42, *, reply_to: Any = None
    ) -> None:
        """Send the client a message, the way a real one arrives."""
        message = a_message(message_id, text)
        message.reply_to = reply_to
        pts = self._next_pts()
        await self.push(
            types.Updates(
                updates=[
                    types.UpdateNewMessage(message=message, pts=pts, pts_count=1)
                ],
                users=[a_user()],
                chats=[],
                date=1700000000,
                seq=0,
            ).to_bytes()
        )

    async def push_press(self, data: bytes = b"yes", message_id: int = 42) -> None:
        """Send the client a button press, the way a real one arrives."""
        await self.push(
            types.Updates(
                updates=[
                    types.UpdateBotCallbackQuery(
                        query_id=12345,
                        user_id=OTHER,
                        peer=types.PeerUser(user_id=OTHER),
                        msg_id=message_id,
                        chat_instance=999,
                        data=data,
                    )
                ],
                users=[a_user()],
                chats=[],
                date=1700000000,
                seq=0,
            ).to_bytes()
        )


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


@asynccontextmanager
async def live(**options: Any) -> AsyncIterator[tuple[Client, ClientServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    client = Client(
        MemoryStorage(session),
        api_id=12345,
        api_hash="0" * 32,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
        # One socket, so the single scripted server below answers everything.
        # A transfer would otherwise open its own connections and wait forever
        # on wires nobody is listening to; the pool has its own tests.
        bulk_connections=0,
        **options,
    )
    await client.invoker.start()
    connection = client.invoker.connection
    assert connection is not None
    server = ClientServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    # The invoker is already up, so start only has the signing in and the
    # update stream left to do.
    await client.start()
    try:
        yield client, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await client.stop()


class TestTheClient:
    async def test_starting_says_who_we_are(self):
        async with live() as (client, server):
            assert client.me is not None
            assert client.me.id == ME
            assert client.running

    async def test_a_message_goes_out_and_comes_back_wrapped(self):
        async with live() as (client, server):
            sent = await client.send_message("@durov", "hello")
            assert isinstance(sent, Message)
            assert sent.text == "hello"
            assert sent.outgoing

    async def test_markdown_is_the_default_and_is_parsed(self):
        async with live() as (client, server):
            await client.send_message("@durov", "**bold**")
            call = server.sent[0]
            assert call.message == "bold"
            assert isinstance(call.entities[0], types.MessageEntityBold)

    async def test_html_can_be_asked_for(self):
        async with live(parse_mode="html") as (client, server):
            await client.send_message("@durov", "<i>slanted</i>")
            assert server.sent[0].message == "slanted"
            assert isinstance(server.sent[0].entities[0], types.MessageEntityItalic)

    async def test_no_parse_mode_sends_the_text_as_written(self):
        async with live() as (client, server):
            await client.send_message("@durov", "**as written**", parse_mode=None)
            assert server.sent[0].message == "**as written**"
            assert not server.sent[0].entities

    async def test_entities_given_by_hand_are_used_as_they_are(self):
        async with live() as (client, server):
            given = [types.MessageEntityCode(offset=0, length=4)]
            await client.send_message("@durov", "code", entities=given)
            assert server.sent[0].entities == given

    async def test_a_username_is_resolved_once_and_then_known(self):
        async with live() as (client, server):
            await client.send_message("@durov", "one")
            await client.send_message("@durov", "two")
            resolves = [
                call
                for call in server.asked
                if isinstance(call, functions.contacts.ResolveUsername)
            ]
            assert len(resolves) == 1

    async def test_history_pages_itself(self):
        async with live() as (client, server):
            got = [
                message.text
                async for message in client.get_history("@durov", limit=5, batch=3)
            ]
            assert len(got) == 5
            assert got[0] == "old 9"

    async def test_an_arriving_message_reaches_a_handler_and_can_be_answered(self):
        # The whole library, end to end: an update off the wire becomes a
        # Message, a filter says yes, a handler replies, and the reply is a
        # real call on the other side.
        answered = asyncio.Event()

        async with live() as (client, server):

            @client.on_message(filters.text & filters.incoming)
            async def echo(app: Client, message: Message) -> None:
                await message.reply(f"you said {message.text}")
                answered.set()

            client.invoker.peers.learn(a_user())
            await server.push_message("ping")
            await asyncio.wait_for(answered.wait(), 5)

            assert server.sent[0].message == "you said ping"
            assert server.sent[0].reply_to.reply_to_msg_id == 42

    async def test_a_handler_can_be_removed_again(self):
        async with live() as (client, server):
            seen: list[Message] = []
            handler = client.add_handler(lambda app, m: _record(seen, m))
            client.remove_handler(handler)
            client.invoker.peers.learn(a_user())
            await server.push_message("ignored")
            await asyncio.sleep(0.05)
            assert seen == []

    async def test_the_client_reads_as_what_it_is(self):
        async with live() as (client, server):
            client.add_handler(lambda app, m: _record([], m))
            assert "1 handlers" in repr(client)


class TestSendingFiles:
    async def test_a_photo_goes_up_and_out_as_a_photo(self, tmp_path):
        picture = tmp_path / "cat.jpg"
        picture.write_bytes(b"not really a jpeg, but bytes are bytes")

        async with live() as (client, server):
            sent = await client.send_photo("@durov", picture, caption="**mine**")
            assert isinstance(sent, Message)
            assert server.parts, "the file never went up"
            call = server.sent[0]
            assert isinstance(call.media, types.InputMediaUploadedPhoto)
            assert call.message == "mine"
            assert isinstance(call.entities[0], types.MessageEntityBold)

    async def test_the_kind_is_worked_out_from_the_name(self, tmp_path):
        clip = tmp_path / "clip.mp4"
        clip.write_bytes(b"pretend video")

        async with live() as (client, server):
            await client.send_file("@durov", clip)
            media = server.sent[0].media
            assert isinstance(media, types.InputMediaUploadedDocument)
            assert media.mime_type == "video/mp4"
            kinds = [type(one) for one in media.attributes]
            assert types.DocumentAttributeVideo in kinds
            assert types.DocumentAttributeFilename in kinds

    async def test_a_picture_sent_as_a_document_is_kept_as_it_is(self, tmp_path):
        picture = tmp_path / "cat.png"
        picture.write_bytes(b"pretend png")

        async with live() as (client, server):
            await client.send_document("@durov", picture)
            media = server.sent[0].media
            assert isinstance(media, types.InputMediaUploadedDocument)
            # Without this Telegram would re-encode it back into a photo,
            # which is the whole reason somebody sent it as a file.
            assert media.force_file

    async def test_a_voice_note_says_it_is_one(self, tmp_path):
        note = tmp_path / "note.ogg"
        note.write_bytes(b"pretend audio")

        async with live() as (client, server):
            await client.send_voice("@durov", note, duration=7)
            audio = server.sent[0].media.attributes[0]
            assert isinstance(audio, types.DocumentAttributeAudio)
            assert audio.voice
            assert audio.duration == 7

    async def test_bytes_with_no_name_go_as_a_document(self):
        async with live() as (client, server):
            await client.send_file("@durov", b"just bytes", name=None)
            assert isinstance(
                server.sent[0].media, types.InputMediaUploadedDocument
            )


class TestMessageMethods:
    async def test_messages_can_be_fetched_by_id(self):
        async with live() as (client, server):
            got = await client.get_messages("@durov", [7, 9])
            assert [message.id for message in got] == [7, 9]

    async def test_search_pages_itself(self):
        async with live() as (client, server):
            found = [
                message.text
                async for message in client.search_messages(
                    "@durov", "old", limit=5, batch=2
                )
            ]
            assert len(found) == 5
            assert found[0] == "found 19"

    async def test_reading_a_chat_marks_it_read(self):
        async with live() as (client, server):
            await client.read_history("@durov", max_id=12)
            call = server.only(functions.messages.ReadHistory)[0]
            assert call.max_id == 12

    async def test_pinning_is_quiet_unless_asked(self):
        async with live() as (client, server):
            await client.pin_message("@durov", 5)
            await client.pin_message("@durov", 6, silent=False)
            calls = server.only(functions.messages.UpdatePinnedMessage)
            assert calls[0].silent and not calls[0].unpin
            assert not calls[1].silent

    async def test_pinning_stays_on_our_side_of_a_private_chat(self):
        async with live() as (client, server):
            await client.pin_message("@durov", 5)
            await client.pin_message("@durov", 6, both_sides=True)
            calls = server.only(functions.messages.UpdatePinnedMessage)
            assert calls[0].pm_oneside
            assert not calls[1].pm_oneside

    async def test_unpinning_says_so(self):
        async with live() as (client, server):
            await client.unpin_message("@durov", 5)
            assert server.only(functions.messages.UpdatePinnedMessage)[0].unpin

    async def test_typing_is_the_default_action(self):
        async with live() as (client, server):
            await client.send_action("@durov")
            call = server.only(functions.messages.SetTyping)[0]
            assert isinstance(call.action, types.SendMessageTypingAction)


class TestChatsAndPeople:
    async def test_dialogs_page_themselves(self):
        async with live() as (client, server):
            got = [
                dialog async for dialog in client.get_dialogs(limit=5, batch=2)
            ]
            assert len(got) == 5
            assert got[0].chat.id == OTHER
            assert got[0].unread == 9

    async def test_a_dialog_carries_its_last_message(self):
        async with live() as (client, server):
            first = await anext(client.get_dialogs(limit=1))
            assert first.top_message is not None
            assert first.top_message.text == "last 9"

    async def test_participants_come_back_as_people(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel())
            found = [
                user
                async for user in client.get_participants(
                    -1000000000000 - CHANNEL, limit=10
                )
            ]
            assert [user.id for user in found] == [OTHER]

    async def test_members_come_back_with_their_standing(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel())
            found = [
                member
                async for member in client.get_members(
                    -1000000000000 - CHANNEL, limit=10
                )
            ]
        assert [member.user_id for member in found] == [OTHER]
        assert found[0].status is MemberStatus.MEMBER
        assert found[0].chat_id == CHANNEL

    async def test_the_creator_is_findable_without_a_raw_call(self):
        """The short version of why get_members exists."""
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel())
            creator = None
            async for member in client.get_members(
                -1000000000000 - CHANNEL, kind="admins"
            ):
                if member.status is MemberStatus.CREATOR:
                    creator = member
        assert creator is not None
        assert creator.user_id == OTHER
        assert creator.title == "founder"

    async def test_a_chat_can_be_asked_about(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel())
            chat = await client.get_chat(-1000000000000 - CHANNEL)
            assert chat.title == "A channel"
            assert chat.is_channel

    async def test_a_person_can_be_asked_about(self):
        async with live() as (client, server):
            user = await client.get_user("@durov")
            assert user.username == "durov"

    async def test_contacts_come_back_as_people(self):
        async with live() as (client, server):
            found = await client.get_contacts()
            assert [user.id for user in found] == [OTHER]

    async def test_blocking_and_unblocking(self):
        async with live() as (client, server):
            assert await client.block_user("@durov")
            assert await client.unblock_user("@durov")
            assert server.only(functions.contacts.Block)
            assert server.only(functions.contacts.Unblock)

    async def test_updating_the_profile_changes_who_we_are(self):
        async with live() as (client, server):
            me = await client.update_profile(first_name="Renamed")
            assert me.first_name == "Renamed"
            assert client.me is not None and client.me.first_name == "Renamed"

    async def test_leaving_a_channel_uses_the_channel_call(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel())
            await client.leave_chat(-1000000000000 - CHANNEL)
            assert server.only(functions.channels.LeaveChannel)

    async def test_joining_by_invite_link_is_the_other_call(self):
        async with live() as (client, server):
            with pytest.raises(SunnygramError):
                # The scripted server does not answer importChatInvite, which
                # is fine: what is being tested is which call went out.
                await client.join_chat("https://t.me/+abcdef")
            assert any(
                isinstance(call, functions.messages.ImportChatInvite)
                and call.hash == "abcdef"
                for call in server.asked
            )

    async def test_topics_come_back_wrapped(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel(megagroup=True))
            found = [
                topic
                async for topic in client.get_topics(-1000000000000 - CHANNEL)
            ]
            assert [topic.id for topic in found] == [10, 20]
            assert found[0].title == "Topic 10"
            assert found[0].chat_id == CHANNEL
            assert found[0].top_message is not None

    async def test_one_topic_can_be_asked_for_by_id(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel(megagroup=True))
            topic = await client.get_topic(-1000000000000 - CHANNEL, 20)
            assert topic.id == 20
            assert server.only(functions.messages.GetForumTopicsByID)[0].topics == [20]

    async def test_creating_a_topic_answers_with_it(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel(megagroup=True))
            topic = await client.create_topic(-1000000000000 - CHANNEL, "Bugs")
            # A topic is the message that opened it, so the id of the message
            # the server made is the id to go and look up.
            assert topic.id == server.only(functions.messages.GetForumTopicsByID)[0].topics[0]

    async def test_closing_a_topic_changes_only_that(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel(megagroup=True))
            await client.close_topic(-1000000000000 - CHANNEL, 10)
            call = server.only(functions.messages.EditForumTopic)[0]
            assert (call.topic_id, call.closed) == (10, True)
            assert call.title is None

    async def test_sending_into_a_topic_is_spelled_as_a_reply(self):
        async with live() as (client, server):
            message = await client.send_message("@durov", "in here", topic=10)
            assert message.text == "in here"
            assert server.sent[-1].reply_to.reply_to_msg_id == 10

    async def test_a_topic_can_send_for_itself(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_channel(megagroup=True))
            topic = await client.get_topic(-1000000000000 - CHANNEL, 10)
            await topic.send("hello")
            assert server.sent[-1].reply_to.reply_to_msg_id == 10


class TestSendingWhatAlreadyExists:
    """send_file uploads, send_media points. Mixing them up must be loud."""

    REFERENCE = types.InputMediaDocument(
        id=types.InputDocument(id=9, access_hash=7, file_reference=b"ref")
    )

    async def test_send_file_refuses_a_reference_instead_of_uploading_it(self):
        # The mistake a caller makes after storing what they sent: the stored
        # thing looks like a file and is not one, and handing it to the
        # uploader fails far away from the call that was actually wrong.
        app = Client(MemoryStorage(SessionState(dc_id=2)), api_id=1, api_hash="0" * 32)
        with pytest.raises(SunnygramError, match="Use send_media"):
            await app.send_file("me", self.REFERENCE)

    async def test_send_media_refuses_a_path(self):
        app = Client(MemoryStorage(SessionState(dc_id=2)), api_id=1, api_hash="0" * 32)
        with pytest.raises(SunnygramError, match="Use send_file"):
            await app.send_media("me", "holiday.jpg")

    async def test_a_written_down_reference_can_be_sent_again(self):
        async with live() as (client, server):
            written = client.file_ref(a_message(5, media=a_document_media()))
            await client.send_media("@durov", written)
            media = server.sent[-1].media
            assert isinstance(media, types.InputMediaDocument)
            assert media.id.id == 90210
            # No upload, which is the whole point of writing one down.
            assert not server.parts

    async def test_a_sent_file_can_answer_itself(self):
        # A send answers with the message and nothing alongside it to build a
        # Chat from, so the chat is the raw peer inside. Everything that only
        # needs the id has to keep working, which is most of what a message
        # does.
        async with live() as (client, server):
            sent = await client.send_file("@durov", b"bytes", name="a.bin")
            assert sent.chat is None
            assert sent.chat_id == OTHER
            await sent.reply("and this is a reply to it")
            assert server.sent[-1].reply_to.reply_to_msg_id == sent.id

    async def test_a_message_writes_its_own_file_down(self):
        async with live() as (client, server):
            message = wrap(a_message(5, media=a_document_media()), client=client)
            assert client.file_ref(message) == message.file_ref


class TestAlbumOptions:
    """An album takes the same per-file options a single send does, and a video
    needs them: without a poster frame, a duration and a size, what arrives is a
    file rather than something that plays in place."""

    async def test_a_poster_frame_goes_up_as_a_file_of_its_own(self, tmp_path):
        # The thumbnail is the one option that is not a number: it names a file,
        # and handing the name itself to the wire put a Path where an uploaded
        # file belongs. It failed in the serializer, several layers from the
        # call that was wrong, and it failed for every album carrying a video.
        poster = tmp_path / "poster.jpg"
        poster.write_bytes(b"not really a jpeg")
        async with live() as (client, server):
            await client.send_album(
                "@durov",
                [b"first video", b"second video"],
                options=[
                    {
                        "kind": "video",
                        "name": "one.mp4",
                        "thumb": poster,
                        "duration": 3,
                        "width": 640,
                        "height": 480,
                    },
                    {"kind": "video", "name": "two.mp4", "thumb": poster},
                ],
            )
        registered = server.only(functions.messages.UploadMedia)
        assert len(registered) == 2
        assert all(
            isinstance(one.media.thumb, types.InputFile) for one in registered
        )

    async def test_an_album_with_no_poster_asks_for_no_upload_of_one(self, tmp_path):
        async with live() as (client, server):
            await client.send_album(
                "@durov",
                [b"a video"],
                options=[{"kind": "video", "name": "one.mp4"}],
            )
        registered = server.only(functions.messages.UploadMedia)
        assert registered[0].media.thumb is None

    async def test_a_photo_is_not_charged_for_a_thumbnail_it_cannot_carry(
        self, tmp_path
    ):
        # A photo has no thumbnail field, so uploading one for it is a round
        # trip whose answer is thrown away.
        poster = tmp_path / "poster.jpg"
        poster.write_bytes(b"not really a jpeg")
        async with live() as (client, server):
            await client.send_album(
                "@durov",
                [b"a photo"],
                options=[{"kind": "photo", "name": "one.jpg", "thumb": poster}],
            )
        # One file went up, not two.
        assert len({part.file_id for part in server.parts}) == 1


class TestKeyboards:
    async def test_a_keyboard_goes_out_with_the_message(self):
        async with live() as (client, server):
            await client.send_message(
                "@durov",
                "pick one",
                reply_markup=keyboard([Button.callback("Yes"), Button.callback("No")]),
            )
            markup = server.sent[-1].reply_markup
            assert isinstance(markup, types.ReplyInlineMarkup)
            assert [one.text for one in markup.rows[0].buttons] == ["Yes", "No"]

    async def test_a_keyboard_goes_out_with_a_file(self, tmp_path):
        picture = tmp_path / "cat.jpg"
        picture.write_bytes(b"pretend jpeg")

        async with live() as (client, server):
            await client.send_photo(
                "@durov", picture, reply_markup=keyboard([Button.callback("Save")])
            )
            assert isinstance(server.sent[-1].reply_markup, types.ReplyInlineMarkup)

    async def test_editing_the_buttons_leaves_the_text_alone(self):
        async with live() as (client, server):
            await client.edit_markup(
                "@durov", 5, keyboard([Button.callback("Later", "later")])
            )
            call = server.edited[-1]
            assert call.message is None
            assert call.reply_markup.rows[0].buttons[0].data == b"later"

    async def test_taking_the_buttons_away(self):
        async with live() as (client, server):
            await client.edit_markup("@durov", 5)
            # No keyboard is the field left unset. An inline keyboard with no
            # rows in it looks like the same thing and is refused on the wire,
            # so a menu's close button failed with REPLY_MARKUP_INVALID.
            assert server.edited[-1].reply_markup is None

    async def test_a_message_reads_its_own_buttons_back(self):
        async with live() as (client, server):
            raw = a_message(5, "pick")
            raw.reply_markup = keyboard([Button.callback("Yes"), Button.callback("No")])
            message = wrap(raw, client=client)
            assert [one.text for one in message.buttons[0]] == ["Yes", "No"]


class TestButtonPresses:
    async def test_a_press_reaches_a_handler_and_can_be_answered(self):
        # The other end to end path: a press off the wire becomes a
        # CallbackQuery, a filter on its payload says yes, and answering it is
        # a real call on the other side.
        answered = asyncio.Event()

        async with live() as (client, server):

            @client.on_callback_query(filters.data("yes"))
            async def confirm(app: Client, press: Any) -> None:
                await press.answer("done", alert=True)
                answered.set()

            client.invoker.peers.learn(a_user())
            await server.push_press(b"yes")
            await asyncio.wait_for(answered.wait(), 5)

            call = server.only(functions.messages.SetBotCallbackAnswer)[0]
            assert call.message == "done"
            assert call.alert

    async def test_a_press_can_edit_the_message_it_is_under(self):
        edited = asyncio.Event()

        async with live() as (client, server):

            @client.on_callback_query()
            async def press(app: Client, query: Any) -> None:
                await query.edit("chosen")
                edited.set()

            client.invoker.peers.learn(a_user())
            await server.push_press(b"anything", message_id=88)
            await asyncio.wait_for(edited.wait(), 5)

            assert (server.edited[-1].id, server.edited[-1].message) == (88, "chosen")

    async def test_a_press_on_an_inline_message_is_edited_the_other_way(self):
        # A message an inline query produced belongs to no chat, so editing it
        # is a different call, aimed at the datacenter that issued its id.
        edited = asyncio.Event()

        async with live() as (client, server):

            @client.on_callback_query()
            async def press(app: Client, query: Any) -> None:
                assert query.is_inline
                await query.edit("chosen")
                await query.edit_markup()
                edited.set()

            client.invoker.peers.learn(a_user())
            await server.push(
                types.Updates(
                    updates=[
                        types.UpdateInlineBotCallbackQuery(
                            query_id=7,
                            user_id=OTHER,
                            msg_id=types.InputBotInlineMessageID(
                                dc_id=2, id=555, access_hash=999
                            ),
                            chat_instance=1,
                            data=b"x",
                        )
                    ],
                    users=[a_user()],
                    chats=[],
                    date=1700000000,
                    seq=0,
                ).to_bytes()
            )
            await asyncio.wait_for(edited.wait(), 5)

            calls = server.only(functions.messages.EditInlineBotMessage)
            assert calls[0].message == "chosen"
            assert calls[0].id.id == 555
            # Taking the buttons away leaves the field unset, here as anywhere.
            assert calls[1].reply_markup is None
            # Nothing was fetched: an inline message has no chat to fetch from.
            assert not [
                call
                for call in server.asked
                if isinstance(call, functions.messages.GetMessages)
            ]

    async def test_an_inline_press_cannot_fetch_its_message(self):
        press = CallbackQuery(
            id=1,
            inline_id=types.InputBotInlineMessageID(dc_id=2, id=5, access_hash=6),
            client=object(),
        )
        with pytest.raises(SunnygramError, match="no chat to"):
            await press.get_message()

    async def test_a_press_says_who_pressed_it_and_where(self):
        seen: list[Any] = []
        arrived = asyncio.Event()

        async with live() as (client, server):

            @client.on_callback_query()
            async def press(app: Client, query: Any) -> None:
                seen.append(query)
                arrived.set()

            client.invoker.peers.learn(a_user())
            await server.push_press(b"page:2")
            await asyncio.wait_for(arrived.wait(), 5)

            assert seen[0].sender is not None and seen[0].sender.username == "durov"
            assert seen[0].chat is not None and seen[0].chat.is_private
            assert seen[0].text == "page:2"


class TestAMessageWeJustSent:
    """What comes back from a send has to be usable, not just returned.

    Telegram answers a send in a private chat with updateShortSentMessage: the
    id and the date, and nothing else. Everything here failed against a real
    datacenter and passed against this server, because this server used to
    answer every send with a full Updates carrying the message and the user.
    That is what a group looks like, not a private chat, so the whole class of
    bug was invisible: a bot that sends a status line and edits it as it works
    got an error on the edit and never on the send.
    """

    async def test_it_knows_which_chat_it_is_in(self):
        async with live() as (client, server):
            server.sends_are_short = True
            sent = await client.send_message("@durov", "working on it")
            assert sent.id == server.next_id
            # The one thing the shorthand leaves out and the one thing every
            # follow-up call needs.
            assert sent._peer() is not None

    async def test_it_can_be_edited(self):
        async with live() as (client, server):
            server.sends_are_short = True
            sent = await client.send_message("@durov", "working on it")
            await sent.edit("done")
            edited = server.only(functions.messages.EditMessage)
            assert len(edited) == 1
            assert edited[0].message == "done"
            assert edited[0].id == sent.id

    async def test_it_can_be_deleted(self):
        async with live() as (client, server):
            server.sends_are_short = True
            sent = await client.send_message("@durov", "working on it")
            await sent.delete()

    async def test_it_can_be_replied_to(self):
        async with live() as (client, server):
            server.sends_are_short = True
            sent = await client.send_message("@durov", "a question")
            await sent.reply("and an answer")
            assert server.sent[-1].message == "and an answer"

    async def test_the_text_we_wrote_comes_back_on_it(self):
        # The server did not echo it, so the only copy is the one we sent.
        async with live() as (client, server):
            server.sends_are_short = True
            sent = await client.send_message("@durov", "written here")
            assert sent.text == "written here"
            assert sent.outgoing


class TestStaleFileReferences:
    async def test_a_send_renews_the_reference_and_tries_again(self):
        async with live() as (client, server):
            server.messages_carry_media = True
            written = client.file_ref(a_message(5, media=a_document_media(b"old")))
            server.stale_sends = 1

            sent = await client.send_media("@durov", written)

            assert isinstance(sent, Message)
            # Twice: the first refused, the second with a reference fetched
            # from the message the file came from.
            attempts = [
                call
                for call in server.asked
                if isinstance(call, functions.messages.SendMedia)
            ]
            assert len(attempts) == 2
            assert attempts[0].media.id.file_reference == b"old"
            assert attempts[1].media.id.file_reference == b"fresh"

    async def test_a_reference_with_no_origin_cannot_be_renewed(self):
        async with live() as (client, server):
            written = client.file_ref(
                a_message(5, media=a_document_media()), origin=False
            )
            server.stale_sends = 1
            with pytest.raises(RPCError, match="FILE_REFERENCE_EXPIRED"):
                await client.send_media("@durov", written)

    async def test_the_renewal_is_tried_once_and_not_in_a_loop(self):
        async with live() as (client, server):
            server.messages_carry_media = True
            written = client.file_ref(a_message(5, media=a_document_media()))
            # Stale however many times it is asked, which is the server being
            # broken rather than the reference being old. Renewing in a loop
            # against that would never end.
            server.stale_sends = 10
            with pytest.raises(RPCError, match="FILE_REFERENCE_EXPIRED"):
                await client.send_media("@durov", written)

    async def test_a_hidden_send_is_renewed_like_any_other(self):
        # The two used to be exclusive. Hiding a file meant building the media
        # by hand, and a media built by hand says nothing about which message
        # it came from, so asking for a spoiler quietly cost the reference the
        # thing that renews it. Both now come off the same send.
        async with live() as (client, server):
            server.messages_carry_media = True
            written = client.file_ref(a_message(5, media=a_document_media(b"old")))
            server.stale_sends = 1

            await client.send_media("@durov", written, spoiler=True)

            attempts = [
                call
                for call in server.asked
                if isinstance(call, functions.messages.SendMedia)
            ]
            assert len(attempts) == 2
            assert attempts[1].media.id.file_reference == b"fresh"
            # And the renewed one is still hidden. Rebuilding the media around
            # a fresh reference is where that would go missing.
            assert all(call.media.spoiler is True for call in attempts)


class TestRepliesWithoutARoundTrip:
    async def test_a_reply_to_something_just_seen_is_already_here(self):
        arrived = asyncio.Event()
        seen: list[Message] = []

        async with live() as (client, server):

            @client.on_message(filters.reply)
            async def answering(app: Client, message: Message) -> None:
                seen.append(message)
                arrived.set()

            client.invoker.peers.learn(a_user())
            await server.push_message("the question", 41)
            await server.push_message(
                "the answer",
                42,
                reply_to=types.MessageReplyHeader(reply_to_msg_id=41),
            )
            await asyncio.wait_for(arrived.wait(), 5)

            assert seen[0].reply_to_message is not None
            assert seen[0].reply_to_message.text == "the question"
            # And it cost nothing, which is the point.
            assert not [
                call
                for call in server.asked
                if isinstance(call, functions.messages.GetMessages)
            ]

    async def test_get_reply_hands_back_what_is_already_known(self):
        arrived = asyncio.Event()
        found: list[Any] = []

        async with live() as (client, server):

            @client.on_message(filters.reply)
            async def answering(app: Client, message: Message) -> None:
                found.append(await message.get_reply())
                arrived.set()

            client.invoker.peers.learn(a_user())
            await server.push_message("the question", 41)
            await server.push_message(
                "the answer",
                42,
                reply_to=types.MessageReplyHeader(reply_to_msg_id=41),
            )
            await asyncio.wait_for(arrived.wait(), 5)

            assert found[0] is not None and found[0].text == "the question"
            assert not [
                call
                for call in server.asked
                if isinstance(call, functions.messages.GetMessages)
            ]

    async def test_an_old_message_still_costs_a_call(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            reply = wrap(a_message(42, "the answer"), client=client)
            reply.reply_to_id = 3
            found = await reply.get_reply()
            assert found is not None and found.id == 3
            assert server.only(functions.messages.GetMessages)

    async def test_a_page_of_history_ties_its_own_replies_together(self):
        async with live() as (client, server):
            got = await client.get_messages("@durov", [7, 9])
            # Nothing on this page replies to anything, so the check is that
            # asking for the page did not go looking for more.
            assert [message.reply_to_message for message in got] == [None, None]


class TestConversations:
    """Asking somebody something, all the way through a real update stream.

    test_dispatcher.py covers the table this is built on. What is left, and
    what only shows up here, is the wiring: that the chat a caller named
    resolves to the id updates actually arrive with, that a wait started before
    a send cannot be beaten by the answer, and that a question nobody answers
    ends rather than hanging.
    """

    async def test_ask_sends_the_question_and_returns_the_answer(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())

            asking = asyncio.create_task(client.ask(OTHER, "what is your name?"))
            await _until(lambda: bool(server.sent))
            await server.push_message("Alex")

            answer = await asyncio.wait_for(asking, 5)
            assert answer.text == "Alex"
            assert server.sent[0].message == "what is your name?"

    async def test_the_answer_does_not_also_reach_the_handlers(self):
        async with live() as (client, server):
            seen: list[Message] = []
            client.add_handler(lambda app, m: _record(seen, m))
            client.invoker.peers.learn(a_user())

            asking = asyncio.create_task(client.ask(OTHER, "name?"))
            await _until(lambda: bool(server.sent))
            await server.push_message("Alex")
            await asyncio.wait_for(asking, 5)

            # Our own question comes back as an update like anything else and
            # still reaches the handlers, which is unchanged. What must not
            # reach them is the reply, since a program that asked somebody's
            # name does not want its command router reading the answer.
            await asyncio.sleep(0.05)
            assert [m.text for m in seen if not m.outgoing] == []

    async def test_a_conversation_reads_as_one(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())

            async def talking() -> str:
                async with await client.conversation(OTHER) as talk:
                    await talk.send("what should I call you?")
                    said = await talk.wait()
                    await talk.send(f"hello {said.text}")
                    return str(said.text)

            running = asyncio.create_task(talking())
            await _until(lambda: bool(server.sent))
            await server.push_message("Alex")

            assert await asyncio.wait_for(running, 5) == "Alex"
            assert [call.message for call in server.sent] == [
                "what should I call you?",
                "hello Alex",
            ]

    async def test_a_question_nobody_answers_ends_and_says_so(self, caplog):
        # Rule C3. The raise reaches the caller, but a bot that has stopped
        # being answered is worth a line in the log as well, since the caller
        # is quite likely catching this to move on.
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            with caplog.at_level("WARNING", logger="sunnygram.conversation"):
                with pytest.raises(NoAnswer, match="answered within"):
                    await client.ask(OTHER, "still there?", timeout=0.05)
            assert "nothing came back" in caplog.text

    async def test_a_wait_that_ends_gives_its_place_back(self):
        # The bound is on questions outstanding, so one that ended has to stop
        # counting whichever way it ended, or a long-running program refuses to
        # ask anything after the first few hundred.
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            for _ in range(3):
                with pytest.raises(NoAnswer):
                    await client.wait_for(OTHER, timeout=0.02)
            assert client.dispatcher.listening == 0

    async def test_waiting_for_something_nobody_asked_about(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            waiting = asyncio.create_task(client.wait_for(OTHER))
            await _until(lambda: client.dispatcher.listening == 1)
            await server.push_message("unprompted")
            assert (await asyncio.wait_for(waiting, 5)).text == "unprompted"

    async def test_a_filter_decides_what_counts_as_the_answer(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            waiting = asyncio.create_task(
                client.wait_for(OTHER, filters=filters.command("done"))
            )
            await _until(lambda: client.dispatcher.listening == 1)

            await server.push_message("not yet", 43)
            await asyncio.sleep(0.05)
            assert not waiting.done()

            await server.push_message("/done", 44)
            assert (await asyncio.wait_for(waiting, 5)).text == "/done"

    async def test_leaving_the_block_stops_it_being_used(self):
        async with live() as (client, server):
            client.invoker.peers.learn(a_user())
            async with await client.conversation(OTHER) as talk:
                pass
            with pytest.raises(RuntimeError, match="already been left"):
                await talk.wait(timeout=0.01)
