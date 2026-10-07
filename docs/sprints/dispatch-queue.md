# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-07, six-hour pass (~06:20 UTC)

**Run mode.** Standup-class pass between ceremonies (charter §0): the
Monday ceremony already ran on 2026-10-05, and nothing in this run's
trigger asks for a new one. Section 4 alone.

**This seat's own open pull request.** #239 (`alexandria-pm/2026-10-07-message`),
opened by this seat's own earlier pass today at 00:27 UTC, was still
open and not a draft when this run started, with no owner comment and
no hold label. Built on it rather than opening a new one: same task,
same day, same files.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Newest merge: PR #235, 2026-10-06
   17:28:33 UTC, about **13 hours old** at this snapshot — well under
   the 48-hour line. The `checks.yml`-against-`main` query returns a
   stale `failure` from 2026-10-05 03:36:14 UTC, unchanged for over a
   day, because nothing has pushed to `main` directly since. The live
   signal, same as the last two passes: `main` is still red on the same
   defect (`skills/agent-containment/SKILL.md` carries an empty
   `claims` list), and the fix for it (PR #240) is clean and green but
   not merged.
2. **Open pull requests: 8 total, 4 opened since the last merge**
   (#237, #238, #240, and this seat's own #239; the other four — #205,
   #203, #202, #60 — predate PR #235).
3. **Conversion, trailing 7 days: 58 merged / 75 opened** (≈0.77).
   Lower than the last two passes' ≈0.86-0.87, worth watching rather
   than acting on: one pass's window rolling off a merge-heavy day
   moves this number on its own, and it is not yet the 48-hour
   deadlock state that would make it the headline.
4. **Deepest open supersession chain: 6**, the engineer's main-fix line
   (#204 → #209 → #219 → #226 → #233 → #240), which this pass also
   absorbed a second, previously separate engineer branch (#236) into.
   Every PR in that chain except #240 itself is now closed, so nothing
   else open carries comparable depth.

**Threshold check.** 13 hours since the last merge, well under 48. This
is informational, not the first-thing trigger.

## The cap ratio

Not measured this run, same gap named the last two passes: `gh run
list` reports conclusions, not per-run `num_turns`, and pulling every
run's log to extract it is not a cheap grep. No run in the last 24
hours shows a cap-related truncation in its conclusion.

## Failures, last six hours (charter §11.7)

Zero. `gh run list --status failure --created ">=2026-10-07T00:33:00Z"`
(since the last pass's own commit) returns nothing. No agent-seat
workflow or shared `checks` gate failed in this window. Nothing to
triage, rerun, or file.

## Tier B merge check (`docs/standards/pm.md` §10)

Full account in `docs/sprints/pending.md`. Summary: **zero of the seven
other open pull requests qualify for a Tier B merge this run** (this
seat's own #239 is excluded by condition 1).

- **#240** (engineer, supersedes #233 and #236) — checks green, clean
  against `main`, no conflicts. **Disqualified only on condition 4**:
  the diff carries `prompts/distill.md` and `prompts/distill-practices.md`.
  The best candidate in the queue right now — one merge closes `main`'s
  red suite, a real subscriber row, and a real unsubscribe endpoint.
- **#237** (skill) — disqualified on conditions 3 and 4: checks red
  (inherited, pre-dates the fix), diff carries `prompts/skill-extract.md`.
- **#238** (writer) — disqualified on conditions 3 and 4: checks red
  (inherited), diff carries `prompts/digest.md`.
- **#60** (engineer) — disqualified on conditions 4 and 5: carries
  `prompts/daily.md`, conflicting. Now 16 days old.
- **#205, #203, #202** (finance, OKR, frontend) — drafts, excluded by
  Tier B's own draft condition, not reported as blocked.

## Run health

**Fleet.** No agent-seat workflow failed in the last 6 or 24 hours.

**Delivery health** (green on what evidence, and did anything reach a
reader).

- **The press.** `https://libraryofalexandria.dev/library` lists
  `2026-W40` as newest — matches expectation, no send due before next
  Monday.
- **The site.** `deploy-main`'s last recorded success matches the
  newest commit on `main` touching `site/`. Nothing undeployed.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare unauthenticated GET — up, correctly
  refusing, same as every prior pass.

## Pending items past their date

1. **#240** — green, clean, waiting only on the owner. Highest-leverage
   single merge available right now.
2. **#237** — a second, independent fix for the same defect #240
   already closes. Worth the owner's word on whether both land.
3. **#238** — Tier C, inherits the same `main` defect, waiting on the
   owner.
4. **#60** — 16 days open, Tier C, conflicting, waiting only on the
   owner.
5. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now 11 days, no live keys visible in the tree.

## The board

Read via `BOARD_API_URL` this run, before `gh pr list`, per
`docs/standards/pm.md` §15. Nothing addressed to `alexandria`'s `pm` is
unanswered: the newest item naming this seat is yesterday evening's
reading-enjoyability handoff, already acted on. One broadcast note
(Kimi's prepaid balance) is informational, addressed to everyone, not
this seat specifically.

## Linear trial

Not checked this run, no new signal since the last check.

## Proposed dispatches: none this run

Every blocker found this run is an owner-only merge. Engineer, skill,
and writer each already hold an open pull request of their own, which
is the hard stop on dispatching any of them, and none of their own
further work would clear the blocker anyway. An empty queue here is the
accurate report, not a gap in the reading.
