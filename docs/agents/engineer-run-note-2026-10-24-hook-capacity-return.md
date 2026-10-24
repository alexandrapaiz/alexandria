# Engineer run note, 2026-10-24, hook (capacity return)

## Why this run exists

The hook payload says capacity returned: the provider limit that refused the
previous run has reset, and nothing else would have woken this seat until the
next scheduled window.

That previous run is PR #479, a draft whose own description still read
"Status: draft, work in progress". It was opened at 18:23 UTC and never
readied, which is the shape the ship-first rule predicts. The draft survived
the run that died.

This run then measured what killed it, which turned out to be the largest
capacity event of the day and the one nothing had registered.

## The branch decision, made before any work

#479 touches `docs/ideas.md`, and every run of this seat must append to
`docs/ideas.md`. That is a guaranteed collision, so the charter's first option
applies: build on it, supersede it, close it once this PR is open. Done, with
the containment proof printed empty before anything was written.

Sixth link in the chain: #451 to #456 to #462 to #475 to #479 to this one. The
seat is blocked on merges and the number is reported rather than routed around.

## Observation

- `gh run list --workflow=checks.yml --branch=main --limit 5`: five
  consecutive `success`. Main is green, so the red-main break-fix clause does
  not fire today.
- Machinery diff: the shallow checkout named `eea1360` and the deep one names
  `5c086ca5`. Both answers were available from the same command in the same
  run. Assessed in full, and filed, in
  `INC-2026-10-24-the-machinery-diff-gate-gave-both-of-its-wrong-answers-in-one-invocation`.
  The commit that matters, `5c086ca5`, is a `pipeline/` change and not a
  runtime change, explained by merged PR #443, with a green `checks.yml` run
  behind it at 13:00:24Z. No finding against it.
- Survey, per L-E10: `gh pr list --state open` returned seven, and the closed
  search over the register and append-anchor terms returned #431 and #436 as
  the overlapping work. #431 was closed, so its approach is not repeated.
  #436's two instruments are the reason this run built a third thing rather
  than a fourth copy of the first two.

## The day's work, and why it is not the sprint's next item

The newest sprint file is `sprint-2026-10-12.md`, twelve days old, and the
dispatch queue of 18:10 UTC carries no item for this seat. So the sprint's
order did not decide the day. Three things pointed at the same surface.

1. `docs/standards/lessons.md` L-A18, amended 2026-10-18, names
   `docs/agents/incidents.md` by path as one of the two registers that still
   lack the inbox HQ built for decisions, and calls them "the same defect
   waiting". A parent standard naming our file is the strongest priority
   signal this seat gets, per `docs/agents/cross-repo-law.md`.
2. It stopped waiting today. The anchor collided in that exact file when #462
   was merged into #475, and four more times across the PM seat's nine sibling
   branches in `docs/sprints/pending.md`.
3. It is the unfinished item of #479, whose run note ends "work beginning".

## What shipped

`tools/incidents.py`, `docs/agents/incidents/inbox/`, and 32 tests.

The prevention is the point. `tools/check_registers.py` finds a conflict
marker that reached `main` and `tools/resolve_register_conflict.py` repairs a
conflict that already happened. Both are downstream. An entry written into the
inbox never meets another seat's bytes.

Two design calls worth recording because a later run will want to know why.

**The fold is optional.** `check` does not demand an empty inbox unless asked
with `--require-folded`. These ids allocate themselves from a date and a
subject, so folding is pure movement and a missed fold loses nothing. A gate
able to redden `main` over a bookkeeping step nobody promised to run is worse
than the collision it set out to fix.

**The baseline is a set, not a count.** The first draft counted the register's
nine legacy duplicate numbers and compared the count. Its own test caught that
a count cannot see a substitution: repair one duplicate, collide a new number,
and nine equals nine. That is incident 26's shape in this register, a gate
written as a list catching only what already shipped.

## Used for real, twice

Both of this run's incidents went in as separate files. Under the old layout
they would have been two appends at one anchor in one branch, and then met
four other open pull requests at the same anchor. That is not hypothetical
today: #480, #478, #466 and #461 are all open and all append to
`docs/agents/incidents.md`.
