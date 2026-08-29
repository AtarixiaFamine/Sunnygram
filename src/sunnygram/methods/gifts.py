# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Star gifts: buying them, keeping them, upgrading them, selling them on.

The largest surface in the payments namespace and the one with the most ways to
be got subtly wrong, so three conventions are worth reading before any of it.

**A gift is named three different ways and this module takes all of them.**
Telegram identifies a gift somebody owns by the service message it arrived in
if they are a person, by a saved id beside the channel if they are a channel,
and by a public slug once it has been upgraded into something transferable.
Every call here takes whichever the caller has: an int is a message id, an int
with a peer beside it is a channel's saved id, a string is a slug, and a raw
constructor passes straight through. Nothing has to know which spelling the
call underneath wanted.

**Anything that spends money says so in its name.** Half of these operations go
through an invoice, which means a payment form is fetched and then submitted,
and the Stars leave the balance without another prompt. Every one of those is
called send_ or buy_, and every method not called that costs nothing. Upgrading
is the pair that makes this matter: upgrade_gift spends nothing because the
upgrade was already paid for when the gift was sent, and buy_gift_upgrade pays
for one that was not. They are the same operation with different funding and
the names are the only thing that says which.

**One collection call does five things and is spelled as five methods.** The
schema updates a collection's title, adds gifts, removes gifts and reorders
them through one function with four optional lists. Passing four Nones and one
list is not an API, so there is a method per verb.
"""

from __future__ import annotations

import secrets
from typing import Any

from ..network import Invoker
from ..peers import Target, resolve
from ..raw import base, functions, types
from .account import password_proof

__all__ = [
    "accept_gift_offer",
    "add_to_gift_collection",
    "bid_on_gift_auction",
    "buy_gift_transfer",
    "buy_gift_upgrade",
    "buy_resale_gift",
    "can_send_gift",
    "convert_gift",
    "craft_gift",
    "craftable_gifts",
    "create_gift_collection",
    "decline_gift_offer",
    "delete_gift_collection",
    "gift_auction_gifts",
    "gift_auction_state",
    "gift_auctions",
    "gift_catalogue",
    "gift_collections",
    "gift_upgrade_attributes",
    "gift_upgrade_preview",
    "gift_withdrawal_url",
    "hide_gift",
    "pin_gifts",
    "remove_from_gift_collection",
    "rename_gift_collection",
    "reorder_gift_collection",
    "reorder_gift_collections",
    "resale_gifts",
    "saved_gift",
    "saved_gifts",
    "send_gift",
    "send_gift_offer",
    "set_gift_notifications",
    "set_gift_resale_price",
    "show_gift",
    "transfer_gift",
    "unique_gift",
    "unique_gift_value",
    "upgrade_gift",
]

# What people paste in front of a unique gift's slug. Same idea as the username
# normalizer next door: a link copied out of a client is the name with furniture
# around it, and the name is the part the call wants.
_SLUG_PREFIXES = ("https://t.me/nft/", "http://t.me/nft/", "t.me/nft/", "@")

# A gift given away rather than sold has no price, and the schema still wants a
# StarsAmount. Nanos are always zero here: Stars have no smaller unit, and the
# fractional part exists on the wire for exchange rates rather than for prices.
_NO_NANOS = 0


def _slug(text: str) -> str:
    """The slug out of whatever spelling of a gift link was handed over."""
    cleaned = text.strip()
    for prefix in _SLUG_PREFIXES:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    return cleaned.split("?", 1)[0].strip("/")


def stars(amount: int) -> types.StarsAmount:
    """A whole number of Stars, in the shape the schema asks a price in."""
    if amount < 0:
        raise ValueError("a price is not negative")
    return types.StarsAmount(amount=amount, nanos=_NO_NANOS)


async def _saved(
    invoker: Invoker, gift: Any, peer: Target | None = None
) -> base.InputSavedStarGift:
    """One gift somebody owns, from whichever way the caller happens to name it.

    The ambiguous case is an int, which is a message id for a gift a person
    received and a saved id for one a channel received, and the two are
    different constructors. What settles it is whether a peer was named beside
    it, because a channel's gift is only ever addressed with the channel.
    """
    if isinstance(gift, (types.InputSavedStarGiftUser, types.InputSavedStarGiftChat)):
        return gift
    if isinstance(gift, types.InputSavedStarGiftSlug):
        return gift
    if isinstance(gift, str):
        return types.InputSavedStarGiftSlug(slug=_slug(gift))
    if isinstance(gift, int):
        if peer is None:
            return types.InputSavedStarGiftUser(msg_id=gift)
        where = await resolve(invoker, peer)
        return types.InputSavedStarGiftChat(peer=where, saved_id=gift)
    raise TypeError(
        "a gift is named by the message it arrived in, by a slug, or by a "
        f"saved id with the chat it belongs to, not by {type(gift).__name__}"
    )


async def _saved_many(
    invoker: Invoker, gifts: Any, peer: Target | None = None
) -> list[base.InputSavedStarGift]:
    """The same for a list, since half of these calls take several at once."""
    if isinstance(gifts, (str, int)) or not hasattr(gifts, "__iter__"):
        gifts = [gifts]
    return [await _saved(invoker, one, peer) for one in gifts]


async def _pay(invoker: Invoker, invoice: base.InputInvoice) -> Any:
    """Fetch the form behind an invoice and submit it, which is what buying is.

    Every purchase in this module is these two calls. The form carries the
    price the server has decided on, which is why it cannot be skipped: the
    amount is not something the client gets to assert.

    Nothing here confirms anything with anybody. A caller reaching one of these
    has already decided to spend, which is why every one of them is named for
    spending.
    """
    form = await invoker.invoke(functions.payments.GetPaymentForm(invoice=invoice))
    return await invoker.invoke(
        functions.payments.SendStarsForm(form_id=form.form_id, invoice=invoice)
    )


def _text(message: str | None) -> base.TextWithEntities | None:
    """The note that travels with a gift, which is text and no formatting."""
    if not message:
        return None
    return types.TextWithEntities(text=message, entities=[])


# --- browsing ---------------------------------------------------------------


async def gift_catalogue(invoker: Invoker) -> Any:
    """Every gift on sale, which is the shop rather than anybody's shelf."""
    return await invoker.invoke(functions.payments.GetStarGifts(hash=0))


