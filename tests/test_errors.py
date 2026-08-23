"""Turning what a server said into something a caller can act on."""

from __future__ import annotations

import subprocess
import sys

import pytest

from sunnygram.errors import (
    BadRequest,
    FileMigrate,
    FloodWait,
    Forbidden,
    InternalError,
    Migrate,
    NetworkMigrate,
    NotFound,
    PhoneMigrate,
    RPCError,
    SlowmodeWait,
    SunnygramError,
    TakeoutInitDelay,
    Unauthorized,
    UserMigrate,
    rpc_error,
)


class TestWaits:
    def test_flood_wait_carries_the_seconds(self):
        error = rpc_error(420, "FLOOD_WAIT_42")
        assert isinstance(error, FloodWait)
        assert error.seconds == 42

    def test_premium_flood_wait_is_still_a_flood_wait(self):
        assert isinstance(rpc_error(420, "FLOOD_PREMIUM_WAIT_7"), FloodWait)

    def test_slowmode_and_takeout_carry_seconds_too(self):
        assert rpc_error(420, "SLOWMODE_WAIT_5").seconds == 5
        assert rpc_error(420, "TAKEOUT_INIT_DELAY_86400").seconds == 86400
        assert isinstance(rpc_error(420, "SLOWMODE_WAIT_5"), SlowmodeWait)
        assert isinstance(rpc_error(420, "TAKEOUT_INIT_DELAY_1"), TakeoutInitDelay)


class TestMigrations:
    @pytest.mark.parametrize(
        "message,kind",
        [
            ("PHONE_MIGRATE_4", PhoneMigrate),
            ("NETWORK_MIGRATE_2", NetworkMigrate),
            ("USER_MIGRATE_5", UserMigrate),
            ("FILE_MIGRATE_1", FileMigrate),
        ],
    )
    def test_each_kind_carries_the_datacenter(self, message, kind):
        error = rpc_error(303, message)
        assert isinstance(error, kind)
        assert isinstance(error, Migrate)
        assert error.dc_id == int(message.rsplit("_", 1)[1])


class TestByCode:
    @pytest.mark.parametrize(
        "code,kind",
        [
            (400, BadRequest),
            (401, Unauthorized),
            (403, Forbidden),
            (404, NotFound),
            (500, InternalError),
            (503, InternalError),
        ],
    )
    def test_the_code_picks_the_class(self, code, kind):
        assert isinstance(rpc_error(code, "SOMETHING_WENT_WRONG"), kind)

    def test_an_unmapped_code_still_arrives_as_an_rpc_error(self):
        error = rpc_error(418, "I_AM_A_TEAPOT")
        assert type(error) is RPCError
        assert error.code == 418

    def test_a_trailing_number_that_means_nothing_is_left_alone(self):
        # CHANNEL_PRIVATE and friends have no value in them; a message that
        # merely ends in digits must not be mistaken for a parametrized one.
        error = rpc_error(400, "MSG_ID_INVALID_2")
        assert type(error) is BadRequest
        assert error.value is None


class TestNamedErrors:
    """The generated tree: an error worth catching by the name it has."""

    def test_a_documented_error_arrives_as_its_own_class(self):
        from sunnygram.errors import PeerIdInvalid

        error = rpc_error(400, "PEER_ID_INVALID")
        assert isinstance(error, PeerIdInvalid)
        assert isinstance(error, BadRequest)

    def test_the_class_explains_itself(self):
        from sunnygram.errors import PeerIdInvalid

        assert "peer" in (PeerIdInvalid.__doc__ or "").lower()

    def test_a_value_in_the_middle_of_a_name_is_still_found(self):
        from sunnygram.errors import FileReferenceExpired

        error = rpc_error(400, "FILE_REFERENCE_3_EXPIRED")
        assert isinstance(error, FileReferenceExpired)
        assert error.value == 3

    def test_both_spellings_of_one_error_are_one_class(self):
        # Telegram lists FILE_REFERENCE_EXPIRED and FILE_REFERENCE_%d_EXPIRED
        # separately, and they are the same thing said about one file or about
        # the file at an index. Catching one has to catch the other.
        plain = rpc_error(400, "FILE_REFERENCE_EXPIRED")
        indexed = rpc_error(400, "FILE_REFERENCE_3_EXPIRED")
        assert type(plain) is type(indexed)
        assert plain.value is None

    def test_a_premium_flood_is_a_flood_wait_of_its_own(self):
        from sunnygram.errors import FloodPremiumWait

        error = rpc_error(420, "FLOOD_PREMIUM_WAIT_30")
        assert isinstance(error, FloodPremiumWait)
        assert isinstance(error, FloodWait)
        assert error.seconds == 30

    def test_the_code_on_the_wire_wins_over_the_one_the_class_implies(self):
        # PEER_ID_INVALID is a 400 from two hundred methods and a 403 from one,
        # so its class hangs off BadRequest. The number still has to be the one
        # the server actually sent.
        error = rpc_error(403, "PEER_ID_INVALID")
        assert isinstance(error, BadRequest)
        assert error.code == 403

    def test_an_error_added_since_the_last_refresh_is_still_its_status_code(self):
        error = rpc_error(400, "SOMETHING_TELEGRAM_ADDED_ON_TUESDAY")
        assert type(error) is BadRequest

    def test_naming_one_first_thing_in_a_process_works(self):
        # In-process this is hidden: by the time a test asks for a name, some
        # other test has already made an error and pulled the table in the
        # ordinary way. Cold, the import has to stand on its own.
        code = (
            "from sunnygram.errors import PeerIdInvalid, BadRequest;"
            "print(issubclass(PeerIdInvalid, BadRequest))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr[-2000:]
        assert result.stdout.strip() == "True"

    def test_the_table_is_not_loaded_until_something_fails(self):
        # Eight hundred classes nobody has asked for (rule P7). Reaching for
        # sunnygram.errors must not drag them in.
        code = "import sys, sunnygram.errors; print('generated' in str(sys.modules))"
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert result.stdout.strip() == "False"


class TestShape:
    def test_everything_is_catchable_as_one_family(self):
        assert isinstance(rpc_error(420, "FLOOD_WAIT_1"), SunnygramError)
        assert isinstance(rpc_error(420, "FLOOD_WAIT_1"), RPCError)

    def test_it_says_what_happened(self):
        error = rpc_error(400, "CHAT_ID_INVALID", method="messages.sendMessage")
        assert error.code == 400
        assert error.message == "CHAT_ID_INVALID"
        assert error.method == "messages.sendMessage"
        assert "400" in str(error)
        assert "CHAT_ID_INVALID" in str(error)
        assert "messages.sendMessage" in str(error)

    def test_the_method_is_optional(self):
        assert "from" not in str(rpc_error(400, "CHAT_ID_INVALID"))
