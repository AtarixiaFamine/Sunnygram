# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the account namespace.

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


class RegisterDevice(TLFunction["bool"]):
    """The TL function account.registerDevice#ec86017a, answered with Bool."""

    __slots__ = ("no_muted", "token_type", "token", "app_sandbox", "secret", "other_uids",)

    ID = 0xEC86017A
    QUALNAME = "functions.account.RegisterDevice"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        no_muted: bool = False,
        token_type: int,
        token: str,
        app_sandbox: bool,
        secret: bytes,
        other_uids: list[int],
    ) -> None:
        self.no_muted = no_muted
        self.token_type = token_type
        self.token = token
        self.app_sandbox = app_sandbox
        self.secret = secret
        self.other_uids = other_uids

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.no_muted:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_int(self.token_type)
        w.write_string(self.token)
        w.write_bool(self.app_sandbox)
        w.write_bytes(self.secret)
        w.write_vector(self.other_uids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        no_muted = bool(flags & (1 << 0))
        token_type = r.read_int()
        token = r.read_string()
        app_sandbox = r.read_bool()
        secret = r.read_bytes()
        other_uids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.no_muted = no_muted
        self.token_type = token_type
        self.token = token
        self.app_sandbox = app_sandbox
        self.secret = secret
        self.other_uids = other_uids
        return self


class UnregisterDevice(TLFunction["bool"]):
    """The TL function account.unregisterDevice#6a0d3206, answered with Bool."""

    __slots__ = ("token_type", "token", "other_uids",)

    ID = 0x6A0D3206
    QUALNAME = "functions.account.UnregisterDevice"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        token_type: int,
        token: str,
        other_uids: list[int],
    ) -> None:
        self.token_type = token_type
        self.token = token
        self.other_uids = other_uids

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.token_type)
        w.write_string(self.token)
        w.write_vector(self.other_uids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        token_type = r.read_int()
        token = r.read_string()
        other_uids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.token_type = token_type
        self.token = token
        self.other_uids = other_uids
        return self


class UpdateNotifySettings(TLFunction["bool"]):
    """The TL function account.updateNotifySettings#84be5b93, answered with Bool."""

    __slots__ = ("peer", "settings",)

    ID = 0x84BE5B93
    QUALNAME = "functions.account.UpdateNotifySettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputNotifyPeer,
        settings: base.InputPeerNotifySettings,
    ) -> None:
        self.peer = peer
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        self.settings = settings
        return self


class GetNotifySettings(TLFunction["base.PeerNotifySettings"]):
    """The TL function account.getNotifySettings#12b3ad31, answered with PeerNotifySettings."""

    __slots__ = ("peer",)

    ID = 0x12B3AD31
    QUALNAME = "functions.account.GetNotifySettings"
    RESULT = "PeerNotifySettings"

    def __init__(
        self,
        *,
        peer: base.InputNotifyPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class ResetNotifySettings(TLFunction["bool"]):
    """The TL function account.resetNotifySettings#db7e1747, answered with Bool."""

    __slots__ = ()

    ID = 0xDB7E1747
    QUALNAME = "functions.account.ResetNotifySettings"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UpdateProfile(TLFunction["base.User"]):
    """The TL function account.updateProfile#78515775, answered with User."""

    __slots__ = ("first_name", "last_name", "about",)

    ID = 0x78515775
    QUALNAME = "functions.account.UpdateProfile"
    RESULT = "User"

    def __init__(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        about: str | None = None,
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.about = about

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.first_name is not None:
            flags |= 1 << 0
        if self.last_name is not None:
            flags |= 1 << 1
        if self.about is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.first_name is not None:
            w.write_string(self.first_name)
        if self.last_name is not None:
            w.write_string(self.last_name)
        if self.about is not None:
            w.write_string(self.about)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        first_name = r.read_string() if flags & (1 << 0) else None
        last_name = r.read_string() if flags & (1 << 1) else None
        about = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.first_name = first_name
        self.last_name = last_name
        self.about = about
        return self


class UpdateStatus(TLFunction["bool"]):
    """The TL function account.updateStatus#6628562c, answered with Bool."""

    __slots__ = ("offline",)

    ID = 0x6628562C
    QUALNAME = "functions.account.UpdateStatus"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        offline: bool,
    ) -> None:
        self.offline = offline

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.offline)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offline = r.read_bool()
        self = cls.__new__(cls)
        self.offline = offline
        return self


class GetWallPapers(TLFunction["base.account.WallPapers"]):
    """The TL function account.getWallPapers#07967d36, answered with account.WallPapers."""

    __slots__ = ("hash",)

    ID = 0x07967D36
    QUALNAME = "functions.account.GetWallPapers"
    RESULT = "account.WallPapers"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ReportPeer(TLFunction["bool"]):
    """The TL function account.reportPeer#c5ba3d86, answered with Bool."""

    __slots__ = ("peer", "reason", "message",)

    ID = 0xC5BA3D86
    QUALNAME = "functions.account.ReportPeer"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        reason: base.ReportReason,
        message: str,
    ) -> None:
        self.peer = peer
        self.reason = reason
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.reason.write(w)
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        reason = r.read_object()
        message = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.reason = reason
        self.message = message
        return self


class CheckUsername(TLFunction["bool"]):
    """The TL function account.checkUsername#2714d86c, answered with Bool."""

    __slots__ = ("username",)

    ID = 0x2714D86C
    QUALNAME = "functions.account.CheckUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        username: str,
    ) -> None:
        self.username = username

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.username)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        username = r.read_string()
        self = cls.__new__(cls)
        self.username = username
        return self


class UpdateUsername(TLFunction["base.User"]):
    """The TL function account.updateUsername#3e0bdd7c, answered with User."""

    __slots__ = ("username",)

    ID = 0x3E0BDD7C
    QUALNAME = "functions.account.UpdateUsername"
    RESULT = "User"

    def __init__(
        self,
        *,
        username: str,
    ) -> None:
        self.username = username

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.username)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        username = r.read_string()
        self = cls.__new__(cls)
        self.username = username
        return self


class GetPrivacy(TLFunction["base.account.PrivacyRules"]):
    """The TL function account.getPrivacy#dadbc950, answered with account.PrivacyRules."""

    __slots__ = ("key",)

    ID = 0xDADBC950
    QUALNAME = "functions.account.GetPrivacy"
    RESULT = "account.PrivacyRules"

    def __init__(
        self,
        *,
        key: base.InputPrivacyKey,
    ) -> None:
        self.key = key

    def write_body(self, w: TLWriter) -> None:
        self.key.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        key = r.read_object()
        self = cls.__new__(cls)
        self.key = key
        return self


class SetPrivacy(TLFunction["base.account.PrivacyRules"]):
    """The TL function account.setPrivacy#c9f81ce8, answered with account.PrivacyRules."""

    __slots__ = ("key", "rules",)

    ID = 0xC9F81CE8
    QUALNAME = "functions.account.SetPrivacy"
    RESULT = "account.PrivacyRules"

    def __init__(
        self,
        *,
        key: base.InputPrivacyKey,
        rules: list[base.InputPrivacyRule],
    ) -> None:
        self.key = key
        self.rules = rules

    def write_body(self, w: TLWriter) -> None:
        self.key.write(w)
        w.write_vector(self.rules)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        key = r.read_object()
        rules = r.read_vector()
        self = cls.__new__(cls)
        self.key = key
        self.rules = rules
        return self


class DeleteAccount(TLFunction["bool"]):
    """The TL function account.deleteAccount#a2c0cf74, answered with Bool."""

    __slots__ = ("reason", "password",)

    ID = 0xA2C0CF74
    QUALNAME = "functions.account.DeleteAccount"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        reason: str,
        password: base.InputCheckPasswordSRP | None = None,
    ) -> None:
        self.reason = reason
        self.password = password

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.password is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.reason)
        if self.password is not None:
            self.password.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        reason = r.read_string()
        password = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.reason = reason
        self.password = password
        return self


class GetAccountTTL(TLFunction["base.AccountDaysTTL"]):
    """The TL function account.getAccountTTL#08fc711d, answered with AccountDaysTTL."""

    __slots__ = ()

    ID = 0x08FC711D
    QUALNAME = "functions.account.GetAccountTTL"
    RESULT = "AccountDaysTTL"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetAccountTTL(TLFunction["bool"]):
    """The TL function account.setAccountTTL#2442485e, answered with Bool."""

    __slots__ = ("ttl",)

    ID = 0x2442485E
    QUALNAME = "functions.account.SetAccountTTL"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        ttl: base.AccountDaysTTL,
    ) -> None:
        self.ttl = ttl

    def write_body(self, w: TLWriter) -> None:
        self.ttl.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ttl = r.read_object()
        self = cls.__new__(cls)
        self.ttl = ttl
        return self


class SendChangePhoneCode(TLFunction["base.auth.SentCode"]):
    """The TL function account.sendChangePhoneCode#82574ae5, answered with auth.SentCode."""

    __slots__ = ("phone_number", "settings",)

    ID = 0x82574AE5
    QUALNAME = "functions.account.SendChangePhoneCode"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        settings: base.CodeSettings,
    ) -> None:
        self.phone_number = phone_number
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.settings = settings
        return self


