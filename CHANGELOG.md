# Changelog

All notable changes to Sunnygram are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-08-27

### Fixed

- **A container is judged in the order its counters say things happened**, not the order
  they were sent. Telegram routinely puts an update carrying `pts_count = 0` ahead of the
  one that actually moved the counter, both carrying the same `pts`: a read receipt in front
  of the message it acknowledges is the everyday case. Read in that order the receipt lands
  short of its own `pts` and is indistinguishable from a gap, so every one of them cost an
  `updates.getDifference` that came back with nothing to say. Nothing was ever lost, which is
  why this went unnoticed, but on an account being read while it is being written to it was a
  round trip per message under the lock everything else waits on.

  The reordering is per counter and never across them. `pts`, `qts` and each channel count
  separately, so their values are not comparable and one sort over the whole container would
  interleave streams by numeric coincidence; instead each stream's updates are rearranged
  among the places they already occupy. Everything else, counted or not, stays exactly where
  the server put it, and a container already in counter order, which is nearly all of them,
  is handed straight back.

  Ordering hands each update's counter on to the judging rather than letting it be worked
  out twice, because deciding which counter an update moves is several times the cost of the
  ordering itself and is the only part of this worth measuring. `benchmarks/delta.py` is the
  three shapes side by side: not ordering at all, ordering and working the counter out again
  to judge with, and ordering that hands it on. Working it out twice costs several times what
  the ordering does, which is more than the round trip this was written to save.

- **CI linted against ruff's default rule set**, which widens between releases: ruff 0.16
  folded pyupgrade, isort and more into its defaults, failing the build on code that had not
  changed (1.1.0 reports 1473 errors under it, 1230 of them `__slots__` ordering in the
  generated layer). The rule set is now pinned in `pyproject.toml`, so upgrading the linter
  no longer changes what the project enforces.

- **The import budget test measured the interpreter as much as the library.** It counts the
  modules `import sunnygram` adds to `sys.modules`, and the ceiling of thirty was set on 3.13,
  which preloads most of what the import reaches for. The same import costs 24 modules there
  and 35 on 3.11, so CI failed on the two older versions in the matrix while passing on the
  newest, with nothing about the library having changed. What means the same thing on every
  version is how many of our own modules the import costs, which is six, and that is what the
  test holds now. The total stays as a loose ceiling set for the oldest version in the matrix,
  where it still catches a dependency being imported eagerly.

- The comment on the bulk vector read quoted ratios no run had produced, 12x and 16x where
  rule P3, `benchmarks/rules.py` and this file all say about 10x and level at four. Checking
  a claim against the file that measures it is the whole point of quoting one.

- **`kind="auto"` called a webp or a bmp a photo**, which Telegram does not accept as one:
  jpg, jpeg and png are the whole list, and anything else offered as a photo comes back
  `PHOTO_EXT_INVALID`. webp is the format a sticker is made of, so a send that never named
  a kind failed on exactly the files a caller was least likely to have checked. Both
  classify as documents now, which is the kind that carries them intact, and `docs/files.md`
  says which extensions guess their way to a photo instead of leaving it to be discovered.

### Added

- **Star gifts**, in a new `methods/gifts.py`: thirty-nine methods covering the catalogue,
  what a peer owns, upgrading, transferring, resale, collections, auctions, offers and
  crafting. The second and largest slice of the payments surface.

  Three conventions carry the whole module. **A gift is named three ways and every method
  takes all of them**: Telegram addresses one by the service message it arrived in for a
  person, by a saved id beside the channel for a channel, and by a public slug once it has
  been upgraded. An int alone is a message id, an int with a peer beside it is a channel's
  saved id, a string is a slug with or without the link wrapped round it, and a raw
  constructor passes through. Nothing above has to know which spelling the call underneath
  wanted.

  **Anything that spends money says so in its name.** Half of these go through an invoice,
  which fetches a payment form and submits it, and the Stars leave the balance with nothing
  further asked. Every one of those is `send_` or `buy_` and nothing else is. The pair that
  makes it matter is upgrading: `upgrade_gift` spends nothing because whoever sent the gift
  paid for the upgrade too, and `buy_gift_upgrade` pays for one that was not. Same operation,
  different funding, and the name is the only thing that says which. `transfer_gift` and
  `buy_gift_transfer` are the same pair for the same reason.

  **One schema call that does five things is spelled as five methods.**
  `payments.updateStarGiftCollection` renames, adds, removes and reorders through four
  optional lists, and passing three Nones and one list is not an API.

  The filters on `get_saved_gifts` are spelled as what to keep where the schema has both
  halves of a pair, and keep the schema's `exclude_` spelling where it has only one side,
  because inventing a positive name for a flag with no complement would be describing
  something the server does not offer.

- **Telegram Stars beyond paying with them**, in a new `methods/stars.py`: seventeen methods
  covering subscriptions, revenue and affiliate programs, which were previously reachable
  only through `invoke`. The first slice of the payments surface; gifts, giveaways and
  auctions are still to come.

  Four things the shape of it is arguing with. **A balance belongs to a peer, not to the
  session**, since a channel has its own purse, so every call here takes one and defaults to
  the account rather than assuming it. **A subscription can be cancelled from either end and
  they are different calls**: the subscriber cancels by subscription id and a bot cancels by
  the charge id it was paid under, so `cancel_stars_subscription` and
  `cancel_bot_subscription` are separate names rather than one with a flag deciding which
  handle it was given. **Stars and TON are the same calls with a flag**, because Telegram
  added a second currency to the revenue side rather than a second set of methods, and
  inventing the distinction here would be inventing one the server does not make. And
  **`get_suggested_referral_bots(by=...)` takes a word** where the schema has two independent
  booleans that are meaningless together.

  `get_stars_withdrawal_url` takes the account password and never sends it: `password_proof`
  in `methods/account.py` is new alongside it and turns a password into the SRP proof the
  server actually wants, so nothing outside that module has to know a second factor is an
  exchange rather than a string. A test asserts the password reaches no request on the wire.

- **A stream that goes silent is caught up on anyway.** Every other recovery in the update
  layer starts from something the server said. This one starts from the server saying
  nothing, which is the one fault the counters cannot see: they only move when an update
  moves them, so a connection that has quietly stopped carrying updates leaves them exactly
  where a quiet account would, and the ping loop cannot tell the two apart because it proves
  the socket is alive, which was never in doubt. After a quarter of an hour without a word,
  the manager asks. `Client(idle_catch_up=...)` moves it or turns it off, and
  `app.updates.resyncs` counts the times it has had to.

- **`client.stream`**, which hands a file over a piece at a time, in order, instead of all
  at once. For anything that can start on the front of a file before the back of it has
  arrived, and for anything too big to want in memory. `offset` and `length` take a byte
  range, the same pair an HTTP range asks in, so serving a seek passes the numbers straight
  through; an offset in the middle of a chunk is rounded down and the head of the first piece
  dropped for you. Only the range asked for is fetched, so a hundred bytes off a sixty
  megabyte file is one round trip. One piece is in flight at a time, which is the trade and
  not an oversight: pieces have to be handed over in order, so fetching ahead only helps if
  they are held, and not holding them is the reason to be here. `download` is still the
  faster call when the whole file is what is wanted.

- **`sunnygram.compose`**, which runs several clients on one loop until interrupted. `run` is
  one account's program; this is the same thing for a program holding more than one, which
  otherwise meant writing the loop and the shutdown by hand and getting the shutdown wrong.
  Each client keeps its own session, connection and handlers, and all they share is the loop.
  They start one after another rather than at once, because starting can ask for a code and
  two accounts asking at the same moment is two prompts on one terminal, and whatever started
  is stopped again in reverse on the way out, including when one of the later ones fails to
  start.

### Changed

- **A vector of one fixed-width primitive is read in one `struct` call** instead of one call
  per item. `benchmarks/rules.py` measures about 10x on a thousand longs and level at four,
  and level at the short end is the point rather than a disappointment: the common vector is
  a handful of ids and pays nothing either way, and the ones worth anything are long. There
  are 128 such fields in the pinned schema and they are the ones that come back long, being
  message ids, user ids, read receipts and every difference batch. The reader decides this
  from the item reader the generated code already passes it, so nothing in `raw/` changed and
  nothing there knows about it. The bounds check is the same one, taken once over the whole
  span instead of once per item, so rule S3 is unchanged.

## [1.1.0] - 2026-08-23

### Added

Four surfaces that were reachable only through `invoke` now have friendly methods, which
was the last of the coverage gap: **statistics**, **boosts**, **shared folders** and
**sticker sets**. Around sixty-five methods in total.

- **Statistics.** `get_chat_stats` picks between the channel call and the supergroup call
  from the chat, so asking the wrong one is not a mistake available to make. Also
  `get_message_stats`, `get_story_stats`, `get_public_forwards` and `load_graph`, since a
  graph in an answer is a token rather than data and needs a second call to become one.
  `get_public_forwards` yields a `Message` or a `Story` depending on which each repost is,
  rather than dropping the kind not asked about.
