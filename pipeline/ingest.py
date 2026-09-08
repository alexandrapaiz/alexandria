"""Ingest: pull new papers from the sources in sources.yaml into the bronze layer.

Runs daily on Modal. Requires the `neon` secret (DATABASE_URL).

    modal run pipeline/ingest.py        # one-off manual run
    modal deploy pipeline/ingest.py     # install the daily schedule
"""

import hashlib

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


def fetch_arxiv(cfg: dict) -> list[dict]:
    import feedparser

    rows = []
    for entry in cfg["arxiv"]:
        cat, tier = entry["category"], entry["tier"]
        url = (
            "http://export.arxiv.org/api/query"
            f"?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending"
            f"&max_results={ARXIV_MAX_PER_CAT}"
        )
        feed = feedparser.parse(url)
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
    return rows


def fetch_feeds(cfg: dict) -> list[dict]:
    import feedparser

    rows = []
    for f in cfg["feeds"]:
        feed = feedparser.parse(f["url"])
        print(f"feed {f['name']}: {len(feed.entries)} entries")
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
    return rows


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


def upsert_papers(rows: list[dict]) -> int:
    import os

    import psycopg

    insert = """
        insert into papers (id, source, tier, title, authors, abstract, url, published_at)
        values (%(id)s, %(source)s, %(tier)s, %(title)s, %(authors)s, %(abstract)s, %(url)s, %(published_at)s)
    """
    inserted = 0
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
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
    rows = fetch_arxiv(cfg) + fetch_feeds(cfg) + fetch_hf_daily(cfg)
    inserted = upsert_papers(rows)
    print(f"fetched {len(rows)} items, inserted {inserted} new papers")
    return inserted


@app.local_entrypoint()
def main():
    print(f"inserted: {ingest.remote()}")
