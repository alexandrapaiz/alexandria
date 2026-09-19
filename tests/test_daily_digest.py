"""The daily issue's pure logic, tested without Modal, Neon, or Groq.

Everything here runs offline. The SQL and the model call are not covered, and
cannot be from a sandbox; what is covered is the part most likely to go quietly
wrong on a schedule nobody watches every day: which kind of issue a given date
produces, what key it writes under, and whether an empty day can ever reach the
model.
"""

from datetime import date

import pytest

from pipeline.weekly import (
    MASTHEAD,
    MAX_TOKENS,
    add_masthead,
    daily_is_empty,
    daily_key,
    empty_issue,
    kind_for,
    weekly_key,
)

STREAMS = ("new_claims", "deprecated", "superseded", "deep_reads")


def empty_payload():
    return {k: [] for k in STREAMS}


# ---------------- which kind runs on which day ----------------

def test_monday_is_the_weekly():
    assert kind_for(date(2026, 9, 21)) == "weekly"


@pytest.mark.parametrize("day", range(22, 28))  # Tuesday 22nd to Sunday 27th
def test_every_other_day_is_a_daily(day):
    assert kind_for(date(2026, 9, day)) == "daily"


def test_a_full_week_produces_one_weekly_and_six_dailies():
    kinds = [kind_for(date(2026, 9, 21) + __import__("datetime").timedelta(days=n))
             for n in range(7)]
    assert kinds.count("weekly") == 1
    assert kinds.count("daily") == 6


# ---------------- issue keys ----------------

def test_daily_key_is_the_date_it_covers():
    key, dates = daily_key(date(2026, 9, 19))
    assert key == "2026-09-19"
    assert dates == "September 19, 2026"


def test_weekly_key_still_labels_the_week_that_just_ended():
    # unchanged behaviour: Monday 2026-09-21 labels the week ending Sunday the 20th
    key, dates = weekly_key(date(2026, 9, 21))
    assert key == "2026-W38"
    assert dates == "September 14–20, 2026"


def test_weekly_key_spells_both_months_when_the_week_straddles_one():
    key, dates = weekly_key(date(2026, 10, 5))
    assert key == "2026-W40"
    assert dates == "September 28 – October 4, 2026"


def test_daily_and_weekly_keys_can_never_collide():
    """Both kinds share one unique column, so the formats must stay disjoint."""
    for n in range(370):
        day = date(2026, 1, 1) + __import__("datetime").timedelta(days=n)
        assert daily_key(day)[0] != weekly_key(day)[0]
        assert "W" not in daily_key(day)[0]
        assert "W" in weekly_key(day)[0]


# ---------------- the honest empty day ----------------

def test_an_empty_payload_is_empty():
    assert daily_is_empty(empty_payload()) is True


@pytest.mark.parametrize("stream", STREAMS)
def test_any_single_stream_with_anything_in_it_is_not_empty(stream):
    payload = empty_payload()
    payload[stream] = [{"anything": 1}]
    assert daily_is_empty(payload) is False


def test_pipeline_counts_alone_do_not_make_a_day_non_empty():
    """Ingesting forty routine papers that produced no claims is still a day
    with nothing to say, and must not be padded into an issue."""
    payload = empty_payload()
    payload["stats"] = {"papers_ingested": 40, "claims_distilled": 0, "edges_drawn": 0}
    assert daily_is_empty(payload) is True


def test_the_empty_issue_is_one_line_and_names_its_date():
    body = empty_issue("September 19, 2026")
    assert body.startswith("# Nothing worth your time today [September 19, 2026]")
    prose = body.split("\n\n", 1)[1]
    assert len(prose.split()) < 40
    assert "Monday" in prose  # points the reader at the weekly


# ---------------- masthead ----------------

def test_each_kind_gets_its_own_masthead_under_the_title():
    body = add_masthead("# A title [September 19, 2026]\n\nLead.", "daily")
    lines = body.split("\n")
    assert lines[0] == "# A title [September 19, 2026]"
    assert lines[2] == MASTHEAD["daily"]
    assert "24 hours" in lines[2]


def test_the_two_mastheads_differ():
    assert MASTHEAD["daily"] != MASTHEAD["weekly"]
    assert "Monday" in MASTHEAD["daily"]


