# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sunnygram, an async MTProto client library for Telegram user accounts.

The short version:

    from sunnygram import Client, filters

    app = Client("my.session", api_id=API_ID, api_hash=API_HASH)

    @app.on_message(filters.private & filters.text)
    async def echo(client, message):
        await message.reply(message.text)

    app.run()

Everything under the client is reachable on its own, and ARCHITECTURE.md is the
map: ten layers from the TCP framing up, each knowing only the one below it.

The names below are fetched when they are first asked for instead of at import.
Reaching the client means loading the generated TL layer, and a program that
only wants the codec or the session file should not pay for that by importing
this package (rule P7).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import SunnygramError
from .tl import TLObject, set_constructor_resolver

__version__ = "1.0.0"

__all__ = [
    "WHEN_ONLINE",
    "AdminRights",
    "Blocked",
    "Button",
    "CallbackQuery",
    "Chat",
    "ChosenResult",
    "Client",
    "Conversation",
    "DeletedMessages",
    "Dialog",
    "Event",
    "Folder",
    "ImportedSession",
    "InlineQuery",
    "InlineResult",
    "JoinRequest",
    "Kind",
    "Member",
    "MemberStatus",
    "MemberUpdate",
    "MemoryStorage",
    "Message",
    "Permissions",
    "Poll",
    "PollAnswer",
    "PollVote",
    "PreCheckoutQuery",
    "Price",
    "Proxy",
    "ReactionUpdate",
    "SQLiteStorage",
    "ShippingQuery",
    "SuccessfulPayment",
    "Status",
    "Story",
    "StopPropagation",
    "Stopped",
    "SunnygramError",
    "Typing",
    "User",
    "adopt_session",
    "file_ref",
    "filters",
    "force_reply",
    "keyboard",
    "loop",
    "plugins",
    "read_file_id",
    "read_session",
    "remove_keyboard",
    "__version__",
]

if TYPE_CHECKING:
    from . import filters as filters
    from . import loop as loop
    from . import plugins as plugins
    from .client import Client as Client
    from .conversation import Conversation as Conversation
    from .dispatcher import Kind as Kind
    from .dispatcher import StopPropagation as StopPropagation
    from .files import file_ref as file_ref
    from .migrate import ImportedSession as ImportedSession
    from .migrate import adopt_session as adopt_session
    from .migrate import read_file_id as read_file_id
    from .migrate import read_session as read_session
    from .methods import WHEN_ONLINE as WHEN_ONLINE
    from .storage import MemoryStorage as MemoryStorage
    from .storage import SQLiteStorage as SQLiteStorage
    from .transport import Proxy as Proxy
    from .types import AdminRights as AdminRights
    from .types import Blocked as Blocked
    from .types import Button as Button
    from .types import CallbackQuery as CallbackQuery
    from .types import Chat as Chat
    from .types import Folder as Folder
    from .types import ChosenResult as ChosenResult
    from .types import DeletedMessages as DeletedMessages
    from .types import InlineQuery as InlineQuery
    from .types import InlineResult as InlineResult
    from .types import JoinRequest as JoinRequest
    from .types import Member as Member
    from .types import MemberStatus as MemberStatus
    from .types import MemberUpdate as MemberUpdate
    from .types import Message as Message
    from .types import Permissions as Permissions
    from .types import Poll as Poll
    from .types import PollAnswer as PollAnswer
    from .types import PollVote as PollVote
    from .types import ReactionUpdate as ReactionUpdate
    from .types import PreCheckoutQuery as PreCheckoutQuery
    from .types import Price as Price
    from .types import ShippingQuery as ShippingQuery
    from .types import SuccessfulPayment as SuccessfulPayment
    from .types import Status as Status
    from .types import Story as Story
    from .types import Stopped as Stopped
    from .types import Typing as Typing
    from .types import User as User
    from .types import force_reply as force_reply
    from .types import keyboard as keyboard
    from .types import remove_keyboard as remove_keyboard

