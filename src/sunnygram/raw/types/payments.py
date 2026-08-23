# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the payments namespace.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class PaymentForm(TLObject):
    """The TL type payments.paymentForm#a0058751, a form of payments.PaymentForm."""

    __slots__ = ("can_save_credentials", "password_missing", "form_id", "bot_id", "title", "description", "photo", "invoice", "provider_id", "url", "native_provider", "native_params", "additional_methods", "saved_info", "saved_credentials", "users",)

    ID = 0xA0058751
    QUALNAME = "types.payments.PaymentForm"

    def __init__(
        self,
        *,
        can_save_credentials: bool = False,
        password_missing: bool = False,
        form_id: int,
        bot_id: int,
        title: str,
        description: str,
        photo: base.WebDocument | None = None,
        invoice: base.Invoice,
        provider_id: int,
        url: str,
        native_provider: str | None = None,
        native_params: base.DataJSON | None = None,
        additional_methods: list[base.PaymentFormMethod] | None = None,
        saved_info: base.PaymentRequestedInfo | None = None,
        saved_credentials: list[base.PaymentSavedCredentials] | None = None,
        users: list[base.User],
    ) -> None:
        self.can_save_credentials = can_save_credentials
        self.password_missing = password_missing
        self.form_id = form_id
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.provider_id = provider_id
        self.url = url
        self.native_provider = native_provider
        self.native_params = native_params
        self.additional_methods = additional_methods
        self.saved_info = saved_info
        self.saved_credentials = saved_credentials
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.can_save_credentials:
            flags |= 1 << 2
        if self.password_missing:
            flags |= 1 << 3
        if self.photo is not None:
            flags |= 1 << 5
        if self.native_provider is not None:
            flags |= 1 << 4
        if self.native_params is not None:
            flags |= 1 << 4
        if self.additional_methods is not None:
            flags |= 1 << 6
        if self.saved_info is not None:
            flags |= 1 << 0
        if self.saved_credentials is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_long(self.form_id)
        w.write_long(self.bot_id)
        w.write_string(self.title)
        w.write_string(self.description)
        if self.photo is not None:
            self.photo.write(w)
        self.invoice.write(w)
        w.write_long(self.provider_id)
        w.write_string(self.url)
        if self.native_provider is not None:
            w.write_string(self.native_provider)
        if self.native_params is not None:
            self.native_params.write(w)
        if self.additional_methods is not None:
            w.write_vector(self.additional_methods)
        if self.saved_info is not None:
            self.saved_info.write(w)
        if self.saved_credentials is not None:
            w.write_vector(self.saved_credentials)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        can_save_credentials = bool(flags & (1 << 2))
        password_missing = bool(flags & (1 << 3))
        form_id = r.read_long()
        bot_id = r.read_long()
        title = r.read_string()
        description = r.read_string()
        photo = r.read_object() if flags & (1 << 5) else None
        invoice = r.read_object()
        provider_id = r.read_long()
        url = r.read_string()
        native_provider = r.read_string() if flags & (1 << 4) else None
        native_params = r.read_object() if flags & (1 << 4) else None
        additional_methods = r.read_vector() if flags & (1 << 6) else None
        saved_info = r.read_object() if flags & (1 << 0) else None
        saved_credentials = r.read_vector() if flags & (1 << 1) else None
        users = r.read_vector()
        self = cls.__new__(cls)
        self.can_save_credentials = can_save_credentials
        self.password_missing = password_missing
        self.form_id = form_id
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.provider_id = provider_id
        self.url = url
        self.native_provider = native_provider
        self.native_params = native_params
        self.additional_methods = additional_methods
        self.saved_info = saved_info
        self.saved_credentials = saved_credentials
        self.users = users
        return self


class PaymentFormStars(TLObject):
    """The TL type payments.paymentFormStars#7bf6b15c, a form of payments.PaymentForm."""

    __slots__ = ("form_id", "bot_id", "title", "description", "photo", "invoice", "users",)

    ID = 0x7BF6B15C
    QUALNAME = "types.payments.PaymentFormStars"

    def __init__(
        self,
        *,
        form_id: int,
        bot_id: int,
        title: str,
        description: str,
        photo: base.WebDocument | None = None,
        invoice: base.Invoice,
        users: list[base.User],
    ) -> None:
        self.form_id = form_id
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.photo is not None:
            flags |= 1 << 5
        w.write_int(flags)
        w.write_long(self.form_id)
        w.write_long(self.bot_id)
        w.write_string(self.title)
        w.write_string(self.description)
        if self.photo is not None:
            self.photo.write(w)
        self.invoice.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        form_id = r.read_long()
        bot_id = r.read_long()
        title = r.read_string()
        description = r.read_string()
        photo = r.read_object() if flags & (1 << 5) else None
        invoice = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.form_id = form_id
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.users = users
        return self


