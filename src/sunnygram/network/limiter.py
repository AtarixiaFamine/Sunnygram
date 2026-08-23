# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Staying under Telegram's limits rather than finding them.

The connection already waits out a short FLOOD_WAIT and carries on, which is
what to do once it has happened. This is the other half of rule S4, which is not
hitting one in the first place.

The distinction matters more for a user account than it would for a bot. A bot
that floods gets throttled; an account that floods gets limited, and repeatedly
limited accounts get taken away. So the default here is on, and it is set below
where the trouble starts instead of at it.

Two buckets, because there are two different limits underneath. Telegram counts
calls of every kind against one budget, and counts messages into a single chat
against a much tighter one. A program pulling history from twenty chats is
nowhere near the second and can still trip the first; a program answering one
busy group is the other way round.

The numbers here are conservative on purpose. Telegram publishes limits for bots
and not for accounts, so these are set from what the published ones imply and
what clients settle on in practice, and they are arguments instead of
constants: a caller who knows better about their own account can say so, and one
who wants none of it can pass rate_limit=False and own the consequences.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from ..tl import TLObject

__all__ = ["RateLimiter", "TokenBucket"]

# Calls per second across everything, and how many may go at once after a quiet
# spell. Well under where an account starts collecting FLOOD_WAITs.
CALLS_PER_SECOND = 20.0
CALL_BURST = 20.0

# Messages per second into one chat, and the burst that goes with it. One a
# second is the rate Telegram documents for bots writing to a single chat, and
# an account has no reason to want more.
SENDS_PER_SECOND = 1.0
SEND_BURST = 3.0

# How long a per-destination bucket is kept after its last use. Long enough that
# a conversation keeps its bucket, short enough that a program touching many
# chats does not accumulate one per chat forever (rule P6).
IDLE_BUCKET = 300.0

# What counts as putting something into a chat rather than reading one. A list
# instead of a rule read off the schema: the schema says which calls carry a
# peer, and it does not say which of those the server counts as traffic, so
# guessing would either throttle history paging or miss half the sends.
SENDING = frozenset(
    {
        "functions.messages.SendMessage",
        "functions.messages.SendMedia",
        "functions.messages.SendMultiMedia",
        "functions.messages.SendInlineBotResult",
        "functions.messages.ForwardMessages",
        "functions.messages.SendScheduledMessages",
        "functions.messages.SendReaction",
        "functions.messages.EditMessage",
        "functions.messages.SetTyping",
    }
)


class TokenBucket:
    """A rate, a burst, and somewhere to wait.

    Tokens accrue at a fixed rate up to a ceiling, and a call spends one. A
    bucket that is full is a program that has been quiet, and it is allowed to
    catch up all at once, which the burst is for.
    """

    __slots__ = ("_rate", "_burst", "_tokens", "_stamp", "_lock")

    def __init__(self, rate: float, burst: float) -> None:
        if rate <= 0:
            raise ValueError("a rate limit has to be a positive number of calls")
        self._rate = rate
        self._burst = max(burst, 1.0)
        self._tokens = self._burst
        self._stamp = time.monotonic()
        # Handing out a token and charging for it is two steps, and without
        # this two callers arriving together would both be given the last one.
        self._lock = asyncio.Lock()

    @property
    def tokens(self) -> float:
        """Roughly how many calls could go right now, for a diagnostic."""
        return min(self._burst, self._tokens + self._earned())

    def _earned(self) -> float:
        return (time.monotonic() - self._stamp) * self._rate

    async def take(self) -> float:
        """Wait until a call may go, and say how long that took.

        The wait happens holding the lock, so callers go through in the order
        they arrived instead of racing each time a token appears.
        """
        async with self._lock:
            now = time.monotonic()
            self._tokens = min(self._burst, self._tokens + (now - self._stamp) * self._rate)
            self._stamp = now
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return 0.0

            delay = (1.0 - self._tokens) / self._rate
            await asyncio.sleep(delay)
            self._tokens = 0.0
            self._stamp = time.monotonic()
            return delay


class RateLimiter:
    """The pacing an account gets unless it asks for something else.

    One bucket for every call, and one per chat for the calls that put
    something into a chat. A call waits on whichever of the two is behind.
    """

    __slots__ = ("_all", "_rate", "_burst", "_idle", "_per_peer", "_seen", "_waited")

    def __init__(
        self,
        *,
        calls_per_second: float = CALLS_PER_SECOND,
        call_burst: float = CALL_BURST,
        sends_per_second: float = SENDS_PER_SECOND,
        send_burst: float = SEND_BURST,
        idle_bucket: float = IDLE_BUCKET,
    ) -> None:
        self._all = TokenBucket(calls_per_second, call_burst)
        self._rate = sends_per_second
        self._burst = send_burst
        self._idle = idle_bucket
        self._per_peer: dict[int, TokenBucket] = {}
        self._seen: dict[int, float] = {}
        self._waited = 0.0

    def __repr__(self) -> str:
        return (
            f"RateLimiter({self._all.tokens:.1f} calls in hand, "
            f"{len(self._per_peer)} chats, {self._waited:.1f}s waited)"
        )

    @property
    def waited(self) -> float:
        """Seconds this limiter has held calls back, over its whole life.

        Worth looking at. A number that keeps climbing means the program wants
        to go faster than the account safely can, and the answer is usually to
        do less rather than to raise the limit.
        """
        return self._waited

    async def hold(self, request: TLObject, *, bulk: bool = False) -> None:
        """Wait until this call may go out.

        A transfer goes straight through. Telegram meters a file by the bytes
        on a connection instead of by the calls made, which is the whole reason
        the file engine spreads parts across several, and pacing those here
        would undo that without making the account any safer. They stay bounded
        by the pool and the in-flight cap instead (rule P6).
        """
        if bulk:
            return
        self._waited += await self._all.take()
        peer = _destination(request)
        if peer is not None:
            self._waited += await self._bucket(peer).take()

    def _bucket(self, peer: int) -> TokenBucket:
        now = time.monotonic()
        self._seen[peer] = now
        found = self._per_peer.get(peer)
        if found is None:
            found = self._per_peer[peer] = TokenBucket(self._rate, self._burst)
            self._forget(now)
        return found

    def _forget(self, now: float) -> None:
        """Drop the buckets for chats nothing has spoken to in a while."""
        stale = [
            peer for peer, last in self._seen.items() if now - last > self._idle
        ]
        for peer in stale:
            self._per_peer.pop(peer, None)
            self._seen.pop(peer, None)


def _destination(request: TLObject) -> int | None:
    """Which chat this call writes to, if it writes to one.

    The id is only ever compared against itself, so the access hash is left out
    and a peer named two ways lands in the same bucket, which is what a chat
    having one rate limit means.
    """
    if request.QUALNAME not in SENDING:
        return None
    peer = getattr(request, "to_peer", None) or getattr(request, "peer", None)
    return _peer_id(peer)


def _peer_id(peer: Any) -> int | None:
    for field in ("user_id", "chat_id", "channel_id"):
        found = getattr(peer, field, None)
        if isinstance(found, int):
            return found
    # InputPeerSelf and the rest name no one in particular, and the saved
    # messages chat is not rate limited the way a conversation is.
    return None