- **Boosts**, with a `BoostStatus` type carrying the arithmetic Telegram leaves to the
  reader. `needed` is not `next_level_boosts - current_level_boosts`: the next level is
  measured from zero, so subtracting the two is off by every boost already spent. Also
  `get_boosts`, `get_my_boosts`, `get_user_boosts` and `boost`, plus a `Boost` type whose
  absent multiplier reads as one rather than none.
- **Shared folders**: exporting a link, previewing and joining somebody else's, taking or
  declining the chats a folder gains later, and leaving. Leaving names no chats by default,
  because leaving chats is the half that cannot be undone quietly.
- **Sticker sets**: created, added to, reordered, retitled, rethumbed and deleted, with
  `kind="regular" | "mask" | "emoji"` as one word where the schema has two independent
  flags. `upload_sticker` does the step that is easy to miss: a set is built out of
  documents and an upload is not one yet, so it registers the file and hands back something
  a set can actually hold.
- **`PeerCache.kind_of`**, which answers what sort of peer an id belongs to from memory
  and without a round trip. What `chat_stats` uses to choose its call.

- **An id spelled as text now resolves as an id.** Ids travel as strings, out of config
  files and command arguments and other programs' output, and one used to go to the server
  as a username and come back refused. A username has to start with a letter, so nothing
  written entirely in digits is one and there is nothing here to guess at. Both spellings
  work, `"777000"` and `"-1001234567890"` alike. A phone number is still the case that
  needs its `+`.

- **`Chat.marked_id` and `User.marked_id`**, the id in the spelling that says what it is
  without anything beside it. `id` stays the one the protocol uses, which is what a raw
  call wants and what not to keep on its own: `3003` on its own could be a person or a
  small group, and only the kind next to it settles which. This is the pair put back
  together, for anything writing a peer into a database or a config.

### Fixed

- **A `>` inside a styled run is a character, not a quote.** A blockquote is line-level,
  and it was allowed to begin anywhere a line did, including in the middle of a run that
  had not closed yet. The quote then took the rest of the line into a parse of its own
  while the run was still waiting, so the two ended up covering the same characters and
  the same styling was reported twice: `__>__` came back as two italics over a blockquote
  rather than one italic holding a `>`. It now begins only where a line does *and* nothing
  inline is open.

- **Text that begins with `>` no longer loses the character.** A literal `>` at the start
  of a line was written back out unescaped, so reading a message and sending it again
  turned the line into a quote and dropped the marker: `"> a"` came back as `"a"`. It is
  escaped where a line begins, and only there, since escaping every `>` would put
  backslashes through ordinary prose.

- **Runs that start on the same character now nest instead of crossing.** Both writers
  wrote opening marks in whatever order the entities arrived in, and Telegram does not
  promise an order. In HTML that produced `<i><b>abc</i>de</b>`, which is crossed tags
  rather than nested ones. In markdown it put a blockquote's marker inside a code span,
  where it stopped being a marker at all and `` >`a` `` came back as code reading `"> a"`.
  The widest run opens first now, and a line-level one ahead of an inline one covering the
  same characters.

- **A download with a byte limit no longer writes past it.** When the size is not known
  in advance the limit can only be enforced as the pieces arrive, and it was checked after
  each piece had been handed over rather than before. A caller downloading into a file had
  already written the piece that crossed the line, so a 5000 byte limit could leave 8192
  bytes on disk before saying the limit was reached.

- **An `Invoker` built to attempt nothing says so.** `attempts=0` left the retry loop with
  nothing to raise at the end and came apart on the assertion that said so, which under
  `-O` is not an assertion any more but a `TypeError` naming nothing. A negative `backoff`
  is refused for the same reason. Every other constructor in the library already checked
  its arguments this way.

### Changed

- **Filters are about 60% quicker.** `Filter.__call__` asked `inspect.isawaitable`
  whether the answer needed awaiting, and for the plain `True` or `False` almost every
  filter returns, that question cost more than the whole rest of the filter: it falls
  through to an abstract base class check to say no. Two identity tests settle it in
  front, and anything else still goes the long way. This runs once per filter per handler
  per update, so it is the most repeated question the library asks.

- **Reading markdown is about 58% quicker.** Two things ran once per character of every
  message parsed: the running UTF-16 offset was worked out by encoding the character, and
  the delimiter table was walked with a `startswith` per token. An offset in an entirely
  ASCII run is its length, and a character that is not the first character of any
  delimiter cannot begin one.

- **Writing markdown back out is about 30% quicker**, and HTML a little. Escaping was
  eight chained `str.replace` passes per character, which is one `str.translate` table
  built once; both writers encoded the text to UTF-16 a second time to count what they
  had already counted; and both rebuilt a small lookup dict for every entity.

- **About 10% off every TL read.** `read_bytes` and `read_raw` built a memoryview for
  each slice and then copied out of it, where `tobytes` does the same in one object.
  Strings are roughly a third of the cost of reading a payload.

- **`normalize_username` got about 27% off `learn`**, which is the function every users
  vector on the update path goes through. It was lowercasing the whole string once per
  prefix it checked, seven throwaway copies to answer a question about the first few
  characters, and it now walks the prefix list only for a name that carries something
  worth stripping. Behaviour is unchanged, checked against the previous implementation
  over 50,000 generated strings.

- **A `Chat` or a `User` now names a peer**, so anything `get_chat`, `get_user`, a dialog,
  a member or a message hands back goes straight into the next call. `resolve` already took
  the raw constructors those wrap; refusing the wrapped form meant every read followed by
  an act had to unwrap by hand, and the obvious unwrap, `.id`, is the one that throws the
  access hash away and leaves the call depending on the cache. The wrapper is resolved
  through the constructor it kept, which costs nothing and cannot miss.

## [1.0.1] - 2026-08-23

### Added

- **`get_members`**, which answers what each person is in a chat rather than only who they
  are: status, rights, custom title, who promoted them. Whoever created a chat is now one
  loop over `kind="admins"` looking for `MemberStatus.CREATOR`, where before it meant
  building a `channels.getParticipants` call with the admins filter and reading the
  participant constructors back by hand.
- **`get_participants` takes a `kind`**, so asking a chat for its administrators, its bots,
  the people thrown out, the people silenced, or the members who are also contacts no longer
  means dropping to `channels.getParticipants` by hand. `banned` and `restricted` are said
  the readable way round, because Telegram's own two names for them are the opposite of what
  they read as: its `kicked` is someone thrown out and its `banned` is someone still in the
  chat but silenced. Same convention the rights already use.

### Changed

- **`Target` is a union instead of `Any`.** The first argument of nearly every client method
  now says what it accepts, so an editor offers the right shapes and a checker refuses the
  wrong ones. The union is declared for type checkers only and stays `Any` at run time, so
  importing the library still loads six modules and none of the schema (rule P7). Narrowing
  an annotation cannot change behaviour, but code that was passing something a peer cannot be
  made from will now say so at the call rather than at the round trip.
- **`send_file(kind=...)` is a `Literal`** of the seven words it always accepted, so
  `kind="documnet"` is a type error rather than a document sent as a photo.

### Fixed

- `docs/chats.md` claimed administration was not wrapped and showed how to hand-build a
  `channels.editBanned` call for it. It has been wrapped for a long time, with twenty-one
  methods and a page of its own, and the stale section pointed people at the trap that page
  exists to explain.
- The README said "around ninety client methods". There are 135.

## [1.0.0] - 2026-08-23

### Added

- **`Dialog` and `Event` are exported from the top level**, which every other type a caller
  is handed already was. `Event` is what `on_raw` gives a handler and the one the docs call
  the escape hatch, so it was the odd one out among the eighteen; `Dialog` is what
  `get_dialogs` answers with, next to `Message`, `Chat` and `User` which were all there.
  Both were reachable by their full path, so nothing was broken, only inconsistent in the
  place a person looks first (rule H6).

- **`spoiler=` on `send_media`**, so hiding a file behind a tap composes with re-sending
  one. It did not before, and the two were mutually exclusive in a way nothing said out
  loud: a portable reference handed to `send_media` was resolved by `existing_media`, which
  built a plain media, and the only way to get a hidden one was to build the `InputMedia`
  yourself, which threw away the origin and with it the automatic renewal of a stale
  `file_reference`. So a program with a media cache had to choose between hiding a file and
  having a stale entry heal itself.

  Hiding is asked for at the send, not read off the file because that is where it belongs:
  the same cached photo goes out plain to one asker and covered to the next, which is also
  why a reference never writes it down. The flag only ever turns hiding on, so a media the
  caller built hidden stays hidden, and `existing_media` still returns a caller's own
  object unchanged when nothing is asked of it. Where it is, the media is **copied**, not
  marked in place: it may be the caller's object and a send is not entitled to change it.

  `spoiler` on an already-held entry of an album is taken out of that entry's `options`
  too, the same as one being uploaded. Reading it only on the upload path meant a cached
  photo could not be sent covered while a fresh one could.

  Found while porting an existing bot onto the library, which is where most of the gaps at
  this stage are being found.

