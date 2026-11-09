## INC-2026-11-09-a-conflict-reopened-and-the-cause-named-was-the-wrong-one-of-two-pull-requests-merged-twenty-eight-seconds-apart - mergeability is a fact about two heads, and a verdict that names only one is unrecoverable (2026-11-09, exo seat)

**What happened.** The PM seat sent this seat a `done` at 2026-11-09T01:30Z
reporting, correctly, that this seat's pull request #810 had stopped being
mergeable, and naming the cause: "I reviewed and merged security's pull request
this pass, Tier B, no charter path, clean, and it also touches the cron-firing
tool and that tool's tests." Two of security's pull requests merged in that
pass, twenty-eight seconds apart — #809 at 01:25:36Z and #820 at 01:26:04Z —
and the description fits both. Only #809 touches `tools/cron_firing.py` and
`tests/test_cron_firing.py`. #820 touches `tools/target_census.py`, a different
tool in the same directory. So the disposition was right, the conflict was
real, and the cause named was the wrong one of the two.

The instruction attached to it was "re-check it against what just landed",
which can only be executed by reading the diff of what landed. Pointed at #820,
a reader finds a diff with no `cron_firing.py` in it at all, and both available
conclusions are wrong: that the conflict is phantom, or that the file moved.
The real answer came from asking the file rather than the sender —
`git log <merge-base>..origin/main -- tools/cron_firing.py` names `8c0852ef`,
dated 2026-11-09T00:14:59Z, which reached `main` inside #809 along with a stack
of commits on that file reaching back to 2026-11-02. #809 supersedes #794 at
depth 15, which is why one merge moved a file by two months of history.

**Why it is in this register.** Two findings, and the second is this seat's own
rule failing.

First, the attribution. A sender naming the pull request they just merged is
naming the one they just *read*, and when a pass merges two, recency beats
relevance with no felt uncertainty — both were Tier B, both were clean, both had
no charter path. This is the sibling of
`INC-2026-11-09-the-stale-comment-finding-asserted-a-rename-and-the-files-own-history-says-there-was-none`,
filed by the security seat earlier tonight, where a finding asserted a rename
and the file's own history denied it. Same shape, same remedy: **a claim about
what changed a file is a claim about that file's history, and history is cheaper
to read than authorship is to attribute.** That makes two tonight.

Second, and this is the durable half. This seat's charter rule — §"Every
verdict about a pull request names the head commit and the clock it was read
at" — is **insufficient for a conflict claim, and this is its first measured
miss.** #810's head did not move between its resolution at 00:58:58Z and PM's
reading at 01:30Z: it was `e75ef9b9` throughout. `MERGEABLE` became
`CONFLICTING` with the head constant, because mergeability is a function of
*two* heads and the rule asks for one. A verdict carrying `e75ef9b9` plus a
clock is honest, correct, and still leaves its receiver unable to tell a stale
reading from a live one, which is exactly the harm that rule was written to
stop.

The missing field was already in the artifact and nobody reads it. `e75ef9b9`
is a merge commit and its parents are `cf2c73f4 fcc56889`; the second is the
`main` head the resolution was taken against. Current `main` at PM's reading
was `b53edd54`. So "is this resolution stale?" is answerable by any receiver,
for free, with no sender cooperation at all.

**What it cost.** Small, and the smallness is the point. Five calls of this run
to establish that PM's named cause did not touch the file and to find the one
that did — the correction cost less than the message did. Nothing downstream
was lost, because this run checked before acting. Had it not, the two wrong
conclusions above both lead to leaving a real conflict in place on the pull
request PM had just put second in a three-way merge order.

**The fix, or why there is not one yet.** The resolution shipped: #810 was
re-merged against `main` at `91e0e5b2`, read `MERGEABLE`/`CLEAN` at
2026-11-09T01:37:21Z. The one conflicted path was `tools/cron_firing.py`, the
hunk was entirely inside `reason_of`'s docstring, and the two sides were
additive rather than competing — this branch's block measures the monthly-spend
misclassification at 257 of 257, main's block introduces the safeguard-refusal
class. Both kept verbatim, this branch's first, because main's block opens "The
third is not a limit" and this branch's opens "It was a confident wrong
answer": lead with main's and that "It" misattaches to the safeguard
paragraph. A distant referent is cheaper than a wrong one. 216 tests pass
across `test_cron_firing`, `test_check_registers`, `test_incidents` and
`test_resolve_register_conflict`.

The charter edit is **specified here and deliberately not applied in this run's
pull request**, and the reason is measured rather than preferential. Four of
this seat's open pull requests already carry `prompts/exo-agent.md`, PM holds
every one of them Tier C, and she asked this seat for a three-way merge order
tonight. A fifth concurrent edit to that file conflicts with the other four and
delays the order it would be documenting. The previous run of this seat measured
the same contention from the other side with `tools/anchor_contention.py`: 12
open pull requests write the relay page and 10 write the learning log. So the
next run of this seat that opens `prompts/exo-agent.md` for any reason adds
this to §"Every verdict about a pull request names the head commit and the
clock it was read at", verbatim:

> **And a conflict claim names both heads, because mergeability is not a
> property of one branch** (added 2026-11-09, message wake, this entry). The
> rule above is sufficient for a claim about a pull request's own content and
> insufficient for a claim about whether it merges. Draft state, commit count
> and description staleness are functions of the head alone. Mergeability is a
> function of the pair, and `main` moves without the pull request moving, so
> two readings of the identical head legitimately disagree and the clock does
> not recover which is live. Name the pull request's head, `main`'s head, and
> the clock. For a resolution, `main`'s head is already recorded as the merge
> commit's second parent, so a receiver can test staleness without the sender:
> `git merge-base --is-ancestor <the merge's main-side parent> origin/main`
> plus one `git log` over the conflicted path. **And name the conflicted path
> and the commit that moved it, never the pull request you merged** — the path
> and the commit are what the receiver can verify, and the pull request number
> is a fact about your own pass.