class ChangePhone(TLFunction["base.User"]):
    """The TL function account.changePhone#70c32edb, answered with User."""

    __slots__ = ("phone_number", "phone_code_hash", "phone_code",)

    ID = 0x70C32EDB
    QUALNAME = "functions.account.ChangePhone"
    RESULT = "User"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        phone_code: str,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        w.write_string(self.phone_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        phone_code = r.read_string()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        return self


class UpdateDeviceLocked(TLFunction["bool"]):
    """The TL function account.updateDeviceLocked#38df3532, answered with Bool."""

    __slots__ = ("period",)

    ID = 0x38DF3532
    QUALNAME = "functions.account.UpdateDeviceLocked"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        period: int,
    ) -> None:
        self.period = period

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        period = r.read_int()
        self = cls.__new__(cls)
        self.period = period
        return self


class GetAuthorizations(TLFunction["base.account.Authorizations"]):
    """The TL function account.getAuthorizations#e320c158, answered with account.Authorizations."""

    __slots__ = ()

    ID = 0xE320C158
    QUALNAME = "functions.account.GetAuthorizations"
    RESULT = "account.Authorizations"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ResetAuthorization(TLFunction["bool"]):
    """The TL function account.resetAuthorization#df77f3bc, answered with Bool."""

    __slots__ = ("hash",)

    ID = 0xDF77F3BC
    QUALNAME = "functions.account.ResetAuthorization"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetPassword(TLFunction["base.account.Password"]):
    """The TL function account.getPassword#548a30f5, answered with account.Password."""

    __slots__ = ()

    ID = 0x548A30F5
    QUALNAME = "functions.account.GetPassword"
    RESULT = "account.Password"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetPasswordSettings(TLFunction["base.account.PasswordSettings"]):
    """The TL function account.getPasswordSettings#9cd4eaf9, answered with account.PasswordSettings."""

    __slots__ = ("password",)

    ID = 0x9CD4EAF9
    QUALNAME = "functions.account.GetPasswordSettings"
    RESULT = "account.PasswordSettings"

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


class UpdatePasswordSettings(TLFunction["bool"]):
    """The TL function account.updatePasswordSettings#a59b102f, answered with Bool."""

    __slots__ = ("password", "new_settings",)

    ID = 0xA59B102F
    QUALNAME = "functions.account.UpdatePasswordSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        password: base.InputCheckPasswordSRP,
        new_settings: base.account.PasswordInputSettings,
    ) -> None:
        self.password = password
        self.new_settings = new_settings

    def write_body(self, w: TLWriter) -> None:
        self.password.write(w)
        self.new_settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        password = r.read_object()
        new_settings = r.read_object()
        self = cls.__new__(cls)
        self.password = password
        self.new_settings = new_settings
        return self


class SendConfirmPhoneCode(TLFunction["base.auth.SentCode"]):
    """The TL function account.sendConfirmPhoneCode#1b3faa88, answered with auth.SentCode."""

    __slots__ = ("hash", "settings",)

    ID = 0x1B3FAA88
    QUALNAME = "functions.account.SendConfirmPhoneCode"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        hash: str,
        settings: base.CodeSettings,
    ) -> None:
        self.hash = hash
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.hash)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_string()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.hash = hash
        self.settings = settings
        return self


class ConfirmPhone(TLFunction["bool"]):
    """The TL function account.confirmPhone#5f2178c3, answered with Bool."""

    __slots__ = ("phone_code_hash", "phone_code",)

    ID = 0x5F2178C3
    QUALNAME = "functions.account.ConfirmPhone"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phone_code_hash: str,
        phone_code: str,
    ) -> None:
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_code_hash)
        w.write_string(self.phone_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_code_hash = r.read_string()
        phone_code = r.read_string()
        self = cls.__new__(cls)
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        return self


class GetTmpPassword(TLFunction["base.account.TmpPassword"]):
    """The TL function account.getTmpPassword#449e0b51, answered with account.TmpPassword."""

    __slots__ = ("password", "period",)

    ID = 0x449E0B51
    QUALNAME = "functions.account.GetTmpPassword"
    RESULT = "account.TmpPassword"

    def __init__(
        self,
        *,
        password: base.InputCheckPasswordSRP,
        period: int,
    ) -> None:
        self.password = password
        self.period = period

    def write_body(self, w: TLWriter) -> None:
        self.password.write(w)
        w.write_int(self.period)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        password = r.read_object()
        period = r.read_int()
        self = cls.__new__(cls)
        self.password = password
        self.period = period
        return self


class GetWebAuthorizations(TLFunction["base.account.WebAuthorizations"]):
    """The TL function account.getWebAuthorizations#182e6d6f, answered with account.WebAuthorizations."""

    __slots__ = ()

    ID = 0x182E6D6F
    QUALNAME = "functions.account.GetWebAuthorizations"
    RESULT = "account.WebAuthorizations"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ResetWebAuthorization(TLFunction["bool"]):
    """The TL function account.resetWebAuthorization#2d01b9ef, answered with Bool."""

    __slots__ = ("hash",)

    ID = 0x2D01B9EF
    QUALNAME = "functions.account.ResetWebAuthorization"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ResetWebAuthorizations(TLFunction["bool"]):
    """The TL function account.resetWebAuthorizations#682d2594, answered with Bool."""

    __slots__ = ()

    ID = 0x682D2594
    QUALNAME = "functions.account.ResetWebAuthorizations"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetAllSecureValues(TLFunction["list[base.SecureValue]"]):
    """The TL function account.getAllSecureValues#b288bc7d, answered with Vector<SecureValue>."""

    __slots__ = ()

    ID = 0xB288BC7D
    QUALNAME = "functions.account.GetAllSecureValues"
    RESULT = "Vector<SecureValue>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSecureValue(TLFunction["list[base.SecureValue]"]):
    """The TL function account.getSecureValue#73665bc2, answered with Vector<SecureValue>."""

    __slots__ = ("types",)

    ID = 0x73665BC2
    QUALNAME = "functions.account.GetSecureValue"
    RESULT = "Vector<SecureValue>"

    def __init__(
        self,
        *,
        types: list[base.SecureValueType],
    ) -> None:
        self.types = types

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.types)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        types = r.read_vector()
        self = cls.__new__(cls)
        self.types = types
        return self


class SaveSecureValue(TLFunction["base.SecureValue"]):
    """The TL function account.saveSecureValue#899fe31d, answered with SecureValue."""

    __slots__ = ("value", "secure_secret_id",)

    ID = 0x899FE31D
    QUALNAME = "functions.account.SaveSecureValue"
    RESULT = "SecureValue"

    def __init__(
        self,
        *,
        value: base.InputSecureValue,
        secure_secret_id: int,
    ) -> None:
        self.value = value
        self.secure_secret_id = secure_secret_id

    def write_body(self, w: TLWriter) -> None:
        self.value.write(w)
        w.write_long(self.secure_secret_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        value = r.read_object()
        secure_secret_id = r.read_long()
        self = cls.__new__(cls)
        self.value = value
        self.secure_secret_id = secure_secret_id
        return self


class DeleteSecureValue(TLFunction["bool"]):
    """The TL function account.deleteSecureValue#b880bc4b, answered with Bool."""

    __slots__ = ("types",)

    ID = 0xB880BC4B
    QUALNAME = "functions.account.DeleteSecureValue"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        types: list[base.SecureValueType],
    ) -> None:
        self.types = types

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.types)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        types = r.read_vector()
        self = cls.__new__(cls)
        self.types = types
        return self


class GetAuthorizationForm(TLFunction["base.account.AuthorizationForm"]):
    """The TL function account.getAuthorizationForm#a929597a, answered with account.AuthorizationForm."""

    __slots__ = ("bot_id", "scope", "public_key",)

    ID = 0xA929597A
    QUALNAME = "functions.account.GetAuthorizationForm"
    RESULT = "account.AuthorizationForm"

    def __init__(
        self,
        *,
        bot_id: int,
        scope: str,
        public_key: str,
    ) -> None:
        self.bot_id = bot_id
        self.scope = scope
        self.public_key = public_key

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.bot_id)
        w.write_string(self.scope)
        w.write_string(self.public_key)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot_id = r.read_long()
        scope = r.read_string()
        public_key = r.read_string()
        self = cls.__new__(cls)
        self.bot_id = bot_id
        self.scope = scope
        self.public_key = public_key
        return self