async def can_send_gift(invoker: Invoker, gift_id: int) -> Any:
    """Whether this account may send a particular gift, and why not if it may not.

    Worth asking before offering the button. A gift can be sold out, limited to
    a region, or restricted to accounts older than this one, and finding out by
    being refused mid-purchase is a worse way to learn it.
    """
    return await invoker.invoke(functions.payments.CheckCanSendGift(gift_id=gift_id))


async def gift_upgrade_preview(invoker: Invoker, gift_id: int) -> Any:
    """What a gift of this kind could turn into, before one is owned.

    Upgrading mints something with randomly drawn attributes, so this is the
    sample of what is in the pool rather than a promise about any one gift.
    """
    return await invoker.invoke(
        functions.payments.GetStarGiftUpgradePreview(gift_id=gift_id)
    )


async def gift_upgrade_attributes(invoker: Invoker, gift_id: int) -> Any:
    """The full attribute pool for a kind of gift, with how rare each one is."""
    return await invoker.invoke(
        functions.payments.GetStarGiftUpgradeAttributes(gift_id=gift_id)
    )


async def unique_gift(invoker: Invoker, slug: str) -> Any:
    """One upgraded gift by its public name, which anybody can look up."""
    return await invoker.invoke(
        functions.payments.GetUniqueStarGift(slug=_slug(slug))
    )


async def unique_gift_value(invoker: Invoker, slug: str) -> Any:
    """What an upgraded gift is reckoned to be worth, and what it last sold for."""
    return await invoker.invoke(
        functions.payments.GetUniqueStarGiftValueInfo(slug=_slug(slug))
    )


