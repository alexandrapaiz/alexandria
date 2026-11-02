# Writer run, 2026-11-02, message: a duplicate wake with half a message left in it

**This run graded no issue, and the reason is the one the charter's step 3
anticipates.** Counting this file, seventeen review files now carry 2026-11-02,
the press has served one edition across the whole span they cover, and `press`
reports the deployed generator at `9b6410ea`, 18.5 days old, with 30 merged
commits to it queued behind the deploy. One more wording of a rule already
queued would make the generator longer and the press no better.

What this run owed instead was a question about itself, and then one answer
nobody had sent.

## The wake was a duplicate, verified in four commands

The payload carried four inbox items. One note from the PM seat at 08:28Z
naming both copy clocks, and three from the engineer seat at 08:29Z and
08:30Z. This seat's own #781 was opened at 08:32Z, which makes the first
question whether a previous run of this seat had already done this event's
work.

It had, and the verification was read at the sources rather than out of that
pull request's report of itself:

- `board.py inbox --seat engineer` and `--seat pm` carry this seat's replies on
  the bus at 08:47, 08:48, 08:49 and 08:50Z, all four after the newest payload
  item.
- `check_voice.py deadlines` prints the duplicated-ask finding against both
  register rows, so the PM's two new ids are recorded and the governing clock
  is argued in the file.
- `check_voice.py exits` prints the matched sentence verbatim under the
  finding the engineer seat corrected, with the wrapped line joined, which is
  the repair that note asked for.

Four commands and no reconstruction. Filed as a recurrence against
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
which is where this class lives.

The fifth item in the inbox, the engineer seat's 08:30Z note, is read and owes
nothing back. It agrees with the zero-of-fifty-six arithmetic, adopts this
seat's ordering change of putting a correction on the bus before the commit
that proves it, and names its own first instance of doing so. Recorded here so
the next run does not re-answer an agreement.

## What a second wake is actually worth reading for

Three of the four messages were answered in full. The fourth was answered in
part, and that is the finding worth keeping.

The engineer seat's done named four things, and the first of them drew no
reply: the shallow check inside `undeployed_commits`, which this seat had
itself asked for on the previous run. Beside it, without asserting the cause,
the clock says the predecessor's `done` to that same seat was cut by the wake
limit at 1,151 of 1,543 characters and that its next two notes both went on
repairing the cut.

So the question a second wake should spend its turns on is not the payload
again. It is which part of the first run's reply never went. That is four
commands rather than a run, and here it found a half, and the half was the
gate this seat grades through.

## The answer that was owed, measured three times because main moved

The engineer seat wrote that `undeployed_commits` now checks the shallow case
its own docstring has promised since the function existed, and that the dict
carries `shallow: True` "so that you need not grep a sentence".

Verified rather than taken, on a one-commit clone of this repository with this
seat's gate pointed at it:

- With `tools/delivery_health.py` as it stood on `main` when this run started,
  the refusal reads "the running digest matches none of the last 1 commits to
  touch this app's files, so the deploy was built from code that is not in
  this history". That is a sentence about another seat's deploy over a cause
  that is this checkout's depth.
- With that seat's branch in place, the same clone reads "this checkout is a
  shallow clone, so the 1 commit(s) of history it holds for this app's files
  cannot place the running digest. The depth is the cause and the deploy has
  not been judged".
- **#776 then merged while this run was open**, at `b9b1d1b`, so the third
  reading is the one that counts and it was taken against the real trunk. Both
  sentences come out, the engineer's refusal and this seat's owner line under
  it.

The repair changes exactly the sentence that misled, and the string it prints
as the remedy is sufficient for its own reader, because `press_deploy` asks
about `origin/main` and that is the one ref a `--single-branch` clone does
fetch. This seat's charter carries a longer unshallow with a refspec line in
front of it, and that longer form is for naming OTHER branches, so leaving
`UNSHALLOW` alone was right.

**And the third reading nearly went into this file as a false negative.** The
probe clones this repository over `file://` with `--branch main`, and a local
branch called `main` is not `origin/main`. This clone's `main` was still at
`1c07feb` because nothing in a writer run ever checks it out, so a probe run
ten minutes after the merge measured the pre-merge tree and printed the old
sentence. One `git rev-parse main` against `git rev-parse origin/main` is what
caught it. A probe that clones from a local repository tests whichever ref the
local repository happens to hold, and the ref a run keeps current is the remote
one.

## And this seat's half of it was unbuilt, which the same probe showed

`press_verdict` collapses every refusal into the single word REFUSED. That was
right while every refusal had one remedy and it is not right any more. The
flag arrived and reached nothing in this file, so this gate was the caller it
was built for and it did not call.

The repair is `refusal_owner`, a pure function over the dict with seven pinned
cases covering the five shapes `undeployed_commits` actually returns, plus a
recovered deploy, which is nobody's. Three owners:

- `depth` is this run's own and it is two commands away.
- `deploy` is another seat's, and the printed line names
  `git rev-parse --is-shallow-repository` as the way to falsify it, because
  until #776 is on `main` a shallow clone lands in this branch.
- `receipt` is neither, and concluding anything about the press from it is the
  mistake the whole gate exists to stop.

`REFUSAL_CASES` is 7 of 7. The gate deliberately does not re-ask git the
question itself: the module that owns it is already imported two lines above
the call, and a second reader of one fact in this file is the parallel
structure this charter forbids before it forbids anything else.

**Against this seat, and it is the same shape as the predecessor's entry 114.**
Rewriting that closing paragraph stranded ban-list entry 146's `LANDED`
citation, which quoted the sentence being replaced, and `enforcements` went
red on it. The citation moved and the entry says in two sentences why it got
stronger rather than weaker. A register that cites a line has a stake in every
rewording of it, and this is the second time in one day that this chain found
that out by breaking it.

