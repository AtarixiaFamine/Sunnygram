"""Pacing calls so the account never finds the limit.

Everything here uses rates fast enough that the tests are quick and slow enough
that the waits are measurable. Real time rather than a fake clock, because the
bucket refills against the monotonic clock and faking that would be testing the
fake.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from sunnygram.network.limiter import RateLimiter, TokenBucket
from sunnygram.raw import functions, types

PEER = types.InputPeerUser(user_id=42, access_hash=7)
OTHER = types.InputPeerUser(user_id=99, access_hash=7)


def send_to(peer: types.InputPeerUser) -> functions.messages.SendMessage:
    return functions.messages.SendMessage(peer=peer, message="hi", random_id=1)


class TestTokenBucket:
    async def test_a_full_bucket_lets_the_burst_straight_through(self):
        bucket = TokenBucket(rate=10, burst=5)
        started = time.monotonic()
        for _ in range(5):
            assert await bucket.take() == 0.0
        assert time.monotonic() - started < 0.05

    async def test_the_call_after_the_burst_waits(self):
        bucket = TokenBucket(rate=20, burst=2)
        await bucket.take()
        await bucket.take()
        waited = await bucket.take()
        assert waited > 0

    async def test_waiting_is_roughly_the_rate(self):
        bucket = TokenBucket(rate=20, burst=1)
        await bucket.take()
        started = time.monotonic()
        await bucket.take()
        # One call at twenty a second is fifty milliseconds, with room for a
        # slow machine on either side.
        assert 0.02 < time.monotonic() - started < 0.5

    async def test_tokens_come_back_over_time(self):
        bucket = TokenBucket(rate=100, burst=2)
        await bucket.take()
        await bucket.take()
        await asyncio.sleep(0.1)
        assert await bucket.take() == 0.0

    async def test_the_ceiling_holds(self):
        # A long quiet spell does not bank an unlimited burst.
        bucket = TokenBucket(rate=1000, burst=3)
        await asyncio.sleep(0.05)
        assert bucket.tokens <= 3

    async def test_callers_arriving_together_do_not_share_a_token(self):
        bucket = TokenBucket(rate=50, burst=1)
        waits = await asyncio.gather(*(bucket.take() for _ in range(4)))
        # One goes free and the other three each wait longer than the last.
        assert sorted(waits)[0] == 0.0
        assert sum(1 for wait in waits if wait > 0) == 3

    def test_a_rate_of_zero_is_refused(self):
        with pytest.raises(ValueError, match="positive"):
            TokenBucket(rate=0, burst=1)


class TestRateLimiter:
    async def test_reads_only_pay_the_general_bucket(self):
        limiter = RateLimiter(calls_per_second=1000, call_burst=1000, sends_per_second=1)
        for _ in range(20):
            await limiter.hold(functions.messages.GetHistory(
                peer=PEER, offset_id=0, offset_date=0, add_offset=0,
                limit=1, max_id=0, min_id=0, hash=0,
            ))
        assert limiter.waited == 0.0

    async def test_sending_to_one_chat_is_paced(self):
        limiter = RateLimiter(
            calls_per_second=1000, call_burst=1000, sends_per_second=20, send_burst=1
        )
        await limiter.hold(send_to(PEER))
        await limiter.hold(send_to(PEER))
        assert limiter.waited > 0

    async def test_two_chats_do_not_pace_each_other(self):
        limiter = RateLimiter(
            calls_per_second=1000, call_burst=1000, sends_per_second=1, send_burst=1
        )
        await limiter.hold(send_to(PEER))
        await limiter.hold(send_to(OTHER))
        assert limiter.waited == 0.0

    async def test_a_chat_named_two_ways_is_one_chat(self):
        limiter = RateLimiter(
            calls_per_second=1000, call_burst=1000, sends_per_second=20, send_burst=1
        )
        await limiter.hold(send_to(PEER))
        # Same person, different access hash, which happens whenever the peer
        # came from a different answer.
        await limiter.hold(send_to(types.InputPeerUser(user_id=42, access_hash=123)))
        assert limiter.waited > 0

    async def test_the_general_bucket_covers_everything(self):
        limiter = RateLimiter(calls_per_second=20, call_burst=1)
        await limiter.hold(functions.help.GetConfig())
        await limiter.hold(functions.help.GetConfig())
        assert limiter.waited > 0

    async def test_a_transfer_goes_straight_through(self):
        limiter = RateLimiter(calls_per_second=1, call_burst=1)
        for _ in range(50):
            await limiter.hold(
                functions.upload.GetFile(
                    location=types.InputFileLocation(
                        volume_id=1, local_id=1, secret=1, file_reference=b""
                    ),
                    offset=0,
                    limit=4096,
                ),
                bulk=True,
            )
        assert limiter.waited == 0.0

    async def test_forwarding_is_paced_by_where_it_lands(self):
        limiter = RateLimiter(
            calls_per_second=1000, call_burst=1000, sends_per_second=20, send_burst=1
        )
        forward = functions.messages.ForwardMessages(
            from_peer=OTHER, id=[1], random_id=[1], to_peer=PEER
        )
        await limiter.hold(forward)
        await limiter.hold(send_to(PEER))
        assert limiter.waited > 0

    async def test_idle_chats_are_forgotten(self):
        limiter = RateLimiter(
            calls_per_second=1000, call_burst=1000, sends_per_second=1000, idle_bucket=0
        )
        await limiter.hold(send_to(PEER))
        await limiter.hold(send_to(OTHER))
        # The bucket for the first chat goes when the second arrives and finds
        # it stale, so nothing accumulates over a long run (rule P6).
        assert repr(limiter).count("1 chats") == 1

    def test_it_says_what_it_is_doing(self):
        assert "calls in hand" in repr(RateLimiter())


class TestThroughTheInvoker:
    async def test_on_by_default(self):
        from sunnygram.network.invoker import _limiter_for

        assert isinstance(_limiter_for(True), RateLimiter)

    def test_the_invoker_hands_it_back(self):
        from sunnygram.network import ClientInfo, Invoker
        from sunnygram.storage import MemoryStorage

        client = ClientInfo(api_id=1, api_hash="0" * 32)
        assert Invoker(MemoryStorage(), client=client).limiter is not None
        assert (
            Invoker(MemoryStorage(), client=client, rate_limit=False).limiter is None
        )

    def test_it_can_be_turned_off(self):
        from sunnygram.network.invoker import _limiter_for

        assert _limiter_for(False) is None

    def test_a_caller_can_bring_their_own(self):
        from sunnygram.network.invoker import _limiter_for

        mine = RateLimiter(calls_per_second=3)
        assert _limiter_for(mine) is mine
