# Frontend run, 2026-09-30 (second window)

The weekly visual sweep. Ten pages at 390x844, 820x1180 and 1440x900, every
screenshot looked at, plus the morph driven from machine to book, the scene
two reveal tested at all three viewports, hover and touch profiles separated,
a reduced motion pass, and the skills library judged at 52 entries rather than
at the six the repo holds today.

Branch: this run **builds on #154** and supersedes it. That was this seat's
earlier window today and it ended with a single six line README stub in this
directory, which is the directory this run writes. Its commit is merged in
here, so #154 can be closed rather than reviewed.

## The first thing the run got wrong, because it matters more than the fixes

The container has no Clerk instance, so the site would not boot. The run gave
it a format valid placeholder key, confirmed every route answered 200 with
curl, screenshotted all thirty combinations, and got back a perfectly clean
audit: no overflow, no clipped text, no contrast failure, no small target,
nothing at opacity 0, at any page, at any viewport.

All thirty screenshots were of a Clerk error document. `clerkMiddleware` on a
`pk_test_` key issues a dev browser handshake redirect, so the browser left
the site on every navigation and landed on a two line JSON error page. curl
never saw it because curl does not follow the redirect and the server's own
HTML was correct. The audit did not see it because a two line error page
genuinely has no overflow, no low contrast and no small targets. A clean
report was the *symptom*.

What caught it was the charter's own rule and nothing else. The run looked at
the pixels, and the pixels said Clerk. The fix was a production form key, so
the middleware treats the request as an ordinary signed out visitor and issues
no handshake, plus a Playwright route rule that blocks every request leaving
localhost.

Two lessons worth keeping. An automated pass is only evidence once something
has confirmed the page under test is the page you meant, so the harness now
fails loudly rather than reporting clean. And uniform output is a smell: all
thirty files landed within 1% of the same byte size, which is what identical
renders look like and what no real set of ten different pages ever looks like.

## Two things the pixels appeared to show and the measurements refuted

Both are recorded because the run nearly filed them as bugs.

**The nav looked transparent.** Scrolled body text appeared to read straight
through the sticky bar and collide with the wordmark, at 390 and again at
1440. Decoding the PNG and reading the actual rows says otherwise: inside the
nav band the darkest pixel over the text column is 246 to 254 out of 255,
against 0 for the nav's own links and pill and 0 for the body text one pixel
below the bar. The 0.94 white and the 22px backdrop blur are doing their job
and what is left is a ghost at about 3% ink. No defect, no change.
`nav-band-measured-iphone.png` is the frame that was measured.

**The desk looked like ban list entry 24.** The audit reported 251 elements at
opacity 0 at every viewport, which is the exact shape of the failure that
entry names. They are the `review →` affordances, which are a hover reveal,
and the stylesheet already carries an `@media (hover: none)` fallback. The
audit was wrong because headless Chromium reports `hover: hover` inside a
touch context, so every `@media (hover: none)` rule in the stylesheet was
going untested. The harness now forces `hover: none` and `pointer: coarse`
through CDP on the two touch viewports. Measured under a real touch profile
the affordances read opacity 1, and opacity 0 at rest on desktop, which is
correct in both cases.

The general point is that the seat's rule cuts both ways. A screenshot is
authority on whether something looks wrong and it is not authority on why, and
the cheap confirmation is to read the number the pixel is supposed to have.

## What was verified and found healthy

- **The scene two reveal**, which is the owner's ruling of 2026-09-19 and
  which uses `animation-timeline: view()`, the exact mechanism ban list entry
  24 names. Computed opacity at rest and after scrolling, at all three
  viewports: 0 then 1 every time. The range opens everywhere.
  `home-scene2-*.png`.
- **The morph**, driven rather than waited on. Desktop spends wheel input on
  the transformation while the page holds still, and `scrollY` stays 0 across
  the whole turn. Machine, mid and book are in
  `morph-desktop-0-machine.png` through `morph-desktop-2-book.png`. On the
  phone it autoplays on load, which is the 2026-09-19 fix, and
  `morph-start-iphone.png` and `morph-end-iphone.png` show it moving without
  any input. The geometry was not touched.
- **Reduced motion.** The home page's scene two sits at opacity 1 at rest
  under `prefers-reduced-motion`, so the reduced experience is a designed one
  rather than a broken one.
- **The skills library at 52 entries**, generated under `skills/fixture-*`
  with deliberately lumpy shapes: 1 to 20 claims, 1 to 7 papers, some
  deprecated, some unvalidated. One offer on the page rather than one per row
  (entry 21), one identifier and two facts per row at rest (entry 22), a
  designed empty state behind a filter that matches nothing, and the house
  focus ring on the filter. `skills-*-after*.png`, `skills-filter-*.png`.
- **No horizontal overflow and no element outside the viewport** at any of the
  thirty combinations.

## What was fixed

