"""Stars beyond paying with them: subscriptions, revenue, referrals.

What is worth testing here is not that a call goes out, which is the same
sentence in every method. It is the four places where this surface can be got
wrong quietly: cancelling from the wrong end, an order-by that is a pair of
booleans rather than a word, a withdrawal that must prove a password rather
than send one, and the flag that decides which of two currencies a call is
about.
"""

from __future__ import annotations

import pytest

from mtproto_server import recording
from sunnygram.methods import (
    cancel_bot_subscription,
    cancel_stars_subscription,
    connect_referral_bot,
    fulfill_stars_subscription,
    referral_bots,
    resume_stars_subscription,
    revoke_referral_link,
    stars_ads_url,
    stars_revenue_stats,
    stars_subscriptions,
    stars_topup_options,
    stars_transactions_by_id,
    stars_withdrawal_url,
    suggested_referral_bots,
)
from sunnygram.raw import functions, types

ME = types.InputPeerSelf()


def _status():
    return types.payments.StarsStatus(
        balance=types.StarsAmount(amount=0, nanos=0), chats=[], users=[]
    )


class TestSubscriptions:
    async def test_the_subscriber_cancels_by_setting_the_flag(self):
        async with recording() as (invoker, server):
            await cancel_stars_subscription(invoker, "sub-1", ME)
            asked = server.only(functions.payments.ChangeStarsSubscription)
            assert asked.subscription_id == "sub-1"
            assert asked.canceled is True

    async def test_resuming_is_the_same_call_the_other_way_round(self):
        async with recording() as (invoker, server):
            await resume_stars_subscription(invoker, "sub-1", ME)
            assert server.only(functions.payments.ChangeStarsSubscription).canceled is (
                False
            )

    async def test_a_bot_cancels_by_charge_not_by_subscription(self):
        # The two ends really are different calls, and mixing them up is the
        # mistake this pair of names exists to prevent.
        async with recording() as (invoker, server):
            await cancel_bot_subscription(invoker, ME, "charge-9")
            asked = server.only(functions.payments.BotCancelStarsSubscription)
            assert asked.charge_id == "charge-9"
            assert asked.restore is False

    async def test_a_bot_can_put_one_back(self):
        async with recording() as (invoker, server):
            await cancel_bot_subscription(invoker, ME, "charge-9", restore=True)
            assert server.only(
                functions.payments.BotCancelStarsSubscription
            ).restore is True

    async def test_unpaid_only_is_the_missing_balance_flag(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: _status()
            await stars_subscriptions(invoker, ME, unpaid_only=True, offset="cur")
            asked = server.only(functions.payments.GetStarsSubscriptions)
            assert asked.missing_balance is True
            assert asked.offset == "cur"

    async def test_fulfilling_names_the_subscription(self):
        async with recording() as (invoker, server):
            await fulfill_stars_subscription(invoker, "sub-2", ME)
            assert server.only(
                functions.payments.FulfillStarsSubscription
            ).subscription_id == "sub-2"


class TestRevenue:
    async def test_a_withdrawal_proves_the_password_and_never_sends_it(self):
        async with recording() as (invoker, server):
            def answer(query):
                if isinstance(query, functions.account.GetPassword):
                    # No second factor, so the proof is the empty one. The point
                    # of the test is which object reaches the wire, not SRP.
                    return types.account.Password(
                        new_algo=types.PasswordKdfAlgoUnknown(),
                        new_secure_algo=types.SecurePasswordKdfAlgoUnknown(),
                        secure_random=b"\x00" * 32,
                    )
                return types.payments.StarsRevenueWithdrawalUrl(url="https://t.me/$w")

            server.answer_with = answer
            url = await stars_withdrawal_url(invoker, "hunter2", ME, amount=50)
            assert url == "https://t.me/$w"
            asked = server.only(functions.payments.GetStarsRevenueWithdrawalUrl)
            assert asked.amount == 50
            assert isinstance(asked.password, types.InputCheckPasswordEmpty)
            # The password itself must appear nowhere on the wire.
            assert all(
                "hunter2" not in repr(query) for query in server.queries
            ), "the password reached the server"

    async def test_ton_is_a_flag_on_the_same_calls(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.payments.StarsRevenueStats(
                top_hours_graph=types.StatsGraphError(error="none"),
                revenue_graph=types.StatsGraphError(error="none"),
                status=types.StarsRevenueStatus(
                    current_balance=types.StarsAmount(amount=0, nanos=0),
                    available_balance=types.StarsAmount(amount=0, nanos=0),
                    overall_revenue=types.StarsAmount(amount=0, nanos=0),
                ),
                usd_rate=1.0,
            )
            await stars_revenue_stats(invoker, ME, ton=True, dark=True)
            asked = server.only(functions.payments.GetStarsRevenueStats)
            assert asked.ton is True
            assert asked.dark is True

    async def test_the_ads_url_comes_back_as_a_string(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.StarsRevenueAdsAccountUrl(
                url="https://ads.telegram.org/x"
            )
            assert await stars_ads_url(invoker, ME) == "https://ads.telegram.org/x"

    async def test_looking_up_entries_wraps_each_id(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: _status()
            await stars_transactions_by_id(invoker, ["a", "b"], ME)
            asked = server.only(functions.payments.GetStarsTransactionsByID)
            assert [one.id for one in asked.id] == ["a", "b"]
            assert all(
                isinstance(one, types.InputStarsTransaction) for one in asked.id
            )


class TestReferrals:
    @pytest.mark.parametrize(
        "word, revenue, date",
        [("revenue", True, False), ("date", False, True), ("default", False, False)],
    )
    async def test_the_order_is_a_word_not_two_booleans(self, word, revenue, date):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.SuggestedStarRefBots(
                count=0, suggested_bots=[], users=[], next_offset=None
            )
            await suggested_referral_bots(invoker, ME, by=word)
            asked = server.only(functions.payments.GetSuggestedStarRefBots)
            assert asked.order_by_revenue is revenue
            assert asked.order_by_date is date

    async def test_an_order_that_is_not_one_is_refused_before_the_round_trip(self):
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="revenue"):
                await suggested_referral_bots(invoker, ME, by="profit")
            assert server.queries == []

    async def test_paging_carries_both_halves_of_the_cursor(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.ConnectedStarRefBots(
                count=0, connected_bots=[], users=[]
            )
            await referral_bots(invoker, ME, before=1700000000, before_link="l", limit=5)
            asked = server.only(functions.payments.GetConnectedStarRefBots)
            assert asked.offset_date == 1700000000
            assert asked.offset_link == "l"
            assert asked.limit == 5

    async def test_joining_and_revoking_are_different_calls(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.ConnectedStarRefBots(
                count=0, connected_bots=[], users=[]
            )
            await connect_referral_bot(invoker, ME, ME)
            assert server.only(functions.payments.ConnectStarRefBot) is not None
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.ConnectedStarRefBots(
                count=0, connected_bots=[], users=[]
            )
            await revoke_referral_link(invoker, "https://t.me/bot?start=ref", ME)
            asked = server.only(functions.payments.EditConnectedStarRefBot)
            assert asked.revoked is True
            assert asked.link == "https://t.me/bot?start=ref"


class TestOptions:
    async def test_topup_options_take_no_arguments(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: []
            await stars_topup_options(invoker)
            assert server.only(functions.payments.GetStarsTopupOptions) is not None
