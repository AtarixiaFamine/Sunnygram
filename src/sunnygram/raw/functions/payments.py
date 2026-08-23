# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the payments namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class GetPaymentForm(TLFunction["base.payments.PaymentForm"]):
    """The TL function payments.getPaymentForm#37148dbb, answered with payments.PaymentForm."""

    __slots__ = ("invoice", "theme_params",)

    ID = 0x37148DBB
    QUALNAME = "functions.payments.GetPaymentForm"
    RESULT = "payments.PaymentForm"

    def __init__(
        self,
        *,
        invoice: base.InputInvoice,
        theme_params: base.DataJSON | None = None,
    ) -> None:
        self.invoice = invoice
        self.theme_params = theme_params

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.theme_params is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.invoice.write(w)
        if self.theme_params is not None:
            self.theme_params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        invoice = r.read_object()
        theme_params = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.invoice = invoice
        self.theme_params = theme_params
        return self


class GetPaymentReceipt(TLFunction["base.payments.PaymentReceipt"]):
    """The TL function payments.getPaymentReceipt#2478d1cc, answered with payments.PaymentReceipt."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x2478D1CC
    QUALNAME = "functions.payments.GetPaymentReceipt"
    RESULT = "payments.PaymentReceipt"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class ValidateRequestedInfo(TLFunction["base.payments.ValidatedRequestedInfo"]):
    """The TL function payments.validateRequestedInfo#b6c8f12b, answered with payments.ValidatedRequestedInfo."""

    __slots__ = ("save", "invoice", "info",)

    ID = 0xB6C8F12B
    QUALNAME = "functions.payments.ValidateRequestedInfo"
    RESULT = "payments.ValidatedRequestedInfo"

    def __init__(
        self,
        *,
        save: bool = False,
        invoice: base.InputInvoice,
        info: base.PaymentRequestedInfo,
    ) -> None:
        self.save = save
        self.invoice = invoice
        self.info = info

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.save:
            flags |= 1 << 0
        w.write_int(flags)
        self.invoice.write(w)
        self.info.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        save = bool(flags & (1 << 0))
        invoice = r.read_object()
        info = r.read_object()
        self = cls.__new__(cls)
        self.save = save
        self.invoice = invoice
        self.info = info
        return self


class SendPaymentForm(TLFunction["base.payments.PaymentResult"]):
    """The TL function payments.sendPaymentForm#2d03522f, answered with payments.PaymentResult."""

    __slots__ = ("form_id", "invoice", "requested_info_id", "shipping_option_id", "credentials", "tip_amount",)

    ID = 0x2D03522F
    QUALNAME = "functions.payments.SendPaymentForm"
    RESULT = "payments.PaymentResult"

    def __init__(
        self,
        *,
        form_id: int,
        invoice: base.InputInvoice,
        requested_info_id: str | None = None,
        shipping_option_id: str | None = None,
        credentials: base.InputPaymentCredentials,
        tip_amount: int | None = None,
    ) -> None:
        self.form_id = form_id
        self.invoice = invoice
        self.requested_info_id = requested_info_id
        self.shipping_option_id = shipping_option_id
        self.credentials = credentials
        self.tip_amount = tip_amount

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.requested_info_id is not None:
            flags |= 1 << 0
        if self.shipping_option_id is not None:
            flags |= 1 << 1
        if self.tip_amount is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_long(self.form_id)
        self.invoice.write(w)
        if self.requested_info_id is not None:
            w.write_string(self.requested_info_id)
        if self.shipping_option_id is not None:
            w.write_string(self.shipping_option_id)
        self.credentials.write(w)
        if self.tip_amount is not None:
            w.write_long(self.tip_amount)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        form_id = r.read_long()
        invoice = r.read_object()
        requested_info_id = r.read_string() if flags & (1 << 0) else None
        shipping_option_id = r.read_string() if flags & (1 << 1) else None
        credentials = r.read_object()
        tip_amount = r.read_long() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.form_id = form_id
        self.invoice = invoice
        self.requested_info_id = requested_info_id
        self.shipping_option_id = shipping_option_id
        self.credentials = credentials
        self.tip_amount = tip_amount
        return self


class GetSavedInfo(TLFunction["base.payments.SavedInfo"]):
    """The TL function payments.getSavedInfo#227d824b, answered with payments.SavedInfo."""

    __slots__ = ()

    ID = 0x227D824B
    QUALNAME = "functions.payments.GetSavedInfo"
    RESULT = "payments.SavedInfo"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ClearSavedInfo(TLFunction["bool"]):
    """The TL function payments.clearSavedInfo#d83d70c1, answered with Bool."""

    __slots__ = ("credentials", "info",)

    ID = 0xD83D70C1
    QUALNAME = "functions.payments.ClearSavedInfo"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        credentials: bool = False,
        info: bool = False,
    ) -> None:
        self.credentials = credentials
        self.info = info

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.credentials:
            flags |= 1 << 0
        if self.info:
            flags |= 1 << 1
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        credentials = bool(flags & (1 << 0))
        info = bool(flags & (1 << 1))
        self = cls.__new__(cls)
        self.credentials = credentials
        self.info = info
        return self


class GetBankCardData(TLFunction["base.payments.BankCardData"]):
    """The TL function payments.getBankCardData#2e79d779, answered with payments.BankCardData."""

    __slots__ = ("number",)

    ID = 0x2E79D779
    QUALNAME = "functions.payments.GetBankCardData"
    RESULT = "payments.BankCardData"

    def __init__(
        self,
        *,
        number: str,
    ) -> None:
        self.number = number

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.number)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        number = r.read_string()
        self = cls.__new__(cls)
        self.number = number
        return self


class ExportInvoice(TLFunction["base.payments.ExportedInvoice"]):
    """The TL function payments.exportInvoice#0f91b065, answered with payments.ExportedInvoice."""

    __slots__ = ("invoice_media",)

    ID = 0x0F91B065
    QUALNAME = "functions.payments.ExportInvoice"
    RESULT = "payments.ExportedInvoice"

    def __init__(
        self,
        *,
        invoice_media: base.InputMedia,
    ) -> None:
        self.invoice_media = invoice_media

    def write_body(self, w: TLWriter) -> None:
        self.invoice_media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        invoice_media = r.read_object()
        self = cls.__new__(cls)
        self.invoice_media = invoice_media
        return self