class PaymentFormStarGift(TLObject):
    """The TL type payments.paymentFormStarGift#b425cfe1, a form of payments.PaymentForm."""

    __slots__ = ("form_id", "invoice",)

    ID = 0xB425CFE1
    QUALNAME = "types.payments.PaymentFormStarGift"

    def __init__(
        self,
        *,
        form_id: int,
        invoice: base.Invoice,
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


class ValidatedRequestedInfo(TLObject):
    """The TL type payments.validatedRequestedInfo#d1451883, a form of payments.ValidatedRequestedInfo."""

    __slots__ = ("id", "shipping_options",)

    ID = 0xD1451883
    QUALNAME = "types.payments.ValidatedRequestedInfo"

    def __init__(
        self,
        *,
        id: str | None = None,
        shipping_options: list[base.ShippingOption] | None = None,
    ) -> None:
        self.id = id
        self.shipping_options = shipping_options

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.id is not None:
            flags |= 1 << 0
        if self.shipping_options is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.id is not None:
            w.write_string(self.id)
        if self.shipping_options is not None:
            w.write_vector(self.shipping_options)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        id = r.read_string() if flags & (1 << 0) else None
        shipping_options = r.read_vector() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.id = id
        self.shipping_options = shipping_options
        return self


class PaymentResult(TLObject):
    """The TL type payments.paymentResult#4e5f810d, a form of payments.PaymentResult."""

    __slots__ = ("updates",)

    ID = 0x4E5F810D
    QUALNAME = "types.payments.PaymentResult"

    def __init__(
        self,
        *,
        updates: base.Updates,
    ) -> None:
        self.updates = updates

    def write_body(self, w: TLWriter) -> None:
        self.updates.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        updates = r.read_object()
        self = cls.__new__(cls)
        self.updates = updates
        return self


class PaymentVerificationNeeded(TLObject):
    """The TL type payments.paymentVerificationNeeded#d8411139, a form of payments.PaymentResult."""

    __slots__ = ("url",)

    ID = 0xD8411139
    QUALNAME = "types.payments.PaymentVerificationNeeded"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class PaymentReceipt(TLObject):
    """The TL type payments.paymentReceipt#70c4fe03, a form of payments.PaymentReceipt."""

    __slots__ = ("date", "bot_id", "provider_id", "title", "description", "photo", "invoice", "info", "shipping", "tip_amount", "currency", "total_amount", "credentials_title", "users",)

    ID = 0x70C4FE03
    QUALNAME = "types.payments.PaymentReceipt"

    def __init__(
        self,
        *,
        date: int,
        bot_id: int,
        provider_id: int,
        title: str,
        description: str,
        photo: base.WebDocument | None = None,
        invoice: base.Invoice,
        info: base.PaymentRequestedInfo | None = None,
        shipping: base.ShippingOption | None = None,
        tip_amount: int | None = None,
        currency: str,
        total_amount: int,
        credentials_title: str,
        users: list[base.User],
    ) -> None:
        self.date = date
        self.bot_id = bot_id
        self.provider_id = provider_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.info = info
        self.shipping = shipping
        self.tip_amount = tip_amount
        self.currency = currency
        self.total_amount = total_amount
        self.credentials_title = credentials_title
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.photo is not None:
            flags |= 1 << 2
        if self.info is not None:
            flags |= 1 << 0
        if self.shipping is not None:
            flags |= 1 << 1
        if self.tip_amount is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_int(self.date)
        w.write_long(self.bot_id)
        w.write_long(self.provider_id)
        w.write_string(self.title)
        w.write_string(self.description)
        if self.photo is not None:
            self.photo.write(w)
        self.invoice.write(w)
        if self.info is not None:
            self.info.write(w)
        if self.shipping is not None:
            self.shipping.write(w)
        if self.tip_amount is not None:
            w.write_long(self.tip_amount)
        w.write_string(self.currency)
        w.write_long(self.total_amount)
        w.write_string(self.credentials_title)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        date = r.read_int()
        bot_id = r.read_long()
        provider_id = r.read_long()
        title = r.read_string()
        description = r.read_string()
        photo = r.read_object() if flags & (1 << 2) else None
        invoice = r.read_object()
        info = r.read_object() if flags & (1 << 0) else None
        shipping = r.read_object() if flags & (1 << 1) else None
        tip_amount = r.read_long() if flags & (1 << 3) else None
        currency = r.read_string()
        total_amount = r.read_long()
        credentials_title = r.read_string()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.date = date
        self.bot_id = bot_id
        self.provider_id = provider_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.info = info
        self.shipping = shipping
        self.tip_amount = tip_amount
        self.currency = currency
        self.total_amount = total_amount
        self.credentials_title = credentials_title
        self.users = users
        return self


class PaymentReceiptStars(TLObject):
    """The TL type payments.paymentReceiptStars#dabbf83a, a form of payments.PaymentReceipt."""

    __slots__ = ("date", "bot_id", "title", "description", "photo", "invoice", "currency", "total_amount", "transaction_id", "users",)

    ID = 0xDABBF83A
    QUALNAME = "types.payments.PaymentReceiptStars"

    def __init__(
        self,
        *,
        date: int,
        bot_id: int,
        title: str,
        description: str,
        photo: base.WebDocument | None = None,
        invoice: base.Invoice,
        currency: str,
        total_amount: int,
        transaction_id: str,
        users: list[base.User],
    ) -> None:
        self.date = date
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.currency = currency
        self.total_amount = total_amount
        self.transaction_id = transaction_id
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.photo is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.date)
        w.write_long(self.bot_id)
        w.write_string(self.title)
        w.write_string(self.description)
        if self.photo is not None:
            self.photo.write(w)
        self.invoice.write(w)
        w.write_string(self.currency)
        w.write_long(self.total_amount)
        w.write_string(self.transaction_id)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        date = r.read_int()
        bot_id = r.read_long()
        title = r.read_string()
        description = r.read_string()
        photo = r.read_object() if flags & (1 << 2) else None
        invoice = r.read_object()
        currency = r.read_string()
        total_amount = r.read_long()
        transaction_id = r.read_string()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.date = date
        self.bot_id = bot_id
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.currency = currency
        self.total_amount = total_amount
        self.transaction_id = transaction_id
        self.users = users
        return self


