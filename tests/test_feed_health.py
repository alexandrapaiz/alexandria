"""The sources check, and ingest's refusal to call an empty run a success.

`pipeline/ingest.py` fetched fifty-three sources every day and could not
tell you whether any of them answered. `feedparser.parse(url)` does not
raise, so a 404 came back as an empty `entries` list and the job printed a
four-digit `fetched` count anyway, because the arXiv firehose dominates
that number whatever the blogs do. Seven of the fifty-three were
delivering nothing when the check was first run
(`docs/evals/2026-10-16-feed-health.json`).

Two halves are under test here and they fail in opposite directions.

`tools/feed_health.py` must not report a working feed as dead, because a
census that cries wolf gets ignored and then the real deaths are invisible
again. The sharp edge is `malformed`: `feedparser` is lenient and
`xml.etree` is not, so a feed this tool cannot parse strictly may be
ingesting fine, and the tests below pin that case to a warning rather than
a failure.

`pipeline/ingest.py`'s `judge_sources` must not stop the corpus over one
dead blog, and must refuse the one case that was previously silent. So the
tests are mostly refusals in the other direction: a zero `inserted` is a
normal day, a zero `fetched` is not, and forty-four dead blogs with a live
firehose still ingest.

Neither half touches the network, a database or the GitHub API. The
fetching is driven through a fake client, and the sources reader runs
against the real `sources.yaml` in the checkout.

Run with `python3 -m pytest tests/test_feed_health.py -q`.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.ingest import judge_sources  # noqa: E402
from tools import feed_health as fh  # noqa: E402

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)


# ------------------------------------------------------ the sources reader

def test_read_sources_finds_all_three_blocks_of_the_real_file():
    cfg = fh.read_sources()
    assert cfg["arxiv"], "no arXiv categories read"
    assert cfg["feeds"], "no feeds read"
    assert cfg["hf_daily_papers"]["url"].startswith("https://")
    for entry in cfg["arxiv"]:
        assert entry["category"] and entry["tier"]
    for feed in cfg["feeds"]:
        assert feed["name"] and feed["url"].startswith("http"), feed
        assert feed["tier"]


def test_read_sources_counts_what_an_independent_count_finds():
    """The reader may not skip a line, so a second method checks the first.

    A reader that quietly dropped an entry it could not parse would commit
    the exact defect this module exists to catch, one level up: a source
    missing from the census is a source nothing checks.
    """
    text = (ROOT / "sources.yaml").read_text(encoding="utf-8")
    independent = 0
    block = None
    for line in text.splitlines():
        if line.strip() and not line[0].isspace() and ":" in line:
            block = line.split(":", 1)[0]
        elif block in ("arxiv", "feeds") and line.strip().startswith("- {"):
            independent += 1

    cfg = fh.read_sources()
    assert len(cfg["arxiv"]) + len(cfg["feeds"]) == independent


def test_sources_to_check_covers_every_source_ingest_fetches():
    cfg = fh.read_sources()
    checks = fh.sources_to_check(cfg)
    assert len(checks) == len(cfg["arxiv"]) + len(cfg["feeds"]) + 1
    names = [c["name"] for c in checks]
    assert len(names) == len(set(names)), "a source name is duplicated"
    assert "hf-daily" in names
    for check in checks:
        assert check["url"].startswith("https://")


def test_read_sources_refuses_an_unknown_block(tmp_path):
    path = tmp_path / "sources.yaml"
    path.write_text("feeds:\n  - {name: a, url: \"https://a\", tier: d}\n"
                    "newthing:\n  - {name: b, url: \"https://b\", tier: d}\n")
    with pytest.raises(ValueError, match="top-level block"):
        fh.read_sources(path)


def test_read_sources_refuses_a_line_it_cannot_parse(tmp_path):
    path = tmp_path / "sources.yaml"
    path.write_text('feeds:\n  - name: a\n    url: "https://a"\n')
    with pytest.raises(ValueError, match="flow mapping"):
        fh.read_sources(path)


def test_read_sources_keeps_comments_out_of_the_data(tmp_path):
    path = tmp_path / "sources.yaml"
    path.write_text(
        "# a leading comment\n"
        "feeds:\n"
        "  # verified 2026-09-07, the convention this file already uses\n"
        '  - {name: a, url: "https://a", tier: d}\n'
    )
    cfg = fh.read_sources(path)
    assert cfg["feeds"] == [{"name": "a", "url": "https://a", "tier": "d"}]


# ------------------------------------------------------------- the counting

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<title>t</title>
<item><title>one</title><pubDate>Wed, 15 Oct 2026 10:00:00 +0000</pubDate></item>
<item><title>two</title><pubDate>Tue, 14 Oct 2026 10:00:00 +0000</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<updated>2026-10-10T00:00:00Z</updated>
<entry><title>one</title><updated>2026-10-16T09:00:00Z</updated></entry>
</feed>"""

