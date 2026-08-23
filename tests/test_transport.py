"""Framing and the TCP connection.

The codecs are driven through a StreamReader fed by hand, and the connection is
driven against a loopback server. Nothing here leaves the machine.
"""

from __future__ import annotations

import asyncio
from zlib import crc32

import pytest

from mtproto_server import closing
from sunnygram.errors import (
    MalformedFrame,
    TransportClosed,
    TransportError,
    TransportRejected,
)
from sunnygram.transport import (
    MAX_PACKET_SIZE,
    Abridged,
    Full,
    Intermediate,
    PaddedIntermediate,
    TCPTransport,
)

PAYLOAD = b"sunnygram payload\x00\x00\x00"


def fed(data: bytes) -> asyncio.StreamReader:
    reader = asyncio.StreamReader()
    reader.feed_data(data)
    reader.feed_eof()
    return reader


class TestIntermediate:
    async def test_round_trip(self):
        codec = Intermediate()
        assert await codec.decode(fed(codec.encode(PAYLOAD))) == PAYLOAD

    async def test_frame_layout(self):
        assert Intermediate().encode(b"\x01\x02\x03\x04") == (
            b"\x04\x00\x00\x00\x01\x02\x03\x04"
        )

    def test_announces_itself_on_connect(self):
        assert Intermediate.init == b"\xee\xee\xee\xee"

    async def test_back_to_back_packets(self):
        codec = Intermediate()
        reader = fed(codec.encode(PAYLOAD) + codec.encode(b"second\x00\x00"))
        assert await codec.decode(reader) == PAYLOAD
        assert await codec.decode(reader) == b"second\x00\x00"

    async def test_four_byte_packet_is_an_error_code(self):
        payload = b"\x04\x00\x00\x00" + (-404).to_bytes(4, "little", signed=True)
        with pytest.raises(TransportRejected) as info:
            await Intermediate().decode(fed(payload))
        assert info.value.code == -404
        assert "authorization key" in str(info.value)

    async def test_negative_length_is_an_error_code(self):
        payload = (-444).to_bytes(4, "little", signed=True)
        with pytest.raises(TransportRejected) as info:
            await Intermediate().decode(fed(payload))
        assert info.value.code == -444

    async def test_absurd_length_is_refused_before_reading(self):
        payload = (MAX_PACKET_SIZE + 4).to_bytes(4, "little")
        with pytest.raises(MalformedFrame):
            await Intermediate().decode(fed(payload))

    async def test_unaligned_length_is_refused(self):
        with pytest.raises(MalformedFrame):
            await Intermediate().decode(fed((13).to_bytes(4, "little")))

    async def test_truncated_packet(self):
        codec = Intermediate()
        with pytest.raises(TransportClosed):
            await codec.decode(fed(codec.encode(PAYLOAD)[:-4]))

    async def test_nothing_to_read(self):
        with pytest.raises(TransportClosed):
            await Intermediate().decode(fed(b""))

    def test_unaligned_payload_is_refused(self):
        with pytest.raises(MalformedFrame):
            Intermediate().encode(b"three")


