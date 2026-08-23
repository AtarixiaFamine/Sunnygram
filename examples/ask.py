"""Ask somebody a few questions and read the answers, in a straight line.

The point of this one is what it does not contain. There is no dictionary of
who is halfway through what, no handler per question, and no state machine: the
code that asks is the code that reads the reply, in the order the conversation
happens in, which is the shape the conversation actually has.

    SUNNYGRAM_API_ID=123456 SUNNYGRAM_API_HASH=... \
        python examples/ask.py @somebody

The account this runs as does the asking, so point it at somebody expecting it.
Options:

    --timeout N   how long to wait for each answer, in seconds

Two things worth watching while it runs. The answers do not reach the handler
this also registers, which is the exclusive default: a program asking somebody's
name should not have its command router reading the name. And a question nobody
answers ends by itself rather than hanging, with a line in the log saying so.

This is not part of the test suite, which stays offline. tests/test_client.py
covers the same paths against a scripted server; what needs a real account is
somebody on the other end typing.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from sunnygram import Client, filters
from sunnygram.errors import NoAnswer
from sunnygram.types import Message


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("who", help="a username, a phone number, or an id")
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


async def interview(app: Client, who: str, timeout: float) -> None:
    async with await app.conversation(who, timeout=timeout) as talk:
        await talk.send("Hello. Two questions, and you can ignore me.")

        name = await talk.wait()
        await talk.send(f"Good to meet you, {name.text}.")

        # A filter says what counts as an answer, so anything else arriving
        # goes on waiting rather than being taken as the reply. Without it a
        # sticker would be somebody's favourite colour.
        colour = await talk.wait(filters=filters.text)
        await talk.send(f"{colour.text} is a fine colour. That is all.")


async def main() -> int:
    options = arguments()
    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH", file=sys.stderr)
        return 1

    # So the "nobody answered" warning is visible, since that is half of what
    # this example is showing.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    app = Client("sunnygram.session", api_id=int(api_id), api_hash=api_hash)

    @app.on_message(filters.incoming & filters.private)
    async def anything_else(client: Client, message: Message) -> None:
        # This never sees the answers above. That is the exclusive default,
        # and running both together is the clearest way to watch it work.
        print(f"the ordinary handler saw: {message.text!r}")

    async with app:
        try:
            await interview(app, options.who, options.timeout)
        except NoAnswer as unanswered:
            print(f"giving up: {unanswered}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
