"""A shop: invoices, the two questions, and being paid.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... SUNNYGRAM_BOT_TOKEN=... \\
        python examples/shop.py

    # to sell for money rather than Stars, add the provider token from BotFather
    SUNNYGRAM_PROVIDER_TOKEN=... python examples/shop.py

Write /buy to the bot and it sends an invoice. Pay it and it says so.

Two things here are worth watching rather than reading about.

The first is the pre-checkout handler. Telegram gives it about ten seconds, and
an unanswered query is not an error anybody sees: it is a customer whose payment
quietly fails. So it answers first and does everything else afterwards, and that
ordering is the whole lesson.

The second is that the two invoice kinds are different builders. A Stars invoice
has no provider and no token because there is nothing to connect; a currency
invoice needs both. Running this without a provider token sells for Stars.

Options:

    --session   which session file to use
    --stars     price in Stars (default 50)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from sunnygram import Client, filters, methods
from sunnygram.types import Price

SESSION_FILE = "sunnygram-shop.session"

# What we are selling, and the order this run knows about. A real shop keeps
# this in a database and looks it up by the payload; the payload is the point,
# since it is the only thing that comes back on every question about an order.
CATALOGUE = {
    b"order-hat": ("A very good hat", "Wool, one size, ships from Rome"),
}


def build(provider: str | None, stars: int) -> Any:
    """The invoice, of whichever kind this run can send."""
    title, description = CATALOGUE[b"order-hat"]
    if provider:
        return methods.as_invoice(
            title,
            description,
            currency="EUR",
            # In the smallest unit: 2500 is 25.00, not 2500 euros. This is the
            # mistake to make once.
            prices=[Price("Hat", 2500)],
            payload=b"order-hat",
            provider=provider,
            # Without this no shipping query is ever sent, and the handler
            # below would simply never run.
            flexible=True,
        )
    return methods.as_stars_invoice(
        title, description, amount=stars, payload=b"order-hat"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default=SESSION_FILE)
    parser.add_argument("--stars", type=int, default=50)
    options = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    token = os.environ.get("SUNNYGRAM_BOT_TOKEN")
    if not (api_id and api_hash and token):
        print(
            "set SUNNYGRAM_API_ID, SUNNYGRAM_API_HASH and SUNNYGRAM_BOT_TOKEN",
            file=sys.stderr,
        )
        return 1
    provider = os.environ.get("SUNNYGRAM_PROVIDER_TOKEN")

    app = Client(options.session, api_id=int(api_id), api_hash=api_hash)

    @app.on_message(filters.command("buy"))
    async def buy(client: Client, message: Any) -> None:
        await client.send_invoice(
            message.chat_id, build(provider, options.stars)
        )

    @app.on_shipping()
    async def deliver(client: Client, query: Any) -> None:
        """Only ever arrives for a flexible invoice, so never for Stars."""
        if query.country != "IT":
            await query.fail("We only ship within Italy")
            return
        await query.answer(
            [
                methods.shipping_option(
                    "std", "Standard, 3 days", [Price("Post", 500)]
                ),
                methods.shipping_option("fast", "Next day", [Price("Post", 1500)]),
            ]
        )

    @app.on_pre_checkout()
    async def confirm(client: Client, query: Any) -> None:
        """Answer first. Everything else afterwards.

        Ten seconds, and past them the payment fails on the customer's side
        with nothing said here. Anything slow, a database write above all,
        belongs after the answer and not before it.
        """
        if query.payload not in CATALOGUE:
            await query.reject("That item is no longer for sale")
            return
        await query.approve()

    @app.on_message()
    async def paid(client: Client, message: Any) -> None:
        """A successful payment is a service message, not an update of its own."""
        payment = message.payment
        if payment is None:
            return
        print(
            f"paid: {payment.total_amount} {payment.currency} "
            f"for {payment.payload!r}"
        )
        if payment.refundable:
            # Only the seller's reading carries the charge id, which is what a
            # refund needs. Worth keeping.
            print(f"  charge {payment.charge_id}")
        await message.respond("Thank you. Your hat is on its way.")

    print("selling. Write /buy to the bot. Ctrl-C to stop.")
    app.run(bot_token=token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
