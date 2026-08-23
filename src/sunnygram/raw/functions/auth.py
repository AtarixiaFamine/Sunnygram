# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the auth namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class SendCode(TLFunction["base.auth.SentCode"]):
    """The TL function auth.sendCode#a677244f, answered with auth.SentCode."""

    __slots__ = ("phone_number", "api_id", "api_hash", "settings",)

    ID = 0xA677244F
    QUALNAME = "functions.auth.SendCode"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        api_id: int,
        api_hash: str,
        settings: base.CodeSettings,
    ) -> None:
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_int(self.api_id)
        w.write_string(self.api_hash)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        api_id = r.read_int()
        api_hash = r.read_string()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.settings = settings
        return self


class SignUp(TLFunction["base.auth.Authorization"]):
    """The TL function auth.signUp#aac7b717, answered with auth.Authorization."""

    __slots__ = ("no_joined_notifications", "phone_number", "phone_code_hash", "first_name", "last_name",)

    ID = 0xAAC7B717
    QUALNAME = "functions.auth.SignUp"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        no_joined_notifications: bool = False,
        phone_number: str,
        phone_code_hash: str,
        first_name: str,
        last_name: str,
    ) -> None:
        self.no_joined_notifications = no_joined_notifications
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.first_name = first_name
        self.last_name = last_name

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_joined_notifications:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        w.write_string(self.first_name)
        w.write_string(self.last_name)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_joined_notifications = bool(flags & (1 << 0))
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        first_name = r.read_string()
        last_name = r.read_string()
        self = cls.__new__(cls)
        self.no_joined_notifications = no_joined_notifications
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.first_name = first_name
        self.last_name = last_name
        return self


class SignIn(TLFunction["base.auth.Authorization"]):
    """The TL function auth.signIn#8d52a951, answered with auth.Authorization."""

    __slots__ = ("phone_number", "phone_code_hash", "phone_code", "email_verification",)

    ID = 0x8D52A951
    QUALNAME = "functions.auth.SignIn"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        phone_code: str | None = None,
        email_verification: base.EmailVerification | None = None,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        self.email_verification = email_verification

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.phone_code is not None:
            flags |= 1 << 0
        if self.email_verification is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        if self.phone_code is not None:
            w.write_string(self.phone_code)
        if self.email_verification is not None:
            self.email_verification.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        phone_code = r.read_string() if flags & (1 << 0) else None
        email_verification = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        self.email_verification = email_verification
        return self


class LogOut(TLFunction["base.auth.LoggedOut"]):
    """The TL function auth.logOut#3e72ba19, answered with auth.LoggedOut."""

    __slots__ = ()

    ID = 0x3E72BA19
    QUALNAME = "functions.auth.LogOut"
    RESULT = "auth.LoggedOut"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ResetAuthorizations(TLFunction["bool"]):
    """The TL function auth.resetAuthorizations#9fab0d1a, answered with Bool."""

    __slots__ = ()

    ID = 0x9FAB0D1A
    QUALNAME = "functions.auth.ResetAuthorizations"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ExportAuthorization(TLFunction["base.auth.ExportedAuthorization"]):
    """The TL function auth.exportAuthorization#e5bfffcd, answered with auth.ExportedAuthorization."""

    __slots__ = ("dc_id",)

    ID = 0xE5BFFFCD
    QUALNAME = "functions.auth.ExportAuthorization"
    RESULT = "auth.ExportedAuthorization"

    def __init__(
        self,
        *,
        dc_id: int,
    ) -> None:
        self.dc_id = dc_id

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.dc_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dc_id = r.read_int()
        self = cls.__new__(cls)
        self.dc_id = dc_id
        return self


