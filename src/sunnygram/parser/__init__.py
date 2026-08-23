# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Turning marked-up text into text plus entities, and back.

Two flavours, picked by name. Both answer with the same pair, because that is
what the wire takes: the plain text, and a list saying what is styled where.

    parse("**hi**")                  -> ("hi", [MessageEntityBold(0, 2)])
    parse("<b>hi</b>", "html")       -> the same
    unparse("hi", entities)          -> "**hi**"

Passing None as the mode means the text is already plain and nothing should be
read into it, which is how a caller sends a message full of asterisks without
any of them disappearing.
"""

from __future__ import annotations

from typing import Any

from ..errors import SunnygramError
from . import html, markdown
from .entities import Span, utf16_length

__all__ = [
    "Span",
    "html",
    "markdown",
    "parse",
    "unparse",
    "utf16_length",
]

# Every spelling of the two modes, so that "md", "Markdown" and "markdown" all
# mean the same thing instead of one of them being a silent mistake.
_MODES = {
    "md": "markdown",
    "markdown": "markdown",
    "html": "html",
    "htm": "html",
}


def parse(text: str, mode: str | None = "markdown") -> tuple[str, list[Any]]:
    """Read marked-up text, and answer with the text and its entities."""
    if mode is None:
        return text, []
    chosen = _MODES.get(mode.strip().lower())
    if chosen is None:
        raise SunnygramError(
            f"{mode!r} is not a parse mode. Use markdown, html, or None for "
            "text that should be taken as it is"
        )
    if chosen == "html":
        return html.parse(text)
    return markdown.parse(text)


def unparse(
    text: str, entities: list[Any] | None, mode: str | None = "markdown"
) -> str:
    """Write text and its entities back out as marked-up text."""
    if mode is None:
        return text
    chosen = _MODES.get(mode.strip().lower())
    if chosen is None:
        raise SunnygramError(f"{mode!r} is not a parse mode")
    if chosen == "html":
        return html.unparse(text, entities)
    return markdown.unparse(text, entities)
