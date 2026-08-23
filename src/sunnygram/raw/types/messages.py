# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the messages namespace.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class Dialogs(TLObject):
    """The TL type messages.dialogs#15ba6c40, a form of messages.Dialogs."""

    __slots__ = ("dialogs", "messages", "chats", "users",)

    ID = 0x15BA6C40
    QUALNAME = "types.messages.Dialogs"

    def __init__(
        self,
        *,
        dialogs: list[base.Dialog],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.dialogs)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dialogs = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class DialogsSlice(TLObject):
    """The TL type messages.dialogsSlice#71e094f3, a form of messages.Dialogs."""

    __slots__ = ("count", "dialogs", "messages", "chats", "users",)

    ID = 0x71E094F3
    QUALNAME = "types.messages.DialogsSlice"

    def __init__(
        self,
        *,
        count: int,
        dialogs: list[base.Dialog],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.dialogs)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        dialogs = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class DialogsNotModified(TLObject):
    """The TL type messages.dialogsNotModified#f0e3e596, a form of messages.Dialogs."""

    __slots__ = ("count",)

    ID = 0xF0E3E596
    QUALNAME = "types.messages.DialogsNotModified"

    def __init__(
        self,
        *,
        count: int,
    ) -> None:
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        return self


class Messages(TLObject):
    """The TL type messages.messages#1d73e7ea, a form of messages.Messages."""

    __slots__ = ("messages", "topics", "chats", "users",)

    ID = 0x1D73E7EA
    QUALNAME = "types.messages.Messages"

    def __init__(
        self,
        *,
        messages: list[base.Message],
        topics: list[base.ForumTopic],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.messages)
        w.write_vector(self.topics)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        messages = r.read_vector()
        topics = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users
        return self


class MessagesSlice(TLObject):
    """The TL type messages.messagesSlice#5f206716, a form of messages.Messages."""

    __slots__ = ("inexact", "count", "next_rate", "offset_id_offset", "search_flood", "messages", "topics", "chats", "users",)

    ID = 0x5F206716
    QUALNAME = "types.messages.MessagesSlice"

    def __init__(
        self,
        *,
        inexact: bool = False,
        count: int,
        next_rate: int | None = None,
        offset_id_offset: int | None = None,
        search_flood: base.SearchPostsFlood | None = None,
        messages: list[base.Message],
        topics: list[base.ForumTopic],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.inexact = inexact
        self.count = count
        self.next_rate = next_rate
        self.offset_id_offset = offset_id_offset
        self.search_flood = search_flood
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inexact:
            flags |= 1 << 1
        if self.next_rate is not None:
            flags |= 1 << 0
        if self.offset_id_offset is not None:
            flags |= 1 << 2
        if self.search_flood is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_int(self.count)
        if self.next_rate is not None:
            w.write_int(self.next_rate)
        if self.offset_id_offset is not None:
            w.write_int(self.offset_id_offset)
        if self.search_flood is not None:
            self.search_flood.write(w)
        w.write_vector(self.messages)
        w.write_vector(self.topics)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inexact = bool(flags & (1 << 1))
        count = r.read_int()
        next_rate = r.read_int() if flags & (1 << 0) else None
        offset_id_offset = r.read_int() if flags & (1 << 2) else None
        search_flood = r.read_object() if flags & (1 << 3) else None
        messages = r.read_vector()
        topics = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.inexact = inexact
        self.count = count
        self.next_rate = next_rate
        self.offset_id_offset = offset_id_offset
        self.search_flood = search_flood
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users
        return self


class ChannelMessages(TLObject):
    """The TL type messages.channelMessages#c776ba4e, a form of messages.Messages."""

    __slots__ = ("inexact", "pts", "count", "offset_id_offset", "messages", "topics", "chats", "users",)

    ID = 0xC776BA4E
    QUALNAME = "types.messages.ChannelMessages"

    def __init__(
        self,
        *,
        inexact: bool = False,
        pts: int,
        count: int,
        offset_id_offset: int | None = None,
        messages: list[base.Message],
        topics: list[base.ForumTopic],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.inexact = inexact
        self.pts = pts
        self.count = count
        self.offset_id_offset = offset_id_offset
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inexact:
            flags |= 1 << 1
        if self.offset_id_offset is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_int(self.pts)
        w.write_int(self.count)
        if self.offset_id_offset is not None:
            w.write_int(self.offset_id_offset)
        w.write_vector(self.messages)
        w.write_vector(self.topics)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inexact = bool(flags & (1 << 1))
        pts = r.read_int()
        count = r.read_int()
        offset_id_offset = r.read_int() if flags & (1 << 2) else None
        messages = r.read_vector()
        topics = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.inexact = inexact
        self.pts = pts
        self.count = count
        self.offset_id_offset = offset_id_offset
        self.messages = messages
        self.topics = topics
        self.chats = chats
        self.users = users
        return self


class MessagesNotModified(TLObject):
    """The TL type messages.messagesNotModified#74535f21, a form of messages.Messages."""

    __slots__ = ("count",)

    ID = 0x74535F21
    QUALNAME = "types.messages.MessagesNotModified"

    def __init__(
        self,
        *,
        count: int,
    ) -> None:
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        return self


class Chats(TLObject):
    """The TL type messages.chats#64ff9fd5, a form of messages.Chats."""

    __slots__ = ("chats",)

    ID = 0x64FF9FD5
    QUALNAME = "types.messages.Chats"

    def __init__(
        self,
        *,
        chats: list[base.Chat],
    ) -> None:
        self.chats = chats

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.chats)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        chats = r.read_vector()
        self = cls.__new__(cls)
        self.chats = chats
        return self


class ChatsSlice(TLObject):
    """The TL type messages.chatsSlice#9cd81144, a form of messages.Chats."""

    __slots__ = ("count", "chats",)

    ID = 0x9CD81144
    QUALNAME = "types.messages.ChatsSlice"

    def __init__(
        self,
        *,
        count: int,
        chats: list[base.Chat],
    ) -> None:
        self.count = count
        self.chats = chats

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.chats)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        chats = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.chats = chats
        return self


class ChatFull(TLObject):
    """The TL type messages.chatFull#e5d7d19c, a form of messages.ChatFull."""

    __slots__ = ("full_chat", "chats", "users",)

    ID = 0xE5D7D19C
    QUALNAME = "types.messages.ChatFull"

    def __init__(
        self,
        *,
        full_chat: base.ChatFull,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.full_chat = full_chat
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.full_chat.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        full_chat = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.full_chat = full_chat
        self.chats = chats
        self.users = users
        return self


_PACK_AffectedHistory = struct.Struct("<iii")


class AffectedHistory(TLObject):
    """The TL type messages.affectedHistory#b45c69d1, a form of messages.AffectedHistory."""

    __slots__ = ("pts", "pts_count", "offset",)

    ID = 0xB45C69D1
    QUALNAME = "types.messages.AffectedHistory"

    def __init__(
        self,
        *,
        pts: int,
        pts_count: int,
        offset: int,
    ) -> None:
        self.pts = pts
        self.pts_count = pts_count
        self.offset = offset

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_AffectedHistory.pack(self.pts, self.pts_count, self.offset))
        except struct.error:
            w.write_int(self.pts)
            w.write_int(self.pts_count)
            w.write_int(self.offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pts = r.read_int()
        pts_count = r.read_int()
        offset = r.read_int()
        self = cls.__new__(cls)
        self.pts = pts
        self.pts_count = pts_count
        self.offset = offset
        return self


class DhConfigNotModified(TLObject):
    """The TL type messages.dhConfigNotModified#c0e24635, a form of messages.DhConfig."""

    __slots__ = ("random",)

    ID = 0xC0E24635
    QUALNAME = "types.messages.DhConfigNotModified"

    def __init__(
        self,
        *,
        random: bytes,
    ) -> None:
        self.random = random

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.random)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        random = r.read_bytes()
        self = cls.__new__(cls)
        self.random = random
        return self


