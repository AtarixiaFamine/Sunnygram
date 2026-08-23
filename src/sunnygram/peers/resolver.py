# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Turning whatever someone typed into something the server understands.

A person writing a program thinks in usernames, in the ids they saw in a Bot API
payload, or in the message object they already have in hand. MTProto thinks in
input peers, which pair an id with an access hash. This is the translation, and
the whole point of the cache underneath is that it usually happens without a
round trip.

The one shape that has to reach the network is a username or a phone number
no one in this session has seen yet. Everything else is either self evident, a
lookup, or an honest refusal.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, TypeGuard

from ..errors import PeerNotFound, RPCError, SunnygramError
from ..raw import functions, types
from ..storage import PeerKind, PeerRecord
from .cache import input_peer_for, normalize_phone, normalize_username

if TYPE_CHECKING:
    # Only for the annotations. Importing the invoker for real would close a
    # circle, since the invoker is what carries the cache this uses, and
    # importing the abstract types would load the API schema at import time
    # instead of at first use (rule P7).
    from ..network import Invoker
    from ..raw import base

__all__ = [
    "Target",
    "as_channel",
    "as_user",
    "mark_id",
    "mark_peer",
    "resolve",
    "resolve_phone",
    "resolve_username",
    "unmark_id",
]

# Anything that can name a peer: an input peer or input user or input channel
# already, a Peer or a User or a Chat straight out of an answer, an id in either
# spelling, a username, a phone number, or "me".
Target = Any

# How the Bot API spells a chat id that is not a user's, and what Sunnygram
# accepts so that an id copied from there works here. A channel is the negative
# of its id past this mark, a basic group is simply negative.
CHANNEL_MARK = -1_000_000_000_000

# What a username can be made of. Checked before a call goes out so that a typo
# costs nothing and reads clearly, instead of coming back as USERNAME_INVALID.
_USERNAME = re.compile(r"^[a-z0-9_]{1,32}$")

# What the server says when the name is fine but no one answers to it. These
# are not really errors in the caller's sense, they are an answer of no.
_NO_SUCH_PEER = frozenset(
    {
        "USERNAME_NOT_OCCUPIED",
        "USERNAME_INVALID",
        "PHONE_NOT_OCCUPIED",
        "PHONE_NUMBER_INVALID",
    }
)

_SELF = frozenset({"me", "self"})

# Built on first use rather than at import. Naming a generated class is what
# loads the module holding every API constructor, and a program that imports
# Sunnygram without resolving anybody should not pay for that (rule P7).
_input_peers: tuple[type, ...] = ()


def _already_a_peer(target: Any) -> TypeGuard[base.InputPeer]:
    """Whether this is an input peer already, in any of its forms."""
    global _input_peers
    if not _input_peers:
        _input_peers = (
            types.InputPeerEmpty,
            types.InputPeerSelf,
            types.InputPeerChat,
            types.InputPeerUser,
            types.InputPeerChannel,
            types.InputPeerUserFromMessage,
            types.InputPeerChannelFromMessage,
        )
    return isinstance(target, _input_peers)


def mark_id(peer_id: int, kind: PeerKind) -> int:
    """Spell an id the way the Bot API does, for talking to things that do.

    Only useful at the edges: Sunnygram works in the ids the protocol uses.
    """
    if kind.is_user:
        return peer_id
    if kind.is_channel:
        return CHANNEL_MARK - peer_id
    return -peer_id


def mark_peer(peer: Any) -> int | None:
    """A Peer as the one number that names it, or nothing if it is not a peer.

    The useful part is that the answer is a single int, so a peer fits anywhere
    something has to be written down: a dict key, a database column, a portable
    file reference. Handing it back to resolve reaches the same peer.
    """
    if isinstance(peer, types.PeerUser):
        return mark_id(peer.user_id, PeerKind.USER)
    if isinstance(peer, types.PeerChat):
        return mark_id(peer.chat_id, PeerKind.CHAT)
    if isinstance(peer, types.PeerChannel):
        return mark_id(peer.channel_id, PeerKind.CHANNEL)
    return None


