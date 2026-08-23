# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the account namespace.

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


class PrivacyRules(TLObject):
    """The TL type account.privacyRules#50a04e45, a form of account.PrivacyRules."""

    __slots__ = ("rules", "chats", "users",)

    ID = 0x50A04E45
    QUALNAME = "types.account.PrivacyRules"

    def __init__(
        self,
        *,
        rules: list[base.PrivacyRule],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.rules = rules
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.rules)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        rules = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.rules = rules
        self.chats = chats
        self.users = users
        return self


class Authorizations(TLObject):
    """The TL type account.authorizations#4bff8ea0, a form of account.Authorizations."""

    __slots__ = ("authorization_ttl_days", "authorizations",)

    ID = 0x4BFF8EA0
    QUALNAME = "types.account.Authorizations"

    def __init__(
        self,
        *,
        authorization_ttl_days: int,
        authorizations: list[base.Authorization],
    ) -> None:
        self.authorization_ttl_days = authorization_ttl_days
        self.authorizations = authorizations

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.authorization_ttl_days)
        w.write_vector(self.authorizations)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        authorization_ttl_days = r.read_int()
        authorizations = r.read_vector()
        self = cls.__new__(cls)
        self.authorization_ttl_days = authorization_ttl_days
        self.authorizations = authorizations
        return self


class Password(TLObject):
    """The TL type account.password#957b50fb, a form of account.Password."""

    __slots__ = ("has_recovery", "has_secure_values", "has_password", "current_algo", "srp_B", "srp_id", "hint", "email_unconfirmed_pattern", "new_algo", "new_secure_algo", "secure_random", "pending_reset_date", "login_email_pattern",)

    ID = 0x957B50FB
    QUALNAME = "types.account.Password"

    def __init__(
        self,
        *,
        has_recovery: bool = False,
        has_secure_values: bool = False,
        has_password: bool = False,
        current_algo: base.PasswordKdfAlgo | None = None,
        srp_B: bytes | None = None,
        srp_id: int | None = None,
        hint: str | None = None,
        email_unconfirmed_pattern: str | None = None,
        new_algo: base.PasswordKdfAlgo,
        new_secure_algo: base.SecurePasswordKdfAlgo,
        secure_random: bytes,
        pending_reset_date: int | None = None,
        login_email_pattern: str | None = None,
    ) -> None:
        self.has_recovery = has_recovery
        self.has_secure_values = has_secure_values
        self.has_password = has_password
        self.current_algo = current_algo
        self.srp_B = srp_B
        self.srp_id = srp_id
        self.hint = hint
        self.email_unconfirmed_pattern = email_unconfirmed_pattern
        self.new_algo = new_algo
        self.new_secure_algo = new_secure_algo
        self.secure_random = secure_random
        self.pending_reset_date = pending_reset_date
        self.login_email_pattern = login_email_pattern

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.has_recovery:
            flags |= 1 << 0
        if self.has_secure_values:
            flags |= 1 << 1
        if self.has_password:
            flags |= 1 << 2
        if self.current_algo is not None:
            flags |= 1 << 2
        if self.srp_B is not None:
            flags |= 1 << 2
        if self.srp_id is not None:
            flags |= 1 << 2
        if self.hint is not None:
            flags |= 1 << 3
        if self.email_unconfirmed_pattern is not None:
            flags |= 1 << 4
        if self.pending_reset_date is not None:
            flags |= 1 << 5
        if self.login_email_pattern is not None:
            flags |= 1 << 6
        w.write_int(flags)
        if self.current_algo is not None:
            self.current_algo.write(w)
        if self.srp_B is not None:
            w.write_bytes(self.srp_B)
        if self.srp_id is not None:
            w.write_long(self.srp_id)
        if self.hint is not None:
            w.write_string(self.hint)
        if self.email_unconfirmed_pattern is not None:
            w.write_string(self.email_unconfirmed_pattern)
        self.new_algo.write(w)
        self.new_secure_algo.write(w)
        w.write_bytes(self.secure_random)
        if self.pending_reset_date is not None:
            w.write_int(self.pending_reset_date)
        if self.login_email_pattern is not None:
            w.write_string(self.login_email_pattern)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        has_recovery = bool(flags & (1 << 0))
        has_secure_values = bool(flags & (1 << 1))
        has_password = bool(flags & (1 << 2))
        current_algo = r.read_object() if flags & (1 << 2) else None
        srp_B = r.read_bytes() if flags & (1 << 2) else None
        srp_id = r.read_long() if flags & (1 << 2) else None
        hint = r.read_string() if flags & (1 << 3) else None
        email_unconfirmed_pattern = r.read_string() if flags & (1 << 4) else None
        new_algo = r.read_object()
        new_secure_algo = r.read_object()
        secure_random = r.read_bytes()
        pending_reset_date = r.read_int() if flags & (1 << 5) else None
        login_email_pattern = r.read_string() if flags & (1 << 6) else None
        self = cls.__new__(cls)
        self.has_recovery = has_recovery
        self.has_secure_values = has_secure_values
        self.has_password = has_password
        self.current_algo = current_algo
        self.srp_B = srp_B
        self.srp_id = srp_id
        self.hint = hint
        self.email_unconfirmed_pattern = email_unconfirmed_pattern
        self.new_algo = new_algo
        self.new_secure_algo = new_secure_algo
        self.secure_random = secure_random
        self.pending_reset_date = pending_reset_date
        self.login_email_pattern = login_email_pattern
        return self


