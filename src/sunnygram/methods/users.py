# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""People: looking them up, and the few things an account does about them.

Small module on purpose. Most of what there is to know about someone arrives
attached to something else, a message or a dialog or a member list, and the
peer cache has already learned what it needs from it. What is left is the
handful of calls that ask directly.
"""

from __future__ import annotations

from typing import Any

from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import functions, types

__all__ = [
    "block_user",
    "get_contacts",
    "unblock_user",
    "update_profile",
    "user_info",
]


async def user_info(invoker: Invoker, peer: Target) -> Any:
    """Everything about one person, including what a message never carries.

    The full form is where the bio, the common chats and the blocked flag are.
    A user off a message has none of them, which is not a gap in the wrapping:
    Telegram does not send them until they are asked for.
    """
    return await invoker.invoke(
        functions.users.GetFullUser(id=as_user(await resolve(invoker, peer)))
    )


async def get_contacts(invoker: Invoker) -> Any:
    """The account's contact list.

    Not paged, because Telegram answers this one whole. The hash is how a
    client that already has the list says so and gets told nothing changed;
    zero asks for all of it.
    """
    return await invoker.invoke(functions.contacts.GetContacts(hash=0))


async def block_user(invoker: Invoker, peer: Target) -> bool:
    """Block someone, so they cannot write to this account."""
    answer = await invoker.invoke(
        functions.contacts.Block(id=await resolve(invoker, peer))
    )
    return bool(answer)


async def unblock_user(invoker: Invoker, peer: Target) -> bool:
    """Undo that."""
    answer = await invoker.invoke(
        functions.contacts.Unblock(id=await resolve(invoker, peer))
    )
    return bool(answer)


async def update_profile(
    invoker: Invoker,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    about: str | None = None,
) -> types.User:
    """Change this account's own name or bio.

    Only what is named is changed: leaving an argument out leaves that field
    alone, instead of clearing it. Clearing one is passing an empty string,
    which is the distinction None is carrying here.
    """
    answer = await invoker.invoke(
        functions.account.UpdateProfile(
            first_name=first_name, last_name=last_name, about=about
        )
    )
    if not isinstance(answer, types.User):
        raise TypeError(f"updateProfile answered with {type(answer).__name__}")
    return answer
