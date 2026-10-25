"""The slow loop's trigger: which claims the current prompt has never read.

    python3 -m pytest tests/test_rejudge_queue.py -q

The second half of slice 5 in `docs/product/graph-quality.md`. Slice 5 gave a
second opinion somewhere to land and nothing a way to ask for one, and the
design doc named the gap in its own words: "nothing re-queues a judged claim
yet ... the loop needs a trigger that picks claims whose newest opinion
predates the current prompt sha".

Three things have to be true, and they fail in three different ways.

**The trigger has to terminate.** A pass that found no relation writes no edge,
so a trigger that reads `claim_links` cannot tell "October read this claim and
found nothing" from "October has never read it". That claim then comes back on
every run and pays for a model call every time, which is the one failure here
that costs money rather than correctness. `claim_judgments` records the pass
instead of the finding, and the empty passes are the rows that matter.

**It has to key on the prompt and not on `method`.** `method` is `model@sha`,
and the model is whichever provider answered: Moonshot normally, Groq's free
tier when Moonshot did not. A trigger keyed on `method` therefore re-judges the
whole corpus the first time the fallback answers, and again when the primary
comes back, forever, and every pass of it is a bill. The prompt is the judge's
instructions and the model is a capacity accident.

**It must not displace a first opinion.** An unjudged claim has no edges at
all, so judging it can only add to the graph. Re-judgment takes the slots the
fresh queue leaves and never a slot it wanted, so turning the loop on cannot
move this job's spend or slow the drain.

The split is the same one tests/test_latest_links.py uses and for the same
reason. The first half runs everywhere, including a CI with no database. The
second half starts a PostgreSQL cluster when it can find one, so it is the
stronger evidence and the less available one, and a green run that skipped it
has proved the structure and not the behaviour.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import sql_schema as ss  # noqa: E402

SCHEMA_PATH = ROOT / "db" / "schema.sql"
SCHEMA = SCHEMA_PATH.read_text()
INTERPRET = (ROOT / "pipeline" / "interpret.py").read_text()


def interpret_module():
    """pipeline/interpret.py's module-level names, with modal stubbed out.

    The file builds a `modal.Image` and decorates its functions with
    `@app.function`, so importing it for real needs the modal package. Nothing
    this suite asserts about touches modal: `REJUDGE_QUEUE_SQL` is a string and
    `rejudge_budget` is arithmetic. So a stub goes into `sys.modules` and the
    file is imported the ordinary way, which keeps the test reading the real
    module rather than a rewritten copy of it.
    """
    import importlib.util
    import types

    class _Stub:
        """Chains for `modal.Image.debian_slim().pip_install(...)`, and when
        called as a decorator gives the function back rather than swallowing it."""

        def __getattr__(self, _):
            return self

        def __call__(self, *a, **k):
            if len(a) == 1 and not k and callable(a[0]):
                return a[0]
            return self

    stub = types.ModuleType("modal")
    stub.__getattr__ = lambda _: _Stub()           # type: ignore[attr-defined]
    for name in ("Image", "App", "Secret", "Cron", "Period", "Volume", "Dict"):
        setattr(stub, name, _Stub())

    saved = sys.modules.get("modal")
    sys.modules["modal"] = stub
    try:
        spec = importlib.util.spec_from_file_location(
            "interpret_under_test", ROOT / "pipeline" / "interpret.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if saved is None:
            sys.modules.pop("modal", None)
        else:
            sys.modules["modal"] = saved


# ------------------------------------------------- the schema and the queries

def test_claim_judgments_records_the_pass_and_not_the_finding():
    """The table has to carry an edge count, including zero."""
    body = ss.table_body("claim_judgments")
    assert "claim_id" in body
    assert "prompt_sha" in body
    assert re.search(r"edges\s+integer", body), (
        "the pass needs to record how many edges it wrote, because 0 is the "
        "answer that makes the trigger terminate")


def test_the_key_is_the_claim_and_the_prompt():
    body = ss.table_body("claim_judgments")
    assert re.search(r"primary key\s*\(\s*claim_id\s*,\s*prompt_sha\s*\)", body), (
        "one row per claim per prompt: that is what makes re-running the same "
        "prompt idempotent instead of a second bill")


def test_the_trigger_keys_on_the_prompt_and_not_on_the_method():
    """The regression that would cost money, asserted on the query itself."""
    sql = interpret_module().REJUDGE_QUEUE_SQL
    assert "prompt_sha" in sql
    assert "j.method" not in sql, (
        "method is model@sha and the model is whichever provider answered, so "
        "keying the trigger on it re-judges the corpus every time the fallback "
        "answers")


def test_the_trigger_resolves_against_the_schema():
    """libpg_query, the server's own parser, against db/schema.sql.

    The placeholders are filled with literals of the right shape first: psycopg
    binds them, so the server never sees a `%s` and neither should the parser.
    """
    sql = interpret_module().REJUDGE_QUEUE_SQL
    ss.assert_resolves("REJUDGE_QUEUE_SQL",
                       sql.replace("%s", "'octo1111'", 1).replace("%s", "100"))


def test_the_trigger_is_disjoint_from_the_fresh_queue():
    """A claim must not be able to arrive twice in one run."""
    sql = interpret_module().REJUDGE_QUEUE_SQL
    assert "interpreted_at is not null" in sql, (
        "interpret_queue is `interpreted_at is null`; without the opposite "
        "here a never-judged claim is in both queues at once")


def test_the_trigger_reads_claim_judgments_and_not_claim_links():
    sql = interpret_module().REJUDGE_QUEUE_SQL
    assert "claim_judgments" in sql
    assert "claim_links" not in sql, (
        "an absent edge cannot tell 'read it and found nothing' from 'never "
        "read it', which is the whole reason claim_judgments exists")


def test_latest_judgment_is_one_row_per_claim():
    m = re.search(r"create or replace view latest_judgment as(.*?);", SCHEMA,
                  re.S | re.I)
    assert m, "db/schema.sql creates no latest_judgment view"
    assert "distinct on (claim_id)" in m.group(1), (
        "same shape as latest_triage and latest_links: the current answer is "
        "one row")
    assert "created_at desc" in m.group(1), "recency is the ordering"


# -------------------------------------------------------- the spending policy

@pytest.mark.parametrize("fresh,cap,want", [
    (90, 90, 0),      # today: the fresh queue fills the run, so no re-judgment
    (0, 90, 90),      # the drain is finished, the loop gets the whole run
    (85, 90, 5),      # the leftovers, and only those
    (91, 90, 0),      # never negative, whatever the caller passed
])
def test_rejudge_takes_the_leftovers_and_only_the_leftovers(fresh, cap, want):
    assert interpret_module().rejudge_budget(fresh, cap) == want


def test_the_loop_is_latent_while_the_corpus_is_still_draining():
    """The honest claim this slice ships under, as a number.

    The fresh queue was 2,000-odd deep at the last reading, so a run takes its
    full 90 fresh claims and the trigger returns nothing. That is the correct
    order of work and it is also the reason this change cannot regress
    production today.
    """
    mod = interpret_module()
    assert mod.rejudge_budget(mod.MAX_CLAIMS_PER_RUN, mod.MAX_CLAIMS_PER_RUN) == 0


# ---------------------------------------------- what the run records and says

def test_every_pass_writes_a_judgment_row_including_the_empty_ones():
    assert "insert into claim_judgments" in INTERPRET
    # The insert sits after the if/else on `neighbors`, at the same indentation
    # as the interpreted_at update, so both arms reach it.
    insert = INTERPRET.index("insert into claim_judgments")
    no_neighbors = INTERPRET.index("no_neighbors += 1")
    assert no_neighbors < insert, (
        "a claim with no older neighbor costs no call and still has to be "
        "recorded, or it comes back on every run")


def test_the_judgment_insert_is_idempotent_on_the_same_prompt():
    assert "on conflict (claim_id, prompt_sha) do nothing" in INTERPRET


def test_re_judgment_does_not_restamp_the_first_judgment_marker():
    assert ("update claims set interpreted_at = now() \"\n"
            "                         \"where id = %s and interpreted_at is null"
            ) in INTERPRET or "and interpreted_at is null" in INTERPRET, (
        "moving interpreted_at on a re-judgment dates a September claim to "
        "today, which puts it back in the issue's seven-day sections as new")


def test_the_drain_forecast_counts_first_opinions_only():
    """A re-judgment takes nothing out of the queue, so it is not progress."""
    assert "drain_forecast(max(depth - fresh_seen, 0), fresh_seen)" in INTERPRET, (
        "forecasting the drain off a count that includes re-judgments reports "
        "a queue emptying at a rate nothing is emptying it at")


def test_the_run_says_how_many_of_each_it_did():
    assert "first opinions" in INTERPRET and "second ones" in INTERPRET


def test_the_dry_run_reports_the_re_judgment_depth():
    """`drain` spends nothing and is where the loop is observed from."""
    drain = INTERPRET[INTERPRET.index("def drain()"):]
    assert "re-judgment:" in drain
    assert "the graph currently reflects" in drain
    assert "latest_judgment" in drain


# ------------------------------------------------------ against a real server

def pg_bin() -> str | None:
    """A PostgreSQL server's bin directory, or None. Same probe as slice 5's."""
    if shutil.which("initdb") and shutil.which("psql"):
        return ""
    for base in sorted(Path("/usr/lib/postgresql").glob("*/bin"), reverse=True):
        if (base / "initdb").exists() and (base / "psql").exists():
            return str(base)
    return None


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    """A throwaway cluster with db/schema.sql loaded, or a skip.

    Loaded twice, because `psql -f db/schema.sql` is how this database is
    migrated and the backfill in this slice is two INSERTs, which is the shape
    that is easiest to write non-idempotently.
    """
    base = pg_bin()
    if base is None:
        pytest.skip("no PostgreSQL server on this host (CI runs none)")
    env = {**os.environ,
           "PATH": f"{base}:{os.environ['PATH']}" if base else os.environ["PATH"]}
    data = tmp_path_factory.mktemp("pgdata") / "data"
    sock = data.parent

    def run(*argv, **kw):
        return subprocess.run(argv, env=env, capture_output=True, text=True, **kw)

    made = run("initdb", "-D", str(data), "-U", "postgres", "--auth=trust")
    if made.returncode != 0:
        pytest.skip(f"initdb would not run here: {made.stderr[-300:]}")
    port = "55441"
    started = run("pg_ctl", "-D", str(data), "-l", str(data / "server.log"),
                  "-o", f"-p {port} -k {sock} -c listen_addresses=''",
                  "-w", "start")
    if started.returncode != 0:
        pytest.skip(f"no cluster: {started.stderr[-300:]}")
    try:
        made_db = run("createdb", "-h", str(sock), "-p", port, "-U", "postgres",
                      "alexandria_rejudge")
        assert made_db.returncode == 0, made_db.stderr

        def psql(sql: str, *, tuples=True):
            argv = ["psql", "-h", str(sock), "-p", port, "-U", "postgres",
                    "-d", "alexandria_rejudge", "-v", "ON_ERROR_STOP=1", "-q"]
            if tuples:
                argv += ["-At"]
            done = run(*argv, "-c", sql)
            assert done.returncode == 0, f"{sql[:80]}\n{done.stderr}"
            return done.stdout.strip()

        def migrate():
            """Apply db/schema.sql, the way this database is actually migrated.

            Exposed to the tests because the backfill in this slice is the half
            that can only be observed against rows that already existed when it
            ran. Loading the schema into an empty cluster proves it parses and
            nothing else.
            """
            loaded = run("psql", "-h", str(sock), "-p", port, "-U", "postgres",
                         "-d", "alexandria_rejudge", "-v", "ON_ERROR_STOP=1",
                         "-q", "-f", str(SCHEMA_PATH))
            assert loaded.returncode == 0, (
                f"db/schema.sql will not load: {loaded.stderr[-800:]}")

        for _ in range(2):              # idempotence is part of the contract
            migrate()
        psql.migrate = migrate
        yield psql
    finally:
        run("pg_ctl", "-D", str(data), "-m", "immediate", "stop")


SEPT = "sept0000"
OCT = "octo1111"


@pytest.fixture
def corpus(db):
    """Three claims in the three states the trigger has to tell apart.

    - 10 and 20: a pair September judged, so there is an edge and a sha.
    - 30: judged by September and it found nothing, so there is no edge.
    - 40: never judged at all, so it belongs to the fresh queue.

    The rows go in with `claim_judgments` empty and then the schema is applied
    again, because that is the actual shape of this migration: a database that
    already holds a judged corpus, meeting the table for the first time. A
    fixture that inserted the judgment rows itself would test the trigger
    against data the backfill never had to recover.
    """
    db("""
        delete from claim_judgments; delete from claim_links;
        delete from claims; delete from papers;
        insert into papers (id, source, title, url) values
          ('p1','arxiv','The older paper','http://example.test/1'),
          ('p2','arxiv','The newer paper','http://example.test/2');
        insert into claims (id, paper_id, claim, embedding, interpreted_at) values
          (10,'p1','Chain of thought always helps.',
               array_fill(0.1::real, array[1024])::vector, '2026-09-01 10:00+00'),
          (20,'p2','Chain of thought does not help on short tasks.',
               array_fill(0.2::real, array[1024])::vector, '2026-09-01 10:00+00'),
          (30,'p2','An unrelated claim about FFT kernels.',
               array_fill(0.3::real, array[1024])::vector, '2026-09-01 10:00+00'),
          (40,'p2','A claim nobody has judged yet.',
               array_fill(0.4::real, array[1024])::vector, null);
        insert into claim_links
            (from_claim,to_claim,relation,confidence,method,created_at)
        values (20,10,'contradicts',0.9,'kimi-k2.6@%s','2026-09-01 10:00+00');
    """ % SEPT, tuples=False)
    db.migrate()                 # the backfill meets a corpus that predates it
    return db


def due(db, sha):
    """The trigger's own query, run at a prompt sha. Returns claim ids."""
    sql = interpret_module().REJUDGE_QUEUE_SQL.replace(
        "%s", f"'{sha}'", 1).replace("%s", "100")
    out = db(f"select id from ({sql}) q")
    return [int(line) for line in out.splitlines() if line]


