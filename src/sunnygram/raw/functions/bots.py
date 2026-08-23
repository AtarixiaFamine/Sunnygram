# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the bots namespace.

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


class SendCustomRequest(TLFunction["base.DataJSON"]):
    """The TL function bots.sendCustomRequest#aa2769ed, answered with DataJSON."""

    __slots__ = ("custom_method", "params",)

    ID = 0xAA2769ED
    QUALNAME = "functions.bots.SendCustomRequest"
    RESULT = "DataJSON"

    def __init__(
        self,
        *,
        custom_method: str,
        params: base.DataJSON,
    ) -> None:
        self.custom_method = custom_method
        self.params = params

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.custom_method)
        self.params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        custom_method = r.read_string()
        params = r.read_object()
        self = cls.__new__(cls)
        self.custom_method = custom_method
        self.params = params
        return self


class AnswerWebhookJSONQuery(TLFunction["bool"]):
    """The TL function bots.answerWebhookJSONQuery#e6213f4d, answered with Bool."""

    __slots__ = ("query_id", "data",)

    ID = 0xE6213F4D
    QUALNAME = "functions.bots.AnswerWebhookJSONQuery"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        query_id: int,
        data: base.DataJSON,
    ) -> None:
        self.query_id = query_id
        self.data = data

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.query_id)
        self.data.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        query_id = r.read_long()
        data = r.read_object()
        self = cls.__new__(cls)
        self.query_id = query_id
        self.data = data
        return self


class SetBotCommands(TLFunction["bool"]):
    """The TL function bots.setBotCommands#0517165a, answered with Bool."""

    __slots__ = ("scope", "lang_code", "commands",)

    ID = 0x0517165A
    QUALNAME = "functions.bots.SetBotCommands"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        scope: base.BotCommandScope,
        lang_code: str,
        commands: list[base.BotCommand],
    ) -> None:
        self.scope = scope
        self.lang_code = lang_code
        self.commands = commands

    def write_body(self, w: TLWriter) -> None:
        self.scope.write(w)
        w.write_string(self.lang_code)
        w.write_vector(self.commands)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        scope = r.read_object()
        lang_code = r.read_string()
        commands = r.read_vector()
        self = cls.__new__(cls)
        self.scope = scope
        self.lang_code = lang_code
        self.commands = commands
        return self


class ResetBotCommands(TLFunction["bool"]):
    """The TL function bots.resetBotCommands#3d8de0f9, answered with Bool."""

    __slots__ = ("scope", "lang_code",)

    ID = 0x3D8DE0F9
    QUALNAME = "functions.bots.ResetBotCommands"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        scope: base.BotCommandScope,
        lang_code: str,
    ) -> None:
        self.scope = scope
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        self.scope.write(w)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        scope = r.read_object()
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.scope = scope
        self.lang_code = lang_code
        return self


class GetBotCommands(TLFunction["list[base.BotCommand]"]):
    """The TL function bots.getBotCommands#e34c0dd6, answered with Vector<BotCommand>."""

    __slots__ = ("scope", "lang_code",)

    ID = 0xE34C0DD6
    QUALNAME = "functions.bots.GetBotCommands"
    RESULT = "Vector<BotCommand>"

    def __init__(
        self,
        *,
        scope: base.BotCommandScope,
        lang_code: str,
    ) -> None:
        self.scope = scope
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        self.scope.write(w)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        scope = r.read_object()
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.scope = scope
        self.lang_code = lang_code
        return self


class SetBotMenuButton(TLFunction["bool"]):
    """The TL function bots.setBotMenuButton#4504d54f, answered with Bool."""

    __slots__ = ("user_id", "button",)

    ID = 0x4504D54F
    QUALNAME = "functions.bots.SetBotMenuButton"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        button: base.BotMenuButton,
    ) -> None:
        self.user_id = user_id
        self.button = button

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        self.button.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        button = r.read_object()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.button = button
        return self


