"""The update stream, held against a model of what the server actually did.

Every other test in this suite asks whether one known fault is handled. This one
asks the question the module docstring actually promises, and that no example
can answer: given any sequence of things a server is allowed to do, is every
update delivered exactly once and in order?

Hypothesis generates the sequence. The server here is a model rather than a
script: it holds the true history, decides for itself what to send and what to
withhold, and answers a difference with exactly what it withheld. That is the
part worth having. A scripted server answers what the test author expected to be
asked, so a client asking the wrong question still gets a plausible answer and
the test passes. This one answers what was really asked against the history it
really has, so asking from the wrong place earns the empty answer it deserves
and an invariant notices what got skipped.

All three counters are modelled, because they fail differently. pts is the
common stream. qts covers secret chats and the long tail of events added to the
protocol later, and is where sixteen constructors once went uncounted. seq
numbers the containers themselves, so a gap there is a gap in the envelopes
rather than in anything they carry. Channels are counted apart, one mark each,
and there are two of them here so that a mark belonging to one can never quietly
be used for the other.

Two of the server's answers are allowed to lose updates on purpose, and getting
that right is what keeps the model honest rather than merely strict.
differenceTooLong and channelDifferenceTooLong both mean "you are too far behind
to be told in detail, here is the counter, re-read what you need as history".
Those updates are forgiven: the server never showed them and never will, so an
invariant that demanded them would be demanding something the protocol does not
offer. Everything not forgiven is owed.
"""

from __future__ import annotations

import asyncio
from typing import Any

from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    precondition,
    rule,
)

from sunnygram.raw import functions, types
from sunnygram.storage import PeerKind, PeerRecord, UpdateState
from sunnygram.updates import UpdateManager

# Two, so that a mark belonging to one channel can never be used for the other
# without an invariant noticing.
CHANNELS = (55, 66)

# How many updates one difference slice carries when the server is slicing.
SLICE = 2


def _message(id: int, peer: Any = None) -> types.Message:
    return types.Message(
        id=id,
        peer_id=peer or types.PeerUser(user_id=7),
        date=1700000000,
        message=f"message {id}",
    )


def _bot_stopped(id: int, qts: int) -> types.UpdateBotStopped:
    """A qts-counted update that is deliberately not the encrypted one.

    The fault this layer actually had was a qts list naming one constructor out
    of the seventeen that carry the counter, and the one it named was
    updateNewEncryptedMessage. A model that only ever generates that one cannot
    tell the narrow implementation from the right one, which is why this is a
    bot event instead. Found by mutation testing: the first version of this file
    used the encrypted message and the old bug walked straight through it.
    """
    return types.UpdateBotStopped(user_id=id, date=1700000000, stopped=True, qts=qts)


def _typing(id: int) -> types.UpdateUserTyping:
    """An update carrying no counter at all.

    These are what seq is for. An update with a pts announces its own gap, so a
    container that goes missing carrying one is noticed twice over and seq never
    gets a chance to be the thing that caught it. A container of these is
    invisible to every counter, so the envelope numbering is the only thing left.
    """
    return types.UpdateUserTyping(user_id=id, action=types.SendMessageTypingAction())


class ModelPeers:
    """Just enough peer cache for the manager to be able to name the channels."""

    def __init__(self) -> None:
        self.known = {
            id: PeerRecord(id=id, kind=PeerKind.CHANNEL, access_hash=id * 3)
            for id in CHANNELS
        }

    async def get(self, peer_id: int) -> PeerRecord | None:
        return self.known.get(peer_id)

    def learn(self, *peers: Any) -> int:
        return 0

    async def flush(self, *, force: bool = True) -> int:
        return 0


