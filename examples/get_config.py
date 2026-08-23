"""Call help.getConfig against a real datacenter.

The first thing this library does over a live connection, and the smallest one
worth doing: no account, no login, nothing stored. It negotiates an
authorization key, introduces itself, asks for the configuration, and prints
what came back.

    SUNNYGRAM_API_ID=123456 python examples/get_config.py

The api_id comes from my.telegram.org and is what initConnection needs to accept
the connection at all. Add --test to talk to Telegram's test datacenters
instead, which is the friendlier place to point a new stack at.

This is not part of the test suite. The suite is offline by design, so the one
thing it cannot prove is that a real server agrees with us.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from sunnygram.network import ClientInfo, connect
from sunnygram.raw import functions, types


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dc", type=int, default=2, help="which datacenter to ask")
    parser.add_argument(
        "--test", action="store_true", help="use the test datacenters"
    )
    parser.add_argument("--ipv6", action="store_true", help="connect over IPv6")
    arguments = parser.parse_args()

    api_id = os.environ.get("SUNNYGRAM_API_ID")
    if not api_id:
        print(
            "set SUNNYGRAM_API_ID first; get one from https://my.telegram.org",
            file=sys.stderr,
        )
        return 2

    print(f"connecting to DC {arguments.dc}{' (test)' if arguments.test else ''}")
    connection = await connect(
        arguments.dc,
        test=arguments.test,
        ipv6=arguments.ipv6,
        client=ClientInfo(api_id=int(api_id)),
    )
    print(f"connected: {connection}")

    try:
        config = await connection.invoke(functions.help.GetConfig())
        if not isinstance(config, types.Config):
            print(f"the server answered with {type(config).__name__}")
            return 1

        print(f"this dc:      {config.this_dc}")
        print(f"test mode:    {config.test_mode}")
        print(f"expires:      {config.expires}")
        print(f"chat size:    up to {config.chat_size_max} members")
        print(f"caption size: up to {config.caption_length_max} characters")
        print(f"dc options:   {len(config.dc_options)}")
        for option in config.dc_options:
            kind = "".join(
                letter
                for letter, flag in (
                    ("6", option.ipv6),
                    ("m", option.media_only),
                    ("c", option.cdn),
                    ("s", option.static),
                )
                if flag
            )
            print(f"  dc{option.id:<3} {option.ip_address}:{option.port} {kind}")

        # A second call, to show the connection stays usable and does not
        # introduce itself twice.
        nearest = await connection.invoke(functions.help.GetNearestDc())
        print(f"nearest:      dc{nearest.nearest_dc} (you look like {nearest.country})")
        print(f"dropped updates:      {connection.dropped_updates}")
        print(f"unknown constructors: {connection.unknown_constructors}")
    finally:
        await connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
