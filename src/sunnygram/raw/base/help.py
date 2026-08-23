# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the help namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import help as types_help

    AppConfig = (
        types_help.AppConfigNotModified
        | types_help.AppConfig
    )

    AppUpdate = (
        types_help.AppUpdate
        | types_help.NoAppUpdate
    )

    ConfigSimple = types_help.ConfigSimple

    CountriesList = (
        types_help.CountriesListNotModified
        | types_help.CountriesList
    )

    Country = types_help.Country

    CountryCode = types_help.CountryCode

    DeepLinkInfo = (
        types_help.DeepLinkInfoEmpty
        | types_help.DeepLinkInfo
    )

    InviteText = types_help.InviteText

    PassportConfig = (
        types_help.PassportConfigNotModified
        | types_help.PassportConfig
    )

    PeerColorOption = types_help.PeerColorOption

    PeerColorSet = (
        types_help.PeerColorSet
        | types_help.PeerColorProfileSet
    )

    PeerColors = (
        types_help.PeerColorsNotModified
        | types_help.PeerColors
    )

    PremiumPromo = types_help.PremiumPromo

    PromoData = (
        types_help.PromoDataEmpty
        | types_help.PromoData
    )

    RecentMeUrls = types_help.RecentMeUrls

    Support = types_help.Support

    SupportName = types_help.SupportName

    TermsOfService = types_help.TermsOfService

    TermsOfServiceUpdate = (
        types_help.TermsOfServiceUpdateEmpty
        | types_help.TermsOfServiceUpdate
    )

    TimezonesList = (
        types_help.TimezonesListNotModified
        | types_help.TimezonesList
    )

    UserInfo = (
        types_help.UserInfoEmpty
        | types_help.UserInfo
    )
