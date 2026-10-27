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
           reading|taste|candidates|firstuse|generator|specimens|all]
           [path...]
        python3 docs/voice/check_voice.py enforcements <git-ref>
        python3 docs/voice/check_voice.py selfcheck <git-ref-or-range>
Exit:   1 if any check reports a finding, 0 if clean.
"""
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


def quoting(text):
    """Is the mark inside something quoted, or inside a command?

    The two exceptions are the whole difficulty and both were settled in prose
    by the grades of 2026-10-10 and 2026-10-12. A semicolon inside a quotation
    of the artifact or of a surface's output cannot be struck without
    falsifying the quote, and a semicolon inside a shell line is the literal
    character. Everything else is a finding.
    """
    stripped = text.lstrip()
    if text.startswith(("    ", "\t")) or stripped.startswith((">", "$", "#!")):
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
            if n in fences[path] or quoting(text):
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
)


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
    return [(want, cell) for want, cell in STATE_CASES
            if claim_state(cell)[0] != want]


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


def claims():
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
    print(f"  the verdict cases                         {len(STATE_CASES)} pass")
    rows, fails = claim_rows(), []
    hedged, moved, spread, gone = [], [], [], []
    surfaces = []
    for glob in SURFACE_GLOBS:
        surfaces += sorted(ROOT.glob(glob))
    scanned = [(p, surface_sentences(p)) for p in surfaces if p.is_file()]
    print(f"rows in docs/agents/quality-claims.md       {len(rows)}")
    print(f"  not `held`, so hedged or not shipped      "
          f"{sum(1 for r in rows if r['state'] != 'held')}")
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
            rel = str(path.relative_to(ROOT))
            for line, body in sentences:
                have = claim_words(body)
                score = max((len(w & have) / len(w)) if w else 0 for w in words)
                if score >= 0.6 and max(len(w & have) for w in words) >= 3:
                    hits.append((rel, line, body, score))
        print(f"{row['state']:>13}  \"{row['label'][:58]}\"")
        if row["ambiguous"]:
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
    targets = [ROOT / p for p in paths] if paths else []
    if not targets:
        for glob in SURFACE_GLOBS + ARCHIVE_GLOBS:
            targets += sorted(ROOT.glob(glob))
    hits = []
    for path in [t for t in targets if t.is_file()]:
        text, marks = surface_text(path)
        for m in READING.finditer(text):
            around = norm(text[max(0, m.start() - 40):m.start() + 72])
            hits.append((str(path.relative_to(ROOT)),
                         line_of(marks, m.start()), m.group(), around))
    print(f"surfaces read                               "
          f"{len([t for t in targets if t.is_file()])}")
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
    new = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2 or not parts[0].startswith("A"):
            continue
        path = parts[-1]
        if path.startswith("docs/voice/") and path.endswith(".md") \
                and (ROOT / path).exists() and (ROOT / path) != AWAITING:
            new.append(path)
    clashes = []
    unregistered = []
    registered = registered_candidates()
    for path in new:
        body = (ROOT / path).read_text()
        named = set(CANDIDATE_FILE.findall(body)) | {m for m in re.findall(
            r"([a-z0-9][A-Za-z0-9_.-]*\.md)", body)}
        surfaces = sorted(set(SURFACE.findall(body)))
        if surfaces and is_candidate(path) \
                and pathlib.Path(path).name not in registered:
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

#: What `deadline_findings` must say, pinned against a fixed clock so a case
#: here means the same thing on every day this file is run. The rows are the
#: register's own, trimmed to the cells that carry the reading. The false cases
#: are load-bearing in the usual direction: a question with no clock at all is
#: the ordinary shape of this table and must stay silent, because nine of its
#: ten rows wait on her with no standard attached and failing them would make
#: the check unusable by the register it reads.
#: Fields: (the codes expected, the row)
DEADLINE_CASES = (
    ((), "| Does a paid tier keep a bullet for a machine that does not "
     "exist, hedged, or lose the bullet? | `claim-repairs-2026-10-18.md`, "
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
    """One row's clock problems, as codes, read against a given moment."""
    found = DEADLINE.findall(row)
    out = []
    if SILENCE.search(row) and not found:
        out.append("unreadable")
    for stamp in found:
        when = datetime.datetime.fromisoformat(stamp).replace(
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
    print(f"read at                                    "
          f"{now.strftime('%Y-%m-%dT%H:%MZ')}")
    for row in rows:
        for code in deadline_findings(row, now):
            rc = 1
            question = [c.strip() for c in row.split("|")][1]
            print(f"  FAIL    {question[:88]}")
            if code == "unreadable":
                print("            argues a silence rule and names no "
                      "`deadline YYYY-MM-DDTHH:MMZ`")
            else:
                print("            the deadline passed and the row is still "
                      "open, so the recommendation in the candidate is in "
                      "force and this register says it is still a question")
    if rc == 0:
        print("  every clock here is readable and none of them has run out")
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


def scope(paths, retired, given):
    """What this pass read, printed before any count it reports.

    `L-A47`: an instrument's scope is part of its answer, and a scope it does
    not state is whatever it happened to be pointed at. This pass globs
    `site/content/issues/*.md` and calls the result the issues. The site
    archive is not the send record. 2026-W40 went to readers on 2026-10-05 and
    never became a file in this repository, so every count this pass has ever
    printed described the archive while reading as a verdict on what the press
    sends, which is `INC-2026-10-24-a-gate-grades-a-print-against-rules-written-
    after-it`. The authority on what was sent is the `digests` table, reachable
    only with `NEON_RO_URL`, so when that is unset the gap is named here rather
    than left for a reader to infer from a number.
    """
    if given:
        print(f"  read from   {len(paths)} path(s) named on the command line")
        print( "              a figure below belongs to the artifact above it")
        print( "              and to no other, which is ban list 91")
        return
    served = [pathlib.Path(x) for x in paths]
    off = [x.stem for x in served if x.stem in retired]
    on = [x.stem for x in served if x.stem not in retired]
    print(f"  read from   site/content/issues, {len(on)} served: "
          f"{', '.join(on) if on else 'none'}")
    if off:
        print(f"              {len(off)} retired and not served: {', '.join(off)}")
    print( "  NOT read    the send record. An issue is not a file here when it")
    print( "              sends: 2026-W40 reached readers on 2026-10-05 and is")
    print( "              not in the list above. The authority is the digests")
    if os.environ.get("NEON_RO_URL"):
        print( "              table, and NEON_RO_URL is set, so a run can check")
        print( "              this list against it rather than trusting it")
    else:
        print( "              table and NEON_RO_URL is unset, so this pass")
        print( "              cannot say how many prints it has never seen")
    print( "              A count below grades this archive. Reading it as a")
    print( "              grade of the generator needs the date of the print")
    print( "              and the dates of the rules, which is a review's job")


def firstuse(paths=None):
    retired = hidden_weeks()
    given = paths is not None
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    rc = 0
    scope(paths, retired, given)
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
#: gives it a target of zero, or says "never", or the canon numbers it a law and
#: the owner has ruled on it twice. The phrase is quoted so a row cannot outlive
#: the rule it describes, which is `blockrules`' technique and the reason that
#: pass catches a dropped rule.
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
    # Where the paths came from, and not the directory this pass used to
    # assume they came from. L-A47 says an instrument's scope is part of its
    # answer, and this line printed `site/content/issues` for a path given on
    # the command line, so the one pass that reported its own scope reported
    # somebody else's directory. Found by pointing it at a served edition.
    inside = all(str(x).startswith(str(ROOT / "site/content/issues"))
                 for x in paths)
    print(f"  read from   {'site/content/issues' if inside else 'paths given'},"
          f" {len(paths)} issue(s): {', '.join(p.stem for p in paths)}")
    print(f"  sentences whose subject is 'you' and whose verb is past  "
          f"{len(hits) + len(exempt)}")
    for path, n, span in hits:
        print(f"  FAIL    {path.relative_to(ROOT)}:{n}")
        print(f"            {span[:92]}")
    for path, n, span in exempt:
        print(f"  HERS    {path.relative_to(ROOT)}:{n}  exempt, in taste.md")
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
    weeks = served_weeks()
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
    weeks = served_weeks()
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


def editions(paths=None):
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
    weeks = served_weeks()
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
    sets = [(p, label) for p, label in CAPTION_SETS
            if not paths or p in paths]
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
# edits. Ban list 142 is the entry; this is its enforcement.
PRESS_APP = "weekly"
PRESS_FILE = "prompts/digest.md"
# The engineer's walk is bounded at 40 commits and the deployed commit passed
# that mark on 2026-10-26. 400 is not a tuned number, it is a window wide
# enough that the bound is the deploy's age rather than this seat's output
# rate, which is the whole defect being worked around here.
PRESS_WINDOW = 400


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


def press_cases():
    """The verdict function against its four pinned cases."""
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
    return rc


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
    is the defect ban list 142 names. The ledger entry of 2026-10-27 asks the
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
    try:
        sys.path.insert(0, str(ROOT))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_dh", ROOT / "tools" / "delivery_health.py")
        dh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dh)
    except Exception as e:
        print(f"  UNREACHED tools/delivery_health.py: {type(e).__name__}: {e}")
        print("    nothing was read, so nothing is concluded about the press")
        return 1
    body = _fetch(dh.RECEIPT_URL)
    if body is None:
        print("    nothing was read, so nothing is concluded about the press")
        return 1
    try:
        rows = {r["app"]: r for r in json.loads(body).get("deploy", [])}
    except (ValueError, KeyError, TypeError) as e:
        print(f"  UNREACHED {dh.RECEIPT_URL}: {type(e).__name__}: {e}")
        return 1
    row = rows.get(PRESS_APP)
    if row is None:
        print(f"  FAIL    the receipt carries no row for {PRESS_APP}, so the "
              f"press has never reported what it runs")
        return 1
    found = dh.undeployed_commits(ROOT, PRESS_APP, row.get("runtime_sha"),
                                  limit=PRESS_WINDOW, ref="origin/main")
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
    print(f"deployed commit                            {deployed or 'unknown'}")
    print(f"commits searched                           "
          f"{found.get('searched', 0)} of a {PRESS_WINDOW} window")
    print(f"the generator it carries                   {gen or 'unknown'}")
    print(f"deployed at                                {at or 'unknown'}")
    print(f"queued commits to the generator            {len(queued)}")
    for line in queued[:5]:
        print(f"    {line}")
    if len(queued) > 5:
        print(f"    and {len(queued) - 5} more")
    print()
    print(f"  {'FAIL' if verdict != 'CURRENT' else 'OK  '}    {verdict}: {why}")
    print()
    print("A verdict on an issue is a verdict on the generator that wrote it,")
    print("so the run that cannot name that generator is grading an unnamed")
    print("artifact. REFUSED is the answer to act on rather than to read")
    print("past: it means the window ran out and the number is recoverable,")
    print("not that the press was built from code nobody pushed.")
    return rc | (verdict != "CURRENT")


