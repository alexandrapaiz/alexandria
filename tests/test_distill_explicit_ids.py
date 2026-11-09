#!/usr/bin/env python3
"""The route to a paper `distill_queue` has already dropped, and the third number.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

`db/schema.sql` defines `distill_queue` as `where p.distilled_at is null`, and
`pipeline/distill.py` holds the only `insert into claims` outside `tests/` and
only ran over that view. So every paper this job has ever read is out of reach
of the only thing that can write a claim about it, permanently, and on
2026-11-02 the research seat measured what that costs: three papers in one
reading-queue block, each distilled from its abstract alone with five claims,
each with an appendix nothing has extracted and nothing could. The gap is the
class rather than the row.

Two seats before that had routed the same request as a missing `NEON_RO_URL`,
which is why the tests below assert on what the route REFUSES as hard as on
what it reads. A route that silently does the wrong half is how the first
version of this was wrong.

Nothing here calls a provider, a database, or Modal.
"""

import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import distill                                                   # noqa: E402

SOURCE = (ROOT / "pipeline" / "distill.py").read_text()
SCHEMA = (ROOT / "db" / "schema.sql").read_text()

TODAY = {"paper": "aaaaaaaaaaaa", "practices": "bbbbbbbbbbbb"}


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None


class FakeConn:
    """Enough of psycopg3 to answer the two selects `explicit_intake` makes.

    Routed on the table named rather than on call order, because the point of
    the route under test is which table it reads: a version that asked
    `distill_queue` would pass a call-ordered fake and fail in production.
    """

    def __init__(self, papers=(), claims=(), columns=("prompt_sha",)):
        self.papers = list(papers)      # (id, title, abstract, decision, source, distilled_at)
        self.claims = list(claims)      # (paper_id, prompt_sha)
        self.columns = set(columns)     # which optional columns the schema has
        self.statements = []

    def execute(self, sql, params=()):
        flat = " ".join(sql.split())
        self.statements.append((flat, params))
        wanted = params[0] if params else []
        if "information_schema.columns" in flat:
            return FakeCursor([(1,)] if params[1] in self.columns else [])
        if "from papers p" in flat:
            # Both halves of `p.id = any(%s) or p.id like any(%s)`. A fake that
            # ran only the first passed a route that reported every firehose
            # paper absent, which is what it did until 2026-11-09.
            likes = params[1] if len(params) > 1 else []
            return FakeCursor([
                r for r in self.papers
                if r[0] in wanted
                or any(r[0].startswith(pat[:-1]) for pat in likes)
            ])
        if "from claims" in flat:
            return FakeCursor([r for r in self.claims if r[0] in wanted])
        raise AssertionError(f"unexpected statement: {flat}")

    def commit(self):
        pass


def test_the_view_is_still_the_thing_this_route_exists_to_bypass():
    """If `distill_queue` ever stops filtering on `distilled_at`, delete this route.

    The whole argument for reading `papers` directly is one clause in the
    schema. Asserting the clause is here keeps the route honest about why it
    exists rather than leaving it as an unexplained second code path.
    """
    view = SCHEMA.split("create view distill_queue as", 1)[1]
    view = view.split(";", 1)[0]
    assert "p.distilled_at is null" in view


def test_a_distilled_paper_is_read_again_when_it_is_named():
    conn = FakeConn(papers=[
        ("arxiv:2609.08371", "EvoSafeHarness", "an abstract", "distill",
         "arxiv", dt.datetime(2026, 9, 14)),
    ])
    rows, lines = distill.explicit_intake(conn, ["arxiv:2609.08371"], shas=TODAY)
    assert [r[0] for r in rows] == ["arxiv:2609.08371"]
    # The shape the walk reads, not the shape the query returned: `distilled_at`
    # is the route's business and the walk must not see a sixth column.
    assert len(rows[0]) == len(distill.INTAKE_COLUMNS) == 5
    assert "2026-09-14" in " ".join(lines)
    assert "read again" in " ".join(lines)


def test_it_reads_papers_and_never_the_view():
    conn = FakeConn(papers=[("a", "t", "x", "distill", "arxiv", None)])
    distill.explicit_intake(conn, ["a"], shas=TODAY)
    asked = " ".join(s for s, _ in conn.statements)
    assert "distill_queue" not in asked


