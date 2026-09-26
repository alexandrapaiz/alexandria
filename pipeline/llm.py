"""One JSON-answering chat client for the corpus jobs, with a spend cap.

The owner's finding, 2026-09-25: the corpus is not being read. 8,956 papers
ingested, 4,973 never triaged, 164 read in full, 746 claims, 11 to 14 links a
day against a 487-claim interpret backlog. Every one of those numbers is the
shape of Groq's free tier, where 8,000 tokens per minute means a run makes two
calls and then takes a 429 for the rest of the day. ADR-32 already moved the
press to Moonshot's Kimi on a funded account. This module moves triage and
interpret to the same place, and it is the only file they call a model from.

Three things live here and nowhere else.

**The fallback walk.** Kimi first, Groq's free tier behind it. Not because
Groq will succeed where Kimi failed, but because a single provider is a single
point of failure and incident 24 is what that costs. The walk is the same
shape as the press's (`pipeline/weekly.py` `write_digest`), deliberately: a
404 moves down the list at once, a 429 backs off on our own schedule because
Moonshot's concurrency-1 refusal is not a rate limit, and a run that exhausts
the list says so with one line per model.

**The spend cap.** A funded account can be drained by a loop, and the loop
this module serves is a backlog drain that wants to run as hard as it can.
`Cap` counts prompt and completion tokens out of the provider's own `usage`
block on every response, prices them through `budget.cost_usd`, and refuses
the next call once the run has spent its allowance. The cap is checked BEFORE
a call, so the job stops at the cap rather than one call past it, and the line
it prints is the real number rather than an estimate: `usage` is what the
provider billed.

**The one-at-a-time lock.** Moonshot's organization concurrency is 1 for this
account, which means a second Kimi call anywhere in the org gets a 429 saying
`max organization concurrency`. Failure 2 of
INC-2026-09-24-press-provider-migration was exactly that, the press against
the engineer's rehearsal. Nothing in code can serialize two Modal apps, so the
defence is in two halves: the backoff below waits minutes rather than the
1-second hint the header sends, and the crons are scheduled into slots that do
not overlap (see the `schedule=` comment on each job).

Kept free of Modal so the walk and the cap can be tested without a
deployment. `budget()` finds pipeline/budget.py whether it is beside this file
or dropped at /root by a Modal image, the same two-path trick weekly.py uses.
"""

from __future__ import annotations

import json
import pathlib
import time

# Retries per model before the walk gives up on it and tries the next one.
# Matches the press: a per-model 429 means moving down the list is itself a
# rate-limit remedy and not only a deprecation remedy.
RETRIES_PER_MODEL = 4
BACKOFF_SECONDS = 30      # doubled each attempt, capped below
BACKOFF_CEILING = 180

# Kimi reasons before it writes even with thinking disabled, and 300s timed out
# in production on 2026-09-24. These jobs send far smaller requests than the
# press does, so the ceiling is lower than weekly.py's 1500 and still generous.
CLIENT_TIMEOUT_SECONDS = 600


def budget():
    """pipeline/budget.py, wherever this is running from."""
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import budget as module

    return module


class ModelGone(RuntimeError):
    """The provider does not have this model any more. Incident 24's 404."""


class RateLimited(RuntimeError):
    """429 survived every retry on this model."""


class MissingKey(RuntimeError):
    """A provider's API key is not in this environment.

    Its own class rather than a bare KeyError, so the walk can treat "we cannot
    reach this provider" the way it treats a withdrawn model: record it, name
    the Modal secret that is missing, and try the next one.
    """


class CapReached(RuntimeError):
    """The run has spent its allowance. Not a failure; the caller stops."""


class NoModelAnswered(RuntimeError):
    """Every model in the list failed. Carries one line per model."""