async def resale_gifts(
    invoker: Invoker,
    gift_id: int,
    *,
    by: str = "price",
    stars_only: bool = False,
    for_craft: bool = False,
    attributes: list[Any] | None = None,
    offset: str = "",
    limit: int = 100,
) -> Any:
    """Upgraded gifts of one kind that their owners have put up for sale.

    by is "price" for the cheapest first, "number" for the lowest mint number,
    or "default" to take the server's own order. stars_only leaves out the ones
    priced in TON.
    """
    if by not in ("price", "number", "default"):
        raise ValueError(
            f'resale gifts are sorted by "price", "number" or "default", not {by!r}'
        )
    return await invoker.invoke(
        functions.payments.GetResaleStarGifts(
            gift_id=gift_id,
            sort_by_price=by == "price",
            sort_by_num=by == "number",
            stars_only=stars_only,
            for_craft=for_craft,
            attributes=list(attributes) if attributes else None,
            offset=offset,
            limit=limit,
        )
    )


# --- what a peer owns -------------------------------------------------------


async def saved_gifts(
    invoker: Invoker,
    peer: Target = "me",
    *,
    collection_id: int | None = None,
    shown_only: bool = False,
    hidden_only: bool = False,
    upgradable_only: bool = False,
    exclude_upgraded: bool = False,
    exclude_unlimited: bool = False,
    exclude_hosted: bool = False,
    by_value: bool = False,
    offset: str = "",
    limit: int = 100,
) -> Any:
    """The gifts a peer holds, newest first unless sorted by value.

    Two shapes of filter here and the difference is the schema's, not a choice.
    Where a flag has a complement the pair is spelled as what to keep, so
    shown_only and hidden_only mean what they say, and asking for both is
    refused rather than sent: the server would answer it with nothing and the
    caller would read that as an empty shelf. Where the schema offers only one
    side, the argument keeps the exclude spelling, because "exclude_upgraded"
    is what it does and there is no flag that means only the upgraded ones.
    """
    if shown_only and hidden_only:
        raise ValueError("a gift is either shown or hidden, so asking for both is empty")
    return await invoker.invoke(
        functions.payments.GetSavedStarGifts(
            peer=await resolve(invoker, peer),
            collection_id=collection_id,
            exclude_unsaved=shown_only,
            exclude_saved=hidden_only,
            exclude_unupgradable=upgradable_only,
            exclude_unique=exclude_upgraded,
            exclude_unlimited=exclude_unlimited,
            exclude_hosted=exclude_hosted,
            sort_by_value=by_value,
            offset=offset,
            limit=limit,
        )
    )


async def saved_gift(
    invoker: Invoker, gifts: Any, peer: Target | None = None
) -> Any:
    """Particular gifts by their handles, rather than paging somebody's shelf."""
    return await invoker.invoke(
        functions.payments.GetSavedStarGift(
            stargift=await _saved_many(invoker, gifts, peer)
        )
    )


async def show_gift(invoker: Invoker, gift: Any, peer: Target | None = None) -> bool:
    """Put a gift on the public shelf, where anyone looking at the profile sees it."""
    return bool(
        await invoker.invoke(
            functions.payments.SaveStarGift(
                stargift=await _saved(invoker, gift, peer), unsave=False
            )
        )
    )


async def hide_gift(invoker: Invoker, gift: Any, peer: Target | None = None) -> bool:
    """Take a gift off the public shelf. It is still owned, just not displayed."""
    return bool(
        await invoker.invoke(
            functions.payments.SaveStarGift(
                stargift=await _saved(invoker, gift, peer), unsave=True
            )
        )
    )


async def convert_gift(invoker: Invoker, gift: Any, peer: Target | None = None) -> bool:
    """Turn a gift back into Stars, which destroys it.

    There is no way back and the Stars returned are fewer than the gift cost.
    Only ordinary gifts can be converted; once one has been upgraded it is a
    unique thing and this is refused.
    """
    return bool(
        await invoker.invoke(
            functions.payments.ConvertStarGift(
                stargift=await _saved(invoker, gift, peer)
            )
        )
    )


