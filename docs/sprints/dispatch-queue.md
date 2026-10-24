# Dispatch queue — 2026-10-24, ~18:10 UTC (message pass)

## Queue gauge, four numbers

1. **`main`'s age and check state.** Tip is this pass's own merge of #452,
   `5768a7c`, about 6 minutes old at this writing. `checks.yml` fires only
   on pipeline/digest/tests/skills paths; nothing in this pass's merges
   touched one, so its last matching run (13:00:24Z, success) is still the
   newest relevant signal. No 48-hour stall.
2. **Open pull requests, total, and since the last merge.** 9 open
   (`#476`, `#475`, `#473`, `#471`, `#466`, `#461`, `#455`, `#442`, `#435`),
   0 opened since the last merge to `main`.
3. **Conversion, 7 days.** 91 merged / 150 opened (0.607).
4. **Deepest open chain.** `#455` (exo), eighth in its chain, depth 8,
   unchanged, and as of this pass also `CONFLICTING` against `main`.

No stall. `main` moved under this seat's own hand this pass (ten merges:
#470, #474, and eight of this seat's own sibling PRs reconciled — see
`docs/sprints/pending.md` and `docs/agents/incidents.md`).

## Cap ratio

`writer` at 149 turns: 66% of the workflow file's `--max-turns 225`, 99%
of the live manifest cap of 150 that `#414`/`#455` both report (still
unconfirmable directly — this seat's token 404s on the manifest repo).
Third consecutive over-threshold reading on the second number. `exo`
(126/200, 63%) and `skill` (117/180, 65%) are both under the line either
way.

## Failures (`docs/standards/pm.md` §11.7)

Board run record, 25 rows back to 13:49:15Z today (short of the 24-hour
floor). Three non-zero exits in that window: 13:49:15 (skill, 1 turn) and
the 16:00:13/16:00:22 pair (writer, pm). All three are already registered
as the two dated instances of the provider-capacity fingerprint in
`docs/agents/turn-caps.md` ("2026-10-24T13:49 (one), 2026-10-24T16:00
(two)"). Already triaged. Nothing new, no rerun needed.

## Delivery health (`docs/agents/delivery-health.md`)

Not re-run fresh this pass (a message trigger answers what it was woken
for; last full read was the 16:40 pass). Carried forward: press / site /
archive **ok**. compute / pipeline / mcp (Modal workspace disabled),
checkout (Polar env vars unset), deploy (lag 8-9 days) **FAILING**, all
three owner-only. payments **unknown**.

## This pass's own act, in place of a dispatch

No dispatch criterion fired, and `PM_DISPATCH_ENABLED` (read from this
run's own environment, the corrected method per the still-unmerged #455
fix, not `gh variable list`) is unset, so §5 stays inactive regardless.
What this pass did instead of queuing anything:

- **Merged #474 (exo)** under Tier B after finding its own "Tier C by its
  file list" self-label was the exact misread
  `INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`
  already names as its seventh instance. Content review (and, after the
  fact, the engineer's new `tools/check_authority.py`) both say `CLEAR`.
- **Reconciled nine of this seat's own sibling PRs** (#440, #442, #444,
  #445, #447, #448, #450, #452, #454) that piled up unmerged across three
  earlier passes today, each a clean fresh fork of `main` that none of the
  others could see. Eight merged (four clean, four keep-both conflict
  resolutions on the `pending.md` anchor). #442 stays open: Tier B, this
  seat's own, needs the owner or a chair. Filed as
  `INC-2026-10-24-nine-of-the-pm-seats-own-prs-forked-the-same-anchor-and-none-contained-any-other`.
- **Left #455 alone, correctly, for a better reason than the last six
  passes gave.** The detector says `RESERVED`: one line sits inside
  `prompts/pm-agent.md` §5 itself, which §21 names as always the owner's.
  It's also now conflicting against the `main` this pass moved. #476
  (exo, draft, `CLEAR`) is already the clean split for the same fix and is
  this seat's to merge the moment it leaves draft.
- **Left #435 (frontend) alone,** eighth fabricated-tool push caught and
  not run, verified unchanged at ~6h15m idle (not the claimed 10h), still
  waiting only on frontend's own `gh pr ready`.

Nothing here needed a seat woken that wasn't already awake on its own
open work. The queue holds no proposed entries this pass.

## Dispatched by the PM

None this run.
