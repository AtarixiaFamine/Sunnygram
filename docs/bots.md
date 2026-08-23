# Talking to bots

This is the part a user account can do that a bot cannot, and it is most of the reason
anybody writes a userbot. A bot's own API has no calls for any of it, because a bot is on
the other side.

Writing the bot itself is the other side, and it is [Buttons](buttons.md): putting a
keyboard under a message, and answering it when someone presses one.

## Pressing buttons

```python
@app.on_message(filters.text)
async def handle(client, message):
    answer = await client.click(message, "Yes")
    print(answer.message)
```

A button is not addressed by anything you naturally have. The message carries a keyboard,
the keyboard is rows, and the button carries opaque data the bot gave it. So the useful
call is not "press button 3", it is "press the one that says Yes", and all three ways of
saying which work:

```python
await app.click(message, "Yes")     # by label, which is how anybody refers to one
await app.click(message, 2)         # by number, in reading order
await app.click(message, (1, 0))    # by row and position
```

The answer is what a person would see: usually a short notice, sometimes an instruction to
open a url. A bot that replies by editing the message instead says nothing here, and the
edit arrives as an update.

```python
for row in app.buttons_of(message):
    for button in row:
        print(button.text)
```

A label that is not there raises, and the message says which labels are.

A link button raises too, instead of being pressed: it opens a url and does nothing on
Telegram's side. A button asking for the account password raises unless one is passed,
because sending a password means the SRP exchange and doing that quietly on a button press
is not a library's decision to make.

## Inline queries

```python
results = await app.inline_query(bot, "cats")
await app.send_inline_result(chat, results.query_id, results.results[0].id)
```

The same thing as typing `@bot cats` and picking a result. The chat matters even before
anything is sent: bots are told where a query came from and may answer differently in a
group than in a private chat.

```python
results = await app.inline_query(bot, "cats", peer=chat)
```

The two ids belong to one answer and go stale, so sending a result is the call that
follows the query, not one to hold onto.

## Starting a bot

```python
await app.start_bot(bot)
await app.start_bot(bot, parameter="ref123")
await app.start_bot(bot, peer=group)
```

The first is what the start button under a fresh bot chat does. The second is what the
payload in a `t.me/bot?start=ref123` link becomes. The third adds the bot to a group with
a parameter attached.
