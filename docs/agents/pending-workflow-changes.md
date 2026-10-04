# Workflow changes the agents cannot apply themselves

**Enforced at:** prompts/exo-agent.md §5, which verifies each queued
item against the live workflow files every run.

## The one structural blocker, for the owner

**No agent seat can fix the machinery that runs it.** Every cap raise,
every tripwire, every timeout change on this page has to pass through a
human hand, and that is the single reason this page exists.

The mechanism, verified by attempting it (incident 12): GitHub refuses
any push from `GITHUB_TOKEN` that touches a file under
`.github/workflows/`, with

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/agent-engineer.yml` without `workflows` permission
```

This is not a misconfiguration. There is no `workflows:` key to add to a
workflow's `permissions:` block, because `GITHUB_TOKEN` cannot hold that
scope at all. Only a personal access token carrying the `workflow` scope
can push these files.

**What it costs, concretely.** On 2026-09-18 six runs failed, all of
them turn-cap collisions, and not one of the seats affected could raise
its own cap. The chair applied every fix by hand. The caps are current
now (item 3 below), and the cost has moved to a sharper place: on
2026-09-20 the PM seat lost a whole run to a two-line workflow condition
that no seat could change (item 1b, incident 23).

**The decision that is yours, and only yours.** Mint a PAT with the
`workflow` scope, store it as a repository secret, and pass it to
`actions/checkout` in the agent workflows. That would let the seats
repair their own machinery, which is the autonomy tiebreak in vision.md
§0 pointing one way. It would also hand every agent run a token strong
enough to rewrite what runs the agents, which is an authority change
rather than a convenience. Both things are true at once, which is why
this seat states the tradeoff and does not decide it.

**Until you decide, the standing arrangement holds:** workflow edits are
written out here in full, ready to apply, and the chair or you applies
them. Nothing here is blocked on analysis. It is blocked on a hand.

---

## Two lanes, and which change takes which

**Added 2026-09-27, because this page described one lane for eight days
after the org started using two.** The push is refused for paths under
`.github/workflows/` and for nothing else. So there is a second lane, and
it is better than this one wherever it applies.

| The change | The lane | What the owner does |
|---|---|---|
| A **new** workflow file | commit it to `.github/workflows-pending/`, with a section in that directory's README | `git mv` it one directory up |
| An **edit** to a workflow that already exists | a diff on this page, with every anchor verified against the live file | apply the diff by hand |

The engineer seat found the second lane on 2026-09-19 and has used it
four times since; `.github/workflows-pending/checks.yml` is the standing
example and it is still waiting for the move. Nothing in that directory
runs, which that README states plainly, so anything sitting there is a
guard that is not guarding yet. Audit it every run the same way this page
is audited.

**Why an edit does not get the better lane, which is the part worth
understanding before someone improves on this.** Pushing a full modified
copy of an existing workflow would also work and would also reduce the
owner's hand-work to a `git mv -f`. It trades a loud failure for a silent
one. A diff's anchor stops matching the moment the live file moves under
it, and the item is then visibly rotted, which is the entire mechanism of
the re-verification rule in `prompts/exo-agent.md` §5 and the only reason
incident 26 was caught before a hand applied it. A full copy taken on
Monday and moved on Sunday applies cleanly and silently reverts every
edit made in between. The owner edited these twelve files three times in
one week without a pull request, so that is not a hypothetical here.

Where a queued edit has grown too large to read as a diff, split the
item. Do not switch its lane.

---

Applied items get deleted from this file by the next ExO run, which
verifies against the workflow files themselves rather than trusting this
page.

---

## Pending, queued 2026-09-18 by the ExO agent

### 2. The PM goes daily, so the org has a seat that is present

**CANCELLED IN PART 2026-09-27. Read this paragraph and then decide
whether to read any further.** The cadence half was applied on
2026-09-23 and the README half has been applied too. The remaining half
is the cap raise from 300 to 400, and the standup's share of it is now
cancelled on measurement rather than on judgment. Four standup runs have
completed since the split (2026-09-24, 25, 26, 27) and their turn demand
is 62, 44, 81 and 38 against a cap of 300. The rule in
[turn-caps.md](turn-caps.md) is twice the peak, which gives 162. There is
no shortfall and there is no headroom argument left either.

What survives is narrower and it is honest about being unmeasured: **the
Monday ceremony run has not completed once since the cron split.** The
last Monday, 2026-09-21, failed at turn 30. Its last good measurement is
a peak of 141 from before the split, when the ceremony and the standup
were one run, and the ceremony has since taken the grooming and the
dispatch queue that the standup does not carry. So the ceremony's cap is
the one open question on this item, and the next ExO run answers it from
the 2026-09-28 run rather than from a feeling. **Until then, apply
nothing on this item.** If 2026-09-28 comes in under 150 like the
standups, delete the item.

The two `-` anchors below still match the live file exactly once each, so
the item is not rotted. It is simply not evidenced, which is a different
and more common reason not to apply something.

**Queued 2026-09-19 by the ExO agent, on the owner's order. THE CADENCE
HALF WAS APPLIED 2026-09-23 by the chair, in commit 2ae2650, and the cap
half was not. Read the next three paragraphs before the diffs below,
because two of them are now historical.**

**What the chair applied, and it is better than what this page
proposed.** This item asked for one daily cron, `35 10 * * *`, with the
charter branching on the day. The live file instead carries two crons,
`35 10 * * 1` for the Monday ceremony and `5 11 * * 0,2-6` for the
standup, plus a `RUN_MODE` env var computed from
`github.event.schedule` and `actions: write` for the dispatch grant. Two
crons and an explicit mode beat one cron and a charter that has to infer
the day, because the run knows which schedule fired it and never has to
reason about the calendar. Recorded here as the correction it is: this
page proposed the cheaper version and the chair shipped the better one.

**What was not applied: the cap. And this run is downgrading its own
predecessor's proposal rather than repeating it.** `agent-pm.yml` still
reads `--max-turns 300` on both steps, and both `-` lines below match
the live file exactly, once each. But the duty-growth re-check in
turn-caps.md, run today, gives 300 as the rule's answer: the PM's peak
is 141, twice that rounds to 300, and the peak has not moved because the
seat has not completed a run since 2026-09-19. So **the raise to 400 is
optional headroom, not a shortfall, and whoever applies this page should
feel free to skip it.** The methodology exists to stop caps being set
from a feeling that a seat has more to do, and the feeling in question
was this seat's own on 2026-09-21. The two failed PM runs died at turn 1
and turn 30 and contribute nothing in either direction.

**What is now moot.** The cron diff and the two documentation lines
below are superseded by what the chair shipped, and as of 2026-09-27 the
two documentation lines are moot for a second reason: README.md already
reads `pm · daily, Mon is the ceremony` in the STEER node and
`daily 6:35 ET standup, Mon is the ceremony` in the seat table, so both
`-` anchors for those lines are gone from the live file. Verified this
run. They are left in place
rather than deleted so that the next reader can see what was proposed
against what landed, and they are marked here rather than there.

**Original item follows.**

**Why.** Her words: "right now i feel like im doing the PMs job, i want
the pm to be proactive." The evidence is one day. On 2026-09-19 the org
started twenty-five agent runs and opened fifteen pull requests, and the
PM seat ran zero times, because `35 10 * * 1` fires once every
168 hours. A seat that is awake for one hour a week in a company that
changes state every forty minutes cannot be proactive no matter what its
charter says, so the charter half of this fix (prompts/pm-agent.md
sections 0, 4 and 5) is worth nothing until this cron changes. The
diagnosis in full is in docs/agents/learning-log.md under the presence
gradient.

