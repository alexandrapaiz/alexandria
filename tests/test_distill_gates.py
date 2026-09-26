#!/usr/bin/env python3
"""Distill's two missing gates, and the question only distill's gate can ask.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The ladder in docs/agents/runtime-changes.md gives a provider or model change
three gates. On 2026-09-26 the press had all three and so did triage and
interpret. `distill` had none: no `preflight`, no `rehearse`, and no gate chain
in its deploy docstring, which is how the job whose entire purpose is reading
papers in full came to be unable to read one.

That last part is measured rather than feared. `python3 pipeline/budget.py`,
with tiktoken installed so the count is exact, prints that distill's full-paper
request misses Groq's usable free tier by 109 tokens on both of its models, and
that the run then retries at `abstract[:6000]` and succeeds. A job that succeeds while doing the lesser thing is the owner's
finding of 2026-09-25 in miniature: 164 papers read in full out of 8,956.

Nothing here calls a provider. `extract_claims` makes the one HTTP request the
job makes, with a function-local `import httpx`, so these tests replace
`httpx.post` and assert on what was sent and on what the caller did with it.
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
    """`load_prompt` reads /root inside Modal. Point it at the repo's own file."""
    text = (ROOT / "prompts" / "distill.md").read_text()
    monkeypatch.setattr(distill, "load_prompt", lambda: (text, "abc123def456"))
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")


def post_returning(monkeypatch, *responses):
    """Replace the one HTTP call, and record every request body it received."""
    sent = []
    queue = list(responses)

    def fake_post(url, headers=None, json=None, timeout=None):
        sent.append({"url": url, "json": json, "timeout": timeout})
        return queue.pop(0) if len(queue) > 1 else queue[0]

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent


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
    block = SOURCE[SOURCE.index("def rehearse") - 700:SOURCE.index("def rehearse")]
    assert 'Secret.from_name("groq")' in block
    assert 'Secret.from_name("neon")' not in block, \
        "a rehearsal with a Neon credential can write a claim, which is the one " \
        "thing it must not be able to do"


def test_the_rehearsal_sends_a_full_paper_worth_of_payload(monkeypatch):
    """The size is the whole question, so the payload is the real ceiling."""
    sent = post_returning(monkeypatch, FakeResponse(200, claims=[GOOD_CLAIM]))
    distill.rehearse()
    content = sent[0]["json"]["messages"][1]["content"]
    assert len(content) >= distill.FULLTEXT_CHARS, \
        "a rehearsal that sends less than FULLTEXT_CHARS does not test the " \
        "request the daily run actually sends"
    assert sent[0]["timeout"] == 180, "the real timeout, not a shorter one"
    assert sent[0]["json"]["model"] == distill.PROVIDERS["groq"]["model"]


def test_the_rehearsal_uses_the_real_prompt_and_response_format(monkeypatch):
    sent = post_returning(monkeypatch, FakeResponse(200, claims=[GOOD_CLAIM]))
    distill.rehearse()
    assert sent[0]["json"]["response_format"] == {"type": "json_object"}
    assert sent[0]["json"]["temperature"] == 0.2
    system = sent[0]["json"]["messages"][0]["content"]
    assert "claim" in system.lower(), "the real prompts/distill.md, not a stub"


def test_a_successful_rehearsal_reports_that_it_wrote_nothing(monkeypatch, capsys):
    post_returning(monkeypatch, FakeResponse(200, claims=[GOOD_CLAIM],
                                             institutions=["DeepMind"]))
    verdict = distill.rehearse()
    out = capsys.readouterr().out
    assert "wrote nothing" in out
    assert "read in full: True" in out
    assert "prompt_sha: abc123def456" in out
    assert "rehearsal ok" in verdict and "in full" in verdict


# ---------------- the question only this gate asks ----------------

def test_a_refused_full_paper_stops_the_deploy(monkeypatch):
    """The finding, turned into a gate.

    budget.py says the full-paper request misses by 109 tokens on either model
    and that the run degrades to the abstract and succeeds. A rehearsal that accepted the
    degradation would be green on the exact defect the owner named.
    """
    post_returning(monkeypatch, FakeResponse(413))
    with pytest.raises(RuntimeError) as exc:
        distill.rehearse()
    assert "Nothing was deployed" in str(exc.value)
    assert "abstract" in str(exc.value).lower()
    assert "--allow-abstract-only" in str(exc.value), \
        "a gate that blocks must name its escape hatch"


