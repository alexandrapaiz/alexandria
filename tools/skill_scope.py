#!/usr/bin/env python3
"""Load the skills a query names, not the library, and measure what that buys.

    python3 tools/skill_scope.py --query "our reranker made the agent confident about things nobody said"
    python3 tools/skill_scope.py --measure              # before/after on this repository's own suite
    python3 tools/skill_scope.py --measure --json out.json
    python3 tools/skill_scope.py --smoke                # the arithmetic, against fixtures

Exit code 0 when the measurement completes, 1 when scoping loses to no
scoping on the full pool, 2 on a data error. Losing is a real possible
outcome and the exit code says so rather than the report burying it.

## What this is for

docs/ideas.md, 2026-09-18, "Scoped skill delivery by default": the library
should put the skills a task needs in context, not all of them. The ledger
entry was triggered by one HN commenter. Five measurements later, the
market brief of 2026-10-16 is the controlled one: "Lost in Implicit
Routing" (arXiv 2610.18522) holds tasks and golden skills fixed, adds
irrelevant skills to the library, and watches loaded-skill recall fall from
73.6% to 27.4% at 1,000 irrelevant skills while the rate of loading no
skill at all rises from 9.3% to 51.6%. Explicit pre-selection from the same
library holds recall at 73.9%.

This repository ships nine skills, so it is nowhere near the regime that
paper measures. The point of measuring here anyway is that the trend line
starts at two skills, and a reader who installs this plugin installs it
next to whatever else they already have.

## The mechanism, in two stages

    stage 1, scope:   rank the whole catalogue by BM25 over each skill's own
                      body, keep the top one plus anything within KEEP_RATIO
                      of it, at most K_MAX. This is the stage that scales:
                      it reads text no harness can afford to hold in
                      context, and it runs before the model sees anything.
    stage 2, select:  the pre-registered lexical/2.1 router of
                      skills/_validation/trigger_test.py, over the scoped
                      set plus the unchanged decoy null panel. Firing still
                      has to outrank the null, so silence is still earned.

Stage 2 is imported rather than reimplemented, deliberately. The baseline
this measurement compares against is that same router over the whole
catalogue, which is what a harness does today when every description is in
context, so any difference between the two arms is the scoping and nothing
else.

## Why the distractors are real skills and not synthetic ones

`.agents/skills/` already holds twenty vendored Clerk skills: real
descriptions, real bodies, written by somebody else for a domain this
library does not serve. Generating a thousand fake irrelevant skills would
have produced a bigger number and a weaker one, because a distractor pool
written by the same run that measures against it is a pool tuned to lose.
Twenty real ones is the honest sample this checkout contains, and the
report says twenty rather than implying a thousand.

## The control that keeps the body index honest

The nine library skills average far more body text than the twenty
distractors, and BM25 normalises length but does not make the asymmetry
disappear. So the measurement runs the scoping stage twice:

    scope/body   stage 1 indexes each candidate's full SKILL.md body
    scope/desc   stage 1 indexes descriptions only, the same text stage 2
                 and the unscoped baseline already see

`scope/desc` adds no information at all. It can only narrow the pool. If
scoping wins on `scope/desc` too, the gain is the narrowing, which is the
mechanism the paper attributes it to. If it wins only on `scope/body`, the
gain is partly the richer index, and the report has to say so.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Pre-registered scoping policy.
#
# Fixed before the suite was run and printed in every bundle, the same
# discipline skills/_validation/trigger_test.py states for its own engine.
# Changing any of it means a new SCOPE_VERSION and a line in the history.
# ---------------------------------------------------------------------------
K_MAX = 3            # most skills a scope may name
KEEP_RATIO = 0.5     # keep a candidate scoring at least this share of the top
BM25_K1 = 1.2        # term-frequency saturation, the standard value, untuned
BM25_B = 0.75        # length normalisation, the standard value, untuned
SCOPE_VERSION = "scope/1"

# The library:distractor mean-body-length ratio past which the report says the
# body index is reading one pool more closely than the other. Same role as
# trigger_test.py's PANEL_LENGTH_TOLERANCE, and a wider tolerance because the
# pools here are two different authors' libraries rather than a null model
# built to match.
POOL_LENGTH_TOLERANCE = 2.0

# Scoping policy history, kept because a policy that can be retuned until it
# wins is not a measurement:
#   scope/1 (2026-10-26, current): BM25 over bodies, ratio cutoff at half the
#     top score, three skills maximum. K_MAX is 3 because the paper's holding
#     arm is explicit pre-selection of the task's own skills and a task in
#     this library's suite has one golden skill; 3 leaves room for a near-tie
#     without handing the selector the pool back.

LIBRARY_DIR = "skills"
DISTRACTOR_DIR = os.path.join(".agents", "skills")
DECOYS = os.path.join("skills", "_validation", "decoys.json")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def _trigger_test(root: Path):
    """The pre-registered router, loaded from its own file.

    Imported rather than copied so that this measurement cannot drift from
    the instrument the skill library already publishes. If lexical/2.1
    changes, the baseline and the scoped arm change together.
    """
    path = root / "skills" / "_validation" / "trigger_test.py"
    spec = importlib.util.spec_from_file_location("trigger_test", path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise SystemExit(f"cannot load the router from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# The catalogue: what a harness could load
# ---------------------------------------------------------------------------

def body_of(raw: str) -> str:
    """Everything after the frontmatter. This is the text a scoping stage can
    read and an in-context description cannot."""
    return FRONTMATTER_RE.sub("", raw, count=1)


def load_pool(tt, directory: Path, origin: str) -> dict:
    out = {}
    for path in sorted(glob.glob(str(directory / "*" / "SKILL.md"))):
        raw = open(path, encoding="utf-8").read()
        fm = tt.parse_frontmatter(raw)
        name = fm.get("name") or os.path.basename(os.path.dirname(path))
        desc = fm.get("description", "")
        out[name] = {
            "name": name,
            "path": os.path.relpath(path, ROOT),
            "description": desc,
            "activation": tt.activation_clause(desc),
            "body": body_of(raw),
            "origin": origin,
            # A candidate a router may fire. The decoy panel is the only thing
            # in the selection pool that is not, which is what lets silence be
            # a decision rather than a score falling off a cliff.
            "library": True,
        }
    return out


def load_null_panel(tt, path: Path) -> dict:
    panel = tt.load_decoys(str(path))
    for d in panel.values():
        d["origin"] = "null"
        d["body"] = d["description"]
        d["library"] = False
    return panel


# ---------------------------------------------------------------------------
# Stage 1: the scope
# ---------------------------------------------------------------------------

class BM25Index:
    """Okapi BM25 over one field of the catalogue.

    Length normalisation is the reason this is BM25 and not the router's own
    scorer. lexical/2.1 divides by the prompt's idf mass and never by the
    candidate's, so a longer candidate strictly dominates a terser one on any
    prompt both cover (trigger_test.py says so at DESCRIPTION_WORD_MAX, and
    incident 31 is what it cost). A stage that indexes whole skill bodies
    cannot carry that bias: the nine library skills average several times the
    body length of the twenty distractors, so a scorer that rewards length
    would hand this measurement the answer it wants.
    """

    def __init__(self, tt, candidates: dict, field: str):
        self.tt = tt
        self.field = field
        self.keys = list(candidates)
        self.docs = {k: tt.tokens(candidates[k][field]) for k in self.keys}
        self.lengths = {k: len(v) for k, v in self.docs.items()}
        self.freqs = {}
        df: dict[str, int] = {}
        for k, toks in self.docs.items():
            tf: dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            self.freqs[k] = tf
            for t in tf:
                df[t] = df.get(t, 0) + 1
        n = len(self.keys)
        self.avgdl = (sum(self.lengths.values()) / n) if n else 0.0
        # Lucene's non-negative idf. The textbook form goes negative for a term
        # in more than half the documents, which would let a common term push a
        # candidate below a candidate the term does not appear in at all.
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5))
                    for t, c in df.items()}

    def score(self, query: str, key: str) -> float:
        tf = self.freqs[key]
        dl = self.lengths[key]
        if not dl:
            return 0.0
        total = 0.0
        for t in set(self.tt.tokens(query)):
            f = tf.get(t)
            if not f:
                continue
            denom = f + BM25_K1 * (1 - BM25_B + BM25_B * dl / self.avgdl)
            total += self.idf.get(t, 0.0) * f * (BM25_K1 + 1) / denom
        return total

    def rank(self, query: str) -> list[tuple[str, float]]:
        scored = [(k, round(self.score(query, k), 4)) for k in self.keys]
        return sorted(scored, key=lambda kv: (-kv[1], kv[0]))


def scope(index: BM25Index, query: str,
          k_max: int = K_MAX, keep_ratio: float = KEEP_RATIO) -> dict:
    """The skills a query names. An empty scope is a valid answer: a prompt
    whose every term is absent from every body names nothing, and loading
    nothing is the right delivery for it."""
    ranked = index.rank(query)
    top = ranked[0][1] if ranked else 0.0
    if top <= 0:
        return {"loaded": [], "ranked": ranked[:k_max], "top_score": 0.0,
                "cutoff": 0.0}
    cutoff = top * keep_ratio
    loaded = [k for k, v in ranked[:k_max] if v >= cutoff]
    return {"loaded": loaded, "ranked": ranked[:k_max],
            "top_score": top, "cutoff": round(cutoff, 4)}


# ---------------------------------------------------------------------------
# Stage 2: the selection, and the baseline it is measured against
# ---------------------------------------------------------------------------

def select(tt, pool: dict, null_panel: dict, prompt: str) -> str | None:
    """Which skill actually loads. The pre-registered router, unchanged, over
    whatever pool it is handed plus the unchanged null panel.

    `fired` may name a distractor. That is the point: a wrong skill loaded is
    a different failure from no skill loaded, and the paper measures both.
    """
    if not pool:
        return None
    engine = tt.ENGINES[tt.ENGINE_VERSION]({**pool, **null_panel})
    return engine.route(prompt)["fired"]


def outcome(fired: str | None, expect: str | None) -> str:
    if expect is None:
        return "correct" if fired is None else "wrong"
    if fired == expect:
        return "correct"
    return "none" if fired is None else "wrong"


# ---------------------------------------------------------------------------
# The suite
# ---------------------------------------------------------------------------

def load_cases(root: Path, library: dict) -> list[dict]:
    """The synthetic query set. These are skills/*/triggers.json, the same 67
    cases the published trigger receipts are scored on, so this measurement
    does not get to write its own exam."""
    cases = []
    for path in sorted(glob.glob(str(root / LIBRARY_DIR / "*" / "triggers.json"))):
        suite = json.load(open(path, encoding="utf-8"))
        for case in suite["cases"]:
            expect = case.get("expect")
            if expect is not None and expect not in library:
                raise SystemExit(f"{path}: case {case['id']} expects unknown "
                                 f"skill {expect!r}")
            cases.append({"id": case["id"], "kind": case["kind"],
                          "prompt": case["prompt"], "expect": expect,
                          "suite": suite["skill"]})
    if not cases:
        raise SystemExit(f"no triggers.json cases under {root / LIBRARY_DIR}")
    return cases


def tally(results: list[dict]) -> dict:
    """Recall the way the paper states it, over the cases that have a golden
    skill, plus the negative cases reported separately.

    A negative case cannot contribute to recall and it is the only place the
    distractors can do damage that recall would never see, so it is counted
    and not folded in.
    """
    golden = [r for r in results if r["expect"] is not None]
    silent = [r for r in results if r["expect"] is None]
    n = len(golden)
    correct = sum(1 for r in golden if r["outcome"] == "correct")
    wrong = sum(1 for r in golden if r["outcome"] == "wrong")
    none = sum(1 for r in golden if r["outcome"] == "none")
    return {
        "golden_cases": n,
        "recall": round(correct / n, 4) if n else None,
        "recall_count": correct,
        "wrong_skill": round(wrong / n, 4) if n else None,
        "wrong_skill_count": wrong,
        "no_skill_loaded": round(none / n, 4) if n else None,
        "no_skill_loaded_count": none,
        "silent_cases": len(silent),
        "silence_held": round(
            sum(1 for r in silent if r["outcome"] == "correct") / len(silent), 4
        ) if silent else None,
        "suite_pass": round(
            sum(1 for r in results if r["outcome"] == "correct") / len(results), 4
        ),
    }


def run_arm(tt, cases: list[dict], pool: dict, null_panel: dict,
            index: BM25Index | None) -> dict:
    """One arm. `index` None is the unscoped baseline: the whole pool goes to
    the selector, which is what a harness holding every description in context
    is already doing."""
    results, scope_misses, loaded_sizes, context_words = [], 0, [], []
    for case in cases:
        if index is None:
            selection_pool = pool
            loaded = list(pool)
        else:
            loaded = scope(index, case["prompt"])["loaded"]
            selection_pool = {k: pool[k] for k in loaded}
            if case["expect"] is not None and case["expect"] not in loaded:
                scope_misses += 1
        loaded_sizes.append(len(loaded))
        # What the delivery actually costs. A harness pays for the description
        # of every skill it holds, on every turn, whether or not any of them
        # fires, so this is the number the proposal is about and recall is the
        # number that has to survive it.
        context_words.append(sum(len(pool[k]["description"].split())
                                 for k in loaded))
        fired = select(tt, selection_pool, null_panel, case["prompt"])
        results.append({"id": case["id"], "kind": case["kind"],
                        "expect": case["expect"], "fired": fired,
                        "loaded": len(loaded),
                        "outcome": outcome(fired, case["expect"])})
    report = tally(results)
    golden = sum(1 for c in cases if c["expect"] is not None)
    report["scope_misses"] = scope_misses
    report["scope_miss_rate"] = round(scope_misses / golden, 4) if golden else None
    report["mean_skills_loaded"] = round(statistics.mean(loaded_sizes), 2)
    report["mean_context_words"] = round(statistics.mean(context_words))
    report["cases"] = results
    return report


def pool_lengths(tt, library: dict, distractors: dict) -> dict:
    def mean_words(pool):
        if not pool:
            return 0.0
        return statistics.mean(len(c["body"].split()) for c in pool.values())
    lib, dis = mean_words(library), mean_words(distractors)
    ratio = (lib / dis) if dis else None
    return {"library_mean_body_words": round(lib),
            "distractor_mean_body_words": round(dis),
            "ratio": round(ratio, 2) if ratio else None,
            "tolerance": POOL_LENGTH_TOLERANCE,
            "past_tolerance": bool(ratio and ratio > POOL_LENGTH_TOLERANCE)}


def measure(root: Path, counts: list[int] | None = None) -> dict:
    tt = _trigger_test(root)
    library = load_pool(tt, root / LIBRARY_DIR, "library")
    if not library:
        raise SystemExit(f"no skills under {root / LIBRARY_DIR}")
    distractors = load_pool(tt, root / DISTRACTOR_DIR, "distractor")
    clash = set(library) & set(distractors)
    if clash:
        raise SystemExit(f"a distractor shares a name with a real skill: {clash}")
    null_panel = load_null_panel(tt, root / DECOYS)
    cases = load_cases(root, library)

    available = sorted(distractors)
    if counts is None:
        counts = sorted({0, 5, 10, len(available)} & set(range(len(available) + 1)))
    conditions = []
    for n in counts:
        if n > len(available):
            continue
        added = available[:n]
        pool = {**library, **{k: distractors[k] for k in added}}
        body = BM25Index(tt, pool, "body")
        desc = BM25Index(tt, pool, "description")
        conditions.append({
            "distractors_added": n,
            "catalogue_size": len(pool),
            "arms": {
                "unscoped": run_arm(tt, cases, pool, null_panel, None),
                "scope/body": run_arm(tt, cases, pool, null_panel, body),
                "scope/desc": run_arm(tt, cases, pool, null_panel, desc),
            },
        })

    return {
        "measured": SCOPE_VERSION,
        "selector": tt.ENGINE_VERSION,
        "policy": {"k_max": K_MAX, "keep_ratio": KEEP_RATIO,
                   "bm25_k1": BM25_K1, "bm25_b": BM25_B},
        "library": {"count": len(library), "names": sorted(library)},
        "distractor_pool": {"count": len(distractors),
                            "source": DISTRACTOR_DIR,
                            "names": available},
        "null_panel": {"count": len(null_panel)},
        "cases": {"total": len(cases),
                  "golden": sum(1 for c in cases if c["expect"] is not None),
                  "silent": sum(1 for c in cases if c["expect"] is None)},
        "pool_lengths": pool_lengths(tt, library, distractors),
        "conditions": conditions,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def pct(x: float | None) -> str:
    return "  n/a" if x is None else f"{100 * x:5.1f}%"


def render(report: dict) -> list[str]:
    out = [f"scoped skill delivery: {report['measured']}, selector "
           f"{report['selector']}",
           f"  {report['library']['count']} library skills, "
           f"{report['distractor_pool']['count']} real distractors from "
           f"{report['distractor_pool']['source']}, "
           f"{report['null_panel']['count']} decoys in the null panel",
           f"  {report['cases']['total']} cases: "
           f"{report['cases']['golden']} with a golden skill, "
           f"{report['cases']['silent']} that must stay silent",
           f"  policy: at most {report['policy']['k_max']} skills loaded, "
           f"cutoff at {report['policy']['keep_ratio']:.0%} of the top score",
           ""]
    pl = report["pool_lengths"]
    out.append(f"  bodies: library averages {pl['library_mean_body_words']} "
               f"words, distractors {pl['distractor_mean_body_words']}, a "
               f"{pl['ratio']}x gap"
               + (f" past the {pl['tolerance']}x tolerance, which is what "
                  f"scope/desc is the control for" if pl["past_tolerance"]
                  else ""))
    out.append("")
    head = (f"  {'distractors':>11}  {'arm':<11}  {'recall':>6}  "
            f"{'wrong':>6}  {'no skill':>8}  {'silence':>7}  "
            f"{'loaded':>6}  {'ctx words':>9}  {'scope miss':>10}")
    out.append(head)
    out.append("  " + "-" * (len(head) - 2))
    for cond in report["conditions"]:
        for arm_name, arm in cond["arms"].items():
            out.append(
                f"  {cond['distractors_added']:>11}  {arm_name:<11}  "
                f"{pct(arm['recall'])}  {pct(arm['wrong_skill'])}  "
                f"{pct(arm['no_skill_loaded'])}  {pct(arm['silence_held'])}  "
                f"{arm['mean_skills_loaded']:>6}  "
                f"{arm['mean_context_words']:>9}  "
                f"{pct(arm['scope_miss_rate'])}")
        out.append("")
    full = report["conditions"][-1]
    base = full["arms"]["unscoped"]
    for arm_name in ("scope/body", "scope/desc"):
        arm = full["arms"][arm_name]
        delta = arm["recall"] - base["recall"]
        saved = 1 - arm["mean_context_words"] / base["mean_context_words"]
        out.append(f"  at {full['distractors_added']} distractors, {arm_name} "
                   f"moves recall {delta:+.1%} against no scoping "
                   f"({pct(base['recall']).strip()} to "
                   f"{pct(arm['recall']).strip()}), loads "
                   f"{arm['mean_skills_loaded']} skills instead of "
                   f"{base['mean_skills_loaded']}, and spends "
                   f"{saved:.0%} fewer words on descriptions")
    out.append("")
    out += render_baseline_note(report)
    return out


def baseline_drift(report: dict) -> dict:
    """Did adding distractors cost the unscoped baseline anything?

    The paper's whole finding is that it does, so a measurement here that
    finds a flat baseline has found something about this distractor pool and
    has to say so rather than letting the scoped arm's win imply otherwise.
    """
    recalls = [c["arms"]["unscoped"]["recall"] for c in report["conditions"]]
    return {"first": recalls[0], "last": recalls[-1],
            "moved": round(recalls[-1] - recalls[0], 4),
            "flat": recalls[0] == recalls[-1]}


def render_baseline_note(report: dict) -> list[str]:
    d = baseline_drift(report)
    first = report["conditions"][0]["distractors_added"]
    last = report["conditions"][-1]["distractors_added"]
    if d["flat"]:
        return [f"  the unscoped baseline did not move between {first} and "
                f"{last} distractors ({pct(d['first']).strip()} both times), "
                f"so this pool does not reproduce the recall collapse the "
                f"market brief cites. Twenty real skills from one adjacent "
                f"domain are not a thousand near-neighbours. What scoping "
                f"buys here is the context cost and the confusion cases, not "
                f"a rescue from a collapse this checkout cannot stage."]
    return [f"  the unscoped baseline moved {d['moved']:+.1%} between {first} "
            f"and {last} distractors, which is the direction the market brief "
            f"predicts at far larger pools."]


def verdict(report: dict) -> int:
    """1 when scoping does not beat no scoping on the full distractor pool.

    The scope/body arm is the shipped mechanism, so it is the one the exit
    code answers for. A tie is not a win: the whole claim is that loading less
    costs nothing, and a mechanism that only matches the baseline has to say
    so loudly enough that a run notices.
    """
    full = report["conditions"][-1]["arms"]
    return 0 if full["scope/body"]["recall"] > full["unscoped"]["recall"] else 1


# ---------------------------------------------------------------------------
# Smoke: the arithmetic, on fixtures that make the answer obvious
# ---------------------------------------------------------------------------

def smoke(tt) -> list[str]:
    candidates = {
        "alpha": {"name": "alpha", "description": "pelican roosting habits",
                  "activation": "", "body": "pelican pelican roosting habits",
                  "origin": "library", "library": True},
        "beta": {"name": "beta", "description": "diesel engine timing",
                 "activation": "", "body": "diesel engine timing belts",
                 "origin": "library", "library": True},
    }
    index = BM25Index(tt, candidates, "body")
    lines = []

    s = scope(index, "where do pelicans roost")
    assert s["loaded"] == ["alpha"], s
    lines.append(f"  a query naming one body scopes to it: {s['loaded']}")

    s = scope(index, "quantum chromodynamics")
    assert s["loaded"] == [], s
    lines.append("  a query no body covers scopes to nothing, and nothing loads")

    s = scope(index, "pelican diesel")
    assert set(s["loaded"]) == {"alpha", "beta"}, s
    lines.append(f"  a query straddling two bodies scopes to both: "
                 f"{sorted(s['loaded'])}")

    assert outcome("alpha", "alpha") == "correct"
    assert outcome("beta", "alpha") == "wrong"
    assert outcome(None, "alpha") == "none"
    assert outcome(None, None) == "correct"
    assert outcome("alpha", None) == "wrong"
    lines.append("  the four outcomes separate a wrong skill from no skill")

    t = tally([{"expect": "a", "outcome": "correct"},
               {"expect": "a", "outcome": "wrong"},
               {"expect": "a", "outcome": "none"},
               {"expect": None, "outcome": "correct"}])
    assert t["recall"] == round(1 / 3, 4), t
    assert t["wrong_skill"] == round(1 / 3, 4), t
    assert t["no_skill_loaded"] == round(1 / 3, 4), t
    assert t["silence_held"] == 1.0, t
    assert t["suite_pass"] == 0.5, t
    lines.append("  recall counts only the cases with a golden skill, and "
                 "silence is reported beside it rather than inside it")

    # Length normalisation, the property that earns BM25 over the router's own
    # scorer: padding a body with text the query never mentions must not win it.
    padded = {
        "short": {"name": "short", "description": "", "activation": "",
                  "body": "pelican roosting", "origin": "library",
                  "library": True},
        "long": {"name": "long", "description": "", "activation": "",
                 "body": "pelican roosting " + "unrelated filler prose " * 60,
                 "origin": "library", "library": True},
    }
    pad_index = BM25Index(tt, padded, "body")
    ranked = pad_index.rank("pelican roosting")
    assert ranked[0][0] == "short", ranked
    lines.append("  padding a body with 180 irrelevant words loses the query "
                 "it padded, so length does not buy a scope slot")
    return lines


# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--query", help="print the scope this query names")
    ap.add_argument("--measure", action="store_true",
                    help="before/after recall over the trigger suite")
    ap.add_argument("--distractors", help="comma-separated distractor counts "
                                         "to measure at (default 0,5,10,all)")
    ap.add_argument("--json", nargs="?", const="-", metavar="PATH",
                    help="the report as data, to stdout or to a file")
    ap.add_argument("--smoke", action="store_true",
                    help="the arithmetic, against fixtures")
    ap.add_argument("--root", default=str(ROOT), help="a checkout to measure")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    tt = _trigger_test(root)

    if args.smoke:
        print(f"skill_scope {SCOPE_VERSION}: smoke")
        for line in smoke(tt):
            print(line)
        print("  smoke: ok")
        return 0

    if args.query:
        library = load_pool(tt, root / LIBRARY_DIR, "library")
        distractors = load_pool(tt, root / DISTRACTOR_DIR, "distractor")
        pool = {**library, **distractors}
        index = BM25Index(tt, pool, "body")
        s = scope(index, args.query)
        null_panel = load_null_panel(tt, root / DECOYS)
        fired = select(tt, {k: pool[k] for k in s["loaded"]}, null_panel,
                       args.query)
        report = {"query": args.query, "catalogue_size": len(pool),
                  "scoped": s["loaded"], "ranked": s["ranked"],
                  "cutoff": s["cutoff"], "fires": fired}
        if args.json:
            text = json.dumps(report, indent=2)
            print(text) if args.json == "-" else Path(args.json).write_text(text + "\n")
        else:
            print(f"scope of {len(pool)} catalogue entries, cutoff "
                  f"{s['cutoff']}:")
            for name, score in s["ranked"]:
                mark = "loaded" if name in s["loaded"] else "      "
                print(f"  {mark}  {score:>8.4f}  {name} "
                      f"({pool[name]['origin']})")
            print(f"  fires: {fired or 'nothing'}")
        return 0

    if not args.measure:
        ap.error("one of --query, --measure or --smoke")

    counts = None
    if args.distractors:
        counts = sorted({int(x) for x in args.distractors.split(",")})
    report = measure(root, counts)
    code = verdict(report)
    report["verdict"] = "scoping wins" if code == 0 else "scoping does not win"

    if args.json:
        text = json.dumps(report, indent=2)
        if args.json == "-":
            print(text)
        else:
            Path(args.json).write_text(text + "\n")
            print(f"wrote {args.json}")
    else:
        for line in render(report):
            print(line)
        print(f"  verdict: {report['verdict']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
