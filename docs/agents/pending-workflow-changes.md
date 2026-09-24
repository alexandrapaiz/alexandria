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

Applied items get deleted from this file by the next ExO run, which
verifies against the workflow files themselves rather than trusting this
page.

---

## Pending, queued 2026-09-18 by the ExO agent

### 1b. The open-routed step must fall back instead of failing the run

**Queued 2026-09-20 by the ExO agent. Incident 23.**

**RE-VERIFIED 2026-09-24, and its status has changed from urgent to
conditional.** The owner took the alternative at the bottom of this
item: the chair removed the OPENROUTE secrets from this repository on
2026-09-23, so all four seats fall back to Sonnet today and nothing is
currently failing. Every `-` line in the diffs below was grepped against
the live files this run and each appears exactly once, in all four
workflows, so the diffs are good.

**What changed is what this item now means. It is a precondition rather
than a fix.** The either/or shape is still in all four files. It is
dormant only because a secret is absent, and a secret is the easiest
thing in this org to put back. So:

> **The OPENROUTE secrets do not go back into this repository until this
> item is applied.** Re-adding the key today re-arms the identical
> failure on the identical seat, and the PM is the seat that reports
> every other failure.

That sentence is the recommendation this seat carries to the owner, and
it is also in the relay note to HQ, because HQ's copies have the same
shape and HQ has not removed its key. The second precondition is the
golden-set comparison this repo's routing law already requires, and the
third is the ordering rule from incident 23's postmortem: the first seat
routed is the one whose failure costs least, which is finance or okr,
and never the PM.

**Why.** Commit 609d7cc gave four workflows two run steps, chosen by a
condition rather than by an outcome:

```yaml
      - name: Seat run (open-routed)
        if: env.OPENROUTE != ''
      - name: Seat run (Claude)
        if: env.OPENROUTE == ''
```

That is an either/or, not a fallback. The Sonnet step is written into
the file and can never execute while the secret exists, so a routing
experiment that fails costs the org the entire run rather than a retry.
Run 35493791740 is the proof: the PM seat produced nothing at all on
2026-09-20 because its first model call errored, and the perfectly good
Claude path sitting twelve lines below it was unreachable by
construction.

**How.** Two edits per file, in `agent-pm.yml`, `agent-market.yml`,
`agent-okr.yml` and `agent-finance.yml`. Give the open-routed step an
id and let it fail without failing the job, then gate the Claude step on
its outcome instead of on the secret.

```diff
       - name: Seat run (open-routed)
+        id: openrouted
         if: env.OPENROUTE != ''
+        continue-on-error: true
         uses: anthropics/claude-code-action@v1
```

```diff
       - name: Seat run (Claude)
-        if: env.OPENROUTE == ''
+        # Runs when open routing is off, and also when it was on and
+        # failed. Incident 23: an either/or between two run steps turns
+        # a routing experiment into a lost run. This makes the open
+        # model preferred rather than mandatory.
+        if: env.OPENROUTE == '' || steps.openrouted.outcome == 'failure'
         uses: anthropics/claude-code-action@v1
```

**What it does and does not do.** A failed open-routed attempt now costs
three minutes and a warning, and the seat still does its job. It does
not detect the worse case, which is an open-routed run that succeeds and
does the work badly, because no condition in YAML can judge that. That
case belongs to the three tests in
[model-routing.md](model-routing.md) and to the owner's reading of the
output.

**One caveat, and it is now a live edit rather than a conditional one.**
The fallback makes the run green whenever Claude rescues it, so the
failure becomes invisible in `gh run list`. Keep it visible by reading the
step outcome rather than the job conclusion, which is incident 8's lesson
again. Item 1's tripwire was applied on 2026-09-20, so this is simply a
third edit to the same four files. In the `No-ship tripwire` step, inside
the summary block, after the `pull request:` line:

```diff
             echo "- pull request: ${pr:-none}"
+            echo "- open-routed attempt: ${{ steps.openrouted.outcome || 'not attempted' }}"
           } >> "$GITHUB_STEP_SUMMARY"
```

**Cost.** Two lines per file, $0. It spends a Claude run only on the
days the open model fails, which is the days the org was losing a run
entirely.

**The alternative, which is the owner's and takes ten seconds.** Delete
or rename the `OPENROUTE_API_KEY` secret. The four seats fall back to
Sonnet immediately with no file edit at all, because the existing
conditions already do that when the secret is absent. That is the right
move if the experiment is not worth a failed Monday, and it is
reversible.

### 2. The PM goes daily, so the org has a seat that is present

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

**What was not applied: the cap.** `agent-pm.yml` still reads
`--max-turns 300` on both steps. Verified this run by grep, and both `-`
lines below match the live file exactly, once each. The case for 400 is
stronger now than when it was written, since this run added a delivery-
health half to the PM's §1f and the seat now carries a daily standup it
did not have when 300 was derived. It is not urgent: the two failed PM
runs died at turn 1 and turn 30, so nothing has come near the cap, and a
cap is a tripwire rather than a budget.

**What is now moot.** The cron diff and the two documentation lines
below are superseded by what the chair shipped. They are left in place
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

---

## Not queued here, because it needs a key rather than a hand

The GitHub App token-mint step (ADR-27) is the change that makes this
whole page unnecessary. It is written out in
[app-identity-handover.md](app-identity-handover.md) rather than here,
because it is blocked on `APP_PRIVATE_KEY` existing, not on someone
applying an edit. `APP_ID` is already set.

## Applied and deleted

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
