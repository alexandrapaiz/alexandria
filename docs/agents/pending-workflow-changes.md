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
its own cap. The chair applied every fix by hand. Three caps are still
short of what the measured rule requires (item 2 below), and they will
stay short until someone applies them.

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

**How.** Three edits to `.github/workflows/agent-pm.yml`, plus the
prompt rewrite. The cron change is one character.

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

```diff
-          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model sonnet"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model sonnet"
```

And the prompt block, replaced in full:

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
