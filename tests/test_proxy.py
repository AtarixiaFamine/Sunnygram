"""Getting out through a proxy.

The two tunnels are driven against scripted servers that speak their protocol
back, so the handshakes are exercised for real rather than asserted about. The
destination is a second loopback server, which is what proves the tunnel
actually joined the two ends rather than merely agreeing to.
"""

from __future__ import annotations

import asyncio
from base64 import urlsafe_b64encode

import pytest

from mtproto_server import closing
from sunnygram.errors import ProxyError, TransportError
from sunnygram.transport import Intermediate, TCPTransport
from sunnygram.transport.proxy import Proxy, open_through

SECRET = bytes(range(16))
PAYLOAD = b"sunnygram payload\x00\x00\x00"


class TestSecrets:
    def test_hex(self):
        proxy = Proxy.mtproto("proxy.example", 443, SECRET.hex())
        assert proxy.secret == SECRET
        assert not proxy.padded

    def test_bytes_straight_through(self):
        assert Proxy.mtproto("proxy.example", 443, SECRET).secret == SECRET

    def test_base64(self):
        encoded = urlsafe_b64encode(SECRET).decode().rstrip("=")
        assert Proxy.mtproto("proxy.example", 443, encoded).secret == SECRET

    def test_a_dd_secret_asks_for_padding(self):
        proxy = Proxy.mtproto("proxy.example", 443, (b"\xdd" + SECRET).hex())
        assert proxy.secret == SECRET
        assert proxy.padded

    def test_a_tls_secret_is_refused_rather_than_half_supported(self):
        secret = (b"\xee" + SECRET + b"example.com").hex()
        with pytest.raises(ProxyError, match="TLS-disguised"):
            Proxy.mtproto("proxy.example", 443, secret)

    def test_the_wrong_length_is_caught_here(self):
        with pytest.raises(ProxyError, match="sixteen bytes"):
            Proxy.mtproto("proxy.example", 443, "00112233")

    def test_neither_hex_nor_base64(self):
        with pytest.raises(ProxyError, match="neither hex nor base64"):
            Proxy.mtproto("proxy.example", 443, "not a secret at all!!")


class TestLinks:
    def test_an_mtproxy_link(self):
        proxy = Proxy.from_link(
            f"https://t.me/proxy?server=1.2.3.4&port=443&secret={SECRET.hex()}"
        )
        assert (proxy.kind, proxy.host, proxy.port) == ("mtproto", "1.2.3.4", 443)
        assert proxy.secret == SECRET

    def test_the_tg_spelling(self):
        proxy = Proxy.from_link(
            f"tg://proxy?server=1.2.3.4&port=443&secret={SECRET.hex()}"
        )
        assert proxy.kind == "mtproto"

    def test_a_socks_link(self):
        proxy = Proxy.from_link(
            "https://t.me/socks?server=1.2.3.4&port=1080&user=me&pass=shh"
        )
        assert (proxy.kind, proxy.username, proxy.password) == ("socks5", "me", "shh")

    def test_a_link_naming_nothing(self):
        with pytest.raises(ProxyError, match="server and a port"):
            Proxy.from_link("https://t.me/proxy?secret=00")


class TestRedaction:
    def test_the_secret_never_stringifies(self):
        proxy = Proxy.mtproto("proxy.example", 443, SECRET)
        assert SECRET.hex() not in repr(proxy)
        assert str(SECRET) not in repr(proxy)
        assert "proxy.example:443" in repr(proxy)

    def test_the_password_never_stringifies(self):
        proxy = Proxy.socks5("proxy.example", 1080, username="me", password="hunter2")
        assert "hunter2" not in repr(proxy)


