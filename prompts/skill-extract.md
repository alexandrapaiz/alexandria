# Skill extraction — turning a claim cluster into a draft skill

You are the skill agent (prompts/skill-agent.md), at step 2 of the weekly
run, with a cluster already picked at step 1. This prompt is the method for
turning that cluster into one skills/<slug>/SKILL.md, in the shape of the
gold specimen (skills/harness-engineering/SKILL.md). Read the specimen
before drafting; it is the format contract, not just an example.

## 1. Finding and judging the cluster

Query silver with psql against `NEON_RO_URL`. A cluster is a set of `claims`
rows connected by `supports` edges in `claim_links`, usually anchored to two
or more `papers` rows so the skill is not one paper's opinion restated.

Sketch:

```sql
-- candidate clusters: claims with the most mutual support, excluding
-- anything already promoted
select c.id, c.claim, c.procedure, c.topics, p.title, p.url
from claims c
join papers p on p.id = c.paper_id
where c.id not in (
  select unnest(claim_ids) from promotions where status in ('approved', 'proposed')
)
order by c.id;

select from_claim, to_claim, relation, confidence
from claim_links
where relation = 'supports'
order by confidence desc nulls last;
```

The column is `claims.claim`, not `claims.text`, and there is no
`confidence` column on `claims` (the confidence that exists is on
`claim_links`). Check db/schema.sql before trusting any column name written
here, since this prompt restates the schema by hand and nothing keeps the two
in sync. `claims.procedure` is the field worth selecting first: it holds the
mechanism as numbered steps, which is the raw material the procedure-rich
test below is really asking about.

Group claims into clusters by shared `supports` edges and topic overlap
(`claims.topics`, `claims.embedding` for a similarity pass if the SQL alone
under- or over-groups). Score each candidate cluster:

- **Procedure-rich.** The claims describe steps, decisions, or tradeoffs a
  builder can act on, not just a finding ("X improves Y by Z%"). A cluster
  of pure benchmark deltas with no actionable procedure is thin; note it in
  the ledger and move to the next candidate rather than padding it with
  invented steps.
- **Cross-supported.** Prefer clusters spanning two or more papers over a
  single paper's claims. A single-paper cluster is acceptable only if it is
  unusually procedure-dense and no multi-paper alternative exists.
- **On-topic now.** Favor clusters matching vocabulary in the current sprint
  (docs/sprints/, newest file) or the current quarter's OKRs
  (docs/okrs/, newest file) — a skill the business needs this month beats
  one that is merely available.
- **Not already gold.** Check `skills/` on disk and `select path from
  promotions where status = 'approved'` so the run never re-extracts a
  cluster the library already carries.

Before you rank anything on `supports` edges, measure whether that criterion
can be applied at all:

```sql
select count(*) filter (where interpreted_at is null) as waiting,
       count(*) as total,
       (select max(greatest(from_claim, to_claim)) from claim_links) as max_edged_id
from claims;
```

`interpret` drains in strict id order and has run behind `distill` since at
least 2026-09-22, when 439 of 661 claims were waiting and no claim above id
221 carried a single edge (incident 23, docs/agents/incidents.md). The
`procedure` column was added to the schema after `interpret` had passed that
region, so the edged claims and the procedure-rich claims are today almost
disjoint sets: 15 claims carry both, 262 carry procedure and no edges.

When the two criteria cannot both be satisfied, procedure-rich wins and
cross-paper breadth is satisfied by topic and embedding grouping instead. Say
so at the top of the pull request, name the numbers you measured, and do not
quietly downgrade a topic cluster into an "edge-supported cluster" in the
prose. A skill drawn from six papers that agree is still well-evidenced; it
is the claim that the graph verified the agreement that would be false.

If the strongest available cluster still fails the procedure-rich test,
that is the run's finding, not a license to draft anyway. Record it in
docs/ideas.md (status `proposed`, one line: which topic is thin and why)
and stop step 2 for this run.

## 2. Drafting the skill

Frontmatter, exactly the fields the gold specimen carries and the site
parser (site/lib/content.js `parseSkill`) reads:

```yaml
---
name: <kebab-slug, matches the directory name>
description: <one paragraph, concrete trigger conditions — see "the trigger test" below>
version: 1
status: active
provenance:
  extracted: <YYYY-MM-DD, today>
  validated: ""   # leave empty; the ADR-13 validator fills this at promotion, never fabricate a result here
  claims: [<every claim id the body cites, as a flat list>]
  papers:
    - "<paper title> — <arxiv or source url>"
---
```

Never write a non-empty `validated` string. The gold specimen's validated
field records a real recorded A/B trial result; that trial is the ADR-13
validator's job, not this prompt's. A draft skill ships with `validated: ""`
and `status: active` is provisional until the panel passes it — say so in
the PR body, not in the frontmatter.

Body shape, after the specimen:

1. **Opening paragraph.** What the skill covers and why it is a delta from
   generic practice a competent engineer already has — not a restatement of
   the description field.