class GetBotMenuButton(TLFunction["base.BotMenuButton"]):
    """The TL function bots.getBotMenuButton#9c60eb28, answered with BotMenuButton."""

    __slots__ = ("user_id",)

    ID = 0x9C60EB28
    QUALNAME = "functions.bots.GetBotMenuButton"
    RESULT = "BotMenuButton"

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


class SetBotBroadcastDefaultAdminRights(TLFunction["bool"]):
    """The TL function bots.setBotBroadcastDefaultAdminRights#788464e1, answered with Bool."""

    __slots__ = ("admin_rights",)

    ID = 0x788464E1
    QUALNAME = "functions.bots.SetBotBroadcastDefaultAdminRights"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        admin_rights: base.ChatAdminRights,
    ) -> None:
        self.admin_rights = admin_rights

    def write_body(self, w: TLWriter) -> None:
        self.admin_rights.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        admin_rights = r.read_object()
        self = cls.__new__(cls)
        self.admin_rights = admin_rights
        return self


class SetBotGroupDefaultAdminRights(TLFunction["bool"]):
    """The TL function bots.setBotGroupDefaultAdminRights#925ec9ea, answered with Bool."""

    __slots__ = ("admin_rights",)

    ID = 0x925EC9EA
    QUALNAME = "functions.bots.SetBotGroupDefaultAdminRights"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        admin_rights: base.ChatAdminRights,
    ) -> None:
        self.admin_rights = admin_rights

    def write_body(self, w: TLWriter) -> None:
        self.admin_rights.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        admin_rights = r.read_object()
        self = cls.__new__(cls)
        self.admin_rights = admin_rights
        return self


class SetBotInfo(TLFunction["bool"]):
    """The TL function bots.setBotInfo#10cf3123, answered with Bool."""

    __slots__ = ("bot", "lang_code", "name", "about", "description",)

    ID = 0x10CF3123
    QUALNAME = "functions.bots.SetBotInfo"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser | None = None,
        lang_code: str,
        name: str | None = None,
        about: str | None = None,
        description: str | None = None,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code
        self.name = name
        self.about = about
        self.description = description

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.bot is not None:
            flags |= 1 << 2
        if self.name is not None:
            flags |= 1 << 3
        if self.about is not None:
            flags |= 1 << 0
        if self.description is not None:
            flags |= 1 << 1
        w.write_int(flags)
        if self.bot is not None:
            self.bot.write(w)
        w.write_string(self.lang_code)
        if self.name is not None:
            w.write_string(self.name)
        if self.about is not None:
            w.write_string(self.about)
        if self.description is not None:
            w.write_string(self.description)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        bot = r.read_object() if flags & (1 << 2) else None
        lang_code = r.read_string()
        name = r.read_string() if flags & (1 << 3) else None
        about = r.read_string() if flags & (1 << 0) else None
        description = r.read_string() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        self.name = name
        self.about = about
        self.description = description
        return self


class GetBotInfo(TLFunction["base.bots.BotInfo"]):
    """The TL function bots.getBotInfo#dcd914fd, answered with bots.BotInfo."""

    __slots__ = ("bot", "lang_code",)

    ID = 0xDCD914FD
    QUALNAME = "functions.bots.GetBotInfo"
    RESULT = "bots.BotInfo"

    def __init__(
        self,
        *,
        bot: base.InputUser | None = None,
        lang_code: str,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.bot is not None:
            flags |= 1 << 0
        w.write_int(flags)
        if self.bot is not None:
            self.bot.write(w)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        bot = r.read_object() if flags & (1 << 0) else None
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        return self


class ReorderUsernames(TLFunction["bool"]):
    """The TL function bots.reorderUsernames#9709b1c2, answered with Bool."""

    __slots__ = ("bot", "order",)

    ID = 0x9709B1C2
    QUALNAME = "functions.bots.ReorderUsernames"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        order: list[str],
    ) -> None:
        self.bot = bot
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_vector(self.order, TLWriter.write_string)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        order = r.read_vector(TLReader.read_string)
        self = cls.__new__(cls)
        self.bot = bot
        self.order = order
        return self