- **Payments and Telegram Stars** (`methods/payments.py`, `types/payments.py`,
  `docs/payments.md`). Invoices for money and invoices for Stars are two builders, not one
  with a flag, because they differ in more places than a flag suggests: a Stars invoice has
  no provider, no provider token, and Telegram's own currency. `on_shipping` and
  `on_pre_checkout` handlers, with both questions arriving as objects that answer
  themselves; the successful payment as `message.payment`, since it comes on a service
  message instead of an update; Stars balance, ledger and refunds.

  **The rule this adds, written down because money is where a swallowed error costs someone
  something:** a pre-checkout query has about ten seconds to be answered, and an unanswered
  one is a customer whose payment fails with nothing said to the bot. So
  `answer_pre_checkout` logs at error and re-raises instead of passing anything over,
  rejecting without a reason is refused before it is sent (the reason is what the customer
  is shown), and the docstrings say the window out loud.

  `refundable` on a successful payment exists because two constructors carry one and only
  the seller's has the charge id a refund needs.

- **Stories** (`methods/stories.py`, `types/story.py`, `docs/stories.md`). Posting,
  editing, deleting, pinning, reading, views, and an `on_story` handler.

  Privacy is a word with a default, not the list the wire wants, and that is the point:
  `stories.sendStory` takes a *required* vector of privacy rules and an empty one means
  **no one**, so a story posted without thinking about it posts successfully and is seen by
  no one. `audience("nobody")` says so deliberately; the default is everyone. The allowed
  periods are checked here, not at the server, and a list of stories is understood to
  contain things that are not stories: a hidden one becomes a placeholder with `available`
  false, a deleted one is dropped, since nothing is left of it.

- **Scheduled messages.** `schedule_date` on `send_message`, `send_file` and everything
  that goes through them, taking a `datetime` or a timestamp, plus `get_scheduled` /
  `send_scheduled` / `delete_scheduled` and a `scheduled` handler kind.
  `sunnygram.WHEN_ONLINE` is Telegram's one magic value, a flag wearing a timestamp's
  clothes, and `schedule_at` passes it through rather than converting it into a message
  scheduled for 2038.

- **Folders** (dialog filters), with `Folder` reading the title out of the styled text it
  became a few layers ago, and telling an editable folder from one someone shared as a
  link. There is no create or delete call in the API: both are `updateDialogFilter` with a
  used or unused id, which the docs now say instead of leaving to be discovered.

- **Takeout sessions.** `app.takeout(...)` is an async context manager that wraps every
  call made inside it and closes the session on the way out, saying the export failed if it
  is leaving because something raised. `TakeoutInitDelay` staying outside the automatic
  flood wait is now pinned by a test, not being true by luck: it subclasses `Flood` without
  being a rate limit, and sleeping through it would block a program for hours with nothing
  said.

- **Editing the media on a message**, `app.edit_media` and `message.edit_media`, uploading
  first when given something not yet sent.

- **The raw API is typed all the way through: `invoke` now answers with what the call is
  answered with, instead of `Any`.** Every one of the 816 generated functions declares its
  own result, taken from the schema that already knew it, so
  `app.invoke(functions.help.GetConfig())` is a `Config`, a `Bool` call is a `bool`, a
  `Vector<ContactStatus>` is a `list[ContactStatus]`, and a type with several constructors
  arrives as the union of them, which is the list of cases the caller has to handle.
  `TLFunction` carried its result as a string all along and said in its own docstring that
  the string was for "the typed client layer that sits on top"; this is that layer. A raw
  API that hands back `Any` is a raw API a type checker cannot help with, which is the
  thing this closes.

  The eleven wrappers of the `{X:Type}` family stay generic instead of widening what passes
  through them, so `InvokeWithLayer(layer=..., query=GetConfig())` is still a `Config`.

  Free at runtime, which was the constraint worth respecting. Subscripting a generated
  class is a no-op that hands back the class itself, so no typing machinery is built for
  the thousands of classes in the generated tree and rule P7 is untouched: `import
  sunnygram` still loads no raw module at all. Measured, alternating in one process: 18.9
  us to create a class before, 24.5 us after, which on the largest module in the tree at
  259 functions is +0.8 ms against 111 ms, inside the noise. A real generic subscript would
  have been 37.8 us and was rejected for it.

  `TLResult` is covariant, and that is load-bearing, not decorative: the parameter is only
  ever something a call gives back, and without it the ordinary `bool(await invoke(...))`
  spelling stops compiling. Getting this wrong was the only thing the change broke, in
  seven places, and covariance fixed all seven without touching a call site.

- **`Client.invoke`.** The raw API's documented spelling was `app.invoker.invoke(...)`,
  which is the layer below leaking into the public surface, and it was the one place where
  the documented spelling was longer than it needed to be. `app.invoke` now takes the same
  arguments and the same types. `app.invoker` keeps working.

- `tests/test_typing.py`, which asks mypy what it makes of a small program and reads the
  answer back. Nothing at runtime can tell whether `invoke` returned a `Config` or an
  `Any`, so a type checker is the only witness this property has (rule C4).

- **The write path is no longer the one benchmark row that lost** (`codegen/gen_tl.py`,
  `raw/` regenerated, rule P8). A constructor whose fields are all fixed-width and none of
  them conditional has a layout that is known when the generator runs, so it is now written
  by one `struct` call instead of one method call per field. Measured with
  `benchmarks/rules.py`, quoted as the range four runs on one machine produce rather than
  the best of them: about 4x to 5x on `inputPeerUser`, 3.9x to 4.8x on `pong`, 3.1x on
  `updates.State` and 1.9x to 2x on a two-int constructor. Earlier rounds reported 5.5x and
  a prototype before that 5.9x, and four runs reached neither, so both were the top of a
  range being read as the middle of one. That is the same lesson twice, so the range is
  what is quoted now.

  It catches 113 of 2507 definitions. That sounds thin and is not: one flag, one string,
  one vector or one nested object and the layout stops being fixed, so what qualifies is
  exactly the small dense constructors, and those are the ones sent in quantity.
  `inputPeerUser`, `inputPeerChannel`, `inputUser` and `inputChannel` all qualify, and
  nearly every outgoing call names a peer.

  It is a fast path, not a replacement. `write_long` takes an id or a hash in either
  spelling, signed or unsigned, because that is how Telegram generates them, and struct's
  `q` refuses anything past `2**63`. So the generated body tries the layout and falls back
  to the field-by-field writing on `struct.error`, which costs nothing when it does not
  happen and is exactly what it always was when it does. `tests/test_codegen.py` holds both
  paths to the same bytes and drives the fallback with a real unsigned hash.

- **Conversations: `ask`, `wait_for` and `client.conversation`**
  (`sunnygram.conversation`). Asking a question and reading the answer in the same place,
  without a state machine in between. The dispatcher grew a table of questions waiting for
  an answer, consulted before the handler pass: a chat, a filter, a future and a deadline.
  Three things about it are decisions, not side effects, so all three are written down. A
  message that answers a question is not also offered to ordinary handlers, because a
  program asking someone's name does not want its command router reading the name;
  `exclusive=False` turns that off. Our own outgoing messages never answer a question,
  which is not an edge case: `ask` starts listening before it sends, so without that rule
  every `ask` would return the question it had just asked, and the first test written found
  exactly that. And a question no one answers raises `NoAnswer` and says so through the
  logger, instead of returning a `None` that fails somewhere further away (rule C3). The
  table is bounded and a wait gives its place back however it ends, cancellation included
  (P6).

- **Plugins: handlers in their own files** (`sunnygram.plugins`, `Client.load_plugins`).
  The decorators here record what a function asked for onto the function, so a plugin
  module needs no client to be readable, and the loader walks a package and attaches
  everything it finds. The names match the client's, and a test holds the two lists
  together. It refuses to be quiet about the three ways this goes wrong invisibly: a plugin
  that fails to import raises instead of being skipped, a package that yields no handlers
  at all says so, and loading twice really does register twice and returns the count that
  shows it.

- **`CallbackQuery.chat_id`**, the same shape `Message` already had and for the same
  reason: `chat` is built from the users and chats an update carried, and an update that
  carried none of them still has the peer inside it. A press on an inline message has no
  chat and answers `None`.

