# Statistics and boosts

Two things a channel owner asks about that a member cannot: how it is doing, and
where it stands on the boost ladder.

## Statistics

```python
numbers = await app.get_chat_stats(channel)
print(numbers.followers.current, numbers.followers.previous)
```

A channel and a supergroup are counted differently and answered by two different
calls. Which one a chat needs is worked out from the chat, so there is one method
rather than two, and asking the wrong question is not a mistake you can make.

| | |
| --- | --- |
| a channel | followers, views per post, shares per post, reactions per post |
| a supergroup | members, messages, viewers, posters |

Every counter arrives as a value paired with the value from the period before it,
so growth reads without keeping your own history.

Statistics start only past a size Telegram picks and does not publish. Below it
the server refuses. That is its rule and not this library's, and there is no way
to ask how close a chat is.

### Graphs are a second call

```python
loaded = await app.load_graph(numbers.growth_graph.token)
```

A graph in the answer is usually not the data. It is a token, because Telegram
builds graphs on demand rather than sending a dozen of them with every reply.
`load_graph` turns one into the other, and `x=` asks for the detail behind a
single point on a graph that offers one.

`dark=True` asks for graphs styled for a dark background. It changes nothing
about the numbers.

### One post, and where it went

```python
post = await app.get_message_stats(channel, message_id)
story = await app.get_story_stats(channel, story_id)

async for repost in app.get_public_forwards(channel, message_id, limit=50):
    print(repost)
```

A repost is a message in another public chat **or** a story, and Telegram answers
with both mixed together. `get_public_forwards` yields whichever each one is
rather than quietly dropping the kind you did not ask about, so check what you
have if it matters.

## Boosts

A Premium account holds a few boost slots and lends them out, one chat at a time.
Enough of them and a chat goes up a level, which is what unlocks custom emoji, a
wallpaper, more stories a day, and the rest of what Telegram gates by level
rather than by payment.

```python
status = await app.get_boosts_status(channel)
print(f"level {status.level}, {status.needed} boosts to go")
```

| | |
| --- | --- |
| `level` | where the chat is now |
| `boosts` | how many it has |
| `needed` | how many more the next level takes, or `None` at the top |
| `progress` | how far through the current level, `0.0` to `1.0` |
| `mine` | whether this account is one of the boosters |
| `my_slots` | which of your slots are lent to it |
| `url` | the link that lets somebody spend a slot on it |

### The arithmetic worth not doing yourself

`needed` is **not** `next_level_boosts - current_level_boosts`. Telegram measures
the next level from zero rather than from the level below, so subtracting the two
is off by every boost already spent. A chat at level 3 with 47 boosts, where the
next level is 50 and this one started at 25, needs **3** more and not 25.

That is the whole reason `BoostStatus` exists rather than handing back the raw
answer, and there is a test named after it.

### Lending and reading

```python
mine = await app.get_my_boosts()          # your slots, and what each is lent to
await app.boost(channel)                  # let the server pick a free slot
await app.boost(channel, slots=[3, 4])    # or move particular ones

async for booster in app.get_boosts(channel, limit=100):
    print(booster.user_id, booster.expires)

async for gifted in app.get_boosts(channel, gifts=True):
    ...
```

A boost is lent, not given: every one expires and comes back, which is what
`expires` is for. `gifts=True` narrows the list to the ones that came from a
giveaway or a gift rather than from somebody spending a slot of their own, and
those have no `user_id` while they are unclaimed.

Which of one person's slots are on a chat is a separate question, and an
administrator's:

```python
theirs = await app.get_user_boosts(channel, "@somebody")
```
