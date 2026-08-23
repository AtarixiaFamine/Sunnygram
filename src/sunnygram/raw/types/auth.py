# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the auth namespace.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class SentCode(TLObject):
    """The TL type auth.sentCode#5e002502, a form of auth.SentCode."""

    __slots__ = ("type", "phone_code_hash", "next_type", "timeout",)

    ID = 0x5E002502
    QUALNAME = "types.auth.SentCode"

    def __init__(
        self,
        *,
        type: base.auth.SentCodeType,
        phone_code_hash: str,
        next_type: base.auth.CodeType | None = None,
        timeout: int | None = None,
    ) -> None:
        self.type = type
        self.phone_code_hash = phone_code_hash
        self.next_type = next_type
        self.timeout = timeout

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_type is not None:
            flags |= 1 << 1
        if self.timeout is not None:
            flags |= 1 << 2
        w.write_int(flags)
        self.type.write(w)
        w.write_string(self.phone_code_hash)
        if self.next_type is not None:
            self.next_type.write(w)
        if self.timeout is not None:
            w.write_int(self.timeout)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        type = r.read_object()
        phone_code_hash = r.read_string()
        next_type = r.read_object() if flags & (1 << 1) else None
        timeout = r.read_int() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.type = type
        self.phone_code_hash = phone_code_hash
        self.next_type = next_type
        self.timeout = timeout
        return self


class SentCodeSuccess(TLObject):
    """The TL type auth.sentCodeSuccess#2390fe44, a form of auth.SentCode."""

    __slots__ = ("authorization",)

    ID = 0x2390FE44
    QUALNAME = "types.auth.SentCodeSuccess"

    def __init__(
        self,
        *,
        authorization: base.auth.Authorization,
    ) -> None:
        self.authorization = authorization

    def write_body(self, w: TLWriter) -> None:
        self.authorization.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        authorization = r.read_object()
        self = cls.__new__(cls)
        self.authorization = authorization
        return self


class SentCodePaymentRequired(TLObject):
    """The TL type auth.sentCodePaymentRequired#f8827ebf, a form of auth.SentCode."""

    __slots__ = ("store_product", "phone_code_hash", "support_email_address", "support_email_subject", "premium_days", "currency", "amount",)

    ID = 0xF8827EBF
    QUALNAME = "types.auth.SentCodePaymentRequired"

    def __init__(
        self,
        *,
        store_product: str,
        phone_code_hash: str,
        support_email_address: str,
        support_email_subject: str,
        premium_days: int,
        currency: str,
        amount: int,
    ) -> None:
        self.store_product = store_product
        self.phone_code_hash = phone_code_hash
        self.support_email_address = support_email_address
        self.support_email_subject = support_email_subject
        self.premium_days = premium_days
        self.currency = currency
        self.amount = amount

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.store_product)
        w.write_string(self.phone_code_hash)
        w.write_string(self.support_email_address)
        w.write_string(self.support_email_subject)
        w.write_int(self.premium_days)
        w.write_string(self.currency)
        w.write_long(self.amount)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        store_product = r.read_string()
        phone_code_hash = r.read_string()
        support_email_address = r.read_string()
        support_email_subject = r.read_string()
        premium_days = r.read_int()
        currency = r.read_string()
        amount = r.read_long()
        self = cls.__new__(cls)
        self.store_product = store_product
        self.phone_code_hash = phone_code_hash
        self.support_email_address = support_email_address
        self.support_email_subject = support_email_subject
        self.premium_days = premium_days
        self.currency = currency
        self.amount = amount
        return self


