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

def test_a_status_outside_the_contract_warns_and_does_not_block(registers):
    """The entry belongs to another seat, so this reports and does not block."""
    write(registers, "docs/ideas.md", "### An idea\n- Status: mostly moot as of run 3\n")
    blocking, warnings = checker.check(registers)
    assert blocking == []
    assert len(warnings) == 1
    assert "'mostly'" in warnings[0]


@pytest.mark.parametrize("status", sorted(checker.VALID_STATUSES))
def test_every_status_the_contract_names_is_accepted(registers, status):
    write(registers, "docs/ideas.md", f"### An idea\n- Status: {status}\n")
    _, warnings = checker.check(registers)
    assert warnings == []


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
