# Frontend run, 2026-09-26

The dispatch ordered one build: the queued paywalled `/graph` page, from the
live claim graph rather than from the committed fixture, with its UI consistent
with the rest of the site. That is most of this run. The weekly sweep ran
around it: ten pages at 390x844, 820x1180 and 1440x900, every screenshot
looked at, plus the graph at four more states, a keyboard pass, a
reduced-motion pass, and the scroll-reveal test the ban list asks for.

Branch: no frontend PR was open at the start of the run (`gh pr list` showed
only #107, writer, and #60, engineer), so this branched from main. Neither of
those touches `site/`.

## The graph

`/graph` is a real route again and the underscore folder is gone.
`site/app/_graph/` and `site/lib/graph-data.js` are deleted, so the fixture
cannot come back by accident. That fixture described 254 claims and 88 edges
from a 2026-09-13 snapshot, against tonight's 746 and 238. A page that draws a
picture of last fortnight's database is a page that lies about the product,
and the claim graph is the product.

What is there now:

- `site/lib/graph-live.js` reads Neon: the claims that carry at least one
  link, each joined to its paper, every edge, and the four totals. It fails
  closed exactly the way `lib/entitlement.js` does, and it returns `null`
  rather than an empty graph when the database cannot be read, because "no
  edges" and "could not read the database" are different things to tell a
  subscriber.
- `site/app/graph/page.jsx` gates the whole page on `hasSpine()`. The query
  runs only after that returns true, so an unpaid visitor's response carries
  no claim text at all. Verified by reading the served DOM at all three
  viewports: no canvas element, no claim data, nothing but the heading and
  the offer. Her ruling of 2026-09-19 was "no preview, no teaser rendering".
- `site/app/graph/GraphExplorer.jsx` is the canvas, the legend toggles, the
  topic filter, the search, and the side panel with the claim, its evidence
  grade, its paper as an arXiv link, and every neighbour with its relation.

No dependency was added. 214 nodes and 238 edges is well inside what plain
arithmetic draws, and the canon wants a ledger proposal before a library
arrives, not after.

## Verified at volume, because the container has no database

There is no `DATABASE_URL` in the agent container, so the live query cannot
run here. Rather than judge the page at zero rows, the run generated rows in
the exact shape `graph-live.js` returns, at tonight's real counts (746 claims,
746 total, 214 linked, 238 edges, 8,956 papers), pushed them through the same
`shape()` function, and rendered them through the same component on a
temporary route. That route is deleted; it is not in this PR. What it verified
is the layout and the interaction at volume. It does not verify the SQL, and
nothing here claims it does. The SQL wants one look against the real database
before the owner merges.

## What the pixels said about the graph, three times

The first render was the useful one, and it was bad.

**The small components smeared into horizontal rules.** The first layout
packed component slots into rows, which put every two-node and three-node
component at one y value. A pair whose spring rest length exceeded its slot
stretched sideways into its neighbours, and the top and bottom of the canvas
read as dotted rules rather than as claims. At today's shape that is roughly
thirty components, most of them pairs, so it was most of the picture.
`graph-layout-desktop-before.png`.

**Unit coordinates were drawn onto a non-square canvas.** `x * width` and
`y * height` on an 870 by 620 stage stretches everything horizontally by a
factor of 1.4, which is the second reason the pairs looked like rules. There
is a view transform now, computed from the settled bounds, so the graph fills
the stage at any aspect without distorting.

**Repulsion was five times too weak.** After the packing was replaced, every
component collapsed into a knot with no readable edge inside it
(`graph-layout-desktop-mid-knots.png`). Two nodes sit at equilibrium where
`K/d` balances the spring's `0.016 * (d - rest)`; solving for a comfortable
separation of 0.07 gives `K` near 1.6e-5, and the first tuning used 3e-6.
Component gravity also became containment rather than attraction, because a
centre-seeking force compresses exactly the structure the page exists to show.

`graph-volume-desktop-after.png` is the third render and the one that ships.

**The canvas was unreachable by keyboard.** Found by the tab pass, not by
looking. A keyboard reader could search, filter, and toggle all four edge
types, and never open a single claim, on the one page the subscription is
being sold for. The canvas now takes focus, carries the house ring, and the
arrow keys walk the matching claims in id order, with Escape to clear.
`graph-volume-desktop-keyboard.png`.

**The old gate was glassmorphism.** `.graph-gate` carried
`backdrop-filter: blur(10px)` over a translucent white panel, which is ban
list entry 7 by name. It was rebuilt as a hairline card on paper.

## The rest of the site

Nine other pages at three viewports, every screenshot looked at. No horizontal
scroll and no element outside the viewport at any of the twenty-seven
combinations. No clipped text, no broken wrap, no contrast failure. The skills
library was judged at 52 entries under the `skills/fixture-*` convention, and
the two fixes the 2026-09-24 run made there hold at volume: rows stay one
line, a row at rest still carries only name, version and source count, and one
call to action sits at the foot rather than on every row.

