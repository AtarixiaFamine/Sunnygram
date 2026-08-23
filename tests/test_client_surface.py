"""The client's surface: the registrations, the helpers, and run().

test_client.py covers the interesting path, which is an update arriving and a
handler answering it. This covers the rest of the file, which is mostly thin:
one decorator per dispatcher kind, the small module-level
helpers, and the one-line wrappers over methods that live in methods/.

Thin is exactly why it is worth a sweep rather than a test each. Every one of
these is a place where the wrong string or the wrong argument produces a
handler that never runs or a call that never goes out, and neither of those
raises anything: the failure is silence, which is the kind this suite exists to
refuse.
"""

from __future__ import annotations

import asyncio

import pytest

from sunnygram.client import (
    Client,
    _as_result,
    _peer_id,
    _random_id,
    _storage_for,
    _topic_opened,
)
from sunnygram.dispatcher import KINDS
from sunnygram.errors import SunnygramError
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SQLiteStorage
from sunnygram.types import InlineResult

from test_client import CHANNEL, ME, OTHER, a_message, live

# Every decorator on the client, and the dispatcher kind it registers for. The
# pairing is the thing under test: a decorator wired to the wrong word is a
# handler that is never called and never complains.
DECORATORS = {
    "on_message": "message",
    "on_edited": "edited",
    "on_scheduled": "scheduled",
    "on_album": "album",
    "on_callback_query": "callback",
    "on_inline_query": "inline_query",
    "on_chosen_result": "chosen_result",
    "on_chat_member": "chat_member",
    "on_join_request": "join_request",
    "on_deleted": "deleted",
    "on_reaction": "reaction",
    "on_poll": "poll",
    "on_poll_vote": "poll_vote",
    "on_story": "story",
    "on_shipping": "shipping",
    "on_pre_checkout": "pre_checkout",
    "on_status": "status",
    "on_typing": "typing",
    "on_blocked": "blocked",
    "on_stopped": "stopped",
    "on_raw": "raw",
}


class TestEveryDecoratorRegistersItsOwnKind:
    def test_the_table_below_covers_every_kind_there_is(self):
        # A sweep that has fallen behind the thing it sweeps passes quietly, so
        # the list is checked against the dispatcher's own before it is used.
        assert set(DECORATORS.values()) == set(KINDS)

    @pytest.mark.parametrize("name,kind", sorted(DECORATORS.items()))
    async def test_a_decorator_registers_for_its_kind(self, name, kind):
        async with live() as (client, _server):

            async def handler(_client, _update):
                return None

            decorate = getattr(client, name)
            # on_raw takes no filter, which is the one shape difference.
            decorated = decorate(group=3)(handler) if kind == "raw" else decorate(
                None, group=3
            )(handler)
            assert decorated is handler

            registered = [
                h for h in client.dispatcher.handlers if h.callback is handler
            ]
            assert len(registered) == 1
            assert registered[0].kind == kind
            assert registered[0].group == 3

    async def test_a_handler_can_be_added_and_taken_away_again(self):
        async with live() as (client, _server):

            async def handler(_client, _update):
                return None

            added = client.add_handler(handler, kind="poll_vote", group=2)
            assert added.kind == "poll_vote"
            assert added in client.dispatcher.handlers
            client.remove_handler(added)
            assert added not in client.dispatcher.handlers

    async def test_adding_an_album_handler_turns_collection_on(self):
        async with live() as (client, _server):

            async def handler(_client, _messages):
                return None

            client.add_handler(handler, kind="album")
            assert client.dispatcher.albums is not None


