# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Buttons, and the keyboards they sit in.

On the wire a keyboard is rows of constructors inside a markup inside a send
call. In a program it is a list of things to press. This is that translation,
and it spends its length on one distinction Telegram makes and no one remembers:
there are two kinds of keyboard and a button belongs to exactly one of them.

An inline keyboard hangs under a message and its buttons do something when
pressed: they call the bot back, open a link, start an inline query. A reply
keyboard replaces the other side's suggestions above the text field and its
buttons only ever send their own label, or ask for a phone number or a location.
Mixing the two is not a layout mistake to be tidied up, it is two different
fields on two different constructors, so a keyboard built out of both says so
here rather than being refused on the wire.

Which kind is being built is worked out instead of asked for, because the
buttons already say. Nothing but a callback belongs inline and nothing but a
plain label belongs above the text field, so the caller writes the buttons they
mean and the markup follows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..raw import types

if TYPE_CHECKING:
    from ..raw import base

__all__ = [
    "Button",
    "buttons_of",
    "force_reply",
    "keyboard",
    "remove_keyboard",
]

# What Telegram will carry as a callback payload. It is small on purpose: the
# data travels back on every press, so it is a key into whatever the program
# knows instead of the thing itself.
CALLBACK_DATA_LIMIT = 64

# Buttons that only work under a message, and buttons that only work above the
# text field. Everything here is one or the other, which lets a
# keyboard be built without being told which kind it is.
_INLINE_ONLY = (
    types.KeyboardButtonCallback,
    types.KeyboardButtonUrl,
    types.KeyboardButtonUrlAuth,
    types.KeyboardButtonSwitchInline,
    types.KeyboardButtonGame,
    types.KeyboardButtonBuy,
    types.KeyboardButtonUserProfile,
    types.KeyboardButtonWebView,
    types.KeyboardButtonCopy,
)
_REPLY_ONLY = (
    types.KeyboardButton,
    types.KeyboardButtonRequestPhone,
    types.KeyboardButtonRequestGeoLocation,
    types.KeyboardButtonRequestPoll,
    types.KeyboardButtonRequestPeer,
    types.KeyboardButtonSimpleWebView,
)


class Button:
    """Every kind of button, one call each.

    Nothing here talks to the network and nothing holds state, so a button can
    be built once and reused for as long as the program runs.
    """

    __slots__ = ()

    @staticmethod
    def callback(
        text: str, data: str | bytes | None = None, *, password: bool = False
    ) -> types.KeyboardButtonCallback:
        """A button that calls the bot back with a payload.

        The payload defaults to the label, which a program wants often
        enough to be worth not writing twice. It is capped at sixty four bytes
        by Telegram, so it is a key into what the program knows, not the
        thing itself, and something too long is refused here instead of on the
        wire.

        password asks the person to confirm with their account password before
        the press goes through, which is Telegram's own safeguard for a button
        that does something irreversible.
        """
        payload = text.encode() if data is None else _payload(data)
        if not payload:
            raise ValueError("a callback button needs something to send back")
        if len(payload) > CALLBACK_DATA_LIMIT:
            raise ValueError(
                f"callback data is {len(payload)} bytes and Telegram takes at "
                f"most {CALLBACK_DATA_LIMIT}. Put the payload somewhere the "
                f"program can look up and send the key to it"
            )
        return types.KeyboardButtonCallback(
            text=text, data=payload, requires_password=password
        )

    @staticmethod
    def url(text: str, url: str) -> types.KeyboardButtonUrl:
        """A button that opens a link. Nothing reaches the program."""
        return types.KeyboardButtonUrl(text=text, url=url)

    @staticmethod
    def login(
        text: str, url: str, *, button_id: int = 0, forward_text: str = ""
    ) -> types.KeyboardButtonUrlAuth:
        """A button that logs the person into a website as themselves.

        The site is told who pressed it, once they have agreed to that, which
        is what makes this different from an ordinary link.
        """
        return types.KeyboardButtonUrlAuth(
            text=text,
            url=url,
            button_id=button_id,
            fwd_text=forward_text or None,
        )

    @staticmethod
    def switch_inline(
        text: str, query: str = "", *, same_chat: bool = False
    ) -> types.KeyboardButtonSwitchInline:
        """A button that starts an inline query somewhere.

        Pressing it opens the chat picker with the bot's name and the query
        already typed. same_chat keeps it in the chat the button is in, which
        is the form a bot uses to hand someone its own results.
        """
        return types.KeyboardButtonSwitchInline(
            text=text, query=query, same_peer=same_chat
        )

    @staticmethod
    def web_app(text: str, url: str, *, simple: bool = False) -> Any:
        """A button that opens a mini app.

        The ordinary form belongs under a message and tells the app who opened
        it. simple is the other one, which sits above the text field and does
        not.
        """
        if simple:
            return types.KeyboardButtonSimpleWebView(text=text, url=url)
        return types.KeyboardButtonWebView(text=text, url=url)

    @staticmethod
    def game(text: str) -> types.KeyboardButtonGame:
        """The button that starts the game a message carries."""
        return types.KeyboardButtonGame(text=text)

    @staticmethod
    def pay(text: str) -> types.KeyboardButtonBuy:
        """The button that pays for the invoice a message carries."""
        return types.KeyboardButtonBuy(text=text)

    @staticmethod
    def copy(text: str, copy_text: str) -> types.KeyboardButtonCopy:
        """A button that puts something on the clipboard, and calls no one."""
        return types.KeyboardButtonCopy(text=text, copy_text=copy_text)

    @staticmethod
    def profile(text: str, user_id: int) -> types.KeyboardButtonUserProfile:
        """A button that opens someone's profile."""
        return types.KeyboardButtonUserProfile(text=text, user_id=user_id)

    @staticmethod
    def text(label: str) -> types.KeyboardButton:
        """A plain suggestion above the text field, which sends its own label.

        Nothing comes back but an ordinary message, so a handler for one of
        these is a text filter instead of a callback handler.
        """
        return types.KeyboardButton(text=label)

    @staticmethod
    def request_phone(text: str) -> types.KeyboardButtonRequestPhone:
        """A suggestion that asks for the person's phone number.

        They are asked to confirm, and what arrives is an ordinary message
        carrying a contact.
        """
        return types.KeyboardButtonRequestPhone(text=text)

    @staticmethod
    def request_location(text: str) -> types.KeyboardButtonRequestGeoLocation:
        """A suggestion that asks where the person is, with the same confirmation."""
        return types.KeyboardButtonRequestGeoLocation(text=text)

    @staticmethod
    def request_poll(
        text: str, *, quiz: bool | None = None
    ) -> types.KeyboardButtonRequestPoll:
        """A suggestion that opens the poll composer.

        Saying nothing about quiz lets them choose; saying True or False fixes
        it to one kind.
        """
        return types.KeyboardButtonRequestPoll(text=text, quiz=quiz)


