# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sending a message, and getting back the one that was sent.

The call itself is one line. Everything around it is the part worth writing
once: a message goes out with a random id that makes sending it twice harmless,
the answer comes back as updates rather than as a message, and the message has
to be found among them. Sometimes it is not there at all and the server sends a
shorthand instead, leaving the client to assemble what it already knows.

Whatever comes back also has to reach the update manager. The answer to a call
carries the same counters as an update that arrives on its own, and dropping
them on the floor is how a client ends up asking for a difference it does not
need, or worse, missing one it does.
"""

from __future__ import annotations

import secrets
import time
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from ..errors import RPCError, SunnygramError
from ..network import Invoker
from ..peers import Target, as_channel, resolve
from ..raw import base, functions, types
from ..tl import TLObject
from ..updates import UpdateManager
from .attachments import (
    as_document,
    as_photo,
    existing_media,
    media_origin,
    option_bytes,
    with_reference,
)

__all__ = [
    "WHEN_ONLINE",
    "Renew",
    "close_poll",
    "copy_message",
    "delete_scheduled_messages",
    "get_messages",
    "get_scheduled_messages",
    "pin_message",
    "poll_results",
    "random_id",
    "read_history",
    "rebuild_sent",
    "renewing",
    "reply_header",
    "schedule_at",
    "scheduled_history",
    "search_messages",
    "send_action",
    "send_media",
    "send_message",
    "send_scheduled_messages",
    "unpin_all_messages",
    "unpin_message",
    "vote_poll",
]

# Telegram's one magic schedule_date: send it the moment the recipient is next
# online, instead of at a time. It is a real timestamp as far as the wire is
# concerned, one second short of the 32-bit ceiling, which is why it has to be
# named instead of worked out.
WHEN_ONLINE = 0x7FFFFFFE

# Asked for the same file described again, with a token that has not expired.
# Only the caller can do this: the media in hand says which file it is and not
# where it was found, and finding it again is the only way to a fresh token.
# What comes back is an InputMedia, spelled loosely here for the same reason
# Refresh is in the file engine: the abstract TL types have no runtime form.
Renew = Callable[[], Awaitable[Any]]

# What the server says when the token inside a media reference has aged out.
# The file is still there, which is why this is worth telling apart and worth
# one more attempt rather than being handed straight to the caller.
STALE_REFERENCE = "FILE_REFERENCE_EXPIRED"


def reply_header(
    reply_to: int | None, topic: int | None = None
) -> base.InputReplyTo | None:
    """Where in a chat a message belongs: a reply, a topic, or neither.

    A forum topic is the message that opened it, and being in one is spelled as
    replying to that message, which is why one field says both things. Given
    only a topic, the message is posted to it; given both, the reply names the
    message being answered and the topic names the thread it is in.
    """
    if reply_to is None:
        if topic is None:
            return None
        return types.InputReplyToMessage(reply_to_msg_id=topic)
    return types.InputReplyToMessage(reply_to_msg_id=reply_to, top_msg_id=topic)


def schedule_at(when: datetime | int | None) -> int | None:
    """When a message should go out, as the wire spells it.

    A datetime is the useful way to say it and a unix timestamp is what
    Telegram takes, so both are accepted. A naive datetime is read as local
    time, which is what someone writing datetime(2030, 1, 1, 9, 0) in their
    own timezone means by it; give it a tzinfo to be explicit.

    WHEN_ONLINE passes through as itself. It is a timestamp the server reads as
    "when they are next online" instead of as a date, and converting it would
    turn a feature into a message scheduled for 2038.
    """
    if when is None:
        return None
    if isinstance(when, datetime):
        if when.tzinfo is None:
            when = when.astimezone()
        return int(when.timestamp())
    return when


def random_id() -> int:
    """A fresh id for one outgoing message.

    Telegram remembers these for a while and answers a repeat with the message
    it already made, which makes sending again after a dropped
    connection safe instead of a way to say everything twice.
    """
    return int.from_bytes(secrets.token_bytes(8), "little", signed=True)


async def send_message(
    invoker: Invoker,
    peer: Target,
    message: str,
    *,
    reply_to: int | None = None,
    topic: int | None = None,
    silent: bool = False,
    no_webpage: bool = False,
    reply_markup: base.ReplyMarkup | None = None,
    schedule_date: datetime | int | None = None,
    updates: UpdateManager | None = None,
) -> types.Message:
    """Send a text message, and return the message the server made of it.

    The peer is whatever names the recipient: an input peer, a username, an id
    in either spelling, "me" for the account itself, or a user or chat object
    that arrived with something else. Anything the session has met already
    costs nothing to name.

    reply_markup is the keyboard to put under it, which types/buttons.py
    builds and only a bot may send.

    schedule_date holds the message until then rather than sending it now, as a
    datetime or a unix timestamp, or WHEN_ONLINE to wait for the recipient. The
    message comes back the same way, but it is a scheduled message: it has its
    own numbering, it is not in the chat yet, and scheduled_history is where it
    can be found until it goes out.

    Pass the update manager if there is one. The answer to this call carries
    counters that belong to it, and it is the only thing allowed to move them.
    """
    if not message:
        raise ValueError("a message needs something in it")

    where = await resolve(invoker, peer)
    chosen = random_id()
    answer = await invoker.invoke(
        functions.messages.SendMessage(
            peer=where,
            message=message,
            random_id=chosen,
            no_webpage=no_webpage,
            silent=silent,
            reply_to=reply_header(reply_to, topic),
            reply_markup=reply_markup,
            schedule_date=schedule_at(schedule_date),
        )
    )
    if updates is not None:
        await updates.feed(answer)

    sent = _sent_message(answer, chosen)
    if sent is not None:
        return sent
    if isinstance(answer, types.UpdateShortSentMessage):
        # The server saw nothing worth describing, so it sent the id and the
        # date and left the rest to us. We know the rest: we wrote it.
        return rebuild_sent(invoker, answer, where, message, reply_to)
    raise SunnygramError(
        f"the server answered sendMessage with {type(answer).__name__} and no "
        "message in it"
    )


async def send_media(
    invoker: Invoker,
    peer: Target,
    media: base.InputMedia,
    *,
    message: str = "",
    entities: list[base.MessageEntity] | None = None,
    reply_to: int | None = None,
    topic: int | None = None,
    silent: bool = False,
    reply_markup: base.ReplyMarkup | None = None,
    schedule_date: datetime | int | None = None,
    renew: Renew | None = None,
    updates: UpdateManager | None = None,
) -> types.Message:
    """Send a message carrying a file, and return the one the server made.

    The media is already-uploaded bytes described as something, which is what
    methods/media.py builds. The caption is the message text: Telegram has no
    separate field for it, which is why a photo with something written under it
    and a plain message are the same call with different arguments.

    A file that is being pointed at instead of uploaded carries a token that
    goes stale after an hour or so. renew is how to get a fresh one: given it,
    a stale token is renewed and the send is tried once more, which turns the
    most common failure of re-sending an old file into something that simply
    works. Once, not in a loop, because a token that is stale again straight
    after being renewed means something other than time has gone wrong.
    """
    where = await resolve(invoker, peer)
    chosen = random_id()
    described = media
    for attempt in range(2):
        try:
            answer = await invoker.invoke(
                functions.messages.SendMedia(
                    peer=where,
                    media=described,
                    message=message,
                    random_id=chosen,
                    entities=entities or None,
                    silent=silent,
                    reply_to=reply_header(reply_to, topic),
                    reply_markup=reply_markup,
                    schedule_date=schedule_at(schedule_date),
                )
            )
            break
        except RPCError as refused:
            if attempt or renew is None or refused.message != STALE_REFERENCE:
                raise
            described = with_reference(described, await renew())
    if updates is not None:
        await updates.feed(answer)

    sent = _sent_message(answer, chosen)
    if sent is not None:
        return sent
    if isinstance(answer, types.UpdateShortSentMessage):
        return rebuild_sent(invoker, answer, where, message, reply_to)
    raise SunnygramError(
        f"the server answered sendMedia with {type(answer).__name__} and no "
        "message in it"
    )


def renewing(invoker: Invoker, origin: tuple[int, int] | None) -> Renew | None:
    """A way back to a fresh reference for the file in one particular message.

    This is what makes a stale token recoverable instead of fatal: the origin
    says which message carried the file, so fetching that message again yields
    the same file described with a token that works. Nothing is fetched until
    something actually goes stale, so an origin that is never needed costs one
    closure and no calls.
    """
    if origin is None:
        return None
    where, message_id = origin

    async def renew() -> base.InputMedia:
        answer = await get_messages(invoker, where, [message_id])
        for found in getattr(answer, "messages", ()):
            media = existing_media(found)
            if media is not None:
                return media
        raise SunnygramError(
            f"the file reference expired and message {message_id} no longer "
            "carries the file it came from, so there is nothing to renew it "
            "with"
        )

    return renew


async def get_messages(
    invoker: Invoker, peer: Target, ids: list[int]
) -> Any:
    """Fetch particular messages by id, with the users and chats they name.

    A channel counts its messages separately from everything else, so asking it
    is a different call. The answer has the same shape either way.
    """
    where = await resolve(invoker, peer)
    wanted: list[base.InputMessage] = [types.InputMessageID(id=one) for one in ids]
    if isinstance(
        where, (types.InputPeerChannel, types.InputPeerChannelFromMessage)
    ):
        return await invoker.invoke(
            functions.channels.GetMessages(channel=as_channel(where), id=wanted)
        )
    return await invoker.invoke(functions.messages.GetMessages(id=wanted))


async def scheduled_history(invoker: Invoker, peer: Target) -> Any:
    """Everything queued for a chat but not sent yet.

    One call and no paging, because Telegram caps how many a chat may hold and
    the cap is small. The answer has the shape every history call has, so the
    users and chats it names come with it.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.GetScheduledHistory(peer=where, hash=0)
    )


