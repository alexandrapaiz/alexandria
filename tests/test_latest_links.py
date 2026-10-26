"""The slow loop's read path: `latest_links`, and the reads that follow it.

    python3 -m pytest tests/test_latest_links.py -q

Slice 5 of `docs/product/graph-quality.md`. Re-judgment appends a second
opinion, so a pair can hold more than one verdict and exactly one of them is
current. Two things have to be true for that to work, and they fail
differently, so they are tested differently.

**The key has to let a second opinion exist.** Until 2026-10-24 it did not:
`claim_links` keyed the pair and the relation, so an October prompt that
agreed with September's collided and `pipeline/interpret.py`'s `on conflict do
nothing` dropped it in silence. That is a fact about a real server and no
amount of parsing finds it, which is why the second half of this file starts a
PostgreSQL cluster when it can find one.

**Every read has to ask for the current verdict.** That is a fact about
statements, and the parser catches it: the first half resolves the SQL in
`pipeline/weekly.py` against `db/schema.sql` with libpg_query, the same parser
the server uses. The digest had no parser-level guard over its own queries
before this file, only assertions that a substring appeared in the source.

The split is deliberate. The first half runs everywhere, including a CI that
has no database. The second half skips where there is no server, so it is the
stronger evidence and the less available one, and a green run that skipped it
has proved the structure and not the behaviour.
"""

import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))

import sql_schema as ss  # noqa: E402

SCHEMA_PATH = ROOT / "db" / "schema.sql"
SCHEMA = SCHEMA_PATH.read_text()
WEEKLY = (ROOT / "pipeline" / "weekly.py").read_text()


# --------------------------------------------------------- the schema, parsed

def test_latest_links_exists_and_is_one_row_per_pair():
    """One current answer per pair is the whole point, so the shape is pinned.

    `distinct on (from_claim, to_claim)` with a matching leading ORDER BY is
    what makes that true in Postgres. A `distinct on` whose ORDER BY starts
    somewhere else is an error the server raises, and one that merely orders
    differently after the leading keys returns a different row, so both halves
    are asserted rather than the name alone.
    """
    relations, _ = ss.schema_names()
    assert "latest_links" in relations, "db/schema.sql creates no latest_links"

    body = re.search(
        r"create or replace view latest_links as(.*?);", SCHEMA, re.S)
    assert body, "latest_links is not a CREATE OR REPLACE VIEW"
    sql = " ".join(body.group(1).split())
    assert "distinct on (from_claim, to_claim)" in sql
    assert "order by from_claim, to_claim, created_at desc" in sql


def test_the_view_is_recency_and_not_alphabetical_method_order():
    """`method desc` must not outrank `created_at desc`.

    The methods are model@sha and a sha sorts alphabetically, so a view that
    ranked by method would hand back whichever prompt hashed highest and call
    it current. It would also pass every other assertion in this file.
    """
    sql = " ".join(re.search(
        r"create or replace view latest_links as(.*?);",
        SCHEMA, re.S).group(1).split())
    keys = sql.split("order by", 1)[1]
    assert keys.index("created_at desc") < keys.index("method desc")


def test_deprecated_claims_reads_the_current_verdict():
    """ADR-8's deprecation list is slice 5's named done-condition."""
    body = re.search(
        r"create or replace view deprecated_claims as(.*?);", SCHEMA, re.S)
    assert body
    sql = body.group(1)
    assert "latest_links" in sql, (
        "deprecated_claims must read latest_links: a contradiction a later "
        "prompt withdrew is not a deprecation")
    assert "claim_links" not in sql


def test_a_second_opinion_is_keyed_by_the_method_that_gave_it():
    """And NULL-folded, or the unattributed era cannot be keyed at all."""
    assert re.search(
        r"create unique index if not exists claim_links_opinion_idx\s*\n"
        r"\s*on claim_links \(from_claim, to_claim, relation, "
        r"coalesce\(method, ''\)\);", SCHEMA), (
        "no NULL-folded unique index over the opinion")


