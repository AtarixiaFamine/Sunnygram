# Messages

## Sending

```python
await app.send_message("me", "**hello**")
await app.send_message("@durov", "hi", silent=True)
await app.send_message(chat_id, "see above", reply_to=message.id)
```

The first argument is any [peer](peers.md): a username, a phone number, an id, `"me"`, or
a peer out of an earlier answer. The answer is the `Message` the server made of it, not a
raw TL object.

Text is markdown by default. `no_webpage=True` stops the link preview, `silent=True` sends
without a notification, and `reply_markup=` puts [buttons](buttons.md) under it, which
only a bot may do.

## From a message

A message knows the client it arrived on, so it can answer:

```python
@app.on_message(filters.text)
async def handler(client, message):
    await message.reply("as a reply")          # replies to this message
    await message.respond("in the same chat")  # no reply
    await message.edit("changed")              # if it is ours
    await message.edit_markup(keyboard([...]))  # the buttons only
    await message.delete()
    await message.forward_to("@somewhere")
    data = await message.download()            # if it has media
```

## What is on one

| | |
| --- | --- |
| `id` | the message id, per chat |
| `text` | the text, without formatting |
| `markdown` / `html` | the text with the formatting written back in |
| `entities` | the formatting itself, as Telegram spells it |
| `chat` | a `Chat`: `id`, `title`, `username`, `is_private`, `is_group`, `is_channel` |
| `sender` | a `User`: `id`, `username`, `full_name`, `mention`, `is_bot`, `is_premium` |
| `date` | when it was sent, as a `datetime` |
| `media` | the attachment, if any; `has_media` is the short question |
| `reply_to_id` | the id of the message this replies to |
| `reply_to_message` | that message itself, when it was known without asking |
| `partial` | whether this is an outline of a message rather than the message |
| `buttons` | the rows of inline buttons under it, if any |
| `file_ref` | its file as one string that can be written down |
| `outgoing` | whether we sent it |
| `service` | whether Telegram wrote it rather than a person |
| `raw` | the TL object it was built from, always |

`command`, `arguments` and `match` are filled in by the filters that work them out. See
[Filters](filters.md).

`reply_to_message` is usually already there, because the message being answered went past
this client a moment ago. `await message.get_reply()` is the same thing and fetches when
it is not. See [Handling updates](updates.md#replies-come-for-free).

## Formatting

```python
await app.send_message("me", "**bold** __italic__ `code` [link](https://example.com)")
await app.send_message("me", "<b>bold</b> <i>italic</i>", parse_mode="html")
await app.send_message("me", "literally **this**", parse_mode=None)
```

`parse_mode` on the client sets the default for every call:

```python
app = Client("my.session", api_id=..., api_hash=..., parse_mode="html")
```

Offsets are counted in UTF-16 code units, which is how Telegram counts them and why
formatting stays where you put it once someone sends an emoji. Getting that wrong is the
classic way for bold text to drift a character to the left halfway down a message.

To send formatting you already have, pass entities and skip parsing altogether:

```python
await app.send_message(peer, message.text, entities=message.entities)
```

## Editing, deleting, forwarding

```python
await app.edit_message(peer, message_id, "new text")
await app.delete_messages(peer, [id1, id2])              # for everyone
await app.delete_messages(peer, [id1], everywhere=False) # only for us
await app.forward_messages(target, source, [id1, id2])
```

`delete_messages` answers with how many the server owned up to. Deleting for everyone is
allowed for a while after sending, and always in a chat you administer.

## Reading history

```python
async for message in app.get_history("@durov", limit=100):
    print(message.date, message.text)
```

Telegram answers history a page at a time and expects the client to keep asking with the
id it got to. `get_history` does that bookkeeping: you say how many you want and read them.
`batch` controls how many come per call, `offset_id` starts partway down.

## Fetching and searching

```python
found = await app.get_messages("@durov", [1234, 1235])

async for message in app.search_messages("@durov", "hello", limit=50):
    print(message.id, message.text)
```

`get_messages` leaves out anything that is not there, not returning a hole, so the answer
can be shorter than what you asked for. `search_messages` pages itself the same way
`get_history` does.

An empty query with a filter asks for everything of one kind:

```python
from sunnygram.raw import types

async for photo in app.search_messages(
    "@durov", filter=types.InputMessagesFilterPhotos(), limit=20
):
    await photo.download(into=f"{photo.id}.jpg")
```

## Pinning, reading, typing

```python
await app.pin_message(peer, message.id)              # quietly
await app.pin_message(peer, message.id, silent=False)  # and notify the chat
await app.unpin_message(peer, message.id)
await app.unpin_all_messages(peer)

await app.read_history(peer)                # everything
await app.read_history(peer, max_id=1234)   # up to one message

await app.send_action(peer)                 # "typing..."
```

Pinning is quiet by default, which is the opposite of Telegram's own default and the
kinder one: the noisy version notifies everybody in the chat. In a private chat it pins
only on your side unless you pass `both_sides=True`.

A typing action is forgotten after about six seconds, so anything slower has to say it
again. Other actions live in `sunnygram.raw.types`:

```python
from sunnygram.raw import types

await app.send_action(peer, types.SendMessageUploadPhotoAction(progress=0))
```

## Sending twice

Every send carries a random id, and Telegram deduplicates on it. That is what makes the
invoker's retry-after-a-dropped-connection safe: a message that went out, whose answer was
lost, is not sent again when the call is.

Field by field: [Types reference](api/types.md).

## Sending later

`schedule_date` queues a message instead of sending it now. A `datetime` or a unix
timestamp, on `send_message` and on everything that sends a file.

```python
from datetime import datetime, timedelta

await app.send_message(chat, "Happy new year", schedule_date=datetime(2031, 1, 1))
await app.send_photo(chat, "cake.jpg", schedule_date=datetime.now() + timedelta(hours=2))
```

A naive `datetime` is read as local time, which is what someone writing a wall-clock time
means by it. Pass one with a `tzinfo` to be explicit.

`sunnygram.WHEN_ONLINE` is the one special value: send it the moment the recipient next
appears, instead of at a time.

```python
from sunnygram import WHEN_ONLINE

await app.send_message(user, "Morning", schedule_date=WHEN_ONLINE)
```

What comes back is the queued message. It is not in the chat yet and it has its own
numbering, so its id is only good for the other scheduled calls:

```python
queued = await app.get_scheduled(chat)
await app.send_scheduled(chat, [queued[0].id])     # send it now instead
await app.delete_scheduled(chat, [queued[1].id])   # or never
```

A message being queued arrives as its own kind of event, not as a message, because no one
has received it:

```python
@app.on_scheduled()
async def queued(client, message):
    print("queued for later:", message.text)
```

The moment it actually goes out it arrives again as an ordinary message, because by
then it is one.

## Replacing the file on a message

```python
await app.edit_media(chat, message_id, "better.jpg")
await message.edit_media("better.jpg", caption="Fixed")
```

Telegram will not put a file on a message that has none and will not take one off, so this
swaps a photo for another photo instead of turning text into an image. Passing no caption
leaves the existing one alone.
