# Benchmarks

Two harnesses. Neither runs in CI: both need a machine that is not doing
anything else, and a number measured on a busy laptop is worse than no number.

- `delta.py` puts Sunnygram next to itself, for a change that is supposed to
  make something faster. Its contents are whatever the current round is
  measuring, so it is rewritten rather than added to.
- `rules.py` re-measures the claims ARCHITECTURE.md makes with a number in
  them, which is the one that outlives a round. It is a release step: see
  CONTRIBUTING.md.

## Running them

```bash
PYTHONPATH=/path/to/Sunnygram/src python benchmarks/rules.py
```

`rules.py` needs nothing but this library, since what it compares Sunnygram
against is a twin of Sunnygram written the way the rule decided not to.

## Two ways these lie

**An async benchmark must enter the event loop once.** Calling
`run_until_complete` per iteration costs about a hundred microseconds of its
own, which is more than most of what is being measured. Timed that way the
command filter read eight thousand a second; timed inside a single coroutine it
reads two hundred and thirty thousand. Same code, same machine, wrong by thirty
times.

**A before-and-after must alternate.** Run the old implementation, then the new
one, then the old one again, several times over, and take the median. Machines
speed up and slow down while they are being measured: three single-shot runs of
the same change here reported +29%, +51% and +20%, and only the alternating
median was true.

And absolute numbers do not travel. The same machine measured AES-IGE at 97 MB/s
one week and 55 MB/s the next. Ratios within one run are the thing worth
quoting.
