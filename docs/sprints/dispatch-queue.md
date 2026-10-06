# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

**Housekeeping note.** This file had accumulated ten dated sections
across today's chain of PM passes instead of being replaced, which is
the drift this run corrects. Nothing in the older sections is lost: it
is either carried forward below or superseded by what this pass found
fresh.

## 2026-10-06, standup (~17:30 UTC)

**Run mode.** Today is Tuesday, not Monday, so this is the standup
alone (charter §4; §0 says the date decides when no dispatch carries
other instructions, and none did). The Monday ceremony for this week
already ran on 2026-10-05: `docs/sprints/sprint-2026-10-05.md` exists,
the ledger was groomed, and the retro on the prior sprint already
landed, all on main.

**This seat's own open pull request.** PR #235
(`alexandria-pm/2026-10-06-message-pass3`) was already open when this
run started, opened by a host-window session, not this run's scheduled
cron. Its own body says "Full description follows as the run completes"
and the file diffs show that completion never happened. Rather than open
an eleventh branch on top of a chain ten deep, this run continued that
same branch and finished the pass it started. **This is still the
tenth pull request in today's single PM supersession chain**
(#213/#215 → #217/#218 → #222 → #223 → #224 → #225 → #231 → #232 → #234
→ #235), **and per the charter's own depth-3+ rule this seat has been
blocked on merges all day.** The mechanism that actually clears a
product PM's own Tier B pull request is the one epitome's PM used
successfully today (board note, 2026-10-06T12:25:38Z): ask HQ's PM
(`alexandra-systems/pm`) by name. That ask is posted from this run (see
"Dispatched by the PM" below, which also logs it).

## The most important finding this run: `main` is red, and the fix is stuck on a Tier C file, not on review

PR #233 (engineer, clean, green, mergeable, opened 2026-10-06T02:55Z,
"main's red guard, a real subscriber row, and a real unsubscribe")
measured it directly: `python3 -m pytest tests/ -q` is **19 failed,
1021 passed on `main`** and **0 failed, 1185 passed on its own branch**.
Confirmed independently this run: `skills/agent-containment/SKILL.md` on
`main` still reads `claims: []`, which is what
`tests/test_panel_provenance.py` and `tests/test_skill_receipts.py` fail
against. This is not stale CI attribution; it is the file on `main` as
of this run.

**Why this seat cannot clear it under Tier B.** `gh pr diff 233
--name-only` shows `prompts/distill-practices.md` and `prompts/distill.md`
in the diff. Tier C (`docs/standards/pm.md` §10) names "Charters
(`prompts/`)" without carving out the content-generation prompts from
the role charters, and `docs/decisions.md`'s own account of
`prompts/digest.md` (the precedent for exactly this split) also required
the owner's merge. So the whole pull request waits for her, per Tier C's
own rule: "escalates them rather than bypassing her." Every other
condition is already met.

**What it costs to leave it.** `main` has been red on this defect since
before this run started, and the engineer's own PR body says it is the
fifth PR in its own chain (#204 → #209 → #219 → #226 → #233), blocked
on merges the same way this seat is. A second, narrower defect is filed
`urgent` in the ledger by that PR's own account (a `suite-runnable`
failure whose fix needs a `policy` block under `skills/` that ADR-13
reserves for the reviewer panel, outside the engineer's own writable
surface) — named here rather than guessed at further.

## The queue gauge (four numbers, charter §4)

```
gh pr list --state all --limit 200 --json number,state,createdAt,mergedAt
gh run list --workflow=checks.yml --branch=main --limit 1 --json conclusion,createdAt
```

1. **`main`'s age and check state.** Newest merge: PR #228, 2026-10-06
   00:32:12 UTC, about **17 hours old** at this snapshot. The exact
   command the charter names returns a `checks.yml` run against `main`
   from 2026-10-05 03:36:14 UTC (`failure`), unchanged for over a day —
   stale attribution, because `checks.yml` runs on pull requests and
   nothing has pushed to `main` directly since. The stronger evidence is
   the finding above: `main` is red right now, confirmed by running the
   suite's own assertion (PR #233's measurement) and by reading the file
   the test depends on directly.
