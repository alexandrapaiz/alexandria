"""rag_answer's failure modes, as tests. Incident 24, applied to the MCP server.

The press learned this lesson three times in five days (413, 429, 404) and
answered it with an ordered fallback list. `rag_answer` kept one hardcoded
free-tier model, so it kept the failure class, and two of its error paths raised
a 500 through the tool call instead of answering: `json.loads` on a body that was
not JSON, and a read timeout.

Every path here only ever runs on a bad day, and a path that only runs on a bad
day is a path nothing has ever exercised. That is what these are for.

What is covered and what is not. `mcp/synthesis.py` is the whole walk and is
tested directly, transport injected, no network and no Modal. The three lines
inside `serve()` that call it cannot be reached without a deployment, which is
why they are three lines.

Run with `python3 -m pytest tests/test_rag_fallback.py -q`.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


synthesis = _load("alexandria_synthesis", "mcp/synthesis.py")
budget = _load("alexandria_budget", "pipeline/budget.py")


# ---------------- a transport that answers however a test wants ----------------

class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload) if payload is not None else text

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON in this response")
        return self._payload


def answer(content, model="whatever"):
    """A provider's envelope around whatever the model wrote."""
    return FakeResponse(200, {"choices": [{"message": {"content": content}}]})


def good(claim_ids=(1,)):
    return answer(json.dumps({"answer": "Yes, with caveats. [C1]",
                              "claim_ids_used": list(claim_ids)}))


