# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sunnygram's exception tree.

The names in __all__ are the roots: what can go wrong locally, and one class
per status code a server can refuse a call with. Every error Telegram
documents is reachable from here by name too, all eight hundred of them,
though those are generated instead of listed and are loaded only once
something asks for one (rule P7):

    from sunnygram.errors import FloodWait, PeerIdInvalid

Catch whichever level says what you mean. PeerIdInvalid is one mistake,
BadRequest is any of them, RPCError is any refusal at all, and SunnygramError
is everything this library raises.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import (
    BadMessage,
    DuplicateMessage,
    FileTooLarge,
    MalformedFrame,
    NoAnswer,
    PeerNotFound,
    ProxyError,
    SecurityError,
    SunnygramError,
    TLDeserializationError,
    TLError,
    TLSerializationError,
    TransportClosed,
    TransportError,
    TransportRejected,
    UnknownConstructorError,
    UploadRefused,
)
from .rpc import (
    AuthTokenExpired,
    AuthTokenInvalid,
    BadRequest,
    FileMigrate,
    Flood,
    FloodWait,
    Forbidden,
    InternalError,
    Migrate,
    NetworkMigrate,
    NotAcceptable,
    NotFound,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneMigrate,
    PhoneNumberInvalid,
    RPCError,
    SessionPasswordNeeded,
    SlowmodeWait,
    StatsMigrate,
    TakeoutInitDelay,
    Timeout,
    Unauthorized,
    UserMigrate,
    rpc_error,
)

if TYPE_CHECKING:
    # Only so a type checker knows the generated names are real. At runtime
    # they arrive through __getattr__ below, one import the first time one of
    # them is asked for and never for a program that asks for none.
    from .generated import *  # noqa: F403

__all__ = [
    "AuthTokenExpired",
    "AuthTokenInvalid",
    "BadMessage",
    "BadRequest",
    "DuplicateMessage",
    "FileMigrate",
    "FileTooLarge",
    "Flood",
    "FloodWait",
    "Forbidden",
    "InternalError",
    "MalformedFrame",
    "NoAnswer",
    "Migrate",
    "NetworkMigrate",
    "NotAcceptable",
    "NotFound",
    "PasswordHashInvalid",
    "PeerNotFound",
    "PhoneCodeExpired",
    "PhoneCodeInvalid",
    "PhoneMigrate",
    "PhoneNumberInvalid",
    "ProxyError",
    "RPCError",
    "SecurityError",
    "SessionPasswordNeeded",
    "SlowmodeWait",
    "StatsMigrate",
    "SunnygramError",
    "TLDeserializationError",
    "TLError",
    "TLSerializationError",
    "TakeoutInitDelay",
    "Timeout",
    "TransportClosed",
    "TransportError",
    "TransportRejected",
    "Unauthorized",
    "UnknownConstructorError",
    "UploadRefused",
    "UserMigrate",
    "rpc_error",
]


def __getattr__(name: str) -> Any:
    """Any of the generated errors, fetched the first time it is named.

    Reached through import_module rather than "from . import generated": the
    from-form asks this same function for the submodule while the submodule is
    still not an attribute of the package, which is a loop with no exit.
    """
    from importlib import import_module

    found = getattr(import_module(f"{__name__}.generated"), name, None)
    if found is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = found
    return found
