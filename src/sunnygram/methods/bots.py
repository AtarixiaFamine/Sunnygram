# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Both sides of a conversation with a bot.

Most of this is the side a user account is on, and it is most of why anybody
writes a userbot: pressing a bot's buttons, asking it for inline results, and
starting it with a parameter. A bot's own API has no calls for any of this,
because a bot is on the other side of it.

Pressing a button is the awkward one, because a button is not addressed by
anything a caller naturally has. The message carries a keyboard, the keyboard is
rows of buttons, and the one that does anything when pressed carries opaque data
the bot gave it. So the useful call is not "press button 3" but "press the one
that says Yes", and finding it is what this module spends its length on.

The rest is the other side, for a session signed in with a bot token: answering
a press, publishing the command menu, and editing a message that came out of an
inline query. That last one is the only call here that does not go to the
account's own datacenter. An inline message belongs to no chat, it is named by
an opaque id that one datacenter issued, and editing it means talking to that
datacenter rather than to home.
"""

from __future__ import annotations

from typing import Any

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import base, functions, types
from ..types.buttons import buttons_of
from ..types.inline import MAX_RESULTS
from ..updates import UpdateManager
from .messages import random_id, reply_header

__all__ = [
    "answer_callback",
    "answer_inline_query",
    "click_button",
    "delete_bot_commands",
    "edit_inline_message",
    "find_button",
    "get_bot_commands",
    "inline_results",
    "keyboard_of",
    "send_inline_result",
    "set_bot_commands",
    "start_bot",
]


def keyboard_of(message: Any) -> list[list[Any]]:
    """The rows of buttons under a message, or nothing if it has none.

    The same thing Message.buttons answers, kept here because this module is
    where a program that holds an invoker instead of a client reaches it.
    """
    return buttons_of(message)


def find_button(message: Any, which: str | int | tuple[int, int]) -> Any:
    """The button a caller means, however they said which one.

    A string matches the label, which is how anybody actually refers to a
    button. A number counts through them in reading order, and a pair is the
    row and the position in it.
    """
    rows = keyboard_of(message)
    if not rows:
        raise SunnygramError("this message has no buttons under it")

    if isinstance(which, tuple):
        row, column = which
        try:
            return rows[row][column]
        except IndexError:
            raise SunnygramError(
                f"there is no button at row {row}, position {column}"
            ) from None

    flat = [button for row in rows for button in row]
    if isinstance(which, int):
        try:
            return flat[which]
        except IndexError:
            raise SunnygramError(
                f"there are {len(flat)} buttons and {which} is not one of them"
            ) from None

    for button in flat:
        if getattr(button, "text", None) == which:
            return button
    labels = ", ".join(repr(getattr(button, "text", "")) for button in flat)
    raise SunnygramError(f"no button says {which!r}; there is {labels}")


async def click_button(
    invoker: Invoker,
    peer: Target,
    message: Any,
    which: str | int | tuple[int, int] = 0,
    *,
    password: str = "",
) -> Any:
    """Press a button under a message and hand back what the bot answered.

    The answer is what a person would see: usually a short notice, sometimes an
    instruction to open a url, and sometimes nothing at all because the bot
    replied by editing the message instead. That arrives as an update rather
    than here.

    A button asking for the account password is refused instead of half
    handled, since sending one means the SRP dance and doing that quietly on a
    button press is not something a library should decide for someone.
    """
    button = find_button(message, which)
    if isinstance(button, types.KeyboardButtonUrl):
        raise SunnygramError(
            f"{button.text!r} is a link rather than a button that does "
            f"something here; it opens {button.url}"
        )
    if not isinstance(button, (types.KeyboardButtonCallback, types.KeyboardButtonGame)):
        raise SunnygramError(
            f"{type(button).__name__} is not a button this can press"
        )
    if getattr(button, "requires_password", False) and not password:
        raise SunnygramError(
            f"{button.text!r} asks for the account password, so pass one"
        )

    return await invoker.invoke(
        functions.messages.GetBotCallbackAnswer(
            peer=await resolve(invoker, peer),
            msg_id=_message_id(message),
            data=getattr(button, "data", None),
            game=isinstance(button, types.KeyboardButtonGame),
        )
    )


async def inline_results(
    invoker: Invoker,
    bot: Target,
    query: str = "",
    *,
    peer: Target = "me",
    offset: str = "",
) -> Any:
    """Ask a bot for its inline results, the way typing @bot query does.

    The chat matters even though nothing is being sent to it yet: bots are told
    where the query came from and are allowed to answer differently in a group
    than in a private chat. Passing "me" is the honest answer when there is no
    particular chat in mind.
    """
    return await invoker.invoke(
        functions.messages.GetInlineBotResults(
            bot=as_user(await resolve(invoker, bot)),
            peer=await resolve(invoker, peer),
            query=query,
            offset=offset,
        )
    )


async def send_inline_result(
    invoker: Invoker,
    peer: Target,
    query_id: int,
    result_id: str,
    *,
    reply_to: int | None = None,
    topic: int | None = None,
    silent: bool = False,
    hide_via: bool = False,
    updates: UpdateManager | None = None,
) -> Any:
    """Send one of the results a bot answered with.

    The pair of ids comes from inline_results and belongs to that one answer:
    the query id names the answer and the result id names which of its results.
    They go stale, so this is the call that follows the other, not one
    to hold onto.

    hide_via drops the "via @bot" line, which Telegram only allows for some
    bots and refuses for the rest.
    """
    answer = await invoker.invoke(
        functions.messages.SendInlineBotResult(
            peer=await resolve(invoker, peer),
            query_id=query_id,
            id=result_id,
            random_id=random_id(),
            hide_via=hide_via,
            silent=silent,
            reply_to=reply_header(reply_to, topic),
        )
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def start_bot(
    invoker: Invoker,
    bot: Target,
    *,
    parameter: str = "",
    peer: Target | None = None,
    updates: UpdateManager | None = None,
) -> Any:
    """Press start on a bot, with the parameter a deep link would have carried.

    This is what the button under a fresh bot chat does, and what the payload
    in a t.me/bot?start=xyz link becomes. Naming a group starts the bot there
    instead, which is how a bot gets added to one with a parameter attached.
    """
    where = await resolve(invoker, bot)
    answer = await invoker.invoke(
        functions.messages.StartBot(
            bot=as_user(where),
            peer=where if peer is None else await resolve(invoker, peer),
            random_id=random_id(),
            start_param=parameter,
        )
    )
    if updates is not None:
        await updates.feed(answer)
    return answer


async def answer_callback(
    invoker: Invoker,
    query_id: int,
    text: str = "",
    *,
    alert: bool = False,
    url: str | None = None,
    cache_time: int = 0,
) -> bool:
    """Answer a button press, which stops the button spinning.

    Telegram holds the press open until the bot says something about it, and
    every client draws that as a spinner on the button. So this is not optional
    politeness: a bot that answers by editing the message still has to answer
    the press, with nothing in it, or the button spins until it times out.

    text puts a notice along the top of the screen and alert makes it a box
    they have to dismiss. url opens something, and Telegram only allows it for
    a game or for the bot's own deep link. cache_time lets the client answer
    the same press itself for that many seconds, which is worth setting when
    the answer cannot change.
    """
    return bool(
        await invoker.invoke(
            functions.messages.SetBotCallbackAnswer(
                query_id=query_id,
                message=text or None,
                alert=alert,
                url=url,
                cache_time=cache_time,
            )
        )
    )


async def answer_inline_query(
    invoker: Invoker,
    query_id: int,
    results: list[base.InputBotInlineResult],
    *,
    cache_time: int = 300,
    gallery: bool = False,
    private: bool = False,
    next_offset: str = "",
    switch_pm: str = "",
    start_parameter: str = "",
) -> bool:
    """Answer an inline query with the things this bot is offering.

    The same rule the callback query has, for the same reason: Telegram holds
    the query open until the bot answers, and until then the person sees a
    panel that never finishes loading. An answer with no results in it is a
    complete answer and is what a bot sends when it has nothing for that query.

    cache_time lets the clients reuse this answer for that many seconds without
    asking again, which is worth turning down to nothing when a result depends
    on the moment. private says the answer was built for this one person and
    must never be shown to anybody else, which matters the moment a result
    depends on who asked. gallery draws them as a grid instead of a list.

    next_offset is the cursor: hand back where this page ended and the client
    asks for the rest by scrolling, arriving with that string as the query's
    offset. Leaving it empty means this is everything.

    switch_pm puts a button above the results leading into the bot's own chat,
    carrying start_parameter as the deep link payload. It is how a bot that
    needs setting up first says so, instead of answering with an apology
    no one can act on.
    """
    if len(results) > MAX_RESULTS:
        raise ValueError(
            f"Telegram takes at most {MAX_RESULTS} results in one answer and "
            f"this has {len(results)}. Send the first page and hand back a "
            f"next_offset for the rest"
        )
    return bool(
        await invoker.invoke(
            functions.messages.SetInlineBotResults(
                query_id=query_id,
                results=results,
                cache_time=cache_time,
                gallery=gallery,
                private=private,
                next_offset=next_offset or None,
                switch_pm=(
                    types.InlineBotSwitchPM(
                        text=switch_pm, start_param=start_parameter
                    )
                    if switch_pm
                    else None
                ),
            )
        )
    )


async def edit_inline_message(
    invoker: Invoker,
    inline_id: Any,
    message: str | None = None,
    *,
    entities: Any = None,
    media: Any = None,
    reply_markup: Any = None,
    no_webpage: bool = False,
) -> bool:
    """Rewrite a message that an inline query produced.

    The id comes off a callback query and names a message with no chat behind
    it, which is why this is a separate call from editing an ordinary one. It
    also names the datacenter that issued it, and the call has to go there:
    home knows nothing about it.

    The answer is whether the edit went through. There is no message to hand
    back, because there is no chat to fetch one from.
    """
    where = getattr(inline_id, "dc_id", None)
    if not isinstance(where, int):
        raise SunnygramError(
            f"{type(inline_id).__name__} is not an inline message id; one "
            "comes off a callback query and says which datacenter issued it"
        )
    return bool(
        await invoker.invoke(
            functions.messages.EditInlineBotMessage(
                id=inline_id,
                message=message,
                entities=entities or None,
                media=media,
                reply_markup=reply_markup,
                no_webpage=no_webpage,
            ),
            dc_id=where,
        )
    )


async def set_bot_commands(
    invoker: Invoker,
    commands: list[tuple[str, str]],
    *,
    lang_code: str = "",
    scope: Any = None,
) -> Any:
    """Publish the command menu, which is the slash list clients autocomplete.

    This is the one thing here a bot does about itself, not something a
    user account does to a bot, so it only works signed in with a bot token.

    The scope says where the menu applies. Leaving it out means everywhere,
    which almost every bot wants; the alternatives are Telegram's
    BotCommandScope constructors, and they exist for a bot that shows admins a
    longer list than everybody else.
    """
    return await invoker.invoke(
        functions.bots.SetBotCommands(
            scope=scope or types.BotCommandScopeDefault(),
            lang_code=lang_code,
            commands=[
                types.BotCommand(command=name.lstrip("/"), description=description)
                for name, description in commands
            ],
        )
    )


async def get_bot_commands(
    invoker: Invoker, *, lang_code: str = "", scope: Any = None
) -> list[tuple[str, str]]:
    """The command menu as it stands, in the shape set_bot_commands takes."""
    answer = await invoker.invoke(
        functions.bots.GetBotCommands(
            scope=scope or types.BotCommandScopeDefault(), lang_code=lang_code
        )
    )
    return [(one.command, one.description) for one in answer]


async def delete_bot_commands(
    invoker: Invoker, *, lang_code: str = "", scope: Any = None
) -> Any:
    """Take the command menu away again, for this scope and language."""
    return await invoker.invoke(
        functions.bots.ResetBotCommands(
            scope=scope or types.BotCommandScopeDefault(), lang_code=lang_code
        )
    )


def _message_id(message: Any) -> int:
    found = getattr(message, "id", None)
    if not isinstance(found, int):
        raise SunnygramError("a button belongs to a message, and this has no id")
    return found