def test_the_old_pair_and_relation_key_is_dropped():
    """The declaration still carries it, so the migration has to remove it.

    `create table if not exists` is a no-op against the production database,
    so a key dropped only in the declaration is a key that is still there.
    """
    assert "primary key (from_claim, to_claim, relation)" in SCHEMA, (
        "the declaration is the record of what fresh databases got")
    assert re.search(
        r"alter table claim_links drop constraint claim_links_pkey", SCHEMA), (
        "nothing drops the key that silences the second opinion")
    migration = SCHEMA.split("create unique index if not exists "
                             "claim_links_opinion_idx", 1)[1]
    assert "drop constraint claim_links_pkey" in migration, (
        "the key must be dropped after the index that replaces it, never "
        "before: there must be no window where the table has neither")


# ------------------------------------------- the digest's SQL, parsed in full

def weekly_queries() -> dict[str, str]:
    """Every literal SQL statement `pipeline/weekly.py` hands to the server.

    Read out of the AST rather than by regex over the source, so a query that
    moves or gains a line is still collected. Named by the line it starts on,
    which is what a failure needs in order to be findable. `%s` is psycopg's
    placeholder and `$1` is what the server sees.
    """
    found = {}
    for node in ast.walk(ast.parse(WEEKLY)):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "execute"):
            continue
        if node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            found[f"weekly.py:{node.lineno}"] = \
                node.args[0].value.replace("%s", "$1")
    return found


def test_the_digest_asks_for_enough_queries_to_be_worth_checking():
    """A guard that collects nothing passes forever."""
    assert len(weekly_queries()) >= 15


@pytest.mark.parametrize("name", sorted(weekly_queries()))
def test_every_query_the_digest_runs_resolves_against_the_schema(name):
    ss.assert_resolves(name, weekly_queries()[name])


@pytest.mark.parametrize("marker,why", [
    ("left join latest_links l on l.from_claim = c.id",
     "the relation list beside each new claim would print two verdicts on one "
     "pair as though the judge held both at once"),
    ("join latest_links l on l.to_claim = c.id and l.relation = 'supports'",
     "two prompts agreeing is one support, and on claim_links it reads as the "
     "two the 2+ list requires"),
])
def test_the_digest_counts_current_verdicts(marker, why):
    assert marker in WEEKLY, why


def test_the_two_seven_day_sections_read_the_view():
    """`superseded` and `deprecated` both date a pair by its current verdict.

    On `claim_links` a re-judgment gives an old pair a new `created_at`, so a
    verdict reached in September would reappear as this week's news.
    """
    for section in ("superseded", "deprecated"):
        block = re.search(
            rf"{section} = conn\.execute\(\s*\"\"\"(.*?)\"\"\"", WEEKLY, re.S)
        assert block, f"no {section} query in pipeline/weekly.py"
        assert "from latest_links l" in block.group(1), (
            f"the {section} section still reads every verdict ever given")


def test_the_issues_own_headline_counts_connections_and_not_opinions():
    """`prompts/digest.md` promises a subscriber connections between findings.

    Counting rows would let a prompt re-run inflate it, which is the exact
    class of flattery the owner's 2026-09-25 directive on the stats line
    ruled out.
    """
    assert "having min(created_at) > now() - interval '7 days'" in WEEKLY
    assert "connections_drawn" in WEEKLY


# ------------------------------------------------ the instrument's own metric

def test_self_contradiction_is_grouped_by_the_opinion_not_the_pair():
    """Slice 1 is the instrument every later slice is measured against.

    Grouped by the pair, this count turns every changed mind into a corruption
    report the moment the slow loop runs, which is the instrument breaking on
    the thing it was built to measure.
    """
    import graph_audit as ga
    integrity = " ".join(ga.QUERIES["integrity"].split())
    assert "group by from_claim, to_claim, coalesce(method, '')" in integrity
    contradiction = " ".join(ga.QUERIES["contradiction"].split())
    assert "from claim_links" not in contradiction, (
        "the first three counts must reconcile with deprecated_claims, which "
        "reads latest_links")


# ------------------------------------------------------ against a real server