def api_key_for(provider: str, env) -> str:
    """The key for `provider`, or a loud failure naming the Modal secret.

    Never prints the value. What it can say, when the value is absent, is which
    secret is missing and the command that creates it, because a job that dies
    on a KeyError for `MOONSHOT_API_KEY` tells the owner nothing.
    """
    spec = budget().PROVIDERS[provider]
    key = (env.get(spec["key_env"]) or "").strip()
    if not key:
        raise MissingKey(
            f"{spec['key_env']} is not in this environment, so this job cannot "
            f"reach {provider}. It comes from the Modal secret named "
            f"`{spec['secret']}`, which the chair creates with:\n"
            f"    modal secret create {spec['secret']} {spec['key_env']}=<paste>"
        )
    return key


class Cap:
    """A per-run spend ceiling, measured from the provider's own usage block.

    `limit_usd` is the allowance for one run of one job. Every response's
    `usage` is added at `budget.cost_usd`'s list prices, so `spent` is what the
    account was actually billed rather than a tokenizer's guess. `allows()` is
    asked before each call, which is what makes the job stop AT the cap: a
    drain loop that checked afterwards would always overshoot by one call, and
    on a 260K-context model one call is not a rounding error.

    A cap of 0 means "do not call a model at all", which is what the dry-run
    paths use. It is deliberately not the same as no cap; there is no no-cap.
    """

    def __init__(self, limit_usd: float, label: str = "run"):
        self.limit_usd = float(limit_usd)
        self.label = label
        self.spent = 0.0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.calls = 0
        self.per_model: dict[str, int] = {}

    def allows(self) -> bool:
        return self.spent < self.limit_usd

    def require(self) -> None:
        if not self.allows():
            raise CapReached(
                f"{self.label}: spent ${self.spent:.4f} of the "
                f"${self.limit_usd:.2f} cap over {self.calls} calls; stopping "
                "before the next one. The next run resumes where this stopped."
            )

    def record(self, model: str, usage: dict | None) -> None:
        """Book one response. Silence in `usage` is charged, not ignored.

        Moonshot and Groq both return `usage`. If one ever stops, charging zero
        would turn the cap into decoration, so an absent block is charged at
        the model's full context window: the cap trips early and loudly rather
        than late and invisibly.
        """
        guard = budget()
        usage = usage or {}
        prompt = int(usage.get("prompt_tokens") or 0)
        completion = int(usage.get("completion_tokens") or 0)
        if not prompt and not completion:
            prompt = guard.MODELS.get(model, {}).get("context", 0)
            print(f"  cap: {model} returned no usage block; charging its full "
                  f"{prompt}-token context so the cap errs toward stopping")
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.spent += guard.cost_usd(prompt, completion, model)
        self.calls += 1
        self.per_model[model] = self.per_model.get(model, 0) + 1

    def line(self) -> str:
        """The one line every run prints, whether or not it hit the cap."""
        split = ", ".join(f"{m}={n}" for m, n in sorted(self.per_model.items()))
        return (
            f"spend: ${self.spent:.4f} of ${self.limit_usd:.2f} cap over "
            f"{self.calls} calls ({self.prompt_tokens} prompt + "
            f"{self.completion_tokens} completion tokens"
            + (f"; {split}" if split else "") + ")"
        )