class PasswordSettings(TLObject):
    """The TL type account.passwordSettings#9a5c33e5, a form of account.PasswordSettings."""

    __slots__ = ("email", "secure_settings",)

    ID = 0x9A5C33E5
    QUALNAME = "types.account.PasswordSettings"

    def __init__(
        self,
        *,
        email: str | None = None,
        secure_settings: base.SecureSecretSettings | None = None,
    ) -> None:
        self.email = email
        self.secure_settings = secure_settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.email is not None:
            flags |= 1 << 0
        if self.secure_settings is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.email is not None:
            w.write_string(self.email)
        if self.secure_settings is not None:
            self.secure_settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        email = r.read_string() if flags & (1 << 0) else None
        secure_settings = r.read_object() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.email = email
        self.secure_settings = secure_settings
        return self


class PasswordInputSettings(TLObject):
    """The TL type account.passwordInputSettings#c23727c9, a form of account.PasswordInputSettings."""

    __slots__ = ("new_algo", "new_password_hash", "hint", "email", "new_secure_settings",)

    ID = 0xC23727C9
    QUALNAME = "types.account.PasswordInputSettings"

    def __init__(
        self,
        *,
        new_algo: base.PasswordKdfAlgo | None = None,
        new_password_hash: bytes | None = None,
        hint: str | None = None,
        email: str | None = None,
        new_secure_settings: base.SecureSecretSettings | None = None,
    ) -> None:
        self.new_algo = new_algo
        self.new_password_hash = new_password_hash
        self.hint = hint
        self.email = email
        self.new_secure_settings = new_secure_settings

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.new_algo is not None:
            flags |= 1 << 0
        if self.new_password_hash is not None:
            flags |= 1 << 0
        if self.hint is not None:
            flags |= 1 << 0
        if self.email is not None:
            flags |= 1 << 1
        if self.new_secure_settings is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.new_algo is not None:
            self.new_algo.write(w)
        if self.new_password_hash is not None:
            w.write_bytes(self.new_password_hash)
        if self.hint is not None:
            w.write_string(self.hint)
        if self.email is not None:
            w.write_string(self.email)
        if self.new_secure_settings is not None:
            self.new_secure_settings.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        new_algo = r.read_object() if flags & (1 << 0) else None
        new_password_hash = r.read_bytes() if flags & (1 << 0) else None
        hint = r.read_string() if flags & (1 << 0) else None
        email = r.read_string() if flags & (1 << 1) else None
        new_secure_settings = r.read_object() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.new_algo = new_algo
        self.new_password_hash = new_password_hash
        self.hint = hint
        self.email = email
        self.new_secure_settings = new_secure_settings
        return self


