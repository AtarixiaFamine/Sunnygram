# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the stories namespace.

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


class CanSendStory(TLFunction["base.stories.CanSendStoryCount"]):
    """The TL function stories.canSendStory#30eb63f0, answered with stories.CanSendStoryCount."""

    __slots__ = ("peer",)

    ID = 0x30EB63F0
    QUALNAME = "functions.stories.CanSendStory"
    RESULT = "stories.CanSendStoryCount"

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


class SendStory(TLFunction["base.Updates"]):
    """The TL function stories.sendStory#8f9e6898, answered with Updates."""

    __slots__ = ("pinned", "noforwards", "fwd_modified", "peer", "media", "media_areas", "caption", "entities", "privacy_rules", "random_id", "period", "fwd_from_id", "fwd_from_story", "albums", "music",)

    ID = 0x8F9E6898
    QUALNAME = "functions.stories.SendStory"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        pinned: bool = False,
        noforwards: bool = False,
        fwd_modified: bool = False,
        peer: base.InputPeer,
        media: base.InputMedia,
        media_areas: list[base.MediaArea] | None = None,
        caption: str | None = None,
        entities: list[base.MessageEntity] | None = None,
        privacy_rules: list[base.InputPrivacyRule],
        random_id: int,
        period: int | None = None,
        fwd_from_id: base.InputPeer | None = None,
        fwd_from_story: int | None = None,
        albums: list[int] | None = None,
        music: base.InputDocument | None = None,
    ) -> None:
        self.pinned = pinned
        self.noforwards = noforwards
        self.fwd_modified = fwd_modified
        self.peer = peer
        self.media = media
        self.media_areas = media_areas
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.random_id = random_id
        self.period = period
        self.fwd_from_id = fwd_from_id
        self.fwd_from_story = fwd_from_story
        self.albums = albums
        self.music = music

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pinned:
            flags |= 1 << 2
        if self.noforwards:
            flags |= 1 << 4
        if self.fwd_modified:
            flags |= 1 << 7
        if self.media_areas is not None:
            flags |= 1 << 5
        if self.caption is not None:
            flags |= 1 << 0
        if self.entities is not None:
            flags |= 1 << 1
        if self.period is not None:
            flags |= 1 << 3
        if self.fwd_from_id is not None:
            flags |= 1 << 6
        if self.fwd_from_story is not None:
            flags |= 1 << 6
        if self.albums is not None:
            flags |= 1 << 8
        if self.music is not None:
            flags |= 1 << 9
        w.write_int(flags)
        self.peer.write(w)
        self.media.write(w)
        if self.media_areas is not None:
            w.write_vector(self.media_areas)
        if self.caption is not None:
            w.write_string(self.caption)
        if self.entities is not None:
            w.write_vector(self.entities)
        w.write_vector(self.privacy_rules)
        w.write_long(self.random_id)
        if self.period is not None:
            w.write_int(self.period)
        if self.fwd_from_id is not None:
            self.fwd_from_id.write(w)
        if self.fwd_from_story is not None:
            w.write_int(self.fwd_from_story)
        if self.albums is not None:
            w.write_vector(self.albums, TLWriter.write_int)
        if self.music is not None:
            self.music.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pinned = bool(flags & (1 << 2))
        noforwards = bool(flags & (1 << 4))
        fwd_modified = bool(flags & (1 << 7))
        peer = r.read_object()
        media = r.read_object()
        media_areas = r.read_vector() if flags & (1 << 5) else None
        caption = r.read_string() if flags & (1 << 0) else None
        entities = r.read_vector() if flags & (1 << 1) else None
        privacy_rules = r.read_vector()
        random_id = r.read_long()
        period = r.read_int() if flags & (1 << 3) else None
        fwd_from_id = r.read_object() if flags & (1 << 6) else None
        fwd_from_story = r.read_int() if flags & (1 << 6) else None
        albums = r.read_vector(TLReader.read_int) if flags & (1 << 8) else None
        music = r.read_object() if flags & (1 << 9) else None
        self = cls.__new__(cls)
        self.pinned = pinned
        self.noforwards = noforwards
        self.fwd_modified = fwd_modified
        self.peer = peer
        self.media = media
        self.media_areas = media_areas
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.random_id = random_id
        self.period = period
        self.fwd_from_id = fwd_from_id
        self.fwd_from_story = fwd_from_story
        self.albums = albums
        self.music = music
        return self