def pg_bin() -> str | None:
    """A PostgreSQL server's bin directory, or None.

    `psql` alone is not enough: the client ships without the server on most
    hosts, and this needs `initdb`. The company host has one and this org runs
    no database in CI, so the tests below are evidence where they run and a
    skip where they do not.
    """
    if shutil.which("initdb") and shutil.which("psql"):
        return ""
    for base in sorted(Path("/usr/lib/postgresql").glob("*/bin"), reverse=True):
        if (base / "initdb").exists() and (base / "psql").exists():
            return str(base)
    return None


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    """A throwaway cluster with db/schema.sql loaded, or a skip.

    The schema is loaded twice on purpose. `psql -f db/schema.sql` is how this
    database is actually migrated, every run of it has to be a no-op after the
    first, and the migration in this slice drops a constraint, which is the
    shape that is easiest to write non-idempotently.
    """
    base = pg_bin()
    if base is None:
        pytest.skip("no PostgreSQL server on this host (CI runs none)")
    env = {**os.environ, "PATH": f"{base}:{os.environ['PATH']}" if base
           else os.environ["PATH"]}
    data = tmp_path_factory.mktemp("pgdata") / "data"
    sock = data.parent

    def run(*argv, **kw):
        return subprocess.run(argv, env=env, capture_output=True, text=True,
                              **kw)

    made = run("initdb", "-D", str(data), "-U", "postgres", "--auth=trust")
    if made.returncode != 0:
        pytest.skip(f"initdb would not run here: {made.stderr[-300:]}")
    port = "55439"
    started = run("pg_ctl", "-D", str(data), "-l", str(data / "server.log"),
                  "-o", f"-p {port} -k {sock} -c listen_addresses=''",
                  "-w", "start")
    if started.returncode != 0:
        pytest.skip(f"no cluster: {started.stderr[-300:]}")
    try:
        made_db = run("createdb", "-h", str(sock), "-p", port, "-U", "postgres",
                      "alexandria_slice5")
        assert made_db.returncode == 0, made_db.stderr

        def psql(sql: str, *, tuples=True):
            argv = ["psql", "-h", str(sock), "-p", port, "-U", "postgres",
                    "-d", "alexandria_slice5", "-v", "ON_ERROR_STOP=1", "-q"]
            if tuples:
                argv += ["-At"]
            done = run(*argv, "-c", sql)
            assert done.returncode == 0, f"{sql[:80]}\n{done.stderr}"
            return done.stdout.strip()

        for _ in range(2):            # idempotence is part of the contract
            loaded = run("psql", "-h", str(sock), "-p", port, "-U", "postgres",
                         "-d", "alexandria_slice5", "-v", "ON_ERROR_STOP=1",
                         "-q", "-f", str(SCHEMA_PATH))
            assert loaded.returncode == 0, (
                f"db/schema.sql will not load: {loaded.stderr[-800:]}")
        yield psql
    finally:
        run("pg_ctl", "-D", str(data), "-m", "immediate", "stop")


@pytest.fixture
def pair(db):
    """Two claims and September's verdict: claim 20 contradicts claim 10."""
    db("""
        delete from claim_links; delete from claims; delete from papers;
        insert into papers (id, source, title, url) values
          ('p1','arxiv','The older paper','http://example.test/1'),
          ('p2','arxiv','The newer paper','http://example.test/2');
        insert into claims (id, paper_id, claim) values
          (10,'p1','Chain of thought always helps.'),
          (20,'p2','Chain of thought does not help on short tasks.');
        insert into claim_links
            (from_claim,to_claim,relation,confidence,method,created_at)
        values (20,10,'contradicts',0.9,'kimi-k2.6@sept0000',
                '2026-09-01 10:00+00');
    """, tuples=False)
    return db


def opinion(db, relation, method, when, confidence="0.95"):
    return db(f"""
        insert into claim_links
            (from_claim,to_claim,relation,confidence,method,created_at)
        values (20,10,'{relation}',{confidence},'{method}','{when}')
        on conflict do nothing
        returning 1
    """)


def test_an_agreeing_second_opinion_is_recorded(pair):
    """The defect this slice exists for: it used to insert zero rows.

    A new prompt confirming an old verdict is the single most useful thing the
    slow loop can find, and the old key was built so that it was the one
    outcome that could not be written down.
    """
    assert opinion(pair, "contradicts", "kimi-k2.6@octo1111",
                   "2026-10-24 10:00+00") == "1", \
        "the agreeing second opinion was dropped on conflict"
    assert pair("select count(*) from claim_links "
                "where from_claim=20 and to_claim=10") == "2"
    assert pair("select count(*) from latest_links "
                "where from_claim=20 and to_claim=10") == "1", \
        "two rows, and exactly one current answer"


