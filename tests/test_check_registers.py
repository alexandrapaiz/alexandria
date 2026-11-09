"""The register checker, tested against registers known to be damaged.

Incident 32's rule, verbatim: every gate is tested against an artifact known to
fail it before the gate is trusted. PR #60's checker was tested only against the
defects it was written to find, never against a real file carrying them, and the
first real issue it met was one it passed. So these build damaged registers on
disk and assert the checker finds the damage, and then point it at the real
repository and assert it finds none of the blocking class there.

    python3 -m pytest tests/test_check_registers.py -q
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_registers", REPO / "tools" / "check_registers.py")
checker = importlib.util.module_from_spec(spec)
sys.modules["check_registers"] = checker
spec.loader.exec_module(checker)


@pytest.fixture
def registers(tmp_path):
    """A repository shaped like this one, with every register present and clean."""
    for name in checker.REGISTERS:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# a register\n\nNothing wrong here.\n")
    return tmp_path


def write(root, name, body):
    (root / name).write_text(body)


# ---------------- the damage this was written for ----------------

def test_it_finds_the_marker_that_was_actually_on_main(registers):
    """The real case: outer markers cleaned up, the middle one left behind."""
    write(registers, "docs/agents/incidents.md",
          "### The rule that would have caught it\n\nEvery gate is tested.\n"
          "=======\n"
          "*Renumbering note.*\n")
    blocking, _ = checker.check(registers)
    assert len(blocking) == 1
    assert "incidents.md:4" in blocking[0]
    assert "merge conflict marker" in blocking[0]


@pytest.mark.parametrize("marker", ["<<<<<<< HEAD", "=======", ">>>>>>> theirs"])
def test_it_finds_every_marker_git_writes(registers, marker):
    write(registers, "docs/ideas.md", f"# ledger\n\n{marker}\n")
    blocking, _ = checker.check(registers)
    assert any("conflict marker" in f for f in blocking), marker


def test_a_setext_heading_is_not_merge_damage(registers):
    """`===` under a heading is ordinary markdown, and a checker that cried
    wolf on it would be turned off within a week."""
    write(registers, "docs/ideas.md", "The ledger\n==========\n\nAn entry.\n")
    write(registers, "docs/decisions.md", "ADR\n===\n\nA decision.\n")
    blocking, _ = checker.check(registers)
    assert blocking == []


def test_a_divider_inside_a_heading_line_is_not_merge_damage(registers):
    """The schema and the incident register both use `====` inside headings."""
    write(registers, "docs/agents/incidents.md",
          "## Incident 30 ============ the newest claims are invisible\n")
    blocking, _ = checker.check(registers)
    assert blocking == []


# ---------------- the id collision the date scheme was meant to end ----------------

def test_it_finds_two_entries_claiming_one_incident_id(registers):
    write(registers, "docs/agents/incidents.md",
          "## INC-2026-09-24-press-provider-migration one\n\nbody\n\n"
          "## INC-2026-09-24-press-provider-migration two\n\nbody\n")
    blocking, _ = checker.check(registers)
    assert len(blocking) == 1
    assert "already used at line 1" in blocking[0]


def test_distinct_incident_ids_pass(registers):
    write(registers, "docs/agents/incidents.md",
          "## INC-2026-09-24-one thing\n\nbody\n\n## INC-2026-09-24-two thing\n\nbody\n")
    blocking, _ = checker.check(registers)
    assert blocking == []


# ---------------- the ledger contract, which only warns ----------------

#: The contract's own shape, `### YYYY-MM-DD — name`. These fixtures used to
#: read `### An idea`, which no entry in the ledger has ever looked like, and
#: that is why the checker's blind spot survived them: a heading with no date
#: is not an entry to anything that reads the file, so a fixture written that
#: way cannot exercise the entry walk at all.
HEAD = "### 2026-10-17 — An idea"


def test_a_status_outside_the_contract_warns_and_does_not_block(registers):
    """The entry belongs to another seat, so this reports and does not block."""
    write(registers, "docs/ideas.md", f"{HEAD}\n- Status: mostly moot as of run 3\n")
    blocking, warnings = checker.check(registers)
    assert blocking == []
    assert len(warnings) == 1
    assert "unknown-status" in warnings[0]
    assert "mostly moot as of run 3" in warnings[0]


@pytest.mark.parametrize("status", sorted(checker.VALID_STATUSES))
def test_every_status_the_contract_names_is_accepted(registers, status):
    write(registers, "docs/ideas.md", f"{HEAD}\n- Status: {status}\n")
    _, warnings = checker.check(registers)
    assert warnings == []


def test_an_entry_with_no_status_line_at_all_is_reported(registers):
    """The class the old status walk could not see, and 51 entries are in it."""
    write(registers, "docs/ideas.md", f"{HEAD}\n- What: a paragraph and no verdict\n")
    blocking, warnings = checker.check(registers)
    assert blocking == []
    assert len(warnings) == 1
    assert "no-status" in warnings[0]
    assert "invisible to every status filter" in warnings[0]


def test_an_empty_status_is_reported(registers):
    """`- Status:` with nothing after it matched no word, so it matched nothing."""
    write(registers, "docs/ideas.md", f"{HEAD}\n- Status:\n")
    _, warnings = checker.check(registers)
    assert len(warnings) == 1
    assert "empty-status" in warnings[0]


def test_a_heading_with_no_date_is_reported(registers):
    """Not an entry to the parser, so not an entry to any consumer either.

    Two warnings rather than one, and the second is the interesting one: a
    status line under a heading the parser cannot read belongs to no entry, so
    it is a line that answers a grep for a verdict while being attached to
    nothing. That is the over-count and the under-count in one entry.
    """
    write(registers, "docs/ideas.md", "### An idea\n- Status: proposed\n")
    blocking, warnings = checker.check(registers)
    assert blocking == []
    assert len(warnings) == 2
    assert "heading with no date" in warnings[0]
    assert "makes a grep over-count" in warnings[1]


def test_prose_that_reads_like_a_status_is_reported(registers):
    """The over-count half: this is what put two inventions in a grep's answer."""
    write(registers, "docs/ideas.md",
          f"{HEAD}\n- What: the owner wrote Status: accepted in a comment\n"
          "- Status: proposed\n")
    _, warnings = checker.check(registers)
    assert len(warnings) == 1
    assert "makes a grep over-count" in warnings[0]