class TmpPassword(TLObject):
    """The TL type account.tmpPassword#db64fd34, a form of account.TmpPassword."""

    __slots__ = ("tmp_password", "valid_until",)

    ID = 0xDB64FD34
    QUALNAME = "types.account.TmpPassword"

    def __init__(
        self,
        *,
        tmp_password: bytes,
        valid_until: int,
    ) -> None:
        self.tmp_password = tmp_password
        self.valid_until = valid_until

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.tmp_password)
        w.write_int(self.valid_until)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        tmp_password = r.read_bytes()
        valid_until = r.read_int()
        self = cls.__new__(cls)
        self.tmp_password = tmp_password
        self.valid_until = valid_until
        return self


class WebAuthorizations(TLObject):
    """The TL type account.webAuthorizations#ed56c9fc, a form of account.WebAuthorizations."""

    __slots__ = ("authorizations", "users",)

    ID = 0xED56C9FC
    QUALNAME = "types.account.WebAuthorizations"

    def __init__(
        self,
        *,
        authorizations: list[base.WebAuthorization],
        users: list[base.User],
    ) -> None:
        self.authorizations = authorizations
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.authorizations)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        authorizations = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.authorizations = authorizations
        self.users = users
        return self


class AuthorizationForm(TLObject):
    """The TL type account.authorizationForm#ad2e1cd8, a form of account.AuthorizationForm."""

    __slots__ = ("required_types", "values", "errors", "users", "privacy_policy_url",)

    ID = 0xAD2E1CD8
    QUALNAME = "types.account.AuthorizationForm"

    def __init__(
        self,
        *,
        required_types: list[base.SecureRequiredType],
        values: list[base.SecureValue],
        errors: list[base.SecureValueError],
        users: list[base.User],
        privacy_policy_url: str | None = None,
    ) -> None:
        self.required_types = required_types
        self.values = values
        self.errors = errors
        self.users = users
        self.privacy_policy_url = privacy_policy_url

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.privacy_policy_url is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_vector(self.required_types)
        w.write_vector(self.values)
        w.write_vector(self.errors)
        w.write_vector(self.users)
        if self.privacy_policy_url is not None:
            w.write_string(self.privacy_policy_url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        required_types = r.read_vector()
        values = r.read_vector()
        errors = r.read_vector()
        users = r.read_vector()
        privacy_policy_url = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.required_types = required_types
        self.values = values
        self.errors = errors
        self.users = users
        self.privacy_policy_url = privacy_policy_url
        return self


class SentEmailCode(TLObject):
    """The TL type account.sentEmailCode#811f854f, a form of account.SentEmailCode."""

    __slots__ = ("email_pattern", "length",)

    ID = 0x811F854F
    QUALNAME = "types.account.SentEmailCode"

    def __init__(
        self,
        *,
        email_pattern: str,
        length: int,
    ) -> None:
        self.email_pattern = email_pattern
        self.length = length

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.email_pattern)
        w.write_int(self.length)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        email_pattern = r.read_string()
        length = r.read_int()
        self = cls.__new__(cls)
        self.email_pattern = email_pattern
        self.length = length
        return self


class Takeout(TLObject):
    """The TL type account.takeout#4dba4501, a form of account.Takeout."""

    __slots__ = ("id",)

    ID = 0x4DBA4501
    QUALNAME = "types.account.Takeout"

    def __init__(
        self,
        *,
        id: int,
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_long()
        self = cls.__new__(cls)
        self.id = id
        return self


class WallPapersNotModified(TLObject):
    """The TL type account.wallPapersNotModified#1c199183, a form of account.WallPapers."""

    __slots__ = ()

    ID = 0x1C199183
    QUALNAME = "types.account.WallPapersNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class WallPapers(TLObject):
    """The TL type account.wallPapers#cdc3858c, a form of account.WallPapers."""

    __slots__ = ("hash", "wallpapers",)

    ID = 0xCDC3858C
    QUALNAME = "types.account.WallPapers"

    def __init__(
        self,
        *,
        hash: int,
        wallpapers: list[base.WallPaper],
    ) -> None:
        self.hash = hash
        self.wallpapers = wallpapers

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.wallpapers)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        wallpapers = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.wallpapers = wallpapers
        return self


