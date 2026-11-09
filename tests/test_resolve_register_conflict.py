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
from unittest import mock
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


# ---------------------------------------------------------------------------
# The merge direction the seats actually use, and the order it used to produce.
#
# `INC-2026-11-09-the-register-resolver-orders-two-appends-backwards-in-the-only-merge-direction-we-use`:
# a seat clearing a conflict runs `git merge origin/main` from its own branch,
# because that is how you do it without rewriting pushed history. So ours is the
# branch and theirs is the trunk, and the first version of this tool put the
# branch's newer entry above the trunk's older one on every one of them. The ExO
# seat measured two registers that way and resolved both by hand.

EARLIER_APPEND = """
### 2026-11-09 09:05 - the trunk's entry
- What: landed on main first
- Status: proposed
"""

LATER_APPEND = """
### 2026-11-09 09:25 - the branch's entry
- What: stamped twenty minutes after the trunk's
- Status: proposed
"""


def trunk_merged_into_branch(repo, branch=LATER_APPEND, trunk=EARLIER_APPEND,
                             path="docs/ideas.md"):
    """The only direction we use: the branch is checked out and main is merged in.

    So `ours` is the branch and `theirs` is the trunk, which is the opposite of
    what `two_appends` above sets up and of what the tool's first version assumed.
    """
    file = repo / path
    base = file.read_text()

    git(repo, "checkout", "-q", "-b", "seat")
    file.write_text(base + branch)
    git(repo, "commit", "-qam", "the seat's append, stamped later")

    git(repo, "checkout", "-q", "main")
    file.write_text(base + trunk)
    git(repo, "commit", "-qam", "the trunk's append, stamped earlier")

    git(repo, "checkout", "-q", "seat")
    done = git(repo, "merge", "--no-edit", "main", check=False)
    assert done.returncode != 0, "the fixture is supposed to conflict"
    return done


def test_merging_the_trunk_into_a_branch_still_puts_the_earlier_entry_first(repo):
    """The defect, as the ExO seat met it twice in one run."""
    trunk_merged_into_branch(repo)
    state, said = rrc.resolve_one("docs/ideas.md", repo=repo)

    assert state == rrc.RESOLVED, said
    text = (repo / "docs" / "ideas.md").read_text()
    assert text.index("the trunk's entry") < text.index("the branch's entry"), \
        "the newer block landed above the older one, which is the 2026-11-09 defect"
    assert "theirs first" in said[0] and "stamp order" in said[0]


def test_the_report_names_the_rule_it_ordered_by_rather_than_claiming_ours_first(repo):
    """The old report said "ours first" on a register written backwards."""
    trunk_merged_into_branch(repo)
    _, said = rrc.resolve_one("docs/ideas.md", repo=repo, write=False)
    assert "ours first" not in said[0]
    assert said[0].endswith("by stamp order, theirs is the earlier block")


def test_the_stamp_decides_it_in_both_directions(repo):
    """Direction-independence is the point: the same two blocks, merged either way."""
    trunk_merged_into_branch(repo)
    rrc.resolve_one("docs/ideas.md", repo=repo)
    one = (repo / "docs" / "ideas.md").read_text()

    git(repo, "merge", "--abort", check=False)
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "--no-edit", "seat", check=False)
    rrc.resolve_one("docs/ideas.md", repo=repo)
    other = (repo / "docs" / "ideas.md").read_text()

    assert one == other, "the resolution depended on which way the merge was typed"


def test_the_order_check_is_not_blind_to_a_register_written_backwards():
    """The half the line arithmetic cannot see.

    The multiset check reads this resolution as balanced, because every line of
    both sides is present exactly once. It is only the order that is wrong, and
    that is how both of the ExO seat's registers passed their own gate.
    """
    base = BASE
    ours = BASE + LATER_APPEND      # the branch, stamped 09:25
    theirs = BASE + EARLIER_APPEND  # the trunk, stamped 09:05
    backwards = BASE + LATER_APPEND + EARLIER_APPEND

    assert rrc.audit(base, ours, theirs, backwards) == [], \
        "the multiset check is supposed to be order-blind; that is the premise here"

    findings = rrc.order_findings(base, ours, theirs, backwards)
    assert len(findings) == 1
    assert findings[0].startswith("out of order: 2026-11-09 09:25 is above 2026-11-09 09:05")

    forwards = BASE + EARLIER_APPEND + LATER_APPEND
    assert rrc.order_findings(base, ours, theirs, forwards) == []


def test_check_on_a_committed_merge_reports_the_backwards_order(repo):
    """`--check`, which is the mode that audits a resolution already pushed."""
    trunk_merged_into_branch(repo)
    file = repo / "docs" / "ideas.md"
    file.write_text(BASE + LATER_APPEND + EARLIER_APPEND)  # a hand resolution, ours first
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "merge, resolved by hand the way the tool used to")

    state, report = rrc.check_commit("HEAD", repo=repo, registers=["docs/ideas.md"])
    assert state == rrc.REFUSED, report
    assert any("out of order" in line for line in report)


def test_equal_stamps_fall_back_to_the_trunk_side_and_say_so(repo):
    """When the stamp cannot decide, the trunk label can, and it is still not "ours"."""
    trunk_merged_into_branch(repo, branch=THEIRS_APPEND, trunk=OURS_APPEND)
    state, said = rrc.resolve_one("docs/ideas.md", repo=repo)

    assert state == rrc.RESOLVED, said
    text = (repo / "docs" / "ideas.md").read_text()
    assert text.index("the writer's entry") < text.index("the engineer's entry"), \
        "the trunk's block should lead when the stamps tie"
    assert "same stamp" in said[0] and "theirs is the trunk" in said[0]


