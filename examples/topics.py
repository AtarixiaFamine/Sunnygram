"""Forum topics, against a real account.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/topics.py --chat ID

Log in first with examples/login.py, which leaves the session in a file this
picks up. Reading is the default and everything that changes the forum has to be
asked for:

    --chat ID          list the topics in a forum
    --open TITLE       open a topic with that title
    --say TEXT         send a message into --topic
    --topic ID         which topic --say goes to, and what --close acts on
    --close            close that topic
    --reopen           open it again

A topic is the message that opened it, so the id printed for one is a message
id. That is the whole trick and it is worth seeing on a real forum: send into a
topic, then look at the message in an official client and watch it appear in the
right thread.

The offline suite proves these calls are built correctly and cannot prove a real
server agrees, which is what this is for.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from sunnygram import Client

SESSION_FILE = "sunnygram.session"


async def list_topics(app: Client, chat: str) -> None:
    """Read only. Nothing here changes anything for anybody."""
    where = await app.get_chat(chat)
    print(f"\n{where.title or where.id}")
    found = 0
    async for topic in app.get_topics(where.id):
        found += 1
        marks = "".join(
            mark
            for mark, on in (
                ("pinned", topic.pinned),
                ("closed", topic.closed),
                ("hidden", topic.hidden),
            )
            if on
        )
        last = topic.top_message.text[:40] if topic.top_message else ""
        print(f"  {topic.id:>7}  {topic.title:<30} {marks:<8} {last}")
    if not found:
        print("  no topics, which means this is not a forum")


async def run(app: Client, arguments: argparse.Namespace) -> int:
    if arguments.chat:
        await list_topics(app, arguments.chat)

    if arguments.open:
        topic = await app.create_topic(arguments.chat, arguments.open)
        print(f"\nopened topic {topic.id}: {topic.title}")

    if arguments.say:
        if not arguments.topic:
            print("--say needs --topic", file=sys.stderr)
            return 2
        sent = await app.send_message(
            arguments.chat, arguments.say, topic=arguments.topic
        )
        print(f"\nsent message {sent.id} into topic {arguments.topic}")

    if arguments.close or arguments.reopen:
        if not arguments.topic:
            print("--close and --reopen need --topic", file=sys.stderr)
            return 2
        if arguments.close:
            await app.close_topic(arguments.chat, arguments.topic)
            print(f"\nclosed topic {arguments.topic}")
        else:
            await app.reopen_topic(arguments.chat, arguments.topic)
            print(f"\nreopened topic {arguments.topic}")
    return 0


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default=SESSION_FILE)
    parser.add_argument("--chat", required=True, help="the forum, by id or name")
    parser.add_argument("--open", help="a title to open a topic with")
    parser.add_argument("--say", help="something to send into --topic")
    parser.add_argument("--topic", type=int, help="which topic to act on")
    parser.add_argument("--close", action="store_true")
    parser.add_argument("--reopen", action="store_true")
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
