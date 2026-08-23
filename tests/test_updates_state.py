"""The arithmetic that decides whether an update is next, old, or past a gap.

No connection here and nothing async: these are the rules on their own, which is
the point of keeping them in a module of their own. Everything that can go wrong
in the update layer goes wrong here first.
"""

from __future__ import annotations

import pytest

from sunnygram.raw import types
from sunnygram.storage import UpdateState
from sunnygram.updates import Verdict, counter_of, judge, seq_verdict
from sunnygram.updates.state import apply, channel_of


def a_message(peer: types.PeerChannel | types.PeerUser | None = None) -> types.Message:
    return types.Message(
        id=1,
        peer_id=types.PeerUser(user_id=7) if peer is None else peer,
        date=0,
        message="hi",
    )


class TestCounters:
    def test_a_new_message_moves_the_common_pts(self):
        counter = counter_of(
            types.UpdateNewMessage(message=a_message(), pts=11, pts_count=1)
        )
        assert counter is not None
        assert (counter.kind, counter.value, counter.count) == ("pts", 11, 1)

    def test_a_channel_message_counts_against_its_own_channel(self):
        update = types.UpdateNewChannelMessage(
            message=a_message(types.PeerChannel(channel_id=-100)), pts=4, pts_count=1
        )
        counter = counter_of(update)
        assert counter is not None
        assert counter.kind == "channel"
        assert counter.channel_id == -100
        assert channel_of(update) == -100

    def test_a_channel_update_that_names_its_channel_directly(self):
        update = types.UpdateDeleteChannelMessages(
            channel_id=55, messages=[1, 2], pts=9, pts_count=2
        )
        counter = counter_of(update)
        assert counter is not None
        assert (counter.channel_id, counter.count) == (55, 2)

    def test_a_secret_message_moves_the_qts(self):
        counter = counter_of(
            types.UpdateNewEncryptedMessage(
                message=types.EncryptedMessageService(
                    random_id=1, chat_id=1, date=0, bytes=b""
                ),
                qts=3,
            )
        )
        assert counter is not None
        assert (counter.kind, counter.value, counter.count) == ("qts", 3, 1)

    def test_a_short_message_carries_its_own_counter(self):
        counter = counter_of(
            types.UpdateShortMessage(
                id=1, user_id=7, message="hi", pts=12, pts_count=1, date=0
            )
        )
        assert counter is not None
        assert counter.kind == "pts"

    def test_an_update_with_nothing_to_order_has_no_counter(self):
        assert counter_of(types.UpdateUserTyping(user_id=7, action=None)) is None
        assert channel_of(types.UpdateUserTyping(user_id=7, action=None)) == 0

    def test_a_member_change_moves_the_qts(self):
        counter = counter_of(
            types.UpdateChannelParticipant(
                channel_id=55, date=0, actor_id=1, user_id=7, qts=4
            )
        )
        assert counter is not None
        assert (counter.kind, counter.value, counter.count) == ("qts", 4, 1)

    def test_a_join_request_moves_the_qts(self):
        counter = counter_of(
            types.UpdateBotChatInviteRequester(
                peer=types.PeerUser(user_id=7),
                date=0,
                user_id=7,
                about="",
                invite=types.ChatInviteExported(link="t.me/+x", admin_id=1, date=0),
                qts=4,
            )
        )
        assert counter is not None
        assert counter.kind == "qts"


