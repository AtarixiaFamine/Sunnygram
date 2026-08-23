# Files

## Downloading

```python
data = await message.download()                  # into memory, as bytes
path = await message.download(into="photo.jpg")  # onto disk, answers the path
```

Or from the client, given a message, the media off one, a document, or a photo:

```python
data = await app.download(message)
path = await app.download(message.media, into="file.bin")
```

Options:

| | |
| --- | --- |
| `into` | a path to write to; leave it out to get bytes |
| `workers` | how many pieces to fetch at once |
| `chunk_size` | how big each piece is |
| `progress` | a callable taking (done, total) |
| `limit` | refuse anything bigger than this |

```python
def show(done, total):
    print(f"{done}/{total}")

await app.download(message, into="big.zip", progress=show, limit=100 * 1024 * 1024)
```

`limit` refuses before fetching instead of after, which is the point of it for a program
downloading something it did not choose.

## Sending

```python
await app.send_file(peer, "holiday.jpg")           # works it out from the name
await app.send_photo(peer, "holiday.jpg", caption="**Crete**")
await app.send_document(peer, "report.pdf")
await app.send_video(peer, "clip.mp4", duration=12, width=640, height=480)
await app.send_audio(peer, "song.mp3", title="A Song", performer="Somebody")
await app.send_voice(peer, "note.ogg", duration=7)
```

The file is a path, the bytes themselves, or anything with a `read` method. Bytes have no
name to go on, so give them one:

```python
await app.send_document(peer, data, name="report.csv")
```

The caption is the message text, since Telegram has no separate field for one, and is
parsed exactly like a message: markdown by default, `parse_mode=` and `entities=` mean
what they do in [`send_message`](messages.md).

**The kind matters more than it looks.** The same bytes sent as a photo, a document, a
video and a voice note are four different things on the other side, and which one it is
comes down to what the send says, not to anything in the file:

| | |
| --- | --- |
| `send_photo` | Telegram re-encodes it and shows it inline. Not byte-for-byte. |
| `send_document` | Kept exactly as it is, including a picture you did not want re-encoded. |
| `send_video` | Plays in place. Pass `duration`, `width` and `height` or it may not. |
| `send_audio` | A music track, with `title` and `performer`. |
| `send_voice` | The round note that plays where it sits. |

`send_file` guesses from the extension and falls back to a document. Anything else takes
`kind=`:

```python
await app.send_file(peer, "holiday.jpg", kind="document")   # keep it exact
```

Other options: `thumb=` for a video's cover, `spoiler=True` to hide it behind a tap,
`ttl_seconds=` for a view-once picture, `reply_to=`, `silent=`, and `progress=` for the
same callable `download` takes.

## Writing a file down

Everything above names a file with an object, which is fine inside one program and useless
the moment the file has to outlive it. A queue, a database row, a config file and a log
line all want a string:

```python
written = message.file_ref            # or app.file_ref(message), or of media, or a photo
```

Hand that back later, from another process, out of a column, and the file is sent or
fetched with no upload and no download in between:

```python
await app.send_media(chat, written)
data = await app.download(written)
```

A reference is about eighty characters and carries the four things a file is named by:
which datacenter holds it, its id, the access hash this account was issued for it, and the
file reference token. It also carries a checksum, so a string that was truncated in a
column or had a character eaten by a URL fails as a reference instead of becoming a
request for some other file.

It is not a secret, but it is not nothing either: anybody holding one can fetch the file
with **their own** account only if Telegram lets them, and the access hash in it was
issued to this account. Treat it the way you would treat a link to the file.

**One part of it perishes.** The id and the access hash are good for as long as the file
exists. The file reference token goes stale after an hour or so, and the only cure is to
fetch whatever carried the file again. A reference made from a message remembers which
message that was, so it renews itself:

```python
written = message.file_ref                    # remembers the message
written = message.file_ref                    # a week later, this still works
await app.send_media(chat, written)           # renews the token and sends
```

If that is more than you want to write down, leave it out:

```python
written = app.file_ref(message, origin=False)
```

Without an origin a stale reference comes back as an error, and fetching the message again
is yours to do.

**Hiding it is asked for at the send**, not written into the reference:

```python
await app.send_media(chat, written, spoiler=True)
```

That is deliberate. Whether a file arrives behind a tap belongs to who is being sent it,
not to the file, so one stored reference serves both: the same cached photo goes out plain
to one asker and covered to the next without being written down twice. Asking here also
keeps the renewal above, which building the media yourself would cost you, since a media
on its own says nothing about which message it came from. In an album the same thing is
said per file, through `options`:

```python
await app.send_album(chat, [written, other], options=[{"spoiler": True}] * 2)
```

## Uploading without sending

```python
handle = await app.upload("photo.jpg")
```

The answer is a handle for attaching the file to something, good for one send and only for
a while. `send_file` does this for you; reach for `upload` when you are building a raw
`messages.SendMedia` yourself, for an album or a media kind nothing above wraps.

## Profile pictures

```python
path = await app.download_profile_photo("@durov", into="durov.jpg")
mine = await app.download_profile_photo()          # "me" by default
```

This asks Telegram for the full-size photo rather than using the small one carried around
in answers, so it costs a call before it costs a download.

## How it goes

A transfer opens its own connections to whichever datacenter it is talking to, as many as
it has pieces in flight, up to four. Telegram meters a connection instead of an account,
so that is what makes the pieces actually arrive at once instead of queueing. Ordinary
calls keep to one connection each, where their order and the update stream are safe.

A file in another datacenter is fetched from there without the account moving to it. A
file that has been moved is followed. A file reference that has gone stale is refreshed
and the transfer carries on, on the way down and on the way back out: sending a file that
Telegram already holds renews its reference once and tries again, as long as what you
passed says which message the file came from. A message says so, and so does a written
down reference.

## Files that come from a CDN

A popular file is not held by Telegram. It is held by a content delivery network Telegram
rents, and asking for one gets a redirect back instead of the bytes. Sunnygram follows
that by default, which is where most of the speed on a large public file comes from.

```python
# Followed unless you say otherwise.
await app.download(message, into="video.mp4")

# Kept inside Telegram, at the cost of whatever the CDN would have saved.
await app.download(message, into="video.mp4", cdn=False)
```

The interesting part is what the CDN is not told. It never learns whose file it is handing
over: no authorization is exported to it, and the only name it is given for the file is a
token that means nothing anywhere else. It never sees the file either, since what it holds
is encrypted with a key that arrives from Telegram in the redirect and is never sent on.

That leaves one thing it could still do, which is hand back the wrong bytes, and this does
not let it. Telegram publishes a SHA-256 for every block of the file, and no byte reaches
the caller without being hashed and compared against one. A mismatch is a `SecurityError`,
not a retry: the bytes are wrong, and going on with them would be the checking done for
nothing.

Two more things follow from a CDN being a cache. It can miss, and when it does Sunnygram
asks Telegram to push the file over and tries again, a few times, before giving up with a
message saying what happened. And a CDN datacenter is not in the built-in address table,
so the first file from one costs two extra calls: `help.getConfig` for the address, and
`help.getCdnConfig` for the public key that proves the server answering is the one we were
sent to. Both are kept for the rest of the session.

## Two things to know

**Pure-Python AES is too slow for media.** If no faster backend is installed, a 512 KiB
part is seconds of CPU. Install `cryptography` (or `sunnygram[speedups]`) before moving
anything large. See [Performance](performance.md).

Every option: [Layers reference](api/layers.md#files).
