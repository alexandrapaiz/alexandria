"""Fill site/emails/digest.html from a digest markdown body.

This is the frontend seat's verification harness for the 2026-09-19 email
template, and it doubles as the reference implementation of the slot
contract in site/emails/README.md. It uses the standard library only, so
the engineer can lift it into pipeline/weekly.py's Modal image as is.

    python3 docs/design/reviews/2026-09-19/render_sample.py

Writes the filled samples next to this file.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = ROOT / "site/emails/digest.html"

BULLET = re.compile(r"^(\s*)(?:[-*]\s+|(\d+)[.)]\s+)(.*)$")
BOLD_ONLY = re.compile(r"^\*\*(.+?)\*\*[.:]?$")
SOURCE = re.compile(
    r"^\*(?P<title>.+?)\*\s*[—–-]+\s*\[(?P<label>[^\]]+)\]\((?P<url>[^)]+)\)(?P<rest>.*)$"
)
EVIDENCE = re.compile(r"^Evidence:\s*(.+)$", re.I)
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


# ---------------- markdown -> slots ----------------

def normalise(text: str) -> str:
    """Fill-time typography, not editing.

    The writing model emits U+202F (narrow no-break space) inside names and
    before percent signs. Helvetica draws it so tight that "Claude Opus 5"
    reads as "ClaudeOpus5" in the mail client, verified at 3x on 2026-09-19.
    A normal space restores the word gap, and English takes no space before
    a percent sign at all.
    """
    for ch in ("\u202f", "\u2009", "\u200a"):
        text = text.replace(ch + "%", "%").replace(ch, "\u00a0")
    return text


def inline(text: str) -> str:
    """The inline subset an issue actually uses: links, bold, italic."""
    out = html.escape(normalise(text).strip())
    out = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" style="color:#0a0a0a; text-decoration:underline;">\1</a>',
        out,
    )
    out = re.sub(r"\*\*(.+?)\*\*", r'<span style="font-weight:600;">\1</span>', out)
    out = re.sub(r"(?<![\*\w])\*([^*]+?)\*(?!\*)", r"<em>\1</em>", out)
    return out


def plain(text: str) -> str:
    text = LINK.sub(r"\1", normalise(text))
    return re.sub(r"[*_`]", "", text).strip()


def host_path(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.strip()).rstrip("/")


def parse_item(lines: list[str], kind: str | None) -> dict:
    item: dict = {"kind": kind, "points": []}
    body: list[str] = []
    for n, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        m = BULLET.match(raw)
        if m and (n > 0 or raw.startswith((" ", "\t"))):
            item["points"].append({"marker": f"{m.group(2)}." if m.group(2) else "·",
                                   "text": inline(m.group(3))})
            continue
        src = SOURCE.match(line)
        if src:
            item["source"] = plain(src.group("title"))
            item["url"] = src.group("url")
            item["meta"] = host_path(src.group("url"))
            rest = re.sub(r"^\s*[—–-]+\s*", "", src.group("rest")).strip()
            if rest:
                body.append(rest)
            continue
        ev = EVIDENCE.match(line)
        if ev:
            item["evidence"] = plain(ev.group(1))
            continue
        if n == 0:
            title = BOLD_ONLY.match(line)
            if title:
                item["title"] = plain(title.group(1))
                continue
        body.append(line)
    if body:
        item["body"] = inline(" ".join(body))
    return item


def parse_section(body_lines: list[str]) -> list[dict]:
    items, current, kind = [], None, None
    for raw in body_lines:
        line = raw.strip()
        if not line:
            continue
        label = BOLD_ONLY.match(line)
        if label and not raw.startswith((" ", "\t")) and not BULLET.match(raw):
            if current:
                items.append(parse_item(current, kind))
                current = None
            kind = plain(label.group(1))
            continue
        top = BULLET.match(raw)
        if top and not raw.startswith((" ", "\t")):
            if current:
                items.append(parse_item(current, kind))
            current = [top.group(3)]
            continue
        if current is not None and raw.startswith((" ", "\t")):
            current.append(raw)
        else:
            if current:
                items.append(parse_item(current, kind))
                current = None
            items.append(parse_item([line], kind))
    if current:
        items.append(parse_item(current, kind))
    return [i for i in items if i.get("body") or i.get("title") or i.get("source")]


def parse_issue(md: str) -> dict:
    issue: dict = {"sections": [], "stats": None, "masthead": None}
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    issue["title"] = plain(lines[i][2:]) if i < len(lines) else ""
    i += 1
    opening: list[str] = []
    while i < len(lines) and not lines[i].startswith("## "):
        line = lines[i].strip()
        if line.startswith("---"):
            break
        if line:
            if re.fullmatch(r"\*[^*].*[^*]\*", line) and not opening:
                issue["masthead"] = plain(line)
            else:
                opening.append(line)
        i += 1
    issue["opening"] = "<br /><br />".join(inline(p) for p in opening)
    section, buf = None, []
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            if section:
                issue["sections"].append({"title": plain(section), "items": parse_section(buf)})
            section, buf = line[3:].strip(), []
        elif line.strip().startswith("---") and section:
            issue["sections"].append({"title": plain(section), "items": parse_section(buf)})
            section, buf = None, []
            tail = [l.strip() for l in lines[i + 1:] if l.strip()]
            issue["stats"] = plain(tail[0]) if tail else None
            break
        else:
            buf.append(line)
        i += 1
    if section:
        issue["sections"].append({"title": plain(section), "items": parse_section(buf)})
    return issue


# ---------------- slots -> html ----------------

def split_block(tpl: str, name: str) -> tuple[str, str, str]:
    begin, end = f"<!-- BEGIN:{name} -->", f"<!-- END:{name} -->"
    a, b = tpl.index(begin), tpl.index(end)
    return tpl[:a], tpl[a + len(begin):b], tpl[b + len(end):]


def fill(tpl: str, values: dict) -> str:
    for key, value in values.items():
        tpl = tpl.replace("{{%s}}" % key, value if value is not None else "")
    return tpl


def optional(tpl: str, name: str, values: dict | None) -> str:
    before, inner, after = split_block(tpl, name)
    return before + (fill(inner, values) if values else "") + after


def render(issue: dict, meta: dict) -> str:
    tpl = TEMPLATE.read_text()
    head, section_tpl, tail = split_block(tpl, "SECTION")
    sec_head, item_tpl, sec_tail = split_block(section_tpl, "ITEM")

    sections_html = []
    for section in issue["sections"]:
        items_html, last_kind = [], None
        for item in section["items"]:
            chunk = item_tpl
            show_kind = item.get("kind") and item["kind"] != last_kind
            last_kind = item.get("kind") or last_kind
            chunk = optional(chunk, "ITEM_KIND", {"item_kind": html.escape(item["kind"])} if show_kind else None)
            chunk = optional(chunk, "ITEM_TITLE", {"item_title": html.escape(item["title"])} if item.get("title") else None)
            chunk = optional(chunk, "ITEM_BODY", {"item_body": item["body"]} if item.get("body") else None)
            if item["points"]:
                before, points_tpl, after = split_block(chunk, "ITEM_POINTS")
                p_head, point_tpl, p_tail = split_block(points_tpl, "ITEM_POINT")
                rows = "".join(fill(point_tpl, {"point_marker": p["marker"], "point": p["text"]})
                               for p in item["points"])
                chunk = before + p_head + rows + p_tail + after
            else:
                chunk = optional(chunk, "ITEM_POINTS", None)
            chunk = optional(chunk, "ITEM_EVIDENCE",
                             {"item_evidence": html.escape(item["evidence"])} if item.get("evidence") else None)
            chunk = optional(chunk, "ITEM_SOURCE",
                             {"item_source": html.escape(item["source"]), "item_url": item["url"],
                              "item_meta": html.escape(item.get("meta", ""))} if item.get("source") else None)
            items_html.append(chunk)
        sections_html.append(fill(sec_head, {"section_title": html.escape(section["title"])})
                             + "".join(items_html) + sec_tail)

    doc = head + "".join(sections_html) + tail
    stats = re.sub(r"(\d) (?=[a-z])", "\\1\u00a0", issue["stats"]) if issue.get("stats") else None
    doc = optional(doc, "STATS", {"stats": html.escape(stats)} if stats else None)
    doc = optional(doc, "MASTHEAD", {"masthead": html.escape(issue["masthead"])} if issue.get("masthead") else None)
    return fill(doc, {
        "title": html.escape(issue["title"]),
        "opening": issue["opening"],
        "preheader": html.escape(meta["preheader"]),
        "edition": html.escape(meta["edition"]),
        "edition_short": html.escape(meta["edition_short"]),
        "close": html.escape(meta["close"]),
        "web_url": meta["web_url"],
        "archive_url": meta["archive_url"],
        "unsubscribe_url": meta["unsubscribe_url"],
        "recipient_email": html.escape(meta["recipient_email"]),
    })


CLOSE = "You read to decide. Your agents load to act."

if __name__ == "__main__":
    here = Path(__file__).parent
    weekly_md = (ROOT / "site/content/issues/2026-W37.md").read_text()
    daily_md = (here / "sample-daily.md").read_text()

    weekly = render(parse_issue(weekly_md), {
        "preheader": "Feedback-enriched environments and a dense verification reward, both with numbers.",
        "edition": "Weekly synthesis · September 14–20, 2026",
        "edition_short": "the weekly synthesis",
        "close": CLOSE,
        "web_url": "https://alexandr.ia/library/2026-W37",
        "archive_url": "https://alexandr.ia/library",
        "unsubscribe_url": "https://alexandr.ia/unsubscribe?t=SAMPLE",
        "recipient_email": "reader@example.com",
    })
    (here / "sample-weekly-2026-W37.html").write_text(weekly)

    daily = render(parse_issue(daily_md), {
        "preheader": "One dense reward beat a binary one by 28 percent relative, on the authors' own runs.",
        "edition": "Daily dispatch · September 19, 2026",
        "edition_short": "the daily dispatch",
        "close": CLOSE,
        "web_url": "https://alexandr.ia/library/2026-09-19",
        "archive_url": "https://alexandr.ia/library",
        "unsubscribe_url": "https://alexandr.ia/unsubscribe?t=SAMPLE",
        "recipient_email": "reader@example.com",
    })
    (here / "sample-daily-2026-09-19.html").write_text(daily)
    print("rendered weekly:", len(weekly), "bytes")
    print("rendered daily:", len(daily), "bytes")
    sys.exit(0)
