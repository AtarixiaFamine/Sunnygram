# Plugins

A program that grows past one file wants its features in separate ones. The obstacle is
that the decorators are methods on a client, so a file written to be imported has no `app`
to decorate with and should not have to be handed one to be readable.

So the intent is recorded on the function and attached later.

```python
# plugins/greet.py
from sunnygram import filters, plugins

@plugins.on_message(filters.command("hello"))
async def greet(client, message):
    await message.reply("Hello yourself")
```

```python
# main.py
from sunnygram import Client

app = Client("my.session", api_id=API_ID, api_hash=API_HASH)
app.load_plugins("plugins")
app.run()
```

Every module in the package is imported, and every function in it carrying one of the
decorators is registered. The package needs an `__init__.py`, so that a traceback from
inside a plugin says which plugin it came from.

## The decorators

The same twenty-one the client has, with the same names, taking the same filters and the
same `group`:

```python
@plugins.on_message(filters.text)
@plugins.on_callback_query(filters.data("yes"))
@plugins.on_inline_query()
@plugins.on_edited(group=1)
```

Stacking two of them on one function registers it twice, once per kind, which is usually
what someone stacking them meant.

The decorator is `@plugins.on_message(...)` instead of a method on the client. Hanging
these off the class would mean each of the twenty-one has to accept a filter where the
client belongs, and giving that up is not worth what it costs in what your editor can tell
you.

## What it will not do quietly

**A plugin that fails to import raises.** It is not skipped with a warning. A feature that
is silently absent looks exactly like a program with nothing to do, and that is the fault
class this library refuses everywhere.

**A package with no handlers in it says so.** Not an error, since a package of helpers is a
reasonable thing to point at, but it is nearly always the decorators having been left off,
and nothing else in the program would ever mention it.

**Loading twice registers twice.** `load_plugins` returns how many handlers it registered,
and calling it twice on the same package gives you each handler twice, which means every
message answered twice by code that appears once in the source. The count is there to be
read.

## Choosing what loads

```python
app.load_plugins("plugins", exclude=("weather",))
app.load_plugins("plugins", include=("greet", "echo"))
```

Names are modules without the package in front. A module whose name starts with `_` is
never loaded, which is where shared code between plugins goes.
