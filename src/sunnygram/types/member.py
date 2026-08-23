# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""One person's standing in one chat, and it changing.

Telegram says this with a different constructor per standing, and says it twice
over: a basic group has its own three and a channel has six more. A caller
almost never wants that. What they want is the question they came with, which is
either "is this person allowed to run the place" or "are they still here at all",
so both families collapse to one status here and the details hang off it.

The one piece worth knowing is that being restricted and being banned are the
same constructor. Telegram tells them apart by a flag saying whether the person
is still in the chat, and the two mean opposite things to a program: a
restricted member is present and limited, a banned one is gone.

The other half of this file is the update that says a standing changed. It
carries the standing before and the standing after, and that pair is the whole
point: Telegram never says "joined" or "was promoted", it says what they were
and what they are now, and every question a program actually has is the
difference between the two.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ..peers import mark_id
from ..raw import types
from ..storage import PeerKind
from .rights import AdminRights, Permissions

__all__ = ["Member", "MemberStatus", "MemberUpdate"]


class MemberStatus(StrEnum):
    """Where someone stands, in the six ways Telegram distinguishes."""

    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"
    RESTRICTED = "restricted"
    LEFT = "left"
    BANNED = "banned"


@dataclass(frozen=True, slots=True)
class Member:
    """Someone's standing in a chat, whichever kind of chat it is."""

    user_id: int
    status: MemberStatus
    chat_id: int = 0
    rights: AdminRights | None = None
    permissions: Permissions | None = None
    title: str = ""
    joined: int = 0
    promoted_by: int = 0
    invited_by: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        return f"Member({self.user_id}, {self.status.value})"

    @property
    def is_admin(self) -> bool:
        """Whether they may act on the chat, the creator included.

        This is the question most callers are really asking, and asking it
        directly avoids the mistake of testing for admin and forgetting that
        the creator is not one.
        """
        return self.status in (MemberStatus.CREATOR, MemberStatus.ADMIN)

    @property
    def present(self) -> bool:
        """Whether they are in the chat at all."""
        return self.status not in (MemberStatus.LEFT, MemberStatus.BANNED)

    @classmethod
    def from_raw(cls, participant: Any, *, chat_id: int = 0) -> Member:
        """Wrap whichever of the nine constructors arrived."""
        status = _status_of(participant)
        rights = None
        if status is MemberStatus.CREATOR:
            rights = AdminRights.everything()
        else:
            powers = getattr(participant, "admin_rights", None)
            if powers is not None:
                rights = AdminRights.from_raw(powers)

        restriction = getattr(participant, "banned_rights", None)
        permissions = (
            Permissions.from_raw(restriction)
            if restriction is not None
            else Permissions.everything()
        )

        return cls(
            user_id=_user_of(participant),
            status=status,
            chat_id=chat_id,
            rights=rights,
            permissions=permissions,
            title=getattr(participant, "rank", "") or "",
            joined=getattr(participant, "date", 0) or 0,
            promoted_by=getattr(participant, "promoted_by", 0) or 0,
            invited_by=getattr(participant, "inviter_id", 0) or 0,
            raw=participant,
        )