def unmark_id(marked: int) -> tuple[int, PeerKind]:
    """Read a Bot API style id back, with the kind its sign implies.

    The kind that comes out is the coarse one, because that is all a sign can
    carry: a person and a bot are spelled alike, and so are a channel and a
    supergroup. That is enough to build an input peer, and the cache knows
    better anyway whenever it has met the peer before.
    """
    if marked >= 0:
        return marked, PeerKind.USER
    if marked <= CHANNEL_MARK:
        return CHANNEL_MARK - marked, PeerKind.CHANNEL
    return -marked, PeerKind.CHAT


def as_channel(peer: base.InputPeer) -> base.InputChannel:
    """The same channel, spelled the way the channels namespace wants it.

    Telegram splits its API by what it is talking to, so half a dozen calls
    take an input channel instead of an input peer even though the two carry
    the same id and hash. This is that conversion, and the refusal when it is
    asked of something that is not a channel at all.
    """
    if isinstance(peer, types.InputPeerChannel):
        return types.InputChannel(
            channel_id=peer.channel_id, access_hash=peer.access_hash
        )
    if isinstance(peer, types.InputPeerChannelFromMessage):
        return types.InputChannelFromMessage(
            peer=peer.peer, msg_id=peer.msg_id, channel_id=peer.channel_id
        )
    raise SunnygramError(
        f"this call is only for channels and supergroups, and "
        f"{type(peer).__name__} is not one"
    )


def as_user(peer: base.InputPeer) -> base.InputUser:
    """The same person, spelled the way the users namespace wants it."""
    if isinstance(peer, types.InputPeerSelf):
        return types.InputUserSelf()
    if isinstance(peer, types.InputPeerUser):
        return types.InputUser(user_id=peer.user_id, access_hash=peer.access_hash)
    if isinstance(peer, types.InputPeerUserFromMessage):
        return types.InputUserFromMessage(
            peer=peer.peer, msg_id=peer.msg_id, user_id=peer.user_id
        )
    raise SunnygramError(
        f"this call is only for people, and {type(peer).__name__} is not one"
    )


async def resolve(invoker: Invoker, target: Target) -> base.InputPeer:
    """Name a peer to the server, however the caller happened to say it.

    Costs nothing for anything the session has already seen. A username or a
    phone number that is genuinely new costs one call, after which it is known
    for good.
    """
    if _already_a_peer(target):
        return target

    if isinstance(target, types.InputUserSelf):
        return types.InputPeerSelf()
    if isinstance(target, types.InputUser):
        return types.InputPeerUser(
            user_id=target.user_id, access_hash=target.access_hash
        )
    if isinstance(target, types.InputChannel):
        return types.InputPeerChannel(
            channel_id=target.channel_id, access_hash=target.access_hash
        )

    if isinstance(target, str):
        return await _from_text(invoker, target)

    if isinstance(target, bool):
        # Caught before int, which bool is a form of, because True naming user
        # number one is no one's intention.
        raise TypeError("a bool does not name a peer")

    if isinstance(target, int):
        return await _from_id(invoker, target)

    if isinstance(target, (types.PeerUser, types.PeerChat, types.PeerChannel)):
        return await _from_id(invoker, _id_of(target))

    if isinstance(
        target,
        (
            types.User,
            types.Chat,
            types.Channel,
            types.ChatForbidden,
            types.ChannelForbidden,
        ),
    ):
        # Something straight out of an answer. Worth learning on the way past,
        # and worth using directly, since it carries its own hash unless it is
        # one of the min forms the cache refuses.
        invoker.peers.learn(target)
        return await _from_id(invoker, target.id)

    raise TypeError(f"{type(target).__name__} does not name a peer")


async def resolve_username(invoker: Invoker, username: str) -> PeerRecord:
    """Ask the server who holds a username, and remember the answer.

    Goes to the network even when the peer is already known, which is what
    makes it the way to notice that a name changed hands. resolve is the one to
    call for ordinary work.
    """
    name = normalize_username(username)
    if not _USERNAME.match(name):
        raise PeerNotFound(f"{username!r} is not shaped like a username")

    answer = await _ask(
        invoker, functions.contacts.ResolveUsername(username=name), f"@{name}"
    )
    record = await _learned(invoker, answer)
    if record is None:
        raise PeerNotFound(f"the server answered about @{name} with nothing usable")
    return record


