"""Moving files, without a network.

The scripted server here keeps the parts it is sent and hands back slices of
what it holds, which is enough to prove the parts of this that are ours: that a
file is cut up the way Telegram insists on, that the pieces go out several at a
time and come back into the right places, that a file living in another
datacenter is fetched from there without the account moving, and that the two
things which routinely go wrong on a real download, a stale file reference and a
file that has been moved, are recovered from rather than raised over.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import FileTooLarge, SunnygramError, UploadRefused
from sunnygram.files import (
    FileSource,
    download_file,
    locate,
    stream_file,
    upload_file,
)
from sunnygram.files.parts import check_download_chunk, check_upload_part, in_parallel
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
HOME = 2
FAR = 4


def a_document(
    id: int = 900,
    *,
    size: int = 1000,
    dc_id: int = HOME,
    reference: bytes = b"ref",
    name: str | None = "notes.txt",
) -> types.Document:
    attributes: list[Any] = []
    if name is not None:
        attributes.append(types.DocumentAttributeFilename(file_name=name))
    return types.Document(
        id=id,
        access_hash=77,
        file_reference=reference,
        date=1700000000,
        mime_type="text/plain",
        size=size,
        dc_id=dc_id,
        attributes=attributes,
    )


def a_photo(id: int = 500, *, dc_id: int = HOME) -> types.Photo:
    return types.Photo(
        id=id,
        access_hash=88,
        file_reference=b"pref",
        date=1700000000,
        sizes=[
            types.PhotoStrippedSize(type="i", bytes=b"\x01\x02"),
            types.PhotoSize(type="m", w=320, h=320, size=2000),
            types.PhotoSize(type="x", w=800, h=800, size=9000),
        ],
        dc_id=dc_id,
    )


class Datacenter:
    """What one datacenter holds, shared by every connection into it.

    A pool means several sockets to the same place, and they are the same place:
    a part sent down one and a part sent down another belong to the same file.
    So the state lives here and the servers below are only mouths.
    """

    def __init__(self, dc_id: int) -> None:
        self.dc_id = dc_id
        self.parts: dict[int, dict[int, bytes]] = {}
        self.total_parts: dict[int, int] = {}
        self.content = b""
        self.asked: list[Any] = []
        self.refuse_part: int | None = None
        self.stale_reference: bytes | None = None
        self.moved_to: int | None = None
        self.imported = False
        self.sessions: set[int] = set()

    def uploaded(self, file_id: int) -> bytes:
        held = self.parts[file_id]
        return b"".join(held[number] for number in sorted(held))


class FileServer(ScriptedServer):
    """One connection's worth of a datacenter."""

    def __init__(self, wire: Wire, session: Any, dc: Datacenter) -> None:
        super().__init__(wire, session)
        self.dc = dc
        # Every connection is its own MTProto session, which is what makes a
        # pool safe: the ids and sequence numbers of one never touch another's.
        dc.sessions.add(session.session_id)

    @property
    def content(self) -> bytes:
        return self.dc.content

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            self.dc.asked.append(query)
            if isinstance(query, functions.upload.SaveFilePart):
                await self._save(request.msg_id, query.file_id, query.file_part, query.bytes)
            elif isinstance(query, functions.upload.SaveBigFilePart):
                self.dc.total_parts[query.file_id] = query.file_total_parts
                await self._save(request.msg_id, query.file_id, query.file_part, query.bytes)
            elif isinstance(query, functions.upload.GetFile):
                await self._serve(request.msg_id, query)
            elif isinstance(query, functions.auth.ExportAuthorization):
                await self.answer(
                    request.msg_id,
                    types.auth.ExportedAuthorization(id=1, bytes=b"exported"),
                )
            elif isinstance(query, functions.auth.ImportAuthorization):
                self.dc.imported = True
                await self.answer(
                    request.msg_id,
                    types.auth.Authorization(user=types.UserEmpty(id=ME)),
                )
            else:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")

    async def _save(self, msg_id: int, file_id: int, part: int, data: bytes) -> None:
        if self.dc.refuse_part is not None and part == self.dc.refuse_part:
            await self.answer(msg_id, False)
            return
        self.dc.parts.setdefault(file_id, {})[part] = data
        await self.answer(msg_id, True)

    async def _serve(self, msg_id: int, query: Any) -> None:
        reference = getattr(query.location, "file_reference", b"")
        if self.dc.stale_reference is not None and reference == self.dc.stale_reference:
            await self.refuse(msg_id, 400, "FILE_REFERENCE_EXPIRED")
            return
        if self.dc.moved_to is not None:
            await self.refuse(msg_id, 303, f"FILE_MIGRATE_{self.dc.moved_to}")
            return
        piece = self.dc.content[query.offset : query.offset + query.limit]
        await self.answer(
            msg_id,
            types.upload.File(
                type=types.storage.FileUnknown(), mtime=0, bytes=piece
            ),
        )