def test_the_backfill_recovers_the_sha_from_the_edges(corpus):
    """September's pass is history and it is in `method`, so it is recoverable."""
    assert corpus("select prompt_sha from claim_judgments where claim_id = 20") == SEPT
    assert corpus("select edges from claim_judgments where claim_id = 20") == "1"


def test_the_backfill_dates_the_pass_when_it_happened(corpus):
    """Stamping a recovered pass with now() would make the history a lie."""
    assert corpus("select created_at::date from claim_judgments "
                  "where claim_id = 20") == "2026-09-01"


def test_an_interpreted_claim_with_no_edge_is_recorded_as_unknown(corpus):
    """Claim 30 was judged and found nothing, so it has no sha to recover."""
    assert corpus("select prompt_sha from claim_judgments where claim_id = 30") == "unknown"
    assert corpus("select edges from claim_judgments where claim_id = 30") == "0"


def test_a_never_judged_claim_gets_no_backfill_row(corpus):
    assert corpus("select count(*) from claim_judgments where claim_id = 40") == "0"


def test_september_does_not_re_judge_what_september_already_read(corpus):
    """The money test. Claim 20 is done under September and stays done."""
    assert 20 not in due(corpus, SEPT)


def test_october_is_due_everything_september_read(corpus):
    assert sorted(due(corpus, OCT)) == [10, 20, 30]


