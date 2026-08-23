# Sunnygram Architecture

The contract this codebase is held to: what sits where, what is generated, and the
numbered rules a review can point at. The README says what the library does and the docs
say how to use it; neither is repeated here.

## The layer stack

Bottom to top. Each layer knows only the layer below it. The right column marks
whether the code is generated or hand-written.

```
 10  Client + DX          client.py, methods/, types/, dispatcher, filters, parser   hand
  9  Auth / login         auth/         phone, code, 2FA (SRP), QR, bot login         hand
  8  File engine          files/        chunked up/download, CDN, file_reference      hand
  7  Peer cache           peers/        access_hash resolve + cache                   hand
  6  Storage              storage/      sqlite / memory / string session              hand
  5  Updates              updates/      pts/qts/seq state machine, getDifference       hand
  4  Network / invoke     network/      connection loop, DC migration, RPC routing     hand
  3  MTProto session      session/      salt, session_id, msg_id, acks, containers     hand
  2  Transport            transport/    TCP framing, obfuscation, proxies              hand
  1  Crypto               crypto/       DH auth key, AES-IGE, RSA, PQ, SRP, msg_key     hand
  0  TL core + schema     tl/ + raw/    binary codec (hand) + all constructors (gen)   both
```

### Layer notes

| | |
| --- | --- |
| **0. TL core + schema** | `tl/` is the hand-written codec: `TLObject`, the primitive reader and writer, boxed dispatch. `raw/` is generated, split `types` / `functions` / `base`, imported lazily (rule P7). `mtproto.tl`'s service constructors live in `raw/types/mtproto` and `api.tl`'s in `raw/types/_root`, so speaking the protocol does not mean loading the API. |
| **1. Crypto** | DH handshake and auth-key generation, AES-IGE (the hot path), RSA of the PQ inner data, PQ factorization, MTProto 2.0 `msg_key` derivation, SRP. Security-sensitive and finite. Validated against known vectors. |
| **2. Transport** | TCP plus four framings: intermediate, full, abridged, padded-intermediate. Obfuscation sits below the framing and above the socket, which nothing above it knows about. Proxies live here too: a tunnel is dealt with before the first frame and then forgotten. |
| **3. MTProto session** | The encrypted-message envelope: server salt, session id, message id, sequence numbers, acks, containers, gzip, and recovery from `bad_server_salt` and `bad_msg_notification`. |
| **4. Network / invoke** | Transport and session tied into a live connection with a single receive loop. Routes results to their callers, handles DC config and the `*_MIGRATE` errors, reconnects with backoff, turns `rpc_error` into typed exceptions. |
| **5. Updates** | `pts` / `qts` / `seq` / `date`, per-channel `pts`, gap detection, and recovery via `updates.getDifference` and `getChannelDifference`. Single source of truth for update state. |
| **6. Storage** | Auth keys per DC, the update state, and the peer cache. Backends: sqlite, memory, and a portable string session. |
| **7. Peer cache** | Resolves a username, an id or a phone to an `InputPeer` and caches the access hashes. A known peer must never cost a round trip. |
| **8. File engine** | Chunked upload with the big-file path and parallel parts; download with CDN redirect handling and `FILE_REFERENCE_EXPIRED` refresh. |
| **9. Auth / login** | Phone and code, 2FA over SRP, QR, bot token, session listing and termination, logout. |
| **10. Client + DX** | The product. `Client`, the `methods/` operations, friendly `Message` / `Chat` / `User`, the dispatcher with handler groups, composable filters, markdown and HTML parsing. |

Those operations are plain functions taking an invoker, one module per part of
the API they touch, and `Client` is what turns each into a method and wraps the
answer in a friendly type. They were written as mixins first and the split is
better: a function taking an invoker can be tested without a client and called
by a program that would rather not hold one, where a mixin gave a class its
methods at the price of every one of them needing the whole client to exist.
What it costs is a long `client.py`, since that file now holds one thin wrapper
per operation. Taken deliberately, and the reason the word mixin is gone.

## Package tree


