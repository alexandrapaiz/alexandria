"""The arXiv window: the date range, the paging, and the two bounds on it.

    pip install -r requirements-dev.txt && python3 -m pytest tests/test_arxiv_window.py -q

`pipeline/ingest.py` asked arXiv for `max_results=100` sorted by submission
date, with no date bound, from the job's first day until 2026-10-26. The
monthly source census measured what that window holds against what the
categories behind it submit
(`docs/research/notes/2026-10-26-source-census.md` section 2): cs.AI submits
116 papers a day and cs.LG 114, against a window of 100 per run. Six of the
eight listed categories have slack and those two do not, and they are the two
the skills literature lives in.

The cost is not latency, which is the finding worth keeping. A pipeline
reading a durable queue loses time when it stops; one reading a sliding window
loses records. The 3.33 days this cron spent stopped put between 290 and 570
papers permanently out of reach of every future run, growing by about 130 a
day
(`INC-2026-10-26-the-arxiv-window-is-smaller-than-two-of-the-categories-behind-it`).

So the assertion this file exists for is
`test_three_days_of_downtime_comes_back_in_full`: against a fake arXiv holding
three days of cs.AI at the measured volume, the run takes all 348 and not the
hundred most recent. Everything else here is a bound on that, because a window
paged to exhaustion is unbounded work by default and this job has a 900-second
timeout it must not spend.

No network and no database. `fetch_arxiv` takes its parser, its sleep and its
clock as arguments for exactly that reason, and the fake arXiv below answers
the real query string, including `start=`, so that a paging bug shows up as a
wrong count rather than as a passing test of a mock.
"""

import datetime as dt
import pathlib
import re
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pipeline"))

import ingest  # noqa: E402

TODAY = dt.date(2026, 10, 26)

QUERY = re.compile(
    r"search_query=cat:(?P<cat>[\w.]+)\+AND\+"
    r"submittedDate:%5B(?P<since>\d{12})\+TO\+(?P<until>\d{12})%5D"
)
PAGING = re.compile(r"start=(?P<start>\d+)&max_results=(?P<rows>\d+)")


def entry(number: int, day: dt.date):
    """One arXiv Atom entry, in the shape feedparser hands back."""
    return types.SimpleNamespace(
        id=f"http://arxiv.org/abs/26{day:%m%d}.{number:05d}v1",
        title=f"  A paper\n  numbered {number}  ",
        authors=[types.SimpleNamespace(name="A Researcher")],
        summary="An abstract.",
        link=f"http://arxiv.org/abs/26{day:%m%d}.{number:05d}v1",
        published_parsed=types.SimpleNamespace(
            tm_year=day.year, tm_mon=day.month, tm_mday=day.day
        ),
    )


class FakeArxiv:
    """An arXiv that answers the query string, paging and date range included.

    `papers` maps a category to `{date: count}`. A request is served by
    filtering to the submitted-date range the URL asks for, sorting newest
    first the way `sortOrder=descending` promises, and slicing `start:start+rows`.
    """

    def __init__(self, papers: dict[str, dict[dt.date, int]], status: int = 200):
        self.papers = papers
        self.status = status
        self.urls: list[str] = []

    def parse(self, url: str):
        self.urls.append(url)
        query = QUERY.search(url)
        paging = PAGING.search(url)
        assert query, f"no submittedDate window in {url}"
        assert paging, f"no start/max_results in {url}"
        since = dt.datetime.strptime(query["since"], "%Y%m%d%H%M").date()
        until = dt.datetime.strptime(query["until"], "%Y%m%d%H%M").date()

        rows = []
        for day, count in sorted(self.papers.get(query["cat"], {}).items(), reverse=True):
            if since <= day <= until:
                rows.extend(entry(n, day) for n in range(count))
        start, size = int(paging["start"]), int(paging["rows"])
        return types.SimpleNamespace(entries=rows[start:start + size], status=self.status)


def cfg(*categories: str) -> dict:
    return {"arxiv": [{"category": c, "tier": "a"} for c in categories]}


def days(category: str, per_day: int, count: int, last: dt.date = TODAY):
    """`count` days of `per_day` submissions, ending on `last`."""
    return {category: {last - dt.timedelta(days=n): per_day for n in range(count)}}