def test_neither_side_on_the_trunk_and_no_stamp_to_separate_them_is_refused(repo):
    """Two branches merged off-trunk with tied stamps: no rule can speak, so refuse."""
    file = repo / "docs" / "ideas.md"
    base = file.read_text()
    git(repo, "checkout", "-q", "-b", "one")
    file.write_text(base + OURS_APPEND)
    git(repo, "commit", "-qam", "one")
    git(repo, "checkout", "-q", "-b", "two", "main")
    file.write_text(base + THEIRS_APPEND)
    git(repo, "commit", "-qam", "two")
    git(repo, "checkout", "-q", "one")
    assert git(repo, "merge", "--no-edit", "two", check=False).returncode != 0

    state, said = rrc.resolve_one("docs/ideas.md", repo=repo)
    assert state == rrc.REFUSED
    assert "neither side is reachable from the trunk" in said[0]
    assert "<<<<<<<" in file.read_text(), "a refused file must be left as git left it"


def test_the_stamp_reads_every_heading_shape_the_registers_use():
    """Four shapes across the sixteen registers, agreeing on nothing but the date."""
    shapes = {
        "### 2026-11-09 - Idea name": (2026, 11, 9, -1, -1),
        "## INC-2026-11-09-a-slug - what happened (2026-11-09, writer seat)":
            (2026, 11, 9, -1, -1),
        "## 2026-11-09 09:12 - message wake": (2026, 11, 9, 9, 12),
        "## Queued 2026-11-09 by the skill seat": (2026, 11, 9, -1, -1),
    }
    for heading, key in shapes.items():
        found = rrc.stamp(["", heading, "- body"])
        assert found is not None, heading
        assert found[0] == key, heading
        assert found[1] == heading

    assert rrc.stamp(["", "## no date anywhere in this block", "- body"]) is None


def test_a_stamped_time_outranks_the_bare_date_it_shares():
    """Two entries on one day: the one with a clock on it is not equal to the one without."""
    bare = rrc.stamp(["### 2026-11-09 - no clock"])
    timed = rrc.stamp(["### 2026-11-09 09:05 - a clock"])
    assert bare[0] < timed[0], "a bare date sorts before any time on the same day"


def test_order_findings_abstains_when_it_cannot_localise_a_block():
    """L-A21: a check that cannot see the thing must not vote on it."""
    base = "# Ideas\n\n### 2026-11-09 - repeated heading\n"
    ours = base + "\n### 2026-11-09 - repeated heading\n"
    theirs = base + "\n### 2026-11-10 - the other side\n"
    resolved = base + "\n### 2026-11-09 - repeated heading\n\n### 2026-11-10 - the other side\n"
    assert rrc.order_findings(base, ours, theirs, resolved) == []


# ---------------- a question that cannot be asked is not an answer ----------------


def test_an_unresolvable_ref_refuses_instead_of_reporting_the_register_absent(repo):
    """The conflation this tool's own `None` carried until 2026-11-09.

    `git show` exits non-zero both for an absent path and for a ref it cannot
    resolve, so a bad ref read as "the register is not in that tree" and the
    audit skipped it without saying so.
    """
    with pytest.raises(RuntimeError) as caught:
        rrc.blob("no-such-ref-at-all", "docs/agents/incidents.md", repo=repo)
    assert "does not resolve" in str(caught.value)


def test_a_genuinely_absent_path_still_answers_none(repo):
    """The control. Without it the test above would pass on a `blob` that raised
    for everything, which would be a different bug and not a fix."""
    assert rrc.blob("HEAD", "docs/no-such-register-anywhere.md", repo=repo) is None


def test_check_commit_names_the_registers_it_did_not_audit(repo):
    """Coverage narrower than the question used to be silent, and silence from
    an auditor reads as a verdict on everything it was asked about."""
    two_appends(repo)
    rrc.resolve_one("docs/ideas.md", repo=repo)
    git(repo, "commit", "-qm", "merge, resolved by the tool")
    state, report = rrc.check_commit(
        "HEAD", repo=repo,
        registers=["docs/ideas.md", "docs/not-a-real-register.md"])
    joined = "\n".join(report)
    assert "were not audited" in joined, joined
    assert "docs/not-a-real-register.md" in joined
    # The register that is there is still audited, so this is a named gap in
    # coverage rather than a refusal to answer at all.
    assert "docs/ideas.md" in joined


def test_every_git_call_carries_a_timeout(repo):
    """Until 2026-11-09 the single git helper here had no timeout at all."""
    seen = []
    real = subprocess.run

    def recording(*args, **kwargs):
        seen.append(kwargs.get("timeout"))
        return real(*args, **kwargs)

    with mock.patch.object(rrc.subprocess, "run", recording):
        rrc.conflicted(repo=repo)
        rrc.blob("HEAD", "docs/agents/incidents.md", repo=repo)
    assert seen, "no git call was made, so this test proves nothing"
    assert all(t is not None for t in seen), seen


def test_no_git_binary_refuses_and_says_no_register_was_audited(repo, capsys):
    def missing(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "git")

    with mock.patch.object(rrc.subprocess, "run", missing):
        assert rrc.main(["--check", "HEAD", "--repo", str(repo)]) == rrc.EXIT[rrc.NOTHING]
    assert "could not be asked" in capsys.readouterr().err