class ToggleUsername(TLFunction["bool"]):
    """The TL function bots.toggleUsername#053ca973, answered with Bool."""

    __slots__ = ("bot", "username", "active",)

    ID = 0x053CA973
    QUALNAME = "functions.bots.ToggleUsername"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        username: str,
        active: bool,
    ) -> None:
        self.bot = bot
        self.username = username
        self.active = active

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.username)
        w.write_bool(self.active)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        username = r.read_string()
        active = r.read_bool()
        self = cls.__new__(cls)
        self.bot = bot
        self.username = username
        self.active = active
        return self


class CanSendMessage(TLFunction["bool"]):
    """The TL function bots.canSendMessage#1359f4e6, answered with Bool."""

    __slots__ = ("bot",)

    ID = 0x1359F4E6
    QUALNAME = "functions.bots.CanSendMessage"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class AllowSendMessage(TLFunction["base.Updates"]):
    """The TL function bots.allowSendMessage#f132e3ef, answered with Updates."""

    __slots__ = ("bot",)

    ID = 0xF132E3EF
    QUALNAME = "functions.bots.AllowSendMessage"
    RESULT = "Updates"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class InvokeWebViewCustomMethod(TLFunction["base.DataJSON"]):
    """The TL function bots.invokeWebViewCustomMethod#087fc5e7, answered with DataJSON."""

    __slots__ = ("bot", "custom_method", "params",)

    ID = 0x087FC5E7
    QUALNAME = "functions.bots.InvokeWebViewCustomMethod"
    RESULT = "DataJSON"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        custom_method: str,
        params: base.DataJSON,
    ) -> None:
        self.bot = bot
        self.custom_method = custom_method
        self.params = params

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.custom_method)
        self.params.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        custom_method = r.read_string()
        params = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        self.custom_method = custom_method
        self.params = params
        return self


class GetPopularAppBots(TLFunction["base.bots.PopularAppBots"]):
    """The TL function bots.getPopularAppBots#c2510192, answered with bots.PopularAppBots."""

    __slots__ = ("offset", "limit",)

    ID = 0xC2510192
    QUALNAME = "functions.bots.GetPopularAppBots"
    RESULT = "bots.PopularAppBots"

    def __init__(
        self,
        *,
        offset: str,
        limit: int,
    ) -> None:
        self.offset = offset
        self.limit = limit

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.offset)
        w.write_int(self.limit)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        offset = r.read_string()
        limit = r.read_int()
        self = cls.__new__(cls)
        self.offset = offset
        self.limit = limit
        return self


class AddPreviewMedia(TLFunction["base.BotPreviewMedia"]):
    """The TL function bots.addPreviewMedia#17aeb75a, answered with BotPreviewMedia."""

    __slots__ = ("bot", "lang_code", "media",)

    ID = 0x17AEB75A
    QUALNAME = "functions.bots.AddPreviewMedia"
    RESULT = "BotPreviewMedia"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        lang_code: str,
        media: base.InputMedia,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code
        self.media = media

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.lang_code)
        self.media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        lang_code = r.read_string()
        media = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        self.media = media
        return self


class EditPreviewMedia(TLFunction["base.BotPreviewMedia"]):
    """The TL function bots.editPreviewMedia#8525606f, answered with BotPreviewMedia."""

    __slots__ = ("bot", "lang_code", "media", "new_media",)

    ID = 0x8525606F
    QUALNAME = "functions.bots.EditPreviewMedia"
    RESULT = "BotPreviewMedia"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        lang_code: str,
        media: base.InputMedia,
        new_media: base.InputMedia,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code
        self.media = media
        self.new_media = new_media

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.lang_code)
        self.media.write(w)
        self.new_media.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        lang_code = r.read_string()
        media = r.read_object()
        new_media = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        self.media = media
        self.new_media = new_media
        return self


class DeletePreviewMedia(TLFunction["bool"]):
    """The TL function bots.deletePreviewMedia#2d0135b3, answered with Bool."""

    __slots__ = ("bot", "lang_code", "media",)

    ID = 0x2D0135B3
    QUALNAME = "functions.bots.DeletePreviewMedia"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        lang_code: str,
        media: list[base.InputMedia],
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code
        self.media = media

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.lang_code)
        w.write_vector(self.media)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        lang_code = r.read_string()
        media = r.read_vector()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        self.media = media
        return self


