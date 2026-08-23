# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the help namespace.

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


class ConfigSimple(TLObject):
    """The TL type help.configSimple#5a592a6c, a form of help.ConfigSimple."""

    __slots__ = ("date", "expires", "rules",)

    ID = 0x5A592A6C
    QUALNAME = "types.help.ConfigSimple"

    def __init__(
        self,
        *,
        date: int,
        expires: int,
        rules: list[base.AccessPointRule],
    ) -> None:
        self.date = date
        self.expires = expires
        self.rules = rules

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.date)
        w.write_int(self.expires)
        w.write_vector(self.rules, boxed=False)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        date = r.read_int()
        expires = r.read_int()
        rules = r.read_vector(boxed=False)
        self = cls.__new__(cls)
        self.date = date
        self.expires = expires
        self.rules = rules
        return self


class AppUpdate(TLObject):
    """The TL type help.appUpdate#ccbbce30, a form of help.AppUpdate."""

    __slots__ = ("can_not_skip", "id", "version", "text", "entities", "document", "url", "sticker",)

    ID = 0xCCBBCE30
    QUALNAME = "types.help.AppUpdate"

    def __init__(
        self,
        *,
        can_not_skip: bool = False,
        id: int,
        version: str,
        text: str,
        entities: list[base.MessageEntity],
        document: base.Document | None = None,
        url: str | None = None,
        sticker: base.Document | None = None,
    ) -> None:
        self.can_not_skip = can_not_skip
        self.id = id
        self.version = version
        self.text = text
        self.entities = entities
        self.document = document
        self.url = url
        self.sticker = sticker

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.can_not_skip:
            flags |= 1 << 0
        if self.document is not None:
            flags |= 1 << 1
        if self.url is not None:
            flags |= 1 << 2
        if self.sticker is not None:
            flags |= 1 << 3
        w.write_int(flags)
        w.write_int(self.id)
        w.write_string(self.version)
        w.write_string(self.text)
        w.write_vector(self.entities)
        if self.document is not None:
            self.document.write(w)
        if self.url is not None:
            w.write_string(self.url)
        if self.sticker is not None:
            self.sticker.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        can_not_skip = bool(flags & (1 << 0))
        id = r.read_int()
        version = r.read_string()
        text = r.read_string()
        entities = r.read_vector()
        document = r.read_object() if flags & (1 << 1) else None
        url = r.read_string() if flags & (1 << 2) else None
        sticker = r.read_object() if flags & (1 << 3) else None
        self = cls.__new__(cls)
        self.can_not_skip = can_not_skip
        self.id = id
        self.version = version
        self.text = text
        self.entities = entities
        self.document = document
        self.url = url
        self.sticker = sticker
        return self


class NoAppUpdate(TLObject):
    """The TL type help.noAppUpdate#c45a6536, a form of help.AppUpdate."""

    __slots__ = ()

    ID = 0xC45A6536
    QUALNAME = "types.help.NoAppUpdate"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class InviteText(TLObject):
    """The TL type help.inviteText#18cb9f78, a form of help.InviteText."""

    __slots__ = ("message",)

    ID = 0x18CB9F78
    QUALNAME = "types.help.InviteText"

    def __init__(
        self,
        *,
        message: str,
    ) -> None:
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        message = r.read_string()
        self = cls.__new__(cls)
        self.message = message
        return self


class Support(TLObject):
    """The TL type help.support#17c6b5f6, a form of help.Support."""

    __slots__ = ("phone_number", "user",)

    ID = 0x17C6B5F6
    QUALNAME = "types.help.Support"

    def __init__(
        self,
        *,
        phone_number: str,
        user: base.User,
    ) -> None:
        self.phone_number = phone_number
        self.user = user

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.phone_number)
        self.user.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_number = r.read_string()
        user = r.read_object()
        self = cls.__new__(cls)
        self.phone_number = phone_number
        self.user = user
        return self


