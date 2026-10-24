# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message wake (~11:40 UTC)

**Trigger.** The event bus woke this seat on engineer's PR #436 (scheduled
run) opening, with a standing note asking this seat to read it against the
merge rule and to decide the disposition of two idle drafts, #430 (writer)
and #435 (frontend), each with no live run behind it, naming the owning
seat in whatever this run does.

**Own last run may still be open, checked first, and it was.** This seat's
own `#437` (the cron standup, opened ~11:07 UTC) was still open, writing
into this file and `docs/sprints/pending.md` at the same anchors this pass
needs. Built on it directly rather than branching from `main`
(`git log --oneline origin/alexandria-pm/2026-10-24-scheduled ^HEAD`
printed nothing, proving containment), and `#437` is closed as superseded
by this run's own PR, `#438`. **Chain: `#397` to `#399` to `#401` to
`#403` to `#427` to `#429` to `#432` to `#434` to `#437` to this one,
depth 10.**

That number carries a caveat the chain alone does not. `docs/standards/
pm.md` §10 and §11.6 both say the queue file and the standup PR are
**Tier A** — a knowledge surface this seat merges itself once the scope
check clears — and this PR's diff (`docs/sprints/`, a grooming edit to
`docs/ideas.md`, `docs/agents/incidents.md`) is exactly that surface. This
run's own operating instructions said "never merge your own PR" for this
session, so the gate holding this chain open right now is that instruction,
not the owner's queue and not an absence of authority. Naming both rather
than letting "depth 10" read as a bottleneck nobody can open.

**PR #436 (engineer, scheduled run, the register-conflict instruments)
checked against Tier B and merged** at `11:34:49Z`. Full reasoning in
`docs/sprints/pending.md`'s entry for this pass. One piece of evidence
worth surfacing here: merging it produced a real tail-append conflict on
this branch's own `docs/ideas.md` and `docs/agents/incidents.md`, and the
first hand-resolution attempt dropped a line the same way `INC-2026-10-24-
a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`
describes, caught by `tools/resolve_register_conflict.py --check` before
push and fixed. The new instrument works; it does not make the underlying
anchor safe to resolve by eye, which is the finding underneath it.

**One entry proposed, dispatch still off.** `PM_DISPATCH_ENABLED` is unset
in this run's own environment, so nothing below fires; it is written for
the owner or a chair to copy.

### 1. skill — sprint item 1's before/after delta still has not moved, 19 days silent, 2 working days left on the sprint's own fallback clock

**Trigger.** `docs/sprints/sprint-2026-10-19.md` item 1, carried from the
Regroom, serves sellable condition 4. The skill seat's last pull request of
any kind is `#200`, 2026-10-05 — 19 days before this run — and it has not
run once since the five-day host outage ended on 2026-10-23. Item 2
(frontend) is chained behind it. Carried forward unchanged for the third
pass (`#434`'s and `#437`'s dispatch-queue.md both carried the identical
entry); nothing has moved since the first proposal at ~06:30 UTC.

**Cost of skipping it today.** The sprint's own fallback rule escalates
this on its own if the skill seat's first post-outage run is not before
Tuesday 2026-10-27. Today is Saturday; one more silent day leaves two
working days (Sunday, Monday) before the deadline.

**Dispatch.**

```bash
gh workflow run agent-skill.yml \
  -f owner_instructions='Sprint 2026-10-19 item 1: package one existing
with/without delta (ADR-36, ADR-38, ADR-40, evals/results.json already
hold the data) as a before/after a stranger sees right after install, not
a provenance block. This is your first run since the five-day host outage
(ended 2026-10-23), and the sprint fallback escalates if it is not before
Tuesday 2026-10-27. Build nothing else.'
```

**Not fired.** `PM_DISPATCH_ENABLED` is unset.

**Not escalated past a proposal.** The deadline is not missed yet, so this
stays one proposed entry rather than a louder claim.

## Other open pull requests, named rather than dispatched against

- **`#414`** (ExO, depth 6) — held on the owner's Tier question from the
  06:30 UTC pass. Not a dispatch candidate; ExO is never dispatchable per
  charter §5 in any case.
- **`#430`** (writer) — open draft, ~9.9 hours old. Read off its diff this
  pass (unchanged from the 06:55 UTC pass's own verification): nothing
  outstanding but the writer's own `gh pr ready`. Named for the writer
  seat on `docs/sprints/pending.md`. Hard stop holds regardless: last pull
  request still open.
- **`#435`** (frontend) — open draft, ~4.8 hours old, the catalog
  shelf-assignment fix for sprint item 2. Read off its diff for the first
  time this pass: nothing outstanding but the frontend seat's own `gh pr
  ready`. Named for the frontend seat on `docs/sprints/pending.md`. Hard
  stop holds.
- **`#439`** (engineer) — opened four minutes ago, mid-run ("filling in"
  stub title), not yet assessable. Not an idle draft; named for the count
  only.
- **market, security** — both last opened a pull request 2026-10-05, 19
  days ago, same as skill, but neither has a sprint item or any other
  evidenced trigger pointing at them this week. Named rather than queued,
  per the no-invented-trigger rule.

## Run health

**Fleet.** `gh run list --limit 30` shows zero `agent-*.yml` runs since
2026-10-17, as expected (schedules moved off GitHub Actions that day).
Read live from the board this pass (`BOARD_API_URL`/`BOARD_RUNTIME_TOKEN`
are present in this run's environment, unlike the prior two passes today
— worth a note, since §14's board check has been reading as unavailable
on a stale `PROJECTS_TOKEN` check rather than the current board vars):
`python3 tools/board.py show` lists the engineer's `#436` run (11:28:06,
exit 0) and this seat's own `#437` run (11:14:35, exit 0) as the two
newest, both success. **No new non-success since the last check.**

**Cap ratio.** Unchanged from the 11:07 UTC pass (same 25-row window, no
new runs posted besides the two successes above): `exo` at 155/200
(77.5%) remains the one seat over 70%. Not re-measured this pass since no
new run entered the window.

## Delivery health

Not recomputed this pass; unchanged from the 11:07 UTC pass is the
reasonable assumption since nothing in this pass's diff touches the
press, the site, or the MCP server, and no new Modal or Polar state has
been reported. For the record as of that pass: **ok** — press
(2026-W42), site, archive. **FAILING** — compute, pipeline, mcp (Modal
workspace disabled); checkout (no Polar env vars). **unknown** —
payments, deploy.

## Queue gauge, four numbers

1. **`main`'s age and checks.** Newest commit `b7e76e5a` (this pass's own
   `#436` merge), `2026-10-24T11:34:49Z`, a few minutes old at this
   writing. `checks.yml` has not yet run against this tip — the newest
   recorded run is still `6ddc90b` (the prior merge, success at
   06:53:00Z). Said plainly rather than assumed green.
2. **Open pull requests: 5** (`#414`, `#430`, `#435`, `#439`, this seat's
   own `#438`). **1 opened after the last merge** (`#439`, 11:36:37Z,
   two minutes after `#436` landed); `#438` was opened 13 seconds before
   the merge timestamp and is counted with the pre-merge queue.
3. **7-day conversion: 80 merged / 116 opened (0.69).**
4. **Deepest open chain: 10**, this seat's own `#438` — the Tier A/
   self-merge caveat above is what actually bounds it, not the owner's
   queue. Past that, `#414`'s 6 is the next deepest.

No 48-hour stall; `main` moved minutes ago. Ordinary reporting, not the
headline.

## GitHub Projects board

Superseded by the live board above; the old `PROJECTS_TOKEN` check this
line used to run is for the retired GitHub Projects integration.

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` unset.
