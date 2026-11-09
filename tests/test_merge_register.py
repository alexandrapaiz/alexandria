#!/usr/bin/env python3
"""The vendored register merger does what this repository needs it to do.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

`tools/merge_register.py` is HQ's `tools/merge-register.py`, vendored on
2026-11-09 on a handoff from `alexandria/exo`, which measured that seven of its
eight open pull requests conflicted with `main` and that every conflicting file
was an append-only register under `docs/agents/`. `docs/standards/pm.md` §864
names this tool as the cure and says in the same breath that it is not a merge
driver, because L-A49 measured all three `.gitattributes` arms and the forge
honours none. So it is run by hand, and these are the tests for the claims the
vendoring itself makes.

Nothing here touches the network. The provenance test reads the header rather
than re-fetching from HQ, which is deliberate: a test that called the GitHub
API would be red on every offline run and would then be pinned or deleted.
What it asserts is that the header carries enough to make drift checkable by
hand, which is the part that rots.
"""

import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "merge_register.py"
sys.path.insert(0, str(ROOT / "tools"))

import merge_register as mr  # noqa: E402


def run(base, ours, theirs, tmp_path, *extra):
    paths = []
    for name, text in (("base", base), ("ours", ours), ("theirs", theirs)):
        p = tmp_path / f"{name}.md"
        p.write_text(text, encoding="utf-8")
        paths.append(str(p))
    return subprocess.run(
        [sys.executable, str(TOOL), *extra, *paths],
        capture_output=True, text=True)


# --------------------------------------------------------------------------
# The vendoring's own claims
# --------------------------------------------------------------------------

def test_the_header_says_where_this_came_from_and_at_which_blob():
    """A vendored file whose header cannot be checked against its source is a
    fork nobody has noticed yet.

    `docs/agents/cross-repo-law.md` asks for the vendored copies to be checked
    "against the commit they claim", which requires the copy to claim one. The
    sha is asserted as a 40-hex blob id rather than as a literal, so re-vendoring
    updates one line and does not have to update this test.
    """
    head = TOOL.read_text(encoding="utf-8")[:4000]
    assert "alexandrapaiz/alexandra-systems" in head
    assert "tools/merge-register.py" in head, "the source path is not recorded"
    assert re.search(r"blob sha\s+[0-9a-f]{40}", head), "no checkable blob sha"
    assert re.search(r"last commit\s+[0-9a-f]{40}", head), "no source commit"


def test_the_usage_line_names_a_path_that_exists_here():
    """`docs/agents/cross-repo-law.md`: a tool path in a vendored sentence is
    readable without a filesystem call, and a hyphen in a `tools/` path means
    the path belongs to the parent.

    The one edit this vendoring makes to the body is the usage line, and this
    is why. Byte-identical would have told every reader here to run a file that
    does not exist, which is the exact defect that rule was written for: 44 of
    45 tool paths named in the vendored standards were absent here.
    """
    usage = [l for l in TOOL.read_text(encoding="utf-8").splitlines()
             if "--heading" in l and "tools/" in l]
    assert usage, "no usage line found in the docstring"
    for line in usage:
        named = re.search(r"tools/\S+\.py", line).group(0)
        assert (ROOT / named).exists(), f"usage line names {named}, which is absent"


# --------------------------------------------------------------------------
# The fence guard, which is why the vendoring took HQ head and not the pin
# --------------------------------------------------------------------------

def test_a_hash_line_inside_a_fence_is_not_an_entry_start(tmp_path):
    """The guard HQ added in 9a12e957, six days after the content Ursa pinned.

    Before it, the heading pattern was tested against every line, so an entry
    quoting a shell comment that begins with hashes was split at that line and
    everything after it was reattributed to a key read out of a code sample.
    That is the only way this tool can fail while still returning a file.
    """
    base = "# R\n\n"
    entry = (
        "## 2026-11-09 - an entry that quotes a command\n\n"
        "```\n"
        "## this is a comment inside a fence, not a heading\n"
        "git log --oneline\n"
        "```\n\n"
        "The sentence after the fence belongs to this entry.\n\n"
    )
    done = run(base, base + entry, base, tmp_path, "--heading", "^## ")
    assert done.returncode == 0, done.stderr
    assert done.stdout.count("## this is a comment inside a fence") == 1
    assert "The sentence after the fence belongs to this entry." in done.stdout
    # The real proof: the quoted line did not become an entry of its own.
    _, entries = mr.parse(done.stdout, re.compile("^## "))
    headings = [key for key, _block in entries]
    assert len(headings) == 1, headings
    assert not any("inside a fence" in h for h in headings), headings


