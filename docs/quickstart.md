# Quickstart

## Before anything

Get an `api_id` and an `api_hash` from [my.telegram.org](https://my.telegram.org/apps).
They identify your application instead of your account. Keep them out of source control:
everything below reads them from the environment.

```bash
pip install sunnygram
export SUNNYGRAM_API_ID=1234567
export SUNNYGRAM_API_HASH=0123456789abcdef0123456789abcdef
```

## A program that answers

```python
import os

from sunnygram import Client, filters

app = Client(
    "my.session",
    api_id=int(os.environ["SUNNYGRAM_API_ID"]),
    api_hash=os.environ["SUNNYGRAM_API_HASH"],
)


@app.on_message(filters.private & filters.text & filters.incoming)
async def echo(client, message):
    await message.reply(f"you said: **{message.text}**")


app.run()
```

The first run asks for your phone number and the code Telegram sends you, and for your
password if the account has one. It writes the key into `my.session` and every run after
that starts straight away.

`run` is `start`, wait, `stop`. A program with its own event loop calls those directly, or
uses the client as a context manager:

```python
async with Client("my.session", api_id=API_ID, api_hash=API_HASH) as app:
    me = await app.get_me()
    await app.send_message("me", f"hello from {me.full_name}")
```

## A program that does one thing and leaves

```python
import asyncio


async def main():
    async with Client("my.session", api_id=API_ID, api_hash=API_HASH) as app:
        async for message in app.get_history("@durov", limit=20):
            print(message.date, message.text)


asyncio.run(main())
```

`get_history` pages the request for you: you say how many you want and read them.

## Signing in as a bot

A bot token works too, over MTProto instead of the Bot API. Do that when a bot needs
something the Bot API does not expose, and worth *not* doing when it does not, since
Moonlygram is a nicer thing to hold for ordinary bot work.

```python
app = Client("bot.session", api_id=API_ID, api_hash=API_HASH)
app.run(bot_token="123456:ABC-DEF...")
```

## What to read next

- [Logging in](login.md) if you want to control the sign-in flow yourself.
- [Sessions](sessions.md) for keeping the key somewhere other than a file.
- [Handling updates](updates.md) and [Filters](filters.md) for the handler side.
- [The raw API](raw-api.md) for everything the friendly layer does not wrap, which is most
  of a very large API.
