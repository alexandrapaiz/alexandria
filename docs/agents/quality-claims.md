# Quality claims, and the machinery under each one

**Enforced at:** prompts/exo-agent.md §3g, every run. Artifact-side, at
prompts/writer-agent.md before any reader-facing copy ships, and at
prompts/frontend-agent.md before any copy reaches the live site.

Maintained by the ExO agent. Created 2026-09-30 on the owner's order, after
the first skill measurement.

## Why this register exists

ADR-36 was written because the site said a skill is revised when the research
moves and nothing in the organization did that. The site sentence shipped on
2026-09-18 (commit 7c714c6). The decision to build the machine came eleven
days later, on 2026-09-29, and the code for it is still on an unmerged
branch. For those eleven days the sentence was simply untrue in public, and
it is untrue today. That is not a copy defect. The writer had approval,
the frontend shipped what was approved, and the claim was plausible to
everyone who read it, because the thing it described was the thing the org
intended to build.

So the pattern has a name and it is the same shape as `recording is not
enforcing` in docs/agents/registers.md, pointed outward instead of inward:
**a public claim is a promise with a mechanism, or it is a promise with
nothing.** The org has no shortage of seats that check copy against taste,
voice, canon and the ban list. Until this file, no seat checked a claim
against the machine that would have to be true for it to hold.

One reason it went unnoticed for so long is that the claims are all true of
the *research*, which is real and cited, while what a reader buys is a claim
about *our artifact*. "The research has shown this technique to work" and
"this skill makes your agent better" are different sentences with different
evidence, and the second one is the one the product is sold on. Every row
below that is red is red on the second sentence.

## How to read the table

One row per claim a public surface makes about the quality of what we ship.
Not marketing adjectives and not mission statements. A claim is in scope when
a reasonable reader could ask "how do you know that" and expect an answer.

- **Mechanism** is the specific code, job, test or file that would have to
  run for the claim to be true. Prose in a charter is not a mechanism. A
  charter clause telling a seat to do it by hand is a mechanism only if the
  seat can actually reach the evidence, which is the capability test in
  docs/agents/unowned-duties.md.
- **State** is one of: `held` (mechanism exists, runs, and its result
  supports the claim), `unproven` (mechanism exists and has produced no
  result yet), `contradicted` (mechanism exists and its result does not
  support the claim), `not built` (no mechanism anywhere), `queued`
  (mechanism written and not merged or not deployed).
- **Measured** is the number, with the date it was measured. Empty is a
  finding on its own.

## The table, 2026-09-30

| Claim | Where | Mechanism | State | Measured |
| --- | --- | --- | --- | --- |
| "proven against the same tasks with and without it" (skills) | `site/app/mission/page.jsx:30` | `tools/skill_eval.py`, per-skill `evals/evals.json` | **contradicted** | 1 of 6 skills measured, 2026-09-30: 5.4 without against 5.3 with. The harness and five of the six suites are on unmerged branches |
| "revised when the research sharpens it" | `site/app/mission/page.jsx:31`, `site/app/llms.txt/route.js:30`, `site/app/pricing/page.jsx:35` | `pipeline/skill_revision.py` and the `skills_needing_revision` view | **queued** | 0 revisions ever fired. The view has never returned a row because `promotions` is empty. This is the precedent claim, ADR-36 |
| "retired with an explanation when it is overturned" (skills) | `site/app/mission/page.jsx:31`, `site/app/llms.txt/route.js:30` | none for the trigger. `SkillLibrary.jsx:111` renders a non-active status word | **not built** | 0 skills retired. There is no field for the explanation and nothing sets the status |
| "keeps every skill current at the pace of the research" | `site/app/skills/page.jsx:31` | same as revision, plus a freshness number that does not exist | **not built** | no skill freshness metric is computed or published anywhere. The staleness flag on the page is about the trigger-test bundle, not about the research |
| "agents that work from the current state of the evidence today and still will next month" | `site/app/skills/page.jsx:31` | a forward guarantee, so it needs the revision job deployed and a published lag | **not built** | five of six skills are at `version: 1` and none has ever been revised by a mechanism |
| "every finding is linked to the findings that support, refine, or contradict it" | `site/app/mission/page.jsx:21` | `pipeline/interpret.py`, `claim_links`, bounded by `docs/product/graph-quality.md`, audited by `tools/graph_audit.py` | **contradicted on "every"** | last measured 2026-09-29: 545 of 846 claims waiting on interpret, edged frontier at claim id 301. The mechanism is real and it covers a minority |
| "the graph shows what confirmed it, what narrowed it, and what has contradicted it" | `site/app/graph/page.jsx:28` | same as above | **contradicted on the universal reading** | same numbers. True of an edged claim and false of most claims |
| "every finding in it carries its evidence" | `site/app/page.jsx:40` | the `claims`-to-`papers` foreign key, and the provenance block on every skill | **held** | every claim row has a paper. This one is sound and worth saying plainly |
| "replaced when newer work overturns it" (findings) | `site/app/page.jsx:40` | `pipeline/weekly.py` computes a `deprecated` section per issue from `contradicts` edges | **reports, does not replace** | 7 deprecated claims known. The issue tells the reader. Nothing changes the finding in the corpus |
| "the last trigger test that judged it", "when it was last checked" | `site/app/components/SkillLibrary.jsx`, `site/lib/skill-provenance.js` | `skills/_validation/trigger_test.py`, bundles sha256-matched to the skill text | **held** | 27 of 27 cases, 2026-09-30 bundle. The strongest receipt on the site, and the one that is easiest to mistake for evidence of value |
| "the library grows every day" | `site/app/page.jsx:40` | the daily distill cron | **held** | the corpus grew to 846 claims by 2026-09-29 |

## What this table says as a whole

Eleven claims. Three hold. Two are contradicted by our own measurement. Four
have no mechanism at all. Two are waiting on code that is written and not
merged.

And the distribution is not random. **Every claim that holds is about the
corpus, and every claim that fails is about the skills.** The library's
machinery is real and measured. The product the owner decided to sell is the
one whose promises have the least under them. That is the single most useful
sentence on this page and no seat could have produced it from inside its own
lane, because the writer sees copy, the skill seat sees skills, and only a
pass over the claims together shows which half of the product is carrying
the other.

## The rule this register enforces

**A new quality claim does not ship before its mechanism is named in this
file.** Not built is an acceptable state to ship in, when the claim is
honestly hedged the way `routines/page.jsx` hedges "once they ship". What is
not acceptable is a flat present-tense claim with an empty mechanism column,
because that is the 2026-09-18 skills copy again.

Three things follow each ExO run.

1. Re-read the surfaces for claims added since the last run. `site/app/`,
   `site/app/llms.txt/route.js`, the emails under `site/emails/`, and any
   launch copy the sales seat has drafted.
2. Re-measure the numbers in the Measured column, or say which one could not
   be re-measured and why. A number with no date is the beginning of the same
   failure.
3. Move any row whose mechanism landed, and say in the learning log which
   way it moved. A row going from `queued` to `held` is the org paying a debt
   and it should be visible.

## What is deliberately not here

Mission statements and positioning. "Accelerate every builder and agent to
frontier speed" is a purpose, not a claim about an artifact, and gating it
would make this file a copy review. The test is whether a reader could ask
"how do you know" and expect a number.
