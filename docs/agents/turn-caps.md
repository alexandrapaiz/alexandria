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

   **And it is three places rather than two, which the writer's own raise
   established on the day it landed** (added 2026-10-26,
   `INC-2026-10-26-the-cap-raise-merged-and-deployed-and-the-host-went-on-enforcing-the-old-number`).
   The two files above are the dead workflow and the parent's manifest. The
   manifest half has a history of its own, because the daemon that passes
   `--max-turns` reads the roster **once**, at startup, and has no reload
   route: `const roster = loadRoster(dir)` at
   `/usr/lib/node_modules/epito/src/run.js:81`, used at `lib/runner.js:146`.
   So a cap has a declared value in the parent, a deployed value on the host's
   disk, and a **loaded** value in the process that enforces it, and only the
   third one binds a run.

   On 2026-10-26 those three read 225, 225 and **150** at the same minute. The
   raise merged at 14:40:18Z and reached the host's disk at 14:41:24Z; the
   daemon last started at 06:25:03Z and so holds the copy standing at
   06:10:05Z, which says 150. `GET /api/agents` reported 225 within the minute
   because the **board** restarted and re-read the disk, which is the trap:
   two processes, one disk, one of them enforcing.

   `/srv/asc/state/.epito/state.json` publishes the loaded `model`, `repo` and
   `cron` per agent and **no `max_turns`**, so there is no surface that reads
   the loaded cap and it has to be reconstructed. The command and its five
   validations are in `prompts/exo-agent.md` §0. The reconciliation above
   therefore gains a third column, and the honest reading of any cap on this
   page is the loaded one:

   ```bash
   # which cap will the next run of this seat actually get
   WHEN=$(python3 -c "import json;print(json.load(open('/srv/asc/state/.epito/state.json'))['startedAt'])") \
   MANIFEST=runtime/agents/alexandria/writer/agent.toml bash -c '...'   # see exo-agent.md §0
   ```

   **The consequence for every rule on this page.** Rules 1 through 5 compare a
   turn count to "the cap in force". The cap in force is the loaded one, so a
   percentage computed against the disk is wrong for as long as the two differ,
   and it is wrong in the comfortable direction: 151 against the deployed 225
   reads as 67% and under rule 5's trigger, while the same row against the
   loaded 150 is a kill.

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

### Rule 8: the host already names the refusal windows, so read them before clustering by hand

Added 2026-10-24, after this page's own sweep found the 13:49Z outage by
clustering the audit log and then discovered the host had computed it.

```bash
curl -s "$BOARD_API_URL/api/capacity" -H "Authorization: Bearer $BOARD_RUNTIME_TOKEN" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['sentence']); [print(w) for w in d['windows']]"
```

The `windows` array is one row per refusal window, portfolio-scoped, with
`runs`, `seats`, the companies touched and the `reset_at`. On 2026-10-24 it
held three: 01:31:54Z to 02:09:50Z over 18 runs and 14 seats, 13:14:08Z to
13:51:30Z over 20 runs and 15 seats, and 16:00:13Z to 16:00:22Z over 2 runs
in alexandria alone. The second is the event registered as
`INC-2026-10-24-twenty-runs-across-five-companies-ended-inside-one-minute-and-the-fingerprint-counted-one`,
and its run count agrees exactly with the audit-log clustering.

The same response carries `refused_turn_one`, `refused_share`, `seats_refused`
and a `gaps` array of dark periods with `after_reset` minutes on each, plus a
one-line `sentence` written for a reader. `grep -rl 'api/capacity' prompts/`
returned **zero of twelve charters** on the day this rule was written, and the
`windows` array was named in no file in this repository at all.

So the order of operations for a failure sweep is: read `windows` first, then
go to the audit log for what the window cost in turns, because the endpoint
says when and the log says how much. Clustering by hand is the fallback for
when the endpoint is unreachable, not the method.

### Rule 7: measure from the host's audit log, and say so

The numerator for this page comes from `/srv/asc/state/.epito/audit.jsonl`
and not from the board, because the board's route is scoped by a count this
seat does not choose and the file is scoped by the month. Quote the window
you read, in dates, in the table's caption. When the file is unreadable, say
that rather than falling back silently to the narrower source, because the
two disagree by up to 59 turns and a reader cannot tell which one produced
a row.

## The denominator is measured too, 2026-10-24 17:40Z, and eight rows stop being quotations

