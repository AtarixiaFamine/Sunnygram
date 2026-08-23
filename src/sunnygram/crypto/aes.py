# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""AES, plus the two modes MTProto uses, in plain Python.

IGE wraps every encrypted MTProto message, and CTR carries CDN file chunks and
the obfuscated transport. Both are built on the AES class here, which uses the
usual four table formulation so a round costs sixteen lookups instead of a
bit-level MixColumns.

This is the implementation that is always present, and the one every faster
backend is checked against. Which of them actually runs is accel.py's decision:
this module has no opinion about it and no knowledge of it, so the reference
stays a reference.

The tables are derived at import from the AES polynomial instead of pasted in,
which keeps them auditable. Deriving them costs a couple of milliseconds, once.
"""

from __future__ import annotations

import struct

__all__ = [
    "AES",
    "CTR",
    "check_ige",
    "ige256_decrypt_python",
    "ige256_encrypt_python",
]

_MASK32 = 0xFFFFFFFF
_MASK128 = (1 << 128) - 1


def _log_tables() -> tuple[list[int], list[int]]:
    """Discrete logs in GF(2^8), which reduce multiplication to a lookup."""
    log = [0] * 256
    alog = [0] * 256
    x = 1
    for i in range(255):
        alog[i] = x
        log[x] = i
        # Step to the next power of the generator 3, spelled out because the
        # multiplication table being built here does not exist yet.
        doubled = (x << 1) & 0xFF
        if x & 0x80:
            doubled ^= 0x1B
        x = doubled ^ x
    return log, alog


_LOG, _ALOG = _log_tables()


def _mul(a: int, b: int) -> int:
    """Multiply two bytes in GF(2^8) modulo the AES polynomial."""
    if a == 0 or b == 0:
        return 0
    return _ALOG[(_LOG[a] + _LOG[b]) % 255]


def _build_sboxes() -> tuple[list[int], list[int]]:
    # The S-box is the multiplicative inverse followed by an affine step.
    sbox = [0] * 256
    for a in range(256):
        inverse = 0 if a == 0 else _ALOG[(255 - _LOG[a]) % 255]
        value = inverse
        rotated = inverse
        for _ in range(4):
            rotated = ((rotated << 1) | (rotated >> 7)) & 0xFF
            value ^= rotated
        sbox[a] = value ^ 0x63

    inv_sbox = [0] * 256
    for a, s in enumerate(sbox):
        inv_sbox[s] = a
    return sbox, inv_sbox


def _build_tables(
    sbox: list[int], inv_sbox: list[int]
) -> tuple[list[list[int]], list[list[int]]]:
    # te[n] folds SubBytes, ShiftRows and MixColumns into one word per input
    # byte; td[n] does the same for the inverse cipher. Each table is the
    # previous one rotated right by a byte.
    te = [[0] * 256 for _ in range(4)]
    td = [[0] * 256 for _ in range(4)]
    for x in range(256):
        s = sbox[x]
        word = (_mul(s, 2) << 24) | (s << 16) | (s << 8) | _mul(s, 3)
        for n in range(4):
            te[n][x] = word
            word = ((word >> 8) | (word << 24)) & _MASK32

        s = inv_sbox[x]
        word = (
            (_mul(s, 14) << 24) | (_mul(s, 9) << 16) | (_mul(s, 13) << 8) | _mul(s, 11)
        )
        for n in range(4):
            td[n][x] = word
            word = ((word >> 8) | (word << 24)) & _MASK32
    return te, td


_SBOX, _INV_SBOX = _build_sboxes()
_TE, _TD = _build_tables(_SBOX, _INV_SBOX)
_TE0, _TE1, _TE2, _TE3 = _TE
_TD0, _TD1, _TD2, _TD3 = _TD


def _sub_word(word: int) -> int:
    return (
        (_SBOX[(word >> 24) & 0xFF] << 24)
        | (_SBOX[(word >> 16) & 0xFF] << 16)
        | (_SBOX[(word >> 8) & 0xFF] << 8)
        | _SBOX[word & 0xFF]
    )


def _inv_mix_column(word: int) -> int:
    a = (word >> 24) & 0xFF
    b = (word >> 16) & 0xFF
    c = (word >> 8) & 0xFF
    d = word & 0xFF
    return (
        ((_mul(a, 14) ^ _mul(b, 11) ^ _mul(c, 13) ^ _mul(d, 9)) << 24)
        | ((_mul(a, 9) ^ _mul(b, 14) ^ _mul(c, 11) ^ _mul(d, 13)) << 16)
        | ((_mul(a, 13) ^ _mul(b, 9) ^ _mul(c, 14) ^ _mul(d, 11)) << 8)
        | (_mul(a, 11) ^ _mul(b, 13) ^ _mul(c, 9) ^ _mul(d, 14))
    )


def _expand_key(key: bytes) -> tuple[list[int], int]:
    words = len(key) // 4
    rounds = words + 6
    schedule = list(struct.unpack(f">{words}I", key))
    rcon = 1
    for i in range(words, 4 * (rounds + 1)):
        temp = schedule[i - 1]
        if i % words == 0:
            temp = ((temp << 8) | (temp >> 24)) & _MASK32
            temp = _sub_word(temp) ^ (rcon << 24)
            rcon = _mul(rcon, 2)
        elif words > 6 and i % words == 4:
            temp = _sub_word(temp)
        schedule.append(schedule[i - words] ^ temp)
    return schedule, rounds


def _invert_key(schedule: list[int], rounds: int) -> list[int]:
    # The equivalent inverse cipher: round keys in reverse order, with the
    # inverse MixColumns applied to every one but the first and the last.
    inverted = list(schedule)
    low, high = 0, 4 * rounds
    while low < high:
        inverted[low : low + 4], inverted[high : high + 4] = (
            inverted[high : high + 4],
            inverted[low : low + 4],
        )
        low += 4
        high -= 4
    for r in range(1, rounds):
        base = 4 * r
        for k in range(base, base + 4):
            inverted[k] = _inv_mix_column(inverted[k])
    return inverted


class AES:
    """A single AES key, expanded once and reusable for either direction.

    Key setup is the expensive part, so build one of these per key and keep it
    for the life of the session rather than per message.
    """

    __slots__ = ("_encrypt_key", "_decrypt_key", "_rounds")

    _decrypt_key: list[int] | None

    def __init__(self, key: bytes) -> None:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"AES key must be 16, 24 or 32 bytes, got {len(key)}")
        self._encrypt_key, self._rounds = _expand_key(key)
        # The inverse schedule costs about as much again to build, and a given
        # MTProto message only ever travels one way, so wait until it is asked
        # for.
        self._decrypt_key = None

    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != 16:
            raise ValueError(f"AES block must be 16 bytes, got {len(block)}")
        rk = self._encrypt_key
        s0, s1, s2, s3 = struct.unpack(">4I", block)
        s0 ^= rk[0]
        s1 ^= rk[1]
        s2 ^= rk[2]
        s3 ^= rk[3]

        offset = 4
        for _ in range(self._rounds - 1):
            s0, s1, s2, s3 = (
                _TE0[s0 >> 24]
                ^ _TE1[(s1 >> 16) & 0xFF]
                ^ _TE2[(s2 >> 8) & 0xFF]
                ^ _TE3[s3 & 0xFF]
                ^ rk[offset],
                _TE0[s1 >> 24]
                ^ _TE1[(s2 >> 16) & 0xFF]
                ^ _TE2[(s3 >> 8) & 0xFF]
                ^ _TE3[s0 & 0xFF]
                ^ rk[offset + 1],
                _TE0[s2 >> 24]
                ^ _TE1[(s3 >> 16) & 0xFF]
                ^ _TE2[(s0 >> 8) & 0xFF]
                ^ _TE3[s1 & 0xFF]
                ^ rk[offset + 2],
                _TE0[s3 >> 24]
                ^ _TE1[(s0 >> 16) & 0xFF]
                ^ _TE2[(s1 >> 8) & 0xFF]
                ^ _TE3[s2 & 0xFF]
                ^ rk[offset + 3],
            )
            offset += 4

        # The last round drops MixColumns, so it reads the plain S-box.
        return struct.pack(
            ">4I",
            (
                (_SBOX[s0 >> 24] << 24)
                | (_SBOX[(s1 >> 16) & 0xFF] << 16)
                | (_SBOX[(s2 >> 8) & 0xFF] << 8)
                | _SBOX[s3 & 0xFF]
            )
            ^ rk[offset],
            (
                (_SBOX[s1 >> 24] << 24)
                | (_SBOX[(s2 >> 16) & 0xFF] << 16)
                | (_SBOX[(s3 >> 8) & 0xFF] << 8)
                | _SBOX[s0 & 0xFF]
            )
            ^ rk[offset + 1],
            (
                (_SBOX[s2 >> 24] << 24)
                | (_SBOX[(s3 >> 16) & 0xFF] << 16)
                | (_SBOX[(s0 >> 8) & 0xFF] << 8)
                | _SBOX[s1 & 0xFF]
            )
            ^ rk[offset + 2],
            (
                (_SBOX[s3 >> 24] << 24)
                | (_SBOX[(s0 >> 16) & 0xFF] << 16)
                | (_SBOX[(s1 >> 8) & 0xFF] << 8)
                | _SBOX[s2 & 0xFF]
            )
            ^ rk[offset + 3],
        )

    def decrypt_block(self, block: bytes) -> bytes:
        if len(block) != 16:
            raise ValueError(f"AES block must be 16 bytes, got {len(block)}")
        rk = self._decrypt_key
        if rk is None:
            rk = self._decrypt_key = _invert_key(self._encrypt_key, self._rounds)
        s0, s1, s2, s3 = struct.unpack(">4I", block)
        s0 ^= rk[0]
        s1 ^= rk[1]
        s2 ^= rk[2]
        s3 ^= rk[3]

        offset = 4
        for _ in range(self._rounds - 1):
            s0, s1, s2, s3 = (
                _TD0[s0 >> 24]
                ^ _TD1[(s3 >> 16) & 0xFF]
                ^ _TD2[(s2 >> 8) & 0xFF]
                ^ _TD3[s1 & 0xFF]
                ^ rk[offset],
                _TD0[s1 >> 24]
                ^ _TD1[(s0 >> 16) & 0xFF]
                ^ _TD2[(s3 >> 8) & 0xFF]
                ^ _TD3[s2 & 0xFF]
                ^ rk[offset + 1],
                _TD0[s2 >> 24]
                ^ _TD1[(s1 >> 16) & 0xFF]
                ^ _TD2[(s0 >> 8) & 0xFF]
                ^ _TD3[s3 & 0xFF]
                ^ rk[offset + 2],
                _TD0[s3 >> 24]
                ^ _TD1[(s2 >> 16) & 0xFF]
                ^ _TD2[(s1 >> 8) & 0xFF]
                ^ _TD3[s0 & 0xFF]
                ^ rk[offset + 3],
            )
            offset += 4

        return struct.pack(
            ">4I",
            (
                (_INV_SBOX[s0 >> 24] << 24)
                | (_INV_SBOX[(s3 >> 16) & 0xFF] << 16)
                | (_INV_SBOX[(s2 >> 8) & 0xFF] << 8)
                | _INV_SBOX[s1 & 0xFF]
            )
            ^ rk[offset],
            (
                (_INV_SBOX[s1 >> 24] << 24)
                | (_INV_SBOX[(s0 >> 16) & 0xFF] << 16)
                | (_INV_SBOX[(s3 >> 8) & 0xFF] << 8)
                | _INV_SBOX[s2 & 0xFF]
            )
            ^ rk[offset + 1],
            (
                (_INV_SBOX[s2 >> 24] << 24)
                | (_INV_SBOX[(s1 >> 16) & 0xFF] << 16)
                | (_INV_SBOX[(s0 >> 8) & 0xFF] << 8)
                | _INV_SBOX[s3 & 0xFF]
            )
            ^ rk[offset + 2],
            (
                (_INV_SBOX[s3 >> 24] << 24)
                | (_INV_SBOX[(s2 >> 16) & 0xFF] << 16)
                | (_INV_SBOX[(s1 >> 8) & 0xFF] << 8)
                | _INV_SBOX[s0 & 0xFF]
            )
            ^ rk[offset + 3],
        )


def check_ige(data: bytes, key: bytes, iv: bytes) -> None:
    """Refuse the arguments no IGE implementation could honour.

    Public because every backend has to make the same three checks, and making
    them in one place is what keeps a fast one from being lenient where this is
    strict.
    """
    if len(key) != 32:
        raise ValueError(f"IGE-256 key must be 32 bytes, got {len(key)}")
    if len(iv) != 32:
        raise ValueError(f"IGE-256 iv must be 32 bytes, got {len(iv)}")
    if len(data) % 16:
        raise ValueError(f"IGE works on whole blocks, got {len(data)} bytes")


def ige256_encrypt_python(data: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypt whole blocks with AES-256-IGE, in plain Python.

    The first half of the iv stands in for the previous ciphertext block and
    the second half for the previous plaintext block.
    """
    check_ige(data, key, iv)
    cipher = AES(key)
    previous_cipher = int.from_bytes(iv[:16], "big")
    previous_plain = int.from_bytes(iv[16:], "big")
    out = bytearray()
    for offset in range(0, len(data), 16):
        plain = int.from_bytes(data[offset : offset + 16], "big")
        encrypted = cipher.encrypt_block(
            (plain ^ previous_cipher).to_bytes(16, "big")
        )
        current = int.from_bytes(encrypted, "big") ^ previous_plain
        out += current.to_bytes(16, "big")
        previous_cipher = current
        previous_plain = plain
    return bytes(out)


