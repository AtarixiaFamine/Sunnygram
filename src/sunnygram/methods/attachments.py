# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The things a message can carry that are not a file.

Everything in methods/media.py describes bytes that have been uploaded. These
describe things that need no upload at all: a poll, a place, a person's card, a
rolled die, or a document that already exists somewhere and is being pointed at
instead of sent again. They are pure builders, so they cost nothing and can be
held onto, and each hands back an InputMedia that send_media takes.

Two conventions worth stating once. A poll option is named by its position, not
by its text, everywhere in this library: option zero is the first answer. And
the protocol spells a position as a single byte, which is done here so that no
caller ever has to.
"""

from __future__ import annotations

from typing import Any

from ..files import parse_ref
from ..migrate import read_foreign_file_id
from ..peers import mark_peer
from ..raw import base, types

__all__ = [
    "DICE",
    "MAX_POLL_ANSWERS",
    "as_contact",
    "as_dice",
    "as_document",
    "as_location",
    "as_photo",
    "as_poll",
    "as_venue",
    "existing_media",
    "media_origin",
    "with_reference",
    "option_bytes",
]

# What Telegram will take, which is fewer than a caller usually expects.
MAX_POLL_ANSWERS = 12

# The animated ones, by what to pass for each. Telegram decides the outcome, so
# these choose the animation instead of the result.
DICE = {
    "dice": "\N{GAME DIE}",
    "dart": "\N{DIRECT HIT}",
    "basketball": "\N{BASKETBALL AND HOOP}",
    "football": "\N{SOCCER BALL}",
    "bowling": "\N{BOWLING}",
    "slots": "\N{SLOT MACHINE}",
}


def option_bytes(index: int) -> bytes:
    """A poll answer's position, as the protocol spells it.

    One byte, which caps a poll at 256 answers and is well above the dozen
    Telegram allows anyway.
    """
    if not 0 <= index < 256:
        raise ValueError(f"{index} is not a poll answer position")
    return bytes((index,))


def as_poll(
    question: str,
    answers: list[str],
    *,
    multiple: bool = False,
    quiz: bool = False,
    correct: int | None = None,
    explanation: str = "",
    anonymous: bool = True,
    closes_in: int = 0,
    closed: bool = False,
) -> base.InputMedia:
    """Describe a poll, or a quiz if one of the answers is the right one.

    A quiz is a poll with a correct answer, and Telegram will not take one
    without it, so passing correct is what makes this a quiz, not the
    flag. The explanation is what people see after answering and only a quiz
    has one.

    closes_in is a number of seconds from sending, which the protocol keeps
    separately from a fixed closing time; anything under five seconds or over a
    week is refused by the server instead of here.
    """
    if not answers:
        raise ValueError("a poll needs some answers")
    if len(answers) > MAX_POLL_ANSWERS:
        raise ValueError(
            f"a poll takes at most {MAX_POLL_ANSWERS} answers, not {len(answers)}"
        )
    if correct is not None and not 0 <= correct < len(answers):
        raise ValueError(f"answer {correct} is not one of the {len(answers)} given")
    if quiz and correct is None:
        raise ValueError("a quiz needs to know which answer is the right one")
    if explanation and correct is None:
        raise ValueError("only a quiz has an explanation, and this one has no answer")

    poll = types.Poll(
        id=0,
        hash=0,
        question=types.TextWithEntities(text=question, entities=[]),
        answers=[
            types.PollAnswer(
                text=types.TextWithEntities(text=text, entities=[]),
                option=option_bytes(index),
            )
            for index, text in enumerate(answers)
        ],
        closed=closed,
        public_voters=not anonymous,
        multiple_choice=multiple,
        quiz=quiz or correct is not None,
        close_period=closes_in or None,
    )
    return types.InputMediaPoll(
        poll=poll,
        correct_answers=None if correct is None else [correct],
        solution=explanation or None,
        solution_entities=[] if explanation else None,
    )


def as_dice(kind: str = "dice") -> base.InputMedia:
    """Roll something. Telegram picks the number, not the sender.

    Takes one of the names in DICE, or the emoji itself for anything added
    since. The result arrives on the message that comes back.
    """
    return types.InputMediaDice(emoticon=DICE.get(kind, kind))


def as_location(
    latitude: float, longitude: float, *, accuracy: int | None = None
) -> base.InputMedia:
    """A point on the map, as a plain location instead of a named place."""
    return types.InputMediaGeoPoint(
        geo_point=types.InputGeoPoint(
            lat=latitude, long=longitude, accuracy_radius=accuracy
        )
    )


def as_venue(
    latitude: float,
    longitude: float,
    title: str,
    address: str,
    *,
    provider: str = "",
    venue_id: str = "",
    venue_type: str = "",
) -> base.InputMedia:
    """A named place, which is a location with a title and an address on it.

    The provider fields identify the place in someone else's directory and are
    only meaningful when the venue came out of an inline bot's results. Sending
    one made up here works and simply carries no link back.
    """
    return types.InputMediaVenue(
        geo_point=types.InputGeoPoint(
            lat=latitude, long=longitude, accuracy_radius=None
        ),
        title=title,
        address=address,
        provider=provider,
        venue_id=venue_id,
        venue_type=venue_type,
    )


def as_contact(
    phone: str, first_name: str, *, last_name: str = "", vcard: str = ""
) -> base.InputMedia:
    """Someone's card. Sending one does not add them to the contact list."""
    return types.InputMediaContact(
        phone_number=phone,
        first_name=first_name,
        last_name=last_name,
        vcard=vcard,
    )


