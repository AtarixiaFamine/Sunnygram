"""The datacenter table and the handshake, run against a scripted server.

The server here is real work, not a stub: it opens our RSA block, completes the
Diffie-Hellman exchange and proves it reached the same key. That means the test
covers RSA_PAD, the temporary key derivation, the answer envelope, the parameter
checks and the final hash in one go, and any asymmetry between the two sides
shows up immediately.

It needs a private key, which Telegram's is not, so a throwaway 2048-bit pair is
generated for the run and offered as if it were a test datacenter's.
"""

from __future__ import annotations

import asyncio
import hashlib
import secrets
import time

import pytest

from sunnygram.crypto import (
    PublicKey,
    ige256_decrypt,
    ige256_encrypt,
    new_nonce_hash,
    server_salt,
    temp_key_iv,
    unwrap_answer,
    wrap_client_data,
)
from sunnygram.crypto import rsa as rsa_module
from sunnygram.crypto.auth_key import _is_probable_prime
from sunnygram.crypto.rsa import _fingerprint
from sunnygram.errors import SecurityError
from sunnygram.network import Address, address_for, create_auth_key
from sunnygram.raw import functions, types
from sunnygram.session import pack_plaintext, unpack_plaintext
from sunnygram.tl import TLReader
from sunnygram.utils import signed

# The safe prime from Telegram's own worked example, with g = 3.
PRIME = int(
    "C71CAEB9C6B1C9048E6C522F70F13F73980D40238E3E21C14934D037563D930F"
    "48198A0AA7C14058229493D22530F4DBFA336F6E0AC925139543AED44CCE7C37"
    "20FD51F69458705AC68CD4FE6B6B13ABDC9746512969328454F18FAF8C595F64"
    "2477FE96BB2A941D5BCD1D4AC8CC49880708FA9B378E3C4F3A9060BEE67CF9A4"
    "A4A695811051907E162753B56B0F6B410DBA74D8A84B2A14B3144E0EF1284754"
    "FD17ED950D5965B4B9DD46582DB1178D169C6BC465B0D6FF9CA3928FEF5B9AE4"
    "E418FC15E83EBEA0F87FA9FF5EED70050DED2849F47BF959D956850CE929851F"
    "0D8115F635B105EE2E4E15D04B2454BF6F4FADF034B10403119CD8E3B92FCC5B",
    16,
)
G = 3


class TestDatacenters:
    def test_the_main_datacenters_are_reachable_by_id(self):
        for dc_id in (1, 2, 3, 4, 5):
            assert address_for(dc_id).port == 443
            assert address_for(dc_id).dc_id == dc_id

    def test_test_datacenters_are_a_separate_table(self):
        assert address_for(2, test=True) != address_for(2)

    def test_ipv6_is_a_separate_table(self):
        assert ":" in address_for(2, ipv6=True).host
        assert "." in address_for(2).host

    def test_an_unknown_datacenter_says_which_ones_exist(self):
        with pytest.raises(LookupError, match="there are"):
            address_for(99)

    def test_addresses_are_comparable_values(self):
        assert Address(1, "127.0.0.1") == Address(1, "127.0.0.1", 443)


def _prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (3 << (bits - 2)) | 1
        if _is_probable_prime(candidate, rounds=16):
            return candidate


@pytest.fixture(scope="module")
def keypair() -> tuple[PublicKey, int]:
    """A throwaway 2048-bit RSA key, public half plus private exponent."""
    p, q = _prime(1024), _prime(1024)
    modulus = p * q
    exponent = 65537
    assert modulus.bit_length() == 2048
    private = pow(exponent, -1, (p - 1) * (q - 1))
    return PublicKey(modulus, exponent, _fingerprint(modulus, exponent)), private


class Wire:
    """Two queues standing in for a connection, from the client's side."""

    def __init__(self) -> None:
        self.to_server: asyncio.Queue[bytes] = asyncio.Queue()
        self.to_client: asyncio.Queue[bytes] = asyncio.Queue()

    async def send(self, payload: bytes) -> None:
        await self.to_server.put(payload)

    async def receive(self) -> bytes:
        return await self.to_client.get()


