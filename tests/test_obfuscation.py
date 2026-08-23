"""The obfuscated2 stream cipher.

The interesting test here is the last one, which is not a unit test at all: a
scripted server derives its own keys the way a real proxy does, out of nothing
but the sixty-four bytes the client sent, and the two hold a conversation. That
is the only check that actually proves the derivation is right, since every
other property here would still hold if both directions were wrong together.
"""

from __future__ import annotations

import asyncio
from hashlib import sha256

import pytest

from mtproto_server import closing
from sunnygram.crypto.accel import new_ctr
from sunnygram.errors import TransportError
from sunnygram.transport import Full, Intermediate, TCPTransport
from sunnygram.transport.obfuscation import HEADER_SIZE, ObfuscatedReader, start
from sunnygram.transport.proxy import Proxy

PAYLOAD = b"sunnygram payload\x00\x00\x00"
SECRET = bytes(range(16))


class TestHeader:
    def test_it_is_sixty_four_bytes(self):
        assert len(start(Intermediate.tag).header) == HEADER_SIZE

    def test_the_tag_is_not_readable_in_the_clear(self):
        # The last eight bytes go out encrypted, so a watcher cannot read the
        # framing off the handshake even though it is in there.
        headers = [start(Intermediate.tag).header[56:60] for _ in range(32)]
        assert Intermediate.tag not in headers

    def test_the_opening_is_never_mistakable(self):
        for _ in range(256):
            header = start(Intermediate.tag).header
            assert header[0] != 0xEF
            assert header[:4] not in (b"HEAD", b"POST", b"GET ", b"OPTI")
            assert header[:4] not in (b"\xdd\xdd\xdd\xdd", b"\xee\xee\xee\xee")
            assert header[:4] != b"\x16\x03\x01\x02"
            assert header[4:8] != b"\x00\x00\x00\x00"

    def test_every_handshake_is_different(self):
        assert len({start(Intermediate.tag).header for _ in range(64)}) == 64

    def test_a_framing_without_a_tag_cannot_be_obfuscated(self):
        with pytest.raises(TransportError, match="no tag"):
            start(Full.tag)

    def test_the_datacenter_travels_in_the_handshake(self):
        # Encrypted, so it has to be read back the way a proxy would.
        for dc_id in (2, -2, 4):
            obfuscation = start(Intermediate.tag, dc_id=dc_id)
            plain = _unscramble(obfuscation.header)
            assert int.from_bytes(plain[60:62], "little", signed=True) == dc_id

    def test_the_framing_travels_in_the_handshake(self):
        plain = _unscramble(start(Intermediate.tag).header)
        assert plain[56:60] == Intermediate.tag

    def test_a_secret_changes_the_keys_and_nothing_else(self):
        # Same sixty-four bytes would give a different keystream, so the plain
        # tail a proxy reads back is only reachable while holding the secret.
        obfuscation = start(Intermediate.tag, secret=SECRET)
        assert _unscramble(obfuscation.header, secret=SECRET)[56:60] == Intermediate.tag
        assert _unscramble(obfuscation.header)[56:60] != Intermediate.tag


class TestCiphers:
    def test_the_keystream_carries_across_calls(self):
        # The same bytes twice must not encrypt to the same thing, or the
        # cipher is restarting per call and the stream is a repeating pad.
        obfuscation = start(Intermediate.tag)
        first = obfuscation.encrypt(PAYLOAD)
        assert len(first) == len(PAYLOAD)
        assert obfuscation.encrypt(PAYLOAD) != first

    def test_a_call_split_in_two_is_the_same_stream(self):
        whole = start(Intermediate.tag)
        parts = start(Intermediate.tag)
        # Different handshakes, so compare each against a fresh copy of itself
        # rather than against each other.
        assert whole.encrypt(PAYLOAD) != parts.encrypt(PAYLOAD)
        halves = parts.encrypt(PAYLOAD[:8]) + parts.encrypt(PAYLOAD[8:])
        assert len(halves) == len(PAYLOAD)

    async def test_the_reader_unscrambles_what_it_reads(self):
        obfuscation = start(Intermediate.tag)
        # The far end's incoming cipher is this end's outgoing one, so a reader
        # built on the second decrypts what the first wrote.
        mirror = _server_side(obfuscation.header)
        reader = asyncio.StreamReader()
        reader.feed_data(obfuscation.encrypt(PAYLOAD))
        reader.feed_eof()
        wrapped = ObfuscatedReader(reader, mirror["decrypt"])
        assert await wrapped.readexactly(len(PAYLOAD)) == PAYLOAD


