# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-29 (Tuesday standup)

**One entry, fired this run.**

### 1. skill — the Tuesday cron never fired, and sprint item 4 is ready and waiting

**Trigger.** `agent-skill.yml`'s own schedule (`0 12 * * 2`, 8:00 AM ET
Tuesdays) did not run today. `gh run list --workflow=agent-skill.yml`
shows the last scheduled run was last Tuesday, 2026-09-22T15:50:51Z; the
workflow is confirmed `active` via the Actions API, and no run of any
kind appears for it since 2026-09-26 (a `workflow_dispatch`). It is now
16:53 UTC, just under five hours past the scheduled time, with nothing
queued or in progress. Separately, sprint item 4 in
`docs/sprints/sprint-2026-09-28.md` (still on the open, unmerged
`pm/sprint-2026-09-28` branch, PR #129) assigns the skill seat exactly
this kind of day-sized work: rewrite the trigger-test decoy panel to
the library's own word budget and re-measure lexical/2.1 against
lexical/3, carried from the skill seat's own recommendation in PR #83
and not yet acted on.

**Cost of skipping it today.** A second missed week on a fix the skill
seat itself flagged, and the cron gap goes unreported until the next
scheduled Tuesday, another 7 days away, since nothing else in this org
watches skill's cadence.

**No open PR blocks this.** `gh pr list --state open` shows nothing on
a `skill/*` branch.

**Dispatch, fired this run:**

```bash
gh workflow run agent-skill.yml \
  -f owner_instructions='Your own Tuesday 12:00 UTC schedule did not fire
today (last scheduled run was 2026-09-22); this dispatch exists to close
that gap, not to add new scope. Sprint item 4, from the sprint plan still
open on PR #129 (docs/sprints/sprint-2026-09-28.md on branch
pm/sprint-2026-09-28, read it from that branch since it has not merged
to main yet): rewrite skills/_validation/decoys.json to the library's own
word budget (100-150 words, matching skill description length, not the
current ~40-word decoys), add the length-warning check from incident 31
to trigger_test.py, and re-measure lexical/2.1 against lexical/3 on the
same cases with the confound removed. This was your own recommendation
from PR #83, not yet acted on. Done means both result bundles filed
under skills/_validation/results/ with today'\''s date, and a plain
statement of which engine wins now that the confound is removed.'
```

Run URL recorded below under "Dispatched by the PM" once fired.

**Not proposed for any other seat.** Engineer has an open PR (#133,
superseding #130 and the whole earlier chain) — a hard stop under §4's
rule regardless of the deploy-drift item (sprint item 2) still being
open, and that item needs Modal CLI access no seat holds anyway, which
makes it an owner action rather than a dispatch. Frontend's own
Wednesday cadence covers sprint item 5 tomorrow with no gap to close
today. Research, market, writer, security, and okr have no fresh,
evidenced trigger: writer's daily run is under an hour past its usual
time, well inside the multi-hour variance this lane has shown all week,
so that is not treated as a miss.

## Run health

**Fleet health.** One repeat non-success to account for since the last
PM run (2026-09-28T18:13:40Z, the ceremony): `engineer-agent`
2026-09-29T02:32:53Z read as `failure` in `gh run list`. This is the
same already-diagnosed class as the prior five (`INC-2026-09-26-run-
report-dash-echo`, escalated at `INC-2026-09-28-dash-echo-sixth-
failure`): the run's real work completed and opened PR #133, only the
`Post run report` step crashes on a dash-vs-bash `echo` bug in twelve
workflows at once. The fix (`tools/run_report.py`, tested) is written
and sitting in PR #133, but landing it needs a one-line edit to
`.github/workflows/agent-*.yml`, which no seat's token can push
(`docs/agents/pending-workflow-changes.md`'s structural blocker). This
is now an eight-run streak per PR #133's own count. It cannot be
queued as a dispatch (`exo` is a forbidden seat under charter §5, and
this needs a workflow-file edit, not a run), so it goes here as an
owner action: merge PR #133, then apply the workflow edit yourself or
route it through the ExO seat's Sunday cadence sooner than that.

Also new and unexplained: `agent-skill.yml`'s Tuesday schedule did not
fire today. See the dispatch above, which is this run's response to it
rather than a separate finding.

Both `engineer-agent` and `pm-agent` (this run) show as `in_progress`
in the same minute this run started, both `schedule`-triggered, not
`workflow_dispatch` — the org's two independent daily crons landing
close together, not a synchronous-owner-present condition. No other
`workflow_dispatch` run appears in the last two hours, so the §5
"owner present" guard does not block today's dispatch.

**Delivery health.**

- **The press.** No database credential in this sandbox, so the
  `digests` table itself could not be queried; reported `unknown` per
  guardrail 4, not green. `https://libraryofalexandria.dev/library`
  returns 200 and still lists `2026-W39` as newest, consistent with no
  new issue being due until Monday 2026-10-05. Not a staleness finding.
  PR #133 carries `tools/delivery_health.py`, a script that would
  automate this exact check once `DATABASE_URL` exists as a repo
  secret (still the open, owner-only "urgent" ledger item).
- **The site.** `https://libraryofalexandria.dev/` returns 200.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  answers HTTP 404 on a bare unauthenticated GET — up, and correctly
  refusing rather than serving.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone, per
charter §4; full `pending.md` reconciliation is ceremony-only, §1d).
One item worth naming here rather than waiting for Monday: the
`DATABASE_URL` read-only credential (filed `urgent` in `docs/ideas.md`
by PR #130) is now blocking two things at once, this run's delivery
check and PR #133's own new tool.

## GitHub Projects board

`PROJECTS_TOKEN` is present, but the GraphQL query this seat has used
before (`user(login: "alexandrapaiz").projectV2(number: 4)`) returned
`NOT_FOUND` this run. Not dug into further to keep this run cheap, per
charter §4's "spend few turns on it" — noted rather than left silent.

## Linear trial

Not checked this run (no new signal). Still on trial per the
2026-09-19 ruling; no verdict recorded since.

## Dispatched by the PM

1. **skill**, 2026-09-29, dispatched to close the Tuesday cron gap and
   run sprint item 4 (decoy panel rewrite, lexical/2.1 vs lexical/3
   re-measure). Full instruction: see entry 1 above. Run: *(added after
   firing, below)*