def test_the_fence_reader_closes_on_the_second_fence_and_runs_to_eof_unclosed():
    """Both halves of `fenced`, because an unclosed fence is the ambiguous case
    and the tool chooses the safe direction deliberately."""
    closed = "a\n```\nb\n```\nc\n".splitlines()
    assert mr.fenced(closed) == {1, 2, 3}
    unclosed = "a\n```\nb\nc\n".splitlines()
    assert mr.fenced(unclosed) == {1, 2, 3}


# --------------------------------------------------------------------------
# What it does on this repository's shapes
# --------------------------------------------------------------------------

def test_two_sides_appending_different_entries_both_survive(tmp_path):
    """The whole point. This is the conflict every seat here keeps producing:
    two runs appending to one register tail, which is not a disagreement."""
    base = "# R\n\n## 2026-11-07 - old\n\nbody\n\n"
    ours = base + "## 2026-11-09 - mine\n\nmine\n\n"
    theirs = base + "## 2026-11-08 - theirs\n\ntheirs\n\n"
    done = run(base, ours, theirs, tmp_path, "--heading", "^## ")
    assert done.returncode == 0, done.stderr
    for heading in ("2026-11-07 - old", "2026-11-08 - theirs", "2026-11-09 - mine"):
        assert heading in done.stdout, heading
    # Nothing blended: each entry's body is intact and unduplicated.
    for body in ("mine", "theirs"):
        assert done.stdout.count(f"\n{body}\n") == 1, body


def test_a_duplicate_entry_on_either_side_is_refused_and_nothing_is_written(tmp_path):
    """The refusal this repository actually met, in both directions.

    `alexandria/exo` found it against `main` on 2026-11-09 and repaired the
    duplicate that caused it. This run re-ran the tool on PR #890's live
    conflict after that repair merged and met the same refusal with the sides
    swapped: the stale copy is now on the branch, because the branch's base
    predates the repair. The refusal moving rather than disappearing is the
    behaviour, and it is correct both times.
    """
    base = "# R\n\n"
    dupe = "## 2026-11-09 - twice\n\nbody\n\n"
    for ours, theirs in ((base + dupe + dupe, base), (base, base + dupe + dupe)):
        done = run(base, ours, theirs, tmp_path, "--heading", "^## ")
        assert done.returncode != 0
        assert "twice" in done.stderr + done.stdout
        assert done.stdout.strip() == "", "refused and still wrote something"


def test_the_invocations_the_header_documents_find_this_repositorys_entries():
    """The header names a `--heading` per register, and an invocation nobody has
    run against the real file is a guess.

    A pattern that matched nothing would not fail here: the tool would merge a
    one-entry document and exit 0, which is in band. So this asserts a floor on
    each register rather than only that the pattern compiles. That is the
    control Ursa's ExO seat's 2026-11-09 triage asks for.
    """
    expected = {
        "docs/agents/learning-log.md": ("^## ", 50),
        "docs/agents/incidents.md": ("^## ", 200),
        "docs/ideas.md": ("^### ", 500),
        "docs/decisions.md": ("^## ", 30),
    }
    for name, (pattern, floor) in expected.items():
        path = ROOT / name
        assert path.exists(), name
        _, entries = mr.parse(path.read_text(encoding="utf-8"), re.compile(pattern))
        assert len(entries) >= floor, (
            f"{name} parses {len(entries)} entries under {pattern!r}, below the "
            f"floor of {floor}; the documented invocation is wrong for this file")


def test_the_adr_register_merges_by_number_and_refuses_a_minted_collision(tmp_path):
    """`docs/decisions.md` is numbered, so the identifier mode is the one the
    header documents for it. The failure that mode exists to prevent is the
    silent one: an `--identifier` that matches nothing degrades to a date-keyed
    merge and publishes a duplicate number at exit 0.
    """
    base = "# D\n\n## ADR-1: first\n\nbody\n\n"
    ours = base + "## ADR-2: mine\n\nmine\n\n"
    theirs = base + "## ADR-2: theirs\n\ntheirs\n\n"
    done = run(base, ours, theirs, tmp_path,
               "--heading", "^## ", "--identifier", r"^## (ADR-[0-9]+)")
    assert done.returncode != 0, (
        "two sides minted ADR-2 and the merge published both:\n" + done.stdout)
    assert "ADR-2" in done.stderr + done.stdout
