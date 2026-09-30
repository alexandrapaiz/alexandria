#!/usr/bin/env python3
"""read_paper.py — read one arXiv paper as plain text, in one command.

    python3 tools/read_paper.py 2602.12670
    python3 tools/read_paper.py arxiv:2602.12670 arxiv:2603.22455
    python3 tools/read_paper.py 2602.12670 --max-chars 40000 --bare

ADR-35 says skill creation requires reading, and the skill seat's reading step
was a paragraph of instructions rather than a command: fetch the arXiv HTML,
strip the tags, notice when there is no HTML version, fall back to the
abstract, and remember which of the two you got. Every seat that did it wrote
its own version, and a seat that gets an abstract back and forgets to say so
reports a paper as read when it read 200 words of it.

This is that step, once. It fetches `arxiv.org/html/<id>`, cleans it to plain
text with the same two regexes `pipeline/distill.py` has always used, and falls
back to the abstract from the arXiv API when arXiv serves no HTML — which is
the fallback distill already makes, hoisted out of the pipeline so that the job
and the seats read a paper the same way. `pipeline/distill.py` imports
`fetch_fulltext` from this file, so there is one reader and not two.

**Exit code is the answer to "did you actually read it".** 0 means full text, 3
means the abstract only, 4 means neither. A run that gets 3 has found exactly
the thing docs/research/reading-queue.md exists to record, and can say so
without having to parse this output:

    python3 tools/read_paper.py 2602.12670 > paper.txt || echo "queue it"

Results are cached under `.cache/papers/` in the workspace (gitignored), so
asking twice in one run costs one fetch. `--refresh` re-fetches, `--cache-dir`
moves it, and `READ_PAPER_CACHE` sets it for a whole session.

The pending reading queue, one id per line, is `python3 pipeline/reading_queue.py`.

Standard library only, on purpose: the seats run on `ubuntu-latest` with no
`pip install` step, so a reader with a dependency is a reader nobody runs. It
uses `httpx` when it is importable, because the Modal images have it pinned.
"""

from __future__ import annotations

import argparse
import html as htmllib
import os
import pathlib
import re
import sys
import time
import xml.etree.ElementTree as ET

ARXIV_HTML = "https://arxiv.org/html/{id}"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={id}"
ARXIV_ABS = "https://arxiv.org/abs/{id}"

# arXiv asks automated readers to identify themselves, and an unidentified
# urllib request is the one most likely to be refused.
USER_AGENT = "alexandria-read-paper/1.0 (https://github.com/alexandrapaiz/alexandria)"

DEFAULT_CACHE = os.environ.get("READ_PAPER_CACHE") or ".cache/papers"

# An arXiv "HTML" page that is really a stub ("no HTML for this paper") is a
# few hundred bytes, and a cleaned body under 2,000 characters is a landing
# page rather than a paper. Both numbers come from distill's fetch_fulltext,
# where they have been in production since the full-text change.
MIN_HTML_BYTES = 5000
MIN_TEXT_CHARS = 2000

FULL_TEXT, ABSTRACT_ONLY, NOTHING = "full-text", "abstract-only", "unavailable"
EXIT = {FULL_TEXT: 0, ABSTRACT_ONLY: 3, NOTHING: 4}


def normalize_id(raw: str) -> str:
    """`arxiv:2602.12670v2`, an abs/pdf URL, or a bare id, all to `2602.12670`.

    The version suffix goes because arXiv's HTML lives at the unversioned path,
    and because the reading queue and `papers.id` both key on the bare id.
    """
    text = raw.strip()
    text = re.sub(r"^arxiv:", "", text, flags=re.I)
    match = re.search(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})", text)
    if not match:
        raise ValueError(f"not an arXiv id: {raw!r}")
    return re.sub(r"v\d+$", "", match.group(1))


def _get(url: str, timeout: float) -> tuple[int, str]:
    """One GET, redirects followed, as text. httpx when present, urllib when not."""
    try:
        import httpx

        resp = httpx.get(url, follow_redirects=True, timeout=timeout,
                         headers={"User-Agent": USER_AGENT})
        return resp.status_code, resp.text
    except ImportError:
        pass
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.status, resp.read().decode(charset, "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""


def clean_html(raw_html: str) -> str:
    """Tags out, entities in, whitespace collapsed. distill's two regexes."""
    text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", raw_html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = htmllib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_fulltext(paper_id: str, *, max_chars: int | None = None,
                   timeout: float = 30) -> str | None:
    """arXiv's HTML rendering as plain text, or None so the caller falls back.

    `pipeline/distill.py` calls this with its own `FULLTEXT_CHARS`; the seats
    call it through this file's CLI with no cap at all. None means arXiv has no
    HTML for this paper, which for anything before roughly 2024 is the common
    case and is not an error.
    """
    if paper_id.startswith("blog:"):
        return None  # blog posts: the feed summary already is the content
    try:
        arxiv_id = normalize_id(paper_id)
    except ValueError:
        return None
    try:
        status, body = _get(ARXIV_HTML.format(id=arxiv_id), timeout)
        if status != 200 or len(body) < MIN_HTML_BYTES:
            return None
        text = clean_html(body)
        if len(text) < MIN_TEXT_CHARS:
            return None
        return text[:max_chars] if max_chars else text
    except Exception as exc:
        print(f"  fulltext fetch failed for {paper_id}: {exc}", file=sys.stderr)
        return None