class DhConfig(TLObject):
    """The TL type messages.dhConfig#2c221edd, a form of messages.DhConfig."""

    __slots__ = ("g", "p", "version", "random",)

    ID = 0x2C221EDD
    QUALNAME = "types.messages.DhConfig"

    def __init__(
        self,
        *,
        g: int,
        p: bytes,
        version: int,
        random: bytes,
    ) -> None:
        self.g = g
        self.p = p
        self.version = version
        self.random = random

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.g)
        w.write_bytes(self.p)
        w.write_int(self.version)
        w.write_bytes(self.random)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        g = r.read_int()
        p = r.read_bytes()
        version = r.read_int()
        random = r.read_bytes()
        self = cls.__new__(cls)
        self.g = g
        self.p = p
        self.version = version
        self.random = random
        return self


class SentEncryptedMessage(TLObject):
    """The TL type messages.sentEncryptedMessage#560f8935, a form of messages.SentEncryptedMessage."""

    __slots__ = ("date",)

    ID = 0x560F8935
    QUALNAME = "types.messages.SentEncryptedMessage"

    def __init__(
        self,
        *,
        date: int,
    ) -> None:
        self.date = date

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        date = r.read_int()
        self = cls.__new__(cls)
        self.date = date
        return self


class SentEncryptedFile(TLObject):
    """The TL type messages.sentEncryptedFile#9493ff32, a form of messages.SentEncryptedMessage."""

    __slots__ = ("date", "file",)

    ID = 0x9493FF32
    QUALNAME = "types.messages.SentEncryptedFile"

    def __init__(
        self,
        *,
        date: int,
        file: base.EncryptedFile,
    ) -> None:
        self.date = date
        self.file = file

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.date)
        self.file.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        date = r.read_int()
        file = r.read_object()
        self = cls.__new__(cls)
        self.date = date
        self.file = file
        return self


class StickersNotModified(TLObject):
    """The TL type messages.stickersNotModified#f1749a22, a form of messages.Stickers."""

    __slots__ = ()

    ID = 0xF1749A22
    QUALNAME = "types.messages.StickersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Stickers(TLObject):
    """The TL type messages.stickers#30a6ec7e, a form of messages.Stickers."""

    __slots__ = ("hash", "stickers",)

    ID = 0x30A6EC7E
    QUALNAME = "types.messages.Stickers"

    def __init__(
        self,
        *,
        hash: int,
        stickers: list[base.Document],
    ) -> None:
        self.hash = hash
        self.stickers = stickers

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.stickers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        stickers = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.stickers = stickers
        return self


class AllStickersNotModified(TLObject):
    """The TL type messages.allStickersNotModified#e86602c3, a form of messages.AllStickers."""

    __slots__ = ()

    ID = 0xE86602C3
    QUALNAME = "types.messages.AllStickersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class AllStickers(TLObject):
    """The TL type messages.allStickers#cdbbcebb, a form of messages.AllStickers."""

    __slots__ = ("hash", "sets",)

    ID = 0xCDBBCEBB
    QUALNAME = "types.messages.AllStickers"

    def __init__(
        self,
        *,
        hash: int,
        sets: list[base.StickerSet],
    ) -> None:
        self.hash = hash
        self.sets = sets

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.sets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        sets = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.sets = sets
        return self


_PACK_AffectedMessages = struct.Struct("<ii")


class AffectedMessages(TLObject):
    """The TL type messages.affectedMessages#84d19185, a form of messages.AffectedMessages."""

    __slots__ = ("pts", "pts_count",)

    ID = 0x84D19185
    QUALNAME = "types.messages.AffectedMessages"

    def __init__(
        self,
        *,
        pts: int,
        pts_count: int,
    ) -> None:
        self.pts = pts
        self.pts_count = pts_count

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_AffectedMessages.pack(self.pts, self.pts_count))
        except struct.error:
            w.write_int(self.pts)
            w.write_int(self.pts_count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pts = r.read_int()
        pts_count = r.read_int()
        self = cls.__new__(cls)
        self.pts = pts
        self.pts_count = pts_count
        return self


class StickerSet(TLObject):
    """The TL type messages.stickerSet#6e153f16, a form of messages.StickerSet."""

    __slots__ = ("set", "packs", "keywords", "documents",)

    ID = 0x6E153F16
    QUALNAME = "types.messages.StickerSet"

    def __init__(
        self,
        *,
        set: base.StickerSet,
        packs: list[base.StickerPack],
        keywords: list[base.StickerKeyword],
        documents: list[base.Document],
    ) -> None:
        self.set = set
        self.packs = packs
        self.keywords = keywords
        self.documents = documents

    def write_body(self, w: TLWriter) -> None:
        self.set.write(w)
        w.write_vector(self.packs)
        w.write_vector(self.keywords)
        w.write_vector(self.documents)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        set = r.read_object()
        packs = r.read_vector()
        keywords = r.read_vector()
        documents = r.read_vector()
        self = cls.__new__(cls)
        self.set = set
        self.packs = packs
        self.keywords = keywords
        self.documents = documents
        return self


class StickerSetNotModified(TLObject):
    """The TL type messages.stickerSetNotModified#d3f924eb, a form of messages.StickerSet."""

    __slots__ = ()

    ID = 0xD3F924EB
    QUALNAME = "types.messages.StickerSetNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedGifsNotModified(TLObject):
    """The TL type messages.savedGifsNotModified#e8025ca2, a form of messages.SavedGifs."""

    __slots__ = ()

    ID = 0xE8025CA2
    QUALNAME = "types.messages.SavedGifsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedGifs(TLObject):
    """The TL type messages.savedGifs#84a02a0d, a form of messages.SavedGifs."""

    __slots__ = ("hash", "gifs",)

    ID = 0x84A02A0D
    QUALNAME = "types.messages.SavedGifs"

    def __init__(
        self,
        *,
        hash: int,
        gifs: list[base.Document],
    ) -> None:
        self.hash = hash
        self.gifs = gifs

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.gifs)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        gifs = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.gifs = gifs
        return self


class BotResults(TLObject):
    """The TL type messages.botResults#e021f2f6, a form of messages.BotResults."""

    __slots__ = ("gallery", "query_id", "next_offset", "switch_pm", "switch_webview", "results", "cache_time", "users",)

    ID = 0xE021F2F6
    QUALNAME = "types.messages.BotResults"

    def __init__(
        self,
        *,
        gallery: bool = False,
        query_id: int,
        next_offset: str | None = None,
        switch_pm: base.InlineBotSwitchPM | None = None,
        switch_webview: base.InlineBotWebView | None = None,
        results: list[base.BotInlineResult],
        cache_time: int,
        users: list[base.User],
    ) -> None:
        self.gallery = gallery
        self.query_id = query_id
        self.next_offset = next_offset
        self.switch_pm = switch_pm
        self.switch_webview = switch_webview
        self.results = results
        self.cache_time = cache_time
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.gallery:
            flags |= 1 << 0
        if self.next_offset is not None:
            flags |= 1 << 1
        if self.switch_pm is not None:
            flags |= 1 << 2
        if self.switch_webview is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_long(self.query_id)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        if self.switch_pm is not None:
            self.switch_pm.write(w)
        if self.switch_webview is not None:
            self.switch_webview.write(w)
        w.write_vector(self.results)
        w.write_int(self.cache_time)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        gallery = bool(flags & (1 << 0))
        query_id = r.read_long()
        next_offset = r.read_string() if flags & (1 << 1) else None
        switch_pm = r.read_object() if flags & (1 << 2) else None
        switch_webview = r.read_object() if flags & (1 << 3) else None
        results = r.read_vector()
        cache_time = r.read_int()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.gallery = gallery
        self.query_id = query_id
        self.next_offset = next_offset
        self.switch_pm = switch_pm
        self.switch_webview = switch_webview
        self.results = results
        self.cache_time = cache_time
        self.users = users
        return self


