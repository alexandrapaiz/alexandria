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
    python3 skills/_validation/trigger_test.py --invariance  # the ENGINE gate
    python3 skills/_validation/trigger_test.py --sweep       # all 255 panels

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
  lexical/3 (2026-09-24, implemented but NOT the default): adds candidate-side
    normalisation, the fix the 2026-09-22 ledger entry proposed. lexical/3
    scores the harmonic mean of lexical/2.1's coverage and a precision term,
    the share of the description's own idf mass the prompt accounts for.
    Select it with --engine lexical/3. It is not the default because the run
    that implemented it also added a skill the engine judges, and a seat does
    not get to change the instrument and the artifact in one commit and call
    the result a pass. Adoption is a separate decision with the two recorded
    bundles side by side.
      This entry used to say that lexical/2.1 "rewards verbosity" and that
    lexical/3 was the fix for it. That is refuted and reversed, 2026-11-02,
    and run_invariance() below is the proof. lexical/2.1's denominator is the
    prompt's idf mass, which no candidate's text can move, so its score is
    *exactly* invariant to any description change that misses the prompt.
    lexical/3 divides by the candidate's own mass, so it is strictly
    decreasing in unmatched description mass. The verbosity defect belongs to
    the challenger alone. lexical/2.1 is monotone non-decreasing in the
    candidate's term set, which is a real property and a different one: a
    description wins more prompts by covering more *terms the prompt uses*,
    never by being longer.
  lexical/2.1 (2026-09-18): same scores as lexical/2, conservative tie
    handling. The pre-registered lexical/2 run produced an exact score tie
    between a library skill and a decoy, which argmax resolved
    alphabetically; a coin flip is not a verdict. A skill must now strictly
    outrank every decoy to fire. No case outcome changed, and the affected
    case is still reported as a zero-margin decision rather than a clean
    pass.
  lexical/2.2 (2026-11-02, current default): identical scoring function,
    three words added to STOPWORDS. "got", "last" and "think" are prompt
    framing rather than topic, and weighting them is what wrote the refuted
    length-bias finding above. This moves scores, so it owes a version
    number; it moves no case. Measured both ways before the change landed:
    61 of 67 either way, the same six cases failing, positives 29/29,
    negatives 15/18, confusion 17/20 in both arms.
      The gate on an engine change is run_invariance(), not the pass rate.
    The pass rate cannot do that job and the number is exact: the two
    engines are paired on the same 67 cases, 58 concordant passes and 6
    concordant failures carry no information about which is better, and the
    three discordant cases all favour the default. Six one-way discordances
    is the floor for any two-sided McNemar verdict at 0.05, so at a
    discordance rate of 3/67 a 67-case suite has power 0.079 against an
    engine that wins every case it differs on, and would need 176 cases.
    Invariance is a property of the scoring function, provable from the code
    at power 1 with no cases at all.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import itertools
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from earned_pass import REFUSAL, verdict                  # noqa: E402
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
USE_WHEN_BOOST = 1.25   # rests on NO published weight; see the block below
ENGINE_VERSION = "lexical/2.2"
ALPHA = 0.05            # 95% intervals

