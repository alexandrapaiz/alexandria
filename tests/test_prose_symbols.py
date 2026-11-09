"""Does the prose reader tell a stale name from a fair mention.

Run with `python3 -m pytest tests/test_prose_symbols.py -q`.

`tools/prose_symbols.py` exists because of one wrong word in a comment. On
2026-11-08 `alexandria/security` read `runtime/board/runpr.py`, whose comments
name an `annotate()` twice, and sent this seat an ask built on it. There is no
`annotate` in that module and there never has been: `corrected_report` shipped
2026-10-24 in `45c50bf4`, and the comment naming `annotate()` was added two days
later in `34a95642`, a 27-line pure addition that never touched the function it
mis-names. Nothing was renamed. Two seats' runs went into a function that does
not exist, and the first test below is that exact module, inline.

The hard part of this tool is not finding missing names, it is not crying wolf,
and the tests are weighted accordingly: one regression test for the defect and
four for the ways the first versions of this file were wrong about innocent
prose.

Each of those four is a real false positive this tool produced against this
repository before the test existed, which is why they are asserted by name:

`test_a_name_from_an_imported_module_resolves` -- 52 findings in `tests/`, all
wrong. A test that does `from tools import drift_watch as dw` and writes "the
guard at the top of `watch()`" is naming a function that exists, spelled the way
a reader says it rather than the way the file imports it.

`test_a_call_the_code_makes_resolves` -- prose saying `mkdtemp()` beside a body
that calls `tempfile.mkdtemp()`. Collecting the calls the file's own code makes
is what removes the need for a stdlib allowlist.

`test_a_mention_of_another_module_is_not_a_local_claim` -- the narrow-window
rule. "`schedules()` in `pipeline/runtime_sha.py`" was promoted to a finding by
a "this file's own" forty characters later about a different symbol, and
`schedules` is really there at line 93 of that module.

`test_prose_may_name_things_that_are_not_python` -- a pipeline stage, an MCP
subcommand, a Postgres function and a camelCase method are all legitimately
named in call form by prose, and this repo has fifty such mentions and no
defects. They are reported in the untiered bucket and never as stale.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import prose_symbols as ps  # noqa: E402


def check(tmp_path, name="m.py", **files):
    """Write a tree, read one file of it, return its findings by tier."""
    for filename, body in files.items():
        path = tmp_path / filename.replace("__", "/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    findings = ps.check_file(tmp_path / name, tmp_path, {})
    return (
        [f for f in findings if f["verdict"] == "unresolved" and f["claims_local"]],
        [f for f in findings if f["verdict"] == "unresolved" and not f["claims_local"]],
    )


def test_the_runpr_defect_is_found(tmp_path):
    """The comment that cost two runs, with the real module's shape around it."""
    stale, _ = check(tmp_path, **{"m.py": '''
# `annotate()` below rewrites the runner's sentence in place, and when it found
# nothing it rewrites it into "no pull request, looked for in <where>."
NO_PR_STEM = "no pull request"


def corrected_report(report, pr_url, where):
    """The rewrite itself."""
    return report


def resolve_into(payload, log=None):
    return bool(corrected_report(payload["report"], None, None))
'''})
    assert [f["name"] for f in stale] == ["annotate"]
    assert stale[0]["line"] == 2


def test_the_real_function_is_not_reported(tmp_path):
    """`corrected_report` is named in prose and defined, so it is not a finding."""
    stale, mentioned = check(tmp_path, **{"m.py": '''
# `corrected_report()` below is the rewrite.
def corrected_report(report, pr_url, where):
    return report
'''})
    assert stale == [] and mentioned == []


def test_a_near_miss_is_told_from_a_name_that_was_never_there(tmp_path):
    """The edit distance is the tell, and `annotate` has no near match.

    A typo carries its own correction and a seat can fix it by reading. A name
    that matches nothing is a function that never existed under that spelling,
    and that is the one a reader cannot repair from the comment alone -- which
    is why the finding prints the distance rather than only the name.
    """
    stale, _ = check(tmp_path, **{"m.py": '''
# `corected_report()` below, and `annotate()` below too.
def corrected_report(report, pr_url, where):
    return report
'''})
    by_name = {f["name"]: f["nearest"] for f in stale}
    assert by_name["corected_report"] == "corrected_report"
    assert by_name["annotate"] is None


def test_a_name_from_an_imported_module_resolves(tmp_path):
    """52 wrong findings in `tests/`: prose names the module under test's function."""
    stale, mentioned = check(
        tmp_path,
        **{
            "tools__drift_watch.py": "def watch(today=None):\n    return {}\n",
            "m.py": '''
from tools import drift_watch as dw


def test_it():
    """The `unknown` guard at the top of `watch()` below is what this covers."""
    assert dw.watch() == {}
''',
        },
    )
    assert stale == [] and mentioned == []


def test_a_call_the_code_makes_resolves(tmp_path):
    """Prose may name a call the body makes on something this tool cannot see."""
    stale, mentioned = check(tmp_path, **{"m.py": '''
import tempfile


def fixture(path):
    """Built below with `mkdtemp()`, then `mkdir()` on the result."""
    root = tempfile.mkdtemp()
    path.mkdir(parents=True)
    return root
'''})
    assert stale == [] and mentioned == []


def test_a_mention_of_another_module_is_not_a_local_claim(tmp_path):
    """The locality cue must attach to the name, not sit in the same sentence."""
    stale, mentioned = check(tmp_path, **{"m.py": '''
def press_write_site(path=None):
    """Derived, never declared.

    For the reason `schedules()` in `pipeline/runtime_sha.py` gives about file
    manifests and this file's own `press_schedule` gives about the cron.
    """
    return {}
'''})
    assert stale == []
    assert [f["name"] for f in mentioned] == ["schedules"]


def test_prose_may_name_things_that_are_not_python(tmp_path):
    """A stage, a subcommand, a Postgres function and a camelCase method."""
    stale, mentioned = check(tmp_path, **{"m.py": '''
# The gather() stage runs first, serve() is the subcommand that hosts it,
# the ids come from gen_random_uuid() and the client calls hasSpine().
STAGE = "gather"
'''})
    assert stale == []
    assert {f["name"] for f in mentioned} == {
        "gather", "serve", "gen_random_uuid", "hasSpine"}


def test_a_dotted_call_on_an_unplaceable_module_is_unverifiable(tmp_path):
    """Guessing here is how a checker earns the findings that get it switched off."""
    (tmp_path / "m.py").write_text('''
import requests

# `requests.get_it_all()` is not something this tool can check.
URL = "https://example.invalid"
''')
    findings = ps.check_file(tmp_path / "m.py", tmp_path, {})
    assert [(f["name"], f["verdict"]) for f in findings] == [
        ("requests.get_it_all", "unverifiable")]


def test_this_repository_has_no_stale_local_claims(tmp_path):
    """The measurement, asserted so that a new one has to be noticed.

    164 Python files, zero prose claims that a function is in a module where it
    is not. This is the baseline, not a guarantee: the fifty untiered mentions
    are deliberately not covered, because a comment is allowed to name a
    pipeline stage or a SQL function, and failing a build over that is how a
    useful check becomes one a seat turns off.
    """
    root = Path(__file__).resolve().parent.parent
    cache = {}
    stale = [
        f
        for path in ps.tracked_python(root, [])
        for f in ps.check_file(path, root, cache)
        if f["verdict"] == "unresolved" and f["claims_local"]
    ]
    assert stale == [], f"new stale local claims: {stale}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
