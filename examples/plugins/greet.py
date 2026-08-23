"""One feature, in its own file, knowing nothing about any other.

There is no client here to decorate with, and that is the point: the decorator
records what this function wants, and load_plugins attaches it to a real client
when the program starts.
"""

from __future__ import annotations

from typing import Any

from sunnygram import filters, plugins


@plugins.on_message(filters.command("hello"))
async def greet(client: Any, message: Any) -> None:
    await message.reply(f"Hello, {message.sender.first_name or 'you'}.")


@plugins.on_message(filters.command("who"))
async def who(client: Any, message: Any) -> None:
    me = await client.get_me()
    await message.reply(f"I am {me.first_name}, running on Sunnygram.")
