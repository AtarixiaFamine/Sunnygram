"""Star gifts.

Thirty-nine methods, and testing that each one sends its call would be
thirty-nine copies of the same sentence. What is worth holding down is the
three conventions the module is built on, because every one of them is a place
where being wrong would be quiet:

the handle, which has three spellings and picks between two of them on whether
a peer was named; the money, where the names are the only thing separating an
operation that spends from the same operation that does not; and the collection
call, which does five different things depending on which of four optional
lists is filled in.
"""

from __future__ import annotations

import pytest

from mtproto_server import recording
from sunnygram.methods import (
    add_to_gift_collection,
    buy_gift_transfer,
    buy_gift_upgrade,
    buy_resale_gift,
    convert_gift,
    craft_gift,
    create_gift_collection,
    gift_auction_state,
    gift_withdrawal_url,
    hide_gift,
    pin_gifts,
    remove_from_gift_collection,
    rename_gift_collection,
    reorder_gift_collection,
    resale_gifts,
    saved_gifts,
    send_gift,
    show_gift,
    transfer_gift,
    unique_gift,
    upgrade_gift,
)
from sunnygram.methods.gifts import _saved, stars
from sunnygram.raw import functions, types

ME = types.InputPeerSelf()


def _form(query):
    """Enough of a payment form for the two-step purchase to complete."""
    if isinstance(query, functions.payments.GetPaymentForm):
        return types.payments.PaymentFormStarGift(
            form_id=999,
            invoice=types.Invoice(
                currency="XTR",
                prices=[types.LabeledPrice(label="gift", amount=25)],
            ),
        )
    return types.payments.PaymentResult(updates=types.UpdatesTooLong())


class TestTheHandle:
    async def test_an_int_alone_is_the_message_a_gift_arrived_in(self):
        async with recording() as (invoker, server):
            handle = await _saved(invoker, 4321)
            assert isinstance(handle, types.InputSavedStarGiftUser)
            assert handle.msg_id == 4321

    async def test_an_int_with_a_peer_is_a_channel_saved_id(self):
        async with recording() as (invoker, server):
            handle = await _saved(invoker, 4321, ME)
            assert isinstance(handle, types.InputSavedStarGiftChat)
            assert handle.saved_id == 4321

    @pytest.mark.parametrize(
        "given",
        [
            "plushpepe-42",
            "@plushpepe-42",
            "t.me/nft/plushpepe-42",
            "https://t.me/nft/plushpepe-42",
            "https://t.me/nft/plushpepe-42?single",
        ],
    )
    async def test_a_slug_is_taken_out_of_whatever_was_pasted(self, given):
        async with recording() as (invoker, server):
            handle = await _saved(invoker, given)
            assert isinstance(handle, types.InputSavedStarGiftSlug)
            assert handle.slug == "plushpepe-42"

    async def test_a_raw_constructor_goes_straight_through(self):
        async with recording() as (invoker, server):
            given = types.InputSavedStarGiftUser(msg_id=7)
            assert await _saved(invoker, given) is given

    async def test_anything_else_says_what_a_gift_is_named_by(self):
        async with recording() as (invoker, server):
            with pytest.raises(TypeError, match="named by"):
                await _saved(invoker, 4.5)

    async def test_one_gift_is_accepted_where_a_list_is_taken(self):
        async with recording() as (invoker, server):
            await pin_gifts(invoker, 11, ME)
            asked = server.only(functions.payments.ToggleStarGiftsPinnedToTop)
            assert len(asked.stargift) == 1


