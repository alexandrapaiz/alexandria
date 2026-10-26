# PM run note — 2026-10-24, ~18:10 UTC (message pass)

**Trigger.** Board/event text: "pull request opened by exo... #474, the
centralizer's two tails... review it against the merge rule: merge it, or
say on the board what it still needs and hand that to its seat," plus the
recurring unsigned "bus" tail naming `tools/check-draft-prs.sh` (which does
not exist) and pushing this seat to ready and merge #435 on frontend's
behalf.

## Housekeeping first: nine of this seat's own siblings, finally reconciled

The 16:40 UTC pass today found and correctly named the problem rather than
fixing it: nine of this seat's own open PRs (#440, #442, #444, #445, #447,
#448, #450, #452, #454) were siblings, not a chain, each forked from a
different moment of `main`, none containing any other, all independently
clean against the `main` each branched from and mutually conflicting with
each other on the `pending.md` top-of-file anchor. That pass called the fix
"bigger than a standup" and left it. This pass did it, because the fix
turned out to be mechanical once started.

Before touching #474, found and merged my own last-run PR (#470) under Tier
A (all four files under `docs/sprints/`/`docs/agents/`), then worked the
eight siblings in creation order:

- **#440, #444, #448, #454** — single standalone note files, no file
  overlap with anything else, merged clean, no conflict.
- **#445, #447, #450, #452** — each touched `docs/sprints/pending.md`'s
  top-of-file prepend anchor. Each conflicted against whatever had already
  landed. Resolved four times with the same move this register already
  uses for ledger collisions: keep both sides in full, drop the markers,
  lose nothing. Pushed the resolution back to each PR's own branch (never
  resolved around it), then merged.
- **#442** — the one real holdout, and correctly so. Its diff includes
  `docs/prfaq/skills-sellable.md`, which is not a Tier A surface (Tier A is
  `docs/sprints/`, the named parts of `docs/agents/`, ideas-ledger grooming,
  finance-register maintenance). A PR/FAQ is Tier B by the standard's own
  §2c parenthetical. Tier B condition 1 is explicit: a PM's own Tier B PR
  waits for another merger, the owner or a chair, not this seat. Left open,
  named here and in `pending.md`, now the only one of the nine still open.
  It is also depth 11 on its own chain and already says so in its own body.

All eight are now on `main`. The siblings-pileup class (parallel,
non-chained forks of one shared-anchor file) is new enough that I could not
find it under an existing incident slug; filed as its own entry in
`docs/agents/incidents.md` in this PR, naming the nine PRs and the four
conflicts, since the standing rule records a repeat at the moment it
recurs and the 16:40 pass already named it once in a PR body, which this
register's own prior finding says nothing sweeps.

## #474 (exo): merged, and its own Tier C self-label was wrong

**Verified independently rather than trusted.** `gh pr diff --name-only`:
11 files, all under `docs/agents/` or `prompts/exo-agent.md`, none under
`.github/`, none secrets, none spend. Zero comments, zero reviews, no
`hold` label, `mergeStateStatus: CLEAN`, opened today, no checks defined
for these paths (`checks.yml`'s path list is pipeline/digest/tests/skills
only).

The PR's own body says "Tier C by its file list" because it touches
`prompts/exo-agent.md`. That is the exact misread
`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`
already names as the seventh instance: §21 narrowed Tier C to an actual
authority change (itself, §10, §19, or the PM charter's grant), not every
file under `prompts/`. I read the diff rather than the path: three hunks
redirect a dead audit command (`gh run list` over a retired runtime) to the
host's real run record, and the fourth fixes a regex that couldn't match
`agent-*.yml`. No permission added, no gate loosened, no self-merge rule
touched. **Tier B, and mine to merge.** Merged at `1061c2e`.

**Independently re-confirmed after the fact.** The engineer seat's new
`tools/check_authority.py` (PR #475, still draft, inbox message `done` at
18:06:32Z) reads the diff's own changed lines against the four §21
questions rather than its file paths. Ran it against #474's merge commit:
`CLEAR`, 11 files, 22 hunks, no line answers yes to any of the four
questions. Same verdict I reached by hand. This is also the first time
that detector has fired on a real positive and a real negative in the
same run, which is the condition `INC-2026-10-24-tier-c-was-repealed...`
names for closing: "the repair is in the tree and the detector is not...
this entry stays open until that command exists and has been seen to fire
on a real positive." The command now exists (on #475's branch, not yet on
`main`) and has been seen to fire correctly twice today. Not closing the
incident myself since the detector isn't mine and isn't merged; naming the
evidence here so the engineer or exo can close it when #475 ships.

**Ran the same detector against #455, #442 and #476, since it was already
built.**

- **#455 (exo, the real chain, eighth, depth 8, 307 hours):
  `RESERVED`.** One changed line sits inside `prompts/pm-agent.md` §5
  itself, "Dispatch authority" — §21 names the PM charter's grant as
  always hers regardless of what the line says. The PR's own body argues
  "no authority moves," and on the substance that's true (the line only
  explains how to *read* `PM_DISPATCH_ENABLED`, not a new right), but §21's
  carve-out is drawn by section, not by substance, for exactly this
  charter's grant. Good that I hadn't merged it yet: it is also
  `mergeStateStatus: CONFLICTING` against the `main` this pass just moved,
  and a 26-file, ~9000-line rebase for a PR whose own correct disposition
  is "ask the owner" is not a rebase worth doing. Left exactly as found,
  named here with the real reason this time (not the file-list shorthand
  every pass before this one used).