class AcceptAuthorization(TLFunction["bool"]):
    """The TL function account.acceptAuthorization#f3ed4c73, answered with Bool."""

    __slots__ = ("bot_id", "scope", "public_key", "value_hashes", "credentials",)

    ID = 0xF3ED4C73
    QUALNAME = "functions.account.AcceptAuthorization"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot_id: int,
        scope: str,
        public_key: str,
        value_hashes: list[base.SecureValueHash],
        credentials: base.SecureCredentialsEncrypted,
    ) -> None:
        self.bot_id = bot_id
        self.scope = scope
        self.public_key = public_key
        self.value_hashes = value_hashes
        self.credentials = credentials

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.bot_id)
        w.write_string(self.scope)
        w.write_string(self.public_key)
        w.write_vector(self.value_hashes)
        self.credentials.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot_id = r.read_long()
        scope = r.read_string()
        public_key = r.read_string()
        value_hashes = r.read_vector()
        credentials = r.read_object()
        self = cls.__new__(cls)
        self.bot_id = bot_id
        self.scope = scope
        self.public_key = public_key
        self.value_hashes = value_hashes
        self.credentials = credentials
        return self


class SendVerifyPhoneCode(TLFunction["base.auth.SentCode"]):
    """The TL function account.sendVerifyPhoneCode#a5a356f9, answered with auth.SentCode."""

    __slots__ = ("phone_number", "settings",)

    ID = 0xA5A356F9
    QUALNAME = "functions.account.SendVerifyPhoneCode"
    RESULT = "auth.SentCode"

    def __init__(
        self,
        *,
        phone_number: str,
        settings: base.CodeSettings,
    ) -> None:
        self.phone_number = phone_number
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.settings = settings
        return self


class VerifyPhone(TLFunction["bool"]):
    """The TL function account.verifyPhone#4dd3a7f6, answered with Bool."""

    __slots__ = ("phone_number", "phone_code_hash", "phone_code",)

    ID = 0x4DD3A7F6
    QUALNAME = "functions.account.VerifyPhone"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        phone_number: str,
        phone_code_hash: str,
        phone_code: str,
    ) -> None:
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        w.write_string(self.phone_code_hash)
        w.write_string(self.phone_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        phone_code_hash = r.read_string()
        phone_code = r.read_string()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        return self


class SendVerifyEmailCode(TLFunction["base.account.SentEmailCode"]):
    """The TL function account.sendVerifyEmailCode#98e037bb, answered with account.SentEmailCode."""

    __slots__ = ("purpose", "email",)

    ID = 0x98E037BB
    QUALNAME = "functions.account.SendVerifyEmailCode"
    RESULT = "account.SentEmailCode"

    def __init__(
        self,
        *,
        purpose: base.EmailVerifyPurpose,
        email: str,
    ) -> None:
        self.purpose = purpose
        self.email = email

    def write_body(self, w: TLWriter) -> None:
        self.purpose.write(w)
        w.write_string(self.email)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        purpose = r.read_object()
        email = r.read_string()
        self = cls.__new__(cls)
        self.purpose = purpose
        self.email = email
        return self


class VerifyEmail(TLFunction["base.account.EmailVerified"]):
    """The TL function account.verifyEmail#032da4cf, answered with account.EmailVerified."""

    __slots__ = ("purpose", "verification",)

    ID = 0x032DA4CF
    QUALNAME = "functions.account.VerifyEmail"
    RESULT = "account.EmailVerified"

    def __init__(
        self,
        *,
        purpose: base.EmailVerifyPurpose,
        verification: base.EmailVerification,
    ) -> None:
        self.purpose = purpose
        self.verification = verification

    def write_body(self, w: TLWriter) -> None:
        self.purpose.write(w)
        self.verification.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        purpose = r.read_object()
        verification = r.read_object()
        self = cls.__new__(cls)
        self.purpose = purpose
        self.verification = verification
        return self


class InitTakeoutSession(TLFunction["base.account.Takeout"]):
    """The TL function account.initTakeoutSession#8ef3eab0, answered with account.Takeout."""

    __slots__ = ("contacts", "message_users", "message_chats", "message_megagroups", "message_channels", "files", "file_max_size",)

    ID = 0x8EF3EAB0
    QUALNAME = "functions.account.InitTakeoutSession"
    RESULT = "account.Takeout"

    def __init__(
        self,
        *,
        contacts: bool = False,
        message_users: bool = False,
        message_chats: bool = False,
        message_megagroups: bool = False,
        message_channels: bool = False,
        files: bool = False,
        file_max_size: int | None = None,
    ) -> None:
        self.contacts = contacts
        self.message_users = message_users
        self.message_chats = message_chats
        self.message_megagroups = message_megagroups
        self.message_channels = message_channels
        self.files = files
        self.file_max_size = file_max_size

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.contacts:
            flags |= 1 << 0
        if self.message_users:
            flags |= 1 << 1
        if self.message_chats:
            flags |= 1 << 2
        if self.message_megagroups:
            flags |= 1 << 3
        if self.message_channels:
            flags |= 1 << 4
        if self.files:
            flags |= 1 << 5
        if self.file_max_size is not None:
            flags |= 1 << 5
        w.write_int(flags)
        if self.file_max_size is not None:
            w.write_long(self.file_max_size)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        contacts = bool(flags & (1 << 0))
        message_users = bool(flags & (1 << 1))
        message_chats = bool(flags & (1 << 2))
        message_megagroups = bool(flags & (1 << 3))
        message_channels = bool(flags & (1 << 4))
        files = bool(flags & (1 << 5))
        file_max_size = r.read_long() if flags & (1 << 5) else None
        self = cls.__new__(cls)
        self.contacts = contacts
        self.message_users = message_users
        self.message_chats = message_chats
        self.message_megagroups = message_megagroups
        self.message_channels = message_channels
        self.files = files
        self.file_max_size = file_max_size
        return self


class FinishTakeoutSession(TLFunction["bool"]):
    """The TL function account.finishTakeoutSession#1d2652ee, answered with Bool."""

    __slots__ = ("success",)

    ID = 0x1D2652EE
    QUALNAME = "functions.account.FinishTakeoutSession"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        success: bool = False,
    ) -> None:
        self.success = success

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.success:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        success = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.success = success
        return self


class ConfirmPasswordEmail(TLFunction["bool"]):
    """The TL function account.confirmPasswordEmail#8fdf1920, answered with Bool."""

    __slots__ = ("code",)

    ID = 0x8FDF1920
    QUALNAME = "functions.account.ConfirmPasswordEmail"
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


class ResendPasswordEmail(TLFunction["bool"]):
    """The TL function account.resendPasswordEmail#7a7f2a15, answered with Bool."""

    __slots__ = ()

    ID = 0x7A7F2A15
    QUALNAME = "functions.account.ResendPasswordEmail"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CancelPasswordEmail(TLFunction["bool"]):
    """The TL function account.cancelPasswordEmail#c1cbd5b6, answered with Bool."""

    __slots__ = ()

    ID = 0xC1CBD5B6
    QUALNAME = "functions.account.CancelPasswordEmail"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetContactSignUpNotification(TLFunction["bool"]):
    """The TL function account.getContactSignUpNotification#9f07c728, answered with Bool."""

    __slots__ = ()

    ID = 0x9F07C728
    QUALNAME = "functions.account.GetContactSignUpNotification"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetContactSignUpNotification(TLFunction["bool"]):
    """The TL function account.setContactSignUpNotification#cff43f61, answered with Bool."""

    __slots__ = ("silent",)

    ID = 0xCFF43F61
    QUALNAME = "functions.account.SetContactSignUpNotification"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        silent: bool,
    ) -> None:
        self.silent = silent

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.silent)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        silent = r.read_bool()
        self = cls.__new__(cls)
        self.silent = silent
        return self


class GetNotifyExceptions(TLFunction["base.Updates"]):
    """The TL function account.getNotifyExceptions#53577479, answered with Updates."""

    __slots__ = ("compare_sound", "compare_stories", "peer",)

    ID = 0x53577479
    QUALNAME = "functions.account.GetNotifyExceptions"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        compare_sound: bool = False,
        compare_stories: bool = False,
        peer: base.InputNotifyPeer | None = None,
    ) -> None:
        self.compare_sound = compare_sound
        self.compare_stories = compare_stories
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.compare_sound:
            flags |= 1 << 1
        if self.compare_stories:
            flags |= 1 << 2
        if self.peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        compare_sound = bool(flags & (1 << 1))
        compare_stories = bool(flags & (1 << 2))
        peer = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.compare_sound = compare_sound
        self.compare_stories = compare_stories
        self.peer = peer
        return self


class GetWallPaper(TLFunction["base.WallPaper"]):
    """The TL function account.getWallPaper#fc8ddbea, answered with WallPaper."""

    __slots__ = ("wallpaper",)

    ID = 0xFC8DDBEA
    QUALNAME = "functions.account.GetWallPaper"
    RESULT = "WallPaper"

    def __init__(
        self,
        *,
        wallpaper: base.InputWallPaper,
    ) -> None:
        self.wallpaper = wallpaper

    def write_body(self, w: TLWriter) -> None:
        self.wallpaper.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        wallpaper = r.read_object()
        self = cls.__new__(cls)
        self.wallpaper = wallpaper
        return self


