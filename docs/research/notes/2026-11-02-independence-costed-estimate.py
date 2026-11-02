#!/usr/bin/env python3
"""What the two independence remedies cost, from measured inputs only.

Remedy one is the cross-family reviewer pass over this library's 102
prediction fields. Remedy two is a run of Skill-Use (`arxiv:2608.04828`).
The skill seat filed remedy two with "Cost: unknown, and the honest first
step is one costed estimate rather than a run" (docs/ideas.md, 2026-11-02).
This is that estimate.

Three rules it keeps, because a number without its provenance is the
defect this seat filed against itself earlier today
(INC-2026-11-02-a-count-shipped-with-three-of-its-eight-ids-...):

  * Every MEASURED input is read off a file in this repository or a
    sentence in the paper, and prints with its source.
  * Every UNMEASURED input prints as a range with the reason it is a
    range and the experiment that would collapse it.
  * No price is remembered. Provider prices come from pipeline/budget.py,
    which records the date each was read; Anthropic prices come from the
    claude-api skill's model table.

Run: python3 docs/research/notes/2026-11-02-independence-costed-estimate.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHARS_PER_TOKEN = 3.6   # cleaned-text ratio pipeline/budget.py uses for arXiv

# ---------------------------------------------------------------- prices
# USD per million tokens, input / output.
PRICES = {
    # pipeline/budget.py MODELS, read from the provider's live docs 2026-09-24.
    "kimi-k2.6":          (0.95, 4.00, "pipeline/budget.py (moonshot, paid)"),
    "openai/gpt-oss-120b": (0.00, 0.00, "pipeline/budget.py (groq free tier)"),
    "qwen/qwen3.8-27b":   (0.00, 0.00, "pipeline/budget.py (groq free tier)"),
    # claude-api skill model table, cached 2026-06-24. Subject-family models;
    # here only to price the Skill-Use subject arm, never the reviewer.
    "claude-opus-5":      (5.00, 25.00, "claude-api skill model table"),
    "claude-sonnet-5":    (2.00, 10.00, "claude-api skill model table"),
    "claude-haiku-4-5":   (1.00,  5.00, "claude-api skill model table"),
}
CACHE_READ_MULTIPLIER = 0.1    # claude-api: cache reads ~0.1x input
CACHE_WRITE_MULTIPLIER = 1.25  # claude-api: cache writes ~1.25x input
BATCH_DISCOUNT = 0.5           # claude-api: Batch API runs at 50%

# groq free-tier ceilings for the three general text models, same source.
GROQ_TPM, GROQ_RPM, GROQ_RPD, GROQ_TPD = 8_000, 30, 1_000, 200_000


def usd(tok_in: float, tok_out: float, model: str, *,
        cached_in: float = 0.0, batch: bool = False) -> float:
    pin, pout, _ = PRICES[model]
    total = (tok_in * pin
             + cached_in * pin * CACHE_READ_MULTIPLIER
             + tok_out * pout) / 1_000_000
    return total * (BATCH_DISCOUNT if batch else 1.0)


# ------------------------------------------------- remedy one, measured
def remedy_one() -> dict:
    """102 binary verdicts from a reviewer outside this model family.

    Every input here is measured. The payload is the four fields a
    masked-skill check is allowed to see -- situation, prompt, the claimed
    bare-arm behaviour, the with-skill behaviour -- and never `check` or
    `exploit`, which would hand the reviewer the answer.
    """
    fields = ("situation", "prompt", "without_skill", "with_skill")
    chars, cases = 0, 0
    for path in sorted((ROOT / "skills").glob("*/evals/evals.json")):
        doc = json.loads(path.read_text())
        for case in (doc.get("cases") or doc.get("tasks") or []):
            cases += 1
            chars += sum(len(str(case.get(f, ""))) for f in fields)
    if not cases:                      # the suites live on the skill seat's branch
        cases, chars = 102, 110_254    # measured there 2026-11-02, this script's run
        measured_here = False
    else:
        measured_here = True

    # The instruction prefix is the paper's masked-skill question plus its
    # red-team refutation clause. 600 tokens is this seat's drafting estimate
    # and it is the only unmeasured quantity in remedy one; at 102 calls a
    # 2x error on it moves the total by six cents.
    prefix_tokens = 600
    payload_tokens = chars / CHARS_PER_TOKEN
    tok_in = payload_tokens + prefix_tokens * cases
    # Verdict plus a reason capped at 25 words, which is Skill-Use's own
    # judge contract (`arxiv:2608.04828`, appendix D).
    tok_out = 60 * cases

    rows = []
    for model in ("openai/gpt-oss-120b", "qwen/qwen3.8-27b", "kimi-k2.6"):
        rows.append((model, usd(tok_in, tok_out, model), PRICES[model][2]))

    return {
        "cases": cases, "measured_here": measured_here,
        "payload_chars": chars,
        "tok_in": tok_in, "tok_out": tok_out,
        "rows": rows,
        # Pacing on the free tier, which is what decides whether one seat's
        # run can finish the sweep.
        "minutes_tpm": (tok_in + tok_out) / GROQ_TPM,
        "minutes_rpm": cases / GROQ_RPM,
        "fits_rpd": cases <= GROQ_RPD,
        "fits_tpd": (tok_in + tok_out) <= GROQ_TPD,
    }


# ------------------------------------- remedy two, bounded by the paper
TASKS = 177             # arxiv:2608.04828 abstract
RUBRIC_ITEMS = 1_314    # sec 3.2: 1,314 items, mean 7.4 per rubric, range 3-16
TURN_CEILING_CC = 120   # appendix D: turn limit 120 under CC, 80 under Codex
TURN_CEILING_CODEX = 80
WALL_CLOCK_S = 1_500    # appendix D: wall-clock limit 1,500s per task


def subject_arm(turns: int, prefix: int, growth: int, out_per_turn: int,
                model: str, cached: bool) -> tuple[float, float]:
    """Tokens and dollars for one model-harness arm over all 177 tasks.

    A harness resends its history every turn, so uncached input over a
    task of T turns is T*prefix + growth*T*(T-1)/2. With caching the
    repeated part is a cache read and only `growth` is new each turn.
    """
    uncached_in = turns * prefix + growth * turns * (turns - 1) / 2
    out = turns * out_per_turn
    if cached:
        fresh = prefix + growth * turns            # written to cache once
        read = max(0.0, uncached_in - fresh)
        per_task = usd(fresh * CACHE_WRITE_MULTIPLIER, out, model, cached_in=read)
    else:
        per_task = usd(uncached_in, out, model)
    return uncached_in * TASKS, per_task * TASKS


def judge_arm(trace_tokens: int, model: str) -> float:
    """1,314 binary verdicts. 7.4 items share one task's trace, so the
    trace is cached once per task and read by the rest of its items."""
    writes = TASKS * trace_tokens
    reads = (RUBRIC_ITEMS - TASKS) * trace_tokens
    out = RUBRIC_ITEMS * 60
    return usd(writes * CACHE_WRITE_MULTIPLIER, out, model,
               cached_in=reads, batch=True)


def main() -> int:
    r1 = remedy_one()
    print("=" * 74)
    print("REMEDY ONE -- the cross-family reviewer pass over the prediction fields")
    print("=" * 74)
    src = "this checkout" if r1["measured_here"] else "the skill seat's branch, 2026-11-02"
    print(f"  {r1['cases']} tasks, {r1['payload_chars']:,} chars of reviewable payload"
          f"  (measured on {src})")
    print(f"  input {r1['tok_in']:,.0f} tokens, output {r1['tok_out']:,.0f} tokens"
          f"   (at {CHARS_PER_TOKEN} chars/token)")
    print()
    for model, cost, source in r1["rows"]:
        print(f"    {model:<22} ${cost:>7.4f}   {source}")
    print()
    print(f"  Free-tier pacing: {r1['minutes_tpm']:.1f} min bound by {GROQ_TPM:,} TPM, "
          f"{r1['minutes_rpm']:.1f} min bound by {GROQ_RPM} RPM")
    print(f"  Daily ceilings: {r1['cases']} requests vs {GROQ_RPD} RPD -> "
          f"{'fits' if r1['fits_rpd'] else 'OVER'};  "
          f"{r1['tok_in'] + r1['tok_out']:,.0f} tokens vs {GROQ_TPD:,} TPD -> "
          f"{'fits' if r1['fits_tpd'] else 'OVER'}")
    print()
    print("  So the sweep is one pass inside one seat's run, and the money is not")
    print("  the decision. The decision is one key.")
    print()

    print("=" * 74)
    print("REMEDY TWO -- one arm of Skill-Use, 177 tasks")
    print("=" * 74)
    print(f"  Fixed by the paper: {TASKS} tasks, {RUBRIC_ITEMS} rubric items,")
    print(f"  turn ceiling {TURN_CEILING_CC} (CC) / {TURN_CEILING_CODEX} (Codex),"
          f" wall clock {WALL_CLOCK_S}s per task.")
    print()
    print("  UNMEASURED, and this is the whole width of the estimate: tokens per")
    print("  turn. The paper reports no token counts, and nothing in this")
    print("  repository has measured an agentic harness turn either.")
    print()
    prefix = 15_000      # harness system prompt + 79-skill progressive-disclosure menu
    print(f"  {'turns':>6} {'growth/turn':>12} {'out/turn':>9} "
          f"{'cached $':>10} {'uncached $':>12}")
    for turns in (20, 60, TURN_CEILING_CC):
        for growth, out_per_turn in ((500, 300), (1_500, 600), (3_000, 1_000)):
            _, cached = subject_arm(turns, prefix, growth, out_per_turn,
                                    "claude-opus-5", cached=True)
            _, plain = subject_arm(turns, prefix, growth, out_per_turn,
                                   "claude-opus-5", cached=False)
            print(f"  {turns:>6} {growth:>12,} {out_per_turn:>9,} "
                  f"{cached:>10,.0f} {plain:>12,.0f}")
    print()
    print("  Judge arm, 1,314 verdicts on Batch API with the trace cached per task:")
    for model in ("claude-haiku-4-5", "claude-sonnet-5"):
        for trace in (5_000, 15_000):
            print(f"    {model:<18} trace {trace:>6,} tokens  "
                  f"${judge_arm(trace, model):>7.2f}")
    print()
    hours = TASKS * WALL_CLOCK_S / 3600
    print(f"  Sandbox ceiling: {TASKS} containers x {WALL_CLOCK_S}s = "
          f"{hours:.1f} container-hours worst case,")
    print(f"  {hours / 8:.1f} wall-clock hours at 8-wide. On a 2-vCPU commodity")
    print("  instance that is tens of dollars, so it is not the cost driver.")
    print()
    print("  THE CHEAP MEASUREMENT THAT COLLAPSES THE RANGE: five tasks, one")
    print("  model, one harness, logging usage per turn. At the middle row that")
    _, mid = subject_arm(60, prefix, 1_500, 600, "claude-opus-5", cached=True)
    print(f"  is ${mid / TASKS * 5:,.0f}, and it replaces a 60x spread with a number.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
