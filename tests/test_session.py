"""Message ids, envelopes, and the session that enforces the incoming checks.

The server side is played by packing with the direction flipped, which is
exactly what a real server does with the other half of the auth key.
"""

from __future__ import annotations

import gzip
import time

import pytest

from sunnygram.crypto import auth_key_id
from sunnygram.errors import DuplicateMessage, SecurityError
from sunnygram.session import (
    CONTAINER_ID,
    FUTURE_TOLERANCE,
    HEADER_SIZE,
    MAX_PADDING,
    MIN_PADDING,
    Message,
    MessageIdGenerator,
    PAST_TOLERANCE,
    Session,
    is_server_id,
    msg_id_time,
    pack_encrypted,
    pack_plaintext,
    unpack_encrypted,
    unpack_plaintext,
    unwrap_container,
)
from sunnygram.tl import GZIP_PACKED, TLWriter

AUTH_KEY = bytes(range(256))
BODY = b"a serialized TL call"[:16]

# An offset small enough not to move anything, used where a test wants a session
# that already knows the time so the window is enforced rather than learned.
_TINY = 1e-9


def server_id(when: float | None = None, *, reply: bool = True) -> int:
    """A message id with the server's parity."""
    moment = time.time() if when is None else when
    return (int(moment) << 32) | (1 if reply else 3)


def from_server(
    session: Session, body: bytes = BODY, *, msg_id: int | None = None, seq_no: int = 1
) -> bytes:
    return pack_encrypted(
        AUTH_KEY,
        session.salt,
        session.session_id,
        Message(server_id() if msg_id is None else msg_id, seq_no, body),
        outgoing=False,
    )


class TestMessageIds:
    def test_ours_are_divisible_by_four(self):
        generator = MessageIdGenerator()
        for _ in range(50):
            assert generator.next() % 4 == 0

    def test_always_increasing(self):
        generator = MessageIdGenerator()
        ids = [generator.next() for _ in range(200)]
        assert ids == sorted(ids)
        assert len(set(ids)) == 200

    def test_a_clock_that_steps_back_cannot_repeat_an_id(self):
        generator = MessageIdGenerator()
        ahead = generator.next()
        generator.time_offset = -3600.0
        assert generator.next() > ahead

    def test_carries_the_current_time(self):
        assert abs(msg_id_time(MessageIdGenerator().next()) - time.time()) < 5

    def test_the_offset_moves_the_clock(self):
        assert (
            msg_id_time(MessageIdGenerator(3600.0).next())
            - msg_id_time(MessageIdGenerator().next())
            > 3000
        )

    def test_parity_says_who_minted_it(self):
        assert not is_server_id(MessageIdGenerator().next())
        assert is_server_id(server_id())
        assert is_server_id(server_id(reply=False))


class TestPlaintextEnvelope:
    def test_round_trip(self):
        frame = pack_plaintext(0x5F000000_00000000, BODY)
        assert frame[:8] == bytes(8)
        assert unpack_plaintext(frame) == (0x5F000000_00000000, BODY)

    def test_layout(self):
        frame = pack_plaintext(4, b"\x01\x02\x03\x04")
        assert len(frame) == 24
        assert int.from_bytes(frame[16:20], "little") == 4

    def test_refuses_an_encrypted_message(self):
        with pytest.raises(SecurityError, match="encrypted, not plaintext"):
            unpack_plaintext(auth_key_id(AUTH_KEY) + bytes(40))

    def test_refuses_a_length_that_does_not_match(self):
        frame = bytearray(pack_plaintext(4, BODY))
        frame[16] = 0xFF
        with pytest.raises(SecurityError, match="claims"):
            unpack_plaintext(bytes(frame))

    def test_refuses_a_stub(self):
        with pytest.raises(SecurityError):
            unpack_plaintext(bytes(8))


