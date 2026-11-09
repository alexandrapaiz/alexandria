#!/usr/bin/env python3
"""The query that separates "absent from the corpus" from "fetched and discarded".

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

The research seat asked for this on 2026-11-09 for `2610.07639` and could not
run it: no read credential in any seat sandbox. The two states it separates need
opposite repairs, so answering the wrong one keeps the paper absent, which is
the sentence the ask ended on.

What these tests are mostly about is the one way the query answers the wrong
state silently. `papers.id` holds arXiv papers under two shapes and the empty
result that means "absent" is exactly what an equality join returns for a paper
held under the other one. That is
`INC-2026-10-05-absence-asserted-from-an-unnormalised-id-join`, where the
mistake was made, corrected inside one run, and then made again by the
corrected run's own first query.

Nothing here opens a connection.
"""

import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import corpus_row                                                # noqa: E402

PAPER = ("arxiv:2610.07639v2", "arxiv", "a-low", "HarnessSecurity-Bench",
         "https://arxiv.org/abs/2610.07639v2", dt.date(2026, 10, 6),
         dt.datetime(2026, 10, 7), None)


def lines_of(value, papers, decisions):
    out = []
    code = corpus_row.report(value, papers, decisions, out=out.append)
    return code, "\n".join(out)


# --- the id shapes, which is why this is a tool ------------------------------

def test_every_lookup_matches_both_id_shapes():
    """The whole reason for the file. An equality join on the bare id misses
    every paper the arxiv feed ingested, and misses it by returning the result
    that means absent."""
    for sql in (corpus_row.PAPERS_SQL, corpus_row.TRIAGE_SQL):
        assert "= %(base)s or" in sql
        assert "like %(versioned)s" in sql


def test_the_versioned_pattern_is_anchored_on_a_literal_v():
    """`arxiv:2610.07639%` would match a different paper. arXiv's numeric ids
    carry no `v`, so the literal one is what makes the prefix safe."""
    bound = corpus_row.params("2610.07639")
    assert bound == {"base": "arxiv:2610.07639",
                     "versioned": "arxiv:2610.07639v%"}


def test_every_shape_of_a_reference_reaches_the_same_base_id():
    for value in ("2610.07639", "arxiv:2610.07639", "arXiv:2610.07639V2",
                  "https://arxiv.org/abs/2610.07639v1", " 2610.07639 "):
        assert corpus_row.base_id(value) == "arxiv:2610.07639"


def test_an_id_this_does_not_recognise_is_not_rewritten():
    """`papers.id` is also a url hash for a blog post, and inventing an
    `arxiv:` prefix for one would ask about a paper that does not exist."""
    assert corpus_row.base_id("blog-9fe3a1c") == "blog-9fe3a1c"
    assert corpus_row.base_id("") == ""


# --- the five states, and the exit code is the answer ------------------------

def test_absent_names_the_intake_and_the_route_that_needs_no_credential():
    code, text = lines_of("2610.07639", [], [])
    assert code == corpus_row.ABSENT == 3
    assert "ABSENT" in text
    assert "reading_queue.py --add" in text


def test_discarded_names_the_judgement_and_not_the_intake():
    """The repair that the other state asks for would do nothing here, because
    the insert is `on conflict (id) do nothing`. Saying so is the point."""
    decisions = [("arxiv:2610.07639v2", "discard", 0.21, "a-model", "abc123",
                  dt.datetime(2026, 10, 7), None, None)]
    code, text = lines_of("2610.07639", [PAPER], decisions)
    assert code == corpus_row.PRESENT_DISCARDED == 1
    assert "PRESENT AND DISCARDED" in text
    assert "human_verdict" in text
    assert "abc123" in text


def test_present_and_never_judged_is_its_own_state():
    """Neither of the two the ask named. An intake would change nothing and a
    triage prompt is not at fault either; the paper is waiting on a run."""
    code, text = lines_of("2610.07639", [PAPER], [])
    assert code == corpus_row.PRESENT_UNTRIAGED == 2
    assert "PRESENT, NEVER JUDGED" in text
    assert "triage  no row" in text


