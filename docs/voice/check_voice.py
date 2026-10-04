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

Not wired to anything yet, which is the honest half of L-A22: until a command
that already runs calls this, these three are enforced at the reliability of
someone choosing to type it. Filed in docs/ideas.md for the engineer, to move
to tools/ and add to .github/workflows/checks.yml beside check_registers.py.

Usage:  python3 docs/voice/check_voice.py [enforcements|stale|measure|all]
Exit:   1 if any check reports a finding, 0 if clean.
"""
import collections
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
        if not re.search(r"Enforced\b", nb):
            continue
        claims = LANDED.findall(body)
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


def measure(paths=None):
    retired = hidden_weeks()
    paths = paths or sorted((ROOT / "site/content/issues").glob("*.md"))
    rc = 0
    for p in paths:
        if not p.exists():
            print(f"{p}: missing")
            continue
        t = p.read_text(encoding="utf-8")
        na = collections.Counter(c for c in t if ord(c) > 127)
        paras = [x for x in re.split(r"\n\s*\n", t) if x.strip()]
        lens = [len(x.split()) for x in paras]
        off = p.stem in retired
        print(f"{p.relative_to(ROOT)}" + ("   [retired, not served]" if off else ""))
        print(f"  words {len(t.split()):<6} paragraphs {len(paras):<4} "
              f"longest {max(lens) if lens else 0:<4} over100 {len([x for x in lens if x > 100])}")
        print(f"  em dashes {t.count(chr(8212)):<4} semicolons {t.count(';'):<4} "
              f"non-ASCII {sum(na.values()):<5} distinct {len(na)}")
        for c, k in na.most_common():
            print(f"    U+{ord(c):04X} {unicodedata.name(c, '?'):<28} x{k}")
        if not off and (sum(na.values()) or t.count(chr(8212))):
            rc = 1
    print()
    print("Every figure above is printed under the path it was measured on.")
    print("A grade quotes it with that path or does not quote it (ban list 91).")
    return rc


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    rc = 0
    for name, fn in (("enforcements", enforcements), ("stale", stale),
                     ("measure", measure)):
        if which in (name, "all"):
            print(f"==== {name} ====")
            rc |= fn()
            print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
