"""Does the anchor reader tell a fold from a bypass, and a long file from an anchor.

Run with `python3 -m pytest tests/test_anchor_contention.py -q`.

`tools/anchor_contention.py` measures the open pull request set, which is not
present on a checkout and needs the network to read. So every test here hands it
the file lists directly, in the shape `gh pr view --json files` returns, and
nothing here calls `gh`.

Two distinctions carry the whole file and both are easy to get wrong in the
direction that flatters the remedy.

A `fold` touches the anchor and is not contention: it is the one-writer movement
the inbox exists to enable, and counting it as a bypass would report the remedy
as failing precisely when it is working. A `both` is the mirror — it writes
inbox entries, so a diff summary reads as adoption, and it appends to the
register too, so it collides exactly like a bypass. The bypass rate is wrong in
one direction if either is misfiled, so both are asserted here by name.

The last test is the remedy's own prediction turned into an assertion: two passes
that each write their own dated file must produce no anchor at all. If that ever
fails, the file-per-pass rule has stopped being worth its cost.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import anchor_contention as ac  # noqa: E402

REGISTER = "docs/agents/incidents.md"
INBOX = "docs/agents/incidents/inbox/"


def pr(number, *files):
    """A pull request in the shape `gh pr view --json files` returns."""
    return {
        "number": number,
        "files": [
            {"path": p, "additions": a, "deletions": d} for p, a, d in files
        ],
    }


# --- discovery -------------------------------------------------------------

def test_a_register_is_discovered_from_the_inbox_beside_it(tmp_path):
    (tmp_path / "docs/agents/incidents/inbox").mkdir(parents=True)
    (tmp_path / "docs/agents/incidents.md").write_text("# register\n")
    assert ac.discover_registers(tmp_path) == {REGISTER: INBOX}


def test_a_second_inbox_appears_without_being_listed(tmp_path):
    """L-A18 names another register still owed an inbox; it must need no edit here."""
    (tmp_path / "docs/agents/incidents/inbox").mkdir(parents=True)
    (tmp_path / "docs/standards/lessons/inbox").mkdir(parents=True)
    found = ac.discover_registers(tmp_path)
    assert found == {
        REGISTER: INBOX,
        "docs/standards/lessons.md": "docs/standards/lessons/inbox/",
    }


def test_no_docs_directory_is_not_an_error(tmp_path):
    assert ac.discover_registers(tmp_path) == {}


# --- the four readings -----------------------------------------------------

def test_a_pull_request_that_does_not_touch_the_register_reads_as_nothing():
    p = pr(1, ("tools/thing.py", 10, 0))
    assert ac.classify(p, REGISTER, INBOX) is None


def test_writing_only_the_inbox_is_the_remedy_working():
    p = pr(2, (INBOX + "INC-a.md", 40, 0))
    assert ac.classify(p, REGISTER, INBOX) == "inbox"


def test_appending_to_the_register_with_no_inbox_entry_is_a_bypass():
    p = pr(3, (REGISTER, 51, 0))
    assert ac.classify(p, REGISTER, INBOX) == "bypass"


def test_removing_inbox_entries_into_the_register_is_a_fold_not_a_bypass():
    """The one-writer movement the inbox is built for. Miscounting it hides success."""
    p = pr(4, (REGISTER, 427, 0), (INBOX + "INC-a.md", 0, 109), (INBOX + "INC-b.md", 0, 55))
    assert ac.classify(p, REGISTER, INBOX) == "fold"


def test_writing_the_inbox_and_appending_too_is_both_not_inbox():
    """Reads as adoption in a diff summary and collides exactly like a bypass."""
    p = pr(5, (REGISTER, 110, 0), (INBOX + "INC-a.md", 30, 0))
    assert ac.classify(p, REGISTER, INBOX) == "both"


# --- contention ------------------------------------------------------------

def test_a_path_counts_once_per_pull_request_not_once_per_entry():
    p = pr(6, (REGISTER, 5, 0), (REGISTER, 7, 0))
    assert ac.contention([p])[REGISTER] == 1


def test_contention_counts_across_pull_requests():
    counts = ac.contention([pr(7, (REGISTER, 1, 0)), pr(8, (REGISTER, 1, 0))])
    assert counts[REGISTER] == 2


def test_a_file_per_pass_produces_no_anchor():
    """The remedy's own prediction: new files collide with nothing, in any order."""
    passes = [
        pr(9, ("docs/sprints/pending/2026-11-01-2330-message.md", 13, 0)),
        pr(10, ("docs/sprints/pending/2026-11-01-2339-message.md", 13, 0)),
        pr(11, ("docs/sprints/pending/2026-11-02-0015-message.md", 13, 0)),
    ]
    assert max(ac.contention(passes).values()) == 1


# --- the rate --------------------------------------------------------------

def test_the_bypass_rate_excludes_folds():
    prs = [
        pr(12, (REGISTER, 427, 0), (INBOX + "INC-a.md", 0, 109)),  # fold
        pr(13, (INBOX + "INC-b.md", 40, 0)),                        # inbox
        pr(14, (REGISTER, 51, 0)),                                  # bypass
    ]
    r = ac.measure(prs, {REGISTER: INBOX})["registers"][REGISTER]
    assert (r["touching"], r["folds"], r["using_inbox"], r["bypassing"]) == (3, 1, 1, 1)
    assert r["bypass_rate"] == pytest.approx(0.5)


def test_a_register_nothing_contests_has_no_rate_rather_than_a_zero():
    """Division by nobody. A rate of 0% would read as perfect adoption."""
    r = ac.measure([pr(15, ("tools/thing.py", 1, 0))], {REGISTER: INBOX})["registers"][REGISTER]
    assert r["touching"] == 0 and r["bypass_rate"] is None


# --- the exit code ---------------------------------------------------------

def test_contention_alone_does_not_fail(tmp_path, capsys):
    """Report-only by default: contention is a cost, not an error."""
    prs = [pr(n, (REGISTER, 1, 0)) for n in range(20, 30)]
    path = tmp_path / "prs.json"
    path.write_text(json.dumps(prs))
    assert ac.main(["--prs", str(path), "--root", str(tmp_path)]) == 0


def test_max_anchor_fails_when_exceeded_and_names_the_path(tmp_path, capsys):
    prs = [pr(n, (REGISTER, 1, 0)) for n in range(30, 37)]
    path = tmp_path / "prs.json"
    path.write_text(json.dumps(prs))
    assert ac.main(["--prs", str(path), "--root", str(tmp_path), "--max-anchor", "6"]) == 1
    assert REGISTER in capsys.readouterr().err


def test_max_anchor_passes_at_the_threshold_rather_than_one_below_it(tmp_path):
    """`--max-anchor 6` means six is allowed. An off-by-one here cries wolf weekly."""
    prs = [pr(n, (REGISTER, 1, 0)) for n in range(40, 46)]
    path = tmp_path / "prs.json"
    path.write_text(json.dumps(prs))
    assert ac.main(["--prs", str(path), "--root", str(tmp_path), "--max-anchor", "6"]) == 0


def test_the_json_report_is_machine_readable(tmp_path, capsys):
    path = tmp_path / "prs.json"
    path.write_text(json.dumps([pr(50, (REGISTER, 1, 0))]))
    ac.main(["--prs", str(path), "--root", str(tmp_path), "--json"])
    report = json.loads(capsys.readouterr().out)
    assert report["open_prs"] == 1
    assert report["anchors"][0]["path"] == REGISTER
