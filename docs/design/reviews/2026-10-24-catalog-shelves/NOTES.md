# The catalog's shelf assignment — 2026-10-24

Board item `a1a2f14a`. The card's title says the page shows two skills instead
of nine, and the PM's comment of 2026-10-18 corrects it: the page already
lists all nine, because `listSkills()` reads the skills directory rather than a
hand-written count. The comment names the real risk, which is which shelf each
of the nine lands on.

It had happened. Four of the nine stood under a heading that misdescribed
them, and the page read as correct at every viewport while doing it.

## What the shelves held, before and after

| skill | before | after |
|---|---|---|
| harness-engineering | Agent harnesses | Agent harnesses |
| recursive-harness-self-improvement | Agent harnesses | Agent harnesses |
| agent-memory-selection | Context engineering | Context engineering |
| context-window-engineering | Context engineering | Context engineering |
| self-improving-post-training-loops | Training loops | Training loops |
| **agent-security-measurement** | **Agent harnesses** | More from the library |
| **agent-containment** | **Context engineering** | More from the library |
| **skill-library-engineering** | **Context engineering** | More from the library |
| **evaluation-integrity** | **Training loops** | More from the library |

## Why it happened

`shelfFor` matched a shelf's keywords against the skill's whole `description`.
A description is written for an agent's router, so after its first sentence it
runs a long list of "use when" triggers, and a trigger names a situation the
skill is reached FOR rather than what the skill is ABOUT. Every one of the four
was filed on a word inside that trigger list:

- `agent-containment` → Context engineering, on "prompt", from "when tool
  filtering or injection detection is the proposed fix for a prompt-injection
  incident".
- `agent-security-measurement` → Agent harnesses, on "harness", from "when a
  safety harness that suits one model over-blocks another".
- `skill-library-engineering` → Context engineering, on "context", from "leaves
  the run worse than an empty context".
- `evaluation-integrity` → Training loops, on "rubric", from "a model-written
  rubric".

The PM's comment predicted a skill matching nothing would fall onto the last
shelf regardless of fit. The failure is the other way round and it is worse: a
skill matching the wrong thing lands on a NAMED shelf with every appearance of
having been put there on purpose. An unnamed catch-all declares its own
uncertainty. A wrong heading does not, which is why a reader cannot catch this
and neither could three previous visual sweeps of this page.

## The fix

Two lines of behaviour in `site/lib/skill-shelves.js`.

1. The keyword match reads the subject sentence, not the whole description.
   `splitDescription` already separates the two halves for the page, so the
   sentence to match on was already computed and thrown away.
2. `rubric` is dropped from the Training loops keywords. The shelf's other five
   words name the training loop itself. A rubric is an instrument for judging
   an output, so it appears as often in work about evaluation, and it was the
   whole reason `evaluation-integrity` stood on that shelf.

## What the fix does not fix, and is owed as words

Four of nine skills now stand on `More from the library`, which is honest and
is not organisation. The six shelves are the research program's four layers
plus the owner's 2026-09-18 coverage areas, and the library has grown past
them: it holds two skills about agent security and containment, one about
evaluation instruments, and one about the skill file itself, and no shelf
names any of those subjects. Meanwhile three named shelves read `NONE YET`.

Naming a shelf is reader-facing copy, so this seat does not write it. It is a
ledger note of 2026-10-24 instead.

The same note carries a second line. `More from the library`'s blurb reads
"Distilled and shelved, on a shelf of its own for now.", which was written when
at most one skill could land there. It now sits above four.

## Frames

Full page, 1x, three viewports.

| | before | after |
|---|---|---|
| desktop 1440x900 | `shelves-before-desktop-1440x900.png` | `shelves-after-desktop-1440x900.png` |
| iPad 820x1180 | `shelves-before-ipad-820x1180.png` | `shelves-after-ipad-820x1180.png` |
| iPhone 390x844 | `shelves-before-iphone-390x844.png` | `shelves-after-iphone-390x844.png` |