- **A stale access hash no longer breaks a peer for the life of the session file**
  (`Invoker`, `PeerCache.forget`, `Storage.drop_peer`, rules P4 and C3). An `access_hash`
  is a number Telegram gave this account for that peer and it can stop being accepted; when
  it does, every call naming that peer is refused with `PEER_ID_INVALID`,
  `CHANNEL_INVALID`, `USER_ID_INVALID` or `CHAT_ID_INVALID`. The bad hash was written down,
  so it survived the restart anybody tries first and the peer stayed broken until the
  session file was deleted, which is the usual advice for it. Now a call refused for one of
  those four reasons has the peers it named dropped from memory, from the pending batch and
  from the storage, and says so at warning level rather than quietly (C3). The call itself
  still fails and still raises what the server said, because the request in hand cannot be
  repaired without resolving again; what stops happening is the second failure.
  `client.forget_peer()` and `client.refresh_peer()` do it by hand, and the peers doc
  explains what a hash is, whose it is, and why none of this is portable between accounts.

- **The numbered rules that quote a ratio now have something that re-measures them**
  (`benchmarks/rules.py`, a release step in CONTRIBUTING.md). P3 claimed the shape of the
  generated codec was worth about 1.7x and nothing could tell whether that was still true,
  which makes it a comment, not a promise. The harness builds a twin of a real generated
  type with P3's two decisions reversed and nothing else changed, and sweeps the width,
  because the two decisions do not scale alike: skipping `__init__` saves a fixed amount
  per object, while the inline bounds check saves a call per field. First run said 1.63x at
  fifty fields and 1.31x at five, so the rule now quotes the range and says which end
  matters: `Message` is 49 fields, `User` 51 and `Channel` 50, and those are most of what a
  program actually reads. It stays out of CI, since a number measured on a shared runner is
  worse than no number.

- **The event loop is now part of the speedups ladder** (`sunnygram.loop`, rule P1). A
  Telegram client spends most of its life waiting on a socket, and asyncio's own loop is
  Python around a selector where `uvloop` is libuv. `sunnygram[speedups]` now installs
  `uvloop`, or `winloop` on Windows where uvloop has never shipped a wheel, and `app.run()`
  uses whichever is there. Nothing is installed as a policy at import: a library that calls
  `uvloop.install()` when it is imported has replaced the event loop of a program that may
  have chosen its own, and that surprise surfaces in someone else's code. So the choice is
  made in the one place the library creates a loop, not joins one, `Client.run`, which grew
  `fast_loop=False` for ruling it in or out of a bug. A program with its own loop keeps it
  and can opt in with `asyncio.Runner(loop_factory=loop.new_event_loop)`. `loop.describe()`
  says which rung this process got, next to `crypto.describe()`.

- **The update layer is now proved against a model, not a script**
  (`tests/test_updates_model.py`, new rule C5). Hypothesis generates the sequence of things
  a server does: gaps of one and of several, redelivery, `TooLong` on both streams, a
  session the server started for itself, updates the connection threw away. The server is a
  model that holds the real history and derives every answer from it, so a client asking
  from the wrong place earns the empty answer it deserves instead of the plausible one a
  script would hand back. Four invariants, of which the load-bearing one is that a counter
  is a claim: `pts = N` says the first N things have been handled, so everything below our
  own mark must have reached the program. Validated by reintroducing both faults this layer
  has actually had, and by simulating the classic form of it, where a detected gap is never
  recovered from and the stream silently stops. All three are caught, the first in a
  two-step shrunk counterexample.

- **A guard for rule S2.** The rule claimed a redaction guard enforced it and none existed;
  redaction was correct everywhere, but by hand, with one assertion behind it.
  `tests/test_redaction.py` now puts a canary key through every object known to hold one,
  and walks the hand-written package for any class with a secret-shaped field that would
  inherit a `repr` printing it. The second half is the one that matters, because it fails
  for a class no one has thought about yet.

- Tests for the client's own surface: that each decorator registers for the kind it names,
  that `run` starts and stops in the right order even when the work raises, and the
  branches where the client picks between two calls instead of delegating.

- **The dispatcher hears everything.** Five kinds of event out of twenty-nine was the
  ceiling on what could be written with this: a program cannot act on something it is never
  told about, however good the layers underneath are. This release takes it to twenty-one.
  Twelve of those arrive here, each with a decorator, a wrapper that reads the awkward
  parts of the constructor, and a test that produces the event: `on_inline_query`,
  `on_chosen_result`, `on_chat_member`, `on_join_request`, `on_deleted`, `on_reaction`,
  `on_poll`, `on_poll_vote`, `on_status`, `on_typing`, `on_blocked` and `on_stopped`.
  `docs/updates.md` has the table of which session sees which, because a handler that never
  fires is worse than one that errors. The remaining four came with payments, stories and
  scheduled messages: `on_shipping`, `on_pre_checkout`, `on_story` and `on_scheduled`.

- **Inline mode, both halves of it.** `answer_inline_query`, `InlineQuery.answer`, and
  `InlineResult` with a factory per kind: article, photo, animation, video, audio, voice,
  document, sticker, location, venue, contact, game. Each one works out which of Telegram's
  four result constructors it needs from what was passed, and anything that carries a file
  takes either something Telegram already holds, which is anything `send_media` takes, or a
  http link it fetches for itself. The message a result sends is styled when the answer
  goes out, not when the result is built, since the parse mode belongs to the client and a
  result is usually built before there is one in hand. The rule that goes with it is the
  one buttons taught: a query must be answered, an empty answer is a real answer, and an
  unanswered query is a person looking at a panel that never finishes loading.

- **`MemberUpdate`, which is a pair, not an event.** Telegram never says "joined" or "was
  promoted", it says what someone was and what they are now, and every question a program
  actually has is the difference: `joined`, `left`, `banned`, `promoted`, `demoted`,
  `restricted`, `by_self`, and `what` for a log line. The chat is named the way `resolve`
  takes it back, which closes a real trap: a bare channel id is a valid user id, so a
  greeter answering into it would have written to a stranger.

- **`JoinRequest`, with `approve` and `decline` on it.** Both directions already existed as
  a call; what was missing was being told the request arrived. `approve_all_join_requests`
  answers the whole queue in one call, because a week of requests answered one at a time is
  that many calls and the flood wait that comes with them.

- **`ReactionUpdate`, which says which of the two readings it got.** A user account is told
  the running totals and a bot is told what one named person changed, and neither is a
  summary of the other: the totals never say who, the per-person reading never says how
  many. `by_person` says which arrived instead of filling the other half with zeros.
  Telegram's paid reaction carries nothing to name it by, so it is the word `paid`, not an
  invented star that would collide with the star someone really sent.

- **`Poll` and `PollVote`.** The poll update carries the question only when the poll itself
  changed, which is once, and the results alone every other time, so `known` says which
  arrived and a poll with no question is the normal case, not a fault. `winner` answers
  nothing on a tie, since a tie is a real outcome and picking a side of it quietly is found
  out much later.

- **The small ones**: `DeletedMessages`, `Status`, `Typing`, `Blocked`, `Stopped`. The
  deletion one is worth reading about before it surprises someone: outside a channel
  Telegram does not say which chat the messages were in, so `chat_id` is nothing at all and
  `located` says so, rather than a plausible wrong number.

- **`filters.query`**, for what has been typed into an inline query so far. Naming words
  matches a query starting with any of them; `empty=True` is the other question, and a
  different one: the panel someone sees before they have typed anything, which deserves its
  own handler because searching for the empty string is not what they meant.

- **An existing session can be read.** `sunnygram.read_session(...)` takes a session file
  or a session string written elsewhere, works out which format it is, and hands back the
  state; `sunnygram.adopt_session(...)` writes it into a Sunnygram storage. The
  authorization key is the same MTProto key, so a migrated project is already logged in and
  no one has to type a code and a second factor to try something. Session **files** also
  carry the update counters, so the first run continues from where the old program stopped,
  and the peers with their access hashes, without which a project that stores chat ids in
  its own database cannot reach any of them until it meets them again. The formats read
  write Bot API style ids, so those are read back before they reach the cache. The file is
  opened read-only and left as it was found. Verified against real session files instead of
  synthesized ones, with those formats then frozen into the offline suite.

- **A Bot API style `file_id` can be read.** Hand one to anything that sends a file and it
  is sent with no upload and no download, so a migrating project's column of stored file
  ids keeps working instead of being re-uploaded. `sunnygram.read_file_id(...)` opens one
  up. Reading only, deliberately: Sunnygram's own `file_ref` remembers which message a file
  came from, which lets a stale reference renew itself, and a file id cannot carry that.
  Checked against ten ids produced by a real encoder for the format.

- **Logging, under the `sunnygram` logger.** No handlers and no levels are set, so the
  program decides where its output goes, but the moments that change how a program behaves
  are now said out loud: reconnections, datacenter moves, flood waits being sat out,
  updates being caught up on, a connection that stopped answering, a call given up on.
  Warnings and errors reach stderr with no configuration at all. Auth keys, session
  material, `api_hash`, passwords and message text are never logged, at any level. There is
  a guide at `docs/logging.md`.

