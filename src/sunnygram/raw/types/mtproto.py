# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""TL constructors in the MTProto service schema.

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

from ...tl import TLObject, TLReader, TLWriter

if TYPE_CHECKING:
    from .. import base


class ResPQ(TLObject):
    """The TL type resPQ#05162463, a form of ResPQ."""

    __slots__ = ("nonce", "server_nonce", "pq", "server_public_key_fingerprints",)

    ID = 0x05162463
    QUALNAME = "types.mtproto.ResPQ"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        pq: bytes,
        server_public_key_fingerprints: list[int],
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.pq = pq
        self.server_public_key_fingerprints = server_public_key_fingerprints

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_bytes(self.pq)
        w.write_vector(self.server_public_key_fingerprints, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        pq = r.read_bytes()
        server_public_key_fingerprints = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.pq = pq
        self.server_public_key_fingerprints = server_public_key_fingerprints
        return self


class PQInnerData(TLObject):
    """The TL type p_q_inner_data#83c95aec, a form of P_Q_inner_data."""

    __slots__ = ("pq", "p", "q", "nonce", "server_nonce", "new_nonce",)

    ID = 0x83C95AEC
    QUALNAME = "types.mtproto.PQInnerData"

    def __init__(
        self,
        *,
        pq: bytes,
        p: bytes,
        q: bytes,
        nonce: int,
        server_nonce: int,
        new_nonce: int,
    ) -> None:
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.pq)
        w.write_bytes(self.p)
        w.write_bytes(self.q)
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int256(self.new_nonce)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pq = r.read_bytes()
        p = r.read_bytes()
        q = r.read_bytes()
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce = r.read_int256()
        self = cls.__new__(cls)
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        return self


class PQInnerDataDc(TLObject):
    """The TL type p_q_inner_data_dc#a9f55f95, a form of P_Q_inner_data."""

    __slots__ = ("pq", "p", "q", "nonce", "server_nonce", "new_nonce", "dc",)

    ID = 0xA9F55F95
    QUALNAME = "types.mtproto.PQInnerDataDc"

    def __init__(
        self,
        *,
        pq: bytes,
        p: bytes,
        q: bytes,
        nonce: int,
        server_nonce: int,
        new_nonce: int,
        dc: int,
    ) -> None:
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.dc = dc

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.pq)
        w.write_bytes(self.p)
        w.write_bytes(self.q)
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int256(self.new_nonce)
        w.write_int(self.dc)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pq = r.read_bytes()
        p = r.read_bytes()
        q = r.read_bytes()
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce = r.read_int256()
        dc = r.read_int()
        self = cls.__new__(cls)
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.dc = dc
        return self


class PQInnerDataTemp(TLObject):
    """The TL type p_q_inner_data_temp#3c6a84d4, a form of P_Q_inner_data."""

    __slots__ = ("pq", "p", "q", "nonce", "server_nonce", "new_nonce", "expires_in",)

    ID = 0x3C6A84D4
    QUALNAME = "types.mtproto.PQInnerDataTemp"

    def __init__(
        self,
        *,
        pq: bytes,
        p: bytes,
        q: bytes,
        nonce: int,
        server_nonce: int,
        new_nonce: int,
        expires_in: int,
    ) -> None:
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.expires_in = expires_in

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.pq)
        w.write_bytes(self.p)
        w.write_bytes(self.q)
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int256(self.new_nonce)
        w.write_int(self.expires_in)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pq = r.read_bytes()
        p = r.read_bytes()
        q = r.read_bytes()
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce = r.read_int256()
        expires_in = r.read_int()
        self = cls.__new__(cls)
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.expires_in = expires_in
        return self


class PQInnerDataTempDc(TLObject):
    """The TL type p_q_inner_data_temp_dc#56fddf88, a form of P_Q_inner_data."""

    __slots__ = ("pq", "p", "q", "nonce", "server_nonce", "new_nonce", "dc", "expires_in",)

    ID = 0x56FDDF88
    QUALNAME = "types.mtproto.PQInnerDataTempDc"

    def __init__(
        self,
        *,
        pq: bytes,
        p: bytes,
        q: bytes,
        nonce: int,
        server_nonce: int,
        new_nonce: int,
        dc: int,
        expires_in: int,
    ) -> None:
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.dc = dc
        self.expires_in = expires_in

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.pq)
        w.write_bytes(self.p)
        w.write_bytes(self.q)
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int256(self.new_nonce)
        w.write_int(self.dc)
        w.write_int(self.expires_in)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        pq = r.read_bytes()
        p = r.read_bytes()
        q = r.read_bytes()
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce = r.read_int256()
        dc = r.read_int()
        expires_in = r.read_int()
        self = cls.__new__(cls)
        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce
        self.dc = dc
        self.expires_in = expires_in
        return self