class ModelServer:
    """A datacenter that remembers what really happened.

    The history is the truth. Everything the client is told, and everything it
    is later given when it asks for a difference, is derived from that rather
    than handed over by the test, which is what stops the model from agreeing
    with a client that asked the wrong question.
    """

    def __init__(self) -> None:
        self.history: list[int] = []
        self.qts_history: list[int] = []
        # Updates carrying no counter. They travel in containers and are made
        # good through the other_updates of a difference, so the only thing that
        # can notice one going missing is the container sequence.
        self.presence: list[int] = []
        self.withheld_presence: list[int] = []
        self.channels: dict[int, list[int]] = {id: [] for id in CHANNELS}
        self.next_id = 1
        self.seq = 0
        # What the client was really shown, whether announced or handed over in
        # a difference. Anything in a history and not in here is owed.
        self.shown: set[int] = set()
        # What the server has said it will never describe in detail. Both of the
        # "too long" answers mean exactly that, and an update inside one of them
        # is not a loss, it is the protocol declining to replay history.
        self.forgiven: set[int] = set()
        # Whether the next difference comes back in slices, and whether it comes
        # back as a refusal to describe anything at all.
        self.slicing = False
        self.too_long = False
        self.channel_too_long = False

    @property
    def pts(self) -> int:
        """The server's counter, which is simply how much has happened."""
        return len(self.history)

    @property
    def qts(self) -> int:
        return len(self.qts_history)

    def channel_pts(self, channel: int) -> int:
        return len(self.channels[channel])

    def next_seq(self) -> int:
        self.seq += 1
        return self.seq

    def add(
        self,
        *,
        channel: int | None = None,
        secret: bool = False,
        uncounted: bool = False,
    ) -> int:
        """Something happened. Returns the id it happened to."""
        message_id = self.next_id
        self.next_id += 1
        if channel is not None:
            self.channels[channel].append(message_id)
        elif secret:
            self.qts_history.append(message_id)
        elif uncounted:
            self.presence.append(message_id)
        else:
            self.history.append(message_id)
        return message_id

    def update_for(self, message_id: int, *, channel: int | None = None) -> Any:
        """The update announcing one event, carrying the pts it really has."""
        self.shown.add(message_id)
        if channel is not None:
            return types.UpdateNewChannelMessage(
                message=_message(message_id, types.PeerChannel(channel_id=channel)),
                pts=self.channels[channel].index(message_id) + 1,
                pts_count=1,
            )
        return types.UpdateNewMessage(
            message=_message(message_id),
            pts=self.history.index(message_id) + 1,
            pts_count=1,
        )

    def secret_update_for(self, message_id: int) -> Any:
        """The same for a qts-counted update, which counts one at a time."""
        self.shown.add(message_id)
        return _bot_stopped(message_id, self.qts_history.index(message_id) + 1)

    def presence_update_for(self, message_id: int) -> Any:
        """An update with no counter, which only the envelope can order."""
        self.shown.add(message_id)
        return _typing(message_id)

    def difference_since(self, pts: int, qts: int) -> Any:
        """Everything after the marks given, the way the real one answers it.

        The client says where it has got to and is given what came after. Asking
        from too far along is answered honestly, which means answered with
        nothing, and that is the point of modelling rather than scripting: an
        empty answer is what a wrong cursor earns, and the invariants are what
        notice the messages it skipped over.
        """
        missed = self.history[max(pts, 0) :]
        missed_secret = self.qts_history[max(qts, 0) :]

        if self.too_long:
            # Too far behind to be told in detail. The counter is all the client
            # gets, and everything under it is history it must re-read for
            # itself, so it is forgiven rather than owed.
            self.too_long = False
            self.forgiven.update(missed)
            self.forgiven.update(missed_secret)
            return types.updates.DifferenceTooLong(pts=self.pts)

        if self.slicing and len(missed) > SLICE:
            head = missed[:SLICE]
            self.shown.update(head)
            return types.updates.DifferenceSlice(
                new_messages=[_message(one) for one in head],
                new_encrypted_messages=[],
                other_updates=[],
                chats=[],
                users=[],
                intermediate_state=types.updates.State(
                    pts=pts + len(head),
                    qts=qts,
                    date=1700000000,
                    seq=self.seq,
                    unread_count=0,
                ),
            )

        # Everything uncounted that was withheld goes out here, which is the
        # only way one of those is ever made good.
        owed_presence, self.withheld_presence = self.withheld_presence, []
        self.shown.update(missed)
        self.shown.update(missed_secret)
        self.shown.update(owed_presence)
        return types.updates.Difference(
            new_messages=[_message(one) for one in missed],
            new_encrypted_messages=[],
            other_updates=(
                [
                    _bot_stopped(one, self.qts_history.index(one) + 1)
                    for one in missed_secret
                ]
                + [_typing(one) for one in owed_presence]
            ),
            chats=[],
            users=[],
            state=types.updates.State(
                pts=self.pts,
                qts=self.qts,
                date=1700000000,
                seq=self.seq,
                unread_count=0,
            ),
        )

    def channel_difference_since(self, channel: int, pts: int) -> Any:
        history = self.channels[channel]
        missed = history[max(pts, 0) :]

        if self.channel_too_long:
            # The dialog says where the channel is now. Its messages are history
            # rather than updates and are not delivered as events, so they are
            # forgiven for the same reason the common one above is.
            self.channel_too_long = False
            self.forgiven.update(missed)
            return types.updates.ChannelDifferenceTooLong(
                final=True,
                timeout=None,
                dialog=types.Dialog(
                    peer=types.PeerChannel(channel_id=channel),
                    top_message=history[-1] if history else 0,
                    read_inbox_max_id=0,
                    read_outbox_max_id=0,
                    unread_count=0,
                    unread_mentions_count=0,
                    unread_reactions_count=0,
                    unread_poll_votes_count=0,
                    notify_settings=types.PeerNotifySettings(),
                    pts=len(history),
                ),
                messages=[],
                chats=[],
                users=[],
            )

        self.shown.update(missed)
        return types.updates.ChannelDifference(
            final=True,
            pts=len(history),
            timeout=None,
            new_messages=[
                _message(one, types.PeerChannel(channel_id=channel)) for one in missed
            ],
            other_updates=[],
            chats=[],
            users=[],
        )


