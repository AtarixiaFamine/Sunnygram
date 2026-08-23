# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Money: invoices, the two questions a bot is asked, and what was paid.

Selling something through Telegram is a short conversation with a hard deadline
in the middle of it. A bot sends an invoice; the person fills it in; Telegram
asks the bot to confirm shipping options, and then asks it to confirm the whole
order. That second question has about ten seconds to be answered, and an
unanswered one is not an error anybody sees. It is a customer whose payment
quietly fails, and the money never moves.

So the two query types here answer themselves instead of making the caller
find the right call, and answering is the thing they make easiest to do.

Amounts are always in the currency's smallest unit: 1099 is 10.99 in a currency
with two decimal places, and Stars have none, so 50 Stars is 50.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..raw import types

__all__ = [
    "PreCheckoutQuery",
    "Price",
    "ShippingQuery",
    "SuccessfulPayment",
]


@dataclass(frozen=True, slots=True)
class Price:
    """One line on an invoice.

    The amount is in the smallest unit of the currency, so a thing costing
    10.99 is 1099. Getting this wrong by a factor of a hundred is the classic
    mistake here and Telegram cannot catch it for you.
    """

    label: str
    amount: int

    def to_raw(self) -> types.LabeledPrice:
        return types.LabeledPrice(label=self.label, amount=self.amount)

    @classmethod
    def from_raw(cls, raw: Any) -> Price:
        return cls(label=raw.label, amount=raw.amount)


@dataclass(frozen=True, slots=True)
class ShippingQuery:
    """Telegram asking what delivery would cost for this address.

    Only arrives for an invoice sent with flexible on. Answer it with the
    options available, or with an error saying why there are none: an address
    you do not ship to is a refusal with a reason, not silence.
    """

    query_id: int
    user_id: int
    payload: bytes
    address: Any = None
    _client: Any = field(default=None, repr=False, compare=False)
    raw: Any = None

    def __repr__(self) -> str:
        return f"ShippingQuery({self.query_id}, user {self.user_id})"

    @property
    def country(self) -> str:
        """The two-letter country code, which is what most rules key on."""
        return getattr(self.address, "country_iso2", "") or ""

    async def answer(self, options: list[Any]) -> bool:
        """Offer these delivery options."""
        return bool(
            await self._acting().answer_shipping(self.query_id, options=options)
        )

    async def fail(self, error: str) -> bool:
        """Say why this order cannot be delivered. The text is shown."""
        return bool(await self._acting().answer_shipping(self.query_id, error=error))

    def _acting(self) -> Any:
        if self._client is None:
            raise RuntimeError("this query did not come from a client")
        return self._client

    @classmethod
    def from_raw(cls, update: Any, *, client: Any = None) -> ShippingQuery | None:
        if not isinstance(update, types.UpdateBotShippingQuery):
            return None
        return cls(
            query_id=update.query_id,
            user_id=update.user_id,
            payload=update.payload,
            address=update.shipping_address,
            _client=client,
            raw=update,
        )


@dataclass(frozen=True, slots=True)
class PreCheckoutQuery:
    """The last question before the money moves, and it is on a clock.

    Telegram gives roughly ten seconds for an answer. Past that the payment
    fails on the customer's side with nothing said to the bot, so a handler for
    this should do the least work it can and answer: check the payload against
    what is still in stock, approve or reject, and do the slow part afterwards.
    """

    query_id: int
    user_id: int
    payload: bytes
    currency: str
    total_amount: int
    info: Any = None
    shipping_option_id: str | None = None
    _client: Any = field(default=None, repr=False, compare=False)
    raw: Any = None

    def __repr__(self) -> str:
        return (
            f"PreCheckoutQuery({self.query_id}, {self.total_amount} "
            f"{self.currency}, user {self.user_id})"
        )

    async def approve(self) -> bool:
        """Let the payment go through."""
        return bool(
            await self._acting().answer_pre_checkout(self.query_id, ok=True)
        )

    async def reject(self, error: str) -> bool:
        """Stop the payment, and say why. The text is shown to the customer."""
        return bool(
            await self._acting().answer_pre_checkout(
                self.query_id, ok=False, error=error
            )
        )

    def _acting(self) -> Any:
        if self._client is None:
            raise RuntimeError("this query did not come from a client")
        return self._client

    @classmethod
    def from_raw(cls, update: Any, *, client: Any = None) -> PreCheckoutQuery | None:
        if not isinstance(update, types.UpdateBotPrecheckoutQuery):
            return None
        return cls(
            query_id=update.query_id,
            user_id=update.user_id,
            payload=update.payload,
            currency=update.currency,
            total_amount=update.total_amount,
            info=update.info,
            shipping_option_id=update.shipping_option_id,
            _client=client,
            raw=update,
        )


@dataclass(frozen=True, slots=True)
class SuccessfulPayment:
    """A payment that went through, as it arrives on a service message.

    Two constructors carry this and they are not the same. The bot that sold
    the thing gets the one with the charge id on it, which is what a refund
    needs; everybody else in the chat gets the version without. charge_id being
    empty means this reading is the second kind.
    """

    currency: str
    total_amount: int
    payload: bytes = b""
    charge_id: str = ""
    provider_charge_id: str = ""
    info: Any = None
    shipping_option_id: str | None = None
    recurring: bool = False
    raw: Any = None

    def __repr__(self) -> str:
        return f"SuccessfulPayment({self.total_amount} {self.currency})"

    @property
    def refundable(self) -> bool:
        """Whether this reading carries what a refund needs."""
        return bool(self.charge_id)

    @classmethod
    def from_raw(cls, action: Any) -> SuccessfulPayment | None:
        """Read either payment action, or None for anything else."""
        if isinstance(action, types.MessageActionPaymentSentMe):
            return cls(
                currency=action.currency,
                total_amount=action.total_amount,
                payload=action.payload,
                charge_id=action.charge.id,
                provider_charge_id=action.charge.provider_charge_id,
                info=action.info,
                shipping_option_id=action.shipping_option_id,
                recurring=action.recurring_init or action.recurring_used,
                raw=action,
            )
        if isinstance(action, types.MessageActionPaymentSent):
            return cls(
                currency=action.currency,
                total_amount=action.total_amount,
                recurring=action.recurring_init or action.recurring_used,
                raw=action,
            )
        return None
