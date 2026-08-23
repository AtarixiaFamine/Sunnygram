"""The ladder of event loops, and who is allowed to pick one.

Two things are worth testing here and they pull in opposite directions. The
first is that the fast loop really is used when it is installed, because a
speedup that silently does not happen is the most expensive kind of bug: the
program works, so nobody looks. The second is that nothing is installed
globally at import, because a library that changes the event loop policy of the
process that imported it has broken every program that made its own choice, and
that failure is loud but happens in somebody else's code.

Most of this machine may only have the bottom rung, so the ladder itself is
tested by standing in fake modules rather than by asserting what happens to be
installed here. That is the same discipline as the crypto ladder next door: the
ordering is a decision and gets a test, the environment is not.
"""

from __future__ import annotations

import asyncio
import sys
import types

from sunnygram import loop as loop_module
from sunnygram.loop import LOOP_BACKEND, describe, loop_factory, new_event_loop


def a_fake_loop_module(name):
    """A stand-in for uvloop or winloop, as far as _detect is concerned.

    It only has to have new_event_loop, because that is the whole of the api
    this library uses from either of them.
    """
    module = types.ModuleType(name)
    module.new_event_loop = lambda: f"a {name} loop"  # type: ignore[attr-defined]
    return module


class TestTheLadder:
    def test_what_this_machine_got_is_one_of_the_three(self):
        assert LOOP_BACKEND in {"uvloop", "winloop", "asyncio"}
        # None means asyncio's own, which is what Runner does with no factory.
        # Anything else has to be callable or Client.run would fail late.
        if LOOP_BACKEND == "asyncio":
            assert loop_factory() is None
        else:
            assert callable(loop_factory())

    def test_uvloop_wins_when_both_are_installed(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "uvloop", a_fake_loop_module("uvloop"))
        monkeypatch.setitem(sys.modules, "winloop", a_fake_loop_module("winloop"))
        name, factory = loop_module._detect()
        assert name == "uvloop"
        assert factory() == "a uvloop loop"

    def test_winloop_is_the_rung_below(self, monkeypatch):
        # The platform this matters on is Windows, where uvloop has never had a
        # wheel, so the interesting case is winloop present and uvloop absent.
        monkeypatch.setitem(sys.modules, "uvloop", None)
        monkeypatch.setitem(sys.modules, "winloop", a_fake_loop_module("winloop"))
        name, factory = loop_module._detect()
        assert name == "winloop"
        assert factory() == "a winloop loop"

    def test_neither_installed_falls_back_to_asyncio(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "uvloop", None)
        monkeypatch.setitem(sys.modules, "winloop", None)
        assert loop_module._detect() == ("asyncio", None)


class TestNothingIsInstalledGlobally:
    def test_importing_the_module_never_calls_install(self, monkeypatch):
        # The whole reason this is a module of functions rather than a call at
        # import time. uvloop.install() replaces the policy for the process,
        # so a library that calls it on import has changed the event loop of a
        # program that may have chosen its own, and the program finds out
        # somewhere else entirely.
        import importlib

        installed: list[str] = []
        fake = a_fake_loop_module("uvloop")
        fake.install = lambda: installed.append("uvloop")  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "uvloop", fake)

        reloaded = importlib.reload(loop_module)
        try:
            assert reloaded.LOOP_BACKEND == "uvloop"
            assert installed == []
        finally:
            # The module object the rest of the suite imported by name is this
            # one, so leaving it detecting a fake would leak into every test
            # after it.
            monkeypatch.undo()
            importlib.reload(loop_module)


class TestNewEventLoop:
    def test_it_hands_out_a_working_loop(self):
        # Whichever rung this machine has, the loop it returns has to be one a
        # coroutine can actually run on, since Client.run does nothing else
        # with it.
        made = new_event_loop()
        try:
            assert made.run_until_complete(asyncio.sleep(0, "ran")) == "ran"
        finally:
            made.close()

    def test_a_loop_it_hands_out_is_the_callers_to_close(self):
        made = new_event_loop()
        made.close()
        assert made.is_closed()


class TestDescribe:
    def test_it_names_the_backend(self):
        assert LOOP_BACKEND in describe()

    def test_the_slow_rung_says_what_to_install(self):
        # describe() exists to be pasted into a bug report, and the answer is
        # nearly always "you are on the plain loop", so it says so itself
        # rather than leaving the reader to know that asyncio is the slow one.
        if LOOP_BACKEND == "asyncio":
            assert "uvloop" in describe()
