# Awaiting her word

Every copy candidate this seat has drafted and nobody has ruled on, with the
surface it is for and whether the line it replaces is still live.

**Read this before drafting anything.** It is the first file a writer run opens
after the charter, ahead of the taste register, because it answers the one
question the other registers cannot: has this surface already been written for?
On 2026-10-18 the fifth run of the day drafted repairs for the skills page and
the pricing page that the second and fourth runs of the same day had already
drafted, having read every register the charter names. None of them pointed
here, because this file did not exist.

**And that sentence was not enough, four runs later.** The ninth run of
2026-10-18 drafted four candidates for four surfaces, three of which have rows
below, one of them twenty-two days old. It had read seven registers and not
this one, because the charter's shipping step names seven and does not name
this file. So the duty is a command now and not only this paragraph:

```
python3 docs/voice/check_voice.py candidates
```

It reads the open table below against the candidate files a run's own diff
adds, and fails where a new candidate is for a surface already listed here
without naming the candidate already open on it. A run may still supersede a
draft. It may not do so without knowing the draft exists, and naming it is how
it shows that it does.

**A row leaves this file two ways.** She rules on it, in which case the verdict
and her words go into the current file in `docs/voice/preferences/` and the row
moves to the closed list at the bottom. Or the frontend seat sets it and the
live line changes, in which case the row says so with the date. A row nobody
has touched does not quietly expire, which is the whole point: the oldest row
below has been open for twenty-two days and nothing in the org knew that until
a command was written to look.

## Open, newest first

**Re-confirmed 2026-10-23 by command, writer run 42.** Every row below is
still open and every defective line is still live. `check_voice.py reading`
reports the same 4 failures on the same 4 lines as on 2026-10-18, and
`check_voice.py claims` reports 17 unhedged claims live right now. Nothing in
this table has been ruled on or set in five days, and the oldest row is
twenty-seven days old. The re-confirmation is recorded here rather than in the
last column of each row, because what changed is the date and not the reading.

**Widened 2026-10-23 by writer run 44, and the count went up rather than
down.** `reading` was reading 61 surfaces and none of them was the archive, so
it reported 4 failures. It now reads 63 and reports 5. The new row is the top
one and it is the oldest defect in this table by four days, which is the
argument for the row rather than against it: the line has been live for
twenty-eight days and was never drafted, because nothing in the repository
could see it. A table of open rows is only as honest as the scope of the
command that re-confirms it.


**New surface 2026-10-24, writer run 45.** The desk is the eleventh row and
the first one that is not public copy. It is here because the test this table
applies is whether a defective line is live, and the owner's own console is the
surface where a defective line costs the most per reader. Its defect is a
number rather than a sentence, so `check_voice.py ledger` is what re-confirms
it rather than a reading.

**Re-confirmed 2026-10-25 by command, writer run 50, and one number moved the
wrong way.** `check_voice.py reading` now reports 4 failures rather than 5,
and the one that left is the archive masthead in the closed table below, set by
the frontend seat and verified on `main`. So no row above was repaired, one was
completed by another seat, and the rest are untouched at thirty days for the
oldest. `check_voice.py claims` reports 23 unhedged claims live right now
against 17 on 2026-10-23, which is six more than a run that drafted nothing for
these surfaces can account for. The delta is not diagnosed here, because this
run produced no copy and `docs/voice/value.md` still has no recorded approval,
which is the precondition the charter puts ahead of drafting. The same command
reports 9 cited files that no longer carry their claim and 5 drifted line
numbers, and those belong to `docs/agents/quality-claims.md` and its owner
rather than to this table.

**Re-confirmed 2026-10-26 by command, writer run 51, and one number moved
because a gate was repaired rather than because a page changed.**
`check_voice.py reading` reports the same 4 failures on the same 4 lines as on
2026-10-25, so no row below was repaired and the oldest is thirty-one days.
`check_voice.py claims` reports 24 against 23 yesterday, and the one that moved
is this run's own repair: the row for "the library grows every day" has read
`contradicted` since 2026-10-11 and the gate was resolving it to `held`, because
its state cell records what it moved from and `held` was first in the list the
gate searched. So `site/app/page.jsx:33` was printing a sentence the register
calls false while this seat's instrument printed `ok` beside it. That line is
not added to the table below, because the row for that same paragraph is
already open as `claim-repairs-2026-10-18.md` and the charter's precondition
for drafting is unmet: `docs/voice/value.md` still has no recorded approval.
The delta run 50 could not account for is also answered and it was not the
copy. The register went from 11 rows to 13 on 2026-10-24, and the current gate
run against the tree of 2026-10-23 returns 17, so neither the gate nor the
surfaces moved.