def test_the_empty_issue_still_gets_its_masthead():
    body = add_masthead(empty_issue("September 19, 2026"), "daily")
    assert MASTHEAD["daily"] in body


# ---------------- budget ----------------

def test_the_daily_cannot_ask_for_weekly_length():
    assert MAX_TOKENS["daily"] < MAX_TOKENS["weekly"]


def test_the_two_kinds_are_the_only_two_kinds():
    """digest() validates its --kind against MASTHEAD's keys, so the two must
    stay in step with MAX_TOKENS and with the digests table's check."""
    assert set(MASTHEAD) == set(MAX_TOKENS) == {"weekly", "daily"}


# ---------------- gather_daily's row mapping ----------------

class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        return self._rows[0]

    def fetchall(self):
        return self._rows


class FakeConn:
    """Hands back canned rows in the order gather_daily asks for them.

    There is no Postgres here, so this proves nothing about the SQL. What it
    does prove is the part that sits between the SQL and the model: that every
    positional index in the row-to-dict mapping lines up with the column it
    means. That mapping has thirteen positions in the claims query alone, and a
    mistake in it surfaces at 15:00 UTC and nowhere else.
    """

    def __init__(self, results):
        self.results = list(results)
        self.queries = []

    def execute(self, sql, params=None):
        self.queries.append((sql, params))
        return FakeResult(self.results.pop(0))


CLAIM_ROW = (
    7, "Dense rewards stabilise long-horizon agents", ["rl", "agents"],
    "A paper title", "https://arxiv.org/abs/2609.00001", "a",
    "deep_read", 0.91, ["supports -> claim 3"],
    "evidence text", "1. do this\n2. then this", ["Ada L."], ["Tsinghua"],
)


def gather_results(claims=(CLAIM_ROW,), superseded=(), deprecated=(), deep_reads=()):
    return [
        [(12, 4, 9)],           # stats (fetchone)
        list(claims),
        list(superseded),
        list(deprecated),
        list(deep_reads),
    ]


def test_gather_daily_maps_every_column_to_its_name():
    from pipeline.weekly import DAILY_WINDOW_HOURS, gather_daily

    conn = FakeConn(gather_results())
    payload = gather_daily(conn)

    assert payload["stats"] == {
        "papers_ingested": 12, "claims_distilled": 4, "edges_drawn": 9
    }
    claim = payload["new_claims"][0]
    assert claim["claim_id"] == 7
    assert claim["claim"].startswith("Dense rewards")
    assert claim["paper"] == "A paper title"
    assert claim["url"].startswith("https://arxiv.org/")
    assert claim["tier"] == "a"
    assert claim["triage"] == "deep_read"
    assert claim["score"] == 0.91
    assert claim["topics"] == ["rl", "agents"]
    assert claim["institutions"] == ["Tsinghua"]
    assert claim["authors"] == ["Ada L."]
    assert claim["procedure"].startswith("1. do this")
    assert claim["evidence"] == "evidence text"

    # every windowed query is bounded by the same 24-hour lookback
    windowed = [p for _, p in conn.queries if p]
    assert all(DAILY_WINDOW_HOURS in p for p in windowed)


def test_gather_daily_produces_a_payload_the_empty_check_understands():
    from pipeline.weekly import gather_daily

    empty = gather_daily(FakeConn(gather_results(claims=())))
    assert daily_is_empty(empty) is True

    one_claim = gather_daily(FakeConn(gather_results()))
    assert daily_is_empty(one_claim) is False


def test_gather_daily_asks_for_no_traction_streams():
    """The daily is dispatch, not synthesis. Citation movers and accumulated
    supports belong to Monday, and the citation loop only refreshes then."""
    from pipeline.weekly import gather_daily

    conn = FakeConn(gather_results())
    payload = gather_daily(conn)
    assert "traction" not in payload
    assert not any("citation_log" in sql for sql, _ in conn.queries)


def test_the_daily_payload_survives_shrink():
    from pipeline.weekly import gather_daily, shrink

    payload = gather_daily(FakeConn(gather_results()))
    payload["dates"] = "September 19, 2026"
    body = shrink(payload)
    assert "Dense rewards" in body