_PACK_BindAuthKeyInner = struct.Struct("<qqqqi")


class BindAuthKeyInner(TLObject):
    """The TL type bind_auth_key_inner#75a3f765, a form of BindAuthKeyInner."""

    __slots__ = ("nonce", "temp_auth_key_id", "perm_auth_key_id", "temp_session_id", "expires_at",)

    ID = 0x75A3F765
    QUALNAME = "types.mtproto.BindAuthKeyInner"

    def __init__(
        self,
        *,
        nonce: int,
        temp_auth_key_id: int,
        perm_auth_key_id: int,
        temp_session_id: int,
        expires_at: int,
    ) -> None:
        self.nonce = nonce
        self.temp_auth_key_id = temp_auth_key_id
        self.perm_auth_key_id = perm_auth_key_id
        self.temp_session_id = temp_session_id
        self.expires_at = expires_at

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_BindAuthKeyInner.pack(self.nonce, self.temp_auth_key_id, self.perm_auth_key_id, self.temp_session_id, self.expires_at))
        except struct.error:
            w.write_long(self.nonce)
            w.write_long(self.temp_auth_key_id)
            w.write_long(self.perm_auth_key_id)
            w.write_long(self.temp_session_id)
            w.write_int(self.expires_at)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_long()
        temp_auth_key_id = r.read_long()
        perm_auth_key_id = r.read_long()
        temp_session_id = r.read_long()
        expires_at = r.read_int()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.temp_auth_key_id = temp_auth_key_id
        self.perm_auth_key_id = perm_auth_key_id
        self.temp_session_id = temp_session_id
        self.expires_at = expires_at
        return self


class ServerDHParamsFail(TLObject):
    """The TL type server_DH_params_fail#79cb045d, a form of Server_DH_Params."""

    __slots__ = ("nonce", "server_nonce", "new_nonce_hash",)

    ID = 0x79CB045D
    QUALNAME = "types.mtproto.ServerDHParamsFail"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        new_nonce_hash: int,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash = new_nonce_hash

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int128(self.new_nonce_hash)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce_hash = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash = new_nonce_hash
        return self


class ServerDHParamsOk(TLObject):
    """The TL type server_DH_params_ok#d0e8075c, a form of Server_DH_Params."""

    __slots__ = ("nonce", "server_nonce", "encrypted_answer",)

    ID = 0xD0E8075C
    QUALNAME = "types.mtproto.ServerDHParamsOk"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        encrypted_answer: bytes,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.encrypted_answer = encrypted_answer

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_bytes(self.encrypted_answer)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        encrypted_answer = r.read_bytes()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.encrypted_answer = encrypted_answer
        return self


class ServerDHInnerData(TLObject):
    """The TL type server_DH_inner_data#b5890dba, a form of Server_DH_inner_data."""

    __slots__ = ("nonce", "server_nonce", "g", "dh_prime", "g_a", "server_time",)

    ID = 0xB5890DBA
    QUALNAME = "types.mtproto.ServerDHInnerData"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        g: int,
        dh_prime: bytes,
        g_a: bytes,
        server_time: int,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.g = g
        self.dh_prime = dh_prime
        self.g_a = g_a
        self.server_time = server_time

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int(self.g)
        w.write_bytes(self.dh_prime)
        w.write_bytes(self.g_a)
        w.write_int(self.server_time)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        g = r.read_int()
        dh_prime = r.read_bytes()
        g_a = r.read_bytes()
        server_time = r.read_int()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.g = g
        self.dh_prime = dh_prime
        self.g_a = g_a
        self.server_time = server_time
        return self


