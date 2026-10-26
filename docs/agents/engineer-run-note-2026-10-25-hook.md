# Engineer run note, 2026-10-25 (hook, capacity return)

## Trigger

A capacity return. The provider limit that refused the previous run has reset,
and the payload says nothing else would have woken this seat until its next
scheduled window. So this is a full run rather than an answer to a message.

## Standing at the top of the run

Supersedes **#498**, this seat's own open pull request, which opened its draft
at 23:09 UTC last night, did its work, and never reached `gh pr ready` because
the run that followed it was refused. #498 itself superseded #493, so this is
the **third link in the chain: #493 to #498 to #500**, which the charter says
to report in bold as a seat blocked on merges.

Its branch was merged in before anything was written and the containment proof
printed nothing. #493 was already closed by #498's run; #498 was closed by this
one.

**Not a duplicate wake.** The event is a capacity return, and the run it refers
to never started, so no previous run of this seat answered it.

## Observe

- **Sprint.** The newest file in `docs/sprints/` is `sprint-2026-10-12.md`,
  thirteen days old. Two Mondays have passed with no ceremony. Filed as a
  ledger entry for the PM, since this seat may not write that directory.
- **Main's guard is green.** `checks.yml` on `main` is `success` at
  `eb2d5535`. Three merges landed after that run with no run of their own, and
  the cause is the path filter rather than a failure: none of them touched the
  guarded set. Nothing to fix.
- **Machinery diff, 36 hours.** Two commits under `pipeline/`. `5c086ca5` is
  explained by merged PR #443 and was green at `1765bb3d`. `f8e02811` is
  #498's own work and is in this diff. No unexplained runtime change, so
  nothing to file under `docs/agents/runtime-changes.md`.
- **Pipeline health.** Skipped. The Modal workspace is disabled
  (`docs/ideas.md`, urgent, 2026-10-23), so there are no cron runs to read and
  the modal CLI has nothing to authenticate against.

## Work

The second half of slice 5 of `docs/product/graph-quality.md`: the re-judgment
trigger the design doc named in its own words as "the natural next day of work
here". Taken under the charter's fallback, an `accepted` ledger entry
("Knowledge graph upgraded to industry standard") that no sprint has picked up,
because the stale sprint's own items all close with a hand this seat does not
have.

## What this run found that the design did not

The design asked for a trigger picking "claims whose newest opinion predates
the current prompt sha". Two things that sentence assumes are false of the
data, and both of them cost money rather than correctness.

**A claim's newest opinion is not always a row.** An edge is written when the
judge found a relation, so a pass that read a claim and found nothing leaves
nothing behind. Reading `claim_links`, that claim is indistinguishable from one
the current prompt has never seen, so the trigger re-selects it every run and
pays for a model call every time, forever. The pass is therefore the unit
rather than the finding.

**And the sha to compare is the prompt's, not `method`'s.** `method` is
`model@sha` and the model is whichever provider answered. A trigger keyed on it
re-judges the whole corpus the first time Groq answers for Moonshot, and again
when Moonshot comes back, and neither pass is a change of mind.

Both are one-word edits away from being wrong, both pass every other test in
the repository, and both are now pinned by a test.

## Scope held, and where the line is

`rejudge_budget` gives re-judgment the slots the fresh queue leaves and never
one it wanted, inside the `max_claims` and the dollar cap the run already had.
The fresh queue is 2,000-odd deep, so the trigger returns nothing today: this
ships correct and latent, the same way slice 5's read path did.

The audit was not touched. `tools/graph_audit.py` now has a blind spot it did
not have yesterday, because its numbers are ambiguous across two judges, and
that is a ledger entry rather than a widening of this diff.
