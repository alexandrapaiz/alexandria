"""Ingest: pull new papers from the sources in sources.yaml into the bronze layer.

Runs daily on Modal. Requires the `neon` secret (DATABASE_URL).

    modal run pipeline/ingest.py        # one-off manual run
    modal deploy pipeline/ingest.py     # install the daily schedule

Before a deploy, the availability check this job's sources need:

    python3 tools/feed_health.py && modal deploy pipeline/ingest.py

That is the link `docs/agents/press-rehearsal.md` asks for in its closing
section. This job calls no model, so it needs neither that file's
`preflight` nor its `rehearse`. What it needs is to know that the
fifty-three sources it fetches are still answering, and it had no way to
know until 2026-10-16: `feedparser.parse(url)` does not raise, so a feed
that 404s or moved returned an empty `entries` list, the loop added
nothing, and this job printed a four-digit `fetched` count because the
arXiv firehose dominates it either way. Seven of the fifty-three were
delivering nothing on the day the check was written
(`docs/evals/2026-10-16-feed-health.json`), the oldest of them silent
since 2019.

So `fetch_arxiv` and `fetch_feeds` now report per-source counts to the
caller instead of only to the log, and `ingest` refuses to return a
success when the run fetched nothing at all. Fetching nothing and
inserting nothing are different events and only the first is a failure:
a day where every paper was already seen is a correct zero.

The arXiv half of the job changed on 2026-10-26 and the constants below say
why at length. In one line: the window is a date range paged to exhaustion
from the newest submission date already in `papers`, so a day this cron does
not run costs a day of latency rather than a day of papers. It used to be the
hundred most recent papers per category, which two of the eight categories
overflow every day.
"""

import datetime as dt
import hashlib
import pathlib
import time

import modal

# The firehose's window, and until 2026-10-26 it was one number. The query was
# `sortBy=submittedDate&sortOrder=descending&max_results=100` with no date
# bound, so a run saw the hundred most recent papers in a category and nothing
# else. A paper that fell out of that window was not delayed, it was gone,
# because nothing ever asked for it again.
#
# The monthly source census measured what that cost
# (docs/research/notes/2026-10-26-source-census.md section 2). Two of the eight
# listed categories submit more papers a day than the window holds: cs.AI at
# 116 a day and cs.LG at 114, which are the two largest and the two the skills
# literature lives in. The other six have between 1.6 and 12.1 days of slack.
# So the overflow in those two was lost on most days, and the 3.33 days this
# cron spent stopped put somewhere between 290 and 570 papers permanently out
# of reach, growing by about 130 a day
# (INC-2026-10-26-the-arxiv-window-is-smaller-than-two-of-the-categories-behind-it).
#
# The repair is that the window is a date range and 100 is only a page size.
# A run asks arXiv for everything submitted since the newest submission date
# already in `papers` and pages until the range is exhausted, so a missed run
# costs latency instead of records, which is what the census asked for.
ARXIV_PAGE = 100  # rows per request; arXiv's own paging unit
# A ceiling per category per run, so a cursor that is somehow very old cannot
# turn one run into an unbounded crawl. 2,000 is 14 days of cs.AI at the
# measured 116 a day with slack, which is the longest lookback below, so this
# is a guard against a bad cursor rather than a limit on an ordinary backlog.
# When it does bind, the category's status row says so instead of going quiet.
ARXIV_MAX_PER_CAT = 2000
# No arXiv rows in `papers` yet, so there is no cursor to page back to. Two
# days is the census's floor: one day of cs.AI already overflows 100.
ARXIV_LOOKBACK_DAYS = 2
# arXiv announces on weekdays and a paper is searchable by submission date
# only once it is announced, so the newest date we hold is never proof that we
# hold that whole day, and the lag is not one day. Measured live on 2026-10-26
# at 19:00Z against this job's own query: the newest announced cs.CL
# submission date was 2026-10-23, three days back, because nothing announces
# over a weekend. So the window reaches back past the cursor far enough to
# cover a weekend and a day, which is what stops the cursor from stepping over
# papers that were not yet announced when it moved. The upsert discards what
# it has already seen, so the overlap costs requests and not rows.
ARXIV_CURSOR_OVERLAP_DAYS = 4
# The furthest back any cursor may send a single run. Past this the backlog is
# a backfill job and not a daily ingest, and it should be run deliberately.
ARXIV_MAX_LOOKBACK_DAYS = 14
# arXiv asks callers to pause between requests, the same 3.0 seconds
# tools/feed_health.py waits.
ARXIV_DELAY = 3.0
# Wall clock for the whole firehose, under this job's timeout=900. Paging is
# the first thing here that can grow with the size of the backlog, and a run
# that overruns the Modal timeout loses the feeds and the upsert too, which
# would make a deep backlog worse rather than better. On the budget, a
# category stops short and says which.
ARXIV_BUDGET_S = 420.0