**The desk's lane badge read the branch spelling, not the seat.** Seat
branches arrive in two shapes for one seat, the short lane a local run writes
(`fe/...`) and the seat's own name from a cloud run
(`alexandria-frontend/...`). Only the first was ever looked up. Tonight that
was 15 of the 30 rows on the owner's daily page wearing an identical `OTHER`
badge, which sorts nothing and says nothing. The prefix is normalised before
the lookup now. `fix-desk-lanes-before.png` and `fix-desk-lanes-after.png`:
SEC, SALES, WRITER, FE and CHAIR stand where OTHER did.

**Three controls were under the canon's 44 by 44 touch rule.** The wordmark
is a 146x20 link inside an 83px bar, the nav links are about 20px tall, and
the footer's Privacy and Terms are 43x15 and 35x15. A finger landing a few
pixels above or below the words hit nothing, on a bar with the room to accept
it. The hit area now grows with padding and the growth is taken back out with
a negative margin. Verified layout neutral by measuring both states on the
running page: the nav at 390x83 and 1440x85, the footer's origin and height,
the wordmark, the Pricing pill and the document height are identical, and only
the hit boxes changed, 146x20 to 146x44 and 43x15 to 43x45.

## The benchmark

Elicit, Linear and Consensus, read off the live pages this run rather than
from memory. The measurement was every distinct (property, duration, easing)
triple actually computed on their hoverable elements.

| | durations in use | curves in use |
|---|---|---|
| Elicit | 0.2s | one, transform and opacity only |
| Linear | 0.1s and 0.16s | `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, plus the browser's `ease` for plain colour |
| Consensus | 0.1s | one |

This is ban list entry 25 confirmed from the outside a second time. The best
in class run their whole marketing surface on one curve and one or two clocks.
Our own tokens are already Linear's exactly, `--ease:
cubic-bezier(0.25, 0.46, 0.45, 0.94)`, `--fast: 0.1s`, `--slow: 0.16s`, which
a previous run adopted. So the benchmark's value this time was not a new idea.
It was a yardstick to audit our own drift against, and it found some.

## Two refinements, the budget for the run

**1. The disclosure panel back on the house curve.** The skill panel's
contents animated in on `0.18s cubic-bezier(0.4, 0, 0.2, 1)`, which was the
only instance of either value in 2257 lines of stylesheet, and the comment
directly above them described the curve as "ease-out". It is Material's
standard curve and it eases in. So on the surface motion.md names as high
frequency, the panel left the gate slowly, which is precisely the "sluggish"
rule 1 warns about. It now runs on `var(--slow)` and `var(--ease)`, which is
easeOutQuad and actually starts fast.

Measured on the running page, opacity by elapsed time:

| | 32ms | 48ms | 64ms | 96ms | finish |
|---|---|---|---|---|---|
| before | 0.111 | 0.308 | 0.549 | 0.837 | 180ms |
| after | 0.549 | 0.685 | 0.790 | 0.927 | 160ms |

Five times further along at the second frame, which is where snappy is
decided. `refinement1-panel-before.png` and `refinement1-panel-after.png` are
the same frame of the same animation, both frozen at 36ms.

**2. The graph's wide shell arrives with the workspace it is for.**
`.graph-page` caps at 1280 because a canvas and its panel need the room. A
visitor who is not entitled receives neither, so what everyone except a
subscriber saw was a masthead and a 480px offer card stranded at the left of
an 800px void, with the h1 at x=104 against x=404 on pricing, mission,
routines, the issue and the 404. Moving between pages slid the masthead 300px
across the screen. The gate is an article, so it now gets the article shell,
and the workspace keeps its width for the reader who has a graph to explore.
`refinement2-graphgate-before.png` and `refinement2-graphgate-after.png`.

This is the observation behind the new ban list entry 29.

## Registers

- **canon.md**: every value used is from the measurement system. No new colour,
  no new dependency, no new font. The two refinements remove a curve and a
  clock rather than adding any.
- **ban-list.md**: checked entry by entry. Entry 29 appended, from the graph
  shell. Nothing deleted.
- **taste.md**: checked entry by entry. The hero geometry, timing and
  choreography are untouched. The mission line is unchanged. No colour. The
  graph stays paywalled with no preview and unlisted in the nav. Density was
  added rather than removed. No copy was written by this seat.
- **motion.md**: the disclosure refinement is rule 1 applied directly, and the
  high frequency guidance is why the panel's job is feedback rather than
  ceremony. `prefers-reduced-motion` already cancels that animation and was
  re-verified.
- **Copy**: no reader facing words were invented, changed or moved. The one
  copy adjacent finding is in the ledger as a question for the writer, not as
  a sentence written here.

## Left undone, deliberately

The `#86868b` house grey computes to 3.62:1 on white, which is below WCAG AA's
4.5 for text under 24px, and it carries most of the running prose on the site.
That is 823 strings on the skills page alone at 52 entries. The palette is the
owner's alone under the canon, so this is a ledger proposal and not a change.

The masthead still starts at three different x positions across the remaining
shells, 404 on most pages, 364 on skills and 264 on the desk. Both of those
shells have a real reason to be wider. Making the masthead hold one left edge
while the content below widens is a design decision rather than a bug fix, so
it is in the ledger.