class AutoDownloadSettings(TLObject):
    """The TL type account.autoDownloadSettings#63cacf26, a form of account.AutoDownloadSettings."""

    __slots__ = ("low", "medium", "high",)

    ID = 0x63CACF26
    QUALNAME = "types.account.AutoDownloadSettings"

    def __init__(
        self,
        *,
        low: base.AutoDownloadSettings,
        medium: base.AutoDownloadSettings,
        high: base.AutoDownloadSettings,
    ) -> None:
        self.low = low
        self.medium = medium
        self.high = high

    def write_body(self, w: TLWriter) -> None:
        self.low.write(w)
        self.medium.write(w)
        self.high.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        low = r.read_object()
        medium = r.read_object()
        high = r.read_object()
        self = cls.__new__(cls)
        self.low = low
        self.medium = medium
        self.high = high
        return self


class ThemesNotModified(TLObject):
    """The TL type account.themesNotModified#f41eb622, a form of account.Themes."""

    __slots__ = ()

    ID = 0xF41EB622
    QUALNAME = "types.account.ThemesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class Themes(TLObject):
    """The TL type account.themes#9a3d8c6d, a form of account.Themes."""

    __slots__ = ("hash", "themes",)

    ID = 0x9A3D8C6D
    QUALNAME = "types.account.Themes"

    def __init__(
        self,
        *,
        hash: int,
        themes: list[base.Theme],
    ) -> None:
        self.hash = hash
        self.themes = themes

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.themes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        themes = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.themes = themes
        return self


class ContentSettings(TLObject):
    """The TL type account.contentSettings#57e28221, a form of account.ContentSettings."""

    __slots__ = ("sensitive_enabled", "sensitive_can_change",)

    ID = 0x57E28221
    QUALNAME = "types.account.ContentSettings"

    def __init__(
        self,
        *,
        sensitive_enabled: bool = False,
        sensitive_can_change: bool = False,
    ) -> None:
        self.sensitive_enabled = sensitive_enabled
        self.sensitive_can_change = sensitive_can_change

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.sensitive_enabled:
            flags |= 1 << 0
        if self.sensitive_can_change:
            flags |= 1 << 1
        w.write_int(flags)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        sensitive_enabled = bool(flags & (1 << 0))
        sensitive_can_change = bool(flags & (1 << 1))
        self = cls.__new__(cls)
        self.sensitive_enabled = sensitive_enabled
        self.sensitive_can_change = sensitive_can_change
        return self


class ResetPasswordFailedWait(TLObject):
    """The TL type account.resetPasswordFailedWait#e3779861, a form of account.ResetPasswordResult."""

    __slots__ = ("retry_date",)

    ID = 0xE3779861
    QUALNAME = "types.account.ResetPasswordFailedWait"

    def __init__(
        self,
        *,
        retry_date: int,
    ) -> None:
        self.retry_date = retry_date

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.retry_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        retry_date = r.read_int()
        self = cls.__new__(cls)
        self.retry_date = retry_date
        return self


class ResetPasswordRequestedWait(TLObject):
    """The TL type account.resetPasswordRequestedWait#e9effc7d, a form of account.ResetPasswordResult."""

    __slots__ = ("until_date",)

    ID = 0xE9EFFC7D
    QUALNAME = "types.account.ResetPasswordRequestedWait"

    def __init__(
        self,
        *,
        until_date: int,
    ) -> None:
        self.until_date = until_date

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.until_date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        until_date = r.read_int()
        self = cls.__new__(cls)
        self.until_date = until_date
        return self


