# Conversations

A handler is a standing offer: anything of this kind, whenever it turns up, do this with
it. Most of a Telegram program is that shape. Some of it is not. Code that asks a question
already knows, at the point where it asks, what to do with the reply, and splitting that
across two handlers and a dictionary of who-is-halfway-through-what is the part people
dislike about writing bots.

```python
answer = await app.ask("@someone", "What should I call you?")
print(answer.text)
```

That is the whole of the common case. `ask` sends the question, waits for the reply, and
returns it as an ordinary [message](messages.md).

## A back and forth

```python
async with await app.conversation(chat) as talk:
    await talk.send("What should I call you?")
    name = await talk.wait()

    await talk.send(f"Hello {name.text}. How old are you?")
    age = await talk.wait(filters=filters.text)

    await talk.send("Thanks")
```

`await` before the `async with` because the chat has to be resolved to the id updates
arrive with, and resolving is a call.

Nothing is held between waits. A conversation is somewhere to keep the chat and the
deadline so the code reads like a conversation; the only resource it takes is one row in
the dispatcher's table, and only while it is actually waiting.

## The answer does not also reach your handlers

This is the decision that matters, because it is the one that would surprise you later. A
message that answers a question is **not** offered to ordinary handlers. A program asking
someone's name does not want its command router reading the name and deciding it is not a
command it knows.

That is the default because it is what asking a question almost always means, and it is
off with one word:

```python
async with await app.conversation(chat, exclusive=False) as talk:
    ...
```

Your own outgoing messages never answer a question, which matters more than it sounds:
`ask` starts listening before it sends, so without that rule every `ask` would return the
question it had just asked.

## Waiting for something you did not ask for

```python
press = await app.wait_for(chat, kind="callback", timeout=30)
photo = await app.wait_for(chat, filters=filters.photo)
```

For the half of a conversation that starts with them: a confirmation, a file someone was
told to send, a button being pressed. A filter narrows what counts as an answer, so the
wrong thing arriving goes on waiting instead of being taken as the reply.

## Nothing waits for ever

Every wait has a deadline, 60 seconds unless you say otherwise, and a question no one
answers raises `NoAnswer`:

```python
from sunnygram.errors import NoAnswer

try:
    answer = await app.ask(chat, "Still there?", timeout=30)
except NoAnswer:
    await app.send_message(chat, "I will ask again later")
```

It raises instead of returning `None` because a question that went unanswered is nearly
always a different path through the program, and a `None` no one checked for fails further
away with less to say for itself. The timeout is also logged at warning level: a bot that
has stopped being answered is worth a line even when the code handles it.

The table of outstanding questions is bounded, and a wait gives its place back however it
ends, including when the surrounding task is cancelled. A client that stops cancels
anything still waiting, since the update stream that would have answered it has stopped
too.
