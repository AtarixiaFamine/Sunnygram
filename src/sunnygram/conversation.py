# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Asking someone something and waiting for the answer.

Handlers are a standing offer: anything of this kind, whenever it arrives, do
this. A program that asks a question already has everything it needs to handle
the reply at the point it asks, and splitting that across two handlers and a
table of who-is-halfway-through-what is what makes bots tedious to write.

    async with app.conversation("@someone") as talk:
        await talk.send("What should I call you?")
        name = await talk.wait()
        await talk.send(f"Hello, {name.text}")

A question is a filter, a future and a deadline in a table the dispatcher
consults before the handler pass.

Three things about it are decisions, not side effects, so they are written down.

**A message that answers a question does not also reach the handlers.** A
program asking someone's name does not want its command router reading the
answer. `exclusive=False` turns it off, on the conversation or on one wait.

**Waiting is bounded and always ends.** Every wait has a deadline, the table is
capped (rule P6), and an unanswered question raises `NoAnswer`. The slot is
released whichever way the wait ends, cancellation included.

**A question that times out says so**, through the logger at warning. A
conversation that quietly stopped waiting is the silent no-op rule C3 refuses.
"""

from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Any, Self

from .dispatcher import Kind, Listening
from .errors import NoAnswer
from .filters import Filter
from .types import Message

__all__ = ["Conversation", "DEFAULT_TIMEOUT"]

_log = logging.getLogger(__name__)

# Long enough that a person can read a question and type an answer, short
# enough that a program which has stopped being talked to lets go. Anything
# waiting on a human is a guess; this one is long enough to be polite and has held
# up.
DEFAULT_TIMEOUT = 60.0


class Conversation:
    """A back and forth with one chat.

    Built by `Client.conversation` instead of directly, since it needs the
    chat resolved to the id the dispatcher will see on the way in, and that is
    a call the client already knows how to make.

    Nothing is held between waits. The conversation is a place to keep the chat
    and the deadline so that the code reads like a conversation; the only
    resource it takes is one row in the dispatcher's table, and only for as
    long as it is actually waiting for something.
    """

    __slots__ = ("_client", "_chat_id", "_timeout", "_exclusive", "_open")

    def __init__(
        self,
        client: Any,
        chat_id: int,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        exclusive: bool = True,
    ) -> None:
        self._client = client
        self._chat_id = chat_id
        self._timeout = timeout
        self._exclusive = exclusive
        self._open = True

    def __repr__(self) -> str:
        return f"Conversation(chat {self._chat_id}, {self._timeout:g}s)"

    @property
    def chat_id(self) -> int:
        """The chat this is a conversation with."""
        return self._chat_id

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Nothing to release: a wait takes its place in the table out on the
        # way past, whether it was answered, timed out or cancelled. This exists
        # so the block reads as one thing and so that leaving it stops any
        # further waiting from looking like it belongs to a conversation that
        # is over.
        self._open = False

    async def send(self, text: str, **options: Any) -> Message:
        """Say something in this chat."""
        self._check()
        sent: Message = await self._client.send_message(self._chat_id, text, **options)
        return sent

    async def wait(
        self,
        *,
        filters: Filter | None = None,
        timeout: float | None = None,
        kind: Kind = "message",
        exclusive: bool | None = None,
    ) -> Any:
        """Wait for the next message from this chat, and return it.

        Raises `NoAnswer` if nothing arrives in time. A filter narrows what
        counts as an answer, which is what to reach for when the reply has to
        be a photo, or a number, or anything else where the wrong thing
        arriving should go on waiting rather than be taken as the answer.
        """
        self._check()
        return await _wait_in(
            self._client,
            self._chat_id,
            kind=kind,
            filters=filters,
            timeout=self._timeout if timeout is None else timeout,
            exclusive=self._exclusive if exclusive is None else exclusive,
        )

    async def ask(
        self,
        text: str,
        *,
        filters: Filter | None = None,
        timeout: float | None = None,
        **options: Any,
    ) -> Any:
        """Say something and wait for the reply. The two lines that matter.

        The listening starts before the question is sent, which is the whole
        reason this is one method instead of two calls the caller writes
        themselves: an answer that arrives while the send is still in flight
        would otherwise reach the handlers instead, and that race is rare
        enough to be found in production instead of in testing.
        """
        self._check()
        return await _ask_in(
            self._client,
            self._chat_id,
            text,
            filters=filters,
            timeout=self._timeout if timeout is None else timeout,
            exclusive=self._exclusive,
            **options,
        )

    async def wait_click(self, *, timeout: float | None = None) -> Any:
        """Wait for a button under a message in this chat to be pressed."""
        return await self.wait(kind="callback", timeout=timeout)

    def _check(self) -> None:
        if not self._open:
            raise RuntimeError(
                "this conversation has already been left. Waiting after the "
                "async with block has ended is nearly always a wait nothing "
                "will answer"
            )


async def _wait_in(
    client: Any,
    chat_id: int,
    *,
    kind: Kind = "message",
    filters: Filter | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    exclusive: bool = True,
) -> Any:
    """One wait, from registering to answered or given up on."""
    dispatcher = client.dispatcher
    waiting: Listening = dispatcher.listen(
        chat_id, kind=kind, filters=filters, exclusive=exclusive
    )
    try:
        return await asyncio.wait_for(waiting.future, timeout)
    except asyncio.TimeoutError:
        # Said out loud rather than raised silently (rule C3). The raise below
        # reaches the caller, but the caller may well be catching NoAnswer to
        # move on, and a bot that has stopped being answered is worth a line in
        # the log either way.
        _log.warning(
            "nothing arrived from chat %d in %gs, so the wait for a %s has "
            "been given up on",
            chat_id,
            timeout,
            kind,
        )
        raise NoAnswer(
            f"nobody in chat {chat_id} answered within {timeout:g}s"
        ) from None
    finally:
        # Every way out of here, including the caller being cancelled, gives
        # the place back. A table that only cleaned up on the happy path would
        # be a leak with a bound on it, which is worse than a leak: it works
        # until it suddenly refuses.
        dispatcher.stop_listening(waiting)


async def _ask_in(
    client: Any,
    chat_id: int,
    text: str,
    *,
    filters: Filter | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    exclusive: bool = True,
    **options: Any,
) -> Any:
    """Ask, with the listening in place before the question goes out."""
    dispatcher = client.dispatcher
    waiting: Listening = dispatcher.listen(
        chat_id, kind="message", filters=filters, exclusive=exclusive
    )
    try:
        await client.send_message(chat_id, text, **options)
        return await asyncio.wait_for(waiting.future, timeout)
    except asyncio.TimeoutError:
        _log.warning(
            "asked chat %d something and nothing came back in %gs", chat_id, timeout
        )
        raise NoAnswer(
            f"nobody in chat {chat_id} answered within {timeout:g}s"
        ) from None
    finally:
        dispatcher.stop_listening(waiting)
