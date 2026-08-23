# Inline mode

Inline mode is a bot that works in chats it is not in. Someone types the bot's name in any
chat, then a query, and every keystroke reaches the bot; the bot answers with a list of
things they could send; whatever they pick is sent by them, not by the bot.

Turn it on in BotFather first (`/setinline`), or the queries never arrive.

```python
from sunnygram import Client, InlineResult, filters

app = Client("bot.session", api_id=API_ID, api_hash=API_HASH)


@app.on_inline_query()
async def answer(client, query):
    await query.answer([
        InlineResult.article(
            title=f"Say {query.text}",
            text=query.text,
            description="sends exactly what you typed",
        )
    ])
```

## Answering is not optional

Telegram holds the query open until the bot answers, and every client draws that as a
panel that never finishes loading. So a handler that decides it has nothing to offer still
answers, with an empty list:

```python
@app.on_inline_query()
async def answer(client, query):
    found = await search(query.text)
    await query.answer([InlineResult.article(one.title, one.url) for one in found])
```

This is the same rule buttons have, for the same reason, and it is the one thing worth
being careful about here.

## Results

`InlineResult` has a factory per kind, and each of them works out which of Telegram's four
result constructors it needs:

```python
InlineResult.article("Rome", "Rome is the capital", description="a city")
InlineResult.photo(message.file_ref, caption="from the album")
InlineResult.photo("https://example.com/cat.jpg")
InlineResult.animation("https://example.com/loop.mp4")
InlineResult.video(file_ref, title="The clip")
InlineResult.audio(song, title="The song")
InlineResult.voice(note)
InlineResult.document(paper, title="The paper", mime="application/pdf")
InlineResult.sticker(sticker)
InlineResult.location(41.9, 12.5, "Rome")
InlineResult.venue(41.9, 12.5, "The place", "A street")
InlineResult.contact("+390000000", "Some", last_name="Body")
InlineResult.game("chess")
```

Anything that carries a file takes either something Telegram already holds, which is
anything `send_media` takes, or a `http` link, which Telegram fetches for itself when the
result is picked. A link has to still work then, which is the practical difference.

The title and the description are what the person reads in the list; the text is what they
send by picking it, and the two have no reason to be the same. A keyboard under the sent
message is `reply_markup=`, built the usual way:

```python
InlineResult.article(
    "Rome",
    "Rome is the capital",
    reply_markup=keyboard([Button.callback("More", "more:rome")]),
)
```

## Ids, and knowing what was picked

Every result carries an id. One is made up when you do not pass one, which is fine until
you want to know which of your results people actually pick, because that id is what comes
back:

```python
@app.on_inline_query()
async def answer(client, query):
    await query.answer([
        InlineResult.article("Rome", "...", id="city:rome"),
        InlineResult.article("Milan", "...", id="city:milan"),
    ])


@app.on_chosen_result()
async def picked(client, chosen):
    await count(chosen.id)          # "city:rome"
```

`on_chosen_result` needs inline feedback turned on in BotFather, and Telegram samples it
for busy bots, so it counts what people pick instead of witnessing every pick.

A chosen result can also be edited afterwards, but only if the result carried an inline
keyboard: that is when Telegram issues an id for the sent message. `chosen.editable` says
so, and editing one without it explains itself instead of failing obscurely.

## Paging

An answer takes at most fifty results. For more, hand back where this page ended and the
client asks for the rest by scrolling:

```python
@app.on_inline_query()
async def answer(client, query):
    start = int(query.offset or 0)
    page = await search(query.text, offset=start, limit=50)
    await query.answer(
        [InlineResult.article(one.title, one.url) for one in page],
        next_offset=str(start + len(page)) if len(page) == 50 else "",
    )
```

An empty `next_offset` means this is everything, which stops the client asking again.

## Caching, and answers built for one person

```python
await query.answer(results, cache_time=0, private=True)
```

`cache_time` is how long the clients may reuse this answer without asking again, five
minutes by default. `private` says the answer was built for this one person and must never
be shown to anybody else, which matters the moment a result depends on who asked. Setting
`private=True` and leaving `cache_time` high is the combination that caches per person,
which is usually what a personalised bot wants.

`gallery=True` draws the results as a grid of pictures rather than as a list of rows.

## Sending someone to the bot's own chat

A bot that has to be set up before it can answer says so with a button above the results
instead of with an apology no one can act on:

```python
if not await is_signed_in(query.sender.id):
    await query.answer([], switch_pm="Log in first", start_parameter="login")
    return
```

Pressing it opens the bot's own chat and sends `/start login`, which is where the setting
up happens.

## Filters

`filters.query` asks what has been typed:

```python
@app.on_inline_query(filters.query("weather"))
async def forecast(client, query): ...


@app.on_inline_query(filters.query(empty=True))
async def suggestions(client, query): ...
```

The empty query is the panel someone sees before they have typed anything, and it is worth
its own handler: searching for the empty string is not what they meant. `filters.regex`
works here too, since a query has text, and the filters about who asked work as they do
everywhere else.

## The other side of it

A user account can use inline bots instead of being one, which is [Talking to
bots](bots.md): `inline_results` asks a bot what it would offer, and `send_inline_result`
sends one of them.

Signature by signature: [Types reference](api/types.md#inline-mode).