class TestSpendingIsInTheName:
    async def test_upgrading_a_prepaid_gift_pays_nothing(self):
        async with recording() as (invoker, server):
            await upgrade_gift(invoker, 5)
            # One call, and no payment form anywhere near it.
            assert server.only(functions.payments.UpgradeStarGift) is not None
            assert server.all(functions.payments.GetPaymentForm) == []

    async def test_buying_an_upgrade_goes_through_a_form(self):
        async with recording() as (invoker, server):
            server.answer_with = _form
            await buy_gift_upgrade(invoker, 5)
            form = server.only(functions.payments.GetPaymentForm)
            assert isinstance(form.invoice, types.InputInvoiceStarGiftUpgrade)
            sent = server.only(functions.payments.SendStarsForm)
            assert sent.form_id == 999
            # And the free call is not used as well as the paid one.
            assert server.all(functions.payments.UpgradeStarGift) == []

    async def test_transferring_free_and_paid_are_different_calls(self):
        async with recording() as (invoker, server):
            await transfer_gift(invoker, 5, ME)
            assert server.only(functions.payments.TransferStarGift) is not None
            assert server.all(functions.payments.GetPaymentForm) == []
        async with recording() as (invoker, server):
            server.answer_with = _form
            await buy_gift_transfer(invoker, 5, ME)
            form = server.only(functions.payments.GetPaymentForm)
            assert isinstance(form.invoice, types.InputInvoiceStarGiftTransfer)

    async def test_sending_a_gift_carries_the_note_and_the_flags(self):
        async with recording() as (invoker, server):
            server.answer_with = _form
            await send_gift(
                invoker, ME, 77, message="happy birthday", anonymous=True,
                with_upgrade=True,
            )
            invoice = server.only(functions.payments.GetPaymentForm).invoice
            assert isinstance(invoice, types.InputInvoiceStarGift)
            assert invoice.gift_id == 77
            assert invoice.message.text == "happy birthday"
            assert invoice.hide_name is True
            assert invoice.include_upgrade is True

    async def test_a_gift_with_no_note_carries_no_empty_one(self):
        async with recording() as (invoker, server):
            server.answer_with = _form
            await send_gift(invoker, ME, 77)
            assert server.only(functions.payments.GetPaymentForm).invoice.message is None

    async def test_buying_a_resale_names_who_ends_up_holding_it(self):
        async with recording() as (invoker, server):
            server.answer_with = _form
            await buy_resale_gift(invoker, "https://t.me/nft/x-1", ME, ton=True)
            invoice = server.only(functions.payments.GetPaymentForm).invoice
            assert isinstance(invoice, types.InputInvoiceStarGiftResale)
            assert invoice.slug == "x-1"
            assert invoice.ton is True


class TestTheCollectionCall:
    async def test_each_verb_fills_in_only_its_own_list(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.StarGiftCollection(
                collection_id=1, title="t", icon=None, gifts_count=0, hash=0
            )
            await rename_gift_collection(invoker, 1, "New name", ME)
            asked = server.only(functions.payments.UpdateStarGiftCollection)
            assert asked.title == "New name"
            assert asked.add_stargift is None
            assert asked.delete_stargift is None
            assert asked.order is None

        for verb, field in (
            (add_to_gift_collection, "add_stargift"),
            (remove_from_gift_collection, "delete_stargift"),
            (reorder_gift_collection, "order"),
        ):
            async with recording() as (invoker, server):
                server.answer_with = lambda q: types.StarGiftCollection(
                    collection_id=1, title="t", icon=None, gifts_count=0, hash=0
                )
                await verb(invoker, 1, [3, 4], ME)
                asked = server.only(functions.payments.UpdateStarGiftCollection)
                assert getattr(asked, field) is not None, field
                assert asked.title is None
                others = {"add_stargift", "delete_stargift", "order"} - {field}
                for other in others:
                    assert getattr(asked, other) is None, (verb.__name__, other)

    async def test_a_collection_cannot_be_created_empty(self):
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="at least one"):
                await create_gift_collection(invoker, "Empty", [], ME)
            assert server.queries == []

    async def test_crafting_needs_something_to_consume(self):
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="at least one"):
                await craft_gift(invoker, [])
            assert server.queries == []


