#!/usr/bin/env python3
"""A flag that names a target must be classified, and the list is derived.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

Two findings of 2026-11-02 meet here and they are the same finding.

`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
ends by naming the work: "Making the 56 an enumerated set that each tool must
declare against is the next day-sized piece of work." Its own repair shipped
with a probe that was a hand list of three, and the incident says why that is
not enough: such a list "cannot tell the difference between a tool that
resolves its target and a tool nobody has looked at".

The skill seat reached the same shape from the other side and handed it over:
its `GATES` was a hand list of five, "so the probe cannot tell a gate that
refuses from a gate nobody registered", and it carded deriving the list with
`ast` and failing when a module is missing from it.

So the gate here is not "do these three tools refuse". It is "is every flag in
the tree accounted for", and the census it asks that over is parsed from the
source rather than typed out. The three tools the incident repaired are now a
consequence of the gate rather than the gate itself.

The probe reaches no network and no database. Every tool it runs is run with a
value nothing carries, which is the one input that cannot do work.
"""

import io
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import target_census as tc                                       # noqa: E402
import resolve_target as rt                                      # noqa: E402

CENSUS = tc.census()


def test_the_census_is_derived_and_not_empty():
    """An empty census is the failure the whole file is guarding against."""
    assert CENSUS, "no add_argument call found under tools/, so nothing was measured"
    assert len(CENSUS) > 200, f"only {len(CENSUS)} flags found; the tree has 45 tools"
    # One row per (file, flag) pair, not per call site: board.py declares --id
    # on three subcommands and they are one judgment.
    assert len({(f.file, f.flag) for f in CENSUS}) == len(CENSUS)


def test_every_flag_needing_a_judgment_has_one():
    """The gate. A new target-naming flag is a red pull request, not a backlog item.

    The failure message names the file, the flag and its help text, so a run
    that trips this has what it needs to classify the flag without re-deriving
    the census.
    """
    missing = tc.undeclared(CENSUS)
    assert not missing, "classified by nobody: " + ", ".join(
        f"{f.file} {f.flag} ({f.help or 'no help'})" for f in missing)


def test_no_declaration_outlives_its_flag():
    """A declaration file that only grows becomes the hand list it replaced."""
    stale = tc.stale_declarations(CENSUS)
    assert not stale, f"declared and gone from the tree: {stale}"


def test_every_judgment_names_a_kind_the_module_defines():
    assert not tc.bad_kinds()
    for key, judgment in tc.DECLARED.items():
        assert judgment.kind in tc.KINDS, key
        if judgment.offline:
            assert judgment.kind == "roster", \
                f"{key}: only a roster flag can be unprobeable"


def test_the_switches_and_the_choices_need_no_judgment():
    """Why the population is 118 and not 248, asserted rather than asserted-about.

    A boolean switch carries no value, and `choices=` is refused by argparse
    before any tool code runs. Both are derivable, so neither is a judgment
    anybody has to maintain, and a declaration for one would be dead weight.
    """
    derived = [f for f in CENSUS if f.derived]
    assert derived, "nothing was auto-classified, so the derivation is broken"
    for flag in derived:
        assert (flag.file, flag.flag) not in tc.DECLARED, \
            f"{flag.file} {flag.flag} is both derived as {flag.derived} and declared"


def test_the_roster_flags_split_into_probeable_and_declared_offline():
    """And "nobody has looked" is not one of the two options."""
    roster = [k for k, j in tc.DECLARED.items() if j.kind == "roster"]
    assert roster, "no roster flag in the census, so the probe measures nothing"
    probeable = tc.roster_flags(probeable=True)
    offline = tc.roster_flags(probeable=False)
    assert set(probeable) | set(offline) == set(roster)
    assert not set(probeable) & set(offline)
    assert probeable, "every roster flag declared unprobeable; the probe is empty"
    for key in offline:
        assert len(tc.DECLARED[key].offline) > 20, \
            f"{key}: the reason it cannot be probed has to be a reason"