class ImportAuthorization(TLFunction["base.auth.Authorization"]):
    """The TL function auth.importAuthorization#a57a7dad, answered with auth.Authorization."""

    __slots__ = ("id", "bytes",)

    ID = 0xA57A7DAD
    QUALNAME = "functions.auth.ImportAuthorization"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        id: int,
        bytes: bytes,
    ) -> None:
        self.id = id
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.id)
        w.write_bytes(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_long()
        bytes = r.read_bytes()
        self = cls.__new__(cls)
        self.id = id
        self.bytes = bytes
        return self


class BindTempAuthKey(TLFunction["bool"]):
    """The TL function auth.bindTempAuthKey#cdd42a05, answered with Bool."""

    __slots__ = ("perm_auth_key_id", "nonce", "expires_at", "encrypted_message",)

    ID = 0xCDD42A05
    QUALNAME = "functions.auth.BindTempAuthKey"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        perm_auth_key_id: int,
        nonce: int,
        expires_at: int,
        encrypted_message: bytes,
    ) -> None:
        self.perm_auth_key_id = perm_auth_key_id
        self.nonce = nonce
        self.expires_at = expires_at
        self.encrypted_message = encrypted_message

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.perm_auth_key_id)
        w.write_long(self.nonce)
        w.write_int(self.expires_at)
        w.write_bytes(self.encrypted_message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        perm_auth_key_id = r.read_long()
        nonce = r.read_long()
        expires_at = r.read_int()
        encrypted_message = r.read_bytes()
        self = cls.__new__(cls)
        self.perm_auth_key_id = perm_auth_key_id
        self.nonce = nonce
        self.expires_at = expires_at
        self.encrypted_message = encrypted_message
        return self


class ImportBotAuthorization(TLFunction["base.auth.Authorization"]):
    """The TL function auth.importBotAuthorization#67a3ff2c, answered with auth.Authorization."""

    __slots__ = ("flags", "api_id", "api_hash", "bot_auth_token",)

    ID = 0x67A3FF2C
    QUALNAME = "functions.auth.ImportBotAuthorization"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        flags: int,
        api_id: int,
        api_hash: str,
        bot_auth_token: str,
    ) -> None:
        self.flags = flags
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_auth_token = bot_auth_token

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.flags)
        w.write_int(self.api_id)
        w.write_string(self.api_hash)
        w.write_string(self.bot_auth_token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        api_id = r.read_int()
        api_hash = r.read_string()
        bot_auth_token = r.read_string()
        self = cls.__new__(cls)
        self.flags = flags
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_auth_token = bot_auth_token
        return self


class CheckPassword(TLFunction["base.auth.Authorization"]):
    """The TL function auth.checkPassword#d18b4d16, answered with auth.Authorization."""

    __slots__ = ("password",)

    ID = 0xD18B4D16
    QUALNAME = "functions.auth.CheckPassword"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        password: base.InputCheckPasswordSRP,
    ) -> None:
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        password = r.read_object()
        self = cls.__new__(cls)
        self.password = password
        return self


class RequestPasswordRecovery(TLFunction["base.auth.PasswordRecovery"]):
    """The TL function auth.requestPasswordRecovery#d897bc66, answered with auth.PasswordRecovery."""

    __slots__ = ()

    ID = 0xD897BC66
    QUALNAME = "functions.auth.RequestPasswordRecovery"
    RESULT = "auth.PasswordRecovery"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RecoverPassword(TLFunction["base.auth.Authorization"]):
    """The TL function auth.recoverPassword#37096c70, answered with auth.Authorization."""

    __slots__ = ("code", "new_settings",)

    ID = 0x37096C70
    QUALNAME = "functions.auth.RecoverPassword"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        code: str,
        new_settings: base.account.PasswordInputSettings | None = None,
    ) -> None:
        self.code = code
        self.new_settings = new_settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.new_settings is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.code)
        if self.new_settings is not None:
            self.new_settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        code = r.read_string()
        new_settings = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.code = code
        self.new_settings = new_settings
        return self


class ResendCode(TLFunction["base.auth.SentCode"]):
    """The TL function auth.resendCode#cae47523, answered with auth.SentCode."""

    __slots__ = ("phone_number", "phone_code_hash", "reason",)

    ID = 0xCAE47523
    QUALNAME = "functions.auth.ResendCode"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        reason: str | None = None,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.reason = reason

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.reason is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        if self.reason is not None:
            w.write_string(self.reason)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        reason = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.reason = reason
        return self


class CancelCode(TLFunction["bool"]):
    """The TL function auth.cancelCode#1f040578, answered with Bool."""

    __slots__ = ("phone_number", "phone_code_hash",)

    ID = 0x1F040578
    QUALNAME = "functions.auth.CancelCode"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        return self


