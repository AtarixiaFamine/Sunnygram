"""A program whose features live in their own files.

    SUNNYGRAM_API_ID=123456 SUNNYGRAM_API_HASH=... \
        python examples/plugin_bot.py

Everything this program does is in examples/plugins/, and this file does not
import any of it by name. It says where to look, and the loader imports the
package and registers what it finds.

Worth reading the count it prints. A package whose handlers were written
without the decorators registers nothing at all, and a program that answers
nobody looks exactly like a program with nothing to answer, which is why the
number is returned rather than kept.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from sunnygram import Client


async def main() -> int:
    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH", file=sys.stderr)
        return 1

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    app = Client("sunnygram.session", api_id=int(api_id), api_hash=api_hash)
    registered = app.load_plugins("examples.plugins")
    print(f"{registered} handlers loaded. Say /hello or anything else.")

    async with app:
        await asyncio.Event().wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