class SavedInfo(TLObject):
    """The TL type payments.savedInfo#fb8fe43c, a form of payments.SavedInfo."""

    __slots__ = ("has_saved_credentials", "saved_info",)

    ID = 0xFB8FE43C
    QUALNAME = "types.payments.SavedInfo"

    def __init__(
        self,
        *,
        has_saved_credentials: bool = False,
        saved_info: base.PaymentRequestedInfo | None = None,
    ) -> None:
        self.has_saved_credentials = has_saved_credentials
        self.saved_info = saved_info

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.has_saved_credentials:
            flags |= 1 << 1
        if self.saved_info is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.saved_info is not None:
            self.saved_info.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        has_saved_credentials = bool(flags & (1 << 1))
        saved_info = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.has_saved_credentials = has_saved_credentials
        self.saved_info = saved_info
        return self


class BankCardData(TLObject):
    """The TL type payments.bankCardData#3e24e573, a form of payments.BankCardData."""

    __slots__ = ("title", "open_urls",)

    ID = 0x3E24E573
    QUALNAME = "types.payments.BankCardData"

    def __init__(
        self,
        *,
        title: str,
        open_urls: list[base.BankCardOpenUrl],
    ) -> None:
        self.title = title
        self.open_urls = open_urls

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.title)
        w.write_vector(self.open_urls)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        title = r.read_string()
        open_urls = r.read_vector()
        self = cls.__new__(cls)
        self.title = title
        self.open_urls = open_urls
        return self


