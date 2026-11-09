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

    This bound moved twice on 2026-11-01 and neither move was a relaxation to
    fit, so both are worth carrying.

    It fell from 206 to 196 when the parser was fixed. A label like
    `- What is worth stealing:` is the `What` field wearing a qualifier, and
    the matcher pinned to the bare label called 163 such lines absent, so
    fourteen entries were being reported incomplete that are not.
    `tools/ledger.py` says a baseline "may fall and it may not rise" and that
    lowering it belongs in the pull request that fixed the entries; what this
    one fixed is the parser, which is a stronger claim than fixing fourteen
    entries would have been.

    Then it rose from 196 to 202, ninety minutes later, because six pull
    requests merged into `main` while this branch was open and six of their
    entries are short of the contract. None of the six is this branch's, and
    that is the whole case for the test below: a bound on one number over 785
    entries cannot say whose the defect is, so it is kept as a ratchet on a
    backlog nobody in the room made, and responsibility is assigned by the
    patch check instead.
    """
    entries = ledger.parse(LIVE.read_text())
    incomplete = [e for e in entries if e.readable and e.missing_fields]
    assert len(incomplete) <= ledger.PROJECT_INCOMPLETE, (
        f"{len(incomplete)} readable entries are missing contract fields, "
        f"up from the {ledger.PROJECT_INCOMPLETE} measured on 2026-11-09. "
        f"Re-measure it on origin/main before raising it, and say in the pull "
        f"request whose entries moved it; see tools/ledger.py"
    )


# --------- the patch status, which is the half with no budget ---------
#
# The project measurement above absorbs everybody's history. These answer for
# the entries the branch under test actually wrote, which is Codecov's split
# between a project status and a patch status, and the reason it is here is in
# `docs/ideas.md` of 2026-11-01 under "The ledger measurement has a project
# status and no patch status".


BASE = (
    "### 2026-10-31 — An entry that was already here\n"
    "- Trigger: yesterday\n- What: a paragraph\n"
    "- First step: one function\n- Cost: $0\n- Status: proposed\n"
)


def test_an_entry_the_branch_did_not_touch_is_not_its_patch():
    report = ledger.patch(BASE, BASE)
    assert report["added"] == 0
    assert report["incomplete"] == []
    assert report["no_status"] == []


def test_a_complete_entry_the_branch_adds_owes_nothing():
    head = BASE + (
        "\n### 2026-11-01 — An entry this branch wrote\n"
        "- Trigger: today\n- What is worth saying: a paragraph\n"
        "- First step: one function\n- Cost: $0\n- Status: proposed\n"
    )
    report = ledger.patch(BASE, head)
    assert report["added"] == 1
    assert report["incomplete"] == []
    assert report["no_status"] == []


def test_an_incomplete_entry_the_branch_adds_is_named_with_its_line():
    head = BASE + (
        "\n### 2026-11-01 — An entry this branch wrote badly\n"
        "- Trigger: today\n- Status: proposed\n"
    )
    report = ledger.patch(BASE, head)
    assert report["added"] == 1
    bad, = report["incomplete"]
    assert bad["missing_fields"] == ["What", "First step", "Cost"]
    assert bad["line"] == 8
    assert bad["name"] == "An entry this branch wrote badly"


def test_an_entry_the_branch_adds_with_no_status_is_reported_separately():
    head = BASE + (
        "\n### 2026-11-01 — An entry with no status at all\n"
        "- Trigger: today\n- What: a paragraph\n"
        "- First step: one function\n- Cost: $0\n"
    )
    report = ledger.patch(BASE, head)
    assert report["incomplete"] == [], "all four fields are there"
    bad, = report["no_status"]
    assert bad["problem"] == "no-status"


def test_the_base_s_own_backlog_is_not_charged_to_the_branch():
    """The point of the split, as an assertion.

    A base full of incomplete entries and a branch that adds one good one. The
    project number would be four; the patch number is zero.
    """
    base = "".join(
        f"### 2026-10-{day} — Entry {day}\n- Trigger: a while ago\n"
        f"- Status: proposed\n\n"
        for day in (20, 21, 22, 23)
    )
    head = base + (
        "### 2026-11-01 — The one entry this branch wrote\n"
        "- Trigger: today\n- What: a paragraph\n"
        "- First step: one function\n- Cost: $0\n- Status: proposed\n"
    )
    assert len([e for e in ledger.parse(head)
                if e.readable and e.missing_fields]) == 4
    assert ledger.patch(base, head)["incomplete"] == []


def test_the_cli_exits_nonzero_on_the_branch_s_own_bad_entry(
        tmp_path, capsys, monkeypatch):
    head = tmp_path / "ideas.md"
    head.write_text(BASE + (
        "\n### 2026-11-01 — An entry this branch wrote badly\n"
        "- Trigger: today\n- Status: proposed\n"
    ))
    monkeypatch.setattr(ledger, "ledger_at",
                        lambda ref, path="docs/ideas.md": BASE)
    code = ledger.main(["--ledger", str(head), "--patch", "whatever"])
    out = capsys.readouterr()
    assert code == 1
    assert "no baseline to lower here" in out.err
    assert "missing What, First step, Cost" in out.out


def test_a_ref_this_checkout_does_not_carry_is_a_skip_and_not_a_failure(capsys):
    """The host clones shallow with a single-branch refspec, so `origin/main`
    resolves on some checkouts and not others. A patch check that errors there
    is a patch check nobody can put in a workflow."""
    assert ledger.ledger_at("no-such-ref-exists-here") is None
    code = ledger.main(["--patch", "no-such-ref-exists-here"])
    assert code == 0
    assert "skipped" in capsys.readouterr().err


def test_this_branch_adds_no_entry_short_of_the_contract():
    """The live one, and the only live assertion in this section.

    Skips rather than fails when `origin/main` is not in the checkout, because
    that is a property of how the clone was made and not of the ledger.
    """
    base_text = ledger.ledger_at("origin/main")
    if base_text is None:
        pytest.skip("origin/main:docs/ideas.md is not in this checkout")
    report = ledger.patch(base_text, LIVE.read_text())
    assert report["incomplete"] == [], (
        f"{len(report['incomplete'])} of this branch's own entries are short "
        f"of the contract: "
        f"{[(b['line'], b['missing_fields']) for b in report['incomplete']]}"
    )
    assert report["no_status"] == [], (
        f"{len(report['no_status'])} of this branch's own entries carry no "
        f"readable status: {[b['line'] for b in report['no_status']]}"
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


# ---------------- the inbox, 2026-11-09 ----------------
#
# L-A18's remedy applied to this register: one file per entry, folded on the
# mainline where there is one author. Every test below is the gate pointed at an
# artifact known to fail it, which is incident 32's rule and the reason this
# section is long. The two that carry the most weight are
# `test_the_skeleton_this_tool_writes_does_not_pass_its_own_gate`, because every
# other predicate passes on a file with no content in it, and
# `test_a_fold_does_not_file_an_entry_under_another_seats_run_section`, because
# that is the one difference from `tools/incidents.py` that a reader would not
# predict.

INBOX_ENTRY = """### 2026-11-09 - a thing worth building (engineer seat)

