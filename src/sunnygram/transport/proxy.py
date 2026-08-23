# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Reaching a datacenter through something else.

Three kinds, and they are not variations on one idea. A SOCKS5 or HTTP proxy is
a plain tunnel: it opens a socket to Telegram on this client's behalf and then
gets out of the way, so everything above it is unchanged and the datacenter is
still what answers. An MTProxy is not a tunnel at all. It speaks MTProto's own
obfuscation, holds a shared secret, and is told which datacenter to forward to
inside the handshake instead of by address, which is why it needs the framing
tag and the datacenter id that a tunnel never sees.

Which one matters depends on why the proxy is there. A tunnel is for reaching a
network that is merely elsewhere. An MTProxy is for reaching Telegram where
Telegram itself is what is being blocked, and it is deliberately hard to tell
from noise.

Nothing here decides anything. It opens the connection and hands back a stream,
and the transport above puts the framing on it.
"""

from __future__ import annotations

import asyncio
import ipaddress
from base64 import b64decode, b64encode
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import parse_qs, urlparse

from ..errors import ProxyError

__all__ = ["Kind", "Proxy", "open_through"]

Kind = Literal["socks5", "http", "mtproto"]

# What a SOCKS5 server can say went wrong, in its own numbering.
_SOCKS_FAILURES = {
    1: "the proxy failed for a reason it did not give",
    2: "the proxy's own rules do not allow this connection",
    3: "the network is unreachable from the proxy",
    4: "the host is unreachable from the proxy",
    5: "the connection was refused",
    6: "the time to live expired",
    7: "the proxy does not support this command",
    8: "the proxy does not support this kind of address",
}

# The MTProxy secret spellings. A bare sixteen bytes is the original one; the
# two prefixes were added later, each announcing that the connection has to be
# dressed up in a particular way beyond the obfuscation itself.
_PADDED_PREFIX = 0xDD
_FAKETLS_PREFIX = 0xEE

# A proxy that answers with more than this is not answering, and a reply is a
# few dozen bytes in every case that works.
_MAX_REPLY = 8192


@dataclass(frozen=True, slots=True)
class Proxy:
    """Where to connect instead of straight to the datacenter.

    Build one through socks5, http or mtproto rather than by hand: each of them
    checks the things that are only wrong for its own kind.
    """

    kind: Kind
    host: str
    port: int
    username: str | None = None
    password: str | None = field(default=None, repr=False)
    # MTProxy only. The shared secret, already unwrapped from whatever spelling
    # it arrived in.
    secret: bytes = field(default=b"", repr=False)
    # Whether that secret asked for the padded framing. A dd secret does, and
    # ignoring it means the proxy drops the connection without saying why.
    padded: bool = False

    def __repr__(self) -> str:
        """Never the secret or the password (rule S2).

        These end up in logs and tracebacks, and an MTProxy secret is a
        credential: anyone holding it can use that proxy.
        """
        return f"Proxy({self.kind}, {self.host}:{self.port})"

    @classmethod
    def socks5(
        cls,
        host: str,
        port: int,
        *,
        username: str | None = None,
        password: str | None = None,
    ) -> Proxy:
        """A SOCKS5 tunnel, with a username and password if it wants them."""
        return cls(kind="socks5", host=host, port=port, username=username, password=password)

    @classmethod
    def http(
        cls,
        host: str,
        port: int,
        *,
        username: str | None = None,
        password: str | None = None,
    ) -> Proxy:
        """An HTTP proxy reached with CONNECT, which is the only verb used."""
        return cls(kind="http", host=host, port=port, username=username, password=password)

    @classmethod
    def mtproto(cls, host: str, port: int, secret: str | bytes) -> Proxy:
        """An MTProxy, with the secret written however it was handed over.

        Hex and the url-safe base64 form both appear in the wild, sometimes for
        the same proxy, so both are read here.
        """
        raw, padded = _unwrap_secret(secret)
        return cls(kind="mtproto", host=host, port=port, secret=raw, padded=padded)

    @classmethod
    def from_link(cls, link: str) -> Proxy:
        """A proxy out of one of the links Telegram hands around.

        Both the tg: and the t.me spellings, and both kinds: a proxy link with a
        secret is an MTProxy, one with a user and password is SOCKS5.
        """
        parsed = urlparse(link.strip())
        query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
        host = query.get("server") or query.get("host") or ""
        port = query.get("port") or ""
        if not host or not port.isdigit():
            raise ProxyError(f"{link!r} does not name a server and a port")

        if "secret" in query:
            return cls.mtproto(host, int(port), query["secret"])
        return cls.socks5(
            host,
            int(port),
            username=query.get("user"),
            password=query.get("pass"),
        )


def _unwrap_secret(secret: str | bytes) -> tuple[bytes, bool]:
    """The sixteen bytes at the heart of an MTProxy secret, and how to frame it.

    A bare secret is sixteen bytes. A seventeenth byte in front says the rest is
    to be used a particular way: dd means the padded framing, and ee means the
    connection has to be disguised as TLS on top of everything else, which is
    not something this library can do yet and is refused here instead of
    failing later as a proxy that will not answer.
    """
    raw = secret if isinstance(secret, bytes) else _decode_secret(secret)

    if len(raw) == 16:
        return raw, False
    if len(raw) == 17 and raw[0] == _PADDED_PREFIX:
        return raw[1:], True
    if len(raw) >= 17 and raw[0] == _FAKETLS_PREFIX:
        raise ProxyError(
            "this is a TLS-disguised MTProxy secret, which Sunnygram does not "
            "speak yet; a plain or dd secret for the same proxy will work"
        )
    raise ProxyError(f"an MTProxy secret is sixteen bytes, this one is {len(raw)}")


def _decode_secret(text: str) -> bytes:
    """Hex first, then url-safe base64, since both are used for the same thing."""
    cleaned = text.strip()
    try:
        return bytes.fromhex(cleaned)
    except ValueError:
        pass
    try:
        # These are handed out without their padding more often than with it.
        # Validated instead of not, because the lenient reading silently drops
        # whatever it does not recognise, and a secret that is quietly wrong is
        # a proxy that will not answer with nothing said about why.
        return b64decode(
            cleaned + "=" * (-len(cleaned) % 4), altchars=b"-_", validate=True
        )
    except (ValueError, TypeError) as exc:
        raise ProxyError("this secret is neither hex nor base64") from exc


async def open_through(
    proxy: Proxy, host: str, port: int, *, timeout: float = 15.0
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Open a socket to a datacenter through a proxy, and hand back the stream.

    An MTProxy is connected to and nothing more: it learns where to forward from
    the obfuscated handshake the transport sends next, not from anything here.
    A tunnel is told the destination now, and does not come back until it has
    reached it.
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(proxy.host, proxy.port), timeout
        )
    except (OSError, asyncio.TimeoutError) as exc:
        raise ProxyError(f"could not reach the proxy at {proxy.host}:{proxy.port}") from exc

    if proxy.kind == "mtproto":
        return reader, writer

    handshake = _socks5 if proxy.kind == "socks5" else _http_connect
    try:
        await asyncio.wait_for(handshake(reader, writer, proxy, host, port), timeout)
    except BaseException:
        writer.close()
        raise
    return reader, writer


async def _read(reader: asyncio.StreamReader, count: int) -> bytes:
    try:
        return await reader.readexactly(count)
    except (asyncio.IncompleteReadError, OSError) as exc:
        raise ProxyError("the proxy closed the connection mid-answer") from exc


async def _socks5(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    proxy: Proxy,
    host: str,
    port: int,
) -> None:
    """RFC 1928, and RFC 1929 for the password if the proxy asks for one."""
    methods = b"\x00\x02" if proxy.username is not None else b"\x00"
    writer.write(b"\x05" + bytes((len(methods),)) + methods)
    await writer.drain()

    version, chosen = await _read(reader, 2)
    if version != 5:
        raise ProxyError(f"the proxy answered SOCKS{version} rather than SOCKS5")
    if chosen == 0xFF:
        raise ProxyError("the proxy rejected every way of authenticating offered")
    if chosen == 0x02:
        await _socks5_password(reader, writer, proxy)
    elif chosen != 0x00:
        raise ProxyError(f"the proxy asked for authentication method {chosen}, which is unknown")

    writer.write(b"\x05\x01\x00" + _socks_address(host) + port.to_bytes(2, "big"))
    await writer.drain()

    version, reply = await _read(reader, 2)
    await _read(reader, 1)
    if version != 5:
        raise ProxyError(f"the proxy answered SOCKS{version} rather than SOCKS5")
    if reply != 0:
        raise ProxyError(
            f"the proxy would not connect to {host}:{port} ({reply}): "
            + _SOCKS_FAILURES.get(reply, "no reason given")
        )
    # The bound address comes back whether or not anyone wants it, and leaving
    # it in the buffer would put the first MTProto frame out by that many bytes.
    kind = await _read(reader, 1)
    await _read(reader, await _socks_address_length(kind, reader) + 2)


async def _socks5_password(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, proxy: Proxy
) -> None:
    user = (proxy.username or "").encode()
    secret = (proxy.password or "").encode()
    if len(user) > 255 or len(secret) > 255:
        raise ProxyError("a SOCKS5 username and password are 255 bytes at most")
    writer.write(
        b"\x01" + bytes((len(user),)) + user + bytes((len(secret),)) + secret
    )
    await writer.drain()

    _, status = await _read(reader, 2)
    if status != 0:
        raise ProxyError("the proxy did not accept the username and password")


def _socks_address(host: str) -> bytes:
    """A destination in the shape SOCKS5 wants, by what kind of address it is."""
    try:
        parsed = ipaddress.ip_address(host)
    except ValueError:
        name = host.encode("idna")
        if len(name) > 255:
            raise ProxyError(f"{host!r} is too long to be a SOCKS5 destination") from None
        return b"\x03" + bytes((len(name),)) + name
    if parsed.version == 4:
        return b"\x01" + parsed.packed
    return b"\x04" + parsed.packed


async def _socks_address_length(kind: bytes, reader: asyncio.StreamReader) -> int:
    if kind == b"\x01":
        return 4
    if kind == b"\x04":
        return 16
    if kind == b"\x03":
        return (await _read(reader, 1))[0]
    raise ProxyError(f"the proxy answered with address type {kind[0]}, which is unknown")


async def _http_connect(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    proxy: Proxy,
    host: str,
    port: int,
) -> None:
    """One CONNECT, and a status line that has to be a 2xx."""
    where = f"[{host}]:{port}" if ":" in host else f"{host}:{port}"
    lines = [f"CONNECT {where} HTTP/1.1", f"Host: {where}"]
    if proxy.username is not None:
        pair = f"{proxy.username}:{proxy.password or ''}".encode()
        lines.append(f"Proxy-Authorization: Basic {b64encode(pair).decode()}")
    writer.write(("\r\n".join(lines) + "\r\n\r\n").encode())
    await writer.drain()

    try:
        head = await reader.readuntil(b"\r\n\r\n")
    except asyncio.LimitOverrunError as exc:
        raise ProxyError("the proxy's answer to CONNECT was too long to be one") from exc
    except (asyncio.IncompleteReadError, OSError) as exc:
        raise ProxyError("the proxy closed the connection without answering CONNECT") from exc
    if len(head) > _MAX_REPLY:
        raise ProxyError("the proxy's answer to CONNECT was too long to be one")

    status = head.split(b"\r\n", 1)[0].decode("latin-1")
    parts = status.split(" ", 2)
    if len(parts) < 2 or not parts[1].isdigit():
        raise ProxyError(f"the proxy answered {status!r}, which is not an HTTP status")
    if not 200 <= int(parts[1]) < 300:
        raise ProxyError(f"the proxy refused CONNECT to {where}: {status}")