class TermsOfService(TLObject):
    """The TL type help.termsOfService#780a0310, a form of help.TermsOfService."""

    __slots__ = ("popup", "id", "text", "entities", "min_age_confirm",)

    ID = 0x780A0310
    QUALNAME = "types.help.TermsOfService"

    def __init__(
        self,
        *,
        popup: bool = False,
        id: base.DataJSON,
        text: str,
        entities: list[base.MessageEntity],
        min_age_confirm: int | None = None,
    ) -> None:
        self.popup = popup
        self.id = id
        self.text = text
        self.entities = entities
        self.min_age_confirm = min_age_confirm

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.popup:
            flags |= 1 << 0
        if self.min_age_confirm is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.id.write(w)
        w.write_string(self.text)
        w.write_vector(self.entities)
        if self.min_age_confirm is not None:
            w.write_int(self.min_age_confirm)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        popup = bool(flags & (1 << 0))
        id = r.read_object()
        text = r.read_string()
        entities = r.read_vector()
        min_age_confirm = r.read_int() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.popup = popup
        self.id = id
        self.text = text
        self.entities = entities
        self.min_age_confirm = min_age_confirm
        return self


class RecentMeUrls(TLObject):
    """The TL type help.recentMeUrls#0e0310d7, a form of help.RecentMeUrls."""

    __slots__ = ("urls", "chats", "users",)

    ID = 0x0E0310D7
    QUALNAME = "types.help.RecentMeUrls"

    def __init__(
        self,
        *,
        urls: list[base.RecentMeUrl],
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.urls = urls
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.urls)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        urls = r.read_vector()
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.urls = urls
        self.chats = chats
        self.users = users
        return self


class TermsOfServiceUpdateEmpty(TLObject):
    """The TL type help.termsOfServiceUpdateEmpty#e3309f7f, a form of help.TermsOfServiceUpdate."""

    __slots__ = ("expires",)

    ID = 0xE3309F7F
    QUALNAME = "types.help.TermsOfServiceUpdateEmpty"

    def __init__(
        self,
        *,
        expires: int,
    ) -> None:
        self.expires = expires

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.expires)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        expires = r.read_int()
        self = cls.__new__(cls)
        self.expires = expires
        return self


class TermsOfServiceUpdate(TLObject):
    """The TL type help.termsOfServiceUpdate#28ecf961, a form of help.TermsOfServiceUpdate."""

    __slots__ = ("expires", "terms_of_service",)

    ID = 0x28ECF961
    QUALNAME = "types.help.TermsOfServiceUpdate"

    def __init__(
        self,
        *,
        expires: int,
        terms_of_service: base.help.TermsOfService,
    ) -> None:
        self.expires = expires
        self.terms_of_service = terms_of_service

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.expires)
        self.terms_of_service.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        expires = r.read_int()
        terms_of_service = r.read_object()
        self = cls.__new__(cls)
        self.expires = expires
        self.terms_of_service = terms_of_service
        return self


class DeepLinkInfoEmpty(TLObject):
    """The TL type help.deepLinkInfoEmpty#66afa166, a form of help.DeepLinkInfo."""

    __slots__ = ()

    ID = 0x66AFA166
    QUALNAME = "types.help.DeepLinkInfoEmpty"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DeepLinkInfo(TLObject):
    """The TL type help.deepLinkInfo#6a4ee832, a form of help.DeepLinkInfo."""

    __slots__ = ("update_app", "message", "entities",)

    ID = 0x6A4EE832
    QUALNAME = "types.help.DeepLinkInfo"

    def __init__(
        self,
        *,
        update_app: bool = False,
        message: str,
        entities: list[base.MessageEntity] | None = None,
    ) -> None:
        self.update_app = update_app
        self.message = message
        self.entities = entities

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.update_app:
            flags |= 1 << 0
        if self.entities is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.message)
        if self.entities is not None:
            w.write_vector(self.entities)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        update_app = bool(flags & (1 << 0))
        message = r.read_string()
        entities = r.read_vector() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.update_app = update_app
        self.message = message
        self.entities = entities
        return self


