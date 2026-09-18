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
select c.id, c.text, c.topics, c.confidence, p.title, p.url
from claims c
join papers p on p.id = c.paper_id
where c.id not in (
  select unnest(claim_ids) from promotions where status in ('approved', 'proposed')
)
order by c.confidence desc nulls last;

select from_claim, to_claim, relation, confidence
from claim_links
where relation = 'supports'
order by confidence desc nulls last;
```

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
proves nothing; the two negatives should be the prompts most likely to
false-positive on a lazy description, not softballs.

## 4. What not to do

- Never invent a claim id, stretch a claim past its abstract, or launder a
  paper's hedge into a flat assertion. If the cluster does not support the
  sentence you want to write, do not write the sentence.
- Never fill `provenance.validated` before a real trial ran.
- One skill per run. A cluster too thin for a good skill is a ledger
  finding, not a reason to pad or to draft two thin skills instead of one
  good one.
- Never write outside skills/, this file, and docs/ideas.md — panel
  promotion, library rendering, and pipeline code are other seats' surface.
