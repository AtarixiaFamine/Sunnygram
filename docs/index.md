# Sunnygram

An async, MTProto-native Telegram client library for user accounts.

Sunnygram speaks Telegram's own binary protocol instead of the HTTP Bot API, so it signs in
as a person, or as a bot over MTProto, and reaches the whole client API surface. The stack
underneath is written here from scratch: crypto, transport, session, update state machine.
It is not a wrapper over another library.

Where [Moonlygram](https://github.com/AtarixiaFamine/Moonlygram) covers the Bot API,
Sunnygram covers everything a real account can do. The two share a design philosophy, not
wire code.

```python
from sunnygram import Client, filters

app = Client("my.session", api_id=API_ID, api_hash=API_HASH)


@app.on_message(filters.private & filters.text & filters.incoming)
async def echo(client, message):
    await message.reply(f"you said: **{message.text}**")


app.run()
```

The first run asks for a phone number and a code. Every run after that finds the key in
the session file and asks nothing.

## Install

```bash
pip install sunnygram
```

There are no required dependencies. If `cryptography` happens to be installed, or you ask
for `sunnygram[speedups]`, the AES backend picks it up on its own and the hot path gets
about thirty times faster. Nothing needs configuring either way. See
[Performance](performance.md).

You need an `api_id` and an `api_hash` of your own, from
[my.telegram.org](https://my.telegram.org/apps). They identify the application, not the
account, and are not something to publish.

## What it does

- **Signs in** with a phone number and a code, a second factor over SRP, a QR code another
  client scans, or a bot token. [Logging in](login.md)
- **Keeps the session** in a sqlite file, in memory, or in a string short enough to paste
  into an environment variable. [Sessions](sessions.md)
- **Delivers updates once and in order**, recovering gaps through `getDifference` rather
  than guessing. [Handling updates](updates.md)
- **Sends, edits, deletes, forwards, pins, searches and reads history**, with markdown and
  HTML parsing that counts offsets the way Telegram does. [Messages](messages.md)
- **Sends photos, videos, music, voice notes and files**, and moves them in parts across
  several connections, following a file to whichever datacenter holds it. A file can be
  written down as one string and sent again next week without passing through this machine.
  [Files](files.md)
- **Puts buttons under a message and answers them being pressed**, for a session signed in
  with a bot token. [Buttons](buttons.md)
- **Lists conversations and members**, joins and leaves, and answers about a chat or a
  person. [Chats and people](chats.md)
- **Knows who is who**, resolving `@username`, a phone number, or an id, and caching the
  access hashes so a known peer never costs a call. [Peers](peers.md)
- **Names every error Telegram documents**, all 780 of them, generated from Telegram's own
  table. [Errors](errors.md)
- **Gets out of the way**, because everything the friendly layer does not wrap is one
  `invoke` away. [The raw API](raw-api.md)

## Seeing it work

The test suite is offline and cannot prove a real server agrees with any of it. The
`examples/` are what can: `login.py` signs in, `echo.py` answers people, and `tour.py`
walks the client surface against your own account, printing what it finds.

```bash
SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/tour.py
```

## Where things are

`ARCHITECTURE.md` in the repository is the map: eleven layers from the TL codec up, each
knowing only the one below it, plus the numbered rules the code is held to. It is worth
reading before changing anything, and unnecessary before using it.

## Status

Stable. The protocol stack, the client, and the developer-facing layer are all in place,
the test suite is offline and green, and sign-in, the read surface and a file round trip are
verified against a real account.

Known gaps, as opposed to merely untested ones: voice and video calls are not implemented,
a TLS-disguised MTProxy secret is refused, not guessed at, and an album takes no keyboard,
which is Telegram's own limit. Registering a new account is deliberately absent and will
stay that way: Sunnygram signs in to accounts that already exist.

## License

Mozilla Public License 2.0. Sunnygram may be used in a program of any licence,
including a closed one; changes to Sunnygram's own files are published under the same
licence.