class TestFull:
    async def test_round_trip(self):
        assert await Full().decode(fed(Full().encode(PAYLOAD))) == PAYLOAD

    def test_frame_layout(self):
        frame = Full().encode(PAYLOAD)
        assert len(frame) == len(PAYLOAD) + 12
        assert int.from_bytes(frame[:4], "little") == len(PAYLOAD) + 12
        assert int.from_bytes(frame[4:8], "little") == 0
        assert int.from_bytes(frame[-4:], "little") == crc32(frame[:-4])

    def test_sequence_numbers_count_packets(self):
        codec = Full()
        assert int.from_bytes(codec.encode(PAYLOAD)[4:8], "little") == 0
        assert int.from_bytes(codec.encode(PAYLOAD)[4:8], "little") == 1

    async def test_reads_a_run_of_packets(self):
        sender, receiver = Full(), Full()
        reader = fed(b"".join(sender.encode(PAYLOAD) for _ in range(3)))
        for _ in range(3):
            assert await receiver.decode(reader) == PAYLOAD

    async def test_out_of_order_packet_is_refused(self):
        sender = Full()
        sender.encode(PAYLOAD)
        frame = sender.encode(PAYLOAD)
        with pytest.raises(MalformedFrame, match="expected packet 0"):
            await Full().decode(fed(frame))

    async def test_corrupted_payload_is_caught(self):
        frame = bytearray(Full().encode(PAYLOAD))
        frame[10] ^= 0xFF
        with pytest.raises(MalformedFrame, match="checksum"):
            await Full().decode(fed(bytes(frame)))

    async def test_corrupted_checksum_is_caught(self):
        frame = bytearray(Full().encode(PAYLOAD))
        frame[-1] ^= 0xFF
        with pytest.raises(MalformedFrame, match="checksum"):
            await Full().decode(fed(bytes(frame)))

    async def test_length_below_a_whole_frame_is_refused(self):
        with pytest.raises(MalformedFrame):
            await Full().decode(fed((8).to_bytes(4, "little")))

    async def test_error_code_instead_of_a_frame(self):
        with pytest.raises(TransportRejected):
            await Full().decode(fed((-429).to_bytes(4, "little", signed=True)))

    def test_sends_no_init_bytes(self):
        assert Full.init == b""


class TestAbridged:
    async def test_round_trip(self):
        codec = Abridged()
        assert await codec.decode(fed(codec.encode(PAYLOAD))) == PAYLOAD

    def test_short_packets_spend_one_byte(self):
        frame = Abridged().encode(b"\x01\x02\x03\x04")
        assert frame == b"\x01\x01\x02\x03\x04"

    def test_long_packets_spend_four(self):
        payload = b"\x00" * 508
        frame = Abridged().encode(payload)
        assert frame[:4] == b"\x7f" + (127).to_bytes(3, "little")
        assert frame[4:] == payload

    async def test_the_long_form_reads_back(self):
        codec = Abridged()
        payload = b"\x00" * 2048
        assert await codec.decode(fed(codec.encode(payload))) == payload

    async def test_back_to_back_packets(self):
        codec = Abridged()
        reader = fed(codec.encode(PAYLOAD) + codec.encode(b"second\x00\x00"))
        assert await codec.decode(reader) == PAYLOAD
        assert await codec.decode(reader) == b"second\x00\x00"

    async def test_one_word_packet_is_an_error_code(self):
        with pytest.raises(TransportRejected) as info:
            await Abridged().decode(
                fed(b"\x01" + (-404).to_bytes(4, "little", signed=True))
            )
        assert info.value.code == -404

    async def test_absurd_length_is_refused_before_reading(self):
        words = MAX_PACKET_SIZE // 4 + 1
        with pytest.raises(MalformedFrame):
            await Abridged().decode(fed(b"\x7f" + words.to_bytes(3, "little")))

    def test_unaligned_payload_is_refused(self):
        with pytest.raises(MalformedFrame):
            Abridged().encode(b"three")

    def test_announces_itself_with_one_byte(self):
        assert Abridged.init == b"\xef"
        assert Abridged.tag == b"\xef\xef\xef\xef"


