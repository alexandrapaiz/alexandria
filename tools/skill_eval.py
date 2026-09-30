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
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

CONTRACT = 1

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

def skill_dir(slug: str) -> pathlib.Path:
    return ROOT / "skills" / slug


def read_skill(slug: str) -> tuple[str, str]:
    """(body, sha256 of the whole file). The body is what the with-arm loads.

    The sha pins the result to the exact text that produced it, the same way the
    trigger-test receipts do. A skill edited after its eval has a result that
    describes an earlier revision, and the site has to be able to say so.
    """
    path = skill_dir(slug) / "SKILL.md"
    raw = path.read_text()
    match = re.match(r"^---\n.*?\n---\n", raw, re.S)
    body = raw[match.end():] if match else raw
    return body.strip(), hashlib.sha256(raw.encode()).hexdigest()


# The skill seat writes `evals/evals.json`, which is also the name the
# skill-creator plugin's own suites use. `evals/tasks.json` is accepted as an
# alias because this harness proposed that name first, on 2026-09-30, in the same
# window the skill seat was writing six suites under the other one. The suites
# that exist win; a harness that cannot read the tasks that were written is worth
# nothing.
TASK_FILENAMES = ("evals.json", "tasks.json")


def tasks_path(slug: str) -> pathlib.Path:
    evals = skill_dir(slug) / "evals"
    for name in TASK_FILENAMES:
        if (evals / name).exists():
            return evals / name
    return evals / TASK_FILENAMES[0]


def results_path(slug: str) -> pathlib.Path:
    return skill_dir(slug) / "evals" / "results.json"


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


def normalize(spec: dict) -> dict:
    """The skill seat's suite in this harness's vocabulary. Idempotent."""
    out = dict(spec)
    out["contract"] = spec.get("contract", spec.get("suite_version"))
    policy = dict(spec.get("policy") or {})
    policy.setdefault("repetitions", DEFAULT_REPS)
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


def conformance(spec: dict, slug: str, base: pathlib.Path) -> list[str]:
    """Everything wrong with one `tasks.json`. Empty means it can be run.

    Its own function so `--check` can be a CI gate over every skill's eval file
    without a key, a model or a dollar.
    """
    problems = []
    if spec.get("contract") != CONTRACT:
        problems.append(f"{slug}: contract is {spec.get('contract')!r}, this "
                        f"harness speaks {CONTRACT}")
    if spec.get("skill") != slug:
        problems.append(f"{slug}: the file says skill {spec.get('skill')!r}")
    policy = spec.get("policy") or {}
    if not isinstance(policy, dict) or "repetitions" not in policy:
        problems.append(f"{slug}: policy.repetitions is not pre-registered, so "
                        "the run would choose its own n. Rule 1.")
    if policy.get("subject") and policy.get("subject") == policy.get("judge"):
        problems.append(f"{slug}: the subject and the judge are the same model")

    tasks = spec.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        problems.append(f"{slug}: no tasks")
        return problems

    seen = set()
    real = 0
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
        if task.get("scored_in") and not is_indicator(task):
            problems.append(f"{slug}/{tid}: scored_in is "
                            f"{task['scored_in']!r}, and the only value this "
                            f"harness knows is {INDICATOR!r}")
        if task.get("control") and is_indicator(task):
            problems.append(f"{slug}/{tid}: a control and an indicator at once. "
                            "A control is a task the skill must not change and "
                            "an indicator is one only the skill can pass.")
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


def load_tasks(slug: str) -> tuple[dict, list[str]]:
    path = tasks_path(slug)
    if not path.exists():
        return {}, [f"{slug}: no evals/evals.json. Unmeasured, which is an "
                    "honest state and is never a pass (ADR-36: a skill with no "
                    "eval is status draft, never active)."]
    try:
        spec = normalize(json.loads(path.read_text()))
    except json.JSONDecodeError as exc:
        return {}, [f"{slug}: {path.name} is not JSON ({exc})"]
    return spec, conformance(spec, slug, path.parent)


# ------------------------------------------------------------------ scoring

def hard_check(task: dict, answer: str, base: pathlib.Path) -> tuple[float, str]:
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
        return run_project_check(task, answer, base, check)

    return (0.0, f"unknown check type {kind!r}")


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


