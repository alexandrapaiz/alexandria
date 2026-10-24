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
4. **A cron change is a re-measurement trigger too** (added 2026-09-27).
   A cap belongs to a job, not to a seat. When one workflow grows a
   second schedule with a different mode, it has two turn profiles
   sharing one number and this table needs two rows from that moment.
   The PM split into a Monday ceremony and a daily standup on
   2026-09-23, and for four days this page carried one measured row that
   described neither of them.

5. **Any run finishing above 70% of its cap re-derives that seat's row in
   the same week** (added 2026-10-04, **written into this page 2026-10-18**).
   The four triggers above all ask an auditor to name a cause, and the
   October re-derivation found seven of thirteen rows under the measured
   rule with the writer at 91% of its cap while **not one of the four had
   fired**, because the drift had no cause to name. Charters grow two lines
   at a time, and a seat whose last run is still open spends turns reading
   and re-shipping that branch before it starts today's work. Merge latency
   and cap collisions are the same failure. The PM reports the ratio daily
   from the run list it already reads and the re-derivation is the ExO's.

   This rule was cited by `prompts/exo-agent.md` §6 and by the 2026-10-11
   re-derivation on this page for fourteen days without ever being written
   here, which is `registers.md`'s own "recording is not enforcing" with the
   register and the citation the wrong way round. A rule that exists only in
   the files that cite it is a rule whose text nobody can check.

6. **A cap now lives in two files and only one of them runs the seat**
   (added 2026-10-18, `INC-2026-10-18-the-writers-cap-raise-governs-a-door-nothing-opens`).
   HQ decision 056 moved every seat's clock to the company host on
   2026-10-17. Since then `--max-turns` in
   `.github/workflows/agent-<seat>.yml` governs an explicit
   `workflow_dispatch` and nothing else, while `[runtime].max_turns` in
   `alexandrapaiz/alexandra-systems:runtime/agents/alexandria/<seat>/agent.toml`
   governs every real run. **So every cap change is written in both places
   or it is not a cap change.** This seat can read the manifests and can
   write neither, so the manifest half leaves through
   `docs/agents/hq-relay.md` with the exact line, and the item is not closed
   until the chair has carried it.

   The reconciliation is one command and it runs every time this page is
   touched:

   ```bash
   for s in engineer exo finance frontend market okr pm research sales security skill writer; do
     wf=$(grep -oE '\-\-max-turns [0-9]+' .github/workflows/agent-$s.yml | grep -oE '[0-9]+' | head -1)
     mf=$(gh api "repos/alexandrapaiz/alexandra-systems/contents/runtime/agents/alexandria/$s/agent.toml" \
            --jq .content | base64 -d | grep -oE '^max_turns = [0-9]+' | grep -oE '[0-9]+')
     [ "$wf" = "$mf" ] || echo "DIVERGED $s: workflow=$wf manifest=$mf"
   done
   ```

   Run on 2026-10-18 across all twelve seats it printed exactly one line:
   `DIVERGED writer: workflow=225 manifest=150`. Eleven of twelve agree and
   the models agree in all twelve. The check was validated against that
   known instance before being published here, per the 2026-10-11 rule that
   a check which cannot see reports health in the same words as a check that
   found nothing.

7. **And the measurement input is gone for every run after 2026-10-17**
   (added 2026-10-18). Every command in "How to measure" below reads
   `num_turns` and the error subtype out of `claude-execution-output.json`,
   which twelve workflows uploaded as a 90-day Actions artifact. The host
   writes its log to `.epito/logs/<agent>/<runId>.log` on its own disk
   instead, which no seat in this repository can read. So this page cannot
   be re-derived from evidence for any host run, which is now every run, and
   the honest state of the table below is **frozen at 2026-10-11 until the
   transcript is reachable again**. Do not refresh a row from a guess. The
   ask for a reachable transcript is in `docs/agents/hq-relay.md` for
   2026-10-18, and it is the precondition for rules 1 through 5 working at
   all.

## When this gets reviewed

- **Monthly**, by the ExO agent, in its first run of each month. Re-run
  the measurement below, refresh the table, queue any change.
- **Immediately**, in the same run, whenever any cap is hit by any seat.
  A cap hit is evidence about the cap.
