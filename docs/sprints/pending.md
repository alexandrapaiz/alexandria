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

- **Urgent: is the org's monthly Claude spend cap still in force?**
  `INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days`
  (engineer, `docs/agents/incidents/inbox/`): the portfolio ran dark from
  2026-11-03T00:20Z to 2026-11-08T23:02Z because the org hit its monthly
  spend cap, misread by every classifier as the ordinary weekly pool
  resetting. Zero pull requests opened anywhere in this repository for
  six days. The incident's own last line: "whether the monthly cap is
  still in force cannot be read from the logs... it is still set and will
  bite again before the month ends" unless raised at
  `claude.ai/admin-settings/usage`. This is not a background fact; an
  unanswered version of it is a second six-day outage waiting to recur
  before November ends.
- **No seat holds a Modal token.** `MODAL_TOKEN_ID`/`MODAL_TOKEN_SECRET`
  do not exist on any seat host (confirmed again this run; `command -v
  modal` finds nothing here either, and `docs/agents/incidents.md:5141`
  already names "a `modal deploy` step no seat's token can perform").
  Blocks three named board cards — Deploy (`2170a62f`), Press W41
  (`92ab912d`), and by extension the `2026-W43` backfill — all
  independently confirmed this week (engineer PR #803) and again this
  run (`tools/delivery_health.py`: `deploy` and `archive` both
  `FAILING`). Workspace/account reachability ("compute: ok") is a
  separate fact from having a token to authenticate with; the first does
  not imply the second, which cost sprint-2026-11-02 two of its five
  items before the outage above cost it the rest.
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

- **PR #683, this seat's own, open since 2026-11-02 (7 days), and the
  reason this ceremony cost more turns than planned.** It is a full,
  unmerged Monday-ceremony attempt (retro for `sprint-2026-10-12.md`, all
  of `sprint-2026-10-26.md` and `sprint-2026-11-02.md`, its own
  org-chart/playbook/pending/dispatch-queue edits) that this run did not
  discover until late, because this seat's most recent OWN pull request
  (#856) touched none of these files and the charter's open-PR check
  anchors on "your own last run," not "any open PR from your seat." This
  run's PR carries forward #683's unique content (the two sprint files,
  with retros added) and corrects one factual error #683's version of the
  `sprint-2026-10-12.md` retro had already fixed that this run's first
  draft re-introduced (see that file's own correction note). This run
  did NOT merge #683's conflicting edits to `org-chart.md`, `playbook.md`,
  `dispatch-queue.md`, or `pending.md`, because #683 branched from
  2026-11-02 main and `docs/ideas.md` alone has grown by several thousand
  lines since, making a clean merge of those four files into a 7-day-old
  branch riskier than recommending closure. **Recommend: close #683 as
  superseded by this PR** (its unique content is carried forward; nothing
  in it is lost) rather than merging it. The owner or a chair should
  confirm before it closes, since this seat's own read of "superseded" is
  exactly the judgment call incident class this charter asks a seat to
  flag rather than act on unilaterally when it touches this many files.
- **PR #483, this seat's own, depth-13 supersession chain, open since
  2026-10-24 (16 days).** `#...→#480→#483` per the title; not superseded
  further (`gh pr list --state all` finds no PR naming "supersedes #483").
  **This seat is blocked on merging it**, per the charter's own depth-3-plus
  rule, because the PM seat never merges its own pull request regardless of
  depth. Needs the owner or a chair to review and merge or close.
- **PR #860 (security), depth-4 supersession chain** (`#834→#839→#848→#852→
  #860`), self-reported by that seat as "blocked on merges." Draft, run was
  live as of this check; re-confirm before acting.
- **Resolved since this morning: #854 (research) and #850 (skill), both
  flagged as a `reading-queue.md` collision risk, are both now `MERGED`**
  (re-checked 11:16Z via `gh pr view`). No rebase was needed; the file
  carries no conflict markers. Struck rather than carried forward.
- **PR #678 (frontend, depth-3 chain, #554→#559→#678) says "this is the
  one to merge" in its own body, but is not.** Checked live again this run
  (11:16Z, after waiting out a transient `mergeStateStatus: UNKNOWN`):
  `mergeStateStatus: DIRTY`, `mergeable: CONFLICTING`. The claim was true
  when written (2026-11-02) and is still not true a week later. Proposed in
  this run's dispatch queue: frontend rebases and re-pushes rather than
  this seat guessing at the resolution of a visual design PR's conflict.

## §22 asks live on the board (48-hour silence-default clock)

- **PR #851 (charter propagation to all twelve `prompts/*-agent.md`
  files).** Posted by this seat's run #856 at 2026-11-09T04:10:55Z,
  deadline 2026-11-11T04:10:55Z, this seat named as the applier on silence.
  **Checked this run, resolved rather than stuck.** #851 shows `MERGED` on
  GitHub but its content was reverted out of `main` at 04:35:34Z
  (`8ebb17c4`) alongside #841/#825/#833: a later run of this same seat had
  merged all four on a tier-checking tool's verdict without first reading
  its own board inbox, which already held its immediately-prior run's
  considered decision to hold exactly these four for the owner. The revert
  is logged **CLOSED** in `docs/agents/incidents/inbox/INC-2026-11-09-the-pm-merged-over-its-own-prior-runs-posted-hold-because-it-ran-a-tool-before-it-read-the-inbox.md`,
  which states plainly: "The section 22 ask #856 posted is unaffected and
  still governs." So the clock stands as originally posted: the owner's
  word, or the 48-hour silence default (2026-11-11T04:10:55Z) naming this
  seat as the applier, on content not currently in `main`.

## What ships without waiting on her

Everything else open today is ordinary review-and-merge volume (73 open
pull requests as of 11:16Z, re-read this ceremony run; was 69-70 six and a
half hours earlier) rather than a standing ask. See `gh pr list --state
open` and this run's own PR description for the queue gauge; this table
only carries items with a genuine, named block.
