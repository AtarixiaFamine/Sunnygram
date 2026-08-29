# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Keeping the stream of updates whole.

The connection below hands over whatever the server sent that answered no call.
This turns that into a stream a program can trust: every update delivered once,
in order, with nothing missing in between, and the counters written down so the
next run starts where this one stopped.

The work is in what happens when the counters do not line up. A gap means an
update we never saw, and the only way to find out what it was is to ask, which
is what updates.getDifference is for. Channels are asked about separately, since
each counts on its own. A difference may come back in slices, or come back
saying the account is too far behind to be told in detail, and both have to be
followed to the end before anything newer is applied, or the gap simply moves.

Rule C1: this is the only thing that writes pts, qts, seq or a channel's pts.
Nothing else touches them, so there is one place to look when a message goes
missing.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self

from ..errors import Flood, InternalError, RPCError, SunnygramError, Timeout
from ..network import Invoker
from ..raw import functions, types
from ..storage import UpdateState
from ..tl import TLObject
from .state import Counter, Verdict, apply, counter_of, judge, seq_verdict

__all__ = ["Event", "UpdateManager"]

_log = logging.getLogger(__name__)

# How many events to hold for a program that is not draining them fast enough.
EVENTS_QUEUE = 1024

# A difference can arrive in slices, and each one is another round trip. Enough
# to catch up from a long absence, bounded so a server that never says it is
# finished cannot hold us here for ever.
MAX_SLICES = 100

# What to ask for in one channel difference. A hundred is what a client that is
# not a bot is allowed.
CHANNEL_LIMIT = 100

# How long a stream may stay silent before we go and ask anyway. A connection
# that has quietly stopped carrying updates looks exactly like an account with
# nothing happening on it, and the ping loop cannot tell them apart: it proves
# the socket is alive, which is the thing that was never in doubt. Telegram
# documents a quarter of an hour as the point to stop assuming.
IDLE_CATCH_UP = 15 * 60.0

# Bookkeeping instead of news. Both of these say something about a call we made
# ourselves, and whoever made it already has the answer in hand, so delivering
# them would be telling a program about its own request. They still move the
# counters, because the server counts them.
_NOT_NEWS = (types.UpdateMessageID, types.UpdateShortSentMessage)


@dataclass(frozen=True, slots=True)
class Event:
    """One update, with the users and chats it talks about.

    Updates name people and chats by id and leave the client to know the rest,
    so whatever came in the same container is carried along here. The peer cache
    has them too by the time this arrives, but it keeps only what is needed to
    reach someone; the full objects are here, for as long as the event is.
    """

    update: TLObject
    users: dict[int, TLObject] = field(default_factory=dict)
    chats: dict[int, TLObject] = field(default_factory=dict)


