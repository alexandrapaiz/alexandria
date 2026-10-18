#!/usr/bin/env python3
"""Is every source in sources.yaml still answering?

`docs/agents/press-rehearsal.md` closes by naming the one gap its own
ladder does not cover, and it addresses this seat directly:

    `ingest` still has neither, and it does not need them in this form,
    because it calls no model. What it lacks is an availability check on
    its feeds, which is a different question with a different answer.

This is that check. The defect it exists to make noisy is in
`pipeline/ingest.py`'s `fetch_feeds`, and it is invisible by
construction. `feedparser.parse(url)` does not raise. A feed that 404s,
or moved, or returns an HTML error page, comes back as an object with an
empty `entries` list, the loop adds nothing, and the daily run prints
`fetched 4231 items, inserted 112 new papers` because the arXiv firehose
dominates the count either way. So a source can go dark and keep
reporting success for as long as nobody reads one line of a log.

That is not hypothetical arithmetic. `sources.yaml` carries its own
evidence that the org has been answering this question by hand, one
source at a time, in comments: "verified 2026-09-07", "Verified 200 with
20 items and per-item summaries on 2026-09-23". Every one of those is a
measurement that was true once and has never been taken again.

Three verdicts are failures and the rest are not, which is the whole
judgement in this file.

`empty`, `http-<code>` and `unreachable` are failures. The source is not
delivering anything to ingest, and ingest cannot tell.

`stale` is a failure only past `DEAD_DAYS`. A lab blog that posts twice a
year is not broken, so a threshold tight enough to catch a quiet month
would cry wolf on half of tier c. A source with nothing in a year is
abandoned, and the softer `WARN_DAYS` tier is reported with its measured
age so the org can tighten the number against data rather than taste.

`malformed` is a warning, not a failure, and this is the one place where
being right matters more than being strict. `feedparser` is lenient and
`xml.etree` is not, so a feed this file cannot parse as XML may still be
ingesting perfectly. When the strict parse fails, the item count falls
back to counting `<item` and `<entry` openings in the body, and the
verdict says which method produced the number.

Two things stop this from crying wolf, and they are different on purpose.

`expect: archive` on a `sources.yaml` entry is a permanent editorial
statement that a source has stopped publishing and is kept for what it
already holds. `gh-autogen` is the live example and the file already said
so in a comment: active development moved to the AG2 fork, which is a
separate entry. An archived source may be silent forever and still must
answer, so `empty`, `http-<code>` and `unreachable` fail on it exactly as
they do on anything else. Only its age is forgiven.

`KNOWN_DEAD` below is the opposite kind of thing: a dated list of real
defects nobody has ruled on yet. Retiring a source is an editorial call
and ADR-7 gives diffs to `sources.yaml` the shape of a proposal, so a
seat that measures a dead feed records it rather than deleting it. The
set may shrink and may not grow, which is the idiom
`tests/test_ci_coverage.py` already uses for the same reason: a gate that
is permanently red is a gate nobody reads
(`INC-2026-09-30-the-guard-went-red-and-nobody-read-it`), and a gate with
no pin at all is one a seat switches off.

No credentials, no database, no GitHub API. Every source here is public
HTTP, which is what makes this runnable on any runner, in CI, and
locally, unlike the three gates in the ladder above it.

    python3 tools/feed_health.py                  # the census, and the gate
    python3 tools/feed_health.py --report-only    # print the same thing, exit 0
    python3 tools/feed_health.py --json
    python3 tools/feed_health.py --offline        # read sources.yaml, fetch nothing
    python3 tools/feed_health.py --only hn-frontpage,gh-vllm
    python3 tools/feed_health.py --census docs/evals/2026-10-16-feed-health.json

Why it does not use pyyaml. `requirements-dev.txt` has no pyyaml and
`tools/ci_coverage.py` already decided that a guard is a poor reason to
add a dependency. Every list entry in `sources.yaml` is a single-line
flow mapping, so `read_sources` reads exactly those two shapes and
raises on any line in a known block that it cannot parse. A reader that
skipped a line it did not understand would commit this file's own
subject matter, so it refuses instead.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.yaml"

# A source with nothing new in four months is worth a line in the report.
WARN_DAYS = 120
# A source with nothing new in a year is abandoned, and that is a failure.
DEAD_DAYS = 365

TIMEOUT = 20.0
FEED_WORKERS = 8
# arXiv asks callers to go easy on the API, and eight categories serially is
# eight requests. The firehose is the corpus, so correctness beats speed here.
ARXIV_DELAY = 3.0

ARXIV_MAX_PER_CAT = 100  # the same number pipeline/ingest.py queries with

FAILING = {"empty", "unreachable", "dead-stale"}

# Sources measured as delivering nothing on 2026-10-16, the day this file was
# written, and not yet ruled on. Each line is a real defect. The gate does not
# fail on them, the report prints them in their own section, and
# `tests/test_feed_health.py` asserts every name here is still a real source.
#
# This set may shrink and may not grow. Retiring a source is the owner's call
# under ADR-7, so a seat that finds a dead feed adds a line here and a ledger
# entry, and the seat that gets the ruling deletes the line.
KNOWN_DEAD = {
    "qwen": (
        "200 with 44 items and nothing in 389 days. Qwen publishes "
        "constantly, so this is a moved feed rather than a quiet lab. Four "
        "candidate replacements were probed on 2026-10-16 and none answered: "
        "qwen.ai/blog/rss.xml and qwen.ai/rss.xml return 200 with no items, "
        "and both qwenlm.github.io/feed.xml and /index.xml 404. Needs a "
        "human to find the current URL. Tier c, so this is a frontier lab's "
        "own channel and the most costly of these five to lose."
    ),
    "stanford-sail": (
        "200 with 15 items, newest 1595 days old. The SAIL blog stopped "
        "publishing. ai.stanford.edu/blog/index.xml 404s. Retire."
    ),
    "mit-csail": (
        "200 with 9 items, newest 2664 days old, which is 2019. "
        "www.csail.mit.edu/news/rss.xml 404s. mit-news-ai covers MIT and is "
        "live at 0.8 days. Retire."
    ),
    "langchain-blog": (
        "200 with zero items, on both /rss/ and /rss. The `langchain` entry "
        "at www.langchain.com/blog/rss.xml is the same publisher and is live "
        "with 100 items at 0.1 days, so this is a duplicate of a feed that "
        "moved. Retire."
    ),
    # owasp-genai was here and is not dead. Removed 2026-10-17 by the run
    # that re-measured it: 200 with 10 items, newest 8.6 days old, through
    # the transport `pipeline/ingest.py` uses. The 403 that put it on this
    # list was this file's httpx client being refused, which is what
    # `confirm_with_production_transport` now rules out before a verdict.
}

ENTRY_OPEN = re.compile(rb"<(?:item|entry)[\s>]", re.IGNORECASE)


# ------------------------------------------------------------- sources.yaml

ENTRY_LINE = re.compile(r"^\s*-\s*\{(?P<body>.*)\}\s*(?:#.*)?$")
KEY_VALUE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*)$")
BLOCK_LINE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<inline>.*?)\s*(?:#.*)?$")


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _flow_mapping(body: str, where: str) -> dict:
    """Parse `name: x, url: "y", tier: d` and refuse anything else.

    Splitting on commas is safe for this file and would not be in general.
    A URL holding a comma would break it, so the parse is checked rather
    than trusted: every piece must be `key: value` and nothing may be
    dropped.
    """
    out = {}
    for piece in body.split(","):
        if not piece.strip():
            raise ValueError(f"{where}: empty field in {body!r}")
        match = KEY_VALUE.match(piece.strip())
        if not match:
            raise ValueError(
                f"{where}: cannot read {piece.strip()!r} as `key: value`. "
                "sources.yaml changed shape and this reader refuses to skip "
                "a line it does not understand, because a silently dropped "
                "source is the defect tools/feed_health.py exists to catch."
            )
        out[match.group("key")] = _unquote(match.group("value"))
    return out


def read_sources(path: Path | str = SOURCES) -> dict:
    """The three top-level blocks of sources.yaml, with no yaml parser.

    Returns `{"arxiv": [...], "feeds": [...], "hf_daily_papers": {...}}`.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    out: dict = {"arxiv": [], "feeds": [], "hf_daily_papers": {}}
    block: str | None = None

    for number, raw in enumerate(text.splitlines(), start=1):
        where = f"{path.name}:{number}"
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line[0].isspace():
            match = BLOCK_LINE.match(line)
            if not match:
                raise ValueError(f"{where}: unreadable top-level line {line!r}")
            block = match.group("key")
            if block not in out:
                raise ValueError(
                    f"{where}: sources.yaml grew a top-level block "
                    f"{block!r} that this reader does not know. Teach it the "
                    "new block or this census silently stops covering it."
                )
            continue

        if block in ("arxiv", "feeds"):
            match = ENTRY_LINE.match(line)
            if not match:
                raise ValueError(
                    f"{where}: expected a single-line flow mapping under "
                    f"{block!r} and got {line.strip()!r}"
                )
            out[block].append(_flow_mapping(match.group("body"), where))
        elif block == "hf_daily_papers":
            match = KEY_VALUE.match(line.strip())
            if not match:
                raise ValueError(f"{where}: unreadable mapping line {line!r}")
            out[block][match.group("key")] = _unquote(match.group("value"))

    return out


