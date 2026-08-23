# Buttons

A keyboard is two things that look like one. An **inline keyboard** hangs under a message
and its buttons do something when pressed: they call your program back, open a link, start
an inline query. A **reply keyboard** replaces the other side's suggestions above the text
field, and its buttons only ever send their own label.

They are two different fields on two different constructors, so a keyboard cannot hold
both kinds. Sunnygram works out which one you meant from the buttons you used, and says so
if you mixed them.

## Sending one

```python
from sunnygram import Button, keyboard

await app.send_message(
    chat,
    "Delete this?",
    reply_markup=keyboard([Button.callback("Yes", "del:yes"),
                           Button.callback("No", "del:no")]),
)
```

A flat list is one row. A list of lists is the layout you wrote:

```python
keyboard([
    [Button.callback("1"), Button.callback("2")],
    [Button.callback("Cancel", "cancel")],
])
```

Or let it lay a flat list out:

```python
keyboard([Button.callback(str(n)) for n in range(1, 10)], columns=3)
```

`reply_markup=` works on everything that sends: `send_message`, `send_file` and each of
its relatives, `send_media`, `send_photo`, polls, dice, locations. Not on `send_album`,
because Telegram has nowhere to put one on a group of files.

**Only a bot may send a keyboard.** That is Telegram's rule, not this library's. A user
account can read and press them, which is what [Talking to bots](bots.md) is about.

## The buttons

```python
Button.callback("Yes", "del:yes")        # calls your program back
Button.callback("Yes")                   # the payload defaults to the label
Button.url("Docs", "https://example.com")
Button.switch_inline("Search", "cats")   # opens the chat picker with a query typed
Button.web_app("Open", "https://example.com")
Button.copy("Copy code", "ABC-123")
Button.profile("Who", user_id)
Button.login("Sign in", "https://example.com")
Button.game("Play")
Button.pay("Buy")
```

The payload is capped at **64 bytes** by Telegram, and something longer is refused here,
not on the wire. It travels back on every press, so treat it as a key into what your
program knows instead of as the thing itself: `"order:17"`, not the order.

Above the text field instead:

```python
Button.text("Yes")                       # sends its own label as a message
Button.request_phone("Share my number")
Button.request_location("Share where I am")
Button.request_poll("Make a poll")
```

A string counts as `Button.text`, so a reply keyboard can be written as the words on it:

```python
keyboard(["Yes", "No"], one_time=True, placeholder="pick one")
```

`resize=True` is the default here, which shrinks the keyboard to its buttons. Telegram's
own default is the other way and looks like a mistake in every client that draws it.

Two markups are not keyboards at all:

```python
from sunnygram import force_reply, remove_keyboard

await app.send_message(chat, "What is your name?", reply_markup=force_reply())
await app.send_message(chat, "Done", reply_markup=remove_keyboard())
```

`force_reply` opens the other side's keyboard with this message already being replied to,
which is how to ask a question in a group and be sure the answer comes back attached to
it. `remove_keyboard` takes away a reply keyboard a previous message put up; an inline
keyboard belongs to its message and is removed by editing that message's markup away.

## Being pressed

```python
from sunnygram import filters

@app.on_callback_query(filters.data("del:yes"))
async def confirm(client, press):
    await press.answer("Deleted")
    await press.edit("Gone.")
```

**Answer every press.** Telegram holds one open until something does, and every client
draws that as a spinner on the button. Answering with nothing is fine and is what a bot
does when the real reply is an edit:

```python
await press.answer()                          # stops the spinner, says nothing
await press.answer("Saved")                   # a notice along the top
await press.answer("Are you sure?", alert=True)   # a box they have to dismiss
await press.answer("Nothing changed", cache_time=60)
```

`cache_time` lets the client answer the same press itself for that many seconds without
asking again, which is worth setting when the answer cannot change.

What a press carries:

| | |
| --- | --- |
| `press.text` | the payload, as text |
| `press.data` | the payload, as bytes |
| `press.sender` | who pressed it |
| `press.chat` | where, or `None` for an inline message |
| `press.message_id` | which message it is under |
| `press.match` | what `filters.regex` found, if you used one |
| `press.is_inline` | whether the message came from an inline query |

And what it can do:

```python
await press.answer(...)          # required
await press.edit("new text")     # rewrite the message it is under
await press.edit_markup(keyboard([...]))   # change the buttons only
await press.edit_markup()                  # take them away
await press.reply("something new")         # a new message, replying to that one
message = await press.get_message()        # fetch it, which costs a call
```

## Filtering presses

`filters.data` is the one written for this:

```python
@app.on_callback_query(filters.data("yes", "no"))       # exactly one of these
@app.on_callback_query(filters.data(prefix="page:"))    # anything starting with it
```

A prefix is how a bot packs an argument into a payload and reads it back:

```python
@app.on_callback_query(filters.data(prefix="page:"))
async def turn(client, press):
    page = int(press.text.removeprefix("page:"))
    await press.answer()
    await press.edit(render(page), reply_markup=pager(page))
```

`filters.regex` works too, because a press has text: its payload. So do the filters about
who and where, since a press says who pressed it and in which chat:

```python
@app.on_callback_query(filters.regex(r"^page:(\d+)$") & filters.group)
async def turn(client, press):
    page = int(press.match.group(1))
```

The filters asking what kind of media a message carries do not apply to a press, and
putting one on `on_callback_query` is reported as a handler error, not quietly matching
nothing.

## Messages from an inline query

A message a bot produced through an inline query belongs to no chat. It carries an opaque
id issued by one particular datacenter, and editing it means talking to that datacenter
instead of to home. Both kinds of press arrive at the same handler, and `press.edit` and
`press.edit_markup` do the right thing for either:

```python
@app.on_callback_query()
async def pressed(client, press):
    await press.answer()
    await press.edit("chosen")     # works whether or not there is a chat
```

`press.get_message()` is the one thing that cannot: there is no chat to fetch it from, and
it says so, not guessing.

## Reading buttons off a message

```python
for row in message.buttons:
    for button in row:
        print(button.text)
```

Only the inline kind, since only those belong to the message. Pressing one as a user
account is [`app.click`](bots.md#pressing-buttons).
