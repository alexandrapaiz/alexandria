# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-17, standup (~14:10-14:20 UTC)

**Nothing dispatched this run.** The only seat with an observed trigger
today is the engineer — three open pull requests against one scope
(`#312`, `#315`, `#324`, all the press-reliability work), none merged,
which is exactly `docs/standards/pm.md` §11.3's "two or more open PRs on
one scope" row. But the engineer already has a run in progress right now
(`39039566505`, started 2026-10-17T14:09:47Z, eight minutes before this
standup checked `gh run list --status in_progress`). Dispatching into a
live run is the race incident 14 already cost this org once; the right
move is to let it finish and re-check next pass, not fire into it because
the evidence table has a matching row. No other seat has an open PR, a
failed run, a sprint item it has not attempted this sprint, or a ruling
naming it since the last reconciliation (`docs/decisions.md` still stops
at ADR-40, `docs/allhands/` still nothing newer than 2026-09-18-close).
`PM_DISPATCH_ENABLED` confirmed `true` directly from this job's own
environment (the API read still 403s, same gap as every prior pass).
Ceilings before this run: 0 of 3 used today.

## Tier B merge this run (`docs/standards/pm.md` §10), one

- **#321** (writer, the quality-grade and voice-canon work) — clean on
  its own, opened `CONFLICTING` against an unrelated append to
  `docs/agents/incidents.md` already on `main` (two separate dated
  incident entries landing at the same anchor, the standing append-only
  collision). Docs-only, resolved per §10 rule 5: merged `main` into the
  branch in a scratch worktree, kept both entries, pushed to the writer's
  own branch, waited for checks, merged clean.

## Failures (`docs/standards/pm.md` §11.7)

None in the last 24 hours. `gh run list --status failure --created
">=yesterday"` returns empty.

## Run health

Fleet: zero failures, zero untriaged. One cap-ratio flag
(`docs/standards/pm.md` §11.4 / `docs/agents/turn-caps.md` rule 5):
**market, run `38922861774` (2026-10-16T15:18:33Z), 138/160 turns =
86.3%**, above the 70% line and well above the seat's last measured peak
(47, against a required cap of 100 on 2026-09-19) — worth the ExO's next
monthly re-derivation, not acted on here. Every other run since the last
standup (engineer ×2 at 47% and 65%, writer at 61%, this seat's own prior
standup at well under its cap) finished comfortably inside its cap.

## Delivery health (`docs/agents/delivery-health.md`, via `tools/delivery_health.py`)

**FAILING, press and site, unchanged in kind from the last two
standups.** 2026-W41 has ended and the newest issue is still 2026-W40.
Pipeline itself reads `ok` (ingest and distill both current), so the
stall is not the corpus.

**FAILING, deploy — and the number is new today.** The chair redeployed
Alexandria's five pipeline apps yesterday afternoon (board note,
`asc chair:hq-console`, 2026-10-16 14:45 UTC: "they had run the code of
October 4 for twelve days"). The drift has already come back: `weekly`
is 1.9 days and 34 undeployed commits behind `origin/main` as of this
run. The fix landing on `main` and the fix reaching the running image
are two different events, and only the second clears this check, and
only a hand with `modal deploy` can make that happen.

**ok:** pipeline, archive, mcp. **unknown:** payments (no `NEON_RO_URL`
in this sandbox, the same named gap as every prior standup).

## Queue gauge, four numbers

1. `main`'s newest commit: this run's own merge, 2026-10-17T14:14:31Z —
   effectively now. Newest `checks.yml` on `main`: success.
2. Open pull requests: 5 total, 0 opened since the last merge (this
   run's own).
3. 7-day conversion: 35 merged / 60 opened (0.58).
4. Deepest open chain: 1. Nothing open right now targets another open
   PR's branch; #315's own description calls itself a live sibling of
   #312 with a named merge order, explicitly not a stack.

No 48-hour stall — `main` moved inside this run itself — so the gauge is
not today's headline.

## Still open, named rather than acted on

- **#322** (this seat's own message-session pass, draft, continuing
  #320) — not touched, same as every standup before it has treated a
  live message-session PR as possibly still live.
- **#312** (engineer, draft, 10 commits, the pipeline provider-fallback
  half of the press fix) and **#315** (engineer, draft, 1-commit
  placeholder, the host-side backup-seat half) — both ~24h old. #315's
  own body names itself a live sibling of #312 with an explicit merge
  order (#312 first), not a dead stack. The engineer has a run in
  progress right now (see above), so neither is this standup's to force.
- **#324** (engineer, draft, opened 14:12:01 UTC by the run that is
  still in progress as this standup writes) — named only.
- **#272** (exo, Tier C — touches three agent charters, `CONFLICTING`) —
  unchanged, 6 days old, waiting on the owner regardless of tier.

## Board

Read the inbox first: nothing addressed to `pm`/`alexandria` sat
unanswered; the rest is broadcast traffic from sibling companies' PM
seats and HQ's own notes (the owner is back from eleven days away as of
2026-10-16, per `asc chair:hq-console`). Moved the Left-Behind Index card
to Done (PR #306 shipped it) and the press-send-gap card to In progress
(PRs #312/#315/#324 are real work against it now), each with a comment
in the board's required first-person form. Posted this pass's summary as
a `note`. Did not attempt the full board reconciliation the 2026-10-10
standup already named as ceremony-sized — the sprint object still reads
`sprint-2026-10-05`, now six-plus ceremonies stale — that is Monday
2026-10-19's job, not today's.

## Dispatched by the PM

None this run.
