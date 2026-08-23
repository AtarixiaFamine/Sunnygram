# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The client: one object over the eight layers underneath.

A Client owns a session, a connection, a peer cache, an update stream and a list
of handlers, and turns them into a short program.

    app = Client("my.session", api_id=API_ID, api_hash=API_HASH)

    @app.on_message(filters.private & filters.text)
    async def echo(client, message):
        await message.reply(message.text)

    app.run()

It settles the defaults a program would otherwise settle for itself: text is
markdown unless told otherwise, a peer is whatever you wrote and gets resolved,
an update becomes a Message before a handler sees it, and a message knows which
client it came from so it can answer.

Two of those cost something. Every message that goes past is written down,
bounded and least recently used, so a reply is tied to the message it answers
without a call; message_cache=0 turns that off. And every handler matching an
update runs, in group order; first_match=True stops each group after the first
match, which suits handlers that are a list of commands.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime
from types import TracebackType
from typing import Any, Self

from . import filters as filters_module
from . import loop as loop_module
from . import methods
from .auth import get_me, log_in, log_out
from .conversation import DEFAULT_TIMEOUT, Conversation, _ask_in, _wait_in
from .dispatcher import Callback, Dispatcher, Handler, Kind, StopPropagation
from .errors import SunnygramError
from .files import download_file, upload_file
from .network import ClientInfo, Invoker, RateLimiter
from .parser import parse as parse_text
from .peers import Target, resolve, resolve_username, unmark_id
from .plugins import load_into
from .raw import base, functions, types
from .recent import CAPACITY as MESSAGE_CACHE
from .recent import RecentMessages
from .storage import Storage, storage_for
from .tl import TLFunction, TLResult
from .transport import Proxy
from .types import (
    AdminRights,
    Chat,
    Dialog,
    Folder,
    InlineResult,
    Member,
    Message,
    Permissions,
    Story,
    Topic,
    User,
)
from .types.inline import CACHE_TIME as INLINE_CACHE
from .updates import Event, UpdateManager

__all__ = ["Client"]

# What Telegram shows in the account's list of active sessions when nothing
# better is given. Worth setting to the program's own name.
DEVICE = "Sunnygram"


