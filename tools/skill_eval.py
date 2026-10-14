#!/usr/bin/env python3
"""With-versus-without: does a builder actually do better work with this skill loaded.

    python3 tools/skill_eval.py --skill harness-engineering            # run it
    python3 tools/skill_eval.py --skill harness-engineering --reps 3
    python3 tools/skill_eval.py --skill harness-engineering --plan     # spend nothing
    python3 tools/skill_eval.py --skill harness-engineering --smoke    # prove the harness, no key
    python3 tools/skill_eval.py --check                               # every eval file conforms
    python3 tools/skill_eval.py --skill X --subject kimi-k2.6 --judge openai/gpt-oss-120b

ADR-36, the owner's words: "Can we make sure skills are good? Can we run unit
tests and evals on them, comparing projects and prompts with and without the
skills?" A skill's claim on a builder's context window is a claim that the
builder does better work with it loaded. Until this file existed, the library
made that claim on one A/B trial, on one prompt, in one session, at n of 1.

## What it does

For each task in `skills/<slug>/evals/tasks.json`, the subject model answers
twice: once with the skill's body in its system prompt, once without. Same model,
same wrapper, same reservation, same temperature, same task text. Only the skill
varies. That last sentence is the whole design and it comes out of the corpus:
an A/B that changes the skill and anything else about the harness at the same
time is measuring the harness (Iris, via docs/product/skill-validation.md §2).

Each answer is scored either by a hard check, when the task has one, or by a
rubric a second model judges. The subject and the judge are never the same model,
which the runner refuses rather than warns about.

Every task runs `--reps` times per arm, and the report is the delta with its
spread, never a point estimate. `results.json` is the source of truth for
anything the site says about the skill; `site/app/skills/README.md` is the
contract it writes.

## The five rules it will not print around

From `docs/product/skill-validation.md` §V5, which is the gate that governs what
the other gates are allowed to say.

1. The policy is pre-registered. `tasks.json` carries the repetitions, the
   models and the threshold, and the run copies them into the result rather than
   choosing them. Nobody tunes until green.
2. Counts are reported as counts with an exact binomial interval, never as a bare
   percentage. "8 of 10, 95% CI 0.44 to 0.97" is a receipt. "80%" is marketing.
3. Zero observed failures is reported as a finite-sample bound, not as certainty.
4. The task count, the model, the judge, the repetitions and the date are in
   every result, because a delta without them is unreadable.
5. A skill whose eval shows no gain is a finding and it is printed as one. ADR-36
   says such a skill is retired with the numbers, which is also what the site
   promised.

## Who writes the tasks, and why not this file

Not the engineer and not the skill's own author, if the library can help it.
Both the cases and the decoy panel of the existing trigger test were written by
the agent that wrote the skills, in the same session, and that is the
contamination the disjointness results in the corpus warn about
(ModularRSI, Beyond Solver Verdicts). This file is the instrument. The skill seat
authors the tasks. A skill with no `evals/` directory is reported as unmeasured,
which is the honest state, and never as a pass.

## Cost, and the one thing that will bite

The subject is Kimi by default, from `pipeline/budget.py`'s table, because ADR-36
wants an eval cheap enough to run on every skill change; the judge defaults to
Groq's free tier, so judging is free. A 6-task, 5-repetition run is 60 subject
calls, about $0.40 at kimi-k2.6's list price, and `CAP_USD` stops it there.

The thing that will bite is Moonshot's organization concurrency of 1. An eval run
is 60 calls in a row, so it will collide with the press, triage or interpret if
it starts inside one of their windows, and that collision is failure 2 of
INC-2026-09-24-press-provider-migration. This runner reads
`pipeline/llm.py` KIMI_WINDOWS and refuses to start inside a reserved one. Use
`--force` only if you know the other job is not running.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

# What a suite's own version number may say. Two numbers, not one, because
# two seats write one format: this harness called it `contract`, the skill
# seat's suites call it `suite_version: 2`, and a reader that speaks only its
# own number refuses the work it exists to measure
# (URGENT ledger entry, 2026-10-03). The harness moves, since the suites are
# the work and this file is the instrument.
SUITE_CONTRACTS = (1, 2)

# What a result document written today is tagged with, which is a different
# number living in a different document. Until today one constant served both,
# and `summarize` tagged its result with the newest number any *suite* may
# carry, so widening the reader above silently moved the result from 1 to 2.
# site/app/skills/README.md is the contract for the result, it says `1`, and its
# own first rule is that a reader which does not know the number renders pending
# rather than guessing. One constant for two documents means a change to the
# dialect the harness reads can blank the page it writes.
# Two as of 2026-10-05, when ADR-40's items landed. Every key contract 1
# carried is still there and still means the same thing, so a reader written
# against 1 is not broken by a 2; the number moved because a reader that wants
# the per-section deltas, the exploit test or the held-out block has to know
# whether this document is old enough to lack them. Additions only, and the
# contract document in site/app/skills/README.md is the one that says so.
RESULT_CONTRACT = 2

# Defaults. The subject comes from the budget table, so the id here is checked
# against the provider's live catalog by the same machinery the crons use.
DEFAULT_SUBJECT = "kimi-k2.6"
DEFAULT_JUDGE = "openai/gpt-oss-120b"
# Three, not five, and the arithmetic is the reason. The skill seat's real suites
# hold 10 to 12 tasks. At five repetitions per arm that is 110 to 120 subject
# calls, and the $0.75 cap below buys about 92 on kimi-k2.6, so a five-repetition
# run on a real suite stops at the cap partway through. Three is 66 to 72 calls,
# which fits with room, and it is also the default `claude plugin eval` chose for
# the same reason. A suite may pre-register more in its own `policy`, and then the
# cap is the thing to raise, in the same commit as docs/finance/opex.md.
DEFAULT_REPS = 3

# What one eval run may spend, measured from the provider's own usage block by
# pipeline/llm.py's Cap and never estimated. At kimi-k2.6's list price a
# with-skill call is about $0.008 and a without-skill call about $0.005, so
# $0.75 buys roughly 110 pairs: a 6-task run at 5 repetitions is 30 pairs and
# finishes well inside it. This is not a cron and it is not in
# budget.MONTHLY_CAP_CEILING_USD, which is the sum of the daily caps; an eval
# run is paid for when a skill changes.
CAP_USD = 0.75

# The subject's answer budget. Long enough for a considered answer to a design
# question, short enough that a model that starts writing an essay is stopped.
SUBJECT_MAX_TOKENS = 1200
JUDGE_MAX_TOKENS = 700

# Fixed, so a result is replayable. The bootstrap below is the only place
# randomness enters a number this file prints.
BOOTSTRAP_SEED = 20260930
BOOTSTRAP_DRAWS = 10_000

SUBJECT_SYSTEM = (
    "You are a senior engineer answering a colleague's question. Answer in "
    "JSON, as {\"answer\": \"...\"}, with your whole answer in that one string. "
    "Be concrete and specific. Recommend what you would actually do."
)

JUDGE_SYSTEM = (
    "You are grading one answer against a checklist. You do not know how the "
    "answer was produced and you must not speculate about it. Grade only what "
    "the answer says. For a criterion that lists numbered anchors, return the "
    "number of the anchor that describes the answer. For one that does not, "
    "return yes or no. Reply in JSON as {\"verdicts\": {\"<criterion id>\": "
    "<number>|\"yes\"|\"no\"}, \"why\": \"one sentence\"}."
)


# ------------------------------------------------------------------ statistics

def clopper_pearson(successes: int, n: int, alpha: float = 0.05
                    ) -> tuple[float, float]:
    """The exact binomial interval. Not a normal approximation, which at these n
    is simply wrong.

    Solved by bisection on the exact binomial tail rather than through a beta
    quantile, because `math.comb` is in the standard library and scipy is not a
    dependency of this repository. At n of 6 with 6 successes it returns a lower
    bound of 0.5407, which is the number docs/product/skill-validation.md quotes
    when it says a clean sweep of six bounds true reliability at 0.54.
    """
    if n <= 0:
        return (0.0, 1.0)
    successes = max(0, min(int(successes), n))

    def upper_tail(p: float) -> float:            # P(X >= successes)
        return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k)
                   for k in range(successes, n + 1))

    def lower_tail(p: float) -> float:            # P(X <= successes)
        return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k)
                   for k in range(0, successes + 1))

    def solve(target, fn, increasing: bool) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            value = fn(mid)
            if (value < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    low = 0.0 if successes == 0 else solve(alpha / 2, upper_tail, True)
    high = 1.0 if successes == n else solve(alpha / 2, lower_tail, False)
    return (round(low, 4), round(high, 4))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def bootstrap_delta(per_task: list[dict], draws: int = BOOTSTRAP_DRAWS,
                    seed: int = BOOTSTRAP_SEED) -> tuple[float, float, float]:
    """(delta, low, high) for the mean per-task delta, by a clustered bootstrap.

    Tasks are resampled with replacement and the repetitions inside each
    resampled task are resampled too. Clustered because the unit of independence
    is the task: five repetitions of one prompt are five looks at the same
    question, and treating them as thirty independent observations is the
    standard way to report an interval far tighter than the evidence.
    """
    if not per_task:
        return (0.0, 0.0, 0.0)
    point = mean([t["delta"] for t in per_task])
    rng = random.Random(seed)
    draws_out = []
    for _ in range(draws):
        deltas = []
        for _ in range(len(per_task)):
            task = per_task[rng.randrange(len(per_task))]
            w = task["with_scores"]
            o = task["without_scores"]
            if not w or not o:
                continue
            rw = mean([w[rng.randrange(len(w))] for _ in range(len(w))])
            ro = mean([o[rng.randrange(len(o))] for _ in range(len(o))])
            deltas.append(rw - ro)
        if deltas:
            draws_out.append(mean(deltas))
    draws_out.sort()
    if not draws_out:
        return (round(point, 4), 0.0, 0.0)
    low = draws_out[int(0.025 * (len(draws_out) - 1))]
    high = draws_out[int(0.975 * (len(draws_out) - 1))]
    return (round(point, 4), round(low, 4), round(high, 4))


# ADR-40 item 1, the matched ablation. The two arms must differ in the skill file
# and nothing else: same model, same tools, same retrieval, and "same seed where
# the provider allows". Two of those three were already true, because both arms
# go through one `Subject` and one `render_ask`. The seed was not, and neither
# was the temperature: this runner inherited `pipeline/llm.py`'s 0.2 default,
# which is matched across the arms and not replayable across runs.
#
# "Where the provider allows" is load-bearing, and it is a fact about two
# providers rather than a preference. Groq's chat completions accept `seed` and
# document it as best-effort determinism. Moonshot documents k2.6's temperature
# as fixed and documents no seed at all, and `pipeline/llm.py` already sends it
# neither. So a run pins what the provider will honour, and the result says in
# words which knobs were pinned and which could not be. A harness that printed
# `seed 20261005` next to a provider that ignores it would be claiming a
# replayability it does not have, and claiming a replayability you do not have is
# the exact failure this file exists to catch.
SUBJECT_SEED = 20261005
SEED_PROVIDERS = ("groq",)

# Pinned rather than inherited, for the same reason. The arms were always matched
# on temperature; they were not replayable, because the number lived in another
# file's default argument and a change there would move every measured delta in
# the library with no entry anywhere saying so.
EVAL_TEMPERATURE = 0.0

# ADR-40 item 4: an executable task runs in a Docker sandbox. The image is the
# agent image, so a task runs against the interpreter and the packages a real
# seat has, and `--network none` is the containment practice the library sells
# (skills/agent-containment). Overridable by environment because a laptop and
# the runner do not have the same image cached.
SANDBOX_IMAGE_DEFAULT = "ghcr.io/alexandrapaiz/alexandria-agent:latest"
SANDBOX_MODES = ("auto", "docker", "host")

# What a sandboxed command may have. A test that needs the network is a test
# whose result depends on somebody else's uptime.
SANDBOX_MEMORY = "1g"
SANDBOX_PIDS = "256"

# ADR-40 item 5: a rubric criterion is tied to a verifiable certificate in the
# task. These are the three kinds the ADR names, in its own words: a test, a
# number, or a named artifact.
CERTIFICATE_KINDS = ("test", "number", "artifact")

# And the exploit test's ceiling. C476 and C479 measured certificate-faithful
# rubrics at 0 percent exploited, so zero is the number, not a tolerance.
EXPLOIT_CEILING = 0.0

# ADR-40 item 6. The audit is one-time per task, so it lives in a file beside
# the suite rather than being re-run and re-paid for on every eval.
AUDIT_FILENAME = "audit.json"
AUDIT_QUESTIONS = (
    ("ambiguity", "Could a competent engineer read this task two ways that "
                  "score differently?"),
    ("gameability", "Can the scoring be satisfied without doing the work the "
                    "task describes?"),
    ("realism", "Is this a question somebody doing this job would actually "
                "ask?"),
)

# The length-bias check (C934): the same content scored at two lengths. Two
# tasks, one repetition each, because this costs judge calls and the question is
# whether the judge has a length preference at all rather than how large it is.
LENGTH_BIAS_SAMPLE = 2
LENGTH_BIAS_FLAG = 0.1


def seedable(model: str) -> bool:
    """Will this model's provider honour a seed. Read from the budget table."""
    try:
        import budget
    except Exception:                               # pragma: no cover
        return False
    return budget.MODELS.get(model, {}).get("provider") in SEED_PROVIDERS


def ablation_manifest(subject_model: str, judge_model: str, reps: int,
                      sandbox: str) -> dict:
    """What was held constant between the arms, and what could not be pinned.

    This block is the answer to "what else changed", and it is in the result
    document so that the answer is on the record rather than in this docstring.
    `unpinned` is the honest half: a provider that ignores a seed makes a run
    non-replayable, and the result says so out loud instead of implying the
    opposite by listing the seed and stopping.
    """
    pinned = {"subject_model": subject_model, "judge_model": judge_model,
              "repetitions": reps, "temperature": EVAL_TEMPERATURE,
              "system_prompt": "identical, plus the skill body in the with-arm",
              "task_text": "identical, files included, by render_ask",
              "tools": "none in either arm",
              "retrieval": "none in either arm",
              "sandbox": sandbox,
              "bootstrap_seed": BOOTSTRAP_SEED}
    unpinned = []
    if seedable(subject_model):
        pinned["subject_seed"] = SUBJECT_SEED
    else:
        unpinned.append(
            f"{subject_model} is not on a provider this harness can send a seed "
            f"to ({', '.join(SEED_PROVIDERS)}), so the arms are matched but the "
            "run is not replayable call for call")
    if not seedable(judge_model):
        unpinned.append(f"{judge_model} judged without a seed, for the same "
                        "reason")
    return {"differs": "the skill body in the subject's system prompt, and "
                       "nothing else",
            "pinned": pinned, "unpinned": unpinned}


