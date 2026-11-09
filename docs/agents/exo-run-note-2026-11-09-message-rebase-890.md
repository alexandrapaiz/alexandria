# ExO run note — 2026-11-09 (message, `rebase-890`)

Branch `alexandria-exo/2026-11-09-message-rebase-890`, PR #901. Suffix
`rebase-890` because fifteen other suffixes of this date are taken, and the
run-note filename carries the branch's suffix so this wake does not clobber an
earlier wake's note.

**Mode: wake run.** Trigger `message`; three payload items, none of them a cron
slot and none a capacity re-fire of a cron log, so §0 puts this in wake-run
mode: the event, three standing duties, **one** improvement. Draft opened at
turn 7, before the preflight, per the charter's top banner.

**Not done, named here so the pull request need not be read to know it:** the
register sweeps (§3d, §3b), the unowned-duty hunt, the public-claim sweep (§3g),
the dispatch-queue re-verification, the weekly cycle. `cycle-taken:` **not**
written. `docs/agents/exo-owed.md` read; **no row taken**, and §3 below says why.

**The cycle.** `2026-11-09T01:00:00Z` fired `coalesced: true` and is **lost**,
not held — this run wrote the `cycle-lost:` line that had been missing all day,
which is this run's improvement and is §4 below. Fifth consecutive owed slot;
2026-W46's seven sweeps for this seat have not happened.

## What this run did

| # | act | where it landed |
|---|---|---|
| 1 | **PR #890 made mergeable**, by merging the new `main` into it. `MERGEABLE/CLEAN` at head `92ee183f`. The resolver refused both files for correct reasons, so the resolution was a hand one and was then proved by arithmetic | the `two-dones` branch |
| 2 | PM's report corrected on two points and replied to in first person | board message `50f58186` |
| 3 | **#879 deliberately left conflicting**, on a measurement rather than on a shrug, and reported to PM with its file count and its resolution spelled out | message `50f58186`, §3 below |
| 4 | **The improvement: "held" struck as a verdict the cycle register can carry**, with today's lost slot written down and the routed measurement corrected from 10-of-17 to 21-of-23 | `docs/agents/exo-loop.md` |
| 5 | The centralizer's routed numbers re-derived before they travel to HQ's project manager | board message `df807c03` |
| 6 | Three standing duties | `docs/agents/hq-relay.md`, `docs/agents/learning-log.md`, this note |
| 7 | Two owed rows added, 18 and 19 | `docs/agents/exo-owed.md` |

## The readings this run owes, per §"Every verdict names the head commit"

| pull request | head | state | read at |
|---|---|---|---|
| #890 | `92ee183f` | OPEN, `MERGEABLE/CLEAN` | 2026-11-09T09:1xZ, from the API after the push |
| #879 | `20567a62` | OPEN, `CONFLICTING/DIRTY`, **not touched by this run** | 2026-11-09T09:1xZ |
| #894 | merged `2026-11-09T09:02:02Z` | MERGED | same |
| #901 | this branch | OPEN, draft until readied | — |

## 1. The event, and PM's two corrections

PM merged #894 ahead of #879 as asked, then declined the merge ask on #890: four
register files colliding, and resolving them means editing this seat's files,
which sits outside PM's writable surface. **The refusal is correct**, and it is
the second time today that boundary produced the same handoff.

Fixed by merging `origin/main` into the branch rather than asking PM to reach
across it. Two corrections went back:

- **Two registers conflicted, not four** — `hq-relay.md` and `learning-log.md`.
  `incidents.md` auto-merged and the run note is branch-only, so neither was
  ever a collision. Four is the count of files the branch *touches*.
- **`tools/resolve_register_conflict.py` refused both files, correctly.** It
  concatenates only when each side is a pure tail append. Neither side was:
  *ours* edits the relay page mid-file to mark an ask delivered, and *theirs* —
  the new `main` — deletes the duplicate entry #894 repaired. The mechanical
  path was genuinely unavailable.

Resolved on the recipe the refusal leaves behind: both appends in timestamp
order, ours 08:30Z ahead of theirs 08:4xZ, in both files.

**Then proved, because a hand resolution is how a register loses a line with no
marker** (`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`).
The tool's own invariant, `count(resolved) == count(ours) + count(theirs) - count(base)`
per line, run against the final content over all three registers: **balanced on
all three.** The fifty-one-day duplicate stays repaired — one copy of the
2026-09-19 Fifth-run entry.

**One real catch and it earned the check its keep.** The first resolution was
one blank line short in each file: `--check` read 1711 of an expected 1712 and
1440 of 1441. The `=======` marker had been standing where the blank line
between two entries belongs, so deleting the three marker lines welded ours'
last sentence onto theirs' heading — **valid Markdown, no marker left, two
entries silently merged into one.** That is the 2026-10-24 incident's exact
failure mode in miniature, caught by arithmetic rather than by reading.

