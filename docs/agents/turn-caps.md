# Turn caps — the standing right-sizing methodology

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

## The table, measured 2026-09-18 20:50 UTC

Peak is the highest `num_turns` on record for the seat. Required is
twice that, rounded up to the next 50, floor 100.

| Seat | Runs measured | Peak turns | Cap in force | Required | Verdict |
|---|---|---|---|---|---|
| frontend | 6 | 286 | 400 | 600 | **short** |
| pm | 8 | 141 (censored) | 250 | 300 | **short** |
| security | 1 | 108 | 200 | 250 | **short** |
| exo | 3 | 93 | 200 | 200 | ok, no headroom |
| sales | 5 | 76 | 160 | 160 | ok, no headroom |
| engineer | 6 | 73 | 200 | 150 | ok |
| skill | 3 | 67 | 180 | 150 | ok |
| market | 2 | 47 | 160 | 100 | ok |
| okr | 1 | 33 | 160 | 100 | ok |
| research | 0 | never run | 180 | provisional | unmeasured |
| finance | 0 | never run | 120 | provisional | unmeasured |

Notes on the rows that need them.

- **pm** is the only censored number in the table. Its 141 is a run that
  died at a 140 cap, so the work's real demand is unknown and at least
  141. The required figure of 300 is therefore itself a lower bound, and
  the seat should be re-measured from its next run that finishes freely.
- **frontend** holds the org's highest demand by a wide margin. Its
  286-turn run took 31 minutes, so even at 600 turns it lands near 65
  minutes, inside the 90-minute job timeout already in force.
- **exo** ran 93 turns against a 100 cap on 2026-09-18. That was a near
  miss nobody logged, and it is the reason this seat's own cap is in the
  table rather than assumed fine.
- **security** has exactly one run on record and it is the run that
  overshot. One sample is thin, so treat 250 as a starting point rather
  than a settled number.
- Job timeouts were checked against the required caps at the measured
  rate of roughly nine turns per minute. Every seat's current
  `timeout-minutes` clears its required cap, so no timeout change is
  needed alongside these.

## Who applies a cap change

Not the seats. No agent run can push `.github/workflows/`, because
`GITHUB_TOKEN` cannot hold the `workflow` scope (incident 12). Cap
changes are written out in
[pending-workflow-changes.md](pending-workflow-changes.md) and applied
by the chair or the owner. This is the standing constraint on the whole
practice: the org can measure its caps in a minute and cannot fix them
at all without a human hand.
