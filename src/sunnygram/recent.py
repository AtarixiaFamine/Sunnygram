# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The messages this client has lately seen or sent.

There is one question this exists to answer without a round trip: what message
is this one a reply to. The protocol does not carry the answer. A reply says
which id it answers and stops there, so a program that wants the message itself
asks for it, and a bot whose whole job is answering replies pays a call for
every one.

Nearly always it need not. The message being replied to went past this client a
moment ago, either because it arrived as an update or because this client sent
it, and holding onto the last thousand of those turns that call into a dict
lookup. What is left over is the case the cache genuinely cannot cover, an old
message someone scrolled up to, and that still costs a call.

Bounded and least-recently-used, like every other cache here (rule P6). It is a
convenience rather than a source of truth: a miss is not an error, it is one
round trip.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Message

__all__ = ["CAPACITY", "RecentMessages"]

# How many to keep. A message is a handful of fields plus the raw constructor
# it was made from, so a thousand of them is small, and the hit rate past that
# falls off quickly: a reply is nearly always to something recent.
CAPACITY = 1000


class RecentMessages:
    """A bounded, least-recently-used record of messages, by chat and id."""

    __slots__ = ("_held", "_limit", "_hits", "_misses")

    def __init__(self, limit: int = CAPACITY) -> None:
        self._held: OrderedDict[tuple[int, int], Message] = OrderedDict()
        self._limit = limit
        self._hits = 0
        self._misses = 0

    def __len__(self) -> int:
        return len(self._held)

    def __repr__(self) -> str:
        return (
            f"RecentMessages({len(self._held)}/{self._limit} held, "
            f"{self._hits} hits, {self._misses} misses)"
        )

    @property
    def hits(self) -> int:
        """Replies answered from here instead of from the network."""
        return self._hits

    @property
    def misses(self) -> int:
        """Times the message asked for was not held."""
        return self._misses

    def remember(self, message: Message) -> None:
        """Hold onto a message, evicting the least recently used if full.

        A message that does not say which chat it is in is skipped instead of
        stored under a guess: without one there is no key that a later lookup
        could use. The id is enough, so a message that arrived with no chat
        object alongside it is still held.
        """
        chat = message.chat_id
        if self._limit <= 0 or chat is None:
            return
        key = (chat, message.id)
        self._held[key] = message
        self._held.move_to_end(key)
        while len(self._held) > self._limit:
            self._held.popitem(last=False)

    def get(self, chat_id: int, message_id: int) -> Message | None:
        """The message, if it is still held."""
        found = self._held.get((chat_id, message_id))
        if found is None:
            self._misses += 1
            return None
        self._hits += 1
        self._held.move_to_end((chat_id, message_id))
        return found

    def forget(self, chat_id: int, message_id: int) -> None:
        """Drop one, for a message that is known to be gone."""
        self._held.pop((chat_id, message_id), None)

    def clear(self) -> None:
        """Let go of everything."""
        self._held.clear()