class ClientDHInnerData(TLObject):
    """The TL type client_DH_inner_data#6643b654, a form of Client_DH_Inner_Data."""

    __slots__ = ("nonce", "server_nonce", "retry_id", "g_b",)

    ID = 0x6643B654
    QUALNAME = "types.mtproto.ClientDHInnerData"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        retry_id: int,
        g_b: bytes,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.retry_id = retry_id
        self.g_b = g_b

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_long(self.retry_id)
        w.write_bytes(self.g_b)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        retry_id = r.read_long()
        g_b = r.read_bytes()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.retry_id = retry_id
        self.g_b = g_b
        return self


class DhGenOk(TLObject):
    """The TL type dh_gen_ok#3bcbf734, a form of Set_client_DH_params_answer."""

    __slots__ = ("nonce", "server_nonce", "new_nonce_hash1",)

    ID = 0x3BCBF734
    QUALNAME = "types.mtproto.DhGenOk"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        new_nonce_hash1: int,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash1 = new_nonce_hash1

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int128(self.new_nonce_hash1)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce_hash1 = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash1 = new_nonce_hash1
        return self


class DhGenRetry(TLObject):
    """The TL type dh_gen_retry#46dc1fb9, a form of Set_client_DH_params_answer."""

    __slots__ = ("nonce", "server_nonce", "new_nonce_hash2",)

    ID = 0x46DC1FB9
    QUALNAME = "types.mtproto.DhGenRetry"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        new_nonce_hash2: int,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash2 = new_nonce_hash2

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int128(self.new_nonce_hash2)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce_hash2 = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash2 = new_nonce_hash2
        return self


class DhGenFail(TLObject):
    """The TL type dh_gen_fail#a69dae02, a form of Set_client_DH_params_answer."""

    __slots__ = ("nonce", "server_nonce", "new_nonce_hash3",)

    ID = 0xA69DAE02
    QUALNAME = "types.mtproto.DhGenFail"

    def __init__(
        self,
        *,
        nonce: int,
        server_nonce: int,
        new_nonce_hash3: int,
    ) -> None:
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash3 = new_nonce_hash3

    def write_body(self, w: TLWriter) -> None:
        w.write_int128(self.nonce)
        w.write_int128(self.server_nonce)
        w.write_int128(self.new_nonce_hash3)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        nonce = r.read_int128()
        server_nonce = r.read_int128()
        new_nonce_hash3 = r.read_int128()
        self = cls.__new__(cls)
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash3 = new_nonce_hash3
        return self


class DestroyAuthKeyOk(TLObject):
    """The TL type destroy_auth_key_ok#f660e1d4, a form of DestroyAuthKeyRes."""

    __slots__ = ()

    ID = 0xF660E1D4
    QUALNAME = "types.mtproto.DestroyAuthKeyOk"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DestroyAuthKeyNone(TLObject):
    """The TL type destroy_auth_key_none#0a9f2259, a form of DestroyAuthKeyRes."""

    __slots__ = ()

    ID = 0x0A9F2259
    QUALNAME = "types.mtproto.DestroyAuthKeyNone"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class DestroyAuthKeyFail(TLObject):
    """The TL type destroy_auth_key_fail#ea109b13, a form of DestroyAuthKeyRes."""

    __slots__ = ()

    ID = 0xEA109B13
    QUALNAME = "types.mtproto.DestroyAuthKeyFail"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class MsgsAck(TLObject):
    """The TL type msgs_ack#62d6b459, a form of MsgsAck."""

    __slots__ = ("msg_ids",)

    ID = 0x62D6B459
    QUALNAME = "types.mtproto.MsgsAck"

    def __init__(
        self,
        *,
        msg_ids: list[int],
    ) -> None:
        self.msg_ids = msg_ids

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.msg_ids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_ids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.msg_ids = msg_ids
        return self


_PACK_BadMsgNotification = struct.Struct("<qii")


class BadMsgNotification(TLObject):
    """The TL type bad_msg_notification#a7eff811, a form of BadMsgNotification."""

    __slots__ = ("bad_msg_id", "bad_msg_seqno", "error_code",)

    ID = 0xA7EFF811
    QUALNAME = "types.mtproto.BadMsgNotification"

    def __init__(
        self,
        *,
        bad_msg_id: int,
        bad_msg_seqno: int,
        error_code: int,
    ) -> None:
        self.bad_msg_id = bad_msg_id
        self.bad_msg_seqno = bad_msg_seqno
        self.error_code = error_code

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_BadMsgNotification.pack(self.bad_msg_id, self.bad_msg_seqno, self.error_code))
        except struct.error:
            w.write_long(self.bad_msg_id)
            w.write_int(self.bad_msg_seqno)
            w.write_int(self.error_code)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bad_msg_id = r.read_long()
        bad_msg_seqno = r.read_int()
        error_code = r.read_int()
        self = cls.__new__(cls)
        self.bad_msg_id = bad_msg_id
        self.bad_msg_seqno = bad_msg_seqno
        self.error_code = error_code
        return self