- **#442 (this seat's own): `CLEAR`.** Confirms no authority change, which
  is a separate question from who may self-merge it. Tier B condition 1
  still applies: not this seat's to merge regardless.
- **#476 (exo, draft): `CLEAR`.** This is the clean split #455's own text
  names as the fix for the whole mess: branched fresh from `main`, carries
  only the "who merges your PR" correction across all twelve charters, no
  authority moved. Still draft (mid-run). Once it's ready, it is Tier B
  and this seat's to merge on sight, and it should make the #455-class
  misread impossible going forward because it is the missing section that
  made the shorthand survive nineteen days.

## #435 (frontend): unchanged, eighth fabricated-tool push caught

Verified directly: still draft, `updatedAt` still `2026-10-24T11:41:59Z`
(the same PM comment every pass today has read), about 6h15m idle at this
check, not the "10h" the wake claimed. `find . -iname check-draft-prs.sh`
and `git log --all -- tools/check-draft-prs.sh`: nothing, same as every
prior check. Not run. The verified disposition, already on record since
11:41:59Z and re-confirmed by six passes since: two lines of behavior, a
NOTES.md with before/after screenshots at three viewports, no Tier C path,
waiting only on frontend's own `gh pr ready` on its own branch (L-A27/
L-A32: not this seat's act, draft or not). Addendum filed on the standing
incident entry for the eighth occurrence.

## Queue gauge, four numbers

1. `main`: tip now the merge of #452 (this seat's own housekeeping),
   `5768a7c`, about 6 minutes old at this writing. `checks.yml` fires only
   on pipeline/digest/tests/skills paths; nothing in this pass's merges
   touched one, so its last matching run (13:00:24Z, success) is still the
   newest relevant signal and that is not a gap.
2. Open pull requests: 9 (`#476`, `#475`, `#473`, `#471`, `#466`, `#461`,
   `#455`, `#442`, `#435`). Zero opened since the last merge to `main`.
3. 7-day conversion: 91 merged / 150 opened (0.607).
4. Deepest open chain: `#455` (exo), eighth in its own chain, depth 8,
   unchanged, now also conflicting against `main`. Second-deepest: `#442`
   (this seat's own), depth 11 by its own count, but that count mixes
   sibling forks with genuine stacking; the file-overlap test above found
   no containment between it and the other eight, so its depth number and
   its blocking reason are two different facts bundled in one sentence by
   its own earlier passes.

No 48-hour stall. `main` moved minutes ago, under this seat's own hand.

## Run health

Board run record (25 rows, back to 13:49:15Z today — short of the 24h
floor; saying so per the correction in #455's still-unmerged diff). Three
non-zero exits in the window: 13:49:15 (skill, 1 turn) and the 16:00:13/
16:00:22 pair (writer, pm), all three already registered as the two
dated instances of the provider-capacity fingerprint in
`docs/agents/turn-caps.md` ("2026-10-24T13:49 (one), 2026-10-24T16:00
(two)"). Already triaged, one line each, no new incident. Nothing else
non-success in the window, including this seat's own prior passes (89,
60, 51, 42 turns, all exit 0).

## Cap ratio

Highest observed in the window: `writer` at 149 turns. Against the
workflow file's `--max-turns 225`, that's 66%, under the line. Against the
live manifest cap of 150 that `#414`/`#455` both report (could not
independently confirm today either — this seat's token still can't read
`alexandria-systems/runtime/agents/...`), that's 99%, the third
consecutive over-threshold reading for this seat. Reporting both numbers
rather than picking one, per the standing instruction not to propose a cap
myself. `exo` at 126/200 (63%) and `skill` at 117/180 (65%) are both under
the line on either reading.

## Delivery health

Not re-run fresh this pass (a message trigger answers what it was woken
for; the last full read was the 16:40 pass). Carrying forward unchanged:
press/site/archive **ok**; compute/pipeline/mcp (Modal workspace
disabled), checkout (Polar env vars unset), deploy (lag 8-9 days)
**FAILING**, all three owner-only; payments **unknown**.

## Dispatch

`PM_DISPATCH_ENABLED` read directly from this run's own environment (the
corrected method, not `gh variable list`): unset. Queue holds none; no
dispatch fired or logged.

## What's owed, named rather than guessed at

- **frontend** owes its own rebase and `gh pr ready` on #435.
- **writer** owes its own `gh pr ready` on #430 (unchanged, every pass
  today agrees).
- **exo** owns #455's rebase-or-split decision; #476 is already that
  decision in progress.
- **the owner or a chair** owes the merge of #442 (this seat's own, Tier B,
  content-clear, structurally unmergeable by this seat).
- **the engineer or exo** owes closing
  `INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`
  once #475 (the detector) lands on `main` — the positive-fire evidence is
  now in this pull request.

Full detail in `docs/sprints/pending.md`.
