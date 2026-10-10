#!/usr/bin/env python3
"""Three editorial checks that were prose rules until 2026-10-04 (L-A22).

A rule enforced by a sentence in a register is enforced at the reliability of
a model reading a file. Each check below replaced such a sentence, and each one
caught a live defect on the run that wrote it.

1. `enforcements`, docs/voice/ban-list.md ban list 92. An entry's second
   ending names the change to the generator that enforces it. Thirty-four of
   thirty-five named it in prose, so verifying the register meant a close
   reading of prompts/digest.md and nothing re-ran a close reading. This
   reports the ratio and verifies every quoted ending against the live
   generator, matching on normalised whitespace because both files wrap.

2. `stale`, ban list 89 and 90. A prompt is read on a day it was not
   written, so a sentence in it describing the INPUT is a claim about a day
   that has passed. Entry 89 named the class, struck its two specimens, and
   left three live where this command would have found them.

3. `measure`, ban list 91. A measurement carried from one artifact to
   another is how a FAIL got recorded against a clean issue for four days.
   Prints the character census per path, so no figure can be shared between
   two artifacts in a grade.

4. `links`, ban list 100. Law 8's form half. A grade that checks the prefix
   checks the part of the url the law names and not the part the reader
   clicks, which cleared a composed identifier twice. Reports path segment and
   identifier apart, and fails when one artifact disagrees with itself about
   the version suffix.

6. `sweep`, the ledger filing of 2026-09-27. The standing rule that an entry
   ends in the generator change enforcing it was written on 2026-09-25, so
   nothing ever asked whether entries 1 to 50 landed anywhere. This holds the
   answer as data rather than as a pass somebody ran once: every one of the
   fifty is mapped to the text in `prompts/digest.md` that enforces it, or to
   the ledger entry saying why no prompt can. It fails when an anchor leaves
   the generator and when an entry in that range has no row at all.

Not wired to anything yet, which is the honest half of L-A22: until a command
that already runs calls this, these are enforced at the reliability of someone
choosing to type it. Filed in docs/ideas.md for the engineer, to move to
tools/ and add to .github/workflows/checks.yml beside check_registers.py.
The stronger form of check 4 needs the corpus and is filed with it.

Usage:  python3 docs/voice/check_voice.py
          [enforcements|stale|measure|links|delivery|sweep|all] [path...]
Exit:   1 if any check reports a finding, 0 if clean.
"""
import collections
import html
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
BAN = ROOT / "docs/voice/ban-list.md"
DIGEST = ROOT / "prompts/digest.md"
CANON = ROOT / "docs/voice/canon.md"

# The tell from ban list 89, which is the entry's own giveaway. "the last
# issue" and "the newest print" are here because both are referents that move
# to the artifact being written, which is the subtler half of the same class.
STALE_TELL = r"today's|of today|the last issue|the newest print"

norm = lambda s: re.sub(r"\s+", " ", s).strip()


def entries(text):
    """ban-list.md as {number: body}, split on a line starting "N. "."""
    parts = re.split(r"\n(?=(\d+)\. )", "\n" + text)
    out, i = {}, 1
    while i < len(parts):
        out[int(parts[i])] = parts[i + 1]
        i += 2
    return out


LANDED = re.compile(r'LANDED\s+(\S+?):\s*"([^"]+)"')