class BotCallbackAnswer(TLObject):
    """The TL type messages.botCallbackAnswer#36585ea4, a form of messages.BotCallbackAnswer."""

    __slots__ = ("alert", "has_url", "native_ui", "message", "url", "cache_time",)

    ID = 0x36585EA4
    QUALNAME = "types.messages.BotCallbackAnswer"

    def __init__(
        self,
        *,
        alert: bool = False,
        has_url: bool = False,
        native_ui: bool = False,
        message: str | None = None,
        url: str | None = None,
        cache_time: int,
    ) -> None:
        self.alert = alert
        self.has_url = has_url
        self.native_ui = native_ui
        self.message = message
        self.url = url
        self.cache_time = cache_time

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.alert:
            flags |= 1 << 1
        if self.has_url:
            flags |= 1 << 3
        if self.native_ui:
            flags |= 1 << 4
        if self.message is not None:
            flags |= 1 << 0
        if self.url is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.message is not None:
            w.write_string(self.message)
        if self.url is not None:
            w.write_string(self.url)
        w.write_int(self.cache_time)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        alert = bool(flags & (1 << 1))
        has_url = bool(flags & (1 << 3))
        native_ui = bool(flags & (1 << 4))
        message = r.read_string() if flags & (1 << 0) else None
        url = r.read_string() if flags & (1 << 2) else None
        cache_time = r.read_int()
        self = cls.__new__(cls)
        self.alert = alert
        self.has_url = has_url
        self.native_ui = native_ui
        self.message = message
        self.url = url
        self.cache_time = cache_time
        return self


class MessageEditData(TLObject):
    """The TL type messages.messageEditData#26b5dde6, a form of messages.MessageEditData."""

    __slots__ = ("caption",)

    ID = 0x26B5DDE6
    QUALNAME = "types.messages.MessageEditData"

    def __init__(
        self,
        *,
        caption: bool = False,
    ) -> None:
        self.caption = caption

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.caption:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        caption = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.caption = caption
        return self


class PeerDialogs(TLObject):
    """The TL type messages.peerDialogs#3371c354, a form of messages.PeerDialogs."""

    __slots__ = ("dialogs", "messages", "chats", "users", "state",)

    ID = 0x3371C354
    QUALNAME = "types.messages.PeerDialogs"

    def __init__(
        self,
        *,
        dialogs: list[base.Dialog],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
        state: base.updates.State,
    ) -> None:
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        self.state = state

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.dialogs)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        self.state.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dialogs = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        state = r.read_object()
        self = cls.__new__(cls)
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        self.state = state
        return self


class FeaturedStickersNotModified(TLObject):
    """The TL type messages.featuredStickersNotModified#c6dc0c66, a form of messages.FeaturedStickers."""

    __slots__ = ("count",)

    ID = 0xC6DC0C66
    QUALNAME = "types.messages.FeaturedStickersNotModified"

    def __init__(
        self,
        *,
        count: int,
    ) -> None:
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        return self


class FeaturedStickers(TLObject):
    """The TL type messages.featuredStickers#be382906, a form of messages.FeaturedStickers."""

    __slots__ = ("premium", "hash", "count", "sets", "unread",)

    ID = 0xBE382906
    QUALNAME = "types.messages.FeaturedStickers"

    def __init__(
        self,
        *,
        premium: bool = False,
        hash: int,
        count: int,
        sets: list[base.StickerSetCovered],
        unread: list[int],
    ) -> None:
        self.premium = premium
        self.hash = hash
        self.count = count
        self.sets = sets
        self.unread = unread

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.premium:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.hash)
        w.write_int(self.count)
        w.write_vector(self.sets)
        w.write_vector(self.unread, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        premium = bool(flags & (1 << 0))
        hash = r.read_long()
        count = r.read_int()
        sets = r.read_vector()
        unread = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.premium = premium
        self.hash = hash
        self.count = count
        self.sets = sets
        self.unread = unread
        return self


class RecentStickersNotModified(TLObject):
    """The TL type messages.recentStickersNotModified#0b17f890, a form of messages.RecentStickers."""

    __slots__ = ()

    ID = 0x0B17F890
    QUALNAME = "types.messages.RecentStickersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RecentStickers(TLObject):
    """The TL type messages.recentStickers#88d37c56, a form of messages.RecentStickers."""

    __slots__ = ("hash", "packs", "stickers", "dates",)

    ID = 0x88D37C56
    QUALNAME = "types.messages.RecentStickers"

    def __init__(
        self,
        *,
        hash: int,
        packs: list[base.StickerPack],
        stickers: list[base.Document],
        dates: list[int],
    ) -> None:
        self.hash = hash
        self.packs = packs
        self.stickers = stickers
        self.dates = dates

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.packs)
        w.write_vector(self.stickers)
        w.write_vector(self.dates, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        packs = r.read_vector()
        stickers = r.read_vector()
        dates = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.hash = hash
        self.packs = packs
        self.stickers = stickers
        self.dates = dates
        return self


class ArchivedStickers(TLObject):
    """The TL type messages.archivedStickers#4fcba9c8, a form of messages.ArchivedStickers."""

    __slots__ = ("count", "sets",)

    ID = 0x4FCBA9C8
    QUALNAME = "types.messages.ArchivedStickers"

    def __init__(
        self,
        *,
        count: int,
        sets: list[base.StickerSetCovered],
    ) -> None:
        self.count = count
        self.sets = sets

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.sets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        sets = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.sets = sets
        return self


class StickerSetInstallResultSuccess(TLObject):
    """The TL type messages.stickerSetInstallResultSuccess#38641628, a form of messages.StickerSetInstallResult."""

    __slots__ = ()

    ID = 0x38641628
    QUALNAME = "types.messages.StickerSetInstallResultSuccess"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class StickerSetInstallResultArchive(TLObject):
    """The TL type messages.stickerSetInstallResultArchive#35e410a8, a form of messages.StickerSetInstallResult."""

    __slots__ = ("sets",)

    ID = 0x35E410A8
    QUALNAME = "types.messages.StickerSetInstallResultArchive"

    def __init__(
        self,
        *,
        sets: list[base.StickerSetCovered],
    ) -> None:
        self.sets = sets

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.sets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        sets = r.read_vector()
        self = cls.__new__(cls)
        self.sets = sets
        return self


class HighScores(TLObject):
    """The TL type messages.highScores#9a3bfd99, a form of messages.HighScores."""

    __slots__ = ("scores", "users",)

    ID = 0x9A3BFD99
    QUALNAME = "types.messages.HighScores"

    def __init__(
        self,
        *,
        scores: list[base.HighScore],
        users: list[base.User],
    ) -> None:
        self.scores = scores
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.scores)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        scores = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.scores = scores
        self.users = users
        return self


