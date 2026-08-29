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

async for user in app.get_participants(chat_id, kind="admins"):
    ...
```

`kind` asks for one sort of member instead of all of them:

| | |
| --- | --- |
| `recent` | everyone, most recently active first. The default. |
| `admins` | the administrators, and the creator among them |
| `bots` | the bots in the chat |
| `banned` | the people thrown out, who are no longer in the chat |
| `restricted` | the people still in the chat but silenced |
| `contacts` | members who are also your contacts |

The last two are the one place worth reading twice. Telegram's own names for them are the
other way round: its `kicked` filter is the people thrown out and its `banned` filter is
the people still present but silenced. Sunnygram uses the readable word for each, the same
convention the [rights](admin.md) use. `query=` narrows any of them that accepts a search.

It is a fixed set of words rather than any string, so `kind="adminz"` is a type error at
the call instead of a loop that quietly finds nobody.

`get_participants` answers who is in a chat. `get_members` answers what each of them is in
it, with the status, the rights an administrator was given, the custom title and who
promoted them. Finding whoever made a chat is the short version of why it exists:

```python
async for member in app.get_members(chat_id, kind="admins"):
    if member.status is MemberStatus.CREATOR:
        print(member.user_id, member.title)
```

The two are separate calls rather than one handing back a pair, because a `User` is frozen
and a standing belongs to a chat rather than to the person.

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

## Running a chat

Promoting and demoting, restricting, banning and kicking, titles, photos, descriptions,
default permissions, slow mode, creating groups and channels, invite links, join requests
and the admin log all have friendly methods. See [Running a chat](admin.md), which also
explains the one trap in Telegram's rights: an administrator's powers are a list of what
they can do and a member's are a list of what they cannot, and Sunnygram uses the readable
convention for both.