def as_document(document: Any, *, spoiler: bool = False) -> base.InputMedia:
    """Point at a document that already exists rather than sending it again.

    Takes a Document off a message, an InputDocument, or an InputMedia that is
    already one of these and is passed through. Stickers, animations and files
    someone else sent are all documents, which is why there is one call for
    all of them instead of one each.

    The file reference travels with it and goes stale after a while. The file
    engine refreshes one on download; sending is a single call with nowhere to
    put the retry, so a stale reference here comes back as an error and the
    answer is to fetch the message again.
    """
    if isinstance(document, (types.InputMediaDocument, types.InputMediaPhoto)):
        return document
    return types.InputMediaDocument(id=_input_document(document), spoiler=spoiler)


def as_photo(photo: Any, *, spoiler: bool = False) -> base.InputMedia:
    """Point at a photo that already exists, the same way as_document does."""
    if isinstance(photo, (types.InputMediaPhoto, types.InputMediaDocument)):
        return photo
    return types.InputMediaPhoto(id=_input_photo(photo), spoiler=spoiler)


def existing_media(thing: Any, *, spoiler: bool = False) -> base.InputMedia | None:
    """Point at something Telegram already holds, or say this is not one.

    This is what makes re-sending cheap. A file that has been sent once can be
    sent again anywhere by naming it, with no upload and no download in
    between, and the only hard part is recognising the shapes that count: an
    InputMedia that is already one of these, a Document or a Photo off a
    message, the input forms of either, the message itself, or the portable
    reference string that file_ref writes one down as.

    Nothing else is one, and that comes back as nothing instead of as an
    error, so a caller can offer both this and an upload without having to
    know which it was given. That is also why a string that is not a reference
    is nothing, not a complaint: a path is a string too, and telling the
    two apart is exactly what this is for.

    The file reference inside goes stale after a while. Where the caller can
    say which message the file came from, a send renews it and tries once more;
    where it cannot, a stale one comes back as an error and the answer is to
    fetch the message again.

    spoiler hides the file behind a tap. It is asked for here instead of read
    off the file because it belongs to the send and not to the thing being
    sent: the same stored photo goes out plain to one asker and covered to the
    next, which is also why a portable reference never writes it down. It only
    turns hiding on, so a media the caller built hidden stays hidden.
    """
    found = _recognise(thing)
    if found is None or not spoiler:
        return found
    return _hidden(found)


def _hidden(media: base.InputMedia) -> base.InputMedia:
    """The same media, hidden behind a tap.

    A copy instead of the flag set in place, because the media may be the
    caller's own object and a send is not entitled to change it. Anything other
    than these two is a kind Telegram gives a client no way to hide, so it goes
    back as it came rather than pretending.
    """
    if isinstance(media, types.InputMediaPhoto):
        return types.InputMediaPhoto(
            spoiler=True,
            live_photo=media.live_photo,
            id=media.id,
            ttl_seconds=media.ttl_seconds,
            video=media.video,
        )
    if isinstance(media, types.InputMediaDocument):
        return types.InputMediaDocument(
            spoiler=True,
            id=media.id,
            video_cover=media.video_cover,
            video_timestamp=media.video_timestamp,
            ttl_seconds=media.ttl_seconds,
            query=media.query,
        )
    return media


