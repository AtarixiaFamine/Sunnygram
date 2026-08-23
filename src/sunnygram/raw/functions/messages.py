# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the messages namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

import struct

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class GetMessages(TLFunction["base.messages.Messages"]):
    """The TL function messages.getMessages#63c66506, answered with messages.Messages."""

    __slots__ = ("id",)

    ID = 0x63C66506
    QUALNAME = "functions.messages.GetMessages"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        id: list[base.InputMessage],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector()
        self = cls.__new__(cls)
        self.id = id
        return self


class GetDialogs(TLFunction["base.messages.Dialogs"]):
    """The TL function messages.getDialogs#a0f4cb4f, answered with messages.Dialogs."""

    __slots__ = ("exclude_pinned", "folder_id", "offset_date", "offset_id", "offset_peer", "limit", "hash",)

    ID = 0xA0F4CB4F
    QUALNAME = "functions.messages.GetDialogs"
    RESULT = "messages.Dialogs"

    def __init__(
        self,
        *,
        exclude_pinned: bool = False,
        folder_id: int | None = None,
        offset_date: int,
        offset_id: int,
        offset_peer: base.InputPeer,
        limit: int,
        hash: int,
    ) -> None:
        self.exclude_pinned = exclude_pinned
        self.folder_id = folder_id
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_peer = offset_peer
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.exclude_pinned:
            flags |= 1 << 0
        if self.folder_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.folder_id is not None:
            w.write_int(self.folder_id)
        w.write_int(self.offset_date)
        w.write_int(self.offset_id)
        self.offset_peer.write(w)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        exclude_pinned = bool(flags & (1 << 0))
        folder_id = r.read_int() if flags & (1 << 1) else None
        offset_date = r.read_int()
        offset_id = r.read_int()
        offset_peer = r.read_object()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.exclude_pinned = exclude_pinned
        self.folder_id = folder_id
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_peer = offset_peer
        self.limit = limit
        self.hash = hash
        return self


class GetHistory(TLFunction["base.messages.Messages"]):
    """The TL function messages.getHistory#4423e6c5, answered with messages.Messages."""

    __slots__ = ("peer", "offset_id", "offset_date", "add_offset", "limit", "max_id", "min_id", "hash",)

    ID = 0x4423E6C5
    QUALNAME = "functions.messages.GetHistory"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        offset_id: int,
        offset_date: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
        hash: int,
    ) -> None:
        self.peer = peer
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.offset_date)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        offset_id = r.read_int()
        offset_date = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash
        return self


class Search(TLFunction["base.messages.Messages"]):
    """The TL function messages.search#29ee847a, answered with messages.Messages."""

    __slots__ = ("peer", "q", "from_id", "saved_peer_id", "saved_reaction", "top_msg_id", "filter", "min_date", "max_date", "offset_id", "add_offset", "limit", "max_id", "min_id", "hash",)

    ID = 0x29EE847A
    QUALNAME = "functions.messages.Search"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        q: str,
        from_id: base.InputPeer | None = None,
        saved_peer_id: base.InputPeer | None = None,
        saved_reaction: list[base.Reaction] | None = None,
        top_msg_id: int | None = None,
        filter: base.MessagesFilter,
        min_date: int,
        max_date: int,
        offset_id: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
        hash: int,
    ) -> None:
        self.peer = peer
        self.q = q
        self.from_id = from_id
        self.saved_peer_id = saved_peer_id
        self.saved_reaction = saved_reaction
        self.top_msg_id = top_msg_id
        self.filter = filter
        self.min_date = min_date
        self.max_date = max_date
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.from_id is not None:
            flags |= 1 << 0
        if self.saved_peer_id is not None:
            flags |= 1 << 2
        if self.saved_reaction is not None:
            flags |= 1 << 3
        if self.top_msg_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.q)
        if self.from_id is not None:
            self.from_id.write(w)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)
        if self.saved_reaction is not None:
            w.write_vector(self.saved_reaction)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        self.filter.write(w)
        w.write_int(self.min_date)
        w.write_int(self.max_date)
        w.write_int(self.offset_id)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        q = r.read_string()
        from_id = r.read_object() if flags & (1 << 0) else None
        saved_peer_id = r.read_object() if flags & (1 << 2) else None
        saved_reaction = r.read_vector() if flags & (1 << 3) else None
        top_msg_id = r.read_int() if flags & (1 << 1) else None
        filter = r.read_object()
        min_date = r.read_int()
        max_date = r.read_int()
        offset_id = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.q = q
        self.from_id = from_id
        self.saved_peer_id = saved_peer_id
        self.saved_reaction = saved_reaction
        self.top_msg_id = top_msg_id
        self.filter = filter
        self.min_date = min_date
        self.max_date = max_date
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash
        return self


class ReadHistory(TLFunction["base.messages.AffectedMessages"]):
    """The TL function messages.readHistory#0e306d3a, answered with messages.AffectedMessages."""

    __slots__ = ("peer", "max_id",)

    ID = 0x0E306D3A
    QUALNAME = "functions.messages.ReadHistory"
    RESULT = "messages.AffectedMessages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        max_id: int,
    ) -> None:
        self.peer = peer
        self.max_id = max_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        max_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.max_id = max_id
        return self


class DeleteHistory(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.deleteHistory#b08f922a, answered with messages.AffectedHistory."""

    __slots__ = ("just_clear", "revoke", "peer", "max_id", "min_date", "max_date",)

    ID = 0xB08F922A
    QUALNAME = "functions.messages.DeleteHistory"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        just_clear: bool = False,
        revoke: bool = False,
        peer: base.InputPeer,
        max_id: int,
        min_date: int | None = None,
        max_date: int | None = None,
    ) -> None:
        self.just_clear = just_clear
        self.revoke = revoke
        self.peer = peer
        self.max_id = max_id
        self.min_date = min_date
        self.max_date = max_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.just_clear:
            flags |= 1 << 0
        if self.revoke:
            flags |= 1 << 1
        if self.min_date is not None:
            flags |= 1 << 2
        if self.max_date is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.max_id)
        if self.min_date is not None:
            w.write_int(self.min_date)
        if self.max_date is not None:
            w.write_int(self.max_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        just_clear = bool(flags & (1 << 0))
        revoke = bool(flags & (1 << 1))
        peer = r.read_object()
        max_id = r.read_int()
        min_date = r.read_int() if flags & (1 << 2) else None
        max_date = r.read_int() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.just_clear = just_clear
        self.revoke = revoke
        self.peer = peer
        self.max_id = max_id
        self.min_date = min_date
        self.max_date = max_date
        return self


class DeleteMessages(TLFunction["base.messages.AffectedMessages"]):
    """The TL function messages.deleteMessages#e58e95d2, answered with messages.AffectedMessages."""

    __slots__ = ("revoke", "id",)

    ID = 0xE58E95D2
    QUALNAME = "functions.messages.DeleteMessages"
    RESULT = "messages.AffectedMessages"

    def __init__(
        self,
        *,
        revoke: bool = False,
        id: list[int],
    ) -> None:
        self.revoke = revoke
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoke:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoke = bool(flags & (1 << 0))
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.revoke = revoke
        self.id = id
        return self


class ReceivedMessages(TLFunction["list[base.ReceivedNotifyMessage]"]):
    """The TL function messages.receivedMessages#05a954c0, answered with Vector<ReceivedNotifyMessage>."""

    __slots__ = ("max_id",)

    ID = 0x05A954C0
    QUALNAME = "functions.messages.ReceivedMessages"
    RESULT = "Vector<ReceivedNotifyMessage>"

    def __init__(
        self,
        *,
        max_id: int,
    ) -> None:
        self.max_id = max_id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        max_id = r.read_int()
        self = cls.__new__(cls)
        self.max_id = max_id
        return self


class SetTyping(TLFunction["bool"]):
    """The TL function messages.setTyping#58943ee2, answered with Bool."""

    __slots__ = ("peer", "top_msg_id", "action",)

    ID = 0x58943EE2
    QUALNAME = "functions.messages.SetTyping"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        action: base.SendMessageAction,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.action = action

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        self.action.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        action = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.action = action
        return self


class SendMessage(TLFunction["base.Updates"]):
    """The TL function messages.sendMessage#fef48f62, answered with Updates."""

    __slots__ = ("no_webpage", "silent", "background", "clear_draft", "noforwards", "update_stickersets_order", "invert_media", "allow_paid_floodskip", "peer", "reply_to", "message", "random_id", "reply_markup", "entities", "schedule_date", "schedule_repeat_period", "send_as", "quick_reply_shortcut", "effect", "allow_paid_stars", "suggested_post", "rich_message",)

    ID = 0xFEF48F62
    QUALNAME = "functions.messages.SendMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        no_webpage: bool = False,
        silent: bool = False,
        background: bool = False,
        clear_draft: bool = False,
        noforwards: bool = False,
        update_stickersets_order: bool = False,
        invert_media: bool = False,
        allow_paid_floodskip: bool = False,
        peer: base.InputPeer,
        reply_to: base.InputReplyTo | None = None,
        message: str,
        random_id: int,
        reply_markup: base.ReplyMarkup | None = None,
        entities: list[base.MessageEntity] | None = None,
        schedule_date: int | None = None,
        schedule_repeat_period: int | None = None,
        send_as: base.InputPeer | None = None,
        quick_reply_shortcut: base.InputQuickReplyShortcut | None = None,
        effect: int | None = None,
        allow_paid_stars: int | None = None,
        suggested_post: base.SuggestedPost | None = None,
        rich_message: base.InputRichMessage | None = None,
    ) -> None:
        self.no_webpage = no_webpage
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.message = message
        self.random_id = random_id
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post
        self.rich_message = rich_message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_webpage:
            flags |= 1 << 1
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.clear_draft:
            flags |= 1 << 7
        if self.noforwards:
            flags |= 1 << 14
        if self.update_stickersets_order:
            flags |= 1 << 15
        if self.invert_media:
            flags |= 1 << 16
        if self.allow_paid_floodskip:
            flags |= 1 << 19
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.reply_markup is not None:
            flags |= 1 << 2
        if self.entities is not None:
            flags |= 1 << 3
        if self.schedule_date is not None:
            flags |= 1 << 10
        if self.schedule_repeat_period is not None:
            flags |= 1 << 24
        if self.send_as is not None:
            flags |= 1 << 13
        if self.quick_reply_shortcut is not None:
            flags |= 1 << 17
        if self.effect is not None:
            flags |= 1 << 18
        if self.allow_paid_stars is not None:
            flags |= 1 << 21
        if self.suggested_post is not None:
            flags |= 1 << 22
        if self.rich_message is not None:
            flags |= 1 << 23
        w.write_int(flags)
        self.peer.write(w)
        if self.reply_to is not None:
            self.reply_to.write(w)
        w.write_string(self.message)
        w.write_long(self.random_id)
        if self.reply_markup is not None:
            self.reply_markup.write(w)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.schedule_repeat_period is not None:
            w.write_int(self.schedule_repeat_period)
        if self.send_as is not None:
            self.send_as.write(w)
        if self.quick_reply_shortcut is not None:
            self.quick_reply_shortcut.write(w)
        if self.effect is not None:
            w.write_long(self.effect)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)
        if self.suggested_post is not None:
            self.suggested_post.write(w)
        if self.rich_message is not None:
            self.rich_message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_webpage = bool(flags & (1 << 1))
        silent = bool(flags & (1 << 5))
        background = bool(flags & (1 << 6))
        clear_draft = bool(flags & (1 << 7))
        noforwards = bool(flags & (1 << 14))
        update_stickersets_order = bool(flags & (1 << 15))
        invert_media = bool(flags & (1 << 16))
        allow_paid_floodskip = bool(flags & (1 << 19))
        peer = r.read_object()
        reply_to = r.read_object() if flags & (1 << 0) else None
        message = r.read_string()
        random_id = r.read_long()
        reply_markup = r.read_object() if flags & (1 << 2) else None
        entities = r.read_vector() if flags & (1 << 3) else None
        schedule_date = r.read_int() if flags & (1 << 10) else None
        schedule_repeat_period = r.read_int() if flags & (1 << 24) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        quick_reply_shortcut = r.read_object() if flags & (1 << 17) else None
        effect = r.read_long() if flags & (1 << 18) else None
        allow_paid_stars = r.read_long() if flags & (1 << 21) else None
        suggested_post = r.read_object() if flags & (1 << 22) else None
        rich_message = r.read_object() if flags & (1 << 23) else None
        self = cls.__new__(cls)
        self.no_webpage = no_webpage
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.message = message
        self.random_id = random_id
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post
        self.rich_message = rich_message
        return self


class SendMedia(TLFunction["base.Updates"]):
    """The TL function messages.sendMedia#0330e77f, answered with Updates."""

    __slots__ = ("silent", "background", "clear_draft", "noforwards", "update_stickersets_order", "invert_media", "allow_paid_floodskip", "peer", "reply_to", "media", "message", "random_id", "reply_markup", "entities", "schedule_date", "schedule_repeat_period", "send_as", "quick_reply_shortcut", "effect", "allow_paid_stars", "suggested_post",)

    ID = 0x0330E77F
    QUALNAME = "functions.messages.SendMedia"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        silent: bool = False,
        background: bool = False,
        clear_draft: bool = False,
        noforwards: bool = False,
        update_stickersets_order: bool = False,
        invert_media: bool = False,
        allow_paid_floodskip: bool = False,
        peer: base.InputPeer,
        reply_to: base.InputReplyTo | None = None,
        media: base.InputMedia,
        message: str,
        random_id: int,
        reply_markup: base.ReplyMarkup | None = None,
        entities: list[base.MessageEntity] | None = None,
        schedule_date: int | None = None,
        schedule_repeat_period: int | None = None,
        send_as: base.InputPeer | None = None,
        quick_reply_shortcut: base.InputQuickReplyShortcut | None = None,
        effect: int | None = None,
        allow_paid_stars: int | None = None,
        suggested_post: base.SuggestedPost | None = None,
    ) -> None:
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.media = media
        self.message = message
        self.random_id = random_id
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.clear_draft:
            flags |= 1 << 7
        if self.noforwards:
            flags |= 1 << 14
        if self.update_stickersets_order:
            flags |= 1 << 15
        if self.invert_media:
            flags |= 1 << 16
        if self.allow_paid_floodskip:
            flags |= 1 << 19
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.reply_markup is not None:
            flags |= 1 << 2
        if self.entities is not None:
            flags |= 1 << 3
        if self.schedule_date is not None:
            flags |= 1 << 10
        if self.schedule_repeat_period is not None:
            flags |= 1 << 24
        if self.send_as is not None:
            flags |= 1 << 13
        if self.quick_reply_shortcut is not None:
            flags |= 1 << 17
        if self.effect is not None:
            flags |= 1 << 18
        if self.allow_paid_stars is not None:
            flags |= 1 << 21
        if self.suggested_post is not None:
            flags |= 1 << 22
        w.write_int(flags)
        self.peer.write(w)
        if self.reply_to is not None:
            self.reply_to.write(w)
        self.media.write(w)
        w.write_string(self.message)
        w.write_long(self.random_id)
        if self.reply_markup is not None:
            self.reply_markup.write(w)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.schedule_repeat_period is not None:
            w.write_int(self.schedule_repeat_period)
        if self.send_as is not None:
            self.send_as.write(w)
        if self.quick_reply_shortcut is not None:
            self.quick_reply_shortcut.write(w)
        if self.effect is not None:
            w.write_long(self.effect)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)
        if self.suggested_post is not None:
            self.suggested_post.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 5))
        background = bool(flags & (1 << 6))
        clear_draft = bool(flags & (1 << 7))
        noforwards = bool(flags & (1 << 14))
        update_stickersets_order = bool(flags & (1 << 15))
        invert_media = bool(flags & (1 << 16))
        allow_paid_floodskip = bool(flags & (1 << 19))
        peer = r.read_object()
        reply_to = r.read_object() if flags & (1 << 0) else None
        media = r.read_object()
        message = r.read_string()
        random_id = r.read_long()
        reply_markup = r.read_object() if flags & (1 << 2) else None
        entities = r.read_vector() if flags & (1 << 3) else None
        schedule_date = r.read_int() if flags & (1 << 10) else None
        schedule_repeat_period = r.read_int() if flags & (1 << 24) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        quick_reply_shortcut = r.read_object() if flags & (1 << 17) else None
        effect = r.read_long() if flags & (1 << 18) else None
        allow_paid_stars = r.read_long() if flags & (1 << 21) else None
        suggested_post = r.read_object() if flags & (1 << 22) else None
        self = cls.__new__(cls)
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.media = media
        self.message = message
        self.random_id = random_id
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post
        return self


class ForwardMessages(TLFunction["base.Updates"]):
    """The TL function messages.forwardMessages#13704a7c, answered with Updates."""

    __slots__ = ("silent", "background", "with_my_score", "drop_author", "drop_media_captions", "noforwards", "allow_paid_floodskip", "from_peer", "id", "random_id", "to_peer", "top_msg_id", "reply_to", "schedule_date", "schedule_repeat_period", "send_as", "quick_reply_shortcut", "effect", "video_timestamp", "allow_paid_stars", "suggested_post",)

    ID = 0x13704A7C
    QUALNAME = "functions.messages.ForwardMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        silent: bool = False,
        background: bool = False,
        with_my_score: bool = False,
        drop_author: bool = False,
        drop_media_captions: bool = False,
        noforwards: bool = False,
        allow_paid_floodskip: bool = False,
        from_peer: base.InputPeer,
        id: list[int],
        random_id: list[int],
        to_peer: base.InputPeer,
        top_msg_id: int | None = None,
        reply_to: base.InputReplyTo | None = None,
        schedule_date: int | None = None,
        schedule_repeat_period: int | None = None,
        send_as: base.InputPeer | None = None,
        quick_reply_shortcut: base.InputQuickReplyShortcut | None = None,
        effect: int | None = None,
        video_timestamp: int | None = None,
        allow_paid_stars: int | None = None,
        suggested_post: base.SuggestedPost | None = None,
    ) -> None:
        self.silent = silent
        self.background = background
        self.with_my_score = with_my_score
        self.drop_author = drop_author
        self.drop_media_captions = drop_media_captions
        self.noforwards = noforwards
        self.allow_paid_floodskip = allow_paid_floodskip
        self.from_peer = from_peer
        self.id = id
        self.random_id = random_id
        self.to_peer = to_peer
        self.top_msg_id = top_msg_id
        self.reply_to = reply_to
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.video_timestamp = video_timestamp
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.with_my_score:
            flags |= 1 << 8
        if self.drop_author:
            flags |= 1 << 11
        if self.drop_media_captions:
            flags |= 1 << 12
        if self.noforwards:
            flags |= 1 << 14
        if self.allow_paid_floodskip:
            flags |= 1 << 19
        if self.top_msg_id is not None:
            flags |= 1 << 9
        if self.reply_to is not None:
            flags |= 1 << 22
        if self.schedule_date is not None:
            flags |= 1 << 10
        if self.schedule_repeat_period is not None:
            flags |= 1 << 24
        if self.send_as is not None:
            flags |= 1 << 13
        if self.quick_reply_shortcut is not None:
            flags |= 1 << 17
        if self.effect is not None:
            flags |= 1 << 18
        if self.video_timestamp is not None:
            flags |= 1 << 20
        if self.allow_paid_stars is not None:
            flags |= 1 << 21
        if self.suggested_post is not None:
            flags |= 1 << 23
        w.write_int(flags)
        self.from_peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)
        w.write_vector(self.random_id, TLWriter.write_long)
        self.to_peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        if self.reply_to is not None:
            self.reply_to.write(w)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.schedule_repeat_period is not None:
            w.write_int(self.schedule_repeat_period)
        if self.send_as is not None:
            self.send_as.write(w)
        if self.quick_reply_shortcut is not None:
            self.quick_reply_shortcut.write(w)
        if self.effect is not None:
            w.write_long(self.effect)
        if self.video_timestamp is not None:
            w.write_int(self.video_timestamp)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)
        if self.suggested_post is not None:
            self.suggested_post.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 5))
        background = bool(flags & (1 << 6))
        with_my_score = bool(flags & (1 << 8))
        drop_author = bool(flags & (1 << 11))
        drop_media_captions = bool(flags & (1 << 12))
        noforwards = bool(flags & (1 << 14))
        allow_paid_floodskip = bool(flags & (1 << 19))
        from_peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        random_id = r.read_vector(TLReader.read_long)
        to_peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 9) else None
        reply_to = r.read_object() if flags & (1 << 22) else None
        schedule_date = r.read_int() if flags & (1 << 10) else None
        schedule_repeat_period = r.read_int() if flags & (1 << 24) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        quick_reply_shortcut = r.read_object() if flags & (1 << 17) else None
        effect = r.read_long() if flags & (1 << 18) else None
        video_timestamp = r.read_int() if flags & (1 << 20) else None
        allow_paid_stars = r.read_long() if flags & (1 << 21) else None
        suggested_post = r.read_object() if flags & (1 << 23) else None
        self = cls.__new__(cls)
        self.silent = silent
        self.background = background
        self.with_my_score = with_my_score
        self.drop_author = drop_author
        self.drop_media_captions = drop_media_captions
        self.noforwards = noforwards
        self.allow_paid_floodskip = allow_paid_floodskip
        self.from_peer = from_peer
        self.id = id
        self.random_id = random_id
        self.to_peer = to_peer
        self.top_msg_id = top_msg_id
        self.reply_to = reply_to
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.video_timestamp = video_timestamp
        self.allow_paid_stars = allow_paid_stars
        self.suggested_post = suggested_post
        return self


class ReportSpam(TLFunction["bool"]):
    """The TL function messages.reportSpam#cf1592db, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0xCF1592DB
    QUALNAME = "functions.messages.ReportSpam"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class GetPeerSettings(TLFunction["base.messages.PeerSettings"]):
    """The TL function messages.getPeerSettings#efd9a6a2, answered with messages.PeerSettings."""

    __slots__ = ("peer",)

    ID = 0xEFD9A6A2
    QUALNAME = "functions.messages.GetPeerSettings"
    RESULT = "messages.PeerSettings"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class Report(TLFunction["base.ReportResult"]):
    """The TL function messages.report#fc78af9b, answered with ReportResult."""

    __slots__ = ("peer", "id", "option", "message",)

    ID = 0xFC78AF9B
    QUALNAME = "functions.messages.Report"
    RESULT = "ReportResult"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
        option: bytes,
        message: str,
    ) -> None:
        self.peer = peer
        self.id = id
        self.option = option
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)
        w.write_bytes(self.option)
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        option = r.read_bytes()
        message = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.option = option
        self.message = message
        return self


class GetChats(TLFunction["base.messages.Chats"]):
    """The TL function messages.getChats#49e9528f, answered with messages.Chats."""

    __slots__ = ("id",)

    ID = 0x49E9528F
    QUALNAME = "functions.messages.GetChats"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        id: list[int],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.id = id
        return self


class GetFullChat(TLFunction["base.messages.ChatFull"]):
    """The TL function messages.getFullChat#aeb00b34, answered with messages.ChatFull."""

    __slots__ = ("chat_id",)

    ID = 0xAEB00B34
    QUALNAME = "functions.messages.GetFullChat"
    RESULT = "messages.ChatFull"

    def __init__(
        self,
        *,
        chat_id: int,
    ) -> None:
        self.chat_id = chat_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        return self


class EditChatTitle(TLFunction["base.Updates"]):
    """The TL function messages.editChatTitle#73783ffd, answered with Updates."""

    __slots__ = ("chat_id", "title",)

    ID = 0x73783FFD
    QUALNAME = "functions.messages.EditChatTitle"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        chat_id: int,
        title: str,
    ) -> None:
        self.chat_id = chat_id
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)
        w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        title = r.read_string()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        self.title = title
        return self


class EditChatPhoto(TLFunction["base.Updates"]):
    """The TL function messages.editChatPhoto#35ddd674, answered with Updates."""

    __slots__ = ("chat_id", "photo",)

    ID = 0x35DDD674
    QUALNAME = "functions.messages.EditChatPhoto"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        chat_id: int,
        photo: base.InputChatPhoto,
    ) -> None:
        self.chat_id = chat_id
        self.photo = photo

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)
        self.photo.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        photo = r.read_object()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        self.photo = photo
        return self