class FavedStickersNotModified(TLObject):
    """The TL type messages.favedStickersNotModified#9e8fa6d3, a form of messages.FavedStickers."""

    __slots__ = ()

    ID = 0x9E8FA6D3
    QUALNAME = "types.messages.FavedStickersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FavedStickers(TLObject):
    """The TL type messages.favedStickers#2cb51097, a form of messages.FavedStickers."""

    __slots__ = ("hash", "packs", "stickers",)

    ID = 0x2CB51097
    QUALNAME = "types.messages.FavedStickers"

    def __init__(
        self,
        *,
        hash: int,
        packs: list[base.StickerPack],
        stickers: list[base.Document],
    ) -> None:
        self.hash = hash
        self.packs = packs
        self.stickers = stickers

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.packs)
        w.write_vector(self.stickers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        packs = r.read_vector()
        stickers = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.packs = packs
        self.stickers = stickers
        return self


class FoundStickerSetsNotModified(TLObject):
    """The TL type messages.foundStickerSetsNotModified#0d54b65d, a form of messages.FoundStickerSets."""

    __slots__ = ()

    ID = 0x0D54B65D
    QUALNAME = "types.messages.FoundStickerSetsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class FoundStickerSets(TLObject):
    """The TL type messages.foundStickerSets#8af09dd2, a form of messages.FoundStickerSets."""

    __slots__ = ("hash", "sets",)

    ID = 0x8AF09DD2
    QUALNAME = "types.messages.FoundStickerSets"

    def __init__(
        self,
        *,
        hash: int,
        sets: list[base.StickerSetCovered],
    ) -> None:
        self.hash = hash
        self.sets = sets

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.sets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        sets = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.sets = sets
        return self


class SearchCounter(TLObject):
    """The TL type messages.searchCounter#e844ebff, a form of messages.SearchCounter."""

    __slots__ = ("inexact", "filter", "count",)

    ID = 0xE844EBFF
    QUALNAME = "types.messages.SearchCounter"

    def __init__(
        self,
        *,
        inexact: bool = False,
        filter: base.MessagesFilter,
        count: int,
    ) -> None:
        self.inexact = inexact
        self.filter = filter
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inexact:
            flags |= 1 << 1
        w.write_int(flags)
        self.filter.write(w)
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inexact = bool(flags & (1 << 1))
        filter = r.read_object()
        count = r.read_int()
        self = cls.__new__(cls)
        self.inexact = inexact
        self.filter = filter
        self.count = count
        return self


class InactiveChats(TLObject):
    """The TL type messages.inactiveChats#a927fec5, a form of messages.InactiveChats."""

    __slots__ = ("dates", "chats", "users",)

    ID = 0xA927FEC5
    QUALNAME = "types.messages.InactiveChats"

    def __init__(
        self,
        *,
        dates: list[int],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.dates = dates
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.dates, TLWriter.write_int)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dates = r.read_vector(TLReader.read_int)
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.dates = dates
        self.chats = chats
        self.users = users
        return self


class VotesList(TLObject):
    """The TL type messages.votesList#4899484e, a form of messages.VotesList."""

    __slots__ = ("count", "votes", "chats", "users", "next_offset",)

    ID = 0x4899484E
    QUALNAME = "types.messages.VotesList"

    def __init__(
        self,
        *,
        count: int,
        votes: list[base.MessagePeerVote],
        chats: list[base.Chat],
        users: list[base.User],
        next_offset: str | None = None,
    ) -> None:
        self.count = count
        self.votes = votes
        self.chats = chats
        self.users = users
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.votes)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        if self.next_offset is not None:
            w.write_string(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        votes = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.count = count
        self.votes = votes
        self.chats = chats
        self.users = users
        self.next_offset = next_offset
        return self


class MessageViews(TLObject):
    """The TL type messages.messageViews#b6c4f543, a form of messages.MessageViews."""

    __slots__ = ("views", "chats", "users",)

    ID = 0xB6C4F543
    QUALNAME = "types.messages.MessageViews"

    def __init__(
        self,
        *,
        views: list[base.MessageViews],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.views = views
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.views)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        views = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.views = views
        self.chats = chats
        self.users = users
        return self


class DiscussionMessage(TLObject):
    """The TL type messages.discussionMessage#a6341782, a form of messages.DiscussionMessage."""

    __slots__ = ("messages", "max_id", "read_inbox_max_id", "read_outbox_max_id", "unread_count", "chats", "users",)

    ID = 0xA6341782
    QUALNAME = "types.messages.DiscussionMessage"

    def __init__(
        self,
        *,
        messages: list[base.Message],
        max_id: int | None = None,
        read_inbox_max_id: int | None = None,
        read_outbox_max_id: int | None = None,
        unread_count: int,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.messages = messages
        self.max_id = max_id
        self.read_inbox_max_id = read_inbox_max_id
        self.read_outbox_max_id = read_outbox_max_id
        self.unread_count = unread_count
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.max_id is not None:
            flags |= 1 << 0
        if self.read_inbox_max_id is not None:
            flags |= 1 << 1
        if self.read_outbox_max_id is not None:
            flags |= 1 << 2
        w.write_int(flags)
        w.write_vector(self.messages)
        if self.max_id is not None:
            w.write_int(self.max_id)
        if self.read_inbox_max_id is not None:
            w.write_int(self.read_inbox_max_id)
        if self.read_outbox_max_id is not None:
            w.write_int(self.read_outbox_max_id)
        w.write_int(self.unread_count)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        messages = r.read_vector()
        max_id = r.read_int() if flags & (1 << 0) else None
        read_inbox_max_id = r.read_int() if flags & (1 << 1) else None
        read_outbox_max_id = r.read_int() if flags & (1 << 2) else None
        unread_count = r.read_int()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.messages = messages
        self.max_id = max_id
        self.read_inbox_max_id = read_inbox_max_id
        self.read_outbox_max_id = read_outbox_max_id
        self.unread_count = unread_count
        self.chats = chats
        self.users = users
        return self


class HistoryImport(TLObject):
    """The TL type messages.historyImport#1662af0b, a form of messages.HistoryImport."""

    __slots__ = ("id",)

    ID = 0x1662AF0B
    QUALNAME = "types.messages.HistoryImport"

    def __init__(
        self,
        *,
        id: int,
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_long()
        self = cls.__new__(cls)
        self.id = id
        return self


class HistoryImportParsed(TLObject):
    """The TL type messages.historyImportParsed#5e0fb7b9, a form of messages.HistoryImportParsed."""

    __slots__ = ("pm", "group", "title",)

    ID = 0x5E0FB7B9
    QUALNAME = "types.messages.HistoryImportParsed"

    def __init__(
        self,
        *,
        pm: bool = False,
        group: bool = False,
        title: str | None = None,
    ) -> None:
        self.pm = pm
        self.group = group
        self.title = title

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pm:
            flags |= 1 << 0
        if self.group:
            flags |= 1 << 1
        if self.title is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.title is not None:
            w.write_string(self.title)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pm = bool(flags & (1 << 0))
        group = bool(flags & (1 << 1))
        title = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.pm = pm
        self.group = group
        self.title = title
        return self


class AffectedFoundMessages(TLObject):
    """The TL type messages.affectedFoundMessages#ef8d3e6c, a form of messages.AffectedFoundMessages."""

    __slots__ = ("pts", "pts_count", "offset", "messages",)

    ID = 0xEF8D3E6C
    QUALNAME = "types.messages.AffectedFoundMessages"

    def __init__(
        self,
        *,
        pts: int,
        pts_count: int,
        offset: int,
        messages: list[int],
    ) -> None:
        self.pts = pts
        self.pts_count = pts_count
        self.offset = offset
        self.messages = messages

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.pts)
        w.write_int(self.pts_count)
        w.write_int(self.offset)
        w.write_vector(self.messages, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pts = r.read_int()
        pts_count = r.read_int()
        offset = r.read_int()
        messages = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.pts = pts
        self.pts_count = pts_count
        self.offset = offset
        self.messages = messages
        return self


class ExportedChatInvites(TLObject):
    """The TL type messages.exportedChatInvites#bdc62dcc, a form of messages.ExportedChatInvites."""

    __slots__ = ("count", "invites", "users",)

    ID = 0xBDC62DCC
    QUALNAME = "types.messages.ExportedChatInvites"

    def __init__(
        self,
        *,
        count: int,
        invites: list[base.ExportedChatInvite],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.invites = invites
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.invites)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        invites = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.invites = invites
        self.users = users
        return self


class ExportedChatInvite(TLObject):
    """The TL type messages.exportedChatInvite#1871be50, a form of messages.ExportedChatInvite."""

    __slots__ = ("invite", "users",)

    ID = 0x1871BE50
    QUALNAME = "types.messages.ExportedChatInvite"

    def __init__(
        self,
        *,
        invite: base.ExportedChatInvite,
        users: list[base.User],
    ) -> None:
        self.invite = invite
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.invite.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        invite = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.invite = invite
        self.users = users
        return self


class ExportedChatInviteReplaced(TLObject):
    """The TL type messages.exportedChatInviteReplaced#222600ef, a form of messages.ExportedChatInvite."""

    __slots__ = ("invite", "new_invite", "users",)

    ID = 0x222600EF
    QUALNAME = "types.messages.ExportedChatInviteReplaced"

    def __init__(
        self,
        *,
        invite: base.ExportedChatInvite,
        new_invite: base.ExportedChatInvite,
        users: list[base.User],
    ) -> None:
        self.invite = invite
        self.new_invite = new_invite
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.invite.write(w)
        self.new_invite.write(w)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        invite = r.read_object()
        new_invite = r.read_object()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.invite = invite
        self.new_invite = new_invite
        self.users = users
        return self


class ChatInviteImporters(TLObject):
    """The TL type messages.chatInviteImporters#81b6b00a, a form of messages.ChatInviteImporters."""

    __slots__ = ("count", "importers", "users",)

    ID = 0x81B6B00A
    QUALNAME = "types.messages.ChatInviteImporters"

    def __init__(
        self,
        *,
        count: int,
        importers: list[base.ChatInviteImporter],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.importers = importers
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.importers)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        importers = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.importers = importers
        self.users = users
        return self


class ChatAdminsWithInvites(TLObject):
    """The TL type messages.chatAdminsWithInvites#b69b72d7, a form of messages.ChatAdminsWithInvites."""

    __slots__ = ("admins", "users",)

    ID = 0xB69B72D7
    QUALNAME = "types.messages.ChatAdminsWithInvites"

    def __init__(
        self,
        *,
        admins: list[base.ChatAdminWithInvites],
        users: list[base.User],
    ) -> None:
        self.admins = admins
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.admins)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        admins = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.admins = admins
        self.users = users
        return self


class CheckedHistoryImportPeer(TLObject):
    """The TL type messages.checkedHistoryImportPeer#a24de717, a form of messages.CheckedHistoryImportPeer."""

    __slots__ = ("confirm_text",)

    ID = 0xA24DE717
    QUALNAME = "types.messages.CheckedHistoryImportPeer"

    def __init__(
        self,
        *,
        confirm_text: str,
    ) -> None:
        self.confirm_text = confirm_text

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.confirm_text)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        confirm_text = r.read_string()
        self = cls.__new__(cls)
        self.confirm_text = confirm_text
        return self


class SponsoredMessages(TLObject):
    """The TL type messages.sponsoredMessages#ffda656d, a form of messages.SponsoredMessages."""

    __slots__ = ("posts_between", "start_delay", "between_delay", "messages", "chats", "users",)

    ID = 0xFFDA656D
    QUALNAME = "types.messages.SponsoredMessages"

    def __init__(
        self,
        *,
        posts_between: int | None = None,
        start_delay: int | None = None,
        between_delay: int | None = None,
        messages: list[base.SponsoredMessage],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.posts_between = posts_between
        self.start_delay = start_delay
        self.between_delay = between_delay
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.posts_between is not None:
            flags |= 1 << 0
        if self.start_delay is not None:
            flags |= 1 << 1
        if self.between_delay is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.posts_between is not None:
            w.write_int(self.posts_between)
        if self.start_delay is not None:
            w.write_int(self.start_delay)
        if self.between_delay is not None:
            w.write_int(self.between_delay)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        posts_between = r.read_int() if flags & (1 << 0) else None
        start_delay = r.read_int() if flags & (1 << 1) else None
        between_delay = r.read_int() if flags & (1 << 2) else None
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.posts_between = posts_between
        self.start_delay = start_delay
        self.between_delay = between_delay
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class SponsoredMessagesEmpty(TLObject):
    """The TL type messages.sponsoredMessagesEmpty#1839490f, a form of messages.SponsoredMessages."""

    __slots__ = ()

    ID = 0x1839490F
    QUALNAME = "types.messages.SponsoredMessagesEmpty"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SearchResultsCalendar(TLObject):
    """The TL type messages.searchResultsCalendar#147ee23c, a form of messages.SearchResultsCalendar."""

    __slots__ = ("inexact", "count", "min_date", "min_msg_id", "offset_id_offset", "periods", "messages", "chats", "users",)

    ID = 0x147EE23C
    QUALNAME = "types.messages.SearchResultsCalendar"

    def __init__(
        self,
        *,
        inexact: bool = False,
        count: int,
        min_date: int,
        min_msg_id: int,
        offset_id_offset: int | None = None,
        periods: list[base.SearchResultsCalendarPeriod],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.inexact = inexact
        self.count = count
        self.min_date = min_date
        self.min_msg_id = min_msg_id
        self.offset_id_offset = offset_id_offset
        self.periods = periods
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inexact:
            flags |= 1 << 0
        if self.offset_id_offset is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_int(self.count)
        w.write_int(self.min_date)
        w.write_int(self.min_msg_id)
        if self.offset_id_offset is not None:
            w.write_int(self.offset_id_offset)
        w.write_vector(self.periods)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inexact = bool(flags & (1 << 0))
        count = r.read_int()
        min_date = r.read_int()
        min_msg_id = r.read_int()
        offset_id_offset = r.read_int() if flags & (1 << 1) else None
        periods = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.inexact = inexact
        self.count = count
        self.min_date = min_date
        self.min_msg_id = min_msg_id
        self.offset_id_offset = offset_id_offset
        self.periods = periods
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class SearchResultsPositions(TLObject):
    """The TL type messages.searchResultsPositions#53b22baf, a form of messages.SearchResultsPositions."""

    __slots__ = ("count", "positions",)

    ID = 0x53B22BAF
    QUALNAME = "types.messages.SearchResultsPositions"

    def __init__(
        self,
        *,
        count: int,
        positions: list[base.SearchResultsPosition],
    ) -> None:
        self.count = count
        self.positions = positions

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.positions)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        positions = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.positions = positions
        return self


class PeerSettings(TLObject):
    """The TL type messages.peerSettings#6880b94d, a form of messages.PeerSettings."""

    __slots__ = ("settings", "chats", "users",)

    ID = 0x6880B94D
    QUALNAME = "types.messages.PeerSettings"

    def __init__(
        self,
        *,
        settings: base.PeerSettings,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.settings = settings
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.settings.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        settings = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.settings = settings
        self.chats = chats
        self.users = users
        return self


class MessageReactionsList(TLObject):
    """The TL type messages.messageReactionsList#31bd492d, a form of messages.MessageReactionsList."""

    __slots__ = ("count", "reactions", "chats", "users", "next_offset",)

    ID = 0x31BD492D
    QUALNAME = "types.messages.MessageReactionsList"

    def __init__(
        self,
        *,
        count: int,
        reactions: list[base.MessagePeerReaction],
        chats: list[base.Chat],
        users: list[base.User],
        next_offset: str | None = None,
    ) -> None:
        self.count = count
        self.reactions = reactions
        self.chats = chats
        self.users = users
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.reactions)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        if self.next_offset is not None:
            w.write_string(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        reactions = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.count = count
        self.reactions = reactions
        self.chats = chats
        self.users = users
        self.next_offset = next_offset
        return self


class AvailableReactionsNotModified(TLObject):
    """The TL type messages.availableReactionsNotModified#9f071957, a form of messages.AvailableReactions."""

    __slots__ = ()

    ID = 0x9F071957
    QUALNAME = "types.messages.AvailableReactionsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class AvailableReactions(TLObject):
    """The TL type messages.availableReactions#768e3aad, a form of messages.AvailableReactions."""

    __slots__ = ("hash", "reactions",)

    ID = 0x768E3AAD
    QUALNAME = "types.messages.AvailableReactions"

    def __init__(
        self,
        *,
        hash: int,
        reactions: list[base.AvailableReaction],
    ) -> None:
        self.hash = hash
        self.reactions = reactions

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        w.write_vector(self.reactions)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        reactions = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.reactions = reactions
        return self


class TranscribedAudio(TLObject):
    """The TL type messages.transcribedAudio#cfb9d957, a form of messages.TranscribedAudio."""

    __slots__ = ("pending", "transcription_id", "text", "trial_remains_num", "trial_remains_until_date",)

    ID = 0xCFB9D957
    QUALNAME = "types.messages.TranscribedAudio"

    def __init__(
        self,
        *,
        pending: bool = False,
        transcription_id: int,
        text: str,
        trial_remains_num: int | None = None,
        trial_remains_until_date: int | None = None,
    ) -> None:
        self.pending = pending
        self.transcription_id = transcription_id
        self.text = text
        self.trial_remains_num = trial_remains_num
        self.trial_remains_until_date = trial_remains_until_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pending:
            flags |= 1 << 0
        if self.trial_remains_num is not None:
            flags |= 1 << 1
        if self.trial_remains_until_date is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_long(self.transcription_id)
        w.write_string(self.text)
        if self.trial_remains_num is not None:
            w.write_int(self.trial_remains_num)
        if self.trial_remains_until_date is not None:
            w.write_int(self.trial_remains_until_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pending = bool(flags & (1 << 0))
        transcription_id = r.read_long()
        text = r.read_string()
        trial_remains_num = r.read_int() if flags & (1 << 1) else None
        trial_remains_until_date = r.read_int() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.pending = pending
        self.transcription_id = transcription_id
        self.text = text
        self.trial_remains_num = trial_remains_num
        self.trial_remains_until_date = trial_remains_until_date
        return self


class ReactionsNotModified(TLObject):
    """The TL type messages.reactionsNotModified#b06fdbdf, a form of messages.Reactions."""

    __slots__ = ()

    ID = 0xB06FDBDF
    QUALNAME = "types.messages.ReactionsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Reactions(TLObject):
    """The TL type messages.reactions#eafdf716, a form of messages.Reactions."""

    __slots__ = ("hash", "reactions",)

    ID = 0xEAFDF716
    QUALNAME = "types.messages.Reactions"

    def __init__(
        self,
        *,
        hash: int,
        reactions: list[base.Reaction],
    ) -> None:
        self.hash = hash
        self.reactions = reactions

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.reactions)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        reactions = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.reactions = reactions
        return self


class ForumTopics(TLObject):
    """The TL type messages.forumTopics#367617d3, a form of messages.ForumTopics."""

    __slots__ = ("order_by_create_date", "count", "topics", "messages", "chats", "users", "pts",)

    ID = 0x367617D3
    QUALNAME = "types.messages.ForumTopics"

    def __init__(
        self,
        *,
        order_by_create_date: bool = False,
        count: int,
        topics: list[base.ForumTopic],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
        pts: int,
    ) -> None:
        self.order_by_create_date = order_by_create_date
        self.count = count
        self.topics = topics
        self.messages = messages
        self.chats = chats
        self.users = users
        self.pts = pts

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.order_by_create_date:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.topics)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        w.write_int(self.pts)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        order_by_create_date = bool(flags & (1 << 0))
        count = r.read_int()
        topics = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        pts = r.read_int()
        self = cls.__new__(cls)
        self.order_by_create_date = order_by_create_date
        self.count = count
        self.topics = topics
        self.messages = messages
        self.chats = chats
        self.users = users
        self.pts = pts
        return self


class EmojiGroupsNotModified(TLObject):
    """The TL type messages.emojiGroupsNotModified#6fb4ad87, a form of messages.EmojiGroups."""

    __slots__ = ()

    ID = 0x6FB4AD87
    QUALNAME = "types.messages.EmojiGroupsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class EmojiGroups(TLObject):
    """The TL type messages.emojiGroups#881fb94b, a form of messages.EmojiGroups."""

    __slots__ = ("hash", "groups",)

    ID = 0x881FB94B
    QUALNAME = "types.messages.EmojiGroups"

    def __init__(
        self,
        *,
        hash: int,
        groups: list[base.EmojiGroup],
    ) -> None:
        self.hash = hash
        self.groups = groups

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        w.write_vector(self.groups)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        groups = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.groups = groups
        return self


class TranslateResult(TLObject):
    """The TL type messages.translateResult#33db32f8, a form of messages.TranslatedText."""

    __slots__ = ("result",)

    ID = 0x33DB32F8
    QUALNAME = "types.messages.TranslateResult"

    def __init__(
        self,
        *,
        result: list[base.TextWithEntities],
    ) -> None:
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.result)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        result = r.read_vector()
        self = cls.__new__(cls)
        self.result = result
        return self


class BotApp(TLObject):
    """The TL type messages.botApp#eb50adf5, a form of messages.BotApp."""

    __slots__ = ("inactive", "request_write_access", "has_settings", "app",)

    ID = 0xEB50ADF5
    QUALNAME = "types.messages.BotApp"

    def __init__(
        self,
        *,
        inactive: bool = False,
        request_write_access: bool = False,
        has_settings: bool = False,
        app: base.BotApp,
    ) -> None:
        self.inactive = inactive
        self.request_write_access = request_write_access
        self.has_settings = has_settings
        self.app = app

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.inactive:
            flags |= 1 << 0
        if self.request_write_access:
            flags |= 1 << 1
        if self.has_settings:
            flags |= 1 << 2
        w.write_int(flags)
        self.app.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        inactive = bool(flags & (1 << 0))
        request_write_access = bool(flags & (1 << 1))
        has_settings = bool(flags & (1 << 2))
        app = r.read_object()
        self = cls.__new__(cls)
        self.inactive = inactive
        self.request_write_access = request_write_access
        self.has_settings = has_settings
        self.app = app
        return self


class WebPage(TLObject):
    """The TL type messages.webPage#fd5e12bd, a form of messages.WebPage."""

    __slots__ = ("webpage", "chats", "users",)

    ID = 0xFD5E12BD
    QUALNAME = "types.messages.WebPage"

    def __init__(
        self,
        *,
        webpage: base.WebPage,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.webpage = webpage
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.webpage.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        webpage = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.webpage = webpage
        self.chats = chats
        self.users = users
        return self


class SavedDialogs(TLObject):
    """The TL type messages.savedDialogs#f83ae221, a form of messages.SavedDialogs."""

    __slots__ = ("dialogs", "messages", "chats", "users",)

    ID = 0xF83AE221
    QUALNAME = "types.messages.SavedDialogs"

    def __init__(
        self,
        *,
        dialogs: list[base.SavedDialog],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.dialogs)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dialogs = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class SavedDialogsSlice(TLObject):
    """The TL type messages.savedDialogsSlice#44ba9dd9, a form of messages.SavedDialogs."""

    __slots__ = ("count", "dialogs", "messages", "chats", "users",)

    ID = 0x44BA9DD9
    QUALNAME = "types.messages.SavedDialogsSlice"

    def __init__(
        self,
        *,
        count: int,
        dialogs: list[base.SavedDialog],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.dialogs)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        dialogs = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.dialogs = dialogs
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class SavedDialogsNotModified(TLObject):
    """The TL type messages.savedDialogsNotModified#c01f6fe8, a form of messages.SavedDialogs."""

    __slots__ = ("count",)

    ID = 0xC01F6FE8
    QUALNAME = "types.messages.SavedDialogsNotModified"

    def __init__(
        self,
        *,
        count: int,
    ) -> None:
        self.count = count

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        self = cls.__new__(cls)
        self.count = count
        return self


class SavedReactionTagsNotModified(TLObject):
    """The TL type messages.savedReactionTagsNotModified#889b59ef, a form of messages.SavedReactionTags."""

    __slots__ = ()

    ID = 0x889B59EF
    QUALNAME = "types.messages.SavedReactionTagsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedReactionTags(TLObject):
    """The TL type messages.savedReactionTags#3259950a, a form of messages.SavedReactionTags."""

    __slots__ = ("tags", "hash",)

    ID = 0x3259950A
    QUALNAME = "types.messages.SavedReactionTags"

    def __init__(
        self,
        *,
        tags: list[base.SavedReactionTag],
        hash: int,
    ) -> None:
        self.tags = tags
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.tags)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tags = r.read_vector()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.tags = tags
        self.hash = hash
        return self


class QuickReplies(TLObject):
    """The TL type messages.quickReplies#c68d6695, a form of messages.QuickReplies."""

    __slots__ = ("quick_replies", "messages", "chats", "users",)

    ID = 0xC68D6695
    QUALNAME = "types.messages.QuickReplies"

    def __init__(
        self,
        *,
        quick_replies: list[base.QuickReply],
        messages: list[base.Message],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.quick_replies = quick_replies
        self.messages = messages
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.quick_replies)
        w.write_vector(self.messages)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        quick_replies = r.read_vector()
        messages = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.quick_replies = quick_replies
        self.messages = messages
        self.chats = chats
        self.users = users
        return self


class QuickRepliesNotModified(TLObject):
    """The TL type messages.quickRepliesNotModified#5f91eb5b, a form of messages.QuickReplies."""

    __slots__ = ()

    ID = 0x5F91EB5B
    QUALNAME = "types.messages.QuickRepliesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DialogFilters(TLObject):
    """The TL type messages.dialogFilters#2ad93719, a form of messages.DialogFilters."""

    __slots__ = ("tags_enabled", "filters",)

    ID = 0x2AD93719
    QUALNAME = "types.messages.DialogFilters"

    def __init__(
        self,
        *,
        tags_enabled: bool = False,
        filters: list[base.DialogFilter],
    ) -> None:
        self.tags_enabled = tags_enabled
        self.filters = filters

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.tags_enabled:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.filters)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        tags_enabled = bool(flags & (1 << 0))
        filters = r.read_vector()
        self = cls.__new__(cls)
        self.tags_enabled = tags_enabled
        self.filters = filters
        return self


