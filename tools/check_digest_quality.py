#!/usr/bin/env python3
"""The pre-send quality gate: read an issue the way the owner will.

Sprint 2026-09-21 item 4 asked for a quality tier for digest content and for
Monday's issue to be held to it before it sends. This file is the half of that
checklist a machine can settle. The other half, the judgment half, is
docs/standards/digest-quality.md, which names a reader for every line this
script cannot decide.

The reason it is code and not a paragraph is incident 20 and the register map
(docs/agents/registers.md): a rule written down but never opened at the point
of production is documentation, and documentation does not stop anything. The
ban list was already perfect on paper while the one issue that shipped broke
eleven of its entries. So every rule below cites the ban-list entry it
enforces, and the pipeline runs this before the email goes out.

Two levels, and the difference matters:

  block  the send stops. Reserved for defects that are unambiguous from the
         text alone, that the owner has already had to report, or that make
         the issue wrong rather than weak.
  warn   printed, counted, never fatal. Either the rule needs judgment the
         regex does not have, or the pipeline cannot yet satisfy it (the
         per-item citation links are waiting on a gather() change), and a gate
         that blocks on something the generator cannot fix would simply stop
         the newsletter.

    python3 tools/check_digest_quality.py site/content/issues/2026-W37.md
    python3 tools/check_digest_quality.py --kind daily issue.md
    cat issue.md | python3 tools/check_digest_quality.py -

Exit codes: 0 clean or warnings only, 1 at least one blocking finding, 2 the
file could not be read. --strict makes warnings fatal too, which is what a
human review should use once the citation work lands.

Standard library only, no network. tools/check_issue_citations.py is the
companion that does need the network: it settles whether a cited title is the
paper the link resolves to, which is the accuracy line of the same checklist.
"""

import argparse
import re
import sys
from dataclasses import dataclass

BLOCK = "block"
WARN = "warn"


@dataclass(frozen=True)
class Finding:
    level: str
    rule: str
    line: int          # 1-indexed, 0 when the finding is about the whole issue
    detail: str
    ban_list: str      # the docs/voice/ban-list.md entry this enforces

    def __str__(self) -> str:
        where = f"line {self.line}" if self.line else "issue"
        return f"  [{self.level}] {self.rule} ({where}, ban list {self.ban_list}): {self.detail}"


# ---------------- the rules ----------------

# Ban list 20. The generator's internal slot labels, printed as headings. This
# is the one tell the owner has flagged twice, the second time in capitals, and
# the writer seat pre-registered exactly this check in docs/ideas.md on
# 2026-09-19: if the prompt fails again, the fix belongs in code.
SKELETON_HEADINGS = (
    "gaining traction", "trailblazing", "left behind", "read these yourself",
    "key takeaways", "what this means", "new and unproven", "compounding",
)

# Ban list 13. Typesetter punctuation. The reader's search box does not match
# it and neither does an agent loading the issue. 2026-W37 carried 87
# non-breaking hyphens and 19 narrow spaces.
TYPESETTER = {
    "‑": "non-breaking hyphen (use an ordinary hyphen)",
    " ": "narrow no-break space (use an ordinary space)",
    " ": "thin space (use an ordinary space)",
    "×": "multiplication sign (write 3x, not 3×)",
}

# Ban list 1. Split by how much context the word needs. The left column is
# never right in an issue about research. The right column is usually slop but
# is occasionally the paper's own word, so it warns rather than blocks.
SLOP_ALWAYS = (
    "delve", "tapestry", "realm", "supercharge", "game-changer", "game changer",
    "revolutionize", "revolutionise", "ever-evolving", "paradigm shift",
)
SLOP_USUALLY = (
    "seamless", "robust", "crucial", "pivotal", "unlock", "empower",
    "leverage", "cutting-edge", "landscape",
)

# Ban list 4 and 5.
HEDGES = ("could potentially", "may possibly", "it's important to note",
          "it is important to note", "it should be noted")
INTENSIFIERS = ("very ", "truly ", "incredibly ", "remarkably ", "extremely ")

# Ban list 14. Counts of edges in alexandria's claim graph, printed at a reader
# who has no way to decode them, plus the ISO week code and the triage scores.
INTERNAL_VOCAB = (
    (re.compile(r"\b(?:\d+|two|three|four|five|six|seven|eight|nine|ten)\s+"
                r"(?:independent\s+)?(?:supports|supporting edges)\b", re.I),
     "a raw supports count"),
    (re.compile(r"\bsupported\s+(?:twice|by\s+(?:\d+|two|three|four|five)\s+citations|"
                r"(?:\d+|three|four|five)\s+times)\b", re.I), "a raw supports count"),
    (re.compile(r"\bclaim[ _-]?(?:id\s*)?\d{2,}\b", re.I), "a claim id"),
    (re.compile(r"\b\d{4}-W\d{2}\b"), "the ISO week code"),
    (re.compile(r"\btriage score\b|\bdeep[_ -]read flag\b", re.I), "a triage internal"),
    (re.compile(r"\btier\s*[123]\b", re.I), "a source tier"),
)

