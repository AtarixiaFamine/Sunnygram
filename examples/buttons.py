"""A bot with a working menu: keyboards, presses, and editing in place.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... SUNNYGRAM_BOT_TOKEN=... \\
        python examples/buttons.py

This one signs in with a bot token rather than a phone number, because only a
bot may put a keyboard under a message. Write to the bot and it answers with a
menu; press something and the message rewrites itself. Options:

    --session     which session file to use
    --first-match stop each group after the handler that matched

What is worth watching is where the round trips are not. A press carries which
message it is under, so editing costs one call and nothing is fetched first, and
the pager packs its page number into the payload rather than keeping state.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from sunnygram import Button, Client, filters, keyboard

SESSION_FILE = "sunnygram-bot.session"

PAGES = [
    "Page one. The first thing.",
    "Page two. The second thing.",
    "Page three. The last thing.",
]


def menu() -> Any:
    return keyboard(
        [
            [Button.callback("Read", "page:0"), Button.callback("About", "about")],
            [Button.url("Docs", "https://atarixiafamine.github.io/Sunnygram/")],
        ]
    )


def pager(page: int) -> Any:
    buttons = []
    if page > 0:
        buttons.append(Button.callback("Back", f"page:{page - 1}"))
    if page < len(PAGES) - 1:
        buttons.append(Button.callback("Next", f"page:{page + 1}"))
    buttons.append(Button.callback("Close", "close"))
    return keyboard([buttons])


def main() -> int:
    parser = argparse.ArgumentParser(description="A bot with buttons.")
    parser.add_argument("--session", default=SESSION_FILE, help="the session file")
    parser.add_argument(
        "--first-match",
        action="store_true",
        help="stop each group after the handler that matched",
    )
    arguments = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    token = os.environ.get("SUNNYGRAM_BOT_TOKEN")
    if not api_id or not api_hash or not token:
        print(
            "set SUNNYGRAM_API_ID, SUNNYGRAM_API_HASH and SUNNYGRAM_BOT_TOKEN first",
            file=sys.stderr,
        )
        return 2

    app = Client(
        arguments.session,
        api_id=int(api_id),
        api_hash=api_hash,
        device_model="Sunnygram buttons",
        first_match=arguments.first_match,
    )

    @app.on_message(filters.private & filters.incoming)
    async def offer(client: Client, message: Any) -> None:
        await message.reply("What would you like?", reply_markup=menu())

    @app.on_callback_query(filters.data(prefix="page:"))
    async def turn(client: Client, press: Any) -> None:
        page = int(press.text.removeprefix("page:"))
        # Answering is what stops the button spinning, and it is separate from
        # the edit: the edit is the real reply, this is the receipt.
        await press.answer()
        await press.edit(PAGES[page], reply_markup=pager(page))

    @app.on_callback_query(filters.data("about"))
    async def about(client: Client, press: Any) -> None:
        who = press.sender.full_name if press.sender else "you"
        await press.answer(f"Hello {who}. This is Sunnygram.", alert=True)

    @app.on_callback_query(filters.data("close"))
    async def close(client: Client, press: Any) -> None:
        await press.answer("Closed")
        # Nothing but the keyboard changes, which is what edit_markup is for,
        # and passing nothing takes it away.
        await press.edit_markup()

    handled = filters.data("about", "close") | filters.data(prefix="page:")

    @app.on_callback_query(~handled, group=1)
    async def anything_else(client: Client, press: Any) -> None:
        # A press nobody answers spins until it times out, so the last word is
        # a handler that answers whatever the others did not. The filter is
        # what makes it the last word rather than a second one: every handler
        # that matches runs here, so a catch-all has to say what it is not.
        # With --first-match the filter is redundant, which is the difference
        # between the two modes in one line.
        await press.answer()

    print("listening, ctrl-c to stop")
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
