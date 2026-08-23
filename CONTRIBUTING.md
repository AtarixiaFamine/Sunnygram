# Contributing

Thanks for your interest in Sunnygram. This covers the local workflow, the house style,
and the two pieces that are unusual: the generators, and the crypto.

## Setup

```bash
pip install -e ".[dev]"
```

Run the checks the way CI does. All three must pass before anything ships (rule H3):

```bash
ruff check src tests codegen examples
mypy
pytest -q
```

Tests are **offline** (rule H4). No account, no credentials, no network, and that is not
negotiable: a suite that needs a live account is a suite no one can run. The MTProto
handshake is tested end to end against a scripted server in `tests/mtproto_server.py` that
generates its own RSA keypair and completes the DH exchange for real, so "offline" does not
mean "shallow".

The live smoke tests are the `examples/`, and they are for a human to run against a real
account with `SUNNYGRAM_API_ID` and `SUNNYGRAM_API_HASH` set.

## Read ARCHITECTURE.md first

`ARCHITECTURE.md` is the map and the authority: eleven layers, each knowing only the one
below it, and numbered rules a review can point at. H1-H10 are the family bar, S1-S6 are
safety, P1-P7 are speed, C1-C2 are correctness. A change that breaks one of them is not
necessarily wrong, but it needs to say so out loud.

## House style

- **Plain prose** in docstrings and comments (rule H5). No Sphinx cross-references, no
  formal Args/Returns blocks, no em dashes. Comment the *why* of a non-obvious choice;
  the *what* is in the code.
- Public API is re-exported through each package `__init__` with an explicit `__all__`
  (rule H6).
- `mypy --strict` clean, and the package ships `py.typed` (rule H2).
- Comments earn their place. A comment restating the line below it is noise; a comment
  explaining why the obvious approach was rejected is the whole point.

## The generators

Two trees are generated and **neither is edited by hand** (rule H7). CI regenerates both
and fails on any difference.

`src/sunnygram/raw/` is the TL surface: 2495 constructors and functions at a pinned layer.

```bash
python codegen/refresh.py --check    # has Telegram shipped a newer layer?
python codegen/refresh.py            # take it (this is a deliberate act, rule S5)
python codegen/gen_tl.py             # rebuild raw/
```

`src/sunnygram/errors/generated.py` is every error Telegram documents, from Telegram's own
published table:

```bash
python codegen/refresh.py --errors   # take the table, without moving the layer pin
python codegen/gen_errors.py         # rebuild the tree
```

`codegen/overrides.py` holds the small set of deliberate exceptions: constructor ids that do
not reproduce, fields whose declared type lies, error names that are not valid Python
identifiers. An entry that stops being needed after a refresh should be deleted instead of
left to rot.

Changing what is generated means changing the generator or the overrides, never the
output.

## The crypto

`src/sunnygram/crypto/` is treated as frozen (rule S1). It is validated against official
test vectors and against a second implementation in the tests, and several of its pinned
values exist because getting them wrong once was silent, not loud:

- The RSA fingerprint golden vector. Telegram's retired pre-2021 key must fingerprint to
  `C3B42B026CE86B21`. An earlier version prepended a DER-style leading zero and produced
  wrong fingerprints that failed much later, somewhere else.
- The auth-key KDF tests, which flip one byte at a time and assert exactly which offsets
  of the output move.
- The server public keys, which were taken from Telegram Desktop **and** cross-checked
  against tdlib's independent copy. Do not hand-transcribe them; re-run the cross-check.

No "creative" refactor lands here without re-running the vectors. Use `hashlib`, `hmac`,
and `secrets`; never `random`. Every auth-sensitive comparison goes through
`hmac.compare_digest` (rule S6).

## Things that will not be merged

- **Account registration.** Deliberately absent. Bulk account creation is the abuse this
  kind of library attracts, and leaving it out costs a real user one trip to an official
  client.
- **Spam affordances.** No mass-send helpers, no rate-limit bypasses, no "unlimited" modes
  (rule S4). `FLOOD_WAIT` is honored automatically and stays that way.
- **A wrapper over an existing MTProto library.** Wrapping would surrender the two reasons this
  project exists: direct control and update cadence.
- **Anything that logs a secret.** Auth keys and session material never reach a log, a
  `repr`, or an exception message (rule S2). There is a redaction guard; keep it true.

## Releasing

The suite says the code is correct. Nothing in it says the code is still fast, because
the benchmarks do not run in CI and should not: a runner shares its machine, and a
number measured on a busy one is worse than no number. So the speed claims are checked
by hand, once, at the point where they would otherwise go out with a version number on
them.

1. `ruff check src tests codegen examples`, `mypy`, `pytest` green. 2. `PYTHONPATH=src
python benchmarks/rules.py` on a machine doing nothing else. It measures what the numbered
rules in ARCHITECTURE.md claim. If a ratio has moved by more than a few percent, something
the rule describes has changed: either the change is wanted and the rule text moves with it,
or it is a regression and the release waits. Do not carry a number forward that this did not
just produce. 3. `benchmarks/delta.py` as well, if this round changed something for speed.
It is the before-and-after harness and its contents are whatever the round was about, so
rewrite it for the change, not appending to it. 4. Version bumped in `pyproject.toml` and
`src/sunnygram/__init__.py`, which `tests/test_package.py` checks agree. 5. CHANGELOG entry,
with the ratio quoted from step 2 instead of from memory.

Absolute numbers do not travel between machines and are not worth arguing about.
Ratios within one run are the thing, which is why step 2 measures the old shape and
the new one in the same process, minutes apart.

## Pull requests

Say what changed and why. If the change touches a numbered rule, name the rule. If it
touches the wire, say how you know the server agrees, because the offline suite cannot
tell you that on its own.

## Licensing

Sunnygram is under the **Mozilla Public License 2.0**, and a contribution comes in under
the same licence. There is no separate agreement to sign and no copyright assignment: you
keep your copyright, and the licence is what everyone downstream relies on.

MPL is file-level copyleft, so every source file under `src/` carries the three-line
notice from the licence's Exhibit A. A new file needs it too. Files the generators write
get it from the generator rather than by hand, which is the only correct place to put it.

One consequence worth knowing before opening a pull request: **do not paste code from
another Telegram library into this one.** The copyleft ones cannot be incorporated at all
without changing what Sunnygram may be distributed as, and the permissive ones can only be
incorporated by carrying their notice alongside, which makes one file answer to two
licences. Neither is worth it.

Reading another implementation to understand the protocol is fine, and for a protocol
documented as thinly as this one it is sometimes the only way. Copying from one is not. If a
change came from reading someone else's work, say so in the pull request and describe the
behaviour you observed instead of lifting the code that implements it.