**REWRITTEN 2026-09-20 by the ExO agent, because the diffs below had
rotted.** When this item was queued on 2026-09-19, `agent-pm.yml` had
one run step. Commit 609d7cc added a second one four hours later (open
routing, PR #49), and the queued diffs targeted lines that now exist
twice or not at all. Applying the old version would have raised the cap
on the Sonnet step that never runs, rewritten one of two identical
prompt blocks, and left the live open-routed step untouched. The diffs
below are checked against the file as it stands today. Whoever applies
them should still diff before committing, because this page is only as
fresh as the last ExO run.

**REWRITTEN AGAIN 2026-09-21, because two of the diffs had rotted a
second time.** Commit 440163a raised the timeout from 60 to 120 and
renamed the model flag from `sonnet` to `claude-sonnet-5`, five hours
before the 2026-09-20 run that re-verified this item. That run checked
the step structure, which is what had broken the first time, and did not
re-check the values inside the steps. This is incident 26, and the rule
it produces is below in item 3's note: **re-verify every line of a queued
diff against the live file, not the part that broke last time.**

**How.** Four edits to `.github/workflows/agent-pm.yml`, plus the prompt
rewrite in both run steps. The cron change is one character.

```diff
 on:
   schedule:
-    - cron: "35 10 * * 1" # 6:35 AM ET Mondays
+    # Daily at 6:35 AM ET. Monday is the ceremony run (retro, grooming,
+    # sprint plan, and the day's dispatch queue); every other day is the
+    # standup alone. prompts/pm-agent.md section 0 branches on the day,
+    # so one workflow covers both modes and there is no second file to
+    # keep in sync.
+    - cron: "35 10 * * *" # 6:35 AM ET daily
   workflow_dispatch:
```

**The timeout edit is CANCELLED.** It read
`-timeout-minutes: 60 / +timeout-minutes: 75` when it was queued. Commit
440163a raised the PM's timeout to 120 on 2026-09-20, so the anchor no
longer exists and applying the diff's intent would **lower** the timeout
by 45 minutes. Nothing to do here. 120 is more than the 75 this item
wanted.

Both turn caps move, because either step can be the one that runs. The
open-routed step is the one that fires today, so leaving it at 300 would
make the raise a no-op.

```diff
-          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
```

```diff
-          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model claude-sonnet-5"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model claude-sonnet-5"
```

**The second one's model flag was corrected on 2026-09-21.** It read
`--model sonnet` through two ExO runs. Commit 440163a renamed it to
`--model claude-sonnet-5` on 2026-09-20 at 12:34, which was five hours
before the run that rewrote this item against the live file and did not
catch it. See incident 26.

And the prompt block, replaced in full **in both steps**. The file
carries two identical copies, one per run step, and a PM that behaves
differently depending on which model served it is a bug waiting for the
day the fallback fires:

```yaml
          prompt: |
            You are alexandria's project manager agent (ADR-15 in
            docs/decisions.md), running in GitHub Actions with this repository
            already checked out. Read prompts/pm-agent.md; it is your full
            charter. Section 0 tells you which of two runs this is. On Monday,
            or when the owner instructions below say so, execute the ceremony
            run: retrospective on the ending sprint, grooming of
            docs/ideas.md, the new sprint file in docs/sprints/ in the format
            docs/sprints/README.md defines, and then the dispatch queue of
            section 4. On every other day, execute the standup run of section
            4 alone and nothing else: read fleet state, open PRs, pending, the
            board and the newest rulings, then write
            docs/sprints/dispatch-queue.md with at most three proposed
            dispatches, each one a copy-pasteable `gh workflow run` command
            with its owner_instructions drafted in full. You propose
            dispatches; you never fire them, because section 5 is dormant
            until the owner activates it. Commit on a branch named
            pm/sprint-YYYY-MM-DD for a ceremony run or pm/standup-YYYY-MM-DD
            for a standup run, push it, and open exactly one pull request with
            `gh pr create`, carrying the dispatch queue in the PR description
            in full. You write only docs/sprints/ and grooming notes in
            docs/ideas.md. Never write code, never edit charters, never merge
            your own PR, never push to main, never touch secrets or digests/.
            If the charter file is missing, stop and fail loudly instead of
            improvising.
            Owner instructions for this dispatch, binding for this run and
            extending the charter (empty on scheduled runs):
            ${{ inputs.owner_instructions }}
```

**Apply item 1b first, or this item makes things worse.** A daily cron on
a seat whose only reachable model is the failing open-routed one turns
one failure a week into seven. The two items are ordered, not
independent.


**On the cap and the timeout, per the methodology.** The standup run is
a new run shape with no measurement, so rule 2 of
[turn-caps.md](turn-caps.md) applies and it inherits rather than guesses.
It shares the seat's cap, which is correct, because a cap is a tripwire
and not a budget and an unspent cap costs the org nothing. The raise from
300 to 400 is not for the standup. It is because Monday's ceremony run
just gained a whole section, which is duty growth, and the pm row is the
only censored measurement in the table (a run that died at 140, so real
demand is known only to be at least 141). The timeout goes to 75 to match
the rest of the fleet, which at roughly nine turns a minute clears 400
with room.

**On cost.** Seven runs a week instead of one, on sonnet, on the owner's
existing subscription. No new service and no new secret, so the cash cost
stays $0. The real cost is six more short sonnet runs a week and six more
small pull requests, and the charter caps that by requiring an empty
queue to be reported and closed cheaply.

**Two documentation lines change in the same hand, so the repo never
describes a cadence it does not have.** The ExO run that queued this
deliberately left README.md alone, because the README's job is to
describe the system as it actually is and the cron is still weekly until
someone applies the diff above. Apply these two at the same time:

```diff
-        STEER["<b>Steer</b><br/>pm · Mon<br/>okr · monthly<br/>exo · Sun"]
+        STEER["<b>Steer</b><br/>pm · daily<br/>okr · monthly<br/>exo · Sun"]
```

```diff
-| pm | Mon 6:35 ET | sprints, backlog, board, org chart | ADR-15 |
+| pm | daily 6:35 ET, Mon is the ceremony | the day's dispatch queue, sprints, backlog, board, org chart | ADR-15 |
```

**How to tell it worked.** One test, and it is the owner's to judge: a
week goes by in which she dispatches seats without composing a single
instruction herself, because the queue had already drafted them.

### 4a. The writer's dispatch prompt forbids the duty this PR assigns it

**Queued 2026-09-21 by the ExO agent. This is the item that makes the
rest of this pull request work, and without it the charter edits are
inert.**

**RE-VERIFIED 2026-09-27, unchanged and still unapplied on its sixth
day.** All three `-` lines below were grepped against the live
`.github/workflows/agent-writer.yml` this run and each appears exactly
once, at lines 40 to 42. Nothing has rotted. This item is the second
hand that incident 25's fix needs, so for six days the writer charter has
told that seat to draft site copy and the prompt it actually reads has
forbidden it. Incident 13 is the precedent for what a correct fix costs
while it waits, and it waited through sixteen pull requests.

**Why.** `.github/workflows/agent-writer.yml` line 40 carries this
sentence in the inline prompt the seat reads before anything else:

```
            Never edit taste.md, charters, site copy, pipeline code, sprints,
            or skills. Never merge your own PR, never push to main.
```

The owner's ruling of 2026-09-19 gave site copy drafting to this seat.
This PR corrects the charter to match. The workflow prompt still forbids
it, and the workflow prompt is the instruction that arrives last and
closest, so a seat holding both will most likely obey the prohibition.

This is worth stating as a general finding, because it changes what a
charter edit means. **Every seat's real charter is two files.** There is
`prompts/<seat>-agent.md`, which this seat can edit, and there is the
inline prompt inside `.github/workflows/agent-<seat>.yml`, which it
cannot. When the two disagree, the org has no way to know which one the
run obeyed. Incident 25's fix is the first time the disagreement has been
load-bearing, and it will not be the last: the prompts were written on
2026-09-18 and have been copied between seats since.

**How.** One edit to `.github/workflows/agent-writer.yml`. Remove the two
words that contradict the ruling and say what the seat may do, since
"never set it on the site" is still correct and still worth keeping.

```diff
-            Never edit taste.md, charters, site copy, pipeline code, sprints,
-            or skills. Never merge your own PR, never push to main. If the
-            charter file is missing, stop and fail loudly.
+            Never edit taste.md, charters, pipeline code, sprints, or skills.
+            You DRAFT reader-facing site copy into docs/voice/ when the run
+            calls for it, and you never SET it in site/, which is the
+            frontend seat's surface (docs/agents/copy-pipeline.md). Never
+            merge your own PR, never push to main. If the charter file is
+            missing, stop and fail loudly.
```

**Ordering against item 4.** Same file, and they do not overlap: 4a edits
the `prompt:` block and 4 edits the `claude_args:` line one line below it.
Apply either first. Do read both before committing, because they are two
hunks in a nine-line window.

**Cost.** $0.

**The wider sweep this implies, and it is not queued.** Every
`agent-*.yml` carries a prompt written by hand, and no seat has ever
diffed its inline prompt against its charter. That check belongs in this
seat's §2 and the charter edit is in this PR. The audit itself is the next
run's work, because finding a second contradiction is a run's worth of
reading and this run has one confirmed case to fix.

### 4. The writer's cap goes to 200

**Queued 2026-09-21 by the ExO agent.** Measured, not guessed. See the
2026-09-21 duty-growth re-check in [turn-caps.md](turn-caps.md).

**RE-VERIFIED 2026-09-27, unchanged.** The one `-` line below appears
exactly once in the live file, at line 46. The writer has run daily since
and its runs have all concluded `success`, so the evidence behind the
raise has not moved in either direction. Still worth applying: a cap
below the measured rule is a run that dies without warning, and the
writer is the seat whose duties grew most this month.

**Why.** The writer's cap of 150 was derived on 2026-09-19 from two runs
whose peak was 53. The seat runs daily now and has run eight more times,
peaking at **80 turns** in run 35459141039. The standing rule is twice the
peak rounded up to the next 50, which is 200. So the cap is below the rule
already, and this run also gave the seat three new duties: drafting site
copy, drafting the value statement, and recording preference data. No
writer run has hit the cap, which is exactly why nobody noticed.

**How.** One edit to `.github/workflows/agent-writer.yml`. The file has a
single run step, verified 2026-09-21.

```diff
-          claude_args: "--max-turns 150 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 200 --permission-mode bypassPermissions --model claude-opus-5"
```

The writer seat runs on `claude-opus-5`, not on Sonnet. This diff was
first written here with the Sonnet flag, from memory rather than from the
file, and the incident 26 rule caught it in the same run that wrote the
rule down. Recorded because it is the cheapest possible demonstration that
the rule is worth running: grep the live file for every `-` line, every
time, including the ones you just typed.

**Ordering.** Independent. No other item on this page touches
`agent-writer.yml`, so it can be applied in any order with respect to
items 1b and 2.

**Cost.** $0 unless a run uses the turns. A cap is a tripwire and not a
budget.

### 5. An HQ-origin commit should announce itself when it lands

**MOVED OUT OF THIS PAGE 2026-09-27. Do not apply it from here.** This is
a new workflow file, so it takes the other lane. The file is now
`.github/workflows-pending/hq-origin-notice.yml`, written out in full,
YAML-parsed, and one command from live:

    git mv .github/workflows-pending/hq-origin-notice.yml .github/workflows/hq-origin-notice.yml

The prose below is kept as the reasoning behind it, and the file's own
header comment carries the short version so the reasoning travels with
the artifact. Two changes were made to the YAML on the way across, both
recorded in the file: a `timeout-minutes: 5`, and an explicit
`shell: bash` on the run step, because
`INC-2026-09-26-run-report-dash-echo` is what an unstated shell cost the
org five days after this item was queued.

**Its trigger fired this week, which is the argument for moving it.**
Commit `1baeb7f` on 2026-09-25 changed how this repository deploys to
production, citing HQ Incident 5, and `grep -rn "HQ Incident 5" docs/`
returns nothing. The marker grep in this job matches that commit's
subject, verified against the live log this run.

**Queued 2026-09-24 by the ExO agent. Incident 23, and the cadence gap
recorded against the new row in unowned-duties.md.**

**Why.** §3f of the ExO charter now requires that every HQ decision
reaching this repository is read against local law. The trigger for that
duty is a merge, and merges do not respect a weekly cron. ADR-015 landed
on a Friday evening and was first read on a Sunday, after it had already
failed two PM runs. A weekly seat holding a merge-triggered duty is the
same cadence gap this org has already written down twice, and the
register's own rule says the fix is a cron change rather than another
sentence in a charter. Here the correct fix is not a cron at all, since
the trigger is an event.

**How.** A new workflow, `.github/workflows/hq-origin-notice.yml`, that
runs on push to main and does one cheap thing: if the pushed commits
carry an HQ marker, write a job summary naming them and open nothing.
No seat is dispatched and nothing is merged, so the blast radius is a
line of text in the Actions UI plus, once a seat can read it, an entry
the ExO run does not have to reconstruct from `git log`.

```yaml
name: hq-origin-notice

on:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  notice:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Flag HQ-origin commits
        run: |
          range="${{ github.event.before }}..${{ github.sha }}"
          hits=$(git log --pretty='%h %s' "$range" \
            | grep -iE 'ADR-0[0-9]{2}|HQ |company standard|vendored|centralizer' || true)
          if [ -n "$hits" ]; then
            {
              echo "### HQ-origin commits in this push"
              echo ""
              echo "$hits" | sed 's/^/- /'
              echo ""
              echo "Read these against local law before they take effect:"
              echo "docs/agents/cross-repo-law.md. The three questions are"
              echo "in prompts/exo-agent.md section 3f."
            } >> "$GITHUB_STEP_SUMMARY"
          fi
```

**What it does and does not do.** It makes an HQ-origin change visible
at the moment it lands rather than up to six days later, and it costs
one short job per push to main. It does not read the local law, it does
not block anything, and it cannot tell a real override from a commit
that merely mentions an ADR number. It is a smoke alarm, not a gate. The
judgment stays with the ExO run, which is correct, because deciding
whether a parent decision overrode a local safety clause is exactly the
kind of reading a grep cannot do.

**One honest caveat about `github.event.before`.** On a force push or a
first push it is unreliable, and the `|| true` means the step then says
nothing rather than failing. Silence on an edge case is the right
failure mode for a notifier whose backstop is a weekly human-read audit.

**Cost.** $0, a few seconds per push to main.

**Ordering.** Independent of every other item on this page.

### 3. Nothing else. The caps are done.

The earlier item 2 of this page (frontend 400 to 600, pm 250 to 300,
security 200 to 250) was applied by the chair and verified against the
workflow files in the 2026-09-19 ExO run. Every cap in the org clears the
measured rule, and the pm raise proposed in item 2 above is duty growth
rather than a shortfall. See the re-measured table in
[turn-caps.md](turn-caps.md).

### 6. The read-only database URL, for the engineer seat and now the PM seat

**Renumbered from 4 to 6 on 2026-09-27**, because this page carried two
items numbered 4 and the owner applies it by hand. Nothing else about the
engineer half changed.

Queued 2026-09-23 by the engineer agent. One line, in
`.github/workflows/agent-engineer.yml`, in the job's existing `env:`
block beside `GH_TOKEN` and `PROJECTS_TOKEN`:

```yaml
      NEON_RO_URL: ${{ secrets.NEON_RO_URL }}
```

The secret already exists and the research, writer and skill workflows
already read it, so this adds no new credential to the org, only an
existing one to a seat that cannot do its job without it.

**The same line, in `.github/workflows/agent-pm.yml`, added 2026-09-27 by
the ExO agent.** Identical diff, identical `env:` block, and a stronger
case than the engineer's, because the PM's is the only seat holding a
duty that is *defined* by this table.

```yaml
      NEON_RO_URL: ${{ secrets.NEON_RO_URL }}
```

Verified this run: `agent-pm.yml` does not contain `NEON_RO_URL`, and
`agent-research.yml`, `agent-writer.yml` and `agent-skill.yml` each do.

**Why the PM's need is the sharper one.** Guardrail 4 of
[delivery-health.md](delivery-health.md) defines the press's delivery
evidence as the newest row in `digests`, and assigns the daily watch to
the PM's standup. That seat has never been able to run the query. Every
standup since 2026-09-24 says so in the file, honestly, and substitutes
`libraryofalexandria.dev/library`, which is a weaker signal in the
direction that matters: a row written and never sent, a send that failed
after the row landed, and a page served from cache all read as healthy
there, and those are the three failures the guardrail exists to catch.
The full finding is in [unowned-duties.md](unowned-duties.md) under the
2026-09-27 rows, where it is the first example of a duty that passes the
wording, cadence and scope tests and fails on capability.

**Apply both at once.** They are one decision about one existing secret
reaching two more seats, and applying one without the other leaves the
question half answered. The scope note below covers both.

**Why it is queued rather than proposed.** The engineer charter's Observe
step assigns this seat pipeline health, and two ledger entries marked
`urgent` both reduce to one SQL query against the database of record. The
oldest asks whether the newsletter has sent once in eleven days, which is
a question about whether subscribers have been getting anything. Four
engineer runs have now written down that they could not run it. The
repeat is recorded in [incidents.md](incidents.md) under 2026-09-23.

**Scope, so the reader can judge the risk.** Read-only, no write path,
and no secret value ever reaches a PR. It does widen what a compromised
run can read, and from three seats to five, which is the honest cost and
the reason it is the owner's call rather than this seat's. Say no and the
right consequence is not that the guardrail stays as it is: it is that
`delivery-health.md`'s press row gets marked unwatched and the PM stops
being asked for a number it cannot get.

### 7. The ExO seat's own prompt grants it a lane the runtime refuses

**Queued 2026-09-27 by the ExO agent.** Found by the check in §2 of that
charter, which compares each seat's `prompts/<seat>-agent.md` against the
inline `prompt:` block in its workflow, and which this charter requires
whenever a run edits its own boundaries. This run edited §5.

**Why.** `.github/workflows/agent-exo.yml` tells the seat to

```
            orchestrate them as edits to the agent layer only (charters,
            agent workflows, org docs, your own charter included)
```

and `agent workflows` is not a lane this seat has. The push is refused,
verified again this run on a throwaway branch:

```
! [remote rejected] exo-probe-throwaway -> exo-probe-throwaway (refusing
to allow a GitHub App to create or update workflow
`.github/workflows/agent-exo.yml` without `workflows` permission)
```

The inline prompt arrives last and closest, so a run that believes it will
spend turns discovering incident 12 for itself. This is the same class as
item 4a, in the opposite direction: 4a is a prompt forbidding a duty the
charter grants, and this is a prompt granting a lane the runtime denies.

**How.** One edit to `.github/workflows/agent-exo.yml`, in the inline
prompt.

```diff
             decide at most three evidenced improvements, orchestrate them as
-            edits to the agent layer only (charters, agent workflows, org
-            docs, your own charter included), and write the learning log.
+            edits to the agent layer only (charters, org docs under
+            docs/agents/, and your own charter). You cannot push
+            .github/workflows/: queue edits to existing workflows as diffs
+            in docs/agents/pending-workflow-changes.md, and commit new
+            workflow files to .github/workflows-pending/ for a hand to move.
+            Then write the learning log.
```

Verified this run: the three `-` lines appear exactly once each in the live
file, at the prompt block. The seat's other prohibition list in that
prompt is consistent with the charter and is left alone, with one omission
worth noting rather than fixing: the prompt does not carry the charter's
"never set the ideas ledger's statuses", which is a narrowing the charter
supplies and the prompt does not contradict.

**Cost.** Six lines in one file, $0. It saves a run the turns it currently
spends rediscovering a four-week-old incident, and it is the only place a
seat is told the second lane exists at the moment it needs it.

**Ordering.** Independent of every other item on this page.

### 5. Every seat run reports onto the board

**Rewritten 2026-09-28.** The step is unchanged in shape and the diff below is
still one line, but everything this entry said about *why* it was safe was
written against a board that no longer exists. On 2026-09-26 the board was a
ref in this repository and the step's risk was a public ref and a contents-API
write. On 2026-09-27 the owner stood up the real board at
board.libraryofalexandria.dev and put `BOARD_API_URL` and
`BOARD_RUNTIME_TOKEN` into all twelve workflows herself, and `tools/board.py`
is now a client of it (ADR-2026-09-28-board-client). Reading the old version of
this entry and applying it would have been correct by accident: the command is
the same, the reasoning under it was wrong.

One step, identical in all twelve `.github/workflows/agent-*.yml`, placed
immediately after the existing `Post run report` step that writes to Slack:

```yaml
      # The board (docs/board.md), which pm.md §14 makes the state of the work.
      # Slack is the owner's window; the board is the org's state, and it is the
      # one a seat can read back next run. This step cannot fail the job:
      # tools/board.py prints ::warning:: and exits 0 when the board refuses,
      # because a red job for an undelivered report is the lie
      # INC-2026-09-26-run-report-dash-echo told six times.
      - name: Post run report to the board
        if: always()
        run: python3 tools/board.py report --status ${{ job.status }}
```

**It needs nothing new, and this time that is the owner's own doing.** Commit
6820ac1 already put `BOARD_API_URL` and `BOARD_RUNTIME_TOKEN` in every one of
the twelve `env:` blocks. Those two are all `tools/board.py report` reads
beyond what GitHub sets for free, plus `GH_TOKEN` for the pull request lookup,
which all twelve already have. Verified by reading the twelve files on main.

**Apply it whenever.** The old ordering caveat is void: there is no
`board/views.json` to wait for. Applied against a board that is down, the step
prints a warning and exits 0.

**Scope, so the reader can judge the risk.** The tool posts one row to
`POST /api/runs` on the owner's board and writes nothing in this repository. It
calls no model and spends nothing. What it widens is who can see a run: the
board is behind Caddy basic auth rather than public, so this is narrower
exposure than the old ref, which was world-readable because this repository is.

**One thing to know before applying it, because it cannot be undone.** The
board's server implements GET and POST only; PATCH, PUT and DELETE answer 501.
Run rows are permanent. The step runs under `if: always()` and posts exactly
once per job, so that is fine in the normal case, but a *re-run* of a job files
a second row for the same run, and no one can remove it. If that turns out to
matter, the fix is a check on `run_url` before the post, and it belongs in
`tools/board.py` rather than in the step.

**Smoke-tested before it was queued**, which is what
[runtime-changes.md](runtime-changes.md) asks of a change to what a scheduled
job does. The engineer run of 2026-09-28 ran the exact command the step runs,
against the live board, and its row is on `alexandria`'s board with this run's
pull request url and its one-line report. The `--dry-run` form was run first,
which is the only rehearsal a permanent write admits.

---

### 9. One run of a seat at a time, enforced by the runtime instead of by prose

**Queued 2026-09-26 by the engineer seat.
INC-2026-09-26-engineer-run-twice-in-one-window.**

Two engineer runs executed at once tonight, a scheduled one at 01:26:48Z and a
dispatched one at 01:30:18Z. Both opened a pull request, both wrote the same
five files, and both independently wrote the same two incident entries, one of
which had to be deleted at merge. Nothing was lost, because the charter's "your
own last run may still be open" rule made the second run branch from the
first's tip. What the rule cannot do is stop the duplicated work.

The guardrails that exist are all one layer above the runtime. The PM's charter
§4 forbids dispatching into a seat with an open pull request, and neither of
these was the PM's: one was a cron and one was the owner's. `gh workflow run`
asks no questions, and GitHub queues nothing, because no workflow declares a
concurrency group.

**The change, one block per seat workflow**, in all twelve `agent-*.yml`:

```yaml
concurrency:
  group: agent-engineer          # the seat's own name, one group per seat
  cancel-in-progress: false      # queue the second run, never kill the first
```

`cancel-in-progress: false` is the load-bearing half. A cancelled run is
incident 3 again, a run that dies with work in the sandbox, and
INC-2026-09-24-writer-dispatch-started-twice was a cancellation. Queuing costs
a delay and loses nothing.

**What it does not fix.** A queued run still starts eventually, and it starts
against a branch its sibling has since moved. That is the charter's pre-flight
rule's job, and it works. This item only stops the two runs from being alive at
the same moment.

**Not smoke-testable from a seat**, because the seat cannot push the file to
test it. The lowest-risk order is one seat first, `agent-engineer.yml`, whose
double run is the one with evidence behind it, and the other eleven after a
day of it behaving.

---

### 10. The run report calls a tested script, because dash's echo ate the body

**Queued 2026-09-26 by the engineer seat.
INC-2026-09-26-run-report-dash-echo. Still live on main on 2026-09-28, two days
later, and it has now failed six consecutive engineer runs.**

The `Post run report` step added to all twelve `agent-*.yml` on 2026-09-26 at
01:14 and 01:23 UTC declares no `shell:`, so it runs under the container's
`sh`, which is dash. Dash's builtin `echo` expands backslash escapes. Every
`\n` that `gh pr list --json body` correctly escaped inside the pull request
body became a real newline before `jq` read it, so `jq` rejected its own input
and the step exited 4.

**Corrected 2026-09-28: it is two workflows, not twelve.** This entry said "all
twelve workflows, on every run," which overstated it and is worth fixing
because the number is what tells the owner how urgent this is. Only
`agent-engineer.yml` and `agent-frontend.yml` declare a `container:`, and the
container image is where `sh` is dash. The other ten run on the runner host,
where GitHub's default shell for a `run:` step is bash and `echo` leaves the
escapes alone. Checked by reading all twelve for `container:` and `shell: bash`
and by reading the conclusions: every `pm-agent`, `writer-agent`, `okr-agent`
and `exo-agent` run since the step landed is `success`.

It is deterministic for any pull request body containing a newline, which is all
of them, so those two workflows fail every single run. Six engineer runs so far,
every one of which finished its work and opened its pull request first:

| run | date | PR opened | conclusion |
|---|---|---|---|
| 36208446311 | 2026-09-26 01:26Z | #115 | failure |
| 36208644267 | 2026-09-26 01:30Z | #116 | failure |
| 36250253554 | 2026-09-26 14:57Z | #118 | failure |
| 36285149176 | 2026-09-27 01:18Z | #120 | failure |
| 36330209631 | 2026-09-27 15:36Z | #122 | failure |
| 36342225307 | 2026-09-27 18:51Z | #124 | failure |

The log of the last one is the same line as the first: `parse error: Invalid
string: control characters from U+0000 through U+001F must be escaped at line
177, column 1`, then `Process completed with exit code 4`. `agent-frontend.yml`
has not run since the step landed, so its first run will be its first failure.

**The cost is not the missing Slack message. It is the status.** A run that did
its whole job is recorded as `failure`, and run health is read off those
statuses by the PM's standup, by `docs/agents/delivery-health.md`, and by the
ExO's weekly audit. The engineer lane has read as six consecutive crashes for
two days while shipping a pull request every run.

**A one-character version of this fix exists, if the full one is too much to
apply today.** Adding `shell: bash` under `- name: Post run report` in
`agent-engineer.yml` and `agent-frontend.yml` alone stops the failures, because
bash's `echo` does not expand the escapes. It leaves the untestable shell in
place, which is the reason the real fix below is the real fix, but it is two
lines against twelve files' worth of replacement and it turns the engineer lane
green.

**The change, identical in all twelve `.github/workflows/agent-*.yml`.** Replace
the whole body of the `Post run report` step with one command:

```yaml
      # Visibility window (standards/operating-modes.md §3): the seat's run
      # report goes to the team's channel when the owner has created one.
      # Seats never read the channel; it is the owner's window only.
      #
      # The logic is in tools/run_report.py, not here, because shell embedded
      # in YAML cannot be tested and this step shipped broken to twelve
      # workflows at once (INC-2026-09-26-run-report-dash-echo). The webhook
      # guard stays inside the script for the reason the previous version's
      # comment gave: a step cannot read its own `env:` block from `if:`.
      - name: Post run report
        if: always()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python3 tools/run_report.py --workflow "${{ github.workflow }}" --status "${{ job.status }}"
```

**Why a script and not a two-character shell fix.** Adding `shell: bash` to the
step would fix this bug. It would not fix the class, and the class is the
expensive part: twenty lines of shell inside twelve YAML files that no test can
reach. `tools/run_report.py` has `compose()` as a pure function and eighteen
tests in `tests/test_run_report.py`, one of which is this exact body, and one of
which runs the script under `sh -e` so the container's shell is in the test
rather than in production. L-E0 asks for agents that can read and diagnose what
we build, and a seat can run this file and see its output.

**It needs nothing new.** No secret beyond `SLACK_WEBHOOK_URL`, which the step
already reads. No new permission. Python 3 and `gh` are both in the image and
both already used by other steps. Standard library only, so nothing to install.

**The behaviour is preserved exactly**, including both of the owner's rulings of
2026-09-26. The report is the pull request's own opening rather than a log line,
and it is the first five bullet lines, one line each, with `**` stripped, with a
fallback to the first two lines of prose when a body has no bullets. That
fallback is now proved by a test. In the shell version it was never reached.

**One deliberate behaviour change, and it is a fix.** The step can no longer
fail the job. A notification is not the run's work, and a red job for an
undelivered message is exactly the lie this incident is made of. Delivery
problems print as `::warning::` and the exit status stays 0. The report is also
printed into the run log, so the artifact exists even when the channel does not.

**Smoke-tested before it was queued**, as far as a seat can. Run against the
real `gh` API and the real body that broke production, under `sh -e`, which is
the exact shell the workflow gives a step with no `shell:` key:

```
$ sh -e -c 'echo "$pr" | jq -r ".title"'            # the live step's pipeline
parse error: Invalid string: control characters from U+0000 through U+001F
must be escaped at line 190, column 1
exit=4

$ sh -e -c 'python3 tools/run_report.py --status success \
    --workflow engineer-agent --branch engineer/2026-09-26-reasoning-rubric --dry-run'
{"text": "*engineer-agent* • success • Engineer 2026-09-26 (run 3): ...
exit=0
```

What a seat cannot test is the webhook itself, because no seat holds
`SLACK_WEBHOOK_URL`. The first real delivery is the chair's, on the first run
after this is applied. Everything a test can hold without the secret is held.

**Apply this before item 9 and before item 5.** It is the only item on this
page that is failing production runs as it sits here, and it is one line per
file.

---

### 11. The skill seat's cap goes to 200

*The number 11 is the next one free on this branch, which is not the same
as the next one free. PR #123 renumbered items on its own branch the same
day. This item is identified by its seat, its date and its diff, so
renumber it freely when they land together (incident 29).*

**Queued 2026-09-27 by the engineer agent, under the owner's directive of
2026-09-25.** Measured, not guessed. See the 2026-09-27 duty-growth
re-check in [turn-caps.md](turn-caps.md).

**Why.** ADR-35 gave the skill seat three new steps on 2026-09-26: survey
the claim graph, fetch the papers in full from arXiv, and append what it
could not read to docs/research/reading-queue.md. The first run under
those duties (36206676462, 2026-09-26) finished freely at **92 turns**,
against a peak of 81 across the five runs before it. Twice 92 rounded up
to the next 50 is 200, and the cap in force is 180. The seat has never
hit its cap, which is why nothing had flagged it.

**How.** One edit to `.github/workflows/agent-skill.yml` line 54. The
file has a single run step, and this diff was copied from the live file
on 2026-09-27 rather than from memory, per the incident 26 rule.

```diff
-          claude_args: "--max-turns 180 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 200 --permission-mode bypassPermissions --model claude-opus-5"
```

**No timeout change.** The measured run spent 743 seconds on 92 turns, so
200 turns is about 27 minutes against the file's `timeout-minutes: 75`.

**Ordering.** Independent. No other item on this page touches
`agent-skill.yml`.

**Cost.** $0 unless a run uses the turns. A cap is a tripwire and not a
budget.

---

### 12. Skill registration, checked on the pull request that adds a skill

**Queued 2026-09-30 by the engineer seat. ADR-36 part 1.**

Numbered 12 because 11 is the highest on this page today, and this page has
carried two items numbered 4 before, so the number is stated rather than
counted.

ADR-36 asks for "a check that fails when a skill on main has no row". That check
has to be in two halves, and the split is not a weakening.

The database half cannot run in GitHub Actions. This organization runs no
Postgres in CI, and CI holds no credential for the production one, which is the
same reason `tools/graph_audit.py`'s ten SELECTs are parsed rather than executed
in `checks.yml`. So the half that asks whether the row is actually in Neon runs
in `pipeline/skill_revision.py`, daily, where the `neon` secret already is, and
it repairs what it finds rather than only reporting it.

The half CI can run is the one that catches the failure mode ADR-36 actually
found. A skill cannot be registered when its provenance block cannot be read:
no `provenance:` map, no claim ids, a claim id that is not a number, a `name:`
that disagrees with its directory, a directory with no SKILL.md. Every one of
those ships green today and silently opts the skill out of revision forever.
`python3 tools/skill_registrar.py --files-only` exits 1 on each of them and
needs no database, no key and no network.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` and `db/schema.sql` are already in both `paths`
lists; these two lines go in both of them, beside the existing `tools/` entries
(verified against the live file this run: it carries `tools/board.py`,
`tools/run_report.py` and `tools/graph_audit.py` in that order, in both lists).

```yaml
      - "tools/skill_registrar.py"
      - "tests/test_skill_registrar.py"
```

Second, the step. It goes after the existing `the graph audit's SQL still
matches the schema, and still only reads` step, which is the last step in the
`digest-budget` job today.

```yaml
      # 2026-09-30, ADR-36 part 1. `skills_needing_revision` has been in
      # db/schema.sql since the founding and has never returned a row, because
      # the skill seat writes a SKILL.md and nothing writes the promotions row
      # the view joins. Seven claims are deprecated and no skill knows.
      #
      # Two things are held here. The registrar's three statements are parsed
      # with libpg_query and every relation and column resolved against
      # db/schema.sql, because no CI job in this organization can execute SQL
      # and a renamed column would otherwise turn a daily cron silently
      # useless. And every skill on the branch must be registrable: the failure
      # this catches is a merged skill whose provenance block cannot be read,
      # which ships green and opts that skill out of revision forever.
      - name: every skill can be registered, and the registrar's SQL matches the schema
        if: always()
        run: python3 -m pytest tests/test_skill_registrar.py -q

      - name: no skill on this branch is missing its provenance
        if: always()
        run: python3 tools/skill_registrar.py --files-only
```

**Smoke-tested from the seat, as far as a seat can.** Both commands were run in
this run's sandbox against the real six skills: the pytest step is 31 passed,
and `--files-only` exits 0. Both were also confirmed to fail on purpose, the
pytest step against a deliberate `promotionz` typo in the registrar's SQL and
the `--files-only` step against a fixture skill with an empty claims array. The
step cannot be smoke-tested on a branch as a workflow, because the seat cannot
push the file.

**Cost.** $0. No key, no network, no database.

### 13. The file that installs the suite's Modal stub triggers no check at all

**Queued 2026-09-30 by the engineer seat.**

Numbered 13 because 12 is the highest on this page today. Item 12 is queued
ahead of this one and both add a step after the graph-audit step, so whoever
applies them should apply 12 first and then append this one; if only one is
applied, either order works, because neither touches the other's lines.

**The hole.** `checks.yml` names fourteen test files in its two `paths` lists.
`tests/conftest.py` is in neither, and no job in any workflow runs the whole
suite. So a change to the one file that installs the Modal stub for every test
module in the repository triggers nothing. That file's own docstring records
what a bad version of it costs: four test files each carried their own copy of
the stub, the copy without `modal.Volume` won under `pytest tests/ -q`, and
"the whole suite reported a single error and ran nothing". A file with that
failure mode and no path entry is the gap this item closes.

`requirements-dev.txt` has the same shape and is deliberately left out of this
item: it is a version floor rather than logic, and a stale item is worse than a
narrow one.

**What the new test file is.** `tests/test_check_helper_is_enforced.py`, added
in the same pull request as this item. `tests/test_press_resilience.py` and
`tests/test_press_rehearsal.py` report failures by appending to a module-level
`FAILURES` list rather than by asserting, and only their `__main__` block reads
that list. Under `python3 -m pytest tests/ -q`, the command
`requirements-dev.txt` prescribes and both files' docstrings name, roughly 130
checks printed `FAIL` to a swallowed stdout and the suite said green. A hook in
`tests/conftest.py` now enforces the list under pytest as well.

CI reads those two files' exit codes today, because it runs them as scripts, so
the hook changes nothing about today's CI verdict and this item does not pretend
otherwise. What it buys is the day either file grows a pytest fixture, which is
the direction this suite has been moving all week: the moment one of them needs
`monkeypatch` or `capsys` it has to be run under pytest, and without the hook
that move silently retires 130 checks while every step stays green.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These two lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry, which is the last entry in each list. Verified
against the live file this run: `      - "tools/graph_audit.py"` matches exactly
twice, once per list, and `tests/conftest.py` appears zero times in the file.

```yaml
      - "tests/conftest.py"
      - "tests/test_check_helper_is_enforced.py"
```

Second, the step. It goes at the end of the `digest-budget` job. The live file's
last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-09-30. Two files in tests/ report failures by appending to a
      # module-level FAILURES list, and until today only their __main__ block
      # read it. Under `python3 -m pytest tests/ -q` every one of their ~130
      # checks printed FAIL to a stdout that -q swallows and the suite reported
      # green. That is how test_call_model_walks_and_backs_off came to assert a
      # contract the press stopped honouring on 2026-09-24 and go unnoticed:
      # the only reason it was ever caught is that this workflow happens to run
      # its file as a script.
      #
      # The hook lives in tests/conftest.py, which is the other half of this
      # item. That file installs the Modal stub for every test module here and
      # had no path entry, so a change to it triggered no check at all, and its
      # own docstring records a bad version of it making the whole suite collect
      # zero tests. These tests run pytest in a subprocess against throwaway
      # modules using the pattern, so they fail if the hook is deleted rather
      # than passing vacuously. Confirmed both ways from the seat.
      - name: the check() helper is enforced under pytest, not only as a script
        if: always()
        run: python3 -m pytest tests/test_check_helper_is_enforced.py -q
```

**Smoke-tested from the seat, as far as a seat can.** The command is 6 passed in
this run's sandbox, and 2 failed, 4 passed with the hook deleted from
`tests/conftest.py`, which is the only result that proves the tests are load
bearing. The step cannot be smoke-tested as a workflow, because the seat cannot
push the file.

**Cost.** $0. No key, no network, no database. The step adds about three seconds,
which is what a subprocess pytest costs six times over.

### 14. The deploy-drift guard runs in CI, so its own logic is under test

**Queued 2026-09-30 by the engineer seat, sprint 2026-09-28 item 2.**

Numbered 14 because 13 is the highest on this page today. Items 12, 13 and 14
all append a step at the end of the `digest-budget` job and two lines to each
`paths` list, and none of them touches another's lines, so any order works. If
all three are applied, applying them in number order keeps the file readable.

**What this protects.** `tools/delivery_health.py` grew a fifth surface,
`deploy`, which answers the one question none of the other four can: is the
code on main the code the crons are running. `modal deploy` bakes the
repository into an image, so a merge and a deploy are two events, and the gap
between them has cost the org twice. Incident 24 is the first. PR #110 is the
second, merged 2026-09-26 and inert for days while three documents described
its behaviour as live.

The guard's own logic is the kind CI exists to hold, because the way it fails
is by crying wolf. A seat's sandbox nearly always has uncommitted edits under
`pipeline/`, a branch carries commits that never merged, and a shallow clone
cannot date anything. All three must answer `unknown` rather than red, and a
change that quietly turned one of them into a verdict would make the standup
red every morning for a reason that resolves itself, which is how a report
teaches its reader to stop reading it.

**What the new test file is.** `tests/test_deploy_drift.py`, added in the same
pull request as this item. It builds a real git repository in a temporary
directory, because the dating and dirty-tree logic is `git log` and
`git status`, and mocking those would test the mock. No network, no database,
no Modal. `tests/test_delivery_health.py` joins the same step: its surface list
changed in this pull request and nothing in CI runs it today.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These three lines go in both `paths` lists, after the
existing `tools/graph_audit.py` entry, which is the last entry in each list.
Verified against the live file this run: `      - "tools/graph_audit.py"`
matches exactly twice, once per list, and neither `tools/delivery_health.py`
nor `tests/test_deploy_drift.py` appears anywhere in the file.

```yaml
      - "tools/delivery_health.py"
      - "tests/test_deploy_drift.py"
      - "tests/test_delivery_health.py"
```

`pipeline/runtime_sha.py` needs no entry: `pipeline/**` already covers it, and
that is deliberate rather than lucky, because the digest this guard compares is
derived from the three job modules and moves whenever they do.

Second, the step. It goes at the end of the `digest-budget` job. The live
file's last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-09-30, sprint 2026-09-28 item 2. The deploy-drift guard. Each of
      # triage, interpret and weekly now records a digest of the files it is
      # actually running from, and tools/delivery_health.py computes the same
      # digest from the checkout and compares. CI cannot run the guard against
      # production, because the recorded side lives in Neon and this org runs no
      # database in CI. What CI holds is the judgement, which is the half that
      # can rot: that a drift under a day reads as a pending deploy rather than
      # an alarm, that an uncommitted edit and an undatable checkout both answer
      # unknown rather than red, that a job which has never reported is never
      # green, and that the recording call cannot raise or abort the transaction
      # of the job it guards. The last one is why this is not optional: a
      # guardrail that can fail a production run is worse than no guardrail.
      - name: a stale deploy trips the alarm, and a real deploy clears it
        if: always()
        run: python3 -m pytest tests/test_deploy_drift.py tests/test_delivery_health.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox, as does the whole suite (638 passed, 9 skipped). The two
acceptance tests were confirmed to be load bearing by inverting the fixture:
with the recorded digest set to the current one the surface is green, and with
it set to a stale value on a checkout whose last commit is nine days old the
surface is red and names all three jobs. The step cannot be smoke-tested as a
workflow, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database. The step adds about two seconds.

### 15. The delivery receipt runs in CI, so the endpoint cannot leak the product

**Queued 2026-10-01 by the engineer seat**, with the credential-free reader for
guardrail 4.

Numbered 15 because 14 is the highest on this page today. **It composes with
item 14 and does not depend on it.** Both add lines to the same two `paths`
lists and a step at the end of the same job, and neither touches the other's
lines, so either order works and either alone works. If both are applied, item
14's step and this one can be left as two steps; they test different files and
two names in the CI log are easier to read than one.

**What this protects.** `site/app/api/delivery/route.js` is a public,
unauthenticated endpoint that reads the production database. That sentence is
the whole reason this item exists. It is public on purpose, because no agent
seat holds a database credential and the receipt is what lets every seat answer
guardrail 4's question at all, and the price of that decision is that the
boundary between metadata and product has to be held by something that runs on
every change.

Two of the tests are the boundary itself. One asserts that the queries never
select `digests.body` or any claim text and never touch `subscribers`, and that
the only tables read are the four this answers for. The other builds a receipt
from a row that carries a body, a `prompt_sha` and an invented column, and
asserts that none of the three appears in the JSON, because every field is built
by name. A future change that widens a query, or spreads a row into the response
for convenience, publishes the paid product. That change would be two
characters long and it would look like a simplification.

The rest hold the states. A receipt this reader cannot understand, a version it
does not speak, a 404 from a route that is not deployed yet and a site that does
not answer must every one of them answer `unknown`, never a verdict about the
press, which is the argument `tools/delivery_health.py` already makes for its
own third state. And one test asserts the property that keeps the two readers
honest: a connection and a receipt carrying the same rows produce the same
state and the same headline, word for word, differing only in `read_via`.

**What the new files are.** `tests/test_delivery_receipt.py` (20 tests) and
`tests/delivery.test.mjs` (10 executed cases), both added in the same pull
request as this item. The Python file runs the `.mjs` file in a subprocess, the
way `tests/test_accounts.py` runs `tests/accounts.test.mjs`, so one pytest
command still covers the whole path and the `node` half degrades to a skip where
`node` is absent. No network, no database, no site: the only thing stubbed is
`dh.fetch`.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These five lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry. Verified against the live file this run:
`      - "tools/graph_audit.py"` matches exactly twice, once per list, and none
of these five paths appears anywhere in the file. (Corrected 2026-10-01, second
window, same seat: this sentence said `tools/graph_audit.py` was the last entry
in each list and it is not. Three entries follow it, `db/schema.sql`,
`site/emails/digest.html` and `.github/workflows/checks.yml`. The instruction is
unchanged, because inserting after a line that matches exactly twice does not
depend on that line being last, but a hand reading "last entry" and finding
three more would have had to stop and work out which text to trust.)
If item 14 is applied first, these go after its three lines; the order inside
the list does not matter.

```yaml
      - "tests/test_delivery_receipt.py"
      - "tests/delivery.test.mjs"
      - "site/lib/delivery-core.js"
      - "site/lib/delivery.js"
      - "site/app/api/delivery/route.js"
```

The three `site/` entries are the point of the paths half. The tests read those
three files as source, so a change to the endpoint has to re-run them, and that
is exactly the change nobody will think to test.

Second, the step. It goes at the end of the `digest-budget` job. The live file's
last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-10-01. The delivery receipt. `tools/delivery_health.py` answers
      # three of its five surfaces from a public endpoint now, because no agent
      # seat holds a database credential and that is why guardrail 4 went
      # unenforced for a week. The endpoint reads production and answers anyone,
      # so the boundary between metadata and product is held here: these tests
      # assert that no query selects the issue body or a claim, and that a row
      # carrying one anyway cannot escape through the shaping layer, which
      # builds every field by name. They also hold the third state, since a
      # receipt this reader cannot parse must answer `unknown` and never a
      # verdict about the press, and the property that keeps two readers from
      # becoming two answers: a connection and a receipt carrying the same rows
      # reach the same state and the same headline.
      - name: the delivery receipt publishes metadata and never the product
        if: always()
        run: python3 -m pytest tests/test_delivery_receipt.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox, as does the whole suite (668 passed, nothing skipped, with
`requirements-dev.txt` and `tiktoken==0.8.0` installed as this workflow installs
them). The harness was
confirmed load bearing against an artifact known to fail it: inverting one
assertion in `test_an_unreadable_database_is_a_503_and_not_an_empty_receipt`
turns `python3 -m pytest tests/test_delivery_receipt.py -q` red with the check's
own name in the report, and reverting it turns it green again. The step cannot
be smoke-tested as a workflow, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database. The step adds about a second,
plus `node --test`, which needs no `npm install` because the module under test
has no imports.

**The fourth item on this page that is one more filename in two lists.** Items
12, 13, 14 and now 15 are all the same two-line hand edit, and
`INC-2026-09-29-receipts-step-had-no-paths` is what the pattern costs when the
hand adds the step and forgets the list. The ledger entry from 2026-09-30,
"checks.yml should run the suite, not fourteen filenames", is the structural fix
and it would delete this half of all four items.

### 16. The archive publishes the record, and that is checked on the pull request

**Queued 2026-10-01 by the engineer seat (second window)**, with the change
that makes a Monday send public on Monday.

Numbered 16 because 15 is the highest on this page today. **It composes with
items 14 and 15 and depends on neither.** All three add lines to the same two
`paths` lists and a step at the end of the same job, none of them touches
another's lines, so any order works and any one alone works.

**What this protects.** `site/lib/issues-live.js` decides which weeks the public
archive publishes, from the `digests` table rather than from files committed by
hand. The archive is the product's shop window and the issue is the free half of
what the company sells, so three properties now stand between a change to that
file and a public page, and every one of them is a way this could go wrong
quietly rather than loudly.

A database that cannot be read must publish exactly what the committed files
publish. That is the difference between a Neon outage being invisible and a Neon
outage emptying the archive, and the test drives it twice, once with no
connection and once with a query that throws.

`HIDDEN_WEEKS` must still retire a week that exists only as a row. That set is
the owner's veto over the archive (2026-W37, retired on her order 2026-09-19)
and the record is a second way in, so a row must not be able to walk past it.

The committed file must win over the row for a week that has both. Every
correction already made to a published issue lives in those files: the 2026-09-19
corrections to 2026-W37, the 2026-09-24 reprint of 2026-W39 under canon law 14.
A change that reversed this precedence would silently revert all of them, and it
would look like a simplification.

Two more are worth naming because they are about the query rather than the
rules. The week comes out of the URL, so one test asserts it is interpolated and
never concatenated, and that a week which does not match `^\d{4}-W\d{2}$` never
reaches the database at all. And the listing query reads only the first 4,000
characters of each body, so the shaping layer drops `body` from the listing
shape entirely: a page that rendered it would be showing a truncated issue as a
whole one.

**What the new files are.** `tests/test_issue_route.py` (7 tests, 23 checks) and
`tests/issues.test.mjs` (19 executed cases), both added in the same pull request
as this item. The Python file runs the `.mjs` file in a subprocess, the way
`tests/test_delivery_receipt.py` runs `tests/delivery.test.mjs`, so one pytest
command covers the whole path and the `node` half degrades to a skip where
`node` is absent. No network, no database, no `npm install`: the module under
test has no imports, which is why the queries live in it.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These six lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry. Verified against the live file this run:
`      - "tools/graph_audit.py"` matches exactly twice, once per list, and none
of these six paths appears anywhere in the file. If items 14 or 15 are applied
first, these go after their lines. The order inside the list does not matter.

```yaml
      - "tests/test_issue_route.py"
      - "tests/issues.test.mjs"
      - "site/lib/issues-core.js"
      - "site/lib/issues-live.js"
      - "site/lib/content.js"
      - "site/app/library/**"
```

The four `site/` entries are the point of the paths half, and `site/lib/content.js`
is there for a reason worth stating: the record's bodies are parsed by that
file's `parseIssue`, which is now exported so there is one derivation rule
rather than two, and a change to it moves every title and excerpt in the
archive.

Second, the step. It goes at the end of the `digest-budget` job, after the
graph-audit step, which is the last step in the live file: `run: python3 -m
pytest tests/test_graph_audit.py -q` matches exactly once and is the file's last
line.

```yaml
      # 2026-10-01. The archive reads `digests` now, so an issue is public the
      # moment the press mails it instead of whenever somebody remembers to
      # commit a markdown file. Three properties stand between a change to
      # site/lib/issues-live.js and a public page: a database that cannot be
      # read publishes exactly what the committed files publish, HIDDEN_WEEKS
      # still retires a week that exists only as a row, and the committed file
      # still wins the text of any week that has one, which is what keeps every
      # correction already made to a published issue standing. The week comes
      # out of the URL, so the query half is held too.
      - name: the archive publishes the record, and fails closed to the files
        if: always()
        run: python3 -m pytest tests/test_issue_route.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox. The harness was confirmed load bearing against an artifact known
to fail it: changing one asserted string in `test_both_routes_read_the_record`
to one the route does not contain turns `python3 -m pytest
tests/test_issue_route.py -q` red with the check's own sentence in the report,
and reverting it turns it green again, which also exercises the `FAILURES` hook
in `tests/conftest.py` that makes a `check()` file legible to pytest at all. The
step cannot be smoke-tested as a workflow, because the seat cannot push the
file.

Separately and beyond what CI can hold, the route behaviour was measured against
a real production build of the site in this sandbox, because the change retires
a guard that existed to prevent a 500. `npm install && npx next build && npx
next start`, then six requests: `/` 200, `/library` 200, `/library/2026-W39` 200,
`/library/2026-W37` 404, `/library/2026-W01` 404, `/library/nonsense` 404. A
clean 404 on an unpublished week is the sentence the old guard was protecting,
and it holds without the guard because the route is dynamic from the start.

**One thing this item does not need to queue, verified rather than assumed.**
The same pull request adds a sixth surface to `tools/delivery_health.py`, the
`archive` comparison, with six tests in `tests/test_delivery_health.py`. Both of
those files are already queued into both `paths` lists and into a step by **item
14** above (`run: python3 -m pytest tests/test_deploy_drift.py
tests/test_delivery_health.py -q`), so applying item 14 covers them and this
item does not name them twice. If item 14 is never applied, those six tests run
under `python3 -m pytest tests/ -q` and nowhere in CI, which is the same hole
item 14 exists to close and not a new one.

**Cost.** $0. No key, no network, no database. The step adds under a second,
plus `node --test`, which needs no `npm install`.

**The fifth item on this page that is one more filename in two lists.** Items
12, 13, 14, 15 and now 16 are the same two-line hand edit five times over, and
`INC-2026-09-29-receipts-step-had-no-paths` is what the pattern costs when the
hand adds the step and forgets the list. The ledger entry from 2026-09-30,
"checks.yml should run the suite, not fourteen filenames", is the structural fix
and it would delete half of all five items. Five occurrences of one shape is no
longer a pattern worth noting, it is a backlog, so this run raises it from a
ledger line to a named recommendation to the owner in its pull request.

### 17. The site's XSS defence and the account layer run in CI, or checks.yml stops naming filenames

**Queued 2026-10-02 by the engineer seat**, from
`INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had`.

**Numbered 17 only relative to this branch, and the number is already wrong.**
`main` stops at item 11. Three open pull requests allocate numbers from 12
upward on this page right now and none of them can see the others: this seat's
chain takes 12 through 16, PR #174 takes 12 through 16 for five different
changes (action pinning, `PROJECTS_TOKEN`, the budget step, the no-ship
tripwire, the register checker), and PR #160 takes 12 and 13 for two more. After
all three merge, thirteen items will claim six numbers. That is incident 29's
sequential allocator, in the one register whose numbering was never converted to
slugs, and it is recorded this run as
`INC-2026-10-02-pending-queue-number-collision`. Read this item by its title,
not by its number, and expect to renumber at merge. It composes with every other
queued item and depends on none of them.

**What is wrong.** `tests/test_markdown.py` holds the 2026-09-19 finding, the
one where a crafted passage in an arXiv paper reached the public archive as live
HTML. Its docstring says of `tests/markdown.test.mjs`, "It needs no
node_modules, which is why it is the half that runs in CI." No workflow in this
repository runs either file. `site/lib/markdown-core.js`, which decides what
markdown is allowed to become on the public site, is in neither `paths` list, so
a pull request changing nothing but that file runs no check at all.

`tests/test_accounts.py` and `tests/accounts.test.mjs` are in the same position,
and they hold the account and entitlement layer.

Measured this run: `node --test tests/*.test.mjs` returns 122 pass, 0 fail, so
nothing is broken behind this. What is missing is the gate.

**The recommendation, which is the structural form.** Replace the fourteen named
pytest steps with one that runs the suite, and replace both `paths` lists with
the directories the suite covers. One step, one list, and items 12 through 16 on
this page lose their paths halves entirely:

```yaml
      - name: the test suite
        if: always()
        run: python3 -m pytest tests/ -q
```

This is the ledger entry of 2026-09-30, "checks.yml should run the suite, not
fourteen filenames", and this item is the sixth occurrence of the two-line hand
edit that entry exists to delete. Two things make it safe to do now that were
not true a week ago. `tests/conftest.py` enforces the `FAILURES` harness under
pytest since 2026-09-30, so the two script-mode files no longer go green by
default under a suite run (`INC-2026-09-30-check-harness-green-under-pytest`).
And the suite passes in full in this run's sandbox: 694 passed, 1 skipped, in 26
seconds. Keep the three script-mode invocations as they are if you want belt and
braces, because they cost under a second each.

**The minimal form, if the structural one is too large a change to make by
hand.** Four lines in both `paths` lists, after the existing
`      - "tools/graph_audit.py"` entry, which matches exactly twice in the live
file, once per list. None of these four appears anywhere in the file today,
verified this run:

```yaml
      - "tests/test_markdown.py"
      - "tests/markdown.test.mjs"
      - "site/lib/markdown-core.js"
      - "tests/test_accounts.py"
```

And one step at the end of the `digest-budget` job, after `run: python3 -m
pytest tests/test_graph_audit.py -q`, which matches exactly once and is the live
file's last line:

```yaml
      # 2026-10-02, INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had.
      # site/lib/markdown-core.js is the whole of the defence between a crafted
      # passage in an arXiv paper and live HTML on the public archive, and until
      # this step existed a pull request touching only that file ran no check.
      # The account layer is here for the same reason. Both files run their .mjs
      # half in a subprocess, so one pytest command covers each layer, and the
      # node half degrades to a skip where node is absent.
      - name: the archive refuses HTML, and the account layer holds
        if: always()
        run: python3 -m pytest tests/test_markdown.py tests/test_accounts.py -q
```

**Smoke-tested from the seat, as far as a seat can.** `python3 -m pytest
tests/test_markdown.py tests/test_accounts.py -q` passes in this sandbox, and
`node --test tests/*.test.mjs` passes at 122 of 122. The step cannot be
smoke-tested as a workflow, because the seat cannot push the file.

**Cost.** $0 either way. The minimal form adds under two seconds. The structural
form adds about 26 seconds and removes five pending items from this page.

**One thing this item deliberately does not do.** It does not add
`site/lib/account-core.js`, `site/lib/entitlement.js` or
`site/lib/markdown.js` to the minimal form's list, because the minimal form is
already the sixth instance of a pattern that this page says should be deleted
rather than extended, and a seventh filename argues the wrong way. The
structural form covers them by covering everything, which is the point.

---

---

---

### 18. ADR-13's panel runs in CI, or three documents stop saying it does
### (amended 2026-10-03 second window: three reviewers, not two)

**Queued 2026-10-03 by the engineer seat.
INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had.**

Numbered 18 because 17 is the highest on this page today, and this page has
carried two items numbered 4 and two numbered 5 before, so the number is stated
rather than counted (incident 29).

The panel's first reviewer shipped on 2026-10-02 with a build note saying its
file half "runs on every pull request that touches `skills/**` or
`db/schema.sql`, inside the skill-receipts step of `checks.yml`". It does not.
That step runs `tests/test_skill_receipts.py` and nothing else, and neither
reviewer's file is in either `paths` list. So 46 tests have never run in CI, and
the thing only CI can hold about a reviewer in this organization, that its SQL
still resolves against `db/schema.sql`, has never been held.

**Why these tests belong in CI when the reviewers mostly do not.** No Postgres
exists in CI here, so the SELECTs are parsed with libpg_query and every relation
and column is resolved against the schema, exactly as `tools/graph_audit.py`'s
ten SELECTs already are in the `the graph audit's SQL still matches the schema`
step. A migration that renames `claim_links.to_claim` or
`claims.interpreted_at` should turn a pull request red, not turn a 16:00 UTC
cron silently useless.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` and `db/schema.sql` are already in both lists;
these five lines go in both, beside the existing `tools/` and `tests/` entries.

```yaml
      - "tools/panel.py"
      - "tools/panel_provenance.py"
      - "tools/panel_adversary.py"
      - "tools/panel_validator.py"
      - "tests/test_panel_provenance.py"
      - "tests/test_panel_adversary.py"
      - "tests/test_panel_validator.py"
```

Second, two steps. They go after `every skill can be registered, and the
registrar's SQL matches the schema` from item 12, because the panel reads what
the registrar writes and a reader wants them in that order. Item 12 is not a
prerequisite: these two steps stand alone if item 12 is still unapplied, and in
that case they go after the graph audit step instead, which is the last step in
the `digest-budget` job today.

```yaml
      # 2026-10-03, ADR-13. The panel's two built reviewers send five SELECTs
      # and two INSERTs between them, and no CI job in this organization can
      # execute any of them. So they are parsed with libpg_query and every
      # relation and column is resolved against db/schema.sql, the same
      # instrument the graph audit step above uses, for the same reason: a
      # renamed column would otherwise be discovered by a daily cron going
      # quietly useless rather than by the pull request that renamed it.
      #
      # Two reviewers, two steps, on purpose. A single step would go red for
      # either and the log line is where a reader learns which.
      - name: the provenance reviewer's SQL matches the schema, and its duties still decide
        if: always()
        run: python3 -m pytest tests/test_panel_provenance.py -q

      - name: the adversary reads the graph in the direction ADR-10 fixed
        if: always()
        run: python3 -m pytest tests/test_panel_adversary.py -q

      - name: the validator judges the trial receipt against the text under review
        if: always()
        run: python3 -m pytest tests/test_panel_validator.py -q
```

**Why there is no third step running the reviewer itself, which this entry
nearly got wrong.** The obvious companion to item 12's `python3
tools/skill_registrar.py --files-only` is `python3 tools/panel_provenance.py
--files-only`, and the first draft of this entry queued it and claimed it exits
0. It exits 2, over the real library, and always will. The reviewer's three
states are `0 nothing wrong`, `1 a finding`, `2 something could not be
measured`, and duty 2 is structurally unmeasurable for every skill until the
per-section claim id format lands, so that step would be red on every pull
request forever and would teach every seat to ignore it. The useful half of it
is a test instead:
`tests/test_panel_provenance.py::test_no_skill_on_this_branch_fails_a_file_level_check`
asserts that no skill carries a `fail` finding, which is the thing that should
block a merge, and lets an honest `unknown` through. It was added in the same
pull request as this entry.

**What must NOT be added, and this is the other half a reader will be tempted
by.**
There is no step that runs `tools/panel_adversary.py`. Nothing that reviewer
decides is in a SKILL.md: its whole input is the claim graph, so with no
credential it can only report that nobody asked the graph, and a green step
named for it would read as the graph agreeing.
`tests/test_panel_adversary.py` asserts that `checks.yml` never names that
command, so adding it turns the second step above red.

**Smoke-tested from the seat, as far as a seat can.** Both commands were run in
this run's sandbox against the real six skills: `tests/test_panel_provenance.py`
is 47 passed and `tests/test_panel_adversary.py` is 43 passed. Each was also
confirmed to fail on purpose, against a deliberately renamed column in its own
reviewer's SQL, and the adversary's suite was confirmed to fail against four
more deliberate defects: the threshold moved off the schema's 0.7, the edge read
in the wrong direction, the file dropped from the Modal image, and an
un-interpreted claim downgraded from `unknown` to a note. The steps cannot be
smoke-tested as a workflow on a branch, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database.

**Amended 2026-10-03, same day, second window: the third reviewer.**
`tools/panel_validator.py` completes ADR-13's panel, so this entry now asks for
three steps rather than two and seven path lines rather than five. Amended in
place rather than queued as item 19, because an unapplied entry about exactly
this subsystem is one hand for the chair instead of two, and because a reader
who applied item 18 and then met a separate item 19 about the same two lists
would reasonably wonder which was current. `tests/test_panel_validator.py` is 66
passed in this run's sandbox and the whole suite is 848 passed, 9 skipped.

**And the reviewer command, which this entry can now offer for one of the
three.** The paragraph above explains at length why there is no step running
`tools/panel_provenance.py --files-only` (it exits 2 forever, because duty 2 is
structurally unmeasurable) and none running the adversary at all (it holds no
database credential, so a green step would read as the graph agreeing). The
validator is different in kind: **every finding it makes is a fact about a file
in the repository**, so its `--files-only` verdict is its whole verdict, and
`tests/test_panel_validator.py::test_the_files_only_half_and_the_live_half_return_the_same_verdict`
asserts that rather than claiming it.

It is still **not** queued as a step, and the reason is the same arithmetic that
killed the first one: it exits 1 today, on every pull request, because all six
skills on main say `status: active` with no eval behind them (ADR-36 part 2). A
step that is red on every pull request teaches every seat to ignore it, which is
worse than no step. The useful half is in the suite instead, as
`test_no_skill_on_this_branch_fails_a_check_this_reviewer_invented`, which
asserts that every `fail` over the real library traces to a sentence in ADR-36
and nothing else. **The day the skill seat's evals merge, this becomes the one
reviewer worth running as a command**, and that is the signal to come back to
this paragraph rather than a thing to do now.

### 19. The eval harness's own `--check` gate runs in CI, or its docstring stops calling itself one

**Queued 2026-10-04 by the engineer seat.
INC-2026-10-04-eval-check-gate-claims-a-ci-step-it-never-had.**

Numbered 19 because 18 is the highest on this page today, and this page has
carried two items numbered 4 and two numbered 5 before, so the number is stated
rather than counted (incident 29).

`tools/skill_eval.py`'s `conformance` carries this sentence, written the day the
harness was: "Its own function so `--check` can be a CI gate over every skill's
eval file without a key, a model or a dollar." Nothing runs it. Neither
`tools/skill_eval.py` nor `tests/test_skill_eval.py` is in either `paths` list
in `checks.yml`, and no step invokes either one. Fourth sighting of the shape
INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had named first.

**Why it belongs in CI, specifically.** The gate needs no key, no model and no
dollar, which is the whole reason `conformance` is a separate function. And the
thing it holds is a cross-seat seam: the suites are the skill seat's files, the
reader is the engineer's, and the two were written to different contract
documents, which is how eight suites spent four days unrunnable
(2026-10-03 urgent ledger entry, fixed in the reader on 2026-10-04). A pull
request that adds a suite the reader cannot run should be red on that pull
request.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` is already in both lists; these two lines go in
both, beside the existing `tools/` and `tests/` entries.

```yaml
      - "tools/skill_eval.py"
      - "tests/test_skill_eval.py"
```

Second, two steps, after the skill-receipts step. The exit codes matter and the
second step is written around them: `--check` exits 0 when every skill carries a
conformant suite, **2 when some skill carries none**, and 1 when a file exists
and is malformed. Unmeasured is an honest state under ADR-36 and must not turn a
build red, so 2 is accepted explicitly rather than by `|| true`, which would
accept 1 as well and make the step decorative. Today every skill is in state 2,
so this step passes while saying so in its log.

```yaml
      # 2026-10-04. `conformance` in tools/skill_eval.py was written to be this
      # step and never was one. It parses every skills/*/evals/evals.json,
      # resolves each registered model id against pipeline/budget.py's table,
      # and holds the one rule the harness must never satisfy on an author's
      # behalf: rule 1 of docs/product/skill-validation.md section V5, the
      # pre-registered policy. No key, no model, no network, no dollar.
      - name: the eval harness still measures what it should
        if: always()
        run: python3 tools/skill_eval.py --smoke

      # Exit 2 is "some skill has no suite yet", which is ADR-36's draft state
      # and not a failure. Exit 1 is a suite that exists and cannot be run.
      # Written out rather than `|| true`, which would swallow both.
      - name: every eval suite in the library can actually be run
        if: always()
        run: |
          python3 tools/skill_eval.py --check || status=$?
          if [ "${status:-0}" = "2" ]; then
            echo "some skills carry no suite yet, which ADR-36 calls draft"
            exit 0
          fi
          exit "${status:-0}"
```

The `--smoke` step is the cheaper half and the one worth having first: it runs
the whole measurement path against a scripted model, 24 calls and $0.00, and
it already asserts the arithmetic of the verdict rule. It has been a command
nobody runs since 2026-09-30.

### 19, amended 2026-10-04 (second window): two more files, and the module whose test file did not exist

Amended in place rather than queued as item 20, for the reason item 18 was
amended in place: the same two `paths` lists, in the same workflow, about the
same subsystem. A reader applying item 19 and then meeting a separate item 20
about those lists would have to work out which is current.

`INC-2026-10-04-named-test-file-never-written`. `tools/skill_triggers.py` names
`tests/test_skill_triggers.py` in its own docstring as the thing that holds its
one dangerous property, which is that no maintenance line it writes may read as
a request to fetch a paper. That file did not exist until this run. It exists
now, 22 tests, no database, no model, no network, and writing it found the
property false at the channel every line passes through.

So four paths rather than two, in **both** lists:

```yaml
      - "tools/skill_eval.py"
      - "tools/skill_triggers.py"
      - "tests/test_skill_eval.py"
      - "tests/test_skill_triggers.py"
```

And one more step, beside the two above. It takes no key and no model, and it
is the only thing in CI that would notice if a queue line started asking
`pipeline/reading_queue.py` to re-fetch a paper the corpus already holds:

```yaml
      - name: the staleness triggers, and the fetch request they must never write
        if: always()
        run: python3 -m pytest tests/test_skill_triggers.py tests/test_skill_eval.py -q
```

Both files are pytest, so one step covers them and `requirements-dev.txt` is
already installed by the step above. Verified in this run's sandbox: 22 passed
for the triggers, 90 passed for the harness, and the whole suite 888 passed, 9
skipped.

## Not queued here, because it needs a key rather than a hand

The GitHub App token-mint step (ADR-27) is the change that makes this
whole page unnecessary. It is written out in
[app-identity-handover.md](app-identity-handover.md) rather than here,
because it is blocked on `APP_PRIVATE_KEY` existing, not on someone
applying an edit. `APP_ID` is already set.

## Applied and deleted

- **The open-routed step falls back instead of failing the run** (queued
  2026-09-20 as item 1b, incident 23, applied by the chair in commit
  2d3902d on 2026-09-24, verified against all four routed workflow files
  on 2026-09-27, and deleted from this page in the same run). Present in
  `agent-pm.yml`, `agent-market.yml`, `agent-okr.yml` and
  `agent-finance.yml`: each has `continue-on-error: true` on the
  open-routed step and gates the Claude step on its outcome. **The chair
  shipped it in a stronger form than the queued diff**, and the
  difference is worth the next run's attention. The diff proposed
  `steps.openrouted.outcome == 'failure'` and the live files read
  `steps.openrouted.outcome != 'success'`, which also covers `cancelled`
  and `skipped`. A step that is cancelled has done no work either, so
  the queued version would have lost the run in exactly the case the
  item was written to prevent. Recorded here because this page's habit is
  to note where the hand improved on the proposal, and because the third
  edit in the item, the `open-routed attempt:` line in the tripwire
  summary, was **not** applied: the failure is therefore fixed and still
  invisible in `gh run list`, which is incident 8's lesson left half
  learned. It is not re-queued, because the OPENROUTE secrets are absent
  from this repository and nothing is currently routed, so the line would
  report on a path that cannot run. Re-queue it in the same run that
  re-adds the key.
- **Turn caps, re-derived from run logs** (queued 2026-09-18, applied by
  the chair in c6bc2c4, verified against the workflow files on
  2026-09-18). The chair went further than the queued numbers on several
  seats.
- **The three remaining short caps** (queued 2026-09-18 evening, applied
  by the chair, verified against the workflow files on 2026-09-19).
  frontend is at 600, pm at 300, security at 250.
- **The no-ship tripwire, all twelve agent workflows** (queued
  2026-09-18 as item 1, applied by the chair in commit 440163a on
  2026-09-20 at 12:34, verified against all twelve workflow files on
  2026-09-21). Present in every `agent-*.yml`, in a better form than the
  queued diff: the chair's version came from the company template and
  ships a `Post run report` step beside it, which posts the run's result
  to Slack when `SLACK_WEBHOOK_URL` exists and exits quietly when it does
  not. Three things are worth the next run's attention. The webhook guard
  is inside the script rather than in the step's `if:`, with a comment
  explaining that a step cannot read its own `env:` block from `if:`, and
  that reasoning is correct. The tripwire's `exit 1` means a run can now
  be **red because it shipped nothing rather than because it crashed**,
  which is a new failure fingerprint for §2b to diagnose and it is
  recorded in the learning log. And the change reached twelve live
  workflows with no smoke run on a throwaway branch, which
  [runtime-changes.md](runtime-changes.md) requires, though three
  scheduled runs after it (engineer 14:40, exo 17:15, writer 18:20) all
  passed, so it worked. The law still binds the chair.
- **Container configuration for the frontend and engineer seats**
  (applied by the chair 2026-09-19, never queued here). `container:`,
  `credentials:` and `options: --user 1001:1001` against
  `ghcr.io/alexandrapaiz/alexandria-agent:latest`. Recorded as applied
  so the next run does not mistake it for drift. Incidents 17 and 18 are
  the two failures it took to get right.
