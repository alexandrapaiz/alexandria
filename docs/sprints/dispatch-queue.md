# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-07, standup (~17:50 UTC)

**Run mode.** Today is Wednesday, so this is the standup alone (charter
§0: date decides when no dispatch instruction says otherwise, and none
did). No sprint opened, no retro, no grooming.

**This seat's own open pull request.** #241 (`alexandria-pm/2026-10-07-
message-second-pass`) was open when this run started, opened by an
earlier chair session today (its own second pass, which itself built on
#239, closed). Same files this run also writes
(`dispatch-queue.md`, `pending.md`), so this run built on it rather than
branching from `main`: `git log origin/alexandria-pm/2026-10-07-message-
second-pass ^HEAD` printed nothing before any new work was added.
**This is the third pull request in today's single PM chain
(#239 → #241 → this one), and per the charter's own depth-three rule,
this seat has been blocked on merges all day.** Closed #241 with a
pointer here once this PR was open.

## The most important finding this run: the deploy-drift guard just caught a real gap, not a false alarm

`tools/delivery_health.py --surface deploy` reports `triage` FAILING:
its deployed sha is `0f8e1554c1b7`, the sha its own files on `main` hash
to is `110507632118`, and the merge that caused the difference landed
**2026-10-05 04:33:28 UTC**, 61.3 hours ago against the guard's 24-hour
grace. `interpret` and `weekly` both read current. The pipeline is not
down: triage still runs daily, judging papers against logic from before
that merge.

This is the first time this guard has tripped on a real gap since it
shipped (sprint 2026-09-28 item 2), which `docs/sprints/pending.md`
named as the thing that would let this seat stop carrying the class as
a standing worry. It confirms the guard works and that the underlying
gap is real at the same time.

**The repeat this is.** Same shape as
`INC-2026-09-30-triage-runtime-change-with-no-rehearsal` and
`INC-2026-09-28-repair-written-never-deployed`: merged is not deployed.
Filed as `INC-2026-10-07-triage-deploy-drift`. No seat holds Modal CLI
access, so the fix has always been an owner or chair action: one
command, `modal deploy pipeline/triage.py`, then a re-run of
`tools/delivery_health.py --surface deploy` to confirm it cleared.
Posted as a non-urgent `ask` to the board (message
`56c37211-edd0-48e7-85e0-c3352800fd18`) rather than sent to her phone,
because nothing a reader sees is broken today.

**One honest note, not re-litigated further.** The prior pass (#241,
12:23 UTC) reported every delivery surface including deploy as
delivering, with deploy "pending and still inside the 24h window." The
arithmetic above does not support that reading even at 12:23 UTC: the
same merge timestamp would already have been about 56 hours old then,
past the 24-hour grace either way. This looks like that pass's read was
mistaken rather than the state having changed in the last 5 hours.
Flagged so the next pass does not inherit the same error, not re-argued
past that.

## Run health

**Fleet.** No agent-seat workflow has failed since the last pass.
`gh run list --status failure` in the last 24 hours returns 8 `checks`
runs, all against branches already known to be red on the inherited
`skills/agent-containment` defect (`writer/2026-10-06` ×4,
`skill/2026-10-06-agent-containment-retrofit` ×4) — no new failure
class, no rerun warranted (the same input would fail the same way).
One engineer-agent run started at 17:46 UTC, concurrent with this one,
and has already opened PR #242 (draft, "supersedes #240") — too fresh
to assess; #240 itself is now closed as a result.

**Delivery health**, read directly this pass: press ok (`2026-W40`,
`kimi-k2.6`); pipeline ok (ingesting and distilling within two days);
**deploy FAILING** (above); site ok (2 issues, newest `2026-W40`);
archive ok (record and site agree at `2026-W40`); MCP ok (up, correctly
refusing unauthenticated calls). Five of six surfaces deliver; the
sixth is the finding above.

## Tier B merge check (`docs/standards/pm.md` §10)

Zero of the other seven open pull requests qualify:

- **#242** (engineer, new this run) — draft, still in progress.
  Excluded on condition 2.
- **#238** (writer) — checks red on the inherited `agent-containment`
  defect. Excluded on condition 3. Also carries `prompts/digest.md`
  (Tier C) regardless.
- **#237** (skill) — checks red, same inherited defect. Excluded on
  condition 3. Also carries a `prompts/` file.
- **#60** (engineer, 17 days old) — `CONFLICTING`, and touches
  `prompts/daily.md` (Tier C). Excluded on conditions 4 and 5.
- **#205** (finance, window session) — draft, `CONFLICTING`. Excluded
  on conditions 2 and 5.
- **#203** (OKR, window session) — draft, otherwise clean. Excluded on
  condition 2 alone.
- **#202** (frontend, window session) — draft, otherwise clean.
  Excluded on condition 2 alone.

No merges performed this run.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Newest merge: PR #235, 2026-10-06
   17:28:33 UTC, about **24 hours 20 minutes** old at this snapshot,
   still under the 48-hour line. The `checks.yml`-on-`main` command
   still returns a stale 2026-10-05 `failure` (nothing has pushed to
   `main` directly since). Direct evidence instead: `skills/agent-
   containment/SKILL.md` on `main` still reads `claims: []`, so the
   test-suite defect PR #240 (now #242) exists to fix is still live on
   `main` right now, not only inferred from a stale check run.
2. **Open pull requests: 8 total, 4 opened since the last merge**
   (#237, #238, #242, and this one — #240 and #241 both opened and
   closed inside this same window, so they no longer count toward the
   open total).
3. **Conversion, trailing 7 days: 38 merged / 74 opened** (≈0.51).
   Lower than the last pass's 0.76 — the window moved forward a day and
   dropped a cluster of older merges rather than any new stall; nothing
   has merged to `main` in the last 24 hours either way, so this number
   is not yet the headline signal the 48-hour threshold would make it.
4. **Deepest open supersession chain: 7**, the engineer's main-fix line
   (#204 → #209 → #219 → #226 → #233 → #240 → #242, all but #242 now
   closed), one link deeper than the last pass since #240 was
   superseded by #242 this run. This seat's own chain is 3 (above).

**Threshold check.** 24h20m is just over half the 48-hour line.
Informational, not yet the first-thing trigger; worth watching at the
next pass rather than acting on now.

## The cap ratio

Not measured this run, same limitation as every prior pass: `gh run
list` reports workflow conclusions, not per-run `num_turns`, and
downloading every run's log to extract it is not a cheap grep. No run
in the last 24 hours shows a cap-related truncation in its conclusion.
Ceilings, for reference: engineer 200, exo 200, frontend 600,
market/okr 160, finance 120, sales 160, research 180, pm 300, writer
150, security 250, skill 180.

## Dispatch queue: empty

No candidate this run carries fresh evidence. Engineer, writer, and
skill — the three seats with cadence work open right now — each
already hold an open or in-progress pull request of their own (#242,
#238, #237), the hard stop on dispatching any of them without a named
reason to build on that exact branch, and none of their own further
work would close either of today's two blockers (the Tier C files in
the merge-ready PRs, and the triage deploy, which is outside every
seat's writable surface or access). The deploy-drift finding is not a
dispatch candidate for the same reason it is an owner/chair ask: no
seat holds the credential that would fix it.

## Pending items past their date

1. **PR #60**, the pre-send quality checklist — **17 days** open, Tier
   C, conflicting, waiting only on the owner.
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **11 days**, no live keys visible in the tree.
3. **The triage deploy drift**, new this run — owner/chair action,
   `modal deploy pipeline/triage.py`, named in full above.
4. **Decide on #237 vs. #242** (both fix the same `main` defect,
   independently) — still open, carried from the last pass.

## The board

Read the inbox first, per standard §15. Nothing addressed to
`alexandria`'s `pm` is newer than this seat's own 12:31 UTC note from
the earlier pass today. The cross-company feed still surfaces other
companies' broadcasts under the same query, unfiltered by
`to_company`, consistent with every prior pass's note on this — an ExO
fix, not this seat's. Posted one first-person note and one `ask` this
pass (the deploy-drift finding above, message
`56c37211-edd0-48e7-85e0-c3352800fd18`), no codes in either body.

## Linear trial

Not checked this run, no new signal since 2026-09-19's "still on, no
verdict" note.
