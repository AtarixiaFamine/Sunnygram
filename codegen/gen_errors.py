"""Emit the generated error tree from the vendored error table.

    python codegen/gen_errors.py

Telegram publishes every error it can answer with, what each one means, and
which methods raise it. That is a table, so it is generated: one class per
error, hanging off the class for its status code, with the published
explanation as its docstring.

Two things the table does not say cleanly, and how they are settled here.

An error is not tied to one status code. PEER_ID_INVALID arrives as a 400 from
two hundred methods and as a 403 from one, and a class has one base, so the
base is the code that answers with it most often. The code on the instance is
always the one the server actually sent, so the number is never a lie even when
the class it landed in implies another one.

The values in an error are written %d, and the same error is sometimes listed
both with and without one: FILE_REFERENCE_%d_EXPIRED and
FILE_REFERENCE_EXPIRED are one thing said twice. Those collapse into a single
class that answers to both spellings, and the one carrying a number fills in
value. Nothing under errors/ is hand-edited (rule H7); tests/test_codegen.py
fails if the tree on disk is not what this script produces.
"""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
from typing import Any

import overrides

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
ERRORS_FILE = SCHEMA_DIR / "errors.json"
VERSION_FILE = SCHEMA_DIR / "version.json"
OUT_FILE = (
    Path(__file__).resolve().parents[1] / "src" / "sunnygram" / "errors" / "generated.py"
)

# The class each status code hangs its errors off, all hand-written in rpc.py.
# 303 is a redirection rather than a failure and 420 is the whole flood family,
# which is why neither is spelled as a plain number anywhere else.
BASES = {
    "303": "Migrate",
    "400": "BadRequest",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "NotFound",
    "406": "NotAcceptable",
    "420": "Flood",
    "500": "InternalError",
    "-503": "Timeout",
}

# How a tie is broken when an error is listed under several codes by the same
# number of methods. Most specific first: a 401 says more than a 400 does.
CODE_ORDER = ("401", "403", "404", "406", "420", "303", "-503", "500", "400")

LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
ENTITY = {"&raquo;": "»", "&laquo;": "«", "&amp;": "&", "&lt;": "<", "&gt;": ">"}
VALUE = re.compile(r"%d")


def wire_names(table: dict[str, dict[str, list[str]]]) -> dict[str, dict[str, int]]:
    """Every error name, mapped to how many methods raise it under each code."""
    found: dict[str, dict[str, int]] = {}
    for code, errors in table.items():
        for name, methods in errors.items():
            found.setdefault(name, {})[code] = len(methods)
    return found


def class_name(name: str) -> str:
    """PEER_ID_INVALID to PeerIdInvalid, and the value marker is not a word."""
    named = overrides.ERROR_CLASS_NAMES.get(name)
    if named is not None:
        return named
    parts = [part for part in name.replace("%d", "").split("_") if part]
    return "".join(part[:1].upper() + part[1:].lower() for part in parts)


def primary_code(codes: dict[str, int]) -> str:
    """The code an error mostly arrives with, ties broken by specificity."""
    return min(codes, key=lambda code: (-codes[code], CODE_ORDER.index(code)))


def describe(text: str) -> str:
    """The published explanation, as prose a docstring can hold.

    The table is written for a web page, so it carries markdown links, HTML
    entities and the odd stray full stop. A link's text survives and its URL
    does not: a docstring is read where the link cannot be followed.
    """
    text = LINK.sub(r"\1", text)
    for entity, character in ENTITY.items():
        text = text.replace(entity, character)
    text = re.sub(r"\s+", " ", text).strip()
    # The table is written by hand, so a fair few entries end in a stray full
    # stop after the real one. Two of those meeting in a merged class would
    # read as an ellipsis nobody wrote.
    text = re.sub(r"[.\s]+$", ".", text)
    return text.replace("\\", "\\\\").replace('"""', "'''")


def docstring(description: str, indent: str = "    ") -> list[str]:
    """A docstring on one line if it fits, wrapped over several if it does not."""
    if not description:
        description = "No description published."
    if len(indent) + len(description) + 6 <= 88:
        return [f'{indent}"""{description}"""']
    # The opening quotes sit on the first line and count towards its width,
    # which is what initial_indent is for. Everything after them is prose.
    body = textwrap.wrap(description, width=88 - len(indent), initial_indent='"""')
    return [
        *(f"{indent}{line}" for line in body),
        f'{indent}"""',
    ]


def pattern_for(name: str) -> str:
    """The regex matching one spelling of an error that carries a number."""
    parts = [re.escape(part) for part in VALUE.split(name)]
    return "^" + r"(-?\d+)".join(parts) + "$"


def entry(one_line: str, *split: str) -> list[str]:
    """A table entry, written over several lines only if it is too long for one."""
    return [one_line] if len(one_line) <= 88 else list(split)


