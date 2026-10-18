#!/usr/bin/env python3
"""What distill sends must fit, and the gate must be harder than the job.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

On 2026-09-26 `pipeline/budget.py` reported that distill's full-text request
missed Groq's usable free tier by 109 tokens, and that number went into the
ledger twice, into the incident register, into two docstrings and into the
guard's own printed output inside one evening. It was wrong by a factor of
seventeen. The guard sized a 24,000-character paper with `budget._FILLER`,
clean English prose at 6.17 chars/token, and a cleaned arXiv paper runs 3.35
over the window the job sends. The real miss was about 1,900 tokens, and the
free fix the ledger had proposed off the first number would not have worked.

The file exists so that cannot happen quietly again. Four properties, none of
which needs the network or a key:

1. the request the job builds fits, with the margin recorded rather than implied
2. the guard sizes a paper as a paper, not as prose
3. the rehearsal's payload is heavier than the heaviest real paper measured
4. the receipt in docs/evals/ and the constant in budget.py agree

Property 3 is the one with teeth. A gate that sends a lighter request than
production does is a gate that passes what production fails, which is what the
rehearsal did until 2026-09-27 even after the guard was fixed: its sample was
prose, 750 tokens lighter than arxiv:2407.21783 at the same character count.
"""

import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import budget                                                    # noqa: E402
import distill                                                   # noqa: E402

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

RECEIPT = json.loads((ROOT / "docs" / "evals"
                      / "2026-09-30-fulltext-token-density.json").read_text())
SPEC = budget.CRON_REQUESTS["distill (pipeline/distill.py)"]
PROMPT = (ROOT / "prompts" / "distill.md").read_text()
#: The model whose per-request limit binds, read out of the job rather than
#: named here. It was `openai/gpt-oss-120b` until 2026-09-30 and distill moved
#: to kimi-k2.6 that day; a constant naming a fallback checks the wrong ceiling.
MODEL = budget.distill_models()[0]


def rehearsal_body() -> str:
    """Byte for byte what `distill.rehearse` sends, built the same way."""
    sample = distill.REHEARSAL_SAMPLE
    reps = distill.FULLTEXT_CHARS // len(sample) + 1
    return (sample * reps)[:distill.FULLTEXT_CHARS]


# ---------------- 1. it fits ----------------

def test_the_full_text_request_fits_the_model_the_job_actually_calls():
    """The head of the list, which is the one tomorrow's cron meets first.

    This asked it of EVERY model until 2026-09-30, and at a 12,000-character
    window every model could answer. At 250,000 none of the Groq fallbacks can,
    by three orders of magnitude, and that is not a regression: their whole
    per-request budget is 6,800 tokens. The invariant that survives the move is
    that the model the job calls takes the request untrimmed, and the invariant
    below is the one that keeps the fallbacks honest.
    """
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    report = budget.check_request(
        PROMPT, budget.request_text(SPEC, distill.FULLTEXT_CHARS),
        distill.MAX_COMPLETION_TOKENS, MODEL)
    assert report.fits, (
        f"distill cannot send a paper to {MODEL}: {report.summary()}. "
        "The job will be refused and will write claims from the abstract "
        "while reporting success.")


def test_every_fallback_can_at_least_take_the_documented_abstract():
    """A fallback that cannot take the abstract is not a fallback at all.

    The Groq entries cannot read a paper and the job says so in three places.
    What they can still do is keep a run alive when Moonshot is down, writing
    claims from `abstract[:6000]` and marking `fulltext_chars` null so nothing
    downstream calls it a full read. That is worth having and it is worth
    checking, because a fallback list nobody measured is a list of comforts.
    """
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    for model in budget.distill_models():
        if model not in budget.MODELS:
            continue
        report = budget.check_request(
            PROMPT, budget.request_text(SPEC, SPEC["degrades_to_chars"]),
            distill.MAX_COMPLETION_TOKENS, model)
        assert report.fits, (
            f"{model} cannot even take the abstract distill falls back to: "
            f"{report.summary()}. Take it off the list rather than leaving a "
            "run pretending it has somewhere to go.")


