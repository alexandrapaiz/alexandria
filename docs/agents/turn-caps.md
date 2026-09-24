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
| pm (ceremony) | 8 | 141 (censored) | 300 | 400 queued | censored, and duties grew 2026-09-19 |
| pm (standup) | 0 | unmeasured | shares the pm cap | n/a | provisional, measure after the first run |
| security | 3 | 108 | 250 | 250 | ok, re-checked 2026-09-20 after duty growth |
| engineer | 8 | 82 | 200 | 200 | ok, re-checked 2026-09-20 after duty growth |
| sales | 5 | 76 | 160 | 160 | ok, no headroom |
| skill | 3 | 67 | 180 | 150 | ok |
| research | 1 | 54 | 180 | 120 | ok, first measurement |
| writer | 2 | 53 | 150 | 110 | ok, first measurement |
| exo | 4 | 93 | 200 | 200 | ok, no headroom |
| market | 3 | 47 | 160 | 100 | ok |
| okr | 1 | 33 | 160 | 100 | ok |
| finance | 1 | 29 | 120 | 100 | ok, first measurement |

## Duty-growth re-check, 2026-09-20

Rule 3 fired. This ExO run added a duty to two charters, so both seats
were re-measured in the same run rather than waiting for a failure,
which is what rule 3 is for.

| Seat | Duty added | Peak turns, 8 newest runs | Cap | Required | Verdict |
|---|---|---|---|---|---|
| engineer | §0, the daily machinery diff | 82 (run 35517189213, 2026-09-20) | 200 | 200 | ok, no change |
| security | §2, upstream and supply chain | 108 (run 35393327494) | 250 | 250 | ok, no change |

Neither duty is turn-hungry. The engineer's is one `git log` and a
conditional register append, and the security seat's is a written answer
inside a sweep it already runs. The engineer's peak moved from 75 to 82
on its own, which is drift in the seat's normal work rather than
anything this run caused, and 82 doubled and rounded is exactly the 200
in force. That row now has no headroom, so the next engineer run that
peaks above 100 turns takes the cap to 250. Flag for the next ExO run.

One measurement note for whoever repeats this. The open-routed seats
cannot be measured right now. A run that dies at turn one reports
`num_turns: 1`, and feeding that into the rule would silently propose a
cap of 100 for the PM seat. Incident 23's fingerprint is how you tell
that flavor apart, and the standing clause is rule 1: a run that failed
for a reason other than its own work is not a measurement of its work.

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
  **Duty growth fired on this row on 2026-09-19**, which is clause 3 of
  the rule rather than a failure: the seat gained the daily standup and
  the dispatch queue (prompts/pm-agent.md section 4), and the Monday
  ceremony run now carries that section on top of its three ceremonies.
  A raise to 400, with the timeout to 75, is queued in
  [pending-workflow-changes.md](pending-workflow-changes.md) item 2.
  Raising a censored row is the right direction to be wrong in.
- **The pm standup is a new run shape, and it does not get its own
  cap.** Clause 2 says an unmeasured shape inherits from its nearest
  twin, and the nearest twin here is the seat itself. Sharing the pm cap
  is not laziness, it is the tripwire principle: the standup is expected
  to finish in 40 to 60 turns, an unspent cap costs nothing, and a
  second workflow file existing only to hold a smaller number would be
  two files to keep in sync for no gain. Mark the standup provisional,
  measure it after its first free-running run, and if the seat's two
  modes ever diverge enough that one number cannot serve both, that is
  the evidence for splitting the workflow and not before.
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

## Duty-growth re-check, 2026-09-21

Rule 3 fired again. This run edited four charters, so the seats were
re-measured before waiting for a failure. Two of them needed the
measurement and two did not, and saying which is which is part of the
method.

Measured, because their work genuinely grew:

| Seat | Duty added | Peak turns, 8 newest runs | Cap in force | Required | Verdict |
|---|---|---|---|---|---|
| writer | site copy drafting, the value statement, preference capture | **80** (run 35459141039, 2026-09-19) | 150 | **200** | **UNDER-CAPPED, raise queued as item 4** |
| exo | §3d polarity test, §3e owner-as-seat audit | 93 all-time (run 35307859161, at a cap of 100), 79 in the last seven | 200 | 200 | ok, and no headroom at all |

Not measured, with the reason:

- **frontend** gained a restriction rather than a duty. "You set the
  words, you do not write them" removes work from the run. Its peak is
  286 against a cap of 600, so there are 314 turns of headroom even if
  the reasoning is wrong.
- **pm** gained two checks inside a step it already runs. Its cap is
  already censored and a raise to 400 is already queued as item 2, which
  covers this.

### The writer finding, stated plainly

The writer's cap was set from two runs on 2026-09-19, when its peak was
53. It has run eight times since and peaked at 80, which the rule turns
into a required cap of 200. **So the cap was already too low before this
run added a duty to it**, and nobody had re-measured because the seat
never failed.

That is worth a note about the method rather than about the seat. Rule 3
triggers re-measurement on duty growth, and monthly review triggers it on
the calendar, and a seat whose peak simply drifts upward between those two
triggers is measured by neither. The writer went from 53 to 80 in a day
because it started running daily. **A seat's first measurement is its
least reliable one, and the seats that run most often outgrow theirs
fastest.** The cheap correction: whenever this page is opened for any
reason, re-measure any seat whose row was built from fewer than five runs.
Writer, research and finance were all first-measurement rows on
2026-09-19. Writer has now moved.

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

## Duty-growth re-check, 2026-09-24

Triggered by this run's charter edits, which added the delivery-health
half to the PM's §1f and a company-standards read to all twelve seats.
No cap was hit anywhere this week, so nothing here is censored and every
number below is a free-running measurement.

Measured 2026-09-24 from the last five runs of each seat whose duties
grew or whose cap was already queued for a change.

| Seat | Peak now | Rule (2x, next 50) | Cap today | Verdict |
|---|---|---|---|---|
| pm | 141 (run 35311930240) | 300 | 300 | **correct, and the queued raise is not required by the rule** |
| writer | 83 (run 35649273894) | 200 | 150 | **short, confirms queued item 4** |
| engineer | 91 (run 35747676069) | 200 | 200 | correct |
| frontend | 174 (run 35887060776) | 350 | 600 | ample |

Three things to carry forward.

**The PM's queued raise to 400 is not supported by the measurement, and
this run is correcting its own predecessor.** Item 2 on
pending-workflow-changes.md proposed 300 to 400 on duty-growth grounds
when the daily standup was added. The rule gives 300 from a peak of 141,
and the peak has not moved, because the PM has not completed a run since
2026-09-19. So the honest position is that the raise is optional
headroom rather than a shortfall, and the queue now says so. The
methodology exists precisely to stop a cap being set from a feeling that
a seat has more to do, and the feeling in question was this seat's.

**The two PM failures are not cap evidence and must not be fed to the
rule.** Run 35493791740 ended at `num_turns: 1` and run 35626266985 at
`num_turns: 30`, both with `is_error: true` against a cap of 300. Those
are model failures, diagnosed in incident 23. A censored-low number is
as dangerous to this table as a censored-high one: feeding 30 into the
rule would propose cutting the PM's cap to 100. Clause 1 of the rule
covers runs that hit the cap. This is the mirror case and it is worth
naming, because it is the one the arithmetic gets wrong in the
expensive direction. **A run that failed for any reason other than the
cap contributes nothing to this table, high or low.**

**The writer's case got stronger.** Its peak has moved from 80 to 83
since the 2026-09-21 check, on a seat that runs daily and gained three
duties that week. 150 has still never been hit, which is the reason
nobody has noticed, and 200 remains the rule's answer.