async def pin_gifts(invoker: Invoker, gifts: Any, peer: Target = "me") -> bool:
    """Set which gifts sit at the top of the shelf, in the order given.

    This is the whole pinned set rather than an addition to it, so passing one
    gift leaves exactly one pinned and passing none unpins everything.
    """
    return bool(
        await invoker.invoke(
            functions.payments.ToggleStarGiftsPinnedToTop(
                peer=await resolve(invoker, peer),
                stargift=await _saved_many(invoker, gifts, peer),
            )
        )
    )


async def set_gift_notifications(
    invoker: Invoker, peer: Target, enabled: bool = True
) -> bool:
    """Whether to be told when a channel this account runs is sent a gift."""
    return bool(
        await invoker.invoke(
            functions.payments.ToggleChatStarGiftNotifications(
                peer=await resolve(invoker, peer), enabled=enabled
            )
        )
    )


async def set_gift_resale_price(
    invoker: Invoker, gift: Any, amount: int, peer: Target | None = None
) -> Any:
    """Put an upgraded gift up for sale, or change what it is listed at.

    An amount of zero takes it off the market, which is the only way to unlist
    one: there is no separate call for it.
    """
    return await invoker.invoke(
        functions.payments.UpdateStarGiftPrice(
            stargift=await _saved(invoker, gift, peer), resell_amount=stars(amount)
        )
    )


async def gift_withdrawal_url(
    invoker: Invoker, gift: Any, password: str, peer: Target | None = None
) -> str:
    """A one-time link for taking an upgraded gift out to the blockchain.

    The password is proved rather than sent, the same as the Stars withdrawal
    next door. The link is short-lived, single-use, and the whole of the
    authority to move the gift, so it belongs nowhere a log can reach.
    """
    handle = await _saved(invoker, gift, peer)
    proof = await password_proof(invoker, password)
    answer = await invoker.invoke(
        functions.payments.GetStarGiftWithdrawalUrl(stargift=handle, password=proof)
    )
    return str(answer.url)


# --- spending ---------------------------------------------------------------


async def send_gift(
    invoker: Invoker,
    peer: Target,
    gift_id: int,
    *,
    message: str | None = None,
    anonymous: bool = False,
    with_upgrade: bool = False,
) -> Any:
    """Buy a gift and give it to somebody. This spends Stars.

    anonymous hides the sender's name from everyone but the recipient.
    with_upgrade pays for the upgrade at the same time, which is what lets the
    recipient upgrade later without paying themselves.
    """
    return await _pay(
        invoker,
        types.InputInvoiceStarGift(
            peer=await resolve(invoker, peer),
            gift_id=gift_id,
            message=_text(message),
            hide_name=anonymous,
            include_upgrade=with_upgrade,
        ),
    )


async def upgrade_gift(
    invoker: Invoker,
    gift: Any,
    peer: Target | None = None,
    *,
    keep_details: bool = False,
) -> Any:
    """Upgrade a gift whose upgrade was already paid for. This spends nothing.

    Only works when whoever sent it paid for the upgrade too. Otherwise the
    upgrade has to be bought, which is buy_gift_upgrade and is a different call
    because it costs money.

    keep_details leaves the sender's name and note attached to the upgraded
    gift, which cannot be undone afterwards.
    """
    return await invoker.invoke(
        functions.payments.UpgradeStarGift(
            stargift=await _saved(invoker, gift, peer),
            keep_original_details=keep_details,
        )
    )


async def buy_gift_upgrade(
    invoker: Invoker,
    gift: Any,
    peer: Target | None = None,
    *,
    keep_details: bool = False,
) -> Any:
    """Pay to upgrade a gift whose upgrade was not included. This spends Stars."""
    return await _pay(
        invoker,
        types.InputInvoiceStarGiftUpgrade(
            stargift=await _saved(invoker, gift, peer),
            keep_original_details=keep_details,
        ),
    )


async def transfer_gift(
    invoker: Invoker, gift: Any, to: Target, peer: Target | None = None
) -> Any:
    """Give an upgraded gift to somebody else, when the transfer is free.

    Transfers are free for a while after an upgrade and cost Stars afterwards.
    When it costs, this is refused and buy_gift_transfer is the call.
    """
    return await invoker.invoke(
        functions.payments.TransferStarGift(
            stargift=await _saved(invoker, gift, peer),
            to_id=await resolve(invoker, to),
        )
    )


