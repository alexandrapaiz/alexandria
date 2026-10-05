"""The one-time retag: owner directive 2026-10-05, item 2.

Every test here is about the part of the job that is a judgment rather than a
query, because that is where a backfill does damage. The census this job was
built from read 24 claims a keyword had credited to the containment thread and
found none of them about containment, so the thing worth testing is that a
keyword match selects a candidate and never writes a tag.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import priority  # noqa: E402
import topics  # noqa: E402

retag = pytest.importorskip(
    "retag_threads", reason="needs the modal package for the decorators")


# ----------------------------------------------- the four threads and the list

def test_the_threads_it_writes_are_all_on_the_closed_list():
    for thread in retag.THREADS:
        assert thread in topics.TOPICS


def test_it_does_not_touch_reasoning():
    """`reasoning` has been on the list since 2026-09-26 and is in use.

    It is a key of THREAD_TERMS because it is one of the owner's threads, and
    leaving it out of this job is deliberate: re-judging claims against a tag
    the distiller has already been applying for a week would be a second
    taxonomy change wearing a backfill's clothes.
    """
    assert "reasoning" in priority.THREAD_TERMS
    assert "reasoning" not in retag.THREADS


def test_every_thread_it_writes_has_terms_to_select_candidates_with():
    for thread in retag.THREADS:
        assert priority.THREAD_TERMS.get(thread), thread


def test_the_patterns_are_the_thread_terms_and_not_a_second_list():
    patterns = retag.patterns_for(retag.THREADS, priority.THREAD_TERMS)
    expected = [f"%{t}%" for thread in retag.THREADS
                for t in priority.THREAD_TERMS[thread]]
    assert patterns == expected
    # And the flat priority list is still derived from the same table, so the
    # queue order and this job's candidate rule cannot drift apart.
    assert priority.PRIORITY_TERMS == tuple(
        t for terms in priority.THREAD_TERMS.values() for t in terms)


# ------------------------------------------------------- the cheapest model

def test_the_model_is_the_cheapest_in_the_budget_table_read_from_the_table():
    import budget

    order = retag.cheapest_first(budget)
    prices = [budget.MODELS[m]["price_in"] + budget.MODELS[m]["price_out"]
              for m in order]
    assert prices == sorted(prices), order
    assert prices[0] == 0.0, "a free model exists and should be chosen first"


def test_a_preview_or_withdrawn_model_is_never_chosen():
    import budget

    order = retag.cheapest_first(budget)
    for model in order:
        assert budget.MODELS[model]["status"] == "production"
        assert model not in budget.DECOMMISSIONED


# ------------------------------------------- the definitions come from the prompt

def test_the_definitions_are_lifted_from_the_prompt_and_not_restated_here():
    """One copy of a definition, for the reason `prompt_topics` exists.

    A retag judging by its own paraphrase of a boundary would write tags the
    distiller would not have chosen, and the column would stop meaning one
    thing.
    """
    text = (ROOT / "prompts" / "distill.md").read_text()
    defs = retag.definitions(text)
    for thread in retag.THREADS:
        assert f"`{thread}` covers" in defs, thread
    # The boundary clauses are the load-bearing half, so check one survived.
    assert "is `systems`" in defs


def test_a_thread_the_prompt_does_not_define_is_refused_not_guessed():
    defs = retag.definitions("nothing in here at all", ("containment",))
    assert defs == ""


# ---------------------------------------------- what the model's answer becomes

def test_a_model_that_declines_adds_nothing():
    """The common and correct answer. Most keyword candidates take no tag."""
    assert retag.chosen({"topics": [], "why": "an RL result"}, topics) == []
    assert retag.chosen({}, topics) == []


def test_the_answer_is_folded_so_typography_is_not_a_refusal():
    picked = retag.chosen(
        {"topics": ["Containment", "SECURITY", "self improvement"]}, topics)
    assert picked == ["containment", "security", "self-improvement"]


def test_a_model_volunteering_a_tag_outside_the_mandate_is_ignored():
    """Four tags wide. A retag that started writing `evals` would be a different job."""
    assert retag.chosen({"topics": ["evals", "containment", "memory"]}, topics) \
        == ["containment"]


def test_an_invented_tag_is_ignored_rather_than_written():
    assert retag.chosen({"topics": ["safety", "sandboxing"]}, topics) == []


def test_junk_in_the_answer_does_not_raise():
    assert retag.chosen({"topics": [None, 7, {"a": 1}, "containment"]}, topics) \
        == ["containment"]


# ------------------------------------------------------ merging, never removing

def test_an_existing_tag_is_never_removed():
    """A tag already on a claim was a judgment about a text this job cannot see."""
    assert retag.merged(["evals", "safety"], ["security"], topics) \
        == ["evals", "safety", "security"]


def test_an_off_list_tag_survives_because_deleting_it_is_the_research_seats_call():
    assert "safety" in retag.merged(["safety"], ["security"], topics)


def test_the_fallback_comes_off_when_a_real_tag_arrives():
    assert retag.merged(["other"], ["containment"], topics) == ["containment"]


def test_the_fallback_stays_when_nothing_arrives():
    assert retag.merged(["other"], [], topics) == ["other"]


def test_a_claim_already_carrying_the_tag_is_not_given_it_twice():
    assert retag.merged(["containment"], ["containment"], topics) == ["containment"]


def test_the_cap_per_claim_is_respected():
    full = list(topics.TOPICS[:topics.MAX_PER_CLAIM])
    assert len(retag.merged(full, ["containment"], topics)) == topics.MAX_PER_CLAIM


# ------------------------------------------------------------- resumability

def test_the_candidate_query_excludes_what_has_been_judged():
    """Resumability, as a property of the SQL rather than of a comment.

    A model that correctly adds no tag leaves the row byte-identical to one
    nobody read, so `retag_log` is the only thing that can say the call was
    already paid for.
    """
    assert "retag_log" in retag.CANDIDATES
    assert "not exists" in retag.CANDIDATES.lower()
    assert "order by c.id" in retag.CANDIDATES


def test_the_log_table_is_created_by_the_job_so_a_first_run_works():
    assert "create table if not exists retag_log" in retag.LOG_DDL
    assert "claim_id   bigint primary key" in retag.LOG_DDL
    # It records which model said so, or the audit trail is just a tag.
    assert "model" in retag.LOG_DDL and "added" in retag.LOG_DDL


def test_the_dry_run_and_the_write_are_separate_functions_with_separate_secrets():
    """The same split backfill_topics.py has, and for the same reason.

    `count` is given no model secret at all, so it cannot acquire a bill by a
    later edit, and a reviewer can see that from the decorator.
    """
    source = (ROOT / "pipeline" / "retag_threads.py").read_text()
    count_block = source.split("def count(")[0].split("@app.function")[-1]
    assert "neon" in count_block
    assert "groq" not in count_block and "moonshot" not in count_block
    assert "called no model" in source


def test_the_population_query_reports_both_numbers_the_directive_asked_for():
    """"71 candidates, 0 judged" needs a numerator and a denominator."""
    assert "candidates" in retag.POPULATION and "judged" in retag.POPULATION


def test_both_queries_match_title_or_abstract_as_the_directive_says():
    for sql in (retag.CANDIDATES, retag.POPULATION):
        assert "p.title ilike any" in sql
        assert "p.abstract" in sql


def test_the_abstract_match_survives_a_null_abstract():
    """Half the corpus has no abstract; `null ilike any` is null, not false."""
    for sql in (retag.CANDIDATES, retag.POPULATION):
        assert "coalesce(p.abstract, '')" in sql


def test_a_run_is_bounded_so_a_shared_rate_limit_is_not_exhausted():
    assert retag.MAX_CLAIMS_PER_RUN <= 1000, "Groq's free tier allows 1,000 a day"
    assert "limit %(limit)s" in retag.CANDIDATES
