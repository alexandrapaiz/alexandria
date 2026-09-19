#!/usr/bin/env python3
"""Check that every arXiv link in a digest issue points at the paper it names.

The 2026-09-19 accuracy audit (docs/evals/2026-09-19-digest-accuracy-audit.md)
found one issue link whose italicised title did not match the paper the URL
resolves to. A reader who clicks it lands somewhere else, and nothing in the
pipeline would ever have noticed. This is that missing check.

It only verifies the title-to-id binding, which is the part a machine can
settle on its own. Numbers inside a claim still need a human reading the
paper, and the audit report is the record of that reading.

    python3 tools/check_issue_citations.py site/content/issues/2026-W37.md

Exits non-zero if any cited id fails to resolve or names a different paper.
Needs network access to export.arxiv.org and nothing else.
"""

import difflib
import gzip
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
# below this ratio the cited title and the real title are different papers
MATCH_FLOOR = 0.75

# *Title* — [https://arxiv.org/abs/2609.11042](...) and the en-dash variant
CITATION = re.compile(r"\*([^*\n]+?)\*\s*[—–-]\s*\[?https?://arxiv\.org/abs/(\d{4}\.\d{4,5})")


def normalise(text: str) -> str:
    """Fold the typographic characters the digest writer emits into plain ascii."""
    for dash in "‐‑‒–—−":
        text = text.replace(dash, "-")
    return " ".join(text.lower().split())


def fetch(ids: list[str]) -> dict[str, str]:
    # the commas in id_list must stay literal; arxiv answers 406 to %2C
    query = f"id_list={','.join(ids)}&max_results={len(ids)}"
    request = urllib.request.Request(
        f"{ARXIV_API}?{query}", headers={
            "User-Agent": "alexandria-citation-check/1.0",
            # arxiv answers 406 to urllib's default Accept header
            "Accept": "application/atom+xml",
            # arxiv answers 406 to urllib's default Accept-Encoding of identity
            # once the id list grows past a couple of papers
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    feed = ET.fromstring(raw)
    titles = {}
    for entry in feed.findall("a:entry", ATOM):
        arxiv_id = entry.find("a:id", ATOM).text.rsplit("/", 1)[1].split("v")[0]
        titles[arxiv_id] = " ".join(entry.find("a:title", ATOM).text.split())
    return titles


def check(path: str) -> int:
    body = open(path, encoding="utf-8").read()
    cited = {}
    for title, arxiv_id in CITATION.findall(body):
        cited.setdefault(arxiv_id, title)
    if not cited:
        print(f"{path}: no arxiv citations found")
        return 0

    real = fetch(sorted(cited))
    failures = 0
    for arxiv_id, title in sorted(cited.items()):
        actual = real.get(arxiv_id)
        if actual is None:
            print(f"FAIL {arxiv_id}: does not resolve on arxiv (cited as {title!r})")
            failures += 1
            continue
        ratio = difflib.SequenceMatcher(None, normalise(title), normalise(actual)).ratio()
        if ratio < MATCH_FLOOR:
            print(f"FAIL {arxiv_id}: cited as {title!r}, arxiv says {actual!r}")
            failures += 1
        else:
            print(f"ok   {arxiv_id}: {actual}")

    print(f"\n{len(cited)} citations checked, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(check(sys.argv[1]))