def test_an_id_the_corpus_does_not_carry_is_named_rather_than_dropped():
    conn = FakeConn(papers=[("a", "t", "x", "distill", "arxiv", None)])
    rows, lines = distill.explicit_intake(conn, ["a", "nope"], shas=TODAY)
    assert [r[0] for r in rows] == ["a"]
    said = " ".join(lines)
    assert "nope" in said
    assert "pipeline/ingest.py" in said      # the next command, named


def test_the_same_prompt_twice_is_refused_and_force_overrides():
    conn = FakeConn(
        papers=[("a", "t", "x", "distill", "arxiv", dt.datetime(2026, 10, 1))],
        claims=[("a", "aaaaaaaaaaaa"), ("a", "aaaaaaaaaaaa")],
    )
    rows, lines = distill.explicit_intake(conn, ["a"], shas=TODAY)
    assert rows == []
    assert "--force" in " ".join(lines)
    rows, _ = distill.explicit_intake(conn, ["a"], shas=TODAY, force=True)
    assert [r[0] for r in rows] == ["a"]


def test_a_different_prompt_sha_is_not_the_same_reading():
    """A re-read under a new prompt is the point, so it must not be refused."""
    conn = FakeConn(
        papers=[("a", "t", "x", "distill", "arxiv", dt.datetime(2026, 9, 14))],
        claims=[("a", "999999999999")],
    )
    rows, _ = distill.explicit_intake(conn, ["a"], shas=TODAY)
    assert [r[0] for r in rows] == ["a"]


def test_a_null_prompt_sha_is_not_evidence_that_this_prompt_has_read_it():
    """NULL means 'written before the column existed', which answers nothing.

    This is the design question the handoff attached, answered in the only
    direction that cannot lose a paper: a legacy row costs one request to
    re-read and costs the whole appendix to skip.
    """
    conn = FakeConn(
        papers=[("a", "t", "x", "distill", "arxiv", dt.datetime(2026, 8, 1))],
        claims=[("a", None), ("a", "aaaaaaaaaaaa")],
    )
    rows, _ = distill.explicit_intake(conn, ["a"], shas=TODAY)
    assert [r[0] for r in rows] == ["a"]


def test_the_callers_order_is_the_reading_order_and_duplicates_collapse():
    conn = FakeConn(papers=[
        ("a", "t", "x", "distill", "arxiv", None),
        ("b", "t", "x", "distill", "arxiv", None),
        ("c", "t", "x", "distill", "arxiv", None),
    ])
    rows, _ = distill.explicit_intake(conn, ["c", "a", "c", " b ", ""], shas=TODAY)
    assert [r[0] for r in rows] == ["c", "a", "b"]


def test_a_paper_with_no_triage_row_is_still_readable():
    """The view's own filter is `decision in ('distill','deep_read')`.

    A caller naming an id has made that decision, so the left join defaults the
    decision rather than dropping the row.
    """
    conn = FakeConn(papers=[("a", "t", "x", "distill", "arxiv", None)])
    rows, _ = distill.explicit_intake(conn, ["a"], shas=TODAY)
    assert rows[0][3] == "distill"
    sql = next(s for s, _ in conn.statements if "from papers p" in s)
    assert "left join latest_triage" in sql
    assert "coalesce(t.decision, 'distill')" in sql


def test_an_empty_list_says_so_instead_of_reading_the_corpus():
    conn = FakeConn(papers=[("a", "t", "x", "distill", "arxiv", None)])
    rows, lines = distill.explicit_intake(conn, ["", "  "], shas=TODAY)
    assert rows == []
    assert conn.statements == []
    assert "no ids" in " ".join(lines)


# --- the third number --------------------------------------------------------

def test_threads_deeper_than_a_run_make_the_rest_unreachable():
    lines = distill.unreachable(depth=2922, threads=1380, deep_unreached=61,
                                per_run=14)
    said = " ".join(lines)
    assert "UNREACHABLE" in said
    assert "1542" in said          # 2922 - 1380, the rows no ordering reaches
    assert "61" in said
    assert "--ids" in said         # the route that does reach them


def test_threads_that_fit_inside_a_run_are_not_an_alarm():
    lines = distill.unreachable(depth=100, threads=3, deep_unreached=2,
                                per_run=14)
    said = " ".join(lines)
    assert "UNREACHABLE" not in said
    assert "reachable" in said


def test_no_budget_is_its_own_answer():
    lines = distill.unreachable(depth=100, threads=3, deep_unreached=2, per_run=0)
    assert "nothing drains at all" in " ".join(lines)


