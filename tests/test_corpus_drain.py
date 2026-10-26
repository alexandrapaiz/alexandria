"""The 2026-09-26 corpus move: Kimi as primary, a real cap, an honest drain.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The owner's finding was a set of numbers: 8,956 papers ingested, 4,973 never
triaged, 693 claims ungraded, 487 claims never linked. Every one of those is a
pipeline that stopped, and the fix is a provider change plus two drains plus a
backfill. What this file holds is the part of that fix a test can hold: the
spend cap's arithmetic, the fallback walk's behaviour on each failure the
providers actually produce, the backfill's idempotence, and the two promises
each rehearsal makes before a deploy is allowed.

Nothing here calls a provider. `llm._post` does the one HTTP request the client
makes, with a function-local `import httpx` so the Modal image stays the only
place httpx has to exist, so the tests replace `httpx.post` itself and assert on
what was sent and on what the caller did with what came back.
"""

import json
import pathlib
import re
import sys

import httpx
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import budget                                                    # noqa: E402
import distill                                                   # noqa: E402
import evidence                                                  # noqa: E402
import interpret                                                 # noqa: E402
import llm                                                       # noqa: E402
import triage                                                    # noqa: E402

ENV = {"MOONSHOT_API_KEY": "moonshot-key", "GROQ_API_KEY": "groq-key"}


class FakeResponse:
    def __init__(self, status, *, content=None, usage=None, headers=None,
                 text=None, finish_reason="stop"):
        self.status_code = status
        self.headers = headers or {}
        self._text = text
        self._body = {
            "choices": [{"message": {"content": content},
                         "finish_reason": finish_reason}],
            "usage": usage if usage is not None else {
                "prompt_tokens": 1_000, "completion_tokens": 200},
        }

    @property
    def text(self):
        return self._text if self._text is not None else json.dumps(self._body)

    def json(self):
        return self._body


