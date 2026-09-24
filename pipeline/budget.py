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
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ---------------- what the model will accept ----------------

# Groq's free-tier limits, re-read from the live docs on 2026-09-24 (incident
# 24) at https://console.groq.com/docs/rate-limits and cross-checked against
# https://console.groq.com/docs/models. Both pages are quoted in the PR that
# landed this change.
#
# TPM is the number that bites: incident 22 established empirically that a
# single request larger than the TPM ceiling is rejected 413 before any
# generation starts, so the rolling per-minute limit is also a per-request
# limit. RPM, RPD and TPD are recorded because the press shares this key with
# four daily crons and the retry loop needs to know which ceiling it is near.
#
# The free tier has exactly three general text writers, and all three sit at
# 8,000 TPM. There is no longer a free-tier model with room above that: the
# only free entries with a larger TPM are the two prompt-guard classifiers at
# 15K, which cannot write prose. Read that number carefully before proposing a
# press design; it is the constraint the whole press now lives inside.
#
# Keep this table honest: every run of weekly.py logs Groq's own
# `x-ratelimit-limit-tokens` header, which is the authority. If a logged value
# ever disagrees with a number here, the logged value wins and this table is
# the thing to fix.
MODELS = {
    "openai/gpt-oss-120b": {
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 65_536, "status": "production",
    },
    "qwen/qwen3.8-27b": {
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 32_768, "status": "preview",
    },
    "openai/gpt-oss-20b": {
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 65_536, "status": "production",
    },
}

