"""Ingest: pull new papers from arXiv + lab blogs into the bronze layer.

Runs daily on Modal. Requires the `neon` secret (DATABASE_URL).

    modal run pipeline/ingest.py        # one-off manual run
    modal deploy pipeline/ingest.py     # install the daily schedule
"""

import hashlib

import modal

ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]
ARXIV_MAX_PER_CAT = 100

BLOG_FEEDS = [
    ("anthropic", "https://www.anthropic.com/rss.xml"),
    ("deepmind", "https://deepmind.google/blog/rss.xml"),
    ("openai", "https://openai.com/news/rss.xml"),
]

image = modal.Image.debian_slim().pip_install("feedparser==6.0.11", "psycopg[binary]==3.2.4")

app = modal.App("alexandria-ingest", image=image)


def upsert_papers(rows: list[dict]) -> int:
    import os

    import psycopg

    inserted = 0
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            for r in rows:
                cur.execute(
                    """
                    insert into papers (id, source, title, authors, abstract, url, published_at)
                    values (%(id)s, %(source)s, %(title)s, %(authors)s, %(abstract)s, %(url)s, %(published_at)s)
                    on conflict (id) do nothing
                    """,
                    r,
                )
                inserted += cur.rowcount
    return inserted


def pub_date(entry) -> str | None:
    """Feeds disagree on date formats (arXiv: ISO 8601, blogs: RFC 822);
    feedparser's parsed struct_time normalizes both."""
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if t is None:
        return None
    return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"


def fetch_arxiv() -> list[dict]:
    import feedparser

    rows = []
    for cat in ARXIV_CATEGORIES:
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
                    "title": " ".join(e.title.split()),
                    "authors": [a.name for a in getattr(e, "authors", [])],
                    "abstract": " ".join(getattr(e, "summary", "").split()),
                    "url": e.link,
                    "published_at": pub_date(e),
                }
            )
    return rows


def fetch_blogs() -> list[dict]:
    import feedparser

    rows = []
    for name, feed_url in BLOG_FEEDS:
        feed = feedparser.parse(feed_url)
        for e in feed.entries:
            link = getattr(e, "link", None)
            if not link:
                continue
            digest = hashlib.sha256(link.encode()).hexdigest()[:16]
            rows.append(
                {
                    "id": f"blog:{name}:{digest}",
                    "source": "blog",
                    "title": " ".join(getattr(e, "title", "untitled").split()),
                    "authors": [name],
                    "abstract": " ".join(getattr(e, "summary", "").split())[:4000],
                    "url": link,
                    "published_at": pub_date(e),
                }
            )
    return rows


@app.function(
    schedule=modal.Cron("0 11 * * *"),  # daily 11:00 UTC = morning in New York
    secrets=[modal.Secret.from_name("neon")],
    timeout=600,
)
def ingest():
    rows = fetch_arxiv() + fetch_blogs()
    inserted = upsert_papers(rows)
    print(f"fetched {len(rows)} items, inserted {inserted} new papers")
    return inserted


@app.local_entrypoint()
def main():
    print(f"inserted: {ingest.remote()}")