def test_every_model_in_the_list_can_take_the_window_sized_for_it():
    """The invariant the two tests above left uncovered, and it is the defect.

    Those two say the head of the list takes a whole paper and every fallback
    takes an abstract. Both were true on 2026-10-15 and the job sent 250,000
    characters to whichever model the walk reached first anyway, because nothing
    chose the size from the model. `window_for` is that choice and this is the
    property it has to hold: whatever the walk reaches, the request built for it
    fits without the provider having to say so.

    Sized against `budget.request_text`, which builds the payload at the
    measured density of a real paper rather than of prose, and against the
    RENDERED prompt, which is the text the model is sent. The raw file is a
    third of the size and sizing against it is the hazard that made the first
    version of this guard wrong by a factor of seventeen.
    """
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    for kind in distill.PROMPTS:
        rendered, _ = distill.load_prompt(kind)
        for model in distill.MODELS:
            window = distill.window_for(model, kind)
            report = budget.check_request(
                rendered, budget.request_text(SPEC, window),
                distill.MAX_COMPLETION_TOKENS, model)
            assert report.fits, (
                f"a {kind} request sized by window_for at {window} characters "
                f"does not fit {model}: {report.summary()}. The window is "
                "supposed to be derived from this model's own published limit, "
                "so either the derivation lost a term or the density is stale.")


def test_the_head_of_the_list_still_gets_the_whole_measured_window():
    """The funded path does not pay for the fallbacks' problem.

    250,000 characters is a measurement, not a guess: 13 of the 14 papers in
    docs/evals/2026-09-30-fulltext-token-density.json arrive complete at it and
    the expected cost stops moving past it. kimi-k2.6's usable budget is wide
    enough for twice that, so a per-model window must cap at the measurement
    rather than spend the headroom.
    """
    assert distill.window_for(distill.MODELS[0]) == distill.FULLTEXT_CHARS
    for kind in distill.PROMPTS:
        assert distill.window_for(distill.MODELS[0], kind) == distill.FULLTEXT_CHARS


def test_a_fallback_window_is_below_the_floor_so_a_degraded_day_reads_abstracts():
    """The floor is what keeps "read in full" from becoming a 7,000-character claim.

    A Groq fallback's whole per-request budget is 6,800 tokens, which is about
    6,900 characters of a paper once the prompt and the output reservation are
    out. That is a tenth of the shortest window this job has ever called
    reading a paper, so the honest answer is the abstract and a null
    `fulltext_chars`, which is what `preflight` and the end-of-run NOTE have
    both promised since 2026-09-30.
    """
    assert distill.FULLTEXT_FLOOR_CHARS < distill.FULLTEXT_CHARS
    for model in distill.MODELS[1:]:
        window = distill.window_for(model)
        assert window < distill.FULLTEXT_FLOOR_CHARS, (
            f"{model} can take {window} characters of a paper, at or above the "
            f"{distill.FULLTEXT_FLOOR_CHARS}-character floor, so the run would "
            "now record a full read for it. If that is right, the floor and "
            "the masthead's sentence both need revisiting, in that order.")
    # And the abstract the degraded day falls back to fits inside what the
    # fallback can take, or the day has nowhere to go at all.
    assert SPEC["degrades_to_chars"] <= distill.window_for(distill.MODELS[1])


def test_the_window_moves_with_the_providers_published_limit():
    """Derived, not remembered. A tier change is one edit to budget.MODELS.

    The whole point of taking the number out of the job is that the day the
    free tier doubles its per-minute budget, the job reads more of a paper
    without anyone editing the job. A literal anywhere in the chain fails here.
    """
    model = distill.MODELS[1]
    before = distill.window_for(model)
    spec = dict(budget.MODELS[model])
    spec["tpm"] = spec["tpm"] * 4
    saved = budget.MODELS[model]
    budget.MODELS[model] = spec
    try:
        after = distill.window_for(model)
    finally:
        budget.MODELS[model] = saved
    assert after > before, (
        "quadrupling this model's published per-minute budget did not widen "
        "the window, so something in the chain is a constant rather than a "
        "derivation")
    assert distill.window_for(model) == before


def test_reading_model_is_the_model_the_walk_will_actually_reach():
    """Same skips as `llm.ask_json`, or the window is sized for the wrong model.

    Three cases, because the three disagree: the catalogs could not be read
    (trust the table, take the head), the catalogs answered and the head is
    missing (take the first one that is there), and nothing is listed at all
    (say so rather than guess).
    """
    assert distill.reading_model(None) == distill.MODELS[0]
    fallbacks = set(distill.MODELS[1:])
    assert distill.reading_model(fallbacks) == distill.MODELS[1]
    assert distill.reading_model(set()) is None
    assert distill.reading_model({distill.MODELS[2]}) == distill.MODELS[2]
    # A model its provider has withdrawn is skipped the way the walk skips it,
    # which is incident 24's 404 never paid for twice.
    saved = dict(budget.DECOMMISSIONED)
    budget.DECOMMISSIONED[distill.MODELS[0]] = "withdrawn, for this test only."
    try:
        assert distill.reading_model(None) == distill.MODELS[1]
    finally:
        budget.DECOMMISSIONED.clear()
        budget.DECOMMISSIONED.update(saved)


