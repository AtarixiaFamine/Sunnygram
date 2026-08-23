# Logging in

Sunnygram signs in to accounts that already exist. Registering a new one is deliberately
absent and will stay that way: bulk account creation is the abuse this kind of library
gets used for, and leaving it out costs a real user one trip to an official client.

## The easy way

`start` does the whole flow, asking for whatever is missing:

```python
app = Client("my.session", api_id=API_ID, api_hash=API_HASH)

await app.start(
    phone_number=lambda: input("phone number: "),
    code=lambda sent: input(f"code sent by {sent.kind}: "),
    password=lambda hint: getpass(f"password ({hint}): "),
)
```

Each of those may be a plain value, a function, or an async function. They are called only
when the answer is actually needed, which lets the same code work from a terminal, a web
form or a chat window. A session that has already been signed in needs none of them:

```python
await app.start()
```

`run` takes the same arguments and passes them through, so a script can be one call:

```python
app.run(phone_number="+1555...", code=lambda sent: input("code: "))
```

## Bot accounts

```python
await app.start(bot_token="123456:ABC-DEF...")
```

This is a bot over MTProto, not over the Bot API, which is the point: it reaches calls the
Bot API never exposed. For ordinary bot work Moonlygram is the friendlier tool.

## Two-factor authentication

If the account has a password, `start` asks for it through the `password` callable and
finishes the sign-in. The password itself never leaves the machine. What goes out is an
SRP proof built from it, and Telegram checks that against a verifier it holds instead of
against the password. Nothing that could be replayed into a password crosses the wire.

The callable is handed the account's hint, which is often the only reminder someone has.

## By hand

Under `start` are plain functions taking an invoker, for a program that wants to drive the
flow itself, retry a wrong code, or put a step behind a web request:

```python
from sunnygram.auth import send_code, sign_in, check_password
from sunnygram.errors import PhoneCodeInvalid, SessionPasswordNeeded

sent = await send_code(app.invoker, "+1555...")
# sent.kind says where the code went, sent.timeout how long until a resend is
# allowed, sent.next_kind how it would arrive if you asked again.

try:
    user = await sign_in(app.invoker, sent, code)
except PhoneCodeInvalid:
    ...  # ask again, same sent
except SessionPasswordNeeded:
    user = await check_password(app.invoker, password)
```

`resend_code(invoker, sent)` asks for another one, by whatever means `sent.next_kind`
named.

## QR login

An already-signed-in client scans a code and authorizes this one. Nothing is typed, which
makes it the pleasant option for a desktop program.

```python
from sunnygram.auth import sign_in_qr

async def show(token):
    # token.url is what goes in the QR code. It is a credential in flight:
    # show it to the person logging in and to no one else.
    print(token.url, "expires in", token.seconds_left, "seconds")

user = await sign_in_qr(app.invoker, show)
```

`show` is called again whenever a token expires and is replaced, so whatever is drawing
the code can redraw it. An account with a second factor raises `SessionPasswordNeeded`
here exactly as a phone login does, and `check_password` finishes it the same way.

## Logging out

```python
await app.log_out()
```

This ends the session on Telegram's side and takes the key out of storage. With the sqlite
backend that means the key bytes leave the file instead of merely losing their last
reference. The key is dead on the server whether or not the call succeeded, so it is
cleared either way.

## What a session is worth

A session file is the account. Anyone holding one is signed in as you, without a password,
without a code, and without triggering anything you would notice. Treat it the way you
treat a private key: do not commit it, do not put it in an image, and do not pass one
around a team. [Sessions](sessions.md) covers the storage side.

Signature by signature: [Layers reference](api/layers.md#logging-in).
