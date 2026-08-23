# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Handlers written where there is no client yet, and loaded when there is.

The decorators are methods on a client: `@app.on_message(...)` needs `app`, and
a module written to be imported by a loader does not have one.

So the intent is recorded instead. A decorator here writes what the function
asked for onto the function, and `Client.load_plugins` walks a package, imports
it, and registers everything it finds against a real client:

    # plugins/greet.py
    from sunnygram import filters, plugins

    @plugins.on_message(filters.command("hello"))
    async def greet(client, message):
        await message.reply("hello yourself")

    # main.py
    app = Client("my.session", api_id=API_ID, api_hash=API_HASH)
    app.load_plugins("plugins")
    app.run()

The mark goes on the function, not the decorator on the class. Hanging it off
the client reads well but means the decorator cannot be typed as what it is,
since it has to accept a filter where a client belongs.

Two things it will not do. It will not import a plugin twice and register
everything again, since a handler registered twice runs twice and the second is
invisible in the source. And it will not swallow a plugin that fails to import
(rule C3): the program would start, look healthy, and ignore people.
"""

from __future__ import annotations

import importlib
import logging
import os
import pkgutil
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from .dispatcher import Callback, Kind
from .errors import SunnygramError
from .filters import Filter

__all__ = [
    "MARK",
    "Registration",
    "load_into",
    "on",
    "on_album",
    "on_blocked",
    "on_callback_query",
    "on_chat_member",
    "on_chosen_result",
    "on_deleted",
    "on_edited",
    "on_inline_query",
    "on_join_request",
    "on_message",
    "on_poll",
    "on_poll_vote",
    "on_pre_checkout",
    "on_raw",
    "on_reaction",
    "on_scheduled",
    "on_shipping",
    "on_status",
    "on_stopped",
    "on_story",
    "on_typing",
    "registrations",
]

_log = logging.getLogger(__name__)

# Where a decorated function keeps what it asked for. An attribute on the
# function instead of a registry keyed by name, so a module imported and never
# loaded costs nothing and leaves nothing behind, and so two plugins with a
# function of the same name are two functions, not one quietly replacing
# the other.
MARK = "__sunnygram_plugin__"


@dataclass(frozen=True, slots=True)
class Registration:
    """One handler a plugin asked for, before there is a client to attach it to."""

    kind: Kind
    filters: Filter | None
    group: int


def on(
    kind: Kind, filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Record that this function wants a kind of update. The general form.

    The named decorators below are this with the kind filled in, and they are
    the ones worth using: a kind spelled wrong here is a handler that never
    runs and never complains, and a named one cannot be spelled wrong.
    """

    def mark(callback: Callback) -> Callback:
        # Appended instead of replaced, so one function can answer two kinds.
        # Stacking two of these is the obvious thing to try, and the outer one
        # quietly winning would be a surprise found only at runtime.
        asked: list[Registration] = list(getattr(callback, MARK, ()))
        asked.append(Registration(kind=kind, filters=filters, group=group))
        setattr(callback, MARK, asked)
        return callback

    return mark


def registrations(callback: Any) -> tuple[Registration, ...]:
    """What this function asked for, or nothing if it is not a plugin handler."""
    return tuple(getattr(callback, MARK, ()))


def load_into(
    client: Any,
    where: str | os.PathLike[str] | ModuleType,
    *,
    include: tuple[str, ...] | None = None,
    exclude: tuple[str, ...] = (),
) -> int:
    """Import a package of plugins and register what they asked for.

    `Client.load_plugins` is the way to call this. Returns how many handlers
    were registered, which is worth reading: zero out of a package that has
    plugins in it means they were written without the decorators, and nothing
    else in the program would ever say so.

    include and exclude name modules, without the package in front. They are
    there for the case that actually happens, which is one plugin being turned
    off while someone works on it, instead of for building a plugin manager.
    """
    added = 0
    loaded = 0
    for module in _modules_in(where):
        name = module.__name__.rsplit(".", 1)[-1]
        if include is not None and name not in include:
            continue
        if name in exclude:
            continue
        loaded += 1
        for handler in _handlers_in(module):
            for asked in registrations(handler):
                client.add_handler(
                    handler, kind=asked.kind, filters=asked.filters, group=asked.group
                )
                added += 1

    _log.info("loaded %d plugin modules, registering %d handlers", loaded, added)
    if loaded and not added:
        # Not an error: a package of helpers with no handlers in it is a
        # legitimate thing to point this at. But it is nearly always a mistake,
        # and it is an invisible one, so it gets said, not left.
        _log.warning(
            "%d plugin modules were imported and not one handler was found. A "
            "plugin registers by being decorated with sunnygram.plugins, not by "
            "being in the package",
            loaded,
        )
    return added


