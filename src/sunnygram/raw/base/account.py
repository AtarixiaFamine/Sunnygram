# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the account namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import account as types_account

    AuthorizationForm = types_account.AuthorizationForm

    Authorizations = types_account.Authorizations

    AutoDownloadSettings = types_account.AutoDownloadSettings

    AutoSaveSettings = types_account.AutoSaveSettings

    BusinessChatLinks = types_account.BusinessChatLinks

    ChatThemes = (
        types_account.ChatThemesNotModified
        | types_account.ChatThemes
    )

    ConnectedBots = types_account.ConnectedBots

    ContentSettings = types_account.ContentSettings

    EmailVerified = (
        types_account.EmailVerified
        | types_account.EmailVerifiedLogin
    )

    EmojiStatuses = (
        types_account.EmojiStatusesNotModified
        | types_account.EmojiStatuses
    )

    PaidMessagesRevenue = types_account.PaidMessagesRevenue

    PasskeyRegistrationOptions = types_account.PasskeyRegistrationOptions

    Passkeys = types_account.Passkeys

    Password = types_account.Password

    PasswordInputSettings = types_account.PasswordInputSettings

    PasswordSettings = types_account.PasswordSettings

    PrivacyRules = types_account.PrivacyRules

    ResetPasswordResult = (
        types_account.ResetPasswordFailedWait
        | types_account.ResetPasswordRequestedWait
        | types_account.ResetPasswordOk
    )

    ResolvedBusinessChatLinks = types_account.ResolvedBusinessChatLinks

    SavedMusicIds = (
        types_account.SavedMusicIdsNotModified
        | types_account.SavedMusicIds
    )

    SavedRingtone = (
        types_account.SavedRingtone
        | types_account.SavedRingtoneConverted
    )

    SavedRingtones = (
        types_account.SavedRingtonesNotModified
        | types_account.SavedRingtones
    )

    SentEmailCode = types_account.SentEmailCode

    Takeout = types_account.Takeout

    Themes = (
        types_account.ThemesNotModified
        | types_account.Themes
    )

    TmpPassword = types_account.TmpPassword

    WallPapers = (
        types_account.WallPapersNotModified
        | types_account.WallPapers
    )

    WebAuthorizations = types_account.WebAuthorizations

    WebBrowserSettings = (
        types_account.WebBrowserSettingsNotModified
        | types_account.WebBrowserSettings
    )
