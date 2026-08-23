"""Building keyboards, and refusing the ones Telegram would refuse.

Nothing here touches the network: a keyboard is a pure shape, and the only
question worth asking of it is whether the right constructor came out. The one
rule with teeth is that the two kinds of keyboard are two different fields, so a
mixture is a mistake and has to be caught here rather than on the wire, where
the refusal does not say which button was the problem.
"""

from __future__ import annotations

import pytest

from sunnygram.raw import types
from sunnygram.types import (
    CALLBACK_DATA_LIMIT,
    Button,
    buttons_of,
    force_reply,
    keyboard,
    remove_keyboard,
)


class TestButtons:
    def test_a_callback_button_carries_its_payload(self):
        button = Button.callback("Yes", "yes")
        assert isinstance(button, types.KeyboardButtonCallback)
        assert button.data == b"yes"

    def test_the_payload_defaults_to_the_label(self):
        assert Button.callback("Yes").data == b"Yes"

    def test_bytes_are_taken_as_they_are(self):
        assert Button.callback("raw", b"\x00\x01").data == b"\x00\x01"

    def test_a_payload_too_long_for_telegram_is_refused_here(self):
        with pytest.raises(ValueError, match="at most 64"):
            Button.callback("big", "x" * (CALLBACK_DATA_LIMIT + 1))

    def test_a_payload_of_nothing_is_refused(self):
        with pytest.raises(ValueError, match="something to send back"):
            Button.callback("", "")

    def test_a_password_button_says_so(self):
        assert Button.callback("Delete", "del", password=True).requires_password

    def test_a_url_button_is_a_link(self):
        button = Button.url("Docs", "https://example.invalid")
        assert isinstance(button, types.KeyboardButtonUrl)
        assert button.url == "https://example.invalid"

    def test_switching_inline_can_stay_in_the_same_chat(self):
        assert Button.switch_inline("Search", "cats", same_chat=True).same_peer

    def test_a_mini_app_has_two_forms(self):
        under = Button.web_app("Open", "https://example.invalid")
        above = Button.web_app("Open", "https://example.invalid", simple=True)
        assert isinstance(under, types.KeyboardButtonWebView)
        assert isinstance(above, types.KeyboardButtonSimpleWebView)

    def test_a_plain_label_is_the_reply_keyboard_kind(self):
        assert isinstance(Button.text("Hello"), types.KeyboardButton)


class TestLayout:
    def test_rows_are_kept_as_written(self):
        markup = keyboard(
            [[Button.callback("a"), Button.callback("b")], [Button.callback("c")]]
        )
        assert isinstance(markup, types.ReplyInlineMarkup)
        assert [len(row.buttons) for row in markup.rows] == [2, 1]

    def test_a_flat_list_is_one_row(self):
        markup = keyboard([Button.callback("a"), Button.callback("b")])
        assert len(markup.rows) == 1

    def test_one_button_on_its_own_works(self):
        markup = keyboard(Button.callback("only"))
        assert [len(row.buttons) for row in markup.rows] == [1]

    def test_columns_lay_a_flat_list_out(self):
        markup = keyboard([Button.callback(str(n)) for n in range(5)], columns=2)
        assert [len(row.buttons) for row in markup.rows] == [2, 2, 1]

    def test_columns_and_explicit_rows_together_are_a_mistake(self):
        with pytest.raises(ValueError, match="one or the other"):
            keyboard([[Button.callback("a")], [Button.callback("b")]], columns=2)

    def test_a_string_is_a_plain_label(self):
        markup = keyboard(["Yes", "No"])
        assert isinstance(markup, types.ReplyKeyboardMarkup)
        assert markup.rows[0].buttons[0].text == "Yes"

    def test_an_empty_keyboard_is_refused(self):
        with pytest.raises(ValueError, match="at least one button"):
            keyboard([])

    def test_something_that_is_not_a_button_says_so(self):
        with pytest.raises(ValueError, match="is not a button"):
            keyboard([object()])


class TestWhichKindOfKeyboard:
    def test_callback_buttons_make_an_inline_keyboard(self):
        assert isinstance(keyboard([Button.callback("a")]), types.ReplyInlineMarkup)

    def test_plain_labels_make_a_reply_keyboard(self):
        markup = keyboard([Button.text("a")])
        assert isinstance(markup, types.ReplyKeyboardMarkup)
        # Shrunk to the buttons rather than taking a third of the screen, which
        # is the opposite of Telegram's own default and the kinder one.
        assert markup.resize

    def test_asking_for_a_place_makes_a_reply_keyboard(self):
        markup = keyboard([Button.request_location("Where are you")])
        assert isinstance(markup, types.ReplyKeyboardMarkup)

    def test_the_two_kinds_cannot_share_a_keyboard(self):
        with pytest.raises(ValueError, match="cannot be in one keyboard"):
            keyboard([Button.callback("press"), Button.text("type")])

    def test_a_reply_keyboard_carries_its_options(self):
        markup = keyboard(
            ["a"], one_time=True, selective=True, placeholder="pick one"
        )
        assert markup.single_use and markup.selective
        assert markup.placeholder == "pick one"


class TestTheOtherMarkups:
    def test_force_reply_is_one_time_by_default(self):
        markup = force_reply(placeholder="answer here")
        assert isinstance(markup, types.ReplyKeyboardForceReply)
        assert markup.single_use
        assert markup.placeholder == "answer here"

    def test_removing_a_keyboard(self):
        assert isinstance(remove_keyboard(), types.ReplyKeyboardHide)


class TestReadingButtonsBack:
    def test_the_rows_come_back(self):
        message = types.Message(
            id=1,
            peer_id=types.PeerUser(user_id=2),
            date=0,
            message="pick",
            reply_markup=keyboard(
                [[Button.callback("a"), Button.callback("b")], [Button.callback("c")]]
            ),
        )
        assert [len(row) for row in buttons_of(message)] == [2, 1]

    def test_a_message_with_no_keyboard_has_no_buttons(self):
        message = types.Message(
            id=1, peer_id=types.PeerUser(user_id=2), date=0, message="plain"
        )
        assert buttons_of(message) == []

    def test_a_reply_keyboard_is_not_buttons_under_a_message(self):
        # It sits above the text field and its buttons only send their own
        # text, so nothing here can be pressed.
        message = types.Message(
            id=1,
            peer_id=types.PeerUser(user_id=2),
            date=0,
            message="pick",
            reply_markup=keyboard(["a", "b"]),
        )
        assert buttons_of(message) == []
