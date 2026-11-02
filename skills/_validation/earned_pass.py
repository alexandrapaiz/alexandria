#!/usr/bin/env python3
"""The denominator gate: no instrument here may report a pass it did not earn.

The engineer seat named the hole on 2026-11-02 (board note `4179c3ef`), from two
defects in its own code the same day. One read the exit code of a new send gate
through a pipe into `tail` and got zero. The other was a tool whose whole job is
reporting a verdict, and its first live run printed "the suites pass against it"
for a run in which no suite had executed. Its sentence for what neither seat had:

    "A test that enumerates add_argument is a census of the surface. What
    neither of us has is a test that a reported pass was earned."

This file is that test, for this seat's instruments, and it is a probe rather
than a census: it constructs the case that should break each gate and runs it.

The defect has one shape. Every `--check` here ends in `return 1 if problems
else 0`, and an empty input has no problems, so a gate handed nothing prints its
pass sentence over a denominator of zero and exits green. `trigger_test.py`
already carries the fix for the neighbouring case, `SkippedGate`, for a gate that
did not run because PyYAML was missing. A gate that ran over an empty set is the
same lie with better manners, and nothing caught it.

Measured before the fix, 2026-11-02, five instances in four instruments:

    trigger_test.py --receipts  empty skills dir   "all 0 receipts describe
                                                   today's text"            exit 0
    trigger_test.py --receipts  empty skills dir   "all 0 skills load under
                                                   a YAML parser"           exit 0
    claim_receipt.py --check    0 eval tasks       "No eval task names a
                                                   heading its skill no
                                                   longer carries."         exit 0
    claim_receipt.py --check    a planted stale    nothing: --json returns
      --json                    section ref        before the check runs     exit 0
    prediction_basis.py --check 0 predictions      "Every prediction says
                                                   what it rests on."       exit 0
    project_fixture_probe.py    0 project tasks    "Every declared stub
      --check                                      score matches ..."       exit 0

The fourth is the engineer's own defect exactly: a verdict discarded by how the
tool was invoked rather than by what it found.

One helper and one sentence, not four correct refusals, because four cannot be
kept from drifting apart. That reason is the engineer's, given back about four
skills sharing one refusal line.

    python3 skills/_validation/earned_pass.py --probe   # the test. exit 1 on a lie
    python3 skills/_validation/earned_pass.py --list    # the registered gates
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REFUSAL = (
    "{gate}: FAIL, nothing was measured. 0 of 0 {unit} were checked, so there is "
    "no pass to report here. A gate that found nothing to check has not been "
    "cleared, it has been skipped, and those two are the same exit code unless "
    "somebody writes this sentence."
)

# Exit 2 rather than 1, because an empty input is a data error and not a failed
# case, and `trigger_test.py`'s own docstring already reserves 2 for exactly
# that. A caller that only tests for non-zero is unaffected either way.
NOTHING_MEASURED = 2


def verdict(gate: str, *, checked: int, unit: str, failures: int,
            pass_line: str, fail_line: str = "") -> int:
    """The one place an instrument here is allowed to say it passed.

    `checked` is the denominator: how many things this run actually examined.
    Zero is refused, loudly, before `failures` is consulted at all, because
    zero failures out of zero is the sentence this file exists to stop.
    """
    if checked == 0:
        print("\n" + REFUSAL.format(gate=gate, unit=unit))
        return NOTHING_MEASURED
    if failures:
        if fail_line:
            print("\n" + fail_line)
        return 1
    print("\n" + pass_line)
    return 0


# Each gate: the command, and the edit to a copied tree that empties the input
# it reads. `expect` is what the probe demands: a non-zero exit and the refusal
# sentence, or for `json_shortcircuit`, agreement with the same gate's plain run.
GATES = [
    {
        "name": "trigger_test.py --receipts",
        "argv": ["skills/_validation/trigger_test.py", "--receipts",
                 "--skills-dir", "{empty_dir}"],
        "empty": "none",
        "unit": "skills",
    },
    {
        "name": "claim_receipt.py --check",
        "argv": ["skills/_validation/claim_receipt.py", "--check"],
        "empty": "eval_tasks",
        "unit": "section references",
    },
    {
        "name": "claim_receipt.py --check --json",
        "argv": ["skills/_validation/claim_receipt.py", "--check", "--json"],
        "empty": "stale_section_ref",
        "unit": "section references",
        "expect": "nonzero_on_planted_defect",
    },
    {
        "name": "prediction_basis.py --check",
        "argv": ["skills/_validation/prediction_basis.py", "--check"],
        "empty": "eval_tasks",
        "unit": "predictions",
    },
    {
        "name": "project_fixture_probe.py --check",
        "argv": ["skills/_validation/project_fixture_probe.py", "--check"],
        "empty": "eval_tasks",
        "unit": "project tasks",
    },
]


def _empty_eval_tasks(tree: pathlib.Path) -> None:
    for path in sorted(tree.glob("skills/*/evals/evals.json")):
        spec = json.loads(path.read_text())
        spec["tasks"] = []
        if "retired_tasks" in spec:
            spec["retired_tasks"] = []
        path.write_text(json.dumps(spec, indent=2) + "\n")


def _plant_stale_section_ref(tree: pathlib.Path) -> None:
    """Not an empty input: a real defect that plain `--check` catches. The
    probe then asks whether adding `--json` loses the verdict."""
    for path in sorted(tree.glob("skills/*/evals/evals.json")):
        spec = json.loads(path.read_text())
        for task in spec.get("tasks") or []:
            if task.get("sections"):
                task["sections"] = ["A heading no skill in this library carries"]
                path.write_text(json.dumps(spec, indent=2) + "\n")
                return
    raise SystemExit("probe: no eval task carries a `sections` list to plant on")


EMPTIERS = {
    "none": lambda tree: None,
    "eval_tasks": _empty_eval_tasks,
    "stale_section_ref": _plant_stale_section_ref,
}


# `project_fixture_probe.py` imports `command_env` from `tools/skill_eval.py`, so a
# tree of `skills/` alone makes it die on an ImportError. That exit is non-zero
# and it is not a refusal, which would have let the probe pass this gate for the
# wrong reason. Copy what the instruments actually read.
PROBE_TREE = ("skills", "tools")


def _run(tree: pathlib.Path, argv: list[str], empty_dir: pathlib.Path):
    cmd = [sys.executable] + [a.format(empty_dir=empty_dir) for a in argv]
    proc = subprocess.run(cmd, cwd=tree, capture_output=True, text=True,
                          timeout=900)
    return proc.returncode, proc.stdout + proc.stderr


def probe(repo: pathlib.Path) -> int:
    rows = []
    with tempfile.TemporaryDirectory(prefix="earned-pass-") as tmp:
        base = pathlib.Path(tmp)
        empty_dir = base / "no-skills"
        empty_dir.mkdir()
        # One tree per treatment rather than per gate. The gates only read, and
        # the company host runs twelve seats on one `/tmp` that was at 99 percent
        # while this was written, so five copies of a tree three of them share is
        # a cost with nothing bought by it.
        trees: dict[str, pathlib.Path] = {}
        for gate in GATES:
            treatment = gate["empty"]
            if treatment not in trees:
                tree = base / treatment
                for top in PROBE_TREE:
                    shutil.copytree(repo / top, tree / top)
                EMPTIERS[treatment](tree)
                trees[treatment] = tree
            code, out = _run(trees[treatment], gate["argv"], empty_dir)
            if gate.get("expect") == "nonzero_on_planted_defect":
                plain = [a for a in gate["argv"] if a != "--json"]
                ref_code, _ = _run(trees[treatment], plain, empty_dir)
                earned = code != 0 if ref_code != 0 else True
                why = (f"plain run exits {ref_code} on the planted defect, "
                       f"this invocation exits {code}")
            else:
                refused = "nothing was measured" in out
                crashed = "Traceback (most recent call last)" in out
                earned = code != 0 and refused
                why = (f"exit {code}, refusal sentence "
                       f"{'present' if refused else 'absent'}"
                       f"{', and it crashed rather than refusing' if crashed else ''}")
            rows.append({"gate": gate["name"], "earned": earned, "why": why,
                         "exit": code})

    width = max(len(r["gate"]) for r in rows)
    print("earned-pass probe: does each gate refuse to report a pass it did "
          "not earn?\n")
    for r in rows:
        mark = "ok     " if r["earned"] else "UNEARNED"
        print(f"  {mark} {r['gate']:<{width}}  {r['why']}")
    bad = [r for r in rows if not r["earned"]]
    if bad:
        print(f"\n{len(bad)} of {len(rows)} gates report a pass over an input "
              "they never examined. Route the verdict through "
              "`earned_pass.verdict` and give it the denominator.")
        return 1
    print(f"\nAll {len(rows)} gates refuse. A pass from any of them was earned "
          "on a denominator above zero.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--probe", action="store_true",
                    help="run every registered gate against an input it cannot "
                         "pass honestly; exit 1 if any reports a pass")
    ap.add_argument("--list", action="store_true",
                    help="print the registered gates and what the probe empties")
    args = ap.parse_args()
    repo = pathlib.Path(__file__).resolve().parents[2]
    if args.list:
        for gate in GATES:
            print(f"  {gate['name']:<34} empties {gate['empty']:<18} "
                  f"unit: {gate['unit']}")
        return 0
    if args.probe:
        return probe(repo)
    print(__doc__)
    print(f"registered gates: {len(GATES)}. Run --probe to test them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