class TestTheHelpers:
    def test_a_storage_object_is_taken_as_it_is(self):
        given = MemoryStorage()
        assert _storage_for(given) is given

    @pytest.mark.parametrize("name", [":memory:", ""])
    def test_the_two_names_that_mean_do_not_keep_it(self, name):
        assert isinstance(_storage_for(name), MemoryStorage)

    def test_a_plain_name_becomes_a_session_file(self, tmp_path):
        storage = _storage_for(tmp_path / "account")
        assert isinstance(storage, SQLiteStorage)
        assert str(storage.path).endswith("account.session")

    def test_a_name_that_already_says_session_is_not_said_twice(self, tmp_path):
        storage = _storage_for(tmp_path / "account.session")
        assert str(storage.path).endswith("account.session")
        assert not str(storage.path).endswith(".session.session")

    def test_a_random_id_is_a_signed_64_bit_number(self):
        seen = {_random_id() for _ in range(50)}
        assert len(seen) == 50
        assert all(-(2**63) <= value < 2**63 for value in seen)

    @pytest.mark.parametrize(
        "peer,expected",
        [
            (types.InputPeerChannel(channel_id=7, access_hash=1), 7),
            (types.InputPeerChat(chat_id=8), 8),
            (types.InputPeerUser(user_id=9, access_hash=1), 9),
            (types.PeerChannel(channel_id=7), 7),
            (types.PeerUser(user_id=9), 9),
            (types.InputPeerEmpty(), 0),
        ],
    )
    def test_an_id_is_read_out_of_either_spelling(self, peer, expected):
        assert _peer_id(peer) == expected

    def test_a_raw_inline_result_goes_through_untouched(self):
        raw = types.InputBotInlineResult(
            id="1",
            type="article",
            send_message=types.InputBotInlineMessageText(message="hi"),
        )
        assert _as_result(raw, lambda text: (text, [])) is raw

    def test_a_written_inline_result_is_built(self):
        built = _as_result(
            InlineResult(id="1", title="A title", text="hello"),
            lambda text: (text, []),
        )
        assert isinstance(built, types.InputBotInlineResult)

    @pytest.mark.parametrize(
        "answer,expected",
        [
            (
                types.Updates(
                    updates=[types.UpdateMessageID(id=77, random_id=1)],
                    users=[],
                    chats=[],
                    date=0,
                    seq=0,
                ),
                77,
            ),
            (
                types.Updates(
                    updates=[
                        types.UpdateNewMessage(
                            message=a_message(88), pts=1, pts_count=1
                        )
                    ],
                    users=[],
                    chats=[],
                    date=0,
                    seq=0,
                ),
                88,
            ),
            (
                types.Updates(updates=[], users=[], chats=[], date=0, seq=0),
                None,
            ),
            # Something that is not an updates container at all.
            (True, None),
        ],
    )
    def test_a_new_topic_is_found_either_way_it_is_announced(self, answer, expected):
        assert _topic_opened(answer) == expected


async def _no_op_start(self, **_options):
    return None


async def _no_op_stop(self):
    return None


class TestRun:
    def test_run_starts_does_the_work_and_stops(self, monkeypatch):
        # run owns the event loop, so it cannot be driven from inside one. What
        # is under test is the sequence: start, the work, stop, in that order
        # and with stop happening even though the work returned a value.
        order: list[str] = []

        async def fake_start(self, **_options):
            order.append("start")

        async def fake_stop(self):
            order.append("stop")

        monkeypatch.setattr(Client, "start", fake_start)
        monkeypatch.setattr(Client, "stop", fake_stop)
        client = Client(MemoryStorage(), api_id=1, api_hash="x")

        async def work():
            order.append("work")
            return "done"

        assert client.run(work()) == "done"
        assert order == ["start", "work", "stop"]

    def test_run_stops_even_when_the_work_raises(self, monkeypatch):
        stopped: list[str] = []

        async def fake_start(self, **_options):
            return None

        async def fake_stop(self):
            stopped.append("stop")

        monkeypatch.setattr(Client, "start", fake_start)
        monkeypatch.setattr(Client, "stop", fake_stop)
        client = Client(MemoryStorage(), api_id=1, api_hash="x")

        async def work():
            raise ValueError("the handler blew up")

        with pytest.raises(ValueError, match="blew up"):
            client.run(work())
        assert stopped == ["stop"]

    def test_run_uses_the_fast_loop_when_there_is_one(self, monkeypatch):
        # run is the only place the library makes a loop, so it is the only
        # place the choice can be made, and a speedup that quietly does not
        # happen is the kind nobody ever notices.
        from sunnygram import loop as loop_module

        made: list[str] = []

        def fake_factory():
            def build():
                made.append("fast")
                return asyncio.new_event_loop()

            return build

        monkeypatch.setattr(loop_module, "loop_factory", fake_factory)
        monkeypatch.setattr(Client, "start", _no_op_start)
        monkeypatch.setattr(Client, "stop", _no_op_stop)
        client = Client(MemoryStorage(), api_id=1, api_hash="x")

        async def work():
            return "done"

        assert client.run(work()) == "done"
        assert made == ["fast"]

    def test_fast_loop_false_asks_for_nothing_but_asyncio(self, monkeypatch):
        # The escape hatch, for a program that has a reason to want the plain
        # loop back. It has to not consult the ladder at all, otherwise
        # ruling uvloop in or out of a bug is not something it can do.
        from sunnygram import loop as loop_module

        asked: list[str] = []

        def fake_factory():
            asked.append("asked")
            return None

        monkeypatch.setattr(loop_module, "loop_factory", fake_factory)
        monkeypatch.setattr(Client, "start", _no_op_start)
        monkeypatch.setattr(Client, "stop", _no_op_stop)
        client = Client(MemoryStorage(), api_id=1, api_hash="x")

        async def work():
            return "done"

        assert client.run(work(), fast_loop=False) == "done"
        assert asked == []

    def test_run_treats_being_interrupted_as_an_ordinary_stop(self, monkeypatch):
        # Ctrl-C is how most of these programs end, and it should not print a
        # traceback at somebody who did the expected thing.
        stopped: list[str] = []

        async def fake_start(self, **_options):
            return None

        async def fake_stop(self):
            stopped.append("stop")

        monkeypatch.setattr(Client, "start", fake_start)
        monkeypatch.setattr(Client, "stop", fake_stop)
        client = Client(MemoryStorage(), api_id=1, api_hash="x")

        async def work():
            raise KeyboardInterrupt

        assert client.run(work()) is None
        assert stopped == ["stop"]