- **On duty growth**, whenever a charter edit gives a seat more to do.
- **On a cron change**, whenever a workflow gains or splits a schedule,
  because that splits the job behind the cap. Since 2026-10-17 read "cron"
  as `[trigger].cron` in the seat's host manifest, and read a change to
  `[trigger].subscriptions` the same way, because an added subscription is a
  new turn profile for the same reason a second schedule was.
- **On a runtime change**, whenever the thing that starts a seat changes at
  all, because a cap belongs to a job and the job is now somewhere else.
  See `prompts/exo-agent.md` §2d.

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
| pm (ceremony) | 8, none since the cron split | 141 (censored) | 300 | unknown | **stale**: last measured before the ceremony and the standup became separate runs, see below |
| pm (standup) | 4 | 81 | shares the pm cap, 300 | 200 | **measured 2026-09-27**, comfortable, see below |
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

---

## The PM's two runs, measured apart (2026-09-27)

The cron split of 2026-09-23 turned one weekly PM run into two different
jobs sharing one cap, and this page carried the standup row as
`unmeasured, provisional` for four days after the first one completed.
Measured now, with the command at the top of this page, on the four
scheduled standup runs since the split:

| Run | Date | `num_turns` | Cap in force |
|---|---|---|---|
| 36022688185 | 2026-09-24 | 62 | 300 |
| 36156468758 | 2026-09-25 | 44 | 300 |
| 36250215509 | 2026-09-26 | 81 | 300 |
| 36330174329 | 2026-09-27 | 38 | 300 |

Peak 81, so the standing rule of twice the peak rounded up to the next 50
gives 200. The cap in force is 300 and nothing is close to it. **The
consequence for the queue is that the standup's share of the 300-to-400
raise in item 2 of pending-workflow-changes.md is cancelled**, on
measurement rather than on judgment, which is the whole point of keeping
this page.

**The ceremony row is the one to watch, and it is stale rather than
comfortable.** Its 141 was measured when the ceremony and the standup
were the same run, so it includes work the standup now does and excludes
nothing the ceremony has since gained, which is the grooming, the sprint
plan and the day's dispatch queue. No ceremony run has completed since
the split: the only Monday in between, 2026-09-21, failed at turn 30.
Two rows of this table therefore describe a seat that no longer exists in
that shape.

**What the next run does, and it is one command.** The 2026-09-28
ceremony run is the first real measurement of the heavier half.

```bash
gh run list --workflow=agent-pm.yml --limit 5 --json databaseId,createdAt,conclusion
# then the num_turns command at the top of this page, on the Monday id
```

If it comes in under 150, delete item 2 from the queue and mark both rows
ok. If it comes in over 200, the raise is a shortfall rather than
headroom and the item's justification changes from optional to required.
Either way the number decides it.

**The general note, because this is the second time this page has been
wrong for the same reason.** A cap belongs to a job and not to a seat.
When one workflow grows a second cron with a different mode, it has two
turn profiles sharing one number, and this table needs two rows from that
moment rather than from the moment somebody notices. The trigger for a
re-measurement is therefore not only a cap hit and a duty change, which
is what the rule above says. **It is also a cron change**, and that is
now the third entry on the list in this page's opening rule.

---

## Duty-growth re-check, 2026-09-27: the skill seat under ADR-35

Rule 3 again, and this time the duty growth was an ADR rather than a
charter edit. ADR-35 (2026-09-26) made reading a precondition of skill
creation: the skill seat now surveys the claim graph, fetches papers in
full from arXiv, and appends what it could not read to
docs/research/reading-queue.md. Three new steps, all of them turn-hungry
in the same way, because each paper is a fetch and a read.

Re-measured 2026-09-27 from all six runs the seat has completed, by the
command in "How to measure" above. Every one finished freely
(`"subtype": "success"`, `"is_error": false`), so nothing here is
censored in either direction.

| Run | Date | num_turns | Cap in force |
|---|---|---|---|
| 36206676462 | 2026-09-26 | **92** | 180 |
| 35949369039 | 2026-09-24 | 69 | 180 |
| 35750031009 | 2026-09-22 | 81 | 180 |
| 35308548423 | 2026-09-18 | 67 | 100 |
| 35306055976 | 2026-09-18 | 61 | 100 |
| 35305087740 | 2026-09-18 | 41 | 100 |

| Seat | Duty added | Peak turns | Cap in force | Required | Verdict |
|---|---|---|---|---|---|
| skill | ADR-35: survey, read in full, queue what it could not read | **92** (run 36206676462) | 180 | **200** | **UNDER-CAPPED, raise queued as item 11** |

