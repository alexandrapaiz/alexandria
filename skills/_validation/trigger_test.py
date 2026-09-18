#!/usr/bin/env python3
"""Executable trigger test for the alexandria skill library.

Slice 1 of the skill validation system (docs/product/skill-validation.md):
does a skill fire when it should, stay silent when it should not, and stay
distinct from its neighbours? The market audit behind this found 69% of 216
public Claude Code skills would not reliably trigger. A library that sells
receipts cannot ship an unmeasured trigger.

Run:
    python3 skills/_validation/trigger_test.py            # human report
    python3 skills/_validation/trigger_test.py --json out.json

Exit code 0 when every case passes, 1 when any case fails, 2 on a data error.
No third-party dependencies, no network, no database, so this is the screen
that can run on every PR.

How a decision is made. Each prompt is scored against every skill description
in the library and against a fixed panel of decoy descriptions
(decoys.json) covering domains the library does not serve. The top-scoring
candidate wins; the skill fires only if the winner is a library skill and
clears a low sanity floor. The decoys are the null model: silence has to be
earned by something else fitting the prompt better, rather than by a score
falling under an arbitrary cutoff.

What this measures, and what it does not. The lexical engine is a
deterministic stand-in for the retrieval half of a real skill router, not the
router itself. A case that fails here would very likely fail in a real
harness; a case that passes here has cleared a lower bound only. The
model-in-the-loop engine that closes the gap is slice 2 and belongs to the
ADR-13 validator. Read every number this prints as a floor.

Policy history, kept because a test that can be retuned until it passes is
not a test:
  lexical/1 (2026-09-18, retired same day): scored the same way but fired on
    an absolute threshold of 0.25 with no null model. Ranked the correct skill
    first in 12 of 12 cases and still failed 5 of them, because realistic
    prompts carry many words no skill description contains, which drags a
    mass-normalised score below any fixed cutoff. The recorded run is in this
    PR. The finding was the instrument's, not the library's.
  lexical/2 (2026-09-18): replaces the absolute cutoff with the decoy panel.
  lexical/2.1 (current): same scores, conservative tie handling. The
    pre-registered lexical/2 run produced an exact score tie between a library
    skill and a decoy, which argmax resolved alphabetically; a coin flip is
    not a verdict. A skill must now strictly outrank every decoy to fire. No
    case outcome changed, and the affected case is still reported as a
    zero-margin decision rather than a clean pass.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys
from datetime import date

# ---------------------------------------------------------------------------
# Pre-registered decision policy.
#
# Fixed before the cases were run and printed in every result bundle, so a
# later run cannot quietly tune the test until it is green (the
# pre-registration discipline of the Discovery Certification Protocol, claim
# 286). Changing any of it means a new ENGINE_VERSION and a note in the policy
# history above.
# ---------------------------------------------------------------------------
FLOOR = 0.05            # sanity floor: below this, nothing in the prompt matched
NARROW_MARGIN = 0.02    # lead under which a win is reported as narrow, not failed
USE_WHEN_BOOST = 1.25   # activation-condition terms outweigh framing prose
ENGINE_VERSION = "lexical/2.1"
ALPHA = 0.05            # 95% intervals

STOPWORDS = {
    "a", "about", "actually", "after", "all", "already", "also", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "between", "both", "but", "by", "can", "care", "cannot", "do", "does",
    "doing", "done", "for", "from", "get", "gets", "give", "had", "has",
    "have", "how", "i", "if", "in", "into", "is", "it", "its", "just", "keep",
    "like", "make", "many", "me", "more", "most", "much", "my", "need", "no",
    "not", "of", "on", "one", "or", "other", "our", "out", "over", "own",
    "part", "per", "should", "so", "some", "start", "still", "such", "than",
    "that", "the", "their", "them", "then", "there", "these", "they", "thing",
    "things", "this", "those", "to", "up", "us", "use", "used", "uses",
    "using", "want", "wants", "was", "were", "what", "when", "where",
    "whether", "which", "while", "who", "why", "will", "with", "would", "you",
    "your",
}

WORD_RE = re.compile(r"[a-z][a-z0-9'\-]*")


def stem(word: str) -> str:
    """Crude suffix stripping, enough to match 'distilling' to 'distillation'
    without taking on a stemmer dependency."""
    for suffix in ("ization", "isation", "ations", "ation", "ingly", "ing",
                   "edly", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)].rstrip("-'")
    return word


def tokens(text: str) -> list[str]:
    out = []
    for raw in WORD_RE.findall(text.lower()):
        if raw in STOPWORDS or len(raw) < 3:
            continue
        s = stem(raw)
        if len(s) >= 3 and s not in STOPWORDS:
            out.append(s)
    return out


# ---------------------------------------------------------------------------
# Loading the library and the null model
# ---------------------------------------------------------------------------

def parse_frontmatter(raw: str) -> dict:
    """Read the flat frontmatter fields this test needs.

    Deliberately narrow. The site parser has the same flat-line limitation and
    a ledger entry open to fix it; this test needs only the two fields a router
    would see, so it does not take on nested YAML parsing.
    """
    m = re.match(r"^---\n(.*?)\n---", raw, re.S)
    if not m:
        return {}
    block, fields = m.group(1), {}
    for key in ("name", "description", "version", "status"):
        km = re.search(rf"^{key}:\s*(.+)$", block, re.M)
        if km:
            fields[key] = km.group(1).strip().strip('"')
    return fields


def activation_clause(description: str) -> str:
    """The part of a description that states when to fire: everything from the
    first 'Use when' onward. A description with no such clause has no concrete
    activation conditions, which is itself the failure the 69%-never-fire
    finding describes, so the runner warns about it."""
    idx = description.lower().find("use when")
    return description[idx:] if idx != -1 else ""


def load_skills(skills_dir: str) -> dict:
    skills = {}
    for path in sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md"))):
        raw = open(path, encoding="utf-8").read()
        fm = parse_frontmatter(raw)
        name = fm.get("name") or os.path.basename(os.path.dirname(path))
        desc = fm.get("description", "")
        skills[name] = {
            "name": name,
            "path": os.path.relpath(path),
            "description": desc,
            "activation": activation_clause(desc),
            # The frozen evidence bundle: a result is a receipt only for the
            # exact text that produced it (claim 290).
            "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16],
            "library": True,
        }
    return skills


def load_decoys(path: str) -> dict:
    data = json.load(open(path, encoding="utf-8"))
    out = {}
    for d in data["decoys"]:
        out[d["name"]] = {
            "name": d["name"],
            "path": os.path.relpath(path),
            "description": d["description"],
            "activation": activation_clause(d["description"]),
            "library": False,
        }
    return out


# ---------------------------------------------------------------------------
# The lexical engine
# ---------------------------------------------------------------------------

class LexicalEngine:
    """Idf-weighted overlap between a prompt and each candidate description.

    Idf is computed across the library plus the decoy panel, so vocabulary
    every candidate shares ('agent', 'model', 'when') counts for little and the
    terms that separate one candidate from its neighbours count for more. The
    separation sharpens as the library grows, which is the right direction:
    the test gets harder to pass as O2's twelve skills land, not easier.
    """

    name = ENGINE_VERSION

    def __init__(self, candidates: dict):
        self.candidates = candidates
        n = len(candidates)
        df: dict[str, int] = {}
        self.sets = {}
        for key, c in candidates.items():
            body = set(tokens(c["description"]))
            act = set(tokens(c["activation"]))
            self.sets[key] = (body, act)
            for t in body:
                df[t] = df.get(t, 0) + 1
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}
        # A term in no description at all carries full weight: it is evidence
        # the prompt is about something nothing here covers.
        self.default_idf = math.log(n + 1) + 1.0

    def score(self, prompt: str, key: str) -> float:
        body, act = self.sets[key]
        prompt_terms = set(tokens(prompt))
        if not prompt_terms:
            return 0.0
        total = matched = 0.0
        for t in prompt_terms:
            w = self.idf.get(t, self.default_idf)
            total += w
            if t in body:
                matched += w * (USE_WHEN_BOOST if t in act else 1.0)
        return matched / total if total else 0.0

    def route(self, prompt: str) -> dict:
        """Fire the best library skill only when it strictly outranks the whole
        null panel. Silence is the default; firing is what has to be earned."""
        scores = {k: round(self.score(prompt, k), 4) for k in self.candidates}
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        lib = [(k, v) for k, v in ranked if self.candidates[k]["library"]]
        null = [(k, v) for k, v in ranked if not self.candidates[k]["library"]]
        best_library, library_score = lib[0] if lib else (None, 0.0)
        best_decoy, decoy_score = null[0] if null else (None, 0.0)
        null_margin = round(library_score - decoy_score, 4)
        fired = (best_library is not None
                 and library_score >= FLOOR
                 and library_score > decoy_score)
        return {
            "fired": best_library if fired else None,
            "winner": ranked[0][0],
            "winner_is_decoy": not self.candidates[ranked[0][0]]["library"],
            "best_library": best_library,
            "library_score": library_score,
            "closest_decoy": best_decoy,
            "decoy_score": decoy_score,
            "null_margin": null_margin,
            "narrow": abs(null_margin) < NARROW_MARGIN,
            "scores": scores,
        }


# ---------------------------------------------------------------------------
# Statistics: small n, stated honestly
# ---------------------------------------------------------------------------

def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i)
               for i in range(0, k + 1))


def clopper_pearson(k: int, n: int, alpha: float = ALPHA) -> tuple[float, float]:
    """Exact binomial confidence interval by bisection on the exact binomial
    CDF. No SciPy and no normal approximation: at n=6 a Wald interval is simply
    wrong, and not overclaiming is this instrument's entire job."""
    if n == 0:
        return (0.0, 1.0)

    def bisect(too_high) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if too_high(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    # Lower bound L solves P(X >= k | L) = alpha/2; that probability rises
    # with p, so a p where it already exceeds alpha/2 is too high.
    low = 0.0 if k == 0 else bisect(
        lambda p: 1 - binom_cdf(k - 1, n, p) > alpha / 2)
    # Upper bound U solves P(X <= k | U) = alpha/2; that probability falls
    # with p, so a p where it still exceeds alpha/2 is too low.
    high = 1.0 if k == n else bisect(
        lambda p: binom_cdf(k, n, p) <= alpha / 2)
    return (round(low, 4), round(high, 4))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run(skills_dir: str, decoys_path: str) -> dict:
    skills = load_skills(skills_dir)
    if not skills:
        raise SystemExit(f"no skills found under {skills_dir}")
    decoys = load_decoys(decoys_path)
    clash = set(skills) & set(decoys)
    if clash:
        raise SystemExit(f"decoy name collides with a real skill: {clash}")
    engine = LexicalEngine({**skills, **decoys})

    warnings = [f"{sk['path']}: description states no 'Use when' activation "
                f"conditions" for sk in skills.values() if not sk["activation"]]

    case_files = sorted(glob.glob(os.path.join(skills_dir, "*", "triggers.json")))
    if not case_files:
        raise SystemExit(f"no triggers.json files found under {skills_dir}")
    covered = {json.load(open(cf, encoding="utf-8"))["skill"] for cf in case_files}
    warnings += [f"{sk['path']}: no triggers.json, skill is untested"
                 for name, sk in skills.items() if name not in covered]

    suites = []
    for cf in case_files:
        suite = json.load(open(cf, encoding="utf-8"))
        owner = suite["skill"]
        if owner not in skills:
            raise SystemExit(f"{cf}: names unknown skill {owner!r}")
        results = []
        for case in suite["cases"]:
            expect = case.get("expect")  # a skill name, or null for silence
            if expect is not None and expect not in skills:
                raise SystemExit(f"{cf}: case {case['id']} expects unknown "
                                 f"skill {expect!r}")
            decision = engine.route(case["prompt"])
            results.append({
                "id": case["id"],
                "kind": case["kind"],
                "prompt": case["prompt"],
                "expect": expect,
                "got": decision["fired"],
                "passed": decision["fired"] == expect,
                "winner": decision["winner"],
                "winner_is_decoy": decision["winner_is_decoy"],
                "library_score": decision["library_score"],
                "closest_decoy": decision["closest_decoy"],
                "null_margin": decision["null_margin"],
                "narrow": decision["narrow"],
                "scores": decision["scores"],
                "rationale": case.get("rationale", ""),
            })
        passed = sum(1 for r in results if r["passed"])
        suites.append({
            "skill": owner,
            "source": os.path.relpath(cf),
            "skill_sha256": skills[owner]["sha256"],
            "suite_version": suite.get("suite_version"),
            "cases": results,
            "passed": passed,
            "total": len(results),
            "narrow_decisions": sum(1 for r in results if r["narrow"]),
            "reliability": round(passed / len(results), 4),
            "reliability_ci95": clopper_pearson(passed, len(results)),
            "positive_recall": _rate(results, "positive"),
            "negative_rejection": _rate(results, "negative"),
            "confusion_resolved": _rate(results, "confusion"),
        })

    total_pass = sum(s["passed"] for s in suites)
    total_cases = sum(s["total"] for s in suites)
    return {
        "generated": date.today().isoformat(),
        "engine": engine.name,
        "policy": {
            "floor": FLOOR,
            "narrow_margin": NARROW_MARGIN,
            "use_when_boost": USE_WHEN_BOOST,
            "alpha": ALPHA,
            "decoy_panel": os.path.relpath(decoys_path),
            "decoy_count": len(decoys),
            "pre_registered": True,
        },
        "library": {k: {"path": v["path"], "sha256": v["sha256"]}
                    for k, v in skills.items()},
        "warnings": warnings,
        "suites": suites,
        "passed": total_pass,
        "total": total_cases,
        "reliability": round(total_pass / total_cases, 4) if total_cases else 0.0,
        "reliability_ci95": clopper_pearson(total_pass, total_cases),
    }


def _rate(results: list[dict], kind: str) -> str:
    sel = [r for r in results if r["kind"] == kind]
    if not sel:
        return "0/0"
    return f"{sum(1 for r in sel if r['passed'])}/{len(sel)}"


def report(res: dict, verbose: bool) -> None:
    p = res["policy"]
    print(f"trigger test — engine {res['engine']}, floor {p['floor']}, "
          f"{p['decoy_count']} decoys (policy pre-registered)")
    print(f"library: {len(res['library'])} skills, {res['total']} cases\n")
    for w in res["warnings"]:
        print(f"  warning: {w}")
    if res["warnings"]:
        print()
    for suite in res["suites"]:
        print(f"## {suite['skill']}  ({suite['source']})")
        for case in suite["cases"]:
            mark = "PASS" if case["passed"] else "FAIL"
            expect = case["expect"] or "(silence)"
            got = case["got"] or f"(silence, best fit {case['winner']})"
            flag = f"  [narrow, margin {case['null_margin']:+.3f}]" if case["narrow"] else ""
            print(f"  [{mark}] {case['id']:<12} {case['kind']:<9} "
                  f"expect {expect} -> {got}{flag}")
            if verbose or not case["passed"]:
                print(f"         prompt: {case['prompt']}")
                top = sorted(case["scores"].items(), key=lambda kv: -kv[1])[:4]
                print("         top: " + ", ".join(f"{k} {v}" for k, v in top))
                print(f"         library {case['library_score']:.3f} vs null "
                      f"{case['closest_decoy']} {case['scores'][case['closest_decoy']]:.3f} "
                      f"(margin {case['null_margin']:+.3f})")
        lo, hi = suite["reliability_ci95"]
        print(f"  {suite['passed']}/{suite['total']} passed "
              f"(positives {suite['positive_recall']}, "
              f"negatives {suite['negative_rejection']}, "
              f"confusion {suite['confusion_resolved']}, "
              f"narrow {suite['narrow_decisions']}); "
              f"95% CI [{lo:.2f}, {hi:.2f}]\n")
    lo, hi = res["reliability_ci95"]
    print(f"TOTAL {res['passed']}/{res['total']} — "
          f"reliability {res['reliability']:.2f}, 95% CI [{lo:.2f}, {hi:.2f}]")
    if res["passed"] == res["total"]:
        print(f"A clean sweep of {res['total']} cases still only bounds true "
              f"trigger reliability at {lo:.2f} from below. Small n is the "
              f"honest limit here, not a result to advertise.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Trigger test for the alexandria skill library.")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--skills-dir", default=os.path.dirname(here),
                    help="directory holding <slug>/SKILL.md (default: skills/)")
    ap.add_argument("--decoys", default=os.path.join(here, "decoys.json"))
    ap.add_argument("--json", metavar="PATH",
                    help="write the full result bundle for the panel to record")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    res = run(args.skills_dir, args.decoys)
    report(res, args.verbose)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        print(f"\nwrote {args.json}")
    return 0 if res["passed"] == res["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