def stdev(values: list[float]) -> float:
    """The sample standard deviation. Zero below two values, never an error.

    ADR-40 item 3: no conclusion from one sample, and the delta is reported with
    its spread. The bootstrap interval below answers "how uncertain is the mean".
    This answers the different question of "how much do the tasks disagree with
    each other", which an interval around a mean hides by construction.
    """
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def spread_of(values: list[float]) -> dict:
    """The spread of a list of numbers, as something printable."""
    return {"n": len(values), "sd": round(stdev(values), 4),
            "min": round(min(values), 4) if values else 0.0,
            "max": round(max(values), 4) if values else 0.0}


def pass_at_k(successes: int, n: int, k: int) -> float:
    """The unbiased pass@k estimator, 1 - C(n-c, k)/C(n, k).

    Codex's estimator, and the reason it is this rather than "did any of the k
    pass" is that the naive version is biased upward at small n, which is C248's
    warning about misreading small measurements in the one place this harness
    could repeat it. With c successes in n repetitions, pass@k is the chance that
    k draws without replacement from those n contain at least one success.
    """
    if n <= 0 or k <= 0:
        return 0.0
    k = min(k, n)
    c = max(0, min(int(successes), n))
    if n - c < k:
        return 1.0
    return round(1.0 - math.comb(n - c, k) / math.comb(n, k), 4)


def binary(scores: list[float]) -> bool:
    return bool(scores) and all(s in (0.0, 1.0) for s in scores)


def pass_rates(per_task: list[dict], key: str, k: int) -> dict | None:
    """pass@1 and pass@k over the tasks whose check is hard enough to have them.

    Only the tasks with a hard check, because pass@k is a statement about a
    pass-or-fail trial and a rubric score of 0.67 is not one. A suite with no
    such task gets no pass@k rather than a number computed by rounding, which is
    how a soft score quietly becomes a hard claim.
    """
    rows = [t for t in per_task if binary(t[key])]
    if not rows:
        return None
    at_1 = [mean(t[key]) for t in rows]
    at_k = [pass_at_k(int(sum(t[key])), len(t[key]), k) for t in rows]
    return {"k": k, "tasks": len(rows),
            "pass_at_1": round(mean(at_1), 4),
            "pass_at_k": round(mean(at_k), 4),
            "pass_at_1_spread": spread_of(at_1),
            "reads": f"pass@1 {mean(at_1):.2f}, pass@{k} {mean(at_k):.2f} over "
                     f"{len(rows)} hard-check task(s)"}


def gate_problems(result: dict, previous: dict | None) -> list[str]:
    """Why this result does not clear ADR-37's gate. Empty means it does.

    Only the clauses this harness measures. The amendment of 2026-09-29 names
    six and this file can speak to three: the delta is not worse than the
    previous version's within its spread on the same subject model, the control
    tasks are unchanged, and nothing was left unmeasured. The ban list, the
    trigger test, the diff scope and the page render belong elsewhere, and this
    function says so rather than implying it checked them.
    """
    problems = []
    if result.get("incomplete"):
        problems.append(f"the run did not finish: {result['incomplete']}")
    if result.get("unmeasured_tasks"):
        problems.append("tasks could not be measured at all, so the comparison "
                        f"is against a smaller suite: {result['unmeasured_tasks']}")
    controls = result.get("controls")
    if controls and not controls.get("unchanged"):
        problems.append(f"the control tasks moved by {controls['delta']:+.2f}, "
                        "so the skill is changing answers it is not supposed to "
                        "touch")
    if result["verdict"] != "gain":
        problems.append(f"the verdict is {result['verdict']!r} rather than a gain")

    # ADR-40 item 5. An exploited rubric is not a measurement, so it fails the
    # gate ahead of the delta: a delta computed by a rubric that scores an answer
    # written to game it is a number about the rubric.
    exploit = result.get("exploit_test")
    if exploit and exploit.get("verdict") == "exploited":
        problems.append(
            "an answer written to game the rubric scored "
            f"{exploit.get('max_score')} on {', '.join(exploit['exploited'])}, "
            f"against a ceiling of {exploit.get('ceiling')}. ADR-40 item 5: a "
            "rubric that can be gamed is measuring the rubric")

    # ADR-40 refinement item 2. Only on a document that was measured by a
    # harness which computes the block. A contract-1 result predates it, and
    # failing it here would block every revision on the absence of a field
    # nothing had written yet, which is a gate switched off by a detail.
    if int(result.get("contract") or 1) >= 2:
        held = result.get("heldout") or {}
        if held.get("verdict") == "no held-out set":
            problems.append(
                "every graded task is one this revision was written against, so "
                "there is no held-out evidence that the edit generalizes "
                "(ADR-40 refinement item 2). Name the tasks with "
                "--written-against, or add tasks the edit was not written on")
        elif held.get("verdict") == "does not hold":
            problems.append(
                f"the held-out delta is {held['delta']['mean']:+.2f} over "
                f"{len(held['held_out'])} task(s) the edit was not written "
                "against, so what improved is the tasks and not the skill")

    if previous:
        if previous.get("subject_model") != result["subject_model"]:
            problems.append(
                f"the previous result was measured on "
                f"{previous.get('subject_model')!r} and this one on "
                f"{result['subject_model']!r}, so the two deltas are not "
                "comparable and a model rollout must not read as a regression")
        else:
            before = (previous.get("delta") or {}).get("mean", 0.0)
            spread = (previous.get("delta") or {}).get("ci95") or [0.0, 0.0]
            floor = min(spread[0], before)
            if result["delta"]["mean"] < floor:
                problems.append(
                    f"the delta fell from {before:+.2f} to "
                    f"{result['delta']['mean']:+.2f}, below the previous "
                    f"result's own lower bound of {floor:+.2f}")
    return problems


def history_entries(doc: dict) -> list[dict]:
    """Every measured version, oldest first.

    `history` is the record ADR-37 asks for. A document written before the
    history existed is one entry, synthesised from its own top-level fields, so
    the first run after this lands compares against the number that was
    published rather than against nothing.
    """
    history = doc.get("history")
    if isinstance(history, list) and history:
        return [e for e in history if isinstance(e, dict)]
    if doc.get("delta") and doc.get("date"):
        return [summary_entry(doc)]
    return []


ENTRY_FIELDS = ("version", "date", "subject_model", "judge_model", "tasks",
                "repetitions", "verdict", "skill_md_sha256", "trigger",
                "spend_usd")


def summary_entry(result: dict, version: str = "", trigger: str = "") -> dict:
    """One history entry: what a version measured, and what asked for it."""
    entry = {"version": str(version or result.get("version") or ""),
             "trigger": trigger or str(result.get("trigger") or "")}
    for field in ENTRY_FIELDS:
        if field in ("version", "trigger"):
            continue
        if result.get(field) is not None:
            entry[field] = result[field]
    delta = result.get("delta") or {}
    entry["delta"] = {"mean": delta.get("mean"), "ci95": delta.get("ci95")}
    controls = result.get("controls")
    if controls:
        entry["controls_unchanged"] = bool(controls.get("unchanged"))
    return entry


def previous_measurement(previous: dict | None) -> dict | None:
    """The run this one is compared against, read from the history.

    Not the top level of the previous file. The top level is the newest summary
    and a file that was overwritten has no older number in it at all, which is
    the hole the append below closes: before this, two runs on the same day
    left the second one comparing itself against itself.

    A document written before the history existed has one entry synthesised
    from its own top-level fields, which is `tools/skill_triggers.py`'s rule
    and not a second one, so the first run after this lands still compares
    against the number that was published.
    """
    if not previous:
        return None
    entries = history_entries(previous)
    # No entries and no synthesisable summary means there is nothing to compare,
    # and the previous document itself is the honest fallback: it is what the
    # gate read until today.
    return entries[-1] if entries else previous


def appended_history(previous: dict | None, result: dict) -> list[dict]:
    """Every measurement of this skill, oldest first, with this run last.

    `history` is the key ADR-37 asks for, `tools/skill_triggers.py` has read it
    since 2026-09-30, and until today nothing in this repository wrote it. The
    writer belongs here because this is the only place a measurement is
    produced, and it appends because the Agent Memory Leaderboard's rule is the
    right one: a version may not be replaced because its result was
    unflattering. What code can enforce is that discarding a number takes a
    deliberate edit to a file rather than a second run of the harness.
    """
    history = list(history_entries(previous or {}))
    history.append(summary_entry(result))
    return history


def verdict_of(delta: float, low: float, high: float, min_delta: float) -> str:
    """What the numbers are allowed to be called.

    `gain` needs the lower bound above zero AND the point estimate at or above
    the pre-registered threshold. A delta that clears zero but not the threshold
    is `gain too small to matter`, which is a finding and not a pass, because a
    skill earns its place in the context window or it does not.
    """
    if high < 0:
        return "regression"
    if low <= 0:
        return "no gain"
    if delta < min_delta:
        return "gain too small to matter"
    return "gain"


# ------------------------------------------------------------------ the files

def skill_dir(slug: str, root: pathlib.Path | None = None) -> pathlib.Path:
    return (root or ROOT) / "skills" / slug


FRONTMATTER = re.compile(r"^---\n.*?\n---\n", re.S)


def body_of(raw: str) -> str:
    """A SKILL.md without its frontmatter. One function because two readers now
    want it: the with-arm loads the body, and the heading check resolves a
    task's `sections` against it."""
    match = FRONTMATTER.match(raw)
    return (raw[match.end():] if match else raw).strip()


def read_skill(slug: str) -> tuple[str, str]:
    """(body, sha256 of the whole file). The body is what the with-arm loads.

    The sha pins the result to the exact text that produced it, the same way the
    trigger-test receipts do. A skill edited after its eval has a result that
    describes an earlier revision, and the site has to be able to say so.
    """
    path = skill_dir(slug) / "SKILL.md"
    raw = path.read_text()
    return body_of(raw), hashlib.sha256(raw.encode()).hexdigest()


def skill_version(slug: str) -> str:
    """The version in `SKILL.md`'s frontmatter, or "".

    A history entry carries it because ADR-37's second trigger asks for edges
    recorded "since the skill's version date", and
    `tools/skill_triggers.py`'s `version_date` answers that by finding the
    history entry whose `version` matches the one in the frontmatter. An entry
    with no version is an entry that trigger cannot use.

    Parsed by `tools/skill_registrar.py`, which is the one frontmatter reader on
    the Python side: a second one written here is how `validated` and every
    claim id read as the empty string on every skill for eleven days (PR #133).
    """
    import skill_registrar as registrar

    path = skill_dir(slug) / "SKILL.md"
    if not path.exists():
        return ""
    fm, _ = registrar.split_frontmatter(path.read_text())
    return str(registrar.parse_frontmatter(fm).get("version") or "")


# The skill seat writes `evals/evals.json`, which is also the name the
# skill-creator plugin's own suites use. `evals/tasks.json` is accepted as an
# alias because this harness proposed that name first, on 2026-09-30, in the same
# window the skill seat was writing six suites under the other one. The suites
# that exist win; a harness that cannot read the tasks that were written is worth
# nothing.
TASK_FILENAMES = ("evals.json", "tasks.json")


def tasks_path(slug: str, root: pathlib.Path | None = None) -> pathlib.Path:
    evals = skill_dir(slug, root=root) / "evals"
    for name in TASK_FILENAMES:
        if (evals / name).exists():
            return evals / name
    return evals / TASK_FILENAMES[0]


def shown(path: pathlib.Path) -> str:
    """A path as a reader wants it: relative to the repository when it is inside
    it, absolute when it is not. `relative_to` raises on anything else, and a
    print statement is not worth an exception on the line after a measurement
    that cost money."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def results_path(slug: str) -> pathlib.Path:
    return skill_dir(slug) / "evals" / "results.json"


# ------------------------------------------------- the sections a task claims

# `sections` entered the suite contract on 2026-09-30, after a claim-id
# comparison passed two suites whose tasks exercised none of the section they
# named (INC-2026-09-30-eval-task-claims-unchecked). The field is the fix for a
# recorded incident, every task in all eight real suites carries it, and until
# today nothing read it: `grep -rn sections tools/skill_eval.py
# tools/panel_validator.py` returned nothing, so the coverage claims were
# exactly as unchecked as the claim ids they were written to replace.
#
# The suite's own contract (`skills/_validation/evals/README.md`, "Task
# coverage") asks for two checks and says in its own words which is which:
# "every string in `sections` is a heading of that SKILL.md, and every heading
# of that SKILL.md other than the Apply checklist and the caveats appears in at
# least one task's `sections`. Both are decidable with no model. A section with
# no task is what a per-section *Validation:* tag has to say out loud (ADR-38),
# so it is a finding rather than an error."
#
# So the first is in `conformance`, where a problem blocks a run, and the second
# is `uncovered_sections`, which no gate reads as a failure. The exemption list
# below is the contract's two and not one more. A heading this harness decided
# not to require coverage of would be the instrument deciding what a skill has
# to prove, which is the skill seat's call and ADR-38's; and the suites do not
# need the help, since the two skills whose provenance section looks unprovable
# ("Where the full text narrows our claim rows") each have a task for it.
SECTION_EXEMPT_PREFIXES = ("Apply", "Caveats")


def skill_headings(base: pathlib.Path) -> list[str] | None:
    """The `## ` headings of the SKILL.md beside this evals directory, or None.

    `None` means there is no SKILL.md to resolve against, which is a different
    answer from "it has no headings" and the two must never collapse: a suite
    built in a fixture directory makes no false coverage claim, and treating it
    as one would fail every caller that writes a suite to a tmpdir. A real skill
    whose SKILL.md is missing is already a finding of the registrar and of the
    provenance reviewer, both of which open the file this one cannot find.

    The headings come from `tools/panel_provenance.py`'s `sections`, which is
    the one `## ` reader in this repository. A second regex here is how
    `validated:` read as the empty string on every skill for eleven days.
    """
    path = base.parent / "SKILL.md"
    if not path.exists():
        return None
    import panel_provenance

    return panel_provenance.sections(body_of(path.read_text()))


def claimed_sections(spec: dict) -> set[str]:
    """Every heading any task in this suite says it exercises.

    A control carries an empty list by the contract's own instruction, and so
    does a treatment task that tests a boundary rather than a section, so an
    empty list is a deliberate statement and not a missing one. A task with no
    `sections` key at all is a suite written before 2026-09-30 making no
    coverage claim, which the coverage finding reports as uncovered sections
    rather than as a malformed task.
    """
    claimed = set()
    for task in spec.get("tasks") or []:
        names = task.get("sections")
        if isinstance(names, list):
            claimed.update(n for n in names if isinstance(n, str))
    return claimed


def uncovered_sections(spec: dict, slug: str,
                       base: pathlib.Path) -> list[str]:
    """Headings of this skill that no task claims. Findings, never errors.

    The second of the contract's two checks, and the one that catches the
    defect the field was added for. It returns strings rather than raising or
    appending to `conformance`'s list because the contract calls it a finding:
    a section with no task is a gap in what the suite proves, which ADR-38
    wants said out loud on the page, and it is not a reason the harness cannot
    run.
    """
    headings = skill_headings(base)
    if headings is None:
        return []
    claimed = claimed_sections(spec)
    return [f"{slug}: no task exercises the section {name!r}"
            for name in headings
            if not name.startswith(SECTION_EXEMPT_PREFIXES)
            and name not in claimed]


def coverage_counts(spec: dict, base: pathlib.Path) -> tuple[int, int]:
    """(sections a task claims, sections coverage is asked of). (0, 0) when
    there is no SKILL.md beside the suite, so a caller can tell "nothing to
    measure" from "nothing measured"."""
    headings = skill_headings(base)
    if headings is None:
        return 0, 0
    asked = [n for n in headings
             if not n.startswith(SECTION_EXEMPT_PREFIXES)]
    claimed = claimed_sections(spec)
    return sum(1 for n in asked if n in claimed), len(asked)


