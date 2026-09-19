# Turn caps — the standing right-sizing methodology

**Enforced at:** prompts/exo-agent.md, the monthly cap re-derivation and
"Check the register before you ship".

Owner-directed (2026-09-18), after a day on which six agent runs failed
and every one of them was a turn-cap collision. Caps had been set by
guess, then raised by reaction, and both reactive raises were outgrown
by the seat's own next runs. This page replaces guessing with a
measurement. It is the ExO agent's to maintain (charter §6).

The short version: **a cap is a tripwire, not a budget.** Turns cost
nothing unless a run uses them, so a cap that is too high costs the org
nothing and a cap that is too low costs it a whole run. Size caps so
that hitting one is real news.

## The rule

> **A seat's cap is at least twice its highest observed turn count,
> rounded up to the next 50, with a floor of 100.**

Three clauses make it work in practice.

1. **A run that hit its cap is a lower bound, not a measurement.** When
   a run dies at `error_max_turns`, the log records the cap plus one,
   not the work's real demand. That number is censored. Use it to set a
   floor, mark the seat as unmeasured in the table below, and re-derive
   the cap from the first run that finishes freely.
2. **A seat that has never run has no measurement at all.** Give it the
   cap of its nearest twin, mark the row provisional, and replace it
   after the seat's first free-running run.
3. **Duties growing is a re-measurement trigger.** The two seats that
   broke first are the two whose work grew after their caps were set:
   frontend gained Playwright screenshots, security gained a whole
   repository to sweep. A charter edit that adds work to a seat should
   be followed by a cap check, not by waiting for the failure.

## When this gets reviewed

- **Monthly**, by the ExO agent, in its first run of each month. Re-run
  the measurement below, refresh the table, queue any change.
- **Immediately**, in the same run, whenever any cap is hit by any seat.
  A cap hit is evidence about the cap.
- **On duty growth**, whenever a charter edit gives a seat more to do.

Never set a cap from a feeling about how much work a seat "should"
need. The commands below take about a minute.

## How to measure

All four commands were run against this repository on 2026-09-18 and
produce the output shown in the table.

**1. Turn demand for one seat, newest run first.** `num_turns` is in the
action's final result block; `--max-turns` is echoed in the run's
`CLAUDE_ARGS`.

```bash
gh run list --workflow=agent-<seat>.yml --limit 50 \
  --json databaseId,conclusion \
  --jq '.[] | select(.conclusion!="cancelled" and .conclusion!="") | .databaseId' \
| while read -r id; do
    log=$(gh run view "$id" --log 2>/dev/null)
    printf '%s\t%s\t%s\n' "$id" \
      "$(printf '%s' "$log" | grep -oE '"num_turns": *[0-9]+' | tail -1 | grep -oE '[0-9]+')" \
      "$(printf '%s' "$log" | grep -oE '\-\-max-turns [0-9]+'  | head -1 | grep -oE '[0-9]+')"
  done
```

**2. Every cap currently in force.** Read the workflows, never this
page, when you need the truth.

```bash
grep -HoE '\-\-max-turns [0-9]+' .github/workflows/agent-*.yml
```

**3. Which flavor of cap collision a failure was.** The two flavors need
different responses, and the log tells them apart in one line.

```bash
gh run view <run-id> --log-failed \
  | grep -E '"subtype"|"num_turns"|"is_error"|exceeding the configured'
```

- `"subtype": "error_max_turns"` and `num_turns` exactly one above the
  cap: **hard starvation.** The run was killed mid-work. Whatever it had
  not pushed is gone.
- `"subtype": "success"`, `"is_error": false`, and an
  `exceeding the configured maximum` error: **false failure.** The run
  finished its job and the action failed the job afterwards on a
  post-hoc comparison. The work shipped; only the conclusion is red.

**4. Whether a failed run shipped anything.** Take the run's window and
look for commits, because the conclusion will not tell you (incident 8).

