"""The documentation, held against the code it documents.

Twice now a documented call has not run: `SQLiteStorage` was written up before it
was exported, and `app.invoker.storage` was never a public attribute at all.
Neither raised anywhere in the suite, because the suite does not read the docs,
and the person who finds it is somebody following the guide on their first day.

This does not run the examples. It checks the cheaper half, which is the half
that has actually gone wrong: that every name a code block imports is really
exported, and every attribute it reaches for really exists.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

import sunnygram
from sunnygram import filters, plugins
from sunnygram.network import Invoker
from sunnygram.types import Message

DOCS = Path(__file__).resolve().parents[1] / "docs"

# The names a code block is allowed to assume, and what each one stands for.
# Only names that mean one thing everywhere belong here: `event` is left out
# because docs/updates.md means the update wrapper by it and docs/admin.md means
# an entry in the admin log, and a guard that has to guess is worse than none.
BOUND: dict[str, object] = {
    "app.invoker": Invoker,
    "app": sunnygram.Client,
    "client": sunnygram.Client,
    "message": Message,
    "press": sunnygram.CallbackQuery,
    "talk": sunnygram.Conversation,
    "dialog": sunnygram.Dialog,
    "Button": sunnygram.Button,
    "InlineResult": sunnygram.InlineResult,
    "Proxy": sunnygram.Proxy,
    "Permissions": sunnygram.Permissions,
    "AdminRights": sunnygram.AdminRights,
    "sunnygram": sunnygram,
    "filters": filters,
    "plugins": plugins,
}

BLOCK = re.compile("```python\n(.*?)```", re.S)


def _references() -> list[tuple[str, int, str, str]]:
    found: list[tuple[str, int, str, str]] = []
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in BLOCK.finditer(text):
            code = block.group(1)
            line = text[: block.start()].count("\n") + 1
            # Longest base first, so app.invoker.state is not read as app.invoker.
            for base in sorted(BOUND, key=len, reverse=True):
                pattern = re.escape(base) + r"\.([A-Za-z_][A-Za-z0-9_]*)"
                for hit in re.finditer(pattern, code):
                    attribute = hit.group(1)
                    if base == "app" and attribute == "invoker":
                        continue
                    found.append((path.name, line, base, attribute))
    return sorted(set(found))


CASES = _references()


def test_there_is_something_to_check():
    # A regex that quietly stopped matching would make every case below pass.
    assert len(CASES) > 50


@pytest.mark.parametrize(
    "page,line,base,attribute",
    CASES,
    ids=[f"{page}-{line}-{base}.{attribute}" for page, line, base, attribute in CASES],
)
def test_a_documented_attribute_exists(
    page: str, line: int, base: str, attribute: str
) -> None:
    target = BOUND[base]
    assert hasattr(target, attribute), (
        f"docs/{page} line {line} uses {base}.{attribute}, which does not exist"
    )


FROM_IMPORT = re.compile(
    r"^[ \t]*from[ \t]+(sunnygram[\w.]*)[ \t]+import[ \t]+([^\n(]+)", re.M
)
PLAIN_IMPORT = re.compile(r"^[ \t]*import[ \t]+(sunnygram[\w.]*)", re.M)


def _imports() -> list[tuple[str, int, str, str]]:
    found: list[tuple[str, int, str, str]] = []
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in BLOCK.finditer(text):
            code = block.group(1)
            line = text[: block.start()].count("\n") + 1
            for hit in FROM_IMPORT.finditer(code):
                module, names = hit.group(1), hit.group(2)
                for name in names.split(","):
                    name = name.strip().split(" as ")[0].strip()
                    if name:
                        found.append((path.name, line, module, name))
            for hit in PLAIN_IMPORT.finditer(code):
                found.append((path.name, line, hit.group(1), ""))
    return sorted(set(found))


IMPORTS = _imports()


def test_there_are_imports_to_check():
    assert len(IMPORTS) > 20


@pytest.mark.parametrize(
    "page,line,module,name",
    IMPORTS,
    ids=[f"{page}-{line}-{module}.{name}" for page, line, module, name in IMPORTS],
)
def test_a_documented_import_resolves(
    page: str, line: int, module: str, name: str
) -> None:
    # The import lines are the first thing anybody copies, so a name that moved
    # or was never exported fails on somebody's very first paste.
    imported = importlib.import_module(module)
    if name:
        assert hasattr(imported, name), (
            f"docs/{page} line {line} imports {name} from {module}, which is not there"
        )


def test_the_handler_table_lists_every_kind():
    """docs/updates.md calls its table "every kind of handler", so it has to be.

    It said seventeen for a while after the client had twenty-one, having been
    written before payments, stories and scheduled messages added the other
    four. Each of those was documented on its own page, so nothing looked
    missing unless you counted, and the table is the page somebody reads to
    find out what they can handle at all.
    """
    from sunnygram.dispatcher import KINDS

    text = (DOCS / "updates.md").read_text(encoding="utf-8")
    tabled = set(re.findall(r"\|\s*\[?`(on_[a-z_]+)`", text))
    expected = {
        ("on_callback_query" if kind == "callback" else f"on_{kind}") for kind in KINDS
    }
    assert expected - tabled == set(), "handler kinds missing from the docs table"


def test_every_type_a_handler_is_given_is_exported():
    """The middle column of that table names what the handler receives.

    Seventeen of the eighteen were re-exported at the top level and `Event` was
    not, so the one type belonging to `on_raw`, which the same page calls the
    escape hatch, could not be imported the way every other one could. Reading
    the column rather than keeping a second list means this cannot drift from
    what the table says.
    """
    text = (DOCS / "updates.md").read_text(encoding="utf-8")
    named: set[str] = set()
    for row in re.findall(r"^\|\s*`on_[a-z_]+`\s*\|([^|]+)\|", text, re.M):
        for word in re.findall(r"`\[?([A-Za-z_][A-Za-z0-9_]*)", row):
            named.add(word)
        for word in re.findall(r"\[`([A-Za-z_][A-Za-z0-9_]*)`\]", row):
            named.add(word)
    named -= {"list"}  # `list[Message]` names its element, which is what counts
    assert len(named) > 10, "the type column stopped being read"
    missing = sorted(n for n in named if not hasattr(sunnygram, n))
    assert missing == [], f"documented handler types not exported: {missing}"