image = (
    modal.Image.debian_slim()
    .pip_install(
        "feedparser==6.0.11",
        "psycopg[binary]==3.2.4",
        "pyyaml==6.0.2",
        "httpx==0.28.1",
    )
    .add_local_file("sources.yaml", "/root/sources.yaml")
    # The drift guard, so this job can say which deploy it is. Added 2026-10-09:
    # ingest was one of the two scheduled apps the guard never watched, and it
    # is the stage that fills `papers`.
    .add_local_file("pipeline/runtime_sha.py", "/root/runtime_sha.py")
)

app = modal.App("alexandria-ingest", image=image)


def load_sources() -> dict:
    import yaml

    return yaml.safe_load(open("/root/sources.yaml"))


def pub_date(entry) -> str | None:
    """Feeds disagree on date formats (arXiv: ISO 8601, blogs: RFC 822);
    feedparser's parsed struct_time normalizes both."""
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if t is None:
        return None
    return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"


def arxiv_window(cursor: str | None, today: dt.date) -> tuple[dt.date, dt.date]:
    """The `submittedDate` range one run asks every category for.

    `cursor` is the newest arXiv submission date already in `papers`, as a
    `YYYY-MM-DD` string, or None when the corpus holds no arXiv paper yet.
    The returned range is inclusive of its first day and runs to tomorrow, so
    that papers submitted today are inside it in every timezone.

    Three bounds, and each one is a failure this would otherwise have:
    the overlap, because the newest date we hold is not proof we hold all of
    it; the floor, so a cursor from a long outage does not turn a daily job
    into a crawl; and the clamp to today, so a row with a future
    `published_at` cannot produce a range that starts after it ends.
    """
    if cursor:
        since = dt.date.fromisoformat(cursor) - dt.timedelta(days=ARXIV_CURSOR_OVERLAP_DAYS)
    else:
        since = today - dt.timedelta(days=ARXIV_LOOKBACK_DAYS)
    floor = today - dt.timedelta(days=ARXIV_MAX_LOOKBACK_DAYS)
    since = min(max(since, floor), today)
    return since, today + dt.timedelta(days=1)


def arxiv_url(cat: str, since: dt.date, until: dt.date, start: int = 0) -> str:
    """One page of one category, in arXiv's own query language.

    The brackets are percent-encoded and the spaces are `+`, which is the
    form the census verified against the live API rather than the form that
    reads best.
    """
    window = f"submittedDate:%5B{since:%Y%m%d}0000+TO+{until:%Y%m%d}0000%5D"
    return (
        "https://export.arxiv.org/api/query"
        f"?search_query=cat:{cat}+AND+{window}"
        "&sortBy=submittedDate&sortOrder=descending"
        f"&start={start}&max_results={ARXIV_PAGE}"
    )


def arxiv_id_url(ids: list[str]) -> str:
    """The `id_list` query, which is the firehose's query without the window.

    `max_results` is the count asked for rather than `ARXIV_PAGE`, because this
    is a named list and not a walk: there is no page after the last id.
    """
    cleaned = ",".join(normalise_arxiv_id(i) for i in ids)
    return (
        "https://export.arxiv.org/api/query"
        f"?id_list={cleaned}"
        f"&start=0&max_results={max(len(ids), 1)}"
    )


