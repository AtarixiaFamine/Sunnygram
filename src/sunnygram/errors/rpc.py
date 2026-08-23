# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""What a server says when it refuses a call.

An rpc_error is a number and a string, and the string is where the detail is:
FLOOD_WAIT_42 means wait forty-two seconds, PHONE_MIGRATE_4 means ask
datacenter four instead. Those numbers are worth having as attributes rather
than something every caller has to pick out of a message, so the ones that
carry a value get their own class.

This module holds the roots: one class per status code, and the handful of
named errors carrying behavior a table cannot express. The other eight hundred
are generated from Telegram's own error table into generated.py and hang off
these. The table is reached only when a call has actually failed, which is what
keeps importing this module from loading it (rule P7).
"""

from __future__ import annotations

from .base import SunnygramError

__all__ = [
    "AuthTokenExpired",
    "AuthTokenInvalid",
    "BadRequest",
    "FileMigrate",
    "Flood",
    "FloodWait",
    "Forbidden",
    "InternalError",
    "Migrate",
    "NetworkMigrate",
    "NotAcceptable",
    "NotFound",
    "PasswordHashInvalid",
    "PhoneCodeExpired",
    "PhoneCodeInvalid",
    "PhoneMigrate",
    "PhoneNumberInvalid",
    "RPCError",
    "SessionPasswordNeeded",
    "SlowmodeWait",
    "StatsMigrate",
    "TakeoutInitDelay",
    "Timeout",
    "Unauthorized",
    "UserMigrate",
    "rpc_error",
]


class RPCError(SunnygramError):
    """A call reached the server and came back refused."""

    def __init__(
        self,
        code: int,
        message: str,
        *,
        method: str | None = None,
        value: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.method = method
        self.value = value
        where = f" from {method}" if method else ""
        super().__init__(f"[{code}] {message}{where}")


class BadRequest(RPCError):
    """400, the call itself was wrong."""


class Unauthorized(RPCError):
    """401, this key is not signed in."""


class Forbidden(RPCError):
    """403, signed in but not allowed."""


class NotFound(RPCError):
    """404, no such thing."""


class NotAcceptable(RPCError):
    """406, the call was understood and the client is expected to know why.

    Telegram answers this where showing the message to someone would be
    worse than saying nothing, so a client is meant to handle it quietly
    instead of put it on screen.
    """


class InternalError(RPCError):
    """500 or 503, the server's problem. Worth retrying."""


class Timeout(RPCError):
    """The server gave up waiting on itself. Worth retrying."""


class Flood(RPCError):
    """420, too much of something. Slow down."""


class FloodWait(Flood):
    """Too many calls. Wait and try again."""

    @property
    def seconds(self) -> int:
        return self.value or 0


class SlowmodeWait(Flood):
    """This chat has slow mode on, and it is not our turn yet."""

    @property
    def seconds(self) -> int:
        return self.value or 0


class TakeoutInitDelay(Flood):
    """A data export was asked for and has to be approved first."""

    @property
    def seconds(self) -> int:
        return self.value or 0


class Migrate(RPCError):
    """The wrong datacenter was asked. The right one is in dc_id."""

    @property
    def dc_id(self) -> int:
        return self.value or 0


class PhoneMigrate(Migrate):
    """This phone number lives on another datacenter."""


class NetworkMigrate(Migrate):
    """This connection should move to another datacenter."""


class UserMigrate(Migrate):
    """This user lives on another datacenter."""


class FileMigrate(Migrate):
    """This file lives on another datacenter."""


class StatsMigrate(Migrate):
    """These statistics live on another datacenter."""


class SessionPasswordNeeded(Unauthorized):
    """The code was right and there is a second factor to get past."""


class PhoneCodeInvalid(BadRequest):
    """That is not the code that was sent."""


class PhoneCodeExpired(BadRequest):
    """The code was right once. Ask for another."""


class PhoneNumberInvalid(BadRequest):
    """That is not a phone number Telegram will accept."""


class PasswordHashInvalid(BadRequest):
    """The second factor did not check out, so the password was wrong."""


class AuthTokenExpired(BadRequest):
    """The login token timed out. Show a fresh one."""


class AuthTokenInvalid(BadRequest):
    """The login token is not one this account can accept."""


_BY_CODE: dict[int, type[RPCError]] = {
    303: Migrate,
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    406: NotAcceptable,
    420: Flood,
    500: InternalError,
    503: InternalError,
    -503: Timeout,
}


def _known(message: str) -> tuple[type[RPCError] | None, int | None]:
    """The class Telegram's table gives this message, and the value in it.

    Imported here rather than at the top of the module: the table is eight
    hundred classes and nothing needs it until a call comes back refused, so a
    program that never sees an error never loads it (rule P7).
    """
    from .generated import BY_NAME, BY_PATTERN

    exact = BY_NAME.get(message)
    if exact is not None:
        return exact, None
    for pattern, kind in BY_PATTERN:
        found = pattern.match(message)
        if found is not None:
            return kind, int(found[1])
    return None, None


def rpc_error(code: int, message: str, *, method: str | None = None) -> RPCError:
    """Build the most specific error that fits what the server said.

    An error the table has never heard of, which is what an error added since
    the last refresh looks like, comes back as its status code and keeps its
    message. Nothing is guessed from the shape of the name: a message merely
    ending in digits is not a message carrying a number.
    """
    kind, value = _known(message)
    if kind is not None:
        return kind(code, message, method=method, value=value)
    return _BY_CODE.get(code, RPCError)(code, message, method=method)
