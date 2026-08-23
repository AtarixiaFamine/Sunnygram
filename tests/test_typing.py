"""What the generated functions promise a type checker.

The rest of the suite runs the code. The point of a typed raw API is what can
be known before any code runs, so the only honest way to test it is to ask a
type checker and read the answer back. Rule C4 says a property the code claims
is a property the code proves, and this is that claim's only witness: nothing
at runtime can tell whether invoke returned Config or Any.

These are slow next to an ordinary test, because mypy has to walk the library.
CI type-checks the whole tree before it runs pytest, so the cache is warm by
the time these do.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

mypy_api = pytest.importorskip("mypy.api")

SRC = Path(__file__).resolve().parents[1] / "src"

PROGRAM = """
from sunnygram import Client
from sunnygram.raw import functions


async def main(app: Client) -> None:
    reveal_type(await app.invoke(functions.help.GetConfig()))
    reveal_type(await app.invoke(functions.auth.ResetAuthorizations()))
    reveal_type(await app.invoke(functions.contacts.GetStatuses()))
    reveal_type(await app.invoke(functions.messages.GetAvailableReactions(hash=0)))
    reveal_type(
        await app.invoke(
            functions.InvokeWithLayer(layer=228, query=functions.help.GetConfig())
        )
    )
    reveal_type(await app.invoker.invoke(functions.help.GetConfig()))
"""


def _revealed(program: str, tmp_path: Path) -> list[str]:
    """Every revealed type mypy reports for a program, in order.

    MYPYPATH is set rather than trusted, because an installed copy of the
    package would otherwise be type-checked instead of the one in the tree, and
    the whole point is to hold this tree to its claim.
    """
    source = tmp_path / "program.py"
    source.write_text(program, encoding="utf-8")
    previous = os.environ.get("MYPYPATH")
    os.environ["MYPYPATH"] = str(SRC)
    try:
        out, err, _ = mypy_api.run(
            ["--strict", "--ignore-missing-imports", str(source)]
        )
    finally:
        if previous is None:
            del os.environ["MYPYPATH"]
        else:
            os.environ["MYPYPATH"] = previous
    assert not err, err
    # Whether a builtin is revealed bare or as builtins.bool has changed
    # between mypy releases, and the matrix runs more than one. Normalizing is
    # the difference between a test about this library and a test about mypy's
    # printing.
    return [
        line.split('Revealed type is "', 1)[1].rstrip('"').replace("builtins.", "")
        for line in out.splitlines()
        if "Revealed type is" in line
    ]


@pytest.fixture(scope="module")
def revealed(tmp_path_factory: pytest.TempPathFactory) -> list[str]:
    """One mypy run for the whole module, since it is the expensive part."""
    return _revealed(PROGRAM, tmp_path_factory.mktemp("typing"))


def test_a_named_result_is_the_type_it_names(revealed: list[str]) -> None:
    assert revealed[0] == "sunnygram.raw.types._root.Config"


def test_a_bool_result_is_a_bool(revealed: list[str]) -> None:
    assert revealed[1] == "bool"


def test_a_vector_result_is_a_list_of_the_item(revealed: list[str]) -> None:
    assert revealed[2] == "list[sunnygram.raw.types._root.ContactStatus]"


def test_a_result_with_several_constructors_is_their_union(
    revealed: list[str],
) -> None:
    """An abstract TL type is every constructor that produces it.

    This is the shape that makes the change worth having: the caller is told
    there is more than one answer, which is exactly what it has to handle.
    """
    union = revealed[3]
    assert " | " in union
    assert "AvailableReactions" in union


def test_a_wrapper_answers_with_what_it_wrapped(revealed: list[str]) -> None:
    """invokeWithLayer and its family are answered with X, meaning the query.

    So they stay generic and hand the wrapped call's result straight through,
    rather than widening everything sent through them to an anything.
    """
    assert revealed[4] == "sunnygram.raw.types._root.Config"


def test_the_invoker_is_typed_the_same_as_the_client(revealed: list[str]) -> None:
    assert revealed[5] == "sunnygram.raw.types._root.Config"


def test_nothing_in_the_program_came_back_as_any(revealed: list[str]) -> None:
    """The regression this whole module exists to catch.

    Every assertion above would still pass if it were written against Any in a
    world where mypy spelled Any as the expected name. This one says the plain
    thing instead: none of these calls is untyped any more.
    """
    assert revealed
    assert not any(revealed_type == "Any" for revealed_type in revealed)
