"""The shortlist: which older claims a new claim is judged against.

    python3 -m pytest tests/test_shortlist.py -q

Slice 2 of `docs/product/graph-quality.md`. The retrieval in
`pipeline/interpret.py` decides the shape of the claim graph, and until this
slice it was an inline SQL string in the middle of the run loop with no test of
any kind behind it. Everything the audit measures about the graph's density is
downstream of six lines nothing had ever exercised.

Four things have to be true of it, and they fail in four different ways.

**It must only look backwards.** ADR-10 says `from_claim` is always the newer
claim and ids are a bigserial, so a candidate has to be a strictly older claim.
This clause predates slice 2 and is tested here because nothing else tested it:
`integrity.backwards` in the audit catches the symptom after the fact, on a
graph that already holds the bad edges.

**It must not offer a claim its own paper's siblings.** Two claims distilled
from one paper are near-neighbors in embedding space almost by construction, so
kNN hands the judge a paper's own siblings first. Those edges are true, cheap
and worth nothing, because the product's promise is this week's finding against
what we already knew. Worse, each one spent one of five slots, so the same
defect that filled the graph with noise also starved it of signal.

**It must be allowed to come back short.** Before the distance floor, `limit
NEIGHBORS` returned NEIGHBORS rows whenever the corpus held that many older
claims, so a genuinely novel claim had its shortlist padded with whatever
happened to be nearest and the run paid a model call to be told `unrelated`
five times. A claim with nothing close enough now gets no shortlist and costs
no call.

**And the limit must still bind when the corpus can fill it.** The floor is a
filter and not a replacement for the cap: a claim sitting in a dense region
gets the NEIGHBORS nearest of them, in distance order, and that is the case the
ceiling metric is watching.

The split is the one tests/test_rejudge_queue.py and tests/test_latest_links.py
use, for the same reason. The first half runs everywhere, including a CI with no
database. The second half starts a PostgreSQL cluster when it can find one, and
it is the only half that can prove any of the four, because every one of them is
a property of what a query returns rather than of what it says. A green run that
skipped it has checked the shape of the SQL and none of its behaviour.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

SCHEMA_PATH = ROOT / "db" / "schema.sql"
INTERPRET = (ROOT / "pipeline" / "interpret.py").read_text()

DIMENSIONS = 1024               # claims.embedding is vector(1024)


def interpret_module():
    """pipeline/interpret.py's module-level names, with modal stubbed out.

    The same loader tests/test_rejudge_queue.py uses and for the same reason:
    the file builds a `modal.Image` and decorates its functions at import time,
    and nothing this suite asserts about touches modal. Importing the real
    module keeps the test reading the shipped query rather than a copy of it.
    """
    import importlib.util
    import types

    class _Stub:
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
            "interpret_shortlist_under_test", ROOT / "pipeline" / "interpret.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if saved is None:
            sys.modules.pop("modal", None)
        else:
            sys.modules["modal"] = saved


interpret = interpret_module()


# ------------------------------------------------------ the query, as written

def test_the_shortlist_is_one_select_and_reads_only_claims():
    """It runs against the production corpus, so it must not be able to write."""
    pglast = pytest.importorskip("pglast")
    statements = pglast.parse_sql(
        interpret.SHORTLIST_SQL.replace("%s", "$1"))
    assert len(statements) == 1
    assert type(statements[0].stmt).__name__ == "SelectStmt"
    relations = set()
    stack = [statements[0]]
    while stack:
        node = stack.pop()
        if type(node).__name__ == "RangeVar":
            relations.add(node.relname)
        for attr in getattr(node, "__slots__", []) or []:
            value = getattr(node, attr, None)
            if hasattr(value, "__slots__"):
                stack.append(value)
            elif isinstance(value, (list, tuple)):
                stack.extend(v for v in value if hasattr(v, "__slots__"))
    assert relations == {"claims"}


def test_all_three_filters_are_in_the_query():
    """Named one at a time, because each one is a different day's bug.

    Asserted on the shipped string rather than on behaviour so that deleting a
    clause fails here even on a host with no database, which is where this
    suite's stronger half does not run.
    """
    sql = interpret.SHORTLIST_SQL
    assert "id < %s" in sql, "the time direction ADR-10 requires"
    assert "paper_id <> %s" in sql, "the same-paper exclusion"
    assert "embedding <=> %s <= %s" in sql, "the distance floor"
    assert "order by embedding <=> %s" in sql, "nearest first"
    assert "limit %s" in sql, "the shortlist's length"


def test_the_floor_is_applied_before_the_limit_and_not_after():
    """A `limit` that runs first would make the floor cosmetic.

    Filtering before the ordering selects the same rows as filtering after it,
    because the filter is monotone in the distance the ordering uses. Filtering
    after the LIMIT does not: it would take the NEIGHBORS nearest and then drop
    the far ones, which is the same count of calls and a shorter list, where the
    point of the floor is to shorten the list the model is sent.
    """
    sql = interpret.SHORTLIST_SQL
    assert sql.index("embedding <=> %s <= %s") < sql.index("limit %s")


def test_the_call_site_passes_the_parameters_the_query_expects():
    """Six placeholders, in one order, and psycopg checks neither.

    A positional query whose caller swaps two parameters is a class of bug the
    type system cannot see: `paper_id` and the floor are both scalars, and
    `(claim_id, embedding)` transposed would compare an id to a vector and
    raise at runtime inside a Modal cron where nobody reads the log.
    """
    assert interpret.SHORTLIST_SQL.count("%s") == 6
    call = INTERPRET[INTERPRET.index("neighbors = conn.execute("):]
    call = call[:call.index(").fetchall()")]
    assert "SHORTLIST_SQL" in call
    for position, argument in enumerate([
            "claim_id", "paper_id", "embedding", "CANDIDATE_MAX_DISTANCE",
            "embedding", "NEIGHBORS"]):
        assert argument in call, argument
    order = [call.index(name) for name in
             ("claim_id", "paper_id", "CANDIDATE_MAX_DISTANCE", "NEIGHBORS")]
    assert order == sorted(order), (
        "the parameters are passed in a different order than SHORTLIST_SQL "
        "reads them")


def test_both_queues_select_the_paper_the_filter_needs():
    """The exclusion is only as good as the column reaching the call site.

    Both queues feed one loop, so a `paper_id` missing from either one is a
    crash on the first re-judgment or on the first fresh claim, whichever the
    run reaches first.
    """
    assert "select id, claim, paper_id, embedding " in INTERPRET
    assert "select c.id, c.claim, c.paper_id, c.embedding" in INTERPRET
    assert "for claim_id, claim_text, paper_id, embedding in queue:" in INTERPRET


def test_the_run_reports_its_own_ceiling():
    """The done-condition the audit cannot reach from a seat sandbox.

    Slice 2 closes when the ceiling metric is under its bound on a fresh
    snapshot, and no seat in this org holds a database credential, so the only
    reading available today is the job's own log. A run that widened the
    shortlist and printed nothing about it would be unverifiable by anyone
    until the credential exists.
    """
    assert "at_ceiling" in INTERPRET
    assert "if len(neighbors) >= NEIGHBORS:" in INTERPRET
    assert "shortlist:" in INTERPRET


# -------------------------------------------- the cost comment, recomputed

def test_the_measured_token_counts_are_not_understated():
    """The cap is set against these two numbers, so they are checked, not read.

    This file's old cost comment said the system prompt was 880 tokens. That
    was true when it was written and had quietly stopped being true, because
    prompts/interpret.md grew and nothing recomputed the comment beside it. The
    cap was therefore set against a request smaller than the one being sent.

    So the constants are measured here with the same tokenizer
    `python3 pipeline/budget.py` uses, against the real prompt and a
    full-length answer at NEIGHBORS candidates. Understating either one
    understates the ceiling the cap was chosen against, which is the direction
    that costs money. Overstating is allowed and is what a ceiling is for, so
    this asserts a floor on each rather than equality.
    """
    import json

    import budget

    prompt = (ROOT / "prompts" / "interpret.md").read_text()
    # A realistic distilled claim at the 400 characters budget.py's own table
    # allows each one. Filler of repeated characters tokenizes far too cheaply
    # to size a request with.
    claim = ("Explicit scratchpad eviction keeps tool-call accuracy within four "
             "percent of baseline past two hundred thousand tokens of agent "
             "context, where recursive summarization loses thirty-one percent "
             "on the same harness and the same model. " * 3)[:400]
    user = interpret.render_candidates(
        claim, [(1000 + i, claim) for i in range(interpret.NEIGHBORS)])
    measured_in = budget.count_tokens(prompt) + budget.count_tokens(user)
    answer = {"results": [{"candidate_id": 1000 + i, "relation": "supports",
                           "confidence": 0.8}
                          for i in range(interpret.NEIGHBORS)]}
    measured_out = budget.count_tokens(json.dumps(answer, indent=2))

    assert interpret.CALL_PROMPT_TOKENS >= measured_in, (
        f"CALL_PROMPT_TOKENS is {interpret.CALL_PROMPT_TOKENS} and the real "
        f"request measures {measured_in}, so the cap is set against a request "
        "smaller than the one the job sends")
    assert interpret.CALL_OUTPUT_TOKENS >= measured_out, (
        f"CALL_OUTPUT_TOKENS is {interpret.CALL_OUTPUT_TOKENS} and a full "
        f"answer measures {measured_out}")
    # And the reservation has to cover a full answer, or the model is cut off
    # mid-JSON and the whole call is wasted rather than merely expensive.
    assert interpret.MAX_COMPLETION_TOKENS > measured_out


def test_every_forecast_reads_the_same_measured_pair():
    """`drain` and `preflight` each carried their own copy of `1_050, 150`.

    Two forecasts and a cap comment with three copies of one pair is three
    places to update and no way to notice when only two of them were. The
    numbers are constants now, and this is what keeps them from being inlined
    again by the next person who finds the constant indirection unnecessary.
    """
    assert "guard.cost_usd(CALL_PROMPT_TOKENS, CALL_OUTPUT_TOKENS" in INTERPRET
    assert "client.calls_within(CAP_USD, CALL_PROMPT_TOKENS," in INTERPRET
    assert "1_050, 150" not in INTERPRET


# ----------------------------------------------------- the query, as it runs
#
# Everything above reads the SQL. Nothing above can tell whether it selects the
# right rows, and all four properties this slice is about are properties of the
# rows. These start a cluster or skip.


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
    """A throwaway cluster with db/schema.sql loaded, or a skip."""
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
    port = "55443"
    started = run("pg_ctl", "-D", str(data), "-l", str(data / "server.log"),
                  "-o", f"-p {port} -k {sock} -c listen_addresses=''",
                  "-w", "start")
    if started.returncode != 0:
        pytest.skip(f"no cluster: {started.stderr[-300:]}")
    try:
        made_db = run("createdb", "-h", str(sock), "-p", port, "-U", "postgres",
                      "alexandria_shortlist")
        assert made_db.returncode == 0, made_db.stderr

        def psql(sql: str, *, tuples=True):
            argv = ["psql", "-h", str(sock), "-p", port, "-U", "postgres",
                    "-d", "alexandria_shortlist", "-v", "ON_ERROR_STOP=1", "-q"]
            if tuples:
                argv += ["-At"]
            done = run(*argv, "-c", sql)
            assert done.returncode == 0, f"{sql[:120]}\n{done.stderr}"
            return done.stdout.strip()

        loaded = run("psql", "-h", str(sock), "-p", port, "-U", "postgres",
                     "-d", "alexandria_shortlist", "-v", "ON_ERROR_STOP=1",
                     "-q", "-f", str(SCHEMA_PATH))
        if loaded.returncode != 0:
            if "vector" in loaded.stderr:
                pytest.skip("no pgvector on this host's PostgreSQL")
            pytest.fail(f"db/schema.sql will not load: {loaded.stderr[-800:]}")
        yield psql
    finally:
        run("pg_ctl", "-D", str(data), "-m", "immediate", "stop")


def vec(*leading: float) -> str:
    """A `vector(1024)` literal whose first components are the ones given.

    Cosine distance only sees direction, so the fixtures below place every
    claim in the plane spanned by the first two components and set the distance
    by one number. `array_fill`, which the other live suites use, cannot be
    used here: every constant vector points the same way, so a corpus built
    from it sits entirely at distance zero and no filter in this query would be
    observable.
    """
    values = list(leading) + [0.0] * (DIMENSIONS - len(leading))
    return "'[" + ",".join(f"{v:g}" for v in values) + "]'::vector"


#: A second component chosen to put `[1, x]` at a known cosine distance from
#: `[1, 0]`: distance is 1 - 1/sqrt(1 + x^2). The live tests assert the
#: distances the database actually computes, so these are a construction and
#: never the thing being trusted.
NEAR = 0.3286        # about 0.05, well inside the floor
MIDDLE = 1.0202      # about 0.30, inside the floor
FAR = 2.2913         # about 0.60, outside the floor of 0.40


@pytest.fixture
def corpus(db):
    """One target claim and five candidates, one for each way out of the list.

    Ids ascend with time, which is what `id < %s` means on a bigserial.

      10  p1  a cross-paper claim just outside the paraphrase band
      20  p1  a cross-paper claim in the middle of the floor's range
      30  p1  a cross-paper claim past the floor
      40  p2  the target's own sibling, and the nearest claim of all
      50  p2  THE TARGET
      60  p1  a cross-paper claim nearer than any of them, written later

    So the answer is [10, 20] and every other row is excluded by exactly one
    clause: 30 by the floor, 40 by the paper, 60 by time. Claim 40 being the
    nearest of all is deliberate rather than incidental. It is what the defect
    looked like in production, where kNN handed the judge a paper's own
    siblings before anything from another paper.
    """
    db(f"""
        delete from claim_judgments; delete from claim_links;
        delete from claims; delete from papers;
        insert into papers (id, source, title, url) values
          ('p1','arxiv','Another paper','http://example.test/1'),
          ('p2','arxiv','The target''s own paper','http://example.test/2');
        insert into claims (id, paper_id, claim, embedding, interpreted_at) values
          (10,'p1','A near cross-paper claim.',   {vec(1, NEAR)},   null),
          (20,'p1','A middling cross-paper claim.',{vec(1, MIDDLE)}, null),
          (30,'p1','A distant cross-paper claim.', {vec(1, FAR)},    null),
          (40,'p2','The target''s own sibling.',   {vec(1, 0.01)},   null),
          (50,'p2','THE TARGET.',                  {vec(1)},         null),
          (60,'p1','A near claim written later.',  {vec(1, 0.05)},   null);
    """, tuples=False)
    return db


def shortlist(db, claim_id, paper_id, embedding, *, floor=None, limit=None):
    """SHORTLIST_SQL itself, at real parameters. Returns candidate ids in order.

    The placeholders are filled positionally and in the order the call site
    passes them, so a query whose parameter order changed without its caller
    changing fails here rather than in a cron.
    """
    module = interpret_module()
    sql = module.SHORTLIST_SQL
    for value in (str(claim_id), f"'{paper_id}'", embedding,
                  str(module.CANDIDATE_MAX_DISTANCE if floor is None else floor),
                  embedding,
                  str(module.NEIGHBORS if limit is None else limit)):
        sql = sql.replace("%s", value, 1)
    return [int(line.split("|", 1)[0])
            for line in db(sql).splitlines() if line.strip()]


def test_the_fixture_sits_where_the_arithmetic_says_it_does(corpus):
    """The construction, checked against the database that will judge it.

    Every test below reads as an assertion about a filter and would read the
    same way if the embeddings were in the wrong places, so the distances come
    first. pgvector computes these, not this file.
    """
    rows = corpus(f"""
        select id, round((embedding <=> {vec(1)})::numeric, 3)
        from claims where id <> 50 order by id
    """)
    distances = {int(i): float(d) for i, d in
                 (line.split("|") for line in rows.splitlines() if line)}
    assert distances[40] < 0.001            # the sibling, nearest of all
    assert 0.04 < distances[10] < 0.06      # near, inside the floor
    assert 0.28 < distances[20] < 0.32      # middling, inside the floor
    assert 0.58 < distances[30] < 0.62      # past the floor of 0.40
    assert distances[60] < distances[10]    # nearer than any candidate, newer


def test_the_shortlist_is_exactly_the_two_candidates_that_survive(corpus):
    assert shortlist(corpus, 50, "p2", vec(1)) == [10, 20]


def test_a_claims_own_siblings_are_never_offered(corpus):
    """The nearest claim in the corpus, and it must not be on the list.

    Dropping `paper_id <> %s` makes this pass with 40 first, which is the
    before-state: the judge's best candidate was a paper agreeing with itself.
    """
    assert 40 not in shortlist(corpus, 50, "p2", vec(1))
    # And the same query run as if the target belonged to the other paper does
    # offer it, so the exclusion is about the paper and not about claim 40.
    assert 40 in shortlist(corpus, 50, "p1", vec(1))


def test_a_newer_claim_is_never_a_candidate(corpus):
    """ADR-10's time direction, which the audit could only catch after the fact."""
    assert 60 not in shortlist(corpus, 50, "p2", vec(1))
    assert shortlist(corpus, 61, "p2", vec(1)) == [60, 10, 20]