# What a description costs its neighbours is its TERM SET, not its word count.
# LexicalEngine.score sums idf over the prompt's terms and matches against the
# candidate's stem set, so the score is monotone non-decreasing in that set and
# exactly invariant to everything outside it. Incident 31's two skills took a
# neighbour's trigger case by covering more of the prompt's vocabulary, and
# word count is only a weak proxy for that: across the 17 live candidates the
# two correlate at r = 0.286, so word count explains 8 percent of the variance
# in the quantity that decides cases (2026-11-02, verified in panel_audit()).
#
# So there are two separate rules here and they are not interchangeable.
# DESCRIPTION_WORD_MAX is the editorial budget, kept because a 150-word cap is
# what prompts/skill-extract.md states and what a human can hold; it lived in
# that prompt and failed twice, because a rule in a prompt is checked when
# somebody reads the prompt, so the runner carries it too (L-A22).
# PANEL_TERMSET_TOLERANCE is the validity gate, and it is the one that stands
# between the suite and a silently unfair null.
DESCRIPTION_WORD_MAX = 150   # past this, a description is a defect (editorial)
PANEL_LENGTH_TOLERANCE = 1.35  # library:decoy mean-WORD ratio, reported not load-bearing
# Tighter than the word gate on purpose. This is the quantity the score is
# monotone in, and its natural spread is narrower: the 17 live candidates run
# 51 to 70 stems, so a 1.20x gap between the two means is already about twelve
# stems on a 60-stem description, and finding 1d of the 2026-11-02 audit moves
# lexical/3 by 0.031 on four. Tested against an artifact known to fail it
# (L-A21): the retired v1 panel sits at 2.60x on term sets and the live panel
# at 0.95x.
PANEL_TERMSET_TOLERANCE = 1.20  # library:decoy mean distinct-stem ratio
# The third asymmetry, found 2026-11-02 by building the gate above rather than
# by reading. USE_WHEN_BOOST multiplies a candidate's activation-clause terms
# by 1.25, and activation_clause() is a POSITIONAL slice, so what fraction of
# a description gets boosted is decided by where its "Use when" sits. A
# Measured
# today: the decoys carry 94.4 percent of their term set inside the boosted
# slice and the library 79.6, a 0.84x gap, because every decoy opens with its
# activation clause and library descriptions carry more framing prose first.
# Turning the boost off moves three of 67 cases, which is the same count the
# engine choice moves and which the pass rate has power 0.079 to see.
#
# A uniform boost is a no-op on the RANKING and not on the verdict, and the
# distinction is this file's own defect reported back to it by the research
# seat on 2026-11-02. route() reads three things and two of them read an
# absolute number: `library_score >= FLOOR` and `abs(null_margin) <
# NARROW_MARGIN`. A uniform boost scales both. Measured: off and uniform agree
# on all 67 fired decisions and disagree on one narrow flag, he-conf-2 at
# +0.0179 against +0.0224, across the 0.02 threshold. So the no-op is a
# property of THIS PANEL rather than of the scheme, and a comparison that
# prints only the fired decision cannot see it.
#
# The coefficient itself had no evidence behind it and now has evidence
# against it (2026-11-02, skills/_validation/use_when_evidence.py, after the
# research seat answered this seat's queued question by reading both ids in
# full):
#   arXiv:2510.22670 ablates a when-to-use field add-one and one-out on a
#     dense and a sparse retriever over thirty-five unified datasets and keeps
#     it; the field its authors drop is example-usage. HAVING the clause is
#     supported. Its section 4.1 is the finding, and its 2.2 carries a
#     sentence naming the wrong field that reverses it.
#   arXiv:2602.05366 publishes learned per-field weights, and this library
#     cited them against USE_WHEN_BOOST until 2026-11-02. **That magnitude
#     citation is WITHDRAWN.** The row is Table 5's `examples`, and the
#     research seat settled the field identification by fetching both papers:
#     `examples` is 22670's `example_usage`, which holds query text, and not
#     its `when_to_use`, which holds the activation clause. The per-field
#     definition says "representative user intents", the query side aligns the
#     field with "a concrete user utterance", and Table 4's cells hold strings
#     like "clean up podcast recordings by removing background noise". So the
#     0.269x-1.363x range (median 0.695x, below description in five of six) is
#     a weight on somebody else's field. It could not have transferred even if
#     the fields had matched, because MFTR scores `examples` against the
#     query's own intent field, making part of that weight query-to-query
#     homophily, and an activation condition is not query text.
# So the literature supports HAVING the clause and rules out a constant in
# either direction on 05366's own methodological conclusion. **There is no
# published weight for this field at all, so 1.25 is undefended rather than
# contradicted**, and the reason not to retune it is the sweep measurement
# below rather than the literature. Full reconciliation:
# docs/research/notes/2026-11-02-field-identification.md.
#
# The coefficient is NOT retuned here, and the reason is a measurement rather
# than caution. Swept over the published range, this suite's pass rate runs 48
# to 61 of 67 through the positional slice, and under a uniform boost every
# arm at 0.5x and above scores exactly 60. All of the suite's apparent
# preference for a high coefficient is the 0.84x asymmetry, so tuning 1.25 on
# the pass rate would be tuning on a confound, and the prerequisite repair is
# the panel rewrite already queued as decoy panel v3. arXiv:2602.05366 lands
# the same warning independently: the variant that applies field weights to
# raw unstandardized documentation is the one that fluctuates, and its
# conclusion is that a unified schema is the prerequisite. A positional slice
# of free prose is that variant, and the 0.84x is what it costs.
#
# One consequence for the failure list. The boost's three moved cases are +2
# and -1 rather than a net of one: it wins cwe-neg-1 and rhsi-conf-1 and
# LOSES he-conf-2, which is one of the six the suite reports as failing today.
# he-conf-2 passes at boost off and under a uniform boost, and fails live at
# -0.0034. So today's 61 of 67 is five library failures and one instrument
# artifact.
PANEL_BOOST_TOLERANCE = 1.15  # library:decoy boosted-share ratio
# Measured on the STEM COUNT, which is not the quantity the boost multiplies:
# score() weights by idf mass. Both readings trip this tolerance, 0.8435x on
# stems and 0.8538x on idf mass, so the finding stands either way and the gap
# is recorded rather than repaired (2026-11-02).

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
    # Added 2026-11-02. These three are prompt framing, not topic, and giving
    # them idf weight is what produced the 2026-09-30 "length bias" result:
    # the whole published +0.1353 for lexical/2.1 between a 41-word and a
    # 123-word decoy was the single word "last", out of "after the last
    # release" (reproduced at +0.1311 against today's nine-skill library,
    # which recomputes idf; the decomposition is the same either way).
    #
    # The three are NOT interchangeable, and this is the half the first
    # version of this comment left out (2026-11-02, decomposed by the research
    # seat and reproduced in use_when_evidence.py). Only "last" is
    # load-bearing: making it alone a stopword takes the delta to zero.
    # Stripping either of the other two ALONE grows the delta to +0.1501,
    # because both sit in the prompt and in neither description, so removing
    # one shrinks the denominator and leaves the numerator untouched. So the
    # case for "got" and "think" is that they are framing, which is an
    # editorial argument, and not that they carried the length bias, which
    # they did not.
    #
    # Measured before changing it, and on more than the pass rate, which is
    # the other half the first version understated: the suite scores 61/67
    # with and without them, the same six cases failing either way, and the
    # three also move no narrow flag and move nothing across the floor. So the
    # change is clean on every field the bundle carries rather than on the
    # headline number alone, and it removes a term that can only mislead the
    # instrument.
    "got", "last", "think",
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


def word_count(text: str) -> int:
    """Whitespace words, counted the way the 150-word budget in
    prompts/skill-extract.md was measured, so the number here is the number
    that rule talks about."""
    return len(text.split())


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


def refuse_unresolved(flag: str, value: str, what: str, found) -> None:
    """Refuse a flag value that nothing in this checkout carries, by name.

    The engineer seat measured the class on 2026-11-02: across the tools tree
    fifty-six flags name something a tool could resolve, and three of the eight
    probed answered a confident zero with exit zero. The worst was the panel
    validator, whose verdicts gate promotion. This seat probed its own six
    instruments the same way and found the same defect twice, in
    `prediction_basis.py` and `project_fixture_probe.py`, plus two more that
    refused only by traceback. A zero that means "nothing matched" and a zero
    that means "the path was wrong" must not print the same.
    """
    if found:
        return
    raise SystemExit(
        f"{flag} {value!r}: no {what} found there, so there is nothing to "
        f"measure. This is a refusal and not a result of zero."
    )


