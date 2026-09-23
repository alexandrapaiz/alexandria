# Frontend run, 2026-09-23

Every page was rendered from a production build and screenshotted at 390x844,
820x1180 and 1440x900, and every screenshot was looked at. Thirty-six renders
before the fixes and thirty-six after, plus scroll slices of the long pages,
a morph trace, a reduced-motion pass and a hover pass over every interactive
element on eight pages. The files kept here are the ones that carry an
argument.

Branch: built on PR #56, which was still open from my own last run and holds
`site/app/globals.css`, `docs/design/ban-list.md` and
`docs/agents/incidents.md`. It is merged in, so this PR supersedes it.

## What the pixels said

**The hero morph, at 390px.** Her report of 2026-09-19 was exact. On a touch
device `MarkLive` drove the morph from `window.scrollY` alone, so at rest
`p = 0` and the mark held the racked machine forever. A phone visitor who
did not scroll never saw the site's one choreographed moment. Confirmed by
reading the polygon points back out over three seconds at scroll 0: byte for
byte identical.

**The desk's seat lane, at 390px.** `@media (max-width: 560px)` set
`.desk-lane { flex-basis: 64px }`, but a flex item's `min-width: auto` floors
it at its own content, so ENGINEER and RESEARCH pushed their lanes out to
70px while FE and SKILL stayed at 64. Every title then started at a different
x. Measured: lanes 64 and 70, titles at 196 and 190 wide. Ragged at 390 only;
desktop was already correct at a fixed 76px.

**The desk's lane type.** `font-size: 11px`. The canon's type scale says small
print is 12 or 14, never 11.

**The digest's body type.** `font-size: 16.5px`, which is not on the type
scale at all, on the site's primary reading surface. The canon's body size is
17. The measure was checked before touching it and was already fine: 73, 61
and 71 characters on the first three paragraphs at 1440, inside the 75
ceiling, so the column did not have to move with the type.

Everything else was clean: home, library, an issue page, skills, pricing,
mission, routines, privacy, terms and the 404, at all three sizes, with no
horizontal scroll and no overflow anywhere.

## Three things that looked like bugs and were not

Worth recording, because each one would have been a wrong fix.

**The home page reads blank below the mark.** In a full-page capture it does:
the statement, the call to action and the about line all sit at opacity 0.
They are scene two of the home page's approved reveal, and the range does
open. Read back at three viewports and three scroll positions, every one of
them goes to opacity 1 on the first scroll. A full-page screenshot captures
at scroll 0 with an expanded viewport, which is exactly the condition under
which a working `view()` reveal looks broken. Ban list entry 24 says the test
is the computed opacity at rest at every viewport; that test passes here.

**Text ghosting through the nav.** It is there. It is also 7 to 9 greys off
white. Measured across the whole 390x83 band: minimum 246 against a paper of
255, nothing below 240 except the nav's own black. The blur genuinely
composites in this headless build, checked with a hard edge inside the bar,
which smears across roughly 60px. The 0.85 to 0.94 fix in the file's comment
worked. Left alone.

**The library rows and the desk rows have no hover.** A first pass said so.
They both do, on their children rather than on themselves: `.issue:hover > *`
translates 6px, `.desk-row:hover .desk-go` reveals the action. And
`@media (hover: none)` already pins `.desk-go` open for touch. The probe was
reading the wrong node.

## Volume

Judged at the volume the design targets, not the inventory of the day. Fifty
skills (48 dummies under `skills/fixture-*`, gitignored for this) and fourteen
issues (fixtures under `site/content/issues`, deleted before committing). Both
hold: the skills shelves keep fifty rows navigable, a row at rest still
carries only name, version and source count, one call to action sits at the
foot rather than on every row, and the archive's fourteen rows keep their
hairline rhythm at all three sizes. Kept as `volume-*`.

## Benchmark, measured rather than remembered

Read off the live pages with Playwright, computed styles rather than
impressions. The previous run measured hover clocks; this one measured the
system those clocks belong to.