def test_the_claim_that_found_nothing_comes_back_once_and_then_never(corpus):
    """Claim 30 is the one a claim_links-based trigger would loop on forever."""
    assert 30 in due(corpus, OCT)
    corpus("insert into claim_judgments (claim_id, prompt_sha, method, edges) "
           f"values (30, '{OCT}', 'kimi-k2.6@{OCT}', 0)", tuples=False)
    assert 30 not in due(corpus, OCT), (
        "an empty pass has to close the claim out, or the loop pays a model "
        "call for it on every run forever")


def test_the_fresh_queue_and_the_trigger_never_hold_the_same_claim(corpus):
    """Claim 40 is unjudged, so it is the fresh queue's and not the loop's."""
    fresh = [int(x) for x in corpus(
        "select id from interpret_queue order by id").splitlines() if x]
    assert fresh == [40]
    assert not set(fresh) & set(due(corpus, OCT))


def test_the_fallback_answering_does_not_re_judge_the_corpus(corpus):
    """The second money test, and the one the design would have got wrong.

    September's edge was drawn by Moonshot. Groq answering under the same
    prompt is the same judge reading the same instructions, so nothing is due.
    """
    corpus(f"""
        insert into claim_links
            (from_claim,to_claim,relation,confidence,method,created_at)
        values (20,10,'contradicts',0.9,'llama-3.3-70b@{SEPT}',
                '2026-09-02 10:00+00')
    """, tuples=False)
    assert 20 not in due(corpus, SEPT), (
        "two providers under one prompt is one opinion; treating it as two "
        "re-judges the whole corpus whenever the fallback answers")