def _post(model: str, provider: str, key: str, system: str, user: str,
          max_completion: int, temperature: float):
    """One HTTP request. Separated so the retry loop reads as a retry loop."""
    import httpx

    guard = budget()
    body = {
        "model": model,
        "max_completion_tokens": max_completion,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if provider == "moonshot":
        # kimi-k2.6 is a thinking model, and on 2026-09-24 the hidden reasoning
        # ate the whole output reservation twice: finish_reason 'length', no
        # content. ADR-32 disables it. Moonshot also documents temperature as
        # fixed on k2.6, so sending one would be a knob that does nothing.
        body["thinking"] = {"type": "disabled"}
    else:
        body["temperature"] = temperature
    return httpx.post(
        guard.endpoint(provider, "/chat/completions"),
        headers={"Authorization": f"Bearer {key}"},
        json=body,
        timeout=CLIENT_TIMEOUT_SECONDS,
    )


def call_one(model: str, system: str, user: str, env, cap: Cap,
             max_completion: int = 2048, temperature: float = 0.2) -> dict:
    """Ask one model for JSON, with backoff on 429. Raises so the walk moves on.

    Returns the parsed JSON object. A response that is not JSON is `ModelGone`
    rather than a crash, because the next model in the list may well answer
    properly and a drain job should not die on one malformed reply.
    """
    guard = budget()
    provider = guard.provider_of(model)
    key = api_key_for(provider, env)

    for attempt in range(RETRIES_PER_MODEL):
        resp = _post(model, provider, key, system, user, max_completion,
                     temperature)

        if resp.status_code == 404:
            raise ModelGone(f"404 Not Found: {resp.text[:400]}")

        if resp.status_code == 429:
            # Moonshot's concurrency-1 refusal sends retry-after 1, and honoring
            # it is failure 2 of INC-2026-09-24-press-provider-migration: the
            # other call takes minutes, so the wait is our schedule and the
            # header can only lengthen it.
            wait = min(max(float(resp.headers.get("retry-after") or 0),
                           BACKOFF_SECONDS * (2 ** attempt)), BACKOFF_CEILING)
            if attempt < RETRIES_PER_MODEL - 1:
                print(f"  {model}: 429 (attempt {attempt + 1} of "
                      f"{RETRIES_PER_MODEL}); backing off {wait:.0f}s")
                time.sleep(wait)
                continue
            raise RateLimited(
                f"429 after {RETRIES_PER_MODEL} attempts: {resp.text[:400]}")

        if resp.status_code >= 400:
            # The body is where the provider states the actual limit and the
            # actual request size; raise_for_status() throws it away, and
            # incident 22 cost a day partly for that reason.
            print(f"  {provider} {resp.status_code} on {model}: {resp.text[:600]}")
            raise ModelGone(f"{resp.status_code}: {resp.text[:400]}")

        payload = resp.json()
        choice = payload["choices"][0]
        cap.record(model, payload.get("usage"))
        content = (choice["message"].get("content") or "").strip()
        if not content:
            raise ModelGone(
                f"{model} returned no content (finish_reason "
                f"{choice.get('finish_reason')!r})")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ModelGone(f"{model} did not return JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise ModelGone(f"{model} returned {type(parsed).__name__}, not an object")
        return parsed
    raise RateLimited(f"{model}: exhausted retries")


def ask_json(models: list[str], system: str, user: str, env, cap: Cap,
             max_completion: int = 2048, temperature: float = 0.2,
             available: set[str] | None = None) -> tuple[dict, str]:
    """Walk `models` until one answers with JSON. Returns (answer, model used).

    `cap.require()` runs first, so a job at its ceiling raises `CapReached`
    without sending anything. `available`, when given, is the set of ids the
    providers actually list for these keys, and a model missing from it is
    skipped without a request: incident 24's 404, never paid for twice.
    """
    cap.require()
    guard = budget()
    tried: list[str] = []
    for model in models:
        if model in guard.DECOMMISSIONED:
            tried.append(f"{model}: withdrawn by its provider")
            continue
        if available is not None and model not in available:
            provider = guard.MODELS.get(model, {}).get("provider", "?")
            tried.append(f"{model}: not listed by {provider} for this key; "
                         "skipped without a request")
            continue
        try:
            return call_one(model, system, user, env, cap, max_completion,
                            temperature), model
        except (ModelGone, RateLimited, MissingKey, KeyError) as exc:
            tried.append(f"{model}: {exc}")
            print(f"  {model} failed ({exc}); trying the next model")
            continue
    raise NoModelAnswered(
        "every model failed:\n  " + "\n  ".join(tried))


def usable_models(models: list[str], env) -> tuple[set[str] | None, list[str]]:
    """Which of `models` the providers list for these keys, or None if unknown.

    A thin pass-through to `budget.available_everywhere` so the jobs do not each
    reimplement it. None means the catalogs could not be read, and the walk then
    trusts the table and lets a 404 move it along, which is strictly better than
    refusing to run.
    """
    guard = budget()
    try:
        return guard.available_everywhere(models, env)
    except Exception as exc:                       # noqa: BLE001 - never fatal
        return None, [f"could not read provider catalogs ({exc}); "
                      "trusting budget.MODELS and letting a 404 move the walk on"]
