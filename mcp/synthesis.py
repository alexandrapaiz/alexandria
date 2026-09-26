"""The synthesis call behind `rag_answer`: an ordered model list, and one walk down it.

This lives outside `serve()` for the same reason mcp/oauth_flow.py does. Everything
in mcp/server.py's body runs inside a Modal container with secrets attached, so no
test can reach it without a deployment. The functions here take a `post` callable
and return a verdict, which is what lets tests/test_rag_fallback.py cover every
failure path on a laptop.

Why it exists: `rag_answer` called one hardcoded free-tier Groq model with no
availability check and no second choice, which is the exact shape of incident 24.
That incident was three press failures in five days (413, 429, 404) on a provider
whose free tier changes underneath its users, and the press answered it with an
ordered fallback list. The MCP server kept the single model, so it kept the
failure class. Two smaller gaps came with it: `json.loads` on the model's content
raised `JSONDecodeError` through MCP as a 500, and a read timeout did the same,
both of which are ordinary provider behaviour rather than server bugs.

Three things this deliberately does differently from pipeline/weekly.py.

* **No backoff.** The press is a cron with nobody waiting, so it sleeps up to
  three minutes on a 429 and tries the same model again. `rag_answer` answers a
  question somebody is watching a cursor blink for. A 429 here means the next
  model, immediately. Moving down the list is itself a rate-limit remedy.
* **No availability call per request.** Asking `/models` before every question
  would buy one round trip of latency on every answer to catch a withdrawal that
  happens a few times a year. The same question is asked once at deploy instead,
  by `mcp/server.py::preflight`, which is the link in the deploy chain.
* **One provider.** Every model here is served by the `groq` secret the MCP app
  already mounts. A cross-provider list would need the `moonshot` secret added to
  this app, which is a runtime change and therefore the owner's, not this
  module's. The ledger entry of 2026-09-25 carries that proposal.

The list itself is checked by `python3 pipeline/budget.py`, which reads it out of
this file rather than keeping a copy, and fails when an entry has no published
limits or has been withdrawn.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

#: Ordered. Every entry must have a row in `budget.MODELS`, and every entry is
#: served by the `groq` Modal secret this app already mounts. The first is the
#: model the server has always used, so the path a working provider takes is
#: unchanged: the rest of the list only ever runs on a bad day.
FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]

#: The default, and what the docstring above means by "unchanged". Whichever
#: model actually answered is returned by `synthesize`, never this constant.
MODEL = FALLBACK_MODELS[0]

CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

#: Seconds. A synthesis call is a short answer over retrieved context, so this is
#: a client timeout and not a budget: a model that has not started answering in a
#: minute is a model to step past, not one to wait out. Changing it is a runtime
#: change under docs/agents/runtime-changes.md.
REQUEST_TIMEOUT = 60.0

TEMPERATURE = 0.1


class SynthesisUnavailable(RuntimeError):
    """No model could answer, or the configuration makes asking pointless.

    Carries `notes`, one line per model tried, because "the synthesis model is
    unavailable" with no evidence is the message that sends a reader to the
    Modal logs. Incident 8: judge a run by its artifacts, never by its conclusion.
    """

    def __init__(self, message: str, notes: list[str] | None = None,
                 transient: bool = False):
        super().__init__(message)
        self.notes = notes or []
        #: True when at least one model failed in a way that asking again could
        #: fix, which is a 5xx or a transport error rather than a withdrawal.
        #: The ledger entry of 2026-09-25 about the press makes the case that a
        #: provider having a bad minute must not be read as a model that is
        #: gone. The press answers that with backoff, because nobody is waiting
        #: on a cron. Here the caller is waiting, so the answer is to say which
        #: of the two happened and let them decide whether to ask again.
        self.transient = transient


class UnusableAnswer(RuntimeError):
    """The provider answered 200 and the body is not an answer.

    Its own class rather than a bare `JSONDecodeError`, so the walk can treat a
    model that cannot hold the JSON contract the same way it treats a model that
    is rate limited, which is to try the next one.
    """


@dataclass
class Answer:
    """What `synthesize` returns: the parsed object, and who produced it."""

    data: dict
    model: str
    notes: list[str] = field(default_factory=list)


def transport_errors() -> tuple[type[BaseException], ...]:
    """The exception classes a transport raises that mean "this model, not us".

    httpx is imported here rather than at module scope so this file stays
    importable with nothing installed, the way oauth_flow.py is. `TimeoutException`
    is named even though it is a subclass of `TransportError`, because the read
    timeout is the specific gap this module was written to close.
    """
    try:
        import httpx
    except ModuleNotFoundError:
        return (OSError,)
    return (httpx.TimeoutException, httpx.TransportError, OSError)


def chat_request(model: str, system: str, user: str) -> dict:
    """The request body, as a value, so a test can assert on it without a network."""
    return {
        "model": model,
        "temperature": TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }


def parse_answer(body) -> dict:
    """The model's own JSON object, out of the provider's JSON envelope.

    Every shape that is not a JSON object raises `UnusableAnswer`, including a
    JSON array, because the caller reads `claim_ids_used` off this and `.get` on a
    list is an `AttributeError` at the far end of a tool call.
    """
    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise UnusableAnswer(
            f"no message content in the provider's response: {str(body)[:200]}"
        ) from exc
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise UnusableAnswer(
            f"the model did not return JSON: {content[:200]!r}"
        ) from exc
    if not isinstance(data, dict):
        raise UnusableAnswer(
            f"the model returned {type(data).__name__}, not a JSON object: "
            f"{content[:200]!r}"
        )
    return data


def _authentication_failure(status: int) -> bool:
    """A key problem, not a model problem, so the walk stops instead of continuing.

    Walking three models on a bad key makes three identical failed calls and then
    reports that every model is unavailable, which is false and sends whoever
    reads it to the wrong page of the wrong provider's dashboard.
    """
    return status in (401, 403)


def synthesize(post, api_key: str, system: str, user: str,
               models: list[str] | None = None,
               timeout: float = REQUEST_TIMEOUT) -> Answer:
    """Ask each model in turn until one answers. Raises `SynthesisUnavailable`.

    `post` is the transport, injected: `httpx.post` in production and a fake in
    the tests. It must return an object with `status_code`, `text` and `.json()`.
    """
    candidates = list(models if models is not None else FALLBACK_MODELS)
    if not candidates:
        raise SynthesisUnavailable("no synthesis model is configured")
    if not (api_key or "").strip():
        raise SynthesisUnavailable(
            "no GROQ_API_KEY, so there is nothing to ask. The `groq` Modal "
            "secret provides it to this app."
        )

    notes: list[str] = []
    transient = False
    for model in candidates:
        try:
            resp = post(
                CHAT_URL,
                headers={"Authorization": f"Bearer {api_key.strip()}"},
                json=chat_request(model, system, user),
                timeout=timeout,
            )
        except transport_errors() as exc:
            notes.append(f"{model}: {type(exc).__name__}: {exc}")
            transient = True
            continue

        status = getattr(resp, "status_code", 0)
        if _authentication_failure(status):
            raise SynthesisUnavailable(
                f"Groq refused the key with {status}. Every model would refuse "
                "the same way, so none were tried. Check the `groq` Modal secret.",
                notes,
            )
        if status >= 400:
            notes.append(f"{model}: HTTP {status}: {resp.text[:200]}")
            # 429 included: on the free tier a rate limit clears on its own, and
            # a caller who asks again in a minute gets an answer. A 404 does not
            # clear, and that is the distinction this flag exists to keep.
            transient = transient or status >= 500 or status == 429
            continue

        try:
            return Answer(parse_answer(resp.json()), model, notes)
        except UnusableAnswer as exc:
            notes.append(f"{model}: {exc}")
            continue
        except ValueError as exc:            # the envelope itself was not JSON
            notes.append(f"{model}: the provider's response was not JSON: {exc}")
            continue

    raise SynthesisUnavailable(
        ("every synthesis model is busy or unreachable right now, so this is "
         "worth asking again in a minute. Tried, in order: "
         if transient else
         "no synthesis model could answer, and none of them failed in a way "
         "that asking again would fix. Tried, in order: ")
        + ", ".join(candidates),
        notes,
        transient,
    )


def degraded(exc: SynthesisUnavailable, models: list[str] | None = None) -> dict:
    """What `rag_answer` returns when synthesis fails: a message, never a 500.

    Retrieval succeeded, so the caller is told which claims were found and can
    read them with `semantic_search` instead of being handed a stack trace.
    """
    return {
        "error": str(exc),
        "retry_worthwhile": exc.transient,
        "models_tried": list(models if models is not None else FALLBACK_MODELS),
        "notes": exc.notes,
    }
