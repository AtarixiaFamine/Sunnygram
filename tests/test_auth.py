"""Logging in, against a datacenter that behaves like one.

The server here holds an account: a phone number, a code it expects back, and
optionally a password, for which it stores an SRP verifier exactly as Telegram
does rather than the password itself. So a wrong code is refused for the reason
a real one would refuse it, and a wrong password fails the proof rather than a
string comparison.

That matters most for the second factor. The point of SRP is that the server
never sees the password, and a test where the server checks a password it was
given proves nothing about whether we implemented that.
"""

from __future__ import annotations

import asyncio
import hashlib
import secrets
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.auth import (
    LoginToken,
    check_password,
    get_me,
    log_in,
    log_out,
    resend_code,
    send_code,
    sign_in,
    sign_in_bot,
    sign_in_qr,
)
from sunnygram.errors import (
    PhoneCodeInvalid,
    SessionPasswordNeeded,
    SunnygramError,
)
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState
from test_crypto_srp import PRIME, G, pad, sha256

CLIENT = ClientInfo(api_id=12345, api_hash="0123456789abcdef0123456789abcdef")
PHONE = "+39 333 1234567"
DIGITS = "393331234567"
CODE = "22222"
HASH = "the-code-hash"

ME = types.User(id=777000, first_name="Ada", last_name="Lovelace", username="ada")
# bot and bot_info_version share flag bit 14 in the schema, so a bot without a
# version is a user no reader can parse. A real server always sends both.
BOT = types.User(
    id=42, first_name="Botty", bot=True, bot_info_version=0, username="botty"
)


def authorization(user: types.User = ME) -> types.auth.Authorization:
    return types.auth.Authorization(user=user)


class Account:
    """One account, as the datacenter sees it."""

    def __init__(self, *, password: str | None = None, dc_id: int = 2) -> None:
        self.dc_id = dc_id
        self.password = password
        self.srp_id = 999
        self.salt1 = b"\x01" * 8
        self.salt2 = b"\x02" * 16
        self.b = secrets.randbits(2048)
        if password is not None:
            first = sha256(self.salt1, password.encode(), self.salt1)
            second = sha256(self.salt2, first, self.salt2)
            stretched = hashlib.pbkdf2_hmac("sha512", second, self.salt1, 100_000)
            x = int.from_bytes(sha256(self.salt2, stretched, self.salt2), "big")
            self.verifier = pow(G, x, PRIME)
        else:
            self.verifier = 0

    @property
    def challenge(self) -> bytes:
        k = int.from_bytes(sha256(pad(PRIME), pad(G)), "big")
        return pad((k * self.verifier + pow(G, self.b, PRIME)) % PRIME)

    def password_state(self) -> types.account.Password:
        return types.account.Password(
            new_algo=types.PasswordKdfAlgoUnknown(),
            new_secure_algo=types.SecurePasswordKdfAlgoUnknown(),
            secure_random=b"",
            has_password=self.password is not None,
            hint="the usual" if self.password else None,
            srp_id=self.srp_id if self.password else None,
            srp_B=self.challenge if self.password else None,
            current_algo=(
                types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
                    salt1=self.salt1, salt2=self.salt2, g=G, p=pad(PRIME)
                )
                if self.password
                else None
            ),
        )

    def accepts(self, srp: types.InputCheckPasswordSRP) -> bool:
        """Check the proof the way Telegram does, from the verifier alone."""
        g_a = int.from_bytes(srp.A, "big")
        u = int.from_bytes(sha256(pad(g_a), self.challenge), "big")
        shared = pow(g_a * pow(self.verifier, u, PRIME), self.b, PRIME)
        expected = sha256(
            bytes(a ^ b for a, b in zip(sha256(pad(PRIME)), sha256(pad(G)))),
            sha256(self.salt1),
            sha256(self.salt2),
            pad(g_a),
            self.challenge,
            sha256(pad(shared)),
        )
        return srp.srp_id == self.srp_id and srp.M1 == expected