_PACK_BadServerSalt = struct.Struct("<qiiq")


class BadServerSalt(TLObject):
    """The TL type bad_server_salt#edab447b, a form of BadMsgNotification."""

    __slots__ = ("bad_msg_id", "bad_msg_seqno", "error_code", "new_server_salt",)

    ID = 0xEDAB447B
    QUALNAME = "types.mtproto.BadServerSalt"

    def __init__(
        self,
        *,
        bad_msg_id: int,
        bad_msg_seqno: int,
        error_code: int,
        new_server_salt: int,
    ) -> None:
        self.bad_msg_id = bad_msg_id
        self.bad_msg_seqno = bad_msg_seqno
        self.error_code = error_code
        self.new_server_salt = new_server_salt

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_BadServerSalt.pack(self.bad_msg_id, self.bad_msg_seqno, self.error_code, self.new_server_salt))
        except struct.error:
            w.write_long(self.bad_msg_id)
            w.write_int(self.bad_msg_seqno)
            w.write_int(self.error_code)
            w.write_long(self.new_server_salt)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        bad_msg_id = r.read_long()
        bad_msg_seqno = r.read_int()
        error_code = r.read_int()
        new_server_salt = r.read_long()
        self = cls.__new__(cls)
        self.bad_msg_id = bad_msg_id
        self.bad_msg_seqno = bad_msg_seqno
        self.error_code = error_code
        self.new_server_salt = new_server_salt
        return self


class MsgsStateReq(TLObject):
    """The TL type msgs_state_req#da69fb52, a form of MsgsStateReq."""

    __slots__ = ("msg_ids",)

    ID = 0xDA69FB52
    QUALNAME = "types.mtproto.MsgsStateReq"

    def __init__(
        self,
        *,
        msg_ids: list[int],
    ) -> None:
        self.msg_ids = msg_ids

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.msg_ids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_ids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.msg_ids = msg_ids
        return self


class MsgsStateInfo(TLObject):
    """The TL type msgs_state_info#04deb57d, a form of MsgsStateInfo."""

    __slots__ = ("req_msg_id", "info",)

    ID = 0x04DEB57D
    QUALNAME = "types.mtproto.MsgsStateInfo"

    def __init__(
        self,
        *,
        req_msg_id: int,
        info: bytes,
    ) -> None:
        self.req_msg_id = req_msg_id
        self.info = info

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.req_msg_id)
        w.write_bytes(self.info)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        req_msg_id = r.read_long()
        info = r.read_bytes()
        self = cls.__new__(cls)
        self.req_msg_id = req_msg_id
        self.info = info
        return self


class MsgsAllInfo(TLObject):
    """The TL type msgs_all_info#8cc0d131, a form of MsgsAllInfo."""

    __slots__ = ("msg_ids", "info",)

    ID = 0x8CC0D131
    QUALNAME = "types.mtproto.MsgsAllInfo"

    def __init__(
        self,
        *,
        msg_ids: list[int],
        info: bytes,
    ) -> None:
        self.msg_ids = msg_ids
        self.info = info

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.msg_ids, TLWriter.write_long)
        w.write_bytes(self.info)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_ids = r.read_vector(TLReader.read_long)
        info = r.read_bytes()
        self = cls.__new__(cls)
        self.msg_ids = msg_ids
        self.info = info
        return self


_PACK_MsgDetailedInfo = struct.Struct("<qqii")


