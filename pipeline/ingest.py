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
"""

import hashlib
import pathlib

import modal

ARXIV_MAX_PER_CAT = 100

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


def fetch_arxiv(cfg: dict) -> tuple[list[dict], list[dict]]:
    """The firehose, and one status row per category.

    The status rows are the point. A category that returns nothing used to
    be indistinguishable from a quiet day, and cs.SE and cs.CR were each
    added to sources.yaml to close a measured hole in the corpus, so a
    category going dark undoes that work in silence.
    """
    import feedparser

    rows = []
    status = []
    for entry in cfg["arxiv"]:
        cat, tier = entry["category"], entry["tier"]
        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending"
            f"&max_results={ARXIV_MAX_PER_CAT}"
        )
        feed = feedparser.parse(url)
        print(f"arxiv {cat}: {len(feed.entries)} entries "
              f"(http {getattr(feed, 'status', '?')})")
        status.append({"name": f"arxiv:{cat}", "kind": "arxiv",
                       "entries": len(feed.entries),
                       "http": getattr(feed, "status", None)})
        for e in feed.entries:
            arxiv_id = e.id.rsplit("/", 1)[-1]
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
    return rows, status


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
    arxiv_rows, arxiv_status = fetch_arxiv(cfg)
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


@app.local_entrypoint()
def main():
    print(f"inserted: {ingest.remote()}")