def run(fake, categories, cursor=None, today=TODAY, clock=None):
    """`fetch_arxiv` with no network, no waiting and a clock that stands still."""
    slept = []
    rows, status = ingest.fetch_arxiv(
        cfg(*categories),
        cursor=cursor,
        today=today,
        parse=fake.parse,
        sleep=slept.append,
        clock=clock or (lambda: 0.0),
    )
    return rows, status, slept


# ------------------------------------------------------------- the window

def test_no_cursor_window_is_the_two_day_floor():
    """An empty corpus has nothing to resume from, so it takes the floor."""
    since, until = ingest.arxiv_window(None, TODAY)
    assert since == dt.date(2026, 10, 24)
    assert until == dt.date(2026, 10, 27), "the range must include today"


def test_the_window_reaches_back_past_the_cursor():
    """A paper is searchable by submission date only once it is announced, and
    nothing announces over a weekend, so the newest date in `papers` is never
    proof the whole day is there. Measured live on 2026-10-26: the newest
    announced cs.CL submission date was three days back."""
    since, _ = ingest.arxiv_window("2026-10-23", TODAY)
    assert since == dt.date(2026, 10, 19)


def test_the_overlap_covers_a_weekend_and_a_day():
    """The constant's reason, asserted rather than left in a comment: a run on
    a Monday resumes from a Friday cursor and must still reach the Thursday
    before it, because a weekend announces nothing."""
    assert ingest.ARXIV_CURSOR_OVERLAP_DAYS >= 3


def test_a_long_outage_is_clamped_to_the_max_lookback():
    since, _ = ingest.arxiv_window("2026-01-01", TODAY)
    assert since == TODAY - dt.timedelta(days=ingest.ARXIV_MAX_LOOKBACK_DAYS)


def test_a_future_cursor_cannot_invert_the_window():
    """One row with a wrong `published_at` must not produce since > until."""
    since, until = ingest.arxiv_window("2027-03-01", TODAY)
    assert since == TODAY and since < until


def test_the_url_carries_the_window_the_page_and_the_sort():
    url = ingest.arxiv_url("cs.AI", dt.date(2026, 10, 24), dt.date(2026, 10, 27), start=200)
    assert "cat:cs.AI+AND+submittedDate:%5B202610240000+TO+202610270000%5D" in url
    assert "sortBy=submittedDate&sortOrder=descending" in url
    assert f"start=200&max_results={ingest.ARXIV_PAGE}" in url


# -------------------------------------------------------------- the paging

def test_three_days_of_downtime_comes_back_in_full():
    """The assertion this file exists for.

    Three days of cs.AI at the census's measured 116 a day, with a cursor
    three days old, is 348 papers. The window this replaces would have
    returned the 100 most recent and left 248 beyond the reach of every
    future run.
    """
    fake = FakeArxiv(days("cs.AI", 116, 3))
    rows, status, _ = run(fake, ["cs.AI"], cursor="2026-10-24")

    assert len(rows) == 348
    assert status[0]["entries"] == 348
    assert status[0]["truncated"] is None
    assert len(fake.urls) == 4, "348 rows at 100 a page is four requests"
    assert status[0]["pages"] == 4


def test_a_full_last_page_still_asks_once_more():
    """A window that is an exact multiple of the page size is the case a
    `len(page) < PAGE` stopping condition gets wrong in the lossy direction
    if it is written as `len(page) == 0`."""
    fake = FakeArxiv({"cs.AI": {TODAY: 200}})
    rows, status, _ = run(fake, ["cs.AI"], cursor="2026-10-26")
    assert len(rows) == 200
    assert status[0]["pages"] == 3, "two full pages, then the empty one that ends it"


def test_the_page_size_is_not_the_window():
    """The regression guard on the defect itself: one page must not be a run."""
    assert ingest.ARXIV_PAGE == 100
    assert ingest.ARXIV_MAX_PER_CAT > ingest.ARXIV_PAGE
    fake = FakeArxiv(days("cs.LG", 114, 2))
    rows, _, _ = run(fake, ["cs.LG"], cursor="2026-10-25")
    assert len(rows) > ingest.ARXIV_PAGE


def test_the_rows_carry_what_the_upsert_needs():
    fake = FakeArxiv({"cs.AI": {TODAY: 1}})
    rows, _, _ = run(fake, ["cs.AI"], cursor="2026-10-26")
    row = rows[0]
    assert row["id"] == "arxiv:261026.00000v1"
    assert row["source"] == "arxiv" and row["tier"] == "a"
    assert row["title"] == "A paper numbered 0", "whitespace is collapsed"
    assert row["authors"] == ["A Researcher"]
    assert row["published_at"] == "2026-10-26"