```
src/sunnygram/
  __init__.py            public API, explicit __all__, everything lazy
  client.py              the high-level Client
  utils.py               signed(), and the other small shared things
  loop.py                which event loop Client.run makes, uvloop when there is one
  py.typed

  tl/                    hand-written TL codec
    core.py              TLObject, the reader and writer, boxed dispatch
  raw/                   GENERATED  (do not edit)
    types/  functions/  base/  all.py

  errors/
    base.py              SunnygramError and what can go wrong locally
    rpc.py               RPCError, one class per status code, the valued ones
    generated.py         GENERATED  every error Telegram documents
  crypto/                aes.py accel.py auth_key.py rsa.py factorization.py
                         srp.py mtproto.py
  transport/             tcp.py codec.py obfuscation.py proxy.py
  session/               session.py mtproto.py msg_id.py
  network/               connection.py datacenter.py handshake.py invoker.py
                         limiter.py
  updates/               manager.py state.py
  storage/               base.py sqlite.py memory.py string.py
  peers/                 resolver.py cache.py
  files/                 upload.py download.py location.py parts.py cdn.py
                         ref.py
  auth/                  login.py
  methods/               messages.py media.py attachments.py albums.py
                         reactions.py chats.py admin.py users.py bots.py
                         account.py forum.py
  types/                 message.py chat.py user.py dialog.py rights.py
                         member.py topic.py buttons.py callback.py
  parser/                markdown.py html.py entities.py
  dispatcher.py          handlers, groups, StopPropagation, the questions waiting
  conversation.py        ask and wait, for code that talks rather than listens
  plugins.py             handlers written in their own files, and the loader
  filters.py
  recent.py              the messages lately seen, so a reply costs nothing
  migrate.py             reading session files and file ids written elsewhere

codegen/
  refresh.py             vendor the .tl schema at a pinned layer, and the error table
  parser.py              read the TL grammar
  gen_tl.py              emit raw/ from the schema
  gen_errors.py          emit errors/generated.py from the error table
  overrides.py           the handful of manual tweaks
  schema/                the vendored copies, with a sha256 and layer record

tests/                   offline: TL codec, crypto vectors, update-gap fixtures,
                         codegen drift, a scripted MTProto server
docs/                    mkdocs-material, docstring-driven
examples/                the live smoke tests, for a human with a real account
```

`migrate.py` is the only module in the package that nothing else in the package needs, which
is why it is at the top, not inside `storage/` or `files/` next to the formats it is a
counterpart to. It reads another library's session and another library's file ids, so it has
to see both the storage layer and the peer layer, and putting it under either would be an
import going the wrong way for no gain. Its one connection to the rest is that
`methods/attachments.py` asks it whether a string it does not recognise is a foreign file
id, which is the whole point: a project moving over should not have to know it moved.

Four things sit somewhere other than where their name suggests, all deliberately. `PeerKind`
is in `storage/base.py` instead of an `enums.py`, because it is part of what a session
persists and having it there is what keeps `storage` from importing `peers`. `Handler` is in
`dispatcher.py` rather than a `handlers.py`, because a handler on its own does nothing: it
is a record the dispatcher reads, and splitting the two would be two files that only ever
change together. `types/buttons.py` describes what is about to be sent, not what arrived,
which is the other way round from everything else in `types/`, and it is there anyway
because it is a shape with no call attached and that is what `types/` is. And `recent.py` is
at the top, not under `types/` or `peers/`, because it is neither a shape nor a peer: it is
one bounded cache the client owns, in the same position `filters.py` and `dispatcher.py` are
in.

## Codegen strategy

The same shape as Moonlygram, scaled up. The TL schema is a formal grammar, so it
generates cleanly and carries most of the surface.

- `codegen/refresh.py` vendors a pinned copy of the `.tl` schema (a specific layer) and
  Telegram's error table. The schema is taken at a published client release tag, not off
  `dev`, so the layer we announce in `invokeWithLayer` is one Telegram has actually
  deployed. Pinning the layer is what makes releases reproducible and upgrades deliberate;
  `refresh.py --check` says whether a newer layer has shipped without writing anything.
- `codegen/gen_tl.py` parses the schema and emits `raw/types`, `raw/functions`,
  and `raw/base`. Every generated object serializes and deserializes itself
  through the `tl/` codec.
- `codegen/gen_errors.py` emits the typed error tree from Telegram's published error table,
  one class per documented error with the official explanation as its docstring. The roots
  stay hand-written in `errors/rpc.py`: one class per status code, plus the few carrying
  behavior a table cannot express, which is a value to wait for or a datacenter to go to.
  The generated classes hang off those, so `except FloodWait` and `except BadRequest` both
  keep working while the eight hundred names underneath come from upstream. The error table
  is vendored on its own terms, not at a release tag, since Telegram regenerates it whenever
  it likes; `refresh.py --errors` takes a fresh copy without moving the layer pin.
