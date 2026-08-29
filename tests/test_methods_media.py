"""Deciding what a file is, before any of it goes anywhere.

All of this is guessing from a name, which is worth testing on its own because
the guess is what decides whether a video plays in place or arrives as a file
somebody has to download first. None of it touches the network.
"""

from __future__ import annotations

import io

import pytest

from sunnygram.methods import as_media, existing_media, kind_of, name_of
from sunnygram.methods.attachments import with_reference
from sunnygram.raw import types

HANDLE = types.InputFile(id=1, parts=1, name="x", md5_checksum="")


class TestNaming:
    def test_a_name_given_by_hand_wins(self):
        assert name_of("photo.jpg", "other.png") == "other.png"

    def test_a_path_carries_its_own(self):
        assert name_of("/tmp/holiday/photo.jpg") == "photo.jpg"

    def test_an_open_file_remembers_where_it_came_from(self, tmp_path):
        picture = tmp_path / "cat.png"
        picture.write_bytes(b"x")
        with picture.open("rb") as handle:
            assert name_of(handle) == "cat.png"

    def test_bytes_have_no_name(self):
        assert name_of(b"just bytes") is None
        assert name_of(io.BytesIO(b"just bytes")) is None


class TestKinds:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("holiday.jpg", "photo"),
            ("holiday.JPEG", "photo"),
            ("drawing.png", "photo"),
            # Image shaped, but Telegram refuses both as a photo.
            ("sticker.webp", "document"),
            ("scan.bmp", "document"),
            ("clip.mp4", "video"),
            ("clip.MKV", "video"),
            ("cat.gif", "animation"),
            ("song.mp3", "audio"),
            ("song.flac", "audio"),
            ("report.pdf", "document"),
            ("archive.tar.gz", "document"),
            ("no_extension", "document"),
        ],
    )
    def test_the_extension_decides(self, name, expected):
        assert kind_of(name) == expected

    def test_nothing_to_go_on_means_a_document(self):
        assert kind_of(None) == "document"

    def test_asking_for_a_kind_overrides_the_guess(self):
        assert kind_of("holiday.jpg", "document") == "document"
        assert kind_of("report.pdf", "photo") == "photo"

    def test_a_kind_that_does_not_exist_is_refused(self):
        with pytest.raises(ValueError):
            kind_of("holiday.jpg", "hologram")


class TestDescribing:
    def test_a_photo_is_a_photo_and_carries_no_attributes(self):
        media = as_media(HANDLE, "photo", name="holiday.jpg")
        assert isinstance(media, types.InputMediaUploadedPhoto)

    def test_a_document_says_it_must_not_be_re_encoded(self):
        # Otherwise Telegram turns a picture sent as a file back into a photo,
        # which is exactly what the sender was avoiding.
        media = as_media(HANDLE, "document", name="holiday.jpg")
        assert media.force_file

    def test_a_video_that_is_not_a_document_is_not_forced(self):
        assert not as_media(HANDLE, "video", name="clip.mp4").force_file

    def test_an_animation_is_a_video_that_says_it_is_one(self):
        # The animated attribute is the whole difference. Without it the same
        # bytes arrive as an ordinary video with a mute button on it.
        media = as_media(HANDLE, "animation", name="cat.mp4")
        kinds = [type(one).__name__ for one in media.attributes]
        assert "DocumentAttributeAnimated" in kinds
        assert media.attributes[0].nosound
        assert media.mime_type == "video/mp4"

    def test_a_video_is_not_marked_animated(self):
        media = as_media(HANDLE, "video", name="clip.mp4")
        kinds = [type(one).__name__ for one in media.attributes]
        assert "DocumentAttributeAnimated" not in kinds
        assert not media.attributes[0].nosound

    def test_a_video_carries_its_shape(self):
        media = as_media(
            HANDLE, "video", name="clip.mp4", duration=12, width=640, height=480
        )
        video = media.attributes[0]
        assert isinstance(video, types.DocumentAttributeVideo)
        assert (video.duration, video.w, video.h) == (12, 640, 480)
        assert video.supports_streaming

    def test_a_voice_note_is_an_audio_that_says_so(self):
        media = as_media(HANDLE, "voice", name="note.ogg", duration=5)
        audio = media.attributes[0]
        assert isinstance(audio, types.DocumentAttributeAudio)
        assert audio.voice and audio.duration == 5

    def test_a_track_keeps_its_title_and_performer(self):
        media = as_media(
            HANDLE, "audio", name="song.mp3", title="A Song", performer="Somebody"
        )
        audio = media.attributes[0]
        assert not audio.voice
        assert (audio.title, audio.performer) == ("A Song", "Somebody")

    def test_the_filename_comes_last(self):
        # Telegram reads the list in order, and a client showing the name
        # should not talk the one before it out of being a video.
        media = as_media(HANDLE, "video", name="clip.mp4")
        assert isinstance(media.attributes[-1], types.DocumentAttributeFilename)
        assert media.attributes[-1].file_name == "clip.mp4"

    @pytest.mark.parametrize(
        "name,kind,expected",
        [
            ("report.pdf", "document", "application/pdf"),
            ("clip.mp4", "video", "video/mp4"),
            ("song.mp3", "audio", "audio/mpeg"),
            (None, "voice", "audio/ogg"),
            (None, "document", "application/octet-stream"),
        ],
    )
    def test_the_content_type_is_guessed_or_defaulted(self, name, kind, expected):
        assert as_media(HANDLE, kind, name=name).mime_type == expected

    def test_a_content_type_given_by_hand_wins(self):
        media = as_media(HANDLE, "document", name="thing.bin", mime_type="text/csv")
        assert media.mime_type == "text/csv"