# Ban list 24. A figure with nothing to place it against. The sentence passes
# if a second number or an explicit comparison sits beside it.
COMPARISON = re.compile(
    r"\b(?:versus|vs\.?|compared|comparison|baseline|up from|down from|against|"
    r"from\s+[\d.]+|than|prior|previous|before)\b", re.I)

URL_LINE = re.compile(r"^\s*(?:[-*]\s*)?\*?[^*]*\*?\s*[—–-]?\s*\[?https?://\S+", re.I)
HAS_URL = re.compile(r"https?://\S+")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# `%\b` would require a word character after the sign, which never happens in
# "64 % of tasks", so the boundary goes on the word form only
NUMBER = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|\bpercent\b)", re.I)


def _lines(body: str) -> list[str]:
    return body.replace("\r\n", "\n").split("\n")


@dataclass
class Item:
    """One thing the issue is telling the reader about, with its line span."""
    start: int         # 1-indexed line of the item's first line
    lines: list[str]
    section: str


def parse_items(body: str) -> list[Item]:
    """Top-level bullets, each running until the next bullet or heading.

    Indented bullets are part of the item above them, which is how the issue
    writes its method steps, so only column-zero markers start a new item.
    """
    items: list[Item] = []
    section = ""
    current: Item | None = None
    for number, line in enumerate(_lines(body), start=1):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            current = None
            continue
        if re.match(r"^[-*]\s+\S", line):
            current = Item(start=number, lines=[line], section=section)
            items.append(current)
        elif current is not None:
            if line.strip() == "" and current.lines and current.lines[-1].strip() == "":
                current = None   # a blank line pair ends the item
            else:
                current.lines.append(line)
    for item in items:
        while item.lines and item.lines[-1].strip() == "":
            item.lines.pop()
    return items


def check(body: str, kind: str = "weekly") -> list[Finding]:
    """Every machine-decidable line of docs/standards/digest-quality.md."""
    findings: list[Finding] = []
    lines = _lines(body)
    lowered = body.lower()
    items = parse_items(body)

    def add(level, rule, line, detail, entry):
        findings.append(Finding(level, rule, line, detail, entry))

    # --- accuracy and structure ---
    for number, line in enumerate(lines, start=1):
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().strip("*_").lower()
        for banned in SKELETON_HEADINGS:
            if heading == banned or heading.startswith(banned + " ") or heading.endswith(" " + banned):
                add(BLOCK, "skeleton-heading", number,
                    f"{line.strip()!r} prints the generator's own slot label", "19, 20")

    title = next((line for line in lines if line.startswith("# ")), "")
    if title:
        number = lines.index(title) + 1
        if re.search(r"\[[^\]]*\d{4}[^\]]*\]", title):
            add(BLOCK, "date-in-title", number,
                "the headline spends the subject line on a date the email header already carries",
                "22")
        if ":" in title.split("—")[0] and not title.strip().endswith(":"):
            add(WARN, "colon-title", number,
                "a title whose second half explains the first; one finding, one line", "11")
    else:
        add(BLOCK, "no-title", 0, "the issue has no H1, so the email has no subject", "n/a")

    # --- voice: the tells that are decidable from the text alone ---
    for number, line in enumerate(lines, start=1):
        for character, why in TYPESETTER.items():
            if character in line:
                add(BLOCK, "typesetter-punctuation", number, why, "13")
                break
        for pattern, why in INTERNAL_VOCAB:
            found = pattern.search(line)
            if found:
                add(BLOCK, "internal-vocabulary", number,
                    f"{found.group(0)!r} is {why}, which no subscriber can decode", "14")
        low = line.lower()
        for word in SLOP_ALWAYS:
            if word in low:
                add(BLOCK, "slop-lexicon", number, f"{word!r}", "1")
        for word in SLOP_USUALLY:
            if re.search(rf"\b{re.escape(word)}\b", low):
                add(WARN, "slop-lexicon", number, f"{word!r} (the paper's own word, or ours?)", "1")
        for phrase in HEDGES:
            if phrase in low:
                add(WARN, "hedge-stack", number, f"{phrase!r}; state it or grade it", "4")
        for word in INTENSIFIERS:
            if word in low:
                add(WARN, "empty-intensifier", number, f"{word.strip()!r}", "5")

    # --- the consequence line: what the item leaves the reader holding ---
    for item in items:
        last = item.lines[-1] if item.lines else ""
        if URL_LINE.match(last) or last.rstrip().endswith(")"):
            if HAS_URL.search(last):
                add(BLOCK, "ends-on-citation", item.start + len(item.lines) - 1,
                    "the item ends on its source, so the reader works out the consequence alone",
                    "25")

    # --- evidence density: every item names where it came from ---
    for item in items:
        if not HAS_URL.search("\n".join(item.lines)):
            add(WARN, "citation-per-item", item.start,
                "no link in this item; the reader cannot reach the paper", "n/a (O1 KR3)")

    # --- padding and rhythm ---
    by_section: dict[str, list[Item]] = {}
    for item in items:
        by_section.setdefault(item.section, []).append(item)
    for section, group in by_section.items():
        if len(group) < 5:
            continue
        endings = [(item.lines[-1].lower().rstrip(". ").split() or [""])[-1] for item in group]
        for ending in set(endings):
            if ending and endings.count(ending) >= max(3, len(group) * 0.6):
                add(WARN, "uniform-rhythm", group[0].start,
                    f"{endings.count(ending)} of {len(group)} items in {section!r} end on the "
                    f"word {ending!r}", "21, 3")
                break
        lengths = [len("\n".join(item.lines)) for item in group]
        if min(lengths) and max(lengths) / min(lengths) < 1.6:
            add(WARN, "uniform-length", group[0].start,
                f"all {len(group)} items in {section!r} are within a whisker of one length "
                f"({min(lengths)} to {max(lengths)} characters); length is a claim about how "
                "much happened, so a thin week cut to a fat shape lies", "21, 3")

    # --- the first screen ---
    preamble, seen_title = [], False
    for line in lines:
        if line.startswith("# "):
            seen_title = True
            continue
        if line.startswith("## "):
            break
        if seen_title:
            preamble.append(line)
    words = len(body.split())
    if words > 250 and not any(re.match(r"^\s*[-*\d]", line) for line in preamble):
        add(WARN, "no-contents", 0,
            "nothing in the first screen names what is in this issue; the reader scrolls to find out",
            "23")

    # --- numbers the reader cannot place ---
    for number, line in enumerate(lines, start=1):
        for sentence in SENTENCE_SPLIT.split(line):
            figures = NUMBER.findall(sentence)
            if figures and not COMPARISON.search(sentence) and len(NUMBER.findall(sentence)) < 2:
                add(WARN, "bare-number", number,
                    f"{figures[0]!r} with nothing beside it to place it against", "24")
                break

    # --- the daily has its own floor ---
    if kind == "daily" and "nothing worth your time" not in lowered:
        if words > 500:
            add(WARN, "daily-too-long", 0,
                f"{words} words; the daily is dispatch at 150 to 400", "21")
        if words < 40:
            add(BLOCK, "daily-too-short", 0,
                f"{words} words is not an issue and is not the honest empty line either", "n/a")

    return findings