def normalise_arxiv_id(value: str) -> str:
    """`arxiv:2609.08371v2`, a url or a bare id, as the id arXiv's api takes."""
    text = (value or "").strip()
    text = text.rsplit("/", 1)[-1] if "/" in text else text
    if text.lower().startswith("arxiv:"):
        text = text[6:]
    return text.strip()


def fetch_arxiv_ids(ids: list[str], tier: str = "b", parse=None) -> tuple[list[dict], list[dict]]:
    """Named papers, fetched by id rather than found by a window.

    **The gap this closes, which is not the one anybody was fixing.** The daily
    job queries each category sorted by submission date descending and stops at
    a ceiling, so its reach is a window a few days deep: `cs.SE` ran 639 papers
    in September 2026, about twenty-one a day, which is roughly five days. A
    paper submitted before the window's edge on the day a category shipped was
    never inside it, and the window only moves forward, so no run of the cron on
    any day since would have fetched it and none ever will. That is a backfill
    gap and not a missed run, and the research seat measured it on the whole
    addendum rather than one paper: the comment justifying one category named
    six papers by id, and the window could reach zero of six, the newest of them
    twelve days older than the edge on the day the category shipped
    (`INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written`).

    Tier `b` by default, which is the curated tier `fetch_hf_daily` writes and
    which `upsert_papers` lets upgrade a row the firehose already saw. Naming a
    paper by id is a human picking it, so it gets the same standing.

    Writes `arxiv:<id>`, the same key space as the firehose and hf-daily, so a
    backfilled paper and a fetched one are one row.
    """
    if parse is None:
        import feedparser

        parse = feedparser.parse
    asked = [normalise_arxiv_id(i) for i in ids if normalise_arxiv_id(i)]
    if not asked:
        return [], [{"name": "arxiv:by-id", "kind": "arxiv", "entries": 0,
                     "http": None, "asked": 0, "missing": []}]

    feed = parse(arxiv_id_url(asked))
    rows, found = [], set()
    for e in feed.entries:
        arxiv_id = e.id.rsplit("/", 1)[-1]
        found.add(arxiv_id.split("v")[0])
        rows.append(
            {
                "id": f"arxiv:{arxiv_id}",
                "source": "arxiv",
                "tier": tier,
                "title": " ".join(e.title.split()),
                "authors": [a.name for a in getattr(e, "authors", [])],
                "abstract": " ".join(getattr(e, "summary", "").split()),
                "url": e.link,
                "published_at": pub_date(e),
            }
        )
    # An id that came back with nothing is reported rather than counted as a
    # quiet success. A backfill asked for six papers and silently landing four
    # is the shape of defect this entrypoint exists to repair.
    missing = sorted({i.split("v")[0] for i in asked} - found)
    print(f"arxiv by-id: asked {len(asked)}, got {len(rows)}"
          + (f", missing {missing}" if missing else ""))
    return rows, [{"name": "arxiv:by-id", "kind": "arxiv", "entries": len(rows),
                   "http": getattr(feed, "status", None),
                   "asked": len(asked), "missing": missing}]