- Trigger: measured on the live file this morning
- What: one paragraph, and it is this one
- First step: the first day-sized unit
- Cost: $0
- Status: proposed
"""


def inbox_pair(name="2026-11-09-a-thing.md", text=INBOX_ENTRY):
    return [(name, text)]


def test_an_empty_inbox_has_nothing_to_say():
    assert ledger.check_inbox([], "") == []


def test_a_well_formed_inbox_entry_passes():
    assert ledger.check_inbox(inbox_pair(), "") == []


def test_a_filename_that_is_not_a_date_and_a_slug_claims_nothing():
    [problem] = ledger.check_inbox(inbox_pair(name="my-idea.md"))
    assert "YYYY-MM-DD-slug.md" in problem


@pytest.mark.parametrize("name", [
    "2026-11-09-Capitalised.md",
    "2026-11-09-trailing-.md",
    "2026-11-09.md",
    "2026-13-09-a-thing.md",
])
def test_a_filename_outside_the_slugs_own_alphabet_is_refused(name):
    assert ledger.check_inbox(inbox_pair(name=name))


def test_a_conflict_marker_in_an_inbox_entry_is_refused():
    """Step zero of every charter's ship check, on the surface this adds.

    A committed marker conflicts once and is ordinary text forever after, so the
    merge that made it is the only thing that will ever warn anybody.
    """
    bad = INBOX_ENTRY.replace("- Cost: $0", "<<<<<<< HEAD\n- Cost: $0")
    [problem] = ledger.check_inbox(inbox_pair(text=bad))
    assert "conflict marker" in problem


def test_two_entries_in_one_inbox_file_are_refused():
    """Per-entry granularity is the whole remedy, so two in one file undo it."""
    [problem] = ledger.check_inbox(inbox_pair(text=INBOX_ENTRY + "\n" + INBOX_ENTRY))
    assert "exactly one entry" in problem


def test_a_heading_quoted_inside_a_fence_is_not_a_second_entry():
    """The register already holds an entry whose body quotes the contract block."""
    quoted = INBOX_ENTRY + "\n```\n### 2026-01-01 - the contract's own example\n```\n"
    assert ledger.check_inbox(inbox_pair(text=quoted)) == []


def test_an_inbox_file_with_no_entry_heading_is_refused():
    [problem] = ledger.check_inbox(inbox_pair(text="Some prose and no heading.\n"))
    assert "0 `### ` headings" in problem


def test_a_heading_that_does_not_parse_names_the_blindness_it_causes():
    unparsed = INBOX_ENTRY.replace("### 2026-11-09 - a thing worth building",
                                   "### A thing worth building")
    [problem] = ledger.check_inbox(inbox_pair(text=unparsed))
    assert "does not parse" in problem and "blind" in problem


def test_a_heading_and_a_filename_that_disagree_about_the_date_are_refused():
    """A reader sorting the inbox and one sorting the register would disagree."""
    [problem] = ledger.check_inbox(inbox_pair(name="2026-11-08-a-thing.md"))
    assert "dated 2026-11-09 and the filename 2026-11-08" in problem


def test_an_arriving_entry_short_of_the_contract_has_no_baseline():
    """The one thing this surface has that `--check`'s ratchet cannot.

    Sixty-two live entries carry an unreadable status and no seat may rewrite
    another seat's triage, so the register's own gate has to ratchet. An inbox
    holds nothing older than the day it was built.
    """
    thin = "### 2026-11-09 - a thing worth building\n\n- Status: proposed\n"
    [problem] = ledger.check_inbox(inbox_pair(text=thin))
    assert "missing Trigger, What, First step, Cost" in problem
    assert "no baseline" in problem


def test_an_arriving_entry_with_no_readable_status_is_refused():
    blind = INBOX_ENTRY.replace("- Status: proposed", "- Status: mostly moot by now")
    [problem] = ledger.check_inbox(inbox_pair(text=blind))
    assert "unknown-status" in problem and "silently absent" in problem


@pytest.mark.parametrize("status", ["accepted", "rejected", "built"])
def test_a_status_that_is_a_transition_cannot_be_an_arrival(status):
    """`accepted` and `rejected` are the owner's and `built` is a move.

    None of the three can be the status of an entry written for the first time,
    and no other surface in this repository can say so, because no other surface
    knows which entries are new.
    """
    moved = INBOX_ENTRY.replace("- Status: proposed", f"- Status: {status}")
    [problem] = ledger.check_inbox(inbox_pair(text=moved))
    assert f"status {status!r}" in problem
    assert "already exists" in problem


def test_urgent_is_fileable_because_a_charter_tells_a_seat_to_file_it():
    urgent = INBOX_ENTRY.replace("- Status: proposed", "- Status: urgent")
    assert ledger.check_inbox(inbox_pair(text=urgent)) == []


def test_two_inbox_files_claiming_one_entry_are_refused():
    pair = inbox_pair() + inbox_pair(name="2026-11-09-a-thing-again.md")
    [problem] = ledger.check_inbox(pair)
    assert "two entries in this register under one identifier" in problem


def test_an_entry_already_in_the_register_would_be_a_second_answer_to_one_id():
    [problem] = ledger.check_inbox(inbox_pair(), register_text=INBOX_ENTRY)
    assert "already in docs/ideas.md" in problem and "L-A18" in problem


# --- the stub, which every other predicate above passes ----------------------

def test_the_skeleton_this_tool_writes_does_not_pass_its_own_gate(tmp_path):
    """The test that matters most here.

    `--inbox-new` emits four contract fields, a readable status and a parsing
    heading, so every other check in this section says yes to a file with not
    one word of content in it. A stub and a finished entry look identical from
    the outside.
    """
    path = ledger.new_entry("a-thing", "2026-11-09", "engineer", "A thing",
                            inbox=tmp_path)
    problems = ledger.check_inbox([(path.name, path.read_text())])
    assert len(problems) == 1
    assert "placeholder" in problems[0]
    assert ledger.check_inbox([(path.name, INBOX_ENTRY)]) == []


@pytest.mark.parametrize("line, caught", [
    ("- What: <one paragraph, concrete>", True),
    ("- What: `- Routes: <entry name or none>` once per routed finding", False),
    ("- What: the gate reads <div> and stops", False),
    ("- What: superseded by <PR#>", False),
    ("- What: quotes `git log origin/<the-older-branch> ^HEAD` across", False),
])
def test_a_placeholder_inside_a_code_span_is_syntax_and_not_a_stub(line, caught):
    assert bool(ledger.PLACEHOLDER.search(ledger._uncoded(line))) is caught


def test_the_placeholder_pattern_is_clean_on_every_live_entry():
    """Pinned, so the next widening of that pattern moves a number.

    The first draft of it matched two lines on the live register, both of them a
    template being quoted rather than a field left unfilled, which is how the
    code-span half was found.
    """
    text = LIVE.read_text(encoding="utf-8")
    hits = [n for n, line in enumerate(text.splitlines(), start=1)
            if ledger.PLACEHOLDER.search(ledger._uncoded(line))]
    assert hits == [], f"{len(hits)} false positives on {len(ledger.parse(text))} entries"


# --- the fold ----------------------------------------------------------------

OTHER_SEATS_RUN = """# The ledger