def _git_line(*args):
    out = _git_lines(*args)
    return out[0] if out else None


def _git_lines(*args):
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return []
    return [x for x in r.stdout.splitlines() if x.strip()]


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    # Paths after the subcommand go to `measure`. Without this, the arguments
    # were accepted and silently ignored, so `measure <path>` reported on
    # site/content/issues and a grade could read the wrong artifact's figures
    # under the right artifact's name, which is the defect this file exists to
    # prevent (ban list 91, fixed 2026-10-06).
    paths = sys.argv[2:]
    rc = 0
    takes_paths = {"measure", "links", "delivery", "compare", "firstuse",
                   "generator", "specimens", "standalone", "devices",
                   "captions", "marks", "provenance"}
    # `--live` is the answer to `editions`, inside one run. It replaces the
    # archive glob with the editions the product actually serves, fetched from
    # the public pages and un-rendered, so a pass grades what a reader opens
    # rather than what somebody committed. Entry 141 named this class on
    # 2026-10-26 and enforced the reading half of it; this is the half that
    # points the commands at the right artifact instead of the run.
    if "--live" in paths:
        paths = [x for x in paths if x != "--live"]
        live = served_paths()
        if live is None:
            print("--live could not reach the product, so nothing was read.")
            print("A grade on an unreached artifact is the defect entry 141")
            print("names, so this exits rather than falling back to the")
            print("archive under the name `live`.")
            return 1
        paths = [str(x) for x in live] + paths
    # `enforcements` takes a git ref rather than a path, because ban list 105
    # is about the file the press runs and that file is only reachable through
    # the commit the deploy was built from.
    # `selfcheck` is not in `all`, because `all` is run over the artifact and
    # this one is run over the run's own diff. It takes a git ref or a range.
    # `compare` is not in `all` for the same reason `selfcheck` is not: it
    # takes two artifacts the caller has chosen and proved comparable, and
    # `all` runs over whatever is in site/content/issues.
    for name, fn in (("enforcements", enforcements), ("sweep", sweep),
                     ("taste", taste),
                     ("stale", stale), ("measure", measure), ("links", links),
                     ("delivery", delivery), ("claims", claims),
                     ("reading", reading),
                     ("candidates", candidates),
                     ("deadlines", deadlines),
                     ("press", press),
                     ("ledger", ledger),
                     ("firstuse", firstuse),
                     ("generator", generator),
                     ("specimens", specimens),
                     ("standalone", standalone),
                     ("provenance", provenance),
                     ("devices", devices),
                     ("routed", routed),
                     ("editions", editions),
                     ("marks", marks),
                     ("ungated", ungated),
                     ("slotwords", slotwords),
                     ("captions", captions),
                     ("blockrules", blockrules),
                     ("compare", compare), ("selfcheck", selfcheck)):
        if which == name or (which == "all"
                             and name not in ("selfcheck", "compare",
                                              "press")):
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