def keyboard(
    rows: Any,
    *,
    columns: int = 0,
    resize: bool = True,
    one_time: bool = False,
    persistent: bool = False,
    selective: bool = False,
    placeholder: str | None = None,
) -> base.ReplyMarkup:
    """Build a keyboard out of buttons, in whichever kind they belong to.

    The rows are a list of lists, or a flat list for a single row, or one
    button on its own. A string counts as a plain label, so a reply keyboard
    can be written as the words on it.

    columns lays a flat list out for you, which is the case that otherwise
    turns three buttons into a nested list no one enjoys reading.

    The remaining arguments only mean anything to a reply keyboard: resize
    shrinks it to the buttons rather than taking a third of the screen, and is
    on here because the other way round looks like a mistake in every client
    that draws it; one_time folds it away after a press; persistent keeps it up
    instead of the ordinary text field; selective shows it only to the people a
    message names or replies to; and placeholder is the grey text in the field
    behind it. An inline keyboard has nowhere to put any of them and ignores
    them.
    """
    laid_out = _rows(rows, columns)
    if not laid_out:
        raise ValueError("a keyboard needs at least one button")

    flat = [button for row in laid_out for button in row]
    inline = [button for button in flat if isinstance(button, _INLINE_ONLY)]
    above = [button for button in flat if isinstance(button, _REPLY_ONLY)]
    if inline and above:
        raise ValueError(
            f"{type(inline[0]).__name__} hangs under a message and "
            f"{type(above[0]).__name__} sits above the text field, so they "
            f"cannot be in one keyboard. Send two messages, or pick one kind"
        )
    if not inline and not above:
        raise ValueError(f"{type(flat[0]).__name__} is not a button")

    packed = [types.KeyboardButtonRow(buttons=list(row)) for row in laid_out]
    if inline:
        return types.ReplyInlineMarkup(rows=packed)
    return types.ReplyKeyboardMarkup(
        rows=packed,
        resize=resize,
        single_use=one_time,
        persistent=persistent,
        selective=selective,
        placeholder=placeholder,
    )


def force_reply(
    *, placeholder: str | None = None, one_time: bool = True, selective: bool = False
) -> types.ReplyKeyboardForceReply:
    """Open the other side's keyboard with this message already being replied to.

    The way to ask a question and be sure the answer comes back attached to it,
    which is worth more in a group than in a private chat: without it an answer
    is an ordinary message and matching it to the question is guesswork.
    """
    return types.ReplyKeyboardForceReply(
        placeholder=placeholder, single_use=one_time, selective=selective
    )


def remove_keyboard(*, selective: bool = False) -> types.ReplyKeyboardHide:
    """Take away the reply keyboard a previous message put up.

    Only reply keyboards. An inline keyboard belongs to its message and is
    removed by editing that message's markup away.
    """
    return types.ReplyKeyboardHide(selective=selective)


def buttons_of(message: Any) -> list[list[Any]]:
    """The rows of buttons under a message, or nothing if it has none.

    Only the inline kind. The other keyboard is a suggestion of things to type
    and pressing one sends its text, which arrives as an ordinary message
    instead of as anything to do with the message that put the keyboard up.
    """
    markup = getattr(getattr(message, "raw", message), "reply_markup", None)
    if not isinstance(markup, types.ReplyInlineMarkup):
        return []
    return [list(row.buttons) for row in markup.rows]


def _payload(data: str | bytes) -> bytes:
    return data.encode() if isinstance(data, str) else bytes(data)


def _rows(rows: Any, columns: int) -> list[list[Any]]:
    """However the caller wrote the layout, as a list of rows."""
    if rows is None:
        return []
    if not isinstance(rows, (list, tuple)):
        return [[_as_button(rows)]]

    if any(isinstance(item, (list, tuple)) for item in rows):
        if columns:
            raise ValueError(
                "columns lays out a flat list, and this one already has rows "
                "in it. Pass one or the other"
            )
        laid_out = [
            [_as_button(button) for button in row]
            if isinstance(row, (list, tuple))
            else [_as_button(row)]
            for row in rows
        ]
        return [row for row in laid_out if row]

    flat = [_as_button(button) for button in rows]
    if not flat:
        return []
    width = columns or len(flat)
    return [flat[at : at + width] for at in range(0, len(flat), width)]


def _as_button(button: Any) -> Any:
    """A button, or a string standing for the plain kind."""
    return types.KeyboardButton(text=button) if isinstance(button, str) else button