class TestEncryptedEnvelope:
    def test_round_trip(self):
        frame = pack_encrypted(AUTH_KEY, 7, 9, Message(4, 1, BODY))
        session_id, message = unpack_encrypted(AUTH_KEY, frame, outgoing=True)
        assert session_id == 9
        assert message == Message(4, 1, BODY)

    def test_layout(self):
        frame = pack_encrypted(AUTH_KEY, 7, 9, Message(4, 1, BODY))
        assert frame[:8] == auth_key_id(AUTH_KEY)
        assert (len(frame) - 24) % 16 == 0

    @pytest.mark.parametrize("size", [0, 4, 12, 16, 20, 64, 1024])
    def test_padding_stays_inside_the_allowed_range(self, size):
        frame = pack_encrypted(AUTH_KEY, 0, 1, Message(4, 1, bytes(size)))
        padding = len(frame) - 24 - HEADER_SIZE - size
        assert MIN_PADDING <= padding <= MAX_PADDING
        assert (len(frame) - 24) % 16 == 0

    def test_the_two_directions_do_not_share_a_key(self):
        frame = pack_encrypted(AUTH_KEY, 0, 1, Message(4, 1, BODY))
        with pytest.raises(SecurityError):
            unpack_encrypted(AUTH_KEY, frame, outgoing=False)

    def test_refuses_a_message_for_another_key(self):
        frame = pack_encrypted(AUTH_KEY, 0, 1, Message(4, 1, BODY))
        other = bytes(256)
        with pytest.raises(SecurityError, match="different key"):
            unpack_encrypted(other, frame, outgoing=True)

    def test_a_flipped_byte_anywhere_is_caught(self):
        frame = pack_encrypted(AUTH_KEY, 0, 1, Message(4, 1, BODY))
        for index in (8, 20, 24, 40, len(frame) - 1):
            broken = bytearray(frame)
            broken[index] ^= 0xFF
            with pytest.raises(SecurityError):
                unpack_encrypted(AUTH_KEY, bytes(broken), outgoing=True)

    def test_refuses_a_frame_that_is_not_whole_blocks(self):
        frame = pack_encrypted(AUTH_KEY, 0, 1, Message(4, 1, BODY))
        with pytest.raises(SecurityError, match="whole envelope"):
            unpack_encrypted(AUTH_KEY, frame[:-4], outgoing=True)
        with pytest.raises(SecurityError):
            unpack_encrypted(AUTH_KEY, bytes(24), outgoing=True)

    def test_a_forged_length_cannot_read_past_the_plaintext(self):
        # Rebuild a valid envelope around a header that lies about the body,
        # so the message key still matches and only the bounds check stands.
        from sunnygram.crypto import (
            compute_msg_key,
            derive_key_iv,
            ige256_encrypt,
        )

        header = (
            bytes(8)
            + (1).to_bytes(8, "little")
            + (4).to_bytes(8, "little")
            + (1).to_bytes(4, "little")
            + (0xFFFF).to_bytes(4, "little")
        )
        plaintext = header + bytes(16)
        msg_key = compute_msg_key(AUTH_KEY, plaintext, outgoing=True)
        key, iv = derive_key_iv(AUTH_KEY, msg_key, outgoing=True)
        frame = auth_key_id(AUTH_KEY) + msg_key + ige256_encrypt(plaintext, key, iv)
        with pytest.raises(SecurityError, match="claims 65535 bytes"):
            unpack_encrypted(AUTH_KEY, frame, outgoing=True)