class Recorder:
    """Hands back queued responses and keeps every request it was given."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError(f"unexpected extra call to {url}")
        return self.responses.pop(0)


def ok(payload, **kw):
    return FakeResponse(200, content=json.dumps(payload), **kw)


@pytest.fixture
def no_sleep(monkeypatch):
    """Backoff and pacing are real seconds in production and zero here."""
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)


# ---------------- the spend cap ----------------

#: These files assert token counts, and a count is only a measurement when the
#: real tokenizer produced it. Without tiktoken `pipeline/budget.py` falls back
#: to a chars-per-token ratio, and every one of these assertions then compares
#: the ratio against itself and fails with a message about a production defect
#: that is not there. Reporting a fallback ratio as a measurement is
#: INC-2026-09-25-budget-guard-estimates, and `tests/test_rag_fallback.py`
#: already guards its own three counting tests this way.
NEEDS_TIKTOKEN = (
    "these assertions are a measurement, and only the real tokenizer makes one. "
    "Run pip install tiktoken==0.8.0, which is what CI does."
)


def test_the_cap_is_measured_from_the_providers_own_usage_block():
    cap = llm.Cap(1.00, label="t")
    cap.record("kimi-k2.6", {"prompt_tokens": 1_000_000,
                             "completion_tokens": 1_000_000})
    # kimi-k2.6 is $0.95/M in and $4.00/M out, so a million of each is $4.95.
    assert cap.spent == pytest.approx(4.95)
    assert cap.prompt_tokens == 1_000_000 and cap.completion_tokens == 1_000_000
    assert cap.calls == 1


def test_a_response_with_no_usage_block_is_charged_not_ignored(capsys):
    # Charging zero would turn the cap into decoration. An absent block is
    # charged at the model's whole context window, so the cap trips early and
    # loudly rather than late and invisibly.
    cap = llm.Cap(1.00)
    cap.record("kimi-k2.6", None)
    assert cap.spent > 0
    assert cap.prompt_tokens == budget.MODELS["kimi-k2.6"]["context"]
    assert "no usage block" in capsys.readouterr().out


def test_the_cap_is_checked_before_a_call_so_a_run_stops_at_it_not_past_it(no_sleep, monkeypatch):
    # A drain loop that checked afterwards would overshoot by one call every
    # time, and on a 262K-context model one call is not a rounding error.
    cap = llm.Cap(0.001)
    cap.record("kimi-k2.6", {"prompt_tokens": 1_000, "completion_tokens": 200})
    post = Recorder()          # any call at all raises "unexpected extra call"
    monkeypatch.setattr(httpx, "post", post)
    with pytest.raises(llm.CapReached) as caught:
        llm.ask_json(["kimi-k2.6"], "sys", "user", ENV, cap)
    assert post.calls == []
    assert "stopping before the next one" in str(caught.value)
    assert "resumes" in str(caught.value)


def test_the_cap_line_names_the_real_numbers():
    cap = llm.Cap(0.60, label="triage")
    cap.record("kimi-k2.6", {"prompt_tokens": 3_513, "completion_tokens": 700})
    line = cap.line()
    assert "$0.60 cap" in line and "1 calls" in line
    assert "3513 prompt" in line and "700 completion" in line
    assert "kimi-k2.6=1" in line


# ---------------- the fallback walk ----------------

def test_kimi_is_asked_first_and_answers(no_sleep, monkeypatch):
    post = Recorder(ok({"results": [{"i": 0, "decision": "index"}]}))
    monkeypatch.setattr(httpx, "post", post)
    out, model = llm.ask_json(triage.MODELS, "sys", "user", ENV, llm.Cap(1.0))
    assert model == "kimi-k2.6"
    assert post.calls[0]["url"].startswith("https://api.moonshot.ai/")
    assert post.calls[0]["headers"]["Authorization"] == "Bearer moonshot-key"
    assert out["results"][0]["decision"] == "index"


def test_thinking_is_disabled_on_kimi_and_temperature_is_not_sent(no_sleep, monkeypatch):
    # kimi-k2.6 is a thinking model, and on 2026-09-24 the hidden reasoning ate
    # the whole output reservation twice. Moonshot also fixes temperature on
    # k2.6, so sending one would be a knob that does nothing.
    post = Recorder(ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    llm.ask_json(["kimi-k2.6"], "sys", "user", ENV, llm.Cap(1.0))
    body = post.calls[0]["json"]
    assert body["thinking"] == {"type": "disabled"}
    assert "temperature" not in body
    assert body["response_format"] == {"type": "json_object"}


def test_temperature_is_sent_to_groq(no_sleep, monkeypatch):
    post = Recorder(ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    llm.ask_json(["openai/gpt-oss-120b"], "sys", "user", ENV, llm.Cap(1.0),
                 temperature=0.2)
    assert post.calls[0]["json"]["temperature"] == 0.2
    assert "thinking" not in post.calls[0]["json"]


def test_a_404_moves_to_groq_without_waiting(no_sleep, monkeypatch):
    # Incident 24: a withdrawn model is not a slow model. No amount of backoff
    # fixes it, and moving down the list at once is the point of having one.
    post = Recorder(FakeResponse(404, text="not found"),
                    ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    out, model = llm.ask_json(triage.MODELS, "sys", "user", ENV, llm.Cap(1.0))
    assert model == "openai/gpt-oss-120b"
    assert len(post.calls) == 2
    assert post.calls[1]["headers"]["Authorization"] == "Bearer groq-key"


def test_a_429_waits_on_our_own_schedule_not_the_providers_hint(monkeypatch):
    # Moonshot's concurrency-1 refusal sends retry-after 1, and honoring it is
    # failure 2 of INC-2026-09-24-press-provider-migration: the other call takes
    # minutes, so the header can only ever lengthen our wait.
    slept = []
    monkeypatch.setattr(llm.time, "sleep", slept.append)
    post = Recorder(
        FakeResponse(429, text="max organization concurrency: 1",
                     headers={"retry-after": "1"}),
        ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    _, model = llm.ask_json(["kimi-k2.6"], "sys", "user", ENV, llm.Cap(1.0))
    assert model == "kimi-k2.6"
    assert slept == [llm.BACKOFF_SECONDS], slept


def test_a_longer_retry_after_is_honored(monkeypatch):
    slept = []
    monkeypatch.setattr(llm.time, "sleep", slept.append)
    post = Recorder(FakeResponse(429, headers={"retry-after": "90"}, text="slow"),
                    ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    llm.ask_json(["kimi-k2.6"], "sys", "user", ENV, llm.Cap(1.0))
    assert slept == [90.0]


def test_the_backoff_is_capped(monkeypatch):
    slept = []
    monkeypatch.setattr(llm.time, "sleep", slept.append)
    post = Recorder(*[FakeResponse(429, text="busy")
                      for _ in range(llm.RETRIES_PER_MODEL)])
    monkeypatch.setattr(httpx, "post", post)
    with pytest.raises(llm.RateLimited):
        llm.call_one("kimi-k2.6", "sys", "user", ENV, llm.Cap(1.0))
    assert max(slept) <= llm.BACKOFF_CEILING
    assert len(slept) == llm.RETRIES_PER_MODEL - 1


def test_a_reply_that_is_not_json_moves_on_rather_than_crashing(no_sleep, monkeypatch):
    # A drain job must not die on one malformed reply. The next model in the
    # list may well answer properly.
    post = Recorder(FakeResponse(200, content="Sure! Here are the results:"),
                    ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    _, model = llm.ask_json(triage.MODELS, "sys", "user", ENV, llm.Cap(1.0))
    assert model == "openai/gpt-oss-120b"


def test_an_empty_content_is_a_failure_with_the_finish_reason_in_it(no_sleep, monkeypatch):
    # Failure 1 of INC-2026-09-24-press-provider-migration was a silent empty
    # response. The finish_reason is the difference between legible and not.
    post = Recorder(FakeResponse(200, content=None, finish_reason="length"))
    monkeypatch.setattr(httpx, "post", post)
    with pytest.raises(llm.ModelGone) as caught:
        llm.call_one("kimi-k2.6", "sys", "user", ENV, llm.Cap(1.0))
    assert "'length'" in str(caught.value)


def test_a_missing_key_names_the_modal_secret_and_never_the_value(no_sleep, monkeypatch):
    post = Recorder(ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    _, model = llm.ask_json(["kimi-k2.6", "openai/gpt-oss-120b"], "sys", "user",
                            {"GROQ_API_KEY": "groq-key"}, llm.Cap(1.0))
    assert model == "openai/gpt-oss-120b"
    with pytest.raises(llm.MissingKey) as caught:
        llm.api_key_for("moonshot", {})
    message = str(caught.value)
    assert "modal secret create moonshot" in message
    assert "groq-key" not in message


def test_a_model_absent_at_the_provider_is_skipped_without_a_request(no_sleep, monkeypatch):
    post = Recorder(ok({"ok": True}))
    monkeypatch.setattr(httpx, "post", post)
    _, model = llm.ask_json(triage.MODELS, "sys", "user", ENV, llm.Cap(1.0),
                            available={"openai/gpt-oss-120b"})
    assert model == "openai/gpt-oss-120b"
    assert len(post.calls) == 1, "a 404 was paid for that the catalog predicted"


def test_every_model_failing_names_every_one_of_them(no_sleep, monkeypatch):
    post = Recorder(*[FakeResponse(404, text="gone") for _ in triage.MODELS])
    monkeypatch.setattr(httpx, "post", post)
    with pytest.raises(llm.NoModelAnswered) as caught:
        llm.ask_json(triage.MODELS, "sys", "user", ENV, llm.Cap(1.0))
    for model in triage.MODELS:
        assert model in str(caught.value)


def test_a_catalog_read_that_fails_never_stops_the_run(monkeypatch):
    # None means "unknown", and the walk then trusts the table and lets a 404
    # move it along, which is strictly better than refusing to run.
    def boom(*a, **k):
        raise RuntimeError("moonshot is down")
    monkeypatch.setattr(budget, "available_everywhere", boom)
    available, notes = llm.usable_models(triage.MODELS, ENV)
    assert available is None
    assert "letting a 404 move the walk on" in notes[0]


# ---------------- pacing and the concurrency band ----------------

def test_pacing_comes_from_the_published_rpm():
    # kimi-k2.6 is 3 requests a minute at tier 0, which is 20 seconds, and that
    # is what actually decides how fast a backlog drains.
    assert llm.pace("kimi-k2.6") == pytest.approx(20.0)
    assert budget.MODELS["kimi-k2.6"]["rpm"] == 3


def test_a_model_with_no_published_rpm_keeps_the_old_pause():
    assert llm.pace("not-a-model") == 3.0


def test_every_job_that_can_call_kimi_has_a_window():
    labels = set(llm.KIMI_WINDOWS)
    assert "press (pipeline/weekly.py)" in labels
    for label in budget.CRON_MODELS:
        assert label in labels, f"{label} calls Kimi with no declared window"


# ---------------- triage ----------------

def test_the_triage_batch_carries_the_tier_and_a_truncated_abstract():
    rendered = triage.render_batch([
        ("p1", "A Title", "x" * 5_000, "a"),
        ("p2", "Another", None, "b"),
    ])
    assert "[0] tier=a" in rendered and "[1] tier=b" in rendered
    assert "x" * 1_500 in rendered and "x" * 1_501 not in rendered
    assert "(no abstract; judge from title)" in rendered


def test_the_tier_drain_is_fair_under_truncation():
    # The starvation bug: 2,445 papers, zero triage rows, because one tier was
    # always sent first. Fairness has to live in the send order.
    rows = [(f"{tier}{i}", "t", "a", tier)
            for tier in ("a", "b", "a-low", "c", "d") for i in range(50)]
    plan = triage.plan_batches(rows, max_calls=5)
    assert len({chunk[0][3] for chunk in plan}) == 5, "one tier took every call"


def test_the_drain_forecast_is_a_remainder_and_a_run_count():
    assert "3 more runs" in triage.drain_forecast(300, 100)
    assert "1 more run" in triage.drain_forecast(100, 100)
    assert "judged none" in triage.drain_forecast(4_973, 0)


def test_the_rehearsal_batch_is_not_all_one_answer():
    # A model answering 'index' to everything has to fail the gate, so the
    # sample has to contain papers whose right answers differ.
    assert all(len(row) == 4 for row in triage.REHEARSAL_BATCH)
    assert len({row[0] for row in triage.REHEARSAL_BATCH}) == len(triage.REHEARSAL_BATCH)
    rendered = triage.render_batch(list(triage.REHEARSAL_BATCH))
    assert "Fourier" in rendered and "Context Rot" in rendered
    # Four decisions exist and the sample has to be able to draw all four, which
    # it cannot do from one tier: the tier is in the user message and a batch
    # that is all tier `a` tells the model the answer before it reads anything.
    assert len({row[3] for row in triage.REHEARSAL_BATCH}) >= 3


def test_the_triage_cap_buys_more_than_one_call_at_the_worst_case_price():
    # A cap below the price of a single call would make every run a no-op that
    # looks like a cap working.
    ceiling = budget.cost_usd(3_513 + 1_200, 0, "kimi-k2.6") \
        + budget.cost_usd(0, 1_200, "kimi-k2.6")
    assert triage.CAP_USD > 10 * ceiling


# ---------------- interpret ----------------

def test_interpret_takes_the_oldest_claims_first():
    # The owner asked for oldest first by name, and an old claim's neighbors are
    # already in the graph, so its edges connect the most.
    source = (ROOT / "pipeline" / "interpret.py").read_text()
    assert "from interpret_queue order by id limit" in source


def test_only_relations_the_schema_allows_and_ids_on_the_shortlist_become_edges():
    out = {"results": [
        {"candidate_id": 101, "relation": "supports", "confidence": 0.9},
        {"candidate_id": 101, "relation": "inspires", "confidence": 0.9},
        {"candidate_id": 999, "relation": "supports", "confidence": 0.9},
        {"candidate_id": 102, "relation": "contradicts"},
        "not a dict",
    ]}
    edges = interpret.edges_from(out, {101, 102})
    assert edges == [(101, "supports", 0.9), (102, "contradicts", None)]


def test_every_relation_interpret_will_write_is_in_the_schema():
    schema = (ROOT / "db" / "schema.sql").read_text()
    for relation in interpret.RELATIONS:
        assert f"'{relation}'" in schema, relation


def test_the_rehearsal_shortlist_has_a_knowable_right_answer():
    # Half should relate and half should not, which is what lets the rehearsal
    # fail a model that labels everything and one that labels nothing.
    ids = [nid for nid, _ in interpret.REHEARSAL_NEIGHBORS]
    assert len(set(ids)) == len(ids)
    rendered = interpret.render_candidates(interpret.REHEARSAL_CLAIM,
                                           interpret.REHEARSAL_NEIGHBORS)
    assert rendered.startswith("NEW claim:")
    assert "Candidates:" in rendered
    for nid in ids:
        assert f"[{nid}]" in rendered


# ---------------- the grading backfill ----------------

def test_the_backfill_grade_is_deterministic_which_is_what_makes_it_idempotent():
    row = ("arxiv:2609.11042", "accuracy rose from 61.4 to 74.9", None)
    assert evidence.backfill_grade(*row) == evidence.backfill_grade(*row)


def test_the_backfill_reads_the_source_class_off_the_paper_id():
    assert evidence.backfill_grade("arxiv:2609.1", "38.2% better") == "controlled"
    assert evidence.backfill_grade("arxiv:2609.1", "they argue it works") == "asserted"
    assert evidence.backfill_grade("blog:x:1", "p95 fell 40ms") == "field_measured"
    assert evidence.backfill_grade("blog:x:1", "it works well") == "anecdote"


def test_a_claim_with_no_evidence_at_all_grades_on_source_class_alone():
    assert evidence.backfill_grade("arxiv:2609.1", None) == "asserted"
    assert evidence.backfill_grade("blog:x:1", "") == "anecdote"


def test_every_grade_the_backfill_can_write_is_one_the_schema_accepts():
    schema = (ROOT / "db" / "schema.sql").read_text()
    for grade in evidence.GRADES:
        assert f"'{grade}'" in schema, grade


def test_the_backfill_errs_generous_never_harsh_and_says_so():
    # The live grader needs the model's `measured` boolean AND a number in the
    # text. The backfill has only the text, so it is the permissive half of the
    # pair: it can be one step stronger, never one step weaker.
    strict = evidence.grade("arxiv:2609.1", "38.2% better", measured=False)
    loose = evidence.backfill_grade("arxiv:2609.1", "38.2% better")
    assert (strict, loose) == ("asserted", "controlled")
    order = list(evidence.GRADES)
    assert order.index(loose) < order.index(strict)
    assert "never weaker" in evidence.__doc__


def test_the_backfills_query_only_ever_touches_ungraded_rows():
    # Idempotence and resumability both come from this one clause. There is no
    # cursor, no state table and nothing to reset.
    sys.path.insert(0, str(ROOT / "pipeline"))
    import backfill_grades

    assert "evidence_grade is null" in backfill_grades.UNGRADED_SQL
    source = (ROOT / "pipeline" / "backfill_grades.py").read_text()
    assert "where id = %s and evidence_grade is null" in source, (
        "the UPDATE must repeat the guard at row level, or a concurrent distill "
        "run's better grade gets overwritten by this weaker one")


def test_the_backfill_has_no_model_secret_and_therefore_no_bill():
    source = (ROOT / "pipeline" / "backfill_grades.py").read_text()
    assert "moonshot" not in source.lower().replace("moonshot's", "")
    assert "GROQ" not in source


def test_the_dry_run_and_the_write_are_separate_functions():
    source = (ROOT / "pipeline" / "backfill_grades.py").read_text()
    assert "def count(" in source and "def backfill(" in source
    # the local entrypoint is the dry run, so `modal run` alone writes nothing
    assert "print(count.remote())" in source


# ---------------- the press stats line ----------------

def test_the_press_stats_name_all_five_steps():
    # Owner's directive 2026-09-25: the stats line says what happened, not
    # "read N papers". Three counts could not say it.
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    for key in ("papers_ingested", "papers_triaged", "papers_read_in_full",
                "claims_distilled", "links_drawn"):
        assert f'"{key}"' in source, key
    # and the worst case the guard measures has to carry the same five, or the
    # budget arithmetic is run against a payload the press does not produce
    assert set(budget.worst_case_payload()["stats"]) == {
        "papers_ingested", "papers_triaged", "papers_read_in_full",
        "claims_distilled", "links_drawn"}


def test_read_in_full_comes_from_a_column_and_not_from_an_assumption():
    schema = (ROOT / "db" / "schema.sql").read_text()
    assert "fulltext_chars" in schema
    weekly = (ROOT / "pipeline" / "weekly.py").read_text()
    assert "fulltext_chars is not null" in weekly


def test_a_rule_backfilled_paper_does_not_count_as_triaged():
    # A paper auto-indexed by date rule was never judged by anything, and
    # counting it would be the same flattery one step along.
    weekly = (ROOT / "pipeline" / "weekly.py").read_text()
    assert "model != 'rule:backfill'" in weekly


def test_the_writer_is_told_which_number_means_read():
    prompt = (ROOT / "prompts" / "digest.md").read_text()
    assert "papers_read_in_full" in prompt
    assert "the only" in prompt.split("papers_read_in_full")[1][:400]


# ---------------- the free tier is priced at zero, which is a division ----------------

def test_the_cap_phrase_does_not_divide_by_a_free_models_price():
    # Found by self-review, not by a failure: `int(cap / cost)` raises
    # ZeroDivisionError on every Groq model, because the free tier is priced at
    # $0.00/M in budget.MODELS and that is the correct price. Both preflights
    # hit it the moment Kimi is absent at the provider and a free-tier fallback
    # is the only usable model, which is exactly the case a preflight exists to
    # report legibly rather than crash in.
    paid = llm.calls_within(0.60, 3_500, 700, "kimi-k2.6")
    assert "97 calls" in paid and "$0.60 cap" in paid
    free = llm.calls_within(0.60, 3_500, 700, "openai/gpt-oss-120b")
    assert "cannot bind" in free
    assert budget.MODELS["openai/gpt-oss-120b"]["price_in"] == 0.0


def test_neither_preflight_computes_a_price_by_bare_division():
    for path in ("triage.py", "interpret.py"):
        source = (ROOT / "pipeline" / path).read_text()
        assert "CAP_USD / est" not in source, path
        assert "calls_within" in source, path


# ---------------- distill, the job the guard could not see ----------------

def test_the_guard_reads_distills_models_out_of_distills_own_table():
    # Distill had a PROVIDERS dict rather than a MODELS list until 2026-09-30,
    # so `cron_model_lists` could not read it and it went unchecked for as long
    # as it did. It is in the shared table now, and the reader still has to be
    # real rather than a copy.
    models = budget.distill_models()
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert models[0] == "kimi-k2.6", models
    assert models == budget.cron_model_lists()["distill (pipeline/distill.py)"]
    for model in models:
        assert f'"{model}"' in source
        assert model in budget.MODELS, f"{model} has no limits in budget.MODELS"


def test_every_corpus_cron_leads_with_the_funded_account():
    # The whole of the 2026-09-26 and 2026-09-30 migrations in one assertion:
    # a corpus job whose head is a free-tier model is a job that takes a 429
    # after two calls and calls it a day's work.
    for label, models in budget.cron_model_lists().items():
        assert models[0] == budget.PRIMARY_MODEL, (
            f"{label} leads with {models[0]}, not the funded account. "
            "That is the shape of 'the corpus is not being read'.")


def test_every_corpus_job_is_in_the_request_table():
    # L-E6: a prompt that grows is measured against the runtime budget. A job
    # missing from this table is a prompt nothing measures.
    labels = " ".join(budget.CRON_REQUESTS)
    for job in ("triage", "interpret", "distill"):
        assert job in labels, job


def test_the_full_text_request_fits_on_the_model_the_job_calls():
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    # This test asserted the opposite on 2026-09-26, and said so: "the full-text
    # path fits now; update this test and opex.md". It fits now. The 2026-09-26
    # arithmetic (miss by 109) was itself wrong — the guard was sizing a paper
    # with prose filler, INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper —
    # and the real miss at FULLTEXT_CHARS of 24,000 was about 1,900 tokens.
    #
    # What closed it: FULLTEXT_CHARS 24,000 -> 12,000, a declared
    # MAX_COMPLETION_TOKENS, and a measured density. The degradation to
    # abstract[:6000] stays in the code as an error path and is no longer the
    # common one.
    # Rewritten 2026-09-30. This asserted `cron_degradations() == []`, which
    # was the right assertion while every model on distill's list could take a
    # 12,000-character paper. At 250,000 the Groq fallbacks cannot, and saying
    # so is the point of that function rather than a regression: what they
    # degrade to is the abstract, which is the documented fallback.
    #
    # The invariant that survives is the one that actually protected the
    # product: the model the job CALLS must not degrade. A degradation there is
    # "read in full" quietly becoming "read the abstract", which is the owner's
    # finding of 2026-09-25.
    head = budget.distill_models()[0]
    degraded = [note for note in budget.cron_degradations() if head in note]
    assert degraded == [], (
        "distill degrades on the model it actually calls, so the job is back "
        "to writing claims from abstracts while reporting success. Run "
        "`python3 tools/fulltext_density.py` and lower FULLTEXT_CHARS.\n"
        + "\n".join(degraded))
    assert [p for p in budget.check_cron_requests() if "distill" in p] == []


def test_the_guard_sizes_a_paper_as_a_paper_and_not_as_prose():
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    # The bug this file's neighbour exists to prevent, stated as arithmetic.
    # Prose filler runs 6.17 chars/token and a real paper runs 3.35, so sizing
    # distill's payload with `_filler` understates it by about 45%, which is
    # how a request that missed by 1,900 tokens was reported as missing by 109.
    spec = budget.CRON_REQUESTS["distill (pipeline/distill.py)"]
    chars = budget.request_payload_chars(spec)
    assert spec["chars_per_token"] == budget.FULLTEXT_CHARS_PER_TOKEN

    as_paper = budget.count_tokens(budget.request_text(spec, chars))
    as_prose = budget.count_tokens(budget._filler(chars))
    assert as_paper > as_prose * 1.4, (
        f"{chars} characters sized as a paper is {as_paper} tokens and as prose "
        f"{as_prose}; if these are close, the density override stopped applying")


def test_the_measured_density_matches_the_committed_receipt():
    # The constant may not drift away from the measurement that justifies it.
    # tools/fulltext_density.py rewrites this receipt against live arXiv; CI
    # reads the receipt because CI does not get to depend on arxiv.org.
    receipt = json.loads((ROOT / "docs" / "evals"
                          / "2026-09-30-fulltext-token-density.json").read_text())
    assert budget.FULLTEXT_CHARS_PER_TOKEN <= receipt["worst_chars_per_token"], (
        "the guard assumes a paper is looser than the worst paper measured")
    assert receipt["window_chars"] == budget.request_payload_chars(
        budget.CRON_REQUESTS["distill (pipeline/distill.py)"]), (
        "the receipt measured a different window than the job sends, which is "
        "the mistake that made the first corrected constant wrong too")
    assert receipt["all_fit"], "a measured paper did not fit at this window"


def _oversize_distill(monkeypatch, payload_chars, degrades_to_chars):
    """Distill's spec with the two request sizes forced, for the paths that no
    longer occur in production now that the real request fits."""
    spec = dict(budget.CRON_REQUESTS["distill (pipeline/distill.py)"])
    spec["payload_chars"] = payload_chars
    spec["degrades_to_chars"] = degrades_to_chars
    monkeypatch.setitem(budget.CRON_REQUESTS, "distill (pipeline/distill.py)", spec)


def test_a_request_that_no_longer_fits_is_a_degradation_and_not_a_failure(monkeypatch):
    # This was distill's real state until 2026-09-27 and it is the state the
    # job returns to the moment the prompt grows or a limit moves, so it keeps
    # its test even though production no longer reaches it.
    _oversize_distill(monkeypatch, 400_000, 6_000)
    notes = [n for n in budget.cron_degradations() if "distill" in n]
    assert notes, "a big request that does not fit has to be reported"
    assert "cannot take a full paper" in notes[0]
    assert "read from its abstract instead of in full" in notes[0]
    assert [p for p in budget.check_cron_requests() if "distill" in p] == [], \
        "a job with a working fallback degrades; it does not fail the gate"


def test_a_job_with_nowhere_left_to_go_is_still_a_failure(monkeypatch):
    # The degradation path must not become a way for any request to pass. If the
    # smaller retry does not fit either, the job cannot write a claim at all.
    _oversize_distill(monkeypatch, 400_000, 400_000)
    problems = [p for p in budget.check_cron_requests() if "distill" in p]
    assert problems, "a retry that does not fit either has to fail the gate"
    assert budget.cron_degradations()[0].endswith(
        "does NOT fit either, so the run cannot write a claim at all.")


# ---------------- distill on Kimi (2026-09-30, owner's directive) ----------------

def test_the_reading_queue_and_the_threads_are_ordered_ahead_of_the_intake():
    """The owner's order of 2026-09-29, read out of the SQL that implements it.

    The reading queue is `first` in the merge, so it cannot be outranked. What
    this checks is the half that was missing: inside the intake, a standing
    thread sorts ahead of `deep_read`, which sorts ahead of recency. Triage had
    honoured the threads since 2026-09-26 and distill had not, which is a
    priority with a hole in it — a thread promoted in the morning could wait
    weeks behind the day's intake in the reading stage.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    order = source[source.index("order by case when title ilike any(%s)"):]
    order = order[:order.index("limit %s")]
    assert order.index("title ilike any") < order.index("deep_read"), (
        "a standing thread must sort ahead of triage's deep_read; the owner's "
        "instruction about a subject outranks triage's opinion about a paper")
    assert order.index("deep_read") < order.index("published_at"), (
        "deep_read must still break the tie inside a thread")