class UploadWallPaper(TLFunction["base.WallPaper"]):
    """The TL function account.uploadWallPaper#e39a8f03, answered with WallPaper."""

    __slots__ = ("for_chat", "file", "mime_type", "settings",)

    ID = 0xE39A8F03
    QUALNAME = "functions.account.UploadWallPaper"
    RESULT = "WallPaper"

    def __init__(
        self,
        *,
        for_chat: bool = False,
        file: base.InputFile,
        mime_type: str,
        settings: base.WallPaperSettings,
    ) -> None:
        self.for_chat = for_chat
        self.file = file
        self.mime_type = mime_type
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_chat:
            flags |= 1 << 0
        w.write_int(flags)
        self.file.write(w)
        w.write_string(self.mime_type)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_chat = bool(flags & (1 << 0))
        file = r.read_object()
        mime_type = r.read_string()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.for_chat = for_chat
        self.file = file
        self.mime_type = mime_type
        self.settings = settings
        return self


class SaveWallPaper(TLFunction["bool"]):
    """The TL function account.saveWallPaper#6c5a5b37, answered with Bool."""

    __slots__ = ("wallpaper", "unsave", "settings",)

    ID = 0x6C5A5B37
    QUALNAME = "functions.account.SaveWallPaper"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        wallpaper: base.InputWallPaper,
        unsave: bool,
        settings: base.WallPaperSettings,
    ) -> None:
        self.wallpaper = wallpaper
        self.unsave = unsave
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        self.wallpaper.write(w)
        w.write_bool(self.unsave)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        wallpaper = r.read_object()
        unsave = r.read_bool()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.wallpaper = wallpaper
        self.unsave = unsave
        self.settings = settings
        return self


class InstallWallPaper(TLFunction["bool"]):
    """The TL function account.installWallPaper#feed5769, answered with Bool."""

    __slots__ = ("wallpaper", "settings",)

    ID = 0xFEED5769
    QUALNAME = "functions.account.InstallWallPaper"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        wallpaper: base.InputWallPaper,
        settings: base.WallPaperSettings,
    ) -> None:
        self.wallpaper = wallpaper
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        self.wallpaper.write(w)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        wallpaper = r.read_object()
        settings = r.read_object()
        self = cls.__new__(cls)
        self.wallpaper = wallpaper
        self.settings = settings
        return self


class ResetWallPapers(TLFunction["bool"]):
    """The TL function account.resetWallPapers#bb3b9804, answered with Bool."""

    __slots__ = ()

    ID = 0xBB3B9804
    QUALNAME = "functions.account.ResetWallPapers"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetAutoDownloadSettings(TLFunction["base.account.AutoDownloadSettings"]):
    """The TL function account.getAutoDownloadSettings#56da0b3f, answered with account.AutoDownloadSettings."""

    __slots__ = ()

    ID = 0x56DA0B3F
    QUALNAME = "functions.account.GetAutoDownloadSettings"
    RESULT = "account.AutoDownloadSettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SaveAutoDownloadSettings(TLFunction["bool"]):
    """The TL function account.saveAutoDownloadSettings#76f36233, answered with Bool."""

    __slots__ = ("low", "high", "settings",)

    ID = 0x76F36233
    QUALNAME = "functions.account.SaveAutoDownloadSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        low: bool = False,
        high: bool = False,
        settings: base.AutoDownloadSettings,
    ) -> None:
        self.low = low
        self.high = high
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.low:
            flags |= 1 << 0
        if self.high:
            flags |= 1 << 1
        w.write_int(flags)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        low = bool(flags & (1 << 0))
        high = bool(flags & (1 << 1))
        settings = r.read_object()
        self = cls.__new__(cls)
        self.low = low
        self.high = high
        self.settings = settings
        return self


class UploadTheme(TLFunction["base.Document"]):
    """The TL function account.uploadTheme#1c3db333, answered with Document."""

    __slots__ = ("file", "thumb", "file_name", "mime_type",)

    ID = 0x1C3DB333
    QUALNAME = "functions.account.UploadTheme"
    RESULT = "Document"

    def __init__(
        self,
        *,
        file: base.InputFile,
        thumb: base.InputFile | None = None,
        file_name: str,
        mime_type: str,
    ) -> None:
        self.file = file
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.thumb is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.file.write(w)
        if self.thumb is not None:
            self.thumb.write(w)
        w.write_string(self.file_name)
        w.write_string(self.mime_type)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        file = r.read_object()
        thumb = r.read_object() if flags & (1 << 0) else None
        file_name = r.read_string()
        mime_type = r.read_string()
        self = cls.__new__(cls)
        self.file = file
        self.thumb = thumb
        self.file_name = file_name
        self.mime_type = mime_type
        return self


class CreateTheme(TLFunction["base.Theme"]):
    """The TL function account.createTheme#652e4400, answered with Theme."""

    __slots__ = ("slug", "title", "document", "settings",)

    ID = 0x652E4400
    QUALNAME = "functions.account.CreateTheme"
    RESULT = "Theme"

    def __init__(
        self,
        *,
        slug: str,
        title: str,
        document: base.InputDocument | None = None,
        settings: list[base.InputThemeSettings] | None = None,
    ) -> None:
        self.slug = slug
        self.title = title
        self.document = document
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.document is not None:
            flags |= 1 << 2
        if self.settings is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_string(self.slug)
        w.write_string(self.title)
        if self.document is not None:
            self.document.write(w)
        if self.settings is not None:
            w.write_vector(self.settings)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        slug = r.read_string()
        title = r.read_string()
        document = r.read_object() if flags & (1 << 2) else None
        settings = r.read_vector() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.slug = slug
        self.title = title
        self.document = document
        self.settings = settings
        return self


class UpdateTheme(TLFunction["base.Theme"]):
    """The TL function account.updateTheme#2bf40ccc, answered with Theme."""

    __slots__ = ("format", "theme", "slug", "title", "document", "settings",)

    ID = 0x2BF40CCC
    QUALNAME = "functions.account.UpdateTheme"
    RESULT = "Theme"

    def __init__(
        self,
        *,
        format: str,
        theme: base.InputTheme,
        slug: str | None = None,
        title: str | None = None,
        document: base.InputDocument | None = None,
        settings: list[base.InputThemeSettings] | None = None,
    ) -> None:
        self.format = format
        self.theme = theme
        self.slug = slug
        self.title = title
        self.document = document
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.slug is not None:
            flags |= 1 << 0
        if self.title is not None:
            flags |= 1 << 1
        if self.document is not None:
            flags |= 1 << 2
        if self.settings is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_string(self.format)
        self.theme.write(w)
        if self.slug is not None:
            w.write_string(self.slug)
        if self.title is not None:
            w.write_string(self.title)
        if self.document is not None:
            self.document.write(w)
        if self.settings is not None:
            w.write_vector(self.settings)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        format = r.read_string()
        theme = r.read_object()
        slug = r.read_string() if flags & (1 << 0) else None
        title = r.read_string() if flags & (1 << 1) else None
        document = r.read_object() if flags & (1 << 2) else None
        settings = r.read_vector() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.format = format
        self.theme = theme
        self.slug = slug
        self.title = title
        self.document = document
        self.settings = settings
        return self


class SaveTheme(TLFunction["bool"]):
    """The TL function account.saveTheme#f257106c, answered with Bool."""

    __slots__ = ("theme", "unsave",)

    ID = 0xF257106C
    QUALNAME = "functions.account.SaveTheme"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        theme: base.InputTheme,
        unsave: bool,
    ) -> None:
        self.theme = theme
        self.unsave = unsave

    def write_body(self, w: TLWriter) -> None:
        self.theme.write(w)
        w.write_bool(self.unsave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        theme = r.read_object()
        unsave = r.read_bool()
        self = cls.__new__(cls)
        self.theme = theme
        self.unsave = unsave
        return self


class InstallTheme(TLFunction["bool"]):
    """The TL function account.installTheme#c727bb3b, answered with Bool."""

    __slots__ = ("dark", "theme", "format", "base_theme",)

    ID = 0xC727BB3B
    QUALNAME = "functions.account.InstallTheme"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        dark: bool = False,
        theme: base.InputTheme | None = None,
        format: str | None = None,
        base_theme: base.BaseTheme | None = None,
    ) -> None:
        self.dark = dark
        self.theme = theme
        self.format = format
        self.base_theme = base_theme

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.dark:
            flags |= 1 << 0
        if self.theme is not None:
            flags |= 1 << 1
        if self.format is not None:
            flags |= 1 << 2
        if self.base_theme is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.theme is not None:
            self.theme.write(w)
        if self.format is not None:
            w.write_string(self.format)
        if self.base_theme is not None:
            self.base_theme.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        dark = bool(flags & (1 << 0))
        theme = r.read_object() if flags & (1 << 1) else None
        format = r.read_string() if flags & (1 << 2) else None
        base_theme = r.read_object() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.dark = dark
        self.theme = theme
        self.format = format
        self.base_theme = base_theme
        return self