CHECK_TYPES = {"contains_all", "contains_none", "number_in_range",
               "json_parses", "command", "rubric", "tests_pass", "parses"}

# A task the skill seat wrote and this harness had never heard of is a bug in
# this harness, not in the task. `normalize` is the one place the two
# vocabularies meet, and everything below it speaks only the second one.
#
#   skill seat            here
#   ----------            ----
#   suite_version         contract
#   kind: control         control: true
#   form: prompt|project  kind: prompt|project
#   prompt                ask
#   files: {name: text}   files, written into the project copy and shown to both arms
#   check.criteria        rubric, with 0/1/2 anchors when the author gave them
#   check.type: rubric    rubric
#   check.type: parses    parses, a deterministic gate plus judged assertions
#   check.type: tests_pass  tests_pass, an exit code
#   check.type: number_in_range  the judge extracts, the range is arithmetic
#   subject_model (top level)    policy.subject, when it is a model id
#   judge (top level)            policy.judge, when it is a model id
#
# The last two rows are a mapping and not a rename, because the skill seat's
# own contract document (skills/_validation/evals/README.md) describes those
# two fields in prose and every suite written against it fills them in prose:
# `"subject_model": "kimi (ADR-32 funded account) by default; a Claude run is
# the monthly OKR benchmark"`. That sentence is documentation. Dialling it into
# the slot a model id goes in would send an English sentence to the provider,
# and `skill_triggers.subject_for` would print it on the library page as the
# model a skill was measured on. So the lift happens only when the value could
# be a model id at all, and the prose is kept where a reader can still see it.


def looks_like_a_model_id(value) -> bool:
    """Could this string be sent to a provider as a model name.

    Deliberately crude, and crude in the safe direction: a model id has no
    spaces, and a sentence does. Anything this returns False for is prose, and
    prose is kept as documentation rather than dialled.
    """
    return isinstance(value, str) and bool(value.strip()) and \
        not any(c.isspace() for c in value.strip())


def normalize(spec: dict) -> dict:
    """The skill seat's suite in this harness's vocabulary. Idempotent."""
    out = dict(spec)
    out["contract"] = spec.get("contract", spec.get("suite_version"))
    policy = dict(spec.get("policy") or {})
    for top, key in (("subject_model", "subject"), ("judge", "judge")):
        value = spec.get(top)
        if value is None or policy.get(key) is not None \
                or policy.get(key + "_described") is not None:
            continue
        if looks_like_a_model_id(value):
            policy[key] = value.strip()
        else:
            policy[key + "_described"] = value
    # No `policy.setdefault("repetitions", DEFAULT_REPS)`. It was here until
    # 2026-10-04 and it is the reason `conformance`'s rule-1 check below could
    # never fail: every suite arrived at the check with a repetitions count,
    # because this line had just written one. Rule 1 of
    # docs/product/skill-validation.md section V5 is that the policy is
    # pre-registered, so the one thing this function must not do is supply a
    # number the author did not. `DEFAULT_REPS` is still the default the CLI's
    # `--reps` documents and the number a suite should copy; it is no longer a
    # number a run can acquire by saying nothing.
    out["policy"] = policy
    tasks = []
    for raw in spec.get("tasks") or []:
        task = dict(raw)
        if task.get("kind") in ("treatment", "control"):
            task["control"] = task["kind"] == "control"
            task["kind"] = task.pop("form", "prompt")
        task.setdefault("kind", task.pop("form", "prompt"))
        if "ask" not in task and "prompt" in task:
            task["ask"] = task["prompt"]
        check = dict(task.get("check") or {})
        if check.get("type") == "rubric":
            task["rubric"] = [
                {"id": c.get("id"), "asks": c.get("criterion") or c.get("asks"),
                 "anchors": c.get("anchors")}
                for c in (check.get("criteria") or [])
            ]
            task.pop("check", None)
        elif check:
            task["check"] = check
        tasks.append(task)
    out["tasks"] = tasks
    return out


def unknown_models(policy: dict, slug: str) -> list[str]:
    """A registered model id this organization cannot call is not runnable.

    `pipeline/budget.py`'s table is the one list of models the crons may use,
    it is a dict in a file, and reading it costs no key and no dollar. So a
    typo or a prose placeholder in `policy.subject` is catchable by `--check`
    rather than at call time, three minutes and part of a cap into a run.
    """
    if not isinstance(policy, dict):
        return []
    try:
        import budget
    except Exception:                               # pragma: no cover
        return []
    out = []
    for key in ("subject", "judge"):
        name = policy.get(key)
        if name is None:
            continue
        if not looks_like_a_model_id(name) or name not in budget.MODELS:
            out.append(f"{slug}: policy.{key} is {name!r}, which is not a "
                       "model in pipeline/budget.py's table, so no run can "
                       "send it anywhere")
    return out


def conformance(spec: dict, slug: str, base: pathlib.Path) -> list[str]:
    """Everything wrong with one `tasks.json`. Empty means it can be run.

    Its own function so `--check` can be a CI gate over every skill's eval file
    without a key, a model or a dollar.

    Errors only. `uncovered_sections` is the other half of the suite contract's
    coverage rule and it returns findings, because the contract calls a section
    with no task a finding rather than an error and a gate that blocks on it
    would stop a suite from running over a gap in what it proves.
    """
    problems = []
    if spec.get("contract") not in SUITE_CONTRACTS:
        problems.append(f"{slug}: contract is {spec.get('contract')!r}, this "
                        f"harness speaks "
                        f"{' and '.join(str(c) for c in SUITE_CONTRACTS)}")
    if spec.get("skill") != slug:
        problems.append(f"{slug}: the file says skill {spec.get('skill')!r}")
    policy = spec.get("policy") or {}
    if not isinstance(policy, dict) or "repetitions" not in policy:
        problems.append(
            f"{slug}: policy.repetitions is not pre-registered, so the run "
            f'would choose its own n. Rule 1. Add `"policy": '
            f'{{"repetitions": {DEFAULT_REPS}, "subject": "{DEFAULT_SUBJECT}", '
            f'"judge": "{DEFAULT_JUDGE}", "min_delta": 0.2}}` to the file and '
            "pick the numbers deliberately, because a threshold chosen after "
            "the delta is not a threshold.")
    if policy.get("subject") and policy.get("subject") == policy.get("judge"):
        problems.append(f"{slug}: the subject and the judge are the same model")
    problems += unknown_models(policy, slug)
    # Opt-in, and then it is an error rather than a finding. A suite that
    # registered `require_certificates` has said its rubrics are tied to
    # verifiable certificates, and a run that proceeds anyway would be measuring
    # against a promise the file itself broke.
    if policy.get("require_certificates"):
        problems += certificate_problems(spec, slug)
        problems += exploit_problems(spec, slug)

    tasks = spec.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        problems.append(f"{slug}: no tasks")
        return problems

    seen = set()
    real = 0
    # Resolved once, because it opens a file and every task resolves against
    # the same list. `None` is "no SKILL.md beside this suite", and the loop
    # below makes no coverage claim at all in that case.
    headings = skill_headings(base)
    for task in tasks:
        tid = task.get("id")
        if not tid:
            problems.append(f"{slug}: a task has no id")
            continue
        if tid in seen:
            problems.append(f"{slug}: two tasks share the id {tid}")
        seen.add(tid)
        if not task.get("ask"):
            problems.append(f"{slug}/{tid}: no `ask`, so there is nothing to send")
        if not task.get("control") and not is_indicator(task):
            real += 1
        check = task.get("check")
        rubric = task.get("rubric")
        if not check and not rubric:
            problems.append(
                f"{slug}/{tid}: neither a hard check nor a rubric, so nothing "
                "scores it")
        if check:
            kind = check.get("type")
            if kind not in CHECK_TYPES:
                problems.append(f"{slug}/{tid}: check type {kind!r} is not one "
                                f"of {sorted(CHECK_TYPES)}")
            if kind in ("contains_all", "contains_none"):
                for pattern in check.get("patterns") or []:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        problems.append(f"{slug}/{tid}: {pattern!r} is not a "
                                        f"regular expression ({exc})")
                if not check.get("patterns"):
                    problems.append(f"{slug}/{tid}: {kind} with no patterns")
            if kind == "tests_pass":
                if not check.get("command"):
                    problems.append(f"{slug}/{tid}: tests_pass with no command")
                if not check.get("answer_path"):
                    problems.append(f"{slug}/{tid}: tests_pass needs "
                                    "answer_path, the file the answer is "
                                    "written to")
            if kind == "parses":
                if check.get("format") not in PARSES_FORMATS:
                    problems.append(f"{slug}/{tid}: `parses` format "
                                    f"{check.get('format')!r} is not one of "
                                    f"{list(PARSES_FORMATS)}")
                if not check.get("assertions"):
                    problems.append(f"{slug}/{tid}: parses with no assertions "
                                    "scores nothing but syntax")
            if kind == "number_in_range" and check.get("range"):
                low, high = check["range"]
                if low > high:
                    problems.append(f"{slug}/{tid}: range {check['range']} is "
                                    "inverted")
                if not check.get("extract"):
                    problems.append(f"{slug}/{tid}: number_in_range needs "
                                    "`extract`, which says what number to take "
                                    "out of the answer")
            if kind == "command":
                if task.get("kind") != "project":
                    problems.append(f"{slug}/{tid}: a command check needs "
                                    "kind: project and a project directory")
                if not task.get("answer_file"):
                    problems.append(f"{slug}/{tid}: a command check needs "
                                    "answer_file, the path the answer is "
                                    "written to inside the project copy")
        if rubric:
            for item in rubric:
                if not item.get("id") or not item.get("asks"):
                    problems.append(f"{slug}/{tid}: a rubric item needs an id "
                                    "and an `asks`")
                if item.get("section") and headings is not None \
                        and item["section"] not in headings:
                    problems.append(
                        f"{slug}/{tid}: criterion {item.get('id')!r} credits "
                        f"section {item['section']!r}, which is not a `## ` "
                        f"heading of {slug}/SKILL.md, so the per-section delta "
                        "it would produce names a section that does not exist")
            if task.get("exploit") and not exploit_answer(task):
                problems.append(f"{slug}/{tid}: `exploit` is present and holds "
                                "no answer text, so the exploit test would "
                                "score an empty string")
        if task.get("scored_in") and not is_indicator(task):
            problems.append(f"{slug}/{tid}: scored_in is "
                            f"{task['scored_in']!r}, and the only value this "
                            f"harness knows is {INDICATOR!r}")
        if task.get("control") and is_indicator(task):
            problems.append(f"{slug}/{tid}: a control and an indicator at once. "
                            "A control is a task the skill must not change and "
                            "an indicator is one only the skill can pass.")
        claims = task.get("sections")
        if claims is not None and not isinstance(claims, list):
            problems.append(f"{slug}/{tid}: sections is {claims!r}, and the "
                            "contract asks for a list of this skill's `## ` "
                            "headings")
        elif headings is not None:
            for name in claims or []:
                if name not in headings:
                    problems.append(
                        f"{slug}/{tid}: sections names {name!r}, which is not a "
                        f"`## ` heading of {slug}/SKILL.md. The contract asks "
                        "for the heading copied verbatim, so this is a typo or "
                        "a section renamed after the task was written, and "
                        "either way the coverage claim is false.")
        # A workspace is needed by the checks that run a command, and by nothing
        # else. A `project`-form task whose check is `parses` is the model
        # writing a file from a description, and there is nothing to copy.
        if (check or {}).get("type") in ("tests_pass", "command") \
                and not task.get("files"):
            project = base / (task.get("project") or "")
            if not task.get("project") or not project.is_dir():
                problems.append(f"{slug}/{tid}: this check runs a command, so "
                                "it needs inline `files` or a `project` "
                                f"directory, and {task.get('project')!r} is "
                                "neither")
    if real == 0:
        problems.append(f"{slug}: every task is a control, so there is nothing "
                        "the skill is being measured on")
    return problems


def load_tasks(slug: str, root: pathlib.Path | None = None
               ) -> tuple[dict, list[str]]:
    path = tasks_path(slug, root=root)
    if not path.exists():
        return {}, [f"{slug}: no evals/evals.json. Unmeasured, which is an "
                    "honest state and is never a pass (ADR-36: a skill with no "
                    "eval is status draft, never active)."]
    try:
        spec = normalize(json.loads(path.read_text()))
    except json.JSONDecodeError as exc:
        return {}, [f"{slug}: {path.name} is not JSON ({exc})"]
    return spec, conformance(spec, slug, path.parent)


def library_slugs(root: pathlib.Path | None = None) -> list[str]:
    base = (root or ROOT) / "skills"
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and p.name != "_validation")


def check_library(root: pathlib.Path | None = None) -> dict:
    """Every suite's conformance, as data. `--check` only prints it.

    Its own function so the classification can be tested without the live
    library deciding the answer. The test that asserts "a missing eval file is
    unmeasured and never a failure" was asserting the exit code of a scan over
    `skills/`, which made it a test of whether eight files written by another
    seat happened to be clean that day; it went red on 2026-10-04 for four real
    suite defects that have nothing to do with what it is named after.

    Exit codes, unchanged: 0 clean, 1 something is malformed, 2 something is
    unmeasured and nothing is malformed.
    """
    root = root or ROOT
    slugs = library_slugs(root)
    problems: list[str] = []
    findings: list[str] = []
    measured = covered = asked = 0
    certified = criteria = 0
    for slug in slugs:
        spec, found = load_tasks(slug, root=root)
        problems += found
        measured += 1 if spec and not found else 0
        if not spec:
            continue
        base = tasks_path(slug, root=root).parent
        findings += uncovered_sections(spec, slug, base)
        # ADR-40 items 5 and 6, reported beside the coverage gap they belong
        # with: a rubric nothing certifies, a rubric with no exploit test, and a
        # task that has never been audited are all "this number means less than
        # it looks like it means", which is what a finding says.
        findings += certificate_problems(spec, slug)
        findings += exploit_problems(spec, slug)
        findings += audit_problems(spec, base, slug)
        hit, of = coverage_counts(spec, base)
        covered += hit
        asked += of
        have, total = certificate_counts(spec)
        certified += have
        criteria += total
    lines = [f"{measured} of {len(slugs)} skills carry a conformant eval file"]
    if asked:
        lines.append(f"{covered} of {asked} sections are exercised by at least "
                     f"one task, excluding the Apply checklist and the caveats")
    if criteria:
        lines.append(f"{certified} of {criteria} rubric criteria are tied to a "
                     f"certificate a reader can check (ADR-40 item 5)")
    # Absent is unmeasured, not broken: the skill seat writes the tasks and
    # ADR-36 makes such a skill `draft`. A malformed file is a real failure.
    # The two are labelled differently on purpose, because a line reading
    # `failing` against a file nobody has written yet is how a report stops
    # being read.
    malformed = [p for p in problems if "no evals/evals.json" not in p]
    return {"slugs": slugs, "measured": measured, "problems": problems,
            "malformed": malformed, "findings": findings, "lines": lines,
            "sections": (covered, asked), "certificates": (certified, criteria),
            "exit": 1 if malformed else (2 if problems else 0)}