class Network:
    """Every datacenter a test reaches, answering on every socket into it.

    A connection pool means a datacenter is reached down several wires at once,
    and every one of them has to answer or the transfer simply waits. So a
    server is attached as each connection is built rather than once per
    datacenter.
    """

    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []
        self.centres: dict[int, Datacenter] = {}
        self.serving: list[asyncio.Task[None]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire

    def dc(self, dc_id: int) -> Datacenter:
        return self.centres.setdefault(dc_id, Datacenter(dc_id))

    def answer_on(self, dc_id: int, connection: Any) -> FileServer:
        """Put a server on the wire the given connection just took."""
        server = FileServer(self.wires[-1][1], connection.session, self.dc(dc_id))
        self.serving.append(asyncio.create_task(server.serve()))
        return server

    @property
    def sockets(self) -> int:
        return len(self.wires)


class Served(Invoker):
    """An invoker whose every connection finds somebody answering.

    Wrapping _open is what makes that exact: the wire a connection was handed
    is the one that was made for it a moment earlier, so there is no guessing
    about which socket belongs to which session.
    """

    def __init__(self, *args: Any, network: Network, **options: Any) -> None:
        super().__init__(*args, **options)
        self._network = network

    async def _open(self, dc_id: int, *, updates: bool = False) -> Any:
        connection = await super()._open(dc_id, updates=updates)
        self._network.answer_on(dc_id, connection)
        return connection


@asynccontextmanager
async def live(
    *, content: bytes = b"", bulk_connections: int = 4
) -> AsyncIterator[tuple[Invoker, Network]]:
    """A session at home, with every datacenter it reaches answering."""
    session = SessionState(dc_id=HOME, user_id=ME)
    session.set_auth_key(HOME, AUTH_KEY)
    session.set_auth_key(FAR, AUTH_KEY)
    network = Network()
    network.dc(HOME).content = content
    network.dc(FAR).content = content
    invoker = Served(
        MemoryStorage(session),
        network=network,
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
        bulk_connections=bulk_connections,
    )
    await invoker.start()
    try:
        yield invoker, network
    finally:
        for task in network.serving:
            task.cancel()
        await asyncio.gather(*network.serving, return_exceptions=True)
        await invoker.close()


class TestTheRules:
    """The arithmetic Telegram insists on, refused here rather than there."""

    @pytest.mark.parametrize("size", [512 * 1024, 256 * 1024, 128 * 1024, 1024])
    def test_a_good_upload_part_is_allowed(self, size):
        assert check_upload_part(size) == size

    @pytest.mark.parametrize("size", [1000, 0, -1024, 3 * 1024, 1024 * 1024])
    def test_a_bad_upload_part_is_refused(self, size):
        with pytest.raises(ValueError):
            check_upload_part(size)

    @pytest.mark.parametrize("size", [512 * 1024, 1024 * 1024, 4096])
    def test_a_good_download_chunk_is_allowed(self, size):
        assert check_download_chunk(size) == size

    @pytest.mark.parametrize("size", [1000, 0, 5000, 3 * 4096])
    def test_a_bad_download_chunk_is_refused(self, size):
        with pytest.raises(ValueError):
            check_download_chunk(size)


class TestFindingTheFile:
    def test_a_document_names_itself(self):
        found = locate(a_document())
        assert isinstance(found.location, types.InputDocumentFileLocation)
        assert found.location.id == 900
        assert found.location.file_reference == b"ref"
        assert found.dc_id == HOME
        assert found.size == 1000
        assert found.name == "notes.txt"

    def test_a_photo_takes_its_largest_size(self):
        found = locate(a_photo())
        assert isinstance(found.location, types.InputPhotoFileLocation)
        assert found.location.thumb_size == "x"
        assert found.size == 9000

    def test_a_photo_size_can_be_asked_for_by_name(self):
        assert locate(a_photo(), thumb="m").size == 2000

    def test_a_size_that_is_not_there_says_which_are(self):
        with pytest.raises(SunnygramError, match="i, m, x"):
            locate(a_photo(), thumb="w")

    def test_a_stripped_size_is_not_offered_as_a_download(self):
        # It is a couple of hundred bytes carried inline, not a file the
        # server will serve.
        photo = types.Photo(
            id=1, access_hash=1, file_reference=b"", date=0,
            sizes=[types.PhotoStrippedSize(type="i", bytes=b"\x01")], dc_id=HOME,
        )
        with pytest.raises(SunnygramError, match="no size that can be downloaded"):
            locate(photo)

    def test_media_and_messages_are_unwrapped(self):
        media = types.MessageMediaDocument(document=a_document())
        assert locate(media).location.id == 900
        message = types.Message(
            id=1, peer_id=types.PeerUser(user_id=ME), date=0, message="", media=media
        )
        assert locate(message).location.id == 900

    def test_a_message_with_no_file_says_so(self):
        message = types.Message(
            id=1, peer_id=types.PeerUser(user_id=ME), date=0, message="hi"
        )
        with pytest.raises(SunnygramError, match="carries no file"):
            locate(message)

    def test_a_progressive_photo_is_as_big_as_its_last_prefix(self):
        photo = types.Photo(
            id=1, access_hash=1, file_reference=b"", date=0,
            sizes=[types.PhotoSizeProgressive(type="y", w=1, h=1, sizes=[10, 200, 3000])],
            dc_id=HOME,
        )
        assert locate(photo).size == 3000


class TestUploading:
    async def test_a_small_file_arrives_whole(self):
        data = os.urandom(3000)
        async with live() as (invoker, network):
            handle = await upload_file(invoker, data, name="x.bin", part_size=1024)
            assert isinstance(handle, types.InputFile)
            assert handle.parts == 3
            assert handle.md5_checksum == hashlib.md5(data).hexdigest()
            assert network.dc(HOME).uploaded(handle.id) == data

    async def test_a_big_file_goes_the_other_way(self, monkeypatch):
        # The threshold is moved rather than the file being made huge: what is
        # under test is the branch, and encrypting eleven megabytes through the
        # pure Python cipher would take longer than the test is worth.
        monkeypatch.setattr("sunnygram.files.upload.BIG_FILE", 2048)
        data = os.urandom(5000)
        async with live() as (invoker, network):
            handle = await upload_file(invoker, data, name="big.bin", part_size=1024)
            assert isinstance(handle, types.InputFileBig)
            assert not hasattr(handle, "md5_checksum")
            assert network.dc(HOME).uploaded(handle.id) == data
            # Every part of a big file declares the total, which is what lets
            # the server assemble it without being told the length first.
            assert network.dc(HOME).total_parts[handle.id] == handle.parts

    async def test_a_file_on_disk_is_read_from_there(self, tmp_path):
        path = tmp_path / "notes.txt"
        data = os.urandom(5000)
        path.write_bytes(data)
        async with live() as (invoker, network):
            handle = await upload_file(invoker, path, part_size=1024)
            assert handle.name == "notes.txt"
            assert network.dc(HOME).uploaded(handle.id) == data

    async def test_the_parts_are_numbered_from_zero_and_in_order(self):
        async with live() as (invoker, network):
            handle = await upload_file(invoker, os.urandom(4096), part_size=1024)
            numbers = sorted(network.dc(HOME).parts[handle.id])
            assert numbers == [0, 1, 2, 3]

    async def test_progress_reaches_the_end(self):
        seen: list[tuple[int, int]] = []
        async with live() as (invoker, network):
            await upload_file(
                invoker, os.urandom(3000), part_size=1024, progress=lambda a, b: seen.append((a, b))
            )
        assert seen[-1] == (3000, 3000)
        assert all(total == 3000 for _, total in seen)

    async def test_an_empty_file_is_refused_rather_than_sent(self):
        # Telegram has nowhere to put one, so the refusal belongs here.
        async with live() as (invoker, network):
            with pytest.raises(ValueError, match="nothing in this file"):
                await upload_file(invoker, b"", name="empty")
            assert network.dc(HOME).asked == []

    async def test_an_empty_file_on_disk_leaves_no_handle_open(self, tmp_path):
        path = tmp_path / "empty.bin"
        path.write_bytes(b"")
        async with live() as (invoker, network):
            with pytest.raises(ValueError):
                await upload_file(invoker, path)
        # Windows will not remove a file that is still open, so this is the
        # check that the refusal above closed what it opened.
        path.unlink()

    async def test_a_refused_part_stops_the_upload(self):
        async with live() as (invoker, network):
            network.dc(HOME).refuse_part = 2
            with pytest.raises(UploadRefused) as refused:
                await upload_file(invoker, os.urandom(8192), part_size=1024, workers=1)
            assert refused.value.part == 2

    async def test_a_part_size_the_server_would_refuse_never_leaves(self):
        async with live() as (invoker, network):
            with pytest.raises(ValueError):
                await upload_file(invoker, b"x", part_size=1000)
            assert network.dc(HOME).asked == []


class TestDownloading:
    async def test_a_file_comes_back_whole(self):
        data = os.urandom(20000)
        async with live(content=data) as (invoker, network):
            got = await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096
            )
            assert got == data

    async def test_the_pieces_land_in_the_right_places(self):
        # Several workers, so the pieces come back out of order. Each carries
        # its own offset, which is what makes that harmless.
        data = bytes(range(256)) * 200
        async with live(content=data) as (invoker, network):
            got = await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=4
            )
            assert got == data

    async def test_it_can_go_straight_to_disk(self, tmp_path):
        data = os.urandom(30000)
        into = tmp_path / "out.bin"
        async with live(content=data) as (invoker, network):
            where = await download_file(
                invoker, a_document(size=len(data)), into=into, chunk_size=4096
            )
            assert where == into
            assert into.read_bytes() == data

    async def test_a_file_of_unknown_length_is_read_to_the_end(self):
        data = os.urandom(10000)
        async with live(content=data) as (invoker, network):
            source = FileSource(
                location=locate(a_document()).location, dc_id=HOME, size=0
            )
            assert await download_file(invoker, source, chunk_size=4096) == data

    async def test_progress_reaches_the_end(self):
        seen: list[tuple[int, int]] = []
        data = os.urandom(12288)
        async with live(content=data) as (invoker, network):
            await download_file(
                invoker,
                a_document(size=len(data)),
                chunk_size=4096,
                workers=1,
                progress=lambda a, b: seen.append((a, b)),
            )
        assert seen[-1] == (12288, 12288)

    async def test_something_too_big_is_refused_before_it_is_fetched(self):
        async with live(content=os.urandom(9000)) as (invoker, network):
            with pytest.raises(FileTooLarge):
                await download_file(invoker, a_document(size=9000), limit=1000)
            assert network.dc(HOME).asked == []

    async def test_a_file_of_unknown_length_stops_at_the_limit(self):
        # The size is not known in advance, so the limit can only be enforced
        # as the pieces arrive, and it has to be enforced before one is handed
        # over: a caller writing to disk has already written what it was given.
        data = os.urandom(10000)
        async with live(content=data) as (invoker, network):
            source = FileSource(
                location=locate(a_document()).location, dc_id=HOME, size=0
            )
            with pytest.raises(FileTooLarge):
                await download_file(invoker, source, chunk_size=4096, limit=5000)

    async def test_nothing_past_the_limit_reaches_the_disk(self, tmp_path):
        # What the check being in front of the yield actually buys. Behind it,
        # the piece that crossed the limit had already been written by the time
        # anyone said the limit was crossed.
        data = os.urandom(10000)
        into = tmp_path / "capped.bin"
        async with live(content=data) as (invoker, network):
            source = FileSource(
                location=locate(a_document()).location, dc_id=HOME, size=0
            )
            with pytest.raises(FileTooLarge):
                await download_file(
                    invoker, source, chunk_size=4096, limit=5000, into=into
                )
        assert not into.exists() or into.stat().st_size <= 5000

    async def test_a_file_of_unknown_length_exactly_at_the_limit_is_kept(self):
        data = os.urandom(8192)
        async with live(content=data) as (invoker, network):
            source = FileSource(
                location=locate(a_document()).location, dc_id=HOME, size=0
            )
            got = await download_file(
                invoker, source, chunk_size=4096, limit=len(data)
            )
            assert got == data