class GetTheme(TLFunction["base.Theme"]):
    """The TL function account.getTheme#3a5869ec, answered with Theme."""

    __slots__ = ("format", "theme",)

    ID = 0x3A5869EC
    QUALNAME = "functions.account.GetTheme"
    RESULT = "Theme"

    def __init__(
        self,
        *,
        format: str,
        theme: base.InputTheme,
    ) -> None:
        self.format = format
        self.theme = theme

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.format)
        self.theme.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        format = r.read_string()
        theme = r.read_object()
        self = cls.__new__(cls)
        self.format = format
        self.theme = theme
        return self


class GetThemes(TLFunction["base.account.Themes"]):
    """The TL function account.getThemes#7206e458, answered with account.Themes."""

    __slots__ = ("format", "hash",)

    ID = 0x7206E458
    QUALNAME = "functions.account.GetThemes"
    RESULT = "account.Themes"

    def __init__(
        self,
        *,
        format: str,
        hash: int,
    ) -> None:
        self.format = format
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.format)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        format = r.read_string()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.format = format
        self.hash = hash
        return self


class SetContentSettings(TLFunction["bool"]):
    """The TL function account.setContentSettings#b574b16b, answered with Bool."""

    __slots__ = ("sensitive_enabled",)

    ID = 0xB574B16B
    QUALNAME = "functions.account.SetContentSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        sensitive_enabled: bool = False,
    ) -> None:
        self.sensitive_enabled = sensitive_enabled

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.sensitive_enabled:
            flags |= 1 << 0
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        sensitive_enabled = bool(flags & (1 << 0))
        self = cls.__new__(cls)
        self.sensitive_enabled = sensitive_enabled
        return self


class GetContentSettings(TLFunction["base.account.ContentSettings"]):
    """The TL function account.getContentSettings#8b9b4dae, answered with account.ContentSettings."""

    __slots__ = ()

    ID = 0x8B9B4DAE
    QUALNAME = "functions.account.GetContentSettings"
    RESULT = "account.ContentSettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetMultiWallPapers(TLFunction["list[base.WallPaper]"]):
    """The TL function account.getMultiWallPapers#65ad71dc, answered with Vector<WallPaper>."""

    __slots__ = ("wallpapers",)

    ID = 0x65AD71DC
    QUALNAME = "functions.account.GetMultiWallPapers"
    RESULT = "Vector<WallPaper>"

    def __init__(
        self,
        *,
        wallpapers: list[base.InputWallPaper],
    ) -> None:
        self.wallpapers = wallpapers

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.wallpapers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        wallpapers = r.read_vector()
        self = cls.__new__(cls)
        self.wallpapers = wallpapers
        return self


class GetGlobalPrivacySettings(TLFunction["base.GlobalPrivacySettings"]):
    """The TL function account.getGlobalPrivacySettings#eb2b4cf6, answered with GlobalPrivacySettings."""

    __slots__ = ()

    ID = 0xEB2B4CF6
    QUALNAME = "functions.account.GetGlobalPrivacySettings"
    RESULT = "GlobalPrivacySettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetGlobalPrivacySettings(TLFunction["base.GlobalPrivacySettings"]):
    """The TL function account.setGlobalPrivacySettings#1edaaac2, answered with GlobalPrivacySettings."""

    __slots__ = ("settings",)

    ID = 0x1EDAAAC2
    QUALNAME = "functions.account.SetGlobalPrivacySettings"
    RESULT = "GlobalPrivacySettings"

    def __init__(
        self,
        *,
        settings: base.GlobalPrivacySettings,
    ) -> None:
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        settings = r.read_object()
        self = cls.__new__(cls)
        self.settings = settings
        return self


class ReportProfilePhoto(TLFunction["bool"]):
    """The TL function account.reportProfilePhoto#fa8cc6f5, answered with Bool."""

    __slots__ = ("peer", "photo_id", "reason", "message",)

    ID = 0xFA8CC6F5
    QUALNAME = "functions.account.ReportProfilePhoto"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        photo_id: base.InputPhoto,
        reason: base.ReportReason,
        message: str,
    ) -> None:
        self.peer = peer
        self.photo_id = photo_id
        self.reason = reason
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        self.photo_id.write(w)
        self.reason.write(w)
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        photo_id = r.read_object()
        reason = r.read_object()
        message = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.photo_id = photo_id
        self.reason = reason
        self.message = message
        return self


class ResetPassword(TLFunction["base.account.ResetPasswordResult"]):
    """The TL function account.resetPassword#9308ce1b, answered with account.ResetPasswordResult."""

    __slots__ = ()

    ID = 0x9308CE1B
    QUALNAME = "functions.account.ResetPassword"
    RESULT = "account.ResetPasswordResult"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DeclinePasswordReset(TLFunction["bool"]):
    """The TL function account.declinePasswordReset#4c9409f6, answered with Bool."""

    __slots__ = ()

    ID = 0x4C9409F6
    QUALNAME = "functions.account.DeclinePasswordReset"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetChatThemes(TLFunction["base.account.Themes"]):
    """The TL function account.getChatThemes#d638de89, answered with account.Themes."""

    __slots__ = ("hash",)

    ID = 0xD638DE89
    QUALNAME = "functions.account.GetChatThemes"
    RESULT = "account.Themes"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SetAuthorizationTTL(TLFunction["bool"]):
    """The TL function account.setAuthorizationTTL#bf899aa0, answered with Bool."""

    __slots__ = ("authorization_ttl_days",)

    ID = 0xBF899AA0
    QUALNAME = "functions.account.SetAuthorizationTTL"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        authorization_ttl_days: int,
    ) -> None:
        self.authorization_ttl_days = authorization_ttl_days

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.authorization_ttl_days)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        authorization_ttl_days = r.read_int()
        self = cls.__new__(cls)
        self.authorization_ttl_days = authorization_ttl_days
        return self


class ChangeAuthorizationSettings(TLFunction["bool"]):
    """The TL function account.changeAuthorizationSettings#40f48462, answered with Bool."""

    __slots__ = ("confirmed", "hash", "encrypted_requests_disabled", "call_requests_disabled",)

    ID = 0x40F48462
    QUALNAME = "functions.account.ChangeAuthorizationSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        confirmed: bool = False,
        hash: int,
        encrypted_requests_disabled: bool | None = None,
        call_requests_disabled: bool | None = None,
    ) -> None:
        self.confirmed = confirmed
        self.hash = hash
        self.encrypted_requests_disabled = encrypted_requests_disabled
        self.call_requests_disabled = call_requests_disabled

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.confirmed:
            flags |= 1 << 3
        if self.encrypted_requests_disabled is not None:
            flags |= 1 << 0
        if self.call_requests_disabled is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_long(self.hash)
        if self.encrypted_requests_disabled is not None:
            w.write_bool(self.encrypted_requests_disabled)
        if self.call_requests_disabled is not None:
            w.write_bool(self.call_requests_disabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        confirmed = bool(flags & (1 << 3))
        hash = r.read_long()
        encrypted_requests_disabled = r.read_bool() if flags & (1 << 0) else None
        call_requests_disabled = r.read_bool() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.confirmed = confirmed
        self.hash = hash
        self.encrypted_requests_disabled = encrypted_requests_disabled
        self.call_requests_disabled = call_requests_disabled
        return self


class GetSavedRingtones(TLFunction["base.account.SavedRingtones"]):
    """The TL function account.getSavedRingtones#e1902288, answered with account.SavedRingtones."""

    __slots__ = ("hash",)

    ID = 0xE1902288
    QUALNAME = "functions.account.GetSavedRingtones"
    RESULT = "account.SavedRingtones"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SaveRingtone(TLFunction["base.account.SavedRingtone"]):
    """The TL function account.saveRingtone#3dea5b03, answered with account.SavedRingtone."""

    __slots__ = ("id", "unsave",)

    ID = 0x3DEA5B03
    QUALNAME = "functions.account.SaveRingtone"
    RESULT = "account.SavedRingtone"

    def __init__(
        self,
        *,
        id: base.InputDocument,
        unsave: bool,
    ) -> None:
        self.id = id
        self.unsave = unsave

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)
        w.write_bool(self.unsave)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        unsave = r.read_bool()
        self = cls.__new__(cls)
        self.id = id
        self.unsave = unsave
        return self


class UploadRingtone(TLFunction["base.Document"]):
    """The TL function account.uploadRingtone#831a83a2, answered with Document."""

    __slots__ = ("file", "file_name", "mime_type",)

    ID = 0x831A83A2
    QUALNAME = "functions.account.UploadRingtone"
    RESULT = "Document"

    def __init__(
        self,
        *,
        file: base.InputFile,
        file_name: str,
        mime_type: str,
    ) -> None:
        self.file = file
        self.file_name = file_name
        self.mime_type = mime_type

    def write_body(self, w: TLWriter) -> None:
        self.file.write(w)
        w.write_string(self.file_name)
        w.write_string(self.mime_type)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        file = r.read_object()
        file_name = r.read_string()
        mime_type = r.read_string()
        self = cls.__new__(cls)
        self.file = file
        self.file_name = file_name
        self.mime_type = mime_type
        return self


