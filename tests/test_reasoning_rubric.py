"""The 2026-09-26 reasoning directive: the rubric, the topic, and the re-triage.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The owner's numbers: 209 papers with "reasoning" in the title, 147 never
triaged, and of the 62 that were, 47 went to `index` and 14 to `distill`,
because the old prompt rewarded a "construction technique" and a reasoning
paper's contribution is usually a training recipe. The research seat wrote the
rubric. What this file holds is the part a test can hold without a database:

- the taxonomy is closed, and the fold that gets a tag onto it fixes spelling
  and never meaning,
- `reasoning` is on that list and on the prompt's list, and the two lists agree,
- reasoning papers are drained first inside every tier, with tier fairness
  untouched,
- the re-triage appends rather than edits, skips what it has already judged, and
  writes the paper that did not move,
- nothing downstream reads `triage_log` in a way that returns a re-triaged paper
  twice.

No database and no provider is reachable from here, so the re-triage is exercised
against a recording connection and a stubbed client. That is enough to hold the
behaviour that matters, which is what it writes and what it refuses to write.
"""

import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import backfill_topics                                           # noqa: E402
import llm                                                       # noqa: E402
import topics                                                    # noqa: E402
import triage                                                    # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# ---------------- the closed list ----------------

def test_reasoning_is_a_topic_the_database_accepts():
    assert "reasoning" in topics.TOPICS


def test_the_prompts_list_and_the_enforced_list_are_the_same_list():
    # The prompt is what the model is told and TOPICS is what the insert accepts.
    # A tag the prompt offers and the code rejects would be dropped on every
    # claim, silently, which is the class of bug this whole module exists for.
    offered = topics.prompt_topics((ROOT / "prompts" / "distill.md").read_text())
    assert offered, "prompts/distill.md no longer lists its topics where this can read them"
    assert offered == list(topics.TOPICS)


def test_the_non_breaking_hyphen_twin_folds_onto_the_real_topic():
    # 18 claims in the corpus carry one of these and are invisible to every query
    # the product runs. U+2011 looks identical to a hyphen in every editor.
    kept, dropped = topics.normalize(["post\u2011training", "harness\u2011engineering"])
    assert kept == ["post-training", "harness-engineering"]
    assert dropped == []


def test_case_and_spaces_are_typography_and_get_folded():
    kept, dropped = topics.normalize(["Multi Agent", "CONTEXT ENGINEERING", " memory "])
    assert kept == ["multi-agent", "context-engineering", "memory"]
    assert dropped == []


def test_an_invented_tag_is_dropped_and_reported_in_its_own_spelling():
    # `training` is not silently promoted to `post-training`: the fold fixes
    # spelling, never meaning, or the column stops being evidence of anything.
    kept, dropped = topics.normalize(["reasoning", "training", "safety"])
    assert kept == ["reasoning"]
    assert dropped == ["training", "safety"]


def test_the_three_aliases_are_the_ones_the_prompt_itself_licenses():
    # prompts/distill.md defines `reasoning` as covering chain-of-thought and
    # test-time compute, so a model answering with the phrase from the definition
    # made a formatting error, not a judgment.
    for phrase in ("chain-of-thought", "Chain Of Thought", "test-time compute"):
        assert topics.normalize([phrase])[0] == ["reasoning"], phrase
    prompt = (ROOT / "prompts" / "distill.md").read_text().lower()
    for alias in topics.ALIASES:
        assert alias.replace("-", " ") in prompt.replace("-", " ") or alias == "cot"


def test_a_claim_whose_every_tag_was_dropped_is_tagged_other_not_nothing():
    kept, dropped = topics.normalize(["nonsense", ""])
    assert kept == ["other"]
    assert dropped == ["nonsense"]


def test_tags_are_deduplicated_and_capped():
    kept, _ = topics.normalize(["memory", "Memory", "memory "] + list(topics.TOPICS))
    assert kept.count("memory") == 1
    assert len(kept) == topics.MAX_PER_CLAIM


def test_the_insert_enforces_the_list_at_the_only_place_claims_are_written():
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "taxonomy.normalize(c.get(\"topics\"))" in source
    # and the old pass-through is gone, or both paths exist and one of them lies
    assert "c.get(\"topics\") or []" not in source


def test_the_off_list_rate_is_printed_every_run():
    # It was 3.9% for the pipeline's whole life and nobody could have known,
    # because nothing counted it.
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "tags dropped as off-list" in source


# ---------------- the distill prompt_sha ----------------

def test_every_claim_records_which_prompt_wrote_it():
    assert "alter table claims add column if not exists prompt_sha text;" in SCHEMA
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "def load_prompt()" in source
    assert "cols.append(\"prompt_sha\")" in source


def test_the_distill_prompt_is_read_in_exactly_one_place():
    # Two readers is how a sha comes to describe a prompt that was not used.
    source = (ROOT / "pipeline" / "distill.py").read_text()
    assert source.count('open("/root/prompts/distill.md")') == 1