class TestContainers:
    def test_a_plain_message_passes_through(self):
        message = Message(4, 1, b"\x01\x02\x03\x04")
        assert unwrap_container(message) == [message]

    def test_a_container_is_flattened(self):
        held = [Message(8, 1, b"\xaa\xbb\xcc\xdd"), Message(12, 3, b"\x01" * 8)]
        assert unwrap_container(Message(4, 0, _container(held))) == held

    def test_an_empty_container(self):
        assert unwrap_container(Message(4, 0, _container([]))) == []

    def test_a_gzipped_body_is_expanded(self):
        inner = b"\x01\x02\x03\x04" * 20
        writer = TLWriter()
        writer.write_int(GZIP_PACKED, signed=False)
        writer.write_bytes(gzip.compress(inner))
        assert unwrap_container(Message(4, 1, writer.getvalue())) == [
            Message(4, 1, inner)
        ]

    def test_a_gzipped_container_is_expanded_and_flattened(self):
        held = [Message(8, 1, b"\xaa\xbb\xcc\xdd")]
        writer = TLWriter()
        writer.write_int(GZIP_PACKED, signed=False)
        writer.write_bytes(gzip.compress(_container(held)))
        assert unwrap_container(Message(4, 0, writer.getvalue())) == held

    def test_an_impossible_count_is_refused(self):
        writer = TLWriter()
        writer.write_int(CONTAINER_ID, signed=False)
        writer.write_int(10**6)
        writer.write_raw(bytes(16))
        with pytest.raises(SecurityError, match="cannot hold"):
            unwrap_container(Message(4, 0, writer.getvalue()))

    def test_an_inner_length_past_the_container_is_refused(self):
        writer = TLWriter()
        writer.write_int(CONTAINER_ID, signed=False)
        writer.write_int(1)
        writer.write_long(8)
        writer.write_int(1)
        writer.write_int(4096)
        writer.write_raw(bytes(8))
        with pytest.raises(SecurityError, match="cannot be 4096 bytes"):
            unwrap_container(Message(4, 0, writer.getvalue()))


def _container(held: list[Message]) -> bytes:
    writer = TLWriter()
    writer.write_int(CONTAINER_ID, signed=False)
    writer.write_int(len(held))
    for message in held:
        writer.write_long(message.msg_id)
        writer.write_int(message.seq_no)
        writer.write_int(len(message.body))
        writer.write_raw(message.body)
    return writer.getvalue()


class TestSequenceNumbers:
    def test_content_advances_the_count(self):
        session = Session(AUTH_KEY)
        assert [
            session.next_seq_no(content_related=True) for _ in range(3)
        ] == [1, 3, 5]

    def test_housekeeping_reads_without_advancing(self):
        session = Session(AUTH_KEY)
        session.next_seq_no(content_related=True)
        assert session.next_seq_no(content_related=False) == 2
        assert session.next_seq_no(content_related=False) == 2
        assert session.next_seq_no(content_related=True) == 3