## 2026-11-08 - what another seat's run turned up (skill seat)

### 2026-11-08 - their idea

- Trigger: theirs
- What: theirs
- First step: theirs
- Cost: $0
- Status: proposed
"""


def test_a_fold_keeps_the_register_as_a_prefix_and_proves_its_arithmetic():
    folded = ledger.fold_text(OTHER_SEATS_RUN, inbox_pair(), "2026-11-09")
    assert folded.startswith(OTHER_SEATS_RUN.rstrip("\n"))
    assert ledger.fold_invariant(OTHER_SEATS_RUN, inbox_pair(), folded, "2026-11-09") == []


def test_a_fold_does_not_file_an_entry_under_another_seats_run_section():
    """The one difference from `tools/incidents.py` a reader would not predict.

    That register's entries are level-two headings, so its fold can append at
    the tail and stop. Here an entry is a `### ` inside a `## ` run section, and
    the last section on the live file belongs to another seat. A register that
    misattributes an entry to a seat that did not write it is worse than one
    that is hard to merge.
    """
    folded = ledger.fold_text(OTHER_SEATS_RUN, inbox_pair(), "2026-11-09")
    heading = ledger.fold_section_heading("2026-11-09")
    assert heading in folded
    assert folded.index(heading) > folded.index("(skill seat)")
    assert folded.index(heading) < folded.index("a thing worth building")


def test_a_fold_that_loses_the_heading_is_refused():
    """The invariant's own fourth claim, pointed at a fold that skips it."""
    bare = OTHER_SEATS_RUN.rstrip("\n") + "\n\n" + INBOX_ENTRY
    failures = ledger.fold_invariant(OTHER_SEATS_RUN, inbox_pair(), bare, "2026-11-09")
    assert any("fold heading is absent" in f for f in failures)