class UpdateManager:
    """The single source of truth for how far through the updates we are."""

    __slots__ = (
        "_invoker",
        "_events",
        "_task",
        "_lock",
        "_dropped",
        "_failures",
        "_catching_up",
        "_channel_limit",
        "_lost",
        "_resyncs",
        "_idle",
        "_seen",
        "_watchdog",
    )

    def __init__(
        self,
        invoker: Invoker,
        *,
        events_queue: int = EVENTS_QUEUE,
        channel_limit: int = CHANNEL_LIMIT,
        idle_catch_up: float = IDLE_CATCH_UP,
    ) -> None:
        self._invoker = invoker
        self._events: asyncio.Queue[Event] = asyncio.Queue(events_queue)
        self._task: asyncio.Task[None] | None = None
        # Everything that touches the counters holds this, so a difference being
        # fetched cannot interleave with an update being judged against the very
        # state that difference is about to replace.
        self._lock = asyncio.Lock()
        self._dropped = 0
        self._failures = 0
        self._catching_up = False
        self._channel_limit = channel_limit
        # How many updates the connection had already thrown away last time we
        # looked. A number that has moved means something never reached us.
        self._lost = 0
        self._resyncs = 0
        self._idle = idle_catch_up
        # Monotonic, because this measures a silence and a clock that is put
        # back would read as one that never ends.
        self._seen = time.monotonic()
        self._watchdog: asyncio.Task[None] | None = None

    def __repr__(self) -> str:
        state = self.state
        return (
            f"UpdateManager(pts={state.pts}, qts={state.qts}, seq={state.seq}, "
            f"channels={len(state.channels)})"
        )

    @property
    def state(self) -> UpdateState:
        """Where the stream has been read up to."""
        return self._invoker.state.updates

    @property
    def events(self) -> asyncio.Queue[Event]:
        """Updates in order, once each, for whoever wants to act on them."""
        return self._events

    @property
    def dropped_events(self) -> int:
        """How many events were dropped because no one was draining them.

        These are gone, and unlike every other loss in this layer they are not
        made up for later. By the time an event reaches the queue its counter
        has already been applied, so as far as the stream is concerned it was
        delivered, and no difference will ever mention it again. That is the
        deliberate half of rule P6: a program that stops reading loses the
        newest rather than stalling the session. A number above zero here means
        the program was handed something it never looked at, and the remedy is
        to drain faster or to build the manager with a bigger events_queue,
        because nothing this layer does afterwards can recover it.

        The other kind of loss, further down, is recoverable and is counted by
        resyncs instead.
        """
        return self._dropped

    @property
    def failures(self) -> int:
        """How many times acting on an update did not go through.

        Not fatal on its own: whatever failed leaves a gap, and the next update
        to notice it asks again. A number that keeps climbing is the signal.
        """
        return self._failures

    @property
    def resyncs(self) -> int:
        """How many times the stream had to be rebuilt from a difference.

        Counts the recoveries that were not the ordinary kind: a session the
        server started for itself, and updates the connection underneath threw
        away before they reached here. Both are survivable, because in both
        cases the counters had not moved yet and a difference can still fetch
        what went missing. Neither should be routine, so a number that keeps
        climbing says the program is either reconnecting or falling behind.

        Not to be confused with dropped_events, which counts what was thrown
        away on the way out of this layer instead of on the way in, and which
        no difference can bring back.
        """
        return self._resyncs

    @property
    def idle_catch_up(self) -> float:
        """How long the stream may stay silent before we go and ask anyway.

        Zero turns the watchdog off, which is the right answer only for a
        program that would rather miss the news than make a call it did not
        ask for.
        """
        return self._idle

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self, *, catch_up: bool = True) -> None:
        """Learn where the stream is, then follow it.

        catch_up decides what happens to whatever was missed while the program
        was not running. Fetching it is the right default for anything that acts
        on messages; skipping it suits a program that only cares about what
        happens from now on, and is much cheaper after a long absence.
        """
        if self._task is not None:
            raise SunnygramError("this update manager is already running")
        # Whatever the connection threw away before anyone was listening is not
        # a gap in what we have applied, so it starts level instead of as a
        # loss to recover from.
        self._lost = self._invoker.dropped_updates
        if not self.state.known:
            await self._fetch_state()
        elif catch_up:
            await self.catch_up()
        self._seen = time.monotonic()
        self._task = asyncio.create_task(self._drain(), name="sunnygram-updates")
        if self._idle > 0:
            self._watchdog = asyncio.create_task(
                self._watch(), name="sunnygram-updates-idle"
            )

    async def stop(self) -> None:
        """Stop following, and write down where we got to."""
        task, self._task = self._task, None
        watchdog, self._watchdog = self._watchdog, None
        for running in (task, watchdog):
            if running is not None:
                running.cancel()
                await asyncio.gather(running, return_exceptions=True)
        await self._invoker.peers.flush()
        await self._invoker.save()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.stop()

    async def feed(self, container: TLObject) -> None:
        """Take one thing the server sent and get every update out of it.

        Public because a call that changes something answers with updates of its
        own, and those count exactly as much as the ones that arrive on their
        own. Sending a message and then being told about it twice is the bug
        this prevents.
        """
        async with self._lock:
            await self._feed(container)

    async def catch_up(self) -> None:
        """Ask for everything that happened while we were not listening."""
        async with self._lock:
            await self._difference()

    async def _drain(self) -> None:
        """Take whatever the connection could not answer and feed it through."""
        try:
            while True:
                container = await self._invoker.updates.get()
                try:
                    async with self._lock:
                        await self._recover_losses()
                        await self._feed(container)
                except (SunnygramError, TimeoutError) as failure:
                    # Asking what we missed can be refused, time out, or arrive
                    # as something unexpected. Stopping here would end the stream
                    # for good, so the gap is left standing and the next update
                    # to notice it asks again. A bug of ours still gets out,
                    # because that is not something to keep running through.
                    self._failures += 1
                    # Said out loud because the gap it leaves is invisible: from
                    # the outside the program is simply missing a message.
                    _log.warning("could not catch up on updates: %s", failure)
        except asyncio.CancelledError:
            raise
        except Exception:
            # The counters are only worth anything written down, so whatever
            # went wrong, what was applied survives it.
            await self._invoker.save()
            raise

    async def _watch(self) -> None:
        """Ask what happened when nothing has arrived for a long time.

        Every other recovery in this layer starts from something the server
        said. This one starts from the server saying nothing, which is the one
        fault the counters cannot see: they only move when an update moves them,
        so a stream that has stopped entirely leaves them exactly where a quiet
        account would. Asking costs one call a quarter of an hour at worst.
        """
        while True:
            silence = self._idle - (time.monotonic() - self._seen)
            if silence > 0:
                await asyncio.sleep(silence)
                continue
            _log.info(
                "no updates for %.0f seconds, asking what was missed", self._idle
            )
            self._seen = time.monotonic()
            self._resyncs += 1
            try:
                async with self._lock:
                    await self._difference()
            except (SunnygramError, TimeoutError) as failure:
                # Same trade as _drain: the stream is worth more than this
                # attempt, so the next one tries again.
                self._failures += 1
                _log.warning("could not catch up after a silence: %s", failure)

    async def _recover_losses(self) -> None:
        """Catch up on whatever the connection had to throw away.

        The queue between the connection and here is bounded, and a reader that
        falls behind loses the newest rather than stalling the session. That is
        the right trade, but it does mean updates went missing, so the count is
        read before each one is fed and a difference makes up for them.

        Most of the time the counters would have found the same gap on their
        own, since a lost update leaves a hole in the pts. Not always: an update
        that carries no counter leaves no trace at all, and it is precisely
        those that nothing else would ever notice.
        """
        lost = self._invoker.dropped_updates
        if lost == self._lost:
            return
        _log.info(
            "%d updates were dropped before they reached here, catching up",
            lost - self._lost,
        )
        self._lost = lost
        self._resyncs += 1
        await self._difference()

    async def _feed(self, container: TLObject) -> None:
        # Anything at all arriving is proof the stream is still running, which
        # is what the watchdog above is waiting to be told.
        self._seen = time.monotonic()
        if isinstance(container, types.UpdatesTooLong):
            # The server has given up on telling us one at a time.
            await self._difference()
            return

        if isinstance(container, types.mtproto.NewSessionCreated):
            # The server started a session for us, which means it had lost the
            # one we were using: the usual reason is that the connection was
            # rebuilt. Updates are counted per session, so whatever happened
            # while we were away went to a session that no longer exists and is
            # not coming. Asking is the only way to find out what it was, and
            # not asking is how a program silently stops seeing messages after
            # its first dropped socket.
            _log.info("the server started a new session, catching up on updates")
            self._resyncs += 1
            await self._difference()
            return

        if isinstance(container, (types.Updates, types.UpdatesCombined)):
            users = _by_id(container.users)
            chats = _by_id(container.chats)
            self._learn(container.users, container.chats)
            await self._invoker.peers.flush(force=False)
            seq_start = getattr(container, "seq_start", container.seq)
            verdict = seq_verdict(self.state, seq_start, container.seq)
            if verdict is Verdict.OLD:
                return
            if verdict is Verdict.GAP:
                await self._difference()
                return
            for update, counter in _in_counter_order(container.updates):
                await self._one(update, users, chats, counter)
            # Only ever forwards: an update in the middle may have gone and
            # fetched a difference, which leaves these further along than the
            # container that started it.
            self.state.seq = max(self.state.seq, container.seq)
            self.state.date = max(self.state.date, container.date)
            return

        if isinstance(container, types.UpdateShort):
            await self._one(container.update, {}, {}, counter_of(container.update))
            self.state.date = max(self.state.date, container.date)
            return

        if isinstance(
            container,
            (
                types.UpdateShortMessage,
                types.UpdateShortChatMessage,
                types.UpdateShortSentMessage,
            ),
        ):
            # A message compact enough that the server skipped the container.
            await self._one(container, {}, {}, counter_of(container))
            self.state.date = max(self.state.date, container.date)
            return

        # Not an update container at all. Nothing above this asked for it, so it
        # is dropped instead of guessed at.

    async def _one(
        self,
        update: TLObject,
        users: dict[int, TLObject],
        chats: dict[int, TLObject],
        counter: Counter | None,
    ) -> None:
        """Judge one update against the counters, then deliver or recover.

        The counter is handed in rather than worked out here, because whoever
        put this container in order had to work it out already and deciding
        which counter an update moves is the expensive part of reading one.
        """
        if isinstance(update, types.UpdateChannelTooLong):
            # The server saying this channel moved on too far to be told about
            # one message at a time. The pts it carries is the channel's latest
            # on the server, which is where the gap ends instead of where it
            # starts, so it is a signal and never the cursor: asking from it
            # would be asking what changed since the newest thing there is, and
            # the empty answer to that would look exactly like having caught up.
            await self._channel_difference(update.channel_id, latest=update.pts or 0)
            return

        # Some updates keep no order at all. Someone coming online has no
        # history, so there is nothing to be out of step with.
        if counter is not None:
            verdict = judge(self.state, counter)
            if verdict is Verdict.OLD:
                return
            if verdict is Verdict.GAP:
                if counter.kind == "channel":
                    await self._channel_difference(counter.channel_id)
                else:
                    await self._difference()
                return
            apply(self.state, counter)

        if isinstance(update, _NOT_NEWS):
            return
        self._deliver(Event(update, users, chats))

    async def _fetch_state(self) -> None:
        """Ask where the stream is, for a session that has never been told."""
        current = await self._invoker.invoke(functions.updates.GetState())
        if not isinstance(current, types.updates.State):
            raise SunnygramError(f"expected a state, got {type(current).__name__}")
        self._adopt(current)
        await self._invoker.save()

    async def _difference(self) -> None:
        """Fetch everything between where we are and where the server is.

        Reentrancy is the trap: applying a difference delivers updates, and one
        of those can look like another gap. The flag makes the inner call a
        no-op, because the fetch already in flight is going to cover it.
        """
        if self._catching_up:
            return
        if not self.state.known:
            await self._fetch_state()
            return

        self._catching_up = True
        try:
            for _ in range(MAX_SLICES):
                difference = await self._invoker.invoke(
                    functions.updates.GetDifference(
                        pts=self.state.pts,
                        date=self.state.date,
                        qts=self.state.qts,
                    )
                )
                if isinstance(difference, types.updates.DifferenceEmpty):
                    self.state.date = difference.date
                    self.state.seq = difference.seq
                    break
                if isinstance(difference, types.updates.DifferenceTooLong):
                    # Too far behind to be told in detail. The counter is all we
                    # get; anything that matters has to be re-read as history.
                    self.state.pts = difference.pts
                    break
                if isinstance(difference, types.updates.Difference):
                    self._absorb(difference)
                    self._adopt(difference.state)
                    break
                if isinstance(difference, types.updates.DifferenceSlice):
                    self._absorb(difference)
                    self._adopt(difference.intermediate_state)
                    continue
                raise SunnygramError(
                    f"expected a difference, got {type(difference).__name__}"
                )
            else:
                # Ran out of slices with the server still not finished. The gap
                # is smaller than it was and is still there, so it is said out
                # loud rather than returned as if we had caught up (rule C3).
                self._failures += 1
                _log.warning(
                    "the difference was still arriving in slices after %d of "
                    "them, so the catch-up stopped short and some updates are "
                    "still missing",
                    MAX_SLICES,
                )
        finally:
            self._catching_up = False
        await self._invoker.save()

    async def _channel_difference(self, channel_id: int, *, latest: int = 0) -> None:
        """Fetch what one channel did while we were not following it.

        latest is what the server said this channel's own pts is, on the
        occasions it says so. That is where the gap ends, not where it starts,
        so it is only ever used by a channel we have never followed, which
        adopts it and has nothing to catch up on. A channel we have followed
        asks from its own mark, because that is the end of the gap that
        actually exists.
        """
        record = await self._invoker.peers.get(channel_id)
        if record is None or not record.kind.is_channel:
            # Nothing to name it with. Forgetting the counter means the next
            # update from it is adopted instead of read as a gap for ever.
            self.state.channels.pop(channel_id, None)
            return
        access_hash = record.access_hash

        known = self.state.channels.get(channel_id, 0)
        if known <= 0:
            # Never followed, so there is no gap: the server's own mark becomes
            # ours, instead of reading a whole history no one asked for.
            if latest > 0:
                self.state.channels[channel_id] = latest
            return

        peer = types.InputChannel(channel_id=channel_id, access_hash=access_hash)
        for _ in range(MAX_SLICES):
            try:
                difference = await self._invoker.invoke(
                    functions.updates.GetChannelDifference(
                        channel=peer,
                        filter=types.ChannelMessagesFilterEmpty(),
                        pts=known,
                        limit=self._channel_limit,
                    )
                )
            except (Flood, InternalError, Timeout):
                # A moment that will pass: a wait we have been given, or the
                # server having a bad time. The counter is still good, so it
                # stays, the gap stays standing, and the next update from this
                # channel asks again. Forgetting here is how a single FLOOD_WAIT
                # used to cost a channel its place in the stream permanently.
                raise
            except RPCError as refused:
                # Left the channel, never had the right to ask, or a counter the
                # server says is not a real one. Nothing about waiting will
                # change any of those, so the counter goes and the next update
                # from this channel is adopted, not read as a gap for
                # ever.
                _log.info(
                    "forgetting where we were in channel %d: %s", channel_id, refused
                )
                self.state.channels.pop(channel_id, None)
                return

            if isinstance(difference, types.updates.ChannelDifferenceEmpty):
                self.state.channels[channel_id] = difference.pts
                return
            if isinstance(difference, types.updates.ChannelDifferenceTooLong):
                # Moved on further than a difference can describe. Its dialog
                # says where it is now, and the messages it carries are history
                # instead of updates, so they are not delivered as events.
                self._learn(difference.users, difference.chats)
                self.state.channels[channel_id] = getattr(difference.dialog, "pts", 0) or 0
                return
            if isinstance(difference, types.updates.ChannelDifference):
                self._absorb_channel(difference)
                self.state.channels[channel_id] = difference.pts
                known = difference.pts
                if difference.final:
                    return
                continue
            raise SunnygramError(
                f"expected a channel difference, got {type(difference).__name__}"
            )
        else:
            # As above: the channel is further along than it was and is still
            # not caught up, and saying nothing here is how that stays invisible.
            self._failures += 1
            _log.warning(
                "channel %d was still sending differences after %d of them, so "
                "the catch-up stopped short at pts %d",
                channel_id,
                MAX_SLICES,
                known,
            )

    def _absorb(self, difference: Any) -> None:
        """Deliver everything a difference carried, without re-judging it.

        The server has already put these in order and said what state they leave
        us in, so running them past the counters again would only find gaps that
        are not there. The messages arrive bare and are wrapped so that whoever
        is reading events sees one kind of thing either way.
        """
        users = _by_id(difference.users)
        chats = _by_id(difference.chats)
        self._learn(difference.users, difference.chats)
        for message in difference.new_messages:
            self._deliver(
                Event(
                    types.UpdateNewMessage(message=message, pts=0, pts_count=0),
                    users,
                    chats,
                )
            )
        for message in difference.new_encrypted_messages:
            self._deliver(
                Event(
                    types.UpdateNewEncryptedMessage(message=message, qts=0),
                    users,
                    chats,
                )
            )
        for update in difference.other_updates:
            self._deliver(Event(update, users, chats))

    def _absorb_channel(self, difference: types.updates.ChannelDifference) -> None:
        users = _by_id(difference.users)
        chats = _by_id(difference.chats)
        self._learn(difference.users, difference.chats)
        for message in difference.new_messages:
            self._deliver(
                Event(
                    types.UpdateNewChannelMessage(message=message, pts=0, pts_count=0),
                    users,
                    chats,
                )
            )
        for update in difference.other_updates:
            self._deliver(Event(update, users, chats))

    def _learn(self, users: list[Any], chats: list[Any]) -> None:
        """Hand the people and chats an update mentioned to the peer cache.

        An update container carries these for the client's benefit and they are
        the main way a session comes to know anybody. Synchronous, because this
        is the path every update takes.
        """
        self._invoker.peers.learn(*users, *chats)

    def _adopt(self, state: Any) -> None:
        """Take the counters a server-sent state names."""
        self.state.pts = state.pts
        self.state.qts = state.qts
        self.state.date = state.date
        self.state.seq = state.seq

    def _deliver(self, event: Event) -> None:
        try:
            self._events.put_nowait(event)
        except asyncio.QueueFull:
            # Bounded, and nothing here ever blocks (rule P6). A program that
            # stops draining loses the newest instead of stalling the session.
            self._dropped += 1