def test_the_gauge_stopped_calling_the_cap_a_rate():
    """`MAX_PAPERS_PER_RUN` is the ceiling; the queue take comes off it first.

    The research seat's correction of 2026-11-02. `reading_queue.merge` fronts
    the queue and trims the intake to `max_papers - len(first)`, so the number
    of queued papers a run reads is the cap less the take.
    """
    drain = SOURCE.split("def drain()", 1)[1].split("\ndef ", 1)[0]
    assert "per_run = MAX_PAPERS_PER_RUN\n" not in drain
    assert "taken = min(waiting, queue.MAX_PER_RUN)" in drain
    assert "per_run = max(MAX_PAPERS_PER_RUN - taken, 0)" in drain


def test_the_gauge_asks_how_many_papers_were_read_from_an_abstract():
    """The number the research seat asked for, which no surface could answer."""
    drain = SOURCE.split("def drain()", 1)[1].split("\ndef ", 1)[0]
    assert "count(*) filter (where fulltext_chars is null)" in drain
    assert "from papers where distilled_at is not null" in drain
    assert "distilled from an abstract alone" in drain


def test_the_gauge_counts_deep_reads_that_match_no_thread():
    """`deep` and `threads` overlap, so neither of them is the alarm."""
    drain = SOURCE.split("def drain()", 1)[1].split("\ndef ", 1)[0]
    assert "deep_unreached = conn.execute" in drain
    assert "and not (title ilike any(%s))" in drain
    assert "unreachable(depth, threads, deep_unreached, per_run)" in drain


# --- the entry point ---------------------------------------------------------

def test_the_scheduled_run_cannot_reach_the_explicit_route_by_accident():
    """`paper_ids` defaults to None, so the cron behaves exactly as before."""
    import inspect
    fn = distill.distill
    # Under `modal.App.function` the callable may be wrapped; `get_raw_f` is
    # the documented way back to the body and it is absent when the local
    # stub is in play, which is what CI runs with.
    fn = fn.get_raw_f() if hasattr(fn, "get_raw_f") else fn
    sig = inspect.signature(fn)
    assert sig.parameters["paper_ids"].default is None
    assert sig.parameters["force"].default is False


def test_the_flag_is_spelled_the_way_ingest_spells_it():
    """One name for one idea, across the two entry points a backfill uses."""
    main = SOURCE.split("def main(max_papers", 1)[1].split("\n@app", 1)[0]
    assert "ids: str = \"\"" in main
    ingest = (ROOT / "pipeline" / "ingest.py").read_text()
    assert "def main(ids: str = \"\")" in ingest


def test_a_named_run_does_not_read_the_reading_queue_off_disk():
    """It is skipped, so it is not opened, and no line claims it is missing."""
    main = SOURCE.split("def main(max_papers", 1)[1].split("\n@app", 1)[0]
    named = main.split("if named:", 1)[1].split("else:", 1)[0]
    # Comments are stripped: this asserts about what the branch DOES, and the
    # branch explains in prose why it does not do the thing.
    code = "\n".join(l for l in named.split("\n")
                     if not l.strip().startswith("#"))
    assert "read_text" not in code
    assert "no reading queue at" not in code


def test_the_named_list_is_never_silently_truncated():
    body = SOURCE.split("def distill(max_papers", 1)[1].split("\n@app", 1)[0]
    branch = body.split("if named:", 1)[1].split("\n        else:", 1)[0]
    assert "the named list wins" in branch
    # `max_papers` must not appear as a slice or a limit on this path.
    assert "[:max_papers]" not in branch
    assert "limit %s" not in branch


def test_an_unmigrated_database_reads_every_named_paper_rather_than_raising():
    """`prompt_sha` ships with the code that writes it; the schema is applied by hand.

    A statement naming a column the schema run has not reached yet does not
    skip a guard, it aborts the transaction, which would take the whole run
    down rather than this one check. So the column is asked about, and where it
    is absent there is no evidence about what has been read: the same answer a
    NULL gives, taking the same branch.
    """
    conn = FakeConn(
        papers=[("a", "t", "x", "distill", "arxiv", dt.datetime(2026, 9, 14))],
        claims=[("a", "aaaaaaaaaaaa")],
        columns=(),
    )
    rows, lines = distill.explicit_intake(conn, ["a"], shas=TODAY)
    assert [r[0] for r in rows] == ["a"]
    said = " ".join(lines)
    assert "claims.prompt_sha is missing" in said
    assert "db/schema.sql" in said
    # And the claims table is not read at all, because reading it is what would
    # have raised.
    assert not any("from claims" in s for s, _ in conn.statements)