@dataclass(frozen=True, slots=True)
class MemberUpdate:
    """Someone's standing in a chat changing, from what to what.

    Both kinds of chat produce this and they are the same thing here. What
    Telegram gives is a pair, and the pair is what answers every question worth
    asking: someone with no standing before and a standing now has joined;
    someone who was an ordinary member and is now an admin has been promoted;
    someone present before and absent now has left, or has been thrown out,
    and which of those it was is whether they did it to themselves.

    Either side of the pair can be missing, and the missing one is the
    information: no standing before means they were not here, and no standing
    after means they are not here now.

    chat_id is marked the Bot API way, which is the spelling resolve takes
    back, so a greeter can answer straight into the chat. The members inside
    carry no chat id of their own, deliberately: one number for the chat, in
    one place, instead of the same chat spelled two ways in one object.
    """

    chat_id: int
    user_id: int
    actor_id: int = 0
    date: int = 0
    before: Member | None = None
    after: Member | None = None
    invite: Any = None
    via_chatlist: bool = False
    raw: Any = None

    def __repr__(self) -> str:
        return f"MemberUpdate({self.user_id} in {self.chat_id}, {self.what})"

    @property
    def what(self) -> str:
        """One word for what happened, which a log line wants.

        The words are the questions below, tried in the order that makes the
        most specific one win: being banned is also leaving, and being promoted
        while joining is still joining.
        """
        if self.joined:
            return "joined"
        if self.banned:
            return "banned"
        if self.left:
            return "left"
        if self.promoted:
            return "promoted"
        if self.demoted:
            return "demoted"
        if self.restricted:
            return "restricted"
        return "changed"

    @property
    def was_present(self) -> bool:
        """Whether they were in the chat before this."""
        return self.before is not None and self.before.present

    @property
    def is_present(self) -> bool:
        """Whether they are in the chat now."""
        return self.after is not None and self.after.present

    @property
    def joined(self) -> bool:
        """Whether this is someone arriving."""
        return self.is_present and not self.was_present

    @property
    def left(self) -> bool:
        """Whether this is someone going, by their own choice or not."""
        return self.was_present and not self.is_present

    @property
    def banned(self) -> bool:
        """Whether they were thrown out instead of merely gone."""
        return self.after is not None and self.after.status is MemberStatus.BANNED

    @property
    def restricted(self) -> bool:
        """Whether they are present and newly limited in what they may do."""
        return (
            self.after is not None
            and self.after.status is MemberStatus.RESTRICTED
            and (self.before is None or self.before.status is not MemberStatus.RESTRICTED)
        )

    @property
    def promoted(self) -> bool:
        """Whether they may now run the place and could not before."""
        return self._admin(self.after) and not self._admin(self.before)

    @property
    def demoted(self) -> bool:
        """Whether they could run the place before and may not now."""
        return self._admin(self.before) and not self._admin(self.after)

    @property
    def by_self(self) -> bool:
        """Whether they did this to themselves.

        The difference between joining and being added, and between leaving and
        being removed. Telegram says both with the same pair and only the actor
        tells them apart.
        """
        return self.actor_id == self.user_id

    @property
    def invite_link(self) -> str:
        """The link they came in through, if they came in through one.

        Worth reading on a join: a chat with several links knows which campaign
        someone arrived from, and this is where that is said.
        """
        found = getattr(self.invite, "link", None)
        return found if isinstance(found, str) else ""

    @property
    def status(self) -> MemberStatus | None:
        """Where they stand now, or nothing if they are no longer anywhere."""
        return None if self.after is None else self.after.status

    @staticmethod
    def _admin(member: Member | None) -> bool:
        return member is not None and member.is_admin

    @classmethod
    def from_raw(cls, update: Any) -> MemberUpdate | None:
        """Wrap either of the two updates that say this."""
        if isinstance(update, types.UpdateChatParticipant):
            chat_id = mark_id(update.chat_id, PeerKind.CHAT)
            via_chatlist = False
        elif isinstance(update, types.UpdateChannelParticipant):
            chat_id = mark_id(update.channel_id, PeerKind.CHANNEL)
            via_chatlist = bool(update.via_chatlist)
        else:
            return None

        return cls(
            chat_id=chat_id,
            user_id=update.user_id,
            actor_id=update.actor_id,
            date=update.date,
            before=_wrap(update.prev_participant),
            after=_wrap(update.new_participant),
            invite=update.invite,
            via_chatlist=via_chatlist,
            raw=update,
        )


def _wrap(participant: Any) -> Member | None:
    """One side of the pair, or nothing when that side is nothing."""
    return None if participant is None else Member.from_raw(participant)


def _status_of(participant: Any) -> MemberStatus:
    if isinstance(
        participant, (types.ChannelParticipantCreator, types.ChatParticipantCreator)
    ):
        return MemberStatus.CREATOR
    if isinstance(
        participant, (types.ChannelParticipantAdmin, types.ChatParticipantAdmin)
    ):
        return MemberStatus.ADMIN
    if isinstance(participant, types.ChannelParticipantLeft):
        return MemberStatus.LEFT
    if isinstance(participant, types.ChannelParticipantBanned):
        # The same constructor for both, told apart by whether they are still
        # in the chat. Restricted means present and limited; banned means gone.
        return MemberStatus.BANNED if participant.left else MemberStatus.RESTRICTED
    return MemberStatus.MEMBER


def _user_of(participant: Any) -> int:
    """Which user this is about.

    Banned and left carry a peer rather than a user id, because a channel can
    ban a channel, and the rest carry the id directly.
    """
    found = getattr(participant, "user_id", None)
    if isinstance(found, int):
        return found
    peer = getattr(participant, "peer", None)
    for field in ("user_id", "channel_id", "chat_id"):
        found = getattr(peer, field, None)
        if isinstance(found, int):
            return found
    return 0
