"""A second feature, which the first one does not know exists.

Group 1, so it runs after anything in group 0. Every matching handler runs by
default, which is what lets two features share a chat without either being
written around the other.
"""

from __future__ import annotations

from typing import Any

from sunnygram import filters, plugins


@plugins.on_message(filters.text & filters.incoming & ~filters.command("hello"), group=1)
async def echo(client: Any, message: Any) -> None:
    await message.reply(message.text)


def shorten(text: str, limit: int = 40) -> str:
    """Not a handler, and not registered as one. Plain functions stay plain."""
    return text if len(text) <= limit else f"{text[: limit - 1]}…"
