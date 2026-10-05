#!/usr/bin/env python3
"""Distill's two missing gates, and the question only distill's gate can ask.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The ladder in docs/agents/runtime-changes.md gives a provider or model change
three gates. On 2026-09-26 the press had all three and so did triage and
interpret. `distill` had none: no `preflight`, no `rehearse`, and no gate chain
in its deploy docstring, which is how the job whose entire purpose is reading
papers in full came to be unable to read one.

That last part is measured rather than feared. On 2026-09-26 `python3
pipeline/budget.py` put the miss at 109 tokens; on 2026-09-27 it turned out to
be about 1,900, because the guard was sizing a paper with a prose filler
(INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper). Either way the run
retried at `abstract[:6000]` and succeeded, which is the owner's finding of
2026-09-25 in miniature: 164 papers read in full out of 8,956. The request fits
now, at `FULLTEXT_CHARS` of 250,000 on kimi-k2.6, and
`tests/test_distill_fulltext_budget.py` is what holds it fitting.

Distill moved to Kimi through `pipeline/llm.py` on 2026-09-30, so the two gates
now walk a fallback list, carry a spend cap and read each provider's catalog.
These tests moved with it: the HTTP call is still one `httpx.post` and the
catalog read is still one `httpx.get`, both made inside `pipeline/llm.py` with
function-local imports, so replacing them here exercises the real walk rather
than a stub of it.

Nothing here calls a provider.
"""

import json
import pathlib
import sys

import httpx
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import distill                                                   # noqa: E402

SOURCE = (ROOT / "pipeline" / "distill.py").read_text()


class FakeResponse:
    def __init__(self, status, *, claims=None, institutions=None, raw=None):
        self.status_code = status
        # `pipeline/llm.py` prints the provider's own body on a refusal,
        # because that is where the actual limit and the actual request size
        # are stated and `raise_for_status()` throws it away. Incident 22 cost
        # a day partly for that reason, so the fake carries one.
        self.text = f"fake {status} body"
        self.headers = {}
        if raw is not None:
            # `/models` answers with its own shape, not a chat completion.
            self._body = raw
        else:
            payload = {"claims": claims or [], "institutions": institutions or []}
            self._body = {"choices": [{"message": {"content": json.dumps(payload)}}]}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=self)


GOOD_CLAIM = {
    "claim": "Distilling the reward model into the policy raises pairwise win rate to 71.3%.",
    "evidence": "Held-out split, three annotators, Krippendorff alpha 0.81.",
    "procedure": "1. SFT on 12,400 demonstrations. 2. Distil with KL penalty 0.02.",
    "topics": ["reasoning"],
}


@pytest.fixture(autouse=True)
def prompt_on_disk(monkeypatch):
    """`load_prompt` reads /root inside Modal. Point it at the repo's own file.

    It takes a `kind` as of 2026-09-30, when distill grew a second prompt for
    field reports, and the stub takes one too. A stub with the old arity made
    every test in this file fail with a TypeError rather than an assertion,
    which is the failure mode that tells you the stub is the thing that is
    stale.
    """
    text = (ROOT / "prompts" / "distill.md").read_text()
    monkeypatch.setattr(distill, "load_prompt",
                        lambda kind="paper": (text, "abc123def456"))
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")
    monkeypatch.setenv("MOONSHOT_API_KEY", "moonshot-key")


def catalog(monkeypatch, *ids):
    """Answer every provider's `/models` with this id list.

    The walk skips a model the provider does not list, without a request, so a
    test that forgets this gets "no model answered" instead of the behaviour it
    meant to exercise. Returns the urls that were asked.
    """
    asked = []

    def fake_get(url, headers=None, timeout=None):
        asked.append({"url": url, "headers": headers})
        return FakeResponse(200, raw={"data": [{"id": i} for i in ids]})

    monkeypatch.setattr(httpx, "get", fake_get)
    return asked