def _by_id(objects: list[Any]) -> dict[int, TLObject]:
    """Users or chats, keyed by the id an update will refer to them by."""
    return {item.id: item for item in objects if hasattr(item, "id")}


def _in_counter_order(
    updates: Sequence[TLObject],
) -> list[tuple[TLObject, Counter | None]]:
    """One container's updates, in the order their counters say they happened.

    The server does not always put them that way. A read receipt advances no
    counter of its own, so it carries the pts it leaves behind and a count of
    zero, and it is routinely sent ahead of the message that actually got there
    first. Judged in that order the receipt lands short of its own pts and looks
    exactly like a gap, which costs a getDifference that finds nothing.

    So each update is keyed by where its counter started rather than where it
    ended, which is the one number that is the same for both of them and puts
    them back in the order they happened.

    Only ever within one counter. pts, qts and each channel count separately, so
    their values are not comparable and sorting the container as a whole would
    interleave streams by numeric coincidence. Instead each stream's updates are
    rearranged among the places they already occupy, which leaves every other
    update, counted or not, exactly where the server put it.

    The counter comes back alongside its update because working out which one an
    update moves is the expensive part of reading a container, several times the
    cost of the ordering itself, and doing it here and again in _one made the
    receive path measurably slower than not ordering at all.

    A container already in counter order is handed straight back, which is
    almost all of them: the scan that decides costs nothing over the pass that
    was needed anyway, and only a container that is really out of order pays for
    the permutation.
    """
    pairs: list[tuple[TLObject, Counter | None]] = []
    latest: dict[tuple[str, int], int] = {}
    behind = False
    for update in updates:
        counter = counter_of(update)
        pairs.append((update, counter))
        if counter is None:
            continue
        stream = (counter.kind, counter.channel_id)
        mark = counter.value - counter.count
        if mark < latest.get(stream, mark):
            behind = True
        latest[stream] = mark
    if not behind:
        return pairs

    marks: dict[int, int] = {}
    slots: dict[tuple[str, int], list[int]] = {}
    for index, (_, counter) in enumerate(pairs):
        if counter is None:
            continue
        marks[index] = counter.value - counter.count
        slots.setdefault((counter.kind, counter.channel_id), []).append(index)
    ordered = list(pairs)
    for where in slots.values():
        for slot, index in zip(where, sorted(where, key=marks.__getitem__)):
            ordered[slot] = pairs[index]
    return ordered