def fetch_arxiv(
    cfg: dict,
    cursor: str | None = None,
    today: dt.date | None = None,
    parse=None,
    sleep=time.sleep,
    clock=time.monotonic,
) -> tuple[list[dict], list[dict]]:
    """The firehose, and one status row per category.

    Each category is paged until the window is exhausted, which is the whole
    repair: the run takes everything submitted since the cursor instead of the
    hundred most recent, so a day this job does not run is a day of latency
    rather than a day of papers nobody will ever ask for again.

    The status rows are the point of the rest. A category that returns nothing
    used to be indistinguishable from a quiet day, and cs.SE and cs.CR were
    each added to sources.yaml to close a measured hole in the corpus, so a
    category going dark undoes that work in silence. `truncated` is the same
    argument for the new failure mode: a category that stopped short of its
    own window has lost records, and it says which bound stopped it.

    `parse`, `sleep` and `clock` are injected so the paging, the ceiling and
    the budget are testable with no network and no three-second waits.
    """
    if parse is None:
        import feedparser

        parse = feedparser.parse
    today = today or dt.date.today()
    since, until = arxiv_window(cursor, today)
    deadline = clock() + ARXIV_BUDGET_S

    rows = []
    status = []
    for entry in cfg["arxiv"]:
        cat, tier = entry["category"], entry["tier"]
        offset, pages, http, truncated = 0, 0, None, None
        seen: set[str] = set()
        while True:
            feed = parse(arxiv_url(cat, since, until, offset))
            pages += 1
            http = getattr(feed, "status", None)
            page = list(feed.entries)
            for e in page:
                arxiv_id = e.id.rsplit("/", 1)[-1]
                # A submission arriving mid-page-walk shifts a descending sort,
                # so the same paper can land on two pages. The upsert would
                # discard the second copy anyway; this keeps the count honest.
                if arxiv_id in seen:
                    continue
                seen.add(arxiv_id)
                rows.append(
                    {
                        "id": f"arxiv:{arxiv_id}",
                        "source": "arxiv",
                        "tier": tier,
                        "title": " ".join(e.title.split()),
                        "authors": [a.name for a in getattr(e, "authors", [])],
                        "abstract": " ".join(getattr(e, "summary", "").split()),
                        "url": e.link,
                        "published_at": pub_date(e),
                    }
                )
            offset += len(page)
            if len(page) < ARXIV_PAGE:
                break  # the window is exhausted, which is the ordinary exit
            if offset >= ARXIV_MAX_PER_CAT:
                truncated = f"stopped at the {ARXIV_MAX_PER_CAT}-row ceiling"
                break
            if clock() >= deadline:
                truncated = f"stopped on the {ARXIV_BUDGET_S:.0f}s firehose budget"
                break
            sleep(ARXIV_DELAY)
        print(f"arxiv {cat}: {len(seen)} entries since {since.isoformat()} "
              f"in {pages} page(s) (http {http if http is not None else '?'})"
              + (f" -- {truncated}" if truncated else ""))
        status.append({"name": f"arxiv:{cat}", "kind": "arxiv",
                       "entries": len(seen),
                       "pages": pages,
                       "since": since.isoformat(),
                       "truncated": truncated,
                       "http": http})
    return rows, status


def arxiv_cursor(conn) -> str | None:
    """The newest arXiv submission date in `papers`, which is where to resume.

    `source = 'arxiv'` and not the `arxiv:` id prefix: hf-daily writes into
    the same key space on purpose, so that a curated pick upgrades a paper the
    firehose already saw, and its dates say when a human picked the paper
    rather than how far this query has reached.
    """
    with conn.cursor() as cur:
        cur.execute("select max(published_at) from papers where source = 'arxiv'")
        row = cur.fetchone()
    value = row[0] if row else None
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)[:10]


def read_arxiv_cursor() -> str | None:
    """`arxiv_cursor` against the real database, or None and a reason.

    Soft on purpose. With no cursor the window is still the two-day floor,
    which is more than the hundred-row window this replaces, and `upsert_papers`
    is one connection later and fails loudly if the database is really gone.
    Refusing to fetch here would turn a database blip into a lost day of arXiv,
    which is the exact cost this whole change exists to stop paying.
    """
    try:
        import os

        import psycopg

        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            return arxiv_cursor(conn)
    except Exception as exc:
        print(f"arxiv cursor unreadable ({exc.__class__.__name__}: {exc}); "
              f"falling back to the {ARXIV_LOOKBACK_DAYS}-day window")
        return None