class AddChatUser(TLFunction["base.messages.InvitedUsers"]):
    """The TL function messages.addChatUser#cbc6d107, answered with messages.InvitedUsers."""

    __slots__ = ("chat_id", "user_id", "fwd_limit",)

    ID = 0xCBC6D107
    QUALNAME = "functions.messages.AddChatUser"
    RESULT = "messages.InvitedUsers"

    def __init__(
        self,
        *,
        chat_id: int,
        user_id: base.InputUser,
        fwd_limit: int,
    ) -> None:
        self.chat_id = chat_id
        self.user_id = user_id
        self.fwd_limit = fwd_limit

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)
        self.user_id.write(w)
        w.write_int(self.fwd_limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        user_id = r.read_object()
        fwd_limit = r.read_int()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        self.user_id = user_id
        self.fwd_limit = fwd_limit
        return self


class DeleteChatUser(TLFunction["base.Updates"]):
    """The TL function messages.deleteChatUser#a2185cab, answered with Updates."""

    __slots__ = ("revoke_history", "chat_id", "user_id",)

    ID = 0xA2185CAB
    QUALNAME = "functions.messages.DeleteChatUser"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        revoke_history: bool = False,
        chat_id: int,
        user_id: base.InputUser,
    ) -> None:
        self.revoke_history = revoke_history
        self.chat_id = chat_id
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoke_history:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.chat_id)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoke_history = bool(flags & (1 << 0))
        chat_id = r.read_long()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.revoke_history = revoke_history
        self.chat_id = chat_id
        self.user_id = user_id
        return self


class CreateChat(TLFunction["base.messages.InvitedUsers"]):
    """The TL function messages.createChat#92ceddd4, answered with messages.InvitedUsers."""

    __slots__ = ("users", "title", "ttl_period",)

    ID = 0x92CEDDD4
    QUALNAME = "functions.messages.CreateChat"
    RESULT = "messages.InvitedUsers"

    def __init__(
        self,
        *,
        users: list[base.InputUser],
        title: str,
        ttl_period: int | None = None,
    ) -> None:
        self.users = users
        self.title = title
        self.ttl_period = ttl_period

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.ttl_period is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.users)
        w.write_string(self.title)
        if self.ttl_period is not None:
            w.write_int(self.ttl_period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        users = r.read_vector()
        title = r.read_string()
        ttl_period = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.users = users
        self.title = title
        self.ttl_period = ttl_period
        return self


_PACK_GetDhConfig = struct.Struct("<ii")


class GetDhConfig(TLFunction["base.messages.DhConfig"]):
    """The TL function messages.getDhConfig#26cf8950, answered with messages.DhConfig."""

    __slots__ = ("version", "random_length",)

    ID = 0x26CF8950
    QUALNAME = "functions.messages.GetDhConfig"
    RESULT = "messages.DhConfig"

    def __init__(
        self,
        *,
        version: int,
        random_length: int,
    ) -> None:
        self.version = version
        self.random_length = random_length

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_GetDhConfig.pack(self.version, self.random_length))
        except struct.error:
            w.write_int(self.version)
            w.write_int(self.random_length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        version = r.read_int()
        random_length = r.read_int()
        self = cls.__new__(cls)
        self.version = version
        self.random_length = random_length
        return self


class RequestEncryption(TLFunction["base.EncryptedChat"]):
    """The TL function messages.requestEncryption#f64daf43, answered with EncryptedChat."""

    __slots__ = ("user_id", "random_id", "g_a",)

    ID = 0xF64DAF43
    QUALNAME = "functions.messages.RequestEncryption"
    RESULT = "EncryptedChat"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        random_id: int,
        g_a: bytes,
    ) -> None:
        self.user_id = user_id
        self.random_id = random_id
        self.g_a = g_a

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_int(self.random_id)
        w.write_bytes(self.g_a)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        random_id = r.read_int()
        g_a = r.read_bytes()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.random_id = random_id
        self.g_a = g_a
        return self


class AcceptEncryption(TLFunction["base.EncryptedChat"]):
    """The TL function messages.acceptEncryption#3dbc0415, answered with EncryptedChat."""

    __slots__ = ("peer", "g_b", "key_fingerprint",)

    ID = 0x3DBC0415
    QUALNAME = "functions.messages.AcceptEncryption"
    RESULT = "EncryptedChat"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
        g_b: bytes,
        key_fingerprint: int,
    ) -> None:
        self.peer = peer
        self.g_b = g_b
        self.key_fingerprint = key_fingerprint

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bytes(self.g_b)
        w.write_long(self.key_fingerprint)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        g_b = r.read_bytes()
        key_fingerprint = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.g_b = g_b
        self.key_fingerprint = key_fingerprint
        return self


class DiscardEncryption(TLFunction["bool"]):
    """The TL function messages.discardEncryption#f393aea0, answered with Bool."""

    __slots__ = ("delete_history", "chat_id",)

    ID = 0xF393AEA0
    QUALNAME = "functions.messages.DiscardEncryption"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        delete_history: bool = False,
        chat_id: int,
    ) -> None:
        self.delete_history = delete_history
        self.chat_id = chat_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.delete_history:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.chat_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        delete_history = bool(flags & (1 << 0))
        chat_id = r.read_int()
        self = cls.__new__(cls)
        self.delete_history = delete_history
        self.chat_id = chat_id
        return self


class SetEncryptedTyping(TLFunction["bool"]):
    """The TL function messages.setEncryptedTyping#791451ed, answered with Bool."""

    __slots__ = ("peer", "typing",)

    ID = 0x791451ED
    QUALNAME = "functions.messages.SetEncryptedTyping"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
        typing: bool,
    ) -> None:
        self.peer = peer
        self.typing = typing

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bool(self.typing)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        typing = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.typing = typing
        return self


class ReadEncryptedHistory(TLFunction["bool"]):
    """The TL function messages.readEncryptedHistory#7f4b690a, answered with Bool."""

    __slots__ = ("peer", "max_date",)

    ID = 0x7F4B690A
    QUALNAME = "functions.messages.ReadEncryptedHistory"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
        max_date: int,
    ) -> None:
        self.peer = peer
        self.max_date = max_date

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.max_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        max_date = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.max_date = max_date
        return self


class SendEncrypted(TLFunction["base.messages.SentEncryptedMessage"]):
    """The TL function messages.sendEncrypted#44fa7a15, answered with messages.SentEncryptedMessage."""

    __slots__ = ("silent", "peer", "random_id", "data",)

    ID = 0x44FA7A15
    QUALNAME = "functions.messages.SendEncrypted"
    RESULT = "messages.SentEncryptedMessage"

    def __init__(
        self,
        *,
        silent: bool = False,
        peer: base.InputEncryptedChat,
        random_id: int,
        data: bytes,
    ) -> None:
        self.silent = silent
        self.peer = peer
        self.random_id = random_id
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_long(self.random_id)
        w.write_bytes(self.data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 0))
        peer = r.read_object()
        random_id = r.read_long()
        data = r.read_bytes()
        self = cls.__new__(cls)
        self.silent = silent
        self.peer = peer
        self.random_id = random_id
        self.data = data
        return self


class SendEncryptedFile(TLFunction["base.messages.SentEncryptedMessage"]):
    """The TL function messages.sendEncryptedFile#5559481d, answered with messages.SentEncryptedMessage."""

    __slots__ = ("silent", "peer", "random_id", "data", "file",)

    ID = 0x5559481D
    QUALNAME = "functions.messages.SendEncryptedFile"
    RESULT = "messages.SentEncryptedMessage"

    def __init__(
        self,
        *,
        silent: bool = False,
        peer: base.InputEncryptedChat,
        random_id: int,
        data: bytes,
        file: base.InputEncryptedFile,
    ) -> None:
        self.silent = silent
        self.peer = peer
        self.random_id = random_id
        self.data = data
        self.file = file

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_long(self.random_id)
        w.write_bytes(self.data)
        self.file.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 0))
        peer = r.read_object()
        random_id = r.read_long()
        data = r.read_bytes()
        file = r.read_object()
        self = cls.__new__(cls)
        self.silent = silent
        self.peer = peer
        self.random_id = random_id
        self.data = data
        self.file = file
        return self


class SendEncryptedService(TLFunction["base.messages.SentEncryptedMessage"]):
    """The TL function messages.sendEncryptedService#32d439a4, answered with messages.SentEncryptedMessage."""

    __slots__ = ("peer", "random_id", "data",)

    ID = 0x32D439A4
    QUALNAME = "functions.messages.SendEncryptedService"
    RESULT = "messages.SentEncryptedMessage"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
        random_id: int,
        data: bytes,
    ) -> None:
        self.peer = peer
        self.random_id = random_id
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.random_id)
        w.write_bytes(self.data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        random_id = r.read_long()
        data = r.read_bytes()
        self = cls.__new__(cls)
        self.peer = peer
        self.random_id = random_id
        self.data = data
        return self


class ReceivedQueue(TLFunction["list[int]"]):
    """The TL function messages.receivedQueue#55a5bb66, answered with Vector<long>."""

    __slots__ = ("max_qts",)

    ID = 0x55A5BB66
    QUALNAME = "functions.messages.ReceivedQueue"
    RESULT = "Vector<long>"

    def __init__(
        self,
        *,
        max_qts: int,
    ) -> None:
        self.max_qts = max_qts

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.max_qts)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        max_qts = r.read_int()
        self = cls.__new__(cls)
        self.max_qts = max_qts
        return self


class ReportEncryptedSpam(TLFunction["bool"]):
    """The TL function messages.reportEncryptedSpam#4b0c8c0f, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0x4B0C8C0F
    QUALNAME = "functions.messages.ReportEncryptedSpam"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class ReadMessageContents(TLFunction["base.messages.AffectedMessages"]):
    """The TL function messages.readMessageContents#36a73f77, answered with messages.AffectedMessages."""

    __slots__ = ("id",)

    ID = 0x36A73F77
    QUALNAME = "functions.messages.ReadMessageContents"
    RESULT = "messages.AffectedMessages"

    def __init__(
        self,
        *,
        id: list[int],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.id = id
        return self


class GetStickers(TLFunction["base.messages.Stickers"]):
    """The TL function messages.getStickers#d5a5d3a1, answered with messages.Stickers."""

    __slots__ = ("emoticon", "hash",)

    ID = 0xD5A5D3A1
    QUALNAME = "functions.messages.GetStickers"
    RESULT = "messages.Stickers"

    def __init__(
        self,
        *,
        emoticon: str,
        hash: int,
    ) -> None:
        self.emoticon = emoticon
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.emoticon)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        emoticon = r.read_string()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.emoticon = emoticon
        self.hash = hash
        return self


class GetAllStickers(TLFunction["base.messages.AllStickers"]):
    """The TL function messages.getAllStickers#b8a0a1a8, answered with messages.AllStickers."""

    __slots__ = ("hash",)

    ID = 0xB8A0A1A8
    QUALNAME = "functions.messages.GetAllStickers"
    RESULT = "messages.AllStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetWebPagePreview(TLFunction["base.messages.WebPagePreview"]):
    """The TL function messages.getWebPagePreview#570d6f6f, answered with messages.WebPagePreview."""

    __slots__ = ("message", "entities",)

    ID = 0x570D6F6F
    QUALNAME = "functions.messages.GetWebPagePreview"
    RESULT = "messages.WebPagePreview"

    def __init__(
        self,
        *,
        message: str,
        entities: list[base.MessageEntity] | None = None,
    ) -> None:
        self.message = message
        self.entities = entities

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.entities is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_string(self.message)
        if self.entities is not None:
            w.write_vector(self.entities)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        message = r.read_string()
        entities = r.read_vector() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.message = message
        self.entities = entities
        return self


class ExportChatInvite(TLFunction["base.ExportedChatInvite"]):
    """The TL function messages.exportChatInvite#a455de90, answered with ExportedChatInvite."""

    __slots__ = ("legacy_revoke_permanent", "request_needed", "peer", "expire_date", "usage_limit", "title", "subscription_pricing",)

    ID = 0xA455DE90
    QUALNAME = "functions.messages.ExportChatInvite"
    RESULT = "ExportedChatInvite"

    def __init__(
        self,
        *,
        legacy_revoke_permanent: bool = False,
        request_needed: bool = False,
        peer: base.InputPeer,
        expire_date: int | None = None,
        usage_limit: int | None = None,
        title: str | None = None,
        subscription_pricing: base.StarsSubscriptionPricing | None = None,
    ) -> None:
        self.legacy_revoke_permanent = legacy_revoke_permanent
        self.request_needed = request_needed
        self.peer = peer
        self.expire_date = expire_date
        self.usage_limit = usage_limit
        self.title = title
        self.subscription_pricing = subscription_pricing

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.legacy_revoke_permanent:
            flags |= 1 << 2
        if self.request_needed:
            flags |= 1 << 3
        if self.expire_date is not None:
            flags |= 1 << 0
        if self.usage_limit is not None:
            flags |= 1 << 1
        if self.title is not None:
            flags |= 1 << 4
        if self.subscription_pricing is not None:
            flags |= 1 << 5
        w.write_int(flags)
        self.peer.write(w)
        if self.expire_date is not None:
            w.write_int(self.expire_date)
        if self.usage_limit is not None:
            w.write_int(self.usage_limit)
        if self.title is not None:
            w.write_string(self.title)
        if self.subscription_pricing is not None:
            self.subscription_pricing.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        legacy_revoke_permanent = bool(flags & (1 << 2))
        request_needed = bool(flags & (1 << 3))
        peer = r.read_object()
        expire_date = r.read_int() if flags & (1 << 0) else None
        usage_limit = r.read_int() if flags & (1 << 1) else None
        title = r.read_string() if flags & (1 << 4) else None
        subscription_pricing = r.read_object() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.legacy_revoke_permanent = legacy_revoke_permanent
        self.request_needed = request_needed
        self.peer = peer
        self.expire_date = expire_date
        self.usage_limit = usage_limit
        self.title = title
        self.subscription_pricing = subscription_pricing
        return self


class CheckChatInvite(TLFunction["base.ChatInvite"]):
    """The TL function messages.checkChatInvite#3eadb1bb, answered with ChatInvite."""

    __slots__ = ("hash",)

    ID = 0x3EADB1BB
    QUALNAME = "functions.messages.CheckChatInvite"
    RESULT = "ChatInvite"

    def __init__(
        self,
        *,
        hash: str,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_string()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ImportChatInvite(TLFunction["base.messages.ChatInviteJoinResult"]):
    """The TL function messages.importChatInvite#de91436e, answered with messages.ChatInviteJoinResult."""

    __slots__ = ("hash",)

    ID = 0xDE91436E
    QUALNAME = "functions.messages.ImportChatInvite"
    RESULT = "messages.ChatInviteJoinResult"

    def __init__(
        self,
        *,
        hash: str,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_string()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetStickerSet(TLFunction["base.messages.StickerSet"]):
    """The TL function messages.getStickerSet#c8a0ec74, answered with messages.StickerSet."""

    __slots__ = ("stickerset", "hash",)

    ID = 0xC8A0EC74
    QUALNAME = "functions.messages.GetStickerSet"
    RESULT = "messages.StickerSet"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
        hash: int,
    ) -> None:
        self.stickerset = stickerset
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        hash = r.read_int()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        self.hash = hash
        return self


class InstallStickerSet(TLFunction["base.messages.StickerSetInstallResult"]):
    """The TL function messages.installStickerSet#c78fe460, answered with messages.StickerSetInstallResult."""

    __slots__ = ("stickerset", "archived",)

    ID = 0xC78FE460
    QUALNAME = "functions.messages.InstallStickerSet"
    RESULT = "messages.StickerSetInstallResult"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
        archived: bool,
    ) -> None:
        self.stickerset = stickerset
        self.archived = archived

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)
        w.write_bool(self.archived)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        archived = r.read_bool()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        self.archived = archived
        return self


class UninstallStickerSet(TLFunction["bool"]):
    """The TL function messages.uninstallStickerSet#f96e55de, answered with Bool."""

    __slots__ = ("stickerset",)

    ID = 0xF96E55DE
    QUALNAME = "functions.messages.UninstallStickerSet"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        stickerset: base.InputStickerSet,
    ) -> None:
        self.stickerset = stickerset

    def write_body(self, w: TLWriter) -> None:
        self.stickerset.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stickerset = r.read_object()
        self = cls.__new__(cls)
        self.stickerset = stickerset
        return self


class StartBot(TLFunction["base.Updates"]):
    """The TL function messages.startBot#e6df7378, answered with Updates."""

    __slots__ = ("bot", "peer", "random_id", "start_param",)

    ID = 0xE6DF7378
    QUALNAME = "functions.messages.StartBot"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        peer: base.InputPeer,
        random_id: int,
        start_param: str,
    ) -> None:
        self.bot = bot
        self.peer = peer
        self.random_id = random_id
        self.start_param = start_param

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        self.peer.write(w)
        w.write_long(self.random_id)
        w.write_string(self.start_param)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        peer = r.read_object()
        random_id = r.read_long()
        start_param = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.peer = peer
        self.random_id = random_id
        self.start_param = start_param
        return self


class GetMessagesViews(TLFunction["base.messages.MessageViews"]):
    """The TL function messages.getMessagesViews#5784d3e1, answered with messages.MessageViews."""

    __slots__ = ("peer", "id", "increment",)

    ID = 0x5784D3E1
    QUALNAME = "functions.messages.GetMessagesViews"
    RESULT = "messages.MessageViews"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
        increment: bool,
    ) -> None:
        self.peer = peer
        self.id = id
        self.increment = increment

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)
        w.write_bool(self.increment)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        increment = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.increment = increment
        return self


class EditChatAdmin(TLFunction["bool"]):
    """The TL function messages.editChatAdmin#a85bd1c2, answered with Bool."""

    __slots__ = ("chat_id", "user_id", "is_admin",)

    ID = 0xA85BD1C2
    QUALNAME = "functions.messages.EditChatAdmin"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        chat_id: int,
        user_id: base.InputUser,
        is_admin: bool,
    ) -> None:
        self.chat_id = chat_id
        self.user_id = user_id
        self.is_admin = is_admin

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)
        self.user_id.write(w)
        w.write_bool(self.is_admin)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        user_id = r.read_object()
        is_admin = r.read_bool()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        self.user_id = user_id
        self.is_admin = is_admin
        return self


class MigrateChat(TLFunction["base.Updates"]):
    """The TL function messages.migrateChat#a2875319, answered with Updates."""

    __slots__ = ("chat_id",)

    ID = 0xA2875319
    QUALNAME = "functions.messages.MigrateChat"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        chat_id: int,
    ) -> None:
        self.chat_id = chat_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        return self


class SearchGlobal(TLFunction["base.messages.Messages"]):
    """The TL function messages.searchGlobal#6126a43c, answered with messages.Messages."""

    __slots__ = ("broadcasts_only", "groups_only", "users_only", "folder_id", "community", "q", "filter", "min_date", "max_date", "offset_rate", "offset_peer", "offset_id", "limit",)

    ID = 0x6126A43C
    QUALNAME = "functions.messages.SearchGlobal"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        broadcasts_only: bool = False,
        groups_only: bool = False,
        users_only: bool = False,
        folder_id: int | None = None,
        community: base.InputChannel | None = None,
        q: str,
        filter: base.MessagesFilter,
        min_date: int,
        max_date: int,
        offset_rate: int,
        offset_peer: base.InputPeer,
        offset_id: int,
        limit: int,
    ) -> None:
        self.broadcasts_only = broadcasts_only
        self.groups_only = groups_only
        self.users_only = users_only
        self.folder_id = folder_id
        self.community = community
        self.q = q
        self.filter = filter
        self.min_date = min_date
        self.max_date = max_date
        self.offset_rate = offset_rate
        self.offset_peer = offset_peer
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.broadcasts_only:
            flags |= 1 << 1
        if self.groups_only:
            flags |= 1 << 2
        if self.users_only:
            flags |= 1 << 3
        if self.folder_id is not None:
            flags |= 1 << 0
        if self.community is not None:
            flags |= 1 << 4
        w.write_int(flags)
        if self.folder_id is not None:
            w.write_int(self.folder_id)
        if self.community is not None:
            self.community.write(w)
        w.write_string(self.q)
        self.filter.write(w)
        w.write_int(self.min_date)
        w.write_int(self.max_date)
        w.write_int(self.offset_rate)
        self.offset_peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        broadcasts_only = bool(flags & (1 << 1))
        groups_only = bool(flags & (1 << 2))
        users_only = bool(flags & (1 << 3))
        folder_id = r.read_int() if flags & (1 << 0) else None
        community = r.read_object() if flags & (1 << 4) else None
        q = r.read_string()
        filter = r.read_object()
        min_date = r.read_int()
        max_date = r.read_int()
        offset_rate = r.read_int()
        offset_peer = r.read_object()
        offset_id = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.broadcasts_only = broadcasts_only
        self.groups_only = groups_only
        self.users_only = users_only
        self.folder_id = folder_id
        self.community = community
        self.q = q
        self.filter = filter
        self.min_date = min_date
        self.max_date = max_date
        self.offset_rate = offset_rate
        self.offset_peer = offset_peer
        self.offset_id = offset_id
        self.limit = limit
        return self


class ReorderStickerSets(TLFunction["bool"]):
    """The TL function messages.reorderStickerSets#78337739, answered with Bool."""

    __slots__ = ("masks", "emojis", "order",)

    ID = 0x78337739
    QUALNAME = "functions.messages.ReorderStickerSets"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        masks: bool = False,
        emojis: bool = False,
        order: list[int],
    ) -> None:
        self.masks = masks
        self.emojis = emojis
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.masks:
            flags |= 1 << 0
        if self.emojis:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_vector(self.order, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        masks = bool(flags & (1 << 0))
        emojis = bool(flags & (1 << 1))
        order = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.masks = masks
        self.emojis = emojis
        self.order = order
        return self


class GetDocumentByHash(TLFunction["base.Document"]):
    """The TL function messages.getDocumentByHash#b1f2061f, answered with Document."""

    __slots__ = ("sha256", "size", "mime_type",)

    ID = 0xB1F2061F
    QUALNAME = "functions.messages.GetDocumentByHash"
    RESULT = "Document"

    def __init__(
        self,
        *,
        sha256: bytes,
        size: int,
        mime_type: str,
    ) -> None:
        self.sha256 = sha256
        self.size = size
        self.mime_type = mime_type

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.sha256)
        w.write_long(self.size)
        w.write_string(self.mime_type)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sha256 = r.read_bytes()
        size = r.read_long()
        mime_type = r.read_string()
        self = cls.__new__(cls)
        self.sha256 = sha256
        self.size = size
        self.mime_type = mime_type
        return self


class GetSavedGifs(TLFunction["base.messages.SavedGifs"]):
    """The TL function messages.getSavedGifs#5cf09635, answered with messages.SavedGifs."""

    __slots__ = ("hash",)

    ID = 0x5CF09635
    QUALNAME = "functions.messages.GetSavedGifs"
    RESULT = "messages.SavedGifs"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SaveGif(TLFunction["bool"]):
    """The TL function messages.saveGif#327a30cb, answered with Bool."""

    __slots__ = ("id", "unsave",)

    ID = 0x327A30CB
    QUALNAME = "functions.messages.SaveGif"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.InputDocument,
        unsave: bool,
    ) -> None:
        self.id = id
        self.unsave = unsave

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_bool(self.unsave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        unsave = r.read_bool()
        self = cls.__new__(cls)
        self.id = id
        self.unsave = unsave
        return self


class GetInlineBotResults(TLFunction["base.messages.BotResults"]):
    """The TL function messages.getInlineBotResults#514e999d, answered with messages.BotResults."""

    __slots__ = ("bot", "peer", "geo_point", "query", "offset",)

    ID = 0x514E999D
    QUALNAME = "functions.messages.GetInlineBotResults"
    RESULT = "messages.BotResults"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        peer: base.InputPeer,
        geo_point: base.InputGeoPoint | None = None,
        query: str,
        offset: str,
    ) -> None:
        self.bot = bot
        self.peer = peer
        self.geo_point = geo_point
        self.query = query
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.geo_point is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.bot.write(w)
        self.peer.write(w)
        if self.geo_point is not None:
            self.geo_point.write(w)
        w.write_string(self.query)
        w.write_string(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        bot = r.read_object()
        peer = r.read_object()
        geo_point = r.read_object() if flags & (1 << 0) else None
        query = r.read_string()
        offset = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.peer = peer
        self.geo_point = geo_point
        self.query = query
        self.offset = offset
        return self


class SetInlineBotResults(TLFunction["bool"]):
    """The TL function messages.setInlineBotResults#bb12a419, answered with Bool."""

    __slots__ = ("gallery", "private", "query_id", "results", "cache_time", "next_offset", "switch_pm", "switch_webview",)

    ID = 0xBB12A419
    QUALNAME = "functions.messages.SetInlineBotResults"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        gallery: bool = False,
        private: bool = False,
        query_id: int,
        results: list[base.InputBotInlineResult],
        cache_time: int,
        next_offset: str | None = None,
        switch_pm: base.InlineBotSwitchPM | None = None,
        switch_webview: base.InlineBotWebView | None = None,
    ) -> None:
        self.gallery = gallery
        self.private = private
        self.query_id = query_id
        self.results = results
        self.cache_time = cache_time
        self.next_offset = next_offset
        self.switch_pm = switch_pm
        self.switch_webview = switch_webview

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.gallery:
            flags |= 1 << 0
        if self.private:
            flags |= 1 << 1
        if self.next_offset is not None:
            flags |= 1 << 2
        if self.switch_pm is not None:
            flags |= 1 << 3
        if self.switch_webview is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_long(self.query_id)
        w.write_vector(self.results)
        w.write_int(self.cache_time)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        if self.switch_pm is not None:
            self.switch_pm.write(w)
        if self.switch_webview is not None:
            self.switch_webview.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        gallery = bool(flags & (1 << 0))
        private = bool(flags & (1 << 1))
        query_id = r.read_long()
        results = r.read_vector()
        cache_time = r.read_int()
        next_offset = r.read_string() if flags & (1 << 2) else None
        switch_pm = r.read_object() if flags & (1 << 3) else None
        switch_webview = r.read_object() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.gallery = gallery
        self.private = private
        self.query_id = query_id
        self.results = results
        self.cache_time = cache_time
        self.next_offset = next_offset
        self.switch_pm = switch_pm
        self.switch_webview = switch_webview
        return self