def load_decoys(path: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit(
            f"--decoys {path!r}: no such file, so there is nothing to measure. "
            f"This is a refusal and not a result of zero."
        )
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

    def _description_mass(self, key: str) -> float:
        body, _ = self.sets[key]
        return sum(self.idf.get(t, self.default_idf) for t in body)

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


class NormalisedLexicalEngine(LexicalEngine):
    """lexical/3: coverage and precision, harmonic mean, no length bonus.

    Coverage is lexical/2.1's score, the share of the prompt's idf mass the
    description matches. Precision is the share of the description's own idf
    mass the prompt accounts for. A description that lists everything scores
    high on the first and low on the second, which is the behaviour the
    2026-09-22 finding asked for: a skill wins a prompt by being about it, not
    by being long. Decoys are short and therefore precise, so this engine
    makes silence easier to earn as well.
    """

    name = "lexical/3"

    def score(self, prompt: str, key: str) -> float:
        coverage = super().score(prompt, key)
        if coverage <= 0:
            return 0.0
        body, _ = self.sets[key]
        prompt_terms = set(tokens(prompt))
        mass = self._description_mass(key)
        if mass <= 0:
            return 0.0
        matched = sum(self.idf.get(t, self.default_idf)
                      for t in body if t in prompt_terms)
        precision = matched / mass
        if precision <= 0:
            return 0.0
        return 2 * coverage * precision / (coverage + precision)


ENGINES = {
    ENGINE_VERSION: LexicalEngine,
    NormalisedLexicalEngine.name: NormalisedLexicalEngine,
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

def run(skills_dir: str, decoys_path: str,
        engine_version: str = ENGINE_VERSION) -> dict:
    skills = load_skills(skills_dir)
    if not skills:
        raise SystemExit(f"no skills found under {skills_dir}")
    decoys = load_decoys(decoys_path)
    clash = set(skills) & set(decoys)
    if clash:
        raise SystemExit(f"decoy name collides with a real skill: {clash}")
    engine = ENGINES[engine_version]({**skills, **decoys})

    warnings = [f"{sk['path']}: description states no 'Use when' activation "
                f"conditions" for sk in skills.values() if not sk["activation"]]

    # Incident 31's fix: measure the length at the moment anything ships.
    warnings += [f"{sk['path']}: description is {word_count(sk['description'])} "
                 f"words, past the {DESCRIPTION_WORD_MAX}-word budget; a longer "
                 f"description outranks a terser one on any prompt both cover"
                 for sk in skills.values()
                 if word_count(sk["description"]) > DESCRIPTION_WORD_MAX]

    # The same defect at panel scale. A null model systematically narrower
    # than the library it nulls decides negative cases by breadth of
    # vocabulary rather than by topic.
    audit = panel_audit(skills, decoys)
    warnings += audit.pop("warnings")

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
        if not results:
            # Before 2026-11-02 this fell through to `passed / len(results)`
            # and died on a ZeroDivisionError, which exits 1, which is this
            # file's code for "a case failed". A new skill shipped with
            # `"cases": []` therefore read as a trigger-suite failure rather
            # than as a suite nobody had written yet. It is a data error.
            raise SystemExit(
                f"{cf}: the suite carries no cases, so there is nothing to "
                "measure for " + owner + ". " + REFUSAL.format(
                    gate="trigger test", unit="cases"))
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
    all_cases = [c for s in suites for c in s["cases"]]
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
            "pre_registered": engine.name == ENGINE_VERSION,
        },
        "library": {k: {"path": v["path"], "sha256": v["sha256"]}
                    for k, v in skills.items()},
        # Kept under its old key as well, because every recorded bundle and
        # every reader of one indexes "length_audit". The new key is the one
        # that carries the load-bearing number.
        "length_audit": audit,
        "panel_audit": audit,
        "warnings": warnings,
        "suites": suites,
        "passed": total_pass,
        "total": total_cases,
        "reliability": round(total_pass / total_cases, 4) if total_cases else 0.0,
        "reliability_ci95": clopper_pearson(total_pass, total_cases),
        # One averaged reliability hides the thing the panel actually does.
        # The three case kinds depend on the panel with opposite signs
        # (r = +0.82, -0.43 and +0.11 against panel size over all 255
        # subsets), so the average is the one number that cannot be read.
        "by_kind": {kind: _kind_block(all_cases, kind)
                    for kind in ("positive", "negative", "confusion")},
    }


def _kind_block(cases: list[dict], kind: str) -> dict:
    sel = [c for c in cases if c["kind"] == kind]
    k, n = sum(1 for c in sel if c["passed"]), len(sel)
    return {
        "passed": k,
        "total": n,
        "rate": round(k / n, 4) if n else 0.0,
        "ci95": clopper_pearson(k, n),
        "failed": [c["id"] for c in sel if not c["passed"]],
    }