def test_a_second_opinion_closes_the_claim_under_the_new_prompt(corpus):
    """The loop's full cycle, on rows: due, judged, not due."""
    assert 20 in due(corpus, OCT)
    corpus(f"""
        insert into claim_links
            (from_claim,to_claim,relation,confidence,method,created_at)
        values (20,10,'supports',0.8,'kimi-k2.6@{OCT}','2026-10-25 10:00+00');
        insert into claim_judgments (claim_id, prompt_sha, method, edges)
        values (20, '{OCT}', 'kimi-k2.6@{OCT}', 1);
    """, tuples=False)
    assert 20 not in due(corpus, OCT)
    assert corpus("select relation from latest_links "
                  "where from_claim = 20 and to_claim = 10") == "supports"


def test_latest_judgment_reports_the_newest_pass(corpus):
    corpus(f"""
        insert into claim_judgments (claim_id, prompt_sha, method, edges, created_at)
        values (20, '{OCT}', 'kimi-k2.6@{OCT}', 1, '2026-10-25 10:00+00')
    """, tuples=False)
    assert corpus("select prompt_sha from latest_judgment "
                  "where claim_id = 20") == OCT
    assert corpus("select count(*) from latest_judgment "
                  "where claim_id = 20") == "1"


def test_the_same_prompt_cannot_record_two_passes_for_one_claim(corpus):
    """The key, on rows: a repeated pass is a no-op rather than a duplicate."""
    corpus(f"""
        insert into claim_judgments (claim_id, prompt_sha, method, edges)
        values (10, '{OCT}', 'kimi-k2.6@{OCT}', 0)
            on conflict (claim_id, prompt_sha) do nothing;
        insert into claim_judgments (claim_id, prompt_sha, method, edges)
        values (10, '{OCT}', 'kimi-k2.6@{OCT}', 0)
            on conflict (claim_id, prompt_sha) do nothing;
    """, tuples=False)
    assert corpus("select count(*) from claim_judgments "
                  f"where claim_id = 10 and prompt_sha = '{OCT}'") == "1"


def test_the_marker_update_leaves_a_re_judged_claim_dated_as_it_was(corpus):
    """The exact statement the run writes, against a claim it re-judges."""
    corpus("update claims set interpreted_at = now() "
           "where id = 20 and interpreted_at is null", tuples=False)
    assert corpus("select interpreted_at::date from claims where id = 20") == "2026-09-01"
    corpus("update claims set interpreted_at = now() "
           "where id = 40 and interpreted_at is null", tuples=False)
    assert corpus("select interpreted_at is not null from claims where id = 40") == "t"
