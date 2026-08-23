# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the ephemeral namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class SendMessage(TLFunction["base.Updates"]):
    """The TL function ephemeral.sendMessage#68cbd09f, answered with Updates."""

    __slots__ = ("peer", "receiver_id", "query_id", "message", "entities", "media", "reply_markup", "rich_message", "random_id", "reply_to",)

    ID = 0x68CBD09F
    QUALNAME = "functions.ephemeral.SendMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        receiver_id: base.InputUser,
        query_id: int | None = None,
        message: str,
        entities: list[base.MessageEntity] | None = None,
        media: base.InputMedia | None = None,
        reply_markup: base.ReplyMarkup | None = None,
        rich_message: base.InputRichMessage | None = None,
        random_id: int,
        reply_to: base.InputReplyTo | None = None,
    ) -> None:
        self.peer = peer
        self.receiver_id = receiver_id
        self.query_id = query_id
        self.message = message
        self.entities = entities
        self.media = media
        self.reply_markup = reply_markup
        self.rich_message = rich_message
        self.random_id = random_id
        self.reply_to = reply_to

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.query_id is not None:
            flags |= 1 << 0
        if self.entities is not None:
            flags |= 1 << 1
        if self.media is not None:
            flags |= 1 << 2
        if self.reply_markup is not None:
            flags |= 1 << 3
        if self.rich_message is not None:
            flags |= 1 << 4
        if self.reply_to is not None:
            flags |= 1 << 5
        w.write_int(flags)
        self.peer.write(w)
        self.receiver_id.write(w)
        if self.query_id is not None:
            w.write_long(self.query_id)
        w.write_string(self.message)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.media is not None:
            self.media.write(w)
        if self.reply_markup is not None:
            self.reply_markup.write(w)
        if self.rich_message is not None:
            self.rich_message.write(w)
        w.write_long(self.random_id)
        if self.reply_to is not None:
            self.reply_to.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        receiver_id = r.read_object()
        query_id = r.read_long() if flags & (1 << 0) else None
        message = r.read_string()
        entities = r.read_vector() if flags & (1 << 1) else None
        media = r.read_object() if flags & (1 << 2) else None
        reply_markup = r.read_object() if flags & (1 << 3) else None
        rich_message = r.read_object() if flags & (1 << 4) else None
        random_id = r.read_long()
        reply_to = r.read_object() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.receiver_id = receiver_id
        self.query_id = query_id
        self.message = message
        self.entities = entities
        self.media = media
        self.reply_markup = reply_markup
        self.rich_message = rich_message
        self.random_id = random_id
        self.reply_to = reply_to
        return self


class DeleteMessage(TLFunction["bool"]):
    """The TL function ephemeral.deleteMessage#a3c0d511, answered with Bool."""

    __slots__ = ("peer", "receiver_id", "id",)

    ID = 0xA3C0D511
    QUALNAME = "functions.ephemeral.DeleteMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        receiver_id: base.InputUser,
        id: int,
    ) -> None:
        self.peer = peer
        self.receiver_id = receiver_id
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.receiver_id.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        receiver_id = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.receiver_id = receiver_id
        self.id = id
        return self


class ReportMessage(TLFunction["base.ReportResult"]):
    """The TL function ephemeral.reportMessage#8704f2bf, answered with ReportResult."""

    __slots__ = ("peer", "id", "option", "message",)

    ID = 0x8704F2BF
    QUALNAME = "functions.ephemeral.ReportMessage"
    RESULT = "ReportResult"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        option: bytes,
        message: str,
    ) -> None:
        self.peer = peer
        self.id = id
        self.option = option
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)
        w.write_bytes(self.option)
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        option = r.read_bytes()
        message = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.option = option
        self.message = message
        return self


class GetCallbackAnswer(TLFunction["base.messages.BotCallbackAnswer"]):
    """The TL function ephemeral.getCallbackAnswer#3fa464c8, answered with messages.BotCallbackAnswer."""

    __slots__ = ("peer", "id", "data",)

    ID = 0x3FA464C8
    QUALNAME = "functions.ephemeral.GetCallbackAnswer"
    RESULT = "messages.BotCallbackAnswer"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        data: bytes | None = None,
    ) -> None:
        self.peer = peer
        self.id = id
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.data is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.data is not None:
            w.write_bytes(self.data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        id = r.read_int()
        data = r.read_bytes() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.data = data
        return self
