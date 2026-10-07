# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-07, six-hour pass (~00:30 UTC)

**Run mode.** This is a standup-class pass between ceremonies (charter
§0): the Monday ceremony for this week already ran on 2026-10-05 and
nothing in the triggering message asks for a new one. Section 4 alone.

**This seat's own open pull request.** None at the start of this run.
The last one (the tenth in Tuesday's single-day chain) was merged by
headquarters' PM at 2026-10-06T17:29:16Z, the route this seat asked for
when its own Tier B grant does not cover self-merges. This run opened a
fresh pull request from `main` rather than a chain.

## The queue gauge (four numbers, charter §4)

```
gh pr list --state all --limit 200 --json number,state,createdAt,mergedAt
gh run list --workflow=checks.yml --branch=main --limit 1 --json conclusion,createdAt
```

1. **`main`'s age and check state.** Newest merge: PR #235, 2026-10-06
   17:28:33 UTC, about **7 hours old** at this snapshot — well under the
   48-hour line. The `checks.yml`-against-`main` query itself returns a
   stale `failure` from 2026-10-05 03:36:14 UTC, unchanged for over a
   day, because that workflow runs on pull requests and nothing has
   pushed to `main` directly since. The live signal is the direct
   measurement carried in `docs/sprints/pending.md`: `main` is still red
   on the same defect named last pass (`skills/agent-containment`
   carries an empty `claims` list), confirmed again this run and still
   true because nothing has merged to fix it.
2. **Open pull requests: 9 total, 3 opened since the last merge**
   (the skill seat's fix, the writer's third chain link, and this
   seat's own pull request; the other five — the engineer's two, and
   the finance, OKR and frontend drafts — all predate PR #235).
3. **Conversion, trailing 7 days: 88 merged / 102 opened** (≈0.86).
   Healthy, org-wide. What is not healthy is concentrated: four pull
   requests now wait on one class of owner-only file.
4. **Deepest open supersession chain: 5**, the engineer's main-fix pull
   request (four closed links beneath the open one). The writer's third
   pull request is a chain of 3 in its own right, named in bold in its
   own body as the point at which a seat's charter calls itself blocked
   on merges — carried here as evidence, not news to that seat.

**Threshold check.** 7 hours since the last merge, well under 48. This
is informational, not the first-thing trigger.

## The cap ratio

Not measured this run, same gap named last pass: `gh run list` reports
conclusions, not per-run `num_turns`, and pulling every run's log to
extract it is not a cheap grep. No run in the last 24 hours shows a
cap-related truncation in its conclusion. Ceilings in force, for
reference: engineer 200, exo 200, frontend 600, market/okr 160, finance
120, sales 160, research 180, pm 300, writer 150, security 250, skill
180.

## Failures, last 6 hours (charter §11.7)

`gh run list --status failure --created ">=...-6 hours"` returns 4
runs, all the shared `checks` gate on the writer's open branch, none an
agent seat's own run.

1. **Real defect, already known, not this branch's own.** All four fail
   `tests/test_panel_provenance.py` on the same assertion named last
   pass: `skills/agent-containment/SKILL.md` on `main` still has an
   empty `claims` list. This branch was cut from `main` before either
   candidate fix (the engineer's or the skill seat's, both below) had
   landed, so it inherits the breakage rather than causing it.
2. **No rerun.** The same input fails the same way until a fix merges
   into `main`; rerunning before that would burn a run for an identical
   result.
3. **No new incident entry.** The root cause and both candidate fixes
   are already named in `docs/sprints/pending.md` and carried inside the
   pull requests that fix them; a repeat note here would duplicate
   rather than add.

No agent-seat workflow (engineer-agent, writer-agent, skill-agent,
research-agent, pm-agent) failed in this window.

## Tier B merge check (`docs/standards/pm.md` §10, operationally confirmed this run)

Full account in `docs/sprints/pending.md`. Summary: **zero of the nine
open pull requests qualify for a Tier B merge this run.**

- The engineer's main-fix pull request and the skill seat's independent
  fix for the same defect both carry a file under `prompts/` — Tier C,
  the owner's. The engineer's is also now conflicting against `main`,
  changed since last pass.
- The writer's third pull request carries a file under `prompts/` and
  also inherits the `main` defect above.
- The engineer's second pull request (the real unsubscribe link in the
  sent email) has no `prompts/` file in its diff, but conflicts against
  `main` right now. Its own body already names the fix: merge the
  main-fix pull request first, then this one, with a one-hunk,
  docs-only conflict in two append-only files. That is within this
  seat's authority to resolve once the order holds — not yet, since the
  first half of that order has not happened.
- The pre-send quality checklist carries a file under `prompts/`, is
  conflicting, and is now 17 days old.
- Three drafts (two of the owner's own window sessions, one of the
  chair's) are excluded by Tier B's own draft condition, not reported
  as blocked on this seat.

## Run health

**Fleet.** No agent-seat workflow failed in the last 6 hours or, re-
checked, the last 24. Every failure in that window is the shared
`checks` gate on an already-identified, already-being-fixed defect.

**Delivery health** (green on what evidence, and did anything reach a
reader).

- **The press.** `https://libraryofalexandria.dev/library` still lists
  `2026-W40` as the newest issue. Matches expectation: Monday's 09:00
  UTC send already confirmed landing two days ago and no send is due
  before next Monday. Not a staleness finding.
- **The site.** `deploy-main`'s last recorded success matches the
  newest commit on `main` touching `site/`. No `site/` change on `main`
  has gone undeployed.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare unauthenticated GET — up, correctly
  refusing, same as every prior pass.

## Pending items past their date

1. **The engineer's main-fix pull request** — Tier C, now also
   conflicting, waiting on the owner. Closing it unlocks `main`'s
   checks, a real subscriber row, and a real unsubscribe endpoint in
   one merge.
2. **The skill seat's independent fix for the same `main` defect** —
   Tier C, waiting on the owner, worth a word on whether it duplicates
   or complements the pull request above.
3. **The writer's third pull request** — Tier C and inherits the `main`
   defect, waiting on the owner.
4. **The pre-send quality checklist** — **17 days** open, Tier C,
   conflicting, waiting only on the owner.
5. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **11 days**, no live keys visible in the tree.

## The board

Read via `BOARD_API_URL` this run, before `gh pr list`, per
`docs/standards/pm.md` §15. Nothing addressed to `alexandria`'s `pm` is
unanswered: the newest item naming this seat is headquarters confirming
last pass's merge, which needs no reply.

## Linear trial

Not checked this run, no new signal since the last check.

## Proposed dispatches: none this run

Every blocker found this run is an owner-only merge or a conflict this
seat cannot resolve until that merge lands. No seat's own further work
clears either kind, so the dispatch criteria (`docs/standards/pm.md`
§11.3) do not fire for anyone. An empty queue here is the accurate
report, not a gap in the reading.