- `codegen/overrides.py` holds the small set of manual adjustments, the same role
  it plays in Moonlygram.
- CI regenerates and runs `git diff --exit-code` over `raw/` and `errors/`; a
  hand-edit or a stale checkout fails the build. `tests/test_codegen.py` adds the
  drift and round-trip guards.

The generated `raw/` layer is the plumbing. The hand-written `types/` wrappers
and `methods/` functions are the library people actually touch, and they are
where all the docstrings and ergonomics live. Same split as Moonlygram's generated
received types vs hand-written `Message` / `Chat` / `User`.

## Principles and rules

Inherited from Moonlygram, then the new rules for this project. They are numbered
so we can point at them in review.

### Inherited (the family bar)

- **H1** src layout, hatchling build, MPL-2.0, published under the Milky family.
- **H2** `mypy --strict` clean; ships `py.typed`.
- **H3** ruff over `src tests codegen`; all of ruff + mypy + pytest green before
  anything ships.
- **H4** Tests are **offline**. No live account, no real credentials in CI. The
  TL codec, crypto, and update-gap logic are tested against vectors and recorded
  fixtures.
- **H5** Plain-prose docstrings and comments. No Sphinx cross-references, no
  formal Args/Returns blocks. Comment the *why* of a non-obvious choice, and no
  em dashes.
- **H6** Public API re-exported through `__init__` with an explicit `__all__`.
- **H7** Generated code is never hand-edited. CI drift guard plus drift tests.
- **H8** Behavior-bearing and friendly types are hand-written; mechanical data
  types are generated.
- **H9** Docs are docstring-driven (mkdocs-material + mkdocstrings). Accurate
  docstrings keep the reference accurate.
- **H10** CI matrix across supported Python versions.

### New: safety

- **S1** Crypto is validated against official test vectors and is treated as
  frozen: no "creative" refactor lands without re-running the vectors. Use vetted
  primitives (`hashlib`, `hmac`), and `secrets` / `os.urandom` for all
  randomness, never `random`.
- **S2** Secrets never stringify. Auth keys and session material must never appear in logs,
  `repr`, or exception messages. `tests/test_redaction.py` is the guard, and it works two
  ways: it puts a canary key through every object known to hold one, and it walks the
  hand-written package for any class with a secret-shaped field that would inherit a `repr`
  printing it. The second half is the one that matters, because it fails for a class no one
  has thought about yet, which is the only kind this rule is ever broken by.
- **S3** Server data is untrusted. The TL deserializer is bounds-checked and
  fails closed on malformed or oversized input. A length prefix never triggers an
  unbounded allocation.
- **S4** Account-safe by default. Auto-honor `FLOOD_WAIT`, ship sane default rate
  limits, and provide no built-in spam affordances. Same "safe tool" ethos as
  Moonlygram.
- **S5** Reproducible codegen. The TL layer is pinned; the library never silently
  follows upstream schema drift.
- **S6** Constant-time comparison (`hmac.compare_digest`) for every
  auth-sensitive equality check (`msg_key`, SRP).

### New: speed and performance

- **P1** Async-first, one receive loop per connection, never blocked. CPU-bound
  crypto must not stall the loop. The loop itself is part of this: `uvloop` when
  it is installed, chosen in `Client.run` and never installed as a policy at
  import, because the event loop of a program that made its own choice is not
  this library's to replace.
- **P2** Optional accelerated crypto backend, auto-detected, with a pure-Python
  fallback so the library always works with zero native deps. AES-IGE is the hot
  path.
- **P3** Allocation-aware TL codec: `bytes` / `bytearray` / `memoryview`, a single growing
  buffer, no per-field object churn. Reading is the hot path and is optimized as one: a
  generated `read` assigns its fields directly instead of calling `__init__`, and the
  fixed-width readers do their own bounds check instead of paying a call for it. That is why
  the generated code has the shape it has. What it is worth depends on how wide the object
  is, because skipping `__init__` saves a fixed amount per object while the inline bounds
  check saves a call per field: `benchmarks/rules.py` measures about 1.3x on a five-field
  type and about 1.65x at fifty fields. Fifty is the end that matters, since `Message` is 49
  fields, `User` 51 and `Channel` 50, and those are most of what a running program reads.
  Quote the range instead of the top of it. The writing side has its own rule, P8.