## Law 8's 27 lines still stay, and the condition is now half met

#781 wrote the condition down rather than deleting the lines: they come out in
the first writer run after #776 is on `main` and deployed. The first half
landed mid-run. The second has not. `press` reports the deployed commit at
`f16e2775` of 2026-10-15 carrying the generator as of `9b6410ea`, 18.5 days
old, with 30 merged commits queued behind it, so the code that now decides
law 8's url is not running anywhere a reader can see.

So the lines stay, for the reason #781 gave: if the deletion deploys first,
law 8 is governed by neither the prompt nor the pipeline for the length of
that gap, and law 8 decides whether a reader's link reaches the full text. The
command that answers the remaining half is `check_voice.py press`, and
`queued 8` still reports 0 of law 8's queued commits naming the law they
serve, which remains this seat's own citation discipline.

## The ledger entry, which is the asymmetry the flag left behind

`shallow: True` is set on the shallow return and no value is set on the
others, so a caller can read the flag positively and never negatively.
Absence has two meanings, either a complete history or a module that predates
the check, and nothing in the dict tells them apart. One live consequence sits
in this run's own diff: `refusal_owner` names the deploy as the cause of an
unmatched digest, which is a default rather than an answer for as long as the
older module is on `main`.

Filed for the engineer seat as one line beside one that already exists, with
the argument that `_shallow_state` keeps three states and its own docstring
argues for the third, while the dict that carries its answer outward keeps
two. The distinction survives inside the module and is lost at its edge.

## Two board refusals, and both rules were quoted in the file I wrote through

Both replies this run sent were refused on the first attempt. One body carried
no reason words, and one carried `#781` in a sentence. `tools/board.py` quotes
both refusals verbatim in its own opening comment, found on 2026-10-14 by a
seat being refused three times, and this seat did not open it before writing.
Incident 20's class, and the cost was two round trips rather than anything
worse, because the server holds that authority and held it.

One half of it is worth a ledger entry rather than a shrug. That file says it
formats rather than validates because the first two rules "are about what a
sentence says, and the third is arithmetic". A pull request number in prose is
neither: it is syntax, and the server's refusal quotes the offending token
back. A run that posts its reply as its last act before the wake ends loses
the reply, and these are the two refusals a seat writing under a limit is
least able to proofread.

## Canon law 1, and the one mark that stands

`check_voice.py selfcheck` read 25 marks across this chain's added lines and
the predecessor shipped with them. Twenty-three are struck here, across seven
files, and none of the strikes changes a finding.

The one left standing is a quotation. Line 9 of the duplicate-ask incident
quotes the PM seat saying "I will not re-post these; the clock runs from the
timestamps above", and the semicolon is inside the quoted words. Law 1 governs
this seat's prose and not another seat's, and a quotation repaired for
punctuation stops being evidence.

## The registers, checked rather than read

- No conflict markers in `docs/`, `prompts/` or `README.md`.
- `docs/voice/taste.md` line by line against this run's output, which is a
  gate, an incident, a ledger entry and this file. No reader-facing copy, so
  the 2026-09-29 site rulings do not bind anything here.
- `taste` is red on one ruling and it is not this run's: verdict 6, "never
  read for ingested", fails because `reading` is red on the four live site
  lines that `docs/voice/awaiting-her-word.md` has carried open for
  thirty-seven days.
- `enforcements` green after the citation move. `candidates` green and this
  run drafted none. `deadlines` red on both question rows by design, which is
  the predecessor's finding and stays until one ask of each pair is withdrawn.
- `check_registers.py` reports 0 blocking.
- No copy drafted, so `quality-claims.md` binds nothing in this diff.

## Main moved mid-run, and the hand resolution cost two lines

`main` advanced from `1c07feb` to `b9b1d1b` while this run was open and
conflicted this branch on `docs/agents/incidents.md` and `docs/ideas.md`, both
at the tail, which is the collision this run's own pull request body predicted
in its merge-order note.

Resolved by hand, keeping both sides in arrival order, and that was the
mistake. `tools/resolve_register_conflict.py` exists for exactly this and this
seat did not reach for it, which is the sentence the 2026-10-24 entry closes
with, now with its author's seat as the instance.

**The mechanism is new and it is the quietest in that class.** Every ledger
entry ends `- Cost: $0` and `- Status: proposed`, so both sides shared an
identical trailing run and git put those two lines below the `>>>>>>>` marker
as context. Keeping both conflict sides therefore keeps one copy of the pair,
at the end, on the other seat's entry. This run's own second entry lost its
cost and its status and stayed valid Markdown with a correct heading and no
marker anywhere. `check_registers.py` blocked on arithmetic kept for another
purpose, "63 entries carry no readable status, up from the recorded 62", and
the repair was two lines put back.

Filed as a recurrence, with the part that is new from the other direction:
the tool's `--check` mode refuses once the fix sits on top of the merge, so a
seat that resolves by hand and only then thinks of the audit has nothing to
run.

## The disk, confirmed and not re-filed

It reached 40K free mid-run and two commands lost their output to ENOSPC,
which is the surface the predecessor added to the existing entry on this same
day. Reclaimed by deleting pytest temp directories older than an hour, `tmp.*`
scratch directories older than two hours and `clone-*` directories older than
forty-five minutes, which returned 2.9G. No seat's working repository was
touched and this run's own probe clones were deleted as they were finished.

Confirmation and not a new instance, because four seats filed it today and the
judgement is the predecessor's with the window tightened. The tightening is
worth naming so the next run can disagree with it: forty-five minutes is a
guess about other products' run lengths, and at 40K free every seat on the box
is already failing.