class DropTempAuthKeys(TLFunction["bool"]):
    """The TL function auth.dropTempAuthKeys#8e48a188, answered with Bool."""

    __slots__ = ("except_auth_keys",)

    ID = 0x8E48A188
    QUALNAME = "functions.auth.DropTempAuthKeys"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        except_auth_keys: list[int],
    ) -> None:
        self.except_auth_keys = except_auth_keys

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.except_auth_keys, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        except_auth_keys = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.except_auth_keys = except_auth_keys
        return self


class ExportLoginToken(TLFunction["base.auth.LoginToken"]):
    """The TL function auth.exportLoginToken#b7e085fe, answered with auth.LoginToken."""

    __slots__ = ("api_id", "api_hash", "except_ids",)

    ID = 0xB7E085FE
    QUALNAME = "functions.auth.ExportLoginToken"
    RESULT = "auth.LoginToken"

    def __init__(
        self,
        *,
        api_id: int,
        api_hash: str,
        except_ids: list[int],
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.except_ids = except_ids

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.api_id)
        w.write_string(self.api_hash)
        w.write_vector(self.except_ids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        api_id = r.read_int()
        api_hash = r.read_string()
        except_ids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.api_id = api_id
        self.api_hash = api_hash
        self.except_ids = except_ids
        return self


class ImportLoginToken(TLFunction["base.auth.LoginToken"]):
    """The TL function auth.importLoginToken#95ac5ce4, answered with auth.LoginToken."""

    __slots__ = ("token",)

    ID = 0x95AC5CE4
    QUALNAME = "functions.auth.ImportLoginToken"
    RESULT = "auth.LoginToken"

    def __init__(
        self,
        *,
        token: bytes,
    ) -> None:
        self.token = token

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        token = r.read_bytes()
        self = cls.__new__(cls)
        self.token = token
        return self


class AcceptLoginToken(TLFunction["base.Authorization"]):
    """The TL function auth.acceptLoginToken#e894ad4d, answered with Authorization."""

    __slots__ = ("token",)

    ID = 0xE894AD4D
    QUALNAME = "functions.auth.AcceptLoginToken"
    RESULT = "Authorization"

    def __init__(
        self,
        *,
        token: bytes,
    ) -> None:
        self.token = token

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        token = r.read_bytes()
        self = cls.__new__(cls)
        self.token = token
        return self


class CheckRecoveryPassword(TLFunction["bool"]):
    """The TL function auth.checkRecoveryPassword#0d36bf79, answered with Bool."""

    __slots__ = ("code",)

    ID = 0x0D36BF79
    QUALNAME = "functions.auth.CheckRecoveryPassword"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        code: str,
    ) -> None:
        self.code = code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        code = r.read_string()
        self = cls.__new__(cls)
        self.code = code
        return self