class Error:
    """One class to emit, and every wire name that should reach it."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.spellings: list[str] = []
        self.codes: dict[str, int] = {}
        self.descriptions: list[str] = []

    def add(self, spelling: str, codes: dict[str, int], description: str) -> None:
        self.spellings.append(spelling)
        for code, count in codes.items():
            self.codes[code] = self.codes.get(code, 0) + count
        if description and description not in self.descriptions:
            self.descriptions.append(description)

    @property
    def base(self) -> str:
        for spelling in self.spellings:
            chosen = overrides.ERROR_BASES.get(spelling)
            if chosen is not None:
                return chosen
        return BASES[primary_code(self.codes)]

    @property
    def hand_written(self) -> bool:
        return any(s in overrides.ERROR_HAND_WRITTEN for s in self.spellings)

    @property
    def exact(self) -> list[str]:
        return sorted(s for s in self.spellings if "%d" not in s)

    @property
    def valued(self) -> list[str]:
        return sorted(s for s in self.spellings if "%d" in s)


def collect() -> list[Error]:
    table: dict[str, Any] = json.loads(ERRORS_FILE.read_text(encoding="utf-8"))
    descriptions: dict[str, str] = table["descriptions"]
    errors: dict[str, Error] = {}
    for spelling, codes in sorted(wire_names(table["errors"]).items()):
        name = class_name(spelling)
        errors.setdefault(name, Error(name)).add(
            spelling, codes, describe(descriptions.get(spelling, ""))
        )
    return [errors[name] for name in sorted(errors)]


def emit(errors: list[Error]) -> str:
    record = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    layer = record["errors"]["layer"]
    generated = [error for error in errors if not error.hand_written]
    # Only what the emitted classes and the tables actually name. A base that
    # every one of its errors turns out to be hand-written is not imported.
    bases = {error.base for error in generated} | {"RPCError"}
    imported = {
        overrides.ERROR_HAND_WRITTEN[spelling]
        for error in errors
        if error.hand_written
        for spelling in error.spellings
        if spelling in overrides.ERROR_HAND_WRITTEN
    }

    lines = [
        # Exhibit A of the Mozilla Public License 2.0. The licence asks each
        # source file to carry it, and the generated tree is source too.
        "# This Source Code Form is subject to the terms of the Mozilla Public",
        "# License, v. 2.0. If a copy of the MPL was not distributed with this",
        "# file, You can obtain one at https://mozilla.org/MPL/2.0/.",
        "",
        f"# Generated from Telegram's error table at layer {layer}. Do not edit by",
        "# hand; run codegen/gen_errors.py instead.",
        '"""Every error Telegram documents, one class each.',
        "",
        "The name is what to catch: except PeerIdInvalid says what went wrong far",
        "better than reading a string out of an exception does. Each one hangs off",
        "the class for its status code, so except BadRequest still catches the",
        "hundreds of ways a call can be wrong, and except RPCError catches the lot.",
        "",
        "An error whose name carries a number fills in value, and the classes that",
        "make something of it, waiting or migrating, are hand-written in rpc.py.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import re",
        "",
        "from .rpc import (",
        *(f"    {name}," for name in sorted(bases | imported)),
        ")",
    ]

    for error in generated:
        lines += ["", ""]
        lines += [f"class {error.name}({error.base}):"]
        lines += docstring(" ".join(error.descriptions))

    exact: list[tuple[str, str]] = []
    valued: list[tuple[str, str]] = []
    for error in errors:
        target = overrides.ERROR_HAND_WRITTEN.get(error.spellings[0], error.name)
        if error.hand_written:
            target = next(
                overrides.ERROR_HAND_WRITTEN[s]
                for s in error.spellings
                if s in overrides.ERROR_HAND_WRITTEN
            )
        exact += [(spelling, target) for spelling in error.exact]
        valued += [(spelling, target) for spelling in error.valued]

    lines += [
        "",
        "",
        "# Every error whose name is fixed, which is nearly all of them. This is the",
        "# first thing a refused call is looked up in and it answers in one step.",
        "BY_NAME: dict[str, type[RPCError]] = {",
        *(
            line
            for spelling, target in sorted(exact)
            for line in entry(
                f'    "{spelling}": {target},',
                f'    "{spelling}": (',
                f"        {target}",
                "    ),",
            )
        ),
        "}",
        "",
        "# The rest carry a number in the middle of the name, so they are matched",
        "# rather than looked up. There are only a few dozen and nothing reaches",
        "# them until a call has already failed, so a scan is fast enough.",
        "BY_PATTERN: tuple[tuple[re.Pattern[str], type[RPCError]], ...] = (",
        *(
            line
            for spelling, target in sorted(valued)
            for line in entry(
                f'    (re.compile(r"{pattern_for(spelling)}"), {target}),',
                "    (",
                f'        re.compile(r"{pattern_for(spelling)}"),',
                f"        {target},",
                "    ),",
            )
        ),
        ")",
        "",
        "__all__ = [",
        *(f'    "{error.name}",' for error in generated),
        "]",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    errors = collect()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(emit(errors), encoding="utf-8", newline="\n")
    generated = sum(1 for error in errors if not error.hand_written)
    spellings = sum(len(error.spellings) for error in errors)
    print(f"wrote {generated} classes for {spellings} error names")


if __name__ == "__main__":
    main()