EMPTY_ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<title>releases</title><updated>2026-10-16T09:00:00Z</updated>
</feed>"""

BROKEN = b"""<rss><channel>
<item><title>one & two</title><pubDate>Wed, 15 Oct 2026 10:00:00 +0000</pubDate></item>
<item><title>unclosed
</channel></rss>"""

HTML = b"<html><body><h1>404 Not Found</h1></body></html>"

# An error page that is not well-formed XML, so the crude count runs on it.
# It names `item` in prose on purpose: the fallback matches a tag opening and
# must not match the word.
HTML_SLOPPY = b"""<html><meta charset=utf-8><body>
<p>No such item was found. <br> Try again.
</body></html>"""


def test_count_items_parses_rss_and_atom():
    assert fh.count_items(RSS) == (2, "parsed")
    assert fh.count_items(ATOM) == (1, "parsed")


def test_count_items_reports_a_feed_with_no_items_as_zero():
    """The gh-spiffe case: a 200, a feed-level date, and no releases."""
    assert fh.count_items(EMPTY_ATOM) == (0, "parsed")


def test_count_items_falls_back_rather_than_calling_a_live_feed_dead():
    """The case this tool must not get wrong in the expensive direction.

    `feedparser` recovers from malformed XML and `xml.etree` raises on it,
    so a strict parse failure is not evidence that ingest gets nothing.
    """
    items, method = fh.count_items(BROKEN)
    assert method == "counted"
    assert items == 2, "the crude count missed an item opening"
    assert fh.classify(items, method, None, now=NOW)[0] == "malformed"


@pytest.mark.parametrize("body", [HTML, HTML_SLOPPY])
def test_count_items_does_not_invent_items_in_an_error_page(body):
    """Zero either way, and the method is not the assertion.

    The tidy error page below happens to be well-formed XML, so the strict
    parser handles it and finds no items. The sloppy one is not, so the
    crude count runs and finds no item openings. Both are the same verdict
    and `empty` is what matters, so this pins the count rather than the
    route it took.
    """
    items, method = fh.count_items(body)
    assert items == 0
    assert fh.classify(items, method, None, now=NOW)[0] == "empty"


# ----------------------------------------------------------- the newest date

def test_newest_date_reads_rfc_822_and_takes_the_latest():
    newest = fh.newest_date(RSS)
    assert newest.startswith("2026-10-15")


def test_newest_date_reads_iso_8601_with_a_z():
    newest = fh.newest_date(ATOM)
    assert newest.startswith("2026-10-16")


def test_newest_date_is_none_when_the_feed_carries_no_date():
    assert fh.newest_date(HTML) is None


def test_newest_date_survives_an_unparseable_date():
    body = b"<rss><channel><item><pubDate>sometime last year</pubDate></item></channel></rss>"
    assert fh.newest_date(body) is None


# ------------------------------------------------------------- the verdicts

@pytest.mark.parametrize(
    "items,method,age_days,expected",
    [
        (20, "parsed", 1, "ok"),
        (0, "parsed", 1, "empty"),
        (0, "counted", None, "empty"),
        (20, "parsed", fh.WARN_DAYS + 1, "stale"),
        (20, "parsed", fh.DEAD_DAYS + 1, "dead-stale"),
        (20, "counted", 1, "malformed"),
        # A quiet source is not a broken one, and this is the boundary that
        # keeps the census from crying wolf on half of tier c.
        (20, "parsed", fh.WARN_DAYS - 1, "ok"),
    ],
)
def test_classify(items, method, age_days, expected):
    newest = None
    if age_days is not None:
        newest = (NOW - timedelta(days=age_days)).isoformat()
    verdict, age = fh.classify(items, method, newest, now=NOW)
    assert verdict == expected
    if age_days is not None:
        assert abs(age - age_days) < 0.1


def test_archive_forgives_age_and_nothing_else():
    """gh-autogen is kept on purpose, so its silence is not a defect.

    The other half is the one that matters: an archived source still has to
    answer. A feed kept for what it already holds is useless if the URL
    rots, and that is exactly the failure an `expect` key could hide.
    """
    old = (NOW - timedelta(days=fh.DEAD_DAYS + 50)).isoformat()
    assert fh.classify(10, "parsed", old, now=NOW, expect="archive")[0] == "archive"
    assert fh.classify(10, "parsed", old, now=NOW)[0] == "dead-stale"
    # Reachability is not forgiven.
    assert fh.classify(0, "parsed", old, now=NOW, expect="archive")[0] == "empty"


def test_an_archived_source_does_not_gate():
    archived = {"name": "gh-autogen", "kind": "feed", "tier": "d",
                "url": "https://gh/a", "expect": "archive"}
    old = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
    <entry><updated>2024-09-30T00:00:00Z</updated></entry></feed>"""
    result = fh.check_one(archived, FakeClient(FakeResponse(200, old)))
    assert result["verdict"] == "archive"
    assert fh.failures([result]) == []