def with_reference(
    media: base.InputMedia, fresh: base.InputMedia
) -> base.InputMedia:
    """The media as it was, pointing at the file as it has just been found.

    What renewal is allowed to change is the token that aged out, and nothing
    else. Sending the freshly fetched media instead is the obvious thing and it
    is wrong: everything the caller said about this particular send lives on
    the media instead of on the file, so a retry built that way silently drops
    whether it is hidden, how long it lives, and the cover on a video. None of
    those can be recovered by fetching the file again, because the file never
    knew them.

    A copy, since the media being carried through the retry may be the
    caller's own object. A fresh one of a different kind means the message now
    carries a different file, and then there is nothing to preserve.
    """
    if isinstance(media, types.InputMediaPhoto) and isinstance(
        fresh, types.InputMediaPhoto
    ):
        return types.InputMediaPhoto(
            spoiler=media.spoiler,
            live_photo=media.live_photo,
            id=fresh.id,
            ttl_seconds=media.ttl_seconds,
            video=media.video,
        )
    if isinstance(media, types.InputMediaDocument) and isinstance(
        fresh, types.InputMediaDocument
    ):
        return types.InputMediaDocument(
            spoiler=media.spoiler,
            id=fresh.id,
            video_cover=media.video_cover,
            video_timestamp=media.video_timestamp,
            ttl_seconds=media.ttl_seconds,
            query=media.query,
        )
    return fresh


def _recognise(thing: Any) -> base.InputMedia | None:
    """Which of the shapes this is, before hiding is considered."""
    if isinstance(thing, str):
        found = parse_ref(thing)
        if found is not None:
            return found.media
        # Not one of ours, so it may be a foreign file id, which is the same
        # idea written down a different way. Reading it costs a project moving
        # over here nothing but the import, and a column full of file ids is
        # otherwise the most expensive thing about leaving.
        return read_foreign_file_id(thing)
    if isinstance(thing, (types.InputMediaDocument, types.InputMediaPhoto)):
        return thing
    if isinstance(thing, (types.InputDocument, types.Document)):
        return types.InputMediaDocument(id=_input_document(thing))
    if isinstance(thing, (types.InputPhoto, types.Photo)):
        return types.InputMediaPhoto(id=_input_photo(thing))

    # A message, or the media off one. Both spell the file the same way, so
    # the message is unwrapped once and the rest is the same two checks.
    carried = getattr(thing, "media", thing)
    carried = getattr(carried, "raw", carried)
    if isinstance(carried, types.MessageMediaDocument):
        document = carried.document
        if isinstance(document, types.Document):
            return types.InputMediaDocument(id=_input_document(document))
    if isinstance(carried, types.MessageMediaPhoto):
        photo = carried.photo
        if isinstance(photo, types.Photo):
            return types.InputMediaPhoto(id=_input_photo(photo))
    return None


def media_origin(thing: Any) -> tuple[int, int] | None:
    """Which message a file came from, or nothing if that cannot be told.

    The one thing a stale file reference needs. A reference is only good for an
    hour or so, and the only cure is to fetch whatever carried the file again,
    which means knowing what that was. A message says so directly, and a
    portable reference says so because it was made from one, so a send can
    renew its own reference and try once more instead of handing the caller an
    error to solve.

    The chat comes back marked the Bot API way, which is one number and is what
    resolve takes back.
    """
    if isinstance(thing, str):
        found = parse_ref(thing)
        return None if found is None else found.origin

    message = getattr(thing, "raw", thing)
    if not isinstance(message, types.Message):
        return None
    marked = mark_peer(message.peer_id)
    return None if marked is None else (marked, message.id)


def _input_document(document: Any) -> base.InputDocument:
    if isinstance(document, types.InputDocument):
        return document
    found = getattr(document, "document", document)
    if isinstance(found, types.Document):
        return types.InputDocument(
            id=found.id,
            access_hash=found.access_hash,
            file_reference=found.file_reference,
        )
    raise TypeError(f"{type(document).__name__} is not a document")


def _input_photo(photo: Any) -> base.InputPhoto:
    if isinstance(photo, types.InputPhoto):
        return photo
    found = getattr(photo, "photo", photo)
    if isinstance(found, types.Photo):
        return types.InputPhoto(
            id=found.id,
            access_hash=found.access_hash,
            file_reference=found.file_reference,
        )
    raise TypeError(f"{type(photo).__name__} is not a photo")
