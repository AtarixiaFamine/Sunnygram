"""Take over a session another library wrote, and prove it is still signed in.

The cheapest possible first run of this library: no phone number, no code, no
second factor. It reads the session file your existing project already has,
writes it into a Sunnygram one, and then connects and asks Telegram who it is,
because a migration that has not made a call has not proved anything.

    SUNNYGRAM_API_ID=123456 SUNNYGRAM_API_HASH=... \
        python examples/adopt.py my_account.session

The argument is a session file, or the session string itself. The format is
detected rather than declared. Options:

    --to NAME   where to write the Sunnygram session (default sunnygram.session)
    --peers no  skip the peer cache and take only the key
    --dry-run   read and report, write nothing

Two things worth knowing before running it against something you care about.

The file you point at is opened read-only and is left exactly as it was, so this
is a copy and going back is always possible.

And an authorization key is one session as far as Telegram is concerned, so two
programs holding the same key are one client with two heads. Running the old
program and this one at the same time will work, in the sense that neither will
break, and both will see every update while each thinks it is alone. Migrate,
then stop the old one.

This is not part of the test suite, which stays offline. tests/test_migrate.py
covers the reading against session files it builds itself; the part that needs a
real account is the last step here, which is the point of the example.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

import sunnygram
from sunnygram.errors import SunnygramError


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="a session file or session string to read")
    parser.add_argument("--to", default="sunnygram.session", help="where to write it")
    parser.add_argument("--peers", default="yes", choices=("yes", "no"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


async def main() -> int:
    options = arguments()

    try:
        imported = sunnygram.read_session(options.source)
    except SunnygramError as error:
        # Worth catching by hand rather than letting it traceback: the usual
        # cause is pointing at the wrong file, and the message says which
        # formats were tried.
        print(f"could not read that: {error}", file=sys.stderr)
        return 1

    print(f"read a {imported.source} session")
    print(f"  datacenter    {imported.state.dc_id}")
    print(f"  peers         {len(imported.peers)}")
    print(f"  who           {imported.state.user_id or 'not recorded, learned on first call'}")

    if options.dry_run:
        print("\ndry run, nothing written")
        return 0

    await sunnygram.adopt_session(imported, options.to, peers=options.peers == "yes")
    print(f"\nwritten to {options.to}, and {options.source} is untouched")

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print("set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH to check it connects")
        return 0

    # The part that actually proves it. Everything above is file formats, which
    # tests can check on their own; only Telegram can say the key still works.
    app = sunnygram.Client(options.to, api_id=int(api_id), api_hash=api_hash)
    async with app:
        me = await app.get_me()
        print(f"connected as {me.first_name} ({me.id}), already signed in")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
