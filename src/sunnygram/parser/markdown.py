# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Markdown in, styled text out, and back again.

Not CommonMark. Telegram's markdown is a handful of delimiters around runs of
text, with no headings, no lists and no paragraphs, because a message is not a
document. What it does have that CommonMark does not is spoilers, mentions of
people by id, and custom emoji, each spelled as a link to a tg: url.

    **bold**   __italic__   ~~strike~~   ||spoiler||   `code`
    ```python
    a block, with the language on the fence
    ```
    [text](https://example.com)      a link
    [name](tg://user?id=777000)      a mention of someone by id
    [👍](tg://emoji?id=5368324170671202286)   a custom emoji
    > a quote, to the end of the line

Delimiters nest, so bold inside italic works, but a delimiter inside code does
not, since the whole point of code is that nothing in it means anything. A
delimiter that is never closed is left as the text it is, which matters more
than it sounds: people write about C**t** and about a || b without meaning any
of this, and a parser that raises at them is a parser that eats messages.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from .entities import Span, spans_to_entities, utf16_length

__all__ = ["parse", "unparse"]

# Longest first, so that ** is never read as two ordinary asterisks.
_DELIMITERS = (
    ("```", "pre"),
    ("**", "bold"),
    ("__", "italic"),
    ("~~", "strike"),
    ("||", "spoiler"),
    ("`", "code"),
)

_ESCAPABLE = set("*_~|`[]()\\>")

_LINK = re.compile(r"\[(?P<text>(?:\\.|[^\]\\])*)\]\((?P<url>(?:\\.|[^)\\])*)\)")


def parse(text: str) -> tuple[str, list[Any]]:
    """Read markdown, and answer with the plain text and what to style in it."""
    out: list[str] = []
    spans: list[Span] = []
    open_spans: dict[str, Span] = {}
    at = 0
    length = len(text)
    position = 0  # in UTF-16 units, which an entity counts in

    def emit(piece: str) -> None:
        nonlocal position
        out.append(piece)
        position += utf16_length(piece)

    while at < length:
        character = text[at]

        if character == "\\" and at + 1 < length and text[at + 1] in _ESCAPABLE:
            emit(text[at + 1])
            at += 2
            continue

        if character == ">" and _at_line_start(out):
            span = Span("blockquote", position)
            line_end = text.find("\n", at)
            body, at = (
                (text[at + 1 :], length) if line_end < 0 else (text[at + 1 : line_end], line_end)
            )
            inner, inner_spans = parse(body.lstrip(" "))
            for nested in inner_spans:
                spans.append(_shifted(nested, position))
            emit(inner)
            span.end = position
            spans.append(span)
            continue

        if character == "[":
            match = _LINK.match(text, at)
            if match is not None:
                label, url = match.group("text"), _unescape(match.group("url"))
                inner, inner_spans = parse(label)
                kind, extra = _link_kind(url)
                if kind is not None:
                    start = position
                    for nested in inner_spans:
                        spans.append(_shifted(nested, start))
                    emit(inner)
                    spans.append(Span(kind, start, position, extra))
                    at = match.end()
                    continue

        found = _delimiter_at(text, at)
        if found is not None:
            token, kind = found
            if kind in open_spans:
                span = open_spans.pop(kind)
                span.end = position
                spans.append(span)
                at += len(token)
                continue
            if kind in ("code", "pre"):
                # Nothing inside these means anything, so the closing delimiter
                # is looked for directly, not by carrying on parsing.
                closed = text.find(token, at + len(token))
                if closed >= 0:
                    body = text[at + len(token) : closed]
                    language = ""
                    if kind == "pre":
                        first, newline, rest = body.partition("\n")
                        if newline and _looks_like_language(first):
                            language, body = first.strip(), rest
                        body = body.strip("\n")
                    start = position
                    emit(body)
                    spans.append(Span(kind, start, position, language or None))
                    at = closed + len(token)
                    continue
            else:
                open_spans[kind] = Span(kind, position)
                at += len(token)
                continue

        emit(character)
        at += 1

    # Whatever never closed was never formatting. Its delimiter is already gone
    # from the text, which is the one thing this cannot undo, so the run simply
    # runs to the end.
    for span in open_spans.values():
        span.end = position
        spans.append(span)

    plain = "".join(out)
    return plain, spans_to_entities(spans, plain)


def unparse(text: str, entities: list[Any] | None) -> str:
    """Write styled text back out as markdown.

    The inverse of parse for everything parse can produce. What the server
    found for itself, a url written plainly or a hashtag, comes back as the
    text it already was, since it needs no marking up to mean the same thing.
    """
    if not entities:
        return _escape(text)

    units = text.encode("utf-16-le")
    marks: dict[int, list[str]] = {}
    # Nothing inside code or a code block means anything, so nothing in there
    # gets escaped either. Escaping it would put backslashes in someone's
    # source listing, which is the one place they are certain to be noticed.
    verbatim: list[range] = []
    for entity in entities:
        pair = _marks_for(entity)
        if pair is None:
            continue
        opening, closing = pair
        start = entity.offset
        end = entity.offset + entity.length
        marks.setdefault(start, []).append(opening)
        marks.setdefault(end, []).insert(0, closing)
        if type(entity).__name__ in ("MessageEntityCode", "MessageEntityPre"):
            verbatim.append(range(start, end))

    out: list[str] = []
    for index in range(utf16_length(text) + 1):
        out.extend(marks.get(index, ()))
        if index * 2 < len(units):
            piece = _unit(units, index)
            plain = any(index in span for span in verbatim)
            out.append(piece if plain else _escape(piece))
    return "".join(out)


def _unit(units: bytes, index: int) -> str:
    """One UTF-16 unit as text, keeping a surrogate pair together."""
    value = units[index * 2] | (units[index * 2 + 1] << 8)
    if 0xD800 <= value <= 0xDBFF and (index + 2) * 2 <= len(units):
        return units[index * 2 : index * 2 + 4].decode("utf-16-le")
    if 0xDC00 <= value <= 0xDFFF:
        # The second half of a pair, already emitted with the first.
        return ""
    return chr(value)


def _marks_for(entity: Any) -> tuple[str, str] | None:
    name = type(entity).__name__
    simple = {
        "MessageEntityBold": ("**", "**"),
        "MessageEntityItalic": ("__", "__"),
        "MessageEntityStrike": ("~~", "~~"),
        "MessageEntitySpoiler": ("||", "||"),
        "MessageEntityCode": ("`", "`"),
    }
    if name in simple:
        return simple[name]
    if name == "MessageEntityPre":
        language = getattr(entity, "language", "") or ""
        return (f"```{language}\n", "\n```")
    if name == "MessageEntityTextUrl":
        return ("[", f"]({entity.url})")
    if name == "MessageEntityMentionName":
        return ("[", f"](tg://user?id={entity.user_id})")
    if name == "MessageEntityCustomEmoji":
        return ("[", f"](tg://emoji?id={entity.document_id})")
    if name == "MessageEntityBlockquote":
        return ("> ", "")
    return None


def _delimiter_at(text: str, at: int) -> tuple[str, str] | None:
    for token, kind in _DELIMITERS:
        if text.startswith(token, at):
            return token, kind
    return None


def _at_line_start(out: list[str]) -> bool:
    return not out or "".join(out[-1:]).endswith("\n")


def _looks_like_language(first: str) -> bool:
    stripped = first.strip()
    return bool(stripped) and all(
        character.isalnum() or character in "+-#._" for character in stripped
    )


def _link_kind(url: str) -> tuple[str | None, Any]:
    """What a link means: an ordinary one, a mention, or a custom emoji."""
    if url.startswith("tg://"):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if parsed.netloc == "user":
            found = query.get("id", [""])[0]
            return ("mention", int(found)) if found.isdigit() else (None, None)
        if parsed.netloc == "emoji":
            found = query.get("id", [""])[0]
            return ("emoji", int(found)) if found.isdigit() else (None, None)
    return "url", url


def _shifted(entity: Any, by: int) -> Span:
    """A finished entity moved along, for text that was parsed on its own."""
    return Span(_kind_of(entity), entity.offset + by, entity.offset + by + entity.length, _extra_of(entity))


def _kind_of(entity: Any) -> str:
    return {
        "MessageEntityBold": "bold",
        "MessageEntityItalic": "italic",
        "MessageEntityUnderline": "underline",
        "MessageEntityStrike": "strike",
        "MessageEntitySpoiler": "spoiler",
        "MessageEntityCode": "code",
        "MessageEntityPre": "pre",
        "MessageEntityBlockquote": "blockquote",
        "MessageEntityTextUrl": "url",
        "MessageEntityMentionName": "mention",
        "MessageEntityCustomEmoji": "emoji",
    }.get(type(entity).__name__, "")


def _extra_of(entity: Any) -> Any:
    for field in ("url", "user_id", "document_id", "language"):
        value = getattr(entity, field, None)
        if value:
            return value
    return None


def _escape(text: str) -> str:
    for character in "\\*_~|`[]":
        text = text.replace(character, "\\" + character)
    return text


def _unescape(text: str) -> str:
    out: list[str] = []
    at = 0
    while at < len(text):
        if text[at] == "\\" and at + 1 < len(text):
            out.append(text[at + 1])
            at += 2
            continue
        out.append(text[at])
        at += 1
    return "".join(out)
