# The digest quality tier

What every issue has to clear before it reaches a reader, and who or what
clears it. Written by the engineer agent on 2026-09-20 for sprint
2026-09-21 item 4, on the owner's release gate: a four on the OKR
benchmark's five axes (ADR-26). Four is the floor for shipping at all, so
the content aims above it.

The tier has two halves and they are enforced differently.

The machine half runs inside the pipeline, before the email goes out, in
`tools/check_digest_quality.py`. The judgment half is read by a person or
by the writer seat's daily grading run. Nothing on this page is a
suggestion. Every line names where it is checked, because the register map
(docs/agents/registers.md) is blunt about what happens otherwise: a rule
written down but never opened at the point of production is documentation,
and documentation does not stop anything. The ban list was already complete
and correct on the day 2026-W37 shipped breaking eleven of its entries.

## The four lines

The sprint named four. Each one is stated as a test, not as a value.

**1. Accuracy.** Every claim in the issue is supported by the paper it
cites, at the strength the issue states, and the link resolves to the paper
whose title is printed beside it. The standard is the 2026-09-19 audit
(docs/evals/2026-09-19-digest-accuracy-audit.md), which read 34 claims
against their sources by hand and found three wrong. A number that came
from the corpus is not thereby true, and an issue that already sent does
not get to keep a wrong claim.

**2. Voice that does not read as templated.** The issue reads as written
by a person about this particular day. The test the ban list uses is the
sharpest one available: a heading, an opening or an item that would fit
tomorrow's issue unchanged is furniture, so it fails. The enumerated tells
are docs/voice/ban-list.md, and the ones that can be decided from the text
alone are in the machine half below.

**3. Evidence density.** Every item names the paper it rests on and links
it. The claim graph knows the supporting paper for every edge it emits, so
an item with no link is a payload gap rather than an editorial choice.
This is O1 KR3's floor.

**4. A consequence line per item.** Every item ends on what it means for
the reader, never on its citation. This is the craft-scan finding from
PR #23: Import AI ends on "Why this matters", The Batch on "We're
thinking", and alexandria's items ended on a URL, which leaves the reader
to work out the consequence alone. End on the judgment, then the source.

## What the machine checks

`python3 tools/check_digest_quality.py <issue.md>` and, inside the
pipeline, `hold_for_quality()` in `pipeline/weekly.py`. Blocking findings
stop the email. Warnings are printed and counted and never fatal, because a
gate that blocks on something the generator cannot fix does not raise
quality, it stops the newsletter.

| Rule | Level | Ban list | What it catches |
| --- | --- | --- | --- |
| `skeleton-heading` | block | 19, 20 | "Trailblazing", "Gaining traction", "Left behind", "Read these yourself" and the other slot labels printed as headings |
| `typesetter-punctuation` | block | 13 | non-breaking hyphens, narrow spaces, the multiplication sign |
| `internal-vocabulary` | block | 14 | "three supports", claim ids, the ISO week code, triage internals |
| `ends-on-citation` | block | 25 | an item whose last line is its source |
| `date-in-title` | block | 22 | the bracketed date range in the headline |
| `slop-lexicon` | block | 1 | "delve", "tapestry", "paradigm shift" and the rest of the always-wrong column |
| `no-title` | block | n/a | an issue with no H1, so the email has no subject |
| `daily-too-short` | block | n/a | a daily that is neither an issue nor the honest empty line |
| `citation-per-item` | warn | n/a | an item with no link in it |
| `uniform-length`, `uniform-rhythm` | warn | 21, 3 | every item cut to one shape, which is what padding looks like |
| `no-contents` | warn | 23 | a first screen that does not say what is in the issue |
| `bare-number` | warn | 24 | a figure with nothing beside it to place it against |
| `slop-lexicon` (context) | warn | 1 | "robust", "crucial", "leverage" and the rest of the maybe-column |
| `hedge-stack`, `empty-intensifier` | warn | 4, 5 | "could potentially", "very" |
| `colon-title` | warn | 11 | a title whose second half explains the first |
| `daily-too-long` | warn | 21 | a daily written at weekly length |

Two of these move to blocking on a named trigger rather than on a feeling.
`citation-per-item` becomes blocking on the day `gather()` carries the
supporting paper's title and url into the traction and deprecation streams,
which is already specified in docs/ideas.md. `bare-number` becomes blocking
when it has run for four issues without a false positive.

## What a person checks

These need a reader. The gate cannot decide any of them, and pretending
otherwise would be worse than leaving them here.

| Line | Who reads it | When |
| --- | --- | --- |
| Are the numbers in each claim what the paper actually reports? | the research seat's Step 1 for the new week, the accuracy audit retroactively | before the send for new claims |
| Does the link resolve to the paper whose title is printed? | `python3 tools/check_issue_citations.py <issue>`, which needs the network | before the send |
| Does the issue read as written by a person about today? | the writer seat's daily grading run (ADR-28) | after publication, into the next prompt |
| Is a term of art handed to the reader on first use? | the writer seat, ban list 26 | the grading run |
| Is the ranking visible in the prose's energy? | the writer seat, ban list 12 | the grading run |
| Does the length match how much actually happened? | the writer seat and the owner | the grading run |

## Running it

```bash
python3 tools/check_digest_quality.py site/content/issues/2026-W37.md
python3 tools/check_digest_quality.py --kind daily --strict issue.md
python3 tools/check_issue_citations.py site/content/issues/2026-W37.md
```

Exit 1 means at least one blocking finding. `--strict` makes warnings fatal
too, which is the right setting for a person reviewing an issue by hand and
the wrong one for the pipeline.

## What happens when an issue fails

Inside the pipeline the sequence is fixed.

1. The finished issue is checked, masthead and all, because the masthead
   ships with it.
2. If anything blocks, the generator gets one more try, with the blocking
   findings appended to its prompt as instructions. Warnings are never sent
   back, because the one extra call should not be spent chasing a judgment
   the regex could not make.
3. The second draft is checked. If it is clean it sends. If it still
   blocks, the better of the two drafts is written to the `digests` table
   and the email is held.

A held issue is not a lost issue. The body is in the database, the log says
why it was held, and the archive and the owner can both read it. If the
gate itself throws, the issue sends unchecked and the log says so, because
an unwritten newsletter is worse than an unchecked one.

## The two gates

Archive side: this file and docs/voice/ban-list.md. The writer seat appends
new tells, the owner rules, the engineer keeps the machine half in step
with the list.

Artifact side: `hold_for_quality()` runs on every send, and
`tools/check_digest_quality.py` runs by hand on any issue. This is the gate
the org keeps forgetting, so it is the one written in code.