def enforcements():
    """Ban list 92. An entry's enforcement ending may carry one or more

    LANDED <path>: "exact text"

    lines, naming the file the change landed in and quoting it verbatim. Those
    are checked exactly, on normalised whitespace, because every file in this
    register wraps its prose. An entry with no LANDED line is reported as
    prose-only: still true, still unverifiable by anything but a reading.

    The convention exists because the obvious heuristic does not work. Quoted
    strings near the word "Enforced" are as often the BANNED specimen as the
    landed repair, and entry 46 quotes two banned labels in exactly that
    position. A check that cannot tell a ban from a fix reports the ban as a
    pass.
    """
    ban = BAN.read_text()
    cache = {}
    prose, ok, missing = [], [], []
    for num, body in sorted(entries(ban).items()):
        nb = norm(body)
        claims = LANDED.findall(body)
        # The "Enforced" word is what the register's own rule keys on, and it
        # was this check's precondition until 2026-10-08, when entry 102 landed
        # a gate without one. That entry's ending is a filing for the engineer
        # PLUS a gate here, which is a third shape the rule did not anticipate,
        # and the old precondition skipped the entry whole rather than checking
        # the line it did carry. A LANDED line is a checkable claim wherever it
        # sits, so the claim decides now and the word only decides the ratio.
        if not re.search(r"Enforced\b", nb) and not claims:
            continue
        if not claims:
            prose.append(num)
            continue
        for path, text in claims:
            f = ROOT / path
            if path not in cache:
                cache[path] = norm(f.read_text()) if f.exists() else None
            hay = cache[path]
            if hay is None:
                missing.append((num, path, text, "no such file"))
            elif norm(text) in hay:
                ok.append((num, path, text))
            else:
                missing.append((num, path, text, "not in file"))

    verified = {n for n, _, _ in ok} | {n for n, _, _, _ in missing}
    print(f"entries carrying an 'Enforced' ending      {len(prose) + len(verified)}")
    print(f"  carrying a checkable LANDED line         {len(verified)}")
    print(f"  prose only, verifiable by reading        {len(prose)}")
    for num, path, text in ok:
        print(f'  OK      entry {num:>3}  {path}: "{text[:54]}"')
    for num, path, text, why in missing:
        print(f'  FAIL    entry {num:>3}  {path}: "{text[:40]}" ({why})')
    if prose:
        print("  prose only: " + ", ".join(map(str, prose)))
    return 1 if missing else 0


# Ban list entries 1 to 50, each against the text in prompts/digest.md that
# enforces it. The standing "an entry is not finished when it is written" rule
# arrived on 2026-09-25 and binds entries from 51 on, so this range was never
# asked the question, and the gap was filed in docs/ideas.md on 2026-09-27 as
# work for this seat with no dependency on anyone. Executed 2026-10-09.
#
# Why a map and not a one-time pass. The filing asked for fifty endings written
# into the register, and the register's own rule says to seed the quoted form
# rather than backfill it, "because a LANDED line asserted without checking the
# generator is worse than the prose it replaced". Forty-six of these are the
# same ending pointing at four places in one file, so written as prose they are
# forty-six sentences nothing re-reads. Written here they are forty-six strings
# a command re-reads every run, which is the whole difference L-A22 names.
#
# A row is the shortest distinctive phrase that carries the rule, never the
# whole rule, because the rule gets rewritten and the phrase survives.
SWEEP = {
    1: "the word that fills the slot where a fact belongs",
    2: "One precise adjective, or the number the three were standing in for",
    3: "Never let three sentences in a row scan the same length and shape",
    4: "The hedge that shrinks a claim the evidence has already graded",
    5: "the intensifier that inflates one",
    6: "never the rhetorical kind that answers itself",
    7: "never let it recap the issue",
    8: "does this add information, or does it tell the reader how to feel",
    9: "None of those subjects is anybody",
    10: "a closing summary of what the reader just finished reading",
    11: "And no colon. The shape the mark makes here is a short label",
    12: "every item weighted alike however much each actually matters",
    13: "Plain ASCII punctuation, always",
    14: "could a subscriber who has never seen alexandria's codebase say what",
    15: "Printing everything `deep_reads` returned is the opposite of judgment",
    16: "Group the rows by paper yourself",
    17: '"Welcome to another edition" and "Happy Monday" are the other failure',
    18: "Frame the content, never the section",
    19: '"Compounding", "New and unproven", "Key takeaways", "What this means"',
    20: "Those are this file's internal names for the slots",
    21: "Padding a thin day and truncating a heavy one are the same failure",
    22: "The date does NOT belong in this line",
    23: "Then say what is in here, in one line, before any interpreting starts",
    24: "A number without its comparison is not finished, in any section",
    25: "Then what a builder does differently now.",
    26: "club words until the sentence itself issues membership",
    27: "no paragraph past about 100 words",
    28: "No sentence about the future that no result can check",
    29: "assert that two papers share people",
    30: "a label is a label whether it sits at heading level or in bold",
    31: '"Builders should X" three items running is the spine showing through',
    32: "are the field's nicknames",
    33: "every run of bold or italic text sitting alone on its own line",
    34: "names one of alexandria's own tables at a reader who has never heard",
    35: "A slot the day gave nothing to holds nothing, and its heading goes",
    36: "it is the question that decides, never a list",
    37: "The test is removal",
    38: "That colleague is serious",
    39: "Do not open those lines with a verb of presentation",
    40: "full stop that went untyped",
    41: "Assume every string you were handed is contaminated",
    42: "is a single reader rather than the field moving",
    43: "A stored sentence kept for empty days is furniture the moment it runs",
    45: 'Find every sentence in the issue whose subject is "you" and whose verb',
    46: "The second is the text in front of any colon",
    47: "A line of plain meaning after every result",
    48: "that is entirely bold, standing alone",
    49: "One kind is a failing issue",
    50: "If you find yourself writing the concession, you do not have",
}

