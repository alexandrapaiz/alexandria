#!/usr/bin/env python3
"""The numerator gauge, and the two directions it has to get right.

`tools/coverage_numerator.py` exists because two readings of
`tools/ci_coverage.py` four hours apart on 2026-11-09 were `14 of 100`
and `14 of 107`. The suite grew by seven files and the covered count did
not move. The gauge turns that pair into a series over history so that
"pinned" is checkable.

It is an inverted gate: red while the covered count is stale, green the
day somebody widens CI. **So the direction that matters here is the
green one**, and it is the one no live reading can exercise, because the
repository has been red every day the tool can measure. A gauge that is
hard-wired to say "stale" passes every live check for as long as the
defect lasts and is wrong on the single day somebody acts on it. That is
the same shape as `tests/test_answered_by.py`, for the same reason, and
it is why the fixtures below build repositories whose numerator rises.

The second thing under test is the staleness arithmetic. The gate's own
first draft asked "did the covered count ever rise" and read **green**
on its first real run, satisfied forever by one step on 2026-10-04. The
cases below pin the recency reading so that a step cannot vouch for a
window it is not in.

Nothing here touches the network, the real history, or the working
tree's git state: every case builds its own repository in `tmp_path`.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))

import coverage_numerator as cn  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUITE_STEP = """\
name: checks
on: [pull_request]
jobs:
  t:
    runs-on: ubuntu-latest
    steps:
      - run: python3 -m pytest tests/ -q
