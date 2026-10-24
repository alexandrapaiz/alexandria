# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, cron standup (~11:07 UTC)

**Trigger.** This seat's own cron, the host's clock rather than a GitHub
Actions schedule (every `agent-*.yml` schedule block was removed by PR #334,
HQ decision 056 — see `docs/agents/org-chart.md`). Today is Saturday, so per
charter §0 this is a standup run: section 4 alone, no ceremony.

**Own last run was still open, checked first, and it was.** This seat's own
`#434` (a message-driven pass, opened ~06:54 UTC) was still open, writing
into this file and `docs/sprints/pending.md` at the same anchors this
standup needs. Built on it by fast-forward merge rather than branching from
main (`git log --oneline origin/alexandria-pm/2026-10-24-message-merge-rule
^HEAD` printed nothing, proving containment), and `#434` is closed as
superseded by this run's own PR, `#437`. **Chain: `#397` to `#399` to
`#401` to `#403` to `#427` to `#429` to `#432` to `#434` to this one, depth
9. This seat is blocked on merges**, the deepest open chain in the company
by a wide margin.

**One entry proposed, dispatch still off.** `PM_DISPATCH_ENABLED` is unset
in this run's own environment, so nothing below fires; it is written for
the owner or a chair to copy.

### 1. skill — sprint item 1's before/after delta still has not moved, 19 days silent, 3 working days left on the sprint's own fallback clock

**Trigger.** `docs/sprints/sprint-2026-10-19.md` item 1, carried from the
Regroom, serves sellable condition 4. The skill seat's last pull request of
any kind is `#200`, 2026-10-05 — 19 days before this run — and it has not
run once since the five-day host outage ended on 2026-10-23. Item 2
(frontend) is chained behind it. Carried forward unchanged from the prior
pass's proposal (`#434`'s dispatch-queue.md, ~06:30 UTC); nothing has moved
since.

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

**Not escalated past a proposal.** The sprint's own item 5 says this
escalates "the moment one is missed," not before. The deadline is not
missed yet, so this stays one proposed entry rather than a louder claim.

## Other open pull requests, named rather than dispatched against

- **`#414`** (ExO, depth 6) — held on the §16/§21 Tier question the prior
  pass asked the owner directly (`docs/sprints/pending.md`, ~06:30 UTC).
  Not a dispatch candidate; it is a pull request waiting on a decision, not
  on a seat, and ExO is never dispatchable per charter §5 in any case.
- **`#430`** (writer) — open draft, ~9.3 hours old. Everything its own
  draft note names (grade, prompt diff, gate extension, suite) was verified
  independently by the prior pass; nothing owed but the writer's own
  `gh pr ready`. Hard stop holds regardless: last pull request still open.
- **`#435`** (frontend) — open draft, ~4.3 hours old, the catalog
  shelf-assignment verification for sprint item 2. Hard stop holds.
- **`#436`** (engineer) — open draft, opened this same cron tick, depth 3
  (`#426` to `#431` to this one), superseding its own `#431`. Hard stop
  holds.
- **market, security** — both last opened a pull request 2026-10-05, 19
  days ago, same as skill, but neither has a sprint item or any other
  evidenced trigger pointing at them this week (confirmed again this run
  in `docs/sprints/pending.md`). Named rather than queued, per the no-
  invented-trigger rule: this is a cadence question for the ExO's weekly
  re-derivation, not a standup dispatch.

## Run health

**Fleet.** `gh run list --limit 30` shows zero `agent-*.yml` runs since
2026-10-17 — expected, not a failure: every seat's schedule moved off
GitHub Actions that day (PR #334, HQ decision 056), and `checks`/
`deploy-main` are the only workflows still live there. Both green: `checks`
success at 06:53:00Z (the `#433` merge), `deploy-main` success at the same
push.

Read from the board instead (`GET /api/board/alexandria`, the receipt
charter §1f now points at): 25 most recent rows, newest ending
06:56:57Z (this seat's own prior pass). Nothing has run on the board since
then except this cron tick's own in-flight runs (this one and the
engineer's, `#436`), which are not yet in the record. **No new
non-success since the last check.** The two exit-1 runs in the window
(engineer, 01:53:49Z, 88 turns; writer, 01:46:06Z, 126 turns) were already
found and triaged by the prior pass: not in `docs/agents/incidents.md`,
classified configuration/unknown for lack of a reachable log, both seats
opened a fresh draft on related scope within three minutes so no work
reads as lost. Not re-filed here; nothing new to add.

**Cap ratio** (`.github/workflows/agent-*.yml` `--max-turns`, against the
board's `turns` field for the same 25-row window): `exo` ran 155 of a
200-turn cap, **77.5%**, the one seat above the 70% line this window.
Everyone else stayed under it: `pm` 198/300 (66%) was the next highest;
`engineer` 133/200 (66.5%); `writer` 126/225 (56%); `frontend` 197/600
(33%). No run hit a cap. Reporting the ratio only, per charter: not
proposing a new number.

## Delivery health

Recomputed live this run (`tools/delivery_health.py`), same picture as the
prior pass: **ok** — press (2026-W42, kimi-k2.6), site (3 issues published,
newest 2026-W42), archive. **FAILING** — compute, pipeline, mcp (all one
cause: Modal workspace `ac-5DsaR3hWSUxqyNoGYiowja` is disabled, which takes
the MCP server and every pipeline cron down with it); checkout (the
pricing page renders no checkout link — `POLAR_CHECKOUT_TRIAL`,
`_MONTHLY`, `_LIFETIME` all unset). **unknown** — payments
(`payment_exceptions` table missing, one schema command away, itself
blocked by the same Modal outage); deploy (drift cannot be dated from this
checkout). Unchanged from the prior pass; no new surface went red.

## Queue gauge, four numbers

1. **`main`'s age and checks.** Newest commit `6ddc90b` (the `#433` merge),
   2026-10-24T06:52:58Z, about 4 hours 15 minutes old at this writing.
   Newest `checks.yml` run on `main`: success, same timestamp.
2. **Open pull requests: 5** (`#414`, `#430`, `#435`, `#436`, this seat's
   own `#437`). **3 opened since the last merge** to `main` (`#435`,
   `#436`, `#437`, all after 06:52:58Z).
3. **7-day conversion: 79 merged / 114 opened (0.69).**
4. **Deepest open chain: 9**, this seat's own `#437` — unchanged in kind
   from every pass tonight, one link deeper each time, still the deepest
   in the company, past `#414`'s 6.

No 48-hour stall; `main` moved 4 hours 15 minutes ago. This is not the
deadlocked shape the threshold describes, so the gauge stays ordinary
reporting rather than the top line.

## GitHub Projects board

Not checked this run: `PROJECTS_TOKEN` is absent from this run's
environment. Said plainly rather than left out.

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` unset.