class AssignAppStoreTransaction(TLFunction["base.Updates"]):
    """The TL function payments.assignAppStoreTransaction#80ed747d, answered with Updates."""

    __slots__ = ("receipt", "purpose",)

    ID = 0x80ED747D
    QUALNAME = "functions.payments.AssignAppStoreTransaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        receipt: bytes,
        purpose: base.InputStorePaymentPurpose,
    ) -> None:
        self.receipt = receipt
        self.purpose = purpose

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.receipt)
        self.purpose.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        receipt = r.read_bytes()
        purpose = r.read_object()
        self = cls.__new__(cls)
        self.receipt = receipt
        self.purpose = purpose
        return self


class AssignPlayMarketTransaction(TLFunction["base.Updates"]):
    """The TL function payments.assignPlayMarketTransaction#dffd50d3, answered with Updates."""

    __slots__ = ("receipt", "purpose",)

    ID = 0xDFFD50D3
    QUALNAME = "functions.payments.AssignPlayMarketTransaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        receipt: base.DataJSON,
        purpose: base.InputStorePaymentPurpose,
    ) -> None:
        self.receipt = receipt
        self.purpose = purpose

    def write_body(self, w: TLWriter) -> None:
        self.receipt.write(w)
        self.purpose.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        receipt = r.read_object()
        purpose = r.read_object()
        self = cls.__new__(cls)
        self.receipt = receipt
        self.purpose = purpose
        return self


class GetPremiumGiftCodeOptions(TLFunction["list[base.PremiumGiftCodeOption]"]):
    """The TL function payments.getPremiumGiftCodeOptions#2757ba54, answered with Vector<PremiumGiftCodeOption>."""

    __slots__ = ("boost_peer",)

    ID = 0x2757BA54
    QUALNAME = "functions.payments.GetPremiumGiftCodeOptions"
    RESULT = "Vector<PremiumGiftCodeOption>"

    def __init__(
        self,
        *,
        boost_peer: base.InputPeer | None = None,
    ) -> None:
        self.boost_peer = boost_peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.boost_peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.boost_peer is not None:
            self.boost_peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        boost_peer = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.boost_peer = boost_peer
        return self


class CheckGiftCode(TLFunction["base.payments.CheckedGiftCode"]):
    """The TL function payments.checkGiftCode#8e51b4c1, answered with payments.CheckedGiftCode."""

    __slots__ = ("slug",)

    ID = 0x8E51B4C1
    QUALNAME = "functions.payments.CheckGiftCode"
    RESULT = "payments.CheckedGiftCode"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class ApplyGiftCode(TLFunction["base.Updates"]):
    """The TL function payments.applyGiftCode#f6e26854, answered with Updates."""

    __slots__ = ("slug",)

    ID = 0xF6E26854
    QUALNAME = "functions.payments.ApplyGiftCode"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class GetGiveawayInfo(TLFunction["base.payments.GiveawayInfo"]):
    """The TL function payments.getGiveawayInfo#f4239425, answered with payments.GiveawayInfo."""

    __slots__ = ("peer", "msg_id",)

    ID = 0xF4239425
    QUALNAME = "functions.payments.GetGiveawayInfo"
    RESULT = "payments.GiveawayInfo"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class LaunchPrepaidGiveaway(TLFunction["base.Updates"]):
    """The TL function payments.launchPrepaidGiveaway#5ff58f20, answered with Updates."""

    __slots__ = ("peer", "giveaway_id", "purpose",)

    ID = 0x5FF58F20
    QUALNAME = "functions.payments.LaunchPrepaidGiveaway"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        giveaway_id: int,
        purpose: base.InputStorePaymentPurpose,
    ) -> None:
        self.peer = peer
        self.giveaway_id = giveaway_id
        self.purpose = purpose

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.giveaway_id)
        self.purpose.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        giveaway_id = r.read_long()
        purpose = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.giveaway_id = giveaway_id
        self.purpose = purpose
        return self


class GetStarsTopupOptions(TLFunction["list[base.StarsTopupOption]"]):
    """The TL function payments.getStarsTopupOptions#c00ec7d3, answered with Vector<StarsTopupOption>."""

    __slots__ = ()

    ID = 0xC00EC7D3
    QUALNAME = "functions.payments.GetStarsTopupOptions"
    RESULT = "Vector<StarsTopupOption>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetStarsStatus(TLFunction["base.payments.StarsStatus"]):
    """The TL function payments.getStarsStatus#4ea9b3bf, answered with payments.StarsStatus."""

    __slots__ = ("ton", "peer",)

    ID = 0x4EA9B3BF
    QUALNAME = "functions.payments.GetStarsStatus"
    RESULT = "payments.StarsStatus"

    def __init__(
        self,
        *,
        ton: bool = False,
        peer: base.InputPeer,
    ) -> None:
        self.ton = ton
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.ton:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        ton = bool(flags & (1 << 0))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.ton = ton
        self.peer = peer
        return self


class GetStarsTransactions(TLFunction["base.payments.StarsStatus"]):
    """The TL function payments.getStarsTransactions#69da4557, answered with payments.StarsStatus."""

    __slots__ = ("inbound", "outbound", "ascending", "ton", "subscription_id", "peer", "offset", "limit",)

    ID = 0x69DA4557
    QUALNAME = "functions.payments.GetStarsTransactions"
    RESULT = "payments.StarsStatus"

    def __init__(
        self,
        *,
        inbound: bool = False,
        outbound: bool = False,
        ascending: bool = False,
        ton: bool = False,
        subscription_id: str | None = None,
        peer: base.InputPeer,
        offset: str,
        limit: int,
    ) -> None:
        self.inbound = inbound
        self.outbound = outbound
        self.ascending = ascending
        self.ton = ton
        self.subscription_id = subscription_id
        self.peer = peer
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inbound:
            flags |= 1 << 0
        if self.outbound:
            flags |= 1 << 1
        if self.ascending:
            flags |= 1 << 2
        if self.ton:
            flags |= 1 << 4
        if self.subscription_id is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.subscription_id is not None:
            w.write_string(self.subscription_id)
        self.peer.write(w)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inbound = bool(flags & (1 << 0))
        outbound = bool(flags & (1 << 1))
        ascending = bool(flags & (1 << 2))
        ton = bool(flags & (1 << 4))
        subscription_id = r.read_string() if flags & (1 << 3) else None
        peer = r.read_object()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.inbound = inbound
        self.outbound = outbound
        self.ascending = ascending
        self.ton = ton
        self.subscription_id = subscription_id
        self.peer = peer
        self.offset = offset
        self.limit = limit
        return self