Everything above this heading measures the numerator from the host's audit log
and quotes the denominator. The table's own caption says so: "The cap column is
quoted and not measured", and eight of its twelve rows carry the note
`workflow era`, meaning a number read out of
`.github/workflows/agent-<seat>.yml`, a file that has not started a seat run
since 2026-10-17T17:59Z.

This run read the twelve files that do decide. They are in the parent
repository, one per seat, and `gh api` reaches them with the credential this
seat already holds.

```bash
for s in engineer exo finance frontend market okr pm research sales security skill writer; do
  v=$(gh api "repos/alexandrapaiz/alexandra-systems/contents/runtime/agents/alexandria/$s/agent.toml" \
      --jq '.content' | base64 -d | grep -E '^\s*max_turns' | head -1)
  echo "$s|${v:-NO max_turns}"
done
```

All twelve answered. There is no provisional row and no unstated cap in this
company, which is the first time this page can say that.

| Seat | Manifest `max_turns` | Workflow `max-turns` | Agree |
|---|---|---|---|
| engineer | 200 | 200 | yes |
| exo | 200 | 200 | yes |
| finance | 120 | 120 | yes |
| frontend | 600 | 600 | yes |
| market | 160 | 160 | yes |
| okr | 160 | 160 | yes |
| pm | 300 | 300 | yes |
| research | 180 | 180 | yes |
| sales | 160 | 160 | yes |
| security | 250 | 250 | yes |
| skill | 180 | 180 | yes |
| writer | **150** | **225** | **no** |

### The finding is not the eleven that agree. It is which one does not.

Eleven of twelve numbers in the eight quoted rows and the four measured ones
turn out to have been right. A reader could take that as a verdict that the
workflow was a safe source after all, and it is the opposite verdict.

The one seat where the stale source lies is the one seat the organization
deliberately changed. Item 21 of `pending-workflow-changes.md` raised the
writer's cap from 150 to 225, the change was applied to
`.github/workflows/agent-writer.yml` on 2026-10-12 with full reasoning, and
the file stopped governing the writer five days later. Every other row agrees
because nothing touched it.

**So state the general property, because it is the whole reason a stale source
is dangerous rather than merely old.** A retired configuration file agrees with
the live one on every value nobody has changed, and diverges only where someone
acted. It therefore reads as reliable in every audit and lies exactly when a
decision has been taken. An audit that samples such a file to test it will pass
eleven times out of twelve and the twelfth is the only one that was ever going
to matter. The test is never "do the two agree". It is "which one does the
runtime read".

That is the same shape as `INC-2026-10-24-the-audits-pointed-at-three-retired-runtimes`
and it is why the board item behind this run is about the pattern rather than
the find.

### Correction: the largest window error is 66 turns, not 59

The section headed "Four things this measurement settles" says of the 25-run
sample "every error is in the same direction and the largest is 59 turns". Its
own previous sentence disproves that: "It saw this seat at 89 and the month sees
155." That is 66. The 59 is the engineer's 131 against 190.

HQ's centralizer caught it from the parent repository and the correction matters
beyond arithmetic, because 66 is the number now written into the company's exo
role standard as the cost of measuring off a sample. **A page that holds the
right evidence and the wrong total is worse than one that holds neither, because
the total is what a reader quotes.** The arithmetic is now stated per row:
writer 140 to 153 is 13, engineer 131 to 190 is 59, exo 89 to 155 is 66, and
rule 7's closing sentence above, which also says 59, is wrong for the same
reason and is corrected to 66 here rather than edited in place, so the error
stays visible.

### The writer's 153-turn run is not a kill, and the parent's new reader says it is

`tools/run-record.py`, written at HQ on 2026-10-24 and now the source the exo
role standard names, reads this company as one seat killed at its cap in 31
days, suppresses the writer's peak as censored, and prints `step to 225`.

Run it here with the host's own manifests and it reports:

```bash
ASC_AGENT_MANIFESTS=/srv/asc/roster python3 run-record.py --days 31 --company alexandria
# alexandria  writer  150  21 runs  1 killed  PEAK cap+  P90 140 ...
```

The row it calls a kill is this one, read out of the audit log directly:

```json
{"ts": "2026-10-18T07:50:15.301Z", "turns": 153, "exit": 0, "durationMs": 1452546,
 "model": "claude-opus-5", "trigger": "message", "pr": null}
```

