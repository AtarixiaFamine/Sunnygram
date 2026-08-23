# Forum topics

A forum is a supergroup with topics turned on, and a topic is a thread inside it. There is
one idea underneath all of it, and knowing it makes the rest obvious:

**A topic is the message that opened it.** Its id is that message's id, and being in a
topic is spelled as replying to it. That is why sending into a topic and answering someone
go through the same field, and why there is no separate id space to keep track of.

The one exception is the topic every forum starts with, `General`, which has id 1 and was
never opened by anybody. It cannot be deleted, and it is the only one that can be hidden.

## Reading them

```python
async for topic in app.get_topics(chat_id):
    print(topic.id, topic.title, topic.unread)

bugs = await app.get_topic(chat_id, 42)
```

Pinned topics come first, then the rest by how recently they were active. Search with
`query=`, which matches on the title:

```python
async for topic in app.get_topics(chat_id, query="release"):
    ...
```

A `Topic` carries:

| | |
| --- | --- |
| `id` | the topic, which is also the id of the message that opened it |
| `title` | what it is called |
| `chat_id` | the forum it is in |
| `closed` | only administrators may post |
| `pinned` | held at the top of the list |
| `hidden` | off the list; only the general topic can be |
| `unread` | how many messages are unread |
| `top_message` | the last message in it, already wrapped, or `None` |

## Sending into one

```python
await app.send_message(chat_id, "found it", topic=42)
await app.send_file(chat_id, "trace.log", topic=42)
await app.send_album(chat_id, ["a.jpg", "b.jpg"], topic=42)
```

Or from the topic itself, which knows where it is:

```python
topic = await app.get_topic(chat_id, 42)
await topic.send("found it")
```

`topic=` and `reply_to=` go together and mean different things. Given both, the reply names
the message being answered and the topic names the thread it is in:

```python
await app.send_message(chat_id, "agreed", reply_to=1234, topic=42)
```

Leaving `topic=` out sends to the general topic, which is what every forum treats as the
default place.

## Making and changing them

```python
topic = await app.create_topic(chat_id, "Release 2.0")
await app.create_topic(chat_id, "Bugs", icon_color=0xFF93B2)
await app.create_topic(chat_id, "Design", icon_emoji_id=5379748062124056162)
```

`create_topic` answers with the `Topic`, having looked it up: the call itself only says
which message was made, and that message's id is the topic.

```python
await app.edit_topic(chat_id, 42, title="Release 2.1")
await app.close_topic(chat_id, 42)      # only admins may post
await app.reopen_topic(chat_id, 42)
await app.pin_topic(chat_id, 42)
await app.pin_topic(chat_id, 42, pinned=False)
```

Deleting one takes everything in it, a slice at a time, and answers with how much went:

```python
gone = await app.delete_topic(chat_id, 42)
```

## Turning a group into a forum

```python
await app.set_forum(chat_id)            # on
await app.set_forum(chat_id, False)     # off
```

Telegram refuses this for a group below the member count it requires, and says so. Turning
it off deletes nothing: everything that was in a topic moves back into the single
conversation the group used to be.

Every option: [Layers reference](api/layers.md#topics).
