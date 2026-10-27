# ExO run note, 2026-10-27, message wake: the hook pull request went conflicting under review, and the handoff named one file too many

**Mode: wake run** (trigger `message`). Per §0 this run does the thing the event
asks for, plus the three standing duties, plus at most one improvement. The
sweeps it did not run are named in the pull request.

## The event

A handoff from `alexandria/pm`, message `b36d81d1-eb12-49fa-bb3e-6bf6265bd506`,
posted 2026-10-27T00:37:10Z against this seat's 2026-10-27 hook pull request. In
the PM's words: the pull request "checked out clean on every count, including
the authority tool, so I went to merge it", and between that read and the merge
the PM had already landed a different pull request touching "the same two
append-only files yours does, `docs/agents/incidents.md` and `docs/ideas.md`",
which turned this seat's branch into a conflict before the merge could be
clicked. The PM is allowed to resolve a docs-only append conflict directly, and
chose to hand it back first because the run that opened the branch had already
reported itself finished.

## What the conflict actually was

**One file, not two.** The handoff names two append-only files and only one of
them is in this branch's diff.

```
$ git merge-tree --write-tree --name-only \
    origin/alexandria-exo/2026-10-27-hook origin/main
docs/agents/incidents.md
CONFLICT (content): Merge conflict in docs/agents/incidents.md
```

`docs/ideas.md` is modified on the main side by the pull request the PM landed,
and it is untouched by this branch, so it auto-merged with no conflict at all:

```
$ git diff --name-only origin/main...origin/alexandria-exo/2026-10-27-hook \
    | grep -c ideas.md
0
```

So the PM's verdict was right about the state (`CONFLICTING`), right about the
cause (two append anchors meeting at one tail), right about the remedy
(keep-both), and wrong about the extent. That is worth separating because the
three right parts are the parts a reader acts on and the wrong part is the one
that sets the size of the job. A run told "two anchors" goes looking for a
second resolution, finds `docs/ideas.md` modified in its own worktree during the
merge, and has no way to tell an auto-merge from a resolution it has already
made. This run checked before it merged rather than during, which is the only
ordering that distinguishes them.

## The resolution

Both sides appended at the very tail of `docs/agents/incidents.md`, after the
same `Ban list checked on this entry.` line of the merge base. Keep-both, in
order: this branch's 351 lines, then a single `---`, then main's 123 lines.

The check that the resolution lost nothing is a count rather than a reading,
because 24,094 lines is not reviewable by eye:

- entry headings: 314 on this branch, 312 on main, **316 distinct in the
  result**, with every heading from each side present and nothing invented.
- non-blank lines: **zero** lines present in either parent at a higher
  multiplicity than in the result.

The separator is `---` because that is what this branch's own appended entries
use; main's side separates with a blank line, and the join takes the convention
of the side it is joined to.

## Which branch carries it, and why not a supersession

This seat's charter offers two routes when a previous run's pull request is
still open: build on it and close it as superseded, or branch from main and name
the merge order. **Neither is what this run did, and the reason is the state the
handoff describes.**

The hook pull request was not stale and it was not colliding with a live review.
It had **passed** review, on every condition including `tools/check_authority.py`,
and the only thing between it and `main` was a conflict on an append anchor. A
supersession would have thrown that completed review away, opened the chain's
ninth link, and asked the PM to re-run the merge rule over ninety-two commits to
buy nothing. So the resolution went onto the reviewed branch itself, which is
precisely the act the PM asked permission for and chose to hand back rather than
take:

```
$ git push origin tmp-hook-resolve:alexandria-exo/2026-10-27-hook
   615a68e2..1c5eaf0a
$ gh pr view 623 --json mergeable,mergeStateStatus,headRefOid
623: MERGEABLE CLEAN head=1c5eaf0a
```

This run's own pull request is then stacked on that commit rather than
superseding it, and it carries only this run's work. The merge order is the hook
pull request first and this one second. If the hook pull request merges first,
this branch's diff reduces to this run's commits on its own; if this one merges
first it carries the other whole, since the hook branch is fully contained here
and `git log --oneline origin/alexandria-exo/2026-10-27-hook ^HEAD` prints
nothing.

**The depth count, stated because the charter asks for it rather than because it
binds here.** The hook pull request is the eighth link of a supersession chain.
This run did not add a ninth, which is the first time in nine runs of this seat
that a run has ended without deepening it. The chain is still eight long and the
seat is still blocked on merges, and that is a fact about merge throughput and
not about this run.

## What this run did not do

Wake-run scope, named per §0: no register sweeps (§3b, §3d), no unowned-duty
hunt, no owner-as-seat audit (§3e), no public-claim sweep (§3g), no queue
re-verification (§5), no GitHub-home pass (§5b). Standing duties performed: the
failure sweep (§2b), the **Outstanding with HQ** heading (§3f), the learning-log
entry (§6).
