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

import os
import subprocess
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

    168 Python files read 2026-11-09, zero prose claims that a function is in a
    module where it is not -- the same pair `alexandria/security` measured
    independently against HQ's checkout that day. The count carries its date
    because it drifts with every added module: it said 164 until 2026-11-09 and
    nothing noticed, in the test file of the tool whose whole job is prose that
    went stale without an event to fire on.

    This is the baseline, not a guarantee: the fifty untiered mentions
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


# The file list, which is the half of this tool that `alexandria/security`
# tested and these tests did not. Every test above hands `check_file` a tree it
# built, so nine passing tests said nothing about which files get read. On
# 2026-11-09 security ran the tool from a copy outside a checkout, with no
# `--root`, and the walk it fell back to went into the shared temp twelve seats
# write to; they killed it at twelve minutes.


def git_init(path):
    """A real checkout, because the thing under test is a question asked of git."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    (path / "m.py").write_text("# nothing\n")
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=a@b", "-c", "user.name=a",
         "commit", "-qm", "x"],
        check=True,
    )


def test_a_tree_that_is_not_a_checkout_is_walked_not_refused(tmp_path):
    """The fallback still exists. It is how the host's runtime gets read at all."""
    (tmp_path / "a.py").write_text("# one\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("# two\n")
    assert not ps.is_checkout(tmp_path)
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "a.py", tmp_path / "sub" / "b.py"]


def test_the_walk_does_not_descend_into_another_checkout(tmp_path):
    """Security's twelve minutes, in the small.

    A directory that is not a checkout, holding directories that are: the
    seats' sandboxes under a shared temp. `Path.rglob` read all of them, so a
    tree whose own answer was one file was reported as 201 and 90 findings about
    code the caller never named. git owns those trees and would list them
    properly if asked about them; this walk was not asked about them.
    """
    (tmp_path / "mine.py").write_text("# mine\n")
    git_init(tmp_path / "seatA")
    git_init(tmp_path / "seatB")
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "mine.py"]


def test_the_walk_prunes_vendored_trees(tmp_path):
    """What `git ls-files` gave for free and the walk has to be told."""
    (tmp_path / "mine.py").write_text("# mine\n")
    for noise in ("node_modules/pkg", ".venv/lib/site-packages", "__pycache__"):
        d = tmp_path / noise
        d.mkdir(parents=True)
        (d / "v.py").write_text("# noise\n")
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "mine.py"]


def test_the_walk_raises_rather_than_truncating(tmp_path):
    """A short list is a quiet zero, and this tool's output is a count of absences.

    Truncating would put the cap in `files_read` and nothing would say the list
    was partial, which on a tool that reports what it did *not* find reads as a
    clean tree.
    """
    for i in range(12):
        (tmp_path / f"m{i}.py").write_text("# x\n")
    with pytest.raises(ps.WalkTooWide):
        ps.tracked_python(tmp_path, [], max_files=5)
    assert ps.main(["--root", str(tmp_path), "--max-files", "5"]) == 2


def test_a_checkout_is_listed_by_git_and_a_broken_git_is_not_silently_walked(tmp_path):
    """The two failures the old code read off one exit code.

    "git does not know this tree" and "git knows it and the call broke" are
    different, and both arrived as a `SubprocessError` caught into the same
    fallback. A thirty-second timeout inside a real checkout therefore became a
    filesystem walk of it, silently, including everything git was keeping out.
    Now the first answers False to `is_checkout` and the second raises.
    """
    git_init(tmp_path)
    (tmp_path / "untracked.py").write_text("# not added\n")
    assert ps.is_checkout(tmp_path)
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "m.py"]

    def broken(*a, **k):
        raise subprocess.TimeoutExpired(cmd="git", timeout=30)

    real = ps.subprocess.run
    ps.subprocess.run = lambda *a, **k: (
        broken() if "ls-files" in a[0] else real(*a, **k)
    )
    try:
        with pytest.raises(subprocess.SubprocessError):
            ps.tracked_python(tmp_path, [])
    finally:
        ps.subprocess.run = real