def panel_audit(skills: dict, decoys: dict) -> dict:
    """Is the null model a fair one?

    Two ratios, and only the second decides anything. Word count is the
    editorial budget. The distinct stemmed term set is what both engines'
    scores are functions of, and across the 17 live candidates the two
    correlate at r = 0.286. The guard watched word count alone from
    2026-09-30 to 2026-11-02 and was valid only because the retired v1 panel
    happened to be skewed on both at once (3.34x words, 2.60x term sets). At
    the margin the panel now occupies it is blind: 1.11x on words, inside
    tolerance, and 0.95x on term sets, which nothing was looking at.
    """
    def means(group, fn):
        vals = [fn(c["description"]) for c in group.values()]
        return sum(vals) / len(vals) if vals else 0.0

    def termset(text: str) -> int:
        return len(set(tokens(text)))

    def boosted_share(c: dict) -> float:
        body = set(tokens(c["description"]))
        return len(set(tokens(c["activation"])) & body) / len(body) if body else 0.0

    def share_mean(group):
        vals = [boosted_share(c) for c in group.values()]
        return sum(vals) / len(vals) if vals else 0.0

    lib_words, dec_words = means(skills, word_count), means(decoys, word_count)
    lib_stems, dec_stems = means(skills, termset), means(decoys, termset)
    lib_boost, dec_boost = share_mean(skills), share_mean(decoys)
    word_ratio = lib_words / dec_words if dec_words else float("inf")
    stem_ratio = lib_stems / dec_stems if dec_stems else float("inf")
    boost_ratio = lib_boost / dec_boost if dec_boost else float("inf")

    warnings = []
    if (boost_ratio > PANEL_BOOST_TOLERANCE
            or boost_ratio < 1 / PANEL_BOOST_TOLERANCE):
        favoured = "library" if boost_ratio > 1 else "decoy panel"
        warnings.append(
            f"decoy panel: the {favoured} gets more of its vocabulary inside "
            f"the {USE_WHEN_BOOST}x activation boost, {lib_boost:.1%} of the "
            f"library's term set against {dec_boost:.1%} of the panel's, a "
            f"{boost_ratio:.2f}x gap past the {PANEL_BOOST_TOLERANCE}x "
            f"tolerance; activation_clause() is a positional slice, so this "
            f"is word order deciding cases. Measured at 3 cases on 2026-11-02, "
            f"when the suite held 67; the figure is dated rather than live "
            f"because nothing in this function recomputes it, and it read "
            f"'3 of 67 today' until the suite reached 68. The "
            f"repair is a panel rewrite that matches the library's boosted "
            f"share, and it is deliberately NOT done in the same commit that "
            f"reports a pass rate")
    if (stem_ratio > PANEL_TERMSET_TOLERANCE
            or stem_ratio < 1 / PANEL_TERMSET_TOLERANCE):
        wider = "library" if stem_ratio > 1 else "decoy panel"
        warnings.append(
            f"decoy panel: the {wider} averages the wider vocabulary, "
            f"{lib_stems:.1f} distinct stems against {dec_stems:.1f}, a "
            f"{stem_ratio:.2f}x gap past the {PANEL_TERMSET_TOLERANCE}x "
            f"tolerance; both engines are monotone in the term set, so "
            f"negative cases are partly decided by vocabulary breadth "
            f"rather than by topic")
    if (word_ratio > PANEL_LENGTH_TOLERANCE
            or word_ratio < 1 / PANEL_LENGTH_TOLERANCE):
        warnings.append(
            f"decoy panel: mean word counts are {lib_words:.0f} against "
            f"{dec_words:.0f}, a {word_ratio:.2f}x gap past the "
            f"{PANEL_LENGTH_TOLERANCE}x editorial tolerance; this is a "
            f"readability signal, not a validity one, and the term-set "
            f"ratio above is the gate")
    return {
        "budget_words": DESCRIPTION_WORD_MAX,
        "panel_tolerance": PANEL_LENGTH_TOLERANCE,
        "termset_tolerance": PANEL_TERMSET_TOLERANCE,
        "library_mean_words": round(lib_words, 1),
        "decoy_mean_words": round(dec_words, 1),
        "ratio": round(word_ratio, 3),
        "library_mean_termset": round(lib_stems, 1),
        "decoy_mean_termset": round(dec_stems, 1),
        "termset_ratio": round(stem_ratio, 3),
        "boost_tolerance": PANEL_BOOST_TOLERANCE,
        "library_mean_boosted_share": round(lib_boost, 4),
        "decoy_mean_boosted_share": round(dec_boost, 4),
        "boosted_share_ratio": round(boost_ratio, 3),
        "gate": ["termset_ratio", "boosted_share_ratio"],
        "over_budget": sorted(sk["name"] for sk in skills.values()
                              if word_count(sk["description"])
                              > DESCRIPTION_WORD_MAX),
        "warnings": warnings,
    }


def _rate(results: list[dict], kind: str) -> str:
    sel = [r for r in results if r["kind"] == kind]
    if not sel:
        return "0/0"
    return f"{sum(1 for r in sel if r['passed'])}/{len(sel)}"


def report(res: dict, verbose: bool) -> None:
    p = res["policy"]
    stance = ("policy pre-registered" if p["pre_registered"]
              else "EXPERIMENT, not the pre-registered policy")
    print(f"trigger test — engine {res['engine']}, floor {p['floor']}, "
          f"{p['decoy_count']} decoys ({stance})")
    a = res["panel_audit"]
    print(f"library: {len(res['library'])} skills, {res['total']} cases")
    print(f"panel:   term sets {a['library_mean_termset']:.1f} library vs "
          f"{a['decoy_mean_termset']:.1f} decoy = {a['termset_ratio']:.2f}x "
          f"(gate, tolerance {a['termset_tolerance']}x)")
    print(f"         boosted share {a['library_mean_boosted_share']:.1%} vs "
          f"{a['decoy_mean_boosted_share']:.1%} = "
          f"{a['boosted_share_ratio']:.2f}x "
          f"(gate, tolerance {a['boost_tolerance']}x)")
    print(f"         words {a['library_mean_words']:.0f} vs "
          f"{a['decoy_mean_words']:.0f} = {a['ratio']:.2f}x "
          f"(editorial, not load-bearing)\n")
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
    print("  and that average is the one number here that cannot be read, "
          "because the three kinds move against the panel in opposite "
          "directions (--sweep):")
    for kind in ("positive", "negative", "confusion"):
        b = res["by_kind"][kind]
        klo, khi = b["ci95"]
        fail = (", failing " + ", ".join(b["failed"])) if b["failed"] else ""
        print(f"    {kind:<10} {b['passed']}/{b['total']} = "
              f"{b['rate']:.3f}  95% CI [{klo:.2f}, {khi:.2f}]{fail}")
    if res["passed"] == res["total"]:
        print(f"A clean sweep of {res['total']} cases still only bounds true "
              f"trigger reliability at {lo:.2f} from below. Small n is the "
              f"honest limit here, not a result to advertise.")


# ---------------------------------------------------------------------------
# The engine gate (--invariance)
#
# This, and not the pass rate, is what an engine change has to clear.
#
# The pass rate cannot do the job, and the number is exact rather than a
# worry. The two engines run on the same cases, so the design is paired: on
# the current suite 58 cases are concordant passes and 6 are concordant
# failures, and those 64 carry zero information about which engine is better.
# Three cases are discordant and all three favour the default. Two-sided
# exact McNemar on three is p = 0.25, and six one-way discordances is the
# floor for any verdict at 0.05 no matter how many concordant cases sit
# behind them. At a discordance rate of 3/67 that leaves a 67-case suite with
# power 0.079 against an engine that wins every case it differs on, 0.041 at
# nine in ten, 0.020 at four in five. It would take 176 cases for the first
# and 1,601 for a 2-to-1 edge.
#
# Invariance is not a rate to be estimated. It is a property of the scoring
# function, decided by the code in under a second with power 1 and variance
# 0. So it is pre-registered here as the gate, and the pass rate stands as a
# regression check rather than as the arbiter of engine choice.
# ---------------------------------------------------------------------------

