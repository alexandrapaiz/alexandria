## INC-2026-11-09-a-one-time-migration-keyed-to-the-first-run-after-it-has-now-been-performed-twice-on-two-unmerged-branches - a once-only step was gated on an ordinal no run can observe, so every run read itself as the first (2026-11-09, exo seat)

**What happened.** On 2026-10-24 this seat edited `prompts/pm-agent.md` §1d to
end the worst merge-contention anchor measured in the portfolio: every PM pass
had been prepending a dated section to `docs/sprints/pending.md`. The edit split
the file — one file per pass under `docs/sprints/pending/`, and the state table
in `pending.md` with exactly one writer, the ceremony run. It also prescribed a
one-time migration, in these words: "**the first ceremony run after this edit**
moves the whole file unchanged to `docs/sprints/pending/archive-to-<that run's
own UTC date>.md` and starts the state table empty." That is an ordinal, not a
condition, and **a run cannot observe its own ordinal.** It reads `main`; the
evidence that an earlier run already migrated lives on that run's branch until
the branch merges. Ceremony pull requests are the one kind the PM seat does not
self-merge. So both ceremony runs since the edit read themselves as the first,
and both performed the migration in full:

| head | branch | archive it wrote | state table it started |
| --- | --- | --- | --- |
| `abd250f2` | `alexandria-pm/2026-11-02-ceremony` (pull request 683) | `pending/archive-to-2026-10-26.md` | 58 lines |
| `20ce4f12` | `alexandria-pm/2026-11-09-message-ceremony` (pull request 863) | `pending/archive-to-2026-11-09.md` | 140 lines |

`git merge-tree --write-tree` on those two heads reports `CONFLICT (content):
docs/sprints/pending.md`. A third open pull request, head `f8230dc9` on
`alexandria-pm/2026-10-24-hook-standup` (483, opened 2026-10-24T21:24Z, 6,564
lines), is an old-regime *prepend* and conflicts with both. `tools/anchor_contention.py --fetch`
independently lists `docs/sprints/pending.md` at three open pull requests, which
is how the count was found rather than assumed.

**Why it is in this register.** This is the third instance of one shape, and the
first two are both on the surface this one was written to fix. The section's own
history records the PM seat merging twenty sibling pull requests by hand,
keeping both sides of every `pending.md` conflict. The remedy for that
contention has now reproduced it — one level up, inside the instruction that was
supposed to end it. The general shape also has prior art in this seat's own
registers: `docs/agents/unowned-duties.md` was corrected on 2026-11-01 for
reading three calendar dates as observations ("a date is not an observation"),
and this is the same error in the ordinal rather than the calendar. **An
instruction keyed to "the first run after this" is correct exactly once and
silently wrong every time after.**

**What it cost.** Sixteen days with no state table on `main`. `pending.md` has
not been written since 2026-10-24, holds 5,458 lines that §1d itself classifies
as "history and not state", and the thing the owner "must never be the one
keeping track of" has therefore had no live surface for the whole period. Two
ceremony runs' migration work is duplicated, and whichever of the two merges
second cannot merge at all. The worse cost is the one not yet paid: the step as
written moves "the whole file unchanged" into an archive **with no test of what
the file is**, so a ceremony run landing after a successful migration would
archive its predecessor's live state table and start empty again — a
destructive step with no idempotence guard.

Note what is *not* a defect here, because it was this run's first reading and it
was wrong. The per-pass half of the split looks abandoned on `main`: the newest
file under `docs/sprints/pending/` is `2026-11-02-0355-message.md`, while the PM
seat has run some twenty passes since. Checked on the branches instead, every
one of those passes wrote its own file — `2026-11-08-2330-message.md`,
`2026-11-09-0303-message.md`, `2026-11-09-0711-message.md`. The rule is being
obeyed exactly; the files are missing from `main` only because the branches
holding them have not merged. Of the **40** PM pull requests opened since
`2026-11-02T04:03Z`, **38 are open**, one merged (858, 04:37Z today) and one
closed — and 46 PM pull requests are open in total. **A surface that reads as a lapsed rule and a
surface that reads as an unmerged backlog are the same surface**, which is §2b's
all-clear problem in a new place.

**The fix.** `prompts/pm-agent.md` §1d, this run: the migration is gated on a
condition readable from `main` in one line — the first line of `pending.md`. A
dated pass heading (`## Updated <date>…`) means history, so migrate; a state
heading (`# Pending…`) means the migration is already done, so do not archive
and do not start empty. An existing `pending/archive-to-*.md` is the same signal
and is the cheaper check when the file is absent. Added with it: two migrations
in flight is a finding rather than a race to merge, and a state table resolved
keep-both is two tables, so the ceremony run that loses the race takes the newer
archive, keeps one table, and names the head it dropped. The general rule, which
is the part worth carrying: **gate a migration on a condition the next run can
observe, never on its position in a sequence it cannot see.**
