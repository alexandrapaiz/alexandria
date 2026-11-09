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

7. `claims`, docs/agents/quality-claims.md and the incident of 2026-10-18.
   The register names the machine under every public quality claim and the file
   that prints it, three charters tell a seat to read it, and two rows recorded
   as unbuilt stayed live in the present tense for eighteen days anyway. This
   reads every row against every reader-facing surface and fails when a claim
   that is not held ships without a hedge, or ships somewhere the row does not
   name.

8. `firstuse`, canon law 12a and her outsider ruling of 2026-09-19. The
   ruling is that every term of art carries its plain-words clause the first
   time it appears. `prompts/digest.md` carries it in seven places across
   about a hundred lines and the last archived issue breaks it in twenty-two,
   because the one class the pass says it exists to catch is defined by not
   looking like jargon, and finding those words in your own prose is a
   judgment about what you know made by the thing that knows it. This builds
   the inventory outside the model: every term of art in an issue, its count,
   and the sentence where the reader first meets it, counting the title, the
   masthead, the headings and the bold leads. The inventory is mechanical.
   Whether a clause defines its term is a reading and stays in the grade.

9. `generator`, the finding of 2026-10-23 and the repeat of the damage
   `tools/check_registers.py` was built for on 2026-09-24. That checker reads
   sixteen shared files for merge damage and the criterion in its own comment
   is that more than one seat appends to the file. `prompts/digest.md` is not
   on the list, and on the day this was written it was carrying four blocks of
   edit damage: two rule bullets, one slot instruction and one line each
   written in beside the copy the file already held, three of the four first
   copies ending mid-sentence. One of them opened a curly brace that never
   closed, so every slot from the reading list to the sign-off was nested
   inside an instruction block with no end, in a file that tells the model
   braces mark instructions to replace with its own words. No conflict marker,
   no failing test, no red anywhere: the loud form of this damage has a gate
   and the quiet form had none.

Usage:  python3 docs/voice/check_voice.py
          [enforcements|stale|measure|links|delivery|sweep|claims|
           reading|taste|candidates|firstuse|figures|generator|
           specimens|all]
           [path...]
        python3 docs/voice/check_voice.py enforcements <git-ref>
        python3 docs/voice/check_voice.py selfcheck <git-ref-or-range>
Exit:   1 if any check reports a finding, 0 if clean.
"""
import ast
import collections
import contextlib
import datetime
import html
import html.parser
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
BAN = ROOT / "docs/voice/ban-list.md"
DIGEST = ROOT / "prompts/digest.md"
#: The degraded edition's generator, which the press prints when no model can
#: take the full issue. `pipeline/budget.py` calls it `SHORT_ISSUE_PROMPT` and
#: says in its own comment that it is this seat's surface. Until 2026-10-24 no
#: gate in this repository named it, so the finding that closed writer run 47,
#: that no gate had ever read the generator, was still true of the second one.
SHORT = ROOT / "prompts/digest-short.md"
GENERATOR = ROOT / "prompts/digest.md"
#: Every file the press writes an issue from. The gates below default to this
#: list rather than to `DIGEST`, because a default naming one of two generators
#: reports a clean file and a silent one under the same verdict.
GENERATORS = [DIGEST, SHORT]
CANON = ROOT / "docs/voice/canon.md"
TASTE = ROOT / "docs/voice/taste.md"
#: The database's own column declarations, read rather than restated.
#: `receipt_columns` below is the only user, and it is here with the
#: other paths because the rule it enforces is the rule this block is an
#: instance of: a name this file needs lives in exactly one place.
SCHEMA = ROOT / "db/schema.sql"

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


def resolves(ref):
    """Does git know this ref, asked once rather than inferred from a result.

    `at_ref` returns None both for a path that is absent at the ref and for a
    ref that does not exist, and `added_lines` used to yield nothing in the
    second case. Both readings blame the artifact for a defect in the
    instrument's input, which is ban list 144. Callers ask this first so the
    message names the real cause.
    """
    return subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                          cwd=ROOT, capture_output=True).returncode == 0


def dead_ref(check, ref):
    """The one line a check prints when its base ref is not a ref."""
    print(f"  FAIL    {ref}: git does not know this ref, so `{check}` read nothing")
    print("Nothing was measured, so nothing is clean (ban list 144).")
    return 1


def at_ref(ref, path):
    """The bytes of one repository path at one git ref, or None if absent.

    Ban list 105. Every LANDED line in this register is checked against the
    working tree, and the working tree is not what writes the issue. The press
    runs an image built by a deploy, so `enforcements` run with no argument
    answers a question about a branch and reports it in the voice of a question
    about the product. Given a ref it answers the second question instead.
    """
    out = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                         capture_output=True)
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else None


def enforcements(ref=None):
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
    if ref and not resolves(ref):
        return dead_ref("enforcements", ref)
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
                if ref:
                    raw = at_ref(ref, path)
                    cache[path] = norm(raw) if raw is not None else None
                else:
                    cache[path] = norm(f.read_text()) if f.exists() else None
            hay = cache[path]
            if hay is None:
                missing.append((num, path, text, "no such file"))
            elif norm(text) in hay:
                ok.append((num, path, text))
            else:
                missing.append((num, path, text, "not in file"))

    verified = {n for n, _, _ in ok} | {n for n, _, _, _ in missing}
    print(f"read from   {ref or 'the working tree'}")
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


# The blocks that arrive on every issue whatever the generator writes, which
# the generator's own shape count already excludes in its own words: "the lines
# you did not write are not yours: the standing line under the title, the rule
# above the close, and the close itself". The first two come from
# `MASTHEAD` and `SHORT_EDITION_NOTE` in pipeline/weekly.py, spliced in by
# `add_masthead` before the row is stored. The last two are literal lines of
# the template in prompts/digest.md. Counted as the writer's work they put a
# floor of two under law 14's first count, so the categorical failure that law
# names, one kind of block, was unreachable (ban list 120).
FURNITURE = {
    "*What's new in AI research, what's gaining acceptance, and what newer "
    "evidence has overturned.*",
    "*A short edition. This week's issue is the week in brief.*",
    "---",
    "**Accelerate every builder and agent to frontier speed.**",
}


#: The citation line, mandated twice in prompts/digest.md as `*title* - [full
#: text](url)` on a line of its own. It is furniture exactly as the masthead is,
#: because the generator has no choice about printing one under every item, and
#: it is one short line standing alone, so `shapes` counted each one as canon
#: law 14's "number on a line" device. Four of 2026-W39's five standalone lines
#: are this. Page-level furniture was taken out of the count on 2026-10-06 and
#: this is the same blindness one level down: every issue the press can produce
#: carries at least one item, so the one condition `measure` fails on could not
#: be reached by any artifact.
ITEM_FURNITURE = re.compile(r"^\*[^*]+\*\s+-\s+\[full text\]\(\S+\)$")


def written_here(block):
    """Did the generator put this block on the page, or does it arrive anyway.

    Normalised on whitespace, because every copy of the issue wraps its prose
    differently and the stored row, the site page and a rehearsal dump do not
    agree on where a line ends.
    """
    flat = " ".join(block.split())
    if ITEM_FURNITURE.match(flat):
        return False
    return flat not in {" ".join(f.split()) for f in FURNITURE}


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


#: Whether `arxiv.org/html/<id>` exists, per identifier, for one process.
_HTML_EXISTS = {}


def html_full_text(ident):
    """Does the HTML full text exist for this arXiv identifier?

    The one question law 8's rule leaves to judgment, answered. The rule says
    to rewrite `abs` to `html` and then says "fall back to the abs page only
    when the paper has no HTML version", so an `abs` link is a violation or the
    rule working, and nothing in the artifact says which. This asks arXiv.

    Returns None when the question could not be reached, and a caller that
    gets None says the artifact was not graded on this axis rather than
    grading it clean. A bogus identifier answers 404 on both paths, which is
    what makes a 200 on `abs` with a 404 on `html` the fallback case rather
    than a broken link.
    """
    if ident in _HTML_EXISTS:
        return _HTML_EXISTS[ident]
    out = None
    for path in ("html",):
        req = urllib.request.Request(f"https://arxiv.org/{path}/{ident}",
                                     method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                out = 200 <= r.status < 300
        except urllib.error.HTTPError as e:
            out = False if e.code == 404 else None
        except (urllib.error.URLError, OSError, ValueError):
            out = None
    _HTML_EXISTS[ident] = out
    return out


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
    scope(paths, hidden_weeks())
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
            # Which of those the rule excuses, which is the half this check
            # used to leave to a reading. The rule's own fallback clause is
            # "only when the paper has no HTML version", so an abs link is a
            # violation exactly when the html url the rule asks for resolves.
            # 2026-W42 printed nine abs links and seven of the papers have a
            # live full text, so seven of its ten links stop at the abstract
            # against her ruling of 2026-09-19 in her own words, "you didn't
            # show me the paper". Entry 100's docstring called the stronger
            # comparison undecidable while the payload is out of reach. The
            # payload is, and arXiv is not.
            if os.environ.get("ALEXANDRIA_OFFLINE"):
                print( "      NOT CHECKED  whether the full text exists for each,")
                print( "                   ALEXANDRIA_OFFLINE is set, so every abs")
                print( "                   above is read as a violation")
                rc = 1
            else:
                excused, broke, unknown = [], [], []
                for seg_name, ident, v in found:
                    if seg_name == "html":
                        continue
                    exists = html_full_text(f"{ident}{v or ''}")
                    (broke if exists else
                     excused if exists is False else unknown
                     ).append(f"{ident}{v or ''}")
                print(f"      of those, full text exists  {len(broke)}"
                      f"   no full text {len(excused)}"
                      f"   unreached {len(unknown)}")
                for ident in broke:
                    print(f"      FAIL    abs/{ident} and arxiv serves"
                          f" html/{ident}")
                for ident in excused:
                    print(f"      OK      abs/{ident}, no html version, which"
                          f" is the rule's own fallback")
                for ident in unknown:
                    print(f"      UNKNOWN abs/{ident}, arxiv unreached, so this"
                          f" link was not graded")
                if broke or unknown:
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


def exempt_character(c):
    """Whether the ASCII rule in prompts/digest.md admits an exception for `c`.

    The rule's own words, at the plain-ASCII bullet: "The one exception is a
    person's or an institution's name as the payload spells it. Punctuation,
    spacing, separators and mathematical symbols get no exception at all." So
    the division is the character's unicode category and not the word it sits
    in, which is the one half of this a command can hold.

    Added 2026-10-16, because the census above was a bare count and a count
    cannot express an exception. The published print of 2026-W40 spelled the
    author of *Hard Stop* "Jose Luis Pino" against `papers.authors`, which
    holds "José Luis Pino", and scored zero non-ASCII characters. The
    rehearsal of the same generator spelled the name correctly and scored one,
    so this command exited non-zero on the print that obeyed the rule and
    clean on the print that stripped a researcher's name. The grade of
    2026-10-15 then quoted that figure as making the rehearsal "worse under
    law 1". Canon pass 1: a FAIL recorded against a clean artifact is worse
    than no grade.

    A letter is reported and left to the grade rather than scored, because the
    rule's exception turns on whose name it is and no command knows that. A
    Greek capital inside a system name is a letter and is NOT exempt under the
    rule, which is exactly why this returns a question and not a verdict.
    """
    return unicodedata.category(c).startswith("L")


def measure(paths=None):
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
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
        # The writer's own blocks, not every block on the page. The line below
        # used to read 2 on an issue whose generator had added nothing but
        # paragraphs, because the masthead, the rule and the close are three
        # standalone lines that arrive on every issue, so the sentence under it
        # could never print on an artifact this press can produce.
        kinds = shapes([b for b in paras if written_here(b)])
        body = {k: v for k, v in kinds.items() if k != "heading"}
        links = set(re.findall(r"https?://[^)\\s]+", t))
        print(f"  shapes {len(body):<5} links {len(links):<5} "
              + "  ".join(f"{k} {v}" for k, v in sorted(body.items())))
        if len(body) < 2:
            print("    one kind of block is a failing issue (canon law 14)")
        # The count above is the law's FIRST question and not its content. Law 14
        # names three devices as required rather than available, and two of them
        # are shapes no furniture can fake: a list where results are parallel,
        # and a written turn inside a section that runs long. The reprint she
        # read and rejected is described in the canon in exactly these terms,
        # "no list, no subheading inside any section, one shape", and it would
        # have scored two here on its paragraphs and its citation lines alone.
        if not body.get("list") and not body.get("turn"):
            print("    no list and no written turn (canon law 14's two named "
                  "devices).")
            print("    This is the shape of the reprint she rejected. The count "
                  "above")
            print("    cannot see it, because paragraphs and one standalone line "
                  "are two.")
            print("    `devices` is the command that holds this. This one "
                  "measures and reports,")
            print("    because its exit code is the character gate's and is "
                  "read by a test.")
        # The colon count, with its specimen and the law it detects. `axes`
        # returns this as a bare number and `measure` printed nothing at all,
        # so the one ruling the owner has had to give TWICE arrived at a grade
        # as "headings carrying a colon: 1" and read as punctuation. 2026-W40
        # printed "What is gaining ground: recursive self-improvement with
        # fewer guardrails", which is the framework's internal name, a colon,
        # and the day's news. The construction is what the count is for.
        for h in [h for h in re.findall(r"^#{1,3} .*$", t, re.M) if ":" in h]:
            print(f"    colon heading, canon law 12 and incident 20: "
                  f"{h.strip()[:72]}")
            print("      the internal names are never printed. Strike the "
                  "label and the colon,")
            print("      and check whether what is left is the heading.")
        unruled = 0
        for c, k in na.most_common():
            word = next((w for w in re.findall(r"\S*" + re.escape(c) + r"\S*", t)), "")
            if exempt_character(c):
                unruled += k
                print(f"    RULE  U+{ord(c):04X} {unicodedata.name(c, '?'):<24} "
                      f"x{k}  in {word!r}")
            else:
                print(f"    U+{ord(c):04X} {unicodedata.name(c, '?'):<28} x{k}"
                      + (f"  in {word!r}" if word else ""))
        if unruled:
            print(f"    {unruled} letter(s) above are the generator's own exception, which is "
                  "a person's or")
            print("    an institution's name as the payload spells it. A grade rules on each "
                  "against")
            print("    `select authors from papers`, and a name stripped to reach zero is the "
                  "finding.")
        strict = sum(k for c, k in na.items() if not exempt_character(c))
        if not off and (strict or t.count(chr(8212))):
            rc = 1
    print()
    print("Every figure above is printed under the path it was measured on.")
    print("A grade quotes it with that path or does not quote it (ban list 91).")
    return rc


def devices(paths=None):
    """Canon law 14's two named devices, as an exit code of their own.

    This is deliberately not folded into `measure`. That command's exit code
    means one thing, which is the character gate, and
    `tests/test_voice_enforcements.py` asserts on it by name. A second meaning
    on one return value makes the test report a cause that is not the cause,
    which is L-A44 in docs/standards/lessons.md, and the first version of this
    check did exactly that: the test said a served issue carried an em dash
    about an issue whose em dash count is zero.

    Why these two of the three devices. A list where results are parallel and a
    written turn inside a long section are the two no furniture can fake. The
    third, a person on the page, is a reading. The canon describes the reprint
    the owner rejected in exactly these terms, "no list, no subheading inside
    any section, one shape".
    """
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"{p}: missing")
            rc = 1
            continue
        t = p.read_text(encoding="utf-8")
        paras = [x for x in re.split(r"\n\s*\n", t) if x.strip()]
        kinds = shapes([b for b in paras if written_here(b)])
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        off = p.stem in retired
        have = [k for k in ("list", "turn") if kinds.get(k)]
        if off:
            print(f"  SKIP    {shown}  retired, not served")
        elif have:
            print(f"  OK      {shown}  carries {' and '.join(have)}")
        else:
            print(f"  FAIL    {shown}  no list and no written turn")
            rc = 1
    print()
    print("Law 14 names three devices as required rather than available, and")
    print("two of them are shapes. A pass here is not a verdict on whether the")
    print("issue is enjoyable, which stays a reading. A failure is a verdict,")
    print("because the one-shape page is the state she read and rejected.")
    return rc


# ---- figures -------------------------------------------------------------
#
# Canon law 14's fourth count, and the one quarter of it no command held.
#
# The generator states four counts in a single sentence group and this file
# scored three. "The longest paragraph: over about 100 words, split it at the
# point where the second result starts" is `axes`'s "paragraphs over 100
# words" at a target of zero. "Sections running past four paragraphs with no
# written turn in them" is its "sections over four paragraphs". The semicolon
# is the generator's fifth count and the colon heading its seventh, and both
# have rows. Between the first and the second of those sits "Numbers in the
# heaviest paragraph: past three, cut every number that does not change what
# the reader would do", and nothing in this file counted a number.
#
# What the gap cost, measured rather than argued. The grade of 2026-11-08
# named the figure dump as the single biggest weakness of `2026-W44`, the
# newest edition the product serves, and it had to count it by hand: one
# 64-word paragraph carrying nineteen numbers under a rule whose target is
# three. Every count this file could take on that edition passed. `measure`
# read `longest 87   over100 0`, so law 14's measurable half printed green on
# the artifact whose figure density is the headline verdict. Law 14's own text
# names that trap one line before the count: "A law whose measurable half can
# be satisfied while its point is missed is a law stated in the wrong order."
# L-A21 is the standard, a gate is judged by what it can see, and put to this
# file before this command the answer was that nothing here could see a
# number at all.
#
# The target is the generator's own three and it is scored rather than
# reported, on this file's own precedent instead of on a reading. "Over about
# 100 words" is hedged in the generator with the word "about" and `axes`
# scores it at zero tolerance, so its sibling in the same sentence group is
# scored the same way. The rule's second half, which of the numbers to cut,
# is a reading and stays in the grade where the other readings are.


#: A figure, and the two readings that decide what the count is of.
#:
#: First, a figure is a maximal run of digits with its own decimal point or
#: thousands comma inside it, so "68.33" is one figure and "21 of 25" is two.
#: A fraction is its two numerals, because a reader of "threshold 1/6" takes
#: in both of them, and the place to argue that is a grade rather than this
#: line.
#:
#: Second, the digits inside a NAME are not figures. A token whose first
#: alphanumeric character is a letter is a name for this count, so
#: "Qwen3.5-4B", "HMMT25", "GPT-5" and the arXiv identifier inside a link
#: contribute nothing. The reason is the rule's own second half: a model's
#: name is not a number anybody can cut, and a count that includes what no fix
#: can remove reports a paragraph that cannot be brought under the target. The
#: hand count of nineteen in the grade of 2026-11-08 counted a model
#: identifier's digits, so this gate reads that same paragraph at sixteen. The
#: number moved and the verdict did not, because both are past three.
FIGURE = re.compile(r"\d+(?:[.,]\d+)*")


def figures_in(block):
    """Every figure in one block, in the order the reader meets them."""
    out = []
    for token in block.split():
        head = next((c for c in token if c.isalnum()), "")
        if not head or head.isalpha():
            continue
        out.extend(FIGURE.findall(token))
    return out


#: What the reading has to get right, asserted before any edition is opened.
#: The first case is the live specimen the grade of 2026-11-08 quoted out of
#: `2026-W44`. The rest are the shapes that look like it and are not, because
#: a count that fired on a model's name or on a citation line would report a
#: paragraph no cut could repair, and a gate nobody can satisfy is a gate the
#: next run deletes. The last case is the boundary that has to keep passing.
FIGURE_CASES = (
    (16, "Across five models and five benchmarks, quantization and pruning "
         "variants improve average accuracy by **4.0** and **5.5 percentage "
         "points** respectively, with positive gains in **21 of 25** and "
         "**23 of 25** settings. The effect is non-monotonic in degradation "
         "strength: **3-bit** quantization peaks at **68.33%** on HMMT25 for "
         "Qwen3.5-4B, while **2-bit** collapses to **49.90%**. Pruning at "
         "threshold **1/6** peaks at **70.52%**, versus **49.58%** at "
         "**1/2**."),
    (0, "Qwen3.5-4B and GPT-5 were scored on HMMT25 and AIME24 by a group at "
        "Tsinghua, and the gap between them held across every run."),
    (0, "Berkeley and DeepMind, *Hard Stop*, "
        "[full text](https://arxiv.org/html/2610.38681v1)."),
    (3, "Accuracy rose from **61%** to **68%** across **25** settings, and "
        "the gain holds for every model the group tried."),
)


#: The generator's own number, quoted so a reader of this file does not have
#: to take the three on trust: "Numbers in the heaviest paragraph: past three,
#: cut every number that does not change what the reader would do."
FIGURE_TARGET = 3


def heaviest_paragraph(text):
    """The writer's own paragraph carrying the most figures, and its figures.

    A paragraph, and not a block, for the same reason `axes` counts sections
    in paragraphs. Law 14 asks the writer for "a line carrying the number that
    matters" as one of the shapes that saves a page, so counting a standalone
    line here would fire on the device the same law demands and the issue would
    be punished for obeying it. Lists are out on the same ground. The furniture
    is out because `written_here` is what separates the blocks the generator
    put on the page from the masthead, the rule and the close, which arrive on
    every issue whatever the model does.
    """
    best, blocks = ("", []), []
    for b in [x for x in re.split(r"\n\s*\n", text) if x.strip()]:
        if not written_here(b) or not shapes([b]).get("paragraph"):
            continue
        found = figures_in(b)
        blocks.append((b, found))
        if len(found) > len(best[1]):
            best = (b, found)
    return best, blocks


def figures(paths=None):
    """Law 14's figure count, as a verdict on an artifact.

    The whole-issue density is printed beside it and deliberately carries no
    target, because the generator states none. 52 figures in 1,017 words is
    the shape of the page and the grade reads it. Three in a paragraph is the
    rule and this is where it is enforced.

        python3 docs/voice/check_voice.py figures --live
    """
    wrong = [(want, case) for want, case in FIGURE_CASES
             if len(figures_in(case)) != want]
    for want, case in wrong:
        print(f"  BROKEN  the count reads {len(figures_in(case))} where its "
              f"own case says {want}")
        print(f"            {case[:84]}")
    if wrong:
        print()
        print("FIGURE_CASES says what this count has to do. Nothing below was")
        print("read, because a count failing its own cases reports a clean")
        print("issue for the wrong reason.")
        return 1
    print(f"  the count's own cases          {len(FIGURE_CASES)} pass")
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"  FAIL    {p}: missing, so nothing was counted")
            rc = 1
            continue
        t = p.read_text(encoding="utf-8")
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        if p.stem in retired:
            print(f"  SKIP    {shown}  retired, not served")
            continue
        (block, found), blocks = heaviest_paragraph(t)
        total = sum(len(f) for _, f in blocks)
        words = len(t.split())
        over = [b for b, f in blocks if len(f) > FIGURE_TARGET]
        per100 = (100.0 * total / words) if words else 0.0
        verdict = "FAIL" if len(found) > FIGURE_TARGET else "OK  "
        print(f"  {verdict}    {shown}  heaviest {len(found)}, target "
              f"{FIGURE_TARGET}, paragraphs past it {len(over)} of "
              f"{len(blocks)}")
        print(f"            {total} figure(s) in {words} words, "
              f"{per100:.1f} per 100 words, which has no target and is read")
        if len(found) > FIGURE_TARGET:
            flat = " ".join(block.split())
            print(f"            {len(block.split())} words: {flat[:96]}")
            print(f"            the figures: {', '.join(found)}")
            rc = 1
    print()
    print("The rule is the generator's fourth count and its number is three.")
    print("A pass here is not a verdict on whether the page reads as a wall,")
    print("which is the shape `devices` holds. A failure is a verdict, because")
    print("the number in the rule is the generator's own and not this file's.")
    return rc


def axes(path):
    """The measurable gates of one body, each as a number beside its target.

    One row per gate a command can hold. Every target is the generator's own
    or the canon's, cited in `compare` below, so a row is a verdict rather
    than a figure a grade has to interpret.
    """
    t = pathlib.Path(path).read_text(encoding="utf-8")
    paras = [x for x in re.split(r"\n\s*\n", t) if x.strip()]
    lens = [len(x.split()) for x in paras]
    kinds = shapes([b for b in paras if written_here(b)])
    na = sum(k for c, k in collections.Counter(
        c for c in t if ord(c) > 127).items() if not exempt_character(c))
    heads = re.findall(r"^#{1,3} .*$", t, re.M)
    # Sections, and the paragraphs and turns and links inside each, because
    # three of law 14's gates are per section and the whole-page counts above
    # cannot see a ten-paragraph section with no turn in it.
    #
    # A paragraph, and not a block. The trigger this serves is the generator's
    # own, "any section running past about four paragraphs gets a written turn
    # inside it", and the same law asks the writer for the other kinds of block
    # in the same breath: a line carrying the number that matters, a bulleted
    # list where the results are parallel, the turn itself. Counting blocks
    # made every one of those count against the section, so obeying one half of
    # law 14 tripped the other half, and six flags across two prints of
    # 2026-W40 were all of them false (ban list 121).
    secs, cur = [], None
    for b in paras:
        if b.startswith("## "):
            cur = {"head": b.strip(), "paras": 0, "turns": 0, "links": 0}
            secs.append(cur)
        elif cur is not None:
            cur["paras"] += shapes([b]).get("paragraph", 0) if written_here(b) else 0
            cur["turns"] += b.startswith("### ")
            cur["links"] += len(re.findall(r"\[full text\]", b))
    long_untitled = [s for s in secs if s["paras"] > 4 and not s["turns"]]
    # The reading list is the last section by construction, so a link anywhere
    # else is a link in a body section. That is the split the grade of
    # 2026-10-15 took by hand and the figure its finding turned on.
    body_links = sum(s["links"] for s in secs[:-1])
    return {
        "semicolons": (t.count(";"), 0, "le"),
        "em dashes": (t.count(EM), 0, "le"),
        "non-ASCII, no exception": (na, 0, "le"),
        "shapes the writer added": (len([k for k in kinds if k != "heading"]), 3, "ge"),
        "paragraphs over 100 words": (len([x for x in lens if x > 100]), 0, "le"),
        # Law 14's fourth count has three thresholds and this file scored two
        # of them for as long as it has existed. The third is `figures` and
        # its number is the generator's own three.
        "numbers in the heaviest paragraph":
            (len(heaviest_paragraph(t)[0][1]), FIGURE_TARGET, "le"),
        "list blocks": (kinds.get("list", 0), 1, "ge"),
        "sections over four paragraphs": (len(long_untitled), 0, "le"),
        "headings carrying a colon": (len([h for h in heads if ":" in h]), 0, "le"),
        "links to a full text": (len(re.findall(r"\[full text\]", t)), 1, "ge"),
        "links outside the reading list": (body_links, 1, "ge"),
    }


def compare(paths=None):
    """Two prints of ONE generator, gate by gate, so a patch can be aimed.

    Canon's artifact paragraph, added 2026-10-15: where `press_rehearsals`
    holds a body for the graded week at the artifact's own `prompt_sha`, it is
    a second sample of the identical generator and the grade measures both.
    That addition came from one axis. On 2026-10-05 two prints of the same file
    five and a half hours apart carried 13 links against 3, so three merged
    patches to the link rule had been aimed at a gap narrower than the spread
    between two runs of one wording.

    This is that reasoning as a command, over every gate a count can hold,
    because the conclusion was never about links. A gate whose two samples
    agree is DETERMINED: its wording is the binding constraint, so a patch to
    it is testable. A gate whose samples disagree is UNDETERMINED: the wording
    was identical in a print that passed and a print that failed, so a further
    wording of it is not a test of anything and the fix is a check outside the
    prompt. L-A22 is the standard this serves, and the ledger filing of
    2026-10-15 is the check it points at.

    The caller passes two bodies of the same week at the same `prompt_sha`,
    and the grade records both shas, because two prints of two generators
    compare nothing. The targets: zero semicolons and zero em dashes are canon
    law 1 and the generator's fifth count. Three shapes is law 14's own
    sentence, "two kinds is thin, three is an issue that reads like something a
    person made". Zero paragraphs over 100 words, zero sections over four
    paragraphs and zero headings carrying a colon are the generator's fourth
    and seventh counts. One list block is the sixth count, whose trigger is the
    superseded group and whose target is a list wherever that group runs past
    two entries.

    Two of those rows carried the wrong number until 2026-10-17 and both were
    law 14, which is the law four of the five determined failures sat on. The
    shape row counted the masthead, the rule and the close as the writer's
    work, so its floor was two and the one-kind failure law 14 calls
    categorical could not be reported. The section row counted blocks rather
    than paragraphs, so the lines and lists this same law demands pushed
    sections over their own threshold, and all six flags it raised on the two
    prints of 2026-W40 were false. Ban list 120 and 121, and the figures are
    not comparable to the ones a grade before that date printed.
    """
    if not paths or len(paths) != 2:
        print("compare takes two paths: the published body and the rehearsal")
        print("of the same week at the same prompt_sha.")
        return 1
    a, b = (axes(p) for p in paths)
    print(f"a  {paths[0]}")
    print(f"b  {paths[1]}")
    print()
    print(f"  {'axis':<32}{'target':>8}{'a':>6}{'b':>6}   class")
    tally = collections.Counter()
    for name in a:
        av, target, how = a[name]
        bv = b[name][0]
        ok = (lambda v: v <= target) if how == "le" else (lambda v: v >= target)
        mark = f"{'<=' if how == 'le' else '>='}{target}"
        if ok(av) == ok(bv):
            verdict = "determined " + ("pass" if ok(av) else "FAIL")
            tally["determined pass" if ok(av) else "determined FAIL"] += 1
        else:
            verdict = "UNDETERMINED"
            tally["undetermined"] += 1
        print(f"  {name:<32}{mark:>8}{av:>6}{bv:>6}   {verdict}")
    print()
    print(f"determined FAIL {tally['determined FAIL']}   "
          f"determined pass {tally['determined pass']}   "
          f"undetermined {tally['undetermined']}")
    print("A determined FAIL is where a wording patch is testable. An undetermined")
    print("gate held in one print and broke in the other under one wording, so the")
    print("next wording of it is not a test and the fix is a check the prompt cannot")
    print("carry (L-A22, and the ledger filing of 2026-10-15).")
    return 1 if tally["determined FAIL"] else 0


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
    scope(paths, hidden_weeks())
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


EM = chr(8212)
FENCE = re.compile(r"^\s*(```|~~~)")


class BadRef(Exception):
    """A base ref git could not resolve.

    Raised rather than returned because a failed diff and a clean diff are the
    same empty string at every call site, and a gate that cannot tell them
    apart reports the better of the two.
    """


def added_lines(ref):
    """Every line this diff adds, as (path, line number in the new file, text).

    `git diff -U0` so no context line is read as the run's own prose, and the
    hunk header carries the new file's line numbers, which is what makes a hit
    something a run can open rather than something it has to search for.
    """
    # A bare ref diffs that commit against the WORKING TREE, which is the
    # state a run is about to ask the owner to merge. `ref..HEAD` would read
    # the commits and miss every line the run has not committed yet, and the
    # draft that broke canon law 1 five times was uncommitted when it was
    # measured. A range is passed through, for a grade re-taken after a fix.
    out = subprocess.run(["git", "diff", "-U0", ref], cwd=ROOT,
                         capture_output=True, text=True)
    # A ref git cannot resolve fails with an empty stdout, and an empty stdout
    # is the same byte string as a clean diff. Every caller below then reports
    # no findings and returns 0, so the gate passes without reading anything.
    # That is ban list 144, and it cost two runs of this seat on 2026-10-26:
    # one reported "zero em dashes" over a branch the gate exits 1 on, and one
    # concluded the gate "reports zero on a file already committed", which is a
    # false belief about the instrument rather than about the prose. Loud here.
    if out.returncode != 0:
        detail = (out.stderr.strip().splitlines() or ["git could not resolve it"])[0]
        raise BadRef(f"{ref}: {detail}")
    path, n = None, 0
    for line in out.stdout.splitlines():
        if line.startswith("+++ b/"):
            path, n = line[6:], 0
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            n = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            yield path, n, line[1:]
            n += 1
    # `git diff` compares a ref to the working tree for TRACKED paths only, so
    # a file this run created is invisible here until `git add`. Every review,
    # every copy candidate and every incident filing is a new file, which makes
    # that the whole of this seat's output. Two planted violations in an
    # untracked file drew zero findings and both appeared the instant it was
    # staged (ban list 144). The docstring above says this reads the state a run
    # is about to ask a merger to take, and an uncommitted new file is exactly
    # that. A range is the one case that excludes them, because a range asks
    # about two commits and the working tree is not either of them.
    if ".." in ref:
        return
    others = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                            cwd=ROOT, capture_output=True, text=True)
    for rel in others.stdout.splitlines():
        f = ROOT / rel
        if not f.is_file():
            continue
        try:
            body = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(body.splitlines(), 1):
            yield rel, i, line


def fenced(path):
    """Which line numbers of a file sit inside a ``` block.

    Read off the working tree rather than guessed from the diff, because a
    fence opens on a line the diff may not have touched. A fenced line is the
    output of a command or the body of an artifact, quoted, so a mark in it is
    not this seat's prose. The first run of this check found two hits and one
    was the press surface's own FAILING line, pasted inside a fence.
    """
    f = ROOT / path
    if not f.exists():
        return set()
    out, inside = set(), False
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            out.add(n)
        elif inside:
            out.add(n)
    return out


def inline_quoted(line, open_at_start):
    """The characters of one line that sit inside an inline-code span.

    Returns the quoted characters and whether a span is still open at the end
    of the line, so a caller can walk a file and know the state each line
    begins in. `quoting` below reads one line with no memory, which is why it
    cannot see a span that opens on line 217 and closes on line 218.
    """
    out, inside = [], open_at_start
    for part in re.split(r"(`)", line):
        if part == "`":
            inside = not inside
            continue
        if inside:
            out.append(part)
    return "".join(out), inside


def code_state(path):
    """For every line of a file, whether an inline-code span was already open
    when the line began.

    A span does not cross a blank line, which is what stops one stray backtick
    from excusing the rest of a file, and a fenced line resets it because
    `fenced` already excuses those wholesale.
    """
    f = ROOT / path
    if not f.exists():
        return {}
    fences, state, inside = fenced(path), {}, False
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        state[n] = inside
        if n in fences or not line.strip():
            inside = False
            continue
        _, inside = inline_quoted(line, inside)
    return state


#: What `quoting` has to get right, as data, because the reading below was
#: changed on 2026-11-08 and a changed reading with no cases is a guess.
#: Fields: (excused, the line, whether a four-space indent means a code block)
QUOTING_CASES = (
    # Markdown, where an indent is a fenceless code block and the mark is the
    # literal character. This is the behaviour that has to survive.
    (True, "    pytest -q; echo done", True),
    # The live case that found the gap. This seat's own prose, inside a Python
    # docstring, joining two finished sentences with a semicolon.
    (False, "    the page and the grade reads it; three in a paragraph is the",
     False),
    # A quoted specimen inside a docstring stays excused, because striking the
    # mark would falsify the quote. That reading is not the indent's.
    (True, '    the row reads "a; b" and the grade quotes it whole', False),
    # A shell line in a docstring, which says so with its own prompt.
    (True, "    $ psql -c 'select 1;'", False),
    # A quotation of somebody else's prose, marked as one.
    (True, "> the rule is stated; nothing enforces it", True),
)


def quoting_cases():
    """Every case above, run before a diff is read."""
    return [(want, line, code) for want, line, code in QUOTING_CASES
            if quoting(line, code) is not want]


def quoting(text, indent_is_code=True):
    """Is the mark inside something quoted, or inside a command?

    The two exceptions are the whole difficulty and both were settled in prose
    by the grades of 2026-10-10 and 2026-10-12. A semicolon inside a quotation
    of the artifact or of a surface's output cannot be struck without
    falsifying the quote, and a semicolon inside a shell line is the literal
    character. Everything else is a finding.

    `indent_is_code` is the third exception and it was wrong by default until
    2026-11-08. In Markdown a four-space indent is a fenceless code block, so
    excusing the line wholesale is right. In Python it is scope, so every line
    of every docstring and every indented comment in this file was excused for
    as long as the check has existed. Measured on the day the parameter was
    added: 2,670 indented prose lines in `check_voice.py`, 14 of them carrying
    a canon law 1 mark this reading could not see, 10 of those plainly this
    seat's own prose joining two finished sentences. The gate that reads this
    seat's added lines for law 1 was blind to the surface this seat writes
    most of its prose on, and the line that found it was added by this run.

    The caller decides, and `selfcheck` passes `False` only for `.py` files
    under `docs/voice/`, which is this seat's own surface. The same reading
    applies to `tools/*.py` and that is a filing for the engineer rather than
    a red this seat drops on another lane (incident 23's class).
    """
    stripped = text.lstrip()
    if indent_is_code and text.startswith(("    ", "\t")):
        return True
    if stripped.startswith((">", "$", "#!")):
        return True
    if stripped.startswith("|") and stripped.endswith("|"):
        return True
    # The tail of a quotation that opened on an earlier line: one quote mark,
    # at the end, with the mark before it. Every register in docs/voice wraps
    # its prose, so a quoted specimen longer than a line is the normal case
    # and the first run of this check reported one as a finding.
    if stripped.count('"') == 1 and stripped.endswith('"'):
        return True
    for span in re.findall(r'"[^"]*"|`[^`]*`|\([^)]*\)', text):
        if ";" in span or EM in span:
            return True
    return False


#: What the wrapped-span reading has to get right, as data rather than as a
#: paragraph, in the shape HEADLESS_CASES and STANDS_ALONE_CASES already use.
#: The true cases are real lines off this seat's own branches on 2026-10-26,
#: where seven register keys quoted the way `routed` demands were reported as
#: canon law 1 violations. The false cases are the shapes that look like them
#: and are not: an em dash in plain prose, and an em dash sitting outside a
#: span that opened or closed on the same line. A reading that excused those
#: would make this gate quiet rather than correct.
#: Fields: (want, the line, whether a span was open when the line began, mark)
SELFCHECK_CASES = (
    (True, "named rather than re-described: `2026-10-24 " + EM
           + " The deepening needs a third", False, EM),
    (True, "above the fold every day since` and `2026-10-03 " + EM
           + " Canon law 12's own wording,", True, EM),
    (True, "the date separator " + EM + " and the key` is what `routed` reads",
     True, EM),
    (False, "The seat was named " + EM
            + " and then forbidden by its own charter.", False, EM),
    (False, "`docs/ideas.md` holds the list " + EM + " and nothing reads it.",
     False, EM),
    (False, "the key` was quoted " + EM + " and then struck.", True, EM),
    (False, "The rule is stated; nothing enforces it.", False, ";"),
    (True, "the gate prints `abs/2604.24594; no html` and moves on", False, ";"),
)


def selfcheck_cases():
    """Every case above, run before a diff is read.

    A reading that fails its own cases either excuses a violation or reports a
    register key, and the second of those is what sent seven true lines to a
    review as findings.
    """
    bad = []
    for want, line, start, mark in SELFCHECK_CASES:
        got = mark in inline_quoted(line, start)[0]
        if got != want:
            bad.append((want, line, start))
    return bad


def selfcheck(ref=None):
    """Canon law 1 over the run's own added lines, which was the last
    measurement this seat took by reading.

    The ledger entry of 2026-10-12 and
    `INC-2026-10-12-the-editors-own-prose-broke-canon-law-one-a-fifth-time`:
    a review reported no semicolon join in any added line, and the per-file
    command then found eleven semicolons, eight of them violations, one inside
    the sentence asserting the check. Five occurrences of this class share one
    diagnosis, which is where the mark hides, and a count does not care.
    An em dash is allowed on a heading line, because every entry in
    docs/agents/incidents.md and docs/ideas.md carries one as its own date
    separator. Nowhere else.
    """
    ref = ref or "origin/main"
    wrong = quoting_cases()
    for want, line, code in wrong:
        print(f"  CASE    wanted excused={want}: {line.strip()[:60]}")
    if wrong:
        print("QUOTING_CASES says which marks this reading excuses, and the")
        print("reading changed. Nothing below was read.")
        return 1
    bad = selfcheck_cases()
    if bad:
        for want, line, start in bad:
            print(f"  CASE    wanted {want}: {line.strip()[:62]}")
        print("The wrapped-span reading changed and SELFCHECK_CASES says how.")
        print("Nothing below was read.")
        return 1
    hits, counts, fences, states = [], collections.Counter(), {}, {}
    try:
        lines = list(added_lines(ref))
    except BadRef as dead:
        print(f"added lines read from   {ref}")
        print(f"  FAIL    {dead}")
        print()
        print("Nothing was measured, so nothing is clean. This used to print a")
        print("clean pass and return 0, which is ban list 144.")
        return 1
    for path, n, text in lines:
        for mark, name in ((";", "semicolon"), (EM, "em dash")):
            if mark not in text:
                continue
            counts[(path, name)] += text.count(mark)
            if path not in fences:
                fences[path] = fenced(path)
                states[path] = code_state(path)
            # Indentation means a code block in Markdown and scope in
            # Python, so the excuse is the caller's to grant. Scoped to this
            # seat's own surface: see `quoting`.
            own_python = path.startswith("docs/voice/") and path.endswith(".py")
            if n in fences[path] or quoting(text, not own_python):
                continue
            if mark == EM and text.lstrip().startswith("#"):
                continue
            # The span that opens on one line and closes on the next. Every
            # entry in docs/ideas.md and docs/agents/incidents.md carries an
            # em dash as its own date separator, and `routed` requires a
            # finding to NAME an entry rather than re-describe it, so obeying
            # one gate tripped this one on seven lines of one branch.
            if mark in inline_quoted(text, states[path].get(n, False))[0]:
                continue
            hits.append((path, n, name, text.strip()))
    print(f"added lines read from   {ref}")
    for (path, name), k in sorted(counts.items()):
        print(f"  {path:<40} {name} {k}")
    if not counts:
        print("  no semicolon and no em dash in any added line")
    for path, n, name, text in hits:
        print(f"  FINDING {path}:{n}  {name}")
        print(f"    {text[:96]}")
    print()
    print(f"{len(hits)} line(s) carry a mark this file cannot excuse. A quotation and a")
    print("shell line are excused in code. Everything else is canon law 1 until the")
    print("run strikes it or the review says in one line why it stands.")
    return 1 if hits else 0


def plain_md(line):
    """Markdown stripped the way the renderer strips it, for comparison only."""
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    return re.sub(r"[*_`]", "", line)


CLAIMS = ROOT / "docs/agents/quality-claims.md"

# What this check can see, which is the half of a gate L-A21 says to state
# rather than assume. The register names one file per row, and the defect it
# missed was a claim COPIED to a page the row does not name, so the search
# space is every reader-facing surface rather than the cited one.
#
# Two modules of the pipeline are on the list and the rest are not. The
# masthead and the email chrome are sentences a reader reads, fixed in code
# and graded by nothing, which is ban list 61 and the reason law 15 went
# unnoticed for the life of the product. The other modules' strings are
# preflight messages and log lines, and the first draft of this list took
# pipeline/*.py and reported four of distill's error strings as reader-facing
# copy. A gate that cries about a log line teaches the seat reading it to
# skim.
SURFACE_GLOBS = ("site/app/**/*.jsx", "site/app/**/*.js", "site/lib/*.js",
                 "site/emails/*.html", "pipeline/weekly.py",
                 "pipeline/email_render.py")

# The archive, which `reading` adds to the list above and no other check does.
# `pipeline/weekly.py` is the string that will print on the NEXT issue. The
# committed issue is the string printing on a published one right now, and
# `site/lib/issues-core.js` says which of the two a reader gets: "the record
# decides which weeks exist, the committed file decides the text of any week
# that has one." So a masthead repaired in the module is repaired for every
# week the press has not written yet, and for no week it already did.
#
# Only `reading` takes these. `claims` reads the same globs and must not: an
# issue body's sentences are claims about the research rather than about our
# artifact, which is the one distinction the writer charter's claims gate turns
# on, and pointing a gate that FAILS on unhedged claims at eighteen hundred
# lines of research prose would redden the tree over work nobody can fix.
# Whether the register's net belongs over the archive is the ExO seat's call on
# its own file, and the ledger entry filed with this change asks it rather than
# answering it here.
ARCHIVE_GLOBS = ("site/content/issues/*.md",)

# The target every line of copy converges on, which is not a surface and is
# read here anyway. `claims` was pointed at the pages that already shipped, so
# the one gate the writer charter hands this seat for its step-1b duty could
# not see a candidate before it left the seat's hands, and it could not see
# `docs/voice/value.md` at all. That page is where a candidate is told what to
# say, so a promise with no machine under it lands there one step before it
# lands on a page, and every candidate written against it inherits the promise
# while this check stays green on the surfaces. L-A21's first half, with the
# scope narrower than the subject: name a change that would break what this
# gate governs, then ask whether the gate would have SEEN it.
#
# One file and not the whole directory, deliberately. The other candidate
# files under docs/voice/ quote the specimens she rejected and the law that
# rejects them, which is the construction L-A23 names, and a per-sentence
# hedge test cannot tell a candidate from the rejection printed beside it to
# warn against it. Reading them needs a convention that marks which lines are
# the candidate, that convention does not exist, and inventing one here would
# redden ten existing files over prose nobody can fix. Filed in docs/ideas.md
# with the proposal rather than guessed at. Until then `claims` takes a path,
# so a round can aim it at the file it is drafting.
TARGET_GLOBS = ("docs/voice/value.md",)

# Words that carry no claim. Overlap is scored on the rest, because the claim
# in the register and the claim on the page are rarely the same string: the
# register holds "revised when the research sharpens it" and /llms.txt prints
# "revised when its research sharpens", which an exact match reads as absent.
CLAIM_STOP = set("""a about an and any are as at be been being but by can could
does do each every for from had has have in into is it its of on only or our
same so than that the their them then there these they this to up was what when
where which who will with without you your""".split())

# The hedge, taken from site/app/routines/page.jsx, which is the form the
# register itself names as acceptable: the absence said out loud. "Still being
# built. We will write to you the day they ship."
#
# The word "will" is not on this list, and the first draft of this check had it
# there, which read the skills page's "agents that work from the current state
# of the evidence today and still will next month" as hedged. That sentence is
# a guarantee about next month for a mechanism the register calls `not built`,
# so it is the furthest thing from a hedge. A hedge says the thing does not
# exist yet. A promise says it will, and only one of the two is honest while
# the mechanism column is empty.
HEDGE = re.compile(r"\b(not built|not yet|yet to|never been|has never|"
                   r"have never|none of them|still being built|not shipped|"
                   r"when (?:they|it) ship|day (?:they|it) ship|planned|"
                   r"not live|so far|no skill has|intend to|aim to)\b")

STATES = ("held", "unproven", "contradicted", "not built", "queued")

# The register writes its verdict as the FIRST bolded span of the state cell
# and then keeps writing: the transition that produced it, the date, and the
# reading behind it. Every one of those is prose about the row's history, and
# one of the words it uses is `held`, because a row that moved says what it
# moved from. So a resolver that searches the whole cell finds two verdicts on
# such a row, and the one it picks decides whether a sentence may ship.
STATE_CASES = (
    ("contradicted", "**contradicted**"),
    ("queued", "**queued**"),
    ("not built", "**not built**"),
    ("held", "**held**"),
    ("contradicted", '**contradicted on "every"**'),
    ("contradicted", "**contradicted on the universal reading**"),
    ("contradicted", "**contradicted on the verb, and dark on the live site**"),
    # The live row, 2026-10-24 onward, and the case this resolver was written
    # for. A whole-cell search reads `held` here and the home page's "The
    # library grows every day" reports ok while the corpus has not grown.
    ("contradicted",
     "**contradicted**, moved from `held` 2026-10-11, and the mechanism is a "
     "**stopped job rather than a widening gap**"),
    # The mirror, which is the one that would be dangerous the other way: a row
    # genuinely held whose cell recounts the contradiction it came out of.
    ("held", "**held** since 2026-10-20, after the `contradicted` reading of "
             "2026-10-11 was repaired"),
    # No state word at all. The verdict is the register's own phrase, it is not
    # `held`, and the row ships hedged or not at all.
    ("**reports, does not replace**", "**reports, does not replace**"),
    # Substrings, because `held` hides inside two ordinary English words and a
    # row that withholds a verdict is not a row that holds one.
    ("contradicted", "**contradicted**, the earlier verdict upheld"),
    ("not built", "**not built**, the receipt withheld"),
    # Unbolded, which no row uses today. The whole cell is the verdict then,
    # and the ambiguity rule below still governs it.
    ("queued", "queued"),
    # The two live cadence rows as of 2026-11-02, both split by half, pinned
    # because the resolver was already right about them and nothing said so.
    # The ExO seat's sweep of that day made "a cadence claim carries two
    # verdicts" step six of its claim sweep, so split cells stop being the
    # exception here. The strictest half still governs whether a line may
    # ship, which for both of these is `contradicted`.
    ("contradicted",
     "**held on the clock, contradicted on the record**, moved from a flat "
     "`contradicted` 2026-11-02, and the mechanism is a **job running and "
     "falling behind** rather than the stopped job of the last reading"),
    ("contradicted",
     "**contradicted on the record and on the clock**, moved from "
     '"contradicted on the record, cadence resumed" 2026-11-02'),
    # The dangerous direction, which no row writes today and one will: a row
    # whose record half is the one that holds. `held` must still lose.
    ("contradicted",
     "**contradicted on the clock, held on the record**"),
)

# Which half of a cadence claim each verdict belongs to. `claim_state` answers
# whether a line may ship and this answers what hedge it needs, which are two
# questions one word cannot carry: a row false about the current period is
# softened by naming the gap, and a row false about the whole series is only
# honest if the claim stops being universal.
HALF_NAMES = ("clock", "record")
HALF_CASES = (
    ("**held on the clock, contradicted on the record**",
     {"clock": "held", "record": "contradicted"}),
    # One verdict, two halves, and the second half names no state of its own.
    ("**contradicted on the record and on the clock**",
     {"clock": "contradicted", "record": "contradicted"}),
    ("**contradicted**", {}),
    # A half-shaped phrase that is not a half. "on the verb" and "on the live
    # site" are the register's own words for other things entirely.
    ("**contradicted on the verb, and dark on the live site**", {}),
    ("**contradicted on the universal reading**", {}),
    # The history recount, which is the case `claim_state` was written for.
    # It names no half, so this returns nothing and the AMBIGUOUS line below
    # stays the right message for it.
    ("**contradicted**, moved from `held` 2026-10-11", {}),
)


def claim_halves(cell):
    """The per-half verdicts a cadence row names, as `{half: state}`.

    Empty for every row that does not split, which is most of them, so the
    caller prints the split only where the register wrote one.
    """
    bold = re.search(r"\*\*(.+?)\*\*", cell)
    scope = (bold.group(1) if bold else cell).lower()
    out, carry = {}, None
    for part in re.split(r",| and ", scope):
        state = next((s for s in STATES
                      if re.search(r"\b" + re.escape(s) + r"\b", part)), None)
        half = re.search(r"\bon the (clock|record)\b", part)
        if state:
            carry = state
        if half:
            out.setdefault(half.group(1), state or carry)
    return out


def claim_state(cell):
    """One row's verdict, and `held` never wins a tie.

    Returns `(state, ambiguous)`. The scope is the first bolded span, because
    that is where the register writes the verdict and everything after it is
    the row's history. Where two verdicts still survive inside that span, the
    strictest reading is taken and the caller reports it, because the
    permissive reading is the one that lets a false sentence ship and a gate
    that guesses in the shipping direction is worse than no gate.
    """
    bold = re.search(r"\*\*(.+?)\*\*", cell)
    scope = (bold.group(1) if bold else cell).lower()
    hits = [s for s in STATES
            if re.search(r"\b" + re.escape(s) + r"\b", scope)]
    if not hits:
        return cell, False
    if len(hits) == 1:
        return hits[0], False
    strict = [s for s in hits if s != "held"]
    return strict[0], True


def state_cases():
    """Every case above, run before the register is read."""
    bad = [(want, cell) for want, cell in STATE_CASES
           if claim_state(cell)[0] != want]
    return bad + [(str(want), cell) for cell, want in HALF_CASES
                  if claim_halves(cell) != want]


def claim_words(phrase):
    """The content words of a claim, lightly stemmed, as a set."""
    words = re.findall(r"[a-z]+", phrase.lower())
    out = set()
    for w in words:
        if w in CLAIM_STOP or len(w) < 3:
            continue
        out.add(re.sub(r"(ies|es|ed|ing|s)$", "", w) if len(w) > 4 else w)
    return out


def claim_rows():
    """The register's table as rows: phrases, surfaces, state, measured."""
    rows = []
    for line in CLAIMS.read_text().split("\n"):
        if not line.startswith("|") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Claim":
            continue
        phrases = re.findall(r'"([^"]+)"', cells[0])
        if not phrases:
            continue
        where = [(p.split(":")[0], int(p.split(":")[1]) if ":" in p else 0)
                 for p in re.findall(r"`([^`]+)`", cells[1])]
        state, ambiguous = claim_state(cells[3])
        rows.append({"phrases": phrases, "where": where, "state": state,
                     "ambiguous": ambiguous, "cell": cells[3],
                     "halves": claim_halves(cells[3]),
                     "label": phrases[0], "measured": cells[4] if len(cells) > 4 else ""})
    return rows


def uncommented(path, lines):
    """The file's lines with its own commentary gone.

    A seat's commentary quotes the claim it is fixing, which is what this check
    hunts, so leaving it in makes the module that documents a defect read as a
    surface committing it. `pipeline/skill_revision.py` opens by quoting the
    site sentence it exists to make true, and the first run of this check
    reported that docstring as a live unhedged claim. The rule that follows is
    narrow and it holds: a reader never sees a comment, so a comment is not a
    surface.

    Python keeps its single-quoted constants, because that is where the
    masthead lives (`pipeline/weekly.py`, ban list 61) and a sentence fixed in
    code prints on every issue. It loses its triple-quoted blocks, which are
    docstrings in every file this reads.
    """
    out, in_doc = [], False
    for line in lines:
        if path.suffix == ".py":
            if line.count('"""') == 1:
                in_doc = not in_doc
                out.append("")
                continue
            line = "" if in_doc else re.sub(r"#.*$", "", line)
        else:
            line = re.sub(r"(?<!:)//.*$", "", line)
        out.append(line)
    return out


def surface_text(path):
    """One file's reader-facing text, with a map from offset back to line."""
    text, marks = "", []
    raw = re.sub(r"/\*.*?\*/|<!--.*?-->", " ", path.read_text(), flags=re.S)
    for n, line in enumerate(uncommented(path, raw.split("\n")), 1):
        marks.append((len(text), n))
        text += re.sub(r"<[^>]*>", " ", line).strip() + " "
    return text, marks


def line_of(marks, offset):
    return max(n for off, n in marks if off <= offset)


def surface_sentences(path):
    """Reader-facing sentences of one file, each with the line it starts on."""
    text, marks = surface_text(path)
    out = []
    for m in re.finditer(r"[^.!?]+[.!?]", text):
        body = norm(m.group())
        if len(body) > 24:
            out.append((line_of(marks, m.start()), body))
    return out


def claims(paths=()):
    """Every registered quality claim against the surface that prints it.

    docs/agents/quality-claims.md says a claim with no mechanism ships hedged
    or does not ship. Three charters enforce that by telling a seat to read the
    file, and on 2026-10-18 two rows recorded as `queued` and `not built` on
    2026-09-30 were live on /llms.txt in the flat present tense, eighteen days
    later, with the register's own cells accurate the whole time
    (INC-2026-10-18-registered-claims-ship-unhedged-because-no-gate-reads-the-register).
    L-A22: the gate goes in the command.

    It fails three ways.

    - UNHEDGED, a claim whose state is not `held` printed in the present tense.
      That is the defect above and it is the writer's to fix, by drafting the
      hedge, or the register's rule to refuse the line.
    - UNNAMED, a claim that is not `held` on a surface the row does not cite.
      The revision claim reached three pages by being copied, and a measurement
      attached to one file does not follow the sentence to the next one.
    - EMPTY, no rows parsed or no surfaces read, because a check that examined
      nothing and a check that found nothing look identical from outside.

    GONE and MOVED print and do not fail, and the reason is whose work they
    are. A cited file that no longer says anything like its claim, and a cited
    line number that has drifted, are both the register's accuracy rather than
    the artifact's honesty, and the register belongs to the ExO seat while this
    command runs in the writer's. A gate that turns red on a file its own seat
    must not edit gets ignored, which is the failure mode after the failure
    mode this check exists for. They are counted separately and reported.

    GONE also fires on a row whose claim is rendered as an element rather than
    written as a sentence. `SkillLibrary.jsx` prints "Trigger test" over a
    date, and the register's row for it is a fair description of what a reader
    sees and not a string that is anywhere in the file. That is the clearest
    case for printing it and not failing on it.

    What it cannot see, which is the other half of L-A21. It finds a claim the
    register already knows. A sentence making a NEW quality claim that no row
    covers scores no overlap and passes here, and that is the finding the
    charter hands to a reading rather than to a command, because deciding
    whether a sentence is a claim about our artifact is the judgment this check
    does not have.
    """
    bad = state_cases()
    if bad:
        for want, cell in bad:
            print(f"  CASE    wanted {want}: {cell[:62]}")
        print("The register's verdict convention changed and STATE_CASES says")
        print("how. Nothing below was read.")
        return 1
    print(f"  the verdict cases                         "
          f"{len(STATE_CASES)} state, {len(HALF_CASES)} half, all pass")
    rows, fails = claim_rows(), []
    hedged, moved, spread, gone = [], [], [], []
    surfaces = []
    if paths:
        surfaces = [pathlib.Path(x) if pathlib.Path(x).is_absolute()
                    else ROOT / x for x in paths]
    else:
        for glob in SURFACE_GLOBS + TARGET_GLOBS:
            surfaces += sorted(ROOT.glob(glob))
    scanned = [(p, surface_sentences(p)) for p in surfaces if p.is_file()]
    print(f"rows in docs/agents/quality-claims.md       {len(rows)}")
    print(f"  not `held`, so hedged or not shipped      "
          f"{sum(1 for r in rows if r['state'] != 'held')}")
    # L-A47: an instrument's scope is part of its answer. A run that aims this
    # at one candidate and a run that swept every surface print the same
    # verdict otherwise, and only one of them has checked the product.
    print(f"scope                                       "
          f"{'aimed at ' + ', '.join(shown_path(p) for p, _ in scanned) if paths else 'the shipped surfaces and the target'}")
    print(f"reader-facing surfaces read                 {len(scanned)}")
    print(f"  sentences in them                         "
          f"{sum(len(s) for _, s in scanned)}")
    print()
    if not rows or not scanned:
        print("  FAIL    this check examined nothing, which is not a pass")
        return 1

    for row in rows:
        words = [claim_words(p) for p in row["phrases"]]
        cited = {p for p, _ in row["where"]}
        hits = []
        for path, sentences in scanned:
            # `shown_path` and never `relative_to(ROOT)`. Its own docstring
            # says the idiom is inlined in six passes, and this was the
            # seventh: the line raised the moment `claims` was first aimed at
            # a candidate dumped into /tmp, which is how a round proves the
            # gate catches the page it is replacing. Same defect as
            # `standalone` on 2026-11-01, one day later, in the pass that
            # reports the FINDING rather than the scope.
            rel = shown_path(path)
            for line, body in sentences:
                have = claim_words(body)
                score = max((len(w & have) / len(w)) if w else 0 for w in words)
                if score >= 0.6 and max(len(w & have) for w in words) >= 3:
                    hits.append((rel, line, body, score))
        print(f"{row['state']:>13}  \"{row['label'][:58]}\"")
        if row["halves"]:
            # A split cell is not an ambiguous one. The register wrote two
            # verdicts on purpose, one per half of a cadence claim, and
            # reporting that as an ambiguity teaches the reader to skim the
            # line. The shipping decision is unchanged and the strictest half
            # still governs it; what this adds is which hedge the half needs.
            print(f"  SPLIT     "
                  + "   ".join(f"{h}: {row['halves'][h]}"
                               for h in HALF_NAMES if h in row["halves"]))
            failed = [h for h in HALF_NAMES
                      if row["halves"].get(h) not in (None, "held")]
            print(f"            the {' and '.join(failed)} "
                  f"{'half fails' if len(failed) == 1 else 'halves fail'}, "
                  f"so the hedge owed is "
                  + ("the gap named" if failed == ["clock"]
                     else "the universal dropped" if failed == ["record"]
                     else "both, which is the claim withdrawn"))
        elif row["ambiguous"]:
            print(f"  AMBIGUOUS the state cell names more than one verdict; "
                  f"the strictest is read")
            print(f"            {row['cell'][:96]}")
        for rel, line, body, score in hits:
            tag = "ok      "
            if row["state"] != "held" and not HEDGE.search(body):
                tag, _ = "UNHEDGED", fails.append((row, rel, line, body))
            elif row["state"] != "held":
                hedged.append((row, rel, line))
            if rel not in cited:
                if row["state"] == "held":
                    spread.append((row, rel, line))
                    tag = "SPREAD  " if tag == "ok      " else tag
                else:
                    fails.append((row, rel, line, body))
                    tag = "UNNAMED " if tag == "ok      " else tag + "+UNNAMED"
            print(f"  {tag}  {rel}:{line}  ({score:.0%} of the claim's words)")
            print(f"            {body[:96]}")
        for path, want in row["where"]:
            f = ROOT / path
            if not f.exists():
                continue
            there = [h for h in hits if h[0] == path]
            if not there:
                print(f"  GONE      {path} is cited and says nothing like it")
                gone.append((row, path))
            elif want and all(abs(h[1] - want) > 4 for h in there):
                print(f"  MOVED     {path} cites line {want}, found at "
                      f"{', '.join(str(h[1]) for h in there)}")
                moved.append((row, path))
        if not hits:
            print("  not printed on any surface this check can see")
        print()

    # The count has two inputs and a review quotes one number, so the number
    # carries both. On 2026-10-25 this figure read 23 against 17 two days
    # earlier and the grade that quoted it could not say which input had
    # moved. It was the register: 11 rows to 13, with the surfaces unchanged.
    # A delta on a figure whose scope is not beside it is not a reading.
    print(f"FAIL, unhedged or unnamed, live right now   {len(fails)}"
          f"   (over {len(rows)} register rows and {len(scanned)} surfaces)")
    print(f"claims not held and properly hedged         {len(hedged)}")
    print(f"held claims on an uncited surface           {len(spread)}")
    print(f"for the register's owner, not a failure here")
    print(f"  cited files that no longer say it         {len(gone)}")
    print(f"  cited line numbers that have drifted      {len(moved)}")
    print()
    print("A claim that is not `held` ships hedged the way routines/page.jsx")
    print("hedges a routine that does not exist yet, or it does not ship. The")
    print("repair is to drop the claim rather than to soften it where softening")
    print("leaves a false sentence standing, which is canon law 15.")
    return 1 if fails else 0


# Canon law 15's own vocabulary, which is the half of the law that makes it
# checkable. Papers come in, arrive or land. They are sorted or ranked. They
# are read in full or read closely, and that is the only act the word "read"
# may name. A reader or an agent may read anything, because the law is about
# what the library claims to have done, not about the verb.
READING = re.compile(
    r"papers? read\b(?! in full| closely)"
    r"|\bread\b(?! in full| closely)\s+[\d,{][^ ]*\s+papers?\b"
    r"|\b(?:library|alexandria|corpus)\b[^.]{0,60}\breads?\b"
    r"[^.]{0,40}\b(?:research|papers?|literature|abstracts?)\b"
    # The subject is a pronoun, which is how three sentences of
    # site/app/llms.txt/route.js escaped this on 2026-10-18. The clause
    # above needs the library named inside the same sentence, and a
    # paragraph that names it once then says "It reads the week's AI
    # research" is the same false claim with the subject moved out of
    # reach. Her 2026-09-20 ruling rejects "it" as the subject of a
    # mechanism sentence anyway, so the form is wrong twice over.
    r"|\bit reads\b[^.]{0,40}"
    r"\b(?:research|papers?|literature|abstracts?)\b"
    # "read in full" is exempted above, and it has to be: it is the one act
    # the law permits the word to name, and "164 papers read in full" is both
    # true and the sentence the law asks for. The exemption is wrong for
    # exactly one form, and that form is the string canon law 15 quotes as its
    # own evidence: 'read in full and distilled weekly'. Attached to a count it
    # is a fact. Attached to a cadence it is a claim about everything that
    # arrives in a week, which is the ingest number wearing the read number's
    # verb, and it is the defect the law was written for.
    # This is the hole the first draft of this check wrote down and left open:
    # "a sentence that says read in full over a number that came from the
    # ingest field passes here". Narrowed to the cadence form, it closes
    # without touching the true sentence. Added 2026-10-23.
    r"|\bread in full\b[^.]{0,40}\b(?:weekly|every week|each week|a week)\b",
    re.I)


# `shown_path` was defined here and again 1,946 lines below, and the lower
# definition is the one every caller in this file has ever reached, because
# Python binds the last one. So this copy was dead for as long as both have
# existed. It was also the worse of the two: it took `path.resolve()` without
# coercing, so a string argument raised `AttributeError`, and it returned the
# path as handed rather than resolved when the artifact sat outside the
# checkout, which is every artifact `--live` fetches. Its docstring, quoted in
# full at the live definition, is the one that argues for the helper.
# Deleted rather than merged: the two bodies agree on every input a caller has
# ever passed, so nothing moves. `doubles` is the gate that would have found
# it, and it did not exist either.


def reading_domain(paths):
    """Law 15's two halves, because only one of them a caller may replace.

    `--live` replaces the archive glob with the editions the product serves,
    and for every other path-taking gate that is exactly right: the question
    is what a reader opens rather than what somebody committed. `reading` is
    the only gate in `TAKES_PATHS` whose default domain is site CODE and not
    the issue archive, so for this one gate replacement silently drops the
    half the law names first.

    Measured on 2026-11-02, both ways, on this branch:

        reading          63 surfaces, 4 FAIL, exit 1
        reading --live    3 surfaces, 0 FAIL, exit 0

    The four it stopped seeing are `site/app/page.jsx`, `site/app/terms`
    and two in `site/app/llms.txt`, and `taste` inherits this verdict for her
    2026-09-29 verdict 6, so the green reported a ruling as held while the
    line that breaks it was live on the home page. `editions` prints "`--live`
    on the passes that take paths is the way to answer it inside one run", so
    a run following this file's own advice got the green.

    The law's own words are the reason the split is not arbitrary: it binds
    "the masthead, the email, the site and any line of copy drafted under the
    canon". A served edition is not a substitute for `site/app/page.jsx`, so
    the code half is unconditional and the archive half is what a caller may
    point somewhere else.
    """
    code = []
    for glob in SURFACE_GLOBS:
        code += sorted(ROOT.glob(glob))
    if paths:
        archive = [p if p.is_absolute() else ROOT / p
                   for p in (pathlib.Path(x) for x in paths)]
    else:
        archive = []
        for glob in ARCHIVE_GLOBS:
            archive += sorted(ROOT.glob(glob))
    return code, archive


# What `reading_domain` owes, as pairs of (paths given, what must hold). The
# defect these exist for is invisible in output: a narrowed domain prints a
# smaller count next to the word "surfaces" and a clean pass under it, and
# both numbers are true of the domain it chose.
READING_DOMAIN_CASES = (
    # No paths is both halves, which is the `all` run and the only shape that
    # was ever correct.
    (None, "code and archive both globbed"),
    # The defect. A path given must ADD to the code half, never replace it,
    # because `--live` hands this three editions and the law binds the code.
    (("site/content/issues/2026-W39.md",), "code half survives a named path"),
    # `--live`'s real shape: absolute paths in a tempdir outside the repo.
    (("/tmp/nonesuch-live/2026-W42.md",), "code half survives absolute paths"),
)


def reading(paths=None):
    """Canon law 15 on every surface, which is where the law says it binds.

    "The library never claims to have read what it only ingested" was her
    ruling of 2026-09-25, and the law's last paragraph says it binds the
    masthead, the email, the site and any line of copy drafted under the canon,
    because a string fixed in code is never graded (ban list 61).

    It was graded by a reading, so on 2026-10-18 the home page's first number
    still printed the ingest count under the word read, twenty-two days after
    writer run 15 drafted the exact repair in
    docs/voice/home-metric-line-2026-09-26.md and the same morning the masthead
    carrying the same defect was fixed. The repair was written, checked against
    the registers and never set. At four days it was recorded as a related
    sighting inside INC-2026-09-30-sales-assets-stale, and this is the same
    line at twenty-two days.

    The subject matters and the regex knows it, which is why two of the three
    branches name the library. A reader may read anything and so may an agent:
    "Your agents can read this catalogue on their own" is a line she approved
    on 2026-09-20, and the first draft of this check failed it along with "You
    do not schedule the update or read the paper". The law is about what the
    library claims to have done.

    It reads the whole text rather than its sentences, because the defect it
    was written for is not a sentence. "papers read this week" sits in a JSX
    fragment under a count, with no full stop anywhere near it, and a check
    that only looks at sentences cannot see the one line this check exists to
    catch.

    It reads the archive as well as the code, added 2026-10-23, and the first
    firing found the law's own evidence still in print. Canon law 15 cites one
    string: 'The masthead said "read in full and distilled weekly" on every
    issue ever sent.' `pipeline/weekly.py` was repaired. The third line of
    `site/content/issues/2026-W39.md` still says it, and that file is the live
    public text of the one week the archive publishes. Twenty-eight days, on a
    page anybody can open, under a law that quotes the sentence.

    What it cannot see. The verb is checkable and the count behind it is not:
    "papers read this week" is caught by the word, while a sentence that says
    read in full over a number that came from the ingest field passes here and
    is a worse version of the same lie. The number's provenance is a reading of
    site/lib/metrics.js and it belongs to the grade.
    """
    code, archive = reading_domain(paths)
    targets = code + archive
    hits = []
    for path in [t for t in targets if t.is_file()]:
        text, marks = surface_text(path)
        for m in READING.finditer(text):
            around = norm(text[max(0, m.start() - 40):m.start() + 72])
            hits.append((shown_path(path),
                         line_of(marks, m.start()), m.group(), around))
    print(f"surfaces read                               "
          f"{len([t for t in targets if t.is_file()])}")
    print(f"  of those, code the law binds unconditionally  "
          f"{len([t for t in code if t.is_file()])}")
    print(f"  of those, the archive this run was pointed at "
          f"{len([t for t in archive if t.is_file()])}")
    print(f"lines giving the arriving count a verb of reading   {len(hits)}")
    for rel, line, phrase, body in hits:
        print(f'  FAIL    {rel}:{line}  "{phrase.strip()}"')
        print(f"            {body[:96]}")
    if not targets:
        print("  FAIL    this check examined nothing, which is not a pass")
        return 1
    if not hits:
        print("  every surface uses the verb the law allows")
    print()
    print("The repair is to drop the claim, never to soften it. Read or")
    print("reviewed, read at some depth, surveyed and processed are hedges on a")
    print("false sentence and the law names each one as ban list 50 in a coat.")
    return 1 if hits else 0


# Her rulings, each mapped to the text that enforces it. The key is the
# ruling's own words, copied verbatim out of docs/voice/taste.md, which is
# what lets this map exist at all: the writer seat is forbidden to edit her
# register, so the anchor convention the ban list uses (a LANDED line inside
# the entry) is not available here. The quote has to live on this side and
# reach across.
#
# That inversion is the whole design. In `sweep` the register holds the
# numbers and the map answers for them. Here the register holds prose nobody
# else may touch, so the map quotes it and the check asks whether the quote
# still resolves. A ruling she rewords breaks its own row, which is correct:
# a reworded ruling is a ruling to re-read.
class Check:
    """An enforcement that is a command in this file rather than a line in a

    file. A ruling with one of these is green only when that command is green,
    so the taste gate inherits the verdict instead of reporting a quote that
    resolves while the rule it anchors is being broken on a live page.

    This exists because the first green run of `taste` was a false one. Her
    ruling of 2026-09-29 carries six numbered verdicts. Two of them were
    anchored to approved headings on the site, both quotes resolved, and the
    sixth verdict, never "read" for ingested, was being violated on three
    reader-facing surfaces at that moment. A quote proves a rule is present
    and says nothing about the artifact.
    """

    def __init__(self, name):
        self.name = name

    exists = staticmethod(lambda: True)

    @property
    def stem(self):
        return self.name


TASTE_MAP = {
    '"stale and mechanical and boring"': [
        (CANON, "Study decisions, never copy sentences"),
    ],
    '"Traction matters a lot." Relevance is impact of': [
        (DIGEST, "Traction leads, because relevance is impact and not release date"),
    ],
    'Fresh items with no traction are listed honestly as': [
        (DIGEST, "Fresh work is labeled honestly as unproven here"),
    ],
    "The headline is a finding a builder can act on, not a greeting.": [
        (DIGEST, "The title states a FINDING, never a topic, a direction, or a greeting"),
    ],
    "Evidence grading appears in-line per item.": [
        (DIGEST, "In-line evidence grades are house law at the top of this file"),
    ],
    "Instrument honesty notes are part of the product.": [
        (DIGEST, "Honesty still binds, but it serves items, in place, in one plain sentence"),
    ],
    '"You didn\'t show me the paper": links must reach the': [
        (DIGEST, "Links reach the full text, never the landing page"),
        (Check("links"), "the form half, on the served issues"),
    ],
    "NO meta-commentary inside the newsletter.": [
        (DIGEST, "the issue never narrates its own methodology, ranking logic, or virtues"),
    ],
    "Section headings must be newsletter craft, not": [
        (DIGEST, "The heading for the traction slot, written from the items you are about to"),
    ],
    '"A lot of things are given with 0 context. I did this': [
        (DIGEST, "Big picture first, then specifics"),
        (DIGEST, "Never make the reader climb through details to find the point"),
    ],
    "The date does NOT belong in the title.": [
        (DIGEST, "The date does NOT belong in this line"),
    ],
    "Section headers: same FRAMEWORK, never the same": [
        (DIGEST, "The slot's internal name is not repeated here and is not a candidate"),
    ],
    "Length follows the news. Issues are never fixed": [
        (DIGEST, "Length follows the news, and the news is different every day"),
        (DIGEST, "Padding a thin day and truncating a heavy one are the same failure"),
    ],
    'SECOND OCCURRENCE, her word "AGAIN": section headings': [
        (DIGEST, "it is REPLACED by your own writing, never printed. That binds the title, "
                 "all four headings"),
        (DIGEST, "the four slot names are held only in the heading gate at the end"),
    ],
    "THE OUTSIDER TEST, from her read of the first": [
        (DIGEST, "The outsider test, and it is a hard rule"),
        (DIGEST, "they do not carry the subfield's map in their head"),
    ],
    'DENSITY is the twin ruling: "avoiding density is': [
        (DIGEST, "White space between sections, and never two walls in a row"),
    ],
    "Two rejected-verbatim specimens for the outsider": [
        (DIGEST, "So every term of art carries its plain-words clause the FIRST time it"),
    ],
    "Scope widens: the voice canon governs SITE COPY too.": [
        (CANON, "this canon governs SITE COPY as well as the newsletter"),
        (CANON, "The writer seat drafts the words and the frontend seat sets them"),
    ],
    "The pilot issue: the current archived issue (2026-W37)": [
        (ROOT / "site/lib/content.js", 'HIDDEN_WEEKS = new Set(["2026-W37"])'),
    ],
    '"dont name it [alexandria] 2026-W39. give it a proper': [
        (ROOT / "pipeline/weekly.py",
         'ALARM_SUBJECT_CANNOT_PRINT = "The press could not print this week\'s issue"'),
        (DIGEST, "never the ISO week id here or anywhere else reader-facing"),
    ],
    '"dont assume readers read each issue." EVERY ISSUE STANDS ALONE.': [
        (DIGEST, "Then check that the issue stands alone. A hard gate"),
    ],
    '"so much better, but feels dense and like a hassle to read.': [
        (DIGEST, "Judge each item's weight and let its length follow"),
        (DIGEST, "a list appears because the material is parallel and never because the "
                 "page needed a list"),
    ],
    "Codes are never owner-facing.": [
        (ROOT / "tools/board.py", "prose must not carry codes or PR numbers"),
    ],
    'Graph page copy. "A graph that never forgets."': [
        (ROOT / "site/app/graph/page.jsx", '<h1 className="page-title">Claim graph</h1>'),
    ],
    'SITE COPY, the rounds that landed (owner: "good. i like': [
        (ROOT / "site/app/skills/page.jsx", "Skill library"),
        (ROOT / "site/app/library/page.jsx", "Every issue"),
        # Verdict (6) of this ruling, never "read" for ingested, has a command
        # of its own. Two bare-noun headings resolving says nothing about it.
        (Check("reading"), "verdict 6, never \"read\" for ingested"),
    ],
    'THE CLOSE. "change each of these: You read to decide. Your': [
        (DIGEST, "**Accelerate every builder and agent to frontier speed.**"),
        (ROOT / "pipeline/email_render.py",
         'CLOSE = "Accelerate every builder and agent to frontier speed."'),
    ],
    'TITLES. "two issues should never have the same title.': [
        (DIGEST, "A title the library has already used is not a title"),
    ],
}

# Rulings no file in this repository can enforce, each with the reason and the
# seat the answer belongs to. This is the `SWEEP_FILED` half of the same idea:
# a row here is a judgment that the ruling is binding and unmechanisable, not
# an exemption from reading it.
TASTE_FILED = {
    "Site copy, round one verdicts (line by line, hers)":
        "Verdicts on eight specific lines, five of them rejections. The rules "
        "they produced are law in canon.md and the ban list; the verdicts "
        "themselves are evidence and are checked by a reading.",
    "Site copy rounds two to eight, all rejected.":
        "docs/agents/copy-pipeline.md is the process fix and "
        "docs/voice/preferences/site-copy-2026-09-20.md is the record. A "
        "rejection of eight drafts cannot be checked against a file; it is "
        "read before the next draft.",
    "Daily cadence adopted so the product can be seen and":
        "A cadence decision, the engineer's surface. The daily has never run, "
        "so there is no artifact for a check to read.",
}

# Rulings a later ruling replaced. The value is the anchor of the ruling that
# replaced it, which must itself carry a row above, so a supersession cannot
# point at nothing.
TASTE_SUPERSEDED = {
    "The dual-audience close stands: \"You read to decide.":
        'THE CLOSE. "change each of these: You read to decide. Your',
}

# Her register separates the date from the ruling with an em dash, written
# here as the escape so that canon law 1 needs no exception for the one
# place in this file that has to match the mark rather than avoid it.
RULING = re.compile("^- (20\\d\\d-\\d\\d-\\d\\d) \\u2014 ", re.M)


def rulings():
    """docs/voice/taste.md's dated bullets, as (date, normalised body).

    A ruling runs from its own "- YYYY-MM-DD — " to the next one, so a bullet
    that wraps over fourteen lines is one ruling and the sub-numbered verdicts
    inside it stay with it. That is her file's shape and not a choice this
    makes: she gives one ruling that contains five verdicts and the writer
    reads it as one ruling.
    """
    text = TASTE.read_text()
    marks = list(RULING.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1), norm(text[m.start():end])))
    return out


def taste():
    """docs/voice/taste.md against the files that carry it, incident 20.

    The canon's grading procedure has read the taste register ruling by ruling
    since the day it was written, and pass 2 says "against the issue and
    against the generator". Nothing re-ran that. Her title ruling of
    2026-10-04 names this seat and prompts/digest.md in its own last sentence,
    and fourteen days and five writer runs later the generator did not carry
    it, because a taste check written as a check against the artifact in front
    of you is blind on a day the artifact is not the generator.

    This is the other gate. It fails five ways, and L-A21's rule that a gate
    seeing nothing is a failure rather than a quiet pass is why each one is
    counted out loud:

      a ruling in her register that no row here claims,
      a row whose quote of her words no longer resolves in her register,
      a row whose anchor matches more than one ruling, which makes the row's
        verdict ambiguous about which ruling it answered,
      an enforcement quote that has left the file it named,
      a supersession pointing at a ruling that has no row.

    What it cannot see is the same thing `sweep` cannot see, and it is worth
    naming rather than discovering. A quote that resolves proves the
    enforcement is present, never that it is as wide as the ruling. Her
    outsider ruling covers every term of art in the issue and the quote
    anchoring it covers the first use of one. Checking the width is a reading,
    and it belongs to the grade.
    """
    rows = {}
    for src, kind in ((TASTE_MAP, "landed"), (TASTE_FILED, "filed"),
                      (TASTE_SUPERSEDED, "superseded")):
        for anchor in src:
            rows.setdefault(anchor, kind)
    found = rulings()
    claimed, ambiguous, phantom = {}, [], []
    for anchor in rows:
        hits = [i for i, (_, body) in enumerate(found) if norm(anchor) in body]
        if not hits:
            phantom.append(anchor)
        elif len(hits) > 1:
            ambiguous.append((anchor, len(hits)))
        else:
            claimed.setdefault(hits[0], []).append(anchor)
    uncovered = [i for i in range(len(found)) if i not in claimed]

    cache, gone, red = {}, [], []
    for anchor, pairs in TASTE_MAP.items():
        for path, quote in pairs:
            if isinstance(path, Check):
                if path.name not in cache:
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        cache[path.name] = globals()[path.name]()
                if cache[path.name]:
                    red.append((anchor, path.name, quote))
                continue
            if path not in cache:
                cache[path] = norm(path.read_text()) if path.exists() else ""
            if norm(quote) not in cache[path]:
                gone.append((anchor, path, quote))
    dangling = [(a, t) for a, t in TASTE_SUPERSEDED.items() if t not in TASTE_MAP]

    print(f"rulings in docs/voice/taste.md                 {len(found)}")
    print(f"  enforced in a file, and quoted here          {len(TASTE_MAP)}")
    print(f"  no file can carry, filed with the reason     {len(TASTE_FILED)}")
    print(f"  replaced by a later ruling                   {len(TASTE_SUPERSEDED)}")
    for anchor, reason in sorted(TASTE_FILED.items()):
        print(f'  FILED   "{anchor[:46]}"')
        print(f"            {reason[:72]}")
    for i in uncovered:
        date, body = found[i]
        print(f"  FAIL    {date} in her register and in no row here")
        print(f'            "{body[14:94]}"')
    for anchor in sorted(phantom):
        print(f'  FAIL    row here and no such ruling: "{anchor[:50]}"')
    for anchor, n in sorted(ambiguous):
        print(f'  FAIL    row matches {n} rulings: "{anchor[:50]}"')
    for anchor, path, quote in gone:
        print(f'  FAIL    enforcement gone from {path.name}: "{quote[:48]}"')
    for anchor, name, quote in red:
        print(f"  FAIL    `{name}` is red, so this ruling is not held: {quote}")
        print(f'            ruling: "{anchor[:62]}"')
    for anchor, target in dangling:
        print(f'  FAIL    superseded by a ruling with no row: "{target[:44]}"')
    if not (uncovered or phantom or ambiguous or gone or dangling or red):
        print("  every ruling is claimed and every enforcement still resolves")
    print()
    print("A quote is the enforcement, never the ruling. A rule rewritten and")
    print("still enforcing the ruling keeps its row. A rule deleted takes the")
    print("ruling's enforcement with it, and that is what fails here.")
    return 1 if (uncovered or phantom or ambiguous or gone or dangling
                 or red) else 0


AWAITING = ROOT / "docs/voice/awaiting-her-word.md"
# A path inside backticks, which is how every row of the register and every
# candidate file names the surface it is about.
#
# `md` is in the list because the archive is a surface, which this run learned
# the expensive way one function over: `reading` held the module that writes
# the next issue and no issue it had already written. The same scope error was
# here, and its cost is worse rather than better. Without `md` a candidate for
# `site/content/issues/<week>.md` matches nothing in the register, so the one
# gate built to stop a surface being redrafted reports "no candidate here
# redrafts a surface already awaiting her word" about a surface it cannot see.
# That is the sentence a later run would have trusted. L-A21 of
# docs/standards/lessons.md is the standard and its test is the one that found
# this: name a change that would break what the gate governs, then ask whether
# the gate would have SEEN it.
SURFACE = re.compile(r"`(site/[A-Za-z0-9_./-]+\.(?:jsx|js|txt|md))")
CANDIDATE_FILE = re.compile(r"`([a-z0-9][A-Za-z0-9_.-]*\.md)`")

#: Where a copy CANDIDATE lives, as against a graded review or a preference
#: record. The distinction is the whole basis of the floor below and it is
#: structural rather than a guess at content: a review's job is to cite a live
#: line as evidence, so it names surfaces by the dozen and must not be asked to
#: open a row for one. A candidate's job is to replace a line, so a surface it
#: names with no row behind it is the defect.
CANDIDATE_DIRS = ("docs/voice/", "docs/voice/corrections/")


#: The registers themselves, which sit in the same directory as the candidates
#: and are not candidates. `candidates` already skips the register it reads.
#: Naming all five here is so `is_candidate` answers the question it is asked
#: rather than the narrower one its caller happens to need.
REGISTERS = ("awaiting-her-word.md", "ban-list.md", "canon.md", "taste.md",
             "value.md")


def is_candidate(path):
    """Is this added file a copy candidate rather than a review or a record?"""
    p = pathlib.PurePosixPath(path)
    return p.name not in REGISTERS and str(p.parent) + "/" in CANDIDATE_DIRS


#: The one judgement the floor rests on, pinned the way SELFCHECK_CASES pins
#: its reading. Every path here is a real file on this seat's branches. The
#: false cases matter more than the true ones: a review and a preference record
#: both live under `docs/voice/`, both quote live surfaces by path as evidence,
#: and a floor that caught them would fail every grade this seat writes.
#: Fields: (is it a candidate, the path)
FLOOR_CASES = (
    (True, "docs/voice/w42-correction-2026-10-26.md"),
    (True, "docs/voice/corrections/2026-W42-corrected.md"),
    (True, "docs/voice/shelf-names-2026-10-26.md"),
    (False, "docs/voice/reviews/2026-10-26-message-overturn-audit.md"),
    (False, "docs/voice/preferences/2026-09-19.md"),
    (False, "docs/voice/awaiting-her-word.md"),
)


def floor_cases():
    """Every case above, run before a diff is read."""
    return [(want, path) for want, path in FLOOR_CASES
            if is_candidate(path) != want]


def registered_candidates():
    """Every candidate filename `awaiting-her-word.md` names, open or closed.

    The unit of that register is the candidate and not the surface: one row
    carries one candidate file and the surface it is for. So the floor in
    `candidates` asks whether the draft is registered at all, rather than
    whether every path it mentions has a row. A candidate quotes the mechanism
    it works through and the sibling page it learned from, and neither of those
    is a line it proposes to replace. Asking for a row apiece would put rows in
    the register for surfaces nobody drafted, which is worse than the silence
    it replaces.

    Closed rows count. A row leaves the open table because she ruled or the
    frontend seat set the line, and either way the draft is no longer a thing
    nobody can find.
    """
    if not AWAITING.exists():
        return set()
    named = set()
    for line in AWAITING.read_text().split("\n"):
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue
        named |= set(CANDIDATE_FILE.findall(cells[2]))
    return named


def open_rows():
    """docs/voice/awaiting-her-word.md's open table, as {surface: candidates}.

    Only the open section. A closed row is a candidate she ruled on or the
    frontend seat set, and drafting for that surface again is ordinary work
    rather than the duplicate this looks for.
    """
    if not AWAITING.exists():
        return {}
    text = AWAITING.read_text()
    start = text.find("## Open")
    end = text.find("\n## ", start + 1)
    rows = {}
    for line in text[start:end if end > 0 else len(text)].split("\n"):
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue
        for surface in SURFACE.findall(cells[1]):
            for cand in CANDIDATE_FILE.findall(cells[2]):
                rows.setdefault(surface, set()).add(cand)
    return rows


def candidates(ref=None):
    """A candidate this run drafted for a surface already awaiting her word.

    `INC-2026-10-18-three-candidates-for-two-surfaces-in-one-day`, and then the
    same thing again four runs later. The register that answers "has this
    surface already been written for" was created on 2026-10-18 and says in its
    own second paragraph that it is the first file a writer run opens. The
    charter's shipping step names seven registers and not that one, so the
    ninth run of the day read all seven, drafted four candidates, and every one
    of the four surfaces already had an open row. All three of the earlier
    candidates were better.

    That is the shape this file keeps recording: the register was written, the
    duty was written inside it, and nothing between the duty and the artifact
    ever opened the file. So the duty becomes a command over the run's own
    diff, which is where `selfcheck` already looks.

    The escape is the register's own rule rather than a new one. A run may
    draft for a listed surface when it builds on the open candidate or says why
    it supersedes it, and naming that candidate file is how it says so. A file
    that names it passes. A file that does not has not read it.

    **And there is a floor under that, because the clash test has no opinion
    about a surface nobody has opened a row for.** Until run 58 this reported
    only the collision between two candidates, so a candidate for a surface the
    register has never held registered nothing and passed, and the pass line
    read the same as it reads for a run that did the bookkeeping right. Run 57
    is the instance: `w42-correction-2026-10-26.md` rules on the live
    `site/content/issues/2026-W42.md`, carries one line that needs her word,
    and reached `main` in #600 with no row anywhere. The regex above was
    widened on an earlier run precisely so an issue page would be visible here,
    which fixed what the gate could see and not what it would say about it.

    So a candidate file that names a live surface and that no row names back
    now fails, and the bookkeeping that clears it is one row. Two scope
    decisions are load-bearing and both were made by running the thing. The
    floor applies to candidate files only, per `is_candidate`, because a review
    cites surfaces as evidence and failing a grade for quoting the line it
    grades would make the gate unusable by the work it governs. And it asks for
    one row per candidate rather than one per surface, per
    `registered_candidates`: the first draft of this check asked per surface
    and reported three failures for the one W42 candidate, because that file
    also cites the W39 page it learned from and the module the correction
    serves through. Clearing it would have put two rows in the register for
    surfaces nobody drafted.
    """
    ref = ref or "origin/main"
    bad = floor_cases()
    if bad:
        for want, path in bad:
            print(f"  CASE    wanted {want}: {path}")
        print("The floor's scope changed and FLOOR_CASES says how. Nothing")
        print("below was read.")
        return 1
    if not resolves(ref):
        return dead_ref("candidates", ref)
    rows = open_rows()
    out = subprocess.run(["git", "diff", "--name-status", ref],
                         cwd=ROOT, capture_output=True, text=True)
    new, cited = [], []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2 or not parts[0].startswith("A"):
            continue
        path = parts[-1]
        if not (path.startswith("docs/voice/") and path.endswith(".md")
                and (ROOT / path).exists() and (ROOT / path) != AWAITING):
            continue
        # The clash test gets the floor's scope, which it should have had from
        # the start. `is_candidate` exists because "a review cites surfaces as
        # evidence and failing a grade for quoting the line it grades would
        # make the gate unusable by the work it governs", which is this
        # function's own docstring, and that reasoning is about citing a
        # surface rather than about which half of the pass does the citing.
        # Run 64 found it by being failed three times over its own grade of
        # `2026-W42`, whose law 15 verdict has to quote the four live `reading`
        # lines to say they are red. A gate that reddens the grade is a gate a
        # run learns to read past.
        (new if is_candidate(path) else cited).append(path)
    clashes = []
    unregistered = []
    registered = registered_candidates()
    for path in new:
        body = (ROOT / path).read_text()
        named = set(CANDIDATE_FILE.findall(body)) | {m for m in re.findall(
            r"([a-z0-9][A-Za-z0-9_.-]*\.md)", body)}
        surfaces = sorted(set(SURFACE.findall(body)))
        if surfaces and pathlib.Path(path).name not in registered:
            unregistered.append((path, surfaces))
        for surface in surfaces:
            held = rows.get(surface, set())
            # A surface held only by THIS candidate is not a clash, it is this
            # run doing the bookkeeping correctly: the row in the register and
            # the file it points at land in one diff, which is the normal shape
            # of a first draft for a new surface. Without this the gate accuses
            # a run of redrafting its own candidate, and the accusation names
            # the file it is being made about, which is how it was found.
            # Latent until now because `new` holds only files the diff ADDS, so
            # it needs a row and its candidate in the same pull request.
            held = held - {pathlib.Path(path).name}
            if held and not (held & named):
                clashes.append((path, surface, sorted(held)))
    print(f"candidate files this diff adds under docs/voice/   {len(new)}")
    for path in new:
        print(f"  {path}")
    # The scope this read, printed, because a count of zero candidates and a
    # count of zero added files mean different things (L-A47).
    print(f"added files it read as records rather than candidates  "
          f"{len(cited)}")
    for path in cited:
        print(f"  {path}")
    print(f"surfaces with an open row in awaiting-her-word.md  {len(rows)}")
    for path, surface, held in clashes:
        print(f"  FAIL    {path}")
        print(f"            drafts for {surface}, which is already open in "
              f"{', '.join(held)}")
    for path, surfaces in unregistered:
        print(f"  FAIL    {path}")
        print(f"            no row in awaiting-her-word.md names it, and it "
              f"names {len(surfaces)} live surface(s):")
        for surface in surfaces:
            print(f"              {surface}")
    if not clashes and not unregistered:
        print("  every candidate here either opens a row or names the one "
              "already open")
    print()
    print("A run may draft for a listed surface. It may not do so without")
    print("naming the candidate already open on it, because that is the")
    print("difference between superseding a draft and not knowing it exists.")
    print("And a candidate for a surface with no row at all opens one, because")
    print("an unregistered draft is a line nobody will ever come back to.")
    return 1 if (clashes or unregistered) else 0


# ---- deadlines --------------------------------------------------------

#: The heading of the register's second table, the questions no wording can
#: answer. A deadline only ever lands in that table: the surface rows above it
#: wait on a seat's diff and nothing about them expires, while a question waits
#: on her and the company standard puts a clock on that wait.
QUESTIONS = "## Questions awaiting her word"

#: A clock a command can read. One fixed form, minute precision, UTC, because
#: the alternative is the prose run 58 wrote, "at about 20:44 UTC on
#: 2026-10-28", which a reader understands and no check does.
DEADLINE = re.compile(r"deadline (\d{4}-\d{2}-\d{2}T\d{2}:\d{2})Z")

#: A row that says its own wait expires. The company standard's silence rule is
#: the only mechanism that does this here, and a row arguing it without naming
#: the hour is the defect this check was written for.
SILENCE = re.compile(r"silence rule|proceeds as (?:recommended|asked)", re.I)

#: A row that names the ask it was posted as. `tools/board.py` prints an id and
#: the PM's pass records it, so the eight-hex prefix is the one durable handle a
#: row can carry back to the message. A row with an ask has a clock whether or
#: not it prints the hour. A row with neither has never had one started.
ASKED = re.compile(r"\bask[a-z]*\s+`?([0-9a-f]{8})", re.I)

#: What `deadline_findings` must say, pinned against a fixed clock so a case
#: here means the same thing on every day this file is run. The rows are the
#: register's own, trimmed to the cells that carry the reading.
#:
#: **The first case was `()` and it was wrong, which cost four days.** The note
#: it carried said a question with no clock at all is the ordinary shape of this
#: table and must stay silent, "because nine of its ten rows wait on her with no
#: standard attached". That premise was false on the day it was written.
#: `docs/standards/pm.md` section 22 has been law since 2026-10-16 and it covers
#: "every other reservation a charter makes, in every company", with four
#: exceptions that are money, accounts, secrets and widening a seat's own
#: authority. None of this table's rows is one of the four. So every row here
#: has a standard attached, every row is owed an ask with a clock on it, and a
#: row carrying neither an ask nor an hour is the finding rather than the norm.
#: The gate was written on 2026-10-26, ten days after the premise expired, and
#: the row it could not see had its clock run out on 2026-10-28T06:19Z.
#: Fields: (the codes expected, the row)
DEADLINE_CASES = (
    (("unasked",), "| Does a paid tier keep a bullet for a machine that does "
     "not exist, hedged, or lose the bullet? | `claim-repairs-2026-10-18.md`, "
     "finding 8 | 2026-10-18 |"),
    (("expired",), "| Does the corrected page carry a notice? | "
     "`w42-correction-2026-10-26.md` | 2026-10-26. deadline "
     "2026-10-28T20:44Z, after which the recommendation is in force under "
     "the company standard's silence rule |"),
    ((), "| Does the corrected page carry a notice? | "
     "`w42-correction-2026-10-26.md` | 2026-10-26. deadline "
     "2026-11-30T20:44Z, after which the recommendation is in force under "
     "the company standard's silence rule |"),
    (("unreadable",), "| Does the corrected page carry a notice? | "
     "`w42-correction-2026-10-26.md` | 2026-10-26. Posted as a formal ask, "
     "and under the silence rule it proceeds as recommended at about 20:44 "
     "UTC on 2026-10-28 |"),
    # An ask with no readable hour is `unreadable` and not `unasked`: the clock
    # started when the message was posted and the row cannot say when it ends.
    # This is the shape every row should be moving towards and the one the
    # register wrote in prose for five days.
    (("unreadable",), "| Are the skill files the paid product? | "
     "`skills-copy-2026-10-18.md`, surface 3 | 2026-10-18. Posted as ask "
     "`db6d191e` under the silence rule |"),
    # An ask and an unexpired hour: nothing to say. The end state of a row.
    ((), "| Are the skill files the paid product? | "
     "`skills-copy-2026-10-18.md`, surface 3 | 2026-10-18. Posted as ask "
     "`db6d191e`, deadline 2026-11-30T06:19Z under the silence rule |"),
    # Two asks for one reservation, the live shape of 2026-11-02. Neither hour
    # has passed, so the only finding is the duplication itself.
    (("duplicated",), "| Are the skill files the paid product? | "
     "`skills-copy-2026-10-18.md`, surface 3 | 2026-10-18. Posted as ask "
     "`2cfc0df6`, deadline 2026-11-30T00:32Z, and re-posted as ask "
     "`cbdb86a5`, deadline 2026-11-30T08:28Z |"),
    # And the half that makes `duplicated` worth a code rather than a note:
    # the EARLIER clock has run out and the later one has not, so a row read
    # on its newest id looks live while the reservation is already resolved.
    (("duplicated", "expired"), "| Are the skill files the paid product? | "
     "`skills-copy-2026-10-18.md`, surface 3 | 2026-10-18. Posted as ask "
     "`2cfc0df6`, deadline 2026-10-28T00:32Z, and re-posted as ask "
     "`cbdb86a5`, deadline 2026-11-30T08:28Z |"),
    # The same id twice is one ask written in two cells, not two postings.
    ((), "| Are the skill files the paid product? | "
     "`skills-copy-2026-10-18.md`, surface 3 | 2026-10-18. Posted as ask "
     "`2cfc0df6`, deadline 2026-11-30T00:32Z, and ask `2cfc0df6` is the one "
     "the row is read against |"),
)

#: The clock `DEADLINE_CASES` is read against. 2026-10-29, the day after the
#: one live deadline, so the expired case is expired and the far one is not.
CASE_NOW = datetime.datetime(2026, 10, 29, tzinfo=datetime.timezone.utc)


def question_rows():
    """Every row of the register's questions table, as whole lines."""
    if not AWAITING.exists():
        return []
    text = AWAITING.read_text()
    start = text.find(QUESTIONS)
    if start < 0:
        return []
    end = text.find("\n## ", start + 1)
    rows = []
    for line in text[start:end if end > 0 else len(text)].split("\n"):
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4 or set(cells[1]) <= set("- ") or cells[1] == "Question":
            continue
        rows.append(line)
    return rows


def deadline_findings(row, now):
    """One row's clock problems, as codes, read against a given moment.

    Four codes and they are not degrees of the same thing. `unasked` is a row
    with no clock because nobody started one. `unreadable` is a row with a clock
    nothing can read. `expired` is a clock that ran out with the row still in
    the table, which under the standard means the answer is already in force.

    `duplicated` is a row naming more than one ask, and it was added on
    2026-11-02 because the PM seat posted both of this register's open
    questions to the owner twice in eight hours. The first pair went out at
    00:32:58Z and 00:33:05Z carrying this seat's handoff, the second pair at
    08:28Z carrying no reference to the first, and all four are live on the
    bus with nothing withdrawn.

    The reason it is a finding rather than bookkeeping is the arithmetic.
    Section 22 starts its forty-eight hours when the reservation is posted, and
    a second posting of the same reservation is not a second reservation. So
    the governing clock is the EARLIEST, and `expired` is read against that one
    rather than against any of them. Recording the newer id as the row's clock
    would have moved both of these rows back eight hours, on rows that have
    been open for fifteen days, and a reservation re-posted often enough would
    never resolve at all.
    """
    found = DEADLINE.findall(row)
    ids = []
    for one in ASKED.findall(row):
        if one.lower() not in ids:
            ids.append(one.lower())
    out = []
    if (ids or SILENCE.search(row)) and not found:
        out.append("unreadable")
    elif not found:
        out.append("unasked")
    if len(ids) > 1:
        out.append("duplicated")
    if found:
        # The earliest, which is the one the standard's clock actually runs
        # from. ISO-8601 to the minute sorts lexicographically, so `min` is
        # the comparison and not an approximation of it.
        when = datetime.datetime.fromisoformat(min(found)).replace(
            tzinfo=datetime.timezone.utc)
        if when <= now:
            out.append("expired")
    return tuple(out)


def deadline_cases():
    """Every case above, run before the register is opened."""
    bad = [(want, row) for want, row in DEADLINE_CASES
           if deadline_findings(row, CASE_NOW) != want]
    print(f"DEADLINE_CASES                             "
          f"{len(DEADLINE_CASES) - len(bad)} of {len(DEADLINE_CASES)}")
    for want, row in bad:
        print(f"  FAIL    wanted {want or 'nothing'}, got "
              f"{deadline_findings(row, CASE_NOW) or 'nothing'}")
        print(f"            {row[:96]}")
    return 1 if bad else 0


def deadlines():
    """A reservation for the owner with a clock on it that nothing reads.

    `awaiting-her-word.md` holds two tables. The upper one waits on a seat's
    diff and nothing in it expires, which is why the oldest row there has been
    open for thirty-one days and the register says so in plain words. The lower
    one waits on her, and until 2026-10-26 that wait had no end either.

    Then §22 of `docs/standards/pm.md` gave it one. A reservation a charter
    makes for the owner is posted by the PM as an ask carrying the PM's own
    recommendation, and it proceeds as recommended after forty-eight hours of
    her silence. So the correction-notice question asked on 2026-10-26 is the
    first row in this register whose answer arrives by itself, at a stated
    hour, whether or not anybody is looking.

    Run 58 wrote that hour into the row as "at about 20:44 UTC on 2026-10-28",
    and wrote beside it that a clock nobody can read is the thing to avoid.
    Both halves of that sentence were true of the sentence itself. This check
    is the other half, and it asks the two questions the prose cannot:

      a row that argues the silence rule and names no deadline,
      a deadline that has passed with the row still in the table.

    The second one is a time bomb on purpose, and the cost is worth naming
    because the inbox README argues the opposite case well: a gate that can
    turn `main` red over a bookkeeping step is worse than the collision it set
    out to fix. This one cannot. No workflow runs this file; it runs in a
    writer seat's own run, which is the only place where the thing to do about
    an expired reservation is decidable. What goes red is a run, in front of
    the seat that can record the resolution, move the row to the closed table,
    and say what the words are now.

    What it deliberately does not do is decide the answer. Resolving a
    reservation by silence is the standard's mechanism and the PM's to apply.
    This reports that the hour has passed and leaves the ruling where it lives.
    """
    rc = deadline_cases()
    print()
    rows = question_rows()
    now = datetime.datetime.now(datetime.timezone.utc)
    print(f"questions awaiting her word                {len(rows)}")
    print(f"carrying a readable deadline               "
          f"{sum(1 for r in rows if DEADLINE.search(r))}")
    print(f"naming the ask they were posted as         "
          f"{sum(1 for r in rows if ASKED.search(r))}")
    print(f"read at                                    "
          f"{now.strftime('%Y-%m-%dT%H:%MZ')}")
    for row in rows:
        for code in deadline_findings(row, now):
            rc = 1
            question = [c.strip() for c in row.split("|")][1]
            print(f"  FAIL    {question[:88]}")
            if code == "unreadable":
                print("            names an ask or a silence rule and no "
                      "`deadline YYYY-MM-DDTHH:MMZ`")
            elif code == "duplicated":
                print("            more than one ask for one reservation. "
                      "Section 22's clock runs from the FIRST posting, so")
                print("            the earliest deadline governs and the "
                      "later id buys no further silence. Say which one")
                print("            the row is read against, and tell the "
                      "seat that posted the second that the first exists")
            elif code == "unasked":
                print("            no ask and no deadline. Section 22 covers "
                      "every reservation a charter makes except money, "
                      "accounts,")
                print("            secrets and a seat's own authority, so this "
                      "row is owed an ask from the PM and has never had one")
            else:
                print("            the deadline passed and the row is still "
                      "open, so the recommendation in the candidate is in "
                      "force and this register says it is still a question")
    if rc == 0:
        print("  every row names its ask, every clock is readable, and none "
              "of them has run out")
    print()
    print("A reservation for the owner that proceeds on her silence is the one")
    print("row in this register whose answer arrives without anybody acting,")
    print("so it is the one row that has to be read by a command rather than")
    print("by whoever happens to open the file.")
    return rc


# ---- ledger -----------------------------------------------------------

DESK = ROOT / "site/app/desk/page.jsx"
LEDGER_MD = ROOT / "docs/ideas.md"

#: The status line as `docs/ideas.md`'s contract writes it, which is the
#: pattern `tools/ledger.py` compiles and the one authority on the shape. Kept
#: as a Python translation of that file's `STATUS_LINE` rather than imported,
#: because what this check compares is a SECOND implementation against the
#: first and importing the first would make the comparison vacuous.
LEDGER_STATUS = re.compile(r"^-\s+Status:\s*(\w+)", re.M)

#: The pattern the desk's own parser uses, lifted out of the page by reading
#: it. A literal copy here would be a third implementation and would go stale
#: silently, which is the defect this whole check is about.
DESK_STATUS = re.compile(r"match\((/[^/]+/[a-z]*)\)")


def desk_queue_statuses():
    """The statuses `site/app/desk/page.jsx` treats as awaiting her verdict."""
    if not DESK.exists():
        return None
    text = DESK.read_text()
    return sorted(set(re.findall(r'i\.status === "(\w+)"', text)))


def ledger_count(pattern, statuses, text):
    """Entries of `docs/ideas.md` whose status matches, read one way."""
    blocks = re.split(r"^### ", text, flags=re.M)[1:]
    out = {}
    for block in blocks:
        body = "\n".join(block.split("\n")[1:])
        m = pattern.search(body)
        status = (m.group(1) if m else "").lower()
        if status in statuses:
            out[status] = out.get(status, 0) + 1
    return out


def ledger(ref=None):
    r"""The number beside "Awaiting your verdict" is a claim, and it is wrong.

    A count printed on a surface is a sentence a reader can answer "how do you
    know that" about, so it is this seat's to check, and the answer here is
    that the desk reads `docs/ideas.md` with its own regex rather than through
    the file's contract.

    `tools/ledger.py` exists for exactly that reason. Its own opening says the
    ledger "is read by grep in at least three places" and that an entry whose
    status is prose "is silently absent, which is the failure mode that leaves
    no trace". That was recorded in the incident register on 2026-09-24. The
    desk's `parseIdeas` is a fourth such reader, in JavaScript, on the page the
    owner opens daily.

    Its pattern carries no line anchor, so it matches `Status:` inside a
    sentence. Measured on the live file the day this check was written, the two
    readers disagree by one entry, and the entry is

        2026-09-24 - A ledger entry can hide from every consumer by writing
        its status as a sentence

    whose real status line reads `proposed` and whose own first bullet quotes
    `grep "Status: accepted" docs/ideas.md`. The entry warning that a status
    written as a sentence hides an entry from every consumer is hidden from the
    owner's console by a status written as a sentence in its own body.

    The fix is one anchor and one flag, `/^-\s+Status:\s*(\w+)/m`, and it is
    written out in `docs/voice/desk-verdict-queue-2026-10-24.md` beside the
    four lines that print these counts. This check fails until the page agrees
    with the contract and goes green on that diff.

    It compares the two readings rather than grepping the page for the right
    regex, because a check that looks for a known-good string passes on any
    pattern that contains it and says nothing about the number on the surface.
    What matters is the count the owner reads.

    And the count the owner reads comes off `main`, not off this checkout. The
    page fetches
    `raw.githubusercontent.com/alexandrapaiz/alexandria/main/docs/ideas.md`, so
    a run that appends to the ledger moves the working tree's figure and not
    the live one. That is ban list 105's lesson in this file already, and it is
    why the ref is an argument and is printed either way: the run that found
    this measured 524 against 525 on `origin/main` and 527 against 528 on its
    own branch, from three entries it had just written.

        python3 -I docs/voice/check_voice.py ledger origin/main
    """
    statuses = desk_queue_statuses()
    if statuses is None:
        print(f"  SKIP    {DESK.relative_to(ROOT)} is not in this checkout")
        return 0
    found = DESK_STATUS.search(DESK.read_text())
    if not found:
        print("  FAIL    no status pattern found in the desk's parser")
        print("            this check reads the page's own regex rather than")
        print("            holding a copy, so a rewrite of the parse needs it")
        print("            pointed at the new shape")
        return 1
    literal = found.group(1)
    body, flags = literal.rsplit("/", 1)
    desk_pattern = re.compile(body[1:].replace("\\s", r"\s"),
                              re.M if "m" in flags else 0)
    if ref and not resolves(ref):
        return dead_ref("ledger", ref)
    text = at_ref(ref, "docs/ideas.md") if ref else LEDGER_MD.read_text()
    if text is None:
        print(f"  FAIL    docs/ideas.md is not readable at {ref}")
        return 1
    mine = ledger_count(desk_pattern, statuses, text)
    contract = ledger_count(LEDGER_STATUS, statuses, text)
    print(f"read from   {ref or 'the working tree'}, and the page reads main")
    print(f"the queue's statuses, read off the page   {', '.join(statuses)}")
    print(f"the desk's pattern, read off the page     {literal}")
    print(f"the contract's pattern, tools/ledger.py   /^-\\s+Status:\\s*(\\w+)/m")
    print()
    rc = 0
    for status in statuses:
        d, c = mine.get(status, 0), contract.get(status, 0)
        mark = "OK  " if d == c else "FAIL"
        print(f"  {mark}    {status:<10} desk {d:>4}   contract {c:>4}")
        if d != c:
            rc = 1
    print(f"            total      desk {sum(mine.values()):>4}   "
          f"contract {sum(contract.values()):>4}")
    if rc:
        print()
        print("The desk prints a count the repository's own reader of the same")
        print("file contradicts. The anchor and the flag are in")
        print("docs/voice/desk-verdict-queue-2026-10-24.md, with the entry the")
        print("page cannot see named in full.")
    return rc


# ---- firstuse ----------------------------------------------------------
#
# Her outsider ruling of 2026-09-19, and the half of it no command could see.
#
# The ruling is that every term of art gets its plain-words clause the FIRST
# time it appears. `prompts/digest.md` carries it in seven places across about
# a hundred lines, one of which orders the model to build the list
# mechanically before judging anything, and the last archived issue breaks it
# roughly twenty times. The taste gate scores that ruling by quoting the rule,
# so it is green on a rule that is present and failing.
#
# The structural reason the prompt cannot hold it is in the prompt's own
# words: the class this pass exists to catch is the one that "does not look
# like jargon on the page". Finding those words in your own prose is a
# judgment about what you know, made by the thing that knows it. So the
# inventory moves out of the model.
#
# What is mechanical here and what is not, stated before the output rather
# than discovered in a grade:
#
#   The INVENTORY is mechanical. Which words are terms of art, how many there
#   are, and where each one first reaches the reader, counting the title, the
#   masthead, the headings and the bold leads. That is the width, and the
#   width is what no eye in this seat's loop had ever counted.
#
#   The ADEQUACY is a reading. Whether a clause actually defines its term is
#   not a thing a regex knows, and the taste gate's lesson is that a quote
#   proves a rule is present and says nothing about the artifact. So a gloss
#   marker is reported as presence and never scored as a pass.
#
# The two gates below are therefore both counts rather than judgments, and
# both numbers are the generator's own.

# The class the first-use pass says it exists to catch: ordinary English doing
# a technical job. Six of these are quoted in her rulings or in the
# generator's own list of examples. The rest came off the archived issues and
# the grades in docs/voice/reviews/. A word here is not banned. It needs a
# clause the first time a reader meets it.
CLUB = set("""
alignment anneal annealed annealing ablation attention bootstrapping
checkpoint checkpoints chain-of-thought distil distill distilled distillation
distills embedding embeddings few-shot fine-tune fine-tuned fine-tunes
fine-tuning gradient gradients hallucination harness harnesses held-out
imitation inference latent logits macro-average mixture-of-experts off-policy
on-policy overfit overfits overfitting perplexity post-training pretraining
pre-training prior priors quantization regularize regularized regularizes
regularization reward rewards rollout rollouts scaffold scaffolding self-play
sparsity student supervision supervised teacher test-time token tokens
trajectory trajectories zero-shot
""".split())

# Ruled ordinary for this reader, so the frequency class below stops
# reporting them. A builder outside the research world holds these. Each one
# is a ruling this seat made in a grade, and the place to argue one is the
# grade rather than the code.
ORDINARY_TERMS = set("""
agent agents api benchmark benchmarks ceiling cpu deployment gpu latency model
models pipeline prompt prompts reasoning repository runtime text training url
""".split())
# "ceiling" and "text" were the first two rows the frequency class produced
# and the grade of 2026-10-23 ruled both ordinary: the first is plain English
# used plainly, the second is the link furniture of every citation line.

# Institutions and their abbreviations. Law 11 requires the attribution, so
# the name is not the writer's choice and reporting it as a club word would
# ask the issue to break one law to hold another. Reported apart, because an
# outsider does not hold "HKUST" either and that is a real cost the grade
# should see rather than a violation the generator can fix.
INSTITUTION = set("""
ai2 aist alibaba baidu berkeley bytedance caltech cmu cnrs deepmind epfl eth
fair hkust huggingface ibm inria kaist meta microsoft mila mit nus ntu nvidia
nyu openai oxford peking riken stanford tencent tsinghua tu ucla ucsd uiuc
us ut usc washu
""".split())

# Capitalised forms a builder reads without help.
ORDINARY_CAPS = set("""
ai api cpu eu gpt gpu i ml llm llms ok pdf sdk uk url us
""".split())

# Ordinary English, for the frequency class only. Short and deliberately
# incomplete: a word this list misses is reported as a CANDIDATE for the grade
# to rule, which is the failure mode worth having. A word it wrongly contains
# is a term of art that never reaches the inventory, and that is the failure
# this whole command exists to stop.
ORDINARY = set("""
able about above across after again against all already also although always
among amount and another answer any anyone anything approach are around as
ask asked at back bad based be because become been before begin behind being
below best better between both break builder builders build building built but
by call called can cannot carry case cases change changed changes cheaper
choice choose claim claims clear close collect come common cost costs could
course cut day days decide decision decisions deep different direction
directions discard do does doing done down drop each early easy edge effect
either else end enough even eventually every everything evidence exactly
example experiments fail fails failing far fast faster few field final finally
find first fit five fix follow for found four from full further gain gap get
gets getting give given go going good got group groups had half hand happens
hard has have having heavy held help high hit hold holds hour hours how
however idea if important in instead into is it its itself just keep keeps
kept kind kinds know known large largest last late later latest lead leads
learn learned least leave leaving left less let level like likely limit line
little local long longer look looks lose lost lot low made make makes making
many matter matters may mean means measure measured measures method methods
middle might mind minimal month months more most move moved much must name
named names need needs never new newer next no none nor not nothing now number
numbers of off offer often old older on once one ones only open or order other
others our out over own paper papers part parts pass passed past pay people
per percent place places point points possibility possible practice present
preserve prevent problem problems process produce progress proposal proposes
propose put question questions raise rate rather reach reaches read reader
readers real really reason reasons recover recovers region regions
replacement replace replaces report reports reserves rest restores result
results review reviewing reviews rewrite rewrites right rise room run runs
said same save saves saw say says scale score scores search second see seen
sense sequential set sets settled several share shares shift ship shipped
shop short should show showed shown shows side simple simpler simply since
single six size slow slower small so software some something sometimes soon
sort sources space specific spent stack stage stages stall stalls stand
standing start started state states stay stays step steps still stop
strongest style such suggests support supports sure system systems take taken
takes target team teams tell ten test tests than that the their them then
there these they thing things think this those though three through time times
to today together told too took top toward trace traced treat trick true try
turn turned turns two under understood until up update upon us use used uses
using usually very wall want was watch watching way ways we week weeks well
went were what whatever when where whether which while who whole why will win
with within without word words work worked works worse worth would write
writes wrong wrote year years yet you your
""".split()) | CLAIM_STOP

# Presence of a clause, never its adequacy.
#
# Tested relative to the term rather than across the whole sentence, which is
# what makes the loose markers safe to include. An appositive arrives directly
# after the word it defines, so ", a" and ", the" mean something a few
# characters past the term and nothing at all somewhere else in a long
# sentence. The first cut searched the sentence, so it had to leave the
# appositive out to avoid matching every comma, and then reported a correctly
# glossed term as bare.
GLOSS = re.compile(r"^.{0,3}(?:'s|s)?\s*(?:,|\(|\u2014|:)\s*"
                   r"(?:which|meaning|where|that is|i\.e\.|one|a|an|the|two)\b"
                   r"|^.{0,24}\b(?:is|are|means|is called|called)\s+"
                   r"(?:the\s+)?(?:plain|name|one|a|an)\b"
                   r"|^.{0,40}\bworks like this\b"
                   r"|^.{0,40}\bin other words\b", re.I)


def glossed(term, window):
    """Is a clause present directly after the term's first appearance here?

    The term, not the sentence. A definition is adjacent to the word it
    defines, so this reads the window from the term onward and asks only
    about the next few characters. Where a term is an inflected family, any
    of its surface forms satisfies the search.
    """
    low = window.lower()
    for form in sorted(term, key=len, reverse=True):
        i = low.find(form)
        while i != -1:
            if GLOSS.match(window[i + len(form):]):
                return True
            i = low.find(form, i + 1)
    return False


SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'])")
WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*")

# The citation line, which is the paper's own title in italic followed by the
# link (law 8 and the generator's title rule). Words that appear ONLY here are
# not the writer's choice, the same way an institution's name is not, so
# reporting them as violations would ask the issue to break one law to hold
# another. A term used in a citation AND in the prose is still caught, at its
# first use in the prose, which is where the ruling bites.
CITATION = re.compile(r"^\s*\*.+\*\s*[-–]\s*\[")


def issue_sentences(path):
    """One issue's sentences in reading order, each with its line and source.

    The title, the masthead, every heading and every bold lead are sentences
    here, because her ruling counts the term the reader MEETS. A pass reading
    body prose only once cleared a title term carried bare through eight
    appearances, a heading and the closing line.

    Split per line and then per sentence, so a line number never drifts and a
    figure like 44.3% is not read as the end of a sentence.
    """
    out = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        source = "citation" if CITATION.match(raw) else "written"
        line = re.sub(r"\]\([^)]*\)", "]", raw)         # the text, not the url
        line = re.sub(r"^\s*(?:#+|>|[-*+])\s+", "", line)
        line = norm(line.replace("**", "").replace("*", "").replace("`", ""))
        if not line or set(line) <= set("-|= "):
            continue
        for s in SENT.split(line):
            if s.strip():
                out.append((n, s.strip(), source))
    return out


def coined(tok):
    """A method name, a benchmark name or an acronym, by its shape alone."""
    bare = tok.replace("-", "")
    if len(bare) < 2 or not bare.isalnum():
        return False
    if bare.isupper():
        return True
    return any(c.isupper() for c in bare[1:])


def family(low):
    """The idea a club word belongs to, so inflections count as one term.

    Her ruling and the generator both say one idea, one word: "distillation",
    "distilled", "distills" and "distil" are four rows in a naive inventory
    and one term to a reader, and an inventory that prints them four times
    overstates the width it exists to measure. Grouped on five characters,
    which separates every pair on the CLUB list, and the surface forms are
    printed beside the row so a grade can see the grouping it is trusting.
    """
    return low[:5]


def terms_of(sentences):
    """Every term of art in one issue, with its count and its first sentence.

    Four classes, and the fourth is why this is a command. The first three
    are lists, so a model could have followed them. The fourth is the
    generator's own rule, which is that the list is built by frequency and
    not by what looks like jargon, and it is the rule that produces the words
    nobody would have thought to list.

    Order matters in one place. CLUB is tested before the capital-letter
    shape, because "On-Policy" inside a paper's title is the same club word
    as "on-policy" in the prose, and the first cut of this counted it twice
    under two classes and reported one of them as clean.
    """
    seen, counts, forms = {}, collections.Counter(), collections.defaultdict(set)
    for n, s, source in sentences:
        for i, m in enumerate(WORD.finditer(s)):
            tok, low = m.group(), m.group().lower()
            if low in ORDINARY_TERMS or low in ORDINARY_CAPS:
                continue
            if low in CLUB:
                kind, key = "club", family(low)
            elif low in INSTITUTION:
                kind, key = "institution", low
            elif coined(tok):
                kind, key = "coined", low
            elif tok[0].isupper() and i > 0:
                # A proper noun: a person or an institution as the payload
                # spells it. Law 11 requires the attribution and ban list 117
                # says the name is copied character for character, so it is
                # not a word the writer chose. The first cut read "Google"
                # and "University" as club words by frequency alone.
                kind, key = "name", low
            elif low not in ORDINARY and len(low) > 3:
                kind, key = "frequency", low
            else:
                continue
            counts[(key, kind)] += 1
            forms[(key, kind)].add(low)
            if (key, kind) not in seen or (seen[(key, kind)][2] == "citation"
                                           and source == "written"):
                seen[(key, kind)] = (n, s, source)
    out = {}
    for k, c in counts.items():
        if k[1] == "frequency" and c < 3:
            continue          # the generator's own threshold, three or more
        out[k] = (c, seen[k][0], seen[k][1], seen[k][2], sorted(forms[k]))
    return out


#: Where the paths a pass grades came from, written once by `main` and read by
#: `scope`. A global rather than a parameter because the per-call-site version
#: of this bookkeeping has already produced a bug: `standalone` worked its own
#: answer out from a path prefix and printed `site/content/issues` for a path
#: given on the command line, so the one pass that stated its scope stated
#: somebody else's directory. One writer and eleven readers is the shape that
#: cannot drift.
SCOPE_SOURCE = "archive"


#: How a pass's scope is read, asserted because the answer is a verdict rather
#: than a note, and because what it replaces was eleven passes printing clean
#: counts over a quarter of the product. Each case is
#: (what was read, what the product serves, what is retired, the source) ->
#: (code, the served weeks that were not read).
SCOPE_CASES = (
    # The default scope on the day this was written. The archive holds two
    # files, one of them retired, and the product serves four.
    ((("2026-W37", "2026-W39"),
      ("2026-W39", "2026-W40", "2026-W42", "2026-W44"), ("2026-W37",),
      "archive"),
     ("SHORT", ("2026-W40", "2026-W42", "2026-W44"))),
    # `--live`. Every served edition was read, so the scope is the product's
    # and there is no deficit to state.
    ((("2026-W39", "2026-W40", "2026-W42", "2026-W44"),
      ("2026-W39", "2026-W40", "2026-W42", "2026-W44"), (), "live"),
     ("WHOLE", ())),
    # The product unreached. How short the scope is is not known, and scoring
    # that as whole is the failure this reading exists to refuse: a gate that
    # cannot see its own deficit says so rather than reporting it as zero.
    ((("2026-W39",), None, ("2026-W37",), "archive"), ("UNKNOWN", ())),
    # Paths named on the command line. The caller chose the scope, so a
    # deficit against the product is not this pass's to report, and ban list
    # 91 is the rule that applies to a figure under a named path instead.
    ((("2026-W42",), ("2026-W39", "2026-W44"), (), "named"), ("NAMED", ())),
    # A retired edition read beside the served ones is not missed, and it does
    # not make a short scope whole either. 2026-W37 is both of those here.
    ((("2026-W37", "2026-W39", "2026-W40", "2026-W42", "2026-W44"),
      ("2026-W39", "2026-W40", "2026-W42", "2026-W44"), ("2026-W37",),
      "archive"),
     ("WHOLE", ())),
    # The archive holding a week the product does not serve at all. It is not
    # retired and it is not served, so it is read and it closes no gap.
    ((("2026-W41",), ("2026-W39", "2026-W44"), (), "archive"),
     ("SHORT", ("2026-W39", "2026-W44"))),
)


#: What `doubles` has to read, asserted on sources rather than on this file,
#: so the cases say what the rule is instead of what today's tree happens to
#: hold. Each case is (source, the names defined more than once).
DOUBLES_CASES = (
    # The live shape of the defect it was written for: one name, two
    # top-level definitions, and the lower one is the only one that runs.
    ("def a():\n    return 1\n\n\ndef b():\n    return 2\n\n\ndef a():\n"
     "    return 3\n", ("a",)),
    # A name defined once and called many times is not a double.
    ("def a():\n    return 1\n\n\nb = a()\nc = a()\n", ()),
    # A nested definition shadows nothing at the top level, and a gate that
    # counted it would fire on every closure and every local helper.
    ("def a():\n    def a():\n        return 1\n    return a\n", ()),
    # A module constant rebound at the top level IS a double, and it is the
    # same defect wearing a different hat: the first value is unreachable and
    # a reader of the first line has read a lie.
    ("X = 1\nY = 2\nX = 3\n", ("X",)),
    # A conditional rebinding is not. One of the two branches runs, which is
    # a choice the author made rather than a line they forgot.
    ("import os\nX = 1\nif os.environ.get('Q'):\n    X = 2\n", ()),
    # Augmented and annotated assignment at the top level, for the same
    # reason: neither one hides an earlier value a reader could mistake for
    # the live one.
    ("X = 1\nX += 1\n", ()),
    # Two names each doubled, reported in the order the file defines them.
    ("A = 1\nB = 2\nA = 3\nB = 4\n", ("A", "B")),
)


def doubles_in(src):
    """Every top-level name this source defines more than once, in file order.

    Top level only, and by plain assignment or `def` or `class` only. The
    narrowness is the reading: a nested `def` shadows a name inside one scope
    on purpose, a branch rebinding a constant is a choice, and `+=` needs the
    earlier value. What this catches is the one shape where a line of a file
    cannot run and nothing says so.
    """
    seen = collections.defaultdict(list)
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            seen[node.name].append(node.lineno)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    seen[target.id].append(node.lineno)
    order = {}
    for name, lines in seen.items():
        if len(lines) > 1:
            order[name] = min(lines)
    return tuple(sorted(order, key=order.get)), seen


def doubles():
    """Is any name in this seat's own python defined twice?

    The gate for a class this file has already shipped once. `shown_path` was
    defined at two top levels 1,946 lines apart, the lower one bound every
    caller, and the upper one was dead from the hour the lower one landed. No
    check here could see it: `selfcheck` reads the lines a run ADDS, so it
    sees the second definition arriving and has nothing to compare it to, and
    `sweep` reads prose. A duplicate definition is silent by construction,
    exactly like a committed conflict marker: it is wrong once, at the moment
    it is written, and ordinary text forever after.

    Scoped to `docs/voice/*.py`, which is this seat's own surface. The same
    reading applies to `tools/*.py` and widening it from here would drop a new
    red into lanes this seat does not own, which is incident 23's class and
    the same boundary entry 159's repair drew for the same reason.
    """
    bad = [(src, want, doubles_in(src)[0]) for src, want in DOUBLES_CASES
           if doubles_in(src)[0] != want]
    if bad:
        for src, want, got in bad:
            print(f"  CASE    {src!r}")
            print(f"            want {want}")
            print(f"            got  {got}")
        print()
        print("DOUBLES_CASES says what this reading has to do. Nothing below")
        print("was read, because a duplicate check failing its own cases")
        print("reports a clean file for the wrong reason.")
        return 1
    print(f"  the reading's own cases    {len(DOUBLES_CASES)} pass")
    files = sorted((ROOT / "docs/voice").glob("*.py"))
    print(f"  python under docs/voice    {len(files)}: "
          f"{', '.join(p.name for p in files)}")
    rc = 0
    for p in files:
        names, seen = doubles_in(p.read_text(encoding="utf-8"))
        if not names:
            continue
        rc = 1
        for name in names:
            where = ", ".join(str(n) for n in seen[name])
            print(f"  FAIL    {shown_path(p)}  {name} defined "
                  f"{len(seen[name])} times at lines {where}")
            print( "            the last one binds every caller, so the")
            print( "            others are lines that cannot run")
    if not rc:
        print("  no name under docs/voice is defined twice at the top level")
    print()
    print("A line that cannot run is not an error and not a warning. It")
    print("reads exactly like a line that can, which is why this needed a")
    print("command rather than a reader.")
    return rc


def scope_reading(read, served, retired, source):
    """The verdict on a pass's scope, kept apart from the printing of it.

    `retired` is accepted and never consulted, and that is the reading rather
    than an oversight. A week retired at the serving layer is not in `served`
    to begin with, because `served_weeks` reads the product's own library
    page, so subtracting it a second time would be arithmetic on a set it was
    never in. It stays in the signature because every caller holds it, and a
    reader of the cases above needs to see that it was weighed.
    """
    if source == "named":
        return "NAMED", ()
    if served is None:
        return "UNKNOWN", ()
    seen = set(read)
    missed = tuple(w for w in served if w not in seen)
    return ("SHORT" if missed else "WHOLE"), missed


def scope(paths, retired, given=None):
    """What this pass read, printed before any count it reports.

    `L-A47`: an instrument's scope is part of its answer, and a scope it does
    not state is whatever it happened to be pointed at. Eleven passes in this
    file glob `site/content/issues/*.md` and call the result the issues. That
    directory holds two files, one of them retired, and the product serves
    four, which is `INC-2026-10-24-a-gate-grades-a-print-against-rules-
    written-after-it`.

    This helper was written for that class and was called by one pass of the
    eleven, so ten of them printed counts with no scope line at all. It also
    named the gap from a sentence about 2026-W40 written into the code, and
    said the authority was the `digests` table behind `NEON_RO_URL`. That was
    true when it was written and stopped being true when `served_weeks`
    landed: the product's own library page names the served weeks with no
    credential at all, so the deficit is printed by week here rather than
    argued in prose.

    The digests table is still the authority on what SENT, and the library
    page is the authority on what a reader can open today. Those are two
    questions, and the counts in this file are about the second one, because
    every law in the canon is a law about a page somebody reads.

    `given` is kept for the one caller that passed it and is ignored. The
    answer comes from `SCOPE_SOURCE`, which `main` writes.
    """
    read = [pathlib.Path(x).stem for x in paths]
    off = [x for x in read if x in retired]
    on = [x for x in read if x not in retired]
    code, missed = scope_reading(read, served_weeks_cached(), retired,
                                 SCOPE_SOURCE)
    if code == "NAMED":
        print(f"  read from   {len(paths)} path(s) named on the command line")
        print( "              a figure below belongs to the artifact above it")
        print( "              and to no other, which is ban list 91")
        return
    where = ("the product, un-rendered" if SCOPE_SOURCE == "live"
             else "site/content/issues")
    print(f"  read from   {where}, {len(on)} served: "
          f"{', '.join(on) if on else 'none'}")
    if off:
        print(f"              {len(off)} retired and not served: "
              f"{', '.join(off)}")
    if code == "WHOLE":
        print( "  WHOLE       every edition the product serves was read")
    elif code == "UNKNOWN":
        # The verdict is UNKNOWN both ways and the sentence is not, because a
        # blind spot a run declared and one it walked into are the same size
        # and not the same kind. `editions` draws that line in its SKIP and
        # this keeps it drawn where the count is.
        why = ("this run declared ALEXANDRIA_OFFLINE"
               if os.environ.get("ALEXANDRIA_OFFLINE")
               else "the product went unreached")
        print(f"  SCOPE?      {why}, so how short this")
        print( "              scope is is unknown. A count below is a verdict")
        print( "              on the files named above and on nothing else")
    else:
        print(f"  SHORT       {len(missed)} served edition(s) not read: "
              f"{', '.join(missed)}")
        print( "              `editions` carries the verdict, --live reads them")


def firstuse(paths=None):
    retired = hidden_weeks()
    # `given` was this pass's own reading of where its paths came from and it
    # is gone, because `SCOPE_SOURCE` is the one place that knows and `--live`
    # made the local reading wrong: live paths ARE given, and calling them
    # named would have hidden the only scope this file can call whole.
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
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
        sents = issue_sentences(p)
        found = terms_of(sents)
        print(f"{shown}" + ("   [retired, not served]" if off else ""))

        # The title gate, first and separately, because the title is a closed
        # list and the rest of this pass is not. The generator says so in its
        # own words and says it has already failed twice. A title term is
        # defined in the title's own sentence or in the first sentence of the
        # opening, and nowhere later, because the reader met it before they
        # had any reason to keep reading.
        title = sents[0][1] if sents else ""
        opening = next((s for n, s, src in sents[2:] if len(s) > 60), "")
        onramp = f"{title} {opening}"
        bare_title = []
        for i, m in enumerate(WORD.finditer(title)):
            tok, low = m.group(), m.group().lower()
            if low in ORDINARY_TERMS or low in ORDINARY_CAPS:
                continue
            if low in INSTITUTION or (low not in CLUB and not coined(tok)
                                      and not (tok[0].isupper() and i > 0)):
                continue
            if low not in CLUB and not coined(tok):
                continue
            if not glossed([low], onramp):
                bare_title.append(tok)
        bare_title = list(dict.fromkeys(x.lower() for x in bare_title))
        print(f"  title terms a reader cannot define            {len(bare_title)}")
        for w in bare_title:
            print(f"    BARE    {w!r} in the title, and no clause in the title's own")
            print( "            sentence or in the opening's first sentence")

        rows = [(k, v) for k, v in found.items()
                if k[1] in ("club", "coined", "frequency")]
        rows.sort(key=lambda kv: (kv[1][1], kv[0][0]))
        own = [r for r in rows if r[1][3] == "written"]
        quoted = [r for r in rows if r[1][3] == "citation"]
        print(f"  terms of art the issue chose for itself       {len(own)}")
        for (key, kind), (count, line, sent, _src, surface) in own:
            window = onramp if line == 1 else sent
            mark = "CLAUSE " if glossed(surface, window) else "BARE   "
            label = "/".join(surface)
            shownkind = "candidate" if kind == "frequency" else kind
            print(f"    {mark} {shownkind:<9} x{count:<3} {label!r}")
            print(f"            {shown}:{line}  {sent[:92]}")

        # Two buckets that are not findings, and both are reported because an
        # outsider pays for them anyway. A grade reads them; the generator
        # cannot fix them without breaking the law that put them there.
        if quoted:
            print(f"  terms only inside a paper's own title         {len(quoted)}")
            print("    " + ", ".join(sorted("/".join(v[4]) for _, v in quoted)))
        named = sorted(k[0] for k, v in found.items()
                       if k[1] == "institution"
                       or (k[1] == "name" and v[3] == "written"))
        if named:
            print(f"  names law 11 requires, spelled as they arrive {len(named)}")
            print("    " + ", ".join(named))

        # The second gate, and the number is the generator's own: more than
        # about five terms needing a definition means the issue is carrying
        # too much, not that it needs more explaining. The repair named there
        # is to cut an item and run the pass again.
        bare = [r for r in own if not
                glossed(r[1][4], onramp if r[1][1] == 1 else r[1][2])]
        named_art = [r for r in own if r[0][1] in ("club", "coined")]
        bare_art = [r for r in bare if r[0][1] in ("club", "coined")]
        print(f"  the generator's cap is five, this issue has   "
              f"{len(named_art)}, {len(bare_art)} of them bare")
        if len(own) != len(named_art):
            print(f"    and {len(own) - len(named_art)} candidate(s) above, "
                  "which the grade rules and the cap does not count")
        if not off and (bare_title or bare_art or len(named_art) > 5):
            rc = 1
    print()
    print("The inventory is the check. A CLAUSE row says a marker sits in the")
    print("same sentence and says nothing about whether it defines the term,")
    print("which is the taste gate's lesson in a second place. A BARE row has")
    print("no marker at all and is the finding. A frequency row a grade rules")
    print("ordinary goes in ORDINARY_TERMS, with the grade that ruled it.")
    return rc


#: The words a line of this generator may not end on when the line after it
#: starts a new block. None of them can close a sentence, so the pair is a
#: first copy whose tail was replaced and whose head was left behind.
DANGLING = set("""a an the and or but of to in on for with that which is are was
were be been by as at from into than then so because its it this these those
not no""".split())

#: What can begin a block rather than continue a wrapped sentence: a markdown
#: bullet, which can never be a continuation, or an ordinary capitalised word,
#: which usually starts a sentence. The exclusions below are what make the
#: second half safe.
RESTART = re.compile(r"^\s*(-\s+\*\*|[A-Z])")

#: A run of capitals is this file emphasising a word mid-sentence ("the heading
#: is\nWRITTEN FRESH"), so it is a continuation and not a restart. Three of
#: this check's four false positives were exactly that shape.
SHOUTED = re.compile(r"^\s*[A-Z][A-Z]+\b")


def duplicated_blocks(lines):
    """A run of lines the file carries twice, contiguously or adjacent.

    Not any repeated line. Two slots of this generator legitimately end on the
    same wrapped cross-reference three hundred lines apart, and a check that
    counted repeated lines would call that damage. What is damage is a run that
    appears twice with nothing between the copies, because the only way to
    write that on purpose is to mean it twice in a row.
    """
    body = [(n, l.strip()) for n, l in enumerate(lines, 1) if l.strip()]
    out, i = [], 0
    while i < len(body):
        best = 0
        # Longest run starting here that is repeated immediately after itself.
        for k in range(1, (len(body) - i) // 2 + 1):
            a = [t for _, t in body[i:i + k]]
            b = [t for _, t in body[i + k:i + 2 * k]]
            if a == b and all(len(t) > 12 for t in a):
                best = k
        if best:
            out.append((body[i][0], body[i + best][0], best, body[i][1]))
            i += 2 * best
        else:
            i += 1
    return out


def unclosed_slots(lines):
    """Where the template's brace depth leaves zero and never comes back.

    Line 502 of the generator tells the model that text in curly braces is an
    instruction to it, replaced by its own words. So a brace that never closes
    does not read as a typo: every slot after it is nested inside an
    instruction block with no end, and the model has to guess where the
    instruction stopped and the template resumed.
    """
    out, depth, opened = [], 0, []
    for n, line in enumerate(lines, 1):
        for ch in line:
            if ch == "{":
                depth += 1
                opened.append(n)
            elif ch == "}":
                depth -= 1
                if opened:
                    opened.pop()
                if depth < 0:
                    out.append((n, "a closing brace with nothing open"))
                    depth = 0
    for n in opened:
        out.append((n, "opened here and the file ends with it still open"))
    return out


def truncations(lines):
    """A line ending mid-clause with a new block on the line after it.

    The fourth false positive is the reason for the two balance tests. A line
    ending inside an open parenthesis or an open quotation is mid-quotation and
    its next line finishes the quote, so an attribution example wrapping after
    `("researchers at` is not damage.
    """
    out = []
    for i in range(len(lines) - 1):
        cur, nxt = lines[i].rstrip(), lines[i + 1]
        if not cur.strip() or not nxt.strip():
            continue
        if cur.endswith((".", ":", "!", "?", "}", "`", '"', ")", "*")):
            continue
        if cur.count("(") != cur.count(")") or cur.count('"') % 2:
            continue
        if SHOUTED.match(nxt):
            continue
        words = re.findall(r"[A-Za-z][A-Za-z-]*", cur)
        if words and words[-1].lower() in DANGLING and RESTART.match(nxt):
            out.append((i + 1, cur.strip()))
    return out


#: The word a headless line may legitimately open with in lower case: a
#: backticked command or path, which is a name rather than a sentence.
NAMED = ("`", "{")

#: `truncations` and `headless` are one defect from two directions, and the
#: second direction is the one the gate could not see. An edit that cuts a
#: bullet's own HEADER leaves the line before it ending on a full stop, so
#: `truncations` discards the pair on its first filter and reports zero. Both
#: cases below are real: they stood in prompts/digest.md for five and thirty-five
#: days, at canon law 12's final heading gate and canon law 6's evidence grade,
#: while `generator` printed "lines ending mid-clause before a new block  0".
#:
#: The false cases are the three shapes that look like this one. A restored
#: header is a bullet and bullets are never continuations. A run of capitals is
#: this file emphasising a word across a line break. And a backticked command
#: opening a line is a name, not a sentence.
HEADLESS_CASES = (
    (True, "institution. It is to write them with no attributive phrase.",
     "  something: every line beginning with `#`, and every run of bold"),
    (True, "rule forbids is an absence and an absence cannot be quoted.",
     "  clause inside the item's own prose, not a footnote and not a line."),
    (True, "Only then output.",
     "  and the fix is to write that line again from the items underneath."),
    (False, "- **Grade the evidence in-line, on every item with a number.** A short",
     "  clause inside the item's own prose, not a footnote and not a line."),
    (False, "Count the links. They match, or the issue is not finished.",
     "- **Grade the evidence in-line.** A short clause inside the prose."),
    (False, "every heading that reaches the reader is",
     "  WRITTEN FRESH from that day's actual news, the way the title is."),
    (False, "Weigh the change before you commit it.",
     "  `python3 pipeline/budget.py` prints the number to read."),
    (False, "A label is a label at any level and in any typeface.",
     "  Ask it of every line and every fragment you collected."),
    (False, "the issue is NOT finished, and the fix is to write that line",
     "  again from the items actually underneath it."),
    # The 2026-10-26 widenings. An unindented paragraph, which is the live
    # specimen at prompts/digest.md:621, and the same shape where a fence used
    # to stop the gate reading at all.
    (True, "never from pleasantries and never from claiming to know their history.",
     "and it is the reason the line exists (owner's dispatch, 2026-09-25). Read it"),
    (True, "Then the source line, on its own line.",
     "steps as a compact numbered list inside the item, indented under it."),
    # And the false positives the widenings could have bought. A paragraph
    # that legitimately opens on a named thing in lower case, a wrapped line
    # whose predecessor carries no full stop, and a fence marker itself.
    (False, "A reader never sees a comment, so a comment is not a surface.",
     "`procedure` is the payload's own name for the field, never the reader's."),
    (False, "The warmth comes from knowing what the reader's job is",
     "like, never from pleasantries and never from claiming to know history."),
    (False, "Count the semicolons. The target is zero.",
     "```"),
)


def headless(lines):
    """A rule whose own opening line was cut, leaving its body standing.

    The shape is one pair of lines: the one before ends a sentence, the one
    after is not a block of its own and opens mid-sentence in lower case.
    Nothing else in these files does that, because a wrapped sentence never
    has a full stop in front of it.

    **Two narrowings came off this on 2026-10-26, because the defect was found
    again in a place both of them hid.** The first version required the body
    line to be INDENTED and skipped every line inside a ``` fence, and both
    choices came from the one specimen it was built from, which was a bullet's
    indented continuation outside the template.

    `prompts/digest.md:621` is the same cut in a plain paragraph inside the
    template. `d022e79a` on 2026-10-18, a trim under the weight rule, removed
    "**A stranger has to enjoy that sentence.** This is the test it has to
    pass" and the blank line above it, so the opening slot's outsider rule now
    begins "and it is the reason the line exists" welded to the end of the rule
    about greetings. The indent test missed it because a paragraph is not
    indented. The fence test missed it because this file's fence runs 520 to
    1353, which is 39% of the generator and is the issue TEMPLATE rather than
    quoted output, so the reasoning `fenced()` uses for review prose is false
    about the one file this gate exists to read.

    So the unit is a sentence, which is what the defect is about, and the
    indent and the fence are not part of it. The guard that does the work is
    the full stop on the line before: a wrapped line never carries one.
    """
    out = []
    for i in range(1, len(lines)):
        prev, cur = lines[i - 1].rstrip(), lines[i]
        if FENCE.match(cur) or not prev.strip() or not cur.strip():
            continue
        # The cut landed on the line before: that is `truncations`, not this.
        if not prev.endswith((".", "!", "?")):
            continue
        if re.match(r"^\s*([-*+]\s|\d+\.\s|#|>|\||```|~~~)", cur):
            continue
        if SHOUTED.match(cur):
            continue
        word = cur.strip().split()[0]
        if word.startswith(NAMED) or not re.match(r"^[a-z]", word):
            continue
        out.append((i + 1, cur.strip()))
    return out


def headless_cases():
    """Every case above, run before the file is read.

    A detector that fails its own cases reports a clean generator for the
    wrong reason, which is the rule `standalone` already works under.
    """
    bad = []
    for want, prev, cur in HEADLESS_CASES:
        got = bool(headless([prev, cur]))
        if got != want:
            bad.append((want, prev, cur))
    return bad


def generator(paths=None):
    """Edit damage in prompts/digest.md, which no gate in this repo read.

    `tools/check_registers.py` reads sixteen shared files for merge damage and
    the criterion in its own comment is that more than one seat appends to the
    file. This one is not on that list, and the damage it was carrying is the
    quiet form rather than the loud one: no conflict marker, just text the file
    already held, written in beside itself.
    """
    paths = paths or GENERATORS
    rc = 0
    bad = headless_cases()
    if bad:
        for want, prev, cur in bad:
            print(f"  CASE    wanted {want}: {cur.strip()[:66]}")
        print("The pattern changed and HEADLESS_CASES says how. Nothing")
        print("below was read.")
        return 1
    print(f"  the headless cases        {len(HEADLESS_CASES)} pass")
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"{p}: missing")
            rc = 1
            continue
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        lines = p.read_text().split("\n")
        dup = duplicated_blocks(lines)
        brace = unclosed_slots(lines)
        trunc = truncations(lines)
        cut = headless(lines)
        print(f"{shown}   {len(lines)} lines")
        print(f"  blocks the file carries twice in a row        {len(dup)}")
        for first, second, k, head in dup:
            print(f"    DUPLICATE  lines {first} and {second}, "
                  f"{k} line(s) each")
            print(f"               {head[:88]}")
        print(f"  curly braces that do not pair                 {len(brace)}")
        for n, why in brace:
            print(f"    BRACE      {shown}:{n}  {why}")
        print(f"  lines ending mid-clause before a new block    {len(trunc)}")
        for n, text in trunc:
            print(f"    TRUNCATED  {shown}:{n}  ...{text[-72:]}")
        print(f"  rules whose own opening line was cut          {len(cut)}")
        for n, text in cut:
            print(f"    HEADLESS   {shown}:{n}  {text[:72]}")
        if dup or brace or trunc or cut:
            rc = 1
    print()
    print("All four findings are one defect seen four ways, and they run in")
    print("both directions. An edit that inserts without removing leaves the")
    print("duplicate, the truncation and the unpaired brace. An edit that")
    print("removes too much leaves the headless rule, which is what a trim")
    print("under the weight rule does when it takes a bullet's own header")
    print("away with the specimens underneath it.")
    print("None of them is a prose judgment, so none of them belongs in a")
    print("grade a person has to remember to run.")
    return rc


# ---- specimens ---------------------------------------------------------

# The writing positions in prompts/digest.md, found by marker rather than by
# line number, because the file is edited on most runs and a hardcoded span
# silently starts reading the wrong region.
#
#   voice   the house-law bullets above the template: how a line gets written
#   slots   the fenced template itself, the {curly brace} writing positions
#   rules   the rules list, which governs writing
#   gates   the passes that read FINISHED output
#
# The boundary that matters is the last one. The file's own doctrine is that a
# banned specimen is safe at a gate, because there you are reading output you
# have already written, and unsafe at a writing position, because there it is
# the nearest available draft. So `gates` is excluded from every finding below
# and the file's own reasoning is why.
REGION_MARKS = (
    ("voice", r"^# The digest writer"),
    ("slots", r"^```$"),
    ("rules", r"^Rules\. Every one of them names examples"),
    ("gates", r"^- Before finishing, reread the whole issue once"),
)

# The payload's own subject matter, taken from the terms the generator's
# first-use rule names as club words plus the stream vocabulary of the field
# it covers. A specimen carrying one of these is written about the research
# the model is about to be handed, which is the one subject a payload controls.
DOMAIN = (
    r"agent|model|paper|benchmark|reward|distillation|gradient|token|cache|"
    r"inference|training|fine-?tun|prompt|LLM|transformer|attention|"
    r"reinforcement|rollout|verifier|alignment|ablation|citation|arxiv|"
    r"researcher|lab\b|dataset|teacher|student|checkpoint|context window|"
    r"self-correction|sampling|scaffold|harness|replicat"
)

# The words the generator forbids the issue to print, in its own words: the
# machine's names for its own parts. A specimen carrying one hands the model a
# sentence that breaks a different rule in the same file.
INTERNAL = (
    r"\bpayload\b|\btriage|\bingest|\bslot\b|\bdeprecation\b|"
    r"\bdeprecated\b|\bdistilled\b|\bclaim graph\b|\bsupports? edge|"
    r"\btraction stream\b|\bsource tier\b|\bdeep[ _]read"
)


def regions(lines):
    """Map each 1-based line number to its writing region."""
    at, seen = {}, None
    for i, line in enumerate(lines, 1):
        for name, pat in REGION_MARKS:
            if re.match(pat, line) and name != seen:
                # The template's fence opens and closes on the same marker, so
                # the second one ends the slots rather than reopening them.
                if name == "slots" and seen == "slots":
                    continue
                seen = name
                break
        at[i] = seen or "voice"
    # The fenced template's closing ``` leaves the region as `slots` until the
    # rules list starts, which is correct: the lines between are the sign-off.
    return at


def quoted(path):
    """Every double-quoted span in a file, with its line and its region.

    The unit is the quoted span because that is the unit the ban list's entry
    93 names: a sentence a reader could lift unchanged. A span running over a
    blank line is a quotation mark used for something else and is skipped.
    """
    text = pathlib.Path(path).read_text()
    lines = text.split("\n")
    at = regions(lines)
    starts, pos = [], 0
    for i, line in enumerate(lines, 1):
        starts.append((pos, i))
        pos += len(line) + 1

    def lineno(off):
        n = 1
        for o, i in starts:
            if o > off:
                break
            n = i
        return n

    out = []
    for m in re.finditer(r'"([^"]{3,400})"', text, re.S):
        body = m.group(1)
        if "\n\n" in body:
            continue
        n = lineno(m.start())
        out.append((n, at[n], norm(body)))
    return out



def shown_path(path):
    """A path as the repository names it, or in full when it is outside.

    The idiom this replaces is inlined in six passes and `measure` carries the
    comment that dates it: a served edition and a `digests` row dumped to a
    file are both artifacts this canon tells a grade to read, and both live
    outside the checkout, so `relative_to(ROOT)` raises on exactly the
    artifacts the `--live` flag exists to fetch. `standalone` still raised on
    2026-11-01, eight days after `--live` was added, because the run that
    widened it repaired the line that reports the SCOPE and left the two lines
    that report a FINDING. That ordering is the defect worth naming: the pass
    printed a clean archive without complaint and crashed only once it had
    something to say.
    """
    path = pathlib.Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())

def past_tense_you(span):
    """The tense check from the stands-alone gate, run on a specimen.

    The gate's own words: find every sentence whose subject is "you" and whose
    verb is in any past tense, past simple, present perfect and past
    continuous alike. This is the one check in the generator the file calls
    grammar rather than judgment, which is why it can be run here at all.

    The participle arm reads a stem of two characters or more, and refuses a
    stem that is itself a negation. It used to read `\\w+`, with no floor, so
    any word ending in ed, en, t or ne was a participle and "you have one
    hour", "you have it", "you have ten" and "you have none" were all read as
    claims about the reader's history. The floor is what separates "done",
    whose stem is "do", from "one", whose stem is "o".

    That mattered the moment this check was pointed at an issue rather than at
    a prompt, because `What to read if you have one hour` is a standing heading
    and the old pattern fired on it. A gate whose first run on the real
    artifact reports a heading the laws permit is a gate nobody keeps, which is
    `INC-2026-10-23-a-voice-gates-first-firing-is-green-for-a-false-reason`
    from the other side. Seventeen cases are asserted in
    `STANDS_ALONE_CASES` below and run by `standalone` before it reads an
    issue, the eight true shapes and the nine that collide with them.
    """
    pat = (r"\byou\b\s+(?:have|had|'ve|'d)\s+(?:not\s+|never\s+)?"
           r"(?!not\b|none\b)\w{2,}(?:ed|en|t|ne)\b"
           r"|\byou\b\s+(?:were|was)\b"
           r"|\byou\b\s+(?:spent|wrote|ran|read|built|saw|went|did|"
           r"watched|shipped|learned|started|stopped)\b")
    return re.search(pat, span, re.I) is not None


def hers(span):
    """Is this specimen the owner's own words, carried over from her register?

    The exemption is computed from `docs/voice/taste.md` and never from a list
    kept here, for the reason the taste gate already gives: this seat may not
    edit her register, so the quote lives on the checker's side and reaches
    across. A specimen she wrote is her fine-tuning, the charter says
    refinements layer on top of it and never beside it, and a gate that
    reported it as a defect would be asking a run to delete her craft.
    """
    if not TASTE.exists():
        return False
    book = norm(TASTE.read_text()).lower()
    low = span.lower()
    if low in book:
        return True
    # Her register wraps, so a long specimen can differ by a word she reworded
    # when she quoted it. Seven words of overlap is her line.
    words = low.split()
    return any(" ".join(words[i:i + 7]) in book
               for i in range(len(words) - 6))


def specimens(paths=None):
    """Ban list 93's unenforced half: the worked example at a writing position.

    Entry 93 was added on 2026-10-05, enforced by deleting the four specimens
    that print had lifted, and left with a stated gap in its own last
    paragraph: the file still teaches by worked example at other writing
    positions and nothing had inventoried them, because a guessed count
    recorded as a sweep is worse than no sweep. Three runs declined that count
    on exactly that ground, the last of them writing "cannot be scored, and
    that is the honest verdict". This is the count.

    Two findings are mechanical and neither is a prose judgment.

    A specimen at a writing position is a draft of the issue's output, so the
    file's own hard gates apply to it. Every one of those gates reads finished
    output and none of them has ever read this file. The first finding runs the
    one gate the file calls grammar rather than judgment, the tense check, over
    the specimens themselves. The second runs the internal-vocabulary rule the
    same way.

    The third is a count rather than a verdict. The file claims, in its own
    words above the template, that every example in it is drawn from a subject
    the payload cannot contain. That claim is checkable and the reading-list
    slot has already refuted it in prose, saying the subject is the one thing a
    payload controls. The count says how far off the claim is. Whether a given
    on-subject specimen is worth its risk stays a reading and stays in the
    grade, and the owner's own specimens are exempted by reaching into her
    register rather than by anyone's judgment here.
    """
    paths = paths or GENERATORS
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"{p}: missing")
            rc = 1
            continue
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            shown = p.resolve()
        spans = quoted(p)
        writing = [(n, r, s) for n, r, s in spans if r != "gates"]
        sentences = [(n, r, s) for n, r, s in writing
                     if len(s.split()) >= 5]
        print(f"{shown}")
        print(f"  quoted spans in the file                      {len(spans)}")
        print(f"  of those at a writing position                {len(writing)}")
        print(f"  of those long enough to lift as a sentence    {len(sentences)}")

        tense = [(n, r, s) for n, r, s in sentences if past_tense_you(s)]
        print(f"  specimens the tense check would fail          {len(tense)}")
        for n, r, s in tense:
            print(f"    TENSE      {shown}:{n}  [{r}]  {s[:96]}")

        internal = [(n, r, s) for n, r, s in sentences
                    if re.search(INTERNAL, s, re.I)]
        print(f"  specimens printing the machine's own words    {len(internal)}")
        for n, r, s in internal:
            print(f"    INTERNAL   {shown}:{n}  [{r}]  {s[:96]}")

        mine = [(n, r, s) for n, r, s in sentences if not hers(s)]
        domain = [(n, r, s) for n, r, s in mine
                  if re.search(DOMAIN, s, re.I)]
        print(f"  specimens that are not her own words          {len(mine)}")
        print(f"  of those written about the payload's subject  {len(domain)}")
        for n, r, s in domain:
            print(f"    ON-SUBJECT {shown}:{n}  [{r}]  {s[:96]}")

        # Only the tense finding fails, and the asymmetry is the file's own.
        # It holds all three shipped past-tense greetings at the gate and says
        # they are "deliberately absent from the opening slot where the line
        # gets written", so a specimen of that shape at a writing position
        # cannot be a banned one and needs no reading. The internal-vocabulary
        # list makes no such promise: the file quotes the machine's own words
        # at writing positions both as the failure and as the form, and one of
        # the two hits below is each. A gate that failed on a correct line is
        # a gate the next run routes around.
        if tense:
            rc = 1
    print()
    print("The tense finding fails this check. A specimen carrying the one")
    print("shape the file calls grammar rather than judgment, at the one")
    print("position the file says that shape is deliberately absent from,")
    print("is a defect by the file's own reasoning and needs no reading.")
    print()
    print("The other two lists are inventory and each is a ceiling rather")
    print("than a verdict, for a reason entry 93 gives itself: a quoted")
    print("BANNED specimen is not this class, because a model copying one")
    print("is caught by the ban, and nothing here can tell a banned")
    print("specimen from an offered one. Both lists hold some of each.")
    print("Sorting them is the reading, and the reading belongs to a")
    print("graded review rather than to this command.")
    return rc


#: The pre-send gate, which is the last thing between a written issue and a
#: reader. `tools/check_digest_quality.py` is the engineer's file and this gate
#: only reads it.
PRESEND = ROOT / "tools/check_digest_quality.py"
BLOCK_RULE = re.compile(r'add\(BLOCK,\s*"([a-z-]+)"')

#: How `prompts/digest-short.md` answers each rule the pre-send gate blocks on.
#: The value is a phrase that has to be present in the short prompt, or None
#: where the rule cannot fire on this edition at all, with the reason beside it.
#:
#: The map is maintained rather than derived, and that is the point of it. A
#: rule added to the pre-send gate lands here as a failure, and the failure is
#: addressed to this seat: does the degraded edition need to be taught this
#: one? Nothing else in the repository asks that question, and the twelve days
#: in INC-2026-10-24-the-short-edition-was-handed-an-editorial-judgment are
#: what not asking it looks like.
SHORT_ANSWERS = {
    "no-title": "A title on the first line",
    "date-in-title": "The title carries no",
    "internal-vocabulary": "claim graph",
    "typesetter-punctuation": "plain ASCII",
    "slop-lexicon": "sound important",
    "ends-on-citation": "before the close",
    # Cannot fire. The short edition prints no section headings, so the
    # generator's slot labels have nowhere to appear.
    "skeleton-heading": None,
    # Cannot fire. Guarded by `kind == "daily"` and this edition is a weekly.
    "daily-too-short": None,
}


def blockrules():
    """Every rule the press blocks on is answered in the short generator.

    The short edition is the one the press prints when no model can take the
    full issue, and `weekly.print_issue` hands it to `hold_for_quality` with
    `rewrite=None`. The full edition gets a second draft on a blocking finding.
    This one does not. So a block on the short edition is not a worse issue, it
    is a held issue and a week with no issue at all, which is the outage the
    short edition was built to answer.

    That makes the pre-send gate's BLOCK list the one mechanical answer to the
    question `pipeline/budget.py` left open in its own comment, that 103 ban
    list entries do not fit in a request this size and choosing which survive
    is an editorial judgment. A rule that can hold the issue survives. The
    judgment is still this seat's, and this gate is where it is recorded.

    Two findings, and neither is a reading. A rule the pre-send gate blocks on
    with no row here is unruled, and a row whose phrase has left the short
    prompt is a rule that was answered once and is not answered now.
    """
    rc = 0
    if not PRESEND.exists() or not SHORT.exists():
        print(f"  {PRESEND.name} or {SHORT.name} is missing")
        return 1
    rules = sorted(set(BLOCK_RULE.findall(PRESEND.read_text())))
    short = SHORT.read_text()
    print(f"  rules the pre-send gate blocks on             {len(rules)}")

    unruled = [r for r in rules if r not in SHORT_ANSWERS]
    print(f"  of those this seat has never ruled on         {len(unruled)}")
    for r in unruled:
        print(f"    UNRULED    {r}  (block on the short edition holds the issue)")
        rc = 1

    inert = [r for r in rules if SHORT_ANSWERS.get(r) is None
             and r in SHORT_ANSWERS]
    print(f"  of those that cannot fire on this edition     {len(inert)}")

    missing = [(r, SHORT_ANSWERS[r]) for r in rules
               if SHORT_ANSWERS.get(r) and SHORT_ANSWERS[r] not in short]
    print(f"  of those the short prompt no longer answers   {len(missing)}")
    for r, phrase in missing:
        print(f"    DROPPED    {r}  expected {phrase!r} in {SHORT.name}")
        rc = 1

    stale = [r for r in SHORT_ANSWERS if r not in rules]
    print(f"  rows here for a rule the gate no longer has   {len(stale)}")
    for r in stale:
        print(f"    STALE      {r}  is not a BLOCK rule in {PRESEND.name}")
        rc = 1

    if not rc:
        print()
        print("  Every rule that can hold the short edition is answered in")
        print("  the prompt that writes it. A new BLOCK rule in the pre-send")
        print("  gate fails this check until this seat rules on it.")
    return rc


#: The generator's ABSOLUTE rules, each with the phrase in `prompts/digest.md`
#: that states it and the pre-send BLOCK rule that can hold an issue breaking
#: it. `None` in the third position is the finding: a rule the file states with
#: no budget and nothing between it and a reader.
#:
#: Absolute and not merely stated, because the whole file is rules and a list of
#: all of them is a list of the file. A row belongs here when the generator
#: gives it a target of zero, or a number with no budget attached to it, or says
#: "never", or the canon numbers it a law and the owner has ruled on it twice.
#: The phrase is quoted so a row cannot outlive the rule it describes, which is
#: `blockrules`' technique and the reason that pass catches a dropped rule.
#:
#: "A number with no budget attached to it" was added on 2026-11-08 and the
#: clause it replaced read "a target of zero". That wording is why this table
#: missed law 14's fourth count for as long as it has existed: the rule's
#: target is three rather than zero, so the one sweep in this file written to
#: find a rule with nothing between it and a reader could not admit it. A
#: criterion that only sees zero is a criterion that cannot see "past three",
#: and the count it could not see is the one the grade of 2026-11-08 named as
#: the newest edition's single biggest weakness. The denominator moves from 11
#: to 12 and the ungated count from 5 to 6, so a figure a grade printed before
#: this date is not comparable to one printed after it (ban list 120's class).
ABSOLUTE_RULES = (
    ("the semicolon",
     "Count the semicolons. The target is zero and there is no budget",
     None),
    ("the em dash",
     "the same as the em\n  dash",
     None),
    ("law 8, the link reaches the full text",
     "Links reach the full text, never the landing page",
     None),
    ("law 8, every item carries its link",
     "Every item in every section carries its own\n  link",
     None),
    ("law 14, a list and a written turn",
     "Sections running past four paragraphs with no\n  written turn in them",
     None),
    # The pre-send gate carries a `bare-number` WARN, which is the
    # generator's EIGHTH count and a different rule: a figure with no
    # comparison beside it. Nothing there counts figures per paragraph, so
    # `None` here is measured rather than assumed, and `figures` in this file
    # is the reference implementation the ask names.
    ("law 14, three numbers in the heaviest paragraph",
     "Numbers in\n  the heaviest paragraph: past three",
     None),
    ("law 12, the framework's names are never printed",
     "no part announces itself with a label",
     "skeleton-heading"),
    ("the date is not in the title",
     "The date does NOT belong in this line",
     "date-in-title"),
    ("ban list 1, the slop lexicon",
     '"Delve", "landscape" and "realm"',
     "slop-lexicon"),
    ("plain ASCII",
     "The one exception is a",
     "typesetter-punctuation"),
    ("the internal vocabulary stays inside",
     "says a payload key out loud",
     "internal-vocabulary"),
    ("an item never ends on its citation",
     "The last sentence of an item is not available",
     "ends-on-citation"),
)


def ungated():
    """Which of the generator's absolute rules the press can actually hold.

    `blockrules` asks this question in one direction, whether every rule the
    pre-send gate blocks on is answered in the prompt that writes the short
    edition. Nothing has ever asked it in the other direction, and the other
    direction is where the issues go out wrong: a rule the generator states
    with a target of zero and no budget, with nothing in the pipeline able to
    stop the send, is enforced at the reliability of a model reading a long
    file, which is L-A22 in one sentence.

    This run's grade is the argument for the pass. Every live defect in the
    current edition is a rule `prompts/digest.md` already states in its most
    explicit available form.

    * Law 8's link rule is bolded, carries a worked `abs` to `html` example
      with a version suffix on it, and warns about coverage in the same
      bullet. 2026-W42 printed ten links, nine to the abstract, and arXiv
      serves the full text for seven of those nine.
    * Law 1's semicolon rule states the target twice, and the second statement
      names the precise construction, "two finished sentences in a balanced
      contrast", from the eight that printed in 2026-W40. 2026-W42 printed two
      and both are that construction.

    Neither rule is unclear and neither is missing. Both have now failed
    through prompt wording more than twice, which is the line the writer
    charter's structure watch draws, and on the far side of that line the fix
    is a gate rather than a sentence. The pre-send gate blocks on eight rules.
    Two of them are the exotic typesetting characters and the semicolon and the
    em dash are not among them, so the mark the generator says has no budget
    passes the only gate standing between the press and a reader.

        python3 docs/voice/check_voice.py ungated
    """
    rc = 0
    gen = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    if not gen or not PRESEND.exists():
        print(f"  {GENERATOR.name} or {PRESEND.name} is missing")
        return 1
    blocks = set(BLOCK_RULE.findall(PRESEND.read_text(encoding="utf-8")))
    print(f"  absolute rules in {GENERATOR.name}            "
          f"{len(ABSOLUTE_RULES)}")
    print(f"  BLOCK rules in {PRESEND.name}      {len(blocks)}")
    dropped = [(n, q) for n, q, _ in ABSOLUTE_RULES
               if " ".join(q.split()) not in " ".join(gen.split())]
    print(f"  rows whose rule has left the generator        {len(dropped)}")
    for name, quote in dropped:
        rc = 1
        print(f"    STALE      {name}: {quote!r} is not in {GENERATOR.name}")
    held = [(n, g) for n, _, g in ABSOLUTE_RULES if g and g in blocks]
    phantom = [(n, g) for n, _, g in ABSOLUTE_RULES if g and g not in blocks]
    open_rules = [n for n, _, g in ABSOLUTE_RULES if not g]
    print(f"  of those the press can hold                   {len(held)}")
    for name, gate in held:
        print(f"    HELD       {name}  ->  {gate}")
    print(f"  rows naming a gate the pre-send gate lacks    {len(phantom)}")
    for name, gate in phantom:
        rc = 1
        print(f"    PHANTOM    {name}  ->  {gate} is not a BLOCK rule")
    print(f"  of those nothing can hold                     {len(open_rules)}")
    for name in open_rules:
        rc = 1
        print(f"    UNGATED    {name}")
    print()
    print("A rule with a target of zero and no gate is enforced by a model")
    print("reading a long file, which is the condition L-A22 names. Each")
    print("UNGATED row above is a rule the generator states absolutely and")
    print("the press cannot refuse, and every one of them has printed.")
    return rc


#: The paragraph of `prompts/digest.md` that bans the slot name in its
#: reader-facing dress, found by its own sentences rather than by a line
#: number, because a line number in a gate is a gate that lies after the next
#: edit. A banned phrasing inside this span is the ban quoting its specimen.
SLOT_BAN_OPEN = "The ban is on the slot's IDEA and not on four strings"
SLOT_BAN_CLOSE = "first job is to say which section the reader is in"

#: The phrasings the ban names, read out of the ban itself. Not a second list:
#: a hand-kept copy of a list the file already holds is the next thing to
#: drift, which is this entry's own class one level up.
SLOT_DRESS = re.compile(r'"(what [a-z ]+)"')

#: A SERIES of slot-shaped phrases, which is the shape that printed and is
#: what separates the specimen from ordinary English. The generator says
#: "what changed, with its number" and "the reader who wants to check what
#: changed" in the course of teaching an item's spine, and a gate that fires
#: on those is a gate somebody deletes. Two or more of these phrases in one
#: comma series is a list of the issue's slots and has no other reading.
SLOT_SERIES = re.compile(
    r"what (?:is |are |to |)[a-z]+(?:ed|ing|s|n)?\b(?:[^.]{0,40}?,\s*"
    r"(?:and\s+)?what (?:is |are |to |)[a-z]+(?:ed|ing|s|n)?\b)+")

#: What `slotwords` has to get right, as data rather than as a test file, for
#: the reason `STANDS_ALONE_CASES` gives. The first two are the specimens that
#: were standing in `prompts/digest.md` when this gate was written and they are
#: quoted from it. The third is the sign-off's own three questions, a series of
#: the same grammar naming nothing the ban names, and a gate tuned only against
#: the specimens fires on it.
SLOT_CASES = (
    (True, "Four slots, her order, same as Monday: what gained ground, what is "
           "genuinely new, what fell behind, what to read yourself."),
    (True, "what is gaining ground supports it, what is new tests it, what "
           "fell behind is the position it replaces."),
    (False, "what you would watch next, what is still unsettled, what this "
            "leaves a builder holding"),
    (False, "Then what changed, with its number and the institution behind it."),
    (False, "the reader who wants to check what changed has to"),
)


def slot_series(text, dress):
    """Every series of slot-shaped phrases in `text` that names a banned one."""
    flat = " ".join(text.split())
    return [m for m in SLOT_SERIES.findall(flat)
            if any(d in m.lower() for d in dress)]


def slotwords():
    """Does the generator write the heading it bans, anywhere outside the ban?

    Ban list 143. The file's own bold sentence says "the words that beat it
    came out of this file", and the run that wrote that sentence banned five
    phrasings and never swept the file for them. Two specimens were standing
    when this pass was written, 1,176 lines apart at the furthest, and two of
    2026-W40's three printed headings are one of them word for word.

    What it reads is a SERIES and not a phrase, because the phrase alone is
    ordinary English in this file four times over and the series is a list of
    the issue's slots with no second reading. The phrasings themselves come out
    of the ban's own quoted list, so this cannot drift from the rule the way a
    hand-kept copy would.

        python3 docs/voice/check_voice.py slotwords
        git show origin/main:prompts/digest.md | python3 -c ...   # the proof
    """
    if not GENERATOR.exists():
        print(f"  {GENERATOR.name} is missing")
        return 1
    text = GENERATOR.read_text(encoding="utf-8")
    start, end = text.find(SLOT_BAN_OPEN), text.find(SLOT_BAN_CLOSE)
    if start < 0 or end < 0:
        print("  the ban paragraph is not where its own sentences say it is")
        print(f"    opening found {start >= 0}, closing found {end >= 0}")
        print("  Nothing below was read, because the scope of this pass is")
        print("  that paragraph and a guess at it is not a scope.")
        return 1
    dress = sorted(set(SLOT_DRESS.findall(text[start:end])))
    wrong = [(want, case) for want, case in SLOT_CASES
             if bool(slot_series(case, dress)) is not want]
    for want, case in wrong:
        print(f"  BROKEN  the detector is {'missing' if want else 'firing on'}"
              f" a case it is asserted against")
        print(f"            {case[:84]}")
    if wrong:
        print()
        print("SLOT_CASES says what this pattern has to do. Nothing below was")
        print("read, because a detector failing its own cases reports a clean")
        print("generator for the wrong reason.")
        return 1
    print(f"  the detector's own cases       {len(SLOT_CASES)} pass")
    print(f"  phrasings the ban names        {len(dress)}: "
          f"{', '.join(repr(d) for d in dress)}")
    outside = text[:start] + text[end:]
    hits = slot_series(outside, dress)
    print(f"  slot series outside the ban    {len(hits)}")
    for h in hits:
        print(f"    FAIL    {h[:92]}")
    if not hits:
        print("  the file writes the banned dress only where it bans it")
    print()
    print("A rule that bans a phrase and then writes it has handed the model")
    print("the specimen at the position where a heading gets drafted, which")
    print("is the family ban list 100 belongs to. The ban is not the fix.")
    print("The sweep is.")
    return 1 if hits else 0


#: What `slot_heading` has to get right. The first four are the headings the
#: product serves today, which is the only reason this gate exists. The rest
#: are the four best headings `2026-W42` printed, because a detector that fires
#: on one of those is a detector somebody deletes within a week.
#: Fields: (fires, the heading as it is printed)
SLOT_HEADING_CASES = (
    (True, "## What to read"),
    (True, "## What fell behind: the assumptions that let agents run unchecked"),
    (True, "## What is gaining ground: recursive self-improvement with fewer "
           "guardrails"),
    (True, "## What is genuinely new: where memory lives and who can pull the "
           "plug"),
    (False, "## Budget-constrained agents can now improve their own harnesses"),
    (False, "## How you show skills to an agent beats how you find them"),
    (False, "## Self-evolved skills beat human curation when the verifier is "
            "specific"),
    (False, "## Hidden reasoning can be encrypted, not merely hidden"),
    # The second form of the read slot, which is the one the generator teaches
    # and `2026-W39` and `2026-W40` both printed. It opens on the same word and
    # it names the day's list rather than the act of listing.
    (False, "## Three papers for anyone wiring memory or kill switches into "
            "production"),
    (False, "## What to read if you have one hour"),
    # The specimen that found the equality bug. `2026-W44` served this on
    # 2026-11-08 and this gate read OK, because 'what to read yourself' is not
    # 'what to read' and nothing here was looking at prefixes. It is the
    # framework's own internal name for the slot, which law 9 writes as "Read
    # these yourself", so it is the one dress the ban could least afford to
    # miss.
    (True, "## What to read yourself"),
    # The same evasion with a standing time adverbial instead of a reflexive.
    # Neither remainder is about the day, which is the whole test.
    (True, "## What is new this week"),
    # And the boundary that keeps this from eating the slot: a remainder that
    # is a reader's condition is material, so it passes exactly as the bare
    # second form above does.
    (False, "## What to read when the week has been long"),
)


#: Remainders that add nothing a reader could date. A banned phrasing followed
#: only by these is the banned phrasing wearing a suffix, which is how
#: `2026-W44` served the reading slot's own internal name past an equality
#: test. Kept small on purpose: the moment a word here could carry the day's
#: material, this reading starts firing on the headings law 12 wants.
SLOT_INVARIANT = frozenset((
    "yourself", "yourselves", "myself", "ourselves",
    "this", "week", "today", "now", "again", "so", "far",
    "month", "year", "issue", "edition",
))


def slot_heading(heading, dress):
    """Why one printed heading is a framework name, or the empty string.

    Two readings and both are quoted law rather than taste.

    The first is the ban's own list, read out of `prompts/digest.md` by
    `SLOT_DRESS` so it cannot drift from the rule: a heading that IS one of
    those phrasings, or that wears one as the label before a colon, is the
    internal name printed. `2026-W42` serves `## What to read`.

    The second reading is the PREFIX, and it is here because equality was the
    whole test until 2026-11-08. `2026-W42` served `## What to read`, the ban
    gained that phrasing in `97de5c8b`, and `2026-W44` served `## What to read
    yourself`, which this gate passed. One trailing word walked past a list the
    product had just been patched to hold, so the list is not where this can be
    held: the phrasing plus a remainder that would be true of every issue is
    the phrasing. `SLOT_INVARIANT` is that remainder and it is deliberately
    tiny, because a remainder carrying the day's material is the heading law 12
    asks for and firing on it would delete this gate within a week. Note what
    this still is, so the next run does not read it as the cure: a closed list
    one level up. The structural answer is in `docs/ideas.md` and it is the
    press composing or refusing this heading the way `ensure_fresh_title`
    already refuses a reused title.

    The third is the colon. Law 12's text says a paraphrase of a banned
    heading is the banned heading, and the generator says in its own words that
    a colon does not launder it. A heading that opens on `What` and then breaks
    to a colon is the slot label with the day's news bolted behind it, which is
    the construction `2026-W40` serves three times. The shape is the finding
    and no list of phrasings can hold it, because the laundered label is
    written fresh each time: `gaining ground` and `genuinely new` are in no
    list anybody keeps.

    What this deliberately does not fire on is a heading that opens on `What`
    and makes a claim. `## What to read if you have one hour` is the generator's
    own worked answer for this slot and it has to pass.
    """
    text = heading.lstrip("#").strip().strip("*_")
    low = text.lower().rstrip(" .")
    label = low.split(":", 1)[0].strip() if ":" in low else low
    for d in dress:
        if label == d:
            return f"the ban's own phrasing, {d!r}"
    for d in dress:
        if label.startswith(d + " "):
            rest = label[len(d):].strip()
            if all(w in SLOT_INVARIANT for w in rest.split()):
                return (f"the ban's own phrasing, {d!r}, plus {rest!r}, which "
                        f"is true of every issue")
    if ":" in low and low.startswith("what "):
        return f"a slot label laundered by a colon, {label!r}"
    return ""


def slotheads(paths=None):
    """Does an ISSUE print the heading the generator bans? Ban list 143's other half.

    `slotwords` asks this of `prompts/digest.md` and answers it well. Nothing
    asked it of the artifact. On 2026-11-01 the previous run of this seat found
    that the pre-send gate's heading ban and the canon's share no phrase at all,
    measured the cost at four live headings, and routed the repair to the
    engineer because `tools/` is pipeline code and this seat may not write it.
    That routing is right and the proposal is still `proposed`.

    What it left is this seat's own instrument, which could not name any of the
    four either. `slotwords` reads the generator and never an issue. `measure`
    prints every heading carrying a colon and that print does not reach its exit
    code, because that code means the character gate and a second meaning on one
    return value is L-A44. So the one ruling the owner has given twice, the
    second time in capitals, had no command that returns a verdict on an
    artifact, and `## What to read` is serving right now.

    A count without a verdict is what let the other two print. This is the
    verdict, on this seat's surface, today, rather than after a deploy.

        python3 docs/voice/check_voice.py slotheads --live
    """
    if not GENERATOR.exists():
        print(f"  {GENERATOR.name} is missing")
        return 1
    gen = GENERATOR.read_text(encoding="utf-8")
    start, end = gen.find(SLOT_BAN_OPEN), gen.find(SLOT_BAN_CLOSE)
    if start < 0 or end < 0:
        print("  the ban paragraph is not where its own sentences say it is")
        print("  Nothing below was read, because the phrasings come out of")
        print("  that paragraph and a guess at it is not a list.")
        return 1
    dress = sorted(set(SLOT_DRESS.findall(gen[start:end])))
    wrong = [(fires, case) for fires, case in SLOT_HEADING_CASES
             if bool(slot_heading(case, dress)) is not fires]
    for fires, case in wrong:
        print(f"  BROKEN  the detector is {'missing' if fires else 'firing on'}"
              f" a case it is asserted against")
        print(f"            {case[:84]}")
    if wrong:
        print()
        print("SLOT_HEADING_CASES says what this pass has to do. Nothing below")
        print("was read, because a detector failing its own cases reports a")
        print("clean issue for the wrong reason.")
        return 1
    print(f"  the detector's own cases       "
          f"{len(SLOT_HEADING_CASES)} pass")
    print(f"  phrasings the ban names        {len(dress)}: "
          f"{', '.join(repr(d) for d in dress)}")
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    rc = 0
    for raw in paths:
        path = pathlib.Path(raw)
        if not path.exists():
            print(f"  {shown_path(path)}: missing")
            rc = 1
            continue
        if path.stem in retired:
            print(f"  SKIP    {shown_path(path)}  retired, not served")
            continue
        heads = re.findall(r"^#{1,6} .*$", path.read_text(encoding="utf-8"),
                           re.M)
        hits = [(h, why) for h in heads
                for why in [slot_heading(h, dress)] if why]
        if not hits:
            print(f"  OK      {shown_path(path)}  {len(heads)} heading(s), "
                  f"none of them a framework name")
            continue
        rc = 1
        for h, why in hits:
            print(f"  FAIL    {shown_path(path)}  {h.strip()[:68]}")
            print(f"            {why}")
    print()
    print("Canon law 12 and incident 20. The framework's internal names are")
    print("never printed, and she has ruled it twice because the first ruling")
    print("reached the register and not the artifact. Strike the label and the")
    print("colon, and check whether what is left is the heading.")
    return rc


#: The words this canon and this generator use for their OWN instruments. Kept
#: to three, and each one earns its place from a specimen rather than from a
#: worry: `2026-W42` printed all three as colon labels in one edition. A longer
#: list would start catching the reader's own nouns, and "the practical
#: consequence" is the reader's.
APPARATUS = ("grade", "procedure", "evidence")

#: What `apparatus_label` has to get right. The true cases are the four
#: `2026-W42` printed. The false cases are the colons of the same edition that
#: are doing honest work, because a detector that reddens those is a detector
#: the next run deletes.
#: Fields: (fires, the segment as it is printed)
APPARATUS_CASES = (
    (True, "The grade: one platform, one model family, five benchmarks, no "
           "replication outside the group yet."),
    (True, "The procedure is extractable: agents submit training configs, "
           "query checkpoints through an OpenAI-compatible gateway."),
    (True, "The procedure is clean: retrieve top-50 candidates, expose only "
           "metadata, allow LOAD_SKILL actions during reasoning."),
    (True, "The procedure runs: sample an initial skill bundle, execute in "
           "environment, initialize test suite from instruction."),
    (False, "This week the field drew a hard line: one camp treats skills as "
            "retrieved documents, the other as living code."),
    (False, "Their fix is Progressive Disclosure: show the agent only skill "
            "names and descriptions, let it request the full content."),
    (False, "A separate team at Fudan, NUS, and Cardinal AI Lab built "
            "SkillDAG, which goes further: skills live in a typed graph."),
    (False, "The practical consequence: if your safety argument assumes exact "
            "reproducibility, you are running on a narrower guarantee."),
    # The grade written the way the generator asks for it. A clause inside a
    # sentence that is also carrying a fact, with no colon anywhere.
    (False, "Nobody outside the group has run it again, and the gains held "
            "across all five benchmarks."),
)

#: The segment before a colon, and the apparatus noun has to be its SUBJECT.
#: Anchored at the segment's own start so "a hard line" and "goes further" do
#: not reach it, and capped at four words so a sentence that happens to use the
#: word somewhere before a legitimate colon is not swept in.
APPARATUS_LABEL = re.compile(
    r"(?:^|(?<=[.!?]\s))\s*(?:\*\*|\*|_)?the\s+(" + "|".join(APPARATUS) +
    r")\b(?:\s+\w+){0,2}?\s*:", re.I)


def apparatus_label(segment):
    """Why one printed segment is the apparatus wearing a colon, or "".

    Ban list 149. The generator already bans this shape twice and reaches
    neither instance of it, for two different reasons, and the reasons are
    worth keeping together because they are why a rule stated twice shipped
    four violations in one edition.

    The grade's rule says the grade is a clause inside a sentence and names
    the shape that keeps shipping instead, which is "a sentence of its own, in
    one frame". A verbless colon fragment is neither of those things by the
    letter, so the rule describes two dresses and the artifact wore a third.

    The procedure's rule says the list is the shape and not a suggestion, and
    the version that names these three specimens by name is queued behind the
    deploy rather than live.

    And the heading gate, which is the one thing in the file that collects
    labels, collects lines beginning with `#` and runs of bold or italic
    sitting ALONE on a line. All four specimens sit mid-paragraph after a full
    stop, so the gate written to catch a label cannot see a label in the one
    position the prose actually puts it.
    """
    hit = APPARATUS_LABEL.search(segment)
    if not hit:
        return ""
    # The span and not the line. All four specimens sit mid-paragraph, so a
    # finding quoted from the line's first characters quotes a sentence that
    # is not the defect, which is ban list 91's rule applied to an excerpt.
    found = segment[hit.start():hit.end() + 48].strip()
    return (f"the apparatus wearing a colon, {hit.group(1).lower()!r}, and the "
            f"reader reads a label where a sentence was owed\n"
            f"            found   {found!r}")


def apparatus(paths=None):
    """Does an ISSUE print this canon's own instruments as colon labels?

    Canon law 7 is the law underneath it. The issue never narrates its own
    method, and the three nouns here are the method's: `grade` is what the
    evidence law does, `procedure` and `evidence` are payload fields the
    vocabulary rule forbids saying out loud. A reader who meets "The grade:"
    in a paragraph has been handed the name of an apparatus they did not know
    existed, in the place where a sentence was owed.

    Why it is a pass of its own rather than a line in `marks` or `slotheads`.
    `slotheads` reads headings, and a heading is a line. `marks` reads two
    punctuation marks and counts them. This reads sentence-internal position,
    which is the thing both of those are structurally unable to see, and
    position is the whole finding: the same four fragments at the start of a
    line would have been caught by the generator's own heading gate before the
    issue ever rendered.

        python3 docs/voice/check_voice.py apparatus --live
    """
    wrong = [(fires, case) for fires, case in APPARATUS_CASES
             if bool(apparatus_label(case)) is not fires]
    for fires, case in wrong:
        print(f"  BROKEN  the detector is {'missing' if fires else 'firing on'}"
              f" a case it is asserted against")
        print(f"            {case[:84]}")
    if wrong:
        print()
        print("APPARATUS_CASES says what this pass has to do. Nothing below was")
        print("read, because a detector failing its own cases reports a clean")
        print("issue for the wrong reason.")
        return 1
    print(f"  the detector's own cases       {len(APPARATUS_CASES)} pass")
    print(f"  the instrument nouns           "
          f"{', '.join(repr(a) for a in APPARATUS)}")
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    rc = 0
    for raw in paths:
        path = pathlib.Path(raw)
        if not path.exists():
            print(f"  {shown_path(path)}: missing")
            rc = 1
            continue
        if path.stem in retired:
            print(f"  SKIP    {shown_path(path)}  retired, not served")
            continue
        hits = []
        for number, line in enumerate(
                path.read_text(encoding="utf-8").split("\n"), 1):
            if line.startswith("#"):
                continue
            why = apparatus_label(line)
            if why:
                hits.append((number, line, why))
        if not hits:
            print(f"  OK      {shown_path(path)}  no instrument wearing a colon")
            continue
        rc = 1
        for number, line, why in hits:
            print(f"  FAIL    {shown_path(path)}:{number}  "
                  f"{line.strip()[:68]}")
            print(f"            {why}")
    print()
    print("Canon law 7, and the generator bans this shape twice without")
    print("reaching it. Write the sentence whole: the grade is a clause inside")
    print("a sentence doing other work, and a procedure is a list.")
    return rc


#: The seventeen cases `past_tense_you` has to satisfy, as data rather than as
#: a test file. `tests/` is the engineer's surface and this seat's is
#: `docs/voice/`, and a first draft of this gate put them in
#: `tests/test_voice_standalone.py`, where `tests/test_ci_coverage.py` correctly
#: answered that no workflow runs it. Here they run every time the gate runs,
#: which is strictly more often, and they need no workflow edit this seat is
#: not allowed to make.
#:
#: Both halves matter. A pattern tuned only against its false positives stops
#: catching the sentence the owner struck, and a pattern tuned only against her
#: specimens fires on a standing heading. The first two CLAIMS are the openings
#: she struck and the one that shipped with her ruling already in the prompt.
STANDS_ALONE_CASES = (
    (True, "You spent last week watching agents get faster by doing less."),
    (True, "You have spent the week watching agents get faster by thinking less."),
    (True, "you have written the same retry logic three times"),
    (True, "You have shipped a dozen agents."),
    (True, "you had built the harness yourself"),
    (True, "you have done this before"),
    (True, "You were running agents overnight."),
    (True, "you have not shipped a single one"),
    (False, "What to read if you have one hour"),
    (False, "you have it in production"),
    (False, "you have ten agents running"),
    (False, "you have none of these"),
    (False, "You keep a dozen agents running."),
    (False, "if you have a minute"),
    (False, "you have two models to choose between"),
    (False, "The agent-building world has spent the week arguing about scaffolding."),
    (False, "Accelerate every builder and agent to frontier speed."),
)


# ---- routed ------------------------------------------------------------

#: A ledger entry nobody has acted on. `built`, `done`, `closed` and
#: `rejected` are settled. Everything else is a finding still waiting, and
#: re-filing one of those as new is what this gate is for.
LEDGER_SETTLED = ("built", "done", "closed", "rejected")

#: What counts as naming the defect rather than naming the machine. A SHOUTING
#: constant is the identifier of one thing, and a filename is the identifier of a
#: building. Measured on this repository the day the gate was written:
#: `check_digest_quality.py` appears in NINE unsettled ledger entries and
#: `INTENSIFIERS` in one, which is the entry that holds the defect. So the gate
#: reads constants and never paths.
IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]{3,}$")

#: A constant can still name a building. `NEON_RO_URL` is a credential every
#: seat's run touches and it sits in fifteen unsettled entries, so "the ledger
#: holds an entry mentioning it" says nothing about whether this finding is
#: filed. The first run of this gate reported all fifteen and the real finding
#: was two rows in the middle of them. A token this broad is reported and not
#: failed on, because the gate cannot tell which of fifteen a run meant, and a
#: check that guesses is one a run learns to skip.
TOO_BROAD = 2

#: Identifiers written in prose rather than in backticks that still name one
#: thing. Measured over the 687 unsettled entries in `docs/ideas.md` on
#: 2026-10-26, by the same test `IDENTIFIER` was measured by against paths,
#: which is how many unsettled entries each distinct token sits in:
#:
#:     an INC id        96 distinct, 74 in exactly one entry,  7 over TOO_BROAD
#:     `ban list N`     46 distinct, 34 in exactly one entry,  3 over TOO_BROAD
#:     `law N`          15 distinct,  4 in exactly one entry,  8 over TOO_BROAD
#:
#: So the first two name a defect and the third names a building. Law 15 sits
#: in THIRTEEN unsettled entries and law 12 in eight, which is worse than the
#: nine of `check_digest_quality.py`, the path this gate already refuses for
#: precisely that reason. Run 51 left this widening for the next run and named
#: "a law, a rule or a file path" as the three invisible classes. Two of those
#: three are rejected here on the measurement, and the class it did not name
#: is the one admitted.
TRACEABLE = re.compile(r"INC-\d{4}-\d{2}-\d{2}-[a-z0-9-]+"
                       r"|ban list(?: entry)? \d+", re.I)

#: The seats a finding can be handed to, which is every seat but this one plus
#: the two authorities above them.
SEATS = r"engineer|frontend|exo|pm|research|skill|owner|chair"

#: The sentences that say a finding is being handed to another seat. The first
#: version of this took five phrasings from the reviews that existed when the
#: gate was written, and five is not how many this seat uses. Measured over all
#: 55 reviews in `docs/voice/reviews` on 2026-10-26, 52 of them hand something
#: on and the five phrasings found 14. Everything below `in the ledger for the`
#: is the widening, and it takes the same measurement to 47 of 52.
#:
#: That recall number is why the widening is not cosmetic. `routed` reads only
#: the sections this pattern matches, so a phrasing it misses is a section the
#: gate never opens, and the `VACUOUS` report added in the same run as this
#: widening cannot fire on a file whose routing the pattern cannot see. The
#: specimen was this run's own review, which routed two findings and which the
#: five phrasings called a review that "routes nothing".
#:
#: The recurring forms the five missed, all of them live in this register:
#: "Filed in `docs/ideas.md`", "Filed, not patched", "filed rather than
#: anchored", "is filed as urgent", "The cause is the engineer's", "retiring it
#: is the frontend seat's call", and "not this seat's file to renumber".
ROUTING = re.compile(
    r"(?:fil|rout)(?:ed|es|ing) (?:rather than|and not|not) "
    r"(?:patched|anchored|fixed|acted)"
    r"|fil(?:ed|es|ing)(?:,| it| them)? (?:not|rather than) patched"
    r"|fil(?:ed|es|ing) (?:in|for) (?:the ledger|`?docs/ideas)"
    r"|fil(?:ed|es|ing) elsewhere"
    r"|fil(?:ed|es|ing) for the (?:" + SEATS + r")"
    r"|rout(?:ed|es?) (?:it |them |both )?to the (?:ledger|" + SEATS + r")"
    r"|(?:goes|go) to the (?:ledger|" + SEATS + r")"
    r"|in the ledger for the (?:" + SEATS + r")"
    r"|is the (?:" + SEATS + r")(?:\'s| seat\'s)"
    r"|(?:is|are) not this seat\'s"
    r"|escalat\w+ (?:rather than|in|to) ", re.I)


#: What `routed_tokens` must and must not pull out of a routing section. The
#: true cases are the two admitted classes on live specimens and the constant
#: this gate already read, which is the case that proves the widening took
#: nothing away. The false cases are the shapes the widening could have
#: bought. A law number, which the measurement above rejects as a building. A
#: path, which this gate has always refused for the same reason. And a ledger
#: heading, which a routing section names as its ESCAPE rather than as its
#: finding, and which therefore belongs to `acknowledged` and not here.
ROUTED_CASES = (
    (True, "filed in the ledger, and INC-2026-10-18-the-duplicate-candidate-"
     "register-is-not-in-the-charters-read-list is the fourth count",
     "INC-2026-10-18-the-duplicate-candidate-register-is-not-in-the-charters-"
     "read-list"),
    (True, "routed to the ledger. Ban list 140 carries the sweep.",
     "Ban list 140"),
    (True, "routed to the ledger, and ban list entry 93's unenforced half",
     "ban list entry 93"),
    (True, "routed rather than patched, about `INTENSIFIERS` matching \"very\"",
     "INTENSIFIERS"),
    (False, "routed to the ledger, because canon law 15 has no gate.",
     "law 15"),
    (False, "routed to the ledger, naming `pipeline/weekly.py` as the file.",
     "pipeline/weekly.py"),
    (False, "duplicates\n`2026-10-05 \u2014 Coverage of links and evidence "
     "grades is a pipeline gate, not a\nprompt rule`, which is this seat's",
     "2026-10-05 \u2014 Coverage of links and evidence grades is a pipeline "
     "gate, not a prompt rule"),
    # An identifier that wraps still comes out, because `TRACEABLE` is read
    # over normalised text. The backticked half of this reader is not: a span
    # is matched within one line. That costs nothing, because `IDENTIFIER`
    # forbids whitespace, so a span it matches cannot wrap by construction.
    (True, "filed in the ledger. INC-2026-09-30-branch-name-reuse-is-systemic\n"
     "is the entry.", "INC-2026-09-30-branch-name-reuse-is-systemic"),
)


#: What `ROUTING` must and must not read as handing a finding on. Every true
#: case is a sentence taken verbatim from a review in this register, and the
#: first five are forms the original five phrasings missed. The false cases are
#: the shapes that look like a route and are not: a finding this run FIXED, a
#: count of rulings in a gate's own output, and a sentence about this seat's own
#: file, which is the lane rather than a handoff.
ROUTING_CASES = (
    (True, "Filed in `docs/ideas.md` for the engineer, with the query fix."),
    (True, "Filed, not patched. For the engineer."),
    (True, "all 49 anchored entries, with 43 and 44 filed rather than anchored"),
    (True, "The cause is the engineer's, is filed as urgent, and is not "
     "restated here."),
    (True, "retiring it is the frontend seat's call, not this run's"),
    (True, "docs/agents/incidents.md, which is not this seat's file to "
     "renumber"),
    (True, "Law 8's form half goes to the engineer instead."),
    (True, "routed rather than patched, about `INTENSIFIERS`"),
    (False, "The procedure now renders as a list, which is the one prompt "
     "patch in this diff."),
    (False, "`check_voice.py taste` reports 31 rulings, 27 enforced and "
     "quoted."),
    (False, "The generator is this seat's own surface and the patch is here."),
)

#: What `entry_name` must strip and must keep. The first is run 51's entry,
#: the specimen that proved the matcher wrong. The last two are the shapes
#: that would break if the pattern were greedy or unanchored: a title whose
#: own words end in a parenthesis it needs, and a heading with no attribution
#: at all, which most of the older entries are.
NAME_CASES = (
    ("2026-10-05 — Coverage of links and evidence grades is a pipeline gate, "
     "not a prompt rule (writer seat)",
     "2026-10-05 — Coverage of links and evidence grades is a pipeline gate, "
     "not a prompt rule"),
    ("2026-10-26 — The rewrite is a substitution (writer seat, run 51)",
     "2026-10-26 — The rewrite is a substitution"),
    ("2026-10-24 — The outsider gate (law 12a) belongs in the pre-send pass",
     "2026-10-24 — The outsider gate (law 12a) belongs in the pre-send pass"),
    ("2026-09-24 — The quality gate passes the issue she rejected",
     "2026-09-24 — The quality gate passes the issue she rejected"),
)


def routed_cases():
    """Every case above, run before any review is read.

    `headless_cases` and `state_cases` are the precedent and the reason is the
    same: a detector that fails its own cases reports a clean diff for the
    wrong reason. This gate spent its whole life so far doing exactly that,
    and the proof is that run 51's review routed a finding and the gate found
    nothing in it to check.
    """
    bad = []
    for want, section, token in ROUTED_CASES:
        got = token in routed_tokens(section)
        if got != want:
            bad.append((want, token))
    for head, want in NAME_CASES:
        if entry_name(head) != want:
            bad.append((want, entry_name(head)))
    for want, line in ROUTING_CASES:
        if bool(ROUTING.search(line)) != want:
            bad.append((want, line))
    return bad


def routed_tokens(section):
    """What one routing section names that can be looked up in the ledger.

    Two classes, kept apart because they are matched differently. A constant
    is matched exactly, as this gate always has. A `TRACEABLE` identifier is
    matched case-insensitively over normalised text, because "ban list 140"
    wraps in a ledger body and this register capitalises it both ways.
    """
    out = {t.strip() for t in re.findall(r"`([^`\n]+)`", section)
           if IDENTIFIER.match(t.strip())}
    out |= {norm(m.group(0)) for m in TRACEABLE.finditer(norm(section))}
    return out


#: A ledger heading ends in its attribution, "(writer seat, run 51)" or
#: "(frontend seat, for the writer seat)", and that parenthetical is metadata
#: about who filed the entry rather than part of the entry's name. A run
#: naming an entry writes the title and drops it, which is what run 51 did:
#: it named "2026-10-05 — Coverage of links and evidence grades is a pipeline
#: gate, not a prompt rule" and the heading carries "(writer seat)" after it,
#: so an exact match on the heading said the entry had not been named. Matching
#: the name and not the attribution is why `routed` does not report that
#: review as a run that routed a finding blindly.
ATTRIBUTION = re.compile(r"\s*\([^()]*\)\s*$")

entry_name = lambda head: norm(ATTRIBUTION.sub("", norm(head)))


def ledger_entries(text=None):
    """`docs/ideas.md` as [(heading, body, status)], unsettled entries only."""
    text = text if text is not None else LEDGER_MD.read_text()
    out = []
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        lines = block.split("\n")
        head, body = lines[0].strip(), "\n".join(lines[1:])
        m = LEDGER_STATUS.search(body)
        status = (m.group(1) if m else "").lower()
        if status not in LEDGER_SETTLED:
            out.append((head, body, status or "none"))
    return out


def routed(ref=None):
    """A finding this run hands to another seat that the ledger already holds.

    Run 48 of this seat closed its review with a section called "Two findings
    in the engineer's file, routed rather than patched", about `INTENSIFIERS`
    matching the substring "very " and `TYPESETTER` enforcing four characters
    where the ban list is a class. Both findings were correct. Both had been
    filed on 2026-09-24, by this same seat, in
    "The quality gate passes the issue the owner rejected (writer seat, for the
    engineer)", status `proposed` ever since. The run did not name that entry,
    and its pull request appended nothing to the ledger either, so the output
    of the work was a second description of a thirty-day-old finding in a file
    the engineer does not read.

    That is the shape this register keeps recording: a register written to stop
    rediscovery whose only reader is the register.
    `INC-2026-10-18-the-duplicate-candidate-register-is-not-in-the-charters-read-list`
    is the fourth count of it and names the other three. This is the fifth and
    the first pointed at the ledger, and the reason is one line of a charter:
    the writer charter names seven files to read every run and `docs/ideas.md`
    is not among them, so a seat following its charter exactly files into a
    register it never opens.

    The fix that incident chose is the fix here, in its own words: a command
    the run types is better than a sentence the run reads. So the duty becomes
    a check over the run's own diff, beside `candidates`, which does the same
    job for copy candidates.

    The escape is the same too, and it is not a new rule. A run may route a
    finding the ledger already holds. It may not do so without naming the
    entry, because that is the difference between escalating a stale finding
    and not knowing it exists. Naming it is also what turns a re-file into the
    thing the org actually wants: `docs/agents/incidents.md` already requires a
    repeat to be escalated rather than filed a fourth time.

        python3 -I docs/voice/check_voice.py routed origin/main
    """
    ref = ref or "origin/main"
    bad = routed_cases()
    if bad:
        for want, token in bad:
            print(f"  CASE    wanted {want}: {token[:62]}")
        print("The token reader is broken and ROUTED_CASES says how. Nothing")
        print("below was read.")
        return 1
    print(f"  the token cases               {len(ROUTED_CASES)} pass")
    print(f"  the entry-name cases          {len(NAME_CASES)} pass")
    print(f"  the routing cases             {len(ROUTING_CASES)} pass")
    out = subprocess.run(["git", "diff", "--name-status", ref],
                         cwd=ROOT, capture_output=True, text=True)
    reviews = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2 or not parts[0].startswith("A"):
            continue
        path = parts[-1]
        if path.startswith("docs/voice/reviews/") and path.endswith(".md") \
                and (ROOT / path).exists():
            reviews.append(path)
    entries = ledger_entries()
    # The escape is read across the whole diff and not per file, because the
    # unit a run ships is a pull request. A review that routes a stale finding
    # and a second file in the same pull request that escalates it by name is
    # the org getting what it wants. Scoping the escape to the routing file
    # would instead ask a run to rewrite a graded review it is carrying from
    # an earlier run, and a grade is a dated record rather than a draft.
    # `added_lines` and not `git diff`, because a diff prefixes every line
    # with "+" and the headings in this register wrap. Normalising the raw
    # diff turns "passes the\n+  issue" into "passes the + issue", so an
    # escalation that names the entry correctly reads as not naming it. The
    # first run of this gate failed its own escalation that way.
    acknowledged = norm("\n".join(
        [(ROOT / r).read_text() for r in reviews]
        + [text for path, _, text in added_lines(ref)
           if path == "docs/ideas.md"]))
    # The entries this diff names anywhere, counted once. A routing section
    # that hands a finding on is doing the right thing when the run names the
    # entry it is not duplicating, and that naming may sit in the review or in
    # the ledger append beside it, which is why the scope is the whole diff.
    named = [h for h, _, _ in entries if entry_name(h) in acknowledged]
    clashes, broad, vacuous = [], [], []
    for path in reviews:
        body = (ROOT / path).read_text()
        if not ROUTING.search(body):
            continue
        # Only the sections that route. Run 48's review named `NEON_RO_URL`
        # four sections away, under "Honest limits of this grade", where it is
        # a fact about the runtime and not a finding being handed to anyone.
        # Reading the whole file made every mention of every constant a
        # routed finding, which is how the first run of this gate buried its
        # own two real rows under fifteen.
        sections = [s for s in re.split(r"(?m)^(?=#{2,}\s)", body)
                    if ROUTING.search(s)]
        tokens = {t for s in sections for t in routed_tokens(s)}
        # Vacuity is asked per file and the escape above is asked across the
        # diff, and the two scopes are not in tension. The escape answers "did
        # this run escalate by name", where the name may sit in the ledger
        # append. This answers "did the gate read anything at all in THIS
        # review", and one named entry in a second file is no evidence about
        # this one. Scoped diff-wide it never fires: the first review in the
        # diff to name an entry excuses every other review's routes.
        if not tokens and not [h for h, _, _ in entries
                               if entry_name(h) in norm(body)]:
            # The case this gate could not report, and the reason it is here:
            # zero checkable identifiers and no entry named is a pass that
            # verified nothing, printed in the same words as a pass that
            # verified something. That is incident 20's shape and it is the
            # bias run 51 found in `claims`, where the state a row LEAVES was
            # the state the gate read. A gate whose silence reassures is worse
            # than no gate, so this one says which silence it is.
            vacuous.append((path, len(sections)))
        for token in sorted(tokens):
            if TRACEABLE.fullmatch(token):
                held = [(h, st) for h, e, st in entries
                        if token.lower() in norm(e).lower()]
            else:
                held = [(h, st) for h, e, st in entries if token in e]
            if not held:
                continue
            if len(held) > TOO_BROAD:
                broad.append((path, token, len(held)))
                continue
            for head, status in held:
                if entry_name(head) in acknowledged:
                    continue
                clashes.append((path, token, status, head))
    print(f"  review files this diff adds   {len(reviews)}")
    for path in reviews:
        routes = "routes a finding" if ROUTING.search(
            (ROOT / path).read_text()) else "routes nothing"
        print(f"    {path}  ({routes})")
    print(f"  unsettled entries in docs/ideas.md   {len(entries)}")
    print(f"  entries this diff names               {len(named)}")
    for path, n in vacuous:
        print(f"  VACUOUS {path}")
        print(f"            {n} section(s) route a finding, no identifier the "
              f"ledger can be searched for, no entry named")
    for path, token, status, head in clashes:
        print(f"  FAIL    {path}")
        print(f"            routes `{token}`, which is already filed and "
              f"still {status}:")
        print(f"            {head[:88]}")
    for path, token, n in broad:
        print(f"  BROAD   {path}")
        print(f"            `{token}` sits in {n} unsettled entries, so it "
              f"names a machine rather than a finding")
    if not clashes and not vacuous:
        print("  no finding routed here is one the ledger already holds")
    print()
    print("A run may route a finding the ledger already holds. It may not do")
    print("so without naming the entry, because that is the difference")
    print("between escalating a stale finding and not knowing it exists.")
    # VACUOUS is reported and not failed on, the way BROAD is. The gate cannot
    # tell a run that routed nothing checkable from a run that routed a
    # finding this register has never held, and a check that guesses is one a
    # run learns to skip. What it can do is stop printing the all-clear.
    return 1 if clashes else 0


# ---- standalone --------------------------------------------------------


def standalone(paths=None):
    """Canon law 13's mechanical half, run over the issue instead of the prompt.

    `past_tense_you` is the grammar question the generator calls "the only one
    of these four that can be checked without judgment", and until this gate it
    had exactly one caller: `specimens`, which reads the two generator prompts.
    So the one hard voice law with a detector already written in this
    repository had never been pointed at the artifact a reader opens.

    It had been pointed at the prompt four times instead. `prompts/digest.md`
    carries the rule at the writing position, the four shapes at the gate, a
    worked repair, and a note that three specimens of it have shipped. The
    charter's step 4 says that when the same structural fix fails twice through
    prompt changes alone, the next fix belongs in the pipeline rather than in a
    third round of prompt-tinkering. By the prompt's own count this is past
    that line, so this run wrote no fifth paragraph.

    What the gate found on its first run is why the prompt was never the
    problem. `site/content/issues/2026-W39.md` opens on the shape, and the
    history says the owner's correction was made and then lost:

        396f4f1  2026-09-23  "You spent last week watching agents get faster
                             by doing less at test time."   <- she struck this
        b7d6929  2026-09-24  "The agent-building world has spent the week
                             arguing about scaffolding"     <- the repair, and
                             it is the exact sentence prompts/digest.md now
                             holds up as the model answer
        820df48  2026-09-29  "You have spent the week watching agents get
                             faster by thinking less at test time."

    The third commit is "2026-W39 is Monday's print (the digests record), not
    Thursday's preview". It replaced the file wholesale with what the press
    actually sent, which was right, and it discarded her correction, because
    the correction had only ever been written into the rendered archive and
    never into the record the archive is rendered from. Two later commits
    touched the same file and neither re-read the opening.

    So the generator is not what failed here and a fifth prompt paragraph would
    not have moved it. A correction applied downstream of the record is lost
    the next time the record renders, and the only thing that catches that is a
    command over the file the public reads. That is this.

    One open question about this gate's own verdict, recorded rather than
    decided. It FAILS on the archive, which is right if the archive is a
    product surface a reader opens. If the owner rules that
    `site/content/issues/` is a faithful record of what subscribers received,
    and `820df48` assumed exactly that, then a shipped issue carrying the shape
    is history rather than a defect, and this verdict should become a report
    while the pre-send gate keeps the failure. The ledger entry filed with this
    gate asks her that question.

    The tense only, deliberately. The generator lists four shapes and says
    three of them "need you to judge whether a reference is load-bearing". A
    literal search for "last week" would fire on "last week the field argued",
    which is a time reference about the research and not about our publishing,
    and a gate that cries on legitimate prose is one nobody keeps. The three
    judged shapes stay a reading, and this gate claims only the quarter it can
    prove.

        python3 -I docs/voice/check_voice.py standalone
    """
    wrong = [(want, span) for want, span in STANDS_ALONE_CASES
             if past_tense_you(span) is not want]
    for want, span in wrong:
        print(f"  BROKEN  the detector is {'missing' if want else 'firing on'}"
              f" a case it is asserted against")
        print(f"            {span}")
    if wrong:
        print()
        print("The pattern changed and STANDS_ALONE_CASES says how. Nothing")
        print("below was read, because a detector that fails its own cases")
        print("reports a clean archive for the wrong reason.")
        return 1
    print(f"  the detector's own cases   {len(STANDS_ALONE_CASES)} pass")
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    paths = [pathlib.Path(p) for p in paths]
    hits, exempt = [], []
    for path in paths:
        for n, span, _ in issue_sentences(path):
            if not past_tense_you(span):
                continue
            # Her own words are her fine-tuning and the charter says
            # refinements layer on top of it, never beside it. The exemption is
            # computed from her register for the reason the taste gate gives.
            (exempt if hers(span) else hits).append((path, n, span))
    # The scope line this pass used to work out for itself is `scope`'s now,
    # printed at the top with every other pass's. Its own version read the
    # source off a path prefix, which got `--live` wrong in both directions:
    # a live path is outside `site/content/issues` and is not a path the
    # caller named, and there was no third answer available to print.
    print(f"  sentences whose subject is 'you' and whose verb is past  "
          f"{len(hits) + len(exempt)}")
    for path, n, span in hits:
        print(f"  FAIL    {shown_path(path)}:{n}")
        print(f"            {span[:92]}")
    for path, n, span in exempt:
        print(f"  HERS    {shown_path(path)}:{n}  exempt, in taste.md")
    if not hits:
        print("  no issue tells a reader what they have been doing")
    print()
    print("Each hit is a claim about what the reader has done, it is not")
    print("knowable from here, and the repair is the present tense and the")
    print("reader's actual job rather than deletion. The generator's own")
    print("worked answer is the b7d6929 line quoted above.")
    return 1 if hits else 0


# ---- where an overturn says it came from -------------------------------

#: A phrase that points an overturn back at the work being overturned. The
#: generator's SOURCE test calls these the first of three dresses, and every
#: one of them has already told the reader that the two ends of the pairing
#: are one end. Matched as a span rather than a sentence subject, because the
#: shape that printed was a mid-sentence "The same paper also overturns".
BACKREFERENCE = re.compile(
    r"\b(?:the same (?:paper|work|study|team|authors|group)"
    r"|this (?:same )?(?:paper|work|study)"
    r"|the (?:same )?authors)\b[^.]{0,80}?"
    r"\b(?:also|further|likewise|additionally)\b|"
    r"\b(?:also|further|likewise)\b[^.]{0,40}?"
    r"\b(?:overturn|overturns|contradict|contradicts|refute|refutes|"
    r"upend|upends|overturned|contradicted)\b",
    re.I,
)

#: A verb of PRIOR belief. The thing this sentence attributes to its subject is
#: something that used to be true, so the subject is the overturned end of the
#: pairing. Where the subject also names a paper the section links, the two
#: ends are one end and no backreference phrase had to appear.
PRIOR_BELIEF = re.compile(
    r"^(?P<who>[A-Z][\w.-]*(?:\s+[A-Z][\w.-]*){0,3})\s+"
    r"(?:had (?:claimed|shown|held|reported|found|established|demonstrated)"
    r"|claimed|held)\b",
)

#: Words a title shares with every other title, so a subject matching one of
#: them is not evidence that the subject is that paper.
TITLE_NOISE = frozenset("""
a an and the for of in on at to with without via from by is are be
agent agents ai llm llms model models language large towards toward
benchmark benchmarks system systems learning self new scale scaling
""".split())

#: Each case is (how many findings, the markdown). They run before any artifact
#: is read, for the reason `SELFCHECK_CASES` was added on 2026-10-26: a
#: detector that has drifted reports a clean archive for the wrong reason, and
#: a provenance gate reporting clean is the exact sentence this seat has
#: already published three times.
PROVENANCE_CASES = (
    # The backreference, as it printed.
    (1, "## What fell behind\n\nThe same paper also overturns a companion"
        " claim that simple covert computation leaves no trace.\n"),
    # The linked work as the subject of a verb of prior belief.
    (1, "## What fell behind\n\nVosti had claimed bitwise-identical logits"
        " across all tested execution variations. New work shows otherwise.\n\n"
        "*Vosti: Specifying and Verifying Deterministic Inference* -"
        " [full text](https://arxiv.org/abs/2609.38981v1)\n"),
    # The same shape where the subject is NOT a work this section links. A
    # field-wide belief with no paper behind it is the legitimate form of a
    # fell-behind opening and the gate may not fire on it.
    (0, "## What fell behind\n\nThe field had claimed that scaffolding must run"
        " at inference. New work from Tsinghua shows otherwise.\n\n"
        "*Harness-Zero* - [full text](https://arxiv.org/html/2610.10310v1)\n"),
    # A named work as a prior belief, where the overturning paper is the one
    # linked and the overturned one is somebody else's. Two papers, no finding.
    (0, "## What fell behind\n\nAgora had claimed a hard ceiling on coding"
        " agents. New work shows otherwise.\n\n"
        "*Harness-Zero* - [full text](https://arxiv.org/html/2610.10310v1)\n"),
    # "also" near an overturn verb, in a sentence that names a second paper.
    # The gate reads the phrase and not the paper count, so this fires and the
    # case records that, rather than a later run discovering it as drift.
    (1, "## What fell behind\n\nA team at Fudan also overturned the claim"
        " that typed graphs do not scale.\n"),
)


def section_titles(lines):
    """The significant words of every paper title cited under each heading.

    Keyed by the heading line's index, so a subject is only ever compared to
    the works the reader meets in the same section. Comparing against the
    whole issue would fire on any section that cites a paper another section
    overturned, which is the ordinary case and the product.
    """
    out, head = {}, 0
    for i, raw in enumerate(lines):
        if raw.startswith("#"):
            head = i
            out.setdefault(head, set())
        if CITATION.match(raw):
            title = re.sub(r"\s*[-–]\s*\[.*$", "", raw.strip()).strip("* ")
            title = title.split(":")[0]
            words = {w.lower() for w in WORD.findall(title)}
            out.setdefault(head, set()).update(words - TITLE_NOISE)
    return out


def provenance_findings(body):
    """Every overturn in `body` whose own text says its two ends are one end.

    Two of the three dresses the generator's SOURCE test names. The third, the
    belief already standing in the draft as the citing paper's own result,
    needs the abstract and stays a reading in the claims pass's seventh
    question. This gate claims only the part it can prove, the way the
    stands-alone gate claims one shape of four.
    """
    lines = body.split("\n")
    titles = section_titles(lines)
    heads = sorted(titles)
    found = []
    for n, raw in enumerate(lines):
        if raw.startswith("#") or CITATION.match(raw):
            continue
        line = norm(re.sub(r"\]\([^)]*\)", "]", raw).replace("**", "")
                    .replace("*", "").replace("`", ""))
        if not line:
            continue
        here = max((h for h in heads if h <= n), default=None)
        mine = titles.get(here, set())
        for span in SENT.split(line):
            span = span.strip()
            if not span:
                continue
            if BACKREFERENCE.search(span):
                found.append((n + 1, "points back at the work it overturns",
                              span))
                continue
            m = PRIOR_BELIEF.match(span)
            if not m:
                continue
            who = {w.lower() for w in WORD.findall(m.group("who"))}
            shared = (who - TITLE_NOISE) & mine
            if shared:
                found.append((n + 1, "the work that held it is a work this "
                              f"section links ({', '.join(sorted(shared))})",
                              span))
    return found


def provenance(paths=None):
    """Two of the three shapes in which one paper overturns itself.

    The claims pass asks six questions about whether an issue is true and
    every one of them is answered by reading the issue. On 2026-10-26 the
    research seat read the live 2026-W42's overturn section against the two
    abstracts it cites and scored it three wrong out of three, seven days
    after it went live, and this seat's own grade of that same section the
    same morning had run all sixteen laws and the six passes over it and
    reported its prose.

    So the gap was never a wording. It was that no instrument in this
    repository had ever compared a statement in an issue to the source the
    issue says it came from. Most of that comparison needs the abstract and
    cannot be a command. Two of the three shapes do not, because the issue's
    own text has already said the two ends are one end, and those two are
    this.

    What it cannot see, said here rather than left for a later grade to
    discover. A pairing whose two papers are genuinely two papers and whose
    relation is still wrong is invisible here, and so is a figure belonging to
    a paper the section never names, which is the worst of the three. Both
    need the abstracts, both are the claims pass's seventh question, and a run
    that reads this gate's clean exit as a verdict on a section has made the
    mistake the section's own grade made.

        python3 -I docs/voice/check_voice.py provenance
        python3 -I docs/voice/check_voice.py provenance --live
    """
    wrong = [(want, md) for want, md in PROVENANCE_CASES
             if len(provenance_findings(md)) != want]
    for want, md in wrong:
        got = len(provenance_findings(md))
        print(f"  BROKEN  a case asserts {want} finding(s) and the detector"
              f" reports {got}")
        print(f"            {norm(md.splitlines()[2])[:88]}")
    if wrong:
        print()
        print("The pattern changed and PROVENANCE_CASES says how. Nothing")
        print("below was read, because a provenance gate reporting clean is")
        print("the sentence this seat has already published three times.")
        return 1
    print(f"  the detector's own cases   {len(PROVENANCE_CASES)} pass")
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    paths = [pathlib.Path(p) for p in paths]
    retired = hidden_weeks()
    hits = 0
    for path in paths:
        if not path.exists():
            print(f"  {path}: missing")
            continue
        off = path.stem in retired
        found = provenance_findings(path.read_text(encoding="utf-8"))
        tag = "   [retired, not served]" if off else ""
        print(f"  {path.stem}{tag}  {len(found)} finding(s)")
        for n, why, span in found:
            print(f"    FAIL  line {n}: {why}")
            print(f"          {span[:86]}")
        if not off:
            hits += len(found)
    print()
    print("One paper cannot overturn itself. Each hit is a sentence whose own")
    print("words name the overturned end as work this section cites, so the")
    print("repair is to drop the pairing rather than to reword it: the")
    print("relation is usually `refines` and the item belongs in the new work.")
    print("A clean exit is not a verdict on the section. The figure under the")
    print("wrong paper and the mislabelled two-paper edge both need the")
    print("abstracts, and they are the claims pass's seventh question.")
    return 1 if hits else 0


# ---- the editions a reader can actually open ---------------------------

#: The product's public address. Every pass below reads it with no credential,
#: which is the whole finding behind this section: `NEON_RO_URL` guards the
#: send record and nothing guards the pages that record renders into.
LIVE_SITE = os.environ.get("ALEXANDRIA_SITE", "https://libraryofalexandria.dev")

#: One cache directory per process, created on first use. Not a fixed name
#: under /tmp: twelve seats of this company run as one user on one host, so
#: `/tmp/editions` is a shared name and a concurrent seat's issue would be read
#: under this one's week number
#: (`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`).
_CACHE = None

#: `<a href="/library/2026-W42">` on the public index. The served list is the
#: product's own answer to which editions exist, and it is three where the
#: repository holds one.
LIVE_WEEK = re.compile(r'href="/library/(\d{4}-W\d{2})"')

#: The inverse of `site/lib/markdown.js` over the subset an issue uses. This is
#: proved rather than asserted: `editions` below un-renders the served copy of
#: an edition the repository also holds and diffs the two, so a change to the
#: site's renderer that this misses shows up as a failing round trip rather
#: than as a silently wrong grade.
_INLINE_OPEN = {"strong": "**", "b": "**", "em": "*", "i": "*", "del": "~~"}


class _Unrender(html.parser.HTMLParser):
    """Rendered issue HTML back to the markdown the press stored.

    The gates below are written against markdown, because the press writes
    markdown and `site/content/issues/*.md` is markdown. Re-deriving it from
    the page is what lets a gate read an edition nobody committed, which is
    every edition since 2026-10-05.
    """

    HEAD = {f"h{n}": "#" * n + " " for n in range(1, 7)}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.lists, self.counts = [], [], [], []
        self.href, self.pre = None, False

    def _flush(self):
        text = "".join(self.buf).strip()
        self.buf = []
        return text

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.pre, self.buf = True, []
            return
        if tag in _INLINE_OPEN:
            self.buf.append(_INLINE_OPEN[tag])
        elif tag == "code" and not self.pre:
            self.buf.append("`")
        elif tag == "a":
            self.href = dict(attrs).get("href")
            self.buf.append("[")
        elif tag == "br":
            self.buf.append("  \n")
        elif tag == "hr":
            self.out.append("---")
        elif tag == "ul":
            self.lists.append("ul")
        elif tag == "ol":
            self.lists.append("ol")
            self.counts.append(0)

    def handle_endtag(self, tag):
        if tag in _INLINE_OPEN:
            self.buf.append(_INLINE_OPEN[tag])
        elif tag == "code" and not self.pre:
            self.buf.append("`")
        elif tag == "a":
            self.buf.append(f"]({self.href})" if self.href else "]")
            self.href = None
        elif tag in self.HEAD:
            self.out.append(self.HEAD[tag] + self._flush())
        elif tag == "p":
            text = self._flush()
            if text:
                self.out.append(text)
        elif tag == "li":
            text = self._flush()
            if self.lists[-1:] == ["ol"]:
                self.counts[-1] += 1
                self.out.append(f"{self.counts[-1]}. {text}")
            else:
                self.out.append(f"- {text}")
        elif tag == "ul" and self.lists:
            self.lists.pop()
        elif tag == "ol":
            if self.lists:
                self.lists.pop()
            if self.counts:
                self.counts.pop()
        elif tag == "pre":
            self.pre = False
            self.out.append("```\n" + "".join(self.buf).strip("\n") + "\n```")
            self.buf = []

    def handle_data(self, data):
        self.buf.append(data)


def unrender(fragment):
    """The markdown behind one rendered `<article class="digest issue-body">`."""
    parser = _Unrender()
    parser.feed(fragment)
    parser.close()
    return "\n\n".join(parser.out).strip() + "\n"


def _fetch(url, timeout=25):
    """The page, or None and the reason printed. Never raises.

    A gate that throws on a slow network is a gate somebody deletes. A gate
    that returns a clean verdict on a network it never reached is the defect
    this whole section exists to repair, so the failure is loud and the caller
    is obliged to say it answered nothing.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"  UNREACHED {url}")
        print(f"            {type(e).__name__}: {e}")
        return None


def served_weeks():
    """The weeks the product serves, newest last, or None when unreached."""
    page = _fetch(f"{LIVE_SITE}/library")
    if page is None:
        return None
    return sorted(set(LIVE_WEEK.findall(page)))


#: One reading of the library per process. `_WEEKS` holds the answer and
#: `_WEEKS_READ` says whether it was asked, because `None` is a real answer
#: here and means unreached.
_WEEKS = None
_WEEKS_READ = False


def served_weeks_cached():
    """`served_weeks`, asked once however many passes want it.

    Eleven passes now state their scope and each of them needs to know what
    the product serves. Un-memoized that is eleven fetches of one page in one
    run, and eleven `UNREACHED` lines when the host has no network, which
    would bury the counts the run exists to print under its own plumbing.
    """
    global _WEEKS, _WEEKS_READ
    if not _WEEKS_READ:
        # A run that declared it cannot reach the product does not spend a
        # doomed request to be told so, and it does not print `UNREACHED`
        # over a blind spot it already owned up to. `editions` draws that
        # distinction already and this is the same one.
        _WEEKS = None if os.environ.get("ALEXANDRIA_OFFLINE") else served_weeks()
        _WEEKS_READ = True
    return _WEEKS


ARTICLE = re.compile(r'<article class="digest issue-body"[^>]*>(.*?)</article>',
                     re.S)


def served_issue(week):
    """One served edition as a markdown file on disk, or None when unreached."""
    global _CACHE
    if _CACHE is None:
        _CACHE = pathlib.Path(tempfile.mkdtemp(prefix="check_voice-editions-"))
    cached = _CACHE / f"{week}.md"
    if cached.exists():
        return cached
    page = _fetch(f"{LIVE_SITE}/library/{week}")
    if page is None:
        return None
    body = ARTICLE.search(page)
    if not body:
        print(f"  UNREADABLE {LIVE_SITE}/library/{week}")
        print( "             no <article class=\"digest issue-body\"> on the page,")
        print( "             so the route's markup moved and this parser is stale")
        return None
    cached.write_text(unrender(body.group(1)), encoding="utf-8")
    return cached


def served_paths():
    """Every served edition as a path, for the passes that take paths."""
    weeks = served_weeks_cached()
    if weeks is None:
        return None
    paths = [served_issue(w) for w in weeks]
    return [p for p in paths if p is not None]


def round_trip():
    """Is the un-renderer faithful? Asked of an edition we hold both copies of.

    The proof and not the claim. For every served week the repository also
    holds as a file, the served page is un-rendered and diffed against that
    file, ignoring blank lines and trailing space, which are the only things
    the render does not carry. A mismatch means a figure taken off the live
    page belongs to a document the press did not write, which is ban list 91
    with a longer fuse.
    """
    weeks = served_weeks_cached()
    if weeks is None:
        return None, []
    rows = []
    for w in weeks:
        on_disk = ROOT / f"site/content/issues/{w}.md"
        if not on_disk.exists():
            continue
        live = served_issue(w)
        if live is None:
            continue
        norm = lambda t: [x.rstrip() for x in t.split("\n") if x.strip()]
        rows.append((w, norm(on_disk.read_text(encoding="utf-8"))
                     == norm(live.read_text(encoding="utf-8"))))
    return True, rows


# No `paths` parameter, removed 2026-11-02. It had one, it was never read in
# the body, and `main` never passed it one either, so `editions <a path>`
# silently graded the global scope under the caller's argument. A parameter a
# gate accepts and ignores is the same promise ban list 91 is about.
def editions():
    """Does this file's default scope reach every edition a reader can open?

    The gate entry 141 needed and did not get. That entry closed the reading
    half of its class on the day it was written: a run now starts a grade by
    asking the press which week is newest. It left the commands alone, and
    eight passes in this file glob `site/content/issues/*.md` and print
    verdicts about "the issues". That directory holds two files, one of them
    retired, and the product serves three. So on the day the class was named
    and banned, every count in this file still described one edition out of
    three, and the two it could not see had never been read by any command or
    any review.

    What the blindness cost, and it is not hypothetical.
    `2026-W40` went to readers on 2026-10-05 and printed three headings:

        ## What is gaining ground: recursive self-improvement with fewer guardrails
        ## What is genuinely new: where memory lives and who can pull the plug
        ## What fell behind: the assumptions that let agents run unchecked

    Those are the framework's internal names, printed, which is canon law 12
    and incident 20, the one ruling the owner has had to give twice. `measure`
    has detected that exact shape since 2026-10-06. It never fired, because the
    edition was never a file here. A ruling given twice, a gate written for it,
    and a print that carried it anyway, all at once, because the gate's scope
    was the repository and the ruling's scope is the product.

    This pass fails on the gap itself rather than on any issue's prose, so the
    blindness is a red line somebody has to answer instead of a sentence in a
    docstring that the counts quietly contradict. `--live` on the passes that
    take paths is the way to answer it inside one run:

        python3 docs/voice/check_voice.py editions
        python3 docs/voice/check_voice.py devices --live
    """
    # The scope reading's cases are asserted here and not inside `scope`,
    # because eleven passes call that and one pass owns this verdict. A case
    # table checked eleven times a run prints its own pass eleven times and
    # says nothing new on ten of them.
    bad = [(a, want, scope_reading(*a)) for a, want in SCOPE_CASES
           if scope_reading(*a) != want]
    if bad:
        for args, want, got in bad:
            print(f"  CASE    {args}")
            print(f"            want {want}")
            print(f"            got  {got}")
        print()
        print("SCOPE_CASES says what a pass's scope line has to say. Nothing")
        print("below was read, because a scope reading that fails its own")
        print("cases is the instrument this pass exists to be.")
        return 1
    print(f"  the scope reading's cases {len(SCOPE_CASES)} pass")
    if os.environ.get("ALEXANDRIA_OFFLINE"):
        print("  SKIP    ALEXANDRIA_OFFLINE is set, so this run declared that")
        print("          it cannot reach the product. A declared blind spot is")
        print("          the one honest kind. Nothing below was read")
        print()
        return 0
    ok, trips = round_trip()
    if ok is None:
        print()
        print("This pass answered nothing, and that is why it is red. The")
        print("question it asks is whether the gates can see the product, and")
        print("an unreached product cannot be reported as a scope that")
        print("matches. Set ALEXANDRIA_OFFLINE=1 to declare the blind spot")
        print("instead of hiding behind it.")
        return 1
    rc = 0
    weeks = served_weeks_cached()
    retired = hidden_weeks()
    held = {p.stem for p in (ROOT / "site/content/issues").glob("*.md")}
    unread = [w for w in weeks if w not in held]
    print(f"  served by the product     {len(weeks)}: {', '.join(weeks)}")
    print(f"  held in the repository    {len(held)}: "
          f"{', '.join(sorted(held))}")
    print(f"  retired at the serving layer  {len(retired & set(weeks))}")
    print(f"  round trip verified on     {len(trips)} edition(s) held both ways")
    for week, same in trips:
        if same:
            print(f"    OK      {week}  the served page un-renders to the file")
        else:
            rc = 1
            print(f"    FAIL    {week}  the served page does not un-render to")
            print( "              the file, so the parser is stale and every")
            print( "              figure taken off the live site is suspect")
    if not trips:
        rc = 1
        print( "    FAIL    no edition is held both ways, so nothing here")
        print( "              proves the un-renderer and `--live` is unsafe")
    print(f"  served and unreadable here {len(unread)}"
          + (f": {', '.join(unread)}" if unread else ""))
    for week in unread:
        rc = 1
        print(f"  FAIL    {week} reached readers and is not a file here, so")
        print( "            every default-scope count in this file excludes it")
    if not unread:
        print("  every served edition is readable from the repository")
    print()
    print("A gate's scope is part of its answer (L-A47) and this file's")
    print("default scope is a directory, while the product's scope is a")
    print("table. They have disagreed since 2026-10-05 and the disagreement")
    print("printed canon law 12 to readers. `--live` closes it per run and")
    print("committing the print closes it for good.")
    return rc


# ---- canon law 1's two marks, over the artifact ------------------------

def marks(paths=None):
    """The em dash and the semicolon, with the generator's own zero target.

    Split out of `measure` for the reason `devices` was: that command's exit
    code means the character gate and a test reads it by name, so a second
    meaning on it reports a cause that is not the cause (L-A44).

    This is not a new rule. `prompts/digest.md` states it twice in its own
    words, "the target is zero and there is no budget, the same as the em
    dash", and canon law 1 bans the semicolon join outright. What was missing
    is the half this file applies to its own author and not to the product:
    `selfcheck` fails this seat's run when a diff adds one semicolon, and
    nothing in `all` ruled on a semicolon in the issue. `measure` printed the
    count and moved on, so the number was visible and never a verdict.

    The current edition carries two, and both are the plainest form of the
    join, two independent clauses with a mark between them:

        Llama-3.1-8B loads skills 72% of the time overall; Llama-3.3-70B
        loads them 11% of the time.

    The exemptions are `selfcheck`'s, for its reasons: a mark inside a
    quotation of a source is the source's, and editing it falsifies the quote.
    """
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    scope(paths, hidden_weeks())
    retired = hidden_weeks()
    rc = 0
    for p in paths:
        p = pathlib.Path(p)
        if not p.exists():
            print(f"  {p}: missing")
            rc = 1
            continue
        try:
            shown = p.resolve().relative_to(ROOT)
        except ValueError:
            # A served edition, un-rendered into this process's cache. Named by
            # its week and its source rather than by a temporary path, because
            # ban list 91 says a figure is quoted with the artifact it was
            # measured on and `/tmp/check_voice-editions-oqj97_z6` is not a
            # name a review can carry.
            shown = f"{p.stem} (served, un-rendered from {LIVE_SITE})"
        if p.stem in retired:
            print(f"  SKIP    {shown}  retired, not served")
            continue
        inside = fenced(p)
        hits = []
        for n, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if n in inside or quoting(line):
                continue
            for mark, name in ((";", "semicolon"), (EM, "em dash")):
                if mark in line:
                    hits.append((n, name, line.strip()))
        print(f"  {shown}   marks outside a quotation  {len(hits)}")
        for n, name, line in hits:
            rc = 1
            print(f"    FAIL    {shown}:{n}  {name}")
            print(f"              {line[:104]}")
    print()
    print("Zero is the generator's own target and it says there is no budget.")
    print("A count without a verdict is what let two of these print: this")
    print("seat's own prose has been failing on the same mark since")
    print("2026-10-10 and the product's prose was only ever measured.")
    return rc


# ---- captions ---------------------------------------------------------

#: The sibling caption sets on the site. One entry per set, because the tell
#: this reads is a property of a SET and is invisible in any one member. Today
#: the skill library's shelves are the only set in the repository that renders
#: a caption under every member of a list. A second set is one line here.
CAPTION_SETS = (("site/lib/skill-shelves.js", "the skill library's shelves"),)

#: A caption built as a short verbless opener, a full stop, and a list. The
#: length bound is what makes it a FRAME rather than an ordinary two-sentence
#: caption: the opener is too short to be an argument, so its only job is to
#: announce the subject before the list arrives.
CAPTION_FRAME = re.compile(r"^[^.]{1,45}\.\s+[A-Z]")

#: What `CAPTION_FRAME` must and must not read as the frame. Every case is a
#: caption string taken verbatim from the surface, so a case here is evidence
#: rather than an illustration. Run before any file is opened, because a
#: pattern that reports the wrong count reports it in the same format as the
#: right one.
CAPTION_CASES = (
    (True, "The scaffold around a model. Tools, prompts, loop structure, and "
     "the feedback the loop runs on."),
    (True, "Several agents dividing work. How they are organised, how they "
     "hand off, and how they fail."),
    (True, "Post-training that updates the weights. Distillation, reward "
     "design, and self-improvement."),
    (True, "Getting an answer out fast and cheap. Decoding, caching, and "
     "test-time compute."),
    (False, "What goes into the window, in what order, and what to do when it "
     "will not fit."),
    (False, "Models that read and act beyond text, across images, audio, and "
     "the world."),
    (False, "Distilled and shelved, on a shelf of its own for now."),
    # The drafted repairs of 2026-10-26, which the frame must not read as the
    # frame it was written to replace. The first is the long one and the last
    # is the short one, which are the two a length-bounded pattern is most
    # likely to get wrong.
    (False, "Most of what makes an agent reliable sits outside the model, in "
     "the tools it is given, the loop it runs in and the corrections it gets "
     "back."),
    (False, "Once the answer is right, the remaining job is getting it out "
     "fast and cheap."),
    (False, "A skill lands here when its subject is not one of the headings "
     "above."),
    # A caption whose FIRST sentence is long enough to carry an argument is
    # two sentences rather than this frame, however the second one reads.
    (False, "An agent that can act needs a boundary somewhere, and where you "
     "put it decides whether the defence does anything. Both halves matter."),
)

#: A caption as the surface declares it, which is a `blurb:` key whose value
#: may wrap across lines the way every string in that file does.
CAPTION = re.compile(r"blurb:\s*\n?\s*((?:\"(?:[^\"\\]|\\.)*\"\s*\+?\s*)+)")


def caption_cases():
    """`CAPTION_FRAME` against the captions it is a verdict about."""
    bad = [(want, s) for want, s in CAPTION_CASES
           if bool(CAPTION_FRAME.match(s)) != want]
    print(f"CAPTION_FRAME cases                        "
          f"{len(CAPTION_CASES) - len(bad)} of {len(CAPTION_CASES)}")
    for want, s in bad:
        print(f"  FAIL    wanted {want}, got {not want}: {s[:60]}")
    return 1 if bad else 0


def captions_of(path):
    """The caption strings one surface declares, in declaration order."""
    text = (ROOT / path).read_text(encoding="utf-8")
    out = []
    for m in CAPTION.finditer(text):
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
        out.append(re.sub(r"\s+", " ", "".join(parts)).strip())
    return out


def captions(paths=None):
    """A set of sibling captions written in one grammar, ban list 3 and 142.

    Entry 3 says vary or die and it has never carried a count, so it has only
    ever been a reading. Entry 113 is the lesson this one is built from in its
    own words: "Every gate in that list that holds was turned into a count
    after a print walked past it."

    What walked past was the skill library's shelf page. Six captions, four of
    them the identical frame, and the set survived three visual sweeps of that
    page and two copy rounds that read the page it sits on, because no single
    caption looks wrong. That is the whole class. A tell that lives in a SET
    is invisible to any gate pointed at a member, and every other check in
    this file is pointed at a member.

    Two counts, both exact string work, both the technique entry 113 already
    settled for evidence grades.

      more than one caption in a set on the same frame,
      two captions in a set opening on the same two words.

    What it deliberately does not count, because the proxy would be worse
    than the reading. Her ruling of 2026-09-29 forbids fragments, and all
    seven captions on that page are fragments, which is the sharper finding
    and the one that needed a person. Deciding whether a clause carries a
    finite verb is not string work, and a fragile detector reporting a verdict
    in this format would be trusted exactly as far as the honest counts above.
    So the fragment count stays in `docs/voice/shelf-names-2026-10-26.md`,
    where a reader can check it, and this gate claims only what it can prove.
    """
    rc = caption_cases()
    print()
    sets = selected_sets(CAPTION_SETS, paths)
    # The caller named surfaces and none of them is a declared caption set, so
    # the loop below runs zero times and the only line printed is the
    # asserted-case count above it, which reads as a clean pass on the thing
    # that was asked about. Found 2026-11-02 and it is the purest instance of
    # the class the ExO seat kept: this gate reported success by saying nothing
    # at all about the artifact.
    if paths and not sets:
        print("  FAIL    none of the paths named is a declared caption set,")
        print("          so no set was read and the count above is about this")
        print("          gate's own cases rather than about anything you asked")
        print("          for. The declared sets are:")
        for path, label in CAPTION_SETS:
            print(f"            {path}  ({label})")
        return 1
    for path, label in sets:
        if not (ROOT / path).exists():
            print(f"  FAIL    {path}  missing")
            rc = 1
            continue
        found = captions_of(path)
        framed = [c for c in found if CAPTION_FRAME.match(c)]
        stems = {}
        for c in found:
            stems.setdefault(" ".join(c.lower().split()[:2]), []).append(c)
        shared = {k: v for k, v in stems.items() if len(v) > 1}
        print(f"  {path}  ({label})")
        print(f"    captions                               {len(found)}")
        print(f"    on the opener-then-list frame          {len(framed)}")
        print(f"    opening on a stem another one uses     {len(shared)}")
        if len(framed) > 1:
            rc = 1
            print(f"    FAIL    {len(framed)} captions share one frame")
            for c in framed:
                print(f"              {c}")
        for stem, members in sorted(shared.items()):
            rc = 1
            print(f'    FAIL    {len(members)} captions open on "{stem}"')
    print()
    print("A caption set is read as one thing by anybody who scrolls the page,")
    print("so one grammar repeated down it is the unit of the tell. Each")
    print("caption above is accurate about its own shelf, which is what makes")
    print("this prose rather than error.")
    return rc


# The generator the press is running, and the distance from the one this seat
# edits. Ban list 146 is the entry and this is its enforcement.
PRESS_APP = "weekly"
PRESS_FILE = "prompts/digest.md"
# The engineer's walk is bounded at 40 commits and the deployed commit passed
# that mark on 2026-10-26. 400 is not a tuned number, it is a window wide
# enough that the bound is the deploy's age rather than this seat's output
# rate, which is the whole defect being worked around here.
PRESS_WINDOW = 400


def queued_count(deployed, queued):
    """The number of queued commits, or `None` when there is nothing to count.

    One line of logic, extracted so it can be asserted. Ban list 154 was
    written about three tools printing a count over a subject they never
    found, and `press` was doing it in this repository at the same hour:
    `queued` is empty until a deployed commit is recovered, so the REFUSED
    path printed `0` under `deployed commit unknown`, and zero queued commits
    is what a current press looks like.

    `None` and never `0`, for the reason `coverage_figure` returns `None` for
    an empty domain. A count of nothing found and a count of nothing there are
    different answers and only one of them is a verdict.
    """
    if not deployed:
        return None
    return len(queued or ())


QUEUED_CASES = (
    # The live defect. No deployed commit recovered, so there is no count,
    # and the empty list beside it is not evidence of a current press.
    ((None, []), None),
    # The same, with the unknown spelled the way `press` prints it.
    (("", []), None),
    # A deployed commit and nothing newer IS zero, and this is the case that
    # makes the two above a measurement rather than a precaution: zero has to
    # stay reachable or the fix is just a mute button.
    (("abc1234", []), 0),
    # The ordinary reading, and the figure the predecessor run reported.
    (("abc1234", ["a", "b", "c"]), 3),
    # A deployed commit with `None` for the list is zero and not an error,
    # because the caller initialises the list and the recovery is what fails.
    (("abc1234", None), 0),
)


def press_verdict(found, generator_commit, queued, now, generator_at):
    """One verdict about the press, from facts a caller has already gathered.

    Separated from the reading so it can be pinned by cases that need no
    network and no git. `found` is `undeployed_commits`'s dict, verbatim.

    The three outcomes are not three grades of the same thing. A refusal means
    the question was not answered and the run must not conclude anything from
    it, which is the reading that cost run 60 forty minutes. A press on the
    trunk's generator means a grade below is a grade on this seat's current
    work. Anything else means the grade is about an older file, and the run has
    to say which one before it scores a single law.
    """
    if "why" in found:
        return "REFUSED", found["why"]
    if not queued and generator_commit:
        return "CURRENT", (f"the press is running {PRESS_FILE} as of "
                           f"{generator_commit}, which is the trunk's")
    # The age is the GENERATOR commit's, not the deploy's. They differ by
    # however long this file sat unedited before the deploy, and the number a
    # grade needs is the age of the prose the press is writing from.
    age = ""
    if generator_at is not None and now is not None:
        age = (f", {round((now - generator_at).total_seconds() / 86400, 1)} "
               f"days old")
    return "BEHIND", (f"the press is running {PRESS_FILE} as of "
                      f"{generator_commit or 'an unnamed commit'}{age}, with "
                      f"{len(queued)} merged commit(s) to it queued behind the "
                      f"deploy")


PRESS_CASES = [
    ({"why": "the running digest matches none of the last 40 commits to touch "
             "this app's files"}, None, [], "REFUSED"),
    ({"deployed_commit": "abc1234", "deployed_at": "2026-10-26T00:00:00+00:00"},
     "abc1234", [], "CURRENT"),
    ({"deployed_commit": "f16e277", "deployed_at": "2026-10-15T17:40:37+00:00"},
     "9b6410e", [{"sha": "x"}, {"sha": "y"}], "BEHIND"),
    # The deploy is newer than the generator commit it carries, which is the
    # ordinary case and the reason the age is read off the second one.
    # A deploy this seat's file predates: the image is current for the app and
    # still behind for the generator, because the app's other seven files moved
    # and this one did not. The verdict is BEHIND and the reason names the
    # generator rather than the app, which is the distinction a writer run
    # needs and the deploy surface does not make.
    ({"deployed_commit": "f16e277", "deployed_at": "2026-10-15T17:40:37+00:00"},
     None, [{"sha": "x"}], "BEHIND"),
]


def refusal_owner(found):
    """Who clears a REFUSED, read off the dict rather than out of its sentence.

    `press_verdict` collapses every refusal into one word, which was right
    while every refusal had one remedy. It does not any more. On 2026-11-02
    the engineer seat gave `undeployed_commits` the shallow check its own
    docstring had promised since the function existed, and put `shallow: True`
    on the dict "so that you need not grep a sentence". This is the caller
    that sentence was written for, and until now there was none: the flag
    arrived and reached nothing in this file.

    The distinction is worth a function because the three causes have three
    owners. A depth is this run's own and it is two commands away. A digest
    that matches a full history is the deploy's, which is another seat's. A
    job that has never reported is neither, and concluding anything about the
    press from it is the mistake this whole gate exists to stop.

    Measured on a shallow clone of this repository rather than reasoned, and
    measured twice because `main` moved underneath the first reading. Before
    `#776` merged, a checkout holding one commit was told "the deploy was
    built from code that is not in this history". After it merged, at
    `b9b1d1b`, the same clone is told "the depth is the cause and the deploy
    has not been judged", and the line below it names this run as the owner.
    So all three owners are answerable today.

    This file does not re-ask git the question itself. The module that owns it
    is already imported two lines above the call, and a second reader of one
    fact in this file is the parallel structure the charter forbids before it
    forbids anything else.
    """
    if "why" not in found:
        return None
    if found.get("shallow") is True:
        return "depth"
    if "searched" in found:
        return "deploy"
    return "receipt"


#: One line per owner, for the reader of a refusal. `deploy` still names the
#: command that falsifies it, because this file cannot see which version of
#: `tools/delivery_health.py` a given checkout holds, and on a checkout whose
#: copy predates the shallow check a depth lands in that branch instead.
REFUSAL_LINES = {
    "depth": "the cause is this checkout's depth, which is this run's own to "
             "clear: git fetch --unshallow, then run this gate again",
    "deploy": "the cause is the deploy, so the image was built from code this "
              "history does not hold, and judging that is another seat's. One "
              "call falsifies it where the question is open: git rev-parse "
              "--is-shallow-repository",
    "receipt": "nothing has been reported to diff against, so this is a fact "
               "about the receipt and not about the press",
}

REFUSAL_CASES = (
    # The five shapes `undeployed_commits` actually returns, in its own order.
    ({"why": "this job has never reported a running digest"}, "receipt"),
    ({"why": "pipeline.weekly cannot be read at origin/main here"}, "receipt"),
    ({"why": "this checkout has no history for the app's files"}, "receipt"),
    ({"why": "the running digest matches none of the last 232 commits",
      "searched": 232}, "deploy"),
    ({"why": "this checkout is a shallow clone, so the 1 commit(s) of history "
             "it holds cannot place the running digest: git fetch --unshallow",
      "searched": 1, "shallow": True}, "depth"),
    # A recovered deploy is not a refusal at all, and the owner of one is
    # nobody. The case is here because `press` calls this on every path.
    ({"deployed_commit": "abc1234", "searched": 232}, None),
    # `is True` and not truthiness, for the reason the engineer gave it: a git
    # that cannot answer must not be reported as a shallow clone.
    ({"why": "the running digest matches none of the last 1 commits",
      "searched": 1, "shallow": None}, "deploy"),
)


def press_cases():
    """The verdict function, the queued count and the refusal owner, pinned."""
    rc = 0
    now = datetime.datetime(2026, 10, 27, tzinfo=datetime.timezone.utc)
    for found, gen, queued, want in PRESS_CASES:
        at = found.get("deployed_at")
        at = datetime.datetime.fromisoformat(at) if at else None
        got, _ = press_verdict(found, gen, queued, now, at)
        if got != want:
            rc = 1
            print(f"  FAIL    case wanted {want} and got {got}")
    print(f"PRESS_CASES                                "
          f"{len(PRESS_CASES) - rc} of {len(PRESS_CASES)}")
    stale = 0
    for (deployed, queued), want in QUEUED_CASES:
        got = queued_count(deployed, queued)
        if got != want:
            stale = 1
            print(f"  FAIL    queued_count({deployed!r}, {queued!r}) wanted "
                  f"{want!r} and got {got!r}")
    print(f"QUEUED_CASES                               "
          f"{len(QUEUED_CASES) - stale} of {len(QUEUED_CASES)}")
    owners = 0
    for found, want in REFUSAL_CASES:
        got = refusal_owner(found)
        if got != want:
            owners = 1
            print(f"  FAIL    refusal_owner wanted {want!r} and got {got!r} "
                  f"for {found.get('why', 'a recovered deploy')[:48]}")
    print(f"REFUSAL_CASES                              "
          f"{len(REFUSAL_CASES) - owners} of {len(REFUSAL_CASES)}")
    return rc | stale | owners


def press():
    """Which generator the press is running, and how far it is from the trunk.

    Every grade this seat writes is a verdict on `prompts/digest.md`, and the
    copy of that file the press runs is not the copy a run edits. The forwards
    half of the canon's procedure asked each run to check that distance, in
    prose, and on 2026-10-27 the one command that answers it stopped answering:
    `tools/delivery_health.py` recovers the deployed commit by replaying the
    image's content digest over the last `DEPLOY_HISTORY_LIMIT` commits to
    touch the app's files, that limit is 40, and `weekly`'s file list contains
    the one file this seat edits on every run. The deployed commit reached walk
    position 43 and the surface printed "the deploy was built from code that is
    not in this history" about a nine-day-old ancestor of `origin/main`.

    So the instrument goes blind in proportion to this seat's own output, which
    is the defect ban list 146 names. The ledger entry of 2026-10-27 asks the
    engineer for the window and for a refusal that says how far it looked. This
    is the half that belongs here: the same question, asked with the window
    widened, by the seat that needs the answer before it grades anything.

    It calls `undeployed_commits` rather than replaying the digest again. A
    second copy of that logic in this file would be a parallel structure, and
    the one thing this charter forbids beyond all others is a seat inventing a
    structure beside one that already works.

    Unreachable is a failure and never a pass. A run that cannot read the row
    and concludes the press is current has made the mistake this whole file was
    built to stop.
    """
    rc = press_cases()
    print()
    found = press_deploy()
    if found is None:
        print("    nothing was read, so nothing is concluded about the press")
        return 1
    row = found["row"]
    deployed = found.get("deployed_commit")
    at = found.get("deployed_at")
    at = datetime.datetime.fromisoformat(at) if at else None
    gen = None
    gen_at = None
    queued = []
    if deployed:
        gen = _git_line("log", "-1", "--format=%h %cI %s", deployed,
                        "--", PRESS_FILE)
        if gen:
            with contextlib.suppress(ValueError, IndexError):
                gen_at = datetime.datetime.fromisoformat(gen.split()[1])
        queued = _git_lines("log", "--format=%h %cI %s",
                            f"{deployed}..origin/main", "--", PRESS_FILE)
    verdict, why = press_verdict(found, gen.split()[0] if gen else None,
                                 queued, datetime.datetime.now(
                                     datetime.timezone.utc), gen_at)
    print(f"recorded digest                            "
          f"{row.get('runtime_sha')}")
    print(f"recorded at                                "
          f"{row.get('recorded_at')}")
    rc |= receipt_columns(row)
    print(f"deployed commit                            {deployed or 'unknown'}")
    print(f"commits searched                           "
          f"{found.get('searched', 0)} of a {PRESS_WINDOW} window")
    print(f"the generator it carries                   {gen or 'unknown'}")
    print(f"deployed at                                {at or 'unknown'}")
    # Ban list 154, found in this gate by running it on the day the entry was
    # written about three of the engineer seat's tools. `queued` is `[]` until
    # a deployed commit is recovered, so on the REFUSED path this line used to
    # print `0` directly under `deployed commit unknown`. Zero queued commits
    # is what a current press looks like. The predecessor run read 30 here and
    # a run that hit this path would have read 0 and reported the press
    # current, which is the promotion-gate defect one layer in from the three
    # the entry names.
    #
    # The exit code was already right: `press` returns 1 and prints REFUSED.
    # That is exactly what 154 is about. An exit code repairs the caller and
    # leaves the reader, and the reader of this line is the next grade.
    n_queued = queued_count(deployed, queued)
    if n_queued is not None:
        print(f"queued commits to the generator            {n_queued}")
        for line in queued[:5]:
            print(f"    {line}")
        if n_queued > 5:
            print(f"    and {n_queued - 5} more")
    else:
        print("queued commits to the generator            UNKNOWN, and that")
        print("          is not zero: the deployed commit was never")
        print("          recovered, so nothing was counted rather than")
        print("          nothing being found")
    print()
    print(f"  {'FAIL' if verdict != 'CURRENT' else 'OK  '}    {verdict}: {why}")
    owner = refusal_owner(found)
    if owner:
        print(f"          {REFUSAL_LINES[owner]}")
    print()
    print("A verdict on an issue is a verdict on the generator that wrote it,")
    print("so the run that cannot name that generator is grading an unnamed")
    print("artifact. REFUSED never means the press is current, and it does")
    print("not mean one thing. The line under it says which of three causes")
    print("was read and who clears it, because the depth of this checkout is")
    print("the run's own to fix in two commands and the other two are not.")
    return rc | (verdict != "CURRENT")


def press_deploy():
    """`undeployed_commits` for the press, or None with the reason printed.

    Factored out of `press` when a second command needed the deployed commit.
    A second copy of the receipt read in this file would be a parallel
    structure, and this charter forbids those before it forbids anything else.

    The row the receipt carried is returned under `row`, because the caller
    that prints a verdict has to be able to say what it read it off.
    """
    try:
        sys.path.insert(0, str(ROOT))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_dh", ROOT / "tools" / "delivery_health.py")
        dh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dh)
    except Exception as e:
        print(f"  UNREACHED tools/delivery_health.py: {type(e).__name__}: {e}")
        return None
    doc = receipt_json(dh.RECEIPT_URL)
    if doc is None:
        return None
    try:
        rows = {r["app"]: r for r in doc.get("deploy", [])}
    except (ValueError, KeyError, TypeError) as e:
        print(f"  UNREACHED {dh.RECEIPT_URL}: {type(e).__name__}: {e}")
        return None
    row = rows.get(PRESS_APP)
    if row is None:
        print(f"  FAIL    the receipt carries no row for {PRESS_APP}, so the "
              f"press has never reported what it runs")
        return None
    found = dh.undeployed_commits(ROOT, PRESS_APP, row.get("runtime_sha"),
                                  limit=PRESS_WINDOW, ref="origin/main")
    found["row"] = row
    return found


def receipt_json(url):
    """The public receipt as a dict, or None with the reason printed.

    `press_deploy` read the receipt for its `deploy` array and threw the rest
    away, and the command below needs the `press` block off the same document.
    Two fetches of one URL in one file would be a parallel structure before it
    was a second request, and this file forbids those before it forbids
    anything else, so both callers come through here.
    """
    body = _fetch(url)
    if body is None:
        return None
    try:
        return json.loads(body)
    except ValueError as e:
        print(f"  UNREACHED {url}: {type(e).__name__}: {e}")
        return None


# ------------------------------------------------- the receipt's column set
#
# A column that exists in the table and reaches no reader is the partial-landing
# class arriving from the other end, and on 2026-11-02 the engineer seat sent
# this seat two live instances of it: `entrypoint` and `file_count` have been in
# `deploy_runtime` since the table was created, the schema's own comment calls
# `entrypoint` the value "for the deploy command", and `tools/delivery_health.py`
# named five columns and dropped both.
#
# The reason nobody caught it is the part worth building on. That suite's fake
# connection answered every query with anonymous tuples and no `description`, so
# a reader naming five columns and a reader naming all seven were
# indistinguishable from inside it. The column list was unobservable to the one
# suite that exists to watch the column.
#
# This is that measurement, for the reader this seat actually runs. `press` and
# `cadence` both read the deploy rows off the public receipt rather than off a
# connection, because no agent seat holds `DATABASE_URL` and
# `site/lib/delivery-core.js` says so in its own opening comment. So the column
# list those two commands see is the one in `site/lib/delivery.js`, and the
# question this gate asks is whether it still carries everything the schema
# declares.
#
# Both functions are pure and the schema text is passed in, which is the
# property that makes the cases below worth having: they pin the comparison and
# not the file.


def declared_columns(table, text):
    """The column names `text` declares for `table`, in order, or None.

    None rather than `()` when the table is not there, because an empty tuple
    says "this table declares no columns" and every caller would read that as
    nothing missing. That is the same refusal `row_writers` makes for a file it
    cannot read, and for the same reason.

    Comments are stripped before the parentheses are matched, because
    `deploy_runtime`'s own comments contain both a comma and a `()`, and a
    parser that counts depth first reads the column list as ending inside a
    sentence about `runtime_sha.digest()`.
    """
    stripped = "\n".join(re.sub(r"--.*$", "", line) for line in text.splitlines())
    m = re.search(r"create\s+table\s+(?:if\s+not\s+exists\s+)?"
                  + re.escape(table) + r"\s*\(", stripped, re.I)
    if not m:
        return None
    depth, start = 1, m.end()
    for i in range(start, len(stripped)):
        depth += {"(": 1, ")": -1}.get(stripped[i], 0)
        if depth == 0:
            body = stripped[start:i]
            break
    else:
        return None
    parts, depth, cur = [], 0, ""
    for c in body:
        depth += {"(": 1, ")": -1}.get(c, 0)
        if c == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    names = []
    for part in parts:
        words = part.split()
        if not words:
            continue
        # A table-level constraint is not a column. Dropped by its leading
        # keyword rather than by position, because `primary key (app)` and
        # `app text primary key` are the same constraint written two ways and
        # only the second one names a column.
        if words[0].lower() in ("primary", "unique", "constraint", "check",
                                "foreign", "exclude", "like", "partition"):
            continue
        names.append(words[0].strip('"'))
    return tuple(names)


def unreached_columns(declared, carried):
    """Declared columns the row does not carry, in declaration order.

    `carried` is the row as a consumer received it, so a mapping. A row that
    names nothing returns every declared column rather than none: that is the
    anonymous-tuple case the engineer seat's fake could not see, and reading it
    as complete is the only answer that would make this gate worthless.

    Columns the row carries that the schema does not declare are NOT graded,
    and the reason is worth stating. A receipt is allowed to publish a field it
    computed, and failing on one would make this gate refuse the next honest
    addition to the endpoint. The direction that matters is the one with the
    silence in it: a column lands in the table, every job writes it, and no
    reader asks.
    """
    if declared is None:
        return None
    keys = set(carried or ())
    return tuple(c for c in declared if c not in keys)


# The parser against the shapes `db/schema.sql` actually contains, and the
# comparison against the exact row the old reader produced. Case 2 is the one
# the whole block is for: five names against seven declared must print two, and
# the suite that could not tell those apart is the reason this file now has a
# case for it.
COLUMN_CASES = (
    # `deploy_runtime` reduced to its skeleton, with both the comma and the
    # `()` that live inside its comments kept, because they are what a
    # depth-first parser breaks on.
    ("create table if not exists deploy_runtime (\n"
     "    app           text primary key,          -- 'triage' | 'weekly'\n"
     "    runtime_sha   text not null,             -- runtime_sha.digest()\n"
     "    entrypoint    text not null,             -- 'pipeline/triage.py'\n"
     "    file_count    integer not null,          -- how many files\n"
     "    recorded_at   timestamptz not null default now(),\n"
     "    notified_at   timestamptz\n"
     ");\n", "deploy_runtime",
     ("app", "runtime_sha", "entrypoint", "file_count", "recorded_at",
      "notified_at")),
    # A type with a comma inside its own parentheses, which is the other way
    # the split goes wrong.
    ("create table t (\n    a numeric(10, 2) not null,\n    b text\n);\n",
     "t", ("a", "b")),
    # A table-level constraint, which names columns and is not one.
    ("create table t (\n    a text,\n    b text,\n    primary key (a, b)\n);\n",
     "t", ("a", "b")),
    # The table is not in the text. Refused, because `()` here would read as
    # nothing missing from every caller below.
    ("create table if not exists other (a text);\n", "deploy_runtime", None),
    # A longer name that starts with the one asked for must not match it.
    ("create table if not exists deploy_runtime_old (a text);\n",
     "deploy_runtime", None),
)

# `unreached_columns` against the seven columns `deploy_runtime` declares today.
SEVEN = ("app", "runtime_sha", "entrypoint", "file_count", "recorded_at",
         "first_seen_at", "notified_at")
UNREACHED_CASES = (
    # The row the receipt serves today, which is complete.
    (SEVEN, dict.fromkeys(SEVEN), ()),
    # The row `deploy_facts` produced until 2026-11-02. This is the engineer
    # seat's finding, pinned: two columns in the table, written by every job,
    # reaching no reader.
    (SEVEN, {"app": 1, "runtime_sha": 1, "recorded_at": 1,
             "first_seen_at": 1, "notified_at": 1},
     ("entrypoint", "file_count")),
    # The column that is carded and not yet migrated. Declared nowhere yet, so
    # a receipt that lacks it is correct and this gate must stay quiet about
    # it; the day it lands in the schema this same case starts naming it.
    (SEVEN, dict.fromkeys(SEVEN + ("invoked_by",)), ()),
    # The anonymous row. No keys at all is not a complete row, and a gate that
    # read it as one would be the fake that could not tell five from seven.
    (SEVEN, {}, SEVEN),
    (SEVEN, None, SEVEN),
    # No declaration to compare against is refused rather than passed.
    (None, dict.fromkeys(SEVEN), None),
)


def column_cases():
    """The parser and the comparison, before either touches a file or the net."""
    bad = 0
    for i, (text, table, want) in enumerate(COLUMN_CASES):
        got = declared_columns(table, text)
        if got != want:
            bad = 1
            print(f"  CASE    declared_columns case {i} wanted {want} and "
                  f"got {got}")
    print(f"COLUMN_CASES                               "
          f"{len(COLUMN_CASES) - bad} of {len(COLUMN_CASES)}")
    worse = 0
    for declared, carried, want in UNREACHED_CASES:
        got = unreached_columns(declared, carried)
        if got != want:
            worse = 1
            print(f"  CASE    unreached_columns({carried!r}) wanted {want} "
                  f"and got {got}")
    print(f"UNREACHED_CASES                            "
          f"{len(UNREACHED_CASES) - worse} of {len(UNREACHED_CASES)}")
    return bad | worse


def columns():
    """The schema parser and the column comparison, asserted and read offline.

    It is its own subcommand because `all` excludes `press` and `cadence`, both
    of which need the network, and `receipt_columns` lives inside `press`
    because that is where the row is already fetched. Leaving the pure half
    there too would have put eleven cases behind a command the ordinary run
    never reaches, which is this file's own defect class wearing a new coat: a
    measurement nothing runs is not a measurement.

    So the split is by what each half needs. The cases and the schema read need
    nothing and are here. The comparison against what the receipt actually
    served needs one fetch and stays in `press`.
    """
    rc = column_cases()
    print()
    try:
        text = SCHEMA.read_text()
    except OSError as e:
        print(f"  FAIL    db/schema.sql could not be read "
              f"({type(e).__name__}), so no consumer's column set has "
              f"anything to be checked against")
        return 1
    declared = declared_columns("deploy_runtime", text)
    if declared is None:
        print("  FAIL    db/schema.sql declares no `deploy_runtime`. Either "
              "the table was renamed or this gate's name for it is stale, "
              "and both make the comparison in `press` a refusal rather "
              "than a verdict")
        return 1 | rc
    print(f"db/schema.sql declares for deploy_runtime  {len(declared)}")
    for name in declared:
        print(f"    {name}")
    print()
    print("Whether the receipt serves all of them is `press`, because that is")
    print("where the row is read. The two columns that prompted this gate,")
    print("`entrypoint` and `file_count`, were declared here from the day the")
    print("table was created and reached no reader through")
    print("`tools/delivery_health.py` until 2026-11-02.")
    return rc


def receipt_columns(row):
    """Does the receipt still carry every column `deploy_runtime` declares.

    Printed and graded inside `press`, off the row that command already read,
    because a second fetch of one URL in this file would be the parallel
    structure this charter forbids before it forbids anything else.

    It fails rather than warns. The whole lesson of the two columns is that an
    unread column produces no complaint from anybody: the job writes it, the
    table holds it, and every consumer is silently a version behind. A warning
    is what that already looks like.

    It compares a schema read from this checkout against a receipt served by
    the deployed site, so the window between a merged migration and a site
    deploy reads as a failure here. That is the intended answer and not a false
    one: during that window the column really is in the table and really is
    invisible to every reader, which is the state this gate exists to name. The
    line it prints says which file closes it.
    """
    try:
        text = SCHEMA.read_text()
    except OSError as e:
        print(f"  FAIL    db/schema.sql could not be read "
              f"({type(e).__name__}), so the receipt's column set was "
              f"compared against nothing")
        return 1
    declared = declared_columns("deploy_runtime", text)
    if declared is None:
        print("  FAIL    db/schema.sql declares no `deploy_runtime`, so this "
              "gate cannot say what the receipt owes")
        return 1
    missing = unreached_columns(declared, row)
    print(f"columns deploy_runtime declares            {len(declared)}  "
          f"{', '.join(declared)}")
    print(f"columns the receipt carries                {len(row or ())}  "
          f"{', '.join(sorted(row or ()))}")
    if not missing:
        print("  OK      every declared column reaches this gate")
        return 0
    print(f"  FAIL    {len(missing)} column(s) are in `deploy_runtime` and no "
          f"consumer of the receipt can see them: {', '.join(missing)}")
    print("          The receipt's deploy rows are built by the hand-written")
    print("          column list in `site/lib/delivery.js`, not by")
    print("          `tools/delivery_health.py:deploy_facts`, because no agent")
    print("          seat holds DATABASE_URL and every seat reads the HTTP")
    print("          receipt. So widening `deploy_facts` does not widen this.")
    return 1


# The press's schedule, read off the job rather than restated here. A copy of
# `0 9 * * 1` in this file goes stale the first time the engineer seat moves
# the cron, and the gate would then be confidently wrong about the one number
# its whole verdict turns on.
WEEKLY_JOB = ROOT / "pipeline/weekly.py"
CRON_LINE = re.compile(r"modal\.Cron\(\s*[\"']([^\"']+)[\"']")
# `M H * * D` and nothing else. Every other cron shape is refused rather than
# approximated, because this command exists to replace a seat's mental
# arithmetic and an approximation puts the mistake back one level down.
WEEKLY_FORM = re.compile(r"^(\d{1,2}) (\d{1,2}) \* \* ([0-7])$")

PRESS_SCHEDULE_CASES = (
    ("0 9 * * 1", (0, 9, 1)),
    # Cron's Sunday is 0 and `isoweekday`'s is 7. Converted once, here, so no
    # caller below compares two conventions.
    ("30 14 * * 0", (30, 14, 7)),
    ("0 1 * * 1", (0, 1, 1)),
    # Refused rather than guessed. A multi-slot or sub-daily cron is a cadence
    # this enumerator does not model, and a wrong slot list is worse than no
    # slot list because there is nothing to check it against
    # (INC-2026-10-26-the-detector-named-a-slot-that-never-came-due-and-called-it-a-slot-that-did-not-fire).
    ("0 9 * * 1,4", None),
    ("*/15 * * * *", None),
    ("0 9 1 * *", None),
)


def press_schedule(line=None):
    """The press's cron as `(minute, hour, isoweekday)`, or `(None, why)`.

    Reads `pipeline/weekly.py` when given nothing, so the gate and the job
    cannot disagree. Weekday comes back in `isoweekday`'s convention, where
    Monday is 1 and Sunday is 7, because every comparison below is against a
    `date`.
    """
    if line is None:
        if not WEEKLY_JOB.exists():
            return None, "pipeline/weekly.py is not in this checkout"
        found = CRON_LINE.findall(WEEKLY_JOB.read_text())
        if len(found) != 1:
            return None, (f"pipeline/weekly.py carries {len(found)} "
                          f"modal.Cron lines, so which one the press runs on "
                          f"is not readable from the file")
        line = found[0]
    m = WEEKLY_FORM.match(line.strip())
    if not m:
        return None, (f"the press cron is `{line.strip()}`, which is not the "
                      f"`M H * * D` form this gate can enumerate")
    minute, hour, dow = (int(x) for x in m.groups())
    if minute > 59 or hour > 23:
        return None, f"the press cron is `{line.strip()}`, which is not a time"
    return (minute, hour, dow or 7), ""


def slots_between(schedule, since, until):
    """Every firing of `schedule` strictly after `since` and at or before `until`.

    This function is the whole command. A cadence claim is read by counting
    FIRINGS, and the mistake it replaces is counting PERIODS: on 2026-11-02
    this seat told the register's owner that two press slots had passed with no
    edition, because two weeks had ended since the last one. One slot had come
    due. A week ends on its own and only a schedule can miss, so the period
    boundary is never the measurable event.
    """
    minute, hour, iso = schedule
    out, day = [], since.date()
    while day <= until.date():
        if day.isoweekday() == iso:
            at = datetime.datetime(day.year, day.month, day.day, hour, minute,
                                   tzinfo=datetime.timezone.utc)
            if since < at <= until:
                out.append(at)
        day += datetime.timedelta(days=1)
    return out


def next_slot(schedule, after):
    """The first firing strictly after `after`."""
    minute, hour, iso = schedule
    day = after.date()
    for _ in range(9):
        at = datetime.datetime(day.year, day.month, day.day, hour, minute,
                               tzinfo=datetime.timezone.utc)
        if day.isoweekday() == iso and at > after:
            return at
        day += datetime.timedelta(days=1)
    return None


def periods_between(schedule, since, until):
    """The period ENDS in the span, printed beside the slots and never instead.

    A period ends at the instant the firing's day begins, because the press
    labels the week that ended the day before it runs. That is not this seat's
    reading of the schedule: the receipt proves it on one row, where
    `newest_week` 2026-W42 was created 2026-10-19T09:02Z and 2026-W42 is the
    week that ended Sunday 2026-10-18.

    Where this count and the slot count differ, the difference is a period that
    has closed whose slot has not come due, and that window is the only time a
    hand count can be wrong. For the press it is nine hours wide once a week,
    and 2026-11-02T01:23Z fell inside it.
    """
    wide = slots_between(schedule, since, until + datetime.timedelta(days=1))
    ends = [datetime.datetime(s.year, s.month, s.day,
                              tzinfo=datetime.timezone.utc) for s in wide]
    return [e for e in ends if since < e <= until]


# The reading that produced this command, and three around it, asserted before
# anything live is read. `since` is 2026-W42's creation on the receipt and
# `until` is the hour of the reading.
CADENCE_CASES = (
    # 2026-11-02T01:23:12Z, this run's `observed_at`. Two weeks had ended, one
    # slot had fired, and this seat reported two. The case IS the incident.
    ("2026-10-19T09:02:52+00:00", "2026-11-02T01:23:12+00:00", 1, 2,
     "2026-11-02T09:00:00+00:00"),
    # The same tree eight hours later, after today's firing. Two slots, two
    # periods, and the two numbers agree again.
    ("2026-10-19T09:02:52+00:00", "2026-11-02T09:30:00+00:00", 2, 2,
     "2026-11-09T09:00:00+00:00"),
    # The gap window itself, an hour before the missed slot of 2026-10-26: the
    # week has closed and nothing has failed yet. A seat reading here counts
    # one and the schedule has missed nothing.
    ("2026-10-19T09:02:52+00:00", "2026-10-26T08:00:00+00:00", 0, 1,
     "2026-10-26T09:00:00+00:00"),
    # The register's own last reading, 2026-10-25T23:32:50Z, which it called
    # "the clock has not yet missed" in prose and got right. Twenty-seven
    # minutes before the week closed, so neither number has moved.
    ("2026-10-19T09:02:52+00:00", "2026-10-25T23:32:50+00:00", 0, 0,
     "2026-10-26T09:00:00+00:00"),
    # Minutes after a firing that produced its edition, which is the only
    # shape of reading on which this row may read OK.
    ("2026-10-19T09:02:52+00:00", "2026-10-19T09:05:00+00:00", 0, 0,
     "2026-10-26T09:00:00+00:00"),
)


def cadence_cases():
    """The schedule parser and the arithmetic, against every pinned case."""
    rc = 0
    for line, want in PRESS_SCHEDULE_CASES:
        got, why = press_schedule(line)
        if got != want:
            rc = 1
            print(f"  CASE    `{line}` wanted {want} and got {got} ({why})")
    print(f"PRESS_SCHEDULE_CASES                       "
          f"{len(PRESS_SCHEDULE_CASES) - rc} of {len(PRESS_SCHEDULE_CASES)}")
    bad = 0
    sched, _ = press_schedule("0 9 * * 1")
    for since, until, slots, periods, nxt in CADENCE_CASES:
        a = datetime.datetime.fromisoformat(since)
        b = datetime.datetime.fromisoformat(until)
        got = (len(slots_between(sched, a, b)),
               len(periods_between(sched, a, b)),
               next_slot(sched, b).isoformat())
        if got != (slots, periods, datetime.datetime.fromisoformat(nxt).isoformat()):
            bad = 1
            print(f"  CASE    at {until} wanted "
                  f"{(slots, periods, nxt)} and got {got}")
    print(f"CADENCE_CASES                              "
          f"{len(CADENCE_CASES) - bad} of {len(CADENCE_CASES)}")
    return rc | bad | zones_cases()


def week_label(end):
    """The ISO week label the press prints for a period ending at `end`.

    `end` is the instant the firing's day begins, so the week it closes is the
    day before it.
    """
    d = (end - datetime.timedelta(days=1)).date()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


# ---------------------------------------------------------------------------
# What an absent run record proves, which is one proposition about one line.
#
# Added 2026-11-02, the second half of the exchange that produced the command
# below. The first draft of `cadence` read a frozen `recorded_at` beside a
# missed slot and printed "the slot was UNSCHEDULED rather than the job broken,
# and nobody has to repair a job to fix it". That is the invented-subject
# defect this command's own docstring refuses when it cannot parse the cron,
# committed one screen further down and shipped: it named one cause out of
# several and recommended a repair on the strength of it.
#
# The ExO seat returned the correction as `bf58bdda` and it is right at the
# code, verified here in `pipeline/weekly.py` rather than accepted from the
# note. `record_runtime` is called at 1885, inside a `try` that opens at 1874,
# after `check_availability()` at 1879 and the `psycopg.connect` at 1881. Three
# calls run BEFORE that handler opens -- `week_just_ended()` at 1846,
# `week_window()` at 1862 and the two `open("/root/prompts/digest*.md")` reads
# at 1863 and 1864 -- and `notify_owner`, defined at 1367, is called only from
# the `except` at the foot of that same handler, so it cannot see any of them.
# The write site therefore cuts a run into zones and the field reads the same
# across them.

def press_write_site(path=None):
    """The line numbers that make the zones, read out of the job's own source.

    Derived, never declared, for exactly the reason `schedules()` in
    `pipeline/runtime_sha.py` gives about file manifests and this file's own
    `press_schedule` gives about the cron: a hand-kept copy of a line number is
    a copy that disagrees with the job on the day it matters, and a line number
    in a gate's output is the most quietly rotting kind of all. The first
    version of this block hard-coded 1846, 1862, 1874 and 1885 in its prints,
    which would have survived exactly as long as nobody edited the press.

    Returns `(sites, "")` or `(None, why)`. `sites` is `try_opens`, `writes_at`,
    `before_try` and `alarms_at`, every one of them a real line in the file.
    """
    import ast
    path = pathlib.Path(path) if path else WEEKLY_JOB
    if not path.exists():
        return None, f"{path} is not in this checkout"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return None, f"{path} did not parse ({exc})"
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == PRESS_APP), None)
    if fn is None:
        return None, f"{path} defines no `{PRESS_APP}` function"
    handler = next((s for s in fn.body if isinstance(s, ast.Try)), None)
    if handler is None:
        return None, (f"`{PRESS_APP}` carries no try/except, so there is no "
                      f"handler boundary and no zone 3")
    writes = [n.lineno for n in ast.walk(handler)
              if isinstance(n, ast.Call)
              and getattr(n.func, "attr", None) == "record_runtime"]
    if len(writes) != 1:
        return None, (f"`{PRESS_APP}` calls record_runtime {len(writes)} times "
                      f"inside its handler, so the write site is not one line")
    alarms = sorted({n.lineno for h in handler.handlers for n in ast.walk(h)
                     if isinstance(n, ast.Call)
                     and getattr(n.func, "id", None) == "notify_owner"})
    # Only the statements that can actually RAISE, which means the ones
    # carrying a call. An import or a dict lookup ahead of the handler is a
    # line and not a risk, and counting it would inflate zone 3 to flatter the
    # finding. This lands on more lines than the returned note named, not
    # fewer: it finds `bool(week.strip())` and the two `hashlib` digests as
    # well as the four calls that note listed.
    ahead = sorted({s.lineno for s in fn.body if s.lineno < handler.lineno
                    for n in ast.walk(s) if isinstance(n, ast.Call)})
    return {"try_opens": handler.lineno,
            "writes_at": writes[0],
            "before_try": ahead,
            "alarms_at": alarms}, ""


ZONE_RECORDED = "recorded"
ZONE_ALARMED = "alarmed-and-unrecorded"
ZONE_SILENT = "silent"
# The narrowed form of the third zone, and the only one of these four that a
# repository can reach on its own. See `zones_open`.
ZONE_NEVER_INVOKED = "silent, narrowed to never-invoked"

# What each zone is, and the surface that holds the answer. The third column is
# the half of this that matters: a zone whose evidence lives somewhere nothing
# here can read is still a zone, and treating an unreadable surface as a
# surface that does not exist is how one field came to be read as three facts.
# The Modal app name the alarm mail itself tells the owner to check, which is
# the surface zone 3 lives on. Taken from `notify_owner`'s own body rather than
# composed, because a gate that names a slightly wrong app sends its reader to
# an empty page and they conclude the page is the answer.
PRESS_MODAL_APP = "alexandria-weekly"


def zone_words(sites):
    """Each zone as (what the run did, the surface that answers), with the real
    line numbers substituted in from `press_write_site`."""
    ahead = sites["before_try"]
    span = (f"{ahead[0]}-{sites['try_opens'] - 1}" if ahead
            else "nowhere, nothing runs ahead of the handler")
    return {
        ZONE_RECORDED: (
            f"reached line {sites['writes_at']} and the row landed",
            "this receipt"),
        ZONE_ALARMED: (
            f"entered the handler at {sites['try_opens']} and died before "
            f"line {sites['writes_at']}",
            f"the owner's inbox, subject ALARM_SUBJECT_CANNOT_PRINT, mailed "
            f"from line {sites['alarms_at'][-1] if sites['alarms_at'] else '?'}"),
        ZONE_SILENT: (
            f"died in one of the {len(ahead)} calls ahead of the handler "
            f"({span}), or was never invoked at all",
            f"modal app logs {PRESS_MODAL_APP}, which no instrument here "
            f"reads"),
        ZONE_NEVER_INVOKED: (
            f"was never invoked. The {len(ahead)} calls ahead of the handler "
            f"({span}) are excluded, not unread: this image got past all of "
            f"them when it printed the newest edition, and none of them reads "
            f"anything that changed since",
            f"modal app list, or the fact that a later firing moves this row "
            f"at all"),
    }



def zones_open(slot_fired, record_fresh, printed_on_this_image=False):
    """Which zones a receipt reading leaves open. Never fewer than it does.

    Three booleans in: did a slot come due after the newest edition, is there a
    run record newer than that edition, and did the image named on that record
    produce the newest edition itself.

    **The third one is the only narrowing available without asking a human, and
    it is worth the parameter.** When the recorded run IS the run that printed
    the newest edition, the row's digest is the digest of an image that
    demonstrably got past every line ahead of the handler. Nothing in those
    lines depends on the week: `press_write_site` names them, and on the press
    today they are a `bool(.strip())`, the calendar read, the window
    arithmetic, two `open()` calls on files baked into that image, and two
    `hashlib` digests of what those calls returned. An identical image invoked
    on a later Monday cannot fail there, because there is nothing for it to
    fail on that changed. So zone 3 collapses to its never-invoked half and the
    two zones that stay open are the two the owner's inbox separates.

    That narrowing is an inference and this function marks it as one by
    returning a different zone name rather than the same name with fewer
    members. The condition is printed beside it, because a caller that cannot
    see the condition cannot tell a narrowing from a measurement.

    The count is **two** where the returned correction said three, and the
    difference is worth carrying rather than rounding off. `record_runtime`
    never raises on any path: its docstring says so and its write runs inside
    `conn.transaction()`, so a failed write returns the string "NOT recorded"
    to a caller that prints it and the run continues. So a run CAN reach 1885,
    leave the field frozen, and go on -- which means `ZONE_RECORDED` is not
    excluded by a frozen field the way a line count alone suggests. But that
    path is observationally identical to `ZONE_ALARMED` when the run then
    fails, and excluded by a moved `newest_week` when it succeeds. It is a
    fourth way INTO the second zone and not a third answer out of it.

    So the zones partition the code in three and the receipt distinguishes two,
    and the one question that separates those two is the owner's inbox.
    """
    if not slot_fired:
        return ()
    if record_fresh:
        return (ZONE_RECORDED,)
    if printed_on_this_image:
        return (ZONE_ALARMED, ZONE_NEVER_INVOKED)
    return (ZONE_ALARMED, ZONE_SILENT)


ZONES_CASES = (
    # Nothing is owed, so there is no zone question to ask.
    (False, False, False, ()),
    (False, True, False, ()),
    (False, False, True, ()),
    # One slot fired, the record frozen, and nothing known about the image.
    # Two zones, and the sentence this replaces named one of them and asked
    # for a redeploy on it.
    (True, False, False, (ZONE_ALARMED, ZONE_SILENT)),
    # The reading of 2026-11-02: the same, except the frozen record IS the run
    # that printed 2026-W42, 81 seconds before its row landed. Zone 3 narrows.
    (True, False, True, (ZONE_ALARMED, ZONE_NEVER_INVOKED)),
    # A slot fired and something wrote the row after the edition. That settles
    # that a run happened. It does not settle that the CRON ran it; see below.
    # The image fact cannot narrow a zone that is already down to one.
    (True, True, False, (ZONE_RECORDED,)),
    (True, True, True, (ZONE_RECORDED,)),
)

# How close to a firing a run record has to sit to be that firing. The live row
# is the calibration: `weekly.recorded_at` 2026-10-19T09:01:21Z against a
# 09:00Z slot, one minute and twenty-one seconds for `check_availability` and
# the connect. Fifteen minutes is generous against that and still tight enough
# that an afternoon `modal run` falls outside it.
SLOT_TOLERANCE_MINUTES = 15


def invocation_window(schedule, when, tolerance=SLOT_TOLERANCE_MINUTES):
    """`slot` if a run record's hour could be the cron's, else `off-slot`.

    This is the limit on the one branch a firing test can settle. The returned
    correction said "a run reaching 1885 proves the schedule is installed", and
    that is one notch stronger than the row can carry. `record_runtime` is on
    the path of EVERY invocation of `weekly`, cron or `modal run
    pipeline/weekly.py::weekly`, and `deploy_runtime`'s columns are app,
    runtime_sha, entrypoint, file_count and three timestamps, where
    `entrypoint` is the literal `APPS[app]` string and names no caller. So the
    row's existence proves a run and the minute is the only thing in it that
    distinguishes the schedule from a hand.

    And the row is one per app, upserted, so a hand run after the slot
    overwrites the cron's own timestamp. The evidence is not merely ambiguous,
    it is erasable by any seat acting in good faith, which is why this prints
    rather than waits to be asked.

    **The paragraph above is true on a date and this function must not assert
    it on every date.** The engineer seat met the same confound from the ingest
    side on 2026-11-02 and returned the half this gate could not see: the
    column list is not a property of the press, it is a property of
    `deploy_runtime`, and `ingest_ids` writes the `ingest` row on the same code
    path the daily cron does. Any job with a second entry point has this, and
    the repair is carded as one column, `invoked_by`, carrying `cron`, `manual`
    or `task`. The day that column lands, "the minute is the only
    discriminator" stops being true, and the sender named that expiry as the
    test of whether the column was worth adding.

    So `caller_field` below reads the row's own keys instead, and this
    function's answer is demoted from the discriminator to corroboration the
    moment the row can name its caller. That is the same discipline
    `press_schedule` applies to the cron and `press_write_site` applies to the
    line numbers, arriving one level up: not a hand-copied line but a
    hand-copied SCHEMA, which rots the same way and more quietly, because
    nothing in a test suite fails when a column is added somewhere else.
    """
    minute, hour, iso = schedule
    at = datetime.datetime(when.year, when.month, when.day, hour, minute,
                           tzinfo=datetime.timezone.utc)
    if when.isoweekday() != iso or when < at:
        return "off-slot"
    if (when - at).total_seconds() > tolerance * 60:
        return "off-slot"
    return "slot"


INVOCATION_CASES = (
    # The live row, which is the calibration: Monday, 81 seconds after 09:00Z.
    ("2026-10-19T09:01:21.333+00:00", "slot"),
    ("2026-11-02T09:00:00+00:00", "slot"),
    # A hand run the same afternoon, which would write this row identically and
    # erase the only evidence today's test produces.
    ("2026-11-02T14:30:00+00:00", "off-slot"),
    # A sibling's Sunday row, the shape that proved the workspace had returned.
    ("2026-11-01T15:00:17.444+00:00", "off-slot"),
    # A minute BEFORE the slot cannot be that firing, and a naive absolute
    # distance would call it one.
    ("2026-11-02T08:59:00+00:00", "off-slot"),
    # Sixteen minutes after, just outside the window.
    ("2026-11-02T09:16:00+00:00", "off-slot"),
)


# The write-site parser, asserted on sources written for it. Every one of the
# three refusals matters more than the happy path: a gate that guesses a line
# number when the shape changed is the hand-kept copy this function replaced.
WRITE_SITE_CASES = (
    ("def weekly(week=''):\n"
     "    w = week_just_ended()\n"
     "    try:\n"
     "        a = check_availability()\n"
     "        print(g().record_runtime(c, 'weekly', __file__)[1])\n"
     "    except Exception as e:\n"
     "        print(notify_owner(S, str(e)))\n"
     "        raise\n",
     {"try_opens": 3, "writes_at": 5, "before_try": [2], "alarms_at": [7]}),
    # No `weekly` at all: the module was renamed or this is the wrong file.
    ("def monthly():\n    pass\n", None),
    # A press with no handler has no boundary, so it has no third zone, and
    # saying so is more useful than reporting two.
    ("def weekly(week=''):\n"
     "    print(g().record_runtime(c, 'weekly', __file__)[1])\n", None),
    # Two write sites inside one handler: the absence of a row no longer
    # corresponds to one line, which is the whole proposition this gate makes.
    ("def weekly(week=''):\n"
     "    try:\n"
     "        print(g().record_runtime(c, 'a', __file__)[1])\n"
     "        print(g().record_runtime(c, 'b', __file__)[1])\n"
     "    except Exception:\n"
     "        raise\n", None),
)


def zones_cases():
    """The zone reading and the invocation window, before any receipt is read."""
    bad = 0
    sites_bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (source, want) in enumerate(WRITE_SITE_CASES):
            f = pathlib.Path(tmp) / f"case{i}.py"
            f.write_text(source)
            got, why = press_write_site(f)
            if want is None:
                if got is not None:
                    sites_bad = 1
                    print(f"  CASE    write-site case {i} should have refused "
                          f"and returned {got}")
                elif not why:
                    sites_bad = 1
                    print(f"  CASE    write-site case {i} refused with no why")
            elif got != want:
                sites_bad = 1
                print(f"  CASE    write-site case {i} wanted {want} and got "
                      f"{got} ({why})")
    print(f"WRITE_SITE_CASES                           "
          f"{len(WRITE_SITE_CASES) - sites_bad} of {len(WRITE_SITE_CASES)}")
    bad |= sites_bad
    for slot_fired, fresh, printed, want in ZONES_CASES:
        got = zones_open(slot_fired, fresh, printed)
        if got != want:
            bad = 1
            print(f"  CASE    zones_open({slot_fired}, {fresh}, {printed}) "
                  f"wanted {want} and got {got}")
    print(f"ZONES_CASES                                "
          f"{len(ZONES_CASES) - bad} of {len(ZONES_CASES)}")
    worse = 0
    sched, _ = press_schedule("0 9 * * 1")
    for stamp, want in INVOCATION_CASES:
        got = invocation_window(
            sched, datetime.datetime.fromisoformat(stamp))
        if got != want:
            worse = 1
            print(f"  CASE    {stamp} wanted {want} and got {got}")
    print(f"INVOCATION_CASES                           "
          f"{len(INVOCATION_CASES) - worse} of {len(INVOCATION_CASES)}")
    return bad | worse | writers_cases()


# ---------------------------------------------------------------------------
# Who could have written the row, which is a question about ENTRY POINTS and
# not about the press.
#
# Added 2026-11-02 from the engineer seat's note `2dc2bae5`, which met this
# gate's confound from the other side. `ingest_ids` is the by-id backfill a
# seat runs to answer a reading-queue line, and it reaches the `ingest` row of
# `deploy_runtime` through the same `upsert_papers` the daily cron goes
# through. So the ambiguity this gate reported as a fact about testing the
# press by hand is a property of the table: any job with a second entry point
# has it, and nothing in the row can tell the two apart.
#
# The three values a caller could honestly claim, from that note: `cron` from a
# scheduled entry point, `manual` from a hand run, `task` from a by-id or
# by-week function somebody asked for. This gate's own printed sentence named
# TWO of them -- "a hand `modal run` writes it identically" -- and the press's
# own signature is `weekly(week: str = "")`, so the third was already live in
# the job this gate was written about.
CALLER_CRON = "cron"
CALLER_MANUAL = "manual"
CALLER_TASK = "task"

# Every key a receipt row might carry the answer under. The gate searches the
# row's OWN keys for one of these rather than asserting that no such column
# exists, because "there is no column naming the caller" is a statement about a
# schema that is already carded to change, and a gate that hard-codes it prints
# a falsehood on the day the column lands and keeps printing it. `invoked_by`
# is the carded name, and the two after it are the names the same column
# would plausibly ship under, and searching three costs nothing.
CALLER_KEYS = ("invoked_by", "invoked_as", "caller")


def caller_field(row):
    """The caller the row names, as `(key, value)`, or `(None, None)`.

    Reads the row's keys. A row that cannot answer returns `(None, None)` and
    the caller above falls back to the minute, which is the fallback with the
    expiry date on it.
    """
    for key in CALLER_KEYS:
        if isinstance(row, dict) and row.get(key):
            return key, str(row[key])
    return None, None


def _decorators(fn):
    """The decorator calls on `fn`, as `(attribute, keyword names)` pairs."""
    import ast
    out = []
    for d in fn.decorator_list:
        node = d.func if isinstance(d, ast.Call) else d
        name = getattr(node, "attr", None) or getattr(node, "id", None)
        kwds = {k.arg for k in (d.keywords if isinstance(d, ast.Call) else [])}
        out.append((name, kwds))
    return out


def _entry_kind(fn):
    """`("cron", ...)`, `("asked", ...)`, or `None` if `fn` is not an entry point.

    An entry point is a function Modal can start: `@app.function(...)` or
    `@app.local_entrypoint()`. Whether it is SCHEDULED is read from the
    presence of a `schedule=` keyword on that decorator, not from a list kept
    here, for the same reason `press_schedule` reads the cron out of the job.
    """
    for name, kwds in _decorators(fn):
        if name in ("function", "local_entrypoint"):
            return CALLER_CRON if "schedule" in kwds else "asked"
    return None


def _called_names(node):
    """Every module-level name `node` calls, including through `.remote()`."""
    import ast
    out = set()
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name):
            out.add(f.id)
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            # `weekly.remote()` and `ingest_ids.remote()`: the caller a
            # `modal run` of the local entrypoint actually goes through.
            out.add(f.value.id)
    return out


def row_writers(app, path):
    """Every entry point that can reach this app's `deploy_runtime` write.

    Returns `(writers, "")` or `(None, why)`. Each writer is
    `{"name", "schedule", "params"}`, where `schedule` is `cron` or `asked`.

    Derived from the module's own call graph rather than declared, because the
    fact this replaces -- how many ways there are into one row -- is exactly
    the kind a hand-kept list gets wrong on the day somebody adds a second
    entry point, which is the day it matters.

    The walk starts at the function CONTAINING the write, which is not always
    an entry point: in `pipeline/ingest.py` the write sits in `upsert_papers`,
    an ordinary helper, and the two entry points that reach it are the daily
    cron and the by-id backfill. Then it closes over callers until the set
    stops growing, so a local entrypoint that calls a scheduled function
    counts as a way in.
    """
    import ast
    path = pathlib.Path(path)
    if not path.exists():
        return None, f"{path} is not in this checkout"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return None, f"{path} did not parse ({exc})"
    funcs = {n.name: n for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef)}
    holders = set()
    for fn in funcs.values():
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call)
                    and getattr(n.func, "attr", None) == "record_runtime"
                    and any(isinstance(a, ast.Constant) and a.value == app
                            for a in n.args)):
                holders.add(fn.name)
    if not holders:
        return None, (f"{path} has no record_runtime write naming `{app}`, so "
                      f"which entry points reach that row is not readable "
                      f"from this file")
    reach = set(holders)
    while True:
        grown = {name for name, fn in funcs.items()
                 if name not in reach and _called_names(fn) & reach}
        if not grown:
            break
        reach |= grown
    writers = []
    for name in sorted(reach):
        kind = _entry_kind(funcs[name])
        if kind is None:
            continue
        writers.append({"name": name, "schedule": kind,
                        "params": [a.arg for a in funcs[name].args.args]})
    if not writers:
        return None, (f"{path} writes the `{app}` row from "
                      f"{', '.join(sorted(holders))}, which no entry point in "
                      f"this file reaches, so nothing here can start it")
    return writers, ""


def caller_values(writers):
    """The values a row for these writers could honestly carry, derived.

    `cron` when some entry point is scheduled. `task` when some entry point
    runs only on request, or when a scheduled one takes an argument that
    changes what it does -- the press's `weekly(week="")` is the second shape
    and it is why this gate's old two-value sentence was wrong about the very
    job it was written for. `manual` whenever there is any entry point at all,
    because every one of them is reachable by `modal run`, which is the whole
    reason the row is erasable.
    """
    out = []
    if any(w["schedule"] == CALLER_CRON for w in writers):
        out.append(CALLER_CRON)
    if writers:
        out.append(CALLER_MANUAL)
    if any(w["schedule"] != CALLER_CRON or w["params"] for w in writers):
        out.append(CALLER_TASK)
    return tuple(out)


# The two real shapes and three refusals. The first two cases are the live
# ones, reduced to their skeletons: the press, where the write is inside the
# scheduled function and a local entrypoint calls it, and ingest, where the
# write is in a helper two entry points share. The refusals matter more than
# the passes, because a gate that guesses an entry-point list when it cannot
# read one puts the invented subject back.
WRITERS_CASES = (
    # The press. One scheduled writer that takes `week`, plus the local
    # entrypoint a `modal run` of the module goes through. Three values, and
    # `task` comes from the parameter rather than from a second function.
    ("import modal\n"
     "@app.function(schedule=modal.Cron('0 9 * * 1'))\n"
     "def weekly(week: str = ''):\n"
     "    try:\n"
     "        print(runtime_guard().record_runtime(conn, 'weekly', __file__))\n"
     "    except Exception:\n"
     "        raise\n"
     "@app.local_entrypoint()\n"
     "def main():\n"
     "    print(weekly.remote())\n",
     "weekly",
     ({"name": "main", "schedule": "asked", "params": []},
      {"name": "weekly", "schedule": "cron", "params": ["week"]}),
     ("cron", "manual", "task")),
    # Ingest, the engineer seat's half. The write is in a helper neither cron
    # nor backfill owns, and the two entry points are indistinguishable in the
    # row they both produce.
    ("import modal\n"
     "def upsert_papers(rows):\n"
     "    print(runtime_guard().record_runtime(conn, 'ingest', __file__))\n"
     "@app.function(schedule=modal.Cron('0 11 * * *'))\n"
     "def ingest():\n"
     "    return upsert_papers(fetch())\n"
     "@app.function()\n"
     "def ingest_ids(ids, tier='b'):\n"
     "    return upsert_papers(fetch_ids(ids))\n",
     "ingest",
     ({"name": "ingest", "schedule": "cron", "params": []},
      {"name": "ingest_ids", "schedule": "asked", "params": ["ids", "tier"]}),
     ("cron", "manual", "task")),
    # One scheduled entry point, no argument, nothing else reaching it. This is
    # the only shape where the minute is genuinely the whole question, and
    # `task` is correctly absent. Without this case the function could return
    # all three values always and still pass.
    ("import modal\n"
     "@app.function(schedule=modal.Cron('0 3 * * *'))\n"
     "def triage():\n"
     "    print(runtime_guard().record_runtime(conn, 'triage', __file__))\n",
     "triage",
     ({"name": "triage", "schedule": "cron", "params": []},),
     ("cron", "manual")),
    # The app is not written here. Refused, because an empty writer list reads
    # as "nothing can write this row", which is the opposite of what an
    # unreadable file means.
    ("def weekly():\n    pass\n", "weekly", None, None),
    # Written, but by nothing any entry point reaches. A helper nobody calls
    # cannot produce the row, and saying so beats reporting zero ways in.
    ("def orphan():\n"
     "    print(runtime_guard().record_runtime(conn, 'weekly', __file__))\n",
     "weekly", None, None),
)

# The receipt row, which is the other half and the half with the clock on it.
# The first case is the row as it exists today and the second is the row the
# carded column produces. Both are asserted now, so the day `invoked_by` lands
# this gate reads it without an edit here and the sentence about the minute
# retires itself.
CALLER_FIELD_CASES = (
    ({"app": "weekly", "recorded_at": "2026-10-19T09:01:21.333+00:00",
      "runtime_sha": "2e313065f5c7", "entrypoint": "pipeline/weekly.py",
      "file_count": 227}, (None, None)),
    ({"app": "weekly", "invoked_by": "cron"}, ("invoked_by", "cron")),
    ({"app": "ingest", "invoked_by": "task"}, ("invoked_by", "task")),
    # An empty string is not an answer. A column that exists and was not
    # written is the row saying nothing, and reading it as a caller named ""
    # would print a blank where the fallback belongs.
    ({"app": "weekly", "invoked_by": ""}, (None, None)),
    ({}, (None, None)),
    (None, (None, None)),
)


def writers_cases():
    """The entry-point walk and the receipt field, before anything live."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (source, app, want, values) in enumerate(WRITERS_CASES):
            f = pathlib.Path(tmp) / f"writer{i}.py"
            f.write_text(source)
            got, why = row_writers(app, f)
            if want is None:
                if got is not None:
                    bad = 1
                    print(f"  CASE    writers case {i} should have refused "
                          f"and returned {got}")
                elif not why:
                    bad = 1
                    print(f"  CASE    writers case {i} refused with no why")
                continue
            if tuple(got or ()) != want:
                bad = 1
                print(f"  CASE    writers case {i} wanted {want} and got "
                      f"{got} ({why})")
                continue
            vals = caller_values(got)
            if vals != values:
                bad = 1
                print(f"  CASE    writers case {i} wanted values {values} "
                      f"and got {vals}")
    print(f"WRITERS_CASES                              "
          f"{len(WRITERS_CASES) - bad} of {len(WRITERS_CASES)}")
    worse = 0
    for row, want in CALLER_FIELD_CASES:
        got = caller_field(row)
        if got != want:
            worse = 1
            print(f"  CASE    caller_field({row!r}) wanted {want} and got "
                  f"{got}")
    print(f"CALLER_FIELD_CASES                         "
          f"{len(CALLER_FIELD_CASES) - worse} of {len(CALLER_FIELD_CASES)}")
    return bad | worse


def cadence():
    """The two verdicts a cadence claim carries, each answered by its own reading.

    The ExO seat owns `docs/agents/quality-claims.md` and this seat is its
    artifact-side gate, which is step 1b of this charter. On 2026-11-02 that
    seat took one improvement from this one and made it step six of its own
    claim sweep: **a cadence claim carries two verdicts and one reading can
    only answer one of them.** This is the half that belongs here, because the
    register's rows are prose and the hedge a candidate has to carry is this
    seat's to draft.

    - **the clock.** Is the claim true of the current period? One reading
      answers it, and the reading is a count of FIRINGS. This is where the
      improvement was paid for: the note that earned it counted two missed
      slots because two weeks had ended, and `slots_between` is the repair.
    - **the record.** Has it been true of every period it covers? No single
      reading answers it, and the register's own words for the growth row are
      that six days between two readings "cannot be recovered from a maximum".
      For the press it CAN be recovered, because every edition is a page that
      either exists or does not, and that is the asymmetry worth having in a
      command rather than in a paragraph.

    Three failure modes, and the third is the one no previous reading of this
    row had asked for.

    - CLOCK, a slot that came due and produced no edition.
    - RECORD, a period inside the served span with no edition and no make-up.
    - UNREACHED, the receipt or the library did not answer. Never a pass: a run
      that cannot read the row and concludes the cadence holds has made the
      mistake this file was built to stop.

    A fourth thing it prints and never grades: which zones a frozen run record
    leaves open. It is not a failure mode because no answer to it changes the
    verdict -- one missed slot fails the clock half whoever missed it -- and it
    is printed anyway because the repair differs by zone and the previous draft
    of this command chose one.

    And it reads the run record beside the output, which is a fourth thing and
    **not** a separation of unscheduled from broken. This docstring claimed
    that separation for one run and the claim was false; `zones_open` above
    carries the correction and the reason. The short form: a frozen run record
    proves that nothing reached `pipeline/weekly.py:1885` and proves nothing
    else, because three calls and a handler boundary sit above that line. A
    fresh one proves a run happened and not that the cron ran it, because the
    row names no caller and the minute is the only discriminator in it.

    What it cannot see, and the second item is new. Whether a slot was served
    and refused upstream, which lives in the platform and not in this receipt.
    **Which zone a frozen record belongs to**, which lives in the owner's inbox
    and in `modal app logs alexandria-weekly`, neither of which any instrument
    here can read: this gate's job is to name the two zones and the surface
    that answers, and then stop. And whether an edition that exists is any
    good, which is every other command in this file.
    """
    rc = cadence_cases()
    print()
    sched, why = press_schedule()
    if sched is None:
        print(f"  FAIL    {why}")
        print("Nothing below was read, because a slot list computed from a")
        print("schedule this gate could not parse is the invented-subject")
        print("defect rather than a weaker version of this answer.")
        return 1
    minute, hour, iso = sched
    day = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
           "Sunday")[iso - 1]
    print(f"the press schedule                         "
          f"{day}s at {hour:02d}:{minute:02d}Z")
    print(f"  read from                                "
          f"pipeline/weekly.py, its own modal.Cron")

    # How many ways there are into this row, which decides how much any
    # reading of it below can mean. Printed before the receipt is fetched,
    # because it is a fact about the repository and holds whether or not the
    # network answers.
    writers, writers_why = row_writers(PRESS_APP, WEEKLY_JOB)
    if writers is None:
        print(f"  UNREACHED entry points: {writers_why}")
        rc = 1
    else:
        values = caller_values(writers)
        print(f"entry points that write this row           {len(writers)}")
        for w in writers:
            how = ("started by the schedule"
                   if w["schedule"] == CALLER_CRON
                   else "started only when a seat asks")
            arg = (f", taking {', '.join(w['params'])}" if w["params"]
                   else "")
            print(f"    {w['name']}  {how}{arg}")
        print(f"  so a caller could honestly claim          "
              f"{', '.join(values)}")
        if len(values) > 1:
            print(f"  and the row names none of them, which is why the "
                  f"reading below")
            print(f"  turns on a minute. This is not a fact about testing the")
            print(f"  press by hand: the engineer seat found the same two-way")
            print(f"  write on `ingest`, where the daily cron and the by-id")
            print(f"  backfill share one helper, so it is a property of")
            print(f"  deploy_runtime and every job with a second door.")

    try:
        sys.path.insert(0, str(ROOT))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_dh", ROOT / "tools" / "delivery_health.py")
        dh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dh)
    except Exception as e:                          # noqa: BLE001
        print(f"  UNREACHED tools/delivery_health.py: {type(e).__name__}: {e}")
        return 1
    doc = receipt_json(dh.RECEIPT_URL)
    if doc is None:
        print("  FAIL    the receipt answered nothing, so this run concludes")
        print("          nothing about the cadence")
        return 1
    press_block = doc.get("press") or {}
    created = press_block.get("created_at")
    newest = press_block.get("newest_week")
    observed = doc.get("observed_at")
    runs = {r.get("app"): r for r in (doc.get("deploy") or [])}
    ran = (runs.get(PRESS_APP) or {}).get("recorded_at")
    if not (created and newest and observed):
        print("  FAIL    the receipt carries no press block, so the newest")
        print("          edition and its hour are both unknown")
        return 1
    since = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = datetime.datetime.fromisoformat(observed.replace("Z", "+00:00"))
    slots = slots_between(sched, since, now)
    periods = periods_between(sched, since, now)
    nxt = next_slot(sched, now)
    print(f"read at                                    "
          f"{observed}, the receipt's own hour")
    print(f"newest edition                             "
          f"{newest}, created {created}")
    print(f"  its age                                  "
          f"{round((now - since).total_seconds() / 86400, 2)} days")
    print()
    print(f"slots that have FIRED since it             {len(slots)}")
    for s in slots:
        print(f"    {s.isoformat()}  for {week_label(s)}")
    print(f"periods that have ENDED since it           {len(periods)}")
    for e in periods:
        print(f"    {e.isoformat()}  closing {week_label(e)}")
    if len(periods) != len(slots):
        print(f"  the two numbers differ by {len(periods) - len(slots)}, which "
              f"is a week that has")
        print("  closed whose slot has not come due. Counting periods here is")
        print("  the error this command was written for.")
    print(f"next slot                                  "
          f"{nxt.isoformat() if nxt else 'unknown'}"
          f"{'' if not nxt else f', in {round((nxt - now).total_seconds() / 3600, 1)}h'}")
    print()

    # The clock half.
    if slots:
        print(f"  FAIL    CLOCK: {len(slots)} slot(s) came due after "
              f"{newest} and produced no edition")
    else:
        print(f"  OK      CLOCK: no slot has come due since {newest}")
    print()

    # Did it run at all? This row answers less than it looks like it answers,
    # and `zones_open` says how much. What it does NOT do any more is name one
    # cause and ask for a repair on it.
    if ran:
        last = datetime.datetime.fromisoformat(ran.replace("Z", "+00:00"))
        print(f"the press last RECORDED a run              {ran}")
        others = sorted((r.get("recorded_at") or "")
                        for a, r in runs.items() if a != PRESS_APP)
        if others:
            print(f"  its siblings' newest run                 {others[-1]}")
        fresh = last > since
        print(f"  newer than the newest edition            "
              f"{'yes' if fresh else 'no'}")
        if fresh:
            # The row's own answer first, the minute only if it has none.
            # Which of these two branches runs is the test the engineer seat
            # named for whether `invoked_by` was worth adding: the day this
            # prints a caller, the sentence below retires itself.
            key, who = caller_field(runs.get(PRESS_APP) or {})
            seen = invocation_window(sched, last)
            if key:
                print(f"  the row names its caller                 "
                      f"{who}, in `{key}`")
                print(f"  consistent with the cron's own slot      {seen}"
                      f"  (corroboration now, not the discriminator)")
                if who != CALLER_CRON:
                    print(f"  so a {who} run wrote this row and the schedule")
                    print("  did not, and this gate can say so without")
                    print("  inferring it from a clock.")
                elif seen == "off-slot":
                    print(f"  the row claims {CALLER_CRON} and its minute is "
                          f"off-slot, which")
                    print("  is the one disagreement worth a human: one of the")
                    print("  two is wrong and this gate cannot say which.")
            else:
                print(f"  consistent with the cron's own slot      {seen}")
                print("  the row names no caller, so this minute is the whole")
                print("  discriminator. That is true until `invoked_by` lands")
                print("  and not after: it is carded in docs/ideas.md by the")
                print("  engineer seat, this gate already reads the column if")
                print("  the receipt carries it, and the line above is the")
                print("  fallback rather than the answer.")
                if seen == "off-slot":
                    print("  so a run wrote this row and the schedule did")
                    print("  not. A hand `modal run` of the cron path and a")
                    print("  `--week` rewrite both write it identically, the")
                    print("  table is one upserted row per app, and this one")
                    print("  has already overwritten whatever the last firing")
                    print("  left.")
        # Is the row's image the image that printed the newest edition? The
        # row carries the digest and `first_seen_at`, so this is readable: the
        # recorded run is that edition's own run when its row landed shortly
        # BEFORE the edition row did, which is the order those two writes
        # happen in (1885, then the `digests` upsert). On this receipt the gap
        # is 91 seconds.
        seen_first = (runs.get(PRESS_APP) or {}).get("first_seen_at")
        printed_on = bool(
            not fresh and 0 <= (since - last).total_seconds()
            <= SLOT_TOLERANCE_MINUTES * 60)
        print(f"  its digest                               "
              f"{(runs.get(PRESS_APP) or {}).get('runtime_sha') or 'none'}"
              f", first seen {seen_first or 'unknown'}")
        print(f"  that run is the one that printed {newest}   "
              f"{'yes' if printed_on else 'no'}")
        open_zones = zones_open(bool(slots), fresh, printed_on)
        sites, site_why = press_write_site()
        if open_zones and sites is None:
            print()
            print(f"  UNREACHED the write site: {site_why}, so this reading")
            print("          cannot name the zones its own absence leaves open")
            rc = 1
        elif open_zones:
            words = zone_words(sites)
            print()
            print(f"  zones this reading leaves open             "
                  f"{len(open_zones)}")
            for z in open_zones:
                what, where = words[z]
                print(f"    {z}")
                print(f"      the run {what}")
                print(f"      answered on: {where}")
        if slots and not fresh:
            print(f"  so the press has not RECORDED a run since that edition,")
            print(f"  and that is one proposition about one line: nothing")
            print(f"  reached {WEEKLY_JOB.relative_to(ROOT)}:"
                  f"{sites['writes_at'] if sites else '?'}. It does not choose")
            print("  between the two zones above, it does not say whether the")
            print("  schedule is installed, and the repair differs by zone, so")
            print("  this gate names neither.")
    else:
        print("the press last RECORDED a run              no row on the receipt")

    # The record half, which needs the series and not the reading.
    print()
    served = served_weeks_cached()
    if served is None:
        print("  FAIL    RECORD: the library did not answer, so the record")
        print("          half is unread and this run concludes nothing on it")
        return 1
    print(f"weeks the product serves                   "
          f"{len(served)}: {', '.join(served)}")
    # Every week the claim covers, which starts at the first edition the
    # product serves and not at the first slot before it. The first draft of
    # this walked from the Monday of 2026-W39 and reported 2026-W38 as a hole,
    # because the firing inside a week labels the week BEFORE it: one slot
    # earlier than the span is one week earlier than the claim. A week whose
    # slot has not come due is not owed yet and is named separately.
    #
    # The labels sort lexicographically because ISO weeks are zero-padded, so
    # `>= first` holds across a year boundary as well as inside one.
    first = min(served)
    span_from = datetime.datetime.fromisoformat(
        datetime.date.fromisocalendar(int(first[:4]), int(first[6:]), 1)
        .isoformat()).replace(tzinfo=datetime.timezone.utc)
    owed = [w for w in (week_label(s)
                        for s in slots_between(sched, span_from, now))
            if w >= first]
    holes = [w for w in owed if w not in served]
    pending = [w for w in (week_label(e)
                           for e in periods_between(sched, span_from, now))
               if w >= first and w not in owed]
    # The archive and the record are two different answers to "which weeks
    # exist", and `site/lib/issues-core.js` says the record decides. Where the
    # checkout carries an edition the library does not serve, the span above
    # starts later than the oldest file, and that is worth one printed line
    # rather than a failure: whether a committed week should be served is the
    # frontend seat's surface and this gate reads the served set on purpose.
    filed = sorted(p.stem for p in (ROOT / "site/content/issues").glob("*.md"))
    older = [w for w in filed if w < first]
    if older:
        print(f"  in the checkout and not served            "
              f"{', '.join(older)}, so the span above starts at {first}")
    print(f"  weeks whose slot has fired since {first}  {len(owed)}")
    print(f"  of those, served                         {len(owed) - len(holes)}")
    print(f"  closed but not yet due                   "
          f"{', '.join(pending) if pending else 'none'}")
    if holes:
        print(f"  FAIL    RECORD: {len(holes)} week(s) had a slot fire and "
              f"carry no edition")
        for w in holes:
            print(f"            {w}")
        print("          A missed week stays missed unless something makes it")
        print("          up, so this half cannot be repaired by the next")
        print("          firing and the claim's universal reading stays false.")
    else:
        print(f"  OK      RECORD: every week with a fired slot since {first} "
              f"is served")
    print()
    print("A cadence sentence asserts both halves at once, so a candidate")
    print("hedged against the clock and silent about the record is still")
    print("printing a false universal. Which half failed decides the hedge:")
    print("a clock failure is softened by naming the gap, and a record")
    print("failure is only honest if the claim stops being universal.")
    return rc | bool(slots) | bool(holes)


# Which law each undeployed generator patch reaches. `press` says the press is
# twelve days and twenty-eight commits behind. This says what is in those
# twenty-eight, which is the fact the charter's structure-watch step turns on.
LAW_CITED = re.compile(r"\blaw (\d+[a-z]?)\b", re.I)


def law_anchors(text):
    """Every `law N` citation in a generator, as (line number, label)."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in LAW_CITED.finditer(line):
            out.append((n, m.group(1)))
    return out


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def changed_lines(diff):
    """The new-side line numbers a `-U0` unified diff writes.

    A pure deletion writes none, and git prints it as `+c,0`. Attributing
    that to nothing loses every revert in the queue, and there is one:
    `0251df0b` reverts law 8's url patch. So a deletion attributes to the
    position the text left rather than to no law at all.
    """
    out = []
    for line in diff.splitlines():
        m = HUNK.match(line)
        if not m:
            continue
        start = int(m.group(1))
        count = 1 if m.group(2) is None else int(m.group(2))
        if count == 0:
            out.append(max(1, start))
        else:
            out.extend(range(start, start + count))
    return out


def law_spans(anchors, lines):
    """How many lines each law's citations own, by the rule below.

    Printed next to a positional count so a reader can discount it. Law 12a's
    citations own 325 lines of a 2,191-line generator and law 1's own 305, so
    between them they own 29% of the file, and a commit that lands anywhere in
    that 29% attributes to one of them whether or not it meant to. A count
    without its span reads like evidence. With its span it reads like what it
    is.
    """
    marks = sorted(anchors)
    out = {}
    for i, (n, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else lines
        out[label] = out.get(label, 0) + max(0, end - n)
    return out


def laws_touched(anchors, changed, message=""):
    """The laws a commit reaches, in two strengths of evidence and never one.

    `named` is what the commit's own message cites. This charter already
    requires a prompt diff to cite the law it serves, so a message that does
    is the author's own claim about their change and it is the reading a run
    can act on.

    `nearby` is position alone: the nearest citation at or above a changed
    line, because the generator is organised that way, the line naming a law
    followed by the prose serving it. It is a lead and not an answer, and the
    first version of this function returned the union of the two under one
    name. On the live queue that version answered that law 12a was worked by
    21 of 28 commits, which contradicted the grade written two hours earlier
    and was wrong: 12a's citations own a 325-line span, so the number measured
    citation sparsity rather than anybody's intent. A flattering instrument is
    worse than none, and an instrument that is confidently flattering about
    the one law with no patch is the worst available case.

    `orphan` counts changed lines above the first citation. They belong to no
    law and are reported rather than folded into law 1, which is what the
    obvious boundary bug here would do.
    """
    marks = sorted(anchors)
    named = {m.group(1) for m in LAW_CITED.finditer(message)}
    nearby = set()
    orphan = 0
    for line in changed:
        best = None
        for n, label in marks:
            if n > line:
                break
            best = label
        if best is None:
            orphan += 1
        else:
            nearby.add(best)
    return named, nearby, orphan


#: Laws whose decision does not live in the generator any more, because the
#: charter's structure-watch step sent it to code. One row per law, and a row
#: is written here only when the fix is merged on `main`.
#:
#: This table exists because the command below reads one file. Its whole input
#: is the commit list for `prompts/digest.md`, so a law the charter's own step
#: 4 escalated out of the prompt is invisible to it, and the verdict it prints
#: for that law is UNNAMED or UNPATCHED: read the span, nothing is coming. The
#: instrument tells the seat to do the thing step 4 forbids, and the better a
#: seat obeys the charter the more laws arrive in that state.
#:
#: Law 8 is the live instance and it cost a grade on 2026-11-09. `queued 8`
#: read UNNAMED, the review concluded a prompt diff was owed and named it as
#: the next run's item, and the fix had been merged seven days earlier in
#: `pipeline/arxiv_html.py`, which decides the url with a HEAD request instead
#: of asking a model to rewrite one. The abs-to-html rewrite had been reworded
#: six times with one revert before that, which is the history the module's own
#: docstring carries.
MOVED_LAWS = {
    "8": {
        "module": "pipeline/arxiv_html.py",
        "wired_in": "pipeline/weekly.py",
        "wiring": "arxiv_html().resolve_payload(",
        "commit": "3cd597a4",
        "escalated": "writer run 51 on 2026-10-26, after the fourth wording "
                     "was written and reverted inside one run",
    },
}


def moved_fix(label, show=None, delivered=None):
    """The row for a law whose fix left the generator, and whether it is live.

    A declared row is a claim about another seat's file, so it is checked
    rather than trusted. The check is the one substring that proves the call
    is still there on `main`, read off `origin/main` and not off the branch,
    for the same reason the spans below are. A fix that was escalated, built
    and then unwired is not a fix, and it must not read as one here: that is
    the same mistake `drop_reverted` fixes one storey down, where a patch and
    its own revert counted as two patches.

    `delivered` is the deploy's half and the caller supplies it, because this
    function knows nothing about the press. Both answers are OK verdicts and
    they ask for different things: an undelivered fix asks for the deploy, and
    a delivered one that still fails live is the code's defect and the
    engineer's. Neither of them asks for a word in the generator.
    """
    row = MOVED_LAWS.get(label)
    if row is None:
        return None
    if show is None:
        def show(path):
            return "\n".join(_git_lines("show", f"origin/main:{path}"))
    text = show(row["wired_in"])
    return dict(row, wired=row["wiring"] in text, delivered=delivered)


def queued_verdict(label, named, nearby, span, moved=None):
    """One law's structure-watch answer, from the queue alone.

    Six answers, because the queue supports six and not two.

    MOVED: the law's decision does not live in the generator at all, because
    the charter's structure-watch step sent it to code and the code is merged.
    `MOVED_LAWS` declares it and `moved_fix` checks the call is still there, so
    the verdict is a reading and not a note. It is first, above every answer
    the queue can give, because once a law is decided by a function every
    wording of it in the prompt is the tinker step 4 refuses, and the queue
    will go on saying UNNAMED about that law for as long as the generator keeps
    the dead prose. The thing owed is the deploy, or nothing.

    UNWIRED: a law this table declares as moved, whose call is not in the file
    on `main` any more. The escalated fix was built and then unwired, so no fix
    is anywhere, and this is the only verdict here that names another seat:
    restoring the call is the engineer's and a wording would paper over it.

    QUEUED: a merged commit the press has not received says in its own message
    that it works this law. A fresh wording is the third tinker the charter's
    structure-watch step refuses, and the grade says the patch is waiting on a
    deploy.

    UNNAMED: commits landed inside this law's span and none said so. The grade
    cannot conclude either way from here and reads those commits. On
    2026-10-27 this covered 26 of the 28 queued commits, so it is the ordinary
    case rather than the edge one.

    UNCITED: the generator never names this law, so it owns no span and the
    queue cannot be asked about it at all. This is not a reading about the
    queue and it must never be printed as one, because the verdict that looks
    like it from the outside is UNPATCHED and acting on that would mean
    writing a rule the generator already carries. Five laws were in this state
    when the command was written, 3, 7, 8, 10 and 16, two of them failures in
    the live grade.

    UNPATCHED: the law is cited, it owns a span, and nothing in the queue
    touches it by either reading. So the fix is not waiting on a deploy, and
    that is the whole of what this verdict establishes.

    **It is not "the generator lacks this rule", and it was read that way on
    2026-11-01.** This command reads the queue. Whether the file already
    carries the rule is a question about the file, and the two answers come
    apart exactly when a rule is present, complete, and disobeyed, which is
    the commonest interesting case a grade meets. That run failed laws 5 and 9
    on the live issue, read UNPATCHED on both, wrote a patch for each, and then
    found both rules already in the generator in full: law 5 at the traction
    slot, "Work that has not actually compounded does not belong in this
    section at all", and law 9 at the opening, "never open with a finding cold
    ... Why comes before what", scoped there to all four jobs. Both patches
    were reverted before the commit. A law whose rule is present and broken is
    the charter's structure-watch case and not a prompt case, and no reading of
    the queue can tell you which one you are in.

    None of the four says the patch is correct. They say whether one exists
    and has not reached the press, which is all a grade can establish before
    the deploy.
    """
    if moved and moved.get("wired"):
        press = ("the press has it, so a live failure of this law is the "
                 "code's and goes to the engineer"
                 if moved.get("delivered") else
                 "the press has not received it, so the deploy is the whole "
                 "of what is owed")
        return "MOVED", (f"law {label} is decided by {moved['module']} as of "
                         f"{moved['commit']}, not by the generator, and "
                         f"{press}: no wording is owed and the queue's answer "
                         f"about this law is not about its fix")
    if moved:
        return "UNWIRED", (f"law {label}'s fix was escalated to "
                           f"{moved['module']} and {moved['wired_in']} does "
                           f"not call it on main, so the fix is gone rather "
                           f"than waiting: restoring the call is the "
                           f"engineer's and a wording would hide it")
    if named:
        return "QUEUED", (f"law {label} is named by {len(named)} queued "
                          f"commit(s), so a fresh wording is the tinker the "
                          f"structure-watch step refuses")
    if nearby:
        return "UNNAMED", (f"{len(nearby)} queued commit(s) landed in law "
                           f"{label}'s span and none names it, so read them "
                           f"before writing or refusing a patch")
    if not span:
        return "UNCITED", (f"the generator never names law {label}, so it "
                           f"owns no span and the queue cannot be asked about "
                           f"it: this is a gap in the generator's citations "
                           f"and not a reading about the patch")
    return "UNPATCHED", (f"no queued commit reaches law {label} by either "
                         f"reading, so the fix is not waiting on the deploy: "
                         f"read the law's own span in the generator before "
                         f"writing, because this answers the queue and never "
                         f"the file")


CHANGED_CASES = [
    ("@@ -1,2 +1,3 @@", [1, 2, 3]),
    # A pure deletion. The revert in the live queue has this shape.
    ("@@ -40,6 +39,0 @@", [39]),
    # One line for one line, which git prints without the counts.
    ("@@ -5 +5 @@", [5]),
    # Two hunks in one commit, which is the ordinary generator patch.
    ("@@ -5 +5 @@\n@@ -20,0 +21,2 @@", [5, 21, 22]),
]

LAWS_CASES = [
    # A change inside law 14's span, by position and not by name.
    ([(10, "14"), (40, "1")], [20], "", set(), {"14"}, 0),
    # A change below the last citation belongs to that one and not the first.
    ([(10, "14"), (40, "1")], [99], "", set(), {"1"}, 0),
    # Above every citation is nobody's law, counted rather than folded in.
    ([(10, "14")], [3], "", set(), set(), 1),
    # The message's own citation is the strong reading and needs no changed
    # line, which is what the charter asks a prompt diff to carry.
    ([(10, "14")], [], "Generator: law 8's url at the three write points",
     {"8"}, set(), 0),
    # Named and nearby disagree, which is the case that must not be merged:
    # the message says 8 and the lines sit under 14. Both are reported.
    ([(10, "14")], [20], "Generator: law 8's url at three write points",
     {"8"}, {"14"}, 0),
    # A sub-lettered law is its own label. Folding 12a into 12 would answer a
    # density failure with the heading patch.
    ([(10, "12"), (50, "12a")], [60], "", set(), {"12a"}, 0),
]

SPAN_CASES = [
    # A law cited twice owns both of its stretches, which is why the live
    # reading has to sum them rather than take the widest.
    ([(10, "1"), (20, "14"), (30, "1")], 50, {"1": 30, "14": 10}),
    # The last citation owns everything to the end of the file.
    ([(10, "6")], 100, {"6": 90}),
]

#: `moved_fix`'s two readings and the two verdicts they produce, with a stub
#: `show` so no case touches git. The third case is the one that matters: a
#: declared row whose call has gone must not read as a fix.
MOVED_CASES = [
    ("8", "probe = law8_probe or arxiv_html().resolve_payload(payload)",
     False, "MOVED"),
    ("8", "probe = law8_probe or arxiv_html().resolve_payload(payload)",
     True, "MOVED"),
    ("8", "# the law 8 step was taken out again", False, "UNWIRED"),
]

VERDICT_CASES = [
    (["c5a32e4c"], [], 40, "QUEUED"),
    ([], ["2c6ce635", "31d3fb23"], 103, "UNNAMED"),
    # Cited, with a span, and nothing in the queue: this run's work.
    ([], [], 103, "UNPATCHED"),
    # No span means no citation, and the answer is about the generator rather
    # than about the queue. Returning UNPATCHED here is the failure that would
    # send a run to reword a rule the generator already carries.
    ([], [], 0, "UNCITED"),
]


def queued_cases():
    """The three pure halves against their cases, with no git and no network."""
    rc = 0
    bad = 0
    for diff, want in CHANGED_CASES:
        got = changed_lines(diff)
        if got != want:
            bad += 1
            print(f"  FAIL    changed_lines wanted {want} and got {got}")
    print(f"CHANGED_CASES                              "
          f"{len(CHANGED_CASES) - bad} of {len(CHANGED_CASES)}")
    rc |= bool(bad)
    bad = 0
    for anchors, changed, msg, wname, wnear, worph in LAWS_CASES:
        named, nearby, orphan = laws_touched(anchors, changed, msg)
        if named != wname or nearby != wnear or orphan != worph:
            bad += 1
            print(f"  FAIL    laws_touched wanted "
                  f"{sorted(wname)}/{sorted(wnear)}/{worph} and got "
                  f"{sorted(named)}/{sorted(nearby)}/{orphan}")
    print(f"LAWS_CASES                                 "
          f"{len(LAWS_CASES) - bad} of {len(LAWS_CASES)}")
    rc |= bool(bad)
    bad = 0
    for anchors, lines, want in SPAN_CASES:
        got = law_spans(anchors, lines)
        if got != want:
            bad += 1
            print(f"  FAIL    law_spans wanted {want} and got {got}")
    print(f"SPAN_CASES                                 "
          f"{len(SPAN_CASES) - bad} of {len(SPAN_CASES)}")
    rc |= bool(bad)
    bad = 0
    for label, wiring, delivered, want in MOVED_CASES:
        row = moved_fix(label, show=lambda _p, t=wiring: t,
                        delivered=delivered)
        got, _ = queued_verdict(label, [], [], 0, moved=row)
        if got != want:
            bad += 1
            print(f"  FAIL    moved law {label} wanted {want} and got {got}")
    if moved_fix("99", show=lambda _p: "") is not None:
        bad += 1
        print("  FAIL    an undeclared law read as moved")
    print(f"MOVED_CASES                                "
          f"{len(MOVED_CASES) - bad} of {len(MOVED_CASES)}")
    rc |= bool(bad)
    bad = 0
    for named, nearby, span, want in VERDICT_CASES:
        got, _ = queued_verdict("14", named, nearby, span)
        if got != want:
            bad += 1
            print(f"  FAIL    queued_verdict wanted {want} and got {got}")
    print(f"VERDICT_CASES                              "
          f"{len(VERDICT_CASES) - bad} of {len(VERDICT_CASES)}")
    return rc | bool(bad)


def _law_sort(label):
    """Law order as a reader of the canon expects it: 12 before 12a."""
    m = re.match(r"(\d+)([a-z]*)", label)
    return (int(m.group(1)), m.group(2)) if m else (999, label)


def drop_reverted(rows):
    """The queue with every revert and the commit it reverts removed.

    A commit and its own revert both name the law in their subject, because
    `git revert` keeps the subject and prefixes it. So the pair counts twice
    and `queued` reads two commits working the law, which is the QUEUED
    verdict, which tells a grade the fix is merged and waiting on a deploy and
    to write nothing. For a pair that cancels there is no fix anywhere.

    This was live on law 8 on 2026-11-01 and it cost that grade a verdict.
    `c5a32e4c` wrote law 8's url form and `0251df0b` reverted it inside the
    same run; `git diff c5a32e4c~1 0251df0b -- prompts/digest.md` is empty. The
    command reported "law 8 is named by 2 queued commit(s), so a fresh wording
    is the tinker the structure-watch step refuses" while nine of the ten links
    on the live issue stopped at the abstract page, which is the one state the
    canon names as the worst this instrument can reach: an instrument
    flattering about the one law with no patch.
    """
    subjects = {}
    for row in rows:
        parts = row.split("\t")
        if len(parts) > 1:
            subjects.setdefault(parts[1], []).append(row)
    drop = set()
    for row in rows:
        parts = row.split("\t")
        subject = parts[1] if len(parts) > 1 else ""
        if not subject.startswith('Revert "') or not subject.endswith('"'):
            continue
        original = subject[len('Revert "'):-1]
        if original in subjects:
            drop.add(row)
            drop.update(subjects[original])
    return [r for r in rows if r not in drop], len(drop)


def queued(labels=()):
    """Which law each undeployed generator patch reaches.

    The charter's structure-watch step says a structural fix that has failed
    twice through prompt changes goes to the ledger rather than into a third
    wording. Running that step needs one fact for each failed law: whether a
    patch for it is already merged and waiting on a deploy. Four consecutive
    runs established that fact by hand, out of commit subjects and memory, and
    wrote it into the review as prose. The 2026-10-27 grade's section on why it
    shipped no prompt diff is three paragraphs of this derivation and nothing
    else, and the run before it refused a fourth wording of law 1 the same way.

    It is mechanical, because the generator names the law each rule serves
    inline, twenty-six times. Take the queued commits, take the lines each one
    wrote, and read the citation standing above them.

    The answer is per law and never one verdict, because the queue is almost
    never empty and almost never complete. A run reads its failed laws off the
    grade and looks them up here. Pass them as arguments to get the verdicts
    alone: `check_voice.py queued 1 8 12a 14`.

    An unreached receipt is a failure. A run that cannot read the queue and
    concludes a law is unpatched would write the fifth wording of a rule that
    is already fixed, which is the exact waste this command exists to prevent.
    """
    rc = queued_cases()
    print()
    found = press_deploy()
    if found is None:
        print("    nothing was read, so no law is called unpatched")
        return 1
    if "why" in found:
        print(f"  FAIL    REFUSED: {found['why']}")
        print("    the queue could not be bounded, so no law is called")
        print("    unpatched and the structure-watch step has no input")
        return 1
    deployed = found.get("deployed_commit")
    rows = _git_lines("log", "--format=%h%x09%s",
                      f"{deployed}..origin/main", "--", PRESS_FILE)
    rows, cancelled = drop_reverted(rows)
    named_by = {}
    nearby_by = {}
    orphans = 0
    unnamed = 0
    for row in rows:
        parts = row.split("\t")
        sha = parts[0]
        subject = parts[1] if len(parts) > 1 else ""
        text = "\n".join(_git_lines("show", f"{sha}:{PRESS_FILE}"))
        diff = "\n".join(_git_lines("show", sha, "-U0", "--format=",
                                    "--", PRESS_FILE))
        named, nearby, orphan = laws_touched(
            law_anchors(text), changed_lines(diff), subject)
        orphans += orphan
        if not named:
            unnamed += 1
        line = f"{sha} {subject}"
        for label in named:
            named_by.setdefault(label, []).append(line)
        for label in nearby:
            nearby_by.setdefault(label, []).append(line)
    # The spans come off origin/main and not off the branch, because the queue
    # is measured `deployed..origin/main` and a span read anywhere else would
    # discount a count taken against a file that never produced it.
    spans = law_spans(law_anchors(
        "\n".join(_git_lines("show", f"origin/main:{PRESS_FILE}"))),
        len(_git_lines("show", f"origin/main:{PRESS_FILE}")))
    print(f"deployed commit                            "
          f"{deployed or 'unknown'}")
    print(f"queued commits to the generator            {len(rows)}")
    print(f"of those, dropped as a cancelling revert    {cancelled}")
    print(f"of those, naming the law they serve        {len(rows) - unnamed}")
    print(f"changed lines under no citation            {orphans}")
    print()
    for label in sorted(set(named_by) | set(nearby_by), key=_law_sort):
        nm = named_by.get(label, [])
        nb = nearby_by.get(label, [])
        print(f"  law {label:<4}  {len(nm):>2} named  {len(nb):>2} in a span "
              f"of {spans.get(label, 0)} lines")
        for c in nm[:2]:
            print(f"              named   {c[:66]}")
        for c in nb[:2] if not nm else []:
            print(f"              nearby  {c[:66]}")
    if labels:
        print()
        for label in labels:
            row = MOVED_LAWS.get(label)
            moved = moved_fix(
                label,
                delivered=bool(row) and bool(deployed) and _git_ok(
                    "merge-base", "--is-ancestor", row["commit"], deployed))
            verdict, why = queued_verdict(label, named_by.get(label, []),
                                          nearby_by.get(label, []),
                                          spans.get(label, 0), moved=moved)
            mark = "OK  " if verdict in OK_VERDICTS else "FAIL"
            print(f"  {mark}    {verdict}: {why}")
            rc |= verdict not in OK_VERDICTS
    print()
    print("A law a queued commit names is fixed and undelivered, so the grade")
    print("that fails it says so and writes nothing. A law nothing reaches")
    print("is not waiting on a deploy, which is not the same as the generator")
    print("lacking the rule: read its span before you write. In between is")
    print("UNNAMED, which was 26 of 28 commits")
    print("the day this was written, and that number is the finding: the")
    print("charter asks a prompt diff to cite the law it serves and the")
    print("citation has been going into the review rather than the commit,")
    print("which is why four runs rebuilt this fact from memory.")
    print()
    print("None of that reaches a law this prompt no longer decides. The")
    print("queue read here is one file's, so a law the structure-watch step")
    print("sent to code is MOVED, and the queue's silence about it is not a")
    print("reading about its fix. Law 8 is that law today.")
    return rc


def _git_line(*args):
    out = _git_lines(*args)
    return out[0] if out else None


#: The verdicts that ask for no prompt diff. QUEUED and MOVED both mean a fix
#: exists and the generator is the wrong lever, so a run that reads either one
#: writes nothing and says which deploy it is waiting on.
OK_VERDICTS = ("QUEUED", "MOVED")


def _git_ok(*args):
    """A git command's exit status, for the questions whose answer is yes or no.

    `_git_lines` reads stdout and `merge-base --is-ancestor` prints nothing, so
    reading it through that helper makes every answer look the same. An error
    is False rather than True: an unreachable git must not report a commit as
    deployed.
    """
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def _git_lines(*args):
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return []
    return [x for x in r.stdout.splitlines() if x.strip()]


# The dispatcher's own contract, as a function, so it can be asserted.
#
# `which` is the name a caller typed. `names` is every name this file answers
# to. The return is the process exit code the dispatcher owes that pair, and
# the only interesting value is the one it did not have until 2026-11-02: a
# name this file does not carry is a USAGE failure, distinct from a gate that
# ran and failed, and never a pass.
DISPATCH_UNKNOWN = 2


def _dispatch_rc(which, names):
    return 0 if which in (set(names) | {"all"}) else DISPATCH_UNKNOWN


# The same defect one level down, found on 2026-11-02 by asking exo's own
# question of this file: where else does a gate report success by saying
# nothing? The dispatcher now refuses a NAME this file does not carry, and it
# still accepted a TARGET this file could not read. `measure`, `links`,
# `firstuse` and `provenance` each printed a verdict and exited 0 when handed a
# path that does not exist, `captions` printed its asserted-case count and
# never mentioned the path at all, and `standalone` raised a traceback, while
# `delivery`, `devices`, `marks` and `specimens` returned 1 on that same
# condition. So one file answered one question four ways, and the majority
# answer was a pass about an artifact nobody had opened.
#
# `exists` is a parameter and not a call, so the cases below assert the
# resolver without putting files on disk. That is the property that makes the
# dispatcher's own repair worth trusting and it is cheap to keep.
def missing_targets(named, exists):
    """The targets a caller named that are not there to be graded."""
    return [p for p in named if not exists(p)]


# The declared sets a caller's paths select. Returning nothing when the caller
# named paths is the condition `captions` could not see: its selection is a
# filter over a fixed table, so a path outside that table emptied the loop and
# left only the asserted-case line, which reads as a clean pass.
def selected_sets(known, named):
    """The members of `known` that `named` asks for, or all of them if none."""
    return [row for row in known if not named or row[0] in named]


# The subcommands whose arguments are paths. Hoisted to module scope so `main`
# and the asserted cases read ONE table instead of two copies of it, because a
# hand-copied schema rots exactly the way a hand-copied line number does.
#
# `queued` is in it because `main` routes arguments to it, and out of
# PATH_ARG_COMMANDS because those arguments are canon law labels rather than
# paths. `reading` is new here as of 2026-11-02: it resolves paths at its own
# first line and the dispatcher had never passed it any, so
# `check_voice.py reading <an edition>` read 63 unrelated surfaces and printed
# the verdict under the caller's path. That is ban list 91 in the file that
# enforces ban list 91, and this table is the thing that was built to stop it.
TAKES_PATHS = ("measure", "links", "delivery", "compare", "firstuse",
               "queued", "claims", "reading",
               "generator", "specimens", "standalone", "devices",
               "captions", "marks", "provenance", "slotheads",
               "apparatus", "figures")
PATH_ARG_COMMANDS = tuple(x for x in TAKES_PATHS if x != "queued")


# Asserted because the defect this repairs was invisible by construction: the
# old dispatcher's wrong answer was silence and exit 0, which is also what a
# clean pass looks like, so no run could tell the two apart and none did for
# as long as the file has existed.
DISPATCH_CASES = (
    # The live case that found it. `cadence` shipped on an unmerged branch, so
    # on `main` it is an unknown name, and the ExO seat read exit 0 and no
    # output as "nothing to report".
    ("cadence", ("press", "queued"), DISPATCH_UNKNOWN),
    # The same name, once the branch carrying it has merged.
    ("cadence", ("press", "queued", "cadence"), 0),
    # A nonsense argument, which behaved identically to the real subcommand
    # and is the proof that the silence was about the dispatcher and not about
    # any one gate.
    ("zzznosuch", ("press", "queued", "cadence"), DISPATCH_UNKNOWN),
    # `all` is not in the table and is always known.
    ("all", ("press",), 0),
    # The empty table still owes an answer rather than an exception.
    ("press", (), DISPATCH_UNKNOWN),
    ("all", (), 0),
)


# A target is named, nothing is there, and the answer must not be a pass. The
# `exists` predicate is a dict lookup here, so these cases pin the resolver and
# not the filesystem.
TARGET_CASES = (
    # The live shape. A caller names an edition, the path is wrong by one
    # character, and five gates graded their default scope and exited 0.
    (("site/content/issues/2026-W41.md",), ("site/content/issues/2026-W39.md",),
     ("site/content/issues/2026-W41.md",)),
    # The ordinary pass. Everything named is there, so nothing is returned and
    # `main` proceeds to the gate.
    (("site/content/issues/2026-W39.md",), ("site/content/issues/2026-W39.md",),
     ()),
    # Order is preserved and every absent target is named, because a caller
    # who mistyped two of four needs both rather than the first.
    (("a.md", "b.md", "c.md"), ("b.md",), ("a.md", "c.md")),
    # No arguments at all is the default scope and never a missing target.
    ((), ("a.md",), ()),
    # `--live` hands this absolute paths outside the repository. They exist, so
    # the check must not refuse the one command that reads what readers open.
    (("/tmp/served/2026-W42.md",), ("/tmp/served/2026-W42.md",), ()),
)

# The two tables this file routes arguments by, asserted against the gates
# that actually accept them rather than against a copy of the list. The prefix
# is not decoration: `ROUTING_CASES` is already taken at line 4464 by
# `routed_cases`, and this run shadowed it for one commit. That crash was loud,
# which is the one mercy in the class this diff is about.
ARG_ROUTING_CASES = (
    # `reading` resolves paths at its own first line, so it must be routed
    # them. It was not until 2026-11-02.
    ("reading", True, True),
    # `queued` takes canon law labels, so it is routed arguments and is not
    # path-checked.
    ("queued", True, False),
    # An ordinary path gate is both.
    ("measure", True, True),
    # A gate that takes no arguments is neither.
    ("taste", False, False),
    # `editions` takes none as of 2026-11-02, having accepted and ignored one.
    ("editions", False, False),
)

# `captions` filters a fixed table, so a path outside it empties the selection.
SELECTION_CASES = (
    # No paths named is the whole table, which is the `all` run.
    ((("a.jsx", "A"), ("b.jsx", "B")), (), 2),
    # One named member selects itself.
    ((("a.jsx", "A"), ("b.jsx", "B")), ("a.jsx",), 1),
    # The defect: a real path that is not a declared set selects nothing, and
    # the gate must say so rather than print its own case count and exit 0.
    ((("a.jsx", "A"), ("b.jsx", "B")), ("site/content/issues/2026-W39.md",), 0),
)


def dispatch():
    """Assert that a request this file cannot answer is never reported as a pass.

    This gate is about this file and not about an edition, which is why it
    asserts and reads nothing. It is in `all` because it is nineteen
    comparisons and because the thing it protects is the one defect class that
    cannot be caught by reading output: the output is empty either way.

    Four tables, one question, asked at the three altitudes a request can be
    dropped at. DISPATCH_CASES is the subcommand NAME, which was the instance
    the ExO seat found on 2026-11-02 by running a gate that had shipped only on
    a branch. TARGET_CASES is the path ARGUMENT, nine gates deep, found the
    same night by asking that seat's own generalisation of its own file: the
    class "will produce a seventh instance anywhere a gate reports success by
    saying nothing". `ARG_ROUTING_CASES` is the table that decides whether an
    argument reaches the gate at all, which is how `reading` came to resolve
    paths it was never given. SELECTION_CASES is the filter inside `captions`,
    which could match nothing and print only its own case count.

    The four are one gate rather than four because they are one defect, and
    the thing they have in common is the thing to keep: in every one of them
    the caller named a target, no gate ran on it, and the exit code said pass.
    """
    worse = 0
    for which, names, want in DISPATCH_CASES:
        got = _dispatch_rc(which, names)
        if got != want:
            worse += 1
            print(f"  DISPATCH_CASES: {which!r} against {names!r} "
                  f"wanted {want}, got {got}")
    print(f"DISPATCH_CASES                             "
          f"{len(DISPATCH_CASES) - worse} of {len(DISPATCH_CASES)}")

    bad = 0
    for named, present, want in TARGET_CASES:
        got = tuple(missing_targets(named, lambda x: x in set(present)))
        if got != want:
            bad += 1
            print(f"  TARGET_CASES: {named!r} against {present!r} "
                  f"wanted {want!r}, got {got!r}")
    print(f"TARGET_CASES                               "
          f"{len(TARGET_CASES) - bad} of {len(TARGET_CASES)}")

    routed_wrong = 0
    for name, takes, checked in ARG_ROUTING_CASES:
        got = (name in TAKES_PATHS, name in PATH_ARG_COMMANDS)
        if got != (takes, checked):
            routed_wrong += 1
            print(f"  ARG_ROUTING_CASES: {name!r} wanted "
                  f"{(takes, checked)!r}, got {got!r}")
    print(f"ARG_ROUTING_CASES                          "
          f"{len(ARG_ROUTING_CASES) - routed_wrong} of {len(ARG_ROUTING_CASES)}")

    picked_wrong = 0
    for known, named, want in SELECTION_CASES:
        got = len(selected_sets(known, named))
        if got != want:
            picked_wrong += 1
            print(f"  SELECTION_CASES: {named!r} against {known!r} "
                  f"wanted {want}, got {got}")
    print(f"SELECTION_CASES                            "
          f"{len(SELECTION_CASES) - picked_wrong} of {len(SELECTION_CASES)}")

    # The code half is unconditional, so every case asserts the same thing and
    # the cases differ in what is handed in. A regression that restores the
    # replacing version fails all three rather than one, which is deliberate:
    # the identity is the guard and not any single call.
    narrowed = 0
    floor = len([p for p in reading_domain(None)[0] if p.is_file()])
    for given, what in READING_DOMAIN_CASES:
        code, _ = reading_domain(given)
        got = len([p for p in code if p.is_file()])
        if got != floor or floor == 0:
            narrowed += 1
            print(f"  READING_DOMAIN_CASES: {what} -- given {given!r}, "
                  f"the code half was {got} of the {floor} it globs alone")
    # `shown_path` is the other half of the same `--live` defect: a hit on a
    # path outside the repository used to raise ValueError, so the only way
    # this gate could ever report a violation on a served edition was a
    # traceback. Asserted on a path that cannot exist here.
    outside = pathlib.Path("/tmp/nonesuch-live/2026-W42.md")
    if shown_path(outside) != str(outside):
        narrowed += 1
        print(f"  READING_DOMAIN_CASES: a path outside the repository must "
              f"print as itself, got {shown_path(outside)!r}")
    print(f"READING_DOMAIN_CASES                       "
          f"{len(READING_DOMAIN_CASES) + 1 - narrowed} "
          f"of {len(READING_DOMAIN_CASES) + 1}")

    worse += bad + routed_wrong + picked_wrong + narrowed
    if worse:
        print()
        print("A dispatcher that returns 0 for a name it does not have makes")
        print("every gate in this file unfalsifiable from the outside, since")
        print("a missing gate and a passing gate print the same nothing. The")
        print("same holds of a target that is not there and of a selection")
        print("that matches nothing, which is why all four tables are here.")
    return 1 if worse else 0


# ---- the fifth altitude, and the one both of this seat's sweeps missed ----
#
# The ExO seat's sentence of 2026-11-02 was that a sweep passing one argument
# tests the command NAME and not what comes after it. This seat agreed, swept
# `tools/` a second time with a nonsense target instead of a nonsense name,
# found every file refusing, and was one commit from reporting the fleet clean
# a second time.
#
# The second sweep's domain was positional arguments and `sys.argv[1]`, because
# those are the shapes this seat's own file uses. A target handed over by a
# FLAG is neither, and `tools/board.py inbox --seat <anything>` answers
# "0 messages" and exits 0 for a seat that does not exist. Twelve seats run
# that command every run, and this seat read a confident zero from it tonight
# against nine messages it actually held, because the name in the dispatch
# prompt is `alexandria-writer` and the name on the board is `writer`.
#
# So the defect was not in the probe. It was in the domain the probe was
# measured over, and the domain was a list of shapes that answered confidently
# about the world it was written in, which is ban list 36 and L-A26 by name.
# `sweep` above cites that same law in its own docstring. This block exists so
# the domain is read from the declarations instead of recalled from habit.
ARG_DECL = re.compile(r"add_argument\(\s*((?:\s*[\"'][^\"']*[\"']\s*,?)+)")
ARG_LIT = re.compile(r"[\"']([^\"']*)[\"']")


def declared_args(source):
    """Every argument a tool's parser declares, as (kind, name) pairs.

    `None` and never `()` for a file that declares no parser, for the reason
    `declared_columns` returns `None`: an empty tuple reads as "nothing to
    cover" and is indistinguishable from a clean pass, which is the entire
    class this block belongs to.

    Only the leading run of string literals in each call is read, so the
    keyword arguments after it cannot contribute a name. The long option wins
    when a call declares both, because `-q, --quiet` is one argument under the
    name argparse itself stores it as.
    """
    runs = ARG_DECL.findall(source or "")
    if not runs:
        return None
    out = []
    for run in runs:
        lits = ARG_LIT.findall(run)
        longs = [x for x in lits if x.startswith("--")]
        if longs:
            out.append(("flag",
                        max(longs, key=len).lstrip("-").replace("-", "_")))
        elif lits and lits[0].startswith("-"):
            # A short option with no long form is still an argument. Dropping
            # it here would undercount the surface silently, which is the
            # defect this whole block is about, so it is a flag under the
            # name argparse stores it as. No tool declares one today and the
            # case below is what makes that a measurement rather than luck:
            # the mutation test found this hole by surviving, not the cases.
            out.append(("flag", lits[0].lstrip("-").replace("-", "_")))
        elif lits:
            out.append(("positional", lits[0]))
    return tuple(out)


def uncovered_args(declared, probed):
    """The declared argument names a probe never passed a value for.

    `None` propagates: a surface that could not be read owes no answer about
    coverage, and saying `()` there would report full coverage of a file
    nobody parsed.
    """
    if declared is None:
        return None
    seen = set(probed or ())
    return tuple(name for _, name in declared if name not in seen)


ARG_CASES = (
    # A positional, which is all either sweep ever reached.
    ('ap.add_argument("paths", nargs="+")', (("positional", "paths"),)),
    # The live instance. A target carried by a flag.
    ('ap.add_argument("--seat", help="the seat acting")',
     (("flag", "seat"),)),
    # Short and long for one argument is one argument, under the long name.
    ('ap.add_argument("-q", "--quiet", action="store_true")',
     (("flag", "quiet"),)),
    # A dash in the option is an underscore in the name, the way argparse
    # stores it, so a probe can be checked against the parser's own spelling.
    ('ap.add_argument("--since-hours", type=int)',
     (("flag", "since_hours"),)),
    # A declaration wrapped over lines, which is most of them in this repo.
    ('ap.add_argument("--to",\n                default="reader@example.com",\n'
     '                help="the recipient the footer names")',
     (("flag", "to"),)),
    # A short option with no long form, which no tool declares today. The
    # mutation that made this a positional survived all eight other cases.
    ('ap.add_argument("-v", action="count")', (("flag", "v"),)),
    # A keyword holding a string must not become an argument name. This is the
    # case that would have invented four arguments for `rehearse_email`.
    ('ap.add_argument("--token", default=None, help="an opaque string")',
     (("flag", "token"),)),
    # A subparser name is not an argument. `tools/board.py` declares eight.
    ('sub.add_parser("show", help="print the board")', None),
    # No parser at all is refused rather than reported as a clean surface.
    ("print('hello')", None),
    # Order is preserved, because a caller reading the gap needs the parser's
    # order rather than a sorted set.
    ('ap.add_argument("--company")\nap.add_argument("--seat")\n'
     'ap.add_argument("key", nargs="?")',
     (("flag", "company"), ("flag", "seat"), ("positional", "key"))),
)

UNCOVERED_CASES = (
    # The live shape. A sweep that passed one positional covers no flag.
    ((("flag", "seat"), ("flag", "company"), ("positional", "paths")),
     ("paths",), ("seat", "company")),
    # A probe that covered everything returns nothing, which is the pass.
    ((("flag", "seat"),), ("seat",), ()),
    # Nothing probed is the whole surface uncovered, which is what the
    # command-name sweep of 2026-11-01 actually achieved.
    ((("flag", "seat"), ("flag", "company")), (), ("seat", "company")),
    # An unreadable surface says so rather than claiming full coverage.
    (None, ("seat",), None),
    # Nothing declared and nothing probed is not a gap.
    ((), (), ()),
)

def coverage_figure(covered, declared):
    """The share of its own declared domain a sweep actually reached.

    A string with one decimal, because this figure's only use is that 1.6 and
    1.7 are different answers to the same question. The ExO seat read 1.7 off
    this tree at 05:34Z and it is 1.6 ninety minutes later, on the same four
    positional arguments, because `main` merged five more declarations in
    between. A figure that moves that fast cannot be kept by quoting it, which
    is why it is computed here and printed on every full run.

    `None` and never `"100.0"` for an empty or incoherent domain. A sweep over
    nothing covered nothing, and printing full coverage there is the exact
    false-confidence shape this whole block exists to prevent: it is ban list
    36 again, one altitude up.
    """
    if covered is None or declared is None:
        return None
    if declared <= 0 or covered < 0 or covered > declared:
        return None
    return f"{100.0 * covered / declared:.1f}"


COVERAGE_CASES = (
    # Tonight's live figure: four positional arguments out of 246 declared.
    ((4, 246), "1.6"),
    # The ExO seat's figure at 05:34Z, the same numerator over a domain five
    # declarations smaller. Same sweep, same night, a different number.
    ((4, 241), "1.7"),
    # The command-name sweep of 2026-11-01, which reached no declared argument
    # at all and reported the fleet clean.
    ((0, 43), "0.0"),
    # Full coverage prints as full coverage.
    ((246, 246), "100.0"),
    # An empty domain is not full coverage. This is the case the figure exists
    # to refuse, and the one a bare division would have printed as a crash.
    ((0, 0), None),
    # More covered than declared is incoherent, so it is refused rather than
    # printed as 100 percent or as some number above it.
    ((4, 0), None),
    ((247, 246), None),
    # A negative numerator is refused rather than printed as a negative
    # percentage. Found by a surviving mutation rather than written for.
    ((-1, 246), None),
    # The two numbers the call site could transpose, kept here so a reader who
    # sees either of them printed knows the wiring is wrong and not the tree:
    # 98.4 is the gap reported as the coverage, and 9.3 is the coverage divided
    # by the file count instead of the declared count. Neither is reachable by
    # this table, which is the point of keeping them in it.
    ((242, 246), "98.4"),
    ((4, 43), "9.3"),
    # An unreadable surface propagates, the way `uncovered_args` propagates it.
    ((None, 246), None),
    ((4, None), None),
)


# ---- the seventh altitude: a numerator that is no member of its domain ----
#
# The engineer seat corrected this gate's denominator on 2026-11-02. 246 was
# right as a count of declarations and wrong as a coverage domain, because 102
# of the 242 flags are boolean switches with no value to get wrong and 7 carry
# a `choices` list that argparse refuses before any tool sees it. 109 of the
# 246 can never enter the numerator, so dividing by 246 reports a share of a
# domain the sweep was never measured over. That is ban list 36 and L-A26 for
# the third time in this block, one layer in from where the last two were.
#
# The sender's narrower figure is 56, and the correction carried this seat's
# numerator across into it: "your sweep covered four of fifty-six". It did
# not. The 56 are flags, `SWEPT` is three positional names, and the overlap is
# empty, so the sweep covered zero of the 56. The sender's own next note is
# the proof, because it reports probing "eight of the fifty-six" as new work,
# which would read as twelve if four had already been reached.
#
# So the lesson is not that the denominator was wrong. Both of us had a
# numerator and a denominator that were separately defensible and belonged to
# different populations, and every check this gate already runs passed on the
# pair: 4 is less than 56, and 7.1 percent of 56 reconstructs to 4. A
# coverage figure needs to prove its numerator is a SUBSET of its denominator
# and not merely smaller than it, which is what `outside_domain` is for.
#
# What is mechanised here is the partition, because a parser declaration says
# in the tree whether a value can be wrong. What is NOT mechanised is the
# sender's split of the remaining 133 into 77 that take a number or free text
# and 56 that name something a tool could resolve. That one is a judgment
# about what a string means, this seat reproduced the 133 exactly and cannot
# reproduce the split without making the same judgment, and encoding a
# judgment as a measurement is the defect one altitude above this one.
_SWITCH_ACTIONS = frozenset((
    "store_true", "store_false", "store_const", "append_const",
    "count", "help", "version",
))


def arg_classes(source):
    """The declared arguments split by whether a value can be wrong.

    Four tuples of names, in parser order: positional, resolvable, switch,
    constrained. `None` for a file that declares no parser, for the reason
    `declared_args` returns `None`.

    Read with `ast` and not the regex `declared_args` uses, because the two
    keywords that decide the split, `action` and `choices`, sit after the name
    literals and wrap over lines in most of this repo's declarations. A regex
    that reads only the leading run of literals is correct for the NAME and
    blind to exactly the two facts this function exists to read.

    `resolvable` is the domain a coverage figure may divide by: an argument
    that takes a value which argparse does not already constrain, so a tool
    receiving a value it cannot resolve is the tool's own answer to give.
    """
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return None
    positional, resolvable, switch, constrained = [], [], [], []
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute)
                and func.attr == "add_argument"):
            continue
        lits = [a.value for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if not lits:
            continue
        found = True
        keywords = {k.arg: k.value for k in node.keywords if k.arg}
        longs = [x for x in lits if x.startswith("--")]
        if longs:
            name = max(longs, key=len).lstrip("-").replace("-", "_")
        elif lits[0].startswith("-"):
            name = lits[0].lstrip("-").replace("-", "_")
        else:
            positional.append(lits[0])
            continue
        action = keywords.get("action")
        action = action.value if isinstance(action, ast.Constant) else None
        if action in _SWITCH_ACTIONS:
            switch.append(name)
        elif "choices" in keywords:
            constrained.append(name)
        else:
            resolvable.append(name)
    if not found:
        return None
    return (tuple(positional), tuple(resolvable), tuple(switch),
            tuple(constrained))


def outside_domain(numerator, domain):
    """The numerator's names that are not members of the domain it divides by.

    The check `coverage_figure` cannot do and this gate needed. A pair can
    satisfy every arithmetic check a share admits -- numerator no greater than
    denominator, percentage reconstructing the pair -- while the two numbers
    count different populations, and then the figure is not small or large, it
    is about nothing.

    `None` propagates from an unreadable domain rather than reporting that
    every name is inside it, which would be the pass-shaped answer.
    """
    if domain is None:
        return None
    inside = set(domain)
    return tuple(n for n in dict.fromkeys(numerator or ()) if n not in inside)


ARG_CLASS_CASES = (
    # The live instance, and the reason this function is not the regex. The
    # switch keyword wraps onto the next line, which is how most of this
    # repo's declarations are written.
    ('ap.add_argument("--broadcast",\n                action="store_true")',
     ((), (), ("broadcast",), ())),
    # A flag taking a value argparse does not constrain. This is the class the
    # coverage figure may divide by.
    ('ap.add_argument("--seat", help="the seat acting")',
     ((), ("seat",), (), ())),
    # A choices list is refused by argparse before a tool sees it, so it is
    # out of the domain even though it takes a value.
    ('ap.add_argument("--kind", choices=("note", "ask"))',
     ((), (), (), ("kind",))),
    # A number is still resolvable BY THIS PARTITION, and the comment above
    # says why the narrower judgment is not made here: `--limit 999` takes a
    # value a tool could in principle refuse, and whether it should is not a
    # fact the tree carries.
    ('ap.add_argument("--limit", type=int, default=50)',
     ((), ("limit",), (), ())),
    # A positional is its own class, because both of this seat's sweeps
    # reached these and nothing else.
    ('ap.add_argument("paths", nargs="+")', (("paths",), (), (), ())),
    # Parser order is preserved within each class, the way `declared_args`
    # preserves it, because a caller reading the gap needs the parser's order.
    ('ap.add_argument("--company")\nap.add_argument("--quiet",'
     ' action="store_true")\nap.add_argument("--seat")\n'
     'ap.add_argument("key", nargs="?")',
     (("key",), ("company", "seat"), ("quiet",), ())),
    # A subparser name is not an argument, matching `declared_args`.
    ('sub.add_parser("show", help="print the board")', None),
    # No parser at all is refused rather than reported as a clean surface.
    ("print('hello')", None),
    # A file this gate cannot parse is refused too. `declared_args` would
    # happily regex a name out of a broken file and report a surface.
    ('ap.add_argument("--seat"', None),
    # `action="append"` is not a switch: it takes a value, so a value can be
    # wrong. The mutation that folded it in with the switches survives every
    # case above.
    ('ap.add_argument("--ref", action="append")', ((), ("ref",), (), ())),
)

OUTSIDE_CASES = (
    # Tonight's defect, which is the case this function was written for. The
    # three swept names against the flag domain the correction named: every
    # one of them is outside it, so the pair "4 of 56" has an empty overlap.
    (("paths", "ids", "key"), ("seat", "company", "skill"),
     ("paths", "ids", "key")),
    # The same numerator against the domain it does belong to is clean, which
    # is what makes the case above a measurement rather than an assertion.
    (("paths", "ids", "key"), ("paths", "ids", "key"), ()),
    # A subset is clean.
    (("paths",), ("paths", "ids"), ()),
    # Partial overlap reports only the strangers, in the numerator's order.
    (("key", "seat", "paths"), ("paths", "key"), ("seat",)),
    # An unreadable domain propagates rather than answering "all inside",
    # which is the pass-shaped answer this file refuses everywhere else.
    (("paths",), None, None),
    # An empty numerator is inside every domain, including an empty one. This
    # is the honest reading of a sweep that passed nothing: no stranger, and
    # the coverage figure beside it is what says it reached nothing.
    ((), (), ()),
    # A repeated name is one stranger and not two, because the domain question
    # is about membership and the count belongs to the figure.
    (("paths", "paths"), ("ids",), ("paths",)),
)


# What this seat's two sweeps actually passed a value for, as a record rather
# than as a memory. The first sweep passed a nonsense first argument to all
# 46 files under `tools/`, which reaches the subcommand name and no declared
# argument at all. The second passed a path to the four positional arguments
# in the tree.
SWEPT = ("paths", "ids", "key")

# Files under `tools/` whose argument surface cannot be read from parser
# declarations, with the reason each one is not a hole in the measurement.
# Three of the four are the same three the command-name sweep of 2026-11-01
# explained, which is why they are quoted from that sweep rather than
# re-derived here.
ARG_FILED = {
    "board_alarm.py": "a library. Its own docstring opens `Not a command`",
    "panel.py": "a library, imported by the four `panel_*` tools",
    "check_registers.py": "parses no arguments at all, by design",
    "check_issue_citations.py":
        "reads `sys.argv[1]` with no parser, and refuses an absent path with "
        "a traceback and exit 1, which is loud rather than a false pass",
}


def flags():
    """The argument surface of `tools/`, read from the declarations.

    This gate grades a measurement and not an edition, so it reads the tree
    and nothing else. It is in `all` because the thing it protects is the one
    defect class no output can reveal, and because this seat has now narrowed
    the same domain twice in two nights.

    What it fails on is closable and small: a file whose surface cannot be
    read and which no row explains, and a row explaining a file that does not
    exist or does declare a parser. That is `sweep`'s three-way shape, chosen
    deliberately, because the register decides the domain and this map only
    answers for it.

    What it prints and does not fail on is the coverage gap, and the reason is
    not softness. Deciding which of the declared flags names a target a tool
    resolves is per-tool judgment across 42 files in the engineer seat's lane,
    and a gate in this seat's file that failed on it would be this seat holding
    another seat's surface red forever. The number is the finding and it is in
    `docs/ideas.md` with an owner. That is the same division `sweep` draws in
    its own last paragraph between a check and a reading.
    """
    tools = ROOT / "tools"
    files = sorted(tools.glob("*.py"))
    if not files:
        print("  FAIL    tools/ holds no python files, so the sweep this gate")
        print("          measures had no domain and its clean result was")
        print("          about nothing")
        return 1

    bad = 0
    for i, (text, want) in enumerate(ARG_CASES):
        got = declared_args(text)
        if got != want:
            bad = 1
            print(f"  CASE    declared_args case {i} wanted {want!r} and "
                  f"got {got!r}")
    print(f"ARG_CASES                                  "
          f"{len(ARG_CASES) - bad} of {len(ARG_CASES)}")
    worse = 0
    for declared, probed, want in UNCOVERED_CASES:
        got = uncovered_args(declared, probed)
        if got != want:
            worse = 1
            print(f"  CASE    uncovered_args({probed!r}) wanted {want!r} "
                  f"and got {got!r}")
    print(f"UNCOVERED_CASES                            "
          f"{len(UNCOVERED_CASES) - worse} of {len(UNCOVERED_CASES)}")
    rough = 0
    for (covered, total), want in COVERAGE_CASES:
        # The raise is caught and reported rather than allowed out, because
        # four of this table's nine cases are guards against a domain that
        # divides by zero or types wrongly. A mutation that drops one of those
        # guards takes the whole gate down on the first case and prints
        # nothing about the other eight, so the loudest failure is also the
        # least informative one. Two mutations of this block did exactly that
        # before this `except` was here, and the harness scoring them read the
        # traceback as a survival.
        try:
            got = coverage_figure(covered, total)
        except Exception as exc:
            got = f"{type(exc).__name__}: {exc}"
        if got != want:
            rough = 1
            print(f"  CASE    coverage_figure({covered!r}, {total!r}) wanted "
                  f"{want!r} and got {got!r}")
    print(f"COVERAGE_CASES                             "
          f"{len(COVERAGE_CASES) - rough} of {len(COVERAGE_CASES)}")
    crude = 0
    for i, (text, want) in enumerate(ARG_CLASS_CASES):
        try:
            got = arg_classes(text)
        except Exception as exc:
            got = f"{type(exc).__name__}: {exc}"
        if got != want:
            crude = 1
            print(f"  CASE    arg_classes case {i} wanted {want!r} and "
                  f"got {got!r}")
    print(f"ARG_CLASS_CASES                            "
          f"{len(ARG_CLASS_CASES) - crude} of {len(ARG_CLASS_CASES)}")
    stray = 0
    for numerator, domain, want in OUTSIDE_CASES:
        try:
            got = outside_domain(numerator, domain)
        except Exception as exc:
            got = f"{type(exc).__name__}: {exc}"
        if got != want:
            stray = 1
            print(f"  CASE    outside_domain({numerator!r}, {domain!r}) "
                  f"wanted {want!r} and got {got!r}")
    print(f"OUTSIDE_CASES                              "
          f"{len(OUTSIDE_CASES) - stray} of {len(OUTSIDE_CASES)}")
    print()

    unreadable, positional, flagged, gap = [], 0, 0, 0
    for path in files:
        declared = declared_args(path.read_text(encoding="utf-8"))
        if declared is None:
            unreadable.append(path.name)
            continue
        positional += sum(1 for k, _ in declared if k == "positional")
        flagged += sum(1 for k, _ in declared if k == "flag")
        gap += len(uncovered_args(declared, SWEPT))

    print(f"files under tools/                         {len(files)}")
    print(f"  surface readable from declarations       "
          f"{len(files) - len(unreadable)}")
    print(f"  no parser, filed with the reason         {len(unreadable)}")
    for name in unreadable:
        print(f"    {name}  {ARG_FILED.get(name, '')}")
    print(f"declared arguments                         "
          f"{positional + flagged}")
    print(f"  positional, which both sweeps reached    {positional}")
    print(f"  carried by a flag, which neither did     {flagged}")
    print(f"never passed a value by either sweep       {gap}")

    # The partition, which is the correction of 2026-11-02. The count of
    # declarations is not the coverage domain: a switch has no value to get
    # wrong and a `choices` list is refused by argparse before a tool is
    # reached, so neither can ever enter the numerator. Dividing by the whole
    # count reports a share of a population the sweep was never measured over.
    positional_names, resolvable_names, switches, constrained = [], [], 0, 0
    for path in files:
        classes = arg_classes(path.read_text(encoding="utf-8"))
        if classes is None:
            continue
        here_pos, here_resolvable, here_switch, here_constrained = classes
        positional_names.extend(here_pos)
        resolvable_names.extend(here_resolvable)
        switches += len(here_switch)
        constrained += len(here_constrained)
    # The two classes are kept apart and concatenated only for the blended
    # figure, because the split is the reading and the blend hides it.
    in_domain = positional_names + resolvable_names
    resolvable = len(resolvable_names)
    print(f"  of which a value can be wrong            "
          f"{len(in_domain)}")
    print(f"    boolean switches, nothing to resolve   {switches}")
    print(f"    a choices list, argparse refuses it    {constrained}")

    domain = len(in_domain)
    covered = domain - len(uncovered_args(
        tuple(("x", n) for n in in_domain), SWEPT))
    # The check the arithmetic ones below cannot do, and the one this gate
    # needed. `coverage_figure` sees two integers and every check under it
    # compares them as integers, so a numerator counting one population and a
    # denominator counting another satisfies all of them: 4 is less than 56,
    # and 7.1 percent of 56 reconstructs to 4. The pair is still about
    # nothing. So the names are checked for membership and not only the
    # counts for size.
    # The dual check, and the one that holds the correction in place. The
    # guard below catches a numerator with members outside its domain; this
    # catches a domain with members that can never be in the numerator, which
    # is what 246 was. Without it, restoring `domain = positional + flagged`
    # passes every other check in this gate: the reconstruction uses whatever
    # domain it is handed, the halves still sum, and the figure prints 1.6
    # with the same confidence it prints 2.9.
    #
    # It is an identity on counts and not a membership test on names, because
    # a membership test is wrong here and the wrongness is in the live tree.
    # `status` and `surface` are each declared with a `choices` list in one
    # tool and as free text in another, so "no switch name appears in the
    # domain" fails a correct tree. A name is not a class; a declaration is.
    if domain != positional + flagged - switches - constrained:
        worse = 1
        print(f"  FAIL    the domain is {domain} and the declarations minus "
              f"the switches and the choices lists give "
              f"{positional + flagged - switches - constrained}, so the "
              f"denominator below holds arguments no sweep could ever cover")
    strangers = outside_domain(SWEPT, in_domain)
    if strangers:
        worse = 1
        print(f"  FAIL    SWEPT names {', '.join(strangers)}, which the "
              f"domain printed above does not contain, so the coverage pair "
              f"below counts two different populations and the percentage is "
              f"not a share of anything")
    # `covered` is 4 today and so is `positional`, and a mutation replacing
    # one with the other survives every check below. They are equal only
    # because `SWEPT` happens to name three positionals and no flag, so the
    # equality is a fact about this sweep and not about the quantities. Do not
    # simplify it: the first flag anybody sweeps makes them different, and the
    # reading this gate exists for is exactly the distance between them.
    # The numerator, derived a second time by counting membership instead of
    # subtracting non-membership, because the cases table above cannot reach
    # this call and two mutations of it survived: one passed `gap` as the
    # numerator and printed 98.4 percent coverage of a domain it had covered
    # 1.6 percent of. A figure that confident is the whole defect class this
    # gate was built for, so it gets a check and not a comment.
    # Counted over the SAME population as `covered` since the correction of
    # 2026-11-02, and by the opposite method. Before the correction this
    # counted SWEPT across all 246 declarations while `covered` was a share
    # of the whole 246, so the populations agreed by accident. Narrowing the
    # domain and leaving this loop alone would have made the two disagree
    # whenever a swept name was a switch, and the gate would have failed a
    # correct tree. Membership counted up here, non-membership subtracted
    # there: two methods, one population.
    swept = sum(1 for n in in_domain if n in SWEPT)
    if swept != covered:
        worse = 1
        print(f"  FAIL    the coverage numerator is wired wrong: counting the "
              f"names in SWEPT gives {swept} and the gap subtraction gives "
              f"{covered}, so the percentage below is not the measurement "
              f"this gate names")
    pct = coverage_figure(covered, domain)
    # The figure must reconstruct the pair printed beside it. The numerator
    # check above guards `covered`; it does not guard what this call passes,
    # and two mutations walked straight through it by leaving `covered` right
    # and handing `coverage_figure` something else. One printed 98.4 percent
    # and one printed 9.3, both beside the text `4 of 246`. So the round trip
    # is the check: a percentage that does not come back to its own numerator
    # is reporting a different measurement than the one it is labelled with.
    # The tolerance is half of the last digit the figure prints, scaled by the
    # domain, and not a round number. The first draft of this check used 0.05
    # and failed the live tree: 1.6 percent of 246 is 3.94 against a true 4,
    # which is 0.064 out, because one decimal of a percentage only locates the
    # numerator to within `domain / 2000`. A threshold picked for looking
    # reasonable rather than derived from the precision of the thing it
    # measures is this gate's own defect class, caught inside the gate built
    # for it, which is the fifth instance tonight.
    slack = domain / 2000.0 + 1e-9
    if pct is not None and abs(float(pct) * domain / 100.0 - covered) > slack:
        worse = 1
        print(f"  FAIL    the coverage figure does not reconstruct its own "
              f"pair: {pct}% of {domain} is "
              f"{float(pct) * domain / 100.0:.1f}, the pair printed is "
              f"{covered}, and the rounding only allows {slack:.2f} of that, "
              f"so one of the two numbers is not from this sweep")
    if pct is None:
        print("the sweep's coverage of its own domain     NONE, and that is")
        print("          not full coverage: tools/ declares no readable")
        print("          argument, so the sweep's clean result is about")
        print("          nothing")
    else:
        print(f"the sweep's coverage of its own domain     {pct}%  "
              f"{covered} of {domain}")

    # The two halves apart, because the blend hides the finding. Every
    # argument either sweep reached is positional, so one half is finished and
    # the other has not been started, and a single number between them reads
    # as slow progress on one job rather than as the two jobs it is. The
    # engineer seat's narrower count of 56 is a subset of the flag
    # denominator here, and its overlap with SWEPT is empty too, so this zero
    # is what "four of fifty-six" was reporting either way.
    pos_swept = sum(1 for n in positional_names if n in SWEPT)
    flag_swept = sum(1 for n in resolvable_names if n in SWEPT)
    print(f"  positional                               "
          f"{coverage_figure(pos_swept, positional)}%  "
          f"{pos_swept} of {positional}")
    print(f"  carried by a flag                        "
          f"{coverage_figure(flag_swept, resolvable)}%  "
          f"{flag_swept} of {resolvable}")
    if pos_swept + flag_swept != covered:
        worse = 1
        print(f"  FAIL    the two halves sum to "
              f"{pos_swept + flag_swept} and the blended numerator is "
              f"{covered}, so the split above is not a partition of the "
              f"figure printed over it")
    print()

    unfiled = [n for n in unreadable if n not in ARG_FILED]
    phantom = sorted(n for n in ARG_FILED
                     if not (tools / n).exists()
                     or declared_args((tools / n).read_text(encoding="utf-8"))
                     is not None)
    if unfiled:
        worse = 1
        for name in unfiled:
            print(f"  FAIL    tools/{name} declares no parser and no row says "
                  f"why, so this gate's domain has a hole in it and the "
                  f"sweep's clean result does not cover that file")
    if phantom:
        worse = 1
        for name in phantom:
            print(f"  FAIL    ARG_FILED names tools/{name}, which either is "
                  f"not there or does declare a parser, so the row explains "
                  f"a hole that is not one")
    if not unfiled and not phantom:
        print("  OK      every file's argument surface is either read here or")
        print("          filed with its reason")
    print()
    print("The gap above is the reading. A sweep that mistypes the command")
    print("name tests the dispatcher, a sweep that mistypes a positional")
    print("tests four arguments, and the target that actually answered a")
    print("confident zero to this seat tonight was carried by `--seat`.")
    print("Which of the flags name a target is the engineer seat's judgment,")
    print("file by file, and it is in docs/ideas.md under that seat's name.")
    print()
    print("The percentage is printed rather than quoted because it moves. The")
    print("ExO seat read 1.7 off this tree at 05:34Z and asked this seat to")
    print("keep that number; it was 1.6 ninety minutes later, on the same four")
    print("positional arguments, because `main` had merged five more")
    print("declarations. Keeping the figure and quoting the figure turned out")
    print("to be opposite instructions.")
    print()
    print("Then the denominator itself was wrong, which no amount of")
    print("printing would have caught. 246 counts declarations and the")
    print("domain counts arguments a value can be wrong in, and 109 of the")
    print("246 are neither: a switch has nothing to resolve and a choices")
    print("list is refused by argparse before a tool is reached. So the")
    print("figure was a share of a population the sweep was never measured")
    print("over, and the correction came from the seat that reads the tools")
    print("rather than from any check in here.")
    # `crude` and `stray` are in this sum because they were not, for the
    # length of one run. The two tables added on 2026-11-02 printed their
    # CASE lines and the gate returned `bad | worse | rough`, so a failing
    # new case was visible to a reader and invisible to a caller, which is
    # this file's own opening defect: a gate that prints a failure and exits
    # 0 is unfalsifiable from the outside. Every table above owes the return.
    return bad | worse | rough | crude | stray


# ---- the sixth altitude: the number an ask names was already spent ----
#
# This seat filed an ask on 2026-11-02 asking the engineer seat to refuse an
# unknown seat name from `tools/board.py inbox` "with exit 2 rather than
# reporting zero. Exit 2 and not 1, so a caller separates `this seat is not
# here` from `this seat has no mail`."
#
# The reasoning was right and the number was wrong. `tools/board.py` on `main`
# already spends 2, at `main()`'s `except BoardError: return 2`, for the board
# refused or could not be asked, and already spends 3 as `EXIT_AMBIGUOUS`. So
# the ask named one of the two low codes that file had allocated, and spending
# it would have merged a transport failure with an unknown addressee. The
# engineer seat answered with the behaviour already built under 4 and with the
# sentence this block is named for: "If your dispatcher is free to use two,
# use two. I cannot."
#
# Both numbers were one grep from the ask. What this seat did instead was
# carry the convention from THIS file, where `_dispatch_rc` returns 2 for an
# unknown gate, into a sentence about a file in another seat's lane. That is
# the two sweeps above one more time: a domain read off this seat's own
# surface and published as a claim about somebody else's.
#
# It reads the tree with `ast` rather than with a regex, and that choice is
# the engineer seat's lesson rather than this seat's caution. Their note
# reported two bugs in their own roster shortcut, a regex matching the company
# key where the board's company name is the product key, and one reading only
# the block form where the manifest writes inline mappings. Both "returned an
# empty set for every real call, which is a roster that is never consulted and
# reads exactly like a roster that agrees", and a gate comparing the shortcut
# to the real parser caught both before they shipped.
#
# The first draft of this gate had that defect with the regex removed, which
# is worth the three lines because it is the whole reason the model below has
# three answers instead of two. It called a file `computed` as soon as ANY
# exit path returned a value rather than a literal, so all 40 tools with an
# entrypoint came back unenumerable, every proposal came back CANNOT, and it
# printed `OK every proposed code is free` over the one real collision in the
# ledger. Certainty is per path and never per file: `board.py` computes
# `args.func(args)` AND writes 2 down, and the written 2 is what the ask
# collided with.
EXIT_CALLS = ("exit", "_exit", "SystemExit")
EXIT_RETURNERS = ("main",)
EXIT_RETURNER_PREFIXES = ("cmd_",)


def _int_const(node):
    """The int a node is, or None. `True` is not an exit code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int) \
            and not isinstance(node.value, bool):
        return node.value
    return None


def _exit_names(tree):
    """Module-level names beginning `EXIT` that are bound to a literal int.

    Resolving these is what keeps `return EXIT_AMBIGUOUS if x else 0` out of
    the unenumerable pile. The name is the declaration, so a return through it
    is as written-down as a bare 2, and it carries the meaning besides.
    """
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("EXIT"):
                if (code := _int_const(node.value)) is not None:
                    out[target.id] = code
    return out


def _returned_codes(node, names):
    """(the int literals this return can be, whether any path is computed).

    `return 0 if ok else 1` allocates both numbers and computes nothing, so
    the test is never walked: the name in it decides WHICH code, never which
    codes exist. `return answer["exit"]` allocates nothing nameable, and the
    second half of the pair is how a caller learns the enumeration is partial
    instead of reading an empty set as a file that spends nothing.
    """
    if node is None:
        return ((), False)
    if isinstance(node, ast.Constant) and node.value is None:
        return ((), False)
    if (code := _int_const(node)) is not None:
        return ((code,), False)
    if isinstance(node, ast.Name) and node.id in names:
        return ((names[node.id],), False)
    if isinstance(node, ast.IfExp):
        yes, cy = _returned_codes(node.body, names)
        no, cn = _returned_codes(node.orelse, names)
        return (yes + no, cy or cn)
    if isinstance(node, ast.BoolOp):
        codes, partial = (), False
        for value in node.values:
            more, worse = _returned_codes(value, names)
            codes, partial = codes + more, partial or worse
        return (codes, partial)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in EXIT_RETURNERS:
        # `raise SystemExit(main())` is the whole tree's entrypoint idiom and
        # it computes nothing of its own. `main`'s own returns are walked
        # separately, so counting the delegation as a computed path would
        # report every tool here partial and make the certainty column say
        # nothing. Any other call does compute, including `smoke()`.
        return ((), False)
    return ((), True)


def _exit_nodes(tree):
    """Every exit path in a module, as (literal codes, computed) pairs.

    An `exit`/`SystemExit` call and a `return` inside `main` or a `cmd_*`
    function. A `return 2` from an ordinary helper is not one, because this
    tree returns small ints from ordinary functions and counting those would
    invent collisions across the whole map.
    """
    names = _exit_names(tree)
    paths = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            leaf = fn.attr if isinstance(fn, ast.Attribute) else (
                fn.id if isinstance(fn, ast.Name) else None)
            if leaf in EXIT_CALLS:
                paths.append(_returned_codes(
                    node.args[0] if node.args else None, names))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name not in EXIT_RETURNERS and not node.name.startswith(
                    EXIT_RETURNER_PREFIXES):
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Return):
                    paths.append(_returned_codes(inner.value, names))
    return paths


def spent_exits(source):
    """Every exit code a tool writes down, as (code, name) pairs.

    `None` and never `()` for source with no exit surface at all, which is a
    library or a file that does not parse, for the reason `declared_args` and
    `declared_columns` return `None`: an empty tuple reads as "this file has
    spent nothing", a collision check over it answers that every number is
    free, and that answer is indistinguishable from a surface that was read.

    `()` is a real and different answer: a file that exits but writes no
    number down. `exit_certainty` is what separates a free number in a file
    that wrote all of its codes down from a free number in a file that did
    not, and a caller that ignores it is reading a provisional answer as a
    checked one.

    What counts, and the list is short so the parser can be certain of each:

    - a module-level name beginning `EXIT` bound to an int, which is how
      `board.py`, `merge_order.py`, `read_paper.py`, `check_authority.py` and
      `resolve_register_conflict.py` all declare theirs, and a return through
      such a name.
    - The int values of a module-level `EXIT`-named dict, under their key's
      name when the key is a bare name or a string.
    - An int literal passed to `sys.exit`, `os._exit` or `SystemExit`.
    - An int literal returned from `main` or a `cmd_*` function, which is the
      shape carrying `board.py`'s 2 and which no module-level scan can see.
    """
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return None
    paths = _exit_nodes(tree)
    constants = _exit_names(tree)
    dicts = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value,
                                                              ast.Dict):
            continue
        if not any(isinstance(t, ast.Name) and t.id.startswith("EXIT")
                   for t in node.targets):
            continue
        for key, val in zip(node.value.keys, node.value.values):
            label = ""
            if isinstance(key, ast.Name):
                label = key.id
            elif isinstance(key, ast.Constant) and isinstance(key.value, str):
                label = key.value
            if (code := _int_const(val)) is not None:
                dicts.setdefault(code, label)
    if not paths and not constants and not dicts:
        return None

    found = {}

    def keep(code, name):
        if code not in found or (name and not found[code]):
            found[code] = name or found.get(code, "")

    for name, code in constants.items():
        keep(code, name)
    for code, label in dicts.items():
        keep(code, label)
    for codes, _ in paths:
        for code in codes:
            keep(code, "")
    return tuple(sorted(found.items()))


def exit_certainty(source):
    """`"complete"` when every exit path writes its number down, else
    `"partial"`, and `None` when there is no exit surface to be certain about.

    Three answers because the first draft of this gate had two and the missing
    one is where the live collision went. A file is not unenumerable because
    one of its paths computes a value: `board.py` computes `args.func(args)`
    and writes 2 down in the same function, and the 2 is the allocation a
    proposal collides with.
    """
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return None
    paths = _exit_nodes(tree)
    if not paths and not _exit_names(tree):
        return None
    return "partial" if any(partial for _, partial in paths) else "complete"


def exit_collision(spent, proposed):
    """What a proposed code collides with in a file, or None if it is free.

    `None` propagates and means cannot-say, not free. A caller reading the
    `None` from a surfaceless file as a clear number is making exactly the
    mistake this block is filed under, so a caller asks `spent is None` first
    and never reads this return value alone.
    """
    if spent is None:
        return None
    for code, name in spent:
        if code == proposed:
            return (code, name)
    return None


CERTAINTY_CASES = (
    # A library. Nothing exits, nothing returns a status, so there is nothing
    # to be certain about.
    ("def render(rows):\n    return '\\n'.join(rows)\n", None),
    # The live shape, and the one the first draft of this gate got wrong: a
    # file that computes one status and writes another down is partial, not
    # unenumerable.
    ("EXIT_AMBIGUOUS = 3\ndef main():\n    try:\n        return "
     "args.func(args)\n    except E:\n        return 2\n", "partial"),
    # Every path a literal.
    ("def main():\n    return 0 if ok else 1\n", "complete"),
    # A return through a declared EXIT name is written down, not computed.
    ("EXIT_NOTHING = 4\ndef main():\n    return EXIT_NOTHING\n", "complete"),
    # `return answer["exit"]` alone is partial and enumerates nothing.
    ('def main():\n    return answer["exit"]\n', "partial"),
    # `sys.exit(__doc__)` is `check_issue_citations.py`'s real shape: an exit
    # surface whose value is not a number this gate can name.
    ("import sys\nsys.exit(__doc__)\n", "partial"),
    # A file that does not parse has no readable surface at all.
    ("def main(:\n", None),
    # `return` with no value is exit 0 and names no code, so it must not read
    # as computed and make a complete file partial.
    ("def main():\n    if x:\n        return\n    return 7\n", "complete"),
    # The entrypoint idiom of every tool in this tree. The delegation is not
    # a computation, because `main`'s own paths are walked on their own, and
    # reading it as one reported all 40 tools partial in this gate's second
    # draft.
    ("def main():\n    return 7\n\nraise SystemExit(main())\n", "complete"),
    # Any other call does compute. `skill_gate.py` and `ban_list.py` both
    # `return smoke()`.
    ("def main():\n    return smoke()\n", "partial"),
)

EXIT_CASES = (
    # The live instance, and the reason the ask was wrong: a module-level
    # constant beginning EXIT, plus the literal inside main.
    ("EXIT_AMBIGUOUS = 3\ndef main():\n    try:\n        return "
     "args.func(args)\n    except E:\n        return 2\n",
     ((2, ""), (3, "EXIT_AMBIGUOUS"))),
    # The literal no module-level scan reaches, on its own.
    ("def main(argv=None):\n    try:\n        return 0\n"
     "    except BoardError:\n        return 2\n",
     ((0, ""), (2, ""))),
    # The dict form, which five tools here use. Bare-name keys carry the
    # meaning, so they become the code's name.
    ("EXIT = {CLEAN: 0, BLOCKED: 1, UNMEASURED: 2}\n",
     ((0, "CLEAN"), (1, "BLOCKED"), (2, "UNMEASURED"))),
    # String keys and a None value, which is `board.py`'s EXIT_FOR_STATUS. The
    # None is skipped rather than counted, because a job that never ran has no
    # exit.
    ('EXIT_FOR_STATUS = {"success": 0, "failure": 1, "skipped": None}\n',
     ((0, "success"), (1, "failure"))),
    # A literal handed to sys.exit.
    ("import sys\nsys.exit(1)\n", ((1, ""),)),
    # A literal raised as SystemExit, which is the engineer seat's new 4.
    ("raise SystemExit(4)\n", ((4, ""),)),
    # Both arms of a conditional return are allocated.
    ("def main():\n    return 0 if ok else 1\n", ((0, ""), (1, ""))),
    # A `cmd_*` function is an exit returner, because that is how `board.py`
    # dispatches and where its subcommand codes live.
    ("def cmd_inbox(args):\n    return 3\n", ((3, ""),)),
    # The same code reached twice is one allocation, and a named reach beats
    # an anonymous one so the report can print what the number means.
    ("EXIT_NOTHING = 4\nraise SystemExit(4)\n", ((4, "EXIT_NOTHING"),)),
    # A small int returned from an ordinary helper is not an exit code. This
    # is the case that stops the gate inventing collisions, and the tree would
    # be full of them without it.
    ("def width(row):\n    return 2\n", None),
    # A file that exits and writes no number down is `()` and not `None`. The
    # two are different answers and the caller needs both.
    ('def main():\n    return answer["exit"]\n', ()),
    # A library is `None`, because there is nothing to collide with at all.
    ("def render(rows):\n    return 2, 3\n", None),
    # `True` is not an exit code, though `isinstance(True, int)` is true.
    ("EXIT_OK = True\nsys.exit(0)\n", ((0, ""),)),
    # A return through a declared name carries that name's meaning into the
    # map, which is what lets the report say what a collision means.
    ("EXIT_NOTHING = 4\ndef main():\n    return EXIT_NOTHING\n",
     ((4, "EXIT_NOTHING"),)),
)

COLLISION_CASES = (
    # The live instance. The ask named 2 and `board.py` had already spent it.
    (((0, ""), (2, ""), (3, "EXIT_AMBIGUOUS")), 2, (2, "")),
    # The number the engineer seat actually used, against the same file.
    (((0, ""), (2, ""), (3, "EXIT_AMBIGUOUS")), 4, None),
    # A collision against a named code reports the name, which is what makes
    # the report say what the number already means.
    (((3, "EXIT_AMBIGUOUS"),), 3, (3, "EXIT_AMBIGUOUS")),
    # A file that exits and wrote nothing down has no collision, and the
    # caller learns the answer is provisional from `exit_certainty` rather
    # than from here.
    ((), 2, None),
    # No surface at all cannot say a number is free. This is the case the
    # block exists for: the answer must not equal the answer above it, and the
    # caller tells them apart by asking about the surface first.
    (None, 2, None),
)


# What a ledger bullet means when it names a number. The ledger's own schema
# draws this line, so the gate reads the schema instead of guessing from
# tense: a code in `What:` or `First step:` is a number the entry asks
# somebody to spend, and a code in `Trigger:` or `Measured:` is a number
# somebody observed. Over 819 dated entries that distinction is the whole
# gate. The unscoped scan returned two non-zero hits, this seat's own wrong
# ask and the 2026-10-24 authority entry's `undecided, exit 3`, and the second
# is an observation of what `check_authority.py` printed. One true positive
# and one false positive out of two is not an instrument.
PROPOSING_BULLETS = ("what:", "first step:")
LEDGER_TOOL = re.compile(r"tools/([a-z_0-9]+)\.py")
LEDGER_CODE = re.compile(r"\bexit (?:code )?(\d+)\b", re.I)
LEDGER_BULLET = re.compile(r"- ([A-Z][^:]{0,60}):\s?(.*)$")


def ledger_bullets(entry):
    """Each `- Label: ...` bullet of one ledger entry, wrapped lines joined.

    The continuation lines matter: this seat's own wrong ask put the number in
    `What:` and wrapped before reaching it, so a scan reading first lines only
    would have missed the single instance in the file.
    """
    out, cur = [], None
    for line in (entry or "").splitlines():
        if m := LEDGER_BULLET.match(line):
            cur = [m.group(1).lower() + ":", m.group(2)]
            out.append(cur)
        elif line.startswith("- ") or line.startswith("### "):
            # A bullet carrying no `Label:` closes the one before it. Without
            # this the continuation lines of an off-schema bullet, which do
            # start with two spaces, are appended to the last LABELLED bullet
            # and read as part of it. This seat found it by writing an
            # `Answered` bullet into the very entry the gate was failing on:
            # the correction's own sentence quoting the wrong number landed
            # inside `What:` and the gate stayed red for a sentence that was
            # repairing it. Same class as everything else in this block, one
            # level down: a parser whose domain is the bullets it expected.
            cur = None
        elif cur is not None and line.startswith("  ") and line.strip():
            cur[1] += " " + line.strip()
    return tuple((label, text) for label, text in out)


def proposed_exits(entry):
    """(tool, code) pairs one ledger entry asks somebody to spend.

    Zero is dropped, and the reason is a rule rather than a convenience:
    every tool that runs spends 0 for success, so an entry naming 0 is not
    asking for a free number, and a gate reporting it would be right about the
    allocation and wrong about the ask.
    """
    tools = tuple(sorted(set(LEDGER_TOOL.findall(entry or ""))))
    if not tools:
        return ()
    out = []
    for label, text in ledger_bullets(entry):
        if label not in PROPOSING_BULLETS:
            continue
        for raw in LEDGER_CODE.findall(text):
            if (code := int(raw)) == 0:
                continue
            for tool in tools:
                if (tool, code) not in out:
                    out.append((tool, code))
    return tuple(out)


def proposing_quote(entry, code):
    """The proposing bullet's own words naming one code, wrapped lines joined.

    This gate cannot decide what a sentence means and must not try. What it can
    do is show the words it matched, and that is the whole of this repair.

    On 2026-11-02 this gate told the engineer seat that a pdf-route entry asked
    `tools/read_paper.py` for exit 3, which the file already spends as
    `ABSTRACT_ONLY`. The entry's sentence was "a sandbox with no `pypdf` must
    still exit 3 rather than crash", which asserts that the EXISTING code keeps
    coming out when the soft route is unavailable. It asks for no allocation at
    all. The finding printed the number and the allocation and never the words,
    so the one fact that settles it was the one fact it withheld, and the seat
    on the receiving end had to go and read the file to refute its own name on
    a defect it did not have.

    A reader who sees "must still exit 3 rather than crash" needs no rule to
    know that is not an ask. So the repair is a quote rather than a pattern:
    the engineer's note makes the point that refusing to mechanise what a
    string means is the altitude here, and a narrower regex would be this gate
    guessing at intent with a longer expression. The cost of the false positive
    was a seat's reading time; the cost of a pattern that drops real asks is a
    collision nobody sees.

    This was that gate's first cross-seat catch, and a reader whose first
    cross-seat finding is false learns to skim the rest.
    """
    want = re.compile(rf"\bexit (?:code )?{int(code)}\b", re.I)
    for label, text in ledger_bullets(entry):
        if label not in PROPOSING_BULLETS or not want.search(text):
            continue
        for sentence in re.split(r"(?<=[.;]) +", text):
            if want.search(sentence):
                return sentence.strip()
        return text.strip()
    return None


#: What `proposing_quote` must return. The live instance first, because it is
#: the one the repair was written for and the only one whose words a reader has
#: already been misled by.
#: Fields: (the entry, the code, the words expected)
QUOTE_CASES = (
    # The live false positive, wrapped the way `docs/ideas.md` wraps it, with
    # the number on a continuation line. The quote has to reach back over the
    # wrap or it prints "exit 3 rather than crash." and still hides the
    # "must still" that makes it an assertion.
    # The colon is deliberately not a sentence break. "The test case is the
    # one that matters:" is the half that tells a reader the entry is naming a
    # test rather than asking for a number, so splitting it off would throw
    # away the context the quote exists to supply.
    ("### x\n- First step: a reader wired into `tools/read_paper.py` between\n"
     "  the HTML routes and the abstract fallback. The test case is the one\n"
     "  that matters: a sandbox with no `pypdf` must still\n"
     "  exit 3 rather than crash.\n", 3,
     "The test case is the one that matters: a sandbox with no `pypdf` must "
     "still exit 3 rather than crash."),
    # A real ask quotes as a real ask, so the quote does not only exonerate.
    ("### x\n- What: `tools/board.py` should refuse an unknown seat\n"
     "  with exit 2 rather than reporting zero.\n", 2,
     "`tools/board.py` should refuse an unknown seat with exit 2 rather "
     "than reporting zero."),
    # A code named only in a bullet this gate does not read quotes as nothing,
    # which keeps the quote's domain identical to the finding's.
    ("### x\n- Trigger: it answered undecided, exit 3\n", 3, None),
    # A code the entry does not name at all.
    ("### x\n- What: `tools/board.py` should use exit 4\n", 9, None),
)

LEDGER_CASES = (
    # The live instance, wrapped the way the entry actually wraps, with the
    # number past the first line of its bullet.
    ("### 2026-11-02 - Refuse a seat name\n"
     "- Trigger: `tools/board.py inbox --seat x` answered 0 messages\n"
     "- What: refuse an unknown one\n  with exit 2 rather than reporting "
     "zero.\n- Status: proposed\n",
     (("board", 2),)),
    # An observed code is not a proposal. This is the 2026-10-24 entry, and
    # the case that makes the field scoping a measurement.
    ("### 2026-10-24 — A detector\n"
     "- Trigger: `tools/check_authority.py --range x` answered undecided, "
     "exit 3\n- What: an auditable waiver, in the `# noqa` idiom\n",
     ()),
    # Zero is not allocable, so naming it is not an ask.
    ("### x\n- What: `tools/merge_order.py` should answer exit 0\n", ()),
    # An entry naming no tool proposes nothing this gate can check.
    ("### x\n- What: refuse it with exit 2\n", ()),
    # `exit code 4` is the same ask as `exit 4`.
    ("### x\n- What: `tools/board.py` should use exit code 4\n",
     (("board", 4),)),
    # Two tools and one code is two pairs, because the gate cannot tell which
    # tool the sentence meant and answering for one would be a guess.
    ("### x\n- What: `tools/a.py` and `tools/b.py` exit 2\n",
     (("a", 2), ("b", 2))),
    # An off-schema bullet, one carrying no `Label:` at all, closes the
    # labelled bullet before it, so its wrapped lines are not read as part of
    # it. `docs/ideas.md` holds 539 such bullets today, so this is live data
    # and not a hypothetical. The instance that found it: the correction
    # recording that this entry had asked for the wrong number quotes
    # `exit 2`, and absorbing that quote into `What:` kept the gate red for
    # the sentence repairing it.
    ("### x\n- What: `tools/board.py` should refuse an unknown seat\n"
     "- The number here was wrong, and the reason is that it said\n"
     "  exit 2 and not 1.\n",
     ()),
    # And the labelled form of the same correction, which is what the live
    # entry carries now. `Answered:` is not a proposing bullet, so the quote
    # inside it is an observation.
    ("### x\n- What: `tools/board.py` should refuse an unknown seat\n"
     "- Answered: the number here was wrong. It said\n  exit 2 and not 1.\n",
     ()),
)


def exits():
    """The exit codes `tools/` has already spent, so an ask can name a free one.

    This gate grades a measurement and not an edition. It is in `all` because
    what it protects is a sentence this seat writes into `docs/ideas.md`,
    which is this seat's own surface, and because the one instance in the file
    was this seat's and was answered by the seat that could not honour it.

    It fails on an entry asking a tool to spend a code that tool already
    writes down. It does not fail on a proposal against a file with no exit
    surface, because `tools/noship.py` is named in a 2026-09-26 entry and does
    not exist yet, and holding the ledger red over a file whose absence is the
    point of the entry would be this seat failing on another seat's unwritten
    work. That prints CANNOT, which is a third answer and never a pass.

    A free number in a file whose enumeration is partial prints as free and
    says so, because a provisional answer read as a checked one is the defect
    directly above this gate in the file.
    """
    tools = ROOT / "tools"
    files = sorted(tools.glob("*.py"))
    if not files:
        print("  FAIL    tools/ holds no python files, so every number below")
        print("          would read as free and this map would be a clean")
        print("          answer about nothing")
        return 1

    bad = 0
    for label, cases, fn in (("CERTAINTY_CASES", CERTAINTY_CASES,
                              exit_certainty),
                             ("EXIT_CASES", EXIT_CASES, spent_exits),
                             ("LEDGER_CASES", LEDGER_CASES, proposed_exits)):
        wrong = 0
        for i, (text, want) in enumerate(cases):
            if (got := fn(text)) != want:
                wrong = 1
                bad = 1
                print(f"  CASE    {fn.__name__} case {i} wanted {want!r} and "
                      f"got {got!r}")
        print(f"{label:<42} {len(cases) - wrong} of {len(cases)}")
    wrong = 0
    for spent, proposed, want in COLLISION_CASES:
        if (got := exit_collision(spent, proposed)) != want:
            wrong = 1
            bad = 1
            print(f"  CASE    exit_collision({spent!r}, {proposed}) wanted "
                  f"{want!r} and got {got!r}")
    print(f"{'COLLISION_CASES':<42} "
          f"{len(COLLISION_CASES) - wrong} of {len(COLLISION_CASES)}")
    wrong = 0
    for entry, code, want in QUOTE_CASES:
        if (got := proposing_quote(entry, code)) != want:
            wrong = 1
            bad = 1
            print(f"  CASE    proposing_quote(.., {code}) wanted {want!r} "
                  f"and got {got!r}")
    print(f"{'QUOTE_CASES':<42} "
          f"{len(QUOTE_CASES) - wrong} of {len(QUOTE_CASES)}")
    print()

    spent, certainty = {}, {}
    for path in files:
        source = path.read_text(encoding="utf-8")
        certainty[path.name] = exit_certainty(source)
        if (codes := spent_exits(source)) is not None:
            spent[path.name] = codes

    counted = collections.Counter(certainty.values())
    allocated = collections.Counter()
    for codes in spent.values():
        for code, _ in codes:
            allocated[code] += 1
    print(f"files under tools/                         {len(files)}")
    print(f"  every exit path written down             "
          f"{counted['complete']}")
    print(f"  some path computes its status            {counted['partial']}")
    print(f"  no exit surface at all, a library        {counted[None]}")
    print("codes written down, and in how many files  "
          + "  ".join(f"{c} in {n}" for c, n in sorted(allocated.items())))
    print()
    named = {name: codes for name, codes in spent.items()
             if any(n for _, n in codes)}
    print("the files that name their codes, which is what makes a")
    print("collision legible to a seat proposing one:")
    for name in sorted(named):
        pairs = ", ".join(f"{c} {n}" for c, n in named[name] if n)
        print(f"    {name:<32} {pairs}")
    print()

    entries = re.split(r"\n(?=### )",
                       (ROOT / "docs/ideas.md").read_text(encoding="utf-8"))
    asks = answered = clean = 0
    for entry in entries:
        for tool, code in proposed_exits(entry):
            asks += 1
            head = entry.split("\n", 1)[0].lstrip("# ").strip()[:64]
            codes = spent.get(f"{tool}.py")
            if codes is None:
                why = ("is not in the tree yet"
                       if not (tools / f"{tool}.py").exists()
                       else "has no exit surface to collide with")
                print(f"  CANNOT  tools/{tool}.py {why}, so exit {code} is "
                      f"unanswered rather than free")
                print(f"          {head}")
                continue
            answered += 1
            if (hit := exit_collision(codes, code)) is not None:
                bad = 1
                means = hit[1] or "an unnamed return in that same file"
                free = " ".join(str(c) for c in range(1, 12)
                                if exit_collision(codes, c) is None)
                print(f"  FAIL    an entry asks tools/{tool}.py for exit "
                      f"{code}, which it already spends as {means}")
                print(f"          {head}")
                # The words, before the remedy. A reader cannot judge this
                # finding without them and the first cross-seat instance of
                # it was false, so the quote comes ahead of the free list
                # rather than under it.
                if (quote := proposing_quote(entry, code)) is not None:
                    print(f"          it says: {quote}")
                    print("          read that before spending a number: an "
                          "entry asserting that a code STILL comes out is "
                          "not")
                    print("          asking for one, and this gate cannot "
                          "tell the two apart")
                print(f"          free in that file: {free}")
            elif certainty.get(f"{tool}.py") == "partial":
                clean += 1
                print(f"  FREE    exit {code} is in none of tools/{tool}.py's "
                      f"written codes, and one of its paths computes a "
                      f"status, so this is provisional")
                print(f"          {head}")
            else:
                clean += 1
                print(f"  OK      exit {code} is free in tools/{tool}.py, "
                      f"every exit path of which is written down")
                print(f"          {head}")
    print(f"ledger entries proposing an exit code      {asks}")
    print(f"  answered against the file's allocation   {answered}")
    print(f"  of those, free                           {clean}")
    print()
    print("The reading, which is not the check: 2 is the code this file's")
    print("own dispatcher returns for an unknown gate, and carrying that")
    print("convention into a sentence about another seat's tool is how the")
    print("instance above happened. The number was a grep away in the file")
    print("the ask names.")
    return bad


#: Bodies whose every blank-line-separated block is at or under the board's
#: block limit, with the length the formatter must leave them at. The property
#: is the gate: the formatter is the identity function on prose written in
#: short blocks, so a sender writing that way can count its own draft and get
#: the number the server will count. A case here that starts failing means the
#: pre-send count a seat takes on its draft is no longer the posted length.
BLOCK_IDENTITY_CASES = (
    ("one short block.", 16),
    ("first block.\n\nsecond block.", 27),
    # Hard wrapping inside a block is free, because the formatter collapses a
    # single newline to the space it replaced. Every seat writes this way.
    ("a block\nwrapped by hand\nat a narrow column.", 43),
    ("x" * 420, 420),
)

#: Bodies the formatter must lengthen, with the floor of the growth. A block
#: over the limit is split and the pieces are rejoined on a blank line, so one
#: space becomes two newlines and the body gains a character per split. This is
#: the half a sender cannot predict from its own draft.
BLOCK_GROWTH_CASES = (
    ("word " * 84 + "end.", 1),
    ("word " * 200 + "end.", 1),
)


def block_bodies(source):
    """Which POST paths in a tool hand the board a body, and which format it.

    Returns (name, formatted) per body-carrying payload, named by the enclosing
    function, because the question is per command and not per file. `formatted`
    is whether the body goes through the shape formatter on the way out.

    Read off the source rather than by importing, because a gate that imports
    another seat's module runs it, and this question is answerable by reading.
    """
    out = []
    current = None
    for line in source.splitlines():
        if match := re.match(r"def (\w+)\(", line):
            current = match.group(1)
        if current is None:
            continue
        match = re.search(r"[\"']body[\"']\s*(?::|\]\s*=)\s*(.+?),?\s*$",
                          line)
        if match:
            value = match.group(1).rstrip(",").strip()
            if not value.startswith(("args.body", "scannable(", "body")):
                continue
            out.append((current, value.startswith("scannable(")))
    return out


def blocks():
    """The board's block limit, which decides what a sender can count.

    This gate grades a measurement and not an edition, like `exits` above it,
    and it is this seat's because the thing it protects is prose this seat
    writes. Canon law 15 binds "any line of copy", and a `note` on the bus is a
    line of copy with a reader.

    The fact it exists for, measured 2026-11-02 on the engineer seat's own
    report: the client reflows prose before it posts, so the body the board
    counts against the wake limit is not the body the sender typed. The
    engineer's number was 1500 characters leaving as 1506. The useful half is
    that the growth is not a mystery. It is one character per block the
    formatter has to split, so it is zero on prose already written in short
    blocks, and the property table above is what holds that.

    The second half fails on a body-carrying POST path that skips the
    formatter. It is reported rather than repaired here, because `tools/` is
    not this seat's surface and the ask is in `docs/ideas.md` under the
    engineer seat's name.
    """
    path = ROOT / "tools/board.py"
    if not path.exists():
        print("  FAIL    tools/board.py is not in the tree, so the limit this")
        print("          gate reads is unverified and every count a seat")
        print("          takes on its own draft is unchecked")
        return 1
    source = path.read_text(encoding="utf-8")

    namespace = {}
    exec(compile(re.search(
        r"BODY_BLOCK_LIMIT = \d+", source).group(0), "<limit>", "exec"),
        namespace)
    limit = namespace["BODY_BLOCK_LIMIT"]
    formatter = None
    try:
        module = {"re": re}
        body = re.search(r"\ndef scannable\(.*?\n(?=\n\ndef )", source,
                         re.S).group(0)
        exec(compile(body.replace("BODY_BLOCK_LIMIT", str(limit)),
                     "<scannable>", "exec"), module)
        formatter = module["scannable"]
    except (AttributeError, SyntaxError, KeyError):
        print("  FAIL    tools/board.py has no readable block formatter, so")
        print("          the property below cannot be checked and a sender's")
        print("          own count is unverified")
        return 1

    bad = 0
    print(f"{'the board block limit, read from the tool':<42} {limit}")
    wrong = 0
    for text, want in BLOCK_IDENTITY_CASES:
        if (got := len(formatter(text))) != want:
            wrong += 1
            bad = 1
            print(f"  CASE    a body of {len(text)} characters in blocks at or "
                  f"under the limit posted at {got}, wanted {want}")
    print(f"{'BLOCK_IDENTITY_CASES':<42} "
          f"{len(BLOCK_IDENTITY_CASES) - wrong} of "
          f"{len(BLOCK_IDENTITY_CASES)}")
    wrong = 0
    for text, floor in BLOCK_GROWTH_CASES:
        if (grew := len(formatter(text)) - len(text)) < floor:
            wrong += 1
            bad = 1
            print(f"  CASE    a single block of {len(text)} characters grew by "
                  f"{grew}, wanted at least {floor}")
    print(f"{'BLOCK_GROWTH_CASES':<42} "
          f"{len(BLOCK_GROWTH_CASES) - wrong} of {len(BLOCK_GROWTH_CASES)}")
    print()

    print("what a sender can count on its own draft, by the shape it wrote:")
    print(f"    {('every block at or under ' + str(limit)):<38}"
          f"the typed length is the posted length")
    print(f"    {'one block over it':<38}"
          f"the typed length plus one per split")
    print()

    carried = block_bodies(source)
    formatted = [name for name, ok in carried if ok]
    bare = [name for name, ok in carried if not ok]
    print(f"{'POST paths handing the board a body':<42} {len(carried)}")
    print(f"{'  of those running the formatter':<42} {len(formatted)}"
          f"  {', '.join(formatted)}")
    print(f"{'  of those posting the body as typed':<42} {len(bare)}"
          f"  {', '.join(bare)}")
    for name in bare:
        bad = 1
        print(f"  FAIL    {name} posts the body as typed, so a block over the "
              f"limit is refused by the")
        print("          server rather than reshaped, and no pre-send count "
              "of it is the posted one.")
        print("          The refusal the formatter was written from is quoted "
              "in that file as a")
        print("          COMMENT refusal, so the one path the evidence names "
              "is a path that skips it.")
    if bare:
        print("          Red in the engineer seat's lane and not repairable "
              "from here, the way")
        print("          `taste` is red on the frontend's. The ask is in "
              "docs/ideas.md.")
    if not bare:
        print("  OK      every body-carrying path runs the formatter, so the")
        print("          posted length is computable on every one of them")
    print()
    print("The reading, which is not the check: the growth is small and the")
    print("entry it answers is not. Three cut sends on record spread 58")
    print("characters on delivered-plus-subject, and a body of that length")
    print("cannot gain more than about six here, so the reflow is a term the")
    print("model was missing rather than the reason no formula fit.")
    return bad


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    # Paths after the subcommand go to `measure`. Without this, the arguments
    # were accepted and silently ignored, so `measure <path>` reported on
    # site/content/issues and a grade could read the wrong artifact's figures
    # under the right artifact's name, which is the defect this file exists to
    # prevent (ban list 91, fixed 2026-10-06).
    paths = sys.argv[2:]
    rc = 0
    takes_paths = TAKES_PATHS
    # `--live` is the answer to `editions`, inside one run. It replaces the
    # archive glob with the editions the product actually serves, fetched from
    # the public pages and un-rendered, so a pass grades what a reader opens
    # rather than what somebody committed. Entry 141 named this class on
    # 2026-10-26 and enforced the reading half of it; this is the half that
    # points the commands at the right artifact instead of the run.
    global SCOPE_SOURCE
    if "--live" in paths:
        paths = [x for x in paths if x != "--live"]
        live = served_paths()
        if live is None:
            print("--live could not reach the product, so nothing was read.")
            print("A grade on an unreached artifact is the defect entry 141")
            print("names, so this exits rather than falling back to the")
            print("archive under the name `live`.")
            return 1
        # `named` wins a tie, because a caller who hands a path alongside
        # `--live` has chosen a scope and `scope` must not claim the
        # product's on their behalf.
        SCOPE_SOURCE = "named" if paths else "live"
        paths = [str(x) for x in live] + paths
    elif paths:
        SCOPE_SOURCE = "named"
    # `enforcements` takes a git ref rather than a path, because ban list 105
    # is about the file the press runs and that file is only reachable through
    # the commit the deploy was built from.
    # `selfcheck` is not in `all`, because `all` is run over the artifact and
    # this one is run over the run's own diff. It takes a git ref or a range.
    # `compare` is not in `all` for the same reason `selfcheck` is not: it
    # takes two artifacts the caller has chosen and proved comparable, and
    # `all` runs over whatever is in site/content/issues.
    # The command table, hoisted out of the `for` below so the dispatcher can
    # be asked whether a name exists BEFORE it does any work. Until it was
    # hoisted, an unknown name matched nothing, printed nothing and returned
    # the initial rc of 0, so this file answered "nothing to report" to a
    # question it had never been able to see. The ExO seat hit that on
    # 2026-11-02 running `cadence` against `main`, where the subcommand had
    # shipped only on this seat's unmerged branch: silent, exit 0, and
    # indistinguishable from a pass. A nonsense argument behaved identically.
    # That is the instrument-answers-a-question-it-cannot-see class this seat
    # filed the same night, arriving through the dispatcher instead of
    # through a gate body (INC-2026-11-02-the-subcommand-dispatcher-
    # answered-ok-to-a-name-it-did-not-have).
    commands = (("enforcements", enforcements), ("sweep", sweep),
                ("taste", taste),
                ("stale", stale), ("measure", measure), ("links", links),
                ("delivery", delivery), ("claims", claims),
                ("reading", reading),
                ("candidates", candidates),
                ("deadlines", deadlines),
                ("press", press),
                ("cadence", cadence),
                ("queued", queued),
                ("ledger", ledger),
                ("firstuse", firstuse),
                ("generator", generator),
                ("specimens", specimens),
                ("standalone", standalone),
                ("provenance", provenance),
                ("devices", devices),
                ("figures", figures),
                ("routed", routed),
                ("editions", editions),
                ("marks", marks),
                ("ungated", ungated),
                ("slotwords", slotwords),
                ("slotheads", slotheads),
                ("apparatus", apparatus),
                ("captions", captions),
                ("blockrules", blockrules),
                ("doubles", doubles),
                ("dispatch", dispatch),
                ("columns", columns),
                ("flags", flags),
                ("exits", exits),
                ("blocks", blocks),
                ("compare", compare), ("selfcheck", selfcheck))
    # An unknown name is a usage failure and never a pass. Exit 2 rather than
    # 1, so a caller can tell "this gate is not here" from "this gate ran and
    # failed", which is the distinction the silent exit 0 destroyed.
    rc_unknown = _dispatch_rc(which, [name for name, _ in commands])
    if rc_unknown:
        print(f"unknown subcommand: {which}", file=sys.stderr)
        print("This file has no gate by that name, so nothing was checked.",
              file=sys.stderr)
        print("A subcommand that shipped on a branch is not here until that",
              file=sys.stderr)
        print("branch merges, so check the pull request before reading this",
              file=sys.stderr)
        print("file's silence as a pass.", file=sys.stderr)
        print("", file=sys.stderr)
        print("known subcommands:", file=sys.stderr)
        for name, _ in commands:
            print(f"  {name}", file=sys.stderr)
        print("  all", file=sys.stderr)
        return rc_unknown
    # A target this file cannot open is the dispatcher's defect at the argument
    # level, so it gets the dispatcher's answer: nothing was checked, the exit
    # code says so, and 2 separates it from a gate that ran and failed. One
    # check here rather than one per gate, because the altitude is the whole
    # point: thirteen gates resolve paths and four of them already refused this
    # condition, which is how the other nine were found.
    absent = missing_targets(paths, lambda x: (ROOT / x).exists())
    if which in PATH_ARG_COMMANDS and absent:
        for target in absent:
            print(f"unknown target: {target}", file=sys.stderr)
        print(f"`{which}` grades the artifacts it is handed, and these are not",
              file=sys.stderr)
        print("there, so nothing was graded. A verdict under a path that does",
              file=sys.stderr)
        print("not exist is ban list 91 with the figure left out.",
              file=sys.stderr)
        return DISPATCH_UNKNOWN
    for name, fn in commands:
        if which == name or (which == "all"
                             and name not in ("selfcheck", "compare",
                                              "press", "cadence", "queued")):
            print(f"==== {name} ====")
            if name in ("enforcements", "selfcheck", "candidates", "ledger",
                        "routed"):
                rc |= fn(paths[0]) if (which == name and paths) else fn()
            else:
                rc |= fn(paths) if (name in takes_paths and paths) else fn()
            print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