2. **A short "adds to, does not replace" paragraph** if the topic overlaps
   standard practice (the specimen's "This skill adds to standard
   engineering practice" paragraph). Skip it if the topic has no such
   overlap; do not force the shape.
3. **Numbered or titled sections, one per finding**, each a procedure or a
   judgment call, grounded in the cluster. Cite claims **by paper title
   inline** in prose — `(Co-Evolving Harnesses and Models)` — not by raw
   numeric id. The numeric ids belong in the frontmatter `provenance.claims`
   list only, where the provenance reviewer (ADR-13) checks each one against
   the database and confirms it actually supports the sentence citing its
   paper. This split exists because a reader wants a paper name, and a
   reviewer wants a stable id to verify against the corpus; conflating them
   in the body makes the prose unreadable and doesn't make citation more
   checkable, the provenance block already does that job.
4. **Mark unsupported judgment explicitly.** Any practical advice not
   traceable to a claim must say so inline, in the specimen's voice: "(ours,
   not the paper's)". This is the line the provenance reviewer polices
   hardest — the one sin the panel exists to catch is overstating evidence.
5. **Caveats section**, always last: the source studies' scope limits
   (model sizes, task counts, sample sizes — whatever narrows how far the
   finding generalizes) and one sentence committing the skill to revision if
   a source claim is later contradicted.

Every `provenance.claims` id must trace to at least one paper-title citation
somewhere in the body. An id in the frontmatter with no corresponding
citation is exactly the failure mode the provenance reviewer is built to
catch — check this yourself before opening the PR, the same check the panel
will run.

## 3. The trigger test

Per prompts/skill-agent.md step 3: the market evidence says 69% of public
skills never fire (docs/market/opportunities-2026-09-18.md), and the
differentiator dies if ours join them. Write `description` as concrete
activation conditions — situations and symptoms, not just a topic label
("use when an agent underperforms and the cause is unclear" beats "about
agent harnesses"). Then include in the PR, as prose the reviewer can check
in one pass:

- **Three prompts that should activate the skill**, realistic requests a
  user or another agent would actually make, each with the one phrase in
  `description` that should trigger the match.
- **Two prompts that should not**, close enough to be a plausible false
  positive (adjacent topic, similar vocabulary, different actual need),
  each with the reason the skill should stay silent.

A trigger test that only tests obviously-on and obviously-off prompts
proves nothing. The two negatives should be the prompts most likely to
false-positive on a lazy description, not softballs.

Two structural rules about the `description` field itself, learned the hard
way on 2026-09-22 when a draft took two cases away from `harness-engineering`
purely by being longer:

- **Keep it short, and treat anything past 150 words as a defect.** The
  existing library sits at 102 and 120 words; the 2026-09-22 draft reached
  170 before it was cut back to 141. The runner scores idf-weighted overlap
  with no normalisation for the candidate's own length, so a description that
  mentions more things wins more prompts, including prompts that belong to a
  neighbour. Verbosity reads as relevance to the instrument and as vagueness
  to a router. One clause per section of the body is the working test: if two
  clauses point at the same section, delete one. The engine fix is a ledger
  entry (2026-09-22); until it lands, the discipline is yours.
- **Put the "distinct from X" boundary sentence before the "Use when" clause,
  never after it.** `activation_clause()` takes everything from the first
  "Use when" to the end of the field and weights it 1.25, so a boundary
  sentence placed at the end injects the neighbour's vocabulary into the
  boosted span and aims your skill at exactly the prompts it was disclaiming.

Then write the same cases as `skills/<slug>/triggers.json` and run them.
The prose version convinces a reviewer once; the file re-runs on every
future change to any skill in the library, which is what stops a new skill
from quietly stealing an old one's prompts. The format, the decision policy,
and the runner are in `skills/_validation/` and the design behind them is in
docs/product/skill-validation.md. Two additions the executable form asks for
beyond the five prompts:

- **One confusion case per neighbouring skill**, a prompt that belongs to
  the neighbour and must route there rather than here. Write it for the
  nearest skill already in the library, not a hypothetical one.
- **`kind` on every case**, one of `positive`, `negative`, or `confusion`,
  since the report scores the three separately and a suite that passes only
  because its negatives are easy should be visible as such.

Run `python3 skills/_validation/trigger_test.py` before opening the PR and
paste the output into the PR body. A failing case is a finding worth
reporting, not a reason to soften the case until it passes. If the failure is
in an existing gold skill rather than in the draft, record it in the ledger
and leave it failing, because a validated skill is not this run's to edit.

## 4. What not to do

- Never invent a claim id, stretch a claim past its abstract, or launder a
  paper's hedge into a flat assertion. If the cluster does not support the
  sentence you want to write, do not write the sentence.
- Never fill `provenance.validated` before a real trial ran.
- One skill per run. A cluster too thin for a good skill is a ledger
  finding, not a reason to pad or to draft two thin skills instead of one
  good one.
- Never soften a trigger case, a decoy, or a decision threshold to turn a
  red suite green. The policy in `skills/_validation/` is pre-registered on
  purpose, and tuning an instrument until it flatters the artifact it
  measures is the same sin as overstating a claim.
- Never write outside skills/, this file, and docs/ideas.md — panel
  promotion, library rendering, and pipeline code are other seats' surface.
