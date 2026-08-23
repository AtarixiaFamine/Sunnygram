# Proxies

```python
from sunnygram import Client, Proxy

app = Client(
    "my.session",
    api_id=API_ID,
    api_hash=API_HASH,
    proxy=Proxy.socks5("127.0.0.1", 1080),
)
```

One argument, and everything above it is unchanged. The proxy applies to every connection
the client opens, including the extra ones a file transfer spreads itself across and the
ones opened to other datacenters.

## The three kinds

A **SOCKS5** or **HTTP** proxy is a tunnel. It opens a socket to Telegram on your behalf
and then gets out of the way, so the datacenter is still what answers and nothing about
the protocol changes.

```python
Proxy.socks5("proxy.example", 1080)
Proxy.socks5("proxy.example", 1080, username="me", password="shh")
Proxy.http("proxy.example", 8080)
```

An **MTProxy** is not a tunnel. It speaks MTProto's own obfuscation, holds a shared secret, and
is told which datacenter to forward to inside the handshake, not by address. Use one where
Telegram itself is what is being blocked: the traffic is deliberately hard to tell from noise.

```python
Proxy.mtproto("proxy.example", 443, "dd0123456789abcdef0123456789abcdef")
```

The secret is read as hex or as the url-safe base64 form, since both are handed out for the same
proxy. A `dd` prefix means the proxy wants the padded framing, and Sunnygram switches to it for
you instead of letting the connection open and go quiet.

## From a link

```python
app = Client(..., proxy=Proxy.from_link("https://t.me/proxy?server=1.2.3.4&port=443&secret=..."))
```

Both the `tg:` and `t.me` spellings, and both kinds: a link with a secret is an MTProxy,
one with a user and a password is SOCKS5.

## Obfuscation without a proxy

The obfuscation an MTProxy speaks is useful on its own where the plain shape of MTProto is the
thing being noticed. It costs one cipher over the stream and hides the framing, the packet
lengths and the handshake.

```python
app = Client(..., obfuscated=True)
```

## Framings

Four, and the default is the right one unless something says otherwise.

| | |
| --- | --- |
| `Intermediate` | four bytes of length. The default |
| `Abridged` | one byte where the packet is small enough, which is most of them |
| `PaddedIntermediate` | intermediate plus random padding. What an MTProxy asks for |
| `Full` | length, sequence number and a checksum. Catches a corrupted stream by itself |

```python
from sunnygram.transport import Abridged

app = Client(..., codec=Abridged())
```

`Full` cannot be obfuscated: it has no framing tag, and the tag is what an obfuscated
handshake carries to say what follows.

## What is not here

A TLS-disguised MTProxy, whose secret starts with `ee`. Sunnygram refuses one of those with a
message saying so instead of failing later as a proxy that will not answer. A plain or `dd`
secret for the same proxy works.

## Errors

Everything above raises `ProxyError`, which is a `TransportError`, so code that only knows
about connections breaking still catches it. It is worth telling apart from the rest: a
datacenter that refuses is retried or migrated away from, and a proxy that refuses will
refuse again until the configuration changes.

A proxy never appears in a `repr`, and neither does an MTProxy secret or a proxy password.
They are credentials, and rule S2 is that secrets do not stringify.