class TestSocks5:
    async def test_it_reaches_the_far_end(self):
        async with _destination() as target:
            async with _socks5_server() as proxy_port:
                proxy = Proxy.socks5("127.0.0.1", proxy_port)
                assert await _round_trip(proxy, target) == PAYLOAD

    async def test_with_a_username_and_password(self):
        async with _destination() as target:
            async with _socks5_server(username="me", password="shh") as proxy_port:
                proxy = Proxy.socks5(
                    "127.0.0.1", proxy_port, username="me", password="shh"
                )
                assert await _round_trip(proxy, target) == PAYLOAD

    async def test_a_wrong_password_is_reported(self):
        async with _destination() as target:
            async with _socks5_server(username="me", password="shh") as proxy_port:
                proxy = Proxy.socks5(
                    "127.0.0.1", proxy_port, username="me", password="wrong"
                )
                with pytest.raises(ProxyError, match="username and password"):
                    await _round_trip(proxy, target)

    async def test_a_proxy_that_refuses_says_why(self):
        async with _socks5_server(refuse=5) as proxy_port:
            proxy = Proxy.socks5("127.0.0.1", proxy_port)
            with pytest.raises(ProxyError, match="connection was refused"):
                await open_through(proxy, "127.0.0.1", 1, timeout=5)

    async def test_a_proxy_offering_no_method_we_have(self):
        async with _socks5_server(no_method=True) as proxy_port:
            proxy = Proxy.socks5("127.0.0.1", proxy_port)
            with pytest.raises(ProxyError, match="every way of authenticating"):
                await open_through(proxy, "127.0.0.1", 1, timeout=5)

    async def test_a_proxy_that_is_not_there(self):
        server = await asyncio.start_server(_nothing, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        server.close()
        await server.wait_closed()
        with pytest.raises(ProxyError, match="could not reach the proxy"):
            await open_through(Proxy.socks5("127.0.0.1", port), "1.2.3.4", 443, timeout=5)

    async def test_a_name_rather_than_an_address(self):
        # A destination that is not an ip travels as a name, which is the whole
        # reason SOCKS5 has three address forms. The scripted proxy refuses
        # rather than resolving it, so nothing here leaves the machine.
        seen: list[bytes] = []
        async with _socks5_server(seen=seen, refuse=4) as proxy_port:
            proxy = Proxy.socks5("127.0.0.1", proxy_port)
            with pytest.raises(ProxyError, match="host is unreachable"):
                await open_through(proxy, "venus.telegram.org", 443, timeout=5)
        assert seen == [b"\x03" + bytes((18,)) + b"venus.telegram.org"]

    async def test_an_ipv6_destination(self):
        seen: list[bytes] = []
        async with _socks5_server(seen=seen, refuse=3) as proxy_port:
            proxy = Proxy.socks5("127.0.0.1", proxy_port)
            with pytest.raises(ProxyError, match="network is unreachable"):
                await open_through(proxy, "2001:b28:f23d:f001::a", 443, timeout=5)
        assert seen[0][:1] == b"\x04" and len(seen[0]) == 17


class TestHttpConnect:
    async def test_it_reaches_the_far_end(self):
        async with _destination() as target:
            async with _http_server() as proxy_port:
                proxy = Proxy.http("127.0.0.1", proxy_port)
                assert await _round_trip(proxy, target) == PAYLOAD

    async def test_with_a_username_and_password(self):
        async with _destination() as target:
            async with _http_server() as proxy_port:
                proxy = Proxy.http("127.0.0.1", proxy_port, username="me", password="shh")
                assert await _round_trip(proxy, target) == PAYLOAD

    async def test_the_credentials_are_basic_encoded(self):
        seen: list[bytes] = []
        async with _http_server(seen=seen, status=b"HTTP/1.1 407 Denied") as port:
            proxy = Proxy.http("127.0.0.1", port, username="me", password="shh")
            with pytest.raises(ProxyError, match="407"):
                await open_through(proxy, "1.2.3.4", 443, timeout=5)
        # base64 of "me:shh", which is what RFC 7617 asks for.
        assert b"Proxy-Authorization: Basic bWU6c2ho\r\n" in seen[0]

    async def test_no_credentials_means_no_header(self):
        seen: list[bytes] = []
        async with _http_server(seen=seen, status=b"HTTP/1.1 407 Denied") as port:
            with pytest.raises(ProxyError):
                await open_through(Proxy.http("127.0.0.1", port), "1.2.3.4", 443, timeout=5)
        assert b"Proxy-Authorization" not in seen[0]

    async def test_a_refusal_carries_the_status(self):
        async with _http_server(status=b"HTTP/1.1 403 Forbidden") as port:
            with pytest.raises(ProxyError, match="403 Forbidden"):
                await open_through(Proxy.http("127.0.0.1", port), "1.2.3.4", 443, timeout=5)

    async def test_something_that_is_not_http_at_all(self):
        async with _http_server(status=b"hello there") as port:
            with pytest.raises(ProxyError, match="not an HTTP status"):
                await open_through(Proxy.http("127.0.0.1", port), "1.2.3.4", 443, timeout=5)

    async def test_the_connect_names_the_destination(self):
        seen: list[bytes] = []
        async with _http_server(seen=seen, status=b"HTTP/1.1 403 No") as port:
            with pytest.raises(ProxyError):
                await open_through(Proxy.http("127.0.0.1", port), "1.2.3.4", 443, timeout=5)
        assert seen[0].startswith(b"CONNECT 1.2.3.4:443 HTTP/1.1\r\n")


class TestThroughTheTransport:
    async def test_a_tunnelled_transport_is_an_ordinary_one(self):
        # No obfuscation and no handshake beyond the tunnel's own: through a
        # SOCKS5 proxy the framing goes out exactly as it would direct.
        seen: list[bytes] = []

        async def serve(reader, writer):
            seen.append(await reader.readexactly(4))
            codec = Intermediate()
            writer.write(codec.encode(await codec.decode(reader)))
            await writer.drain()

        server = await asyncio.start_server(closing(serve), "127.0.0.1", 0)
        target = server.sockets[0].getsockname()[1]
        async with server, _socks5_server() as proxy_port:
            transport = TCPTransport(proxy=Proxy.socks5("127.0.0.1", proxy_port))
            await transport.connect("127.0.0.1", target)
            async with transport:
                await transport.send(PAYLOAD)
                assert await transport.receive() == PAYLOAD
        assert seen == [b"\xee\xee\xee\xee"]

    async def test_a_broken_proxy_is_a_transport_error(self):
        # ProxyError is a TransportError, so code that only knows about the
        # connection breaking still catches it.
        assert issubclass(ProxyError, TransportError)


class _Server:
    """A loopback server that shuts down, and lets go of its clients, on the way out.

    Cancelling the handlers is the part that matters. Several of these pump
    bytes until the far end goes away, and a test that ends by giving up on a
    connection rather than closing it would otherwise leave one running.
    """

    def __init__(self, handler):
        self._handler = handler
        self._server = None
        self._tasks: set[asyncio.Task] = set()

    async def __aenter__(self) -> int:
        async def wrapped(reader, writer):
            task = asyncio.current_task()
            self._tasks.add(task)
            try:
                await self._handler(reader, writer)
            except (OSError, asyncio.IncompleteReadError):
                pass
            finally:
                self._tasks.discard(task)
                writer.close()

        self._server = await asyncio.start_server(wrapped, "127.0.0.1", 0)
        return int(self._server.sockets[0].getsockname()[1])

    async def __aexit__(self, *_) -> None:
        for task in list(self._tasks):
            task.cancel()
        self._server.close()
        await self._server.wait_closed()


def _destination() -> _Server:
    """Something for a tunnel to actually reach: it echoes whatever arrives."""

    async def handle(reader, writer):
        while data := await reader.read(4096):
            writer.write(data)
            await writer.drain()

    return _Server(handle)


def _socks5_server(
    *,
    username: str | None = None,
    password: str | None = None,
    refuse: int = 0,
    no_method: bool = False,
    seen: list[bytes] | None = None,
) -> _Server:
    """Enough of RFC 1928 to answer one client, and to get it wrong on demand."""

    async def handle(reader, writer):
        version, count = await reader.readexactly(2)
        offered = await reader.readexactly(count)
        assert version == 5

        if no_method:
            writer.write(b"\x05\xff")
            await writer.drain()
            return
        if username is not None:
            writer.write(b"\x05\x02")
            await writer.drain()
            assert 0x02 in offered
            await reader.readexactly(1)
            user = await reader.readexactly((await reader.readexactly(1))[0])
            given = await reader.readexactly((await reader.readexactly(1))[0])
            ok = user.decode() == username and given.decode() == (password or "")
            writer.write(b"\x01" + (b"\x00" if ok else b"\x01"))
            await writer.drain()
            if not ok:
                return
        else:
            writer.write(b"\x05\x00")
            await writer.drain()

        head = await reader.readexactly(4)
        assert head[:3] == b"\x05\x01\x00"
        kind = head[3:4]
        if kind == b"\x01":
            where = await reader.readexactly(4)
        elif kind == b"\x04":
            where = await reader.readexactly(16)
        else:
            where = await reader.readexactly((await reader.readexactly(1))[0])
        port = int.from_bytes(await reader.readexactly(2), "big")
        if seen is not None:
            seen.append(kind + (bytes((len(where),)) if kind == b"\x03" else b"") + where)

        if refuse:
            writer.write(b"\x05" + bytes((refuse,)) + b"\x00\x01" + b"\x00" * 6)
            await writer.drain()
            return

        writer.write(b"\x05\x00\x00\x01" + b"\x00" * 6)
        await writer.drain()
        await _splice(reader, writer, ".".join(str(part) for part in where), port)

    return _Server(handle)


def _http_server(
    *,
    status: bytes = b"HTTP/1.1 200 Connection established",
    seen: list[bytes] | None = None,
) -> _Server:
    """One CONNECT, answered with whatever status the test asked for."""

    async def handle(reader, writer):
        head = await reader.readuntil(b"\r\n\r\n")
        if seen is not None:
            seen.append(head)
        writer.write(status + b"\r\n\r\n")
        await writer.drain()
        if not status.split(b" ")[1].startswith(b"2"):
            return
        where = head.split(b" ")[1].decode()
        host, _, port = where.rpartition(":")
        await _splice(reader, writer, host, int(port))

    return _Server(handle)


async def _splice(reader, writer, host: str, port: int) -> None:
    """Join the client to the destination, which is what a tunnel is."""
    far_reader, far_writer = await asyncio.open_connection(host, port)

    async def pump(source, sink):
        try:
            while data := await source.read(4096):
                sink.write(data)
                await sink.drain()
        except OSError:
            pass
        finally:
            sink.close()

    try:
        await asyncio.gather(pump(reader, far_writer), pump(far_reader, writer))
    finally:
        far_writer.close()


async def _round_trip(proxy: Proxy, target: int) -> bytes:
    reader, writer = await open_through(proxy, "127.0.0.1", target, timeout=5)
    try:
        writer.write(PAYLOAD)
        await writer.drain()
        return await reader.readexactly(len(PAYLOAD))
    finally:
        writer.close()


async def _nothing(reader, writer) -> None:
    writer.close()