- **P4** The peer cache is mandatory and in-memory-fast. Resolving a known peer
  never hits the network. What it holds can go stale, so a call the server
  refuses on the grounds of the peer drops what was cached for it, everywhere
  it was kept: an access hash that has stopped working is worse than none,
  because none resolves again and works while a wrong one fails identically on
  every run of the program.
- **P5** Parallel file transfers: multiple workers across media-DC connections,
  configurable concurrency with backpressure.
- **P6** Bounded everything. Caches are bounded LRU, in-flight RPCs are capped,
  queues apply backpressure. Carries over Moonlygram's bounded-in-flight and LRU
  discipline.
- **P7** Lazy imports for the generated `raw/` package so `import sunnygram` stays cheap and
  does not pull thousands of TL classes eagerly. How the modules are grouped is part of
  this: opening a connection loads the forty MTProto service constructors it speaks in and
  none of the API. This is also why `TLFunction` is generic the way it is. A generated
  function names its result as its type parameter, which lets `invoke` answer with a
  `Config`, not an `Any`, but the parameter is a forward reference into `raw/base` and that
  package has no runtime form. So subscripting is overridden to hand back the class itself
  under `if not TYPE_CHECKING`, and building a generated class allocates no typing
  machinery. Measured by alternating in one process: 18.9 us to create a class plainly, 24.5
  us through the no-op, 37.8 us through a real generic subscript. On
  `raw/functions/messages.py`, the largest module in the tree at 259 functions, that is +0.8
  ms against 111 ms. A real subscript was rejected on those numbers, and separate `.pyi`
  stubs were rejected because a stub shadows the module it describes, so the annotations in
  the generated code would stop being checked at all. The type variable is covariant, which
  is not decorative: a result is only ever something a call gives back, and without
  covariance the ordinary `bool(await invoke(...))` stops compiling.
- **P8** The packed write body. A constructor whose fields are all fixed-width and none of
  them conditional has a layout that is known when the generator runs, so it is written by
  one `struct` call instead of one method call per field. `benchmarks/rules.py` measures it,
  and what to quote is the range, not the best run in it: across four runs on one machine,
  about 4x to 5x on `inputPeerUser`, 3.9x to 4.8x on `pong`, 3.1x on `updates.State` and
  1.9x to 2x on a two-int constructor. Earlier rounds reported 5.5x and 5.9x on
  `inputPeerUser` and neither was reached again, so both were the top of a range being read
  as the middle of one. Quote the range. It catches only small dense constructors, which is
  the point: those are the ones sent in quantity, and nearly every outgoing call names a
  peer. It is a fast path, not a replacement, because `struct` refuses values this library
  accepts, so the field-by-field writing stays underneath it as the fallback and the
  generated body falls through to it on `struct.error`.

### New: correctness and robustness

- **C1** The update manager is the single source of truth for `pts`/`qts`. No
  other layer mutates update state.
- **C2** Reconnect and resume are transparent. A dropped transport never loses
  the session; a re-handshake happens only when genuinely required.
- **C3** Nothing fails quietly. Anything the library survives on the program's
  behalf, and anything it swallows so that the stream can carry on, is said out
  loud through the `sunnygram` logger: a reconnection, a datacenter move, a
  flood wait, a resynchronization, a handler that raised. A library sets no
  handlers and no levels of its own, so warnings and errors reach stderr on
  Python's own fallback and everything else is the program's to ask for. The
  rule exists because the alternative is the worst kind of fault report there
  is, which is "it stopped working and there was nothing in the output".
- **C4** A recovery the code performs is a recovery the code proves. Every
  correction this stack makes for itself has a test where the fault is really
  produced: the clock is really wrong, the pong really never comes, the queue
  really overflows, the server really says it has never heard of us. A recovery
  path with no test is a recovery path that has never run, and the ones here
  had not.