class ReorderPreviewMedias(TLFunction["bool"]):
    """The TL function bots.reorderPreviewMedias#b627f3aa, answered with Bool."""

    __slots__ = ("bot", "lang_code", "order",)

    ID = 0xB627F3AA
    QUALNAME = "functions.bots.ReorderPreviewMedias"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        lang_code: str,
        order: list[base.InputMedia],
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code
        self.order = order

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.lang_code)
        w.write_vector(self.order)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        lang_code = r.read_string()
        order = r.read_vector()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        self.order = order
        return self


class GetPreviewInfo(TLFunction["base.bots.PreviewInfo"]):
    """The TL function bots.getPreviewInfo#423ab3ad, answered with bots.PreviewInfo."""

    __slots__ = ("bot", "lang_code",)

    ID = 0x423AB3AD
    QUALNAME = "functions.bots.GetPreviewInfo"
    RESULT = "bots.PreviewInfo"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        lang_code: str,
    ) -> None:
        self.bot = bot
        self.lang_code = lang_code

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.lang_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        lang_code = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.lang_code = lang_code
        return self


class GetPreviewMedias(TLFunction["list[base.BotPreviewMedia]"]):
    """The TL function bots.getPreviewMedias#a2a5594d, answered with Vector<BotPreviewMedia>."""

    __slots__ = ("bot",)

    ID = 0xA2A5594D
    QUALNAME = "functions.bots.GetPreviewMedias"
    RESULT = "Vector<BotPreviewMedia>"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class UpdateUserEmojiStatus(TLFunction["bool"]):
    """The TL function bots.updateUserEmojiStatus#ed9f30c5, answered with Bool."""

    __slots__ = ("user_id", "emoji_status",)

    ID = 0xED9F30C5
    QUALNAME = "functions.bots.UpdateUserEmojiStatus"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        emoji_status: base.EmojiStatus,
    ) -> None:
        self.user_id = user_id
        self.emoji_status = emoji_status

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        self.emoji_status.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        emoji_status = r.read_object()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.emoji_status = emoji_status
        return self


class ToggleUserEmojiStatusPermission(TLFunction["bool"]):
    """The TL function bots.toggleUserEmojiStatusPermission#06de6392, answered with Bool."""

    __slots__ = ("bot", "enabled",)

    ID = 0x06DE6392
    QUALNAME = "functions.bots.ToggleUserEmojiStatusPermission"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        enabled: bool,
    ) -> None:
        self.bot = bot
        self.enabled = enabled

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_bool(self.enabled)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        enabled = r.read_bool()
        self = cls.__new__(cls)
        self.bot = bot
        self.enabled = enabled
        return self


class CheckDownloadFileParams(TLFunction["bool"]):
    """The TL function bots.checkDownloadFileParams#50077589, answered with Bool."""

    __slots__ = ("bot", "file_name", "url",)

    ID = 0x50077589
    QUALNAME = "functions.bots.CheckDownloadFileParams"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        file_name: str,
        url: str,
    ) -> None:
        self.bot = bot
        self.file_name = file_name
        self.url = url

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.file_name)
        w.write_string(self.url)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        file_name = r.read_string()
        url = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.file_name = file_name
        self.url = url
        return self


