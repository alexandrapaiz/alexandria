# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~01:00-01:10 UTC)

**Nothing dispatched this run, and the queue holds none.** `PM_DISPATCH_ENABLED`
read directly from this run's own environment: empty, not `true`, so
section 5 is inactive regardless of what follows. Checked the rest of the
criteria anyway, because an inactive switch is not a reason to skip the
read.

Every dispatchable seat but one either has an open pull request from its
own last run right now (`engineer`, `writer`, `frontend`, all three
visibly still in progress, draft bodies still reading "filling in") or has
no evidenced trigger this pass can cite without inventing one
(`market`, `skill`, `security` last opened a pull request nineteen days
ago; `okr` six days ago; none of the four has a sprint item naming it this
week, because the real current sprint is the one stuck inside `#403` and
has not reached `main` or the board's sprint object). `research`'s own
board card already says fresh work needs the owner's word first, which is
the relay rule answering itself: naming it here instead of queuing it.

## Merge call this run: held, not Tier A/B

**`#414`** (the ExO seat's, sixth in a chain, every seat's charter file in
one diff) was read in full rather than deferred on the strength of the
prior pass's call alone. `gh pr diff --name-only`: eleven `docs/agents/*`
knowledge-surface files (Tier A) and twelve `prompts/*-agent.md` charter
files, one per seat. None of the twelve charter diffs changes a dispatch
ceiling, who may dispatch whom, or a merge-tier definition; every change
read is mechanical (the board-API read replacing the blind `gh run list`,
a shallow-clone caution, a `/tmp`-scratch caution, the `pending.md` writer
split this seat itself asked for on the board). So the amendment's
"except a change to a seat's own authority" carve-out arguably does not
bind here.

Held anyway, for three reasons: this seat's own immediately prior run
read the same diff forty minutes earlier and called it not self-mergeable,
and reversing that with no new fact is not applying the rule, it is
re-litigating it; the standard's §9 and §10 both still name "Charters
(`prompts/`)" as their own enumerated owner-only category, separately
from the authority carve-out, and nothing resolves which of the two
readings governs a routine, non-authority charter fix; and the blast
radius is every seat's next run at once, so the cost of holding one more
cycle is cheap against the cost of a wrong charter merge. Asked plainly in
`docs/sprints/pending.md` rather than guessed either way. `#414`'s own
predecessor chain (`#272`, `#331`, `#381`, `#404`, `#411`) is already
fully closed by the ExO seat itself; nothing left to close there.

## Held, not resolved — the conflict is in code, not prose

Carried unchanged: `#416` was itself superseded and closed by the
frontend seat's own `#421`, which contains the rebase this queue
previously asked for. No action needed from this seat.

## Failures (`docs/standards/pm.md` §11.7)

Two non-successes since the last standup, read off the board because
`gh run list` is blind to every agent seat's run since 2026-10-17
(confirmed again this pass: the newest 30 rows are all `checks` /
`deploy-main` merge pushes). `exo` at 2026-10-23T19:04:14Z, exit 1 at 48
of 200 turns; `pm` at 2026-10-23T19:09:06Z, exit 1 at turn 1, seven
seconds later. Both already drafted as one incident inside `#414`
(unmerged); not duplicating that entry on `main` while it sits one merge
away, to avoid the allocator collision the charter already warns about.
If `#414` is still unmerged by the next ceremony, the registration still
has to land, by whichever seat opens next.

## Run health

Fleet: the two failures above, both already triaged, nothing new since.
Cap ratio: `exo`'s run on `#414`, 155 of 200, 77.5%, over the 70% line.
`writer`'s last two runs, 140 and 113 turns: the workflow file's
`--max-turns 225` reads both under the line, but `#414` reports that
number is stale since cadence moved to host manifests, and gives the live
cap as 150, which reads both over (93% and 75%), the first a third
consecutive measurement over the line per `#414`. Could not independently
confirm 150 — this seat's token 404s against the host-manifest repo.
Reporting both readings rather than picking one.

## Delivery health (`docs/agents/delivery-health.md`, via `tools/delivery_health.py`)

**ok:** press (2026-W42, newest, caught up), site, archive. **FAILING,
unchanged:** compute / pipeline / mcp (Modal workspace disabled, `#406`
urgent, 2026-10-26 09:00 UTC deadline, owner-only); checkout (the three
Polar env vars still unset, owner-only); deploy (distill 8.0 days, ingest
7.4 days, weekly 8.2 days undeployed behind `origin/main`). **unknown:**
payments.

## Queue gauge, four numbers

1. `main`'s newest commit: the merge of `#409`, 2026-10-24T00:47:16Z,
   about fourteen minutes old at this writing. `checks.yml` fires only on
   specific paths (pipeline, digest/daily prompts, named tests,
   `skills/**`); its newest matching run is `success` from the merge of
   `#400`, and nothing since has touched one of its paths, which is why
   nothing newer shows and that is not a gap.
2. Open pull requests: 6 (`#403`, `#414`, `#419`, `#420`, `#421`, `#422`,
   this seat's own), 3 opened since the last merge to `main` (`#420`,
   `#421`, `#422`).
3. 7-day conversion: 73 merged / 100 opened (0.73).
4. Deepest open chain: 6 (`#414`), unchanged. `#403` next at 4.

No 48-hour stall; `main` moved fourteen minutes ago.

## Board

Commented on the ExO seat's own board card (`df7b4a84`) with the merge
status above, and left it in Review rather than moving it to Done, since
the code is not on `main` yet. Walked the whole board for an orphaned
item to hand a seat; the one candidate (the issue dek's widow on tablet
and desktop) already has a card, filed before this pass. Nothing else
needed a new card.

## Dispatched by the PM

None this run.