class TestTheProperties:
    async def test_the_parts_are_reachable_and_are_the_ones_in_use(self):
        async with live() as (client, _server):
            assert client.invoker is not None
            assert client.updates.running
            assert client.dispatcher is not None
            assert client.me is not None and client.me.id == ME
            assert client.running

    async def test_repr_says_who_it_is_without_saying_anything_private(self):
        async with live() as (client, _server):
            text = repr(client)
            assert "Client" in text
            assert client.invoker.client.api_hash not in text

    async def test_starting_twice_is_refused(self):
        async with live() as (client, _server):
            with pytest.raises(Exception):
                await client.start()


class TestTheBranchesThatAreNotJustDelegation:
    """The handful of client methods that decide something themselves.

    Most of this file is one line handing an invoker to a function in methods/,
    which is tested there. These are the ones where the client picks between
    two calls, or arranges something before making one, and that choice is
    only exercised from here.
    """

    async def test_deleting_in_a_channel_takes_the_channel_call(self):
        # A channel counts its own messages, so deleting in one is a different
        # request taking the channel rather than the peer. Sending the ordinary
        # one would delete nothing and report success.
        async with live() as (client, server):
            # Named directly, because the scripted server resolves every
            # username to a user and the branch under test is the other one.
            channel = types.InputPeerChannel(
                channel_id=CHANNEL, access_hash=CHANNEL * 3
            )
            await client.delete_messages(channel, [1, 2, 3])
            sent = server.only(functions.channels.DeleteMessages)
            assert len(sent) == 1
            assert sent[0].id == [1, 2, 3]
            assert sent[0].channel.channel_id == CHANNEL
            assert not server.only(functions.messages.DeleteMessages)

    async def test_deleting_in_a_private_chat_takes_the_ordinary_call(self):
        async with live() as (client, server):
            removed = await client.delete_messages("@durov", [4, 5], everywhere=True)
            sent = server.only(functions.messages.DeleteMessages)
            assert len(sent) == 1
            assert sent[0].id == [4, 5]
            assert sent[0].revoke is True
            assert removed == 2

    async def test_a_download_is_given_a_way_to_renew_a_stale_reference(self):
        # The reference in a file id expires after an hour or so, and the cure
        # is re-fetching whatever carried it. The client arranges that without
        # being asked, which is what lets a reference stored last week work.
        async with live() as (client, server):
            renew = client._refetching((types.InputPeerUser(user_id=OTHER, access_hash=3), 42))
            renewed = await renew()
            assert isinstance(renewed, types.Message)
            assert renewed.id == 42

    async def test_renewing_says_so_plainly_when_the_message_is_gone(self):
        async with live() as (client, server):
            server.messages_are_gone = True
            renew = client._refetching((types.InputPeerUser(user_id=OTHER, access_hash=3), 42))
            with pytest.raises(SunnygramError, match="no longer there"):
                await renew()

    async def test_asking_for_a_profile_photo_nobody_has_says_so(self):
        async with live() as (client, _server):
            with pytest.raises(SunnygramError, match="no profile photo"):
                await client.download_profile_photo("@durov")


class TestResolving:
    async def test_a_username_becomes_an_input_peer(self):
        async with live() as (client, _server):
            where = await client.resolve("@durov")
            assert isinstance(where, types.InputPeerUser)
            assert where.user_id == OTHER

    async def test_me_resolves_without_asking_anybody(self):
        async with live() as (client, _server):
            where = await client.resolve("me")
            assert isinstance(where, (types.InputPeerSelf, types.InputPeerUser))

    async def test_an_input_peer_is_already_resolved(self):
        async with live() as (client, _server):
            given = types.InputPeerUser(user_id=OTHER, access_hash=3)
            assert await client.resolve(given) is given