@pytest.mark.parametrize("file,flag", tc.roster_flags(probeable=True))
def test_each_probeable_roster_flag_refuses_a_value_nothing_carries(file, flag):
    """The class itself, one test case per flag so the failure names the tool.

    Non-zero rather than exactly 4, because two of the four tools the incident
    found already refusing exit 2 and both were refusing correctly. The shared
    number is asserted for the shared helper in test_resolve_target.py; here
    the requirement is that a zero is never the answer.
    """
    ok, code, said = tc.probe_one(file, flag)
    assert ok, f"{file} {flag} exited {code} on {tc.NO_SUCH!r}: {said[:400]}"
    assert tc.NO_SUCH in said, \
        f"{file} {flag} refused without naming the value it refused"


def test_the_three_repaired_today_are_in_the_probe_rather_than_in_a_list():
    """The point of the whole file, stated as an assertion.

    `tools/target_census.py --probe` found these three; nobody listed them.
    They are asserted present in the derived probe set, which is what keeps
    them covered when somebody edits the census.
    """
    probeable = set(tc.roster_flags(probeable=True))
    for key in [("feed_health.py", "--only"),
                ("panel_adversary.py", "--skill"),
                ("panel_provenance.py", "--skill")]:
        assert key in probeable, f"{key} dropped out of the probe"


def test_check_refuses_an_empty_census_rather_than_passing_it(tmp_path):
    """The skill seat's finding, applied to this module before it ships.

    A `--check` pointed at a directory with no tools must not print its pass
    sentence over a denominator of zero. Exit 2, because `trigger_test.py`
    already reserves 2 for a data error and this is one.
    """
    (tmp_path / "tools").mkdir()
    out = io.StringIO()
    assert tc.check(tmp_path, stream=out) == tc.EXIT_EMPTY
    said = out.getvalue()
    assert "refused" in said
    assert "ok:" not in said


def test_check_says_what_it_was_computed_over():
    """A gate you are about to trust prints its denominator."""
    out = io.StringIO()
    assert tc.check(stream=out) == tc.EXIT_OK
    said = out.getvalue()
    assert f"{len(CENSUS)} distinct (file, flag) pairs" in said
    assert f"{len(tc.needs_judgment(CENSUS))} needing a judgment" in said
    assert "by kind:" in said


def test_the_cli_agrees_with_the_functions():
    """`--check` as a person runs it, since that is what a charter step calls."""
    done = subprocess.run([sys.executable, str(ROOT / "tools" / "target_census.py"),
                           "--check"], capture_output=True, text=True, timeout=120)
    assert done.returncode == tc.EXIT_OK, done.stdout + done.stderr
    assert "classified" in done.stdout


def test_the_census_module_is_itself_in_the_census():
    """A sweep that cannot see its own tool reports a domain it does not cover.

    `tools/resolve_target.py` shipped reading `sys.argv` directly and so was
    invisible to the sweep that classifies every flag. Asserted here so the
    same hole cannot open in the module whose whole job is the sweep.
    """
    mine = [f for f in CENSUS if f.file == "target_census.py"]
    assert {f.flag for f in mine} == {"--check", "--probe", "--list"}
    for flag in mine:
        assert flag.derived == "switch", \
            "every flag on this tool is a switch, so none needs a judgment"


def test_the_exit_codes_do_not_collide_with_the_shared_refusal():
    """4 is "the thing you named is not here" across this tree, so it is not reused."""
    assert tc.EXIT_OK == 0
    assert tc.EXIT_PROBLEM == 1
    assert tc.EXIT_EMPTY == 2
    assert rt.EXIT_UNKNOWN_TARGET == 4
    assert rt.EXIT_UNKNOWN_TARGET not in {tc.EXIT_OK, tc.EXIT_PROBLEM,
                                          tc.EXIT_EMPTY}


def test_the_listing_runs_and_classifies_every_row():
    out = io.StringIO()
    assert tc.listing(stream=out) == tc.EXIT_OK
    assert "UNCLASSIFIED" not in out.getvalue()


# ------------------------- a judgment declared twice is a judgment discarded