async def buy_gift_transfer(
    invoker: Invoker, gift: Any, to: Target, peer: Target | None = None
) -> Any:
    """Pay the transfer fee and give an upgraded gift away. This spends Stars."""
    return await _pay(
        invoker,
        types.InputInvoiceStarGiftTransfer(
            stargift=await _saved(invoker, gift, peer),
            to_id=await resolve(invoker, to),
        ),
    )


async def buy_resale_gift(
    invoker: Invoker, slug: str, to: Target = "me", *, ton: bool = False
) -> Any:
    """Buy an upgraded gift somebody has listed. This spends Stars, or TON.

    to is who ends up holding it, which defaults to this account but can be
    anybody: buying one as a present is the same call with a different peer.
    """
    return await _pay(
        invoker,
        types.InputInvoiceStarGiftResale(
            slug=_slug(slug), to_id=await resolve(invoker, to), ton=ton
        ),
    )


# --- collections ------------------------------------------------------------


async def gift_collections(invoker: Invoker, peer: Target = "me") -> Any:
    """The shelves a peer has sorted their gifts onto."""
    return await invoker.invoke(
        functions.payments.GetStarGiftCollections(
            peer=await resolve(invoker, peer), hash=0
        )
    )


async def create_gift_collection(
    invoker: Invoker, title: str, gifts: Any, peer: Target = "me"
) -> Any:
    """Make a new shelf with something already on it.

    A collection cannot be created empty, which is the server's rule rather
    than this library's.
    """
    handles = await _saved_many(invoker, gifts, peer)
    if not handles:
        raise ValueError("a collection is created with at least one gift in it")
    return await invoker.invoke(
        functions.payments.CreateStarGiftCollection(
            peer=await resolve(invoker, peer), title=title, stargift=handles
        )
    )


async def rename_gift_collection(
    invoker: Invoker, collection_id: int, title: str, peer: Target = "me"
) -> Any:
    """Change what a collection is called, and nothing else about it."""
    return await invoker.invoke(
        functions.payments.UpdateStarGiftCollection(
            peer=await resolve(invoker, peer), collection_id=collection_id, title=title
        )
    )


async def add_to_gift_collection(
    invoker: Invoker, collection_id: int, gifts: Any, peer: Target = "me"
) -> Any:
    """Put gifts on a shelf they are not already on."""
    return await invoker.invoke(
        functions.payments.UpdateStarGiftCollection(
            peer=await resolve(invoker, peer),
            collection_id=collection_id,
            add_stargift=await _saved_many(invoker, gifts, peer),
        )
    )


async def remove_from_gift_collection(
    invoker: Invoker, collection_id: int, gifts: Any, peer: Target = "me"
) -> Any:
    """Take gifts off a shelf. They are still owned, just not filed there."""
    return await invoker.invoke(
        functions.payments.UpdateStarGiftCollection(
            peer=await resolve(invoker, peer),
            collection_id=collection_id,
            delete_stargift=await _saved_many(invoker, gifts, peer),
        )
    )


async def reorder_gift_collection(
    invoker: Invoker, collection_id: int, gifts: Any, peer: Target = "me"
) -> Any:
    """Set the order gifts sit in on one shelf, which is the whole order."""
    return await invoker.invoke(
        functions.payments.UpdateStarGiftCollection(
            peer=await resolve(invoker, peer),
            collection_id=collection_id,
            order=await _saved_many(invoker, gifts, peer),
        )
    )


async def reorder_gift_collections(
    invoker: Invoker, order: list[int], peer: Target = "me"
) -> bool:
    """Set the order the shelves themselves sit in."""
    return bool(
        await invoker.invoke(
            functions.payments.ReorderStarGiftCollections(
                peer=await resolve(invoker, peer), order=list(order)
            )
        )
    )


async def delete_gift_collection(
    invoker: Invoker, collection_id: int, peer: Target = "me"
) -> bool:
    """Get rid of a shelf. What was on it is still owned."""
    return bool(
        await invoker.invoke(
            functions.payments.DeleteStarGiftCollection(
                peer=await resolve(invoker, peer), collection_id=collection_id
            )
        )
    )


