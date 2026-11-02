"""The root-scratch gate, which exists because five ignore rules did not work.

Each test names the instance it would have caught. The class is
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
six instances as of 2026-11-02 and two of them still tracked on `main`.
"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import root_scratch        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd):
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


@pytest.fixture
def repo(tmp_path):
    """A two-commit repository whose second commit is a branch, like a seat's."""
    git("init", "-q", "-b", "main", str(tmp_path), cwd=tmp_path.parent)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "t", cwd=tmp_path)
    (tmp_path / "README.md").write_text("base\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("base\n")
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "base", cwd=tmp_path)
    git("checkout", "-q", "-b", "work", cwd=tmp_path)
    return tmp_path


def test_an_unchanged_root_is_silent(repo):
    (repo / "docs" / "second.md").write_text("work\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "work", cwd=repo)
    findings, note = root_scratch.added("main", root=repo)
    assert (findings, note) == ([], "")


def test_the_sixth_instance_is_caught_and_the_five_ignore_lines_miss_it(repo):
    """`.dfseries.txt`, this gate's own run, matching none of the five lines."""
    (repo / ".dfseries.txt").write_text("07:15:37 2112\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "work", cwd=repo)
    findings, _ = root_scratch.added("main", root=repo)
    assert len(findings) == 1
    assert findings[0].startswith(".dfseries.txt: added to the checkout root")


def test_the_fifth_instance_is_caught_under_a_name_no_rule_predicted(repo):
    """`.scratch_mech.py`, which the fourth instance predicted in writing."""
    (repo / ".scratch_mech.py").write_text("print(1)\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "work", cwd=repo)
    findings, _ = root_scratch.added("main", root=repo)
    assert [f.split(":")[0] for f in findings] == [".scratch_mech.py"]


def test_a_root_file_added_on_purpose_passes_with_allow(repo):
    (repo / "sources.yaml").write_text("- a\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "work", cwd=repo)
    assert root_scratch.added("main", root=repo, allow=["sources.yaml"]) == ([], "")


def test_an_unnameable_base_says_so_instead_of_blaming_every_root_file(repo):
    """A shallow clone cannot name every branch, and the gate must not then
    report the whole root as newly added."""
    findings, note = root_scratch.added("origin/nothing-like-this", root=repo)
    assert findings == []
    assert "cannot be named here" in note


def test_this_repository_s_own_root_passes_against_main():
    """The gate is run by this run before readying, so it has to be green here."""
    findings, note = root_scratch.added("origin/main", root=ROOT)
    assert findings == [], findings
    assert note in ("", "origin/main cannot be named here, so the root was not compared")
