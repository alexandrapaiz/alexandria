# Org chart

**Enforced at:** prompts/pm-agent.md §1b, which updates this page whenever seats or initiatives change and flags any initiative with no seat.

Maintained by the PM agent (charter §1b). Owner is Product Owner and
merges everything; the ExO reviews the workers; every seat is one PR
per run. Seeded 2026-09-18 by the chair; the PM keeps it current.

## Active seats

**Cadence column changed 2026-10-23.** PR #334 (merged 2026-10-17T21:07:40Z,
"Every seat's clock leaves GitHub: schedule blocks removed, the host
manifest keeps the cadence") removed every cron from
`.github/workflows/agent-*.yml`; the times below are no longer what
wakes a seat. Per that PR's own body, each seat's cadence now lives in
"the host roster in the HQ repository" (HQ decision 056), outside this
repo and outside this run's reach, and a seat is woken by the board's
event bus instead (pm.md §17). The column below is kept as the
**last-known cadence intent** rather than deleted outright, since it is
the only record of it this repo still holds, but it is a historical note
from here on, not a live fact. This edit was queued by name in
`docs/sprints/pending.md`'s 2026-10-17 ~21:00 UTC entry for "the run
after #334 lands," which is this one. **Still open, and not this seat's
to close:** no entry in `docs/decisions.md` names HQ decision 056 or the
local cadence law it overrides, which `docs/agents/cross-repo-law.md`
rule 1 requires and assigns to the ExO seat's §3e, not the PM's; exo's
own PR #381 (open, Tier C) already found this same gap on 2026-10-18 and
it is still unfixed five days later for the reason everything else was,
the host being dark.

| Seat | Charter | Cadence (pre-2026-10-17, historical) | Lane | Current initiative |
|---|---|---|---|---|
| engineer | prompts/engineer-agent.md | was daily 7:06 ET | product code, pipeline | launch runway; architecture evolution; skills sellable — install line + plugin marketplace, buyer-path measurement |
| skill | prompts/skill-agent.md | was Tue 8:00 ET | skills/ gold production | skills-with-receipts (O2); skills sellable — proof inside the first session |
| frontend | prompts/frontend-agent.md | was Wed 8:00 ET | site UI, visual quality | visual audit; mission on site; skills sellable — catalog page, pricing reframe |
| market | prompts/market-agent.md | was Fri 7:00 ET | docs/market/ | positioning under free+$20; skills sellable — pricing-page copy advisory |
| pm | prompts/pm-agent.md | was daily (Mon: ceremony, Tue-Sun: standup) | sprints, backlog, board, org chart, dispatch queue | recovery from the 2026-10-18 to 2026-10-23 host outage; skills sellable regroom re-targeted to Wednesday 2026-10-28 |
| research | prompts/research-agent.md | was Mon 16:30 UTC | input curation: digest review, curation brief, meta-review | what deserves attention; source discovery |
| exo | prompts/exo-agent.md | was Sun 10:00 ET | charters, workflows, org | org learning; GitHub upkeep |
| security | prompts/security-agent.md | was 1st + 15th | debug + defensive audits | pre-launch hardening |
| okr | prompts/okr-agent.md | was 1st monthly | docs/okrs/ | Q4 OKRs; benchmark trendline |
| writer | prompts/writer-agent.md | was daily 16:00 UTC | newsletter voice: prompts/digest.md, docs/voice/, editorial structure | digest worth reading (O1) |