_LAZY = {
    "WHEN_ONLINE": ("sunnygram.methods", "WHEN_ONLINE"),
    "AdminRights": ("sunnygram.types", "AdminRights"),
    "Blocked": ("sunnygram.types", "Blocked"),
    "Button": ("sunnygram.types", "Button"),
    "CallbackQuery": ("sunnygram.types", "CallbackQuery"),
    "Chat": ("sunnygram.types", "Chat"),
    "ChosenResult": ("sunnygram.types", "ChosenResult"),
    "Client": ("sunnygram.client", "Client"),
    "Conversation": ("sunnygram.conversation", "Conversation"),
    "DeletedMessages": ("sunnygram.types", "DeletedMessages"),
    "Dialog": ("sunnygram.types", "Dialog"),
    "Event": ("sunnygram.updates", "Event"),
    "Folder": ("sunnygram.types", "Folder"),
    "ImportedSession": ("sunnygram.migrate", "ImportedSession"),
    "InlineQuery": ("sunnygram.types", "InlineQuery"),
    "InlineResult": ("sunnygram.types", "InlineResult"),
    "JoinRequest": ("sunnygram.types", "JoinRequest"),
    "Kind": ("sunnygram.dispatcher", "Kind"),
    "Member": ("sunnygram.types", "Member"),
    "MemberStatus": ("sunnygram.types", "MemberStatus"),
    "MemberUpdate": ("sunnygram.types", "MemberUpdate"),
    "MemoryStorage": ("sunnygram.storage", "MemoryStorage"),
    "Message": ("sunnygram.types", "Message"),
    "Permissions": ("sunnygram.types", "Permissions"),
    "Poll": ("sunnygram.types", "Poll"),
    "PollAnswer": ("sunnygram.types", "PollAnswer"),
    "PollVote": ("sunnygram.types", "PollVote"),
    "Proxy": ("sunnygram.transport", "Proxy"),
    "ReactionUpdate": ("sunnygram.types", "ReactionUpdate"),
    "SQLiteStorage": ("sunnygram.storage", "SQLiteStorage"),
    "PreCheckoutQuery": ("sunnygram.types", "PreCheckoutQuery"),
    "Price": ("sunnygram.types", "Price"),
    "ShippingQuery": ("sunnygram.types", "ShippingQuery"),
    "SuccessfulPayment": ("sunnygram.types", "SuccessfulPayment"),
    "Status": ("sunnygram.types", "Status"),
    "Story": ("sunnygram.types", "Story"),
    "StopPropagation": ("sunnygram.dispatcher", "StopPropagation"),
    "Stopped": ("sunnygram.types", "Stopped"),
    "Typing": ("sunnygram.types", "Typing"),
    "User": ("sunnygram.types", "User"),
    "adopt_session": ("sunnygram.migrate", "adopt_session"),
    "file_ref": ("sunnygram.files", "file_ref"),
    "filters": ("sunnygram.filters", None),
    "force_reply": ("sunnygram.types", "force_reply"),
    "keyboard": ("sunnygram.types", "keyboard"),
    "loop": ("sunnygram.loop", None),
    "plugins": ("sunnygram.plugins", None),
    "read_file_id": ("sunnygram.migrate", "read_file_id"),
    "read_session": ("sunnygram.migrate", "read_session"),
    "remove_keyboard": ("sunnygram.types", "remove_keyboard"),
}


def __getattr__(name: str) -> Any:
    from importlib import import_module

    found = _LAZY.get(name)
    if found is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attribute = found
    value: Any = import_module(module)
    if attribute is not None:
        value = getattr(value, attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    # PEP 562 says a module with __getattr__ should have a __dir__ to match,
    # and without one the lazy names are invisible: dir() and a REPL's tab
    # completion both see only what has already been imported, which on a fresh
    # interpreter is almost nothing. Returning the names instead of resolving
    # them keeps rule P7 intact, since nothing is imported to answer this.
    return sorted(set(globals()) | set(__all__))


def _resolve_constructor(constructor_id: int) -> type[TLObject] | None:
    # Imported inside the call, not at module scope: the constructor table and
    # the module it points at are only loaded once something actually arrives
    # off the wire, so importing sunnygram stays cheap (rule P7).
    from .raw.all import find

    return find(constructor_id)


set_constructor_resolver(_resolve_constructor)
