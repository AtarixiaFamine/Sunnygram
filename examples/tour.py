"""A tour of what the client can do, against a real account.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/tour.py

Log in first with examples/login.py, which leaves the session in a file this
picks up. Options:

    --send FILE   also send a file to Saved Messages and read it back
    --members ID  also list the first members of a chat you are in
    --session     which session file to use

Everything without --send only reads. The offline suite can prove these calls
are built correctly and cannot prove a real server agrees with any of it, which
is what this is for: run it once after changing anything above the invoker.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from sunnygram import Client

SESSION_FILE = "sunnygram.session"


async def tour(app: Client, arguments: argparse.Namespace) -> int:
    me = await app.get_me()
    print(f"signed in as {me.full_name} (id {me.id})\n")

    print("dialogs")
    async for dialog in app.get_dialogs(limit=10):
        unread = f"{dialog.unread} unread" if dialog.unread else "read"
        muted = ", muted" if dialog.muted else ""
        last = dialog.top_message.text if dialog.top_message else ""
        print(f"  {dialog.chat.title or dialog.chat.id}: {unread}{muted}")
        if last:
            print(f"     last: {last[:60]}")

    print("\ncontacts")
    contacts = await app.get_contacts()
    for person in contacts[:10]:
        print(f"  {person.full_name} {person.username and '@' + person.username or ''}")
    print(f"  ({len(contacts)} in total)")

    print("\nsaved messages, most recent first")
    async for message in app.get_history("me", limit=5):
        kind = "media" if message.has_media else "text"
        print(f"  {message.id} [{kind}] {message.text[:60]}")

    if arguments.members:
        print(f"\nmembers of {arguments.members}")
        async for user in app.get_participants(_peer(arguments.members), limit=10):
            print(f"  {user.id} {user.full_name}")

    if arguments.send:
        source = Path(arguments.send)
        if not source.is_file():
            print(f"{source} is not a file", file=sys.stderr)
            return 2
        print(f"\nsending {source.name} to Saved Messages")
        sent = await app.send_file(
            "me",
            source,
            caption=f"sent by **Sunnygram**: `{source.name}`",
            progress=lambda done, total: print(
                f"\r  up {done * 100 // max(total, 1)}%", end="", flush=True
            ),
        )
        print(f"\r  sent as message {sent.id}")
        if sent.has_media:
            back = await sent.download()
            same = back == source.read_bytes()
            print(f"  read back {len(back):,} bytes, identical: {same}")
            if not same:
                return 1

    print("\nall of it worked")
    return 0


def _peer(text: str) -> str | int:
    """A chat given on the command line, as an id if that is what it is."""
    try:
        return int(text)
    except ValueError:
        return text


async def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise the client for real.")
    parser.add_argument("--send", help="a file to send to Saved Messages")
    parser.add_argument("--members", help="a chat to list the members of")
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
        device_model="Sunnygram tour",
    )
    # Not catching up on the way in: this is a one-shot script and fetching
    # everything that happened while it was not running would be a slow start
    # for no benefit.
    await app.start(catch_up=False)
    try:
        return await tour(app, arguments)
    finally:
        await app.stop()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
