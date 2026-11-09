"""The boundary duty, tested against the clone shape that answered it wrongly.

Incident 32's rule, verbatim: every gate is tested against an artifact known to
fail it before the gate is trusted. The artifact is a `git clone --depth 1`,
which is the shape the host hands every run, and on it the typed command nine
audits used prints nothing over a repository whose history does carry a private
path. One run of this seat published that empty output as a clean boundary on
2026-11-09. The clones here are built locally rather than fetched, so the test
is offline and the shapes are exact.

    python3 -m pytest tests/test_history_boundary.py -q
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "history_boundary.py"
spec = importlib.util.spec_from_file_location("history_boundary", TOOL)
gate = importlib.util.module_from_spec(spec)
sys.modules["history_boundary"] = gate
spec.loader.exec_module(gate)


def git(repo, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    if check:
        assert proc.returncode == 0, proc.stderr
    return proc.stdout


@pytest.fixture
def origin(tmp_path):
    """A remote whose history adds a private path and then deletes it.

    That is this repository's own shape: `digests/2026-W37.md` was added on
    2026-09-08 and deleted by the commit that made digests private, so the
    working tree is clean and the history is not.
    """
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init", "-q", "-b", "main")
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        git(work, "config", k, v)
    (work / "README.md").write_text("# r\n")
    git(work, "add", "README.md")
    git(work, "commit", "-q", "-m", "first")

    private = work / "digests"
    private.mkdir()
    (private / "2026-W37.md").write_text("the private edition\n")
    git(work, "add", "digests/2026-W37.md")
    git(work, "commit", "-q", "-m", "digest 2026-W37 (first edition)")

    git(work, "rm", "-q", "-r", "digests")
    (work / ".gitignore").write_text("digests/\nsite/content/digests/\n")
    git(work, "add", ".gitignore")
    git(work, "commit", "-q", "-m", "digests go private")

    for _ in range(3):
        (work / "f").write_text(str(_))
        git(work, "add", "f")
        git(work, "commit", "-q", "-m", f"later {_}")

    bare = tmp_path / "origin.git"
    git(work, "clone", "-q", "--bare", str(work), str(bare))
    return bare


def clone(origin, dest, *flags):
    """`file://` on purpose: git ignores --depth for a plain local path.

    A local clone hardlinks the object store and comes out complete, so a test
    that asked for depth 1 over a path would quietly measure a full clone and
    pass for the wrong reason. The host fetches over https, and `file://` is the
    nearest transport that honours the depth.
    """
    proc = subprocess.run(
        ["git", "clone", "-q", *flags, f"file://{origin}", str(dest)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return dest


def run_tool(repo, *args):
    """The real tool from the real checkout, pointed at a test clone.

    `--repo` rather than copying the file into each clone, because the guard it
    borrows imports three other modules under `tools/` and a test that has to
    reproduce an import graph is testing the wrong thing.
    """
    return subprocess.run(
        [sys.executable, str(TOOL), "--repo", str(repo), *args],
        capture_output=True, text=True, cwd=str(REPO),
    )


# ---------------- the shape that got published wrong ----------------


def test_a_depth_one_clone_refuses_rather_than_reporting_absent(origin, tmp_path):
    """The whole finding. The typed command prints nothing here; this exits 2."""
    repo = clone(origin, tmp_path / "shallow", "--depth", "1")

    typed = git(repo, "log", "--all", "--diff-filter=A", "--oneline",
                "--", "digests/", "site/content/digests/")
    assert typed.strip() == "", "the premise of this test is that the typed command is silent here"
    assert git(repo, "rev-list", "--all", "--count").strip() == "1"

    proc = run_tool(repo)
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "COULD NOT LOOK" in proc.stderr
    assert "not an answer of 'absent from history'" in proc.stderr
    assert proc.stdout == ""


def test_the_same_clone_unshallowed_finds_it(origin, tmp_path):
    """The control that makes the refusal mean something rather than being a stuck gate."""
    repo = clone(origin, tmp_path / "deepened", "--depth", "1")
    git(repo, "config", "--add", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
    git(repo, "fetch", "-q", "--unshallow")

    proc = run_tool(repo)
    assert proc.returncode == gate.PRESENT, proc.stdout + proc.stderr
    assert "PRESENT in history" in proc.stdout
    assert "digests/" in proc.stdout


def test_a_narrow_refspec_after_unshallow_is_also_a_refusal(origin, tmp_path):
    """--unshallow deepens history without widening the refspec, three runs' worth of cost."""
    repo = clone(origin, tmp_path / "narrow", "--depth", "1")
    git(repo, "fetch", "-q", "--unshallow")
    assert "refs/heads/*" not in git(repo, "config", "--get-all", "remote.origin.fetch")

    proc = run_tool(repo)
    assert proc.returncode == gate.CANNOT_LOOK, proc.stdout
    assert "refspec" in proc.stderr