def tests_pass(task: dict, answer: str, base: pathlib.Path,
               check: dict) -> tuple[float, str]:
    """The answer is written to `answer_path` and `command` decides. Exit 0 wins.

    The command runs through a shell because the suites write it as one string,
    and it runs inside a temporary copy with a timeout. This is the cheapest and
    least arguable score in the harness: the tests either pass or they do not,
    and no judge is involved.
    """
    with tempfile.TemporaryDirectory() as tmp:
        work = workspace(task, check, base, pathlib.Path(tmp))
        target = work / check["answer_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(extract_code(answer))
        try:
            done = subprocess.run(check["command"], cwd=work, shell=True,
                                  capture_output=True, text=True,
                                  env=command_env(),
                                  timeout=check.get("timeout", 180))
        except subprocess.TimeoutExpired:
            return (0.0, "the command timed out")
        except OSError as exc:
            return (None, f"the command could not be run ({exc})")
        if done.returncode == 0:
            return (1.0, "exit 0")
        tail = (done.stdout + done.stderr).strip().splitlines()[-3:]
        detail = f"exit {done.returncode}: " + " | ".join(tail)
        if done.returncode == UNRUNNABLE:
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


def run_project_check(task: dict, answer: str, base: pathlib.Path,
                      check: dict) -> tuple[float, str]:
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
        try:
            done = subprocess.run(check["run"], cwd=work, capture_output=True,
                                  text=True, timeout=check.get("timeout", 120))
        except subprocess.TimeoutExpired:
            return (0.0, "the check timed out")
        except OSError as exc:
            return (0.0, f"the check could not be run ({exc})")
        if done.returncode == 0:
            return (1.0, "exit 0")
        tail = (done.stdout + done.stderr).strip().splitlines()[-3:]
        return (0.0, f"exit {done.returncode}: " + " | ".join(tail))


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


def rubric_score(verdicts: dict, rubric: list[dict]) -> tuple[float, str]:
    scores = [criterion_score(verdicts.get(item["id"]), item.get("anchors"))
              for item in rubric]
    got = sum(scores)
    detail = ", ".join("{}={:.2f}".format(item["id"], value)
                       for item, value in zip(rubric, scores))
    return (mean(scores),
            f"{got:.2f} of {len(rubric)} criteria ({detail})")


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
        answer, _ = self.llm.ask_json([self.model], system, user, self.env,
                                      self.cap, max_completion=max_tokens,
                                      available=self.available)
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


def score_answer(task: dict, answer: str, judge, base: pathlib.Path
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
        return rubric_score(verdicts, task["rubric"])

    if kind == "tests_pass":
        return tests_pass(task, answer, base, check)

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
        return (mean(parts),
                f"value {value!r} against [{low}, {high}] ({'in' if in_range else 'out'}), "
                f"{int(sum(hits))} of {len(hits)} secondary")

    if check:
        return hard_check(task, answer, base)

    return (0.0, "nothing scores this task")


def run_task(subject, judge, task: dict, skill_body: str, reps: int,
             base: pathlib.Path) -> dict:
    """One task, both arms, `reps` times each."""
    with_system = (SUBJECT_SYSTEM + "\n\n# The skill under test\n\n"
                   + skill_body)
    deterministic = (task.get("check") or {}).get("type") == "tests_pass"
    rows = {"id": task["id"], "control": bool(task.get("control")),
            "indicator": is_indicator(task),
            "scored_by": "rubric" if task.get("rubric")
                         else ("hard check" if deterministic else "mixed"),
            "with_scores": [], "without_scores": [], "notes": [],
            "unmeasured": 0}
    ask = render_ask(task)

    for arm, system, bucket in (("with", with_system, "with_scores"),
                                ("without", SUBJECT_SYSTEM, "without_scores")):
        for rep in range(reps):
            reply = subject.ask(system, ask, SUBJECT_MAX_TOKENS)
            answer = str(reply.get("answer") or "")
            score, why = score_answer(task, answer, judge, base)
            if score is None:
                # Unmeasured, not zero. The repetition is dropped from both the
                # arm and the count, and the note says why, so a task that could
                # not be run shows up as a smaller n rather than as a bad result.
                rows["unmeasured"] += 1
                rows["notes"].append(f"{arm} rep {rep + 1}: unmeasured ({why})")
                continue
            rows[bucket].append(score)
            rows["notes"].append(f"{arm} rep {rep + 1}: {score:.2f} ({why})")

    rows["with_mean"] = round(mean(rows["with_scores"]), 4)
    rows["without_mean"] = round(mean(rows["without_scores"]), 4)
    rows["delta"] = round(rows["with_mean"] - rows["without_mean"], 4)
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
              today: str) -> dict:
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

    delta, low, high = bootstrap_delta(graded)
    binary = all(s in (0.0, 1.0) for t in graded
                 for s in t["with_scores"] + t["without_scores"])

    def arm(key: str) -> dict:
        scores = [s for t in graded for s in t[key]]
        out = {"n": len(scores), "mean": round(mean(scores), 4)}
        if binary:
            successes = int(sum(scores))
            out["successes"] = successes
            out["interval95"] = list(clopper_pearson(successes, len(scores)))
            out["reads"] = f"{successes} of {len(scores)}"
        return out

    result = {
        "contract": CONTRACT,
        "skill": slug,
        "skill_md_sha256": sha,
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
    }
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
    lines.append(f"  spend            ${result['spend_usd']:.4f}")
    if result["verdict"] != "gain":
        lines.append("  This is a finding, not a failure of the harness. "
                     "ADR-36: a skill whose eval shows no gain is retired with "
                     "the numbers.")
    return "\n".join(lines)


SMOKE_SPEC = {
    "contract": CONTRACT,
    "skill": "_smoke",
    "policy": {"repetitions": 3, "min_delta": 0.2},
    "tasks": [
        {"id": "hard-check", "ask": "What should we do?",
         "check": {"type": "contains_all", "patterns": ["harness"]}},
        {"id": "rubric", "ask": "What should we do?",
         "rubric": [{"id": "names-the-move", "asks": "Does it name the move?"}]},
        {"id": "control", "control": True, "ask": "What is 2 + 2?",
         "check": {"type": "contains_all", "patterns": ["4"]}},
    ],
}


def smoke() -> int:
    """The whole harness against a scripted model. No key, no network, no money."""
    subject = ScriptedSubject(
        with_answer="Change the harness before the weights. 4.",
        without_answer="Fine-tune the model on the stronger one's traces. 4.")
    per_task = [run_task(subject, subject, task, "the skill body", 3,
                         pathlib.Path("."))
                for task in SMOKE_SPEC["tasks"]]
    result = summarize("_smoke", "0" * 64, SMOKE_SPEC, per_task,
                       "scripted/with-and-without", "scripted/judge", 3, 0.0,
                       dt.date.today().isoformat())
    print(render(result))
    print(f"\n{subject.calls} scripted calls, $0.00 spent")
    # What this asserts is the arithmetic, not the model. With this scripted
    # pair the with-arm passes everything, the without-arm passes nothing that
    # is being graded, and the control is identical in both arms. Anything else
    # is a bug in the scorer, the bootstrap or the verdict rule.
    ok = (result["with_skill"]["reads"] == "6 of 6"
          and result["without_skill"]["reads"] == "0 of 6"
          and result["with_skill"]["interval95"][0] == 0.5407
          and result["delta"]["mean"] == 1.0
          and result["verdict"] == "gain"
          and result["controls"]["unchanged"]
          and result["tasks"] == 2 and result["control_tasks"] == 1)
    print("smoke: " + ("the harness measures what it should"
                       if ok else "THE HARNESS IS WRONG"))
    return 0 if ok else 1


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
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()

    if args.check:
        import os

        slugs = sorted(p.name for p in (ROOT / "skills").iterdir()
                       if p.is_dir() and p.name != "_validation")
        problems, measured = [], 0
        for slug in slugs:
            spec, found = load_tasks(slug)
            problems += found
            measured += 1 if spec and not found else 0
        print(f"{measured} of {len(slugs)} skills carry a conformant eval file")
        # Absent is unmeasured, not broken: the skill seat writes the tasks and
        # ADR-36 makes such a skill `draft`. A malformed file is a real failure.
        # The two are labelled differently on purpose, because a line reading
        # `failing` against a file nobody has written yet is how a report stops
        # being read.
        malformed = [p for p in problems if "no evals/evals.json" not in p]
        for line in problems:
            print(("failing: " if line in malformed else "unmeasured: ") + line)
        if malformed:
            return 1
        return 2 if problems else 0

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
    per_task = []
    stopped = ""
    for task in spec["tasks"]:
        print(f"  {task['id']}...")
        try:
            per_task.append(run_task(subject, judge, task, body, reps, base))
        except llm.CapReached as exc:
            # The cap is not a failure and a run that hits it must not throw away
            # what it measured. The tasks already finished are a smaller eval,
            # honestly labelled, and the result says where it stopped.
            stopped = (f"the ${args.cap:.2f} cap was reached at {task['id']}, "
                       f"after {len(per_task)} of {len(spec['tasks'])} tasks "
                       f"({exc})")
            print(f"  {stopped}")
            break
        except llm.NoModelAnswered as exc:
            stopped = f"no model answered at {task['id']}: {exc}"
            print(f"  {stopped}")
            break
    if not per_task:
        print("nothing was measured, so nothing was written")
        return 1

    result = summarize(args.skill, sha, spec, per_task, subject_model,
                       judge_model, reps, cap.spent,
                       dt.date.today().isoformat())
    if stopped:
        result["incomplete"] = stopped
        result["verdict"] = "incomplete: " + result["verdict"]
    if args.reps:
        result["repetitions_overridden"] = True
    out = results_path(args.skill)
    # Read before writing. The gate compares against the previous version's
    # measured delta, and this is the only moment the previous one still exists.
    previous = None
    if out.exists():
        try:
            previous = json.loads(out.read_text())
        except json.JSONDecodeError:
            print(f"warning: {out.name} is not JSON, so there is nothing to "
                  "compare this run against")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json
          else render(result))
    print(f"\nwritten to {out.relative_to(ROOT)}")
    if args.gate:
        problems = gate_problems(result, previous)
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
