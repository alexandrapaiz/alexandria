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
