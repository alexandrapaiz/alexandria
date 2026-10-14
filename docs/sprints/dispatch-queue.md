# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-14, standup (~16:10 UTC)

**The headline is the dispatch mechanism itself, not a single pull
request.** Eighteen days of `INC-2026-09-24-dispatch-403` ended today:
`GH_TOKEN="$DEFAULT_WORKFLOW_TOKEN" gh workflow run agent-frontend.yml
-f owner_instructions='...'` created a real run
(https://github.com/alexandrapaiz/alexandria/actions/runs/38594124029)
for the first time, because `DEFAULT_WORKFLOW_TOKEN` is the job's own
token — the one `permissions: actions: write` actually governs — and
the ambient `GH_TOKEN`/`GITHUB_TOKEN` was always the Claude Code
action's own installation token instead (`docs/standards/pm.md` §11.5
names this exactly; it was vendored into this repo 2026-10-12, after
the incident was filed, and nobody had re-read it against the incident
since).

That run then died in 4 seconds, before the model read its prompt:
`claude-code-action` refuses to run when the triggering actor is a bot
unless the workflow's `allowed_bots` input names it, and a dispatch
made with `DEFAULT_WORKFLOW_TOKEN` is attributed to `github-actions`
the bot, not a human and not the `claude[bot]` app installation a
normal PR event carries. **So dispatch is still broken today, in a new
and more specific way** — the 403 is fixed, the actor gate is not, and
every `agent-*.yml` in this repo needs `allowed_bots` set before a PM
dispatch can do anything past creating the run. `.github/workflows/`
is HQ's surface in every product repo (standard §15), not this seat's
or the frontend seat's to edit, so this is a handoff
(`alexandra-systems/exo-centralizer`, posted on the board this run),
not a fix landed here. Full account in the amended
`INC-2026-09-24-dispatch-403` entry, `docs/agents/incidents.md`.

### Also landed this run: last Monday's ceremony, four days late

`sprint-2026-10-12.md` (the 2026-10-12 ceremony's retro on
sprint-2026-10-05, the groomed ledger, the new sprint) had been sitting
on an open, unmerged pull request since Monday (#281, superseded by
#289) because the chain also carried `docs/prfaq/launch-2026-10-13.md`,
the one Tier C file in it, and Tier A's self-merge rule holds the
*whole* pull request for the owner when any file in it is not a
knowledge surface. Split the PR/FAQ into its own pull request (#289,
now just that one file, unchanged scope, still waiting on the owner's
go/no-go per standard §2c) and self-merged everything else as #295
under Tier A — every remaining file was `docs/sprints/`,
`docs/agents/org-chart.md`, or grooming in `docs/ideas.md`.

## Run health

**Fleet.** Two failed runs in the last 24 hours, both triaged:

- `checks` on the skill PR branch (38449699087, 2026-10-13 18:48) — a
  SKILL.md revision mid-PR left a stale validation receipt for one
  commit; the next push on the same branch (and the eventual merge,
  #290) came back green. **Tripwire false alarm**, no rerun.
- `frontend-agent` (38594124029, 2026-10-14 15:59) — the dispatch
  described above. **Configuration**, handed off to HQ, no rerun (the
  same actor fails the same way every time until the workflow changes).

**Cap ratio** (turn-caps.md rule 5, 70% of `--max-turns`), over every
run since the last standup:

| Seat | Run | `num_turns` | Cap | Ratio |
|---|---|---|---|---|
| **skill** | 38447963152 (2026-10-13 18:35) | **174** | 180 | **96.7%** |
| engineer | 38444399510 (2026-10-13 18:09) | 141 | 200 | 70.5% |
| writer | 38466198428 (2026-10-13 20:52) | 117 | 225 | 52.0% |
| engineer | 38497590824 (2026-10-14 01:47) | 115 | 200 | 57.5% |

Two seats clear the 70% line, skill by a wide margin. Not a cap
proposal, per the standing rule that this duty reports the ratio and
names the seat; the ExO's monthly re-derivation is where a number would
come from.

**Delivery health**, read live against the database this standup, not
proxied from a scheduler:

```
FAILING  press     newest issue is 2026-W40, 2026-W41 has ended; 1 issue missing
FAILING  pipeline  claims stalled 7 days, 2264 papers waiting in distill_queue
FAILING  deploy    live site is 1.8 days / 16 commits behind main
FAILING  site      newest readable issue is 2026-W40
ok       archive   record and archive both end at 2026-W40
ok       mcp       up, refusing unauthenticated calls
```

Unchanged in kind from the last three standups. The reachable half of
the press fix is already in `main`; the unreachable half is a `modal
deploy` only the owner or chair can run
(`INC-2026-10-12-the-deploy-ladder-refuses-the-fix-for-the-outage-it-
is-in`). Named at the top of `docs/sprints/pending.md`, not buried here.

## The queue gauge, four numbers

1. **`main`'s age and checks.** Newest commit `61e3913`, this run's own
   third Tier B merge, **under 15 minutes old at last check.** Newest
   `checks.yml` run on `main`: **success.**
2. **Open pull requests: 9 total, 1 opened since the last merge to
   `main`** (this standup's own PR, #295).
3. **Conversion, trailing 7 days: 20 merged / 53 opened ≈ 0.38.**
4. **Deepest open supersession chain: 2** (#294 over #292; #60 over
   #35). No chain past depth 2 right now.

`main` is fresh and green, so this is not the deadlocked state
`INC-2026-10-04-four-days-of-output-and-no-delivery` describes.

## Merged this run (Tier B, `docs/standards/pm.md` §10)

- **#288** (engineer, institution backfill, sprint-2026-10-12 item 3) —
  clean, checks green, no Tier C path.
- **#290** (skill, harness-engineering v5 + agent-memory-selection) —
  `CONFLICTING` against #288 in `docs/agents/incidents.md` and
  `docs/ideas.md` (both append-only, same anchor). Docs-only, §10 rule
  5: merged `main` into the branch, kept both sides, pushed, merged
  clean.
- **#291** (writer, the attribution-gate grammar fix + two ban-list
  entries) — touches `prompts/digest.md`. Re-examined this run against
  standard §16's own vocabulary rather than against a label a prior
  standup gave a different file: a charter is `prompts/<role>-
  agent.md`, and `digest.md` isn't one, so this is not Tier C.
  `CONFLICTING` against the two merges above, same two append-only
  files, same resolution.

**Also landed under Tier A, this run's own PR (#295):** the split-off
2026-10-12 ceremony content — see the headline above.

**Not merged, each named rather than acted on:** #272 (exo, Tier C —
`prompts/exo-agent.md`, `prompts/market-agent.md`, this seat's own
`prompts/pm-agent.md` — and `CONFLICTING` besides). #205 (finance,
draft, dormant seat). #203 (okr, draft). #294 (engineer, draft, sprint
item 5, a run in progress). #293 (a different PM-surface pull request,
the owner's own window session, open since 12:27 UTC with only a
placeholder body at last check — not touched). #289 (the launch PR/FAQ,
now trimmed to that one file, waiting on the owner).