class MsgDetailedInfo(TLObject):
    """The TL type msg_detailed_info#276d3ec6, a form of MsgDetailedInfo."""

    __slots__ = ("msg_id", "answer_msg_id", "bytes", "status",)

    ID = 0x276D3EC6
    QUALNAME = "types.mtproto.MsgDetailedInfo"

    def __init__(
        self,
        *,
        msg_id: int,
        answer_msg_id: int,
        bytes: int,
        status: int,
    ) -> None:
        self.msg_id = msg_id
        self.answer_msg_id = answer_msg_id
        self.bytes = bytes
        self.status = status

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_MsgDetailedInfo.pack(self.msg_id, self.answer_msg_id, self.bytes, self.status))
        except struct.error:
            w.write_long(self.msg_id)
            w.write_long(self.answer_msg_id)
            w.write_int(self.bytes)
            w.write_int(self.status)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_id = r.read_long()
        answer_msg_id = r.read_long()
        bytes = r.read_int()
        status = r.read_int()
        self = cls.__new__(cls)
        self.msg_id = msg_id
        self.answer_msg_id = answer_msg_id
        self.bytes = bytes
        self.status = status
        return self


_PACK_MsgNewDetailedInfo = struct.Struct("<qii")


class MsgNewDetailedInfo(TLObject):
    """The TL type msg_new_detailed_info#809db6df, a form of MsgDetailedInfo."""

    __slots__ = ("answer_msg_id", "bytes", "status",)

    ID = 0x809DB6DF
    QUALNAME = "types.mtproto.MsgNewDetailedInfo"

    def __init__(
        self,
        *,
        answer_msg_id: int,
        bytes: int,
        status: int,
    ) -> None:
        self.answer_msg_id = answer_msg_id
        self.bytes = bytes
        self.status = status

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_MsgNewDetailedInfo.pack(self.answer_msg_id, self.bytes, self.status))
        except struct.error:
            w.write_long(self.answer_msg_id)
            w.write_int(self.bytes)
            w.write_int(self.status)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        answer_msg_id = r.read_long()
        bytes = r.read_int()
        status = r.read_int()
        self = cls.__new__(cls)
        self.answer_msg_id = answer_msg_id
        self.bytes = bytes
        self.status = status
        return self


class MsgResendReq(TLObject):
    """The TL type msg_resend_req#7d861a08, a form of MsgResendReq."""

    __slots__ = ("msg_ids",)

    ID = 0x7D861A08
    QUALNAME = "types.mtproto.MsgResendReq"

    def __init__(
        self,
        *,
        msg_ids: list[int],
    ) -> None:
        self.msg_ids = msg_ids

    def write_body(self, w: TLWriter) -> None:
        w.write_vector(self.msg_ids, TLWriter.write_long)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_ids = r.read_vector(TLReader.read_long)
        self = cls.__new__(cls)
        self.msg_ids = msg_ids
        return self


class RpcError(TLObject):
    """The TL type rpc_error#2144ca19, a form of RpcError."""

    __slots__ = ("error_code", "error_message",)

    ID = 0x2144CA19
    QUALNAME = "types.mtproto.RpcError"

    def __init__(
        self,
        *,
        error_code: int,
        error_message: str,
    ) -> None:
        self.error_code = error_code
        self.error_message = error_message

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.error_code)
        w.write_string(self.error_message)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        error_code = r.read_int()
        error_message = r.read_string()
        self = cls.__new__(cls)
        self.error_code = error_code
        self.error_message = error_message
        return self


class RpcAnswerUnknown(TLObject):
    """The TL type rpc_answer_unknown#5e2ad36e, a form of RpcDropAnswer."""

    __slots__ = ()

    ID = 0x5E2AD36E
    QUALNAME = "types.mtproto.RpcAnswerUnknown"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


class RpcAnswerDroppedRunning(TLObject):
    """The TL type rpc_answer_dropped_running#cd78e586, a form of RpcDropAnswer."""

    __slots__ = ()

    ID = 0xCD78E586
    QUALNAME = "types.mtproto.RpcAnswerDroppedRunning"

    def write_body(self, w: TLWriter) -> None:
        pass

    @classmethod
    def read(cls, r: TLReader) -> Self:
        self = cls.__new__(cls)
        return self


_PACK_RpcAnswerDropped = struct.Struct("<qii")


