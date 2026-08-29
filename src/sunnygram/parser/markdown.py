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

# The first character of every delimiter above. A character that is not one
# of these cannot begin one, which settles the question for almost every
# character in a message without testing the tokens one at a time.
_DELIMITER_STARTS = frozenset(token[0] for token, _ in _DELIMITERS)


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
        # An entity counts in UTF-16 units, and working that out by encoding is
        # both quicker and harder to get wrong than inspecting each character.
        # Except for text that is entirely ASCII, where the count is the length
        # and the encoding is a copy made to learn nothing. This runs once per
        # character of every message parsed, so the check earns its place.
        position += len(piece) if piece.isascii() else utf16_length(piece)

    while at < length:
        character = text[at]

        if character == "\\" and at + 1 < length and text[at + 1] in _ESCAPABLE:
            emit(text[at + 1])
            at += 2
            continue

        # A blockquote is line-level, so it can only begin where a line does
        # and where nothing inline is still open. Without the second half, a >
        # inside a run took the rest of the line into a parse of its own while
        # the run was still waiting to close, and both ended up covering the
        # same characters: "__>__" came out as two italics over one blockquote
        # rather than one italic holding a >.
        if character == ">" and not open_spans and _at_line_start(out):
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
        return _escape_lines(text)

    units = text.encode("utf-16-le")
    # Nothing inside code or a code block means anything, so nothing in there
    # gets escaped either. Escaping it would put backslashes in someone's
    # source listing, which is the one place they are certain to be noticed.
    verbatim: list[range] = []
    # Gathered apart so that runs meeting at the same place can be put in
    # nesting order before they are written out. Two entities starting on the
    # same character have to open outermost first, or the outer one's mark
    # lands inside the inner one and stops being a mark at all.
    opening_at: dict[int, list[tuple[int, int, str]]] = {}
    closing_at: dict[int, list[tuple[int, int, str]]] = {}
    for entity in entities:
        pair = _marks_for(entity)
        if pair is None:
            continue
        opening, closing = pair
        start = entity.offset
        end = entity.offset + entity.length
        rank = _nesting_rank(entity)
        opening_at.setdefault(start, []).append((end, rank, opening))
        closing_at.setdefault(end, []).append((start, rank, closing))
        if type(entity).__name__ in ("MessageEntityCode", "MessageEntityPre"):
            verbatim.append(range(start, end))

    marks: dict[int, list[str]] = {}
    # Closings first at any given place: a run that ends here has to be closed
    # before one that starts here is opened. Among themselves, whichever
    # started last is the one inside, so it closes first.
    for index, closings in closing_at.items():
        closings.sort(key=lambda held: (-held[0], -held[1]))
        marks.setdefault(index, []).extend(mark for _, _, mark in closings)
    # Then openings, widest first, and a line-level run ahead of an inline one
    # when the two cover exactly the same characters.
    for index, openings in opening_at.items():
        openings.sort(key=lambda held: (-held[0], held[1]))
        marks.setdefault(index, []).extend(mark for _, _, mark in openings)

    out: list[str] = []
    # len(units), not utf16_length(text), which would encode the whole string a
    # second time to count what has already been counted here.
    for index in range(len(units) // 2 + 1):
        out.extend(marks.get(index, ()))
        if index * 2 < len(units):
            piece = _unit(units, index)
            # Most messages have no code in them at all, and that is worth
            # settling before walking the spans once per character.
            plain = bool(verbatim) and any(index in span for span in verbatim)
            if plain:
                out.append(piece)
            elif piece == ">" and (index == 0 or _unit(units, index - 1) == "\n"):
                # A > is only a blockquote marker where a line begins, which is
                # the one place a literal one has to be escaped. Escaping every
                # one of them would put backslashes through ordinary prose, and
                # escaping none of them loses the character: the text comes
                # back as a quote and the > is gone.
                out.append("\\>")
            else:
                out.append(_escape(piece))
    return "".join(out)


# A blockquote is a line-level run: its marker belongs at the start of the
# line, outside everything else that starts there. Everything else is inline
# and nests by width alone.
_LINE_LEVEL = frozenset({"MessageEntityBlockquote", "MessageEntityPre"})

# What opens a blockquote, in the one spelling both halves of this module use.
_QUOTE_MARK = "> "


def _escape_lines(text: str) -> str:
    """Escape a whole run, including any > that would start a blockquote.

    The loop in unparse settles that character by character because it knows
    where it is. This is the plainer path, where there are no entities at all
    and the only question a > raises is which line it sits at the front of.
    """
    escaped = _escape(text)
    if ">" not in escaped:
        return escaped
    return "\n".join(
        "\\" + line if line.startswith(">") else line
        for line in escaped.split("\n")
    )


def _nesting_rank(entity: Any) -> int:
    """How far out a run sits when two of them start on the same character."""
    return 0 if type(entity).__name__ in _LINE_LEVEL else 1


def _unit(units: bytes, index: int) -> str:
    """One UTF-16 unit as text, keeping a surrogate pair together."""
    value = units[index * 2] | (units[index * 2 + 1] << 8)
    if 0xD800 <= value <= 0xDBFF and (index + 2) * 2 <= len(units):
        return units[index * 2 : index * 2 + 4].decode("utf-16-le")
    if 0xDC00 <= value <= 0xDFFF:
        # The second half of a pair, already emitted with the first.
        return ""
    return chr(value)


# Built once rather than per entity, which is what a dict literal inside the
# function below meant.
_SIMPLE_MARKS = {
    "MessageEntityBold": ("**", "**"),
    "MessageEntityItalic": ("__", "__"),
    "MessageEntityStrike": ("~~", "~~"),
    "MessageEntitySpoiler": ("||", "||"),
    "MessageEntityCode": ("`", "`"),
}


def _marks_for(entity: Any) -> tuple[str, str] | None:
    name = type(entity).__name__
    if name in _SIMPLE_MARKS:
        return _SIMPLE_MARKS[name]
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
        return (_QUOTE_MARK, "")
    return None


def _delimiter_at(text: str, at: int) -> tuple[str, str] | None:
    if text[at] not in _DELIMITER_STARTS:
        return None
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


# Built once, and one pass instead of eight. The chained replace this stands
# in for had to escape the backslash first so the ones it added afterwards
# were not escaped again; a translate table has no ordering to get wrong and
# does the whole string in C.
_ESCAPES = str.maketrans(
    {character: "\\" + character for character in "\\*_~|`[]"}
)


def _escape(text: str) -> str:
    return text.translate(_ESCAPES)


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
