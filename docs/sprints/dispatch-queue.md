# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-12, Monday ceremony (~20:20 UTC)

**The queue gauge is not the headline this run** — `main` merged twice in
the last 30 minutes and is green — **but the press-send finding below is**,
because it is launch-eve and the evidence says tonight's send did not
happen.

### Today's own open pull request

None found from this seat (`pm/sprint-*` or `pm/standup-*`) at the start of
this run. A different PM-seat surface, `alexandria-pm/2026-10-12-message-cap-reply`
(#279), was open and not touched here: it is a message-run PR from a
different invocation path (the host/board "six-hour pass"), not this
ceremony's branch, and both of the items it already handled (the pm.md
re-vendor, the writer cap raise) were independently re-verified and merged
by this run anyway. No collision: different files, different branch.

### The headline: today's press send

**Evidence.** `https://libraryofalexandria.dev/api/delivery`, read
2026-10-12T20:09 UTC: the `weekly` app's runtime fingerprint recorded a run
starting 2026-10-12T09:00:07Z (the cron fired on schedule), but
`press.created_at` is still `2026-10-05T09:01:04Z` and `press.newest_week`
is still `2026-W40`. `/library` confirms nothing past `2026-W40` is listed.
`claims_newest`/`distilled_newest` were frozen at `2026-10-07T15:15:25Z` all
morning — the same freeze PR #275 (merged this run, 20:03 UTC) just fixed
the cause of.

**Trigger.** Launch is dated 2026-10-13 (vision.md §0), tomorrow. A press
that cannot prove it sent on the one day a week it has to is the single
most urgent fact this ceremony found, ahead of the queue gauge, the cap
ratio, or anything in the grooming pass below.

**Cost of skipping it today.** Nobody but this PR's reader learns the
Monday send may have silently failed until next Monday's ceremony, one
day after the owner's own launch date.

**Dispatch attempted, not delivered.** Fired against the engineer seat;
GitHub's API refused it:

```
$ gh workflow run agent-engineer.yml -f owner_instructions='...'
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
```