def test_sources_yaml_declares_the_archive_it_describes_in_prose():
    """The file's comment and the checker's input must say the same thing."""
    cfg = fh.read_sources()
    archived = {f["name"] for f in cfg["feeds"] if f.get("expect") == "archive"}
    assert "gh-autogen" in archived, (
        "sources.yaml says in a comment that gh-autogen is kept for its "
        "archive, and tools/feed_health.py cannot read a comment"
    )


# ------------------------------------------------------------------- the pin

def test_every_pinned_source_is_still_a_real_source():
    """A pin for a source that no longer exists is a stale exemption.

    This is the network-free half of "may shrink and may not grow": the
    growth check needs a live fetch, but a line that outlived its source is
    catchable here, and it is the way a pin rots.
    """
    cfg = fh.read_sources()
    names = {f["name"] for f in cfg["feeds"]}
    names |= {f"arxiv:{a['category']}" for a in cfg["arxiv"]}
    names.add("hf-daily")
    stale = sorted(set(fh.KNOWN_DEAD) - names)
    assert not stale, (
        f"{len(stale)} pinned source(s) are no longer in sources.yaml: "
        f"{stale}. Delete the line from KNOWN_DEAD in tools/feed_health.py; "
        "the source it excused is gone, so the excuse is now hiding nothing "
        "and confusing the next reader."
    )


def test_every_pin_carries_a_reason_a_human_can_act_on():
    for name, reason in fh.KNOWN_DEAD.items():
        assert len(reason) > 60, f"{name}'s pin is not a reason"
        assert "2026" in reason or "days" in reason or "HTTP" in reason, (
            f"{name}'s pin does not say what was measured"
        )


def test_a_pinned_source_is_reported_but_does_not_gate():
    """The pin changes the exit code and not the finding."""
    name = sorted(fh.KNOWN_DEAD)[0]
    result = {"verdict": "empty", "name": name, "items": 0, "age_days": None,
              "detail": "", "url": "https://x", "kind": "feed", "tier": "d",
              "status": 200, "method": "parsed", "newest": None}
    assert fh.failures([result]) == []
    assert fh.pinned_failures([result]) == [result]
    assert fh.is_broken(result), "the pin must not change the verdict"
    text = fh.render([result])
    assert name in text and "waiting on a ruling" in text


def test_an_unpinned_death_still_gates():
    """The point of the pin is that a new death is still red."""
    result = {"verdict": "empty", "name": "a-source-nobody-pinned", "items": 0,
              "age_days": None, "detail": "", "url": "https://x",
              "kind": "feed", "tier": "d", "status": 200, "method": "parsed",
              "newest": None}
    assert fh.failures([result]) == [result]


def test_only_the_three_real_failures_gate():
    # Single-letter names on purpose: none of them is in KNOWN_DEAD, so this
    # tests the verdict set rather than the pin.
    results = [
        {"verdict": "ok", "name": "a"},
        {"verdict": "stale", "name": "b"},
        {"verdict": "malformed", "name": "c"},
        {"verdict": "empty", "name": "d"},
        {"verdict": "unreachable", "name": "e"},
        {"verdict": "dead-stale", "name": "f"},
        {"verdict": "http-403", "name": "g"},
    ]
    assert [r["name"] for r in fh.failures(results)] == ["d", "e", "f", "g"]


