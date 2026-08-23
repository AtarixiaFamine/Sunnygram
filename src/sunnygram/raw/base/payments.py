# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the payments namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import payments as types_payments

    BankCardData = types_payments.BankCardData

    CheckCanSendGiftResult = (
        types_payments.CheckCanSendGiftResultOk
        | types_payments.CheckCanSendGiftResultFail
    )

    CheckedGiftCode = types_payments.CheckedGiftCode

    ConnectedStarRefBots = types_payments.ConnectedStarRefBots

    ExportedInvoice = types_payments.ExportedInvoice

    GiveawayInfo = (
        types_payments.GiveawayInfo
        | types_payments.GiveawayInfoResults
    )

    PaymentForm = (
        types_payments.PaymentForm
        | types_payments.PaymentFormStars
        | types_payments.PaymentFormStarGift
    )

    PaymentReceipt = (
        types_payments.PaymentReceipt
        | types_payments.PaymentReceiptStars
    )

    PaymentResult = (
        types_payments.PaymentResult
        | types_payments.PaymentVerificationNeeded
    )

    ResaleStarGifts = types_payments.ResaleStarGifts

    SavedInfo = types_payments.SavedInfo

    SavedStarGifts = types_payments.SavedStarGifts

    StarGiftActiveAuctions = (
        types_payments.StarGiftActiveAuctionsNotModified
        | types_payments.StarGiftActiveAuctions
    )

    StarGiftAuctionAcquiredGifts = types_payments.StarGiftAuctionAcquiredGifts

    StarGiftAuctionState = types_payments.StarGiftAuctionState

    StarGiftCollections = (
        types_payments.StarGiftCollectionsNotModified
        | types_payments.StarGiftCollections
    )

    StarGiftUpgradeAttributes = types_payments.StarGiftUpgradeAttributes

    StarGiftUpgradePreview = types_payments.StarGiftUpgradePreview

    StarGiftWithdrawalUrl = types_payments.StarGiftWithdrawalUrl

    StarGifts = (
        types_payments.StarGiftsNotModified
        | types_payments.StarGifts
    )

    StarsRevenueAdsAccountUrl = types_payments.StarsRevenueAdsAccountUrl

    StarsRevenueStats = types_payments.StarsRevenueStats

    StarsRevenueWithdrawalUrl = types_payments.StarsRevenueWithdrawalUrl

    StarsStatus = types_payments.StarsStatus

    SuggestedStarRefBots = types_payments.SuggestedStarRefBots

    UniqueStarGift = types_payments.UniqueStarGift

    UniqueStarGiftValueInfo = types_payments.UniqueStarGiftValueInfo

    ValidatedRequestedInfo = types_payments.ValidatedRequestedInfo