class PassportConfigNotModified(TLObject):
    """The TL type help.passportConfigNotModified#bfb9f457, a form of help.PassportConfig."""

    __slots__ = ()

    ID = 0xBFB9F457
    QUALNAME = "types.help.PassportConfigNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class PassportConfig(TLObject):
    """The TL type help.passportConfig#a098d6af, a form of help.PassportConfig."""

    __slots__ = ("hash", "countries_langs",)

    ID = 0xA098D6AF
    QUALNAME = "types.help.PassportConfig"

    def __init__(
        self,
        *,
        hash: int,
        countries_langs: base.DataJSON,
    ) -> None:
        self.hash = hash
        self.countries_langs = countries_langs

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        self.countries_langs.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        countries_langs = r.read_object()
        self = cls.__new__(cls)
        self.hash = hash
        self.countries_langs = countries_langs
        return self


class SupportName(TLObject):
    """The TL type help.supportName#8c05f1c9, a form of help.SupportName."""

    __slots__ = ("name",)

    ID = 0x8C05F1C9
    QUALNAME = "types.help.SupportName"

    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        self.name = name

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.name)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        name = r.read_string()
        self = cls.__new__(cls)
        self.name = name
        return self


class UserInfoEmpty(TLObject):
    """The TL type help.userInfoEmpty#f3ae2eed, a form of help.UserInfo."""

    __slots__ = ()

    ID = 0xF3AE2EED
    QUALNAME = "types.help.UserInfoEmpty"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UserInfo(TLObject):
    """The TL type help.userInfo#01eb3758, a form of help.UserInfo."""

    __slots__ = ("message", "entities", "author", "date",)

    ID = 0x01EB3758
    QUALNAME = "types.help.UserInfo"

    def __init__(
        self,
        *,
        message: str,
        entities: list[base.MessageEntity],
        author: str,
        date: int,
    ) -> None:
        self.message = message
        self.entities = entities
        self.author = author
        self.date = date

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.message)
        w.write_vector(self.entities)
        w.write_string(self.author)
        w.write_int(self.date)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        message = r.read_string()
        entities = r.read_vector()
        author = r.read_string()
        date = r.read_int()
        self = cls.__new__(cls)
        self.message = message
        self.entities = entities
        self.author = author
        self.date = date
        return self


class PromoDataEmpty(TLObject):
    """The TL type help.promoDataEmpty#98f6ac75, a form of help.PromoData."""

    __slots__ = ("expires",)

    ID = 0x98F6AC75
    QUALNAME = "types.help.PromoDataEmpty"

    def __init__(
        self,
        *,
        expires: int,
    ) -> None:
        self.expires = expires

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.expires)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        expires = r.read_int()
        self = cls.__new__(cls)
        self.expires = expires
        return self