def sources_to_check(cfg: dict) -> list[dict]:
    """One flat list of everything ingest fetches, in ingest's own order."""
    checks = []
    for entry in cfg["arxiv"]:
        cat = entry["category"]
        checks.append(
            {
                "name": f"arxiv:{cat}",
                "kind": "arxiv",
                "tier": entry.get("tier"),
                "url": (
                    "https://export.arxiv.org/api/query"
                    f"?search_query=cat:{cat}&sortBy=submittedDate"
                    f"&sortOrder=descending&max_results={ARXIV_MAX_PER_CAT}"
                ),
            }
        )
    hf = cfg.get("hf_daily_papers") or {}
    if hf.get("url"):
        checks.append(
            {"name": "hf-daily", "kind": "json", "tier": hf.get("tier"),
             "url": hf["url"]}
        )
    for feed in cfg["feeds"]:
        checks.append(
            {"name": feed["name"], "kind": "feed", "tier": feed.get("tier"),
             "url": feed["url"], "expect": feed.get("expect")}
        )
    return checks


# ------------------------------------------------------------------ parsing

def newest_date(body: bytes) -> str | None:
    """The newest item date in a feed, as ISO, or None when it says none.

    Both wire formats, because this corpus reads both: RFC 822 `pubDate`
    in RSS and ISO 8601 `updated` or `published` in Atom.
    """
    from email.utils import parsedate_to_datetime

    best: datetime | None = None
    text = body.decode("utf-8", errors="replace")

    for tag in ("pubDate", "updated", "published"):
        for raw in re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", text,
                              re.IGNORECASE | re.DOTALL):
            value = raw.strip()
            if not value:
                continue
            parsed = None
            try:
                parsed = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                try:
                    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    parsed = None
            if parsed is None:
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            if best is None or parsed > best:
                best = parsed

    return best.isoformat() if best else None


