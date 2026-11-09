# Pending tracker — state, not a log

What each seat currently owes, what sits in open pull requests awaiting
merge, and what waits on an owner-only action. One writer: the ceremony run
(prompts/pm-agent.md §1d). A later ceremony overwrites a line here instead
of prepending beside it. Every other pass writes its own file instead, at
`docs/sprints/pending/YYYY-MM-DD-HHMM-<trigger>.md`.

**This file was reset 2026-11-09** (first ceremony run since the
2026-10-24 single-writer split, four Mondays late — see the retro in
`docs/sprints/sprint-2026-10-12.md`). Everything this file held before today,
5,458 lines back to 2026-09-24, moved unchanged to
[`docs/sprints/pending/archive-to-2026-11-09.md`](pending/archive-to-2026-11-09.md)
rather than being triaged line by line. The table below is read fresh from
today's state, not carried forward from the archive, so an item the archive
names and this table does not is either resolved or not yet re-confirmed —
check the archive before assuming either.

## Owner-only (money, a secret, an account, or widened authority)

- **Polar checkout secrets unset.** `POLAR_CHECKOUT_TRIAL`,
  `POLAR_CHECKOUT_MONTHLY`, `POLAR_CHECKOUT_LIFETIME` are absent from the
  site's environment, unset since 2026-10-14 (26 days). Code is complete and
  merged (`site/lib/polar.js`, `site/lib/polar-core.js`,
  `site/app/api/polar-webhook/route.js`, all 2026-10-13). Blocks O1 KR1/KR2
  (`docs/okrs/okrs-2026-Q4.md`). First step: the owner creates the Polar
  account and pastes the three secrets; nothing else is unbuilt.
- **PR-merge-scoped token for the autonomous reviewer panel.**
  `tools/panel_merge.py` (711 lines, `docs/product/reviewer-panel.md`) names
  this as one of four blockers to O3 KR1's first autonomous merge,
  2026-11-15 target. `PANEL_MERGE_TOKEN` does not exist; the code refuses to
  substitute `GH_TOKEN`. Unchanged since September.
- **A read credential for the corpus database.** `NEON_RO_URL` and
  `DATABASE_URL` are both absent on every seat host checked this week
  (research PR #854, skill PR #850, `tools/loop_close.py` per the 2026-11-01
  OKR check-in). Blocks O3 KR2's loop-closing write (`promotions.live_at`)
  and the chair's own RLVR corpus-presence ask, which "waits on board card
  `6a5e4ad5`" per PR #854.
- **The own-store task board's OKR home.** Flagged as an orphan objective
  in five consecutive OKR check-ins (2026-09-26, 09-30, 10-01, 10-18,
  11-01) with zero ruling. `tools/board.py` has been live production
  infrastructure since 2026-09-27; none of O1/O2/O3 names it. The OKR
  agent's own recommendation: a new KR under O3 rather than a fourth
  objective. Needs the owner's word before a sixth flag in December.
- **Hosting/vendor cost figure for O1 KR2.** No Claude-subscription or
  vendor-cost number has been confirmed on record at any point this
  quarter, per every OKR check-in since 2026-09-24.

## Blocked on a merge only the owner or a chair can make

- **PR #483, this seat's own, depth-13 supersession chain, open since
  2026-10-24 (16 days).** `#...→#480→#483` per the title; not superseded
  further (`gh pr list --state all` finds no PR naming "supersedes #483").
  **This seat is blocked on merging it**, per the charter's own depth-3-plus
  rule, because the PM seat never merges its own pull request regardless of
  depth. Needs the owner or a chair to review and merge or close.
- **PR #860 (security), depth-4 supersession chain** (`#834→#839→#848→#852→
  #860`), self-reported by that seat as "blocked on merges." Draft, run was
  live as of this check; re-confirm before acting.
- **PR #854 (research) and the now-merged #850 (skill) both edited
  `docs/research/reading-queue.md` at the same original lines (3610-3612).**
  #850 merged first (this run, `0d873f79`); #854 read `mergeable: UNKNOWN`
  immediately after and will need a rebase. Not this seat's file to own;
  named so the next pass checks before merging #854 as though it were
  still clean.

## §22 asks live on the board (48-hour silence-default clock)

- **PR #851 (charter propagation to all twelve `prompts/*-agent.md`
  files).** Posted by this seat's run #856 at 2026-11-09T04:10:55Z,
  deadline 2026-11-11T04:10:55Z, this seat named as the applier on silence.
  **Needs re-checking before the clock is trusted**: #851 shows as `MERGED`
  on GitHub, but its content was reverted out of `main` by the tier-sweep
  correction (`8ebb17c4`, this morning, incident filed) alongside
  #841/#825/#833, which were merged under the wrong tier and corrected. The
  revert's own commit message does not say whether #851 was wrongly tiered
  on the same grounds or caught in the same sweep for an unrelated reason.
  The next pass should read that incident before letting the 48-hour clock
  apply itself to a PR that is not currently reflected in `main` either way.

## What ships without waiting on her

Everything else open today is ordinary review-and-merge volume (69-70 open
pull requests as of this run) rather than a standing ask. See
`gh pr list --state open` and this run's own PR description for the queue
gauge; this table only carries items with a genuine, named block.
