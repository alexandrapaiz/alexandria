# Frontend run, 2026-09-20

Every page was rendered from a production build and screenshotted at 390x844,
820x1180 and 1440x900, and every screenshot was looked at. Twenty-seven before
frames, twenty-seven after. The files kept here are the ones that carry an
argument; the rest showed nothing wrong and were not committed.

## What the pixels said

**Library, all three viewports.** The owner's report was exact and the
screenshots were worse than it. Scene two was not merely clipped: at 390px the
kicker, the title, the intro and the first issue's excerpt were all crowded
into the first view under the shelf, with the excerpt cut mid-sentence at the
bottom edge. At 1440 the intro's second line sat 40px above the fold. The
cause was one rule. `.lib-hero` overrode `.hero`'s height down to its own
content, so scene one stopped where the art stopped instead of where the
viewport does.

**The desk at 390px.** A header reading "AWAITING YOUR MERGE 7" over an empty
white page. All seven rows were in the DOM at opacity 0. `.hero-follow`'s rise
animation comes with the class, and its `view()` range never opens for a block
that is taller than the viewport and starts near the fold. Confirmed by
reading the computed opacity back: 0 at 390, 1 at 820 and 1440.

**The shelf art, all three viewports.** The `viewBox` was 1240 units wide
against rows that lay ink out to 1250, so row 5 lost most of its last spine
and row 1 lost half of one. Walking the row table gives the numbers: row 1
ends at 1241.3, row 5 at 1250.0.

Everything else was clean: home, skills, an issue page, pricing, mission,
routines and the 404, at all three sizes, plus the reduced-motion and
no-hover paths.

## Volume

The skills library was judged at fifty-two entries, not at two. Fifty dummy
skills were generated under `skills/fixture-*` in the real frontmatter shape
and deleted before committing. The page holds: shelves keep the list
navigable, a row at rest carries only its name, version and source count, one
call to action sits at the foot rather than on every row, and the empty shelf
still says so. Kept as `volume-skills-*-52.png`.

## Benchmark, measured rather than remembered

Three sites, read with Playwright, computed styles and rAF traces rather than
impressions.

- **Elicit.** The primary CTA is a colour transition and nothing else. No
  lift, no shadow, no transform. It finishes in about 167ms.
- **Linear.** One easing curve across the whole site,
  `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, and two durations: 100ms for a text
  link's colour, 160ms for a button, which moves background, border, shadow
  and transform together on that one curve. Full-pill radius, as ours is.
- **Consensus.** 100ms, background and outline colour, no transform.

The lesson is discipline, not decoration: one curve, two clocks, and nothing
on any of the three runs longer than 170ms. Ours ran at 400ms.

## The two refinements

1. **The house spring's clock.** `.pill` and `.issue > *` kept the owner's
   approved back-out curve and moved from 400ms to 190ms. Traced before and
   after: the overshoot used to peak at scale 1.0659 at 220ms and settle at
   400ms; it now peaks at 1.0657 at 104ms and settles at 190ms. The peak
   frames are byte-for-byte the same shape, which is the point. The bounce is
   untouched; it just lands while the cursor is still arriving.
2. **The library's scene-two glide.** Filling the first view roughly doubled
   the distance this flight covers, and at 1.2ms per pixel it pinned itself to
   its own 950ms ceiling at every size: measured at 801ms. The canon puts
   page-level moments at 300 to 500ms. Now 351ms at 1440 and 417ms at 820,
   landing at the same scroll position as before.

## Register checks before shipping

- `docs/design/taste.md`, line by line. The reveal ruling of 2026-09-19 is
  item 1 of this run. The prose ruling of the same date is why no copy was
  written here. Black and white only: no colour enters. The hero mark in
  MarkLive.jsx is not touched; the shelf art is a different component and its
  shapes are unchanged, only the frame that was clipping them. Density: the
  first view gained air rather than losing it. No heading gained a subtitle.
- `docs/design/ban-list.md`. Entry 23 is the one this run could most easily
  have broken. The reveal is layout: scene one is a full viewport, so scene
  two is below the fold and no element waits at opacity 0 for an observer.
  Entry 4 is why the benchmark did not become a hover lift. Entry 6 is why
  scene one carries no scroll cue.
- `docs/design/canon.md`. Spacing: 48 replaced an off-scale 44 on the library
  hero's bottom padding. Motion rule 2 (micro at 120 to 200ms) and rule 3
  (page moments at 300 to 500ms) are what both refinements were measured
  against. No dependency was added.
- `docs/design/motion.md`. Kowalski 1 (under 300ms, ease-out) is the argument
  for refinement 1. The note that the digest archive is a high-frequency
  surface with no entrance choreography is why the desk fix switches the rise
  off rather than re-timing it.
- `docs/agents/runtime-changes.md`. Nothing in the container changed. The
  Playwright pin stayed at 1.49.1 and its baked browsers were used.

## Arrived mid-run

Main moved under this run. PRs 52, 53, 54 and 57 merged while it was in
flight, so `origin/main` was merged into the branch and the whole sweep was
repeated against it. Two pages are new, `/privacy` and `/terms`, and both were
screenshotted and read at all three viewports; both are clean and both are
kept here at 390 and 1440. The footer gained its first links in the same
merge, and it holds at 390px.

Three taste rulings also landed mid-run, all dated 2026-09-19 and all for this
seat: the iPhone review (the hero morph plays only after a scroll, so a phone
visitor never sees the one choreographed moment, and the phone layout reads
cluttered), the graph returning as a paywalled page, and the graph UI itself
brought to standard. None of them is in this run's dispatch and none is
attempted here. The morph's trigger is a change to the home page's protected
moment and deserves its own run with its own before and after, not a hurried
third motion change at the end of this one. Nothing shipped here touches
MarkLive.jsx or the hero's geometry.
