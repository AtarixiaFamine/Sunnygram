# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""One MTProto session over one authorization key.

A session is the bookkeeping that sits between an auth key and a stream of
messages: the current salt, an id that tells our messages apart from those of
any other client on the same key, the sequence numbers, and the memory needed to
notice a message arriving twice.

Sequence numbers count only the messages that carry content. Acknowledgements
and other housekeeping share the count without advancing it, which lets
both ends agree on what still needs acknowledging.

The incoming checks live here instead of in the envelope because they need
state: which session we are, what time it is, and what we have already seen.
They come in two kinds. A message with the wrong session, the wrong parity or a
date outside the window is a SecurityError and ends the connection. A message we
have already handled only raises DuplicateMessage, because a server that missed
our acknowledgement is meant to send its answer again, so the copy is dropped
and the stream carries on.

The date window has one exception, and it is the difference between a library
that survives a wrong clock and one that does not. A session that has not been
told the time yet takes it from the first message the server sends instead of
judging that message by a local clock there is no reason to trust. Otherwise a
machine an hour out of step refuses the correction it is being sent, which is
the kind of fault that reads as "it just stops working on that one computer".
"""

from __future__ import annotations

import secrets
import time
from collections import deque

from ..crypto import off_loop
from ..errors import DuplicateMessage, SecurityError
from .msg_id import MessageIdGenerator, is_server_id, msg_id_time
from .mtproto import (
    Message,
    pack_encrypted,
    signed_long,
    unpack_encrypted,
    unwrap_container,
)

__all__ = ["FUTURE_TOLERANCE", "PAST_TOLERANCE", "Session"]

# How far out of step with the server a message id may be. A message from too
# far ahead or too far behind is stale or replayed, whatever the reason.
FUTURE_TOLERANCE = 30.0
PAST_TOLERANCE = 300.0

_DEFAULT_HISTORY = 128


class Session:
    """The state of one conversation with one datacenter."""

    __slots__ = (
        "salt",
        "session_id",
        "_auth_key",
        "_ids",
        "_sent",
        "_seen",
        "_order",
        "_floor",
        "_history",
        "_check_time",
        "_time_known",
    )

    def __init__(
        self,
        auth_key: bytes,
        *,
        salt: int = 0,
        session_id: int | None = None,
        time_offset: float = 0.0,
        history: int = _DEFAULT_HISTORY,
        check_time: bool = True,
    ) -> None:
        if len(auth_key) != 256:
            raise ValueError(f"an auth key is 256 bytes, got {len(auth_key)}")
        self._auth_key = auth_key
        # Both are held in the signed spelling the wire reads back, so an id
        # generated from random bits still matches the one that comes home.
        self.salt = signed_long(salt)
        self.session_id = signed_long(
            secrets.randbits(64) if session_id is None else session_id
        )
        self._ids = MessageIdGenerator(time_offset)
        self._sent = 0
        # Bounded, like everything that grows (rule P6). Once an id falls out of
        # the window, the floor stops it coming back.
        self._history = history
        self._seen: set[int] = set()
        self._order: deque[int] = deque()
        self._floor = 0
        self._check_time = check_time
        # Whether anything has told us what time the server thinks it is. A
        # session built on a freshly negotiated key was told during the
        # handshake; one built on a stored key has not been told anything, and
        # the first message the server sends is what tells it. An offset that
        # happens to be zero because the clock is right costs nothing here: the
        # first message sets it to the same thing again.
        self._time_known = time_offset != 0.0

    @property
    def time_offset(self) -> float:
        """How far ahead of us the server's clock runs."""
        return self._ids.time_offset

    @time_offset.setter
    def time_offset(self, value: float) -> None:
        self._ids.time_offset = value

    @property
    def time_known(self) -> bool:
        """Whether this session has been told what time the server thinks it is."""
        return self._time_known

    def adopt_server_time(self, server_msg_id: int) -> None:
        """Set our clock from a message id the server itself minted.

        Used when the server complains that our ids are too low or too high, and
        on the first message of a session that started from a stored key. Its
        own id says what time it thinks it is, which is the only opinion that
        matters, and adopting it lets the next id land inside the window.
        """
        self._ids.adopt(msg_id_time(server_msg_id) - time.time())
        self._time_known = True

    def reset(self) -> None:
        """Start again on the same key, under a new session id.

        The remedy for a sequence number the server will not accept: there is no
        way to argue about the count, so the count is abandoned along with the
        session it belonged to. The key, the salt and the clock all survive,
        since none of them was what went wrong.
        """
        self.session_id = signed_long(secrets.randbits(64))
        self._sent = 0
        self._seen.clear()
        self._order.clear()
        self._floor = 0

    def __repr__(self) -> str:
        # Never the auth key, not even a slice of it (rule S2).
        return f"Session(session_id=0x{self.session_id & 0xFFFFFFFFFFFFFFFF:016x})"

    def next_seq_no(self, *, content_related: bool) -> int:
        """The sequence number for the next message.

        Content-related messages take an odd number and move the count on;
        everything else reads the count without touching it.
        """
        if not content_related:
            return self._sent * 2
        seq_no = self._sent * 2 + 1
        self._sent += 1
        return seq_no

    def encrypt(self, body: bytes, *, content_related: bool = True) -> tuple[int, bytes]:
        """Wrap a serialized message, returning its id and the frame to send.

        The id comes back because it is how an answer will be matched to this
        request.
        """
        msg_id = self._ids.next()
        seq_no = self.next_seq_no(content_related=content_related)
        frame = pack_encrypted(
            self._auth_key, self.salt, self.session_id, Message(msg_id, seq_no, body)
        )
        return msg_id, frame

    async def encrypt_off_loop(
        self, body: bytes, *, content_related: bool = True
    ) -> tuple[int, bytes]:
        """encrypt, with a big cipher call moved to a worker thread.

        The id and the sequence number are still taken here, on the loop, and
        only the cipher travels. That matters: both of those are the order the
        server expects things in, so a caller has to hold whatever lock keeps
        sends in order across the await, exactly as it would for encrypt.
        """
        msg_id = self._ids.next()
        seq_no = self.next_seq_no(content_related=content_related)
        message = Message(msg_id, seq_no, body)
        frame = await off_loop(
            len(body),
            pack_encrypted,
            self._auth_key,
            self.salt,
            self.session_id,
            message,
        )
        return msg_id, frame

    def decrypt(self, frame: bytes) -> Message:
        """Unwrap a message and hold it to every incoming check."""
        return self._checked(*unpack_encrypted(self._auth_key, frame))

    async def decrypt_off_loop(self, frame: bytes) -> Message:
        """decrypt, with a big cipher call moved to a worker thread.

        The checks stay here rather than travelling with the cipher, so the
        replay window is only ever touched by the task that owns this session.
        """
        return self._checked(
            *await off_loop(len(frame), unpack_encrypted, self._auth_key, frame)
        )

    def _checked(self, session_id: int, message: Message) -> Message:
        if session_id != self.session_id:
            raise SecurityError("this message belongs to a different session")
        self._accept(message.msg_id)
        return message

    def receive(self, frame: bytes) -> list[Message]:
        """Unwrap a frame into the messages it really carries.

        What arrives may be one message or a container of several, and each one
        inside a container has an id of its own that has to pass the same checks
        as the envelope's. A copy of something already handled is dropped rather
        than raised over, because a container is allowed to redeliver an answer
        we never acknowledged while still carrying messages that are new.
        """
        return self._unwrap(self.decrypt(frame))

    async def receive_off_loop(self, frame: bytes) -> list[Message]:
        """receive, with a big cipher call moved to a worker thread."""
        return self._unwrap(await self.decrypt_off_loop(frame))

    def _unwrap(self, envelope: Message) -> list[Message]:
        held = unwrap_container(envelope)
        if len(held) == 1 and held[0].msg_id == envelope.msg_id:
            # Not a container, so the id has already been through the checks.
            return held

        fresh = []
        for message in held:
            try:
                self._accept(message.msg_id)
            except DuplicateMessage:
                continue
            fresh.append(message)
        return fresh

    def _accept(self, msg_id: int) -> None:
        if not is_server_id(msg_id):
            raise SecurityError(
                "this message id has our parity, so it did not come from a server"
            )
        if self._check_time:
            if not self._time_known:
                # Nothing has told us the time yet, so this message is what
                # does. Judging it against a clock we have no reason to trust
                # would be judging the server by our own watch, and on a machine
                # whose clock is out that is a trap with no way out: the message
                # refused would be the very bad_msg_notification that says what
                # time it really is. Adopting is safe because the frame has
                # already proved it came from the holder of the auth key, which
                # is a stronger thing to know than the handshake knew when it
                # took the server's word for the time in the first place.
                self.adopt_server_time(msg_id)
            else:
                drift = msg_id_time(msg_id) - (time.time() + self._ids.time_offset)
                if drift > FUTURE_TOLERANCE:
                    raise SecurityError(
                        f"this message is dated {drift:.0f} seconds into the future"
                    )
                if -drift > PAST_TOLERANCE:
                    raise SecurityError(
                        f"this message is dated {-drift:.0f} seconds into the past"
                    )
        if msg_id <= self._floor:
            raise DuplicateMessage(
                "this message is older than anything still remembered"
            )
        if msg_id in self._seen:
            raise DuplicateMessage("this message has already been handled")

        self._seen.add(msg_id)
        self._order.append(msg_id)
        if len(self._order) > self._history:
            dropped = self._order.popleft()
            self._seen.discard(dropped)
            # Whatever leaves the window raises the floor, so it can never be
            # accepted a second time even once it is forgotten.
            self._floor = max(self._floor, dropped)
