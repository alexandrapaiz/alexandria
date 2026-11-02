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

This is that step, once. It tries `arxiv.org/html/<id>` and then the ar5iv
mirror, cleans whichever answered to plain text with the same two regexes
`pipeline/distill.py` has always used, and falls back to the abstract from the
arXiv API only when no full-text route answers — which is the fallback distill
already makes, hoisted out of the pipeline so that the job and the seats read a
paper the same way. The `# source:` line in the output names the route the text
came from, because "no full text" used to mean "one url returned 404" and got
written down as a fact about arXiv. `pipeline/distill.py` imports
`fetch_paper` from this file, so there is one reader and not two: the same
fetch hands back the cleaned text a model reads and the raw markup a parser
reads, rather than two jobs asking arXiv for one page twice.

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
AR5IV_HTML = "https://ar5iv.labs.arxiv.org/html/{id}"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={id}"
ARXIV_ABS = "https://arxiv.org/abs/{id}"

# arXiv asks automated readers to identify themselves, and an unidentified
# urllib request is the one most likely to be refused.
USER_AGENT = "alexandria-read-paper/1.0 (https://github.com/alexandrapaiz/alexandria)"

DEFAULT_CACHE = os.environ.get("READ_PAPER_CACHE") or ".cache/papers"

# A cleaned body under 2,000 characters is a landing page rather than a paper.
# Both numbers come from distill's fetch_fulltext, where they have been in
# production since the full-text change.
#
# The byte floor is the weaker of the two and this comment used to overstate it:
# it said an arXiv stub page is "a few hundred bytes", and on 2026-11-02
# `arxiv.org/html/2609.07103` served a 7,882-byte page, well over the floor.
# It carried HTTP 404, so the status check is what rejected it, and its cleaned
# text was 602 characters, so the character floor would have caught it too. The
# byte floor catches neither. Keep it as the cheap first filter it is, and do
# not read a pass on it as evidence that a route served a paper.
MIN_HTML_BYTES = 5000
MIN_TEXT_CHARS = 2000

# Tried in order, first one that answers with a paper wins. arXiv's own HTML
# only exists for papers submitted in LaTeX from roughly 2024 on; ar5iv is the
# arXiv-run LaTeXML mirror that covers the rest, and it is second rather than
# first because arXiv's own rendering is the authoritative one when it exists.
# Both are LaTeXML output, so both carry the `ltx_role_affiliation` spans
# `pipeline/institutions.py` reads; see `fetch_html`.
HTML_ROUTES = (ARXIV_HTML, AR5IV_HTML)

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


def fetch_html_from(paper_id: str, *, timeout: float = 30) -> tuple[str, str] | None:
    """(raw markup, the url it came from) for one paper, or None.

    The markup rather than the text, because `clean_html` deletes the one
    thing the paper's header is worth reading for: the author affiliations
    live in `ltx_role_affiliation` spans and tag-stripping removes them.
    `pipeline/institutions.py` is the reader of this. Every route in
    `HTML_ROUTES` is LaTeXML output and keeps those spans, so which route
    answered costs that reader nothing.

    **Each route is tried in turn, and the url travels back with the body.**
    Until 2026-11-02 there was one route, `arxiv.org/html`, and a 404 on it
    was reported as "this paper has no full text". That is a claim about one
    url and it was written down as a claim about arXiv: `arxiv:2609.07103`
    returned 404 there while the ar5iv mirror served the whole paper, 78,293
    characters, all eight tables and two appendices the abstract does not
    mention, and a reading-queue line sat open on the wrong conclusion for
    thirty-three days
    (`INC-2026-11-02-a-paper-the-queue-called-unreadable-for-thirty-three-days-was-one-url-away`).
    The url comes back so that the `# source:` line names the route that
    actually answered; a header that names a route the body did not come from
    is how the first wrong claim got written.

    None covers all four of "no route has HTML for this id", "the id is not
    an arXiv id", "every fetch failed" and "this is not an arXiv paper",
    because every caller treats them the same way: there is no header to
    parse, so the field stays empty.
    """
    if paper_id.startswith("blog:"):
        return None  # blog posts: the feed summary already is the content
    try:
        arxiv_id = normalize_id(paper_id)
    except ValueError:
        return None
    for route in HTML_ROUTES:
        url = route.format(id=arxiv_id)
        try:
            status, body = _get(url, timeout)
        except Exception as exc:
            print(f"  html fetch failed for {paper_id} at {url}: {exc}", file=sys.stderr)
            continue
        if status == 200 and len(body) >= MIN_HTML_BYTES:
            return body, url
    return None


def fetch_html(paper_id: str, *, timeout: float = 30) -> str | None:
    """The markup alone, for callers that do not care which route served it."""
    got = fetch_html_from(paper_id, timeout=timeout)
    return got[0] if got else None


