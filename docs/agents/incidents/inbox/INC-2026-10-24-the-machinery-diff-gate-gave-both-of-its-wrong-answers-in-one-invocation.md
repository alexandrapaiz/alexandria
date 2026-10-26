## INC-2026-10-24-the-machinery-diff-gate-gave-both-of-its-wrong-answers-in-one-invocation - the seventh entry on the shallow clone, and the first where the false positive and the false negative arrived together (2026-10-24, engineer seat, hook run)

**What happened.** The engineer charter's first pre-ship gate is one command,
run here at turn six on the checkout the host handed this run, which was one
commit deep:

    git log --since="36 hours ago" --format='%h %ci %an %s' -- .github/ pipeline/

It returned exactly one row, the merge of `#471`, and this run recorded that
row in its own opening commit as the thing to assess.

Later in the run, for an unrelated reason, the checkout was deepened with
`git fetch --unshallow`. The identical command on the same tree then returns a
different single row:

    5c086ca5 2026-10-24 12:13:50 +0000 alexandria-engineer  Each app's cron schedule is read out of its own module, not kept beside it

So the shallow answer was wrong twice over in one invocation. `eea1360` is a
false positive, and its diff against its first parent is one file,
`docs/standards/lessons.md`, with nothing under either watched path:

    $ git diff --name-only eea1360^1 eea1360 -- .github/ pipeline/
    $ git diff --name-only eea1360^1 eea1360
    docs/standards/lessons.md

And `5c086ca5` is a false negative. It touches `pipeline/runtime_sha.py`, it
is inside the window, and the shallow gate did not mention it.

**Why it is in this register.** The standing rule, and the register already
holds six entries on this shape:
`INC-2026-09-24-shallow-clone-merge-base-repeat`,
`INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone`,
`INC-2026-10-23-the-drift-guard-answered-green-from-a-checkout-that-could-not-see`,
`INC-2026-10-24-the-drift-guard-reported-on-the-apps-it-could-measure-and-not-on-the-ones-it-could-not`,
`INC-2026-10-24-the-machinery-diff-gate-named-this-runs-own-commit-as-a-runtime-change`
and
`INC-2026-10-24-the-deepening-fetch-landed-the-history-and-called-it-a-failure`.

**What is new, and it is a correction to the fifth entry rather than a
restatement.** That entry, filed earlier today by this seat on a message run,
established the false positive and then said this:

> After `git fetch --unshallow`, on the same tree in the same minute, the
> identical command returns **nothing at all**. The true answer is that no
> commit touched `.github/` or `pipeline/` in the last thirty-six hours.

The first sentence is a correct observation of that run. The second is a claim
about the repository and it does not survive the day. `5c086ca5` landed at
12:13:50Z and merged to `main` inside `#443` before 13:00Z, which is before
that run started, so the deep answer in that window was `5c086ca5` and not
nothing. The most likely explanation is that the deepened checkout was that
run's own branch rather than one containing the merge, which is the same class
of error one level up: a confident statement about history from a checkout
that could not see all of it.

The reason this matters more than a tidy-up is that the fifth entry's wrong
half is the reassuring half. A seat that reads "the true answer is nothing"
has been handed a reason to believe the watched paths are quiet, which is
precisely the belief the gate exists to withhold.

**What the gate was supposed to catch here, answered properly.** `5c086ca5`
is this seat's own commit. It adds 56 lines to `pipeline/runtime_sha.py` that
read each app's cron schedule out of its own module instead of keeping a
hand-copied list beside it. It changes no schedule, no model, no provider, no
cap, no timeout and no image, so it is a `pipeline/` change and not a runtime
change under `docs/agents/runtime-changes.md`. Both questions the law asks
come back clean. A merged pull request explains it, `#443`, and there is a
green run behind it: `checks.yml` on `main` at 2026-10-24T13:00:24Z,
conclusion `success`, on the merge commit `1765bb3`. No finding, and this
paragraph exists because the gate's purpose is to produce this paragraph
rather than to produce a row.

**The fix, and why it is not a code change here.** The command lives in a
charter, and a charter is not this seat's to edit. What is in this seat's
gift is to put the deepening in front of the gate in its own run every day,
and to record that the reflex has now failed on this topic seven times, which
makes it the single most repeated defect in this register. The durable repair
is that the gate should refuse to answer rather than answer wrongly: one line
before the command, `git rev-parse --is-shallow-repository`, and a seat that
reads `true` has learned something more useful than any row the gate could
print. That is a charter line rather than a code change, so it is written out
here in full, as the one edit that closes seven entries:

    Before the machinery diff, run `git rev-parse --is-shallow-repository`.
    If it prints `true`, run `git fetch --unshallow` and only then the diff.
    A shallow checkout has two wrong answers available to it and no right one.

This run is not filing it as a ledger proposal as well. Three proposals and a
craft scan is what the charter asks a run to draft, this run has drafted them,
and a fourth entry competing with its own siblings for the owner's attention
is how a ledger stops being read. The seven entries above are the argument and
they are already in the register that the ExO seat reads every week.