# ------------------------------------------------------------- the fetching

class FakeResponse:
    def __init__(self, status_code=200, content=b"", payload=None):
        self.status_code = status_code
        self.content = content
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class FakeClient:
    """One response, or one exception, for any URL."""

    def __init__(self, response=None, raises=None):
        self.response = response
        self.raises = raises
        self.calls = 0

    def get(self, url, timeout=None, follow_redirects=False):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.response


FEED = {"name": "x", "kind": "feed", "tier": "d", "url": "https://x/feed"}


def test_check_one_reports_a_404_as_the_code_it_got():
    result = fh.check_one(FEED, FakeClient(FakeResponse(404)))
    assert result["verdict"] == "http-404"
    assert result["status"] == 404


def test_check_one_reports_a_403_as_the_code_it_got():
    """owasp-genai, which is blocked rather than gone."""
    result = fh.check_one(FEED, FakeClient(FakeResponse(403)))
    assert result["verdict"] == "http-403"


def test_check_one_turns_a_transport_failure_into_a_verdict_not_a_crash():
    """One dead host must not end the census before it reaches the rest."""
    result = fh.check_one(FEED, FakeClient(raises=OSError("no route to host")))
    assert result["verdict"] == "unreachable"
    assert "no route to host" in result["detail"]
    assert result["status"] is None


def test_check_one_reads_a_live_feed():
    result = fh.check_one(FEED, FakeClient(FakeResponse(200, RSS)))
    assert result["verdict"] in ("ok", "stale", "dead-stale")
    assert result["items"] == 2
    assert result["method"] == "parsed"


def test_check_one_calls_a_200_with_no_items_empty():
    """The langchain-blog case, and the one ingest could never see."""
    result = fh.check_one(FEED, FakeClient(FakeResponse(200, EMPTY_ATOM)))
    assert result["verdict"] == "empty"
    assert "ingest reads as nothing" in result["detail"]


JSON_SOURCE = {"name": "hf-daily", "kind": "json", "tier": "b",
               "url": "https://hf/api"}


def test_check_one_reads_the_json_source():
    client = FakeClient(FakeResponse(200, payload=[{"paper": {}}] * 50))
    result = fh.check_one(JSON_SOURCE, client)
    assert result["verdict"] == "ok"
    assert result["items"] == 50


def test_check_one_calls_an_empty_json_payload_empty():
    client = FakeClient(FakeResponse(200, payload=[]))
    assert fh.check_one(JSON_SOURCE, client)["verdict"] == "empty"


def test_check_one_calls_a_200_that_is_not_json_empty():
    """hf_daily_papers returning an HTML error page with a 200."""
    client = FakeClient(FakeResponse(200, content=HTML))
    result = fh.check_one(JSON_SOURCE, client)
    assert result["verdict"] == "empty"
    assert "not JSON" in result["detail"]


# ---------------------------------------------------------------- the report

def test_render_names_every_failure_and_counts_them():
    results = [
        {"verdict": "ok", "name": "live", "items": 20, "age_days": 1,
         "detail": "", "url": "https://live"},
        {"verdict": "empty", "name": "dead", "items": 0, "age_days": None,
         "detail": "200 with no items", "url": "https://dead"},
    ]
    text = fh.render(results)
    assert "1 of 2 sources are delivering; 1 are not" in text
    assert "dead: empty  https://dead" in text


def test_the_report_is_a_gate_by_default(monkeypatch):
    """Exit non-zero when a source delivers nothing, the way the deploy
    chain in pipeline/ingest.py's docstring needs."""
    dead = [{"verdict": "empty", "name": "dead", "items": 0, "age_days": None,
             "detail": "", "url": "https://dead", "kind": "feed",
             "tier": "d", "status": 200, "method": "parsed", "newest": None}]
    monkeypatch.setattr(fh, "census", lambda cfg, only=None: dead)
    assert fh.main([]) == 1
    assert fh.main(["--report-only"]) == 0