class SendStarsForm(TLFunction["base.payments.PaymentResult"]):
    """The TL function payments.sendStarsForm#7998c914, answered with payments.PaymentResult."""

    __slots__ = ("form_id", "invoice",)

    ID = 0x7998C914
    QUALNAME = "functions.payments.SendStarsForm"
    RESULT = "payments.PaymentResult"

    def __init__(
        self,
        *,
        form_id: int,
        invoice: base.InputInvoice,
    ) -> None:
        self.form_id = form_id
        self.invoice = invoice

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.form_id)
        self.invoice.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        form_id = r.read_long()
        invoice = r.read_object()
        self = cls.__new__(cls)
        self.form_id = form_id
        self.invoice = invoice
        return self


class RefundStarsCharge(TLFunction["base.Updates"]):
    """The TL function payments.refundStarsCharge#25ae8f4a, answered with Updates."""

    __slots__ = ("user_id", "charge_id",)

    ID = 0x25AE8F4A
    QUALNAME = "functions.payments.RefundStarsCharge"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        charge_id: str,
    ) -> None:
        self.user_id = user_id
        self.charge_id = charge_id

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_string(self.charge_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        charge_id = r.read_string()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.charge_id = charge_id
        return self


class GetStarsRevenueStats(TLFunction["base.payments.StarsRevenueStats"]):
    """The TL function payments.getStarsRevenueStats#d91ffad6, answered with payments.StarsRevenueStats."""

    __slots__ = ("dark", "ton", "peer",)

    ID = 0xD91FFAD6
    QUALNAME = "functions.payments.GetStarsRevenueStats"
    RESULT = "payments.StarsRevenueStats"

    def __init__(
        self,
        *,
        dark: bool = False,
        ton: bool = False,
        peer: base.InputPeer,
    ) -> None:
        self.dark = dark
        self.ton = ton
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        if self.ton:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        ton = bool(flags & (1 << 1))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.dark = dark
        self.ton = ton
        self.peer = peer
        return self


class GetStarsRevenueWithdrawalUrl(TLFunction["base.payments.StarsRevenueWithdrawalUrl"]):
    """The TL function payments.getStarsRevenueWithdrawalUrl#2433dc92, answered with payments.StarsRevenueWithdrawalUrl."""

    __slots__ = ("ton", "peer", "amount", "password",)

    ID = 0x2433DC92
    QUALNAME = "functions.payments.GetStarsRevenueWithdrawalUrl"
    RESULT = "payments.StarsRevenueWithdrawalUrl"

    def __init__(
        self,
        *,
        ton: bool = False,
        peer: base.InputPeer,
        amount: int | None = None,
        password: base.InputCheckPasswordSRP,
    ) -> None:
        self.ton = ton
        self.peer = peer
        self.amount = amount
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.ton:
            flags |= 1 << 0
        if self.amount is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.amount is not None:
            w.write_long(self.amount)
        self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        ton = bool(flags & (1 << 0))
        peer = r.read_object()
        amount = r.read_long() if flags & (1 << 1) else None
        password = r.read_object()
        self = cls.__new__(cls)
        self.ton = ton
        self.peer = peer
        self.amount = amount
        self.password = password
        return self


class GetStarsRevenueAdsAccountUrl(TLFunction["base.payments.StarsRevenueAdsAccountUrl"]):
    """The TL function payments.getStarsRevenueAdsAccountUrl#d1d7efc5, answered with payments.StarsRevenueAdsAccountUrl."""

    __slots__ = ("peer",)

    ID = 0xD1D7EFC5
    QUALNAME = "functions.payments.GetStarsRevenueAdsAccountUrl"
    RESULT = "payments.StarsRevenueAdsAccountUrl"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class GetStarsTransactionsByID(TLFunction["base.payments.StarsStatus"]):
    """The TL function payments.getStarsTransactionsByID#2dca16b8, answered with payments.StarsStatus."""

    __slots__ = ("ton", "peer", "id",)

    ID = 0x2DCA16B8
    QUALNAME = "functions.payments.GetStarsTransactionsByID"
    RESULT = "payments.StarsStatus"

    def __init__(
        self,
        *,
        ton: bool = False,
        peer: base.InputPeer,
        id: list[base.InputStarsTransaction],
    ) -> None:
        self.ton = ton
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.ton:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_vector(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        ton = bool(flags & (1 << 0))
        peer = r.read_object()
        id = r.read_vector()
        self = cls.__new__(cls)
        self.ton = ton
        self.peer = peer
        self.id = id
        return self


class GetStarsGiftOptions(TLFunction["list[base.StarsGiftOption]"]):
    """The TL function payments.getStarsGiftOptions#d3c96bc8, answered with Vector<StarsGiftOption>."""

    __slots__ = ("user_id",)

    ID = 0xD3C96BC8
    QUALNAME = "functions.payments.GetStarsGiftOptions"
    RESULT = "Vector<StarsGiftOption>"

    def __init__(
        self,
        *,
        user_id: base.InputUser | None = None,
    ) -> None:
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.user_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.user_id is not None:
            self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        user_id = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.user_id = user_id
        return self


class GetStarsSubscriptions(TLFunction["base.payments.StarsStatus"]):
    """The TL function payments.getStarsSubscriptions#032512c5, answered with payments.StarsStatus."""

    __slots__ = ("missing_balance", "peer", "offset",)

    ID = 0x032512C5
    QUALNAME = "functions.payments.GetStarsSubscriptions"
    RESULT = "payments.StarsStatus"

    def __init__(
        self,
        *,
        missing_balance: bool = False,
        peer: base.InputPeer,
        offset: str,
    ) -> None:
        self.missing_balance = missing_balance
        self.peer = peer
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.missing_balance:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        missing_balance = bool(flags & (1 << 0))
        peer = r.read_object()
        offset = r.read_string()
        self = cls.__new__(cls)
        self.missing_balance = missing_balance
        self.peer = peer
        self.offset = offset
        return self


class ChangeStarsSubscription(TLFunction["bool"]):
    """The TL function payments.changeStarsSubscription#c7770878, answered with Bool."""

    __slots__ = ("peer", "subscription_id", "canceled",)

    ID = 0xC7770878
    QUALNAME = "functions.payments.ChangeStarsSubscription"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        subscription_id: str,
        canceled: bool | None = None,
    ) -> None:
        self.peer = peer
        self.subscription_id = subscription_id
        self.canceled = canceled

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.canceled is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.subscription_id)
        if self.canceled is not None:
            w.write_bool(self.canceled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        subscription_id = r.read_string()
        canceled = r.read_bool() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.subscription_id = subscription_id
        self.canceled = canceled
        return self


class FulfillStarsSubscription(TLFunction["bool"]):
    """The TL function payments.fulfillStarsSubscription#cc5bebb3, answered with Bool."""

    __slots__ = ("peer", "subscription_id",)

    ID = 0xCC5BEBB3
    QUALNAME = "functions.payments.FulfillStarsSubscription"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        subscription_id: str,
    ) -> None:
        self.peer = peer
        self.subscription_id = subscription_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.subscription_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        subscription_id = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.subscription_id = subscription_id
        return self