```bash
gh run view <run-id> --json createdAt,updatedAt --jq '[.createdAt,.updatedAt]|@tsv'
git log --all --since="<createdAt>" --until="<updatedAt>" --format='%cI %h %s'
```

## The table, re-measured 2026-09-19 04:10 UTC

Peak is the highest `num_turns` on record for the seat. Required is
twice that, rounded up to the next 50, floor 100.

| Seat | Runs measured | Peak turns | Cap in force | Required | Verdict |
|---|---|---|---|---|---|
| frontend | 8 | 286 | 600 | 600 | ok |
| pm | 8 | 141 (censored) | 300 | 300 | ok, and still censored |
| security | 2 | 108 | 250 | 250 | ok |
| engineer | 7 | 75 | 200 | 150 | ok |
| sales | 5 | 76 | 160 | 160 | ok, no headroom |
| skill | 3 | 67 | 180 | 150 | ok |
| research | 1 | 54 | 180 | 120 | ok, first measurement |
| writer | 2 | 53 | 150 | 110 | ok, first measurement |
| exo | 4 | 93 | 200 | 200 | ok, no headroom |
| market | 3 | 47 | 160 | 100 | ok |
| okr | 1 | 33 | 160 | 100 | ok |
| finance | 1 | 29 | 120 | 100 | ok, first measurement |

**Every cap in the org now clears the rule.** The three that were short
on 2026-09-18 (frontend 400, pm 250, security 200) were applied by the
chair and verified against the workflow files in this run, so item 2 of
pending-workflow-changes.md is deleted as applied.

Notes on the rows that need them.

- **The three provisional rows are now measured.** research ran 54
  (35416201317), finance 29 (35410872874), writer 53 and 51 (35417517511
  and 35419120149). All three inherited caps that turned out generous,
  which is the right direction for a guess to be wrong in. The writer
  seat is new with ADR-28 and appears in this table for the first time.
- **frontend's peak is now a stale high, and this is the interesting
  row.** The 286 was set on 2026-09-18 under a cap that failed it. Since
  then the seat has run 175, 141, 147, 126, and, once containerized, 12
  and 86. Chromium is baked into the image, so the turns that used to go
  to installing a browser now go to judgment, which is exactly the fix
  incident 4 asked for. Keep 600 anyway: a cap is a ceiling, not a
  budget, it costs nothing unspent, and one measurement of a new
  environment is not a trend. Re-measure after four containerized runs,
  and if the post-container peak holds under 150, the honest cap is 300.
- **pm** is still the only censored number in the table. Its 141 is a run
  that died at a 140 cap, so real demand is unknown and at least 141.
  The 300 is a lower bound until a pm run finishes freely above 141.
- **exo and sales have no headroom.** Both sit exactly at their required
  figure, so the next run that grows either seat's duties puts it short
  the same day. This seat's own duties grew twice this week.
- **Containerization changes what a turn costs, not how many are
  needed.** Two seats (frontend, engineer) now run in the prebaked
  image. Watch for the peak moving in either direction as the rest
  migrate, and treat the migration as duty growth that triggers
  re-measurement, per the rule above.
- Job timeouts were re-checked against the required caps at roughly nine
  turns per minute. Every seat's `timeout-minutes` clears its required
  cap, so no timeout change is needed.

## Who applies a cap change

Not the seats, for now. No agent run can push `.github/workflows/`,
because `GITHUB_TOKEN` cannot hold the `workflow` scope (incident 12,
re-probed and rejected again on 2026-09-19). Cap changes are written out
in [pending-workflow-changes.md](pending-workflow-changes.md) and applied
by the chair or the owner. This is the standing constraint on the whole
practice: the org can measure its caps in a minute and cannot fix them
at all without a human hand.

That constraint lifts with ADR-27's GitHub App. See
[app-identity-handover.md](app-identity-handover.md): on the day the
App's private key lands, a cap change becomes an ordinary PR from the
seat that measured it, and "an agent raises its own cap and the owner
merges it" is the test that the handover actually worked.
