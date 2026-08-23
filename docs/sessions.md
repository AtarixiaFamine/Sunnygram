# Sessions

A session is the authorization key Telegram gave you, the datacenter it belongs to, where
the update stream had got to, and the peer access hashes learned along the way. Keeping it
is what makes the second run start instantly instead of asking for a code again.

## Picking one

The first argument to `Client` decides:

```python
Client("my.session", ...)        # a sqlite file, created if it is not there
Client(":memory:", ...)          # nothing kept; signs in again every run
Client(SQLiteStorage(path), ...) # the same file, said explicitly
Client(StringStorage(text), ...) # a session that travelled as a string
```

A name without an extension gets `.session` appended, so `Client("my")` and
`Client("my.session")` are the same file.

## The file

`SQLiteStorage` is the default and the one to use. It is created readable only by its
owner, runs with `secure_delete` on so a cleared key leaves the file instead of lingering
in a free page, and every call goes through a worker thread because sqlite blocks.

Its schema is versioned and gains tables, not altering them, so a file written by an older
Sunnygram keeps working.

## Strings

A string session is one pasteable line, which makes it the right thing for a container or
a CI secret where a file is awkward:

```python
import os

from sunnygram.storage import StringStorage, encode_session

# from an existing client
print(encode_session(app.invoker.state))

# somewhere else
app = Client(StringStorage(os.environ["SUNNYGRAM_SESSION"]), api_id=..., api_hash=...)
```

The string is exactly 356 characters: a version byte, the datacenter, some flags, the user
id and the 256-byte key, base64'd. A version byte it does not recognise is refused rather
than misread.

Two things deliberately do not travel in it. Only the home datacenter's key is carried, so
a program restored from a string re-handshakes any other datacenter it needs. And the
update counters are left out, because a `pts` per channel has no bound and the string has
to stay one line. A restored session asks `updates.getState` and starts from now, which
means updates from while it was away are not replayed. If that matters, use a file.

!!! warning
    A string session is the account, in one line, in plain text. It is the easiest thing
    in this library to leak by accident: into a log, a traceback, a screenshot, a commit.
    `SessionState` has a redacting `repr` so printing one does not spill it, but
    `encode_session` gives you the real thing and what happens to it is up to you.

## Memory

`MemoryStorage` keeps everything for the life of the process and nothing after it. Useful
for tests, and for a program that genuinely wants a fresh authorization every run, which
is rare: signing in repeatedly is something Telegram notices.

## Your own

`Storage` is a small abstract class: `open`, `load`, `save`, `delete`, `close`, all async
because a real backend blocks somewhere. Implementing it against redis or postgres is a
short afternoon. `load` must return a copy instead of shared state, which lets the three
built-in backends be swapped for each other without anything else changing.

## Where the peer cache lives

The access hashes learned from traffic are part of the session, not a separate thing to
manage. They are written back through the same storage, which is why a second run can
message someone by `@username` without looking them up again. See [Peers](peers.md).

Signature by signature: [Layers reference](api/layers.md#sessions).
