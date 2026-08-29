# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Moving files, in both directions.

The two halves are not symmetrical. Uploading is a stream of parts under an id
the client invents, and produces a handle that is only good for the one send
that follows. Downloading is a location, a datacenter that may not be home, and
a token that goes stale, and produces bytes or a file on disk. It also has a
third party in it: a popular file is held by a content delivery network rather
than by Telegram, encrypted, and cdn.py is what opens it and checks it.

What they share is the shape: pieces of half a megabyte, several in flight at
once, and progress reported as they land.

Alongside both is ref.py, which is neither: it turns a file into one string that
can be written down and read back, so that sending something again next week
costs a call instead of a round trip through this machine.
"""

from __future__ import annotations

from .cdn import CdnSession
from .download import Progress, Refresh, download_file, stream_file
from .location import FileSource, locate
from .parts import DOWNLOAD_CHUNK, UPLOAD_PART, WORKERS
from .ref import FileRef, decode_ref, file_ref, parse_ref
from .upload import upload_file

__all__ = [
    "CdnSession",
    "DOWNLOAD_CHUNK",
    "FileRef",
    "FileSource",
    "Progress",
    "Refresh",
    "UPLOAD_PART",
    "WORKERS",
    "decode_ref",
    "download_file",
    "file_ref",
    "locate",
    "parse_ref",
    "stream_file",
    "upload_file",
]