def test_a_fold_that_drops_a_line_is_caught_by_the_arithmetic():
    folded = ledger.fold_text(OTHER_SEATS_RUN, inbox_pair(), "2026-11-09")
    lost = folded.replace("- Cost: $0\n", "")
    failures = ledger.fold_invariant(OTHER_SEATS_RUN, inbox_pair(), lost, "2026-11-09")
    assert any("line arithmetic" in f for f in failures)


def test_a_fold_orders_by_the_entrys_own_date_not_by_directory_order():
    older = INBOX_ENTRY.replace("2026-11-09", "2026-11-01").replace(
        "a thing worth building", "the older thing")
    inbox = [("2026-11-09-a-thing.md", INBOX_ENTRY),
             ("2026-11-01-older.md", older)]
    folded = ledger.fold_text(OTHER_SEATS_RUN, inbox, "2026-11-09")
    assert folded.index("the older thing") < folded.index("a thing worth building")
    assert ledger.fold_invariant(OTHER_SEATS_RUN, inbox, folded, "2026-11-09") == []


def test_a_folded_entry_is_then_visible_to_the_consumers_that_grep_for_it():
    """The fold is only worth anything if the register reads the entry after it."""
    folded = ledger.fold_text(OTHER_SEATS_RUN, inbox_pair(), "2026-11-09")
    names = [e.name for e in ledger.by_status(ledger.parse(folded), "proposed")]
    assert "a thing worth building (engineer seat)" in names


