# Running a chat

## Rights, and the trap in them

Telegram spells permissions two ways and only one of them reads naturally.

An administrator's powers are a list of things they **can** do. A member's permissions
arrive as `ChatBannedRights`, which is a list of things they **cannot** do, so allowing
someone to send photos means setting `send_photos` to false. Reading that wrong is easy and
it silences a chat.

Sunnygram uses one convention, the readable one. `True` means allowed, everywhere.

```python
from sunnygram import AdminRights, Permissions

Permissions(send_media=False)          # may write, may not attach anything
Permissions.read_only()                # may read and nothing else
Permissions.everything()               # no restriction, which is also how one is lifted
Permissions.none()                     # not even the chat, which is what a ban is

AdminRights.moderator()                # remove people and posts, pin, invite
AdminRights.everything()               # every power short of anonymity
AdminRights(delete_messages=True)      # exactly one
```

Neither mutates. `with_` makes a changed copy.

```python
rights = AdminRights.moderator().with_(add_admins=True)
```

## Administrators

```python
await app.promote(chat, user, AdminRights.moderator(), title="mod")
await app.demote(chat, user)

await app.get_admin_rights(chat, user)   # what they hold now
```

Promoting with no rights grants none of them, which is the safe direction for a default to
point and is also exactly what `demote` does. An account can only hand out powers it holds
itself.

## Members

```python
await app.restrict(chat, user, Permissions.read_only())
await app.restrict(chat, user, Permissions(send_media=False), until=1800000000)

await app.ban(chat, user)      # removed and kept out
await app.unban(chat, user)    # every restriction lifted
await app.kick(chat, user)     # removed, free to come back

await app.get_permissions(chat, user)
```

`until` is a unix time and zero is forever. Telegram treats anything under thirty seconds
or over a year away as forever too.

Kicking is two calls in a supergroup, because Telegram has no third thing: a ban that is
immediately lifted removes someone and leaves them able to rejoin. A basic group has an
actual call for it and takes that instead.

## The chat itself

```python
await app.set_chat_title(chat, "New name")
await app.set_chat_description(chat, "What this is for")
await app.set_chat_photo(chat, photo)
await app.set_chat_photo(chat, None)          # remove it
await app.set_chat_permissions(chat, Permissions(send_polls=False))
await app.set_slow_mode(chat, 30)
```

A basic group and a supergroup are edited through two entirely different APIs, by a bare
numeric id and by an id with an access hash. Every call above works out which it is
looking at, and says plainly when the answer is that a basic group cannot do this.

## Making and unmaking

```python
group = await app.create_group("Ours", [alice, bob])
channel = await app.create_channel("News", about="Daily")
supergroup = await app.create_channel("Chat", megagroup=True)
forum = await app.create_channel("Forum", forum=True)

await app.delete_chat(chat)
```

A supergroup is created by a call named for channels, because to Telegram it is one with a
flag set. A basic group cannot be created empty, which is why the members are not optional
and why one turns into a supergroup by itself the first time someone needs something only a
supergroup has.

## Invite links

```python
link = await app.export_invite_link(chat)
link = await app.export_invite_link(chat, title="press", expires=1800000000, usage_limit=5)
link = await app.export_invite_link(chat, request_needed=True)

await app.revoke_invite_link(chat, link)
await app.get_invite_links(chat)
```

A link that admits people and a link that has to be approved are different things, and
Telegram refuses a usage limit on the second kind. Revoking a chat's primary link does not
leave it without one: a replacement is made in the same breath.

```python
await app.approve_join_request(chat, user)
await app.approve_join_request(chat, user, approved=False)
```

## The admin log

```python
async for event in app.get_admin_log(chat, limit=50):
    print(event.date, event.user_id, type(event.action).__name__)
```

Raw, deliberately. There are several dozen kinds of entry and they have nothing in common
but an id, a date and who did it, so wrapping them would hide more than it explained.
Telegram keeps these for a couple of days.