class GetStarsGiveawayOptions(TLFunction["list[base.StarsGiveawayOption]"]):
    """The TL function payments.getStarsGiveawayOptions#bd1efd3e, answered with Vector<StarsGiveawayOption>."""

    __slots__ = ()

    ID = 0xBD1EFD3E
    QUALNAME = "functions.payments.GetStarsGiveawayOptions"
    RESULT = "Vector<StarsGiveawayOption>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetStarGifts(TLFunction["base.payments.StarGifts"]):
    """The TL function payments.getStarGifts#c4563590, answered with payments.StarGifts."""

    __slots__ = ("hash",)

    ID = 0xC4563590
    QUALNAME = "functions.payments.GetStarGifts"
    RESULT = "payments.StarGifts"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SaveStarGift(TLFunction["bool"]):
    """The TL function payments.saveStarGift#2a2a697c, answered with Bool."""

    __slots__ = ("unsave", "stargift",)

    ID = 0x2A2A697C
    QUALNAME = "functions.payments.SaveStarGift"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        unsave: bool = False,
        stargift: base.InputSavedStarGift,
    ) -> None:
        self.unsave = unsave
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.unsave:
            flags |= 1 << 0
        w.write_int(flags)
        self.stargift.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        unsave = bool(flags & (1 << 0))
        stargift = r.read_object()
        self = cls.__new__(cls)
        self.unsave = unsave
        self.stargift = stargift
        return self


class ConvertStarGift(TLFunction["bool"]):
    """The TL function payments.convertStarGift#74bf076b, answered with Bool."""

    __slots__ = ("stargift",)

    ID = 0x74BF076B
    QUALNAME = "functions.payments.ConvertStarGift"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        stargift: base.InputSavedStarGift,
    ) -> None:
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        self.stargift.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_object()
        self = cls.__new__(cls)
        self.stargift = stargift
        return self


class BotCancelStarsSubscription(TLFunction["bool"]):
    """The TL function payments.botCancelStarsSubscription#6dfa0622, answered with Bool."""

    __slots__ = ("restore", "user_id", "charge_id",)

    ID = 0x6DFA0622
    QUALNAME = "functions.payments.BotCancelStarsSubscription"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        restore: bool = False,
        user_id: base.InputUser,
        charge_id: str,
    ) -> None:
        self.restore = restore
        self.user_id = user_id
        self.charge_id = charge_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.restore:
            flags |= 1 << 0
        w.write_int(flags)
        self.user_id.write(w)
        w.write_string(self.charge_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        restore = bool(flags & (1 << 0))
        user_id = r.read_object()
        charge_id = r.read_string()
        self = cls.__new__(cls)
        self.restore = restore
        self.user_id = user_id
        self.charge_id = charge_id
        return self


class GetConnectedStarRefBots(TLFunction["base.payments.ConnectedStarRefBots"]):
    """The TL function payments.getConnectedStarRefBots#5869a553, answered with payments.ConnectedStarRefBots."""

    __slots__ = ("peer", "offset_date", "offset_link", "limit",)

    ID = 0x5869A553
    QUALNAME = "functions.payments.GetConnectedStarRefBots"
    RESULT = "payments.ConnectedStarRefBots"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        offset_date: int | None = None,
        offset_link: str | None = None,
        limit: int,
    ) -> None:
        self.peer = peer
        self.offset_date = offset_date
        self.offset_link = offset_link
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.offset_date is not None:
            flags |= 1 << 2
        if self.offset_link is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        if self.offset_date is not None:
            w.write_int(self.offset_date)
        if self.offset_link is not None:
            w.write_string(self.offset_link)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        offset_date = r.read_int() if flags & (1 << 2) else None
        offset_link = r.read_string() if flags & (1 << 2) else None
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.offset_date = offset_date
        self.offset_link = offset_link
        self.limit = limit
        return self


class GetConnectedStarRefBot(TLFunction["base.payments.ConnectedStarRefBots"]):
    """The TL function payments.getConnectedStarRefBot#b7d998f0, answered with payments.ConnectedStarRefBots."""

    __slots__ = ("peer", "bot",)

    ID = 0xB7D998F0
    QUALNAME = "functions.payments.GetConnectedStarRefBot"
    RESULT = "payments.ConnectedStarRefBots"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        bot: base.InputUser,
    ) -> None:
        self.peer = peer
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        bot = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.bot = bot
        return self