INVARIANCE_FILLER = (
    "kubernetes sidecar istio helm terraform ansible jenkins grafana "
    "prometheus loki tempo thanos karpenter cilium envoy nomad consul vault "
    "packer vagrant")


def run_invariance(skills_dir: str, decoys_path: str) -> list[str]:
    """Three properties, proved rather than sampled. Returns failures.

    1. Both engines discard multiplicity, given the activation slice. The
       tokenizer builds a set, so repeating a description cannot move either
       term set and therefore cannot move a score. This is the property the
       2026-09-30 engine-decision doc believed it had refuted; its test
       varied length by *rewriting* the candidate, which moved the term set
       too, and the whole published +0.1353 for lexical/2.1 decomposes to one
       shared word plus a negligible idf shift.
    2. lexical/2.1 and 2.2 are exactly invariant to unmatched description
       mass. The denominator is the prompt's idf mass, which no candidate's
       text can move, so a description can only gain by covering terms the
       prompt actually uses.
    3. lexical/3 is strictly decreasing in unmatched description mass,
       because it divides by the candidate's own mass. The verbosity defect
       the 2026-09-22 ledger entry attributed to the default belongs to the
       challenger, and to it alone.
    """
    skills = load_skills(skills_dir)
    decoys = load_decoys(decoys_path)
    cand = {**skills, **decoys}
    key = sorted(decoys)[0]
    prompt = next(iter(skills.values()))["description"]
    base = cand[key]["description"]
    failures = []

    def scores(text):
        c = dict(cand)
        c[key] = {**cand[key], "description": text,
                  "activation": activation_clause(text)}
        return (LexicalEngine(c).score(prompt, key),
                NormalisedLexicalEngine(c).score(prompt, key))

    print("invariance gate — properties of the scoring function, not a "
          "sample of cases\n")

    def scores_fixed_activation(text):
        """The activation slice held at the real description's, so this
        isolates the tokenizer's set semantics from the positional slice
        property 4 measures."""
        c = dict(cand)
        c[key] = {**cand[key], "description": text,
                  "activation": cand[key]["activation"]}
        return (LexicalEngine(c).score(prompt, key),
                NormalisedLexicalEngine(c).score(prompt, key))

    # 1. multiplicity, given the activation slice
    ref = scores_fixed_activation(base)
    print(f"  1. multiplicity discarded, activation slice held "
          f"(candidate {key})")
    for mult in (1, 2, 3, 5, 9):
        text = " ".join([base] * mult)
        set_same = set(tokens(text)) == set(tokens(base))
        got = scores_fixed_activation(text)
        ok = got == ref and set_same
        print(f"       x{mult}: {word_count(text):4d} words, "
              f"{len(set(tokens(text))):3d} stems -> "
              f"2.x {got[0]:.6f}  3 {got[1]:.6f}  {'ok' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"multiplicity moved a score at x{mult}: "
                            f"{ref} -> {got}")

    # 2 and 3. unmatched mass, both directions at once
    pool = [w for w in INVARIANCE_FILLER.split()
            if stem(w) not in set(tokens(prompt))]
    print(f"  2. lexical/{ENGINE_VERSION.split('/')[1]} invariant to "
          f"unmatched mass; 3. lexical/3 strictly decreasing")
    prev3 = None
    for n in (0, 4, 8, 12, 16, 20):
        s2, s3 = scores(base + " " + " ".join(pool[:n]))
        inv_ok = abs(s2 - ref[0]) < 1e-12
        dec_ok = prev3 is None or s3 < prev3 - 1e-12
        print(f"       +{n:2d} unmatched stems -> "
              f"2.x {s2:.6f} {'ok' if inv_ok else 'FAIL'}   "
              f"3 {s3:.6f} {'ok' if dec_ok else 'FAIL'}")
        if not inv_ok:
            failures.append(f"the default engine moved by {s2 - ref[0]:+.2e} "
                            f"on {n} unmatched stems; it must not move at all")
        if not dec_ok:
            failures.append(f"lexical/3 did not strictly decrease at {n} "
                            f"unmatched stems: {prev3} -> {s3}")
        prev3 = s3

    # 4. the one place the engine reads word order rather than a set.
    # Not a pass/fail assertion, because it is documented policy as of
    # 2026-11-02 rather than a regression, and the asymmetry it creates is
    # gated in panel_audit(). It is printed because it is the exception to
    # everything above, and a reader who takes "the score is a function of
    # the term set" away from properties 1 to 3 has read it slightly wrong.
    print("  4. NOT invariant: activation_clause() is a positional slice, so "
          "the 1.25x boost reads word order")
    ref_pos = scores(base)
    for mult in (1, 2, 3):
        text = " ".join([base] * mult)
        got = scores(text)
        boosted = len(set(tokens(activation_clause(text)))
                      & set(tokens(text))) / len(set(tokens(text)))
        print(f"       x{mult}: boosted share {boosted:.1%} -> "
              f"2.x {got[0]:.6f} ({got[0] - ref_pos[0]:+.6f})   "
              f"3 {got[1]:.6f} ({got[1] - ref_pos[1]:+.6f})")
    print("       Duplication is a pathological input and never occurs in the "
          "library, but the same lever is live at scale: where a description "
          "puts its 'Use when' decides how much of it the boost covers, and "
          "the panel is asymmetric on exactly that today.")

    print()
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        print(f"\ninvariance: {len(failures)} properties violated. An engine "
              f"that fails this is not a candidate, whatever its pass rate.")
    else:
        print("invariance: 3 of 3 properties hold. Power 1, no cases, no "
              "model call. This is the pre-registered engine gate; the pass "
              "rate below it has power 0.079 against the same question.")
    return failures


