# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The rules for reading the stream of updates in order.

Telegram does not send updates and hope. Every update that changes something
carries a counter and how much it advanced it, so a client can tell the
difference between the next update and an update that arrived after one it never
saw. That is the whole idea: the counter is a promise that nothing is missing,
and a break in it is a question the server has to answer.

There are three counters. pts covers messages and most of what happens to them.
qts covers secret chats and a few bot events. seq numbers the containers
themselves. Channels are not in the common pts at all: each one counts on its
own, because a person in five hundred channels would otherwise have five hundred
sources of gaps in one number.

This module is only the arithmetic, kept apart from the machinery that acts on
it so the rules can be read and tested without a connection in sight.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from ..raw import types
from ..storage import UpdateState

__all__ = ["Verdict", "channel_of", "counter_of", "judge", "seq_verdict"]

_log = logging.getLogger(__name__)


class Verdict(Enum):
    """What to do with an update that has just arrived."""

    APPLY = "apply"
    # Already accounted for. The server resends when it is not sure we heard.
    OLD = "old"
    # Something between what we have and this one never arrived.
    GAP = "gap"


@dataclass(frozen=True, slots=True)
class Counter:
    """The counter one update moves, and by how much."""

    kind: str
    value: int
    count: int
    channel_id: int = 0


# Updates that move the common pts. Everything here carries pts and pts_count,
# and the schema is the authority: this list is the set of constructors with
# both, minus the channel ones, which count separately.
_COMMON_PTS = (
    types.UpdateNewMessage,
    types.UpdateDeleteMessages,
    types.UpdateReadHistoryInbox,
    types.UpdateReadHistoryOutbox,
    types.UpdateWebPage,
    types.UpdateReadMessagesContents,
    types.UpdateEditMessage,
    types.UpdatePinnedMessages,
    types.UpdateFolderPeers,
)

_CHANNEL_PTS = (
    types.UpdateNewChannelMessage,
    types.UpdateEditChannelMessage,
    types.UpdateDeleteChannelMessages,
    types.UpdateChannelWebPage,
    types.UpdatePinnedChannelMessages,
)

def _qts_of(update: object) -> int | None:
    """The qts an update carries, if it carries one.

    Read off the object rather than matched against a list of constructors,
    which is the opposite of how pts is decided above and is deliberate. pts
    needs a list because it has to be split three ways: the common stream, the
    per-channel ones, and the compact forms the server sends with no container
    around them. qts has no such split. Every constructor in the schema with a
    qts field is a qts-counted update, so the field is the better authority and
    the only one that cannot fall behind the schema.

    It had fallen behind. The list this replaces named one constructor and the
    pinned layer has seventeen, all but the first of them added to the protocol
    after secret chats were. The sixteen that were missing were not delivered
    wrongly, which is the part that made this survivable and invisible: they
    were delivered, and then delivered again. Nothing moved the counter, so the
    next getDifference asked from a mark the account had long since passed and
    the server duly resent everything after it. A moderation handler banned
    twice, a join request was approved twice, and a vote was counted twice, once
    per reconnect.
    """
    qts = getattr(update, "qts", None)
    return qts if isinstance(qts, int) else None


def channel_of(update: object) -> int:
    """Which channel an update belongs to, or zero for the common stream."""
    if isinstance(update, _CHANNEL_PTS):
        return _channel_id(update)
    if isinstance(update, types.UpdateChannelTooLong):
        channel_id: int = update.channel_id
        return channel_id
    return 0


def counter_of(update: object) -> Counter | None:
    """The counter this update moves, if it moves one.

    Most updates do not. A user going online changes nothing that has to be
    replayed in order, so it carries no counter and is simply delivered.
    """
    if isinstance(update, _CHANNEL_PTS):
        channel_id = _channel_id(update)
        if channel_id == 0:
            # A channel update that does not say which channel. Nothing in the
            # schema produces this, so it means the server sent something
            # malformed or a later layer moved the field. Counting it would
            # write a mark under the id zero, which belongs to no channel, and
            # then keep it: a junk entry that persists to storage and is
            # compared against for the life of the session. Better to hand it
            # over uncounted, which costs the ordering of one update rather
            # than the state of a channel that does not exist.
            _log.warning(
                "a %s arrived without a channel to belong to, so it is "
                "delivered without moving any counter",
                type(update).__name__,
            )
            return None
        return Counter("channel", update.pts, update.pts_count, channel_id=channel_id)
    if isinstance(update, _COMMON_PTS):
        return Counter("pts", update.pts, update.pts_count)
    qts = _qts_of(update)
    if qts is not None:
        # qts counts one at a time, and the schema gives no count field for it.
        return Counter("qts", qts, 1)
    if isinstance(update, (types.UpdateShortMessage, types.UpdateShortChatMessage)):
        return Counter("pts", update.pts, update.pts_count)
    if isinstance(update, types.UpdateShortSentMessage):
        return Counter("pts", update.pts, update.pts_count)
    return None


def judge(state: UpdateState, counter: Counter) -> Verdict:
    """Decide whether an update is next, already seen, or past a gap.

    The rule is the same for all three counters. Where we are plus how much this
    update advances things should land exactly on the value it carries. Landing
    past it means we have already applied it. Landing short means something in
    between never arrived.
    """
    local = _local(state, counter)
    if local == 0:
        # Nothing to be out of step with yet: the first value seen sets the mark.
        return Verdict.APPLY
    if local + counter.count == counter.value:
        return Verdict.APPLY
    if local + counter.count > counter.value:
        return Verdict.OLD
    return Verdict.GAP


def apply(state: UpdateState, counter: Counter) -> None:
    """Move the counter this update belongs to, having decided to apply it."""
    if counter.kind == "pts":
        state.pts = counter.value
    elif counter.kind == "qts":
        state.qts = counter.value
    else:
        state.channels[counter.channel_id] = counter.value


def seq_verdict(state: UpdateState, seq_start: int, seq: int) -> Verdict:
    """Decide the same question for a container, which is numbered as a whole.

    A seq of zero means the container is not part of the sequence at all, which
    the server uses for things that carry no ordering of their own.
    """
    if seq == 0:
        return Verdict.APPLY
    if state.seq == 0 or seq_start == state.seq + 1:
        return Verdict.APPLY
    if seq_start <= state.seq:
        return Verdict.OLD
    return Verdict.GAP


def _local(state: UpdateState, counter: Counter) -> int:
    if counter.kind == "pts":
        return state.pts
    if counter.kind == "qts":
        return state.qts
    return state.channels.get(counter.channel_id, 0)


def _channel_id(update: object) -> int:
    """Which channel an update is about.

    Some say so directly. The ones that carry a message say it through the
    message's peer instead, which is the only place the schema puts it there.
    """
    named = getattr(update, "channel_id", None)
    if isinstance(named, int):
        return named
    message = getattr(update, "message", None)
    if isinstance(message, (types.Message, types.MessageService)):
        peer = message.peer_id
        if isinstance(peer, types.PeerChannel):
            channel: int = peer.channel_id
            return channel
    return 0