class TestStreaming:
    """In order, a piece at a time, from wherever it is asked for."""

    async def test_the_whole_file_arrives_in_order(self):
        data = os.urandom(20000)
        async with live(content=data) as (invoker, network):
            pieces = [
                piece
                async for piece in stream_file(
                    invoker, a_document(size=len(data)), chunk_size=4096
                )
            ]
            assert b"".join(pieces) == data
            # In order means one piece per chunk, not one piece for the file.
            assert len(pieces) > 1

    async def test_a_byte_range_is_honoured_exactly(self):
        data = bytes(range(256)) * 100
        async with live(content=data) as (invoker, network):
            for offset, length in ((0, 10), (1, 10), (4095, 2), (4096, 8192), (9000, 0)):
                got = b"".join(
                    [
                        piece
                        async for piece in stream_file(
                            invoker,
                            a_document(size=len(data)),
                            offset=offset,
                            length=length,
                            chunk_size=4096,
                        )
                    ]
                )
                wanted = data[offset : offset + length] if length else data[offset:]
                assert got == wanted, (offset, length)

    async def test_a_file_of_unknown_length_streams_to_the_end(self):
        data = os.urandom(10000)
        async with live(content=data) as (invoker, network):
            source = FileSource(
                location=locate(a_document()).location, dc_id=HOME, size=0
            )
            got = b"".join(
                [piece async for piece in stream_file(invoker, source, chunk_size=4096)]
            )
            assert got == data

    async def test_it_stops_asking_once_the_range_is_covered(self):
        data = os.urandom(60000)
        async with live(content=data) as (invoker, network):
            home = network.dc(HOME)
            got = b"".join(
                [
                    piece
                    async for piece in stream_file(
                        invoker, a_document(size=len(data)), length=100, chunk_size=4096
                    )
                ]
            )
            assert got == data[:100]
            # The whole point: one chunk fetched, not fifteen.
            fetches = [
                query
                for query in home.asked
                if isinstance(query, functions.upload.GetFile)
            ]
            assert len(fetches) == 1

    async def test_a_negative_range_is_refused(self):
        async with live(content=b"x") as (invoker, network):
            with pytest.raises(ValueError, match="not negative"):
                async for _ in stream_file(invoker, a_document(), offset=-1):
                    pass


