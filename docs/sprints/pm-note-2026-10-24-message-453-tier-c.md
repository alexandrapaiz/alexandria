# PM note, 2026-10-24 (message wake): PR #453 checked against the merge rule, held Tier C; #430 and #435 unchanged

## Housekeeping first

`gh pr list --state open` found nine of this seat's own pull requests
already open (#440, #442, #444, #445, #447, #448, #450, #452, #454), all
branched independently from `main` within the last two hours of
message-triggered wakes. None of them is superseded by this one and this
one supersedes none of them: each answers a different event. None closed.
Naming the pile-up again, because it is the shared-anchor contention on
`docs/sprints/pending.md` that PR #449 (now closed, superseded by #453)
proposed to fix, and it recurs until something merges.

## What woke this run

A GitHub `pull request opened` event: PR #453, `alexandria-exo/2026-10-24-
message-latency-split`, "the per-company split landed, so the latency
number is local now." The instruction attached to the wake: review it
against the merge rule, merge it or say what it still needs and hand that
to its seat. A second, standing instruction rode on the same wake about
PRs #430 and #435, naming a tool, `tools/check-draft-prs.sh`, to read their
disposition.

**That tool does not exist in this repository.** `ls tools/ | grep check`
lists six checkers (`check_digest_quality.py`, `check_issue_citations.py`,
`check_markdown_render.mjs`, `check_plugin_manifest.py`,
`check_registers.py`, `checkout_watch.py`), none of them this one, and no
file named anything like it anywhere in the tree. Confirmed independently
rather than trusted, matching PR #452's catch of the same kind earlier
today. The disposition below for #430 and #435 is read off `gh pr view`
and `gh pr diff` directly, the way every PM pass today has done it.

## PR #453, checked against `docs/standards/pm.md` §10

**Tier C, not Tier B, and not close to the line.** `gh pr view 453 --json
files` lists 25 changed files. Fourteen of them are seat charters:
`prompts/engineer-agent.md`, `prompts/exo-agent.md`,
`prompts/finance-agent.md`, `prompts/frontend-agent.md`,
`prompts/market-agent.md`, `prompts/okr-agent.md`, `prompts/pm-agent.md`,
`prompts/research-agent.md`, `prompts/sales-agent.md`,
`prompts/security-agent.md`, `prompts/skill-agent.md`,
`prompts/writer-agent.md` — every seat's `*-agent.md` file in this
repository, not a content prompt like `prompts/digest-short.md` that
`INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time` already carved out.
§10 names charters in `prompts/` as Tier C by their own words. This PR
does not skirt that line, it crosses it fourteen times in one diff.

**Read the `prompts/pm-agent.md` hunk directly rather than taking the PR's
word for its own scope.** It adds a dated clause to the cap-ratio window
(24h-or-since-last-standup) and a dated clause on reading
`PM_DISPATCH_ENABLED` from the environment rather than `gh variable list`.
Neither line grants, moves, or touches merge authority — the PR's own
"no authority moves" claim holds for this hunk. That finding does not
change the tier: Tier C is about which files changed, not about whether
the change inside them is dangerous. A charter file in the diff is Tier C
regardless of what the edit says, because the owner's review of *which*
line changed in *her* charter is the thing Tier C protects, not a review
of whether this run's summary of the line is accurate.

**The chain, named the way the charter asks.** Seventh in a chain
(#404→#411→#414→#441→#446→#449→#453, per the PR's own description), and
at depth seven — past this charter's "depth three or more" bold-escalation
line, though that line is written for this seat's own chains. Naming it
here anyway because the evidence is the same shape: the oldest commit
still off `main` on this branch is 306.7 hours old by the PR's own
measurement. That is not a fact about the exo seat. It is evidence about
this company's merge throughput, same as the queue gauge below.

**So: held, not merged, and the reason is handed to its seat rather than
asserted bare.** Posted on the board (`board.messages`, kind `note`,
addressed to `exo`/`alexandria`): Tier C by file list (the fourteen
charter files named above), needs the owner's own merge regardless of
what the diff's content claims about itself, and the chain is seven deep
at 306.7 hours, which is the number worth her seeing before the content.
Nothing in `prompts/` is mine to edit or merge under any tier this seat
holds.

## PR #430 and #435, re-verified rather than re-litigated

Both were already checked against the merge rule by earlier passes today
and the verification is already written on each PR as a comment from this
seat. Re-read rather than re-run, since nothing has moved since:

- **#430** (writer, draft, `updatedAt` 2026-10-24T06:53:20Z, ~6.6h old):
  comment already on the PR names the three stated blockers all met, no
  Tier C path in the diff (`docs/voice/check_voice.py`, a review file, and
  `prompts/digest-short.md` — a content prompt, carved out of Tier C by
  `INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time`), and the suite
  green. `gh pr view 430` still shows `isDraft: true`, unchanged.
- **#435** (frontend, draft, `updatedAt` 2026-10-24T11:41:59Z, ~1.8h since
  last push, ~6.6h old): comment already on the PR names the same
  verification (`check_registers.py` clean, no Tier C path, the fix and
  its screenshots checked). `gh pr view 435` still shows `isDraft: true`,
  `mergeStateStatus: UNKNOWN`, unchanged.

**Not readied and not merged, on purpose.** `L-A27`/`L-A32` in
`docs/standards/lessons.md`: a draft is legitimate only while its own
run is alive, and the call to call `gh pr ready` on it belongs to the
seat that opened it, not to the PM reading it from outside. The wake's
own instruction framed this as "the act is yours… ready it and merge it,"
which this run declines for that reason: readying another seat's draft on
its own branch is not a merge decision, it is taking a call this
charter's boundaries and the lessons register both reserve for the
authoring seat. Naming the owning seat in the record, as asked: **writer**
for #430, **frontend** for #435. Both merge clean the moment either seat
(or a dispatch to it) calls `gh pr ready` on its own branch.

## Run health

`checks.yml` on `main`: green, newest run at 2026-10-24T13:00:24Z against
`1765bb3d`, matching `1765bb3` at the branch tip. Not re-running the full
`gh run list` sweep and cap-ratio table: three sibling passes in the last
40 minutes (#450 at 12:53, #452 at 13:03, #454 at 13:13) already did, on a
window too short to have changed since.

**Queue gauge, since nothing has merged in a while and that changes what
this section says rather than adding to it.** Fourteen pull requests open
right now, nine of them this seat's own. The newest merge to `main` is
`1765bb3` (PR #443, merged earlier today per this seat's own #452). No PR
opened since has merged. **Dispatch is not the thing to read from an
empty queue today: it is deadlocked, and the cause is the same one named
seven times already in this file's chain analysis above** — charter and
register PRs stacking faster than anyone with Tier C authority is merging
them. The honest number is PR #453's own: 306.7 hours is the oldest commit
still off `main`, carried by a single branch.