# The entries in that range no edit to this generator can reach, with the
# ledger entry that holds each one. Entry 44 is the whole class: it is about
# generators other than this one, and the file it was written from has never
# been on main. Entry 43 is anchored above AND filed here, because the rule
# landed in this generator and the specimen it was written from lives in the
# other one, so closing the entry needs both halves.
SWEEP_FILED = {
    43: "2026-09-24 One craft layer, two cadence files",
    44: "2026-09-24 One craft layer, two cadence files",
}


def sweep():
    """Ban list 1 to 50 against the generator, as a standing check.

    L-A21 says a gate that saw nothing is a failure rather than a quiet pass,
    so this fails three ways: an anchor that has left prompts/digest.md, an
    entry in the range with no row at all, and a row for an entry number the
    register does not have.

    The domain comes from the register and never from the map, which is what
    keeps this from being the enumeration L-A26 and ban list 36 both warn
    about: a list of names answers confidently about the world it was written
    in. Here the register decides which entries must be covered and the map
    only answers for them, so an entry this file has never heard of fails
    rather than passing silently.

    What it cannot see, which is the other half of L-A21. An amendment. Four
    of these fifty say "Amended" in their own text, 13, 14, 16 and 33, and
    widening is what each amendment did: 13 went from three characters to
    every character outside ASCII, and 33 from three italic labels to four.
    The anchor checks that the entry is enforced somewhere and
    cannot check that the enforcement is as wide as the entry became, so an
    amendment that outgrows its rule passes here. That is a reading, and it
    belongs to pass 4 of the grading procedure rather than to this command.
    """
    have = set(entries(BAN.read_text()))
    want = {n for n in have if n <= 50}
    hay = norm(DIGEST.read_text())
    gone = [(n, a) for n, a in sorted(SWEEP.items()) if norm(a) not in hay]
    unmapped = sorted(want - set(SWEEP) - set(SWEEP_FILED))
    phantom = sorted((set(SWEEP) | set(SWEEP_FILED)) - have)
    print(f"ban list entries 1 to 50                   {len(want)}")
    print(f"  anchored in prompts/digest.md            {len(SWEEP)}")
    print(f"  no prompt can reach, filed instead       {len(SWEEP_FILED)}")
    for n, where in sorted(SWEEP_FILED.items()):
        print(f"  FILED   entry {n:>3}  docs/ideas.md: {where}")
    for n, a in gone:
        print(f'  FAIL    entry {n:>3}  anchor gone: "{a[:56]}"')
    for n in unmapped:
        print(f"  FAIL    entry {n:>3}  in the register and in no row here")
    for n in phantom:
        print(f"  FAIL    entry {n:>3}  row here and not in the register")
    if not (gone or unmapped or phantom):
        print("  every anchor is still in the generator")
    print()
    print("An anchor is the phrase, never the rule. A rule that was rewritten")
    print("and still enforces the entry keeps its row. A rule that was deleted")
    print("takes the entry's enforcement with it, and that is what fails here.")
    return 1 if (gone or unmapped or phantom) else 0


