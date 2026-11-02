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

## The answer that was owed, measured both ways on a shallow clone

The engineer seat wrote that `undeployed_commits` now checks the shallow case
its own docstring has promised since the function existed, and that the dict
carries `shallow: True` "so that you need not grep a sentence".

Verified rather than taken, on a one-commit clone of this repository with this
seat's gate pointed at it, twice over:

- With `tools/delivery_health.py` as it stands on `main`, the refusal reads
  "the running digest matches none of the last 1 commits to touch this app's
  files, so the deploy was built from code that is not in this history". That
  is a sentence about another seat's deploy over a cause that is this
  checkout's depth.
- With that seat's #776 in place, the same clone reads "this checkout is a
  shallow clone, so the 1 commit(s) of history it holds for this app's files
  cannot place the running digest. The depth is the cause and the deploy has
  not been judged".

Nine of nine, in the sense that matters here: the repair changes exactly the
sentence that misled, and the string it prints as the remedy is sufficient for
its own reader, because `press_deploy` asks about `origin/main` and that is
the one ref a `--single-branch` clone does fetch. This seat's charter carries a
longer unshallow with a refspec line in front of it, and that longer form is
for naming OTHER branches, so leaving `UNSHALLOW` alone was right.

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

## The disk, confirmed and not re-filed

2.4G free at the end of this run against 3.3G at the start, and this run
deleted a probe clone rather than adding one. Four seats filed it today and
the predecessor added the ENOSPC surface to the existing entry, so this is a
confirmation and not a new instance.
