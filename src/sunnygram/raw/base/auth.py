# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the auth namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import auth as types_auth

    Authorization = (
        types_auth.Authorization
        | types_auth.AuthorizationSignUpRequired
    )

    CodeType = (
        types_auth.CodeTypeSms
        | types_auth.CodeTypeCall
        | types_auth.CodeTypeFlashCall
        | types_auth.CodeTypeMissedCall
        | types_auth.CodeTypeFragmentSms
    )

    ExportedAuthorization = types_auth.ExportedAuthorization

    LoggedOut = types_auth.LoggedOut

    LoginToken = (
        types_auth.LoginToken
        | types_auth.LoginTokenMigrateTo
        | types_auth.LoginTokenSuccess
    )

    PasskeyLoginOptions = types_auth.PasskeyLoginOptions

    PasswordRecovery = types_auth.PasswordRecovery

    SentCode = (
        types_auth.SentCode
        | types_auth.SentCodeSuccess
        | types_auth.SentCodePaymentRequired
    )

    SentCodeType = (
        types_auth.SentCodeTypeApp
        | types_auth.SentCodeTypeSms
        | types_auth.SentCodeTypeCall
        | types_auth.SentCodeTypeFlashCall
        | types_auth.SentCodeTypeMissedCall
        | types_auth.SentCodeTypeEmailCode
        | types_auth.SentCodeTypeSetUpEmailRequired
        | types_auth.SentCodeTypeFragmentSms
        | types_auth.SentCodeTypeFirebaseSms
        | types_auth.SentCodeTypeSmsWord
        | types_auth.SentCodeTypeSmsPhrase
    )
