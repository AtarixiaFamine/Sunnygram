# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sending several files as one thing.

An album is not a message with several files in it. It is several messages that
share a group id, which the clients then draw as one block, and that shows in
how it has to be sent: every file goes up on its own, is registered with the
server on its own, and only then do the finished descriptions go out together in
a single call. Sending them one at a time instead would produce several separate
messages that look nothing like an album.

The registering step is the one that is easy to miss. sendMultiMedia will not
take an uploaded file the way sendMedia does; it wants media the server has
already seen, so each part is handed to uploadMedia first and comes back as
something with an id, and that is what goes into the call.

Telegram allows ten in a group and mixes photos and videos freely, but nothing
else: a document cannot share a group with a photo. That is checked here, since
the server's refusal does not say which of the ten was the problem.
"""

from __future__ import annotations

from typing import Any

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, resolve
from ..raw import base, functions, types
from ..updates import UpdateManager
from .messages import random_id, reply_header

__all__ = ["ALBUM_LIMIT", "register_media", "send_album"]

# What Telegram takes in one group. Sending more means several albums.
ALBUM_LIMIT = 10

# Which media may share a group with which. A photo and a video are the same
# kind of thing to Telegram here; everything else stands alone.
_VISUAL = (types.InputMediaUploadedPhoto, types.InputMediaPhoto)
_DOCUMENT = (types.InputMediaUploadedDocument, types.InputMediaDocument)


async def register_media(
    invoker: Invoker, peer: Target, media: base.InputMedia
) -> base.InputMedia:
    """Have the server take an uploaded file, and hand back what it made of it.

    This is the step between uploading and sending. An uploaded file is bytes
    the server is holding; what comes back from here is a photo or a document
    with an id, which is what an album entry has to be.

    Anything that is already registered goes straight through, so calling this
    on a document being pointed at instead of sent costs nothing.
    """
    if not isinstance(media, (types.InputMediaUploadedPhoto, types.InputMediaUploadedDocument)):
        return media

    where = await resolve(invoker, peer)
    made = await invoker.invoke(
        functions.messages.UploadMedia(peer=where, media=media)
    )
    # The empty forms are checked for instead of merely None: the server
    # answers a photo it could not keep with photoEmpty, which has an id and
    # nothing else to reach it by.
    if isinstance(made, types.MessageMediaPhoto) and isinstance(
        made.photo, types.Photo
    ):
        return types.InputMediaPhoto(
            id=types.InputPhoto(
                id=made.photo.id,
                access_hash=made.photo.access_hash,
                file_reference=made.photo.file_reference,
            ),
            spoiler=getattr(media, "spoiler", False),
            ttl_seconds=getattr(media, "ttl_seconds", None),
        )
    if isinstance(made, types.MessageMediaDocument) and isinstance(
        made.document, types.Document
    ):
        return types.InputMediaDocument(
            id=types.InputDocument(
                id=made.document.id,
                access_hash=made.document.access_hash,
                file_reference=made.document.file_reference,
            ),
            spoiler=getattr(media, "spoiler", False),
            ttl_seconds=getattr(media, "ttl_seconds", None),
        )
    raise SunnygramError(
        f"the server took the upload and answered with {type(made).__name__}, "
        "which is not something an album can carry"
    )


def check_album(media: list[base.InputMedia]) -> None:
    """Refuse a group Telegram would refuse, with a reason it does not give."""
    if not media:
        raise ValueError("an album needs something in it")
    if len(media) > ALBUM_LIMIT:
        raise ValueError(
            f"an album holds at most {ALBUM_LIMIT} files, not {len(media)}; "
            "send them as several albums"
        )
    visual = sum(isinstance(one, _VISUAL) for one in media)
    documents = sum(isinstance(one, _DOCUMENT) for one in media)
    if visual and documents:
        raise ValueError(
            "photos and videos group together and documents group together, "
            "but the two cannot share one album"
        )


async def send_album(
    invoker: Invoker,
    peer: Target,
    media: list[base.InputMedia],
    *,
    captions: list[tuple[str, list[base.MessageEntity]]] | None = None,
    reply_to: int | None = None,
    topic: int | None = None,
    silent: bool = False,
    updates: UpdateManager | None = None,
) -> list[types.Message]:
    """Send several files as one album, and return the messages made of them.

    captions runs alongside media, one text and its entities per file. Only the
    first is usually worth setting: most clients show the first caption under
    the whole block and hide the rest until a file is opened.
    """
    check_album(media)
    if captions is not None and len(captions) != len(media):
        raise ValueError("there must be one caption per file, or none at all")

    where = await resolve(invoker, peer)
    parts = []
    for index, one in enumerate(media):
        text, entities = captions[index] if captions else ("", [])
        parts.append(
            types.InputSingleMedia(
                media=await register_media(invoker, where, one),
                random_id=random_id(),
                message=text,
                entities=entities or None,
            )
        )

    answer = await invoker.invoke(
        functions.messages.SendMultiMedia(
            peer=where,
            multi_media=parts,
            silent=silent,
            reply_to=reply_header(reply_to, topic),
        )
    )
    if updates is not None:
        await updates.feed(answer)

    sent = _messages_in(answer, {part.random_id for part in parts})
    if len(sent) != len(parts):
        raise SunnygramError(
            f"sent {len(parts)} files as an album and the server described "
            f"{len(sent)} of them"
        )
    return sent


def _messages_in(answer: Any, wanted: set[int]) -> list[types.Message]:
    """The messages an album call answered with, in the order they were sent.

    Matched by random id rather than taken as they come. The updates arrive in
    no particular order and carry other things besides, so pairing them up is
    the only way to know which message is which file.
    """
    by_random: dict[int, int] = {}
    by_id: dict[int, types.Message] = {}
    for update in getattr(answer, "updates", ()):
        if isinstance(update, types.UpdateMessageID) and update.random_id in wanted:
            by_random[update.random_id] = update.id
        found = getattr(update, "message", None)
        if isinstance(found, types.Message):
            by_id[found.id] = found

    ordered = []
    for random in wanted:
        message = by_id.get(by_random.get(random, 0))
        if message is not None:
            ordered.append(message)
    return sorted(ordered, key=lambda message: message.id)
