"""The whole library in twenty lines: answer anybody who writes to you.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/echo.py

Log in first with examples/login.py, which leaves the session in a file this
picks up. Options:

    --to-me       only answer messages sent to you, not ones you send
    --command     also answer /ping with the round trip time
    --session     which session file to use

Everything here goes through the client: a session file, a filter, a handler,
and a message that knows how to answer itself. What is underneath is nine
layers of protocol, and none of it appears.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from sunnygram import Client, filters

SESSION_FILE = "sunnygram.session"


def main() -> int:
    parser = argparse.ArgumentParser(description="Echo what people write.")
    parser.add_argument(
        "--to-me", action="store_true", help="ignore messages you send yourself"
    )
    parser.add_argument("--command", action="store_true", help="also answer /ping")
    parser.add_argument("--session", default=SESSION_FILE, help="the session file")
    arguments = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH first", file=sys.stderr)
        return 2

    app = Client(
        arguments.session,
        api_id=int(api_id),
        api_hash=api_hash,
        device_model="Sunnygram echo",
    )

    wanted = filters.private & filters.text
    if arguments.to_me:
        wanted = wanted & filters.incoming

    @app.on_message(wanted)
    async def echo(client: Client, message) -> None:
        who = message.sender.full_name if message.sender else "somebody"
        print(f"  <- {who}: {message.text}")
        await message.reply(f"you said: {message.text}")

    if arguments.command:

        @app.on_message(filters.command("ping"), group=1)
        async def ping(client: Client, message) -> None:
            started = time.perf_counter()
            sent = await message.reply("...")
            await sent.edit(f"pong, {(time.perf_counter() - started) * 1000:.0f} ms")

    print("listening, ctrl-c to stop")
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
