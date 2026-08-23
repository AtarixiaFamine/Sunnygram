"""A bot that uses the events, rather than only messages.

    SUNNYGRAM_BOT_TOKEN=... SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... \
        python examples/events.py

Signs in with a bot token and then does four things a message handler cannot:
answers inline queries, greets people who join a chat it administers, answers
join requests, and counts reactions. It is the shape of a real bot rather than
a list of calls, because the point of these events is what they let a program
be.

What has to be turned on in BotFather for all of it to arrive:

    /setinline          so inline queries reach the bot at all
    /setinlinefeedback  so it is told which result was picked
    /setprivacy off     so it sees more than commands in groups

Add the bot to a group as an administrator to see the rest. Nothing here
changes anybody's chat without being asked: it greets, it counts, and it
answers requests only if APPROVE_JOINS is set.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

from sunnygram import Button, Client, InlineResult, filters, keyboard

SESSION_FILE = "bot.session"

# Turning this on makes the bot let people in by itself. Off by default, since
# an example that quietly starts admitting strangers to somebody's chat is not
# an example, and the request is left in the queue for a person to answer.
APPROVE_JOINS = os.environ.get("APPROVE_JOINS") == "yes"

reactions: Counter[str] = Counter()
picked: Counter[str] = Counter()


def build(token: str, api_id: int, api_hash: str) -> Client:
    app = Client(SESSION_FILE, api_id=api_id, api_hash=api_hash)

    @app.on_inline_query(filters.query(empty=True))
    async def suggest(client: Client, query) -> None:
        """The panel somebody sees before they have typed anything."""
        await query.answer(
            [
                InlineResult.article(
                    "Type something",
                    "This bot repeats what you type.",
                    description="or try: shout hello",
                    id="hint",
                )
            ],
            cache_time=300,
        )

    @app.on_inline_query(filters.query("shout"))
    async def shout(client: Client, query) -> None:
        said = query.text[len("shout") :].strip()
        await query.answer(
            [
                InlineResult.article(
                    f"Shout {said}",
                    said.upper() or "SAY SOMETHING",
                    id="shout",
                    reply_markup=keyboard([Button.callback("Again", "again")]),
                )
            ],
            cache_time=0,
        )

    @app.on_inline_query()
    async def repeat(client: Client, query) -> None:
        """Everything else. Answering is not optional, so this is the floor."""
        await query.answer(
            [
                InlineResult.article(
                    f"Send {query.text}",
                    query.text,
                    description="exactly what you typed",
                    id=f"say:{query.text[:32]}",
                )
            ],
            cache_time=0,
        )

    @app.on_chosen_result()
    async def counted(client: Client, chosen) -> None:
        picked[chosen.id.split(":")[0]] += 1
        print(f"picked {chosen.id} ({dict(picked)})")

    @app.on_chat_member()
    async def doorman(client: Client, change) -> None:
        """The before and after pair is what makes this possible at all."""
        print(f"{change.user_id} {change.what} in {change.chat_id}")
        if change.joined and not change.by_self:
            print(f"  added by {change.actor_id}")
        if change.joined:
            came_from = change.invite_link or "no link"
            await client.send_message(
                change.chat_id, f"welcome, {change.user_id} ({came_from})"
            )

    @app.on_join_request()
    async def waiting(client: Client, request) -> None:
        print(f"{request.user_id} asks to join {request.chat_id}: {request.about!r}")
        if APPROVE_JOINS:
            await request.approve()
            print("  let in")

    @app.on_reaction()
    async def counting(client: Client, change) -> None:
        if change.by_person:
            for one in change.added:
                reactions[str(one)] += 1
            for one in change.removed:
                reactions[str(one)] -= 1
        else:
            for one, count in change.counts.items():
                reactions[str(one)] = count
        print(f"reactions on {change.message_id}: {dict(reactions)}")

    @app.on_stopped()
    async def left(client: Client, event) -> None:
        word = "stopped" if event.stopped else "started"
        print(f"{event.user_id} {word} the bot")

    @app.on_callback_query(filters.data("again"))
    async def again(client: Client, press) -> None:
        # A press on a message an inline query produced: it has no chat, so it
        # is edited by the id Telegram issued for it.
        await press.answer("again!")

    return app


def main() -> int:
    token = os.environ.get("SUNNYGRAM_BOT_TOKEN")
    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not (token and api_id and api_hash):
        print(
            "set SUNNYGRAM_BOT_TOKEN, SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH",
            file=sys.stderr,
        )
        return 2

    app = build(token, int(api_id), api_hash)
    print("listening, ctrl-c to stop")
    app.run(bot_token=token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