class EditStory(TLFunction["base.Updates"]):
    """The TL function stories.editStory#2c63a72b, answered with Updates."""

    __slots__ = ("peer", "id", "media", "media_areas", "caption", "entities", "privacy_rules", "music",)

    ID = 0x2C63A72B
    QUALNAME = "functions.stories.EditStory"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: int,
        media: base.InputMedia | None = None,
        media_areas: list[base.MediaArea] | None = None,
        caption: str | None = None,
        entities: list[base.MessageEntity] | None = None,
        privacy_rules: list[base.InputPrivacyRule] | None = None,
        music: base.InputDocument | None = None,
    ) -> None:
        self.peer = peer
        self.id = id
        self.media = media
        self.media_areas = media_areas
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.music = music

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.media is not None:
            flags |= 1 << 0
        if self.media_areas is not None:
            flags |= 1 << 3
        if self.caption is not None:
            flags |= 1 << 1
        if self.entities is not None:
            flags |= 1 << 1
        if self.privacy_rules is not None:
            flags |= 1 << 2
        if self.music is not None:
            flags |= 1 << 4
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.id)
        if self.media is not None:
            self.media.write(w)
        if self.media_areas is not None:
            w.write_vector(self.media_areas)
        if self.caption is not None:
            w.write_string(self.caption)
        if self.entities is not None:
            w.write_vector(self.entities)
        if self.privacy_rules is not None:
            w.write_vector(self.privacy_rules)
        if self.music is not None:
            self.music.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        id = r.read_int()
        media = r.read_object() if flags & (1 << 0) else None
        media_areas = r.read_vector() if flags & (1 << 3) else None
        caption = r.read_string() if flags & (1 << 1) else None
        entities = r.read_vector() if flags & (1 << 1) else None
        privacy_rules = r.read_vector() if flags & (1 << 2) else None
        music = r.read_object() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.media = media
        self.media_areas = media_areas
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.music = music
        return self


class DeleteStories(TLFunction["list[int]"]):
    """The TL function stories.deleteStories#ae59db5f, answered with Vector<int>."""

    __slots__ = ("peer", "id",)

    ID = 0xAE59DB5F
    QUALNAME = "functions.stories.DeleteStories"
    RESULT = "Vector<int>"

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


class TogglePinned(TLFunction["list[int]"]):
    """The TL function stories.togglePinned#9a75a1ef, answered with Vector<int>."""

    __slots__ = ("peer", "id", "pinned",)

    ID = 0x9A75A1EF
    QUALNAME = "functions.stories.TogglePinned"
    RESULT = "Vector<int>"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        id: list[int],
        pinned: bool,
    ) -> None:
        self.peer = peer
        self.id = id
        self.pinned = pinned

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.id, TLWriter.write_int)
        w.write_bool(self.pinned)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        id = r.read_vector(TLReader.read_int)
        pinned = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.id = id
        self.pinned = pinned
        return self


class GetAllStories(TLFunction["base.stories.AllStories"]):
    """The TL function stories.getAllStories#eeb0d625, answered with stories.AllStories."""

    __slots__ = ("next", "hidden", "state",)

    ID = 0xEEB0D625
    QUALNAME = "functions.stories.GetAllStories"
    RESULT = "stories.AllStories"

    def __init__(
        self,
        *,
        next: bool = False,
        hidden: bool = False,
        state: str | None = None,
    ) -> None:
        self.next = next
        self.hidden = hidden
        self.state = state

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next:
            flags |= 1 << 1
        if self.hidden:
            flags |= 1 << 2
        if self.state is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.state is not None:
            w.write_string(self.state)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        next = bool(flags & (1 << 1))
        hidden = bool(flags & (1 << 2))
        state = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.next = next
        self.hidden = hidden
        self.state = state
        return self


class GetPinnedStories(TLFunction["base.stories.Stories"]):
    """The TL function stories.getPinnedStories#5821a5dc, answered with stories.Stories."""

    __slots__ = ("peer", "offset_id", "limit",)

    ID = 0x5821A5DC
    QUALNAME = "functions.stories.GetPinnedStories"
    RESULT = "stories.Stories"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        offset_id: int,
        limit: int,
    ) -> None:
        self.peer = peer
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        offset_id = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.offset_id = offset_id
        self.limit = limit
        return self


class GetStoriesArchive(TLFunction["base.stories.Stories"]):
    """The TL function stories.getStoriesArchive#b4352016, answered with stories.Stories."""

    __slots__ = ("peer", "offset_id", "limit",)

    ID = 0xB4352016
    QUALNAME = "functions.stories.GetStoriesArchive"
    RESULT = "stories.Stories"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        offset_id: int,
        limit: int,
    ) -> None:
        self.peer = peer
        self.offset_id = offset_id
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.offset_id)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        offset_id = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.offset_id = offset_id
        self.limit = limit
        return self