def test_the_sha_is_the_same_shape_the_press_and_triage_use():
    # 12 hex of sha256, so a column full of them can be compared across tables.
    for path in ("triage.py", "distill.py", "weekly.py"):
        source = (ROOT / "pipeline" / path).read_text()
        assert "hexdigest()[:12]" in source, path


# ---------------- reasoning first, tier fairness intact ----------------

def test_the_priority_predicate_reads_titles_not_abstracts():
    assert triage.is_priority("Process Reward Models for Long CoT")
    assert triage.is_priority("GRPO at scale")
    assert not triage.is_priority("A Fast Fourier Transform Variant for Radio Astronomy")
    # The SQL and the Python are generated from one tuple, so they cannot drift.
    assert triage.PRIORITY_PATTERNS == [f"%{t}%" for t in triage.PRIORITY_TERMS]


def test_the_queue_query_sorts_reasoning_first_inside_each_tier():
    source = (ROOT / "pipeline" / "triage.py").read_text()
    query = source.split("row_number() over")[1].split(") ranked")[0]
    assert "partition by tier" in query
    assert "case when title ilike any(%s) then 0 else 1 end" in query
    # published_at is still the tie-break, so within the priority the queue is
    # still newest-first and the drain is still resumable without a cursor.
    assert "published_at desc nulls last" in query


def test_reasoning_papers_reach_the_first_batch_of_every_tier():
    # The rows arrive in the order the SQL returns them: priority first within
    # each tier. plan_batches interleaves tiers, so the fairness rule that cost
    # the pipeline 2,445 unread papers is untouched and the priority is served.
    rows = []
    for tier in ("a", "b"):
        for i in range(triage.BATCH):
            rows.append((f"{tier}-r{i}", f"Reasoning traces {i}", "abs", tier))
        for i in range(triage.BATCH):
            rows.append((f"{tier}-o{i}", f"Sparse attention kernels {i}", "abs", tier))
    plan = triage.plan_batches(rows, max_calls=4)
    first_two = plan[:2]
    assert {chunk[0][3] for chunk in first_two} == {"a", "b"}, "tier interleaving lost"
    for chunk in first_two:
        assert all(triage.is_priority(row[1]) for row in chunk)


def test_the_run_prints_how_much_of_its_plan_is_the_priority():
    source = (ROOT / "pipeline" / "triage.py").read_text()
    assert "reasoning-first:" in source
    # and the untriaged reasoning depth, which is the owner's 147, every run
    assert "reasoning-model research by title, " in source


# ---------------- the re-triage ----------------

def test_the_re_triage_only_looks_at_papers_the_current_rubric_has_not_judged():
    sql = triage.RETRIAGE_CANDIDATES
    assert "join latest_triage" in sql, "a paper's newest decision is the only one that counts"
    assert "t.decision = 'index'" in sql
    assert "coalesce(t.prompt_sha, '') != %s" in sql, "this guard is the idempotence"
    assert "p.distilled_at is null" in sql
    assert "t.model != 'rule:backfill'" in sql


def test_the_dry_run_and_the_write_are_separate_functions_with_separate_secrets():
    source = (ROOT / "pipeline" / "triage.py").read_text()
    plan = source.split("def retriage_plan")[1].split("def retriage(")[0]
    head = source.split("def retriage_plan")[0]
    assert "moonshot" not in head.rsplit("@app.function", 1)[-1], \
        "the dry run must not be able to call a model"
    assert "insert" not in plan.lower(), "the dry run must not be able to write"