Run 36206676462 is the first run under ADR-35, and it is the one that
moved the peak. It read five papers in full, queued twelve it could not
read, and finished in 92 turns against a peak of 81 before the ADR. Twice
92 rounded up to the next 50 is 200, and the cap is 180, so the seat is
short by 20 turns having never hit its cap. That is the writer's case
from 2026-09-21 repeating exactly: a seat whose peak drifts up between
triggers is measured by neither of them, and this one was caught only
because the owner asked for the measurement by name.

Two notes for whoever reads this next.

**The queue this seat writes is now drained by machinery, and that cuts
the other way.** From this PR, `pipeline/distill.py` reads
docs/research/reading-queue.md at the top of every run and distills what
it finds ahead of the day's intake. The reading the skill seat cannot
finish inside its own run is therefore work the pipeline picks up
overnight, which is a reason the seat's peak should stop climbing rather
than a reason to expect more growth. Re-measure after the next two runs
before concluding either way.

**The timeout is not the binding constraint.** Run 36206676462 spent
743 seconds on 92 turns, which is 7.4 turns a minute. Two hundred turns
at that rate is 27 minutes against a `timeout-minutes` of 75, so the
raise needs no timeout change. Checked, because the rule says a cap
raise that outruns its job timeout buys nothing.

This measurement was taken by the engineer seat under the owner's
directive of 2026-09-25, not by the ExO seat that maintains this page.
The page stays the ExO's; one directed edit is not a transfer.

## Re-derivation, 2026-10-11, on a cap hit

Rule 2 fired, twice over. The writer hit `error_max_turns` on 2026-10-04
(run 37226048547) and again on 2026-10-09 (run 37986599276), both at
`num_turns: 151` against `--max-turns 150`. Rule 5's ratio also fires for
the engineer. Every number below is the peak over that seat's eight newest
`success` or `failure` runs, by the command at the top of this page.

| Seat | Peak | Prev (2026-10-04) | Cap | Required | % of cap | Verdict |
|---|---|---|---|---|---|---|
| writer | **151, a cap hit** | 136 | 150 | 350 | **100.7%** | **failed twice.** Item 21, split out and urgent |
| engineer | **184** | 168 | 200 | 400 | **92%** | short. Item 14's 350 was below the rule before it was read |
| frontend | 188 | 286 | 600 | 400 | 31% | ok, and the only comfortable row in the org |
| skill | 156 | 156 | 180 | 350 | 87% | short, item 14, unchanged |
| research | 145 | 145 | 180 | 300 | 81% | short, item 14, unchanged |
| security | 134 | 134 | 250 | 300 | 54% | short, item 14, unchanged |
| market | 131 | 131 | 160 | 300 | 82% | short, item 14, unchanged |
| pm | 105 | 81 | 300 | 250 | 35% | ok |
| exo | 134 | 134 | 200 | 300 | 67% | short, item 14, unchanged |

The writer's and the engineer's rows are the only ones that moved, and they
moved in the same direction for different reasons: the writer's peak is now
a floor rather than a measurement, because a capped run tells you demand
exceeded 151 and not what it was, and the engineer's rose 16 turns on its
own in seven days while nothing was added to its charter.

### What a cap hit costs, measured rather than asserted

Both writer hits were `error_max_turns`, which this page's own test
identifies as a run killed mid-work rather than a run failed after
shipping. Ship-first held both times and both times the unpushed increment
died: on 2026-10-09 that was `docs/ideas.md`, `docs/voice/ban-list.md` and
`docs/voice/reviews/2026-10-09.md`, dirty at teardown. So the cost of a
short cap is bounded by ship-first and is not zero, which is the number the
"a cap is a tripwire, not a budget" argument needs beside it.

### Rule 6: a capped run re-derives on a floor, and the proposal is not the old number plus a bit

Added 2026-10-11. When a seat hits its cap, `2 x the cap + 1` is the
arithmetic the rule produces and it is the wrong instinct to then round
down toward the old proposal. Item 14 had already proposed 300 for the
writer off a peak of 136. After the cap hit, 151 doubles to 302 and rounds
to 350, and a run that proposes 300 because 300 was already written down
has let a queued number outrank a measurement. **The queued proposal is
evidence about what a previous run thought, never an input to the rule.**

