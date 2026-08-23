# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL functions in the MTProto service schema.

read builds its object directly rather than calling __init__, which
is worth the odd shape: it is the path every incoming byte takes.

A constructor whose fields are all fixed-width and none of them
conditional has a layout that is known here, so it is written by one
struct call rather than one call per field. The field-by-field version
is kept underneath as the fallback, because struct refuses values this
library accepts: an id or a hash may arrive in either spelling.
"""

from __future__ import annotations

import struct

from typing import TYPE_CHECKING, Self

from ...tl import TLFunction, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base  # noqa: F401


class ReqPq(TLFunction["base.ResPQ"]):
    """The TL function req_pq#60469778, answered with ResPQ."""

    __slots__ = ("nonce",)

    ID = 0x60469778
    QUALNAME = "functions.mtproto.ReqPq"
    RESULT = "ResPQ"

    def __init__(
        self,
        *,
        nonce: int,
    ) -> None:
        self.nonce = nonce

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        return self


class ReqPqMulti(TLFunction["base.ResPQ"]):
    """The TL function req_pq_multi#be7e8ef1, answered with ResPQ."""

    __slots__ = ("nonce",)

    ID = 0xBE7E8EF1
    QUALNAME = "functions.mtproto.ReqPqMulti"
    RESULT = "ResPQ"

    def __init__(
        self,
        *,
        nonce: int,
    ) -> None:
        self.nonce = nonce

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        return self


class ReqDHParams(TLFunction["base.ServerDHParams"]):
    """The TL function req_DH_params#d712e4be, answered with Server_DH_Params."""

    __slots__ = ("nonce", "server_nonce", "p", "q", "public_key_fingerprint", "encrypted_data",)

    ID = 0xD712E4BE
    QUALNAME = "functions.mtproto.ReqDHParams"
    RESULT = "Server_DH_Params"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        p: bytes,
        q: bytes,
        public_key_fingerprint: int,
        encrypted_data: bytes,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.p = p
        self.q = q
        self.public_key_fingerprint = public_key_fingerprint
        self.encrypted_data = encrypted_data

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_bytes(self.p)
        w.write_bytes(self.q)
        w.write_long(self.public_key_fingerprint)
        w.write_bytes(self.encrypted_data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        p = r.read_bytes()
        q = r.read_bytes()
        public_key_fingerprint = r.read_long()
        encrypted_data = r.read_bytes()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.p = p
        self.q = q
        self.public_key_fingerprint = public_key_fingerprint
        self.encrypted_data = encrypted_data
        return self


class SetClientDHParams(TLFunction["base.SetClientDHParamsAnswer"]):
    """The TL function set_client_DH_params#f5045f1f, answered with Set_client_DH_params_answer."""

    __slots__ = ("nonce", "server_nonce", "encrypted_data",)

    ID = 0xF5045F1F
    QUALNAME = "functions.mtproto.SetClientDHParams"
    RESULT = "Set_client_DH_params_answer"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        encrypted_data: bytes,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.encrypted_data = encrypted_data

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_bytes(self.encrypted_data)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        encrypted_data = r.read_bytes()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.encrypted_data = encrypted_data
        return self


class DestroyAuthKey(TLFunction["base.DestroyAuthKeyRes"]):
    """The TL function destroy_auth_key#d1435160, answered with DestroyAuthKeyRes."""

    __slots__ = ()

    ID = 0xD1435160
    QUALNAME = "functions.mtproto.DestroyAuthKey"
    RESULT = "DestroyAuthKeyRes"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RpcDropAnswer(TLFunction["base.RpcDropAnswer"]):
    """The TL function rpc_drop_answer#58e4a740, answered with RpcDropAnswer."""

    __slots__ = ("req_msg_id",)

    ID = 0x58E4A740
    QUALNAME = "functions.mtproto.RpcDropAnswer"
    RESULT = "RpcDropAnswer"

    def __init__(
        self,
        *,
        req_msg_id: int,
    ) -> None:
        self.req_msg_id = req_msg_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.req_msg_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        req_msg_id = r.read_long()
        self = cls.__new__(cls)
        self.req_msg_id = req_msg_id
        return self


class GetFutureSalts(TLFunction["base.FutureSalts"]):
    """The TL function get_future_salts#b921bd04, answered with FutureSalts."""

    __slots__ = ("num",)

    ID = 0xB921BD04
    QUALNAME = "functions.mtproto.GetFutureSalts"
    RESULT = "FutureSalts"

    def __init__(
        self,
        *,
        num: int,
    ) -> None:
        self.num = num

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.num)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        num = r.read_int()
        self = cls.__new__(cls)
        self.num = num
        return self


class Ping(TLFunction["base.Pong"]):
    """The TL function ping#7abe77ec, answered with Pong."""

    __slots__ = ("ping_id",)

    ID = 0x7ABE77EC
    QUALNAME = "functions.mtproto.Ping"
    RESULT = "Pong"

    def __init__(
        self,
        *,
        ping_id: int,
    ) -> None:
        self.ping_id = ping_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.ping_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ping_id = r.read_long()
        self = cls.__new__(cls)
        self.ping_id = ping_id
        return self


_PACK_PingDelayDisconnect = struct.Struct("<qi")


class PingDelayDisconnect(TLFunction["base.Pong"]):
    """The TL function ping_delay_disconnect#f3427b8c, answered with Pong."""

    __slots__ = ("ping_id", "disconnect_delay",)

    ID = 0xF3427B8C
    QUALNAME = "functions.mtproto.PingDelayDisconnect"
    RESULT = "Pong"

    def __init__(
        self,
        *,
        ping_id: int,
        disconnect_delay: int,
    ) -> None:
        self.ping_id = ping_id
        self.disconnect_delay = disconnect_delay

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_PingDelayDisconnect.pack(self.ping_id, self.disconnect_delay))
        except struct.error:
            w.write_long(self.ping_id)
            w.write_int(self.disconnect_delay)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ping_id = r.read_long()
        disconnect_delay = r.read_int()
        self = cls.__new__(cls)
        self.ping_id = ping_id
        self.disconnect_delay = disconnect_delay
        return self


class DestroySession(TLFunction["base.DestroySessionRes"]):
    """The TL function destroy_session#e7512126, answered with DestroySessionRes."""

    __slots__ = ("session_id",)

    ID = 0xE7512126
    QUALNAME = "functions.mtproto.DestroySession"
    RESULT = "DestroySessionRes"

    def __init__(
        self,
        *,
        session_id: int,
    ) -> None:
        self.session_id = session_id

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.session_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        session_id = r.read_long()
        self = cls.__new__(cls)
        self.session_id = session_id
        return self
