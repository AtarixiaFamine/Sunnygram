# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""HTML in, styled text out, and back again.

The same handful of things markdown can say, spelled the way the Bot API spells
them, because that is what most people already have lying around:

    <b> <strong>   <i> <em>   <u> <ins>   <s> <strike> <del>
    <code>   <pre>   <pre><code class="language-python">
    <a href="https://example.com">text</a>
    <a href="tg://user?id=777000">a mention</a>
    <blockquote>   <blockquote expandable>
    <tg-spoiler>   <span class="tg-spoiler">
    <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>

Built on the standard library's parser rather than on expressions, which means
entities like &amp; and attributes in either kind of quote come out right
without any of it being written here. A tag that is not one of the above is
ignored and its contents kept, so a stray <div> costs nothing.
"""

from __future__ import annotations

from html import escape as escape_html
from html.parser import HTMLParser
from typing import Any

from .entities import Span, spans_to_entities, utf16_length
from .markdown import _link_kind, _nesting_rank, _unit

__all__ = ["parse", "unparse"]

_SIMPLE = {
    "b": "bold",
    "strong": "bold",
    "i": "italic",
    "em": "italic",
    "u": "underline",
    "ins": "underline",
    "s": "strike",
    "strike": "strike",
    "del": "strike",
    "code": "code",
    "tg-spoiler": "spoiler",
}


class _Reader(HTMLParser):
    """Collects plain text and the runs of formatting over it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.spans: list[Span] = []
        self.position = 0
        self._open: list[tuple[str, Span]] = []
        # Set while inside a pre, so the code element within it is read as the
        # language instead of as another entity around the same text.
        self._in_pre = False

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        found = dict(attributes)
        if tag == "pre":
            self._in_pre = True
            self._begin("pre", Span("pre", self.position))
            return
        if tag == "code" and self._in_pre:
            language = (found.get("class") or "").removeprefix("language-")
            for _, span in self._open:
                if span.kind == "pre":
                    span.extra = language or None
            return
        if tag == "a":
            kind, extra = _link_kind(found.get("href") or "")
            if kind is not None:
                self._begin(tag, Span(kind, self.position, extra=extra))
            return
        if tag == "blockquote":
            collapsed = "expandable" in found or "collapsed" in found
            self._begin(tag, Span("blockquote", self.position, extra=collapsed))
            return
        if tag == "tg-emoji":
            document = found.get("emoji-id") or found.get("data-document-id") or ""
            if document.isdigit():
                self._begin(tag, Span("emoji", self.position, extra=int(document)))
            return
        if tag == "span":
            if "tg-spoiler" in (found.get("class") or ""):
                self._begin(tag, Span("spoiler", self.position))
            return
        kind = _SIMPLE.get(tag)
        if kind is not None:
            self._begin(tag, Span(kind, self.position))

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre":
            self._in_pre = False
        if tag == "code" and self._in_pre:
            return
        for index in range(len(self._open) - 1, -1, -1):
            if self._open[index][0] == tag:
                _, span = self._open.pop(index)
                span.end = self.position
                self.spans.append(span)
                return

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        self.position += utf16_length(data)

    def close(self) -> None:
        super().close()
        # A tag left open runs to the end instead of being thrown away.
        for _, span in self._open:
            span.end = self.position
            self.spans.append(span)
        self._open.clear()

    def _begin(self, tag: str, span: Span) -> None:
        self._open.append((tag, span))


def parse(text: str) -> tuple[str, list[Any]]:
    """Read HTML, and answer with the plain text and what to style in it."""
    reader = _Reader()
    reader.feed(text)
    reader.close()
    plain = "".join(reader.text)
    return plain, spans_to_entities(reader.spans, plain)


def unparse(text: str, entities: list[Any] | None) -> str:
    """Write styled text back out as HTML."""
    if not entities:
        return escape_html(text, quote=False)

    units = text.encode("utf-16-le")
    # Gathered apart so that runs meeting at the same place can be put in
    # nesting order. Two runs starting on the same character have to open
    # widest first: the other way round produces <i><b>abc</i>de</b>, which is
    # crossed tags rather than nested ones.
    opening_at: dict[int, list[tuple[int, int, str]]] = {}
    closing_at: dict[int, list[tuple[int, int, str]]] = {}
    for entity in entities:
        pair = _tags_for(entity)
        if pair is None:
            continue
        opening, closing = pair
        start = entity.offset
        end = entity.offset + entity.length
        rank = _nesting_rank(entity)
        opening_at.setdefault(start, []).append((end, rank, opening))
        closing_at.setdefault(end, []).append((start, rank, closing))

    marks: dict[int, list[str]] = {}
    # Closings first at any given place, innermost first among themselves.
    for index, closings in closing_at.items():
        closings.sort(key=lambda held: (-held[0], -held[1]))
        marks.setdefault(index, []).extend(tag for _, _, tag in closings)
    for index, openings in opening_at.items():
        openings.sort(key=lambda held: (-held[0], held[1]))
        marks.setdefault(index, []).extend(tag for _, _, tag in openings)

    out: list[str] = []
    # len(units), not utf16_length(text), which would encode the string twice.
    for index in range(len(units) // 2 + 1):
        out.extend(marks.get(index, ()))
        if index * 2 < len(units):
            out.append(escape_html(_unit(units, index), quote=False))
    return "".join(out)


# Built once rather than per entity.
_SIMPLE_TAGS = {
    "MessageEntityBold": "b",
    "MessageEntityItalic": "i",
    "MessageEntityUnderline": "u",
    "MessageEntityStrike": "s",
    "MessageEntityCode": "code",
    "MessageEntitySpoiler": "tg-spoiler",
}


def _tags_for(entity: Any) -> tuple[str, str] | None:
    name = type(entity).__name__
    tag = _SIMPLE_TAGS.get(name)
    if tag is not None:
        return f"<{tag}>", f"</{tag}>"
    if name == "MessageEntityPre":
        language = getattr(entity, "language", "") or ""
        if language:
            return (
                f'<pre><code class="language-{escape_html(language)}">',
                "</code></pre>",
            )
        return "<pre>", "</pre>"
    if name == "MessageEntityBlockquote":
        opening = "<blockquote expandable>" if entity.collapsed else "<blockquote>"
        return opening, "</blockquote>"
    if name == "MessageEntityTextUrl":
        return f'<a href="{escape_html(entity.url)}">', "</a>"
    if name == "MessageEntityMentionName":
        return f'<a href="tg://user?id={entity.user_id}">', "</a>"
    if name == "MessageEntityCustomEmoji":
        return f'<tg-emoji emoji-id="{entity.document_id}">', "</tg-emoji>"
    return None