class PromoData(TLObject):
    """The TL type help.promoData#08a4d87a, a form of help.PromoData."""

    __slots__ = ("proxy", "expires", "peer", "psa_type", "psa_message", "pending_suggestions", "dismissed_suggestions", "custom_pending_suggestion", "chats", "users",)

    ID = 0x08A4D87A
    QUALNAME = "types.help.PromoData"

    def __init__(
        self,
        *,
        proxy: bool = False,
        expires: int,
        peer: base.Peer | None = None,
        psa_type: str | None = None,
        psa_message: str | None = None,
        pending_suggestions: list[str],
        dismissed_suggestions: list[str],
        custom_pending_suggestion: base.PendingSuggestion | None = None,
        chats: list[base.Chat],
        users: list[base.User],
    ) -> None:
        self.proxy = proxy
        self.expires = expires
        self.peer = peer
        self.psa_type = psa_type
        self.psa_message = psa_message
        self.pending_suggestions = pending_suggestions
        self.dismissed_suggestions = dismissed_suggestions
        self.custom_pending_suggestion = custom_pending_suggestion
        self.chats = chats
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.proxy:
            flags |= 1 << 0
        if self.peer is not None:
            flags |= 1 << 3
        if self.psa_type is not None:
            flags |= 1 << 1
        if self.psa_message is not None:
            flags |= 1 << 2
        if self.custom_pending_suggestion is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_int(self.expires)
        if self.peer is not None:
            self.peer.write(w)
        if self.psa_type is not None:
            w.write_string(self.psa_type)
        if self.psa_message is not None:
            w.write_string(self.psa_message)
        w.write_vector(self.pending_suggestions, TLWriter.write_string)
        w.write_vector(self.dismissed_suggestions, TLWriter.write_string)
        if self.custom_pending_suggestion is not None:
            self.custom_pending_suggestion.write(w)
        w.write_vector(self.chats)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        proxy = bool(flags & (1 << 0))
        expires = r.read_int()
        peer = r.read_object() if flags & (1 << 3) else None
        psa_type = r.read_string() if flags & (1 << 1) else None
        psa_message = r.read_string() if flags & (1 << 2) else None
        pending_suggestions = r.read_vector(TLReader.read_string)
        dismissed_suggestions = r.read_vector(TLReader.read_string)
        custom_pending_suggestion = r.read_object() if flags & (1 << 4) else None
        chats = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.proxy = proxy
        self.expires = expires
        self.peer = peer
        self.psa_type = psa_type
        self.psa_message = psa_message
        self.pending_suggestions = pending_suggestions
        self.dismissed_suggestions = dismissed_suggestions
        self.custom_pending_suggestion = custom_pending_suggestion
        self.chats = chats
        self.users = users
        return self


