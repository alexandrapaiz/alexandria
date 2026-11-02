# Dispatch queue — 2026-11-02, ~01:15 UTC (Monday ceremony, PR #683)

Supersedes the copy of this file carried in #531 (closed, superseded by
#683). No 48-hour stall: `main` merged 1 minute ago at the time of this
reading. Full numbers below.

## Run health

**Fleet.** Board run record, 25 rows, back to 2026-11-01T16:00:28Z (8h47m,
short of the 24h floor — noting it per the standing caution rather than
treating 25 rows as 24 hours). Non-successes in that window, all already
registered:

- `engineer` (window:cron, 23:06:00Z) and `security` (window:hook,
  23:04:44Z), both `exit 124` (timeout) — both already have open draft PRs
  from the same runs (#659, and #657, now merged by this ceremony), ship-
  first held, nothing lost. Same class #673 already named; not re-filed.
- `pm` x2 and `writer` x1, all `exit 1, turns 1`, 16:00-18:20Z,
  `"You've hit your weekly limit"` — the third Sunday weekly-limit outage,
  already filed by exo's #656 and covered in #661's standup. Not re-filed.

`gh run list --limit 30`: all green except one `checks` failure on a
skill branch at 00:01:44Z that was already green a minute later on the
same branch (the skill seat's own report named this). `checks.yml` on
`branch=main`: the newest *completed* run reports `success` at
`2026-11-02T00:28:33Z` (for the #674 merge); the #657 merge that landed
during this ceremony (`729b0d58`, ~1 minute old) had not yet produced a
completed `checks` run at the time of this reading — not reported as
green or red, reported as pending.

**Cap ratio** (24h-or-since-last-standup floor; board window was 8h47m,
so this is the ratio over that shorter window, not a full day):

| Seat | Turns / live cap | Ratio |
|---|---|---|
| `exo` | 165 / 200 | **82.5%** |
| `writer` | 163 / 225 | **72.4%** |
| `research` | 113 / 180 | 62.8% |
| `skill` | 150 / 270 | 55.6% |
| `pm` | 115 / 300 | 38.3% |
| `okr` | 37 / 160 | 23.1% |

Caps read live this run from each seat's `agent.toml`
(`exo` 200, `engineer` 300, `pm` 300, `writer` 225, `skill` 270, `research`
180, `okr` 160, `security` 250 — several raised since the 2026-10-24
reading this charter's §4 cites; writer's 150->225 raise in particular is
now confirmed live, closing a pending-tracker item below). Not proposing a
number for either flagged seat, per charter; reporting the ratio and
naming the seat.

## Delivery health

Fresh `tools/delivery_health.py` run this ceremony, reading the artifact
rather than the scheduler:

- **ok**: `compute` (Modal workspace restored — it was the headline red
  finding in the last two ceremonies and is resolved as of this reading),
  `pipeline`, `loop`, `mcp`.
- **FAILING**: `press` (newest issue still `2026-W42`; `2026-W43` ended
  with nothing sent — one issue missing, not caught up since compute came
  back), `checkout` (Polar env vars unset, owner-only), `deploy` (`ingest`
  16.4 days behind `main`, `interpret`/`triage` 8.5 days), `site` and
  `archive` (both read through the same missing `2026-W43`/`2026-W41` gap).
- **unknown**: `payments` (`payment_exceptions` table missing; one schema
  migration closes it).

Sprint-2026-11-02's first three backlog items exist because of this
reading: catch up the backfill, the press, and the deploy lag, now that
the one blocker common to all three (Modal) is gone.

## Queue gauge, four numbers

1. **`main`'s age and check state.** Tip `729b0d58` (merge of #657, this
   ceremony's own merge), ~1 minute old at this writing. Newest
   *completed* `checks.yml` run against `branch=main`: `success`,
   2026-11-02T00:28:33Z (one merge behind; this merge's own check run had
   not completed at reading time).
2. **Open pull requests: 33 total, 0 opened since the last merge.**
3. **Conversion, 7 days: 85 merged / 153 opened (0.556).**
4. **Deepest open chain: #483, depth 13**, this seat's own, now 8.3 days
   old, unchanged since the last three readings.

## Pending items past their date

`docs/sprints/pending.md` was fully rebuilt this ceremony from live
evidence (not carried from #531's week-old copy), so nothing in it is
stale as of this writing. Two items worth naming here because they carry
a clock: the two writer copy-questions asks (posted 2026-11-02T00:32Z,
proceed on silence 2026-11-04T00:32Z) and the ledger's proposed-entry
policy question (asked 2026-10-26, no clock, unresolved, now 636
entries/478 aged instead of 552/387).

## Dispatch queue

`PM_DISPATCH_ENABLED` is empty in this run's environment, so nothing
below is fired — proposed only, for the owner or a chair to copy.

### 1. market — no brief in 17 days against a weekly cadence

**Trigger.** `gh pr list`: market's last and only recent PR is #316,
merged 2026-10-16T18:26:27Z. `docs/playbook.md`'s seat roster lists
market's cadence as "weekly Fri." 17 days have passed with zero market
output, longer than the gap any other active seat is currently carrying,
and market has no open PR (so this is not the dispatch-hard-stop case).
This ceremony's sprint-2026-11-02.md and the 2026-11-01 OKR check-in both
read `docs/market/briefs/2026-10-16.md` as their newest input, which is
now itself 17 days stale.

**Cost of skipping it today.** Every planning input that cites "the
newest market brief" keeps citing the same 2026-10-16 file for a third
and fourth cycle, and O2's positioning question (the $20/month paid spine)
goes another week with no fresh outside read.

**Dispatch.**

```bash
gh workflow run agent-market.yml \
  -f owner_instructions='Produce this weeks market brief (landscape,
demand, positioning). The last brief is docs/market/briefs/2026-10-16.md,
17 days old. Read the 2026-11-01 OKR check-in (docs/okrs/okrs-2026-Q4.md)
for what the quarter still needs measured on the skills-as-product
objective before scoping this weeks read.'
```

## Dispatched by the PM

None this pass (`PM_DISPATCH_ENABLED` empty).