- **Linear.** One curve across the entire surface,
  `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, and exactly two clocks: 100ms for a
  nav link, which moves colour and background only, and 160ms for a button,
  which moves border, background, colour, box-shadow, opacity, filter and
  transform together. Full-pill radius.
- **Consensus.** One clock, 100ms, on background, colour and outline colour.
  Radius 12px. Focus rings are transitioned too, not snapped.
- **Elicit.** Its above-the-fold controls were still hydrating and reported
  nothing useful this run. The previous run's measurement stands: the primary
  CTA is a colour transition finishing near 167ms, no transform.

The lesson is not a number, it is that the number is the same everywhere. Our
sheet had grown to **four easing curves and seven transition clocks**. That is
drift, and drift is what the generated web looks like from close up.

## The two refinements

**1. The morph a phone can see.** On touch the morph now plays itself once on
load, after a 350ms hold that lets the rack register as a rack before it
starts moving (a morph you did not see start teaches nothing). The driver
ramps over 480ms, inside the canon's 300 to 500ms window for a page-level
moment; the mark's own approved lerp carries the tail, exactly as it does on
desktop. The thumb can still carry the morph further and can never drag it
back under what the intro opened. The shapes, the per-page stagger and the
easing inside `compute()` are untouched: only what moves `p` changed. Traced
at 390: identical rack at t=0, moving by t=500, open book by t=1200, settled
by t=2200. Under `prefers-reduced-motion` the polygons are unchanged after
2.5 seconds, and scene two is at opacity 1 at rest.

**2. One curve, two clocks.** Four curves and seven clocks collapse to the
benchmark's discipline, as `--ease`, `--fast` (100ms, colour and opacity on
high-frequency targets) and `--slow` (160ms, anything that also moves), over
nine declarations: the nav links, the mobile toggle, the waitlist field, the
agent-note links, the filter input, the skill line and its two marks, and the
desk's action. The owner's approved bounce,
`cubic-bezier(0.34, 1.56, 0.64, 1)` at 190ms on `.pill` and `.issue`, is not
part of this system and was not touched, and neither was the 90ms press or
`.lib-art`'s 500ms page-level fade.

Two gaps in `prefers-reduced-motion` were closed while in there: the mobile
toggle's bars actually rotate, and the nav link's fade belongs with the other
colour transitions the house already mutes. Neither had ever been listed.

## Register checks before shipping

- `docs/design/taste.md`, line by line. The 2026-09-19 iPhone ruling is
  refinement 1, and only the trigger and the surrounding air changed, as it
  specifies. Black and white only: no colour enters. The hero mark's geometry,
  timing and choreography are untouched. Density: the desk's phone rows gained
  air and lost half their wraps. No heading gained a subtitle. The graph
  rulings are noted below, not attempted.
- `docs/design/ban-list.md`. Entry 24 is the one this run could most easily
  have broken, and the home page was tested against its actual test rather
  than its shape. Entry 4 is why the benchmark did not become a hover lift.
  A new entry, 25, is appended for the tell this run found.
- `docs/design/canon.md`. Type: 11px and 16.5px both removed, both replaced
  from the scale. Spacing: the desk lane moves from an off-grid 76 to 96.
  Motion rules 2 and 3 are what both refinements were measured against. No
  dependency was added.
- `docs/design/motion.md`. Kowalski 1 (under 300ms, ease-out) and 6
  (frequency decides ceremony) are the argument for the two clocks. Freiberg 1
  (motion communicates origin) is the argument for the morph's 350ms hold.
- `docs/agents/runtime-changes.md`. Nothing in the container changed. The
  Playwright pin stayed at 1.49.1 and the baked browsers were used. One
  mismatch found and reported, not changed: `site/package.json` carries
  `playwright ^1.63.0` as a devDependency, which does not match the baked
  browsers and would download its own if anything ever ran it.

## Not attempted, and why

- **The graph.** `/graph` is still a 404; the component lives at
  `site/app/_graph/`, which the underscore keeps off the router. Her two
  rulings of 2026-09-19 want the route to exist behind `hasSpine` and want
  the graph UI rebuilt to industry standard. That is a feature build and a
  full run of its own, not a polish diff at the end of this one.
- **The 92 off-grid spacing values and 38 off-scale type values** across
  `globals.css`. Audited, counted, and proposed in the ledger rather than
  refactored here: changing them all is a large visual diff that cannot be
  honestly re-verified in one run, and the canon's own remedy for an
  off-system value is a ledger entry.
