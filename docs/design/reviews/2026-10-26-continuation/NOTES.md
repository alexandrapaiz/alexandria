# Frontend run, 2026-10-26 (hook) — continuation

This run continues the run the provider limit cut off at turn 45 earlier the
same night. That run worked on `alexandria-frontend/2026-10-24-message-catalog-shelves`
(PR #435); its four commits are merged into this branch, this pull request
supersedes it, and #435 is closed. Second in the chain, which is not a depth
that blocks the seat.

## What I verified of the predecessor's work, live

The shelf-assignment fix is real and it holds at volume. Rendered at 54 skills,
the four skills the predecessor moved stand where it said they stand:
`agent-containment`, `agent-security-measurement`, `evaluation-integrity` and
`skill-library-engineering` are all on `More from the library`, and no named
shelf carries a skill it misdescribes. See `skills-desktop-before.png`.

The predecessor's report was accurate. I did not re-litigate it.

## The sweep

Eleven pages at three viewports, 33 frames before and 33 after, through the
committed harness rather than a hand-rolled script. Volume fixtures loaded so
the judgement is at the volume the design targets: 45 DUMMY FIXTURE skills
(54 total) and 50 DUMMY FIXTURE left-behind findings.

Audits that came back clean, each with the measurement behind it:

- **No horizontal overflow** on any page at any viewport.
- **No tap target under 44px** anywhere.
- **No content stranded at opacity 0.** The three faded blocks on the home
  page are scene two, which the owner ruled on 2026-09-19 should stay hidden
  until she scrolls, and they resolve to opacity 1 on scroll at all three
  viewports. The twelve on the desk at desktop are the `review →` hover
  affordance, which `@media (hover: none)` already makes permanent on touch.
  Ban list 23 and 24 both clear.
- **prefers-reduced-motion** renders every one of those at opacity 1 at rest.
  Canon rules 5 and 8 clear.
- **The morph holds the page still** through the whole turn (`scrollY === 0`
  at the middle and at the end, and on the phone). Geometry untouched.
- **Focus rings are a designed system, not the browser's.** Tabbed every
  interactive element on five pages with a settle wait: one house ring,
  `solid 1px #000` at 3px offset, 4px on the skill rows, 2px on inputs, and a
  white-then-black double ring on the dark pills. Ban list 26 clear.
  My first pass of this audit reported four different alphas and a
  transparent ring on two pages. That was my probe sampling mid-transition,
  because the ring animates `outline-color` over 0.1s. The numbers were an
  artifact of the measurement and not a defect, and they are recorded here
  because the next run will write the same probe.
- **The motion system is one system, not a pile of values.** Read off the
  built site: one micro curve `cubic-bezier(0.25, 0.46, 0.45, 0.94)` carrying
  2,866 of the 2,946 declarations, two micro clocks (0.1s and 0.16s), the
  approved Elicit spring `cubic-bezier(0.34, 1.56, 0.64, 1)` at 0.19s, and
  the house page-level curve at 0.5s. Ban list 25 clear, and it is the same
  discipline the benchmark found at Linear.

## What I fixed

**The routing block's measure, inside the open skill row.** One line.

`.skill-routing` was capped at `max-width: 600px`, inherited from
`.skill-row-summary` directly above it. A width is not a measure. The summary
is 17px and runs 59 characters to the line at 600, which is the canon's
target. The routing block is 14px at the same 600 and ran **84 characters to
the line**, against the canon's "at or near 65 characters, never past 75".
Now 480px and **67 characters**.

| | before | after |
|---|---|---|
| open skill row, desktop 1440x900 | [84 cpl](zoom-skills-openrow-before.png) | [67 cpl](zoom-skills-openrow-after.png) |

Measured with Range client rects down the rendered block rather than estimated
from the width. That distinction earned its place this run: my first pass
estimated `.agent-note` at over 100 characters to the line from its 712px
width and flagged it. Measured honestly it is 129 characters over two lines,
**65 cpl**, inside the canon. A fix nearly shipped against a number I had
guessed rather than read.

## What I found and did not fix, with the numbers

**`/skills` is the only route not on the house page shell.** Ban list 29's
test is to measure the h1's left edge on every route at the widest viewport
and read the numbers side by side. I ran it on ten routes:

| route | h1 left (1440) | h1 left (820) | shell |
|---|---|---|---|
| library, pricing, mission, graph, routines, issue, 404, left-behind | 404 | 94 | 680px |
| **skills** | **364** | **54** | **760px** |

`.page` is 680px. `.skills-page` overrides it to 760px, introduced by the
"Rebuild the skills library to read at fifty skills" commit with no comment
giving a reason. So moving between pages slides the masthead 40px.

I did not change it, and the reason is a measurement rather than caution. At
680 the table still works, but one of 54 names wraps to two lines, because the
name column drops from 409px to 344px:

| shell | h1 left | names wrapping | tallest row | overflow |
|---|---|---|---|---|
| 760 (today) | 364 | 0 of 54 | 50px | none |
| 680 (trial) | 404 | 1 of 54 | 75px | none |

The wrap is `fixture-15-batch-scheduling-under-latency-objectives`, 51
characters, longer than any skill in the library today. The trial frame is
[here](zoom-skills-shell680-trial.png) and it reads well: the name wraps, the
metadata holds its baseline, the columns stay declared.

Two reasons this is a proposal rather than a diff. Entry 29's test flags it
but entry 29's diagnosis does not fit, because that entry is about a shell
sized for a state most visitors never reach, and every visitor to `/skills`
reaches the table. And the 760 was chosen inside the fifty-skill rebuild, so
reversing it is reversing a deliberate decision, which wants the owner's eye
on the two frames rather than my judgement at the keyboard. Filed in the
ledger with both numbers.

**Pricing's plan row breaks out of the shell.** The h1 and prose sit in the
680 shell at x=404; the three plan cards span x=231 to 1209, 978 wide. Both
blocks are centred on the viewport, so this is the site's own centred system
rather than a misalignment, but the page steps 404 → 231 → 404 down its
length. Recorded as an observation, not a finding, because nothing is
measurably wrong and the pricing surface has open work against it.

**Two of the three pricing plans carry a dead `Opens shortly` button.** This
is taste.md's ADR-26 territory ("no coming-soon pages standing in for
something being sold") and it is the subject of an existing branch,
`alexandria-frontend/2026-10-24-message-pricing-pills`. Not reopened here.

## Benchmark

Read off the live sites with the committed `bench.mjs`.

| | clocks | curves | what it means |
|---|---|---|---|
| **Linear** | 0.1s, 0.16s, 0.2s | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` carrying almost everything | one curve, two working clocks, 38 of its transitions are `color` at 0.1s |
| **Consensus** | 0.1s only | `ease` only | the strictest of the three: one clock, one curve, no exceptions |
| **Elicit** | 0.2s | `ease-in-out`, `ease` | the bouncy feel the owner named is carried by 0.2s transform, not by a long spring |

The useful finding is that we already match this. Our micro curve is Linear's
micro curve, exactly, and our two micro clocks are Linear's two. Consensus
proves the discipline can go further still, to one clock, and our 0.1s/0.16s
split is the thing to re-examine if the owner ever wants it tighter. Elicit's
feel, which is the one she asked for, is 0.2s and a spring rather than a long
easing, and ours is 0.19s on the approved spring. Nothing here asks for a
change, which is worth saying plainly rather than inventing a refinement to
fill the slot.

Frames: `benchmark-linear.png`, `benchmark-consensus.png`, `benchmark-elicit.png`.

## Copy

This run changed no word a reader sees. The only diff to `site/` is one CSS
`max-width`. The copy pipeline and the quality-claims check therefore have
nothing to answer, and that is stated rather than skipped.

## Frames

Every page at three viewports, before and after, named `<page>-<viewport>-<tag>.png`.
Grayscale, which loses nothing on a black and white site and cut the set from
25MB to 8.3MB. The three desk frames are box-downsampled to 1/4 because that
page runs past 20,000px with fixtures loaded; every other frame is 1x.