class MyStickers(TLObject):
    """The TL type messages.myStickers#faff629d, a form of messages.MyStickers."""

    __slots__ = ("count", "sets",)

    ID = 0xFAFF629D
    QUALNAME = "types.messages.MyStickers"

    def __init__(
        self,
        *,
        count: int,
        sets: list[base.StickerSetCovered],
    ) -> None:
        self.count = count
        self.sets = sets

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count)
        w.write_vector(self.sets)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count = r.read_int()
        sets = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.sets = sets
        return self


class InvitedUsers(TLObject):
    """The TL type messages.invitedUsers#7f5defa6, a form of messages.InvitedUsers."""

    __slots__ = ("updates", "missing_invitees",)

    ID = 0x7F5DEFA6
    QUALNAME = "types.messages.InvitedUsers"

    def __init__(
        self,
        *,
        updates: base.Updates,
        missing_invitees: list[base.MissingInvitee],
    ) -> None:
        self.updates = updates
        self.missing_invitees = missing_invitees

    def write_body(self, w: TLWriter) -> None:
        self.updates.write(w)
        w.write_vector(self.missing_invitees)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        updates = r.read_object()
        missing_invitees = r.read_vector()
        self = cls.__new__(cls)
        self.updates = updates
        self.missing_invitees = missing_invitees
        return self


