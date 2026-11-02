# Pending — what each seat currently owes

A table of the present, not a log. Each pass writes its own narrative to
`docs/sprints/pending/YYYY-MM-DD-HHMM-<trigger>.md`; only the ceremony run
rewrites this file, in full, from the newest evidence (`prompts/pm-agent.md`
§1d). The ceremony run before this one ran 2026-10-12; this is the first
rewrite under the new rule, so the file below starts from today's reading
rather than from a carried-forward table. The lines this file held before
today are unchanged in `docs/sprints/pending/archive-to-2026-10-26.md`
(5,458 lines, 2026-09-24 through 2026-10-24).

Last rebuilt: 2026-10-26, ~00:40 UTC, by the pm seat (ceremony run).

## Owed by a seat

| Seat | Owes | Since / directive | Dated |
|---|---|---|---|
| writer | Rebase PR #517 against main (CONFLICTING); it checked clear on the authority question | Tier B condition 5, `docs/standards/pm.md` §10 | 2026-10-26 |
| writer | Ask the ExO/HQ relay to confirm its manifest cap move from 150 to 225 (already asked once, unresolved); currently reading ~99% of the live 150 | `docs/agents/turn-caps.md`, rule 5 sweep | 2026-10-25 |
| skill | Rebase PR #466 against main (CONFLICTING); it checked clear on the authority question | Tier B condition 5 | 2026-10-26 |
| skill | The receipts retrofit #464 described still "waits for the owner" per its own text (unmeasured) | #464's own description, carried forward by #466 | 2026-10-24 |
| frontend | Ready PR #435 (still draft, 42+ hours old) and rebase it (CONFLICTING) | Ship-first + Tier B condition 5 | 2026-10-26 |
| exo | No alexandria-local blocker as of this reading; #529 (the Monday-slot fix) merged this pass. The slot move itself (HQ PR 467) and the re-fire widening are HQ-side and not this repo's to act on | exo's own PR #529 body | 2026-10-26 |
| engineer | Nothing blocking as of this reading; #530 is a live in-progress run and not actioned by this pass | — | 2026-10-26 |
| pm (me) | 21 of my own Tier B pull requests sit open and unmergeable by me (Tier B condition 1); one chain (#483) is 13 deep. Filed as `INC-2026-10-26-pm-own-tier-b-prs-piled-up-to-twenty-two-and-one-chain-reached-depth-thirteen` | `docs/standards/pm.md` §10 condition 1 | 2026-10-26 |

## Waiting on the owner, with the reason

| What | Why it is hers | Asked | Proceeds on silence? |
|---|---|---|---|
| PR #473 (re-vendor `docs/standards/pm.md`) | One hunk edits §21 itself; §21 is reserved regardless of content (`tools/check_authority.py --pr 473` → `reserved`) | 2026-10-26, this pass, board ask to owner | Yes, not money/account/secret — recommendation given: merge |
| The alexandria MCP workspace answers "disabled" instead of its challenge | Account-state restoration, not a code change (distribution's handoff, confirmed by this seat) | 2026-10-26, this pass, board ask to owner | Unclear; treating as hers until she says otherwise |
| The Polar merchant account does not exist | O1's checkout path has no account to point at; a decision with the owner's name on it per the OKR seat | Open since 2026-09-26, ~5 weeks, re-flagged in every OKR check-in since | No — opening an account |
| Who owns "the organization's weekly provider budget" | A newly-discovered unowned duty (`docs/agents/unowned-duties.md`, 2026-10-25 row); proposed owners are pm or the dormant finance seat | 2026-10-25, ExO | Not yet asked with a clock; naming it here so it is not lost |
| 22 of the PM's own open pull requests (see above) | Tier B condition 1: a PM's own Tier B PR waits for the owner or a chair | Carried across every pass since 2026-10-24 | N/A — not a silence item, a standing structural wait |

## Reconciled this pass (struck, not carried forward)

- PR #471 (re-vendor `docs/standards/lessons.md`) — merged 2026-10-24T18:21:50Z. Struck.
- PR #510 (plugin manifests point at the real site) — merged 2026-10-25T03:20:34Z; confirmed back to distribution on the board this pass. Struck.
- The nine-sibling PM pull request pileup of 2026-10-24 (`INC-2026-10-24-nine-of-the-pm-seats-own-prs-forked-the-same-anchor-and-none-contained-any-other`) — eight merged, #442 was the ninth; none of #440/#442/#444/#445/#447/#448/#450/#452/#454 remain open as of this reading. Struck, superseded by the fresh pileup logged above.
- The Tier C carve-out ambiguity (`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway` and its siblings) — `tools/check_authority.py` (merged 2026-10-24) now answers the question from the diff rather than the path, and this pass used it successfully on #473, #529, #517, #466 above. The tool is the fix; §10's prose carve-out is still unamended on `main`, which is exactly why #473 (which would have fixed that prose) is itself held as reserved. Not struck — carried as the "waiting on the owner" row for #473.