async def resolve_phone(invoker: Invoker, phone: str) -> PeerRecord:
    """Ask the server whose number this is, and remember the answer.

    Only works for numbers already in the account's contacts, which is Telegram
    being careful instead of this being incomplete.
    """
    digits = normalize_phone(phone)
    if digits is None:
        raise PeerNotFound(f"{phone!r} is not shaped like a phone number")

    answer = await _ask(
        invoker, functions.contacts.ResolvePhone(phone=digits), f"+{digits}"
    )
    record = await _learned(invoker, answer)
    if record is None:
        raise PeerNotFound(f"the server answered about +{digits} with nothing usable")
    return record


async def _from_text(invoker: Invoker, text: str) -> base.InputPeer:
    """A string: ourselves, a username, a link to one, or a phone number."""
    written = text.strip()
    if not written:
        raise PeerNotFound("an empty string does not name anybody")
    if written.lower() in _SELF:
        return types.InputPeerSelf()

    if "joinchat" in written.lower() or "/+" in written:
        # An invite link names a chat the account may not be in yet, and there
        # is no way to turn one into a peer without joining or checking it.
        raise PeerNotFound(
            f"{text!r} is an invite link rather than a username. Joining a chat "
            "from a link is not part of the peer cache"
        )

    if written.startswith("+") and normalize_phone(written) is not None:
        digits = normalize_phone(written)
        assert digits is not None
        known = await invoker.peers.by_phone(digits)
        if known is None:
            known = await resolve_phone(invoker, digits)
        return input_peer_for(known)

    name = normalize_username(written)
    if not _USERNAME.match(name):
        raise PeerNotFound(f"{text!r} is not shaped like a username")
    found = await invoker.peers.by_username(name)
    if found is None:
        found = await resolve_username(invoker, name)
    return input_peer_for(found)


async def _from_id(invoker: Invoker, value: int) -> base.InputPeer:
    """An id, in either spelling, from the cache."""
    peer_id, kind = unmark_id(value)
    # One table for every kind, because Telegram hands out user, chat and
    # channel ids from ranges that do not overlap, so an id names one thing.
    record = await invoker.peers.get(peer_id)
    if record is not None:
        return input_peer_for(record)
    if kind is PeerKind.CHAT:
        # A basic group is reachable by id alone, so not having met it is not
        # in the way.
        return types.InputPeerChat(chat_id=peer_id)
    raise PeerNotFound(
        f"nothing is known about the peer {value}. Resolve them by username "
        "once, or reach them from a chat or an update they appear in, and the "
        "hash is kept from then on"
    )


async def _ask(invoker: Invoker, request: Any, named: str) -> Any:
    """Make a resolving call, with the refusals that mean no turned into one."""
    try:
        return await invoker.invoke(request)
    except RPCError as refused:
        if refused.message in _NO_SUCH_PEER:
            raise PeerNotFound(f"nobody on Telegram answers to {named}") from refused
        raise


async def _learned(invoker: Invoker, answer: Any) -> PeerRecord | None:
    """Take in what a resolving call carried, and pick out who was asked about."""
    if not isinstance(answer, types.contacts.ResolvedPeer):
        raise SunnygramError(
            f"expected a resolved peer, got {type(answer).__name__}"
        )
    cache = invoker.peers
    cache.learn(*answer.users, *answer.chats)
    # A name that cost a round trip is worth writing down now, not at
    # whatever point the batch happens to fill.
    await cache.flush()
    return await cache.get(_id_of(answer.peer))


def _id_of(peer: Any) -> int:
    """The id inside a Peer, whichever of the three it is."""
    if isinstance(peer, types.PeerUser):
        return int(peer.user_id)
    if isinstance(peer, types.PeerChat):
        return int(peer.chat_id)
    if isinstance(peer, types.PeerChannel):
        return int(peer.channel_id)
    raise SunnygramError(f"{type(peer).__name__} does not name a peer")