class Client:
    """One Telegram account, with everything needed to use it."""

    __slots__ = (
        "_invoker",
        "_updates",
        "_dispatcher",
        "_pump",
        "_parse_mode",
        "_me",
        "_started",
        "_recent",
    )

    def __init__(
        self,
        session: str | os.PathLike[str] | Storage,
        *,
        api_id: int,
        api_hash: str,
        device_model: str = DEVICE,
        app_version: str | None = None,
        system_version: str | None = None,
        lang_code: str = "en",
        test_mode: bool = False,
        parse_mode: str | None = "markdown",
        proxy: Proxy | None = None,
        rate_limit: bool | RateLimiter = True,
        first_match: bool = False,
        message_cache: int = MESSAGE_CACHE,
        **options: Any,
    ) -> None:
        client = ClientInfo(
            api_id=api_id,
            api_hash=api_hash,
            device_model=device_model,
            **{
                name: value
                for name, value in (
                    ("app_version", app_version),
                    ("system_version", system_version),
                    ("lang_code", lang_code),
                )
                if value is not None
            },
        )
        self._invoker = Invoker(
            _storage_for(session),
            client=client,
            test_mode=test_mode,
            proxy=proxy,
            rate_limit=rate_limit,
            **options,
        )
        self._updates = UpdateManager(self._invoker)
        self._dispatcher = Dispatcher(first_match=first_match)
        self._pump: asyncio.Task[None] | None = None
        self._parse_mode = parse_mode
        self._me: User | None = None
        self._started = False
        self._recent = RecentMessages(message_cache)

    def __repr__(self) -> str:
        who = self._me.username or self._me.id if self._me else "not started"
        return f"Client({who}, {len(self._dispatcher.handlers)} handlers)"

    @property
    def invoker(self) -> Invoker:
        """The layer below, for anything this one does not wrap."""
        return self._invoker

    async def invoke(
        self,
        request: TLFunction[TLResult],
        *,
        dc_id: int | None = None,
        bulk: bool = False,
        timeout: float | None = None,
    ) -> TLResult:
        """Call a TL function this client has no friendlier spelling for.

        The whole schema is reachable this way, and the answer is typed as
        whatever the function says it is answered with, so reaching past the
        wrapped methods costs nothing in what a type checker can tell you.

        Peers are the one thing to know: a raw call wants an InputPeer, which
        resolve gives back for a username, an id or "me". Everything else is
        the schema as Telegram documents it.
        """
        return await self._invoker.invoke(
            request, dc_id=dc_id, bulk=bulk, timeout=timeout
        )

    @property
    def updates(self) -> UpdateManager:
        """The update state machine, for its counters and its queue."""
        return self._updates

    @property
    def dispatcher(self) -> Dispatcher:
        """The handlers, in the order they will run."""
        return self._dispatcher

    @property
    def me(self) -> User | None:
        """Whoever this client signed in as, once it has."""
        return self._me

    @property
    def running(self) -> bool:
        return self._started

    async def start(
        self,
        *,
        phone_number: str | Callable[[], str] | None = None,
        code: Callable[[Any], Any] | None = None,
        password: Callable[[str], Any] | None = None,
        bot_token: str | None = None,
        catch_up: bool = True,
    ) -> User:
        """Connect, sign in if this session has not, and start listening.

        A session that has been used before needs none of the arguments: the
        key is in the file and this returns the account it belongs to.
        """
        if self._started:
            raise SunnygramError("this client is already started")
        if not self._invoker.started:
            # Only if no one has: an invoker can be handed in already
            # connected, which is how a program with its own connection
            # management puts a client on top of one.
            await self._invoker.start()

        if bot_token is not None:
            from .auth import sign_in_bot

            raw = await sign_in_bot(self._invoker, bot_token)
        elif self._invoker.state.authorized:
            raw = await get_me(self._invoker)
        else:
            if phone_number is None or code is None:
                raise SunnygramError(
                    "this session has not been signed in, so start needs at "
                    "least a phone_number and a code callback, or a bot_token"
                )
            raw = await log_in(
                self._invoker,
                phone_number=phone_number,
                code=code,
                password=password,
            )

        wrapped = User.from_raw(raw)
        self._me = wrapped
        self._invoker.peers.learn(raw)
        await self._invoker.peers.flush()

        await self._updates.start(catch_up=catch_up)
        self._pump = asyncio.create_task(self._deliver(), name="sunnygram-dispatch")
        self._started = True
        assert wrapped is not None
        return wrapped

    async def stop(self) -> None:
        """Stop listening and put everything down."""
        pump, self._pump = self._pump, None
        if pump is not None:
            pump.cancel()
            await asyncio.gather(pump, return_exceptions=True)
        if self._updates.running:
            await self._updates.stop()
        self._dispatcher.close()
        self._recent.clear()
        await self._invoker.close()
        self._started = False

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.stop()

    def run(
        self,
        work: Awaitable[Any] | None = None,
        *,
        fast_loop: bool = True,
        **start: Any,
    ) -> Any:
        """Start, run until interrupted or until work finishes, then stop.

        The one-line way to turn a script into a program. Everything it does
        can be done by hand with start and stop when a program has its own loop
        to fit into.

        This is the only place the library makes a loop, not joining
        one, so it is the only place that gets to pick which kind. If uvloop is
        installed it is used here, which is worth a multiple on everything that
        waits on a socket and needs no other change. Pass fast_loop=False to
        get asyncio's own loop instead, which is worth doing when something in
        the program depends on loop internals or when a bug needs ruling in or
        out. A program that runs its own loop is not touched either way; see
        sunnygram.loop for opting in from there.
        """

        async def main() -> Any:
            await self.start(**start)
            try:
                if work is not None:
                    return await work
                await asyncio.Event().wait()
            except (KeyboardInterrupt, asyncio.CancelledError):
                return None
            finally:
                await self.stop()

        factory = loop_module.loop_factory() if fast_loop else None
        try:
            # Runner instead of asyncio.run because run only grew a
            # loop_factory in 3.12 and this supports 3.11. It is the same
            # machinery either way: asyncio.run is a Runner with the default.
            with asyncio.Runner(loop_factory=factory) as runner:
                return runner.run(main())
        except KeyboardInterrupt:
            return None

    def on_message(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle new messages, on the ones the filter says yes to."""
        return self._decorator("message", filters, group)

    def on_edited(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle messages that were changed after they were sent."""
        return self._decorator("edited", filters, group)

    def on_scheduled(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle messages queued for later instead of sent.

        This fires when something is put in the schedule, not when it goes out.
        The moment it is actually sent it arrives again as an ordinary message,
        because by then it is one.
        """
        return self._decorator("scheduled", filters, group)

    def on_album(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle albums, once all of their parts have arrived.

        The handler is given the list of messages, oldest first. Each part also
        reaches message handlers on its own, since that is what it is: an album
        is several messages sharing a group id, not one message carrying
        several files.

        A filter here is asked about the first part, which is the one that
        carries the caption in every client that shows one.
        """
        self._dispatcher.collect_albums()
        return self._decorator("album", filters, group)

    def on_callback_query(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle inline buttons being pressed.

        The handler is given a CallbackQuery, and its first duty is to answer
        it: Telegram holds the press open until something does, and every
        client draws that as a spinner on the button. Answering with nothing is
        fine and is what a bot does when the real reply is an edit.

        Filters work here as they do on messages. A callback query's text is
        its payload, so filters.data and filters.regex both read what the
        button was built with.
        """
        return self._decorator("callback", filters, group)

    def on_inline_query(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone typing this bot's name in any chat.

        Bot sessions only, and the handler's first duty is to answer: Telegram
        holds the query open until something does, and the person is looking at
        a panel that never finishes loading in the meantime. An answer with no
        results is a complete answer.

        filters.query asks what has been typed so far, and filters.regex works
        here too, since a query has text.
        """
        return self._decorator("inline_query", filters, group)

    def on_chosen_result(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle one of this bot's inline results being picked.

        Bot sessions only, and only if the bot asked to be told: inline
        feedback is a setting in BotFather instead of a call. Telegram samples
        it for busy bots, so this counts what people pick instead of
        witnessing every pick.
        """
        return self._decorator("chosen_result", filters, group)

    def on_chat_member(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone's standing in a chat changing.

        Joining, leaving, being promoted, being banned, being restricted: one
        event with the standing before and the standing after, and the
        difference between them is what happened. A bot is told this for chats
        it administers; a user account is told about the chats it is in.
        """
        return self._decorator("chat_member", filters, group)

    def on_join_request(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone asking to be let into a chat.

        Bot sessions, for a chat the bot administers whose invite link puts
        people in a queue. Nothing happens until the request is answered, and
        approve and decline are both on the request itself.
        """
        return self._decorator("join_request", filters, group)

    def on_deleted(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle messages being deleted.

        Outside a channel Telegram does not say which chat they were in, only
        which ids are gone, so a program that has to know where has to have
        written it down when the message arrived.
        """
        return self._decorator("deleted", filters, group)

    def on_reaction(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle reactions on a message changing.

        Two readings of one event and which one arrives depends on the session:
        a user account is told the running totals, a bot is told what one named
        person changed. by_person says which of the two this is.
        """
        return self._decorator("reaction", filters, group)

    def on_poll(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle a poll's standing changing.

        The question and the answers arrive when the poll itself changed and
        the results alone the rest of the time, which is most of the time.
        """
        return self._decorator("poll", filters, group)

    def on_poll_vote(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle one person voting in a public poll.

        Only a public poll produces this, since an anonymous one is the promise
        not to say who voted for what.
        """
        return self._decorator("poll_vote", filters, group)

    def on_shipping(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle Telegram asking what delivery costs for an address.

        Only arrives for invoices sent with flexible on. Without that, no
        shipping query is ever sent however many handlers are waiting.
        """
        return self._decorator("shipping", filters, group)

    def on_pre_checkout(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle the last question before a customer is charged.

        Answer within about ten seconds. Past that the payment fails on the
        customer's side and nothing is said on this one, so check what has to
        be checked, answer, and do the rest afterwards.
        """
        return self._decorator("pre_checkout", filters, group)

    def on_story(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle a story being posted, changed or taken down.

        One update covers all three, so what arrives is the story as it now
        stands. A story that was deleted has nothing left but its id and does
        not reach here at all.
        """
        return self._decorator("story", filters, group)

    def on_status(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone coming online or going offline.

        User sessions only. A bot is never told this about anybody.
        """
        return self._decorator("status", filters, group)

    def on_typing(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone typing, or doing any of the other things shown.

        Recording a voice note, uploading a video and picking a sticker are the
        same event with a different word, which is why one handler covers them.
        """
        return self._decorator("typing", filters, group)

    def on_blocked(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle this account blocking someone, or unblocking them.

        User sessions only. The bot side of the same idea is on_stopped.
        """
        return self._decorator("blocked", filters, group)

    def on_stopped(
        self, filters: filters_module.Filter | None = None, *, group: int = 0
    ) -> Callable[[Callback], Callback]:
        """Handle someone stopping this bot, or starting it again.

        Bot sessions only, and the number every bot should watch: it is the
        difference between an audience that is quiet and one that has left.
        """
        return self._decorator("stopped", filters, group)

    def on_raw(self, *, group: int = 0) -> Callable[[Callback], Callback]:
        """Handle every update, as it came off the wire.

        The escape hatch: anything the friendly layer does not wrap arrives
        here as the Event the update manager produced.
        """
        return self._decorator("raw", None, group)

    def add_handler(
        self,
        callback: Callback,
        *,
        kind: Kind = "message",
        filters: filters_module.Filter | None = None,
        group: int = 0,
    ) -> Handler:
        """Register a handler without a decorator.

        The kind is one of the words the decorators above stand for, and it is
        a fixed list rather than any string: a handler registered for a kind
        that does not exist is not an error anywhere, it is a handler that
        never runs, so the spelling is checked when the program is type
        checked instead of never.
        """
        if kind == "album":
            self._dispatcher.collect_albums()
        return self._dispatcher.add(
            Handler(callback=callback, kind=kind, filters=filters, group=group)
        )

    def remove_handler(self, handler: Handler) -> None:
        self._dispatcher.remove(handler)

    def load_plugins(
        self,
        where: str | os.PathLike[str] | Any,
        *,
        include: tuple[str, ...] | None = None,
        exclude: tuple[str, ...] = (),
    ) -> int:
        """Import a package of handlers and register them against this client.

            app.load_plugins("plugins")

        Every module in the package is imported and every function in it
        decorated with `sunnygram.plugins` is registered. Returns how many
        handlers that came to, which is worth checking: a package whose plugins
        were written without the decorators registers nothing, and a program
        that answers no one looks exactly like a program with nothing to answer.

        A plugin that fails to import raises instead of being skipped, because
        a feature that is silently absent is the fault this library refuses.
        """
        return load_into(self, where, include=include, exclude=exclude)

    async def resolve(self, target: Target) -> Any:
        """Name a peer to the server, however it was written.

        Costs nothing for anybody this session has already met, one call for a
        username or a phone number it has not. What it will not do is invent a
        peer: an id alone does not reach a stranger on MTProto, so a peer this
        account has never encountered raises PeerNotFound rather than a call
        that fails later somewhere less obvious.
        """
        return await resolve(self._invoker, target)

    async def conversation(
        self,
        peer: Target,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        exclusive: bool = True,
    ) -> Conversation:
        """A back and forth with one chat, for code that asks questions.

            async with await app.conversation("@someone") as talk:
                await talk.send("What should I call you?")
                name = await talk.wait()

        A message that answers a question does not also reach the ordinary
        handlers, which stops a command router from seeing someone's
        name as a command. exclusive=False if both should see it.

        Awaited before the `async with` because the chat has to be resolved to
        the id updates will arrive with, and resolving is a call.
        """
        return Conversation(
            self,
            _peer_id(await resolve(self._invoker, peer)),
            timeout=timeout,
            exclusive=exclusive,
        )

    async def ask(
        self,
        peer: Target,
        text: str,
        *,
        filters: filters_module.Filter | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        exclusive: bool = True,
        **options: Any,
    ) -> Message:
        """Send a question and wait for the answer. One call.

        Raises NoAnswer if nothing arrives in time. The listening is in place
        before the question goes out, so a fast answer cannot arrive while the
        send is still in flight and end up somewhere else.
        """
        answer: Message = await _ask_in(
            self,
            _peer_id(await resolve(self._invoker, peer)),
            text,
            filters=filters,
            timeout=timeout,
            exclusive=exclusive,
            **options,
        )
        return answer

    async def wait_for(
        self,
        peer: Target,
        *,
        kind: Kind = "message",
        filters: filters_module.Filter | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        exclusive: bool = True,
    ) -> Any:
        """Wait for the next message from a chat without asking anything first.

        For the half of a conversation that starts with them instead of with
        us: a confirmation, a file someone was told to send, a button press.
        """
        return await _wait_in(
            self,
            _peer_id(await resolve(self._invoker, peer)),
            kind=kind,
            filters=filters,
            timeout=timeout,
            exclusive=exclusive,
        )

    async def forget_peer(self, target: Target) -> bool:
        """Drop what is remembered about a peer, and say whether there was any.

        Rarely needed by hand, because a call the server refuses on the grounds
        of the peer already drops it. This is here for the case that refusal
        cannot see: a hash that is wrong in a way the server answers by
        pretending the peer does not exist, where the call looks successful and
        the answer is empty.
        """
        if isinstance(target, int) and not isinstance(target, bool):
            # Taken apart instead of resolved, because an id is all that is
            # needed to forget and resolving one that was already forgotten
            # would raise instead of saying no.
            peer_id, _ = unmark_id(target)
        else:
            peer_id = _peer_id(await resolve(self._invoker, target))
        if not peer_id:
            return False
        return await self._invoker.peers.forget(peer_id)

    async def refresh_peer(self, username: str) -> Any:
        """Ask the server about a username again, and keep the new answer.

        The repair for a peer whose access hash has stopped working. resolve
        answers from the cache, which is the whole point of it and exactly what
        is unhelpful when the cached answer is the problem, so this is the one
        that always goes to the network.
        """
        record = await resolve_username(self._invoker, username)
        return await resolve(self._invoker, record.id)

    async def get_me(self) -> User:
        """Who this client is signed in as, asked freshly."""
        wrapped = User.from_raw(await get_me(self._invoker))
        if wrapped is None:
            raise SunnygramError("the server did not say who we are")
        self._me = wrapped
        return wrapped

    async def log_out(self) -> None:
        """End the session on Telegram's side and forget the key."""
        await log_out(self._invoker)
        self._me = None

    async def send_message(
        self,
        peer: Target,
        text: str,
        *,
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        reply_to: int | None = None,
        topic: int | None = None,
        silent: bool = False,
        no_webpage: bool = False,
        reply_markup: Any = None,
        schedule_date: datetime | int | None = None,
    ) -> Message:
        """Send a message, and answer with the one the server made of it.

        parse_mode defaults to the client's, and passing None sends the text
        exactly as it is. Passing entities skips parsing altogether, which is
        what forwarding someone else's formatting looks like.

        reply_markup is a keyboard to put under it, built by types.keyboard
        out of types.Button. Only a bot may send one, which is Telegram's rule
        rather than this one.

        schedule_date queues the message for later instead of sending it now,
        as a datetime or a unix timestamp, or sunnygram.WHEN_ONLINE to send it
        the moment the recipient next appears. What comes back is the queued
        message, which lives in get_scheduled until its time.
        """
        if not text:
            raise ValueError("a message needs something in it")
        body, found = self._styled(text, parse_mode, entities)
        where = await self.resolve(peer)
        answer = await self._invoker.invoke(
            functions.messages.SendMessage(
                peer=where,
                message=body,
                random_id=_random_id(),
                entities=found or None,
                no_webpage=no_webpage,
                silent=silent,
                reply_to=methods.reply_header(reply_to, topic),
                reply_markup=reply_markup,
                schedule_date=methods.schedule_at(schedule_date),
            )
        )
        await self._updates.feed(answer)
        return self._message_out_of(answer, body, found, peer=where, reply_to=reply_to)

    async def edit_message(
        self,
        peer: Target,
        message_id: int,
        text: str,
        *,
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        no_webpage: bool = False,
        reply_markup: Any = None,
    ) -> Message:
        """Rewrite a message that is ours to rewrite.

        The keyboard is replaced along with the text when one is given, and
        left alone when none is. Taking one away is edit_markup with nothing,
        since there is no way to tell "no keyboard" from "do not touch the
        keyboard" in one argument.
        """
        body, found = self._styled(text, parse_mode, entities)
        where = await self.resolve(peer)
        answer = await self._invoker.invoke(
            functions.messages.EditMessage(
                peer=where,
                id=message_id,
                message=body,
                entities=found or None,
                no_webpage=no_webpage,
                reply_markup=reply_markup,
            )
        )
        await self._updates.feed(answer)
        return self._message_out_of(answer, body, found, peer=where)

    async def edit_media(
        self,
        peer: Target,
        message_id: int,
        media: Any,
        *,
        caption: str | None = None,
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        reply_markup: Any = None,
        **upload: Any,
    ) -> Message:
        """Replace the file on a message that already carries one.

        The media is anything send_file or send_media would take: a path, the
        bytes, a file Telegram already holds, or a portable reference. A path
        is uploaded first, which is the only reason this is longer than the
        call it makes.

        Telegram will not put a file on a message that has none, and will not
        take one off, so this edits a photo into a different photo instead of
        turning a text message into one. Passing no caption leaves the existing
        one alone.
        """
        found = methods.existing_media(media)
        if found is None:
            called = methods.name_of(media, upload.pop("name", None))
            chosen = methods.kind_of(called, upload.pop("kind", "auto"))
            handle = await upload_file(self._invoker, media, name=called, **upload)
            found = methods.as_media(
                handle, chosen, name=None if chosen == "photo" else called
            )
        body, styled = self._styled(caption or "", parse_mode, entities)
        where = await self.resolve(peer)
        answer = await self._invoker.invoke(
            functions.messages.EditMessage(
                peer=where,
                id=message_id,
                media=found,
                message=None if caption is None else body,
                entities=styled or None if caption is not None else None,
                reply_markup=reply_markup,
            )
        )
        await self._updates.feed(answer)
        return self._message_out_of(answer, body, styled, peer=where)

    async def edit_markup(
        self, peer: Target, message_id: int, markup: Any = None
    ) -> Message:
        """Change the buttons under a message and leave its text alone.

        Passing nothing takes the keyboard away, which a bot does with
        a menu once it has been used and is the reason this is a call of its
        own instead of an argument to edit_message.
        """
        where = await self.resolve(peer)
        answer = await self._invoker.invoke(
            functions.messages.EditMessage(
                peer=where,
                id=message_id,
                reply_markup=markup or types.ReplyInlineMarkup(rows=[]),
            )
        )
        await self._updates.feed(answer)
        return self._message_out_of(answer, "", [], peer=where)

    async def edit_inline_message(self, inline_id: Any, text: str, **options: Any) -> bool:
        """Rewrite a message an inline query produced.

        These have no chat behind them, so they are named by the opaque id that
        comes off a callback query rather than by a peer and a message id, and
        the answer is whether the edit went through instead of the message.
        """
        parse_mode = options.pop("parse_mode", "")
        entities = options.pop("entities", None)
        body, found = self._styled(text, parse_mode, entities)
        return await methods.edit_inline_message(
            self._invoker, inline_id, body, entities=found or None, **options
        )

    async def edit_inline_markup(self, inline_id: Any, markup: Any = None) -> bool:
        """Change the buttons on an inline message, or take them away."""
        return await methods.edit_inline_message(
            self._invoker,
            inline_id,
            reply_markup=markup or types.ReplyInlineMarkup(rows=[]),
        )

    async def answer_inline_query(
        self,
        query_id: int,
        results: list[InlineResult | Any],
        *,
        cache_time: int = INLINE_CACHE,
        gallery: bool = False,
        private: bool = False,
        next_offset: str = "",
        switch_pm: str = "",
        start_parameter: str = "",
        parse_mode: str | None = "",
    ) -> bool:
        """Answer an inline query with what this bot is offering.

        InlineQuery.answer is the same call reached from the query itself and
        is the one a handler normally wants. This is here for a program holding
        the id.

        The results are InlineResult, built by its factories, or the raw
        constructors for anything they do not cover. The message each one sends
        is styled here instead of when the result was built, because the parse
        mode belongs to the client and a result is usually built before there
        is one in hand.
        """
        style = self._styling(parse_mode)
        return await methods.answer_inline_query(
            self._invoker,
            query_id,
            [_as_result(one, style) for one in results],
            cache_time=cache_time,
            gallery=gallery,
            private=private,
            next_offset=next_offset,
            switch_pm=switch_pm,
            start_parameter=start_parameter,
        )

    async def answer_callback_query(
        self,
        query_id: int,
        text: str = "",
        *,
        alert: bool = False,
        url: str | None = None,
        cache_time: int = 0,
    ) -> bool:
        """Answer a button press, which stops the button spinning.

        CallbackQuery.answer is the same call reached from the press itself,
        and is the one a handler normally wants. This is here for a program
        that has kept the id and is answering later.
        """
        return await methods.answer_callback(
            self._invoker,
            query_id,
            text,
            alert=alert,
            url=url,
            cache_time=cache_time,
        )

    async def delete_messages(
        self, peer: Target, ids: list[int], *, everywhere: bool = True
    ) -> int:
        """Delete messages, and say how many the server owned up to.

        everywhere takes them back for the other side too, which is allowed for
        a while after sending and always in a chat we administer.
        """
        where = await self.resolve(peer)
        if isinstance(where, types.InputPeerChannel):
            # A channel counts its own messages, so deleting in one is a
            # different call taking the channel rather than the peer.
            answer = await self._invoker.invoke(
                functions.channels.DeleteMessages(
                    channel=types.InputChannel(
                        channel_id=where.channel_id, access_hash=where.access_hash
                    ),
                    id=ids,
                )
            )
        else:
            answer = await self._invoker.invoke(
                functions.messages.DeleteMessages(id=ids, revoke=everywhere)
            )
        return int(getattr(answer, "pts_count", 0))

    async def forward_messages(
        self, target: Target, source: Target, ids: list[int], *, silent: bool = False
    ) -> None:
        """Send messages from one chat on to another."""
        await self._invoker.invoke(
            functions.messages.ForwardMessages(
                from_peer=await self.resolve(source),
                to_peer=await self.resolve(target),
                id=ids,
                random_id=[_random_id() for _ in ids],
                silent=silent,
            )
        )

    async def get_history(
        self,
        peer: Target,
        *,
        limit: int = 100,
        offset_id: int = 0,
        batch: int = 100,
    ) -> AsyncIterator[Message]:
        """Read a chat backwards, oldest call last, paging handled here.

        Telegram answers history a page at a time and expects the client to
        keep asking with the id it got to. That bookkeeping is the whole reason
        this exists: a caller says how many they want and reads them.
        """
        where = await self.resolve(peer)
        seen = 0
        cursor = offset_id
        while seen < limit:
            answer = await self._invoker.invoke(
                functions.messages.GetHistory(
                    peer=where,
                    offset_id=cursor,
                    offset_date=0,
                    add_offset=0,
                    limit=min(batch, limit - seen),
                    max_id=0,
                    min_id=0,
                    hash=0,
                )
            )
            raw = list(getattr(answer, "messages", ()) or ())
            if not raw:
                return
            users = {user.id: user for user in getattr(answer, "users", ())}
            chats = {chat.id: chat for chat in getattr(answer, "chats", ())}
            replies = {one.id: one for one in raw if hasattr(one, "id")}
            for one in raw:
                wrapped = self.wrap_message(
                    one, users=users, chats=chats, replies=replies
                )
                if wrapped is not None:
                    yield wrapped
                    seen += 1
                    if seen >= limit:
                        return
                cursor = one.id
            if len(raw) < 2:
                # A page with one message on it is the end of the chat, since
                # the next call would only return that same one again.
                return

    async def get_messages(self, peer: Target, ids: list[int]) -> list[Message]:
        """Fetch particular messages by id.

        A message that is not there, because it was deleted or never existed,
        is left out instead of coming back as a hole, so the answer may be
        shorter than what was asked for.
        """
        answer = await methods.get_messages(self._invoker, peer, ids)
        return self._messages_in(answer)

    async def send_invoice(
        self, peer: Target, invoice: Any, **options: Any
    ) -> Message:
        """Send an invoice, built by methods.as_invoice or as_stars_invoice.

        An invoice is a kind of media instead of a call of its own, so this is
        send_media with a clearer name and the same options.
        """
        return await self._send_attachment(peer, invoice, **options)

    async def answer_shipping(
        self,
        query_id: int,
        *,
        options: list[Any] | None = None,
        error: str | None = None,
    ) -> bool:
        """Answer a shipping query with options, or a reason there are none."""
        return await methods.answer_shipping(
            self._invoker, query_id, options=options, error=error
        )

    async def answer_pre_checkout(
        self, query_id: int, *, ok: bool = True, error: str | None = None
    ) -> bool:
        """Approve or reject a payment. About ten seconds to do it in."""
        return await methods.answer_pre_checkout(
            self._invoker, query_id, ok=ok, error=error
        )

    async def get_stars_balance(self, peer: Target = "me") -> int:
        """How many Stars this account, or a channel it runs, holds."""
        return await methods.stars_balance(self._invoker, peer)

    async def get_stars_transactions(self, peer: Target = "me", **options: Any) -> Any:
        """The Stars ledger, newest first."""
        return await methods.stars_transactions(self._invoker, peer, **options)

    async def refund_stars(self, user: Target, charge_id: str) -> Any:
        """Give back a Stars payment, by the charge id it arrived with."""
        return await methods.refund_stars(self._invoker, user, charge_id)

    async def send_story(
        self,
        peer: Target,
        file: Any,
        *,
        caption: str = "",
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        privacy: str | list[Any] = "everyone",
        pinned: bool = False,
        noforwards: bool = False,
        period: int | None = None,
        progress: Any = None,
        **upload: Any,
    ) -> list[Story]:
        """Post a story, and answer with the stories the server made of it.

        The file is a path, the bytes, or anything with a read method, the same
        as send_file takes, and is uploaded first.

        privacy is who may see it: everyone, contacts, close_friends or no one.
        It has a default because the wire does not: an empty rule list means
        no one, so a story posted without saying is a story no one sees.

        period is how long it stays up, one of 6, 12, 24 or 48 hours in
        seconds. pinned keeps it on the profile once it expires.
        """
        called = methods.name_of(file, upload.pop("name", None))
        chosen = methods.kind_of(called, upload.pop("kind", "auto"))
        if chosen not in ("photo", "video"):
            raise SunnygramError(
                f"a story is a photo or a video, not {chosen}"
            )
        handle = await upload_file(
            self._invoker, file, name=called, progress=progress, **upload
        )
        body, styled = self._styled(caption, parse_mode, entities)
        described = methods.as_media(
            handle, chosen, name=None if chosen == "photo" else called
        )
        answer = await methods.send_story(
            self._invoker,
            peer,
            described,
            caption=body,
            entities=styled or None,
            privacy=privacy,
            pinned=pinned,
            noforwards=noforwards,
            period=period,
            updates=self._updates,
        )
        return self._stories_in(answer)

    async def get_stories(
        self, peer: Target, ids: list[int] | None = None
    ) -> list[Story]:
        """Stories an account has up, or particular ones by id."""
        if ids is None:
            answer = await methods.get_peer_stories(self._invoker, peer)
            found = getattr(getattr(answer, "stories", None), "stories", ())
        else:
            answer = await methods.get_stories(self._invoker, peer, ids)
            found = getattr(answer, "stories", ())
        wrapped = [Story.from_raw(one) for one in found]
        return [one for one in wrapped if one is not None]

    async def get_pinned_stories(
        self, peer: Target, *, limit: int = 100
    ) -> list[Story]:
        """The stories an account keeps on its profile after they expire."""
        answer = await methods.pinned_stories(self._invoker, peer, limit=limit)
        wrapped = [Story.from_raw(one) for one in getattr(answer, "stories", ())]
        return [one for one in wrapped if one is not None]

    async def edit_story(self, peer: Target, story_id: int, **changes: Any) -> None:
        """Change a story that is already up: its caption, media or privacy."""
        await methods.edit_story(
            self._invoker, peer, story_id, updates=self._updates, **changes
        )

    async def delete_stories(self, peer: Target, ids: list[int]) -> list[int]:
        """Take stories down, and say which ones went."""
        return await methods.delete_stories(self._invoker, peer, ids)

    async def pin_stories(
        self, peer: Target, ids: list[int], *, pinned: bool = True
    ) -> list[int]:
        """Keep stories on the profile after they expire, or stop."""
        return await methods.pin_stories(self._invoker, peer, ids, pinned=pinned)

    async def read_stories(self, peer: Target, max_id: int) -> list[int]:
        """Mark everything up to a story as seen."""
        return await methods.read_stories(self._invoker, peer, max_id)

    def _stories_in(self, answer: Any) -> list[Story]:
        """Every story among the updates a story call answered with."""
        found = []
        for update in getattr(answer, "updates", ()):
            story = Story.from_raw(getattr(update, "story", None))
            if story is not None:
                found.append(story)
        return found

    async def get_folders(self) -> list[Folder]:
        """The folders this account has sorted its chats into.

        The unfiltered view Telegram lists alongside them is not a folder and
        is left out, so what comes back is the folders someone actually made.
        """
        found = [Folder.from_raw(one) for one in await methods.get_folders(self._invoker)]
        return [one for one in found if one is not None]

    async def save_folder(
        self, folder_id: int, title: str, **rules: Any
    ) -> bool:
        """Create or replace a folder.

        There is no separate call for creating one: saving under an id nothing
        is using makes it, and saving over a used id replaces it, which is
        Telegram's design rather than this one. Pick an id get_folders is not
        already showing.

        The rules are which chats to include, exclude and pin, and the
        categories to sweep in: contacts, non_contacts, groups, broadcasts,
        bots, and the exclude_muted, exclude_read and exclude_archived
        switches.
        """
        built = await methods.build_folder(self._invoker, folder_id, title, **rules)
        return await methods.save_folder(self._invoker, folder_id, built)

    async def delete_folder(self, folder_id: int) -> bool:
        """Remove a folder. The chats it showed are not affected."""
        return await methods.delete_folder(self._invoker, folder_id)

    async def reorder_folders(self, order: list[int]) -> bool:
        """Set the order folders appear in, by id."""
        return await methods.reorder_folders(self._invoker, order)

    async def takeout(self, **what: Any) -> methods.Takeout:
        """Open a data-export session, which reads without the usual limits.

        Say which parts the export may reach: contacts, message_users,
        message_chats, message_megagroups, message_channels, files, and
        file_max_size to cap how large a file it will take.

        Use it as a context manager, which closes the session afterwards and
        tells Telegram whether the export finished or gave up:

            async with await app.takeout(message_users=True) as export:
                history = await export.invoke(functions.messages.GetHistory(...))

        Raises TakeoutInitDelay if the account holder has not approved the
        export yet. That is a person being asked to tap something in an
        official client, so its seconds are hours and it is not waited out for
        you the way an ordinary flood wait is.
        """
        return methods.Takeout(
            self._invoker, await methods.init_takeout(self._invoker, **what)
        )

    async def get_scheduled(
        self, peer: Target, ids: list[int] | None = None
    ) -> list[Message]:
        """Messages queued for a chat and not sent yet.

        The whole queue, or the ones named. These carry their own ids, which
        are not the ids the messages will have once they go out, so they are
        only good for the other scheduled calls.
        """
        if ids is None:
            answer = await methods.scheduled_history(self._invoker, peer)
        else:
            answer = await methods.get_scheduled_messages(self._invoker, peer, ids)
        return self._messages_in(answer)

    async def send_scheduled(self, peer: Target, ids: list[int]) -> None:
        """Send queued messages now instead of waiting for their time."""
        await methods.send_scheduled_messages(
            self._invoker, peer, ids, updates=self._updates
        )

    async def delete_scheduled(self, peer: Target, ids: list[int]) -> None:
        """Drop queued messages so they never go out."""
        await methods.delete_scheduled_messages(
            self._invoker, peer, ids, updates=self._updates
        )

    async def search_messages(
        self,
        peer: Target,
        query: str = "",
        *,
        limit: int = 100,
        batch: int = 100,
        from_user: Target | None = None,
        filter: base.MessagesFilter | None = None,
    ) -> AsyncIterator[Message]:
        """Search one chat, paging handled here.

        An empty query with a filter is how to ask for every photo, or every
        link, without searching for anything in particular.
        """
        seen = 0
        cursor = 0
        while seen < limit:
            answer = await methods.search_messages(
                self._invoker,
                peer,
                query,
                limit=min(batch, limit - seen),
                offset_id=cursor,
                from_user=from_user,
                filter=filter,
            )
            found = self._messages_in(answer)
            if not found:
                return
            for message in found:
                yield message
                seen += 1
                if seen >= limit:
                    return
            cursor = found[-1].id

    async def read_history(self, peer: Target, *, max_id: int = 0) -> None:
        """Mark a chat as read, up to a message or all of it."""
        await methods.read_history(self._invoker, peer, max_id=max_id)

    async def pin_message(
        self,
        peer: Target,
        message_id: int,
        *,
        silent: bool = True,
        both_sides: bool = False,
    ) -> None:
        """Pin a message, quietly unless told otherwise."""
        await methods.pin_message(
            self._invoker,
            peer,
            message_id,
            silent=silent,
            both_sides=both_sides,
            updates=self._updates,
        )

    async def unpin_message(self, peer: Target, message_id: int) -> None:
        """Unpin one message."""
        await methods.unpin_message(
            self._invoker, peer, message_id, updates=self._updates
        )

    async def unpin_all_messages(self, peer: Target) -> None:
        """Unpin everything pinned in a chat."""
        await methods.unpin_all_messages(self._invoker, peer)

    async def send_action(
        self, peer: Target, action: base.SendMessageAction | None = None
    ) -> None:
        """Show that something is being done. Typing, unless said otherwise.

        Telegram forgets one of these after about six seconds, so anything
        slower than that has to say it again.
        """
        await methods.send_action(self._invoker, peer, action)

    async def send_file(
        self,
        peer: Target,
        file: Any,
        *,
        caption: str = "",
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        kind: str = "auto",
        name: str | None = None,
        mime_type: str | None = None,
        thumb: Any = None,
        duration: float = 0,
        width: int = 0,
        height: int = 0,
        title: str | None = None,
        performer: str | None = None,
        streaming: bool = True,
        spoiler: bool = False,
        ttl_seconds: int | None = None,
        reply_to: int | None = None,
        topic: int | None = None,
        silent: bool = False,
        reply_markup: Any = None,
        schedule_date: datetime | int | None = None,
        progress: Any = None,
        **upload: Any,
    ) -> Message:
        """Send a file, and answer with the message that carries it.

        The file is a path, the bytes themselves, or anything with a read
        method. What it arrives as is worked out from the name unless kind says
        otherwise, and getting that wrong is the difference between a video
        that plays in place and one that has to be downloaded first.

        The caption is the message text, since Telegram has no separate field
        for one, and is parsed the same way a message is.
        """
        if methods.existing_media(file) is not None:
            # Otherwise the reference itself is handed to the uploader, which
            # fails somewhere further down with nothing about it saying that
            # the caller wanted the other kind of send.
            raise SunnygramError(
                f"{type(file).__name__} names a file Telegram already holds, "
                f"which send_file would try to upload. Use send_media"
            )
        called = methods.name_of(file, name)
        chosen = methods.kind_of(called, kind)
        handle = await upload_file(
            self._invoker, file, name=called, progress=progress, **upload
        )
        body, found = self._styled(caption, parse_mode, entities)
        described = methods.as_media(
            handle,
            chosen,
            name=None if chosen == "photo" else called,
            mime_type=mime_type,
            thumb=(
                None
                if thumb is None
                else await upload_file(self._invoker, thumb, name="thumb.jpg")
            ),
            duration=duration,
            width=width,
            height=height,
            title=title,
            performer=performer,
            streaming=streaming,
            spoiler=spoiler,
            ttl_seconds=ttl_seconds,
        )
        sent = await methods.send_media(
            self._invoker,
            peer,
            described,
            message=body,
            entities=found or None,
            reply_to=reply_to,
            topic=topic,
            silent=silent,
            reply_markup=reply_markup,
            schedule_date=schedule_date,
            updates=self._updates,
        )
        return self._sent(sent)

    async def send_photo(self, peer: Target, photo: Any, **options: Any) -> Message:
        """Send an image as a photo, which Telegram re-encodes and shows inline."""
        return await self.send_file(peer, photo, kind="photo", **options)

    async def send_document(self, peer: Target, document: Any, **options: Any) -> Message:
        """Send anything as a file, kept exactly as it is."""
        return await self.send_file(peer, document, kind="document", **options)

    async def send_video(self, peer: Target, video: Any, **options: Any) -> Message:
        """Send a video, playable in place.

        duration, width and height are worth passing when they are known.
        Telegram works them out on its own eventually, and until it has, the
        video shows up as a file.
        """
        return await self.send_file(peer, video, kind="video", **options)

    async def send_media(
        self, peer: Target, media: Any, *, spoiler: bool = False, **options: Any
    ) -> Message:
        """Send a file Telegram already holds, without uploading it again.

        This is the cheap half of sending. A file that has been sent once can
        go anywhere else by being named, so a program that has kept what it
        sent, or is passing along what it received, pays for a single call
        instead of a download and an upload.

        The media is a message, the media off one, a Document or a Photo,
        either of their input forms, or the portable reference string that
        file_ref writes one down as. Anything else says so, since the
        alternative would be silently sending nothing.

        The file reference inside goes stale after an hour or so. Where what
        was passed says which message the file came from, which a message and a
        portable reference both do, that is renewed here and the send is tried
        once more. Where it does not, a stale reference comes back as an error
        and the answer is to fetch the message again.

        spoiler hides it behind a tap. That belongs to this send instead of to
        the file, so a photo kept in a cache goes out plain to one asker and
        covered to the next without being stored twice.
        """
        found = methods.existing_media(media, spoiler=spoiler)
        if found is None:
            raise SunnygramError(
                f"{type(media).__name__} is not a file Telegram already holds. "
                f"Use send_file to upload one"
            )
        return await self._send_attachment(
            peer, found, origin=methods.media_origin(media), **options
        )

    async def send_animation(
        self, peer: Target, animation: Any, **options: Any
    ) -> Message:
        """Send a gif, which Telegram stores as a soundless looping video.

        A real .gif goes as one too: it is converted on arrival, and sending it
        as a document instead is what keeps the original bytes.
        """
        return await self.send_file(peer, animation, kind="animation", **options)

    async def send_audio(self, peer: Target, audio: Any, **options: Any) -> Message:
        """Send a music track, with title and performer if you have them."""
        return await self.send_file(peer, audio, kind="audio", **options)

    async def send_voice(self, peer: Target, voice: Any, **options: Any) -> Message:
        """Send a voice note, the round kind that plays where it sits."""
        return await self.send_file(peer, voice, kind="voice", **options)

    async def send_sticker(self, peer: Target, sticker: Any, **options: Any) -> Message:
        """Send a sticker that already exists, by pointing at its document.

        A sticker is a document, so this takes one off a message, an
        InputDocument, or anything else as_document understands. Uploading new
        sticker bytes is send_file's job and makes a file, not a sticker.
        """
        return await self._send_attachment(
            peer,
            methods.as_document(sticker),
            origin=methods.media_origin(sticker),
            **options,
        )

    async def send_album(
        self,
        peer: Target,
        files: list[Any],
        *,
        captions: list[str] | None = None,
        options: list[dict[str, Any]] | None = None,
        parse_mode: str | None = "",
        reply_to: int | None = None,
        topic: int | None = None,
        silent: bool = False,
        progress: Any = None,
        **upload: Any,
    ) -> list[Message]:
        """Send several files as one album, and answer with their messages.

        Each file is whatever send_file takes, and each is worked out the same
        way. Photos and videos group together; documents group together; the
        two cannot be mixed, and trying says so instead of failing on the
        wire.

        captions runs alongside files. Most clients show only the first under
        the whole block, so that is usually the only one worth setting.

        options runs alongside them too, and is what send_file takes for one
        file: kind, thumb, duration, width, height and the rest. A video in an
        album needs its duration and size as much as one sent on its own, and
        without somewhere to say them every video in an album arrives as a file
        until Telegram has worked them out for itself.

        A file Telegram already holds may be passed instead of a path, and is
        pointed at instead of uploaded again. The two can be mixed freely.
        Such an entry takes spoiler out of its options like any other; the rest
        of them describe an upload and mean nothing to a file already there.

        One thing an album does not do that a single send does: a stale file
        reference is not renewed here. A multi-media send names every file in
        one call, so there is no one file to retry, and an album of pointers
        old enough to have gone stale has to be rebuilt by whoever kept them.
        """
        if captions is not None and len(captions) != len(files):
            raise ValueError("there must be one caption per file, or none at all")
        if options is not None and len(options) != len(files):
            raise ValueError("there must be one set of options per file, or none")

        described = []
        for index, file in enumerate(files):
            each = dict(options[index]) if options else {}
            # An entry that needs no upload still takes spoiler out of its
            # options, the same as one that does. Reading it only on the upload
            # path would mean a cached photo could not be sent covered while a
            # freshly uploaded one could.
            already = methods.existing_media(
                file, spoiler=bool(each.get("spoiler", False))
            )
            if already is not None:
                described.append(already)
                continue
            called = methods.name_of(file, each.pop("name", None))
            chosen = methods.kind_of(called, each.pop("kind", "auto"))
            handle = await upload_file(
                self._invoker, file, name=called, progress=progress, **upload
            )
            described.append(
                methods.as_media(
                    handle,
                    chosen,
                    name=None if chosen == "photo" else called,
                    **each,
                )
            )

        styled = [
            self._styled(caption, parse_mode, None) for caption in (captions or [])
        ]
        sent = await methods.send_album(
            self._invoker,
            peer,
            described,
            captions=styled or None,
            reply_to=reply_to,
            topic=topic,
            silent=silent,
            updates=self._updates,
        )
        return [self._sent(one) for one in sent]

    async def send_poll(
        self,
        peer: Target,
        question: str,
        answers: list[str],
        **options: Any,
    ) -> Message:
        """Send a poll, or a quiz if one of the answers is named as correct.

        Answers are referred to by position everywhere in this library, so
        correct=0 is the first of them and voting takes the same numbers.
        """
        send = {
            name: options.pop(name)
            for name in ("reply_to", "silent")
            if name in options
        }
        return await self._send_attachment(
            peer, methods.as_poll(question, answers, **options), **send
        )

    async def vote(self, peer: Target, message_id: int, *options: int) -> Any:
        """Answer a poll by the positions of the answers, or none to retract."""
        return await methods.vote_poll(
            self._invoker, peer, message_id, list(options)
        )

    async def close_poll(self, peer: Target, message_id: int) -> None:
        """Stop a poll taking votes, which cannot be undone."""
        await methods.close_poll(
            self._invoker, peer, message_id, updates=self._updates
        )

    async def get_poll(self, peer: Target, message_id: int) -> Any:
        """A poll's standing right now, without waiting for an update."""
        return await methods.poll_results(self._invoker, peer, message_id)

    async def send_dice(
        self, peer: Target, kind: str = "dice", **options: Any
    ) -> Message:
        """Roll something. Telegram decides the number, not the sender.

        The names it knows are in methods.DICE, and the emoji itself works for
        anything added since.
        """
        return await self._send_attachment(peer, methods.as_dice(kind), **options)

    async def send_location(
        self, peer: Target, latitude: float, longitude: float, **options: Any
    ) -> Message:
        """Send a point on the map."""
        accuracy = options.pop("accuracy", None)
        return await self._send_attachment(
            peer, methods.as_location(latitude, longitude, accuracy=accuracy), **options
        )

    async def send_venue(
        self,
        peer: Target,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        **options: Any,
    ) -> Message:
        """Send a named place, which is a location with a title on it."""
        venue = {
            name: options.pop(name)
            for name in ("provider", "venue_id", "venue_type")
            if name in options
        }
        return await self._send_attachment(
            peer,
            methods.as_venue(latitude, longitude, title, address, **venue),
            **options,
        )

    async def send_contact(
        self, peer: Target, phone: str, first_name: str, **options: Any
    ) -> Message:
        """Send someone's card. This does not add them as a contact."""
        card = {
            name: options.pop(name)
            for name in ("last_name", "vcard")
            if name in options
        }
        return await self._send_attachment(
            peer, methods.as_contact(phone, first_name, **card), **options
        )

    async def copy_message(
        self, peer: Target, source: Message, **options: Any
    ) -> Message:
        """Send a message again as a new one, with no sign of where it came from.

        Not a forward: nothing on the copy says who wrote it first. What can be
        copied is text and media that already exists, which leaves out polls,
        since a poll is votes, not content.
        """
        raw = source.raw
        if not isinstance(raw, types.Message):
            raise SunnygramError("only a real message can be copied")
        sent = await methods.copy_message(
            self._invoker, raw, peer, updates=self._updates, **options
        )
        return self._sent(sent)

    async def react(
        self,
        peer: Target,
        message_id: int,
        reaction: Any = None,
        *,
        big: bool = False,
    ) -> None:
        """Set this account's reactions on a message, or clear them.

        The call replaces instead of adds, which is Telegram's design: passing
        nothing takes every reaction back, and passing two sets both.
        """
        await self._updates.feed(
            await methods.send_reaction(
                self._invoker, peer, message_id, reaction, big=big
            )
        )

    async def get_reactions(
        self, peer: Target, message_id: int, **options: Any
    ) -> list[Any]:
        """Who reacted to a message, and with what.

        Only chats small enough for Telegram to keep the list answer with
        names; a large channel gives counts and nothing else.
        """
        found = await methods.get_reactions(
            self._invoker, peer, message_id, **options
        )
        return list(getattr(found, "reactions", ()))

    async def click(
        self,
        message: Message,
        which: Any = 0,
        *,
        password: str = "",
    ) -> Any:
        """Press a button under a message, and hand back the bot's answer.

        which is how anybody refers to a button: its label, or its number in
        reading order, or a (row, position) pair. The answer is usually a short
        notice; a bot that replies by editing the message instead says nothing
        here and the edit arrives as an update.
        """
        return await methods.click_button(
            self._invoker, self._peer_of(message), message, which, password=password
        )

    def buttons_of(self, message: Message) -> list[list[Any]]:
        """The rows of inline buttons under a message, if it has any."""
        return methods.keyboard_of(message)

    async def inline_query(
        self, bot: Target, query: str = "", **options: Any
    ) -> Any:
        """Ask a bot for inline results, the way typing @bot query does."""
        return await methods.inline_results(self._invoker, bot, query, **options)

    async def send_inline_result(
        self, peer: Target, query_id: int, result_id: str, **options: Any
    ) -> Any:
        """Send one of the results an inline query answered with."""
        return await methods.send_inline_result(
            self._invoker,
            peer,
            query_id,
            result_id,
            updates=self._updates,
            **options,
        )

    async def start_bot(self, bot: Target, **options: Any) -> Any:
        """Press start on a bot, with the parameter a deep link would carry."""
        return await methods.start_bot(
            self._invoker, bot, updates=self._updates, **options
        )

    async def set_bot_commands(
        self, commands: list[tuple[str, str]], **options: Any
    ) -> Any:
        """Publish the slash-command menu clients offer as autocomplete.

        Each command is a name and a description. A leading slash is allowed
        and stripped, since that is how people write them down.

        Signed in with a bot token only: this is the bot saying something about
        itself, and a user account has nothing to say here.
        """
        return await methods.set_bot_commands(self._invoker, commands, **options)

    async def get_bot_commands(self, **options: Any) -> list[tuple[str, str]]:
        """The published command menu, in the shape set_bot_commands takes."""
        return await methods.get_bot_commands(self._invoker, **options)

    async def delete_bot_commands(self, **options: Any) -> Any:
        """Take the published command menu away."""
        return await methods.delete_bot_commands(self._invoker, **options)

    async def get_sessions(self) -> list[Any]:
        """Every place this account is signed in, this one included."""
        found = await methods.sessions(self._invoker)
        return list(getattr(found, "authorizations", ()))

    async def terminate_session(self, hash: int) -> bool:
        """Sign one other session out, by the hash the listing gave it."""
        return await methods.terminate_session(self._invoker, hash)

    async def terminate_other_sessions(self) -> bool:
        """Sign out everywhere but here."""
        return await methods.terminate_other_sessions(self._invoker)

    async def set_password(self, new: str, **options: Any) -> Any:
        """Set or change the account's second factor.

        Neither password leaves this machine. Set a recovery email while doing
        it: Telegram has no other way back into an account whose second factor
        is forgotten.
        """
        return await methods.set_password(self._invoker, new, **options)

    async def remove_password(self, current: str) -> Any:
        """Take the second factor off, which needs the current one."""
        return await methods.remove_password(self._invoker, current)

    async def has_password(self) -> bool:
        """Whether this account has a second factor at all."""
        return bool((await methods.current_password(self._invoker)).has_password)

    async def get_privacy(self, setting: str) -> Any:
        """What one privacy setting currently says.

        The settings by name are in methods.PRIVACY.
        """
        return await methods.privacy(self._invoker, setting)

    async def set_privacy(self, setting: str, allow: str = "contacts", **options: Any) -> Any:
        """Change one privacy setting, and optionally carve people out of it."""
        return await methods.set_privacy(self._invoker, setting, allow, **options)

    async def set_username(self, username: str) -> Any:
        """Claim a username, or give up the current one by passing nothing."""
        return await methods.set_username(self._invoker, username)

    async def check_username(self, username: str) -> bool:
        """Whether a username can be claimed, without claiming it."""
        return await methods.check_username(self._invoker, username)

    def _peer_of(self, message: Message) -> Target:
        """The chat a message is in, as something a call can be aimed at."""
        if message.chat is None:
            raise SunnygramError("this message does not say which chat it is in")
        return message.chat.id

    async def _send_attachment(
        self,
        peer: Target,
        media: Any,
        *,
        caption: str = "",
        parse_mode: str | None = "",
        entities: list[Any] | None = None,
        reply_to: int | None = None,
        topic: int | None = None,
        silent: bool = False,
        reply_markup: Any = None,
        schedule_date: datetime | int | None = None,
        origin: tuple[int, int] | None = None,
    ) -> Message:
        """Send a message carrying something that needed no upload."""
        body, found = self._styled(caption, parse_mode, entities)
        sent = await methods.send_media(
            self._invoker,
            peer,
            media,
            message=body,
            entities=found or None,
            reply_to=reply_to,
            topic=topic,
            silent=silent,
            reply_markup=reply_markup,
            schedule_date=schedule_date,
            renew=methods.renewing(self._invoker, origin),
            updates=self._updates,
        )
        return self._sent(sent)

    async def get_dialogs(
        self, *, limit: int = 100, batch: int = 100
    ) -> AsyncIterator[Dialog]:
        """Every conversation this account has, newest first."""
        async for page in methods.iter_dialog_pages(
            self._invoker, limit=limit, batch=batch
        ):
            users = {user.id: user for user in getattr(page, "users", ())}
            chats = {chat.id: chat for chat in getattr(page, "chats", ())}
            messages = {
                message.id: message for message in getattr(page, "messages", ())
            }
            for dialog in getattr(page, "dialogs", ()):
                wrapped = Dialog.from_raw(
                    dialog, users=users, chats=chats, messages=messages, client=self
                )
                if wrapped is not None:
                    yield wrapped

    async def get_participants(
        self, peer: Target, *, limit: int = 200, query: str = ""
    ) -> AsyncIterator[User]:
        """The people in a group or channel.

        A channel with many members only lets a client see so far down the
        list, which is Telegram's rule instead of this one: past a few
        thousand the answer stops whether or not more were asked for.
        """
        async for page in methods.iter_participant_pages(
            self._invoker, peer, limit=limit, query=query
        ):
            for user in getattr(page, "users", ()):
                wrapped = User.from_raw(user)
                if wrapped is not None:
                    yield wrapped

    async def get_topics(
        self, peer: Target, *, limit: int = 100, query: str = ""
    ) -> AsyncIterator[Topic]:
        """The topics in a forum, pinned ones first.

        A group that is not a forum has none, and says so, not
        answering with an empty list.
        """
        async for page in methods.iter_topic_pages(
            self._invoker, peer, limit=limit, query=query
        ):
            for topic in self._topics_on(page):
                yield topic

    async def get_topic(self, peer: Target, topic_id: int) -> Topic:
        """One topic, by id, which for a topic is the id of its first message."""
        page = await methods.topics_by_id(self._invoker, peer, [topic_id])
        found = self._topics_on(page)
        if not found:
            raise SunnygramError(f"there is no topic {topic_id} in this forum")
        return found[0]

    async def create_topic(self, peer: Target, title: str, **options: Any) -> Topic:
        """Open a topic, and answer with it.

        The topic's id is the id of the message this makes, which is what the
        answer is dug out of: there is no separate id space for topics.
        """
        answer = await methods.create_topic(self._invoker, peer, title, **options)
        await self._updates.feed(answer)
        opened = _topic_opened(answer)
        if opened is None:
            raise SunnygramError(
                "the server made the topic and did not say which message "
                "opened it, so there is no id to give back"
            )
        return await self.get_topic(peer, opened)

    async def edit_topic(self, peer: Target, topic_id: int, **options: Any) -> Any:
        """Change a topic's title, icon, or whether it is closed or hidden."""
        answer = await methods.edit_topic(self._invoker, peer, topic_id, **options)
        await self._updates.feed(answer)
        return answer

    async def close_topic(self, peer: Target, topic_id: int) -> Any:
        """Stop anybody but an administrator posting in a topic."""
        return await self.edit_topic(peer, topic_id, closed=True)

    async def reopen_topic(self, peer: Target, topic_id: int) -> Any:
        """Let people post in a topic again."""
        return await self.edit_topic(peer, topic_id, closed=False)

    async def pin_topic(
        self, peer: Target, topic_id: int, *, pinned: bool = True
    ) -> Any:
        """Hold a topic at the top of the forum, or let it go."""
        answer = await methods.pin_topic(
            self._invoker, peer, topic_id, pinned=pinned
        )
        await self._updates.feed(answer)
        return answer

    async def delete_topic(self, peer: Target, topic_id: int) -> int:
        """Delete a topic and everything in it, and say how much went."""
        return await methods.delete_topic(self._invoker, peer, topic_id)

    async def set_forum(
        self, peer: Target, enabled: bool = True, *, tabs: bool = False
    ) -> Any:
        """Turn topics on or off for a supergroup.

        Telegram refuses this for a group with too few members. Turning it off
        deletes nothing: everything that was in a topic moves back into the one
        conversation the group used to be.
        """
        answer = await methods.toggle_forum(
            self._invoker, peer, enabled, tabs=tabs
        )
        await self._updates.feed(answer)
        return answer

    def _topics_on(self, page: Any) -> list[Topic]:
        """Wrap the topics on one page, with what the page carried to name them."""
        users = {user.id: user for user in getattr(page, "users", ())}
        chats = {chat.id: chat for chat in getattr(page, "chats", ())}
        messages = {
            message.id: message for message in getattr(page, "messages", ())
        }
        found = [
            Topic.from_raw(
                topic, users=users, chats=chats, messages=messages, client=self
            )
            for topic in getattr(page, "topics", ())
        ]
        return [topic for topic in found if topic is not None]

    async def join_chat(self, peer: Target) -> None:
        """Join a channel or supergroup, by name or by invite link."""
        await self._updates.feed(await methods.join_chat(self._invoker, peer))

    async def leave_chat(self, peer: Target) -> None:
        """Leave a chat, whichever kind it is."""
        await self._updates.feed(await methods.leave_chat(self._invoker, peer))

    async def get_chat(self, peer: Target) -> Chat:
        """Everything Telegram will say about a chat, not only what a list shows."""
        answer = await methods.chat_info(self._invoker, peer)
        for chat in getattr(answer, "chats", ()):
            wrapped = Chat.from_raw(chat)
            if wrapped is not None:
                return wrapped
        raise SunnygramError("the server described a chat that was not in its answer")

    async def get_user(self, peer: Target) -> User:
        """Everything Telegram will say about one person."""
        answer = await methods.user_info(self._invoker, peer)
        for user in getattr(answer, "users", ()):
            wrapped = User.from_raw(user)
            if wrapped is not None:
                return wrapped
        raise SunnygramError("the server described a user that was not in its answer")

    async def get_contacts(self) -> list[User]:
        """This account's contact list."""
        answer = await methods.get_contacts(self._invoker)
        found = [User.from_raw(user) for user in getattr(answer, "users", ())]
        return [user for user in found if user is not None]

    async def block_user(self, peer: Target) -> bool:
        """Block someone, so they cannot write here."""
        return await methods.block_user(self._invoker, peer)

    async def unblock_user(self, peer: Target) -> bool:
        """Undo that."""
        return await methods.unblock_user(self._invoker, peer)

    async def update_profile(self, **fields: Any) -> User:
        """Change this account's own first_name, last_name or about.

        Only what is named changes. Leaving a field out leaves it alone;
        clearing one is passing an empty string.
        """
        wrapped = User.from_raw(await methods.update_profile(self._invoker, **fields))
        if wrapped is None:
            raise SunnygramError("the server did not say who we are now")
        self._me = wrapped
        return wrapped

    async def download_profile_photo(
        self, peer: Target = "me", **options: Any
    ) -> Any:
        """Fetch someone's profile picture, or a chat's.

        Their own copy is fetched instead of the small one carried around in
        answers, which is why this costs a call before it costs a download.
        """
        where = await self.resolve(peer)
        if isinstance(where, (types.InputPeerChannel, types.InputPeerChat)):
            answer = await methods.chat_info(self._invoker, where)
            photo = getattr(getattr(answer, "full_chat", None), "chat_photo", None)
        else:
            answer = await methods.user_info(self._invoker, where)
            photo = getattr(getattr(answer, "full_user", None), "profile_photo", None)
        if photo is None:
            raise SunnygramError("there is no profile photo to download")
        return await self.download(photo, **options)

    async def download(self, what: Any, **options: Any) -> Any:
        """Fetch a file, from a message, media, document, photo or reference.

        A file reference goes stale after an hour or so, and the cure is to
        fetch whatever carried the file again. Where what was passed says which
        message that was, which a message and a portable reference both do,
        that happens here without being asked for, so a reference stored last
        week still downloads.
        """
        if "refresh" not in options:
            found = methods.media_origin(what)
            if found is not None:
                options["refresh"] = self._refetching(found)
        return await download_file(self._invoker, what, **options)

    def _refetching(self, origin: tuple[int, int]) -> Any:
        """A way back to the message a file came from, for a stale reference."""
        where, message_id = origin

        async def refresh() -> Any:
            found = await self.get_messages(where, [message_id])
            if not found:
                raise SunnygramError(
                    f"this file reference expired and message {message_id} is "
                    "no longer there, so there is nothing to renew it with"
                )
            return found[0].raw

        return refresh

    async def upload(self, source: Any, **options: Any) -> Any:
        """Send a file up, and answer with the handle for attaching it."""
        return await upload_file(self._invoker, source, **options)

    async def promote(
        self,
        peer: Target,
        user: Target,
        rights: AdminRights | None = None,
        *,
        title: str = "",
    ) -> None:
        """Make someone an administrator, with the powers named and no others.

        Saying nothing about the rights grants none of them, which is the same
        thing demote does and is the safe way for a default to point.
        """
        await self._updates.feed(
            await methods.promote(self._invoker, peer, user, rights, title=title)
        )

    async def demote(self, peer: Target, user: Target) -> None:
        """Take every power back, leaving them an ordinary member."""
        await self._updates.feed(await methods.demote(self._invoker, peer, user))

    async def restrict(
        self, peer: Target, user: Target, permissions: Permissions, *, until: int = 0
    ) -> None:
        """Limit what one person may do here, until a unix time or forever."""
        await self._updates.feed(
            await methods.restrict_member(
                self._invoker, peer, user, permissions, until=until
            )
        )

    async def ban(self, peer: Target, user: Target, *, until: int = 0) -> None:
        """Remove someone and keep them out."""
        await self._updates.feed(
            await methods.ban_member(self._invoker, peer, user, until=until)
        )

    async def unban(self, peer: Target, user: Target) -> None:
        """Lift every restriction, so they may come back if they want to."""
        await self._updates.feed(
            await methods.unban_member(self._invoker, peer, user)
        )

    async def kick(self, peer: Target, user: Target) -> None:
        """Remove someone without keeping them out, so they may rejoin."""
        await self._updates.feed(
            await methods.kick_member(self._invoker, peer, user)
        )

    async def get_permissions(self, peer: Target, user: Target) -> Permissions:
        """What one person may do here, as the positive set instead of the raw one.

        An administrator comes back allowed everything, since their powers are
        held separately and no restriction applies to them.
        """
        found = await methods.get_participant(self._invoker, peer, user)
        standing = getattr(found, "participant", None)
        restriction = getattr(standing, "banned_rights", None)
        if restriction is None:
            return Permissions.everything()
        return Permissions.from_raw(restriction)

    async def get_member(self, peer: Target, user: Target) -> Member | None:
        """One person's whole standing here, or nothing if they are not in it.

        This is the question behind most permission checks, and asking it in
        one call beats inferring it from rights: `member.is_admin` counts the
        creator, which testing for admin alone does not.

        Both kinds of chat answer. A basic group has no call for one member, so
        the membership is fetched and the one asked about picked out of it.
        """
        where = await resolve(self._invoker, peer)
        found = await methods.get_member(self._invoker, where, user)
        if found is None:
            return None
        return Member.from_raw(found, chat_id=_peer_id(where))

    async def get_admin_rights(self, peer: Target, user: Target) -> AdminRights:
        """What powers one person holds here, or none if they hold none."""
        found = await methods.get_participant(self._invoker, peer, user)
        standing = getattr(found, "participant", None)
        if isinstance(standing, types.ChannelParticipantCreator):
            return AdminRights.everything()
        powers = getattr(standing, "admin_rights", None)
        return AdminRights() if powers is None else AdminRights.from_raw(powers)

    async def set_chat_title(self, peer: Target, title: str) -> None:
        """Rename a chat, whichever kind it is."""
        await self._updates.feed(
            await methods.set_chat_title(self._invoker, peer, title)
        )

    async def set_chat_photo(self, peer: Target, photo: Any = None) -> None:
        """Change a chat's picture, or remove it by passing nothing."""
        await self._updates.feed(
            await methods.set_chat_photo(self._invoker, peer, photo)
        )

    async def set_chat_description(self, peer: Target, about: str) -> bool:
        """Set the description shown above a chat."""
        return bool(
            await methods.set_chat_description(self._invoker, peer, about)
        )

    async def set_chat_permissions(
        self, peer: Target, permissions: Permissions
    ) -> None:
        """What everybody who is not an administrator may do here."""
        await self._updates.feed(
            await methods.set_chat_permissions(self._invoker, peer, permissions)
        )

    async def set_slow_mode(self, peer: Target, seconds: int) -> None:
        """How long a member waits between messages, or zero for no wait."""
        await self._updates.feed(
            await methods.set_slow_mode(self._invoker, peer, seconds)
        )

    async def create_group(self, title: str, users: list[Target]) -> Chat:
        """Start a basic group with some people in it."""
        return self._chat_out_of(
            await methods.create_group(self._invoker, title, users)
        )

    async def create_channel(
        self,
        title: str,
        *,
        about: str = "",
        megagroup: bool = False,
        forum: bool = False,
    ) -> Chat:
        """Start a broadcast channel, or a supergroup if megagroup is asked for."""
        return self._chat_out_of(
            await methods.create_channel(
                self._invoker, title, about=about, megagroup=megagroup, forum=forum
            )
        )

    async def delete_chat(self, peer: Target) -> None:
        """Delete a chat for everybody in it, which only its owner can do."""
        await self._updates.feed(await methods.delete_chat(self._invoker, peer))

    async def add_chat_members(
        self, peer: Target, users: list[Target], *, forward_limit: int = 0
    ) -> None:
        """Put people into a chat directly, rather than handing them a link."""
        await self._updates.feed(
            await methods.add_chat_members(
                self._invoker, peer, users, forward_limit=forward_limit
            )
        )

    async def export_invite_link(self, peer: Target, **options: Any) -> str:
        """Make a new invite link and hand back the link itself.

        Everything else about it is on the raw answer, which is what the
        methods layer hands over; this is the part programs want.
        """
        made = await methods.export_invite_link(self._invoker, peer, **options)
        link = getattr(made, "link", None)
        if link is None:
            raise SunnygramError("the server made an invite with no link in it")
        return str(link)

    async def revoke_invite_link(self, peer: Target, link: str) -> Any:
        """Kill a link, so it admits no one else."""
        return await methods.revoke_invite_link(self._invoker, peer, link)

    async def get_invite_links(
        self, peer: Target, *, admin: Target = "me", revoked: bool = False
    ) -> list[Any]:
        """The links one administrator has made here."""
        found = await methods.invite_links(
            self._invoker, peer, admin=admin, revoked=revoked
        )
        return list(getattr(found, "invites", ()))

    async def approve_join_request(
        self, peer: Target, user: Target, *, approved: bool = True
    ) -> None:
        """Let someone in who asked to join, or turn them down."""
        await self._updates.feed(
            await methods.approve_join_request(
                self._invoker, peer, user, approved=approved
            )
        )

    async def approve_all_join_requests(
        self, peer: Target, *, approved: bool = True, link: str = ""
    ) -> None:
        """Answer everybody waiting to join at once.

        One call instead of one per person, which is the difference between
        emptying a week's queue and being rate limited halfway through it.
        Naming an invite link answers only the people who came in through it.
        """
        await self._updates.feed(
            await methods.approve_all_join_requests(
                self._invoker, peer, approved=approved, link=link
            )
        )

    async def get_admin_log(
        self, peer: Target, *, limit: int = 100, query: str = ""
    ) -> AsyncIterator[Any]:
        """What administrators have done here, newest first.

        The entries are raw: there are several dozen kinds of them and they
        have nothing in common but an id, a date and who did it, so wrapping
        them would hide more than it explained.
        """
        async for page in methods.iter_admin_log(
            self._invoker, peer, limit=limit, query=query
        ):
            for event in getattr(page, "events", ()):
                yield event

    def _chat_out_of(self, answer: Any) -> Chat:
        """The chat a call has just made, out of the updates it answered with."""
        for chat in getattr(answer, "chats", ()):
            wrapped = Chat.from_raw(chat)
            if wrapped is not None:
                return wrapped
        raise SunnygramError("the server made a chat and did not say which")

    def wrap_message(
        self,
        raw: Any,
        *,
        users: dict[int, Any] | None = None,
        chats: dict[int, Any] | None = None,
        replies: dict[int, Any] | None = None,
    ) -> Message | None:
        """Turn a raw message into one bound to this client, and remember it.

        What the dispatcher calls on the way to a handler, and what to call by
        hand for a message pulled off a raw update. Two things happen here that
        Message.from_raw cannot do on its own: the message being replied to is
        looked up among the ones this client has lately seen, and this message
        is written down so that the next reply to it costs nothing either.
        """
        message = Message.from_raw(
            raw, users=users, chats=chats, replies=replies, client=self
        )
        if message is None:
            return None
        if message.reply_to_id is not None and (
            message.reply_to_message is None or message.reply_to_message.partial
        ):
            known = self._recent.get(
                self._reply_chat(message), message.reply_to_id
            )
            if known is not None:
                message.reply_to_message = known
        self._recent.remember(message)
        return message

    @property
    def recent(self) -> RecentMessages:
        """The messages lately seen or sent, which answers a reply."""
        return self._recent

    def file_ref(self, what: Any, **options: Any) -> str:
        """A file as one string that can be written down and used later.

        Takes a message, the media off one, a document or a photo. What comes
        back can be handed to send_media or download tomorrow, from another
        process, out of a database column.
        """
        from .files import file_ref

        return file_ref(what, **options)

    def _reply_chat(self, message: Message) -> int:
        """Which chat holds the message being answered, which is usually this one.

        Usually, not always: a quoted reply can answer a message in another
        chat, and looking that one up here would find whatever else has the
        same id.
        """
        elsewhere = getattr(
            getattr(message.raw, "reply_to", None), "reply_to_peer_id", None
        )
        if elsewhere is not None:
            return _peer_id(elsewhere)
        return message.chat_id or 0

    def _sent(self, raw: Any) -> Message:
        """The message a send answered with, wrapped and written down."""
        wrapped = self.wrap_message(raw)
        if wrapped is None:
            raise SunnygramError(
                "the server answered with something that is not a message"
            )
        return wrapped

    def _messages_in(self, answer: Any) -> list[Message]:
        """The messages in an answer, wrapped, with what came alongside them.

        The messages are handed their own page as replies, so that a reply to
        something else on the same page is tied to it here. A page of history
        usually holds both halves of a conversation, and pairing them up is a
        dict lookup instead of a call.
        """
        users = {user.id: user for user in getattr(answer, "users", ())}
        chats = {chat.id: chat for chat in getattr(answer, "chats", ())}
        raw = list(getattr(answer, "messages", ()))
        replies = {one.id: one for one in raw if hasattr(one, "id")}
        found = [
            self.wrap_message(one, users=users, chats=chats, replies=replies)
            for one in raw
        ]
        return [message for message in found if message is not None]

    def _decorator(
        self, kind: Kind, filters: filters_module.Filter | None, group: int
    ) -> Callable[[Callback], Callback]:
        def register(callback: Callback) -> Callback:
            self.add_handler(callback, kind=kind, filters=filters, group=group)
            return callback

        return register

    def _styling(
        self, parse_mode: str | None | Any
    ) -> Callable[[str], tuple[str, list[Any]]]:
        """How to style text, for a call carrying several pieces of it.

        An inline answer has a message per result and they are all parsed the
        same way, so the mode is settled once here and handed down, not
        looked up again for every result.
        """

        def style(text: str) -> tuple[str, list[Any]]:
            return self._styled(text, parse_mode, None)

        return style

    def _styled(
        self, text: str, parse_mode: str | None | Any, entities: list[Any] | None
    ) -> tuple[str, list[Any]]:
        """The text as it goes out, and what to style in it.

        The empty string as a mode means the client's own, which is how a
        caller says nothing at all and how another says None to mean plainly.
        """
        if entities is not None:
            return text, list(entities)
        mode = self._parse_mode if parse_mode == "" else parse_mode
        return parse_text(text, mode)

    def _message_out_of(
        self,
        answer: Any,
        text: str,
        entities: list[Any],
        *,
        peer: Any,
        reply_to: int | None = None,
    ) -> Message:
        """The message a send or an edit answered with, wrapped.

        The peer is the one the call was addressed to, and it is required
        instead of optional because of what happens when the answer carries no
        message. Telegram answers a send in a private chat with
        updateShortSentMessage, which says the id and the date and nothing
        else, and a message assembled from that alone does not know which chat
        it is in. That is not a cosmetic gap: it is what edit, delete and reply
        all need, so a bot sending a status line and editing it as it works
        would get an error on the edit and never on the send.
        """
        users = {user.id: user for user in getattr(answer, "users", ())}
        chats = {chat.id: chat for chat in getattr(answer, "chats", ())}
        for update in getattr(answer, "updates", ()):
            found = getattr(update, "message", None)
            wrapped = self.wrap_message(found, users=users, chats=chats)
            if wrapped is not None:
                return wrapped
        # The shorthand, and the answer that named no message at all. We know
        # the rest: we wrote it, and we know where we sent it. Rebuilt by the
        # same helper the methods layer uses, so there is one account of what a
        # shorthand stands for instead of two that can drift apart.
        rebuilt = methods.rebuild_sent(
            self._invoker, answer, peer, text, reply_to, entities or None
        )
        wrapped = self.wrap_message(rebuilt)
        if wrapped is None:
            raise SunnygramError(
                "the server answered with something that is not a message"
            )
        return wrapped

    async def _deliver(self) -> None:
        """Take updates off the stream and offer them to the handlers."""
        while True:
            event: Event = await self._updates.events.get()
            try:
                await self._dispatcher.feed(self, event)
            except StopPropagation:
                continue


def _storage_for(session: str | os.PathLike[str] | Storage) -> Storage:
    """What to keep the session in, from however it was named.

    The rule itself is in `storage`, because `migrate.adopt_session` names a
    session the same way and the two have to land on the same file.
    """
    return storage_for(session)


def _random_id() -> int:
    from .methods import random_id

    return random_id()


def _as_result(
    result: Any, style: Callable[[str], tuple[str, list[Any]]]
) -> Any:
    """One inline result as the protocol spells it, however it was written.

    A raw constructor goes through untouched, which is the escape hatch for the
    handful of result shapes the factories do not build.
    """
    if isinstance(result, InlineResult):
        return result.to_raw(style)
    return result


def _peer_id(where: Any) -> int:
    """The bare id out of an input peer or a peer, whichever kind it is.

    Both spellings name their id field the same way, which is why one function
    reads either.
    """
    for field in ("channel_id", "chat_id", "user_id"):
        found = getattr(where, field, None)
        if isinstance(found, int):
            return found
    return 0


def _topic_opened(answer: Any) -> int | None:
    """The id of the topic a createForumTopic answer just made.

    A topic is the message that opens it, so what comes back is an ordinary
    sent message and its id is the topic's. The server may say so in either of
    two ways, so both are looked at, not one being assumed.
    """
    for update in getattr(answer, "updates", ()):
        if isinstance(update, types.UpdateMessageID):
            return update.id
        message = getattr(update, "message", None)
        if isinstance(message, types.Message):
            return message.id
    return None