def test_a_fold_refuses_to_move_an_entry_the_register_would_hold_badly(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "2026-11-09-a-thing.md").write_text(
        INBOX_ENTRY.replace("- Status: proposed", "- Status: accepted"))
    register = tmp_path / "ideas.md"
    register.write_text(OTHER_SEATS_RUN)
    code = ledger.main(["--ledger", str(register), "--inbox-dir", str(inbox),
                        "--fold", "--apply"])
    assert code == 1
    assert register.read_text() == OTHER_SEATS_RUN
    assert (inbox / "2026-11-09-a-thing.md").exists()


def test_fold_apply_moves_the_file_and_leaves_the_inbox_empty(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "2026-11-09-a-thing.md").write_text(INBOX_ENTRY)
    register = tmp_path / "ideas.md"
    register.write_text(OTHER_SEATS_RUN)

    assert ledger.main(["--ledger", str(register), "--inbox-dir", str(inbox),
                        "--fold", "--date", "2026-11-09"]) == 0
    assert (inbox / "2026-11-09-a-thing.md").exists(), "a dry run moved something"

    assert ledger.main(["--ledger", str(register), "--inbox-dir", str(inbox),
                        "--fold", "--apply", "--date", "2026-11-09"]) == 0
    assert not (inbox / "2026-11-09-a-thing.md").exists()
    assert "a thing worth building" in register.read_text()
    assert ledger.check_inbox([], register.read_text()) == []


def test_require_folded_is_off_by_default_and_loud_when_asked(tmp_path):
    """A gate that can turn `main` red for a bookkeeping step nobody promised
    to run is a worse defect than the one being fixed.

    `tools/incidents.py`'s own argument, and it holds here for the same reason:
    the ledger's identifiers come from the date and the name, so a fold is pure
    movement and a missed fold costs nothing but tidiness.
    """
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "2026-11-09-a-thing.md").write_text(INBOX_ENTRY)
    register = tmp_path / "ideas.md"
    register.write_text(OTHER_SEATS_RUN)
    base = ["--ledger", str(register), "--inbox-dir", str(inbox), "--check"]
    assert ledger.main(base) == 0
    assert ledger.main(base + ["--require-folded"]) == 1


# --- the skeleton writer -----------------------------------------------------

def test_new_entry_refuses_a_slug_that_would_not_parse_as_a_filename(tmp_path):
    with pytest.raises(ValueError):
        ledger.new_entry("Not A Slug", "2026-11-09", "engineer", "x", inbox=tmp_path)


def test_new_entry_refuses_to_overwrite_an_entry_already_filed(tmp_path):
    ledger.new_entry("a-thing", "2026-11-09", "engineer", "x", inbox=tmp_path)
    with pytest.raises(FileExistsError):
        ledger.new_entry("a-thing", "2026-11-09", "engineer", "x", inbox=tmp_path)


def test_the_skeleton_carries_no_em_dash():
    """`tools/ban_list.py` entry 13 rejects U+2014 and `ENTRY` takes a hyphen."""
    assert "—" not in ledger.SKELETON