class _SessionLike:
    def __init__(self, updates: UpdateState) -> None:
        self.updates = updates


class ModelInvoker:
    """What the manager talks through, backed by the model server."""

    def __init__(self, server: ModelServer, state: UpdateState) -> None:
        self._server = server
        self.state = _SessionLike(state)
        self.peers = ModelPeers()
        self.updates: asyncio.Queue[Any] = asyncio.Queue(512)
        self.dropped_updates = 0

    async def save(self) -> None:
        return None

    async def invoke(self, request: Any, **_options: Any) -> Any:
        if isinstance(request, functions.updates.GetState):
            return types.updates.State(
                pts=self._server.pts,
                qts=self._server.qts,
                date=1700000000,
                seq=self._server.seq,
                unread_count=0,
            )
        if isinstance(request, functions.updates.GetDifference):
            return self._server.difference_since(request.pts, request.qts)
        if isinstance(request, functions.updates.GetChannelDifference):
            return self._server.channel_difference_since(
                request.channel.channel_id, request.pts
            )
        raise AssertionError(f"the manager asked something unmodelled: {request!r}")


class UpdateStream(RuleBasedStateMachine):
    """Any sequence a server is allowed to produce, against the promises."""

    def __init__(self) -> None:
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.server = ModelServer()
        self.state = UpdateState(pts=0, qts=0, date=1700000000, seq=0)
        self.invoker = ModelInvoker(self.server, self.state)
        self.manager = UpdateManager(self.invoker, events_queue=4096)
        # Everything the program was handed, in the order it was handed it.
        self.delivered: list[int] = []

    def teardown(self) -> None:
        self.loop.close()

    def _run(self, work: Any) -> Any:
        return self.loop.run_until_complete(work)

    def _collect(self) -> None:
        """Take whatever has reached the program since the last look."""
        while True:
            try:
                event = self.manager.events.get_nowait()
            except asyncio.QueueEmpty:
                return
            found = self._identify(event.update)
            if found is not None:
                self.delivered.append(found)

    @staticmethod
    def _identify(update: Any) -> int | None:
        """Which event this update is about.

        Ids come from one counter across every stream, so whichever field the
        constructor happens to carry them in names the same thing.
        """
        message = getattr(update, "message", None)
        if message is not None:
            return getattr(message, "id", None)
        return getattr(update, "user_id", None)

    def _feed(self, container: Any) -> None:
        self._run(self.manager.feed(container))
        self._collect()

    @staticmethod
    def _container(*updates: Any, seq: int = 0) -> types.Updates:
        return types.Updates(
            updates=list(updates), users=[], chats=[], date=1700000000, seq=seq
        )

    # --- the common stream --------------------------------------------------

    @rule()
    def deliver_in_order(self) -> None:
        """The ordinary case: something happens and we are told about it."""
        message_id = self.server.add()
        self._feed(self._container(self.server.update_for(message_id)))

    @rule(count=st.integers(min_value=1, max_value=5))
    def withhold_then_deliver(self, count: int) -> None:
        """Things happen we are never told of, then something else does.

        This is a gap. The later update's pts is further along than one step,
        and the only way to learn what came between is to ask for a difference.
        """
        for _ in range(count):
            self.server.add()
        message_id = self.server.add()
        self._feed(self._container(self.server.update_for(message_id)))

    @precondition(lambda self: bool(self.server.shown))
    @rule()
    def redeliver_something_already_seen(self) -> None:
        """A server that missed our acknowledgement says it again."""
        message_id = max(self.server.shown)
        if message_id in self.server.history:
            self._feed(self._container(self.server.update_for(message_id)))

    # --- the other two counters ---------------------------------------------

    @rule()
    def deliver_a_secret_message(self) -> None:
        """A qts-counted update, which is the counter that went uncounted."""
        message_id = self.server.add(secret=True)
        self._feed(self._container(self.server.secret_update_for(message_id)))

    @rule(count=st.integers(min_value=1, max_value=3))
    def withhold_a_secret_message_then_deliver(self, count: int) -> None:
        for _ in range(count):
            self.server.add(secret=True)
        message_id = self.server.add(secret=True)
        self._feed(self._container(self.server.secret_update_for(message_id)))

    @rule()
    def deliver_in_a_numbered_container(self) -> None:
        """A container that is part of the sequence rather than outside it."""
        message_id = self.server.add(uncounted=True)
        self._feed(
            self._container(
                self.server.presence_update_for(message_id), seq=self.server.next_seq()
            )
        )

    @precondition(lambda self: self.state.seq > 0)
    @rule()
    def withhold_a_whole_container_then_deliver(self) -> None:
        """An envelope that never arrives, carrying nothing that counts itself.

        This is the only fault seq can catch on its own, and getting the model
        right here took two corrections, both of them the model being unfaithful
        rather than the library being wrong.

        The first version withheld a container holding an ordinary message,
        which announces its own gap through pts, so the recovery happened for a
        reason that had nothing to do with seq and breaking seq changed nothing.
        Everything withheld here is uncounted, so the envelope numbering is
        genuinely the only evidence anything went missing.

        The second is that a container judged to be past a gap is discarded
        whole, so the update inside the one that *did* arrive is dropped along
        with the one that did not. That is correct, and it means the server owes
        both of them to the difference rather than only the missing one. A model
        that marked the arriving one as delivered was describing a server that
        does not exist.

        The precondition is the third: a client that has never seen a sequence
        number cannot know it missed one, so it adopts rather than reporting a
        gap. Asserting before then would be asserting against the protocol.

        Asserted in the rule rather than as an invariant because the difference
        is what makes these good, and until it is asked for the server has not
        shown them and no global invariant can honestly demand them.
        """
        missing = self.server.add(uncounted=True)
        self.server.withheld_presence.append(missing)
        self.server.next_seq()

        discarded = self.server.add(uncounted=True)
        self.server.withheld_presence.append(discarded)
        self._feed(self._container(_typing(discarded), seq=self.server.next_seq()))

        for one in (missing, discarded):
            assert one in self.delivered, (
                f"{one} never arrived. Nothing in either container carried a "
                "counter, so the sequence number was the only sign one had gone "
                "missing, and it was not acted on"
            )

    # --- what the server says when it cannot describe things one at a time ---

    @rule()
    def say_it_is_too_long(self) -> None:
        """The server giving up on telling us one at a time."""
        self.server.add()
        self._feed(types.UpdatesTooLong())

    @rule()
    def answer_the_next_difference_in_slices(self) -> None:
        """A catch-up that takes several round trips rather than one.

        Asserted here rather than as an invariant for the same reason as the
        sequence rule. Stopping after the first slice loses nothing and leaves
        an honest counter, so no global invariant is broken by it: the client is
        simply still behind, and the next gap would start the whole thing again.
        That is a bug all the same, and on a stream that then goes quiet it is
        one that never resolves, so what is checked is that a catch-up which was
        allowed to finish did finish.
        """
        self.server.slicing = True
        for _ in range(SLICE * 2 + 1):
            self.server.add()
        self._feed(types.UpdatesTooLong())
        self.server.slicing = False
        assert self.state.pts == self.server.pts, (
            f"the sliced catch-up stopped at pts {self.state.pts} with the "
            f"server at {self.server.pts}, so it gave up part way through "
            "rather than following the slices to the end"
        )

    @rule()
    def declare_us_too_far_behind(self) -> None:
        """differenceTooLong: here is the counter, re-read the rest as history.

        The updates under it are forgiven rather than owed. The protocol is
        declining to replay them, so a client that does not deliver them is
        obeying rather than losing.
        """
        for _ in range(3):
            self.server.add()
        self.server.too_long = True
        self._feed(types.UpdatesTooLong())
        self.server.too_long = False

    # --- channels, of which there are two -----------------------------------

    @rule(channel=st.sampled_from(CHANNELS))
    def deliver_a_channel_message(self, channel: int) -> None:
        message_id = self.server.add(channel=channel)
        self._feed(
            self._container(self.server.update_for(message_id, channel=channel))
        )

    @rule(channel=st.sampled_from(CHANNELS), count=st.integers(min_value=1, max_value=4))
    def withhold_a_channel_message_then_deliver(self, channel: int, count: int) -> None:
        for _ in range(count):
            self.server.add(channel=channel)
        message_id = self.server.add(channel=channel)
        self._feed(
            self._container(self.server.update_for(message_id, channel=channel))
        )

    @rule(channel=st.sampled_from(CHANNELS))
    def say_the_channel_is_too_long(self, channel: int) -> None:
        """The channel moved further than one update at a time can describe.

        The pts it carries is the channel's latest on the server, which is where
        the gap ends. A client asking from it gets nothing back and skips
        everything in between, which was a real bug and is what this catches.
        """
        self.server.add(channel=channel)
        self._feed(
            self._container(
                types.UpdateChannelTooLong(
                    channel_id=channel, pts=self.server.channel_pts(channel)
                )
            )
        )

    @rule(channel=st.sampled_from(CHANNELS))
    def declare_the_channel_too_far_behind(self, channel: int) -> None:
        """channelDifferenceTooLong: the dialog says where it is now."""
        for _ in range(3):
            self.server.add(channel=channel)
        self.server.channel_too_long = True
        self._feed(
            self._container(
                types.UpdateChannelTooLong(
                    channel_id=channel, pts=self.server.channel_pts(channel)
                )
            )
        )
        self.server.channel_too_long = False

    # --- the connection underneath ------------------------------------------

    @rule()
    def start_a_new_session(self) -> None:
        """Telegram moved the session between its own machines.

        Updates are counted per session, so whatever happened while we were
        being moved went to a session that no longer exists and is not coming
        back on its own. Asking is the only way to find out what it was.

        Asserted here rather than left to an invariant, and the reason is worth
        writing down because mutation testing is what found it. Ignoring this
        notification entirely does not fail any global invariant: the next
        update to arrive carries a pts further along than ours, that gap is
        noticed, and the difference it triggers recovers everything. The loss
        only becomes permanent when nothing else arrives, which is precisely the
        case a busy test never reaches and a quiet account always does. So what
        is checked is that the resynchronisation happened when it was called
        for, not merely that something eventually cleaned up after it.
        """
        self.server.add()
        self._feed(
            types.mtproto.NewSessionCreated(first_msg_id=1, unique_id=2, server_salt=3)
        )
        assert self.state.pts == self.server.pts, (
            f"the server started a new session and we are still at pts "
            f"{self.state.pts} with it at {self.server.pts}. Nothing will "
            "resend what the old session was given, so on an account that now "
            "goes quiet those updates are gone for good"
        )

    @rule()
    def drop_updates_underneath(self) -> None:
        """The connection threw some away before they reached the manager.

        Same shape as the one above and asserted for the same reason. An update
        thrown away for backpressure leaves no trace in any counter when it
        carried none, so the dropped count is the only evidence, and acting on
        it has to be checked at the moment it is read.
        """
        self.server.add()
        self.invoker.dropped_updates += 1
        # Only the drain loop notices this, so it is spelled out here the same
        # way the drain loop does it.
        self._run(self.manager._recover_losses())
        self._collect()
        assert self.state.pts == self.server.pts, (
            f"updates were dropped underneath and we are still at pts "
            f"{self.state.pts} with the server at {self.server.pts}, so the "
            "count was read and not acted on"
        )

    # --- the promises -------------------------------------------------------

    @invariant()
    def nothing_is_delivered_twice(self) -> None:
        assert len(self.delivered) == len(set(self.delivered)), (
            f"delivered more than once: {self.delivered}"
        )

    @invariant()
    def nothing_arrives_out_of_order(self) -> None:
        # Ids are handed out in the order things happen, so what the program
        # sees has to climb. The streams interleave and are each in order on
        # their own, so they are checked apart.
        streams = {
            "common": self.server.history,
            "secret": self.server.qts_history,
            **{f"channel {id}": self.server.channels[id] for id in CHANNELS},
        }
        for name, history in streams.items():
            ids = set(history)
            seen = [one for one in self.delivered if one in ids]
            assert seen == sorted(seen), f"{name} arrived out of order: {seen}"

    @invariant()
    def our_counters_never_pass_the_servers(self) -> None:
        assert self.state.pts <= self.server.pts, (
            f"our pts {self.state.pts} is past the server's {self.server.pts}, so "
            "a difference would be asked from a place that does not exist yet"
        )
        assert self.state.qts <= self.server.qts, (
            f"our qts {self.state.qts} is past the server's {self.server.qts}"
        )
        for channel in CHANNELS:
            held = self.state.channels.get(channel, 0)
            assert held <= self.server.channel_pts(channel), (
                f"our mark for channel {channel} is {held}, past the server's "
                f"{self.server.channel_pts(channel)}"
            )

    def _check_counter_is_earned(
        self, history: list[int], held: int, stream: str
    ) -> None:
        """A counter is a claim about how much of a history has been handled.

        pts = N says "I have seen the first N things that happened". So once we
        are following a stream at all, everything in the history below our own
        mark has to have reached the program, minus whatever the server has
        explicitly declined to describe. A mark that climbs past updates nobody
        was given is the exact shape of a silent loss: no ordering rule is
        broken, nothing is delivered twice, and the messages are simply gone.

        Two exclusions, both of them the protocol rather than a let-off. The
        forgiven set is what the two "too long" answers cover, which is the
        server saying it will not replay that stretch at all. And the check
        starts from the first thing we were actually given, because a channel we
        have never followed legitimately adopts wherever the server is rather
        than reading a history nobody asked for.
        """
        seen = set(self.delivered)
        followed = [one for one in history if one in seen]
        if not followed:
            return
        start = history.index(followed[0])
        owed = set(history[start:held]) - self.server.forgiven
        missing = owed - seen
        assert not missing, (
            f"the {stream} mark is at {held}, which claims {sorted(owed)} were "
            f"handled, but {sorted(missing)} never reached the program"
        )

    @invariant()
    def a_counter_never_claims_more_than_was_delivered(self) -> None:
        self._check_counter_is_earned(self.server.history, self.state.pts, "common")
        self._check_counter_is_earned(
            self.server.qts_history, self.state.qts, "secret"
        )
        for channel in CHANNELS:
            self._check_counter_is_earned(
                self.server.channels[channel],
                self.state.channels.get(channel, 0),
                f"channel {channel}",
            )

    @invariant()
    def everything_the_server_showed_us_arrives(self) -> None:
        """Nothing the server actually handed over is quietly missing.

        Anything announced or returned in a difference has to have reached the
        program, so an update that is skipped rather than delivered fails here
        even though no ordering or duplication rule was broken.
        """
        missing = self.server.shown - set(self.delivered) - self.server.forgiven
        assert not missing, (
            f"the server sent {sorted(missing)} and the program never saw them"
        )

    @invariant()
    def the_stream_is_still_running(self) -> None:
        """After any action at all, the next update still gets through.

        This is the classic form of the fault: a gap is detected, the difference
        that would have closed it is never asked for, and every update after it
        is silently ignored. Being not-wrong is not enough for this layer. It
        also has to still be delivering.
        """
        before = len(self.delivered)
        message_id = self.server.add()
        self._feed(self._container(self.server.update_for(message_id)))
        assert len(self.delivered) > before, (
            "the stream stopped: an update sent after the last action never "
            "reached the program"
        )


TestUpdateStream = UpdateStream.TestCase
TestUpdateStream.settings = settings(
    max_examples=300,
    stateful_step_count=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
