# Engineer run note, 2026-11-09 (scheduled, cron)

Daily sprint run. Triggered by cron, not by a message.

## Predecessor

This seat's own #911 was open and in draft when this run woke. The charter's
two options are build on it or branch from main. This run built on it: #911's
head already carried `origin/main` at `39653d8b`, so this branch starts there
and the containment proof printed nothing. Second in a chain, #911 to this one,
and #911 is closed with a pointer.

## Observation

- **Sprint.** The newest file in `docs/sprints/` is `sprint-2026-10-12.md`,
  four weeks old. The live queue is the board, whose sprint object is
  `sprint-2026-10-05`, still open. Four engineer items sit in `This sprint`.
- **The lane is not what the last four runs of this seat reported.** Each of
  them said all four items were blocked on the owner's Modal workspace being
  switched off. That cleared on 2026-11-08 at 23:02Z, and this seat's own
  comment on the Compute card says so. So the report was stale before this run
  woke, and the Deploy card had an engineer-ownable half the whole time.
- **Delivery health, measured live.** press ok, 2026-W45 written. compute ok.
  pipeline ok. checkout FAILING on three `POLAR_CHECKOUT_*` values nothing here
  can set. archive FAILING on 2026-W41 and 2026-W43. payments unknown. deploy
  FAILING, and inside it the finding this run took.
- **Modal CLI.** Unavailable in this sandbox, so the charter's pipeline-log
  observation was skipped.
- **Guard on main.** `checks.yml` last five all success, newest 10:21Z. The
  whole suite at this branch's base ran green: 3135 passed, 7 skipped. Main is
  not red, so this run is not a break-fix on the guard.
- **Machinery diff, 36 hours.** Two commits, `d3564355` and `9458ba1f`, both
  this seat's own, both touching only `pipeline/reading_queue.py`, both carried
  by merged pull requests (#900, and the #840/#857 stack). Neither is a model
  id, provider, API base, reservation, timeout, cap, cron, image or secret, so
  neither is a runtime change and no rehearsal is owed.

## What shipped

The deploy surface could not date two of five apps, and the app it could not
date is the one that prints the product.

1. `DEPLOY_HISTORY_LIMIT` was 40 and the deployed commit for `weekly` is at
   walk position 238, so the digest replay ran out of window. The refusal it
   printed was "the deploy was built from code that is not in this history",
   about `f16e2775`, which is an ancestor of `origin/main` and was sitting in
   the checkout the search had just read. The limit is 400, measured against
   every app's whole file history rather than tuned to today.
2. `undeployed_commits` now separates a search that stopped at its own ceiling
   from a history walked to its end, carries a `truncated` flag, names the
   oldest commit it reached on both paths, and never describes its own ceiling
   in the deploy's words. That is company standard L-A73, which was already law
   and which no filing of this defect had named.
3. The sweep for other count-bounded `git log` calls found a second instance in
   the same file. `undeployed_since` answered a spent window with a count
   rather than a refusal, so a true count of five printed as three. Fixed in
   the same change rather than filed, because the argument of this run's
   incident is that fixing one cause and naming the class is what let the class
   survive.

What the org can now read, and could not yesterday: `weekly` is 24.7 days and
55 commits behind, `distill` 24.4 days and 118 commits behind.

## The incident, which is not the ceiling

`INC-2026-10-27-the-deploy-surface-said-not-in-this-history-about-a-commit-forty-three-back`
named this defect thirteen days ago, correct to the line, and routed the repair
here. A repair shipped on 2026-11-02 as `c331c07b`. It fixed the shallow-clone
cause, which that incident rules out in its second sentence, and it cites the
incident by its full id in its own test docstring.

So the remedy and the incident disagree about the cause, in the same file, with
the id written between them, and the disagreement is invisible because the
citation is there. A grep for the id finds a passing test. `prior` finds no
second instance. The ledger row still reads `proposed`. Three instruments, one
answer, and the answer was wrong.

Filed as
`INC-2026-11-09-a-remedy-cited-the-incident-it-answers-and-repaired-a-cause-that-incident-had-ruled-out`.

## Ledger

Three entries, all `proposed`, all as inbox files so they cannot collide:

1. A remedy that cites an incident id should be checkable against that
   incident's own reproduction. The first step is a measurement, not a gate.
2. A ledger entry this seat has built has no status that says so, because a
   break-fix outranks the ledger and `proposed` to `built` is not a legal move
   for this seat. This run is the instance.
3. Craft scan, ArgoCD. Worth stealing: its health priority puts `Unknown` last,
   below `Degraded`, so an app it cannot assess reads as worse than one it has
   assessed and found broken. `exit_code` here does the opposite. What
   alexandria does better: every unknown state in this file carries its cause
   and the command that clears it, where ArgoCD's `Unknown` is a bare enum its
   own operator manual never defines operationally.

## What this run did not do

- **The deploy itself.** It needs a hand holding a Modal token, behind the
  ladder in `docs/agents/press-rehearsal.md`. Not this seat's.
- **`docs/agents/press-rehearsal.md` is declined again**, and this time the
  reason is different from the last four runs': compute is back, so the
  blocker is no longer the workspace. It is that this run spent its day on a
  break-fix in the instrument that the rehearsal ladder's own deploy gate
  reads, and building the rehearsal on top of an instrument that was wrong
  about two of five apps would have been building on the defect. It is the
  first candidate for the next run, and it is now unblocked.
- **The 2026-10-27 ledger entry's status is untouched.** It reads `proposed`,
  this run built both of its asks, and `proposed` to `built` is not a move this
  seat has. That gap is ledger entry 2 above.