# --- the inbox on this checkout ----------------------------------------------

def test_the_inbox_directory_and_its_readme_exist():
    """A convention with no landing place is a convention nobody follows."""
    assert ledger.INBOX.is_dir()
    readme = (ledger.INBOX / "README.md").read_text(encoding="utf-8")
    assert "tools/ledger.py" in readme
    assert "L-A18" in readme


def test_every_entry_waiting_in_the_live_inbox_would_fold_cleanly():
    """Whatever is in the inbox right now must be foldable by the next merger."""
    text = LIVE.read_text(encoding="utf-8")
    inbox = ledger.read_inbox()
    assert ledger.check_inbox(inbox, text) == []
    folded = ledger.fold_text(text, inbox, "2026-11-09")
    assert ledger.fold_invariant(text, inbox, folded, "2026-11-09") == []


def test_the_readme_is_documentation_and_not_a_filing():
    """It sits in the directory and would fail every predicate as an entry."""
    assert (ledger.INBOX / "README.md").is_file()
    assert all(name != "README.md" for name, _ in ledger.read_inbox())


def test_a_badly_named_file_is_still_listed_so_its_gate_can_reach_it(tmp_path):
    """A listing that skipped these would make the filename predicate dead."""
    (tmp_path / "my-idea.md").write_text(INBOX_ENTRY)
    (tmp_path / "README.md").write_text("docs")
    assert [p.name for p in ledger.inbox_files(tmp_path)] == ["my-idea.md"]


# --- `--seat` is a roster flag, and the probe is what made it one -------------

def test_a_seat_nothing_carries_refuses_by_name():
    """Declared `roster` in `tools/target_census.py`, so it owes a refusal."""
    assert ledger.seat_names(), "company.yaml carried no seats, so nothing refuses"
    assert ledger.main(["--seat", "nonesuch", "--census"]) == 4


def test_the_refusal_is_reachable_without_the_flag_that_consumes_the_value():
    """The defect `tools/target_census.py --probe` found in the first draft.

    `--seat` is used by `--inbox-new` alone, so the check started life inside
    that branch. The probe runs the flag on its own, got exit 0, and the roster
    declaration was dishonest until the check moved to parse time. A check
    reachable only through the flag that consumes it is a check the probe cannot
    see.
    """
    assert ledger.main(["--seat", "nonesuch"]) == 4


def test_every_seat_the_manifest_declares_is_accepted():
    for seat in ledger.seat_names():
        assert ledger.main(["--seat", seat, "--inbox", "--inbox-dir", "/nonexistent"]) == 0


def test_an_unreadable_manifest_refuses_nothing_rather_than_everything(monkeypatch):
    """A source of roster names, never a source of absences."""
    monkeypatch.setattr(ledger, "seat_names", lambda: ())
    assert ledger.main(["--seat", "nonesuch", "--inbox", "--inbox-dir", "/nonexistent"]) == 0


# --- the branch's own appends, which no predicate above could see ------------
#
# `tools/incidents.py` carries this predicate for a reason worth restating:
# every other check in this file inspects an entry already in the inbox or
# already in the register, so a seat that ignores the inbox entirely produces a
# clean read. The question none of them asks is what the branch did.
#
# These build a real repository, because the predicate's subject is a diff
# against a merge base and a fixture cannot have one.

def _git(repo, *args):
    import subprocess
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


@pytest.fixture
def branch_repo(tmp_path):
    """A repository with a register, an inbox and a `base` branch to diff."""
    (tmp_path / "docs" / "ideas" / "inbox").mkdir(parents=True)
    (tmp_path / "docs" / "ideas.md").write_text(OTHER_SEATS_RUN)
    _git(tmp_path, "init", "-q", "-b", "base")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "the register as it stands")
    _git(tmp_path, "checkout", "-q", "-b", "work")
    return tmp_path


def test_a_branch_that_appends_to_the_register_with_no_inbox_file_is_caught(branch_repo):
    (branch_repo / "docs" / "ideas.md").write_text(OTHER_SEATS_RUN + "\n" + INBOX_ENTRY)
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "straight in")
    unclaimed, skipped = ledger.branch_appends("base", [], root=branch_repo)
    assert skipped == ""
    assert unclaimed == ["2026-11-09 - a thing worth building (engineer seat)"]