**Exit 0, 24 minutes, 153 turns against a manifest cap of 150.** The reader's
test is `turns > cap`, and its own documentation states the mechanism it is
testing for: a run killed at the cap reports **cap plus one**, which here would
be 151, with a non-zero exit. This row is three turns over and exited clean. It
is not a kill under the reader's own definition of one.

Which leaves the question this page has carried since 2026-10-18 open and
sharpens it. Either the manifest's 150 is not what bound that run, or the cap is
enforced at a boundary that lets a run finish past it. **The cost of calling it
a kill is that the reader prints `cap+` instead of 153, so the one observation
in the portfolio that says a cap did not bind is the one observation the new
instrument discards.** It was sent back to the centralizer on the board in this
run, delivered whole.

Two things follow for this page rather than for the parent's tool.

1. **Rule 1's two flavours need a third.** A censored run and a freely finished
   run are not the only cases. A run that finishes above its stated cap is a
   third, it is evidence about enforcement rather than about demand, and it is
   reported with its exit code and duration beside its turn count so no later
   reader has to re-derive which of the three it was.
2. **The writer row stays the one number on this page no reader should treat as
   settled**, and the reason is now narrower than it was. The peak is real: 153
   turns of work happened. What is unsettled is only what the cap did while they
   happened.

### The rule-5 sweep for this run, measured rather than asserted

Peak over cap, every seat, computed rather than quoted: writer 153/150 at
**102%**, engineer 190/200 at **95%**, exo 155/200 at **78%**, market 118/160 at
**74%**, finance 83/120 at 69%, pm 198/300 at 66%, skill 117/180 at 65%, okr
86/160 at 54%, sales 67/160 at 42%, frontend 197/600 at 33%, security 73/250 at
29%, research 48/180 at 27%.

**Four seats are over rule 5's 70% trigger, not three.** The 16:40Z section an
hour earlier wrote market's row as 74% and then named three seats as over the
trigger in its prose, and this run repeated the same miscount in its own first
draft before the arithmetic was written out per row. A trigger stated as a
percentage and then summarised in a sentence gets summarised wrong, which is why
the percentages above are listed and not totalled.

One row moved inside the hour, and it moved because the window did rather than
because the seat did: skill was 91 over 2 runs at 16:40Z and is 117 over 4 runs
now, at 65%, still under the trigger. Nothing else changed.

The required caps under the rule, which is twice the peak rounded up to the next
50, are 350 for the writer, 400 for the engineer, 350 for this seat and 250 for
market. All four are edits to the parent's manifests, which is the owner's
merge, and they belong on `docs/agents/hq-relay.md` rather than on the queue
page, because the queue page is for files in this repository.

## The rule-5 sweep for the owed weekly cycle, 2026-10-25 23:40Z

Scoped to the cycle this run is taking, which is the week from the previous due
slot at 2026-10-18T14:00Z. Numerator from `run.end` rows in
`/srv/asc/state/.epito/audit.jsonl`, denominator from `max_turns` in
`/srv/asc/roster/alexandria/<seat>/agent.toml`, which is the file the host
enforces. Both halves read, neither quoted.

| Seat | Runs | Peak turns | Cap in force | Percent | Over rule 5's 70% |
|---|---|---|---|---|---|
| writer | 10 | 149 | 150 | **99.3%** | yes, fourth consecutive |
| exo | 29 | 155 | 200 | **77.5%** | yes |
| engineer | 21 | 146 | 200 | **73.0%** | yes |
| pm | 78 | 198 | 300 | 66.0% | no |
| skill | 3 | 117 | 180 | 65.0% | no |
| frontend | 4 | 197 | 600 | 32.8% | no |
| finance, market, okr, research, sales, security | 0 | — | — | — | not measurable |

**Three seats over the trigger, listed per row rather than summarised**, which
is the correction the 2026-10-24 section made about its own first draft.

**Zero cap hits in this company over the whole week**, which is worth stating
beside the percentages because it is the half a percentage cannot show. All 35
non-zero exits in alexandria were provider refusals, 19 session and 16 weekly.
No crash, no host-side death, nothing unclassified. The portfolio was not so
lucky: 55 cap hits elsewhere, all in HQ's own seats and in ursa, atelier and
epitome, which belong to the exo centralizer rather than here.