# ---------------- reporting ----------------

EXAMPLES_PER_RULE = 3


def report(findings: list[Finding], name: str) -> str:
    """Grouped by rule, because this is read in a Modal log at 15:00 UTC.

    An issue with 40 non-breaking hyphens has one defect, not 40, and a
    report that prints all 40 buries the other three defects under them.
    """
    blocks = [f for f in findings if f.level == BLOCK]
    warns = [f for f in findings if f.level == WARN]
    if not findings:
        return f"{name}: clean. Every machine-checkable line of the quality tier passes."
    lines = [f"{name}: {len(blocks)} blocking, {len(warns)} warnings."]
    for level, group in ((BLOCK, blocks), (WARN, warns)):
        by_rule: dict[str, list[Finding]] = {}
        for finding in group:
            by_rule.setdefault(finding.rule, []).append(finding)
        for rule, hits in by_rule.items():
            head = f"  [{level}] {rule} ({len(hits)}x, ban list {hits[0].ban_list})"
            lines.append(head)
            for finding in hits[:EXAMPLES_PER_RULE]:
                where = f"line {finding.line}" if finding.line else "issue"
                lines.append(f"      {where}: {finding.detail}")
            if len(hits) > EXAMPLES_PER_RULE:
                lines.append(f"      and {len(hits) - EXAMPLES_PER_RULE} more")
    if blocks:
        lines.append("The send stops here. The issue is still written to the digests table, "
                     "so nothing is lost; fix the prompt or the payload and run again.")
    return "\n".join(lines)


def corrections(findings: list[Finding]) -> str:
    """What to tell the generator when it gets one more try.

    Only blocking findings, deduplicated by rule, phrased as instructions
    rather than as a log, because the model is being asked to rewrite and not
    to read a report.
    """
    seen, instructions = set(), []
    for finding in findings:
        if finding.level != BLOCK or finding.rule in seen:
            continue
        seen.add(finding.rule)
        instructions.append(f"- {finding.rule}: {finding.detail}")
    if not instructions:
        return ""
    return ("Your previous draft was rejected by the pre-send quality gate. Rewrite the "
            "whole issue, keeping every fact, and fix these:\n" + "\n".join(instructions))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="issue files, or - for stdin")
    parser.add_argument("--kind", default="weekly", choices=("weekly", "daily"))
    parser.add_argument("--strict", action="store_true", help="warnings are fatal too")
    args = parser.parse_args(argv)

    worst = 0
    for path in args.paths:
        try:
            body = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        except OSError as exc:
            print(f"cannot read {path}: {exc}")
            worst = max(worst, 2)
            continue
        findings = check(body, args.kind)
        print(report(findings, path))
        if any(f.level == BLOCK for f in findings) or (args.strict and findings):
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