# ---------------- a register that went missing ----------------

def test_a_register_that_disappeared_blocks(registers):
    (registers / "docs/voice/ban-list.md").unlink()
    blocking, _ = checker.check(registers)
    assert any("does not exist" in f for f in blocking)


# ---------------- and the real repository ----------------

def test_this_repository_has_no_merge_damage_in_its_registers():
    """The assertion the checker exists to make, against the live files."""
    blocking, _ = checker.check(REPO)
    assert blocking == [], "\n".join(blocking)


def test_every_register_this_tool_guards_is_a_real_file():
    missing = [n for n in checker.REGISTERS if not (REPO / n).exists()]
    assert missing == [], f"check_registers.py names files that are gone: {missing}"


# ---------------- the file that conflicted before it was guarded ----------------

def test_the_reading_queue_is_guarded():
    """`docs/research/reading-queue.md` is append-only and three seats write it.

    It conflicted for real on 2026-11-02 and was resolved by hand, wrongly on
    the first attempt, because `tools/resolve_register_conflict.py` reads
    `REGISTERS` to decide what it can be pointed at and this file was not in
    it. The resolver's own arithmetic, run afterwards against the same three
    trees, returned 2,723 findings for that first attempt and none for the
    resolution that shipped. So the instrument existed and the list was what
    kept it away from the one file that needed it. Filed as
    `INC-2026-11-02-the-register-resolver-could-not-see-the-register-that-conflicted`.
    """
    assert "docs/research/reading-queue.md" in checker.REGISTERS


