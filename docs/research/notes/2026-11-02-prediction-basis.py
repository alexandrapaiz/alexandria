#!/usr/bin/env python3
"""Reconcile two counts of how many eval predictions reason from this repository.

    python3 docs/research/notes/2026-11-02-prediction-basis.py

On 2026-11-02 the research seat reported that 8 of 102 `without_skill`
predictions "reason from this repository's own history rather than from a
subject", and named only three of the eight in prose. The skill seat, labelling
the same 102 tasks by hand, counted 3 and asked the research seat to name its
five or concede them.

That is answerable from the files, which is the point of writing it as a script
rather than as a second hand count. Reads the nine eval suites and nothing else:
no corpus, no model call, no network.

The two counts were never a disagreement about a fact. The skill seat's labels
are mutually exclusive, one basis per task, so a prediction that cites an
observed bare run cannot also be counted as repository history. The research
seat's number was a non-exclusive property of the text. So the first job is to
enumerate every candidate under a deliberately wide net, and the second is to
adjudicate each one by reading its own task's prompt, which is where the
referent of "the graph" or "this library" or "the probes" is actually fixed.

Exit 0 always. This reports, it does not gate. The gate is the skill seat's
`skills/_validation/prediction_basis.py`, which this script does not duplicate.
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")

# A deliberately wide net. Over-matching is the right error here: a candidate
# that survives to the adjudication table costs one line of reading, and a
# candidate that never enters it is the defect this script exists to find.
MARKERS = [
    r"\bour\b", r"\bours\b", r"\bwe\b",
    r"\bthis (skill|suite|librar|seat|repositor|corpus|estate|org|file|shelf|delta|paper|very paper)",
    r"\bthe (graph|suite|librar|seat|corpus|estate|probes?|ledger|register)\b",
    r"20\d\d-\d\d-\d\d", r"\buntil (today|20)", r"\bdeprecat", r"\bprovenance\b",
    r"\balexandria\b", r"\bsince\b", r"\bitself asserted\b", r"\bA/B\b",
]
NET = re.compile("|".join(MARKERS), re.I)

# One verdict per candidate, with the sentence in the task that fixes the
# referent. REPO means the reason the prediction gives is a fact about this
# repository. SUBJECT means the marker points at something inside the task's own
# prompt or check, which is a fact about the scenario and not about us.
VERDICTS = {
    "ac-t9": ("SUBJECT",
              "'the effect and provenance probes' are this task's own four probes. Its"
              " situation says three of the four carry no forbidden substring."),
    "ac-t10": ("SUBJECT",
               "'Neither probe about provenance or intersection' is again this task's"
               " own check, not a record of anything that happened here."),
    "ams-t4": ("SUBJECT",
               "'the graph's offline retrieval metrics' is the prompt's own memory"
               " graph: 'Today each query walks our memory graph... The graph itself"
               " tests well on offline retrieval metrics.'"),
    "ams-c1": ("SUBJECT",
               "'an A/B test online' is the competent answer being predicted, not a"
               " trial of ours."),
    "cwe-t2": ("REPO",
               "'the two tests added on 2026-10-26' are ours: the suite's own revision"
               " note says cwe-t2's hard check 'gained two tests for the bilateral half"
               " of the protection finding' on that date."),
    "cwe-t8": ("REPO",
               "'which this skill itself asserted until 2026-10-26' is this repository's"
               " own dated correction."),
    "cwe-t11": ("REPO",
                "'this suite's own skill asserted it until 2026-10-26' likewise."),
    "he-t1": ("REPO",
              "'the 2026-09-12 A/B trial already in this skill's provenance' is ours."
              " It is also the one observed bare run, which is why an exclusive"
              " labelling puts it in that category instead."),
    "he-t9": ("REPO",
              "'a claim from this very paper that our graph has since deprecated' is"
              " this repository's claim graph. Nothing in this task's prompt has a"
              " graph in it, and the prompt is a warehouse arm and 41 tool calls."),
    "sle-t8": ("SUBJECT",
               "'this library's documents' is the prompt's 60-skill library: 'We are"
               " deciding where to spend our writing effort on a 60-skill library...'"),
}


def load():
    tasks = []
    for path in sorted(glob.glob(os.path.join(ROOT, "skills", "*", "evals", "evals.json"))):
        shelf = path.split(os.sep)[-3]
        for task in json.load(open(path))["tasks"]:
            tasks.append((shelf, task))
    return tasks


def main():
    tasks = load()
    candidates = []
    for shelf, task in tasks:
        text = task.get("without_skill", "")
        hits = sorted({m.group(0).lower() for m in NET.finditer(text)})
        if hits:
            candidates.append((shelf, task, hits))

    print(f"{len(tasks)} predictions across {len({s for s, _ in tasks})} suites")
    print(f"{len(candidates)} caught by the wide net\n")

    unjudged = [t["id"] for _, t, _ in candidates if t["id"] not in VERDICTS]
    if unjudged:
        print(f"!! {len(unjudged)} candidates have no verdict in this file: {unjudged}")
        print("   Adjudicate them by reading the task's prompt before trusting any count below.\n")

    repo, subject = [], []
    for shelf, task, hits in candidates:
        verdict, why = VERDICTS.get(task["id"], ("UNJUDGED", "-"))
        (repo if verdict == "REPO" else subject).append((shelf, task, hits, why))

    print(f"REPOSITORY FACT: {len(repo)}")
    for shelf, task, hits, why in repo:
        print(f"  {task['id']:<10} [{task['kind']:<9}] {shelf}")
        print(f"      {why}")
    print(f"\nSUBJECT FACT (the marker points inside the task): {len(subject)}")
    for shelf, task, hits, why in subject:
        print(f"  {task['id']:<10} [{task['kind']:<9}] {shelf}  markers={hits}")
        print(f"      {why}")

    # The two counts, reconciled.
    skill_labels = {"cwe-t2", "cwe-t8", "cwe-t11"}          # this-repository-history
    skill_observed = {"he-t1"}                               # observed-bare-run
    skill_nearly = {"ac-t9", "ac-t10", "sle-t8", "ac-t11"}   # their "nearly miscounted"
    repo_ids = {t["id"] for _, t, _, _ in repo}
    mine = repo_ids | {t["id"] for _, t, _, _ in subject if t["id"] != "ams-c1"}

    print("\n" + "=" * 68)
    print("The reconciliation")
    print("=" * 68)
    print(f"research seat's reported count          : 8")
    print(f"reconstructed, candidates minus he-t1   : {len(mine - skill_observed)}"
          f"  {sorted(mine - skill_observed)}")
    print(f"skill seat's this-repository-history    : {len(skill_labels)}  {sorted(skill_labels)}")
    print(f"repository facts on reading             : {len(repo_ids)}  {sorted(repo_ids)}")
    print(f"  of those, unlabelled by the new gate  : {sorted(repo_ids - skill_labels - skill_observed)}")
    print(f"conceded: mine, and subject facts       : {sorted(mine - repo_ids)}")
    print(f"in their 'nearly miscounted', never mine: {sorted(skill_nearly - mine)}")
    print(f"mine and outside their sweep entirely   : {sorted((mine - repo_ids) - skill_nearly)}")

    dated = [t["id"] for _, t, _, _ in repo if re.search(r"20\d\d-\d\d-\d\d", t["without_skill"])]
    undated = sorted(repo_ids - set(dated))
    print(f"\nrepository facts carrying a date        : {sorted(dated)}")
    print(f"repository facts carrying no date       : {undated}")
    print("The gate's four labelled rows are exactly the dated ones, so in practice the")
    print("criterion applied was 'has a date' rather than 'is a fact about this repository'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