# ---------------------------------------------------------------------------
# The panel sweep (--sweep)
#
# arxiv:2604.24594 section 5.2.1 publishes a curve over distractor count
# rather than one cell, and the reason applies here: a single reliability
# figure at one panel is a measurement of that panel as much as of the
# library. Every non-empty subset of the decoys is affordable at eight, so
# the whole curve is reported rather than sampled.
# ---------------------------------------------------------------------------

def run_sweep(skills_dir: str, decoys_path: str,
              engine_version: str = ENGINE_VERSION) -> dict:
    skills = load_skills(skills_dir)
    all_decoys = load_decoys(decoys_path)
    names = sorted(all_decoys)
    cases = []
    for cf in sorted(glob.glob(os.path.join(skills_dir, "*", "triggers.json"))):
        for c in json.load(open(cf, encoding="utf-8"))["cases"]:
            cases.append(c)

    rows = []
    for r in range(1, len(names) + 1):
        for sub in itertools.combinations(names, r):
            engine = ENGINES[engine_version](
                {**skills, **{k: all_decoys[k] for k in sub}})
            per = {"positive": [0, 0], "negative": [0, 0], "confusion": [0, 0]}
            ok = 0
            for c in cases:
                passed = engine.route(c["prompt"])["fired"] == c.get("expect")
                ok += passed
                per[c["kind"]][0] += passed
                per[c["kind"]][1] += 1
            rows.append({
                "size": r,
                "decoys": list(sub),
                "reliability": round(ok / len(cases), 4),
                "by_kind": {k: round(v[0] / v[1], 4) if v[1] else 0.0
                            for k, v in per.items()},
            })

    rels = [row["reliability"] for row in rows]
    full = next(row for row in rows if row["size"] == len(names))
    out = {
        "subsets": len(rows),
        "cases": len(cases),
        "engine": engine_version,
        "reliability_min": min(rels),
        "reliability_max": max(rels),
        "reliability_at_full_panel": full["reliability"],
        "worst_panel": min(rows, key=lambda row: row["reliability"]),
        "best_panel": max(rows, key=lambda row: row["reliability"]),
        "by_size": {},
        "kind_correlation_with_panel_size": {},
    }
    for r in range(1, len(names) + 1):
        sel = [row for row in rows if row["size"] == r]
        v = [row["reliability"] for row in sel]
        out["by_size"][r] = {
            "panels": len(sel),
            "min": min(v), "max": max(v),
            "mean": round(sum(v) / len(v), 4),
            "by_kind_mean": {
                k: round(sum(row["by_kind"][k] for row in sel) / len(sel), 4)
                for k in ("positive", "negative", "confusion")},
        }
    sizes = [row["size"] for row in rows]
    for kind in ("positive", "negative", "confusion"):
        out["kind_correlation_with_panel_size"][kind] = round(
            _pearson(sizes, [row["by_kind"][kind] for row in rows]), 3)
    return out


def _pearson(x: list, y: list) -> float:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    vx = sum((a - mx) ** 2 for a in x)
    vy = sum((b - my) ** 2 for b in y)
    return cov / math.sqrt(vx * vy) if vx * vy else float("nan")


def report_sweep(sw: dict) -> None:
    print(f"panel sweep — engine {sw['engine']}, {sw['subsets']} non-empty "
          f"decoy subsets, {sw['cases']} cases, library fixed\n")
    print(f"  reliability spans {sw['reliability_min']:.4f} to "
          f"{sw['reliability_max']:.4f}; the published cell, the full panel, "
          f"is {sw['reliability_at_full_panel']:.4f}")
    print(f"  worst: {sw['worst_panel']['reliability']:.4f} at "
          f"{len(sw['worst_panel']['decoys'])} decoys "
          f"{sw['worst_panel']['decoys']}")
    print(f"  best:  {sw['best_panel']['reliability']:.4f} at "
          f"{len(sw['best_panel']['decoys'])} decoys "
          f"{sw['best_panel']['decoys']}")
    print("\n  size  panels     min     max    mean | positive negative confusion")
    for size, b in sw["by_size"].items():
        k = b["by_kind_mean"]
        print(f"  {size:>4}  {b['panels']:>6}  {b['min']:.4f}  {b['max']:.4f}  "
              f"{b['mean']:.4f} |   {k['positive']:.4f}   {k['negative']:.4f}    "
              f"{k['confusion']:.4f}")
    print("\n  correlation of each kind's rate with panel size:")
    for kind, r in sw["kind_correlation_with_panel_size"].items():
        print(f"    {kind:<10} r = {r:+.3f}")
    print("\n  The three signs are not the same, which is why one averaged "
          "reliability is unreadable: a wider panel buys negative-case "
          "rejection and costs confusion resolution. The maximum in this "
          "table is not a target. Choosing the subset that scores best "
          "would be tuning the instrument to the library, which is the one "
          "thing a null model may never do.")


# ---------------------------------------------------------------------------
# Is every receipt about today's text? (--receipts)
#
# A result bundle pins a per-skill `skill_sha256`, because a pass rate carried
# over from an earlier revision is a claim about a document the reader cannot
# see. tests/test_skill_receipts.py asserts that every skill the page receives
# has a receipt describing today's file, and site/lib/skill-provenance.js tells
# the reader when it does not.
#
# That invariant spans two files, SKILL.md and the newest bundle under
# results/, and a run edits the first several commits before it writes the
# second. CI runs on every push, so the branch is red by construction for the
# window in between, and the receipts step has gone red that way on this seat's
# branches on 2026-10-13 and twice on 2026-10-24
# (INC-2026-10-24-the-receipts-step-has-been-red-on-four-of-this-seats-branches).
#
# Incident 31's lesson is the reason this lives here rather than in a prompt: a
# rule written into a prompt is checked when someone reads the prompt, and a
# rule written into the runner is checked every time anything ships. This mode
# is offline and takes no engine, so it costs nothing to run before a commit.
# ---------------------------------------------------------------------------

