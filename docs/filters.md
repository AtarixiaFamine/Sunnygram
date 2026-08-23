# Filters

A filter decides whether a handler sees a message. They compose:

```python
from sunnygram import filters

@app.on_message(filters.private & filters.text & ~filters.bot)
async def handler(client, message): ...
```

`&` for both, `|` for either, `~` for not. The result is another filter, so there is
nothing special about a combined one.

## What there is

**Content**

| Filter | True when |
| --- | --- |
| `text` | there is text and it is not a service message |
| `media` | there is anything attached |
| `photo` | the attachment is a photo |
| `video`, `audio`, `voice`, `sticker` | the attachment is that kind of document |
| `document` | there is a document of any kind |
| `service` | Telegram wrote it, not a person: joins, pins, title changes |

**Direction and origin**

| Filter | True when |
| --- | --- |
| `incoming` / `outgoing` | someone else sent it / we did |
| `reply` | it replies to another message |
| `forwarded` | it came from somewhere else |
| `me` | the sender is us |
| `bot` | the sender is a bot |

**Where**

| Filter | True when |
| --- | --- |
| `private` | one person to another |
| `group` | a group or supergroup |
| `channel` | a broadcast channel |

**Everything and nothing**

`everything` and `nothing`, which are duller than they sound: `everything` is the default
when a handler names no filter, and `nothing` is a readable way to switch a handler off
without deleting it.

## The ones that take arguments

```python
filters.command("start")                     # /start, and /start@somebot
filters.command(["start", "help"])           # either of them
filters.command("start", prefixes="/!")      # /start or !start
filters.command("start", to_me=True)         # only /start@somebot
filters.regex(r"^\d{4}$")
filters.user("durov", 777000)
filters.chat(-1001234567890, "somegroup")
filters.data("yes", "no")                    # a button press carrying one of these
filters.data(prefix="page:")                 # a press whose payload starts with it
```

`to_me` is for a command in a group with more than one bot in it, where the addressed form
is the only one meant for you.

`command` and `regex` leave what they found on the message, so a handler reads it rather
than parsing the text a second time:

```python
@app.on_message(filters.command("say"))
async def say(client, message):
    await message.respond(" ".join(message.arguments))


@app.on_message(filters.regex(r"issue #(\d+)"))
async def issue(client, message):
    await message.reply(f"issue {message.match[1]}")
```

`user` and `chat` take ids or usernames, as many as you like.

## Your own

Any function of a message will do:

```python
long = filters.make(lambda client, message: len(message.text) > 500, "long")

@app.on_message(filters.text & long)
async def handler(client, message): ...
```

The function may be async, which you want if deciding means a call:

```python
async def admin(client, message):
    return message.sender and message.sender.id in await admins_of(message.chat)

@app.on_message(filters.make(admin, "admin"))
async def handler(client, message): ...
```

Filters run for every message that reaches the dispatcher, so an async one that makes a
call runs that call on every message. Cache it.

A filter that raises is reported as a handler error and the update carries on to the next
handler. It does not end the update stream, which matters more than it sounds: a filter
runs on updates its own handler never sees, so one bad filter would otherwise take down
every other feature in the program.

## Button presses

The other thing a handler can be given is a [button press](buttons.md), and most of these
work on one unchanged. A press says who pressed it and in which chat, so `user`, `chat`,
`private`, `group`, `channel`, `me` and `bot` all read what they always read. So does
`regex`, because a press has text: the payload the button was built with.

```python
@app.on_callback_query(filters.data(prefix="page:") & filters.group)
async def turn(client, press): ...
```

The filters asking what kind of media a message carries have nothing to ask a press, and
putting one on `on_callback_query` is reported as a handler error, not quietly matching
nothing.

Signature by signature: [Filters reference](api/filters.md).
