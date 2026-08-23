# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Selling things, and Telegram Stars.

Two halves that look alike and are not. A currency invoice goes through a
payment provider, needs a provider token, and asks the customer for a card. A
Stars invoice has no provider and no token, because Stars are already in the
account: the customer approves a balance transfer. Telegram spells the
difference as an empty currency string and an empty provider, which is easy to
get half right, so the two are separate functions here, not one with a
flag.

Rule S7, added with this module: an unanswered pre-checkout query is a payment
that fails silently. Answering is on a timer of about ten seconds, so the
answer path never swallows an exception. If the answer cannot be delivered it
is logged at error, because nothing above will hear about it and the customer
certainly will not.
"""

from __future__ import annotations

import logging
from typing import Any

from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import base, functions, types

__all__ = [
    "STARS",
    "answer_pre_checkout",
    "answer_shipping",
    "as_invoice",
    "as_stars_invoice",
    "payment_form",
    "refund_stars",
    "send_stars_form",
    "shipping_option",
    "stars_balance",
    "stars_transactions",
]

_log = logging.getLogger(__name__)

# What Telegram calls its own currency on the wire. A Stars invoice is spelled
# as this with no provider and no token, and Stars have no decimal places, so an
# amount is a whole number of them.
STARS = "XTR"


def _prices(prices: list[Any]) -> list[base.LabeledPrice]:
    """Take Price objects or raw labeled prices, indifferently."""
    return [
        one if isinstance(one, types.LabeledPrice) else one.to_raw() for one in prices
    ]


def as_invoice(
    title: str,
    description: str,
    *,
    currency: str,
    prices: list[Any],
    payload: bytes,
    provider: str,
    provider_data: str = "{}",
    photo_url: str | None = None,
    start_param: str | None = None,
    test: bool = False,
    name_requested: bool = False,
    phone_requested: bool = False,
    email_requested: bool = False,
    shipping_address_requested: bool = False,
    flexible: bool = False,
    max_tip_amount: int | None = None,
    suggested_tip_amounts: list[int] | None = None,
) -> base.InputMedia:
    """Build an invoice to be sent with send_media.

    An invoice is a kind of media instead of a call of its own, which is why
    it is built here and sent by the same function that sends a photo.

    payload is yours and comes back on every question about this order and on
    the payment itself. It never reaches the customer, so it is the right place
    to put the order id.

    provider is the token from the payment provider connected through BotFather.
    Stars do not use one: see as_stars_invoice.

    flexible says delivery cost depends on the address, which makes
    Telegram ask a shipping query at all. Without it no shipping query arrives
    however many handlers are waiting for one.
    """
    if not currency:
        raise ValueError("an invoice needs a currency; for Stars use as_stars_invoice")
    if not prices:
        raise ValueError("an invoice needs at least one price")
    return types.InputMediaInvoice(
        title=title,
        description=description,
        invoice=types.Invoice(
            currency=currency,
            prices=_prices(prices),
            test=test,
            name_requested=name_requested,
            phone_requested=phone_requested,
            email_requested=email_requested,
            shipping_address_requested=shipping_address_requested,
            flexible=flexible,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
        ),
        payload=payload,
        provider=provider,
        provider_data=types.DataJSON(data=provider_data),
        photo=(
            None
            if photo_url is None
            else types.InputWebDocument(
                url=photo_url, size=0, mime_type="image/jpeg", attributes=[]
            )
        ),
        start_param=start_param,
    )


def as_stars_invoice(
    title: str,
    description: str,
    *,
    amount: int,
    payload: bytes,
    label: str = "",
    photo_url: str | None = None,
    start_param: str | None = None,
    subscription_period: int | None = None,
) -> base.InputMedia:
    """Build an invoice paid in Telegram Stars.

    No provider and no provider token, because there is no provider: the
    customer is moving Stars they already hold. amount is a whole number of
    Stars, since Stars have no smaller unit.

    subscription_period makes it a recurring charge, in seconds, and Telegram
    accepts only a month (2592000) today.
    """
    if amount <= 0:
        raise ValueError("a Stars invoice needs a positive amount")
    return types.InputMediaInvoice(
        title=title,
        description=description,
        invoice=types.Invoice(
            currency=STARS,
            prices=[types.LabeledPrice(label=label or title, amount=amount)],
            subscription_period=subscription_period,
        ),
        payload=payload,
        provider=None,
        provider_data=types.DataJSON(data="{}"),
        photo=(
            None
            if photo_url is None
            else types.InputWebDocument(
                url=photo_url, size=0, mime_type="image/jpeg", attributes=[]
            )
        ),
        start_param=start_param,
    )


def shipping_option(option_id: str, title: str, prices: list[Any]) -> types.ShippingOption:
    """One delivery choice to offer in answer to a shipping query."""
    return types.ShippingOption(id=option_id, title=title, prices=_prices(prices))


async def answer_shipping(
    invoker: Invoker,
    query_id: int,
    *,
    options: list[Any] | None = None,
    error: str | None = None,
) -> bool:
    """Answer a shipping query with options, or with a reason there are none.

    One or the other, not both and not neither: an unanswered query stalls the
    order at the delivery step.
    """
    if (options is None) == (error is None):
        raise ValueError("answer a shipping query with either options or an error")
    return bool(
        await invoker.invoke(
            functions.messages.SetBotShippingResults(
                query_id=query_id,
                error=error,
                shipping_options=None if options is None else list(options),
            )
        )
    )


async def answer_pre_checkout(
    invoker: Invoker,
    query_id: int,
    *,
    ok: bool = True,
    error: str | None = None,
) -> bool:
    """Approve or reject a payment, within about ten seconds of being asked.

    This is the last thing standing between a customer and a charge, and the
    window is short. Past it the payment fails on their side and nothing is
    said on this one, so a handler should answer first and do its bookkeeping
    afterwards.

    A rejection needs a reason, because the reason is shown to the customer and
    "an error occurred" is not one.

    Failing to deliver the answer is logged at error instead of passed over.
    Nothing above this will hear about it, and the money not moving is not the
    kind of thing that should be quiet (rules C3 and S7).
    """
    if not ok and not error:
        raise ValueError("a rejected payment needs a reason, which the customer sees")
    try:
        return bool(
            await invoker.invoke(
                functions.messages.SetBotPrecheckoutResults(
                    query_id=query_id, success=ok, error=error
                )
            )
        )
    except Exception:
        _log.exception(
            "could not answer pre-checkout query %s; the payment will fail for "
            "the customer with nothing shown to them",
            query_id,
        )
        raise


async def payment_form(invoker: Invoker, peer: Target, message_id: int) -> Any:
    """The form behind an invoice message, which is the buyer's side."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetPaymentForm(
            invoice=types.InputInvoiceMessage(peer=where, msg_id=message_id)
        )
    )


