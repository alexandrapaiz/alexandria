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

### 1. The no-ship tripwire, for all eleven agent workflows

**Why.** Incident 3: runs that worked for dozens of turns, reported
success, and lost every line at teardown because nothing was pushed. The
run's own conclusion hid it. The charter half of this fix shipped in the
same PR as this file, as the "Ship first, then work" rule now in all
eleven charters. This is the other half, which is the check that does not
depend on an agent remembering to obey.

**How.** Append to the `steps:` list of every
`.github/workflows/agent-*.yml`, after the `anthropics/claude-code-action`
step. Indentation is six spaces for the `- name:` line.

```yaml
      # Incident 3 (docs/agents/incidents.md): runs that worked for dozens of
      # turns, reported success, and lost everything at teardown because
      # nothing was pushed. A green conclusion is not evidence of shipping.
      - name: No-ship tripwire
        if: always()
        run: |
          git fetch origin --quiet 2>/dev/null || true
          branch=$(git rev-parse --abbrev-ref HEAD)
          dirty=$(git status --porcelain)
          pushed=$(git branch -r --contains HEAD 2>/dev/null | tr -d ' ')
          pr=$(gh pr list --head "$branch" --state all --json number --jq '.[0].number' 2>/dev/null || true)
          {
            echo "### Did this run ship anything?"
            echo ""
            echo "- branch: \`$branch\`"
            echo "- pushed to a remote branch: ${pushed:-NO}"
            echo "- pull request: ${pr:-none}"
          } >> "$GITHUB_STEP_SUMMARY"
          if [ -n "$dirty" ]; then
            echo "::warning::Uncommitted changes were left in the sandbox and are lost at teardown."
            printf '%s\n' "$dirty" | head -20
          fi
          if [ -z "$pushed" ]; then
            echo "::error::This run made commits that were never pushed, so the work dies with the sandbox. See incident 3 in docs/agents/incidents.md and the 'Ship first, then work' rule in this seat's charter."
            exit 1
          fi
          if [ -z "$pr" ]; then
            echo "::warning::No pull request exists for branch $branch. A run with nothing to ship must say so in a draft PR and close it, rather than ending silently."
          fi
```

**What each outcome means.** `git branch -r --contains HEAD` is empty
only when the run made commits that reached no remote branch, which is
lost work with no ambiguity, so that case fails the run. A dirty tree and
a missing pull request are warnings rather than failures, because both
have innocent explanations, and both are written to the run summary so a
reviewer sees what shipped without reading logs. Every step of this was
run by hand against this repository before it was written down, and the
one case it cannot see is a run that does nothing at all and leaves the
checkout pristine. That case is the missing-PR warning's job.

**Cost.** One shell step per run, no network beyond a fetch, $0.

### 1b. The open-routed step must fall back instead of failing the run

**Queued 2026-09-20 by the ExO agent. Incident 23. This is the most
urgent item on the page, and it is urgent on a date: the PM's ceremony
cron fires Monday 2026-09-21 at 10:35 UTC and will fail the same way
unless this is applied or the `OPENROUTE_API_KEY` secret is removed.**

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

**One caveat worth applying with it.** The fallback makes the run green
whenever Claude rescues it, so the failure becomes invisible in
`gh run list`. Keep it visible by reading the step outcome rather than
the job conclusion, which is incident 8's lesson again. If item 1's
tripwire is applied in the same hand, add this line to its summary
block:

```bash
            echo "- open-routed attempt: ${{ steps.openrouted.outcome || 'not attempted' }}"
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

**Queued 2026-09-19 by the ExO agent, on the owner's order.**

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

```diff
   run:
     runs-on: ubuntu-latest
-    timeout-minutes: 60
+    timeout-minutes: 75
```

Both caps move, because either step can be the one that runs. The
open-routed step is the one that fires today, so leaving it at 300 would
make the raise a no-op.

```diff
-          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
```

```diff
-          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model sonnet"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model sonnet"
```

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
- **Container configuration for the frontend and engineer seats**
  (applied by the chair 2026-09-19, never queued here). `container:`,
  `credentials:` and `options: --user 1001:1001` against
  `ghcr.io/alexandrapaiz/alexandria-agent:latest`. Recorded as applied
  so the next run does not mistake it for drift. Incidents 17 and 18 are
  the two failures it took to get right.
