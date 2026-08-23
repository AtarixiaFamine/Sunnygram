# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""What someone may do in a chat, said the way round people think about it.

Telegram spells these two ways and only one of them reads naturally. An admin's
powers are a list of things they *can* do, which is fine. A member's permissions
arrive as ChatBannedRights, which is a list of things they *cannot* do, so
allowing someone to send photos means setting send_photos to false. Reading
that wrong is easy, and reading it wrong silences a chat.

So both of these are positive. True means allowed, everywhere, and the flipping
happens once, here, on the way to the wire. There is a cost to that: a caller
who reads the raw ChatBannedRights back off a chat sees the other convention, so
from_raw is provided for going the other way and is what the library uses
whenever it hands one of these back.

Neither has a mutable form. A permission set is passed to a call and then
belongs to the chat instead of to the program, and letting someone hold one
and change it later would only invite the change to be forgotten.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Any

from ..raw import types

__all__ = ["AdminRights", "Permissions"]


@dataclass(frozen=True, slots=True)
class AdminRights:
    """What an administrator is allowed to do.

    Everything is off by default, so promoting someone without saying what
    they may do gives them a title and no powers, which is the safe way round.
    Use the presets for the ordinary cases.
    """

    change_info: bool = False
    post_messages: bool = False
    edit_messages: bool = False
    delete_messages: bool = False
    ban_users: bool = False
    invite_users: bool = False
    pin_messages: bool = False
    add_admins: bool = False
    manage_call: bool = False
    manage_topics: bool = False
    post_stories: bool = False
    edit_stories: bool = False
    delete_stories: bool = False
    # Not a power. It hides who took the action, so an anonymous admin's posts
    # come from the chat rather than from them.
    anonymous: bool = False

    def __repr__(self) -> str:
        return f"AdminRights({', '.join(self.granted) or 'nothing'})"

    @property
    def granted(self) -> tuple[str, ...]:
        """The names of everything that is on, for showing someone."""
        return tuple(
            field.name for field in fields(self) if getattr(self, field.name)
        )

    @classmethod
    def everything(cls) -> AdminRights:
        """Every power there is, short of anonymity.

        Not the same as being the owner: transferring ownership is its own call
        and is deliberately not reachable from here.
        """
        return cls(
            **{
                field.name: True
                for field in fields(cls)
                if field.name != "anonymous"
            }
        )

    @classmethod
    def moderator(cls) -> AdminRights:
        """The usual set for someone keeping order: remove people and posts."""
        return cls(
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            manage_topics=True,
        )

    def with_(self, **changes: bool) -> AdminRights:
        """The same rights with a few changed, since these do not mutate."""
        return replace(self, **changes)

    def to_raw(self) -> types.ChatAdminRights:
        """The TL form, which shares this convention and needs no flipping."""
        return types.ChatAdminRights(
            **{field.name: getattr(self, field.name) for field in fields(self)}
        )

    @classmethod
    def from_raw(cls, rights: Any) -> AdminRights:
        """Read a set back off a chat or a participant."""
        return cls(
            **{
                field.name: bool(getattr(rights, field.name, False))
                for field in fields(cls)
            }
        )


@dataclass(frozen=True, slots=True)
class Permissions:
    """What an ordinary member is allowed to do.

    True is allowed. Restricting someone is passing the set with the things
    they may no longer do turned off, and the same shape sets the default for
    everybody in a chat.

    Note what Telegram does with the group of them: turning off send_messages
    turns off everything that is a way of sending a message, whatever this says
    about the rest, because the server treats it as covering them. That is the
    server's rule and it is not undone here.
    """

    view_messages: bool = True
    send_messages: bool = True
    send_media: bool = True
    send_photos: bool = True
    send_videos: bool = True
    send_roundvideos: bool = True
    send_audios: bool = True
    send_voices: bool = True
    send_docs: bool = True
    send_stickers: bool = True
    send_gifs: bool = True
    send_games: bool = True
    send_inline: bool = True
    send_polls: bool = True
    send_plain: bool = True
    embed_links: bool = True
    change_info: bool = True
    invite_users: bool = True
    pin_messages: bool = True
    manage_topics: bool = True

    def __repr__(self) -> str:
        return f"Permissions({', '.join(self.denied) or 'everything allowed'} denied)"

    @property
    def denied(self) -> tuple[str, ...]:
        """The names of everything that is off, which is what a restriction is."""
        return tuple(
            field.name for field in fields(self) if not getattr(self, field.name)
        )

    @classmethod
    def everything(cls) -> Permissions:
        """No restriction at all, which is also what lifting one looks like."""
        return cls()

    @classmethod
    def read_only(cls) -> Permissions:
        """The usual mute: silenced but still present, able to read and no more."""
        return cls(
            **{field.name: field.name == "view_messages" for field in fields(cls)}
        )

    @classmethod
    def none(cls) -> Permissions:
        """Nothing at all, not even seeing the chat, which is what a ban is."""
        return cls(**{field.name: False for field in fields(cls)})

    def with_(self, **changes: bool) -> Permissions:
        """The same permissions with a few changed, since these do not mutate."""
        return replace(self, **changes)

    def to_raw(self, *, until: int = 0) -> types.ChatBannedRights:
        """The TL form, with every flag flipped to the banned convention.

        until is when the restriction lifts, as a unix time. Zero is forever,
        which is Telegram's own spelling and not a missing value.
        """
        return types.ChatBannedRights(
            until_date=until,
            **{
                field.name: not getattr(self, field.name)
                for field in fields(self)
            },
        )

    @classmethod
    def from_raw(cls, rights: Any) -> Permissions:
        """Read a set back off a chat or a participant, flipping as it comes."""
        return cls(
            **{
                field.name: not getattr(rights, field.name, False)
                for field in fields(cls)
            }
        )