class SendInlineBotResult(TLFunction["base.Updates"]):
    """The TL function messages.sendInlineBotResult#c0cf7646, answered with Updates."""

    __slots__ = ("silent", "background", "clear_draft", "hide_via", "peer", "reply_to", "random_id", "query_id", "id", "schedule_date", "send_as", "quick_reply_shortcut", "allow_paid_stars",)

    ID = 0xC0CF7646
    QUALNAME = "functions.messages.SendInlineBotResult"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        silent: bool = False,
        background: bool = False,
        clear_draft: bool = False,
        hide_via: bool = False,
        peer: base.InputPeer,
        reply_to: base.InputReplyTo | None = None,
        random_id: int,
        query_id: int,
        id: str,
        schedule_date: int | None = None,
        send_as: base.InputPeer | None = None,
        quick_reply_shortcut: base.InputQuickReplyShortcut | None = None,
        allow_paid_stars: int | None = None,
    ) -> None:
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.hide_via = hide_via
        self.peer = peer
        self.reply_to = reply_to
        self.random_id = random_id
        self.query_id = query_id
        self.id = id
        self.schedule_date = schedule_date
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.allow_paid_stars = allow_paid_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.clear_draft:
            flags |= 1 << 7
        if self.hide_via:
            flags |= 1 << 11
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.schedule_date is not None:
            flags |= 1 << 10
        if self.send_as is not None:
            flags |= 1 << 13
        if self.quick_reply_shortcut is not None:
            flags |= 1 << 17
        if self.allow_paid_stars is not None:
            flags |= 1 << 21
        w.write_int(flags)
        self.peer.write(w)
        if self.reply_to is not None:
            self.reply_to.write(w)
        w.write_long(self.random_id)
        w.write_long(self.query_id)
        w.write_string(self.id)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.send_as is not None:
            self.send_as.write(w)
        if self.quick_reply_shortcut is not None:
            self.quick_reply_shortcut.write(w)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 5))
        background = bool(flags & (1 << 6))
        clear_draft = bool(flags & (1 << 7))
        hide_via = bool(flags & (1 << 11))
        peer = r.read_object()
        reply_to = r.read_object() if flags & (1 << 0) else None
        random_id = r.read_long()
        query_id = r.read_long()
        id = r.read_string()
        schedule_date = r.read_int() if flags & (1 << 10) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        quick_reply_shortcut = r.read_object() if flags & (1 << 17) else None
        allow_paid_stars = r.read_long() if flags & (1 << 21) else None
        self = cls.__new__(cls)
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.hide_via = hide_via
        self.peer = peer
        self.reply_to = reply_to
        self.random_id = random_id
        self.query_id = query_id
        self.id = id
        self.schedule_date = schedule_date
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.allow_paid_stars = allow_paid_stars
        return self


class GetMessageEditData(TLFunction["base.messages.MessageEditData"]):
    """The TL function messages.getMessageEditData#fda68d36, answered with messages.MessageEditData."""

    __slots__ = ("peer", "id",)

    ID = 0xFDA68D36
    QUALNAME = "functions.messages.GetMessageEditData"
    RESULT = "messages.MessageEditData"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class EditMessage(TLFunction["base.Updates"]):
    """The TL function messages.editMessage#b106e66c, answered with Updates."""

    __slots__ = ("no_webpage", "invert_media", "peer", "id", "message", "media", "reply_markup", "entities", "schedule_date", "schedule_repeat_period", "quick_reply_shortcut_id", "rich_message",)

    ID = 0xB106E66C
    QUALNAME = "functions.messages.EditMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        no_webpage: bool = False,
        invert_media: bool = False,
        peer: base.InputPeer,
        id: int,
        message: str | None = None,
        media: base.InputMedia | None = None,
        reply_markup: base.ReplyMarkup | None = None,
        entities: list[base.MessageEntity] | None = None,
        schedule_date: int | None = None,
        schedule_repeat_period: int | None = None,
        quick_reply_shortcut_id: int | None = None,
        rich_message: base.InputRichMessage | None = None,
    ) -> None:
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.peer = peer
        self.id = id
        self.message = message
        self.media = media
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.quick_reply_shortcut_id = quick_reply_shortcut_id
        self.rich_message = rich_message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_webpage:
            flags |= 1 << 1
        if self.invert_media:
            flags |= 1 << 16
        if self.message is not None:
            flags |= 1 << 11
        if self.media is not None:
            flags |= 1 << 14
        if self.reply_markup is not None:
            flags |= 1 << 2
        if self.entities is not None:
            flags |= 1 << 3
        if self.schedule_date is not None:
            flags |= 1 << 15
        if self.schedule_repeat_period is not None:
            flags |= 1 << 18
        if self.quick_reply_shortcut_id is not None:
            flags |= 1 << 17
        if self.rich_message is not None:
            flags |= 1 << 23
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.message is not None:
            w.write_string(self.message)
        if self.media is not None:
            self.media.write(w)
        if self.reply_markup is not None:
            self.reply_markup.write(w)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.schedule_repeat_period is not None:
            w.write_int(self.schedule_repeat_period)
        if self.quick_reply_shortcut_id is not None:
            w.write_int(self.quick_reply_shortcut_id)
        if self.rich_message is not None:
            self.rich_message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_webpage = bool(flags & (1 << 1))
        invert_media = bool(flags & (1 << 16))
        peer = r.read_object()
        id = r.read_int()
        message = r.read_string() if flags & (1 << 11) else None
        media = r.read_object() if flags & (1 << 14) else None
        reply_markup = r.read_object() if flags & (1 << 2) else None
        entities = r.read_vector() if flags & (1 << 3) else None
        schedule_date = r.read_int() if flags & (1 << 15) else None
        schedule_repeat_period = r.read_int() if flags & (1 << 18) else None
        quick_reply_shortcut_id = r.read_int() if flags & (1 << 17) else None
        rich_message = r.read_object() if flags & (1 << 23) else None
        self = cls.__new__(cls)
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.peer = peer
        self.id = id
        self.message = message
        self.media = media
        self.reply_markup = reply_markup
        self.entities = entities
        self.schedule_date = schedule_date
        self.schedule_repeat_period = schedule_repeat_period
        self.quick_reply_shortcut_id = quick_reply_shortcut_id
        self.rich_message = rich_message
        return self


class EditInlineBotMessage(TLFunction["bool"]):
    """The TL function messages.editInlineBotMessage#a423bb51, answered with Bool."""

    __slots__ = ("no_webpage", "invert_media", "id", "message", "media", "reply_markup", "entities", "rich_message",)

    ID = 0xA423BB51
    QUALNAME = "functions.messages.EditInlineBotMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        no_webpage: bool = False,
        invert_media: bool = False,
        id: base.InputBotInlineMessageID,
        message: str | None = None,
        media: base.InputMedia | None = None,
        reply_markup: base.ReplyMarkup | None = None,
        entities: list[base.MessageEntity] | None = None,
        rich_message: base.InputRichMessage | None = None,
    ) -> None:
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.id = id
        self.message = message
        self.media = media
        self.reply_markup = reply_markup
        self.entities = entities
        self.rich_message = rich_message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_webpage:
            flags |= 1 << 1
        if self.invert_media:
            flags |= 1 << 16
        if self.message is not None:
            flags |= 1 << 11
        if self.media is not None:
            flags |= 1 << 14
        if self.reply_markup is not None:
            flags |= 1 << 2
        if self.entities is not None:
            flags |= 1 << 3
        if self.rich_message is not None:
            flags |= 1 << 23
        w.write_int(flags)
        self.id.write(w)
        if self.message is not None:
            w.write_string(self.message)
        if self.media is not None:
            self.media.write(w)
        if self.reply_markup is not None:
            self.reply_markup.write(w)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.rich_message is not None:
            self.rich_message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_webpage = bool(flags & (1 << 1))
        invert_media = bool(flags & (1 << 16))
        id = r.read_object()
        message = r.read_string() if flags & (1 << 11) else None
        media = r.read_object() if flags & (1 << 14) else None
        reply_markup = r.read_object() if flags & (1 << 2) else None
        entities = r.read_vector() if flags & (1 << 3) else None
        rich_message = r.read_object() if flags & (1 << 23) else None
        self = cls.__new__(cls)
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.id = id
        self.message = message
        self.media = media
        self.reply_markup = reply_markup
        self.entities = entities
        self.rich_message = rich_message
        return self


class GetBotCallbackAnswer(TLFunction["base.messages.BotCallbackAnswer"]):
    """The TL function messages.getBotCallbackAnswer#9342ca07, answered with messages.BotCallbackAnswer."""

    __slots__ = ("game", "peer", "msg_id", "data", "password",)

    ID = 0x9342CA07
    QUALNAME = "functions.messages.GetBotCallbackAnswer"
    RESULT = "messages.BotCallbackAnswer"

    def __init__(
        self,
        *,
        game: bool = False,
        peer: base.InputPeer,
        msg_id: int,
        data: bytes | None = None,
        password: base.InputCheckPasswordSRP | None = None,
    ) -> None:
        self.game = game
        self.peer = peer
        self.msg_id = msg_id
        self.data = data
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.game:
            flags |= 1 << 1
        if self.data is not None:
            flags |= 1 << 0
        if self.password is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.msg_id)
        if self.data is not None:
            w.write_bytes(self.data)
        if self.password is not None:
            self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        game = bool(flags & (1 << 1))
        peer = r.read_object()
        msg_id = r.read_int()
        data = r.read_bytes() if flags & (1 << 0) else None
        password = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.game = game
        self.peer = peer
        self.msg_id = msg_id
        self.data = data
        self.password = password
        return self


class SetBotCallbackAnswer(TLFunction["bool"]):
    """The TL function messages.setBotCallbackAnswer#d58f130a, answered with Bool."""

    __slots__ = ("alert", "query_id", "message", "url", "cache_time",)

    ID = 0xD58F130A
    QUALNAME = "functions.messages.SetBotCallbackAnswer"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        alert: bool = False,
        query_id: int,
        message: str | None = None,
        url: str | None = None,
        cache_time: int,
    ) -> None:
        self.alert = alert
        self.query_id = query_id
        self.message = message
        self.url = url
        self.cache_time = cache_time

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.alert:
            flags |= 1 << 1
        if self.message is not None:
            flags |= 1 << 0
        if self.url is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_long(self.query_id)
        if self.message is not None:
            w.write_string(self.message)
        if self.url is not None:
            w.write_string(self.url)
        w.write_int(self.cache_time)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        alert = bool(flags & (1 << 1))
        query_id = r.read_long()
        message = r.read_string() if flags & (1 << 0) else None
        url = r.read_string() if flags & (1 << 2) else None
        cache_time = r.read_int()
        self = cls.__new__(cls)
        self.alert = alert
        self.query_id = query_id
        self.message = message
        self.url = url
        self.cache_time = cache_time
        return self


class GetPeerDialogs(TLFunction["base.messages.PeerDialogs"]):
    """The TL function messages.getPeerDialogs#e470bcfd, answered with messages.PeerDialogs."""

    __slots__ = ("peers",)

    ID = 0xE470BCFD
    QUALNAME = "functions.messages.GetPeerDialogs"
    RESULT = "messages.PeerDialogs"

    def __init__(
        self,
        *,
        peers: list[base.InputDialogPeer],
    ) -> None:
        self.peers = peers

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peers = r.read_vector()
        self = cls.__new__(cls)
        self.peers = peers
        return self


class SaveDraft(TLFunction["bool"]):
    """The TL function messages.saveDraft#ad0fa15c, answered with Bool."""

    __slots__ = ("no_webpage", "invert_media", "reply_to", "peer", "message", "entities", "media", "effect", "suggested_post", "rich_message",)

    ID = 0xAD0FA15C
    QUALNAME = "functions.messages.SaveDraft"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        no_webpage: bool = False,
        invert_media: bool = False,
        reply_to: base.InputReplyTo | None = None,
        peer: base.InputPeer,
        message: str,
        entities: list[base.MessageEntity] | None = None,
        media: base.InputMedia | None = None,
        effect: int | None = None,
        suggested_post: base.SuggestedPost | None = None,
        rich_message: base.InputRichMessage | None = None,
    ) -> None:
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.reply_to = reply_to
        self.peer = peer
        self.message = message
        self.entities = entities
        self.media = media
        self.effect = effect
        self.suggested_post = suggested_post
        self.rich_message = rich_message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_webpage:
            flags |= 1 << 1
        if self.invert_media:
            flags |= 1 << 6
        if self.reply_to is not None:
            flags |= 1 << 4
        if self.entities is not None:
            flags |= 1 << 3
        if self.media is not None:
            flags |= 1 << 5
        if self.effect is not None:
            flags |= 1 << 7
        if self.suggested_post is not None:
            flags |= 1 << 8
        if self.rich_message is not None:
            flags |= 1 << 9
        w.write_int(flags)
        if self.reply_to is not None:
            self.reply_to.write(w)
        self.peer.write(w)
        w.write_string(self.message)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.media is not None:
            self.media.write(w)
        if self.effect is not None:
            w.write_long(self.effect)
        if self.suggested_post is not None:
            self.suggested_post.write(w)
        if self.rich_message is not None:
            self.rich_message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_webpage = bool(flags & (1 << 1))
        invert_media = bool(flags & (1 << 6))
        reply_to = r.read_object() if flags & (1 << 4) else None
        peer = r.read_object()
        message = r.read_string()
        entities = r.read_vector() if flags & (1 << 3) else None
        media = r.read_object() if flags & (1 << 5) else None
        effect = r.read_long() if flags & (1 << 7) else None
        suggested_post = r.read_object() if flags & (1 << 8) else None
        rich_message = r.read_object() if flags & (1 << 9) else None
        self = cls.__new__(cls)
        self.no_webpage = no_webpage
        self.invert_media = invert_media
        self.reply_to = reply_to
        self.peer = peer
        self.message = message
        self.entities = entities
        self.media = media
        self.effect = effect
        self.suggested_post = suggested_post
        self.rich_message = rich_message
        return self


class GetAllDrafts(TLFunction["base.Updates"]):
    """The TL function messages.getAllDrafts#6a3f8d65, answered with Updates."""

    __slots__ = ()

    ID = 0x6A3F8D65
    QUALNAME = "functions.messages.GetAllDrafts"
    RESULT = "Updates"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetFeaturedStickers(TLFunction["base.messages.FeaturedStickers"]):
    """The TL function messages.getFeaturedStickers#64780b14, answered with messages.FeaturedStickers."""

    __slots__ = ("hash",)

    ID = 0x64780B14
    QUALNAME = "functions.messages.GetFeaturedStickers"
    RESULT = "messages.FeaturedStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ReadFeaturedStickers(TLFunction["bool"]):
    """The TL function messages.readFeaturedStickers#5b118126, answered with Bool."""

    __slots__ = ("id",)

    ID = 0x5B118126
    QUALNAME = "functions.messages.ReadFeaturedStickers"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: list[int],
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.id, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.id = id
        return self


class GetRecentStickers(TLFunction["base.messages.RecentStickers"]):
    """The TL function messages.getRecentStickers#9da9403b, answered with messages.RecentStickers."""

    __slots__ = ("attached", "hash",)

    ID = 0x9DA9403B
    QUALNAME = "functions.messages.GetRecentStickers"
    RESULT = "messages.RecentStickers"

    def __init__(
        self,
        *,
        attached: bool = False,
        hash: int,
    ) -> None:
        self.attached = attached
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.attached:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        attached = bool(flags & (1 << 0))
        hash = r.read_long()
        self = cls.__new__(cls)
        self.attached = attached
        self.hash = hash
        return self


class SaveRecentSticker(TLFunction["bool"]):
    """The TL function messages.saveRecentSticker#392718f8, answered with Bool."""

    __slots__ = ("attached", "id", "unsave",)

    ID = 0x392718F8
    QUALNAME = "functions.messages.SaveRecentSticker"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        attached: bool = False,
        id: base.InputDocument,
        unsave: bool,
    ) -> None:
        self.attached = attached
        self.id = id
        self.unsave = unsave

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.attached:
            flags |= 1 << 0
        w.write_int(flags)
        self.id.write(w)
        w.write_bool(self.unsave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        attached = bool(flags & (1 << 0))
        id = r.read_object()
        unsave = r.read_bool()
        self = cls.__new__(cls)
        self.attached = attached
        self.id = id
        self.unsave = unsave
        return self


class ClearRecentStickers(TLFunction["bool"]):
    """The TL function messages.clearRecentStickers#8999602d, answered with Bool."""

    __slots__ = ("attached",)

    ID = 0x8999602D
    QUALNAME = "functions.messages.ClearRecentStickers"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        attached: bool = False,
    ) -> None:
        self.attached = attached

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.attached:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        attached = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.attached = attached
        return self


class GetArchivedStickers(TLFunction["base.messages.ArchivedStickers"]):
    """The TL function messages.getArchivedStickers#57f17692, answered with messages.ArchivedStickers."""

    __slots__ = ("masks", "emojis", "offset_id", "limit",)

    ID = 0x57F17692
    QUALNAME = "functions.messages.GetArchivedStickers"
    RESULT = "messages.ArchivedStickers"

    def __init__(
        self,
        *,
        masks: bool = False,
        emojis: bool = False,
        offset_id: int,
        limit: int,
    ) -> None:
        self.masks = masks
        self.emojis = emojis
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.masks:
            flags |= 1 << 0
        if self.emojis:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_long(self.offset_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        masks = bool(flags & (1 << 0))
        emojis = bool(flags & (1 << 1))
        offset_id = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.masks = masks
        self.emojis = emojis
        self.offset_id = offset_id
        self.limit = limit
        return self


class GetMaskStickers(TLFunction["base.messages.AllStickers"]):
    """The TL function messages.getMaskStickers#640f82b8, answered with messages.AllStickers."""

    __slots__ = ("hash",)

    ID = 0x640F82B8
    QUALNAME = "functions.messages.GetMaskStickers"
    RESULT = "messages.AllStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetAttachedStickers(TLFunction["list[base.StickerSetCovered]"]):
    """The TL function messages.getAttachedStickers#cc5b67cc, answered with Vector<StickerSetCovered>."""

    __slots__ = ("media",)

    ID = 0xCC5B67CC
    QUALNAME = "functions.messages.GetAttachedStickers"
    RESULT = "Vector<StickerSetCovered>"

    def __init__(
        self,
        *,
        media: base.InputStickeredMedia,
    ) -> None:
        self.media = media

    def write_body(self, w: TLWriter) -> None:
        self.media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        media = r.read_object()
        self = cls.__new__(cls)
        self.media = media
        return self


class SetGameScore(TLFunction["base.Updates"]):
    """The TL function messages.setGameScore#8ef8ecc0, answered with Updates."""

    __slots__ = ("edit_message", "force", "peer", "id", "user_id", "score",)

    ID = 0x8EF8ECC0
    QUALNAME = "functions.messages.SetGameScore"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        edit_message: bool = False,
        force: bool = False,
        peer: base.InputPeer,
        id: int,
        user_id: base.InputUser,
        score: int,
    ) -> None:
        self.edit_message = edit_message
        self.force = force
        self.peer = peer
        self.id = id
        self.user_id = user_id
        self.score = score

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.edit_message:
            flags |= 1 << 0
        if self.force:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        self.user_id.write(w)
        w.write_int(self.score)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        edit_message = bool(flags & (1 << 0))
        force = bool(flags & (1 << 1))
        peer = r.read_object()
        id = r.read_int()
        user_id = r.read_object()
        score = r.read_int()
        self = cls.__new__(cls)
        self.edit_message = edit_message
        self.force = force
        self.peer = peer
        self.id = id
        self.user_id = user_id
        self.score = score
        return self


class SetInlineGameScore(TLFunction["bool"]):
    """The TL function messages.setInlineGameScore#15ad9f64, answered with Bool."""

    __slots__ = ("edit_message", "force", "id", "user_id", "score",)

    ID = 0x15AD9F64
    QUALNAME = "functions.messages.SetInlineGameScore"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        edit_message: bool = False,
        force: bool = False,
        id: base.InputBotInlineMessageID,
        user_id: base.InputUser,
        score: int,
    ) -> None:
        self.edit_message = edit_message
        self.force = force
        self.id = id
        self.user_id = user_id
        self.score = score

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.edit_message:
            flags |= 1 << 0
        if self.force:
            flags |= 1 << 1
        w.write_int(flags)
        self.id.write(w)
        self.user_id.write(w)
        w.write_int(self.score)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        edit_message = bool(flags & (1 << 0))
        force = bool(flags & (1 << 1))
        id = r.read_object()
        user_id = r.read_object()
        score = r.read_int()
        self = cls.__new__(cls)
        self.edit_message = edit_message
        self.force = force
        self.id = id
        self.user_id = user_id
        self.score = score
        return self


class GetGameHighScores(TLFunction["base.messages.HighScores"]):
    """The TL function messages.getGameHighScores#e822649d, answered with messages.HighScores."""

    __slots__ = ("peer", "id", "user_id",)

    ID = 0xE822649D
    QUALNAME = "functions.messages.GetGameHighScores"
    RESULT = "messages.HighScores"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        user_id: base.InputUser,
    ) -> None:
        self.peer = peer
        self.id = id
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.user_id = user_id
        return self


class GetInlineGameHighScores(TLFunction["base.messages.HighScores"]):
    """The TL function messages.getInlineGameHighScores#0f635e1b, answered with messages.HighScores."""

    __slots__ = ("id", "user_id",)

    ID = 0x0F635E1B
    QUALNAME = "functions.messages.GetInlineGameHighScores"
    RESULT = "messages.HighScores"

    def __init__(
        self,
        *,
        id: base.InputBotInlineMessageID,
        user_id: base.InputUser,
    ) -> None:
        self.id = id
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.id = id
        self.user_id = user_id
        return self


class GetCommonChats(TLFunction["base.messages.Chats"]):
    """The TL function messages.getCommonChats#e40ca104, answered with messages.Chats."""

    __slots__ = ("user_id", "max_id", "limit",)

    ID = 0xE40CA104
    QUALNAME = "functions.messages.GetCommonChats"
    RESULT = "messages.Chats"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        max_id: int,
        limit: int,
    ) -> None:
        self.user_id = user_id
        self.max_id = max_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_long(self.max_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        max_id = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.max_id = max_id
        self.limit = limit
        return self


class GetWebPage(TLFunction["base.messages.WebPage"]):
    """The TL function messages.getWebPage#8d9692a3, answered with messages.WebPage."""

    __slots__ = ("url", "hash",)

    ID = 0x8D9692A3
    QUALNAME = "functions.messages.GetWebPage"
    RESULT = "messages.WebPage"

    def __init__(
        self,
        *,
        url: str,
        hash: int,
    ) -> None:
        self.url = url
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        hash = r.read_int()
        self = cls.__new__(cls)
        self.url = url
        self.hash = hash
        return self


class ToggleDialogPin(TLFunction["bool"]):
    """The TL function messages.toggleDialogPin#a731e257, answered with Bool."""

    __slots__ = ("pinned", "peer",)

    ID = 0xA731E257
    QUALNAME = "functions.messages.ToggleDialogPin"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        pinned: bool = False,
        peer: base.InputDialogPeer,
    ) -> None:
        self.pinned = pinned
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pinned:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pinned = bool(flags & (1 << 0))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.pinned = pinned
        self.peer = peer
        return self


class ReorderPinnedDialogs(TLFunction["bool"]):
    """The TL function messages.reorderPinnedDialogs#3b1adf37, answered with Bool."""

    __slots__ = ("force", "folder_id", "order",)

    ID = 0x3B1ADF37
    QUALNAME = "functions.messages.ReorderPinnedDialogs"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        force: bool = False,
        folder_id: int,
        order: list[base.InputDialogPeer],
    ) -> None:
        self.force = force
        self.folder_id = folder_id
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.force:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.folder_id)
        w.write_vector(self.order)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        force = bool(flags & (1 << 0))
        folder_id = r.read_int()
        order = r.read_vector()
        self = cls.__new__(cls)
        self.force = force
        self.folder_id = folder_id
        self.order = order
        return self


