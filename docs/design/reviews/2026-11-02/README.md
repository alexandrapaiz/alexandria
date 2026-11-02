# Frontend review, 2026-11-02 (message run)

This run was woken by a handoff from alexandria/pm. Pull request #559, the
display-type-balance work, conflicted against `main` and was six and a half
days old. A conflict is not the PM's to resolve in code, so it came here.

The run did two things. It resolved the conflict, and then it re-verified the
change the conflict was blocking, because that change was measured against a
`main` that has since taken 578 commits and nothing had looked at it since.

## What the conflict actually was

Both ledgers and no site code, which is the same shape as #428. `docs/ideas.md`
and `docs/agents/incidents.md` both take new entries by appending at the end of
the file, so two runs appending at one anchor collide on the second merge every
time. `site/app/globals.css` merged clean and additive, and `main` had added no
`text-wrap` rule of its own, so there was nothing to reconcile on the surface
this seat owns.

The resolution keeps both sides, main's entries first and the branch's after,
with the house separator between them.

### The trap inside it, which is on record and was live here

`INC-2026-10-18-keep-both-sides-orphaned-the-line-both-sides-ended-with`
describes the way this exact resolution damages the file anyway. In
`docs/ideas.md` the last line of main's newest entry was `- Status: proposed`
and so was the last line of the branch's, so git matched them as common context
and placed that single pair *after* the `>>>>>>>` marker rather than inside
either side. Keeping both sides naively produces main's entry, then the
branch's entry, then one closing pair that belongs to the first and now reads
as the status of the second.

That was live in this conflict. Both entries were given their own `- Cost:`
and `- Status:` lines in the resolution.

Three proofs rather than a reading, because the incident above is explicit that
reading does not catch this:

- `tools/check_registers.py` reports `0 blocking, 71 warning(s)` on this branch
  and `0 blocking, 71 warning(s)` on `origin/main`. The counts are identical, so
  the merge introduced no new register damage.
- Counting line occurrences with multiplicity, zero lines of `origin/main` and
  zero lines of #559's branch are absent from either resolved file. Multiplicity
  is the part that matters, because the orphaned-suffix defect drops one of two
  identical lines and a set comparison cannot see it.
- The conflict-marker sweep over `docs/`, `prompts/`, `README.md` and `site/`
  prints nothing.

## Re-verifying the change the conflict was blocking

#559 measured `.issue-body h1` on the `main` of 2026-10-26. The rule is
`text-wrap: balance` with `pretty` below 560. Re-measured on the merged tree,
against the live page rather than injected styles:

| viewport | property in force | measure | line boxes | last line |
|---|---|---|---|---|
| 390 | pretty | 342 | 297, 305, 156 | 46% |
| 440 | pretty | 392 | 297, 305, 156 | 40% |
| 470 | pretty | 422 | 420, 346 | 82% |
| 540 | pretty | 492 | 477, 289 | 59% |
| 559 | pretty | 511 | 477, 289 | 57% |
| 560 | pretty | 512 | 477, 289 | 56% |
| 561 | balance | 513 | 420, 346 | 67% |
| 600 | balance | 552 | 420, 346 | 63% |
| 820 | balance | 632 | 420, 346 | 55% |
| 1440 | balance | 632 | 420, 346 | 55% |

The breakpoint fires exactly where the rule says. The wide case reads 420/346,
which is the number #559 reported, so the measurement survived 578 commits of
`main`. No width in the range ends on a stub.

Looked at rather than only measured:

- [390, pretty](h1/h1-390-pretty.png), a clean descending rag with no stub
- [560, pretty](h1/h1-560-pretty.png) and [561, balance](h1/h1-561-balance.png),
  the two sides of the breakpoint, both good two-line sets
- [820](h1/h1-820-balance.png) and [1440](h1/h1-1440-balance.png), the evened pair
- [the issue top at 390](h1/issue-top-390.png) and
  [at 1440](h1/issue-top-1440.png), at 1:1, with the dek under the title

## The sweep

Eleven pages at 390, 820 and 1440, 33 frames, with the skills library carrying
45 DUMMY FIXTURE entries under `skills/fixture-*` so the list surface was judged
at 54 skills on 7 shelves rather than at the nine the repo holds.

The audit returns no failures: no horizontal overflow on any page at any
viewport, no tap target under 44, and every route answering 200.

- [skills at 54 entries](sweep/skills-desktop.png) holds its declared columns
  down the whole list, carries one offer at the foot rather than one per row,
  and keeps each row to an identifier and the facts you would sort by. Ban list
  21, 22 and 30 all pass at volume.
- [home](sweep/home-desktop.png), [library](sweep/library-desktop.png),
  [the issue at desktop](sweep/issue-desktop.png) and
  [at phone](sweep/issue-iphone.png).

Two things the audit flagged that are not defects, checked rather than assumed:

- The home page holds `.statement`, `.hero-act` and `.about-inline` at opacity 0
  at all three viewports. That is the scroll reveal the owner ruled on
  2026-09-19, where the library page was told to match what the home page's
  second scene already did. Approved, not ban list 24.
- The desk holds twelve `.desk-go` spans at opacity 0 at desktop only. The
  stylesheet carries `@media (hover: none) { .desk-go { opacity: 1 } }` and
  names `.desk-go` in the reduced-motion block, so the affordance is present
  wherever there is no hover to give it. That is the charter's touch rule
  already satisfied.

### One measurement worth leaving for the next run

Ban list 29 says to measure the h1's left edge on every route at the widest
viewport and read the numbers side by side. At 1440 the answer is 404 on
library, the issue, graph, left-behind, pricing, mission, routines and the 404
page, 364 on skills, and 264 on the desk.

Every one of those shells is centred, measured to the pixel, so this is a
measure ladder rather than entry 29's stranded layout: 632 for the issue's
article column, 680 for the house, 760 for the skills table, 960 for the desk.
The spread is deliberate and the h1 does slide 40px between the house and
skills and 140px between the house and the desk. Worth an eye some run, not
worth a diff in a run the PM is waiting on.

The same measurement confirms entry 29's recorded defect is repaired. `/graph`
was the page it was spotted on, capped at 1280 with its h1 at x=104 against 404
everywhere else. It now reads 404 and 680 centred, exactly the house constant.

## What this run did not do

It did not run the benchmark pass or ship an interaction refinement. Both are
steps 3 and 4 of the weekly charter and this was a message run answering a
conflict handoff, where the PM has said it will merge the same pass it sees the
branch clean. Adding polish would grow the diff under review for a pull request
whose stated problem is that it is old.

## The container, for the next run

Two things cost turns and neither is a repository defect.

`serve.sh` failed its fourth check with a 500 because no Clerk publishable key
is set in this container. The script names the cause precisely and gives no
cure, and the harness README's "Clerk is solved in the script now" is about the
`__clerk_db_jwt` cookie, which cures the handshake and cannot cure a middleware
that throws before reaching it. A `pk_test_` key over a non-routable host, set
in the environment and committed nowhere, is what got past it.

The browser needed the whole dance the harness README describes: no browser
libraries in the image, and a cache holding `chromium-1248` against a pin that
asks for `1243`. The private browser root that
`INC-2026-10-26-the-shared-browser-cache-lost-a-revision-mid-run-for-the-second-time`
recommends over the in-place symlink is what this run used, and it worked
first time.