- **Buttons, and being pressed.** Sunnygram could read a keyboard and press one, because
  that is the user-account side, and could not send one at all, which meant most bots could
  not be written with it. Now: `sunnygram.Button` for every kind of button,
  `sunnygram.keyboard` to lay them out, and `reply_markup=` on everything that sends. Which
  of the two kinds of keyboard is being built is worked out from the buttons, not asked
  for, because a callback button only belongs under a message and a plain label only
  belongs above the text field, so a mixture is refused here, not on the wire.
  `force_reply` and `remove_keyboard` are the two markups that are not keyboards.

- **`@app.on_callback_query(...)` and the `CallbackQuery` type.** A press arrives with who
  pressed it, where, which message it is under and the payload the button carried, and can
  answer, edit that message, change its buttons, reply, or fetch it. Answering is not
  optional politeness: Telegram holds a press open until something answers, and every
  client draws that as a spinner. A press on a message an inline query produced arrives as
  the same object, and editing one is routed to the datacenter that issued its id, since
  home knows nothing about it.

- **`filters.data(...)`**, matching a press by exact payload or by prefix, which is how a
  bot packs an argument into sixty-four bytes and reads it back. `filters.regex` works on a
  press too, because a press has text: its payload. So do the filters about who and where.

- **`app.edit_markup`**, `app.edit_inline_message`, `app.edit_inline_markup`,
  `app.answer_callback_query`, `message.edit_markup` and `message.buttons`.

- **A portable file reference.** `message.file_ref`, or `app.file_ref(anything)`, writes a
  file down as one string that survives the process: a database column, a queue, a config
  file. Hand it back to `send_media` or `download` and the file moves with no upload and no
  download in between. It is checksummed, so a string truncated in a column fails as a
  reference, not becoming a request for some other file (rule S3), and it carries where it
  came from, so it can renew its own token. `origin=False` leaves that out.

- **A stale file reference is renewed on the way out, not only on the way in.** The
  download path already refreshed one; sending had nowhere to put the retry. Now
  `send_media`, `copy_message` and `message.copy_to` renew once and try again whenever what
  was passed says which message the file came from, which a message and a written down
  reference both do. `download` does the same without being handed a `refresh`.

- **A reply arrives with the message it answers.** `message.reply_to_message` is filled
  from the other messages in the same answer, from the quote a quoted reply carries, or
  from a bounded record of the last thousand messages this client saw or sent, and `await
  message.get_reply()` is the same thing that fetches when none of those had it. A bot
  whose job is answering replies was paying a round trip per message and now pays none in
  the ordinary case. `message_cache=0` turns the holding off; `app.recent` says how well it
  is working.

- **`first_match=True` on the client**, which stops each group after the first handler
  whose filter said yes. Off by default, because the failure it produces is the quiet kind:
  a handler that never runs is harder to find than one that runs twice.

- `app.wrap_message`, for turning a raw message off a raw update into a bound one, with the
  reply linking and the remembering that the dispatcher gets.

- `sunnygram.peers.mark_peer`, a `Peer` as the one number that names it.

- `examples/buttons.py`, a bot with a working menu.

- **Downloads from a CDN.** A popular file is not held by Telegram at all: it is held by a
  content delivery network Telegram rents, encrypted, and asking for the file gets a
  redirect back instead of the bytes. Sunnygram follows one now, and everything about how
  it does that follows from the CDN being a party Telegram does not trust. It is reached at
  an address only `help.getConfig` knows and has to prove itself with a public key from
  `help.getCdnConfig` rather than either of the built-in ones. No authorization is exported
  to it, so it never learns whose file it is handing over. What it hands over is decrypted
  here, with a key that arrived from Telegram and never went near it. And every block is
  hashed and compared against the SHA-256 the real datacenter published: nothing unchecked
  reaches the caller, a mismatch is a `SecurityError`, and a block no one published a hash
  for is refused, not waved through. A cold cache is filled by asking Telegram to push the
  file over; a token that has aged out is asked for again. `download(..., cdn=False)` keeps
  the whole transfer inside Telegram.

- **Forum topics** (`methods/forum.py`, `sunnygram.types.Topic`): `get_topics`,
  `get_topic`, `create_topic`, `edit_topic`, `close_topic`, `reopen_topic`, `pin_topic`,
  `delete_topic` and `set_forum`, plus `reorder_topics` at the method layer. A `Topic` says
  what it is called, whether it is closed, how much in it is unread and what the last
  message was, and can send into itself.

- **`topic=` on everything that sends**: messages, files, albums and inline results. A
  topic is the message that opened it, so being in one is spelled as replying to that
  message, which is why `topic=` and `reply_to=` share one field and mean different things
  together: the reply names the message being answered, the topic names the thread it is
  in.

- `sunnygram.crypto.PublicKey.from_pem`, which reads both the bare PKCS#1 spelling Telegram
  sends and the wrapped SubjectPublicKeyInfo one.

- `create_auth_key(..., keys=)` and `select_key(..., keys=)`, which narrow what counts as a
  key we know. That is what makes a CDN handshake safe: accepting a built-in key from one
  would be accepting a server that is not the one we were sent to.

- `Invoker.prepare_cdn` and `Invoker.is_cdn`, for anything reaching a CDN datacenter for
  itself.

- `sunnygram.methods.reply_header`, the one place that decides what the reply field says.

- **The bot's own command menu**: `set_bot_commands`, `get_bot_commands` and
  `delete_bot_commands`. Everything else in `methods/bots.py` is a user account acting on a
  bot; this is the one thing a bot says about itself, and a program signed in with a token
  had no way to say it.

- **`get_member`** and the `Member` type. Nine constructors across two chat families
  collapse to six standings, and `member.is_admin` counts the creator, which testing for
  administrator alone does not. Both kinds of chat answer: a basic group has no call for
  one member, so the membership is fetched and the one asked about is picked out of it.

- **`send_media`**, which sends a file Telegram already holds without uploading it again.
  This is the cheap half of sending and there was no way to reach it: a program that kept
  what it sent, or is passing on what it received, was paying for a download and an upload
  to move bytes that never had to move. `send_album` takes them too, mixed with paths.

- **Animations.** `send_animation`, and `kind="animation"` on `send_file`. A gif is a
  soundless looping video with one attribute on it, and without that attribute the same
  bytes arrive as an ordinary video.

- **`options=` on `send_album`**, running alongside `files` the way `captions` does. A
  video in an album needs its duration and dimensions as much as one sent alone, and there
  was nowhere to say them, so every album video arrived as a file until Telegram had worked
  it out for itself.

- `Message.reply_file` and `Message.reply_album`, so answering with a file is as short as
  answering with text.

- `sunnygram.methods.existing_media`, which recognises the shapes that name a file Telegram
  already has, and says nothing instead of raising for the ones that do not.

- **Sending files**: `send_file`, `send_photo`, `send_document`, `send_video`, `send_audio`
  and `send_voice`. `send_file` works the kind out from the name and takes `kind=` to
  override it, and the caption is parsed exactly like a message.

- **More message methods**: `get_messages` by id, `search_messages` (paging itself),
  `read_history`, `pin_message`, `unpin_message`, `unpin_all_messages`, and `send_action`
  for the typing indicator. Pinning is quiet by default.

- **Chats and people**: `get_dialogs`, `get_participants`, `join_chat` (by name or invite
  link), `leave_chat`, `get_chat`, `get_user`, `get_contacts`, `block_user`,
  `unblock_user`, `update_profile` and `download_profile_photo`.

- A `Dialog` type, which is this account's relationship with a chat, not the chat itself:
  the unread count, whether it is muted or pinned, and the last message, which arrives with
  it, not costing a call.

- `sunnygram.peers.as_channel` and `as_user`, for the calls that want a peer spelled as one
  of those instead of as an input peer.

- `methods/` grew `media.py`, `chats.py` and `users.py` alongside `messages.py`.

- **Proxies** (`sunnygram.Proxy`). SOCKS5 and HTTP CONNECT tunnels, with a username and
  password where one is wanted, and MTProxy, which is not a tunnel at all: it speaks
  MTProto's own obfuscation, holds a shared secret and is told which datacenter to forward
  to inside the handshake. Secrets are read as hex or as url-safe base64, and a `dd` secret
  switches the framing to the padded one by itself rather than opening a connection that
  then goes quiet. `Proxy.from_link` takes the links Telegram hands around. A TLS-disguised
  (`ee`) secret is refused with a message saying so, not half supported.

- **obfuscated2** (`sunnygram.transport.obfuscation`), the stream cipher an MTProxy speaks,
  usable on a direct connection too with `obfuscated=True` for where the plain shape of
  MTProto is itself the thing being noticed.

- **Two more framings**: `Abridged`, which spends one byte on a length instead of four
  wherever the packet is small enough, and `PaddedIntermediate`, which an MTProxy asks for
  and what stops packet lengths being readable off the wire.

