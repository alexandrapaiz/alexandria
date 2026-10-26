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