def test_a_branch_that_files_into_the_inbox_passes(branch_repo):
    (branch_repo / "docs" / "ideas" / "inbox" / "2026-11-09-a-thing.md").write_text(
        INBOX_ENTRY)
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "through the inbox")
    inbox = ledger.read_inbox(branch_repo / "docs" / "ideas" / "inbox")
    assert ledger.branch_appends("base", inbox, root=branch_repo) == ([], "")


def test_the_claim_is_the_heading_and_not_the_filename(branch_repo):
    """A filename join would claim any entry that merely shares a date.

    The slug in a filename is the author's shorthand; the heading is the
    identifier. `tools/incidents.py` can join on the filename because there the
    filename *is* the id, and here it is not.
    """
    (branch_repo / "docs" / "ideas.md").write_text(
        OTHER_SEATS_RUN + "\n" + INBOX_ENTRY.replace(
            "a thing worth building", "a different thing entirely"))
    (branch_repo / "docs" / "ideas" / "inbox" / "2026-11-09-a-thing.md").write_text(
        INBOX_ENTRY)
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "same date, different entry")
    inbox = ledger.read_inbox(branch_repo / "docs" / "ideas" / "inbox")
    unclaimed, _ = ledger.branch_appends("base", inbox, root=branch_repo)
    assert unclaimed == ["2026-11-09 - a different thing entirely (engineer seat)"]


def test_the_fold_is_exempt_because_it_is_a_move_and_not_an_append(branch_repo):
    """The exemption keys on the file the diff deletes, not the branch it runs on.

    A folded entry's identity has to be read from the merge base, because the
    fold has deleted the only file that carried it.
    """
    inbox_dir = branch_repo / "docs" / "ideas" / "inbox"
    (inbox_dir / "2026-11-09-a-thing.md").write_text(INBOX_ENTRY)
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "filed")
    _git(branch_repo, "checkout", "-q", "base")
    _git(branch_repo, "merge", "-q", "--no-edit", "work")
    _git(branch_repo, "checkout", "-q", "-b", "merger")

    register = branch_repo / "docs" / "ideas.md"
    inbox = ledger.read_inbox(inbox_dir)
    register.write_text(ledger.fold_text(register.read_text(), inbox, "2026-11-09"))
    (inbox_dir / "2026-11-09-a-thing.md").unlink()
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "folded")

    unclaimed, skipped = ledger.branch_appends("base", [], root=branch_repo)
    assert skipped == ""
    assert unclaimed == [], "a fold read as an append"


def test_a_checkout_with_no_merge_base_is_a_skip_and_not_a_pass(tmp_path):
    """A predicate that saw nothing must not read as a quiet pass (L-A21)."""
    (tmp_path / "docs" / "ideas").mkdir(parents=True)
    (tmp_path / "docs" / "ideas.md").write_text(OTHER_SEATS_RUN)
    _git(tmp_path, "init", "-q", "-b", "work")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "only one branch")
    unclaimed, skipped = ledger.branch_appends("nosuchref", [], root=tmp_path)
    assert unclaimed == []
    assert "skipped" in skipped and "merge base" in skipped


def test_the_cli_reaches_the_predicate_with_the_inbox_it_read(branch_repo):
    """The regression this file did not have, and it cost a traceback.

    `branch_appends` took filenames in its first draft and identities in its
    second, and the call site in `main` kept passing filenames. Every unit test
    above called the function directly, so the only broken path was the one a
    seat actually runs, and it raised `ValueError` under a bare exit 1.
    """
    (branch_repo / "docs" / "ideas.md").write_text(OTHER_SEATS_RUN + "\n" + INBOX_ENTRY)
    _git(branch_repo, "add", "-A")
    _git(branch_repo, "commit", "-qm", "straight in")
    code = ledger.main([
        "--ledger", str(branch_repo / "docs" / "ideas.md"),
        "--inbox-dir", str(branch_repo / "docs" / "ideas" / "inbox"),
        "--check", "--base", "base",
    ])
    assert code == 1
