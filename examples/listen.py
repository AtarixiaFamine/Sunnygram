"""Send a message to yourself, then print every message that arrives.

The first thing that is recognisably a Telegram client: it holds a conversation.
It writes to Saved Messages so there is something to see immediately, then sits
on the update stream and prints what comes in, including the message it just
sent, which is how you can tell the counters are working.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/listen.py

Log in first with examples/login.py, which leaves the session in a file this
picks up. Options:

    --send TEXT   what to write to Saved Messages, or nothing to write nothing
    --no-catch-up start from now instead of asking what was missed
    --seconds N   how long to listen for

Stop it and start it again: it picks up where it left off, because the counters
are in the session file too. That is the whole point of the update layer, and
the easiest way to see it is to send yourself something while this is not
running.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timezone

from sunnygram.auth import get_me
from sunnygram.methods import send_message
from sunnygram.network import ClientInfo, Invoker
from sunnygram.raw import types
from sunnygram.storage import SQLiteStorage
from sunnygram.updates import Event, UpdateManager

SESSION_FILE = "sunnygram.session"


def describe(event: Event) -> str | None:
    """One line for an update worth seeing, or nothing for the rest."""
    update = event.update
    if isinstance(update, (types.UpdateNewMessage, types.UpdateNewChannelMessage)):
        message = update.message
        if not isinstance(message, types.Message):
            return f"  [{type(message).__name__}]"
        when = datetime.fromtimestamp(message.date, timezone.utc).strftime("%H:%M:%S")
        who = _who(message, event)
        arrow = "->" if message.out else "<-"
        return f"  {when} {arrow} {who}: {message.message or '[no text]'}"
    if isinstance(update, types.UpdateShortMessage):
        arrow = "->" if update.out else "<-"
        return f"  {arrow} user {update.user_id}: {update.message}"
    if isinstance(update, types.UpdateUserTyping):
        return f"  ... user {update.user_id} is typing"
    return None


def _who(message: types.Message, event: Event) -> str:
    peer = message.from_id or message.peer_id
    if isinstance(peer, types.PeerUser):
        user = event.users.get(peer.user_id)
        name = getattr(user, "first_name", None) if user else None
        return name or f"user {peer.user_id}"
    if isinstance(peer, types.PeerChannel):
        chat = event.chats.get(peer.channel_id)
        return getattr(chat, "title", None) or f"channel {peer.channel_id}"
    if isinstance(peer, types.PeerChat):
        chat = event.chats.get(peer.chat_id)
        return getattr(chat, "title", None) or f"chat {peer.chat_id}"
    return "somebody"


async def main() -> int:
    parser = argparse.ArgumentParser(description="Listen to Telegram.")
    parser.add_argument(
        "--send",
        default="Hello from Sunnygram.",
        help="what to write to Saved Messages first",
    )
    parser.add_argument(
        "--no-catch-up",
        action="store_true",
        help="start from now rather than asking what was missed",
    )
    parser.add_argument("--seconds", type=float, default=60.0, help="how long to listen")
    parser.add_argument("--session", default=SESSION_FILE, help="the session file")
    arguments = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH first", file=sys.stderr)
        return 2

    invoker = Invoker(
        SQLiteStorage(arguments.session),
        client=ClientInfo(
            api_id=int(api_id), api_hash=api_hash, device_model="Sunnygram example"
        ),
    )
    state = await invoker.start()
    if not state.authorized:
        print("log in first: python examples/login.py", file=sys.stderr)
        await invoker.close()
        return 2

    me = await get_me(invoker)
    print(f"signed in as {me.first_name} (id {me.id})")

    manager = UpdateManager(invoker)
    print("asking where the update stream is")
    await manager.start(catch_up=not arguments.no_catch_up)
    print(f"caught up at pts {manager.state.pts}, seq {manager.state.seq}")

    try:
        if arguments.send:
            sent = await send_message(
                invoker, types.InputPeerSelf(), arguments.send, updates=manager
            )
            print(f"sent message {sent.id} to Saved Messages")

        print(f"listening for {arguments.seconds:.0f} seconds, ctrl-c to stop")
        print()
        deadline = asyncio.get_running_loop().time() + arguments.seconds
        seen = 0
        while True:
            left = deadline - asyncio.get_running_loop().time()
            if left <= 0:
                break
            try:
                event = await asyncio.wait_for(manager.events.get(), left)
            except TimeoutError:
                break
            seen += 1
            line = describe(event)
            print(line if line else f"  [{type(event.update).__name__}]")

        print()
        print(f"{seen} updates, now at pts {manager.state.pts}")
        if manager.dropped_events or manager.failures:
            print(
                f"dropped {manager.dropped_events}, failed {manager.failures}"
            )
        print("stop and start again: it resumes from here")
    except KeyboardInterrupt:
        print()
    finally:
        await manager.stop()
        await invoker.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