class TestPaddedIntermediate:
    async def test_round_trip(self):
        codec = PaddedIntermediate()
        for _ in range(32):
            assert await codec.decode(fed(codec.encode(PAYLOAD))) == PAYLOAD

    def test_padding_is_at_most_three_bytes(self):
        codec = PaddedIntermediate()
        lengths = {len(codec.encode(PAYLOAD)) for _ in range(64)}
        assert lengths <= {len(PAYLOAD) + 4 + n for n in range(4)}

    def test_the_length_counts_the_padding(self):
        frame = PaddedIntermediate().encode(PAYLOAD)
        assert int.from_bytes(frame[:4], "little") == len(frame) - 4

    def test_padding_actually_happens(self):
        # Not a fixed number of bytes, or a watcher reads the lengths anyway.
        codec = PaddedIntermediate()
        assert len({len(codec.encode(PAYLOAD)) for _ in range(200)}) > 1

    async def test_back_to_back_packets(self):
        codec = PaddedIntermediate()
        reader = fed(codec.encode(PAYLOAD) + codec.encode(b"second\x00\x00"))
        assert await codec.decode(reader) == PAYLOAD
        assert await codec.decode(reader) == b"second\x00\x00"

    async def test_four_byte_packet_is_an_error_code(self):
        payload = b"\x04\x00\x00\x00" + (-429).to_bytes(4, "little", signed=True)
        with pytest.raises(TransportRejected) as info:
            await PaddedIntermediate().decode(fed(payload))
        assert info.value.code == -429

    async def test_negative_length_is_an_error_code(self):
        with pytest.raises(TransportRejected):
            await PaddedIntermediate().decode(
                fed((-444).to_bytes(4, "little", signed=True))
            )

    async def test_absurd_length_is_refused_before_reading(self):
        payload = (MAX_PACKET_SIZE + 4).to_bytes(4, "little")
        with pytest.raises(MalformedFrame):
            await PaddedIntermediate().decode(fed(payload))

    async def test_an_unaligned_length_is_ordinary_here(self):
        # The whole difference from intermediate: a frame length that is not a
        # multiple of four is padding rather than corruption.
        frame = (len(PAYLOAD) + 3).to_bytes(4, "little") + PAYLOAD + b"\x01\x02\x03"
        assert await PaddedIntermediate().decode(fed(frame)) == PAYLOAD

    def test_announces_itself_on_connect(self):
        assert PaddedIntermediate.init == b"\xdd\xdd\xdd\xdd"
        assert PaddedIntermediate.tag == b"\xdd\xdd\xdd\xdd"


class TestTCPTransport:
    async def test_round_trips_over_a_socket(self):
        seen: list[bytes] = []

        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            codec = Intermediate()
            seen.append(await reader.readexactly(4))
            seen.append(await codec.decode(reader))
            writer.write(codec.encode(b"pong\x00\x00\x00\x00"))
            await writer.drain()

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            transport = TCPTransport()
            await transport.connect("127.0.0.1", port)
            async with transport:
                assert transport.connected
                await transport.send(PAYLOAD)
                assert await transport.receive() == b"pong\x00\x00\x00\x00"
            assert not transport.connected

        assert seen == [b"\xee\xee\xee\xee", PAYLOAD]

    async def test_a_dropped_peer_shows_up_as_closed(self):
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            writer.close()

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            transport = TCPTransport()
            await transport.connect("127.0.0.1", port)
            async with transport:
                with pytest.raises(TransportClosed):
                    await transport.receive()

    async def test_refused_connection_is_reported(self):
        server = await asyncio.start_server(handle_nothing, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        server.close()
        await server.wait_closed()
        with pytest.raises(TransportError):
            await TCPTransport(timeout=5).connect("127.0.0.1", port)

    async def test_using_it_before_connecting(self):
        transport = TCPTransport()
        assert not transport.connected
        with pytest.raises(TransportClosed):
            await transport.send(PAYLOAD)
        with pytest.raises(TransportClosed):
            await transport.receive()

    async def test_closing_twice_is_harmless(self):
        transport = TCPTransport()
        await transport.close()
        await transport.close()

    async def test_full_codec_over_a_socket(self):
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            codec = Full()
            writer.write(codec.encode(await codec.decode(reader)))
            await writer.drain()

        server = await asyncio.start_server(closing(handle), "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        async with server:
            transport = TCPTransport(Full())
            await transport.connect("127.0.0.1", port)
            async with transport:
                await transport.send(PAYLOAD)
                assert await transport.receive() == PAYLOAD


async def handle_nothing(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    writer.close()