# ------------------------------------------------------------------ scoring

def hard_check(task: dict, answer: str, base: pathlib.Path, *,
               sandbox: str = "host", trajectory=None, arm: str = "",
               rep: int = 0) -> tuple[float, str]:
    """(1.0 or 0.0, why). The deterministic half, which needs no judge at all."""
    check = task["check"]
    kind = check["type"]

    if kind == "contains_all":
        missing = [p for p in check["patterns"]
                   if not re.search(p, answer, re.I | re.S)]
        return (0.0, f"missing {missing}") if missing else (1.0, "all present")

    if kind == "contains_none":
        found = [p for p in check["patterns"]
                 if re.search(p, answer, re.I | re.S)]
        return (0.0, f"present {found}") if found else (1.0, "none present")

    if kind == "json_parses":
        try:
            parsed = json.loads(answer)
        except json.JSONDecodeError as exc:
            return (0.0, f"not JSON ({exc})")
        missing = [k for k in check.get("required_keys") or []
                   if k not in parsed]
        return (0.0, f"missing keys {missing}") if missing else (1.0, "parsed")

    if kind == "number_in_range":
        found = re.search(check["pattern"], answer, re.I | re.S)
        if not found:
            return (0.0, "no number matched the pattern")
        try:
            value = float(found.group(1).replace(",", ""))
        except (IndexError, ValueError) as exc:
            return (0.0, f"pattern matched but no number in group 1 ({exc})")
        ok = check["low"] <= value <= check["high"]
        return (1.0 if ok else 0.0, f"{value} against "
                f"[{check['low']}, {check['high']}]")

    if kind == "command":
        return run_project_check(task, answer, base, check, sandbox=sandbox,
                                 trajectory=trajectory, arm=arm, rep=rep)

    return (0.0, f"unknown check type {kind!r}")


# --------------------------------------------------------------- the sandbox

def sandbox_image() -> str:
    return os.environ.get("SKILL_EVAL_SANDBOX_IMAGE") or SANDBOX_IMAGE_DEFAULT


