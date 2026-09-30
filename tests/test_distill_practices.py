#!/usr/bin/env python3
"""A field report is read by a field report's prompt, and what broke is kept.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The corpus took in engineering blogs from 2026-09-23 (sources.yaml,
cloudflare-engineering at tier d) and read every one of them with
`prompts/distill.md`, a prompt whose first line says "Input: a paper" and which
asks for author affiliations out of a header a blog post does not have. The
accepted ledger entry behind this ("Corpus expansion scoping spike", 2026-09-18)
asks for a variant that asks what they did, why, and what broke.

Two things these tests hold, and they are different in kind.

The routing is held mechanically: `pipeline/evidence.py::source_class` already
decides whether a row is a paper or a field report, because the evidence grade
needs to know, and distill routes off that same function. One function means a
row cannot be graded `field` and read as a paper, and a test can prove it.

What the prompt ASKS is held only as text, because nothing here calls a
provider. So these tests assert the three questions are in the file and that
the JSON contract matches the insert path. Whether the model answers them well
is a question for the first real run, and `broke_reported` in the run log is
where that shows.

Nothing here calls a provider or a database.
"""

import json
import pathlib
import sys

import httpx
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import distill                                                   # noqa: E402
import evidence                                                  # noqa: E402

SOURCE = (ROOT / "pipeline" / "distill.py").read_text()
SCHEMA = (ROOT / "db" / "schema.sql").read_text()
PRACTICES = (ROOT / "prompts" / "distill-practices.md").read_text()
PAPER = (ROOT / "prompts" / "distill.md").read_text()


# ---------------- the prompt exists and is a different prompt ----------------

def test_both_prompts_exist_and_load():
    """Two prompts, two shas. The sha is the only audit trail there is."""
    shas = {}
    for kind in distill.PROMPTS:
        text, sha = distill.load_prompt(kind)
        assert text.strip(), f"{kind}: the prompt file is empty"
        assert len(sha) == 12, f"{kind}: sha is not the 12 hex the schema expects"
        shas[kind] = sha
    assert shas["paper"] != shas["practices"], (
        "the two prompts hash the same, so prompt_sha cannot say which one read "
        "a claim and the whole audit trail is decorative")


def test_the_practices_prompt_asks_what_they_did_why_and_what_broke():
    """The ledger entry's three questions, in the file, in as many words.

    A prompt that only says "summarize this post" would pass every other test
    here. This is the one that holds the entry's actual ask.
    """
    low = PRACTICES.lower()
    for question in ("what did they do", "why did they do it", "what broke"):
        assert question in low, f"the practices prompt never asks: {question}"


def test_the_practices_prompt_is_told_not_to_mine_marketing():
    """Half of a company blog post is written for customers, not for a corpus.

    Without this the pipeline turns launch announcements into claims, which is
    the failure mode that makes a field-report corpus worse than no corpus.
    """
    low = PRACTICES.lower()
    assert "zero claims" in low, (
        "the prompt must permit an empty answer, or it will invent claims out "
        "of an announcement rather than decline it")
    for forbidden in ("pricing", "competitor"):
        assert forbidden in low, f"the prompt never rules out {forbidden}"


def test_the_practices_prompt_offers_only_the_closed_topic_list():
    """The tag list in the prompt is the tag list the insert accepts.

    A second copy of the topic list is how `prompts/distill.md` came to offer
    tags the database dropped: 3.9% of every tag written, invisible to every
    query, for the pipeline's whole life. One prompt already made that mistake
    and the new one does not get to repeat it.
    """
    import topics

    # the prompt names its list on one line; every word on it must be real
    offered = {t for t in topics.TOPICS if t in PRACTICES}
    assert offered == set(topics.TOPICS), (
        "the practices prompt does not offer every topic the taxonomy accepts: "
        f"missing {sorted(set(topics.TOPICS) - offered)}")
    # and it must not invent one
    for line in PRACTICES.splitlines():
        if line.strip().startswith("- `topics`"):
            break
    words = {w.strip(" ,.`") for w in PRACTICES.split()}
    invented = {w for w in words
                if w.replace("-", "").isalpha() and w.endswith("-engineering")
                and w not in topics.TOPICS}
    assert not invented, f"the prompt offers tags the taxonomy will drop: {invented}"


def test_both_prompts_promise_the_same_json_keys():
    """The insert path is shared, so the contract has to be.

    `broke` is the one field only the practices prompt asks for, and it is the
    one field only a field report can answer.
    """
    for key in ("institutions", "claims", "claim", "evidence", "measured",
                "procedure", "topics"):
        assert key in PRACTICES, f"the practices prompt drops `{key}`"
        assert key in PAPER, f"the paper prompt drops `{key}`"
    assert "broke" in PRACTICES
    assert "`broke`" not in PAPER, (
        "the paper prompt was given the field-report field; a paper reports the "
        "configuration that worked, and asking it what broke invites invention")


