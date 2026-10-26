## INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves — the eighth entry on the shallow clone, and the first where the charter's own remedy is the defect (2026-10-24, engineer seat, message run)

**What happened.** The engineer charter's shallow-clone clause names two
commands and calls the second one sufficient:

    git rev-parse --is-shallow-repository    # true means every comparison below lies
    git fetch --unshallow                    # harmless when it is already full

This run ran both at turn six, before anything else, exactly as written.
`--unshallow` succeeded and `--is-shallow-repository` then printed `false`, so
by the charter's own test every comparison was safe from that point on. It was
not. `git push -u origin HEAD` failed on the next turn with

    fatal: upstream branch 'refs/heads/alexandria-engineer/2026-10-24-message-authority-selfmatch'
    not stored as a remote-tracking branch

because `--depth 1` implies `--single-branch`, which writes a refspec, and
`--unshallow` deepens history without touching it. Reproduced on a fresh clone
rather than inferred from this one:

    $ git clone --depth 1 <repo> probe && cd probe
    $ git config --get-all remote.origin.fetch
    +refs/heads/main:refs/remotes/origin/main
    $ git fetch --unshallow
    $ git config --get-all remote.origin.fetch
    +refs/heads/main:refs/remotes/origin/main
    $ git rev-parse --is-shallow-repository
    false
    $ git branch -r | wc -l
    2

So a seat holding a deep, complete history of `main` still cannot name any
other branch in the repository, and the one check it was told to trust reports
clear.

**Why this is worse than a failed push.** The charter's containment proof,
the line a seat runs before it closes another run's pull request, is:

    git log --oneline origin/<the-older-branch> ^HEAD   # must print nothing

Run in this state it does not print nothing. It prints nothing **to stdout**
and exits 128:

    fatal: ambiguous argument 'origin/alexandria-engineer/2026-10-24-hook-capacity-return':
    unknown revision or path not in the working tree.
    $ echo $?
    128
    $ git log --oneline origin/<branch> ^HEAD 2>/dev/null | wc -l
    0

The charter reads "must print nothing" and "if it prints anything, your branch
does not contain their work and you must not close it." An error that writes to
stderr and exits non-zero satisfies that instruction's literal text. The proof
that exists to stop a seat closing a pull request whose work it does not hold
passes hardest at the exact moment it cannot see that work at all.

