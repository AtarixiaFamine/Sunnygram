# Errors

Everything Sunnygram raises descends from `SunnygramError`, so one `except` catches the
library and lets everything else through.

```
SunnygramError
├── TLError                 the codec: a malformed or unknown object
├── TransportError          the socket, the framing, a server refusing the connection
├── SecurityError           something arrived that should not have
├── PeerNotFound            we cannot name that peer to the server
└── RPCError                the call reached the server and came back refused
    ├── BadRequest          400
    ├── Unauthorized        401
    ├── Forbidden           403
    ├── NotFound            404
    ├── NotAcceptable       406
    ├── Flood               420
    │   ├── FloodWait           .seconds
    │   ├── SlowmodeWait        .seconds
    │   └── TakeoutInitDelay    .seconds
    ├── InternalError       500 and 503
    ├── Timeout             the server gave up waiting on itself
    └── Migrate             303, .dc_id
        ├── PhoneMigrate    NetworkMigrate    UserMigrate
        └── FileMigrate     StatsMigrate
```

## Catching by name

Every error Telegram documents has a class, generated from Telegram's own error table: 780
of them, each with the published explanation as its docstring.

```python
from sunnygram.errors import PeerIdInvalid, MessageTooLong, ChatWriteForbidden

try:
    await app.send_message(peer, text)
except MessageTooLong:
    await app.send_message(peer, text[:4096])
except ChatWriteForbidden:
    ...
```

Catch whichever level says what you mean. `PeerIdInvalid` is one mistake, `BadRequest` is
any of them, `RPCError` is any refusal at all.

The name is the wire name in PascalCase: `PEER_ID_INVALID` is `PeerIdInvalid`,
`FILE_REFERENCE_EXPIRED` is `FileReferenceExpired`.

## Errors carrying a number

Some names have a value in them. `FLOOD_WAIT_42` means wait forty-two seconds:

```python
import asyncio

from sunnygram.errors import FloodWait

try:
    await app.send_message(peer, text)
except FloodWait as flood:
    await asyncio.sleep(flood.seconds)
```

In practice you rarely write that. A short `FLOOD_WAIT` is slept and retried inside the
connection before it ever reaches you; only a long one comes out, because a program should
decide for itself whether to wait an hour.

`.value` holds the number on any error that carries one. `.seconds` and `.dc_id` are the
named readings of it, on the classes where it means that.

## What is always there

```python
except RPCError as error:
    error.code       # the status code the server actually sent
    error.message    # the wire name, as a string
    error.method     # which call was refused, when the caller said
    error.value      # the number in the name, if there was one
```

`error.code` is always the number that arrived. A few names are listed by Telegram under
several codes; the class hangs off the one it usually arrives with, so a `PEER_ID_INVALID`
that arrived as a 403 is still a `BadRequest` instance while `error.code` says 403.

An error added since the last table refresh comes back as its plain status code and keeps
its message. Nothing is guessed from the shape of a name.

## Migrations

You will not usually see these: the invoker follows `PHONE_MIGRATE`, `USER_MIGRATE` and
`NETWORK_MIGRATE` on its own, and the file engine follows `FILE_MIGRATE`. They are in the
tree because a raw call can still hand you one.

## Keeping the table current

```bash
python codegen/refresh.py --errors
python codegen/gen_errors.py
```

That takes Telegram's published table and rebuilds the tree. The layer pin is not touched.
Nothing under `errors/generated.py` is edited by hand, and CI fails if it has been.
