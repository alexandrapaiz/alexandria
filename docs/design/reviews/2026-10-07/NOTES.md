# Frontend run, 2026-10-07

The weekly visual sweep. Ten pages at 390x844, 820x1180 and 1440x900, every
screenshot looked at, plus the morph driven frame by frame inside its own
scroll window, the scene two reveal measured at rest and after scrolling at
all three viewports, hover and touch profiles separated, a reduced motion
pass, and the skills library judged at 53 entries rather than at the nine the
repo holds today.

Branch: this run **builds on #202** and supersedes it. That was this seat's
2026-10-05 window and it ended with an eight line README stub in
`docs/design/reviews/2026-10-05/`. Its commits are merged in here, so #202 was
closed rather than reviewed. Counting unmerged links the chain is two: #168 is
the lineage behind #202 and is already in main.

## The run's own failure, because the charter says to say so

Three screenshots came back as a white phone frame carrying one line:
"Application error: a client-side exception has occurred". The measurements
taken alongside them said the skills fix had made the column drift worse, 105px
to 213px.

Neither was true. The run rebuilt while the previous `next start` was still
listening on 3000, started a replacement with `(nohup ... &)`, and the
replacement died instantly with `EADDRINUSE` into a log file while the
subshell returned success. The old server kept answering with the previous
build's asset hashes, so every chunk returned 400 and the page rendered with
no stylesheet and no hydration. The "worse" numbers were measurements of an
unstyled page.

This is the third occurrence. `INC-2026-09-23-phantom-production-bug` cost a
dozen turns, `INC-2026-09-24-stale-server-kill-noop` recorded its fix failing
the next day, and both prescribe exactly the checks that would have caught
this. Neither check existed anywhere a run could execute: they live in the
incident register and nowhere else, so each run of this seat starts from a
container with no memory and rebuilds a harness that does not have them.

So the harness is committed this time rather than prescribed a fourth time, at
`docs/design/harness/`, with the kill that cannot match its own argv, a bind
check that reads the log rather than trusting an exit code, the
served-versus-disk stylesheet comparison, and the render assertion that
refuses to photograph a page that is not ours. The incident is
`INC-2026-10-07-stale-server-third-occurrence`.

What caught it was the charter's own rule and nothing else. The numbers looked
like a finding. The screenshot said Clerk's successor.

## What the pixels appeared to show and the measurement refuted

**The nav looked transparent again.** Scrolled body text appeared to read
through the sticky bar on the issue page at 1440. Decoding the PNG and reading
the rows says otherwise: in the gap between the nav's own links the darkest
pixel is 247 to 255 out of 255, against 38 for the nav's links one row down.
The 0.94 white and the 22px backdrop blur are doing their job and what is left
is a ghost at about 3% ink. This is the second run to nearly file it, so the
pixel reader is committed as `docs/design/harness/ink.mjs`. No defect, no
change.

**The audit reported small tap targets everywhere.** The nav toggle at 32x32
and the footer links at 43x15 are real elements, and both already carry a hit
area extended past the glyph by a pseudo-element, which a bounding-box audit
cannot see. Checked in the stylesheet before touching anything. The pills were
the one case where the audit was right.

## What was verified and found healthy

- **The scene two reveal**, the owner's ruling of 2026-09-19, which uses
  `animation-timeline: view()`, the exact mechanism ban list entry 24 names.
  Computed opacity at rest and after scrolling, all three viewports: 0 then 1
  every time. The range opens everywhere. Re-verified after this run's motion
  change. `home-scene2-*.png`.
- **The morph**, driven rather than waited on, and this time inside its own
  window: `MORPH_WHEEL` is 480 in `MarkLive.jsx`, so the turn was spent in
  60px steps and `scrollY` stayed 0 across all of it. Machine, mid and book
  are in `morph-desktop-0-machine.png` through `morph-desktop-2-book.png`. On
  the phone it autoplays on load with `scrollY` at 0, which is the 2026-09-19
  fix. The geometry was not touched.
- **Reduced motion.** Scene two sits at opacity 1 at rest under
  `prefers-reduced-motion` at all three viewports, so the reduced experience
  is a designed one rather than a broken one.
- **The desk's hover affordances.** 12 elements at opacity 0 on desktop and 0
  at the touch viewports, measured under a forced `hover: none` and
  `pointer: coarse` profile. Correct in both directions, which is ban list
  entry 24 staying fixed.