class LoginServer(ScriptedServer):
    """A datacenter that will let you in if you get the answers right."""

    def __init__(self, wire: Wire, session: Any, account: Account) -> None:
        super().__init__(wire, session)
        self.account = account
        self.code = CODE
        self.qr_token = b"\xaa" * 32
        self.qr_scanned = False
        self.qr_exports = 0
        self.calls: list[Any] = []
        # Methods to refuse rather than answer, so a test can make one call go
        # wrong without racing a second reader against the queue.
        self.refusing: dict[type, tuple[int, str]] = {}
        self.answering: dict[type, Any] = {}

    async def serve_login(self) -> None:
        """Answer login calls until cancelled."""
        while True:
            request = await self.take()
            query = request.query
            self.calls.append(query)
            refusal = self.refusing.get(type(query))
            if refusal is not None:
                await self.refuse(request.msg_id, *refusal)
                continue
            instead = self.answering.get(type(query))
            if instead is not None:
                await self.answer(request.msg_id, instead)
                continue
            await self._answer_one(request.msg_id, query)

    async def _answer_one(self, msg_id: int, query: Any) -> None:
        if isinstance(query, functions.auth.SendCode):
            if query.phone_number != DIGITS:
                await self.refuse(msg_id, 400, "PHONE_NUMBER_INVALID")
            elif self.account.dc_id != 2:
                await self.refuse(msg_id, 303, f"PHONE_MIGRATE_{self.account.dc_id}")
            else:
                await self.answer(
                    msg_id,
                    types.auth.SentCode(
                        type=types.auth.SentCodeTypeApp(length=5),
                        phone_code_hash=HASH,
                        timeout=60,
                        next_type=types.auth.CodeTypeSms(),
                    ),
                )
        elif isinstance(query, functions.auth.ResendCode):
            await self.answer(
                msg_id,
                types.auth.SentCode(
                    type=types.auth.SentCodeTypeSms(length=5), phone_code_hash=HASH
                ),
            )
        elif isinstance(query, functions.auth.SignIn):
            if query.phone_code != self.code:
                await self.refuse(msg_id, 400, "PHONE_CODE_INVALID")
            elif self.account.password is not None:
                await self.refuse(msg_id, 401, "SESSION_PASSWORD_NEEDED")
            else:
                await self.answer(msg_id, authorization())
        elif isinstance(query, functions.account.GetPassword):
            await self.answer(msg_id, self.account.password_state())
        elif isinstance(query, functions.auth.CheckPassword):
            if self.account.accepts(query.password):
                await self.answer(msg_id, authorization())
            else:
                await self.refuse(msg_id, 400, "PASSWORD_HASH_INVALID")
        elif isinstance(query, functions.auth.ImportBotAuthorization):
            if query.bot_auth_token == "42:good-token":
                await self.answer(msg_id, authorization(BOT))
            else:
                await self.refuse(msg_id, 400, "ACCESS_TOKEN_INVALID")
        elif isinstance(query, functions.auth.ExportLoginToken):
            self.qr_exports += 1
            if self.qr_scanned:
                await self.answer(
                    msg_id, types.auth.LoginTokenSuccess(authorization=authorization())
                )
            elif self.account.dc_id != 2:
                await self.answer(
                    msg_id,
                    types.auth.LoginTokenMigrateTo(
                        dc_id=self.account.dc_id, token=self.qr_token
                    ),
                )
            else:
                await self.answer(
                    msg_id,
                    types.auth.LoginToken(expires=2**31 - 1, token=self.qr_token),
                )
        elif isinstance(query, functions.auth.ImportLoginToken):
            await self.answer(
                msg_id, types.auth.LoginTokenSuccess(authorization=authorization())
            )
        elif isinstance(query, functions.users.GetUsers):
            await self.answer(msg_id, [ME])
        elif isinstance(query, functions.auth.LogOut):
            await self.answer(msg_id, types.auth.LoggedOut())
        else:
            await self.refuse(msg_id, 400, "METHOD_NOT_TESTED")