class ExportedInvoice(TLObject):
    """The TL type payments.exportedInvoice#aed0cbd9, a form of payments.ExportedInvoice."""

    __slots__ = ("url",)

    ID = 0xAED0CBD9
    QUALNAME = "types.payments.ExportedInvoice"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class CheckedGiftCode(TLObject):
    """The TL type payments.checkedGiftCode#eb983f8f, a form of payments.CheckedGiftCode."""

    __slots__ = ("via_giveaway", "from_id", "giveaway_msg_id", "to_id", "date", "days", "used_date", "chats", "users",)

    ID = 0xEB983F8F
    QUALNAME = "types.payments.CheckedGiftCode"

    def __init__(
        self,
        *,
        via_giveaway: bool = False,
        from_id: base.Peer | None = None,
        giveaway_msg_id: int | None = None,
        to_id: int | None = None,
        date: int,
        days: int,
        used_date: int | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.via_giveaway = via_giveaway
        self.from_id = from_id
        self.giveaway_msg_id = giveaway_msg_id
        self.to_id = to_id
        self.date = date
        self.days = days
        self.used_date = used_date
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.via_giveaway:
            flags |= 1 << 2
        if self.from_id is not None:
            flags |= 1 << 4
        if self.giveaway_msg_id is not None:
            flags |= 1 << 3
        if self.to_id is not None:
            flags |= 1 << 0
        if self.used_date is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.from_id is not None:
            self.from_id.write(w)
        if self.giveaway_msg_id is not None:
            w.write_int(self.giveaway_msg_id)
        if self.to_id is not None:
            w.write_long(self.to_id)
        w.write_int(self.date)
        w.write_int(self.days)
        if self.used_date is not None:
            w.write_int(self.used_date)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        via_giveaway = bool(flags & (1 << 2))
        from_id = r.read_object() if flags & (1 << 4) else None
        giveaway_msg_id = r.read_int() if flags & (1 << 3) else None
        to_id = r.read_long() if flags & (1 << 0) else None
        date = r.read_int()
        days = r.read_int()
        used_date = r.read_int() if flags & (1 << 1) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.via_giveaway = via_giveaway
        self.from_id = from_id
        self.giveaway_msg_id = giveaway_msg_id
        self.to_id = to_id
        self.date = date
        self.days = days
        self.used_date = used_date
        self.chats = chats
        self.users = users
        return self


class GiveawayInfo(TLObject):
    """The TL type payments.giveawayInfo#4367daa0, a form of payments.GiveawayInfo."""

    __slots__ = ("participating", "preparing_results", "start_date", "joined_too_early_date", "admin_disallowed_chat_id", "disallowed_country",)

    ID = 0x4367DAA0
    QUALNAME = "types.payments.GiveawayInfo"

    def __init__(
        self,
        *,
        participating: bool = False,
        preparing_results: bool = False,
        start_date: int,
        joined_too_early_date: int | None = None,
        admin_disallowed_chat_id: int | None = None,
        disallowed_country: str | None = None,
    ) -> None:
        self.participating = participating
        self.preparing_results = preparing_results
        self.start_date = start_date
        self.joined_too_early_date = joined_too_early_date
        self.admin_disallowed_chat_id = admin_disallowed_chat_id
        self.disallowed_country = disallowed_country

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.participating:
            flags |= 1 << 0
        if self.preparing_results:
            flags |= 1 << 3
        if self.joined_too_early_date is not None:
            flags |= 1 << 1
        if self.admin_disallowed_chat_id is not None:
            flags |= 1 << 2
        if self.disallowed_country is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_int(self.start_date)
        if self.joined_too_early_date is not None:
            w.write_int(self.joined_too_early_date)
        if self.admin_disallowed_chat_id is not None:
            w.write_long(self.admin_disallowed_chat_id)
        if self.disallowed_country is not None:
            w.write_string(self.disallowed_country)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        participating = bool(flags & (1 << 0))
        preparing_results = bool(flags & (1 << 3))
        start_date = r.read_int()
        joined_too_early_date = r.read_int() if flags & (1 << 1) else None
        admin_disallowed_chat_id = r.read_long() if flags & (1 << 2) else None
        disallowed_country = r.read_string() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.participating = participating
        self.preparing_results = preparing_results
        self.start_date = start_date
        self.joined_too_early_date = joined_too_early_date
        self.admin_disallowed_chat_id = admin_disallowed_chat_id
        self.disallowed_country = disallowed_country
        return self


class GiveawayInfoResults(TLObject):
    """The TL type payments.giveawayInfoResults#e175e66f, a form of payments.GiveawayInfo."""

    __slots__ = ("winner", "refunded", "start_date", "gift_code_slug", "stars_prize", "finish_date", "winners_count", "activated_count",)

    ID = 0xE175E66F
    QUALNAME = "types.payments.GiveawayInfoResults"

    def __init__(
        self,
        *,
        winner: bool = False,
        refunded: bool = False,
        start_date: int,
        gift_code_slug: str | None = None,
        stars_prize: int | None = None,
        finish_date: int,
        winners_count: int,
        activated_count: int | None = None,
    ) -> None:
        self.winner = winner
        self.refunded = refunded
        self.start_date = start_date
        self.gift_code_slug = gift_code_slug
        self.stars_prize = stars_prize
        self.finish_date = finish_date
        self.winners_count = winners_count
        self.activated_count = activated_count

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.winner:
            flags |= 1 << 0
        if self.refunded:
            flags |= 1 << 1
        if self.gift_code_slug is not None:
            flags |= 1 << 3
        if self.stars_prize is not None:
            flags |= 1 << 4
        if self.activated_count is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.start_date)
        if self.gift_code_slug is not None:
            w.write_string(self.gift_code_slug)
        if self.stars_prize is not None:
            w.write_long(self.stars_prize)
        w.write_int(self.finish_date)
        w.write_int(self.winners_count)
        if self.activated_count is not None:
            w.write_int(self.activated_count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        winner = bool(flags & (1 << 0))
        refunded = bool(flags & (1 << 1))
        start_date = r.read_int()
        gift_code_slug = r.read_string() if flags & (1 << 3) else None
        stars_prize = r.read_long() if flags & (1 << 4) else None
        finish_date = r.read_int()
        winners_count = r.read_int()
        activated_count = r.read_int() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.winner = winner
        self.refunded = refunded
        self.start_date = start_date
        self.gift_code_slug = gift_code_slug
        self.stars_prize = stars_prize
        self.finish_date = finish_date
        self.winners_count = winners_count
        self.activated_count = activated_count
        return self


class StarsStatus(TLObject):
    """The TL type payments.starsStatus#6c9ce8ed, a form of payments.StarsStatus."""

    __slots__ = ("balance", "subscriptions", "subscriptions_next_offset", "subscriptions_missing_balance", "history", "next_offset", "chats", "users",)

    ID = 0x6C9CE8ED
    QUALNAME = "types.payments.StarsStatus"

    def __init__(
        self,
        *,
        balance: base.StarsAmount,
        subscriptions: list[base.StarsSubscription] | None = None,
        subscriptions_next_offset: str | None = None,
        subscriptions_missing_balance: int | None = None,
        history: list[base.StarsTransaction] | None = None,
        next_offset: str | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.balance = balance
        self.subscriptions = subscriptions
        self.subscriptions_next_offset = subscriptions_next_offset
        self.subscriptions_missing_balance = subscriptions_missing_balance
        self.history = history
        self.next_offset = next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.subscriptions is not None:
            flags |= 1 << 1
        if self.subscriptions_next_offset is not None:
            flags |= 1 << 2
        if self.subscriptions_missing_balance is not None:
            flags |= 1 << 4
        if self.history is not None:
            flags |= 1 << 3
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.balance.write(w)
        if self.subscriptions is not None:
            w.write_vector(self.subscriptions)
        if self.subscriptions_next_offset is not None:
            w.write_string(self.subscriptions_next_offset)
        if self.subscriptions_missing_balance is not None:
            w.write_long(self.subscriptions_missing_balance)
        if self.history is not None:
            w.write_vector(self.history)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        balance = r.read_object()
        subscriptions = r.read_vector() if flags & (1 << 1) else None
        subscriptions_next_offset = r.read_string() if flags & (1 << 2) else None
        subscriptions_missing_balance = r.read_long() if flags & (1 << 4) else None
        history = r.read_vector() if flags & (1 << 3) else None
        next_offset = r.read_string() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.balance = balance
        self.subscriptions = subscriptions
        self.subscriptions_next_offset = subscriptions_next_offset
        self.subscriptions_missing_balance = subscriptions_missing_balance
        self.history = history
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        return self


class StarsRevenueStats(TLObject):
    """The TL type payments.starsRevenueStats#6c207376, a form of payments.StarsRevenueStats."""

    __slots__ = ("top_hours_graph", "revenue_graph", "status", "usd_rate",)

    ID = 0x6C207376
    QUALNAME = "types.payments.StarsRevenueStats"

    def __init__(
        self,
        *,
        top_hours_graph: base.StatsGraph | None = None,
        revenue_graph: base.StatsGraph,
        status: base.StarsRevenueStatus,
        usd_rate: float,
    ) -> None:
        self.top_hours_graph = top_hours_graph
        self.revenue_graph = revenue_graph
        self.status = status
        self.usd_rate = usd_rate

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_hours_graph is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.top_hours_graph is not None:
            self.top_hours_graph.write(w)
        self.revenue_graph.write(w)
        self.status.write(w)
        w.write_double(self.usd_rate)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        top_hours_graph = r.read_object() if flags & (1 << 0) else None
        revenue_graph = r.read_object()
        status = r.read_object()
        usd_rate = r.read_double()
        self = cls.__new__(cls)
        self.top_hours_graph = top_hours_graph
        self.revenue_graph = revenue_graph
        self.status = status
        self.usd_rate = usd_rate
        return self


class StarsRevenueWithdrawalUrl(TLObject):
    """The TL type payments.starsRevenueWithdrawalUrl#1dab80b7, a form of payments.StarsRevenueWithdrawalUrl."""

    __slots__ = ("url",)

    ID = 0x1DAB80B7
    QUALNAME = "types.payments.StarsRevenueWithdrawalUrl"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class StarsRevenueAdsAccountUrl(TLObject):
    """The TL type payments.starsRevenueAdsAccountUrl#394e7f21, a form of payments.StarsRevenueAdsAccountUrl."""

    __slots__ = ("url",)

    ID = 0x394E7F21
    QUALNAME = "types.payments.StarsRevenueAdsAccountUrl"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class StarGiftsNotModified(TLObject):
    """The TL type payments.starGiftsNotModified#a388a368, a form of payments.StarGifts."""

    __slots__ = ()

    ID = 0xA388A368
    QUALNAME = "types.payments.StarGiftsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class StarGifts(TLObject):
    """The TL type payments.starGifts#2ed82995, a form of payments.StarGifts."""

    __slots__ = ("hash", "gifts", "chats", "users",)

    ID = 0x2ED82995
    QUALNAME = "types.payments.StarGifts"

    def __init__(
        self,
        *,
        hash: int,
        gifts: list[base.StarGift],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.hash = hash
        self.gifts = gifts
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        w.write_vector(self.gifts)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        gifts = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.gifts = gifts
        self.chats = chats
        self.users = users
        return self


class ConnectedStarRefBots(TLObject):
    """The TL type payments.connectedStarRefBots#98d5ea1d, a form of payments.ConnectedStarRefBots."""

    __slots__ = ("count", "connected_bots", "users",)

    ID = 0x98D5EA1D
    QUALNAME = "types.payments.ConnectedStarRefBots"

    def __init__(
        self,
        *,
        count: int,
        connected_bots: list[base.ConnectedBotStarRef],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.connected_bots = connected_bots
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.connected_bots)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        connected_bots = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.connected_bots = connected_bots
        self.users = users
        return self


class SuggestedStarRefBots(TLObject):
    """The TL type payments.suggestedStarRefBots#b4d5d859, a form of payments.SuggestedStarRefBots."""

    __slots__ = ("count", "suggested_bots", "users", "next_offset",)

    ID = 0xB4D5D859
    QUALNAME = "types.payments.SuggestedStarRefBots"

    def __init__(
        self,
        *,
        count: int,
        suggested_bots: list[base.StarRefProgram],
        users: list[base.User],
        next_offset: str | None = None,
    ) -> None:
        self.count = count
        self.suggested_bots = suggested_bots
        self.users = users
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.suggested_bots)
        w.write_vector(self.users)
        if self.next_offset is not None:
            w.write_string(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        suggested_bots = r.read_vector()
        users = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.count = count
        self.suggested_bots = suggested_bots
        self.users = users
        self.next_offset = next_offset
        return self


class StarGiftUpgradePreview(TLObject):
    """The TL type payments.starGiftUpgradePreview#3de1dfed, a form of payments.StarGiftUpgradePreview."""

    __slots__ = ("sample_attributes", "prices", "next_prices",)

    ID = 0x3DE1DFED
    QUALNAME = "types.payments.StarGiftUpgradePreview"

    def __init__(
        self,
        *,
        sample_attributes: list[base.StarGiftAttribute],
        prices: list[base.StarGiftUpgradePrice],
        next_prices: list[base.StarGiftUpgradePrice],
    ) -> None:
        self.sample_attributes = sample_attributes
        self.prices = prices
        self.next_prices = next_prices

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.sample_attributes)
        w.write_vector(self.prices)
        w.write_vector(self.next_prices)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sample_attributes = r.read_vector()
        prices = r.read_vector()
        next_prices = r.read_vector()
        self = cls.__new__(cls)
        self.sample_attributes = sample_attributes
        self.prices = prices
        self.next_prices = next_prices
        return self


class UniqueStarGift(TLObject):
    """The TL type payments.uniqueStarGift#416c56e8, a form of payments.UniqueStarGift."""

    __slots__ = ("gift", "chats", "users",)

    ID = 0x416C56E8
    QUALNAME = "types.payments.UniqueStarGift"

    def __init__(
        self,
        *,
        gift: base.StarGift,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.gift = gift
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.gift.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.gift = gift
        self.chats = chats
        self.users = users
        return self


class SavedStarGifts(TLObject):
    """The TL type payments.savedStarGifts#95f389b1, a form of payments.SavedStarGifts."""

    __slots__ = ("count", "chat_notifications_enabled", "gifts", "next_offset", "chats", "users",)

    ID = 0x95F389B1
    QUALNAME = "types.payments.SavedStarGifts"

    def __init__(
        self,
        *,
        count: int,
        chat_notifications_enabled: bool | None = None,
        gifts: list[base.SavedStarGift],
        next_offset: str | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.chat_notifications_enabled = chat_notifications_enabled
        self.gifts = gifts
        self.next_offset = next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.chat_notifications_enabled is not None:
            flags |= 1 << 1
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        if self.chat_notifications_enabled is not None:
            w.write_bool(self.chat_notifications_enabled)
        w.write_vector(self.gifts)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        chat_notifications_enabled = r.read_bool() if flags & (1 << 1) else None
        gifts = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.chat_notifications_enabled = chat_notifications_enabled
        self.gifts = gifts
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        return self


class StarGiftWithdrawalUrl(TLObject):
    """The TL type payments.starGiftWithdrawalUrl#84aa3a9c, a form of payments.StarGiftWithdrawalUrl."""

    __slots__ = ("url",)

    ID = 0x84AA3A9C
    QUALNAME = "types.payments.StarGiftWithdrawalUrl"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class ResaleStarGifts(TLObject):
    """The TL type payments.resaleStarGifts#947a12df, a form of payments.ResaleStarGifts."""

    __slots__ = ("count", "gifts", "next_offset", "attributes", "attributes_hash", "chats", "counters", "users",)

    ID = 0x947A12DF
    QUALNAME = "types.payments.ResaleStarGifts"

    def __init__(
        self,
        *,
        count: int,
        gifts: list[base.StarGift],
        next_offset: str | None = None,
        attributes: list[base.StarGiftAttribute] | None = None,
        attributes_hash: int | None = None,
        chats: list[base.Chat],
        counters: list[base.StarGiftAttributeCounter] | None = None,
        users: list[base.User],
    ) -> None:
        self.count = count
        self.gifts = gifts
        self.next_offset = next_offset
        self.attributes = attributes
        self.attributes_hash = attributes_hash
        self.chats = chats
        self.counters = counters
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        if self.attributes is not None:
            flags |= 1 << 1
        if self.attributes_hash is not None:
            flags |= 1 << 1
        if self.counters is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.gifts)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        if self.attributes is not None:
            w.write_vector(self.attributes)
        if self.attributes_hash is not None:
            w.write_long(self.attributes_hash)
        w.write_vector(self.chats)
        if self.counters is not None:
            w.write_vector(self.counters)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        gifts = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        attributes = r.read_vector() if flags & (1 << 1) else None
        attributes_hash = r.read_long() if flags & (1 << 1) else None
        chats = r.read_vector()
        counters = r.read_vector() if flags & (1 << 2) else None
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.gifts = gifts
        self.next_offset = next_offset
        self.attributes = attributes
        self.attributes_hash = attributes_hash
        self.chats = chats
        self.counters = counters
        self.users = users
        return self


class StarGiftCollectionsNotModified(TLObject):
    """The TL type payments.starGiftCollectionsNotModified#a0ba4f17, a form of payments.StarGiftCollections."""

    __slots__ = ()

    ID = 0xA0BA4F17
    QUALNAME = "types.payments.StarGiftCollectionsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class StarGiftCollections(TLObject):
    """The TL type payments.starGiftCollections#8a2932f3, a form of payments.StarGiftCollections."""

    __slots__ = ("collections",)

    ID = 0x8A2932F3
    QUALNAME = "types.payments.StarGiftCollections"

    def __init__(
        self,
        *,
        collections: list[base.StarGiftCollection],
    ) -> None:
        self.collections = collections

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.collections)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        collections = r.read_vector()
        self = cls.__new__(cls)
        self.collections = collections
        return self


class UniqueStarGiftValueInfo(TLObject):
    """The TL type payments.uniqueStarGiftValueInfo#512fe446, a form of payments.UniqueStarGiftValueInfo."""

    __slots__ = ("last_sale_on_fragment", "value_is_average", "currency", "value", "initial_sale_date", "initial_sale_stars", "initial_sale_price", "last_sale_date", "last_sale_price", "floor_price", "average_price", "listed_count", "fragment_listed_count", "fragment_listed_url",)

    ID = 0x512FE446
    QUALNAME = "types.payments.UniqueStarGiftValueInfo"

    def __init__(
        self,
        *,
        last_sale_on_fragment: bool = False,
        value_is_average: bool = False,
        currency: str,
        value: int,
        initial_sale_date: int,
        initial_sale_stars: int,
        initial_sale_price: int,
        last_sale_date: int | None = None,
        last_sale_price: int | None = None,
        floor_price: int | None = None,
        average_price: int | None = None,
        listed_count: int | None = None,
        fragment_listed_count: int | None = None,
        fragment_listed_url: str | None = None,
    ) -> None:
        self.last_sale_on_fragment = last_sale_on_fragment
        self.value_is_average = value_is_average
        self.currency = currency
        self.value = value
        self.initial_sale_date = initial_sale_date
        self.initial_sale_stars = initial_sale_stars
        self.initial_sale_price = initial_sale_price
        self.last_sale_date = last_sale_date
        self.last_sale_price = last_sale_price
        self.floor_price = floor_price
        self.average_price = average_price
        self.listed_count = listed_count
        self.fragment_listed_count = fragment_listed_count
        self.fragment_listed_url = fragment_listed_url

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.last_sale_on_fragment:
            flags |= 1 << 1
        if self.value_is_average:
            flags |= 1 << 6
        if self.last_sale_date is not None:
            flags |= 1 << 0
        if self.last_sale_price is not None:
            flags |= 1 << 0
        if self.floor_price is not None:
            flags |= 1 << 2
        if self.average_price is not None:
            flags |= 1 << 3
        if self.listed_count is not None:
            flags |= 1 << 4
        if self.fragment_listed_count is not None:
            flags |= 1 << 5
        if self.fragment_listed_url is not None:
            flags |= 1 << 5
        w.write_int(flags)
        w.write_string(self.currency)
        w.write_long(self.value)
        w.write_int(self.initial_sale_date)
        w.write_long(self.initial_sale_stars)
        w.write_long(self.initial_sale_price)
        if self.last_sale_date is not None:
            w.write_int(self.last_sale_date)
        if self.last_sale_price is not None:
            w.write_long(self.last_sale_price)
        if self.floor_price is not None:
            w.write_long(self.floor_price)
        if self.average_price is not None:
            w.write_long(self.average_price)
        if self.listed_count is not None:
            w.write_int(self.listed_count)
        if self.fragment_listed_count is not None:
            w.write_int(self.fragment_listed_count)
        if self.fragment_listed_url is not None:
            w.write_string(self.fragment_listed_url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        last_sale_on_fragment = bool(flags & (1 << 1))
        value_is_average = bool(flags & (1 << 6))
        currency = r.read_string()
        value = r.read_long()
        initial_sale_date = r.read_int()
        initial_sale_stars = r.read_long()
        initial_sale_price = r.read_long()
        last_sale_date = r.read_int() if flags & (1 << 0) else None
        last_sale_price = r.read_long() if flags & (1 << 0) else None
        floor_price = r.read_long() if flags & (1 << 2) else None
        average_price = r.read_long() if flags & (1 << 3) else None
        listed_count = r.read_int() if flags & (1 << 4) else None
        fragment_listed_count = r.read_int() if flags & (1 << 5) else None
        fragment_listed_url = r.read_string() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.last_sale_on_fragment = last_sale_on_fragment
        self.value_is_average = value_is_average
        self.currency = currency
        self.value = value
        self.initial_sale_date = initial_sale_date
        self.initial_sale_stars = initial_sale_stars
        self.initial_sale_price = initial_sale_price
        self.last_sale_date = last_sale_date
        self.last_sale_price = last_sale_price
        self.floor_price = floor_price
        self.average_price = average_price
        self.listed_count = listed_count
        self.fragment_listed_count = fragment_listed_count
        self.fragment_listed_url = fragment_listed_url
        return self


class CheckCanSendGiftResultOk(TLObject):
    """The TL type payments.checkCanSendGiftResultOk#374fa7ad, a form of payments.CheckCanSendGiftResult."""

    __slots__ = ()

    ID = 0x374FA7AD
    QUALNAME = "types.payments.CheckCanSendGiftResultOk"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CheckCanSendGiftResultFail(TLObject):
    """The TL type payments.checkCanSendGiftResultFail#d5e58274, a form of payments.CheckCanSendGiftResult."""

    __slots__ = ("reason",)

    ID = 0xD5E58274
    QUALNAME = "types.payments.CheckCanSendGiftResultFail"

    def __init__(
        self,
        *,
        reason: base.TextWithEntities,
    ) -> None:
        self.reason = reason

    def write_body(self, w: TLWriter) -> None:
        self.reason.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        reason = r.read_object()
        self = cls.__new__(cls)
        self.reason = reason
        return self


class StarGiftAuctionState(TLObject):
    """The TL type payments.starGiftAuctionState#6b39f4ec, a form of payments.StarGiftAuctionState."""

    __slots__ = ("gift", "state", "user_state", "timeout", "users", "chats",)

    ID = 0x6B39F4EC
    QUALNAME = "types.payments.StarGiftAuctionState"

    def __init__(
        self,
        *,
        gift: base.StarGift,
        state: base.StarGiftAuctionState,
        user_state: base.StarGiftAuctionUserState,
        timeout: int,
        users: list[base.User],
        chats: list[base.Chat],
    ) -> None:
        self.gift = gift
        self.state = state
        self.user_state = user_state
        self.timeout = timeout
        self.users = users
        self.chats = chats

    def write_body(self, w: TLWriter) -> None:
        self.gift.write(w)
        self.state.write(w)
        self.user_state.write(w)
        w.write_int(self.timeout)
        w.write_vector(self.users)
        w.write_vector(self.chats)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gift = r.read_object()
        state = r.read_object()
        user_state = r.read_object()
        timeout = r.read_int()
        users = r.read_vector()
        chats = r.read_vector()
        self = cls.__new__(cls)
        self.gift = gift
        self.state = state
        self.user_state = user_state
        self.timeout = timeout
        self.users = users
        self.chats = chats
        return self


class StarGiftAuctionAcquiredGifts(TLObject):
    """The TL type payments.starGiftAuctionAcquiredGifts#7d5bd1f0, a form of payments.StarGiftAuctionAcquiredGifts."""

    __slots__ = ("gifts", "users", "chats",)

    ID = 0x7D5BD1F0
    QUALNAME = "types.payments.StarGiftAuctionAcquiredGifts"

    def __init__(
        self,
        *,
        gifts: list[base.StarGiftAuctionAcquiredGift],
        users: list[base.User],
        chats: list[base.Chat],
    ) -> None:
        self.gifts = gifts
        self.users = users
        self.chats = chats

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.gifts)
        w.write_vector(self.users)
        w.write_vector(self.chats)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        gifts = r.read_vector()
        users = r.read_vector()
        chats = r.read_vector()
        self = cls.__new__(cls)
        self.gifts = gifts
        self.users = users
        self.chats = chats
        return self


class StarGiftActiveAuctionsNotModified(TLObject):
    """The TL type payments.starGiftActiveAuctionsNotModified#db33dad0, a form of payments.StarGiftActiveAuctions."""

    __slots__ = ()

    ID = 0xDB33DAD0
    QUALNAME = "types.payments.StarGiftActiveAuctionsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class StarGiftActiveAuctions(TLObject):
    """The TL type payments.starGiftActiveAuctions#aef6abbc, a form of payments.StarGiftActiveAuctions."""

    __slots__ = ("auctions", "users", "chats",)

    ID = 0xAEF6ABBC
    QUALNAME = "types.payments.StarGiftActiveAuctions"

    def __init__(
        self,
        *,
        auctions: list[base.StarGiftActiveAuctionState],
        users: list[base.User],
        chats: list[base.Chat],
    ) -> None:
        self.auctions = auctions
        self.users = users
        self.chats = chats

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.auctions)
        w.write_vector(self.users)
        w.write_vector(self.chats)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        auctions = r.read_vector()
        users = r.read_vector()
        chats = r.read_vector()
        self = cls.__new__(cls)
        self.auctions = auctions
        self.users = users
        self.chats = chats
        return self


class StarGiftUpgradeAttributes(TLObject):
    """The TL type payments.starGiftUpgradeAttributes#46c6e36f, a form of payments.StarGiftUpgradeAttributes."""

    __slots__ = ("attributes",)

    ID = 0x46C6E36F
    QUALNAME = "types.payments.StarGiftUpgradeAttributes"

    def __init__(
        self,
        *,
        attributes: list[base.StarGiftAttribute],
    ) -> None:
        self.attributes = attributes

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.attributes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        attributes = r.read_vector()
        self = cls.__new__(cls)
        self.attributes = attributes
        return self
