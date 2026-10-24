"""Resolving two register appends, and proving the resolution lost nothing.

`tools/resolve_register_conflict.py` exists because a hand resolution deleted a
third seat's status line on 2026-10-24 and left valid Markdown behind
(`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`).
So the fixtures here are real merges in real git repositories that really
conflict, and the assertions are about the bytes on the other side.

The arithmetic is the part worth testing hardest. It has to catch both halves of
what a bad resolution does: a line one side had and the result does not, which
is that incident, and a line counted twice, which is what `merge=union` does to
the shared trailing lines of two appended entries and the measured reason
company lesson L-A49 forbids the attribute.
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "resolve_register_conflict",
        ROOT / "tools" / "resolve_register_conflict.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


rrc = _module()

BASE = """# Ideas

### 2026-10-20 - an old entry
- What: something
- Status: proposed
"""

OURS_APPEND = """
### 2026-10-24 - the writer's entry
- What: a relay filing
- Status: proposed
"""

THEIRS_APPEND = """
### 2026-10-24 - the engineer's entry
- What: a craft scan
- Status: proposed
"""


def git(repo, *args, check=True):
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    if check:
        assert done.returncode == 0, done.stderr
    return done


@pytest.fixture
def repo(tmp_path):
    """A repository whose `docs/ideas.md` two branches will both append to."""
    path = tmp_path / "repo"
    (path / "docs").mkdir(parents=True)
    git(path.parent, "init", "-q", "-b", "main", str(path))
    git(path, "config", "user.email", "seat@example.com")
    git(path, "config", "user.name", "seat")
    (path / "docs" / "ideas.md").write_text(BASE)
    git(path, "add", "-A")
    git(path, "commit", "-qm", "base")
    return path


def two_appends(repo, ours=OURS_APPEND, theirs=THEIRS_APPEND, path="docs/ideas.md"):
    """main gets `ours`, a branch gets `theirs`, and the branch is merged into main."""
    file = repo / path
    base = file.read_text()

    git(repo, "checkout", "-q", "-b", "seat")
    file.write_text(base + theirs)
    git(repo, "commit", "-qam", "the seat's append")

    git(repo, "checkout", "-q", "main")
    file.write_text(base + ours)
    git(repo, "commit", "-qam", "main's append")

    done = git(repo, "merge", "--no-edit", "seat", check=False)
    assert done.returncode != 0, "the fixture is supposed to conflict"
    return done


def test_two_appends_at_one_anchor_resolve_to_both_in_arrival_order(repo):
    two_appends(repo)
    state, said = rrc.resolve_one("docs/ideas.md", repo=repo)

    assert state == rrc.RESOLVED
    text = (repo / "docs" / "ideas.md").read_text()
    assert "<<<<<<<" not in text and "=======" not in text.replace("\n", "")
    assert "the writer's entry" in text and "the engineer's entry" in text
    assert text.index("the writer's entry") < text.index("the engineer's entry")
    assert text.count("- Status: proposed") == 3
    assert said[0].startswith("docs/ideas.md: kept both appends")


def test_the_resolution_is_staged_so_the_merge_can_be_committed(repo):
    two_appends(repo)
    rrc.resolve_one("docs/ideas.md", repo=repo)

    assert rrc.conflicted(repo=repo) == []
    git(repo, "commit", "-qm", "merge, resolved by the tool")
    state, report = rrc.check_commit("HEAD", repo=repo, registers=["docs/ideas.md"])
    assert state == rrc.RESOLVED, report
    assert "balanced" in report[0]


def test_dry_run_writes_nothing_and_stages_nothing(repo):
    two_appends(repo)
    before = (repo / "docs" / "ideas.md").read_text()
    state, _ = rrc.resolve_one("docs/ideas.md", repo=repo, write=False)

    assert state == rrc.RESOLVED
    assert (repo / "docs" / "ideas.md").read_text() == before
    assert rrc.conflicted(repo=repo) == ["docs/ideas.md"]


def test_a_side_that_edited_an_existing_line_is_refused_rather_than_concatenated(repo):
    """Keeping both sides of an edit is not the same operation as keeping both appends.

    The owner's verdict on the last entry and a seat's new entry land on
    adjacent lines, which is the one place an edit and an append collide, and it
    is the realistic case: `- Status: accepted` is written at the bottom of the
    file, where the next append also goes.
    """
    file = repo / "docs" / "ideas.md"
    git(repo, "checkout", "-q", "-b", "seat")
    file.write_text(BASE.replace("- Status: proposed", "- Status: accepted"))
    git(repo, "commit", "-qam", "the owner's verdict on the last entry")
    git(repo, "checkout", "-q", "main")
    file.write_text(BASE + OURS_APPEND)
    git(repo, "commit", "-qam", "main's append")
    done = git(repo, "merge", "--no-edit", "seat", check=False)
    assert done.returncode != 0, "the fixture is supposed to conflict"

    state, said = rrc.resolve_one("docs/ideas.md", repo=repo)
    assert state == rrc.REFUSED
    assert "not the end of the file" in said[0]
    assert "<<<<<<<" in file.read_text(), "a refused file must be left as git left it"


def test_a_file_added_on_both_sides_is_refused(repo):
    git(repo, "checkout", "-q", "-b", "seat")
    (repo / "docs" / "new.md").write_text("theirs\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "theirs")
    git(repo, "checkout", "-q", "main")
    (repo / "docs" / "new.md").write_text("ours\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "ours")
    git(repo, "merge", "--no-edit", "seat", check=False)

    state, said = rrc.resolve_one("docs/new.md", repo=repo)
    assert state == rrc.REFUSED
    assert "all three stages" in said[0]


def test_a_path_that_is_not_a_register_is_refused_by_name(repo, capsys):
    """The recipe is only proven for append-only files, so the list is the gate."""
    file = repo / "app.py"
    git(repo, "checkout", "-q", "-b", "seat")
    file.write_text("def main():\n    return 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "theirs")
    git(repo, "checkout", "-q", "main")
    file.write_text("def main():\n    return 3\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "ours")
    git(repo, "merge", "--no-edit", "seat", check=False)

    code = rrc.main(["--repo", str(repo)])
    printed = capsys.readouterr().out
    assert code == rrc.EXIT[rrc.REFUSED]
    assert "app.py: refused, not an append-only register" in printed


def test_nothing_conflicted_exits_two_rather_than_reporting_clean(repo, capsys):
    """L-A21: a run that saw nothing is not a verdict on the registers."""
    code = rrc.main(["--repo", str(repo)])
    printed = capsys.readouterr().out
    assert code == rrc.EXIT[rrc.NOTHING] == 2
    assert "nothing here is a verdict" in printed


def test_the_audit_names_a_dropped_line_with_both_counts():
    """The 2026-10-24 incident, as arithmetic."""
    base, ours = BASE, BASE + OURS_APPEND
    theirs = BASE + THEIRS_APPEND
    lost = (BASE + OURS_APPEND + THEIRS_APPEND).replace(
        "- What: a craft scan\n- Status: proposed\n", "- What: a craft scan\n", 1)

    findings = rrc.audit(base, ours, theirs, lost)
    assert len(findings) == 1
    assert findings[0].startswith("dropped: 2 of an expected 3")
    assert "- Status: proposed" in findings[0]


def test_the_audit_names_a_duplicated_line_too():
    """What `merge=union` does to two entries that end in the same two lines (L-A49)."""
    base, ours = BASE, BASE + OURS_APPEND
    theirs = BASE + THEIRS_APPEND
    doubled = BASE + OURS_APPEND + THEIRS_APPEND + "- Status: proposed\n"

    findings = rrc.audit(base, ours, theirs, doubled)
    assert len(findings) == 1
    assert findings[0].startswith("duplicated: 4 of an expected 3")


def test_a_balanced_resolution_has_no_findings():
    base, ours = BASE, BASE + OURS_APPEND
    theirs = BASE + THEIRS_APPEND
    assert rrc.audit(base, ours, theirs, BASE + OURS_APPEND + THEIRS_APPEND) == []
    assert rrc.audit(base, ours, theirs, BASE + THEIRS_APPEND + OURS_APPEND) == []


def test_check_finds_the_dropped_line_in_a_commit_that_is_already_made(repo):
    """The mode the incident needed: the damage was committed and pushed before anyone looked."""
    two_appends(repo)
    file = repo / "docs" / "ideas.md"
    # A hand resolution that keeps both entries and loses one line on the seam,
    # which is what left no marker and no failing test on 2026-10-24.
    file.write_text(BASE + OURS_APPEND + THEIRS_APPEND.replace(
        "- What: a craft scan\n- Status: proposed\n", "- What: a craft scan\n", 1))
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "merge, resolved by hand")

    state, report = rrc.check_commit("HEAD", repo=repo, registers=["docs/ideas.md"])
    assert state == rrc.REFUSED
    assert "does not balance" in report[0]
    assert any("- Status: proposed" in line and "dropped" in line for line in report)


def test_check_on_a_commit_with_one_parent_says_so_and_exits_two(repo, capsys):
    code = rrc.main(["--repo", str(repo), "--check", "HEAD"])
    printed = capsys.readouterr().out
    assert code == rrc.EXIT[rrc.NOTHING]
    assert "is not a two-parent merge" in printed


def test_check_on_a_merge_that_touched_no_register_is_not_a_verdict(repo, capsys):
    git(repo, "checkout", "-q", "-b", "seat")
    (repo / "app.py").write_text("x = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "theirs")
    git(repo, "checkout", "-q", "main")
    (repo / "other.py").write_text("y = 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "ours")
    git(repo, "merge", "--no-edit", "seat")

    code = rrc.main(["--repo", str(repo), "--check"])
    printed = capsys.readouterr().out
    assert code == rrc.EXIT[rrc.NOTHING]
    assert "merged no register" in printed


def test_trailing_block_reads_an_append_and_rejects_anything_else():
    base = ["a", "b", "c"]
    assert rrc.trailing_block(base, ["a", "b", "c", "d"]) == ["d"]
    assert rrc.trailing_block(base, ["a", "b", "c"]) == []
    assert rrc.trailing_block(base, ["a", "X", "c", "d"]) is None
    assert rrc.trailing_block(base, ["a", "b"]) is None


def test_the_register_list_comes_from_the_checker_that_owns_it():
    """One list, one place: this file must not grow a second copy that goes stale."""
    registers = rrc._registers()
    assert "docs/ideas.md" in registers
    assert "docs/agents/incidents.md" in registers
    source = (ROOT / "tools" / "resolve_register_conflict.py").read_text()
    assert source.count('"docs/ideas.md"') == 0
