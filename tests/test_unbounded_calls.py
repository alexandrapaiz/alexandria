"""The gate that finds an external call nobody put a clock on.

Every test here carries a control, because the whole point of the tool is that
a negative result must be a fact about the tree and not a fact about the
instrument. A test that only asserts "nothing found" passes equally well
against a scanner that never looked.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import unbounded_calls as uc  # noqa: E402


# --- the predicate ----------------------------------------------------------

def test_a_bounded_call_is_clean_and_the_same_call_unbounded_is_not():
    bounded = "import subprocess\nsubprocess.run(['gh', 'pr', 'list'], timeout=30)\n"
    seen = uc.scan_source(bounded, "x.py")
    assert [r["bounded"] for r in seen] == [True]

    unbounded = "import subprocess\nsubprocess.run(['gh', 'pr', 'list'])\n"
    rows = uc.scan_source(unbounded, "x.py")
    assert len(rows) == 1
    assert rows[0]["bounded"] is False
    assert rows[0]["line"] == 2
    assert rows[0]["call"] == "subprocess.run"
    assert rows[0]["binary"] == "gh"
    assert rows[0]["reach"] == "network"


@pytest.mark.parametrize("starter", sorted(uc.SUBPROCESS_STARTERS))
def test_every_way_of_starting_a_process_is_read(starter):
    """A gate that knows `run` and not `Popen` is quiet about half the tree."""
    src = f"import subprocess\nsubprocess.{starter}(['gh', 'pr', 'list'])\n"
    assert len(uc.scan_source(src, "x.py")) == 1
    src_ok = (f"import subprocess\n"
              f"subprocess.{starter}(['gh', 'pr', 'list'], timeout=5)\n")
    assert [r["bounded"] for r in uc.scan_source(src_ok, "x.py")] == [True]


def test_urlopen_is_read_and_a_bounded_one_is_not_reported():
    src = ("import urllib.request\n"
           "urllib.request.urlopen(req)\n")
    rows = uc.scan_source(src, "x.py")
    assert [r["reach"] for r in rows] == ["network"]
    ok = ("import urllib.request\n"
          "urllib.request.urlopen(req, timeout=10)\n")
    assert [r["bounded"] for r in uc.scan_source(ok, "x.py")] == [True]


# --- reach, which is three answers and not two ------------------------------

@pytest.mark.parametrize("argv,reach", [
    ("['gh', 'pr', 'list']", "network"),
    ("['curl', '-s', 'https://example.test']", "network"),
    ("['git', 'fetch', 'origin']", "network"),
    ("['git', 'ls-remote', '--heads', 'origin']", "network"),
    ("['git', 'rev-parse', '--abbrev-ref', 'HEAD']", "local"),
    ("['git', 'diff', '--no-color']", "local"),
    ("['git', 'remote', 'get-url', 'origin']", "local"),
    ("['grep', '-rn', 'x']", "local"),
    ("argv", "unknown"),
    ("['git', *args]", "unknown"),
    ("['git', '-C', root, 'status']", "unknown"),
])
def test_reach_is_read_off_the_argv_and_is_unknown_when_it_cannot_be(argv, reach):
    """`unknown` is a third answer on purpose.

    Collapsing an unreadable argv into `local` is the conflation this entire
    class is about, one layer up: the instrument's inability to look, written
    down as a fact about the call.
    """
    src = f"import subprocess\nsubprocess.run({argv})\n"
    rows = uc.scan_source(src, "x.py")
    assert len(rows) == 1
    assert rows[0]["reach"] == reach


def test_network_only_keeps_the_calls_it_could_not_read():
    """A filter that drops `unknown` would be quieter than the truth."""
    rows = [
        {"path": "a.py", "line": 1, "reach": "network", "call": "subprocess.run",
         "binary": "gh", "bounded": False, "handlers": []},
        {"path": "b.py", "line": 2, "reach": "unknown", "call": "subprocess.run",
         "binary": "unreadable", "bounded": False, "handlers": []},
        {"path": "c.py", "line": 3, "reach": "local", "call": "subprocess.run",
         "binary": "grep", "bounded": False, "handlers": []},
    ]
    kept, _ = uc.render(rows, set(), network_only=True)
    assert [r["path"] for r in kept] == ["a.py", "b.py"]
    all_three, _ = uc.render(rows, set(), network_only=False)
    assert len(all_three) == 3


# --- a handler is the other half, and is reported rather than accepted ------

def test_a_handler_without_a_bound_is_still_a_finding_and_says_so():
    """The two halves are separate and a tool that conflates them is the bug.

    `skill_registrar.py` is the real case: both of its git calls are handled
    for `OSError` and `CalledProcessError`, and neither has a clock. A handler
    catches a refusal; it does not end a hang.
    """
    src = ("import subprocess\n"
           "try:\n"
           "    subprocess.run(['gh', 'pr', 'list'])\n"
           "except OSError:\n"
           "    pass\n")
    rows = uc.scan_source(src, "x.py")
    assert len(rows) == 1
    assert rows[0]["handlers"] == ["OSError"]
    _, prose = uc.render(rows, set(), network_only=False)
    assert "handled (OSError) but not bounded" in prose


def test_a_bare_except_is_named_as_bare():
    src = ("import subprocess\n"
           "try:\n"
           "    subprocess.run(['gh', 'x'])\n"
           "except:\n"
           "    pass\n")
    assert uc.scan_source(src, "x.py")[0]["handlers"] == ["bare"]


# --- refusing to answer, which is never an answer of clean ------------------

def test_a_file_that_does_not_parse_is_a_refusal_rather_than_a_clean_file():
    with pytest.raises(uc.CannotLook):
        uc.scan_source("def broken(:\n", "x.py")


def test_a_missing_path_is_a_refusal(tmp_path):
    with pytest.raises(uc.CannotLook):
        uc.scan_paths(["no-such-directory"], root=tmp_path)


def test_a_malformed_baseline_is_a_refusal_and_never_an_empty_set(tmp_path):
    """An unreadable baseline read as "nothing accepted" is a wall of noise."""
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"accepted": [{"path": "a.py", "line": 7}]}))
    assert uc.load_baseline(good) == {("a.py", 7)}          # the control

    for bad in ["{not json", json.dumps([]), json.dumps({"accepted": "all"}),
                json.dumps({"accepted": [{"path": "a.py"}]})]:
        rough = tmp_path / "bad.json"
        rough.write_text(bad)
        with pytest.raises(uc.CannotLook):
            uc.load_baseline(rough)

    assert uc.load_baseline(None) == set()


# --- the exit codes, driven through main ------------------------------------

def _tree(tmp_path, **files):
    for name, body in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    return tmp_path


def test_exit_zero_on_a_clean_tree_and_one_on_a_finding(tmp_path, capsys):
    clean = _tree(tmp_path / "clean", **{
        "t/ok.py": "import subprocess\nsubprocess.run(['gh', 'x'], timeout=5)\n"})
    assert uc.main(["t", "--root", str(clean)]) == 0
    assert "1 external call read, 1 bounded in time" in capsys.readouterr().out

    dirty = _tree(tmp_path / "dirty", **{
        "t/bad.py": "import subprocess\nsubprocess.run(['gh', 'x'])\n"})
    assert uc.main(["t", "--root", str(dirty)]) == 1
    assert "t/bad.py:2" in capsys.readouterr().out


def test_the_clean_path_prints_a_line_because_silence_would_be_permission(
        tmp_path, capsys):
    """The gate this seat shipped on 2026-11-09 broke on exactly this.

    A gate whose quiet means permission cannot be quiet, because a reader
    cannot tell "I looked and found nothing" from "I did not run".
    """
    clean = _tree(tmp_path, **{
        "t/ok.py": "import subprocess\nsubprocess.run(['gh', 'x'], timeout=5)\n"})
    assert uc.main(["t", "--root", str(clean)]) == 0
    out = capsys.readouterr().out.strip()
    assert out, "the clean path printed nothing at all"
    assert "1 external call read, 1 bounded in time" in out, out


def test_exit_two_when_the_question_could_not_be_asked(tmp_path, capsys):
    broken = _tree(tmp_path, **{"t/broken.py": "def f(:\n"})
    assert uc.main(["t", "--root", str(broken)]) == 2
    err = capsys.readouterr().err
    assert "not an answer of clean" in err


def test_a_baseline_entry_silences_one_line_and_not_its_neighbour(
        tmp_path, capsys):
    tree = _tree(tmp_path, **{
        "t/two.py": ("import subprocess\n"
                     "subprocess.run(['gh', 'a'])\n"
                     "subprocess.run(['gh', 'b'])\n")})
    assert uc.main(["t", "--root", str(tree)]) == 1   # the control, both found
    assert capsys.readouterr().out.count("t/two.py") == 2

    baseline = tmp_path / "base.json"
    baseline.write_text(json.dumps({"accepted": [{"path": "t/two.py", "line": 2}]}))
    assert uc.main(["t", "--root", str(tree),
                    "--baseline", str(baseline)]) == 1
    out = capsys.readouterr().out
    assert "t/two.py:3" in out and "t/two.py:2" not in out


def test_the_json_render_and_the_prose_render_agree(tmp_path, capsys):
    tree = _tree(tmp_path, **{
        "t/x.py": "import subprocess\nsubprocess.run(['gh', 'a'])\n"})
    uc.main(["t", "--root", str(tree), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["calls_read"] == 1
    assert payload["unbounded"] == 1
    assert payload["findings"][0]["path"] == "t/x.py"
    assert uc.main(["t", "--root", str(tree)]) == 1


def test_skipped_directories_are_not_scanned(tmp_path, capsys):
    tree = _tree(tmp_path, **{
        "t/node_modules/x.py": "import subprocess\nsubprocess.run(['gh', 'a'])\n",
        "t/real.py": "import subprocess\nsubprocess.run(['gh', 'b'])\n"})
    assert uc.main(["t", "--root", str(tree)]) == 1
    out = capsys.readouterr().out
    assert "t/real.py" in out
    assert "node_modules" not in out


# --- the tool run as a process, which is how a ready command runs it --------

def test_the_tool_runs_as_a_command_and_bounds_its_own_run(tmp_path):
    """Driven through a real interpreter, with a real clock over it.

    This scanner opens no sockets and starts no processes, so it has no call of
    its own to bound. The thing worth asserting is that it finishes, because a
    gate in front of an `&&` that does not finish is worse than no gate.
    """
    done = subprocess.run(
        [sys.executable, "tools/unbounded_calls.py", "tools", "pipeline", "mcp"],
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True, text=True, timeout=120,
    )
    assert done.returncode in (0, 1), done.stderr
    assert "unbounded external call" in done.stdout or "in scope" in done.stdout


# --- timeout=None, which the first version of this gate called bounded ------

def test_an_explicit_timeout_of_none_is_unbounded():
    """`subprocess.run(argv, timeout=None)` has no clock and used to pass.

    The gate asked whether the keyword existed. The dimension beside that is
    what the keyword says, which is the same shape as every defect this gate
    reports. Nothing in this repository writes it today; it is the spelling
    the next person silencing this gate would reach for.
    """
    src = "import subprocess\nsubprocess.run(['gh', 'x'], timeout=None)\n"
    rows = uc.scan_source(src, "x.py")
    assert len(rows) == 1
    assert rows[0]["bounded"] is False

    control = "import subprocess\nsubprocess.run(['gh', 'x'], timeout=5)\n"
    assert uc.scan_source(control, "x.py")[0]["bounded"] is True


@pytest.mark.parametrize("spelling,bounded", [
    ("timeout=30", True),
    ("timeout=SOME_CONSTANT", True),
    ("timeout=self.timeout", True),
    ("timeout=None", False),
    ("check=True", False),
])
def test_what_counts_as_a_bound(spelling, bounded):
    """A non-literal timeout is taken at its word; only `None` is refused.

    A name this scanner cannot resolve could be None at runtime. Reporting
    every one of those would bury the twenty-three real findings under the
    whole tree, so the shallow read is deliberate and is stated in the module
    docstring rather than left for a reader to infer.
    """
    src = f"import subprocess\nsubprocess.run(['gh', 'x'], {spelling})\n"
    assert uc.scan_source(src, "x.py")[0]["bounded"] is bounded


def test_the_unbounded_count_over_this_repository_is_unchanged_by_the_guard():
    """The guard adds no finding here, which is the measurement behind it."""
    rows = uc.scan_paths(["tools", "pipeline", "mcp"])
    unbounded = [r for r in rows if not r["bounded"]]
    assert len(unbounded) == 23, [f"{r['path']}:{r['line']}" for r in unbounded]


def test_a_fully_accepted_tree_is_clean_and_still_names_what_it_read(
        tmp_path, capsys):
    """Exit 0 with findings accepted, and the counts must not read as zero.

    The clean line's job is to be checkable. A tree with two unbounded calls
    both in the baseline is clean, and saying "2 unbounded of which 2 accepted"
    is the only rendering a reader can act on: it distinguishes a tree with no
    unbounded calls from one whose unbounded calls somebody signed for.
    """
    tree = _tree(tmp_path, **{
        "t/two.py": ("import subprocess\n"
                     "subprocess.run(['gh', 'a'])\n"
                     "subprocess.run(['gh', 'b'])\n")})
    baseline = tmp_path / "all.json"
    baseline.write_text(json.dumps({"accepted": [
        {"path": "t/two.py", "line": 2}, {"path": "t/two.py", "line": 3}]}))

    assert uc.main(["t", "--root", str(tree), "--baseline", str(baseline)]) == 0
    out = capsys.readouterr().out
    assert "2 external calls read, 0 bounded in time, 2 unbounded" in out
    assert "2 accepted by the baseline" in out


# --- the green state, which was owed ---------------------------------------
#
# The first version of this gate reached exit 0 on no invocation anywhere in
# this repository, and 38 tests passed over it, because every exit-0
# assertion above is against a tree the test built and the one test that runs
# the real command line accepts either answer. These four are the tests that
# would have caught it: they assert against this repository's own tree and
# this repository's own shipped accepted set.

ACCEPTED_SET = Path(__file__).resolve().parent.parent / (
    "docs/security/unbounded-calls.json")


def test_the_documented_invocation_over_this_repository_exits_zero():
    """The defect the ExO seat found by running this file rather than reading it.

    The docstring's own last invocation is the green one. A gate with no green
    state cannot go in a pipeline or a checklist, so it gets run once by its
    author and never again.
    """
    root = Path(__file__).resolve().parent.parent
    done = subprocess.run(
        [sys.executable, "tools/unbounded_calls.py",
         "--baseline", "docs/security/unbounded-calls.json"],
        cwd=str(root), capture_output=True, text=True, timeout=120,
    )
    assert done.returncode == 0, (done.returncode, done.stdout, done.stderr)
    # The control: green must not read as "nothing unbounded here".
    assert "unbounded of which" in done.stdout, done.stdout
    assert "accepted by the baseline" in done.stdout, done.stdout
    # And the same tree with no baseline is still red, so exit 0 above is the
    # accepted set doing the work rather than the scanner having stopped.
    bare = subprocess.run(
        [sys.executable, "tools/unbounded_calls.py"],
        cwd=str(root), capture_output=True, text=True, timeout=120,
    )
    assert bare.returncode == 1, (bare.returncode, bare.stdout, bare.stderr)


def test_the_shipped_accepted_set_is_readable_and_every_row_says_why():
    """A row with no status cannot be told from a blessing by any reader."""
    data = json.loads(ACCEPTED_SET.read_text(encoding="utf-8"))
    rows = uc.load_baseline(ACCEPTED_SET)          # the strict reader accepts it
    assert len(rows) == len(data["accepted"]) == 23
    assert {r["status"] for r in data["accepted"]} == {"debt"}
    assert all(r["why"] for r in data["accepted"])
    assert data["assigned"].endswith(".md")


def test_a_stale_accepted_row_is_named_and_changes_no_exit_status(
        tmp_path, capsys):
    """A set nobody prunes stops being a ratchet.

    Keyed on path and line, so a fixed call and a moved call both leave a row
    matching nothing. `tools/board.py`'s two calls moved 137 lines in one
    evening, which is where the measurement behind this test comes from.
    """
    tree = _tree(tmp_path, **{
        "t/one.py": ("import subprocess\n"
                     "subprocess.run(['gh', 'a'])\n")})
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"accepted": [{"path": "t/one.py", "line": 2}]}))
    assert uc.main(["t", "--root", str(tree), "--baseline", str(live)]) == 0
    assert "should be pruned" not in capsys.readouterr().out   # the control

    drifted = tmp_path / "drifted.json"
    drifted.write_text(json.dumps({"accepted": [
        {"path": "t/one.py", "line": 2},
        {"path": "t/one.py", "line": 99}]}))
    assert uc.main(["t", "--root", str(tree), "--baseline", str(drifted)]) == 0
    out = capsys.readouterr().out
    assert "1 accepted row matched no unbounded call" in out, out
    assert "t/one.py:99" in out


def test_network_only_does_not_turn_an_out_of_scope_row_stale(
        tmp_path, capsys):
    """Staleness is read against the tree, never against the filter's scope.

    A local accepted row matching nothing under `--network-only` is the filter
    working. Reporting it would make the strictest invocation the noisiest.
    """
    tree = _tree(tmp_path, **{
        "t/two.py": ("import subprocess\n"
                     "subprocess.run(['gh', 'a'])\n"
                     "subprocess.run(['ls', '-l'])\n")})
    baseline = tmp_path / "both.json"
    baseline.write_text(json.dumps({"accepted": [
        {"path": "t/two.py", "line": 2}, {"path": "t/two.py", "line": 3}]}))

    assert uc.main(["t", "--root", str(tree), "--baseline", str(baseline),
                    "--network-only"]) == 0
    assert "should be pruned" not in capsys.readouterr().out

    assert uc.main(["t", "--root", str(tree), "--baseline", str(baseline),
                    "--network-only", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["stale_accepted"] == []

    # The control, and the reason staleness is scope-independent: a row that
    # matches nothing in the tree is still reported under the same filter, so
    # the silence above is the scope rule and not the report being switched
    # off by `--network-only`.
    with_stale = tmp_path / "with-stale.json"
    with_stale.write_text(json.dumps({"accepted": [
        {"path": "t/two.py", "line": 2}, {"path": "t/two.py", "line": 3},
        {"path": "t/gone.py", "line": 1}]}))
    assert uc.main(["t", "--root", str(tree), "--baseline", str(with_stale),
                    "--network-only"]) == 0
    assert "t/gone.py:1" in capsys.readouterr().out