- **C5** The update layer is proved against a model, not a script. The two
  promises in `updates/manager.py` are that every update reaches the program
  exactly once and in the order the server put them in, and a promise of that
  shape cannot be kept by examples: a written test asks the one question its
  author thought of, and a scripted server answers whatever it is asked, so a
  client asking the *wrong* question still gets a plausible answer and the test
  passes. `tests/test_updates_model.py` is the answer. Hypothesis generates the
  sequence of things the server does, and the server is a model that holds the
  real history and derives every answer from it, so a wrong cursor earns the
  empty answer it deserves and an invariant notices what it skipped. The
  invariant that carries the most weight is that a counter is a claim: `pts = N`
  says the first N things have been handled, so everything below our own mark
  has to have reached the program. Both faults this project has actually had in
  that layer are caught by it in under three generated steps, and so is the
  classic form of the fault, where a detected gap is never recovered from and
  the stream silently stops.

## Considered and not done

Three things were considered and deliberately not done, written down so they are not
rediscovered as oversights. Outgoing messages are not coalesced into
`msg_container`, and server salts are not fetched before the current one expires. Both are
real optimisations and both were measured against: the profile says this stack costs about
twenty microseconds to code an update and twenty to wrap it, so frames and round trips are
not where a program's time goes, and the container work in particular lands in the one file
where `msg_id` and `seq_no` ordering is load-bearing. The trade was not worth it. If a real
account ever shows otherwise, that is the evidence to reopen them with.

The third is `CTR.apply`, which XORs a whole buffer by turning it and the keystream into
one integer each. For a 512 KiB file part that is a four-megabit bignum, which reads like
the obvious thing to chunk, and it is not: measured on a 512 KiB part with nothing
installed, the whole call is 2.59 s, of which the keystream is 2.27 s and the XOR is 6.0 ms,
or 0.23%. Chunking it at 8 KiB measured 6.2 ms, which is no faster, because
`int.from_bytes`, `^` and `to_bytes` are each one C loop over the buffer and there is
nothing quadratic to remove. The cost on that path is the cipher, which is already in the
four-table formulation, and the honest answer to a slow one is the ladder in accel.py
rather than a rewrite of the reference. The one real cost is transient memory, 4.3x the
input at peak against about 2x if it were chunked, which is 2.2 MB for a part that only
happens when no backend at all is installed. Not worth making the reference implementation
harder to read for.

## Decisions

Settled at scaffolding time, 2026-07-28.

- **Minimum Python: 3.11.** A step ahead of the family's 3.10. This is a fresh
  codebase and the update and connection layers lean on task groups.
- **Crypto acceleration: pure Python core, a ladder of faster backends above it.**
  Auto-detected at import in order: `cryptg`, `tgcrypto`, `cryptography`, then our own
  implementation as the always-present fallback. The third rung is the one that matters in
  practice, since most environments already carry `cryptography` for other reasons: it has
  no IGE, so we drive its AES a block at a time, which is enough to turn 210 KiB/s into 5.9
  MiB/s. Its CTR needs no such trick and goes from 0.22 MiB/s to 812 MiB/s in one call.
  Every rung is tested against the pure Python one over random data, because a fast backend
  that is subtly wrong corrupts a session, not failing it.
- **A datacenter gets several connections, but only for transfers.** Telegram meters a
  connection instead of an account, so parts of a file spread across four sockets arrive
  several times sooner. Ordinary calls stay on one connection per datacenter: they have an
  order, and updates are counted per session, so spreading them would buy throughput no one
  asked for at the cost of both. A call opts in with `bulk=True`, which the file engine sets
  and nothing else does. The pool grows to match how many transfer calls are in hand at once
  and stops at four, and is sized from that count, not from how busy the connections look,
  because a call that has been handed a connection but has not reached the wire yet is still
  demand.
- **Cipher calls above a threshold leave the event loop.** A 512 KiB file part
  is 3.2 seconds of blocking CPU in pure Python and 127 ms with `cryptography`,
  and neither belongs on the loop. The threshold moves with the backend, since
  the hand-off costs more than the work when the work is quick.
- **Default storage: sqlite and string sessions together.**
  They share one base, so shipping one without the other saves nothing.
- **raw/ split: `types` / `functions` / `base`.** The proven shape.
- **License: MPL-2.0.** The family's other libraries are MIT; this one is not, and
  the difference is deliberate. File-level copyleft keeps improvements to the protocol
  stack itself in the open without asking anything of a program that merely imports it,
  which is the trade MIT does not offer and LGPL overcharges for.