class CountryCode(TLObject):
    """The TL type help.countryCode#4203c5ef, a form of help.CountryCode."""

    __slots__ = ("country_code", "prefixes", "patterns",)

    ID = 0x4203C5EF
    QUALNAME = "types.help.CountryCode"

    def __init__(
        self,
        *,
        country_code: str,
        prefixes: list[str] | None = None,
        patterns: list[str] | None = None,
    ) -> None:
        self.country_code = country_code
        self.prefixes = prefixes
        self.patterns = patterns

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.prefixes is not None:
            flags |= 1 << 0
        if self.patterns is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.country_code)
        if self.prefixes is not None:
            w.write_vector(self.prefixes, TLWriter.write_string)
        if self.patterns is not None:
            w.write_vector(self.patterns, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        country_code = r.read_string()
        prefixes = r.read_vector(TLReader.read_string) if flags & (1 << 0) else None
        patterns = r.read_vector(TLReader.read_string) if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.country_code = country_code
        self.prefixes = prefixes
        self.patterns = patterns
        return self


class Country(TLObject):
    """The TL type help.country#c3878e23, a form of help.Country."""

    __slots__ = ("hidden", "iso2", "default_name", "name", "country_codes",)

    ID = 0xC3878E23
    QUALNAME = "types.help.Country"

    def __init__(
        self,
        *,
        hidden: bool = False,
        iso2: str,
        default_name: str,
        name: str | None = None,
        country_codes: list[base.help.CountryCode],
    ) -> None:
        self.hidden = hidden
        self.iso2 = iso2
        self.default_name = default_name
        self.name = name
        self.country_codes = country_codes

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.hidden:
            flags |= 1 << 0
        if self.name is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_string(self.iso2)
        w.write_string(self.default_name)
        if self.name is not None:
            w.write_string(self.name)
        w.write_vector(self.country_codes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hidden = bool(flags & (1 << 0))
        iso2 = r.read_string()
        default_name = r.read_string()
        name = r.read_string() if flags & (1 << 1) else None
        country_codes = r.read_vector()
        self = cls.__new__(cls)
        self.hidden = hidden
        self.iso2 = iso2
        self.default_name = default_name
        self.name = name
        self.country_codes = country_codes
        return self


class CountriesListNotModified(TLObject):
    """The TL type help.countriesListNotModified#93cc1f32, a form of help.CountriesList."""

    __slots__ = ()

    ID = 0x93CC1F32
    QUALNAME = "types.help.CountriesListNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class CountriesList(TLObject):
    """The TL type help.countriesList#87d0759e, a form of help.CountriesList."""

    __slots__ = ("countries", "hash",)

    ID = 0x87D0759E
    QUALNAME = "types.help.CountriesList"

    def __init__(
        self,
        *,
        countries: list[base.help.Country],
        hash: int,
    ) -> None:
        self.countries = countries
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.countries)
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        countries = r.read_vector()
        hash = r.read_int()
        self = cls.__new__(cls)
        self.countries = countries
        self.hash = hash
        return self


class PremiumPromo(TLObject):
    """The TL type help.premiumPromo#5334759c, a form of help.PremiumPromo."""

    __slots__ = ("status_text", "status_entities", "video_sections", "videos", "period_options", "users",)

    ID = 0x5334759C
    QUALNAME = "types.help.PremiumPromo"

    def __init__(
        self,
        *,
        status_text: str,
        status_entities: list[base.MessageEntity],
        video_sections: list[str],
        videos: list[base.Document],
        period_options: list[base.PremiumSubscriptionOption],
        users: list[base.User],
    ) -> None:
        self.status_text = status_text
        self.status_entities = status_entities
        self.video_sections = video_sections
        self.videos = videos
        self.period_options = period_options
        self.users = users

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.status_text)
        w.write_vector(self.status_entities)
        w.write_vector(self.video_sections, TLWriter.write_string)
        w.write_vector(self.videos)
        w.write_vector(self.period_options)
        w.write_vector(self.users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        status_text = r.read_string()
        status_entities = r.read_vector()
        video_sections = r.read_vector(TLReader.read_string)
        videos = r.read_vector()
        period_options = r.read_vector()
        users = r.read_vector()
        self = cls.__new__(cls)
        self.status_text = status_text
        self.status_entities = status_entities
        self.video_sections = video_sections
        self.videos = videos
        self.period_options = period_options
        self.users = users
        return self


class AppConfigNotModified(TLObject):
    """The TL type help.appConfigNotModified#7cde641d, a form of help.AppConfig."""

    __slots__ = ()

    ID = 0x7CDE641D
    QUALNAME = "types.help.AppConfigNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class AppConfig(TLObject):
    """The TL type help.appConfig#dd18782e, a form of help.AppConfig."""

    __slots__ = ("hash", "config",)

    ID = 0xDD18782E
    QUALNAME = "types.help.AppConfig"

    def __init__(
        self,
        *,
        hash: int,
        config: base.JSONValue,
    ) -> None:
        self.hash = hash
        self.config = config

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        self.config.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        config = r.read_object()
        self = cls.__new__(cls)
        self.hash = hash
        self.config = config
        return self


class PeerColorSet(TLObject):
    """The TL type help.peerColorSet#26219a58, a form of help.PeerColorSet."""

    __slots__ = ("colors",)

    ID = 0x26219A58
    QUALNAME = "types.help.PeerColorSet"

    def __init__(
        self,
        *,
        colors: list[int],
    ) -> None:
        self.colors = colors

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.colors, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        colors = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.colors = colors
        return self


class PeerColorProfileSet(TLObject):
    """The TL type help.peerColorProfileSet#767d61eb, a form of help.PeerColorSet."""

    __slots__ = ("palette_colors", "bg_colors", "story_colors",)

    ID = 0x767D61EB
    QUALNAME = "types.help.PeerColorProfileSet"

    def __init__(
        self,
        *,
        palette_colors: list[int],
        bg_colors: list[int],
        story_colors: list[int],
    ) -> None:
        self.palette_colors = palette_colors
        self.bg_colors = bg_colors
        self.story_colors = story_colors

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.palette_colors, TLWriter.write_int)
        w.write_vector(self.bg_colors, TLWriter.write_int)
        w.write_vector(self.story_colors, TLWriter.write_int)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        palette_colors = r.read_vector(TLReader.read_int)
        bg_colors = r.read_vector(TLReader.read_int)
        story_colors = r.read_vector(TLReader.read_int)
        self = cls.__new__(cls)
        self.palette_colors = palette_colors
        self.bg_colors = bg_colors
        self.story_colors = story_colors
        return self