class Authorization(TLObject):
    """The TL type auth.authorization#2ea2c0d4, a form of auth.Authorization."""

    __slots__ = ("setup_password_required", "otherwise_relogin_days", "tmp_sessions", "future_auth_token", "user",)

    ID = 0x2EA2C0D4
    QUALNAME = "types.auth.Authorization"

    def __init__(
        self,
        *,
        setup_password_required: bool = False,
        otherwise_relogin_days: int | None = None,
        tmp_sessions: int | None = None,
        future_auth_token: bytes | None = None,
        user: base.User,
    ) -> None:
        self.setup_password_required = setup_password_required
        self.otherwise_relogin_days = otherwise_relogin_days
        self.tmp_sessions = tmp_sessions
        self.future_auth_token = future_auth_token
        self.user = user

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.setup_password_required:
            flags |= 1 << 1
        if self.otherwise_relogin_days is not None:
            flags |= 1 << 1
        if self.tmp_sessions is not None:
            flags |= 1 << 0
        if self.future_auth_token is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.otherwise_relogin_days is not None:
            w.write_int(self.otherwise_relogin_days)
        if self.tmp_sessions is not None:
            w.write_int(self.tmp_sessions)
        if self.future_auth_token is not None:
            w.write_bytes(self.future_auth_token)
        self.user.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        setup_password_required = bool(flags & (1 << 1))
        otherwise_relogin_days = r.read_int() if flags & (1 << 1) else None
        tmp_sessions = r.read_int() if flags & (1 << 0) else None
        future_auth_token = r.read_bytes() if flags & (1 << 2) else None
        user = r.read_object()
        self = cls.__new__(cls)
        self.setup_password_required = setup_password_required
        self.otherwise_relogin_days = otherwise_relogin_days
        self.tmp_sessions = tmp_sessions
        self.future_auth_token = future_auth_token
        self.user = user
        return self


class AuthorizationSignUpRequired(TLObject):
    """The TL type auth.authorizationSignUpRequired#44747e9a, a form of auth.Authorization."""

    __slots__ = ("terms_of_service",)

    ID = 0x44747E9A
    QUALNAME = "types.auth.AuthorizationSignUpRequired"

    def __init__(
        self,
        *,
        terms_of_service: base.help.TermsOfService | None = None,
    ) -> None:
        self.terms_of_service = terms_of_service

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.terms_of_service is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.terms_of_service is not None:
            self.terms_of_service.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        terms_of_service = r.read_object() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.terms_of_service = terms_of_service
        return self


class ExportedAuthorization(TLObject):
    """The TL type auth.exportedAuthorization#b434e2b8, a form of auth.ExportedAuthorization."""

    __slots__ = ("id", "bytes",)

    ID = 0xB434E2B8
    QUALNAME = "types.auth.ExportedAuthorization"

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


class PasswordRecovery(TLObject):
    """The TL type auth.passwordRecovery#137948a5, a form of auth.PasswordRecovery."""

    __slots__ = ("email_pattern",)

    ID = 0x137948A5
    QUALNAME = "types.auth.PasswordRecovery"

    def __init__(
        self,
        *,
        email_pattern: str,
    ) -> None:
        self.email_pattern = email_pattern

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.email_pattern)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        email_pattern = r.read_string()
        self = cls.__new__(cls)
        self.email_pattern = email_pattern
        return self


class CodeTypeSms(TLObject):
    """The TL type auth.codeTypeSms#72a3158c, a form of auth.CodeType."""

    __slots__ = ()

    ID = 0x72A3158C
    QUALNAME = "types.auth.CodeTypeSms"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CodeTypeCall(TLObject):
    """The TL type auth.codeTypeCall#741cd3e3, a form of auth.CodeType."""

    __slots__ = ()

    ID = 0x741CD3E3
    QUALNAME = "types.auth.CodeTypeCall"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CodeTypeFlashCall(TLObject):
    """The TL type auth.codeTypeFlashCall#226ccefb, a form of auth.CodeType."""

    __slots__ = ()

    ID = 0x226CCEFB
    QUALNAME = "types.auth.CodeTypeFlashCall"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CodeTypeMissedCall(TLObject):
    """The TL type auth.codeTypeMissedCall#d61ad6ee, a form of auth.CodeType."""

    __slots__ = ()

    ID = 0xD61AD6EE
    QUALNAME = "types.auth.CodeTypeMissedCall"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CodeTypeFragmentSms(TLObject):
    """The TL type auth.codeTypeFragmentSms#06ed998c, a form of auth.CodeType."""

    __slots__ = ()

    ID = 0x06ED998C
    QUALNAME = "types.auth.CodeTypeFragmentSms"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SentCodeTypeApp(TLObject):
    """The TL type auth.sentCodeTypeApp#3dbb5986, a form of auth.SentCodeType."""

    __slots__ = ("length",)

    ID = 0x3DBB5986
    QUALNAME = "types.auth.SentCodeTypeApp"

    def __init__(
        self,
        *,
        length: int,
    ) -> None:
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        length = r.read_int()
        self = cls.__new__(cls)
        self.length = length
        return self


