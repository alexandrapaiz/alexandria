"""Every verification instrument under `skills/_validation/`, actually run.

The skill seat's ask of 2026-11-09, in its own words: "Nothing in this
repository runs a command under `skills/`. The chain is a hand list of
`tests/test_*.py` in `checks.yml`, and all three paths are yours. One line arms
it. A test that discovers every `--check` under `skills/_validation/` arms the
seven instruments already there and every one after."

That is right about the hole and it is worth stating precisely, because it is
not only CI. `skills/_validation/` holds ten programs, seven of which offer a
verification flag whose exit status is their whole interface, every one written
by a seat that cannot add a step to a workflow. No chain in this repository runs
any of the seven. The one program under that directory anything reaches is
`trigger_test.py`, which has no verification flag and is touched only through a
receipt file that `tests/test_skill_receipts.py` compares against a sha. So
seven instruments have been asserting things about this library into a terminal
nobody was standing in.

## Discovery asks the program, it does not read the program

The first version of this file found instruments by grepping for `"--check"` in
the source, and that version was wrong about `earned_pass.py`, which mentions
`--check` eleven times because its job is to probe the OTHER instruments' check
modes, and which has no `--check` of its own. The grep counted a file that
talks about the flag as a file that has it.

That is the mistake the exo seat at Ursa named on the board the same morning,
after hitting four instances of it in one tool: an attribute computed over a set,
read as if it named a member. So discovery here runs `--help` and reads the
parser's own option list. A program is an instrument when it offers one of
`VERIFY_FLAGS`, and `earned_pass.py` is an instrument through `--probe` rather
than being excluded.

## The pin, because one instrument exits non-zero on purpose

`skill_length.py --check` exits 1 on this tree and has since it was written. Its
last line says why: rule 4's cap is measured in `wc -l`, under which all ten
skills pass, and the exit code is the rendered-column reading the rule meant
rather than the unit it names. Changing the rule is the owner's.

A test that asserted every instrument exits 0 would therefore be red on main,
and the one thing worse than seven unarmed instruments is an eighth check that
every seat learns to ignore. So `STANDING` below is a pin in the shape this
repository already uses for `UNCOVERED` in `tests/test_ci_coverage.py`: the
expected exit status of every instrument that does not exit 0, with the reason.
It may shrink and may not grow. An instrument that newly breaks turns red, and
an instrument that gets repaired turns red until its line is deleted.

## The positive control

`test_discovery_finds_every_instrument_on_disk` asserts the set is not smaller
than what was measured on 2026-11-09. Without it, a rename under
`skills/_validation/` or a `--help` that stops parsing empties the set and this
whole file goes green by finding nothing, which is L-A21's failure exactly: a
check that saw nothing must not read like a check that saw nothing wrong.

Run with `python3 -m pytest tests/test_validation_instruments.py -q`. No
network, no database. One instrument takes about a minute, which is noted on its
line rather than hidden.
"""

from __future__ import annotations

import functools
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "skills" / "_validation"

# A program under skills/_validation/ is an instrument when its own --help
# offers one of these. `--check` is the convention; `earned_pass.py` is the
# meta-instrument that probes the others and spells its entry point --probe.
VERIFY_FLAGS = ("--check", "--probe")

# Measured 2026-11-09 by this file's own discovery. Seven instruments, which is
# the number the skill seat's handoff named. This set may grow freely, and may
# not shrink: a name that disappears from skills/_validation/ turns the control
# below red, so a rename is a decision somebody makes rather than a set that
# quietly empties.
#
# `prose_distribution.py` is the seventh and it landed on `main` in #861 while
# this branch was open, which is the case this file was written for: it was
# discovered and run with no edit here, and the only reason its name is in this
# set is to pin it, so that a later run which breaks it turns red rather than
# dropping it from the set and staying green.
KNOWN = {
    "checklist_position.py",
    "claim_receipt.py",
    "earned_pass.py",
    "prediction_basis.py",
    "project_fixture_probe.py",
    "prose_distribution.py",
    "skill_length.py",
}