class GetPinnedDialogs(TLFunction["base.messages.PeerDialogs"]):
    """The TL function messages.getPinnedDialogs#d6b94df2, answered with messages.PeerDialogs."""

    __slots__ = ("folder_id",)

    ID = 0xD6B94DF2
    QUALNAME = "functions.messages.GetPinnedDialogs"
    RESULT = "messages.PeerDialogs"

    def __init__(
        self,
        *,
        folder_id: int,
    ) -> None:
        self.folder_id = folder_id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.folder_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        folder_id = r.read_int()
        self = cls.__new__(cls)
        self.folder_id = folder_id
        return self


class SetBotShippingResults(TLFunction["bool"]):
    """The TL function messages.setBotShippingResults#e5f672fa, answered with Bool."""

    __slots__ = ("query_id", "error", "shipping_options",)

    ID = 0xE5F672FA
    QUALNAME = "functions.messages.SetBotShippingResults"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        query_id: int,
        error: str | None = None,
        shipping_options: list[base.ShippingOption] | None = None,
    ) -> None:
        self.query_id = query_id
        self.error = error
        self.shipping_options = shipping_options

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.error is not None:
            flags |= 1 << 0
        if self.shipping_options is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_long(self.query_id)
        if self.error is not None:
            w.write_string(self.error)
        if self.shipping_options is not None:
            w.write_vector(self.shipping_options)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        query_id = r.read_long()
        error = r.read_string() if flags & (1 << 0) else None
        shipping_options = r.read_vector() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.query_id = query_id
        self.error = error
        self.shipping_options = shipping_options
        return self


class SetBotPrecheckoutResults(TLFunction["bool"]):
    """The TL function messages.setBotPrecheckoutResults#09c2dd95, answered with Bool."""

    __slots__ = ("success", "query_id", "error",)

    ID = 0x09C2DD95
    QUALNAME = "functions.messages.SetBotPrecheckoutResults"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        success: bool = False,
        query_id: int,
        error: str | None = None,
    ) -> None:
        self.success = success
        self.query_id = query_id
        self.error = error

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.success:
            flags |= 1 << 1
        if self.error is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.query_id)
        if self.error is not None:
            w.write_string(self.error)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        success = bool(flags & (1 << 1))
        query_id = r.read_long()
        error = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.success = success
        self.query_id = query_id
        self.error = error
        return self


class UploadMedia(TLFunction["base.MessageMedia"]):
    """The TL function messages.uploadMedia#14967978, answered with MessageMedia."""

    __slots__ = ("business_connection_id", "peer", "media",)

    ID = 0x14967978
    QUALNAME = "functions.messages.UploadMedia"
    RESULT = "MessageMedia"

    def __init__(
        self,
        *,
        business_connection_id: str | None = None,
        peer: base.InputPeer,
        media: base.InputMedia,
    ) -> None:
        self.business_connection_id = business_connection_id
        self.peer = peer
        self.media = media

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.business_connection_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.business_connection_id is not None:
            w.write_string(self.business_connection_id)
        self.peer.write(w)
        self.media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        business_connection_id = r.read_string() if flags & (1 << 0) else None
        peer = r.read_object()
        media = r.read_object()
        self = cls.__new__(cls)
        self.business_connection_id = business_connection_id
        self.peer = peer
        self.media = media
        return self


class SendScreenshotNotification(TLFunction["base.Updates"]):
    """The TL function messages.sendScreenshotNotification#a1405817, answered with Updates."""

    __slots__ = ("peer", "reply_to", "random_id",)

    ID = 0xA1405817
    QUALNAME = "functions.messages.SendScreenshotNotification"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        reply_to: base.InputReplyTo,
        random_id: int,
    ) -> None:
        self.peer = peer
        self.reply_to = reply_to
        self.random_id = random_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.reply_to.write(w)
        w.write_long(self.random_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        reply_to = r.read_object()
        random_id = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.reply_to = reply_to
        self.random_id = random_id
        return self


class GetFavedStickers(TLFunction["base.messages.FavedStickers"]):
    """The TL function messages.getFavedStickers#04f1aaa9, answered with messages.FavedStickers."""

    __slots__ = ("hash",)

    ID = 0x04F1AAA9
    QUALNAME = "functions.messages.GetFavedStickers"
    RESULT = "messages.FavedStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class FaveSticker(TLFunction["bool"]):
    """The TL function messages.faveSticker#b9ffc55b, answered with Bool."""

    __slots__ = ("id", "unfave",)

    ID = 0xB9FFC55B
    QUALNAME = "functions.messages.FaveSticker"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.InputDocument,
        unfave: bool,
    ) -> None:
        self.id = id
        self.unfave = unfave

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_bool(self.unfave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        unfave = r.read_bool()
        self = cls.__new__(cls)
        self.id = id
        self.unfave = unfave
        return self


class GetUnreadMentions(TLFunction["base.messages.Messages"]):
    """The TL function messages.getUnreadMentions#f107e790, answered with messages.Messages."""

    __slots__ = ("peer", "top_msg_id", "offset_id", "add_offset", "limit", "max_id", "min_id",)

    ID = 0xF107E790
    QUALNAME = "functions.messages.GetUnreadMentions"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        offset_id: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        w.write_int(self.offset_id)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        offset_id = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        return self


class ReadMentions(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.readMentions#36e5bf4d, answered with messages.AffectedHistory."""

    __slots__ = ("peer", "top_msg_id",)

    ID = 0x36E5BF4D
    QUALNAME = "functions.messages.ReadMentions"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        return self


class GetRecentLocations(TLFunction["base.messages.Messages"]):
    """The TL function messages.getRecentLocations#702a40e0, answered with messages.Messages."""

    __slots__ = ("peer", "limit", "hash",)

    ID = 0x702A40E0
    QUALNAME = "functions.messages.GetRecentLocations"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        limit: int,
        hash: int,
    ) -> None:
        self.peer = peer
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.limit = limit
        self.hash = hash
        return self


class SendMultiMedia(TLFunction["base.Updates"]):
    """The TL function messages.sendMultiMedia#1bf89d74, answered with Updates."""

    __slots__ = ("silent", "background", "clear_draft", "noforwards", "update_stickersets_order", "invert_media", "allow_paid_floodskip", "peer", "reply_to", "multi_media", "schedule_date", "send_as", "quick_reply_shortcut", "effect", "allow_paid_stars",)

    ID = 0x1BF89D74
    QUALNAME = "functions.messages.SendMultiMedia"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        silent: bool = False,
        background: bool = False,
        clear_draft: bool = False,
        noforwards: bool = False,
        update_stickersets_order: bool = False,
        invert_media: bool = False,
        allow_paid_floodskip: bool = False,
        peer: base.InputPeer,
        reply_to: base.InputReplyTo | None = None,
        multi_media: list[base.InputSingleMedia],
        schedule_date: int | None = None,
        send_as: base.InputPeer | None = None,
        quick_reply_shortcut: base.InputQuickReplyShortcut | None = None,
        effect: int | None = None,
        allow_paid_stars: int | None = None,
    ) -> None:
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.multi_media = multi_media
        self.schedule_date = schedule_date
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.clear_draft:
            flags |= 1 << 7
        if self.noforwards:
            flags |= 1 << 14
        if self.update_stickersets_order:
            flags |= 1 << 15
        if self.invert_media:
            flags |= 1 << 16
        if self.allow_paid_floodskip:
            flags |= 1 << 19
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.schedule_date is not None:
            flags |= 1 << 10
        if self.send_as is not None:
            flags |= 1 << 13
        if self.quick_reply_shortcut is not None:
            flags |= 1 << 17
        if self.effect is not None:
            flags |= 1 << 18
        if self.allow_paid_stars is not None:
            flags |= 1 << 21
        w.write_int(flags)
        self.peer.write(w)
        if self.reply_to is not None:
            self.reply_to.write(w)
        w.write_vector(self.multi_media)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.send_as is not None:
            self.send_as.write(w)
        if self.quick_reply_shortcut is not None:
            self.quick_reply_shortcut.write(w)
        if self.effect is not None:
            w.write_long(self.effect)
        if self.allow_paid_stars is not None:
            w.write_long(self.allow_paid_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 5))
        background = bool(flags & (1 << 6))
        clear_draft = bool(flags & (1 << 7))
        noforwards = bool(flags & (1 << 14))
        update_stickersets_order = bool(flags & (1 << 15))
        invert_media = bool(flags & (1 << 16))
        allow_paid_floodskip = bool(flags & (1 << 19))
        peer = r.read_object()
        reply_to = r.read_object() if flags & (1 << 0) else None
        multi_media = r.read_vector()
        schedule_date = r.read_int() if flags & (1 << 10) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        quick_reply_shortcut = r.read_object() if flags & (1 << 17) else None
        effect = r.read_long() if flags & (1 << 18) else None
        allow_paid_stars = r.read_long() if flags & (1 << 21) else None
        self = cls.__new__(cls)
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.noforwards = noforwards
        self.update_stickersets_order = update_stickersets_order
        self.invert_media = invert_media
        self.allow_paid_floodskip = allow_paid_floodskip
        self.peer = peer
        self.reply_to = reply_to
        self.multi_media = multi_media
        self.schedule_date = schedule_date
        self.send_as = send_as
        self.quick_reply_shortcut = quick_reply_shortcut
        self.effect = effect
        self.allow_paid_stars = allow_paid_stars
        return self


class UploadEncryptedFile(TLFunction["base.EncryptedFile"]):
    """The TL function messages.uploadEncryptedFile#5057c497, answered with EncryptedFile."""

    __slots__ = ("peer", "file",)

    ID = 0x5057C497
    QUALNAME = "functions.messages.UploadEncryptedFile"
    RESULT = "EncryptedFile"

    def __init__(
        self,
        *,
        peer: base.InputEncryptedChat,
        file: base.InputEncryptedFile,
    ) -> None:
        self.peer = peer
        self.file = file

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.file.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        file = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.file = file
        return self


class SearchStickerSets(TLFunction["base.messages.FoundStickerSets"]):
    """The TL function messages.searchStickerSets#35705b8a, answered with messages.FoundStickerSets."""

    __slots__ = ("exclude_featured", "q", "hash",)

    ID = 0x35705B8A
    QUALNAME = "functions.messages.SearchStickerSets"
    RESULT = "messages.FoundStickerSets"

    def __init__(
        self,
        *,
        exclude_featured: bool = False,
        q: str,
        hash: int,
    ) -> None:
        self.exclude_featured = exclude_featured
        self.q = q
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.exclude_featured:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.q)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        exclude_featured = bool(flags & (1 << 0))
        q = r.read_string()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.exclude_featured = exclude_featured
        self.q = q
        self.hash = hash
        return self


class GetSplitRanges(TLFunction["list[base.MessageRange]"]):
    """The TL function messages.getSplitRanges#1cff7e08, answered with Vector<MessageRange>."""

    __slots__ = ()

    ID = 0x1CFF7E08
    QUALNAME = "functions.messages.GetSplitRanges"
    RESULT = "Vector<MessageRange>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class MarkDialogUnread(TLFunction["bool"]):
    """The TL function messages.markDialogUnread#8c5006f8, answered with Bool."""

    __slots__ = ("unread", "parent_peer", "peer",)

    ID = 0x8C5006F8
    QUALNAME = "functions.messages.MarkDialogUnread"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        unread: bool = False,
        parent_peer: base.InputPeer | None = None,
        peer: base.InputDialogPeer,
    ) -> None:
        self.unread = unread
        self.parent_peer = parent_peer
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.unread:
            flags |= 1 << 0
        if self.parent_peer is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        unread = bool(flags & (1 << 0))
        parent_peer = r.read_object() if flags & (1 << 1) else None
        peer = r.read_object()
        self = cls.__new__(cls)
        self.unread = unread
        self.parent_peer = parent_peer
        self.peer = peer
        return self


class GetDialogUnreadMarks(TLFunction["list[base.DialogPeer]"]):
    """The TL function messages.getDialogUnreadMarks#21202222, answered with Vector<DialogPeer>."""

    __slots__ = ("parent_peer",)

    ID = 0x21202222
    QUALNAME = "functions.messages.GetDialogUnreadMarks"
    RESULT = "Vector<DialogPeer>"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer | None = None,
    ) -> None:
        self.parent_peer = parent_peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.parent_peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        parent_peer = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        return self


class ClearAllDrafts(TLFunction["bool"]):
    """The TL function messages.clearAllDrafts#7e58ee9c, answered with Bool."""

    __slots__ = ()

    ID = 0x7E58EE9C
    QUALNAME = "functions.messages.ClearAllDrafts"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UpdatePinnedMessage(TLFunction["base.Updates"]):
    """The TL function messages.updatePinnedMessage#d2aaf7ec, answered with Updates."""

    __slots__ = ("silent", "unpin", "pm_oneside", "peer", "id",)

    ID = 0xD2AAF7EC
    QUALNAME = "functions.messages.UpdatePinnedMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        silent: bool = False,
        unpin: bool = False,
        pm_oneside: bool = False,
        peer: base.InputPeer,
        id: int,
    ) -> None:
        self.silent = silent
        self.unpin = unpin
        self.pm_oneside = pm_oneside
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 0
        if self.unpin:
            flags |= 1 << 1
        if self.pm_oneside:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 0))
        unpin = bool(flags & (1 << 1))
        pm_oneside = bool(flags & (1 << 2))
        peer = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.silent = silent
        self.unpin = unpin
        self.pm_oneside = pm_oneside
        self.peer = peer
        self.id = id
        return self


class SendVote(TLFunction["base.Updates"]):
    """The TL function messages.sendVote#10ea6184, answered with Updates."""

    __slots__ = ("peer", "msg_id", "options",)

    ID = 0x10EA6184
    QUALNAME = "functions.messages.SendVote"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        options: list[bytes],
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.options = options

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_vector(self.options, TLWriter.write_bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        options = r.read_vector(TLReader.read_bytes)
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.options = options
        return self


class GetPollResults(TLFunction["base.Updates"]):
    """The TL function messages.getPollResults#eda3e33b, answered with Updates."""

    __slots__ = ("peer", "msg_id", "poll_hash",)

    ID = 0xEDA3E33B
    QUALNAME = "functions.messages.GetPollResults"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        poll_hash: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.poll_hash = poll_hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_long(self.poll_hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        poll_hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.poll_hash = poll_hash
        return self


class GetOnlines(TLFunction["base.ChatOnlines"]):
    """The TL function messages.getOnlines#6e2be050, answered with ChatOnlines."""

    __slots__ = ("peer",)

    ID = 0x6E2BE050
    QUALNAME = "functions.messages.GetOnlines"
    RESULT = "ChatOnlines"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class EditChatAbout(TLFunction["bool"]):
    """The TL function messages.editChatAbout#def60797, answered with Bool."""

    __slots__ = ("peer", "about",)

    ID = 0xDEF60797
    QUALNAME = "functions.messages.EditChatAbout"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        about: str,
    ) -> None:
        self.peer = peer
        self.about = about

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.about)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        about = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.about = about
        return self


class EditChatDefaultBannedRights(TLFunction["base.Updates"]):
    """The TL function messages.editChatDefaultBannedRights#a5866b41, answered with Updates."""

    __slots__ = ("peer", "banned_rights",)

    ID = 0xA5866B41
    QUALNAME = "functions.messages.EditChatDefaultBannedRights"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        banned_rights: base.ChatBannedRights,
    ) -> None:
        self.peer = peer
        self.banned_rights = banned_rights

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.banned_rights.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        banned_rights = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.banned_rights = banned_rights
        return self


class GetEmojiKeywords(TLFunction["base.EmojiKeywordsDifference"]):
    """The TL function messages.getEmojiKeywords#35a0e062, answered with EmojiKeywordsDifference."""

    __slots__ = ("lang_code",)

    ID = 0x35A0E062
    QUALNAME = "functions.messages.GetEmojiKeywords"
    RESULT = "EmojiKeywordsDifference"

    def __init__(
        self,
        *,
        lang_code: str,
    ) -> None:
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.lang_code = lang_code
        return self


class GetEmojiKeywordsDifference(TLFunction["base.EmojiKeywordsDifference"]):
    """The TL function messages.getEmojiKeywordsDifference#1508b6af, answered with EmojiKeywordsDifference."""

    __slots__ = ("lang_code", "from_version",)

    ID = 0x1508B6AF
    QUALNAME = "functions.messages.GetEmojiKeywordsDifference"
    RESULT = "EmojiKeywordsDifference"

    def __init__(
        self,
        *,
        lang_code: str,
        from_version: int,
    ) -> None:
        self.lang_code = lang_code
        self.from_version = from_version

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_code)
        w.write_int(self.from_version)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_code = r.read_string()
        from_version = r.read_int()
        self = cls.__new__(cls)
        self.lang_code = lang_code
        self.from_version = from_version
        return self


class GetEmojiKeywordsLanguages(TLFunction["list[base.EmojiLanguage]"]):
    """The TL function messages.getEmojiKeywordsLanguages#4e9963b2, answered with Vector<EmojiLanguage>."""

    __slots__ = ("lang_codes",)

    ID = 0x4E9963B2
    QUALNAME = "functions.messages.GetEmojiKeywordsLanguages"
    RESULT = "Vector<EmojiLanguage>"

    def __init__(
        self,
        *,
        lang_codes: list[str],
    ) -> None:
        self.lang_codes = lang_codes

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.lang_codes, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_codes = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.lang_codes = lang_codes
        return self


class GetEmojiURL(TLFunction["base.EmojiURL"]):
    """The TL function messages.getEmojiURL#d5b10c26, answered with EmojiURL."""

    __slots__ = ("lang_code",)

    ID = 0xD5B10C26
    QUALNAME = "functions.messages.GetEmojiURL"
    RESULT = "EmojiURL"

    def __init__(
        self,
        *,
        lang_code: str,
    ) -> None:
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.lang_code = lang_code
        return self


class GetSearchCounters(TLFunction["list[base.messages.SearchCounter]"]):
    """The TL function messages.getSearchCounters#1bbcf300, answered with Vector<messages.SearchCounter>."""

    __slots__ = ("peer", "saved_peer_id", "top_msg_id", "filters",)

    ID = 0x1BBCF300
    QUALNAME = "functions.messages.GetSearchCounters"
    RESULT = "Vector<messages.SearchCounter>"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        saved_peer_id: base.InputPeer | None = None,
        top_msg_id: int | None = None,
        filters: list[base.MessagesFilter],
    ) -> None:
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.top_msg_id = top_msg_id
        self.filters = filters

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.saved_peer_id is not None:
            flags |= 1 << 2
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        w.write_vector(self.filters)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        saved_peer_id = r.read_object() if flags & (1 << 2) else None
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        filters = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.top_msg_id = top_msg_id
        self.filters = filters
        return self


class RequestUrlAuth(TLFunction["base.UrlAuthResult"]):
    """The TL function messages.requestUrlAuth#894cc99c, answered with UrlAuthResult."""

    __slots__ = ("peer", "msg_id", "button_id", "url", "in_app_origin",)

    ID = 0x894CC99C
    QUALNAME = "functions.messages.RequestUrlAuth"
    RESULT = "UrlAuthResult"

    def __init__(
        self,
        *,
        peer: base.InputPeer | None = None,
        msg_id: int | None = None,
        button_id: int | None = None,
        url: str | None = None,
        in_app_origin: str | None = None,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.button_id = button_id
        self.url = url
        self.in_app_origin = in_app_origin

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.peer is not None:
            flags |= 1 << 1
        if self.msg_id is not None:
            flags |= 1 << 1
        if self.button_id is not None:
            flags |= 1 << 1
        if self.url is not None:
            flags |= 1 << 2
        if self.in_app_origin is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        if self.msg_id is not None:
            w.write_int(self.msg_id)
        if self.button_id is not None:
            w.write_int(self.button_id)
        if self.url is not None:
            w.write_string(self.url)
        if self.in_app_origin is not None:
            w.write_string(self.in_app_origin)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object() if flags & (1 << 1) else None
        msg_id = r.read_int() if flags & (1 << 1) else None
        button_id = r.read_int() if flags & (1 << 1) else None
        url = r.read_string() if flags & (1 << 2) else None
        in_app_origin = r.read_string() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.button_id = button_id
        self.url = url
        self.in_app_origin = in_app_origin
        return self


class AcceptUrlAuth(TLFunction["base.UrlAuthResult"]):
    """The TL function messages.acceptUrlAuth#67a3f0de, answered with UrlAuthResult."""

    __slots__ = ("write_allowed", "share_phone_number", "peer", "msg_id", "button_id", "url", "match_code",)

    ID = 0x67A3F0DE
    QUALNAME = "functions.messages.AcceptUrlAuth"
    RESULT = "UrlAuthResult"

    def __init__(
        self,
        *,
        write_allowed: bool = False,
        share_phone_number: bool = False,
        peer: base.InputPeer | None = None,
        msg_id: int | None = None,
        button_id: int | None = None,
        url: str | None = None,
        match_code: str | None = None,
    ) -> None:
        self.write_allowed = write_allowed
        self.share_phone_number = share_phone_number
        self.peer = peer
        self.msg_id = msg_id
        self.button_id = button_id
        self.url = url
        self.match_code = match_code

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.write_allowed:
            flags |= 1 << 0
        if self.share_phone_number:
            flags |= 1 << 3
        if self.peer is not None:
            flags |= 1 << 1
        if self.msg_id is not None:
            flags |= 1 << 1
        if self.button_id is not None:
            flags |= 1 << 1
        if self.url is not None:
            flags |= 1 << 2
        if self.match_code is not None:
            flags |= 1 << 4
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        if self.msg_id is not None:
            w.write_int(self.msg_id)
        if self.button_id is not None:
            w.write_int(self.button_id)
        if self.url is not None:
            w.write_string(self.url)
        if self.match_code is not None:
            w.write_string(self.match_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        write_allowed = bool(flags & (1 << 0))
        share_phone_number = bool(flags & (1 << 3))
        peer = r.read_object() if flags & (1 << 1) else None
        msg_id = r.read_int() if flags & (1 << 1) else None
        button_id = r.read_int() if flags & (1 << 1) else None
        url = r.read_string() if flags & (1 << 2) else None
        match_code = r.read_string() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.write_allowed = write_allowed
        self.share_phone_number = share_phone_number
        self.peer = peer
        self.msg_id = msg_id
        self.button_id = button_id
        self.url = url
        self.match_code = match_code
        return self


class HidePeerSettingsBar(TLFunction["bool"]):
    """The TL function messages.hidePeerSettingsBar#4facb138, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0x4FACB138
    QUALNAME = "functions.messages.HidePeerSettingsBar"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class GetScheduledHistory(TLFunction["base.messages.Messages"]):
    """The TL function messages.getScheduledHistory#f516760b, answered with messages.Messages."""

    __slots__ = ("peer", "hash",)

    ID = 0xF516760B
    QUALNAME = "functions.messages.GetScheduledHistory"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        hash: int,
    ) -> None:
        self.peer = peer
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.hash = hash
        return self


class GetScheduledMessages(TLFunction["base.messages.Messages"]):
    """The TL function messages.getScheduledMessages#bdbb0464, answered with messages.Messages."""

    __slots__ = ("peer", "id",)

    ID = 0xBDBB0464
    QUALNAME = "functions.messages.GetScheduledMessages"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class SendScheduledMessages(TLFunction["base.Updates"]):
    """The TL function messages.sendScheduledMessages#bd38850a, answered with Updates."""

    __slots__ = ("peer", "id",)

    ID = 0xBD38850A
    QUALNAME = "functions.messages.SendScheduledMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class DeleteScheduledMessages(TLFunction["base.Updates"]):
    """The TL function messages.deleteScheduledMessages#59ae2b16, answered with Updates."""

    __slots__ = ("peer", "id",)

    ID = 0x59AE2B16
    QUALNAME = "functions.messages.DeleteScheduledMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class GetPollVotes(TLFunction["base.messages.VotesList"]):
    """The TL function messages.getPollVotes#b86e380e, answered with messages.VotesList."""

    __slots__ = ("peer", "id", "option", "offset", "limit",)

    ID = 0xB86E380E
    QUALNAME = "functions.messages.GetPollVotes"
    RESULT = "messages.VotesList"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        option: bytes | None = None,
        offset: str | None = None,
        limit: int,
    ) -> None:
        self.peer = peer
        self.id = id
        self.option = option
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.option is not None:
            flags |= 1 << 0
        if self.offset is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.option is not None:
            w.write_bytes(self.option)
        if self.offset is not None:
            w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        id = r.read_int()
        option = r.read_bytes() if flags & (1 << 0) else None
        offset = r.read_string() if flags & (1 << 1) else None
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.option = option
        self.offset = offset
        self.limit = limit
        return self