def stale():
    hits = []
    for n, line in enumerate(DIGEST.read_text().split("\n"), 1):
        if re.search(STALE_TELL, line):
            hits.append((n, line.strip()))
    print(f"prompts/digest.md lines matching the ban list 89 tell   {len(hits)}")
    for n, line in hits:
        print(f"  {n:>5}: {line[:88]}")
    print()
    print("Each hit is read by hand, because the tell cannot tell the two apart:")
    print("  a claim about past OUTPUT is evidence for a rule and stays,")
    print("  a claim about the INPUT is false by the next morning and goes.")
    return 0


HIDDEN = re.compile(r'HIDDEN_WEEKS\s*=\s*new Set\(\[([^\]]*)\]\)')


def hidden_weeks():
    """Weeks retired at the serving layer, so not reader-facing.

    `site/lib/content.js` hides 2026-W37 on the owner's order of 2026-09-19.
    Its markdown fixture is still on disk and carries 152 non-ASCII characters,
    which is the figure a grade once reported against the issue that replaced
    it. A check that fails on a page nobody serves is noise, and L-A21 says a
    gate is judged by what it can see.
    """
    f = ROOT / "site/lib/content.js"
    if not f.exists():
        return set()
    m = HIDDEN.search(f.read_text())
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()


def shapes(blocks):
    """How many KINDS of block are on the page, which is canon law 14's first count.

    Law 14 names five counts and says four of them can pass while this one
    fails, because splitting long paragraphs changes every other number and
    cannot change this one. The reprint that satisfied the other four and was
    still rejected scored one. This function was added on 2026-10-06 because
    the four it could already take were the four the law says are not the
    failing axis, so the instrument measured everything except the thing the
    owner's ruling is about.
    """
    kinds = collections.Counter()
    for b in blocks:
        lines = [x.strip() for x in b.strip().split("\n") if x.strip()]
        if not lines:
            continue
        if lines[0].startswith("### "):
            kinds["turn"] += 1                     # a subheading inside a section
        elif lines[0].startswith("#"):
            kinds["heading"] += 1
        elif all(re.match(r"^([-*+]|\d+\.)\s", x) for x in lines):
            kinds["list"] += 1
        elif len(lines) == 1 and len(b.split()) <= 25:
            kinds["standalone line"] += 1
        else:
            kinds["paragraph"] += 1
    return kinds


ARXIV = re.compile(r"arxiv\.org/(abs|html|pdf)/(\d{4}\.\d{4,5})(v\d+)?")


def links(paths=None):
    """Canon law 8's FORM half, which a prefix check cannot see (ban list 100).

    Two consecutive grades read the newest issue's three links, saw that three
    of three began with `arxiv.org/html/`, and recorded the form as clean. Two
    of them carried the version suffix the payload supplied and the third did
    not. The prefix is the part law 8 names, because it is the part the rule is
    about. The identifier is the part that decides whether the reader reaches
    the paper, and the law cannot name it, because it is meant to be copied
    rather than chosen.

    So this reports the path segment and the identifier separately, and it
    fails on a disagreement WITHIN one artifact. A version suffix on two links
    out of three is nobody's editorial choice, and inconsistency is the one
    tell available without the payload in hand.

    What it cannot see, stated here rather than discovered by a later grade.
    An artifact that drops the version from EVERY link agrees with itself and
    passes. 2026-W39 is that case, six html links and no suffix on any of
    them. Catching it needs each identifier compared to `papers.url`, and that
    comparison is not decidable today either: 394 groups of rows in `papers`
    are one arXiv paper under several version ids, so three of W39's four ids
    match a bare row and a versioned row both, and "copy the identifier
    exactly" has two correct answers until the corpus is deduplicated. Filed
    for the engineer with the dedup, because the writer's rule cannot be made
    unambiguous ahead of it.
    """
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    retired = hidden_weeks()
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"{p}: missing")
            continue
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        off = p.stem in retired
        found = ARXIV.findall(p.read_text(encoding="utf-8"))
        print(f"{shown}" + ("   [retired, not served]" if off else ""))
        if not found:
            print("  no arXiv links")
            continue
        seg = collections.Counter(s for s, _, _ in found)
        ver = collections.Counter("versioned" if v else "bare" for _, _, v in found)
        print(f"  arXiv links {len(found):<4} "
              + "  ".join(f"{k} {v}" for k, v in sorted(seg.items()))
              + "   " + "  ".join(f"{k} {v}" for k, v in sorted(ver.items())))
        for s, i, v in found:
            print(f"    {s:<5} {i}{v or ''}")
        bad = [s for s in seg if s != "html"]
        if bad and not off:
            print(f"    law 8 wants the html full text, not {', '.join(sorted(bad))}")
            rc = 1
        if len(ver) > 1 and not off:
            print("    one artifact disagrees with itself about the version "
                  "suffix, so at least one identifier was composed rather "
                  "than copied (ban list 100)")
            rc = 1
    print()
    print("The prefix is what law 8 says. The identifier is what the reader")
    print("clicks. A verdict on the first is not a verdict on the second.")
    return rc