class TestWhenThingsMove:
    async def test_a_file_elsewhere_is_fetched_from_there(self):
        data = os.urandom(8192)
        async with live(content=data) as (invoker, network):
            got = await download_file(
                invoker, a_document(size=len(data), dc_id=FAR), chunk_size=4096
            )
            assert got == data
            # Home stayed home, and the far end was signed in to.
            assert invoker.state.dc_id == HOME
            assert network.dc(FAR).imported

    async def test_being_told_the_file_moved_is_believed_once(self):
        data = os.urandom(8192)
        async with live(content=data) as (invoker, network):
            network.dc(HOME).moved_to = FAR
            got = await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=2
            )
            assert got == data

    async def test_a_stale_reference_is_refreshed_and_the_fetch_goes_on(self):
        data = os.urandom(8192)
        refreshed = 0

        async def refresh() -> Any:
            nonlocal refreshed
            refreshed += 1
            return a_document(size=len(data), reference=b"fresh")

        async with live(content=data) as (invoker, network):
            network.dc(HOME).stale_reference = b"ref"
            got = await download_file(
                invoker,
                a_document(size=len(data)),
                chunk_size=4096,
                workers=2,
                refresh=refresh,
            )
            assert got == data
            # Two workers both hit the stale reference; only one refresh.
            assert refreshed == 1

    async def test_a_stale_reference_with_no_refresh_says_what_to_do(self):
        async with live(content=os.urandom(4096)) as (invoker, network):
            network.dc(HOME).stale_reference = b"ref"
            with pytest.raises(SunnygramError, match="pass refresh"):
                await download_file(invoker, a_document(size=4096), chunk_size=4096)

    async def test_a_refresh_that_does_not_help_gives_up(self):
        async def refresh() -> Any:
            return a_document(reference=b"ref")

        async with live(content=os.urandom(4096)) as (invoker, network):
            network.dc(HOME).stale_reference = b"ref"
            with pytest.raises(SunnygramError, match="not producing a usable one"):
                await download_file(
                    invoker, a_document(size=4096), chunk_size=4096, refresh=refresh
                )