class UpdateEmojiStatus(TLFunction["bool"]):
    """The TL function account.updateEmojiStatus#fbd3de6b, answered with Bool."""

    __slots__ = ("emoji_status",)

    ID = 0xFBD3DE6B
    QUALNAME = "functions.account.UpdateEmojiStatus"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        emoji_status: base.EmojiStatus,
    ) -> None:
        self.emoji_status = emoji_status

    def write_body(self, w: TLWriter) -> None:
        self.emoji_status.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        emoji_status = r.read_object()
        self = cls.__new__(cls)
        self.emoji_status = emoji_status
        return self


class GetDefaultEmojiStatuses(TLFunction["base.account.EmojiStatuses"]):
    """The TL function account.getDefaultEmojiStatuses#d6753386, answered with account.EmojiStatuses."""

    __slots__ = ("hash",)

    ID = 0xD6753386
    QUALNAME = "functions.account.GetDefaultEmojiStatuses"
    RESULT = "account.EmojiStatuses"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetRecentEmojiStatuses(TLFunction["base.account.EmojiStatuses"]):
    """The TL function account.getRecentEmojiStatuses#0f578105, answered with account.EmojiStatuses."""

    __slots__ = ("hash",)

    ID = 0x0F578105
    QUALNAME = "functions.account.GetRecentEmojiStatuses"
    RESULT = "account.EmojiStatuses"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class ClearRecentEmojiStatuses(TLFunction["bool"]):
    """The TL function account.clearRecentEmojiStatuses#18201aae, answered with Bool."""

    __slots__ = ()

    ID = 0x18201AAE
    QUALNAME = "functions.account.ClearRecentEmojiStatuses"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ReorderUsernames(TLFunction["bool"]):
    """The TL function account.reorderUsernames#ef500eab, answered with Bool."""

    __slots__ = ("order",)

    ID = 0xEF500EAB
    QUALNAME = "functions.account.ReorderUsernames"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        order: list[str],
    ) -> None:
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.order, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        order = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.order = order
        return self


class ToggleUsername(TLFunction["bool"]):
    """The TL function account.toggleUsername#58d6b376, answered with Bool."""

    __slots__ = ("username", "active",)

    ID = 0x58D6B376
    QUALNAME = "functions.account.ToggleUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        username: str,
        active: bool,
    ) -> None:
        self.username = username
        self.active = active

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.username)
        w.write_bool(self.active)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        username = r.read_string()
        active = r.read_bool()
        self = cls.__new__(cls)
        self.username = username
        self.active = active
        return self


class GetDefaultProfilePhotoEmojis(TLFunction["base.EmojiList"]):
    """The TL function account.getDefaultProfilePhotoEmojis#e2750328, answered with EmojiList."""

    __slots__ = ("hash",)

    ID = 0xE2750328
    QUALNAME = "functions.account.GetDefaultProfilePhotoEmojis"
    RESULT = "EmojiList"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetDefaultGroupPhotoEmojis(TLFunction["base.EmojiList"]):
    """The TL function account.getDefaultGroupPhotoEmojis#915860ae, answered with EmojiList."""

    __slots__ = ("hash",)

    ID = 0x915860AE
    QUALNAME = "functions.account.GetDefaultGroupPhotoEmojis"
    RESULT = "EmojiList"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetAutoSaveSettings(TLFunction["base.account.AutoSaveSettings"]):
    """The TL function account.getAutoSaveSettings#adcbbcda, answered with account.AutoSaveSettings."""

    __slots__ = ()

    ID = 0xADCBBCDA
    QUALNAME = "functions.account.GetAutoSaveSettings"
    RESULT = "account.AutoSaveSettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SaveAutoSaveSettings(TLFunction["bool"]):
    """The TL function account.saveAutoSaveSettings#d69b8361, answered with Bool."""

    __slots__ = ("users", "chats", "broadcasts", "peer", "settings",)

    ID = 0xD69B8361
    QUALNAME = "functions.account.SaveAutoSaveSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        users: bool = False,
        chats: bool = False,
        broadcasts: bool = False,
        peer: base.InputPeer | None = None,
        settings: base.AutoSaveSettings,
    ) -> None:
        self.users = users
        self.chats = chats
        self.broadcasts = broadcasts
        self.peer = peer
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.users:
            flags |= 1 << 0
        if self.chats:
            flags |= 1 << 1
        if self.broadcasts:
            flags |= 1 << 2
        if self.peer is not None:
            flags |= 1 << 3
        w.write_int(flags)
        if self.peer is not None:
            self.peer.write(w)
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        users = bool(flags & (1 << 0))
        chats = bool(flags & (1 << 1))
        broadcasts = bool(flags & (1 << 2))
        peer = r.read_object() if flags & (1 << 3) else None
        settings = r.read_object()
        self = cls.__new__(cls)
        self.users = users
        self.chats = chats
        self.broadcasts = broadcasts
        self.peer = peer
        self.settings = settings
        return self


class DeleteAutoSaveExceptions(TLFunction["bool"]):
    """The TL function account.deleteAutoSaveExceptions#53bc0020, answered with Bool."""

    __slots__ = ()

    ID = 0x53BC0020
    QUALNAME = "functions.account.DeleteAutoSaveExceptions"
    RESULT = "Bool"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class InvalidateSignInCodes(TLFunction["bool"]):
    """The TL function account.invalidateSignInCodes#ca8ae8ba, answered with Bool."""

    __slots__ = ("codes",)

    ID = 0xCA8AE8BA
    QUALNAME = "functions.account.InvalidateSignInCodes"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        codes: list[str],
    ) -> None:
        self.codes = codes

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.codes, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        codes = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.codes = codes
        return self


class UpdateColor(TLFunction["bool"]):
    """The TL function account.updateColor#684d214e, answered with Bool."""

    __slots__ = ("for_profile", "color",)

    ID = 0x684D214E
    QUALNAME = "functions.account.UpdateColor"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        for_profile: bool = False,
        color: base.PeerColor | None = None,
    ) -> None:
        self.for_profile = for_profile
        self.color = color

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.for_profile:
            flags |= 1 << 1
        if self.color is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.color is not None:
            self.color.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        for_profile = bool(flags & (1 << 1))
        color = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.for_profile = for_profile
        self.color = color
        return self


class GetDefaultBackgroundEmojis(TLFunction["base.EmojiList"]):
    """The TL function account.getDefaultBackgroundEmojis#a60ab9ce, answered with EmojiList."""

    __slots__ = ("hash",)

    ID = 0xA60AB9CE
    QUALNAME = "functions.account.GetDefaultBackgroundEmojis"
    RESULT = "EmojiList"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetChannelDefaultEmojiStatuses(TLFunction["base.account.EmojiStatuses"]):
    """The TL function account.getChannelDefaultEmojiStatuses#7727a7d5, answered with account.EmojiStatuses."""

    __slots__ = ("hash",)

    ID = 0x7727A7D5
    QUALNAME = "functions.account.GetChannelDefaultEmojiStatuses"
    RESULT = "account.EmojiStatuses"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetChannelRestrictedStatusEmojis(TLFunction["base.EmojiList"]):
    """The TL function account.getChannelRestrictedStatusEmojis#35a9e0d5, answered with EmojiList."""

    __slots__ = ("hash",)

    ID = 0x35A9E0D5
    QUALNAME = "functions.account.GetChannelRestrictedStatusEmojis"
    RESULT = "EmojiList"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class UpdateBusinessWorkHours(TLFunction["bool"]):
    """The TL function account.updateBusinessWorkHours#4b00e066, answered with Bool."""

    __slots__ = ("business_work_hours",)

    ID = 0x4B00E066
    QUALNAME = "functions.account.UpdateBusinessWorkHours"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        business_work_hours: base.BusinessWorkHours | None = None,
    ) -> None:
        self.business_work_hours = business_work_hours

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.business_work_hours is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.business_work_hours is not None:
            self.business_work_hours.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        business_work_hours = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.business_work_hours = business_work_hours
        return self


class UpdateBusinessLocation(TLFunction["bool"]):
    """The TL function account.updateBusinessLocation#9e6b131a, answered with Bool."""

    __slots__ = ("geo_point", "address",)

    ID = 0x9E6B131A
    QUALNAME = "functions.account.UpdateBusinessLocation"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        geo_point: base.InputGeoPoint | None = None,
        address: str | None = None,
    ) -> None:
        self.geo_point = geo_point
        self.address = address

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.geo_point is not None:
            flags |= 1 << 1
        if self.address is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.geo_point is not None:
            self.geo_point.write(w)
        if self.address is not None:
            w.write_string(self.address)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        geo_point = r.read_object() if flags & (1 << 1) else None
        address = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.geo_point = geo_point
        self.address = address
        return self


class UpdateBusinessGreetingMessage(TLFunction["bool"]):
    """The TL function account.updateBusinessGreetingMessage#66cdafc4, answered with Bool."""

    __slots__ = ("message",)

    ID = 0x66CDAFC4
    QUALNAME = "functions.account.UpdateBusinessGreetingMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        message: base.InputBusinessGreetingMessage | None = None,
    ) -> None:
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.message is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.message is not None:
            self.message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        message = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.message = message
        return self