def test_a_candidate_past_the_floor_is_not_offered(corpus):
    """And raising the floor lets it back in, so the floor is what excluded it."""
    assert 30 not in shortlist(corpus, 50, "p2", vec(1))
    assert shortlist(corpus, 50, "p2", vec(1), floor=0.9) == [10, 20, 30]


def test_a_claim_with_no_close_neighbour_gets_no_shortlist_at_all(corpus):
    """The call this slice declines to pay for.

    A claim orthogonal to the whole corpus sits at distance 1.0 from every
    older claim, so before the floor it was handed the NEIGHBORS nearest of
    them and asked to relate them. The run loop reads an empty list as "no
    older neighbor", counts it, and makes no call.
    """
    assert shortlist(corpus, 70, "p1", vec(0, 0, 1)) == []


def test_the_shortlist_comes_back_shorter_than_its_limit(corpus):
    """Slice 2's whole point, stated as the one assertion that carries it.

    Five older claims exist and two of them are offered, so the length of this
    list was decided by the corpus and the floor rather than by NEIGHBORS. On
    the old query it was five, every time, for every claim in a corpus this
    size.
    """
    offered = shortlist(corpus, 50, "p2", vec(1))
    assert len(offered) < interpret.NEIGHBORS
    assert len(offered) == 2