# ---------------- routing: one function decides, for both purposes ----------------

@pytest.mark.parametrize("paper_id,source,expected", [
    ("arxiv:2609.15906", "arxiv", "paper"),
    ("arxiv:2609.17648", "hf-daily", "paper"),
    ("blog:cloudflare-engineering:9f2a", "cloudflare-engineering", "field"),
    ("blog:openai:11bb", "openai", "field"),
    ("blog:hn-frontpage:77cc", "hn-frontpage", "field"),
])
def test_the_grader_and_the_router_are_one_function(paper_id, source, expected):
    """The prompt a row is read with cannot disagree with the grade it is given.

    Two copies of "is this a paper" is the bug this avoids: a row read as a
    paper and graded as a field report would carry `controlled` evidence mined
    by a prompt that was told to expect anecdotes, or the reverse.
    """
    assert evidence.source_class(paper_id, source) == expected


def test_distill_routes_off_source_class_and_not_off_its_own_copy():
    """Held in the source, because the drain loop needs a database to run."""
    assert 'router.source_class(pid, source) == "field"' in SOURCE
    assert '"practices" if' in SOURCE
    # the router must be loaded whether or not the grade column exists, or an
    # un-migrated database silently reads every blog post as a paper
    assert "router = evidence()" in SOURCE
    assert "grader = router if grading else None" in SOURCE


def test_the_run_says_which_prompt_read_what():
    """A split nobody can see in the log is a split nobody can verify shipped."""
    assert '"read as: "' in SOURCE
    assert "broke_reported" in SOURCE


# ---------------- what broke is kept ----------------

def test_the_schema_keeps_what_broke():
    assert "alter table claims add column if not exists broke text;" in SCHEMA


def test_the_insert_guards_the_column_the_way_the_others_do():
    """A deploy that lands before `modal run pipeline/db_setup.py` must still run.

    The house pattern: ask the database, do not assume the migration ran.
    """
    assert 'has_column(conn, "claims", "broke")' in SOURCE
    assert 'cols.append("broke")' in SOURCE


@pytest.mark.parametrize("value,expected", [
    ("the cache stampeded at 40k rps", "the cache stampeded at 40k rps"),
    ("  padded  ", "padded"),
    ("null", None),
    ("NULL", None),
    ("None", None),
    ("n/a", None),
    ("", None),
    ("   ", None),
    (None, None),
    (0, None),
    ({"a": 1}, None),
])
def test_an_absent_failure_is_none_in_all_of_its_spellings(value, expected):
    """`claims.broke IS NULL` has to mean the source reported no failure.

    JSON from a model is not always typed, and "null" arrives as a string about
    as often as null arrives as null. If the word gets stored, every query that
    counts field reports admitting a failure counts it as an admission.
    """
    assert distill._text_or_none(value) == expected


# ---------------- the request the practices prompt actually sends ----------------

def test_the_practices_prompt_reaches_the_provider(monkeypatch):
    """Same call, same everything, one different system message."""
    sent = {}

    class Response:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": '{"claims": []}'}}]}

        def raise_for_status(self):
            return None

    def fake_post(url, headers=None, json=None, timeout=None):
        sent.update(json)
        return Response()

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", fake_post)

    distill.extract_claims("groq", "How we ran agents", "a body", "practices")
    assert sent["messages"][0]["content"] == PRACTICES, (
        "the practices kind did not reach the provider, so field reports are "
        "still being read as papers")
    assert sent["max_completion_tokens"] == distill.MAX_COMPLETION_TOKENS

    sent.clear()
    distill.extract_claims("groq", "A paper", "a body")
    assert sent["messages"][0]["content"] == PAPER, (
        "the default is no longer the paper prompt")


# ---------------- the gates know about the second prompt ----------------

def test_the_image_carries_the_practices_prompt():
    """A prompt missing from the image fails one paper at a time, forever."""
    assert '.add_local_file("prompts/distill-practices.md",' in SOURCE


def test_the_rehearsal_loads_both_prompts():
    """Gate 3 proves the file is in the image before the deploy, not after.

    It does not call the practices prompt, and the source says so in as many
    words, because a receipt that overclaims is worse than a thin one.
    """
    assert 'load_prompt("practices")' in SOURCE
    assert "practices prompt loaded, not called" in SOURCE


def test_the_budget_guard_sizes_the_new_prompt():
    """A prompt that grows is measured against the runtime budget, not assumed.

    L-E6, and the reason the distill entry was added to that table at all. The
    practices prompt is the larger of the two and would otherwise have been
    sized as the smaller one, or not at all.
    """
    budget = (ROOT / "pipeline" / "budget.py").read_text()
    assert '"prompt": "prompts/distill-practices.md"' in budget
    assert "distill practices (pipeline/distill.py)" in budget