class ToggleStickerSets(TLFunction["bool"]):
    """The TL function messages.toggleStickerSets#b5052fea, answered with Bool."""

    __slots__ = ("uninstall", "archive", "unarchive", "stickersets",)

    ID = 0xB5052FEA
    QUALNAME = "functions.messages.ToggleStickerSets"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        uninstall: bool = False,
        archive: bool = False,
        unarchive: bool = False,
        stickersets: list[base.InputStickerSet],
    ) -> None:
        self.uninstall = uninstall
        self.archive = archive
        self.unarchive = unarchive
        self.stickersets = stickersets

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.uninstall:
            flags |= 1 << 0
        if self.archive:
            flags |= 1 << 1
        if self.unarchive:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_vector(self.stickersets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        uninstall = bool(flags & (1 << 0))
        archive = bool(flags & (1 << 1))
        unarchive = bool(flags & (1 << 2))
        stickersets = r.read_vector()
        self = cls.__new__(cls)
        self.uninstall = uninstall
        self.archive = archive
        self.unarchive = unarchive
        self.stickersets = stickersets
        return self


class GetDialogFilters(TLFunction["base.messages.DialogFilters"]):
    """The TL function messages.getDialogFilters#efd48c89, answered with messages.DialogFilters."""

    __slots__ = ()

    ID = 0xEFD48C89
    QUALNAME = "functions.messages.GetDialogFilters"
    RESULT = "messages.DialogFilters"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSuggestedDialogFilters(TLFunction["list[base.DialogFilterSuggested]"]):
    """The TL function messages.getSuggestedDialogFilters#a29cd42c, answered with Vector<DialogFilterSuggested>."""

    __slots__ = ()

    ID = 0xA29CD42C
    QUALNAME = "functions.messages.GetSuggestedDialogFilters"
    RESULT = "Vector<DialogFilterSuggested>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UpdateDialogFilter(TLFunction["bool"]):
    """The TL function messages.updateDialogFilter#1ad4a04a, answered with Bool."""

    __slots__ = ("id", "filter",)

    ID = 0x1AD4A04A
    QUALNAME = "functions.messages.UpdateDialogFilter"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: int,
        filter: base.DialogFilter | None = None,
    ) -> None:
        self.id = id
        self.filter = filter

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.filter is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.id)
        if self.filter is not None:
            self.filter.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        id = r.read_int()
        filter = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.id = id
        self.filter = filter
        return self


class UpdateDialogFiltersOrder(TLFunction["bool"]):
    """The TL function messages.updateDialogFiltersOrder#c563c1e4, answered with Bool."""

    __slots__ = ("order",)

    ID = 0xC563C1E4
    QUALNAME = "functions.messages.UpdateDialogFiltersOrder"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        order: list[int],
    ) -> None:
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        order = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.order = order
        return self


_PACK_GetOldFeaturedStickers = struct.Struct("<iiq")


class GetOldFeaturedStickers(TLFunction["base.messages.FeaturedStickers"]):
    """The TL function messages.getOldFeaturedStickers#7ed094a1, answered with messages.FeaturedStickers."""

    __slots__ = ("offset", "limit", "hash",)

    ID = 0x7ED094A1
    QUALNAME = "functions.messages.GetOldFeaturedStickers"
    RESULT = "messages.FeaturedStickers"

    def __init__(
        self,
        *,
        offset: int,
        limit: int,
        hash: int,
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_GetOldFeaturedStickers.pack(self.offset, self.limit, self.hash))
        except struct.error:
            w.write_int(self.offset)
            w.write_int(self.limit)
            w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offset = r.read_int()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class GetReplies(TLFunction["base.messages.Messages"]):
    """The TL function messages.getReplies#22ddd30c, answered with messages.Messages."""

    __slots__ = ("peer", "msg_id", "offset_id", "offset_date", "add_offset", "limit", "max_id", "min_id", "hash",)

    ID = 0x22DDD30C
    QUALNAME = "functions.messages.GetReplies"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        offset_id: int,
        offset_date: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
        hash: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_int(self.offset_id)
        w.write_int(self.offset_date)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        offset_id = r.read_int()
        offset_date = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash
        return self


class GetDiscussionMessage(TLFunction["base.messages.DiscussionMessage"]):
    """The TL function messages.getDiscussionMessage#446972fd, answered with messages.DiscussionMessage."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x446972FD
    QUALNAME = "functions.messages.GetDiscussionMessage"
    RESULT = "messages.DiscussionMessage"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class ReadDiscussion(TLFunction["bool"]):
    """The TL function messages.readDiscussion#f731a9f4, answered with Bool."""

    __slots__ = ("peer", "msg_id", "read_max_id",)

    ID = 0xF731A9F4
    QUALNAME = "functions.messages.ReadDiscussion"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        read_max_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.read_max_id = read_max_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_int(self.read_max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        read_max_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.read_max_id = read_max_id
        return self


class UnpinAllMessages(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.unpinAllMessages#062dd747, answered with messages.AffectedHistory."""

    __slots__ = ("peer", "top_msg_id", "saved_peer_id",)

    ID = 0x062DD747
    QUALNAME = "functions.messages.UnpinAllMessages"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        saved_peer_id: base.InputPeer | None = None,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        if self.saved_peer_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        saved_peer_id = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id
        return self


class DeleteChat(TLFunction["bool"]):
    """The TL function messages.deleteChat#5bd0ee50, answered with Bool."""

    __slots__ = ("chat_id",)

    ID = 0x5BD0EE50
    QUALNAME = "functions.messages.DeleteChat"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        chat_id: int,
    ) -> None:
        self.chat_id = chat_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.chat_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chat_id = r.read_long()
        self = cls.__new__(cls)
        self.chat_id = chat_id
        return self


class DeletePhoneCallHistory(TLFunction["base.messages.AffectedFoundMessages"]):
    """The TL function messages.deletePhoneCallHistory#f9cbe409, answered with messages.AffectedFoundMessages."""

    __slots__ = ("revoke",)

    ID = 0xF9CBE409
    QUALNAME = "functions.messages.DeletePhoneCallHistory"
    RESULT = "messages.AffectedFoundMessages"

    def __init__(
        self,
        *,
        revoke: bool = False,
    ) -> None:
        self.revoke = revoke

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoke:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoke = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.revoke = revoke
        return self


class CheckHistoryImport(TLFunction["base.messages.HistoryImportParsed"]):
    """The TL function messages.checkHistoryImport#43fe19f3, answered with messages.HistoryImportParsed."""

    __slots__ = ("import_head",)

    ID = 0x43FE19F3
    QUALNAME = "functions.messages.CheckHistoryImport"
    RESULT = "messages.HistoryImportParsed"

    def __init__(
        self,
        *,
        import_head: str,
    ) -> None:
        self.import_head = import_head

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.import_head)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        import_head = r.read_string()
        self = cls.__new__(cls)
        self.import_head = import_head
        return self


class InitHistoryImport(TLFunction["base.messages.HistoryImport"]):
    """The TL function messages.initHistoryImport#34090c3b, answered with messages.HistoryImport."""

    __slots__ = ("peer", "file", "media_count",)

    ID = 0x34090C3B
    QUALNAME = "functions.messages.InitHistoryImport"
    RESULT = "messages.HistoryImport"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        file: base.InputFile,
        media_count: int,
    ) -> None:
        self.peer = peer
        self.file = file
        self.media_count = media_count

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.file.write(w)
        w.write_int(self.media_count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        file = r.read_object()
        media_count = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.file = file
        self.media_count = media_count
        return self


class UploadImportedMedia(TLFunction["base.MessageMedia"]):
    """The TL function messages.uploadImportedMedia#2a862092, answered with MessageMedia."""

    __slots__ = ("peer", "import_id", "file_name", "media",)

    ID = 0x2A862092
    QUALNAME = "functions.messages.UploadImportedMedia"
    RESULT = "MessageMedia"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        import_id: int,
        file_name: str,
        media: base.InputMedia,
    ) -> None:
        self.peer = peer
        self.import_id = import_id
        self.file_name = file_name
        self.media = media

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.import_id)
        w.write_string(self.file_name)
        self.media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        import_id = r.read_long()
        file_name = r.read_string()
        media = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.import_id = import_id
        self.file_name = file_name
        self.media = media
        return self


class StartHistoryImport(TLFunction["bool"]):
    """The TL function messages.startHistoryImport#b43df344, answered with Bool."""

    __slots__ = ("peer", "import_id",)

    ID = 0xB43DF344
    QUALNAME = "functions.messages.StartHistoryImport"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        import_id: int,
    ) -> None:
        self.peer = peer
        self.import_id = import_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_long(self.import_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        import_id = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.import_id = import_id
        return self


class GetExportedChatInvites(TLFunction["base.messages.ExportedChatInvites"]):
    """The TL function messages.getExportedChatInvites#a2b5a3f6, answered with messages.ExportedChatInvites."""

    __slots__ = ("revoked", "peer", "admin_id", "offset_date", "offset_link", "limit",)

    ID = 0xA2B5A3F6
    QUALNAME = "functions.messages.GetExportedChatInvites"
    RESULT = "messages.ExportedChatInvites"

    def __init__(
        self,
        *,
        revoked: bool = False,
        peer: base.InputPeer,
        admin_id: base.InputUser,
        offset_date: int | None = None,
        offset_link: str | None = None,
        limit: int,
    ) -> None:
        self.revoked = revoked
        self.peer = peer
        self.admin_id = admin_id
        self.offset_date = offset_date
        self.offset_link = offset_link
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoked:
            flags |= 1 << 3
        if self.offset_date is not None:
            flags |= 1 << 2
        if self.offset_link is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        self.admin_id.write(w)
        if self.offset_date is not None:
            w.write_int(self.offset_date)
        if self.offset_link is not None:
            w.write_string(self.offset_link)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoked = bool(flags & (1 << 3))
        peer = r.read_object()
        admin_id = r.read_object()
        offset_date = r.read_int() if flags & (1 << 2) else None
        offset_link = r.read_string() if flags & (1 << 2) else None
        limit = r.read_int()
        self = cls.__new__(cls)
        self.revoked = revoked
        self.peer = peer
        self.admin_id = admin_id
        self.offset_date = offset_date
        self.offset_link = offset_link
        self.limit = limit
        return self


class GetExportedChatInvite(TLFunction["base.messages.ExportedChatInvite"]):
    """The TL function messages.getExportedChatInvite#73746f5c, answered with messages.ExportedChatInvite."""

    __slots__ = ("peer", "link",)

    ID = 0x73746F5C
    QUALNAME = "functions.messages.GetExportedChatInvite"
    RESULT = "messages.ExportedChatInvite"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        link: str,
    ) -> None:
        self.peer = peer
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.link)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        link = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.link = link
        return self


class EditExportedChatInvite(TLFunction["base.messages.ExportedChatInvite"]):
    """The TL function messages.editExportedChatInvite#bdca2f75, answered with messages.ExportedChatInvite."""

    __slots__ = ("revoked", "peer", "link", "expire_date", "usage_limit", "request_needed", "title",)

    ID = 0xBDCA2F75
    QUALNAME = "functions.messages.EditExportedChatInvite"
    RESULT = "messages.ExportedChatInvite"

    def __init__(
        self,
        *,
        revoked: bool = False,
        peer: base.InputPeer,
        link: str,
        expire_date: int | None = None,
        usage_limit: int | None = None,
        request_needed: bool | None = None,
        title: str | None = None,
    ) -> None:
        self.revoked = revoked
        self.peer = peer
        self.link = link
        self.expire_date = expire_date
        self.usage_limit = usage_limit
        self.request_needed = request_needed
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.revoked:
            flags |= 1 << 2
        if self.expire_date is not None:
            flags |= 1 << 0
        if self.usage_limit is not None:
            flags |= 1 << 1
        if self.request_needed is not None:
            flags |= 1 << 3
        if self.title is not None:
            flags |= 1 << 4
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.link)
        if self.expire_date is not None:
            w.write_int(self.expire_date)
        if self.usage_limit is not None:
            w.write_int(self.usage_limit)
        if self.request_needed is not None:
            w.write_bool(self.request_needed)
        if self.title is not None:
            w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        revoked = bool(flags & (1 << 2))
        peer = r.read_object()
        link = r.read_string()
        expire_date = r.read_int() if flags & (1 << 0) else None
        usage_limit = r.read_int() if flags & (1 << 1) else None
        request_needed = r.read_bool() if flags & (1 << 3) else None
        title = r.read_string() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.revoked = revoked
        self.peer = peer
        self.link = link
        self.expire_date = expire_date
        self.usage_limit = usage_limit
        self.request_needed = request_needed
        self.title = title
        return self


class DeleteRevokedExportedChatInvites(TLFunction["bool"]):
    """The TL function messages.deleteRevokedExportedChatInvites#56987bd5, answered with Bool."""

    __slots__ = ("peer", "admin_id",)

    ID = 0x56987BD5
    QUALNAME = "functions.messages.DeleteRevokedExportedChatInvites"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        admin_id: base.InputUser,
    ) -> None:
        self.peer = peer
        self.admin_id = admin_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.admin_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        admin_id = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.admin_id = admin_id
        return self


class DeleteExportedChatInvite(TLFunction["bool"]):
    """The TL function messages.deleteExportedChatInvite#d464a42b, answered with Bool."""

    __slots__ = ("peer", "link",)

    ID = 0xD464A42B
    QUALNAME = "functions.messages.DeleteExportedChatInvite"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        link: str,
    ) -> None:
        self.peer = peer
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.link)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        link = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.link = link
        return self


class GetAdminsWithInvites(TLFunction["base.messages.ChatAdminsWithInvites"]):
    """The TL function messages.getAdminsWithInvites#3920e6ef, answered with messages.ChatAdminsWithInvites."""

    __slots__ = ("peer",)

    ID = 0x3920E6EF
    QUALNAME = "functions.messages.GetAdminsWithInvites"
    RESULT = "messages.ChatAdminsWithInvites"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class GetChatInviteImporters(TLFunction["base.messages.ChatInviteImporters"]):
    """The TL function messages.getChatInviteImporters#df04dd4e, answered with messages.ChatInviteImporters."""

    __slots__ = ("requested", "subscription_expired", "peer", "link", "q", "offset_date", "offset_user", "limit",)

    ID = 0xDF04DD4E
    QUALNAME = "functions.messages.GetChatInviteImporters"
    RESULT = "messages.ChatInviteImporters"

    def __init__(
        self,
        *,
        requested: bool = False,
        subscription_expired: bool = False,
        peer: base.InputPeer,
        link: str | None = None,
        q: str | None = None,
        offset_date: int,
        offset_user: base.InputUser,
        limit: int,
    ) -> None:
        self.requested = requested
        self.subscription_expired = subscription_expired
        self.peer = peer
        self.link = link
        self.q = q
        self.offset_date = offset_date
        self.offset_user = offset_user
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.requested:
            flags |= 1 << 0
        if self.subscription_expired:
            flags |= 1 << 3
        if self.link is not None:
            flags |= 1 << 1
        if self.q is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        if self.link is not None:
            w.write_string(self.link)
        if self.q is not None:
            w.write_string(self.q)
        w.write_int(self.offset_date)
        self.offset_user.write(w)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        requested = bool(flags & (1 << 0))
        subscription_expired = bool(flags & (1 << 3))
        peer = r.read_object()
        link = r.read_string() if flags & (1 << 1) else None
        q = r.read_string() if flags & (1 << 2) else None
        offset_date = r.read_int()
        offset_user = r.read_object()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.requested = requested
        self.subscription_expired = subscription_expired
        self.peer = peer
        self.link = link
        self.q = q
        self.offset_date = offset_date
        self.offset_user = offset_user
        self.limit = limit
        return self


class SetHistoryTTL(TLFunction["base.Updates"]):
    """The TL function messages.setHistoryTTL#b80e5fe4, answered with Updates."""

    __slots__ = ("peer", "period",)

    ID = 0xB80E5FE4
    QUALNAME = "functions.messages.SetHistoryTTL"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        period: int,
    ) -> None:
        self.peer = peer
        self.period = period

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        period = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.period = period
        return self


class CheckHistoryImportPeer(TLFunction["base.messages.CheckedHistoryImportPeer"]):
    """The TL function messages.checkHistoryImportPeer#5dc60f03, answered with messages.CheckedHistoryImportPeer."""

    __slots__ = ("peer",)

    ID = 0x5DC60F03
    QUALNAME = "functions.messages.CheckHistoryImportPeer"
    RESULT = "messages.CheckedHistoryImportPeer"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class SetChatTheme(TLFunction["base.Updates"]):
    """The TL function messages.setChatTheme#081202c9, answered with Updates."""

    __slots__ = ("peer", "theme",)

    ID = 0x081202C9
    QUALNAME = "functions.messages.SetChatTheme"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        theme: base.InputChatTheme,
    ) -> None:
        self.peer = peer
        self.theme = theme

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.theme.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        theme = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.theme = theme
        return self


class GetMessageReadParticipants(TLFunction["list[base.ReadParticipantDate]"]):
    """The TL function messages.getMessageReadParticipants#31c1c44f, answered with Vector<ReadParticipantDate>."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x31C1C44F
    QUALNAME = "functions.messages.GetMessageReadParticipants"
    RESULT = "Vector<ReadParticipantDate>"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class GetSearchResultsCalendar(TLFunction["base.messages.SearchResultsCalendar"]):
    """The TL function messages.getSearchResultsCalendar#6aa3f6bd, answered with messages.SearchResultsCalendar."""

    __slots__ = ("peer", "saved_peer_id", "filter", "offset_id", "offset_date",)

    ID = 0x6AA3F6BD
    QUALNAME = "functions.messages.GetSearchResultsCalendar"
    RESULT = "messages.SearchResultsCalendar"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        saved_peer_id: base.InputPeer | None = None,
        filter: base.MessagesFilter,
        offset_id: int,
        offset_date: int,
    ) -> None:
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.filter = filter
        self.offset_id = offset_id
        self.offset_date = offset_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.saved_peer_id is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)
        self.filter.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.offset_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        saved_peer_id = r.read_object() if flags & (1 << 2) else None
        filter = r.read_object()
        offset_id = r.read_int()
        offset_date = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.filter = filter
        self.offset_id = offset_id
        self.offset_date = offset_date
        return self


class GetSearchResultsPositions(TLFunction["base.messages.SearchResultsPositions"]):
    """The TL function messages.getSearchResultsPositions#9c7f2f10, answered with messages.SearchResultsPositions."""

    __slots__ = ("peer", "saved_peer_id", "filter", "offset_id", "limit",)

    ID = 0x9C7F2F10
    QUALNAME = "functions.messages.GetSearchResultsPositions"
    RESULT = "messages.SearchResultsPositions"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        saved_peer_id: base.InputPeer | None = None,
        filter: base.MessagesFilter,
        offset_id: int,
        limit: int,
    ) -> None:
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.filter = filter
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.saved_peer_id is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)
        self.filter.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        saved_peer_id = r.read_object() if flags & (1 << 2) else None
        filter = r.read_object()
        offset_id = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.saved_peer_id = saved_peer_id
        self.filter = filter
        self.offset_id = offset_id
        self.limit = limit
        return self


class HideChatJoinRequest(TLFunction["base.Updates"]):
    """The TL function messages.hideChatJoinRequest#7fe7e815, answered with Updates."""

    __slots__ = ("approved", "peer", "user_id",)

    ID = 0x7FE7E815
    QUALNAME = "functions.messages.HideChatJoinRequest"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        approved: bool = False,
        peer: base.InputPeer,
        user_id: base.InputUser,
    ) -> None:
        self.approved = approved
        self.peer = peer
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.approved:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        approved = bool(flags & (1 << 0))
        peer = r.read_object()
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.approved = approved
        self.peer = peer
        self.user_id = user_id
        return self


class HideAllChatJoinRequests(TLFunction["base.Updates"]):
    """The TL function messages.hideAllChatJoinRequests#e085f4ea, answered with Updates."""

    __slots__ = ("approved", "peer", "link",)

    ID = 0xE085F4EA
    QUALNAME = "functions.messages.HideAllChatJoinRequests"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        approved: bool = False,
        peer: base.InputPeer,
        link: str | None = None,
    ) -> None:
        self.approved = approved
        self.peer = peer
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.approved:
            flags |= 1 << 0
        if self.link is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.link is not None:
            w.write_string(self.link)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        approved = bool(flags & (1 << 0))
        peer = r.read_object()
        link = r.read_string() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.approved = approved
        self.peer = peer
        self.link = link
        return self


class ToggleNoForwards(TLFunction["base.Updates"]):
    """The TL function messages.toggleNoForwards#b2081a35, answered with Updates."""

    __slots__ = ("peer", "enabled", "request_msg_id",)

    ID = 0xB2081A35
    QUALNAME = "functions.messages.ToggleNoForwards"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        enabled: bool,
        request_msg_id: int | None = None,
    ) -> None:
        self.peer = peer
        self.enabled = enabled
        self.request_msg_id = request_msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.request_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_bool(self.enabled)
        if self.request_msg_id is not None:
            w.write_int(self.request_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        enabled = r.read_bool()
        request_msg_id = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.enabled = enabled
        self.request_msg_id = request_msg_id
        return self


class SaveDefaultSendAs(TLFunction["bool"]):
    """The TL function messages.saveDefaultSendAs#ccfddf96, answered with Bool."""

    __slots__ = ("peer", "send_as",)

    ID = 0xCCFDDF96
    QUALNAME = "functions.messages.SaveDefaultSendAs"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        send_as: base.InputPeer,
    ) -> None:
        self.peer = peer
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        send_as = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.send_as = send_as
        return self


class SendReaction(TLFunction["base.Updates"]):
    """The TL function messages.sendReaction#d30d78d4, answered with Updates."""

    __slots__ = ("big", "add_to_recent", "peer", "msg_id", "reaction",)

    ID = 0xD30D78D4
    QUALNAME = "functions.messages.SendReaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        big: bool = False,
        add_to_recent: bool = False,
        peer: base.InputPeer,
        msg_id: int,
        reaction: list[base.Reaction] | None = None,
    ) -> None:
        self.big = big
        self.add_to_recent = add_to_recent
        self.peer = peer
        self.msg_id = msg_id
        self.reaction = reaction

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.big:
            flags |= 1 << 1
        if self.add_to_recent:
            flags |= 1 << 2
        if self.reaction is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.msg_id)
        if self.reaction is not None:
            w.write_vector(self.reaction)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        big = bool(flags & (1 << 1))
        add_to_recent = bool(flags & (1 << 2))
        peer = r.read_object()
        msg_id = r.read_int()
        reaction = r.read_vector() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.big = big
        self.add_to_recent = add_to_recent
        self.peer = peer
        self.msg_id = msg_id
        self.reaction = reaction
        return self


class GetMessagesReactions(TLFunction["base.Updates"]):
    """The TL function messages.getMessagesReactions#8bba90e6, answered with Updates."""

    __slots__ = ("peer", "id",)

    ID = 0x8BBA90E6
    QUALNAME = "functions.messages.GetMessagesReactions"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class GetMessageReactionsList(TLFunction["base.messages.MessageReactionsList"]):
    """The TL function messages.getMessageReactionsList#461b3f48, answered with messages.MessageReactionsList."""

    __slots__ = ("peer", "id", "reaction", "offset", "limit",)

    ID = 0x461B3F48
    QUALNAME = "functions.messages.GetMessageReactionsList"
    RESULT = "messages.MessageReactionsList"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        reaction: base.Reaction | None = None,
        offset: str | None = None,
        limit: int,
    ) -> None:
        self.peer = peer
        self.id = id
        self.reaction = reaction
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reaction is not None:
            flags |= 1 << 0
        if self.offset is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.reaction is not None:
            self.reaction.write(w)
        if self.offset is not None:
            w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        id = r.read_int()
        reaction = r.read_object() if flags & (1 << 0) else None
        offset = r.read_string() if flags & (1 << 1) else None
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.reaction = reaction
        self.offset = offset
        self.limit = limit
        return self


class SetChatAvailableReactions(TLFunction["base.Updates"]):
    """The TL function messages.setChatAvailableReactions#864b2581, answered with Updates."""

    __slots__ = ("peer", "available_reactions", "reactions_limit", "paid_enabled",)

    ID = 0x864B2581
    QUALNAME = "functions.messages.SetChatAvailableReactions"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        available_reactions: base.ChatReactions,
        reactions_limit: int | None = None,
        paid_enabled: bool | None = None,
    ) -> None:
        self.peer = peer
        self.available_reactions = available_reactions
        self.reactions_limit = reactions_limit
        self.paid_enabled = paid_enabled

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reactions_limit is not None:
            flags |= 1 << 0
        if self.paid_enabled is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        self.available_reactions.write(w)
        if self.reactions_limit is not None:
            w.write_int(self.reactions_limit)
        if self.paid_enabled is not None:
            w.write_bool(self.paid_enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        available_reactions = r.read_object()
        reactions_limit = r.read_int() if flags & (1 << 0) else None
        paid_enabled = r.read_bool() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.available_reactions = available_reactions
        self.reactions_limit = reactions_limit
        self.paid_enabled = paid_enabled
        return self


class GetAvailableReactions(TLFunction["base.messages.AvailableReactions"]):
    """The TL function messages.getAvailableReactions#18dea0ac, answered with messages.AvailableReactions."""

    __slots__ = ("hash",)

    ID = 0x18DEA0AC
    QUALNAME = "functions.messages.GetAvailableReactions"
    RESULT = "messages.AvailableReactions"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SetDefaultReaction(TLFunction["bool"]):
    """The TL function messages.setDefaultReaction#4f47a016, answered with Bool."""

    __slots__ = ("reaction",)

    ID = 0x4F47A016
    QUALNAME = "functions.messages.SetDefaultReaction"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        reaction: base.Reaction,
    ) -> None:
        self.reaction = reaction

    def write_body(self, w: TLWriter) -> None:
        self.reaction.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        reaction = r.read_object()
        self = cls.__new__(cls)
        self.reaction = reaction
        return self