class GetAdminedBots(TLFunction["list[base.User]"]):
    """The TL function bots.getAdminedBots#b0711d83, answered with Vector<User>."""

    __slots__ = ()

    ID = 0xB0711D83
    QUALNAME = "functions.bots.GetAdminedBots"
    RESULT = "Vector<User>"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class UpdateStarRefProgram(TLFunction["base.StarRefProgram"]):
    """The TL function bots.updateStarRefProgram#778b5ab3, answered with StarRefProgram."""

    __slots__ = ("bot", "commission_permille", "duration_months",)

    ID = 0x778B5AB3
    QUALNAME = "functions.bots.UpdateStarRefProgram"
    RESULT = "StarRefProgram"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        commission_permille: int,
        duration_months: int | None = None,
    ) -> None:
        self.bot = bot
        self.commission_permille = commission_permille
        self.duration_months = duration_months

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.duration_months is not None:
            flags |= 1 << 0
        w.write_int(flags)
        self.bot.write(w)
        w.write_int(self.commission_permille)
        if self.duration_months is not None:
            w.write_int(self.duration_months)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        bot = r.read_object()
        commission_permille = r.read_int()
        duration_months = r.read_int() if flags & (1 << 0) else None
        self = cls.__new__(cls)
        self.bot = bot
        self.commission_permille = commission_permille
        self.duration_months = duration_months
        return self


class SetCustomVerification(TLFunction["bool"]):
    """The TL function bots.setCustomVerification#8b89dfbd, answered with Bool."""

    __slots__ = ("enabled", "bot", "peer", "custom_description",)

    ID = 0x8B89DFBD
    QUALNAME = "functions.bots.SetCustomVerification"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        enabled: bool = False,
        bot: base.InputUser | None = None,
        peer: base.InputPeer,
        custom_description: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.bot = bot
        self.peer = peer
        self.custom_description = custom_description

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.enabled:
            flags |= 1 << 1
        if self.bot is not None:
            flags |= 1 << 0
        if self.custom_description is not None:
            flags |= 1 << 2
        w.write_int(flags)
        if self.bot is not None:
            self.bot.write(w)
        self.peer.write(w)
        if self.custom_description is not None:
            w.write_string(self.custom_description)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        enabled = bool(flags & (1 << 1))
        bot = r.read_object() if flags & (1 << 0) else None
        peer = r.read_object()
        custom_description = r.read_string() if flags & (1 << 2) else None
        self = cls.__new__(cls)
        self.enabled = enabled
        self.bot = bot
        self.peer = peer
        self.custom_description = custom_description
        return self


class GetBotRecommendations(TLFunction["base.users.Users"]):
    """The TL function bots.getBotRecommendations#a1b70815, answered with users.Users."""

    __slots__ = ("bot",)

    ID = 0xA1B70815
    QUALNAME = "functions.bots.GetBotRecommendations"
    RESULT = "users.Users"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class CheckUsername(TLFunction["bool"]):
    """The TL function bots.checkUsername#87f2219b, answered with Bool."""

    __slots__ = ("username",)

    ID = 0x87F2219B
    QUALNAME = "functions.bots.CheckUsername"
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


class CreateBot(TLFunction["base.User"]):
    """The TL function bots.createBot#e5b17f2b, answered with User."""

    __slots__ = ("via_deeplink", "name", "username", "manager_id",)

    ID = 0xE5B17F2B
    QUALNAME = "functions.bots.CreateBot"
    RESULT = "User"

    def __init__(
        self,
        *,
        via_deeplink: bool = False,
        name: str,
        username: str,
        manager_id: base.InputUser,
    ) -> None:
        self.via_deeplink = via_deeplink
        self.name = name
        self.username = username
        self.manager_id = manager_id

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.via_deeplink:
            flags |= 1 << 0
        w.write_int(flags)
        w.write_string(self.name)
        w.write_string(self.username)
        self.manager_id.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        via_deeplink = bool(flags & (1 << 0))
        name = r.read_string()
        username = r.read_string()
        manager_id = r.read_object()
        self = cls.__new__(cls)
        self.via_deeplink = via_deeplink
        self.name = name
        self.username = username
        self.manager_id = manager_id
        return self


class ExportBotToken(TLFunction["base.bots.ExportedBotToken"]):
    """The TL function bots.exportBotToken#bd0d99eb, answered with bots.ExportedBotToken."""

    __slots__ = ("bot", "revoke",)

    ID = 0xBD0D99EB
    QUALNAME = "functions.bots.ExportBotToken"
    RESULT = "bots.ExportedBotToken"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        revoke: bool,
    ) -> None:
        self.bot = bot
        self.revoke = revoke

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_bool(self.revoke)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        revoke = r.read_bool()
        self = cls.__new__(cls)
        self.bot = bot
        self.revoke = revoke
        return self


