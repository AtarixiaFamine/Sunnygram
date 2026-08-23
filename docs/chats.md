# Chats and people

## The conversation list

```python
async for dialog in app.get_dialogs(limit=50):
    print(dialog.chat.title, dialog.unread)
```

A `Dialog` is not a `Chat`. The chat is the same for everybody in it; the dialog is this
account's relationship with it: the unread count, whether it is muted, whether it is
pinned, and which message was the last one.

| | |
| --- | --- |
| `chat` | the `Chat` itself |
| `top_message` | the last message, already wrapped, or `None` |
| `unread` | how many are unread |
| `unread_mentions` | how many of those mention you |
| `pinned` | pinned to the top of the list |
| `muted` | muted right now |

The last message comes back with the dialog instead of costing a call of its own, which is
why `get_dialogs` is one round trip per page, not one per row.

```python
async for dialog in app.get_dialogs():
    if dialog.unread and not dialog.muted:
        await dialog.read()
```

## Members

```python
async for user in app.get_participants(chat_id, limit=200):
    print(user.id, user.full_name)

async for user in app.get_participants(chat_id, query="anna"):
    ...
```

A basic group is not paged: Telegram answers the whole membership at once, because a basic
group is small by definition. A supergroup or channel is paged, and Telegram stops
answering somewhere past a few thousand however many you asked for. That is its rule, not
this library's, and there is no way around it from a user account.

## Joining and leaving

```python
await app.join_chat("@somechannel")
await app.join_chat("https://t.me/+AbCdEf123456")   # an invite link
await app.leave_chat("@somechannel")
```

Both spellings of an invite link work, the `joinchat/` one and the `+` one. A plain
username is not an invite and goes through the ordinary join.

## Asking about one

```python
chat = await app.get_chat("@somechannel")
user = await app.get_user("@durov")
```

These ask Telegram for the full record, which carries things a message never does: the
description, the member counts, the bio. Everything a message *does* carry is already on
`message.chat` and `message.sender` and costs nothing.

## Contacts and blocking

```python
for person in await app.get_contacts():
    print(person.full_name, person.phone)

await app.block_user("@spammer")
await app.unblock_user("@spammer")
```

## Your own profile

```python
me = await app.update_profile(first_name="Alex", about="building things")
```

Only what you name changes. Leaving a field out leaves it alone; clearing one is passing
an empty string.

## What is not here

Administration is not wrapped: promoting, banning, changing permissions, editing a title
or a photo, creating a chat. All of it is reachable through [the raw API](raw-api.md),
and none of it has a friendly method yet.

```python
from sunnygram.raw import functions, types

await app.invoke(
    functions.channels.EditBanned(
        channel=types.InputChannel(channel_id=..., access_hash=...),
        participant=await app.resolve("@somebody"),
        banned_rights=types.ChatBannedRights(until_date=0, send_messages=True),
    )
)
```