def test_the_run_counts_a_full_read_against_the_window_and_not_the_constant():
    """`whole` has to compare against what was sent, not against the ambition.

    This is the half of the fix that is about honesty rather than about speed.
    A paper trimmed to what a smaller model can take was not read in full, and
    `papers.fulltext_chars` is the column the masthead's "read in full"
    sentence is counted from. A `len(body) < FULLTEXT_CHARS` left in the loop
    would report a complete read of a paper that was cut by 97%.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "whole = len(body) < window" in source
    assert "whole = len(body) < FULLTEXT_CHARS" not in source
    # And the trim itself, so the body cannot be larger than the window the
    # line above then measures it against.
    assert "body = body[:window]" in source


def test_the_job_declares_its_reservation_instead_of_leaving_it_assumed():
    # The guard used to carry `reservation_assumed: 2000` for this job because
    # the job sent nothing. A request sized against an assumption is not sized.
    assert "reservation_assumed" not in SPEC
    reservation, how = budget.request_reservation(SPEC)
    assert reservation == distill.MAX_COMPLETION_TOKENS
    assert how == "", "the reservation is read out of the job, not assumed"


def test_the_reservation_is_actually_sent(monkeypatch):
    sent = {}

    class Response:
        status_code = 200
        text = ""
        headers: dict = {}

        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": '{"claims": []}'},
                                 "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5}}

    def fake_post(url, headers=None, json=None, timeout=None):
        sent.update(json)
        return Response()

    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")
    # load_prompt reads /root inside Modal; point it at the repo's own file.
    monkeypatch.setattr(distill, "load_prompt",
                        lambda kind="paper": (PROMPT, "abc123def456"))
    import httpx
    monkeypatch.setattr(httpx, "post", fake_post)
    client = distill.llm()
    distill.extract_claims("a title", "a body", env=os.environ,
                           cap=client.Cap(1.0), models=[MODEL])
    assert sent["max_completion_tokens"] == distill.MAX_COMPLETION_TOKENS, (
        "the constant exists and the request does not carry it, so the guard "
        "is checking a number the provider never sees")
    assert sent["model"] == MODEL


# ---------------- 2. a paper is not prose ----------------

def test_the_payload_is_sized_at_the_measured_paper_density():
    assert SPEC["chars_per_token"] == budget.FULLTEXT_CHARS_PER_TOKEN
    tokens = budget.count_tokens(budget.request_text(SPEC, distill.FULLTEXT_CHARS))
    expected = round(distill.FULLTEXT_CHARS / budget.FULLTEXT_CHARS_PER_TOKEN)
    assert abs(tokens - expected) <= 2, (
        f"the filler was asked for {expected} tokens and produced {tokens}")


def test_prose_filler_would_understate_a_paper_by_a_third_or_more():
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    # The bug, stated as the arithmetic that would reintroduce it.
    paper = budget.count_tokens(budget.request_text(SPEC, distill.FULLTEXT_CHARS))
    prose = budget.count_tokens(budget._filler(distill.FULLTEXT_CHARS))
    assert paper >= prose * 1.33, (
        f"sizing {distill.FULLTEXT_CHARS} chars as a paper gives {paper} tokens "
        f"and as prose {prose}; these being close means the override is gone")


# ---------------- 3. the gate is harder than the job ----------------

def test_the_rehearsal_sends_more_tokens_than_the_densest_real_paper():
    """The property that makes gate 3 worth running.

    If the rehearsal's payload were lighter than a real paper's, a provider
    could accept the rehearsal and refuse the papers, and the gate would sign
    off on the defect it exists to catch. It was lighter until 2026-09-27.
    """
    worst = max(row["tokens"] for row in RECEIPT["papers"])
    mine = budget.count_tokens(rehearsal_body())
    assert mine >= worst, (
        f"the rehearsal sends {mine} tokens and arxiv paper "
        f"{max(RECEIPT['papers'], key=lambda r: r['tokens'])['paper']} is "
        f"{worst}. A gate lighter than production passes what production fails.")


def test_the_rehearsal_payload_still_fits():
    pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)
    # Harder than production, and still inside the limit. If this fails, the
    # gate has become impossible to pass rather than strict.
    report = budget.check_request(PROMPT, rehearsal_body(),
                                  distill.MAX_COMPLETION_TOKENS, MODEL)
    assert report.fits, report.summary()


def test_most_of_a_real_paper_arrives_whole_at_this_window():
    """The reason to widen the window at all, stated as a number.

    Fitting is the provider's question. Completeness is the reader's, and it is
    the one the product's masthead answers when it says "read in full". At
    12,000 characters the honest answer was zero of fourteen.
    """
    assert RECEIPT["papers_complete"] >= 12, (
        f"only {RECEIPT['papers_complete']} of {RECEIPT['papers_measured']} "
        "measured papers arrive whole at this window, so 'read in full' is "
        "again a claim about most of a paper rather than a paper")


def test_the_rehearsal_measures_the_window_the_job_sends():
    assert len(rehearsal_body()) == distill.FULLTEXT_CHARS


# ---------------- 4. the receipt and the constant agree ----------------

def test_the_constant_is_no_looser_than_the_worst_paper_measured():
    assert budget.FULLTEXT_CHARS_PER_TOKEN <= RECEIPT["worst_chars_per_token"]


def test_the_receipt_measured_the_window_that_binds():
    # Density is not uniform through a paper: these same papers run 3.65
    # chars/token over their first 24,000 characters and 3.35 over their first
    # 12,000. Measuring the generous window and sending the tight one is how the
    # first corrected constant was still wrong, by 5 tokens, on one real paper.
    assert RECEIPT["window_chars"] == distill.FULLTEXT_CHARS


def test_every_paper_in_the_receipt_fits():
    for row in RECEIPT["papers"]:
        assert row["fits"], f"{row['paper']} does not fit: {row}"
    assert RECEIPT["all_fit"]


def test_the_receipt_is_not_a_single_paper():
    # A worst case drawn from one sample is an anecdote. The spread is the
    # point: 3.35 to 4.93 across these, and the low end is what binds.
    assert len(RECEIPT["papers"]) >= 10
    densities = [row["chars_per_token"] for row in RECEIPT["papers"]]
    assert max(densities) - min(densities) > 1.0, (
        "these papers are too alike to bound a worst case")


# ---------------- the prompt half of the price, measured not remembered ------

def test_the_price_counts_the_prompt_the_job_actually_sends():
    """`EXPECTED_PROMPT_TOKENS = 39_059  # 38,069 payload + 990 prompt` was the
    constant here until 2026-10-09, and 990 was measured once.

    990 was correct on the day it was written: `prompts/distill.md` was 4,120
    characters and exactly 990 tokens at the reasoning rubric commit. The four
    Layer 4 definitions of 2026-10-05 took it to 6,056 characters and 1,427
    tokens, and nothing re-measured. So the two numbers the owner asked for by
    name, cost per paper and projected monthly spend, were each short by 437
    tokens of input for four days, and no test in this repository mentioned
    the constant.

    It is derived now. This test is what keeps it derived: a rounded literal
    put back in its place fails here rather than in a price nobody checks.
    """
    counted = distill.prompt_tokens()
    text, _ = distill.load_prompt("paper")
    assert counted == budget.count_tokens(text)
    # The rendered prompt, so the topic vocabulary is inside the number. The
    # raw file is a third of the size and sizing against it is the hazard
    # `budget.prompt_text` exists to remove.
    raw = (ROOT / "prompts" / "distill.md").read_text()
    assert counted > budget.count_tokens(raw)
    assert distill.expected_prompt_tokens() == (
        distill.EXPECTED_PAYLOAD_TOKENS + counted)
    # The number the stale constant carried. Kept as a literal on purpose: it
    # is the size of the error, and it is what this test was written to end.
    assert counted > 990, (
        "the prompt is smaller than the constant that went stale, so either "
        "the vocabulary stopped being rendered or the prompt lost its body")


def test_no_caller_prices_a_run_off_a_remembered_prompt_size():
    """One derivation, three callers, and no second copy of the number.

    `cost_report` prints the expected cost and the ceiling, and the queue
    report multiplies the expected cost by the queue depth. All three take the
    prompt from `prompt_tokens()`. A literal `990` reappearing beside a
    `cost_usd` call is the regression.
    """
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "EXPECTED_PROMPT_TOKENS" not in source
    assert "+ 990" not in source
    for line in source.splitlines():
        if "cost_usd(" in line:
            assert "990" not in line, line