def docker_available() -> tuple[bool, str]:
    """Is there a Docker daemon that will answer. (yes/no, the sentence why).

    `which docker` is not the question. A binary on PATH with no daemon behind it
    fails every command with the same exit code a failing test uses, which would
    read as the skill making no difference, symmetrically, in both arms.
    """
    exe = shutil.which("docker")
    if not exe:
        return (False, "docker is not on PATH")
    try:
        done = subprocess.run([exe, "version", "--format",
                               "{{.Server.Version}}"],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return (False, f"docker is on PATH and did not answer ({exc})")
    if done.returncode != 0:
        tail = (done.stdout + done.stderr).strip().splitlines()[-1:]
        return (False, "docker is on PATH and its daemon did not answer"
                + (": " + tail[0] if tail else ""))
    return (True, f"docker server {done.stdout.strip()}")


def sandbox_decision(mode: str) -> tuple[str, str]:
    """(where commands will run, the sentence that explains it).

    Three outcomes and the third is the point. `docker` asked for and absent is
    `refuse`, not a quiet fall back to the host: a suite that pre-registered a
    sandbox and got the host measured something else, and the whole contract of
    this file is that the result describes what ran.
    """
    if mode == "host":
        return ("host", "the run asked for the host, so commands run here with "
                        "a timeout and no container")
    ok, why = docker_available()
    if ok:
        return ("docker", f"{why}, image {sandbox_image()}, --network none")
    if mode == "docker":
        return ("refuse", f"this run asked for the Docker sandbox and {why}. "
                          "Pass --sandbox host to measure on the host instead, "
                          "and the result will say that is what happened")
    return ("host", f"{why}, so commands run on the host with a timeout. ADR-40 "
                    "item 4 wants the container, and this result says it did "
                    "not get one")


def docker_argv(command, work: pathlib.Path) -> list[str]:
    """The container a task's command runs in. One place, so one thing to read.

    A suite writes its command either as one shell string or as an argv list,
    and both forms predate this function. A string needs a shell inside the
    container; a list does not, and wrapping one in `sh -lc` would re-introduce
    the quoting the list form exists to avoid.
    """
    run = ["docker", "run", "--rm", "--network", "none",
           "--memory", SANDBOX_MEMORY, "--pids-limit", SANDBOX_PIDS,
           "--workdir", "/work", "--volume", f"{work}:/work",
           sandbox_image()]
    if isinstance(command, str):
        return run + ["/bin/sh", "-lc", command]
    return run + [str(part) for part in command]


def run_in_sandbox(command, work: pathlib.Path, timeout: int,
                   sandbox: str) -> dict:
    """Run one command and report everything about the run. Never raises.

    The return value is the trajectory entry ADR-40 item 4 asks to be logged, so
    it is built here rather than assembled by each caller: one shape, whichever
    check ran the command, and the exit code is in the same field either way.
    """
    started = time.monotonic()
    entry = {"command": command if isinstance(command, str)
                        else " ".join(str(part) for part in command),
             "sandbox": sandbox, "timeout_s": timeout,
             "network": "none" if sandbox == "docker" else "the host's"}
    if sandbox == "docker":
        argv = docker_argv(command, work)
        entry["image"] = sandbox_image()
        shell = False
    else:
        argv = command
        shell = isinstance(command, str)
    try:
        done = subprocess.run(argv, cwd=None if sandbox == "docker" else work,
                              shell=shell, capture_output=True, text=True,
                              env=None if sandbox == "docker" else command_env(),
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        entry.update({"exit_code": None, "outcome": "timed out",
                      "duration_s": round(time.monotonic() - started, 2)})
        return entry
    except OSError as exc:
        entry.update({"exit_code": None, "outcome": f"could not be run ({exc})",
                      "duration_s": round(time.monotonic() - started, 2)})
        return entry
    tail = (done.stdout + done.stderr).strip().splitlines()
    entry.update({"exit_code": done.returncode,
                  "outcome": "exit 0" if done.returncode == 0
                             else f"exit {done.returncode}",
                  "duration_s": round(time.monotonic() - started, 2),
                  "output_tail": tail[-6:]})
    return entry


def log_trajectory(trajectory, task: dict, arm: str, rep: int, answer: str,
                   entry: dict) -> None:
    """Append one executable repetition to the run's trajectory, or do nothing.

    The answer is recorded by hash and length rather than in full. The whole
    answer is already in the eval's own notes path and a trajectory file that
    carried a thousand model answers would stop being opened, which is the way a
    log becomes decoration.
    """
    if trajectory is None:
        return
    trajectory.append(dict(entry, task=task.get("id"), arm=arm, rep=rep + 1,
                           answer_sha256=hashlib.sha256(
                               answer.encode("utf-8")).hexdigest()[:16],
                           answer_chars=len(answer)))


def workspace(task: dict, check: dict, base: pathlib.Path,
              tmp: pathlib.Path) -> pathlib.Path:
    """The task's project, materialized fresh. Inline files, then a directory.

    Fresh every repetition, because a task that leaves state behind scores the
    repetition after it, and these suites hand the model a reference
    implementation and an acceptance gate that it must not be able to edit for
    the next run.
    """
    work = tmp / "project"
    if task.get("project") and (base / task["project"]).is_dir():
        shutil.copytree(base / task["project"], work)
    else:
        work.mkdir(parents=True)
    for source in (task.get("files") or {}, check.get("files") or {}):
        for name, text in source.items():
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
    return work


# A command that could not run at all is not a failing test. `127` is the shell's
# "command not found", and a harness that scored it 0 would report a broken
# environment as a real result, symmetrically in both arms, which reads as "no
# gain" and is the most expensive wrong answer this file can give. Such a task is
# reported unmeasured instead, and `score_answer` returns None for it.
UNRUNNABLE = 127


def command_env() -> dict:
    """The environment a suite's command runs in, with `python` made to exist.

    The suites are written by an agent and say `python -m pytest`. Debian's
    containers ship `python3` and no `python`, so every `tests_pass` task scored
    `exit 127` on the first machine this harness ran on. A shim beats asking six
    task files to spell the interpreter differently, and it is not a lie: the
    interpreter it points at is the one running this file.
    """
    import os

    shim = pathlib.Path(tempfile.mkdtemp()) / "bin"
    shim.mkdir(parents=True)
    link = shim / "python"
    if not shutil.which("python"):
        link.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
        link.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{shim}:{env.get('PATH', '')}"
    return env


def tests_pass(task: dict, answer: str, base: pathlib.Path, check: dict, *,
               sandbox: str = "host", trajectory=None, arm: str = "",
               rep: int = 0) -> tuple[float, str]:
    """The answer is written to `answer_path` and `command` decides. Exit 0 wins.

    The command runs inside a fresh copy of the project with a timeout, and in a
    container when this run has one (ADR-40 item 4). This is the cheapest and
    least arguable score in the harness: the tests either pass or they do not,
    and no judge is involved.

    Every repetition that gets here appends one entry to the run's trajectory,
    which is the record ADR-40 item 4 asks for. The entry says where the command
    ran, what it exited with, how long it took and which answer produced it, so
    an executable result can be audited without re-running it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        work = workspace(task, check, base, pathlib.Path(tmp))
        target = work / check["answer_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(extract_code(answer))
        entry = run_in_sandbox(check["command"], work,
                               int(check.get("timeout", 180)), sandbox)
        entry["answer_path"] = check["answer_path"]
        log_trajectory(trajectory, task, arm, rep, answer, entry)
        code = entry.get("exit_code")
        if code == 0:
            return (1.0, f"exit 0 ({entry['sandbox']})")
        if code is None:
            # Timed out is a real zero: a test suite that never finishes has not
            # passed. A command that could not be started at all is unmeasured,
            # because that is a fact about this machine and not about the answer.
            if entry["outcome"] == "timed out":
                return (0.0, f"the command timed out after {entry['timeout_s']}s")
            return (None, f"the command could not be run: {entry['outcome']}")
        detail = f"exit {code} ({entry['sandbox']}): " + \
            " | ".join(entry.get("output_tail") or [])
        if code == UNRUNNABLE:
            return (None, "UNMEASURED, " + detail)
        return (0.0, detail)


PARSES_FORMATS = ("python_module", "json")


def parses(answer: str, check: dict) -> tuple[bool, str]:
    """Does the answer parse in the format the task named. A gate, not a score.

    A gate rather than a grader on purpose: an artifact that does not parse is not
    a bad artifact, it is not an artifact, and averaging it against the prose
    assertions would let a half-written file score for the half that reads well.
    """
    import ast

    code = extract_code(answer)
    fmt = check.get("format")
    if fmt == "python_module":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            return (False, f"does not parse as Python: {exc}")
        return (True, "parses")
    if fmt == "json":
        try:
            json.loads(code)
        except json.JSONDecodeError as exc:
            return (False, f"does not parse as JSON: {exc}")
        return (True, "parses")
    return (False, f"unknown format {fmt!r}")


def statements_prompt(task: dict, answer: str, statements: list[dict],
                      extract: str = "") -> str:
    """The judge's message for prose assertions, and for one extraction.

    The same blinding rule as the rubric: the judge is told the task and the
    answer and nothing about which arm produced it.
    """
    lines = ["The task the answer was given:", "", task["ask"], "",
             "The answer:", "", answer, ""]
    if extract:
        lines += [f"First, extract this number from the answer: {extract}. "
                  "Report it as `value`, or null when the answer does not give "
                  "one.", ""]
    lines += ["Then decide each statement about the answer, strictly yes or no:",
              ""]
    for item in statements:
        lines.append(f"- {item['id']}: {item['statement']}")
    lines += ["", 'Reply as {"value": <number or null>, "verdicts": '
              '{"<id>": "yes"|"no"}, "why": "one sentence"}.']
    return "\n".join(lines)


def run_project_check(task: dict, answer: str, base: pathlib.Path, check: dict,
                      *, sandbox: str = "host", trajectory=None,
                      arm: str = "", rep: int = 0) -> tuple[float, str]:
    """Copy the project, drop the answer in, run the command, read the exit code.

    A copy every time, because a task that leaves state behind scores the
    repetition after it. The command inherits no arguments from this process and
    is given a timeout, so a model that writes an infinite loop costs one
    timeout rather than the run.
    """
    source = base / task["project"]
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "project"
        shutil.copytree(source, work)
        target = work / task["answer_file"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(extract_code(answer))
        entry = run_in_sandbox(check["run"], work,
                               int(check.get("timeout", 120)), sandbox)
        entry["answer_path"] = task["answer_file"]
        log_trajectory(trajectory, task, arm, rep, answer, entry)
        code = entry.get("exit_code")
        if code == 0:
            return (1.0, f"exit 0 ({entry['sandbox']})")
        if code is None:
            return (0.0, f"the check {entry['outcome']}")
        return (0.0, f"exit {code} ({entry['sandbox']}): "
                + " | ".join(entry.get("output_tail") or []))


def extract_code(answer: str) -> str:
    """The first fenced block in the answer, or the whole answer.

    A model asked for a file writes a fenced block around it more often than not,
    and a project check that wrote the prose too would fail every time for a
    reason that has nothing to do with the skill.
    """
    fence = re.search(r"```[a-zA-Z0-9_+-]*\n(.*?)```", answer, re.S)
    return fence.group(1) if fence else answer


def criterion_score(verdict, anchors: dict | None) -> float:
    """One criterion's score in [0, 1].

    An anchored criterion is scored on its own scale and normalized by its top
    anchor, which is how the skill seat's suites are written: 0, 1 and 2, where 2
    is the behaviour the skill teaches. A criterion with no anchors is yes or no.
    Anything the judge did not answer, or answered outside the scale, is zero.
    Silence is never a pass.
    """
    text = str(verdict).strip().lower()
    if anchors:
        try:
            keys = sorted(int(k) for k in anchors)
        except (TypeError, ValueError):
            keys = []
        top = max(keys) if keys else 0
        if top <= 0:
            return 0.0
        try:
            value = float(text)
        except ValueError:
            # A judge that answered yes on an anchored criterion has not used
            # the scale, and reading it as the top anchor would be generous by
            # construction. Read it as the second-best, and never as full marks.
            return (top - 1) / top if text.startswith("y") else 0.0
        return max(0.0, min(value, top)) / top
    return 1.0 if text.startswith("y") or text == "1" else 0.0


# The key a score that belongs to the whole task is filed under. A hard check
# produces one number for the task rather than one per criterion, and ADR-40
# item 7 still wants it attributed to a section, so it is credited to every
# section the task claims.
WHOLE_TASK = "__task__"


def criterion_scores(verdicts: dict, rubric: list[dict]) -> dict:
    """Each rubric criterion's own score, by criterion id.

    Split out of `rubric_score` so ADR-40 item 7 can attribute a delta to a
    section: the per-criterion numbers were computed here all along and then
    averaged away, which is exactly the credit a section-level finding needs.
    """
    return {item["id"]: criterion_score(verdicts.get(item["id"]),
                                        item.get("anchors"))
            for item in rubric}


def rubric_score(verdicts: dict, rubric: list[dict]) -> tuple[float, str]:
    scores = [criterion_score(verdicts.get(item["id"]), item.get("anchors"))
              for item in rubric]
    got = sum(scores)
    detail = ", ".join("{}={:.2f}".format(item["id"], value)
                       for item, value in zip(rubric, scores))
    return (mean(scores),
            f"{got:.2f} of {len(rubric)} criteria ({detail})")


# ------------------------------------------- certificates, exploits, the audit

# ADR-40 item 5, and the measurement behind it is the reason it is a rule rather
# than a preference: generated rubrics with no tie to a verifiable certificate in
# the task were exploited 8 to 26 percent of the time, and up to 36 percent under
# stress; certificate-faithful ones 0 percent (C476, C479). A certificate is a
# test, a number or a named artifact, so a criterion that says "does the answer
# show good judgement" has nothing behind it and a criterion that says "does the
# answer cite the 4 to 30 point regression" has a number.
#
# Findings rather than errors, and that choice has a precedent in this file. The
# eight real suites were written before this rule existed; a gate that failed
# them all would block every revision of every skill on a debt no revision
# created, which is how a check gets turned off (the same argument the trigger
# test's clause in tools/skill_gate.py makes out loud). A suite opts in with
# `policy.require_certificates`, and then it is an error.

def criterion_certificate(item: dict) -> dict | None:
    cert = item.get("certificate")
    return cert if isinstance(cert, dict) else None


def certificate_problems(spec: dict, slug: str) -> list[str]:
    """Rubric criteria with nothing verifiable behind them. Findings."""
    out = []
    for task in spec.get("tasks") or []:
        for item in task.get("rubric") or []:
            cert = criterion_certificate(item)
            if cert is None:
                out.append(
                    f"{slug}/{task.get('id')}: rubric criterion "
                    f"{item.get('id')!r} names no certificate, so the judge is "
                    "the only thing standing between it and an answer written "
                    "to please a judge. Add `certificate`: "
                    f"{{\"kind\": one of {list(CERTIFICATE_KINDS)}, \"names\": "
                    "the test, the number or the artifact it is tied to}")
                continue
            if cert.get("kind") not in CERTIFICATE_KINDS:
                out.append(f"{slug}/{task.get('id')}: criterion "
                           f"{item.get('id')!r} has certificate kind "
                           f"{cert.get('kind')!r}, not one of "
                           f"{list(CERTIFICATE_KINDS)}")
            if not str(cert.get("names") or "").strip():
                out.append(f"{slug}/{task.get('id')}: criterion "
                           f"{item.get('id')!r} has a certificate kind and "
                           "names nothing, which is the same gap with a label "
                           "on it")
    return out


def certificate_counts(spec: dict) -> tuple[int, int]:
    """(criteria with a certificate, criteria in total)."""
    have = total = 0
    for task in spec.get("tasks") or []:
        for item in task.get("rubric") or []:
            total += 1
            cert = criterion_certificate(item)
            if cert and cert.get("kind") in CERTIFICATE_KINDS \
                    and str(cert.get("names") or "").strip():
                have += 1
    return (have, total)


def exploit_answer(task: dict) -> str:
    """The canned answer that games this task's rubric, or an empty string.

    "Each rubric ships with an exploit test: an answer that games the rubric
    must not score." The author writes it, because only the author knows which
    shortcut their own rubric is open to. A plausible-sounding answer with none
    of the certificates in it is the shape.
    """
    raw = task.get("exploit")
    if isinstance(raw, dict):
        return str(raw.get("answer") or "")
    return str(raw or "")


def exploit_problems(spec: dict, slug: str) -> list[str]:
    """Rubric tasks with no exploit test. Findings, for the same reason."""
    return [f"{slug}/{task.get('id')}: a rubric and no `exploit`, so nothing "
            "proves the rubric cannot be gamed. ADR-40 item 5 asks every rubric "
            "to ship an answer that games it, which must score zero"
            for task in spec.get("tasks") or []
            if task.get("rubric") and not exploit_answer(task)]


def run_exploits(judge, tasks: list[dict], base: pathlib.Path) -> dict:
    """Score every exploit answer. Anything above zero is the finding.

    The subject is never asked: the exploit answer is written by the task's
    author and the question is what the *rubric* does with it. So this costs one
    judge call per rubric task that ships one, and judging is on the free tier.
    """
    rows, worst = [], 0.0
    for task in tasks:
        canned = exploit_answer(task)
        if not canned:
            continue
        score, why = score_answer(task, canned, judge, base)
        score = 0.0 if score is None else score
        worst = max(worst, score)
        rows.append({"id": task["id"], "score": round(score, 4),
                     "clean": score <= EXPLOIT_CEILING, "why": why})
    if not rows:
        return {"ran": 0, "ceiling": EXPLOIT_CEILING, "verdict": "not run",
                "reads": "no task shipped an exploit answer, so nothing here "
                         "says the rubrics cannot be gamed"}
    bad = [r for r in rows if not r["clean"]]
    return {"ran": len(rows), "ceiling": EXPLOIT_CEILING,
            "max_score": round(worst, 4), "per_task": rows,
            "exploited": [r["id"] for r in bad],
            "verdict": "exploited" if bad else "clean",
            "reads": (f"{len(bad)} of {len(rows)} rubrics scored an answer "
                      f"written to game them, worst {worst:.2f}") if bad
                     else f"{len(rows)} exploit answer(s) all scored zero"}


# ADR-40 item 6's audit. One pass per task, ever, so it is a file beside the
# suite rather than a cost on every run. PACT's point (C561) is that an
# ambiguous or gameable task produces a number whose meaning nobody can state,
# and that the cheapest moment to find out is before the task has been counted.

def audit_path(base: pathlib.Path) -> pathlib.Path:
    return base / AUDIT_FILENAME


def read_audit(base: pathlib.Path) -> dict:
    path = audit_path(base)
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    tasks = doc.get("tasks")
    return tasks if isinstance(tasks, dict) else {}


def audited_clean(record: dict) -> bool:
    return all(str(record.get(name) or "").strip().lower() == "ok"
               for name, _ in AUDIT_QUESTIONS)


def audit_problems(spec: dict, base: pathlib.Path, slug: str) -> list[str]:
    """Tasks that have never been audited, and audits that found something."""
    records = read_audit(base)
    out = []
    for task in spec.get("tasks") or []:
        tid = task.get("id")
        record = records.get(tid)
        if not isinstance(record, dict):
            out.append(f"{slug}/{tid}: never audited for ambiguity, "
                       "gameability and realism. ADR-40 item 6 asks for one "
                       "audit per task before it counts: run "
                       f"`python3 tools/skill_eval.py --skill {slug} --audit`")
            continue
        for name, _ in AUDIT_QUESTIONS:
            verdict = str(record.get(name) or "").strip().lower()
            if not verdict:
                out.append(f"{slug}/{tid}: the audit does not answer {name!r}")
            elif verdict != "ok":
                out.append(f"{slug}/{tid}: the audit found {name} "
                           f"({record.get(name)}): "
                           f"{record.get('notes') or 'no note'}")
    return out


AUDIT_SYSTEM = (
    "You are auditing an evaluation task before anybody is scored on it. You "
    "are not answering it. For each question reply exactly \"ok\" when the task "
    "is clean, or one short sentence naming the problem when it is not. Reply "
    "in JSON as {\"ambiguity\": ..., \"gameability\": ..., \"realism\": ..., "
    "\"notes\": \"one sentence\"}."
)


def audit_prompt(task: dict) -> str:
    lines = ["The task:", "", render_ask(task), ""]
    if task.get("rubric"):
        lines += ["How it is scored, by a second model against these criteria:",
                  ""]
        for item in task["rubric"]:
            lines.append(f"- {item.get('id')}: {item.get('asks')}")
            cert = criterion_certificate(item)
            if cert:
                lines.append(f"    tied to a {cert.get('kind')}: "
                             f"{cert.get('names')}")
        lines.append("")
    elif task.get("check"):
        lines += ["How it is scored, mechanically:", "",
                  json.dumps(task["check"], sort_keys=True)[:1200], ""]
    lines += ["The questions:", ""]
    for name, question in AUDIT_QUESTIONS:
        lines.append(f"- {name}: {question}")
    return "\n".join(lines)


def run_audit(judge, spec: dict, base: pathlib.Path, judge_model: str,
              today: str, reaudit: bool = False) -> dict:
    """Audit every task that has not been audited, and write the file."""
    records = dict(read_audit(base))
    fresh = 0
    for task in spec.get("tasks") or []:
        tid = task["id"]
        if tid in records and not reaudit:
            continue
        reply = judge.ask(AUDIT_SYSTEM, audit_prompt(task), JUDGE_MAX_TOKENS)
        records[tid] = {"date": today, "judge": judge_model,
                        "notes": str(reply.get("notes") or "")[:400]}
        for name, _ in AUDIT_QUESTIONS:
            records[tid][name] = str(reply.get(name) or "")[:300]
        fresh += 1
    doc = {"contract": 1, "skill": spec.get("skill"), "generated_at": today,
           "auditor": judge_model, "questions": dict(AUDIT_QUESTIONS),
           "tasks": records}
    path = audit_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return {"written": shown(path), "audited_now": fresh,
            "tasks": len(records),
            "clean": sum(1 for r in records.values() if audited_clean(r))}


# ADR-40 item 6's other half: the length-bias check (C934). Score the same
# content at two lengths and see whether the number moves. The padding restates
# nothing and adds no information, which is the whole point: any score change is
# the judge responding to length rather than to content.

PADDING_PREFACE = ("Restated below in full, adding nothing and changing "
                   "nothing, for a reader who wants it twice:")


def padded(answer: str) -> str:
    return f"{answer}\n\n{PADDING_PREFACE}\n\n{answer}"


def length_bias(judge, tasks: list[dict], answers: dict, base: pathlib.Path,
                sample: int = LENGTH_BIAS_SAMPLE) -> dict:
    """Does the judge score the same content differently when it is longer.

    Rubric tasks only, because a hard check cannot have a length preference: a
    regular expression that matches matches twice as often in a doubled answer
    and the score is identical either way. Sampled, because this is a question
    about the instrument and two pairs answer it as well as ten.
    """
    rows = []
    for task in tasks:
        if len(rows) >= sample:
            break
        if not task.get("rubric"):
            continue
        answer = answers.get((task["id"], "with")) or ""
        if not answer.strip():
            continue
        short, _ = score_answer(task, answer, judge, base)
        long_, _ = score_answer(task, padded(answer), judge, base)
        if short is None or long_ is None:
            continue
        rows.append({"id": task["id"], "short": round(short, 4),
                     "long": round(long_, 4),
                     "shift": round(long_ - short, 4),
                     "chars": [len(answer), len(padded(answer))]})
    if not rows:
        return {"pairs": 0, "verdict": "not run",
                "reads": "no rubric task produced an answer to re-score, so "
                         "the judge's length preference is unmeasured"}
    shifts = [r["shift"] for r in rows]
    worst = max(abs(s) for s in shifts)
    flagged = worst > LENGTH_BIAS_FLAG
    return {"pairs": len(rows), "threshold": LENGTH_BIAS_FLAG,
            "mean_shift": round(mean(shifts), 4),
            "max_abs_shift": round(worst, 4), "per_task": rows,
            "verdict": "length-sensitive" if flagged else "no length effect",
            "reads": (f"the same content scored {mean(shifts):+.2f} on average "
                      f"when doubled in length over {len(rows)} pair(s), worst "
                      f"{worst:.2f} against a {LENGTH_BIAS_FLAG:.2f} threshold")}


# ------------------------------------------------------- credit to the section

def criterion_sections(task: dict, criterion_id: str) -> list[str]:
    """Which skill sections this criterion's score is evidence about.

    ADR-40 item 7, DRACO's per-step credit (C40) and the role-level credit read
    from traces (C1442). The criterion may name its own section, which is the
    precise form; failing that the task's `sections` list is used, which is the
    field the suite contract already requires and every real suite already
    fills. A criterion credited to three sections is weak evidence about each of
    them, and the per-section record says how many criteria stood behind it so a
    reader can see that rather than infer it.
    """
    for item in task.get("rubric") or []:
        if item.get("id") == criterion_id and item.get("section"):
            return [str(item["section"])]
    return [str(s) for s in (task.get("sections") or [])]


def section_credit(per_task: list[dict], tasks: list[dict]) -> dict:
    """Per-section with-arm and without-arm means, their delta and its spread.

    Computed from the per-criterion scores the run recorded, not from the task
    deltas, so a task whose rubric spans two sections contributes each criterion
    to the section that criterion is about. Controls and indicators are left
    out: a control's whole purpose is that the skill must not move it, and
    averaging it into a section would dilute the section's own evidence with a
    number designed to be zero.
    """
    by_id = {t["id"]: t for t in tasks}
    buckets: dict[str, dict] = {}
    for row in per_task:
        if row.get("control") or row.get("indicator"):
            continue
        task = by_id.get(row["id"])
        if task is None:
            continue
        for cid, with_scores in (row.get("credit", {}).get("with") or {}).items():
            without = (row.get("credit", {}).get("without") or {}).get(cid) or []
            if not with_scores or not without:
                continue
            names = criterion_sections(task, cid) if cid != WHOLE_TASK \
                else [str(s) for s in (task.get("sections") or [])]
            for name in names:
                slot = buckets.setdefault(name, {
                    "with": [], "without": [], "deltas": [],
                    "tasks": [], "criteria": []})
                slot["with"] += with_scores
                slot["without"] += without
                slot["deltas"].append(mean(with_scores) - mean(without))
                if row["id"] not in slot["tasks"]:
                    slot["tasks"].append(row["id"])
                label = row["id"] if cid == WHOLE_TASK else f"{row['id']}/{cid}"
                slot["criteria"].append(label)
    out = {}
    for name, slot in sorted(buckets.items()):
        delta = mean(slot["with"]) - mean(slot["without"])
        out[name] = {
            "with_mean": round(mean(slot["with"]), 4),
            "without_mean": round(mean(slot["without"]), 4),
            "delta": round(delta, 4),
            "spread": spread_of(slot["deltas"]),
            "samples": len(slot["with"]),
            "tasks": slot["tasks"],
            "criteria": slot["criteria"],
            # Reserved for ADR-39. Ursa's per-section survival signal is the
            # second axis of ADR-40's refinement loop and it does not arrive
            # from this harness, so the key exists, it is null, and the reader
            # on the skill's page can tell "nobody has measured this" from
            # "nobody acted on this" without guessing.
            "survival": None,
        }
    return out


# ADR-40 refinement item 2: an edit must raise the held-out differential score,
# rather than the score on the tasks it was written against (SkillOpt, C865).
# The harness cannot know which tasks an edit was written against, so it is told:
# either by the task declaring the skill version it was authored alongside, or by
# `--written-against` on the run that measures the edit. Both are recorded, so a
# gate reading the result can tell a real held-out set from an empty one.

def written_against(task: dict, declared: set[str], version: str) -> bool:
    """Was this task written against the revision under test.

    Both halves must be non-empty to match. A task with no `written_for` and a
    run with no version string are not the same thing, and reading two blanks as
    a match made every task count as written-against, which empties the held-out
    set and turns ADR-40's generalization check into a refusal to measure.
    """
    if task["id"] in declared:
        return True
    declared_for = str(task.get("written_for") or "").strip()
    return bool(declared_for) and declared_for == str(version or "").strip()


def heldout_block(per_task: list[dict], tasks: list[dict], declared: set[str],
                  version: str, reps: int) -> dict:
    """The delta over the tasks this revision was not written against."""
    by_id = {t["id"]: t for t in tasks}
    graded = [r for r in per_task
              if not r.get("control") and not r.get("indicator")
              and r["with_scores"] and r["without_scores"]]
    held, written = [], []
    for row in graded:
        task = by_id.get(row["id"]) or {}
        (written if written_against(task, declared, version) else held
         ).append(row)
    block = {"version": version,
             "declared_written_against": sorted(declared),
             "written_against": [r["id"] for r in written],
             "held_out": [r["id"] for r in held]}
    if not held:
        block.update({"verdict": "no held-out set",
                      "reads": "every graded task counts as one this revision "
                               "was written against, so nothing here is "
                               "evidence that the edit generalizes"})
        return block
    delta, low, high = bootstrap_delta(held)
    block.update({"delta": {"mean": delta, "ci95": [low, high]},
                  "spread": spread_of([r["delta"] for r in held]),
                  "pass_at": pass_rates(held, "with_scores", reps),
                  "verdict": "holds" if delta > 0 else "does not hold",
                  "reads": f"{delta:+.2f} over {len(held)} held-out task(s), "
                           f"95% CI {low:+.2f} to {high:+.2f}"})
    return block

# ------------------------------------------------------------------ the models

class Subject:
    """The model under test, and the judge, behind one small interface.

    Both go through `pipeline/llm.py`, which already owns the fallback walk, the
    spend cap measured from the provider's usage block, and the 429 backoff that
    does not honour Moonshot's 1-second concurrency hint. Nothing new talks HTTP
    here, and the press's client is not touched.

    Both arms are asked for `{"answer": "..."}`. A JSON wrapper is not how a user
    would ask, and it is identical in both arms, which is the property that
    matters: the confound is held constant rather than removed, the same way the
    temperature and the reservation are.
    """

    def __init__(self, model: str, env, cap, available=None):
        import llm

        self.llm = llm
        self.model = model
        self.env = env
        self.cap = cap
        self.available = available

    def ask(self, system: str, user: str, max_tokens: int) -> dict:
        # The seed goes only where the provider honours one. `pipeline/llm.py`
        # omits the key entirely when it is None, so a Moonshot call is byte for
        # byte the call it was before ADR-40, which is what keeps this change
        # out of docs/agents/runtime-changes.md's blast radius.
        answer, _ = self.llm.ask_json([self.model], system, user, self.env,
                                      self.cap, max_completion=max_tokens,
                                      temperature=EVAL_TEMPERATURE,
                                      available=self.available,
                                      seed=SUBJECT_SEED
                                      if seedable(self.model) else None)
        return answer


class ScriptedSubject:
    """The smoke test's model. Answers from a table, spends nothing, needs no key.

    `--smoke` exists because every other way of proving this harness works costs
    money and a provider. It runs the whole pipeline, both arms, the checks, the
    judge, the statistics and the written result, against a model whose answers
    are fixed, so a broken scorer or a broken bootstrap fails on a laptop.
    """

    def __init__(self, with_answer: str, without_answer: str,
                 judges_on: str = "harness"):
        self.with_answer = with_answer
        self.without_answer = without_answer
        self.judges_on = judges_on
        self.calls = 0

    def ask(self, system: str, user: str, max_tokens: int) -> dict:
        self.calls += 1
        if system.startswith(JUDGE_SYSTEM[:40]):
            # A scripted judge that answered yes to everything would make every
            # rubric task read as no difference, which would prove nothing about
            # the rubric path. This one grades on one word, and the word is in
            # one arm's answer only, so the rubric path discriminates the way a
            # real judge would.
            ids = re.findall(r"^- ([\w-]+):", user, re.M)
            answer = user.split("The answer:", 1)[-1]
            hit = self.judges_on.lower() in answer.lower()
            return {"verdicts": {i: ("yes" if hit else "no") for i in ids},
                    "why": "scripted"}
        loaded = "# The skill under test" in system
        return {"answer": self.with_answer if loaded else self.without_answer}


def judge_prompt(task: dict, answer: str) -> str:
    lines = ["The task the answer was given:", "", task["ask"], "",
             "The answer:", "", answer, "", "The criteria:", ""]
    for item in task["rubric"]:
        lines.append(f"- {item['id']}: {item['asks']}")
        for key in sorted((item.get("anchors") or {}), key=lambda k: str(k)):
            lines.append(f"    {key} = {item['anchors'][key]}")
    return "\n".join(lines)


# ------------------------------------------------------------------ the run

def window_conflict(now: dt.datetime) -> str:
    """The reserved Kimi window `now` falls inside, or an empty string.

    Moonshot's organization concurrency is 1 for this account. An eval run is
    dozens of calls in a row, so starting one inside the press's band or either
    corpus job's window takes that job's slot away, and the job that meets a 429
    loses its run. That is failure 2 of
    INC-2026-09-24-press-provider-migration, and it is the reason this is a
    refusal rather than a warning.
    """
    import llm

    minute = now.hour * 60 + now.minute
    for label, (start, end) in llm.KIMI_WINDOWS.items():
        if start <= minute < end:
            return label
    return ""


def render_ask(task: dict) -> str:
    """The user message. Identical in both arms, files included.

    A project task hands the model the files it is working against, and it has to
    see them, so they go in the message rather than on a disk it cannot read. The
    same text goes to both arms, which is the property the whole design rests on.
    """
    files = task.get("files") or {}
    if not files:
        return task["ask"]
    parts = [task["ask"], "", "The files in the project:"]
    for name in sorted(files):
        parts += ["", f"{name}:", "```", files[name].rstrip(), "```"]
    return "\n".join(parts)


def score_answer(task: dict, answer: str, judge, base: pathlib.Path, *,
                 credit: dict | None = None, sandbox: str = "host",
                 trajectory=None, arm: str = "", rep: int = 0
                 ) -> tuple[float, str]:
    """One answer's score in [0, 1], by whichever instrument the task named.

    The order matters. Everything deterministic is decided here without a model,
    and the judge is asked only for what cannot be computed: a rubric verdict, a
    prose assertion about an artifact, and the one extraction a
    `number_in_range` task needs before its arithmetic can run.
    """
    check = task.get("check") or {}
    kind = check.get("type")

    if task.get("rubric"):
        verdicts = judge.ask(JUDGE_SYSTEM, judge_prompt(task, answer),
                             JUDGE_MAX_TOKENS).get("verdicts") or {}
        per = criterion_scores(verdicts, task["rubric"])
        if credit is not None:
            credit.update(per)
        return rubric_score(verdicts, task["rubric"])

    if kind == "tests_pass":
        score, why = tests_pass(task, answer, base, check, sandbox=sandbox,
                                trajectory=trajectory, arm=arm, rep=rep)
        if credit is not None and score is not None:
            credit[WHOLE_TASK] = score
        return (score, why)

    if kind == "parses":
        ok, why = parses(answer, check)
        statements = check.get("assertions") or []
        if not ok:
            return (0.0, why)
        if not statements:
            return (1.0, why)
        reply = judge.ask(JUDGE_SYSTEM,
                          statements_prompt(task, extract_code(answer),
                                            statements),
                          JUDGE_MAX_TOKENS)
        verdicts = reply.get("verdicts") or {}
        hits = [criterion_score(verdicts.get(a["id"]), None) for a in statements]
        if credit is not None:
            credit.update({a["id"]: h for a, h in zip(statements, hits)})
        return (mean(hits), f"parses, {int(sum(hits))} of {len(hits)} assertions")

    if kind == "number_in_range" and check.get("extract"):
        # The suites describe the number in prose ("the count of challenger
        # episodes the answer says to budget"), so extraction needs a reader and
        # the comparison does not. The judge reads, the arithmetic decides, and
        # the secondary assertions are scored beside it rather than folded in,
        # because the suite's own pass condition says a right number with wrong
        # reasoning has to stay visible.
        statements = check.get("secondary_assertions") or []
        reply = judge.ask(JUDGE_SYSTEM,
                          statements_prompt(task, answer, statements,
                                            extract=check["extract"]),
                          JUDGE_MAX_TOKENS)
        low, high = check.get("range") or [float("-inf"), float("inf")]
        value = reply.get("value")
        try:
            in_range = 1.0 if low <= float(value) <= high else 0.0
        except (TypeError, ValueError):
            in_range = 0.0
            value = None
        verdicts = reply.get("verdicts") or {}
        hits = [criterion_score(verdicts.get(a["id"]), None) for a in statements]
        parts = [in_range] + hits
        if credit is not None:
            credit[WHOLE_TASK] = in_range
            credit.update({a["id"]: h for a, h in zip(statements, hits)})
        return (mean(parts),
                f"value {value!r} against [{low}, {high}] ({'in' if in_range else 'out'}), "
                f"{int(sum(hits))} of {len(hits)} secondary")

    if check:
        score, why = hard_check(task, answer, base, sandbox=sandbox,
                                trajectory=trajectory, arm=arm, rep=rep)
        if credit is not None and score is not None:
            credit[WHOLE_TASK] = score
        return (score, why)

    return (0.0, "nothing scores this task")


def task_row(task: dict) -> dict:
    """The empty per-task record. One shape, whichever pass fills it."""
    deterministic = (task.get("check") or {}).get("type") in ("tests_pass",
                                                              "command")
    return {"id": task["id"], "control": bool(task.get("control")),
            "indicator": is_indicator(task),
            "demoted": bool(task.get("demoted")),
            "sections": list(task.get("sections") or []),
            "scored_by": "rubric" if task.get("rubric")
                         else ("hard check" if deterministic else "mixed"),
            "with_scores": [], "without_scores": [], "notes": [],
            "credit": {"with": {}, "without": {}},
            "unmeasured": 0}


def arm_pass(subject, judge, task: dict, system: str, reps: int,
             base: pathlib.Path, rows: dict, arm: str, *,
             sandbox: str = "host", trajectory=None, kept=None) -> None:
    """One arm of one task, `reps` times, written into `rows`.

    Factored out of `run_task` because ADR-40 item 2 runs the bare arm first,
    over every task, before the with-arm exists: the selection pass and the
    measurement pass have to be the same code or the scores the selection
    produced cannot honestly be reused as the without-arm's samples.
    """
    bucket = f"{arm}_scores"
    ask = render_ask(task)
    for rep in range(reps):
        reply = subject.ask(system, ask, SUBJECT_MAX_TOKENS)
        answer = str(reply.get("answer") or "")
        credit: dict = {}
        score, why = score_answer(task, answer, judge, base, credit=credit,
                                  sandbox=sandbox, trajectory=trajectory,
                                  arm=arm, rep=rep)
        if kept is not None:
            kept[(task["id"], arm)] = answer
        if score is None:
            # Unmeasured, not zero. The repetition is dropped from both the
            # arm and the count, and the note says why, so a task that could
            # not be run shows up as a smaller n rather than as a bad result.
            rows["unmeasured"] += 1
            rows["notes"].append(f"{arm} rep {rep + 1}: unmeasured ({why})")
            continue
        rows[bucket].append(score)
        for cid, value in credit.items():
            rows["credit"][arm].setdefault(cid, []).append(value)
        rows["notes"].append(f"{arm} rep {rep + 1}: {score:.2f} ({why})")


def with_system_for(skill_body: str) -> str:
    return SUBJECT_SYSTEM + "\n\n# The skill under test\n\n" + skill_body


def bare_pass(subject, judge, tasks: list[dict], reps: int,
              base: pathlib.Path, *, sandbox: str = "host", trajectory=None,
              kept=None) -> dict:
    """ADR-40 item 2's bare-first pass: the without-skill arm, over every task.

    This runs before the skill is ever loaded, which is the only order in which
    differential selection is honest. Selecting tasks after seeing both arms
    would be choosing the comparison from the comparison's own result, and the
    scores it produced would be the same scores the delta is computed from.

    Every score here is kept and reused as the without-arm's samples, so the
    pass costs nothing beyond the calls the measurement needed anyway. The
    repetition count is the pre-registered one for the same reason: a selection
    made at n of 1 and a measurement made at n of 3 would be selecting on noise
    and then measuring against it.
    """
    out = {}
    for task in tasks:
        rows = task_row(task)
        arm_pass(subject, judge, task, SUBJECT_SYSTEM, reps, base, rows,
                 "without", sandbox=sandbox, trajectory=trajectory, kept=kept)
        out[task["id"]] = rows
    return out


# The bare score at or above which a task is not differential. One, because the
# ADR's words are "tasks it already passes are controls" and a task the bare
# subject passes every time is one. A task it passes twice in three is partial,
# it stays graded, and the spread reports the noise.
DIFFERENTIAL_CEILING = 1.0


def differential_selection(tasks: list[dict], bare: dict,
                           ceiling: float = DIFFERENTIAL_CEILING) -> dict:
    """Which tasks the delta is computed on, and which became controls.

    ADR-40 item 2: only tasks the bare subject fails or scores partial on count,
    and the ones it already passes are controls. C412's contrastive pairing is
    the reason, and the practical reason is arithmetic: a task both arms pass
    every time contributes a delta of exactly zero to the mean, so leaving it in
    the graded set drags the measured effect toward zero by however many such
    tasks the suite happens to hold. It is not a neutral observation, it is a
    denominator.

    Marks the task dicts in place and returns the record the result carries.
    A demoted task keeps running in both arms, because a control is a task the
    skill must not change and that claim needs the with-arm too.
    """
    demoted, graded, kept_controls = [], [], []
    for task in tasks:
        row = bare.get(task["id"])
        if task.get("control"):
            kept_controls.append(task["id"])
            continue
        if is_indicator(task):
            continue
        if row is None or not row["without_scores"]:
            graded.append(task["id"])
            continue
        bare_mean = mean(row["without_scores"])
        if bare_mean >= ceiling:
            task["control"] = True
            task["demoted"] = True
            demoted.append({"id": task["id"], "bare_mean": round(bare_mean, 4),
                            "n": len(row["without_scores"])})
        else:
            graded.append(task["id"])
    return {"ceiling": ceiling, "graded": graded,
            "declared_controls": kept_controls,
            "demoted_to_control": demoted,
            "reads": f"{len(graded)} differential task(s), "
                     f"{len(demoted)} the bare subject already passed, "
                     f"{len(kept_controls)} declared control(s)"}


def run_task(subject, judge, task: dict, skill_body: str, reps: int,
             base: pathlib.Path, *, bare: dict | None = None,
             sandbox: str = "host", trajectory=None, kept=None) -> dict:
    """One task, both arms, `reps` times each.

    `bare` is the without-arm this task already has, from the bare-first pass.
    When it is given the without-arm is not asked again: those scores were
    produced by the same code against the same prompt at the same n, and paying
    twice for them would double the cost of every run to measure nothing new.
    """
    rows = bare if bare is not None else task_row(task)
    rows["control"] = bool(task.get("control"))
    rows["demoted"] = bool(task.get("demoted"))
    arm_pass(subject, judge, task, with_system_for(skill_body), reps, base,
             rows, "with", sandbox=sandbox, trajectory=trajectory, kept=kept)
    if bare is None:
        arm_pass(subject, judge, task, SUBJECT_SYSTEM, reps, base, rows,
                 "without", sandbox=sandbox, trajectory=trajectory, kept=kept)

    rows["with_mean"] = round(mean(rows["with_scores"]), 4)
    rows["without_mean"] = round(mean(rows["without_scores"]), 4)
    rows["delta"] = round(rows["with_mean"] - rows["without_mean"], 4)
    rows["spread"] = {"with": spread_of(rows["with_scores"]),
                      "without": spread_of(rows["without_scores"])}
    return rows


# A task the without-arm cannot possibly pass. Stolen, with the reasoning, from
# Anthropic's own `claude plugin eval`, which excludes such graders from the
# score in BOTH arms and reports them in the with-arm as indicators only
# (code.claude.com/docs/en/plugin-evals, read 2026-09-30). The argument is
# exact and it applies to this harness as written: a check like "the answer
# cites the 4 to 30 point regression" can only pass when the skill is loaded,
# because the number is in the skill. Scoring it pushes the without-arm toward
# zero and inflates the delta by however many such tasks the suite holds. The
# task file declares it, because only the author knows which checks are of that
# kind.
INDICATOR = "with_only"


def is_indicator(task: dict) -> bool:
    return str(task.get("scored_in") or "").strip() == INDICATOR


def summarize(slug: str, sha: str, spec: dict, per_task: list[dict],
              subject_model: str, judge_model: str, reps: int, spend: float,
              today: str, version: str = "", *, sandbox: str = "host",
              sandbox_why: str = "", exploit: dict | None = None,
              length: dict | None = None, differential: dict | None = None,
              declared_written_against: set[str] | None = None,
              trajectory: dict | None = None) -> dict:
    """The result document. This shape is the contract site/app/skills/README.md
    describes, and nothing renders a number this function did not compute."""
    measured = [t for t in per_task if t["with_scores"] and t["without_scores"]]
    unmeasured = [t for t in per_task if t not in measured]
    graded = [t for t in measured
              if not t["control"] and not t.get("indicator")]
    controls = [t for t in measured if t["control"]]
    indicators = [t for t in measured if t.get("indicator")]
    policy = spec.get("policy") or {}
    min_delta = float(policy.get("min_delta", 0.0))
    # pass@k's k is the pre-registered one or the repetition count, because
    # pass@k at k greater than n is a number about repetitions that never ran.
    pass_k = min(int(policy.get("pass_at_k") or reps), reps)

    delta, low, high = bootstrap_delta(graded)
    all_binary = all(s in (0.0, 1.0) for t in graded
                     for s in t["with_scores"] + t["without_scores"])

    def arm(key: str) -> dict:
        scores = [s for t in graded for s in t[key]]
        out = {"n": len(scores), "mean": round(mean(scores), 4),
               # ADR-40 item 3. The interval below is the uncertainty of this
               # mean; the spread is how much the tasks disagreed with each
               # other, and a tight interval around a mean of wildly different
               # tasks is the number this field exists to stop anyone quoting.
               "spread": spread_of([mean(t[key]) for t in graded]),
               "pass_at": pass_rates(graded, key, pass_k)}
        if all_binary:
            successes = int(sum(scores))
            out["successes"] = successes
            out["interval95"] = list(clopper_pearson(successes, len(scores)))
            out["reads"] = f"{successes} of {len(scores)}"
        return out

    result = {
        "contract": RESULT_CONTRACT,
        "skill": slug,
        "skill_md_sha256": sha,
        "version": version,
        "date": today,
        "subject_model": subject_model,
        "judge_model": judge_model,
        "repetitions": reps,
        "tasks": len(graded),
        "control_tasks": len(controls),
        "indicator_tasks": len(indicators),
        "unmeasured_tasks": [t["id"] for t in unmeasured],
        "scored_by_hard_check": sum(1 for t in graded
                                    if t["scored_by"] == "hard check"),
        "spend_usd": round(spend, 4),
        "with_skill": arm("with_scores"),
        "without_skill": arm("without_scores"),
        "delta": {"mean": delta, "ci95": [low, high],
                  "method": f"clustered bootstrap over {len(graded)} tasks and "
                            f"{reps} repetitions, {BOOTSTRAP_DRAWS} draws, seed "
                            f"{BOOTSTRAP_SEED}"},
        "min_delta_registered": min_delta,
        "verdict": verdict_of(delta, low, high, min_delta),
        "policy": policy,
        "per_task": per_task,
        "harness": "tools/skill_eval.py",
        # ADR-40 item 1. What was held constant, and what this provider would
        # not let the run pin.
        "ablation": ablation_manifest(subject_model, judge_model, reps,
                                      sandbox),
        # ADR-40 item 7. A delta attributed to a section rather than to a file,
        # which is what makes a per-section validation tag measurable.
        "section_deltas": section_credit(per_task, spec.get("tasks") or []),
        # Reserved for ADR-39's revealed-preference axis. Ursa writes it; this
        # harness only promises the key exists and is honest about being empty.
        "survival": None,
    }
    result["delta"]["spread"] = spread_of([t["delta"] for t in graded])
    if sandbox_why:
        result["ablation"]["pinned"]["sandbox_why"] = sandbox_why
    if differential is not None:
        result["differential"] = differential
    if exploit is not None:
        result["exploit_test"] = exploit
    if length is not None:
        result["length_bias"] = length
    if trajectory is not None:
        result["trajectory"] = trajectory
    result["heldout"] = heldout_block(
        per_task, spec.get("tasks") or [], set(declared_written_against or ()),
        version, reps)
    if indicators:
        # Reported, never scored. `fires` is the with-arm rate, which is the only
        # number an indicator can honestly produce.
        result["indicators"] = [
            {"id": t["id"], "fires": t["with_mean"],
             "n": len(t["with_scores"])} for t in indicators]
    if controls:
        c_delta, c_low, c_high = bootstrap_delta(controls)
        result["controls"] = {"tasks": len(controls), "delta": c_delta,
                              "ci95": [c_low, c_high],
                              "unchanged": abs(c_delta) < 0.1}
    return result


def render(result: dict) -> str:
    """What a person reads. Every number carries its n, or it does not print."""
    d = result["delta"]
    lines = [
        f"{result['skill']}, {result['date']}",
        f"  subject {result['subject_model']}, judged by "
        f"{result['judge_model']}",
        f"  {result['tasks']} tasks, {result['repetitions']} repetitions per "
        f"arm, {result['scored_by_hard_check']} scored by a hard check",
    ]
    for label, key in (("with the skill", "with_skill"),
                       ("without it", "without_skill")):
        arm = result[key]
        if "reads" in arm:
            lines.append(f"  {label:16} {arm['reads']}, 95% CI "
                         f"{arm['interval95'][0]:.2f} to "
                         f"{arm['interval95'][1]:.2f}")
        else:
            lines.append(f"  {label:16} mean {arm['mean']:.2f} over n="
                         f"{arm['n']}")
    lines.append(f"  delta            {d['mean']:+.2f}, 95% CI "
                 f"{d['ci95'][0]:+.2f} to {d['ci95'][1]:+.2f}")
    lines.append(f"  verdict          {result['verdict']}")
    if result.get("controls"):
        c = result["controls"]
        moved = ("unchanged" if c["unchanged"] else
                 "MOVED, which means the skill is changing answers it should "
                 "not touch")
        noun = "task" if c["tasks"] == 1 else "tasks"
        lines.append(f"  controls         {c['tasks']} {noun}, delta "
                     f"{c['delta']:+.2f}, {moved}")
    for key, label in (("with_skill", "with the skill"),
                       ("without_skill", "without it")):
        at = (result.get(key) or {}).get("pass_at")
        if at:
            lines.append(f"  {label:16} {at['reads']}")
    spread = (result.get("delta") or {}).get("spread")
    if spread and spread.get("n", 0) > 1:
        lines.append(f"  task spread      sd {spread['sd']:.2f} over "
                     f"{spread['n']} tasks, {spread['min']:+.2f} to "
                     f"{spread['max']:+.2f}. A tight interval around tasks "
                     f"that disagree is not agreement")
    diff = result.get("differential")
    if diff:
        lines.append(f"  differential     {diff['reads']}")
    held = result.get("heldout")
    if held:
        lines.append(f"  held out         {held['reads']}")
    exploit = result.get("exploit_test")
    if exploit:
        lines.append(f"  exploit test     {exploit['verdict']}, "
                     f"{exploit['reads']}")
    length = result.get("length_bias")
    if length:
        lines.append(f"  length bias      {length['verdict']}, "
                     f"{length['reads']}")
    sections = result.get("section_deltas") or {}
    if sections:
        lines.append(f"  per section      {len(sections)} section(s) carried "
                     f"judged evidence")
        for name, row in sorted(sections.items(),
                                key=lambda kv: kv[1]["delta"], reverse=True):
            lines.append(f"    {row['delta']:+.2f}  sd {row['spread']['sd']:.2f} "
                         f"over {row['samples']} samples  {name}")
    traj = result.get("trajectory")
    if traj and traj.get("entries"):
        lines.append(f"  trajectory       {traj['entries']} command run(s) in "
                     f"the {traj['sandbox']} sandbox, logged to "
                     f"{traj.get('path') or 'this result'}")
    unpinned = (result.get("ablation") or {}).get("unpinned") or []
    for line in unpinned:
        lines.append(f"  not pinned       {line}")
    lines.append(f"  spend            ${result['spend_usd']:.4f}")
    if result.get("trigger"):
        lines.append(f"  asked for by     {result['trigger']}")
    history = result.get("history") or []
    if len(history) > 1:
        lines.append(f"  on the record    {len(history)} measurements, this one "
                     f"last. The earlier ones are not replaced.")
        before = history[-2]
        mean = (before.get("delta") or {}).get("mean")
        if mean is not None:
            lines.append(f"  version {before.get('version') or '?'} measured "
                         f"{float(mean):+.2f} on {before.get('date')}, "
                         f"{before.get('subject_model')}")
    if result["verdict"] != "gain":
        lines.append("  This is a finding, not a failure of the harness. "
                     "ADR-36: a skill whose eval shows no gain is retired with "
                     "the numbers.")
    return "\n".join(lines)


# The smoke suite. Every path the harness has, including the ones ADR-40 added,
# against a model whose answers are fixed. The scripted judge grades on the word
# "harness", which appears in the with-arm's answer and not in the without-arm's,
# so the rubric path discriminates the way a real judge would.
SMOKE_SPEC = {
    "contract": SUITE_CONTRACTS[-1],
    "skill": "_smoke",
    "policy": {"repetitions": 3, "min_delta": 0.2, "pass_at_k": 3},
    "tasks": [
        {"id": "hard-check", "ask": "What should we do?",
         "sections": ["Harness before weights"],
         "check": {"type": "contains_all", "patterns": ["harness"]}},
        {"id": "rubric", "ask": "What should we do?",
         "sections": ["Harness before weights"],
         "rubric": [{"id": "names-the-move", "asks": "Does it name the move?",
                     "section": "Debug one agent at a time",
                     "certificate": {"kind": "artifact",
                                     "names": "the named move in the answer"}}],
         # An answer written to please a judge and to carry none of the
         # certificate. It must score zero (ADR-40 item 5, C476 and C479).
         "exploit": {"answer": "I would follow best practice, align the "
                               "stakeholders and iterate toward excellence."}},
        {"id": "control", "control": True, "ask": "What is 2 + 2?",
         "check": {"type": "contains_all", "patterns": ["4"]}},
        # Graded on paper and not differential in fact: the bare subject answers
        # it every time, so ADR-40 item 2 demotes it to a control rather than
        # letting its guaranteed zero delta dilute the measured effect.
        {"id": "already-passed", "ask": "What is 2 + 2, again?",
         "sections": ["Harness before weights"],
         "check": {"type": "contains_all", "patterns": ["4"]}},
        # The executable path: a real file written into a real workspace and a
        # real command deciding the score, with the run logged (item 4).
        {"id": "executable", "ask": "Write the module.",
         "sections": ["Debug one agent at a time"],
         "check": {"type": "tests_pass", "answer_path": "answer.txt",
                   "command": "grep -q harness answer.txt"}},
    ],
}


def smoke() -> int:
    """The whole harness against a scripted model. No key, no network, no money."""
    subject = ScriptedSubject(
        with_answer="Change the harness before the weights. 4.",
        without_answer="Fine-tune the model on the stronger one's traces. 4.")
    base = pathlib.Path(".")
    tasks = SMOKE_SPEC["tasks"]
    trajectory: list[dict] = []
    kept: dict = {}
    sandbox, sandbox_why = sandbox_decision("host")
    bare = bare_pass(subject, subject, tasks, 3, base, sandbox=sandbox,
                     trajectory=trajectory, kept=kept)
    differential = differential_selection(tasks, bare)
    per_task = [run_task(subject, subject, task, "the skill body", 3, base,
                         bare=bare.get(task["id"]), sandbox=sandbox,
                         trajectory=trajectory, kept=kept)
                for task in tasks]
    exploit = run_exploits(subject, tasks, base)
    length = length_bias(subject, tasks, kept, base)
    result = summarize("_smoke", "0" * 64, SMOKE_SPEC, per_task,
                       "scripted/with-and-without", "scripted/judge", 3, 0.0,
                       dt.date.today().isoformat(), sandbox=sandbox,
                       sandbox_why=sandbox_why, exploit=exploit, length=length,
                       differential=differential,
                       trajectory={"entries": len(trajectory),
                                   "sandbox": sandbox, "path": "not written"})
    print(render(result))
    print(f"\n{subject.calls} scripted calls, $0.00 spent")
    # What this asserts is the arithmetic, not the model. With this scripted pair
    # the with-arm passes everything graded, the without-arm passes nothing
    # graded, the declared control is identical in both arms, and the task the
    # bare subject already answered is a control it was not declared as.
    # Anything else is a bug in the scorer, the selection, the bootstrap or the
    # verdict rule.
    sections = result["section_deltas"]
    checks = {
        "the with-arm sweeps and the without-arm scores nothing graded":
            result["with_skill"]["reads"] == "9 of 9"
            and result["without_skill"]["reads"] == "0 of 9",
        "the exact binomial bound is the finite-sample one":
            result["with_skill"]["interval95"][0] == 0.6637,
        "the delta is a gain and the controls did not move":
            result["delta"]["mean"] == 1.0 and result["verdict"] == "gain"
            and result["controls"]["unchanged"],
        "a task the bare subject already passes becomes a control":
            [r["id"] for r in differential["demoted_to_control"]]
            == ["already-passed"]
            and result["tasks"] == 3 and result["control_tasks"] == 2,
        "pass@1 and pass@k are reported beside each other":
            result["with_skill"]["pass_at"]["pass_at_1"] == 1.0
            and result["with_skill"]["pass_at"]["k"] == 3
            and result["without_skill"]["pass_at"]["pass_at_k"] == 0.0,
        "the delta carries its spread over tasks":
            result["delta"]["spread"]["n"] == 3
            and result["delta"]["spread"]["sd"] == 0.0,
        "an answer written to game the rubric scores zero":
            exploit["verdict"] == "clean" and exploit["ran"] == 1
            and exploit["max_score"] == 0.0,
        "the judge does not score the same content differently when doubled":
            length["verdict"] == "no length effect" and length["pairs"] == 1,
        "the executable task ran a real command and logged it":
            len(trajectory) == 6
            and {e["sandbox"] for e in trajectory} == {"host"}
            and sorted({e["exit_code"] for e in trajectory}) == [0, 1],
        "credit lands on the section and not on the file":
            sections["Harness before weights"]["delta"] == 1.0
            and sections["Debug one agent at a time"]["delta"] == 1.0
            and sections["Debug one agent at a time"]["criteria"]
            == ["rubric/names-the-move", "executable"]
            and "already-passed" not in
            sections["Harness before weights"]["tasks"],
        "every section reserves Ursa's survival signal and claims nothing":
            all(row["survival"] is None for row in sections.values())
            and result["survival"] is None,
        "the held-out set is every graded task when none was named":
            result["heldout"]["verdict"] == "holds"
            and sorted(result["heldout"]["held_out"])
            == ["executable", "hard-check", "rubric"],
        "the ablation says what it could not pin":
            result["ablation"]["pinned"]["temperature"] == EVAL_TEMPERATURE
            and len(result["ablation"]["unpinned"]) == 2,
    }
    for label, ok in checks.items():
        print(("ok:   " if ok else "FAIL: ") + label)
    if all(checks.values()):
        print("smoke: the harness measures what it should")
        return 0
    print("smoke: THE HARNESS IS WRONG")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skill")
    ap.add_argument("--check", action="store_true",
                    help="every skill's eval file conforms. No model, no cost.")
    ap.add_argument("--plan", action="store_true",
                    help="the calls this run would make, and the cost")
    ap.add_argument("--smoke", action="store_true",
                    help="run the harness against a scripted model")
    ap.add_argument("--reps", type=int, default=0,
                    help="override the pre-registered repetitions, and say so")
    ap.add_argument("--subject", default="")
    ap.add_argument("--judge", default="")
    ap.add_argument("--cap", type=float, default=CAP_USD)
    ap.add_argument("--force", action="store_true",
                    help="run inside a reserved Kimi window anyway")
    ap.add_argument("--gate", action="store_true",
                    help="exit 1 unless the verdict is a gain (ADR-37's gate)")
    ap.add_argument("--sandbox", choices=SANDBOX_MODES, default="auto",
                    help="where an executable task's command runs. `auto` "
                         "takes the Docker sandbox when a daemon answers and "
                         "says so in the result when it does not; `docker` "
                         "refuses to run without one (ADR-40 item 4)")
    ap.add_argument("--no-differential", action="store_true",
                    help="grade every task, including the ones the bare "
                         "subject already passes. ADR-40 item 2 says not to, "
                         "and the result records that this run overrode it")
    ap.add_argument("--no-exploit-test", action="store_true",
                    help="skip the exploit answers. The result says so, and "
                         "ADR-37's gate reads a skipped exploit test as "
                         "unmeasured rather than as clean")
    ap.add_argument("--no-length-check", action="store_true",
                    help="skip the judge's length-bias check (ADR-40 item 6)")
    ap.add_argument("--written-against", default="",
                    help="comma-separated task ids this revision's edit was "
                         "written against. They are reported and excluded from "
                         "the held-out delta, which is the number ADR-40's "
                         "refinement item 2 gates on")
    ap.add_argument("--audit", action="store_true",
                    help="audit each task once for ambiguity, gameability and "
                         "realism, write evals/audit.json, and run nothing "
                         "else (ADR-40 item 6)")
    ap.add_argument("--reaudit", action="store_true",
                    help="with --audit, audit tasks that already have a record")
    ap.add_argument("--trigger", default="",
                    help="what asked for this run: one of ADR-37's four "
                         "triggers, or a sentence. It is recorded against this "
                         "version in the history and it is what the skill's "
                         "page shows as the reason for the revision.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()

    if args.check:
        report = check_library()
        for line in report["lines"]:
            print(line)
        for line in report["problems"]:
            print(("failing: " if line in report["malformed"]
                   else "unmeasured: ") + line)
        # Findings print after the problems and never change the exit code. The
        # suite contract says a section with no task is a finding, so this gate
        # reports it and passes.
        for line in report["findings"]:
            print("finding: " + line)
        return report["exit"]

    if not args.skill:
        ap.error("--skill, --check or --smoke")

    import os

    spec, problems = load_tasks(args.skill)
    for line in problems:
        print(f"failing: {line}")
    if problems:
        return 1

    policy = spec.get("policy") or {}
    subject_model = args.subject or policy.get("subject") or DEFAULT_SUBJECT
    judge_model = args.judge or policy.get("judge") or DEFAULT_JUDGE
    # A suite that described its models in prose instead of registering them
    # has not chosen them, and this run has. Say which, rather than printing a
    # model id that looks pre-registered because it is printed next to one.
    for key, described, used in (("subject", "subject_described", subject_model),
                                 ("judge", "judge_described", judge_model)):
        if policy.get(described) and not policy.get(key):
            print(f"note: the suite describes its {key} in prose "
                  f"({policy[described]!r}) and registers none, so this run "
                  f"chose {used}. The result records what ran, and rule 1 "
                  f"wants `policy.{key}` to be the model id itself.")
    reps = args.reps or int(policy.get("repetitions") or DEFAULT_REPS)
    if args.reps:
        print(f"note: repetitions overridden to {reps}; the file registered "
              f"{policy.get('repetitions')}, and the result says so")

    if subject_model == judge_model:
        print(f"refusing to run: the subject and the judge are both "
              f"{subject_model}. ADR-36 requires them to differ, and a model "
              "grading its own answer is the oldest way to measure nothing.")
        return 1

    graded = [t for t in spec["tasks"] if not t.get("control")]
    calls = len(spec["tasks"]) * reps * 2
    print(f"{args.skill}: {len(graded)} graded tasks, "
          f"{len(spec['tasks']) - len(graded)} controls, {reps} repetitions, "
          f"{calls} subject calls on {subject_model}, judged by {judge_model}")

    import llm

    if args.plan:
        print(llm.calls_within(args.cap, 3_500, SUBJECT_MAX_TOKENS,
                               subject_model))
        print("plan only, nothing was sent")
        return 0

    conflict = window_conflict(dt.datetime.utcnow())
    if conflict and llm.budget().provider_of(subject_model) == "moonshot":
        if not args.force:
            print(f"refusing to run: it is inside {conflict}'s reserved window "
                  "and Moonshot's organization concurrency is 1, so this run "
                  "would take that job's slot (failure 2 of "
                  "INC-2026-09-24-press-provider-migration). Wait, or pass "
                  "--force if you know that job is not running.")
            return 1
        print(f"warning: running inside {conflict}'s window under --force")

    body, sha = read_skill(args.skill)
    cap = llm.Cap(args.cap, label=f"eval {args.skill}")
    available, notes = llm.usable_models([subject_model, judge_model],
                                        os.environ)
    for note in notes:
        print(f"availability: {note}")
    subject = Subject(subject_model, os.environ, cap, available)
    judge = Subject(judge_model, os.environ, cap, available)

    base = tasks_path(args.skill).parent
    today = dt.date.today().isoformat()

    if args.audit:
        # ADR-40 item 6. One pass, written to a file, and nothing is scored:
        # auditing the tasks and measuring the skill in the same run would let a
        # task that the audit found gameable count in the same result.
        report = run_audit(judge, spec, base, judge_model, today, args.reaudit)
        print(f"audited {report['audited_now']} task(s) this run, "
              f"{report['clean']} of {report['tasks']} clean; "
              f"written to {report['written']}")
        for line in audit_problems(spec, base, args.skill):
            print("finding: " + line)
        print(f"\n{cap}")
        return 0

    sandbox, sandbox_why = sandbox_decision(args.sandbox)
    print(f"sandbox: {sandbox_why}")
    if sandbox == "refuse":
        return 1

    trajectory: list[dict] = []
    kept: dict = {}
    per_task = []
    stopped = ""
    differential = None
    try:
        # ADR-40 item 2's bare-first pass. The without-skill arm runs over every
        # task before the skill exists in any prompt, the selection is made from
        # those scores, and the scores are then reused as the without-arm's
        # samples rather than paid for twice.
        print(f"  the bare subject first, {len(spec['tasks'])} task(s)...")
        bare = bare_pass(subject, judge, spec["tasks"], reps, base,
                         sandbox=sandbox, trajectory=trajectory, kept=kept)
        if args.no_differential:
            differential = {"ceiling": None, "overridden": True,
                            "reads": "differential selection was overridden by "
                                     "--no-differential, so tasks the bare "
                                     "subject already passes are still graded "
                                     "and the delta is pulled toward zero by "
                                     "however many of those the suite holds"}
        else:
            differential = differential_selection(spec["tasks"], bare)
            print(f"  differential: {differential['reads']}")
        for task in spec["tasks"]:
            print(f"  {task['id']}, with the skill...")
            per_task.append(run_task(subject, judge, task, body, reps, base,
                                     bare=bare.get(task["id"]),
                                     sandbox=sandbox, trajectory=trajectory,
                                     kept=kept))
    except llm.CapReached as exc:
        # The cap is not a failure and a run that hits it must not throw away
        # what it measured. The tasks already finished are a smaller eval,
        # honestly labelled, and the result says where it stopped.
        stopped = (f"the ${args.cap:.2f} cap was reached after "
                   f"{len(per_task)} of {len(spec['tasks'])} tasks ({exc})")
        print(f"  {stopped}")
    except llm.NoModelAnswered as exc:
        stopped = f"no model answered: {exc}"
        print(f"  {stopped}")
    if not per_task:
        print("nothing was measured, so nothing was written")
        return 1

    # ADR-40 item 5 and the second half of item 6. Both are questions about the
    # instrument rather than about the skill, both are judge-only, and both are
    # skipped rather than faked when the cap has already been reached.
    exploit = length = None
    if not stopped:
        try:
            if not args.no_exploit_test:
                exploit = run_exploits(judge, spec["tasks"], base)
                print(f"  exploit test: {exploit['reads']}")
            if not args.no_length_check:
                length = length_bias(judge, spec["tasks"], kept, base)
                print(f"  length bias: {length['reads']}")
        except (llm.CapReached, llm.NoModelAnswered) as exc:
            print(f"  the instrument checks stopped: {exc}")

    traj_block = None
    if trajectory:
        out_dir = base / "trajectories"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{today}-{sha[:12]}.json"
        path.write_text(json.dumps(
            {"contract": 1, "skill": args.skill, "date": today,
             "skill_md_sha256": sha, "sandbox": sandbox,
             "sandbox_why": sandbox_why, "entries": trajectory},
            indent=2, sort_keys=True) + "\n")
        traj_block = {"entries": len(trajectory), "sandbox": sandbox,
                      "path": shown(path),
                      "commands": sorted({e["command"] for e in trajectory})}

    declared = {t.strip() for t in args.written_against.split(",") if t.strip()}
    result = summarize(args.skill, sha, spec, per_task, subject_model,
                       judge_model, reps, cap.spent, today,
                       version=skill_version(args.skill),
                       sandbox=sandbox, sandbox_why=sandbox_why,
                       exploit=exploit, length=length,
                       differential=differential,
                       declared_written_against=declared,
                       trajectory=traj_block)
    if stopped:
        result["incomplete"] = stopped
        result["verdict"] = "incomplete: " + result["verdict"]
    if args.reps:
        result["repetitions_overridden"] = True
    out = results_path(args.skill)
    # Read before writing. `history` is ADR-37's version history: one entry per
    # measured version, with the trigger that asked for it. It is appended to
    # rather than replaced, so a skill's whole measured life is in one file,
    # every number this skill has ever been measured at lives there and nowhere
    # else, and this is the only moment the older ones still exist.
    previous = None
    if out.exists():
        try:
            previous = json.loads(out.read_text())
        except json.JSONDecodeError:
            # An unreadable file is still the only copy of whatever it held, and
            # this run is about to write over it. Keep the bytes, say where they
            # went, and carry on: the measurement that just cost money is not
            # thrown away either.
            kept = out.with_name(f"results.unreadable-{dt.date.today()}.json")
            kept.write_bytes(out.read_bytes())
            print(f"warning: {out.name} is not JSON, so there is nothing to "
                  f"compare this run against. Its bytes are kept at "
                  f"{shown(kept)} rather than overwritten.")
    result["trigger"] = args.trigger.strip() or "asked for by hand"
    result["history"] = appended_history(previous, result)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json
          else render(result))
    print(f"\nwritten to {shown(out)}")
    if args.gate:
        problems = gate_problems(result, previous_measurement(previous))
        for line in problems:
            print(f"gate: {line}")
        if problems:
            print("gate: this revision does not merge on its own. It stays a "
                  "draft pull request for the owner, which is what ADR-37's "
                  "amendment of 2026-09-29 says happens to anything the gate "
                  "does not clear.")
            return 1
        print("gate: clear on the clauses this harness can measure. The rest of "
              "ADR-37's gate is the ban list, the trigger test, the diff scope "
              "and the page render, and they are not this file's to check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