class PeerColorOption(TLObject):
    """The TL type help.peerColorOption#adec6ebe, a form of help.PeerColorOption."""

    __slots__ = ("hidden", "color_id", "colors", "dark_colors", "channel_min_level", "group_min_level",)

    ID = 0xADEC6EBE
    QUALNAME = "types.help.PeerColorOption"

    def __init__(
        self,
        *,
        hidden: bool = False,
        color_id: int,
        colors: base.help.PeerColorSet | None = None,
        dark_colors: base.help.PeerColorSet | None = None,
        channel_min_level: int | None = None,
        group_min_level: int | None = None,
    ) -> None:
        self.hidden = hidden
        self.color_id = color_id
        self.colors = colors
        self.dark_colors = dark_colors
        self.channel_min_level = channel_min_level
        self.group_min_level = group_min_level

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.hidden:
            flags |= 1 << 0
        if self.colors is not None:
            flags |= 1 << 1
        if self.dark_colors is not None:
            flags |= 1 << 2
        if self.channel_min_level is not None:
            flags |= 1 << 3
        if self.group_min_level is not None:
            flags |= 1 << 4
        w.write_int(flags)
        w.write_int(self.color_id)
        if self.colors is not None:
            self.colors.write(w)
        if self.dark_colors is not None:
            self.dark_colors.write(w)
        if self.channel_min_level is not None:
            w.write_int(self.channel_min_level)
        if self.group_min_level is not None:
            w.write_int(self.group_min_level)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        hidden = bool(flags & (1 << 0))
        color_id = r.read_int()
        colors = r.read_object() if flags & (1 << 1) else None
        dark_colors = r.read_object() if flags & (1 << 2) else None
        channel_min_level = r.read_int() if flags & (1 << 3) else None
        group_min_level = r.read_int() if flags & (1 << 4) else None
        self = cls.__new__(cls)
        self.hidden = hidden
        self.color_id = color_id
        self.colors = colors
        self.dark_colors = dark_colors
        self.channel_min_level = channel_min_level
        self.group_min_level = group_min_level
        return self


class PeerColorsNotModified(TLObject):
    """The TL type help.peerColorsNotModified#2ba1f5ce, a form of help.PeerColors."""

    __slots__ = ()

    ID = 0x2BA1F5CE
    QUALNAME = "types.help.PeerColorsNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class PeerColors(TLObject):
    """The TL type help.peerColors#00f8ed08, a form of help.PeerColors."""

    __slots__ = ("hash", "colors",)

    ID = 0x00F8ED08
    QUALNAME = "types.help.PeerColors"

    def __init__(
        self,
        *,
        hash: int,
        colors: list[base.help.PeerColorOption],
    ) -> None:
        self.hash = hash
        self.colors = colors

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)
        w.write_vector(self.colors)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        colors = r.read_vector()
        self = cls.__new__(cls)
        self.hash = hash
        self.colors = colors
        return self


class TimezonesListNotModified(TLObject):
    """The TL type help.timezonesListNotModified#970708cc, a form of help.TimezonesList."""

    __slots__ = ()

    ID = 0x970708CC
    QUALNAME = "types.help.TimezonesListNotModified"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class TimezonesList(TLObject):
    """The TL type help.timezonesList#7b74ed71, a form of help.TimezonesList."""

    __slots__ = ("timezones", "hash",)

    ID = 0x7B74ED71
    QUALNAME = "types.help.TimezonesList"

    def __init__(
        self,
        *,
        timezones: list[base.Timezone],
        hash: int,
    ) -> None:
        self.timezones = timezones
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.timezones)
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        timezones = r.read_vector()
        hash = r.read_int()
        self = cls.__new__(cls)
        self.timezones = timezones
        self.hash = hash
        return self