def fetch_feeds(cfg: dict) -> tuple[list[dict], list[dict]]:
    """The blogs and release feeds, and one status row per source.

    `tools/feed_health.py` is the richer reading of the same question and
    it runs before a deploy. This is the cheap version that runs on every
    ingest, so a feed that dies between deploys is in the day's own log.
    """
    import feedparser

    rows = []
    status = []
    for f in cfg["feeds"]:
        feed = feedparser.parse(f["url"])
        # `bozo` is feedparser saying it recovered from malformed XML. It is
        # not a failure on its own, because feedparser is lenient on purpose
        # and most of these feeds trip it, so it is printed and not judged.
        print(f"feed {f['name']}: {len(feed.entries)} entries "
              f"(http {getattr(feed, 'status', '?')}, "
              f"bozo {int(getattr(feed, 'bozo', 0))})")
        status.append({"name": f["name"], "kind": "feed",
                       "entries": len(feed.entries),
                       "http": getattr(feed, "status", None)})
        for e in feed.entries:
            link = getattr(e, "link", None)
            if not link:
                continue
            digest = hashlib.sha256(link.encode()).hexdigest()[:16]
            rows.append(
                {
                    "id": f"blog:{f['name']}:{digest}",
                    "source": f["name"],
                    "tier": f["tier"],
                    "title": " ".join(getattr(e, "title", "untitled").split()),
                    "authors": [f["name"]],
                    "abstract": " ".join(getattr(e, "summary", "").split())[:4000],
                    "url": link,
                    "published_at": pub_date(e),
                }
            )
    return rows, status


def fetch_hf_daily(cfg: dict) -> list[dict]:
    import httpx

    hf = cfg["hf_daily_papers"]
    try:
        items = httpx.get(hf["url"], timeout=30).json()
    except Exception as exc:
        print(f"hf_daily_papers failed: {exc}")
        return []
    rows = []
    for item in items:
        paper = item.get("paper") or {}
        pid = paper.get("id")
        if not pid:
            continue
        rows.append(
            {
                "id": f"arxiv:{pid}",  # same key space as the firehose, so it upgrades
                "source": "hf-daily",
                "tier": hf["tier"],
                "title": " ".join((paper.get("title") or "untitled").split()),
                "authors": [a.get("name") for a in paper.get("authors", []) if a.get("name")],
                "abstract": " ".join((paper.get("summary") or "").split()),
                "url": f"https://arxiv.org/abs/{pid}",
                "published_at": (paper.get("publishedAt") or "")[:10] or None,
            }
        )
    print(f"hf-daily: {len(rows)} papers")
    return rows


class NothingToIngest(RuntimeError):
    """The run reached no source at all, so a success would be a lie.

    Deliberately narrow. One dead blog must not stop the corpus, because
    forty-four of the fifty-three sources are tier c and d and the firehose
    is what fills `papers`. This raises only when the whole run came back
    empty, or when every arXiv category did, which is the signature of the
    API changing under the job rather than of a quiet day.
    """


def judge_sources(status: list[dict]) -> tuple[str, str | None]:
    """A summary line for the log, and the reason to refuse, or None.

    Separated from `ingest` so it can be tested without a network or a
    database, which is the only way a guard against a silent failure gets
    exercised before the silent failure happens.
    """
    dark = [s["name"] for s in status if not s["entries"]]
    arxiv = [s for s in status if s["kind"] == "arxiv"]
    total = sum(s["entries"] for s in status)

    summary = (
        f"sources: {len(status) - len(dark)} of {len(status)} delivered, "
        f"{total} items fetched"
    )
    if dark:
        summary += f"; delivered nothing: {', '.join(dark)}"

    # A category that stopped short of its window is not a refusal, because
    # what it fetched is real and the rest of the pipeline should have it. It
    # is the one event in this job that still costs records, so it is in the
    # summary line rather than only in the per-category print above it.
    short = [f"{s['name']} ({s['truncated']})" for s in status if s.get("truncated")]
    if short:
        summary += f"; short of the window: {', '.join(short)}"

    if not status:
        return summary, "sources.yaml produced no sources to fetch at all"
    if total == 0:
        return summary, (
            f"all {len(status)} sources returned zero items. This job cannot "
            "fetch nothing from everywhere on a working day, so the failure "
            "is in the network, the image or sources.yaml, and reporting a "
            "successful run of zero would hide it."
        )
    if arxiv and all(not s["entries"] for s in arxiv):
        return summary, (
            f"every one of the {len(arxiv)} arXiv categories returned zero "
            "entries. The firehose is what fills `papers`, and the blog "
            "feeds alone are not a corpus, so this is an arXiv API failure "
            "and not a quiet day."
        )
    return summary, None


