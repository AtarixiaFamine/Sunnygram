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

## Subscriptions

A recurring Stars charge can be stopped from either end, and the two are different
calls with different handles on the same thing. A subscriber knows the subscription
id; a bot knows the charge id off the payment it received.

```python
subs = await app.get_stars_subscriptions()                 # what I pay for
await app.cancel_stars_subscription(subscription_id)       # the subscriber's end
await app.resume_stars_subscription(subscription_id)       # while the period lasts
await app.cancel_bot_subscription(user, charge_id)         # the bot's end
```

A charge that could not be collected leaves the subscription unpaid rather than
lapsing. Topping up the balance does not retry it by itself, which is the part that
surprises people:

```python
unpaid = await app.get_stars_subscriptions(unpaid_only=True)
await app.fulfill_stars_subscription(subscription_id)      # the retry
```

## Earnings

Every one of these takes a peer and defaults to the account, because a channel has
its own purse and it is not the same one.

```python
stats = await app.get_stars_revenue_stats(channel)
graph = await app.load_graph(stats.revenue_graph)          # graphs are tokens
url = await app.get_stars_withdrawal_url(password, channel, amount=1000)
```

The password is proved, not sent: nothing in the library or on the wire carries it.
The link that comes back is short-lived, single-use, and the whole of the authority
to move the money, so it belongs nowhere a log can reach.

TON is the same calls with `ton=True`. Telegram added a second currency to the
revenue side rather than a second set of methods, so it is a flag here too.

```python
await app.get_stars_revenue_stats(channel, ton=True)
await app.get_stars_transactions_by_id(["tx-1", "tx-2"])   # reconcile by id
```

## Affiliate programs

```python
offers = await app.get_suggested_referral_bots(by="revenue")   # or "date", "default"
joined = await app.connect_referral_bot(bot)
mine = await app.get_referral_bots()
await app.revoke_referral_link(link)
```

Revoking cannot be undone. The program can be joined again and doing so mints a
different link, so whatever was printed or posted with the old one is spent.

## Gifts

Three things to know before the list, because all three are places to go wrong quietly.

**A gift is named three ways and every method takes all of them.** An int is the
message a gift arrived in; an int with a peer beside it is a channel's saved id; a
string is the slug of an upgraded gift, with or without the link around it.

```python
await app.hide_gift(message_id)              # a gift I was sent
await app.hide_gift(saved_id, channel)       # a gift my channel was sent
await app.get_unique_gift("t.me/nft/plushpepe-42")
```

**Anything that spends money says so in its name.** Every method called `send_` or
`buy_` fetches a payment form and submits it, and the Stars leave the balance without
another prompt. Everything else costs nothing.

```python
await app.send_gift(user, gift_id, message="happy birthday", with_upgrade=True)
await app.upgrade_gift(message_id)           # free: the sender paid for it
await app.buy_gift_upgrade(message_id)       # pays, because nobody did
await app.transfer_gift(message_id, friend)  # free while the window lasts
await app.buy_gift_transfer(message_id, friend)
```

**One schema call does five things, so there are five methods.**

```python
c = await app.create_gift_collection("Favourites", [msg_a, msg_b])
await app.rename_gift_collection(c.collection_id, "Best")
await app.add_to_gift_collection(c.collection_id, [msg_c])
await app.remove_from_gift_collection(c.collection_id, [msg_a])
await app.reorder_gift_collection(c.collection_id, [msg_c, msg_b])
```

Browsing, owning and selling on:

```python
shop = await app.get_gift_catalogue()
mine = await app.get_saved_gifts(shown_only=True)
await app.show_gift(message_id)              # onto the public shelf
await app.convert_gift(message_id)           # back into Stars, and gone
await app.set_gift_resale_price(message_id, 500)   # 0 unlists it
listed = await app.get_resale_gifts(gift_id, by="price")
await app.buy_resale_gift(slug, to=friend)
```

Auctions, offers and crafting are wrapped too: `get_gift_auctions`,
`get_gift_auction_state`, `bid_on_gift_auction`, `send_gift_offer`,
`accept_gift_offer`, `decline_gift_offer`, `get_craftable_gifts` and `craft_gift`.

Taking an upgraded gift out to the blockchain needs the account password, which is
proved rather than sent, the same as the Stars withdrawal above:

```python
url = await app.get_gift_withdrawal_url(slug, password)
```

## What is not here

Giveaways, premium gift codes and the business account surface are not wrapped yet.
They are [one `app.invoke` away](raw-api.md) and fully typed, like anything else
unwrapped.