2. **Open pull requests: 7 total, 2 opened since the last merge**
   (#235 and #233; the other five — #229, #205, #203, #202, #60 — all
   predate PR #228's merge).
3. **Conversion, trailing 7 days: 87 merged / 100 opened** (≈0.87).
   Healthy — this is an org-wide throughput number, and it is not what
   is wrong today. What is wrong today is concentrated in two places:
   this seat's own chain, and one Tier C file blocking a ready fix.
4. **Deepest open supersession chain: 10**, this seat's own (named
   above). No other seat has a live stacked chain of more than one on
   `main`'s queue right now — the engineer's #233 is fifth in its own
   chain, but #204, #209, #219 and #226 are all already closed, not
   open, so they do not add to the open-chain count the gauge asks for.

**Threshold check.** 17 hours since the last merge is under the 48-hour
line, so this is informational, not the first-thing-in-the-PR trigger.
Org-wide throughput is not blocked; this seat's own queue and one
specific Tier C file are.

## The cap ratio

Not measured this run. `gh run list` reports workflow conclusions, not
per-run `num_turns`, and downloading every run's log to extract it is
not a cheap grep (confirmed again this run on one sample). No run in
the last 24 hours shows a cap-related truncation in its conclusion, so
there is no urgent signal, but the 70%-of-cap ratio itself stays
unmeasured. Ceilings in force, for reference: engineer 200, exo 200,
frontend 600, market/okr 160, finance 120, sales 160, research 180, pm
300, writer 150, security 250, skill 180.

## Failures, last 24h (charter §11.7)

`gh run list --status failure --created ">=...-24 hours"` returns 7
runs, all the `checks` workflow, none an agent seat's own run:

1. **Already resolved by supersession, no rerun.** 6 of the 7
   (`engineer/2026-10-05-panel-provenance-red-main` ×3,
   `writer/2026-10-05` ×3) belong to PRs #226 and #227, both already
   closed in favor of #233 and #229. A tripwire whose PR is superseded
   gets a note, not a rerun.
2. **Real defect, still open, no rerun yet.** The 7th
   (`alexandria-writer/2026-10-05-message`, PR #229's own branch,
   2026-10-05 23:28:47 UTC) fails on the same
   `tests/test_panel_provenance.py` assertions as the finding above —
   this branch was cut before the fix that's sitting in #233 existed, so
   rerunning without a rebase would fail identically. This is the
   trigger for the one dispatch below, not a rerun.

Nothing here is older than 24 hours or a workflow the owner paused. No
agent-seat workflow (as opposed to the shared `checks` gate) failed in
this window.

## Tier B merge check (`docs/standards/pm.md` §10, this run's own authority)

All six other open pull requests checked against the five conditions.
**Zero qualify for a Tier B merge this run:**

- **#233** (engineer) — draft: no. Checks: green. Merge state: clean.
  **Disqualified on condition 4**: diff includes `prompts/distill.md`
  and `prompts/distill-practices.md`, a Tier C path. Waits for the
  owner (see the finding above).
- **#229** (writer) — **disqualified on conditions 2 and 3**: still a
  draft, and `checks` is failing. Also touches `prompts/digest.md`
  (Tier C) regardless. Dispatched below instead of merged.
- **#205** (finance) — **disqualified on conditions 2 and 5**: draft,
  and `mergeable: CONFLICTING`.
- **#203** (okr) — **disqualified on condition 2**: draft, despite
  being otherwise clean and mergeable.
- **#202** (frontend) — **disqualified on condition 2**: draft, despite
  being otherwise clean and mergeable.
- **#60** (engineer, 16 days old) — **disqualified on conditions 4 and
  5**: touches `prompts/daily.md` (Tier C) and is `CONFLICTING`. Also
  the oldest open PR in the repository; named again in pending items
  below.

## Run health

**Fleet.** No agent-seat workflow (engineer-agent, writer-agent, etc.)
failed in the last 24 hours; every failure above is the shared `checks`
gate on a now-superseded or already-known-broken branch. One
engineer-agent and one pm-agent run (this one) are `schedule`-triggered
and in progress as this is written; a third engineer branch,
`engineer/2026-10-06-press-unsubscribe-link`, opened mid-run — not yet
old enough to assess.