class TranslateText(TLFunction["base.messages.TranslatedText"]):
    """The TL function messages.translateText#a5eec345, answered with messages.TranslatedText."""

    __slots__ = ("peer", "id", "text", "to_lang", "tone",)

    ID = 0xA5EEC345
    QUALNAME = "functions.messages.TranslateText"
    RESULT = "messages.TranslatedText"

    def __init__(
        self,
        *,
        peer: base.InputPeer | None = None,
        id: list[int] | None = None,
        text: list[base.TextWithEntities] | None = None,
        to_lang: str,
        tone: str | None = None,
    ) -> None:
        self.peer = peer
        self.id = id
        self.text = text
        self.to_lang = to_lang
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.peer is not None:
            flags |= 1 << 0
        if self.id is not None:
            flags |= 1 << 0
        if self.text is not None:
            flags |= 1 << 1
        if self.tone is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        if self.id is not None:
            w.write_vector(self.id, TLWriter.write_int)
        if self.text is not None:
            w.write_vector(self.text)
        w.write_string(self.to_lang)
        if self.tone is not None:
            w.write_string(self.tone)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object() if flags & (1 << 0) else None
        id = r.read_vector(TLReader.read_int) if flags & (1 << 0) else None
        text = r.read_vector() if flags & (1 << 1) else None
        to_lang = r.read_string()
        tone = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.text = text
        self.to_lang = to_lang
        self.tone = tone
        return self


class GetUnreadReactions(TLFunction["base.messages.Messages"]):
    """The TL function messages.getUnreadReactions#bd7f90ac, answered with messages.Messages."""

    __slots__ = ("peer", "top_msg_id", "saved_peer_id", "offset_id", "add_offset", "limit", "max_id", "min_id",)

    ID = 0xBD7F90AC
    QUALNAME = "functions.messages.GetUnreadReactions"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        saved_peer_id: base.InputPeer | None = None,
        offset_id: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        if self.saved_peer_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        saved_peer_id = r.read_object() if flags & (1 << 1) else None
        offset_id = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        return self


class ReadReactions(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.readReactions#9ec44f93, answered with messages.AffectedHistory."""

    __slots__ = ("peer", "top_msg_id", "saved_peer_id",)

    ID = 0x9EC44F93
    QUALNAME = "functions.messages.ReadReactions"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        saved_peer_id: base.InputPeer | None = None,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        if self.saved_peer_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        if self.saved_peer_id is not None:
            self.saved_peer_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        saved_peer_id = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.saved_peer_id = saved_peer_id
        return self


class SearchSentMedia(TLFunction["base.messages.Messages"]):
    """The TL function messages.searchSentMedia#107e31a0, answered with messages.Messages."""

    __slots__ = ("q", "filter", "limit",)

    ID = 0x107E31A0
    QUALNAME = "functions.messages.SearchSentMedia"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        q: str,
        filter: base.MessagesFilter,
        limit: int,
    ) -> None:
        self.q = q
        self.filter = filter
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.q)
        self.filter.write(w)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        q = r.read_string()
        filter = r.read_object()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.q = q
        self.filter = filter
        self.limit = limit
        return self


class GetAttachMenuBots(TLFunction["base.AttachMenuBots"]):
    """The TL function messages.getAttachMenuBots#16fcc2cb, answered with AttachMenuBots."""

    __slots__ = ("hash",)

    ID = 0x16FCC2CB
    QUALNAME = "functions.messages.GetAttachMenuBots"
    RESULT = "AttachMenuBots"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetAttachMenuBot(TLFunction["base.AttachMenuBotsBot"]):
    """The TL function messages.getAttachMenuBot#77216192, answered with AttachMenuBotsBot."""

    __slots__ = ("bot",)

    ID = 0x77216192
    QUALNAME = "functions.messages.GetAttachMenuBot"
    RESULT = "AttachMenuBotsBot"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class ToggleBotInAttachMenu(TLFunction["bool"]):
    """The TL function messages.toggleBotInAttachMenu#69f59d69, answered with Bool."""

    __slots__ = ("write_allowed", "bot", "enabled",)

    ID = 0x69F59D69
    QUALNAME = "functions.messages.ToggleBotInAttachMenu"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        write_allowed: bool = False,
        bot: base.InputUser,
        enabled: bool,
    ) -> None:
        self.write_allowed = write_allowed
        self.bot = bot
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.write_allowed:
            flags |= 1 << 0
        w.write_int(flags)
        self.bot.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        write_allowed = bool(flags & (1 << 0))
        bot = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.write_allowed = write_allowed
        self.bot = bot
        self.enabled = enabled
        return self


class RequestWebView(TLFunction["base.WebViewResult"]):
    """The TL function messages.requestWebView#269dc2c1, answered with WebViewResult."""

    __slots__ = ("from_bot_menu", "silent", "compact", "fullscreen", "peer", "bot", "url", "start_param", "theme_params", "platform", "reply_to", "send_as",)

    ID = 0x269DC2C1
    QUALNAME = "functions.messages.RequestWebView"
    RESULT = "WebViewResult"

    def __init__(
        self,
        *,
        from_bot_menu: bool = False,
        silent: bool = False,
        compact: bool = False,
        fullscreen: bool = False,
        peer: base.InputPeer,
        bot: base.InputUser,
        url: str | None = None,
        start_param: str | None = None,
        theme_params: base.DataJSON | None = None,
        platform: str,
        reply_to: base.InputReplyTo | None = None,
        send_as: base.InputPeer | None = None,
    ) -> None:
        self.from_bot_menu = from_bot_menu
        self.silent = silent
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.bot = bot
        self.url = url
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform
        self.reply_to = reply_to
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.from_bot_menu:
            flags |= 1 << 4
        if self.silent:
            flags |= 1 << 5
        if self.compact:
            flags |= 1 << 7
        if self.fullscreen:
            flags |= 1 << 8
        if self.url is not None:
            flags |= 1 << 1
        if self.start_param is not None:
            flags |= 1 << 3
        if self.theme_params is not None:
            flags |= 1 << 2
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.send_as is not None:
            flags |= 1 << 13
        w.write_int(flags)
        self.peer.write(w)
        self.bot.write(w)
        if self.url is not None:
            w.write_string(self.url)
        if self.start_param is not None:
            w.write_string(self.start_param)
        if self.theme_params is not None:
            self.theme_params.write(w)
        w.write_string(self.platform)
        if self.reply_to is not None:
            self.reply_to.write(w)
        if self.send_as is not None:
            self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        from_bot_menu = bool(flags & (1 << 4))
        silent = bool(flags & (1 << 5))
        compact = bool(flags & (1 << 7))
        fullscreen = bool(flags & (1 << 8))
        peer = r.read_object()
        bot = r.read_object()
        url = r.read_string() if flags & (1 << 1) else None
        start_param = r.read_string() if flags & (1 << 3) else None
        theme_params = r.read_object() if flags & (1 << 2) else None
        platform = r.read_string()
        reply_to = r.read_object() if flags & (1 << 0) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        self = cls.__new__(cls)
        self.from_bot_menu = from_bot_menu
        self.silent = silent
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.bot = bot
        self.url = url
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform
        self.reply_to = reply_to
        self.send_as = send_as
        return self


class ProlongWebView(TLFunction["bool"]):
    """The TL function messages.prolongWebView#b0d81a83, answered with Bool."""

    __slots__ = ("silent", "peer", "bot", "query_id", "reply_to", "send_as",)

    ID = 0xB0D81A83
    QUALNAME = "functions.messages.ProlongWebView"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        silent: bool = False,
        peer: base.InputPeer,
        bot: base.InputUser,
        query_id: int,
        reply_to: base.InputReplyTo | None = None,
        send_as: base.InputPeer | None = None,
    ) -> None:
        self.silent = silent
        self.peer = peer
        self.bot = bot
        self.query_id = query_id
        self.reply_to = reply_to
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.send_as is not None:
            flags |= 1 << 13
        w.write_int(flags)
        self.peer.write(w)
        self.bot.write(w)
        w.write_long(self.query_id)
        if self.reply_to is not None:
            self.reply_to.write(w)
        if self.send_as is not None:
            self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        silent = bool(flags & (1 << 5))
        peer = r.read_object()
        bot = r.read_object()
        query_id = r.read_long()
        reply_to = r.read_object() if flags & (1 << 0) else None
        send_as = r.read_object() if flags & (1 << 13) else None
        self = cls.__new__(cls)
        self.silent = silent
        self.peer = peer
        self.bot = bot
        self.query_id = query_id
        self.reply_to = reply_to
        self.send_as = send_as
        return self


class RequestSimpleWebView(TLFunction["base.WebViewResult"]):
    """The TL function messages.requestSimpleWebView#413a3e73, answered with WebViewResult."""

    __slots__ = ("from_switch_webview", "from_side_menu", "compact", "fullscreen", "bot", "url", "start_param", "theme_params", "platform",)

    ID = 0x413A3E73
    QUALNAME = "functions.messages.RequestSimpleWebView"
    RESULT = "WebViewResult"

    def __init__(
        self,
        *,
        from_switch_webview: bool = False,
        from_side_menu: bool = False,
        compact: bool = False,
        fullscreen: bool = False,
        bot: base.InputUser,
        url: str | None = None,
        start_param: str | None = None,
        theme_params: base.DataJSON | None = None,
        platform: str,
    ) -> None:
        self.from_switch_webview = from_switch_webview
        self.from_side_menu = from_side_menu
        self.compact = compact
        self.fullscreen = fullscreen
        self.bot = bot
        self.url = url
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.from_switch_webview:
            flags |= 1 << 1
        if self.from_side_menu:
            flags |= 1 << 2
        if self.compact:
            flags |= 1 << 7
        if self.fullscreen:
            flags |= 1 << 8
        if self.url is not None:
            flags |= 1 << 3
        if self.start_param is not None:
            flags |= 1 << 4
        if self.theme_params is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.bot.write(w)
        if self.url is not None:
            w.write_string(self.url)
        if self.start_param is not None:
            w.write_string(self.start_param)
        if self.theme_params is not None:
            self.theme_params.write(w)
        w.write_string(self.platform)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        from_switch_webview = bool(flags & (1 << 1))
        from_side_menu = bool(flags & (1 << 2))
        compact = bool(flags & (1 << 7))
        fullscreen = bool(flags & (1 << 8))
        bot = r.read_object()
        url = r.read_string() if flags & (1 << 3) else None
        start_param = r.read_string() if flags & (1 << 4) else None
        theme_params = r.read_object() if flags & (1 << 0) else None
        platform = r.read_string()
        self = cls.__new__(cls)
        self.from_switch_webview = from_switch_webview
        self.from_side_menu = from_side_menu
        self.compact = compact
        self.fullscreen = fullscreen
        self.bot = bot
        self.url = url
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform
        return self


class SendWebViewResultMessage(TLFunction["base.WebViewMessageSent"]):
    """The TL function messages.sendWebViewResultMessage#0a4314f5, answered with WebViewMessageSent."""

    __slots__ = ("bot_query_id", "result",)

    ID = 0x0A4314F5
    QUALNAME = "functions.messages.SendWebViewResultMessage"
    RESULT = "WebViewMessageSent"

    def __init__(
        self,
        *,
        bot_query_id: str,
        result: base.InputBotInlineResult,
    ) -> None:
        self.bot_query_id = bot_query_id
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.bot_query_id)
        self.result.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot_query_id = r.read_string()
        result = r.read_object()
        self = cls.__new__(cls)
        self.bot_query_id = bot_query_id
        self.result = result
        return self


class SendWebViewData(TLFunction["base.Updates"]):
    """The TL function messages.sendWebViewData#dc0242c8, answered with Updates."""

    __slots__ = ("bot", "random_id", "button_text", "data",)

    ID = 0xDC0242C8
    QUALNAME = "functions.messages.SendWebViewData"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        random_id: int,
        button_text: str,
        data: str,
    ) -> None:
        self.bot = bot
        self.random_id = random_id
        self.button_text = button_text
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_long(self.random_id)
        w.write_string(self.button_text)
        w.write_string(self.data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        random_id = r.read_long()
        button_text = r.read_string()
        data = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.random_id = random_id
        self.button_text = button_text
        self.data = data
        return self


class TranscribeAudio(TLFunction["base.messages.TranscribedAudio"]):
    """The TL function messages.transcribeAudio#269e9a49, answered with messages.TranscribedAudio."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x269E9A49
    QUALNAME = "functions.messages.TranscribeAudio"
    RESULT = "messages.TranscribedAudio"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class RateTranscribedAudio(TLFunction["bool"]):
    """The TL function messages.rateTranscribedAudio#7f1d072f, answered with Bool."""

    __slots__ = ("peer", "msg_id", "transcription_id", "good",)

    ID = 0x7F1D072F
    QUALNAME = "functions.messages.RateTranscribedAudio"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        transcription_id: int,
        good: bool,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.transcription_id = transcription_id
        self.good = good

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_long(self.transcription_id)
        w.write_bool(self.good)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        transcription_id = r.read_long()
        good = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.transcription_id = transcription_id
        self.good = good
        return self


class GetCustomEmojiDocuments(TLFunction["list[base.Document]"]):
    """The TL function messages.getCustomEmojiDocuments#d9ab0f54, answered with Vector<Document>."""

    __slots__ = ("document_id",)

    ID = 0xD9AB0F54
    QUALNAME = "functions.messages.GetCustomEmojiDocuments"
    RESULT = "Vector<Document>"

    def __init__(
        self,
        *,
        document_id: list[int],
    ) -> None:
        self.document_id = document_id

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.document_id, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        document_id = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.document_id = document_id
        return self


class GetEmojiStickers(TLFunction["base.messages.AllStickers"]):
    """The TL function messages.getEmojiStickers#fbfca18f, answered with messages.AllStickers."""

    __slots__ = ("hash",)

    ID = 0xFBFCA18F
    QUALNAME = "functions.messages.GetEmojiStickers"
    RESULT = "messages.AllStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetFeaturedEmojiStickers(TLFunction["base.messages.FeaturedStickers"]):
    """The TL function messages.getFeaturedEmojiStickers#0ecf6736, answered with messages.FeaturedStickers."""

    __slots__ = ("hash",)

    ID = 0x0ECF6736
    QUALNAME = "functions.messages.GetFeaturedEmojiStickers"
    RESULT = "messages.FeaturedStickers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ReportReaction(TLFunction["bool"]):
    """The TL function messages.reportReaction#3f64c076, answered with Bool."""

    __slots__ = ("peer", "id", "reaction_peer",)

    ID = 0x3F64C076
    QUALNAME = "functions.messages.ReportReaction"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        reaction_peer: base.InputPeer,
    ) -> None:
        self.peer = peer
        self.id = id
        self.reaction_peer = reaction_peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)
        self.reaction_peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        reaction_peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.reaction_peer = reaction_peer
        return self


_PACK_GetTopReactions = struct.Struct("<iq")


class GetTopReactions(TLFunction["base.messages.Reactions"]):
    """The TL function messages.getTopReactions#bb8125ba, answered with messages.Reactions."""

    __slots__ = ("limit", "hash",)

    ID = 0xBB8125BA
    QUALNAME = "functions.messages.GetTopReactions"
    RESULT = "messages.Reactions"

    def __init__(
        self,
        *,
        limit: int,
        hash: int,
    ) -> None:
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_GetTopReactions.pack(self.limit, self.hash))
        except struct.error:
            w.write_int(self.limit)
            w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.limit = limit
        self.hash = hash
        return self


_PACK_GetRecentReactions = struct.Struct("<iq")


class GetRecentReactions(TLFunction["base.messages.Reactions"]):
    """The TL function messages.getRecentReactions#39461db2, answered with messages.Reactions."""

    __slots__ = ("limit", "hash",)

    ID = 0x39461DB2
    QUALNAME = "functions.messages.GetRecentReactions"
    RESULT = "messages.Reactions"

    def __init__(
        self,
        *,
        limit: int,
        hash: int,
    ) -> None:
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_GetRecentReactions.pack(self.limit, self.hash))
        except struct.error:
            w.write_int(self.limit)
            w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.limit = limit
        self.hash = hash
        return self


class ClearRecentReactions(TLFunction["bool"]):
    """The TL function messages.clearRecentReactions#9dfeefb4, answered with Bool."""

    __slots__ = ()

    ID = 0x9DFEEFB4
    QUALNAME = "functions.messages.ClearRecentReactions"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetExtendedMedia(TLFunction["base.Updates"]):
    """The TL function messages.getExtendedMedia#84f80814, answered with Updates."""

    __slots__ = ("peer", "id",)

    ID = 0x84F80814
    QUALNAME = "functions.messages.GetExtendedMedia"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class SetDefaultHistoryTTL(TLFunction["bool"]):
    """The TL function messages.setDefaultHistoryTTL#9eb51445, answered with Bool."""

    __slots__ = ("period",)

    ID = 0x9EB51445
    QUALNAME = "functions.messages.SetDefaultHistoryTTL"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        period: int,
    ) -> None:
        self.period = period

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        period = r.read_int()
        self = cls.__new__(cls)
        self.period = period
        return self


class GetDefaultHistoryTTL(TLFunction["base.DefaultHistoryTTL"]):
    """The TL function messages.getDefaultHistoryTTL#658b7188, answered with DefaultHistoryTTL."""

    __slots__ = ()

    ID = 0x658B7188
    QUALNAME = "functions.messages.GetDefaultHistoryTTL"
    RESULT = "DefaultHistoryTTL"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SendBotRequestedPeer(TLFunction["base.Updates"]):
    """The TL function messages.sendBotRequestedPeer#6c5cf2a7, answered with Updates."""

    __slots__ = ("peer", "msg_id", "webapp_req_id", "button_id", "requested_peers",)

    ID = 0x6C5CF2A7
    QUALNAME = "functions.messages.SendBotRequestedPeer"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int | None = None,
        webapp_req_id: str | None = None,
        button_id: int,
        requested_peers: list[base.InputPeer],
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.webapp_req_id = webapp_req_id
        self.button_id = button_id
        self.requested_peers = requested_peers

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.msg_id is not None:
            flags |= 1 << 0
        if self.webapp_req_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.msg_id is not None:
            w.write_int(self.msg_id)
        if self.webapp_req_id is not None:
            w.write_string(self.webapp_req_id)
        w.write_int(self.button_id)
        w.write_vector(self.requested_peers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        msg_id = r.read_int() if flags & (1 << 0) else None
        webapp_req_id = r.read_string() if flags & (1 << 1) else None
        button_id = r.read_int()
        requested_peers = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.webapp_req_id = webapp_req_id
        self.button_id = button_id
        self.requested_peers = requested_peers
        return self


class GetEmojiGroups(TLFunction["base.messages.EmojiGroups"]):
    """The TL function messages.getEmojiGroups#7488ce5b, answered with messages.EmojiGroups."""

    __slots__ = ("hash",)

    ID = 0x7488CE5B
    QUALNAME = "functions.messages.GetEmojiGroups"
    RESULT = "messages.EmojiGroups"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetEmojiStatusGroups(TLFunction["base.messages.EmojiGroups"]):
    """The TL function messages.getEmojiStatusGroups#2ecd56cd, answered with messages.EmojiGroups."""

    __slots__ = ("hash",)

    ID = 0x2ECD56CD
    QUALNAME = "functions.messages.GetEmojiStatusGroups"
    RESULT = "messages.EmojiGroups"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetEmojiProfilePhotoGroups(TLFunction["base.messages.EmojiGroups"]):
    """The TL function messages.getEmojiProfilePhotoGroups#21a548f3, answered with messages.EmojiGroups."""

    __slots__ = ("hash",)

    ID = 0x21A548F3
    QUALNAME = "functions.messages.GetEmojiProfilePhotoGroups"
    RESULT = "messages.EmojiGroups"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SearchCustomEmoji(TLFunction["base.EmojiList"]):
    """The TL function messages.searchCustomEmoji#2c11c0d7, answered with EmojiList."""

    __slots__ = ("emoticon", "hash",)

    ID = 0x2C11C0D7
    QUALNAME = "functions.messages.SearchCustomEmoji"
    RESULT = "EmojiList"

    def __init__(
        self,
        *,
        emoticon: str,
        hash: int,
    ) -> None:
        self.emoticon = emoticon
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.emoticon)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        emoticon = r.read_string()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.emoticon = emoticon
        self.hash = hash
        return self


class TogglePeerTranslations(TLFunction["bool"]):
    """The TL function messages.togglePeerTranslations#e47cb579, answered with Bool."""

    __slots__ = ("disabled", "peer",)

    ID = 0xE47CB579
    QUALNAME = "functions.messages.TogglePeerTranslations"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        disabled: bool = False,
        peer: base.InputPeer,
    ) -> None:
        self.disabled = disabled
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.disabled:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        disabled = bool(flags & (1 << 0))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.disabled = disabled
        self.peer = peer
        return self


class GetBotApp(TLFunction["base.messages.BotApp"]):
    """The TL function messages.getBotApp#34fdc5c3, answered with messages.BotApp."""

    __slots__ = ("app", "hash",)

    ID = 0x34FDC5C3
    QUALNAME = "functions.messages.GetBotApp"
    RESULT = "messages.BotApp"

    def __init__(
        self,
        *,
        app: base.InputBotApp,
        hash: int,
    ) -> None:
        self.app = app
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.app.write(w)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        app = r.read_object()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.app = app
        self.hash = hash
        return self


class RequestAppWebView(TLFunction["base.WebViewResult"]):
    """The TL function messages.requestAppWebView#53618bce, answered with WebViewResult."""

    __slots__ = ("write_allowed", "compact", "fullscreen", "peer", "app", "start_param", "theme_params", "platform",)

    ID = 0x53618BCE
    QUALNAME = "functions.messages.RequestAppWebView"
    RESULT = "WebViewResult"

    def __init__(
        self,
        *,
        write_allowed: bool = False,
        compact: bool = False,
        fullscreen: bool = False,
        peer: base.InputPeer,
        app: base.InputBotApp,
        start_param: str | None = None,
        theme_params: base.DataJSON | None = None,
        platform: str,
    ) -> None:
        self.write_allowed = write_allowed
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.app = app
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.write_allowed:
            flags |= 1 << 0
        if self.compact:
            flags |= 1 << 7
        if self.fullscreen:
            flags |= 1 << 8
        if self.start_param is not None:
            flags |= 1 << 1
        if self.theme_params is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        self.app.write(w)
        if self.start_param is not None:
            w.write_string(self.start_param)
        if self.theme_params is not None:
            self.theme_params.write(w)
        w.write_string(self.platform)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        write_allowed = bool(flags & (1 << 0))
        compact = bool(flags & (1 << 7))
        fullscreen = bool(flags & (1 << 8))
        peer = r.read_object()
        app = r.read_object()
        start_param = r.read_string() if flags & (1 << 1) else None
        theme_params = r.read_object() if flags & (1 << 2) else None
        platform = r.read_string()
        self = cls.__new__(cls)
        self.write_allowed = write_allowed
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.app = app
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform
        return self


class SetChatWallPaper(TLFunction["base.Updates"]):
    """The TL function messages.setChatWallPaper#8ffacae1, answered with Updates."""

    __slots__ = ("for_both", "revert", "peer", "wallpaper", "settings", "id",)

    ID = 0x8FFACAE1
    QUALNAME = "functions.messages.SetChatWallPaper"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        for_both: bool = False,
        revert: bool = False,
        peer: base.InputPeer,
        wallpaper: base.InputWallPaper | None = None,
        settings: base.WallPaperSettings | None = None,
        id: int | None = None,
    ) -> None:
        self.for_both = for_both
        self.revert = revert
        self.peer = peer
        self.wallpaper = wallpaper
        self.settings = settings
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_both:
            flags |= 1 << 3
        if self.revert:
            flags |= 1 << 4
        if self.wallpaper is not None:
            flags |= 1 << 0
        if self.settings is not None:
            flags |= 1 << 2
        if self.id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.wallpaper is not None:
            self.wallpaper.write(w)
        if self.settings is not None:
            self.settings.write(w)
        if self.id is not None:
            w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_both = bool(flags & (1 << 3))
        revert = bool(flags & (1 << 4))
        peer = r.read_object()
        wallpaper = r.read_object() if flags & (1 << 0) else None
        settings = r.read_object() if flags & (1 << 2) else None
        id = r.read_int() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.for_both = for_both
        self.revert = revert
        self.peer = peer
        self.wallpaper = wallpaper
        self.settings = settings
        self.id = id
        return self


