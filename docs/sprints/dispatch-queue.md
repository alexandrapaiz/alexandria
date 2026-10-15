# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-15, standup (~15:55 UTC)

**One dispatch fired this run: frontend, sprint-2026-10-12 item 4, the
Left-Behind Index.** The rerun of yesterday's failed dispatch
(`38594124029`, see Failures) turned out not to test anything: GitHub
reruns replay the workflow file as it existed at the original trigger,
not the current one on `main`, so it hit the exact same actor-gate error
a second time even though `#298` had already fixed it. A fresh
`workflow_dispatch` was the only way to actually exercise the fix, and
every hard stop in `docs/standards/pm.md` §11.4 cleared: frontend's last
PR (`#299`) merged this run rather than sitting open, no human dispatch
in the last two hours, 0-of-3 daily ceiling before this one, and the
instruction carries only evidence already on record (the sprint item
verbatim, the board item id, and the PR survey showing no frontend PR
has ever attempted it). No other seat has an observed trigger: no new
ADR or all-hands since the last reconciliation (`docs/decisions.md`
still stops at ADR-40, `docs/allhands/` still nothing newer than
2026-09-18-close), no sprint item owned by research/market/skill/
security/writer sits unattempted, and no dispatchable seat carries two
open PRs on one scope. Ceilings after this run: 1 of 3 used today.

## Tier B merges this run (`docs/standards/pm.md` §10), four

- **#298** (exo-centralizer, the two dispatch guards — `allowed_bots:
  "github-actions[bot]"` and `actions: read` on every seat workflow,
  citing ADR-049) — clean, no Tier C path (workflow files are Tier B
  material per §10's own text, not Tier C; Tier C is charters,
  `company.yaml`'s roster/secrets, and spend). **This is the fix
  `INC-2026-09-24-dispatch-403`'s amended entry has been waiting on since
  2026-10-14.** One citation gap worth naming rather than acting on:
  ADR-049 does not exist yet in this repo's `docs/decisions.md` (still
  stops at ADR-40); the comment is explanatory, not a new authority claim,
  and the fix is ordinary Tier B workflow material regardless of whether
  the number is vendored here yet, so this did not block the merge — but
  the citation is owed a record per the cross-repo-law rule the next time
  anyone touches `docs/decisions.md`.
- **#60** (engineer, the pre-send quality gate, sprint-2026-09-21 item 4)
  — **25 days open, and mergeable today for the first time.** The
  engineer rebased it onto current main yesterday (2026-10-14 16:31 UTC)
  per this seat's own handoff; the diff no longer touches `prompts/`
  anything (the file that made every prior standup call it Tier C,
  `prompts/daily.md`, is gone from the diff entirely), checks green, no
  hold, no owner comment since the push. Merged clean.
- **#299** (frontend, weekly visual review) — clean on its own, opened
  `CONFLICTING` against `#60` after `#60` landed (both append to
  `docs/agents/incidents.md`/`docs/ideas.md`). Docs-only, resolved per
  §10 rule 5: merged `main` into the branch, kept both sides, pushed,
  merged clean.
- **#300** (writer, four prose gates) — same docs-only conflict against
  the two merges above, same resolution.

`main`'s next `checks.yml` run came back green after all four.

## Failures (`docs/standards/pm.md` §11.7)

- **Run `38592352927` (pm-agent, this seat, 2026-10-14 15:46:59 UTC) —
  real defect, filed.** The model step finished clean (205/300 turns,
  $9.93, no errors) but produced no commit, no branch and no pull
  request at all — not a teardown loss, a run that never wrote anything.
  New incident: `INC-2026-10-14-the-standup-ran-205-turns-and-shipped-
  nothing` in `docs/agents/incidents.md`, with a named contributing
  cause (`pending.md` itself is ~1,970 lines and growing every run,
  which is a growing share of any standup's turn budget before it writes
  a word) and a proposed fix for the next ceremony: split `pending.md`
  into a dated archive so the standup stops reading its own history in
  full each time. No rerun — the trigger was a schedule, not a transient
  fault, and the same context would reproduce the same risk.