class ScriptedServer:
    """The server half of the handshake, well enough to be convincing."""

    def __init__(
        self, wire: Wire, key: PublicKey, private: int, *, clock_skew: int = 0
    ) -> None:
        self.wire = wire
        self.key = key
        self.private = private
        self.auth_key = b""
        self.salt = 0
        # Something the client will have to factor, sized like the real thing.
        self.pq = 2147483647 * 1000000007
        self.server_nonce = signed(secrets.randbits(128), 128)
        self.a = secrets.randbits(2048)
        self.clock_skew = clock_skew
        self.server_time = 0
        self.seen: list[object] = []

    async def _take(self) -> object:
        _, body = unpack_plaintext(await self.wire.to_server.get())
        request = TLReader(body).read_object()
        self.seen.append(request)
        return request

    async def _give(self, response: object, msg_id: int = 1) -> None:
        assert hasattr(response, "to_bytes")
        await self.wire.to_client.put(pack_plaintext(msg_id, response.to_bytes()))

    def _open_rsa_block(self, encrypted: bytes) -> bytes:
        """Undo RSA_PAD the way a real server does."""
        block = pow(
            int.from_bytes(encrypted, "big"), self.private, self.key.modulus
        ).to_bytes(256, "big")
        hidden, body = block[:32], block[32:]
        aes_key = bytes(
            a ^ b for a, b in zip(hidden, hashlib.sha256(body).digest())
        )
        with_hash = ige256_decrypt(body, aes_key, bytes(32))
        padded = with_hash[:192][::-1]
        if with_hash[192:] != hashlib.sha256(aes_key + padded).digest():
            raise AssertionError("the client's padded block does not hash out")
        return padded

    async def run(self) -> None:
        request = await self._take()
        assert isinstance(request, functions.mtproto.ReqPqMulti)
        nonce = request.nonce
        await self._give(
            types.mtproto.ResPQ(
                nonce=nonce,
                server_nonce=self.server_nonce,
                pq=self.pq.to_bytes(8, "big"),
                server_public_key_fingerprints=[self.key.fingerprint],
            )
        )

        request = await self._take()
        assert isinstance(request, functions.mtproto.ReqDHParams)
        assert request.public_key_fingerprint == self.key.fingerprint
        assert int.from_bytes(request.p, "big") * int.from_bytes(
            request.q, "big"
        ) == self.pq
        padded = self._open_rsa_block(request.encrypted_data)
        inner = TLReader(padded).read_object()
        assert isinstance(inner, types.mtproto.PQInnerDataDc)
        assert inner.nonce == nonce
        assert inner.server_nonce == self.server_nonce
        new_nonce = inner.new_nonce

        temp_key, temp_iv = temp_key_iv(self.server_nonce, new_nonce)
        # Stamped as the answer goes out, like a real server would.
        self.server_time = int(time.time()) + self.clock_skew
        answer = types.mtproto.ServerDHInnerData(
            nonce=nonce,
            server_nonce=self.server_nonce,
            g=G,
            dh_prime=PRIME.to_bytes(256, "big"),
            g_a=pow(G, self.a, PRIME).to_bytes(256, "big"),
            server_time=self.server_time,
        )
        await self._give(
            types.mtproto.ServerDHParamsOk(
                nonce=nonce,
                server_nonce=self.server_nonce,
                encrypted_answer=ige256_encrypt(
                    wrap_client_data(answer.to_bytes()), temp_key, temp_iv
                ),
            )
        )

        request = await self._take()
        assert isinstance(request, functions.mtproto.SetClientDHParams)
        client_data = TLReader(
            unwrap_answer(ige256_decrypt(request.encrypted_data, temp_key, temp_iv))
        ).read_object()
        assert isinstance(client_data, types.mtproto.ClientDHInnerData)
        assert client_data.nonce == nonce
        g_b = int.from_bytes(client_data.g_b, "big")
        self.auth_key = pow(g_b, self.a, PRIME).to_bytes(256, "big")
        self.salt = server_salt(new_nonce, self.server_nonce)

        await self._give(
            types.mtproto.DhGenOk(
                nonce=nonce,
                server_nonce=self.server_nonce,
                new_nonce_hash1=new_nonce_hash(new_nonce, self.auth_key, 1),
            )
        )