def count_items(body: bytes) -> tuple[int, str]:
    """How many items a feed carries, and which method produced the number.

    Strict first. `xml.etree` rejects feeds that `feedparser` accepts, so a
    strict failure is not evidence that ingest gets nothing, and the crude
    count is what keeps this file from reporting a working feed as dead.
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return len(ENTRY_OPEN.findall(body)), "counted"

    items = [
        element
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1].lower() in ("item", "entry")
    ]
    return len(items), "parsed"


def classify(items: int, method: str, newest: str | None,
             now: datetime | None = None,
             expect: str | None = None) -> tuple[str, float | None]:
    """The verdict and the age in days, from a fetch that reached the host.

    `expect="archive"` forgives age and nothing else. A source kept for
    what it already holds still has to answer, so an archived feed that
    404s or empties out is as broken as any other.
    """
    now = now or datetime.now(timezone.utc)
    age = None
    if newest:
        try:
            when = datetime.fromisoformat(newest)
        except ValueError:
            when = None
        if when is not None:
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            age = round((now - when).total_seconds() / 86400, 1)

    if items == 0:
        return "empty", age
    if expect == "archive":
        return "archive", age
    if age is not None and age >= DEAD_DAYS:
        return "dead-stale", age
    if age is not None and age >= WARN_DAYS:
        return "stale", age
    if method == "counted":
        return "malformed", age
    return "ok", age


# ------------------------------------------------------------------ fetching

def confirm_with_production_transport(url: str) -> tuple[bytes | None, str]:
    """Fetch the way `pipeline/ingest.py` does, and say what happened.

    Returns (body, detail). `body` is None when this transport failed too,
    and then `detail` says how, so a recorded failure carries both answers
    rather than one.

    `feedparser.parse(url)` is what ingest calls and `feedparser` fetches
    with `urllib.request`, so this uses `urllib.request` directly: it needs
    the raw bytes for `count_items` and `newest_date`, and going through
    feedparser would hand back a parsed struct instead. The transport is the
    same one, which is the only part that matters here.
    """
    import urllib.error
    import urllib.request

    request = urllib.request.Request(
        url, headers={"User-Agent": "alexandria-feed-health/1.0 (+docs/agents/press-rehearsal.md)"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return None, f"HTTP {response.status} to urllib as well"
            return response.read(), "200 to urllib"
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code} to urllib as well"
    except Exception as exc:  # noqa: BLE001 - one verdict for any transport failure
        return None, f"{type(exc).__name__} to urllib as well: {exc}"


def check_one(source: dict, client) -> dict:
    """Fetch one source and judge it. Never raises, so one dead host cannot
    end the census before it reaches the rest."""
    result = {
        "name": source["name"],
        "kind": source["kind"],
        "tier": source.get("tier"),
        "url": source["url"],
        "status": None,
        "items": 0,
        "method": None,
        "newest": None,
        "age_days": None,
        "verdict": None,
        "detail": "",
    }
    result["transport"] = "httpx"
    body = None
    try:
        response = client.get(source["url"], timeout=TIMEOUT,
                              follow_redirects=True)
    except Exception as exc:  # noqa: BLE001 - any transport failure is one verdict
        result["status"] = None
        failure = f"{type(exc).__name__}: {exc}"
    else:
        result["status"] = response.status_code
        if response.status_code == 200:
            body = response.content
            failure = None
        else:
            failure = f"HTTP {response.status_code}"

    if body is None:
        # Confirm with the transport production uses before calling a source
        # dead. INC-2026-09-20's own ruling is "before changing a request to
        # fix an error, run the unchanged request again", and this adds the
        # half that entry could not have known: the request has to be the
        # one `pipeline/ingest.py` makes. It calls `feedparser.parse(url)`,
        # which fetches with `urllib.request`, and this file fetches with
        # `httpx`. On 2026-10-17 `genai.owasp.org/feed/` answered 403 to
        # httpx under five different user agents and 200 with ten items,
        # newest 8.6 days old, to urllib. So the verdict was about the client
        # rather than about the feed, and it had already reached `sources.yaml`
        # as `MEASURED DEAD` and the ledger as a retirement proposal.
        confirmed, detail = confirm_with_production_transport(source["url"])
        if confirmed is not None:
            body = confirmed
            result["status"] = 200
            result["transport"] = "urllib"
            result["detail"] = (
                f"{failure} to httpx, 200 to urllib, which is how "
                f"pipeline/ingest.py fetches. Judged on the urllib answer."
            )
        else:
            result["verdict"] = (
                "unreachable" if result["status"] is None
                else f"http-{result['status']}"
            )
            result["detail"] = f"{failure}; and {detail}"
            return result

    if source["kind"] == "json":
        try:
            payload = json.loads(body)
        except Exception as exc:  # noqa: BLE001
            result["verdict"] = "empty"
            result["detail"] = f"200 but not JSON: {type(exc).__name__}: {exc}"
            return result
        result["items"] = len(payload) if isinstance(payload, list) else 0
        result["method"] = "parsed"
        result["verdict"] = "ok" if result["items"] else "empty"
        if not result["items"]:
            result["detail"] = "200 with an empty JSON payload"
        return result

    items, method = count_items(body)
    newest = newest_date(body)
    verdict, age = classify(items, method, newest,
                            expect=source.get("expect"))
    result.update(items=items, method=method, newest=newest, age_days=age,
                  verdict=verdict)
    note = ""
    if verdict == "empty":
        note = "200 with no items, which ingest reads as nothing"
    elif verdict == "malformed":
        note = "strict XML parse failed, items counted crudely"
    elif verdict in ("stale", "dead-stale"):
        note = f"newest item is {age} days old"
    elif verdict == "archive":
        note = f"archived on purpose, newest item {age} days old"
    if note:
        # The transport note, when there is one, is kept rather than replaced.
        # It is the reason the verdict is trustworthy at all.
        result["detail"] = f"{result['detail']}. {note}" if result["detail"] else note
    return result


def census(cfg: dict, only: list[str] | None = None) -> list[dict]:
    """Check every source. arXiv serially and politely, the rest in parallel."""
    import time

    import httpx

    checks = sources_to_check(cfg)
    if only:
        wanted = set(only)
        checks = [c for c in checks if c["name"] in wanted]

    headers = {"User-Agent": "alexandria-feed-health/1.0 (+docs/agents/press-rehearsal.md)"}
    results: list[dict] = []
    with httpx.Client(headers=headers) as client:
        arxiv = [c for c in checks if c["kind"] == "arxiv"]
        rest = [c for c in checks if c["kind"] != "arxiv"]

        for index, source in enumerate(arxiv):
            if index:
                time.sleep(ARXIV_DELAY)
            results.append(check_one(source, client))

        if rest:
            with ThreadPoolExecutor(max_workers=FEED_WORKERS) as pool:
                results.extend(pool.map(lambda s: check_one(s, client), rest))

    order = {c["name"]: n for n, c in enumerate(checks)}
    results.sort(key=lambda r: order.get(r["name"], 0))
    return results


def is_broken(result: dict) -> bool:
    """Does this verdict mean the source delivers nothing to ingest?"""
    verdict = str(result["verdict"])
    return verdict in FAILING or verdict.startswith("http-")


def failures(results: list[dict]) -> list[dict]:
    """The broken sources nobody has ruled on yet, which is what gates.

    `KNOWN_DEAD` is subtracted here and nowhere else, so a pinned source is
    still measured, still printed, and still carries its verdict in the JSON
    census. The pin changes the exit code and not the finding.
    """
    return [r for r in results if is_broken(r) and r["name"] not in KNOWN_DEAD]


def pinned_failures(results: list[dict]) -> list[dict]:
    """Broken and already written down. Reported, never gating."""
    return [r for r in results if is_broken(r) and r["name"] in KNOWN_DEAD]


# ------------------------------------------------------------------- report

def render(results: list[dict]) -> str:
    lines = []
    width = max((len(r["name"]) for r in results), default=4)
    for r in results:
        age = "" if r["age_days"] is None else f"  newest {r['age_days']}d ago"
        detail = f"  {r['detail']}" if r["detail"] else ""
        lines.append(
            f"  {r['verdict']:<10} {r['name']:<{width}} "
            f"{r['items']:>4} items{age}{detail}"
        )

    bad = failures(results)
    pinned = pinned_failures(results)
    warn = [r for r in results if r["verdict"] in ("stale", "malformed")]
    lines.append("")
    lines.append(
        f"{len(results) - len(bad) - len(pinned)} of {len(results)} sources "
        f"are delivering; {len(bad)} are not and are unrecorded; "
        f"{len(pinned)} are not and are pinned; {len(warn)} carry a warning"
    )
    if pinned:
        lines.append("")
        lines.append(
            "Known dead, pinned in tools/feed_health.py, waiting on a ruling:"
        )
        for r in pinned:
            lines.append(f"  {r['name']}: {r['verdict']}")
            lines.append(f"      {KNOWN_DEAD[r['name']]}")
    if bad:
        lines.append("")
        lines.append("Delivering nothing, so ingest gets nothing from them:")
        for r in bad:
            lines.append(f"  {r['name']}: {r['verdict']}  {r['url']}")
        lines.append("")
        lines.append(
            "Each line above is a source pipeline/ingest.py fetches every day "
            "and reports success on. Fix the URL in sources.yaml, or delete "
            "the entry, or say in the file why it stays."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report-only", action="store_true",
                        help="print the census and exit 0 even on failures")
    parser.add_argument("--offline", action="store_true",
                        help="read sources.yaml and fetch nothing")
    parser.add_argument("--only", default="",
                        help="comma-separated source names")
    parser.add_argument("--census", default="",
                        help="also write the full result to this JSON file")
    parser.add_argument("--sources", default=str(SOURCES))
    args = parser.parse_args(argv)

    cfg = read_sources(args.sources)

    if args.offline:
        checks = sources_to_check(cfg)
        if args.json:
            print(json.dumps(checks, indent=2))
        else:
            print(f"{len(checks)} sources in {Path(args.sources).name}: "
                  f"{len(cfg['arxiv'])} arXiv categories, "
                  f"{len(cfg['feeds'])} feeds, "
                  f"{1 if cfg.get('hf_daily_papers', {}).get('url') else 0} JSON")
        return 0

    only = [name for name in args.only.split(",") if name.strip()]
    results = census(cfg, only=only or None)

    if args.census:
        Path(args.census).write_text(
            json.dumps(
                {
                    "measured_at": datetime.now(timezone.utc).isoformat(),
                    "warn_days": WARN_DAYS,
                    "dead_days": DEAD_DAYS,
                    "results": results,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(render(results))

    if args.report_only:
        return 0
    return 1 if failures(results) else 0


if __name__ == "__main__":
    sys.exit(main())