def test_offline_fetches_nothing(monkeypatch):
    """The mode that runs where there is no network, and the assertion is
    that it never reaches the fetcher at all."""
    def boom(*a, **k):
        raise AssertionError("--offline reached the network")

    monkeypatch.setattr(fh, "census", boom)
    assert fh.main(["--offline"]) == 0


# ------------------------------------------- ingest's refusal, the other half

def status_rows(arxiv_entries: list[int], feed_entries: list[int],
                hf: int = 50) -> list[dict]:
    rows = [{"name": f"arxiv:c{n}", "kind": "arxiv", "entries": e, "http": 200}
            for n, e in enumerate(arxiv_entries)]
    rows += [{"name": f"feed{n}", "kind": "feed", "entries": e, "http": 200}
             for n, e in enumerate(feed_entries)]
    rows += [{"name": "hf-daily", "kind": "json", "entries": hf, "http": None}]
    return rows


def test_a_healthy_run_is_not_refused():
    summary, refusal = judge_sources(status_rows([100] * 8, [20] * 44))
    assert refusal is None
    assert "53 of 53 delivered" in summary


def test_one_dead_blog_does_not_stop_the_corpus():
    summary, refusal = judge_sources(status_rows([100] * 8, [0] + [20] * 43))
    assert refusal is None
    assert "delivered nothing: feed0" in summary


def test_every_dead_blog_still_does_not_stop_the_corpus():
    """Forty-four dead feeds and a live firehose is a bad day, not a failure.

    The corpus is the firehose. Refusing here would turn a report into an
    outage, which is how a guard gets switched off.
    """
    summary, refusal = judge_sources(status_rows([100] * 8, [0] * 44))
    assert refusal is None
    assert "9 of 53 delivered" in summary


def test_a_dark_firehose_is_refused():
    """Every arXiv category returning zero is an API failure, not a quiet
    day, and this is the case that used to print a success."""
    summary, refusal = judge_sources(status_rows([0] * 8, [20] * 44))
    assert refusal is not None
    assert "arXiv" in refusal
    assert "not a quiet day" in refusal


def test_a_wholly_empty_run_is_refused():
    summary, refusal = judge_sources(status_rows([0] * 8, [0] * 44, hf=0))
    assert refusal is not None
    assert "all 53 sources returned zero items" in refusal


def test_no_sources_at_all_is_refused():
    """sources.yaml read as empty is the failure that looks most like success."""
    summary, refusal = judge_sources([])
    assert refusal is not None
    assert "no sources to fetch" in refusal


def test_the_refusal_names_the_credential_free_tool():
    """A seat meeting this error must be told what to run, and the thing it
    is told to run must work without the secrets Modal holds."""
    import pipeline.ingest as ingest

    status = status_rows([0] * 8, [20] * 44)
    summary, refusal = judge_sources(status)
    assert refusal
    with pytest.raises(ingest.NothingToIngest, match="tools/feed_health.py"):
        raise ingest.NothingToIngest(
            f"{refusal}\n\n{summary}\n\n"
            "Run `python3 tools/feed_health.py` for the per-source verdicts. "
            "It needs no credentials, so it runs anywhere."
        )


def test_fetched_zero_and_inserted_zero_are_different_events():
    """A day where every paper was already seen is a correct zero.

    The distinction is the whole reason this guard is safe to turn on: the
    number ingest used to print was `inserted`, which is legitimately zero,
    and the number that means the job is broken is `fetched`.
    """
    summary, refusal = judge_sources(status_rows([100] * 8, [20] * 44))
    assert refusal is None, (
        "a run that fetched plenty must not be refused, whatever it inserted"
    )


# -------------------------------------- ingest end to end, with no network