class TestSession:
    def test_sessions_do_not_collide(self):
        assert len({Session(AUTH_KEY).session_id for _ in range(20)}) == 20

    def test_refuses_an_auth_key_of_the_wrong_size(self):
        with pytest.raises(ValueError, match="256 bytes"):
            Session(bytes(128))

    @pytest.mark.parametrize(
        "given", [0, 1, -1, 2**63, 2**64 - 1, -(2**63), 0xA2AE955CB6090024]
    )
    def test_an_id_survives_either_spelling(self, given):
        # An id from a random source is unsigned and one off the wire is signed.
        # Both have to name the same session, or half of all sessions would
        # refuse every message they received.
        session = Session(AUTH_KEY, session_id=given)
        assert session.decrypt(from_server(session)).body == BODY

    def test_encrypt_hands_back_the_id_it_used(self):
        session = Session(AUTH_KEY)
        msg_id, frame = session.encrypt(BODY)
        assert msg_id % 4 == 0
        _, message = unpack_encrypted(AUTH_KEY, frame, outgoing=True)
        assert message.msg_id == msg_id
        assert message.body == BODY

    def test_accepts_a_message_from_the_server(self):
        session = Session(AUTH_KEY)
        assert session.decrypt(from_server(session)).body == BODY

    def test_refuses_another_session(self):
        session = Session(AUTH_KEY)
        frame = pack_encrypted(
            AUTH_KEY,
            0,
            session.session_id ^ 1,
            Message(server_id(), 1, BODY),
            outgoing=False,
        )
        with pytest.raises(SecurityError, match="different session"):
            session.decrypt(frame)

    def test_refuses_a_message_with_our_own_parity(self):
        session = Session(AUTH_KEY)
        ours = (int(time.time()) << 32) | 0
        with pytest.raises(SecurityError, match="our parity"):
            session.decrypt(from_server(session, msg_id=ours))

    def test_refuses_the_same_message_twice(self):
        # A copy is droppable rather than fatal: the server resends an answer it
        # never saw acknowledged, so this is ordinary traffic, not an attack.
        session = Session(AUTH_KEY)
        frame = from_server(session)
        session.decrypt(frame)
        with pytest.raises(DuplicateMessage, match="already been handled"):
            session.decrypt(frame)
        assert not isinstance(DuplicateMessage(""), SecurityError)

    def test_refuses_a_message_from_the_future(self):
        session = Session(AUTH_KEY, time_offset=_TINY)
        ahead = server_id(time.time() + FUTURE_TOLERANCE + 60)
        with pytest.raises(SecurityError, match="into the future"):
            session.decrypt(from_server(session, msg_id=ahead))

    def test_refuses_a_message_from_the_distant_past(self):
        session = Session(AUTH_KEY, time_offset=_TINY)
        behind = server_id(time.time() - PAST_TOLERANCE - 60)
        with pytest.raises(SecurityError, match="into the past"):
            session.decrypt(from_server(session, msg_id=behind))

    def test_the_time_window_follows_the_offset(self):
        # A server an hour ahead of us is fine once we know it is.
        ahead = server_id(time.time() + 3600)
        session = Session(AUTH_KEY, time_offset=3600.0)
        assert session.decrypt(from_server(session, msg_id=ahead)).body == BODY

    def test_the_first_message_of_a_session_sets_the_clock(self):
        # The trap this avoids: a stored key knows no offset, so on a machine
        # whose clock is out the first message would be refused, and the first
        # message is exactly the bad_msg_notification that says what time it is.
        # Refusing it means never being corrected.
        session = Session(AUTH_KEY)
        assert not session.time_known
        ahead = server_id(time.time() + 3600)
        assert session.decrypt(from_server(session, msg_id=ahead)).body == BODY
        assert session.time_known
        assert 3590 < session.time_offset < 3610

    def test_the_clock_is_only_taken_from_the_first_message(self):
        # Once it is set, the window is enforced against it as before, so a
        # message out of step is still refused rather than moving the clock.
        session = Session(AUTH_KEY)
        session.decrypt(from_server(session, msg_id=server_id(time.time())))
        wild = server_id(time.time() + 86400)
        with pytest.raises(SecurityError, match="into the future"):
            session.decrypt(from_server(session, msg_id=wild))

    def test_a_new_id_is_minted_from_the_clock_just_learned(self):
        session = Session(AUTH_KEY)
        session.decrypt(from_server(session, msg_id=server_id(time.time() + 3600)))
        minted = msg_id_time(session.encrypt(b"\x00" * 4)[0])
        assert minted - time.time() > 3500

    def test_the_time_check_can_be_left_out(self):
        session = Session(AUTH_KEY, check_time=False)
        ancient = server_id(time.time() - 86400)
        assert session.decrypt(from_server(session, msg_id=ancient))

    def test_history_is_bounded_but_still_blocks_a_replay(self):
        session = Session(AUTH_KEY, history=4, check_time=False)
        base = server_id()
        first = base
        for step in range(6):
            session.decrypt(from_server(session, msg_id=base + step * 4))
        # The earliest id has fallen out of the window, and must still not be
        # accepted a second time.
        with pytest.raises(DuplicateMessage, match="older than anything"):
            session.decrypt(from_server(session, msg_id=first))

    def test_out_of_order_ids_inside_the_window_are_fine(self):
        session = Session(AUTH_KEY, history=16, check_time=False)
        base = server_id()
        session.decrypt(from_server(session, msg_id=base + 8))
        assert session.decrypt(from_server(session, msg_id=base + 4))

    def test_the_auth_key_never_stringifies(self):
        session = Session(AUTH_KEY)
        text = repr(session)
        assert AUTH_KEY[:8].hex() not in text
        assert str(list(AUTH_KEY[:8])) not in text
        assert "0x" in text

    def test_the_auth_key_never_reaches_an_error_message(self):
        session = Session(AUTH_KEY)
        broken = bytearray(from_server(session))
        broken[30] ^= 0xFF
        with pytest.raises(SecurityError) as info:
            session.decrypt(bytes(broken))
        assert AUTH_KEY[:8].hex() not in str(info.value)