def test_a_paper_that_shifts_between_pages_is_counted_once():
    """A submission arriving mid-walk shifts a descending sort, so the same
    paper can land on two pages. The upsert would discard the copy; the count
    a reader sees in the log should not carry it either."""
    fake = FakeArxiv({"cs.AI": {TODAY: 150}})

    real = fake.parse
    shifted = {"done": False}

    def parse(url):
        feed = real(url)
        if not shifted["done"] and "start=100" in url:
            shifted["done"] = True
            feed.entries = [entry(99, TODAY)] + list(feed.entries)
        return feed

    rows, status = ingest.fetch_arxiv(
        cfg("cs.AI"), cursor="2026-10-26", today=TODAY,
        parse=parse, sleep=lambda _: None, clock=lambda: 0.0,
    )
    assert status[0]["entries"] == 150
    assert len({r["id"] for r in rows}) == len(rows) == 150


def test_every_category_is_walked_and_reported_separately():
    fake = FakeArxiv({**days("cs.AI", 116, 1), **days("cs.MA", 8, 1)})
    rows, status, _ = run(fake, ["cs.AI", "cs.MA"], cursor="2026-10-26")
    assert [s["name"] for s in status] == ["arxiv:cs.AI", "arxiv:cs.MA"]
    assert [s["entries"] for s in status] == [116, 8]
    assert {r["id"] for r in rows if r["tier"] == "a"}, "tier is carried from sources.yaml"


def test_a_dark_category_is_one_request_and_still_reported():
    """The 2026-10-16 finding, unchanged by paging: a category that answers
    nothing is a status row and not an exception."""
    fake = FakeArxiv({"cs.AI": {}})
    rows, status, _ = run(fake, ["cs.AI"], cursor="2026-10-26")
    assert rows == []
    assert status[0]["entries"] == 0 and status[0]["pages"] == 1
    assert status[0]["http"] == 200


def test_arxiv_is_given_its_pause_between_pages_and_not_after_the_last():
    fake = FakeArxiv({"cs.AI": {TODAY: 250}})
    _, _, slept = run(fake, ["cs.AI"], cursor="2026-10-26")
    assert slept == [ingest.ARXIV_DELAY] * 2, "three requests, two pauses"


# -------------------------------------------------------------- the bounds

def test_the_ceiling_binds_and_the_category_says_so(monkeypatch):
    monkeypatch.setattr(ingest, "ARXIV_MAX_PER_CAT", 200)
    fake = FakeArxiv({"cs.AI": {TODAY: 500}})
    rows, status, _ = run(fake, ["cs.AI"], cursor="2026-10-26")
    assert len(rows) == 200
    assert "200-row ceiling" in status[0]["truncated"]


def test_the_ceiling_clears_the_longest_lookback_at_the_measured_volume():
    """The ceiling is a guard against a bad cursor, not a limit on a real
    backlog, so it must not bind inside the lookback the window allows."""
    worst = 116 * ingest.ARXIV_MAX_LOOKBACK_DAYS  # cs.AI, per the census
    assert ingest.ARXIV_MAX_PER_CAT > worst


def test_the_budget_stops_the_walk_and_the_category_says_so():
    """A run that overruns the Modal timeout loses the feeds and the upsert
    too, so a deep backlog has to stop short rather than take the job down."""
    ticks = iter([0.0] + [ingest.ARXIV_BUDGET_S + 1.0] * 50)
    fake = FakeArxiv({"cs.AI": {TODAY: 500}})
    rows, status, slept = run(fake, ["cs.AI"], cursor="2026-10-26", clock=lambda: next(ticks))
    assert len(rows) == 100, "the page in hand is kept"
    assert "firehose budget" in status[0]["truncated"]
    assert slept == [], "a run out of budget does not then wait three seconds"


def test_the_budget_is_inside_the_jobs_timeout():
    source = (ROOT / "pipeline" / "ingest.py").read_text(encoding="utf-8")
    timeout = int(re.search(r"timeout=(\d+)", source).group(1))
    assert ingest.ARXIV_BUDGET_S < timeout, "the budget must leave the job room"


# ------------------------------------------------------------- the cursor

class FakeCursor:
    def __init__(self, row):
        self.row, self.sql = row, None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, *_):
        self.sql = sql

    def fetchone(self):
        return self.row


