"""Downloading through a content delivery network, without a network.

Two datacenters answer here: Telegram, which knows who we are and hands out a
key, and a CDN, which does not and hands out encrypted blocks. That split is the
whole point of the arrangement and it is what these tests are about. The CDN is
given every chance to misbehave, because in this design it is the party nobody
trusts: it is checked that a changed byte is caught, that a wrong hash is
caught, that a hash that was never published is not quietly waved through, and
that the account is never introduced to it.

The other half is the ordinary business of a cache: a miss, which the real
datacenter fixes by pushing the file over, and a token that has aged out, which
it fixes by issuing another.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import pytest

from mtproto_server import AUTH_KEY, ScriptedServer, Wire
from sunnygram.crypto import PublicKey, new_ctr
from sunnygram.errors import SecurityError, SunnygramError
from sunnygram.files import download_file
from sunnygram.files.cdn import CdnSession
from sunnygram.network import Address, ClientInfo, Invoker
from sunnygram.network.config import cdn_address, cdn_keys
from sunnygram.raw import functions, types
from sunnygram.storage import MemoryStorage, SessionState

CLIENT = ClientInfo(api_id=12345, api_hash="0" * 32)
ME = 777000
HOME = 2
CDN = 203

TOKEN = b"a file token"
KEY = bytes(range(32))
IV = bytes(range(100, 116))
BLOCK = 4096


def a_document(size: int, *, dc_id: int = HOME) -> types.Document:
    return types.Document(
        id=900,
        access_hash=77,
        file_reference=b"ref",
        date=1700000000,
        mime_type="application/octet-stream",
        size=size,
        dc_id=dc_id,
        attributes=[types.DocumentAttributeFilename(file_name="big.bin")],
    )


def encrypt_at(offset: int, plain: bytes) -> bytes:
    """What a CDN holds for one piece of a file.

    The counter starts at the block this piece begins on, which is what lets
    the middle of a file be decrypted without the beginning.
    """
    counter = IV[:12] + (offset // 16).to_bytes(4, "big")
    return new_ctr(KEY, counter).apply(plain)


def hashes_for(content: bytes, block: int, *, start: int = 0) -> list[types.FileHash]:
    return [
        types.FileHash(
            offset=at,
            limit=len(content[at : at + block]),
            hash=hashlib.sha256(content[at : at + block]).digest(),
        )
        for at in range(start, len(content), block)
    ]


# A minimal DER writer, so a test can hand over a public key the way a config
# does: as PEM text. Nothing in the library writes DER, only reads it.


def _der_len(size: int) -> bytes:
    if size < 0x80:
        return bytes([size])
    body = size.to_bytes((size.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def _der_int(value: int) -> bytes:
    raw = value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")
    if raw[0] & 0x80:
        raw = b"\x00" + raw
    return b"\x02" + _der_len(len(raw)) + raw


def _pkcs1(key: PublicKey) -> bytes:
    body = _der_int(key.modulus) + _der_int(key.exponent)
    return b"\x30" + _der_len(len(body)) + body


def _wrap(der: bytes, label: str) -> str:
    body = base64.b64encode(der).decode()
    lines = "\n".join(body[at : at + 64] for at in range(0, len(body), 64))
    return f"-----BEGIN {label}-----\n{lines}\n-----END {label}-----\n"


def pkcs1_pem(key: PublicKey) -> str:
    return _wrap(_pkcs1(key), "RSA PUBLIC KEY")


def spki_pem(key: PublicKey) -> str:
    rsa_encryption = bytes.fromhex("06092a864886f70d010101") + b"\x05\x00"
    algorithm = b"\x30" + _der_len(len(rsa_encryption)) + rsa_encryption
    inner = b"\x00" + _pkcs1(key)
    bits = b"\x03" + _der_len(len(inner)) + inner
    body = algorithm + bits
    return _wrap(b"\x30" + _der_len(len(body)) + body, "PUBLIC KEY")


A_KEY = PublicKey(modulus=0xC0FFEE00BAADF00D, exponent=65537, fingerprint=1)


class Network:
    """Every datacenter a test reaches, answering on every socket into it."""

    def __init__(self) -> None:
        self.wires: list[tuple[Address, Wire]] = []
        self.telegram = Telegram()
        self.cdn = Cdn(self.telegram)
        self.serving: list[asyncio.Task[None]] = []

    async def connect(self, where: Address) -> Wire:
        wire = Wire()
        self.wires.append((where, wire))
        return wire

    def answer_on(self, dc_id: int, connection: Any) -> None:
        holder = self.telegram if dc_id == HOME else self.cdn
        server = _Server(self.wires[-1][1], connection.session, holder)
        self.serving.append(asyncio.create_task(server.serve()))


class Telegram:
    """The datacenter that knows the account, and redirects."""

    def __init__(self) -> None:
        self.content = b""
        self.block = BLOCK
        # How many hashes the redirect itself carries. Fewer than the file
        # needs is the ordinary case: the rest are asked for as the download
        # moves through it.
        self.hashes_up_front = 0
        self.publishes_hashes = True
        self.asked: list[Any] = []
        self.redirects = 0
        self.pushes = 0
        self.address = "10.0.0.203"
        self.cdn_flag = True
        self.tcpo_only = False
        self.serve_directly = False

    def redirect(self) -> types.upload.FileCdnRedirect:
        self.redirects += 1
        upfront = hashes_for(self.content, self.block)[: self.hashes_up_front]
        return types.upload.FileCdnRedirect(
            dc_id=CDN,
            file_token=TOKEN,
            encryption_key=KEY,
            encryption_iv=IV,
            file_hashes=upfront,
        )

    def config(self) -> types.Config:
        option = types.DcOption(
            id=CDN,
            ip_address=self.address,
            port=443,
            cdn=self.cdn_flag,
            tcpo_only=self.tcpo_only,
        )
        return _config([types.DcOption(id=HOME, ip_address="10.0.0.2", port=443), option])

    def cdn_config(self) -> types.CdnConfig:
        return types.CdnConfig(
            public_keys=[types.CdnPublicKey(dc_id=CDN, public_key=pkcs1_pem(A_KEY))]
        )


class Cdn:
    """The datacenter that holds the bytes and knows nothing else."""

    def __init__(self, telegram: Telegram) -> None:
        self.telegram = telegram
        self.asked: list[Any] = []
        self.introduced = False
        self.cold = 0
        self.stale_token = 0
        self.tamper: bool = False
        self.answer_wrongly = False

    def piece(self, offset: int, limit: int) -> bytes:
        plain = self.telegram.content[offset : offset + limit]
        if self.tamper and plain:
            plain = bytes([plain[0] ^ 0xFF]) + plain[1:]
        return encrypt_at(offset, plain)


def _config(options: list[types.DcOption]) -> types.Config:
    """A config with the one field these tests care about filled in."""
    return types.Config(
        date=0,
        expires=0,
        test_mode=False,
        this_dc=HOME,
        dc_options=options,
        dc_txt_domain_name="",
        chat_size_max=200,
        megagroup_size_max=200000,
        forwarded_count_max=100,
        online_update_period_ms=0,
        offline_blur_timeout_ms=0,
        offline_idle_timeout_ms=0,
        online_cloud_timeout_ms=0,
        notify_cloud_delay_ms=0,
        notify_default_delay_ms=0,
        push_chat_period_ms=0,
        push_chat_limit=0,
        edit_time_limit=0,
        revoke_time_limit=0,
        revoke_pm_time_limit=0,
        rating_e_decay=0,
        stickers_recent_limit=0,
        channels_read_media_period=0,
        call_receive_timeout_ms=0,
        call_ring_timeout_ms=0,
        call_connect_timeout_ms=0,
        call_packet_timeout_ms=0,
        me_url_prefix="",
        caption_length_max=1024,
        message_length_max=4096,
        webfile_dc_id=4,
    )


class _Server(ScriptedServer):
    """One connection into whichever of the two datacenters it belongs to."""

    def __init__(self, wire: Wire, session: Any, holder: Telegram | Cdn) -> None:
        super().__init__(wire, session)
        self.holder = holder

    async def serve(self) -> None:
        while True:
            request = await self.take()
            query = request.query
            self.holder.asked.append(query)
            if isinstance(self.holder, Telegram):
                await self._telegram(request.msg_id, query, self.holder)
            else:
                await self._cdn(request.msg_id, query, self.holder)

    async def _telegram(self, msg_id: int, query: Any, dc: Telegram) -> None:
        if isinstance(query, functions.upload.GetFile):
            if query.cdn_supported and not dc.serve_directly:
                await self.answer(msg_id, dc.redirect())
                return
            piece = dc.content[query.offset : query.offset + query.limit]
            await self.answer(
                msg_id,
                types.upload.File(
                    type=types.storage.FileUnknown(), mtime=0, bytes=piece
                ),
            )
        elif isinstance(query, functions.help.GetConfig):
            await self.answer(msg_id, dc.config())
        elif isinstance(query, functions.help.GetCdnConfig):
            await self.answer(msg_id, dc.cdn_config())
        elif isinstance(query, functions.upload.GetCdnFileHashes):
            found = (
                hashes_for(dc.content, dc.block, start=query.offset)
                if dc.publishes_hashes
                else []
            )
            await self.answer(msg_id, found)
        elif isinstance(query, functions.upload.ReuploadCdnFile):
            dc.pushes += 1
            await self.answer(msg_id, hashes_for(dc.content, dc.block))
        else:
            await self.refuse(msg_id, 400, "METHOD_NOT_TESTED")

    async def _cdn(self, msg_id: int, query: Any, dc: Cdn) -> None:
        if isinstance(query, functions.auth.ImportAuthorization):
            dc.introduced = True
            await self.refuse(msg_id, 400, "CDN_METHOD_INVALID")
        elif isinstance(query, functions.upload.GetCdnFile):
            if dc.stale_token > 0:
                dc.stale_token -= 1
                await self.refuse(msg_id, 400, "FILE_TOKEN_INVALID")
            elif dc.answer_wrongly:
                await self.answer(
                    msg_id,
                    types.upload.File(
                        type=types.storage.FileUnknown(), mtime=0, bytes=b"nope"
                    ),
                )
            elif dc.cold > 0:
                dc.cold -= 1
                await self.answer(
                    msg_id, types.upload.CdnFileReuploadNeeded(request_token=b"push")
                )
            else:
                await self.answer(
                    msg_id,
                    types.upload.CdnFile(bytes=dc.piece(query.offset, query.limit)),
                )
        else:
            await self.refuse(msg_id, 400, "METHOD_NOT_TESTED")


class Served(Invoker):
    """An invoker whose every connection finds somebody answering."""

    def __init__(self, *args: Any, network: Network, **options: Any) -> None:
        super().__init__(*args, **options)
        self._network = network

    async def _open(self, dc_id: int, *, updates: bool = False) -> Any:
        connection = await super()._open(dc_id, updates=updates)
        self._network.answer_on(dc_id, connection)
        return connection


@asynccontextmanager
async def live(content: bytes) -> AsyncIterator[tuple[Invoker, Network]]:
    session = SessionState(dc_id=HOME, user_id=ME)
    session.set_auth_key(HOME, AUTH_KEY)
    # The key for the CDN is seeded so these tests are about the download
    # rather than about the handshake, which test_network covers whole.
    session.set_auth_key(CDN, AUTH_KEY)
    network = Network()
    network.telegram.content = content
    invoker = Served(
        MemoryStorage(session),
        network=network,
        client=CLIENT,
        connector=network.connect,
        ping_interval=None,
        timeout=5.0,
        bulk_connections=0,
    )
    await invoker.start()
    try:
        yield invoker, network
    finally:
        for task in network.serving:
            task.cancel()
        await asyncio.gather(*network.serving, return_exceptions=True)
        await invoker.close()


class TestReadingTheConfig:
    """Finding a datacenter that is not in the built-in table."""

    def test_a_cdn_datacenter_is_found_by_its_flag(self):
        options = [
            types.DcOption(id=CDN, ip_address="1.2.3.4", port=443),
            types.DcOption(id=CDN, ip_address="5.6.7.8", port=443, cdn=True),
        ]
        assert cdn_address(options, CDN) == Address(CDN, "5.6.7.8", 443)

    def test_ipv6_is_preferred_when_asked_for(self):
        options = [
            types.DcOption(id=CDN, ip_address="5.6.7.8", port=443, cdn=True),
            types.DcOption(id=CDN, ip_address="::1", port=443, cdn=True, ipv6=True),
        ]
        assert cdn_address(options, CDN, ipv6=True).host == "::1"
        assert cdn_address(options, CDN).host == "5.6.7.8"

    def test_the_other_family_is_taken_rather_than_failing(self):
        options = [types.DcOption(id=CDN, ip_address="5.6.7.8", port=443, cdn=True)]
        assert cdn_address(options, CDN, ipv6=True).host == "5.6.7.8"

    def test_an_address_that_wants_obfuscation_is_skipped(self):
        options = [
            types.DcOption(
                id=CDN, ip_address="5.6.7.8", port=443, cdn=True, tcpo_only=True
            )
        ]
        with pytest.raises(SunnygramError, match="did not say where it is"):
            cdn_address(options, CDN)

    def test_a_datacenter_missing_from_the_config_says_so(self):
        with pytest.raises(SunnygramError, match="did not say where it is"):
            cdn_address([], CDN)

    def test_keys_are_taken_by_datacenter(self):
        config = types.CdnConfig(
            public_keys=[
                types.CdnPublicKey(dc_id=204, public_key=pkcs1_pem(A_KEY)),
                types.CdnPublicKey(dc_id=CDN, public_key=pkcs1_pem(A_KEY)),
            ]
        )
        assert len(cdn_keys(config, CDN)) == 1

    def test_a_datacenter_with_no_key_is_refused(self):
        config = types.CdnConfig(public_keys=[])
        with pytest.raises(SunnygramError, match="no public key"):
            cdn_keys(config, CDN)


class TestReadingAKey:
    """The PEM a config carries, in both spellings."""

    def test_a_pkcs1_key_round_trips(self):
        read = PublicKey.from_pem(pkcs1_pem(A_KEY))
        assert (read.modulus, read.exponent) == (A_KEY.modulus, A_KEY.exponent)

    def test_a_wrapped_key_round_trips(self):
        read = PublicKey.from_pem(spki_pem(A_KEY))
        assert (read.modulus, read.exponent) == (A_KEY.modulus, A_KEY.exponent)

    def test_a_real_key_is_read_the_same_either_way(self):
        from sunnygram.crypto import PRODUCTION_KEYS

        real = PRODUCTION_KEYS[0]
        assert PublicKey.from_pem(pkcs1_pem(real)) == real
        assert PublicKey.from_pem(spki_pem(real)) == real

    def test_text_that_is_not_a_key_is_refused(self):
        with pytest.raises(ValueError):
            PublicKey.from_pem("-----BEGIN RSA PUBLIC KEY-----\n-----END-----")


class TestFollowingARedirect:
    """The ordinary path: Telegram points elsewhere and the file arrives."""

    async def test_a_file_comes_back_whole_through_the_cdn(self):
        content = os.urandom(20000)
        async with live(content) as (invoker, network):
            got = await download_file(
                invoker, a_document(len(content)), chunk_size=8192
            )
            assert got == content
            assert network.telegram.redirects == 1
            # And every byte came from the CDN rather than from Telegram.
            served = [
                query
                for query in network.telegram.asked
                if isinstance(query, functions.upload.GetFile)
            ]
            assert len(served) == 1

    async def test_the_account_is_never_introduced_to_the_cdn(self):
        content = os.urandom(9000)
        async with live(content) as (invoker, network):
            assert await download_file(invoker, a_document(len(content))) == content
            assert network.cdn.introduced is False
            assert invoker.is_cdn(CDN) is True

    async def test_a_file_of_unknown_size_is_fetched_in_order(self):
        content = os.urandom(10000)
        async with live(content) as (invoker, network):
            got = await download_file(
                invoker, a_document(0), chunk_size=4096
            )
            assert got == content

    async def test_hashes_are_asked_for_when_the_redirect_carries_none(self):
        content = os.urandom(12288)
        async with live(content) as (invoker, network):
            assert await download_file(invoker, a_document(len(content))) == content
            asked = [
                query
                for query in network.telegram.asked
                if isinstance(query, functions.upload.GetCdnFileHashes)
            ]
            assert asked, "the hashes have to come from Telegram, not the CDN"

    async def test_hashes_in_the_redirect_are_used_as_they_stand(self):
        content = os.urandom(12288)
        async with live(content) as (invoker, network):
            network.telegram.hashes_up_front = 3
            assert await download_file(invoker, a_document(len(content))) == content
            asked = [
                query
                for query in network.telegram.asked
                if isinstance(query, functions.upload.GetCdnFileHashes)
            ]
            assert not asked

    async def test_a_download_can_refuse_to_be_redirected(self):
        content = os.urandom(9000)
        async with live(content) as (invoker, network):
            got = await download_file(invoker, a_document(len(content)), cdn=False)
            assert got == content
            assert network.telegram.redirects == 0
            assert not network.cdn.asked

    async def test_pieces_smaller_than_a_block_are_still_checked_whole(self):
        # A caller asking for less than one published hash covers cannot have
        # what it asked for checked on its own, so the blocks around it are
        # fetched and checked and the piece is cut out of them.
        content = os.urandom(16384)
        async with live(content) as (invoker, network):
            network.telegram.block = 8192
            got = await download_file(
                invoker, a_document(len(content)), chunk_size=4096
            )
            assert got == content


class TestWhenTheCdnMisbehaves:
    """The part that matters: nothing unverified reaches the caller."""

    async def test_a_changed_byte_is_caught(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            network.cdn.tamper = True
            with pytest.raises(SecurityError, match="not what Telegram says"):
                await download_file(invoker, a_document(len(content)))

    async def test_a_block_nobody_published_a_hash_for_is_refused(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            # Telegram answers the request for hashes with none at all, which
            # leaves the download holding bytes it cannot check. Handing those
            # over would be the CDN being trusted, which is the one thing this
            # arrangement is built not to do.
            network.telegram.publishes_hashes = False
            with pytest.raises(SecurityError, match="published no hash"):
                await download_file(invoker, a_document(len(content)))

    async def test_a_short_answer_inside_a_block_is_refused(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            session = CdnSession(invoker, network.telegram.redirect(), HOME)
            hashes = hashes_for(content, 4096)
            session._learn(hashes)
            with pytest.raises(SecurityError, match="would go unchecked"):
                await session._check(0, content[:2048])

    async def test_a_hash_covering_nothing_is_refused_rather_than_looped_on(self):
        content = os.urandom(4096)
        async with live(content) as (invoker, network):
            session = CdnSession(invoker, network.telegram.redirect(), HOME)
            session._learn([types.FileHash(offset=0, limit=0, hash=b"")])
            with pytest.raises(SecurityError, match="cannot be right"):
                await session._check(0, content)

    async def test_an_answer_that_is_not_a_file_says_what_it_was(self):
        content = os.urandom(4096)
        async with live(content) as (invoker, network):
            network.cdn.answer_wrongly = True
            session = CdnSession(invoker, network.telegram.redirect(), HOME)
            with pytest.raises(SunnygramError, match="expected a CDN file"):
                await session._encrypted(0, 4096)

    async def test_a_piece_that_cannot_be_decrypted_says_why(self):
        content = os.urandom(4096)
        async with live(content) as (invoker, network):
            session = CdnSession(invoker, network.telegram.redirect(), HOME)
            # The counter is set from the offset divided by sixteen, so an
            # offset that is not a multiple of sixteen names no counter at all.
            with pytest.raises(SunnygramError, match="16 byte boundary"):
                await session._verified(8, 4096)

    def test_a_redirect_with_the_wrong_sized_key_is_refused(self):
        redirect = types.upload.FileCdnRedirect(
            dc_id=CDN,
            file_token=TOKEN,
            encryption_key=b"short",
            encryption_iv=IV,
            file_hashes=[],
        )
        with pytest.raises(SecurityError, match="not a 256 bit one"):
            CdnSession(None, redirect, HOME)  # type: ignore[arg-type]

    def test_a_redirect_with_the_wrong_sized_counter_is_refused(self):
        redirect = types.upload.FileCdnRedirect(
            dc_id=CDN,
            file_token=TOKEN,
            encryption_key=KEY,
            encryption_iv=b"short",
            file_hashes=[],
        )
        with pytest.raises(SecurityError, match="not a 128 bit one"):
            CdnSession(None, redirect, HOME)  # type: ignore[arg-type]


class TestWhenTheCacheMisses:
    """A CDN is a cache, and the ordinary failures are cache failures."""

    async def test_a_cold_cache_is_filled_and_the_piece_arrives(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            network.cdn.cold = 1
            assert await download_file(invoker, a_document(len(content))) == content
            assert network.telegram.pushes == 1

    async def test_a_cache_that_never_fills_gives_up(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            network.cdn.cold = 99
            with pytest.raises(SunnygramError, match="has not got this file"):
                await download_file(invoker, a_document(len(content)))

    async def test_an_aged_out_token_is_asked_for_again(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            network.cdn.stale_token = 1
            assert await download_file(invoker, a_document(len(content))) == content
            assert network.telegram.redirects == 2

    async def test_a_token_that_keeps_ageing_out_gives_up(self):
        content = os.urandom(8192)
        async with live(content) as (invoker, network):
            network.cdn.stale_token = 99
            with pytest.raises(SunnygramError, match="not producing a usable one"):
                await download_file(invoker, a_document(len(content)))


class TestDecryption:
    """The counter, which is the one piece of arithmetic here."""

    async def test_a_piece_from_the_middle_decrypts_on_its_own(self):
        content = os.urandom(16384)
        async with live(content) as (invoker, network):
            got = await download_file(
                invoker, a_document(len(content)), chunk_size=4096
            )
            assert got == content
            # Which is only true if each piece started its counter where it
            # belongs: one stream from zero would decrypt the first piece and
            # nothing after it.
            offsets = sorted(
                query.offset
                for query in network.cdn.asked
                if isinstance(query, functions.upload.GetCdnFile)
            )
            assert offsets == [0, 4096, 8192, 12288]
