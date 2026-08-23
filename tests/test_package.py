"""The package as something that gets installed and imported.

Small things that are easy to get wrong in a way nothing else notices: a
version bumped in one of the two places it lives, or a public name that is
listed but does not actually resolve.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import sunnygram

REPO = Path(__file__).resolve().parents[1]


def test_the_version_is_the_same_in_both_places():
    # One is what pip installs, the other is what a bug report quotes.
    metadata = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    assert sunnygram.__version__ == metadata["project"]["version"]


@pytest.mark.parametrize("name", sorted(sunnygram.__all__))
def test_every_public_name_resolves(name):
    # The names come through a lazy __getattr__ backed by a table of module
    # paths, so a typo in the table is invisible until somebody imports that
    # one name, which may be long after it was written.
    assert getattr(sunnygram, name) is not None


def test_a_name_that_is_not_there_says_so():
    with pytest.raises(AttributeError):
        sunnygram.NoSuchThing


def test_dir_lists_every_public_name():
    # PEP 562 pairs __getattr__ with __dir__, and without the second one the
    # lazy names are invisible: dir() and a REPL's tab completion see only what
    # has already been imported, which on a fresh interpreter is two names out
    # of fifty. Nothing raises, so the only symptom is an API that looks empty
    # to anybody exploring it.
    assert set(sunnygram.__all__) <= set(dir(sunnygram))


def test_dir_does_not_import_anything():
    # The point of answering dir() from the name table rather than by resolving
    # the names is that it stays free (rule P7). A subprocess, because by the
    # time this file runs the rest of the suite has imported half the tree.
    code = "; ".join(
        (
            "import sys",
            "before = len(sys.modules)",
            "import sunnygram",
            "after = len(sys.modules)",
            "dir(sunnygram)",
            "generated = sum(1 for m in sys.modules if '.raw' in m)",
            "print(after - before, len(sys.modules) - after, generated)",
        )
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    on_import, on_dir, generated = (int(n) for n in result.stdout.split())
    assert on_dir == 0, "dir() imported something"
    assert generated == 0, "dir() reached the generated tree"
    assert on_import <= 30, f"importing sunnygram now costs {on_import} modules"
