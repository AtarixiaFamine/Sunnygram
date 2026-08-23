# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Choosing the fastest AES this machine has, and keeping it off the event loop.

AES-IGE wraps every MTProto message and AES-CTR carries CDN chunks, so between
them they are the hot path of the whole library. The implementation in aes.py is
pure Python and always present, which lets Sunnygram install with no
dependencies at all. It is also, unavoidably, about a thousand times slower than
the same cipher in C, and that is the difference between a file transfer and a
frozen program.

So there is a ladder. Four rungs for IGE, and whichever is highest gets used:

1. cryptg, the Rust one, the fastest and the one the speedups extra installs.
2. tgcrypto, the C one, for anybody who already has it from another library.
3. cryptography, which nearly every Python environment already has for other
   reasons. It has no IGE, so this drives its AES a block at a time: each block
   is still an OpenSSL call instead of a hundred Python operations, which is
   most of the win for none of the install.
4. The pure Python cipher, which always works.

Nothing here changes what the cipher computes. Every rung is checked against the
pure Python one over random data in the test suite, because a fast backend that
is subtly wrong would corrupt a session instead of fail it (rule S1).

The second job of this module is rule P1. A cipher call is CPU-bound and
synchronous, so a large one blocks the loop: on the pure Python rung a single
512 KiB file part is roughly three seconds during which nothing else in the
program runs, not a ping, not a read, not another task. Anything past a
threshold therefore goes to a worker thread. With a native backend that thread
really does run in parallel, since the extension releases the GIL; with the pure
Python one it at least interleaves, which turns a freeze into a slowdown.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Protocol, TypeVar

from .aes import (
    CTR,
    check_ige,
    ige256_decrypt_python,
    ige256_encrypt_python,
)

__all__ = [
    "BACKEND",
    "CTR_BACKEND",
    "OFFLOAD_ABOVE",
    "StreamCipher",
    "describe",
    "ige256_decrypt",
    "ige256_encrypt",
    "new_ctr",
    "off_loop",
]

_R = TypeVar("_R")

IgeFunc = Callable[[bytes, bytes, bytes], bytes]


class StreamCipher(Protocol):
    """What the transport and the file engine need from a CTR cipher.

    One instance covers a whole transfer: a call that ends part way through a
    keystream block resumes there on the next one.
    """

    def apply(self, data: bytes) -> bytes: ...


CTRFactory = Callable[[bytes, bytes], StreamCipher]


def _from_cryptg() -> tuple[str, IgeFunc, IgeFunc] | None:
    try:
        import cryptg
    except ImportError:
        return None
    return "cryptg", cryptg.encrypt_ige, cryptg.decrypt_ige


def _from_tgcrypto() -> tuple[str, IgeFunc, IgeFunc] | None:
    try:
        import tgcrypto
    except ImportError:
        return None
    return "tgcrypto", tgcrypto.ige256_encrypt, tgcrypto.ige256_decrypt


def _from_cryptography() -> tuple[str, IgeFunc, IgeFunc] | None:
    """IGE built out of OpenSSL's AES, one block at a time.

    IGE chains both the ciphertext and the plaintext into the next block, so
    unlike CTR there is no way to hand the whole buffer over at once. What is
    left is still worth having: the sixteen table lookups and the key schedule
    move into C, and only the two chaining xors stay in Python.
    """
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        return None

    def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        check_ige(data, key, iv)
        block = Cipher(algorithms.AES(key), modes.ECB()).encryptor().update
        previous_cipher = int.from_bytes(iv[:16], "big")
        previous_plain = int.from_bytes(iv[16:], "big")
        out = bytearray()
        for offset in range(0, len(data), 16):
            plain = int.from_bytes(data[offset : offset + 16], "big")
            encrypted = block((plain ^ previous_cipher).to_bytes(16, "big"))
            current = int.from_bytes(encrypted, "big") ^ previous_plain
            out += current.to_bytes(16, "big")
            previous_cipher = current
            previous_plain = plain
        return bytes(out)

    def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        check_ige(data, key, iv)
        block = Cipher(algorithms.AES(key), modes.ECB()).decryptor().update
        previous_cipher = int.from_bytes(iv[:16], "big")
        previous_plain = int.from_bytes(iv[16:], "big")
        out = bytearray()
        for offset in range(0, len(data), 16):
            current = int.from_bytes(data[offset : offset + 16], "big")
            decrypted = block((current ^ previous_plain).to_bytes(16, "big"))
            plain = int.from_bytes(decrypted, "big") ^ previous_cipher
            out += plain.to_bytes(16, "big")
            previous_cipher = current
            previous_plain = plain
        return bytes(out)

    return "cryptography", encrypt, decrypt


def _select_ige() -> tuple[str, IgeFunc, IgeFunc]:
    for probe in (_from_cryptg, _from_tgcrypto, _from_cryptography):
        found = probe()
        if found is not None:
            return found
    return "python", ige256_encrypt_python, ige256_decrypt_python


def _select_ctr() -> tuple[str, CTRFactory]:
    """The counter mode cipher, which has only two rungs.

    CTR is a plain keystream, so OpenSSL takes the whole buffer in one call and
    the win is the full one, not IGE's partial one. The two Telegram
    extensions are left out here on purpose: both spell their streaming CTR
    differently and neither is worth guessing at, since a wrong guess is a
    corrupted download instead of an error.
    """
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        return "python", CTR

    class OpenSSLCTR:
        """The same interface as the pure Python CTR, over one OpenSSL context."""

        __slots__ = ("_update",)

        def __init__(self, key: bytes, iv: bytes) -> None:
            if len(iv) != 16:
                raise ValueError(f"CTR iv must be 16 bytes, got {len(iv)}")
            self._update = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor().update

        def apply(self, data: bytes) -> bytes:
            if not data:
                return b""
            applied: bytes = self._update(data)
            return applied

        encrypt = apply
        decrypt = apply

    return "cryptography", OpenSSLCTR


BACKEND, _ige_encrypt, _ige_decrypt = _select_ige()
CTR_BACKEND, new_ctr = _select_ctr()

# Where a cipher call stops being cheap enough to do on the loop. The pure
# Python rung runs at roughly 160 KiB/s, so a kilobyte is already several
# milliseconds and worth the thread; a native one is a thousand times quicker,
# so the hop only pays off around the size of a file part.
OFFLOAD_ABOVE = 1024 if BACKEND == "python" else 64 * 1024


def ige256_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypt whole blocks with AES-256-IGE, on the fastest rung present."""
    return _ige_encrypt(data, key, iv)


def ige256_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt whole blocks with AES-256-IGE, on the fastest rung present."""
    return _ige_decrypt(data, key, iv)


async def off_loop(size: int, work: Callable[..., _R], *args: Any) -> _R:
    """Run a cipher-bound call, in a thread if it is big enough to be worth it.

    size is what the call is about to chew through. Below the threshold the
    hand-off costs more than the work, so the call happens right here.
    """
    if size < OFFLOAD_ABOVE:
        return work(*args)
    return await asyncio.to_thread(work, *args)


def describe() -> str:
    """One line saying which ciphers are in use, for a diagnostic or a bug report.

    Worth printing when a transfer is slower than it should be: the answer is
    almost always that this says python.
    """
    if BACKEND == CTR_BACKEND:
        return f"AES: {BACKEND}"
    return f"AES: {BACKEND} for IGE, {CTR_BACKEND} for CTR"