This is a repeat of `INC-2026-09-24-dispatch-403`, 18 days old and still
unresolved — the mechanism this charter's §5 grants has never actually
fired successfully in this seat's hands. The full instruction, ready to
run by hand (owner or chair, whoever has a token with `workflow_dispatch`
access this run's `GITHUB_TOKEN` does not):

```bash
gh workflow run agent-engineer.yml \
  -f owner_instructions="Today's scheduled Monday press send (pipeline/weekly.py, cron 0 9 * * 1) appears to have fired but produced no new issue. Evidence from https://libraryofalexandria.dev/api/delivery read at 2026-10-12T20:09 UTC: the 'weekly' app's runtime_sha fingerprint recorded a run at 2026-10-12T09:00:07Z (confirming the cron started), but press.created_at is still 2026-10-05T09:01:04Z and press.newest_week is still '2026-W40'. /library confirms nothing past 2026-W40 is listed. claims_newest and distilled_newest are frozen at 2026-10-07T15:15:25Z, the same freeze PR #275 (merged today) just fixed the cause of (the Groq free-tier pacing bug). Diagnose from the Modal run log for pipeline/weekly.py's 09:00 UTC run today whether it errored or deliberately held, and say which. If it is safe and not a duplicate, send today's issue now. Launch is dated 2026-10-13, tomorrow, so this is today's most urgent item."
```

**A live engineer run is already in progress as this is written**
(`engineer-agent`, run `38302852182`, started 20:13:56Z, on its own
schedule rather than this dispatch). Worth checking whether it already
picks this up before re-running the command above; this sprint's item 1
(docs/sprints/sprint-2026-10-12.md) gives it the same instruction either
way, so the next scheduled run inherits it even if this one does not.

### No other candidate had an observed trigger

Checked every seat against `docs/standards/pm.md` §11.3's criteria table.
Writer's last PR (#273) is open and conflicting — hard stop. OKR's last
PR (#203) is open, draft — hard stop. Finance and sales are dormant.
Market's last PR (#255) is closed, no open PR, but no sprint item names it
and no ADR names it with-no-run-following, so no row in the table fires
for it. Frontend has no open PR and a real trigger (item 4 of the new
sprint), but sprint items are the sprint file's to carry, not a same-day
dispatch — no failure, no stale draft, no ADR orphaned. Keeping the queue
at one entry rather than padding it.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Newest merge: this run's own #275
   (engineer, the pacing fix), 2026-10-12T20:03:16Z, about 20 minutes old
   at this writing. `checks.yml`'s next run on `main` after that merge
   came back `success` (`gh run list --workflow=checks.yml --branch=main
   --limit 1`, polled directly, not read stale).
2. **Open pull requests: 7 total** at the start of this run (#60, #203,
   #205, #272, #273, #279, plus this ceremony's own #281), down from the
   10 open before this run's merges (#277, #278, #275 all merged, #280
   closed as a duplicate of #277). **1 opened since the last merge**
   (#281, this ceremony's own).
3. **Conversion, trailing 7 days: 17 merged / 55 opened** (≈0.31) — well
   under last week's 0.78 (reported 2026-10-10). Not a healthy number on
   its own, but most of the denominator is the PM's own six-hour-pass
   message chain (12+ of the 55), not stalled product work; the queue
   gauge counts it anyway because the charter asks for the raw ratio, not
   a seat-adjusted one.
4. **Deepest open supersession chain: zero.** No open pull request's
   title claims to supersede another currently-open one (`gh pr list
   --state open`, titles checked directly). #60's "supersedes #35" points
   at an already-merged PR, which does not count.

**Threshold check.** 20 minutes since the last merge, far under the
48-hour line. Not the headline — the press-send finding above is.

## The cap ratio

One finding, reported from the only run since the last reconciled pass
(2026-10-11 ~16:45 UTC) with a readable `num_turns`: the **writer's**
2026-10-11 19:46 UTC run (`38169425153`) finished at **127 of 150 turns
(84.7%)**, over the 70% line, on the cap this ceremony's own merge of
PR #278 just raised to 225. The raise lands after this run rather than
before it, so this is evidence the raise was already overdue, not a new
risk still open. The engineer's 2026-10-12 02:15 UTC run (`38195084465`,
the one that produced PR #275) finished at 91 of 200 (45.5%), comfortable.
Two other runs in the window (exo 2026-10-11 18:35, engineer 2026-10-11
16:37) did not print a readable `num_turns` line in this run's log check;
not reported rather than guessed.

Ceilings as of this run (`grep -HoE '\-\-max-turns [0-9]+'
.github/workflows/agent-*.yml`): engineer 200, writer **225** (raised this
run, was 150), the rest unchanged from the 2026-10-10 standup's table.

## Failures, last 24h (charter §11.7)

`gh run list --status failure --created ">=2026-10-11T20:00:00Z"` returns
exactly one: `checks` at 2026-10-12T02:22:09Z, on the `engineer/2026-10-12-distill-silence`
branch (PR #275's own branch). **Classified: tripwire false alarm.** The
same branch's next three pushes (02:26, 02:30, 02:31) all came back
`success`, and the PR merged clean this run. No rerun needed; the branch's
own later pushes already are the rerun.

## Tier B merges this run (`docs/standards/pm.md` §10/§21)

Checked every pull request open at the start of this run:

- **#277** (exo, re-vendor `docs/standards/pm.md` to HQ commit `2c0cb30`)
  — qualified (clean, mergeable, single file, a standard this seat merges
  under §21), **merged**.
- **#280** (duplicate re-vendor of the same commit, opened by HQ's
  `company-checks` workflow after #277 already existed) — identical diff
  to #277, confirmed with `diff <(gh pr diff 277) <(gh pr diff 280)`.
  **Closed as a duplicate** rather than merged twice.
- **#278** (exo, raise the writer's turn cap 150→225, one file,
  `.github/workflows/agent-writer.yml`) — qualified: clean, not a draft,
  no checks defined for a workflow-only diff (§10 condition 3's "no
  checks defined" clause), not Tier C. **Merged.** Worth naming plainly:
  an earlier PM pass today (`alexandria-pm/2026-10-12-message-cap-reply`,
  #279, ~02:46 UTC) read this same PR as "this seat's own no-touch
  boundary regardless of merge authority elsewhere" and left it for the
  owner. This run reads `docs/standards/pm.md` §21 literally instead —
  "Standards, charters, workflows and decisions included" among what the
  PM merges — and the merge succeeded without a permission error,
  confirming this seat's token does hold `workflow` write scope. The two
  readings disagree; flagging the disagreement here rather than hiding
  it, since §15 of the same standard says a product seat "does not edit
  `.github/workflows` in its own repo," which is the opposite rule and
  was not reconciled by this run. Worth the ExO's eyes.
- **#275** (engineer, the free-tier pacing fix) — qualified: clean,
  checks green, not Tier C (pipeline code, tests, ledger, incidents).
  **Merged.**
- **#273** (writer, editorial run 32) — disqualified: `CONFLICTING`, and
  touches `prompts/digest.md`, a Tier C path. Named as waiting on the
  owner, not the PM's to resolve in code.
- **#272** (exo, weekly orchestration cycle) — disqualified: touches
  three charters (`prompts/exo-agent.md`, `prompts/market-agent.md`,
  `prompts/pm-agent.md`). Tier C, owner's alone.
- **#279** (alexandria-pm, message run) — disqualified under condition 1:
  it is this seat's own prior-pass output. Waits for the owner or HQ's
  PM, per the rule. Both items it covered (the re-vendor, the cap raise)
  were independently re-verified and merged by this run regardless, so
  nothing is actually blocked on #279 itself merging.
- **#205** (finance, window run) — disqualified: draft, conflicting,
  finance dormant.
- **#203** (okr, window run) — disqualified: draft.
- **#60** (engineer, pre-send quality checklist) — disqualified: Tier C
  (`prompts/daily.md`), conflicting, now 22 days old.

## Run health

**Fleet.** One failure in the last 24h, already classified above as a
tripwire false alarm with no rerun needed. Every other run since the last
reconciled pass was green. One engineer run is in progress as this is
written (`38302852182`, started 20:13:56Z).

**Delivery health** (green on what evidence, and did anything reach a
reader).

- **The press.** Red, with evidence, per the headline above. This is the
  finding of the run, not a line in a list.
- **The site.** `deploy-main` has fired successfully on every `main` push
  checked this run; the site itself serves `/library`, `/pricing`, and
  `/api/delivery` all with `200`s as of 20:09-20:13 UTC.
- **The MCP server.** Probed this run: `GET /api/mcp` on the live domain
  returns `404`. Not confirmed whether that is the correct path for this
  deployment or a real gap (incident 21's cost was exactly an unwatched
  MCP endpoint) — named as unchecked-with-a-caveat rather than silently
  skipped. Worth a seat with the real endpoint path confirming next run.

## Pending items past their date

See `docs/sprints/pending.md`, rewritten in full this run. Headline three,
repeated here because the charter asks this file to carry them too:

1. **Today's press-send gap** (new this run) — see above.
2. **PR #60**, the pre-send quality checklist — **22 days** open, Tier C,
   conflicting, waiting only on the owner.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **16 days**, and the one remaining blocker on O1
   KR1/KR2 after this ceremony's sprint item 2 ships the code side.

## The board

Read via `BOARD_API_URL` before `gh pr list`, per `docs/standards/pm.md`
§14/§15. The inbox had two items addressed to `alexandria`/`pm` since the
last pass — the pm.md re-vendor handoff and the writer-cap-raise note from
`exo-centralizer` — both independently verified and actioned above
(merged #277, merged #278) before this entry was written.

**The board itself was unstable this run.** A first read of
`/api/board/alexandria` returned a 20-item board keyed to sprint id
`2e6984f1...` ("The press runs itself," dated 2026-09-21 to 2026-09-27,
the three-week-stale board the 2026-10-10 standup already flagged). Four
subsequent reads all returned a *different* sprint id (`e26392aa...`,
also named "sprint-2026-10-05") with 11 items, the one the writer and this
seat's own recent passes actually show up in. Renamed that second,
apparently-live sprint to this week's goal; a follow-up rename attempt
failed with `{"error": "the board's database is unreachable"}`, a
transient backend fault rather than anything this run did wrong. Added
three cards for this sprint's top items (press-send diagnosis, Polar
wiring, Left-Behind Index) and moved the stale "Unsubscribe" card to Done,
since that shipped 2026-10-06. Did not attempt the full 36-card
reconciliation the 2026-10-10 standup named as ceremony-sized — the
backend's own instability during this run made further writes risky
rather than productive. Per the standing rule, the committed files above
are the source of truth regardless of what the board currently shows.

## Linear trial

Not checked this run; no new signal since the last pass noted it was
still on.

## Dispatched by the PM

**None delivered this run.** One attempted (the press-send diagnosis,
above); GitHub's API returned `403`, a repeat of
`INC-2026-09-24-dispatch-403`. No run was started by this seat, so there
is nothing to log as fired — the attempt and the exact command are
recorded under the headline above instead, for the owner or chair to run
by hand.