class GetStoriesByID(TLFunction["base.stories.Stories"]):
    """The TL function stories.getStoriesByID#5774ca74, answered with stories.Stories."""

    __slots__ = ("peer", "id",)

    ID = 0x5774CA74
    QUALNAME = "functions.stories.GetStoriesByID"
    RESULT = "stories.Stories"

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


class ToggleAllStoriesHidden(TLFunction["bool"]):
    """The TL function stories.toggleAllStoriesHidden#7c2557c4, answered with Bool."""

    __slots__ = ("hidden",)

    ID = 0x7C2557C4
    QUALNAME = "functions.stories.ToggleAllStoriesHidden"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        hidden: bool,
    ) -> None:
        self.hidden = hidden

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.hidden)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hidden = r.read_bool()
        self = cls.__new__(cls)
        self.hidden = hidden
        return self


class ReadStories(TLFunction["list[int]"]):
    """The TL function stories.readStories#a556dac8, answered with Vector<int>."""

    __slots__ = ("peer", "max_id",)

    ID = 0xA556DAC8
    QUALNAME = "functions.stories.ReadStories"
    RESULT = "Vector<int>"

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


class IncrementStoryViews(TLFunction["bool"]):
    """The TL function stories.incrementStoryViews#b2028afb, answered with Bool."""

    __slots__ = ("peer", "id",)

    ID = 0xB2028AFB
    QUALNAME = "functions.stories.IncrementStoryViews"
    RESULT = "Bool"

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


class GetStoryViewsList(TLFunction["base.stories.StoryViewsList"]):
    """The TL function stories.getStoryViewsList#7ed23c57, answered with stories.StoryViewsList."""

    __slots__ = ("just_contacts", "reactions_first", "forwards_first", "peer", "q", "id", "offset", "limit",)

    ID = 0x7ED23C57
    QUALNAME = "functions.stories.GetStoryViewsList"
    RESULT = "stories.StoryViewsList"

    def __init__(
        self,
        *,
        just_contacts: bool = False,
        reactions_first: bool = False,
        forwards_first: bool = False,
        peer: base.InputPeer,
        q: str | None = None,
        id: int,
        offset: str,
        limit: int,
    ) -> None:
        self.just_contacts = just_contacts
        self.reactions_first = reactions_first
        self.forwards_first = forwards_first
        self.peer = peer
        self.q = q
        self.id = id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.just_contacts:
            flags |= 1 << 0
        if self.reactions_first:
            flags |= 1 << 2
        if self.forwards_first:
            flags |= 1 << 3
        if self.q is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.peer.write(w)
        if self.q is not None:
            w.write_string(self.q)
        w.write_int(self.id)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        just_contacts = bool(flags & (1 << 0))
        reactions_first = bool(flags & (1 << 2))
        forwards_first = bool(flags & (1 << 3))
        peer = r.read_object()
        q = r.read_string() if flags & (1 << 1) else None
        id = r.read_int()
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.just_contacts = just_contacts
        self.reactions_first = reactions_first
        self.forwards_first = forwards_first
        self.peer = peer
        self.q = q
        self.id = id
        self.offset = offset
        self.limit = limit
        return self


class GetStoriesViews(TLFunction["base.stories.StoryViews"]):
    """The TL function stories.getStoriesViews#28e16cc8, answered with stories.StoryViews."""

    __slots__ = ("peer", "id",)

    ID = 0x28E16CC8
    QUALNAME = "functions.stories.GetStoriesViews"
    RESULT = "stories.StoryViews"

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


class ExportStoryLink(TLFunction["base.ExportedStoryLink"]):
    """The TL function stories.exportStoryLink#7b8def20, answered with ExportedStoryLink."""

    __slots__ = ("peer", "id",)

    ID = 0x7B8DEF20
    QUALNAME = "functions.stories.ExportStoryLink"
    RESULT = "ExportedStoryLink"

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


class Report(TLFunction["base.ReportResult"]):
    """The TL function stories.report#19d8eb45, answered with ReportResult."""

    __slots__ = ("peer", "id", "option", "message",)

    ID = 0x19D8EB45
    QUALNAME = "functions.stories.Report"
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