class TestReceive:
    def test_a_lone_message_comes_back_as_one(self):
        session = Session(AUTH_KEY)
        msg_id = server_id()
        assert session.receive(from_server(session, msg_id=msg_id)) == [
            Message(msg_id, 1, BODY)
        ]

    def test_a_container_is_flattened_and_each_id_checked(self):
        session = Session(AUTH_KEY, check_time=False)
        base = server_id()
        held = [Message(base + 4, 1, BODY), Message(base + 8, 3, BODY)]
        frame = from_server(session, _container(held), msg_id=base, seq_no=0)
        assert session.receive(frame) == held
        # Every id inside went through the checks, so replaying any of them in a
        # later container is caught.
        again = from_server(
            session, _container(held[:1]), msg_id=base + 12, seq_no=0
        )
        assert session.receive(again) == []

    def test_a_container_keeps_the_messages_that_are_new(self):
        session = Session(AUTH_KEY, check_time=False)
        base = server_id()
        first = Message(base + 4, 1, BODY)
        session.receive(from_server(session, _container([first]), msg_id=base, seq_no=0))
        second = Message(base + 12, 1, BODY)
        held = session.receive(
            from_server(session, _container([first, second]), msg_id=base + 8, seq_no=0)
        )
        assert held == [second]

    def test_our_own_parity_inside_a_container_is_still_fatal(self):
        session = Session(AUTH_KEY, check_time=False)
        base = server_id()
        ours = (base >> 32) << 32
        frame = from_server(
            session, _container([Message(ours, 1, BODY)]), msg_id=base, seq_no=0
        )
        with pytest.raises(SecurityError, match="our parity"):
            session.receive(frame)


class TestRecovery:
    def test_adopting_the_server_clock_moves_our_ids(self):
        session = Session(AUTH_KEY)
        session.adopt_server_time(server_id(time.time() + 3600))
        assert 3500 < session.time_offset < 3700
        assert msg_id_time(session.encrypt(BODY)[0]) > time.time() + 3000

    def test_ids_may_come_back_down_when_the_server_says_so(self):
        session = Session(AUTH_KEY, time_offset=3600.0)
        ahead = session.encrypt(BODY)[0]
        # The server refused that id as too high, so obeying means going back.
        session.adopt_server_time(server_id())
        assert session.encrypt(BODY)[0] < ahead

    def test_a_reset_starts_a_new_session_and_keeps_the_key(self):
        session = Session(AUTH_KEY, salt=0x1234)
        session.next_seq_no(content_related=True)
        before = session.session_id
        session.reset()
        assert session.session_id != before
        assert session.salt == 0x1234
        assert session.next_seq_no(content_related=True) == 1
        # The new session still speaks for the same key.
        assert session.decrypt(from_server(session)).body == BODY

    def test_a_reset_forgets_what_the_old_session_had_seen(self):
        session = Session(AUTH_KEY, check_time=False)
        frame = from_server(session)
        session.decrypt(frame)
        session.reset()
        # A different session id, so the same frame no longer addresses us.
        with pytest.raises(SecurityError, match="different session"):
            session.decrypt(frame)
