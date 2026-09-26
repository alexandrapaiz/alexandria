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
