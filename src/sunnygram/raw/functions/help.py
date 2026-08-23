# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the help namespace.

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


class GetConfig(TLFunction["base.Config"]):
    """The TL function help.getConfig#c4f9186b, answered with Config."""

    __slots__ = ()

    ID = 0xC4F9186B
    QUALNAME = "functions.help.GetConfig"
    RESULT = "Config"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetNearestDc(TLFunction["base.NearestDc"]):
    """The TL function help.getNearestDc#1fb33026, answered with NearestDc."""

    __slots__ = ()

    ID = 0x1FB33026
    QUALNAME = "functions.help.GetNearestDc"
    RESULT = "NearestDc"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetAppUpdate(TLFunction["base.help.AppUpdate"]):
    """The TL function help.getAppUpdate#522d5a7d, answered with help.AppUpdate."""

    __slots__ = ("source",)

    ID = 0x522D5A7D
    QUALNAME = "functions.help.GetAppUpdate"
    RESULT = "help.AppUpdate"

    def __init__(
        self,
        *,
        source: str,
    ) -> None:
        self.source = source

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.source)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        source = r.read_string()
        self = cls.__new__(cls)
        self.source = source
        return self


class GetInviteText(TLFunction["base.help.InviteText"]):
    """The TL function help.getInviteText#4d392343, answered with help.InviteText."""

    __slots__ = ()

    ID = 0x4D392343
    QUALNAME = "functions.help.GetInviteText"
    RESULT = "help.InviteText"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetSupport(TLFunction["base.help.Support"]):
    """The TL function help.getSupport#9cdf08cd, answered with help.Support."""

    __slots__ = ()

    ID = 0x9CDF08CD
    QUALNAME = "functions.help.GetSupport"
    RESULT = "help.Support"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class SetBotUpdatesStatus(TLFunction["bool"]):
    """The TL function help.setBotUpdatesStatus#ec22cfcd, answered with Bool."""

    __slots__ = ("pending_updates_count", "message",)

    ID = 0xEC22CFCD
    QUALNAME = "functions.help.SetBotUpdatesStatus"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        pending_updates_count: int,
        message: str,
    ) -> None:
        self.pending_updates_count = pending_updates_count
        self.message = message

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.pending_updates_count)
        w.write_string(self.message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pending_updates_count = r.read_int()
        message = r.read_string()
        self = cls.__new__(cls)
        self.pending_updates_count = pending_updates_count
        self.message = message
        return self


class GetCdnConfig(TLFunction["base.CdnConfig"]):
    """The TL function help.getCdnConfig#52029342, answered with CdnConfig."""

    __slots__ = ()

    ID = 0x52029342
    QUALNAME = "functions.help.GetCdnConfig"
    RESULT = "CdnConfig"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetRecentMeUrls(TLFunction["base.help.RecentMeUrls"]):
    """The TL function help.getRecentMeUrls#3dc0f114, answered with help.RecentMeUrls."""

    __slots__ = ("referer",)

    ID = 0x3DC0F114
    QUALNAME = "functions.help.GetRecentMeUrls"
    RESULT = "help.RecentMeUrls"

    def __init__(
        self,
        *,
        referer: str,
    ) -> None:
        self.referer = referer

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.referer)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        referer = r.read_string()
        self = cls.__new__(cls)
        self.referer = referer
        return self


class GetTermsOfServiceUpdate(TLFunction["base.help.TermsOfServiceUpdate"]):
    """The TL function help.getTermsOfServiceUpdate#2ca51fd1, answered with help.TermsOfServiceUpdate."""

    __slots__ = ()

    ID = 0x2CA51FD1
    QUALNAME = "functions.help.GetTermsOfServiceUpdate"
    RESULT = "help.TermsOfServiceUpdate"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class AcceptTermsOfService(TLFunction["bool"]):
    """The TL function help.acceptTermsOfService#ee72f79a, answered with Bool."""

    __slots__ = ("id",)

    ID = 0xEE72F79A
    QUALNAME = "functions.help.AcceptTermsOfService"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        id: base.DataJSON,
    ) -> None:
        self.id = id

    def write_body(self, w: TLWriter) -> None:
        self.id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        id = r.read_object()
        self = cls.__new__(cls)
        self.id = id
        return self


class GetDeepLinkInfo(TLFunction["base.help.DeepLinkInfo"]):
    """The TL function help.getDeepLinkInfo#3fedc75f, answered with help.DeepLinkInfo."""

    __slots__ = ("path",)

    ID = 0x3FEDC75F
    QUALNAME = "functions.help.GetDeepLinkInfo"
    RESULT = "help.DeepLinkInfo"

    def __init__(
        self,
        *,
        path: str,
    ) -> None:
        self.path = path

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.path)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        path = r.read_string()
        self = cls.__new__(cls)
        self.path = path
        return self


class GetAppConfig(TLFunction["base.help.AppConfig"]):
    """The TL function help.getAppConfig#61e3f854, answered with help.AppConfig."""

    __slots__ = ("hash",)

    ID = 0x61E3F854
    QUALNAME = "functions.help.GetAppConfig"
    RESULT = "help.AppConfig"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class SaveAppLog(TLFunction["bool"]):
    """The TL function help.saveAppLog#6f02f748, answered with Bool."""

    __slots__ = ("events",)

    ID = 0x6F02F748
    QUALNAME = "functions.help.SaveAppLog"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        events: list[base.InputAppEvent],
    ) -> None:
        self.events = events

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.events)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        events = r.read_vector()
        self = cls.__new__(cls)
        self.events = events
        return self


