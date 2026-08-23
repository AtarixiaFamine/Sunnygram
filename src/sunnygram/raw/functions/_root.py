# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the root namespace.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self, cast

from ...tl import TLFunction, TLReader, TLResult, TLWriter

if TYPE_CHECKING:
    from .. import base


class InvokeAfterMsg(TLFunction[TLResult]):
    """The TL function invokeAfterMsg#cb9f372d, answered with X."""

    __slots__ = ("msg_id", "query",)

    ID = 0xCB9F372D
    QUALNAME = "functions.InvokeAfterMsg"
    RESULT = "X"

    def __init__(
        self,
        *,
        msg_id: int,
        query: TLFunction[TLResult],
    ) -> None:
        self.msg_id = msg_id
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.msg_id)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_id = r.read_long()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.msg_id = msg_id
        self.query = query
        return self


class InvokeAfterMsgs(TLFunction[TLResult]):
    """The TL function invokeAfterMsgs#3dc4b4f0, answered with X."""

    __slots__ = ("msg_ids", "query",)

    ID = 0x3DC4B4F0
    QUALNAME = "functions.InvokeAfterMsgs"
    RESULT = "X"

    def __init__(
        self,
        *,
        msg_ids: list[int],
        query: TLFunction[TLResult],
    ) -> None:
        self.msg_ids = msg_ids
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.msg_ids, TLWriter.write_long)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_ids = r.read_vector(TLReader.read_long)
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.msg_ids = msg_ids
        self.query = query
        return self


class InitConnection(TLFunction[TLResult]):
    """The TL function initConnection#c1cd5ea9, answered with X."""

    __slots__ = ("api_id", "device_model", "system_version", "app_version", "system_lang_code", "lang_pack", "lang_code", "proxy", "params", "query",)

    ID = 0xC1CD5EA9
    QUALNAME = "functions.InitConnection"
    RESULT = "X"

    def __init__(
        self,
        *,
        api_id: int,
        device_model: str,
        system_version: str,
        app_version: str,
        system_lang_code: str,
        lang_pack: str,
        lang_code: str,
        proxy: base.InputClientProxy | None = None,
        params: base.JSONValue | None = None,
        query: TLFunction[TLResult],
    ) -> None:
        self.api_id = api_id
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version
        self.system_lang_code = system_lang_code
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.proxy = proxy
        self.params = params
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        flags = 0
        if self.proxy is not None:
            flags |= 1 << 0
        if self.params is not None:
            flags |= 1 << 1
        w.write_int(flags)
        w.write_int(self.api_id)
        w.write_string(self.device_model)
        w.write_string(self.system_version)
        w.write_string(self.app_version)
        w.write_string(self.system_lang_code)
        w.write_string(self.lang_pack)
        w.write_string(self.lang_code)
        if self.proxy is not None:
            self.proxy.write(w)
        if self.params is not None:
            self.params.write(w)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        flags = r.read_int()
        api_id = r.read_int()
        device_model = r.read_string()
        system_version = r.read_string()
        app_version = r.read_string()
        system_lang_code = r.read_string()
        lang_pack = r.read_string()
        lang_code = r.read_string()
        proxy = r.read_object() if flags & (1 << 0) else None
        params = r.read_object() if flags & (1 << 1) else None
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.api_id = api_id
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version
        self.system_lang_code = system_lang_code
        self.lang_pack = lang_pack
        self.lang_code = lang_code
        self.proxy = proxy
        self.params = params
        self.query = query
        return self


class InvokeWithLayer(TLFunction[TLResult]):
    """The TL function invokeWithLayer#da9b0d0d, answered with X."""

    __slots__ = ("layer", "query",)

    ID = 0xDA9B0D0D
    QUALNAME = "functions.InvokeWithLayer"
    RESULT = "X"

    def __init__(
        self,
        *,
        layer: int,
        query: TLFunction[TLResult],
    ) -> None:
        self.layer = layer
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.layer)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        layer = r.read_int()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.layer = layer
        self.query = query
        return self


