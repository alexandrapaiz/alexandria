# Writer run, 2026-11-02 (message). The seventh instance of a class, found because another seat wrote down where to look

Woken by a `note` from alexandria/exo, `21680b0d`, closing this seat's
dispatcher repair. Read in full in the inbox and untruncated at 1,196
characters. Replied on the board, and the reply id is in the pull request.

**Sixth in a chain: #677 to #687 to #695 to #704 to #709 to this one. This seat
is blocked on merges.** Five runs of work now sit behind one review, which is
one link deeper than the night started and the figure the charter says to report
rather than route around.

## What the note closed, and the one sentence in it that was work

The sender closed three things and kept one, and the three closed halves are
closed correctly, so there is nothing in them for this run to do.

**The exit code is accepted, including the argument for 2 over 1.** Their
words: "a caller that cannot distinguish absent from failed has no way to tell
a typo from a regression, so the silent zero was the whole defect and not a
cosmetic one." That is the reasoning the repair was built on, returned sharper
than it was sent. Nothing owed.

**The pull request number beside the command is dropped, and they are right to
drop it.** My own entry had called the annotation correct and perishable. They
generalised it past this case: "a perishable identifier cited from a seat four
deep in a chain will be stale before it is read, so it is a courtesy and never
a mechanism." This seat is now six deep, so `cadence` has been in #687, #695,
#704, #709 and is in #714 tonight, and four of those five are closed. The
generalisation held across one more link inside two hours.

**The register row and the mail question stay theirs.** Stated in the note and
not disputed.

**What they kept is the only line in the note with work in it.** "The class
will produce a seventh instance anywhere a gate reports success by saying
nothing." They said why, and the why is the part that makes it actionable: the
four repairs before the dispatcher's all shipped a wrong SENTENCE, so each one
had a reader who could disagree with it, and all four were caught inside an
hour by somebody who did. An empty output has no reader, because an empty
output is also what a pass prints.

So the note is an instruction with an address in it. Ask that question of the
file the sixth instance lives in.

## The answer, and it is three

Every one of the 31 subcommands was run alone first, because the cheap version
of this question is whether any gate is silent on a pass, and none is. All 31
print at least two lines. The defect is not in the ordinary run, which is why
nine days of grading never reached it. It is reachable only when a caller names
a target, and that is the shape worth keeping: **the only witnesses to this
defect are the runs taking the most care about which artifact they graded.**

**One. A named path that is not there was a pass in four gates, a failure in
four others, and a traceback in one.**

```
$ python3 docs/voice/check_voice.py measure /nothing/here.md
/nothing/here.md: missing
[exit 0]
```

`measure`, `links`, `firstuse` and `provenance` exited 0. `delivery`,
`devices`, `marks` and `specimens` exited 1. `standalone` raised
`FileNotFoundError` out of `issue_sentences`. One file, one condition, four
answers, and the majority answer is a verdict of pass on an artifact nobody
opened. Each of those nine gates had been left to get this right on its own and
five of them did not, which is the argument for where the fix goes rather than
for what it says.

**Two. `captions` reported a pass and never mentioned the artifact at all, and
that is the purest instance in the register.**

```
$ python3 docs/voice/check_voice.py captions site/content/issues/2026-W39.md
CAPTION_FRAME cases                        11 of 11
[exit 0]
```

Its selection is a filter over a fixed table, `sets = [... if not paths or p in
paths]`, so a path outside that table empties the loop and the only line left
is the gate's count of its own cases. That reads greener than a real pass. It
is the sender's sentence word for word: success reported by saying nothing
about the thing that was asked.

**Three. `reading` resolves paths at its own first line and the dispatcher had
never passed it any.**

```
$ python3 docs/voice/check_voice.py reading site/content/issues/2026-W39.md
surfaces read                               63
```

`reading`'s body opens `targets = [ROOT / p for p in paths] if paths else []`,
so the capability is there and a caller can type it. `main`'s `takes_paths` set
never held `reading`, so the argument was dropped and 63 unrelated surfaces
were graded under the one path the caller named. That is ban list 91 inside the
file that enforces ban list 91, and it is the one of the three with no reader at
all: the other two print the word `missing`, and this one prints a clean
verdict under a path it did not read. `editions` has the same unused parameter
with no body that reads it, so its argument was silently ignored too.

## The repair, and why it is one check and not nine

`missing_targets(named, exists)` and `selected_sets(known, named)` are pure,
with `exists` passed in rather than called, which is the property that makes
the dispatcher's own repair worth trusting. `TAKES_PATHS` is hoisted to module
scope so `main` and the asserted cases read **one** table instead of two copies
of it, which is the discipline this file already carries twice in its own
comments: `press_schedule` reads the cron out of the job rather than declaring
it, and `press_write_site`'s docstring says its first version hard-coded four
line numbers, "which would have survived exactly as long as nobody edited the
press."

The existence check sits in `main`, immediately after the unknown-subcommand
check, and returns the same 2 for the same reason. Nine gates at the altitude
below it had each been asked to handle one condition and five got it wrong, so
putting the answer in one of them a sixth time would have been the tinker the
structure-watch step refuses. `reading` joins the routing table. `editions`
loses the parameter it accepted and never read.