def test_both_jobs_read_the_same_thread_list():
    """One list, or the threads triage promotes are not the threads distill reads.

    It was a constant in pipeline/triage.py until 2026-09-30. Two copies of a
    list like this drift in silence: nothing prints a disagreement, and the
    symptom is a thread that looks prioritised at one stage and is not at the
    next.
    """
    import priority
    import triage
    assert triage.PRIORITY_TERMS is priority.PRIORITY_TERMS
    assert triage.PRIORITY_PATTERNS == priority.PRIORITY_PATTERNS
    for job in ("pipeline/triage.py", "pipeline/distill.py"):
        source = (ROOT / job).read_text()
        assert '.add_local_file("pipeline/priority.py"' in source, (
            f"{job} uses the shared list and does not carry it into its image, "
            "so the deployed job will fail at import")


def test_every_ceiling_distill_can_stop_on_names_itself():
    """Three ceilings, three different fixes, so three different messages.

    Money, the account's daily token allowance, and the paper count each stop
    the run, and they want different responses: raise the cap, raise the
    Moonshot tier, raise MAX_PAPERS_PER_RUN. A single "stopped" line would hide
    which, and the wrong fix for a token-allowance stop is more money.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    body = source[source.index("def distill("):]
    assert 'stopped = f"the ${cap_usd:.2f} spend cap"' in body
    assert 'stopped = f"the {TOKENS_PER_RUN:,}-token daily share"' in body
    assert 'print(f"stopped on: {stopped}")' in body


def test_the_three_ceilings_are_checked_before_the_call_not_after():
    """A drain loop that checks afterwards always overshoots by one call.

    On a 262,144-token model one call is not a rounding error: a single paper
    is about 40,000 tokens and $0.04. `llm.Cap.allows()` exists for this and
    the token check has to sit beside it.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    body = source[source.index("for pid, title, abstract, decision, source in papers:"):]
    first_call = body.index("out, answered_by = extract_claims(")
    assert body.index("if not cap.allows():") < first_call
    assert body.index("if drawn >= TOKENS_PER_RUN:") < first_call


