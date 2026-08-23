"""Money.

The rule this file is really about: a pre-checkout query has roughly ten
seconds to be answered, and an unanswered one is a customer whose payment fails
with nothing said to the bot. So the answer path is the one place in this
library where an exception is logged rather than passed over quietly, and where
a rejection without a reason is refused before it is sent, because the reason is
what the customer is shown.

The rest is arithmetic and shapes: amounts are in the currency's smallest unit,
Stars have no smaller unit, and the two invoice kinds differ in enough places
that building one when you meant the other should not be possible by accident.
"""

from __future__ import annotations

import logging

import pytest

from mtproto_server import recording
from sunnygram.methods import (
    STARS,
    answer_pre_checkout,
    answer_shipping,
    as_invoice,
    as_stars_invoice,
    refund_stars,
    shipping_option,
    stars_balance,
    stars_transactions,
)
from sunnygram.raw import functions, types
from sunnygram.types import PreCheckoutQuery, Price, ShippingQuery, SuccessfulPayment


class TestBuildingAnInvoice:
    def test_a_currency_invoice_carries_its_provider(self):
        built = as_invoice(
            "A thing",
            "It is a thing",
            currency="EUR",
            prices=[Price("The thing", 1099)],
            payload=b"order-1",
            provider="provider-token",
        )
        assert isinstance(built, types.InputMediaInvoice)
        assert built.invoice.currency == "EUR"
        assert built.invoice.prices[0].amount == 1099
        assert built.provider == "provider-token"
        assert built.payload == b"order-1"

    def test_raw_prices_are_taken_as_well_as_price_objects(self):
        built = as_invoice(
            "A thing",
            "d",
            currency="EUR",
            prices=[types.LabeledPrice(label="x", amount=5)],
            payload=b"p",
            provider="t",
        )
        assert built.invoice.prices[0].amount == 5

    def test_an_invoice_with_no_prices_is_refused(self):
        with pytest.raises(ValueError, match="at least one price"):
            as_invoice("t", "d", currency="EUR", prices=[], payload=b"p", provider="t")

    def test_an_invoice_with_no_currency_points_at_the_stars_one(self):
        with pytest.raises(ValueError, match="for Stars use as_stars_invoice"):
            as_invoice(
                "t", "d", currency="", prices=[Price("x", 1)], payload=b"p", provider="t"
            )

    def test_a_stars_invoice_has_no_provider_and_telegrams_currency(self):
        """The two differences that make it a separate function."""
        built = as_stars_invoice("Access", "One month", amount=50, payload=b"sub-1")
        assert built.invoice.currency == STARS == "XTR"
        assert built.provider is None
        assert built.invoice.prices[0].amount == 50

    def test_a_stars_invoice_needs_a_positive_amount(self):
        with pytest.raises(ValueError, match="positive amount"):
            as_stars_invoice("t", "d", amount=0, payload=b"p")

    def test_flexible_is_what_makes_a_shipping_query_happen(self):
        """Worth pinning: without it no shipping query is ever sent, and a
        handler waiting for one simply never runs."""
        plain = as_invoice(
            "t", "d", currency="EUR", prices=[Price("x", 1)], payload=b"p", provider="t"
        )
        flexible = as_invoice(
            "t",
            "d",
            currency="EUR",
            prices=[Price("x", 1)],
            payload=b"p",
            provider="t",
            flexible=True,
        )
        assert plain.invoice.flexible is False
        assert flexible.invoice.flexible is True


