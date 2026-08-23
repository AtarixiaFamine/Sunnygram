"""Writing a file down, and reading it back.

The reference is the one thing in this library that is meant to outlive the
process that made it, so the tests are about two things: that what goes in comes
back out unchanged, and that anything which is not a reference fails as one
rather than becoming a request for some other file. The second matters more. A
string that has been truncated in a database column or had a character eaten by
a URL must not decode into a location, and the checksum is what makes sure it
does not.
"""

from __future__ import annotations

import pytest

from sunnygram.errors import SunnygramError
from sunnygram.files import FileRef, decode_ref, file_ref, locate, parse_ref
from sunnygram.methods import existing_media, media_origin
from sunnygram.raw import types

CHANNEL = 1234567
MARKED = -1_000_000_000_000 - CHANNEL


def a_document(**fields) -> types.Document:
    return types.Document(
        id=fields.pop("id", -948_372_615_243),
        access_hash=fields.pop("access_hash", 87_654_321),
        file_reference=fields.pop("file_reference", b"\x01\x02\x03\xff\x00"),
        date=0,
        mime_type="audio/mpeg",
        size=fields.pop("size", 5_123_456),
        dc_id=fields.pop("dc_id", 4),
        attributes=[types.DocumentAttributeFilename(file_name="song.mp3")],
        **fields,
    )


def a_photo() -> types.Photo:
    return types.Photo(
        id=777_888_999,
        access_hash=111_222_333,
        file_reference=b"\xaa\xbb",
        date=0,
        sizes=[types.PhotoSize(type="y", w=1280, h=720, size=90_000)],
        dc_id=2,
    )


def a_message(media, id: int = 77) -> types.Message:
    return types.Message(
        id=id,
        peer_id=types.PeerChannel(channel_id=CHANNEL),
        date=0,
        message="",
        media=media,
    )


class TestRoundTrip:
    def test_a_document_comes_back_the_same(self):
        document = a_document()
        found = decode_ref(file_ref(document))
        assert found.id == document.id
        assert found.access_hash == document.access_hash
        assert found.file_reference == document.file_reference
        assert found.dc_id == 4
        assert found.size == document.size
        assert found.name == "song.mp3"

    def test_a_photo_keeps_which_rendition_it_named(self):
        found = decode_ref(file_ref(a_photo()))
        assert found.is_photo
        assert found.thumb == "y"
        assert found.dc_id == 2

    def test_encoding_it_again_gives_the_same_string(self):
        text = file_ref(a_document())
        assert decode_ref(text).encode() == text
        assert str(decode_ref(text)) == text

    def test_a_thumbnail_is_a_reference_of_its_own(self):
        photo = a_photo()
        photo.sizes.append(types.PhotoSize(type="m", w=320, h=180, size=9_000))
        found = decode_ref(file_ref(photo, thumb="m"))
        assert found.thumb == "m"
        assert found.size == 9_000

    def test_it_is_shorter_than_a_line(self):
        # Nothing depends on this, but a reference is going into database
        # columns and log lines, so it is worth noticing if it ever grows.
        assert len(file_ref(a_document())) < 120


class TestWhatItBecomes:
    def test_a_document_becomes_something_a_send_can_carry(self):
        media = decode_ref(file_ref(a_document())).media
        assert isinstance(media, types.InputMediaDocument)
        assert media.id.access_hash == 87_654_321

    def test_a_photo_becomes_the_other_kind(self):
        assert isinstance(decode_ref(file_ref(a_photo())).media, types.InputMediaPhoto)

    def test_it_becomes_something_the_download_engine_can_fetch(self):
        source = decode_ref(file_ref(a_document())).source
        assert isinstance(source.location, types.InputDocumentFileLocation)
        assert source.dc_id == 4
        assert source.name == "song.mp3"

    def test_locate_takes_the_string_itself(self):
        source = locate(file_ref(a_document()))
        assert source.size == 5_123_456

    def test_send_media_takes_the_string_itself(self):
        media = existing_media(file_ref(a_document()))
        assert isinstance(media, types.InputMediaDocument)

    def test_a_hidden_send_keeps_the_origin_that_renews_it(self):
        # The two halves of re-sending have to compose. Hiding is read off the
        # send and the origin is read off the string, so asking for a covered
        # send does not cost the reference the thing that renews it when it has
        # gone stale. Reading hiding off the media instead would, since a media
        # says nothing about which message it came from.
        message = a_message(types.MessageMediaDocument(document=a_document()))
        written = file_ref(message)
        covered = existing_media(written, spoiler=True)
        assert isinstance(covered, types.InputMediaDocument)
        assert covered.spoiler is True
        assert media_origin(written) == (MARKED, 77)


class TestWhereItCameFrom:
    def test_a_message_names_itself(self):
        message = a_message(types.MessageMediaDocument(document=a_document()))
        assert decode_ref(file_ref(message)).origin == (MARKED, 77)

    def test_the_origin_can_be_left_out(self):
        message = a_message(types.MessageMediaDocument(document=a_document()))
        assert decode_ref(file_ref(message, origin=False)).origin is None

    def test_a_document_on_its_own_has_no_origin(self):
        assert decode_ref(file_ref(a_document())).origin is None

    def test_the_origin_survives_the_string(self):
        message = a_message(types.MessageMediaPhoto(photo=a_photo()), id=99)
        assert media_origin(file_ref(message)) == (MARKED, 99)

    def test_a_message_gives_its_origin_directly(self):
        message = a_message(types.MessageMediaDocument(document=a_document()))
        assert media_origin(message) == (MARKED, 77)

    def test_something_that_is_not_a_message_has_none(self):
        assert media_origin(a_document()) is None


class TestRefusingWhatIsNotOne:
    @pytest.mark.parametrize(
        "text",
        [
            "",
            "photo.jpg",
            "/home/somebody/a file.mp4",
            "https://example.invalid/thing",
            "not base64 at all !!",
        ],
    )
    def test_an_ordinary_string_is_not_a_reference(self, text):
        assert parse_ref(text) is None
        # Which is what lets send_file and send_media tell a path from a
        # reference without the caller having to say which they hold.
        assert existing_media(text) is None

    def test_a_truncated_reference_is_refused(self):
        text = file_ref(a_document())
        assert parse_ref(text[:-4]) is None

    def test_a_reference_with_a_character_changed_is_refused(self):
        text = file_ref(a_document())
        swapped = ("A" if text[8] != "A" else "B") + text[9:]
        assert parse_ref(text[:8] + swapped) is None

    def test_decoding_one_explains_itself(self):
        with pytest.raises(SunnygramError, match="not a Sunnygram file reference"):
            decode_ref("nonsense")

    def test_locate_says_so_too(self):
        with pytest.raises(SunnygramError, match="not a Sunnygram file reference"):
            locate("nonsense")

    def test_a_future_version_is_not_read_as_this_one(self):
        made = FileRef(
            kind=1, id=1, access_hash=2, file_reference=b"\x00", dc_id=2
        ).encode()
        import base64

        packed = bytearray(base64.urlsafe_b64decode(made + "=" * (-len(made) % 4)))
        packed[0] = 99
        ahead = base64.urlsafe_b64encode(bytes(packed)).rstrip(b"=").decode()
        # The checksum catches it first, which is the same answer: not one of
        # ours, so nothing is believed about it.
        assert parse_ref(ahead) is None

    def test_something_with_no_file_in_it_says_so(self):
        with pytest.raises(SunnygramError, match="no file"):
            file_ref(a_message(None))