This is the fourth time a stale number on `pending-workflow-changes.md`
nearly shipped as a fix: items 4 and 11 proposed 200 for two seats already
above it, item 26's timeout diff would have lowered a live value, and item
14 itself carried 350 for a seat that needed 400 within a week of being
written. Re-read the numbers in a queued item every run, not only its
anchors.

## Re-derived 2026-10-24, from the board's run record, after thirteen days frozen

This page said at the top of its measurement section that it was frozen at
2026-10-11 because `num_turns` lived in a GitHub Actions artifact and the
seats had left GitHub. The ask that would unfreeze it was written into
`docs/agents/hq-relay.md` on 2026-10-18 in these words: "The board already
receives a run record per run, so a `num_turns` field on it would close this
at the lowest cost."

**That field was built on 2026-10-18, is called `turns`, and this page stayed
frozen for six more days.** Two runs of this seat read both files in between.
The account is
`INC-2026-10-24-the-receipt-we-asked-for-was-built-and-no-charter-was-pointed-at-it`.

### The new measurement command

The numerator and the denominator now come from two different places, and
both are readable by any seat:

```bash
# numerator: turns per run, per seat
curl -s "$BOARD_API_URL/api/board/alexandria" \
  -H "Authorization: Bearer $BOARD_RUNTIME_TOKEN" \
  | python3 -c 'import json,sys
from collections import defaultdict
peak=defaultdict(int)
for r in json.load(sys.stdin)["runs"]:
    peak[r["seat"]]=max(peak[r["seat"]], r["turns"] or 0)
for s,t in sorted(peak.items(), key=lambda kv:-kv[1]): print(s,t)'

# denominator: the cap that actually governs, which is not in any workflow
for s in engineer exo pm writer frontend market okr research sales security skill finance; do
  printf '%s ' "$s"
  gh api "repos/alexandrapaiz/alexandra-systems/contents/runtime/agents/alexandria/$s/agent.toml" \
    --jq .content | base64 -d | grep -E '^max_turns|^model' | tr '\n' ' '
  echo
done
```

### The table

Peak over the runs the board returned, which is the 25 most recent across all
seats, covering 2026-10-18T12:40Z to 2026-10-24T00:08Z.

| Seat | Peak | Cap in manifest | Required (2x, next 50) | % of cap | Verdict |
|---|---|---|---|---|---|
| writer | **140** (2026-10-23T23:31Z) | **150** | 300 | **93%** | **over the rule-5 trigger for the third consecutive measurement.** Ask 4 on the relay page asks for 225, the owner's own approved number; the rule asks 300 |
| pm | 141 (2026-10-23T17:04Z) | 300 | 300 | 47% | ok, and correct at 300 |
| engineer | 131 (2026-10-23T23:35Z) | 200 | 300 | 66% | under the trigger, short of the rule |
| exo | 89 (2026-10-23T23:43Z) | 200 | 200 | 45% | ok |

### Three things this measurement cannot do, stated so no reader over-reads it

1. **It covers four seats of twelve.** The board's run route returns a fixed
   count of recent runs and accepts no query string, so eight seats that did
   not run in the last 25 sessions have no row. Their last real measurement
   is still 2026-10-11. **A table scoped by somebody else's count is the
   defect this page's rule 5 was written against**, and the ask to scope the
   route by time is the 2026-10-24 entry on the relay page.
2. **It cannot tell a cap hit from a crash**, which rule 1 of this page
   depends on. The record carries `exit` and `turns` and no error subtype,
   so a run killed at its cap and a run that died on its own both read as a
   non-zero exit at some turn count. Every near-cap number here is therefore
   *possibly* censored and the writer's 140 is the one that matters: if that
   run was killed, 140 is a floor and not a peak. Residual ask filed.
3. **The cap it compares against is one this seat cannot write.** The
   governing value is `max_turns` in a manifest in `alexandrapaiz/alexandra-systems`.
   `pending-workflow-changes.md` is the wrong lane for it and always was;
   the lane is `hq-relay.md`. That is already recorded as a capability gap
   on `docs/agents/unowned-duties.md` and as
   `INC-2026-10-18-the-writers-cap-raise-governs-a-door-nothing-opens`.

### What the numbers say about the organization, which is not what they say about the caps

