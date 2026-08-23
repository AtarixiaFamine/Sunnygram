# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A reaction being put on a message, or taken off one.

This is one kind of event and two entirely different readings of it, and the
difference is which side is listening. A user account is told the running
totals: this message now has four thumbs up and one heart. A bot is told about
one person: this account had a thumb up on that message and now has a heart.

Neither is a summary of the other. The totals never say who, and the per-person
reading never says how many. So this wrapper carries both shapes and says which
one it was given instead of filling in the other half with guesses, and a
program that wants one and gets the other finds out by asking instead of by
reading zeros.

A reaction is named the way the rest of the library names one: an ordinary
emoji is the character, a custom emoji is the document id it was uploaded as.
Telegram's third kind, the paid one, carries nothing at all to name it by, so it
is the word "paid" here. That is a made up name and it is deliberately not an
emoji, since inventing a star would put it in the same namespace as the star
someone actually sent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..peers import mark_peer
from ..raw import types

if TYPE_CHECKING:
    from ..client import Client
    from .message import Message

__all__ = ["PAID", "ReactionUpdate"]

# What a paid reaction is called here. It carries nothing to name it by, and an
# emoji would collide with the one someone could have sent for real.
PAID = "paid"


@dataclass(slots=True)
class ReactionUpdate:
    """Reactions on one message changing, in whichever way we were told."""

    chat_id: int
    message_id: int
    reading: str = "totals"
    date: int = 0
    actor_id: int = 0
    before: tuple[str | int, ...] = ()
    after: tuple[str | int, ...] = ()
    counts: dict[str | int, int] = field(default_factory=dict)
    mine: tuple[str | int, ...] = ()
    topic_id: int = 0
    raw: Any = None
    client: Any = None

    def __repr__(self) -> str:
        if self.by_person:
            return (
                f"ReactionUpdate({self.actor_id} on {self.message_id}: "
                f"{list(self.before)} -> {list(self.after)})"
            )
        return f"ReactionUpdate({self.message_id}: {self.counts})"

    @property
    def by_person(self) -> bool:
        """Whether this reading is one person's reactions, not totals.

        The one question worth asking before reading anything else. A bot gets
        this reading and a user account gets the other, and which one arrived
        decides whether actor_id and the before and after pair mean anything.
        """
        return self.reading == "person"

    @property
    def added(self) -> tuple[str | int, ...]:
        """What this person just put on the message.

        Empty on the totals reading, because it cannot be worked out from
        totals: two people swapping reactions leaves every number the same.
        """
        return tuple(one for one in self.after if one not in self.before)

    @property
    def removed(self) -> tuple[str | int, ...]:
        """What this person just took off the message."""
        return tuple(one for one in self.before if one not in self.after)

    @property
    def total(self) -> int:
        """How many reactions the message carries, over every kind."""
        return sum(self.counts.values())

    async def get_message(self) -> Message:
        """Fetch the message these reactions are on. Costs a call."""
        found = await self._acting().get_messages(self.chat_id, [self.message_id])
        if not found:
            raise SunnygramError(
                f"message {self.message_id} is not there any more, so the "
                "reaction was on something that has since been deleted"
            )
        return found[0]

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this reaction update is not bound to a client, so it cannot "
                "act on its own"
            )
        client: Client = self.client
        return client

    @classmethod
    def from_raw(cls, update: Any, *, client: Any = None) -> ReactionUpdate | None:
        """Wrap whichever of the three updates that say this arrived."""
        if isinstance(update, types.UpdateMessageReactions):
            counts, mine = _totals(getattr(update.reactions, "results", []))
            return cls(
                chat_id=mark_peer(update.peer) or 0,
                message_id=update.msg_id,
                reading="totals",
                counts=counts,
                mine=mine,
                topic_id=update.top_msg_id or 0,
                raw=update,
                client=client,
            )
        if isinstance(update, types.UpdateBotMessageReactions):
            counts, mine = _totals(update.reactions)
            return cls(
                chat_id=mark_peer(update.peer) or 0,
                message_id=update.msg_id,
                reading="totals",
                date=update.date,
                counts=counts,
                mine=mine,
                raw=update,
                client=client,
            )
        if isinstance(update, types.UpdateBotMessageReaction):
            return cls(
                chat_id=mark_peer(update.peer) or 0,
                message_id=update.msg_id,
                reading="person",
                date=update.date,
                actor_id=mark_peer(update.actor) or 0,
                before=tuple(_named(one) for one in update.old_reactions),
                after=tuple(_named(one) for one in update.new_reactions),
                raw=update,
                client=client,
            )
        return None


def _totals(
    results: list[Any],
) -> tuple[dict[str | int, int], tuple[str | int, ...]]:
    """The counts, and which of them this account is one of.

    chosen_order is how Telegram says "you reacted with this one", and it is an
    order instead of a flag because a premium account may react several times
    and the order is what the clients draw.
    """
    counts: dict[str | int, int] = {}
    chosen: list[tuple[int, str | int]] = []
    for one in results:
        name = _named(one.reaction)
        counts[name] = counts.get(name, 0) + one.count
        if one.chosen_order is not None:
            chosen.append((one.chosen_order, name))
    return counts, tuple(name for _, name in sorted(chosen))


def _named(reaction: Any) -> str | int:
    """One reaction, as the caller writes one: an emoji or a document id."""
    if isinstance(reaction, types.ReactionEmoji):
        return reaction.emoticon
    if isinstance(reaction, types.ReactionCustomEmoji):
        return reaction.document_id
    if isinstance(reaction, types.ReactionPaid):
        return PAID
    return ""
