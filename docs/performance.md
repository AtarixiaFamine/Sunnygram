# Performance

## The crypto backend

Every byte in and out of Telegram goes through AES-IGE. It is the hot path, and pure
Python is slow at it. Sunnygram picks the fastest backend present at import, in this order:

| Backend | IGE throughput | Install |
| --- | --- | --- |
| `cryptg` | fastest | `pip install sunnygram[speedups]` |
| `tgcrypto` | fast | `pip install tgcrypto` |
| `cryptography` | ~5.9 MiB/s | usually already there |
| bundled pure Python | ~210 KiB/s | nothing to install |

Nothing needs configuring. The library works with none of them installed, which is the
point of having the fallback, and every rung is held to the same test vectors against the
pure Python one, because a fast backend that is subtly wrong corrupts a session rather
than failing it.

The third rung is the one that matters in practice. `cryptography` is already installed in
most environments for other reasons, and it has no IGE, so Sunnygram drives its AES a
block at a time: enough to turn 210 KiB/s into 5.9 MiB/s. Its CTR needs no such trick and
goes from 0.22 MiB/s to 812 MiB/s in one call.

For control traffic even the pure Python path is fine. For [files](files.md) it is not:
a 512 KiB part is about 3.2 seconds of pure Python and 127 ms with `cryptography`. If you
move media, install something.

To find out what you actually got, which is the first thing worth checking when a transfer
is slower than it should be:

```python
from sunnygram.crypto import describe

print(describe())     # "AES: python" is the slow one
```

## The event loop

The other half of the same idea. A Telegram client spends most of its life waiting on a
socket, and what does the waiting is the event loop: asyncio's own is Python around a
selector, and [uvloop](https://github.com/MagicStack/uvloop) is libuv, the event loop node
runs on, wrapped in Cython. Nothing about the library changes. What changes is the cost of
every read, every write, every timer and every task switch underneath it.

| Backend | Where it works | Install |
| --- | --- | --- |
| `uvloop` | Linux, macOS | `pip install sunnygram[speedups]` |
| `winloop` | Windows, same libuv | `pip install sunnygram[speedups]` |
| asyncio's own | everywhere | nothing to install |

`speedups` installs whichever of the two can build on the platform doing the installing,
because uvloop has never shipped a Windows wheel and winloop exists for exactly that gap.

Sunnygram never installs an event loop policy at import. A library that does has quietly
replaced the loop of a program that may have chosen its own, and the surprise turns up in
someone else's code. Instead the choice is made in the one place the library creates a
loop, not joins one:

```python
app.run()                    # uses uvloop or winloop if either is installed
app.run(fast_loop=False)     # asyncio's own, for ruling it in or out of a bug
```

A program with its own loop keeps it, which is right even when the choice was made by not
making it. Opting in from there is one line:

```python
import asyncio
from sunnygram import loop

with asyncio.Runner(loop_factory=loop.new_event_loop) as runner:
    runner.run(main())
```

And the same question as the crypto ladder, answered the same way:

```python
from sunnygram import loop

print(loop.describe())    # "loop: asyncio" is the slow one
```

## Not blocking the loop

A cipher call big enough to be worth the hand-off runs in a worker thread, so a file part
being encrypted does not stop a ping, a read, or anything else in flight. The threshold
moves with the backend, because the hand-off costs more than the work when the work is
quick.

The same applies to the two other CPU-heavy things: the 2048-bit arithmetic of the
handshake, and SRP's PBKDF2, both of which leave the loop.

## Connections

One connection per datacenter for ordinary calls. They have an order, and updates are
counted per session, so spreading them across sockets would buy throughput no one asked for
at the cost of both.

Transfers are different. Telegram meters a connection instead of an account, so a file
opens its own connections to the datacenter it is talking to, as many as it has pieces in
flight, up to four. The pool is sized from how many transfer calls are in hand, not from
how busy the sockets look, because a call that has been given a connection but has not
reached the wire yet is still demand.

## Imports

`import sunnygram` loads no generated code at all. The TL layer is 2495 constructors
across 81 modules and they arrive as they are named. Opening a connection pulls the forty
MTProto service constructors it speaks in and none of the API. The error classes, one per
name in Telegram's published table, are loaded the first time a call is refused, and never
in a program where none is.

## Round trips that do not happen

Two caches exist to turn a call into a dict lookup. The peer cache is the one that has to
be there at all: MTProto needs an access hash for nearly every peer reference, so a peer
met once is never looked up again.

The other is the last thousand messages seen or sent, which answers "what does this reply
to" without asking. A bot whose whole job is answering replies would otherwise pay a call
per message. `message_cache=0` turns it off; `app.recent` says how often it is hitting.

A page of history pairs its own replies up as it is wrapped, and a quoted reply carries an
outline of what it quotes, so those cost nothing either.

## Bounded everything

Caches are bounded LRU, in-flight RPCs are capped by a semaphore, and the update queue
drops the oldest and counts it instead of blocking the connection's reader. A reader that
stops reading is a connection that dies, so back pressure is applied where it can be
survived.

## Numbers worth knowing

Measured on the machine this was written on, so treat them as ratios, not promises:

- Pure-Python AES-IGE: ~210 KiB/s. With `cryptography`: ~5.9 MiB/s. - AES key setup: ~0.06
  ms. - A 512 KiB part through pure-Python CTR: 2.59 s, of which the cipher is 2.27 s and
  the XOR that combines it with the data is 6.0 ms. When this path is slow it is the
  cipher, which the ladder above is for. - Reading a generated object: about 1.65x what the
  obvious shape would cost at fifty fields, which is where `Message`, `User` and `Channel`
  sit, and about 1.35x at five. - Writing one whose layout is fixed: about 4x to 5x on
  `inputPeerUser`, which is named by nearly every outgoing call, and about 2x on a two-int
  constructor. The spread is the honest form of it: four runs on one machine covered that
  range. - `mypy --strict` over the generated tree: ~17 s.

`benchmarks/rules.py` re-measures the codec rows on demand, which is how they stay true.
Rules P3 and P8 in `ARCHITECTURE.md` are where the numbers are quoted from.
