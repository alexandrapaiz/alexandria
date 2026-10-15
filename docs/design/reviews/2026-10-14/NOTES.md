# Frontend visual review — 2026-10-14

Every page was built, screenshotted at three viewports, and looked at. The
numbers below come from measurement rather than impression, because three of
this run's candidate findings dissolved when they were measured.

## Survey (company standard L-E10)

Open pull requests at the start of this run: 298 (ExO, dispatch guards), 297
(engineer, message), 296 (PM, message), 294 (engineer, quiet-send guardrail),
293 (PM six-hour pass), 272 (ExO 2026-10-11), 205 (finance), 203 (OKR), 60
(engineer, digest quality gate). None is a frontend run and none writes under
`site/` or `docs/design/`.

Closed-PR search for overlapping visual work returned only this seat's own
merged runs: 244 (2026-10-07), 168 (2026-09-30), 108 (2026-09-26), 19
(2026-09-18). No open pull request from this seat, so this run branched from
main with nothing to supersede. Chain depth: one.

## What was verified

Ten routes at 390x844, 820x1180 and 1440x900, which is thirty frames, all of
them read. The skills library was judged at 54 entries, generated as
`skills/fixture-*` and deleted before the run finished, because the owner's
ruling of 2026-09-18 is that the library must scale to fifty.

States exercised: the scene-two reveal at rest and after scrolling at every
viewport, the morph's start and end frames, `prefers-reduced-motion`, hover
under a real `hover: none` and `pointer: coarse` profile, and a 44 by 44 hit
probe on every control.

## Four candidate findings that measurement killed

These are recorded because the next run will see the same things and should
not spend its turns the same way.

1. **The sticky nav looked like it was leaking scrolled text.** Magnified, the
   bleed is plainly legible. Measured with `ink.mjs`, the darkest pixel in the
   empty space of the bar is 252 of 255 at 390 and 247 of 255 at 1440, which
   is a ghost of one to three percent. This is the third run to nearly file
   it, so it went in the incident register and the harness README now carries
   the numbers and tells the next run to measure before filing.

2. **Thirty frames reported sub-44px touch targets.** All of them pass. The
   house extends hit areas past the drawn control with a positioned `::after`,
   which `getBoundingClientRect` cannot see. Probed properly at the four edges
   of the 44 by 44 box, zero controls miss. `shoot.mjs` was fixed to probe
   rather than measure, so this stops recurring.

3. **The three pricing cards looked like they did not bottom-align.** They do.
   All three are 706px tall and end at y=1199. The scaled screenshot misled.

4. **The home page's statement, subscribe form and about line sit at opacity 0
   at rest.** That is the owner-approved scene-two reveal, and it resolves to
   1 at all three viewports on scroll. Under `prefers-reduced-motion` all
   three are already at 1 at rest, so the reduced experience is a designed one
   rather than a broken one.

## What was fixed

**The desk's verdict queue repeated one line 426 times.** Ban list entry 22,
caught at the real count. Every row of "Awaiting your verdict" carried the
same second line naming the ledger file and the action, identical on all 426
rows, while "Recently merged" beside it is capped at eight. The list alone was
33,947px of a 39,789px page.

The row now carries the identifier and the one fact you sort by, which is the
status already in the lane badge. The page went from 39,789px to 31,676px at
desktop, and from 74,298px to 65,778px at 390. No words were added or changed.

Evidence: `fix-desk-verdict-*`.

## Two refinements

**1. The issue body's citation links answer the pointer.** Found by hovering
every interactive element on every route and diffing the computed style. Two
answered nothing. These were one of them, and they are the links that matter
most, because they are the evidence under a claim. They also arrive from
rendered markdown rather than from a component, which is the blind spot ban
list entry 26 names. They now take the same hairline wash `.skill-line`
already uses, on `--fast` and `--ease`, with `:active` carrying it on touch.

Evidence: `refine-citation-hover-*`.

**2. The pricing measure at desktop.** Three tiers inside the 632px prose
shell gave each one a 135px text column, which wrapped 11 of 12 feature lines
at 1440. "The complete archive" is 20 characters and took two lines. Meanwhile
808px of the viewport sat empty either side. The comparison block alone now
widens to 980 above 1180, on the centre axis the masthead already uses, and
the prose keeps its 632 article measure. After: 1 of 12 lines wraps, and that
one is the 72-character trial note that should. No overflow at any width, and
iPad and phone are unchanged.

Evidence: `fix-pricing-measure-*`.

## Benchmark

Read off the live pages this run rather than from memory, with `bench.mjs`.

| Site | Durations in use | Curves |
|---|---|---|
| Elicit | 0.2s | `ease-in-out`, `ease` |
| Linear | 0.1s, 0.16s, 0.2s | one dominant `cubic-bezier(0.25, 0.46, 0.45, 0.94)` |
| Consensus | 0.1s | `ease` |

The craft that transfers: all three give colour and text feedback the fastest
clock they own, and reserve the slower one for things that actually move.
Linear's single most common transition, 38 of them, is `color` at 0.1s. That
is the pattern behind both of this run's refinements, and it is why the
citation wash runs at `--fast` rather than on a slower clock that would have
felt sluggish on a link.

The same measurement turned on us returns four durations and three curves:
`--fast` 0.1s for colour, `--slow` 0.16s for movement, the owner's approved
0.19s spring on the pill, and the 0.5s page clock. That is the shape ban list
entry 25 asks for, and this run added no new value to it. Verified after the
refinements landed.

Linear's marketing page is also worth noting for a non-motion reason. Its hero
is a real product view rather than a mockup, which is the same instinct as the
positive test at the bottom of our ban list.

Evidence: `benchmark-elicit.png`, `benchmark-linear.png`, `benchmark-consensus.png`.

## Proposals, not fixed here

Three went to the ledger, two of them also to the board.

1. **The desk's verdict queue needs a cap or a filter.** 426 rows is still 426
   rows. A cap has to tell the reader the list is truncated and where the rest
   are, and that is a sentence this seat does not author. Ban list entry 21 is
   also still standing there, because the same "open" affordance appears 426
   times and every one points at the same destination.

2. **Three page shell widths make the masthead slide.** Running entry 29's own
   measurement at 1440: seven routes put the h1 at x=404, skills at 364, the
   desk at 264. The cause is `.page` at 680, `.skills-page` at 760 and `.desk`
   at 960, each centred at its own width. Each is individually defensible,
   which is what entry 29 says about this failure. It needs an owner ruling on
   whether the house anchors to a constant left rail, not a hack at the
   keyboard.

3. **The wordmark is the one nav control that answers nothing.** Its
   neighbours do, because `.nav-links a` sits at 0.85 and arrives at 1. The
   wordmark cannot copy that without dimming the brand at rest on every page,
   which is an identity change rather than polish. Left for a ruling, and this
   run stopped at its two refinements rather than taking a third.

## A note on the evidence

The desk page is 31,676px tall at desktop and 65,778px at 390 even after the
fix, so `desk-*-after.png` is cropped to the first three viewport heights
rather than shipped full page. The fix itself is evidenced separately at the
scroll position where the verdict list lives.
