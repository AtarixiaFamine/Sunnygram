# Logging

Sunnygram logs through the standard library, under the `sunnygram` logger and
one child per module. It sets up no handlers and no levels of its own, which is
what a library is supposed to do: the program decides where its output goes.

With no configuration at all you still see warnings and errors, because Python's
own fallback prints those to standard error. That is deliberate. The things
Sunnygram says at those levels are the things you would otherwise have to guess
at.

## Turning it up

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
```

`INFO` is the useful setting for a program you are running and watching. It
covers the moments where the library does something on your behalf: a
reconnection, a move to another datacenter, a pause because Telegram asked for
one, a catch-up after updates went missing.

```python
logging.getLogger("sunnygram").setLevel(logging.DEBUG)
```

`DEBUG` adds the per-connection detail. It is noisy and occasionally what you
need.

## Turning it down

```python
logging.getLogger("sunnygram").setLevel(logging.CRITICAL)
```

Or one part of it, if a particular thing is chattier than you want:

```python
logging.getLogger("sunnygram.network.invoker").setLevel(logging.ERROR)
```

## What gets said, and why

| Level | What it means |
|---|---|
| `ERROR` | A handler of yours raised and no one caught it. |
| `WARNING` | Something was lost or given up on: a connection that stopped answering, updates dropped because nothing was draining them, a call abandoned after its retries. |
| `INFO` | The library did something for you that changed how the program is behaving: reconnected, moved datacenter, waited out a flood, caught up on updates. |
| `DEBUG` | Detail for working out a specific problem. |

The `ERROR` case is worth calling out. A handler that raises does not stop the
update stream, and nothing above the dispatcher ever sees that exception, so if
it were not logged it would not be reported anywhere: your program would simply
appear to ignore some messages. If you would rather handle that yourself, set
`on_error` and the logging stops:

```python
async def report(failure: BaseException, handler) -> None:
    await app.send_message("me", f"{handler.kind} handler failed: {failure!r}")

app.dispatcher.on_error = report
```

## What is never logged

Authorization keys, session material, your `api_hash`, and 2FA passwords do not
appear in log output at any level, and neither do the `repr`s of the objects
that hold them. That is rule S2 in `ARCHITECTURE.md` and there are tests on it.
Message text is not logged either: the library has no business writing your
conversations to a file.