- **A rate limiter** (`sunnygram.network.RateLimiter`), on by default, which is the other
  half of rule S4. Two token buckets, one over every call and one per chat for the calls
  that write to a chat, since Telegram counts those separately. Transfers go straight
  through, being metered by bytes on a connection instead of by calls. Turn it off with
  `rate_limit=False` and own what happens.

- **Chat administration** (`methods/admin.py`): `promote`, `demote`, `restrict`, `ban`,
  `unban`, `kick`, `get_permissions`, `get_admin_rights`, `set_chat_title`,
  `set_chat_photo`, `set_chat_description`, `set_chat_permissions`, `set_slow_mode`,
  `create_group`, `create_channel`, `delete_chat`, `add_chat_members`,
  `export_invite_link`, `revoke_invite_link`, `get_invite_links`, `approve_join_request`
  and `get_admin_log`. Each works out whether it is looking at a basic group or a
  supergroup, which are two entirely separate APIs, and says plainly when the answer is
  that a basic group cannot do this.

- `AdminRights` and `Permissions`, which are what those take. Both say what someone **may**
  do: Telegram's own permission flags are inverted, so allowing a photo means clearing
  `send_photos`, and reading that wrong silences a chat. The flipping happens once, on the
  way to the wire. Presets for the ordinary cases.

- **Albums**: `send_album`, which does the three-step dance sendMultiMedia needs, and an
  `on_album` handler for the receiving side, which puts the parts back together after a
  short silence since Telegram marks neither the first nor the last. The parts still reach
  ordinary message handlers.

- **Polls**: `send_poll`, `vote`, `get_poll` and `close_poll`, plus `message.vote`. Answers
  are named by position throughout. Naming a correct one makes it a quiz.

- **Reactions**: `react`, `get_reactions` and `message.react`. Setting rather than adding,
  which is how the call works: reacting with nothing takes every reaction back.

- **More kinds of message**: `send_sticker`, `send_dice`, `send_location`, `send_venue`,
  `send_contact`, and `copy_message` / `message.copy_to`, which sends a message again with
  no sign of where it came from.

- **Talking to bots** (`methods/bots.py`): `click`, which presses a button by its label,
  its number or its position, `buttons_of`, `inline_query`, `send_inline_result` and
  `start_bot`. A link button and a button wanting the account password both refuse instead
  of doing something surprising.

- **The account itself** (`methods/account.py`): `get_sessions`, `terminate_session`,
  `terminate_other_sessions`, `set_password`, `remove_password`, `has_password`,
  `get_privacy`, `set_privacy`, `set_username` and `check_username`. Neither password ever
  reaches the wire, and privacy exceptions are a separate argument because Telegram reads
  the rules in order and a list built the other way round means the opposite of what it
  looks like.

### Changed

- **The licence is now the Mozilla Public License 2.0, not MIT.** MPL is file-level
  copyleft: a program may import Sunnygram whatever its own licence, closed included, and
  owes nothing for doing so, while changes to Sunnygram's own files are published under the
  same terms. That is the part MIT does not ask for and the part LGPL overcharges for,
  since LGPL's linking model was written for C and has no settled reading in Python. Every
  file under `src/` carries the notice from the licence's Exhibit A, the generated tree
  included, which the generators emit instead of anyone adding by hand. `pyproject.toml`
  declares it as the SPDX expression `MPL-2.0`, so the built wheel carries
  `License-Expression: MPL-2.0` and bundles the licence text.

- `dropped_events` and `resyncs` now say plainly that they count different things. An event
  dropped on the way out of the update layer is gone for good, because its counter has
  already been applied and no difference will mention it again; what the connection dropped
  on the way in is recoverable, and is what `resyncs` counts. The two had one description
  between them.

- `ARCHITECTURE.md` no longer calls the `methods/` modules mixins. They are plain functions
  taking an invoker, and have been for some time; the document had not followed the code.

- **`Handler.kind` is a fixed list, not any string.** `add_handler(kind="calback")` was not
  an error anywhere: it was a handler that never ran, and finding that takes an afternoon.
  It is now a `Literal` exported as `sunnygram.Kind`, so mypy says so. A test walks the
  readings table and the list of kinds against each other, since a kind in one and not the
  other is the same silent fault by another route.

- **A reading no one asked for is no longer built.** The dispatcher used to wrap every
  message before offering it around, so a program with one inline handler in it paid to
  wrap every message in every chat it could see. The handlers are already indexed by the
  kind they asked for, so asking that index first is the whole of the saving. The
  isinstance chain that decided what to build became a table keyed on the update's type,
  which is what made adding twelve kinds a row each, not a chain three times longer.

- **A built-in filter asked about something it cannot read says no.** It used to raise,
  which the dispatcher caught and logged, so a program with a media filter and a typing
  handler reported a fault about every update no one wanted. A filter written with
  `filters.make` is untouched: that one is the program's own, and one that raises is a
  fault to report, not a quiet no.

- **Wrapping an incoming message is about a fifth cheaper.** Building a `Chat` for a
  private message wrapped a whole `User` in order to read four fields off it and then
  dropped it. Reading them off the raw user instead takes `Message.from_raw` from 26.0 to
  21.7 microseconds, and it is the piece of work that runs most often in any program that
  reads messages. Measured as the median of seven passes alternating between the old
  implementation and the new one in the same process.

- **The dispatcher no longer walks every handler for every reading.** Handlers are indexed
  by the kind they asked for, and the index is rebuilt when the list changes, not copied
  per update. Worth 10 to 16 percent of the cost of feeding one update, more the smaller
  the handler set, since a large one spends its time in filters instead. The public
  `handlers` field stays the source of truth, so appending to it directly still works.

- **`locate` and `send_media` take a string.** Anything that names a file now also accepts
  the portable reference form. A string that is not one comes back as "not a file Telegram
  already holds", not as an error about references, since a path is a string too and
  telling the two apart is the point.

- **`message.download()` sends the message down rather than the media off it.** The media
  alone does not say which message it came from, which a stale reference needs to renew
  itself.

- `sunnygram.types` gained `buttons.py` and `callback.py`, and `Chat.of_peer`. Neither new
  module imports anything the package did not already import, so what `import sunnygram`
  costs is unchanged: still no generated code, still twenty-four modules.

- **A download asks for a CDN redirect by default.** It previously never asked, and an
  answer that redirected anyway was an error.

- **The first piece of a download goes on its own.** What comes back for it is what says
  whether the file is Telegram's to serve or a CDN's, and four workers all asking at the
  same moment would all be redirected separately and pay for it.

- `StopPropagation` is exported from the top level, where handler code needs it.

- A frame is now built and written as one step under the send lock. Both the full codec's
  sequence number and the obfuscation keystream advance once per frame and have to advance
  in the order the frames reach the wire, so building one and writing it could not stay two
  separately ordered steps.

- MTProxy secrets are base64-decoded strictly. The lenient reading silently drops whatever
  it does not recognise, and a secret that is quietly wrong is a proxy that will not answer
  with nothing said about why.

### Fixed

- **The table of every handler kind listed seventeen of twenty-one.** `docs/updates.md`
  calls it every kind of handler, and it was written before payments, stories and scheduled
  messages added `on_shipping`, `on_pre_checkout`, `on_story` and `on_scheduled`. Each of
  those is documented on its own page, so nothing looked missing unless you counted, and
  this is the page someone reads to find out what can be handled at all. The four rows are
  there now, in both that table and the one saying which session sees which, and
  `tests/test_docs.py` fails if the table and `KINDS` part company again.

- **`docs/performance.md` quoted codec ratios no one could reproduce**, 5.5x on
  `inputPeerUser` where four runs give 4x to 5x, and 1.75x on a fifty-field read where the
  rule says 1.65x and the harness agrees with the rule. It also carried a stray list item
  orphaned below a paragraph. The numbers now match rules P3 and P8, which the page points
  at instead of restating, since restating them is what let them drift.

- **Three documented things did not exist.** `docs/sessions.md` spelled exporting a session
  as `await app.invoker.storage.load()`, and the invoker has no public `storage`: the line
  raises `AttributeError`. It is `app.invoker.state`, which is a property, not a coroutine,
  so the `await` was wrong too. `docs/inline.md` passed `message.photo` to
  `InlineResult.photo` and a message has no `photo`; it is `message.file_ref`. Two examples
  also used a module they did not import. None of this raised anywhere in the suite,
  because the suite did not read the docs.

    That is now the fix rather than the three corrections: `tests/test_docs.py` walks every
  Python block in `docs/`, collects what each one reaches for off the client, the invoker,
  a message, the package, the filters and the plugin decorators, and asserts the attribute
  exists. Three hundred and forty-nine references, and it catches both this and the
  `SQLiteStorage` fault recorded above.