def test_re_running_the_same_method_stays_idempotent(pair):
    """`on conflict do nothing` still has a job: the same judge, twice."""
    opinion(pair, "contradicts", "kimi-k2.6@octo1111", "2026-10-24 10:00+00")
    assert opinion(pair, "contradicts", "kimi-k2.6@octo1111",
                   "2026-10-24 10:00+00") == "", "a re-run duplicated a row"
    assert pair("select count(*) from claim_links "
                "where from_claim=20 and to_claim=10") == "2"


def test_deprecation_follows_the_newest_verdict(pair):
    """Slice 5's done-condition, both directions.

    September says claim 10 is contradicted. October withdraws it. The old
    verdict stays on the record and stops being the answer.
    """
    assert pair("select id from deprecated_claims") == "10"
    opinion(pair, "supports", "kimi-k2.6@octo1111", "2026-10-24 10:00+00")
    assert pair("select relation from latest_links "
                "where from_claim=20 and to_claim=10") == "supports"
    assert pair("select count(*) from deprecated_claims") == "0", \
        "a contradiction a later prompt withdrew is not a deprecation"
    assert pair("select count(*) from claim_links where relation='contradicts'"
                ) == "1", "nothing is edited and nothing is deleted"


def test_a_re_contradiction_deprecates_again(pair):
    """And the withdrawal is not sticky either. The newest row wins, always."""
    opinion(pair, "supports", "kimi-k2.6@octo1111", "2026-10-24 10:00+00")
    opinion(pair, "contradicts", "kimi-k2.6@novo2222", "2026-11-02 10:00+00")
    assert pair("select id from deprecated_claims") == "10"


def test_the_unattributed_era_folds_to_one_opinion(pair):
    """NULL is never equal to itself in a key, so the index folds it.

    Edges drawn before `method` existed all read as one opinion, which is the
    honest reading: nothing records who drew them.
    """
    db = pair
    db("insert into claims (id,paper_id,claim) values (30,'p2','A third.')",
       tuples=False)
    first = db("insert into claim_links (from_claim,to_claim,relation,method) "
               "values (30,10,'supports',null) on conflict do nothing "
               "returning 1")
    again = db("insert into claim_links (from_claim,to_claim,relation,method) "
               "values (30,10,'supports',null) on conflict do nothing "
               "returning 1")
    assert (first, again) == ("1", ""), \
        "an unattributed edge must insert once and never twice"


def test_two_prompts_agreeing_is_one_support_not_two(pair):
    """The shape of the digest's 2+ supports list, on real rows.

    Counting `claim_links` here would promote one claim pair into a list whose
    only entry criterion is that two different claims support it.
    """
    db = pair
    db("""
        insert into claims (id,paper_id,claim) values (40,'p2','A fourth.');
        delete from claim_links;
        insert into claim_links (from_claim,to_claim,relation,confidence,method,created_at) values
          (40,10,'supports',0.9,'kimi-k2.6@sept0000','2026-09-01 10:00+00'),
          (40,10,'supports',0.9,'kimi-k2.6@octo1111','2026-10-24 10:00+00');
    """, tuples=False)
    counted = "select count(*) from {} where to_claim=10 and relation='supports'"
    assert db(counted.format("claim_links")) == "2"
    assert db(counted.format("latest_links")) == "1", \
        "one pair, judged twice, is one support"


def test_a_changed_mind_is_not_reported_as_corruption(pair):
    """The audit's integrity metric, run against a real changed mind.

    Grouped by the pair this returns 1 and the audit calls the slow loop
    corrupt. Grouped by the opinion it returns 0 here and still returns 1 for
    the defect it was written for, which is one judge asserting both at once.
    """
    import graph_audit as ga
    sql = ga.QUERIES["integrity"].replace("%s", "5")
    opinion(pair, "supports", "kimi-k2.6@octo1111", "2026-10-24 10:00+00")
    changed_mind = pair(sql).split("|")
    assert changed_mind[-1] == "0", (
        "a pair judged contradicts in September and supports in October is "
        f"re-judgment working, not corruption: {changed_mind}")

    pair("""insert into claim_links
              (from_claim,to_claim,relation,confidence,method,created_at)
            values (20,10,'supports',0.4,'kimi-k2.6@sept0000',
                    '2026-09-01 10:00+00')""", tuples=False)
    both_at_once = pair(sql).split("|")
    assert both_at_once[-1] == "1", (
        "one judge asserting supports and contradicts on one pair is still "
        f"the defect this count was written for: {both_at_once}")