class SearchEmojiStickerSets(TLFunction["base.messages.FoundStickerSets"]):
    """The TL function messages.searchEmojiStickerSets#92b4494c, answered with messages.FoundStickerSets."""

    __slots__ = ("exclude_featured", "q", "hash",)

    ID = 0x92B4494C
    QUALNAME = "functions.messages.SearchEmojiStickerSets"
    RESULT = "messages.FoundStickerSets"

    def __init__(
        self,
        *,
        exclude_featured: bool = False,
        q: str,
        hash: int,
    ) -> None:
        self.exclude_featured = exclude_featured
        self.q = q
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.exclude_featured:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.q)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        exclude_featured = bool(flags & (1 << 0))
        q = r.read_string()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.exclude_featured = exclude_featured
        self.q = q
        self.hash = hash
        return self


class GetSavedDialogs(TLFunction["base.messages.SavedDialogs"]):
    """The TL function messages.getSavedDialogs#1e91fc99, answered with messages.SavedDialogs."""

    __slots__ = ("exclude_pinned", "parent_peer", "offset_date", "offset_id", "offset_peer", "limit", "hash",)

    ID = 0x1E91FC99
    QUALNAME = "functions.messages.GetSavedDialogs"
    RESULT = "messages.SavedDialogs"

    def __init__(
        self,
        *,
        exclude_pinned: bool = False,
        parent_peer: base.InputPeer | None = None,
        offset_date: int,
        offset_id: int,
        offset_peer: base.InputPeer,
        limit: int,
        hash: int,
    ) -> None:
        self.exclude_pinned = exclude_pinned
        self.parent_peer = parent_peer
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_peer = offset_peer
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.exclude_pinned:
            flags |= 1 << 0
        if self.parent_peer is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        w.write_int(self.offset_date)
        w.write_int(self.offset_id)
        self.offset_peer.write(w)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        exclude_pinned = bool(flags & (1 << 0))
        parent_peer = r.read_object() if flags & (1 << 1) else None
        offset_date = r.read_int()
        offset_id = r.read_int()
        offset_peer = r.read_object()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.exclude_pinned = exclude_pinned
        self.parent_peer = parent_peer
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_peer = offset_peer
        self.limit = limit
        self.hash = hash
        return self


class GetSavedHistory(TLFunction["base.messages.Messages"]):
    """The TL function messages.getSavedHistory#998ab009, answered with messages.Messages."""

    __slots__ = ("parent_peer", "peer", "offset_id", "offset_date", "add_offset", "limit", "max_id", "min_id", "hash",)

    ID = 0x998AB009
    QUALNAME = "functions.messages.GetSavedHistory"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer | None = None,
        peer: base.InputPeer,
        offset_id: int,
        offset_date: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
        hash: int,
    ) -> None:
        self.parent_peer = parent_peer
        self.peer = peer
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.parent_peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        self.peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.offset_date)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        parent_peer = r.read_object() if flags & (1 << 0) else None
        peer = r.read_object()
        offset_id = r.read_int()
        offset_date = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        self.peer = peer
        self.offset_id = offset_id
        self.offset_date = offset_date
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash
        return self


class DeleteSavedHistory(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.deleteSavedHistory#4dc5085f, answered with messages.AffectedHistory."""

    __slots__ = ("parent_peer", "peer", "max_id", "min_date", "max_date",)

    ID = 0x4DC5085F
    QUALNAME = "functions.messages.DeleteSavedHistory"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer | None = None,
        peer: base.InputPeer,
        max_id: int,
        min_date: int | None = None,
        max_date: int | None = None,
    ) -> None:
        self.parent_peer = parent_peer
        self.peer = peer
        self.max_id = max_id
        self.min_date = min_date
        self.max_date = max_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.parent_peer is not None:
            flags |= 1 << 0
        if self.min_date is not None:
            flags |= 1 << 2
        if self.max_date is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        self.peer.write(w)
        w.write_int(self.max_id)
        if self.min_date is not None:
            w.write_int(self.min_date)
        if self.max_date is not None:
            w.write_int(self.max_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        parent_peer = r.read_object() if flags & (1 << 0) else None
        peer = r.read_object()
        max_id = r.read_int()
        min_date = r.read_int() if flags & (1 << 2) else None
        max_date = r.read_int() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        self.peer = peer
        self.max_id = max_id
        self.min_date = min_date
        self.max_date = max_date
        return self


class GetPinnedSavedDialogs(TLFunction["base.messages.SavedDialogs"]):
    """The TL function messages.getPinnedSavedDialogs#d63d94e0, answered with messages.SavedDialogs."""

    __slots__ = ()

    ID = 0xD63D94E0
    QUALNAME = "functions.messages.GetPinnedSavedDialogs"
    RESULT = "messages.SavedDialogs"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ToggleSavedDialogPin(TLFunction["bool"]):
    """The TL function messages.toggleSavedDialogPin#ac81bbde, answered with Bool."""

    __slots__ = ("pinned", "peer",)

    ID = 0xAC81BBDE
    QUALNAME = "functions.messages.ToggleSavedDialogPin"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        pinned: bool = False,
        peer: base.InputDialogPeer,
    ) -> None:
        self.pinned = pinned
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pinned:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pinned = bool(flags & (1 << 0))
        peer = r.read_object()
        self = cls.__new__(cls)
        self.pinned = pinned
        self.peer = peer
        return self


class ReorderPinnedSavedDialogs(TLFunction["bool"]):
    """The TL function messages.reorderPinnedSavedDialogs#8b716587, answered with Bool."""

    __slots__ = ("force", "order",)

    ID = 0x8B716587
    QUALNAME = "functions.messages.ReorderPinnedSavedDialogs"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        force: bool = False,
        order: list[base.InputDialogPeer],
    ) -> None:
        self.force = force
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.force:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.order)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        force = bool(flags & (1 << 0))
        order = r.read_vector()
        self = cls.__new__(cls)
        self.force = force
        self.order = order
        return self


class GetSavedReactionTags(TLFunction["base.messages.SavedReactionTags"]):
    """The TL function messages.getSavedReactionTags#3637e05b, answered with messages.SavedReactionTags."""

    __slots__ = ("peer", "hash",)

    ID = 0x3637E05B
    QUALNAME = "functions.messages.GetSavedReactionTags"
    RESULT = "messages.SavedReactionTags"

    def __init__(
        self,
        *,
        peer: base.InputPeer | None = None,
        hash: int,
    ) -> None:
        self.peer = peer
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object() if flags & (1 << 0) else None
        hash = r.read_long()
        self = cls.__new__(cls)
        self.peer = peer
        self.hash = hash
        return self


class UpdateSavedReactionTag(TLFunction["bool"]):
    """The TL function messages.updateSavedReactionTag#60297dec, answered with Bool."""

    __slots__ = ("reaction", "title",)

    ID = 0x60297DEC
    QUALNAME = "functions.messages.UpdateSavedReactionTag"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        reaction: base.Reaction,
        title: str | None = None,
    ) -> None:
        self.reaction = reaction
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.reaction.write(w)
        if self.title is not None:
            w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reaction = r.read_object()
        title = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.reaction = reaction
        self.title = title
        return self


class GetDefaultTagReactions(TLFunction["base.messages.Reactions"]):
    """The TL function messages.getDefaultTagReactions#bdf93428, answered with messages.Reactions."""

    __slots__ = ("hash",)

    ID = 0xBDF93428
    QUALNAME = "functions.messages.GetDefaultTagReactions"
    RESULT = "messages.Reactions"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetOutboxReadDate(TLFunction["base.OutboxReadDate"]):
    """The TL function messages.getOutboxReadDate#8c4bfe5d, answered with OutboxReadDate."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x8C4BFE5D
    QUALNAME = "functions.messages.GetOutboxReadDate"
    RESULT = "OutboxReadDate"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class GetQuickReplies(TLFunction["base.messages.QuickReplies"]):
    """The TL function messages.getQuickReplies#d483f2a8, answered with messages.QuickReplies."""

    __slots__ = ("hash",)

    ID = 0xD483F2A8
    QUALNAME = "functions.messages.GetQuickReplies"
    RESULT = "messages.QuickReplies"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ReorderQuickReplies(TLFunction["bool"]):
    """The TL function messages.reorderQuickReplies#60331907, answered with Bool."""

    __slots__ = ("order",)

    ID = 0x60331907
    QUALNAME = "functions.messages.ReorderQuickReplies"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        order: list[int],
    ) -> None:
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        order = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.order = order
        return self


class CheckQuickReplyShortcut(TLFunction["bool"]):
    """The TL function messages.checkQuickReplyShortcut#f1d0fbd3, answered with Bool."""

    __slots__ = ("shortcut",)

    ID = 0xF1D0FBD3
    QUALNAME = "functions.messages.CheckQuickReplyShortcut"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        shortcut: str,
    ) -> None:
        self.shortcut = shortcut

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.shortcut)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        shortcut = r.read_string()
        self = cls.__new__(cls)
        self.shortcut = shortcut
        return self


class EditQuickReplyShortcut(TLFunction["bool"]):
    """The TL function messages.editQuickReplyShortcut#5c003cef, answered with Bool."""

    __slots__ = ("shortcut_id", "shortcut",)

    ID = 0x5C003CEF
    QUALNAME = "functions.messages.EditQuickReplyShortcut"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        shortcut_id: int,
        shortcut: str,
    ) -> None:
        self.shortcut_id = shortcut_id
        self.shortcut = shortcut

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.shortcut_id)
        w.write_string(self.shortcut)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        shortcut_id = r.read_int()
        shortcut = r.read_string()
        self = cls.__new__(cls)
        self.shortcut_id = shortcut_id
        self.shortcut = shortcut
        return self


class DeleteQuickReplyShortcut(TLFunction["bool"]):
    """The TL function messages.deleteQuickReplyShortcut#3cc04740, answered with Bool."""

    __slots__ = ("shortcut_id",)

    ID = 0x3CC04740
    QUALNAME = "functions.messages.DeleteQuickReplyShortcut"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        shortcut_id: int,
    ) -> None:
        self.shortcut_id = shortcut_id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.shortcut_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        shortcut_id = r.read_int()
        self = cls.__new__(cls)
        self.shortcut_id = shortcut_id
        return self


class GetQuickReplyMessages(TLFunction["base.messages.Messages"]):
    """The TL function messages.getQuickReplyMessages#94a495c3, answered with messages.Messages."""

    __slots__ = ("shortcut_id", "id", "hash",)

    ID = 0x94A495C3
    QUALNAME = "functions.messages.GetQuickReplyMessages"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        shortcut_id: int,
        id: list[int] | None = None,
        hash: int,
    ) -> None:
        self.shortcut_id = shortcut_id
        self.id = id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.shortcut_id)
        if self.id is not None:
            w.write_vector(self.id, TLWriter.write_int)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        shortcut_id = r.read_int()
        id = r.read_vector(TLReader.read_int) if flags & (1 << 0) else None
        hash = r.read_long()
        self = cls.__new__(cls)
        self.shortcut_id = shortcut_id
        self.id = id
        self.hash = hash
        return self


class SendQuickReplyMessages(TLFunction["base.Updates"]):
    """The TL function messages.sendQuickReplyMessages#6c750de1, answered with Updates."""

    __slots__ = ("peer", "shortcut_id", "id", "random_id",)

    ID = 0x6C750DE1
    QUALNAME = "functions.messages.SendQuickReplyMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        shortcut_id: int,
        id: list[int],
        random_id: list[int],
    ) -> None:
        self.peer = peer
        self.shortcut_id = shortcut_id
        self.id = id
        self.random_id = random_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.shortcut_id)
        w.write_vector(self.id, TLWriter.write_int)
        w.write_vector(self.random_id, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        shortcut_id = r.read_int()
        id = r.read_vector(TLReader.read_int)
        random_id = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.peer = peer
        self.shortcut_id = shortcut_id
        self.id = id
        self.random_id = random_id
        return self


class DeleteQuickReplyMessages(TLFunction["base.Updates"]):
    """The TL function messages.deleteQuickReplyMessages#e105e910, answered with Updates."""

    __slots__ = ("shortcut_id", "id",)

    ID = 0xE105E910
    QUALNAME = "functions.messages.DeleteQuickReplyMessages"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        shortcut_id: int,
        id: list[int],
    ) -> None:
        self.shortcut_id = shortcut_id
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.shortcut_id)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        shortcut_id = r.read_int()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.shortcut_id = shortcut_id
        self.id = id
        return self


class ToggleDialogFilterTags(TLFunction["bool"]):
    """The TL function messages.toggleDialogFilterTags#fd2dda49, answered with Bool."""

    __slots__ = ("enabled",)

    ID = 0xFD2DDA49
    QUALNAME = "functions.messages.ToggleDialogFilterTags"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        enabled: bool,
    ) -> None:
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.enabled = enabled
        return self


_PACK_GetMyStickers = struct.Struct("<qi")


class GetMyStickers(TLFunction["base.messages.MyStickers"]):
    """The TL function messages.getMyStickers#d0b5e1fc, answered with messages.MyStickers."""

    __slots__ = ("offset_id", "limit",)

    ID = 0xD0B5E1FC
    QUALNAME = "functions.messages.GetMyStickers"
    RESULT = "messages.MyStickers"

    def __init__(
        self,
        *,
        offset_id: int,
        limit: int,
    ) -> None:
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_GetMyStickers.pack(self.offset_id, self.limit))
        except struct.error:
            w.write_long(self.offset_id)
            w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offset_id = r.read_long()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.offset_id = offset_id
        self.limit = limit
        return self


class GetEmojiStickerGroups(TLFunction["base.messages.EmojiGroups"]):
    """The TL function messages.getEmojiStickerGroups#1dd840f5, answered with messages.EmojiGroups."""

    __slots__ = ("hash",)

    ID = 0x1DD840F5
    QUALNAME = "functions.messages.GetEmojiStickerGroups"
    RESULT = "messages.EmojiGroups"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetAvailableEffects(TLFunction["base.messages.AvailableEffects"]):
    """The TL function messages.getAvailableEffects#dea20a39, answered with messages.AvailableEffects."""

    __slots__ = ("hash",)

    ID = 0xDEA20A39
    QUALNAME = "functions.messages.GetAvailableEffects"
    RESULT = "messages.AvailableEffects"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class EditFactCheck(TLFunction["base.Updates"]):
    """The TL function messages.editFactCheck#0589ee75, answered with Updates."""

    __slots__ = ("peer", "msg_id", "text",)

    ID = 0x0589EE75
    QUALNAME = "functions.messages.EditFactCheck"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        text: base.TextWithEntities,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.text = text

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        self.text.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        text = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.text = text
        return self


class DeleteFactCheck(TLFunction["base.Updates"]):
    """The TL function messages.deleteFactCheck#d1da940c, answered with Updates."""

    __slots__ = ("peer", "msg_id",)

    ID = 0xD1DA940C
    QUALNAME = "functions.messages.DeleteFactCheck"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class GetFactCheck(TLFunction["list[base.FactCheck]"]):
    """The TL function messages.getFactCheck#b9cdc5ee, answered with Vector<FactCheck>."""

    __slots__ = ("peer", "msg_id",)

    ID = 0xB9CDC5EE
    QUALNAME = "functions.messages.GetFactCheck"
    RESULT = "Vector<FactCheck>"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: list[int],
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.msg_id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class RequestMainWebView(TLFunction["base.WebViewResult"]):
    """The TL function messages.requestMainWebView#c9e01e7b, answered with WebViewResult."""

    __slots__ = ("compact", "fullscreen", "peer", "bot", "start_param", "theme_params", "platform",)

    ID = 0xC9E01E7B
    QUALNAME = "functions.messages.RequestMainWebView"
    RESULT = "WebViewResult"

    def __init__(
        self,
        *,
        compact: bool = False,
        fullscreen: bool = False,
        peer: base.InputPeer,
        bot: base.InputUser,
        start_param: str | None = None,
        theme_params: base.DataJSON | None = None,
        platform: str,
    ) -> None:
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.bot = bot
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.compact:
            flags |= 1 << 7
        if self.fullscreen:
            flags |= 1 << 8
        if self.start_param is not None:
            flags |= 1 << 1
        if self.theme_params is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        self.bot.write(w)
        if self.start_param is not None:
            w.write_string(self.start_param)
        if self.theme_params is not None:
            self.theme_params.write(w)
        w.write_string(self.platform)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        compact = bool(flags & (1 << 7))
        fullscreen = bool(flags & (1 << 8))
        peer = r.read_object()
        bot = r.read_object()
        start_param = r.read_string() if flags & (1 << 1) else None
        theme_params = r.read_object() if flags & (1 << 0) else None
        platform = r.read_string()
        self = cls.__new__(cls)
        self.compact = compact
        self.fullscreen = fullscreen
        self.peer = peer
        self.bot = bot
        self.start_param = start_param
        self.theme_params = theme_params
        self.platform = platform
        return self


class SendPaidReaction(TLFunction["base.Updates"]):
    """The TL function messages.sendPaidReaction#58bbcb50, answered with Updates."""

    __slots__ = ("peer", "msg_id", "count", "random_id", "private",)

    ID = 0x58BBCB50
    QUALNAME = "functions.messages.SendPaidReaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        count: int,
        random_id: int,
        private: base.PaidReactionPrivacy | None = None,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.count = count
        self.random_id = random_id
        self.private = private

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.private is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_int(self.count)
        w.write_long(self.random_id)
        if self.private is not None:
            self.private.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        msg_id = r.read_int()
        count = r.read_int()
        random_id = r.read_long()
        private = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.count = count
        self.random_id = random_id
        self.private = private
        return self


class TogglePaidReactionPrivacy(TLFunction["bool"]):
    """The TL function messages.togglePaidReactionPrivacy#435885b5, answered with Bool."""

    __slots__ = ("peer", "msg_id", "private",)

    ID = 0x435885B5
    QUALNAME = "functions.messages.TogglePaidReactionPrivacy"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        private: base.PaidReactionPrivacy,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.private = private

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        self.private.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        private = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.private = private
        return self


class GetPaidReactionPrivacy(TLFunction["base.Updates"]):
    """The TL function messages.getPaidReactionPrivacy#472455aa, answered with Updates."""

    __slots__ = ()

    ID = 0x472455AA
    QUALNAME = "functions.messages.GetPaidReactionPrivacy"
    RESULT = "Updates"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ViewSponsoredMessage(TLFunction["bool"]):
    """The TL function messages.viewSponsoredMessage#269e3643, answered with Bool."""

    __slots__ = ("random_id",)

    ID = 0x269E3643
    QUALNAME = "functions.messages.ViewSponsoredMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        random_id: bytes,
    ) -> None:
        self.random_id = random_id

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.random_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        random_id = r.read_bytes()
        self = cls.__new__(cls)
        self.random_id = random_id
        return self


class ClickSponsoredMessage(TLFunction["bool"]):
    """The TL function messages.clickSponsoredMessage#8235057e, answered with Bool."""

    __slots__ = ("media", "fullscreen", "random_id",)

    ID = 0x8235057E
    QUALNAME = "functions.messages.ClickSponsoredMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        media: bool = False,
        fullscreen: bool = False,
        random_id: bytes,
    ) -> None:
        self.media = media
        self.fullscreen = fullscreen
        self.random_id = random_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.media:
            flags |= 1 << 0
        if self.fullscreen:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_bytes(self.random_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        media = bool(flags & (1 << 0))
        fullscreen = bool(flags & (1 << 1))
        random_id = r.read_bytes()
        self = cls.__new__(cls)
        self.media = media
        self.fullscreen = fullscreen
        self.random_id = random_id
        return self


class ReportSponsoredMessage(TLFunction["base.channels.SponsoredMessageReportResult"]):
    """The TL function messages.reportSponsoredMessage#12cbf0c4, answered with channels.SponsoredMessageReportResult."""

    __slots__ = ("random_id", "option",)

    ID = 0x12CBF0C4
    QUALNAME = "functions.messages.ReportSponsoredMessage"
    RESULT = "channels.SponsoredMessageReportResult"

    def __init__(
        self,
        *,
        random_id: bytes,
        option: bytes,
    ) -> None:
        self.random_id = random_id
        self.option = option

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.random_id)
        w.write_bytes(self.option)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        random_id = r.read_bytes()
        option = r.read_bytes()
        self = cls.__new__(cls)
        self.random_id = random_id
        self.option = option
        return self


class GetSponsoredMessages(TLFunction["base.messages.SponsoredMessages"]):
    """The TL function messages.getSponsoredMessages#3d6ce850, answered with messages.SponsoredMessages."""

    __slots__ = ("peer", "msg_id",)

    ID = 0x3D6CE850
    QUALNAME = "functions.messages.GetSponsoredMessages"
    RESULT = "messages.SponsoredMessages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int | None = None,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.msg_id is not None:
            w.write_int(self.msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        msg_id = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        return self


class SavePreparedInlineMessage(TLFunction["base.messages.BotPreparedInlineMessage"]):
    """The TL function messages.savePreparedInlineMessage#f21f7f2f, answered with messages.BotPreparedInlineMessage."""

    __slots__ = ("result", "user_id", "peer_types",)

    ID = 0xF21F7F2F
    QUALNAME = "functions.messages.SavePreparedInlineMessage"
    RESULT = "messages.BotPreparedInlineMessage"

    def __init__(
        self,
        *,
        result: base.InputBotInlineResult,
        user_id: base.InputUser,
        peer_types: list[base.InlineQueryPeerType] | None = None,
    ) -> None:
        self.result = result
        self.user_id = user_id
        self.peer_types = peer_types

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.peer_types is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.result.write(w)
        self.user_id.write(w)
        if self.peer_types is not None:
            w.write_vector(self.peer_types)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        result = r.read_object()
        user_id = r.read_object()
        peer_types = r.read_vector() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.result = result
        self.user_id = user_id
        self.peer_types = peer_types
        return self


class GetPreparedInlineMessage(TLFunction["base.messages.PreparedInlineMessage"]):
    """The TL function messages.getPreparedInlineMessage#857ebdb8, answered with messages.PreparedInlineMessage."""

    __slots__ = ("bot", "id",)

    ID = 0x857EBDB8
    QUALNAME = "functions.messages.GetPreparedInlineMessage"
    RESULT = "messages.PreparedInlineMessage"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        id: str,
    ) -> None:
        self.bot = bot
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        id = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.id = id
        return self


class SearchStickers(TLFunction["base.messages.FoundStickers"]):
    """The TL function messages.searchStickers#29b1c66a, answered with messages.FoundStickers."""

    __slots__ = ("emojis", "q", "emoticon", "lang_code", "offset", "limit", "hash",)

    ID = 0x29B1C66A
    QUALNAME = "functions.messages.SearchStickers"
    RESULT = "messages.FoundStickers"

    def __init__(
        self,
        *,
        emojis: bool = False,
        q: str,
        emoticon: str,
        lang_code: list[str],
        offset: int,
        limit: int,
        hash: int,
    ) -> None:
        self.emojis = emojis
        self.q = q
        self.emoticon = emoticon
        self.lang_code = lang_code
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.emojis:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.q)
        w.write_string(self.emoticon)
        w.write_vector(self.lang_code, TLWriter.write_string)
        w.write_int(self.offset)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        emojis = bool(flags & (1 << 0))
        q = r.read_string()
        emoticon = r.read_string()
        lang_code = r.read_vector(TLReader.read_string)
        offset = r.read_int()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.emojis = emojis
        self.q = q
        self.emoticon = emoticon
        self.lang_code = lang_code
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class ReportMessagesDelivery(TLFunction["bool"]):
    """The TL function messages.reportMessagesDelivery#5a6d7395, answered with Bool."""

    __slots__ = ("push", "peer", "id",)

    ID = 0x5A6D7395
    QUALNAME = "functions.messages.ReportMessagesDelivery"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        push: bool = False,
        peer: base.InputPeer,
        id: list[int],
    ) -> None:
        self.push = push
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.push:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        push = bool(flags & (1 << 0))
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.push = push
        self.peer = peer
        self.id = id
        return self


class GetSavedDialogsByID(TLFunction["base.messages.SavedDialogs"]):
    """The TL function messages.getSavedDialogsByID#6f6f9c96, answered with messages.SavedDialogs."""

    __slots__ = ("parent_peer", "ids",)

    ID = 0x6F6F9C96
    QUALNAME = "functions.messages.GetSavedDialogsByID"
    RESULT = "messages.SavedDialogs"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer | None = None,
        ids: list[base.InputPeer],
    ) -> None:
        self.parent_peer = parent_peer
        self.ids = ids

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.parent_peer is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        w.write_vector(self.ids)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        parent_peer = r.read_object() if flags & (1 << 1) else None
        ids = r.read_vector()
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        self.ids = ids
        return self


