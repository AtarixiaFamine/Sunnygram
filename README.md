<h1 align="center">Sunnygram</h1>

<p align="center">
  <b>An async, MTProto-native Telegram client library for user accounts.</b>
  <br>
  The user-side sibling of Moonlygram.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-stable-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="Python versions">
  <img src="https://img.shields.io/badge/mypy-strict-blue.svg" alt="mypy strict">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MPL--2.0-green.svg" alt="License"></a>
</p>

<p align="center">
  <a href="https://atarixiafamine.github.io/Sunnygram/"><b>Documentation</b></a>
  &middot;
  <a href="https://atarixiafamine.github.io/Sunnygram/quickstart/">Quickstart</a>
  &middot;
  <a href="https://atarixiafamine.github.io/Sunnygram/importing/">Bring your session with you</a>
</p>

---

Sunnygram speaks Telegram's native binary protocol instead of the HTTP Bot API, so it signs in
as a person, or as a bot over MTProto, and reaches the whole client API surface. The stack is
written here from scratch: crypto, transport, session, update state machine. It is not a wrapper
over another library.

Where [Moonlygram](https://github.com/AtarixiaFamine/Moonlygram) covers the Bot API, Sunnygram
covers everything a real account can do.

## Install

```bash
pip install sunnygram
```

No required dependencies. `sunnygram[speedups]` adds a native AES backend and `uvloop`, both
picked up automatically if present. See
[performance](https://atarixiafamine.github.io/Sunnygram/performance/).

You need an `api_id` and an `api_hash` from [my.telegram.org](https://my.telegram.org/apps).

## Example

```python
from sunnygram import Client, filters

app = Client("my.session", api_id=API_ID, api_hash=API_HASH)


@app.on_message(filters.private & filters.text & filters.incoming)
async def echo(client, message):
    await message.reply(f"you said: **{message.text}**")


app.run()
```

The first run asks for a phone number and a code. Every run after that finds the key in the
session file and asks nothing.

```python
async with Client("my.session", api_id=API_ID, api_hash=API_HASH) as app:
    me = await app.get_me()
    await app.send_message("me", f"hello from {me.full_name}")

    async for message in app.get_history("@durov", limit=20):
        if message.has_media:
            await message.download(into=f"{message.id}.bin")

    # Anything unwrapped is one invoke away, typed as what the call answers with.
    from sunnygram.raw import functions
    config = await app.invoke(functions.help.GetConfig())   # -> types.Config
```

## Bring an existing session

```python
imported = sunnygram.read_session("my_account.session")
await sunnygram.adopt_session(imported, "sunny.session")
```

Session files and session strings both read. The peer cache and any stored `file_id` come
across with the key, and the source file is opened read-only.
[Bringing a project over](https://atarixiafamine.github.io/Sunnygram/importing/).

## What it does

Around ninety client methods:

| | |
| --- | --- |
| Send | text, photos, video, music, voice notes, files, albums, polls, quizzes, stickers, dice, locations, venues, contacts |
| Read | history, search, dialogs, members, contacts |
| Act | edit, delete, forward, pin, react, vote, mark read, typing |
| Administer | promote, restrict, ban, titles, photos, permissions, slow mode, invite links, join requests, admin log |
| Talk to bots | press a button by its label, inline queries, start with a parameter |
| Be a bot | keyboards, callback queries, inline mode both ways, the command menu |
| Account | sessions listed and terminated, the second factor, privacy, usernames |
| Forums | topics listed, searched, opened, renamed, closed, pinned |
| Payments | invoices, Telegram Stars, balance, ledger, refunds |
| Stories | posted, edited, pinned, taken down, read |
| Later | any send queued by datetime or `WHEN_ONLINE` |

Twenty-one kinds of event, from messages and edits to inline queries, join requests, reactions
and presence. [Which of them a user account sees and which a bot
does](https://atarixiafamine.github.io/Sunnygram/updates/).

The stack under it, layer by layer:

| | |
| --- | --- |
| `sunnygram.tl` | the TL binary codec, bounds-checked against hostile input |
| `sunnygram.raw` | 2495 constructors and functions at layer 228, generated from a pinned schema |
| `sunnygram.transport` | TCP, four framings including abridged and padded |
| `sunnygram.crypto` | the authorization handshake, AES-IGE and AES-CTR, RSA_PAD, SRP |
| `sunnygram.session` | message ids, envelopes, sequence numbers, containers, replay checks |
| `sunnygram.network` | the connection loop, the invoker, per-datacenter keys, the rate limiter |
| `sunnygram.updates` | `pts` / `qts` / `seq` and gap recovery through `getDifference` |
| `sunnygram.storage` | sqlite, in memory, or a session string |
| `sunnygram.peers` | access hashes learned from every answer, in a bounded LRU |
| `sunnygram.files` | multi-part transfers, cross-datacenter, CDN, stale reference refresh |
| `sunnygram.auth` | phone and code, 2FA over SRP, bot token, QR |
| `sunnygram.errors` | all 780 documented errors, generated, hung off their status codes |

**Not here:** calls above the raw layer, TLS-disguised MTProxy, and account registration, which
is deliberate and permanent. Sunnygram signs in to accounts that already exist.

## Design

- **Generated where it is mechanical.** TL constructors and the error tree come from a pinned
  schema, drift-guarded in CI. Friendly types and client methods are written by hand.
- **Safe by default.** Calls are paced, `FLOOD_WAIT` is honored automatically, secrets never
  reach a log or a `repr`, malformed server data fails closed.
- **Correct updates.** One state machine owns the counters. Every update is delivered once and
  in order, or not at all.
- **Never silent.** Everything the library survives on your behalf goes to the `sunnygram`
  logger, including a handler of yours that raised.
- **Never blocked.** Cipher calls, the handshake's 2048-bit arithmetic and SRP's PBKDF2 all
  leave the event loop.
- **Conversations natively.** `answer = await app.ask(chat, "What is your name?")`, with no
  state machine in between.
- **Plugins.** `app.load_plugins("plugins")` registers every decorated handler in a package.

Rights are said the readable way round, which Telegram's own flags are not. Text is markdown
unless you say otherwise, HTML if you ask, and offsets are counted in UTF-16 the way Telegram
counts them.

## Status

Stable. The protocol stack, the client surface and the documentation are in place.
[`ARCHITECTURE.md`](ARCHITECTURE.md) has the layer stack and the numbered rules the code is
held to.

Over 2200 offline tests, `mypy --strict` across the package, and a scripted MTProto server that
completes a real handshake, plus a live tour against a real account covering sign-in, the read
surface and a file round trip.

Runnable examples in [`examples/`](examples/), each against a real account:
[`login.py`](examples/login.py) signs in and keeps the session,
[`tour.py`](examples/tour.py) walks the client surface,
[`echo.py`](examples/echo.py) answers anybody who writes to you,
[`files.py`](examples/files.py) round-trips a file,
[`adopt.py`](examples/adopt.py) takes over a session from elsewhere,
[`ask.py`](examples/ask.py) holds a conversation,
[`buttons.py`](examples/buttons.py) is a bot with a menu,
[`events.py`](examples/events.py) answers inline queries and greets joiners, and
[`moderate.py`](examples/moderate.py), [`topics.py`](examples/topics.py),
[`shop.py`](examples/shop.py), [`listen.py`](examples/listen.py),
[`plugin_bot.py`](examples/plugin_bot.py) and [`get_config.py`](examples/get_config.py).

## Development

```bash
pip install -e ".[dev]"
ruff check src tests codegen examples
mypy
pytest -q
```

Tests are offline. No account, no credentials, no network.

Two trees are generated and neither is edited by hand:

```bash
python codegen/refresh.py --check    # has Telegram shipped a newer layer?
python codegen/gen_tl.py             # rebuild raw/ from the pinned schema
python codegen/refresh.py --errors   # take a fresh error table
python codegen/gen_errors.py         # rebuild the error tree
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md).

## License

Mozilla Public License 2.0. See [`LICENSE`](LICENSE). Copyright © 2026 AtarixiaFamine.

File-level copyleft: use Sunnygram in a program of any licence, closed included, and publish
changes to Sunnygram's own files under the same one. Your program's code is unaffected.