class InvokeWithoutUpdates(TLFunction[TLResult]):
    """The TL function invokeWithoutUpdates#bf9459b7, answered with X."""

    __slots__ = ("query",)

    ID = 0xBF9459B7
    QUALNAME = "functions.InvokeWithoutUpdates"
    RESULT = "X"

    def __init__(
        self,
        *,
        query: TLFunction[TLResult],
    ) -> None:
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.query = query
        return self


class InvokeWithMessagesRange(TLFunction[TLResult]):
    """The TL function invokeWithMessagesRange#365275f2, answered with X."""

    __slots__ = ("range", "query",)

    ID = 0x365275F2
    QUALNAME = "functions.InvokeWithMessagesRange"
    RESULT = "X"

    def __init__(
        self,
        *,
        range: base.MessageRange,
        query: TLFunction[TLResult],
    ) -> None:
        self.range = range
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        self.range.write(w)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        range = r.read_object()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.range = range
        self.query = query
        return self


class InvokeWithTakeout(TLFunction[TLResult]):
    """The TL function invokeWithTakeout#aca9fd2e, answered with X."""

    __slots__ = ("takeout_id", "query",)

    ID = 0xACA9FD2E
    QUALNAME = "functions.InvokeWithTakeout"
    RESULT = "X"

    def __init__(
        self,
        *,
        takeout_id: int,
        query: TLFunction[TLResult],
    ) -> None:
        self.takeout_id = takeout_id
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.takeout_id)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        takeout_id = r.read_long()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.takeout_id = takeout_id
        self.query = query
        return self


class InvokeWithBusinessConnection(TLFunction[TLResult]):
    """The TL function invokeWithBusinessConnection#dd289f8e, answered with X."""

    __slots__ = ("connection_id", "query",)

    ID = 0xDD289F8E
    QUALNAME = "functions.InvokeWithBusinessConnection"
    RESULT = "X"

    def __init__(
        self,
        *,
        connection_id: str,
        query: TLFunction[TLResult],
    ) -> None:
        self.connection_id = connection_id
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.connection_id)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        connection_id = r.read_string()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.connection_id = connection_id
        self.query = query
        return self


class InvokeWithGooglePlayIntegrity(TLFunction[TLResult]):
    """The TL function invokeWithGooglePlayIntegrity#1df92984, answered with X."""

    __slots__ = ("nonce", "token", "query",)

    ID = 0x1DF92984
    QUALNAME = "functions.InvokeWithGooglePlayIntegrity"
    RESULT = "X"

    def __init__(
        self,
        *,
        nonce: str,
        token: str,
        query: TLFunction[TLResult],
    ) -> None:
        self.nonce = nonce
        self.token = token
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.nonce)
        w.write_string(self.token)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_string()
        token = r.read_string()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.nonce = nonce
        self.token = token
        self.query = query
        return self


class InvokeWithApnsSecret(TLFunction[TLResult]):
    """The TL function invokeWithApnsSecret#0dae54f8, answered with X."""

    __slots__ = ("nonce", "secret", "query",)

    ID = 0x0DAE54F8
    QUALNAME = "functions.InvokeWithApnsSecret"
    RESULT = "X"

    def __init__(
        self,
        *,
        nonce: str,
        secret: str,
        query: TLFunction[TLResult],
    ) -> None:
        self.nonce = nonce
        self.secret = secret
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.nonce)
        w.write_string(self.secret)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_string()
        secret = r.read_string()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.nonce = nonce
        self.secret = secret
        self.query = query
        return self


class InvokeWithReCaptcha(TLFunction[TLResult]):
    """The TL function invokeWithReCaptcha#adbb0f94, answered with X."""

    __slots__ = ("token", "query",)

    ID = 0xADBB0F94
    QUALNAME = "functions.InvokeWithReCaptcha"
    RESULT = "X"

    def __init__(
        self,
        *,
        token: str,
        query: TLFunction[TLResult],
    ) -> None:
        self.token = token
        self.query = query

    def write_body(self, w: TLWriter) -> None:
        w.write_string(self.token)
        self.query.write(w)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        token = r.read_string()
        query = cast("TLFunction[TLResult]", r.read_object())
        self = cls.__new__(cls)
        self.token = token
        self.query = query
        return self