def ige256_decrypt_python(data: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt whole blocks with AES-256-IGE, in plain Python.

    The iv halves keep the same meaning as when encrypting.
    """
    check_ige(data, key, iv)
    cipher = AES(key)
    previous_cipher = int.from_bytes(iv[:16], "big")
    previous_plain = int.from_bytes(iv[16:], "big")
    out = bytearray()
    for offset in range(0, len(data), 16):
        current = int.from_bytes(data[offset : offset + 16], "big")
        decrypted = cipher.decrypt_block(
            (current ^ previous_plain).to_bytes(16, "big")
        )
        plain = int.from_bytes(decrypted, "big") ^ previous_cipher
        out += plain.to_bytes(16, "big")
        previous_cipher = current
        previous_plain = plain
    return bytes(out)


class CTR:
    """AES in counter mode over a sixteen byte big-endian counter.

    Telegram uses this as a stream, so one instance covers a whole transfer or
    a whole connection: a call that ends part way through a keystream block
    resumes there on the next call. Counter mode is symmetric, so encrypt and
    decrypt are the same operation.
    """

    __slots__ = ("_aes", "_counter", "_block", "_offset")

    def __init__(self, key: bytes, iv: bytes) -> None:
        if len(iv) != 16:
            raise ValueError(f"CTR iv must be 16 bytes, got {len(iv)}")
        self._aes = AES(key)
        self._counter = int.from_bytes(iv, "big")
        self._block = b""
        # 16 means the current block is used up, so the next call refills.
        self._offset = 16

    def apply(self, data: bytes) -> bytes:
        if not data:
            return b""
        stream = bytearray(self._block[self._offset :])
        while len(stream) < len(data):
            self._block = self._aes.encrypt_block(self._counter.to_bytes(16, "big"))
            self._counter = (self._counter + 1) & _MASK128
            stream += self._block
        leftover = len(stream) - len(data)
        self._offset = 16 - leftover
        # One integer for the buffer and one for the keystream, however big the
        # buffer is. That reads like something to chunk and it is not: each of
        # from_bytes, ^ and to_bytes is a single C loop, so a 512 KiB part
        # spends 6 ms here against 2.27 s making the keystream above, and
        # chunking it at 8 KiB measured no faster. See ARCHITECTURE.md,
        # considered and not done.
        keystream = int.from_bytes(stream[: len(data)], "big")
        return (int.from_bytes(data, "big") ^ keystream).to_bytes(len(data), "big")

    encrypt = apply
    decrypt = apply