**The writer row is the one that needs saying rather than re-measuring.** 149
against 150 is one turn from an exhaustion, and it is the **fourth consecutive
sweep** to put this seat over the trigger. The ask is already written and
already delivered: Ask 4 of the 2026-10-24 entry on `docs/agents/hq-relay.md`,
which asks for 225 because that is the number the owner already approved, with
the measured rule's larger figure noted. The manifest still reads
`max_turns = 150`, confirmed by reading it again in this run. So this is not a
new ask and re-filing it would be noise. What is new is the count, and the
count is the argument: a delivered ask that has survived four measurements is
evidence about the queue rather than about the measurement.

**And one thing this sweep cannot see, named so no reader infers coverage.** A
peak is the highest turn count among runs that **finished**. Sixteen of this
company's weekly refusals killed runs before they could reach their own peak,
and this week's own 14:00Z cron died at turn one. A week with heavy refusals
therefore reports a lower peak than the same week with capacity, so every
percentage above is a floor and never a ceiling. Read a refusal-heavy week's
cap table as the weakest reading of the headroom rather than the truest one.

## The rule-5 line for 2026-10-26, which is a count rather than a re-derivation

**Window: 2026-10-25T23:45Z to 2026-10-26T00:11Z**, the 26 minutes between this
seat's previous run and this one. A window that short cannot re-derive a table
and is not offered as one. It is recorded because one row crossed the trigger
in it and the count is the argument.

| Seat | Runs | Peak turns | Cap in force | Percent | Over rule 5's 70% |
|---|---|---|---|---|---|
| writer | 1 | 145 | 150 | **96.7%** | yes, **fifth consecutive** |
| exo | 1 | 97 | 200 | 48.5% | no |
| engineer | 1 | 25 | 200 | 12.5% | no |
| pm | 3 | 37 | 300 | 12.3% | no |

Numerator from `run.end` rows in `/srv/asc/state/.epito/audit.jsonl`,
denominator from `max_turns` in `/srv/asc/roster/alexandria/<seat>/agent.toml`,
which is the file the host enforces. Both halves read, neither quoted.

**The ask is not re-filed and that is deliberate.** Ask 4 of the 2026-10-24
entry on `docs/agents/hq-relay.md` is delivered and asks for 225, the figure
the owner already approved. The manifest still reads `max_turns = 150`, read
again in this run. A fifth measurement of one seat sitting one turn from
exhaustion is evidence about the merge queue rather than about the
measurement, so what this line adds is the number five.

**Zero cap hits in this company in the window**, and zero non-success rows of
any kind. The two failures the host recorded in the same minutes belong to
`ursa-exo` and `epitome-engineer`.

## The writer's raise landed on disk 2026-10-26T14:41Z and the host is still enforcing 150

**This heading stopped being true at 2026-10-26T15:32:23Z and the correction is
the subsection at the end of it.** It is left standing because the three-state
table below is the record of the defect, and because the state it could not read
turned out to be readable all along.

Ask 4 of the 2026-10-18 decision-056 entry, five times measured on this page
and open for eight days, was **granted**. `alexandra-systems` pull request 521
raised `runtime/agents/alexandria/writer/agent.toml` from `max_turns = 150` to
`225`, with the reason written into the file beside the number rather than only
into the pull request. It was merged by the owner at **2026-10-26T14:40:18Z**
and reached the host's roster clone at **14:41:24Z**.

**It is not in force, and the heading says so on purpose.** Three states, read
at the same minute:

| State | Reads | Why |
|---|---|---|
| declared, parent `main` | 225 | merged 14:40:18Z |
| deployed, host disk | 225 | clone reset 14:41:24Z |
| **loaded, the daemon** | **150** | started 06:25:03Z, no reload route |

### Corrected 19:20Z the same day: the raise is in force, and the third state was never unreadable

Two things moved, and the second is worth more than the first.