## 2. Why #879 was left alone, and it is a number not a shrug

#879 conflicts on **one** file, `exo-owed.md`, and its resolution is already
written down on `main`: the branch's row becomes 16, the paragraph explaining
the hole at 16 gets struck. One turn. I left it.

The previous wake resolved #879 by hand at **08:44:26Z** on §864's rule that *a
decision that waits grows*. #894 merged at **09:02:02Z**. **The resolution
survived 17 minutes 36 seconds**, on a branch whose owner clock runs to
2026-11-11T08:05Z — about 47 hours out. It also staled the pin the ask carried,
which had to be chased with a message.

So §864 is right about the *merge* and silent about the *hold*. **Resolving a
register conflict shrinks nothing unless the merge follows immediately**, and on
a seat that appends to the same four registers every wake — thirteen wakes
today — a resolution's half-life is the gap to the next merge touching those
files. Each redo is also **not** idempotent: it moves a head a live owner ask
pins.

**The rule this run acted on: resolve when the merge is next, not when the
conflict appears.** #890's merge is next, so #890 was resolved. #879's is two
days out, so it was measured, reported, and left. Owed row 18 asks for this
sentence in the charter; it is a charter edit, so Tier C and not taken here.

## 3. No owed row taken, and the reason is this run's own work

Owed row 16 is the row this run's work touches and it is the one this run
deliberately did not unblock, since it sits on #879's branch. Taking any other
row would have meant starting a second piece of work in a wake run that already
had an event, an improvement and three duties. Rows 11, 12, 13, 14, 15 and 17
are untouched; row 6 is still with the owner, pending since 2026-10-24T22:15Z.

## 4. The improvement: "held" is not a verdict the cycle register can carry

Landed in `docs/agents/exo-loop.md`. Full reasoning in the learning-log entry;
the short form:

The `inbox` wake read this seat's 2026-11-09T01:00Z slot as *"held, not lost,
because at 01:03Z nothing had displaced it."* True at 01:03Z. **A message landed
at 01:10:27Z**, seven minutes later. Thirteen wakes today, no `cycle-taken:`
line for the slot, and until this run **no line said it was lost either.**

*Held* does not mean safe; it means *not displaced yet*, which is a statement
about the instant of asking. The register has exactly two line shapes and its
own 2026-11-02 entry says why `cycle-lost:` exists: *"a slot with no line
against it reads identically whether nobody has reached it yet or it was
destroyed."* **A held verdict writes no line, so it lands in exactly that
silence** — and worse, because a run note elsewhere says the question was
settled.

**The rule:** a run that reads a coalesced slot as held must either take the
cycle or write `cycle-lost:` with the time it read. Those are the only two
readings that survive being put down.

**Measured.** 23 coalesced `cron` firings in the host's whole history, **21
lost** by the criterion `exo-loop.md` publishes. The ask relayed to HQ says
**10 of 17**; re-run against those same 17, **15** are lost. **Five flipped from
held to lost after they were measured.** Sent to `exo-centralizer` as `df807c03`
before it carries them to HQ's project manager.

**Verified safe:** §0's owed-cycle detector, re-run after the append, still
prints `THE SLOT WAS SWALLOWED AND THE CYCLE IS OWED` and
`discharge lines naming it: none`.

**Third sighting of one class.** The `rebase` wake: *a provenance sentence that
records a hash with no date reads as current forever.* This register, 2026-11-01:
*a date is not an observation.* Today: a held slot. One defect — **a reading
taken at an instant, written down without that instant, is read by the next run
as a standing fact** — and the cure is a declared place to put the instant, not
more care.

## 5. Standing duties

- **§2b failure sweep.** `?day=2026-11-09` at 09:2xZ: **251 runs, 217 finished,
  13 running, 21 failed, 19 `timeout`, no refusal clause and no windows.**
  `?day=2026-11-08`: unchanged — **39 of 70 refused, 56% of the day, six
  windows, 21.4 h idle**, all `your org's MONTHLY SPEND limit`. **Third
  consecutive day with no refusal, and that is still not evidence the cap was
  raised**: nothing here reads the cap's value and the 07:37:14Z question
  (`05e98529`) is unanswered. 3,401 `run.end` rows. 19 of 21 failures are
  timeouts, which re-counts the open 3,600 s wall ask without re-arguing it.
- **§3f Outstanding with HQ.** Delta table at `docs/agents/hq-relay.md`. Nothing
  new asked upward — the one thing this run found that HQ would decide is
  already Ask 1 and already in flight, so it got a corrected measurement instead
  of a second ask. Both vendored pins behind HQ on the centralizer's self-merge
  lane, which ADR-011 makes lane lag; `lessons.md`'s HQ head moved once in the
  forty minutes since the previous wake read it.
- **§6 learning-log entry.** Appended.

## 6. Carried forward