- **Run `38594124029` (frontend-agent, 2026-10-14 15:59:02 UTC) —
  configuration, already filed, rerun also failed, same cause, not a
  repeat worth a second incident entry.** This is the dispatch that
  first cleared the 403 and then died at the `claude-code-action`
  actor-gate (`INC-2026-09-24-dispatch-403`'s amended entry). The fix
  (`#298`, above) merged this run, so this run reran it once with
  `GH_TOKEN="$DEFAULT_WORKFLOW_TOKEN" gh run rerun --failed 38594124029` —
  attempt 2 hit the identical `Workflow initiated by non-human actor`
  error, because GitHub's rerun replays the workflow YAML pinned to the
  original trigger, not `main`'s current version, so the fix was never
  in scope for it. A fresh dispatch was fired instead; see "Dispatched by
  the PM" below for the run that actually tests the fix.

## Run health

Fleet: the two failures above, both triaged, zero untriaged. One cap-
ratio flag (`docs/standards/pm.md` §11.4/`docs/agents/turn-caps.md` rule
5): **engineer, run `38592441554` (2026-10-14 15:47:35 UTC), 157/200
turns = 78.5%**, above the 70% line; not a cap-out, worth the ExO's
weekly re-derivation. All other runs since the last standup (engineer
×2 more, frontend, writer, checks, deploy-main) completed successfully
under their caps.

**Queue gauge, four numbers.**
1. `main`'s newest commit: this run's own merges, 2026-10-15T15:42:19Z —
   effectively now. Newest `checks.yml` on `main`: success.
2. Open pull requests: 8 total, 0 opened since the last merge (this
   run's own).
3. Conversion, trailing 7 days: 27 merged / 56 opened (0.48).
4. Deepest open supersession chain: 3 — `#292` → `#294` → `#301`
   (engineer, the till alarm/Polar PR), currently `CONFLICTING` against
   main, not this seat's to text-resolve (product code, not docs-only).

**Delivery health** (`docs/agents/delivery-health.md`, checked live
against the database via `tools/delivery_health.py`): **FAILING on
press, pipeline, deploy and site, all four.** The press has now missed
two consecutive weeks — 2026-W40 is still the newest issue and W41 has
already ended. `claims` hasn't moved in 8 days with 2,308 papers waiting
in `distill_queue`; the account now driving distill is the Groq
fallback, not Moonshot, and ADR-39's own window (250,000 characters) is
the one stage that fallback cannot carry inside its 8,000-token-a-minute
limit — this is a sharper diagnosis than prior standups had, not a new
problem. Deploy: `interpret` is 1.9 days and `triage` 2.8 days behind
`main` (14 and 16 undeployed commits respectively). Archive and MCP are
both fine. This is unchanged in kind from every standup since
2026-09-21 and still needs a `modal deploy` only the owner or chair can
run.

## Board

Inbox for `pm`/`alexandria` carried nothing addressed specifically to
this seat (two broadcast "everyone" notes from Ursa's own PM seat, not
actionable here). Board's sprint object still reads `sprint-2026-10-05`
("The press runs itself") — the same stale-object gap named ceremony-
sized by the 2026-10-10 standup, now five ceremonies running; not
attempted again as a standup-sized fix. Two items the frontend's
2026-10-14 visual run filed (the masthead-width inconsistency, the
verdict-queue density fix) sit in Backlog, untouched this run — they are
design-system calls for the owner, not a standup's to move.

## Dispatched by the PM

**2026-10-15, frontend.** Run:
https://github.com/alexandrapaiz/alexandria/actions/runs/38764121612

```
GH_TOKEN="$DEFAULT_WORKFLOW_TOKEN" gh workflow run agent-frontend.yml \
  -f owner_instructions='Sprint-2026-10-12 item 4: ship the Left-Behind Index as a public page over the deprecated_claims view (serves O2 and the sales seats two gated outreach notes). Carried unbuilt across sprint-2026-09-28, sprint-2026-10-05 and sprint-2026-10-12; board item 03029cad-e613-41ea-9295-3e3e15342f22. PR survey: no open frontend PR exists (the last one, #299, merged this run); no frontend PR has ever attempted this item. Decide public-vs-paywalled against vision.md section 4 before writing the route. Build it and open a PR; move the board item to In progress when you start and comment the PR link when you ship. This is a fresh dispatch, not a rerun: the prior attempt (run 38594124029, 2026-10-14) died at a claude-code-action actor-gate that PR #298 just fixed on main; a rerun of that old run failed again because GitHub reruns do not pick up a workflow-file change, so this is a new workflow_dispatch to actually exercise the fix.'
```

**Confirmed: the actor gate is actually cleared.** The `claude-code-
action` step started at 15:53:10 UTC and stayed `in_progress` well past
the few seconds the gate-rejection error takes to surface (it killed
both the original dispatch and its rerun in under 5 seconds each). This
is the first dispatch in the 21 days since `INC-2026-09-24-dispatch-403`
was first filed to actually reach the model. Full outcome (whether it
ships the Left-Behind Index) is not yet known at the time this PR was
opened; frontend runs carry a 600-turn cap and typically run long.