def _meta_from_atom(body: str, arxiv_id: str) -> dict | None:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = ET.fromstring(body).find("a:entry", ns)
    if entry is None:
        return None
    title = (entry.findtext("a:title", "", ns) or "").strip()
    summary = (entry.findtext("a:summary", "", ns) or "").strip()
    # The API answers a withdrawn or unknown id with a placeholder entry whose
    # title is "Error" and which carries no summary at all.
    if not title or title.lower() == "error" or not summary:
        return None
    return {
        "title": " ".join(title.split()),
        "abstract": " ".join(summary.split()),
        "authors": [" ".join((n.text or "").split())
                    for n in entry.findall("a:author/a:name", ns)
                    if (n.text or "").strip()],
        "published_at": (entry.findtext("a:published", "", ns) or "")[:10] or None,
    }


def _meta_from_abs(body: str) -> dict | None:
    """The same four fields off the `abs` page's `citation_*` meta tags.

    The second path exists because the first one is not reachable from
    everywhere. On 2026-09-27 every form of `export.arxiv.org/api/query`
    answered HTTP 406 from the GitHub Actions runner this repository's seats
    run on, with and without headers, over http and https, while
    `arxiv.org/abs/<id>` answered 200 from the same process a second later. A
    fallback whose only failure mode is different from the primary's is worth
    forty lines.
    """
    def meta(attr: str, name: str) -> list[str]:
        return [htmllib.unescape(m) for m in re.findall(
            rf'<meta[^>]+{attr}="{name}"[^>]+content="([^"]*)"', body)]

    titles = meta("name", "citation_title")
    abstracts = meta("name", "citation_abstract") or meta("property", "og:description")
    if not titles or not abstracts:
        return None
    dates = meta("name", "citation_date")
    return {
        "title": " ".join(titles[0].split()),
        "abstract": " ".join(abstracts[0].split()),
        "authors": [" ".join(a.split()) for a in meta("name", "citation_author")],
        "published_at": dates[0].replace("/", "-") if dates else None,
    }


def fetch_metadata(paper_id: str, *, timeout: float = 30) -> dict | None:
    """Title, authors, abstract, date and url for one arXiv id, or None.

    This is the abstract half of the fallback, and it is also how a paper the
    corpus has never seen gets a row in `papers` when the reading queue asks
    for it (`pipeline/reading_queue.py`). Atom XML from the API first, parsed
    with the standard library rather than feedparser, because adding a
    dependency to the distill image to read one entry is a dependency per
    queue line. The `abs` page is the second try; see `_meta_from_abs`.
    """
    try:
        arxiv_id = normalize_id(paper_id)
    except ValueError:
        return None
    fields = None
    for url, parse in ((ARXIV_API.format(id=arxiv_id), lambda b: _meta_from_atom(b, arxiv_id)),
                       (ARXIV_ABS.format(id=arxiv_id), _meta_from_abs)):
        try:
            status, body = _get(url, timeout)
            if status != 200 or not body.strip():
                continue
            fields = parse(body)
            if fields:
                break
        except Exception as exc:
            print(f"  metadata fetch failed for {paper_id} at {url}: {exc}", file=sys.stderr)
    if not fields:
        return None
    return {"id": f"arxiv:{arxiv_id}", "arxiv_id": arxiv_id,
            "url": ARXIV_ABS.format(id=arxiv_id), **fields}


def _cache_path(arxiv_id: str, cache_dir: str) -> pathlib.Path:
    return pathlib.Path(cache_dir) / f"arxiv-{arxiv_id.replace('/', '-')}.txt"