def test_present_and_kept_reads_the_latest_decision_not_the_first():
    """Re-triage appends, so a paper discarded in October and distilled in
    November has two rows and one current answer."""
    decisions = [
        ("arxiv:2610.07639v2", "discard", 0.2, "m", "a", dt.datetime(2026, 10, 7),
         None, None),
        ("arxiv:2610.07639v2", "deep_read", 0.9, "m", "b", dt.datetime(2026, 11, 1),
         "overturn", "the research seat asked for it"),
    ]
    code, text = lines_of("2610.07639", [PAPER], decisions)
    assert code == corpus_row.PRESENT_KEPT == 0
    assert "PRESENT AND KEPT" in text
    assert "`deep_read`" in text
    assert "overturn" in text


def test_a_duplicate_pair_is_reported_as_a_pair():
    """Resolving to one half of it silently is how 322 duplicated papers went
    unnoticed until a census found them."""
    other = ("arxiv:2610.07639", "reading-queue", "b", "HarnessSecurity-Bench",
             "https://arxiv.org/abs/2610.07639", dt.date(2026, 10, 6),
             dt.datetime(2026, 11, 1), dt.datetime(2026, 11, 2))
    code, text = lines_of("2610.07639", [other, PAPER], [])
    assert "2 rows carry this paper" in text
    assert "arxiv:2610.07639v2" in text and "arxiv:2610.07639\n" in text
    assert code == corpus_row.PRESENT_UNTRIAGED


# --- it refuses rather than guesses -----------------------------------------

def test_with_no_credential_it_exits_four_and_prints_the_query_to_hand_over(capsys):
    """Every seat sandbox in this company is this case, and has been for every
    run of this seat: `NEON_RO_URL` is an owner secret still pending in
    `docs/backlog.md`, and the Modal workspace holding `DATABASE_URL` has been
    off since 2026-10-23."""
    assert corpus_row.main(["2610.07639"]) == corpus_row.UNKNOWN == 4
    out = capsys.readouterr().out
    assert "cannot answer" in out
    assert "--sql" in out


def test_sql_mode_prints_a_query_a_credential_holder_can_paste(capsys):
    assert corpus_row.main(["2610.07639", "--sql"]) == 0
    out = capsys.readouterr().out
    assert "'arxiv:2610.07639'" in out
    assert "'arxiv:2610.07639v%'" in out
    assert "%(base)s" not in out        # every placeholder bound
    assert out.count(";") == 2          # both queries, ready to run


def test_nothing_here_writes():
    """Read-only is asserted by parsing the statements rather than by the
    docstring that claims it, the way tools/graph_audit.py does."""
    for sql in (corpus_row.PAPERS_SQL, corpus_row.TRIAGE_SQL):
        assert sql.strip().lower().startswith("select")
        for word in ("insert", "update", "delete", "drop", "alter", "truncate"):
            assert word not in sql.lower()


def test_the_credential_it_prefers_is_the_read_only_one(monkeypatch):
    """`NEON_RO_URL` before `DATABASE_URL`, because a tool that only reads
    should ask for the credential that only reads."""
    monkeypatch.setenv("NEON_RO_URL", "postgres://ro/x")
    monkeypatch.setenv("DATABASE_URL", "postgres://rw/x")
    seen = {}

    class FakePsycopg:
        @staticmethod
        def connect(url, connect_timeout=None):
            seen["url"] = url
            raise RuntimeError("no server here")

    monkeypatch.setitem(sys.modules, "psycopg", FakePsycopg)
    conn, why = corpus_row.connect()
    assert conn is None
    assert seen["url"] == "postgres://ro/x"
    assert "NEON_RO_URL is set but the connection failed" in why


def test_the_two_states_the_ask_was_between_have_different_exit_codes():
    """The one assertion the research seat's script depends on."""
    assert corpus_row.ABSENT != corpus_row.PRESENT_DISCARDED
