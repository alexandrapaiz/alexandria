# Pending — what each seat currently owes

A table of the present, not a log. Each pass writes its own narrative to
`docs/sprints/pending/YYYY-MM-DD-HHMM-<trigger>.md`; only the ceremony run
rewrites this file, in full, from the newest evidence (`prompts/pm-agent.md`
§1d). The prior rebuild was 2026-10-26, ~00:40 UTC, inside PR #531, which
stayed open 7 days (a PM-authored Tier B PR cannot be merged by any PM run)
and was superseded this ceremony by #683. Everything below is read live
against `main` and the open-PR list at the time of this rebuild, not carried
from #531's copy.

Last rebuilt: 2026-11-02, ~01:30 UTC, by the pm seat (ceremony run, PR #683).

## Owed by a seat

| Seat | Owes | Since / directive | Dated |
|---|---|---|---|
| frontend | Ready PR #678 (draft, clean, supersedes #559 depth 3) and it merges under Tier B the moment it is | Ship-first + Tier B | 2026-11-02 |
| engineer | PR #659 is open, draft, `CONFLICTING`/`DIRTY`, body still "work in progress," names closed-not-merged #649 as its predecessor — rebase and verify #649's work is actually contained before readying | Ship-first + Tier B condition 5 | 2026-11-01 |
| engineer | This sprint's items 1-5 (sprint-2026-11-02.md) all depend on the Modal workspace, now restored; item 4 depends on reading #542's own unbuilt half rather than re-describing its three owner-only blockers | sprint-2026-11-02.md | 2026-11-02 |
| skill | PR #675 is open, not draft, `CONFLICTING`/`DIRTY` — rebase against current `main` | Tier B condition 5 | 2026-11-02 |
| pm (me) | 25 of my own Tier B pull requests sit open and unmergeable by me (Tier B condition 1), oldest #483 at depth 13, now 8.3 days old. Unchanged in kind since 2026-10-24; the count has grown (9 -> 21 -> 25) across three ceremonies | `docs/standards/pm.md` §10 condition 1 | 2026-11-02 |

## Waiting on the owner, with the reason

| What | Why it is hers | Asked | Proceeds on silence? |
|---|---|---|---|
| The Polar merchant account does not exist | O1's checkout path has no account to point at; opening an account is an owner-only act | Open since 2026-09-26, ~5.5 weeks, re-flagged every OKR check-in since | No — opening an account |
| Who owns "the organization's weekly provider budget" | A standing unowned duty (`docs/agents/unowned-duties.md`, row found 2026-10-25); proposed owners are pm or the dormant finance seat | 2026-10-25, ExO; carried every ceremony since with no ruling | Not yet asked with a clock |
| 636 ledger entries are `proposed`, 478 of them (75%) two or more weeks old with no verdict, up from 552/387 at the last ceremony | A status decision the charter gives to the owner alone; too many to list individually, and this is itself the finding carried from #531 | First raised 2026-10-26 (#531), unresolved, growing | Not asked with a clock — this needs a policy ruling, not a 48-hour default |
| Two writer copy questions, each posted with a 48-hour clock | §22: a reservation proceeds on her silence after 48 hours unless money/account/secret/authority | 2026-11-02T00:32Z, per PR #673's report | Yes — 2026-11-04T00:32Z |
| Reviewer-panel's three owner-only blockers (ADR-12 whitelist refusing every real proposal; the same whitelist over-admitting `prompts/*.md`; `PANEL_MERGE_TOKEN` and the commit-status write grant missing) | Named in `docs/product/reviewer-panel.md`'s own numbered list; none is engineer-buildable | First named 2026-10-26 (#542) | Unclear — not re-asked with a clock this pass, carried as-is |

## Reconciled this pass (struck, not carried forward)

- The MCP workspace answering "disabled" — struck. `tools/delivery_health.py`
  this ceremony reads `mcp: ok` and `compute: ok`; the Modal workspace
  restoration also closes the press/backfill half of this ask, though the
  press itself still shows a missed `2026-W43` issue (new row above, under
  engineer).
- PR #473 (re-vendor `docs/standards/pm.md`, held on a §21 hunk) — merged
  2026-11-02T00:something UTC per PR #673's report ("five Tier B merges
  unstall the queue"). Struck.
- Writer's manifest-cap ask (150 -> 225) — confirmed live this ceremony by
  reading `runtime/agents/alexandria/writer/agent.toml` directly:
  `max_turns = 225`. Struck.
- PR #517 (writer, rebase), PR #466 (skill, rebase), PR #435 (frontend,
  ready+rebase), PR #529 (exo, Monday-slot fix), PR #530 (engineer,
  in-progress run) — all merged or closed as superseded as of this
  reading (`gh pr view` on each, live). Struck as a batch; none remains
  open under these numbers.
- exo: "no blocker as of 2026-10-26" — struck as stale phrasing now that a
  full week has passed; exo's current open PR (#680, draft, clean) is not
  blocked on anything found this pass.
- The nine-sibling PM pull-request pileup and the Tier C carve-out
  ambiguity, both already struck or superseded before the 2026-10-26
  rebuild — not restated here; see `docs/sprints/pending/archive-to-2026-10-26.md`
  if the detail is needed.
