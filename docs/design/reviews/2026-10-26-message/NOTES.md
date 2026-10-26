# Frontend run, 2026-10-26 (message)

Woken by `pr.merged` on #533, which is on `main`, with the instruction to take
the next item in the lane. Pull request #546.

## Pre-flight

- Clone arrived shallow. `git rev-parse --is-shallow-repository` printed true
  and `git fetch --unshallow` ran before any comparison.
- `gh pr list --state open` carries no pull request from this seat. #533 is
  merged and #435 is closed behind it, so there is nothing to supersede and
  this branch starts from `main`. No chain, no depth to report.
- The branch name has never carried a pull request, checked with
  `--state all --limit 300`.
- Not a duplicate wake. The 2026-10-24 rule says to check whether an open pull
  request from this seat already answered the event; there is none open, and
  the event's own subject, #533, is the predecessor rather than the answer.

## What the lane said, and why this item

`python3 tools/board.py show --seat frontend`. Five backlog items, one in
progress, one in this sprint, four in review. Taken in horizon order:

| Item | Horizon | State |
|---|---|---|
| `af60726e` pricing promises a complete archive | now | Blocked. Candidate `docs/voice/pricing-claims-2026-10-18.md` is unruled, open 8 days in `docs/voice/awaiting-her-word.md` |
| `0c0bddd7` /llms.txt tells agents things no longer true | now | Blocked. Same, `llms-txt-2026-10-18.md`, and the card's own body says "once the owner rules on the candidate" |
| `f52e1e63` pricing reframed to skill-library tiers | now, this sprint | Blocked on a product decision, per the writer's comment of 2026-10-18 |
| `a1a2f14a` catalog shows nine skills not two | now, in progress | Done. The real work was shelf assignment and #533 verified it live at 54 skills |
| `67402f63` the issue in mail | next | Both halves belong to other seats: a verdict on which section-title contract is real, and `parse_section` in `pipeline/email_render.py` |
| `eb85b8d1` the page shells are three widths | later | Owner ruling. #533 measured it and put it up as a proposal |
| **`b37a342a` the issue dek's second line is a two-word widow** | **later** | **Taken. Nothing blocks it and it is entirely this seat's surface** |

Every item above `b37a342a` is waiting on somebody else's word. This one is a
measurement and a layout rule, so it is the next item this run could finish.

## The defect, measured

The dek is the standing line under an issue's title. `add_masthead` in
`pipeline/weekly.py` splices a string that is fixed in code directly under the
H1 of every issue, so its rag is not a property of a week's writing. Every
issue the archive publishes wraps it identically, which is why the card filed
it as the shape of every issue rather than a quirk of one.

Line boxes read with Range client rects down the rendered block, not estimated
from the column width.

| viewport | measure | dek lines | last line |
|---|---|---|---|
| 390 | 342px | 3 | **1 word, 86px, 25% of the measure** |
| 820 | 632px | 2 | **2 words, 118px, 19%** |
| 1440 | 632px | 2 | **2 words, 118px, 19%** |

**One correction to the card, and it reverses the trade the card was worried
about.** The card says "at 390px the dek is three full lines and has no widow,
so any rule added here must not cost the phone anything." The phone's third
line is one word at 86px of 342. It is the worst instance of the defect on the
site, not the exception to it. The phone had the most to gain.

## Judged across the generator's whole title range

The card asks for this explicitly, because a one-line headline and a
three-line headline change what reads as balanced underneath.
`ensure_fresh_title` caps a title at 120 characters, so the range is bounded
and three points cover it: the real 2026-W37 title at 28 characters, the live
2026-W39 title at 51, and a 113-character measurement string against the
ceiling. The long string is a ruler and was injected into the rendered DOM; it
is not copy and it ships nowhere.

Nine frames before, nine after, `dek-<title>-<viewport>-<before|after>.png`.

## The fix

`text-wrap: balance` on `.issue-body h1 + p`.

| viewport | last line before | last line after |
|---|---|---|
| 390 | 1 word, 86px, 25% | 4 words, 242px, **71%** |
| 820 | 2 words, 118px, 19% | 6 words, 316px, **50%** |
| 1440 | 2 words, 118px, 19% | 6 words, 316px, **50%** |

Identical in all nine cases, because the string and the measure are both
constant. The H1's own line boxes are byte-identical before and after in all
nine, which is the proof the rule reached only what it was aimed at.

**`balance` and not `pretty`, measured rather than assumed.** `pretty` is the
property whose stated job is the last-line widow, so it was the first thing
tried. At 820 and 1440 it changed nothing at all: it only moves where the last
line breaks and this sentence offers no better break. At 390 it moved one word
up and left two on the last line. `balance` evens the lines instead.

**Two things the fixture test caught that reading would not have.**