- **No horizontal overflow and no element outside the viewport** at any of the
  thirty combinations, before and after.
- **The graph gate** now opens at the article shell with its h1 at x=404, the
  same as pricing, mission, routines, the issue and the 404. That is the
  previous run's second refinement landing, verified from the outside.
- **A real 250 character string in a receipts value slot.** One real skill's
  `validated` field holds a date followed by a sentence. It wraps cleanly in
  the value column at 1440 and at 390, no overflow and no clipping.

## What was fixed

**The skill row at volume, at both ends, from one cause.** The row is a flex
line with the name at one end and the metadata at the other, and the columns
were never declared, so each field floated against the width of its own text.

Wide, the fields wandered. Across 53 rows the version alone started at 14
different x positions spanning 105px, so a list whose whole job is to be
scanned read as a ragged edge rather than as a table. The metadata is three
fixed tracks now, sized to the longest string each field can hold, measured on
the page rather than guessed: 18, 94 and 89px for `V1`, `DEPRECATED` and
`10 SOURCES`, rounded onto the spacing scale with room for a two-digit version
and a three-digit count. The status cell renders empty rather than being
dropped, because a missing cell slides the two beside it.

Narrow, the secondary field won. The metadata is `nowrap` and a name is not,
so at 390px the cluster took 109 to 205px of a 342px row and left the name 89
to 136px. Names broke to three, four and in one case seven lines, with the
hyphen leading the line, and rows ran 101 to 177px tall against 50 for a row
that fits. Below 560px the name takes the width and the metadata goes beneath
it.

| | before | after |
|---|---|---|
| version column spread, 53 rows | 105px | 0 |
| status column spread | ragged | 0 |
| source count column spread | ragged | 0 |
| worst name wrap, 390px | 7 lines | 2 |
| tallest row, 390px | 177px | 97px |
| narrowest name, 390px | 89px | 146px |
| page height, 390px | 8244px | 6656px |

`fix-skillrow-desktop-before.png` against `fix-skillrow-desktop-after.png`,
and the same pair at `-iphone-`. At 820 every row is a single line at 50px:
`skills-rows-ipad-after.png`. This is the observation behind new ban list
entry 30.

**The pill was under the touch minimum.** 10px of padding on a 14px label
draws a 39px button, 41 with the ghost border. Measured on the phone: the
nav's Pricing at 75x39, See pricing at 114x41, All issues at 105x43. None of
them reaches the canon's 44 by 44, on the one pointer that cannot aim, and the
pill is the site's primary control. The hit area is extended past the glyph
with a pointer-only pseudo-element rather than the pill being grown, which is
how `.mobile-nav-toggle` and `.skill-line` already solve this. Verified after:
every pill reports a 44px target on touch, `::after` resolves to `none` on
desktop, the nav stays 390x83, the h1 stays at x=24, no overflow.

**The receipts list printed two date formats in one table.** `Distilled` ran
through `formatDate` and `Held up in use` did not, so the same `dl` read
"October 7, 2026" on one row and "2026-10-07" two rows below it. The formatter
was already imported into the file. No skill in the repo carries a validated
date today, so the row never renders at the inventory of the day: it showed up
against the fixtures, which is what judging at volume is for.
`fix-receipts-dates-after.png`.

## The benchmark

Elicit, Linear and Consensus, read off the live pages this run rather than
from memory. The measurement is every distinct (property, duration, easing)
triple actually computed on their hoverable elements.

