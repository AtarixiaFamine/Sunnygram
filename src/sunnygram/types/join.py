# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Someone asking to be let into a chat.

A chat can be set up so that its invite link puts people in a queue instead of
in the chat, and then every attempt to join arrives as this. It is one of the
few updates that is genuinely a request: nothing happens until something
answers it, and until then the person sees a note saying their request is
pending.

Both answers already existed as a call. What was missing was being told the
request arrived at all, which makes an automatic doorman possible: read
the bio, check the invite link they used, let them in or turn them down.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..peers import mark_peer
from ..raw import types
from .user import User

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["JoinRequest"]


@dataclass(slots=True)
class JoinRequest:
    """One person waiting to be let into one chat."""

    chat_id: int
    user_id: int
    sender: User | None = None
    date: int = 0
    about: str = ""
    invite: Any = None
    raw: Any = None
    client: Any = None

    def __repr__(self) -> str:
        who = self.sender.username or self.user_id if self.sender else self.user_id
        return f"JoinRequest({who} wants into {self.chat_id})"

    @property
    def invite_link(self) -> str:
        """The link they used, when it was a link they could be told apart by.

        A chat with several links can tell where someone came from, which is
        the whole reason to have several. A request that came in some other way
        has nothing here instead of a made up link.
        """
        found = getattr(self.invite, "link", None)
        return found if isinstance(found, str) else ""

    async def approve(self) -> None:
        """Let them in."""
        await self._acting().approve_join_request(
            self.chat_id, self.user_id, approved=True
        )

    async def decline(self) -> None:
        """Turn them down.

        They are told, and they may ask again: this is a refusal, not a
        ban. Banning is what stops someone asking forever.
        """
        await self._acting().approve_join_request(
            self.chat_id, self.user_id, approved=False
        )

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this join request is not bound to a client, so it cannot be "
                "answered on its own"
            )
        client: Client = self.client
        return client

    @classmethod
    def from_raw(
        cls,
        update: Any,
        *,
        users: dict[int, Any] | None = None,
        client: Any = None,
    ) -> JoinRequest | None:
        """Wrap a request off the wire, with whoever came alongside it."""
        if not isinstance(update, types.UpdateBotChatInviteRequester):
            return None
        known = users or {}
        return cls(
            chat_id=mark_peer(update.peer) or 0,
            user_id=update.user_id,
            sender=User.from_raw(known.get(update.user_id)),
            date=update.date,
            about=update.about,
            invite=update.invite,
            raw=update,
            client=client,
        )