"""


def one_step(*files: str) -> str:
    """A workflow that runs exactly the named test files and nothing else."""
    named = " ".join(files)
    return (
        "name: checks\non: [pull_request]\njobs:\n  t:\n"
        "    runs-on: ubuntu-latest\n    steps:\n"
        f"      - run: python3 -m pytest {named} -q\n"
    )


def build(root, days):
    """A git repository with one commit per entry of `days`.

    Each entry is `(date, {path: text})`, applied cumulatively, so a day
    that names no workflow leaves the previous day's workflow standing.
    That is how the real repository behaves and it is the behaviour the
    step function depends on.
    """
    env = dict(
        os.environ,
        GIT_AUTHOR_NAME="t",
        GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t",
        GIT_COMMITTER_EMAIL="t@t",
    )
    subprocess.run(("git", "init", "-q", "-b", "main", str(root)), check=True, env=env)
    for date, files in days:
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        stamp = f"{date}T12:00:00+00:00"
        subprocess.run(
            ("git", "add", "-A"),
            cwd=str(root),
            check=True,
            env=env,
        )
        subprocess.run(
            ("git", "commit", "-q", "-m", date),
            cwd=str(root),
            check=True,
            env=dict(env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp),
        )
    return str(root)


# ------------------------------------------------------- the sampling

def test_a_day_is_sampled_at_its_last_commit(tmp_path):
    """The state of the tree at the end of the day, not the start of it.

    A reader asking what CI ran on the 7th means the 7th as it was left.
    Taking the first commit of a day would attribute a widening to the
    day after the one that shipped it.
    """
    root = build(
        tmp_path / "r",
        [
            ("2026-10-01", {"tests/test_a.py": "", ".github/workflows/c.yml": one_step("tests/test_a.py")}),
            ("2026-10-02", {"tests/test_b.py": ""}),
        ],
    )
    # A second commit on the same day, widening the workflow.
    (tmp_path / "r" / ".github" / "workflows" / "c.yml").write_text(SUITE_STEP, encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_AUTHOR_DATE="2026-10-02T23:00:00+00:00",
               GIT_COMMITTER_DATE="2026-10-02T23:00:00+00:00")
    subprocess.run(("git", "add", "-A"), cwd=root, check=True, env=env)
    subprocess.run(("git", "commit", "-q", "-m", "late"), cwd=root, check=True, env=env)

    rows = cn.series("main", "2026-09-01", "day", cwd=root)
    assert [r["period"] for r in rows] == ["2026-10-01", "2026-10-02"]
    # The late commit is the one measured, so the 2nd reads 2 of 2.
    assert (rows[-1]["covered"], rows[-1]["total"]) == (2, 2)


def test_a_commit_with_no_tests_directory_measures_nothing(tmp_path):
    """Zero of zero, and not an exception.

    `git archive` exits non-zero on a path that does not match, which is
    a plausible repository state at the left edge of a window rather
    than an error.
    """
    root = build(tmp_path / "r", [("2026-10-01", {"README.md": "hi"})])
    rows = cn.series("main", "2026-09-01", "day", cwd=root)
    assert (rows[0]["covered"], rows[0]["total"]) == (0, 0)


# ------------------------------------------------------- the verdict

def test_a_rise_is_found_and_a_fall_is_not(tmp_path):
    """Only upward steps. A numerator that falls is a different finding.

    Read as "changed" rather than "rose", a workflow deletion would
    satisfy this gate, which is the one outcome it must never call
    progress.
    """
    rose = [{"period": "a", "commit": "1", "covered": 1, "total": 9},
            {"period": "b", "commit": "2", "covered": 4, "total": 9}]
    fell = [{"period": "a", "commit": "1", "covered": 4, "total": 9},
            {"period": "b", "commit": "2", "covered": 1, "total": 9}]
    assert len(cn.risen(rose)) == 1
    assert cn.risen(fell) == []


def test_an_empty_sample_cannot_manufacture_a_step(tmp_path):
    """A 0-of-0 row at the window's edge is skipped, not stepped out of.

    Without this, every window whose first sample predates `tests/`
    reports a rise from zero and the gate reads green on the oldest
    possible question.
    """
    rows = [{"period": "a", "commit": "1", "covered": 0, "total": 0},
            {"period": "b", "commit": "2", "covered": 14, "total": 107},
            {"period": "c", "commit": "3", "covered": 14, "total": 107}]
    assert cn.risen(rows) == []


def test_staleness_counts_samples_since_the_last_rise(tmp_path):
    """And the last rise, not the first.

    The live series rises once, on 2026-10-04, and had this counted from
    the first step in the window a later widening would read as stale.
    """
    rows = [{"period": "d1", "commit": "1", "covered": 1, "total": 9},
            {"period": "d2", "commit": "2", "covered": 2, "total": 9},
            {"period": "d3", "commit": "3", "covered": 3, "total": 9},
            {"period": "d4", "commit": "4", "covered": 3, "total": 9}]
    when, stale = cn.stale_by(rows, cn.risen(rows))
    assert (when, stale) == ("d3", 1)


def test_a_numerator_that_never_rose_is_stale_by_the_whole_window(tmp_path):
    rows = [{"period": "d1", "commit": "1", "covered": 14, "total": 90},
            {"period": "d2", "commit": "2", "covered": 14, "total": 107}]
    assert cn.stale_by(rows, []) == (None, 2)


# ------------------------------------------------------- end to end

def test_a_pinned_numerator_is_red_and_report_only_is_not(tmp_path, capsys, monkeypatch):
    """The live state, reproduced in a fixture: denominator grows, numerator does not."""
    root = build(
        tmp_path / "r",
        [
            ("2026-10-01", {"tests/test_a.py": "", ".github/workflows/c.yml": one_step("tests/test_a.py")}),
            ("2026-10-02", {"tests/test_b.py": ""}),
            ("2026-10-03", {"tests/test_c.py": ""}),
        ],
    )
    monkeypatch.setattr(cn, "REPO", root)
    assert cn.main(["--ref", "main", "--since", "2026-09-01", "--stale-days", "1"]) == 1
    out = capsys.readouterr().out
    # Three samples, no rise in any of them. Counted as three and not as
    # two transitions on purpose: a one-sample window would otherwise
    # report zero staleness and read green on no evidence at all.
    assert "has not risen in 3 samples" in out
    assert "workflows-pending/checks.yml" in out, "the red verdict names the remedy"
    assert cn.main(
        ["--ref", "main", "--since", "2026-09-01", "--stale-days", "1", "--report-only"]
    ) == 0


def test_a_widening_turns_it_green(tmp_path, monkeypatch, capsys):
    """The transition, which no live reading of this repository can exercise.

    This is the case the gate is for. Three files, a workflow that runs
    one of them, and then a day on which the workflow runs the suite.
    """
    root = build(
        tmp_path / "r",
        [
            ("2026-10-01", {"tests/test_a.py": "", ".github/workflows/c.yml": one_step("tests/test_a.py")}),
            ("2026-10-02", {"tests/test_b.py": "", "tests/test_c.py": ""}),
            ("2026-10-03", {".github/workflows/c.yml": SUITE_STEP}),
        ],
    )
    monkeypatch.setattr(cn, "REPO", root)
    assert cn.main(["--ref", "main", "--since", "2026-09-01", "--stale-days", "1"]) == 0
    out = capsys.readouterr().out
    assert "rose at 2026-10-03" in out
    assert "1 -> 3" in out
    assert "PASS" in out


def test_json_carries_the_series_and_the_staleness(tmp_path, monkeypatch, capsys):
    import json

    root = build(
        tmp_path / "r",
        [("2026-10-01", {"tests/test_a.py": "", ".github/workflows/c.yml": one_step("tests/test_a.py")})],
    )
    monkeypatch.setattr(cn, "REPO", root)
    assert cn.main(["--ref", "main", "--since", "2026-09-01", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["series"][0]["covered"] == 1
    assert payload["last_rise"] is None
    assert payload["samples_since_rise"] == 1


def test_an_empty_window_is_not_a_failure(tmp_path, monkeypatch, capsys):
    """A window with no commits says so and exits 0.

    A gate that fails on an unanswerable question teaches a reader to
    pass `--report-only` permanently.
    """
    root = build(tmp_path / "r", [("2026-10-01", {"tests/test_a.py": ""})])
    monkeypatch.setattr(cn, "REPO", root)
    assert cn.main(["--ref", "main", "--since", "2026-11-01"]) == 0
    assert "no commits" in capsys.readouterr().out


# ------------------------------------------------- the docstring's claims

def test_the_remedy_the_verdict_names_is_a_file_that_exists():
    """The red verdict prints one command. It has to be runnable.

    A gate that routes a remedy by name is only as good as the name. The
    parked file has been moved once already in this repository's history
    (`checks.yml`, 2026-09-29), so the path in that sentence is exactly
    the kind of thing that goes stale without a reader noticing.
    """
    parked = os.path.join(REPO, ".github", "workflows-pending", "checks.yml")
    assert os.path.exists(parked), "the verdict names a parked file that is gone"
    import ci_coverage

    report = ci_coverage.coverage(only=[".github/workflows-pending/checks.yml"])
    assert not report["uncovered"], (
        "the parked file no longer covers the whole suite, so the remedy the "
        "red verdict names would not turn this gauge green"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