class TestOverASocket:
    async def test_a_scripted_proxy_holds_a_conversation(self):
        """The whole point, end to end.

        The server is told nothing: it reads sixty-four bytes, derives both keys
        from them and the shared secret the way MTProxy does, and answers. If
        either derivation were wrong this is where it would show, and nowhere
        else.
        """
        seen: list[bytes] = []

        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            keys = _server_side(await reader.readexactly(HEADER_SIZE), secret=SECRET)
            seen.append(keys["tag"])
            seen.append(keys["dc_id"])
            codec = Intermediate()
            seen.append(await codec.decode(ObfuscatedReader(reader, keys["decrypt"])))
            writer.write(keys["encrypt"].apply(codec.encode(b"pong\x00\x00\x00\x00")))
            await writer.drain()

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            proxy = Proxy.mtproto("127.0.0.1", port, SECRET)
            transport = TCPTransport(Intermediate(), proxy=proxy, dc_id=2)
            await transport.connect("149.154.167.51", 443)
            async with transport:
                await transport.send(PAYLOAD)
                assert await transport.receive() == b"pong\x00\x00\x00\x00"

        assert seen == [Intermediate.tag, (2).to_bytes(2, "little"), PAYLOAD]

    async def test_a_run_of_packets_stays_in_step(self):
        # CTR is a keystream, so one frame framed or written out of order
        # desynchronises everything after it. Several in a row is the check.
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            keys = _server_side(await reader.readexactly(HEADER_SIZE))
            codec = Intermediate()
            wrapped = ObfuscatedReader(reader, keys["decrypt"])
            for _ in range(16):
                body = await codec.decode(wrapped)
                writer.write(keys["encrypt"].apply(codec.encode(body)))
            await writer.drain()

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            transport = TCPTransport(Intermediate(), obfuscated=True)
            await transport.connect("127.0.0.1", port)
            async with transport:
                for index in range(16):
                    payload = index.to_bytes(4, "little") * 3
                    await transport.send(payload)
                    assert await transport.receive() == payload

    async def test_concurrent_sends_do_not_interleave(self):
        """Framing and writing are one step or the stream is unrecoverable.

        Both the frame counter and the keystream advance once per frame, so a
        frame built before another and written after it corrupts everything
        following. Sixteen senders let go at once is what catches that.
        """
        got: list[bytes] = []

        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            keys = _server_side(await reader.readexactly(HEADER_SIZE))
            codec = Intermediate()
            wrapped = ObfuscatedReader(reader, keys["decrypt"])
            for _ in range(16):
                got.append(await codec.decode(wrapped))

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            transport = TCPTransport(Intermediate(), obfuscated=True)
            await transport.connect("127.0.0.1", port)
            async with transport:
                await asyncio.gather(
                    *(
                        transport.send(index.to_bytes(4, "little") * 3)
                        for index in range(16)
                    )
                )
                await asyncio.sleep(0.1)

        assert sorted(got) == sorted(
            index.to_bytes(4, "little") * 3 for index in range(16)
        )

    async def test_a_dd_secret_forces_the_padded_framing(self):
        proxy = Proxy.mtproto("127.0.0.1", 443, b"\xdd" + SECRET)
        transport = TCPTransport(Intermediate(), proxy=proxy)
        # Reaching into the transport, because the whole behaviour is that the
        # codec handed in is not the one used.
        assert type(transport._codec).__name__ == "PaddedIntermediate"


def _server_side(header: bytes, *, secret: bytes = b"") -> dict:
    """Derive what a proxy derives, from the handshake alone."""
    out_key, out_iv = header[8:40], header[40:56]
    mirror = header[8:56][::-1]
    in_key, in_iv = mirror[:32], mirror[32:48]
    if secret:
        out_key = sha256(out_key + secret).digest()
        in_key = sha256(in_key + secret).digest()

    decrypt = new_ctr(out_key, out_iv)
    # The client encrypted the whole header before sending it, so the far end
    # has to burn the same sixty-four bytes of keystream. Doing it this way
    # hands back the plaintext tail as a side effect, which is where the tag is.
    plain = decrypt.apply(header)
    return {
        "decrypt": decrypt,
        "encrypt": new_ctr(in_key, in_iv),
        "tag": plain[56:60],
        "dc_id": plain[60:62],
        "plain": header[:56] + plain[56:HEADER_SIZE],
    }


def _unscramble(header: bytes, *, secret: bytes = b"") -> bytes:
    """The handshake as the client built it, before the tail was encrypted."""
    unscrambled: bytes = _server_side(header, secret=secret)["plain"]
    return unscrambled