**Gap closed 2026-09-24 (ceremony-lite sync).** The writer seat
(ADR-28, editor-in-chief, owner's decision 2026-09-19) has run
`.github/workflows/agent-writer.yml` daily since 2026-09-19 and merged
seven PRs (#36, #47, #48, and the #55→#81 chain) but was never added
to this table — a seat with no line here is exactly the gap charter
§1b asks this run to flag. Fixed in place rather than left for Monday
since it costs one row.

## Dormant seats (ADR-24, owner activates)

ADR-24 defines dormant precisely: `workflow_dispatch` only, no cron,
"activation is a one-line schedule addition." Both seats below have
been hand-dispatched repeatedly this week (finance: PR #32, #84;
sales: PR #14, #17, #22) but neither has a cron in its workflow file,
so this table is accurate as written, not stale — a prior pending.md
note flagged sales as possibly stale here; checked against ADR-24's
own text this run, and it isn't. Finance's dormant-vs-activated status
is a live question for the owner regardless (see pending.md).

| Seat | Charter | Planned cadence | Lane | Waits on |
|---|---|---|---|---|
| finance | prompts/finance-agent.md | monthly | docs/finance/ OPEX, later revenue | owner activation (cron) |
| sales | prompts/sales-agent.md | on dispatch | docs/sales/ campaigns, drafts only | launch proximity, owner activation (cron) |

## Company initiatives

1. **Launch Oct 13** — pm leads; engineer, frontend, skill execute; sales activates near launch.
2. **Skills as the product** — skill leads; engineer (receipts rendering), market (positioning) support. Sharpened 2026-10-17 by the owner's own directive into five sellable conditions, one seat per condition, done defined as a URL and an install line she runs herself by Wednesday's brief: engineer (install line + plugin marketplace, buyer-path measurement), skill (proof inside the first session), frontend (catalog page, pricing reframe), market (pricing-copy advisory). Full detail in docs/sprints/sprint-2026-10-12.md's "Regroom" section and docs/prfaq/skills-sellable.md. The checkout's mechanical completion needs no seat — it is an owner-only sandbox walkthrough, docs/product/polar-go-live.md, overdue 21 days.
3. **Digest worth reading** — writer leads (voice, structure, ADR-28);
   research (curation, meta-review, ADR-25 renamed the old "weekly"
   seat); engineer (prompt plumbing); market (prose benchmark) support.
   Corrected 2026-09-24: this line still named the pre-ADR-25/28
   "weekly" seat as sole lead.
4. **The org improves itself** — exo leads; okr guards purpose; security guards the boundaries.
5. **Books and growth (dormant)** — finance and sales, when activated.

## Dispatch authority (company standard pm.md §11, ADR-033, active since 2026-09-24)

The PM seat may fire `gh workflow run` against engineer, research,
market, writer, frontend, skill, security, and okr, inside the ceilings
in prompts/pm-agent.md §5 and pm.md §11.4, when the repository variable
`PM_DISPATCH_ENABLED` is `true`. It may never dispatch exo (its own
auditor), itself, or a dormant seat. Every fired dispatch is logged in
docs/sprints/dispatch-queue.md under "Dispatched by the PM". A standing
defect (INC-2026-09-24-dispatch-403, repeated 2026-09-26 and
2026-09-27) has 403'd every dispatch attempted from this seat's own
scheduled run so far; the one dispatch that has actually fired
(PR #113, 2026-09-26) went through a chair-directed synchronous session
instead. Unresolved as of this run; see the incident register. Repeated
again 2026-10-12 (Monday ceremony), same `HTTP 403`, now 18 days old
with zero successful self-fired dispatches in this seat's history.

## The board (company standard pm.md §14, since 2026-09-27)

The company board at board.libraryofalexandria.dev (the `asc-board`
service) is now the state of the work, not GitHub Projects. Every seat
reads it at the start of a run and writes to it as it works, via
`BOARD_API_URL`/`BOARD_RUNTIME_TOKEN` on GitHub runners. The sprint file
in docs/sprints/ is a rendered export of the board's current sprint from
now on, not the other way around.

## Operating modes (owner's rule, 2026-09-18)

Two modes, one org. **Synchronous**: when the owner is present in a
working session, the relevant seats work WITH her, convened live by
the chair or dispatched immediately with her instructions carried in.
**Asynchronous**: when she is away, the schedules are the heartbeat
and every seat works its cadence unattended. Scheduled runs never wait
for her presence; live sessions never duplicate what a scheduled run
is already doing.