class TestAnsweringShipping:
    async def test_options_go_out(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await answer_shipping(
                invoker,
                7,
                options=[shipping_option("std", "Standard", [Price("Post", 500)])],
            )
            asked = server.only(functions.messages.SetBotShippingResults)
            assert asked.query_id == 7
            assert asked.shipping_options[0].title == "Standard"
            assert asked.error is None

    async def test_an_error_goes_out_instead(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await answer_shipping(invoker, 7, error="We do not ship there")
            asked = server.only(functions.messages.SetBotShippingResults)
            assert asked.error == "We do not ship there"
            assert asked.shipping_options is None

    @pytest.mark.parametrize(
        "kwargs",
        [{}, {"options": [], "error": "both"}],
    )
    async def test_neither_or_both_is_refused_before_it_is_sent(self, kwargs):
        """An unanswered shipping query stalls the order at the delivery step."""
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="either options or an error"):
                await answer_shipping(invoker, 7, **kwargs)
            assert server.queries == []


class TestAnsweringPreCheckout:
    async def test_approving_says_success(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            assert await answer_pre_checkout(invoker, 9) is True
            asked = server.only(functions.messages.SetBotPrecheckoutResults)
            assert asked.query_id == 9
            assert asked.success is True
            assert asked.error is None

    async def test_rejecting_carries_the_reason(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: True
            await answer_pre_checkout(invoker, 9, ok=False, error="Out of stock")
            asked = server.only(functions.messages.SetBotPrecheckoutResults)
            assert asked.success is False
            assert asked.error == "Out of stock"

    async def test_rejecting_without_a_reason_is_refused(self):
        """The reason is shown to the customer, so there has to be one."""
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="needs a reason"):
                await answer_pre_checkout(invoker, 9, ok=False)
            assert server.queries == []

    async def test_a_failed_answer_is_shouted_about_not_swallowed(self, caplog):
        """The rule this module exists to hold.

        Nothing above this hears about a pre-checkout answer that did not
        arrive, and the customer hears nothing either: the payment just fails.
        So it is logged at error and re-raised, never quietly dropped.
        """
        async with recording() as (invoker, server):

            def refuse(query):
                raise RuntimeError("no")

            server.answer_with = refuse
            with caplog.at_level(logging.ERROR, logger="sunnygram.methods.payments"):
                with pytest.raises(Exception):
                    await answer_pre_checkout(invoker, 9)
            assert any(
                "pre-checkout" in record.message and record.levelno >= logging.ERROR
                for record in caplog.records
            )


class TestStars:
    async def test_a_balance_is_the_whole_stars(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.payments.StarsStatus(
                balance=types.StarsAmount(amount=1234, nanos=500000000),
                chats=[],
                users=[],
            )
            assert await stars_balance(invoker) == 1234

    async def test_no_balance_at_all_reads_as_zero(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.payments.StarsStatus(
                balance=types.StarsAmount(amount=0, nanos=0), chats=[], users=[]
            )
            assert await stars_balance(invoker) == 0

    async def test_a_ledger_asks_with_the_paging_cursor(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda query: types.payments.StarsStatus(
                balance=types.StarsAmount(amount=0, nanos=0), chats=[], users=[]
            )
            await stars_transactions(invoker, offset="abc", limit=25, inbound=True)
            asked = server.only(functions.payments.GetStarsTransactions)
            assert asked.offset == "abc"
            assert asked.limit == 25
            assert asked.inbound is True

    async def test_a_refund_names_the_charge(self):
        async with recording() as (invoker, server):
            await refund_stars(invoker, types.InputPeerSelf(), "charge-77")
            assert server.only(functions.payments.RefundStarsCharge).charge_id == (
                "charge-77"
            )


class TestTheQueriesAsObjects:
    def test_a_shipping_query_reads_its_address(self):
        update = types.UpdateBotShippingQuery(
            query_id=1,
            user_id=2,
            payload=b"order",
            shipping_address=types.PostAddress(
                street_line1="1 Road",
                street_line2="",
                city="Rome",
                state="",
                country_iso2="IT",
                post_code="00100",
            ),
        )
        wrapped = ShippingQuery.from_raw(update)
        assert wrapped is not None
        assert wrapped.country == "IT"
        assert wrapped.payload == b"order"

    def test_a_pre_checkout_query_reads_the_amount(self):
        update = types.UpdateBotPrecheckoutQuery(
            query_id=3,
            user_id=4,
            payload=b"order",
            currency="EUR",
            total_amount=1099,
        )
        wrapped = PreCheckoutQuery.from_raw(update)
        assert wrapped is not None
        assert wrapped.total_amount == 1099
        assert wrapped.currency == "EUR"

    async def test_a_query_with_no_client_says_so_rather_than_failing_oddly(self):
        wrapped = PreCheckoutQuery(
            query_id=1, user_id=2, payload=b"", currency="EUR", total_amount=1
        )
        with pytest.raises(RuntimeError, match="did not come from a client"):
            await wrapped.approve()

    def test_anything_else_is_not_one_of_these(self):
        assert ShippingQuery.from_raw(types.UpdateStory) is None
        assert PreCheckoutQuery.from_raw(None) is None


class TestTheSuccessfulPayment:
    def test_the_sellers_reading_carries_what_a_refund_needs(self):
        action = types.MessageActionPaymentSentMe(
            currency="EUR",
            total_amount=1099,
            payload=b"order-1",
            charge=types.PaymentCharge(id="ch_1", provider_charge_id="pi_1"),
        )
        paid = SuccessfulPayment.from_raw(action)
        assert paid is not None
        assert paid.charge_id == "ch_1"
        assert paid.payload == b"order-1"
        assert paid.refundable is True

    def test_everybody_elses_reading_does_not(self):
        """Both constructors are a successful payment and only one can be
        refunded, which is worth being able to ask rather than discover."""
        action = types.MessageActionPaymentSent(currency="EUR", total_amount=1099)
        paid = SuccessfulPayment.from_raw(action)
        assert paid is not None
        assert paid.total_amount == 1099
        assert paid.refundable is False

    def test_any_other_service_action_is_not_a_payment(self):
        assert SuccessfulPayment.from_raw(types.MessageActionPinMessage()) is None
        assert SuccessfulPayment.from_raw(None) is None


class TestTheEvents:
    def test_both_questions_have_their_own_kind(self):
        from sunnygram.dispatcher import KINDS, _READINGS

        assert _READINGS[types.UpdateBotShippingQuery][0] == "shipping"
        assert _READINGS[types.UpdateBotPrecheckoutQuery][0] == "pre_checkout"
        assert "shipping" in KINDS
        assert "pre_checkout" in KINDS
