"""A datacenter that answers, for tests that need one.

The server side of an encrypted session: it shares the auth key and packs with
the direction flipped, which is what a real one does with the other half of the
key. Anything driven through this goes over the whole path, envelope and session
checks included, so a test can be about routing or reconnecting without being
about make-believe.

Shared by the connection tests and the invoker tests, since the second is the
first with the socket pulled out from under it.
"""

from __future__ import annotations

import asyncio
import gzip
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from sunnygram.errors import TransportClosed
from sunnygram.raw import functions, types
from sunnygram.session import (
    CONTAINER_ID,
    RPC_RESULT_ID,
    Message,
    Session,
    pack_encrypted,
    unpack_encrypted,
    unwrap_container,
)
from sunnygram.tl import GZIP_PACKED, TLObject, TLReader, TLWriter

AUTH_KEY = bytes(range(256))
SALT = 0x0102030405060708
NEW_SALT = 0x1122334455667788

NEAREST = types.NearestDc(country="IT", this_dc=2, nearest_dc=2)


def a_call() -> functions.help.GetNearestDc:
    """A small request with a small answer, for tests about anything else."""
    return functions.help.GetNearestDc()


def closing(handler: Any) -> Any:
    """Wrap a loopback handler so its half of the socket is put down after.

    asyncio's stream writer complains about being collected still open, and
    the complaint arrives whenever the garbage collector gets round to it,
    which is inside whatever unrelated test is running by then. Closing it
    here stops the tests that use a real socket blaming the ones that do not.
    """

    async def wrapped(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            await handler(reader, writer)
        finally:
            writer.close()

    return wrapped


class Wire:
    """Two queues standing in for a socket, from the client's side."""

    def __init__(self) -> None:
        self.to_server: asyncio.Queue[bytes] = asyncio.Queue()
        self.to_client: asyncio.Queue[bytes | BaseException] = asyncio.Queue()
        self.closed = False

    async def send(self, payload: bytes) -> None:
        if self.closed:
            raise TransportClosed("the transport is not connected")
        await self.to_server.put(payload)

    async def receive(self) -> bytes:
        payload = await self.to_client.get()
        if isinstance(payload, BaseException):
            raise payload
        return payload

    async def close(self) -> None:
        self.closed = True

    def break_it(self, error: BaseException | None = None) -> None:
        """Make the next read fail, the way a dropped socket would."""
        self.to_client.put_nowait(
            error or TransportClosed("the connection ended mid-packet")
        )


@dataclass(frozen=True, slots=True)
class Received:
    """One message the server took off the wire."""

    msg_id: int
    seq_no: int
    body: TLObject

    @property
    def query(self) -> Any:
        """What was really asked, past any wrapping the connection added."""
        request = self.body
        while isinstance(
            request, (functions.InvokeWithLayer, functions.InitConnection)
        ):
            request = request.query
        return request


class ScriptedServer:
    """The datacenter half: reads what the client sends, answers on demand."""

    def __init__(
        self, wire: Wire, session: Session, *, auth_key: bytes = AUTH_KEY
    ) -> None:
        self.wire = wire
        self.auth_key = auth_key
        # Held rather than copied, so a session the connection resets stays
        # readable here, exactly as a real server would learn the new id.
        self.session = session
        self.salt = SALT
        self.acked: list[int] = []
        self.seen: list[Received] = []
        self._next_id = 0

    def _mint(self) -> int:
        """A server message id: ours to hand out, and always increasing."""
        self._next_id = max(self._next_id + 4, (int(time.time()) << 32) | 1)
        return self._next_id

    async def _read(self) -> list[Received]:
        session_id, message = unpack_encrypted(
            self.auth_key, await self.wire.to_server.get(), outgoing=True
        )
        assert session_id == self.session.session_id, "a message for another session"
        received = []
        for held in unwrap_container(message):
            body = TLReader(held.body).read_object()
            received.append(Received(held.msg_id, held.seq_no, body))
        return received

    async def take(self) -> Received:
        """The next real request, recording any acknowledgements on the way."""
        while True:
            for received in await self._read():
                if isinstance(received.body, types.mtproto.MsgsAck):
                    self.acked.extend(received.body.msg_ids)
                    continue
                self.seen.append(received)
                return received

    async def take_ack(self) -> list[int]:
        """Wait for the next batch of acknowledgements."""
        while True:
            for received in await self._read():
                if isinstance(received.body, types.mtproto.MsgsAck):
                    self.acked.extend(received.body.msg_ids)
                    return received.body.msg_ids
                self.seen.append(received)

    async def push(self, body: bytes, *, seq_no: int = 1, msg_id: int = 0) -> int:
        """Send one already-serialized message to the client."""
        chosen = msg_id or self._mint()
        await self.wire.to_client.put(
            pack_encrypted(
                self.auth_key,
                self.salt,
                self.session.session_id,
                Message(chosen, seq_no, body),
                outgoing=False,
            )
        )
        return chosen

    async def send(self, body: TLObject, *, seq_no: int = 1) -> int:
        return await self.push(body.to_bytes(), seq_no=seq_no)

    async def answer(
        self,
        req_msg_id: int,
        result: TLObject | list[TLObject] | bool,
        *,
        packed: bool = False,
    ) -> int:
        """Answer one request with an rpc_result carrying a result."""
        return await self.push(rpc_result(req_msg_id, result, packed=packed))

    async def refuse(self, req_msg_id: int, code: int, message: str) -> int:
        return await self.answer(
            req_msg_id, types.mtproto.RpcError(error_code=code, error_message=message)
        )

    async def container(self, *bodies: bytes) -> int:
        """Bundle several answers into one message, as a busy server would."""
        writer = TLWriter()
        writer.write_int(CONTAINER_ID, signed=False)
        writer.write_int(len(bodies))
        for body in bodies:
            writer.write_long(self._mint())
            writer.write_int(1)
            writer.write_int(len(body))
            writer.write_raw(body)
        return await self.push(writer.getvalue(), seq_no=0)

    async def serve(self, answers: dict[type, TLObject]) -> None:
        """Answer whatever arrives, from a table, until cancelled.

        For tests that care about what happens around a call rather than about
        the call itself.
        """
        while True:
            request = await self.take()
            result = answers.get(type(request.query))
            if result is None:
                await self.refuse(request.msg_id, 400, "METHOD_NOT_TESTED")
            else:
                await self.answer(request.msg_id, result)


class RecordingServer(ScriptedServer):
    """A server that keeps every request and answers from one rule.

    What a test about a call rather than about the protocol wants: run it, then
    read back what actually went out. answer_with is a function of the request,
    and leaving it alone answers everything with an empty Updates, which is
    what most calls really answer with.
    """

    def __init__(self, wire: Wire, session: Session, *, auth_key: bytes = AUTH_KEY):
        super().__init__(wire, session, auth_key=auth_key)
        self.queries: list[Any] = []
        self.answer_with: Any = None

    async def serve_all(self) -> None:
        while True:
            request = await self.take()
            self.queries.append(request.query)
            try:
                made = (
                    self.answer_with(request.query)
                    if self.answer_with is not None
                    else types.Updates(
                        updates=[], users=[], chats=[], date=1700000000, seq=0
                    )
                )
                await self.answer(request.msg_id, made)
            except Exception as failure:
                # A scripted answer that raises would otherwise take this task
                # down quietly and leave the caller waiting out its timeout, so
                # the mistake comes back as an error the test can read. Writing
                # the answer is inside this too: an answer that cannot be
                # serialized is exactly as easy to write by accident, and it
                # used to hang instead of saying so.
                await self.refuse(request.msg_id, 500, f"SCRIPT_FAILED: {failure!r}")
                continue

    def all(self, kind: type) -> list[Any]:
        return [query for query in self.queries if isinstance(query, kind)]

    def only(self, kind: type) -> Any:
        found = self.all(kind)
        assert len(found) == 1, f"expected one {kind.__name__}, got {len(found)}"
        return found[0]


def rpc_result(
    req_msg_id: int,
    result: TLObject | list[TLObject] | bool,
    *,
    packed: bool = False,
) -> bytes:
    """The rpc_result envelope, which the schema leaves to be written by hand."""
    writer = TLWriter()
    writer.write_int(RPC_RESULT_ID, signed=False)
    writer.write_long(req_msg_id)
    if packed:
        writer.write_int(GZIP_PACKED, signed=False)
        writer.write_bytes(gzip.compress(_serialize(result)))
    else:
        writer.write_raw(_serialize(result))
    return writer.getvalue()


def _serialize(result: TLObject | list[TLObject] | bool) -> bytes:
    """One object, the boxed vector some calls answer with, or a plain Bool.

    The bool is worth spelling out. It is a TL constructor rather than a byte,
    and a Python bool carries an int's to_bytes, so leaving it to the last
    branch would quietly produce one byte and a frame nobody can read.
    """
    if isinstance(result, bool):
        writer = TLWriter()
        writer.write_bool(result)
        return writer.getvalue()
    if isinstance(result, list):
        writer = TLWriter()
        # Vector<int> is a real answer shape, and its elements are bare ints
        # rather than boxed objects, so they need the writer naming.
        if all(isinstance(item, int) and not isinstance(item, bool) for item in result):
            writer.write_vector(result, TLWriter.write_int)
        else:
            writer.write_vector(result)
        return writer.getvalue()
    return result.to_bytes()


class Loopback:
    """A connector that hands out a fresh wire per connection and keeps them.

    The seam Invoker takes instead of opening a socket, which is what lets a
    test drive the whole stack without one.
    """

    def __init__(self) -> None:
        self.wires: list[tuple[Any, Wire]] = []

    async def connect(self, where: Any) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


@asynccontextmanager
async def recording(
    *, user_id: int = 777000, dc_id: int = 2
) -> AsyncIterator[tuple[Any, RecordingServer]]:
    """A started invoker talking to a RecordingServer, and the pair of them.

    Every test about a call rather than about the protocol wants exactly this,
    and four copies of it had been written before it was worth sharing. The
    rate limiter is off because these send in bursts no real program would and
    waiting out its buckets would only make the suite slow.
    """
    from sunnygram.network import ClientInfo, Invoker
    from sunnygram.storage import MemoryStorage, SessionState

    session = SessionState(dc_id=dc_id, user_id=user_id)
    session.set_auth_key(dc_id, AUTH_KEY)
    network = Loopback()
    invoker = Invoker(
        MemoryStorage(session),
        client=ClientInfo(api_id=12345, api_hash="0" * 32),
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
        rate_limit=False,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = RecordingServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve_all())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
