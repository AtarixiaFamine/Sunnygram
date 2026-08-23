# Stories

Something posted to be seen for a day and then not. This is a user-account feature:
a bot has no stories to post.

## Posting one

```python
stories = await app.send_story("me", "sunset.jpg", caption="Tonight")
```

The file is a path, the bytes, or anything with a read method, the same as
`send_file`, and it has to be a photo or a video.

## Who sees it

`privacy` is the one argument that needs care, because the wire has no sensible
default and this library does.

```python
await app.send_story("me", "sunset.jpg", privacy="close_friends")
```

One of `everyone`, `contacts`, `close_friends`, `nobody`, or a list of raw
`InputPrivacyRule` for anything finer.

The reason it is a word, not a list: `stories.sendStory` takes a **required** list
of privacy rules, and an empty list does not mean "the default", it means **no
one**. So a story posted without thinking about privacy posts successfully and is
seen by no one, which looks exactly like a bug in your program. Here the default is
`everyone` and `nobody` has to be asked for.

## How long it stays up

```python
await app.send_story("me", "clip.mp4", period=12 * 3600)
```

Telegram takes 6, 12, 24 or 48 hours and refuses anything else, so this library
refuses anything else too instead of spending a round trip to find out.

`pinned=True` keeps the story on the profile after it expires.

## Reading them

```python
mine   = await app.get_stories("me")            # what is up now
theirs = await app.get_stories("@someone")
kept   = await app.get_pinned_stories("@someone")
some   = await app.get_stories("@someone", [12, 13])
```

**A list of stories routinely contains things that are not stories.** Telegram sends
a placeholder where a story exists but this account is not being shown it, and
another where one has been deleted. Sunnygram reads the first as a `Story` with
`available` set to `False`, and drops the second entirely, since nothing is left of
it but an id.

```python
for story in await app.get_stories("@someone"):
    if not story.available:
        continue           # there, but not for us
    print(story.id, story.caption)
```

## Changing and removing

```python
await app.edit_story("me", story_id, caption="Better words")
await app.pin_stories("me", [story_id])
await app.delete_stories("me", [story_id])
await app.read_stories("@someone", max_id)
```

## Being told about them

```python
@app.on_story()
async def posted(client, story):
    print("story", story.id)
```

One update covers posting, editing and taking down, so what arrives is the story as
it now stands.