class UpdateBusinessAwayMessage(TLFunction["bool"]):
    """The TL function account.updateBusinessAwayMessage#a26a7fa5, answered with Bool."""

    __slots__ = ("message",)

    ID = 0xA26A7FA5
    QUALNAME = "functions.account.UpdateBusinessAwayMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        message: base.InputBusinessAwayMessage | None = None,
    ) -> None:
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.message is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.message is not None:
            self.message.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        message = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.message = message
        return self


class UpdateConnectedBot(TLFunction["base.Updates"]):
    """The TL function account.updateConnectedBot#66a08c7e, answered with Updates."""

    __slots__ = ("deleted", "rights", "bot", "recipients",)

    ID = 0x66A08C7E
    QUALNAME = "functions.account.UpdateConnectedBot"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        deleted: bool = False,
        rights: base.BusinessBotRights | None = None,
        bot: base.InputUser,
        recipients: base.InputBusinessBotRecipients,
    ) -> None:
        self.deleted = deleted
        self.rights = rights
        self.bot = bot
        self.recipients = recipients

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.deleted:
            flags |= 1 << 1
        if self.rights is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.rights is not None:
            self.rights.write(w)
        self.bot.write(w)
        self.recipients.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        deleted = bool(flags & (1 << 1))
        rights = r.read_object() if flags & (1 << 0) else None
        bot = r.read_object()
        recipients = r.read_object()
        self = cls.__new__(cls)
        self.deleted = deleted
        self.rights = rights
        self.bot = bot
        self.recipients = recipients
        return self


class GetConnectedBots(TLFunction["base.account.ConnectedBots"]):
    """The TL function account.getConnectedBots#4ea4c80f, answered with account.ConnectedBots."""

    __slots__ = ()

    ID = 0x4EA4C80F
    QUALNAME = "functions.account.GetConnectedBots"
    RESULT = "account.ConnectedBots"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetBotBusinessConnection(TLFunction["base.Updates"]):
    """The TL function account.getBotBusinessConnection#76a86270, answered with Updates."""

    __slots__ = ("connection_id",)

    ID = 0x76A86270
    QUALNAME = "functions.account.GetBotBusinessConnection"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        connection_id: str,
    ) -> None:
        self.connection_id = connection_id

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.connection_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        connection_id = r.read_string()
        self = cls.__new__(cls)
        self.connection_id = connection_id
        return self


class UpdateBusinessIntro(TLFunction["bool"]):
    """The TL function account.updateBusinessIntro#a614d034, answered with Bool."""

    __slots__ = ("intro",)

    ID = 0xA614D034
    QUALNAME = "functions.account.UpdateBusinessIntro"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        intro: base.InputBusinessIntro | None = None,
    ) -> None:
        self.intro = intro

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.intro is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.intro is not None:
            self.intro.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        intro = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.intro = intro
        return self


class ToggleConnectedBotPaused(TLFunction["bool"]):
    """The TL function account.toggleConnectedBotPaused#646e1097, answered with Bool."""

    __slots__ = ("peer", "paused",)

    ID = 0x646E1097
    QUALNAME = "functions.account.ToggleConnectedBotPaused"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        paused: bool,
    ) -> None:
        self.peer = peer
        self.paused = paused

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_bool(self.paused)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        paused = r.read_bool()
        self = cls.__new__(cls)
        self.peer = peer
        self.paused = paused
        return self


class DisablePeerConnectedBot(TLFunction["bool"]):
    """The TL function account.disablePeerConnectedBot#5e437ed9, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0x5E437ED9
    QUALNAME = "functions.account.DisablePeerConnectedBot"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
    ) -> None:
        self.peer = peer

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        self = cls.__new__(cls)
        self.peer = peer
        return self


class UpdateBirthday(TLFunction["bool"]):
    """The TL function account.updateBirthday#cc6e0c11, answered with Bool."""

    __slots__ = ("birthday",)

    ID = 0xCC6E0C11
    QUALNAME = "functions.account.UpdateBirthday"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        birthday: base.Birthday | None = None,
    ) -> None:
        self.birthday = birthday

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.birthday is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.birthday is not None:
            self.birthday.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        birthday = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.birthday = birthday
        return self


class CreateBusinessChatLink(TLFunction["base.BusinessChatLink"]):
    """The TL function account.createBusinessChatLink#8851e68e, answered with BusinessChatLink."""

    __slots__ = ("link",)

    ID = 0x8851E68E
    QUALNAME = "functions.account.CreateBusinessChatLink"
    RESULT = "BusinessChatLink"

    def __init__(
        self,
        *,
        link: base.InputBusinessChatLink,
    ) -> None:
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        self.link.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        link = r.read_object()
        self = cls.__new__(cls)
        self.link = link
        return self


class EditBusinessChatLink(TLFunction["base.BusinessChatLink"]):
    """The TL function account.editBusinessChatLink#8c3410af, answered with BusinessChatLink."""

    __slots__ = ("slug", "link",)

    ID = 0x8C3410AF
    QUALNAME = "functions.account.EditBusinessChatLink"
    RESULT = "BusinessChatLink"

    def __init__(
        self,
        *,
        slug: str,
        link: base.InputBusinessChatLink,
    ) -> None:
        self.slug = slug
        self.link = link

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)
        self.link.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        link = r.read_object()
        self = cls.__new__(cls)
        self.slug = slug
        self.link = link
        return self


class DeleteBusinessChatLink(TLFunction["bool"]):
    """The TL function account.deleteBusinessChatLink#60073674, answered with Bool."""

    __slots__ = ("slug",)

    ID = 0x60073674
    QUALNAME = "functions.account.DeleteBusinessChatLink"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class GetBusinessChatLinks(TLFunction["base.account.BusinessChatLinks"]):
    """The TL function account.getBusinessChatLinks#6f70dde1, answered with account.BusinessChatLinks."""

    __slots__ = ()

    ID = 0x6F70DDE1
    QUALNAME = "functions.account.GetBusinessChatLinks"
    RESULT = "account.BusinessChatLinks"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ResolveBusinessChatLink(TLFunction["base.account.ResolvedBusinessChatLinks"]):
    """The TL function account.resolveBusinessChatLink#5492e5ee, answered with account.ResolvedBusinessChatLinks."""

    __slots__ = ("slug",)

    ID = 0x5492E5EE
    QUALNAME = "functions.account.ResolveBusinessChatLink"
    RESULT = "account.ResolvedBusinessChatLinks"

    def __init__(
        self,
        *,
        slug: str,
    ) -> None:
        self.slug = slug

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.slug)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        slug = r.read_string()
        self = cls.__new__(cls)
        self.slug = slug
        return self


class UpdatePersonalChannel(TLFunction["bool"]):
    """The TL function account.updatePersonalChannel#d94305e0, answered with Bool."""

    __slots__ = ("channel",)

    ID = 0xD94305E0
    QUALNAME = "functions.account.UpdatePersonalChannel"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        channel: base.InputChannel,
    ) -> None:
        self.channel = channel

    def write_body(self, w: TLWriter) -> None:
        self.channel.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        channel = r.read_object()
        self = cls.__new__(cls)
        self.channel = channel
        return self


class ToggleSponsoredMessages(TLFunction["bool"]):
    """The TL function account.toggleSponsoredMessages#b9d9a38d, answered with Bool."""

    __slots__ = ("enabled",)

    ID = 0xB9D9A38D
    QUALNAME = "functions.account.ToggleSponsoredMessages"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        enabled: bool,
    ) -> None:
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.enabled = enabled
        return self


class GetReactionsNotifySettings(TLFunction["base.ReactionsNotifySettings"]):
    """The TL function account.getReactionsNotifySettings#06dd654c, answered with ReactionsNotifySettings."""

    __slots__ = ()

    ID = 0x06DD654C
    QUALNAME = "functions.account.GetReactionsNotifySettings"
    RESULT = "ReactionsNotifySettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetReactionsNotifySettings(TLFunction["base.ReactionsNotifySettings"]):
    """The TL function account.setReactionsNotifySettings#316ce548, answered with ReactionsNotifySettings."""

    __slots__ = ("settings",)

    ID = 0x316CE548
    QUALNAME = "functions.account.SetReactionsNotifySettings"
    RESULT = "ReactionsNotifySettings"

    def __init__(
        self,
        *,
        settings: base.ReactionsNotifySettings,
    ) -> None:
        self.settings = settings

    def write_body(self, w: TLWriter) -> None:
        self.settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        settings = r.read_object()
        self = cls.__new__(cls)
        self.settings = settings
        return self


