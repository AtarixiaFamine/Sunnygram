# Handling updates

## Handlers

A handler is a function taking the client and the thing that happened:

```python
@app.on_message(filters.text)
async def seen(client, message):
    print(message.chat, message.text)


@app.on_edited()
async def changed(client, message):
    print("edited:", message.text)


@app.on_callback_query(filters.data(prefix="page:"))
async def pressed(client, press):
    await press.answer()


@app.on_chat_member()
async def greeter(client, change):
    if change.joined:
        await client.send_message(change.chat_id, "welcome")


@app.on_raw()
async def everything(client, event):
    print(event.update)
```

## Every kind of handler

| decorator | what the handler is given | what it is about |
| --- | --- | --- |
| `on_message` | [`Message`](messages.md) | a new message |
| `on_edited` | `Message` | a message changed after it was sent |
| `on_scheduled` | `Message` | a message queued for later rather than sent |
| `on_album` | `list[Message]` | several messages sent as one block |
| `on_callback_query` | [`CallbackQuery`](buttons.md) | an inline button pressed |
| `on_inline_query` | [`InlineQuery`](inline.md) | someone typing the bot's name |
| `on_chosen_result` | [`ChosenResult`](inline.md) | one of its results picked |
| `on_chat_member` | `MemberUpdate` | a member's standing in a chat changing |
| `on_join_request` | `JoinRequest` | someone asking to be let in |
| `on_deleted` | `DeletedMessages` | messages being deleted |
| `on_reaction` | `ReactionUpdate` | reactions on a message changing |
| `on_poll` | `Poll` | a poll's standing changing |
| `on_poll_vote` | `PollVote` | one person voting in a public poll |
| `on_shipping` | [`ShippingQuery`](payments.md) | Telegram asking what delivery costs |
| `on_pre_checkout` | [`PreCheckoutQuery`](payments.md) | the last question before a charge |
| `on_story` | [`Story`](stories.md) | a story posted, changed or taken down |
| `on_status` | `Status` | someone coming online or going offline |
| `on_typing` | `Typing` | someone typing, recording, uploading |
| `on_blocked` | `Blocked` | this account blocking someone |
| `on_stopped` | `Stopped` | someone stopping a bot |
| `on_raw` | `Event` | every update, as it came off the wire |

`on_raw` hands you the `Event` the update manager produced, with the update as it came off
the wire plus the users and chats that arrived alongside it. That is the escape hatch for
anything the friendly layer does not wrap, which is still a great deal: Telegram has
hundreds of update types.

Without a decorator:

```python
handler = app.add_handler(seen, kind="message", filters=filters.text, group=1)
app.remove_handler(handler)
```

`kind` is one of the words in the table above and is a fixed list, not any string, so
`kind="calback"` is a type error, not a handler that silently never runs.

## Which session sees what

Sunnygram signs in as a user account or, with a bot token, as a bot. Several of these
updates only ever arrive for one of the two, and a handler that never fires is worse than
one that errors, so check before writing one:

| kind | user account | bot |
| --- | --- | --- |
| `message`, `edited`, `album`, `deleted`, `typing` | yes | yes |
| `scheduled` | yes | yes |
| `chat_member` | the chats it is in | the chats it administers |
| `poll`, `poll_vote` | yes | yes |
| `callback` | on its own bots' messages | yes |
| `inline_query`, `chosen_result` | no | yes |
| `join_request` | no | yes, where it administers |
| `stopped` | no | yes |
| `shipping`, `pre_checkout` | no | yes, and only for what it sold |
| `story` | yes | no, a bot has no stories |
| `status`, `blocked` | yes | no |
| `reaction` | the running totals | one person's, before and after |

The reaction row is the one that catches people out. They are not two views of the same
message: the totals never say who, and the per-person reading never says how many.
`update.by_person` says which one arrived.

A bot is also subject to Telegram's own privacy setting in groups: unless privacy mode is
turned off in BotFather, it sees commands addressed to it, not every message.

## Groups

Handlers live in numbered groups and run in group order. **Every** handler that matches
runs, not just the first one:

```python
@app.on_message(filters.command("start"), group=0)
async def greet(client, message): ...


@app.on_message(filters.everything, group=1)
async def log(client, message): ...
```

Both of those run for `/start`. To stop the ones after, raise:

```python
from sunnygram import StopPropagation

@app.on_message(filters.command("stop"))
async def only_this(client, message):
    await message.reply("handled")
    raise StopPropagation
```

## First match wins

If your handlers are a list of commands, two of them matching one message is a mistake,
not a feature, and saying so once beats raising `StopPropagation` in every one:

```python
app = Client("my.session", api_id=..., api_hash=..., first_match=True)
```

Each group then stops after the first handler in it whose filter said yes. Later groups
still get their turn, so a logger in group 1 still sees everything a command in group 0
handled.

A handler that matched and then raised still counts as having taken the update: falling
through to the next one would handle it twice, which is the opposite of what this was
asked for. The default is off, because the failure this mode produces is the quiet kind:
a handler that never runs is harder to find than one that runs twice.

## What arrives, and when

The update layer is the part that makes this a library, not a script. Telegram numbers
updates with `pts`, `qts` and `seq`, plus a `pts` per channel, and expects the client to
notice when a number arrives that does not follow the last one. Sunnygram does: a gap is
recovered through `updates.getDifference` or `getChannelDifference`, slices are followed
to the end, and the counters are kept in the session so the next run resumes, not
restarts.

The promise is that every update is delivered once and in order, or not at all. Nothing
is dropped quietly and nothing is processed twice.

`start(catch_up=True)` fetches what was missed while the program was not running. Pass
`catch_up=False` to begin from now and ignore the backlog.

```python
await app.start(catch_up=False)
```

A session restored from a string has no counters to resume from and always starts from
now. See [Sessions](sessions.md).

## Replies come for free

A reply says which message it answers and stops there, so a program wanting the message
itself would have to ask for it. Nearly always it need not: the message being answered
went past this client a moment ago, and the last thousand of those are held.

```python
@app.on_message(filters.reply)
async def answering(client, message):
    earlier = message.reply_to_message        # usually already here, no call
    earlier = await message.get_reply()       # the same, and fetches if it is not
```

Three things can supply it without a call, in this order: the other messages that came in
the same answer, as a page of history does; the quote a quoted reply carries, which is an
outline, not the whole message and says so with `partial=True`; and the bounded cache of
what this client has lately seen or sent. Only when all three come up empty does
`get_reply` ask, and `reply_to_message` stays `None`.

`message_cache=0` on the client turns the holding off for a program that would rather have
the memory back.

## Back pressure

Updates arrive on a bounded queue. If handlers cannot keep up, the queue drops the oldest
and counts what it dropped instead of blocking the connection's reader, because a reader
that stops reading is a connection that dies. A program doing slow work per message should
hand it to a task or a queue of its own instead of awaiting it in the handler.

## The counters, if you need them

```python
app.updates.state       # pts, qts, date, seq, and the per-channel table
app.updates.events      # the queue the dispatcher reads from
await app.updates.feed(answer)   # the counters in a call's own answer
```

`feed` is public for a reason: the answer to a call carries the same counters an update
does, and letting them go is how a client ends up fetching a difference it did not need.
The client does this for you on the calls it wraps. A raw `invoke` whose answer carries
updates is yours to feed.

Signature by signature: the dispatcher is in the
[Client reference](api/client.md#dispatcher) and the update manager in the
[Types reference](api/types.md#updates).
