"""Log in to a real account and print who you are.

The first thing that makes this a client rather than a protocol stack. It signs
in, keeps the session in a file, and on every run after the first it finds the
key already there and asks nobody anything.

    SUNNYGRAM_API_ID=123456 SUNNYGRAM_API_HASH=... python examples/login.py

Both come from my.telegram.org, and the pair identifies the application rather
than the account. Options:

    --qr        approve this login by scanning a code in another client
    --bot       sign in with a bot token instead of a phone number
    --logout    end the session and delete the file
    --export    print the session as a string, for a machine with no disk

The session file is the account. Anyone who can read it is signed in as you, so
it is created readable only by its owner and is worth keeping where a password
would be kept.

This is not part of the test suite, which stays offline. Signing in is the one
thing that cannot be proved without a real account.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from getpass import getpass

from sunnygram.auth import (
    LoginToken,
    SentCode,
    get_me,
    log_in,
    log_out,
    sign_in_qr,
)
from sunnygram.errors import SessionPasswordNeeded
from sunnygram.network import ClientInfo, Invoker
from sunnygram.storage import SQLiteStorage, encode_session

SESSION_FILE = "sunnygram.session"


def ask_for_code(sent: SentCode) -> str:
    where = {
        "app": "in Telegram",
        "sms": "by SMS",
        "call": "by phone call",
        "email": "by email",
    }.get(sent.kind, f"as a {sent.kind} code")
    return input(f"the code sent {where}: ")


def ask_for_password(hint: str) -> str:
    prompt = "two-factor password"
    if hint:
        prompt += f" (hint: {hint})"
    return getpass(f"{prompt}: ")


def show_code(token: LoginToken) -> None:
    print()
    print("open Telegram on a signed-in device, go to")
    print("  Settings > Devices > Link Desktop Device")
    print("and scan a QR code made from this link:")
    print()
    print(f"  {token.url}")
    print()
    print(f"it is good for {token.seconds_left:.0f} seconds")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Log in to Telegram.")
    parser.add_argument("--qr", action="store_true", help="log in by QR code")
    parser.add_argument("--bot", metavar="TOKEN", help="log in as a bot")
    parser.add_argument("--logout", action="store_true", help="end the session")
    parser.add_argument(
        "--export", action="store_true", help="print the session as a string"
    )
    parser.add_argument("--test", action="store_true", help="use the test network")
    parser.add_argument("--session", default=SESSION_FILE, help="where to keep it")
    arguments = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    api_hash = os.environ.get("SUNNYGRAM_API_HASH")
    if not api_id or not api_hash:
        print(
            "set SUNNYGRAM_API_ID and SUNNYGRAM_API_HASH first; both come from "
            "https://my.telegram.org",
            file=sys.stderr,
        )
        return 2

    storage = SQLiteStorage(arguments.session)
    invoker = Invoker(
        storage,
        client=ClientInfo(
            api_id=int(api_id), api_hash=api_hash, device_model="Sunnygram example"
        ),
        test_mode=arguments.test,
    )

    state = await invoker.start()
    print(f"connected to DC {state.dc_id}")
    try:
        if arguments.logout:
            if not state.authorized:
                print("this session was not signed in")
                return 0
            await log_out(invoker)
            print("signed out, and the session file is empty")
            return 0

        if arguments.qr and not state.authorized:
            try:
                user = await sign_in_qr(invoker, show_code)
            except SessionPasswordNeeded:
                from sunnygram.auth import check_password

                user = await check_password(invoker, ask_for_password(""))
        else:
            user = await log_in(
                invoker,
                phone_number=lambda: input("phone number: "),
                code=ask_for_code,
                password=ask_for_password,
                bot_token=arguments.bot,
            )

        name = " ".join(
            part for part in (user.first_name, user.last_name) if part
        )
        print()
        print(f"signed in as {name or 'somebody'}")
        print(f"  id:       {user.id}")
        if user.username:
            print(f"  username: @{user.username}")
        print(f"  bot:      {bool(user.bot)}")

        # Proof the session is usable, not just that the login returned.
        again = await get_me(invoker)
        print(f"  verified: users.getUsers agrees, id {again.id}")
        print()
        print(f"the session is in {storage.path}, so the next run asks nothing")

        if arguments.export:
            print()
            print("session string (treat it exactly like a password):")
            print(f"  {encode_session(invoker.state)}")
    finally:
        await invoker.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
