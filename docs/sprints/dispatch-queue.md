# Dispatch queue, 2026-11-09, Monday ceremony + standup (cron trigger)

**This replaces the 04:58Z version of this file (PR #863), which this run
builds on and supersedes.** The numbers below are read fresh at 11:16Z,
roughly 6.5 hours later, after a large volume of `message`-trigger PM/engineer/
exo/research/skill activity landed on `main` in between. Nothing in the
ceremony's substance (sprint, retro, grooming, org-chart, playbook) changed
in that window — only `docs/ideas.md` grew, by 82 lines of new entries folded
into this PR's grooming — so only this file's time-sensitive numbers needed
re-reading rather than the whole ceremony.

**Read this first, still: is the org's monthly spend cap still in force?**
`INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days`
(engineer, 2026-11-08): the portfolio ran dark for six days
(2026-11-03T00:20Z–2026-11-08T23:02Z) because the org hit its monthly Claude
spend cap and every classifier misread it as the ordinary weekly pool
resetting. The incident's own last line is still unresolved: whether the cap
is still in force "cannot be read from the logs... it is still set and will
bite again before the month ends" unless raised at
`claude.ai/admin-settings/usage`. Unchanged since this morning. Full detail
in `docs/sprints/pending.md`.

**Not firing anything this run.** `PM_DISPATCH_ENABLED` read empty from this
run's own environment, which is the whole check (prompts/pm-agent.md §5):
empty means no dispatch, full stop. The entries below are proposed for the
owner or a chair to copy.

## Queue gauge, four numbers (read 11:16Z)

1. **`main`'s age: about 12 minutes** (tip `39653d8b`, PR #913's merge,
   2026-11-09T11:04:07Z). Checks on `main`: green (`checks.yml`, success,
   10:21:24Z — correctly silent on the two merges since, neither touched its
   path filter). No stall, no dispatch deadlock: four merges landed in the
   last 90 minutes alone (#900, #904, #907, #913).
2. **Open pull requests: 73 total, 3 opened since the last merge** (11:04:07Z).
3. **Conversion: 55/121** merged vs. opened in the last 7 days (~45%).
4. **Deepest open supersession chain: depth 13, PR #483**, this seat's own,
   open since 2026-10-24 (16 days), not superseded further — unchanged from
   this morning's reading. **This seat is blocked on merging it**, per the
   charter's depth-three-plus rule: the PM never merges its own pull request,
   at any depth. Needs the owner or a chair. This ceremony's own PR (#918) is
   itself third in a chain (#683 → #863 → #918), so add this run to the same
   list rather than exempting it.

## Run health

Board read (`GET /api/board/alexandria`) at 11:16Z, 25 rows, back to
08:15:36Z (about 3 hours — short of the 24-hour floor again; the route
returns a fixed row count, not a fixed window). **Four non-successes in this
window, all `exit 124` (workflow timeout), across `engineer` (#892, #900,
#911) and `skill` (#908).** Combined with the two `exit 124` rows this
morning's ceremony already found (`skill` #850, `security`, pre-08:15 and so
outside this narrower window), that is **six `exit 124` instances in one day
across three seats** — a repeat of the exact class this morning's draft of
this file proposed but did not file ("if it recurs, the next run should file
it"). It recurred. Filed this run as
`INC-2026-11-09-exit-124-timeouts-recurred-six-times-in-one-day-across-three-seats-and-nobody-filed-it`
in `docs/agents/incidents.md`. Every instance shipped — ship-first worked as
designed, no pushed work was lost — which is exactly why six of them sat
unfiled for over six hours despite the charter's no-exceptions rule on
repeats.

`gh run list --limit 30`: `checks` and `deploy-main` both green on every
`main` push today. No red `main`.

## Cap ratio (24h floor; board only reaches 3 hours back today)

Four seats over 70% of cap within the visible window, all landed clean (exit
0, no failures):

- **exo**: 178/200 (89.0%), 148/200 (74.0%) — two separate runs today.
- **research**: 147/180 (81.7%).
- **skill**: 215/270 (79.6%).

Caps as read fresh by this morning's ceremony pass from the host manifest
(not the charter's 2026-10-24 snapshot): exo 200, pm 300, research 180,
security 250, skill 270, writer 225, engineer 300, frontend 600, okr 160,
market 160.

## Delivery health

Unchanged from this morning's ceremony reading (`tools/delivery_health.py`,
re-confirmed now rather than re-run, since nothing in this window touches
press/site/compute/checkout paths):

- **ok**: press, compute, pipeline, loop, site, mcp.
- **FAILING, owner-only**: `checkout` (`POLAR_CHECKOUT_*` unset 26+ days),
  `deploy` and `archive` (no seat holds a Modal token). See `pending.md` for
  the full account.
- **unknown**: payments (`payment_exceptions` table does not exist).

## Awaiting your verdict

Unchanged from this morning; none of these resolve by themselves between
ceremony and standup:

- **Grant a Modal token to the engineer seat, or say the deploy/archive gaps
  wait indefinitely.** Blocking Deploy, Press W41, and the W43 backfill since
  before sprint-2026-11-02.
- **637 of 802 `proposed` ledger entries are 14+ days old** (per
  `tools/ledger.py --census`). A systemic verdict bottleneck; the grooming
  agent's recommendation stands: a weekly verdict quota rather than a
  one-time sweep.
- **The own-store task board's OKR home**, five consecutive OKR check-ins
  (09-26 through 11-01) with no ruling.
- **Five `accepted` ledger entries read as already built** and only need a
  one-line status flip to `built`. Flagged in `docs/ideas.md`.
- **The §22 ask from this seat's own #856** (approve PR #851's charter
  propagation) needs a fresh look: #851's content was reverted out of `main`
  this morning by a tier-sweep correction alongside three other PRs merged
  under the wrong tier. See `pending.md`.
- **PR #683, this seat's own week-old ceremony attempt, and the superseding
  chain it started.** Recommend closing #683 (superseded by #863, which this
  PR in turn supersedes) once this PR is reviewed — see "Ship first" note in
  this PR's description for the full chain and why none of #683's unique
  content is lost.

## Proposed dispatches

### 1. market — the brief is still 24 days stale against a weekly cadence

**Trigger.** `docs/market/briefs/` newest file is still `2026-10-16.md`
(re-confirmed 11:16Z). Cadence is weekly Friday; three Fridays have passed
with no new brief (10-23, 10-30, 11-06). No open PR exists from this seat
right now, so this is not a build-on-it case.

**Cost of skipping it today.** O1 is graded `missed` on all three KRs
(2026-11-01 OKR check-in); the positioning read feeding that conversation is
now 24 days old and getting staler.

**Dispatch.**

```bash
gh workflow run agent-market.yml \
  -f owner_instructions='The last market brief is 2026-10-16, 24 days
old against the weekly cadence. Produce a fresh brief: re-read
docs/okrs/okrs-2026-Q4.md's 2026-11-01 check-in (O1 missed on all three
KRs) and docs/agents/delivery-health.md's current state, then rotate the
comparator set per the existing method and say what, if anything, changes
in the $20/month positioning now that the Oct 13 date has passed. Do not
change pricing yourself; name what the owner should weigh.'
```

### 2. frontend — PR #678 claims it is ready to merge and still is not

**Trigger.** #678's own body says "This is the one to merge," written
2026-11-02. Checked live twice this run: first at 11:16Z (`UNKNOWN`, mid-
recompute), then again after it settled: `mergeStateStatus: DIRTY`,
`mergeable: CONFLICTING`, confirming this morning's ceremony reading still
holds a week later.

**Cost of skipping it today.** A depth-3 chain (#554→#559→#678) of visual
design work stays stuck a second week with nobody rebasing it.

**Dispatch.**

```bash
gh workflow run agent-frontend.yml \
  -f owner_instructions='Your own PR #678 (alexandria-frontend/2026-11-02-message)
says it is ready to merge but gh pr view reports mergeable: CONFLICTING
with zero checks on the branch. Build on that branch: rebase against
current main, resolve the conflict, confirm checks run and pass, and
re-push. Do not open a fresh branch for this.'
```

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` is empty, not `true`.