The pm at 47% of 300 and the writer at 93% of 150 are the same week of work.
The difference is not that one seat does more; the pm ran ten sessions in
that window and the writer three. **A seat woken often finishes each session
well inside its cap. A seat woken rarely arrives at each session holding
everything that accumulated since the last one**, which it must read, plus
its own unmerged branch, which it must carry. That is the merge-latency
finding of 2026-10-04 and the cap finding seen from one more angle, and it
suggests the cheapest cap relief available is a subscription rather than a
number.

## Re-derived again 2026-10-24 16:40Z, from the host's own audit log, for all twelve seats

The section above was written earlier the same day, from the board's run
route, and it opened by naming its own first limitation: "It covers four
seats of twelve. The board's run route returns a fixed count of recent runs
and accepts no query string, so eight seats that did not run in the last 25
sessions have no row." The ask to scope that route by time went onto the
relay page the same run.

**The scoped record already existed, on this host, readable by every seat,
and no charter in this repository names it.** The resident runtime has been
appending one line per run to `/srv/asc/state/.epito/audit.jsonl` since
2026-09-24T02:57Z. Each `run.end` row carries `agent`, `trigger`, `model`,
`exit`, `durationMs`, `turns`, `session` and, when the run opened one, `pr`.
That is 985 rows across the portfolio and 171 for alexandria, spanning a
month rather than 25 sessions.

So this page is re-derived a second time on the same day, because the better
source cost one `cat` to find and the earlier table understates three of the
four rows it does carry.

### The command

No credential and no network. The file is on the seat's own filesystem.

```bash
python3 - <<'PY'
import json, collections, statistics as st
rows = []
for line in open('/srv/asc/state/.epito/audit.jsonl'):
    try: d = json.loads(line)
    except ValueError: continue
    if d.get('action') == 'run.end' and (d.get('agent') or '').startswith('alexandria-'):
        rows.append(d)
by = collections.defaultdict(list)
for d in rows: by[d['agent']].append(d)
for seat in sorted(by):
    t = sorted(x['turns'] for x in by[seat] if x.get('turns') is not None)
    if not t: continue
    print(seat, 'runs', len(by[seat]), 'median', st.median(t), 'peak', max(t))
PY
```

### The table

Peak over every alexandria run the host recorded between 2026-09-24T04:16Z
and 2026-10-24T16:00Z. The cap column is quoted and not measured, for the
reason stated under the table.

| Seat | Runs | Median turns | Peak | Cap | % of cap | Required (2x, next 50) | Verdict |
|---|---|---|---|---|---|---|---|
| writer | 20 | 103 | **153** (2026-10-18T07:50Z, exit 0) | **150** (manifest) | **102%** | 350 | **the cap has been passed, not merely approached** |
| engineer | 19 | 107 | **190** (2026-10-18T01:02Z, exit 0) | 200 (manifest) | **95%** | 400 | **over the rule-5 trigger, and 59 turns above what the 25-run window saw** |
| exo | 12 | 89 | **155** (2026-10-24T00:42Z, exit 0) | 200 (manifest) | **78%** | 350 | **over the rule-5 trigger, and 66 turns above what the 25-run window saw** |
| market | 3 | 96 | 118 | 160 (workflow era) | 74% | 250 | over the trigger, on three runs, so the number is thin |
| finance | 2 | 62 | 83 | 120 (workflow era) | 69% | 200 | at the trigger, on two runs |
| pm | 93 | 54 | 198 (2026-10-24T00:52Z, exit 0) | 300 (manifest) | 66% | 400 | under the trigger, short of the rule |
| okr | 6 | 62 | 86 | 160 (workflow era) | 54% | 200 | ok |
| skill | 2 | 46 | 91 | 180 (workflow era) | 51% | 200 | ok, on two runs |
| sales | 2 | 67 | 67 | 160 (workflow era) | 42% | 150 | ok, on two runs |
| frontend | 8 | 101 | 197 (2026-10-24T01:39Z, exit 0) | 600 (workflow era) | 33% | 400 | ample, and the 600 is the least trustworthy cap on this page |
| security | 2 | 73 | 73 | 250 (workflow era) | 29% | 150 | ok, on two runs |
| research | 2 | 48 | 48 | 180 (workflow era) | 27% | 100 | ok, on two runs |

### Four things this measurement settles, and two it does not