def test_the_daily_token_allowance_is_a_guard_and_not_a_comment():
    """The ceiling nobody was watching until a request got big.

    Busting a per-request limit is a 413 on one call. Busting the account's
    daily allowance is every Kimi call in the org failing for the rest of the
    UTC day, press included, so it is the more dangerous of the two and it had
    no check at all until distill started sending whole papers.
    """
    assert budget.check_kimi_tpd() == [], budget.check_kimi_tpd()
    total, lines = budget.kimi_daily_draw()
    allowance = budget.MODELS[budget.PRIMARY_MODEL]["tpd"]
    assert total <= allowance * (1 - budget.MARGIN), (
        f"{total:,} tokens a day against a {allowance:,} allowance")
    for label in budget.cron_model_lists():
        assert label in budget.KIMI_DAILY_DRAW, (
            f"{label} calls Kimi on a schedule and draws from the account's "
            "day, and nothing counts it")


def test_distills_cap_buys_more_than_one_paper_at_the_worst_case_price():
    """A cap smaller than one call is a job that never runs.

    Triage has the same test and distill needs it more: one paper at the
    ceiling is $0.10, which is sixteen times a triage batch, so the margin
    between a working cap and a useless one is much thinner here.
    """
    job = distill
    ceiling = budget.cost_usd(
        int(job.FULLTEXT_CHARS / budget.FULLTEXT_CHARS_PER_TOKEN) + 990,
        job.MAX_COMPLETION_TOKENS, job.MODELS[0])
    assert ceiling > 0
    assert job.CAP_USD / ceiling >= 5, (
        f"${job.CAP_USD:.2f} buys {job.CAP_USD / ceiling:.1f} papers at the "
        f"worst-case price of ${ceiling:.4f}. A cap that buys almost nothing "
        "is a job that reports success after one paper.")


def test_the_density_constant_was_measured_at_the_window_the_job_sends():
    """A density is only valid for the window it was measured at.

    The same fourteen papers run 3.35 chars/token over their first 12,000
    characters and 2.53 over their whole bodies, because a paper opens with a
    title block and an abstract and only later reaches its equations. Widening
    FULLTEXT_CHARS without re-measuring would have under-sized every request by
    about a third.
    """
    job = distill
    receipt = json.loads((ROOT / "docs" / "evals"
                          / "2026-09-30-fulltext-token-density.json").read_text())
    assert receipt["window_chars"] == job.FULLTEXT_CHARS
    assert receipt["model"] == job.MODELS[0]
    assert budget.FULLTEXT_CHARS_PER_TOKEN <= receipt["worst_chars_per_token"]


def test_the_token_counter_survives_a_paper_that_prints_a_special_token():
    """The crash that a small window hid for the life of the guard.

    tiktoken raises by default on text containing `<|endoftext|>`, and a
    cleaned arXiv paper contains it whenever it quotes a prompt template or
    discusses tokenizers. At 12,000 characters the guard never reached one; the
    first measurement at 250,000 hit it on the first paper. A token counter
    that throws is a guard that fails closed on exactly the papers the corpus
    most wants to read.
    """
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    assert budget.count_tokens("before <|endoftext|> after") > 0
    assert budget.count_tokens("<|im_start|><|endofprompt|>") > 0


# ================ the day's run, driven end to end (2026-09-30) ================
#
# Every distill test above and in tests/test_distill_gates.py checks a gate, a
# constant or a query. None of them runs the loop, and on 2026-09-30 the loop
# is the part that changed most: it moved to the shared client, it gained three
# ceilings that each have to stop it cleanly, it lost the per-run fetch budget,
# and it has to tell the truth about which papers arrived whole.
#
# This section is what the engineer seat could run in place of a smoke run. A
# real smoke run is `modal run pipeline/distill.py --max-papers 1 --cap-usd
# 0.15` and it needs the Moonshot key, which lives in Modal and which no seat
# sandbox has. So the provider and the database are fakes here and everything
# between them is the real code: the real ordering, the real cap accounting out
# of a real usage block, the real fulltext_chars write, the real stop
# conditions. What it cannot prove is that Moonshot answers a
# 250,000-character paper well, which is gate 3's question and the chair's to
# ask.
#
# It lives in this file rather than its own because checks.yml names test files
# one by one and no seat can push a workflow. A test CI does not run is
# enforced at the reliability of somebody running it locally, which is L-A22,
# and this section is too load-bearing for that.

