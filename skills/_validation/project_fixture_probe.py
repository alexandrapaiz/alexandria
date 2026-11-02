#!/usr/bin/env python3
"""What a project task's own starter file scores against its own probes, measured.

ADR-38 rule 5 only counts a task if the bare subject fails it, and rule 6 prefers
a hard check to a judged one. A `project` task satisfies rule 6 by handing the
subject a starter file and a pytest suite. That form has a cost the library did
not measure until now: **a fixture cannot be written without naming its fields**,
so the starter file tells the subject which structures the graded answer uses.

The research seat's refutation pass of 2026-11-02
(`docs/research/notes/2026-11-02-prediction-refutation.md`) rejected `ac-t9` and
`ac-t10` on exactly that, and asked for a sweep of the remaining project tasks
against their own starter files. This instrument is the sweep, and it measures
rather than reads.

Ten of the library's twenty-two project tasks carry a `tests_pass` check with one
starter module and one pytest file. For each, this runs the starter file
unchanged as the answer and counts the probes it already passes. That number is
the task's floor: a subject that changes nothing scores it, so a prediction that
the bare arm does worse than the floor is arithmetically impossible.

    python3 skills/_validation/project_fixture_probe.py
    python3 skills/_validation/project_fixture_probe.py --json
    python3 skills/_validation/project_fixture_probe.py --check   # exit 1 on a defect

`--check` fails on a task whose declared `fixture_leak.stub_score` disagrees with
what the probe just measured. That is the point of the field: it turns "the
deny-list stub scores 1 of 4" from a sentence in a `pass_condition` nobody
re-runs into a number a gate re-derives. Both of the numbers the agent-containment
suite asserted in prose are correct, and they were correct by luck rather than by
check until this file existed.

**The finding this instrument was written to record, which is about the harness
and not about any task.** `tools/skill_eval.py:tests_pass` returns 1.0 on exit 0
and 0.0 otherwise. It is binary. So every row below whose floor is not a clean
sweep scores 0.0, and an answer that passes three of four probes is recorded
identically to one that passes one of four. Three `pass_condition` fields in this
library say the opposite in their own words -- "the harness reports the passing
count in both arms, so a partial improvement is visible" -- and that sentence is
false. `parses` tasks are the ones that get partial credit, because
`score_answer` means their assertion hits. The two forms are the opposite way
round from how the suites describe them.
"""
import argparse
import glob
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# The harness's own `python` shim, imported rather than reimplemented. The
# suites say `python -m pytest` and Debian ships `python3` only, so a probe that
# spelled this itself would drift from the thing it is meant to agree with.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from skill_eval import command_env                       # noqa: E402

# Counted from pytest's own summary line, each outcome read independently.
# A first draft required " passed" to be present and so could not count a
# fixture that passes nothing, which is three of the twelve rows below.
PYTEST_PASSED = re.compile(r"(\d+) passed")
PYTEST_FAILED = re.compile(r"(\d+) (?:failed|error)")
# pytest never got as far as a summary. The one case in this library is a
# starter file named for a standard-library module, which shadows it for the
# whole interpreter and breaks pytest's own imports before collection.
COLLECTION_DIED = re.compile(r"ImportError|INTERNALERROR|error during collection",
                             re.I)
TIMEOUT_S = 180


def project_tasks(root):
    """Every project task with a hard check, one starter module and one probe file."""
    for path in sorted(glob.glob(str(pathlib.Path(root) / "*" / "evals" / "evals.json"))):
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        slug = data.get("skill") or pathlib.Path(path).parts[-3]
        for task in data.get("tasks", []):
            if task.get("form") != "project":
                continue
            check = task.get("check") or {}
            if check.get("type") != "tests_pass":
                continue
            starters = [p for p in (task.get("files") or {}) if p.endswith(".py")]
            if len(starters) != 1:
                continue
            yield slug, task, starters[0], check


def counts(output):
    """`(passed, total)` from pytest's own summary line, or None if there is none."""
    best = None
    for line in output.splitlines():
        passed = PYTEST_PASSED.search(line)
        failed = PYTEST_FAILED.search(line)
        if passed or failed:
            p = int(passed.group(1)) if passed else 0
            f = int(failed.group(1)) if failed else 0
            if p or f:
                best = (p, p + f)
    return best