**It settles that no seat has hit a cap in a month.** Every one of the 38
non-zero exits is listed below with its turn count, and the highest is the
writer at 126. A cap hit kills a run, so a cap hit appears here as a
non-zero exit at or near the cap, and there is none. That matters because
the earlier section had to write "every near-cap number here is therefore
*possibly* censored". None of them is. The peaks are peaks.

**It settles the writer's queued raise by passing the cap rather than
nearing it.** The writer's 153-turn run on 2026-10-18 exited 0 at three
turns above its stated cap of 150. Either the manifest's `max_turns` is not
150, or the runtime does not enforce it the way this page has assumed for
five weeks. Both readings are findings and they point at the same question,
which is on the relay page as a new ask. Until it is answered, **the writer
row is the one number on this page that no reader should treat as settled.**

**It settles the cost of a window scoped by somebody else's count, in
turns.** Three seats appear in both tables. The 25-run window saw the
engineer at 131 and the month sees 190. It saw this seat at 89 and the month
sees 155. It saw the writer at 140 and the month sees 153. Every error is in
the same direction and the largest is 59 turns, which is the difference
between 66% of a cap and 95% of it. **Rule 5 fires for three seats on the
month's data and fired for one on the window's.** That is rule 5's own
defect, which is that a table scoped by a count somebody else chose reads
as healthy, measured against itself.

**It settles that rule 5's trigger is the right detector and its cadence is
not.** The three seats over the trigger are the three seats that ran most,
in the order they ran most. Nothing about any of their charters changed to
cause it, which is the 2026-10-04 finding restated: none of the four named
triggers would have fired, because none of them asks a question with no
named cause.

**It does not tell a cap hit from a crash in general**, only in this
window's particular case. The row carries `exit` and `turns` and no error
subtype, so the two flavours rule 1 of this page depends on are still
indistinguishable in principle. The reason the conclusion holds anyway is
that every non-zero exit is far from its cap, which is evidence and not a
mechanism. The residual ask stands.

**It does not give eight of twelve seats a governing cap.** Peaks are now
measured for all twelve. `max_turns` lives in
`alexandrapaiz/alexandra-systems:runtime/agents/alexandria/<seat>/agent.toml`,
which this seat reads by leaving the repository and cannot write at all, and
the host's `state.json` carries `model`, `cron`, `repo` and `nextCron` but
no cap. So eight rows above compare a measured 2026-10-24 peak against a cap
last confirmed in the workflow era, and a workflow has not governed a seat
since 2026-10-17. **Those eight caps are quoted from a file that no longer
decides anything, and that is worse than an unmeasured row, because the
percentage column looks like arithmetic.** The ask is on the relay page.

### The 38 non-zero exits, and the two fingerprints in them

This is the §2b failure sweep for the month, done once properly rather than
per run, because the whole month is now readable in one file.

**Fingerprint one: the provider refusal.** `turns == 1` with
`durationMs < 30000`, and never alone. Eight instances, every one of them
inside a cluster of rows whose timestamps agree to the second across
different seats: 2026-10-18T02:39 (four seats), 2026-10-23T19:09 (one),
2026-10-24T13:49 (one), 2026-10-24T16:00 (two). The host's own
`GET /api/capacity` counts the same class portfolio-wide as
`refused_turn_one`, which stood at 13 of 252 attempts on 2026-10-24. **A run
that ends at one turn in seven seconds is capacity and not a seat**, and
that sentence is the whole diagnosis, so the next run looks it up rather
than deriving it.

**Fingerprint two: the daemon took eleven seats down mid-run, and it is in
no register.** At 2026-10-05T03:27:08Z through 03:27:13Z, eleven alexandria
seats ended with `exit: 143`, which is 128 plus SIGTERM, inside five
seconds of each other. Every one had been running about fourteen minutes.
Ten of the eleven recorded no turn count at all, so ten runs' worth of work
is unmeasurable as well as lost. `grep -c 'exit 143' docs/agents/incidents.md`
returns zero, and this is the first mention of it anywhere in this
repository, nineteen days after it happened. It is registered as
`INC-2026-10-24-eleven-seats-were-sigtermed-mid-run-and-nobody-filed-it`.

**Everything else is the known classes.** The 2026-09-30T04:02 cluster is
eight seats ending within 52 seconds with full turn counts, which is the
window close rather than a refusal. The remainder are single `exit: 1` rows
at ordinary turn counts, already diagnosed in the learning log as
cap-adjacent, and now known not to be cap hits.

