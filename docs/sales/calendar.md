# Campaign calendar — runway to launch (2026-10-13)

Maintained by the sales agent (prompts/sales-agent.md, ADR-24). One law
governs every date below: **the agent prepares, the owner sends.**
Nothing on this calendar fires itself — every row is a drafted asset
in docs/sales/, ready for the owner's hand on the date shown, and every
date is a suggestion she can move.

Keyed to two fixed points: the weekly digest send (Mondays, currently
16:30 UTC, comped-friends list only) and the owner's launch date,
**Tuesday 2026-10-13** (docs/allhands/2026-09-17.md, OKR O1 KR1).

## Blocking dependencies outside sales' lane

Read this before sending anything below — it determines what's honest
to say on which date. Source: docs/market/report-2026-09.md's
hands-on walkthrough, 2026-09-18, plus a repo check the same day.

1. **No email capture exists on the site today.** Both homepage CTAs
   dead-end (Subscribe → pricing marked "Coming soon," no signup form
   anywhere; Read an issue → an archive that renders empty). Nothing
   in this calendar that asks a stranger to "sign up" can go out
   before this is fixed. Pre-launch posts below route to the public
   GitHub repo instead, which is real and already a receipt.
2. **Two skills in gold, not a library** (updated 2026-09-18:
   `harness-engineering` and `self-improving-post-training-loops`; this
   line said "one" when first written and that is no longer true). Every
   draft names the two directly — never "the skill library" and never a
   projected count. Fix this by revising copy, not by waiting; O2 KR1's
   twelve-skill target is a Q4 arc, not a launch-day fact. Note for the
   skill seat: `self-improving-post-training-loops` has an empty
   `validated:` field, and the dated A/B line is the single best sales
   sentence we own.
3. **The homepage's "papers ingested this week" counter is
   hardcoded**, per the market report. If it still is on launch day,
   no draft below should point to it as a live metric — this audience
   reads source and will notice.
4. **Free list is comped friends only** (roadmap.md, sprint 1). The
   launch email's addressee count is small and known, not "our
   subscribers" phrased to sound bigger than it is.

Sales cannot fix any of these; they belong to engineer/frontend/PM.
Flagging them here so the launch-day send doesn't repeat a claim this
run already knows is false. [SITE_URL] and [SIGNUP_LINK] placeholders
below get filled in only once real.

## Pre-launch (2026-09-18 → 2026-10-12)

No asks, no signup links — just proof-of-work, because that's the one
channel that's actually live: the public repo itself.

| Date | Channel | Asset | Purpose |
|---|---|---|---|
| Week of 09-22 | X | `launch/pre-launch-teasers.md` #1 | Introduce the premise: a company whose decisions are public. Links to docs/decisions.md, no ask. |
| Week of 09-29 | X | `launch/pre-launch-teasers.md` #2 | Spotlight the one skill in gold and its receipts (claims, papers, dated A/B validation). |
| 10-05 (Mon) | Digest | — | Weekly send to comped list as normal; no campaign change. |
| Week of 10-06 | X + LinkedIn | `launch/pre-launch-teasers.md` #3 | Countdown post: launch date, what ships, why free digest + $20 spine. |
| 10-12 (Mon) | Digest | — | Final digest before launch; if copy changes are wanted, note "launch tomorrow," but only once [SITE_URL] is real. |

## Launch day — Tuesday 2026-10-13

Fire order matters less than venue-fit copy; each draft is written for
its own room. All in `docs/sales/launch/`.

| Order | Channel | File | Notes |
|---|---|---|---|
| 1 | Email | `email.md` | To the existing (small, comped) free list first — they're warmest. |
| 2 | X | `x.md` | Thread, the meta-hook (this campaign was agent-drafted) leads. |
| 3 | Hacker News | `hn.md` | Show HN. Post mid-morning ET for the best window; expect the skillbay.sh-style "why pay for a markdown file" pushback and let the receipts framing answer it before anyone asks. |
| 4 | LinkedIn | `linkedin.md` | Same day, professional register, staff+/technical-leader angle. |
| 5 | Reddit | `reddit.md` | r/ClaudeAI, r/AI_Agents, r/SideProject — check each sub's current self-promo rule immediately before posting; these change without notice and sales can't verify them same-day. |
| — | Referral | `referral.md` | Live from hour one — the referral ask belongs in the launch email itself, not a separate send. |

## Follow-up sequence (2026-10-14 → 2026-10-27)

| Date | Channel | Purpose |
|---|---|---|
| 10-14 | X + email reply-all-style note | Thank-you + one real number from launch day (whatever it honestly is — signups, HN points, nothing invented). |
| 10-19 (Mon) | Digest | First regular digest post-launch; becomes the new steady cadence anchor. |
| 10-20 | X | "What shipped in week 1" — receipts again: what's true now that wasn't true on launch morning. |
| 10-26 (Mon) | Digest | — |
| 10-27 | X | Second orbit: reference the harness-engineering skill's real-world use if the owner has a usage anecdote by then; skip if not. |

## Steady-state cadence (from 2026-11-01)

One light social snippet per weekly digest send (Mondays), drafted the
week the digest ships once this agent's cadence is scheduled — not
produced speculatively now, since digest content this far out doesn't
exist yet to draw from.

## Change log

- 2026-09-18: first calendar, this run.
- 2026-09-18 (fourth run): dependency 2 corrected from one gold skill
  to two. The launch-month schedule this calendar covers is expanded
  day by day in docs/sales/first-customers.md, which this calendar now
  defers to for everything between 2026-10-13 and 2026-11-11.
