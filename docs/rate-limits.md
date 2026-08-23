# Staying inside the limits

Sunnygram paces calls by default, and it is on, not off because of what is at stake. A bot
that floods gets throttled. An account that floods gets limited, and an account that is
limited repeatedly gets taken away.

```python
app = Client("my.session", api_id=API_ID, api_hash=API_HASH)   # paced
```

Nothing to configure for the ordinary case.

## The two limits

Telegram counts calls of every kind against one budget, and counts messages into a single
chat against a much tighter one. They catch different programs: one pulling history from
twenty chats is nowhere near the second and can still trip the first; one answering a busy
group is the other way round.

So there are two buckets. A call waits on whichever is behind.

| | |
| --- | --- |
| every call | 20 a second, with a burst of 20 |
| into one chat | 1 a second, with a burst of 3 |

The numbers are deliberately conservative. Telegram publishes limits for bots and not for
accounts, so these are set from what the published ones imply.

File transfers go straight through. Telegram meters a file by the bytes on a connection
instead of by the calls made, which is the whole reason the file engine spreads parts
across several, and pacing those would undo it without making the account any safer. They
stay bounded by the connection pool and the in-flight cap instead.

## Changing it, or turning it off

```python
from sunnygram.network import RateLimiter

app = Client(..., rate_limit=RateLimiter(calls_per_second=8, sends_per_second=0.5))
app = Client(..., rate_limit=False)
```

Turning it off means owning what happens next. The reactive half stays either way: a short
`FLOOD_WAIT` is still waited out by the connection, not raised.

## Watching it

```python
limiter = app.invoker.limiter
print(limiter.waited)   # seconds this has held calls back, over its whole life
print(limiter)          # calls in hand, chats tracked, total waited
```

A number that keeps climbing means the program wants to go faster than the account safely
can. The answer is usually to do less, not to raise the limit.

## What it does not do

It does not know about the limits that are not per-second: how many groups an account may
join in a day, how many people it may message who have not messaged it, how many channels
it may create. Those are counted over hours and days, are not published, and no client-side
pacing can see them. `FLOOD_WAIT` with a long wait on it usually means one of those, and
the answer is to stop, not to sleep.
