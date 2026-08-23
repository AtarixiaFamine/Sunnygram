# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Running the authorization key exchange over a live connection.

Three round trips, all of them unencrypted because there is no key yet. We ask
for a proof-of-work puzzle, answer it inside a block only the server can open,
and finish a Diffie-Hellman exchange whose result becomes the auth key.

Every value the server sends back is checked against what we sent: the nonces
tie the three round trips into one conversation, and the final hash proves the
server derived the same key we did. A mismatch anywhere is fatal, because the
only thing it can mean is that something is sitting in the middle.

The arithmetic lives in sunnygram.crypto. This module is the conversation.
"""

from __future__ import annotations

import asyncio
import secrets
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from ..crypto import (
    PublicKey,
    check_dh_parameters,
    derive_auth_key,
    generate_b,
    ige256_decrypt,
    ige256_encrypt,
    factorize,
    new_nonce_hash,
    rsa_pad,
    select_key,
    server_salt,
    temp_key_iv,
    unwrap_answer,
    wrap_client_data,
)
from ..errors import SecurityError
from ..raw import functions, types
from ..session import MessageIdGenerator, pack_plaintext, unpack_plaintext
from ..tl import TLObject, TLReader
from ..utils import signed

__all__ = ["AuthKey", "Wire", "create_auth_key"]


@dataclass(frozen=True, slots=True)
class AuthKey:
    """What a finished handshake leaves behind."""

    key: bytes
    salt: int
    # How far ahead of us the server's clock runs, so message ids line up.
    time_offset: float


class Wire(Protocol):
    """The two things the handshake needs from a transport.

    Narrow on purpose: the handshake predates any session, so it wants framed
    payloads and nothing else. A TCPTransport satisfies this, and so does
    anything standing in for one.
    """

    async def send(self, payload: bytes) -> None: ...
    async def receive(self) -> bytes: ...


def _big_endian(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")


def _dh_exchange(g: int, dh_prime: bytes, g_a: bytes) -> tuple[int, bytes]:
    """Our half of the exchange, and the shared key.

    All the 2048-bit arithmetic in one place, including the primality test,
    because this is the part that has to run off the event loop (rule P1). The
    secret exponent never leaves this function.
    """
    prime = int.from_bytes(dh_prime, "big")
    theirs = int.from_bytes(g_a, "big")
    b = generate_b()
    ours = pow(g, b, prime)
    # Checked before the shared secret is derived from any of it, and our own
    # half is held to the same standard as theirs.
    check_dh_parameters(g, prime, theirs, ours)
    return ours, derive_auth_key(theirs, b, prime)


async def create_auth_key(
    wire: Wire,
    *,
    dc_id: int,
    test: bool = False,
    keys: Sequence[PublicKey] | None = None,
) -> AuthKey:
    """Negotiate an authorization key with one datacenter.

    keys says which server keys are acceptable, and is how a CDN datacenter is
    reached: it is named by a key that arrives in help.getCdnConfig rather than
    by either of the built-in ones, and accepting a built-in one there would be
    accepting a server that is not the one asked for.
    """
    ids = MessageIdGenerator()

    async def call(request: TLObject) -> Any:
        await wire.send(pack_plaintext(ids.next(), request.to_bytes()))
        _, body = unpack_plaintext(await wire.receive())
        return TLReader(body).read_object()

    nonce = signed(secrets.randbits(128), 128)
    res_pq = await call(functions.mtproto.ReqPqMulti(nonce=nonce))
    if not isinstance(res_pq, types.mtproto.ResPQ):
        raise SecurityError(f"expected resPQ, got {type(res_pq).__name__}")
    if res_pq.nonce != nonce:
        raise SecurityError("the server answered resPQ with a different nonce")
    server_nonce = res_pq.server_nonce

    key = select_key(res_pq.server_public_key_fingerprints, test=test, keys=keys)
    p, q = factorize(int.from_bytes(res_pq.pq, "big"))
    new_nonce = signed(secrets.randbits(256), 256)
    inner = types.mtproto.PQInnerDataDc(
        pq=res_pq.pq,
        p=_big_endian(p),
        q=_big_endian(q),
        nonce=nonce,
        server_nonce=server_nonce,
        new_nonce=new_nonce,
        dc=dc_id,
    )
    params = await call(
        functions.mtproto.ReqDHParams(
            nonce=nonce,
            server_nonce=server_nonce,
            p=_big_endian(p),
            q=_big_endian(q),
            public_key_fingerprint=key.fingerprint,
            encrypted_data=rsa_pad(inner.to_bytes(), key),
        )
    )
    if isinstance(params, types.mtproto.ServerDHParamsFail):
        raise SecurityError("the server rejected our answer to the puzzle")
    if not isinstance(params, types.mtproto.ServerDHParamsOk):
        raise SecurityError(f"expected server_DH_params, got {type(params).__name__}")
    if params.nonce != nonce or params.server_nonce != server_nonce:
        raise SecurityError("the server changed nonces between round trips")

    temp_key, temp_iv = temp_key_iv(server_nonce, new_nonce)
    answer = unwrap_answer(
        ige256_decrypt(params.encrypted_answer, temp_key, temp_iv)
    )
    inner_data = TLReader(answer).read_object()
    if not isinstance(inner_data, types.mtproto.ServerDHInnerData):
        raise SecurityError(
            f"expected server_DH_inner_data, got {type(inner_data).__name__}"
        )
    if inner_data.nonce != nonce or inner_data.server_nonce != server_nonce:
        raise SecurityError("the encrypted answer carries the wrong nonces")

    g_b, auth_key = await asyncio.to_thread(
        _dh_exchange, inner_data.g, inner_data.dh_prime, inner_data.g_a
    )

    client_data = types.mtproto.ClientDHInnerData(
        nonce=nonce,
        server_nonce=server_nonce,
        retry_id=0,
        g_b=_big_endian(g_b),
    )
    generated = await call(
        functions.mtproto.SetClientDHParams(
            nonce=nonce,
            server_nonce=server_nonce,
            encrypted_data=ige256_encrypt(
                wrap_client_data(client_data.to_bytes()), temp_key, temp_iv
            ),
        )
    )
    if isinstance(generated, types.mtproto.DhGenRetry):
        raise SecurityError("the server asked to retry the exchange")
    if isinstance(generated, types.mtproto.DhGenFail):
        raise SecurityError("the server could not agree on a key")
    if not isinstance(generated, types.mtproto.DhGenOk):
        raise SecurityError(
            f"expected a dh_gen answer, got {type(generated).__name__}"
        )
    if generated.nonce != nonce or generated.server_nonce != server_nonce:
        raise SecurityError("the final answer carries the wrong nonces")
    # Proof that the server arrived at the same key. Without this the exchange
    # could have been completed with someone else.
    if generated.new_nonce_hash1 != new_nonce_hash(new_nonce, auth_key, 1):
        raise SecurityError("the server derived a different key")

    return AuthKey(
        key=auth_key,
        salt=server_salt(new_nonce, server_nonce),
        time_offset=inner_data.server_time - time.time(),
    )
