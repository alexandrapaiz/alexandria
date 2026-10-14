# Frontend run, 2026-09-24

Every page was rendered from a production build and screenshotted at 390x844,
820x1180 and 1440x900, and every screenshot was looked at. Nine pages at three
viewports, plus scroll slices of the four long pages, the skills library at
fifty rows, a keyboard pass over three pages, a hover pass, the mobile menu
open, and a reduced-motion pass. Before and after crops are kept for the four
changes; the files here are the ones that carry an argument.

Branch: built on PR #73, which was still open from my own last run and holds
`site/app/globals.css` and `site/app/components/MarkLive.jsx`. It is merged
in, so this PR supersedes it.

## What the pixels said

**Markdown tables were never styled.** `globals.css` had no table rule at all,
so `marked`'s output fell through to the browser's defaults: no gutter, no
rules, no head. On the desk's own sprint table at 1440 the columns touched
each other and read `1Remove the digest teaser gate` and `engineernot
started`. The desk is the owner's daily surface and the press writes markdown
too, so the same defaults were waiting for any issue with a table in it.

**The skills library's disclosure marker came apart on a wrapped row.** The
`+` was pinned at `top: 50%`, which is the same place as the first line only
while the name fits on one line. The metadata sits on the first baseline, so
the moment the name wrapped the two drifted apart. Measured at 390px: meta at
26px from the row's top, marker at 38px on a two-line row, further on a
three-line one. At the two skills in the library today this was invisible. At
the fifty the library is built for it was the common case, because most
kebab-case skill names wrap on a phone.

**The phone's menu button was 32 by 32.** The canon's touch law is 44, and
this is the only way into the site's navigation on a phone.

**Keyboard focus was the one state nobody had systematised.** Three elements
carried a designed ring and everything else fell back to the browser's own
`1px auto` outline: the wordmark, all three nav links, the footer links,
`/llms.txt` and every row in the archive. Tabbing the site put the UA's
cramped rectangle next to the house's own ring on the very next stop. The
filter field was worse than either: `outline: none` at a specificity the house
could not reach, so a keyboard user got a border that darkens and nothing
else.

Everything else was clean. No horizontal scroll and no overflowing element at
any viewport on any of the nine pages, no clipped text, no contrast failure.

## Two things that looked like findings and were not

**The bracketed date in the issue headline.** The first capture showed the
issue's H1 reading `The week reinforcement learning stopped needing a verifier
[September 14-20, 2026]` in display type. That was my own fixture inventing a
format the press does not use. `prompts/digest.md` specifies a bare editorial
title and says the date lives in the header, and `site/lib/content.js` only
carries the bracket parser for older issues. The fixture was corrected and
re-shot rather than the page being "fixed".

**The home page reading blank below the mark.** It does in a full-page
capture, at all three viewports. It is scene two of the owner-approved reveal,
and the range opens: computed opacity goes 0 to 1 on the first scroll at 390,
820 and 1440, and under `prefers-reduced-motion` it is 1 at rest. Ban list
entry 24's actual test passes.

## Volume

Judged at the volume the design targets. Fifty skills on seven shelves, 48
dummies under `skills/fixture-*` (gitignored for this, each marked DUMMY
FIXTURE in its description). Desktop holds: rows stay on one line, a row at
rest still carries only name, version and source count, and one call to action
sits at the foot rather than on every row. The phone is where the marker
defect lived, which is the whole reason the charter asks for this pass.

## Benchmark, measured rather than remembered

Read off the live pages with Playwright, computed styles rather than
impressions.

- **Linear.** One curve across the entire surface,
  `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, and exactly two clocks, 100ms and
  160ms, over 73 interactive elements. This is the same reading the last run
  took, and it is the system this house adopted from it. Nothing to take this
  week: we already match it.
- **Consensus.** One clock, 100ms, and the detail worth taking:
  `outline-color` is in the transition list alongside `background-color` and
  `color`. The focus ring is designed and it moves on the same clock as every
  other state rather than snapping into place.
- **Elicit.** Its above-the-fold controls were still hydrating and reported
  one transitioning element, the skip link. Third run in a row that Elicit has
  refused to be measured on load. The owner's bouncy-hover ruling is already
  carried by `.pill`'s approved spring, so nothing is blocked on it, but this
  is now a standing measurement problem worth a different approach.

