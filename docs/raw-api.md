# The raw API

Telegram's API has around two and a half thousand calls and constructors. The friendly
layer wraps the handful people reach for every day. Everything else is right here, fully
typed, and no less supported for being unwrapped:

```python
from sunnygram.raw import functions, types

config = await app.invoke(functions.help.GetConfig())

await app.invoke(
    functions.messages.SetTyping(
        peer=await app.resolve("@durov"),
        action=types.SendMessageTypingAction(),
    )
)
```

This is not an escape hatch bolted on the side. It is the layer the rest of the library is
built on, and a program that lives entirely down here is a perfectly ordinary way to use
Sunnygram.

## The answer has a type

Fully typed above means what it says. Every function in the schema declares what it is
answered with, and `invoke` gives you that, not an `Any` you have to guess your way
through. Your editor completes the fields, and `mypy` catches the ones you got wrong:

```python
config = await app.invoke(functions.help.GetConfig())
#      -> types.Config
config.this_dc          # fine
config.this_dcc         # caught before it runs

statuses = await app.invoke(functions.contacts.GetStatuses())
#        -> list[types.ContactStatus]

ok = await app.invoke(functions.auth.ResetAuthorizations())
#  -> bool
```

Where a TL type has more than one constructor, the answer is the union of them, which is
the honest answer and the useful one: it is a list of the cases you have to handle.

```python
answer = await app.invoke(functions.messages.SendMessage(...))
#      -> types.Updates | types.UpdatesCombined | types.UpdateShort | ...
```

Narrow it the ordinary way, with `isinstance`, and each branch knows its own fields.

The wrappers are generic too, so putting one around a call does not lose the call's type:

```python
config = await app.invoke(
    functions.InvokeWithLayer(layer=LAYER, query=functions.help.GetConfig())
)
#      -> types.Config
```

## Finding the call

The names follow the TL schema exactly, in PascalCase, under their namespace:

| TL | Python |
| --- | --- |
| `help.getConfig` | `functions.help.GetConfig` |
| `messages.sendMessage` | `functions.messages.SendMessage` |
| `channels.getParticipants` | `functions.channels.GetParticipants` |
| `inputPeerUser` | `types.InputPeerUser` |
| `messages.dialogs` | `types.messages.Dialogs` |

[core.telegram.org/methods](https://core.telegram.org/methods) is the reference. Whatever
it lists for the layer Sunnygram is pinned to is here under that name.

```python
from sunnygram.raw import LAYER
print(LAYER)   # the layer this build speaks
```

## Peers

Most calls want an `InputPeer` instead of an id. That is what `resolve` is for:

```python
peer = await app.resolve("@durov")
await app.invoke(functions.messages.GetHistory(peer=peer, ...))
```

Some calls want an `InputChannel` or an `InputUser` instead, which is the same information
in a different wrapper:

```python
peer = await app.resolve("@somechannel")
channel = types.InputChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)
```

## Updates in the answer

The answer to a call often carries update counters. Letting them go is how a program ends
up fetching a difference it did not need:

```python
answer = await app.invoke(functions.messages.SendMessage(...))
await app.updates.feed(answer)
```

The wrapped methods do this for you. A raw call is yours to feed.

## invoke, and the invoker under it

`app.invoke` is the client's. `app.invoker.invoke` is the layer below and takes the same
arguments, typed the same way. Use the client's unless you are working with an invoker
directly, as in the next section.

## Without a Client

The layers underneath stand alone. This is the whole of a program that makes one call:

```python
import asyncio

from sunnygram.network import ClientInfo, Invoker
from sunnygram.raw import functions
from sunnygram.storage import SQLiteStorage


async def main():
    invoker = Invoker(
        SQLiteStorage("my.session"),
        client=ClientInfo(api_id=API_ID, api_hash=API_HASH),
    )
    await invoker.start()
    try:
        print(await invoker.invoke(functions.help.GetConfig()))
    finally:
        await invoker.close()


asyncio.run(main())
```

The invoker keeps a key per datacenter, follows the server when it says the account lives
somewhere else, rebuilds a dropped connection and sends the call again. It does not
dispatch to handlers or wrap anything in friendly types, because that is the client's job.

## What you give up

The friendly layer is doing things you now have to think about: resolving peers, parsing
markdown into entities, inventing a `random_id` so a resend cannot double-post, wrapping
answers, and feeding the update counters. None of it is hard. All of it is easy to forget.

## Importing is cheap

`import sunnygram` loads none of the generated layer. Modules are pulled in as they are
named, so reaching for `functions.messages` costs the messages module and nothing else.
There is no benefit to avoiding these imports.