class GetCollectibleEmojiStatuses(TLFunction["base.account.EmojiStatuses"]):
    """The TL function account.getCollectibleEmojiStatuses#2e7b4543, answered with account.EmojiStatuses."""

    __slots__ = ("hash",)

    ID = 0x2E7B4543
    QUALNAME = "functions.account.GetCollectibleEmojiStatuses"
    RESULT = "account.EmojiStatuses"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetPaidMessagesRevenue(TLFunction["base.account.PaidMessagesRevenue"]):
    """The TL function account.getPaidMessagesRevenue#19ba4a67, answered with account.PaidMessagesRevenue."""

    __slots__ = ("parent_peer", "user_id",)

    ID = 0x19BA4A67
    QUALNAME = "functions.account.GetPaidMessagesRevenue"
    RESULT = "account.PaidMessagesRevenue"

    def __init__(
        self,
        *,
        parent_peer: base.InputPeer | None = None,
        user_id: base.InputUser,
    ) -> None:
        self.parent_peer = parent_peer
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.parent_peer is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        parent_peer = r.read_object() if flags & (1 << 0) else None
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.parent_peer = parent_peer
        self.user_id = user_id
        return self


class ToggleNoPaidMessagesException(TLFunction["bool"]):
    """The TL function account.toggleNoPaidMessagesException#fe2eda76, answered with Bool."""

    __slots__ = ("refund_charged", "require_payment", "parent_peer", "user_id",)

    ID = 0xFE2EDA76
    QUALNAME = "functions.account.ToggleNoPaidMessagesException"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        refund_charged: bool = False,
        require_payment: bool = False,
        parent_peer: base.InputPeer | None = None,
        user_id: base.InputUser,
    ) -> None:
        self.refund_charged = refund_charged
        self.require_payment = require_payment
        self.parent_peer = parent_peer
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.refund_charged:
            flags |= 1 << 0
        if self.require_payment:
            flags |= 1 << 2
        if self.parent_peer is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.parent_peer is not None:
            self.parent_peer.write(w)
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        refund_charged = bool(flags & (1 << 0))
        require_payment = bool(flags & (1 << 2))
        parent_peer = r.read_object() if flags & (1 << 1) else None
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.refund_charged = refund_charged
        self.require_payment = require_payment
        self.parent_peer = parent_peer
        self.user_id = user_id
        return self


class SetMainProfileTab(TLFunction["bool"]):
    """The TL function account.setMainProfileTab#5dee78b0, answered with Bool."""

    __slots__ = ("tab",)

    ID = 0x5DEE78B0
    QUALNAME = "functions.account.SetMainProfileTab"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        tab: base.ProfileTab,
    ) -> None:
        self.tab = tab

    def write_body(self, w: TLWriter) -> None:
        self.tab.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tab = r.read_object()
        self = cls.__new__(cls)
        self.tab = tab
        return self


class SaveMusic(TLFunction["bool"]):
    """The TL function account.saveMusic#b26732a9, answered with Bool."""

    __slots__ = ("unsave", "id", "after_id",)

    ID = 0xB26732A9
    QUALNAME = "functions.account.SaveMusic"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        unsave: bool = False,
        id: base.InputDocument,
        after_id: base.InputDocument | None = None,
    ) -> None:
        self.unsave = unsave
        self.id = id
        self.after_id = after_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.unsave:
            flags |= 1 << 0
        if self.after_id is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.id.write(w)
        if self.after_id is not None:
            self.after_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        unsave = bool(flags & (1 << 0))
        id = r.read_object()
        after_id = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.unsave = unsave
        self.id = id
        self.after_id = after_id
        return self


class GetSavedMusicIds(TLFunction["base.account.SavedMusicIds"]):
    """The TL function account.getSavedMusicIds#e09d5faf, answered with account.SavedMusicIds."""

    __slots__ = ("hash",)

    ID = 0xE09D5FAF
    QUALNAME = "functions.account.GetSavedMusicIds"
    RESULT = "account.SavedMusicIds"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetUniqueGiftChatThemes(TLFunction["base.account.ChatThemes"]):
    """The TL function account.getUniqueGiftChatThemes#e42ce9c9, answered with account.ChatThemes."""

    __slots__ = ("offset", "limit", "hash",)

    ID = 0xE42CE9C9
    QUALNAME = "functions.account.GetUniqueGiftChatThemes"
    RESULT = "account.ChatThemes"

    def __init__(
        self,
        *,
        offset: str,
        limit: int,
        hash: int,
    ) -> None:
        self.offset = offset
        self.limit = limit
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.offset)
        w.write_int(self.limit)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offset = r.read_string()
        limit = r.read_int()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.offset = offset
        self.limit = limit
        self.hash = hash
        return self


class InitPasskeyRegistration(TLFunction["base.account.PasskeyRegistrationOptions"]):
    """The TL function account.initPasskeyRegistration#429547e8, answered with account.PasskeyRegistrationOptions."""

    __slots__ = ()

    ID = 0x429547E8
    QUALNAME = "functions.account.InitPasskeyRegistration"
    RESULT = "account.PasskeyRegistrationOptions"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RegisterPasskey(TLFunction["base.Passkey"]):
    """The TL function account.registerPasskey#55b41fd6, answered with Passkey."""

    __slots__ = ("credential",)

    ID = 0x55B41FD6
    QUALNAME = "functions.account.RegisterPasskey"
    RESULT = "Passkey"

    def __init__(
        self,
        *,
        credential: base.InputPasskeyCredential,
    ) -> None:
        self.credential = credential

    def write_body(self, w: TLWriter) -> None:
        self.credential.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        credential = r.read_object()
        self = cls.__new__(cls)
        self.credential = credential
        return self


class GetPasskeys(TLFunction["base.account.Passkeys"]):
    """The TL function account.getPasskeys#ea1f0c52, answered with account.Passkeys."""

    __slots__ = ()

    ID = 0xEA1F0C52
    QUALNAME = "functions.account.GetPasskeys"
    RESULT = "account.Passkeys"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DeletePasskey(TLFunction["bool"]):
    """The TL function account.deletePasskey#f5b5563f, answered with Bool."""

    __slots__ = ("id",)

    ID = 0xF5B5563F
    QUALNAME = "functions.account.DeletePasskey"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: str,
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_string()
        self = cls.__new__(cls)
        self.id = id
        return self


class ConfirmBotConnection(TLFunction["bool"]):
    """The TL function account.confirmBotConnection#67ed1f68, answered with Bool."""

    __slots__ = ("bot_id",)

    ID = 0x67ED1F68
    QUALNAME = "functions.account.ConfirmBotConnection"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot_id: base.InputUser,
    ) -> None:
        self.bot_id = bot_id

    def write_body(self, w: TLWriter) -> None:
        self.bot_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot_id = r.read_object()
        self = cls.__new__(cls)
        self.bot_id = bot_id
        return self


class GetWebBrowserSettings(TLFunction["base.account.WebBrowserSettings"]):
    """The TL function account.getWebBrowserSettings#56655768, answered with account.WebBrowserSettings."""

    __slots__ = ("hash",)

    ID = 0x56655768
    QUALNAME = "functions.account.GetWebBrowserSettings"
    RESULT = "account.WebBrowserSettings"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class UpdateWebBrowserSettings(TLFunction["base.account.WebBrowserSettings"]):
    """The TL function account.updateWebBrowserSettings#9adf82fe, answered with account.WebBrowserSettings."""

    __slots__ = ("open_external_browser", "display_close_button",)

    ID = 0x9ADF82FE
    QUALNAME = "functions.account.UpdateWebBrowserSettings"
    RESULT = "account.WebBrowserSettings"

    def __init__(
        self,
        *,
        open_external_browser: bool = False,
        display_close_button: bool = False,
    ) -> None:
        self.open_external_browser = open_external_browser
        self.display_close_button = display_close_button

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.open_external_browser:
            flags |= 1 << 0
        if self.display_close_button:
            flags |= 1 << 1
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        open_external_browser = bool(flags & (1 << 0))
        display_close_button = bool(flags & (1 << 1))
        self = cls.__new__(cls)
        self.open_external_browser = open_external_browser
        self.display_close_button = display_close_button
        return self


class ToggleWebBrowserSettingsException(TLFunction["base.Updates"]):
    """The TL function account.toggleWebBrowserSettingsException#60ed4229, answered with Updates."""

    __slots__ = ("delete", "open_external_browser", "url",)

    ID = 0x60ED4229
    QUALNAME = "functions.account.ToggleWebBrowserSettingsException"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        delete: bool = False,
        open_external_browser: bool | None = None,
        url: str,
    ) -> None:
        self.delete = delete
        self.open_external_browser = open_external_browser
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.delete:
            flags |= 1 << 1
        if self.open_external_browser is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.open_external_browser is not None:
            w.write_bool(self.open_external_browser)
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        delete = bool(flags & (1 << 1))
        open_external_browser = r.read_bool() if flags & (1 << 0) else None
        url = r.read_string()
        self = cls.__new__(cls)
        self.delete = delete
        self.open_external_browser = open_external_browser
        self.url = url
        return self


class DeleteWebBrowserSettingsExceptions(TLFunction["base.account.WebBrowserSettings"]):
    """The TL function account.deleteWebBrowserSettingsExceptions#86a0765d, answered with account.WebBrowserSettings."""

    __slots__ = ()

    ID = 0x86A0765D
    QUALNAME = "functions.account.DeleteWebBrowserSettingsExceptions"
    RESULT = "account.WebBrowserSettings"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self