First, the selector. The intended shape test was
`:has(> em:only-child)`, read as "a paragraph that is nothing but emphasis."
Rendered against one of every paragraph shape the issue markdown can emit, it
matched prose containing an inline `<em>` as well, because `:only-child`
counts element children and ignores text nodes. CSS cannot express the test at
all. The selector that is exact is the positional one, and it is exact by
construction rather than by luck: `add_masthead` puts this block directly under
the H1 for every issue, including the short edition, where the edition note
lands after it and not before. The one body with no masthead is the
hand-committed 2026-W37, which is in `HIDDEN_WEEKS` and unreachable, and
`balance` was measured against its eight-line lead paragraph and left it
byte-identical, because Chromium does not balance past its line cap.

Second, the scope. `.digest` is the house reading type and two surfaces wear
it: the issue, and the skill file an entitled member opens in the catalogue.
Every `SKILL.md` is also an H1 followed by a paragraph, so `.digest h1 + p`
reached a surface the rule was never measured against. The issue article now
carries `.issue-body` beside `.digest`, the way the other one already carries
`.skill-body`. Verified in the browser rather than read: the issue dek computes
`text-wrap: balance` and a `.digest.skill-body` first paragraph computes
`wrap`.

## What I found and did not fix

**The headline has the same defect and the phone refuses the same cure.** The
card describes the dek as sitting under a headline that is "itself two balanced
lines." Measured, the H1 at 820 and 1440 runs 610px then 156px in a 632px
measure, so the reader met two stubs stacked in the first 60px of the page and
this run repaired the lower one. `balance` on the H1 is right in five of six
cases and a regression in the sixth: the live title at 390 goes from
297/305/156, a descending rag, to 297/172/289, which puts the short line in the
middle and reads as a dent. `h1-live-phone-plain.png` and
`h1-live-phone-balanced.png` are both committed so the call can be made from
pixels. It is a ledger proposal rather than a diff, because the honest fix is a
breakpoint on a type rule, which is a house decision and not this seat's.

## The sweep

Eleven pages at three viewports, 33 frames, at the volume the design targets:
45 DUMMY FIXTURE skills (54 total) and 50 DUMMY FIXTURE left-behind findings,
both gitignored. No horizontal overflow anywhere, no tap target under 44px.
The opacity-0 counts are the two known ones and unchanged: home's three are
scene two, which the owner ruled hidden-until-scroll, and the desk's twelve are
the hover affordance `@media (hover: none)` makes permanent on touch. The h1
left-edge table is identical to #533's, 404 on eight routes, 364 on skills, 264
on the desk, which confirms both that the shells finding is untouched and that
this run's diff moved nothing outside the issue.

The sweep frames are not committed. They reproduce #533's, which are already in
`docs/design/reviews/2026-10-26-continuation/`, and committing a second
identical set to say "still clean" is weight without evidence. The nine
before-and-after frames this run's fix rests on are here.

## Benchmark

Read live with `bench.mjs`.

| | clocks | curves |
|---|---|---|
| Elicit | 0.2s | `ease-in-out`, `ease` |
| Linear | 0.1s, 0.16s, 0.2s | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` carrying almost everything |
| Consensus | 0.1s | `ease` only |

Unchanged from #533 ninety minutes earlier, which is the expected result and
is reported rather than dressed up. Our own system read back the same way: four
clocks, three curves, and one curve on 1432 + 1352 + 1352 of the declarations.
This run invented no motion refinement to fill the slot, because the
measurement says we already sit where the benchmark sits, and the refinement it
did ship is a typographic one with before and after frames behind it.

## Registers

- **Conflict markers:** none, across `docs/`, `prompts/`, `README.md`, `site/`.
- **Scratch files:** the pull request body went to a `mktemp -d`. The sweep did
  not, and that is this run's incident, below.
- **`taste.md`:** checked entry by entry against this diff. No colour, hero
  geometry untouched, no heading subtitle, no coming-soon page, the density
  ruling not engaged because no spacing value moved.
- **`ban-list.md`:** entry 26 is the argument for the fix, a browser default
  standing where the house had written `text-wrap` for the one block it
  designed on purpose, on a tag that arrives from rendered markdown rather than
  from a component anybody designed. Entry 31 is why the rule is scoped and why
  the H1 went to the ledger instead of into the diff.
- **`canon.md`:** no value from the measurement system moved. `balance` is a
  wrapping algorithm, not a size, a space or a radius, so there is nothing to
  justify against the scale.
- **`motion.md`:** no timing, easing or transition touched, confirmed by
  reading our own system back after the change.
- **Copy:** this run changed no word a reader sees. The diff is one CSS rule
  and one `className`. So the copy pipeline and the quality-claims check have
  nothing to answer, and that is stated rather than skipped.
- **Incident appended:** the harness README teaches a fixed `/tmp` name, which
  check 0b forbids, and this run followed it.
