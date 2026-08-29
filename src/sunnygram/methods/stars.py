# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Telegram Stars beyond paying with them.

payments.py covers the transaction: an invoice goes out, Stars come back, and
either side can refund. This is everything around that, which is a ledger, a
shop, a subscription book and a payout desk, all hung off the same handful of
calls.

Four things worth knowing before reading any of it.

A balance belongs to a peer, not to the session. An account has one and so does
every channel it administers, and they are separate purses, so nearly every
call here takes a peer and defaults to the account rather than assuming it.

Stars and TON are the same calls with a flag. Telegram added a second currency
to the revenue side rather than a second set of methods, so the withdrawal, the
statistics and the transaction lookup all carry `ton` and mean a different
balance when it is set. It is a flag here too, because splitting them would be
inventing a distinction the server does not make.

A subscription can be cancelled from either end and the two are different calls
with different arguments. The subscriber cancels their own by id; a bot cancels
one it is owed by charge, and can put it back. Both spellings are here under
names that say which end you are standing at.

Withdrawing needs the account password, and needs it as a proof rather than as
a string. That is what `password_proof` in account.py is for, and it is why the
withdrawal call here asks for a password and not for a token.
"""

from __future__ import annotations

from typing import Any

from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import functions, types
from .account import password_proof

__all__ = [
    "cancel_bot_subscription",
    "cancel_stars_subscription",
    "connect_referral_bot",
    "fulfill_stars_subscription",
    "referral_bot",
    "referral_bots",
    "resume_stars_subscription",
    "revoke_referral_link",
    "stars_ads_url",
    "stars_gift_options",
    "stars_giveaway_options",
    "stars_revenue_stats",
    "stars_subscriptions",
    "stars_topup_options",
    "stars_transactions_by_id",
    "stars_withdrawal_url",
    "suggested_referral_bots",
]


async def stars_topup_options(invoker: Invoker) -> Any:
    """The bundles of Stars this account can buy, and what each costs.

    Prices are per store and per country, so this is asked rather than known,
    and the amounts come back in the smallest unit of the currency named
    beside them.
    """
    return await invoker.invoke(functions.payments.GetStarsTopupOptions())


async def stars_gift_options(invoker: Invoker, user: Target | None = None) -> Any:
    """The bundles that can be bought for somebody else.

    Naming the recipient can change what is offered, since not every bundle is
    available everywhere. Leaving them out asks what is on offer in general.
    """
    who = None if user is None else as_user(await resolve(invoker, user))
    return await invoker.invoke(functions.payments.GetStarsGiftOptions(user_id=who))


async def stars_giveaway_options(invoker: Invoker) -> Any:
    """The bundles that can be put up as a giveaway prize."""
    return await invoker.invoke(functions.payments.GetStarsGiveawayOptions())


async def stars_subscriptions(
    invoker: Invoker,
    peer: Target = "me",
    *,
    unpaid_only: bool = False,
    offset: str = "",
) -> Any:
    """The recurring Stars charges a peer is signed up to.

    unpaid_only narrows it to the ones that could not be collected, which is
    the list worth showing somebody: a subscription whose charge failed is
    about to lapse and nothing else says so.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetStarsSubscriptions(
            peer=where, missing_balance=unpaid_only, offset=offset
        )
    )


async def cancel_stars_subscription(
    invoker: Invoker, subscription_id: str, peer: Target = "me"
) -> bool:
    """Stop paying for a subscription, from the subscriber's end.

    What is already paid for runs to the end of its period. This is the call a
    person makes about their own subscription; a bot cancelling one it is owed
    wants cancel_bot_subscription, which is a different call with a different
    handle on the same thing.
    """
    where = await resolve(invoker, peer)
    return bool(
        await invoker.invoke(
            functions.payments.ChangeStarsSubscription(
                peer=where, subscription_id=subscription_id, canceled=True
            )
        )
    )


async def resume_stars_subscription(
    invoker: Invoker, subscription_id: str, peer: Target = "me"
) -> bool:
    """Undo a cancellation, while the period already paid for is still running.

    Past the end of that period there is nothing to resume and the answer is a
    refusal, not a new subscription.
    """
    where = await resolve(invoker, peer)
    return bool(
        await invoker.invoke(
            functions.payments.ChangeStarsSubscription(
                peer=where, subscription_id=subscription_id, canceled=False
            )
        )
    )


async def fulfill_stars_subscription(
    invoker: Invoker, subscription_id: str, peer: Target = "me"
) -> bool:
    """Pay a charge that was missed, once the balance can cover it.

    A subscription whose charge failed sits unpaid rather than lapsing at once.
    Topping the balance up does not retry it by itself, which is the part that
    surprises people: this is the retry.
    """
    where = await resolve(invoker, peer)
    return bool(
        await invoker.invoke(
            functions.payments.FulfillStarsSubscription(
                peer=where, subscription_id=subscription_id
            )
        )
    )


