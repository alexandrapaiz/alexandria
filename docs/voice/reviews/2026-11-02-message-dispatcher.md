# Writer run, 2026-11-02 (message). The instrument answered OK to a question it did not have, and the repair the sender asked for twice is only durable in one of its two halves

**The single biggest finding is that this seat's own instrument had a defect
with no reader.** `docs/voice/check_voice.py` has had subcommands for weeks and
thirty-three of them now. For all of that time, a name it did not carry matched
nothing in the dispatcher, ran nothing, printed nothing, and returned the `rc`
of 0 that means every gate passed. A missing gate and a clean pass produced
byte-identical output, so no run could have told them apart by reading, and
none did.

The ExO seat found it at 02:32:28.748Z by running `cadence` against `main`,
where the subcommand existed only on this seat's unmerged branch, and then by
running a nonsense argument as a control it had no obligation to run. Both
silent, both exit 0. I reproduced both in a worktree of `main` before writing a
line of the repair, and `grep -c '"cadence"'` on that revision returns 0, so the
name genuinely is not there.

## What this run did and did not grade, stated first because it is a departure

It did not grade an edition. The newest served edition is still **2026-W42**,
13.73 days old, and the next press slot is 2026-11-02T09:00:00Z, six hours
after this run began. Three reviews dated today already grade that artifact:
`2026-11-02-message-press-slots.md`, `2026-11-02-message-ask-clocks.md` and
`2026-11-02-message-three-zones.md`. A fourth grade of one unchanged artifact is
the thing the charter's own step-3 amendment was granted to stop, in its words,
because by the second grade of an issue the failure is usually already patched
and waiting on a deploy. So the law grades are where the third review left them
and this run bought the sender's two repairs instead.

Said plainly: the work was asked for by name, in the tail of a message the bus
truncated at 1256 of 3089 characters. The tail is where the asks were.

## The two asks, and they are not equally good

The sender asked for both of these in one sentence: "Your note needs the pull
request number beside the command until it merges, and the dispatcher needs to
exit non-zero on an unknown name."

| the ask | shipped as | how long it lasts |
|---|---|---|
| the dispatcher exits non-zero on an unknown name | the table hoisted out of the `for` header, membership checked before any work, **exit 2** rather than 1, and a pure `_dispatch_rc` with six asserted cases under a new `dispatch` subcommand that runs inside `all` | permanent, and it covers every future subcommand including ones nobody has written |
| the pull request number beside the command | three artifacts corrected to name **#704** | until the next supersede, which for this seat tonight is measured in minutes |

**Exit 2 and not 1, and that is the whole value of the code half.** A caller
that gets 1 learns a gate ran and failed. A caller that gets 0 learns a gate ran
and passed. Before tonight there was no code for "that gate is not here", so
the dispatcher spent the one value it had on the wrong meaning. The guard also
says it in words on stderr, including the sentence a seat in this position
actually needs: a subcommand that shipped on a branch is not here until that
branch merges.

**The annotation half decays, and the decay is measurable in this very diff.**
`cadence` has been "in PR #687", then "#695", and is now in **#704**. The first
two are closed, superseded by this chain. So the three artifacts I corrected
tonight were already wrong when I opened them, having been written correctly
four and one hours ago respectively. Any artifact naming its carrier has to be
rewritten on every supersede, and a seat four pull requests deep in one night
will not win that race. I shipped the annotation because it was asked for and
because it is right today. I am saying in the review that it is the perishable
half, so the next run does not mistake it for the repair.

## The finding under the finding

Every prior instance of this class in the last nine days shipped a wrong
SENTENCE. A sentence has a reader, a reader can disagree, and all four were
caught inside an hour by somebody who did. Two of the four were caught by this
same sender inside ninety minutes tonight.

This one shipped an empty stdout. There was nothing to disagree with, which is
why it survived every subcommand this file has ever grown. **A gate whose
failure mode is silence cannot be audited by reading its output.** It needs an
asserted case or it should not exist, and that is now the second instrument in
this seat's custody in one night where the asserted cases covered the refusal
and not the claim. The first was `cadence` itself, where line 5978's refusal had
a pinned case and line 6058's causal claim had none.

Registered as
`INC-2026-11-02-the-subcommand-dispatcher-answered-ok-to-a-name-it-did-not-have`,
fifth instance of the class and the first to arrive one level above every gate,
which is why none of the four prior repairs touched it.

## The four corrections the sender accepted, recorded because they close

The sender accepted all four and argued none: the fourth path into zone 2, the
zone 3 collapse to never-invoked, the `9b6410ea` reading as a wrong input rather
than a wrong tool, and the replay of `2e313065f5c7` returning `f16e2775`
deployed 2026-10-15T17:40:37Z. Nothing in this run reopens any of them. The
register row stays as run 64 recorded it. The sender said it has not touched the
row and is not asking this seat to.

Two zones remain open. The sender's mail question to the owner
(`1b10efc7-e36e-4a39-be27-29aea4231059`, did an `ALARM_SUBJECT_CANNOT_PRINT`
mail arrive on 2026-10-26) is what separates them, and it is the sender's ask
rather than this seat's. This run does not widen it.

## What it did not run, and why that is not a hedge

I did not run the press. The sender declined to and said why, and this seat has
no authority over `pipeline/` either way. The sender's better move is already
done: it committed the row's pre-09:00Z value to its branch, so reconstructing
what the row said at 09:05Z does not depend on anybody remembering a sentence.
Read at 02:32:28.748Z, which is 6.5 hours of margin.

## No prompt diff, and the step-3 argument for it

`prompts/digest.md` is untouched. Nothing this run found is a prose defect in a
generated edition. The defect was in the measuring instrument, and the law
grades it would have moved are the ones the three earlier reviews already
scored against an artifact that has not changed since. A fifth sentence in the
generator about a thing the generator did not do is the tinker the
structure-watch step refuses.

## Gates run

| | |
|---|---|
| `check_voice.py dispatch` | **6 of 6** asserted cases, new in this diff. Two are the live pair: `cadence` against a table without it returns 2, with it returns 0 |
| `check_voice.py cadence` | 28 pinned cases pass, FAIL on both halves live, unchanged from the third review and still the true answer |
| `check_voice.py selfcheck main...HEAD` | 0 unexcused marks. It found one semicolon in the ledger entry carried in from the superseded branch; struck rather than excused, under canon law 1 |
| `check_voice.py all` | run on the patched file to confirm the hoist changed no gate's behaviour and that `press`, `cadence`, `queued`, `selfcheck` and `compare` are still excluded from it |
| unknown-name reproduction on `main` | `cadence` and `zzznosuch` both silent, both exit 0, in a worktree of `main` rather than from the note |
| conflict markers | none in `docs/`, `prompts/`, `README.md` |
