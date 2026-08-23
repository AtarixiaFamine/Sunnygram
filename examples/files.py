"""Send a file to Saved Messages, then fetch it back and check it survived.

The round trip is the point. Uploading proves the parts go up and the handle
means something; downloading the same file back proves the location, the
datacenter and the file reference all worked, and comparing the bytes proves
nothing was lost or reordered on the way.

    SUNNYGRAM_API_ID=... SUNNYGRAM_API_HASH=... python examples/files.py FILE

Log in first with examples/login.py. Options:

    --keep PATH   where to write the copy that comes back
    --workers N   how many pieces to keep in flight

A file uploaded from one datacenter is often served from another, so the second
half of this quietly signs in to somewhere the account has never been. Watch the
progress lines: the download usually reaches the end sooner than the upload,
because Telegram gives more of itself to sending than to receiving.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import sys
from pathlib import Path

from sunnygram.auth import get_me
from sunnygram.crypto import describe as describe_crypto
from sunnygram.files import download_file, locate, upload_file
from sunnygram.network import ClientInfo, Invoker
from sunnygram.raw import functions, types
from sunnygram.storage import SQLiteStorage

SESSION_FILE = "sunnygram.session"


def bar(what: str) -> object:
    """A progress line that rewrites itself."""

    def report(done: int, total: int) -> None:
        if total:
            share = done / total
            filled = int(share * 30)
            print(
                f"\r  {what} [{'#' * filled}{'.' * (30 - filled)}] "
                f"{share:6.1%} of {total:,} bytes",
                end="",
                flush=True,
            )
        else:
            print(f"\r  {what} {done:,} bytes", end="", flush=True)

    return report


async def main() -> int:
    parser = argparse.ArgumentParser(description="Send a file and get it back.")
    parser.add_argument("file", help="what to upload")
    parser.add_argument("--keep", help="where to write the copy that comes back")
    parser.add_argument("--workers", type=int, default=4, help="pieces in flight")
    parser.add_argument("--session", default=SESSION_FILE, help="the session file")
    arguments = parser.parse_args()

    source = Path(arguments.file)
    if not source.is_file():
        print(f"{source} is not a file", file=sys.stderr)
        return 2

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH first", file=sys.stderr)
        return 2

    invoker = Invoker(
        SQLiteStorage(arguments.session),
        client=ClientInfo(
            api_id=int(api_id), api_hash=api_hash, device_model="Sunnygram example"
        ),
    )
    state = await invoker.start()
    if not state.authorized:
        print("log in first: python examples/login.py", file=sys.stderr)
        await invoker.close()
        return 2

    me = await get_me(invoker)
    print(f"signed in as {me.first_name} (id {me.id}), {describe_crypto()}")
    original = source.read_bytes()
    print(f"{source.name}: {len(original):,} bytes")

    try:
        handle = await upload_file(
            invoker,
            source,
            workers=arguments.workers,
            progress=bar("up  "),
        )
        print()

        sent = await invoker.invoke(
            functions.messages.SendMedia(
                peer=types.InputPeerSelf(),
                media=types.InputMediaUploadedDocument(
                    file=handle,
                    mime_type="application/octet-stream",
                    attributes=[
                        types.DocumentAttributeFilename(file_name=source.name)
                    ],
                ),
                message=f"Sunnygram sent {source.name}",
                random_id=int.from_bytes(os.urandom(8), "little", signed=True),
            )
        )
        document = _document_in(sent)
        if document is None:
            print("the message went out but carried no document back")
            return 1

        found = locate(document)
        print(f"stored as document {found.location.id} in DC {found.dc_id}")

        copy = await download_file(
            invoker,
            document,
            into=arguments.keep,
            workers=arguments.workers,
            progress=bar("down"),
        )
        print()

        returned = Path(copy).read_bytes() if arguments.keep else copy
        assert isinstance(returned, bytes)
        same = hashlib.sha256(returned).digest() == hashlib.sha256(original).digest()
        print(f"{len(returned):,} bytes back, identical: {same}")
        if arguments.keep:
            print(f"written to {arguments.keep}")
        return 0 if same else 1
    finally:
        await invoker.close()


def _document_in(answer: object) -> types.Document | None:
    """The document out of whatever sendMedia answered with."""
    for update in getattr(answer, "updates", []):
        message = getattr(update, "message", None)
        media = getattr(message, "media", None)
        document = getattr(media, "document", None)
        if isinstance(document, types.Document):
            return document
    return None


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
