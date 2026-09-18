# The design canon

This file is where the frontend seat's decisions come from. A model
asked to "make it beautiful" with no constraints regresses to the
statistical center of its training data, which is the vibe-coded look.
This canon replaces that center with specific human judgment: Apple's
measurement system as numbers, named references studied for their
decisions, and named sources for animation. The seat reads this file
every run, before designing anything. Owner adopted 2026-09-18.

## The measurement system (Apple's, adapted for the web)

These are the only numbers the seat may use. When a design needs a
value, it comes from these scales; a value outside them needs a ledger
entry explaining why.

**Type scale (px):** 12, 14, 17, 19, 21, 24, 28, 32, 40, 48, 56, 64,
80. Body text is 17 with line-height 1.47 (Apple's 25/17) and letter
spacing -0.022em. Subheads live at 19 to 28. Display lives at 40 and
up, line-height tightening toward 1.05 at 80. Small print is 12 or 14,
never 11.

**Weights:** 400 for running text, 600 for emphasis and headings, 700
only for display moments. Nothing lighter than 400 at sizes under 28.

**Spacing (px):** the 8-point grid with 4 as the half step: 4, 8, 12,
16, 24, 32, 48, 64, 96, 128. All gaps, padding, and margins come from
this list. When a space looks dense, the fix is moving up this scale,
not inventing 37.

**Measure:** running text at or near 65 characters, never past 75.
Article and statement columns cap near 692px (Apple's article
measure). Page shells cap at 980 to 1440 depending on content.

**Touch:** every tappable target is at least 44 by 44.

**Radii:** the house has two: the full pill (border-radius 980px,
Apple's own button value, already the site's pill) and small 8 to 12
for containers that genuinely need an edge. No middle radii sprinkled
per component.

**Color:** the house black and white stands above this file. #0a0a0a,
#ffffff, #86868b, #4a4a4a, #e5e5e5 and nothing else. This canon adds
no color and never will without the owner's word.

## References, and what to take from each

Study these for their decisions, never their pixels. Copying a look is
banned; understanding why a spacing works is the whole point.

- **Apple (apple.com, HIG):** restraint, whitespace as hierarchy, the
  measurement system above, one idea per scene, scroll choreography
  where the page itself is the demo.
- **Linear:** information density done right, keyboard-quality
  interactions, staggered entrances with discipline, marketing pages
  that read as product truth.
- **Stripe:** documentation-grade precision, tables and code treated
  as first-class design objects, trust built through specificity.
- **Clerk:** small states and flows, the owner's named UX benchmark.
  Empty states, loading, errors, account switching: every minor state
  designed on purpose. Take the flows, never the look.
- **Dieter Rams' ten principles and the Swiss grid (Müller-Brockmann):**
  first principles for any case no reference covers. As little design
  as possible; the grid is the default answer to layout questions.
- **Elicit:** the hover responsiveness the owner liked. Feedback that
  feels alive without being decorative.

## The animation canon

The owner wants really cool animations. Cool, for an engineering
product, means choreographed and physical, never scattered or
decorative. Where to learn from, by name:

- **Apple product pages:** the master class in scroll-driven
  choreography. One orchestrated moment per page that demonstrates the
  product, not the animator.
- **Emil Kowalski's work and writing** (Animations on the Web; the
  Sonner and Vaul libraries): the working rulebook. Animate only
  transform and opacity, use spring curves, animate from the trigger's
  origin, keep micro-interactions near 120 to 200ms.
- **Rauno Freiberg's "Invisible details of interaction design":** why
  the best animation is felt rather than noticed.
- **Linear and family.co:** entrance stagger and fluid gesture-grade
  motion at production quality.

The distilled working knowledge from Kowalski and Freiberg lives in
docs/design/motion.md; read it in full whenever a run touches motion,
hover, or gesture. The rules the seat animates under:

1. Every animation has a job: orientation (where did this come from),
   feedback (did that work), or continuity (what changed). An
   animation with no job is decoration and gets cut.
2. One choreographed moment per page at most. Everything else is
   micro: 120 to 200ms, transform and opacity only.
3. Page-level moments run 300 to 500ms on eased curves
   (cubic-bezier(0.4, 0, 0.6, 1) is the house default, Apple's own).
   Springs for anything the user touches.
4. Never animate layout properties (width, height, top, margin); the
   compositor properties (transform, opacity) or nothing.
5. prefers-reduced-motion is honored completely, always.
6. Everything visible at rest. Nothing waits at opacity 0 for an
   observer; the animated version enhances a page that already works.
7. No animation dependency enters the repo without a ledger proposal.
   CSS and the Web Animations API first; the Motion library is the
   one pre-approved candidate to propose when CSS runs out.

## Maintenance

The frontend seat may propose additions to this canon in the ledger.
Changing the measurement system or the color law is the owner's alone.