class TestEveryCounterTheSchemaGives:
    """The drift guard, which is the reason this fault could exist at all.

    An update that moves a counter and is not counted is not dropped, which is
    what makes it so quiet: it is delivered, and then delivered again after the
    next resync, because the mark it should have moved never moved and the
    server is entitled to believe we never saw it. The list of qts carriers had
    one name in it while the pinned layer had seventeen.

    So the schema is asked rather than a list, both in the code and here. This
    walks the generated surface for every constructor the schema gives a
    counter to and asserts the arithmetic knows about it, which means the next
    layer bump reports the difference rather than quietly widening the hole.
    """

    def _constructors_with(self, field: str) -> list[type]:
        found = []
        for name in types.__all__:
            candidate = getattr(types, name)
            if not isinstance(candidate, type) or not name.startswith("Update"):
                continue
            if field in getattr(candidate, "__slots__", ()):
                found.append(candidate)
        return found

    def test_every_update_that_carries_a_qts_moves_it(self):
        carriers = self._constructors_with("qts")
        # A walk that finds nothing would pass every assertion under it, which
        # is the one way this test could rot into saying nothing at all.
        assert len(carriers) > 10

        for constructor in carriers:
            # Built without going through __init__, since the fields these need
            # differ from one to the next and the only one under test is the
            # counter. A slotted class is happy to be made this way.
            update = object.__new__(constructor)
            update.qts = 7
            counter = counter_of(update)
            assert counter is not None, f"{constructor.QUALNAME} does not count"
            assert (counter.kind, counter.value, counter.count) == ("qts", 7, 1)

    def test_every_update_that_advances_a_pts_moves_it(self):
        # The same question for the other counter, which is answered by two
        # hand-written lists and so is the one that can still fall behind. The
        # split is real, since a channel counts on its own, so the lists stay,
        # but nothing that advances a pts may go uncounted.
        #
        # Advancing is what pts_count says, and carrying both fields is what
        # makes an update one of these. The two that carry a pts without one
        # are not increments at all and have their own test below.
        advancing = [
            constructor
            for constructor in self._constructors_with("pts")
            if "pts_count" in constructor.__slots__
        ]
        assert len(advancing) > 10

        for constructor in advancing:
            update = object.__new__(constructor)
            update.pts = 7
            update.pts_count = 1
            # A channel update has to say which channel, the way a real one
            # always does: either directly or through the message it carries.
            # One that names no channel is deliberately uncounted, so leaving
            # this out would be exercising that path instead of this one.
            slots = constructor.__slots__
            if "channel_id" in slots:
                update.channel_id = 55
            elif "message" in slots:
                update.message = a_message(types.PeerChannel(channel_id=55))
            assert counter_of(update) is not None, f"{constructor.QUALNAME} is uncounted"

    def test_a_channel_update_that_names_no_channel_is_not_counted(self):
        # Nothing in the schema produces this, so it means malformed server data
        # or a field that moved. Counting it would write a mark under the id
        # zero, which belongs to no channel, and then keep comparing against it
        # for the life of the session. Delivering it uncounted costs the
        # ordering of one update instead.
        update = types.UpdateNewChannelMessage(
            message=a_message(types.PeerUser(user_id=7)), pts=4, pts_count=1
        )
        assert counter_of(update) is None

    def test_the_two_that_carry_a_pts_without_advancing_one(self):
        """Both are deliberate, and neither can lose us our place.

        The schema gives exactly two updates a pts and no pts_count, and the
        difference from the qts fault is worth being precise about, because
        "not counted" describes both and means opposite things.

        A qts update that went uncounted left the mark behind the server's, so
        the next difference was asked from a position the account had passed
        and everything after it came back a second time. These two cannot do
        that, because neither is an increment: the pts they carry is a
        statement of where the channel already is, put there by the messages
        that did carry a pts_count. Ignoring them costs a chance to notice a
        gap somebody else will notice a moment later. It cannot cost a place in
        the stream, and it cannot deliver anything twice.

        updateChannelTooLong is read before the counters in any case. Its pts is
        the channel's latest on the server, which is where a gap ends rather
        than where it starts, so it is a signal that one exists and never the
        position to ask from. Asking from it was a real bug: the difference came
        back empty, because nothing has changed since the newest thing there is,
        and the empty answer was written down as having caught up.
        """
        stated = [
            constructor
            for constructor in self._constructors_with("pts")
            if "pts_count" not in constructor.__slots__
        ]
        assert {constructor.QUALNAME for constructor in stated} == {
            "types.UpdateChannelTooLong",
            "types.UpdateReadChannelInbox",
        }

        read = types.UpdateReadChannelInbox(
            channel_id=55, max_id=9, still_unread_count=0, pts=7
        )
        assert counter_of(read) is None


