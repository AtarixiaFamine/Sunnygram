# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sending something that is not only text.

Every one of these is the same three steps: put the bytes up, describe what
they are, and send a message carrying that description. The first step is the
file engine's job and the third is the same call that sends text. What is left,
and what this module is, is the middle one: turning a path into the handful of
attributes Telegram wants alongside it.

The description matters more than it looks. The same bytes sent as a photo, a
document, a video and a voice note are four different things on the other side,
and which one it is comes down to the attributes attached here instead of to
anything in the file. Get them wrong and a video arrives as a file no one can
play in place.
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any

from ..raw import base, types

__all__ = [
    "KINDS",
    "as_media",
    "kind_of",
    "name_of",
]

# What a caller can ask for, and what each one means on the other side.
KINDS = ("auto", "photo", "video", "animation", "audio", "voice", "document")

# The only two Telegram accepts as a photo. Anything else image shaped goes as
# a document, webp and bmp included: webp is the format a sticker is made of,
# and an upload that calls either of them a photo comes back PHOTO_EXT_INVALID.
# What it does accept it re-encodes, stripping whatever it does not need, so
# anything a caller wants back byte for byte belongs in a document as well.
_PHOTO_TYPES = frozenset({".jpg", ".jpeg", ".png"})
_VIDEO_TYPES = frozenset({".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"})
_AUDIO_TYPES = frozenset({".mp3", ".m4a", ".flac", ".wav", ".aac", ".opus"})
# A gif is not a gif on Telegram. It is a soundless mp4 marked as animated, and
# a real .gif is converted into one on arrival, so both names land here.
_ANIMATION_TYPES = frozenset({".gif"})

_DEFAULT_TYPE = "application/octet-stream"


def name_of(source: Any, given: str | None = None) -> str | None:
    """What to call the file on the other side.

    A name given explicitly wins. Failing that, a path has one, and an open
    file usually remembers the path it came from. Bytes have nothing, and the
    upload gives those a name of their own instead of guessing here.
    """
    if given is not None:
        return given
    if isinstance(source, (str, os.PathLike)):
        return Path(os.fspath(source)).name
    found = getattr(source, "name", None)
    return Path(str(found)).name if isinstance(found, (str, os.PathLike)) else None


def kind_of(name: str | None, asked: str = "auto") -> str:
    """Which of the five kinds to send this as.

    Only the extension is consulted, deliberately. Reading the first bytes of a
    file to decide would be more accurate and would mean touching a stream this
    module was not given, and being wrong here costs a caller one argument.
    """
    if asked not in KINDS:
        raise ValueError(f"{asked!r} is not one of {', '.join(KINDS)}")
    if asked != "auto":
        return asked
    if name is None:
        return "document"
    suffix = Path(name).suffix.lower()
    if suffix in _PHOTO_TYPES:
        return "photo"
    if suffix in _ANIMATION_TYPES:
        return "animation"
    if suffix in _VIDEO_TYPES:
        return "video"
    if suffix in _AUDIO_TYPES:
        return "audio"
    return "document"


def as_media(
    handle: base.InputFile,
    kind: str,
    *,
    name: str | None = None,
    mime_type: str | None = None,
    thumb: base.InputFile | None = None,
    duration: float = 0,
    width: int = 0,
    height: int = 0,
    title: str | None = None,
    performer: str | None = None,
    streaming: bool = True,
    spoiler: bool = False,
    ttl_seconds: int | None = None,
) -> base.InputMedia:
    """Describe an uploaded file as the kind of thing it is meant to be."""
    if kind == "photo":
        return types.InputMediaUploadedPhoto(
            file=handle, spoiler=spoiler, ttl_seconds=ttl_seconds
        )

    attributes: list[base.DocumentAttribute] = []
    if kind in ("video", "animation"):
        attributes.append(
            types.DocumentAttributeVideo(
                duration=float(duration),
                w=width,
                h=height,
                supports_streaming=streaming,
                # An animation has no sound by definition, and saying so is
                # what makes a client loop it in place instead of offering it
                # as a video with a mute button.
                nosound=kind == "animation",
            )
        )
        if kind == "animation":
            # This attribute is the whole difference between a short video and
            # a gif. Without it the same bytes arrive as an ordinary video.
            attributes.append(types.DocumentAttributeAnimated())
    elif kind in ("audio", "voice"):
        attributes.append(
            types.DocumentAttributeAudio(
                duration=int(duration),
                voice=kind == "voice",
                title=title,
                performer=performer,
            )
        )
    if name is not None:
        # Last, because Telegram reads the list in order and a client showing
        # the filename wants the kind it already decided on to stand.
        attributes.append(types.DocumentAttributeFilename(file_name=name))

    return types.InputMediaUploadedDocument(
        file=handle,
        thumb=thumb,
        mime_type=mime_type or _mime_for(name, kind),
        attributes=attributes,
        # A photo sent as a document is a photo someone wanted kept as it is,
        # so it must not be re-encoded back into one on arrival.
        force_file=kind == "document",
        spoiler=spoiler,
        ttl_seconds=ttl_seconds,
    )


def _mime_for(name: str | None, kind: str) -> str:
    """The content type to declare, guessed from the name and the kind."""
    if name is not None:
        guessed, _ = mimetypes.guess_type(name)
        if guessed:
            return guessed
    if kind == "voice":
        return "audio/ogg"
    if kind in ("video", "animation"):
        return "video/mp4"
    if kind == "audio":
        return "audio/mpeg"
    return _DEFAULT_TYPE