class AvailableEffectsNotModified(TLObject):
    """The TL type messages.availableEffectsNotModified#d1ed9a5b, a form of messages.AvailableEffects."""

    __slots__ = ()

    ID = 0xD1ED9A5B
    QUALNAME = "types.messages.AvailableEffectsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class AvailableEffects(TLObject):
    """The TL type messages.availableEffects#bddb616e, a form of messages.AvailableEffects."""

    __slots__ = ("hash", "effects", "documents",)

    ID = 0xBDDB616E
    QUALNAME = "types.messages.AvailableEffects"

    def __init__(
        self,
        *,
        hash: int,
        effects: list[base.AvailableEffect],
        documents: list[base.Document],
    ) -> None:
        self.hash = hash
        self.effects = effects
        self.documents = documents

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        w.write_vector(self.effects)
        w.write_vector(self.documents)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        effects = r.read_vector()
        documents = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.effects = effects
        self.documents = documents
        return self


class BotPreparedInlineMessage(TLObject):
    """The TL type messages.botPreparedInlineMessage#8ecf0511, a form of messages.BotPreparedInlineMessage."""

    __slots__ = ("id", "expire_date",)

    ID = 0x8ECF0511
    QUALNAME = "types.messages.BotPreparedInlineMessage"

    def __init__(
        self,
        *,
        id: str,
        expire_date: int,
    ) -> None:
        self.id = id
        self.expire_date = expire_date

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.id)
        w.write_int(self.expire_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_string()
        expire_date = r.read_int()
        self = cls.__new__(cls)
        self.id = id
        self.expire_date = expire_date
        return self


class PreparedInlineMessage(TLObject):
    """The TL type messages.preparedInlineMessage#ff57708d, a form of messages.PreparedInlineMessage."""

    __slots__ = ("query_id", "result", "peer_types", "cache_time", "users",)

    ID = 0xFF57708D
    QUALNAME = "types.messages.PreparedInlineMessage"

    def __init__(
        self,
        *,
        query_id: int,
        result: base.BotInlineResult,
        peer_types: list[base.InlineQueryPeerType],
        cache_time: int,
        users: list[base.User],
    ) -> None:
        self.query_id = query_id
        self.result = result
        self.peer_types = peer_types
        self.cache_time = cache_time
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.query_id)
        self.result.write(w)
        w.write_vector(self.peer_types)
        w.write_int(self.cache_time)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        query_id = r.read_long()
        result = r.read_object()
        peer_types = r.read_vector()
        cache_time = r.read_int()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.query_id = query_id
        self.result = result
        self.peer_types = peer_types
        self.cache_time = cache_time
        self.users = users
        return self


