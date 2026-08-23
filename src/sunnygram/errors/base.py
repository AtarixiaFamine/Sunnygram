# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The hand-written roots of the exception tree.

Everything Sunnygram raises derives from SunnygramError, so a caller can wrap a
whole session in one except clause. The typed RPC errors that Telegram returns
are generated from the error table and hang off this same root.
"""

from __future__ import annotations

__all__ = [
    "BadMessage",
    "DuplicateMessage",
    "FileTooLarge",
    "MalformedFrame",
    "NoAnswer",
    "PeerNotFound",
    "ProxyError",
    "SecurityError",
    "SunnygramError",
    "TLError",
    "TLSerializationError",
    "TLDeserializationError",
    "TransportClosed",
    "TransportError",
    "TransportRejected",
    "UnknownConstructorError",
    "UploadRefused",
]

# The negative codes a server can answer with instead of a packet, and what
# they usually mean in practice.
_TRANSPORT_CODES = {
    -404: "the server does not know this authorization key",
    -429: "too many connections from this address",
    -444: "the request reached the wrong datacenter",
}

# What a bad_msg_notification means. The connection acts on some of these on
# its own; the rest reach the caller.
_BAD_MESSAGE_CODES = {
    16: "the message id was too low, so our clock is behind the server's",
    17: "the message id was too high, so our clock is ahead of the server's",
    18: "the message id was not divisible by four",
    19: "two messages in one container shared a message id",
    20: "the message was too old to still be answerable",
    32: "the sequence number was too low",
    33: "the sequence number was too high",
    34: "an even sequence number was used for a content-related message",
    35: "an odd sequence number was used for a housekeeping message",
    48: "the server salt had expired",
    64: "the container was invalid",
}


class SunnygramError(Exception):
    """Base class for every error the library raises."""


class TLError(SunnygramError):
    """Something went wrong encoding or decoding the binary TL format."""


class TLSerializationError(TLError):
    """A value cannot be represented in TL, so nothing was written."""


class TLDeserializationError(TLError):
    """The incoming bytes are not valid TL.

    Server data is untrusted, so the reader raises this instead of guessing:
    truncated buffers, impossible lengths and unknown constructors all land
    here instead of producing a half-built object.
    """


class SecurityError(SunnygramError):
    """A cryptographic check did not hold.

    Always fatal. There is no safe way to carry on with data that failed one
    of these, so nothing catches it to retry.
    """


class DuplicateMessage(SunnygramError):
    """A message that has already been handled, or is too old to tell.

    Not a SecurityError, because the protocol asks for it: a server that never
    saw our acknowledgement is expected to send an answer again, so the same
    message id arriving twice is ordinary. The right response either way is to
    drop the copy and carry on, which is also the right response to a replay,
    so the two need no telling apart.
    """


class BadMessage(SunnygramError):
    """The server refused a message before running it.

    A bad_msg_notification, which says what was wrong with the envelope rather
    than with the call: the clock, the sequence number, the salt. The
    connection corrects and resends what it can, and what it cannot reaches the
    caller as this.
    """

    def __init__(self, code: int) -> None:
        self.code = code
        reason = _BAD_MESSAGE_CODES.get(code, "the server did not say why")
        super().__init__(f"the server rejected the message ({code}): {reason}")


class NoAnswer(SunnygramError):
    """No one answered a question inside the time it was given.

    Raised by the conversation helpers instead of returned as None, because a
    question that went unanswered is nearly always a different path through the
    program than one that was answered, and a None that is not checked for goes
    on to fail somewhere further away with less to say for itself.
    """


class PeerNotFound(SunnygramError):
    """Nothing known can name this person or chat to the server.

    MTProto refers to almost everyone by an id and an access hash together, and
    the hash is only ever learned by being told it. So this is not the server
    saying no: it is the client saying it has never seen this peer and has no
    way to ask about it. Resolving a username, or anything that makes the peer
    arrive alongside an update, fixes it for good.
    """


class UploadRefused(SunnygramError):
    """The server said no to a part of an upload without saying why.

    saveFilePart answers with a plain boolean, so a false is the whole of the
    detail. It should not happen: anything with a reason arrives as an RPC
    error instead, which is why this one carries the part number.
    """

    def __init__(self, part: int) -> None:
        self.part = part
        super().__init__(f"the server refused part {part} of this upload")


class FileTooLarge(SunnygramError):
    """A download turned out to be bigger than the caller allowed for."""


class TransportError(SunnygramError):
    """Something went wrong below MTProto, on the connection itself."""


class TransportClosed(TransportError):
    """The connection ended, possibly in the middle of a packet."""


class ProxyError(TransportError):
    """The proxy is the thing that went wrong, rather than Telegram.

    Worth telling apart, because the two ask for opposite responses. A
    datacenter that refuses is retried or migrated away from; a proxy that
    refuses will refuse again, and what has to change is the configuration.
    """


class MalformedFrame(TransportError):
    """The framing does not hold up: an impossible length, a bad checksum, or
    a packet arriving out of order.

    Treated as fatal for the connection instead of skipped, because there is
    no way to find where the next packet starts once the stream is off by a byte.
    """


class TransportRejected(TransportError):
    """The server answered with an error code in place of a packet."""

    def __init__(self, code: int) -> None:
        self.code = code
        reason = _TRANSPORT_CODES.get(code)
        super().__init__(
            f"the server rejected the connection with {code}"
            + (f": {reason}" if reason else "")
        )


class UnknownConstructorError(TLDeserializationError):
    """A constructor id that no known type claims.

    Usually means the pinned schema layer is older than the server's.
    """

    def __init__(self, constructor_id: int) -> None:
        self.constructor_id = constructor_id
        super().__init__(f"unknown constructor 0x{constructor_id:08x}")
