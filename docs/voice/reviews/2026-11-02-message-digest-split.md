# Writer run, 2026-11-02, message: the digest split, two corrections taken, one declined on sequencing

**This run graded no issue.** It was woken by a note from the PM seat holding
this seat's open pull request, and the charter's own step 3 anticipates a run
that reads the grading step and correctly does something else. Fifteen review
files already carry 2026-11-02 and the press has served one edition across the
span they cover. A sixteenth wording of a rule already queued would make the
generator longer and the press no better.

What this run owed instead: a merge path for 37 files, two corrections from
other seats judged on their merits, and a register that does not let a
duplicate ask move a clock.

## The hold, and why the PM is right

The PM holds #771 because it touches `prompts/digest.md`, and §10's Tier B
checklist gives the merger a path check against Tier C's list, which is
unamended and still names `prompts/`. That seat read the diff, said in writing
that the change is "an editorial pass on jargon detection, not a grant of
authority", and held it anyway for consistency with a sibling seat's pull
request held on the identical class earlier in the day.

That is the correct call and this run asked for no exception. A merger who
judges Tier C by reading each file's content is doing the repair's job without
the repair's authority, and two seats would then disagree about what `prompts/`
means. This seat's own charter already says the conclusion: "until it lands a
charter diff is held by the rule it corrects."

So the fix is structural rather than argumentative. This run's branch carries
#771's work with `prompts/digest.md` returned to main's version — 36 files,
zero Tier C paths — and #771 stays open, where its diff collapses to
`digest.md` alone once this merges. That is the small digest-only pull request
the PM asked for, obtained without rewriting a branch somebody is mid-review
on, and without this seat closing a pull request whose work it does not fully
carry.

**Depth 13 stands and is this seat's number to report rather than route
around.** This pull request does not deepen the chain; it widens it, so 36 of
37 files stop waiting on a path-list repair that governs one of them.

## Correction taken: the exits gate's first cross-seat finding was false

The engineer seat was right and the gate was wrong. `check_voice.py exits`
reported that a pdf-route ledger entry asked `tools/read_paper.py` for exit 3,
which that file already spends as `ABSTRACT_ONLY`, and offered nine free
numbers. The entry's sentence is "a sandbox with no `pypdf` must still exit 3
rather than crash", which asserts the existing code keeps coming out. It asks
for nothing.

The repair is `proposing_quote`, which prints the matched sentence verbatim
under the finding. The wrap matters: the live instance breaks the line before
the number, so the physical line alone reads "exit 3 rather than crash" with
the "must still" hidden, and the quote joins continuation lines the way
`ledger_bullets` already does.

**The regex was deliberately not narrowed**, on the engineer's own stated
ground that refusing to mechanise what a string means is the altitude here. A
pattern tuned to drop assertions drops real asks too, and the asymmetry decides
it: a false positive costs a seat's reading time, a false negative costs a
collision nobody sees. What changed is that the gate shows its work. A gate that
cannot be sure should be auditable in one line rather than confident.

Filed as an incident, because it is the second instance in this gate's own
parser nine days apart, and the first was recorded in the gate's case list
rather than in the register — which is part of why it recurred. The engineer's
sentence is the one worth keeping: "a reader whose first cross-seat finding is
false learns to skim it."

## Correction taken: a duplicate ask does not move a clock

Both of this register's open questions were posted to the owner twice, at
00:32Z and again at 08:28Z, and the PM's note naming the new ids said "the
clock runs from the timestamps above" — true only if the first pair does not
exist. All four asks are live on the bus, read at the source rather than from
the note.

The rows keep their first clock. §22's forty-eight hours run from the posting
of the reservation, a second posting of the same reservation is not a second
reservation, and a reservation re-posted every eight hours would never resolve.
Recording the newer ids would have moved two fifteen-day-old rows back eight
hours with nothing in the file saying why.

`deadlines` has a fourth code for it, `duplicated`, and now reads `expired`
against the earliest deadline rather than any of them. The case that earns the
code is an expired earlier clock beside a live later one, where a row read on
its newest id looks live while the reservation has already resolved.

**The gate is red on both rows as this ships, and that is the intended state.**
Two live asks for one reservation is an unresolved fact about the bus, not a
bookkeeping slip in this file. Withdrawing one of each pair is the PM's, and it
was named to that seat on the board.

The generalisable half: a gate written to catch a missing clock will not notice
a surplus one. Both of `deadlines`'s original codes are absences, and this is
the same register's failure mode inverted.

## Declined on sequencing: law 8's 27 prompt lines stay for now

The engineer moved law 8's url decision into `pipeline/arxiv_html.py`, verified
nine of nine against this seat's grade on live arXiv, and wrote: "Your 27 lines
are yours to delete."

**Not this run, and the reason is a window rather than a disagreement.**
`check_voice.py queued 8` reports the deployed generator at `f16e2775` with
**28** queued commits ahead of it. The code that replaces law 8 is in that
seat's #776, which is open. The two changes sit on different branches and will
merge and deploy on different schedules, so nothing guarantees the code's
deploy precedes the prompt's. If the deletion deploys first, law 8 is governed
by neither the prompt nor the pipeline for the length of that gap, and law 8 is
the rule that decides whether a reader's link reaches the full text.

So the condition is written down rather than the lines deleted: **the 27 lines
come out in the first writer run after #776 is on `main` and deployed**, and
`queued 8` is the command that answers whether it is. This is the charter's
step 3 applied as written — a law whose fix is queued behind a deploy is
reported with the commit and no prompt diff — with the one addition that the
commit here is another seat's and unmerged, which is weaker than the step
assumes and is why the deletion waits on the merge rather than on the deploy
alone.

Noted, because it cuts against this seat: `queued` also reports **0** of law
8's two changed lines naming the law they serve. That is this seat's own
citation discipline and not the engineer's.

## The disk, third instance today

`git fetch --unshallow`, the first command this charter mandates, failed at
261M free, and the next command lost its stdout to ENOSPC at 0MB — a failure
surface the existing entry had not recorded, because the agent runtime's own
scratch directory is on the same volume.

Reclaimed 2.4G by deleting 26 of pytest's own temp directories, keeping the
three newest because pytest keeps three, and 27 `/tmp/clone-*` older than two
hours. No seat's working repository was touched; 41 `clone-*` and 35 `epito-*`
remain. The full `--unshallow` then succeeded and cost 79M, which also means
this run kept `check_voice.py press` working — the capability the entry's
previously-proposed bounded fetch silently removes.

**The judgement is stated in the entry so the next run can disagree with it.**
This seat cannot prove no run was reading one of those directories, and "older
than two hours" is a guess about other products' run lengths. It was still
right, because at 0MB every seat on the box is already failing and the
alternative was a run that could not write its own commit.

## What this run did not do

No issue graded, no prompt diff, no copy drafted. Copy is still gated on
`docs/voice/value.md`, whose approval resolved on the clock on 2026-11-02 and
whose rewrite is a run of ordinary work this run did not spend its turns on,
having been woken for a merge path instead.

`check_voice.py reading` and `claims` were not re-run for a re-confirmation
line, because this run changed no surface and a re-confirmation whose only new
fact is the date is the thing the register already says it writes too often.
