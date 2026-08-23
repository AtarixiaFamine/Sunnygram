# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Exporting an account's own data.

Telegram treats a bulk export differently from ordinary reading. You ask for a
takeout session, the account holder approves it in an official client, and
every call that is part of the export is wrapped so the server knows to answer
generously instead of refusing you for asking too much.

The approval is the part worth knowing about. Asking for a session when one has
not been approved is refused with TakeoutInitDelay, which carries the number of
seconds left to wait, and that wait is hours instead of the seconds a
FLOOD_WAIT means. It is deliberately not slept through anywhere in this
library: the caller has to be told, because what it is really waiting for is a
person tapping a button somewhere else.
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, Self

from ..network import Invoker
from ..raw import functions, types
from ..tl import TLFunction, TLResult

__all__ = ["Takeout", "finish_takeout", "init_takeout"]


async def init_takeout(
    invoker: Invoker,
    *,
    contacts: bool = False,
    message_users: bool = False,
    message_chats: bool = False,
    message_megagroups: bool = False,
    message_channels: bool = False,
    files: bool = False,
    file_max_size: int | None = None,
) -> int:
    """Ask for a takeout session, and return the id it was given.

    Each flag says what the export is allowed to reach. Asking for nothing is
    allowed and useless, so pick the parts wanted: the flags are separate
    because Telegram meters them separately.

    file_max_size caps how large a file the export will hand over, in bytes,
    and only means anything alongside files.

    Raises TakeoutInitDelay when the account holder has not approved this yet.
    That is not a rate limit, whatever it looks like: read its seconds, tell
    someone, and ask again later.
    """
    answer = await invoker.invoke(
        functions.account.InitTakeoutSession(
            contacts=contacts,
            message_users=message_users,
            message_chats=message_chats,
            message_megagroups=message_megagroups,
            message_channels=message_channels,
            files=files,
            file_max_size=file_max_size,
        )
    )
    if not isinstance(answer, types.account.Takeout):
        raise TypeError(f"initTakeoutSession answered with {type(answer).__name__}")
    return answer.id


async def finish_takeout(
    invoker: Invoker, takeout_id: int, *, success: bool = True
) -> bool:
    """Close a takeout session.

    success is what the account holder is shown afterwards, so an export that
    gave up halfway should say so rather than claiming it finished. The call
    goes out inside the session it is closing, which is how the server knows
    which one is meant.
    """
    return bool(
        await invoker.invoke(
            functions.InvokeWithTakeout(
                takeout_id=takeout_id,
                query=functions.account.FinishTakeoutSession(success=success),
            )
        )
    )


class Takeout:
    """A takeout session, and the calls made inside it.

    Every call goes out wrapped in invokeWithTakeout, which is the only
    difference between this and an ordinary invoker. Used as a context manager
    it closes the session on the way out, and says the export failed if it is
    leaving because something raised.
    """

    __slots__ = ("_invoker", "id", "_open")

    def __init__(self, invoker: Invoker, takeout_id: int) -> None:
        self._invoker = invoker
        self.id = takeout_id
        self._open = True

    def __repr__(self) -> str:
        return f"Takeout({self.id}, {'open' if self._open else 'closed'})"

    async def invoke(
        self, request: TLFunction[TLResult], **options: Any
    ) -> TLResult:
        """Make one call as part of this export."""
        if not self._open:
            raise RuntimeError("this takeout session has been finished")
        return await self._invoker.invoke(
            functions.InvokeWithTakeout(takeout_id=self.id, query=request), **options
        )

    async def finish(self, *, success: bool = True) -> bool:
        """Close the session. Doing it twice is not an error, just a no-op."""
        if not self._open:
            return False
        self._open = False
        return await finish_takeout(self._invoker, self.id, success=success)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.finish(success=error is None)