class Recording:
    """A connection that answers with queued rows and keeps every statement."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.statements = []

    def execute(self, sql, params=None):
        self.statements.append((" ".join(sql.split()), params))
        rows = self.answers.pop(0) if self.answers else []
        return types.SimpleNamespace(fetchall=lambda: rows,
                                     fetchone=lambda: rows[0] if rows else None,
                                     rowcount=len(rows))

    def commit(self):
        self.statements.append(("COMMIT", None))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def retriage_run(monkeypatch):
    """Drive triage.retriage against a recording connection and a stub model."""

    def run(rows, answer):
        conn = Recording(rows)
        psycopg = types.ModuleType("psycopg")
        psycopg.connect = lambda *a, **k: conn
        monkeypatch.setitem(sys.modules, "psycopg", psycopg)
        monkeypatch.setenv("DATABASE_URL", "postgres://stub")
        monkeypatch.setattr(triage, "load_prompt", lambda: ("rubric text", "beef1234cafe"))
        monkeypatch.setattr(llm, "usable_models", lambda *a, **k: (None, []))
        monkeypatch.setattr(llm, "ask_json", lambda *a, **k: (answer, "kimi-k2.6"))
        monkeypatch.setattr(triage.time, "sleep", lambda s: None)
        return conn, triage.retriage()

    return run


def test_a_promoted_paper_gets_a_second_row_and_the_first_one_is_left_alone(retriage_run):
    conn, result = retriage_run(
        [("arxiv:1", "Reasoning traces as supervision", "abs", "a", 0.4, None)],
        {"results": [{"i": 0, "decision": "distill", "score": 0.8,
                      "reasoning": "gives the reward and the curriculum"}]},
    )
    writes = [(sql, params) for sql, params in conn.statements if sql.startswith("insert")]
    assert len(writes) == 1
    sql, params = writes[0]
    assert "insert into triage_log" in sql
    assert "update" not in " ".join(s for s, _ in conn.statements).lower()
    assert params[0] == "arxiv:1" and params[1] == "distill"
    assert params[5] == "beef1234cafe"
    assert params[6] == "kimi-k2.6@beef1234cafe", "method is model@sha, as claim_links has always been"
    assert "re-triage under the reasoning rubric" in params[3]
    assert "1 promoted" in result


def test_a_paper_the_new_rubric_agrees_about_is_still_written(retriage_run, capsys):
    # Without the row the job would ask the same question of the same paper every
    # time it ran, because the skip guard is the row's prompt_sha.
    conn, result = retriage_run(
        [("arxiv:2", "A reasoning benchmark for telecom", "abs", "a", 0.3, None)],
        {"results": [{"i": 0, "decision": "index", "score": 0.3,
                      "reasoning": "measures, offers no recipe"}]},
    )
    writes = [p for sql, p in conn.statements if sql.startswith("insert")]
    assert len(writes) == 1 and writes[0][1] == "index"
    assert "index -> index: 1" in capsys.readouterr().out
    assert "0 promoted" in result


def test_a_batch_the_model_answered_badly_leaves_the_paper_where_it_was(retriage_run):
    conn, result = retriage_run(
        [("arxiv:3", "Reasoning and planning", "abs", "a", 0.3, None)],
        {"results": [{"i": 0, "decision": "maybe", "score": 0.3, "reasoning": "?"}]},
    )
    assert [s for s, _ in conn.statements if s.startswith("insert")] == []
    assert "re-judged 0 papers" in result


def test_the_re_triage_cap_is_smaller_than_the_daily_drains(retriage_run):
    assert triage.RETRIAGE_CAP_USD < triage.CAP_USD
    # 47 papers is five calls, so the cap has room for an order of magnitude more
    # papers than the set it was written for.
    per_call = llm.budget().cost_usd(3_500, triage.MAX_COMPLETION_TOKENS, "kimi-k2.6")
    assert triage.RETRIAGE_CAP_USD / per_call > 47 / triage.BATCH


# ---------------- one paper, one current decision ----------------

def test_the_schema_has_a_latest_decision_view_and_distill_reads_it():
    assert "create or replace view latest_triage as" in SCHEMA
    assert "distinct on (paper_id)" in SCHEMA
    distill_queue = SCHEMA.split("create view distill_queue as")[1].split(";")[0]
    assert "latest_triage" in distill_queue
    assert "join triage_log" not in distill_queue, \
        "a re-triaged paper would be distilled twice in one run"


def test_triage_log_records_the_judge_as_one_string():
    assert "alter table triage_log add column if not exists method text;" in SCHEMA
    # and old rows get the pair they already had in two columns
    assert "set method = coalesce(model, 'unknown') || '@' || coalesce(prompt_sha" in SCHEMA
    source = (ROOT / "pipeline" / "triage.py").read_text()
    # three writers: the rule backfill, the daily judged row, and the re-triage
    assert source.count("prompt_sha, method)") == 3, \
        "every insert into triage_log carries the method, or the column is half true"


def test_no_consumer_joins_triage_log_expecting_one_row_per_paper():
    for path in (ROOT / "pipeline" / "weekly.py", ROOT / "mcp" / "server.py"):
        source = path.read_text()
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith(("join triage_log", "left join triage_log")):
                raise AssertionError(f"{path.name}: {stripped} returns a re-triaged "
                                     "paper once per decision it has ever had")


def test_the_weekly_triaged_count_is_papers_and_not_decisions():
    # Re-triage appends a second row per paper. Counting rows would let the issue
    # say it triaged 47 papers it had already triaged in September.
    weekly = (ROOT / "pipeline" / "weekly.py").read_text()
    stat = weekly.split("(select count(*) from triage_log t")[1].split("),")[0]
    assert "not exists" in stat and "e.paper_id = t.paper_id" in stat


# ---------------- the repair of the 18 invisible claims ----------------

def test_the_repair_fixes_a_misspelling_and_leaves_an_invention_alone():
    fixed, untouched = backfill_topics.repair(
        ["post\u2011training", "reward-design"], topics)
    assert fixed == ["post-training", "reward-design"]
    assert untouched == ["reward-design"]


def test_the_repair_collapses_two_spellings_of_one_tag():
    fixed, _ = backfill_topics.repair(["post\u2011training", "post-training"], topics)
    assert fixed == ["post-training"]


def test_the_repair_is_a_fixed_point_which_is_what_makes_it_idempotent():
    once, _ = backfill_topics.repair(["Post\u2011Training", "memory", "training"], topics)
    twice, _ = backfill_topics.repair(once, topics)
    assert once == twice


def test_the_repair_job_has_no_model_secret_and_therefore_no_bill():
    source = (ROOT / "pipeline" / "backfill_topics.py").read_text()
    assert "moonshot" not in source and "groq" not in source
    assert source.count('Secret.from_name("neon")') == 2
    assert "def count" in source and "def backfill" in source