class Row(list):
    """psycopg hands back tuples; the fake cursor hands back these."""


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConn:
    """Answers the handful of queries the run makes, and records every write.

    Deliberately literal rather than clever: it matches on a distinctive
    fragment of each statement, so a query that changes shape fails here loudly
    instead of silently answering something else.
    """

    def __init__(self, papers, queue_depth=0):
        self.papers = papers
        self.queue_depth = queue_depth
        self.inserts = []
        self.fulltext_writes = {}
        self.institution_writes = {}
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append(" ".join(sql.split()))
        low = sql.lower()
        if "information_schema.columns" in low:
            return FakeCursor([(1,)])          # every optional column exists
        if "from distill_queue" in low and "count(*)" in low:
            return FakeCursor([(self.queue_depth,)])
        if "from distill_queue" in low:
            return FakeCursor(self.papers)
        if low.strip().startswith("insert into claims"):
            self.inserts.append((sql, params))
            return FakeCursor([])
        if "fulltext_chars = %s" in low:
            self.fulltext_writes[params[1]] = params[0]
            return FakeCursor([])
        if "set institutions = %s" in low:
            self.institution_writes[params[1]] = params[0]
            return FakeCursor([])
        if "where embedding is null" in low:
            return FakeCursor([])              # nothing left to embed
        return FakeCursor([])

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def paper_reply(status=200, claims=None, prompt_tokens=40_000,
                institutions=None):
    body = {
        "choices": [{"message": {"content": json.dumps(
            {"claims": claims or [], "institutions": institutions or []})},
            "finish_reason": "stop"}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": 900},
    }

    class R:
        status_code = status
        text = ""
        headers: dict = {}

        def json(self):
            return body

        def raise_for_status(self):
            pass

    return R()


CLAIM = {
    "claim": "Two-stage distillation raises pairwise win rate to 71.3%.",
    "evidence": "Held-out split, three annotators, Krippendorff alpha 0.81.",
    "procedure": "1. SFT on 12,400 demonstrations. 2. Distil with KL 0.02.",
    "topics": ["reasoning"],
}

PAPERS = [
    ("arxiv:1", "Chain of thought prompting at scale", "an abstract",
     "deep_read", "arxiv"),
    ("arxiv:2", "A sandbox for untrusted agent tools", "an abstract",
     "distill", "arxiv"),
    ("arxiv:3", "A fast Fourier transform variant", "an abstract",
     "distill", "arxiv"),
]


@pytest.fixture
def loop_env(monkeypatch, no_sleep):
    """Everything the loop reaches for, faked at its own edge."""
    monkeypatch.setenv("MOONSHOT_API_KEY", "moonshot-key")
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")
    monkeypatch.setenv("DATABASE_URL", "postgres://fake")
    monkeypatch.setattr(distill, "load_prompt",
                        lambda kind="paper": ("a prompt", f"sha-{kind}"))
    monkeypatch.setattr(distill, "reading_queue", lambda: _NoQueue())
    monkeypatch.setattr(distill, "read_paper", lambda: _NoFetch())
    monkeypatch.setattr(httpx, "get", lambda *a, **k: response(
        200, claims=[]) if False else _catalog())
    # setitem rather than assignment, so the fakes are removed when the test
    # ends. A `psycopg` left in sys.modules would follow the suite into every
    # file collected after this one.
    monkeypatch.setitem(sys.modules, "sentence_transformers",
                        _fake_sentence_transformers())
    monkeypatch.setitem(sys.modules, "psycopg", _fake_psycopg())
    return None


def _catalog():
    class R:
        status_code = 200
        text = ""
        headers: dict = {}

        def json(self):
            return {"data": [{"id": m} for m in distill.MODELS]}

    return R()


class _NoQueue:
    QUEUE_PATH = "docs/research/reading-queue.md"
    MAX_PER_RUN = 6

    def read_file(self, path):
        return None

    def pending(self, text, limit=None):
        return []

    def resolve(self, conn, requested, fetch_metadata=None):
        return []

    def merge(self, first, intake, max_papers):
        return (list(first) + list(intake))[:max_papers]


class _NoFetch:
    """arXiv serves no HTML, so the run takes the documented fallback."""

    def fetch_paper(self, pid, max_chars=None):
        return None

    def fetch_metadata(self, pid):
        return None


class _WholePaper(_NoFetch):
    """A paper with full text and no parseable header.

    `html` is a page rather than None, because that is the ordinary case: arXiv
    renders the paper, and whether its author block carries affiliations is a
    separate question from whether the page exists. A run against this reader
    therefore takes the model's answer for `institutions`, which is the
    fallback and not the source.
    """

    def __init__(self, length, header=""):
        self.length = length
        self.header = header

    def fetch_paper(self, pid, max_chars=None):
        body = "x" * self.length
        return {"text": body[:max_chars] if max_chars else body,
                "html": f'<html><div class="ltx_authors">{self.header}'
                        f'</div>{body[:200]}</html>'}


def _fake_sentence_transformers():
    import types
    mod = types.ModuleType("sentence_transformers")
    mod.SentenceTransformer = lambda name: None
    return mod


def _fake_psycopg():
    import types
    mod = types.ModuleType("psycopg")
    mod.connect = lambda url: CONN["conn"]
    return mod


CONN: dict = {}


def drive(monkeypatch, papers, responses, reader=None, **kwargs):
    conn = FakeConn(papers, queue_depth=kwargs.pop("queue_depth", 0))
    CONN["conn"] = conn
    if reader is not None:
        monkeypatch.setattr(distill, "read_paper", lambda: reader)
    queue = list(responses)
    monkeypatch.setattr(httpx, "post",
                        lambda *a, **k: queue.pop(0) if len(queue) > 1
                        else queue[0])
    # The Modal stub gives `hf_cache` as None, and the embedding sweep only
    # touches it when there is something to embed, which the fake database
    # says there is not.
    distill.distill(**kwargs)
    return conn


# ---------------- the loop writes what it read ----------------

def test_a_complete_paper_is_recorded_as_the_number_of_characters_read(
        loop_env, monkeypatch, capsys):
    """`papers.fulltext_chars` is what the masthead's number is counted from.

    So it has to be the real length, and a paper cut at the window has to be
    distinguishable from one that arrived whole. The run prints both counts and
    the column carries the per-paper number behind them.
    """
    conn = drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])],
                 reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert conn.fulltext_writes["arxiv:1"] == 40_000
    assert "read 1 of 1 papers from their full text, 1 of those complete" in out


def test_a_paper_longer_than_the_window_is_read_but_not_counted_complete(
        loop_env, monkeypatch, capsys):
    conn = drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])],
                 reader=_WholePaper(distill.FULLTEXT_CHARS + 50_000))
    out = capsys.readouterr().out
    assert conn.fulltext_writes["arxiv:1"] == distill.FULLTEXT_CHARS
    assert "0 of those complete" in out
    assert f"cut at {distill.FULLTEXT_CHARS}" in out


def test_a_paper_with_no_html_falls_back_to_the_abstract_and_says_null(
        loop_env, monkeypatch, capsys):
    """The documented fallback, and the honest marker that goes with it.

    A stat the weekly issue prints cannot be generous about what was read, so
    an abstract-only paper writes NULL rather than the abstract's length.
    """
    conn = drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])])
    out = capsys.readouterr().out
    assert conn.fulltext_writes["arxiv:1"] is None
    assert "1 from the abstract alone" in out


# ---------------- the three ceilings ----------------

def test_the_spend_cap_stops_the_run_and_names_itself(loop_env, monkeypatch, capsys):
    """Less than one paper's allowance, three papers queued.

    A paper here bills $0.0416, so a $0.03 cap is spent by the first one and
    the second is refused before it is sent. That is the shape `llm.Cap` is
    built for: the check is BEFORE the call, so a run stops at its cap rather
    than one call past it, and on a 262,144-token model one call past it is
    four cents rather than a rounding error.
    """
    drive(monkeypatch, PAPERS, [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000), cap_usd=0.03)
    out = capsys.readouterr().out
    assert "stopped on: the $0.03 spend cap" in out
    assert out.count("claims (paper)") == 1, (
        "the cap is checked before the call, so the run stops AT it rather "
        "than one paper past it")