# Models the press has pointed at and that Groq has since withdrawn. Kept so a
# 404 is explained rather than raising a bare KeyError, and so nobody proposes
# a return to one of them without reading why it went.
#
# This is the failure class incident 24 named: PROVIDER MODEL DEPRECATION. Both
# entries were `groq/compound*`, an agentic *preview* system, and previews are
# withdrawn without the deprecation notice production models get. The press
# moved to compound on 2026-09-19 (PR #51) purely for its 70K TPM, which is now
# the clearest evidence available that a capacity number is the wrong reason to
# pick a model.
DECOMMISSIONED = {
    "groq/compound": "404 Not Found as of 2026-09-23; absent from Groq's "
                     "model catalog and rate-limit table on 2026-09-24. Was "
                     "70,000 TPM, which is why the press was moved to it.",
    "groq/compound-mini": "withdrawn with groq/compound; same catalog absence.",
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
    if model in DECOMMISSIONED:
        raise KeyError(
            f"{model!r} was withdrawn by Groq: {DECOMMISSIONED[model]} A press "
            "cannot be pointed at it. Pick from budget.MODELS."
        )
    if model not in MODELS:
        raise KeyError(
            f"{model!r} has no published limits in budget.MODELS. Add it with "
            "the numbers from https://console.groq.com/docs/rate-limits before "
            "pointing a press at it."
        )
    return int(MODELS[model]["tpm"] * (1 - MARGIN))


# ---------------- does the model still exist? ----------------

# Incident 24: the budget guard checked that the request fits and nothing
# checked that the model exists, so the press was pointed at a model Groq had
# withdrawn and the failure surfaced three days later as the owner noticing an
# empty inbox. `GET /models` is the cheapest possible answer to "can we print at
# all", it costs no tokens against any ceiling, and it runs twice: once at
# deploy and once at the start of every run.
MODELS_URL = "https://api.groq.com/openai/v1/models"


class AvailabilityError(RuntimeError):
    """The provider could not be asked which models it has."""


class NoUsableModel(RuntimeError):
    """Every candidate is either missing from the provider or over budget."""


def available_models(api_key: str, timeout: float = 30.0) -> set[str]:
    """The set of model ids Groq reports as active for this key.

    Raises rather than returning an empty set on any failure. An empty set and
    a failed request are the same value and very different facts, and treating
    a network blip as "every model is gone" would walk the whole fallback list
    for nothing.
    """
    # the cheap check first: no key is a configuration fact, not a network one
    if not api_key:
        raise AvailabilityError(
            "no Groq API key, so model availability cannot be checked. Set the "
            "GROQ_API_KEY the `groq` Modal secret provides."
        )

    import httpx
    try:
        resp = httpx.get(
            MODELS_URL,
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            timeout=timeout,
        )
    except Exception as exc:
        raise AvailabilityError(f"GET {MODELS_URL} failed: {exc}") from exc
    if resp.status_code >= 400:
        raise AvailabilityError(
            f"GET {MODELS_URL} answered {resp.status_code}: {resp.text[:500]}"
        )
    try:
        data = resp.json()["data"]
    except Exception as exc:
        raise AvailabilityError(
            f"GET {MODELS_URL} returned no usable model list: {resp.text[:500]}"
        ) from exc
    # `active` is Groq's own flag; a listed but inactive model still 404s
    return {m["id"] for m in data if m.get("active", True)}


@dataclass
class Choice:
    """Which model the press will use, and why every rejected one was rejected."""

    model: str | None
    report: Report | None
    rejected: list[tuple[str, str]] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        for name, why in self.rejected:
            lines.append(f"  rejected {name}: {why}")
        if self.model:
            lines.append(f"  CHOSEN {self.model}: {self.report.summary()}")
        else:
            lines.append("  NO USABLE MODEL: the press cannot print.")
        return "\n".join(lines)


def choose_model(candidates: list[str], available: set[str] | None,
                 prompt: str, payload_json: str, max_completion: int) -> Choice:
    """First candidate that both exists at the provider and fits the budget.

    Two gates, in this order, because they fail for different reasons and the
    operator needs to know which one bit. `available=None` skips the existence
    gate, for the offline CI run that has no key.
    """
    choice = Choice(model=None, report=None)
    for name in candidates:
        if name in DECOMMISSIONED:
            choice.rejected.append((name, f"withdrawn by Groq. {DECOMMISSIONED[name]}"))
            continue
        if name not in MODELS:
            choice.rejected.append(
                (name, "no published limits in budget.MODELS, so no budget can "
                       "be checked for it"))
            continue
        if available is not None and name not in available:
            choice.rejected.append(
                (name, f"not in the {len(available)} models Groq reports for "
                       "this key; a request would 404"))
            continue
        report = check_request(prompt, payload_json, max_completion, name)
        if not report.fits:
            choice.rejected.append(
                (name, f"over budget by {-report.headroom} tokens. "
                       f"{report.summary()}"))
            continue
        choice.model, choice.report = name, report
        return choice
    return choice


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
    models: list[str]
    max_completion: int
    optional: bool = False


def fallback_models() -> list[str]:
    """The press's ordered fallback list, read out of weekly.py.

    Incident 24 added the list; this guard reads it from production rather than
    keeping a copy, for the same reason it already reads the model name and the
    output reservation from there. A guard with its own copy of the fallback
    order is a guard that verifies a list nothing uses.
    """
    source = _weekly_source()
    match = re.search(r"^FALLBACK_MODELS = (\[[^\]]*\])", source, re.M)
    if match:
        models = ast.literal_eval(match.group(1))
        if not isinstance(models, list) or len(models) < 3:
            raise LookupError(
                "weekly.FALLBACK_MODELS must be a list of at least three "
                f"models; found {models!r}. One model is a single point of "
                "failure, and incident 24 is what that costs."
            )
        return models
    # a press that predates the fallback list still has to be checkable
    return [_literal(source, r'^MODEL = "([^"]+)"', "MODEL")]


def presses() -> list[Press]:
    """Read the press settings out of weekly.py rather than restating them.

    A guard that keeps its own copy of the model name and the output
    reservation is a guard that passes while production fails.
    """
    source = _weekly_source()
    models = fallback_models()
    # one reservation today; PR #35 replaces it with a MAX_TOKENS dict keyed by
    # kind, and this reads either shape
    table = re.search(r"^MAX_TOKENS = (\{[^}]*\})", source, re.M)
    if table:
        tokens = ast.literal_eval(table.group(1))
    else:
        tokens = {"weekly": int(_literal(
            source, r"^MAX_COMPLETION_TOKENS = (\d+)", "MAX_COMPLETION_TOKENS"))}
    return [
        Press("weekly digest", "prompts/digest.md", models, tokens["weekly"]),
        Press("daily issue", "prompts/daily.md", models,
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
    """The `limit N` on each evidence stream's query in weekly.py."""
    out = {}
    pattern = re.compile(r"^\s{4}(\w+) = conn\.execute\(\s*\n\s*\"\"\"(.*?)\"\"\"",
                         re.S | re.M)
    for match in pattern.finditer(source):
        name, body = match.group(1), match.group(2)
        found = re.findall(r"\blimit\s+(\d+)\b", body, re.I)
        if found:
            out[name] = int(found[-1])
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

    # Availability, when a key happens to be present. CI has none, and that is
    # fine: the deploy-time and run-time checks in weekly.py are the ones that
    # gate a real send. Here it is a bonus, never a requirement, so the guard
    # stays runnable offline.
    available = None
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        try:
            available = available_models(key)
            print(f"groq reports {len(available)} active models for this key")
            for name in MODELS:
                if name not in available:
                    failures.append(
                        f"{name} is in budget.MODELS but Groq does not list it; "
                        "a press pointed at it would 404")
                    print(f"  MISSING AT PROVIDER: {name}")
            print()
        except AvailabilityError as exc:
            print(f"availability check skipped: {exc}\n")
    else:
        print("no GROQ_API_KEY here, so model existence is not checked. "
              "weekly.py checks it at deploy and at run start.\n")

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
        print(f"{press.name} ({press.prompt}, {len(prompt)} chars, "
              f"{count_tokens(prompt)} tokens)")
        print(f"  output reservation: {press.max_completion} tokens")
        print(f"  fallback list, in order, every entry checked:")

        # Requirement from the 2026-09-24 dispatch: the guard verifies that
        # EVERY fallback fits, not just the one in use. A fallback that has
        # never been measured is a fallback that fails at 3am.
        fits_any = False
        for rank, model in enumerate(press.models, start=1):
            if model in DECOMMISSIONED:
                failures.append(
                    f"{press.name} fallback {rank} is {model}, withdrawn by Groq")
                print(f"  {rank}. {model}: WITHDRAWN. {DECOMMISSIONED[model]}")
                continue
            if model not in MODELS:
                failures.append(
                    f"{press.name} fallback {rank} ({model}) has no published "
                    "limits in budget.MODELS")
                print(f"  {rank}. {model}: no limits published here; cannot be "
                      "checked")
                continue
            report = check_request(prompt, payload_json, press.max_completion,
                                   model)
            flag = "" if available is None else (
                " [at provider]" if model in available else " [ABSENT AT PROVIDER]")
            print(f"  {rank}. {report.summary()}{flag}")
            if report.fits:
                fits_any = True

        if not fits_any:
            best = min(
                (check_request(prompt, payload_json, press.max_completion, m)
                 for m in press.models if m in MODELS),
                key=lambda r: -r.headroom, default=None)
            over = -best.headroom if best else 0
            failures.append(
                f"{press.name} does not fit ANY model in its fallback list; the "
                f"closest is {over} tokens over")
            print(f"  FAIL: no model in the fallback list can take this "
                  f"request. Closest miss is {over} tokens.")
            print("  Fix one of: shorten the generator prompt, lower the output "
                  "reservation, tighten pipeline/budget.py PAYLOAD_CAPS (and the "
                  "matching `limit` in gather()), split the issue across several "
                  "requests, or add a model with a larger per-request budget to "
                  "budget.MODELS.")
            print(f"  Note the arithmetic: the prompt ({count_tokens(prompt)}) "
                  f"plus the reservation ({press.max_completion}) alone is "
                  f"{count_tokens(prompt) + press.max_completion} tokens, "
                  "before a single row of payload.")
        print()

    if failures:
        print(f"budget check FAILED ({len(failures)} problem"
              f"{'s' if len(failures) > 1 else ''})")
        return 1
    print("budget check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