def _render(arxiv_id: str, how: str, title: str, body: str, total: int | None = None) -> str:
    """The cache file, which is also what stdout gets: `#` header, then text.

    `total` is the length of the whole paper when `body` has been cut by
    `--max-chars`. The header always reports how much there is, and says
    separately how much is printed, because a reader that sees only the
    printed figure will believe a truncated paper is a short one.
    """
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    header = [
        f"# arxiv:{arxiv_id}",
        f"# title: {title or '(unknown)'}",
        f"# read: {how} ({total if total is not None else len(body):,} chars) {stamp}",
        f"# source: {ARXIV_HTML.format(id=arxiv_id) if how == FULL_TEXT else ARXIV_ABS.format(id=arxiv_id)}",
    ]
    if total is not None and total > len(body):
        header.append(f"# printed: the first {len(body):,} chars (--max-chars)")
    return "\n".join(header) + "\n\n" + body + "\n"


def _parse_cached(text: str) -> tuple[str, str, str]:
    """(how, title, body) back out of a cache file written by `_render`."""
    head, _, body = text.partition("\n\n")
    how, title = FULL_TEXT, ""
    for line in head.splitlines():
        if line.startswith("# title: "):
            title = line.removeprefix("# title: ")
        elif line.startswith("# read: "):
            how = line.removeprefix("# read: ").split(" ", 1)[0]
    return how, title, body.strip()


def read(raw_id: str, *, cache_dir: str | None = DEFAULT_CACHE, refresh: bool = False,
         timeout: float = 30) -> dict:
    """Read one paper. Returns {id, title, how, text, cached, path}.

    `how` is `full-text`, `abstract-only` or `unavailable`, and it is the field
    that matters: a caller that ignores it will report a paper as read on the
    strength of its abstract, which is the failure ADR-35 was written about.
    """
    arxiv_id = normalize_id(raw_id)
    path = _cache_path(arxiv_id, cache_dir) if cache_dir else None

    if path and path.exists() and not refresh:
        how, title, body = _parse_cached(path.read_text())
        return {"id": f"arxiv:{arxiv_id}", "title": title, "how": how,
                "text": body, "cached": True, "path": str(path)}

    body = fetch_fulltext(arxiv_id, timeout=timeout)
    meta = None
    if body:
        how = FULL_TEXT
        meta = fetch_metadata(arxiv_id, timeout=timeout)
    else:
        meta = fetch_metadata(arxiv_id, timeout=timeout)
        if meta:
            how, body = ABSTRACT_ONLY, meta["abstract"]
        else:
            how, body = NOTHING, ""
    title = (meta or {}).get("title", "")

    wrote = bool(path) and how != NOTHING
    if wrote:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render(arxiv_id, how, title, body))
    # An unavailable paper is not cached and must not claim a path: the next
    # run should try again rather than inherit today's outage as a fact.
    return {"id": f"arxiv:{arxiv_id}", "title": title, "how": how, "text": body,
            "cached": False, "path": str(path) if wrote else ""}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Read an arXiv paper as plain text. Exit 0 full text, "
                    "3 abstract only, 4 nothing.")
    ap.add_argument("ids", nargs="+", help="arXiv ids, with or without the arxiv: prefix")
    ap.add_argument("--max-chars", type=int, default=0,
                    help="truncate the printed text (the cache keeps it whole)")
    ap.add_argument("--bare", action="store_true", help="body only, no # header")
    ap.add_argument("--refresh", action="store_true", help="re-fetch even if cached")
    ap.add_argument("--no-cache", action="store_true", help="do not read or write the cache")
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE, help=f"default {DEFAULT_CACHE}")
    ap.add_argument("--quiet", action="store_true", help="no status line on stderr")
    args = ap.parse_args(argv)

    worst = 0
    for raw in args.ids:
        started = time.monotonic()
        try:
            paper = read(raw, cache_dir=None if args.no_cache else args.cache_dir,
                         refresh=args.refresh)
        except ValueError as exc:
            print(f"{exc}", file=sys.stderr)
            worst = max(worst, 1)
            continue
        text = paper["text"][:args.max_chars] if args.max_chars else paper["text"]
        if paper["how"] == NOTHING:
            print(f"# arxiv:{normalize_id(raw)}\n# read: {NOTHING}\n")
        elif args.bare:
            print(text)
        else:
            print(_render(normalize_id(raw), paper["how"], paper["title"], text,
                          total=len(paper["text"])))
        if not args.quiet:
            where = "cached" if paper["cached"] else f"fetched in {time.monotonic() - started:.1f}s"
            note = "" if paper["how"] == NOTHING else f", {len(paper['text']):,} chars"
            print(f"{paper['id']}: {paper['how']}{note} ({where})"
                  + (f" -> {paper['path']}" if paper["path"] and not args.no_cache else ""),
                  file=sys.stderr)
        worst = max(worst, EXIT[paper["how"]])
    return worst


if __name__ == "__main__":
    sys.exit(main())