def test_the_checker_and_the_register_map_name_the_same_files():
    """The checker's list and docs/agents/registers.md must not drift on a path.

    Ratcheted rather than absolute, which is the pattern `ledger_ratchet` in
    the tool itself already uses: this blocks a NEW disagreement and records
    the one that exists, so no seat is blocked on a backlog it did not make.

    There are no known exceptions left, and the one there was is why this test
    is shaped as a ratchet. `docs/backlog.md` was guarded here and had NO row
    in the map at all, found by this test on 2026-11-02. It is `company.yaml`'s
    declared `pending` surface, so the gap was in the map rather than in the
    list, and writing that row was the ExO seat's call since the map is its
    file. **The ExO seat wrote it on 2026-11-09, in the `red-gate` wake's §3d
    sweep, and the second assertion below is what told it to** -- this test
    refused to go on tolerating a gap that had been closed, which is the whole
    reason a ratchet records its exceptions by name instead of skipping them.

    The first draft of this test also excused `docs/standards/lessons.md` as
    vendored prose. The second assertion below refused that, because the map
    does name it, which is the whole point of asserting a gap still exists
    rather than only that it is tolerated.

    The direction this does enforce is the one that bit on 2026-11-02:
    `docs/research/reading-queue.md` sat in the map with a writer and a reader
    that are different seats and was absent from the checker, so the resolver
    that reads this list could not be pointed at it.
    """
    known_gaps: set[str] = set()   # closed 2026-11-09 by the ExO §3d sweep
    table = (REPO / "docs/agents/registers.md").read_text()
    missing = {n for n in checker.REGISTERS if f"`{n}`" not in table}
    assert missing <= known_gaps, (
        "a guarded register is not named in docs/agents/registers.md: "
        f"{sorted(missing - known_gaps)}")
    assert known_gaps - missing == set(), (
        "a known gap has been closed, so remove it from `known_gaps` and let "
        f"this test hold the line: {sorted(known_gaps - missing)}")


# ---------------- the queue data gate, which no workflow could reach ----------------

QUEUE = "docs/research/reading-queue.md"

GOOD_LINE = (
    "- [ ] arxiv:2606.08433 \u2014 why it is worth a read "
    "\u2014 asked by the research seat's L-R1 check \u2014 2026-11-02\n")

#: The same line in the plain ASCII `docs/voice/ban-list.md` entry 13 requires.
#: This is what the research seat's sweep writes, and it is NOT a defect: the
#: parser was widened on 2026-11-02 to accept it, because repairing the data
#: loses against a law that keeps being correct.
ASCII_LINE = (
    "- [ ] arxiv:2606.08433 - why it is worth a read "
    "- asked by the research seat's L-R1 check - 2026-11-02\n")

#: The real defect, which survives the widening: no separator at all before the
#: date, so the field runs to the end of the line. Three lines reached `main`
#: on 2026-11-02 in this shape.
BAD_LINE = (
    "- [ ] arxiv:2606.08433 - why it is worth a read "
    "- asked by the research seat's L-R1 check 2026-11-02\n")


def test_it_finds_the_asker_that_swallowed_its_date(registers):
    write(registers, QUEUE, "# Reading queue\n\n" + BAD_LINE)
    findings = checker.unparseable_queue_askers(registers / QUEUE, registers)
    assert len(findings) == 1, findings
    assert "runs past its separator" in findings[0]
    assert "2026-11-02" in findings[0]


def test_it_passes_the_em_dash_the_format_documents(registers):
    write(registers, QUEUE, "# Reading queue\n\n" + GOOD_LINE)
    assert checker.unparseable_queue_askers(registers / QUEUE, registers) == []


def test_it_passes_the_ascii_the_ban_list_requires(registers):
    """The regression that cost a red `main`, asserted from the other side.

    A gate that only accepted the em dash would report every line the voice
    law mandates as damage, which is the same defect one level up.
    """
    write(registers, QUEUE, "# Reading queue\n\n" + ASCII_LINE)
    assert checker.unparseable_queue_askers(registers / QUEUE, registers) == []


def test_the_queue_check_is_blocking_not_a_warning(registers):
    """A wrong attribution is damage, and the instances were real."""
    write(registers, QUEUE, "# Reading queue\n\n" + BAD_LINE)
    blocking, warnings = checker.check(registers)
    assert any("runs past its separator" in b for b in blocking), blocking
