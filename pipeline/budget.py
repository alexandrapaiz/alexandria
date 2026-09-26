"""Does the request fit? The digest press's token budget, in one place.

Incident 22 (docs/agents/incidents.md): the editorial rebuild grew
`prompts/digest.md` from 223 lines to 587, the generator's first autonomous
run came back `413 Payload Too Large`, and no issue was written. Groq's 413
is not a byte limit. It is the tokens-per-minute ceiling applied to a single
request, and the tokens it counts are the ones you *ask for*: system prompt
plus user payload plus `max_completion_tokens`. Reserve 6,000 tokens of
output and you have spent 6,000 tokens of budget before the model writes a
word.

Since ADR-32 the press writes on Moonshot's Kimi and keeps Groq's free tier
as its last resort, so the guard is now a two-provider guard. The ceiling
that binds is not the same kind of number on each: Groq refuses on
tokens-per-minute, Moonshot on the model's context window. `binding_limit`
takes the smaller of the two and every printed line says which one it was.

The arithmetic that must hold, every run:

    prompt + payload + max_completion_tokens + envelope  <=  TPM * (1 - MARGIN)

This module owns that arithmetic and nothing else. Three callers share it so
the number can never drift between them:

* `pipeline/weekly.py` sizes the payload against it (`fit_payload`) and
  refuses to call the provider when the request cannot fit (`check_request`).
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

# The press talks to two providers now (ADR-32, 2026-09-24), and the number
# that binds a single request is not the same kind of number on each of them.
#
# * **Moonshot** (Kimi K2) is a prepaid account, so the per-minute ceilings are
#   enormous and the CONTEXT WINDOW is what a request has to fit inside.
# * **Groq**'s free tier is the opposite: the context window is generous and
#   the TOKENS-PER-MINUTE ceiling is what refuses the request, because incident
#   22 established that a single request larger than TPM is rejected 413 before
#   generation starts.
#
# `limit_for` therefore takes the smaller of the two on every model, and
# `Report.summary` says which one bit. Getting this wrong in either direction
# is a press that either 413s in production or refuses a request that would
# have been fine.
PROVIDERS = {
    "moonshot": {
        "base_url": "https://api.moonshot.ai/v1",
        "key_env": "MOONSHOT_API_KEY",
        "secret": "moonshot",          # the Modal secret name, never its value
        "docs": "https://platform.kimi.ai/docs/models",
        "limits_docs": "https://platform.kimi.ai/docs/pricing/limits",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "secret": "groq",
        "docs": "https://console.groq.com/docs/models",
        "limits_docs": "https://console.groq.com/docs/rate-limits",
    },
}

PRIMARY_PROVIDER = "moonshot"


def provider_of(model: str) -> str:
    """Which provider serves `model`. Raises rather than guessing from the id."""
    if model in DECOMMISSIONED:
        raise KeyError(
            f"{model!r} was withdrawn by its provider: {DECOMMISSIONED[model]} "
            "There is nowhere to send this request."
        )
    if model not in MODELS:
        raise KeyError(
            f"{model!r} has no entry in budget.MODELS, so there is no provider "
            "to send it to. Add it with the numbers from its provider's docs "
            "before pointing a press at it."
        )
    return MODELS[model]["provider"]


def endpoint(provider: str, path: str) -> str:
    return f"{PROVIDERS[provider]['base_url']}{path}"


# Every number here is read from the provider's live documentation, and the
# date it was read is in the comment above its block. Nothing in this table is
# remembered or inferred.
#
# Keep it honest: weekly.py logs whatever rate-limit headers the provider
# returns, and a logged value always outranks a value written here.
#
# `price_in` / `price_out` are USD per million tokens, cache-miss input. They
# are not a guard input; they exist so `python3 pipeline/budget.py` can print
# what an issue costs, which is the number finance books (ADR-32).
MODELS = {
    # Moonshot, read from https://platform.kimi.ai/docs/models,
    # https://platform.kimi.ai/docs/pricing/chat and
    # https://platform.kimi.ai/docs/pricing/limits on 2026-09-24.
    #
    # THE MODEL ID IS NOT `kimi-k2`. The dispatch and ADR-32 both say "Kimi
    # K2", and the bare `kimi-k2` series was discontinued on 2026-05-25: a
    # request to it would 404, which is incident 24 all over again on a new
    # provider. The current 256K-class general Kimi is `kimi-k2.6`. The other
    # two K2 ids in the catalog are `kimi-k2.7-code` and its high-speed
    # variant, which are coding models, and the press writes prose.
    #
    # TPM is the tier-0 number, the floor of what a funded account gets ($1
    # minimum recharge). Every higher tier has more. Even the floor is 500,000
    # TPM against a 262,144-token context, so the context is what binds and the
    # press's ~36,000-token request has room to spare at any tier.
    "kimi-k2.6": {
        "provider": "moonshot",
        "tpm": 500_000, "rpm": 3, "rpd": None, "tpd": 1_500_000,
        "context": 262_144, "max_output": 32_768, "status": "production",
        "price_in": 0.95, "price_out": 4.00,
    },

    # Groq's free tier, re-read from the live docs on 2026-09-24 (incident 24)
    # at https://console.groq.com/docs/rate-limits and cross-checked against
    # https://console.groq.com/docs/models.
    #
    # All three general text writers sit at 8,000 TPM and there is no free-tier
    # model above it that can write prose. At today's prompt size that ceiling
    # is below the prompt plus the output reservation, so these three cannot
    # print the weekly issue at all. They stay in the fallback list on purpose:
    # they are the last resort for the day the prompt gets shorter or the
    # ceiling moves, and the guard prints their arithmetic every run so nobody
    # has to guess whether that day has arrived.
    "openai/gpt-oss-120b": {
        "provider": "groq",
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 65_536, "status": "production",
        "price_in": 0.0, "price_out": 0.0,
    },
    "qwen/qwen3.8-27b": {
        "provider": "groq",
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 32_768, "status": "preview",
        "price_in": 0.0, "price_out": 0.0,
    },
    "openai/gpt-oss-20b": {
        "provider": "groq",
        "tpm": 8_000, "rpm": 30, "rpd": 1_000, "tpd": 200_000,
        "context": 131_072, "max_output": 65_536, "status": "production",
        "price_in": 0.0, "price_out": 0.0,
    },
}

# Models the press has pointed at, or that a reader might reasonably reach for,
# and that the provider has since withdrawn. Kept so a 404 is explained rather
# than raising a bare KeyError, and so nobody proposes a return to one of them
# without reading why it went.
#
# This is the failure class incident 24 named: PROVIDER MODEL DEPRECATION. It
# is not a Groq problem. Moonshot has run three deprecation waves of its own,
# and `kimi-k2` is in one of them, so the same discipline applies on both
# providers: the id in the code is the id in today's catalog, checked by
# `GET /models` before every deploy and at the start of every run.
DECOMMISSIONED = {
    "groq/compound": "404 Not Found as of 2026-09-23; absent from Groq's "
                     "model catalog and rate-limit table on 2026-09-24. Was "
                     "70,000 TPM, which is why the press was moved to it.",
    "groq/compound-mini": "withdrawn with groq/compound; same catalog absence.",
    "kimi-k2": "the bare kimi-k2 series was discontinued by Moonshot on "
               "2026-05-25. ADR-32 names 'Kimi K2' as the press's model and "
               "this is the id that sounds right and 404s; the live 256K "
               "general model is kimi-k2.6.",
    "kimi-k2.5": "discontinued by Moonshot on 2026-08-31, with kimi-k2.6 and "
                 "kimi-k3 as the migration path.",
    "moonshot-v1-128k": "the moonshot-v1 series was discontinued on "
                        "2026-08-31; use kimi-k2.6.",
}

# Headroom held back from the published ceiling. Three things live in it: the
# tokenizer estimate below is close but not the provider's own, the rolling
# window may still hold tokens from the citation pass or a retried call, and an
# editorial merge lands between one run and the next.
MARGIN = 0.15

# Chat framing the provider adds around the two messages. Measured generously;
# it is tens of tokens against a budget of thousands.
ENVELOPE_TOKENS = 32


def binding_limit(model: str) -> tuple[int, str]:
    """The ceiling a single request must fit inside, and which one it is.

    Two different ceilings can bind, on the same arithmetic: a per-minute token
    budget applied to one request (Groq's 413, incident 22) and the model's own
    context window (everywhere). Whichever is smaller is the real limit.
    """
    spec = MODELS[model]
    tpm, context = spec["tpm"], spec["context"]
    if tpm <= context:
        return tpm, f"{tpm} TPM"
    return context, f"{context}-token context"


def limit_for(model: str) -> int:
    """Usable tokens per request for `model`, margin already deducted."""
    if model in DECOMMISSIONED:
        raise KeyError(
            f"{model!r} was withdrawn by its provider: {DECOMMISSIONED[model]} "
            "A press cannot be pointed at it. Pick from budget.MODELS."
        )
    if model not in MODELS:
        raise KeyError(
            f"{model!r} has no published limits in budget.MODELS. Add it with "
            "the numbers from its provider's docs before pointing a press at it."
        )
    ceiling, _ = binding_limit(model)
    return int(ceiling * (1 - MARGIN))


def cost_usd(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """What one request costs at list price, worst case (no cache hit)."""
    spec = MODELS[model]
    return (prompt_tokens * spec["price_in"]
            + completion_tokens * spec["price_out"]) / 1_000_000


# ---------------- does the model still exist? ----------------

# Incident 24: the budget guard checked that the request fits and nothing
# checked that the model exists, so the press was pointed at a model Groq had
# withdrawn and the failure surfaced three days later as the owner noticing an
# empty inbox. `GET /models` is the cheapest possible answer to "can we print at
# all", it costs no tokens against any ceiling, and it runs twice: once at
# deploy and once at the start of every run.
#
# Both providers serve it at the same OpenAI-compatible path, so one function
# covers both: Groq at https://api.groq.com/openai/v1/models and Moonshot at
# https://api.moonshot.ai/v1/models, each with its own bearer key.


def models_url(provider: str) -> str:
    return endpoint(provider, "/models")


class AvailabilityError(RuntimeError):
    """The provider could not be asked which models it has."""


class NoUsableModel(RuntimeError):
    """Every candidate is either missing from the provider or over budget."""


def available_models(api_key: str, provider: str, timeout: float = 30.0) -> set[str]:
    """The set of model ids `provider` reports as active for this key.

    Raises rather than returning an empty set on any failure. An empty set and
    a failed request are the same value and very different facts, and treating
    a network blip as "every model is gone" would walk the whole fallback list
    for nothing.
    """
    if provider not in PROVIDERS:
        raise AvailabilityError(f"unknown provider {provider!r}")
    spec = PROVIDERS[provider]
    url = models_url(provider)

    # the cheap check first: no key is a configuration fact, not a network one
    if not api_key:
        raise AvailabilityError(
            f"no {provider} API key, so model availability cannot be checked. "
            f"Set the {spec['key_env']} that the `{spec['secret']}` Modal "
            "secret provides."
        )

    import httpx
    try:
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            timeout=timeout,
        )
    except Exception as exc:
        raise AvailabilityError(f"GET {url} failed: {exc}") from exc
    if resp.status_code >= 400:
        raise AvailabilityError(
            f"GET {url} answered {resp.status_code}: {resp.text[:500]}"
        )
    try:
        data = resp.json()["data"]
    except Exception as exc:
        raise AvailabilityError(
            f"GET {url} returned no usable model list: {resp.text[:500]}"
        ) from exc
    # `active` is Groq's own flag and a listed but inactive model still 404s.
    # Moonshot does not send one, so absent means listed means usable.
    return {m["id"] for m in data if m.get("active", True)}


def providers_for(models: list[str]) -> list[str]:
    """The providers a candidate list actually needs, primary first."""
    seen = [MODELS[m]["provider"] for m in models if m in MODELS]
    ordered = [p for p in PROVIDERS if p in seen]
    return ordered


def available_everywhere(models: list[str], env) -> tuple[set[str], list[str]]:
    """Ask every provider the candidate list touches. Returns (ids, notes).

    One provider being unreachable must not hide the models another provider
    still has, so a failure here is a note rather than an exception. The caller
    decides whether what survived is enough to print with, because that is a
    judgment about the press and not about HTTP.
    """
    found: set[str] = set()
    notes: list[str] = []
    for provider in providers_for(models):
        spec = PROVIDERS[provider]
        key = env.get(spec["key_env"], "")
        try:
            ids = available_models(key, provider)
        except AvailabilityError as exc:
            notes.append(f"{provider}: NOT REACHED. {exc}")
            continue
        found |= ids
        mine = [m for m in models if MODELS.get(m, {}).get("provider") == provider]
        missing = [m for m in mine if m not in ids]
        notes.append(
            f"{provider}: {len(ids)} models listed for this key; "
            + (f"MISSING {', '.join(missing)}" if missing
               else f"all {len(mine)} fallback(s) present"))
    return found, notes


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
            choice.rejected.append(
                (name, f"withdrawn by its provider. {DECOMMISSIONED[name]}"))
            continue
        if name not in MODELS:
            choice.rejected.append(
                (name, "no published limits in budget.MODELS, so no budget can "
                       "be checked for it"))
            continue
        if available is not None and name not in available:
            choice.rejected.append(
                (name, f"not in the {len(available)} models "
                       f"{MODELS[name]['provider']} reports for this key; a "
                       "request would 404"))
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
        # five counts since 2026-09-26, one per pipeline step; see gather()
        "stats": {"papers_ingested": 9999, "papers_triaged": 9999,
                  "papers_read_in_full": 9999, "claims_distilled": 9999,
                  "links_drawn": 9999},
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
        _, ceiling = binding_limit(self.model)
        verdict = "fits" if self.fits else "DOES NOT FIT"
        return (
            f"{self.model}: prompt {self.prompt_tokens} + payload "
            f"{self.payload_tokens} + output reservation {self.completion_tokens} "
            f"+ envelope {ENVELOPE_TOKENS} = {self.total} tokens against "
            f"{self.limit} usable ({ceiling} less {MARGIN:.0%} margin); "
            f"{verdict}, headroom {self.headroom}"
        )

    @property
    def cost(self) -> float:
        """List-price cost of this request, output reservation spent in full."""
        return cost_usd(self.prompt_tokens + self.payload_tokens
                        + ENVELOPE_TOKENS, self.completion_tokens, self.model)


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


def synthesis_models() -> list[str]:
    """rag_answer's ordered fallback list, read out of mcp/synthesis.py.

    Same discipline as `fallback_models`: read the production list rather than
    keeping a copy, because a guard with its own copy is a guard that verifies a
    list nothing uses. The MCP server is a runtime under
    docs/agents/runtime-changes.md, and until this ran, nothing checked that the
    model it calls still exists.
    """
    source = (ROOT / "mcp" / "synthesis.py").read_text()
    match = re.search(r"^FALLBACK_MODELS = (\[[^\]]*\])", source, re.M)
    if not match:
        raise LookupError(
            "mcp/synthesis.py no longer defines FALLBACK_MODELS where this "
            "guard looks for it. Fix the pattern in budget.synthesis_models(); "
            "a guard that cannot read the settings it checks is worse than no "
            "guard."
        )
    models = ast.literal_eval(match.group(1))
    if not isinstance(models, list) or len(models) < 2:
        raise LookupError(
            "mcp/synthesis.py FALLBACK_MODELS must be a list of at least two "
            f"models; found {models!r}. One model is a single point of failure, "
            "and incident 24 is what that costs."
        )
    return models


def model_problems(where: str, model: str,
                   available: set[str] | None = None) -> list[str]:
    """The three questions any caller of a model has to be able to answer.

    Does the id have a row here, has its provider withdrawn it, and does that
    provider still list it for this key. The press asks a fourth one, whether the
    request fits, and that needs a payload to measure. These three need nothing
    but the id, which is why every runtime that calls a model can be checked by
    the same command whether or not it has a payload.
    """
    if model in DECOMMISSIONED:
        return [f"{where} is {model}, withdrawn by its provider: "
                f"{DECOMMISSIONED[model]}"]
    if model not in MODELS:
        return [f"{where} ({model}) has no entry in budget.MODELS, so there is "
                "no provider to send it to"]
    if available is not None and model not in available:
        return [f"{where} ({model}) is not listed by {MODELS[model]['provider']} "
                "for this key; a request to it would 404"]
    return []


def check_synthesis(available: set[str] | None = None) -> list[str]:
    """Every model rag_answer can reach for has published limits and still exists.

    Returns problems, the way `check_drift` does. The MCP server does not size a
    payload against a ceiling, because a synthesis request is a short answer over
    retrieved context rather than a whole issue.
    """
    problems = []
    for rank, model in enumerate(synthesis_models(), start=1):
        problems += model_problems(f"rag_answer fallback {rank}", model, available)
    return problems


#: The scheduled corpus jobs that call a chat model. Both are Modal crons, both
#: are runtimes under docs/agents/runtime-changes.md, and until 2026-09-25
#: nothing checked the ids either of them calls. A withdrawal takes the corpus
#: down quietly: triage stops judging papers and interpret stops drawing edges,
#: and the only symptom is a red run nobody is watching.
#:
#: On 2026-09-26 both of them gained a fallback list and moved to Moonshot as
#: primary, so this reads a list rather than one id. The guard reads it out of
#: the job, never from a copy here, for the reason `fallback_models` gives.
CRON_MODELS = {
    "triage (pipeline/triage.py)": "pipeline/triage.py",
    "interpret (pipeline/interpret.py)": "pipeline/interpret.py",
}

#: What one run of each corpus job may spend, read out of the job. The cap is a
#: runtime number under docs/agents/runtime-changes.md in exactly the way a
#: token reservation is, and `check_cron_spend` is what stops it drifting into a
#: monthly bill nobody projected.
CRON_CAPS = {
    "triage (pipeline/triage.py)": ("pipeline/triage.py", "CAP_USD"),
    "interpret (pipeline/interpret.py)": ("pipeline/interpret.py", "CAP_USD"),
}

#: Together the two corpus caps plus the press. The ceiling finance books is the
#: sum of every cap firing every day, which is the worst case and not the
#: expectation; docs/finance/opex.md carries both numbers and the difference
#: between them. Raise this only with that file in the same commit.
MONTHLY_CAP_CEILING_USD = 30.0


def cron_model_lists() -> dict[str, list[str]]:
    """Each corpus cron's ordered model list, read out of the cron itself."""
    found: dict[str, list[str]] = {}
    for label, path in CRON_MODELS.items():
        source = (ROOT / path).read_text()
        match = re.search(r"^MODELS = (\[[^\]]*\])", source, re.M)
        if not match:
            raise LookupError(
                f"{path} no longer defines MODELS where this guard looks for "
                "it. Fix the pattern in budget.cron_model_lists(); a guard "
                "that cannot read the settings it checks is worse than no "
                "guard."
            )
        models = ast.literal_eval(match.group(1))
        if not isinstance(models, list) or len(models) < 2:
            raise LookupError(
                f"{path} MODELS must be a list of at least two models; found "
                f"{models!r}. One model is a single point of failure, and "
                "incident 24 is what that costs."
            )
        found[label] = models
    return found


def cron_models() -> dict[str, str]:
    """Each corpus cron's PRIMARY model, which is the head of its list.

    Kept as its own function because the head is the id that matters most: it
    is the one tomorrow's cron actually calls, and the one a rehearsal receipt
    has to name.
    """
    return {label: models[0] for label, models in cron_model_lists().items()}


def distill_models() -> list[str]:
    """Distill's models, production first, read out of its PROVIDERS table.

    Distill is the one corpus job that never moved to `pipeline/llm.py`, so it
    has a PROVIDERS dict instead of a MODELS list and `cron_model_lists` cannot
    read it. That difference is why it went unchecked, which is the whole reason
    this function exists rather than a copy of the two model ids.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    tree = ast.parse(source)
    providers = production = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        name = getattr(node.targets[0], "id", "")
        if name == "PROVIDERS":
            providers = ast.literal_eval(node.value)
        elif name == "PRODUCTION_PROVIDER":
            production = ast.literal_eval(node.value)
    if not providers or production not in providers:
        raise LookupError(
            "pipeline/distill.py no longer defines PROVIDERS and "
            "PRODUCTION_PROVIDER where this guard looks for them. A guard that "
            "cannot read the settings it checks is worse than no guard.")
    order = [production] + [k for k in providers if k != production]
    return [providers[k]["model"] for k in order]


def cron_caps() -> dict[str, float]:
    """Each corpus cron's per-run spend cap, read out of the cron."""
    found: dict[str, float] = {}
    for label, (path, name) in CRON_CAPS.items():
        source = (ROOT / path).read_text()
        match = re.search(rf"^{name} = ([\d.]+)", source, re.M)
        if not match:
            raise LookupError(
                f"{path} no longer defines {name} where this guard looks for "
                "it. A spend cap this guard cannot read is a spend cap nobody "
                "is projecting."
            )
        found[label] = float(match.group(1))
    return found


def check_crons(available: set[str] | None = None) -> list[str]:
    """Every model every corpus cron can reach for exists and has limits.

    The same three questions `model_problems` asks of everything else, now asked
    of the whole list rather than only the head, because a fallback that has
    never been checked is a fallback that fails at 3am.
    """
    problems = []
    for label, models in cron_model_lists().items():
        for rank, model in enumerate(models, start=1):
            problems += model_problems(f"{label} fallback {rank}", model,
                                       available)
    return problems


#: The worst request each corpus cron sends, so the guard can ask the press's
#: fourth question of them too: does it fit. The press cannot fit its request on
#: Groq's free tier at all, and its Groq entries are therefore a last resort that
#: has never printed. These two jobs are the opposite case and it is worth
#: proving rather than assuming: a triage batch is a few thousand tokens, so
#: Groq's 6,800 usable really can answer, and the fallback is a working fallback
#: instead of a comforting list.
#:
#: `prompt` is the file. `payload` is the largest user message the job builds,
#: measured rather than guessed: BATCH papers at title plus abstract[:1500] for
#: triage, one claim plus NEIGHBORS candidates for interpret. `reservation` is
#: read out of the job, so it cannot drift from what the job actually sends.
CRON_REQUESTS = {
    "triage (pipeline/triage.py)": {
        "path": "pipeline/triage.py",
        "prompt": "prompts/triage.md",
        "reservation": "MAX_COMPLETION_TOKENS",
        # BATCH * (title + abstract[:1500]); the filler is realistic English
        # because 'x' * n tokenizes far too cheaply.
        "payload_chars": 10 * 1_700,
    },
    "interpret (pipeline/interpret.py)": {
        "path": "pipeline/interpret.py",
        "prompt": "prompts/interpret.md",
        "reservation": "MAX_COMPLETION_TOKENS",
        # one claim plus five candidate claims, each capped by the distiller at
        # a few hundred characters; 400 each is generous.
        "payload_chars": 6 * 400,
    },
    # Distill was missing from this table until 2026-09-26 and it is the job
    # with the largest request in the pipeline by an order of magnitude: the
    # skills are the product and abstracts do not contain procedures, so every
    # arXiv paper in a run gets its HTML full text, FULLTEXT_CHARS of it.
    # L-E6 in docs/standards/lessons.md is why it is here now. Two prompts grew
    # on 2026-09-26 with the reasoning rubric, and a quality law that inflates a
    # runtime input is measured against the runtime budget rather than assumed
    # to fit.
    "distill (pipeline/distill.py)": {
        "path": "pipeline/distill.py",
        "prompt": "prompts/distill.md",
        # The job sends no output reservation at all, so there is no literal to
        # read. 1 to 5 claims, each with evidence and a numbered procedure,
        # measures around 1,500 tokens; 2,000 is the generous version of that.
        # The absence is itself worth seeing, which is why this is a separate key
        # rather than a number quietly written into the other one.
        "reservation_assumed": 2_000,
        "payload_chars": "FULLTEXT_CHARS",
        # What the job does when the provider refuses the full text: retries the
        # same call with abstract[:6000]. So the full-text request failing to fit
        # is a degradation rather than an outage, and the request that MUST fit is
        # this one.
        "degrades_to_chars": 6_000,
        "models": "distill",
    },
}


def request_models(label: str, spec: dict) -> list[str]:
    """The ordered model list for one CRON_REQUESTS entry."""
    return distill_models() if spec.get("models") == "distill" \
        else cron_model_lists()[label]


def request_reservation(spec) -> tuple[int, str]:
    """(tokens, how we know). Read out of the job, or the documented assumption."""
    if "reservation" in spec:
        source = (ROOT / spec["path"]).read_text()
        literal = _literal(source, rf"^{spec['reservation']} = ([\d_]+)",
                           f"{spec['path']} {spec['reservation']}")
        return int(literal.replace("_", "")), ""
    return spec["reservation_assumed"], " (assumed: the job sends none)"


def request_payload_chars(spec) -> int:
    """The largest user message the job builds, as a number or a name to read."""
    chars = spec["payload_chars"]
    if isinstance(chars, int):
        return chars
    source = (ROOT / spec["path"]).read_text()
    return int(_literal(source, rf"^{chars} = ([\d_]+)",
                        f"{spec['path']} {chars}").replace("_", ""))


def check_cron_requests() -> list[str]:
    """Every model a corpus cron can reach for can actually take its request.

    The press's own guard asks this of the press. Nothing asked it of the corpus
    jobs, which is how "Groq as fallback" could have been a list of three models
    that 413 on the first batch.
    """
    problems = []
    for label, spec in CRON_REQUESTS.items():
        prompt_path = ROOT / spec["prompt"]
        if not prompt_path.exists():
            problems.append(f"{label}: {spec['prompt']} is missing, so no "
                            "request can be sized for it")
            continue
        reservation, _ = request_reservation(spec)
        user = _filler(request_payload_chars(spec))
        degraded = (_filler(spec["degrades_to_chars"])
                    if "degrades_to_chars" in spec else None)
        for rank, model in enumerate(request_models(label, spec), start=1):
            if model not in MODELS:
                continue        # check_crons already reports this
            report = check_request(prompt_path.read_text(), user, reservation,
                                   model)
            if report.fits:
                continue
            if degraded is not None:
                # The job has a measured smaller request it retries with, so the
                # big one not fitting costs quality rather than the run. What
                # must fit is the retry, and if that does not fit either then the
                # job has nowhere left to go and this is a real problem.
                fallback = check_request(prompt_path.read_text(), degraded,
                                         reservation, model)
                if fallback.fits:
                    continue
            problems.append(
                f"{label} fallback {rank} ({model}) cannot take the job's "
                f"own request. {report.summary()}. A fallback that does not "
                "fit is not a fallback: either lower the reservation, "
                "shrink the batch, or take the model off the list so the "
                "run stops pretending it has somewhere to go.")
    return problems


def cron_degradations() -> list[str]:
    """Jobs whose big request does not fit, and that quietly send a smaller one.

    This is not a failure and it is not nothing. Distill fetches a paper's full
    text because the procedure is the product and an abstract has no procedure in
    it, then retries with the abstract when the provider refuses. The run
    succeeds, the claim is written, and the library read a summary. 164 of 8,956
    papers have ever been read in full, and this is the arithmetic behind that
    number rather than a theory about it.
    """
    notes = []
    for label, spec in CRON_REQUESTS.items():
        if "degrades_to_chars" not in spec:
            continue
        prompt_path = ROOT / spec["prompt"]
        if not prompt_path.exists():
            continue
        reservation, _ = request_reservation(spec)
        big = _filler(request_payload_chars(spec))
        small = _filler(spec["degrades_to_chars"])
        for rank, model in enumerate(request_models(label, spec), start=1):
            if model not in MODELS:
                continue
            full = check_request(prompt_path.read_text(), big, reservation, model)
            if full.fits:
                continue
            short = check_request(prompt_path.read_text(), small, reservation, model)
            notes.append(
                f"{label} rank {rank} ({model}) cannot take a full paper: "
                f"{full.summary()}. It falls back to abstract[:"
                f"{spec['degrades_to_chars']}], which "
                + ("fits, so the run succeeds and the paper is read from its "
                   "abstract instead of in full."
                   if short.fits else
                   "does NOT fit either, so the run cannot write a claim at all."))
    return notes


def cron_request_report() -> list[str]:
    """The same arithmetic, printed. One block per corpus cron."""
    lines = []
    for label, spec in CRON_REQUESTS.items():
        prompt_path = ROOT / spec["prompt"]
        if not prompt_path.exists():
            lines.append(f"  {label}: {spec['prompt']} missing")
            continue
        reservation, how = request_reservation(spec)
        user = _filler(request_payload_chars(spec))
        lines.append(f"  {label}, worst request, reservation {reservation}{how}")
        for rank, model in enumerate(request_models(label, spec), start=1):
            if model not in MODELS:
                continue
            report = check_request(prompt_path.read_text(), user, reservation,
                                   model)
            lines.append(f"    {rank}. [{MODELS[model]['provider']}] "
                         f"{report.summary()}")
            if rank == 1:
                lines.append(f"       ${report.cost:.5f} a call at list price")
    return lines


def monthly_projection() -> tuple[float, list[str]]:
    """The worst-case monthly spend if every corpus cap fires every day.

    Returns (usd, lines). This is the number finance books as a ceiling. It is
    not the expectation: a cap is only reached while a backlog exists, and the
    backlogs are finite. docs/finance/opex.md carries both.
    """
    caps = cron_caps()
    daily = sum(caps.values())
    lines = [f"  {label}: ${cap:.2f} a run, ${cap * 30:.2f} a month at 30 runs"
             for label, cap in sorted(caps.items())]
    return daily * 30, lines


def check_cron_spend() -> list[str]:
    """The corpus caps still add up to less than the ceiling finance was given."""
    projected, _ = monthly_projection()
    if projected > MONTHLY_CAP_CEILING_USD:
        return [
            f"the corpus crons' spend caps now project ${projected:.2f} a month "
            f"in the worst case, over the ${MONTHLY_CAP_CEILING_USD:.2f} "
            "ceiling in budget.MONTHLY_CAP_CEILING_USD. Raising a cap is a "
            "change to what the org spends, so it goes to the owner with "
            "docs/finance/opex.md updated in the same commit, never as a "
            "one-line edit to a job."
        ]
    return []


def check_kimi_windows() -> list[str]:
    """No two jobs that call Kimi can be running at the same time.

    Moonshot's organization concurrency is 1 on this account, which means a
    second Kimi call anywhere in the org gets a 429 and the run that meets it
    loses its slot. That was failure 2 of
    INC-2026-09-24-press-provider-migration, the press against a rehearsal.
    Nothing in code can serialize two Modal apps, so the schedule is the
    enforcement, and this is the check that the schedule still holds.

    `pipeline/llm.py` KIMI_WINDOWS is the table. This reads it and also reads
    each job's real cron minute out of its own source, so a schedule edit that
    forgets the table fails here rather than in production.
    """
    problems = []
    try:
        client = _llm()
    except Exception as exc:                     # noqa: BLE001
        return [f"pipeline/llm.py could not be read, so the Kimi concurrency "
                f"windows are unchecked: {exc}"]
    problems += client.window_overlaps()
    for label, path in {**CRON_MODELS,
                        "press (pipeline/weekly.py)": "pipeline/weekly.py"}.items():
        window = client.KIMI_WINDOWS.get(label)
        if window is None:
            problems.append(
                f"{label} calls a model on a schedule but has no entry in "
                "llm.KIMI_WINDOWS, so nothing checks it against the others.")
            continue
        source = (ROOT / path).read_text()
        for match in re.finditer(r'modal\.Cron\("(\d+)\s+(\d+)([^"]*)"\)', source):
            minute, hour = int(match.group(1)), int(match.group(2))
            start = hour * 60 + minute
            if not window[0] <= start < window[1]:
                problems.append(
                    f"{label} is scheduled at {hour:02d}:{minute:02d} UTC but "
                    f"llm.KIMI_WINDOWS gives it {window[0] // 60:02d}:"
                    f"{window[0] % 60:02d}-{window[1] // 60:02d}:"
                    f"{window[1] % 60:02d}. One of the two is wrong, and the "
                    "table is what the overlap check trusts.")
    return problems


def _llm():
    """pipeline/llm.py, imported without making budget.py depend on it at import."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_alexandria_llm", ROOT / "pipeline" / "llm.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    # 3. the head of the fallback list must take the real request at full
    #    PAYLOAD_CAPS and the real reservation, untrimmed. This is the check
    #    that makes the whole guard mean something: a press whose primary only
    #    fits after trimming is a press that quietly prints a thinner issue
    #    every week. ADR-32 moved the press to Kimi precisely so this holds.
    real = ROOT / "prompts" / "digest.md"
    if real.exists():
        head = fallback_models()[0]
        report = check_request(real.read_text(), encode(worst_case_payload()),
                               6_000, head)
        if not report.fits:
            failures.append(
                f"selftest: the primary model {head} cannot take the worst-case "
                f"request untrimmed. {report.summary()}")

    return failures


def main() -> int:
    payload_json = encode(worst_case_payload())
    print(f"worst-case payload: {len(payload_json)} chars, "
          f"{count_tokens(payload_json)} tokens "
          f"({'exact' if exact() else 'estimated'})\n")

    # Arithmetic run on estimates is not arithmetic. `count_tokens` falls back
    # to a chars-per-token ratio when tiktoken is missing, and that ratio is
    # deliberately pessimistic, so a request that fits can be reported as one
    # that does not. Everything measured below therefore carries the confidence
    # it was measured at, and the verdict at the bottom says which it was. Before
    # 2026-09-25 it did not: on a machine without tiktoken this command printed
    # `budget check FAILED (1 problem)` and advised shortening a generator prompt
    # that fits with room to spare. See INC-2026-09-25-budget-guard-estimates.
    measured = exact()

    failures = check_drift()
    for problem in failures:
        print(f"DRIFT: {problem}\n")

    # Only the token arithmetic is affected by the tokenizer. Drift, the model
    # tables and availability are exact either way, so they stay failures.
    unconfirmed = []
    for problem in selftest():
        if measured:
            failures.append(problem)
            print(f"SELFTEST: {problem}\n")
        else:
            unconfirmed.append(problem)
            print(f"SELFTEST (estimated counts, unconfirmed): {problem}\n")

    # Availability, for whichever providers have a key here. CI has none, and
    # that is fine: the deploy-time and run-time checks in weekly.py are the
    # ones that gate a real send. Here it is a bonus, never a requirement, so
    # the guard stays runnable offline.
    available = None
    candidates = fallback_models()
    if any(os.environ.get(PROVIDERS[p]["key_env"]) for p in providers_for(candidates)):
        available, notes = available_everywhere(candidates, os.environ)
        for note in notes:
            print(f"  {note}")
        for name in MODELS:
            provider = MODELS[name]["provider"]
            if not os.environ.get(PROVIDERS[provider]["key_env"]):
                continue
            if name not in available:
                failures.append(
                    f"{name} is in budget.MODELS but {provider} does not list "
                    "it; a press pointed at it would 404")
                print(f"  MISSING AT PROVIDER: {name}")
        print()
    else:
        missing = ", ".join(
            PROVIDERS[p]["key_env"] for p in providers_for(candidates))
        print(f"no provider key here ({missing}), so model existence is not "
              "checked. weekly.py checks it at deploy and at run start.\n")

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
            provider = MODELS[model]["provider"]
            print(f"  {rank}. [{provider}] {report.summary()}{flag}")
            if report.fits:
                if not fits_any:
                    # the first model that fits is the one that will write, so
                    # its cost is the issue's cost. ADR-32 budgeted ~$0.05.
                    print(f"     cost at list price, worst case: "
                          f"${report.cost:.4f} an issue "
                          f"(${MODELS[model]['price_in']:.2f}/M in, "
                          f"${MODELS[model]['price_out']:.2f}/M out)")
                fits_any = True

        if not fits_any:
            best = min(
                (check_request(prompt, payload_json, press.max_completion, m)
                 for m in press.models if m in MODELS),
                key=lambda r: -r.headroom, default=None)
            over = -best.headroom if best else 0
            complaint = (
                f"{press.name} does not fit ANY model in its fallback list; the "
                f"closest is {over} tokens over")
            (failures if measured else unconfirmed).append(complaint)
            print(f"  {'FAIL' if measured else 'UNCONFIRMED (estimated counts)'}: "
                  f"no model in the fallback list can take this "
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

    # The MCP server's synthesis list. It is not a press and has no payload to
    # size, but it is a runtime that calls a model, and nothing checked it until
    # 2026-09-25. Same command, so the same `&&` covers it.
    try:
        models = synthesis_models()
        print(f"rag_answer (mcp/synthesis.py, {len(models)} models in order)")
        for rank, model in enumerate(models, start=1):
            provider = MODELS.get(model, {}).get("provider", "?")
            flag = "" if available is None else (
                " [at provider]" if model in available else " [ABSENT AT PROVIDER]")
            print(f"  {rank}. [{provider}] {model}{flag}")
        for problem in check_synthesis(available):
            failures.append(problem)
            print(f"  SYNTHESIS: {problem}")
    except LookupError as exc:
        failures.append(str(exc))
        print(f"SYNTHESIS: {exc}")
    print()

    # The daily corpus crons. Since 2026-09-26 each has a fallback list with
    # Moonshot at the head, a per-run spend cap, and a scheduled window it has
    # to keep to, because Moonshot's organization concurrency is 1.
    try:
        print("daily corpus crons, in order, every entry checked")
        for label, models in cron_model_lists().items():
            print(f"  {label}")
            for rank, model in enumerate(models, start=1):
                provider = MODELS.get(model, {}).get("provider", "?")
                flag = "" if available is None else (
                    " [at provider]" if model in available
                    else " [ABSENT AT PROVIDER]")
                print(f"    {rank}. [{provider}] {model}{flag}")
        for problem in check_crons(available):
            failures.append(problem)
            print(f"  CRON: {problem}")
    except LookupError as exc:
        failures.append(str(exc))
        print(f"CRON: {exc}")
    print()

    # And the fourth question, the one only a payload can answer: does each
    # corpus job's own request fit every model it can reach for.
    try:
        print("\n".join(cron_request_report()))
        for problem in check_cron_requests():
            (failures if measured else unconfirmed).append(problem)
            print(f"  {'CRON REQUEST' if measured else 'UNCONFIRMED (estimated)'}"
                  f": {problem}")
    except LookupError as exc:
        failures.append(str(exc))
        print(f"CRON REQUEST: {exc}")

    # A job that shrinks its own request rather than failing is not a failure and
    # must not be silence either. This is where "read in full" quietly becomes
    # "read the abstract", and it is printed under its own heading so nobody has
    # to notice it inside a table of fits and headrooms.
    try:
        degraded = cron_degradations()
        if degraded:
            print("\n  reads less than it asked for (not a failure, a quality "
                  "ceiling):")
            for note in degraded:
                print(f"    {note}")
    except LookupError as exc:
        failures.append(str(exc))
        print(f"CRON DEGRADATION: {exc}")
    print()

    # What the corpus costs, at the caps the jobs actually carry. This is the
    # number docs/finance/opex.md books, printed by the same command that gates
    # the deploy, so the projection cannot drift away from the caps.
    try:
        projected, lines = monthly_projection()
        print("corpus spend, worst case (every cap reached every day)")
        print("\n".join(lines))
        print(f"  total: ${projected:.2f} a month against a "
              f"${MONTHLY_CAP_CEILING_USD:.2f} ceiling")
        print("  This is a ceiling, not an expectation: a cap is only reached "
              "while a backlog exists, and both backlogs are finite. See "
              "docs/finance/opex.md.")
        for problem in check_cron_spend():
            failures.append(problem)
            print(f"  SPEND: {problem}")
    except LookupError as exc:
        failures.append(str(exc))
        print(f"SPEND: {exc}")
    print()

    # Moonshot's organization concurrency is 1, so two Kimi jobs overlapping is
    # a 429 and a lost slot. The schedule is the only enforcement there is, and
    # this is the check that it still holds. A rule enforced by a link in a
    # command is enforced at the reliability of a shell.
    print("Kimi windows (organization concurrency is 1)")
    try:
        client = _llm()
        for label, (start, end) in sorted(client.KIMI_WINDOWS.items(),
                                          key=lambda kv: kv[1]):
            print(f"  {start // 60:02d}:{start % 60:02d}-{end // 60:02d}:"
                  f"{end % 60:02d} UTC  {label}")
    except Exception as exc:                     # noqa: BLE001
        print(f"  could not read the table: {exc}")
    for problem in check_kimi_windows():
        failures.append(problem)
        print(f"  CONCURRENCY: {problem}")
    print()

    if failures:
        print(f"budget check FAILED ({len(failures)} problem"
              f"{'s' if len(failures) > 1 else ''})")
        return 1
    if not measured:
        # Non-zero on purpose. This command is the first link in two deploy
        # chains, and a chain that proceeds on estimated numbers has not been
        # checked. The exit code says stop; the message says the press is not
        # known to be broken, which is the part the old verdict got wrong.
        print(f"budget check INCONCLUSIVE: token counts are estimated at "
              f"{FALLBACK_CHARS_PER_TOKEN} chars/token because tiktoken is not "
              f"installed here, and that estimate runs high. "
              f"{len(unconfirmed)} arithmetic check"
              f"{'s' if len(unconfirmed) != 1 else ''} could not be confirmed"
              + (f": {unconfirmed[0]}" if unconfirmed else "") +
              "\nEverything that does not depend on a token count passed: "
              "drift, the model tables, the fallback lists and availability.\n"
              "Run `pip install tiktoken && python3 pipeline/budget.py` for the "
              "real numbers.")
        return 2
    print("budget check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
