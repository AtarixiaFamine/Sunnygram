# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Styled text, and the arithmetic underneath it.

Telegram sends formatting alongside a message rather than inside it: the text is
plain, and a list of entities says that characters 5 to 9 are bold. The catch is
in what a character means. Offsets and lengths are counted in UTF-16 code units,
which is what Java and JavaScript call a character and what Python does not:
anything outside the Basic Multilingual Plane, which is most emoji, counts as
two. Get this wrong and formatting is fine until someone sends an emoji, then
every entity after it is off by one. It is the single most common bug in this
part of every Telegram library, so all the counting happens here.

The rest of the module is the small print the API documentation asks for: an
entity is trimmed before its length is measured, so a bold run that swallowed a
trailing space does not underline it; entities come out in order; and the ones a
client is not allowed to invent, the urls and the hashtags the server finds for
itself, are left to the server.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..raw import types

__all__ = [
    "Span",
    "spans_to_entities",
    "text_and_entities",
    "utf16_length",
]

# What the server works out for itself. A client that sends these is telling
# Telegram something it already knows, and telling it wrong is worse than not
# telling it, so the parsers here do not produce them.
SERVER_FOUND = (
    types.MessageEntityUrl,
    types.MessageEntityMention,
    types.MessageEntityHashtag,
    types.MessageEntityCashtag,
    types.MessageEntityBotCommand,
    types.MessageEntityEmail,
    types.MessageEntityPhone,
    types.MessageEntityBankCard,
)


def utf16_length(text: str) -> int:
    """How long a string is in the units Telegram counts in.

    Every code point in the Basic Multilingual Plane is one unit, everything
    above it is two. Measured by encoding instead of by inspecting each
    character, which is both quicker and harder to get wrong.
    """
    return len(text.encode("utf-16-le")) // 2


@dataclass(slots=True)
class Span:
    """One run of formatting, while it is still being worked out.

    The parsers build these because they know where a run starts before they
    know where it ends, and because a nested run has to be able to close while
    the one around it stays open. kind names the entity to make of it and extra
    carries whatever that entity needs beyond its bounds: a url, a user id, a
    language, a document id.
    """

    kind: str
    start: int
    end: int = -1
    extra: Any = None


def spans_to_entities(spans: list[Span], text: str) -> list[Any]:
    """Turn finished spans into the entities that go on the wire.

    Trailing whitespace is dropped from each run before its length is taken,
    which the API documentation asks for: a run that reads to the end of
    a line should not carry the newline with it. A run left with nothing in it
    is dropped instead of sent as an empty entity.
    """
    units = text.encode("utf-16-le")
    entities: list[Any] = []
    for span in sorted(spans, key=lambda item: (item.start, item.end)):
        start, end = span.start, span.end
        if end < 0:
            end = utf16_length(text)
        while end > start and _unit_is_space(units, end - 1):
            end -= 1
        while start < end and _unit_is_space(units, start):
            start += 1
        if end <= start:
            continue
        entity = _entity(span, start, end - start)
        if entity is not None:
            entities.append(entity)
    return entities


def text_and_entities(text: str, spans: list[Span]) -> tuple[str, list[Any]]:
    """The pair every parser answers with, with nothing sent when nothing is set."""
    entities = spans_to_entities(spans, text)
    return text, entities


def _unit_is_space(units: bytes, index: int) -> bool:
    """Whether one UTF-16 unit is whitespace.

    Only the ones in the Basic Multilingual Plane can be, and a lone surrogate
    is half of something else, so anything paired is not whitespace either.
    """
    pair = units[index * 2 : index * 2 + 2]
    if len(pair) < 2:
        return False
    value = pair[0] | (pair[1] << 8)
    if 0xD800 <= value <= 0xDFFF:
        return False
    return chr(value).isspace()


def _entity(span: Span, offset: int, length: int) -> Any:
    kind = span.kind
    if kind == "bold":
        return types.MessageEntityBold(offset=offset, length=length)
    if kind == "italic":
        return types.MessageEntityItalic(offset=offset, length=length)
    if kind == "underline":
        return types.MessageEntityUnderline(offset=offset, length=length)
    if kind == "strike":
        return types.MessageEntityStrike(offset=offset, length=length)
    if kind == "spoiler":
        return types.MessageEntitySpoiler(offset=offset, length=length)
    if kind == "code":
        return types.MessageEntityCode(offset=offset, length=length)
    if kind == "pre":
        return types.MessageEntityPre(
            offset=offset, length=length, language=span.extra or ""
        )
    if kind == "blockquote":
        return types.MessageEntityBlockquote(
            offset=offset, length=length, collapsed=bool(span.extra)
        )
    if kind == "url":
        return types.MessageEntityTextUrl(
            offset=offset, length=length, url=str(span.extra)
        )
    if kind == "mention":
        return types.MessageEntityMentionName(
            offset=offset, length=length, user_id=int(span.extra)
        )
    if kind == "emoji":
        return types.MessageEntityCustomEmoji(
            offset=offset, length=length, document_id=int(span.extra)
        )
    return None