class SentCodeTypeSms(TLObject):
    """The TL type auth.sentCodeTypeSms#c000bba2, a form of auth.SentCodeType."""

    __slots__ = ("length",)

    ID = 0xC000BBA2
    QUALNAME = "types.auth.SentCodeTypeSms"

    def __init__(
        self,
        *,
        length: int,
    ) -> None:
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        length = r.read_int()
        self = cls.__new__(cls)
        self.length = length
        return self


class SentCodeTypeCall(TLObject):
    """The TL type auth.sentCodeTypeCall#5353e5a7, a form of auth.SentCodeType."""

    __slots__ = ("length",)

    ID = 0x5353E5A7
    QUALNAME = "types.auth.SentCodeTypeCall"

    def __init__(
        self,
        *,
        length: int,
    ) -> None:
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        length = r.read_int()
        self = cls.__new__(cls)
        self.length = length
        return self


class SentCodeTypeFlashCall(TLObject):
    """The TL type auth.sentCodeTypeFlashCall#ab03c6d9, a form of auth.SentCodeType."""

    __slots__ = ("pattern",)

    ID = 0xAB03C6D9
    QUALNAME = "types.auth.SentCodeTypeFlashCall"

    def __init__(
        self,
        *,
        pattern: str,
    ) -> None:
        self.pattern = pattern

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.pattern)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pattern = r.read_string()
        self = cls.__new__(cls)
        self.pattern = pattern
        return self


class SentCodeTypeMissedCall(TLObject):
    """The TL type auth.sentCodeTypeMissedCall#82006484, a form of auth.SentCodeType."""

    __slots__ = ("prefix", "length",)

    ID = 0x82006484
    QUALNAME = "types.auth.SentCodeTypeMissedCall"

    def __init__(
        self,
        *,
        prefix: str,
        length: int,
    ) -> None:
        self.prefix = prefix
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.prefix)
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        prefix = r.read_string()
        length = r.read_int()
        self = cls.__new__(cls)
        self.prefix = prefix
        self.length = length
        return self