class ActivateStealthMode(TLFunction["base.Updates"]):
    """The TL function stories.activateStealthMode#57bbd166, answered with Updates."""

    __slots__ = ("past", "future",)

    ID = 0x57BBD166
    QUALNAME = "functions.stories.ActivateStealthMode"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        past: bool = False,
        future: bool = False,
    ) -> None:
        self.past = past
        self.future = future

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.past:
            flags |= 1 << 0
        if self.future:
            flags |= 1 << 1
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        past = bool(flags & (1 << 0))
        future = bool(flags & (1 << 1))
        self = cls.__new__(cls)
        self.past = past
        self.future = future
        return self


class SendReaction(TLFunction["base.Updates"]):
    """The TL function stories.sendReaction#7fd736b2, answered with Updates."""

    __slots__ = ("add_to_recent", "peer", "story_id", "reaction",)

    ID = 0x7FD736B2
    QUALNAME = "functions.stories.SendReaction"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        add_to_recent: bool = False,
        peer: base.InputPeer,
        story_id: int,
        reaction: base.Reaction,
    ) -> None:
        self.add_to_recent = add_to_recent
        self.peer = peer
        self.story_id = story_id
        self.reaction = reaction

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.add_to_recent:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.story_id)
        self.reaction.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        add_to_recent = bool(flags & (1 << 0))
        peer = r.read_object()
        story_id = r.read_int()
        reaction = r.read_object()
        self = cls.__new__(cls)
        self.add_to_recent = add_to_recent
        self.peer = peer
        self.story_id = story_id
        self.reaction = reaction
        return self


class GetPeerStories(TLFunction["base.stories.PeerStories"]):
    """The TL function stories.getPeerStories#2c4ada50, answered with stories.PeerStories."""

    __slots__ = ("peer",)

    ID = 0x2C4ADA50
    QUALNAME = "functions.stories.GetPeerStories"
    RESULT = "stories.PeerStories"

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


class GetAllReadPeerStories(TLFunction["base.Updates"]):
    """The TL function stories.getAllReadPeerStories#9b5ae7f9, answered with Updates."""

    __slots__ = ()

    ID = 0x9B5AE7F9
    QUALNAME = "functions.stories.GetAllReadPeerStories"
    RESULT = "Updates"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetPeerMaxIDs(TLFunction["list[base.RecentStory]"]):
    """The TL function stories.getPeerMaxIDs#78499170, answered with Vector<RecentStory>."""

    __slots__ = ("id",)

    ID = 0x78499170
    QUALNAME = "functions.stories.GetPeerMaxIDs"
    RESULT = "Vector<RecentStory>"

    def __init__(
        self,
        *,
        id: list[base.InputPeer],
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


class GetChatsToSend(TLFunction["base.messages.Chats"]):
    """The TL function stories.getChatsToSend#a56a8b60, answered with messages.Chats."""

    __slots__ = ()

    ID = 0xA56A8B60
    QUALNAME = "functions.stories.GetChatsToSend"
    RESULT = "messages.Chats"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class TogglePeerStoriesHidden(TLFunction["bool"]):
    """The TL function stories.togglePeerStoriesHidden#bd0415c4, answered with Bool."""

    __slots__ = ("peer", "hidden",)

    ID = 0xBD0415C4
    QUALNAME = "functions.stories.TogglePeerStoriesHidden"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        hidden: bool,
    ) -> None:
        self.peer = peer
        self.hidden = hidden

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bool(self.hidden)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        hidden = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.hidden = hidden
        return self


class GetStoryReactionsList(TLFunction["base.stories.StoryReactionsList"]):
    """The TL function stories.getStoryReactionsList#b9b2881f, answered with stories.StoryReactionsList."""

    __slots__ = ("forwards_first", "peer", "id", "reaction", "offset", "limit",)

    ID = 0xB9B2881F
    QUALNAME = "functions.stories.GetStoryReactionsList"
    RESULT = "stories.StoryReactionsList"

    def __init__(
        self,
        *,
        forwards_first: bool = False,
        peer: base.InputPeer,
        id: int,
        reaction: base.Reaction | None = None,
        offset: str | None = None,
        limit: int,
    ) -> None:
        self.forwards_first = forwards_first
        self.peer = peer
        self.id = id
        self.reaction = reaction
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.forwards_first:
            flags |= 1 << 2
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
        forwards_first = bool(flags & (1 << 2))
        peer = r.read_object()
        id = r.read_int()
        reaction = r.read_object() if flags & (1 << 0) else None
        offset = r.read_string() if flags & (1 << 1) else None
        limit = r.read_int()
        self = cls.__new__(cls)
        self.forwards_first = forwards_first
        self.peer = peer
        self.id = id
        self.reaction = reaction
        self.offset = offset
        self.limit = limit
        return self