class Recorder:
    """Plays a scripted reply per call and remembers what it was asked."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json,
                           "timeout": timeout})
        reply = self.replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        return reply

    @property
    def models(self):
        return [c["body"]["model"] for c in self.calls]


# ---------------- the list itself ----------------

def test_the_default_is_the_model_the_server_already_used():
    # The point of the change is resilience, not a model swap. A model swap is a
    # runtime change under docs/agents/runtime-changes.md and needs a rehearsal.
    assert synthesis.MODEL == "openai/gpt-oss-120b"
    assert synthesis.FALLBACK_MODELS[0] == synthesis.MODEL


def test_the_list_has_a_second_choice_and_no_duplicates():
    assert len(synthesis.FALLBACK_MODELS) >= 2
    assert len(set(synthesis.FALLBACK_MODELS)) == len(synthesis.FALLBACK_MODELS)


def test_every_model_is_served_by_the_secret_this_app_mounts():
    # A cross-provider list would need the `moonshot` secret added to the MCP
    # app, which is the owner's runtime change and not this module's.
    for model in synthesis.FALLBACK_MODELS:
        assert budget.MODELS[model]["provider"] == "groq"


# ---------------- the guard reads the production list ----------------

def test_the_budget_guard_reads_the_list_out_of_the_module():
    assert budget.synthesis_models() == synthesis.FALLBACK_MODELS


def test_the_guard_passes_on_todays_list():
    assert budget.check_synthesis() == []


def test_the_guard_catches_a_withdrawn_model(monkeypatch):
    monkeypatch.setattr(budget, "synthesis_models", lambda: ["groq/compound"])
    problems = budget.check_synthesis()
    assert len(problems) == 1
    assert "withdrawn" in problems[0]


def test_the_guard_catches_a_model_with_no_published_limits(monkeypatch):
    monkeypatch.setattr(budget, "synthesis_models", lambda: ["groq/invented-1"])
    problems = budget.check_synthesis()
    assert len(problems) == 1
    assert "no entry in budget.MODELS" in problems[0]


def test_the_guard_catches_a_model_the_provider_stopped_listing(monkeypatch):
    monkeypatch.setattr(budget, "synthesis_models",
                        lambda: ["openai/gpt-oss-120b"])
    problems = budget.check_synthesis(available={"qwen/qwen3.8-27b"})
    assert len(problems) == 1
    assert "would 404" in problems[0]


# ---------------- the happy path is unchanged ----------------

def test_the_first_model_answers_and_says_so():
    post = Recorder(good())
    result = synthesis.synthesize(post, "key-123", "SYSTEM", "USER")
    assert result.model == "openai/gpt-oss-120b"
    assert result.data["claim_ids_used"] == [1]
    assert result.notes == []
    assert len(post.calls) == 1


def test_the_request_still_asks_for_json_at_a_low_temperature():
    post = Recorder(good())
    synthesis.synthesize(post, "  key-123  ", "SYSTEM", "USER")
    call = post.calls[0]
    assert call["url"] == synthesis.CHAT_URL
    assert call["headers"]["Authorization"] == "Bearer key-123"
    assert call["body"]["response_format"] == {"type": "json_object"}
    assert call["body"]["temperature"] == 0.1
    assert call["body"]["messages"][0]["content"] == "SYSTEM"
    assert call["timeout"] == synthesis.REQUEST_TIMEOUT


# ---------------- the bad days ----------------

def test_a_rate_limit_moves_to_the_next_model_without_sleeping():
    # No backoff on purpose: somebody is watching a cursor blink. The press
    # sleeps because nobody is watching a cron.
    post = Recorder(FakeResponse(429, text="rate limit reached for ..."), good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert post.models == ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    assert result.model == "qwen/qwen3.8-27b"
    assert "429" in result.notes[0]


def test_a_withdrawn_model_moves_to_the_next_one():
    # Incident 24 itself: the model 404s because the provider retired it.
    post = Recorder(FakeResponse(404, text='{"error":"model not found"}'), good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert result.model == "qwen/qwen3.8-27b"


def test_a_read_timeout_moves_on_rather_than_raising_a_500():
    httpx = pytest.importorskip("httpx")
    post = Recorder(httpx.ReadTimeout("timed out"), good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert result.model == "qwen/qwen3.8-27b"
    assert "ReadTimeout" in result.notes[0]


def test_a_dropped_connection_moves_on_too():
    post = Recorder(OSError("connection reset by peer"), good())
    assert synthesis.synthesize(post, "key", "S", "U").model == "qwen/qwen3.8-27b"


def test_a_body_that_is_not_json_moves_on_rather_than_raising_a_500():
    # The `json.JSONDecodeError` gap, which used to surface as a 500 through MCP.
    post = Recorder(answer("I'm sorry, I cannot answer that."), good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert result.model == "qwen/qwen3.8-27b"
    assert "did not return JSON" in result.notes[0]


def test_a_json_array_is_not_an_answer():
    # `.get` on a list is an AttributeError at the far end of a tool call.
    post = Recorder(answer('["one", "two"]'), good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert result.model == "qwen/qwen3.8-27b"
    assert "not a JSON object" in result.notes[0]


def test_an_envelope_with_no_message_moves_on():
    post = Recorder(FakeResponse(200, {"choices": []}), good())
    assert synthesis.synthesize(post, "key", "S", "U").model == "qwen/qwen3.8-27b"


def test_an_unparseable_envelope_moves_on():
    post = Recorder(FakeResponse(200, None, text="<html>502 Bad Gateway</html>"),
                    good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert result.model == "qwen/qwen3.8-27b"
    assert "not JSON" in result.notes[0]


def test_the_walk_reaches_the_last_model():
    post = Recorder(FakeResponse(429, text="slow down"),
                    FakeResponse(503, text="upstream unavailable"),
                    good())
    result = synthesis.synthesize(post, "key", "S", "U")
    assert post.models == synthesis.FALLBACK_MODELS
    assert result.model == synthesis.FALLBACK_MODELS[-1]
    assert len(result.notes) == 2


# ---------------- when nothing works ----------------

def test_every_model_failing_raises_with_one_note_each():
    post = Recorder(*[FakeResponse(429, text="slow down")
                      for _ in synthesis.FALLBACK_MODELS])
    with pytest.raises(synthesis.SynthesisUnavailable) as caught:
        synthesis.synthesize(post, "key", "S", "U")
    assert len(caught.value.notes) == len(synthesis.FALLBACK_MODELS)
    for model in synthesis.FALLBACK_MODELS:
        assert model in str(caught.value)


def test_the_degraded_answer_carries_the_evidence():
    # Incident 8: judge a run by its artifacts. "Unavailable" with no evidence
    # is the message that sends a reader to the Modal logs.
    post = Recorder(*[FakeResponse(429, text="slow down")
                      for _ in synthesis.FALLBACK_MODELS])
    with pytest.raises(synthesis.SynthesisUnavailable) as caught:
        synthesis.synthesize(post, "key", "S", "U")
    degraded = synthesis.degraded(caught.value)
    assert degraded["models_tried"] == synthesis.FALLBACK_MODELS
    assert len(degraded["notes"]) == len(synthesis.FALLBACK_MODELS)
    assert "429" in degraded["notes"][0]


def test_a_refused_key_stops_the_walk_and_names_the_secret():
    # Walking three models on a bad key makes three identical failed calls and
    # then reports that every model is unavailable, which is false.
    post = Recorder(FakeResponse(401, text='{"error":"invalid api key"}'))
    with pytest.raises(synthesis.SynthesisUnavailable) as caught:
        synthesis.synthesize(post, "bad-key", "S", "U")
    assert len(post.calls) == 1
    assert "groq" in str(caught.value)


def test_no_key_is_a_configuration_fact_and_costs_no_calls():
    post = Recorder()
    with pytest.raises(synthesis.SynthesisUnavailable) as caught:
        synthesis.synthesize(post, "", "S", "U")
    assert post.calls == []
    assert "GROQ_API_KEY" in str(caught.value)


# ---------------- the daily crons, checked by the same command ----------------

def test_the_guard_reads_each_crons_model_out_of_the_cron():
    models = budget.cron_models()
    assert set(models) == set(budget.CRON_MODELS)
    for label, model in models.items():
        assert model in budget.MODELS, f"{label} calls an unknown model"


def test_the_crons_pass_today():
    assert budget.check_crons() == []


def test_the_guard_catches_a_cron_pointed_at_a_withdrawn_model(monkeypatch):
    # Incident 24 in the shape it would take here: the model is retired, and
    # the first symptom is a red cron nobody is watching.
    monkeypatch.setattr(budget, "cron_models", lambda: {"triage": "groq/compound"})
    problems = budget.check_crons()
    assert len(problems) == 1
    assert "withdrawn" in problems[0]


def test_the_guard_catches_a_cron_model_absent_at_the_provider(monkeypatch):
    monkeypatch.setattr(budget, "cron_models",
                        lambda: {"interpret": "openai/gpt-oss-120b"})
    problems = budget.check_crons(available={"qwen/qwen3.8-27b"})
    assert len(problems) == 1
    assert "would 404" in problems[0]


def test_the_guard_says_where_to_fix_the_pattern_if_a_cron_moves(monkeypatch):
    # A guard that cannot read the settings it checks is worse than no guard,
    # so it raises with the file to edit rather than silently checking nothing.
    monkeypatch.setitem(budget.CRON_MODELS, "invented", "pipeline/budget.py")
    with pytest.raises(LookupError) as caught:
        budget.cron_models()
    assert "budget.py MODEL" in str(caught.value)