class FoundStickersNotModified(TLObject):
    """The TL type messages.foundStickersNotModified#6010c534, a form of messages.FoundStickers."""

    __slots__ = ("next_offset",)

    ID = 0x6010C534
    QUALNAME = "types.messages.FoundStickersNotModified"

    def __init__(
        self,
        *,
        next_offset: int | None = None,
    ) -> None:
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.next_offset is not None:
            w.write_int(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        next_offset = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.next_offset = next_offset
        return self


class FoundStickers(TLObject):
    """The TL type messages.foundStickers#82c9e290, a form of messages.FoundStickers."""

    __slots__ = ("next_offset", "hash", "stickers",)

    ID = 0x82C9E290
    QUALNAME = "types.messages.FoundStickers"

    def __init__(
        self,
        *,
        next_offset: int | None = None,
        hash: int,
        stickers: list[base.Document],
    ) -> None:
        self.next_offset = next_offset
        self.hash = hash
        self.stickers = stickers

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.next_offset is not None:
            w.write_int(self.next_offset)
        w.write_long(self.hash)
        w.write_vector(self.stickers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        next_offset = r.read_int() if flags & (1 << 0) else None
        hash = r.read_long()
        stickers = r.read_vector()
        self = cls.__new__(cls)
        self.next_offset = next_offset
        self.hash = hash
        self.stickers = stickers
        return self


class WebPagePreview(TLObject):
    """The TL type messages.webPagePreview#8c9a88ac, a form of messages.WebPagePreview."""

    __slots__ = ("media", "chats", "users",)

    ID = 0x8C9A88AC
    QUALNAME = "types.messages.WebPagePreview"

    def __init__(
        self,
        *,
        media: base.MessageMedia,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.media = media
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.media.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        media = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.media = media
        self.chats = chats
        self.users = users
        return self


class EmojiGameOutcome(TLObject):
    """The TL type messages.emojiGameOutcome#da2ad647, a form of messages.EmojiGameOutcome."""

    __slots__ = ("seed", "stake_ton_amount", "ton_amount",)

    ID = 0xDA2AD647
    QUALNAME = "types.messages.EmojiGameOutcome"

    def __init__(
        self,
        *,
        seed: bytes,
        stake_ton_amount: int,
        ton_amount: int,
    ) -> None:
        self.seed = seed
        self.stake_ton_amount = stake_ton_amount
        self.ton_amount = ton_amount

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.seed)
        w.write_long(self.stake_ton_amount)
        w.write_long(self.ton_amount)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        seed = r.read_bytes()
        stake_ton_amount = r.read_long()
        ton_amount = r.read_long()
        self = cls.__new__(cls)
        self.seed = seed
        self.stake_ton_amount = stake_ton_amount
        self.ton_amount = ton_amount
        return self


class EmojiGameUnavailable(TLObject):
    """The TL type messages.emojiGameUnavailable#59e65335, a form of messages.EmojiGameInfo."""

    __slots__ = ()

    ID = 0x59E65335
    QUALNAME = "types.messages.EmojiGameUnavailable"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class EmojiGameDiceInfo(TLObject):
    """The TL type messages.emojiGameDiceInfo#44e56023, a form of messages.EmojiGameInfo."""

    __slots__ = ("game_hash", "prev_stake", "current_streak", "params", "plays_left",)

    ID = 0x44E56023
    QUALNAME = "types.messages.EmojiGameDiceInfo"

    def __init__(
        self,
        *,
        game_hash: str,
        prev_stake: int,
        current_streak: int,
        params: list[int],
        plays_left: int | None = None,
    ) -> None:
        self.game_hash = game_hash
        self.prev_stake = prev_stake
        self.current_streak = current_streak
        self.params = params
        self.plays_left = plays_left

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.plays_left is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.game_hash)
        w.write_long(self.prev_stake)
        w.write_int(self.current_streak)
        w.write_vector(self.params, TLWriter.write_int)
        if self.plays_left is not None:
            w.write_int(self.plays_left)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        game_hash = r.read_string()
        prev_stake = r.read_long()
        current_streak = r.read_int()
        params = r.read_vector(TLReader.read_int)
        plays_left = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.game_hash = game_hash
        self.prev_stake = prev_stake
        self.current_streak = current_streak
        self.params = params
        self.plays_left = plays_left
        return self


class ComposedMessageWithAI(TLObject):
    """The TL type messages.composedMessageWithAI#90d7adfa, a form of messages.ComposedMessageWithAI."""

    __slots__ = ("result_text", "diff_text",)

    ID = 0x90D7ADFA
    QUALNAME = "types.messages.ComposedMessageWithAI"

    def __init__(
        self,
        *,
        result_text: base.TextWithEntities,
        diff_text: base.TextWithEntities | None = None,
    ) -> None:
        self.result_text = result_text
        self.diff_text = diff_text

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.diff_text is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.result_text.write(w)
        if self.diff_text is not None:
            self.diff_text.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        result_text = r.read_object()
        diff_text = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.result_text = result_text
        self.diff_text = diff_text
        return self


class ChatInviteJoinResultOk(TLObject):
    """The TL type messages.chatInviteJoinResultOk#445663a7, a form of messages.ChatInviteJoinResult."""

    __slots__ = ("updates",)

    ID = 0x445663A7
    QUALNAME = "types.messages.ChatInviteJoinResultOk"

    def __init__(
        self,
        *,
        updates: base.Updates,
    ) -> None:
        self.updates = updates

    def write_body(self, w: TLWriter) -> None:
        self.updates.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        updates = r.read_object()
        self = cls.__new__(cls)
        self.updates = updates
        return self


class ChatInviteJoinResultWebView(TLObject):
    """The TL type messages.chatInviteJoinResultWebView#61ca29d3, a form of messages.ChatInviteJoinResult."""

    __slots__ = ("bot_id", "query_id", "users",)

    ID = 0x61CA29D3
    QUALNAME = "types.messages.ChatInviteJoinResultWebView"

    def __init__(
        self,
        *,
        bot_id: int,
        query_id: int,
        users: list[base.User],
    ) -> None:
        self.bot_id = bot_id
        self.query_id = query_id
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.bot_id)
        w.write_long(self.query_id)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot_id = r.read_long()
        query_id = r.read_long()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.bot_id = bot_id
        self.query_id = query_id
        self.users = users
        return self


class TranslatedRichMessage(TLObject):
    """The TL type messages.translatedRichMessage#4203998f, a form of messages.TranslatedRichMessage."""

    __slots__ = ("result",)

    ID = 0x4203998F
    QUALNAME = "types.messages.TranslatedRichMessage"

    def __init__(
        self,
        *,
        result: list[base.RichMessage],
    ) -> None:
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.result)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        result = r.read_vector()
        self = cls.__new__(cls)
        self.result = result
        return self


class ComposedRichMessageWithAI(TLObject):
    """The TL type messages.composedRichMessageWithAI#4c4537c8, a form of messages.ComposedRichMessageWithAI."""

    __slots__ = ("result",)

    ID = 0x4C4537C8
    QUALNAME = "types.messages.ComposedRichMessageWithAI"

    def __init__(
        self,
        *,
        result: base.RichMessage,
    ) -> None:
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        self.result.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        result = r.read_object()
        self = cls.__new__(cls)
        self.result = result
        return self
