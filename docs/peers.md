# Peers

MTProto does not let you name someone by id alone. Almost every reference needs an
`access_hash` too: a number Telegram gave *you* for *that* peer, which proves you came by
them legitimately. Getting that right is most of what makes a raw MTProto client tedious,
and it is the layer this one hides.

## Naming a peer

Anywhere a peer is wanted, any of these work:

```python
await app.send_message("me", "...")                  # ourselves
await app.send_message("@durov", "...")              # a username
await app.send_message("durov", "...")               # the @ is optional
await app.send_message(777000, "...")                # a user id
await app.send_message(-1001234567890, "...")        # a marked channel id
await app.send_message("+15551234567", "...")        # a phone number, if a contact
await app.send_message(message.chat.id, "...")       # wherever a message came from
```

Only a name this session has never seen costs a call. Everything else is answered from the
cache.

## Marked ids

The id `-1001234567890` is the convention every Telegram library shares: a plain positive
number is a user, a negative one is a small group, and a `-100` prefix is a channel or
supergroup. Sunnygram reads all three and gives them back the same way, so an id copied
out of another library's output works here.

```python
from sunnygram.peers import mark_id, unmark_id
```

## The cache

Access hashes are learned from every answer and every update that carries them, kept in a
bounded LRU, and written into the session, which is why the second run of a program can
message someone it met in the first without looking them up again.

Hashes belong to the account that was given them. An [adopted session](importing.md)
brings its peers across because it is the same account; a hash copied between two accounts
is not a shortcut, it is a call that fails.

One deliberate exception: a **min peer** is never learned. Telegram sends those inside a
chat where the hash is only good in that chat, and storing it would produce a peer that
fails everywhere else in a way that looks like a bug in your code instead of a bug in the
cache.

## Resolving explicitly

```python
peer = await app.resolve("@durov")     # an InputPeer, for a raw call
```

That is what to pass to [raw calls](raw-api.md) that want an `InputPeer`. The underlying
functions take an invoker and are there for a program not using `Client`:

```python
from sunnygram.peers import resolve, resolve_username, resolve_phone

peer = await resolve(app.invoker, "@durov")
record = await resolve_username(app.invoker, "durov")
```

## When a hash stops working

An `access_hash` is not permanent and not portable. It is a number Telegram gave this
account for that peer, so it is worthless to another account, and Telegram may stop
accepting one it handed out earlier. When that happens the call comes back
`PEER_ID_INVALID`, `CHANNEL_INVALID`, `USER_ID_INVALID` or `CHAT_ID_INVALID`, depending on
what was named.

The trap in every library that caches peers is what happens next. The bad hash is in the
session file, so it survives the restart that a person tries first, and every call naming
that peer fails the same way for as long as the file lasts. The usual advice ends up being
to delete the session and log in again.

Sunnygram drops it instead. A call refused for any of those four reasons has the peers it
named forgotten, in memory and in the session file, and says so through the logger:

```
WARNING sunnygram.network.invoker: functions.messages.SendMessage was refused with
PeerIdInvalid, so the access hash held for peer 7 has been dropped: naming them again
resolves them afresh instead of failing the same way
```

The call that hit it still fails, and still raises what the server said. What does not
happen is the second failure: naming that peer again resolves them from scratch. If they
can be reached by username the next mention just works, and if the only name your program
has for them is an id then the next mention raises `PeerNotFound`, which at least says
what the problem is.

Two ways to do it by hand:

```python
await app.forget_peer(-1001234567890)   # drop what is remembered
await app.refresh_peer("durov")         # ask the server again and keep the answer
```

`refresh_peer` is the repair, and the reason it takes a username is that a username is the
only thing that survives a hash going bad. `resolve` deliberately answers from the cache,
which makes it free and exactly what is unhelpful when the cached answer is the problem.

## What can go wrong

`PeerNotFound` means we cannot name that peer to the server: an unknown username, or an id
this account has never encountered. An id alone is not enough to reach a stranger, by
design. You have to have met them: in a chat, in a search, in a contact list, in an update.

Signature by signature: [Layers reference](api/layers.md#peers).