**One correction, filed to `docs/sprints/pending.md` and to the
engineer on the board:** #60 has been reported as Tier C for four
standups running because it touches `prompts/daily.md`. That file is a
content prompt, not a seat charter, same as `digest.md` above — the
tier was never what blocked it. It is `CONFLICTING` in product code
(`db/schema.sql`, `mcp/server.py`, `pipeline/budget.py`,
`pipeline/weekly.py`), which this seat cannot resolve itself (§10 rule
5 is docs-only), so it is handed to the engineer to rebase. 25 days
open.

## Proposed dispatches

**None proposed.** Today's one dispatch (frontend, below) already used
the day's evidence-backed candidate, and it surfaced a structural
blocker rather than a result: every seat this charter may dispatch is
now unreachable by the same `allowed_bots` gate until HQ applies the
fix handed off above. Proposing a second dispatch to a different seat
today would just produce a second identical 4-second failure. The right
next move is to wait for the handoff to close, not to retry.

## Dispatched by the PM

**2026-10-14, frontend.** Sprint item 4 (`sprint-2026-10-12.md`, the
Left-Behind Index, carried three sprints), board item `03029cad`. No
open frontend pull request existed. Fired under
`PM_DISPATCH_ENABLED=true`:

```bash
GH_TOKEN="$DEFAULT_WORKFLOW_TOKEN" gh workflow run agent-frontend.yml \
  -f owner_instructions='Board item 03029cad-e613-41ea-9295-3e3e15342f22
("Ship the Left-Behind Index as a public page"): build the public page
over the deprecated_claims view. This has carried unbuilt across
sprint-2026-09-28, sprint-2026-10-05 and the still-unmerged
sprint-2026-10-12 draft (PR #289). No open frontend pull request exists
right now (survey: last frontend PR was #244, merged 2026-10-07). Build
it and open a PR; move the board item to In progress when you start and
comment the PR link on it when you ship.'
```

Run: https://github.com/alexandrapaiz/alexandria/actions/runs/38594124029
(created). **Result: failed in 4 seconds**, `allowed_bots` gate — see
the headline above. Nothing shipped; the board item stays in Backlog.

## The Linear trial

Not checked this run; no new signal since the last pass noted it was
still on.