def test_the_daily_token_share_stops_the_run_and_names_itself(
        loop_env, monkeypatch, capsys):
    """A different ceiling with a different fix, so a different message.

    Running out of the account's day is not a cost problem, and answering it
    with more money buys nothing. The line has to say which one it was.
    """
    monkeypatch.setattr(distill, "TOKENS_PER_RUN", 50_000)
    drive(monkeypatch, PAPERS, [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert "stopped on: the 50,000-token daily share" in out
    assert "the next run resumes" in out


def test_the_paper_count_is_what_normally_stops_the_run(loop_env, monkeypatch, capsys):
    drive(monkeypatch, PAPERS, [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert "stopped on: the queue ran out" in out
    assert out.count("claims (paper)") == 3


# ---------------- what the run tells the reader ----------------

def test_the_run_prints_the_measured_cost_per_paper(loop_env, monkeypatch, capsys):
    """The owner asked for this number by name, so the run prints the realised
    version of it beside the projection the preflight printed."""
    drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert "cost per paper this run: $" in out
    assert "spend: $" in out


def test_the_run_says_which_model_answered(loop_env, monkeypatch, capsys):
    drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert f"answered by: {distill.MODELS[0]} x1" in out


def test_a_run_answered_only_by_a_fallback_warns_that_it_read_abstracts(
        loop_env, monkeypatch, capsys):
    """The quiet failure this whole change exists to end.

    A Groq fallback answers, the run succeeds, claims are written, and every
    one of them came from an abstract. That is the owner's finding of
    2026-09-25 in one run, so the log has to name it rather than report a
    normal day.
    """
    drive(monkeypatch, PAPERS[:1],
          [paper_reply(404), paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert f"NOTE: {distill.MODEL} answered nothing this run" in out
    assert "came from abstracts" in out


def test_the_run_forecasts_the_remaining_queue(loop_env, monkeypatch, capsys):
    drive(monkeypatch, PAPERS[:1], [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000), queue_depth=400)
    out = capsys.readouterr().out
    assert "400 papers still queued" in out
    assert "OVER A WEEK" in out, (
        "a queue that cannot clear in a week is the condition the owner's "
        "directive named, so the run has to say so rather than print a number")


def test_the_daily_draw_reads_the_paper_count_out_of_the_job():
    """The number that will move is the number the guard reads, not a copy.

    Distill dominates this table by an order of magnitude, so raising
    MAX_PAPERS_PER_RUN without the guard following would be a job quietly
    drawing more of the account's day than anything checks. That is the same
    argument `cron_caps` makes for spend caps, applied to the other ceiling.
    """
    spec, per_call, _ = budget.KIMI_DAILY_DRAW["distill (pipeline/distill.py)"]
    assert budget._calls(spec) == distill.MAX_PAPERS_PER_RUN
    # And the arithmetic downstream of it actually uses that number.
    total, _ = budget.kimi_daily_draw()
    assert distill.MAX_PAPERS_PER_RUN * per_call <= total


# ---------------- pacing, the limit that actually binds (2026-10-11) ----------

def test_pace_reads_the_limit_that_binds_on_each_provider():
    """Requests a minute on Moonshot, tokens a minute on the free tier.

    `llm.pace` read RPM alone until 2026-10-11, which is right for exactly one
    of the two providers in `budget.MODELS`. Moonshot gives this account 3 RPM
    against a 500,000-token minute, so one call every 20 seconds and the token
    budget never binds. Every Groq free-tier model gives 30 RPM against 8,000
    TPM, so a call over 266 tokens runs out of minute long before it runs out
    of requests, and a drain paced from RPM asks for fifteen times what the
    provider publishes.
    """
    paper = budget.KIMI_DAILY_DRAW["distill (pipeline/distill.py)"][1]
    batch = budget.KIMI_DAILY_DRAW["triage (pipeline/triage.py)"][1]

    # The primary is unchanged, and that is half of what makes this safe: the
    # fix must not slow the drain on the provider that works.
    assert llm.pace(budget.PRIMARY_MODEL, paper) == pytest.approx(20.0)
    assert llm.pace(budget.PRIMARY_MODEL) == pytest.approx(20.0)

    for model, limits in budget.MODELS.items():
        if limits["provider"] == budget.MODELS[budget.PRIMARY_MODEL]["provider"]:
            continue
        pause = llm.pace(model, batch)
        assert pause * limits["tpm"] >= batch * 60.0 - 1e-6, (
            f"{model} publishes {limits['tpm']:,} tokens a minute and a "
            f"{batch:,}-token call every {pause:.1f}s asks for "
            f"{batch * 60.0 / pause:,.0f}")
        # And the defect itself, stated as the number it produced: RPM alone
        # on this model is 2 seconds, which is the pause that stopped the
        # corpus for four days.
        assert pause > 60.0 / limits["rpm"]


def test_every_paced_caller_tells_pace_how_big_its_call_was():
    """A one-argument pace() is a job that paces from the wrong limit.

    The source is the only place to ask this. The pause is taken inside a Modal
    container, after a walk whose landing model nothing outside the run can
    predict, so a test that waits for production to disagree is a test that
    costs four days of claims.
    """
    assert budget.check_fallback_pacing() == [], budget.check_fallback_pacing()
    for path in budget.PACED_CALLERS:
        source = (ROOT / path).read_text()
        assert "cap.last_tokens" in source, (
            f"{path} is paced but passes no provider-counted call size")


def test_the_cap_that_bounds_a_run_cannot_bind_on_a_free_tier():
    """So the fallback's day is sized from the call ceiling, not the spend cap.

    Every Groq model in `budget.MODELS` is priced at $0.00 a million, which is
    correct and makes `CAP_USD` unable to stop anything. What is left is the
    job's own per-run call ceiling, and it is a bigger number than the cap
    allows at Moonshot's prices: triage's day is 70 calls when it is paying and
    90 when it is not.
    """
    label = "triage (pipeline/triage.py)"
    priced = budget.KIMI_DAILY_DRAW[label][0]
    assert budget.fallback_calls(label) == triage.MAX_CALLS_PER_RUN
    assert budget.fallback_calls(label) > priced, (
        "the free tier's call budget must be the one that is larger, or this "
        "whole guard is measuring the wrong day")
    for model, limits in budget.MODELS.items():
        if limits["provider"] == "groq":
            assert limits["price_in"] == 0.0 and limits["price_out"] == 0.0


def test_the_fallback_day_is_sized_at_the_request_the_job_can_actually_send():
    """Distill's fallback day is abstracts, because no free model takes a paper.

    A day sized at 40,259 tokens a paper would be a day distill cannot have:
    the full-text request is 102,272 tokens against 6,800 usable, so what
    actually goes to the free tier is `abstract[:6000]`. Sizing the degraded
    day at the primary's request would over-count it by an order of magnitude
    and point the fix at the wrong job.
    """
    label = "distill (pipeline/distill.py)"
    measured = budget.KIMI_DAILY_DRAW[label][1]
    size, basis = budget.fallback_call_tokens(label, "openai/gpt-oss-120b",
                                              measured)
    assert "counted" in basis and size < measured / 5

    # Triage's request fits the free tier untouched, so its measured number is
    # the right one and the basis says so.
    size, basis = budget.fallback_call_tokens("triage (pipeline/triage.py)",
                                              "openai/gpt-oss-120b",
                                              budget.KIMI_DAILY_DRAW[
                                                  "triage (pipeline/triage.py)"][1])
    assert basis == "measured"

    per_model, lines = budget.fallback_daily_draw()
    assert per_model, "no corpus job lands anywhere when the primary is absent"
    assert all(budget.MODELS[m]["provider"] != "moonshot" for m in per_model)


def test_a_paced_fallback_drain_still_finishes_inside_its_own_timeout():
    """The pause that respects the provider has to leave a drain that drains.

    A correct pause that does not fit the Modal timeout is a job that is killed
    mid-run instead of rate-limited mid-run, which is the same outage wearing a
    different hat. Distill's window is 90 minutes and this is the arithmetic
    that says 20 abstracts fit inside it.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    # The drain's own decorator, not whichever @app.function comes first in the
    # file: distill.py declares several and they do not share a timeout.
    decorator = source[:source.index("def distill(max_papers")]
    timeout = int(re.findall(r"^\s+timeout=(\d+),", decorator, re.M)[-1])
    label = "distill (pipeline/distill.py)"
    size, _ = budget.fallback_call_tokens(
        label, "openai/gpt-oss-120b", budget.KIMI_DAILY_DRAW[label][1])
    # Two calls a paper on the fallback: the full text is refused before it is
    # paced, and the abstract is the one that answers and is paced.
    spent = distill.MAX_PAPERS_PER_RUN * llm.pace("openai/gpt-oss-120b", size)
    assert spent < timeout * 0.75, (
        f"{distill.MAX_PAPERS_PER_RUN} papers at "
        f"{llm.pace('openai/gpt-oss-120b', size):.0f}s a paper is {spent:.0f}s "
        f"of a {timeout}s window, before a single HTTP round trip")


# ---------------- the day the primary is absent has a share per stage ----------------

def test_every_corpus_job_publishes_a_fallback_share_and_the_shares_fit():
    """The ceiling that was missing for the four days `claims` stood still.

    Every job had a bound for the day it is paying: a spend cap, a call count,
    and for distill a token share of Moonshot's allowance. None of the three
    binds on the free tier. The cap cannot, because every Groq model in
    `budget.MODELS` is priced at $0.00 a million; the call counts were sized
    against a paid minute and together ask 642,650 tokens of a 200,000-token
    day. So the stage that runs last in `llm.KIMI_WINDOWS` met a day two other
    stages had already spent, which is a 429 on every call and no claims.
    """
    assert budget.check_fallback_shares() == [], budget.check_fallback_shares()
    for job, label in ((triage, "triage (pipeline/triage.py)"),
                       (interpret, "interpret (pipeline/interpret.py)"),
                       (distill, "distill (pipeline/distill.py)")):
        share, _ = budget.fallback_share(label)
        assert budget.fallback_ceiling(label) == job.FALLBACK_TOKENS_PER_RUN, (
            f"{label}'s guard and its job disagree about the ceiling the job "
            "will actually apply")
        assert job.FALLBACK_TOKENS_PER_RUN <= share


def test_the_fallback_share_is_derived_from_the_published_day_not_chosen(
        monkeypatch):
    """A share somebody picked is a number that stops being true quietly.

    The provider publishes the day, the request guard already holds back
    `MARGIN` of it, and the jobs that land on that model split what is left
    evenly. Nothing here is an opinion, so a tier change or a fourth stage
    moves every share with no constant in this file to edit.
    """
    label = "distill (pipeline/distill.py)"
    landing = budget.fallback_landing(label)
    allowance = budget.MODELS[landing]["tpd"]
    sharers = sum(1 for other in budget.KIMI_DAILY_DRAW
                  if budget.fallback_landing(other) == landing)
    share, basis = budget.fallback_share(label)
    assert share == int(allowance * (1 - budget.MARGIN)) // sharers
    assert f"{allowance:,}" in basis and f"{sharers} ways" in basis

    # And it moves with the published number rather than being pinned to it.
    monkeypatch.setitem(budget.MODELS[landing], "tpd", allowance * 2)
    doubled, _ = budget.fallback_share(label)
    assert doubled == int(allowance * 2 * (1 - budget.MARGIN)) // sharers
    assert doubled > share


def test_the_shares_together_fit_the_free_tier_s_day():
    """The acceptance number, as the guard now reads it.

    Before this change the corpus asked 642,650 tokens of a day that allows
    200,000. `check_fallback_tpd` printed that as a note and named lowering a
    per-run ceiling as the lever; this is the lever, pulled.
    """
    per_model, _ = budget.fallback_daily_draw()
    for model, draw in per_model.items():
        allowance = budget.MODELS[model]["tpd"]
        assert draw <= int(allowance * (1 - budget.MARGIN)), (
            f"{draw:,} tokens asked of {model}'s {allowance:,}-token day")
    assert budget.check_fallback_tpd() == [], budget.check_fallback_tpd()


def test_on_fallback_asks_about_the_provider_and_not_the_model_list():
    """Which account paid, which is the question the walk never answered.

    A job's own list is no help: its head and its tail can be the same
    provider or three different ones, and what decides which day a call spends
    is the provider behind the id that answered.
    """
    assert llm.on_fallback(budget.PRIMARY_MODEL) is False
    primary = budget.MODELS[budget.PRIMARY_MODEL]["provider"]
    for model, limits in budget.MODELS.items():
        assert llm.on_fallback(model) is (limits["provider"] != primary)
    # An id the table does not know keeps the primary's larger ceiling: a run
    # should not throttle itself to a fifth of its day on a guess.
    assert llm.on_fallback("a-model-nobody-added-to-the-table") is False


def test_the_fallback_share_stops_the_run_and_names_itself(
        loop_env, monkeypatch, capsys):
    """A fourth ceiling, a fourth message, because it wants a fourth fix.

    Money, Moonshot's day, the paper count and now the free tier's day. The
    right answer to this one is neither more money nor a higher tier: it is
    that the corpus is running degraded and every stage gets a third of a day
    a fifth the size.
    """
    monkeypatch.setattr(distill, "MODELS", ["openai/gpt-oss-120b"])
    monkeypatch.setattr(distill, "FALLBACK_TOKENS_PER_RUN", 30_000)
    drive(monkeypatch, PAPERS, [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert "stopped on: the 30,000-token fallback share" in out
    assert "A thin day of claims rather than none" in out
    assert out.count("claims (paper)") == 1, (
        "the share is checked before the call, so the run stops AT it rather "
        "than one paper past it")


def test_the_fallback_share_does_not_slow_the_run_the_primary_answers(
        loop_env, monkeypatch, capsys):
    """Half of what makes this safe: the fix must not touch the working day.

    A ceiling on the free tier's day that also bound a Kimi run would make
    every normal day 94% smaller, which is a worse outage than the one it is
    fixing. Only tokens drawn off the primary's provider count against it, so
    a share of one token stops nothing while Moonshot is answering.
    """
    monkeypatch.setattr(distill, "FALLBACK_TOKENS_PER_RUN", 1)
    drive(monkeypatch, PAPERS, [paper_reply(claims=[CLAIM])],
          reader=_WholePaper(40_000))
    out = capsys.readouterr().out
    assert "stopped on: the queue ran out" in out
    assert out.count("claims (paper)") == len(PAPERS)


def test_the_share_is_checked_before_the_call_in_every_corpus_job():
    """A drain that checks afterwards overshoots, and overshooting is the bug.

    One call past the share is one call of the next stage's day, and the next
    stage is the one that was writing nothing. Asserted in the source of all
    three, because two of them have no token ceiling of any kind to sit beside
    and nothing else would catch a check added after the call.
    """
    for path, loop, call in (
            ("pipeline/distill.py",
             "for pid, title, abstract, decision, source in papers:",
             "out, answered_by = extract_claims("),
            ("pipeline/triage.py", "for chunk in plan:",
             "out, model = client.ask_json("),
            ("pipeline/interpret.py",
             "for claim_id, claim_text, paper_id, embedding in queue:",
             "out, model = client.ask_json(")):
        body = (ROOT / path).read_text()
        body = body[body.index(loop):]
        assert body.index("if fallback_drawn >= FALLBACK_TOKENS_PER_RUN:") \
            < body.index(call), f"{path} checks its share after it has spent it"
        assert "if client.on_fallback(" in body, (
            f"{path} never adds to fallback_drawn, so its share can never bind")


# ---------------- gate 3 on the day the head is what is broken ----------------
#
# INC-2026-10-12-the-deploy-ladder-refuses-the-fix-for-the-outage-it-is-in.
# Two merged pull requests sized the fallback's minute and the fallback's day,
# both of them inert until a deploy, and the third rung of every corpus deploy
# chain ends by asking whether the head of the model list answered. The primary
# was not answering. That is what the hatch below is for, and these are the
# tests that hold its two halves: it refuses by default, and when it forgives it
# says so in the receipt.


def test_a_fallback_receipt_is_refused_by_default():
    """The ordinary day, unchanged. A receipt from a fallback is not a receipt."""
    with pytest.raises(llm.NoModelAnswered) as caught:
        llm.head_receipt("openai/gpt-oss-120b", ["kimi-k2.6", "openai/gpt-oss-120b"],
                         False, gate="pipeline/triage.py::rehearse")
    said = str(caught.value)
    assert "kimi-k2.6" in said and "openai/gpt-oss-120b" in said
    # The refusal carries the way out of it. A gate that refuses without naming
    # its own hatch is a gate the operator routes around instead of using.
    assert "modal run pipeline/triage.py::rehearse --allow-fallback" in said


def test_the_head_answering_is_silent():
    """Nothing to forgive means nothing printed. The receipt stays clean."""
    assert llm.head_receipt("kimi-k2.6", ["kimi-k2.6", "openai/gpt-oss-120b"],
                            False, gate="x") == ""
    assert llm.head_receipt("kimi-k2.6", ["kimi-k2.6"], True, gate="x") == ""


def test_the_hatch_says_what_it_forgave():
    """Forgiving quietly is how a degraded deploy becomes the new normal.

    The returned line has to name both models and has to say that the head is
    still broken after the deploy, because that is the fact the next person to
    read the receipt needs and the deploy itself will not tell them.
    """
    line = llm.head_receipt("openai/gpt-oss-120b",
                            ["kimi-k2.6", "openai/gpt-oss-120b"], True,
                            gate="pipeline/triage.py::rehearse")
    assert "FORGIVEN" in line
    assert "kimi-k2.6" in line and "openai/gpt-oss-120b" in line
    assert "still broken" in line


def test_every_corpus_rehearsal_has_a_hatch_and_defaults_to_refusing():
    """The three corpus gates, read out of their own source.

    Distill's hatch is `--allow-abstract-only` and predates this one by two
    weeks; it is the shape the other two were modelled on, so it counts here
    rather than being special-cased away. What every one of them must have is a
    parameter that defaults to False, because a hatch that is open by default is
    not a hatch, it is the removal of the gate.
    """
    for path, flag in (("pipeline/triage.py", "allow_fallback"),
                       ("pipeline/interpret.py", "allow_fallback"),
                       ("pipeline/distill.py", "allow_abstract_only")):
        source = (ROOT / path).read_text()
        assert f"def rehearse({flag}: bool = False)" in source, (
            f"{path}'s rehearsal has no {flag} hatch defaulting to False, so "
            "the day its model list's head is what is broken, the gate refuses "
            "to deploy the fix for it")


def test_the_corpus_rehearsals_forgive_only_the_head():
    """The hatch is not a `--force`.

    Triage's short-batch check and interpret's edge-set check are faults in the
    answer rather than in which account gave it, so both must still raise with
    the hatch open. Asserted in the source, because running either rehearsal
    needs a provider and a key.
    """
    for path, other in (("pipeline/triage.py",
                         "if len(good) != len(REHEARSAL_BATCH):"),
                        ("pipeline/interpret.py", "if not edges:"),
                        ("pipeline/interpret.py",
                         "if len(edges) == len(REHEARSAL_NEIGHBORS):")):
        source = (ROOT / path).read_text()
        body = source[source.index("def rehearse("):]
        assert other in body, f"{path} lost the check that is not about the head"
        # The hatch must reach head_receipt and nothing else: once in the
        # signature, once in the call. A third mention is the hatch leaking
        # into a check it was never meant to forgive.
        assert body.count("allow_fallback") == 2, (
            f"{path} mentions its hatch {body.count('allow_fallback')} times "
            "inside rehearse(), so it reaches something other than "
            "head_receipt")


# ---------------- the rehearsal sends the request the run sends ----------------
#
# A gate that exercises a smaller request than production exercises a request
# production never makes. It still catches a dead key, a missing model and a
# timeout, so it never looks broken; what it stops catching is everything that
# only appears at full size, which is the class of failure the gate is most
# needed for.
#
# This went unnoticed in two of the three corpus jobs at once. Interpret's
# shortlist was widened from five candidates to ten on 2026-10-25 and its
# fixture stayed at five, so from that day the gate in front of every interpret
# deploy sent half the user message the run sends, and the half it skipped was
# the half that had just grown. Triage's was worse and older: three papers
# against a BATCH of ten, with MAX_COMPLETION_TOKENS reserved for ten results,
# in front of a gate whose own failure message is about a model that answers for
# some of a batch and not the rest. Distill had it right from the start and is
# the reason this is a test rather than a rule: its rehearsal pads its body to
# exactly FULLTEXT_CHARS with a comment calling that "the request that must
# fit", so the correspondence is in the expression and cannot drift.
#
# The fix for the other two is the same shape, which is why one test holds all
# three: the fixture's length is checked against the constant the run reads, so
# the next person who widens a payload gets a red test instead of a quiet gate.


def test_each_rehearsal_sends_the_payload_size_its_run_sends():
    assert len(triage.REHEARSAL_BATCH) == triage.BATCH, (
        f"triage rehearses {len(triage.REHEARSAL_BATCH)} papers where the run "
        f"sends {triage.BATCH}, so the gate cannot meet the truncated-tail "
        "failure its own error message describes")
    assert len(interpret.REHEARSAL_NEIGHBORS) == interpret.NEIGHBORS, (
        f"interpret rehearses {len(interpret.REHEARSAL_NEIGHBORS)} candidates "
        f"where the run sends {interpret.NEIGHBORS}, so a model that handles "
        "the short list and degrades on the long one passes the gate")


def test_the_distill_rehearsal_sizes_its_body_from_the_constant_not_a_number():
    # Distill's payload is generated rather than written out, so the guard is
    # that the generator reads FULLTEXT_CHARS. Checked two ways: the expression
    # is in the source, and running it here produces exactly that many chars.
    source = (ROOT / "pipeline" / "distill.py").read_text()
    body_of_rehearse = source[source.index("def rehearse("):]
    assert "[:FULLTEXT_CHARS]" in body_of_rehearse, (
        "distill's rehearsal stopped sizing its payload from FULLTEXT_CHARS, "
        "so the request the gate sends is no longer the request that must fit")
    sample = distill.REHEARSAL_SAMPLE
    n = distill.FULLTEXT_CHARS
    assert len((sample * (n // len(sample) + 1))[:n]) == n


def test_the_widened_fixtures_still_fit_the_reservations_they_are_sent_under():
    """The payload grew; the reservation did not, and that is on purpose.

    Both reservations were already sized for the full batch. Triage's comment
    says "ten results of {i, decision, score, reasoning}" and interpret's says
    "up to ten relations with confidences", so widening the fixtures changed
    nothing about the request's shape, only about whether the gate ever sends
    it. If either constant is ever cut below what its fixture can produce, the
    rehearsal starts failing on truncation rather than on the provider, and the
    reader will blame the model. This is the test that says which it was.
    """
    # ~55 tokens a result, the figure triage's own comment is derived from.
    assert triage.MAX_COMPLETION_TOKENS >= 55 * len(triage.REHEARSAL_BATCH)
    # 299 tokens measured for ten relations, in interpret's comment.
    assert interpret.MAX_COMPLETION_TOKENS >= 30 * len(interpret.REHEARSAL_NEIGHBORS)


# ---------------- who answers "who did this work" ----------------
#
# `papers.institutions` was empty on 99.2% of rows, measured by the writer seat
# on 2026-09-19 and unchanged at the 2026-10-12 ceremony, on a path that was
# meant to fill it: distill fetched the paper's HTML, ran every tag out of it
# with `clean_html`, and then asked the model for "the author affiliations in
# the header" of a payload with no header left in it. These four cases are the
# order that fixes it, and the first one is the whole fix.

AFFILIATION = ('<span class="ltx_personname">A Person</span>'
               '<span class="ltx_role_affiliation">Google DeepMind</span>')


def test_the_paper_s_own_header_beats_the_model_s_answer(
        loop_env, monkeypatch, capsys):
    """Both sources answer, and the one printed in the paper wins.

    An affiliation has one correct answer and the paper prints it, so this is
    not a preference between two guesses: a parser cannot invent a lab and a
    model can. The model here returns a plausible wrong answer, which is the
    failure mode that matters, because a digest that says "a team at Oxford"
    about an OpenAI system card is a worse artifact than one that says nothing.
    """
    conn = drive(monkeypatch, PAPERS[:1],
                 [paper_reply(claims=[CLAIM], institutions=["Oxford"])],
                 reader=_WholePaper(40_000, header=AFFILIATION))
    assert conn.institution_writes == {"arxiv:1": ["Google DeepMind"]}
    assert "institutions (affiliation-spans): ['Google DeepMind']" \
        in capsys.readouterr().out


def test_the_model_answers_for_a_paper_whose_header_names_no_lab(
        loop_env, monkeypatch, capsys):
    """The fallback, which is the model, and the log says it was the fallback.

    Two patterns of three found nothing and the third is only tried on a header
    that names no person, so a paper with an author list and no affiliations
    reaches the model's answer. Keeping that answer is deliberate: it is the
    behaviour this job has always had, and the change is its rank.
    """
    conn = drive(monkeypatch, PAPERS[:1],
                 [paper_reply(claims=[CLAIM], institutions=["DeepMind"])],
                 reader=_WholePaper(40_000, header=AFFILIATION.split("<span c"
                                                                    "lass=\"ltx_role")[0]))
    assert conn.institution_writes == {"arxiv:1": ["DeepMind"]}
    out = capsys.readouterr().out
    assert "institutions (the model, nothing found nothing): ['DeepMind']" in out


def test_a_paper_arxiv_serves_no_html_for_reaches_the_model_too(
        loop_env, monkeypatch, capsys):
    """No page at all, which before roughly 2024 is the common case.

    `no-html` rather than `nothing` in the log, because the two are different
    findings: one says arXiv has no rendering of this paper and the other says
    it has one whose header named no institution. Only the second is a reason
    to add a pattern.
    """
    conn = drive(monkeypatch, PAPERS[:1],
                 [paper_reply(claims=[CLAIM], institutions=["Meta AI"])],
                 reader=_NoFetch())
    assert conn.institution_writes == {"arxiv:1": ["Meta AI"]}
    assert "institutions (the model, no-html found nothing)" \
        in capsys.readouterr().out


def test_a_refused_affiliation_is_printed_and_never_written(
        loop_env, monkeypatch, capsys):
    """The filter stays reviewable by reading the run's output.

    `arxiv:2310.06825` (Mistral 7B) puts twenty author names in the
    affiliation field, and a row reading "institutions: Devendra Singh
    Chaplot" is a visible defect in the issue. The backfill's dry run prints
    every refusal for this reason and the live insert now does too, so the
    patterns are reviewed from a log rather than from the code.
    """
    # Three names, two commas and no organisation word, which is what
    # `looks_like_a_person_list` is measuring. Two names and one comma are
    # accepted today and should not be: filed to docs/ideas.md this run with
    # the string, because the threshold that fixes it also refuses
    # "Google DeepMind, London" and that trade is the owner's to make.
    people = ('<span class="ltx_role_affiliation">Devendra Singh Chaplot, '
              'Diego de las Casas, Florian Bressand</span>')
    conn = drive(monkeypatch, PAPERS[:1],
                 [paper_reply(claims=[CLAIM])],
                 reader=_WholePaper(40_000, header=people))
    assert conn.institution_writes == {}, "neither source had an answer"
    out = capsys.readouterr().out
    assert "refused:" in out and "Devendra" in out