class TogglePinnedToTop(TLFunction["bool"]):
    """The TL function stories.togglePinnedToTop#0b297e9b, answered with Bool."""

    __slots__ = ("peer", "id",)

    ID = 0x0B297E9B
    QUALNAME = "functions.stories.TogglePinnedToTop"
    RESULT = "Bool"

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


class SearchPosts(TLFunction["base.stories.FoundStories"]):
    """The TL function stories.searchPosts#d1810907, answered with stories.FoundStories."""

    __slots__ = ("hashtag", "area", "peer", "offset", "limit",)

    ID = 0xD1810907
    QUALNAME = "functions.stories.SearchPosts"
    RESULT = "stories.FoundStories"

    def __init__(
        self,
        *,
        hashtag: str | None = None,
        area: base.MediaArea | None = None,
        peer: base.InputPeer | None = None,
        offset: str,
        limit: int,
    ) -> None:
        self.hashtag = hashtag
        self.area = area
        self.peer = peer
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.hashtag is not None:
            flags |= 1 << 0
        if self.area is not None:
            flags |= 1 << 1
        if self.peer is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.hashtag is not None:
            w.write_string(self.hashtag)
        if self.area is not None:
            self.area.write(w)
        if self.peer is not None:
            self.peer.write(w)
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hashtag = r.read_string() if flags & (1 << 0) else None
        area = r.read_object() if flags & (1 << 1) else None
        peer = r.read_object() if flags & (1 << 2) else None
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.hashtag = hashtag
        self.area = area
        self.peer = peer
        self.offset = offset
        self.limit = limit
        return self


class CreateAlbum(TLFunction["base.StoryAlbum"]):
    """The TL function stories.createAlbum#a36396e5, answered with StoryAlbum."""

    __slots__ = ("peer", "title", "stories",)

    ID = 0xA36396E5
    QUALNAME = "functions.stories.CreateAlbum"
    RESULT = "StoryAlbum"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        title: str,
        stories: list[int],
    ) -> None:
        self.peer = peer
        self.title = title
        self.stories = stories

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.title)
        w.write_vector(self.stories, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        title = r.read_string()
        stories = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.title = title
        self.stories = stories
        return self


class UpdateAlbum(TLFunction["base.StoryAlbum"]):
    """The TL function stories.updateAlbum#5e5259b6, answered with StoryAlbum."""

    __slots__ = ("peer", "album_id", "title", "delete_stories", "add_stories", "order",)

    ID = 0x5E5259B6
    QUALNAME = "functions.stories.UpdateAlbum"
    RESULT = "StoryAlbum"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        album_id: int,
        title: str | None = None,
        delete_stories: list[int] | None = None,
        add_stories: list[int] | None = None,
        order: list[int] | None = None,
    ) -> None:
        self.peer = peer
        self.album_id = album_id
        self.title = title
        self.delete_stories = delete_stories
        self.add_stories = add_stories
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.title is not None:
            flags |= 1 << 0
        if self.delete_stories is not None:
            flags |= 1 << 1
        if self.add_stories is not None:
            flags |= 1 << 2
        if self.order is not None:
            flags |= 1 << 3
        w.write_int(flags)
        self.peer.write(w)
        w.write_int(self.album_id)
        if self.title is not None:
            w.write_string(self.title)
        if self.delete_stories is not None:
            w.write_vector(self.delete_stories, TLWriter.write_int)
        if self.add_stories is not None:
            w.write_vector(self.add_stories, TLWriter.write_int)
        if self.order is not None:
            w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        album_id = r.read_int()
        title = r.read_string() if flags & (1 << 0) else None
        delete_stories = r.read_vector(TLReader.read_int) if flags & (1 << 1) else None
        add_stories = r.read_vector(TLReader.read_int) if flags & (1 << 2) else None
        order = r.read_vector(TLReader.read_int) if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.peer = peer
        self.album_id = album_id
        self.title = title
        self.delete_stories = delete_stories
        self.add_stories = add_stories
        self.order = order
        return self


