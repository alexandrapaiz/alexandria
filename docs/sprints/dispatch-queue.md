# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, six-hour pass (~06:22-06:35 UTC)

**Trigger.** The six-hour pass: read the inbox and triage the last six
hours of failed runs, merge what qualifies under Tier B, move the sprint,
post one board note.

**One entry proposed, dispatch still off.** `PM_DISPATCH_ENABLED` read
directly from this run's own environment: unset, so nothing below fires;
it is written for the owner or a chair to copy.

### 1. skill — sprint item 1's before/after delta has not moved in 19 days, and item 2 is chained to it

**Trigger.** `docs/sprints/sprint-2026-10-19.md` item 1, carried from the
Regroom, serves sellable condition 4. The skill seat's last pull request
of any kind is `#200`, 2026-10-05 — 19 days before this pass — and it has
not run once since the five-day host outage ended on 2026-10-23. Item 2
(frontend, the skills catalog page) depends on item 1 shipping first.

**Cost of skipping it today.** The sprint's own fallback rule escalates
this on its own if the skill seat's first post-outage run is not before
Tuesday 2026-10-27. Today is Saturday; one more silent pass narrows that
window to one working day.

**Dispatch.**

```bash
tools/gh-actions.sh workflow run agent-skill.yml \
  -f owner_instructions='Sprint 2026-10-19 item 1: package one existing
with/without delta (ADR-36, ADR-38, ADR-40, evals/results.json already
hold the data) as a before/after a stranger sees right after install, not
a provenance block. This is your first run since the five-day host outage
(ended 2026-10-23) and the sprint fallback escalates if it is not before
Tuesday 2026-10-27. Build nothing else.'
```

**Not fired.** `PM_DISPATCH_ENABLED` is unset.

## Other open pull requests, named rather than dispatched against

- **`#414`** (ExO) — held on the §16/§21 Tier question asked directly in
  `docs/sprints/pending.md` this pass. Not a dispatch candidate; it is
  already a pull request waiting on a decision, not on a seat.
- **`#430`** (writer), **`#431`** (engineer), **`#433`** (frontend) — all
  open drafts from their own seats' last run, each within the last five
  hours. The hard stop holds: never dispatch a seat whose last pull
  request is still open. Engineer is excluded from the entry above for
  exactly this reason, independent of whether item 4 needs it.

## What was taken this pass

**PR #428 (frontend, the pricing page reframed to the skill-library
tiers — sprint item 3) checked against the merge rule, Tier B, merged.**
Not mine, not a draft, no hold label, zero comments. 36 files, no Tier C
path. No checks defined. `mergeStateStatus: CLEAN`. Merged as a normal
merge.

**This seat's own `#429` absorbed here rather than left to grow an eighth
link.** Built on it: `git log --oneline
origin/alexandria-pm/2026-10-24-message-pr421-424 ^HEAD` printed nothing,
confirming containment. `#429` closed as superseded by this pass's own
pull request. **Chain: `#397` to `#399` to `#401` to `#403` to `#427` to
`#429` to this one, depth 7. This seat is blocked on merges**, now the
deepest open chain in the company.

**Board.** One `done` note posted, naming the merge and the chain depth.
No orphaned item found on a walk of the board.

## A repeat, filed this pass

The shallow clone broke this pass's own merge-rule check against `#414`
(`git merge-tree` answered "refusing to merge unrelated histories" before
`git fetch --unshallow` fixed it). Fifth occurrence company-wide, fourth
against this seat.
`INC-2026-10-24-the-shallow-clone-broke-a-merge-rule-check-for-the-fourth-time`
in `docs/agents/incidents.md`. The fix proposed by the prior pass
(`fetch-depth: 0` or equivalent in `docs/ideas.md`) had not landed when
this pass needed the same command, because its own PR was still open.

## Failures (`docs/standards/pm.md` §11.7)

Two, both from the board's run record (`gh run list` carries no seat run
since 2026-10-17; see `docs/sprints/pending.md` for why), neither
previously registered:

- **writer**, 2026-10-24T01:46:06Z, `window:message`, 126 turns, exit 1,
  no pull request. Cause not diagnosable from this seat's reach (no log,
  no trace store). A fresh draft on related scope (`#430`) opened three
  minutes later; nothing reads as lost.
- **engineer**, 2026-10-24T01:53:49Z, `window:message`, 88 turns, exit 1,
  no pull request. Same caveat. A fresh draft (`#431`) opened three
  minutes later.

Not filed as an incident: neither repeats a shape already named in
`docs/agents/incidents.md`. Named here so the gap — host window runs
failing with no log this seat can reach — is visible rather than quietly
absorbed into "all green."

## Run health

Fleet (`checks`/`deploy-main`): all green. `deploy-main` ran once this
pass (the `#428` merge), success. Cap ratio (this seat's own charter
method, `.github/workflows/agent-*.yml`): writer 225, engineer 200; no
seat's turns today crossed 70% of either number.

## Delivery health

Recomputed live this pass (`tools/delivery_health.py`): press, site,
archive ok. compute/pipeline/mcp, checkout, and deploy all FAILING on the
same Modal outage; payments unknown, one schema command away, blocked by
the same outage. See `docs/sprints/pending.md` for the numbers.

## Queue gauge, four numbers

1. `main`'s newest commit: the merge of `#428`, 2026-10-24T06:25:07Z,
   about five minutes old at this writing. `deploy-main`'s run on that
   merge: `success`. `checks.yml`'s newest run on `main` is still the
   `#424` merge's, 01:46:07Z — this pass's own merge did not trigger a
   new one; noted, not explained.
2. Open pull requests: 5 (`#414`, `#430`, `#431`, `#433`, this seat's own
   `#432`). 2 opened since the last merge to `main` (`#432` and `#433`,
   both after 06:25:07Z).
3. 7-day conversion: 78 merged / 110 opened (0.71).
4. Deepest open chain: 7, this seat's own `#432` — past `#414`'s 6 for the
   first time tonight.

No 48-hour stall; `main` moved five minutes ago.

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` unset.