# Every instrument whose verification mode does not exit 0 on this tree, with
# the exit status and the reason. May shrink, may not grow.
STANDING = {
    # Rule 4's cap is 120 lines. All ten skills pass it in `wc -l` and none
    # passes it rendered at 100 columns, which is the unit the instrument
    # argues the rule meant. Its own last line says changing the rule is the
    # owner's, so this is a standing finding addressed to her rather than a
    # regression, and it has been standing in a terminal nobody reads.
    "skill_length.py": 1,
}

# Instruments that cost real time. Measured 2026-11-09, worst case first:
# project_fixture_probe 57s, earned_pass 7.3s, claim_receipt 2.3s,
# checklist_position 1.3s, prose_distribution 0.4s, skill_length 0.3s,
# prediction_basis 0.2s.
TIMEOUT_SECONDS = 300


def programs() -> list[str]:
    """Every program under skills/_validation/. Filesystem only, no subprocess.

    This is what the tests below parametrize over, and it is deliberately not
    the instrument set. Asking ten programs for their `--help` is ten
    subprocesses, and doing it at module scope to feed `parametrize` would run
    them during collection, which is the defect Ursa's exo seat reported on the
    bus the same morning about a tool of its own: a `main()` at module scope
    turned an import into sixty live requests. Quoting that lesson in this
    file's own header and then committing it here would have been the second
    instance. So collection reads the directory, and the subprocess happens
    inside the test that needs it.
    """
    return sorted(path.name for path in VALIDATION.glob("*.py"))


@functools.lru_cache(maxsize=None)
def verify_flag(name: str) -> str | None:
    """The program's verification entry point, read off its own --help."""
    proc = subprocess.run([sys.executable, str(VALIDATION / name), "--help"],
                          cwd=ROOT, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return None
    for flag in VERIFY_FLAGS:
        if flag in proc.stdout:
            return flag
    return None


@functools.lru_cache(maxsize=None)
def instruments() -> tuple[tuple[str, str], ...]:
    """Every instrument under skills/_validation/, name to verification flag."""
    return tuple((name, flag) for name in programs()
                 if (flag := verify_flag(name)) is not None)


def test_the_validation_directory_exists_and_holds_programs():
    """The outermost control: this file's whole subject could be moved."""
    assert VALIDATION.is_dir(), f"{VALIDATION} is gone, so nothing below means anything"
    assert sorted(VALIDATION.glob("*.py")), "no programs under skills/_validation/"


def test_discovery_finds_every_instrument_on_disk():
    """The positive control. Without it an empty set reads as a clean run."""
    found = dict(instruments())
    missing = KNOWN - set(found)
    assert not missing, (
        f"{sorted(missing)} offered a verification flag on 2026-11-09 and does "
        "not now. Either the file moved, or its --help stopped listing the "
        "flag, in which case nothing in this repository runs it any more. If "
        "the removal is deliberate, delete the name from KNOWN in the same "
        "commit and say so.")
    assert len(found) >= len(KNOWN)


def test_every_standing_pin_names_a_real_instrument():
    """A pin for an instrument that no longer exists hides a green instrument."""
    stale = set(STANDING) - set(dict(instruments()))
    assert not stale, (
        f"{sorted(stale)} is pinned as exiting non-zero and is not discovered. "
        "Delete the line.")


@pytest.mark.parametrize("name", programs())
def test_the_instrument_exits_as_pinned(name):
    """One test per program, so a failure names the instrument in its own id.

    A program with no verification flag is skipped rather than filtered out of
    collection, because a skip is visible in the run and an absent test is not.
    """
    flag = verify_flag(name)
    if flag is None:
        assert name not in KNOWN, "the positive control covers this case"
        pytest.skip(f"{name} offers none of {VERIFY_FLAGS}, so nothing to run")
    proc = subprocess.run([sys.executable, str(VALIDATION / name), flag],
                          cwd=ROOT, capture_output=True, text=True,
                          timeout=TIMEOUT_SECONDS)
    expected = STANDING.get(name, 0)
    tail = "\n".join((proc.stdout + proc.stderr).strip().split("\n")[-6:])
    assert proc.returncode == expected, (
        f"skills/_validation/{name} {flag} exited {proc.returncode}, pinned at "
        f"{expected}.\n"
        "If this is a regression, fix the instrument or the tree it reads. If "
        "the instrument is now correct to exit non-zero, add it to STANDING "
        "with the reason. If it was pinned and is now green, delete its line.\n"
        f"Its last words:\n{tail}")
