"""The ledger parser, tested against a ledger known to hide entries from a grep.

Incident 32's rule, verbatim: every gate is tested against an artifact known to
fail it before the gate is trusted. The artifact here is unusual in that the
repository already carries it. `docs/ideas.md` holds all four classes this
tool exists to find, so the last section of this file points the tool at the
live ledger and pins the numbers, and the rest builds small ledgers on disk so
each class is exercised on its own.

One test matters more than the others and it is
`test_the_tool_and_the_grep_disagree_and_the_grep_is_wrong`. It runs the
command the charters actually tell seats to run, runs the parser beside it, and
asserts the two answers differ by exactly the two lines of prose that a grep
cannot tell from a verdict. That is the defect stated as an assertion rather
than as a paragraph, which is the only form of it that stays true.

    python3 -m pytest tests/test_ledger.py -q
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ledger", REPO / "tools" / "ledger.py")
ledger = importlib.util.module_from_spec(spec)
sys.modules["ledger"] = ledger
spec.loader.exec_module(ledger)

LIVE = REPO / "docs" / "ideas.md"


def entry(status_line="- Status: proposed", head="### 2026-10-17 — An idea", body=""):
    return f"{head}\n- Trigger: something observed\n- What: a paragraph\n{body}{status_line}\n"


# ---------------- the shape of an entry ----------------

def test_an_entry_is_read_whole():
    [e] = ledger.parse(entry())
    assert (e.line, e.date, e.name, e.status) == (1, "2026-10-17", "An idea", "proposed")
    assert e.readable and e.problem is None


@pytest.mark.parametrize("dash", ["—", "–", "-"])
def test_both_dashes_and_a_typed_hyphen_open_an_entry(dash):
    [e] = ledger.parse(entry(head=f"### 2026-10-17 {dash} An idea"))
    assert e.name == "An idea"


def test_a_section_heading_closes_the_entry_above_it():
    text = (
        "### 2026-10-17 — First\n- Status: proposed\n\n"
        "## A new section\n\n"
        "### 2026-10-17 — Second\n- Status: urgent\n"
    )
    first, second = ledger.parse(text)
    assert (first.status, second.status) == ("proposed", "urgent")


def test_a_status_line_in_the_next_section_does_not_leak_backwards():
    text = "### 2026-10-17 — Only entry\n- What: no verdict\n\n## Notes\n- Status: urgent\n"
    [e] = ledger.parse(text)
    assert e.problem == "no-status"


def test_a_heading_inside_an_entry_is_body_and_not_a_sibling():
    """The ledger does this once on purpose, so it must not be miscounted."""
    text = entry(body="### a sub-finding inside the entry\nmore prose\n")
    assert len(ledger.parse(text)) == 1
    assert ledger.undated_headings(text) == []


def test_a_status_with_a_note_after_it_is_still_the_keyword():
    """Four live entries are written this way and all four are readable.

    This is the one judgement in the parser that could have gone the other
    way. `- Status: proposed  (filed 2026-09-20 as urgent; carried here)` is a
    `proposed` entry whose author wrote down the history beside the verdict,
    and reading it as unreadable would hide four entries to enforce a
    formatting rule the contract does not state. The keyword has to come
    first, though, which is what separates it from `mostly moot as of run 3`.
    """
    [e] = ledger.parse(entry("- Status: proposed  (filed 2026-09-20 as `urgent`)"))
    assert e.status == "proposed" and e.readable


# ---------------- the four ways an entry hides ----------------

def test_no_status_line_at_all():
    [e] = ledger.parse("### 2026-10-17 — An idea\n- What: a paragraph\n")
    assert e.problem == "no-status" and not e.readable


def test_an_empty_status_line():
    [e] = ledger.parse(entry("- Status:"))
    assert e.problem == "empty-status" and not e.readable


def test_a_status_written_as_a_sentence():
    [e] = ledger.parse(entry("- Status: mostly moot as of run 3"))
    assert e.problem == "unknown-status" and e.status == "mostly"


def test_two_status_lines_in_one_entry_are_ambiguous():
    [e] = ledger.parse(entry(body="- Status: proposed\n", status_line="- Status: built"))
    assert e.problem == "duplicate-status" and not e.readable
    assert e.extra_status_lines


def test_a_heading_with_no_date_is_invisible_to_the_parser_and_reported_separately():
    text = "## Section\n\n### Craft scan — a product\n- Status: proposed\n"
    assert ledger.parse(text) == []
    assert [h for _, h in ledger.undated_headings(text)] == ["Craft scan — a product"]


def test_prose_that_reads_like_a_verdict_is_counted_as_a_decoy():
    [e] = ledger.parse(entry(body="- What: the chair wrote Status: accepted in a note\n"))
    assert e.decoys and e.status == "proposed"


# ---------------- the filter consumers actually use ----------------

def test_by_status_returns_only_entries_a_filter_can_read():
    text = (
        "### 2026-10-17 — Readable\n- Status: accepted\n\n"
        "### 2026-10-17 — Hidden by prose\n- Status: mostly accepted, in spirit\n\n"
        "### 2026-10-17 — Hidden by absence\n- What: nothing\n"
    )
    picked = ledger.by_status(ledger.parse(text), "accepted")
    assert [e.name for e in picked] == ["Readable"]
    assert len(ledger.unreadable(ledger.parse(text))) == 2


def test_by_status_ignores_case_and_surrounding_space():
    [e] = ledger.parse(entry("- Status:   ACCEPTED  "))
    assert ledger.by_status([e], " Accepted ")


def test_the_census_accounts_for_every_entry():
    text = Path(LIVE).read_text()
    data = ledger.census(ledger.parse(text), text)
    assert data["entries"] == data["readable"] + data["unreadable"]
    assert sum(data["by_status"].values()) == data["readable"]


# ---------------- the ratchet ----------------

def test_the_ratchet_blocks_when_the_count_climbs(monkeypatch):
    monkeypatch.setattr(ledger, "BASELINE", 0)
    blocking, warnings = ledger.check(ledger.parse(entry("- Status:")))
    assert any("up from the recorded 0" in f for f in blocking)
    assert warnings


def test_the_ratchet_passes_at_the_recorded_count(monkeypatch):
    monkeypatch.setattr(ledger, "BASELINE", 1)
    blocking, warnings = ledger.check(ledger.parse(entry("- Status:")))
    assert blocking == []
    assert warnings, "it still says what is wrong, it just does not block"


def test_a_new_undated_heading_blocks(monkeypatch):
    monkeypatch.setattr(ledger, "BASELINE_UNDATED", 0)
    text = "## Section\n\n### Craft scan — a product\n- Status: proposed\n"
    blocking, _ = ledger.check(ledger.parse(text), text)
    assert any("carry no date" in f for f in blocking)


def test_a_new_decoy_blocks(monkeypatch):
    monkeypatch.setattr(ledger, "BASELINE_DECOYS", 0)
    text = entry(body="- What: see the note reading Status: accepted above\n")
    blocking, _ = ledger.check(ledger.parse(text), text)
    assert any("without being a status line" in f for f in blocking)


def test_a_clean_ledger_blocks_on_nothing_and_warns_about_nothing():
    text = entry() + "\n" + entry(head="### 2026-10-16 — Another", status_line="- Status: built")
    blocking, warnings = ledger.check(ledger.parse(text), text)
    assert (blocking, warnings) == ([], [])


# ---------------- and the real ledger ----------------

def test_the_live_ledger_is_at_or_under_every_recorded_baseline():
    """The assertion the gate exists to make, against the file every seat appends to."""
    text = LIVE.read_text()
    blocking, _ = ledger.check(ledger.parse(text), text)
    assert blocking == [], "\n".join(blocking)


def test_the_baselines_are_not_stale_upwards():
    """A baseline above the real count is a gate that has stopped gating.

    It may be lowered in the pull request that fixes entries. It must never
    sit above the truth, because the slack is exactly how many bad entries the
    next run may add without the check noticing.
    """
    text = LIVE.read_text()
    entries = ledger.parse(text)
    assert len(ledger.unreadable(entries)) == ledger.BASELINE
    assert len(ledger.undated_headings(text)) == ledger.BASELINE_UNDATED
    assert sum(len(e.decoys) for e in entries) == ledger.BASELINE_DECOYS


def test_the_tool_and_the_grep_disagree_and_the_grep_is_wrong():
    """`grep "Status: accepted" docs/ideas.md` is what the charters tell seats to run.

    It returns more entries than exist, because two lines of prose in this
    file read `Status: accepted` while being a quotation and a remark. The
    parser returns the nine real ones. The gap is the defect.
    """
    text = LIVE.read_text()
    grepped = [n for n, line in enumerate(text.splitlines(), 1)
               if re.search(r"Status:\s*accepted\b", line)]
    parsed = ledger.by_status(ledger.parse(text), "accepted")
    assert len(grepped) > len(parsed)
    decoys = set(n for e in ledger.parse(text) for n in e.decoys)
    assert set(grepped) - {e.status_line for e in parsed} <= decoys


def test_every_live_entry_carrying_a_readable_status_has_the_contract_fields():
    """Not a gate, a measurement: how far the file is from its own contract.

    The bound fell from 206 to 196 on 2026-11-01, and the entries did not
    change. `tools/ledger.py` says the baseline "may fall and it may not rise"
    and that lowering it belongs in the pull request that fixed the entries.
    What this one fixed is the parser: a label like `- What is worth stealing:`
    is the `What` field wearing a qualifier, and the matcher pinned to the bare
    label called 163 such lines absent. Fourteen entries left the set because
    they were never outside the contract, which is why the number may be read
    as a drop in defects rather than as a bound relaxed to fit.
    """
    entries = ledger.parse(LIVE.read_text())
    incomplete = [e for e in entries if e.readable and e.missing_fields]
    assert len(incomplete) <= 196, (
        f"{len(incomplete)} readable entries are missing contract fields, "
        f"up from the 196 measured on 2026-11-01"
    )


# ------------- the field label, qualified and bare -------------
#
# `INC-2026-11-01-the-contract-field-matcher-read-the-label-and-not-the-field`.
# Every case below is synthetic on purpose. The measurement above is the only
# thing here that reads the live file, because a second pinned count beside it
# is a copy that goes stale, which is the defect `tests/test_ci_coverage.py`
# refuses to commit in its own header.


def test_the_bare_label_the_contract_prints_is_read_as_itself():
    assert ledger.field_label("- What: a paragraph") == ("What", "What")
    assert ledger.field_label("- Cost: $0") == ("Cost", "Cost")


@pytest.mark.parametrize("line,field", [
    ("- What alexandria does better: the corpus", "What"),
    ("- What is worth stealing: their stop signal", "What"),
    ("- Cost to HQ: one review", "Cost"),
    ("- First step, if accepted: one function", "First step"),
    ("- Trigger, twice over: two runs", "Trigger"),
])
def test_a_qualified_label_is_still_the_field_it_opens_with(line, field):
    found = ledger.field_label(line)
    assert found is not None and found[0] == field
    assert found[1] != field, "the label is reported as written, not normalised"


@pytest.mark.parametrize("line", [
    "- Costs nothing: so it is not a Cost field",
    "- First steps: plural is a different label",
    "- Whatever happened: not a What field",
    "- Triggered by nothing: not a Trigger field",
])
def test_a_word_that_merely_starts_with_the_field_name_is_not_the_field(line):
    assert ledger.field_label(line) is None


def test_a_label_too_wide_to_be_a_label_is_prose():
    wide = "What " + "x" * ledger.FIELD_QUALIFIER_WIDTH
    assert ledger.field_label(f"- {wide}: still prose") is None
    # The case above scales with the constant, so it stays true if the bound is
    # widened to swallow a paragraph. This is the half that does not: the
    # widest real label measured on the live file is 75 characters, so a bound
    # loose enough to admit a sentence is a bound that is not doing the work.
    assert ledger.FIELD_QUALIFIER_WIDTH <= 120


def test_a_line_that_is_not_a_list_item_is_not_a_field():
    assert ledger.field_label("What: a heading, not a field") is None
    assert ledger.field_label("  - What: indented past the body") is None


def test_an_entry_written_entirely_in_qualified_labels_owes_nothing(tmp_path):
    text = (
        "### 2026-11-01 — Craft scan: somebody else's product\n"
        "- Trigger: today's scan\n"
        "- What is worth stealing: their stop signal\n"
        "- What alexandria does better: the provenance\n"
        "- First step, if accepted: one function\n"
        "- Cost to HQ: $0\n"
        "- Status: proposed\n"
    )
    found, = ledger.parse(text)
    assert found.missing_fields == []
    assert found.qualified_fields == {
        "What": "What is worth stealing",
        "First step": "First step, if accepted",
        "Cost": "Cost to HQ",
    }, "Trigger was bare, so it is not reported as qualified"


def test_the_bare_label_wins_when_an_entry_writes_both():
    text = (
        "### 2026-11-01 — An idea\n"
        "- Trigger: something\n"
        "- What is still open: the half nobody owns\n"
        "- What: the paragraph the contract asks for\n"
        "- First step: one function\n"
        "- Cost: $0\n"
        "- Status: proposed\n"
    )
    found, = ledger.parse(text)
    assert found.missing_fields == []
    assert "What" not in found.qualified_fields


def test_a_genuinely_absent_field_is_still_absent():
    text = (
        "### 2026-11-01 — An idea\n"
        "- Trigger: something\n"
        "- Status: proposed\n"
    )
    found, = ledger.parse(text)
    assert found.missing_fields == ["What", "First step", "Cost"]
    assert found.qualified_fields == {}


def test_the_json_surface_carries_the_qualified_labels():
    text = (
        "### 2026-11-01 — An idea\n"
        "- Trigger: something\n"
        "- What it is: a paragraph\n"
        "- First step: one function\n"
        "- Cost: $0\n"
        "- Status: proposed\n"
    )
    found, = ledger.parse(text)
    assert found.as_dict()["qualified_fields"] == {"What": "What it is"}
