# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Becoming someone.

An authorization key on its own is anonymous: it can ask a datacenter for its
configuration and very little else. Logging in binds that key to an account, and
from then on the key is the account, which is why what the storage holds
afterwards deserves the care it gets.

Three ways in. A phone number and the code Telegram sends to it, with a second
factor if the account has one, which is the usual path for a person. A bot
token, which is one call. And a QR code, where another logged-in client approves
this one, which is the same three-legged dance with the phone replaced by a
scan.

The steps are separate functions because a login is interactive and only the
caller knows how to ask a person for a code. log_in stitches them together for
the common case, and takes callables so it can do the asking through whatever
interface it has.

Registering a new account is deliberately not here. This library signs in
accounts that already exist; making new ones in bulk is what abuse looks like on
this protocol, and a server that asks us to sign up gets a clear refusal
pointing at an official client instead.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from base64 import urlsafe_b64encode
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from ..crypto import SRPParameters, srp_proof
from ..errors import AuthTokenExpired, SessionPasswordNeeded, SunnygramError
from ..network import Invoker
from ..raw import functions, types

__all__ = [
    "LoginToken",
    "SentCode",
    "check_password",
    "get_me",
    "log_in",
    "log_out",
    "resend_code",
    "send_code",
    "sign_in",
    "sign_in_bot",
    "sign_in_qr",
]

T = TypeVar("T")

# How often to ask whether a QR code has been scanned yet, and how long to keep
# offering one before giving up on the person at the other end.
QR_POLL = 3.0
QR_TIMEOUT = 180.0

_CODE_KINDS = {
    types.auth.SentCodeTypeApp: "app",
    types.auth.SentCodeTypeSms: "sms",
    types.auth.SentCodeTypeCall: "call",
    types.auth.SentCodeTypeFlashCall: "flash call",
    types.auth.SentCodeTypeMissedCall: "missed call",
    types.auth.SentCodeTypeEmailCode: "email",
    types.auth.SentCodeTypeFragmentSms: "fragment",
    types.auth.SentCodeTypeFirebaseSms: "sms",
    types.auth.SentCodeTypeSmsWord: "sms word",
    types.auth.SentCodeTypeSmsPhrase: "sms phrase",
}


@dataclass(frozen=True, slots=True)
class SentCode:
    """A code is on its way, and this is what signing in with it will need.

    The hash is what ties the code to the request that asked for it, so it has
    to come back with the code. kind says where the code went, which is worth
    telling the person, since a code in the Telegram app and a code in an SMS
    look for different things.
    """

    phone_number: str
    phone_code_hash: str
    kind: str
    timeout: int | None = None
    next_kind: str | None = None


@dataclass(frozen=True, slots=True)
class LoginToken:
    """A QR login waiting to be scanned."""

    token: bytes
    expires: int

    @property
    def url(self) -> str:
        """The link to put in the QR code.

        An official client that scans this is being asked to authorize us, so
        what it encodes is a credential in flight. Show it to the person logging
        in and no one else.
        """
        packed = urlsafe_b64encode(self.token).decode().rstrip("=")
        return f"tg://login?token={packed}"

    @property
    def seconds_left(self) -> float:
        return max(0.0, self.expires - time.time())


async def send_code(
    invoker: Invoker, phone_number: str, *, settings: types.CodeSettings | None = None
) -> SentCode:
    """Ask Telegram to send a login code to a phone number.

    The number may belong to another datacenter than the one we are talking to,
    in which case the server says so and the invoker moves before this returns.
    """
    phone_number = _clean(phone_number)
    sent = await invoker.invoke(
        functions.auth.SendCode(
            phone_number=phone_number,
            api_id=invoker.client.api_id,
            api_hash=_api_hash(invoker),
            settings=types.CodeSettings() if settings is None else settings,
        )
    )
    if isinstance(sent, types.auth.SentCodeSuccess):
        # Only happens when the request carried a token from a previous session,
        # which nothing here does yet. Saying so is better than pretending a
        # code is coming.
        raise SunnygramError(
            "the server signed this session in without sending a code, which "
            "this build does not ask for"
        )
    if not isinstance(sent, types.auth.SentCode):
        raise SunnygramError(f"expected a sent code, got {type(sent).__name__}")

    return SentCode(
        phone_number=phone_number,
        phone_code_hash=sent.phone_code_hash,
        kind=_CODE_KINDS.get(type(sent.type), "unknown"),
        timeout=sent.timeout,
        next_kind=None if sent.next_type is None else _CODE_KINDS.get(
            type(sent.next_type), "unknown"
        ),
    )