class TestHandshake:
    async def test_both_sides_end_up_with_the_same_key(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()
        server = ScriptedServer(wire, key, private)
        running = asyncio.create_task(server.run())

        result = await create_auth_key(wire, dc_id=2, test=True)
        await running

        assert result.key == server.auth_key
        assert len(result.key) == 256
        assert result.salt == server.salt
        # A server on our own clock leaves an offset near zero, give or take
        # however long the exchange itself took.
        assert abs(result.time_offset) < 30

    async def test_the_offset_picks_up_the_server_clock(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()
        server = ScriptedServer(wire, key, private, clock_skew=3600)
        running = asyncio.create_task(server.run())
        result = await create_auth_key(wire, dc_id=2, test=True)
        await running
        # An hour ahead, so every message id from here on has to follow.
        assert 3500 < result.time_offset < 3700

    async def test_it_asked_for_the_right_datacenter(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()
        server = ScriptedServer(wire, key, private)
        running = asyncio.create_task(server.run())
        await create_auth_key(wire, dc_id=4, test=True)
        await running
        # The datacenter is inside the encrypted block, so the server had to
        # open it to see this at all.
        assert isinstance(server.seen[1], functions.mtproto.ReqDHParams)

    async def test_a_key_we_do_not_know_is_refused(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()

        async def unknown_key() -> None:
            request = TLReader(unpack_plaintext(await wire.to_server.get())[1]).read_object()
            await wire.to_client.put(
                pack_plaintext(
                    1,
                    types.mtproto.ResPQ(
                        nonce=request.nonce,
                        server_nonce=1,
                        pq=(2147483647 * 1000000007).to_bytes(8, "big"),
                        server_public_key_fingerprints=[12345],
                    ).to_bytes(),
                )
            )

        running = asyncio.create_task(unknown_key())
        with pytest.raises(SecurityError, match="no key we know"):
            await create_auth_key(wire, dc_id=2, test=True)
        await running

    async def test_a_cdn_datacenter_is_named_by_the_key_it_came_with(self, keypair):
        # Nothing is monkeypatched here, which is the point: a CDN datacenter
        # is named by neither built-in key, only by the one that arrived in
        # help.getCdnConfig, so the handshake has to be handed it.
        key, private = keypair
        wire = Wire()
        server = ScriptedServer(wire, key, private)
        running = asyncio.create_task(server.run())
        result = await create_auth_key(wire, dc_id=203, keys=(key,))
        await running
        assert result.key == server.auth_key

    async def test_a_cdn_offering_a_key_from_elsewhere_is_refused(self, keypair):
        from sunnygram.crypto import PRODUCTION_KEYS

        key, private = keypair
        wire = Wire()
        server = ScriptedServer(wire, key, private)
        running = asyncio.create_task(server.run())
        # The server offers the key it holds, which is a real key and is not
        # the one this datacenter was introduced with.
        with pytest.raises(SecurityError, match="no key we know"):
            await create_auth_key(wire, dc_id=203, keys=tuple(PRODUCTION_KEYS))
        running.cancel()
        await asyncio.gather(running, return_exceptions=True)

    async def test_a_swapped_nonce_is_caught(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()

        async def wrong_nonce() -> None:
            await wire.to_server.get()
            await wire.to_client.put(
                pack_plaintext(
                    1,
                    types.mtproto.ResPQ(
                        nonce=999,
                        server_nonce=1,
                        pq=(2147483647 * 1000000007).to_bytes(8, "big"),
                        server_public_key_fingerprints=[key.fingerprint],
                    ).to_bytes(),
                )
            )

        running = asyncio.create_task(wrong_nonce())
        with pytest.raises(SecurityError, match="different nonce"):
            await create_auth_key(wire, dc_id=2, test=True)
        await running

    async def test_a_server_that_will_not_agree(self, keypair, monkeypatch):
        key, private = keypair
        monkeypatch.setattr(rsa_module, "TEST_KEYS", (key,))
        wire = Wire()
        server = ScriptedServer(wire, key, private)

        async def refuse_at_the_end() -> None:
            request = await server._take()
            await server._give(
                types.mtproto.ResPQ(
                    nonce=request.nonce,
                    server_nonce=server.server_nonce,
                    pq=server.pq.to_bytes(8, "big"),
                    server_public_key_fingerprints=[key.fingerprint],
                )
            )
            await server._take()
            await server._give(
                types.mtproto.ServerDHParamsFail(
                    nonce=request.nonce,
                    server_nonce=server.server_nonce,
                    new_nonce_hash=0,
                )
            )

        running = asyncio.create_task(refuse_at_the_end())
        with pytest.raises(SecurityError, match="rejected our answer"):
            await create_auth_key(wire, dc_id=2, test=True)
        await running
