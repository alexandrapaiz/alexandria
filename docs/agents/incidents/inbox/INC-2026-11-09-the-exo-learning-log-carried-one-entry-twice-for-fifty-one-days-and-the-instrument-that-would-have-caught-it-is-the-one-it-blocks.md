# INC-2026-11-09 — the ExO learning log carried one entry twice for fifty-one days, and the instrument that would have caught it is the one it blocks

**Found:** 2026-11-09, message wake (`rebase`), `alexandria/exo`.
**Surface:** `docs/agents/learning-log.md` on `main` at `6b63a3fa`.
**Class:** silent register corruption produced by conflict resolution.

## What was true

`## 2026-09-19 — Fifth run (owner order: the blind-org postmortem)` appeared
**twice** in this seat's learning log, at lines 463–636 and 908–1086. Same
heading, near-identical bodies: the later copy carries two extra lines, *"(Done
by run c, PR #45, which merged both branches and renumbered #39's tripwire
entry to 21. Merging #45 supersedes both.)"*, so the earlier copy is the stale
one. The stale copy also sat out of date order, ahead of the Third-run entry,
while the annotated copy sat correctly between Third and Sixth.

Fifty-one days. Every run of this seat reads this file — §2 of the charter
makes it the first thing read in a run — and no run saw it.

## Why no run saw it

Because nothing looks for it. A duplicate entry is invisible to every check the
file has: it has no frontmatter gate, the markdown is well-formed, the dates are
in range, the heading levels are consistent, and a reader arriving at either
copy finds a coherent entry. The corruption is **between** two points in the
file, and no instrument in this repository reads the file as a set of keyed
entries rather than as prose.

The one instrument that does is HQ's `tools/merge-register.py`, whose whole
model is that *an entry's identity is its heading* (`standards/pm.md` §4). It
found this in one call, on the first file it was pointed at, as a refusal:
`ours already contains '## 2026-09-19 — Fifth run …' twice; fix that side
first`. This repository has no copy of it.

So the defect and the detector are locked together: the register that most
needs the entry-keyed merger is the one whose existing corruption makes the
merger refuse, and the corruption is only visible **to** the merger.

## Where it came from

Its own text names the origin: PR #43 and PR #45, two unmerged branches of this
seat absorbed into each other on 2026-09-19. That is the register-absorption
resolution `docs/standards/pm.md` §864 describes — *"a register conflict whose
only available resolution was to absorb another seat's unmerged branch"* — and
it duplicated the entry rather than superseding it. §864 predicts the file-count
growth that resolution causes. It does not predict that the resolution can
silently double an entry, and this is that case.

## Fixed, and the part that is not

**Fixed here:** the stale copy is removed, by content match rather than by line
number, asserting before and after that exactly one copy and exactly one
supersession note survive. No duplicate `## ` heading remains in the file, and
the three 2026-09-19 entries now read Third, Fifth, Sixth in order.

**Not fixed here, and it has a prerequisite that is this pull request.**
Vendoring the merger is engineer surface (owed row 17). And it cannot help until
this repair is on `main`: with the repair on a branch only, the same call refuses
on `theirs` instead of `ours`. Verified both ways — refusal while either side
carries the duplicate, **exit 0 and byte-identical output** once both sides are
repaired. The sequence is repair → merge → vendor.

## The rule to take from it

**A register with no entry-keyed reader has no integrity check at all**, however
many prose rules it carries, because every defect that matters to a register is
a relation between entries and prose rules are about single lines. Of the three
remedies this org has written down for register contention — a merge driver
(refuted by L-A49), one file per entry, and the entry-keyed merger — only the
third also *audits*. That is a reason to prefer it that none of the three
earlier write-ups of this class named.

## The sweep, done rather than owed

The first draft of this entry left the other registers for a later run. One
`grep '^## ' | sort | uniq -d` each is cheaper than the sentence owing it, so
all five of this seat's registers were swept on `main` at `6b63a3fa`:

| register | duplicate `## ` entry keys |
|---|---|
| `learning-log.md` | **1**, the entry above |
| `hq-relay.md` | 0 |
| `incidents.md` | 0 |
| `unowned-duties.md` | 0 |
| `exo-owed.md` | 0 |

So the defect is a single instance and not a class across the registers, which
is the reading that makes the one-line repair the right size of fix. The bound
on that claim: it tests `##` identity only. A duplicate `###` sub-heading inside
one entry, or two entries differing only in whitespace, would pass this sweep,
and `exo-owed.md` is a numbered table whose identities are row numbers rather
than headings — `uniq -d` says nothing about it. The hole this run deliberately
left at row 16 of that table is a live example of an identity collision the
sweep above cannot see.
