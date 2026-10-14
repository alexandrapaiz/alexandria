# Consumer reports: the reviews lane

ADR-38 (owner-directed, 2026-09-29): every skill carries a `reviews/` lane, and
any session or seat that loads a skill on real work may file into it. An eval
measures whether the skill changes a model's answer on tasks this seat wrote. A
consumer report measures whether it changed a decision someone was actually in.
The two disagree often enough that we keep both, and neither substitutes for the
other.

The reports live next to the skill they judge, one file each:

```
skills/<slug>/reviews/YYYY-MM-DD-<consumer>.md
```

This directory holds the contract they share. The first report in the library,
`skills/harness-engineering/reviews/2026-09-29-ursa-chair.md`, is the worked
example, and its consumer derived the format additions of ADR-38 by hand before
the format existed.

## Frontmatter

```yaml
---
skill: <slug, matching the directory>
skill_version: <the version field of the SKILL.md that was loaded>
consumer: <who, with the model and harness, so a reader can judge transfer>
date: <YYYY-MM-DD>
task: <the real work, one sentence, concrete enough to picture>
loaded: <when in the task the skill entered context>
baseline_caveat: <what makes the without-skill comparison impure, or "none">
sections_exercised: [<section numbers or titles that bore on a decision>]
sections_confirmatory: [<sections that only confirmed a decision already made>]
decisions_changed: <integer>
procedures_adopted: <integer>
verdict: <keep active | revise | deprecation candidate, with the reason>
---
```

`decisions_changed` is the field the library is scored on, so it is the field a
report must be hardest on itself about. A section that told the consumer
something true, which the consumer was already going to do, is confirmatory and
not a decision change. Counting confirmations as changes is the one way a
report can make a useless skill look load-bearing.

## Body

Four parts, in this order.

1. **Bottom line.** Was loading it worth the context, in two or three
   sentences, with the counts.
2. **Section by section.** One entry per section of the skill, each ending in a
   verdict of exercised, confirmatory, or not exercised. Say which specific
   part carried the weight: the claim, the number, the caveat, or the
   procedure. A section that changed a decision should name the decision.
3. **What the artifact does well, as a form.** Kept separately from content,
   because this is what the other skills copy.
4. **What alexandria should improve.** Numbered proposals. These reach the
   skill agent as revision input and the ledger as proposals, so write them as
   things a seat can do, not as impressions.

## What the skill agent does with a report

Per ADR-37, maintenance before creation. A report filed since the last run is
one of the triggers that dispatch the seat, and the run reads every new one
before it picks a cluster.

- A decision-change finding becomes part of that section's *Validation:* tag,
  worded as adoption, never as a trial. Adoption is evidence that the section
  was actionable. It is not evidence that the section was right.
- A proposal becomes a revision in the next version of the skill, or a ledger
  entry saying why not.
- Several reports across different consumers showing zero decision changes make
  the skill a deprecation candidate, exactly as a regressed eval would. One
  such report is not a signal: a single consumer may simply have been doing
  work the skill does not cover, which the `task` field is there to show.

## Two things a report is not

It is not a rating. There is no score field and none should be added, because a
number that is not decisions-changed invites the skill to be tuned for
agreeableness.

It is not an endorsement the skill may quote as validation. The frontmatter
`validated` field belongs to the ADR-13 panel alone. A per-section tag citing a
report says a consumer adopted the section, with the file named so the reader
can weigh the consumer.
