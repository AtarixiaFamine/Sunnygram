"""The surface above the stack, against a real account.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/moderate.py --chat ID

Log in first with examples/login.py, which leaves the session in a file this
picks up. What runs depends on what is asked for, and nothing that changes
somebody else's chat runs without being asked:

    --chat ID       read a chat's settings and your own standing in it
    --album A B C   send an album to Saved Messages
    --poll          send a poll to Saved Messages and vote in it
    --bot @name     ask a bot for inline results, without sending one
    --sessions      list where this account is signed in

The offline suite proves these calls are built correctly and cannot prove a real
server agrees with any of them, which is what this is for.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from sunnygram import Client

SESSION_FILE = "sunnygram.session"


async def look_at_chat(app: Client, chat: str) -> None:
    """Read only. Nothing here changes anything for anybody."""
    where = await app.get_chat(chat)
    print(f"\n{where.title or where.id} ({where.kind.value})")

    me = await app.get_me()
    try:
        rights = await app.get_admin_rights(where.id, me.id)
        allowed = await app.get_permissions(where.id, me.id)
    except Exception as failure:
        # A basic group has no participants call, and a channel this account
        # merely reads may refuse. Both are ordinary answers here.
        print(f"  standing: {type(failure).__name__}: {failure}")
        return
    print(f"  your powers: {', '.join(rights.granted) or 'none'}")
    print(f"  denied to you: {', '.join(allowed.denied) or 'nothing'}")

    print("  members:")
    async for person in app.get_participants(where.id, limit=5):
        print(f"    {person.full_name} ({person.id})")


async def send_an_album(app: Client, files: list[str]) -> None:
    sent = await app.send_album("me", files, captions=["from the example", ""][: len(files)])
    print(f"\nalbum: {len(sent)} messages, ids {[one.id for one in sent]}")
    print(f"  they share album {sent[0].album_id}")


async def send_a_poll(app: Client) -> None:
    poll = await app.send_poll(
        "me", "Does this work?", ["Yes", "No"], anonymous=False
    )
    print(f"\npoll: message {poll.id}")
    await app.vote("me", poll.id, 0)
    standing = await app.get_poll("me", poll.id)
    for answer in standing.results.results or ():
        print(f"  {answer.option!r}: {answer.voters} votes")
    await app.close_poll("me", poll.id)
    print("  closed")


async def ask_a_bot(app: Client, bot: str) -> None:
    """Reads a bot's results and sends none of them."""
    results = await app.inline_query(bot, "test")
    print(f"\n{bot}: {len(results.results)} results, query {results.query_id}")
    for result in results.results[:3]:
        print(f"  {getattr(result, 'title', None) or result.id}")


async def list_sessions(app: Client) -> None:
    print("\nsessions")
    for session in await app.get_sessions():
        here = " (this one)" if session.current else ""
        print(f"  {session.device_model} from {session.country}{here}")


async def run(app: Client, arguments: argparse.Namespace) -> int:
    me = await app.get_me()
    print(f"signed in as {me.full_name} (id {me.id})")

    if arguments.chat:
        await look_at_chat(app, arguments.chat)
    if arguments.album:
        await send_an_album(app, arguments.album)
    if arguments.poll:
        await send_a_poll(app)
    if arguments.bot:
        await ask_a_bot(app, arguments.bot)
    if arguments.sessions:
        await list_sessions(app)

    # Worth printing whatever ran: a number that climbs means the program wants
    # to go faster than the account safely can.
    limiter = app.invoker.limiter
    if limiter is not None and limiter.waited:
        print(f"\npacing held calls back for {limiter.waited:.1f}s")
    return 0


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default=SESSION_FILE)
    parser.add_argument("--chat", help="a chat to read the settings of")
    parser.add_argument("--album", nargs="+", help="files to send as one album")
    parser.add_argument("--poll", action="store_true")
    parser.add_argument("--bot", help="an inline bot to ask, by username")
    parser.add_argument("--sessions", action="store_true")
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
        device_model="Sunnygram example",
    )
    await app.start(catch_up=False)
    try:
        return await run(app, arguments)
    finally:
        await app.stop()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