class Network:
    """Queues instead of sockets, one pair per connection attempt."""

    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire

    @property
    def datacenters(self) -> list[int]:
        return [where.dc_id for where, _ in self.wires]


@asynccontextmanager
async def live(
    account: Account | None = None, storage: MemoryStorage | None = None
) -> AsyncIterator[tuple[Invoker, LoginServer]]:
    """An invoker connected to a datacenter that is serving a login."""
    account = Account() if account is None else account
    if storage is None:
        state = SessionState(dc_id=2)
        state.set_auth_key(2, AUTH_KEY)
        state.set_auth_key(account.dc_id, AUTH_KEY)
        storage = MemoryStorage(state)

    network = Network()
    invoker = Invoker(
        storage,
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        # Short, so a call nobody answers fails the test rather than stalling it
        # for a minute.
        timeout=5.0,
    )
    await invoker.start()
    connection = invoker.connection
    assert connection is not None
    server = LoginServer(network.wires[-1][1], connection.session, account)
    serving = asyncio.create_task(server.serve_login())
    try:
        yield invoker, server
    finally:
        serving.cancel()
        await asyncio.gather(serving, return_exceptions=True)
        await invoker.close()

    # Migration replaces the connection, so a test that moved needs its server
    # rebuilt; the helper below is what does that.
    _ = network


class TestSendingCode:
    async def test_a_code_is_asked_for(self):
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            assert sent.phone_number == DIGITS
            assert sent.phone_code_hash == HASH
            assert sent.kind == "app"
            assert sent.timeout == 60

    async def test_the_number_is_cleaned_up_first(self):
        async with live() as (invoker, server):
            await send_code(invoker, "+39 (333) 123-4567")
            assert server.calls[0].phone_number == DIGITS

    async def test_the_application_identifies_itself(self):
        async with live() as (invoker, server):
            await send_code(invoker, PHONE)
            assert server.calls[0].api_id == CLIENT.api_id
            assert server.calls[0].api_hash == CLIENT.api_hash

    async def test_a_number_with_no_digits_is_refused_before_it_is_sent(self):
        async with live() as (invoker, server):
            with pytest.raises(ValueError, match="no digits"):
                await send_code(invoker, "not a phone")
            assert server.calls == []

    async def test_without_an_api_hash_it_says_so(self):
        state = SessionState(dc_id=2)
        state.set_auth_key(2, AUTH_KEY)
        network = Network()
        invoker = Invoker(
            MemoryStorage(state),
            client=ClientInfo(api_id=1),
            connector=network.connect,
            ping_interval=None,
        )
        await invoker.start()
        try:
            with pytest.raises(SunnygramError, match="api_hash"):
                await send_code(invoker, PHONE)
        finally:
            await invoker.close()

    async def test_the_code_can_be_asked_for_again(self):
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            again = await resend_code(invoker, sent)
            assert again.kind == "sms"


class TestSigningIn:
    async def test_the_right_code_signs_in(self):
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            user = await sign_in(invoker, sent, CODE)
            assert user.id == ME.id
            assert user.first_name == "Ada"

    async def test_signing_in_is_written_down(self):
        state = SessionState(dc_id=2)
        state.set_auth_key(2, AUTH_KEY)
        storage = MemoryStorage(state)
        async with live(storage=storage) as (invoker, server):
            sent = await send_code(invoker, PHONE)
            await sign_in(invoker, sent, CODE)
            assert invoker.state.authorized
        stored = await storage.load()
        assert stored.user_id == ME.id
        assert stored.is_bot is False

    async def test_the_wrong_code_is_refused(self):
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            with pytest.raises(PhoneCodeInvalid):
                await sign_in(invoker, sent, "00000")
            assert not invoker.state.authorized

    async def test_whitespace_around_the_code_is_forgiven(self):
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            assert await sign_in(invoker, sent, f" {CODE}\n")

    async def test_an_account_that_does_not_exist_is_not_created(self):
        # Registering is deliberately out of scope, and the refusal says where
        # to go instead rather than leaving the caller guessing.
        async with live() as (invoker, server):
            sent = await send_code(invoker, PHONE)
            server.answering[functions.auth.SignIn] = (
                types.auth.AuthorizationSignUpRequired()
            )
            with pytest.raises(SunnygramError, match="official Telegram client"):
                await sign_in(invoker, sent, CODE)