class TestJudging:
    def test_the_next_one_is_applied(self):
        state = UpdateState(pts=10)
        counter = counter_of(
            types.UpdateNewMessage(message=a_message(), pts=11, pts_count=1)
        )
        assert judge(state, counter) is Verdict.APPLY
        apply(state, counter)
        assert state.pts == 11

    def test_one_we_have_already_had_is_old(self):
        state = UpdateState(pts=11)
        counter = counter_of(
            types.UpdateNewMessage(message=a_message(), pts=11, pts_count=1)
        )
        assert judge(state, counter) is Verdict.OLD

    def test_one_that_skips_ahead_is_a_gap(self):
        state = UpdateState(pts=10)
        counter = counter_of(
            types.UpdateNewMessage(message=a_message(), pts=20, pts_count=1)
        )
        assert judge(state, counter) is Verdict.GAP

    def test_a_batch_that_lands_exactly_is_applied(self):
        # pts_count is how many the update accounts for, so a delete of three
        # messages moves the counter by three in one go.
        state = UpdateState(pts=10)
        counter = counter_of(
            types.UpdateDeleteMessages(messages=[1, 2, 3], pts=13, pts_count=3)
        )
        assert judge(state, counter) is Verdict.APPLY
        apply(state, counter)
        assert state.pts == 13

    def test_a_batch_that_lands_short_is_a_gap(self):
        state = UpdateState(pts=10)
        counter = counter_of(
            types.UpdateDeleteMessages(messages=[1, 2, 3], pts=20, pts_count=3)
        )
        assert judge(state, counter) is Verdict.GAP

    def test_knowing_nothing_yet_means_taking_what_arrives(self):
        state = UpdateState()
        counter = counter_of(
            types.UpdateNewMessage(message=a_message(), pts=5000, pts_count=1)
        )
        assert judge(state, counter) is Verdict.APPLY

    def test_channels_are_judged_apart_from_the_common_stream(self):
        state = UpdateState(pts=10, channels={-100: 4})
        update = types.UpdateNewChannelMessage(
            message=a_message(types.PeerChannel(channel_id=-100)), pts=5, pts_count=1
        )
        counter = counter_of(update)
        assert judge(state, counter) is Verdict.APPLY
        apply(state, counter)
        assert state.channels[-100] == 5
        # The common counter did not move, because this was never in it.
        assert state.pts == 10

    def test_one_channel_falling_behind_does_not_affect_another(self):
        state = UpdateState(channels={-100: 4, -200: 90})
        behind = counter_of(
            types.UpdateNewChannelMessage(
                message=a_message(types.PeerChannel(channel_id=-100)),
                pts=40,
                pts_count=1,
            )
        )
        fine = counter_of(
            types.UpdateNewChannelMessage(
                message=a_message(types.PeerChannel(channel_id=-200)),
                pts=91,
                pts_count=1,
            )
        )
        assert judge(state, behind) is Verdict.GAP
        assert judge(state, fine) is Verdict.APPLY


class TestSequence:
    def test_the_next_container_is_applied(self):
        assert seq_verdict(UpdateState(seq=4), 5, 5) is Verdict.APPLY

    def test_one_already_seen_is_old(self):
        assert seq_verdict(UpdateState(seq=9), 5, 5) is Verdict.OLD

    def test_one_that_skips_ahead_is_a_gap(self):
        assert seq_verdict(UpdateState(seq=4), 9, 9) is Verdict.GAP

    def test_a_container_outside_the_sequence_is_always_applied(self):
        # seq zero means the server is not numbering this one at all.
        assert seq_verdict(UpdateState(seq=4), 0, 0) is Verdict.APPLY

    def test_a_combined_container_is_judged_by_where_it_starts(self):
        # updatesCombined covers a range, so it is the start that has to follow
        # on from what we have.
        assert seq_verdict(UpdateState(seq=4), 5, 9) is Verdict.APPLY
        assert seq_verdict(UpdateState(seq=4), 6, 9) is Verdict.GAP

    def test_knowing_nothing_yet_means_taking_what_arrives(self):
        assert seq_verdict(UpdateState(), 500, 500) is Verdict.APPLY


@pytest.mark.parametrize(
    "kind, field", [("pts", "pts"), ("qts", "qts")]
)
def test_applying_moves_only_its_own_counter(kind, field):
    state = UpdateState(pts=1, qts=1)
    counter = counter_of(
        types.UpdateNewMessage(message=a_message(), pts=2, pts_count=1)
        if kind == "pts"
        else types.UpdateNewEncryptedMessage(
            message=types.EncryptedMessageService(
                random_id=1, chat_id=1, date=0, bytes=b""
            ),
            qts=2,
        )
    )
    apply(state, counter)
    assert getattr(state, field) == 2
    assert getattr(state, "qts" if field == "pts" else "pts") == 1
