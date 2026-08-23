"""Pressing a bot's buttons, and looking after the account.

Finding a button is the part with logic in it and is checked directly against
built keyboards. The rest is driven against a scripted datacenter, including the
password calls, where what is being checked is that no password ever reaches the
wire: what goes out is a proof of one and a verifier for the other.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.errors import SunnygramError
from sunnygram.methods import account, bots
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
WHERE = types.InputPeerUser(user_id=1001, access_hash=3003)
PASSWORD = "correct horse battery staple"

# Straight out of Telegram's own parameters, small enough to be quick.
SALT1 = b"\x01" * 32
SALT2 = b"\x02" * 32
PRIME = int.from_bytes(
    bytes.fromhex(
        "C71CAEB9C6B1C9048E6C522F70F13F73980D40238E3E21C14934D037563D930F"
        "48198A0AA7C14058229493D22530F4DBFA336F6E0AC925139543AED44CCE7C37"
        "20FD51F69458705AC68CD4FE6B6B13ABDC9746512969328454F18FAF8C595F64"
        "2477FE96BB2A941D5BCD1D4AC8CC49880708FA9B378E3C4F3A9060BEE67CF9A4"
        "A4A695811051907E162753B56B0F6B410DBA74D8A84B2A14B3144E0EF1284754"
        "FD17ED950D5965B4B9DD46582DB1178D169C6BC465B0D6FF9CA3928FEF5B9AE4"
        "E418FC15E83EBEA0F87FA9FF5EED70050DED2849F47BF959D956850CE929851F"
        "0D8115F635B105EE2E4E15D04B2454BF6F4FADF034B10403119CD8E3B92FCC5B"
    ),
    "big",
)


def keyboard(*rows: list[Any]) -> types.Message:
    return types.Message(
        id=7,
        peer_id=types.PeerUser(user_id=1001),
        date=1700000000,
        message="pick one",
        reply_markup=types.ReplyInlineMarkup(
            rows=[types.KeyboardButtonRow(buttons=row) for row in rows]
        ),
    )


def callback(text: str, data: bytes = b"x") -> types.KeyboardButtonCallback:
    return types.KeyboardButtonCallback(text=text, data=data)


class TestFindingButtons:
    def test_by_label(self):
        message = keyboard([callback("Yes", b"y"), callback("No", b"n")])
        assert bots.find_button(message, "No").data == b"n"

    def test_by_number_in_reading_order(self):
        message = keyboard([callback("a"), callback("b")], [callback("c")])
        assert bots.find_button(message, 2).text == "c"

    def test_by_row_and_position(self):
        message = keyboard([callback("a"), callback("b")], [callback("c")])
        assert bots.find_button(message, (0, 1)).text == "b"

    def test_a_label_that_is_not_there_says_what_is(self):
        message = keyboard([callback("Yes"), callback("No")])
        with pytest.raises(SunnygramError, match="'Yes', 'No'"):
            bots.find_button(message, "Maybe")

    def test_a_number_past_the_end(self):
        with pytest.raises(SunnygramError, match="there are 1 buttons"):
            bots.find_button(keyboard([callback("a")]), 5)

    def test_a_position_past_the_end(self):
        with pytest.raises(SunnygramError, match="no button at row 3"):
            bots.find_button(keyboard([callback("a")]), (3, 0))

    def test_a_message_with_no_buttons(self):
        plain = types.Message(
            id=1, peer_id=types.PeerUser(user_id=1), date=0, message="hi"
        )
        with pytest.raises(SunnygramError, match="no buttons"):
            bots.find_button(plain, 0)

    def test_the_other_keyboard_does_not_count(self):
        # A reply keyboard is a list of things to type, and pressing one sends
        # its text rather than calling anything.
        message = types.Message(
            id=1,
            peer_id=types.PeerUser(user_id=1),
            date=0,
            message="hi",
            reply_markup=types.ReplyKeyboardMarkup(
                rows=[
                    types.KeyboardButtonRow(buttons=[types.KeyboardButton(text="a")])
                ]
            ),
        )
        assert bots.keyboard_of(message) == []


class TestPressingButtons:
    async def test_the_data_goes_out(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.BotCallbackAnswer(
                cache_time=0, message="done"
            )
            answer = await bots.click_button(
                invoker, WHERE, keyboard([callback("Yes", b"yes")]), "Yes"
            )
        assert answer.message == "done"
        call = server.only(functions.messages.GetBotCallbackAnswer)
        assert call.data == b"yes" and call.msg_id == 7

    async def test_a_link_is_not_a_button_to_press(self):
        message = keyboard([types.KeyboardButtonUrl(text="Docs", url="https://x")])
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="is a link rather than"):
                await bots.click_button(invoker, WHERE, message, "Docs")

    async def test_a_button_wanting_the_password_says_so(self):
        message = keyboard(
            [types.KeyboardButtonCallback(text="Pay", data=b"p", requires_password=True)]
        )
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="asks for the account password"):
                await bots.click_button(invoker, WHERE, message, "Pay")


class TestInlineBots:
    async def test_a_query_names_the_bot_and_the_chat(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.messages.BotResults(
                query_id=123, results=[], cache_time=0, users=[]
            )
            await bots.inline_results(invoker, WHERE, "cats", peer=WHERE)
        call = server.only(functions.messages.GetInlineBotResults)
        assert call.query == "cats"
        assert call.bot.user_id == 1001

    async def test_sending_a_result_carries_both_ids(self):
        async with live() as (invoker, server):
            await bots.send_inline_result(invoker, WHERE, 123, "abc")
        call = server.only(functions.messages.SendInlineBotResult)
        assert (call.query_id, call.id) == (123, "abc")
        assert call.random_id

    async def test_starting_a_bot_carries_the_parameter(self):
        async with live() as (invoker, server):
            await bots.start_bot(invoker, WHERE, parameter="ref123")
        call = server.only(functions.messages.StartBot)
        assert call.start_param == "ref123"
        # Started in its own chat unless somewhere else was named.
        assert call.peer == WHERE

    async def test_starting_a_bot_in_a_group(self):
        group = types.InputPeerChat(chat_id=5005)
        async with live() as (invoker, server):
            await bots.start_bot(invoker, WHERE, peer=group)
        assert server.only(functions.messages.StartBot).peer == group


class TestSessions:
    async def test_listing_them(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.account.Authorizations(
                authorization_ttl_days=30, authorizations=[]
            )
            found = await account.sessions(invoker)
        assert found.authorization_ttl_days == 30
        assert server.only(functions.account.GetAuthorizations)

    async def test_ending_one(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: True
            assert await account.terminate_session(invoker, 999)
        assert server.only(functions.account.ResetAuthorization).hash == 999

    async def test_the_current_one_cannot_be_ended_this_way(self):
        async with live() as (invoker, _):
            with pytest.raises(SunnygramError, match="log out instead"):
                await account.terminate_session(invoker, 0)

    async def test_ending_all_the_others(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: True
            assert await account.terminate_other_sessions(invoker)
        assert server.only(functions.auth.ResetAuthorizations)


class TestPasswords:
    async def test_setting_a_first_password_sends_no_proof(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=False)
            await account.set_password(invoker, PASSWORD, hint="a hint")
        call = server.only(functions.account.UpdatePasswordSettings)
        assert isinstance(call.password, types.InputCheckPasswordEmpty)
        assert call.new_settings.hint == "a hint"

    async def test_the_password_itself_never_reaches_the_wire(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=False)
            await account.set_password(invoker, PASSWORD)
        call = server.only(functions.account.UpdatePasswordSettings)
        sent = call.to_bytes()
        assert PASSWORD.encode() not in sent
        # What goes out is g raised to the password, the size of the prime.
        assert len(call.new_settings.new_password_hash) == 256

    async def test_changing_one_proves_the_current_password_first(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=True)
            await account.set_password(invoker, "a new one", current=PASSWORD)
        call = server.only(functions.account.UpdatePasswordSettings)
        assert isinstance(call.password, types.InputCheckPasswordSRP)
        assert call.password.srp_id == 4242
        assert PASSWORD.encode() not in call.to_bytes()

    async def test_changing_one_without_the_current_says_so(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=True)
            with pytest.raises(SunnygramError, match="the current one is needed"):
                await account.set_password(invoker, "a new one")

    async def test_removing_one_sends_the_unknown_algorithm(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=True)
            await account.remove_password(invoker, PASSWORD)
        call = server.only(functions.account.UpdatePasswordSettings)
        assert isinstance(call.new_settings.new_algo, types.PasswordKdfAlgoUnknown)
        assert call.new_settings.new_password_hash == b""

    async def test_setting_an_empty_password(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="remove_password"):
                await account.set_password(invoker, "")

    async def test_an_account_with_no_password_checks_as_false(self):
        async with live() as (invoker, server):
            server.answer_with = _password_state(has_password=False)
            assert not await account.password_check(invoker, PASSWORD)


class TestPrivacyAndNames:
    async def test_a_setting_by_name(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.account.PrivacyRules(
                rules=[], chats=[], users=[]
            )
            await account.privacy(invoker, "last_seen")
        call = server.only(functions.account.GetPrivacy)
        assert isinstance(call.key, types.InputPrivacyKeyStatusTimestamp)

    async def test_a_setting_that_does_not_exist_lists_the_ones_that_do(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="last_seen"):
                await account.privacy(invoker, "nonsense")

    async def test_setting_one(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.account.PrivacyRules(
                rules=[], chats=[], users=[]
            )
            await account.set_privacy(invoker, "last_seen", "nobody")
        rules = server.only(functions.account.SetPrivacy).rules
        assert isinstance(rules[0], types.InputPrivacyValueDisallowAll)

    async def test_exceptions_go_before_the_rule(self):
        # Telegram reads the rules in order, so a list built the other way
        # round quietly means the opposite of what it looks like.
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.account.PrivacyRules(
                rules=[], chats=[], users=[]
            )
            await account.set_privacy(
                invoker, "last_seen", "contacts", except_users=[WHERE]
            )
        rules = server.only(functions.account.SetPrivacy).rules
        assert isinstance(rules[0], types.InputPrivacyValueDisallowUsers)
        assert isinstance(rules[1], types.InputPrivacyValueAllowContacts)

    async def test_an_exception_to_a_denial_is_an_allowance(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: types.account.PrivacyRules(
                rules=[], chats=[], users=[]
            )
            await account.set_privacy(
                invoker, "last_seen", "nobody", except_users=[WHERE]
            )
        rules = server.only(functions.account.SetPrivacy).rules
        assert isinstance(rules[0], types.InputPrivacyValueAllowUsers)

    async def test_a_rule_that_does_not_exist(self):
        async with live() as (invoker, _):
            with pytest.raises(ValueError, match="not something a privacy rule"):
                await account.set_privacy(invoker, "last_seen", "sometimes")

    async def test_the_at_sign_is_optional(self):
        async with live() as (invoker, server):
            server.answer_with = lambda query: True
            await account.check_username(invoker, "@durov")
        assert server.only(functions.account.CheckUsername).username == "durov"


def _password_state(*, has_password: bool):
    """A server that answers getPassword and takes whatever follows."""
    algorithm = types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
        salt1=SALT1, salt2=SALT2, g=3, p=PRIME.to_bytes(256, "big")
    )

    def answer(query: Any) -> Any:
        if isinstance(query, functions.account.GetPassword):
            return types.account.Password(
                has_recovery=False,
                has_secure_values=False,
                has_password=has_password,
                current_algo=algorithm if has_password else None,
                srp_B=b"\x05" * 256 if has_password else None,
                srp_id=4242 if has_password else None,
                new_algo=algorithm,
                new_secure_algo=types.SecurePasswordKdfAlgoSHA512(salt=SALT1),
                secure_random=b"\x00" * 32,
            )
        if isinstance(query, functions.account.GetPasswordSettings):
            return types.account.PasswordSettings()
        return True

    return answer


class TestTheCommandMenu:
    """The one thing here a bot does about itself rather than to a bot."""

    async def test_the_menu_is_published_for_everybody_by_default(self):
        async with live() as (invoker, server):
            await bots.set_bot_commands(
                invoker, [("start", "Wake up"), ("help", "List everything")]
            )
        sent = server.only(functions.bots.SetBotCommands)
        assert isinstance(sent.scope, types.BotCommandScopeDefault)
        assert [(one.command, one.description) for one in sent.commands] == [
            ("start", "Wake up"),
            ("help", "List everything"),
        ]

    async def test_a_slash_is_allowed_and_stripped(self):
        # People write commands down with the slash, and Telegram refuses one.
        async with live() as (invoker, server):
            await bots.set_bot_commands(invoker, [("/start", "Wake up")])
        assert server.only(functions.bots.SetBotCommands).commands[0].command == "start"

    async def test_a_scope_is_passed_along(self):
        async with live() as (invoker, server):
            await bots.set_bot_commands(
                invoker,
                [("ban", "Remove somebody")],
                scope=types.BotCommandScopeChatAdmins(),
                lang_code="it",
            )
        sent = server.only(functions.bots.SetBotCommands)
        assert isinstance(sent.scope, types.BotCommandScopeChatAdmins)
        assert sent.lang_code == "it"

    async def test_reading_the_menu_back_gives_what_setting_it_takes(self):
        def answer(query: Any) -> Any:
            return [
                types.BotCommand(command="start", description="Wake up"),
                types.BotCommand(command="help", description="List everything"),
            ]

        async with live() as (invoker, server):
            server.answer_with = answer
            found = await bots.get_bot_commands(invoker)
        assert found == [("start", "Wake up"), ("help", "List everything")]

    async def test_the_menu_can_be_taken_away(self):
        async with live() as (invoker, server):
            await bots.delete_bot_commands(invoker)
        assert isinstance(
            server.only(functions.bots.ResetBotCommands).scope,
            types.BotCommandScopeDefault,
        )


class Network:
    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire


class RecordingServer(ScriptedServer):
    def __init__(self, wire: Wire, session: Any) -> None:
        super().__init__(wire, session)
        self.seen: list[Any] = []
        self.answer_with: Any = None

    async def serve(self) -> None:
        while True:
            request = await self.take()
            self.seen.append(request.query)
            try:
                made = (
                    self.answer_with(request.query)
                    if self.answer_with is not None
                    else types.Updates(
                        updates=[], users=[], chats=[], date=1700000000, seq=0
                    )
                )
            except Exception as failure:
                # A scripted answer that raises would otherwise take this task
                # down quietly and leave the caller waiting out its timeout, so
                # the mistake comes back as an error the test can read.
                await self.refuse(request.msg_id, 500, f"SCRIPT_FAILED: {failure!r}")
                continue
            await self.answer(request.msg_id, made)

    def all(self, kind: type) -> list[Any]:
        return [query for query in self.seen if isinstance(query, kind)]

    def only(self, kind: type) -> Any:
        found = self.all(kind)
        assert len(found) == 1, f"expected one {kind.__name__}, got {len(found)}"
        return found[0]


@asynccontextmanager
async def live() -> AsyncIterator[tuple[Invoker, RecordingServer]]:
    session = SessionState(dc_id=2, user_id=ME)
    session.set_auth_key(2, AUTH_KEY)
    network = Network()
    invoker = Invoker(
        MemoryStorage(session),
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=10.0,
        rate_limit=False,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = RecordingServer(network.wires[-1][1], connection.session)
    serving = asyncio.create_task(server.serve())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()