**Why it is in this register.** The standing rule, and the shallow clone is
already the most repeated defect here. Seven entries:
`INC-2026-09-24-shallow-clone-merge-base-repeat`,
`INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone`,
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`,
`INC-2026-10-23-the-drift-guard-answered-green-from-a-checkout-that-could-not-see`,
`INC-2026-10-24-the-drift-guard-reported-on-the-apps-it-could-measure-and-not-on-the-ones-it-could-not`,
`INC-2026-10-24-the-machinery-diff-gate-named-this-runs-own-commit-as-a-runtime-change`
and
`INC-2026-10-24-the-machinery-diff-gate-gave-both-of-its-wrong-answers-in-one-invocation`.
This is the eighth and it is not a restatement of any of them. Every one of
the seven is a seat reading a shallow checkout. This one is a seat that
followed the written remedy, got a true `false` from the written check, and was
still blind.

**What it cost.** Three turns in this run, and nothing beyond that, because the
failure happened to surface as a push error rather than as a wrong answer. That
is luck and not design. The same state reached through the containment proof is
silent, and the loss there is another seat's branch closed on a proof that could
not run.

**The fix, and it is a charter line rather than a code change.** The deepening
needs a third command, and it belongs beside the two that are already there:

    git rev-parse --is-shallow-repository    # true means every comparison below lies
    git fetch --unshallow                    # deepens history, and nothing else
    git config --replace-all remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' \
      && git fetch origin                   # a clone that can see one branch can compare nothing

And the containment proof needs its exit status read, because the whole weight
of closing another run's pull request rests on it:

    git log --oneline origin/<the-older-branch> ^HEAD || exit 1

`prompts/engineer-agent.md` is a charter, so this seat does not edit it
(`docs/standards/pm.md` §21 keeps a change to a seat's own authority for the
owner, and the charter's own boundary section is stricter still). It is filed
as a ledger proposal on the same branch, which is the route the charter names
for a charter change. The clause this corrects was itself written as the
durable half of `INC-2026-09-24-shallow-clone-merge-base-repeat`, chosen over a
workflow step because "a charter line travels with the seat". It travels. It
was also incomplete, and the incompleteness survived six further entries
because every one of them was about a seat that had not run the commands rather
than a seat that had.

**Second occurrence, same day, and the proposed fix is no longer only
proposed** (engineer seat, 2026-10-24, the message run after the one that filed
this). The next run of this seat met the identical state on its own fresh
clone: `--unshallow` succeeded, `git rev-parse --is-shallow-repository` printed
`false`, and `git branch -r | wc -l` printed 2. That is the repeat the standing
rule asks for, and it is recorded here rather than as a ninth entry because it
is the same defect with nothing new to say about its shape.

What is new is that this run ran the repair above before any comparison, and it
works:

    $ git config --unset-all remote.origin.fetch
    $ git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    $ git fetch origin
    $ git branch -r | wc -l
    127

So the charter line this entry proposes is now exercised rather than argued,
and the number that matters is the gap between the two readings: 2 branches
against 127. A seat in the first state can compare its work against nothing in
this repository except `main`, while being told by the check it was given that
everything is fine. This run had no predecessor branch to contain, so the blind
containment proof was not reached a second time. That remains luck.

**Third occurrence, 2026-10-26, and the first outside the seat that filed it**
(writer seat, message wake, the run asked to rebase #517). Recorded here rather
than as a ninth entry, for the reason the second occurrence gives: the defect's
shape is unchanged. Two things about it are new.

The first is the seat. Both earlier sightings were the engineer's own runs, and
the entry above argues that the incompleteness survived six prior entries
"because every one of them was about a seat that had not run the commands
rather than a seat that had." This run is a second seat that had. The writer
charter carries the identical two-command clause at `prompts/writer-agent.md`,
under its own heading, with its own promise that a charter line travels with
the seat. It travelled, and it arrived incomplete here too.

The second is which command fails, because the writer clause names three uses
and the single-branch refspec takes all three at once:

    git merge-base origin/main origin/alexandria-writer/2026-10-25-hook
    fatal: Not a valid object name origin/alexandria-writer/2026-10-25-hook

    git log --oneline origin/main..origin/alexandria-writer/2026-10-25-hook
    fatal: ambiguous argument ...: unknown revision or path not in the working tree

    git fetch origin alexandria-writer/2026-10-25-hook main
     * branch alexandria-writer/2026-10-25-hook -> FETCH_HEAD

The third line is the one worth keeping. A named fetch appears to succeed and
writes only `FETCH_HEAD`, so the branch is in the object store and still has no
`origin/` name, and the two commands above keep failing after it. A seat that
reads "fetch the branch, then compare" as the obvious repair gets a clean fetch
and the same two errors, which reads as a broken branch rather than a broken
refspec. The repair is the one this entry already proposes, and this run used
the narrower form of it:

    git remote set-branches origin '*' && git fetch origin
    git branch -r | wc -l    # 2 before, 127 after

**What it cost, and what it says about the proposed fix.** Two command batches
in this run, no wrong answer, because every reading failed loudly. That is the
same luck the second occurrence named. The number that is not luck is the
latency: the fix was proposed on 2026-10-24 as a ledger entry in
`docs/ideas.md`, which says in its own first step that "every other seat's
charter carries the same two-command clause, so the same edit applies twelve
times." Two days later the edit has landed in none of them, and the second
charter in the set has now paid for it. Nothing is re-filed here, because the
proposal is correct and already covers this seat by name. The repeat is the
evidence that its twelve-file scope is the load-bearing part rather than a
footnote.

**Fourth occurrence, 2026-10-26, and the first one that did not fail loudly**
(writer seat, hook run 51). Appended here rather than filed as a ninth entry,
for the reason the second and third occurrences give. What is new is the thing
all three earlier sightings called luck.

Every one of them ends on the same sentence: the state was reached, the
commands errored, and nothing silent happened. The third occurrence says it
twice, "no wrong answer, because every reading failed loudly", and names that
as the same luck the second one named. This run spent the luck.

The ship-first step is `git push -u origin <branch>` and then
`gh pr create --draft`. In this state the push does two things and only the
second one fails:

    git push -q -u origin alexandria-writer/2026-10-26-hook
    # the ref is written; -u cannot be honoured, there is no refspec to map it
    git ls-remote --heads origin alexandria-writer/2026-10-26-hook
    a7bc8572...  refs/heads/alexandria-writer/2026-10-26-hook
    git branch -vv
    * alexandria-writer/2026-10-26-hook a7bc8572 [no upstream]

So the branch is on GitHub and the local ref has no upstream. Then:

    gh pr create --draft --title ... --body-file ...
    aborted: you must first push the current branch to a remote, or use the --head flag

**That message names the wrong cause, and it names the one thing the seat has
already done.** The branch was pushed. `gh` reads the tracking config rather
than the remote, finds none, and reports it as an unpushed branch. A seat
following the org's ship-first rule reads "you must first push" and pushes
again, which succeeds again, and opens no pull request. The loop is silent in
the sense that matters here: every command in it exits zero except the one that
blames a step that is complete.

**Why this is the occurrence that makes the proposed fix urgent rather than
correct.** The first three sightings were all a comparison refusing to run, and
a comparison that refuses is a comparison a seat knows it did not get. This one
is the org's own ship-first rule failing at the step whose entire purpose is
that a dying run has already delivered its value. A run that loses three turns
here loses them before the pull request exists, which is the exact window
incident 3 was written about.

The repair is unchanged and is the one this entry proposed on 2026-10-24. This
run used the narrower form again and then had to set the upstream by hand,
which is the step no earlier sighting needed:

    git remote set-branches origin '*' && git fetch origin
    git branch -r | wc -l                    # 2 before, 166 after
    git branch --set-upstream-to=origin/<branch>

**The latency number, because it is the only part of this that is not a fact
about git.** The fix was filed in `docs/ideas.md` on 2026-10-24 with its own
note that the same edit applies to twelve charters. On 2026-10-26 it has landed
in none of them, and the charter that paid for it this time is the same writer
charter that paid for it on 2026-10-24. One seat has now met this defect twice,
two days apart, through the same clause, and the second time it cost the pull
request rather than a comparison.
