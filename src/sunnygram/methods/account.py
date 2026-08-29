# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Looking after the account itself, instead of talking to anybody with it.

The sessions, the second factor, the privacy settings and the username. None of
it is interesting to a program that only wants to answer messages, and all of it
matters to a program that is going to run unattended on someone's account: a
userbot that cannot list its own sessions cannot notice that it has been signed
in to from somewhere else.

The password calls are the ones with real weight. Changing a second factor means
proving the current one and computing the new one, and neither the old password
nor the new one leaves this machine: what goes out is a proof of one and a hash
of the other. Both of those are slow on purpose, so both happen off the event
loop.
"""

from __future__ import annotations

import asyncio
from typing import Any

from ..crypto.srp import SRPParameters, password_hash, srp_proof
from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import base, functions, types

__all__ = [
    "PRIVACY",
    "account_ttl",
    "check_username",
    "current_password",
    "password_check",
    "password_proof",
    "privacy",
    "remove_password",
    "sessions",
    "set_account_ttl",
    "set_password",
    "set_privacy",
    "set_username",
    "terminate_other_sessions",
    "terminate_session",
]

# The settings Telegram lets an account restrict, by a name worth typing. The
# constructors are empty markers, so this is the whole of the mapping.
PRIVACY = {
    "last_seen": types.InputPrivacyKeyStatusTimestamp,
    "invites": types.InputPrivacyKeyChatInvite,
    "calls": types.InputPrivacyKeyPhoneCall,
    "call_p2p": types.InputPrivacyKeyPhoneP2P,
    "forwards": types.InputPrivacyKeyForwards,
    "profile_photo": types.InputPrivacyKeyProfilePhoto,
    "phone_number": types.InputPrivacyKeyPhoneNumber,
    "found_by_phone": types.InputPrivacyKeyAddedByPhone,
    "voice_messages": types.InputPrivacyKeyVoiceMessages,
    "about": types.InputPrivacyKeyAbout,
    "birthday": types.InputPrivacyKeyBirthday,
}

# What a rule can say, in the same spirit. "contacts" and "no one" are the two
# anybody reaches for; the rest are here because leaving them out would mean
# dropping to raw for an ordinary setting.
_RULES = {
    "everybody": types.InputPrivacyValueAllowAll,
    "contacts": types.InputPrivacyValueAllowContacts,
    "close_friends": types.InputPrivacyValueAllowCloseFriends,
    "premium": types.InputPrivacyValueAllowPremium,
    "bots": types.InputPrivacyValueAllowBots,
    "nobody": types.InputPrivacyValueDisallowAll,
    "not_contacts": types.InputPrivacyValueDisallowContacts,
    "not_bots": types.InputPrivacyValueDisallowBots,
}


async def sessions(invoker: Invoker) -> Any:
    """Every place this account is signed in, this one included.

    Worth checking on a schedule for a program that runs unattended. The
    current session is the one with its own flag set, and it is the one call
    that cannot be terminated by hash.
    """
    return await invoker.invoke(functions.account.GetAuthorizations())


async def terminate_session(invoker: Invoker, hash: int) -> bool:
    """Sign one other session out, by the hash the listing gave it.

    The current session has a hash of zero and Telegram refuses to end it this
    way, which is what log_out is for.
    """
    if not hash:
        raise SunnygramError(
            "the current session cannot be ended by hash; log out instead"
        )
    return bool(
        await invoker.invoke(functions.account.ResetAuthorization(hash=hash))
    )


async def terminate_other_sessions(invoker: Invoker) -> bool:
    """Sign out everywhere but here, all at once.

    Telegram will not let anything signed in within the last day be reached
    this way, so a session made minutes ago survives it.
    """
    return bool(await invoker.invoke(functions.auth.ResetAuthorizations()))


async def current_password(invoker: Invoker) -> types.account.Password:
    """The state of the second factor: whether there is one, and its salts."""
    found = await invoker.invoke(functions.account.GetPassword())
    if not isinstance(found, types.account.Password):
        raise SunnygramError(f"expected a password, got {type(found).__name__}")
    return found


async def set_password(
    invoker: Invoker,
    new: str,
    *,
    current: str = "",
    hint: str = "",
    email: str = "",
) -> Any:
    """Set the account's second factor, or change one that is already there.

    Nothing about either password is sent. The current one goes out as an SRP
    proof and the new one as a hash the server cannot reverse, which is what
    lets it check a password it has never seen.

    A recovery email is worth setting and is Telegram's only way back in: an
    account whose second factor is forgotten and has no email attached waits a
    week and loses everything on it.
    """
    if not new:
        raise ValueError("use remove_password to take the second factor off")
    state = await current_password(invoker)
    algorithm = _new_algorithm(state)

    hashed = await asyncio.to_thread(
        password_hash, new, algorithm.salt1, algorithm.salt2
    )
    return await invoker.invoke(
        functions.account.UpdatePasswordSettings(
            password=await _prove(state, current),
            new_settings=types.account.PasswordInputSettings(
                new_algo=algorithm,
                new_password_hash=_verifier(algorithm, hashed),
                hint=hint,
                email=email or None,
            ),
        )
    )


async def remove_password(invoker: Invoker, current: str) -> Any:
    """Take the second factor off, which needs the current one to do."""
    state = await current_password(invoker)
    return await invoker.invoke(
        functions.account.UpdatePasswordSettings(
            password=await _prove(state, current),
            new_settings=types.account.PasswordInputSettings(
                new_algo=types.PasswordKdfAlgoUnknown(),
                new_password_hash=b"",
                hint="",
            ),
        )
    )


async def password_check(invoker: Invoker, password: str) -> bool:
    """Whether a password is the account's, without changing anything.

    Useful before doing something a program should not do on a guess. It costs
    a real SRP round trip, so it is not something to call in a loop, and
    Telegram counts wrong answers.
    """
    state = await current_password(invoker)
    if not state.has_password:
        return False
    try:
        await invoker.invoke(
            functions.account.GetPasswordSettings(
                password=await _prove(state, password)
            )
        )
    except SunnygramError:
        return False
    return True


async def privacy(invoker: Invoker, setting: str) -> Any:
    """What one privacy setting currently says."""
    return await invoker.invoke(
        functions.account.GetPrivacy(key=_privacy_key(setting)())
    )


async def set_privacy(
    invoker: Invoker,
    setting: str,
    allow: str = "contacts",
    *,
    except_users: list[Target] | None = None,
) -> Any:
    """Change one privacy setting, and optionally carve people out of it.

    The rules are read in order and the exceptions go first, which is why they
    are a separate argument instead of something to assemble: a list built the
    other way round quietly means the opposite of what it looks like.
    """
    rules: list[base.InputPrivacyRule] = []
    if except_users:
        excluded = [as_user(await resolve(invoker, one)) for one in except_users]
        rules.append(
            types.InputPrivacyValueDisallowUsers(users=excluded)
            if allow in ("everybody", "contacts", "close_friends", "premium", "bots")
            else types.InputPrivacyValueAllowUsers(users=excluded)
        )
    rules.append(_privacy_rule(allow)())

    return await invoker.invoke(
        functions.account.SetPrivacy(key=_privacy_key(setting)(), rules=rules)
    )


async def set_username(invoker: Invoker, username: str) -> Any:
    """Claim a username, or give the current one up by passing nothing."""
    return await invoker.invoke(
        functions.account.UpdateUsername(username=username.lstrip("@"))
    )


async def check_username(invoker: Invoker, username: str) -> bool:
    """Whether a username can be claimed, without claiming it."""
    return bool(
        await invoker.invoke(
            functions.account.CheckUsername(username=username.lstrip("@"))
        )
    )


async def account_ttl(invoker: Invoker) -> int:
    """How many days of not signing in before Telegram deletes this account."""
    found = await invoker.invoke(functions.account.GetAccountTTL())
    return int(getattr(found, "days", 0))


async def set_account_ttl(invoker: Invoker, days: int) -> bool:
    """Change that. Telegram takes a month at the least and a year at the most."""
    return bool(
        await invoker.invoke(
            functions.account.SetAccountTTL(
                ttl=types.AccountDaysTTL(days=days)
            )
        )
    )


def _privacy_key(setting: str) -> Any:
    found = PRIVACY.get(setting)
    if found is None:
        raise ValueError(
            f"{setting!r} is not a privacy setting; there is "
            + ", ".join(sorted(PRIVACY))
        )
    return found


def _privacy_rule(allow: str) -> Any:
    found = _RULES.get(allow)
    if found is None:
        raise ValueError(
            f"{allow!r} is not something a privacy rule can say; there is "
            + ", ".join(sorted(_RULES))
        )
    return found


def _new_algorithm(
    state: types.account.Password,
) -> types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow:
    """The scheme the server wants a new password computed under.

    Sent by the server rather than chosen here, and it comes with fresh salt
    which is exactly why it cannot be assumed: reusing the salts of the old
    password would leave the new one as guessable as the old one was.
    """
    algorithm = state.new_algo
    if not isinstance(
        algorithm,
        types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow,
    ):
        raise SunnygramError(
            "the server asked for a password algorithm this build does not "
            f"know: {type(algorithm).__name__}"
        )
    return algorithm


def _verifier(
    algorithm: types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow,
    hashed: bytes,
) -> bytes:
    """g raised to the password, which the server stores instead of it.

    The point of the whole exercise: from this the server can check a password
    and cannot work out what it is.
    """
    return pow(
        algorithm.g,
        int.from_bytes(hashed, "big"),
        int.from_bytes(algorithm.p, "big"),
    ).to_bytes(len(algorithm.p), "big")


async def password_proof(invoker: Invoker, password: str) -> base.InputCheckPasswordSRP:
    """Prove a password to the server for a call that demands one.

    A handful of calls outside this module will not proceed without the account
    password, withdrawing money being the obvious one, and they want the proof
    rather than the password. This fetches what the server wants proved against
    and answers with the proof, so nothing else has to know that a second factor
    is an SRP exchange rather than a string.
    """
    state = await invoker.invoke(functions.account.GetPassword())
    if not isinstance(state, types.account.Password):
        raise SunnygramError(
            f"expected the password settings, got {type(state).__name__}"
        )
    return await _prove(state, password)


async def _prove(state: types.account.Password, password: str) -> base.InputCheckPasswordSRP:
    """Prove the current password, or say plainly that there is not one."""
    if not state.has_password:
        return types.InputCheckPasswordEmpty()
    if not password:
        raise SunnygramError(
            "this account already has a second factor, so the current one is "
            "needed to change it"
        )
    if state.srp_B is None or state.srp_id is None:
        raise SunnygramError("the server did not send anything to prove against")

    algorithm = state.current_algo
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
        state.srp_B,
    )
    return types.InputCheckPasswordSRP(
        srp_id=state.srp_id, A=proof.a, M1=proof.m1
    )