- **Forty-eight of the fifty public names were invisible to `dir()`.** The package resolves
  its exports through a lazy `__getattr__` so that `import sunnygram` stays cheap (rule
  P7), and PEP 562 pairs that with a `__dir__` the package did not have. Without one,
  `dir(sunnygram)` and a REPL's tab completion see only what has already been imported,
  which on a fresh interpreter is two names out of fifty. Nothing raised and every
  documented call worked, so the only symptom was an API that looks empty to anybody
  exploring it, not reading the docs. `__dir__` now answers from the name table, which
  costs nothing and imports nothing: `import sunnygram` is still twenty-four modules and
  still no generated code, and `tests/test_package.py` holds both halves, the listing and
  the cost. The same gap existed one level down, in the generated `raw.types` and
  `raw.functions` namespaces and in `raw` itself, where `dir()` returned two names out of
  thirteen hundred. That is the layer the raw API guide sends people to, so the fix is in
  `codegen/gen_tl.py` and the tree is regenerated from it.

- **Four kinds of event could not be handled from a plugin file.** `plugins.py` had
  seventeen decorators where the client had twenty-one: `on_scheduled`, `on_shipping`,
  `on_pre_checkout` and `on_story` were never added when the payments and stories work grew
  the client. A plugin asking for one failed at import with an `AttributeError`, and the
  documentation said the two sets matched, so the page a reader would check to find out was
  the page that was wrong.

  The two lists live in different files and nothing held them together. That is the actual
  fault, so the fix is a test, not four functions: `tests/test_plugins.py::TestSurface`
  compares the plugin decorators against the client's and against the dispatcher's `KINDS`,
  and fails if any of the three drifts from the others again.

- **A message the client had just sent did not know which chat it was in, so it could not
  be edited, deleted or replied to.** Every send in a private chat came back that way,
  which is to say every send a bot makes to a person. The visible failure was
  `SunnygramError: this message does not say which chat it is in`, raised not by the send
  but by whatever was done with the message afterwards.

  There were two implementations of the same thing. `methods.messages` rebuilt the message
  the shorthand stands for and set its peer; `Client._message_out_of` had its own copy that
  put the raw `updateShortSentMessage` in `raw` and set no peer at all, and the client is
  the layer everything public goes through. The two had drifted, and only the correct one
  was tested.

  The scripted test server hid it perfectly: it answered every send with a full `Updates`
  carrying the message and the user, which is what a group looks like. Telegram answers a
  private chat with `updateShortSentMessage`, which names no chat. So the client-layer path
  that real Telegram takes on every send to a person had no test at all, while the
  methods-layer path that Telegram takes less often had four.

  The duplicate is gone: `methods.rebuild_sent` is now the one account of what a shorthand
  stands for, and the client calls it. The four call sites that resolve a peer keep it
  instead of dropping it, since the peer is exactly what the answer leaves out. The test
  server can now answer a send the short way (`sends_are_short`), and
  `TestAMessageWeJustSent` sends one and then edits, deletes and replies to it.

- **The two vendored server RSA keys were labelled the wrong way round, so no handshake
  with a real datacenter could ever succeed.** Every production connection asked for the
  test key, and every server refused it with `SecurityError: the server offered no key we
  know`. It was found by the first attempt to connect to a real datacenter.

  The bytes were right. Both keys came from Telegram Desktop and agree with TDLib byte for
  byte, exactly as the module said, and that check is what gave the false confidence: it
  establishes that the keys are genuine and says nothing about which is which.

  Nothing offline could have caught it. The scripted server in the test suite generates its
  own keypair and offers its own fingerprint, so the handshake tests pass whichever way
  round the labels are, and so did every test in `test_crypto_rsa.py`: they compared the
  two keys to each other, checked their shape, and pinned the fingerprint of a third,
  retired key. Not one of them named the production key.

  Now pinned to `0xd09d1d85de64fd85`, the fingerprint dc 2 actually asks for, observed
  against a live datacenter rather than derived from anything in this repo. The lesson is
  written into the module: for a constant whose only meaning is which server accepts it, a
  test that does not involve a server can check everything except the thing that matters.

- **Renewing a stale file reference threw away everything else the send said.** Found by
  the test written for `spoiler=` on `send_media`, and it is the more serious half. The
  retry replaced the whole media with the one fetched from the message, so a send that was
  hidden came back plain, and a `ttl_seconds`, a `video_cover` or a `video_timestamp` was
  dropped on the floor with it. None of them can be recovered by fetching the file again,
  because they describe the send and the file has never heard of them.

  Renewal now swaps the token and nothing else (`with_reference`), keeping the media the
  caller asked for and pointing it at the file as just found. A copy instead of a flag set
  in place, since the media carried through the retry may be the caller's own object. A
  message that carries a different kind of file now is the one case with nothing to
  preserve, and takes the fresh one.

- **A call answering with `Vector<int>` or `Vector<long>` could not be read at all.** Those
  two results are the vector id followed by *bare* numbers, and nothing in the bytes says
  so, so the reader treated the elements as boxed objects and the number three came back as
  `UnknownConstructorError: 0x00000003`. The function that was called is the only thing
  that knows, so the answer is now read with its `RESULT` in hand (`tl.read_answer`, used
  by the connection). Latent until now because nothing implemented had one of these
  results; `stories.deleteStories` and its neighbours do.

- **`stories.editStory` shares one flag bit between `caption` and `entities`**, unlike
  `sendStory` where they have one each. Setting the caption alone set the bit and then
  wrote one of the two fields, producing a request no reader can parse and a call that hung
  instead of failed. The entities now always travel with the caption. Same family as the
  `user.bot` / `bot_info_version` pair already recorded: a shared flag bit means the fields
  are not optional independently.

- **A channel could lose any number of messages, silently, whenever the server said it had
  fallen behind.** `updateChannelTooLong` carries the channel's own `pts`, and that number
  was being passed straight into `updates.getChannelDifference` as the position to ask
  from. It is the wrong end of the gap. The server is saying where it has got to, so asking
  from it means asking what has changed since the newest thing there is, which answers
  `channelDifferenceEmpty` every time. That empty answer was then written down as the new
  mark, so the gap was not closed but erased, and a channel could skip hundreds of messages
  with nothing in the output to say so. The cursor is now always our own stored mark; the
  number on the update is used only by a channel we have never followed, which adopts it
  because it has nothing to catch up on. The test covering this passed throughout, because
  it used the same value for the update's `pts` and for the stored one, and two numbers
  that agree cannot distinguish the two things they might mean. It now uses different ones,
  which is rule C4 read one level further: producing the fault is necessary, and so is a
  fixture that can tell the right answer from the wrong one.

- **The keepalive could not run on a busy connection.** The ping went out through the same
  path as ordinary calls, so it waited on the in-flight semaphore, and its pong timeout did
  not start until it got a slot. On a saturated connection the one thing that notices a
  half-open socket was queued behind the traffic it exists to protect. Housekeeping now
  bypasses the cap, which is what the cap always meant: it bounds a program's own work, and
  a ping is not that.

- **Running out of difference slices looked like success.** Both `getDifference` and
  `getChannelDifference` stop after `MAX_SLICES` rounds, and until now they fell out of the
  loop and returned as though the catch-up had finished. The gap was smaller and still
  there, with nothing said about it. Both now log and count a failure (rule C3).

- **A channel update naming no channel wrote a mark under the id zero.** Nothing in the
  schema produces one, so it means malformed server data, but the junk entry persisted to
  storage and was compared against for the life of the session. Such an update is now
  delivered without moving any counter, and says so.

- **Every constructor in the generated layer was unhashable.** `TLObject` defines `__eq__`,
  which drops the inherited `__hash__`, so no raw object could go in a set or key a dict.

- **A username pasted from a desktop browser did not resolve.** `www.` was not among the
  prefixes stripped, so `https://www.t.me/name` normalized to `www.t.me`.

- **`CdnSession` had no `repr` of its own**, so the class holding a file's decryption key
  fell back on the default. Found by the new redaction guard on its first run.

- **The documented way to bring a session over did not run.** `docs/importing.md` opened
  with `sunnygram.SQLiteStorage("sunny.session")` and that name was never exported from the
  package, so the first thing anyone following the migration guide typed raised
  `AttributeError`. `SQLiteStorage` and `MemoryStorage` are exported now, and
  `adopt_session` takes a path as well as a `Storage`, so the two-line version in the
  README is the whole of it. The path is named through the same helper `Client` uses, which
  is the part that matters: had they been spelled separately, `adopt_session(...,
  "account")` would write `account` while `Client("account")` opened `account.session`, and
  the symptom of that is being asked to log in again, which is indistinguishable from the
  importer not working. `tests/test_migrate.py` now holds the two to the same file.