class GetSuggestedStarRefBots(TLFunction["base.payments.SuggestedStarRefBots"]):
    """The TL function payments.getSuggestedStarRefBots#0d6b48f7, answered with payments.SuggestedStarRefBots."""

    __slots__ = ("order_by_revenue", "order_by_date", "peer", "offset", "limit",)

    ID = 0x0D6B48F7
    QUALNAME = "functions.payments.GetSuggestedStarRefBots"
    RESULT = "payments.SuggestedStarRefBots"

    def __init__(
        self,
        *,
        order_by_revenue: bool = False,
        order_by_date: bool = False,
        peer: base.InputPeer,
        offset: str,
        limit: int,
    ) -> None:
        self.order_by_revenue = order_by_revenue
        self.order_by_date = order_by_date
        self.peer = peer
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.order_by_revenue:
            flags |= 1 << 0
        if self.order_by_date:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        order_by_revenue = bool(flags & (1 << 0))
        order_by_date = bool(flags & (1 << 1))
        peer = r.read_object()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.order_by_revenue = order_by_revenue
        self.order_by_date = order_by_date
        self.peer = peer
        self.offset = offset
        self.limit = limit
        return self


class ConnectStarRefBot(TLFunction["base.payments.ConnectedStarRefBots"]):
    """The TL function payments.connectStarRefBot#7ed5348a, answered with payments.ConnectedStarRefBots."""

    __slots__ = ("peer", "bot",)

    ID = 0x7ED5348A
    QUALNAME = "functions.payments.ConnectStarRefBot"
    RESULT = "payments.ConnectedStarRefBots"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        bot: base.InputUser,
    ) -> None:
        self.peer = peer
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        bot = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.bot = bot
        return self


class EditConnectedStarRefBot(TLFunction["base.payments.ConnectedStarRefBots"]):
    """The TL function payments.editConnectedStarRefBot#e4fca4a3, answered with payments.ConnectedStarRefBots."""

    __slots__ = ("revoked", "peer", "link",)

    ID = 0xE4FCA4A3
    QUALNAME = "functions.payments.EditConnectedStarRefBot"
    RESULT = "payments.ConnectedStarRefBots"

    def __init__(
        self,
        *,
        revoked: bool = False,
        peer: base.InputPeer,
        link: str,
    ) -> None:
        self.revoked = revoked
        self.peer = peer
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoked:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.link)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoked = bool(flags & (1 << 0))
        peer = r.read_object()
        link = r.read_string()
        self = cls.__new__(cls)
        self.revoked = revoked
        self.peer = peer
        self.link = link
        return self


class GetStarGiftUpgradePreview(TLFunction["base.payments.StarGiftUpgradePreview"]):
    """The TL function payments.getStarGiftUpgradePreview#9c9abcb1, answered with payments.StarGiftUpgradePreview."""

    __slots__ = ("gift_id",)

    ID = 0x9C9ABCB1
    QUALNAME = "functions.payments.GetStarGiftUpgradePreview"
    RESULT = "payments.StarGiftUpgradePreview"

    def __init__(
        self,
        *,
        gift_id: int,
    ) -> None:
        self.gift_id = gift_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.gift_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift_id = r.read_long()
        self = cls.__new__(cls)
        self.gift_id = gift_id
        return self


class UpgradeStarGift(TLFunction["base.Updates"]):
    """The TL function payments.upgradeStarGift#aed6e4f5, answered with Updates."""

    __slots__ = ("keep_original_details", "stargift",)

    ID = 0xAED6E4F5
    QUALNAME = "functions.payments.UpgradeStarGift"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        keep_original_details: bool = False,
        stargift: base.InputSavedStarGift,
    ) -> None:
        self.keep_original_details = keep_original_details
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.keep_original_details:
            flags |= 1 << 0
        w.write_int(flags)
        self.stargift.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        keep_original_details = bool(flags & (1 << 0))
        stargift = r.read_object()
        self = cls.__new__(cls)
        self.keep_original_details = keep_original_details
        self.stargift = stargift
        return self


class TransferStarGift(TLFunction["base.Updates"]):
    """The TL function payments.transferStarGift#7f18176a, answered with Updates."""

    __slots__ = ("stargift", "to_id",)

    ID = 0x7F18176A
    QUALNAME = "functions.payments.TransferStarGift"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        stargift: base.InputSavedStarGift,
        to_id: base.InputPeer,
    ) -> None:
        self.stargift = stargift
        self.to_id = to_id

    def write_body(self, w: TLWriter) -> None:
        self.stargift.write(w)
        self.to_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_object()
        to_id = r.read_object()
        self = cls.__new__(cls)
        self.stargift = stargift
        self.to_id = to_id
        return self


