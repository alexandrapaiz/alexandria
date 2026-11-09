# Dispatch queue, 2026-11-09, Monday ceremony + standup (message trigger)

**Read this first, before the queue gauge: is the org's monthly spend cap
still in force?** `INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days`
(engineer, 2026-11-08): the portfolio ran dark from 2026-11-03T00:20Z to
2026-11-08T23:02Z — zero pull requests opened anywhere in this repository
for six days — because the org hit its monthly Claude spend cap and every
classifier misread the refusal as the ordinary weekly pool resetting. The
incident's own last line is unresolved: "whether the monthly cap is still
in force cannot be read from the logs... it is still set and will bite
again before the month ends" unless raised at
`claude.ai/admin-settings/usage`. Full detail in `docs/sprints/pending.md`.

**This ceremony also found and is carrying forward PR #683**
(`alexandria-pm/2026-11-02-ceremony`), this seat's own ceremony attempt
from a week ago, open and unmerged the whole time. Its unique content
(retros and two sprint files this run had no other way to know existed)
is folded into this PR; its conflicting edits to the files below are not,
because its branch is a week stale against `docs/ideas.md` alone. Full
account, and the recommendation to close it as superseded, in
`docs/sprints/pending.md`.

**Not firing anything this run.** `PM_DISPATCH_ENABLED` read empty from
this run's own environment, which is the whole check (prompts/pm-agent.md
§5): empty means no dispatch, full stop. The two entries below are
proposed for the owner or a chair to copy, exactly as every standup's
queue is.

## Queue gauge, four numbers

1. **`main`'s age: about 20 minutes** (tip `0d873f79`, this run's own merge
   of PR #850, 2026-11-09T04:56:06Z). Checks on `main`: green
   (`checks.yml`, success, 04:56:09Z). No stall, no dispatch deadlock.
2. **Open pull requests: 70 total, 2 opened since the last merge.**
3. **Conversion: 60/128** merged vs. opened in the last 7 days (~47%).
4. **Deepest open supersession chain: depth 13, PR #483.** This seat's
   own, open since 2026-10-24 (16 days), not superseded further.
   **This seat is blocked on merging it**, per the charter's own
   depth-three-plus rule: the PM never merges its own pull request, at
   any depth. Needs the owner or a chair. Second-deepest: PR #860
   (security), depth 4, self-reported as "blocked on merges," draft, run
   was live as of this check.

## Run health

Board read (`GET /api/board/alexandria`), 25 rows, back to 01:45:13Z
(about 3.2 hours — short of the 24-hour floor; the API returns a fixed
row count, not a fixed window, so earlier non-successes today are not
visible from this call). Two non-successes, both a class not yet in
`docs/agents/incidents.md`:

- **security**, 03:44:31Z, `exit 124` (timeout), no PR recorded for that
  row. The seat's chain continued (#834→#839→#848→#852→#860, still open,
  draft), so the work was not lost, consistent with ship-first.
- **skill**, 03:37:50Z, `exit 124`, PR recorded as #850. That PR shipped
  complete and green; merged this run under §21. The run that produced it
  died of a wall-clock timeout after its work was already pushed.

`exit 124` is a new failure class for this register (a workflow timeout,
distinct from the provider-refusal `exit 1`/one-turn class already
tracked). Proposed as a register entry rather than filed outright, since
both instances recovered cleanly and neither repeats a known class yet;
if it recurs, the next run should file it.

`gh run list --limit 30`: `checks` and `deploy-main` both green since this
morning's run began. No red `main`.

## Cap ratio (24h floor; board only reaches 3.2h back today)

Two seats over 70% of cap within the visible window:

- **security**: 228 of 250 turns (91.2%), 02:56:37Z run.
- **skill**: 198 of 270 turns (73.3%), 02:53:03Z run.

Caps read fresh from the host manifest this run (not the charter's
2026-10-24 snapshot, which is now stale): exo 200, pm 300, research 180,
security 250, skill 270, writer 225, engineer 300, frontend 600, okr 160,
market 160.

## Delivery health

`tools/delivery_health.py`, run fresh this ceremony:

- **ok**: press (`2026-W44` current, `2026-W45` not due until 11:00 UTC
  today), compute, pipeline, loop, site (4 issues, newest `2026-W44`), mcp.