def measure(paths=None):
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"{p}: missing")
            continue
        t = p.read_text(encoding="utf-8")
        na = collections.Counter(c for c in t if ord(c) > 127)
        paras = [x for x in re.split(r"\n\s*\n", t) if x.strip()]
        lens = [len(x.split()) for x in paras]
        off = p.stem in retired
        # Never relative_to(ROOT): the canon names the stored `digests` row as
        # an artifact to grade and a row dumped to a file is outside the repo,
        # so the one tool written to stop a figure drifting off its artifact
        # used to raise rather than measure it (2026-10-06).
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        print(f"{shown}" + ("   [retired, not served]" if off else ""))
        print(f"  words {len(t.split()):<6} paragraphs {len(paras):<4} "
              f"longest {max(lens) if lens else 0:<4} over100 {len([x for x in lens if x > 100])}")
        print(f"  em dashes {t.count(chr(8212)):<4} semicolons {t.count(';'):<4} "
              f"non-ASCII {sum(na.values()):<5} distinct {len(na)}")
        kinds = shapes(paras)
        body = {k: v for k, v in kinds.items() if k != "heading"}
        links = set(re.findall(r"https?://[^)\\s]+", t))
        print(f"  shapes {len(body):<5} links {len(links):<5} "
              + "  ".join(f"{k} {v}" for k, v in sorted(body.items())))
        if len(body) < 2:
            print("    one kind of block is a failing issue (canon law 14)")
        for c, k in na.most_common():
            print(f"    U+{ord(c):04X} {unicodedata.name(c, '?'):<28} x{k}")
        if not off and (sum(na.values()) or t.count(chr(8212))):
            rc = 1
    print()
    print("Every figure above is printed under the path it was measured on.")
    print("A grade quotes it with that path or does not quote it (ban list 91).")
    return rc


# The press renders an issue twice. The site gets the markdown, and a
# subscriber gets `pipeline/email_render.py` over `site/emails/digest.html`.
# Only the second one edits the words on the way out, and it is the one half of
# the product no grade had ever executed (ban list 101, 102, 103).
EMAIL_KEY = "2026-W40"