class TestFiltersAndPrices:
    async def test_shown_and_hidden_together_is_refused_not_sent(self):
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="shown or hidden"):
                await saved_gifts(invoker, ME, shown_only=True, hidden_only=True)
            assert server.queries == []

    async def test_the_filters_map_to_the_exclusions_they_mean(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.SavedStarGifts(
                count=0, gifts=[], chats=[], users=[]
            )
            await saved_gifts(invoker, ME, shown_only=True, upgradable_only=True)
            asked = server.only(functions.payments.GetSavedStarGifts)
            assert asked.exclude_unsaved is True
            assert asked.exclude_saved is False
            assert asked.exclude_unupgradable is True

    @pytest.mark.parametrize(
        "word, price, num",
        [("price", True, False), ("number", False, True), ("default", False, False)],
    )
    async def test_resale_order_is_a_word(self, word, price, num):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: types.payments.ResaleStarGifts(
                count=0, gifts=[], counters=None, chats=[], users=[],
                attributes=None, attributes_hash=None, next_offset=None,
            )
            await resale_gifts(invoker, 1, by=word)
            asked = server.only(functions.payments.GetResaleStarGifts)
            assert asked.sort_by_price is price
            assert asked.sort_by_num is num

    async def test_an_order_that_is_not_one_never_reaches_the_wire(self):
        async with recording() as (invoker, server):
            with pytest.raises(ValueError, match="price"):
                await resale_gifts(invoker, 1, by="cheapest")
            assert server.queries == []

    def test_a_price_is_whole_stars_with_no_fraction(self):
        assert stars(250) == types.StarsAmount(amount=250, nanos=0)
        with pytest.raises(ValueError, match="not negative"):
            stars(-1)


class TestOddCorners:
    async def test_showing_and_hiding_are_the_same_call_inverted(self):
        async with recording() as (invoker, server):
            await show_gift(invoker, 3)
            assert server.only(functions.payments.SaveStarGift).unsave is False
        async with recording() as (invoker, server):
            await hide_gift(invoker, 3)
            assert server.only(functions.payments.SaveStarGift).unsave is True

    async def test_converting_names_the_gift_and_nothing_else(self):
        async with recording() as (invoker, server):
            await convert_gift(invoker, 3)
            asked = server.only(functions.payments.ConvertStarGift)
            assert isinstance(asked.stargift, types.InputSavedStarGiftUser)

    async def test_an_auction_is_named_by_id_or_by_slug(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: True
            await gift_auction_state(invoker, 55)
            assert isinstance(
                server.only(functions.payments.GetStarGiftAuctionState).auction,
                types.InputStarGiftAuction,
            )
        async with recording() as (invoker, server):
            server.answer_with = lambda q: True
            await gift_auction_state(invoker, "t.me/nft/thing-1")
            asked = server.only(functions.payments.GetStarGiftAuctionState)
            assert isinstance(asked.auction, types.InputStarGiftAuctionSlug)
            assert asked.auction.slug == "thing-1"

    async def test_a_gift_withdrawal_proves_the_password_and_never_sends_it(self):
        async with recording() as (invoker, server):
            def answer(query):
                if isinstance(query, functions.account.GetPassword):
                    return types.account.Password(
                        new_algo=types.PasswordKdfAlgoUnknown(),
                        new_secure_algo=types.SecurePasswordKdfAlgoUnknown(),
                        secure_random=b"\x00" * 32,
                    )
                return types.payments.StarGiftWithdrawalUrl(url="https://t.me/$g")

            server.answer_with = answer
            # A distinct slug, so that finding "hunter2" on the wire can only
            # mean the password leaked and never that the gift was named it.
            url = await gift_withdrawal_url(invoker, "thing-1", "hunter2")
            assert url == "https://t.me/$g"
            assert all("hunter2" not in repr(q) for q in server.queries)

    async def test_a_slug_is_normalised_on_the_way_to_a_lookup(self):
        async with recording() as (invoker, server):
            server.answer_with = lambda q: True
            await unique_gift(invoker, "https://t.me/nft/thing-1")
            assert server.only(functions.payments.GetUniqueStarGift).slug == "thing-1"