class ImportWebTokenAuthorization(TLFunction["base.auth.Authorization"]):
    """The TL function auth.importWebTokenAuthorization#2db873a9, answered with auth.Authorization."""

    __slots__ = ("api_id", "api_hash", "web_auth_token",)

    ID = 0x2DB873A9
    QUALNAME = "functions.auth.ImportWebTokenAuthorization"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        api_id: int,
        api_hash: str,
        web_auth_token: str,
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.web_auth_token = web_auth_token

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.api_id)
        w.write_string(self.api_hash)
        w.write_string(self.web_auth_token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        api_id = r.read_int()
        api_hash = r.read_string()
        web_auth_token = r.read_string()
        self = cls.__new__(cls)
        self.api_id = api_id
        self.api_hash = api_hash
        self.web_auth_token = web_auth_token
        return self


class RequestFirebaseSms(TLFunction["bool"]):
    """The TL function auth.requestFirebaseSms#8e39261e, answered with Bool."""

    __slots__ = ("phone_number", "phone_code_hash", "safety_net_token", "play_integrity_token", "ios_push_secret",)

    ID = 0x8E39261E
    QUALNAME = "functions.auth.RequestFirebaseSms"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        safety_net_token: str | None = None,
        play_integrity_token: str | None = None,
        ios_push_secret: str | None = None,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.safety_net_token = safety_net_token
        self.play_integrity_token = play_integrity_token
        self.ios_push_secret = ios_push_secret

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.safety_net_token is not None:
            flags |= 1 << 0
        if self.play_integrity_token is not None:
            flags |= 1 << 2
        if self.ios_push_secret is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        if self.safety_net_token is not None:
            w.write_string(self.safety_net_token)
        if self.play_integrity_token is not None:
            w.write_string(self.play_integrity_token)
        if self.ios_push_secret is not None:
            w.write_string(self.ios_push_secret)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        safety_net_token = r.read_string() if flags & (1 << 0) else None
        play_integrity_token = r.read_string() if flags & (1 << 2) else None
        ios_push_secret = r.read_string() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.safety_net_token = safety_net_token
        self.play_integrity_token = play_integrity_token
        self.ios_push_secret = ios_push_secret
        return self


class ResetLoginEmail(TLFunction["base.auth.SentCode"]):
    """The TL function auth.resetLoginEmail#7e960193, answered with auth.SentCode."""

    __slots__ = ("phone_number", "phone_code_hash",)

    ID = 0x7E960193
    QUALNAME = "functions.auth.ResetLoginEmail"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        return self


class ReportMissingCode(TLFunction["bool"]):
    """The TL function auth.reportMissingCode#cb9deff6, answered with Bool."""

    __slots__ = ("phone_number", "phone_code_hash", "mnc",)

    ID = 0xCB9DEFF6
    QUALNAME = "functions.auth.ReportMissingCode"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        mnc: str,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.mnc = mnc

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        w.write_string(self.mnc)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        mnc = r.read_string()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.mnc = mnc
        return self


class CheckPaidAuth(TLFunction["base.auth.SentCode"]):
    """The TL function auth.checkPaidAuth#56e59f9c, answered with auth.SentCode."""

    __slots__ = ("phone_number", "phone_code_hash", "form_id",)

    ID = 0x56E59F9C
    QUALNAME = "functions.auth.CheckPaidAuth"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        form_id: int,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.form_id = form_id

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        w.write_long(self.form_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        form_id = r.read_long()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.form_id = form_id
        return self


class InitPasskeyLogin(TLFunction["base.auth.PasskeyLoginOptions"]):
    """The TL function auth.initPasskeyLogin#518ad0b7, answered with auth.PasskeyLoginOptions."""

    __slots__ = ("api_id", "api_hash",)

    ID = 0x518AD0B7
    QUALNAME = "functions.auth.InitPasskeyLogin"
    RESULT = "auth.PasskeyLoginOptions"

    def __init__(
        self,
        *,
        api_id: int,
        api_hash: str,
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.api_id)
        w.write_string(self.api_hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        api_id = r.read_int()
        api_hash = r.read_string()
        self = cls.__new__(cls)
        self.api_id = api_id
        self.api_hash = api_hash
        return self


class FinishPasskeyLogin(TLFunction["base.auth.Authorization"]):
    """The TL function auth.finishPasskeyLogin#9857ad07, answered with auth.Authorization."""

    __slots__ = ("credential", "from_dc_id", "from_auth_key_id",)

    ID = 0x9857AD07
    QUALNAME = "functions.auth.FinishPasskeyLogin"
    RESULT = "auth.Authorization"

    def __init__(
        self,
        *,
        credential: base.InputPasskeyCredential,
        from_dc_id: int | None = None,
        from_auth_key_id: int | None = None,
    ) -> None:
        self.credential = credential
        self.from_dc_id = from_dc_id
        self.from_auth_key_id = from_auth_key_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.from_dc_id is not None:
            flags |= 1 << 0
        if self.from_auth_key_id is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.credential.write(w)
        if self.from_dc_id is not None:
            w.write_int(self.from_dc_id)
        if self.from_auth_key_id is not None:
            w.write_long(self.from_auth_key_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        credential = r.read_object()
        from_dc_id = r.read_int() if flags & (1 << 0) else None
        from_auth_key_id = r.read_long() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.credential = credential
        self.from_dc_id = from_dc_id
        self.from_auth_key_id = from_auth_key_id
        return self