class TestThePool:
    """Several sockets to one datacenter, for the work that is worth it."""

    async def test_a_transfer_spreads_over_several_connections(self):
        data = os.urandom(16 * 4096)
        async with live(content=data) as (invoker, network):
            before = invoker.open_connections
            assert await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=4
            ) == data
            # Four workers, all of them busy at once, so the pool grew to meet
            # them rather than queueing behind one socket.
            assert invoker.open_connections > before
            assert len(invoker._pools[HOME]) == 4

    async def test_the_pool_stops_where_it_was_told_to(self):
        data = os.urandom(16 * 4096)
        async with live(content=data, bulk_connections=2) as (invoker, network):
            await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=6
            )
            assert len(invoker._pools[HOME]) == 2

    async def test_every_connection_is_its_own_mtproto_session(self):
        # The thing that makes a pool safe rather than a race: message ids and
        # sequence numbers are counted per session, so two sockets sharing one
        # would each invalidate the other's.
        data = os.urandom(16 * 4096)
        async with live(content=data) as (invoker, network):
            await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=4
            )
            assert len(network.dc(HOME).sessions) == invoker.open_connections

    async def test_a_small_fetch_does_not_open_four_sockets(self):
        data = os.urandom(4096)
        async with live(content=data) as (invoker, network):
            for _ in range(3):
                await download_file(
                    invoker, a_document(size=len(data)), chunk_size=4096, workers=1
                )
            # One piece at a time leaves the connection idle between calls, and
            # an idle one is reused rather than joined by another.
            assert len(invoker._pools[HOME]) == 1

    async def test_ordinary_calls_stay_off_the_transfer_connections(self):
        data = os.urandom(16 * 4096)
        async with live(content=data) as (invoker, network):
            await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=4
            )
            main = invoker.connection
            assert main is not None
            assert main not in invoker._pools[HOME]

    async def test_uploading_spreads_too(self):
        async with live() as (invoker, network):
            handle = await upload_file(
                invoker, os.urandom(16 * 1024), part_size=1024, workers=4
            )
            assert len(invoker._pools[HOME]) > 1
            assert network.dc(HOME).uploaded(handle.id)

    async def test_turning_the_pool_off_uses_the_one_connection(self):
        data = os.urandom(8 * 4096)
        async with live(content=data, bulk_connections=0) as (invoker, network):
            assert await download_file(
                invoker, a_document(size=len(data)), chunk_size=4096, workers=4
            ) == data
            assert invoker._pools == {}
            assert invoker.open_connections == 1


class TestWorkingInParallel:
    async def test_one_failure_stops_the_others(self):
        started = 0
        cancelled = 0

        async def work() -> None:
            nonlocal started, cancelled
            started += 1
            try:
                if started == 1:
                    raise ValueError("this one goes wrong")
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled += 1
                raise

        with pytest.raises(ValueError, match="goes wrong"):
            await in_parallel(work, 4)
        assert cancelled == 3

    async def test_the_original_failure_is_what_comes_out(self):
        async def work() -> None:
            raise FileTooLarge("as it is")

        with pytest.raises(FileTooLarge):
            await in_parallel(work, 2)

    async def test_no_workers_is_refused(self):
        async def work() -> None:
            return None

        with pytest.raises(ValueError):
            await in_parallel(work, 0)