# ---------------- the answers ----------------


def test_a_full_clone_names_the_commit_and_prints_no_content(origin, tmp_path):
    repo = clone(origin, tmp_path / "full")
    proc = run_tool(repo)
    assert proc.returncode == gate.PRESENT
    assert "the private edition" not in proc.stdout, "private content must never be quoted"
    assert "2026-W37" in proc.stdout


def test_a_clean_history_exits_zero_and_carries_its_denominator(tmp_path):
    """A repository that never held a private path. The pass is not an empty line."""
    work = tmp_path / "clean"
    work.mkdir()
    git(work, "init", "-q", "-b", "main")
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        git(work, "config", k, v)
    (work / "README.md").write_text("# c\n")
    git(work, "add", "README.md")
    git(work, "commit", "-q", "-m", "first")
    (work / "second").write_text("x\n")
    git(work, "add", "second")
    git(work, "commit", "-q", "-m", "second")
    bare = tmp_path / "clean.git"
    git(work, "clone", "-q", "--bare", str(work), str(bare))

    repo = clone(bare, tmp_path / "cleanclone")
    proc = run_tool(repo)
    assert proc.returncode == gate.ABSENT, proc.stdout + proc.stderr
    assert proc.stdout.strip(), "a duty whose quiet means clean must not be quiet"
    assert "absent:" in proc.stdout
    assert "commits" in proc.stdout and "refs" in proc.stdout


def test_json_carries_the_scope_so_a_reader_can_tell_measurement_from_silence(origin, tmp_path):
    repo = clone(origin, tmp_path / "j")
    proc = run_tool(repo, "--json")
    out = json.loads(proc.stdout)
    assert out["absent"] is False
    assert out["scope"]["commits"] > 1
    assert out["scope"]["refs"] >= 1
    assert out["paths"]["digests/"][0]["commit"]


def test_json_on_a_refusal_says_absent_is_unknown_rather_than_true(origin, tmp_path):
    repo = clone(origin, tmp_path / "jr", "--depth", "1")
    proc = run_tool(repo, "--json")
    out = json.loads(proc.stdout)
    assert out["absent"] is None
    assert "cannot_look" in out


def test_one_path_can_be_measured_alone(origin, tmp_path):
    repo = clone(origin, tmp_path / "p")
    proc = run_tool(repo, "--path", "site/content/digests/")
    assert proc.returncode == gate.ABSENT, proc.stdout + proc.stderr
    assert "digests/:" not in proc.stdout.replace("site/content/digests/", "")


# ---------------- the contract ----------------


def test_the_standing_list_is_the_charter_s_two_paths():
    assert gate.PRIVATE_PATHS == ("digests/", "site/content/digests/")


def test_the_three_exit_codes_are_distinct():
    assert len({gate.ABSENT, gate.PRESENT, gate.CANNOT_LOOK}) == 3
    assert gate.ABSENT == 0


def test_self_check_prints_and_exits_zero():
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--self-check"], capture_output=True, text=True
    )
    assert proc.returncode == 0
    assert "--depth 1" in proc.stdout


def test_this_repository_s_own_known_instance_is_found():
    """Not synthetic: run against the checkout this test is in."""
    if gate.preflight() is not None:
        pytest.skip("this clone cannot see the history, which the gate itself reports")
    result = gate.check()
    assert result["absent"] is False
    rows = result["paths"]["digests/"]
    assert [r["commit"] for r in rows] == ["043767e5"], rows
    assert result["paths"]["site/content/digests/"] == []