**The cap is live.** The daemon restarted at **2026-10-26T15:32:23Z**
(`state.json`'s own `startedAt`, pid 168995), 52 minutes after the grant reached
disk, and picked the new number up. So Ask 4 is **LANDED** after eight days.

**And the loaded state was readable from the start.** The reason this page said
"no reload route" is that `state.json` carries no `max_turns` field, which is
true and is a fact about `state.json`. The host writes the cap it passed the
provider into every run's own log:

```bash
grep -o -- '--max-turns [0-9]*' "$(ls -t /srv/asc/state/.epito/logs/<seat>/*.log | head -1)"
```

That is **better** evidence than the field that was looked for, because
`state.json` would say what the daemon intends for the next run and the
invocation line says what was enforced on a run that happened. The hour the
grant took effect is bracketed by two of the writer's own logs:

| Run log | `--max-turns` |
|---|---|
| `2026-10-26T14-56-40-255Z-message.log` | **150** |
| `2026-10-26T16-00-23-647Z-cron.log` | **225** |

**It also generalises to the whole portfolio in one loop**, which no reading of
this page has ever had: disk and invocation agree on **all 32 seats of all five
companies** at 19:20Z. That is a far stronger statement about the reload gap
than one seat's divergence was, and it is the measurement that should be taken
after every roster deploy from here.

Three corrections follow for rule 6 and the rule-5 table. The writer's loaded
cap is **225**, so its best measured peak of 134 is **59.6%** and not 89.3%,
which is the reading the table below predicted a restart would produce and is
**under** rule 5's 70% trigger for the first time in six sweeps. The two kills
at `turns 151` stand as evidence about the period they happened in. And the
`turns == cap + 1` fingerprint for this seat is now `226`.

**What this does not close.** The relay entry saying the roster deploys to disk
and is never re-read stays **open**, because what happened here was a restart
and not a reload. The entry now carries a measured latency — 52 minutes, and
only because something restarted the daemon for unrelated reasons — rather than
an argument. A grant that takes effect when a process happens to die is not a
grant that takes effect.

**Still owed and now four wake runs deep:** the rule-5 re-derivations for
`engineer` (81.0%) and `skill` (71.7%). Neither moved today and neither is
blocked on anything but a run with the budget for it.

Rule 6 above now carries the mechanism. The consequence here is the one that
matters for this page: **the cap in force is the loaded one**, so until the
daemon restarts every `alexandria-writer` run is still capped at 150 and the
kill fingerprint stays `turns == 151`. The ask is recorded on
`docs/agents/hq-relay.md` as GRANTED (not live) with a corrected live test,
because the test that entry carried — `grep max_turns` on the host's
roster file — passes already and would have marked it landed.

### The two kills, and the enforcement question they settle

Every `alexandria-writer` `run.end` row of 2026-10-26, from
`/srv/asc/state/.epito/audit.jsonl`:

| Ended (UTC) | Trigger | Exit | Turns | Note |
|---|---|---|---|---|
| 00:57:47 | message | 0 | 2 | |
| 00:58:31 | message | 1 | 1 | provider refusal |
| 04:45:39 | hook | 0 | 3 | PR 534 |
| **05:36:58** | message | **1** | **151** | **kill** |
| 06:14:13 | message | 0 | 134 | PR 550 |
| 06:22:24 | message | 1 | 14 | |
| **09:42:05** | hook | **1** | **151** | **kill** |

Both kills are `cap + 1` with a non-zero exit, which is rule 1's censored case
and this page's own stated fingerprint. They are the **first cap hits in this
company** since the register began tracking: the 2026-10-25 sweep recorded zero
over the whole preceding week, with all 35 non-zero exits being provider
refusals.

**They also answer, in one direction, the question this page has carried open
since 2026-10-18.** The writer's 2026-10-18T07:50:15Z row is 153 turns at
exit 0 against the same cap of 150, and the page could not say whether the 150
bound that run at all. Today the same cap bound twice, at 151, with the
documented signature. So the enforcement mechanism works as described, and the
153/exit-0 row is an anomaly against a working mechanism rather than evidence
of an absent one. It remains unexplained. It is no longer the only reading.

### The rule-5 line for 2026-10-26, computed against the loaded cap

Window: the whole of 2026-10-26 UTC. Numerator from `run.end` rows in the audit
log; denominator from the **loaded** roster copy, which is
`/srv/asc/repos/alexandra-systems` at `c914672`, the disk standing at the
daemon's `startedAt` of 06:25:03Z. Peak excludes killed runs, which are
censored and set a floor rather than a measurement.

| Seat | Runs | Free peak | Loaded cap | Disk cap | Percent | Over 70% |
|---|---|---|---|---|---|---|
| writer | 7 | 134 | **150** | 225 | **89.3%** | yes, sixth consecutive, plus two kills |
| engineer | 14 | 162 | 200 | 200 | **81.0%** | yes |
| skill | 3 | 129 | 180 | 180 | **71.7%** | yes |
| exo | 5 | 101 | 200 | 200 | 50.5% | no |
| pm | 36 | 125 | 300 | 300 | 41.7% | no |
| frontend | 5 | 150 | 600 | 600 | 25.0% | no |
| finance, market, okr, research, sales, security | 0 | — | — | — | — | not measurable |

**Three seats over the trigger, listed per row rather than summarised**, which
is the correction the 2026-10-24 section made about its own first draft.

**The writer is the only seat in this company whose loaded and disk caps
differ**, checked across all twelve rather than assumed from the one that
changed. That is worth stating because it is the number that will move: a
restart makes the divergence zero and makes the writer's row 134/225 at 59.6%,
under the trigger for the first time in six sweeps.

**And 225 is below what the measured rule asks for.** Rule 1 says a killed run
is a lower bound, so the writer's demand is known only to be above 150. The
largest free-running observation on record is 153 turns (2026-10-18), and twice
that rounded up to the next 50 is **350**. 225 is the number the owner had
already approved and it is the number that stops today's kills; it is not the
number the rule derives. The writer row therefore stays marked unmeasured, and
the first free-running run above 112 turns under a loaded cap of 225 re-derives
it.

## The writer's raise is loaded now, and HQ's own seat is the same defect inverted (2026-10-26 20:20Z, message wake)

Two readings close and one opens, and they are the same measurement taken on
three surfaces rather than one.

**The writer is landed, and the restart boundary is visible to the run.**
`/srv/asc/roster/alexandria/writer/agent.toml` reads `max_turns = 225`, and the
invocation lines straddle the daemon restart of **2026-10-26T15:32:23Z**
exactly: `--max-turns 150` for the run started **14:56:40Z**, with the manifest
already changed and the daemon not yet restarted, and `225` for every run
started after it — 16:00:23Z, 19:03:27Z, 19:54:45Z. The run started 19:03:27Z
took **124 turns to exit 0** rather than dying at 151. The divergence this page
recorded at 14:41Z is closed by measurement, and the seat's last
`error_max_turns` kill ran 09:02:46Z to 09:42:04Z, before the restart.

**HQ's `exo-centralizer` is the same two surfaces disagreeing in the opposite
direction, and it is the one that is still live.** That seat's most recent cap
kill **started 19:23:27Z and ended 19:55:33Z** at **151 turns**, with
`error_max_turns` written in its own log beside the `--max-turns 150` it was
given. It started **4h29m after that seat's manifest changed** and **3h51m
after the daemon restart**.

| surface | reading | time |
|---|---|---|
| `/srv/asc/roster/exo-centralizer/agent.toml` | `max_turns = 225` | changed in `075141b`, **2026-10-26T14:54:31Z** |
| invocation, run started 19:23:27Z | `--max-turns 150` | after the change *and* the restart |
| that run's outcome | 151 turns, `error_max_turns` | `turns == cap + 1` |
| invocation, run started 19:55:34Z | `--max-turns 150` | still 150 |

**All twelve invocations of that seat readable today carry `--max-turns 150`**,
including both that started after the restart. Its other `error_max_turns` kill
of the day ran 09:44:51Z to 10:13:50Z, also at 151.

**Two explanations are ruled out before the third is offered.** It is not
unmerged: the value is on the host's disk, in the file the host reads, changed
by a commit the deployed `HEAD` (`7606036`, 16:08Z) contains. It is not waiting
on a reload either, and the writer is the positive control on that very same
restart: cap 150 for the run started 14:56:40Z, cap 225 for every run started
after 15:32:23Z. One restart, two seats, and only one of them picked up its new
number.

**The control, because one seat reading oddly is not a finding.** Disk against
invocation, read the same minute on three company seats:

| seat | disk | invocation | agrees |
|---|---|---|---|
| `alexandria-writer` | 225 | 225 | yes |
| `alexandria-skill` | 180 | 180 | yes |
| `alexandria-exo` | 200 | 200 | yes |
| `exo-centralizer` | **225** | **150** | **no** |

So the mechanism works and that seat is the exception. And the rest of its
manifest is reaching the daemon: `state.json` holds `cron = "0 23 * * 0"` and
`model = "claude-opus-5"` for it, both matching the file exactly. Every field
checked is current except the one that kills it. The cause is in HQ's host and
is not this seat's to diagnose; the measurement and the control are, and they
went back on the board in the run that took them.

### Rule 9: a cap lives on three surfaces, and a disagreement between them after a deploy and a restart is the finding rather than a verdict

HQ's rule of 2026-10-26, which this seat asked for, is that **a grant is read
off a run that already happened, never off the manifest that intends the next
one.** That is right, and it is half of it. The three surfaces answer three
different questions and none of them is "the cap":

- the **manifest on disk** says what the host will pass to the next invocation;
- the **invocation line in the run log** says what a run was actually given,
  and it is the only one that can kill anything;
- the **run record** says what that run then did with it.

A run record is therefore a reading *as of an invocation*, so it dates. Read
HQ's rule alone and the centralizer's seat says "150 on every run today,
therefore not granted" — which is what its own seat concluded about itself, and
it is false. The missing clause: **when the disk and the invocation disagree
after the manifest changed and the daemon restarted, neither one is the answer
and the disagreement is the thing to report.** The cheap discriminator is one
command, needs no network, and every run log carries it:

```bash
grep -oE '\-\-max-turns[= ][0-9]+' "$(ls -t /srv/asc/state/.epito/logs/<seat>/ | head -1)"
```


### Rule 10: the two surfaces that date a run use opposite timestamps, and this page conflated them once

Added 2026-10-26 20:35Z, by the run that made the error and caught it on a
control.

- a `run.end` row's `ts` in `/srv/asc/state/.epito/audit.jsonl` is the run's
  **end**;
- a log filename in `/srv/asc/state/.epito/logs/<seat>/` is the run's
  **start**, and that file's mtime is its end;
- the board's `started_at` is the start, so **the board and the audit log do not
  agree on which end of a run a single timestamp names.**

So a `151` beside an audit `ts` and a `150` beside a log of the same clock time
are two different runs, and reading them as one is how this section first said
`exo-centralizer` "died at 19:55:34Z" when 19:55:34Z is when its *next* run
began. The kill ran 19:23:27Z to 19:55:33Z. The correction strengthened the
finding rather than weakening it, which is luck and not a defence.

The reading that settles a cap needs no join at all, because the cap, the
outcome and the turn count are all in the same file:

```bash
d=/srv/asc/state/.epito/logs/<seat>; f=$(ls -t $d | head -1)
grep -oE '\-\-max-turns[= ][0-9]+' "$d/$f"
grep -c error_max_turns "$d/$f"
grep -oE 'num_turns"?:[[:space:]]*[0-9]+' "$d/$f" | tail -1
```

**The general form, and it is why this is a rule rather than a footnote: when
two surfaces both carry a timestamp for the same object, check which end of it
they name before you join them.** A wrong join of this kind is silent. Both
rows exist, both parse, and the pair tells a coherent story about a run that
never happened.

## Re-derived 2026-10-26 20:55Z, on five cap hits in one day, which is every cap hit this company has ever had on the host

**Trigger: rule 1 and rule 5 together.** §6 of `prompts/exo-agent.md` says
re-derive immediately in any run where a cap was hit. Three were hit in the
ninety minutes before this run started, and the day holds five.

### The five, and the window they are all in

Read off each run's **own invocation line** rather than off the manifest, which
is rule 9 of this page: the number that killed a run is the number that run
loaded.

| Started | Seat | Cap that run loaded | Turns | Terminal |
|---|---|---|---|---|
| 04:53:06Z | writer | 150 | 151 | `max_turns` |
| 09:02:46Z | writer | 150 | 151 | `max_turns` |
| 19:30:45Z | skill | 180 | 181 | `max_turns` |
| 19:58:19Z | engineer | 200 | 201 | `max_turns` |
| 20:06:55Z | skill | 180 | 181 | `max_turns` |

**The denominator is the part worth reading.** The host keeps 341 alexandria run
logs carrying a result line, the oldest started 2026-09-26T01:10:32Z, and
**five of the 341 are cap hits. All five are on 2026-10-26.** Zero in the thirty
days before it. So this is not a drift, it is a step, and it is the first day on
which this company's caps have cost it work since the seats moved to the host.

The two writer rows are closed. The raise to 225 loaded at 15:32:23Z and that
seat's peak after it is 165, so neither of its kills can recur at the number it
now carries. **The skill and engineer rows are open and they are the finding.**

### The rows, re-derived under the rule

The rule is at the top of this page: at least twice the highest observed turn
count, rounded up to the next 50, floor 100. Rule 1 governs what "observed"
means here, and it matters: a cap hit records the cap plus one rather than the
work's demand, so 181 and 201 are **floors and not measurements**, and both
seats are marked unmeasured until a run of each finishes freely above its old
peak.

| Seat | Censored lower bound | Free-running peak today | Cap in force | Required by the rule | Percent | Verdict |
|---|---|---|---|---|---|---|
| skill | **181**, twice, 36 minutes apart | 129 (14:17:47Z) | 180 | **400** | **100.6%** | **UNMEASURED and under-capped. Two kills.** |
| engineer | **201** | 162 (04:41:51Z) | 200 | **450** | **100.5%** | **UNMEASURED and under-capped. One kill.** |
| writer | 151, twice, both pre-raise | 165 (19:54:45Z) | 225 | 350 | 73.3% | raise landed, kills closed, **still over rule 5's 70%** |
| exo | none | 166 (19:03:27Z) | 200 | 350 | **83.0%** | over rule 5's 70%, no kill yet |
| pm | none | 125 | 300 | 300 | 41.7% | ok |
| research | none | 94 | 180 | 200 | 52.2% | ok |
| frontend | none | 150 | 600 | 300 | 25.0% | ample |

Numerator from the `num_turns` in each run's own result line under
`/srv/asc/state/.epito/logs/alexandria-<seat>/`. Denominator from the
`--max-turns` on that same run's invocation line, cross-checked against
`max_turns` in `/srv/asc/roster/alexandria/<seat>/agent.toml`, which agreed for
every seat in this table. Both halves read, neither quoted.

### What this page already knew, and for how long

This is the part that makes it an argument rather than a table. **The
2026-10-11 re-derivation on this page already carried both rows as short**, with
the required figures computed: `skill 156 → 350, short, item 14, unchanged` and
`engineer 184 → 400, short. Item 14's 350 was below the rule before it was
read`. Fifteen days later the required figures have grown to 400 and 450,
nothing was applied to either seat, and on the sixteenth day both seats were
killed by the number the page had already called short.

The writer's row is the control, and it is the useful half. Its verdict on
2026-10-11 was the same word, `short`. The difference is that one seat's raise
became an explicit ask with a cost attached and got granted inside eight days,
and the other seats' identical verdicts stayed table cells. **A verdict in a
column is not an ask**, which is this register's own "recording is not
enforcing" with the register being this one.

### Correction to "Who applies a cap change", which is stale and would misroute this ask

That section says cap changes are written into
[pending-workflow-changes.md](pending-workflow-changes.md) and applied by the
chair or the owner, because no agent run can push `.github/workflows/`. The
premise is still true and the conclusion no longer is. Rule 6 of this page says
a cap lives in two files and only one of them runs the seat, and the one that
runs it is `max_turns` in `runtime/agents/alexandria/<seat>/agent.toml` in
`alexandra-systems`. That is a manifest and not a workflow, so the `workflow`
scope has nothing to do with it.

**The live route is the relay page, and the writer's raise is the proof.** Ask 4
of the 2026-10-24 entry in `docs/agents/hq-relay.md` went to
`alexandra-systems/exo-centralizer` as a handoff, the owner approved 225, HQ
wrote the manifest at 14:54:31Z, and the host loaded it at 15:32:23Z. Nothing
touched `pending-workflow-changes.md` at any point. A run that reads the old
section today files its ask where the one surface that acted on a cap this month
does not look.

So: **a cap change for a company seat leaves through `docs/agents/hq-relay.md`
as a handoff to `alexandra-systems/exo-centralizer`, per §3f.** The workflow
route stays recorded above for the Actions-era history it explains, and it
governs nothing.

### The ask, filed rather than tabled

Filed on `docs/agents/hq-relay.md` in this run and delivered in the same run,
which is rule 1 of §3f. It asks for skill at 400 and engineer at 450, names the
floors of 181 and 201 so a smaller raise can be argued against a number, and
carries the cost, which is three runs killed in thirty-six minutes on the one
day this company has ever lost a run to a cap.

**The live test, which needs no network:**

```bash
grep max_turns /srv/asc/roster/alexandria/skill/agent.toml      # 180 today, want 400
grep max_turns /srv/asc/roster/alexandria/engineer/agent.toml   # 200 today, want 450
```

And the one that says the raise is loaded rather than merely on disk, which is
rule 9's lesson and the writer's whole eight days:

```bash
ls -1t /srv/asc/state/.epito/logs/alexandria-skill/ | head -1 | \
  xargs -I{} grep -ho '\--max-turns[= ][0-9]*' /srv/asc/state/.epito/logs/alexandria-skill/{}
```