async def get_scheduled_messages(
    invoker: Invoker, peer: Target, ids: list[int]
) -> Any:
    """Particular scheduled messages by id.

    Scheduled messages are numbered separately from sent ones, so these ids are
    the ones scheduled_history gave back and not the ids the messages will have
    once they go out.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.GetScheduledMessages(peer=where, id=list(ids))
    )


async def send_scheduled_messages(
    invoker: Invoker,
    peer: Target,
    ids: list[int],
    *,
    updates: UpdateManager | None = None,
) -> Any:
    """Send queued messages now rather than waiting for their time.

    Each one leaves the schedule and enters the chat, which means it gets a new
    id: the one it was queued under is gone afterwards.
    """
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.messages.SendScheduledMessages(peer=where, id=list(ids))
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def delete_scheduled_messages(
    invoker: Invoker,
    peer: Target,
    ids: list[int],
    *,
    updates: UpdateManager | None = None,
) -> Any:
    """Drop queued messages so they never go out."""
    where = await resolve(invoker, peer)
    answer = await invoker.invoke(
        functions.messages.DeleteScheduledMessages(peer=where, id=list(ids))
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def vote_poll(
    invoker: Invoker, peer: Target, message_id: int, options: list[int]
) -> Any:
    """Answer a poll, by the positions of the answers instead of their text.

    Passing an empty list retracts a vote, which the protocol has no separate
    call for. A poll that does not allow several answers takes one; the server
    refuses more instead of taking the first.
    """
    return await invoker.invoke(
        functions.messages.SendVote(
            peer=await resolve(invoker, peer),
            msg_id=message_id,
            options=[option_bytes(one) for one in options],
        )
    )


async def poll_results(invoker: Invoker, peer: Target, message_id: int) -> Any:
    """The current standing of a poll, without waiting for an update about it."""
    return await invoker.invoke(
        functions.messages.GetPollResults(
            peer=await resolve(invoker, peer), msg_id=message_id, poll_hash=0
        )
    )


async def close_poll(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    *,
    updates: UpdateManager | None = None,
) -> Any:
    """Stop a poll taking votes, which cannot be undone.

    Spelled as editing the message with a closed poll in place of the open one,
    because there is no call for closing. The poll sent here carries only the
    closed flag: everything else about it is already on the server, and sending
    the question again would be a second poll rather than the same one ending.
    """
    answer = await invoker.invoke(
        functions.messages.EditMessage(
            peer=await resolve(invoker, peer),
            id=message_id,
            media=types.InputMediaPoll(
                poll=types.Poll(
                    id=0,
                    hash=0,
                    closed=True,
                    question=types.TextWithEntities(text="", entities=[]),
                    answers=[],
                )
            ),
        )
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def copy_message(
    invoker: Invoker,
    source: types.Message,
    peer: Target,
    *,
    caption: str | None = None,
    entities: list[base.MessageEntity] | None = None,
    reply_to: int | None = None,
    silent: bool = False,
    reply_markup: base.ReplyMarkup | None = None,
    updates: UpdateManager | None = None,
) -> types.Message:
    """Send a message again as a new one, with no sign of where it came from.

    Not a forward. A forward keeps the original author's name on it and the
    original chat behind it, and there are chats where that is exactly what is
    not wanted. This sends the same content as though it were being written
    here for the first time.

    What can be copied is what can be pointed at: text, and media that already
    exists on the server. A poll cannot be copied, because a poll is a live
    thing with votes in it instead of content, and the server would make a
    second poll instead of a copy of the first.
    """
    media = _copyable(source.media)
    text = source.message if caption is None else caption
    styling = list(source.entities or []) if caption is None else (entities or [])

    if media is None:
        if not text:
            raise SunnygramError(
                "this message carries nothing that can be copied; forward it "
                "instead, or send its media by hand"
            )
        return await send_message(
            invoker,
            peer,
            text,
            reply_to=reply_to,
            silent=silent,
            reply_markup=reply_markup,
            updates=updates,
        )
    return await send_media(
        invoker,
        peer,
        media,
        message=text,
        entities=styling or None,
        reply_to=reply_to,
        silent=silent,
        reply_markup=reply_markup,
        # A copy points at the original's file, so it is exactly the send that
        # goes stale, and the original is exactly what renews it.
        renew=renewing(invoker, media_origin(source)),
        updates=updates,
    )


def _copyable(media: Any) -> base.InputMedia | None:
    """The same media, pointed at rather than uploaded again, if it can be."""
    if isinstance(media, types.MessageMediaPhoto) and isinstance(
        media.photo, types.Photo
    ):
        return as_photo(media.photo, spoiler=bool(getattr(media, "spoiler", False)))
    if isinstance(media, types.MessageMediaDocument) and isinstance(
        media.document, types.Document
    ):
        return as_document(
            media.document, spoiler=bool(getattr(media, "spoiler", False))
        )
    if isinstance(media, (types.MessageMediaGeo, types.MessageMediaVenue)):
        return _place(media)
    if isinstance(media, types.MessageMediaContact):
        return types.InputMediaContact(
            phone_number=media.phone_number,
            first_name=media.first_name,
            last_name=media.last_name,
            vcard=media.vcard,
        )
    if isinstance(media, types.MessageMediaDice):
        # A copy rolls again instead of showing the same number, which is the
        # only thing a die can mean when it is sent instead of remembered.
        return types.InputMediaDice(emoticon=media.emoticon)
    return None


def _place(media: Any) -> base.InputMedia | None:
    point = getattr(media, "geo", None)
    if not isinstance(point, types.GeoPoint):
        return None
    where = types.InputGeoPoint(
        lat=point.lat, long=point.long, accuracy_radius=point.accuracy_radius
    )
    if isinstance(media, types.MessageMediaVenue):
        return types.InputMediaVenue(
            geo_point=where,
            title=media.title,
            address=media.address,
            provider=media.provider,
            venue_id=media.venue_id,
            venue_type=media.venue_type,
        )
    return types.InputMediaGeoPoint(geo_point=where)


async def search_messages(
    invoker: Invoker,
    peer: Target,
    query: str,
    *,
    limit: int = 100,
    offset_id: int = 0,
    from_user: Target | None = None,
    filter: base.MessagesFilter | None = None,
) -> Any:
    """Search one chat, one page at a time.

    The filter narrows by kind rather than by text: photos only, links only,
    and so on. Leaving it out searches everything, which is what a plain query
    means.
    """
    return await invoker.invoke(
        functions.messages.Search(
            peer=await resolve(invoker, peer),
            q=query,
            from_id=None if from_user is None else await resolve(invoker, from_user),
            filter=filter or types.InputMessagesFilterEmpty(),
            min_date=0,
            max_date=0,
            offset_id=offset_id,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0,
        )
    )


async def read_history(
    invoker: Invoker, peer: Target, *, max_id: int = 0
) -> None:
    """Mark everything up to a message as read, or the whole chat.

    max_id of 0 means all of it. A channel keeps its own count, so it is the
    other call again.
    """
    where = await resolve(invoker, peer)
    if isinstance(where, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
        await invoker.invoke(
            functions.channels.ReadHistory(channel=as_channel(where), max_id=max_id)
        )
        return
    await invoker.invoke(
        functions.messages.ReadHistory(peer=where, max_id=max_id)
    )


async def pin_message(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    *,
    silent: bool = True,
    both_sides: bool = False,
    updates: UpdateManager | None = None,
) -> None:
    """Pin a message.

    Pinning is quiet by default, which is the opposite of Telegram's default
    and the kinder one: the noisy version notifies everybody in the chat, and a
    program pinning things regularly should have to ask for that.

    both_sides pins in the other person's copy of a private chat too, which is
    the one case where pinning affects someone else's view.
    """
    answer = await invoker.invoke(
        functions.messages.UpdatePinnedMessage(
            peer=await resolve(invoker, peer),
            id=message_id,
            silent=silent,
            pm_oneside=not both_sides,
        )
    )
    if updates is not None:
        await updates.feed(answer)


async def unpin_message(
    invoker: Invoker,
    peer: Target,
    message_id: int,
    *,
    updates: UpdateManager | None = None,
) -> None:
    """Unpin one message."""
    answer = await invoker.invoke(
        functions.messages.UpdatePinnedMessage(
            peer=await resolve(invoker, peer), id=message_id, unpin=True
        )
    )
    if updates is not None:
        await updates.feed(answer)


async def unpin_all_messages(invoker: Invoker, peer: Target) -> None:
    """Unpin everything pinned in a chat."""
    await invoker.invoke(
        functions.messages.UnpinAllMessages(peer=await resolve(invoker, peer))
    )


async def send_action(
    invoker: Invoker,
    peer: Target,
    action: base.SendMessageAction | None = None,
) -> None:
    """Show the other side that something is being done.

    Typing by default. Telegram forgets one of these after about six seconds,
    so anything that takes longer than that has to say it again.
    """
    await invoker.invoke(
        functions.messages.SetTyping(
            peer=await resolve(invoker, peer),
            action=action or types.SendMessageTypingAction(),
        )
    )


def _sent_message(answer: TLObject, chosen: int) -> types.Message | None:
    """Find our message among the updates the call answered with.

    updateMessageID is the link: it says which message id the random id we sent
    turned into. Matching on that instead of on position is what keeps this
    right when the same call also carries someone else's message.

    A scheduled message arrives in its own update instead of the ordinary one,
    because it has not been sent yet and does not belong to the chat's
    numbering. It is the same message otherwise, so it is read here too and the
    caller gets back what it asked to be sent either way.
    """
    if not isinstance(answer, (types.Updates, types.UpdatesCombined)):
        return None

    message_id = next(
        (
            update.id
            for update in answer.updates
            if isinstance(update, types.UpdateMessageID) and update.random_id == chosen
        ),
        None,
    )
    for update in answer.updates:
        if isinstance(
            update,
            (
                types.UpdateNewMessage,
                types.UpdateNewChannelMessage,
                types.UpdateNewScheduledMessage,
            ),
        ):
            found = update.message
            if isinstance(found, types.Message) and (
                message_id is None or found.id == message_id
            ):
                return found
    return None


def rebuild_sent(
    invoker: Invoker,
    answer: Any,
    peer: base.InputPeer,
    message: str,
    reply_to: int | None = None,
    entities: list[base.MessageEntity] | None = None,
) -> types.Message:
    """Assemble the message a shorthand answer stands for.

    Telegram answers a send in a private chat with updateShortSentMessage: the
    id and the date, and nothing else, because the rest is what we just wrote.
    Rebuilding it is not a nicety. The one thing the shorthand leaves out that
    cannot be worked out later is which chat the message is in, and without it
    the message that comes back cannot be edited, deleted or replied to. A bot
    that sends a status line and edits it as it works is the ordinary case, so
    every caller that hands a message back to a user goes through here.

    Read with getattr because this serves the shorthand and the answer that
    carried no message at all, and the second kind has none of these fields.
    """
    return types.Message(
        id=int(getattr(answer, "id", 0)),
        out=bool(getattr(answer, "out", True)),
        peer_id=_peer_of(peer, invoker.state.user_id),
        from_id=types.PeerUser(user_id=invoker.state.user_id)
        if invoker.state.user_id
        else None,
        date=getattr(answer, "date", None) or int(time.time()),
        message=message,
        media=getattr(answer, "media", None),
        entities=getattr(answer, "entities", None) or entities or None,
        ttl_period=getattr(answer, "ttl_period", None),
        reply_to=(
            None
            if reply_to is None
            else types.MessageReplyHeader(reply_to_msg_id=reply_to)
        ),
    )


def _peer_of(peer: base.InputPeer, me: int) -> base.Peer:
    """The peer as a message names it, from the peer we addressed it to."""
    if isinstance(peer, types.InputPeerSelf):
        return types.PeerUser(user_id=me)
    if isinstance(peer, (types.InputPeerUser, types.InputPeerUserFromMessage)):
        return types.PeerUser(user_id=peer.user_id)
    if isinstance(peer, types.InputPeerChat):
        return types.PeerChat(chat_id=peer.chat_id)
    if isinstance(peer, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
        return types.PeerChannel(channel_id=peer.channel_id)
    raise SunnygramError(f"{type(peer).__name__} does not name a peer to send to")