def test_no_target_is_declared_twice_in_the_table():
    """The repeat that was live on `main` when this test was written.

    `("prose_symbols.py", "--root")` and `("prose_symbols.py", "paths")` each
    appeared twice in `DECLARED`, once from #813's reader and once from the
    engineer seat, so the table held 139 written rows and the gate printed
    `137 declared`. Both pairs agreed on the kind, so no answer was wrong. What
    was discarded was a reason: two comment blocks each explaining a row, one
    of each pair attached to nothing, and no way for a reader to tell which.
    """
    assert tc.repeated_declarations() == []


def test_a_duplicate_declaration_is_caught_in_a_real_file(tmp_path):
    """Against an artifact known to fail it, per incident 32, and the artifact
    is this module's own source with one line duplicated rather than a fixture
    written to look wrong."""
    source = (ROOT / "tools" / "target_census.py").read_text()
    row = '    ("pr_backlog.py", "--prs"): Judgment("path"),'
    assert row in source
    damaged = source.replace(
        row, row + '\n    ("pr_backlog.py", "--prs"): Judgment("opaque"),', 1
    )
    found = tc.repeated_declarations(damaged)
    assert len(found) == 1
    key, lines = found[0]
    assert key == ("pr_backlog.py", "--prs")
    assert len(lines) == 2 and lines[0] + 1 == lines[1]


def test_the_dict_itself_cannot_answer_the_question(tmp_path):
    """Why the check reads text and not `DECLARED`.

    A dict literal keeps the last value for a repeated key and reports
    nothing, so the duplicate is already gone by the time the module is
    imported. This is the same shape alexandria/exo found in
    `tools/sentinel.py` the same morning, where `dict(args.part)` dropped a
    part somebody had named.
    """
    assert len({"a": 1, "a": 2}) == 1  # noqa: F601 - the defect, asserted
    assert dict([("a", 18.0), ("a", 6.9)]) == {"a": 6.9}


def test_a_file_with_no_declared_table_is_refused_rather_than_called_clean():
    """An empty answer from a source that was never read is the confident zero
    this whole module exists to refuse, so it raises instead."""
    with pytest.raises(tc.CannotRead):
        tc.repeated_declarations("X = 1\n")


def test_check_fails_on_a_repeat_and_says_how_short_the_count_is(tmp_path):
    """The whole tool, run as a command, over a copy of the tree with one row
    duplicated. A monkeypatch would be testing the assertion and not the gate,
    because the gate's input is the file on disk under its own `__file__`.
    """
    shutil.copytree(ROOT / "tools", tmp_path / "tools")
    target = tmp_path / "tools" / "target_census.py"
    row = '    ("pr_backlog.py", "--now"): Judgment("date"),'
    source = target.read_text()
    assert row in source
    target.write_text(source.replace(row, row + "\n" + row, 1))
    done = subprocess.run([sys.executable, str(target), "--check"],
                          capture_output=True, text=True)
    assert done.returncode == tc.EXIT_PROBLEM, done.stdout
    assert "--now is declared 2 times" in done.stdout
    assert "short by 1" in done.stdout
    # And the undamaged tool answers clean on the same copied tree, so the
    # failure above is the duplicate and not the copy.
    target.write_text(source)
    clean = subprocess.run([sys.executable, str(target), "--check"],
                           capture_output=True, text=True)
    assert clean.returncode == tc.EXIT_OK, clean.stdout


def test_the_four_flags_pr_backlog_brought_to_main_are_declared():
    """#836 landed `tools/pr_backlog.py` at 06:26Z on 2026-11-09 with four
    unclassified targets, which turned `main` red for every seat. The judgments
    are asserted here and not only the fact of them."""
    assert tc.DECLARED[("pr_backlog.py", "--prs")].kind == "path"
    assert tc.DECLARED[("pr_backlog.py", "--merged")].kind == "path"
    assert tc.DECLARED[("pr_backlog.py", "--since")].kind == "date"
    assert tc.DECLARED[("pr_backlog.py", "--now")].kind == "date"