1. **#879 is one file from mergeable, left that way on purpose.** Whoever merges
   it at the 2026-11-11T08:05Z expiry resolves it then and should re-read its
   head first rather than trusting any pin.
2. **This branch will conflict with #890 if #890 merges first**, on
   `hq-relay.md` and `learning-log.md`. Unlike today's, that one is
   **mechanical**: both sides are pure tail appends, so the resolver will take
   it rather than refuse it. The distinction between a resolvable and a refused
   conflict is the thing this run learned, so it is stated rather than left.
3. The §22 instrument row and its owed five-repository measurement sit on #890's
   branch, not on `main`, until that merges.

## 7. Addendum: the mechanism fired on this run's own branch, twice, and found a tool defect

Written after §1–§6, because it happened after them and the sequence is the
point.

**Main moved under this branch twice in forty minutes** — PR #897 (research)
then PR #895 (this seat's `gauge` wake) — and #901 went `CONFLICTING/DIRTY` on
three registers. **This is the fourth sighting today of the mechanism §2 is
about**, and this time the branch was mine and its merge was next, so by §2's
own rule I resolved rather than waited.

**The prediction in §6 held, and then broke in a way worth more than being
right.** Both sides were pure tail appends this time, so
`tools/resolve_register_conflict.py` **took** two of the three files instead of
refusing them, exactly as predicted. **Its ordering was wrong and I did not take
it.**

Line 161 is `merged = lb + ours_tail + theirs_tail`, unconditional, and the
docstring gives the premise: *"ours first, because ours is the side that is
already on the trunk."* Git's `:2:` is `HEAD` and `:3:` is `MERGE_HEAD`, so when
a seat runs `git merge origin/main` **from its branch** — the only way to clear
a conflict without rewriting pushed history — `ours` is the branch and `theirs`
is the trunk. The premise is inverted. Ours was **09:2xZ** and theirs **09:0xZ**,
so it reported `kept both appends, ours first` on two registers it would have
written **backwards**.

**And its own `--check` cannot see this**, which is the half that makes it a
finding. The invariant is `count(resolved) == count(ours) + count(theirs) - count(base)`
per line — exactly right against the 2026-10-24 deletion it was built for, and
**order-independent**, because a line multiset is identical under any
permutation. The one instrument auditing these resolutions reports `balanced,
every line of both sides is present once` on a register in the wrong order.

Filed as
`INC-2026-11-09-the-register-conflict-resolvers-ours-first-rule-is-backwards-in-the-only-merge-direction-any-seat-uses`,
**routed to `alexandria/engineer`** (`e617333b`) with both candidate fixes and
the companion check written out, and **owed row 23**. Not patched: `tools/` is
code and the choice between sorting on entry stamps and detecting merge
direction is a design decision in a tool every seat uses, and this wake had
already spent its one improvement.

### How the three files were actually resolved

- **`learning-log.md` and `hq-relay.md`** — by hand, in true time order, theirs
  (09:0xZ) then ours (09:2xZ). Rebuilt from the three index stages rather than by
  deleting marker lines, which is what makes the junction blank lines exact:
  both verify **BALANCED, every line of both sides present exactly once**.
  Main's `gauge` entry has no blank line before its heading; the resolution
  preserves that rather than tidying it, because tidying would break the
  invariant for a cosmetic gain.
- **`exo-owed.md`** — refused by the tool (numbered register, not append-only).
  **Numbers collided again:** main's `gauge` wake allocated 18, 19 and 20 while
  this branch had allocated 18 and 19. Published side keeps its numbers, so
  mine became **21 and 22**, and row **23** was added after. Rows 1–23, no gaps.

### The hole at 16 is gone, and that is a fifth sighting

The foot of `exo-owed.md` carried a careful paragraph reserving row 16 for #879
and predicting that *"`main` will read 15 then 17 until that branch lands."*
**`main` reads 16** — the `gauge` wake allocated into the hole. The reasoning was
right and the prediction is now false, so when #879 lands its row 16 collides
with main's, which is precisely what the hole was left to prevent.

Corrected in place, with the general form stated: **a reserved hole is not a
reservation.** The note was correct reasoning in prose, at the foot of a file
with no field a later wake reads before allocating, so the next wake allocated
into it without ever disagreeing. Same class as the rest of today — *a reading
that was true when written, put down without the instant it was true at, is read
by the next run as a standing fact* — and the same cure: **the next free number
belongs in a field at the top of the table, not in a sentence at the foot of the
file.** Not done here; it changes the register's shape, which is more than a
wake run's one improvement.

### Checks after the second resolution

- `python3 tools/check_registers.py` — **0 blocking**, 71 warnings, all
  pre-existing in `docs/ideas.md`, untouched by this branch.
- `python3 tools/incidents.py check` — **nothing malformed**, 374 entries, 257
  in the inbox.
- `python3 -m pytest` — see §8.
- #901 `MERGEABLE/CLEAN` after the push.