**New surface 2026-10-26, writer run 53, and it is the first row here that
arrived as a hand-off rather than as this seat's own finding.** The frontend
seat's shelf audit of 2026-10-24 found the words half of a shelving defect,
left it as a proposal in `docs/ideas.md` because naming a shelf is not its
lane, and the PM relayed it to this seat on the board. So the row below is
owed to two other seats and not only to her. Its candidate carries nine
captions rather than the two the proposal asked for, and the reason is a
count. Not one of the seven captions live on that page contains a finite
verb, and her ruling of 2026-09-29 forbids fragments. The seven predate the
ruling by eleven days and no owner has ruled on one of them.

**Missing row added 2026-10-26, writer run 58, and it was written nine hours
late by the gate that exists to ask for it.** `check_voice.py candidates`
failed a candidate only where the surface it drafted for was already held by
another candidate. A candidate for a surface this register had never held
registered nothing and passed, and the pass line read the same as it reads for
a run that did the bookkeeping right. So run 57 ruled on the live `2026-W42`
page, wrote the exact words, raised one line for her, and reached `main` with
no row anywhere. The regex that reads a surface out of a candidate was widened
on an earlier run precisely so an issue page would be visible here, which fixed
what the gate could see and left untouched what it would say about it. The
floor shipped in this run's diff and the row below is the row it now demands.

**Two rows confirmed against their sources 2026-10-26, writer run 59, and the
clock in one of them became readable.** The PM answered this seat's W42 ruling
on the board at 20:45Z: agreed with the pull, merged it, posted the
correction-notice question to her as a formal ask, and did not dispatch the
frontend seat because that seat's own pull request is still open. Both halves
were read at their sources rather than taken from the note. The ask is board
message `065eda95-92e7-4f94-8625-906c10691b81`, named in the PM's #609, and the
live `2026-W42` page still serves the pulled section, re-read at 21:04Z by
`check_voice.py provenance --live` on the same two findings. What changed in the
rows is therefore the owing rather than the defect: the surface row now says
which seat owes the diff and what it waits behind, and the question row carries
`deadline 2026-10-28T20:44Z` in a fixed form. Run 58 wrote that clock in prose
and prose is the thing no command can read, which is the defect this register
keeps recording about itself. `check_voice.py deadlines` reads the token now and
fails both ways: a row that argues a silence rule and names no deadline, and a
deadline that has passed with the row still open.

**Re-confirmed 2026-10-27 by command, writer run 60, and nothing in this table
moved.** `check_voice.py reading` reports the same 4 failures on the same 4
lines as on 2026-10-26 and `claims` reports the same 24 unhedged claims live
right now, so no row below was repaired and the oldest is thirty-two days.
`provenance --live` re-read the `2026-W42` row's defect at 00:12Z on 2026-10-27
and found the same two findings at lines 47 and 49, which is the fourth live
confirmation and the first one on the day after the ruling. The row's reader
should now expect the live line to outlast the ruling by two days rather than
one, because the frontend seat's #559 is still open. The question row's clock
is unexpired: `deadlines` reads `2026-10-28T20:44Z` against a fixed
`2026-10-27T00:05Z` and says so. This run adds no candidate, because
`docs/voice/value.md` still carries no recorded approval.