def delivery(paths=None):
    """What a subscriber receives, which is not what the grade reads.

    Canon pass 6 asks a grade to walk the path the words take, from the
    model's output to the reader's eye, and grade every string that joins or
    changes them. Written as a sentence, that pass was executed twice by
    listing assignments in `pipeline/`. Listing a constant is not running the
    renderer, and the three findings below were all invisible to a reading.

    So this imports the real renderer and puts the real artifact through it.
    Three questions, each one a defect already confirmed on 2026-W40:

    1. Does every editorial line reach the inbox? `parse_issue` assigns only
       the first line after the closing rule to the `{{stats}}` slot and drops
       the rest. The sign-off is written in two moves, so the issue that sets
       them as two paragraphs loses one, and the one it loses is the scale
       sentence canon law 15 exists to protect.

    2. Does a list survive as a list? Law 14 requires parallel results set as
       bullets. `parse_section` reads a top-level bullet as a new ITEM, so the
       points list stays empty and three parallel bullets render as three
       paragraphs in the body register. The site renders the same markdown as
       a real `<ul>`, so the shape law 14 asks for exists on one surface and
       is flattened on the other, after the last gate, by code.

    3. Does the inbox preview stand alone? The preview is the first sentence of
       the opening, which is written to continue into the second. 2026-W40's is
       128 characters and truncates inside "until this week those two pipel".

    What it cannot see. It does not read the typography, so it cannot tell that
    the stats slot is 12px grey monospace below the sign-off or that every
    section heading is set uppercase. Those are the template's, they are filed,
    and a character census would not find them either.
    """
    try:
        sys.path.insert(0, str(ROOT))
        from pipeline import email_render as er
    except Exception as exc:                        # noqa: BLE001
        print(f"  renderer unavailable, so the delivery path is ungraded: {exc}")
        return 1
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    rc = 0
    for raw in paths:
        p = pathlib.Path(raw)
        if not p.exists():
            print(f"{p}: missing")
            rc = 1
            continue
        md = p.read_text(encoding="utf-8")
        print(f"{p}")
        issue = er.parse_issue(md)
        rendered = er.render_issue(md, EMAIL_KEY, "reader@example.com",
                                   "https://example.com/u")
        # Entities have to come back before anything is compared. The first
        # version of this compared escaped html against raw markdown and
        # reported 2026-W39's sign-off as dropped over one apostrophe.
        seen = norm(html.unescape(re.sub(r"<[^>]+>", " ", rendered)))

        # 1. the sign-off, which is every line after the closing rule.
        tail = [l.strip() for l in re.split(r"^\s*---+\s*$", md, flags=re.M)[-1]
                .split("\n") if l.strip()]
        standing = norm(er.CLOSE).rstrip(".")
        dropped = [l for l in tail if standing not in norm(l)
                   and norm(er.normalise(plain_md(l)))[:40] not in seen]
        print(f"  sign-off lines {len(tail)}    dropped {len(dropped)}")
        for l in dropped:
            print(f"    DROPPED  {l[:72]}")
            rc = 1

        # 2. the lists, which law 14 requires and the renderer flattens.
        bullets = len([l for l in md.split("\n")
                       if re.match(r"^[-*] +\S", l)])
        points = sum(len(i["points"]) for s in issue["sections"]
                     for i in s["items"])
        print(f"  top-level bullets {bullets}   rendered as list points {points}")
        if bullets and not points:
            print("    every bullet was read as a separate item, so the list law 14")
            print("    asks for reaches a subscriber as paragraphs (ban list 102)")
            rc = 1

        # 3. the inbox preview.
        pre = er.preheader_for(issue)
        print(f"  inbox preview {len(pre)} chars")
        if len(pre) > 90:
            print(f"    truncates at  {pre[:90]!r}")
            print("    the preview is one sentence of the opening, so an opening")
            print("    written to continue sells a fragment (ban list 103)")
            rc = 1
    print()
    print("The renderer ran. A constant inventory is not this check, and")
    print("two executions of canon pass 6 found none of the three.")
    return rc


def plain_md(line):
    """Markdown stripped the way the renderer strips it, for comparison only."""
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    return re.sub(r"[*_`]", "", line)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    # Paths after the subcommand go to `measure`. Without this, the arguments
    # were accepted and silently ignored, so `measure <path>` reported on
    # site/content/issues and a grade could read the wrong artifact's figures
    # under the right artifact's name, which is the defect this file exists to
    # prevent (ban list 91, fixed 2026-10-06).
    paths = sys.argv[2:]
    rc = 0
    takes_paths = {"measure", "links", "delivery"}
    for name, fn in (("enforcements", enforcements), ("sweep", sweep),
                     ("stale", stale), ("measure", measure), ("links", links),
                     ("delivery", delivery)):
        if which in (name, "all"):
            print(f"==== {name} ====")
            rc |= fn(paths) if (name in takes_paths and paths) else fn()
            print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