def measure(slug, task, starter, check):
    """Run the starter file unchanged as the answer, and count what it passes."""
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        for name, body in (task.get("files") or {}).items():
            (work / name).parent.mkdir(parents=True, exist_ok=True)
            (work / name).write_text(body, encoding="utf-8")
        for name, body in (check.get("files") or {}).items():
            (work / name).parent.mkdir(parents=True, exist_ok=True)
            (work / name).write_text(body, encoding="utf-8")
        shutil.copyfile(work / starter, work / check.get("answer_path", "answer.py"))
        try:
            proc = subprocess.run(check["command"], cwd=work, shell=True,
                                  capture_output=True, text=True,
                                  timeout=TIMEOUT_S, env=command_env())
        except subprocess.TimeoutExpired:
            return {"skill": slug, "task": task["id"], "starter": starter,
                    "outcome": "timed out", "passed": None, "of": None,
                    "harness_score": None, "declared": None}
        output = proc.stdout + proc.stderr
        got = counts(output)
        declared = ((task.get("fixture_leak") or {}).get("stub_score"))
        outcome = "ran"
        if got is None and COLLECTION_DIED.search(output):
            outcome = "pytest died before collecting a single probe"
        return {"skill": slug, "task": task["id"], "starter": starter,
                "outcome": outcome, "exit_code": proc.returncode,
                "passed": got[0] if got else None,
                "of": got[1] if got else None,
                # What `tools/skill_eval.py:tests_pass` would record for it.
                "harness_score": 1.0 if proc.returncode == 0 else 0.0,
                "declared": declared}


def problems(rows):
    out = []
    for r in rows:
        if r["passed"] is None:
            out.append(f"{r['skill']}/{r['task']}: {r['outcome']}, so this task "
                       f"scores 0.0 in BOTH arms whatever the subject writes, and "
                       f"the starter file `{r['starter']}` is why: it is named for "
                       f"a standard-library module and shadows it")
            continue
        d = r["declared"]
        if d is None:
            continue
        if (d.get("passed"), d.get("of")) != (r["passed"], r["of"]):
            out.append(
                f"{r['skill']}/{r['task']}: declares `fixture_leak.stub_score` "
                f"{d.get('passed')} of {d.get('of')} and the starter file just "
                f"scored {r['passed']} of {r['of']}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows = [measure(*t) for t in project_tasks(args.skills_dir)]
    bad = problems(rows)
    undeclared = [r for r in rows if r["declared"] is None]
    collapsed = [r for r in rows
                 if r["passed"] is not None and r["passed"] != r["of"]]

    if args.json:
        print(json.dumps({"rows": rows, "problems": bad,
                          "undeclared": [r["task"] for r in undeclared],
                          "collapsed_to_zero": [r["task"] for r in collapsed]},
                         indent=2))
        return 1 if (args.check and bad) else 0

    print(f"{len(rows)} project tasks with a hard check, one starter module and "
          "one probe file.\nEach starter file run unchanged as its own answer:\n")
    width = max((len(f"{r['skill']}/{r['task']}") for r in rows), default=10)
    print("  {}  {:>8}  {:>13}  {}".format("task".ljust(width), "floor",
                                           "harness score", "declared"))
    for r in rows:
        label = f"{r['skill']}/{r['task']}".ljust(width)
        floor = "-" if r["passed"] is None else f"{r['passed']} of {r['of']}"
        d = r["declared"]
        decl = "-" if d is None else f"{d.get('passed')} of {d.get('of')}"
        print(f"  {label}  {floor:>8}  {str(r['harness_score']):>13}  {decl}")

    print(f"\n{len(collapsed)} of these {len(rows)} tasks have a floor short of a "
          "clean sweep, and\nevery one of them is scored 0.0 by "
          "`tests_pass`, which is binary. A subject that\nfixes most of a fixture "
          "and a subject that changes nothing are the same number\nto this "
          "harness, so none of these rows can show the partial improvement its\n"
          "own prediction implies.")
    print(f"\n{len(undeclared)} of {len(rows)} declare no `fixture_leak`, so what "
          "their starter file hands the\nsubject is unrecorded. That is the "
          "backlog this instrument exists to shrink, and\nit is reported rather "
          "than failed: a gate that failed here would fail on work\nnobody has "
          "done yet, which is how a register stops being read.")
    for p in bad:
        print(f"\nfailing: {p}")
    if bad:
        print(f"\n{len(bad)} of these rows cannot be read as written: either a "
              "declared stub score\ndisagrees with the measurement, or the probe "
              "never ran at all.")
        return 1 if args.check else 0
    print("\nEvery declared stub score matches what the starter file just scored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