def fetch_paper(paper_id: str, *, max_chars: int | None = None,
                timeout: float = 30) -> dict | None:
    """One fetch of arXiv's HTML, both of the things a caller wants from it.

        {"text": <cleaned, cut to max_chars>, "html": <the raw markup>,
         "source": <the url that answered>}

    `text` is what a model reads and `html` is what a parser reads, and until
    2026-10-15 getting both meant fetching the page twice: distill pulled it,
    cleaned it, threw the markup away, and the institution backfill asked
    arXiv for the whole paper again to read a header distill had already held.
    On 2,223 pending papers that is 2,223 duplicate fetches of a volunteer
    service we are asked to be polite to.

    `text` is None when arXiv's page is a stub or cleans down to a landing
    page, which is the case `fetch_fulltext` has always reported as None.
    `html` is NOT None in that case, and the asymmetry is deliberate: a page
    too thin to read can still carry a parseable author block, so the caller
    can fill `institutions` for a paper it reads from the abstract. The whole
    return is None only when there is no page at all.
    """
    got = fetch_html_from(paper_id, timeout=timeout)
    if got is None:
        return None
    body, source = got
    try:
        text = clean_html(body)
    except Exception as exc:
        print(f"  cleaning failed for {paper_id}: {exc}", file=sys.stderr)
        text = ""
    if len(text) < MIN_TEXT_CHARS:
        return {"text": None, "html": body, "source": source}
    return {"text": text[:max_chars] if max_chars else text, "html": body,
            "source": source}


def fetch_fulltext(paper_id: str, *, max_chars: int | None = None,
                   timeout: float = 30) -> str | None:
    """arXiv's HTML rendering as plain text, or None so the caller falls back.

    The seats call this through this file's CLI with no cap at all. None means
    arXiv has no HTML for this paper, which for anything before roughly 2024
    is the common case and is not an error.

    `fetch_paper` is the same fetch keeping the markup as well, which is what
    `pipeline/distill.py` calls now. This stays because the CLI and the cache
    want the text alone and nothing else.
    """
    got = fetch_paper(paper_id, max_chars=max_chars, timeout=timeout)
    return got["text"] if got else None


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


def _render(arxiv_id: str, how: str, title: str, body: str, total: int | None = None,
            source: str | None = None) -> str:
    """The cache file, which is also what stdout gets: `#` header, then text.

    `total` is the length of the whole paper when `body` has been cut by
    `--max-chars`. The header always reports how much there is, and says
    separately how much is printed, because a reader that sees only the
    printed figure will believe a truncated paper is a short one.

    `source` is the url that actually answered, and it is passed rather than
    assumed because there is more than one full-text route now. Omitting it
    falls back to naming the first route, which is only right when that route
    is the one that answered.
    """
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if not source:
        source = (ARXIV_HTML if how == FULL_TEXT else ARXIV_ABS).format(id=arxiv_id)
    header = [
        f"# arxiv:{arxiv_id}",
        f"# title: {title or '(unknown)'}",
        f"# read: {how} ({total if total is not None else len(body):,} chars) {stamp}",
        f"# source: {source}",
    ]
    if total is not None and total > len(body):
        header.append(f"# printed: the first {len(body):,} chars (--max-chars)")
    return "\n".join(header) + "\n\n" + body + "\n"


def _parse_cached(text: str) -> tuple[str, str, str, str]:
    """(how, title, body, source) back out of a cache file written by `_render`.

    `source` comes back because a second `--no-cache`-less read reprints the
    header from the cache, and a reprint that renames the route is the same
    wrong claim as a first read that does.
    """
    head, _, body = text.partition("\n\n")
    how, title, source = FULL_TEXT, "", ""
    for line in head.splitlines():
        if line.startswith("# title: "):
            title = line.removeprefix("# title: ")
        elif line.startswith("# read: "):
            how = line.removeprefix("# read: ").split(" ", 1)[0]
        elif line.startswith("# source: "):
            source = line.removeprefix("# source: ").strip()
    return how, title, body.strip(), source


def read(raw_id: str, *, cache_dir: str | None = DEFAULT_CACHE, refresh: bool = False,
         timeout: float = 30) -> dict:
    """Read one paper. Returns {id, title, how, text, source, cached, path}.

    `how` is `full-text`, `abstract-only` or `unavailable`, and it is the field
    that matters: a caller that ignores it will report a paper as read on the
    strength of its abstract, which is the failure ADR-35 was written about.

    `source` is the url the text came from. It matters for the same reason:
    `abstract-only` is now a statement about every route in `HTML_ROUTES`
    rather than about one of them, and a run that records the outcome in
    `docs/research/reading-queue.md` should be able to name what was tried.
    """
    arxiv_id = normalize_id(raw_id)
    path = _cache_path(arxiv_id, cache_dir) if cache_dir else None

    if path and path.exists() and not refresh:
        how, title, body, source = _parse_cached(path.read_text())
        return {"id": f"arxiv:{arxiv_id}", "title": title, "how": how,
                "text": body, "source": source, "cached": True, "path": str(path)}

    got = fetch_paper(arxiv_id, timeout=timeout)
    body = got["text"] if got else None
    source = got["source"] if got else ""
    meta = fetch_metadata(arxiv_id, timeout=timeout)
    if body:
        how = FULL_TEXT
    elif meta:
        how, body = ABSTRACT_ONLY, meta["abstract"]
        source = ARXIV_ABS.format(id=arxiv_id)
    else:
        how, body, source = NOTHING, "", ""
    title = (meta or {}).get("title", "")

    wrote = bool(path) and how != NOTHING
    if wrote:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render(arxiv_id, how, title, body, source=source))
    # An unavailable paper is not cached and must not claim a path: the next
    # run should try again rather than inherit today's outage as a fact.
    return {"id": f"arxiv:{arxiv_id}", "title": title, "how": how, "text": body,
            "source": source, "cached": False, "path": str(path) if wrote else ""}


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
                          total=len(paper["text"]), source=paper["source"]))
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