async def resend_code(invoker: Invoker, sent: SentCode) -> SentCode:
    """Ask for the code again, usually by another route than the first."""
    again = await invoker.invoke(
        functions.auth.ResendCode(
            phone_number=sent.phone_number, phone_code_hash=sent.phone_code_hash
        )
    )
    if not isinstance(again, types.auth.SentCode):
        raise SunnygramError(f"expected a sent code, got {type(again).__name__}")
    return SentCode(
        phone_number=sent.phone_number,
        phone_code_hash=again.phone_code_hash,
        kind=_CODE_KINDS.get(type(again.type), "unknown"),
        timeout=again.timeout,
    )


async def sign_in(invoker: Invoker, sent: SentCode, code: str) -> types.User:
    """Finish a phone login with the code that arrived.

    Raises SessionPasswordNeeded when the account has a second factor, which is
    not a failure: the code was right, and check_password is what comes next.
    """
    authorization = await invoker.invoke(
        functions.auth.SignIn(
            phone_number=sent.phone_number,
            phone_code_hash=sent.phone_code_hash,
            phone_code=code.strip(),
        )
    )
    if isinstance(authorization, types.auth.AuthorizationSignUpRequired):
        raise SunnygramError(
            "this number has no account yet. Sunnygram signs in to accounts "
            "that already exist; register in an official Telegram client first"
        )
    return await _adopt(invoker, authorization)


async def check_password(invoker: Invoker, password: str) -> types.User:
    """Get past a second factor with the account password.

    The password itself never leaves this machine. What goes out is a proof
    built from it, and building that proof is deliberately slow, so it happens
    off the event loop.
    """
    current = await invoker.invoke(functions.account.GetPassword())
    if not isinstance(current, types.account.Password):
        raise SunnygramError(f"expected a password, got {type(current).__name__}")
    algorithm = current.current_algo
    if current.srp_B is None or current.srp_id is None:
        raise SunnygramError("this account has no password set")
    if not isinstance(
        algorithm,
        types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow,
    ):
        raise SunnygramError(
            "the server asked for a password algorithm this build does not "
            f"know: {type(algorithm).__name__}"
        )

    proof = await asyncio.to_thread(
        srp_proof,
        password,
        SRPParameters(
            salt1=algorithm.salt1,
            salt2=algorithm.salt2,
            g=algorithm.g,
            p=algorithm.p,
        ),
        current.srp_B,
    )
    authorization = await invoker.invoke(
        functions.auth.CheckPassword(
            password=types.InputCheckPasswordSRP(
                srp_id=current.srp_id, A=proof.a, M1=proof.m1
            )
        )
    )
    return await _adopt(invoker, authorization)


async def sign_in_bot(invoker: Invoker, token: str) -> types.User:
    """Sign in as a bot, which needs nothing but its token."""
    authorization = await invoker.invoke(
        functions.auth.ImportBotAuthorization(
            flags=0,
            api_id=invoker.client.api_id,
            api_hash=_api_hash(invoker),
            bot_auth_token=token.strip(),
        )
    )
    return await _adopt(invoker, authorization)


async def export_login_token(invoker: Invoker) -> LoginToken | types.User:
    """Ask for one QR login token, following a migration if one is asked for.

    Comes back as a token to show, or as the user if someone scanned the
    previous one in the meantime.
    """
    exported = await invoker.invoke(
        functions.auth.ExportLoginToken(
            api_id=invoker.client.api_id,
            api_hash=_api_hash(invoker),
            except_ids=[],
        )
    )
    if isinstance(exported, types.auth.LoginTokenMigrateTo):
        # The account lives elsewhere. Move, then hand the token over there,
        # which is the only call that finishes a QR login across datacenters.
        await invoker.migrate(exported.dc_id)
        exported = await invoker.invoke(
            functions.auth.ImportLoginToken(token=exported.token)
        )
    if isinstance(exported, types.auth.LoginTokenSuccess):
        return await _adopt(invoker, exported.authorization)
    if isinstance(exported, types.auth.LoginToken):
        return LoginToken(token=exported.token, expires=exported.expires)
    raise SunnygramError(f"expected a login token, got {type(exported).__name__}")


