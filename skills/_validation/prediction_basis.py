#!/usr/bin/env python3
"""What each `without_skill` prediction is actually evidence of, counted.

ADR-38 rule 5 makes a task count toward the delta only if the bare subject fails
it, and this library decides that in advance by writing a `without_skill` field:
what the author expects an unaided subject to answer. The research seat audited
all 102 of them on 2026-11-02 and found the instrument sound in shape and
ungated in fact. The predictions name a specific rival artifact rather than
negating the grading criterion, which is the good news, and almost none of them
cite an observed run of the unaided arm, which is the whole of the bad news.

A prediction nobody has checked against a bare subject is the author's model of
the subject. That may well be right and it is not a measurement, and the only
way a reader can tell the difference is if the file says which it is. So every
task now carries `without_skill_basis`, with one of three `kind` values:

  observed-bare-run        an actual unaided run was observed, and the field
                           names which one
  this-repository-history  the reason given is something this repository
                           believed, measured or changed, rather than anything
                           about a subject model
  authored-judgement       the author's model of a bare subject. Never observed.

The third value is the admission, not a pass. It is the honest label for most of
this library and it is meant to look like what it is in the count below.

    python3 skills/_validation/prediction_basis.py            # the table
    python3 skills/_validation/prediction_basis.py --json
    python3 skills/_validation/prediction_basis.py --check     # exit 1 on a defect

`--check` fails on the two things a label can be wrong about rather than merely
weak: a task with no `without_skill_basis` at all, and a task claiming
`observed-bare-run` without naming the run it observed. It deliberately does not
fail on `authored-judgement`, because failing on it would make the honest label
the expensive one and this seat would start writing the other two.
"""
import argparse
import glob
import json
import pathlib
import sys

KINDS = ("observed-bare-run", "this-repository-history", "authored-judgement")


def suites(root):
    for path in sorted(glob.glob(str(pathlib.Path(root) / "*" / "evals" / "evals.json"))):
        yield pathlib.Path(path)


def audit(root):
    rows, problems = [], []
    for path in suites(root):
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = data.get("skill") or path.parts[-3]
        for task in data.get("tasks", []):
            tid = task.get("id", "?")
            basis = task.get("without_skill_basis")
            if not isinstance(basis, dict) or "kind" not in basis:
                problems.append(f"{slug}/{tid}: no `without_skill_basis`, so a reader "
                                "cannot tell a measurement from the author's expectation")
                continue
            kind = basis["kind"]
            if kind not in KINDS:
                problems.append(f"{slug}/{tid}: `without_skill_basis.kind` is {kind!r}, "
                                f"which is not one of {', '.join(KINDS)}")
                continue
            if kind == "observed-bare-run" and not basis.get("run"):
                problems.append(f"{slug}/{tid}: claims `observed-bare-run` and names no run")
                continue
            rows.append({"skill": slug, "task": tid, "kind": kind,
                         "detail": basis.get("run") or basis.get("note", "")})
    return rows, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows, problems = audit(args.skills_dir)
    counts = {k: sum(1 for r in rows if r["kind"] == k) for k in KINDS}
    total = len(rows) + len(problems)

    if args.json:
        print(json.dumps({"total": total, "counts": counts,
                          "problems": problems, "rows": rows}, indent=2))
        return 1 if (args.check and problems) else 0

    for kind in KINDS:
        print(f"{counts[kind]:>4} of {total} predictions: {kind}")
        for row in rows:
            if row["kind"] == kind and kind != "authored-judgement":
                print(f"       {row['skill']}/{row['task']}: {row['detail']}")
    print()
    print(f"{counts['observed-bare-run']} of {total} predictions have ever been checked "
          "against a run of the unaided arm. Every delta this library reports rests on "
          "the other " f"{total - counts['observed-bare-run']}.")
    for p in problems:
        print(f"failing: {p}")
    if problems:
        print(f"\n{len(problems)} predictions carry no usable basis label.")
        return 1 if args.check else 0
    print("\nEvery prediction says what it rests on. Exit 0 does not mean the "
          "predictions are right, only that none of them is pretending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