async def cancel_bot_subscription(
    invoker: Invoker, user: Target, charge_id: str, *, restore: bool = False
) -> bool:
    """Cancel a subscription a bot is being paid for, or put it back.

    The handle here is the charge id off the payment, not the subscription id,
    because a bot knows about the charge it received and not about the
    subscriber's list. restore=True undoes it while the paid period lasts.
    """
    where = await resolve(invoker, user)
    return bool(
        await invoker.invoke(
            functions.payments.BotCancelStarsSubscription(
                user_id=as_user(where), charge_id=charge_id, restore=restore
            )
        )
    )


async def stars_revenue_stats(
    invoker: Invoker, peer: Target = "me", *, ton: bool = False, dark: bool = False
) -> Any:
    """Earnings for a peer, as figures and as graphs to be loaded separately.

    The graphs come back as tokens rather than data, the same as the other
    statistics in this library, so load_graph turns one into something to draw.
    dark asks for the dark-theme rendering of those graphs and changes nothing
    else. ton reads the other balance.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetStarsRevenueStats(peer=where, ton=ton, dark=dark)
    )


async def stars_withdrawal_url(
    invoker: Invoker,
    password: str,
    peer: Target = "me",
    *,
    amount: int | None = None,
    ton: bool = False,
) -> str:
    """A one-time link for taking earnings out, which needs the password.

    The password is proved rather than sent (see password_proof), so nothing
    here or on the wire carries it. The link that comes back is short-lived and
    single-use, and it is the whole of the authority to move the money, so it
    belongs nowhere a log or a traceback can reach.

    amount is in whole Stars and may be left out for the TON side, which
    withdraws the lot.
    """
    where = await resolve(invoker, peer)
    proof = await password_proof(invoker, password)
    answer = await invoker.invoke(
        functions.payments.GetStarsRevenueWithdrawalUrl(
            peer=where, amount=amount, password=proof, ton=ton
        )
    )
    return str(answer.url)


async def stars_ads_url(invoker: Invoker, peer: Target = "me") -> str:
    """A link into the ad platform, for spending earnings rather than taking them."""
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.payments.GetStarsRevenueAdsAccountUrl(peer=where)
    )
    return str(answer.url)


async def stars_transactions_by_id(
    invoker: Invoker, ids: list[str], peer: Target = "me", *, ton: bool = False
) -> Any:
    """Look up particular ledger entries, rather than paging the whole ledger.

    For reconciling against ids written down elsewhere, which is what a program
    keeping its own books actually needs and what paging the ledger is a poor
    way to do.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetStarsTransactionsByID(
            peer=where,
            id=[types.InputStarsTransaction(id=one) for one in ids],
            ton=ton,
        )
    )


async def referral_bots(
    invoker: Invoker,
    peer: Target = "me",
    *,
    limit: int = 100,
    before: int | None = None,
    before_link: str | None = None,
) -> Any:
    """The affiliate programs this peer has joined, newest first.

    before and before_link are the pair the server pages by, and they travel
    together: the date on its own is not enough to place a cursor when two were
    joined in the same second.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetConnectedStarRefBots(
            peer=where, limit=limit, offset_date=before, offset_link=before_link
        )
    )


async def referral_bot(invoker: Invoker, bot: Target, peer: Target = "me") -> Any:
    """One affiliate program, if this peer has joined it."""
    where = await resolve(invoker, peer)
    which = await resolve(invoker, bot)
    return await invoker.invoke(
        functions.payments.GetConnectedStarRefBot(peer=where, bot=as_user(which))
    )


async def suggested_referral_bots(
    invoker: Invoker,
    peer: Target = "me",
    *,
    by: str = "revenue",
    offset: str = "",
    limit: int = 100,
) -> Any:
    """Programs on offer that this peer has not joined.

    by is "revenue" for the ones paying most, "date" for the newest, or
    "default" to take the server's own order.
    """
    if by not in ("revenue", "date", "default"):
        raise ValueError(
            f'suggested referral bots are ordered by "revenue", "date" or '
            f'"default", not {by!r}'
        )
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.GetSuggestedStarRefBots(
            peer=where,
            order_by_revenue=by == "revenue",
            order_by_date=by == "date",
            offset=offset,
            limit=limit,
        )
    )


async def connect_referral_bot(invoker: Invoker, bot: Target, peer: Target = "me") -> Any:
    """Join an affiliate program, which mints the link that earns the commission."""
    where = await resolve(invoker, peer)
    which = await resolve(invoker, bot)
    return await invoker.invoke(
        functions.payments.ConnectStarRefBot(peer=where, bot=as_user(which))
    )


async def revoke_referral_link(invoker: Invoker, link: str, peer: Target = "me") -> Any:
    """Give up an affiliate link, which stops it earning and cannot be undone.

    The program can be joined again afterwards, and doing so mints a different
    link: whatever was printed or posted with the old one is spent.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.payments.EditConnectedStarRefBot(peer=where, link=link, revoked=True)
    )