class ResetPasswordOk(TLObject):
    """The TL type account.resetPasswordOk#e926d63e, a form of account.ResetPasswordResult."""

    __slots__ = ()

    ID = 0xE926D63E
    QUALNAME = "types.account.ResetPasswordOk"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ChatThemesNotModified(TLObject):
    """The TL type account.chatThemesNotModified#e011e1c4, a form of account.ChatThemes."""

    __slots__ = ()

    ID = 0xE011E1C4
    QUALNAME = "types.account.ChatThemesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class ChatThemes(TLObject):
    """The TL type account.chatThemes#be098173, a form of account.ChatThemes."""

    __slots__ = ("hash", "themes", "chats", "users", "next_offset",)

    ID = 0xBE098173
    QUALNAME = "types.account.ChatThemes"

    def __init__(
        self,
        *,
        hash: int,
        themes: list[base.ChatTheme],
        chats: list[base.Chat],
        users: list[base.User],
        next_offset: str | None = None,
    ) -> None:
        self.hash = hash
        self.themes = themes
        self.chats = chats
        self.users = users
        self.next_offset = next_offset

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.next_offset is not None:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_long(self.hash)
        w.write_vector(self.themes)
        w.write_vector(self.chats)
        w.write_vector(self.users)
        if self.next_offset is not None:
            w.write_string(self.next_offset)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hash = r.read_long()
        themes = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        next_offset = r.read_string() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.hash = hash
        self.themes = themes
        self.chats = chats
        self.users = users
        self.next_offset = next_offset
        return self


class SavedRingtonesNotModified(TLObject):
    """The TL type account.savedRingtonesNotModified#fbf6e8b1, a form of account.SavedRingtones."""

    __slots__ = ()

    ID = 0xFBF6E8B1
    QUALNAME = "types.account.SavedRingtonesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedRingtones(TLObject):
    """The TL type account.savedRingtones#c1e92cc5, a form of account.SavedRingtones."""

    __slots__ = ("hash", "ringtones",)

    ID = 0xC1E92CC5
    QUALNAME = "types.account.SavedRingtones"

    def __init__(
        self,
        *,
        hash: int,
        ringtones: list[base.Document],
    ) -> None:
        self.hash = hash
        self.ringtones = ringtones

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.ringtones)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        ringtones = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.ringtones = ringtones
        return self


class SavedRingtone(TLObject):
    """The TL type account.savedRingtone#b7263f6d, a form of account.SavedRingtone."""

    __slots__ = ()

    ID = 0xB7263F6D
    QUALNAME = "types.account.SavedRingtone"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedRingtoneConverted(TLObject):
    """The TL type account.savedRingtoneConverted#1f307eb7, a form of account.SavedRingtone."""

    __slots__ = ("document",)

    ID = 0x1F307EB7
    QUALNAME = "types.account.SavedRingtoneConverted"

    def __init__(
        self,
        *,
        document: base.Document,
    ) -> None:
        self.document = document

    def write_body(self, w: TLWriter) -> None:
        self.document.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        document = r.read_object()
        self = cls.__new__(cls)
        self.document = document
        return self


class EmojiStatusesNotModified(TLObject):
    """The TL type account.emojiStatusesNotModified#d08ce645, a form of account.EmojiStatuses."""

    __slots__ = ()

    ID = 0xD08CE645
    QUALNAME = "types.account.EmojiStatusesNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class EmojiStatuses(TLObject):
    """The TL type account.emojiStatuses#90c467d1, a form of account.EmojiStatuses."""

    __slots__ = ("hash", "statuses",)

    ID = 0x90C467D1
    QUALNAME = "types.account.EmojiStatuses"

    def __init__(
        self,
        *,
        hash: int,
        statuses: list[base.EmojiStatus],
    ) -> None:
        self.hash = hash
        self.statuses = statuses

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.hash)
        w.write_vector(self.statuses)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_long()
        statuses = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.statuses = statuses
        return self