class RpcAnswerDropped(TLObject):
    """The TL type rpc_answer_dropped#a43ad8b7, a form of RpcDropAnswer."""

    __slots__ = ("msg_id", "seq_no", "bytes",)

    ID = 0xA43AD8B7
    QUALNAME = "types.mtproto.RpcAnswerDropped"

    def __init__(
        self,
        *,
        msg_id: int,
        seq_no: int,
        bytes: int,
    ) -> None:
        self.msg_id = msg_id
        self.seq_no = seq_no
        self.bytes = bytes

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_RpcAnswerDropped.pack(self.msg_id, self.seq_no, self.bytes))
        except struct.error:
            w.write_long(self.msg_id)
            w.write_int(self.seq_no)
            w.write_int(self.bytes)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_id = r.read_long()
        seq_no = r.read_int()
        bytes = r.read_int()
        self = cls.__new__(cls)
        self.msg_id = msg_id
        self.seq_no = seq_no
        self.bytes = bytes
        return self


_PACK_FutureSalt = struct.Struct("<iiq")


class FutureSalt(TLObject):
    """The TL type future_salt#0949d9dc, a form of FutureSalt."""

    __slots__ = ("valid_since", "valid_until", "salt",)

    ID = 0x0949D9DC
    QUALNAME = "types.mtproto.FutureSalt"

    def __init__(
        self,
        *,
        valid_since: int,
        valid_until: int,
        salt: int,
    ) -> None:
        self.valid_since = valid_since
        self.valid_until = valid_until
        self.salt = salt

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_FutureSalt.pack(self.valid_since, self.valid_until, self.salt))
        except struct.error:
            w.write_int(self.valid_since)
            w.write_int(self.valid_until)
            w.write_long(self.salt)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        valid_since = r.read_int()
        valid_until = r.read_int()
        salt = r.read_long()
        self = cls.__new__(cls)
        self.valid_since = valid_since
        self.valid_until = valid_until
        self.salt = salt
        return self


class FutureSalts(TLObject):
    """The TL type future_salts#ae500895, a form of FutureSalts."""

    __slots__ = ("req_msg_id", "now", "salts",)

    ID = 0xAE500895
    QUALNAME = "types.mtproto.FutureSalts"

    def __init__(
        self,
        *,
        req_msg_id: int,
        now: int,
        salts: list[FutureSalt],
    ) -> None:
        self.req_msg_id = req_msg_id
        self.now = now
        self.salts = salts

    def write_body(self, w: TLWriter) -> None:
        w.write_long(self.req_msg_id)
        w.write_int(self.now)
        w.write_vector(self.salts, lambda w, item: item.write_body(w), boxed=False)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        req_msg_id = r.read_long()
        now = r.read_int()
        salts = r.read_vector(FutureSalt.read, boxed=False)
        self = cls.__new__(cls)
        self.req_msg_id = req_msg_id
        self.now = now
        self.salts = salts
        return self


_PACK_Pong = struct.Struct("<qq")


class Pong(TLObject):
    """The TL type pong#347773c5, a form of Pong."""

    __slots__ = ("msg_id", "ping_id",)

    ID = 0x347773C5
    QUALNAME = "types.mtproto.Pong"

    def __init__(
        self,
        *,
        msg_id: int,
        ping_id: int,
    ) -> None:
        self.msg_id = msg_id
        self.ping_id = ping_id

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_Pong.pack(self.msg_id, self.ping_id))
        except struct.error:
            w.write_long(self.msg_id)
            w.write_long(self.ping_id)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        msg_id = r.read_long()
        ping_id = r.read_long()
        self = cls.__new__(cls)
        self.msg_id = msg_id
        self.ping_id = ping_id
        return self


class DestroySessionOk(TLObject):
    """The TL type destroy_session_ok#e22045fc, a form of DestroySessionRes."""

    __slots__ = ("session_id",)

    ID = 0xE22045FC
    QUALNAME = "types.mtproto.DestroySessionOk"

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


class DestroySessionNone(TLObject):
    """The TL type destroy_session_none#62d350c9, a form of DestroySessionRes."""

    __slots__ = ("session_id",)

    ID = 0x62D350C9
    QUALNAME = "types.mtproto.DestroySessionNone"

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


_PACK_NewSessionCreated = struct.Struct("<qqq")


