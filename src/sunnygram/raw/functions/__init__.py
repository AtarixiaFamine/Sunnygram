# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The generated TL functions.

A name in the root namespace is reachable straight from here, and a
namespace is reachable as an attribute, so raw.types.Message and
raw.types.messages.Messages both work. Either one imports only the
module it needs.

The mtproto attribute is not a TL namespace but the service schema,
which is kept apart so that speaking the protocol does not mean loading
the API.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    "account",
    "aicompose",
    "auth",
    "bots",
    "channels",
    "chatlists",
    "communities",
    "contacts",
    "ephemeral",
    "folders",
    "fragment",
    "help",
    "langpack",
    "messages",
    "mtproto",
    "payments",
    "phone",
    "photos",
    "premium",
    "smsjobs",
    "stats",
    "stickers",
    "stories",
    "updates",
    "upload",
    "users",
    "InitConnection",
    "InvokeAfterMsg",
    "InvokeAfterMsgs",
    "InvokeWithApnsSecret",
    "InvokeWithBusinessConnection",
    "InvokeWithGooglePlayIntegrity",
    "InvokeWithLayer",
    "InvokeWithMessagesRange",
    "InvokeWithReCaptcha",
    "InvokeWithTakeout",
    "InvokeWithoutUpdates",
]

if TYPE_CHECKING:
    from . import account as account
    from . import aicompose as aicompose
    from . import auth as auth
    from . import bots as bots
    from . import channels as channels
    from . import chatlists as chatlists
    from . import communities as communities
    from . import contacts as contacts
    from . import ephemeral as ephemeral
    from . import folders as folders
    from . import fragment as fragment
    from . import help as help
    from . import langpack as langpack
    from . import messages as messages
    from . import mtproto as mtproto
    from . import payments as payments
    from . import phone as phone
    from . import photos as photos
    from . import premium as premium
    from . import smsjobs as smsjobs
    from . import stats as stats
    from . import stickers as stickers
    from . import stories as stories
    from . import updates as updates
    from . import upload as upload
    from . import users as users
    from ._root import InitConnection as InitConnection
    from ._root import InvokeAfterMsg as InvokeAfterMsg
    from ._root import InvokeAfterMsgs as InvokeAfterMsgs
    from ._root import InvokeWithApnsSecret as InvokeWithApnsSecret
    from ._root import InvokeWithBusinessConnection as InvokeWithBusinessConnection
    from ._root import InvokeWithGooglePlayIntegrity as InvokeWithGooglePlayIntegrity
    from ._root import InvokeWithLayer as InvokeWithLayer
    from ._root import InvokeWithMessagesRange as InvokeWithMessagesRange
    from ._root import InvokeWithReCaptcha as InvokeWithReCaptcha
    from ._root import InvokeWithTakeout as InvokeWithTakeout
    from ._root import InvokeWithoutUpdates as InvokeWithoutUpdates
else:
    _NAMESPACES = frozenset({'account', 'aicompose', 'auth', 'bots', 'channels', 'chatlists', 'communities', 'contacts', 'ephemeral', 'folders', 'fragment', 'help', 'langpack', 'messages', 'mtproto', 'payments', 'phone', 'photos', 'premium', 'smsjobs', 'stats', 'stickers', 'stories', 'updates', 'upload', 'users'})
    _EXPORTED = frozenset(__all__)

    def __getattr__(name: str) -> Any:
        if name in _NAMESPACES:
            value: Any = import_module(f".{name}", __name__)
        elif name in _EXPORTED:
            value = getattr(import_module("._root", __name__), name)
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            )
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        # PEP 562 pairs __getattr__ with a __dir__. Without one, dir()
        # and a REPL's tab completion see only what has already been
        # imported, which on a fresh interpreter is nothing, and this
        # is the layer docs/raw-api.md sends people to. Naming the
        # names imports none of them, so rule P7 is untouched.
        return sorted(set(globals()) | _EXPORTED | _NAMESPACES)