def rank_bundles(bundles: list[dict]) -> list[dict]:
    """The ranking rule of rankBundles() in site/lib/skill-provenance.js, and
    it has to stay the same rule or this check and the page disagree about
    which bundle is the library's result. Newest first, and at one date the
    pre-registered engine wins, because an experimental engine's run measures
    the engine rather than judging the skill."""
    usable = [b for b in bundles if isinstance(b.get("generated"), str)]
    return sorted(
        usable,
        key=lambda b: (
            _NEGATED(b["generated"]),
            0 if (b.get("policy") or {}).get("pre_registered") else 1,
        ),
    )


class _NEGATED:
    """Descending order on a string key without reversing the whole sort, so
    the pre-registered tie-break still reads ascending."""

    __slots__ = ("s",)

    def __init__(self, s: str) -> None:
        self.s = s

    def __lt__(self, other: "_NEGATED") -> bool:
        return self.s > other.s

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _NEGATED) and self.s == other.s


def load_bundles(results_dir: str) -> list[dict]:
    out = []
    for path in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_path"] = os.path.relpath(path)
            out.append(data)
    return out


def latest_receipt(bundles: list[dict], skill: str) -> dict | None:
    for bundle in rank_bundles(bundles):
        for suite in bundle.get("suites") or []:
            if not isinstance(suite, dict):
                continue
            if suite.get("skill") == skill and suite.get("total"):
                return {
                    "date": bundle.get("generated", ""),
                    "engine": bundle.get("engine", ""),
                    "path": bundle.get("_path", ""),
                    "sha256": suite.get("skill_sha256", ""),
                    "passed": suite.get("passed", 0),
                    "total": suite.get("total", 0),
                }
    return None


def check_receipts(skills_dir: str, results_dir: str) -> int:
    """Print, per skill, whether the newest recorded receipt describes the
    file as it stands now. Returns the number of skills that fail, which is
    the number tests/test_skill_receipts.py will fail on."""
    skills = load_skills(skills_dir)
    bundles = load_bundles(results_dir)
    stale = []
    print(f"receipts: {len(skills)} skills against "
          f"{len(bundles)} result bundles in {os.path.relpath(results_dir)}\n")
    for name in sorted(skills):
        sha = skills[name]["sha256"]
        receipt = latest_receipt(bundles, name)
        if receipt is None:
            stale.append(name)
            print(f"  MISSING  {name}: no bundle scores this skill, so the page "
                  f"has no receipt to show")
            continue
        if receipt["sha256"] == sha:
            print(f"  ok       {name}: {receipt['passed']}/{receipt['total']} on "
                  f"{receipt['date']}, sha {sha}")
            continue
        stale.append(name)
        print(f"  STALE    {name}: SKILL.md is sha {sha}, newest receipt "
              f"({receipt['date']}, {receipt['path']}) measured "
              f"{receipt['sha256']}")
    if stale:
        print(f"\n{len(stale)} of {len(skills)} receipts do not describe today's "
              f"text: {', '.join(stale)}.")
        print("The page will say so and tests/test_skill_receipts.py will fail. "
              "Re-run the trigger test and commit its bundle in the same commit "
              "as the SKILL.md edit, not a later one:")
        print("  python3 skills/_validation/trigger_test.py "
              "--json skills/_validation/results/<date>-<engine>-<slug>.json")
    elif skills:
        print(f"\nall {len(skills)} receipts describe today's text.")
    return len(stale)


# Is every skill's frontmatter loadable by the consumer that loads skills?
# (--frontmatter, folded into --receipts)
#
# This file's own parse_frontmatter and site/lib/skill-provenance.js both read
# the block with regexes, so both accept frontmatter no YAML parser will load.
# On 2026-10-26 two of nine shipped skills were in exactly that state:
# `description:` carried an unquoted ": " in its prose, which makes the whole
# document invalid YAML, and nothing in this repository noticed because nothing
# in this repository parses it as YAML. An agent harness does. A skill that a
# consumer cannot load fires zero percent of the time, which is the failure this
# library's differentiator is defined against, so it is checked here rather than
# left to the first consumer to discover.
#
# The check needs PyYAML, which neither requirements file declares, so the
# import failing is the ordinary case rather than the strange one. Until
# 2026-10-27 the import failure returned 0, which is the same value a clean
# tree returns, so `--receipts` exited green on a tree carrying two skills no
# consumer could load. Measured on one unchanged broken skill: 1 and exit 1
# with PyYAML, 0 and exit 0 without it. A count is the wrong return type for a
# check that did not run, so the skip path returns the sentinel below instead.
# It is truthy on purpose: any caller that writes `if unloadable:` now fails
# closed, and a caller that wants the reason gets a sentence rather than a
# number it would have to guess the meaning of.
class SkippedGate:
    """Stand-in for a count the gate never computed. Truthy, so it fails
    closed, and it prints the reason it did not run."""

    def __init__(self, reason: str) -> None:
        self.reason = reason

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        return self.reason


NO_YAML = SkippedGate(
    "the frontmatter check did not run, because PyYAML is not installed. "
    "A skipped gate is not a pass. Install it with `pip install pyyaml` and "
    "run this command again.")