def test_the_escape_hatch_says_what_it_is_forgiving(monkeypatch, capsys):
    """Opinionated default, escape hatch, and a receipt that does not lie."""
    post_returning(monkeypatch, FakeResponse(413),
                   FakeResponse(200, claims=[GOOD_CLAIM]))
    verdict = distill.rehearse(allow_abstract_only=True)
    out = capsys.readouterr().out
    assert "read in full: False" in out
    assert "from an abstract only" in verdict, \
        "the receipt must say which of the two things was proved"


def test_an_empty_claims_list_stops_the_deploy(monkeypatch):
    """The silent failure: a paper marked processed with nothing written."""
    post_returning(monkeypatch, FakeResponse(200, claims=[]))
    with pytest.raises(RuntimeError, match="no claim with text"):
        distill.rehearse()


def test_a_claim_with_a_blank_text_does_not_count(monkeypatch):
    post_returning(monkeypatch, FakeResponse(200, claims=[{"claim": "   ",
                                                           "topics": ["reasoning"]}]))
    with pytest.raises(RuntimeError, match="no claim with text"):
        distill.rehearse()


def test_an_off_list_topic_stops_the_deploy(monkeypatch):
    """Incident 30 and the 18 invisible claims, asked before a deploy."""
    claim = dict(GOOD_CLAIM, topics=["not-a-real-topic"])
    post_returning(monkeypatch, FakeResponse(200, claims=[claim]))
    with pytest.raises(RuntimeError) as exc:
        distill.rehearse()
    assert "off" in str(exc.value) and "closed list" in str(exc.value)
    assert "Nothing was deployed" in str(exc.value)


# ---------------- preflight ----------------

def test_preflight_raises_when_the_production_model_is_gone(monkeypatch):
    """Incident 24: a model retired under a running schedule."""
    monkeypatch.setattr(httpx, "get", lambda *a, **k: FakeResponse(
        200, raw={"data": [{"id": "some/other-model"}]}))
    with pytest.raises(RuntimeError) as exc:
        distill.preflight()
    assert distill.PROVIDERS["groq"]["model"] in str(exc.value)
    assert "Nothing was deployed" in str(exc.value)


def test_preflight_passes_when_the_production_model_is_listed(monkeypatch, capsys):
    production = distill.PROVIDERS[distill.PRODUCTION_PROVIDER]["model"]
    monkeypatch.setattr(httpx, "get", lambda *a, **k: FakeResponse(
        200, raw={"data": [{"id": production}]}))
    verdict = distill.preflight()
    out = capsys.readouterr().out
    assert "preflight ok" in verdict
    assert "(production)" in out
    # The non-production bake-off model is absent here, and that is a note.
    assert "NOTE" in out
    # Fit is gate 1's question and preflight says so rather than guessing.
    assert "pipeline/budget.py" in out


def test_preflight_names_the_secret_and_never_the_value(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as exc:
        distill.preflight()
    assert "modal secret create groq" in str(exc.value)


def test_preflight_asks_the_provider_with_the_real_key(monkeypatch):
    seen = {}

    def fake_get(url, headers=None, timeout=None):
        seen.update(url=url, headers=headers)
        return FakeResponse(200, raw={"data": [
            {"id": p["model"]} for p in distill.PROVIDERS.values()]})

    monkeypatch.setattr(httpx, "get", fake_get)
    distill.preflight()
    assert seen["url"] == "https://api.groq.com/openai/v1/models"
    assert seen["headers"]["Authorization"] == "Bearer groq-key"


def test_neither_gate_can_reach_the_claims_table():
    """Neither gate writes, and the reason is structural rather than careful."""
    start = SOURCE.index("def preflight")
    end = SOURCE.index("def bake_off")
    gates = SOURCE[start:end]
    for forbidden in ("insert into", "psycopg", "DATABASE_URL", "update "):
        assert forbidden not in gates.lower().replace("update the", ""), \
            f"a gate that can {forbidden!r} is not a gate"