class GetUniqueStarGift(TLFunction["base.payments.UniqueStarGift"]):
    """The TL function payments.getUniqueStarGift#a1974d72, answered with payments.UniqueStarGift."""

    __slots__ = ("slug",)

    ID = 0xA1974D72
    QUALNAME = "functions.payments.GetUniqueStarGift"
    RESULT = "payments.UniqueStarGift"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class GetSavedStarGifts(TLFunction["base.payments.SavedStarGifts"]):
    """The TL function payments.getSavedStarGifts#a319e569, answered with payments.SavedStarGifts."""

    __slots__ = ("exclude_unsaved", "exclude_saved", "exclude_unlimited", "exclude_unique", "sort_by_value", "exclude_upgradable", "exclude_unupgradable", "peer_color_available", "exclude_hosted", "peer", "collection_id", "offset", "limit",)

    ID = 0xA319E569
    QUALNAME = "functions.payments.GetSavedStarGifts"
    RESULT = "payments.SavedStarGifts"

    def __init__(
        self,
        *,
        exclude_unsaved: bool = False,
        exclude_saved: bool = False,
        exclude_unlimited: bool = False,
        exclude_unique: bool = False,
        sort_by_value: bool = False,
        exclude_upgradable: bool = False,
        exclude_unupgradable: bool = False,
        peer_color_available: bool = False,
        exclude_hosted: bool = False,
        peer: base.InputPeer,
        collection_id: int | None = None,
        offset: str,
        limit: int,
    ) -> None:
        self.exclude_unsaved = exclude_unsaved
        self.exclude_saved = exclude_saved
        self.exclude_unlimited = exclude_unlimited
        self.exclude_unique = exclude_unique
        self.sort_by_value = sort_by_value
        self.exclude_upgradable = exclude_upgradable
        self.exclude_unupgradable = exclude_unupgradable
        self.peer_color_available = peer_color_available
        self.exclude_hosted = exclude_hosted
        self.peer = peer
        self.collection_id = collection_id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.exclude_unsaved:
            flags |= 1 << 0
        if self.exclude_saved:
            flags |= 1 << 1
        if self.exclude_unlimited:
            flags |= 1 << 2
        if self.exclude_unique:
            flags |= 1 << 4
        if self.sort_by_value:
            flags |= 1 << 5
        if self.exclude_upgradable:
            flags |= 1 << 7
        if self.exclude_unupgradable:
            flags |= 1 << 8
        if self.peer_color_available:
            flags |= 1 << 9
        if self.exclude_hosted:
            flags |= 1 << 10
        if self.collection_id is not None:
            flags |= 1 << 6
        w.write_int(flags)
        self.peer.write(w)
        if self.collection_id is not None:
            w.write_int(self.collection_id)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        exclude_unsaved = bool(flags & (1 << 0))
        exclude_saved = bool(flags & (1 << 1))
        exclude_unlimited = bool(flags & (1 << 2))
        exclude_unique = bool(flags & (1 << 4))
        sort_by_value = bool(flags & (1 << 5))
        exclude_upgradable = bool(flags & (1 << 7))
        exclude_unupgradable = bool(flags & (1 << 8))
        peer_color_available = bool(flags & (1 << 9))
        exclude_hosted = bool(flags & (1 << 10))
        peer = r.read_object()
        collection_id = r.read_int() if flags & (1 << 6) else None
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.exclude_unsaved = exclude_unsaved
        self.exclude_saved = exclude_saved
        self.exclude_unlimited = exclude_unlimited
        self.exclude_unique = exclude_unique
        self.sort_by_value = sort_by_value
        self.exclude_upgradable = exclude_upgradable
        self.exclude_unupgradable = exclude_unupgradable
        self.peer_color_available = peer_color_available
        self.exclude_hosted = exclude_hosted
        self.peer = peer
        self.collection_id = collection_id
        self.offset = offset
        self.limit = limit
        return self


class GetSavedStarGift(TLFunction["base.payments.SavedStarGifts"]):
    """The TL function payments.getSavedStarGift#b455a106, answered with payments.SavedStarGifts."""

    __slots__ = ("stargift",)

    ID = 0xB455A106
    QUALNAME = "functions.payments.GetSavedStarGift"
    RESULT = "payments.SavedStarGifts"

    def __init__(
        self,
        *,
        stargift: list[base.InputSavedStarGift],
    ) -> None:
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.stargift)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_vector()
        self = cls.__new__(cls)
        self.stargift = stargift
        return self


class GetStarGiftWithdrawalUrl(TLFunction["base.payments.StarGiftWithdrawalUrl"]):
    """The TL function payments.getStarGiftWithdrawalUrl#d06e93a8, answered with payments.StarGiftWithdrawalUrl."""

    __slots__ = ("stargift", "password",)

    ID = 0xD06E93A8
    QUALNAME = "functions.payments.GetStarGiftWithdrawalUrl"
    RESULT = "payments.StarGiftWithdrawalUrl"

    def __init__(
        self,
        *,
        stargift: base.InputSavedStarGift,
        password: base.InputCheckPasswordSRP,
    ) -> None:
        self.stargift = stargift
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        self.stargift.write(w)
        self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_object()
        password = r.read_object()
        self = cls.__new__(cls)
        self.stargift = stargift
        self.password = password
        return self


class ToggleChatStarGiftNotifications(TLFunction["bool"]):
    """The TL function payments.toggleChatStarGiftNotifications#60eaefa1, answered with Bool."""

    __slots__ = ("enabled", "peer",)

    ID = 0x60EAEFA1
    QUALNAME = "functions.payments.ToggleChatStarGiftNotifications"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        enabled: bool = False,
        peer: base.InputPeer,
    ) -> None:
        self.enabled = enabled
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.enabled:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        enabled = bool(flags & (1 << 0))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.enabled = enabled
        self.peer = peer
        return self


class ToggleStarGiftsPinnedToTop(TLFunction["bool"]):
    """The TL function payments.toggleStarGiftsPinnedToTop#1513e7b0, answered with Bool."""

    __slots__ = ("peer", "stargift",)

    ID = 0x1513E7B0
    QUALNAME = "functions.payments.ToggleStarGiftsPinnedToTop"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        stargift: list[base.InputSavedStarGift],
    ) -> None:
        self.peer = peer
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.stargift)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        stargift = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.stargift = stargift
        return self


class CanPurchaseStore(TLFunction["bool"]):
    """The TL function payments.canPurchaseStore#4fdc5ea7, answered with Bool."""

    __slots__ = ("purpose",)

    ID = 0x4FDC5EA7
    QUALNAME = "functions.payments.CanPurchaseStore"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        purpose: base.InputStorePaymentPurpose,
    ) -> None:
        self.purpose = purpose

    def write_body(self, w: TLWriter) -> None:
        self.purpose.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        purpose = r.read_object()
        self = cls.__new__(cls)
        self.purpose = purpose
        return self


class GetResaleStarGifts(TLFunction["base.payments.ResaleStarGifts"]):
    """The TL function payments.getResaleStarGifts#7a5fa236, answered with payments.ResaleStarGifts."""

    __slots__ = ("sort_by_price", "sort_by_num", "for_craft", "stars_only", "attributes_hash", "gift_id", "attributes", "offset", "limit",)

    ID = 0x7A5FA236
    QUALNAME = "functions.payments.GetResaleStarGifts"
    RESULT = "payments.ResaleStarGifts"

    def __init__(
        self,
        *,
        sort_by_price: bool = False,
        sort_by_num: bool = False,
        for_craft: bool = False,
        stars_only: bool = False,
        attributes_hash: int | None = None,
        gift_id: int,
        attributes: list[base.StarGiftAttributeId] | None = None,
        offset: str,
        limit: int,
    ) -> None:
        self.sort_by_price = sort_by_price
        self.sort_by_num = sort_by_num
        self.for_craft = for_craft
        self.stars_only = stars_only
        self.attributes_hash = attributes_hash
        self.gift_id = gift_id
        self.attributes = attributes
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.sort_by_price:
            flags |= 1 << 1
        if self.sort_by_num:
            flags |= 1 << 2
        if self.for_craft:
            flags |= 1 << 4
        if self.stars_only:
            flags |= 1 << 5
        if self.attributes_hash is not None:
            flags |= 1 << 0
        if self.attributes is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.attributes_hash is not None:
            w.write_long(self.attributes_hash)
        w.write_long(self.gift_id)
        if self.attributes is not None:
            w.write_vector(self.attributes)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        sort_by_price = bool(flags & (1 << 1))
        sort_by_num = bool(flags & (1 << 2))
        for_craft = bool(flags & (1 << 4))
        stars_only = bool(flags & (1 << 5))
        attributes_hash = r.read_long() if flags & (1 << 0) else None
        gift_id = r.read_long()
        attributes = r.read_vector() if flags & (1 << 3) else None
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.sort_by_price = sort_by_price
        self.sort_by_num = sort_by_num
        self.for_craft = for_craft
        self.stars_only = stars_only
        self.attributes_hash = attributes_hash
        self.gift_id = gift_id
        self.attributes = attributes
        self.offset = offset
        self.limit = limit
        return self


