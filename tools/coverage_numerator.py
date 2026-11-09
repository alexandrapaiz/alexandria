#!/usr/bin/env python3
"""The covered count, over history, because it is the number that never moves.

`tools/ci_coverage.py` answers how many test files CI runs *today*. Two
seats measured it four hours apart on 2026-11-09 and the readings were
`14 of 100` and `14 of 107`: the suite gained seven files and the covered
count did not move at all. The `alexandria/skill` seat put the
consequence in one sentence — **the gate is not falling behind, it is
pinned** — and the arithmetic does the rest. Every file added to `tests/`
makes the ratio worse by construction, with nobody neglecting anything.

Two readings are an anecdote. This module makes it a series.

It samples one commit per day from a ref's history, materialises just
`tests/` and `.github/workflows/` at each, and asks
`ci_coverage.coverage()` the same question it asks about the working
tree. The output is the numerator and the denominator side by side, day
by day, so "pinned" is a column a reader can check rather than a claim
to take.

    python3 tools/coverage_numerator.py                   # the series, as a gate
    python3 tools/coverage_numerator.py --report-only     # no verdict
    python3 tools/coverage_numerator.py --json
    python3 tools/coverage_numerator.py --since 2026-11-01

**It is an inverted gate, and the thing it waits for is a transition.**
It exits non-zero while the covered count has not risen *recently* —
`--stale-days`, 7 by default — and goes green the first time somebody
widens what CI runs.

Recency and not "ever", because the first draft of this gate read green
on its own first run. Over `--since 2026-10-01` the numerator does rise
exactly once, 13 to 14 on 2026-10-04, and a gate that asks "did it ever
move" is satisfied by that step forever. The step is the finding, not the
reassurance: **the covered count has been 14 every day since
2026-10-04**, while the denominator went 27 to 107. So the verdict is
about the age of the last rise, which keeps the whole series readable in
one pass without letting its oldest row vouch for today.

There is one known command that would move it, it has been parked for
thirty-three days, and no seat may run it because a seat's token has no
`workflows` permission:

    git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml

So a red exit here is not a defect to repair in this repository. It is a
routed ask that has not landed, kept in a form that will notice when it
does. `.github/workflows-pending/README.md` carries the argument;
`python3 tools/ci_coverage.py --only .github/workflows-pending/checks.yml`
is the one-line proof that the parked file covers the whole suite.

Why the numerator rather than the ratio. A ratio moves when either term
moves, so a worsening ratio is ambiguous between a gate falling behind
and a suite growing, and those have different owners. The numerator is a
statement about one thing only: whether anybody has widened what CI
runs. Thirty-three days of a constant numerator is a fact about the
parked file; a worsening ratio over the same window is a fact about how
productive the seats were.

Why one commit a day rather than every commit. Three and a half thousand
commits reached `main` in the window and the measurement costs a `git
archive` each. The numerator is a step function that changes when a
workflow file changes, and a daily sample cannot miss a step that lasted
longer than a day. `--every` takes it finer where that matters.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ci_coverage  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The two trees the measurement reads. Archiving the whole repository at
# every sampled commit is the obvious implementation and it is thirty
# times the bytes for the same answer, because `coverage()` opens exactly
# these two directories.
TREES = ("tests", ".github/workflows")


# Every function below resolves its repository at call time rather than
# binding `REPO` as a default argument. A default is evaluated once, at
# import, so a test that points the module at a fixture repository would
# be silently ignored and would measure this repository instead — which
# is a test that passes by reading the thing it was written to not read.
def _at(cwd: str | None) -> str:
    return cwd if cwd is not None else REPO


def git(*args: str, cwd: str | None = None) -> str:
    """One git command's stdout, stripped. Raises on a non-zero exit."""
    out = subprocess.run(
        ("git",) + args, cwd=_at(cwd), capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def samples(ref: str, since: str, every: str, cwd: str | None = None) -> list[tuple[str, str]]:
    """One (date, sha) per period in `ref`'s history, oldest first.

    The sample taken for a period is its **last** commit, which is the
    state of the tree at the end of that day rather than at the start of
    it. A reader asking "what did CI run on the 7th" means the 7th as it
    was left.
    """
    fmt = {"day": "%ad", "hour": "%ad"}[every]
    date_fmt = {"day": "short", "hour": "format:%Y-%m-%dT%H"}[every]
    lines = git(
        "log",
        ref,
        f"--since={since}",
        f"--date={date_fmt}",
        f"--format={fmt} %H",
        cwd=cwd,
    ).splitlines()
    # `git log` is newest first, so the first row seen for a period is
    # that period's last commit.
    seen: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        period, sha = line.split(" ", 1)
        seen.setdefault(period, sha.strip())
    return sorted(seen.items())


def measure_at(sha: str, cwd: str | None = None) -> dict:
    """`ci_coverage.coverage()` against one commit's tree.

    Returns the covered and total counts, plus the workflow files that
    existed then, so a step in the series can be attributed to a file
    rather than only to a date.
    """
    with tempfile.TemporaryDirectory() as tmp:
        present = []
        for tree in TREES:
            # A tree can be absent from an old commit, and `git archive`
            # exits non-zero on a path that does not match. That is a
            # measurement of nothing rather than an error.
            try:
                git("cat-file", "-e", f"{sha}:{tree}", cwd=cwd)
            except subprocess.CalledProcessError:
                continue
            present.append(tree)
        if "tests" not in present:
            return {"covered": 0, "total": 0, "workflows": []}
        archive = subprocess.run(
            ("git", "archive", sha) + tuple(present),
            cwd=_at(cwd),
            capture_output=True,
            check=True,
        )
        subprocess.run(("tar", "-x", "-C", tmp), input=archive.stdout, check=True)
        report = ci_coverage.coverage(root=tmp)
        return {
            "covered": len(report["covered"]),
            "total": report["total"],
            "workflows": report["workflows"],
        }


def series(ref: str, since: str, every: str, cwd: str | None = None) -> list[dict]:
    """The measurement at every sampled commit, oldest first."""
    rows = []
    for period, sha in samples(ref, since, every, cwd):
        row = {"period": period, "commit": sha[:8]}
        row.update(measure_at(sha, cwd))
        rows.append(row)
    return rows


def risen(rows: list[dict]) -> list[tuple[dict, dict]]:
    """Every adjacent pair where the covered count went up.

    Up and not merely different: a numerator that falls is a separate
    finding and this gate is not it. Only rows with a non-zero total
    count, because a commit with no `tests/` measures nothing and a step
    out of it is an artefact of the window's left edge.
    """
    real = [r for r in rows if r["total"]]
    return [
        (a, b)
        for a, b in zip(real, real[1:])
        if b["covered"] > a["covered"]
    ]


def stale_by(rows: list[dict], steps: list[tuple[dict, dict]]) -> tuple[str | None, int]:
    """The period of the last rise, and how many samples have passed since.

    Counted in samples rather than in calendar days on purpose: the days
    with no commit are days nothing could have moved the numerator, and
    charging them to the staleness would make a quiet weekend read like
    neglect. The caller converts.
    """
    real = [r for r in rows if r["total"]]
    if not steps:
        return None, len(real)
    last = steps[-1][1]
    index = next(i for i, r in enumerate(real) if r["commit"] == last["commit"])
    return last["period"], len(real) - 1 - index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="origin/main", help="default: %(default)s")
    parser.add_argument("--since", default="2026-10-01", help="default: %(default)s")
    parser.add_argument(
        "--every",
        default="day",
        choices=("day", "hour"),
        help="sampling period (default: %(default)s)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=7,
        metavar="N",
        help="fail when the last rise is more than N samples old (default: %(default)s)",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="print the series and exit 0 even when the numerator is stale",
    )
    args = parser.parse_args(argv)

    rows = series(args.ref, args.since, args.every)
    steps = risen(rows)
    when, stale = stale_by(rows, steps)
    if args.json:
        print(
            json.dumps(
                {
                    "series": rows,
                    "risen": steps,
                    "last_rise": when,
                    "samples_since_rise": stale,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if not rows:
        print(f"no commits on {args.ref} since {args.since}")
        return 0

    print(f"the covered count on {args.ref}, one sample per {args.every}:\n")
    print(f"  {'period':<19}  {'commit':<9}  {'ran':>4}  {'of':>4}   share")
    previous = None
    for row in rows:
        total = row["total"]
        share = f"{row['covered'] / total:5.0%}" if total else "    -"
        mark = ""
        if previous is not None and row["covered"] != previous:
            mark = "  <- moved"
        print(
            f"  {row['period']:<19}  {row['commit']:<9}  "
            f"{row['covered']:>4}  {total:>4}   {share}{mark}"
        )
        previous = row["covered"]

    real = [r for r in rows if r["total"]]
    if real:
        first, last = real[0], real[-1]
        print(
            f"\n  denominator: {first['total']} -> {last['total']} "
            f"({last['total'] - first['total']:+d}) over {len(real)} samples"
        )
        print(
            f"  numerator:   {first['covered']} -> {last['covered']} "
            f"({last['covered'] - first['covered']:+d})"
        )

    for before, after in steps:
        print(
            f"\n  the covered count rose at {after['period']} "
            f"({after['commit']}): {before['covered']} -> {after['covered']}"
        )
    if when is None:
        print(f"\n  the covered count never rose in these {stale} samples")
    else:
        print(f"  and not since: {stale} samples with no rise, the last at {when}")

    if stale <= args.stale_days:
        print(
            f"\nPASS: the covered count rose within the last {args.stale_days} "
            "samples."
        )
        return 0
    if args.report_only:
        return 0
    print(
        f"\nFAIL: the covered count has not risen in {stale} samples. Every file\n"
        "      added to tests/ since has made the ratio worse and nothing has\n"
        "      widened CI. The known remedy is one command and no seat may run\n"
        "      it, because a seat's token has no `workflows` permission:\n"
        "      git mv -f .github/workflows-pending/checks.yml "
        ".github/workflows/checks.yml\n"
        "      Pass --report-only for the series without the verdict."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