### Correction, same day, later run: fingerprint one's test selects the retry and discards the kill

The paragraph above is wrong about 2026-10-24T13:49, and wrong in a way that
matters more than the count. It records that minute as one instance of the
provider refusal, because its test is `turns == 1` and exactly one
alexandria row in that minute had one turn. Read the window by time instead
of by turn count and it is not one row. It is **twenty**.

```bash
# the test that finds the event: cluster on time, across seats, at any turn count
python3 - <<'PY2'
import json
rows = []
for line in open('/srv/asc/state/.epito/audit.jsonl'):
    try: rows.append(json.loads(line))
    except Exception: pass          # see the torn line below; do not drop this guard
w = [r for r in rows if r.get('action') == 'run.end' and r.get('exit') == 1
     and '2026-10-24T13:49' <= r['ts'] <= '2026-10-24T13:52']
print(len(w), [(r['agent'], r.get('turns')) for r in w])
PY2
```

**The `try` is not defensive habit and the first version of this command did
not have it.** The log holds one torn line, 4209 of 5639, where a `message`
row from 2026-10-20T12:20Z is truncated mid-key at 124 characters and a
second row from 2026-10-23T15:26Z is written over the remainder. A strict
parse raises on it and the whole sweep returns nothing, which is how this
command failed the first time it was run after being written. The lost record
is a `message` action and not a `run.end`, so this page's numerators are
intact, and rule 7 says to quote the source rather than trust it: an
append-only file written non-atomically loses a record about every 5,600 and
gives no sign of which one.

`2026-10-24T13:49:23.944Z` through `13:51:37.170Z`, a span of 133 seconds,
twenty `run.end` rows with `exit: 1`, across all five companies: Ursa 10,
alexandra-systems 4, alexandria 3, atelier 2, epitome 1. **Thirteen of the
twenty were live runs killed mid-work**, at turn counts 4, 6, 35, 36, 41, 46,
50, 53, 64, 75, 75, 92 and 98, which is 675 turns of work. The other seven
are at exactly one turn with durations from 6.3 to 24.0 seconds, and four of
those seven are immediate restarts of a seat that had just been killed:
`ursa-market`, `atelier-pm`, `ursa-exo` and HQ's `engineer` each have a kill
row and a one-turn row inside the same half minute.

**So the one-turn rows are the aftershock and the kills are the event.**
Fingerprint one describes a run that was refused before it started, which is
real and is the right diagnosis for a seat that wakes into an exhausted
provider. It is the wrong diagnosis for this minute, because it reads the
retries and discards the thirteen runs whose work was actually lost. A test
keyed on `turns == 1` cannot see a kill by construction.

**The third fingerprint, then, stated as a test rather than as a story.**

> Two or more `exit: 1` rows from different seats inside sixty seconds is one
> event, whatever their turn counts. Count the window, not the row.

That holds for `exit: 143` too, which is fingerprint two, so the two
fingerprints are one shape read through two signals. The sharper question a
cluster asks is which signal the host sent, and the turn counts answer a
different question: how much work the event cost.

**Why nobody diagnosed this one on the day, which is the organizational
half.** The event killed `alexandria-exo` at 41 turns, `epitome-exo` at 36,
`ursa-exo` at 92 and HQ's `exo-centralizer` at 6. **Every seat in the
portfolio whose charter owns failure diagnosis was inside the failure.** The
seat that would have swept it was dead for the same reason the sweep was
needed, and the next ExO run of each company read a board run list scoped to
25 rows and saw a handful of ordinary-looking single failures. That is not a
gap in anybody's charter. It is a correlated-failure property of putting one
duty in one seat per company and waking all of them off one host, and the
honest fix is a detector that does not depend on a seat being alive.
Registered as
`INC-2026-10-24-twenty-runs-across-five-companies-ended-inside-one-minute-and-the-fingerprint-counted-one`.

### Rule 7: measure from the host's audit log, and say so

The numerator for this page comes from `/srv/asc/state/.epito/audit.jsonl`
and not from the board, because the board's route is scoped by a count this
seat does not choose and the file is scoped by the month. Quote the window
you read, in dates, in the table's caption. When the file is unreadable, say
that rather than falling back silently to the narrower source, because the
two disagree by up to 59 turns and a reader cannot tell which one produced
a row.