def post_returning(monkeypatch, *responses):
    """Replace the one HTTP call, and record every request body it received."""
    sent = []
    queue = list(responses)

    def fake_post(url, headers=None, json=None, timeout=None):
        sent.append({"url": url, "json": json, "timeout": timeout})
        return queue.pop(0) if len(queue) > 1 else queue[0]

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent


def chat(claims=None, institutions=None, status=200):
    """A chat completion the shared client will accept, with a usage block.

    The usage block is not decoration: `llm.Cap` charges a response with no
    usage at the model's whole context window, on purpose, so a fake without
    one trips the spend cap after a single call and the test fails for the
    wrong reason.
    """
    payload = {"claims": claims or [], "institutions": institutions or []}
    return FakeResponse(status, raw={
        "choices": [{"message": {"content": json.dumps(payload)},
                     "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 40_000, "completion_tokens": 900},
    })


# ---------------- the gate chain exists at all ----------------

def test_the_deploy_docstring_carries_all_three_gates_in_order():
    """The gate has to be in the command, not in the charter.

    runtime-changes.md's own words. The chair runs an `&&` chain, so the chain
    written here is the enforcement, and a gate missing from it is a gate that
    is skipped by default rather than on purpose.
    """
    chain = SOURCE[:SOURCE.index('"""', 3)]
    for i, link in enumerate([
        "python3 pipeline/budget.py",
        "modal run pipeline/distill.py::preflight",
        "modal run pipeline/distill.py::rehearse",
        "modal deploy pipeline/distill.py",
    ]):
        assert link in chain, f"gate {i + 1} missing from distill's deploy chain"
    assert (chain.index("::rehearse") < chain.index("modal deploy")), \
        "the rehearsal must come before the deploy or it is not a gate"


def test_both_gates_are_deployed_functions():
    assert callable(distill.preflight)
    assert callable(distill.rehearse)


# ---------------- the rehearsal's two promises ----------------

def test_the_rehearsal_has_no_database_credential():
    """The promise that leaves no trace when it is kept.

    A rehearsal must not be able to write a claim. The strongest form of that is
    a missing credential, not a missing function call, so it is asserted against
    the decorator rather than against behaviour.
    """
    block = SOURCE[SOURCE.index("def rehearse") - 900:SOURCE.index("def rehearse")]
    assert 'Secret.from_name("moonshot")' in block
    assert 'Secret.from_name("neon")' not in block, \
        "a rehearsal with a Neon credential can write a claim, which is the one " \
        "thing it must not be able to do"


def test_the_rehearsal_sends_a_full_paper_worth_of_payload(monkeypatch):
    """The size is the whole question, so the payload is the real ceiling."""
    catalog(monkeypatch, *distill.MODELS)
    sent = post_returning(monkeypatch, chat(claims=[GOOD_CLAIM]))
    distill.rehearse()
    content = sent[0]["json"]["messages"][1]["content"]
    assert len(content) >= distill.FULLTEXT_CHARS, \
        "a rehearsal that sends less than FULLTEXT_CHARS does not test the " \
        "request the daily run actually sends"
    assert sent[0]["json"]["model"] == distill.MODELS[0]
    assert sent[0]["json"]["max_completion_tokens"] == distill.MAX_COMPLETION_TOKENS
    assert sent[0]["url"].startswith("https://api.moonshot.ai/"), \
        "the head of the list is on Moonshot and the rehearsal must reach it"


def test_the_rehearsal_uses_the_real_prompt_and_response_format(monkeypatch):
    catalog(monkeypatch, *distill.MODELS)
    sent = post_returning(monkeypatch, chat(claims=[GOOD_CLAIM]))
    distill.rehearse()
    assert sent[0]["json"]["response_format"] == {"type": "json_object"}
    # Kimi reasons before it writes even with thinking disabled, and ADR-32
    # disables it; Moonshot documents temperature as fixed on k2.6, so sending
    # one would be a knob that does nothing.
    assert sent[0]["json"]["thinking"] == {"type": "disabled"}
    assert "temperature" not in sent[0]["json"]
    system = sent[0]["json"]["messages"][0]["content"]
    assert "claim" in system.lower(), "the real prompts/distill.md, not a stub"


def test_a_successful_rehearsal_reports_that_it_wrote_nothing(monkeypatch, capsys):
    catalog(monkeypatch, *distill.MODELS)
    post_returning(monkeypatch, chat(claims=[GOOD_CLAIM],
                                     institutions=["DeepMind"]))
    verdict = distill.rehearse()
    out = capsys.readouterr().out
    assert "wrote nothing" in out
    assert "read in full: True" in out
    assert "prompt_sha: abc123def456" in out
    assert "spend: $" in out, "the rehearsal costs money now and must say so"
    assert "rehearsal ok" in verdict and "in full" in verdict


# ---------------- the question only this gate asks ----------------

def test_a_refused_full_paper_stops_the_deploy(monkeypatch):
    """The finding, turned into a gate.

    The request fits as of 2026-09-27, so this gate should not fire. It stays
    because fitting is a property of today's prompt, today's density and
    today's provider limit, and all three move. A rehearsal that accepted the
    degradation would be green on the exact defect the owner named.
    """
    catalog(monkeypatch, *distill.MODELS)
    post_returning(monkeypatch, FakeResponse(413))
    with pytest.raises(RuntimeError) as exc:
        distill.rehearse()
    assert "Nothing was deployed" in str(exc.value)
    assert "abstract" in str(exc.value).lower()
    assert "--allow-abstract-only" in str(exc.value), \
        "a gate that blocks must name its escape hatch"


def test_the_escape_hatch_says_what_it_is_forgiving(monkeypatch, capsys):
    """Opinionated default, escape hatch, and a receipt that does not lie."""
    catalog(monkeypatch, *distill.MODELS)
    # Four refusals, one per model on the walk, then the abstract-sized retry
    # succeeds. The walk tries every model before it gives up, which is the
    # difference between this shape and the single-provider one it replaced.
    post_returning(monkeypatch, *([FakeResponse(413)] * 4),
                   chat(claims=[GOOD_CLAIM]))
    verdict = distill.rehearse(allow_abstract_only=True)
    out = capsys.readouterr().out
    assert "read in full: False" in out
    assert "from an abstract only" in verdict, \
        "the receipt must say which of the two things was proved"


def test_a_fallback_answering_is_not_a_receipt(monkeypatch):
    """New on 2026-09-30, and it is the gate the fallback list made necessary.

    Every model below kimi-k2.6 has a per-request budget smaller than one
    paper, so a rehearsal a Groq model answered proves the opposite of what the
    deploy needs to know. Triage's rehearsal has had this check since it moved;
    distill could not have it while it had one provider.
    """
    catalog(monkeypatch, *distill.MODELS)
    post_returning(monkeypatch, FakeResponse(404), chat(claims=[GOOD_CLAIM]))
    with pytest.raises(RuntimeError) as exc:
        distill.rehearse()
    assert distill.MODELS[0] in str(exc.value)
    assert "Nothing was deployed" in str(exc.value)


def test_an_empty_claims_list_stops_the_deploy(monkeypatch):
    """The silent failure: a paper marked processed with nothing written."""
    catalog(monkeypatch, *distill.MODELS)
    post_returning(monkeypatch, chat(claims=[]))
    with pytest.raises(RuntimeError, match="no claim with text"):
        distill.rehearse()


def test_a_claim_with_a_blank_text_does_not_count(monkeypatch):
    catalog(monkeypatch, *distill.MODELS)
    post_returning(monkeypatch, chat(claims=[{"claim": "   ",
                                              "topics": ["reasoning"]}]))
    with pytest.raises(RuntimeError, match="no claim with text"):
        distill.rehearse()


def test_an_off_list_topic_stops_the_deploy(monkeypatch):
    """Incident 30 and the 18 invisible claims, asked before a deploy."""
    catalog(monkeypatch, *distill.MODELS)
    claim = dict(GOOD_CLAIM, topics=["not-a-real-topic"])
    post_returning(monkeypatch, chat(claims=[claim]))
    with pytest.raises(RuntimeError) as exc:
        distill.rehearse()
    assert "off" in str(exc.value) and "closed list" in str(exc.value)
    assert "Nothing was deployed" in str(exc.value)


# ---------------- preflight ----------------

def test_preflight_raises_when_every_model_is_gone(monkeypatch):
    """Incident 24: a model retired under a running schedule."""
    catalog(monkeypatch, "some/other-model")
    with pytest.raises(RuntimeError) as exc:
        distill.preflight()
    assert "cannot read a single paper" in str(exc.value)
    assert "pipeline/distill.py MODELS" in str(exc.value)


def test_preflight_passes_when_the_production_model_is_listed(monkeypatch, capsys):
    catalog(monkeypatch, *distill.MODELS)
    verdict = distill.preflight()
    out = capsys.readouterr().out
    assert "preflight ok" in verdict
    assert distill.MODELS[0] in verdict
    # The two numbers the owner asked for by name, printed where the deploy is.
    assert "cost per paper" in out
    assert "projected monthly" in out


def test_preflight_warns_when_only_a_fallback_survives(monkeypatch, capsys):
    """A fallback can judge nothing here, and the note has to say so.

    Triage's equivalent note says the corpus drains at the free tier's pace.
    Distill's is harsher and the difference is the point: one Groq model's
    whole per-request budget is 6,800 tokens against a 98,800-token paper, so
    falling back does not slow the reading down, it stops it and keeps writing
    claims from abstracts.
    """
    catalog(monkeypatch, "openai/gpt-oss-120b")
    verdict = distill.preflight()
    out = capsys.readouterr().out
    assert "NOTE" in out
    assert "abstract" in out
    assert "openai/gpt-oss-120b" in verdict


def test_preflight_names_the_secret_and_never_the_value(monkeypatch, capsys):
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    distill.preflight_env_note = None
    with pytest.raises(RuntimeError):
        distill.preflight()
    out = capsys.readouterr().out
    assert "MOONSHOT_API_KEY" in out
    assert "moonshot-key" not in out and "groq-key" not in out


def test_preflight_asks_both_providers_with_the_real_keys(monkeypatch):
    asked = catalog(monkeypatch, *distill.MODELS)
    distill.preflight()
    urls = {a["url"] for a in asked}
    assert "https://api.moonshot.ai/v1/models" in urls
    assert "https://api.groq.com/openai/v1/models" in urls
    by_url = {a["url"]: a["headers"]["Authorization"] for a in asked}
    assert by_url["https://api.moonshot.ai/v1/models"] == "Bearer moonshot-key"
    assert by_url["https://api.groq.com/openai/v1/models"] == "Bearer groq-key"


def test_neither_gate_can_reach_the_claims_table():
    """Neither gate writes, and the reason is structural rather than careful."""
    start = SOURCE.index("def preflight")
    end = SOURCE.index("def drain_forecast")
    gates = SOURCE[start:end]
    for forbidden in ("insert into", "psycopg", "DATABASE_URL", "update "):
        assert forbidden not in gates.lower().replace("update the", ""), \
            f"a gate that can {forbidden!r} is not a gate"


def test_the_dry_run_cannot_call_a_model_even_by_mistake():
    """`drain` reads the queue and prices it. It must not be able to spend.

    The same structural promise the rehearsal makes about the database, made in
    the other direction: no provider secret in the container, so the plan
    cannot become the thing it is planning.
    """
    block = SOURCE[SOURCE.index("def drain(") - 500:SOURCE.index("def drain(")]
    assert 'Secret.from_name("neon")' in block
    assert 'Secret.from_name("moonshot")' not in block
    assert 'Secret.from_name("groq")' not in block