class ReorderAlbums(TLFunction["bool"]):
    """The TL function stories.reorderAlbums#8535fbd9, answered with Bool."""

    __slots__ = ("peer", "order",)

    ID = 0x8535FBD9
    QUALNAME = "functions.stories.ReorderAlbums"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        order: list[int],
    ) -> None:
        self.peer = peer
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_vector(self.order, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        order = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.peer = peer
        self.order = order
        return self


class DeleteAlbum(TLFunction["bool"]):
    """The TL function stories.deleteAlbum#8d3456d0, answered with Bool."""

    __slots__ = ("peer", "album_id",)

    ID = 0x8D3456D0
    QUALNAME = "functions.stories.DeleteAlbum"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        album_id: int,
    ) -> None:
        self.peer = peer
        self.album_id = album_id

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.album_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        album_id = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.album_id = album_id
        return self


class GetAlbums(TLFunction["base.stories.Albums"]):
    """The TL function stories.getAlbums#25b3eac7, answered with stories.Albums."""

    __slots__ = ("peer", "hash",)

    ID = 0x25B3EAC7
    QUALNAME = "functions.stories.GetAlbums"
    RESULT = "stories.Albums"

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


class GetAlbumStories(TLFunction["base.stories.Stories"]):
    """The TL function stories.getAlbumStories#ac806d61, answered with stories.Stories."""

    __slots__ = ("peer", "album_id", "offset", "limit",)

    ID = 0xAC806D61
    QUALNAME = "functions.stories.GetAlbumStories"
    RESULT = "stories.Stories"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        album_id: int,
        offset: int,
        limit: int,
    ) -> None:
        self.peer = peer
        self.album_id = album_id
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_int(self.album_id)
        w.write_int(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        album_id = r.read_int()
        offset = r.read_int()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.peer = peer
        self.album_id = album_id
        self.offset = offset
        self.limit = limit
        return self


class StartLive(TLFunction["base.Updates"]):
    """The TL function stories.startLive#d069ccde, answered with Updates."""

    __slots__ = ("pinned", "noforwards", "rtmp_stream", "peer", "caption", "entities", "privacy_rules", "random_id", "messages_enabled", "send_paid_messages_stars",)

    ID = 0xD069CCDE
    QUALNAME = "functions.stories.StartLive"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        pinned: bool = False,
        noforwards: bool = False,
        rtmp_stream: bool = False,
        peer: base.InputPeer,
        caption: str | None = None,
        entities: list[base.MessageEntity] | None = None,
        privacy_rules: list[base.InputPrivacyRule],
        random_id: int,
        messages_enabled: bool | None = None,
        send_paid_messages_stars: int | None = None,
    ) -> None:
        self.pinned = pinned
        self.noforwards = noforwards
        self.rtmp_stream = rtmp_stream
        self.peer = peer
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.random_id = random_id
        self.messages_enabled = messages_enabled
        self.send_paid_messages_stars = send_paid_messages_stars

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.pinned:
            flags |= 1 << 2
        if self.noforwards:
            flags |= 1 << 4
        if self.rtmp_stream:
            flags |= 1 << 5
        if self.caption is not None:
            flags |= 1 << 0
        if self.entities is not None:
            flags |= 1 << 1
        if self.messages_enabled is not None:
            flags |= 1 << 6
        if self.send_paid_messages_stars is not None:
            flags |= 1 << 7
        w.write_int(flags)
        self.peer.write(w)
        if self.caption is not None:
            w.write_string(self.caption)
        if self.entities is not None:
            w.write_vector(self.entities)
        w.write_vector(self.privacy_rules)
        w.write_long(self.random_id)
        if self.messages_enabled is not None:
            w.write_bool(self.messages_enabled)
        if self.send_paid_messages_stars is not None:
            w.write_long(self.send_paid_messages_stars)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        pinned = bool(flags & (1 << 2))
        noforwards = bool(flags & (1 << 4))
        rtmp_stream = bool(flags & (1 << 5))
        peer = r.read_object()
        caption = r.read_string() if flags & (1 << 0) else None
        entities = r.read_vector() if flags & (1 << 1) else None
        privacy_rules = r.read_vector()
        random_id = r.read_long()
        messages_enabled = r.read_bool() if flags & (1 << 6) else None
        send_paid_messages_stars = r.read_long() if flags & (1 << 7) else None
        self = cls.__new__(cls)
        self.pinned = pinned
        self.noforwards = noforwards
        self.rtmp_stream = rtmp_stream
        self.peer = peer
        self.caption = caption
        self.entities = entities
        self.privacy_rules = privacy_rules
        self.random_id = random_id
        self.messages_enabled = messages_enabled
        self.send_paid_messages_stars = send_paid_messages_stars
        return self
