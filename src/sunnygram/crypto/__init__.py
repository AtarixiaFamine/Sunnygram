# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The cryptography MTProto needs.

Small, finite, and validated against known vectors. Treat it as frozen: no
refactor lands here without the vector tests passing.
"""

from __future__ import annotations

from .accel import (
    BACKEND,
    CTR_BACKEND,
    OFFLOAD_ABOVE,
    StreamCipher,
    describe,
    ige256_decrypt,
    ige256_encrypt,
    new_ctr,
    off_loop,
)
from .aes import (
    AES,
    CTR,
    check_ige,
    ige256_decrypt_python,
    ige256_encrypt_python,
)
from .auth_key import (
    DH_PRIME_BITS,
    MAX_INNER_DATA,
    check_dh_parameters,
    derive_auth_key,
    generate_b,
    new_nonce_hash,
    pad_block,
    rsa_pad,
    server_salt,
    temp_key_iv,
    unwrap_answer,
    wrap_client_data,
)
from .factorization import factorize
from .mtproto import (
    AUTH_KEY_SIZE,
    auth_key_id,
    compute_msg_key,
    derive_key_iv,
    verify_msg_key,
)
from .rsa import PRODUCTION_KEYS, TEST_KEYS, PublicKey, select_key
from .srp import SRPParameters, SRPProof, password_hash, srp_proof

__all__ = [
    "AES",
    "AUTH_KEY_SIZE",
    "BACKEND",
    "CTR",
    "CTR_BACKEND",
    "OFFLOAD_ABOVE",
    "StreamCipher",
    "DH_PRIME_BITS",
    "MAX_INNER_DATA",
    "PRODUCTION_KEYS",
    "PublicKey",
    "SRPParameters",
    "SRPProof",
    "TEST_KEYS",
    "auth_key_id",
    "check_dh_parameters",
    "check_ige",
    "compute_msg_key",
    "derive_auth_key",
    "derive_key_iv",
    "describe",
    "factorize",
    "new_ctr",
    "off_loop",
    "generate_b",
    "new_nonce_hash",
    "pad_block",
    "password_hash",
    "rsa_pad",
    "server_salt",
    "temp_key_iv",
    "unwrap_answer",
    "wrap_client_data",
    "ige256_decrypt",
    "ige256_decrypt_python",
    "ige256_encrypt",
    "ige256_encrypt_python",
    "select_key",
    "srp_proof",
    "verify_msg_key",
]
