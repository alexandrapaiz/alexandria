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
    assert len(triage.REHEARSAL_BATCH) >= 3
    assert all(len(row) == 4 for row in triage.REHEARSAL_BATCH)
    rendered = triage.render_batch(list(triage.REHEARSAL_BATCH))
    assert "Fourier" in rendered and "Context Rot" in rendered


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
    # Three of the five should relate and two should not, which is what lets the
    # rehearsal fail a model that labels everything and one that labels nothing.
    assert len(interpret.REHEARSAL_NEIGHBORS) == 5
    ids = [nid for nid, _ in interpret.REHEARSAL_NEIGHBORS]
    assert len(set(ids)) == 5
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
        if "where embedding is null" in low:
            return FakeCursor([])              # nothing left to embed
        return FakeCursor([])

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def paper_reply(status=200, claims=None, prompt_tokens=40_000):
    body = {
        "choices": [{"message": {"content": json.dumps(
            {"claims": claims or [], "institutions": []})},
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

    def fetch_fulltext(self, pid, max_chars=None):
        return None

    def fetch_metadata(self, pid):
        return None


class _WholePaper(_NoFetch):
    def __init__(self, length):
        self.length = length

    def fetch_fulltext(self, pid, max_chars=None):
        body = "x" * self.length
        return body[:max_chars] if max_chars else body


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