def test_the_walk_does_not_read_a_symlinked_file(tmp_path):
    """The bound the first repair did not have, reported by security 2026-11-09.

    All three original bounds are decisions about a directory, and the step that
    appends a file had none. `followlinks=False` stops the descent into a linked
    directory and says nothing about a linked file: a symlink named `x.py`
    arrives in `filenames` like any other entry. So the one case the repair did
    not cover is a link aimed *past* the bound that had just excluded its
    target -- here into a nested checkout -- and the finding printed under a
    path inside the root the caller named. Two files read where the answer was
    one, which is the tool's own failure mode.
    """
    (tmp_path / "named").mkdir()
    (tmp_path / "named" / "own.py").write_text("# mine\n")
    git_init(tmp_path / "named" / "nested")
    (tmp_path / "named" / "nested" / "secret.py").write_text(
        "# names ghost_helper() below, which is not here\n"
    )
    (tmp_path / "named" / "leak.py").symlink_to(
        tmp_path / "named" / "nested" / "secret.py"
    )

    root = tmp_path / "named"
    excluded: list[str] = []
    assert ps.tracked_python(root, [], excluded=excluded) == [root / "own.py"]
    assert excluded == [str(root / "leak.py")]

    # And the report says it skipped, because a silent exclusion reads from
    # outside exactly like a clean tree.
    assert ps.main(["--root", str(root), "--max-unresolved", "0"]) == 0


def test_a_dangling_symlink_is_refused_before_it_is_opened(tmp_path):
    """`is_symlink` does not follow the link, so this is refused by the bound.

    The guard asks what the entry *is*, not what it points at, which is why a
    link to nothing costs a skip rather than a traceback.
    """
    (tmp_path / "real.py").write_text("# mine\n")
    (tmp_path / "gone.py").symlink_to(tmp_path / "never_existed.py")
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "real.py"]


def test_a_fifo_named_py_is_not_read(tmp_path):
    """The same guard's other half: the walk would otherwise block on `open`.

    A tree nobody has declared the contents of can hold an entry that is not a
    regular file, and this tool's reported failure in the field was twelve
    minutes of not returning.
    """
    (tmp_path / "real.py").write_text("# mine\n")
    os.mkfifo(tmp_path / "pipe.py")
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "real.py"]


def test_a_timed_out_ownership_question_raises_rather_than_answering_false(tmp_path):
    """The half of the conflation that survived the first repair, untested.

    Splitting the question out of the listing and then catching every failure
    of it into `return False` moves the conflation up one call: the caller reads
    False as "git does not own this tree" and walks a real checkout, including
    everything git was keeping out. The test above this one patches the listing
    call and leaves `rev-parse` real, so this is the case it cannot see --
    reproduced by `alexandria/security` against a real checkout, which got an
    untracked file back.

    git saying no and git saying nothing are different answers now: a non-zero
    exit returns False, and a timeout raises.
    """
    git_init(tmp_path)
    (tmp_path / "untracked.py").write_text("# not added\n")

    real = ps.subprocess.run

    def only_rev_parse_times_out(*a, **k):
        if "rev-parse" in a[0]:
            raise subprocess.TimeoutExpired(cmd="git", timeout=30)
        return real(*a, **k)

    ps.subprocess.run = only_rev_parse_times_out
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            ps.is_checkout(tmp_path)
        with pytest.raises(subprocess.TimeoutExpired):
            ps.tracked_python(tmp_path, [])
        # and the caller turns it into an explicit could-not-look, not a walk
        assert ps.main(["--root", str(tmp_path)]) == 2
    finally:
        ps.subprocess.run = real


def test_git_answering_no_is_still_False_and_still_walks(tmp_path):
    """The other side of the same split, so the raise did not eat the fallback.

    A non-zero exit from `rev-parse` is git answering the question, and the
    walk of a tree git does not own is how the host's runtime gets read at all.
    """
    (tmp_path / "a.py").write_text("# one\n")
    assert ps.is_checkout(tmp_path) is False
    assert ps.tracked_python(tmp_path, []) == [tmp_path / "a.py"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
