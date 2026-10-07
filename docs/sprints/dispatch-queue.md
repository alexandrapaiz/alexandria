# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-07, six-hour pass (~12:22 UTC)

**Run mode.** Standup-class pass between ceremonies (charter §0): the
Monday ceremony already ran on 2026-10-05, and nothing in this run's
trigger asks for a new one. Section 4, plus the dispatch's own asks:
inbox and failed-run triage, the Tier B merge check against the landed
authority, a sprint-progress line, and one board note.

**This seat's own open pull request.** #239 (`alexandria-pm/2026-10-07-message`)
was still open from an earlier pass today (00:27 UTC) when this run
started, not a draft, no owner comment, no hold label. Built on it on a
new branch (`alexandria-pm/2026-10-07-message-second-pass`) rather than
reusing the open one, then closed #239 with a pointer to this pull
request once containment was verified.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Newest merge: PR #235, 2026-10-06
   17:28:33 UTC, about **19 hours old** at this snapshot — under the
   48-hour line. The `checks.yml`-against-`main` query still returns a
   stale `failure` from 2026-10-05 03:36:14 UTC, over two days old now,
   because nothing has pushed to `main` directly since. The live signal,
   unchanged for three passes: `main` is still red on the same defect
   (`skills/agent-containment/SKILL.md` carries an empty `claims` list),
   and the fix for it (PR #240) is clean and green but not merged.
2. **Open pull requests: 8 total, 4 opened since the last merge**
   (#237, #238, #240, and this seat's own #241; the other four — #205,
   #203, #202, #60 — predate PR #235).
3. **Conversion, trailing 7 days: 58 merged / 76 opened** (≈0.76). In
   the same range as the last two passes (≈0.76-0.87); not the 48-hour
   deadlock state that would make this the headline.
4. **Deepest open supersession chain: 6**, the engineer's main-fix line
   (#204 → #209 → #219 → #226 → #233 → #240), unchanged since last pass.
   Every link in that chain except #240 itself is closed.

**Threshold check.** 19 hours since the last merge, well under 48. This
is informational, not the first-thing trigger.

## The cap ratio

Not measured this run: zero GitHub Actions workflow runs of any kind
fired in the last six hours (`gh run list --created ">=2026-10-07T05:00:00Z"`
is empty), so there is no `num_turns` to compare against any seat's
`--max-turns` this pass.

## Failures, last six hours (charter §11.7)

Zero, on both the fleet and the board. No GitHub Actions run fired at
all in the window, and the company board's own run feed shows nothing
with a non-zero exit since this seat's last pass. Nothing to triage,
rerun, or file.

## Tier B merge check (`docs/standards/pm.md` §10, §21)

**The authority has landed and has held for two days.** HQ decision 041
reached this repo as PR #147 and merged into `main` on 2026-10-05 at
03:31 UTC, carrying the amended standard (§21) and the workflow
permissions this seat's merges use. Checked again this pass rather than
assumed. The finding below is about the shape of the open queue, not
about whether the grant exists.

Full account in `docs/sprints/pending.md`. Summary: **zero of the seven
other open pull requests qualify for a Tier B merge this run** (this
seat's own #241 is excluded by condition 1; #239 is closed).

- **#240** (engineer, supersedes #233 and #236) — checks green, clean
  against `main`, no conflicts. **Disqualified only on condition 4**:
  the diff carries `prompts/distill.md` and `prompts/distill-practices.md`.
  The best candidate in the queue, unchanged for three passes — one
  merge closes `main`'s red suite, a real subscriber row, and a real
  unsubscribe endpoint.
- **#237** (skill) — disqualified on conditions 3 and 4: checks red
  (inherited, pre-dates the fix), diff carries `prompts/skill-extract.md`.
- **#238** (writer) — disqualified on conditions 3 and 4: checks red
  (inherited), diff carries `prompts/digest.md`.
- **#60** (engineer) — disqualified on conditions 4 and 5: carries
  `prompts/daily.md`, conflicting. Now 17 days old.
- **#205, #203, #202** (finance, OKR, frontend) — drafts, excluded by
  Tier B's own draft condition, not reported as blocked.

## Run health

**Fleet.** No agent-seat workflow ran at all in the last six hours, let
alone failed. All green by absence of any red, not by a clean run of
everything.

**Delivery health** (green on what evidence, and did anything reach a
reader) — read from `tools/delivery_health.py` this pass rather than
proxied by hand:

- **The press.** `2026-W40` is written, by `kimi-k2.6`. The daily
  pipeline is ingesting and distilling within two days.
- **The deploy.** A deploy is pending and still inside the 24-hour
  window (triage, 18.9h) — not stale yet.
- **The site.** Two issues published, newest `2026-W40`.
- **The archive.** The record and the public archive both end at
  `2026-W40` — agree, so the read path between them is proven live, not
  just the write path.
- **The MCP server.** Up, and refusing unauthenticated calls.

Every surface checked answered, and every one of them is delivering.

## Pending items past their date

1. **#240** — green, clean, waiting only on the owner. Highest-leverage
   single merge available right now, unchanged for two passes.
2. **#237** — a second, independent fix for the same defect #240
   already closes. Worth the owner's word on whether both land.
3. **#238** — Tier C, inherits the same `main` defect, waiting on the
   owner.
4. **#60** — 17 days open, Tier C, conflicting, waiting only on the
   owner.
5. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now 12 days, no live keys visible in the tree.

## The sprint ("The press runs itself")

No pull request has merged into `main` since #235 on 2026-10-06 at
17:28 UTC, so nothing has moved against the goal since the last pass:
`main`'s test suite is still red on the same defect, the real
subscriber row and the real unsubscribe endpoint are still unshipped.
What moves it next is still the same single action: the owner's merge
of #240. Noted in the sprint file itself, so the goal's own page carries
the same line rather than only this queue.

## The board

Read via `BOARD_API_URL` this run, before `gh pr list`, per
`docs/standards/pm.md` §15. The query returns the cross-company feed
rather than one filtered to `alexandria`, so this run read all of it and
kept what named `alexandria`: nothing addressed to this seat is
unanswered, the newest item naming it is the reading-enjoyability
handoff of 2026-10-05, already acted on.

## Linear trial

Not checked this run, no new signal since the last check.

## Proposed dispatches: none this run

Every blocker found this run is an owner-only merge. Engineer, skill,
and writer each already hold an open pull request of their own, which
is the hard stop on dispatching any of them, and none of their own
further work would clear the blocker anyway. An empty queue here is the
accurate report, not a gap in the reading.