class TestSecondFactor:
    async def test_a_password_is_asked_for_after_the_code(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            sent = await send_code(invoker, PHONE)
            with pytest.raises(SessionPasswordNeeded):
                await sign_in(invoker, sent, CODE)

    async def test_the_right_password_gets_past_it(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            user = await check_password(invoker, "hunter2")
            assert user.id == ME.id
            assert invoker.state.authorized

    async def test_the_password_itself_never_goes_out(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            await check_password(invoker, "hunter2")
            sent = [
                call
                for call in server.calls
                if isinstance(call, functions.auth.CheckPassword)
            ]
            assert len(sent) == 1
            blob = sent[0].password.A + sent[0].password.M1
            assert b"hunter2" not in blob
            assert b"hunter2" not in sent[0].to_bytes()

    async def test_the_wrong_password_does_not(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            from sunnygram.errors import PasswordHashInvalid

            with pytest.raises(PasswordHashInvalid):
                await check_password(invoker, "hunter3")
            assert not invoker.state.authorized

    async def test_an_account_with_no_password_says_so(self):
        async with live() as (invoker, server):
            with pytest.raises(SunnygramError, match="no password"):
                await check_password(invoker, "hunter2")


class TestBots:
    async def test_a_token_signs_a_bot_in(self):
        async with live() as (invoker, server):
            user = await sign_in_bot(invoker, "42:good-token")
            assert user.id == BOT.id
            assert invoker.state.is_bot is True

    async def test_a_bad_token_is_refused(self):
        async with live() as (invoker, server):
            from sunnygram.errors import BadRequest

            with pytest.raises(BadRequest):
                await sign_in_bot(invoker, "42:nope")


class TestQrLogin:
    async def test_a_scanned_code_signs_in(self):
        async with live() as (invoker, server):
            shown: list[LoginToken] = []

            async def scan_it(token: LoginToken) -> None:
                shown.append(token)
                server.qr_scanned = True

            user = await sign_in_qr(invoker, scan_it, poll=0.01)
            assert user.id == ME.id
            assert shown and shown[0].url.startswith("tg://login?token=")
            assert invoker.state.authorized

    async def test_nobody_scanning_it_gives_up(self):
        async with live() as (invoker, server):
            with pytest.raises(SunnygramError, match="in time"):
                await sign_in_qr(invoker, lambda token: None, timeout=0.1, poll=0.01)

    async def test_the_token_is_a_link_a_client_can_read(self):
        token = LoginToken(token=b"\x00\xff" * 8, expires=0)
        assert token.url == "tg://login?token=AP8A_wD_AP8A_wD_AP8A_w"
        assert token.seconds_left == 0.0


class TestWhoAndOut:
    async def test_it_can_say_who_it_is(self):
        async with live() as (invoker, server):
            assert (await get_me(invoker)).username == "ada"

    async def test_logging_out_forgets_everything(self):
        state = SessionState(dc_id=2)
        state.set_auth_key(2, AUTH_KEY)
        storage = MemoryStorage(state)
        async with live(storage=storage) as (invoker, server):
            sent = await send_code(invoker, PHONE)
            await sign_in(invoker, sent, CODE)
            await log_out(invoker)
            assert not invoker.state.authorized
        stored = await storage.load()
        assert stored.user_id == 0
        assert stored.auth_keys == {}

    async def test_the_key_goes_even_if_the_server_never_answers(self):
        # The key is dead on the server either way, so keeping it would only
        # leave a credential that opens nothing.
        async with live() as (invoker, server):
            invoker.state.user_id = ME.id
            server.refusing[functions.auth.LogOut] = (403, "AUTH_KEY_PERM_EMPTY")
            with pytest.raises(SunnygramError):
                await log_out(invoker)
            assert invoker.state.auth_keys == {}
            assert not invoker.state.authorized


class TestLogIn:
    async def test_it_walks_the_whole_path(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            asked = []

            def for_code(sent):
                asked.append(sent.kind)
                return CODE

            def for_password(hint):
                asked.append(hint)
                return "hunter2"

            user = await log_in(
                invoker,
                phone_number=PHONE,
                code=for_code,
                password=for_password,
            )
            assert user.id == ME.id
            assert asked == ["app", "the usual"]

    async def test_the_callables_may_be_async(self):
        async with live() as (invoker, server):
            async def for_code(sent):
                return CODE

            async def for_number():
                return PHONE

            user = await log_in(
                invoker, phone_number=for_number, code=for_code
            )
            assert user.id == ME.id

    async def test_a_session_that_is_already_signed_in_is_left_alone(self):
        state = SessionState(dc_id=2, user_id=ME.id)
        state.set_auth_key(2, AUTH_KEY)
        async with live(storage=MemoryStorage(state)) as (invoker, server):
            user = await log_in(
                invoker,
                phone_number=PHONE,
                code=lambda sent: pytest.fail("it asked for a code anyway"),
            )
            assert user.id == ME.id
            assert isinstance(server.calls[0], functions.users.GetUsers)

    async def test_a_bot_token_short_circuits_the_whole_thing(self):
        async with live() as (invoker, server):
            user = await log_in(
                invoker,
                phone_number=PHONE,
                code=lambda sent: pytest.fail("a bot has no phone"),
                bot_token="42:good-token",
            )
            assert user.id == BOT.id

    async def test_a_password_nobody_can_supply_is_raised(self):
        async with live(Account(password="hunter2")) as (invoker, server):
            with pytest.raises(SessionPasswordNeeded):
                await log_in(
                    invoker, phone_number=PHONE, code=lambda sent: CODE
                )


class TestMigrationDuringLogin:
    async def test_a_number_from_another_datacenter_moves_the_session(self):
        # The one migration that always happens in practice: the number decides
        # which datacenter the account lives on, and only the server knows.
        account = Account(dc_id=4)
        state = SessionState(dc_id=2)
        state.set_auth_key(2, AUTH_KEY)
        state.set_auth_key(4, AUTH_KEY)
        network = Network()
        invoker = Invoker(
            MemoryStorage(state),
            client=CLIENT,
            connector=network.connect,
            ping_interval=None,
        )
        await invoker.start()
        try:
            first = LoginServer(network.wires[0][1], invoker.connection.session, account)
            serving = asyncio.create_task(first.serve_login())
            call = asyncio.create_task(send_code(invoker, PHONE))

            # It moves to DC 4, and the code request has to be made again there.
            await _until(lambda: len(network.wires) == 2)
            serving.cancel()
            account.dc_id = 2  # arrived: from here the account is local
            second = LoginServer(
                network.wires[1][1], invoker.connection.session, account
            )
            serving_there = asyncio.create_task(second.serve_login())

            sent = await asyncio.wait_for(call, 5)
            assert sent.phone_code_hash == HASH
            assert invoker.state.dc_id == 4
            assert network.datacenters == [2, 4]

            serving_there.cancel()
            await asyncio.gather(serving, serving_there, return_exceptions=True)
        finally:
            await invoker.close()


async def _until(condition, timeout: float = 5.0) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not condition():
        if loop.time() > deadline:
            raise AssertionError("it never got there")
        await asyncio.sleep(0.01)
