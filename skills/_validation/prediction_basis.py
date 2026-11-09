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
  refuted-and-survived     an authored judgement that was put through a written
                           refutation pass and survived it, naming the pass
  measured-floor           part of the prediction is measured, and the measured
                           part is a floor rather than a bare run: the fixture
                           shipped in the task's own files was run unchanged and
                           its score bounds the task from below

The third value is the admission, not a pass. It is the honest label for most of
this library and it is meant to look like what it is in the count below.

The fourth value exists because the research seat's costed estimate of
2026-11-02 (`docs/research/notes/2026-11-02-independence-costed-estimate.md`)
narrowed this instrument's blocker. Skill-Use's own exclusivity check is not an
observed bare run either; it is a model's counterfactual judgement in exactly
the shape of the `authored-judgement` rows here. What makes that admissible is
three separable safeguards, and only the first of them needs a credential this
seat does not have: cross-family review, a red-team refutation pass on named
axes, and a ten percent human spot-check. So a judgement that survived
refutation is a different and better thing than one that was merely labelled,
and it is reachable today with no key at all. `refuted-and-survived` is where
that work gets recorded when it is done. Nothing carries it yet, and the count
below says so rather than hiding it.

    python3 skills/_validation/prediction_basis.py            # the table
    python3 skills/_validation/prediction_basis.py --json
    python3 skills/_validation/prediction_basis.py --check     # exit 1 on a defect

## The hole this file had until 2026-11-02, and what closes it

The research seat ran the refutation pass on five rows on 2026-11-02 and **none
of the five survived**: two rejects and three revises. There was nowhere to
record that. The five would have sat at `authored-judgement`, indistinguishable
from the rows nobody has read, so running the pass and not recording it lost the
result -- which was that seat's first finding, and it outranked all five
verdicts.

So a `refutation` field now hangs off any basis, carrying the pass, the verdict,
the axes it landed on and what was amended. It is deliberately **not** a fifth
kind. A row that was refuted and then repaired is still an authored judgement,
because the repair is another authored judgement, and promoting it on the
strength of having been criticised would be the opposite of what the pass found.
`refuted-and-survived` stays reserved for a verdict of `survived`, and the gate
below refuses the label to anything else.

`--check` fails on the things a label can be wrong about rather than merely
weak: a task with no `without_skill_basis` at all, a task claiming
`observed-bare-run` without naming the run it observed, a task claiming
`refuted-and-survived` without naming the refutation or while its own
refutation records a verdict other than `survived`, a task claiming
`measured-floor` with no measured floor beside it, and a malformed
`refutation`. It deliberately does not
fail on `authored-judgement`, because failing on it would make the honest label
the expensive one and this seat would start writing the other two.

