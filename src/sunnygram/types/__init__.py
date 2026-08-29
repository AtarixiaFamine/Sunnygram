# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The friendly shapes, as opposed to the ones the protocol uses.

Every one of them keeps what it was made from on a raw attribute, because the
whole surface cannot be wrapped and pretending otherwise would mean a library
that can do less than the protocol under it. The wrapper is for the common
case; raw is there for the rest.

Two of them face the other way. A Message describes what arrived; a keyboard
describes what is about to be sent, and is here instead of in methods because
it is a shape with no call attached, the same as the rest of these. An inline
result is both at once, which is why it sits beside the query it answers.
"""

from __future__ import annotations

from .buttons import (
    CALLBACK_DATA_LIMIT,
    Button,
    buttons_of,
    force_reply,
    keyboard,
    remove_keyboard,
)
from .callback import CallbackQuery
from .boost import Boost, BoostStatus
from .chat import Chat
from .dialog import Dialog
from .events import Blocked, DeletedMessages, Status, Stopped, Typing
from .folder import Folder
from .inline import ChosenResult, InlineQuery, InlineResult
from .join import JoinRequest
from .member import Member, MemberStatus, MemberUpdate
from .message import Message
from .payments import PreCheckoutQuery, Price, ShippingQuery, SuccessfulPayment
from .poll import Poll, PollAnswer, PollVote
from .reaction import ReactionUpdate
from .rights import AdminRights, Permissions
from .story import Story
from .topic import Topic
from .user import User

__all__ = [
    "CALLBACK_DATA_LIMIT",
    "AdminRights",
    "Blocked",
    "Button",
    "CallbackQuery",
    "Boost",
    "BoostStatus",
    "Chat",
    "ChosenResult",
    "DeletedMessages",
    "Dialog",
    "Folder",
    "InlineQuery",
    "InlineResult",
    "JoinRequest",
    "Member",
    "MemberStatus",
    "MemberUpdate",
    "Message",
    "Permissions",
    "Poll",
    "PollAnswer",
    "PollVote",
    "PreCheckoutQuery",
    "Price",
    "ReactionUpdate",
    "ShippingQuery",
    "Status",
    "Stopped",
    "Story",
    "SuccessfulPayment",
    "Topic",
    "Typing",
    "User",
    "buttons_of",
    "force_reply",
    "keyboard",
    "remove_keyboard",
]
