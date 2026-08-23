# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the stories namespace.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class AllStoriesNotModified(TLObject):
    """The TL type stories.allStoriesNotModified#1158fe3e, a form of stories.AllStories."""

    __slots__ = ("state", "stealth_mode",)

    ID = 0x1158FE3E
    QUALNAME = "types.stories.AllStoriesNotModified"

    def __init__(
        self,
        *,
        state: str,
        stealth_mode: base.StoriesStealthMode,
    ) -> None:
        self.state = state
        self.stealth_mode = stealth_mode

    def write_body(self, w: TLWriter) -> None:
        w.write_int(0)
        w.write_string(self.state)
        self.stealth_mode.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        r.read_int()
        state = r.read_string()
        stealth_mode = r.read_object()
        self = cls.__new__(cls)
        self.state = state
        self.stealth_mode = stealth_mode
        return self


class AllStories(TLObject):
    """The TL type stories.allStories#6efc5e81, a form of stories.AllStories."""

    __slots__ = ("has_more", "count", "state", "peer_stories", "chats", "users", "stealth_mode",)

    ID = 0x6EFC5E81
    QUALNAME = "types.stories.AllStories"

    def __init__(
        self,
        *,
        has_more: bool = False,
        count: int,
        state: str,
        peer_stories: list[base.PeerStories],
        chats: list[base.Chat],
        users: list[base.User],
        stealth_mode: base.StoriesStealthMode,
    ) -> None:
        self.has_more = has_more
        self.count = count
        self.state = state
        self.peer_stories = peer_stories
        self.chats = chats
        self.users = users
        self.stealth_mode = stealth_mode

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.has_more:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_string(self.state)
        w.write_vector(self.peer_stories)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        self.stealth_mode.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        has_more = bool(flags & (1 << 0))
        count = r.read_int()
        state = r.read_string()
        peer_stories = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        stealth_mode = r.read_object()
        self = cls.__new__(cls)
        self.has_more = has_more
        self.count = count
        self.state = state
        self.peer_stories = peer_stories
        self.chats = chats
        self.users = users
        self.stealth_mode = stealth_mode
        return self


class Stories(TLObject):
    """The TL type stories.stories#63c3dd0a, a form of stories.Stories."""

    __slots__ = ("count", "stories", "pinned_to_top", "chats", "users",)

    ID = 0x63C3DD0A
    QUALNAME = "types.stories.Stories"

    def __init__(
        self,
        *,
        count: int,
        stories: list[base.StoryItem],
        pinned_to_top: list[int] | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.stories = stories
        self.pinned_to_top = pinned_to_top
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pinned_to_top is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.stories)
        if self.pinned_to_top is not None:
            w.write_vector(self.pinned_to_top, TLWriter.write_int)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        stories = r.read_vector()
        pinned_to_top = r.read_vector(TLReader.read_int) if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.stories = stories
        self.pinned_to_top = pinned_to_top
        self.chats = chats
        self.users = users
        return self


class StoryViewsList(TLObject):
    """The TL type stories.storyViewsList#59d78fc5, a form of stories.StoryViewsList."""

    __slots__ = ("count", "views_count", "forwards_count", "reactions_count", "views", "chats", "users", "next_offset",)

    ID = 0x59D78FC5
    QUALNAME = "types.stories.StoryViewsList"

    def __init__(
        self,
        *,
        count: int,
        views_count: int,
        forwards_count: int,
        reactions_count: int,
        views: list[base.StoryView],
        chats: list[base.Chat],
        users: list[base.User],
        next_offset: str | None = None,
    ) -> None:
        self.count = count
        self.views_count = views_count
        self.forwards_count = forwards_count
        self.reactions_count = reactions_count
        self.views = views
        self.chats = chats
        self.users = users
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_int(self.views_count)
        w.write_int(self.forwards_count)
        w.write_int(self.reactions_count)
        w.write_vector(self.views)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        if self.next_offset is not None:
            w.write_string(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        views_count = r.read_int()
        forwards_count = r.read_int()
        reactions_count = r.read_int()
        views = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.count = count
        self.views_count = views_count
        self.forwards_count = forwards_count
        self.reactions_count = reactions_count
        self.views = views
        self.chats = chats
        self.users = users
        self.next_offset = next_offset
        return self


class StoryViews(TLObject):
    """The TL type stories.storyViews#de9eed1d, a form of stories.StoryViews."""

    __slots__ = ("views", "users",)

    ID = 0xDE9EED1D
    QUALNAME = "types.stories.StoryViews"

    def __init__(
        self,
        *,
        views: list[base.StoryViews],
        users: list[base.User],
    ) -> None:
        self.views = views
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.views)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        views = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.views = views
        self.users = users
        return self


class PeerStories(TLObject):
    """The TL type stories.peerStories#cae68768, a form of stories.PeerStories."""

    __slots__ = ("stories", "chats", "users",)

    ID = 0xCAE68768
    QUALNAME = "types.stories.PeerStories"

    def __init__(
        self,
        *,
        stories: base.PeerStories,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.stories = stories
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.stories.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stories = r.read_object()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.stories = stories
        self.chats = chats
        self.users = users
        return self


class StoryReactionsList(TLObject):
    """The TL type stories.storyReactionsList#aa5f789c, a form of stories.StoryReactionsList."""

    __slots__ = ("count", "reactions", "chats", "users", "next_offset",)

    ID = 0xAA5F789C
    QUALNAME = "types.stories.StoryReactionsList"

    def __init__(
        self,
        *,
        count: int,
        reactions: list[base.StoryReaction],
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


class FoundStories(TLObject):
    """The TL type stories.foundStories#e2de7737, a form of stories.FoundStories."""

    __slots__ = ("count", "stories", "next_offset", "chats", "users",)

    ID = 0xE2DE7737
    QUALNAME = "types.stories.FoundStories"

    def __init__(
        self,
        *,
        count: int,
        stories: list[base.FoundStory],
        next_offset: str | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.count = count
        self.stories = stories
        self.next_offset = next_offset
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.count)
        w.write_vector(self.stories)
        if self.next_offset is not None:
            w.write_string(self.next_offset)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        count = r.read_int()
        stories = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.count = count
        self.stories = stories
        self.next_offset = next_offset
        self.chats = chats
        self.users = users
        return self


class CanSendStoryCount(TLObject):
    """The TL type stories.canSendStoryCount#c387c04e, a form of stories.CanSendStoryCount."""

    __slots__ = ("count_remains",)

    ID = 0xC387C04E
    QUALNAME = "types.stories.CanSendStoryCount"

    def __init__(
        self,
        *,
        count_remains: int,
    ) -> None:
        self.count_remains = count_remains

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.count_remains)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        count_remains = r.read_int()
        self = cls.__new__(cls)
        self.count_remains = count_remains
        return self


class AlbumsNotModified(TLObject):
    """The TL type stories.albumsNotModified#564edaeb, a form of stories.Albums."""

    __slots__ = ()

    ID = 0x564EDAEB
    QUALNAME = "types.stories.AlbumsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Albums(TLObject):
    """The TL type stories.albums#c3987a3a, a form of stories.Albums."""

    __slots__ = ("hash", "albums",)

    ID = 0xC3987A3A
    QUALNAME = "types.stories.Albums"

    def __init__(
        self,
        *,
        hash: int,
        albums: list[base.StoryAlbum],
    ) -> None:
        self.hash = hash
        self.albums = albums

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.albums)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        albums = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.albums = albums
        return self