- **Sixteen kinds of update were delivered a second time after every resync.** The other
  counter, `qts`, covers secret chats and a long list of events that reached the protocol
  later: a member joining or leaving, a join request, a vote cast in a poll, a reaction,
  someone blocking a bot. The arithmetic knew about one of the seventeen constructors the
  pinned layer gives a `qts` to, so for the other sixteen the mark never moved while the
  server's did. Nothing was lost and nothing arrived out of order, which is what kept it
  invisible: the next `getDifference` simply asked from a point the account had long since
  passed, and the server dutifully sent everything after it again. Every reconnect, every
  `new_session_created`, every sequence gap. A moderation handler written against these
  would have banned the same person twice. The counter is now read off the update's own
  field, not matched against a list of names, because the list is what fell behind, and a
  test walks the generated schema to assert that everything carrying a counter is counted,
  so the next layer bump reports a new one instead of quietly widening the hole.

- **Updates were silently lost after every reconnect.** The connection layer sent
  `new_session_created` to the update layer and said in its own docstring that this was
  treated as a reason to resynchronize. It was not: the update manager did not recognise it
  and dropped it. Updates are counted per session, so everything that happened while a
  socket was down went to a session that no longer existed and was never asked for. A
  program looked healthy and quietly missed messages from its first dropped connection
  onward. It now fetches a difference, and `manager.resyncs` counts how often that happens.

- **Updates dropped for backpressure were never made up for.** `Connection.dropped_updates`
  was documented as the update layer's cue to catch up, and nothing read it. A program too
  slow to drain the queue lost updates for good. The count is now carried across
  connections as `Invoker.dropped_updates`, and the manager fetches a difference when it
  moves. This matters most for the updates that carry no counter, since those leave no gap
  for anything else to notice.

- **One transient error could cost a channel its place in the stream, permanently.**
  `getChannelDifference` was wrapped in a blanket `except RPCError` that forgot the
  channel's `pts`. A `FLOOD_WAIT` or a 500 there meant the channel stopped being followed
  and nothing ever said so. Now only the errors that mean "this channel is not ours any
  more" forget it; a wait or a server hiccup leaves the counter alone and the gap is
  re-noticed later.

- **A machine with a wrong clock could never recover.** A session built on a stored key
  knows no time offset, and incoming messages were judged against the local clock, so on a
  machine out of step the first message was refused as a security error. That first message
  is exactly the `bad_msg_notification` that says what time it really is, so the correction
  could never arrive: the library was unusable on that computer, for good. A session with
  no offset now takes it from the first message the server sends, which has already proved
  it came from the holder of the auth key.

- **A half-open connection went unnoticed for ever.** The keepalive ping was sent and its
  answer ignored. When a laptop sleeps, a phone changes network, or a router drops a NAT
  mapping, the socket stays open, every write succeeds and no read ever returns. Nothing
  failed and nothing arrived. The pong is now waited for, and a connection that does not
  answer one is torn down so the invoker rebuilds it.

- **Telegram's "not right now" errors reached the caller as failures.** The 500 and -503
  family (`RPC_CALL_FAIL`, `WORKER_BUSY_TOO_LONG_RETRY`, `MSGID_DECREASE_RETRY`, `Timeout`
  and the rest) say nothing is wrong with the call, and every long-lived program meets
  them. They are now retried with the same bounded backoff a dropped connection gets.

- **`CONNECTION_NOT_INITED` was fatal to a session.** Telegram moves a session between its
  own machines and the new one has never heard of the application. The introduction is sent
  once per connection, so nothing above the connection layer could have fixed it and every
  later call would have been refused for the same reason. It now introduces itself again
  and resends.

- **A handler that raised said nothing at all.** The dispatcher swallowed it unless
  `on_error` was set, which is right for the stream and wrong for the person debugging:
  nothing above the dispatcher ever sees that exception, so the program simply appeared to
  ignore messages. It is now logged with its traceback, which reaches stderr with no
  logging configured.

- **A message the server answered a send with can now answer itself.** Nothing arrives
  alongside one to build a `Chat` from, so `message.chat` was `None` and `reply`, `edit`,
  `delete` and the rest all raised "this message does not say which chat it is in". The
  peer inside the message names the chat perfectly well and is what `resolve` takes, so
  they use that when there is no `Chat`. `message.chat_id` is the id either way.

- **A raw handler is called once per update, not twice.** Every update carrying a message
  reached `@app.on_raw()` twice: once with the `Event` it asked for, and once with the
  `Message` inside it, which is the reading the message handlers were for. So a handler
  doing the obvious thing with `event.update` raised on every message the program saw, and
  the dispatcher swallowed that as a handler failure. One reading now goes to one kind of
  handler.

- **A filter that raises no longer ends the update stream.** The filter call sat outside
  the protection the handler call had, so a `TypeError` in one filter took the dispatch
  task down and with it every other feature in the program. It is now reported like any
  other handler failure and the update carries on. This is the more important half of the
  rule, not the same one twice: a filter runs on updates its own handler never sees.

- The test suite no longer leaves sqlite connections or loopback sockets open. Those
  surfaced as resource warnings inside whichever unrelated test the garbage collector
  happened to be in; a leak is an error where it happens now.

### Known gaps

- Voice and video calls are not implemented. The signalling calls can be reached through
  `invoke`, but the media side of a call is a separate protocol this library does not
  speak.
- A TLS-disguised MTProxy secret is refused with an explanation of why. The plain and
  padded spellings of a secret both work.
- An album takes no keyboard. That is Telegram's own limit, not this library's.
- The crypto has not been independently audited. See `SECURITY.md`.
- The offline suite proves that calls are built correctly and cannot prove that a real
  server agrees with any of them. `examples/tour.py` is there to be run against a real
  account after any change below the client.

## 0.1.0 - 2026-08-01

An internal milestone that predates publication, recorded for continuity. It was never
tagged or released.

Eleven layers, from the TL codec up to the dispatcher, all written here rather than
wrapped.

### The protocol

- **TL codec** (`sunnygram.tl`), bounds-checked against hostile server data and failing
  closed on anything malformed.
- **The whole TL surface at layer 228** (`sunnygram.raw`), 2495 constructors and functions
  generated from a pinned schema into 81 modules, loaded one at a time so importing the
  library costs nothing.
- **TCP transport** (`sunnygram.transport`): the intermediate and full framings.
- **The authorization-key handshake** (`sunnygram.crypto`): AES-IGE and AES-CTR, MTProto
  2.0 key derivation, RSA_PAD, the server public keys, semiprime factorization, and every
  parameter check Telegram's security guidelines ask a client to make.
- **The session layer** (`sunnygram.session`): message ids, both message envelopes,
  sequence numbers, containers, and the incoming checks that go with them.
- **The connection loop** (`sunnygram.network`): one reader routing answers back to
  whoever asked, batched acknowledgements, a keepalive, updates on a bounded queue, and
  recovery from an expired salt, a drifted clock, or a sequence number the server will
  not accept.
- **The invoker** (`sunnygram.network.Invoker`): a key per datacenter, migration when the
  server says the account lives elsewhere, and a call that survives a dropped socket.

### The library

- **Logging in** (`sunnygram.auth`): phone and code, 2FA over SRP, a bot token, or a QR
  code another client scans. Registering a new account is deliberately absent.
- **Session storage** (`sunnygram.storage`): in memory, in a sqlite file created readable
  only by its owner, or in a 356-character string.
- **The update state machine** (`sunnygram.updates`): `pts`, `qts`, `seq` and a `pts` per
  channel, gaps recovered through `getDifference` and `getChannelDifference`. Every update
  delivered once and in order, or not at all.
- **The peer cache** (`sunnygram.peers`): usernames, phone numbers, ids in either
  spelling, and `"me"` all name the same person, and only a name this session has never
  seen costs a call.
- **The file engine** (`sunnygram.files`): chunked upload and download, several pieces at
  once across a pool of connections, following a file to whichever datacenter holds it and
  refreshing a stale file reference mid-transfer.
- **The client** (`sunnygram.Client`): a session, a connection, a peer cache, an update
  stream and a list of handlers behind one object, with markdown and HTML parsing that
  counts offsets in UTF-16 the way Telegram does.
- **Filters and handlers**: filters compose with `&`, `|` and `~`; handlers live in
  numbered groups and every one that matches runs unless one raises `StopPropagation`.
- **Every error Telegram documents** (`sunnygram.errors`): 780 of them, generated from
  Telegram's published error table with the official explanation as each docstring, and
  loaded only once a call is actually refused.

### Known gaps

- No CDN download path. Every file comes from the datacenter that holds it, which works
  and is slower than an official client for large public files.
- No `send_photo` and friends: `upload` gives you the handle and the send is a raw
  `messages.SendMedia`.
- No obfuscated transport, so no MTProxy.
- The crypto has not been independently audited. See `SECURITY.md`.

[1.2.0]: https://github.com/AtarixiaFamine/Sunnygram/releases/tag/v1.2.0
[1.1.0]: https://github.com/AtarixiaFamine/Sunnygram/releases/tag/v1.1.0
[1.0.1]: https://github.com/AtarixiaFamine/Sunnygram/releases/tag/v1.0.1
[1.0.0]: https://github.com/AtarixiaFamine/Sunnygram/releases/tag/v1.0.0
