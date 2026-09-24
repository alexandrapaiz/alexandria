# Org chart

**Enforced at:** prompts/pm-agent.md §1b, which updates this page whenever seats or initiatives change and flags any initiative with no seat.

Maintained by the PM agent (charter §1b). Owner is Product Owner and
merges everything; the ExO reviews the workers; every seat is one PR
per run. Seeded 2026-09-18 by the chair; the PM keeps it current.

## Active seats

| Seat | Charter | Cadence | Lane | Current initiative |
|---|---|---|---|---|
| engineer | prompts/engineer-agent.md | daily 7:06 ET | product code, pipeline | launch runway; architecture evolution |
| skill | prompts/skill-agent.md | Tue 8:00 ET | skills/ gold production | skills-with-receipts (O2) |
| frontend | prompts/frontend-agent.md | Wed 8:00 ET | site UI, visual quality | visual audit; mission on site |
| market | prompts/market-agent.md | Fri 7:00 ET | docs/market/ | positioning under free+$20 |
| pm | prompts/pm-agent.md | Mon 6:35 ET | sprints, backlog, board, org chart | Oct 13 launch runway |
| research | prompts/research-agent.md | Mon 16:30 UTC | input curation: digest review, curation brief, meta-review | what deserves attention; source discovery |
| exo | prompts/exo-agent.md | Sun 10:00 ET | charters, workflows, org | org learning; GitHub upkeep |
| security | prompts/security-agent.md | 1st + 15th | debug + defensive audits | pre-launch hardening |
| okr | prompts/okr-agent.md | 1st monthly | docs/okrs/ | Q4 OKRs; benchmark trendline |
| writer | prompts/writer-agent.md | daily 16:00 UTC | newsletter voice: prompts/digest.md, docs/voice/, editorial structure | digest worth reading (O1) |

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
2. **Skills as the product** — skill leads; engineer (receipts rendering), market (positioning) support.
3. **Digest worth reading** — writer leads (voice, structure, ADR-28);
   research (curation, meta-review, ADR-25 renamed the old "weekly"
   seat); engineer (prompt plumbing); market (prose benchmark) support.
   Corrected 2026-09-24: this line still named the pre-ADR-25/28
   "weekly" seat as sole lead.
4. **The org improves itself** — exo leads; okr guards purpose; security guards the boundaries.
5. **Books and growth (dormant)** — finance and sales, when activated.

## Operating modes (owner's rule, 2026-09-18)

Two modes, one org. **Synchronous**: when the owner is present in a
working session, the relevant seats work WITH her, convened live by
the chair or dispatched immediately with her instructions carried in.
**Asynchronous**: when she is away, the schedules are the heartbeat
and every seat works its cadence unattended. Scheduled runs never wait
for her presence; live sessions never duplicate what a scheduled run
is already doing.