**And that deliberate silence is where the one error this scheme cannot see
lives.** On 2026-11-02 the research seat showed that the four rows labelled
something other than `authored-judgement` were exactly the four whose reason
contains a date, so the criterion applied in practice was "has a date" rather
than "is a fact about this repository". The two the seats nearly lost between
them, `he-t9` and `ams-t4`, are the two with no date in them, and one of them
turned out to be a real repository fact. Since the gate does not fail on
`authored-judgement`, a repository fact mislabelled as authored judgement is
invisible to it by design. So the report below prints the dateless candidates a
deliberately wide repository-shape net catches, beside their labels, which is
the five cases where the two criteria come apart. The gate cannot adjudicate
them, because the referent of "the graph" or "this library" is fixed by each
task's own prompt and only a reader can see that. Printing them is what makes a
hand relabelling possible at all.
"""
import argparse
import contextlib
import glob
import json
import os
import pathlib
import re
import sys

# The named refusal lives in trigger_test so all four instruments in this
# directory print the same sentence for the same mistake (engineer seat's
# unresolved-flag class, 2026-11-02).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trigger_test as tt                                # noqa: E402
from earned_pass import verdict                          # noqa: E402

KINDS = ("observed-bare-run", "this-repository-history", "authored-judgement",
         "refuted-and-survived", "measured-floor")

# The verdicts a refutation pass can return. `survived` is the only one that
# earns the `refuted-and-survived` kind, and the gate below enforces that rather
# than trusting the label.
VERDICTS = ("reject", "revise", "survived")

# A deliberately wide net for text that reasons from this repository rather than
# about a subject model. Over-matching is the right error: a candidate that
# reaches the hand-review list below costs one line of reading, and a candidate
# that never reaches it is the defect this report exists to surface. The net is
# the research seat's, from `docs/research/notes/2026-11-02-prediction-basis.py`,
# and is one way to do it rather than the only one.
REPOSITORY_SHAPE = re.compile("|".join([
    r"\bour\b", r"\bours\b", r"\bwe\b",
    r"\bthis (skill|suite|librar|seat|repositor|corpus|estate|org|file|shelf"
    r"|delta|paper|very paper)",
    r"\bthe (graph|suite|librar|seat|corpus|estate|probes?|ledger|register)\b",
    r"20\d\d-\d\d-\d\d", r"\buntil (today|20)", r"\bdeprecat",
    r"\bprovenance\b", r"\balexandria\b", r"\bsince\b",
    r"\bitself asserted\b", r"\bA/B\b",
]), re.I)

# The criterion that was actually being applied, made explicit so the report can
# show where it and the intended criterion disagree.
HAS_A_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def refutation_problems(slug, tid, kind, ref):
    """A refutation record that cannot be a gesture at having been reviewed."""
    if not isinstance(ref, dict):
        return [f"{slug}/{tid}: `refutation` is not a record"]
    out = []
    if not ref.get("pass"):
        out.append(f"{slug}/{tid}: `refutation` names no pass, so a reader cannot "
                   "find what refuted it")
    verdict = ref.get("verdict")
    if verdict not in VERDICTS:
        out.append(f"{slug}/{tid}: `refutation.verdict` is {verdict!r}, which is not "
                   f"one of {', '.join(VERDICTS)}")
    if not ref.get("axes"):
        out.append(f"{slug}/{tid}: `refutation` names no axes, and the axis an attack "
                   "landed on is the whole content of a verdict")
    if verdict in ("reject", "revise") and not ref.get("amended"):
        out.append(f"{slug}/{tid}: `refutation.verdict` is {verdict!r} and nothing says "
                   "what was amended, so the row records a criticism it did not act on")
    if verdict == "survived" and kind != "refuted-and-survived":
        out.append(f"{slug}/{tid}: `refutation.verdict` is 'survived' and the kind is "
                   f"{kind!r}, so a row that earned the better label is not wearing it")
    if kind == "refuted-and-survived" and verdict != "survived":
        out.append(f"{slug}/{tid}: claims the kind `refuted-and-survived` while its own "
                   f"refutation records {verdict!r}. The label is for a prediction that "
                   "survived a pass, not for one that went through one")
    return out


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
            if kind == "refuted-and-survived" and not basis.get("refutation"):
                problems.append(f"{slug}/{tid}: claims `refuted-and-survived` and names "
                                "no refutation, so there is nothing to check it against")
                continue
            if kind == "measured-floor" and not (
                    (task.get("fixture_leak") or {}).get("stub_score")):
                problems.append(f"{slug}/{tid}: claims `measured-floor` and carries no "
                                "`fixture_leak.stub_score`, so the floor it claims to "
                                "have measured is not written down anywhere a gate can "
                                "re-derive it. "
                                "`skills/_validation/project_fixture_probe.py` measures "
                                "it")
                continue
            ref = basis.get("refutation")
            if ref is not None:
                bad = refutation_problems(slug, tid, kind, ref)
                if bad:
                    problems.extend(bad)
                    continue
            reason = " ".join(str(basis.get(f, "")) for f in
                              ("run", "note", "refutation"))
            rows.append({"skill": slug, "task": tid, "kind": kind,
                         "task_kind": task.get("kind", "treatment"),
                         "refutation": basis.get("refutation"),
                         "detail": basis.get("run") or basis.get("refutation")
                         or basis.get("note", ""),
                         "dated": bool(HAS_A_DATE.search(reason)),
                         "repository_shape": bool(
                             REPOSITORY_SHAPE.search(task.get("without_skill") or ""))})
    return rows, problems


def criteria_come_apart(rows):
    """Every candidate the wide net catches, with both criteria printed beside it.

    This is a report and not a check, and it prints all the net's catches rather
    than only the dateless ones. The first draft printed the dateless ones alone
    and that version deleted its own evidence: relabelling `he-t9` by hand wrote
    a dated note onto it, the row stopped being dateless, and the one
    counter-example to "has a date" vanished from the list that exists to show
    the two criteria disagreeing. A list that empties when somebody does the work
    it asked for cannot be read twice.

    So both columns ship. The reader sees the correlation, the exceptions to it,
    and which rows are still labelled `authored-judgement` while reading like
    repository facts, which is the set actually worth a hand reading. Which
    referent "the graph" has in any one of them is fixed by that task's own
    prompt, and no gate can see that.
    """
    return [r for r in rows if r["repository_shape"]]


def _verdict(total, problems):
    """One exit for both output modes, through the shared refusal.

    `total` is the denominator: every prediction this run read a label off. It
    was never consulted before 2026-11-02, so an empty suite printed the pass
    sentence below over nothing at all and exited 0.
    """
    return verdict(
        "prediction-basis labels", checked=total, unit="predictions",
        failures=len(problems),
        pass_line=f"Every one of the {total} predictions says what it rests on. "
                  "Exit 0 does not mean the predictions are right, only that "
                  "none of them is pretending.",
        fail_line=f"{len(problems)} of {total} predictions carry no usable "
                  "basis label.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    tt.refuse_unresolved("--skills-dir", args.skills_dir, "skill directory",
                         glob.glob(os.path.join(args.skills_dir, "*", "SKILL.md")))

    rows, problems = audit(args.skills_dir)
    counts = {k: sum(1 for r in rows if r["kind"] == k) for k in KINDS}
    total = len(rows) + len(problems)

    apart = criteria_come_apart(rows)
    refuted = [r for r in rows if r.get("refutation")]
    survived = [r for r in refuted if r["refutation"].get("verdict") == "survived"]
    treatments = [r for r in rows if r["task_kind"] == "treatment"]
    controls = [r for r in rows if r["task_kind"] == "control"]

    if args.json:
        print(json.dumps({"total": total, "counts": counts,
                          "refuted": [
                              {"skill": r["skill"], "task": r["task"],
                               "verdict": r["refutation"].get("verdict"),
                               "axes": r["refutation"].get("axes")}
                              for r in refuted],
                          "survived_a_pass": len(survived),
                          "by_task_kind": {
                              "treatment": {k: sum(1 for r in treatments
                                                   if r["kind"] == k) for k in KINDS},
                              "control": {k: sum(1 for r in controls
                                                 if r["kind"] == k) for k in KINDS}},
                          "problems": problems, "rows": rows,
                          "criteria_come_apart": [
                              {"skill": r["skill"], "task": r["task"],
                               "kind": r["kind"]} for r in apart]}, indent=2))
        if not args.check:
            return 0
        with contextlib.redirect_stdout(sys.stderr):
            return _verdict(total, problems)

    for kind in KINDS:
        print(f"{counts[kind]:>4} of {total} predictions: {kind}")
        for row in rows:
            if row["kind"] == kind and kind != "authored-judgement":
                print(f"       {row['skill']}/{row['task']}: {row['detail']}")
    print()
    print(f"{counts['observed-bare-run']} of {total} predictions have ever been checked "
          "against a run of the unaided arm. Every delta this library reports rests on "
          "the other " f"{total - counts['observed-bare-run']}.")
    print(f"{counts['refuted-and-survived']} of the {counts['authored-judgement']} "
          "authored judgements have survived a written refutation pass. That pass needs "
          "no credential and is the cheapest thing on this instrument's list.")

    # Finding 1 of the 2026-11-02 pass: a prediction that failed the pass had
    # nowhere to be recorded, so running the pass lost its own result.
    print()
    print(f"       {len(refuted)} predictions have been through a written refutation "
          f"pass and {len(survived)} survived one.")
    if refuted:
        width = max(len(f"{r['skill']}/{r['task']}") for r in refuted)
        print("       {}  {:<9}  {}".format("task".ljust(width), "verdict", "axes"))
        for r in sorted(refuted, key=lambda r: (r["refutation"].get("verdict"),
                                                r["skill"], r["task"])):
            ref = r["refutation"]
            print("       {}  {:<9}  {}".format(
                f"{r['skill']}/{r['task']}".ljust(width),
                ref.get("verdict", "?"), ", ".join(ref.get("axes") or [])))
        print()
        print("       A refuted row is not promoted for having been refuted. The repair")
        print("       is another authored judgement, so the kind stays "
              "`authored-judgement`")
        print("       and the verdict sits beside it. What this block buys is that the "
              "rows")
        print("       which have been attacked are no longer indistinguishable from the "
              "ones")
        print("       nobody has read, which is the whole of the finding it answers.")

    # Finding 3 of the same pass: a control's prediction gates nothing, so
    # counting it beside a treatment's overstates the instrument's exposure.
    print()
    print(f"       Partitioned by what the row is for, because a control's prediction "
          "gates")
    print("       nothing: a control is passed when the two arms agree, whatever it "
          "said.")
    print("       {:<26}  {:>10}  {:>8}".format("label", "treatment", "control"))
    for kind in KINDS:
        t = sum(1 for r in treatments if r["kind"] == kind)
        c = sum(1 for r in controls if r["kind"] == kind)
        print("       {:<26}  {:>10}  {:>8}".format(kind, t, c))
    print("       {:<26}  {:>10}  {:>8}".format("all", len(treatments), len(controls)))
    aj_t = sum(1 for r in treatments if r["kind"] == "authored-judgement")
    print()
    print(f"       So the number that bounds this library's exposure is {aj_t} and not "
          f"{counts['authored-judgement']}:")
    print("       an unobserved prediction on a treatment row gates a delta, and one on "
          "a")
    print("       control row gates nothing at all.")

    print()
    print(f"{len(apart)} predictions the repository-shape net catches, with both "
          "criteria beside each:")
    labels = {id(r): "{}/{}".format(r["skill"], r["task"]) for r in apart}
    width = max([len(v) for v in labels.values()], default=0)
    print("       {}  {:<23}  {}".format("task".ljust(width), "label", "reason dated"))
    for row in sorted(apart, key=lambda r: (r["kind"], r["skill"], r["task"])):
        print("       {}  {:<23}  {}".format(labels[id(row)].ljust(width), row["kind"],
                                             "yes" if row["dated"] else "no"))
    undated_aj = [r for r in apart
                  if not r["dated"] and r["kind"] == "authored-judgement"]
    disagree = [r for r in apart
                if r["dated"] != (r["kind"] != "authored-judgement")]
    print()
    print(f"       {len(disagree)} of these {len(apart)} rows break the correlation "
          "between the two columns, and do not")
    print("       read it as progress either. On 2026-11-02 the correlation was perfect")
    print("       across the whole library and that was the finding against this")
    print("       instrument: the criterion being applied in practice was \"has a date\"")
    print("       rather than \"is a fact about this repository\". It broke later the")
    print("       same day, and not because anything was relabelled. The refutation pass")
    print("       wrote a dated amendment onto four rows that are still")
    print("       `authored-judgement`, so they now read dated and carry the honest")
    print("       label, which is exactly the combination the old sentence called")
    print("       impossible. The column moves when a row is edited for any reason at")
    print("       all, so it tracks how recently a row was touched rather than what it")
    print("       rests on. It is printed to be read, not watched.")
    print()
    print(f"       The {len(undated_aj)} rows with `authored-judgement` and no date are "
          "the set worth a hand")
    print("       reading. The gate does not fail on `authored-judgement`, so a repository")
    print("       fact wearing that label is invisible to every check here, and a reading")
    print("       is the only thing that can settle one: the referent of \"the graph\" or")
    print("       \"this library\" is fixed by each task's own prompt and nowhere else.")
    print("       The net over-matches on purpose. The research seat's hand adjudication")
    print("       dropped `ams-c1`, whose only marker is \"an A/B test online\" inside the")
    print("       competent answer being predicted rather than a trial of ours. A gate")
    print("       cannot see that, so it says too much instead of guessing.")
    for p in problems:
        print(f"failing: {p}")
    code = _verdict(total, problems)
    # Without `--check` this is a reader and a labelled defect is printed rather
    # than failed. A denominator of zero is refused either way, because then
    # the reader read nothing and said so as though it had read everything.
    if not args.check and code == 1:
        return 0
    return code


if __name__ == "__main__":
    sys.exit(main())