class SentCodeTypeEmailCode(TLObject):
    """The TL type auth.sentCodeTypeEmailCode#f450f59b, a form of auth.SentCodeType."""

    __slots__ = ("apple_signin_allowed", "google_signin_allowed", "email_pattern", "length", "reset_available_period", "reset_pending_date",)

    ID = 0xF450F59B
    QUALNAME = "types.auth.SentCodeTypeEmailCode"

    def __init__(
        self,
        *,
        apple_signin_allowed: bool = False,
        google_signin_allowed: bool = False,
        email_pattern: str,
        length: int,
        reset_available_period: int | None = None,
        reset_pending_date: int | None = None,
    ) -> None:
        self.apple_signin_allowed = apple_signin_allowed
        self.google_signin_allowed = google_signin_allowed
        self.email_pattern = email_pattern
        self.length = length
        self.reset_available_period = reset_available_period
        self.reset_pending_date = reset_pending_date

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.apple_signin_allowed:
            flags |= 1 << 0
        if self.google_signin_allowed:
            flags |= 1 << 1
        if self.reset_available_period is not None:
            flags |= 1 << 3
        if self.reset_pending_date is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_string(self.email_pattern)
        w.write_int(self.length)
        if self.reset_available_period is not None:
            w.write_int(self.reset_available_period)
        if self.reset_pending_date is not None:
            w.write_int(self.reset_pending_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        apple_signin_allowed = bool(flags & (1 << 0))
        google_signin_allowed = bool(flags & (1 << 1))
        email_pattern = r.read_string()
        length = r.read_int()
        reset_available_period = r.read_int() if flags & (1 << 3) else None
        reset_pending_date = r.read_int() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.apple_signin_allowed = apple_signin_allowed
        self.google_signin_allowed = google_signin_allowed
        self.email_pattern = email_pattern
        self.length = length
        self.reset_available_period = reset_available_period
        self.reset_pending_date = reset_pending_date
        return self


class SentCodeTypeSetUpEmailRequired(TLObject):
    """The TL type auth.sentCodeTypeSetUpEmailRequired#a5491dea, a form of auth.SentCodeType."""

    __slots__ = ("apple_signin_allowed", "google_signin_allowed",)

    ID = 0xA5491DEA
    QUALNAME = "types.auth.SentCodeTypeSetUpEmailRequired"

    def __init__(
        self,
        *,
        apple_signin_allowed: bool = False,
        google_signin_allowed: bool = False,
    ) -> None:
        self.apple_signin_allowed = apple_signin_allowed
        self.google_signin_allowed = google_signin_allowed

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.apple_signin_allowed:
            flags |= 1 << 0
        if self.google_signin_allowed:
            flags |= 1 << 1
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        apple_signin_allowed = bool(flags & (1 << 0))
        google_signin_allowed = bool(flags & (1 << 1))
        self = cls.__new__(cls)
        self.apple_signin_allowed = apple_signin_allowed
        self.google_signin_allowed = google_signin_allowed
        return self


class SentCodeTypeFragmentSms(TLObject):
    """The TL type auth.sentCodeTypeFragmentSms#d9565c39, a form of auth.SentCodeType."""

    __slots__ = ("url", "length",)

    ID = 0xD9565C39
    QUALNAME = "types.auth.SentCodeTypeFragmentSms"

    def __init__(
        self,
        *,
        url: str,
        length: int,
    ) -> None:
        self.url = url
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.url)
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        url = r.read_string()
        length = r.read_int()
        self = cls.__new__(cls)
        self.url = url
        self.length = length
        return self


class SentCodeTypeFirebaseSms(TLObject):
    """The TL type auth.sentCodeTypeFirebaseSms#009fd736, a form of auth.SentCodeType."""

    __slots__ = ("nonce", "play_integrity_project_id", "play_integrity_nonce", "receipt", "push_timeout", "length",)

    ID = 0x009FD736
    QUALNAME = "types.auth.SentCodeTypeFirebaseSms"

    def __init__(
        self,
        *,
        nonce: bytes | None = None,
        play_integrity_project_id: int | None = None,
        play_integrity_nonce: bytes | None = None,
        receipt: str | None = None,
        push_timeout: int | None = None,
        length: int,
    ) -> None:
        self.nonce = nonce
        self.play_integrity_project_id = play_integrity_project_id
        self.play_integrity_nonce = play_integrity_nonce
        self.receipt = receipt
        self.push_timeout = push_timeout
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.nonce is not None:
            flags |= 1 << 0
        if self.play_integrity_project_id is not None:
            flags |= 1 << 2
        if self.play_integrity_nonce is not None:
            flags |= 1 << 2
        if self.receipt is not None:
            flags |= 1 << 1
        if self.push_timeout is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.nonce is not None:
            w.write_bytes(self.nonce)
        if self.play_integrity_project_id is not None:
            w.write_long(self.play_integrity_project_id)
        if self.play_integrity_nonce is not None:
            w.write_bytes(self.play_integrity_nonce)
        if self.receipt is not None:
            w.write_string(self.receipt)
        if self.push_timeout is not None:
            w.write_int(self.push_timeout)
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        nonce = r.read_bytes() if flags & (1 << 0) else None
        play_integrity_project_id = r.read_long() if flags & (1 << 2) else None
        play_integrity_nonce = r.read_bytes() if flags & (1 << 2) else None
        receipt = r.read_string() if flags & (1 << 1) else None
        push_timeout = r.read_int() if flags & (1 << 1) else None
        length = r.read_int()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.play_integrity_project_id = play_integrity_project_id
        self.play_integrity_nonce = play_integrity_nonce
        self.receipt = receipt
        self.push_timeout = push_timeout
        self.length = length
        return self