class UpdateStarGiftPrice(TLFunction["base.Updates"]):
    """The TL function payments.updateStarGiftPrice#edbe6ccb, answered with Updates."""

    __slots__ = ("stargift", "resell_amount",)

    ID = 0xEDBE6CCB
    QUALNAME = "functions.payments.UpdateStarGiftPrice"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        stargift: base.InputSavedStarGift,
        resell_amount: base.StarsAmount,
    ) -> None:
        self.stargift = stargift
        self.resell_amount = resell_amount

    def write_body(self, w: TLWriter) -> None:
        self.stargift.write(w)
        self.resell_amount.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_object()
        resell_amount = r.read_object()
        self = cls.__new__(cls)
        self.stargift = stargift
        self.resell_amount = resell_amount
        return self


class CreateStarGiftCollection(TLFunction["base.StarGiftCollection"]):
    """The TL function payments.createStarGiftCollection#1f4a0e87, answered with StarGiftCollection."""

    __slots__ = ("peer", "title", "stargift",)

    ID = 0x1F4A0E87
    QUALNAME = "functions.payments.CreateStarGiftCollection"
    RESULT = "StarGiftCollection"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        title: str,
        stargift: list[base.InputSavedStarGift],
    ) -> None:
        self.peer = peer
        self.title = title
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.title)
        w.write_vector(self.stargift)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        title = r.read_string()
        stargift = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.title = title
        self.stargift = stargift
        return self


class UpdateStarGiftCollection(TLFunction["base.StarGiftCollection"]):
    """The TL function payments.updateStarGiftCollection#4fddbee7, answered with StarGiftCollection."""

    __slots__ = ("peer", "collection_id", "title", "delete_stargift", "add_stargift", "order",)

    ID = 0x4FDDBEE7
    QUALNAME = "functions.payments.UpdateStarGiftCollection"
    RESULT = "StarGiftCollection"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        collection_id: int,
        title: str | None = None,
        delete_stargift: list[base.InputSavedStarGift] | None = None,
        add_stargift: list[base.InputSavedStarGift] | None = None,
        order: list[base.InputSavedStarGift] | None = None,
    ) -> None:
        self.peer = peer
        self.collection_id = collection_id
        self.title = title
        self.delete_stargift = delete_stargift
        self.add_stargift = add_stargift
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title is not None:
            flags |= 1 << 0
        if self.delete_stargift is not None:
            flags |= 1 << 1
        if self.add_stargift is not None:
            flags |= 1 << 2
        if self.order is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.collection_id)
        if self.title is not None:
            w.write_string(self.title)
        if self.delete_stargift is not None:
            w.write_vector(self.delete_stargift)
        if self.add_stargift is not None:
            w.write_vector(self.add_stargift)
        if self.order is not None:
            w.write_vector(self.order)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        collection_id = r.read_int()
        title = r.read_string() if flags & (1 << 0) else None
        delete_stargift = r.read_vector() if flags & (1 << 1) else None
        add_stargift = r.read_vector() if flags & (1 << 2) else None
        order = r.read_vector() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.collection_id = collection_id
        self.title = title
        self.delete_stargift = delete_stargift
        self.add_stargift = add_stargift
        self.order = order
        return self


class ReorderStarGiftCollections(TLFunction["bool"]):
    """The TL function payments.reorderStarGiftCollections#c32af4cc, answered with Bool."""

    __slots__ = ("peer", "order",)

    ID = 0xC32AF4CC
    QUALNAME = "functions.payments.ReorderStarGiftCollections"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        order: list[int],
    ) -> None:
        self.peer = peer
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        order = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.order = order
        return self


class DeleteStarGiftCollection(TLFunction["bool"]):
    """The TL function payments.deleteStarGiftCollection#ad5648e8, answered with Bool."""

    __slots__ = ("peer", "collection_id",)

    ID = 0xAD5648E8
    QUALNAME = "functions.payments.DeleteStarGiftCollection"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        collection_id: int,
    ) -> None:
        self.peer = peer
        self.collection_id = collection_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.collection_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        collection_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.collection_id = collection_id
        return self


class GetStarGiftCollections(TLFunction["base.payments.StarGiftCollections"]):
    """The TL function payments.getStarGiftCollections#981b91dd, answered with payments.StarGiftCollections."""

    __slots__ = ("peer", "hash",)

    ID = 0x981B91DD
    QUALNAME = "functions.payments.GetStarGiftCollections"
    RESULT = "payments.StarGiftCollections"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        hash: int,
    ) -> None:
        self.peer = peer
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.hash = hash
        return self


class GetUniqueStarGiftValueInfo(TLFunction["base.payments.UniqueStarGiftValueInfo"]):
    """The TL function payments.getUniqueStarGiftValueInfo#4365af6b, answered with payments.UniqueStarGiftValueInfo."""

    __slots__ = ("slug",)

    ID = 0x4365AF6B
    QUALNAME = "functions.payments.GetUniqueStarGiftValueInfo"
    RESULT = "payments.UniqueStarGiftValueInfo"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class CheckCanSendGift(TLFunction["base.payments.CheckCanSendGiftResult"]):
    """The TL function payments.checkCanSendGift#c0c4edc9, answered with payments.CheckCanSendGiftResult."""

    __slots__ = ("gift_id",)

    ID = 0xC0C4EDC9
    QUALNAME = "functions.payments.CheckCanSendGift"
    RESULT = "payments.CheckCanSendGiftResult"

    def __init__(
        self,
        *,
        gift_id: int,
    ) -> None:
        self.gift_id = gift_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.gift_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift_id = r.read_long()
        self = cls.__new__(cls)
        self.gift_id = gift_id
        return self


