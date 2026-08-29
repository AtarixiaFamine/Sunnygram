# Shared folders and sticker sets

Two things that are made rather than read: a folder other people can join, and a
sticker set of your own.

## Shared folders

An ordinary folder is a private arrangement of your own dialogs, and is in
[folders](chats.md). This is the other half: a folder given a link, so that
opening the link puts somebody in every chat in it at once.

Both are the same object underneath, named by the folder's id.

```python
link = await app.export_folder_link(
    folder_id, title="Python", peers=["@somechannel", "@another"]
)
```

The chats in the link are **named** rather than taken from the folder, because
not every chat can be shared: only public ones, and ones you can invite to.
Asking for a chat the server will not share is refused outright, which is the
honest answer. A link that quietly carried fewer chats than you asked for would
be worse than one that failed.

### Joining somebody else's

```python
preview = await app.preview_folder_link(slug)     # look without joining
await app.join_folder_link(slug, peers=[...])     # take the chats you name
```

The chats are named on the way in for the same reason they are named on the way
out. A link with twenty chats behind it should not put an account in twenty chats
without being asked which.

### It keeps sharing

A shared folder goes on being shared: chats added to it later are an update the
people who joined can take or ignore.

```python
gained = await app.get_folder_updates(folder_id)
await app.join_folder_updates(folder_id, peers=[...])   # take them
await app.hide_folder_updates(folder_id)                # or decline
```

### Leaving

```python
suggested = await app.get_leave_suggestions(folder_id)
await app.leave_folder(folder_id)                       # folder only
await app.leave_folder(folder_id, peers=suggested.peers)  # and these chats
```

Naming no chats leaves the folder and stays in everything, which is the safe
default: leaving chats is the half that cannot be undone quietly. Telegram will
suggest which chats you joined *through* the folder and are in for no other
reason, and a suggestion is all it is.

Managing the links themselves:

```python
await app.get_folder_links(folder_id)
await app.edit_folder_link(folder_id, slug, title="New name")
await app.delete_folder_link(folder_id, slug)
```

Editing leaves out what you did not pass, so a title change keeps the chats.
Deleting a link does not remove anybody who already joined through it.

## Sticker sets

Sending a sticker is in [files](files.md) and needs none of this. This is making
one.

```python
first = await app.upload_sticker("cat.webp", "🐱", keywords=["cat", "meow"])

await app.create_sticker_set(
    "me",
    title="My cats",
    short_name="my_cats_by_me",
    stickers=[first],
)
```

`upload_sticker` is two calls rather than one, and the second is the one worth
knowing about. A set is built out of **documents**, and an upload is not a
document yet: it has to be registered with the server first, which is what turns
a handle into something carrying the id and access hash a set can hold. That
registering happens in Saved Messages, costs nothing and sends nobody anything.

The default assumes a still `image/webp` sticker. Pass `mime_type="video/webm"`
for an animated one, or `"application/x-tgsticker"` for a Lottie.

Three things shape every call here.

**A set is named by its short name, not an id**, because the short name is what a
t.me link carries. Leading `@` and stray spaces are trimmed for you.

**A sticker is named by the document it is, not by a position.** So removing one
means having the document in hand: read it off the set, or off a message carrying
it. That is also why `remove_sticker` takes no set, since the document already
says which one it is in.

**The emoji is not decoration.** It is how the sticker is found when somebody
types that emoji, so a set built with the same emoji on every sticker is a set
nobody can search.

### Kinds

`kind=` is one word: `"regular"`, `"mask"` or `"emoji"`. Telegram spells this as
two independent boolean flags, which reads as though a set could be both. It
cannot, so it is one choice here.

A set cannot be created empty, which is why `stickers` is not optional.

### Picking a short name

```python
if await app.short_name_free("my_cats_by_me"):
    ...
suggested = await app.suggest_short_name("My cats")
```

### Editing a set

```python
await app.add_sticker("my_cats_by_me", await app.upload_sticker("cat2.webp", "😻"))
await app.move_sticker(document, 0)              # counting from zero
await app.edit_sticker(document, emoji="😾")     # what it is found by
await app.replace_sticker(document, replacement)  # keeps its place
await app.remove_sticker(document)
await app.rename_sticker_set("my_cats_by_me", "Better cats")
await app.set_sticker_set_thumb("my_cats_by_me", document_id=document.id)
await app.delete_sticker_set("my_cats_by_me")
```

Renaming changes the title and keeps the short name, so the link still works.
Deleting is not undoable and does not free the short name.