class FakeConn:
    def __init__(self, row):
        self.cur = FakeCursor(row)

    def cursor(self):
        return self.cur


def test_the_cursor_is_the_newest_arxiv_submission_date():
    conn = FakeConn((dt.date(2026, 10, 23),))
    assert ingest.arxiv_cursor(conn) == "2026-10-23"
    assert "max(published_at)" in conn.cur.sql
    assert "source = 'arxiv'" in conn.cur.sql, (
        "hf-daily writes into the same id space and its dates are a human's "
        "pick, not this query's reach"
    )


def test_an_empty_corpus_has_no_cursor():
    assert ingest.arxiv_cursor(FakeConn((None,))) is None
    assert ingest.arxiv_cursor(FakeConn(None)) is None


def test_the_cursor_is_read_only():
    conn = FakeConn((dt.date(2026, 10, 23),))
    ingest.arxiv_cursor(conn)
    assert conn.cur.sql.strip().lower().startswith("select")


# ----------------------------------------------------------- the reporting

def test_judge_sources_reports_a_short_window_without_refusing():
    status = [
        {"name": "arxiv:cs.AI", "kind": "arxiv", "entries": 2000,
         "truncated": "stopped at the 2000-row ceiling", "http": 200},
        {"name": "arxiv:cs.MA", "kind": "arxiv", "entries": 8, "truncated": None,
         "http": 200},
    ]
    summary, refusal = judge(status)
    assert refusal is None, "what it did fetch is real and the rest of the run wants it"
    assert "short of the window: arxiv:cs.AI (stopped at the 2000-row ceiling)" in summary


def test_judge_sources_still_refuses_a_dark_firehose():
    """Paging changed what a category fetches and not what a dead firehose
    means: the blogs alone are not a corpus, so a working day where every
    category answers zero is an API failure and not a quiet day."""
    status = [
        {"name": "arxiv:cs.AI", "kind": "arxiv", "entries": 0, "truncated": None,
         "http": 200},
        {"name": "anthropic-news", "kind": "feed", "entries": 4, "http": 200},
    ]
    summary, refusal = judge(status)
    assert refusal and "arXiv API failure" in refusal
    assert "delivered nothing: arxiv:cs.AI" in summary


def judge(status):
    return ingest.judge_sources(status)


# --------------------------------------------------------------- the pin

def test_the_availability_probe_is_pinned_to_the_page_size():
    """`tools/feed_health.py` carried the comment "the same number
    pipeline/ingest.py queries with" and nothing checked it, which is how a
    true comment survives the change that falsifies it."""
    sys.path.insert(0, str(ROOT / "tools"))
    import feed_health  # noqa: PLC0415

    assert feed_health.ARXIV_PROBE_ROWS == ingest.ARXIV_PAGE
    assert feed_health.ARXIV_DELAY == ingest.ARXIV_DELAY

# ------------------------------------------------------ the by-id entrypoint
#
# The window is the whole reach of the daily job, and it only moves forward, so
# a paper submitted before the edge on the day a category shipped was never
# inside it and never will be. `cs.SE` ran 639 papers in September 2026, about
# twenty-one a day, which is roughly five days deep. The research seat measured
# the addendum rather than the one paper: the comment justifying that category
# names six papers by id and the window could reach zero of six, the newest of
# them twelve days older than the edge on the day the category shipped. That is
# a backfill gap, and no run of the cron closes it
# (`INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written`).

ID_LIST = re.compile(r"id_list=(?P<ids>[^&]*)")


class FakeArxivById:
    """An arXiv that answers `id_list`, and can be missing an id it was asked for."""

    def __init__(self, holds: dict[str, dt.date], status: int = 200):
        self.holds = holds
        self.status = status
        self.urls: list[str] = []

    def parse(self, url: str):
        self.urls.append(url)
        asked = ID_LIST.search(url)
        assert asked, f"no id_list in {url}"
        assert "submittedDate" not in url, "a named list has no window"
        rows = []
        for raw in asked["ids"].split(","):
            bare = raw.split("v")[0]
            if bare in self.holds:
                day = self.holds[bare]
                number = int(bare.split(".")[1])
                item = entry(number, day)
                item.id = f"http://arxiv.org/abs/{bare}v1"
                item.link = item.id
                rows.append(item)
        return types.SimpleNamespace(entries=rows, status=self.status)