class GetPassportConfig(TLFunction["base.help.PassportConfig"]):
    """The TL function help.getPassportConfig#c661ad08, answered with help.PassportConfig."""

    __slots__ = ("hash",)

    ID = 0xC661AD08
    QUALNAME = "functions.help.GetPassportConfig"
    RESULT = "help.PassportConfig"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetSupportName(TLFunction["base.help.SupportName"]):
    """The TL function help.getSupportName#d360e72c, answered with help.SupportName."""

    __slots__ = ()

    ID = 0xD360E72C
    QUALNAME = "functions.help.GetSupportName"
    RESULT = "help.SupportName"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetUserInfo(TLFunction["base.help.UserInfo"]):
    """The TL function help.getUserInfo#038a08d3, answered with help.UserInfo."""

    __slots__ = ("user_id",)

    ID = 0x038A08D3
    QUALNAME = "functions.help.GetUserInfo"
    RESULT = "help.UserInfo"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
    ) -> None:
        self.user_id = user_id

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        self = cls.__new__(cls)
        self.user_id = user_id
        return self


class EditUserInfo(TLFunction["base.help.UserInfo"]):
    """The TL function help.editUserInfo#66b91b70, answered with help.UserInfo."""

    __slots__ = ("user_id", "message", "entities",)

    ID = 0x66B91B70
    QUALNAME = "functions.help.EditUserInfo"
    RESULT = "help.UserInfo"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        message: str,
        entities: list[base.MessageEntity],
    ) -> None:
        self.user_id = user_id
        self.message = message
        self.entities = entities

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        w.write_string(self.message)
        w.write_vector(self.entities)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        message = r.read_string()
        entities = r.read_vector()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.message = message
        self.entities = entities
        return self


class GetPromoData(TLFunction["base.help.PromoData"]):
    """The TL function help.getPromoData#c0977421, answered with help.PromoData."""

    __slots__ = ()

    ID = 0xC0977421
    QUALNAME = "functions.help.GetPromoData"
    RESULT = "help.PromoData"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class HidePromoData(TLFunction["bool"]):
    """The TL function help.hidePromoData#1e251c95, answered with Bool."""

    __slots__ = ("peer",)

    ID = 0x1E251C95
    QUALNAME = "functions.help.HidePromoData"
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


class DismissSuggestion(TLFunction["bool"]):
    """The TL function help.dismissSuggestion#f50dbaa1, answered with Bool."""

    __slots__ = ("peer", "suggestion",)

    ID = 0xF50DBAA1
    QUALNAME = "functions.help.DismissSuggestion"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        peer: base.InputPeer,
        suggestion: str,
    ) -> None:
        self.peer = peer
        self.suggestion = suggestion

    def write_body(self, w: TLWriter) -> None:
        self.peer.write(w)
        w.write_string(self.suggestion)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        peer = r.read_object()
        suggestion = r.read_string()
        self = cls.__new__(cls)
        self.peer = peer
        self.suggestion = suggestion
        return self


class GetCountriesList(TLFunction["base.help.CountriesList"]):
    """The TL function help.getCountriesList#735787a8, answered with help.CountriesList."""

    __slots__ = ("lang_code", "hash",)

    ID = 0x735787A8
    QUALNAME = "functions.help.GetCountriesList"
    RESULT = "help.CountriesList"

    def __init__(
        self,
        *,
        lang_code: str,
        hash: int,
    ) -> None:
        self.lang_code = lang_code
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.lang_code)
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        lang_code = r.read_string()
        hash = r.read_int()
        self = cls.__new__(cls)
        self.lang_code = lang_code
        self.hash = hash
        return self


class GetPremiumPromo(TLFunction["base.help.PremiumPromo"]):
    """The TL function help.getPremiumPromo#b81b93d4, answered with help.PremiumPromo."""

    __slots__ = ()

    ID = 0xB81B93D4
    QUALNAME = "functions.help.GetPremiumPromo"
    RESULT = "help.PremiumPromo"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class GetPeerColors(TLFunction["base.help.PeerColors"]):
    """The TL function help.getPeerColors#da80f42f, answered with help.PeerColors."""

    __slots__ = ("hash",)

    ID = 0xDA80F42F
    QUALNAME = "functions.help.GetPeerColors"
    RESULT = "help.PeerColors"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetPeerProfileColors(TLFunction["base.help.PeerColors"]):
    """The TL function help.getPeerProfileColors#abcfa9fd, answered with help.PeerColors."""

    __slots__ = ("hash",)

    ID = 0xABCFA9FD
    QUALNAME = "functions.help.GetPeerProfileColors"
    RESULT = "help.PeerColors"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self


class GetTimezonesList(TLFunction["base.help.TimezonesList"]):
    """The TL function help.getTimezonesList#49b30240, answered with help.TimezonesList."""

    __slots__ = ("hash",)

    ID = 0x49B30240
    QUALNAME = "functions.help.GetTimezonesList"
    RESULT = "help.TimezonesList"

    def __init__(
        self,
        *,
        hash: int,
    ) -> None:
        self.hash = hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        hash = r.read_int()
        self = cls.__new__(cls)
        self.hash = hash
        return self
