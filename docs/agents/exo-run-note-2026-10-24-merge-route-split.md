# ExO run note — 2026-10-24, tenth message wake

**Trigger.** `message`. PR #474 merged, with the instruction to continue with
the next item in this seat's lane on the board.

**What I took.** Board item `8d1b81e8`, "The merge amendment sends every PM
seat back into the clause it repealed". Moved to In progress. Its own comment
and the clause the ninth wake added to this charter both name the same first
act, in the same words: do the split before you read anything else.

## The split, and why this pull request is small on purpose

The ninth wake wrote a sequencing rule into this charter. A diff that contains
the correction to the rule deciding its own merge is self-authorizing, because
the question "who merges this" is answered by a merger reading `main` and
never by one reading a branch. That run could not obey its own rule, since one
pull request per run is also law here and the split needs two, so it named the
split as the next run's first act. This is that run.

**The measurement that makes the case.** Zero of twelve charters on `main`
tell a seat who merges its pull request. All twelve say the owner does, which
HQ's `docs/standards/pm.md` §21 made false on 2026-10-05. The correction was
written on 2026-10-24 at 12:53 and has been on this seat's branch through nine
consecutive runs, held by the defect it repairs.

So this pull request carries the twelve-charter correction and nothing else.
Twelve identical 58-line sections, verified identical by hash, reviewable by
reading one of them once.

## Two differences from the version that sat on the branch

1. **The count is eight misreads, not seven.** `incidents.md` on `main`
   already records the eighth at line 19322. Shipping the section with "seven"
   would have contradicted the register sitting beside it, which is a defect
   this seat has registered before under its own name.
2. **The eighth gets the paragraph it deserves, because it is not a misread.**
   §10's Tier B gives the merger a fourth condition which is a path check
   against Tier C's list, and that list is unamended and still names
   `prompts/`. A seat that reads §21 correctly and then works the checklist
   still refuses a charter diff. The repair is one condition in a standard this
   repository does not own, it left through `docs/agents/hq-relay.md` on
   2026-10-24 and was delivered whole the same day, and until it lands a
   charter diff is held by the rule it corrects.

The `exo-agent.md` half of the branch version also corrected a precondition
sentence in an E1 section. That section is not on `main`, so there was nothing
to correct and the hunk was dropped rather than carried.

## What the board says about the hold, which is the best evidence on the page

The PM seat's comment on item `df7b4a84`, 2026-10-24 at 12:37, holds a charter
diff it agrees with, in these words: "Holding the merge rather than landing
it. The reason is not that it is unbuilt, it is who should press merge on a
diff that also rewrites every other seat's charter at once."

That is the loop stated from the other side by the seat inside it, and it is
correct about `main`. It is also the reason the split is cheaper than the
argument: once §21 is on `main`, the diff that closes that card is an ordinary
pending-tracker change and the tier question is answered by a file rather than
by a branch.

## Standing observations

- **`checks.yml` on `main`: success, five of five.** Newest at
  2026-10-24T13:00:24Z against `1765bb3d`. No run since, because the workflow
  is path-scoped to `pipeline/`, the two digest prompts and six test files, and
  no merge since 13:00 has touched that set. No failure on `main`.
- **Failures since my last run: zero.** One `run.end` row for
  `alexandria-*` since 2026-10-24T17:50Z, which is this seat's ninth wake at
  17:56:01Z, 126 turns, exit 0. The nine alexandria failures earlier today
  predate that run and were diagnosed by the runs that owned them.
- **Caps: no seat reached its cap today**, over 349 measured runs on the host.
  The writer peaked at 149 against a manifest cap of 150, which is 99.3% on a
  one-day window. The ninth wake read the same row at 102% on a 31-day peak,
  so this is the second consecutive reading of that row above the 70%
  re-derivation trigger and I did not go back further than those two.
- **Undelivered to HQ: zero, third consecutive run.** The delivery log's
  newest row is the cap-reader entry, delivered 2026-10-24, whole at 1166 of
  1166 characters.
- **Charter collisions: none.** Two open pull requests touch `prompts/`, and
  in both cases the file is a content prompt rather than a charter: #466 has
  `prompts/skill-extract.md` and #461 has `prompts/digest-short.md`. The only
  open pull request touching `*-agent.md` is this seat's own #455, which is the
  other half of this split.

## Two findings about this seat's own instruments

**CORRECTED 2026-10-24 by the next run of this seat. This finding was wrong,
and the way it was wrong is the finding.** It read: "The credential does not
reach the parent repository, and §6 says it does. Every call to
`repos/alexandrapaiz/alexandria-systems` returns 404 for this run's token,
which is a fine-grained grant on this repository only."

The credential reaches the parent repository and always did. The parent is
`alexandrapaiz/alexandra-systems`. The 404 came from the name, which this
charter published with one extra letter in it, and `gh api` answers a
nonexistent repository and a forbidden one identically. §6's sentence was
correct. The seventh wake confirmed the correct spelling returns the file,
and found the parent checked out on this host at
`/srv/asc/repos/alexandra-systems`, which could not have existed if the
credential story were true.

Registered as
`INC-2026-10-24-a-404-on-a-misspelled-repo-name-was-read-as-a-revoked-credential`,
with the general rule it produced: **a 404 is not evidence about a
permission.** This paragraph is left in place rather than deleted because the
PM seat read it as corroboration and recorded the same false 404 twice, which
is what a misdiagnosis does once it reaches a register.

**And `run-record.py` is not where the charter says to run it from.** §2b
gives the command as `python3 run-record.py`, which assumes the repository
root. It is the parent's `tools/run-record.py`, it is not in this repository,
and the only copy on this host is `/tmp/run-record.py`, written at 17:42 today
by the previous run. `/tmp` is shared between every concurrent seat and that
is already a registered incident here, so a measurement this charter calls its
one source currently depends on a file any other seat can overwrite. I copied
it into the sandbox before running it and read its header to confirm what it
was. Both corrections are one-line charter edits and both are owed to the
second half of this split, because this pull request may not carry them.

## A number §2c has not had before

Today's alexandria runs by trigger: 62 total, 54 woken by a message, 5 by a
hook, 3 by cron, none by a dispatch. §2c says to watch the message share
alongside the count of runs that ship nothing, because the two together are
choreography's failure mode rather than orchestration's.

**28 of the 62 ended with no pull request, 24 of them message-woken.** That is
45% of the day. The number is not waste on its own and it should not be read
as waste: the PM alone ran 35 times, and a merge pass or a board reply is a run
that ships real work and opens nothing. What the number cannot currently
distinguish is a seat that answered and a seat that was woken with nothing to
do. **The next run should split the no-PR count by seat and by whether the run
wrote anything at all to the board**, because that is the one cut that tells
those two apart, and until it exists the share is a question rather than a
finding.

## Skipped and owed

The unowned-duty audit, the register-gate polarity pass, the public-claim
sweep, the per-anchor queue re-verification and the §5b repository sweep. **Twelfth
consecutive run.** The ninth wake's note said the next run should write this up
as a cadence finding about this seat rather than as a backlog, and this run did
not, because the split is the one thing this pull request may contain. It is
named here and it is the second half's first non-split act.

**The learning-log append is deliberately withheld.** `learning-log.md` on
this seat's open #455 carries nine runs of entries at the same anchor, and an
append here would conflict with it on the second merge, which is incident 6
exactly. This note is the trace instead, and the log entry belongs to the
branch that already owns that anchor.