class ReadSavedHistory(TLFunction["bool"]):
    """The TL function messages.readSavedHistory#ba4a3b5b, answered with Bool."""

    __slots__ = ("parent_peer", "peer", "max_id",)

    ID = 0xBA4A3B5B
    QUALNAME = "functions.messages.ReadSavedHistory"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer,
        peer: base.InputPeer,
        max_id: int,
    ) -> None:
        self.parent_peer = parent_peer
        self.peer = peer
        self.max_id = max_id

    def write_body(self, w: TLWriter) -> None:
        self.parent_peer.write(w)
        self.peer.write(w)
        w.write_int(self.max_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        parent_peer = r.read_object()
        peer = r.read_object()
        max_id = r.read_int()
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        self.peer = peer
        self.max_id = max_id
        return self


class ToggleTodoCompleted(TLFunction["base.Updates"]):
    """The TL function messages.toggleTodoCompleted#d3e03124, answered with Updates."""

    __slots__ = ("peer", "msg_id", "completed", "incompleted",)

    ID = 0xD3E03124
    QUALNAME = "functions.messages.ToggleTodoCompleted"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        completed: list[int],
        incompleted: list[int],
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.completed = completed
        self.incompleted = incompleted

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_vector(self.completed, TLWriter.write_int)
        w.write_vector(self.incompleted, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        completed = r.read_vector(TLReader.read_int)
        incompleted = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.completed = completed
        self.incompleted = incompleted
        return self


class AppendTodoList(TLFunction["base.Updates"]):
    """The TL function messages.appendTodoList#21a61057, answered with Updates."""

    __slots__ = ("peer", "msg_id", "list",)

    ID = 0x21A61057
    QUALNAME = "functions.messages.AppendTodoList"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        list: list[base.TodoItem],
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.list = list

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_vector(self.list)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        list = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.list = list
        return self


class ToggleSuggestedPostApproval(TLFunction["base.Updates"]):
    """The TL function messages.toggleSuggestedPostApproval#8107455c, answered with Updates."""

    __slots__ = ("reject", "peer", "msg_id", "schedule_date", "reject_comment",)

    ID = 0x8107455C
    QUALNAME = "functions.messages.ToggleSuggestedPostApproval"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        reject: bool = False,
        peer: base.InputPeer,
        msg_id: int,
        schedule_date: int | None = None,
        reject_comment: str | None = None,
    ) -> None:
        self.reject = reject
        self.peer = peer
        self.msg_id = msg_id
        self.schedule_date = schedule_date
        self.reject_comment = reject_comment

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reject:
            flags |= 1 << 1
        if self.schedule_date is not None:
            flags |= 1 << 0
        if self.reject_comment is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.msg_id)
        if self.schedule_date is not None:
            w.write_int(self.schedule_date)
        if self.reject_comment is not None:
            w.write_string(self.reject_comment)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reject = bool(flags & (1 << 1))
        peer = r.read_object()
        msg_id = r.read_int()
        schedule_date = r.read_int() if flags & (1 << 0) else None
        reject_comment = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.reject = reject
        self.peer = peer
        self.msg_id = msg_id
        self.schedule_date = schedule_date
        self.reject_comment = reject_comment
        return self


class GetForumTopics(TLFunction["base.messages.ForumTopics"]):
    """The TL function messages.getForumTopics#3ba47bff, answered with messages.ForumTopics."""

    __slots__ = ("peer", "q", "offset_date", "offset_id", "offset_topic", "limit",)

    ID = 0x3BA47BFF
    QUALNAME = "functions.messages.GetForumTopics"
    RESULT = "messages.ForumTopics"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        q: str | None = None,
        offset_date: int,
        offset_id: int,
        offset_topic: int,
        limit: int,
    ) -> None:
        self.peer = peer
        self.q = q
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_topic = offset_topic
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.q is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.q is not None:
            w.write_string(self.q)
        w.write_int(self.offset_date)
        w.write_int(self.offset_id)
        w.write_int(self.offset_topic)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        q = r.read_string() if flags & (1 << 0) else None
        offset_date = r.read_int()
        offset_id = r.read_int()
        offset_topic = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.q = q
        self.offset_date = offset_date
        self.offset_id = offset_id
        self.offset_topic = offset_topic
        self.limit = limit
        return self


class GetForumTopicsByID(TLFunction["base.messages.ForumTopics"]):
    """The TL function messages.getForumTopicsByID#af0a4a08, answered with messages.ForumTopics."""

    __slots__ = ("peer", "topics",)

    ID = 0xAF0A4A08
    QUALNAME = "functions.messages.GetForumTopicsByID"
    RESULT = "messages.ForumTopics"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        topics: list[int],
    ) -> None:
        self.peer = peer
        self.topics = topics

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.topics, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        topics = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.topics = topics
        return self


class EditForumTopic(TLFunction["base.Updates"]):
    """The TL function messages.editForumTopic#cecc1134, answered with Updates."""

    __slots__ = ("peer", "topic_id", "title", "icon_emoji_id", "closed", "hidden",)

    ID = 0xCECC1134
    QUALNAME = "functions.messages.EditForumTopic"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        topic_id: int,
        title: str | None = None,
        icon_emoji_id: int | None = None,
        closed: bool | None = None,
        hidden: bool | None = None,
    ) -> None:
        self.peer = peer
        self.topic_id = topic_id
        self.title = title
        self.icon_emoji_id = icon_emoji_id
        self.closed = closed
        self.hidden = hidden

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title is not None:
            flags |= 1 << 0
        if self.icon_emoji_id is not None:
            flags |= 1 << 1
        if self.closed is not None:
            flags |= 1 << 2
        if self.hidden is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.topic_id)
        if self.title is not None:
            w.write_string(self.title)
        if self.icon_emoji_id is not None:
            w.write_long(self.icon_emoji_id)
        if self.closed is not None:
            w.write_bool(self.closed)
        if self.hidden is not None:
            w.write_bool(self.hidden)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        topic_id = r.read_int()
        title = r.read_string() if flags & (1 << 0) else None
        icon_emoji_id = r.read_long() if flags & (1 << 1) else None
        closed = r.read_bool() if flags & (1 << 2) else None
        hidden = r.read_bool() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.topic_id = topic_id
        self.title = title
        self.icon_emoji_id = icon_emoji_id
        self.closed = closed
        self.hidden = hidden
        return self


class UpdatePinnedForumTopic(TLFunction["base.Updates"]):
    """The TL function messages.updatePinnedForumTopic#175df251, answered with Updates."""

    __slots__ = ("peer", "topic_id", "pinned",)

    ID = 0x175DF251
    QUALNAME = "functions.messages.UpdatePinnedForumTopic"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        topic_id: int,
        pinned: bool,
    ) -> None:
        self.peer = peer
        self.topic_id = topic_id
        self.pinned = pinned

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.topic_id)
        w.write_bool(self.pinned)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        topic_id = r.read_int()
        pinned = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.topic_id = topic_id
        self.pinned = pinned
        return self


class ReorderPinnedForumTopics(TLFunction["base.Updates"]):
    """The TL function messages.reorderPinnedForumTopics#0e7841f0, answered with Updates."""

    __slots__ = ("force", "peer", "order",)

    ID = 0x0E7841F0
    QUALNAME = "functions.messages.ReorderPinnedForumTopics"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        force: bool = False,
        peer: base.InputPeer,
        order: list[int],
    ) -> None:
        self.force = force
        self.peer = peer
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.force:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        force = bool(flags & (1 << 0))
        peer = r.read_object()
        order = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.force = force
        self.peer = peer
        self.order = order
        return self


class CreateForumTopic(TLFunction["base.Updates"]):
    """The TL function messages.createForumTopic#2f98c3d5, answered with Updates."""

    __slots__ = ("title_missing", "peer", "title", "icon_color", "icon_emoji_id", "random_id", "send_as",)

    ID = 0x2F98C3D5
    QUALNAME = "functions.messages.CreateForumTopic"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        title_missing: bool = False,
        peer: base.InputPeer,
        title: str,
        icon_color: int | None = None,
        icon_emoji_id: int | None = None,
        random_id: int,
        send_as: base.InputPeer | None = None,
    ) -> None:
        self.title_missing = title_missing
        self.peer = peer
        self.title = title
        self.icon_color = icon_color
        self.icon_emoji_id = icon_emoji_id
        self.random_id = random_id
        self.send_as = send_as

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title_missing:
            flags |= 1 << 4
        if self.icon_color is not None:
            flags |= 1 << 0
        if self.icon_emoji_id is not None:
            flags |= 1 << 3
        if self.send_as is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.title)
        if self.icon_color is not None:
            w.write_int(self.icon_color)
        if self.icon_emoji_id is not None:
            w.write_long(self.icon_emoji_id)
        w.write_long(self.random_id)
        if self.send_as is not None:
            self.send_as.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        title_missing = bool(flags & (1 << 4))
        peer = r.read_object()
        title = r.read_string()
        icon_color = r.read_int() if flags & (1 << 0) else None
        icon_emoji_id = r.read_long() if flags & (1 << 3) else None
        random_id = r.read_long()
        send_as = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.title_missing = title_missing
        self.peer = peer
        self.title = title
        self.icon_color = icon_color
        self.icon_emoji_id = icon_emoji_id
        self.random_id = random_id
        self.send_as = send_as
        return self


class DeleteTopicHistory(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.deleteTopicHistory#d2816f10, answered with messages.AffectedHistory."""

    __slots__ = ("peer", "top_msg_id",)

    ID = 0xD2816F10
    QUALNAME = "functions.messages.DeleteTopicHistory"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.top_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        top_msg_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        return self


class GetEmojiGameInfo(TLFunction["base.messages.EmojiGameInfo"]):
    """The TL function messages.getEmojiGameInfo#fb7e8ca7, answered with messages.EmojiGameInfo."""

    __slots__ = ()

    ID = 0xFB7E8CA7
    QUALNAME = "functions.messages.GetEmojiGameInfo"
    RESULT = "messages.EmojiGameInfo"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SummarizeText(TLFunction["base.TextWithEntities"]):
    """The TL function messages.summarizeText#abbbd346, answered with TextWithEntities."""

    __slots__ = ("peer", "id", "to_lang", "tone",)

    ID = 0xABBBD346
    QUALNAME = "functions.messages.SummarizeText"
    RESULT = "TextWithEntities"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        to_lang: str | None = None,
        tone: str | None = None,
    ) -> None:
        self.peer = peer
        self.id = id
        self.to_lang = to_lang
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.to_lang is not None:
            flags |= 1 << 0
        if self.tone is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.to_lang is not None:
            w.write_string(self.to_lang)
        if self.tone is not None:
            w.write_string(self.tone)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        id = r.read_int()
        to_lang = r.read_string() if flags & (1 << 0) else None
        tone = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.to_lang = to_lang
        self.tone = tone
        return self


class EditChatCreator(TLFunction["base.Updates"]):
    """The TL function messages.editChatCreator#f743b857, answered with Updates."""

    __slots__ = ("peer", "user_id", "password",)

    ID = 0xF743B857
    QUALNAME = "functions.messages.EditChatCreator"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        user_id: base.InputUser,
        password: base.InputCheckPasswordSRP,
    ) -> None:
        self.peer = peer
        self.user_id = user_id
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.user_id.write(w)
        self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        user_id = r.read_object()
        password = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.user_id = user_id
        self.password = password
        return self


class GetFutureChatCreatorAfterLeave(TLFunction["base.User"]):
    """The TL function messages.getFutureChatCreatorAfterLeave#3b7d0ea6, answered with User."""

    __slots__ = ("peer",)

    ID = 0x3B7D0EA6
    QUALNAME = "functions.messages.GetFutureChatCreatorAfterLeave"
    RESULT = "User"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class EditChatParticipantRank(TLFunction["base.Updates"]):
    """The TL function messages.editChatParticipantRank#a00f32b0, answered with Updates."""

    __slots__ = ("peer", "participant", "rank",)

    ID = 0xA00F32B0
    QUALNAME = "functions.messages.EditChatParticipantRank"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        participant: base.InputPeer,
        rank: str,
    ) -> None:
        self.peer = peer
        self.participant = participant
        self.rank = rank

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.participant.write(w)
        w.write_string(self.rank)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        participant = r.read_object()
        rank = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.participant = participant
        self.rank = rank
        return self


class DeclineUrlAuth(TLFunction["bool"]):
    """The TL function messages.declineUrlAuth#35436bbc, answered with Bool."""

    __slots__ = ("url",)

    ID = 0x35436BBC
    QUALNAME = "functions.messages.DeclineUrlAuth"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        url: str,
    ) -> None:
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        return self


class CheckUrlAuthMatchCode(TLFunction["bool"]):
    """The TL function messages.checkUrlAuthMatchCode#c9a47b0b, answered with Bool."""

    __slots__ = ("url", "match_code",)

    ID = 0xC9A47B0B
    QUALNAME = "functions.messages.CheckUrlAuthMatchCode"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        url: str,
        match_code: str,
    ) -> None:
        self.url = url
        self.match_code = match_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)
        w.write_string(self.match_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        match_code = r.read_string()
        self = cls.__new__(cls)
        self.url = url
        self.match_code = match_code
        return self


class ComposeMessageWithAI(TLFunction["base.messages.ComposedMessageWithAI"]):
    """The TL function messages.composeMessageWithAI#daecc589, answered with messages.ComposedMessageWithAI."""

    __slots__ = ("proofread", "emojify", "text", "translate_to_lang", "tone",)

    ID = 0xDAECC589
    QUALNAME = "functions.messages.ComposeMessageWithAI"
    RESULT = "messages.ComposedMessageWithAI"

    def __init__(
        self,
        *,
        proofread: bool = False,
        emojify: bool = False,
        text: base.TextWithEntities,
        translate_to_lang: str | None = None,
        tone: base.InputAiComposeTone | None = None,
    ) -> None:
        self.proofread = proofread
        self.emojify = emojify
        self.text = text
        self.translate_to_lang = translate_to_lang
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.proofread:
            flags |= 1 << 0
        if self.emojify:
            flags |= 1 << 3
        if self.translate_to_lang is not None:
            flags |= 1 << 1
        if self.tone is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.text.write(w)
        if self.translate_to_lang is not None:
            w.write_string(self.translate_to_lang)
        if self.tone is not None:
            self.tone.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        proofread = bool(flags & (1 << 0))
        emojify = bool(flags & (1 << 3))
        text = r.read_object()
        translate_to_lang = r.read_string() if flags & (1 << 1) else None
        tone = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.proofread = proofread
        self.emojify = emojify
        self.text = text
        self.translate_to_lang = translate_to_lang
        self.tone = tone
        return self


class ReportReadMetrics(TLFunction["bool"]):
    """The TL function messages.reportReadMetrics#4067c5e6, answered with Bool."""

    __slots__ = ("peer", "metrics",)

    ID = 0x4067C5E6
    QUALNAME = "functions.messages.ReportReadMetrics"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        metrics: list[base.InputMessageReadMetric],
    ) -> None:
        self.peer = peer
        self.metrics = metrics

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.metrics)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        metrics = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.metrics = metrics
        return self


class ReportMusicListen(TLFunction["bool"]):
    """The TL function messages.reportMusicListen#ddbcd819, answered with Bool."""

    __slots__ = ("id", "listened_duration",)

    ID = 0xDDBCD819
    QUALNAME = "functions.messages.ReportMusicListen"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.InputDocument,
        listened_duration: int,
    ) -> None:
        self.id = id
        self.listened_duration = listened_duration

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_int(self.listened_duration)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        listened_duration = r.read_int()
        self = cls.__new__(cls)
        self.id = id
        self.listened_duration = listened_duration
        return self


class AddPollAnswer(TLFunction["base.Updates"]):
    """The TL function messages.addPollAnswer#19bc4b6d, answered with Updates."""

    __slots__ = ("peer", "msg_id", "answer",)

    ID = 0x19BC4B6D
    QUALNAME = "functions.messages.AddPollAnswer"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        answer: base.PollAnswer,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.answer = answer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        self.answer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        answer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.answer = answer
        return self


class DeletePollAnswer(TLFunction["base.Updates"]):
    """The TL function messages.deletePollAnswer#ac8505a5, answered with Updates."""

    __slots__ = ("peer", "msg_id", "option",)

    ID = 0xAC8505A5
    QUALNAME = "functions.messages.DeletePollAnswer"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        option: bytes,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.option = option

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        w.write_bytes(self.option)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        option = r.read_bytes()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.option = option
        return self


class GetUnreadPollVotes(TLFunction["base.messages.Messages"]):
    """The TL function messages.getUnreadPollVotes#43286cf2, answered with messages.Messages."""

    __slots__ = ("peer", "top_msg_id", "offset_id", "add_offset", "limit", "max_id", "min_id",)

    ID = 0x43286CF2
    QUALNAME = "functions.messages.GetUnreadPollVotes"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
        offset_id: int,
        add_offset: int,
        limit: int,
        max_id: int,
        min_id: int,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)
        w.write_int(self.offset_id)
        w.write_int(self.add_offset)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        offset_id = r.read_int()
        add_offset = r.read_int()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        self.offset_id = offset_id
        self.add_offset = add_offset
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        return self


class ReadPollVotes(TLFunction["base.messages.AffectedHistory"]):
    """The TL function messages.readPollVotes#1720b4d8, answered with messages.AffectedHistory."""

    __slots__ = ("peer", "top_msg_id",)

    ID = 0x1720B4D8
    QUALNAME = "functions.messages.ReadPollVotes"
    RESULT = "messages.AffectedHistory"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        top_msg_id: int | None = None,
    ) -> None:
        self.peer = peer
        self.top_msg_id = top_msg_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.top_msg_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        if self.top_msg_id is not None:
            w.write_int(self.top_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        top_msg_id = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.top_msg_id = top_msg_id
        return self


class SetBotGuestChatResult(TLFunction["base.InputBotInlineMessageID"]):
    """The TL function messages.setBotGuestChatResult#b8f106e3, answered with InputBotInlineMessageID."""

    __slots__ = ("query_id", "result",)

    ID = 0xB8F106E3
    QUALNAME = "functions.messages.SetBotGuestChatResult"
    RESULT = "InputBotInlineMessageID"

    def __init__(
        self,
        *,
        query_id: int,
        result: base.InputBotInlineResult,
    ) -> None:
        self.query_id = query_id
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.query_id)
        self.result.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        query_id = r.read_long()
        result = r.read_object()
        self = cls.__new__(cls)
        self.query_id = query_id
        self.result = result
        return self


class DeleteParticipantReactions(TLFunction["bool"]):
    """The TL function messages.deleteParticipantReactions#a0b80cf8, answered with Bool."""

    __slots__ = ("peer", "participant",)

    ID = 0xA0B80CF8
    QUALNAME = "functions.messages.DeleteParticipantReactions"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        participant: base.InputPeer,
    ) -> None:
        self.peer = peer
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.participant = participant
        return self


class DeleteParticipantReaction(TLFunction["base.Updates"]):
    """The TL function messages.deleteParticipantReaction#e3b7f82c, answered with Updates."""

    __slots__ = ("peer", "msg_id", "participant",)

    ID = 0xE3B7F82C
    QUALNAME = "functions.messages.DeleteParticipantReaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        msg_id: int,
        participant: base.InputPeer,
    ) -> None:
        self.peer = peer
        self.msg_id = msg_id
        self.participant = participant

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.msg_id)
        self.participant.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        msg_id = r.read_int()
        participant = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.msg_id = msg_id
        self.participant = participant
        return self


class GetPersonalChannelHistory(TLFunction["base.messages.Messages"]):
    """The TL function messages.getPersonalChannelHistory#55fb0996, answered with messages.Messages."""

    __slots__ = ("user_id", "limit", "max_id", "min_id", "hash",)

    ID = 0x55FB0996
    QUALNAME = "functions.messages.GetPersonalChannelHistory"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        limit: int,
        max_id: int,
        min_id: int,
        hash: int,
    ) -> None:
        self.user_id = user_id
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_int(self.limit)
        w.write_int(self.max_id)
        w.write_int(self.min_id)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        limit = r.read_int()
        max_id = r.read_int()
        min_id = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.limit = limit
        self.max_id = max_id
        self.min_id = min_id
        self.hash = hash
        return self


class GetRichMessage(TLFunction["base.messages.Messages"]):
    """The TL function messages.getRichMessage#501569cf, answered with messages.Messages."""

    __slots__ = ("peer", "id",)

    ID = 0x501569CF
    QUALNAME = "functions.messages.GetRichMessage"
    RESULT = "messages.Messages"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
    ) -> None:
        self.peer = peer
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        return self


class TranslateRichMessage(TLFunction["base.messages.TranslatedRichMessage"]):
    """The TL function messages.translateRichMessage#1a542004, answered with messages.TranslatedRichMessage."""

    __slots__ = ("peer", "id", "text", "to_lang", "tone",)

    ID = 0x1A542004
    QUALNAME = "functions.messages.TranslateRichMessage"
    RESULT = "messages.TranslatedRichMessage"

    def __init__(
        self,
        *,
        peer: base.InputPeer | None = None,
        id: list[int] | None = None,
        text: list[base.InputRichMessage] | None = None,
        to_lang: str,
        tone: str | None = None,
    ) -> None:
        self.peer = peer
        self.id = id
        self.text = text
        self.to_lang = to_lang
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.peer is not None:
            flags |= 1 << 0
        if self.id is not None:
            flags |= 1 << 0
        if self.text is not None:
            flags |= 1 << 1
        if self.tone is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        if self.id is not None:
            w.write_vector(self.id, TLWriter.write_int)
        if self.text is not None:
            w.write_vector(self.text)
        w.write_string(self.to_lang)
        if self.tone is not None:
            w.write_string(self.tone)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object() if flags & (1 << 0) else None
        id = r.read_vector(TLReader.read_int) if flags & (1 << 0) else None
        text = r.read_vector() if flags & (1 << 1) else None
        to_lang = r.read_string()
        tone = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.text = text
        self.to_lang = to_lang
        self.tone = tone
        return self


class ComposeRichMessageWithAI(TLFunction["base.messages.ComposedRichMessageWithAI"]):
    """The TL function messages.composeRichMessageWithAI#8d7ae6af, answered with messages.ComposedRichMessageWithAI."""

    __slots__ = ("proofread", "emojify", "text", "translate_to_lang", "tone",)

    ID = 0x8D7AE6AF
    QUALNAME = "functions.messages.ComposeRichMessageWithAI"
    RESULT = "messages.ComposedRichMessageWithAI"

    def __init__(
        self,
        *,
        proofread: bool = False,
        emojify: bool = False,
        text: base.InputRichMessage | None = None,
        translate_to_lang: str | None = None,
        tone: base.InputAiComposeTone | None = None,
    ) -> None:
        self.proofread = proofread
        self.emojify = emojify
        self.text = text
        self.translate_to_lang = translate_to_lang
        self.tone = tone

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.proofread:
            flags |= 1 << 0
        if self.emojify:
            flags |= 1 << 3
        if self.text is not None:
            flags |= 1 << 4
        if self.translate_to_lang is not None:
            flags |= 1 << 1
        if self.tone is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.text is not None:
            self.text.write(w)
        if self.translate_to_lang is not None:
            w.write_string(self.translate_to_lang)
        if self.tone is not None:
            self.tone.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        proofread = bool(flags & (1 << 0))
        emojify = bool(flags & (1 << 3))
        text = r.read_object() if flags & (1 << 4) else None
        translate_to_lang = r.read_string() if flags & (1 << 1) else None
        tone = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.proofread = proofread
        self.emojify = emojify
        self.text = text
        self.translate_to_lang = translate_to_lang
        self.tone = tone
        return self


class RequestChatJoinWebView(TLFunction["base.WebViewResult"]):
    """The TL function messages.requestChatJoinWebView#ba9ee679, answered with WebViewResult."""

    __slots__ = ("query_id", "theme_params", "platform",)

    ID = 0xBA9EE679
    QUALNAME = "functions.messages.RequestChatJoinWebView"
    RESULT = "WebViewResult"

    def __init__(
        self,
        *,
        query_id: int,
        theme_params: base.DataJSON | None = None,
        platform: str,
    ) -> None:
        self.query_id = query_id
        self.theme_params = theme_params
        self.platform = platform

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.theme_params is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.query_id)
        if self.theme_params is not None:
            self.theme_params.write(w)
        w.write_string(self.platform)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        query_id = r.read_long()
        theme_params = r.read_object() if flags & (1 << 0) else None
        platform = r.read_string()
        self = cls.__new__(cls)
        self.query_id = query_id
        self.theme_params = theme_params
        self.platform = platform
        return self
