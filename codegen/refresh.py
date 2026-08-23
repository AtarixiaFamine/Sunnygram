"""Vendor the TL schema at a pinned layer, and the error table beside it.

Run this to move Sunnygram to a newer layer. It rewrites the files under
schema/ and the version record beside them, and nothing else in the library
follows upstream on its own: moving layers is a deliberate act that ends in a
commit (rule S5). After running this, regenerate raw/ and errors/ and commit
all of it.

    python codegen/refresh.py --check     # is the pin still the current layer?
    python codegen/refresh.py             # move it to the newest release
    python codegen/refresh.py v7.0.6      # or to a named one
    python codegen/refresh.py --errors    # take the error table and nothing else
    python codegen/gen_tl.py
    python codegen/gen_errors.py

The source is Telegram Desktop's copy of the scheme, which is the one that
records the layer number in a trailing comment. It is taken at a release tag
rather than off the dev branch: the two usually say the same thing, but dev is
where a layer Telegram has not deployed yet appears first, and announcing a
layer no server answers on is worse than being a release behind.

The error table has no such tag. It is one live JSON file that Telegram
regenerates whenever it likes, so it is vendored on its own terms: a copy is
taken with the schema, and --check reports that it moved without failing over
it. A schema behind the newest release is a thing to go and fix; an error
table that gained a line since Tuesday is not.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com/repos/telegramdesktop/tdesktop"
BASE = (
    "https://raw.githubusercontent.com/telegramdesktop/tdesktop"
    "/{ref}/Telegram/SourceFiles/mtproto/scheme"
)
FILES = ("mtproto.tl", "api.tl")
ERRORS_URL = "https://core.telegram.org/api/errors.json"

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
VERSION_FILE = SCHEMA_DIR / "version.json"
ERRORS_FILE = SCHEMA_DIR / "errors.json"
LAYER_PATTERN = re.compile(r"^//\s*LAYER\s+(\d+)", re.MULTILINE)


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sunnygram-codegen",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return str(response.read().decode())


def latest_release() -> str:
    """The tag of the newest published Telegram Desktop release."""
    tag = json.loads(fetch(f"{API}/releases/latest")).get("tag_name")
    if not isinstance(tag, str) or not tag:
        raise SystemExit("the release API answered without a tag name")
    return tag


def find_layer(schema: str) -> int:
    matches = LAYER_PATTERN.findall(schema)
    if not matches:
        raise SystemExit("api.tl carries no LAYER comment, refusing to pin blindly")
    return int(matches[-1])


def schema_at(tag: str) -> dict[str, str]:
    """Both schema files as they stand at a tag.

    Line endings are normalized so the pin does not depend on the checkout, and
    both are fetched before either is written: a refresh that fails halfway
    would otherwise leave schema/ describing two different layers.
    """
    base = BASE.format(ref=tag)
    return {
        name: fetch(f"{base}/{name}").replace("\r\n", "\n") for name in FILES
    }


def fetch_errors() -> str:
    """Telegram's error table, as the bytes it served.

    Kept as text rather than as a parsed object so the recorded hash is of
    something that can be compared byte for byte with what is on disk.
    """
    return fetch(ERRORS_URL).replace("\r\n", "\n")


def errors_record(text: str) -> dict[str, Any]:
    table = json.loads(text)
    return {
        "url": ERRORS_URL,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "layer": table.get("layer"),
        "count": sum(len(names) for names in table["errors"].values()),
    }


def record_for(tag: str, schemas: dict[str, str], errors: str) -> dict[str, Any]:
    return {
        "layer": find_layer(schemas["api.tl"]),
        "release": tag,
        "retrieved": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "files": {
            name: {
                "url": f"{BASE.format(ref=tag)}/{name}",
                "sha256": hashlib.sha256(schemas[name].encode()).hexdigest(),
                "lines": schemas[name].count("\n") + 1,
            }
            for name in FILES
        },
        "errors": errors_record(errors),
    }


def pinned() -> dict[str, Any]:
    return dict(json.loads(VERSION_FILE.read_text(encoding="utf-8")))


def _without(record: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in keys}


def _same(old: dict[str, Any], new: dict[str, Any]) -> bool:
    """Whether two records pin the same thing.

    The date a copy was taken is not part of what it says, so a check that finds
    nothing new does not move it.
    """
    return _without(old, "retrieved") == _without(new, "retrieved")


def _same_pin(old: dict[str, Any], new: dict[str, Any]) -> bool:
    """Whether two records pin the same layer, ignoring the error table.

    The two move for different reasons and only one of them is a release.
    """
    return _without(old, "retrieved", "errors") == _without(new, "retrieved", "errors")


def _same_schema(old: dict[str, Any], new: dict[str, Any]) -> bool:
    """Whether two records pin the same bytes, whatever they name as the source."""

    def hashes(record: dict[str, Any]) -> dict[str, str | None]:
        files = record.get("files", {})
        return {name: files.get(name, {}).get("sha256") for name in FILES}

    return hashes(old) == hashes(new)


def check() -> int:
    """Report whether the pin is still what the newest release carries.

    Non-zero means the schema itself has moved on, which is the answer worth
    failing a job over. A pin that names an older tag but holds identical bytes
    is not behind on anything a server can tell the difference between.
    """
    old = pinned()
    tag = latest_release()
    new = record_for(tag, schema_at(tag), fetch_errors())
    print(f"pinned  layer {old['layer']} from {old.get('release', 'the dev branch')}")
    print(f"newest  layer {new['layer']} from {tag}")

    was, now = old.get("errors", {}), new["errors"]
    if was.get("sha256") == now["sha256"]:
        print(f"the error table is current at {now['count']} errors")
    else:
        moved = now["count"] - int(was.get("count", 0))
        print(f"the error table has changed ({moved:+d} errors); taking it is optional")

    if _same_pin(old, new):
        print("the pin is current")
        return 0
    if _same_schema(old, new):
        print(f"the same schema, recorded against a different source than {tag}")
        return 0
    print("the pin is behind; run codegen/refresh.py, then the two generators")
    return 1


def take_errors() -> int:
    """Take a fresh error table without touching the layer pin.

    The table is not tied to a release, so it is worth being able to follow it
    on its own. The alternative is moving the schema pin to say that Telegram
    documented another error, which is a much bigger thing to do by accident.
    """
    text = fetch_errors()
    record = pinned()
    if record.get("errors", {}).get("sha256") == errors_record(text)["sha256"]:
        print(f"the error table is current at {record['errors']['count']} errors")
        return 0

    record["errors"] = errors_record(text)
    record["retrieved"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    SCHEMA_DIR.mkdir(exist_ok=True)
    ERRORS_FILE.write_text(text, encoding="utf-8", newline="\n")
    VERSION_FILE.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"took {record['errors']['count']} errors; now run codegen/gen_errors.py")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--check":
        return check()
    if argv and argv[0] == "--errors":
        return take_errors()

    tag = argv[0] if argv else latest_release()
    schemas = schema_at(tag)
    errors = fetch_errors()
    new = record_for(tag, schemas, errors)
    if VERSION_FILE.exists() and ERRORS_FILE.exists() and _same(pinned(), new):
        print(f"already pinned to layer {new['layer']} from {tag}, nothing written")
        return 0

    SCHEMA_DIR.mkdir(exist_ok=True)
    for name, text in schemas.items():
        (SCHEMA_DIR / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"{name}: {len(text)} bytes")
    ERRORS_FILE.write_text(errors, encoding="utf-8", newline="\n")
    print(f"errors.json: {new['errors']['count']} errors")
    VERSION_FILE.write_text(
        json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"pinned layer {new['layer']} from {tag}; now run the two generators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
