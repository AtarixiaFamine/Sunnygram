"""The ladder of AES backends, and keeping a big one off the event loop.

The point of a faster backend is that it computes exactly what the slow one
computes. So the tests that matter here are the ones that run whichever rungs
this machine has against the pure Python reference over random data: a backend
that is subtly wrong would corrupt a session rather than fail it (rule S1).

The rest is about rule P1. A cipher call is synchronous, and a big one on the
pure Python rung takes seconds, so it has to be able to leave the loop.
"""

from __future__ import annotations

import asyncio
import os
import threading

import pytest

from sunnygram.crypto import (
    BACKEND,
    CTR,
    CTR_BACKEND,
    OFFLOAD_ABOVE,
    describe,
    ige256_decrypt,
    ige256_decrypt_python,
    ige256_encrypt,
    ige256_encrypt_python,
    new_ctr,
    off_loop,
)
from sunnygram.crypto.accel import (
    _from_cryptg,
    _from_cryptography,
    _from_tgcrypto,
    _select_ctr,
)

KEY = bytes(range(32))
IGE_IV = bytes(range(32, 64))
CTR_IV = bytes(range(16))


def available():
    """Every IGE backend this machine actually has, named."""
    found = [("python", ige256_encrypt_python, ige256_decrypt_python)]
    for probe in (_from_cryptg, _from_tgcrypto, _from_cryptography):
        rung = probe()
        if rung is not None:
            found.append(rung)
    return found


class TestTheLadder:
    def test_the_chosen_rung_is_the_highest_one_present(self):
        names = [name for name, _, _ in available()]
        for better in ("cryptg", "tgcrypto", "cryptography"):
            if better in names:
                assert BACKEND == better
                return
        assert BACKEND == "python"

    def test_there_is_always_a_rung(self):
        assert BACKEND in ("cryptg", "tgcrypto", "cryptography", "python")
        assert CTR_BACKEND in ("cryptography", "python")

    def test_what_is_in_use_can_be_said_out_loud(self):
        said = describe()
        assert BACKEND in said
        assert CTR_BACKEND in said

    @pytest.mark.parametrize("size", [16, 64, 1024, 4096])
    def test_every_backend_agrees_with_the_reference(self, size):
        data = os.urandom(size)
        expected = ige256_encrypt_python(data, KEY, IGE_IV)
        for name, encrypt, decrypt in available():
            assert encrypt(data, KEY, IGE_IV) == expected, name
            assert decrypt(expected, KEY, IGE_IV) == data, name

    def test_every_backend_refuses_the_same_arguments(self):
        for name, encrypt, _ in available():
            with pytest.raises(ValueError):
                encrypt(bytes(24), KEY, IGE_IV)
            with pytest.raises(ValueError):
                encrypt(bytes(16), bytes(16), IGE_IV)
            with pytest.raises(ValueError):
                encrypt(bytes(16), KEY, bytes(16))

    def test_the_entry_points_round_trip(self):
        data = os.urandom(512)
        assert ige256_decrypt(ige256_encrypt(data, KEY, IGE_IV), KEY, IGE_IV) == data


class TestCounterMode:
    def test_the_chosen_ctr_agrees_with_the_reference(self):
        data = os.urandom(1000)
        assert new_ctr(KEY, CTR_IV).apply(data) == CTR(KEY, CTR_IV).apply(data)

    def test_it_is_a_stream_rather_than_a_series_of_calls(self):
        # Telegram uses this over a whole transfer, so a call that ends part
        # way through a keystream block has to resume there and not restart.
        data = os.urandom(100)
        one_shot = CTR(KEY, CTR_IV).apply(data)
        cipher = new_ctr(KEY, CTR_IV)
        in_pieces = b"".join(
            cipher.apply(data[at : at + 7]) for at in range(0, len(data), 7)
        )
        assert in_pieces == one_shot

    def test_it_is_its_own_inverse(self):
        data = os.urandom(64)
        encrypted = new_ctr(KEY, CTR_IV).apply(data)
        assert new_ctr(KEY, CTR_IV).apply(encrypted) == data

    def test_nothing_in_nothing_out(self):
        assert new_ctr(KEY, CTR_IV).apply(b"") == b""

    def test_a_bad_iv_is_refused(self):
        with pytest.raises(ValueError):
            new_ctr(KEY, bytes(8))

    def test_the_fallback_is_the_pure_python_one(self):
        name, factory = _select_ctr()
        if name == "python":
            assert factory is CTR


class TestLeavingTheLoop:
    async def test_a_small_call_stays_where_it_is(self):
        here = threading.get_ident()
        ran_on = await off_loop(OFFLOAD_ABOVE - 1, threading.get_ident)
        assert ran_on == here

    async def test_a_big_call_goes_to_a_thread(self):
        here = threading.get_ident()
        ran_on = await off_loop(OFFLOAD_ABOVE, threading.get_ident)
        assert ran_on != here

    async def test_the_answer_comes_back_either_way(self):
        data = os.urandom(OFFLOAD_ABOVE + 16 - (OFFLOAD_ABOVE % 16))
        big = await off_loop(len(data), ige256_encrypt, data, KEY, IGE_IV)
        small = await off_loop(0, ige256_encrypt, data, KEY, IGE_IV)
        assert big == small == ige256_encrypt_python(data, KEY, IGE_IV)

    async def test_what_the_work_raises_reaches_the_caller(self):
        with pytest.raises(ValueError):
            await off_loop(OFFLOAD_ABOVE, ige256_encrypt, bytes(24), KEY, IGE_IV)

    async def test_the_loop_keeps_running_underneath_a_big_one(self):
        # The point of the whole exercise: a long cipher call must not stop a
        # ping, a read, or anything else the program has going on.
        ticks = 0

        async def tick() -> None:
            nonlocal ticks
            while True:
                await asyncio.sleep(0.001)
                ticks += 1

        ticking = asyncio.create_task(tick())
        await asyncio.sleep(0.01)
        before = ticks
        # Sized so the pure Python rung takes a moment; a native one is quick
        # enough that the sleep below is what does the waiting.
        data = os.urandom(64 * 1024)
        await off_loop(len(data), ige256_encrypt, data, KEY, IGE_IV)
        await asyncio.sleep(0.01)
        ticking.cancel()
        await asyncio.gather(ticking, return_exceptions=True)
        assert ticks > before
