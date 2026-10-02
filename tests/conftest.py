"""One Modal stub for the whole suite, installed before any test module imports.

Four test files each carried their own copy of this stub, each guarded by
`if "modal" not in sys.modules`. That guard is what broke the suite. Under
`python3 -m pytest tests/ -q`, the command every one of those files' docstrings
prescribes, `test_email_template.py` is collected first and its copy wins, and
its copy is the one with no `modal.Volume`. So `test_evidence_grade.py` raised
`AttributeError` while pytest was still collecting, and a collection error is
not one red test, it is no tests at all. The whole suite reported a single
error and ran nothing.

A conftest runs before collection, so this stub is always the one that wins and
the four in-file copies become no-ops through their own guard. They are left in
place on purpose: each of those files also documents running it directly, and
that still has to work with no conftest involved.

The stub is the union of what `pipeline/` and `mcp/` actually reach for at
import time. It is not a Modal emulator. Nothing here executes on Modal, and
anything that needs to must be driven against a real deployment instead.
"""

import sys
import types

import pytest


def _install_modal_stub():
    modal = types.ModuleType("modal")

    class _Image:
        """`.pip_install(...).add_local_file(...)` and anything else, all chaining."""

        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.Volume = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    # The decorators have to hand the real function back. A stub that returned
    # a stub here would leave every decorated function untestable, which is the
    # opposite of the point.
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
        cls=lambda *a, **k: (lambda c: c),
    )
    modal.asgi_app = lambda *a, **k: (lambda f: f)
    modal.enter = lambda *a, **k: (lambda f: f)
    modal.method = lambda *a, **k: (lambda f: f)
    modal.fastapi_endpoint = lambda *a, **k: (lambda f: f)
    return modal


if "modal" not in sys.modules:
    sys.modules["modal"] = _install_modal_stub()


# ---------------------------------------------------------------------------
# The `check()` files report their failures under pytest too.
#
# Two files in this suite predate pytest here and carry their own harness: a
# module-level `FAILURES` list, a `check(name, condition, detail)` that appends
# to it and prints, and an `if __name__ == "__main__"` block that exits 1 when
# the list is not empty. `tests/test_press_resilience.py` and
# `tests/test_press_rehearsal.py` are both written that way, and checks.yml runs
# both of them as scripts, so CI reads the exit code and the pattern works.
#
# It does not work under `python3 -m pytest tests/ -q`, which is the command
# requirements-dev.txt prescribes and every one of those two files' docstrings
# names. pytest never runs `__main__`, nothing else looks at `FAILURES`, and a
# test function that calls `check()` and returns normally is a test function
# that passed. So roughly 130 assertions print `FAIL` on stdout, which `-q`
# swallows, and the suite says green.
#
# That is not hypothetical. `test_call_model_walks_and_backs_off` asserted the
# pre-incident backoff contract and had been failing on main "since" 2026-09-24,
# per the note the fix left in it on 2026-09-30. The only reason anyone found it
# is that checks.yml happens to run that one file as a script. Nobody running
# the repo's own test command would ever have seen it.
#
# So: any test module that owns a list named `FAILURES` gets it enforced. The
# snapshot is taken per test rather than per module, so a failure is attributed
# to the test that produced it instead of to whichever test ran last. Script
# mode is untouched, because a conftest is not imported when a file is run
# directly, which is the whole reason both files keep their `__main__` block.


def _failures_list(item):
    """The module-level `FAILURES` list this test writes into, or None."""
    module = getattr(item, "module", None)
    failures = getattr(module, "FAILURES", None)
    return failures if isinstance(failures, list) else None


# `wrapper=True` rather than the older `hookwrapper=True`: under the old form,
# raising during teardown is what pluggy calls a PluggyTeardownRaisedWarning, and
# a check that warns while it fails is a check people learn to ignore. The new
# form is the sanctioned way for a wrapper to replace a hook's outcome, it makes
# `yield` re-raise whatever the test raised so a real traceback still wins, and
# it needs pluggy 1.2, which pytest 8 brings. requirements-dev.txt pins
# `pytest>=8`, and checks.yml installs from that file.
@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    failures = _failures_list(item)
    before = 0 if failures is None else len(failures)

    # A test that raised propagates from here with its own traceback intact, and
    # keeps whatever it appended before raising out of the report: that verdict
    # is already correct and a list of strings would only bury it.
    result = yield

    if failures is not None:
        # The slice from `before` is what keeps this honest: each test answers
        # only for the lines it appended itself, never for a predecessor's.
        appended = failures[before:]
        if appended:
            detail = "\n".join(f"  - {line}" for line in appended)
            pytest.fail(
                f"{len(appended)} check() failure(s) in {item.name}:\n{detail}\n\n"
                "These print `FAIL` on stdout and, before tests/conftest.py grew "
                "this hook, were invisible to pytest.",
                pytrace=False,
            )
    return result