What the benchmark bought this run is the focus ring, not a curve.

## The two refinements

**1. The phone's toggle accepts a finger.** The drawn control stays 32px,
which is what the bar wants optically, and the hit area is extended past the
glyph with a pseudo-element inset at -6px, so 32 plus 6 on every side is 44.
Nothing on the page moves. Verified by hit-testing outward from the centre
until the point stops landing on the button: 44 by 44, bars still 20px, and a
tap 4px outside the drawn box opens the menu. `.skill-line` already does the
same thing with a negative margin, and Freiberg's Fitts note is the argument
for both.

**2. One focus ring, house-wide, and it fades.** The house ring is the
hairline it already used. The one thing that varies is the offset, with the
size of what it wraps: 2px on a field, 3px on inline text, 4px on a
full-width row band. That is a scale rather than drift, and the per-component
rules still win on purpose, including the pill's white-gap-then-black ring,
which exists because a black ring on a black pill is invisible. The base rule
is written with `:where()` so it has zero specificity and cannot outrank
anything already designed. It carries a transparent ring at rest for the
colour to move from, which is what makes the fade possible at all, and
`prefers-reduced-motion` drops that transition with the other colour ones.
After: every tab stop on three pages reports `1px solid` ink, and the
fractional alphas caught mid-tab are the fade being measured in flight.

## Register checks before shipping

- `docs/design/taste.md`, line by line. Black and white only: nothing added
  has a colour, the ring is `--ink` and the table rules are `--line`. The hero
  mark is untouched, geometry and trigger both. Density: the table fix moves
  the sprint table up the spacing scale rather than down. No heading gained a
  subtitle. Clerk as the small-states benchmark is the argument for the focus
  work, and the fifty-skill ruling is what surfaced the marker defect. The two
  graph rulings are not attempted and are noted below.
- `docs/design/ban-list.md`. Entry 4 is why the table got rules and gutters
  rather than a card. Entry 3 is why there is no zebra striping. Entry 25 is
  the direct parent of the focus finding. A new entry, 26, is appended for the
  tell this run found.
- `docs/design/canon.md`. Type: the table uses 12 for the head and 17 for the
  cells, both on the scale, and no new value enters. Spacing: 32, 24, 16, 12
  and 8, all on the 8-point grid. Radii: none added. Motion: the ring moves on
  `--fast`, which is the existing clock, and on `--ease`, the existing curve,
  so the system stays at one curve and two clocks. No dependency was added.
- `docs/design/motion.md`. Kowalski 1 (under 300ms, ease-out) is the ring's
  clock. Kowalski 8 (a designed reduced experience) is why the reduced-motion
  block gained the ring rather than being left to drop it raggedly. Freiberg 5
  (Fitts, generous hit areas) is refinement 1 entire.
- `docs/agents/runtime-changes.md`. Nothing in the container changed. The
  Playwright pin stayed at 1.49.1 and the baked browsers were used. The
  mismatch the last run reported is still there: `site/package.json` carries
  `playwright ^1.63.0` as a devDependency, and `site/node_modules/playwright`
  is 1.63.0 on disk, so a script that imports `playwright` by bare name gets
  the wrong one. This run imported 1.49.1 by absolute path out of the npx
  cache to stay on the baked browsers.

## Not attempted, and why

- **The graph.** `/graph` is still a 404 and the component still lives at
  `site/app/_graph/`, which the underscore keeps off the router. Her two
  rulings of 2026-09-19 want the route behind `hasSpine` and the graph UI
  rebuilt to industry standard. That is a feature build and a run of its own.
  Two runs have now deferred it, which is the thing worth her attention here.
- **The nav's ghosting.** The bar is `rgba(255,255,255,0.94)` over
  `blur(22px)`, and content genuinely composites through it. Measured again
  this run at fifty rows, where it is at its worst: still faint at 1x, and the
  0.94 was the last run's deliberate fix. Left alone rather than spent as one
  of two refinements.
- **The off-scale values across `globals.css`.** Still there, still counted,
  still a ledger proposal rather than a refactor, for the reason the last run
  gave: it is a large visual diff that cannot be honestly re-verified in one
  run.