| Surface | Candidate | Drafted | Is the defective line still live? |
|---|---|---|---|
| `site/content/issues/2026-W42.md`, the overturn section at lines 43 to 53, the lead's third sentence and the lead's count | `w42-correction-2026-10-26.md`, whose corrected body is `2026-W42-corrected.md` | 2026-10-26, run 57 | Yes. Read live at 20:49Z on 2026-10-26, after the ruling merged: the heading "Hidden reasoning can be encrypted, not merely hidden" still serves, and the research seat scored that section three wrong out of three against the abstracts the issue itself cites. The ruling is to pull the section rather than reword it. Setting it is the frontend seat's diff, and the file does not exist under `site/content/issues/` yet, so the correction lands as a new file that overrides the stored row. Owed to that seat and not dispatched: the PM is holding it until the frontend seat's open #559 clears, said on the board at 20:45Z on 2026-10-26, so the row's reader should expect the live line to outlast the ruling by a day or more |
| `site/lib/skill-shelves.js`, the shelf names and the nine captions | `shelf-names-2026-10-26.md` | 2026-10-26, run 53 | Yes. Four of nine skills stand on the catch-all shelf under a caption written when at most one could land there, and all seven live captions are fragments against her 2026-09-29 ruling. Two shelves do not exist yet |
| `site/app/desk/page.jsx`, the verdict queue | `desk-verdict-queue-2026-10-24.md` | 2026-10-24, run 45 | Yes. The queue renders 524 rows oldest first, so the newest entry on it is the compute outage of 2026-10-23 and a reader reaches it last. The count beside the heading is also wrong by one against `tools/ledger.py --census`, which `check_voice.py ledger` now fails on. Four lines and a one-character anchor, in one diff |
| `site/app/mission/page.jsx`, third paragraph | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. Three unheld claims in one sentence, confirmed by `check_voice.py claims` on 2026-10-18 |
| `site/app/mission/page.jsx`, second paragraph | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "every finding is linked", contradicted on "every" |
| `site/app/page.jsx`, the paragraph under the hero | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "replaced when newer work overturns it", which reports rather than replaces |
| `site/app/graph/page.jsx`, the intro | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. The colon-led construction and the universal reading |
| `site/app/terms/page.jsx`, what the service is | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "The library reads AI research", confirmed by `check_voice.py reading` |
| `site/app/llms.txt/route.js`, the whole body | `llms-txt-2026-10-18.md` | 2026-10-18, run 39 | Yes. Law 15 three times now, two registered claims unhedged, and a launch date five days past. The third instance is the pronoun subject at line 13, which no command saw until `reading` was widened on run 41 |
| `site/app/pricing/page.jsx`, the free column and the intro | `pricing-claims-2026-10-18.md` | 2026-10-18, fourth run | Yes. "The complete archive" over an archive with a hole in it, live for thirty days |
| `site/app/skills/page.jsx` intro, the install block, the nine catalogue rows | `skills-copy-2026-10-18.md` | 2026-10-18, second run | Yes for the intro. The install block is the engineer's surface and moved with PR #339 |
| `site/app/page.jsx:44`, the metric line | `home-metric-line-2026-09-26.md` | 2026-09-26, run 15 | Yes, twenty-two days, confirmed by `check_voice.py reading`. Recorded as an incident the same day this file was created |

## Questions awaiting her word, which no wording can answer

| Question | Where it is argued | Asked |
|---|---|---|
| Are the skill files the paid product, or the free distribution that sells something else? The repository is public and all nine are in it, so the entitlement gate guards a door in a wall with no other sides | `skills-copy-2026-10-18.md`, surface 3 | 2026-10-18 |
| Does a paid tier keep a bullet for a machine that does not exist, hedged, or lose the bullet? | `claim-repairs-2026-10-18.md`, finding 8 | 2026-10-18 |
| Is `docs/voice/value.md` the target still owed an approval, or stale against the five pages she approved on 2026-09-29? | `value.md`, the note of 2026-09-30 | 2026-09-30 |
| Does the corrected `2026-W42` page carry a notice saying a section was removed and why, on that page only? Recommended yes, quoted in full in the candidate, and canon law 7 is the ground it stands on rather than an exception to her ban: that law's first clause asks for a limitation that materially affects the day's content in one plain sentence, and its second bans narrating the method | `w42-correction-2026-10-26.md`, the one line that needs her word, with the insertion point and the form settled in its sequencing section | 2026-10-26. Posted to her as a formal ask by the PM, read on the board rather than taken on report: board message `065eda95-92e7-4f94-8625-906c10691b81`, named in #609. deadline 2026-10-28T20:44Z, after which the recommendation is in force under the company standard's silence rule |

## Closed

| Surface | Candidate | How it closed |
|---|---|---|
| Home, library, skills, graph, mission | `site-copy-2026-09-19.md` and the rounds after it | Superseded by her approvals of 2026-09-29, "good. i like this.", recorded in `docs/voice/taste.md`. The live pages are the positive examples |
| `site/content/issues/2026-W39.md`, line 3 | `archive-masthead-2026-10-23.md` | Set, and on `main`. Verified by writer run 49: line 3 of the file on `origin/main` matches the `MASTHEAD` constant in `pipeline/weekly.py` character for character, and `check_voice.py reading` no longer reports the archive. The open row said moving it was this seat's call, so this is that call |

## What this file is honestly worth

It is a register, and the lesson this seat keeps writing down is that recording
is not enforcing. Nothing fires when a row here goes stale. Two of the nine
statuses above are checkable by command today, because
`docs/voice/check_voice.py claims` and `check_voice.py reading` read the live
surfaces, and the rest are a seat's reading of a page on a date.

So the duty is the smallest one that could work: a writer run opens this file,
and a candidate for a surface already listed here either builds on that
candidate or says why it supersedes it. The alternative is what happened on
2026-10-18, which is three candidates for two surfaces in one day and no way
for any of them to know about the others, and then a fourth candidate four
runs after this file was written to prevent exactly that. The duty is now a
command over the run's own diff, which is the only version of it that has ever
held. What is still a seat's reading on a date is the last column.
