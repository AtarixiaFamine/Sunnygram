# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Chats, and the people in them.

Everything here pages. Telegram answers a list of anything a slice at a time
and expects the client to come back with where it got to, and the shape of
"where it got to" is different for every list: dialogs carry a date, a message
id and a peer all three, participants carry a plain offset. That bookkeeping is
the reason these exist, since the call itself is one line and the loop around
it is the part no one wants to write twice.

Each of these yields whole pages instead of items. A page carries the users
and chats that explain what is in it, and losing that link is how a caller ends
up with a dialog it cannot name.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, as_channel, resolve
from ..raw import base, functions, types

__all__ = [
    "iter_dialog_pages",
    "iter_participant_pages",
    "join_chat",
    "leave_chat",
    "chat_info",
]

# What Telegram will answer with at once, whatever is asked for above it.
DIALOG_BATCH = 100
PARTICIPANT_BATCH = 200


async def iter_dialog_pages(
    invoker: Invoker, *, limit: int = 100, batch: int = DIALOG_BATCH
) -> AsyncIterator[Any]:
    """Every conversation this account has, newest first, a page at a time.

    The cursor is three things together: the date and id of the last message
    seen and the peer it was in. Passing only the id, which looks like it ought
    to work, walks a chat instead of the list of them.
    """
    offset_date = 0
    offset_id = 0
    offset_peer: base.InputPeer = types.InputPeerEmpty()
    seen = 0

    while seen < limit:
        page = await invoker.invoke(
            functions.messages.GetDialogs(
                offset_date=offset_date,
                offset_id=offset_id,
                offset_peer=offset_peer,
                limit=min(batch, limit - seen),
                hash=0,
            )
        )
        dialogs = list(getattr(page, "dialogs", ()) or ())
        if not dialogs:
            return
        yield page
        seen += len(dialogs)

        if isinstance(page, types.messages.Dialogs):
            # The unsliced form is the whole list, so there is no next page
            # however many came back.
            return
        cursor = _last_message(page, dialogs[-1])
        if cursor is None:
            return
        offset_date, offset_id, offset_peer = cursor


async def iter_participant_pages(
    invoker: Invoker,
    peer: Target,
    *,
    limit: int = 200,
    query: str = "",
    batch: int = PARTICIPANT_BATCH,
) -> AsyncIterator[Any]:
    """The members of a group or channel, a page at a time.

    A basic group is not paged at all: Telegram answers the whole membership in
    one call, because a basic group is small by definition. A supergroup or a
    channel is paged, and a search term narrows it.
    """
    where = await resolve(invoker, peer)

    if isinstance(where, types.InputPeerChat):
        full = await invoker.invoke(
            functions.messages.GetFullChat(chat_id=where.chat_id)
        )
        yield full
        return

    chosen: base.ChannelParticipantsFilter = (
        types.ChannelParticipantsSearch(q=query)
        if query
        else types.ChannelParticipantsRecent()
    )
    offset = 0
    while offset < limit:
        page = await invoker.invoke(
            functions.channels.GetParticipants(
                channel=as_channel(where),
                filter=chosen,
                offset=offset,
                limit=min(batch, limit - offset),
                hash=0,
            )
        )
        found = list(getattr(page, "participants", ()) or ())
        if not found:
            return
        yield page
        offset += len(found)


async def join_chat(invoker: Invoker, peer: Target) -> Any:
    """Join a channel or supergroup, or accept an invite link.

    A link is the other call entirely: the hash in it stands for a chat this
    account cannot name yet, which is the whole point of an invite.
    """
    if isinstance(peer, str) and _invite_hash(peer) is not None:
        return await invoker.invoke(
            functions.messages.ImportChatInvite(hash=_invite_hash(peer) or "")
        )
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.channels.JoinChannel(channel=as_channel(where))
    )


async def leave_chat(invoker: Invoker, peer: Target) -> Any:
    """Leave a chat, whichever kind it is."""
    where = await resolve(invoker, peer)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.DeleteChatUser(
                chat_id=where.chat_id, user_id=types.InputUserSelf(), revoke_history=False
            )
        )
    return await invoker.invoke(
        functions.channels.LeaveChannel(channel=as_channel(where))
    )


async def chat_info(invoker: Invoker, peer: Target) -> Any:
    """Everything Telegram knows about a chat, not only what a list shows.

    The full form is a separate call for a reason: it carries the description,
    the counts and the pinned message, and asking for it on every chat in a
    list would be one round trip per row.
    """
    where = await resolve(invoker, peer)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.GetFullChat(chat_id=where.chat_id)
        )
    if isinstance(
        where, (types.InputPeerChannel, types.InputPeerChannelFromMessage)
    ):
        return await invoker.invoke(
            functions.channels.GetFullChannel(channel=as_channel(where))
        )
    raise SunnygramError(
        f"{type(where).__name__} is a person rather than a chat; ask for a user"
    )


def _last_message(page: Any, dialog: Any) -> tuple[int, int, base.InputPeer] | None:
    """Where the next page of dialogs starts, from the last one on this page."""
    top = getattr(dialog, "top_message", 0)
    date = next(
        (
            message.date
            for message in getattr(page, "messages", ()) or ()
            if getattr(message, "id", None) == top
        ),
        None,
    )
    if date is None:
        return None
    peer = _input_for(getattr(dialog, "peer", None), page)
    return (date, top, peer) if peer is not None else None


def _input_for(peer: Any, page: Any) -> base.InputPeer | None:
    """The input peer for a dialog, from what the same page carried."""
    if isinstance(peer, types.PeerUser):
        for user in getattr(page, "users", ()) or ():
            if user.id == peer.user_id:
                return types.InputPeerUser(
                    user_id=user.id, access_hash=user.access_hash or 0
                )
    elif isinstance(peer, types.PeerChat):
        return types.InputPeerChat(chat_id=peer.chat_id)
    elif isinstance(peer, types.PeerChannel):
        for chat in getattr(page, "chats", ()) or ():
            if chat.id == peer.channel_id:
                return types.InputPeerChannel(
                    channel_id=chat.id, access_hash=getattr(chat, "access_hash", 0) or 0
                )
    return None


def _invite_hash(text: str) -> str | None:
    """The hash out of an invite link, if that is what this is.

    Telegram writes these two ways and has for years, so both are read here.
    A plain username is not an invite and comes back as nothing.
    """
    cleaned = text.strip()
    for prefix in ("https://t.me/joinchat/", "http://t.me/joinchat/", "t.me/joinchat/"):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :] or None
    for prefix in ("https://t.me/+", "http://t.me/+", "t.me/+", "+"):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :] or None
    return None