class TestPointingAtWhatAlreadyExists:
    """Re-sending is the cheap half, and recognising the shapes is all of it."""

    DOCUMENT = types.Document(
        id=9,
        access_hash=7,
        file_reference=b"ref",
        date=0,
        mime_type="video/mp4",
        size=10,
        dc_id=2,
        attributes=[],
    )
    PHOTO = types.Photo(
        id=1, access_hash=2, file_reference=b"ref", date=0, sizes=[], dc_id=2
    )

    def test_a_document_off_a_message(self):
        found = existing_media(types.MessageMediaDocument(document=self.DOCUMENT))
        assert isinstance(found, types.InputMediaDocument)
        assert found.id.id == 9 and found.id.file_reference == b"ref"

    def test_a_photo_off_a_message(self):
        found = existing_media(types.MessageMediaPhoto(photo=self.PHOTO))
        assert isinstance(found, types.InputMediaPhoto)
        assert found.id.id == 1

    def test_the_bare_document_and_photo_too(self):
        assert isinstance(existing_media(self.DOCUMENT), types.InputMediaDocument)
        assert isinstance(existing_media(self.PHOTO), types.InputMediaPhoto)

    def test_an_input_media_is_passed_straight_through(self):
        already = types.InputMediaDocument(
            id=types.InputDocument(id=9, access_hash=7, file_reference=b"ref")
        )
        assert existing_media(already) is already

    def test_a_path_is_not_one_and_says_nothing_rather_than_raising(self):
        # Nothing rather than an error, so a caller can offer both this and an
        # upload without knowing in advance which it was handed.
        assert existing_media("holiday.jpg") is None
        assert existing_media(b"bytes") is None
        assert existing_media(types.MessageMediaEmpty()) is None

    def test_hiding_is_asked_for_at_the_send(self):
        # Hiding belongs to the send rather than to the file, so the same
        # document goes out plain once and covered the next time.
        plain = existing_media(self.DOCUMENT)
        covered = existing_media(self.DOCUMENT, spoiler=True)
        assert plain.spoiler is False
        assert covered.spoiler is True
        assert covered.id.id == 9 and covered.id.file_reference == b"ref"

    def test_a_photo_hides_too(self):
        assert existing_media(self.PHOTO, spoiler=True).spoiler is True

    def test_hiding_a_caller_owned_media_copies_rather_than_marks_it(self):
        # The media may be the caller's own object and a send is not entitled
        # to change it, so the one handed back is a different object and the
        # one passed in is exactly as it was.
        already = types.InputMediaDocument(
            id=types.InputDocument(id=9, access_hash=7, file_reference=b"ref"),
            ttl_seconds=30,
        )
        covered = existing_media(already, spoiler=True)
        assert covered is not already
        assert already.spoiler is False
        assert covered.spoiler is True
        # Everything else it carried comes across, or hiding a file would
        # quietly drop the rest of what was said about it.
        assert covered.ttl_seconds == 30
        assert covered.id is already.id

    def test_a_media_built_hidden_stays_hidden(self):
        already = types.InputMediaPhoto(
            id=types.InputPhoto(id=1, access_hash=2, file_reference=b"ref"),
            spoiler=True,
        )
        assert existing_media(already) is already

    def test_renewal_swaps_the_token_and_keeps_everything_else(self):
        # What a retry is allowed to change. Sending the freshly fetched media
        # instead is the obvious thing and it drops every one of these, because
        # they describe the send and the file has never heard of them.
        asked = types.InputMediaDocument(
            id=types.InputDocument(id=9, access_hash=7, file_reference=b"old"),
            spoiler=True,
            ttl_seconds=45,
            video_timestamp=12,
        )
        fresh = types.InputMediaDocument(
            id=types.InputDocument(id=9, access_hash=7, file_reference=b"fresh")
        )
        renewed = with_reference(asked, fresh)
        assert renewed.id.file_reference == b"fresh"
        assert renewed.spoiler is True
        assert renewed.ttl_seconds == 45
        assert renewed.video_timestamp == 12
        # A copy: the one being carried through the retry may be the caller's.
        assert renewed is not asked
        assert asked.id.file_reference == b"old"

    def test_a_photo_keeps_its_own_fields_through_renewal(self):
        asked = types.InputMediaPhoto(
            id=types.InputPhoto(id=1, access_hash=2, file_reference=b"old"),
            spoiler=True,
            ttl_seconds=30,
        )
        fresh = types.InputMediaPhoto(
            id=types.InputPhoto(id=1, access_hash=2, file_reference=b"fresh")
        )
        renewed = with_reference(asked, fresh)
        assert renewed.id.file_reference == b"fresh"
        assert renewed.spoiler is True and renewed.ttl_seconds == 30

    def test_a_message_carrying_a_different_kind_of_file_now(self):
        # Nothing to preserve: the message no longer carries what was asked
        # for, so what comes back is what is actually there.
        asked = types.InputMediaPhoto(
            id=types.InputPhoto(id=1, access_hash=2, file_reference=b"old"),
            spoiler=True,
        )
        fresh = types.InputMediaDocument(
            id=types.InputDocument(id=9, access_hash=7, file_reference=b"fresh")
        )
        assert with_reference(asked, fresh) is fresh
