"""Fill the designed digest template (site/emails/digest.html) for the press.

The owner's ruling of 2026-09-24: "no ui applied to the emails... only the
html. i want the emails to have ui." The template had existed since
2026-09-19 and the press had never used it, so every issue that went out
was markdown wrapped in an inline Georgia div while the designed email sat
in the repo.

This module is the reference renderer from
docs/design/reviews/2026-09-19/render_sample.py, lifted into the pipeline
with the press-facing half added: the meta block that turns an issue key
and a subscriber row into the slots the template needs. The parsing and
filling code below is deliberately the same code the frontend seat
verified at 3x on 2026-09-19, not a reimplementation of it. The slot
contract it honours is site/emails/README.md.

Standard library only, on purpose. The template is bundled into the Modal
image as a data file, so the press gains no dependency for the UI.
"""

import html
import os
import re
from datetime import date
from pathlib import Path

# The template ships two ways: bundled at /root/emails/digest.html inside the
# Modal image, and in the working tree when a rehearsal or a test runs it
# locally. Resolved per call rather than at import, so a test can monkeypatch
# neither path and still get a legible error instead of an import failure.
BUNDLED = Path("/root/emails/digest.html")
IN_REPO = Path(__file__).resolve().parents[1] / "site" / "emails" / "digest.html"

# The closing line, from the 2026-09-19 design review. It is the one piece of
# reader-facing copy this module owns, so it is a constant a writer can find.
CLOSE = "You read to decide. Your agents load to act."

BULLET = re.compile(r"^(\s*)(?:[-*]\s+|(\d+)[.)]\s+)(.*)$")
BOLD_ONLY = re.compile(r"^\*\*(.+?)\*\*[.:]?$")
SOURCE = re.compile(
    r"^\*(?P<title>.+?)\*\s*[—–-]+\s*\[(?P<label>[^\]]+)\]\((?P<url>[^)]+)\)(?P<rest>.*)$"
)
EVIDENCE = re.compile(r"^Evidence:\s*(.+)$", re.I)
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

WEEK_KEY = re.compile(r"^(\d{4})-W(\d{2})$")
DAY_KEY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def template_text() -> str:
    for path in (BUNDLED, IN_REPO):
        try:
            return path.read_text()
        except OSError:
            # Missing is the ordinary case for whichever path is not this
            # environment's. PermissionError is the interesting one: outside
            # Modal the process is not root, and probing /root raises rather
            # than answering False, which is why this asks forgiveness rather
            # than permission.
            continue
    raise FileNotFoundError(
        f"digest template not found at {BUNDLED} or {IN_REPO}. Inside Modal "
        "this means the image is missing its add_local_file for "
        "site/emails/digest.html."
    )


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
    # kept alongside the HTML because the preheader is drawn from the opening
    # and an inbox preview cannot contain markup
    issue["opening_plain"] = " ".join(plain(p) for p in opening)
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
    tpl = template_text()
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


# ---------------- the press's half: an issue key becomes an edition ----------

def site_base() -> str:
    """Where an issue lives on the web. Overridable so a rehearsal can point
    at a preview deploy without editing code."""
    return os.environ.get("SITE_URL", "https://alexandr.ia").rstrip("/")


def week_dates(year: int, week: int) -> str:
    """'September 21–27, 2026' for an ISO week, spelled the way weekly() does.

    Same arithmetic as the `dates` line the generator prompt already receives,
    kept here so the email can label an edition without the caller passing it.
    """
    monday = date.fromisocalendar(year, week, 1)
    sunday = date.fromisocalendar(year, week, 7)
    if monday.month == sunday.month:
        return f"{monday.strftime('%B')} {monday.day}–{sunday.day}, {sunday.year}"
    return (f"{monday.strftime('%B')} {monday.day} – "
            f"{sunday.strftime('%B')} {sunday.day}, {sunday.year}")


def edition_for(key: str) -> tuple[str, str]:
    """(edition, edition_short) from the issue key, and nothing else needed.

    The key is what the press already has in hand: '2026-W39' for the weekly
    synthesis, and '2026-09-19' for a daily dispatch once the daily cadence
    lands (PR #35/#60 rename `week` to `key` for exactly this reason). Reading
    the cadence off the key is what makes the daily path free: it renders
    correctly the day that branch merges, with no second call site to update.

    `edition_short` completes the footer sentence "You are receiving ___ of
    alexandria at you@example.com", so it is a kind of issue and never a date.
    """
    m = WEEK_KEY.match(key)
    if m:
        return (f"Weekly synthesis · {week_dates(int(m.group(1)), int(m.group(2)))}",
                "the weekly issue")
    m = DAY_KEY.match(key)
    if m:
        day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return (f"Daily dispatch · {day.strftime('%B')} {day.day}, {day.year}",
                "the daily issue")
    # An unrecognised key still sends. A label we cannot compute is a cosmetic
    # loss; refusing to render the issue over it would not be.
    return ("From the library", "this issue")


def subject_for(body: str) -> str:
    """The issue's own H1. The W code is an internal id and never reader-facing."""
    if body.startswith("# "):
        title = body.split("\n", 1)[0][2:].strip()
        if title:
            return plain(title)
    return "This week's issue from the library"


def preheader_for(issue: dict) -> str:
    """One plain sentence for the inbox preview, and never the title again.

    Drawn from the issue's own opening, because the opening is already the
    sentence the writer chose to lead with. Trimmed to one sentence so the
    preview does not run past what a mail client shows.
    """
    opening = (issue.get("opening_plain") or "").strip()
    if not opening:
        return ""
    first = re.split(r"(?<=[.!?])\s+", opening)[0].strip()
    if len(first) > 160:
        first = first[:157].rstrip(" ,;:") + "..."
    return first


def build_meta(key: str, issue: dict, recipient_email: str,
               unsubscribe_url: str) -> dict:
    edition, edition_short = edition_for(key)
    base = site_base()
    return {
        "preheader": preheader_for(issue),
        "edition": edition,
        "edition_short": edition_short,
        "close": CLOSE,
        "web_url": f"{base}/library/{key}",
        "archive_url": f"{base}/library",
        "unsubscribe_url": unsubscribe_url,
        "recipient_email": recipient_email,
    }


def render_issue(body: str, key: str, recipient_email: str,
                 unsubscribe_url: str) -> str:
    """The one call the press makes: issue markdown in, designed email out."""
    issue = parse_issue(body)
    return render(issue, build_meta(key, issue, recipient_email, unsubscribe_url))