def check_frontmatter(skills_dir: str) -> int | SkippedGate:
    """Load every SKILL.md frontmatter with a real YAML parser. Returns the
    number that fail, which is the number of skills a consumer cannot load,
    or NO_YAML when the parser is missing and no number was computed."""
    try:
        import yaml
    except ImportError:
        print("frontmatter: PyYAML is not installed, so this check did not "
              "run. That is a skipped gate, not a pass.")
        return NO_YAML
    paths = sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md")))
    bad = []
    print(f"\nfrontmatter: {len(paths)} skills parsed with PyYAML")
    for path in paths:
        slug = os.path.basename(os.path.dirname(path))
        raw = open(path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", raw, re.S)
        if not m:
            bad.append(slug)
            print(f"  NO BLOCK {slug}: no frontmatter delimited by ---")
            continue
        try:
            loaded = yaml.safe_load(m.group(1))
        except yaml.YAMLError as exc:
            bad.append(slug)
            first = str(exc).split("\n")[0]
            print(f"  INVALID  {slug}: {first}")
            continue
        if not isinstance(loaded, dict) or not loaded.get("description"):
            bad.append(slug)
            print(f"  EMPTY    {slug}: parses, but carries no description")
            continue
        print(f"  ok       {slug}")
    if bad:
        print(f"\n{len(bad)} of {len(paths)} skills have frontmatter a YAML "
              f"consumer cannot load: {', '.join(bad)}.")
        print("The usual cause is a colon followed by a space inside an "
              "unquoted description. Wrap the value in double quotes; both "
              "readers in this repository strip them, so the text a router "
              "scores does not change.")
    elif paths:
        print(f"\nall {len(paths)} skills load under a YAML parser.")
    return len(bad)


# Is every description inside the editorial word budget?
# (--budget, folded into --receipts)
#
# DESCRIPTION_WORD_MAX has been carried by run() since incident 31 and carried
# there as a WARNING, which means it is read by whoever reads the bundle's
# `warnings` array. On 2026-11-02 this seat shipped a 171-word description to
# carry two new activation conditions, the warning was printed, and the cost
# landed somewhere nobody would look for it: `evaluation-integrity`'s first
# negative case went from silence to firing `agent-security-measurement` at a
# null margin of 0.005. The seat that caused it is not the seat whose case goes
# red, and the suite's exit code does not distinguish the two, so the warning
# was still true and still unenforced.
#
# So it moves next to the frontmatter check, which is the sibling defect with
# the sibling remedy: both are properties of one description that a seat can
# only have broken in the edit it is about to commit, and `--receipts` is the
# mode that edit is told to run. No engine, no cases, no model call.
def check_budget(skills_dir: str) -> int:
    """Count the descriptions past DESCRIPTION_WORD_MAX. Returns the number
    over budget, which is the number of skills that outrank their neighbours
    on breadth of vocabulary rather than on topic."""
    skills = load_skills(skills_dir)
    over = []
    print(f"\nbudget: {len(skills)} descriptions against the "
          f"{DESCRIPTION_WORD_MAX}-word editorial budget")
    for name in sorted(skills):
        words = word_count(skills[name]["description"])
        if words > DESCRIPTION_WORD_MAX:
            over.append(name)
            print(f"  OVER     {name}: {words} words, "
                  f"{words - DESCRIPTION_WORD_MAX} past the budget")
            continue
        print(f"  ok       {name}: {words} words")
    if over:
        print(f"\n{len(over)} of {len(skills)} descriptions are past the "
              f"{DESCRIPTION_WORD_MAX}-word budget: {', '.join(over)}.")
        print("A longer description outranks a terser one on any prompt both "
              "cover, and the case that goes red is usually another skill's. "
              "Cut the description, then re-run the trigger test, because the "
              "bundle you are about to commit measures a composition that "
              "includes this one.")
    elif skills:
        print(f"\nall {len(skills)} descriptions are inside the "
              f"{DESCRIPTION_WORD_MAX}-word budget.")
    return len(over)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Trigger test for the alexandria skill library.")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--skills-dir", default=os.path.dirname(here),
                    help="directory holding <slug>/SKILL.md (default: skills/)")
    ap.add_argument("--decoys", default=os.path.join(here, "decoys.json"))
    ap.add_argument("--json", metavar="PATH",
                    help="write the full result bundle for the panel to record")
    ap.add_argument("--engine", default=ENGINE_VERSION, choices=sorted(ENGINES),
                    help="scoring engine; the default is the pre-registered "
                         "policy and anything else is an experiment")
    ap.add_argument("--results", metavar="DIR",
                    default=os.path.join(here, "results"),
                    help="directory of recorded result bundles (for --receipts)")
    ap.add_argument("--receipts", action="store_true",
                    help="offline check: does every skill's newest recorded "
                         "receipt describe its SKILL.md as it stands now? Run "
                         "this before committing a SKILL.md edit. No engine, "
                         "no cases, exits non-zero on a stale receipt, on frontmatter "
                         "no YAML parser can load, or on a description "
                         "past the 150-word budget.")
    ap.add_argument("--invariance", action="store_true",
                    help="the pre-registered ENGINE gate: prove the scoring "
                         "function's invariance properties from the code. "
                         "Power 1, no cases, no model call. An engine change "
                         "clears this, not the pass rate, which has power "
                         "0.079 against the same question at 67 cases.")
    ap.add_argument("--sweep", action="store_true",
                    help="reliability over every non-empty decoy subset, "
                         "split by case kind, because the three kinds depend "
                         "on the panel with opposite signs and one averaged "
                         "number hides it")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.invariance:
        return 1 if run_invariance(args.skills_dir, args.decoys) else 0

    if args.sweep:
        sw = run_sweep(args.skills_dir, args.decoys, args.engine)
        report_sweep(sw)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(sw, fh, indent=2)
            print(f"\nwrote {args.json}")
        return 0

    if args.receipts:
        # The denominator the gate was missing. `refuse_unresolved` above
        # covers a path that holds no skills *directory*; this covers a
        # directory that resolved and holds no skills, which printed "all 0
        # receipts describe today's text" and exited 0 until 2026-11-02.
        n_skills = len(load_skills(args.skills_dir))
        stale = check_receipts(args.skills_dir, args.results)
        unloadable = check_frontmatter(args.skills_dir)
        if isinstance(unloadable, SkippedGate):
            print(f"\nreceipts: FAIL, {unloadable}")
            return 1
        over_budget = check_budget(args.skills_dir)
        return verdict(
            "receipts, frontmatter and budget", checked=n_skills, unit="skills",
            failures=stale + unloadable + over_budget,
            pass_line=f"receipts: all {n_skills} skills carry a receipt for "
                      "today's text, load under a YAML parser and keep their "
                      f"descriptions inside {DESCRIPTION_WORD_MAX} words.",
            fail_line=f"receipts: {stale} stale, {unloadable} unloadable and "
                      f"{over_budget} over the word budget, of {n_skills} "
                      "skills.")

    res = run(args.skills_dir, args.decoys, args.engine)
    report(res, args.verbose)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        print(f"\nwrote {args.json}")
    return 0 if res["passed"] == res["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