**Delivery health** (green on what evidence, and did anything reach a
reader).

- **The press.** `https://libraryofalexandria.dev/library` lists
  `2026-W40` as the newest issue — matches expectation, since Monday's
  09:00 UTC send already confirmed landing yesterday and no send is due
  today. Not a staleness finding.
- **The site.** `deploy-main`'s last run was 2026-10-05 03:26:41 UTC,
  success, and matches the timestamp of the newest commit on `main`
  that touches `site/` (2026-10-05 03:26:29 UTC). No `site/` change on
  `main` has gone undeployed since.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare unauthenticated GET — up, correctly
  refusing rather than serving, same as every prior standup.

## Pending items past their date

1. **PR #60**, the pre-send quality checklist — **16 days** open, Tier
   C, conflicting, waiting only on the owner.
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, no live keys visible in the tree as of this run.
3. **PR #233**, red `main`'s fix — new finding, named above, Tier C,
   waiting only on the owner.

## The board

Read via `BOARD_API_URL` this run, before `gh pr list`, per
`docs/standards/pm.md` §15. Nothing addressed specifically to
`alexandria`'s `pm` in the inbox is newer than yesterday evening's
reading-enjoyability handoff (`388df6c3`), and that one is already
acted on (the writer items it created, `7e1841c0` and `59fcc1f4`, are
in "This sprint"). The query also surfaces unaddressed broadcast notes
from other companies' PM seats (`epitome`, HQ) because `to_company`
does not appear to filter — worth a line for the ExO rather than
treated as alexandria's own inbox being busy.

Board item `00863731` ("The merge-authority grant is unconfirmed")
moved to Done and commented: `docs/standards/pm.md` §21 is now vendored
into this repo's own copy (merged as PR #230, commit `c696875`), which
is the confirmation this item was waiting on.

Board sprint record updated to match `docs/sprints/sprint-2026-10-05.md`
(name and goal were still unset): `sprint-2026-10-05`, "The press runs
itself."

## Linear trial

Not checked this run (no new signal since 2026-09-19's "still on, no
verdict" note).

## Dispatched by the PM

### 1. writer — build on the open branch for PR #229

**Trigger.** PR #229 (`alexandria-writer/2026-10-05-message`, the
reading-enjoyability work the chair already assigned, board items
`7e1841c0`/`59fcc1f4`) is a draft whose only `checks` run failed on
`tests/test_panel_provenance.py` (`skills/agent-containment` cites no
claim ids) and is `CONFLICTING` against `main`. That is the same defect
PR #233 already fixed; #229's branch predates the fix.

**Cost of skipping it today.** The urgent reading-enjoyability work the
owner asked for yesterday morning stays unmergeable behind a defect
that already has a fix elsewhere, for no reason tied to the prose work
itself.

**Hard-stop check.** Writer's only open PR is #229 itself; the
instruction below tells it to build on that exact branch, which is the
charter's named exception to "never dispatch a seat with an open PR."
No run was dispatched by anyone in the last two hours (`gh run list
--event workflow_dispatch` shows nothing newer than 2026-10-05 04:42
UTC), so the org is not in synchronous mode. This is the first PM
dispatch today; well inside the three-a-day, one-per-seat ceiling.

```bash
gh workflow run agent-writer.yml \
  -f owner_instructions='Build on the open branch for PR #229
(alexandria-writer/2026-10-05-message). Its only checks run failed on
tests/test_panel_provenance.py: skills/agent-containment/SKILL.md still
has an empty claims list, the same defect PR #233 already fixed on a
different branch. Merge main into this branch (or rebase) to pick up
that fix and resolve the merge conflict, then continue the
reading-enjoyability work the board already assigned you
(items 7e1841c0 and 59fcc1f4): the blind benchmark against the market
register, and the quality bar in the digest prompt and voice check.'
```

Run URL and result: logged in the next pass once the workflow starts
(this run fires it after pushing this file, per the three-minute
spacing rule — there is only one dispatch this run, so spacing does not
bind, but the fire happens after the commit either way).