class EmailVerified(TLObject):
    """The TL type account.emailVerified#2b96cd1b, a form of account.EmailVerified."""

    __slots__ = ("email",)

    ID = 0x2B96CD1B
    QUALNAME = "types.account.EmailVerified"

    def __init__(
        self,
        *,
        email: str,
    ) -> None:
        self.email = email

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.email)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        email = r.read_string()
        self = cls.__new__(cls)
        self.email = email
        return self


class EmailVerifiedLogin(TLObject):
    """The TL type account.emailVerifiedLogin#e1bb0d61, a form of account.EmailVerified."""

    __slots__ = ("email", "sent_code",)

    ID = 0xE1BB0D61
    QUALNAME = "types.account.EmailVerifiedLogin"

    def __init__(
        self,
        *,
        email: str,
        sent_code: base.auth.SentCode,
    ) -> None:
        self.email = email
        self.sent_code = sent_code

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.email)
        self.sent_code.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        email = r.read_string()
        sent_code = r.read_object()
        self = cls.__new__(cls)
        self.email = email
        self.sent_code = sent_code
        return self


class AutoSaveSettings(TLObject):
    """The TL type account.autoSaveSettings#4c3e069d, a form of account.AutoSaveSettings."""

    __slots__ = ("users_settings", "chats_settings", "broadcasts_settings", "exceptions", "chats", "users",)

    ID = 0x4C3E069D
    QUALNAME = "types.account.AutoSaveSettings"

    def __init__(
        self,
        *,
        users_settings: base.AutoSaveSettings,
        chats_settings: base.AutoSaveSettings,
        broadcasts_settings: base.AutoSaveSettings,
        exceptions: list[base.AutoSaveException],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.users_settings = users_settings
        self.chats_settings = chats_settings
        self.broadcasts_settings = broadcasts_settings
        self.exceptions = exceptions
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        self.users_settings.write(w)
        self.chats_settings.write(w)
        self.broadcasts_settings.write(w)
        w.write_vector(self.exceptions)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        users_settings = r.read_object()
        chats_settings = r.read_object()
        broadcasts_settings = r.read_object()
        exceptions = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.users_settings = users_settings
        self.chats_settings = chats_settings
        self.broadcasts_settings = broadcasts_settings
        self.exceptions = exceptions
        self.chats = chats
        self.users = users
        return self


class ConnectedBots(TLObject):
    """The TL type account.connectedBots#17d7f87b, a form of account.ConnectedBots."""

    __slots__ = ("connected_bots", "users",)

    ID = 0x17D7F87B
    QUALNAME = "types.account.ConnectedBots"

    def __init__(
        self,
        *,
        connected_bots: list[base.ConnectedBot],
        users: list[base.User],
    ) -> None:
        self.connected_bots = connected_bots
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.connected_bots)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        connected_bots = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.connected_bots = connected_bots
        self.users = users
        return self


class BusinessChatLinks(TLObject):
    """The TL type account.businessChatLinks#ec43a2d1, a form of account.BusinessChatLinks."""

    __slots__ = ("links", "chats", "users",)

    ID = 0xEC43A2D1
    QUALNAME = "types.account.BusinessChatLinks"

    def __init__(
        self,
        *,
        links: list[base.BusinessChatLink],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.links = links
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.links)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        links = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.links = links
        self.chats = chats
        self.users = users
        return self