| | durations in use | curves in use |
|---|---|---|
| Elicit | 0.2s | one, transform and opacity only |
| Linear | 0.1s and 0.16s | `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, plus the browser's `ease` for plain colour |
| Consensus | 0.1s | one |

This reproduces the 2026-09-30 result exactly, which is itself worth having:
the best in class run their whole marketing surface on one curve and one or
two clocks, and they still did a week later. Our tokens are already Linear's
exactly, which a previous run adopted. So the benchmark's value was again a
yardstick rather than an idea, and this time the measurement was turned on us
with the same script (`docs/design/harness/ourmotion.mjs`).

## The refinement, and there is one rather than two

**The last browser default is out of the motion system.** Measured across ten
pages at two viewports, we shipped five durations and three curves, and one of
those curves was the browser's own `ease`. It is not a decision anyone made,
which is exactly why it survived review: there is no line in the stylesheet to
read and object to. It carried both of the site's page-level moments, `@rise`
at 0.7s and `.lib-art`'s fade, and 0.7s sits outside the canon's own 300 to
500ms page-level window.

`canon.md` animation rule 3 names a page-level curve, `cubic-bezier(0.4, 0,
0.6, 1)`, Apple's, at 300 to 500ms. The stylesheet never had it. It is a token
pair now, `--page` and `--ease-page`, and both moments run on it. No value here
is invented: both numbers are written in the canon already.

| | before | after |
|---|---|---|
| distinct durations shipped | 5 | 4 |
| distinct curves shipped | 3 | 3 |
| curves no register names | 1 | 0 |

One note on what this does and does not change. `@rise` carries
`animation-timeline: view()`, so in a browser with scroll-driven animations
the duration is ignored and the timeline drives progress across the range;
the curve shapes that progress and the duration governs the fallback path for
browsers without it. So the curve change is visible everywhere and the
duration change is the fallback coming inside the canon's window. Verified
after: the reveal still goes 0 to 1 at all three viewports and reduced motion
still sits legible at rest.

The second refinement slot went unused on purpose. The skills row was the
honest use of this run's budget, and a second interaction change on top of a
layout change of that size would have arrived unmeasured.

## Registers

- **canon.md**: every value used is from the measurement system. The two new
  motion tokens are the canon's own numbers, quoted from animation rule 3. No
  new colour, no new dependency, no new font. The fixed metadata tracks are
  24, 96 and 96, from the spacing scale.
- **ban-list.md**: checked entry by entry against this diff. Entry 30 appended
  from the skill row. Nothing deleted. Entry 21 holds, one offer on the page
  at 53 rows. Entry 22 holds, a row at rest still carries an identifier and
  two facts. Entries 23 and 24 re-measured and clear. Entry 25 is what the
  refinement serves. Entry 26 is the argument for it.
- **taste.md**: checked entry by entry. Hero geometry, timing and
  choreography untouched. The mission line stands alone. No colour. The graph
  stays paywalled with no preview and unlisted in the nav. The library intro
  is not cut at the viewport edge at 390. Density was added rather than
  removed, on the phone row especially. Clerk remains the flows benchmark and
  the library is organised to scale to fifty, which is what it was judged at.
- **motion.md**: the refinement is rule 1's sibling for page-level motion, and
  Freiberg's Fitts note is the argument for the pill's hit area, as it already
  was for the nav toggle and the skill row. `prefers-reduced-motion` re-verified.
- **runtime-changes.md**: read. Nothing in this run touches the container, the
  Playwright pin, a workflow or a secret. `npx playwright@1.49.1` exactly, and
  the container's baked Chromium is build 1148, which is that pin's.
- **Copy**: no reader-facing word was invented, changed or moved. The diff
  carries one JSX text change, `{s.status ... : ""}`, which renders the same
  characters it rendered before. Nothing on the site needed a line this run
  that an approved file does not already carry, so there was nothing to set
  and nothing to check against `quality-claims.md`.
- **incidents.md**: `INC-2026-10-07-stale-server-third-occurrence` appended,
  because the standing rule binds this seat and a repeat that goes unrecorded
  is itself an incident.
- **lessons.md**: read the `any` section and the `engineer` section, there
  being no frontend section. L-E10 produced the PR survey in the description.
  L-E3 is the draft PR opened before the work. L-E1 added no subtitles.

## Left undone, deliberately

The `#86868b` house grey computes to 3.62:1 on white, below WCAG AA's 4.5 for
text under 24px, and it carries most of the running prose on the site. The
palette is the owner's alone under the canon, so this stays a ledger proposal
rather than a change. It was left undone by the previous run for the same
reason and is recorded again here because nothing has moved.

The masthead still starts at three x positions across the desktop shells: 404
on most pages, 364 on skills, 264 on the desk. Both of those shells have a
real reason to be wider. Holding one left edge while the content below widens
is a design decision rather than a bug fix, so it is in the ledger.

The desk is 30,713px tall at 1440 and 57,631px at 390, which is 68 phone
screens, because it renders 324 open items with no pagination. It is the
owner's internal surface and the volume is real rather than a layout fault, so
it is a ledger note. The full-page frames for the desk in this directory are
viewport frames for that reason; a 57,000px PNG is neither readable evidence
nor a thing to commit.

`skills/fixture-*` was removed before this PR was finished. The pattern is
gitignored and nothing from it is in the diff.