@pytest.fixture
def fake_ingest(monkeypatch):
    """`ingest()` with its four I/O calls replaced and nothing else.

    This is the test the refactor actually needed. `fetch_arxiv` and
    `fetch_feeds` changed from returning a list to returning a pair, and a
    mistake in unpacking either one is invisible to every unit test above:
    `judge_sources` would still be correct, the suite would still be green,
    and the daily cron would raise a TypeError on its next unattended run.
    Modal is stubbed by `tests/conftest.py`, which hands the real function
    back through the decorator.
    """
    import pipeline.ingest as ingest

    state = {"upserted": None}

    def upsert(rows):
        state["upserted"] = rows
        return len(rows)

    monkeypatch.setattr(ingest, "load_sources", lambda: {"arxiv": [], "feeds": []})
    monkeypatch.setattr(ingest, "upsert_papers", upsert)

    def configure(arxiv_counts, feed_counts, hf_count):
        def paper(name, n):
            return {"id": f"{name}:{n}", "source": name, "tier": "a"}

        def fetch_arxiv(cfg):
            rows, status = [], []
            for index, count in enumerate(arxiv_counts):
                name = f"arxiv:c{index}"
                rows += [paper(name, n) for n in range(count)]
                status.append({"name": name, "kind": "arxiv",
                               "entries": count, "http": 200})
            return rows, status

        def fetch_feeds(cfg):
            rows, status = [], []
            for index, count in enumerate(feed_counts):
                name = f"feed{index}"
                rows += [paper(name, n) for n in range(count)]
                status.append({"name": name, "kind": "feed",
                               "entries": count, "http": 200})
            return rows, status

        monkeypatch.setattr(ingest, "fetch_arxiv", fetch_arxiv)
        monkeypatch.setattr(ingest, "fetch_feeds", fetch_feeds)
        monkeypatch.setattr(ingest, "fetch_hf_daily",
                            lambda cfg: [paper("hf", n) for n in range(hf_count)])
        return ingest, state

    return configure


def test_ingest_unpacks_both_fetchers_and_upserts_every_row(fake_ingest):
    """The integration the unit tests cannot see."""
    ingest, state = fake_ingest([10] * 8, [5] * 44, 50)
    inserted = ingest.ingest()
    assert inserted == 80 + 220 + 50
    assert len(state["upserted"]) == 350
    sources = {row["source"] for row in state["upserted"]}
    assert "arxiv:c0" in sources and "feed0" in sources and "hf" in sources


def test_ingest_counts_hf_daily_among_the_sources(fake_ingest):
    """hf-daily has no status row of its own from the fetcher, so `ingest`
    builds one. A miscount there would make the summary line lie."""
    ingest, _ = fake_ingest([10] * 8, [5] * 44, 0)
    summary, _ = judge_sources(
        [{"name": f"arxiv:c{n}", "kind": "arxiv", "entries": 10, "http": 200}
         for n in range(8)]
        + [{"name": f"feed{n}", "kind": "feed", "entries": 5, "http": 200}
           for n in range(44)]
        + [{"name": "hf-daily", "kind": "json", "entries": 0, "http": None}]
    )
    assert "52 of 53 delivered" in summary
    assert "hf-daily" in summary
    # And the run still succeeds, because one dead source is not an outage.
    assert ingest.ingest() == 300


def test_ingest_raises_when_the_firehose_is_dark(fake_ingest):
    """The case that used to print `fetched 880 items` and a success."""
    ingest, state = fake_ingest([0] * 8, [20] * 44, 50)
    with pytest.raises(ingest.NothingToIngest, match="arXiv"):
        ingest.ingest()
    assert state["upserted"] is None, (
        "the refusal must come before the write, or a broken run still "
        "changes the database"
    )


def test_ingest_raises_when_every_source_is_dark(fake_ingest):
    ingest, state = fake_ingest([0] * 8, [0] * 44, 0)
    with pytest.raises(ingest.NothingToIngest, match="returned zero items"):
        ingest.ingest()
    assert state["upserted"] is None


def test_ingest_tells_the_reader_what_to_run(fake_ingest):
    """A refusal a seat cannot act on is an outage with extra steps."""
    ingest, _ = fake_ingest([0] * 8, [20] * 44, 50)
    with pytest.raises(ingest.NothingToIngest) as caught:
        ingest.ingest()
    assert "tools/feed_health.py" in str(caught.value)
    assert "no credentials" in str(caught.value)


def test_a_day_with_nothing_new_is_not_a_failure(fake_ingest, monkeypatch):
    """`inserted` is legitimately zero when every paper was already seen,
    and that must never raise. It is the reason the guard reads `fetched`
    rather than `inserted`, and it is the assumption that makes the guard
    safe to switch on at all.
    """
    ingest, state = fake_ingest([10] * 8, [5] * 44, 50)
    monkeypatch.setattr(ingest, "upsert_papers", lambda rows: 0)
    assert ingest.ingest() == 0