class NewSessionCreated(TLObject):
    """The TL type new_session_created#9ec20908, a form of NewSession."""

    __slots__ = ("first_msg_id", "unique_id", "server_salt",)

    ID = 0x9EC20908
    QUALNAME = "types.mtproto.NewSessionCreated"

    def __init__(
        self,
        *,
        first_msg_id: int,
        unique_id: int,
        server_salt: int,
    ) -> None:
        self.first_msg_id = first_msg_id
        self.unique_id = unique_id
        self.server_salt = server_salt

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_NewSessionCreated.pack(self.first_msg_id, self.unique_id, self.server_salt))
        except struct.error:
            w.write_long(self.first_msg_id)
            w.write_long(self.unique_id)
            w.write_long(self.server_salt)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        first_msg_id = r.read_long()
        unique_id = r.read_long()
        server_salt = r.read_long()
        self = cls.__new__(cls)
        self.first_msg_id = first_msg_id
        self.unique_id = unique_id
        self.server_salt = server_salt
        return self


_PACK_HttpWait = struct.Struct("<iii")


class HttpWait(TLObject):
    """The TL type http_wait#9299359f, a form of HttpWait."""

    __slots__ = ("max_delay", "wait_after", "max_wait",)

    ID = 0x9299359F
    QUALNAME = "types.mtproto.HttpWait"

    def __init__(
        self,
        *,
        max_delay: int,
        wait_after: int,
        max_wait: int,
    ) -> None:
        self.max_delay = max_delay
        self.wait_after = wait_after
        self.max_wait = max_wait

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_HttpWait.pack(self.max_delay, self.wait_after, self.max_wait))
        except struct.error:
            w.write_int(self.max_delay)
            w.write_int(self.wait_after)
            w.write_int(self.max_wait)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        max_delay = r.read_int()
        wait_after = r.read_int()
        max_wait = r.read_int()
        self = cls.__new__(cls)
        self.max_delay = max_delay
        self.wait_after = wait_after
        self.max_wait = max_wait
        return self


_PACK_IpPort = struct.Struct("<ii")


class IpPort(TLObject):
    """The TL type ipPort#d433ad73, a form of IpPort."""

    __slots__ = ("ipv4", "port",)

    ID = 0xD433AD73
    QUALNAME = "types.mtproto.IpPort"

    def __init__(
        self,
        *,
        ipv4: int,
        port: int,
    ) -> None:
        self.ipv4 = ipv4
        self.port = port

    def write_body(self, w: TLWriter) -> None:
        try:
            w.write_raw(_PACK_IpPort.pack(self.ipv4, self.port))
        except struct.error:
            w.write_int(self.ipv4)
            w.write_int(self.port)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ipv4 = r.read_int()
        port = r.read_int()
        self = cls.__new__(cls)
        self.ipv4 = ipv4
        self.port = port
        return self


class IpPortSecret(TLObject):
    """The TL type ipPortSecret#37982646, a form of IpPort."""

    __slots__ = ("ipv4", "port", "secret",)

    ID = 0x37982646
    QUALNAME = "types.mtproto.IpPortSecret"

    def __init__(
        self,
        *,
        ipv4: int,
        port: int,
        secret: bytes,
    ) -> None:
        self.ipv4 = ipv4
        self.port = port
        self.secret = secret

    def write_body(self, w: TLWriter) -> None:
        w.write_int(self.ipv4)
        w.write_int(self.port)
        w.write_bytes(self.secret)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        ipv4 = r.read_int()
        port = r.read_int()
        secret = r.read_bytes()
        self = cls.__new__(cls)
        self.ipv4 = ipv4
        self.port = port
        self.secret = secret
        return self


class AccessPointRule(TLObject):
    """The TL type accessPointRule#4679b65f, a form of AccessPointRule."""

    __slots__ = ("phone_prefix_rules", "dc_id", "ips",)

    ID = 0x4679B65F
    QUALNAME = "types.mtproto.AccessPointRule"

    def __init__(
        self,
        *,
        phone_prefix_rules: bytes,
        dc_id: int,
        ips: list[base.IpPort],
    ) -> None:
        self.phone_prefix_rules = phone_prefix_rules
        self.dc_id = dc_id
        self.ips = ips

    def write_body(self, w: TLWriter) -> None:
        w.write_bytes(self.phone_prefix_rules)
        w.write_int(self.dc_id)
        w.write_vector(self.ips, boxed=False)

    @classmethod
    def read(cls, r: TLReader) -> Self:
        phone_prefix_rules = r.read_bytes()
        dc_id = r.read_int()
        ips = r.read_vector(boxed=False)
        self = cls.__new__(cls)
        self.phone_prefix_rules = phone_prefix_rules
        self.dc_id = dc_id
        self.ips = ips
        return self