- **FAILING, red, top of this PR**: `checkout` (`POLAR_CHECKOUT_*` unset
  since 2026-10-14, 26 days — owner-only). `deploy` (ingest 23.6 days
  behind `main`, interpret/triage 15.7 days behind each) and `archive`
  (`2026-W41` and `2026-W43` unopenable) — both owner-only too, on a
  second credential: no seat holds a Modal token
  (`MODAL_TOKEN_ID`/`MODAL_TOKEN_SECRET`), confirmed this run and by the
  engineer's own PR #803. `compute` reading `ok` means the workspace is
  reachable, not that a seat can authenticate to it; this run's first
  sprint draft conflated the two and was corrected before shipping (see
  `sprint-2026-11-09.md`'s own header).
- **unknown**: payments (`payment_exceptions` table does not exist).

## Awaiting your verdict

- **Grant a Modal token to the engineer seat, or say the deploy/archive
  gaps wait indefinitely.** Three board cards (Deploy, Press W41, and by
  extension the W43 backfill) have been blocked on this since before
  sprint-2026-11-02, confirmed unchanged today. See `pending.md`.
- **637 of 802 `proposed` ledger entries are 14+ days old** (confirmed via
  `tools/ledger.py --census`, not a grep estimate). This is a systemic
  verdict bottleneck, not a list to read line by line: only 10 accepted +
  10 built + 5 rejected have ever resolved out of that stream. The
  grooming agent's recommendation, which this seat agrees with: a weekly
  verdict quota is the fix, not a one-time sweep. 48 of the oldest date to
  2026-09-17/18, day one.
- **The own-store task board's OKR home**, five consecutive check-ins
  (09-26 through 11-01) with no ruling: does it earn a key result under
  O3, per `docs/okrs/okrs-2026-Q4.md`'s own recommendation.
- **Five `accepted` ledger entries read as already built** (Member site
  auth/deploy, skill-extract prompt, the harness-engineering trigger fix,
  the Left-Behind Index under both its names, and the writer-charter step-3
  fix) and only need a one-line status flip to `built`, which this seat
  cannot make itself. Flagged with evidence inline in `docs/ideas.md`,
  several of them for the second time 28 days apart.
- **The §22 ask from this seat's own #856** (approve PR #851's charter
  propagation, deadline 2026-11-11T04:10:55Z) needs a fresh look before its
  silence-default applies: #851's content was reverted out of `main` by
  this morning's tier-sweep correction alongside three other PRs merged
  under the wrong tier. See `docs/sprints/pending.md`.

## Proposed dispatches

### 1. market — the brief is 24 days stale against a weekly cadence, the same gap this ceremony just found in its own sprint file

**Trigger.** `docs/market/briefs/` newest file is `2026-10-16.md`. Cadence
is weekly Friday (11:00 UTC per the host manifest); three Fridays have
passed with no new brief (10-23, 10-30, 11-06). No open PR exists from
this seat right now, so this is not a build-on-it case.

**Cost of skipping it today.** O1 is now graded `missed` on all three KRs
(2026-11-01 OKR check-in) going into whatever repositioning conversation
follows a missed launch date, and the positioning read feeding that
conversation is three weeks old.

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

### 2. frontend — PR #678 claims it is ready to merge and no longer is

**Trigger.** #678's own body says "This is the one to merge," written
2026-11-02. Checked live this run: `mergeStateStatus: DIRTY`,
`mergeable: CONFLICTING`, zero checks reported on the branch. Six days of
`main` traffic since the claim was written is the most likely cause; this
is a build-on-it dispatch, not a fresh-branch one, so it clears the
hard-stop rule by naming the open PR explicitly.

**Cost of skipping it today.** A depth-3 chain (#554→#559→#678) of visual
design work, already reviewed once, stays stuck and risks a fourth link
being stacked on top of a branch nobody has rebased.

**Dispatch.**

```bash
gh workflow run agent-frontend.yml \
  -f owner_instructions='Your own PR #678 (alexandria-frontend/2026-11-02-message)
says it is ready to merge but gh pr view now reports mergeable:
CONFLICTING and zero checks on the branch. Build on that branch: rebase
against current main, resolve the conflict, confirm checks run and pass,
and re-push. Do not open a fresh branch for this.'
```

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` is empty, not `true`.
