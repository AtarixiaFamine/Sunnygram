# Albums, polls, and the rest

Sending a file is in [Files](files.md). This is everything else a message can carry, most
of which needs no upload at all.

## Albums

```python
sent = await app.send_album(chat, ["a.jpg", "b.jpg", "c.jpg"])
sent = await app.send_album(chat, ["a.jpg", "b.jpg"], captions=["under the block", ""])
```

An album is not one message with several files in it. It is several messages that share a
group id, which the clients then draw as one block. That shows in how it has to be sent:
each file goes up on its own, is registered with the server on its own, and only then do
the finished descriptions go out together. `send_album` answers with the list of messages
it made.

Ten to a group. Photos and videos mix freely; documents group with documents; the two
cannot share one, and trying says so here instead of failing on the wire.

Most clients show only the first caption under the whole block, so that is usually the only
one worth setting.

### Receiving one

```python
@app.on_album()
async def handler(client, messages):
    print(len(messages), "files")
```

The parts arrive as separate updates with no marker on the last one, so the handler fires
after a short silence. Each part also reaches ordinary message handlers, because that is
what it is: a program written before albums existed keeps working.

A filter on an album handler is asked about the first part, which is the one carrying the
caption.

```python
message.album_id      # which album a message is part of, or None
```

## Polls

```python
await app.send_poll(chat, "Which?", ["A", "B", "C"])
await app.send_poll(chat, "Which?", ["A", "B"], multiple=True, anonymous=False)
await app.send_poll(chat, "Which?", ["A", "B"], correct=1, explanation="B, because")
```

Naming a correct answer is what makes it a quiz, instead of a flag: Telegram will not take
a quiz without one. Answers are referred to by position everywhere here, so `correct=1` is
the second answer and voting uses the same numbers.

```python
await app.vote(chat, message_id, 0)      # answer
await app.vote(chat, message_id)         # retract
await app.get_poll(chat, message_id)     # standing right now
await app.close_poll(chat, message_id)   # cannot be undone

await message.vote(0)
```

Closing is spelled as editing the message with a closed poll in its place, because there is
no call for closing one.

## Reactions

```python
await app.react(chat, message_id, "\N{THUMBS UP SIGN}")
await app.react(chat, message_id, 5312536423851630001)   # a custom emoji, by document id
await app.react(chat, message_id)                        # clear
await message.react("\N{FIRE}")

await app.get_reactions(chat, message_id)
```

One call does all three things. Sending sets the whole list of this account's reactions on
that message, so adding a second means sending both and taking them back means sending
none. There is no separate call for removing one.

Only chats small enough for Telegram to keep the list answer `get_reactions` with names; a
large channel gives counts and nothing else.

## Stickers, dice and places

```python
await app.send_sticker(chat, sticker)                 # a document off another message
await app.send_dice(chat)                             # Telegram picks the number
await app.send_dice(chat, "slots")
await app.send_location(chat, 51.5, -0.12)
await app.send_venue(chat, 51.5, -0.12, "Somewhere", "1 Road")
await app.send_contact(chat, "+441234", "Pavel")
```

A sticker is a document, so `send_sticker` points at one that already exists, not uploading
anything. The dice names are `dice`, `dart`, `basketball`, `football`, `bowling` and
`slots`, and the emoji itself works for anything added since.

## Copying

```python
await app.copy_message(chat, message)
await app.copy_message(chat, message, caption="something else")
await message.copy_to(chat)
```

Not a forward. A forward keeps the original author's name on it and the original chat
behind it, and there are chats where that is exactly what is not wanted. A copy is sent as
though it were written here for the first time.

What can be copied is text and media that already exists on the server. A poll cannot be: a
poll is votes, not content, and the server would make a second poll, not a copy of the
first.
