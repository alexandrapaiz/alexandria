"""The completeness terminator, and the four verdicts only a reader reaches.

`tools/sentinel.py` answers one class, and this file holds the instance that
produced it. On 2026-11-09 at 06:04Z this seat backgrounded the full suite and
the harness reported `completed`, `exit code 0`, four seconds later. The
process was alive and the output file held zero bytes. That is the seventh
instance on this seat's file of a false zero, and the first with a remedy
standing in front of it.

Every prior remedy in the register prescribes `pipefail` or a redirect, and
there was no pipe in any of the last two instances. The remedy that does reach
them is a line the work appends after it is reaped, because what a killed
process leaves behind is the absence of a line, and absence is the one thing a
reader can check without trusting the reporter.

Three things are under test here.

The writer, because a verdict composed before the child is reaped would be
true about the launch and silent about the work, which is the defect one layer
up wearing this file's own clothes.

The reader, and this is the weight of the file. Four of the seven codes cannot
be printed by the process that did the work: `absent`, `stale`, `truncated`
and `continued`. A test that only ran clean children would exercise none of
them, so every one of the four is produced here by damaging a real output file
rather than by writing a fixture that looks damaged. That is incident 32's
rule, which this repository states verbatim in `tests/test_check_registers.py`
and which cost a gate its credibility once already: every gate is tested
against an artifact known to fail it before the gate is trusted.

The residual, from alexandria/exo's rule of the same morning: a composition
claim must publish its residual, always, and is refused when the residual
reaches the largest part the claim names. The case that triggered it is in
here as a regression: `18 + 6.9` published under the word `measured` against a
total of 43.

And the two holes alexandria/exo found in that first version, which are the
reason this file grew. Both arrived as shell transcripts rather than as
readings of the code, and neither was in the thirty-four cases this file
already held, so each one is here as the transcript it arrived as. A negative
part laundered an OVERCOUNT past a gate that only looked at the sum, and a
repeated `--part` name was `dict()`'s last-wins, so a figure that had been
named was dropped without a word.

No count appears in this docstring. The parametrized sets below are the count.

Run with `python3 -m pytest tests/test_sentinel.py -q`.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import sentinel as sn  # noqa: E402

TOOL = ROOT / "tools" / "sentinel.py"


def run_child(out: Path, code: str, **kw):
    return sn.run_guarded([sys.executable, "-c", code], out, **kw)


# ----------------------------------------------------------------- the writer


def test_a_clean_child_leaves_a_verdict_a_reader_can_check(tmp_path):
    out = tmp_path / "ok.txt"
    status, line = run_child(out, "print('rows: 4')", label="rows")
    assert status == 0
    assert line.startswith("SENTINEL run=")
    verdict = sn.read_verdict(out)
    assert verdict.ok
    assert verdict.label == "rows"
    assert verdict.fields["exit"] == "0"


def test_the_verdict_is_the_last_line_and_the_output_is_above_it(tmp_path):
    out = tmp_path / "ordered.txt"
    run_child(out, "print('one'); print('two')")
    lines = out.read_text().strip().split("\n")
    assert lines[0].startswith("SENTINEL") and " BEGIN " in lines[0]
    assert lines[1:3] == ["one", "two"]
    assert " COMPLETE " in lines[-1]


def test_a_failing_child_is_complete_and_not_ok(tmp_path):
    """A known end that failed is not the same claim as no end at all.

    Collapsing the two is what makes a reader treat silence as success, so the
    verdict keeps `COMPLETE` and the code says `nonzero`.
    """
    out = tmp_path / "bad.txt"
    status, _ = run_child(out, "import sys; sys.exit(3)")
    assert status == 3
    verdict = sn.read_verdict(out)
    assert verdict.complete is True
    assert verdict.ok is False
    assert verdict.code == "nonzero"
    assert "exit=3" in verdict.reason


def test_a_child_killed_at_the_limit_says_so_rather_than_nothing(tmp_path):
    out = tmp_path / "slow.txt"
    status, _ = run_child(out, "import time; time.sleep(30)", timeout=0.2)
    assert status == 1
    verdict = sn.read_verdict(out)
    assert verdict.code == "timeout"
    assert verdict.fields["limit"] == "0.2"


def test_a_child_that_dies_on_a_signal_is_named_by_its_signal(tmp_path):
    out = tmp_path / "killed.txt"
    run_child(out, "import os, signal; os.kill(os.getpid(), signal.SIGKILL)")
    verdict = sn.read_verdict(out)
    assert verdict.code == "signal"
    assert verdict.fields["signal"] == "SIGKILL"


def test_a_command_that_does_not_exist_is_a_known_end(tmp_path):
    out = tmp_path / "missing.txt"
    status, _ = sn.run_guarded(["./no-such-binary-here"], out)
    assert status == 127
    assert sn.read_verdict(out).code == "nonzero"


def test_the_byte_count_is_in_the_verdict_because_a_fast_pass_is_the_tell(
    tmp_path,
):
    """The cheap half of the live instance, and the only half a verdict gives.

    A child that backgrounds its own work and exits is below what this tool
    waits for, so the verdict will say `COMPLETE exit=0` over work still
    running, exactly as the harness did. `bytes` is what a reader has left: a
    sixteen-minute suite that wrote nothing did not run.
    """
    out = tmp_path / "hollow.txt"
    run_child(out, "pass", label="suite")
    verdict = sn.read_verdict(out)
    assert verdict.ok
    body = [
        ln
        for ln in out.read_text().split("\n")
        if ln.strip() and not ln.startswith("SENTINEL")
    ]
    assert body == []
    assert int(verdict.fields["bytes"]) < 200


# ----------------------------------------------------------------- the reader


def test_the_live_instance_a_running_suite_reads_as_absent(tmp_path):
    """06:04Z, four seconds in: pytest alive, file at zero bytes, exit 0 said.

    This is the shape rather than a reconstruction: progress lines and no
    verdict, which is what a killed or still-running suite leaves.
    """
    out = tmp_path / "suite.txt"
    out.write_text(
        "........................................ [  4%]\n"
        "........................................ [  9%]\n"
    )
    verdict = sn.read_verdict(out)
    assert verdict.code == "absent"
    assert verdict.ok is False
    assert "still running" in verdict.reason


def test_a_file_holding_only_a_begin_line_is_absent_and_not_truncated(tmp_path):
    """Found by running the tool against a live suite rather than by reading it.

    Thirty seconds into a real run the file holds one BEGIN and nothing else,
    and the first version of this file called that `truncated`, because its
    damage test was that the last line starts with the marker. A started run
    with no verdict yet is the commonest absence there is, and naming it
    damage would send a reader looking for a cut write.
    """
    out = tmp_path / "started.txt"
    out.write_text(sn.begin_line("abc123def456", "suite", ["pytest", "tests/"]))
    verdict = sn.read_verdict(out)
    assert verdict.code == "absent"
    assert verdict.run == "abc123def456"
    assert "began" in verdict.reason and "no verdict" in verdict.reason


def test_a_begin_line_followed_by_output_is_still_absent(tmp_path):
    out = tmp_path / "midway.txt"
    with out.open("w") as fh:
        fh.write(sn.begin_line("abc123def456", "suite", ["pytest"]))
        fh.write("..... [ 42%]\n")
    assert sn.read_verdict(out).code == "absent"


def test_a_marker_line_that_is_neither_a_begin_nor_a_verdict_is_truncated(
    tmp_path,
):
    out = tmp_path / "cut-begin.txt"
    out.write_text("SENTINEL run=abc123def456 label=suite BEG")
    assert sn.read_verdict(out).code == "truncated"


def test_a_zero_byte_output_is_absent_and_this_is_what_defeats_a_count_guard(
    tmp_path,
):
    """Ursa/exo conceded the denominator guard on exactly this input.

    A guard that checks rows against a denominator passes an empty file by
    having nothing to check. The terminator fails it, because the terminator is
    the thing that is missing.
    """
    out = tmp_path / "empty.txt"
    out.write_bytes(b"")
    verdict = sn.read_verdict(out)
    assert verdict.code == "absent"
    assert "0 bytes" in verdict.reason


def test_a_file_that_was_never_created_is_absent_rather_than_an_error(tmp_path):
    verdict = sn.read_verdict(tmp_path / "never.txt")
    assert verdict.code == "absent"
    assert verdict.reason == "no such file"


def test_a_second_run_appending_to_one_file_cannot_inherit_the_first_verdict(
    tmp_path,
):
    """The nastiest shape, and the reason the verdict carries a nonce.

    Two runs, one output path, the second killed. The file holds a real
    `COMPLETE exit=0`, written by a real process, about work that is not the
    work being asked about.
    """
    out = tmp_path / "twice.txt"
    run_child(out, "print('first run')", label="suite")
    assert sn.read_verdict(out).ok
    with out.open("a") as fh:
        fh.write(sn.begin_line("ffffffffffff", "suite", ["second", "run"]))
        fh.write("........ [ 9%]\n")
    verdict = sn.read_verdict(out)
    assert verdict.code == "stale"
    assert "earlier run" in verdict.reason


def test_a_verdict_with_no_begin_above_it_cannot_be_tied_to_a_run(tmp_path):
    out = tmp_path / "forged.txt"
    out.write_text(
        "SENTINEL run=deadbeefcafe label=suite COMPLETE exit=0 "
        "seconds=1.0 bytes=10 at=2026-11-09T06:00:00+00:00\n"
    )
    verdict = sn.read_verdict(out)
    assert verdict.code == "stale"
    assert "no BEGIN" in verdict.reason


def test_a_verdict_cut_mid_write_is_truncated_rather_than_read_as_complete(
    tmp_path,
):
    out = tmp_path / "cut.txt"
    run_child(out, "print('work')")
    whole = out.read_text()
    out.write_text(whole[: whole.rindex("at=")])
    verdict = sn.read_verdict(out)
    assert verdict.code == "truncated"
    assert "inside it" in verdict.reason


def test_a_marker_line_that_does_not_parse_is_truncated_not_absent(tmp_path):
    out = tmp_path / "half.txt"
    out.write_text("rows: 3\nSENTINEL run=abc123def456 label=suite COMPL\n")
    assert sn.read_verdict(out).code == "truncated"


def test_output_after_the_verdict_means_the_verdict_covers_less_than_the_file(
    tmp_path,
):
    out = tmp_path / "more.txt"
    run_child(out, "print('work')")
    with out.open("a") as fh:
        fh.write("and then more happened\n")
    verdict = sn.read_verdict(out)
    assert verdict.code == "continued"
    assert "1 line(s)" in verdict.reason


def test_asking_for_one_label_refuses_another_seats_verdict(tmp_path):
    out = tmp_path / "other.txt"
    run_child(out, "pass", label="ledger")
    assert sn.read_verdict(out, label="ledger").ok
    verdict = sn.read_verdict(out, label="suite")
    assert verdict.code == "stale"
    assert "label=ledger" in verdict.reason


@pytest.mark.parametrize("code", sn.READER_CODES)
def test_every_reader_side_code_is_reachable_and_none_reports_ok(code, tmp_path):
    """The set is the count, and the four are the whole argument for the file.

    A writer cannot print any of these, so a suite that only ran children
    would leave all four untested while looking thorough.
    """
    out = tmp_path / f"{code}.txt"
    if code == "absent":
        out.write_text("progress\n")
    elif code == "stale":
        out.write_text(
            "SENTINEL run=deadbeefcafe label=x COMPLETE exit=0 "
            "seconds=1.0 bytes=1 at=2026-11-09T06:00:00+00:00\n"
        )
    elif code == "truncated":
        out.write_text("SENTINEL run=deadbeefcafe label=x COMPLETE exit=0 s")
    else:
        run_child(out, "pass", label="x")
        with out.open("a") as fh:
            fh.write("more\n")
    verdict = sn.read_verdict(out)
    assert verdict.code == code
    assert verdict.ok is False


# --------------------------------------------------------------- the residual


def test_the_entry_that_triggered_the_residual_rule_is_refused(tmp_path):
    """`/srv/asc 18G` and `/tmp 6.9G` published as `measured` against 43G.

    The residual is larger than the largest part the claim names, so the word
    `measured` was carrying 18.1 GiB nobody had looked at.
    """
    comp = sn.Composition(43.0, {"srv": 18.0, "tmp": 6.9}, "GiB")
    assert round(comp.residual, 1) == 18.1
    assert comp.ok is False
    report = "\n".join(comp.report())
    assert "unattributed" in report
    assert "REFUSED" in report


def test_the_residual_is_published_even_when_the_claim_passes(tmp_path):
    """The rule is not a gate with a quiet pass. It prints either way."""
    comp = sn.Composition(100.0, {"a": 60.0, "b": 35.0})
    assert comp.ok is True
    report = "\n".join(comp.report())
    assert "unattributed" in report and " 5 " in report + " "
    assert "ok: the residual is under a" in report


def test_a_residual_that_reaches_the_largest_part_is_refused(tmp_path):
    comp = sn.Composition(100.0, {"a": 30.0, "b": 10.0})
    assert comp.residual == 60.0
    assert comp.ok is False
    # And the boundary is `reaches`, not `exceeds`: equal is refused.
    assert sn.Composition(100.0, {"a": 50.0, "b": 0.0}).ok is False
    assert sn.Composition(100.0, {"a": 60.0, "b": 0.0}).ok is True


def test_parts_that_sum_above_the_total_are_an_overcount_not_a_residual(
    tmp_path,
):
    """Double counting is worse than an unnamed remainder and reads the same.

    A negative residual printed as a residual invites a reader to shrug at a
    minus sign. Named as an overcount it says what it is: two parts counting
    one thing.
    """
    comp = sn.Composition(10.0, {"a": 8.0, "b": 7.0})
    assert comp.overcount is True
    assert comp.ok is False
    report = "\n".join(comp.report())
    assert "OVERCOUNT" in report
    assert "count the same thing" in report


def test_a_claim_with_no_parts_at_all_is_refused(tmp_path):
    """The degenerate case, and it is the one a report reaches by saying
    nothing: a total with no composition is all residual."""
    comp = sn.Composition(43.0, {})
    assert comp.residual == 43.0
    assert comp.ok is False
    assert "names no parts at all" in "\n".join(comp.report())


# ------------------------------------- the two holes alexandria/exo found


def test_a_negative_part_cannot_launder_an_impossible_one(tmp_path):
    """exo's transcript, verbatim: `--compose 43 --part a=50` refuses, and
    adding `--part credit=-20` makes the identical claim about `a` pass.

    The gate was on the sum, so `43 = 50 + (-20) + 13` balanced and `a 50 GiB
    116.3%` printed one line above the word `ok`. Any negative term buys
    headroom for an impossible part, one unit for one unit.
    """
    launder = sn.Composition(43.0, {"a": 50.0, "credit": -20.0}, "GiB")
    # The arithmetic that let it through is still the arithmetic. What changed
    # is that the sum is no longer the only thing asked.
    assert round(launder.residual, 1) == 13.0
    assert launder.overcount is False
    assert launder.ok is False
    report = "\n".join(launder.report())
    assert "116.3%" in report
    assert "\nok:" not in "\n" + report


def test_both_gates_refuse_the_laundered_claim_independently(tmp_path):
    """The repair is two gates and not one, so neither is load-bearing alone.

    exo proposed `max(part) > total`, which is here and holds for this claim.
    This seat added the refusal of a negative part, which also holds. The test
    asserts both, because a later run that decides a negative part is legal
    after all must not take exo's check down with it.
    """
    launder = sn.Composition(43.0, {"a": 50.0, "credit": -20.0}, "GiB")
    assert launder.oversized == (("a", 50.0),)
    assert launder.negative == (("credit", -20.0),)
    # And the negative gate is the one that speaks, because it is the more
    # specific diagnosis: the impossible part is a consequence of the credit.
    assert "A part is a share" in (launder.refusal or "")


def test_a_negative_part_is_refused_even_when_nothing_is_oversized(tmp_path):
    """The form exo's own check does not reach, which is why the second gate
    is here. `40 + (-20) + 20` against 43 has no part above the total and no
    overcount, and `a` and `c` still sum to 60 against a total of 43."""
    comp = sn.Composition(43.0, {"a": 40.0, "b": -20.0, "c": 20.0}, "GiB")
    assert comp.oversized == ()
    assert comp.overcount is False
    assert comp.residual == 3.0
    assert comp.ok is False
    assert "b is -20 GiB" in (comp.refusal or "")


def test_one_part_larger_than_the_whole_is_not_two_parts_double_counting(
    tmp_path,
):
    """A message repair found while fixing the gate above.

    `--compose 43 --part a=50` was refused, correctly, with the sentence `at
    least two of them count the same thing`. There is one part. The overcount
    line now states the excess and leaves the diagnosis to the refusal, which
    names the part that cannot fit.
    """
    comp = sn.Composition(43.0, {"a": 50.0}, "GiB")
    assert comp.ok is False
    report = "\n".join(comp.report())
    assert "OVERCOUNT" in report
    assert "count the same thing" not in report
    assert "a alone is 50 GiB" in report
    # And the two-part reading is still available when there are two parts.
    two = "\n".join(sn.Composition(10.0, {"a": 8.0, "b": 7.0}).report())
    assert "count the same thing" in two


def test_a_repeated_part_name_is_refused_rather_than_resolved(tmp_path):
    """exo's second transcript: `--part a=18 --part a=6.9` printed `a 6.9`.

    `dict(pairs)` is last-wins. The verdict direction was safe, because
    dropping a part only raises the residual, but the figure 18 was named by
    the caller and never appeared, in the one table whose whole job is to
    print a composition honestly.
    """
    # The old behaviour, kept here as the thing being refused.
    assert dict([("a", 18.0), ("a", 6.9)]) == {"a": 6.9}
    with pytest.raises(sn.RepeatedPart) as caught:
        sn.collect_parts([("a", 18.0), ("a", 6.9)], "GiB")
    report = caught.value.report()
    assert "REFUSED" in report
    # The dropped figure is in the refusal, which is the whole complaint.
    assert "18 GiB" in report and "6.9 GiB" in report
    assert caught.value.repeats == {"a": [18.0, 6.9]}


def test_the_sum_is_not_the_repair_for_a_repeated_name(tmp_path):
    """exo's preferred direction, taken. A sum would read 24.9 and the reader
    could not tell it from a single `--part a=24.9`, so which of the two
    readings was meant is exactly what the quiet repair destroys."""
    report = sn.RepeatedPart({"a": [18.0, 6.9]}, "GiB").report()
    assert "24.9" not in report
    assert "summing them invents a third" in report


def test_distinct_names_and_a_single_figure_both_still_pass(tmp_path):
    """The refusal above must not catch the two ways out it recommends."""
    assert sn.collect_parts([("a", 18.0), ("b", 6.9)]) == {"a": 18.0, "b": 6.9}
    assert sn.collect_parts([("a", 24.9)]) == {"a": 24.9}
    assert sn.collect_parts([]) == {}


def test_three_readings_under_one_name_are_all_reported(tmp_path):
    """Not only the first and the last. A refusal that printed two of three
    would be the same defect one figure further along."""
    with pytest.raises(sn.RepeatedPart) as caught:
        sn.collect_parts([("a", 1.0), ("a", 2.0), ("a", 3.0)])
    assert caught.value.repeats == {"a": [1.0, 2.0, 3.0]}
    assert "given 3 times" in caught.value.report()


# ---------------------------------------------------------------- the command


def test_the_cli_exits_nonzero_on_an_absent_verdict(tmp_path):
    out = tmp_path / "running.txt"
    out.write_text("........ [ 4%]\n")
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(out)], capture_output=True, text=True
    )
    assert proc.returncode == 1
    assert "code=absent" in proc.stdout
    assert "A missing verdict is not a passing one" in proc.stdout


def test_the_cli_runs_a_command_and_reads_its_own_output_back(tmp_path):
    out = tmp_path / "cli.txt"
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--label",
            "demo",
            "--out",
            str(out),
            "--",
            sys.executable,
            "-c",
            "print('ran')",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert " COMPLETE exit=0 " in proc.stdout
    back = subprocess.run(
        [sys.executable, str(TOOL), "--expect-label", "demo", str(out)],
        capture_output=True,
        text=True,
    )
    assert back.returncode == 0
    assert ": ok" in back.stdout


def test_the_cli_passes_the_childs_own_status_through(tmp_path):
    out = tmp_path / "cli-bad.txt"
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--out",
            str(out),
            "--",
            sys.executable,
            "-c",
            "import sys; sys.exit(7)",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 7
    assert "code=nonzero" in proc.stdout


def test_the_cli_compose_mode_exits_nonzero_on_an_unnamed_majority(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--compose",
            "43",
            "--part",
            "srv=18",
            "--part",
            "tmp=6.9",
            "--unit",
            "GiB",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "unattributed" in proc.stdout


def test_the_cli_refuses_the_laundered_claim_exo_sent_back(tmp_path):
    """The transcript as it arrived, through the command line, because that is
    where it was found. The library test above cannot see `argparse`."""
    base = [sys.executable, str(TOOL), "--compose", "43", "--unit", "GiB"]
    bare = subprocess.run(
        base + ["--part", "a=50"], capture_output=True, text=True
    )
    assert bare.returncode == 1
    with_credit = subprocess.run(
        base + ["--part", "a=50", "--part", "credit=-20"],
        capture_output=True,
        text=True,
    )
    assert with_credit.returncode == 1, with_credit.stdout
    assert "a                50 GiB  116.3%" in with_credit.stdout
    assert "REFUSED" in with_credit.stdout


def test_the_cli_refuses_a_repeated_part_name(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--compose",
            "43",
            "--part",
            "a=18",
            "--part",
            "a=6.9",
            "--unit",
            "GiB",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, proc.stdout
    # Not the old output, which printed a table with 18 missing from it.
    assert "unattributed" not in proc.stdout
    assert "18 GiB" in proc.stdout


def test_the_smoke_counts_its_own_denominator(tmp_path):
    """It published `7 of 7` beside nine `check` calls.

    A hand-written denominator in a file about counts a reader cannot check is
    the subject of the file appearing inside it, so the assertion here is that
    the two numbers agree and not that either one is 7.
    """
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--smoke"], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stdout
    match = re.search(r"^smoke: (\d+) of (\d+) ok$", proc.stdout, re.M)
    assert match, proc.stdout
    passed, asked = int(match.group(1)), int(match.group(2))
    assert passed == asked
    # And the count is the real one: one per code, plus exo's two findings.
    source = (ROOT / "tools" / "sentinel.py").read_text()
    body = source.split("def smoke(")[1].split("\ndef ")[0]
    assert asked == len(re.findall(r"^\s+check\(", body, re.M))


def test_the_tool_refuses_to_be_asked_for_nothing(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(TOOL)], capture_output=True, text=True
    )
    assert proc.returncode == 2
    assert "give a file to read" in proc.stderr
