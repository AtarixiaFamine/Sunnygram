# Payments and Stars

Two ways to be paid, which look alike and are not. A **currency invoice** goes
through a payment provider connected in BotFather, needs that provider's token, and
asks the customer for a card. A **Stars invoice** has no provider and no token,
because there is nothing to connect: the customer is moving Stars they already hold.

Amounts are always in the currency's smallest unit. `1099` is 10.99 where the
currency has two decimal places. Stars have none, so 50 Stars is `50`.

## The one deadline

A pre-checkout query has roughly **ten seconds** to be answered. Past that the
payment fails on the customer's side and nothing at all is said on yours.

That shapes how a handler should be written: check what has to be checked, answer,
and do the bookkeeping afterwards.

```python
@app.on_pre_checkout()
async def confirm(client, query):
    if not still_in_stock(query.payload):
        await query.reject("That sold out while you were checking out")
        return
    await query.approve()          # answer first
    await record_the_order(query)  # then take your time
```

Answering is the one place in this library where a failure is logged at error rather
than passed over. Nothing above will hear about it and the customer will not either.

## Selling for money

```python
from sunnygram import methods
from sunnygram.types import Price

invoice = methods.as_invoice(
    "A very good hat",
    "Wool, one size",
    currency="EUR",
    prices=[Price("Hat", 2500), Price("Postage", 500)],
    payload=b"order-1041",
    provider="<the token from BotFather>",
    flexible=True,          # ask me what delivery costs
)
await app.send_invoice(chat, invoice)
```

`payload` is yours. It comes back on every question about this order and on the
payment itself, and never reaches the customer, so it is where the order id goes.

`flexible=True` is what makes Telegram ask a shipping query at all. Without it no
shipping query is ever sent, however many handlers are waiting for one.

```python
from sunnygram import methods

@app.on_shipping()
async def deliver(client, query):
    if query.country != "IT":
        await query.fail("We only ship within Italy")
        return
    await query.answer([
        methods.shipping_option("std", "Standard, 3 days", [Price("Post", 500)]),
        methods.shipping_option("fast", "Next day", [Price("Post", 1500)]),
    ])
```

## Selling for Stars

```python
invoice = methods.as_stars_invoice(
    "A month of access",
    "Everything, for thirty days",
    amount=50,                  # fifty Stars
    payload=b"sub-1041",
)
await app.send_invoice(chat, invoice)
```

No provider, no token, no card. `subscription_period=2592000` makes it recur monthly,
which is the only period Telegram takes today.

## Being paid

A successful payment arrives as a **service message**, not as an update of its own:

```python
@app.on_message()
async def paid(client, message):
    payment = message.payment
    if payment is None:
        return
    print(f"{payment.total_amount} {payment.currency} for {payment.payload!r}")
```

Two constructors carry this and they differ in one important way. The bot that sold
the thing gets the reading with the charge id on it; everybody else in the chat gets
the one without. `payment.refundable` says which you are holding.

## The Stars ledger

```python
balance = await app.get_stars_balance()
statement = await app.get_stars_transactions(limit=50)
await app.refund_stars(user, charge_id)      # charge_id off the payment
```

`get_stars_balance` gives whole Stars. The wire carries a fractional part in
billionths for the exchange rate's sake, which nothing a bot does with a balance
needs.

## What is not here

Gifts, giveaways, star-gift auctions and affiliate programs all exist in the schema
and none of them is wrapped. They are [one `app.invoke` away](raw-api.md) and fully
typed, like anything else unwrapped.