@pytest.fixture
def dense(db):
    """Twelve near cross-paper claims, so the limit is what binds again.

    The floor is a filter and not a replacement for the cap. A claim in a dense
    region should get the NEIGHBORS nearest of what is there, in order, and
    that is the state the audit's ceiling metric exists to report.
    """
    rows = ",\n".join(
        f"({100 + i},'p1','Dense claim {i}.',{vec(1, 0.02 * i)},null)"
        for i in range(1, 13))
    db(f"""
        delete from claim_judgments; delete from claim_links;
        delete from claims; delete from papers;
        insert into papers (id, source, title, url) values
          ('p1','arxiv','Another paper','http://example.test/1'),
          ('p2','arxiv','The target''s own paper','http://example.test/2');
        insert into claims (id, paper_id, claim, embedding, interpreted_at)
        values {rows},
          (200,'p2','THE TARGET.',{vec(1)},null);
    """, tuples=False)
    return db


def test_the_limit_still_binds_when_the_corpus_can_fill_it(dense):
    offered = shortlist(dense, 200, "p2", vec(1))
    assert len(offered) == interpret.NEIGHBORS
    # Nearest first, and the two it dropped are the two furthest away.
    assert offered == [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]


def test_the_old_shortlist_would_have_offered_fewer_of_the_same_claims(dense):
    """The raise, measured: ten candidates where five was a Python constant.

    Run at the old limit against the same corpus, the query returns the first
    five of the same ordered list. That is what the ceiling metric was
    reporting, and it is the half of slice 2 that needed no cleverness at all.
    """
    assert shortlist(dense, 200, "p2", vec(1), limit=5) == \
        [101, 102, 103, 104, 105]