async def send_stars_form(
    invoker: Invoker, form_id: int, peer: Target, message_id: int
) -> Any:
    """Pay a Stars invoice, which needs no card and no provider."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.SendStarsForm(
            form_id=form_id,
            invoice=types.InputInvoiceMessage(peer=where, msg_id=message_id),
        )
    )


async def stars_balance(invoker: Invoker, peer: Target = "me") -> int:
    """How many Stars an account or a channel holds.

    The whole Stars, rounded down. The wire carries a fractional part in
    billionths for the exchange rate's sake, which nothing a bot does with a
    balance needs.
    """
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(functions.payments.GetStarsStatus(peer=where))
    balance = getattr(answer, "balance", None)
    if isinstance(balance, types.StarsAmount):
        return balance.amount
    return 0


async def stars_transactions(
    invoker: Invoker,
    peer: Target = "me",
    *,
    inbound: bool = False,
    outbound: bool = False,
    offset: str = "",
    limit: int = 100,
) -> Any:
    """The Stars ledger for an account, newest first.

    Saying neither inbound nor outbound gives both, which is what a statement
    usually means.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetStarsTransactions(
            peer=where,
            inbound=inbound,
            outbound=outbound,
            offset=offset,
            limit=limit,
        )
    )


async def refund_stars(invoker: Invoker, user: Target, charge_id: str) -> Any:
    """Give back a Stars payment.

    charge_id is the one off the successful payment, which only the bot that
    was paid receives.
    """
    where = await resolve(invoker, user)
    return await invoker.invoke(
        functions.payments.RefundStarsCharge(
            user_id=as_user(where), charge_id=charge_id
        )
    )