class ResolvedBusinessChatLinks(TLObject):
    """The TL type account.resolvedBusinessChatLinks#9a23af21, a form of account.ResolvedBusinessChatLinks."""

    __slots__ = ("peer", "message", "entities", "chats", "users",)

    ID = 0x9A23AF21
    QUALNAME = "types.account.ResolvedBusinessChatLinks"

    def __init__(
        self,
        *,
        peer: base.Peer,
        message: str,
        entities: list[base.MessageEntity] | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.peer = peer
        self.message = message
        self.entities = entities
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.entities is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.peer.write(w)
        w.write_string(self.message)
        if self.entities is not None:
            w.write_vector(self.entities)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        peer = r.read_object()
        message = r.read_string()
        entities = r.read_vector() if flags & (1 << 0) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.peer = peer
        self.message = message
        self.entities = entities
        self.chats = chats
        self.users = users
        return self


class PaidMessagesRevenue(TLObject):
    """The TL type account.paidMessagesRevenue#1e109708, a form of account.PaidMessagesRevenue."""

    __slots__ = ("stars_amount",)

    ID = 0x1E109708
    QUALNAME = "types.account.PaidMessagesRevenue"

    def __init__(
        self,
        *,
        stars_amount: int,
    ) -> None:
        self.stars_amount = stars_amount

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.stars_amount)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        stars_amount = r.read_long()
        self = cls.__new__(cls)
        self.stars_amount = stars_amount
        return self


class SavedMusicIdsNotModified(TLObject):
    """The TL type account.savedMusicIdsNotModified#4fc81d6e, a form of account.SavedMusicIds."""

    __slots__ = ()

    ID = 0x4FC81D6E
    QUALNAME = "types.account.SavedMusicIdsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SavedMusicIds(TLObject):
    """The TL type account.savedMusicIds#998d6636, a form of account.SavedMusicIds."""

    __slots__ = ("ids",)

    ID = 0x998D6636
    QUALNAME = "types.account.SavedMusicIds"

    def __init__(
        self,
        *,
        ids: list[int],
    ) -> None:
        self.ids = ids

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.ids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.ids = ids
        return self


class Passkeys(TLObject):
    """The TL type account.passkeys#f8e0aa1c, a form of account.Passkeys."""

    __slots__ = ("passkeys",)

    ID = 0xF8E0AA1C
    QUALNAME = "types.account.Passkeys"

    def __init__(
        self,
        *,
        passkeys: list[base.Passkey],
    ) -> None:
        self.passkeys = passkeys

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.passkeys)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        passkeys = r.read_vector()
        self = cls.__new__(cls)
        self.passkeys = passkeys
        return self


class PasskeyRegistrationOptions(TLObject):
    """The TL type account.passkeyRegistrationOptions#e16b5ce1, a form of account.PasskeyRegistrationOptions."""

    __slots__ = ("options",)

    ID = 0xE16B5CE1
    QUALNAME = "types.account.PasskeyRegistrationOptions"

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


class WebBrowserSettingsNotModified(TLObject):
    """The TL type account.webBrowserSettingsNotModified#c31c8f4e, a form of account.WebBrowserSettings."""

    __slots__ = ()

    ID = 0xC31C8F4E
    QUALNAME = "types.account.WebBrowserSettingsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class WebBrowserSettings(TLObject):
    """The TL type account.webBrowserSettings#79eb8cb3, a form of account.WebBrowserSettings."""

    __slots__ = ("open_external_browser", "display_close_button", "external_exceptions", "inapp_exceptions", "hash",)

    ID = 0x79EB8CB3
    QUALNAME = "types.account.WebBrowserSettings"

    def __init__(
        self,
        *,
        open_external_browser: bool = False,
        display_close_button: bool = False,
        external_exceptions: list[base.WebDomainException],
        inapp_exceptions: list[base.WebDomainException],
        hash: int,
    ) -> None:
        self.open_external_browser = open_external_browser
        self.display_close_button = display_close_button
        self.external_exceptions = external_exceptions
        self.inapp_exceptions = inapp_exceptions
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.open_external_browser:
            flags |= 1 << 0
        if self.display_close_button:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_vector(self.external_exceptions)
        w.write_vector(self.inapp_exceptions)
        w.write_long(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        open_external_browser = bool(flags & (1 << 0))
        display_close_button = bool(flags & (1 << 1))
        external_exceptions = r.read_vector()
        inapp_exceptions = r.read_vector()
        hash = r.read_long()
        self = cls.__new__(cls)
        self.open_external_browser = open_external_browser
        self.display_close_button = display_close_button
        self.external_exceptions = external_exceptions
        self.inapp_exceptions = inapp_exceptions
        self.hash = hash
        return self