class RequestWebViewButton(TLFunction["base.bots.RequestedButton"]):
    """The TL function bots.requestWebViewButton#31a2a35e, answered with bots.RequestedButton."""

    __slots__ = ("user_id", "button",)

    ID = 0x31A2A35E
    QUALNAME = "functions.bots.RequestWebViewButton"
    RESULT = "bots.RequestedButton"

    def __init__(
        self,
        *,
        user_id: base.InputUser,
        button: base.KeyboardButton,
    ) -> None:
        self.user_id = user_id
        self.button = button

    def write_body(self, w: TLWriter) -> None:
        self.user_id.write(w)
        self.button.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        user_id = r.read_object()
        button = r.read_object()
        self = cls.__new__(cls)
        self.user_id = user_id
        self.button = button
        return self


class GetRequestedWebViewButton(TLFunction["base.KeyboardButton"]):
    """The TL function bots.getRequestedWebViewButton#bf25b7f3, answered with KeyboardButton."""

    __slots__ = ("bot", "webapp_req_id",)

    ID = 0xBF25B7F3
    QUALNAME = "functions.bots.GetRequestedWebViewButton"
    RESULT = "KeyboardButton"

    def __init__(
        self,
        *,
        bot: base.InputUser,
        webapp_req_id: str,
    ) -> None:
        self.bot = bot
        self.webapp_req_id = webapp_req_id

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)
        w.write_string(self.webapp_req_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        webapp_req_id = r.read_string()
        self = cls.__new__(cls)
        self.bot = bot
        self.webapp_req_id = webapp_req_id
        return self


class GetAccessSettings(TLFunction["base.bots.AccessSettings"]):
    """The TL function bots.getAccessSettings#213853a3, answered with bots.AccessSettings."""

    __slots__ = ("bot",)

    ID = 0x213853A3
    QUALNAME = "functions.bots.GetAccessSettings"
    RESULT = "bots.AccessSettings"

    def __init__(
        self,
        *,
        bot: base.InputUser,
    ) -> None:
        self.bot = bot

    def write_body(self, w: TLWriter) -> None:
        self.bot.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bot = r.read_object()
        self = cls.__new__(cls)
        self.bot = bot
        return self


class EditAccessSettings(TLFunction["bool"]):
    """The TL function bots.editAccessSettings#31813cd8, answered with Bool."""

    __slots__ = ("restricted", "bot", "add_users",)

    ID = 0x31813CD8
    QUALNAME = "functions.bots.EditAccessSettings"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        restricted: bool = False,
        bot: base.InputUser,
        add_users: list[base.InputUser] | None = None,
    ) -> None:
        self.restricted = restricted
        self.bot = bot
        self.add_users = add_users

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.restricted:
            flags |= 1 << 0
        if self.add_users is not None:
            flags |= 1 << 1
        w.write_int(flags)
        self.bot.write(w)
        if self.add_users is not None:
            w.write_vector(self.add_users)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        restricted = bool(flags & (1 << 0))
        bot = r.read_object()
        add_users = r.read_vector() if flags & (1 << 1) else None
        self = cls.__new__(cls)
        self.restricted = restricted
        self.bot = bot
        self.add_users = add_users
        return self


class SetJoinChatResults(TLFunction["bool"]):
    """The TL function bots.setJoinChatResults#e71a4810, answered with Bool."""

    __slots__ = ("query_id", "result",)

    ID = 0xE71A4810
    QUALNAME = "functions.bots.SetJoinChatResults"
    RESULT = "Bool"

    def __init__(
        self,
        *,
        query_id: int,
        result: base.JoinChatBotResult,
    ) -> None:
        self.query_id = query_id
        self.result = result

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.query_id)
        self.result.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        query_id = r.read_long()
        result = r.read_object()
        self = cls.__new__(cls)
        self.query_id = query_id
        self.result = result
        return self