def runtime_guard():
    """pipeline/runtime_sha.py, from the image or from a checkout.

    The two-path trick every job in this pipeline uses: the module is a sibling
    in a checkout and sits at /root inside the image, and deciding which from
    an environment variable goes stale the first time the image changes.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import runtime_sha as module

    return module


def upsert_papers(rows: list[dict]) -> int:
    import os

    import psycopg

    insert = """
        insert into papers (id, source, tier, title, authors, abstract, url, published_at)
        values (%(id)s, %(source)s, %(tier)s, %(title)s, %(authors)s, %(abstract)s, %(url)s, %(published_at)s)
    """
    inserted = 0
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # Say which deploy this is before anything else happens, the way
        # triage, interpret and weekly have since 2026-09-28. It cannot raise
        # and cannot abort this transaction; pipeline/runtime_sha.py says how.
        print(runtime_guard().record_runtime(conn, "ingest", __file__)[1])
        with conn.cursor() as cur:
            for r in rows:
                if r["tier"] == "b":
                    # curated pick: upgrade the tier even if the firehose saw it first
                    cur.execute(insert + "on conflict (id) do update set tier = 'b'", r)
                else:
                    cur.execute(insert + "on conflict (id) do nothing", r)
                    inserted += cur.rowcount
    return inserted


@app.function(
    schedule=modal.Cron("0 11 * * *"),  # daily 11:00 UTC = morning in New York
    secrets=[modal.Secret.from_name("neon")],
    timeout=900,
)
def ingest():
    cfg = load_sources()
    # Where the last run got to, read before anything is fetched. This is the
    # line that makes a missed day recoverable instead of lost.
    arxiv_rows, arxiv_status = fetch_arxiv(cfg, cursor=read_arxiv_cursor())
    feed_rows, feed_status = fetch_feeds(cfg)
    hf_rows = fetch_hf_daily(cfg)

    status = arxiv_status + feed_status + [
        {"name": "hf-daily", "kind": "json", "entries": len(hf_rows),
         "http": None}
    ]
    summary, refusal = judge_sources(status)
    print(summary)
    if refusal:
        raise NothingToIngest(
            f"{refusal}\n\n{summary}\n\n"
            "Run `python3 tools/feed_health.py` for the per-source verdicts. "
            "It needs no credentials, so it runs anywhere."
        )

    rows = arxiv_rows + feed_rows + hf_rows
    inserted = upsert_papers(rows)
    # Two numbers, because they fail differently. A zero `inserted` is a
    # normal day where every paper was already seen. A zero `fetched` is this
    # job not working, and it raised above before reaching here.
    print(f"fetched {len(rows)} items, inserted {inserted} new papers")
    return inserted


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=300,
)
def ingest_ids(ids: list[str], tier: str = "b"):
    """Backfill named papers. No schedule: this runs when a seat asks for it.

    Deliberately not wired into the daily job. The firehose's reach is a
    property of the window, and a list of ids is a judgment somebody made, so
    the two have different failure modes and mixing them would hide a missing
    backfill inside a normal day's count. `judge_sources` is not consulted here
    for the same reason: a by-id fetch that returns nothing is a wrong id rather
    than a dead source, and the missing ids are printed above.
    """
    rows, status = fetch_arxiv_ids(ids, tier=tier)
    if not rows:
        print(f"nothing to insert for {ids}")
        return 0
    inserted = upsert_papers(rows)
    print(f"fetched {len(rows)} of {status[0]['asked']} asked, "
          f"inserted {inserted} new papers")
    return inserted


@app.local_entrypoint()
def main(ids: str = ""):
    """`modal run pipeline/ingest.py` for the day's window.

    `--ids 2610.02858,2606.29537` for a backfill instead, which is the entry
    point the reading queue needs when a line names a paper the window cannot
    reach.
    """
    if ids:
        named = [i for i in (part.strip() for part in ids.split(",")) if i]
        print(f"inserted: {ingest_ids.remote(named)}")
        return
    print(f"inserted: {ingest.remote()}")
