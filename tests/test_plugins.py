"""Handlers written in their own files, and loaded against a client.

The failure this has to be tested against is the silent one, and it has three
shapes. A plugin whose decorator was forgotten registers nothing and the
program simply ignores people. A plugin that fails to import, if the loader
swallows it, does the same thing while looking healthier. And a plugin loaded
twice registers twice, so every message is answered twice by code that appears
once in the source.

The packages here are written to a temporary directory and imported for real,
rather than faked, because the part that goes wrong is the importing.
"""

from __future__ import annotations

import sys
import textwrap
from typing import Any

import pytest

from sunnygram import filters, plugins
from sunnygram.dispatcher import Dispatcher, Handler
from sunnygram.errors import SunnygramError

GREET = """
from sunnygram import filters, plugins

@plugins.on_message(filters.command("hello"))
async def greet(client, message):
    message.answered = "greet"

@plugins.on_callback_query()
async def pressed(client, query):
    query.answered = "pressed"
"""

ECHO = """
from sunnygram import plugins

@plugins.on_message(group=3)
async def echo(client, message):
    message.answered = "echo"

def helper():
    return "not a handler"
"""

BROKEN = """
from sunnygram import plugins

raise RuntimeError("this plugin does not import")
"""


class FakeClient:
    """Just enough client for a loader: somewhere to put handlers."""

    def __init__(self) -> None:
        self.dispatcher = Dispatcher()

    def add_handler(self, callback: Any, **options: Any) -> Handler:
        return self.dispatcher.add(Handler(callback=callback, **options))


@pytest.fixture
def package(tmp_path, monkeypatch):
    """A real, importable plugin package, gone again by the next test.

    The modules are removed from sys.modules on the way out as well as from the
    path. A test that left them behind would make the next one pass or fail
    depending on which ran first, which is the kind of test failure that costs
    an afternoon.
    """
    made: list[str] = []

    def build(name: str, **modules: str) -> str:
        root = tmp_path / name
        root.mkdir()
        (root / "__init__.py").write_text("", encoding="utf-8")
        for module, source in modules.items():
            (root / f"{module}.py").write_text(textwrap.dedent(source), encoding="utf-8")
        made.append(name)
        return name

    monkeypatch.syspath_prepend(str(tmp_path))
    yield build
    for name in made:
        for loaded in [key for key in sys.modules if key == name or key.startswith(f"{name}.")]:
            del sys.modules[loaded]


class TestSurface:
    """The plugin decorators against the client's, which are meant to be the same set.

    These two lists are written in different files and nothing but this test
    makes them agree. When they drifted apart before, four kinds the client had
    grown could not be reached from a plugin at all, and the failure was the
    quiet kind: the decorator simply did not exist, so a plugin asking for one
    failed at import with an AttributeError naming nothing useful.
    """

    def test_every_kind_has_a_plugin_decorator(self):
        from sunnygram.dispatcher import KINDS

        have = {
            name.removeprefix("on_")
            for name in plugins.__all__
            if name.startswith("on_")
        }
        # The client spells one of them differently from its kind.
        have = {"callback" if n == "callback_query" else n for n in have}
        assert have == set(KINDS)

    def test_the_plugin_decorators_match_the_client_by_name(self):
        from sunnygram.client import Client

        on_client = {n for n in dir(Client) if n.startswith("on_")}
        on_plugins = {n for n in plugins.__all__ if n.startswith("on_")}
        assert on_plugins == on_client

    def test_every_exported_name_exists(self):
        missing = [n for n in plugins.__all__ if not hasattr(plugins, n)]
        assert missing == []


class TestMarking:
    def test_a_decorator_records_what_was_asked_for(self):
        @plugins.on_message(filters.text, group=2)
        async def handler(client, message):
            pass

        asked = plugins.registrations(handler)
        assert len(asked) == 1
        assert asked[0].kind == "message"
        assert asked[0].group == 2
        assert asked[0].filters is filters.text

    def test_the_function_is_returned_unchanged(self):
        async def original(client, message):
            return "still me"

        assert plugins.on_message()(original) is original

    def test_two_decorators_on_one_function_both_count(self):
        # Stacking them is the obvious thing to try. The outer one quietly
        # winning would be a surprise nothing reports.
        @plugins.on_message()
        @plugins.on_edited()
        async def handler(client, message):
            pass

        assert {one.kind for one in plugins.registrations(handler)} == {
            "message",
            "edited",
        }

    def test_an_ordinary_function_asked_for_nothing(self):
        def plain():
            pass

        assert plugins.registrations(plain) == ()


class TestLoading:
    def test_it_registers_what_the_package_asked_for(self, package):
        name = package("plugins_one", greet=GREET, echo=ECHO)
        client = FakeClient()

        assert plugins.load_into(client, name) == 3
        kinds = sorted(handler.kind for handler in client.dispatcher.handlers)
        assert kinds == ["callback", "message", "message"]

    def test_the_group_a_plugin_asked_for_is_kept(self, package):
        name = package("plugins_group", echo=ECHO)
        client = FakeClient()
        plugins.load_into(client, name)
        assert client.dispatcher.handlers[0].group == 3

    def test_a_function_without_a_decorator_is_not_a_handler(self, package):
        # ECHO has a plain helper in it. A loader that registered everything
        # callable would register that too, and it would be called with a
        # message and fail on every single update.
        name = package("plugins_helper", echo=ECHO)
        client = FakeClient()
        assert plugins.load_into(client, name) == 1

    def test_a_plugin_that_does_not_import_is_not_skipped(self, package):
        # The whole point. A feature that is silently absent looks exactly like
        # a program with nothing to do (rule C3).
        name = package("plugins_broken", broken=BROKEN)
        client = FakeClient()
        with pytest.raises(RuntimeError, match="does not import"):
            plugins.load_into(client, name)

    def test_a_package_that_is_not_there_says_so(self):
        client = FakeClient()
        with pytest.raises(SunnygramError, match="neither an importable module"):
            plugins.load_into(client, "no_such_plugins_package")

    def test_modules_can_be_left_out(self, package):
        name = package("plugins_excluded", greet=GREET, echo=ECHO)
        client = FakeClient()
        assert plugins.load_into(client, name, exclude=("greet",)) == 1

    def test_or_named_one_at_a_time(self, package):
        name = package("plugins_included", greet=GREET, echo=ECHO)
        client = FakeClient()
        assert plugins.load_into(client, name, include=("echo",)) == 1

    def test_a_module_starting_with_an_underscore_is_left_alone(self, package):
        name = package("plugins_private", _shared=GREET, echo=ECHO)
        client = FakeClient()
        assert plugins.load_into(client, name) == 1

    def test_a_package_with_no_handlers_in_it_says_so(self, package, caplog):
        # Not an error, since pointing this at a package of helpers is a
        # reasonable thing to do. But it is nearly always the decorators having
        # been left off, and that is invisible everywhere else.
        name = package("plugins_empty", nothing="x = 1\n")
        client = FakeClient()
        with caplog.at_level("WARNING", logger="sunnygram.plugins"):
            assert plugins.load_into(client, name) == 0
        assert "not one handler was found" in caplog.text

    def test_loading_the_same_package_twice_registers_twice(self, package):
        # Written down rather than prevented: calling it twice is a mistake in
        # the program, and a loader that silently ignored the second call would
        # be lying about what it did. The count says what happened.
        name = package("plugins_twice", echo=ECHO)
        client = FakeClient()
        assert plugins.load_into(client, name) == 1
        assert plugins.load_into(client, name) == 1
        assert len(client.dispatcher.handlers) == 2
