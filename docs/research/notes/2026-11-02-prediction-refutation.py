#!/usr/bin/env python3
"""The red-team refutation pass, as the checkable half of a judgement.

The skill seat asked this seat (board message `d94f98dd`, PR #706) to run the
red-team refutation pass of Skill-Use (`arxiv:2608.04828`, appendix B.1 and
F.1, figure 15) on the five dateless `authored-judgement` rows its own gate
prints, on the paper's five named axes: skill-specificity, verifiability,
triggerability, non-redundancy, gradability, with an accept, revise or reject
verdict per row.

A refutation is a reading and most of it cannot be mechanised. What CAN be
mechanised is every factual premise the reading rests on, and that is what this
script is for. It asserts each one against the suite files rather than against
the note beside it, so a reader can tell a measured premise from an argument.

    python3 docs/research/notes/2026-11-02-prediction-refutation.py
    python3 docs/research/notes/2026-11-02-prediction-refutation.py --check

No corpus, no model call, no network. It reads `skills/*/evals/evals.json` and
nothing else.

The suites it reads live on `alexandria-skill/2026-11-02-message-use-when-coefficient`
(PR #717) and not yet on `main`, because `skills/` is the skill seat's under
ADR-22 and this seat does not write there. Point `--skills-dir` at a checkout
of that branch, or pass `--from-ref` to read the files straight out of it.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

SKILL_BRANCH = "origin/alexandria-skill/2026-11-02-message-use-when-coefficient"

ROWS = ("agent-containment/ac-t9", "agent-containment/ac-t10",
        "agent-memory-selection/ams-t4", "agent-memory-selection/ams-c1",
        "skill-library-engineering/sle-t8")

# The five axes, as figure 15 names them, with the mapping this pass applied.
# The paper attacks a CONSTRAINT in a skill document; the object here is a
# `without_skill` PREDICTION about an unaided arm. The mapping is stated so a
# reader can reject it rather than having to reconstruct it.
AXES = {
    "skill-specificity":
        "does the gap the prediction asserts belong to this skill, or is the "
        "skilled answer reachable from what the task already hands the subject",
    "verifiability":
        "is the prediction stated concretely enough that one observed bare run "
        "would confirm or falsify it, rather than absorb either outcome",
    "triggerability":
        "does the task's own prompt create the situation the prediction is "
        "about, or does it foreclose the predicted answer in its own wording",
    "non-redundancy":
        "does this prediction do work no sibling row's prediction already does, "
        "so the delta is not counting one predicted behaviour twice",
    "gradability":
        "can the check distinguish the predicted bare answer from the skilled "
        "one by degree, or is a near-miss recorded identically to a miss",
}


def load(skills_dir, from_ref):
    out = {}
    for slug in sorted({r.split("/")[0] for r in ROWS}):
        rel = f"skills/{slug}/evals/evals.json"
        if from_ref:
            text = subprocess.run(["git", "show", f"{from_ref}:{rel}"],
                                  capture_output=True, text=True, check=True).stdout
        else:
            text = (pathlib.Path(skills_dir) / slug / "evals" / "evals.json").read_text(
                encoding="utf-8")
        data = json.loads(text)
        for task in data["tasks"]:
            out[f"{slug}/{task['id']}"] = task
    return out


def premises(tasks):
    """Every factual premise the note's five readings rest on, each decidable.

    Returns (label, passed, what was found) triples.
    """
    got = []

    def check(label, condition, found):
        got.append((label, bool(condition), found))

    # --- ac-t9: the starter file names the two axes the prediction says the
    # bare arm will miss, and hands `allow` an argument its body never reads.
    guard = tasks["agent-containment/ac-t9"]["files"]["guard.py"]
    check("ac-t9 guard.py documents `arg_sources` with a `tool_output` value",
          "arg_sources" in guard and "tool_output" in guard,
          "both substrings present" if "tool_output" in guard else "absent")
    check("ac-t9 guard.py documents `effect` as op/resource/persistence",
          all(k in guard for k in ('"op"', '"resource"', '"persistence"')),
          "all three keys named in the docstring")
    body = guard.split("def allow(")[1]
    check("ac-t9 `allow` takes `authority` and its body never reads it",
          "authority" in body.split("\n")[0] and "authority." not in body,
          "signature takes it, body does not touch it")
    check("ac-t9 is a project task, so the subject is handed that file",
          tasks["agent-containment/ac-t9"]["form"] == "project",
          tasks["agent-containment/ac-t9"]["form"])
    check("ac-t9 prompt says the logged command carried nothing on the deny list",
          "nothing on our deny list" in tasks["agent-containment/ac-t9"]["prompt"],
          "present verbatim")

    # --- ac-t10: the same, one step further, plus the prompt asking in words
    # for the property the prediction says the bare arm will not produce.
    authz = tasks["agent-containment/ac-t10"]["files"]["authz.py"]
    check("ac-t10 authz.py documents `bindings` as permitted argument origins",
          "bindings" in authz and "argument origins" in authz,
          "both present")
    check("ac-t10 `authorize` ignores `bindings` entirely",
          "bindings" not in authz.split("def authorize(")[1].split("def delegate(")[0],
          "the body is `return call.tool in grant.tools`")
    check("ac-t10 `delegate` docstring confesses the defect probe 3 tests",
          "whatever is asked for" in authz,
          "'Current design: whatever is asked for.'")
    check("ac-t10 prompt asks in words for delegation not to widen authority",
          "delegation cannot widen authority"
          in tasks["agent-containment/ac-t10"]["prompt"],
          "present verbatim")
    check("ac-t10 prompt says the tool used was one we intend to allow",
          "one we intend to allow" in tasks["agent-containment/ac-t10"]["prompt"],
          "present verbatim, which forecloses the predicted allowlist answer")

    # --- ams-t4: the prediction names no assertion, and the check reports no
    # partial credit, so neither end of the row can be checked by degree.
    t4 = tasks["agent-memory-selection/ams-t4"]
    ids = [a["id"] for a in t4["check"]["assertions"]]
    check("ams-t4 has five named assertions",
          len(ids) == 5, ", ".join(ids))
    # The verifiability premise, stated the way it is actually decidable. A
    # substring match on an assertion id is no good here: `traversal` appears in
    # ams-t4's prediction inside "parallelises traversal", which is English and
    # not a reference. What separates the rows is whether anything in the task
    # commits to a predicted bare SCORE, which an observed run can contradict.
    scored = {r: bool(re.search(r"scores \d+ of \d+",
                               json.dumps(tasks[r]["check"]) + tasks[r]["without_skill"]))
              for r in ROWS}
    check("only the two agent-containment rows commit to a predicted bare score",
          [r for r, v in scored.items() if v]
          == ["agent-containment/ac-t9", "agent-containment/ac-t10"],
          "scored: " + ", ".join(r.split("/")[1] for r, v in scored.items() if v)
          + "; unscored: "
          + ", ".join(r.split("/")[1] for r, v in scored.items() if not v))
    check("ams-t4's five assertions are an undifferentiated set in the prediction",
          "assertion" not in t4["without_skill"],
          "the prediction describes a mechanism and maps it to no assertion")
    check("ams-t4 pass_condition is all-or-nothing",
          t4["check"]["pass_condition"] == "all five assertions hold",
          t4["check"]["pass_condition"])
    check("ams-t4 prompt contains the `quality` assertion's own requirement",
          "keep the quality" in t4["prompt"],
          "'I want to keep the quality and cut the latency'")

    # --- ams-c1: the decoy vocabulary the situation claims is not in the prompt.
    c1 = tasks["agent-memory-selection/ams-c1"]
    claimed = ["retrieval", "candidates", "rerank", "top-k", "embedding"]
    absent = [w for w in claimed if not re.search(re.escape(w), c1["prompt"], re.I)]
    check("ams-c1 situation lists five borrowed words",
          all(re.search(re.escape(w), c1["situation"], re.I) for w in claimed),
          ", ".join(claimed))
    check("ams-c1 prompt carries none of the five as spelled",
          len(absent) == 5, f"absent from the prompt: {', '.join(absent)}")
    check("ams-c1 is a control, so its prediction gates no delta",
          c1["kind"] == "control",
          "a control passes when the two arms agree, whatever the prediction said")
    check("ams-c1 keeps the numeric decoy the lexical one lost",
          "30 candidate" in c1["prompt"] and "top 10" in c1["prompt"],
          "30 shown as 10 is the skill's own keep ratio, carried by the numbers")

    # --- sle-t8: the task's own `exploit` field is a written bare-shaped answer
    # that does the thing the prediction says the bare arm will not do.
    t8 = tasks["skill-library-engineering/sle-t8"]
    check("sle-t8 prediction says the bare arm misses the conditional",
          "without noticing" in t8["without_skill"]
          and "mechanisms" in t8["without_skill"],
          t8["without_skill"][:60] + "...")
    check("sle-t8 carries an `exploit` whose answer states that conditional",
          "It depends on how your harness routes" in t8["exploit"]["answer"],
          "the exploit's first sentence is the conditional, stated")
    check("sle-t8 exploit ceiling is 0.0, so the shape alone scores nothing",
          t8["exploit"]["ceiling"] == 0.0,
          f"ceiling {t8['exploit']['ceiling']}")
    check("sle-t8 prompt plants both facts the `procedural_case` criterion wants",
          "long procedural runbooks" in t8["prompt"]
          and "share a lot of surface vocabulary" in t8["prompt"],
          "both present verbatim in the prompt")
    check("sle-t8 is the only one of the five whose check carries certificates",
          all("certificate" in c for c in t8["check"]["criteria"]),
          f"{len(t8['check']['criteria'])} criteria, every one with a certificate")

    # --- non-redundancy, across the whole of each suite rather than the five.
    ac = {k: v for k, v in tasks.items() if k.startswith("agent-containment/")}
    deny = [k for k, v in ac.items()
            if re.search(r"deny list", v["without_skill"], re.I)]
    check("ac-t9's predicted failure is predicted by two siblings too",
          len(deny) >= 3 and "agent-containment/ac-t9" in deny,
          f"{len(deny)} rows predict a deny-list answer: " + ", ".join(sorted(deny)))
    inj = [k for k, v in ac.items()
           if re.search(r"injection (classifier|detection)", v["without_skill"], re.I)]
    check("ac-t10's predicted failure is predicted by a sibling too",
          set(inj) >= {"agent-containment/ac-t2", "agent-containment/ac-t10"},
          "rows predicting an injection classifier: " + ", ".join(sorted(inj)))

    # --- the gap in the instrument the pass itself opens.
    kinds = ("observed-bare-run", "this-repository-history", "authored-judgement",
             "refuted-and-survived")
    check("the gate has no label for a prediction that FAILED a refutation",
          not any("refuted" in k and "survived" not in k for k in kinds),
          "the four kinds are: " + ", ".join(kinds))

    return got


# The readings themselves. Each verdict is a judgement; the premises above are
# what it rests on. `hit` axes are the ones the attack landed on.
VERDICTS = {
    "agent-containment/ac-t9": ("reject", ["skill-specificity", "triggerability",
                                           "non-redundancy"]),
    "agent-containment/ac-t10": ("reject", ["skill-specificity", "triggerability",
                                            "non-redundancy"]),
    "agent-memory-selection/ams-t4": ("revise", ["verifiability", "gradability",
                                                 "triggerability"]),
    "agent-memory-selection/ams-c1": ("revise", ["triggerability"]),
    "skill-library-engineering/sle-t8": ("revise", ["verifiability",
                                                    "triggerability"]),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--from-ref", default=SKILL_BRANCH,
                    help="read the suites out of this git ref; '' to read the tree")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any premise below no longer holds")
    args = ap.parse_args()

    tasks = load(args.skills_dir, args.from_ref or None)
    got = premises(tasks)

    print("The five axes, and how figure 15's object maps onto a prediction\n")
    for axis, gloss in AXES.items():
        print(f"  {axis}")
        print(f"      {gloss}")
    print()

    print("Premises, each decided against the suite file rather than the note\n")
    failed = [g for g in got if not g[1]]
    for label, ok, found in got:
        print(f"  [{'ok ' if ok else 'NO '}] {label}")
        print(f"         {found}")
    print()

    print("Verdicts, one per row, on the paper's accept/revise/reject contract\n")
    for row in ROWS:
        verdict, hits = VERDICTS[row]
        print(f"  {row:34}  {verdict:7}  axes the attack landed on: "
              f"{', '.join(hits) if hits else 'none'}")
    print()
    survived = [r for r in ROWS if VERDICTS[r][0] == "accept"]
    print(f"  {len(survived)} of {len(ROWS)} survived unamended, so none of the five "
          "may carry `refuted-and-survived` today.")
    print("  Two are rejected on evidence inside their own task files and three "
          "need a named amendment first.")
    print()

    if failed:
        print(f"{len(failed)} premises no longer hold, so the note above is stale:")
        for label, _, found in failed:
            print(f"  {label}: {found}")
        return 1 if args.check else 0
    print(f"All {len(got)} premises hold. That makes the readings checkable, "
          "not correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
