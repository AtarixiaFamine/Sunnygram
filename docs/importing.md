# Bringing a project over

Two things make moving an existing project expensive, and neither is about
writing code. Your session is an authorization key, so without a way to read the
one you have, trying Sunnygram means logging in again, which for a user account
means a code and possibly a second factor. And your database is full of file
ids, which are worthless if nothing can read them, so every file would have to
be uploaded a second time.

Sunnygram reads both. It writes neither, on purpose: this is a one-way door. A
project kept half in one library and half in another is one account with two
clients on it, which is a harder problem than the migration it postpones.

## Your session

```python
import asyncio
import sunnygram

async def main() -> None:
    imported = sunnygram.read_session("my_account.session")
    print(imported)  # says which library wrote it, and what came across
    await sunnygram.adopt_session(imported, "sunny.session")

asyncio.run(main())
```

After that, `Client("sunny.session", api_id=..., api_hash=...)` starts up already
logged in. The destination is named the way `Client` names one, so the two always
land on the same file; hand it a `Storage` instead when it should live somewhere
other than a file on disk. `read_session` detects the format it was handed, and reads
session strings as well as session files:

```python
imported = sunnygram.read_session("1ApWapzMBuwABAgMEBQ...")
```

The file you point at is opened read-only and left exactly as it was, so going
back is always possible.

### What comes across

| | from a session file | from a session string |
|---|---|---|
| Authorization key and datacenter | yes | yes |
| Update counters (`pts`, `qts`, `seq`) | yes | no |
| Peers and their access hashes | yes | no |
| Who you are (`user_id`, bot or not) | depends on the source format | depends |
| `api_id` | depends on the source format | no |

Where the last two rows say it depends, the difference is in what the format
being read wrote down in the first place. `print(imported)` reports what actually
came across, which is more reliable than a table. Anything missing is learned on
the first call instead.

The update counters are worth more than they look: with them, the first run
carries on from where the old program stopped instead of asking Telegram for
everything it missed.

The peers matter more still. An access hash is what lets you name a chat, and a
project that stores chat ids in its own database cannot reach any of them until
it has met them again. Importing them means it can, from the first call. A
session **string** carries neither, because a string is one pasteable line by
design; a session **file** carries both.

That is the one thing worth planning around: if you have the choice, bring the file
instead of the string.

!!! warning "Stop the old program first"

    An authorization key is one session as far as Telegram is concerned, so two
    programs holding the same key are one client with two heads. Nothing breaks,
    but both will see every update and each will act as though it were alone.
    Migrate, then stop the old one.

## Your file ids

A stored Bot API `file_id` can be handed to anything that sends a file:

```python
await app.send_media(chat, "BQACAgIAAxkBAAIB...")
```

No upload, no download. It works because a file id and Sunnygram's own
`file_ref` say the same thing in different words, and everything that accepts one
now accepts the other.

To look inside one instead of send it:

```python
read = sunnygram.read_file_id("BQACAgIAAxkBAAIB...")
print(read.kind, read.dc_id, read.media_id)
```

Two limits. A file id that names a thumbnail, a profile picture or a wallpaper is
refused, not sent, because those are places inside a file, not files anybody can
post, and Telegram has nothing to send them as. And the file reference inside a file
id goes stale like any other, so a very old one may need the message it came from
fetching again.

Sunnygram does not write this format. Its own [`file_ref`](files.md) remembers which
message a file came from, which lets a stale reference renew itself, and a file id
cannot carry that. Read yours in, write Sunnygram's out.
