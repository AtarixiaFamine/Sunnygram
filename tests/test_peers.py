"""Knowing who is who.

Three things are worth proving here. That what the cache learns survives being
evicted and being restarted, because a forgotten access hash means a peer that
can no longer be reached. That a min constructor is never learned, because a
hash that only works in one context is worse than no hash at all. And that the
resolver turns what a person writes into what the protocol wants, going to the
network exactly once for a name it has never seen.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import PeerNotFound, SunnygramError
from sunnygram.methods import send_message
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.peers import (
    PeerCache,
    as_channel,
    as_user,
    mark_id,
    normalize_phone,
    normalize_username,
    record_for,
    resolve,
    resolve_username,
    unmark_id,
)
from sunnygram.raw import functions, types
from sunnygram.storage import (
    MemoryStorage,
    PeerKind,
    PeerRecord,
    SessionState,
    SQLiteStorage,
)

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000


def a_user(
    id: int = 1001,
    *,
    username: str | None = "durov",
    access_hash: int | None = 12345,
    min: bool = False,
    bot: bool = False,
    phone: str | None = None,
    usernames: list[Any] | None = None,
) -> types.User:
    return types.User(
        id=id,
        access_hash=access_hash,
        first_name="Pavel",
        username=username,
        usernames=usernames,
        phone=phone,
        min=min,
        bot=bot,
    )


def a_channel(
    id: int = 2002,
    *,
    username: str | None = "telegram",
    access_hash: int | None = 54321,
    min: bool = False,
    megagroup: bool = False,
) -> types.Channel:
    return types.Channel(
        id=id,
        access_hash=access_hash,
        title="Telegram",
        username=username,
        photo=types.ChatPhotoEmpty(),
        date=1700000000,
        min=min,
        megagroup=megagroup,
    )


def a_group(id: int = 3003) -> types.Chat:
    return types.Chat(
        id=id,
        title="A group",
        photo=types.ChatPhotoEmpty(),
        participants_count=3,
        date=1700000000,
        version=1,
    )


class TestWhatIsWorthLearning:
    def test_a_user_becomes_a_record(self):
        record = record_for(a_user(phone="+39 333 1234567"))
        assert record == PeerRecord(
            id=1001,
            kind=PeerKind.USER,
            access_hash=12345,
            usernames=("durov",),
            phone="393331234567",
        )

    def test_a_bot_is_told_apart_from_a_person(self):
        assert record_for(a_user(bot=True)).kind is PeerKind.BOT
        assert record_for(a_user()).kind is PeerKind.USER

    def test_a_supergroup_is_told_apart_from_a_channel(self):
        assert record_for(a_channel(megagroup=True)).kind is PeerKind.SUPERGROUP
        assert record_for(a_channel()).kind is PeerKind.CHANNEL

    def test_a_basic_group_needs_no_hash(self):
        record = record_for(a_group())
        assert record.kind is PeerKind.CHAT
        assert record.access_hash == 0

    def test_a_min_peer_is_refused(self):
        # The hash on a min constructor belongs to the context it arrived in.
        # Keeping it would produce one that works in one chat and nowhere else.
        assert record_for(a_user(min=True)) is None
        assert record_for(a_channel(min=True)) is None

    def test_a_user_with_no_hash_is_refused(self):
        assert record_for(a_user(access_hash=None)) is None

    def test_only_active_usernames_are_kept(self):
        peer = a_user(
            username=None,
            usernames=[
                types.Username(username="taken", active=True),
                types.Username(username="parked", active=False),
            ],
        )
        assert record_for(peer).usernames == ("taken",)

    def test_nothing_is_learned_from_an_empty_one(self):
        assert record_for(types.UserEmpty(id=5)) is None
        assert record_for(types.ChatEmpty(id=5)) is None


class TestNormalising:
    @pytest.mark.parametrize(
        "written",
        [
            "durov",
            "@durov",
            "Durov",
            "t.me/durov",
            "https://t.me/durov",
            "https://telegram.me/durov",
            "https://t.me/durov?start=1",
            # What a desktop browser puts on the clipboard.
            "https://www.t.me/durov",
            "www.t.me/durov",
        ],
    )
    def test_every_way_of_writing_a_username_is_one_name(self, written):
        assert normalize_username(written) == "durov"

    def test_a_phone_number_is_its_digits(self):
        assert normalize_phone("+39 333 123-4567") == "393331234567"
        assert normalize_phone("nonsense") is None
        assert normalize_phone(None) is None


class TestMarkedIds:
    @pytest.mark.parametrize(
        ("peer_id", "kind"),
        [
            (1001, PeerKind.USER),
            (1001, PeerKind.BOT),
            (3003, PeerKind.CHAT),
            (2002, PeerKind.CHANNEL),
            (2002, PeerKind.SUPERGROUP),
        ],
    )
    def test_a_marked_id_reads_back_as_itself(self, peer_id, kind):
        back, coarse = unmark_id(mark_id(peer_id, kind))
        assert back == peer_id
        assert coarse.is_user == kind.is_user
        assert coarse.is_channel == kind.is_channel

    def test_the_bot_api_spelling_is_the_one_people_paste(self):
        assert mark_id(2002, PeerKind.CHANNEL) == -1000000002002
        assert mark_id(3003, PeerKind.CHAT) == -3003
        assert unmark_id(-1000000002002) == (2002, PeerKind.CHANNEL)


class TestTheOtherSpellings:
    """Telegram splits its API by what it is talking to, so a peer has to be
    re-spelled as an input channel or an input user before half of it."""

    def test_a_channel_keeps_its_id_and_hash(self):
        peer = types.InputPeerChannel(channel_id=2002, access_hash=99)
        channel = as_channel(peer)
        assert isinstance(channel, types.InputChannel)
        assert (channel.channel_id, channel.access_hash) == (2002, 99)

    def test_a_person_keeps_theirs(self):
        peer = types.InputPeerUser(user_id=1001, access_hash=77)
        user = as_user(peer)
        assert isinstance(user, types.InputUser)
        assert (user.user_id, user.access_hash) == (1001, 77)

    def test_ourselves_stay_ourselves(self):
        assert isinstance(as_user(types.InputPeerSelf()), types.InputUserSelf)

    def test_a_hash_borrowed_from_a_message_stays_borrowed(self):
        # These carry where the hash came from rather than the hash itself, so
        # the conversion has to keep the reference rather than flatten it.
        peer = types.InputPeerChannelFromMessage(
            peer=types.InputPeerSelf(), msg_id=5, channel_id=2002
        )
        converted = as_channel(peer)
        assert isinstance(converted, types.InputChannelFromMessage)
        assert converted.msg_id == 5

    def test_asking_a_person_to_be_a_channel_is_refused(self):
        with pytest.raises(SunnygramError):
            as_channel(types.InputPeerUser(user_id=1, access_hash=1))

    def test_asking_a_channel_to_be_a_person_is_refused(self):
        with pytest.raises(SunnygramError):
            as_user(types.InputPeerChannel(channel_id=1, access_hash=1))


class TestTheCache:
    async def test_what_goes_in_comes_out(self):
        cache = PeerCache(MemoryStorage())
        assert cache.learn(a_user(), a_channel(), a_group()) == 3
        found = await cache.get(1001)
        assert found.access_hash == 12345
        assert (await cache.by_username("@Durov")).id == 1001

    async def test_a_known_peer_costs_nothing(self):
        cache = PeerCache(MemoryStorage())
        cache.learn(a_user())
        await cache.get(1001)
        await cache.by_username("durov")
        assert cache.hits == 2
        assert cache.misses == 0

    async def test_learning_the_same_peer_twice_is_not_news(self):
        cache = PeerCache(MemoryStorage())
        assert cache.learn(a_user()) == 1
        assert cache.learn(a_user()) == 0
        assert cache.pending == 1

    async def test_a_renamed_peer_gives_up_its_old_name(self):
        cache = PeerCache(MemoryStorage())
        cache.learn(a_user(username="durov"))
        cache.learn(a_user(username="pavel"))
        assert (await cache.by_username("pavel")).id == 1001
        assert await cache.by_username("durov") is None

    async def test_what_was_flushed_survives_eviction(self):
        store = MemoryStorage()
        cache = PeerCache(store, capacity=2)
        cache.learn(a_user(1), a_user(2), a_user(3))
        await cache.flush()
        assert cache.size == 2
        # The oldest is gone from memory, and the storage still has it.
        assert (await cache.get(1)).id == 1
        assert cache.misses == 1

    async def test_nothing_learned_is_lost_before_it_is_written(self):
        store = MemoryStorage()
        cache = PeerCache(store, capacity=1)
        cache.learn(a_user(1), a_user(2), a_user(3))
        assert cache.size == 1
        assert await cache.flush() == 3
        assert await store.peer_count() == 3

    async def test_a_flush_that_fails_keeps_what_it_could_not_write(self):
        class Broken(MemoryStorage):
            async def put_peers(self, peers):
                raise OSError("the disk is on fire")

        cache = PeerCache(Broken())
        cache.learn(a_user())
        with pytest.raises(OSError):
            await cache.flush()
        assert cache.pending == 1

    async def test_a_batch_is_not_written_until_it_is_full(self):
        store = MemoryStorage()
        cache = PeerCache(store, flush_every=3)
        cache.learn(a_user(1), a_user(2))
        assert await cache.flush(force=False) == 0
        cache.learn(a_user(3))
        assert await cache.flush(force=False) == 3
        assert await store.peer_count() == 3

    async def test_an_input_peer_comes_out_the_right_shape(self):
        cache = PeerCache(MemoryStorage())
        cache.learn(a_user(), a_channel(), a_group())
        assert await cache.input_peer(1001) == types.InputPeerUser(
            user_id=1001, access_hash=12345
        )
        assert await cache.input_peer(2002) == types.InputPeerChannel(
            channel_id=2002, access_hash=54321
        )
        assert await cache.input_peer(3003) == types.InputPeerChat(chat_id=3003)

    async def test_a_stranger_says_so(self):
        cache = PeerCache(MemoryStorage())
        with pytest.raises(PeerNotFound, match="9999"):
            await cache.input_peer(9999)


class TestKeepingPeers:
    @pytest.fixture(params=["memory", "sqlite"])
    async def store(self, request, tmp_path):
        if request.param == "memory":
            yield MemoryStorage()
            return
        storage = SQLiteStorage(tmp_path / "session.db")
        await storage.open()
        yield storage
        await storage.close()

    async def test_a_peer_read_back_is_the_peer_written(self, store):
        record = PeerRecord(
            id=1001,
            kind=PeerKind.BOT,
            access_hash=-9000,
            usernames=("one", "two"),
            phone="393331234567",
        )
        await store.put_peers([record])
        assert await store.peer_by_id(1001) == record
        assert await store.peer_by_username("two") == record
        assert await store.peer_by_phone("393331234567") == record

    async def test_a_name_given_up_stops_pointing_at_its_owner(self, store):
        await store.put_peers([PeerRecord(1001, PeerKind.USER, 1, ("durov",))])
        await store.put_peers([PeerRecord(1001, PeerKind.USER, 1, ("pavel",))])
        assert await store.peer_by_username("durov") is None
        assert (await store.peer_by_username("pavel")).id == 1001

    async def test_a_name_can_change_hands(self, store):
        await store.put_peers([PeerRecord(1, PeerKind.USER, 1, ("taken",))])
        await store.put_peers([PeerRecord(2, PeerKind.USER, 2, ("taken",))])
        assert (await store.peer_by_username("taken")).id == 2

    async def test_forgetting_is_thorough(self, store):
        await store.put_peers([PeerRecord(1001, PeerKind.USER, 1, ("durov",))])
        await store.clear_peers()
        assert await store.peer_count() == 0
        assert await store.peer_by_username("durov") is None


class TestAcrossRestarts:
    async def test_a_file_remembers_who_it_met(self, tmp_path):
        path = tmp_path / "session.db"
        first = SQLiteStorage(path)
        cache = PeerCache(first)
        cache.learn(a_user(), a_channel())
        await cache.flush()
        await first.close()

        second = SQLiteStorage(path)
        again = PeerCache(second)
        found = await again.by_username("durov")
        assert found is not None
        assert found.access_hash == 12345
        await second.close()


class TestForgettingOne:
    """Dropping a peer whose access hash has stopped being accepted.

    The whole value of this is that it outlives the process. A forget that only
    reached memory would fix a program until it restarted and then hand it the
    same broken hash back out of the session file, which is the shape of bug
    that gets reported as "it works until I restart it".
    """

    async def test_it_goes_from_memory_and_from_the_file(self, tmp_path):
        path = tmp_path / "session.db"
        store = SQLiteStorage(path)
        cache = PeerCache(store)
        cache.learn(a_user(), a_channel())
        await cache.flush()

        assert await cache.forget(a_user().id) is True
        assert await cache.get(a_user().id) is None
        assert await store.peer_by_id(a_user().id) is None
        # The lookups go with it, or the name would still answer with the id
        # of a peer that is no longer there.
        assert await cache.by_username("durov") is None
        # And the one next to it is untouched.
        assert await cache.get(a_channel().id) is not None
        await store.close()

        again = SQLiteStorage(path)
        after = PeerCache(again)
        assert await after.get(a_user().id) is None
        assert await after.get(a_channel().id) is not None
        await again.close()

    async def test_forgetting_one_that_was_never_there_says_no(self, tmp_path):
        cache = PeerCache(MemoryStorage())
        assert await cache.forget(12345) is False

    async def test_a_peer_still_waiting_to_be_written_goes_too(self, tmp_path):
        # The pending batch is the trap: forgetting a peer that has been
        # learned but not flushed would look right, and then the next flush
        # would write the record it had just been told to drop.
        store = SQLiteStorage(tmp_path / "session.db")
        cache = PeerCache(store)
        cache.learn(a_user())
        assert cache.pending == 1

        assert await cache.forget(a_user().id) is True
        await cache.flush()
        assert await store.peer_by_id(a_user().id) is None
        await store.close()


class ResolveServer(ScriptedServer):
    """A datacenter that knows one username and one number."""

    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.asked: list[Any] = []

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            self.asked.append(query)
            if isinstance(query, functions.contacts.ResolveUsername):
                if query.username != "durov":
                    await self.refuse(request.msg_id, 400, "USERNAME_NOT_OCCUPIED")
                    continue
                await self.answer(
                    request.msg_id,
                    types.contacts.ResolvedPeer(
                        peer=types.PeerUser(user_id=1001),
                        chats=[],
                        users=[a_user()],
                    ),
                )
            elif isinstance(query, functions.contacts.ResolvePhone):
                await self.answer(
                    request.msg_id,
                    types.contacts.ResolvedPeer(
                        peer=types.PeerUser(user_id=1001),
                        chats=[],
                        users=[a_user(phone="+393331234567")],
                    ),
                )
            elif isinstance(query, functions.messages.SendMessage):
                await self.answer(
                    request.msg_id,
                    types.Updates(
                        updates=[
                            types.UpdateMessageID(id=7, random_id=query.random_id),
                            types.UpdateNewMessage(
                                message=types.Message(
                                    id=7,
                                    peer_id=types.PeerUser(user_id=1001),
                                    date=1700000000,
                                    message=query.message,
                                    out=True,
                                ),
                                pts=1,
                                pts_count=1,
                            ),
                        ],
                        users=[a_user()],
                        chats=[],
                        date=1700000000,
                        seq=0,
                    ),
                )
            else:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


@asynccontextmanager
async def live(
    storage: Any = None,
) -> AsyncIterator[tuple[Invoker, ResolveServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    invoker = Invoker(
        MemoryStorage(session) if storage is None else storage,
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = ResolveServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()


class TestResolving:
    async def test_me_is_free(self):
        async with live() as (invoker, server):
            assert await resolve(invoker, "me") == types.InputPeerSelf()
            assert await resolve(invoker, "self") == types.InputPeerSelf()
            assert server.asked == []

    async def test_an_input_peer_is_already_an_answer(self):
        async with live() as (invoker, server):
            given = types.InputPeerUser(user_id=5, access_hash=6)
            assert await resolve(invoker, given) is given
            assert server.asked == []

    async def test_a_username_is_asked_about_once(self):
        async with live() as (invoker, server):
            first = await resolve(invoker, "@durov")
            second = await resolve(invoker, "https://t.me/durov")
            assert first == types.InputPeerUser(user_id=1001, access_hash=12345)
            assert second == first
            # The second spelling of the same name never left the machine.
            assert len(server.asked) == 1

    async def test_a_name_nobody_holds_says_so(self):
        async with live() as (invoker, server):
            with pytest.raises(PeerNotFound, match="nobody on Telegram"):
                await resolve(invoker, "@nosuchperson")

    async def test_a_typo_never_reaches_the_server(self):
        async with live() as (invoker, server):
            with pytest.raises(PeerNotFound, match="shaped like a username"):
                await resolve(invoker, "not a username!")
            assert server.asked == []

    async def test_an_invite_link_is_refused_for_what_it_is(self):
        async with live() as (invoker, server):
            with pytest.raises(PeerNotFound, match="invite link"):
                await resolve(invoker, "https://t.me/+AbCdEf")
            assert server.asked == []

    async def test_a_phone_number_resolves_and_is_remembered(self):
        async with live() as (invoker, server):
            first = await resolve(invoker, "+39 333 1234567")
            assert first == types.InputPeerUser(user_id=1001, access_hash=12345)
            await resolve(invoker, "+393331234567")
            assert len(server.asked) == 1

    async def test_an_id_works_once_the_peer_is_known(self):
        async with live() as (invoker, server):
            await resolve(invoker, "@durov")
            assert await resolve(invoker, 1001) == types.InputPeerUser(
                user_id=1001, access_hash=12345
            )

    async def test_a_bot_api_id_works_too(self):
        async with live() as (invoker, server):
            invoker.peers.learn(a_channel())
            assert await resolve(invoker, -1000000002002) == types.InputPeerChannel(
                channel_id=2002, access_hash=54321
            )

    async def test_a_basic_group_needs_no_introduction(self):
        async with live() as (invoker, server):
            assert await resolve(invoker, -3003) == types.InputPeerChat(chat_id=3003)

    async def test_an_unknown_id_says_what_to_do_about_it(self):
        async with live() as (invoker, server):
            with pytest.raises(PeerNotFound, match="Resolve them by username"):
                await resolve(invoker, 9999)

    async def test_a_peer_out_of_an_answer_names_itself(self):
        async with live() as (invoker, server):
            # A Peer carries an id and no hash, so it is only as good as what
            # the session already knows about that id.
            with pytest.raises(PeerNotFound):
                await resolve(invoker, types.PeerUser(user_id=1001))
            invoker.peers.learn(a_user())
            assert await resolve(invoker, types.PeerUser(user_id=1001)) == (
                types.InputPeerUser(user_id=1001, access_hash=12345)
            )

    async def test_a_user_object_is_learned_on_the_way_past(self):
        async with live() as (invoker, server):
            assert await resolve(invoker, a_user()) == types.InputPeerUser(
                user_id=1001, access_hash=12345
            )
            assert (await invoker.peers.get(1001)).access_hash == 12345

    async def test_a_bool_is_not_a_peer(self):
        async with live() as (invoker, server):
            with pytest.raises(TypeError):
                await resolve(invoker, True)

    async def test_resolving_by_hand_always_asks(self):
        async with live() as (invoker, server):
            await resolve(invoker, "@durov")
            await resolve_username(invoker, "@durov")
            assert len(server.asked) == 2


class TestTheCacheFillsItself:
    async def test_an_answer_teaches_the_session_who_was_in_it(self):
        async with live() as (invoker, server):
            await send_message(invoker, "@durov", "hello")
            # The username cost one call; the peer that came back with the
            # answer is now known by id as well.
            assert (await invoker.peers.get(1001)).usernames == ("durov",)

    async def test_a_username_can_be_sent_to_directly(self):
        async with live() as (invoker, server):
            sent = await send_message(invoker, "@durov", "hello")
            assert sent.message == "hello"
            asked = [
                call
                for call in server.asked
                if isinstance(call, functions.messages.SendMessage)
            ]
            assert asked[0].peer == types.InputPeerUser(
                user_id=1001, access_hash=12345
            )

    async def test_what_a_session_learns_reaches_the_file(self, tmp_path):
        storage = SQLiteStorage(tmp_path / "session.db")
        session = SessionState(dc_id=2, user_id=ME)
        session.set_auth_key(2, AUTH_KEY)
        await storage.open()
        await storage.save(session)
        async with live(storage) as (invoker, server):
            await resolve(invoker, "@durov")
        # The invoker was closed, which flushes what it learned.
        again = SQLiteStorage(tmp_path / "session.db")
        assert (await again.peer_by_username("durov")).id == 1001
        await again.close()
