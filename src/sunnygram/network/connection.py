# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A live connection: one transport, one session, one reader.

This is the layer where a request becomes something you can await. Everything
below deals in frames and envelopes; from here up a caller says invoke and gets
an answer or an exception, and never has to know that the answer arrived out of
order, inside a container, gzipped, or after the server changed its mind about
the salt.

There is exactly one task reading the socket. A request registers a future under
the message id it was sent with, and the reader hands the answer back by looking
up rpc_result.req_msg_id. One reader is not an implementation detail: the
protocol numbers messages per session, so two readers would race over the same
replay window and the same acknowledgement list.

The reader also handles what the server says about the conversation itself
rather than about any one call. A stale salt, a clock that has drifted, a
sequence number the server will not accept: each has a correction, and the
request that tripped it is sent again under a new id once the correction is in.
That retry is why a caller can ignore all of it.

What is not here yet: reconnecting a dropped socket and following the *_MIGRATE
errors to another datacenter. Both need to decide which datacenter to talk to
and where the auth key for it is kept, which is the invoker's job above this.
A dropped connection therefore ends every waiting call and stays down.
"""

from __future__ import annotations

import asyncio
import logging
import platform
import secrets
from collections import deque
from contextlib import nullcontext
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Protocol, Self, cast

from ..errors import (
    BadMessage,
    DuplicateMessage,
    FloodWait,
    TLError,
    TransportClosed,
    TransportError,
    rpc_error,
)
from ..raw import LAYER, functions, types
from ..session import RPC_RESULT_ID, Message, Session, signed_long
from ..tl import TLFunction, TLObject, TLReader, TLResult, read_answer
from ..transport import Codec, TCPTransport
from .datacenter import Address, address_for
from .handshake import create_auth_key

__all__ = ["ClientInfo", "Connection", "Stream", "connect"]

_log = logging.getLogger(__name__)

# How long to sit on an acknowledgement hoping others arrive to travel with it,
# and how many are worth sending without waiting at all.
ACK_DELAY = 0.3
ACK_BATCH = 8

# A ping every so often keeps a connection the server would otherwise consider
# idle, and tells it to hang up if we go quiet for the delay instead.
PING_INTERVAL = 30.0
PING_DISCONNECT_DELAY = 75

# How long the answer to a ping is worth waiting for before deciding there is
# no one there. This is the only thing that notices a connection which is open
# as far as the operating system is concerned and dead as far as the
# conversation is concerned: a laptop that slept, a phone that changed network,
# a router that dropped the mapping without telling either end. Nothing arrives,
# nothing fails, and without this the program simply goes quiet for ever.
PONG_TIMEOUT = 15.0

# A FLOOD_WAIT no longer than this is waited out instead of raised, and a call
# only does that so many times before the caller hears about it.
FLOOD_THRESHOLD = 10.0
FLOOD_RETRIES = 2

# How many corrections one request is worth. Salts, clocks and sequence numbers
# each converge in one round, so a request needing more than this is caught in
# something that is not going to settle.
MAX_RESENDS = 5

# Calls in flight at once, and updates held for a reader that is not keeping up.
MAX_IN_FLIGHT = 512
UPDATES_QUEUE = 512

# How long a call waits before giving up on an answer that is not coming.
REQUEST_TIMEOUT = 60.0

# The server saying it has no record of the application on this connection, so
# the introduction has to be made again. Matched by name because it is the one
# RPC error this layer acts on itself instead of passing up.
_NOT_INITED = "CONNECTION_NOT_INITED"

# The bad_msg_notification codes this layer knows what to do about. The clock
# ones are corrected from the server's own message id; the sequence ones cannot
# be argued with and cost the session.
_CLOCK_CODES = frozenset({16, 17, 20})
_SEQUENCE_CODES = frozenset({32, 33})

# Housekeeping the server never expects an acknowledgement for, so sending one
# does not advance the sequence count either.
_NOT_CONTENT_RELATED = (
    types.mtproto.MsgsAck,
    functions.mtproto.Ping,
    functions.mtproto.PingDelayDisconnect,
)


class Stream(Protocol):
    """What a connection needs from whatever carries its frames.

    A TCPTransport satisfies this. Keeping it to three methods means the loop
    above has no opinion about TCP, which lets the tests drive it over a
    pair of queues instead of a socket.
    """

    async def send(self, payload: bytes) -> None: ...
    async def receive(self) -> bytes: ...
    async def close(self) -> None: ...


@dataclass(frozen=True, slots=True, repr=False)
class ClientInfo:
    """Who is calling: the application, and what to call the device it runs on.

    The api_id and api_hash are the pair my.telegram.org issues, and they belong
    together even though only the id is ever sent in initConnection. The device
    and app strings are what the account holder sees in their list of active
    sessions, so they are worth setting to something recognizable, not
    leaving as the default.
    """

    api_id: int
    api_hash: str = ""
    device_model: str = "Sunnygram"
    system_version: str = platform.system() or "Unknown"
    app_version: str = "0.1"
    lang_code: str = "en"
    system_lang_code: str = "en"
    lang_pack: str = ""

    def __repr__(self) -> str:
        # The hash is a credential, so it is written by hand instead of left to
        # the generated repr that would print it (rule S2).
        return (
            f"ClientInfo(api_id={self.api_id}, api_hash=<redacted>, "
            f"device_model={self.device_model!r}, app_version={self.app_version!r})"
        )


class _Pending:
    """One call waiting for its answer.

    Holds the request instead of the bytes it serializes to, because a request
    that has to be sent again may need to go out differently: a session that was
    reset has to introduce itself once more, and that wrapping is decided at the
    moment of sending.
    """

    __slots__ = ("future", "request", "msg_id", "resends")

    def __init__(self, request: TLFunction[Any]) -> None:
        self.future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self.request = request
        self.msg_id = 0
        self.resends = 0

    @property
    def method(self) -> str:
        """What to call this in an error message."""
        return self.request.QUALNAME

    def settle(self, result: Any) -> None:
        if not self.future.done():
            self.future.set_result(result)

    def fail(self, error: BaseException) -> None:
        if not self.future.done():
            self.future.set_exception(error)


class Connection:
    """One live, encrypted conversation with one datacenter.

    Built around an already-connected transport and a session that holds the
    auth key for it, so what happens when the socket cannot be opened, and where
    the key came from, are both someone else's decision. See connect for the
    usual way to get one.
    """

    __slots__ = (
        "_transport",
        "_session",
        "_client",
        "_dc_id",
        "_pending",
        "_slots",
        "_sending",
        "_acks",
        "_has_acks",
        "_updates",
        "_dropped_updates",
        "_unknown",
        "_reader",
        "_acker",
        "_pinger",
        "_failure",
        "_inited",
        "_timeout",
        "_flood_threshold",
        "_ping_interval",
        "_pong_timeout",
    )

    def __init__(
        self,
        transport: Stream,
        session: Session,
        *,
        dc_id: int = 0,
        client: ClientInfo | None = None,
        timeout: float = REQUEST_TIMEOUT,
        flood_threshold: float = FLOOD_THRESHOLD,
        ping_interval: float | None = PING_INTERVAL,
        pong_timeout: float = PONG_TIMEOUT,
        max_in_flight: int = MAX_IN_FLIGHT,
        updates_queue: int = UPDATES_QUEUE,
        updates: asyncio.Queue[TLObject] | None = None,
    ) -> None:
        self._transport = transport
        self._session = session
        self._client = client
        self._dc_id = dc_id
        self._timeout = timeout
        self._flood_threshold = flood_threshold
        self._ping_interval = ping_interval
        self._pong_timeout = pong_timeout

        self._pending: dict[int, _Pending] = {}
        # Backpressure rather than an error: a caller that would overflow the
        # in-flight cap waits its turn (rule P6).
        self._slots = asyncio.Semaphore(max_in_flight)
        # Held across minting an id and writing the frame. Sequence numbers only
        # mean anything in the order they reach the server.
        self._sending = asyncio.Lock()

        self._acks: deque[int] = deque()
        self._has_acks = asyncio.Event()
        # A queue can be handed in so it outlives the connection. Updates have
        # to survive a reconnect, since the layer draining them is tracking a
        # sequence that a gap in would cost a full resynchronization.
        self._updates: asyncio.Queue[TLObject] = (
            asyncio.Queue(updates_queue) if updates is None else updates
        )
        self._dropped_updates = 0
        self._unknown = 0

        self._reader: asyncio.Task[None] | None = None
        self._acker: asyncio.Task[None] | None = None
        self._pinger: asyncio.Task[None] | None = None
        self._failure: BaseException | None = None
        self._inited = client is None

    def __repr__(self) -> str:
        # The session redacts itself, and nothing else here is a secret.
        state = "running" if self.running else "stopped"
        return f"Connection(dc={self._dc_id or '?'}, {state}, {self._session!r})"

    @property
    def session(self) -> Session:
        """The session this connection speaks through."""
        return self._session

    @property
    def dc_id(self) -> int:
        """Which datacenter this connection reaches, if it was told."""
        return self._dc_id

    @property
    def in_flight(self) -> int:
        """How many calls are waiting on an answer right now.

        The one honest measure of how busy this connection is, which is what
        the pool above chooses on: a connection with nothing outstanding will
        answer sooner than one already carrying a file.
        """
        return len(self._pending)

    @property
    def running(self) -> bool:
        """Whether the reader is alive and calls can still be made.

        A recorded failure counts as not running even in the moment before the
        reader task has finished unwinding, so that nothing new is handed to a
        connection already known to be dead.
        """
        return (
            self._reader is not None
            and not self._reader.done()
            and self._failure is None
        )

    @property
    def updates(self) -> asyncio.Queue[TLObject]:
        """Everything the server sent that was not an answer to a call.

        The update layer drains this. It is bounded, because a consumer that
        stops draining must not be able to grow it without limit, and the reader
        never blocks on it: when it is full the newest update is dropped and
        counted, and a non-zero count is the update layer's cue that it has to
        catch up through getDifference instead of trust what it has.
        """
        return self._updates

    @property
    def dropped_updates(self) -> int:
        """How many updates were dropped because no one was draining them."""
        return self._dropped_updates

    @property
    def unknown_constructors(self) -> int:
        """How many incoming objects no constructor in the pinned layer claimed.

        Expected to be zero, and not fatal if it is not: a server running ahead
        of our schema can send something we cannot read, and dropping it is
        better than dropping the connection.
        """
        return self._unknown

    async def start(self) -> None:
        """Start the reader and the housekeeping that goes with it."""
        if self._reader is not None:
            raise TransportError("this connection is already running")
        self._failure = None
        self._reader = asyncio.create_task(self._read_loop(), name="sunnygram-reader")
        self._acker = asyncio.create_task(self._ack_loop(), name="sunnygram-acks")
        if self._ping_interval:
            self._pinger = asyncio.create_task(
                self._ping_loop(), name="sunnygram-ping"
            )

    async def close(self) -> None:
        """Stop everything and end any call still waiting. Safe to repeat."""
        for task in (self._reader, self._acker, self._pinger):
            if task is not None:
                task.cancel()
        for task in (self._reader, self._acker, self._pinger):
            if task is not None:
                # Cancellation is the expected outcome; a reader that stopped on
                # its own already recorded why in _failure.
                await asyncio.gather(task, return_exceptions=True)
        self._reader = self._acker = self._pinger = None
        self._settle_pending(TransportClosed("the connection was closed"))
        await self._transport.close()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def invoke(
        self, request: TLFunction[TLResult], *, timeout: float | None = None
    ) -> TLResult:
        """Call a TL function and wait for what the server answers with.

        The answer is typed as whatever the function says it is answered with,
        so invoking help.GetConfig gives back a Config and not an anything.

        Raises whatever the server refused with, as a typed error. A FLOOD_WAIT
        short enough to sit out is waited out here instead, which is the safe
        default: the alternative is every caller writing the same retry.
        """
        for attempt in range(FLOOD_RETRIES + 1):
            try:
                # What comes off the wire is a boxed object the codec resolves
                # by its id, so this is the one point where the static claim
                # meets the dynamic read. The schema is what backs it up.
                return cast(TLResult, await self._call(request, timeout))
            except FloodWait as flood:
                if attempt == FLOOD_RETRIES or flood.seconds > self._flood_threshold:
                    raise
                # Worth saying: from the outside this is the program pausing
                # for no visible reason, and knowing which call is being paced
                # is most of working out why.
                _log.info(
                    "waiting %.1fs before asking %s again, Telegram is pacing us",
                    flood.seconds,
                    request.QUALNAME,
                )
                await asyncio.sleep(flood.seconds)
        raise AssertionError("unreachable")

    async def _call(
        self, request: TLFunction[Any], timeout: float | None, *, metered: bool = True
    ) -> Any:
        if not self.running:
            raise self._closed_error()

        # Housekeeping does not queue behind content. The in-flight cap bounds
        # how much work a program has outstanding, and a ping is not that: it is
        # the one thing that notices the connection has died, so waiting for a
        # slot would switch it off exactly when a saturated connection makes an
        # unnoticed stall most expensive. The timeout it is given starts when
        # the call does, which on a metered path would be after the wait.
        async with (self._slots if metered else nullcontext()):
            pending = _Pending(request)
            await self._dispatch(pending)
            try:
                return await asyncio.wait_for(
                    pending.future, self._timeout if timeout is None else timeout
                )
            finally:
                # By now the id may not be the one it was sent under, because a
                # correction resends under a new one.
                self._pending.pop(pending.msg_id, None)

    def _prepare(self, request: TLFunction[Any]) -> TLObject:
        """Wrap the first call of a connection in what the server expects.

        A connection has to say who is calling and which schema layer it speaks
        before anything else, and only once. Doing it here instead of making
        callers remember is the whole point; a connection built without a
        ClientInfo sends the request bare, which only the handful of methods that
        need no application will answer.
        """
        if self._inited or self._client is None:
            return request
        self._inited = True
        info = self._client
        return functions.InvokeWithLayer(
            layer=LAYER,
            query=functions.InitConnection(
                api_id=info.api_id,
                device_model=info.device_model,
                system_version=info.system_version,
                app_version=info.app_version,
                system_lang_code=info.system_lang_code,
                lang_pack=info.lang_pack,
                lang_code=info.lang_code,
                query=request,
            ),
        )

    async def _dispatch(self, pending: _Pending) -> None:
        """Send a request and register it under the id it went out with.

        Registering happens under the same lock as minting the id, so an answer
        cannot arrive before there is anywhere to put it.
        """
        async with self._sending:
            prepared = self._prepare(pending.request)
            msg_id, frame = await self._session.encrypt_off_loop(
                prepared.to_bytes(), content_related=_content_related(prepared)
            )
            pending.msg_id = msg_id
            self._pending[msg_id] = pending
            try:
                await self._transport.send(frame)
            except TransportError:
                del self._pending[msg_id]
                raise

    async def _send(self, request: TLObject) -> int:
        """Send something no one is waiting on, like an ack or a ping."""
        async with self._sending:
            msg_id, frame = await self._session.encrypt_off_loop(
                request.to_bytes(), content_related=_content_related(request)
            )
            await self._transport.send(frame)
        return msg_id

    async def _resend(self, pending: _Pending) -> None:
        """Send a request again after correcting whatever the server objected to."""
        self._pending.pop(pending.msg_id, None)
        pending.resends += 1
        if pending.resends > MAX_RESENDS:
            pending.fail(
                TransportError(
                    f"{pending.method} was corrected and resent {MAX_RESENDS} "
                    "times without the server accepting it"
                )
            )
            return
        try:
            await self._dispatch(pending)
        except TransportError as exc:
            pending.fail(exc)

    async def _read_loop(self) -> None:
        """The one task that reads the socket.

        Anything that gets out of here ends the connection, because there is
        nothing above it to catch it: a break, a failed cryptographic check, or a
        bug of ours all leave callers waiting on an answer that can no longer
        arrive, so they are told instead.
        """
        try:
            while True:
                try:
                    frame = await self._transport.receive()
                    # One reader, so decrypting in a thread cannot let two
                    # frames through the replay window at once: the next read
                    # does not start until this one has been accounted for.
                    messages = await self._session.receive_off_loop(frame)
                except DuplicateMessage:
                    # A frame we have already been through, whole.
                    continue
                for message in messages:
                    await self._handle(message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._settle_pending(exc)

    async def _handle(self, message: Message) -> None:
        """Act on one message, whatever it turns out to be."""
        # Content-related messages are the ones the server wants an answer about,
        # and the sequence number is what says which those are.
        if message.seq_no % 2:
            self._queue_ack(message.msg_id)

        if _peek(message.body) == RPC_RESULT_ID:
            await self._handle_result(message.body)
            return

        try:
            body = TLReader(message.body).read_object()
        except TLError as unreadable:
            # A newer layer than ours, or something we simply cannot read. Not
            # worth the connection.
            self._unknown += 1
            _log.debug("dropped an object this layer cannot read: %s", unreadable)
            return

        if isinstance(body, types.mtproto.BadServerSalt):
            await self._handle_bad_salt(body)
        elif isinstance(body, types.mtproto.BadMsgNotification):
            await self._handle_bad_message(body, message.msg_id)
        elif isinstance(body, types.mtproto.NewSessionCreated):
            self._handle_new_session(body)
        elif isinstance(body, types.mtproto.Pong):
            self._answer(body.msg_id, body)
        elif isinstance(body, types.mtproto.FutureSalts):
            self._answer(body.req_msg_id, body)
        elif isinstance(body, types.mtproto.MsgsAck):
            # Nothing to do: we do not resend on our own, so knowing which of our
            # messages arrived changes nothing yet.
            pass
        elif isinstance(
            body, (types.mtproto.MsgDetailedInfo, types.mtproto.MsgNewDetailedInfo)
        ):
            # The server is describing an answer it is holding. Acknowledging it
            # is what stops the description from coming back.
            self._queue_ack(body.answer_msg_id)
        elif isinstance(body, TLObject):
            self._queue_update(body)

    async def _handle_result(self, body: bytes) -> None:
        """Route one rpc_result back to whoever asked.

        rpc_result is one of the constructors the schema cannot generate, since
        what it carries depends on the call it answers, so it is read by hand:
        the id, the message id of the request, and then whatever came back.
        """
        reader = TLReader(body)
        reader.read_int(signed=False)
        req_msg_id = reader.read_long()
        pending = self._pending.get(req_msg_id)
        try:
            # The call that was made is what knows how to read its own answer,
            # for the two result shapes the bytes do not describe.
            result = read_answer(
                reader, pending.request.RESULT if pending is not None else ""
            )
        except TLError as exc:
            self._unknown += 1
            if pending is not None:
                pending.fail(exc)
            return

        if pending is None:
            # No one is waiting: the call was cancelled or timed out.
            return
        if isinstance(result, types.mtproto.RpcError):
            if result.error_message == _NOT_INITED:
                _log.info(
                    "dc %s has no record of this application, introducing it again",
                    self._dc_id or "?",
                )
                # The server has forgotten who is calling, which happens when it
                # moves a session between its own machines. Only this layer can
                # answer it, because only this layer knows the introduction is
                # something it sends once and stops sending. Saying it again and
                # resending is the whole fix, and without it every call from
                # here on is refused for the same reason.
                self._inited = self._client is None
                await self._resend(pending)
                return
            pending.fail(
                rpc_error(result.error_code, result.error_message, method=pending.method)
            )
        else:
            pending.settle(result)

    async def _handle_bad_salt(self, notification: types.mtproto.BadServerSalt) -> None:
        """Take the salt the server offered and send the refused request again.

        Salts expire, and the server answers a stale one by handing over the
        current one. Nothing was processed, so resending is safe.
        """
        self._session.salt = signed_long(notification.new_server_salt)
        pending = self._pending.get(notification.bad_msg_id)
        if pending is not None:
            await self._resend(pending)

    async def _handle_bad_message(
        self, notification: types.mtproto.BadMsgNotification, msg_id: int
    ) -> None:
        """Correct what the server objected to, if it is correctable.

        The clock complaints are answered from the notification's own message id,
        which is the server saying what time it is. A sequence number it will not
        accept cannot be corrected in place, so the session goes and everything
        outstanding follows into the new one.

        This only ever corrects small drifts, because the handshake already set
        our clock from the server's: a gap wide enough to fall outside the
        session's own time window fails there first, as it should, since at that
        point we cannot tell a stale message from a replayed one.
        """
        code = notification.error_code
        pending = self._pending.get(notification.bad_msg_id)

        if code in _CLOCK_CODES:
            self._session.adopt_server_time(msg_id)
            if pending is not None:
                await self._resend(pending)
            return

        if code in _SEQUENCE_CODES:
            _log.warning(
                "dc %s refused our sequence numbering (code %d), starting a new "
                "session and sending %d outstanding calls again",
                self._dc_id or "?",
                code,
                len(self._pending),
            )
            self._session.reset()
            self._inited = self._client is None
            for outstanding in list(self._pending.values()):
                await self._resend(outstanding)
            return

        if pending is not None:
            pending.fail(BadMessage(code))
            self._pending.pop(notification.bad_msg_id, None)

    def _handle_new_session(
        self, notification: types.mtproto.NewSessionCreated
    ) -> None:
        """Adopt the salt of a session the server started on its own.

        It means the server lost track of ours, so anything sent before
        first_msg_id may never have run. It may equally have run and had its
        answer lost, and sending a message twice is worse than a call that times
        out, so nothing is resent. The notification goes to the update layer,
        which treats it as a reason to resynchronize from scratch.
        """
        self._session.salt = signed_long(notification.server_salt)
        self._queue_update(notification)

    def _answer(self, req_msg_id: int, result: TLObject) -> None:
        """Hand an answer that is not an rpc_result to whoever asked for it."""
        pending = self._pending.get(req_msg_id)
        if pending is not None:
            pending.settle(result)

    def _queue_ack(self, msg_id: int) -> None:
        self._acks.append(msg_id)
        self._has_acks.set()

    def _queue_update(self, update: TLObject) -> None:
        try:
            self._updates.put_nowait(update)
        except asyncio.QueueFull:
            if not self._dropped_updates:
                # Once per connection, not once per update: something already
                # falling behind does not need a log line for every one it
                # loses. The count is on the property for anyone who wants it,
                # and the update layer is watching that, not this.
                _log.warning(
                    "nobody is draining updates fast enough, so some are being "
                    "dropped and made up for with a difference"
                )
            self._dropped_updates += 1

    async def _ack_loop(self) -> None:
        """Send acknowledgements in batches instead of one per message."""
        while True:
            await self._has_acks.wait()
            if len(self._acks) < ACK_BATCH:
                # Give the others a moment to arrive and travel together.
                await asyncio.sleep(ACK_DELAY)
            batch = list(self._acks)
            self._acks.clear()
            self._has_acks.clear()
            if not batch:
                continue
            try:
                await self._send(types.mtproto.MsgsAck(msg_ids=batch))
            except TransportError:
                # The reader will see the same break and end the connection.
                return

    async def _ping_loop(self) -> None:
        """Keep the connection alive, and notice when it is not.

        The delay carried by the ping is what tells the server to give up on us
        if we go quiet. The answer is what tells us to give up on the server,
        and it is the half that matters more: a socket can stay open long after
        anything is listening at the other end, and every write into it will
        succeed while every read waits for ever. Nothing else in the stack
        notices that, because from the inside it is indistinguishable from a
        conversation where no one has said anything yet.
        """
        assert self._ping_interval is not None
        while True:
            await asyncio.sleep(self._ping_interval)
            ping = functions.mtproto.PingDelayDisconnect(
                ping_id=secrets.randbits(63),
                disconnect_delay=PING_DISCONNECT_DELAY,
            )
            try:
                await self._call(ping, self._pong_timeout, metered=False)
            except TransportError:
                # The reader has seen the same break and is ending the
                # connection for itself.
                return
            except TimeoutError:
                _log.warning(
                    "dc %s did not answer a ping in %.0fs, dropping the connection",
                    self._dc_id or "?",
                    self._pong_timeout,
                )
                self._die(
                    TransportClosed(
                        "the server did not answer a ping within "
                        f"{self._pong_timeout:.0f} seconds, so this connection "
                        "is not carrying anything any more"
                    )
                )
                return

    def _die(self, error: BaseException) -> None:
        """End this connection from the inside, instead of waiting on a socket.

        Used when something other than the reader works out that the connection
        is finished. Everything waiting is told, and the reader is stopped: a
        reader blocked on a socket that will never produce another byte would
        otherwise keep this looking alive for ever.
        """
        self._settle_pending(error)
        reader = self._reader
        if reader is not None:
            reader.cancel()

    def _settle_pending(self, error: BaseException) -> None:
        """End every waiting call with the same reason."""
        if self._failure is None:
            self._failure = error
        pending, self._pending = self._pending, {}
        for waiting in pending.values():
            waiting.fail(error)

    def _closed_error(self) -> BaseException:
        """Why a call made now cannot go anywhere.

        A new error each time rather than the failure itself, which would collect
        a traceback for every call made after the connection went down. What went
        wrong is still reachable as the cause.
        """
        failure = self._failure
        if failure is None:
            return TransportClosed("this connection is not running")
        error = TransportClosed(f"this connection is not running: {failure}")
        error.__cause__ = failure
        return error


async def connect(
    dc_id: int = 2,
    *,
    test: bool = False,
    ipv6: bool = False,
    address: Address | None = None,
    auth_key: bytes | None = None,
    salt: int = 0,
    time_offset: float = 0.0,
    client: ClientInfo | None = None,
    codec: Codec | None = None,
    **options: Any,
) -> Connection:
    """Open a connection to a datacenter and start reading.

    With no auth key one is negotiated first, which costs three round trips and
    is why the key is worth storing. The connection comes back already running,
    so the caller can invoke straight away, and closing it is the caller's job.
    """
    where = address_for(dc_id, test=test, ipv6=ipv6) if address is None else address
    transport = TCPTransport(codec)
    await transport.connect(where.host, where.port)
    try:
        if auth_key is None:
            negotiated = await create_auth_key(transport, dc_id=dc_id, test=test)
            auth_key, salt, time_offset = (
                negotiated.key,
                negotiated.salt,
                negotiated.time_offset,
            )
        connection = Connection(
            transport,
            Session(auth_key, salt=salt, time_offset=time_offset),
            dc_id=where.dc_id,
            client=client,
            **options,
        )
        await connection.start()
    except BaseException:
        await transport.close()
        raise
    return connection


def _content_related(request: TLObject) -> bool:
    """Whether a message counts toward the sequence the server acknowledges.

    Acks and pings do not: they are about the conversation instead of part of
    it, and numbering them as content would put the two ends out of step over
    what still needs acknowledging.
    """
    return not isinstance(request, _NOT_CONTENT_RELATED)


def _peek(body: bytes) -> int | None:
    """The constructor id at the front of a body, if there is room for one."""
    if len(body) < 4:
        return None
    return int.from_bytes(body[:4], "little")