class GetStarGiftAuctionState(TLFunction["base.payments.StarGiftAuctionState"]):
    """The TL function payments.getStarGiftAuctionState#5c9ff4d6, answered with payments.StarGiftAuctionState."""

    __slots__ = ("auction", "version",)

    ID = 0x5C9FF4D6
    QUALNAME = "functions.payments.GetStarGiftAuctionState"
    RESULT = "payments.StarGiftAuctionState"

    def __init__(
        self,
        *,
        auction: base.InputStarGiftAuction,
        version: int,
    ) -> None:
        self.auction = auction
        self.version = version

    def write_body(self, w: TLWriter) -> None:
        self.auction.write(w)
        w.write_int(self.version)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        auction = r.read_object()
        version = r.read_int()
        self = cls.__new__(cls)
        self.auction = auction
        self.version = version
        return self


class GetStarGiftAuctionAcquiredGifts(TLFunction["base.payments.StarGiftAuctionAcquiredGifts"]):
    """The TL function payments.getStarGiftAuctionAcquiredGifts#6ba2cbec, answered with payments.StarGiftAuctionAcquiredGifts."""

    __slots__ = ("gift_id",)

    ID = 0x6BA2CBEC
    QUALNAME = "functions.payments.GetStarGiftAuctionAcquiredGifts"
    RESULT = "payments.StarGiftAuctionAcquiredGifts"

    def __init__(
        self,
        *,
        gift_id: int,
    ) -> None:
        self.gift_id = gift_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.gift_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift_id = r.read_long()
        self = cls.__new__(cls)
        self.gift_id = gift_id
        return self


class GetStarGiftActiveAuctions(TLFunction["base.payments.StarGiftActiveAuctions"]):
    """The TL function payments.getStarGiftActiveAuctions#a5d0514d, answered with payments.StarGiftActiveAuctions."""

    __slots__ = ("hash",)

    ID = 0xA5D0514D
    QUALNAME = "functions.payments.GetStarGiftActiveAuctions"
    RESULT = "payments.StarGiftActiveAuctions"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ResolveStarGiftOffer(TLFunction["base.Updates"]):
    """The TL function payments.resolveStarGiftOffer#e9ce781c, answered with Updates."""

    __slots__ = ("decline", "offer_msg_id",)

    ID = 0xE9CE781C
    QUALNAME = "functions.payments.ResolveStarGiftOffer"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        decline: bool = False,
        offer_msg_id: int,
    ) -> None:
        self.decline = decline
        self.offer_msg_id = offer_msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.decline:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.offer_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        decline = bool(flags & (1 << 0))
        offer_msg_id = r.read_int()
        self = cls.__new__(cls)
        self.decline = decline
        self.offer_msg_id = offer_msg_id
        return self


class SendStarGiftOffer(TLFunction["base.Updates"]):
    """The TL function payments.sendStarGiftOffer#8fb86b41, answered with Updates."""

    __slots__ = ("peer", "slug", "price", "duration", "random_id", "allow_paid_stars",)

    ID = 0x8FB86B41
    QUALNAME = "functions.payments.SendStarGiftOffer"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        slug: str,
        price: base.StarsAmount,
        duration: int,
        random_id: int,
        allow_paid_stars: int | None = None,
    ) -> None:
        self.peer = peer
        self.slug = slug
        self.price = price
        self.duration = duration
        self.random_id = random_id
        self.allow_paid_stars = allow_paid_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.allow_paid_stars is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.slug)
        self.price.write(w)
        w.write_int(self.duration)
        w.write_long(self.random_id)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        slug = r.read_string()
        price = r.read_object()
        duration = r.read_int()
        random_id = r.read_long()
        allow_paid_stars = r.read_long() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.slug = slug
        self.price = price
        self.duration = duration
        self.random_id = random_id
        self.allow_paid_stars = allow_paid_stars
        return self


class GetStarGiftUpgradeAttributes(TLFunction["base.payments.StarGiftUpgradeAttributes"]):
    """The TL function payments.getStarGiftUpgradeAttributes#6d038b58, answered with payments.StarGiftUpgradeAttributes."""

    __slots__ = ("gift_id",)

    ID = 0x6D038B58
    QUALNAME = "functions.payments.GetStarGiftUpgradeAttributes"
    RESULT = "payments.StarGiftUpgradeAttributes"

    def __init__(
        self,
        *,
        gift_id: int,
    ) -> None:
        self.gift_id = gift_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.gift_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift_id = r.read_long()
        self = cls.__new__(cls)
        self.gift_id = gift_id
        return self


class GetCraftStarGifts(TLFunction["base.payments.SavedStarGifts"]):
    """The TL function payments.getCraftStarGifts#fd05dd00, answered with payments.SavedStarGifts."""

    __slots__ = ("gift_id", "offset", "limit",)

    ID = 0xFD05DD00
    QUALNAME = "functions.payments.GetCraftStarGifts"
    RESULT = "payments.SavedStarGifts"

    def __init__(
        self,
        *,
        gift_id: int,
        offset: str,
        limit: int,
    ) -> None:
        self.gift_id = gift_id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.gift_id)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift_id = r.read_long()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.gift_id = gift_id
        self.offset = offset
        self.limit = limit
        return self


class CraftStarGift(TLFunction["base.Updates"]):
    """The TL function payments.craftStarGift#b0f9684f, answered with Updates."""

    __slots__ = ("stargift",)

    ID = 0xB0F9684F
    QUALNAME = "functions.payments.CraftStarGift"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        stargift: list[base.InputSavedStarGift],
    ) -> None:
        self.stargift = stargift

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.stargift)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stargift = r.read_vector()
        self = cls.__new__(cls)
        self.stargift = stargift
        return self