# --- both id shapes, which is the hand half of INC-2026-10-05 ---------------

def test_a_firehose_paper_named_by_its_bare_id_is_found_not_reported_absent():
    """The defect of 2026-11-09. `pipeline/ingest.py` stores
    `arxiv:2609.08371v1`; a caller types `arxiv:2609.08371`. The old equality
    join reported the paper absent and sent the caller to an ingest whose
    insert is `on conflict (id) do nothing`, so the advice could not work
    either."""
    conn = FakeConn(papers=[
        ("arxiv:2609.08371v1", "EvoSafeHarness", "an abstract", "distill",
         "arxiv", None),
    ])
    rows, lines = distill.explicit_intake(conn, ["arxiv:2609.08371"], shas=TODAY)
    assert [r[0] for r in rows] == ["arxiv:2609.08371v1"]
    assert not [line for line in lines if "no row in `papers`" in line]


def test_a_paper_absent_under_every_shape_is_still_reported_absent():
    """The fix must not turn every absence into a match, which is the direction
    a prefix match fails in."""
    conn = FakeConn(papers=[
        ("arxiv:2609.08371v1", "EvoSafeHarness", "a", "distill", "arxiv", None),
    ])
    rows, lines = distill.explicit_intake(conn, ["arxiv:2610.07639"], shas=TODAY)
    assert rows == []
    assert any("no row in `papers` for arxiv:2610.07639" in line for line in lines)


def test_the_claims_lookup_asks_about_the_id_the_corpus_holds():
    """`claims.paper_id` carries the real id, so a lookup keyed on what the
    caller typed finds no prior reading and reads a versioned paper twice."""
    conn = FakeConn(
        papers=[("arxiv:2609.08371v2", "EvoSafeHarness", "a", "distill",
                 "arxiv", dt.datetime(2026, 9, 14))],
        claims=[("arxiv:2609.08371v2", TODAY["paper"])],
    )
    rows, lines = distill.explicit_intake(conn, ["arxiv:2609.08371"], shas=TODAY)
    claims_query = [(s, prm) for s, prm in conn.statements if "from claims" in s][0]
    assert claims_query[1][0] == ["arxiv:2609.08371v2"]
    assert rows == []
    assert any("same reading twice" in line for line in lines)


def test_a_duplicate_pair_is_named_and_resolved_the_way_the_queue_resolves_it():
    """This route re-reads a distilled paper on purpose, so `pick_held`'s
    distilled-first rule would be wrong here and is not used. The shape
    ordering IS shared, and that is deliberate: two routes resolving one
    duplicated paper to two different shapes would write claims under two ids
    and rebuild the defect both are being fixed for."""
    conn = FakeConn(papers=[
        ("arxiv:2609.08371", "EvoSafeHarness", "a", "discard", "hf-daily",
         dt.datetime(2026, 9, 14)),
        ("arxiv:2609.08371v2", "EvoSafeHarness", "a", "distill", "arxiv", None),
    ])
    rows, lines = distill.explicit_intake(conn, ["arxiv:2609.08371"], shas=TODAY)
    assert [r[0] for r in rows] == ["arxiv:2609.08371"]
    assert rows[0][0] == rq_pick_shape(["arxiv:2609.08371", "arxiv:2609.08371v2"])
    assert any("held under 2 ids" in line and "INC-2026-10-05" in line
               for line in lines)


def rq_pick_shape(ids):
    """The queue's own ordering, asked rather than restated, so this test fails
    if the two routes ever diverge."""
    import reading_queue

    return max(ids, key=reading_queue.version_rank)


def test_the_statement_itself_carries_both_halves():
    """The query and not the fake, because a fake taught both shapes will pass
    a statement that matches one."""
    conn = FakeConn(papers=[])
    distill.explicit_intake(conn, ["arxiv:2609.08371"], shas=TODAY)
    select = [(s, prm) for s, prm in conn.statements if "from papers p" in s][0]
    assert "p.id = any(%s) or p.id like any(%s)" in select[0]
    assert select[1] == (["arxiv:2609.08371"], ["arxiv:2609.08371v%"])