Thirteen asserted cases, inside the existing `dispatch` gate rather than a
thirty-fourth subcommand, because this is one defect at three altitudes and
splitting it would hide that. `TARGET_CASES` has five, including the `--live`
case where absolute paths outside the repository must not be refused, and the
two-of-four case because a caller who mistyped two paths needs both names.
`ROUTING_CASES` has five and asserts against the live tables rather than a copy.
`SELECTION_CASES` has three, and the one that matters is a real path that
selects nothing, because without it `selected_sets` could return the whole table
always and still pass.

**Each of the three repairs was backed out in a worktree and its own cases
confirmed to fail without it.** `missing_targets` stubbed to `[]` drops
TARGET_CASES to 3 of 5, `selected_sets` stubbed to the whole table drops
SELECTION_CASES to 1 of 3, and removing `reading` from the table drops
ROUTING_CASES to 4 of 5. That step is not ceremony. The dispatcher's own entry
says this class needs it, because a case that passes either way is the defect
wearing the remedy's clothes, and this is the second instrument in this seat's
custody in one night whose cases covered the refusal and not the claim.

## The taste gate, run before the laws as the charter orders

`docs/voice/taste.md`, ruling by ruling, against what this run produced, which
is code comments, a register entry, a ban list entry and this review.

- **Codes are never owner-facing (2026-09-27).** This run's board reply and
  the pull request opening name the decisions rather than the identifiers.
  Incident slugs appear in this file and in the register, which is where the
  ruling says they stay. The ban list entry names one slug in full, inside a
  file no owner reads.
- **No meta-commentary (2026-09-19).** Binds the issue and not the review,
  and no edition was touched.
- **Plain short sentences, no semicolon joins, no stylistic em dashes
  (standing).** `check_voice.py selfcheck` over this run's diff is the machine
  for it and the figure is in the gates table below.
- **Every line of reader-facing copy reaches her first (2026-09-20).** No
  reader-facing copy was produced, so step 1b of the charter does not fire and
  no row of `docs/agents/quality-claims.md` is engaged. Nothing in this diff
  makes a claim about what the product ships.

## The laws, and why there is no grade of an edition in this file

No edition was read cold and none was graded. The newest served edition is
still **2026-W42**, `recorded_at` 2026-10-19T09:01:21.333Z, read again at
03:4xZ tonight and unmoved. Five reviews dated today already grade that one
unchanged artifact. Nothing this run found is a prose defect in a generated
edition: all three findings are in the measuring instrument, and the thing
being measured did not change tonight.

The charter's granted step-3 amendment is the clause that permits this, and the
press reading is the evidence for it. `check_voice.py press` tonight:
`f16e2775` deployed 2026-10-15, carrying the generator as of `9b6410ea`, which
is **18.3 days old**, with **30 merged commits to `prompts/digest.md` queued
behind the deploy**. A rule reworded tonight would be the thirty-first thing
waiting on the same deploy, and the last four runs reached that same answer.

**`prompts/digest.md` is untouched, which is not an omission but the whole
shape of the night.** My lasting output is the generator, and the generator's
lever is a deploy this seat does not own. What this seat does own is the
instrument that grades it, and an instrument that answers a question it cannot
see is worse than one that refuses, which is ban list 146. Three of those were
found and closed tonight.

## Structure watch

Empty. No structural fix was attempted twice through prompt changes here,
because no prompt change was made.

## What this run did not resolve, and whose it is

Nothing is handed back. The sender said the register row and the mail question
are theirs and neither is blocked on this seat, and this run agrees and did not
touch either. The three findings are all inside `docs/voice/`, which is this
seat's own surface, so they are fixed rather than reported.

The one thing worth saying upward is about the method and not the defect. The
seventh instance of this class was found because somebody wrote down where to
look, in one sentence, as a closing remark on a repair they had already agreed
to. This seat shipped the dispatcher fix believing the instance was the class.
In 364 entries of that register this is the first sibling that arrived because
a seat generalised a repair it did not own, and that is cheaper than any of the
six searches that found the others.

## The fourth instance, which this run produced while verifying the other three

The regression check for this diff was a shell line, and it reported a pass by
reading nothing.

```
diff <(grep -o 'FAIL.*' "$s/base.out" | sort | uniq -c) \
     <(grep -o 'FAIL.*' "$s/new2.out" | sort | uniq -c) && echo "IDENTICAL"
```

Both files had been written under `mktemp -d` and both were gone by the time
this ran, cleaned out of the shared `/tmp` the charter's step 0b is about.
`grep` warned on stderr, each side produced an empty stream, `diff` found no
difference between two nothings, and `IDENTICAL` printed. That is the exact
shape of the three findings above, in the instrument I was using to prove the
three findings above, inside the same hour.

It is in this review rather than quietly fixed because of what it says about
the repair's reach. The fix in `check_voice.py` makes that file refuse a target
it cannot read, and it does nothing for the next shell line any seat writes.
The class lives in the habit of composing a check out of parts that are silent
when empty, and no diff to one file reaches that. The re-run used a path inside
the working tree, asserted both files exist with `wc -l`, and recorded both
exit codes to a file rather than to a variable.

## This review's own prose, measured

`check_voice.py selfcheck` over this run's own additions reports one em-dash
mark and zero it cannot excuse. The mark is the string `--live` in the
paragraph about `TARGET_CASES`, which is the name of a command-line flag and
not a dash doing a sentence's work, so it stands under the clause that asks
this line to be written.
