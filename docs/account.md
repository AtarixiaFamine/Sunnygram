# The account itself

None of this matters to a program that only answers messages, and all of it matters to one
that runs unattended on someone's account. A userbot that cannot list its own sessions
cannot notice that it has been signed in to from somewhere else.

## Sessions

```python
for session in await app.get_sessions():
    print(session.device_model, session.ip, session.country, session.hash)

await app.terminate_session(hash)
await app.terminate_other_sessions()
```

The current session has a hash of zero and cannot be ended this way; `log_out` is what ends
it. `terminate_other_sessions` will not reach anything signed in within the last day, which
is Telegram's rule, not this one.

## The second factor

```python
await app.has_password()
await app.set_password("a new one", hint="the usual", email="me@example.com")
await app.set_password("a newer one", current="a new one")
await app.remove_password("a newer one")
```

Neither password leaves the machine. The current one goes out as an SRP proof and the new
one as `g` raised to a hash of it, which lets the server check a password it has never
seen. Both are deliberately slow to compute, so both happen off the event loop.

!!! warning "Set a recovery email"
    It is Telegram's only way back in. An account whose second factor is forgotten and has
    no email attached waits a week and then loses everything on it.

## Privacy

```python
await app.set_privacy("last_seen", "contacts")
await app.set_privacy("last_seen", "nobody", except_users=[alice])
await app.set_privacy("forwards", "everybody")

await app.get_privacy("phone_number")
```

The settings, by name: `last_seen`, `invites`, `calls`, `call_p2p`, `forwards`,
`profile_photo`, `phone_number`, `found_by_phone`, `voice_messages`, `about`, `birthday`.

What a rule can say: `everybody`, `contacts`, `close_friends`, `premium`, `bots`,
`nobody`, `not_contacts`, `not_bots`.

Exceptions are a separate argument, not something to assemble, because Telegram reads the
rules in order and a list built the other way round quietly means the opposite of what it
looks like. `except_users` is placed first and pointed the right way for whichever rule
follows it.

## Username

```python
if await app.check_username("something"):
    await app.set_username("something")

await app.set_username("")   # give the current one up
```

The `@` is optional in both.

## Folders

What Telegram calls dialog filters. A folder is not a place a chat is kept, it is a
rule for which chats to show, so a chat can be in several and being in one moves
nothing.

```python
for folder in await app.get_folders():
    print(folder.id, folder.title, len(folder.included))
```

There is no create call and no delete call: `updateDialogFilter` does all three jobs,
telling them apart by the id and by whether a filter is given. So creating a folder is
saving under an id nothing is using, and deleting one is saving nothing under a used
id.

```python
await app.save_folder(
    2, "Work",
    include=["@a_colleague", "@the_team_chat"],
    groups=True,
    exclude_muted=True,
)
await app.reorder_folders([2, 1])
await app.delete_folder(2)          # the chats are not touched, only the rule
```

A folder someone shared as a link and this account added comes back with `shared` set and
`editable` false. Its contents belong to whoever published it.

## Exporting everything

A takeout session reads without the usual limits, and the account holder has to
approve it in an official client first.

```python
from sunnygram.raw import functions

async with await app.takeout(message_users=True, files=True) as export:
    history = await export.invoke(
        functions.messages.GetHistory(peer=..., limit=100, offset_id=0,
                                      offset_date=0, add_offset=0,
                                      max_id=0, min_id=0, hash=0)
    )
```

Every call made through `export` goes out wrapped so the server knows it is part of
the export. Leaving the block closes the session, and says the export failed if it is
leaving because something raised.

**`TakeoutInitDelay` is not a rate limit**, whatever it looks like. It subclasses
`Flood` because Telegram sends it as a 420, but what it means is that a person has
been asked to approve something in another client and has not yet. Its `seconds` are
hours, and it is deliberately never slept through: it reaches you so you can say so.

```python
from sunnygram.errors import TakeoutInitDelay

try:
    export = await app.takeout(contacts=True)
except TakeoutInitDelay as waiting:
    print(f"Approve the export in Telegram; {waiting.seconds}s left on the timer")
```