def _modules_in(where: str | os.PathLike[str] | ModuleType) -> Iterator[ModuleType]:
    """Every module in a plugin package, imported, in a settled order."""
    package = where if isinstance(where, ModuleType) else _import_package(where)
    paths = getattr(package, "__path__", None)
    if paths is None:
        # One module instead of a package. Pointing at a single file is a
        # reasonable thing to do and there is nothing to walk.
        yield package
        return

    # Sorted, because the order handlers are registered in is the order they
    # run in within a group, and the order a filesystem happens to return is
    # not a decision anybody made.
    for found in sorted(pkgutil.iter_modules(list(paths)), key=lambda one: one.name):
        if found.name.startswith("_"):
            continue
        yield importlib.import_module(f"{package.__name__}.{found.name}")


def _import_package(where: str | os.PathLike[str]) -> ModuleType:
    """Import a plugin package, named either as a module path or a directory."""
    named = str(where).replace("/", ".").replace("\\", ".").strip(".")
    try:
        return importlib.import_module(named)
    except ImportError as unimportable:
        if not Path(where).exists():
            raise SunnygramError(
                f"no plugins at {where!r}: it is neither an importable module "
                "nor a directory that exists"
            ) from unimportable
        raise SunnygramError(
            f"{where!r} exists but is not an importable package. Give it an "
            "__init__.py and make sure it is on the path, so that a traceback "
            "from inside a plugin says which plugin it came from"
        ) from unimportable


def _handlers_in(module: ModuleType) -> Iterator[Callback]:
    """The decorated functions in a module, in the order they were written."""
    for value in vars(module).values():
        if callable(value) and getattr(value, MARK, None):
            yield value


def on_raw(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle every update exactly as it arrived, before anything wraps it."""
    return on("raw", filters, group=group)


def on_message(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle new messages, on the ones the filter says yes to."""
    return on("message", filters, group=group)


def on_edited(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle messages that were changed after they were sent."""
    return on("edited", filters, group=group)


def on_scheduled(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle messages queued for later instead of sent."""
    return on("scheduled", filters, group=group)


def on_album(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a group of media sent together, once all of it has arrived."""
    return on("album", filters, group=group)


def on_callback_query(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a press of an inline button."""
    return on("callback", filters, group=group)


def on_inline_query(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle someone typing this account's name in another chat."""
    return on("inline_query", filters, group=group)


def on_chosen_result(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle an inline result being picked."""
    return on("chosen_result", filters, group=group)


def on_chat_member(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle someone joining, leaving, or being given rights."""
    return on("chat_member", filters, group=group)


def on_join_request(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a request to join a chat that approves people."""
    return on("join_request", filters, group=group)


def on_deleted(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle messages being deleted."""
    return on("deleted", filters, group=group)


def on_reaction(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a reaction being put on or taken off a message."""
    return on("reaction", filters, group=group)


def on_poll(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a poll's results changing."""
    return on("poll", filters, group=group)


def on_poll_vote(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle one person voting in a poll."""
    return on("poll_vote", filters, group=group)


def on_shipping(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle Telegram asking what delivery costs for an address."""
    return on("shipping", filters, group=group)


def on_pre_checkout(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle the last question before a customer is charged."""
    return on("pre_checkout", filters, group=group)


def on_story(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a story being posted, changed or taken down."""
    return on("story", filters, group=group)


def on_status(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle someone's last-seen changing."""
    return on("status", filters, group=group)


def on_typing(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle someone typing, or recording, or uploading."""
    return on("typing", filters, group=group)


def on_blocked(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle this account being blocked or unblocked by someone."""
    return on("blocked", filters, group=group)


def on_stopped(
    filters: Filter | None = None, *, group: int = 0
) -> Callable[[Callback], Callback]:
    """Handle a user stopping or restarting this bot."""
    return on("stopped", filters, group=group)