# --- auctions and offers ----------------------------------------------------


async def gift_auctions(invoker: Invoker) -> Any:
    """Auctions running now."""
    return await invoker.invoke(functions.payments.GetStarGiftActiveAuctions(hash=0))


async def gift_auction_state(
    invoker: Invoker, auction: int | str, *, version: int = 0
) -> Any:
    """Where an auction has got to, named by gift id or by slug.

    version is the state already held, and the server answers with nothing when
    it has not moved past it, which is what makes polling this cheap.
    """
    which: base.InputStarGiftAuction = (
        types.InputStarGiftAuctionSlug(slug=_slug(auction))
        if isinstance(auction, str)
        else types.InputStarGiftAuction(gift_id=auction)
    )
    return await invoker.invoke(
        functions.payments.GetStarGiftAuctionState(auction=which, version=version)
    )


async def gift_auction_gifts(invoker: Invoker, gift_id: int) -> Any:
    """What this account has already won in auctions of one kind of gift."""
    return await invoker.invoke(
        functions.payments.GetStarGiftAuctionAcquiredGifts(gift_id=gift_id)
    )


async def bid_on_gift_auction(
    invoker: Invoker,
    gift_id: int,
    amount: int,
    *,
    peer: Target | None = None,
    message: str | None = None,
    anonymous: bool = False,
    raise_existing: bool = False,
) -> Any:
    """Bid in an auction. This spends Stars, and a bid cannot be taken back.

    raise_existing says this replaces a bid already standing rather than being
    a first one, which the server needs told: sent as a new bid it would be
    refused for bidding twice.
    """
    return await _pay(
        invoker,
        types.InputInvoiceStarGiftAuctionBid(
            gift_id=gift_id,
            bid_amount=amount,
            peer=None if peer is None else await resolve(invoker, peer),
            message=_text(message),
            hide_name=anonymous,
            update_bid=raise_existing,
        ),
    )


async def send_gift_offer(
    invoker: Invoker,
    peer: Target,
    slug: str,
    amount: int,
    *,
    duration: int,
    paid_stars: int | None = None,
) -> Any:
    """Offer to buy somebody's upgraded gift off them at a price.

    duration is how long the offer stands, in seconds. Nothing is spent here:
    the Stars move if and when the offer is accepted.
    """
    return await invoker.invoke(
        functions.payments.SendStarGiftOffer(
            peer=await resolve(invoker, peer),
            slug=_slug(slug),
            price=stars(amount),
            duration=duration,
            random_id=int.from_bytes(secrets.token_bytes(8), "little", signed=True),
            allow_paid_stars=paid_stars,
        )
    )


async def accept_gift_offer(invoker: Invoker, message_id: int) -> Any:
    """Take an offer for one of your gifts, which hands it over and pays you."""
    return await invoker.invoke(
        functions.payments.ResolveStarGiftOffer(offer_msg_id=message_id, decline=False)
    )


async def decline_gift_offer(invoker: Invoker, message_id: int) -> Any:
    """Turn an offer down. The offer ends; the gift stays where it is."""
    return await invoker.invoke(
        functions.payments.ResolveStarGiftOffer(offer_msg_id=message_id, decline=True)
    )


# --- crafting ---------------------------------------------------------------


async def craftable_gifts(
    invoker: Invoker, gift_id: int, *, offset: str = "", limit: int = 100
) -> Any:
    """Which of the gifts held could go into crafting one of this kind."""
    return await invoker.invoke(
        functions.payments.GetCraftStarGifts(
            gift_id=gift_id, offset=offset, limit=limit
        )
    )


async def craft_gift(invoker: Invoker, gifts: Any, peer: Target | None = None) -> Any:
    """Consume several gifts to make one. The ones put in are gone."""
    handles = await _saved_many(invoker, gifts, peer)
    if not handles:
        raise ValueError("crafting consumes gifts, so it needs at least one")
    return await invoker.invoke(
        functions.payments.CraftStarGift(stargift=handles)
    )