async def sign_in_qr(
    invoker: Invoker,
    show: Callable[[LoginToken], Any],
    *,
    timeout: float = QR_TIMEOUT,
    poll: float = QR_POLL,
) -> types.User:
    """Log in by having an already-signed-in client scan a code.

    show is called with each token, and again whenever one expires and is
    replaced, so whatever is drawing the code can redraw it. Raises
    SessionPasswordNeeded if the account has a second factor, exactly as a phone
    login does, and check_password finishes it the same way.
    """
    deadline = time.monotonic() + timeout
    shown: LoginToken | None = None
    while time.monotonic() < deadline:
        if shown is None or shown.seconds_left <= 0:
            exported = await export_login_token(invoker)
            if isinstance(exported, types.User):
                return exported
            shown = exported
            await _maybe_await(show(shown))

        await asyncio.sleep(min(poll, max(0.0, deadline - time.monotonic())))
        try:
            answer = await export_login_token(invoker)
        except AuthTokenExpired:
            shown = None
            continue
        if isinstance(answer, types.User):
            return answer
        if answer.token != shown.token:
            shown = answer
            await _maybe_await(show(shown))

    raise SunnygramError("nobody scanned the login code in time")


async def get_me(invoker: Invoker) -> types.User:
    """Who this session is signed in as."""
    users = await invoker.invoke(
        functions.users.GetUsers(id=[types.InputUserSelf()])
    )
    if not users or not isinstance(users[0], types.User):
        raise SunnygramError("the server did not say who we are")
    found: types.User = users[0]
    return found


async def log_out(invoker: Invoker) -> None:
    """End this session and forget everything that was kept for it.

    The key is dead on the server the moment this returns, so keeping our copy
    would only be a credential that no longer opens anything.
    """
    try:
        await invoker.invoke(functions.auth.LogOut())
    finally:
        invoker.state.user_id = 0
        invoker.state.is_bot = False
        invoker.state.auth_keys.clear()
        await invoker.save()


async def log_in(
    invoker: Invoker,
    *,
    phone_number: str | Callable[[], Any],
    code: Callable[[SentCode], Any],
    password: Callable[[str], Any] | None = None,
    bot_token: str | None = None,
) -> types.User:
    """Sign in, asking for whatever is missing along the way.

    The callables are how this stays usable from a script, a prompt or a chat
    window without knowing which it is: each is called when the answer is needed
    and may be sync or async. password is handed the account's hint, which is
    often the only reminder the person has.

    A session that is already signed in is returned as it is, so this is safe to
    call every run.
    """
    if invoker.state.authorized:
        return await get_me(invoker)
    if bot_token is not None:
        return await sign_in_bot(invoker, bot_token)

    number = phone_number if isinstance(phone_number, str) else phone_number()
    sent = await send_code(invoker, str(await _maybe_await(number)))
    try:
        return await sign_in(invoker, sent, str(await _maybe_await(code(sent))))
    except SessionPasswordNeeded:
        if password is None:
            raise
        hint = await _password_hint(invoker)
        return await check_password(
            invoker, str(await _maybe_await(password(hint)))
        )


async def _adopt(invoker: Invoker, authorization: Any) -> types.User:
    """Take an authorization the server just granted and keep it."""
    if not isinstance(authorization, types.auth.Authorization):
        raise SunnygramError(
            f"expected an authorization, got {type(authorization).__name__}"
        )
    user = authorization.user
    if not isinstance(user, types.User):
        raise SunnygramError("the authorization does not say who it is for")

    invoker.state.user_id = user.id
    invoker.state.is_bot = bool(user.bot)
    await invoker.save()
    return user


async def _password_hint(invoker: Invoker) -> str:
    current = await invoker.invoke(functions.account.GetPassword())
    hint = getattr(current, "hint", None)
    return hint if isinstance(hint, str) else ""


async def _maybe_await(value: T | Awaitable[T]) -> T:
    """Take an answer from a callable that may or may not be async."""
    if inspect.isawaitable(value):
        awaited: T = await value
        return awaited
    return value


def _clean(phone_number: str) -> str:
    """A phone number as Telegram wants it: digits, and nothing else."""
    digits = "".join(character for character in phone_number if character.isdigit())
    if not digits:
        raise ValueError(f"{phone_number!r} has no digits in it")
    return digits


def _api_hash(invoker: Invoker) -> str:
    api_hash = invoker.client.api_hash
    if not api_hash:
        raise SunnygramError(
            "logging in needs the api_hash that came with the api_id; set it on "
            "the ClientInfo this invoker was built with"
        )
    return api_hash