def test_an_id_outside_every_window_is_still_reachable_by_name():
    # The paper the gap was found on: submitted 2026-09-08, sole category, and
    # seventeen days outside the window on the earliest day that category could
    # have been live.
    fake = FakeArxivById({"2609.08371": dt.date(2026, 9, 8)})
    rows, status = ingest.fetch_arxiv_ids(["2609.08371"], parse=fake.parse)
    # Versioned, because `test_the_rows_carry_what_the_upsert_needs` shows the
    # firehose keeping the suffix too. Same key space means the same key, and
    # the id asked for is deliberately not the id written: arXiv answers a bare
    # id with whichever version is current, and that answer is the row.
    assert [r["id"] for r in rows] == ["arxiv:2609.08371v1"]
    assert status[0]["missing"] == []
    assert status[0]["asked"] == 1


def test_the_rows_land_in_the_same_key_space_the_firehose_upserts():
    # `arxiv:<id>`, so a backfilled paper and a fetched one are one row rather
    # than two, which is the same reason hf-daily writes this prefix.
    fake = FakeArxivById({"2610.02858": dt.date(2026, 10, 2)})
    rows, _ = ingest.fetch_arxiv_ids(["2610.02858"], parse=fake.parse)
    row = rows[0]
    assert row["id"] == "arxiv:2610.02858v1"
    assert row["source"] == "arxiv"
    assert row["tier"] == "b"          # a named paper is a curated pick
    assert row["title"] == "A paper numbered 2858"
    assert row["published_at"] == "2026-10-02"
    assert set(row) == {"id", "source", "tier", "title", "authors", "abstract",
                        "url", "published_at"}


def test_every_form_a_queue_line_writes_an_id_in_is_accepted():
    assert ingest.normalise_arxiv_id("2609.08371") == "2609.08371"
    assert ingest.normalise_arxiv_id("arxiv:2609.08371") == "2609.08371"
    assert ingest.normalise_arxiv_id("ARXIV:2609.08371") == "2609.08371"
    assert ingest.normalise_arxiv_id("2609.08371v2") == "2609.08371v2"
    assert ingest.normalise_arxiv_id("https://arxiv.org/abs/2609.08371") == "2609.08371"
    assert ingest.normalise_arxiv_id("  2609.08371  ") == "2609.08371"
    assert ingest.normalise_arxiv_id("") == ""
    fake = FakeArxivById({"2609.08371": dt.date(2026, 9, 8)})
    rows, _ = ingest.fetch_arxiv_ids(
        ["arxiv:2609.08371", "https://arxiv.org/abs/2609.08371"], parse=fake.parse)
    # Asked twice in two spellings, and arXiv answers each, which the upsert
    # collapses on the primary key.
    assert {r["id"] for r in rows} == {"arxiv:2609.08371v1"}


def test_an_id_that_comes_back_with_nothing_is_named_rather_than_counted():
    # A backfill asking for six and silently landing four is the defect shape
    # this entrypoint exists to repair, so the absence is reported.
    fake = FakeArxivById({"2609.08371": dt.date(2026, 9, 8)})
    rows, status = ingest.fetch_arxiv_ids(
        ["2609.08371", "2607.25635", "2606.09182"], parse=fake.parse)
    assert len(rows) == 1
    assert status[0]["asked"] == 3
    assert status[0]["missing"] == ["2606.09182", "2607.25635"]


def test_the_query_asks_for_the_count_it_named_and_carries_no_window():
    fake = FakeArxivById({})
    ingest.fetch_arxiv_ids(["2606.09182", "2607.25635", "2607.27294",
                            "2609.00072", "2609.08371", "2609.14721"],
                           parse=fake.parse)
    url = fake.urls[0]
    assert "max_results=6" in url and "start=0" in url
    assert "sortBy" not in url          # a named list has no order to ask for
    assert "submittedDate" not in url


def test_asking_for_nothing_makes_no_request():
    fake = FakeArxivById({})
    rows, status = ingest.fetch_arxiv_ids(["", "   "], parse=fake.parse)
    assert (rows, fake.urls) == ([], [])
    assert status[0]["asked"] == 0


def test_the_tier_can_be_set_down_for_a_bulk_backfill():
    fake = FakeArxivById({"2609.08371": dt.date(2026, 9, 8)})
    rows, _ = ingest.fetch_arxiv_ids(["2609.08371"], tier="a", parse=fake.parse)
    assert rows[0]["tier"] == "a"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