Two things that look like findings in a capture and are not, both re-checked
this run rather than inherited:

- **The home page reads blank below the mark.** It is scene two of the
  owner-approved reveal. Computed opacity at rest and after scroll, measured
  at all three viewports: 0.00 to 1.00 on the first scroll, and 1.00 at rest
  under `prefers-reduced-motion`. Ban list entry 24's actual test passes.
- **The nav floats mid-page in the long captures.** `position: sticky` in a
  full-page screenshot. Not a defect.

## Benchmark, measured rather than remembered

Computed styles read off the live sites with Playwright.

| | interactive elements | curves | clocks |
| --- | --- | --- | --- |
| Linear | 133 | one, `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, plus `ease` on the rest | 0.1s x45, 0.16s x24 |
| Consensus | 37 | one, `ease` | 0.1s x32 |
| Elicit | 77 | `ease-in-out`, `ease` | 0.2s |

The house already runs Linear's exact curve and both of its clocks, adopted on
the 2026-09-23 benchmark. Nothing in this reading argues for a new value, and
nothing was added.

Two things worth recording.

**Elicit's bouncy hover is not on Elicit's marketing page any more.** Probing
sixty interactive elements, every hover that changed anything changed
`background-color` and nothing else. No transform, no scale, no spring, on
`transition: all` at 0.2s. The house `.pill` spring the owner approved on
2026-09-18, `cubic-bezier(0.34, 1.56, 0.64, 1)` at 190ms, is now more animated
than the site it was taken from. That is reported, not acted on: the bounce is
hers and it stays until she says otherwise.

**All three run `transition: all` or an explicit list, and only Linear uses
the list.** Linear names seven properties. Elicit and Consensus use `all`,
which is the cheap version and the one the house correctly does not use.

## The two refinements

Both are on the graph, both are before-and-after, and both came out of the
benchmark's discipline rather than its look.

**1. Hover emphasises, selection dims.** Hover and selection were one code
path, so moving the cursor over one claim greyed out the other 213
(`refinement1-hover-before.png`). That is the heaviest response in the
component fired by its lightest input, and it reverses Freiberg's order:
feedback the instant the input starts, the committed state only past a
threshold. Hover now grows the node and thickens its own edges and dims
nothing; selection keeps the ring and the dimming
(`refinement1-hover-after.png`).

**2. The legend's off state is designed rather than dimmed.** It was
`opacity: 0.4` on the whole control, which put the label near 2.9:1 against
paper and the count near 1.5:1, so the control that says which edges are
hidden was the least readable thing on the page
(`refinement2-legend-before.png`). The off state now drops the swatch to the
hairline and the label to grey, both legible, colour only, on the house
100ms clock, which is what Consensus does across its whole surface
(`refinement2-legend-after.png`).

## Checked before shipping

- **taste.md.** Black and white holds, with the one exception she granted in
  this dispatch and nothing else. The hero mark is untouched; no file under
  `components/` changed. No coming-soon page. No explanatory subtitle under a
  heading. The graph is paywalled whole, per 2026-09-19, and stays out of the
  nav.
- **ban-list.md.** Entry 7 was the old gate's blur, and it is gone. Entry 3,
  the uniform rounded-card grid: the counts row is a hairline rule, not four
  cards. Entry 13, metric tiles without a real number: the four counts are
  read from the database. Entry 19 and 23 and 24: nothing on this page waits
  at opacity 0, and the canvas has no entrance animation at all. Entry 25: no
  new curve and no new clock. Entry 26: the `select` was going to be the
  browser's, and it is styled.
- **canon.md.** Type from the scale, spacing from the 8-point grid, radius 10
  and the pill, hairlines. The one value outside the canon is the red, which
  the owner granted by name, and it has a ledger entry.
- **motion.md.** The canvas settles before its first paint and then never
  animates on a timer. A surface a subscriber works in is high-frequency and
  gets no entrance choreography, and the site's one choreographed moment stays
  the mark on the home page.

## Copy

No reader-facing prose was authored this run. The graph page's kicker,
heading, intro and gate text are the lines already in the repo, transcribed
forward from `_graph/page.jsx` unchanged. The new strings on the page are
interface labels and data readings: the four relation names come from the
`claim_links` check constraint, the evidence grades from the `claims` one, and
the counts are numbers. Two surfaces have words nobody has ruled on, flagged
here rather than drafted: the empty-panel hint and the database-unavailable
line. The writer's pricing-page claim-graph draft
(`docs/voice/reviews/2026-09-25-pricing-claim-graph.md`, PR #107) is explicitly
unapproved, so the pricing page is untouched.
