#!/usr/bin/env python3
"""The pre-send quality gate: read an issue the way the owner will.

Sprint 2026-09-21 item 4 asked for a quality tier for digest content and for
Monday's issue to be held to it before it sends. This file is the half of that
checklist a machine can settle. The other half, the judgment half, is
docs/product/digest-quality.md, which names a reader for every line this
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
import pathlib
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

# Ban list 19, 20, the derived half, and the reason it is derived.
#
# `SKELETON_HEADINGS` above is a hand list and every entry in it is one of the
# generator's INTERNAL slot names or a near-synonym. What the press actually
# prints is the reader-facing paraphrase, and law 12's own text says the
# paraphrase is the violation: "A paraphrase of a banned heading is the banned
# heading." So the floor holds the one shape the generator is least likely to
# emit and none of the shapes it does.
#
# The writer seat measured that on 2026-11-01 and routed the repair here,
# because `tools/` is pipeline code and that charter may not write it
# (docs/ideas.md, "The pre-send heading ban and the voice canon's heading ban
# share no phrase"). The intersection of the floor and the canon's list was
# empty. Not small. Empty. Four headings the owner has ruled on twice, the
# second time in capitals, were serving while this gate read them clean.
#
# The repair is not a ninth hand entry. It is to read the phrasings out of the
# ban itself, which is the paragraph of `prompts/digest.md` that
# `docs/voice/check_voice.py slotwords` already reads, so the two gates cannot
# hold two vocabularies for one rule. A derived list does not drift.
# `tests/test_digest_quality.py` pins this pass to the canon's own asserted
# cases, so widening the ban there fails here until both agree.
# The short edition's standing line, as `pipeline/weekly.py` writes it into
# the body. The degraded edition declares itself in band, and it does so
# because the press attaches this line rather than asking the generator for it:
# "a label the model can forget is a label that goes missing on the week it
# matters". That makes it the one tell this gate can trust about which edition
# it is reading, and `tests/test_digest_quality.py` pins the literal against
# the press's own copy of it.
SHORT_EDITION_NOTE = "*A short edition. This week's issue is the week in brief.*"

# A Markdown list item's opening row. Canon law 14's first device.
BULLET = re.compile(r"^([-*+]|\d+\.)\s")

SLOT_BAN_OPEN = "The ban is on the slot's IDEA and not on four strings"
SLOT_BAN_CLOSE = "first job is to say which section the reader is in"

# The phrasings, read out of the ban's own span. Found by its sentences rather
# than by a line number, because a line number in a gate is a gate that lies
# after the next edit.
SLOT_DRESS = re.compile(r'"(what [a-z ]+)"')

# Remainders that add nothing a reader could date. A banned phrasing followed
# only by these is the banned phrasing wearing a suffix, which is how 2026-W44
# served the reading slot's own internal name past an equality test. Kept small
# on purpose: the moment a word here could carry the day's material, this
# reading starts firing on the headings law 12 asks for.
SLOT_INVARIANT = frozenset((
    "yourself", "yourselves", "myself", "ourselves",
    "this", "week", "today", "now", "again", "so", "far",
    "month", "year", "issue", "edition",
))

# Where the generator is, in both places this file runs. A checkout has it
# beside `tools/`; the Modal image drops it at `/root/prompts/digest.md`
# (`pipeline/weekly.py`'s image list), and this file at `/root/`. Neither path
# is a guess: both are declared in that image.
GENERATOR_PATHS = (
    pathlib.Path(__file__).resolve().parent.parent / "prompts" / "digest.md",
    pathlib.Path("/root/prompts/digest.md"),
)


def slot_dress() -> tuple[tuple[str, ...], str]:
    """The banned phrasings, and why the list is empty when it is.

    Returns `(phrasings, complaint)`. A non-empty complaint is a finding in its
    own right rather than a silent pass: a gate that reports zero defects
    because it could not read its own rule is the confident zero this
    repository keeps filing, so the caller warns and the floor still applies.
    """
    for path in GENERATOR_PATHS:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        start, end = text.find(SLOT_BAN_OPEN), text.find(SLOT_BAN_CLOSE)
        if start < 0 or end < 0:
            return (), (f"{path.name}'s slot-ban paragraph is not where its own "
                        "sentences say it is, so the derived phrasings were not read")
        found = tuple(sorted(set(SLOT_DRESS.findall(text[start:end]))))
        if not found:
            return (), (f"{path.name}'s slot-ban paragraph quotes no phrasing, "
                        "so the derived half of this rule read nothing")
        return found, ""
    return (), ("prompts/digest.md is not beside this file or at "
                "/root/prompts/digest.md, so only the hand floor was applied")


def slot_heading(heading: str, dress) -> str:
    """Why one printed heading is the framework's own name, or the empty string.

    Three readings, each of them quoted law rather than taste. They are the
    canon's, lifted here so the verdict arrives before the send instead of in a
    grade written afterwards.

    1. The ban's own list: a heading that IS one of the phrasings, or wears one
       as the label before a colon.
    2. The prefix, because equality was the whole test until 2026-11-08.
       `## What to read` was banned, and `## What to read yourself` then served
       past the list the product had just been patched to hold. One trailing
       word walked through, so the list is not where this can be held: the
       phrasing plus a remainder that would be true of every issue is the
       phrasing.
    3. The colon. The generator says in its own words that a colon does not
       launder the label, and 2026-W40 served that construction three times.
       The shape is the finding and no list of phrasings can hold it, because
       the laundered label is written fresh each time: `gaining ground` and
       `genuinely new` are in no list anybody keeps.

    What it deliberately passes is a heading that opens on `What` and then
    makes a claim. `## What to read if you have one hour` is the generator's
    own worked answer for that slot and has to survive this.
    """
    text = heading.lstrip("#").strip().strip("*_")
    low = text.lower().rstrip(" .")
    label = low.split(":", 1)[0].strip() if ":" in low else low
    for phrase in dress:
        if label == phrase:
            return f"the ban's own phrasing, {phrase!r}"
    for phrase in dress:
        if label.startswith(phrase + " "):
            rest = label[len(phrase):].strip()
            if all(word in SLOT_INVARIANT for word in rest.split()):
                return (f"the ban's own phrasing, {phrase!r}, plus {rest!r}, "
                        "which is true of every issue")
    if ":" in low and low.startswith("what "):
        return f"a slot label laundered by a colon, {label!r}"
    return ""

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
INTENSIFIERS = ("very", "truly", "incredibly", "remarkably", "extremely")


def _word_edge(term: str) -> re.Pattern[str]:
    r"""A listed term matches a word, never the inside of one.

    The anchor is the left edge alone, because a listed word's inflections are
    the same defect as the word: "delves" and "revolutionized" have to block
    the way "delve" and "revolutionize" do, and closing the right edge too
    would let the generator through on a suffix.

    The left edge is the half that was missing. `INTENSIFIERS` held `"very "`
    and the test was `if word in low`, a substring match, so the gate read
    "behavioral recovery rate" and "Accelerate every builder" as the word
    "very" and warned on both. The second is the close the owner mandated on
    2026-09-30, which canon law 10 requires in every issue, so that finding
    could never be cleared by fixing the issue. It was filed 2026-09-24 and
    escalated at thirty days on 2026-10-24.

    The trailing space those terms carried was standing in for a boundary and
    it was the wrong one, which cost recall as well as precision: a line
    ending on "very" had no space after it and went unreported. `\b` is the
    general form of what the space was reaching for, so the space is gone.
    """
    return re.compile(rf"\b{re.escape(term)}", re.I)


# Compiled once at import, and paired with the term so the finding still names
# the word it found rather than a pattern. The per-line loop below runs over
# every line of every issue, so it builds nothing.
SLOP_ALWAYS_RX = tuple((_word_edge(word), word) for word in SLOP_ALWAYS)
HEDGES_RX = tuple((_word_edge(phrase), phrase) for phrase in HEDGES)
INTENSIFIERS_RX = tuple((_word_edge(word), word) for word in INTENSIFIERS)

# `SLOP_USUALLY` is the fourth list and it is the one that was already
# anchored, on both edges, which is why it is the only one of the four that
# has never produced a false finding. It keeps the pattern it has: loosening
# it to the left edge alone would newly warn on "robustness" and "landscapes",
# which is a widening nobody asked for and the opposite of this repair.
SLOP_USUALLY_RX = tuple(
    (re.compile(rf"\b{re.escape(word)}\b", re.I), word) for word in SLOP_USUALLY)

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
    """Every machine-decidable line of docs/product/digest-quality.md."""
    findings: list[Finding] = []
    lines = _lines(body)
    lowered = body.lower()
    items = parse_items(body)

    def add(level, rule, line, detail, entry):
        findings.append(Finding(level, rule, line, detail, entry))

    # --- accuracy and structure ---
    # Two readings of one rule. The floor is the hand list of the generator's
    # internal labels; the second is derived from the ban itself and catches
    # the reader-facing paraphrase, which is the shape that actually prints.
    # They are reported under separate rule names because a log that cannot
    # tell them apart cannot say which half fired, and the derived half is the
    # one that was missing.
    dress, unreadable = slot_dress()
    if unreadable:
        add(WARN, "slot-ban-unreadable", 0, unreadable, "19, 20")
    for number, line in enumerate(lines, start=1):
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().strip("*_").lower()
        floor = False
        for banned in SKELETON_HEADINGS:
            if heading == banned or heading.startswith(banned + " ") or heading.endswith(" " + banned):
                add(BLOCK, "skeleton-heading", number,
                    f"{line.strip()!r} prints the generator's own slot label", "19, 20")
                floor = True
        if floor:
            continue   # one defect, one finding; the floor already named it
        why = slot_heading(line, dress)
        if why:
            add(BLOCK, "slot-heading", number,
                f"{line.strip()!r} is {why}; write the heading from the day's "
                "news instead", "19, 20")

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
        for pattern, word in SLOP_ALWAYS_RX:
            if pattern.search(low):
                add(BLOCK, "slop-lexicon", number, f"{word!r}", "1")
        for pattern, word in SLOP_USUALLY_RX:
            if pattern.search(low):
                add(WARN, "slop-lexicon", number, f"{word!r} (the paper's own word, or ours?)", "1")
        for pattern, phrase in HEDGES_RX:
            if pattern.search(low):
                add(WARN, "hedge-stack", number, f"{phrase!r}; state it or grade it", "4")
        for pattern, word in INTENSIFIERS_RX:
            if pattern.search(low):
                add(WARN, "empty-intensifier", number, f"{word!r}", "5")

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

    # --- canon law 14: the shape of the page ---
    # The second rule the writer seat routed here on 2026-11-01, filed as "Law
    # 14's one-shape failure cannot block a send". The gate had eight blocking
    # rules and not one of them measured the shape of the page, so an issue set
    # as one column of grey paragraphs was green at the only gate that can stop
    # a send. The owner has read that page and rejected it twice, and the
    # market seat's ranking of 2026-09-24 put alexandria last on exactly this
    # while first on rigor: "a formatting and craft gap, not a substance gap".
    #
    # Two devices of law 14's three, and only these two, because a list with
    # parallel results and a written turn inside a long section are the two no
    # furniture can fake. A person on the page is a reading. Same pair
    # `docs/voice/check_voice.py devices` takes, so the two commands cannot
    # reach different verdicts on one page.
    #
    # Why it blocks, which was a judgment made against this file's own policy
    # and is recorded because it could have gone the other way. `warn` is for a
    # rule the generator cannot satisfy, and the first draft of this rule
    # warned on exactly that reading, because the served issue fails it. Three
    # facts moved it:
    #
    #   1. `prompts/digest.md` states this one as "A hard gate (canon law 14)"
    #      that "can fail an issue by itself", and "One kind is a failing
    #      issue, whatever the word counts say". Blocking is implementing that
    #      sentence rather than tightening it.
    #   2. The same file mandates the shape it wants, "Bullets where the
    #      results are parallel", so the generator is already told to do this
    #      and 2026-W39 is a deviation from its instructions rather than a
    #      rule nothing can meet. The GOOD fixture in
    #      tests/test_digest_quality.py meets it.
    #   3. `docs/voice/check_voice.py ungated` counts rules the press cannot
    #      refuse, and it counts BLOCK rules only. A warning leaves this row
    #      UNGATED, which is the L-A22 condition of a target-zero rule
    #      enforced by a model reading a long file. A warning would have
    #      looked like a repair in a diff and moved that register not at all.
    #
    # The cost is bounded and it is not the issue. A blocking finding gives the
    # generator one more try with `corrections()` as instructions, and this
    # instruction is structural rather than a matter of taste, so the retry is
    # the likely end of it. If it survives the retry the email is held and the
    # body is still written to the digests table, which is `hold_for_quality`'s
    # contract and not new here.
    # Not on the short edition, and this is the one scope decision in this rule
    # that was found by a gate rather than by reading. `check_voice.py
    # blockrules` reports every BLOCK rule here against the prompt that writes
    # the degraded edition, and it named this one UNRULED with the consequence
    # attached: "block on the short edition holds the issue". Measured rather
    # than assumed, `prompts/digest-short.md` asks for no list and no written
    # turn anywhere in its 132 lines, and says "No other sections", so this
    # rule would hold every degraded week. The degraded edition exists because
    # 2026-10-12 was a week with no issue at all, so a rule that blocks it
    # recreates the failure the edition was built to prevent. The full edition
    # is where law 14 is mandated and it is the edition every healthy Monday
    # prints.
    if kind == "weekly" and SHORT_EDITION_NOTE not in body:
        devices = []
        for block in re.split(r"\n\s*\n", body):
            rows = [x.strip() for x in block.strip().split("\n") if x.strip()]
            if not rows:
                continue
            if rows[0].startswith("### "):
                devices.append("turn")
            elif not rows[0].startswith("#") and BULLET.match(rows[0]):
                # The FIRST row, which is what Markdown means by a list item:
                # the rows under a bullet are the bullet's continuation, not
                # separate blocks. The canon's `shapes` asks this of every row
                # instead, and the press's mandated item shape is a bold claim
                # wrapped over two or three lines with prose under it, so no
                # item the generator can write satisfies an all-rows reading.
                # Measured on this repository's own fixtures: the worked
                # tier-four issue in tests/test_digest_quality.py has two such
                # blocks and `shapes` scores it `list: 0`, so law 14 would fail
                # the one issue the gate holds up as correct. That is the same
                # blindness `check_voice.py` recorded for the citation line one
                # level down, and it is filed for the writer seat rather than
                # fixed here, because docs/voice/ is that seat's surface.
                devices.append("list")
        if not devices:
            add(BLOCK, "one-shape", 0,
                "the page is one shape, with no list and no written turn in it; "
                "find the material in the payload that is genuinely parallel, "
                "meaning several results that did the same kind of thing, and "
                "set that part as a list with a short bold lead per item on the "
                "same line as its sentence, or give a section running past four "
                "paragraphs a third-level written turn", "49")

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
