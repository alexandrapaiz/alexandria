"""Does the request fit? The digest press's token budget, in one place.

Incident 22 (docs/agents/incidents.md): the editorial rebuild grew
`prompts/digest.md` from 223 lines to 587, the generator's first autonomous
run came back `413 Payload Too Large`, and no issue was written. Groq's 413
is not a byte limit. It is the tokens-per-minute ceiling applied to a single
request, and the tokens it counts are the ones you *ask for*: system prompt
plus user payload plus `max_completion_tokens`. Reserve 6,000 tokens of
output and you have spent 6,000 tokens of budget before the model writes a
word.

The arithmetic that must hold, every run:

    prompt + payload + max_completion_tokens + envelope  <=  TPM * (1 - MARGIN)

This module owns that arithmetic and nothing else. Three callers share it so
the number can never drift between them:

* `pipeline/weekly.py` sizes the payload against it (`fit_payload`) and
  refuses to call Groq when the request cannot fit (`check_request`).
* CI runs `python3 pipeline/budget.py` on every pull request that touches a
  generator prompt or the pipeline, and fails the build with the arithmetic
  printed, so an editorial merge cannot break the press again.
* The same command is the pre-deploy check; see the module docstring in
  `pipeline/weekly.py` for the deploy path.

Run it directly to see the sums:

    pip install tiktoken && python3 pipeline/budget.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ---------------- what the model will accept ----------------

# Groq's published free-tier limits, read 2026-09-19 from
# https://console.groq.com/docs/rate-limits. TPM is the number that bites: a
# single request larger than it is rejected 413 before any generation starts,
# and the window is rolling, so it is both a per-request and a per-minute cap.
#
# Only four free-tier entries carry a TPM above 8K, and three of them are
# classifiers or speech models. `groq/compound` is the one usable writer with
# room, at 70K. Keep this table honest: every run of weekly.py logs Groq's own
# `x-ratelimit-limit-tokens` header, which is the authority. If a logged value
# ever disagrees with a number here, the logged value wins and this table is
# the thing to fix.
MODELS = {
    "openai/gpt-oss-120b": {"tpm": 8_000, "context": 131_072, "max_output": 65_536},
    "openai/gpt-oss-20b": {"tpm": 8_000, "context": 131_072, "max_output": 65_536},
    "qwen/qwen3.8-27b": {"tpm": 8_000, "context": 131_072, "max_output": 32_768},
    "groq/compound": {"tpm": 70_000, "context": 131_072, "max_output": 8_192},
    "groq/compound-mini": {"tpm": 70_000, "context": 131_072, "max_output": 8_192},
}

# Headroom held back from the published ceiling. Three things live in it: the
# tokenizer estimate below is close but not Groq's own, the rolling window may
# still hold tokens from the citation pass or a retried call, and an editorial
# merge lands between one run and the next. Fifteen percent of 70K is 10,500
# tokens, which is more than the whole prompt.
MARGIN = 0.15

# Chat framing Groq adds around the two messages. Measured generously; it is
# tens of tokens against a budget of thousands.
ENVELOPE_TOKENS = 32


def limit_for(model: str) -> int:
    """Usable tokens per request for `model`, margin already deducted."""
    if model not in MODELS:
        raise KeyError(
            f"{model!r} has no published limits in budget.MODELS. Add it with "
            "the numbers from https://console.groq.com/docs/rate-limits before "
            "pointing a press at it."
        )
    return int(MODELS[model]["tpm"] * (1 - MARGIN))


# ---------------- counting tokens ----------------

# Falls back to a chars-per-token ratio when tiktoken is not installed or its
# vocabulary cannot be downloaded. 3.0 is deliberately pessimistic: measured
# against the real prompt the ratio is 4.32 for editorial prose and about 3.2
# for the payload's dense JSON, so the fallback over-counts and the guard errs
# toward refusing a request that would have fitted.
FALLBACK_CHARS_PER_TOKEN = 3.0

_encoding = None
_exact = None


def _encoder():
    """o200k_base, the closest public tokenizer to the gpt-oss vocabulary."""
    global _encoding, _exact
    if _exact is None:
        try:
            import tiktoken

            _encoding = tiktoken.get_encoding("o200k_base")
            _exact = True
        except Exception as exc:  # no tiktoken, or no network for its vocab
            print(f"budget: exact tokenizer unavailable ({exc}); using the "
                  f"{FALLBACK_CHARS_PER_TOKEN} chars/token fallback")
            _encoding, _exact = None, False
    return _encoding


def count_tokens(text: str) -> int:
    enc = _encoder()
    if enc is not None:
        return len(enc.encode(text))
    return int(len(text) / FALLBACK_CHARS_PER_TOKEN) + 1


def exact() -> bool:
    """True when counts come from the tokenizer rather than the ratio."""
    _encoder()
    return bool(_exact)


# ---------------- the worst payload gather() can hand us ----------------

# One entry per evidence stream in `weekly.py:gather()`: how many rows its SQL
# can return, and the longest each of its text fields can be after the
# truncation gather() applies. The row counts are checked against the `limit`
# clauses in weekly.py by `check_drift()` below, so a query that quietly raises
# its limit fails CI instead of failing the press.
#
# `floor` is how far `fit_payload` may trim a stream before it starts taking
# from the next one. It is editorial judgment, not arithmetic: an issue can be
# written from eight new claims, and it cannot be written from none.
@dataclass
class Stream:
    rows: int
    floor: int
    fields: dict[str, int] = field(default_factory=dict)


PAYLOAD_CAPS = {
    # claim[:280], evidence[:350], procedure[:600] are gather()'s own slices;
    # titles, urls, topics, edges, authors and institutions are unbounded in
    # the SQL, so these are generous observed maxima.
    "new_claims": Stream(22, 8, {
        "claim": 280, "evidence": 350, "procedure": 600, "paper": 220,
        "url": 140, "topics": 180, "edges": 360, "authors": 140,
        "institutions": 200, "tier": 12, "triage": 12,
    }),
    "superseded": Stream(10, 3, {
        "old_claim": 280, "new_claim": 280, "old_paper": 220, "new_paper": 220,
        "old_url": 140, "new_url": 140,
    }),
    "supported_claims": Stream(12, 4, {"claim": 400, "paper": 220, "url": 140}),
    "citation_movers": Stream(12, 4, {"paper": 220, "url": 140}),
    "deprecated": Stream(8, 2, {
        "old_claim": 400, "contradicted_by": 400, "paper": 220, "url": 140,
    }),
    "deep_reads": Stream(10, 3, {"paper": 220, "url": 140, "why": 200}),
}

# The order fit_payload trims in, least load-bearing first. The reading list
# and the citation movers are the cheapest things to lose: they are one line
# each in the issue. New claims are trimmed early only down to their floor,
# because their tail is the single biggest thing in the payload and it is
# already sorted worst-last by triage score.
TRIM_ORDER = [
    "new_claims", "deep_reads", "citation_movers", "supported_claims",
    "superseded", "deprecated",
]

_FILLER = (
    "The method trains a reward model on preference pairs and then distills "
    "the resulting policy into a smaller student network, reporting gains on "
    "held-out reasoning benchmarks without additional human annotation. "
)


def _filler(n: int) -> str:
    """Realistic English of length n. Not 'x' * n, which tokenizes far too
    cheaply and would make every estimate here look better than it is."""
    reps = -(-n // len(_FILLER))
    return (_FILLER * reps)[:n]


def worst_case_payload() -> dict:
    """The largest payload `gather()` can return, built from PAYLOAD_CAPS."""

    def rows(name):
        cap = PAYLOAD_CAPS[name]
        return [
            {k: _filler(v) for k, v in cap.fields.items()} | {
                "claim_id": 999_999, "score": 0.98, "confidence": 0.99,
                "supports": 99, "citations_before": 9_999, "citations_now": 9_999,
            }
            for _ in range(cap.rows)
        ]

    return {
        "stats": {"papers_ingested": 9999, "claims_distilled": 9999, "edges_drawn": 9999},
        "new_claims": rows("new_claims"),
        "superseded": rows("superseded"),
        "traction": {
            "supported_claims": rows("supported_claims"),
            "citation_movers": rows("citation_movers"),
        },
        "deprecated": rows("deprecated"),
        "deep_reads": rows("deep_reads"),
        "week": "2026-W38",
        "dates": "September 15-21, 2026",
    }


def encode(payload: dict) -> str:
    return json.dumps(payload, separators=(",", ":"), default=str)


# ---------------- the check ----------------

@dataclass
class Report:
    model: str
    prompt_tokens: int
    payload_tokens: int
    completion_tokens: int
    limit: int

    @property
    def total(self) -> int:
        return (self.prompt_tokens + self.payload_tokens
                + self.completion_tokens + ENVELOPE_TOKENS)

    @property
    def fits(self) -> bool:
        return self.total <= self.limit

    @property
    def headroom(self) -> int:
        return self.limit - self.total

    def summary(self) -> str:
        tpm = MODELS[self.model]["tpm"]
        verdict = "fits" if self.fits else "DOES NOT FIT"
        return (
            f"{self.model}: prompt {self.prompt_tokens} + payload "
            f"{self.payload_tokens} + output reservation {self.completion_tokens} "
            f"+ envelope {ENVELOPE_TOKENS} = {self.total} tokens against "
            f"{self.limit} usable ({tpm} TPM less {MARGIN:.0%} margin); "
            f"{verdict}, headroom {self.headroom}"
        )


def check_request(prompt: str, payload_json: str, max_completion: int,
                  model: str) -> Report:
    return Report(
        model=model,
        prompt_tokens=count_tokens(prompt),
        payload_tokens=count_tokens(payload_json),
        completion_tokens=max_completion,
        limit=limit_for(model),
    )


class BudgetExceeded(RuntimeError):
    """Raised instead of letting Groq answer 413."""


def fit_payload(payload: dict, prompt: str, max_completion: int,
                model: str) -> str:
    """Trim the payload until the whole request fits, or say why it cannot.

    Trimming happens in TRIM_ORDER, each stream down to its floor first, then
    a second pass that takes everything down to a single row. If the request
    still does not fit with one row per stream, the payload was never the
    problem and no amount of trimming will help, so this raises with the
    arithmetic rather than letting the press fail in production.
    """
    limit = limit_for(model)
    fixed = count_tokens(prompt) + max_completion + ENVELOPE_TOKENS

    def streams():
        yield "new_claims", payload.get("new_claims")
        yield "superseded", payload.get("superseded")
        traction = payload.get("traction") or {}
        yield "supported_claims", traction.get("supported_claims")
        yield "citation_movers", traction.get("citation_movers")
        yield "deprecated", payload.get("deprecated")
        yield "deep_reads", payload.get("deep_reads")

    by_name = {name: rows for name, rows in streams() if isinstance(rows, list)}

    body = encode(payload)
    for floors in (True, False):
        for name in TRIM_ORDER:
            rows = by_name.get(name)
            if rows is None:
                continue
            floor = PAYLOAD_CAPS[name].floor if floors else 1
            while len(rows) > floor and fixed + count_tokens(body) > limit:
                rows.pop()
                body = encode(payload)
            if fixed + count_tokens(body) <= limit:
                return body

    report = check_request(prompt, body, max_completion, model)
    if report.fits:
        return body
    raise BudgetExceeded(
        "the request does not fit even with the payload trimmed to one row per "
        f"stream. {report.summary()}. The prompt and the output reservation "
        f"alone are {report.prompt_tokens + max_completion} tokens, so no "
        "payload selection can rescue this: either the generator prompt gets "
        "shorter, the output reservation gets smaller, or the press moves to a "
        "model with a larger per-request budget (pipeline/budget.py MODELS)."
    )


# ---------------- the standing guard ----------------

# Each press CI checks. `optional` presses are ones whose prompt has not
# landed on main yet; PR #35 adds prompts/daily.md, and the day it merges this
# guard starts covering it with no further edit here.
@dataclass
class Press:
    name: str
    prompt: str
    model: str
    max_completion: int
    optional: bool = False


def presses() -> list[Press]:
    """Read the press settings out of weekly.py rather than restating them.

    A guard that keeps its own copy of the model name and the output
    reservation is a guard that passes while production fails.
    """
    source = _weekly_source()
    model = _literal(source, r'^MODEL = "([^"]+)"', "MODEL")
    # one reservation today; PR #35 replaces it with a MAX_TOKENS dict keyed by
    # kind, and this reads either shape
    table = re.search(r"^MAX_TOKENS = (\{[^}]*\})", source, re.M)
    if table:
        tokens = ast.literal_eval(table.group(1))
    else:
        tokens = {"weekly": int(_literal(
            source, r"^MAX_COMPLETION_TOKENS = (\d+)", "MAX_COMPLETION_TOKENS"))}
    return [
        Press("weekly digest", "prompts/digest.md", model, tokens["weekly"]),
        Press("daily issue", "prompts/daily.md", model,
              tokens.get("daily", tokens["weekly"]), optional=True),
    ]


def _literal(source: str, pattern: str, name: str) -> str:
    match = re.search(pattern, source, re.M)
    if not match:
        raise LookupError(
            f"pipeline/weekly.py no longer defines {name} where this guard "
            "looks for it. Fix the pattern in budget.presses(); a guard that "
            "cannot read the settings it checks is worse than no guard."
        )
    return match.group(1)


def _weekly_source() -> str:
    return (ROOT / "pipeline" / "weekly.py").read_text()


def sql_limits(source: str) -> dict[str, int]:
    """The `limit N` on each evidence stream's query in weekly.py.

    The largest one per stream, not the last one. Since the daily cadence
    landed there are two gather functions in that file selecting streams of
    the same names, and the daily's limits are smaller. Reading the last match
    made the guard measure the daily's payload and report the weekly's real
    caps as drift, which is a guard failing on correct code. The worst case is
    what this guard exists to measure, so the worst case is what it takes.
    """
    out: dict[str, int] = {}
    pattern = re.compile(r"^\s{4}(\w+) = conn\.execute\(\s*\n\s*\"\"\"(.*?)\"\"\"",
                         re.S | re.M)
    for match in pattern.finditer(source):
        name, body = match.group(1), match.group(2)
        found = re.findall(r"\blimit\s+(\d+)\b", body, re.I)
        if found:
            out[name] = max(int(found[-1]), out.get(name, 0))
    return out


# gather() names two streams differently from the payload keys they land under.
SQL_TO_PAYLOAD = {"supported": "supported_claims", "movers": "citation_movers"}


def check_drift() -> list[str]:
    """Every row cap in PAYLOAD_CAPS must match the SQL that fills it."""
    problems = []
    limits = sql_limits(_weekly_source())
    for sql_name, rows in limits.items():
        key = SQL_TO_PAYLOAD.get(sql_name, sql_name)
        if key not in PAYLOAD_CAPS:
            continue
        if PAYLOAD_CAPS[key].rows != rows:
            problems.append(
                f"weekly.py gather() selects up to {rows} {sql_name} rows but "
                f"budget.PAYLOAD_CAPS['{key}'] assumes {PAYLOAD_CAPS[key].rows}. "
                "The worst case this guard measures is not the worst case the "
                "press can produce."
            )
    for key in PAYLOAD_CAPS:
        sql_name = next((s for s, p in SQL_TO_PAYLOAD.items() if p == key), key)
        if sql_name not in limits:
            problems.append(
                f"weekly.py gather()'s {sql_name} query has no `limit` clause, so "
                f"the {key} stream is unbounded and no worst case exists for it."
            )
    return problems


# ---------------- the guard's own tests ----------------

def selftest() -> list[str]:
    """Check the trimmer against the two cases that matter.

    A guard is only worth its constants if the thing it guards behaves the way
    the guard assumes. These run in CI beside the budget check, cost
    milliseconds, and need no database, no network and no key.
    """
    failures = []
    prompt = _filler(20_000)  # ~4,600 tokens of prose

    # 1. an oversized payload is trimmed until it fits, and it does fit.
    #    Deliberately a tight model and a small reservation, so the trimmer has
    #    to do real work rather than passing on the first check.
    payload = worst_case_payload()
    before = len(payload["new_claims"])
    try:
        body = fit_payload(payload, prompt, 1_000, "openai/gpt-oss-20b")
    except BudgetExceeded as exc:
        failures.append(f"selftest: trimming could not fit a prompt of "
                        f"{count_tokens(prompt)} tokens: {exc}")
    else:
        report = check_request(prompt, body, 1_000, "openai/gpt-oss-20b")
        if not report.fits:
            failures.append(f"selftest: fit_payload returned a body that does "
                            f"not fit. {report.summary()}")
        if len(payload["new_claims"]) >= before:
            failures.append("selftest: fit_payload trimmed nothing from a "
                            "worst-case payload that cannot fit untrimmed")

    # 2. when the prompt alone busts the budget, say so instead of trimming
    #    forever and shipping something that will 413
    try:
        fit_payload(worst_case_payload(), _filler(200_000), 6_000,
                    "openai/gpt-oss-120b")
    except BudgetExceeded:
        pass
    else:
        failures.append("selftest: a prompt far over the model's ceiling was "
                        "accepted; the press would 413 in production")

    return failures


def main() -> int:
    payload_json = encode(worst_case_payload())
    print(f"worst-case payload: {len(payload_json)} chars, "
          f"{count_tokens(payload_json)} tokens "
          f"({'exact' if exact() else 'estimated'})\n")

    failures = check_drift()
    for problem in failures:
        print(f"DRIFT: {problem}\n")

    for problem in selftest():
        failures.append(problem)
        print(f"SELFTEST: {problem}\n")

    for press in presses():
        path = ROOT / press.prompt
        if not path.exists():
            if press.optional:
                print(f"{press.name}: {press.prompt} not on this branch, skipped\n")
                continue
            failures.append(f"{press.name}: {press.prompt} is missing")
            print(f"MISSING: {press.prompt}\n")
            continue
        prompt = path.read_text()
        report = check_request(prompt, payload_json, press.max_completion, press.model)
        print(f"{press.name} ({press.prompt}, {len(prompt)} chars)")
        print(f"  {report.summary()}")
        if not report.fits:
            over = -report.headroom
            failures.append(
                f"{press.name} is {over} tokens over budget on {press.model}"
            )
            print(f"  FAIL: {over} tokens over. Groq answers 413 and no issue "
                  "is written.")
            print("  Fix one of: shorten the generator prompt, lower the output "
                  "reservation, tighten pipeline/budget.py PAYLOAD_CAPS (and the "
                  "matching `limit` in gather()), or move the press to a model "
                  "with a larger per-request budget.")
        print()

    if failures:
        print(f"budget check FAILED ({len(failures)} problem"
              f"{'s' if len(failures) > 1 else ''})")
        return 1
    print("budget check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