class SentCodeTypeSmsWord(TLObject):
    """The TL type auth.sentCodeTypeSmsWord#a416ac81, a form of auth.SentCodeType."""

    __slots__ = ("beginning",)

    ID = 0xA416AC81
    QUALNAME = "types.auth.SentCodeTypeSmsWord"

    def __init__(
        self,
        *,
        beginning: str | None = None,
    ) -> None:
        self.beginning = beginning

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.beginning is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.beginning is not None:
            w.write_string(self.beginning)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        beginning = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.beginning = beginning
        return self


class SentCodeTypeSmsPhrase(TLObject):
    """The TL type auth.sentCodeTypeSmsPhrase#b37794af, a form of auth.SentCodeType."""

    __slots__ = ("beginning",)

    ID = 0xB37794AF
    QUALNAME = "types.auth.SentCodeTypeSmsPhrase"

    def __init__(
        self,
        *,
        beginning: str | None = None,
    ) -> None:
        self.beginning = beginning

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.beginning is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.beginning is not None:
            w.write_string(self.beginning)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        beginning = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.beginning = beginning
        return self


class LoginToken(TLObject):
    """The TL type auth.loginToken#629f1980, a form of auth.LoginToken."""

    __slots__ = ("expires", "token",)

    ID = 0x629F1980
    QUALNAME = "types.auth.LoginToken"

    def __init__(
        self,
        *,
        expires: int,
        token: bytes,
    ) -> None:
        self.expires = expires
        self.token = token

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.expires)
        w.write_bytes(self.token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        expires = r.read_int()
        token = r.read_bytes()
        self = cls.__new__(cls)
        self.expires = expires
        self.token = token
        return self


class LoginTokenMigrateTo(TLObject):
    """The TL type auth.loginTokenMigrateTo#068e9916, a form of auth.LoginToken."""

    __slots__ = ("dc_id", "token",)

    ID = 0x068E9916
    QUALNAME = "types.auth.LoginTokenMigrateTo"

    def __init__(
        self,
        *,
        dc_id: int,
        token: bytes,
    ) -> None:
        self.dc_id = dc_id
        self.token = token

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.dc_id)
        w.write_bytes(self.token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        dc_id = r.read_int()
        token = r.read_bytes()
        self = cls.__new__(cls)
        self.dc_id = dc_id
        self.token = token
        return self


class LoginTokenSuccess(TLObject):
    """The TL type auth.loginTokenSuccess#390d5c5e, a form of auth.LoginToken."""

    __slots__ = ("authorization",)

    ID = 0x390D5C5E
    QUALNAME = "types.auth.LoginTokenSuccess"

    def __init__(
        self,
        *,
        authorization: base.auth.Authorization,
    ) -> None:
        self.authorization = authorization

    def write_body(self, w: TLWriter) -> None:
        self.authorization.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        authorization = r.read_object()
        self = cls.__new__(cls)
        self.authorization = authorization
        return self


class LoggedOut(TLObject):
    """The TL type auth.loggedOut#c3a2835f, a form of auth.LoggedOut."""

    __slots__ = ("future_auth_token",)

    ID = 0xC3A2835F
    QUALNAME = "types.auth.LoggedOut"

    def __init__(
        self,
        *,
        future_auth_token: bytes | None = None,
    ) -> None:
        self.future_auth_token = future_auth_token

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.future_auth_token is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.future_auth_token is not None:
            w.write_bytes(self.future_auth_token)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        future_auth_token = r.read_bytes() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.future_auth_token = future_auth_token
        return self


class PasskeyLoginOptions(TLObject):
    """The TL type auth.passkeyLoginOptions#e2037789, a form of auth.PasskeyLoginOptions."""

    __slots__ = ("options",)

    ID = 0xE2037789
    QUALNAME = "types.auth.PasskeyLoginOptions"

    def __init__(
        self,
        *,
        options: base.DataJSON,
    ) -> None:
        self.options = options

    def write_body(self, w: TLWriter) -> None:
        self.options.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        options = r.read_object()
        self = cls.__new__(cls)
        self.options = options
        return self
