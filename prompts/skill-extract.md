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
- **Not already gold.** Check `skills/` on disk, reading each existing
  SKILL.md's `provenance.claims` list, and exclude every id it names. The
  `promotions` table is the intended index for this and is empty: it
  returned zero rows on 2026-09-26 against four skills on disk, because
  nothing has ever written to it (ledger, 2026-09-26). Query it if you
  like, but the disk is the authority until the ADR-13 panel starts
  writing verdict rows.

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
region, so the edged claims and the procedure-rich claims have been close to
disjoint sets.

Run the query rather than trusting the numbers in this paragraph, because the
overlap is moving fast in the right direction and any figure written here goes
stale within the week. The series so far, each measured by the run that
recorded it in docs/ideas.md: 2026-09-22, no edge above id 221; 2026-09-26, 15
claims carrying both a procedure and an edge; 2026-09-29, 66 of 846, with the
edged frontier at id 301 and 545 claims still waiting on interpret. The ratio
is the thing to read, not the count. While it is low, working inside the edged
id range is what lets a run satisfy both criteria at once, and that is a real
constraint on which clusters are available to you.

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

## 1b. Reading the papers (ADR-35, owner's ruling 2026-09-25)

A skill written from claim rows alone is a summary of a summary, so the run
does not proceed to drafting until the cluster's papers have been read. This
section is the method; the ruling itself is in prompts/skill-agent.md.

Fetch each paper's full text yourself. arXiv HTML works and is cheap:

```bash
curl -sS -L --max-time 45 "https://arxiv.org/html/<id>" -o /tmp/<id>.html
```

A tag-stripping pass in python turns that into readable text; the five papers
of the 2026-09-26 cluster came to roughly 50,000 words in total, which is one
comfortable read, so budget for the whole cluster rather than for excerpts.
`tools/read_paper.py` does not exist yet and may when you run; check first.
Fall back to the abstract page (`/abs/`) when there is no HTML rendering, and
record that fallback as a paper you could not read in full.

Read for four things, in this order, because they are what the claim rows
cannot carry:

1. **The setup.** How many tasks, which models, which harness. Almost every
   overstatement this method catches is a number reported without its n.
2. **The ablation table.** A row that says a component helps rarely says how
   much it helps relative to the paper's other components. The 2026-09-26 run
   found a structural finding that was real, cited approvingly in our claim
   row, and the smallest of its own paper's three ablations.
3. **The baseline the comparison rests on.** Check that the baseline was
   measured the same way at the same cutoff. One claim row in that run
   reported large gains that came from a cutoff at which the baseline's
   released output was truncated, which the paper said plainly and the row
   did not.
4. **Limitations and negative results.** These are where the skill's caveats
   section comes from, and they are almost never distilled into claims.

Two rules fall out of this.

- **The paper wins.** Where the full text narrows or contradicts a claim row,
  say so in the skill in its own section, and file the row for revision in
  docs/ideas.md. Do not quietly write the narrower version and leave the row
  standing.
- **Read the references too.** Every paper this cluster is measured against
  and the library has not read goes to docs/research/reading-queue.md, with
  its arXiv id taken from the reference list of the paper you just read. The
  2026-09-26 run found that all twelve works its cluster built on were absent
  from the corpus, which no amount of querying silver would have revealed.

Say in the pull request, paper by paper, whether you read it in full or could
not, and where the reading changed what you would have written from the rows.

### A third rule, and it is measured rather than argued (2026-11-09)

- **A related-work summary is admissible as evidence that a mechanism exists
  and never as evidence of what the mechanism contains.** The components it
  omits are, measurably, the ones the summariser's own design has no slot for,
  which are also the ones a prescription built on that summary will be blind
  to. A paper's statement that it did not build something is about that paper
  and not about the field, and reading it as a field-wide claim is the same
  error in the other direction.

The number behind it, measured by the research seat on PR #926 over the nine
papers `agent-approval-paths` cites, all nine read in full: across four
enumerating related-work summaries, scored by taking each summarised paper's
components from its own design section rather than from the summary, **10 of 10
components with no counterpart in the summariser's own design were dropped**.
The converse fails, because a summary also drops things the summariser has, so
the implication runs one way only and presence in a summary carries no
information about importance. The control is the pair that makes it more than
an anecdote: two papers summarise the same third paper and keep **disjoint
halves** of it, each half matching what the summariser itself built. If the
drops tracked importance in the summarised paper, the two would agree.

The cost of not having this rule is on the record here. `agent-approval-paths`
held one of its nine papers only through a citing paper's related-work section
for weeks. The one field that summary dropped was a digest over the complete
descriptor shown to the human, the summariser has no counterpart for it, and
the skill that resulted shipped a ceiling with no precondition under it. v7
fixed the skill and v8 had to fix a second instance of the same reading in the
same file.

Two things follow for the run.

1. **A queue line for a cited-but-unread paper says which paper's description
   it rests on.** Then the next reader knows the description is a lower bound
   rather than a summary. The 2026-11-09 instance is the model: the queue line
   for the unread paper carried a characterisation from the citing paper's
   section VIII-A, the read confirmed the characterisation and refuted two
   sentences derived at queue time, and the line says which is which.
2. **Never let a related-work paragraph be the provenance for a prescription,
   and say in the skill when a prescription's source is a summary.** If the
   full text is not reachable this run, the section says so rather than
   shipping the prescription with a borrowed citation.


## 2. Drafting the skill

Frontmatter, exactly the fields the gold specimen carries and the site
parser (site/lib/content.js `parseSkill`) reads:

```yaml
---
name: <kebab-slug, matches the directory name>
description: <one paragraph, concrete trigger conditions — see "the trigger test" below>
version: 1
status: provisional   # `active` is earned on a measured positive delta (ADR-38 rule 5), never assumed
provenance:
  extracted: <YYYY-MM-DD, today>
  validated: ""   # leave empty; the ADR-13 validator fills this at promotion, never fabricate a result here
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions: []   # one LINE per revision once there are any, with the narrative in REVISIONS.md (see below)
  claims: [<every claim id the body cites, as a flat list>]
  papers:
    - "<paper title> — <arxiv or source url>"
---
```

Never write a non-empty `validated` string. The gold specimen's validated
field records a real recorded A/B trial result; that trial is the ADR-13
validator's job, not this prompt's. A draft skill ships with `validated: ""`.

**`revisions` is one line per revision, and the narrative goes in
`skills/<slug>/REVISIONS.md`.** This paragraph was added 2026-11-09 after a
measurement, and the measurement is the argument. ADR-37 puts the maintenance
record in `provenance.revisions`, one entry per revision, forever. Nothing reads
that field: `site/lib/content.js` `parseSkill` returns `name`, `description`,
`version`, `status`, `extracted`, `validated`, `claims`, `papers` and the body,
and no test, no instrument under `skills/_validation/` and no tool under
`tools/` reads `provenance.revisions` at all. Rule 4 counts it anyway, because
the cap is "including frontmatter". On `harness-engineering` the five entries had
reached 8,651 of the file's 17,602 characters, 49 percent of this library's gold
specimen, and three of them record in their own words cutting reader-facing
advice to pay for the space a revision entry took: delta 3's closing clause, the
itemised list in the last caveat, a checklist item, and four prose lines. That is
a gate deleting advice to make room for metadata about having deleted advice.

So each frontmatter entry is one line that names the date, the trigger, and what
changed, which is what ADR-37 asks the record to carry, and the full narrative
goes under a dated heading in `skills/<slug>/REVISIONS.md`. Nothing is deleted;
the text moves. The relocation on `harness-engineering` took it from 229 rendered
lines to 160 without touching a sentence of the body.

Two things that have bitten this seat and are cheap to avoid. A long quoted YAML
scalar is the shape that reached `main` unparseable on 2026-11-02, two entries
glued onto one physical line, with the registrar's own detector calling the file
clean; one-line entries make that failure small. And editing a `SKILL.md` makes
every recorded trigger receipt stale, so re-run
`python3 skills/_validation/trigger_test.py --json skills/_validation/results/<date>-<slug>.json`
and bundle it in the same commit.

`differential_screen` is not in the template above and belongs in it whenever
there is no route to an eval arm: a string saying either what the bare-arm
pre-screen measured, or why it could not run. A missing key reads as an
oversight and an honest sentence reads as the state of the world.

**And the template's `status: active` is wrong for a new skill.** ADR-38 rule 5
earns `status: active` on a positive differential delta on the benchmark subject
and nothing else, so a skill with no measurement ships `status: provisional` and
the word *unmeasured* in the PR body. Write `status: provisional` in the
frontmatter rather than writing `active` and disclaiming it in prose, because
the frontmatter is what the site renders and the PR body is not. Corrected
2026-10-06, after this file had prescribed `active` for every draft since ADR-38
landed. While there is no route to either eval arm, also fill
`provenance.differential_screen` with the reason the screen could not run.

**And `provisional` is wrong for a skill that cites no claim ids, which this
file did not say until 2026-11-02.** Two gates govern that case and only one of
them was documented here. `tests/skill-provenance.test.mjs` requires
`status: draft` when `provenance.claims` is empty, and it allows exactly ONE
such skill in the library at a time, so a second one fails the suite rather
than the gate. A seat following the paragraph above writes `provisional`, the
test fails, and nothing in this file explains why. The third gate is the one to
respect rather than route around: `tools/skill_registrar.py --files-only` fails
a zero-claim skill outright, and `tools/panel_provenance.py`
`waiting_on_the_queue` downgrades that failure to `waiting` only when all three
of these hold at once.

1. The skill says `status: draft`, so it is not published advice.
2. Its `provenance.papers` names the papers it was built from, with arXiv ids.
3. At least one of those papers is an **unchecked** `- [ ]` line in
   `docs/research/reading-queue.md` whose text names `skills/<this-slug>`.

Condition 3 is the one a run forgets, because the queue append usually happens
at step 6 and the registrar runs before it. Append the ingestion lines first and
the gate reads `waiting`; append them last and it reads `failing` for no reason
but ordering. `skills/agent-approval-paths` landed this way on 2026-11-02, and
`skills/agent-containment` on 2026-09-30 is the case the excuse path was written
for. Write `claims: []` rather than omitting the key, because an empty list is a
statement and a missing key is an oversight.

Body shape, after the specimen:

1. **Opening paragraph.** What the skill covers and why it is a delta from
   generic practice a competent engineer already has — not a restatement of
   the description field.
2. **A short "adds to, does not replace" paragraph** if the topic overlaps
   standard practice (the specimen's "This skill adds to standard
   engineering practice" paragraph). Skip it if the topic has no such
   overlap; do not force the shape.
3. **Numbered or titled sections, one per finding**, each a procedure or a
   judgment call, grounded in the cluster. Directly under each section
   heading, one italic *Validation:* line stating what has actually tested
   that section: the recorded trial that exercised it, a consumer report
   that adopted it (cite the file under the skill's `reviews/`), or "none
   yet; claim provenance only". Adoption is not validation and the line
   never blurs the two. The frontmatter `validated` field remains the
   ADR-13 panel's alone; a per-section tag never claims a trial that was
   not recorded (ADR-38). Cite claims **by paper title
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
5. **An "Apply" checklist**, placed **first, immediately after the opening
   paragraph**, with every delta below it. ADR-38 inverted this on 2026-09-30
   and this list described the old shape until 2026-10-06: a consumer who reads
   the first twenty lines and stops must have the whole procedure. It is still
   written last, because you cannot compress sections you have not drafted, and
   it still reads as item 5 of this list for that reason. The retrofitted gold
   specimen (skills/harness-engineering/SKILL.md) is the shape to copy. The
   checklist itself is the whole skill compressed
   into five to seven checkable lines a builder runs down before shipping,
   each line a question with the section it came from. Five to seven is the
   owner's number (2026-09-30), and the reason for the ceiling is that a
   checklist longer than the sections it summarises is a second skill. Every
   section of the body appears in exactly one line, so a skill with nine
   sections merges rather than adds. The first consumer report in the library
   (harness-engineering `reviews/`, 2026-09-29) derived this checklist by hand
   and said the skill should have shipped it, and every skill ships it now
   (ADR-38). A skill whose content cannot be compressed this way is describing
   findings, not procedures, and that is a cluster-selection finding to
   report.
6. **Caveats section**, always last: the source studies' scope limits
   (model sizes, task counts, sample sizes — whatever narrows how far the
   finding generalizes) and one sentence committing the skill to revision if
   a source claim is later contradicted. A caveat that names a requirement
   also names its floor: "needs an embedding model (a MiniLM-class sentence
   embedder is sufficient)" turns a hesitation into a decision, while
   "needs an embedding model" alone leaves the reader to research one
   (ADR-38).

One deliverable sits beside the body rather than inside it. **The `reviews/`
lane ships with the skill, not after its first consumer** (ADR-38, owner
directive 2026-09-30). Create `skills/<slug>/reviews/README.md` in the same
pull request as the SKILL.md. It points at the shared contract
(`skills/_validation/reviews/README.md`) and then does the one thing only the
author can do: name, in priority order, the two or three sections a report
would move most, and say why. Every section of a new skill is unvalidated on
day one, so "most wanted" means the sections whose prescriptions are marked
ours rather than the papers', the sections with the thinnest sample, and the
sections a reader is most likely to skip. The frontmatter
`provenance.reviews` list points back at the lane and carries one line per
filed report, or the placeholder line shown in the frontmatter template above
when the lane is empty. A lane created only once a report arrives never
receives one, because nothing told the consumer it existed.

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
  clauses point at the same section, delete one.

  **This is now measured rather than trusted (2026-09-30).** The rule above
  failed twice while it lived only in this file, on 2026-09-22 and again on
  2026-09-24, because you read this prompt at step 2 and write the
  description at step 3. Incident 31 records both. `trigger_test.py` now
  counts the words and warns past 150, and it records the count in every
  result bundle under `length_audit`, so the number travels with the
  receipt. You do not have to hold the budget in your head. Run the trigger
  test and read its warnings, which you were doing anyway at step 5.

  **The engine fix still has not landed, and the reason is now a measurement
  rather than a plan.** Both engines were tested on 2026-09-30 with
  candidate, prompt and topic fixed and only length varied. lexical/2.1 pays
  a candidate +0.1353 for going from 41 words to 123. lexical/3 fines it
  -0.1227 for the same change. Neither is length-invariant, so no engine
  choice available today removes this discipline from you. The proposal for
  one that would is lexical/4 in `docs/ideas.md`, and the evidence is
  `skills/_validation/results/2026-09-30-panel-v2-engine-decision.md`.
- **Put the "distinct from X" boundary sentence before the "Use when" clause,
  never after it.** `activation_clause()` takes everything from the first
  "Use when" to the end of the field and weights it 1.25, so a boundary
  sentence placed at the end injects the neighbour's vocabulary into the
  boosted span and aims your skill at exactly the prompts it was disclaiming.
- **Never write the boundary as a list of what the skill excludes.** The
  engine has no negation. "Not about human-traffic experiments or hand-written
  CI suites" puts *experiment*, *human*, *CI* and *suite* into the description,
  and the two negative cases those words came from then match harder, not
  softer. State the subject positively instead ("the subject is the instrument,
  not the system it scores") and let the excluded vocabulary stay out of the
  field entirely. Learned 2026-09-24, when writing that sentence was the first
  instinct and would have inverted the result.
- **Qualify every activation clause with the thing that makes it yours.** On
  2026-09-24 the draft's clauses said *tests*, *pass*, *fail* and *result*,
  which are the vocabulary of any flaky CI suite and any product A/B test, and
  both hard negatives fired. Rewriting the same clauses around what only this
  skill covers (a model-written rubric, the repository history as a shortcut
  channel, a checker's verdict) cleared both without touching a case. Note
  that hyphenated compounds tokenise whole, so "pass-or-fail" does not match a
  prompt's bare "pass"; that is a cheap way to keep a term you need.
- **Budget for three or four revisions of the field.** Four is what 2026-09-24
  took to reach 27 of 27: the first green version was 184 words and stole a
  case from `self-improving-post-training-loops`, and the cut to 150 words is
  what gave it back. Revising your own description is the honest response to a
  red case. Revising the case, the decoy panel, or the engine is not.
- **Report under the default engine.** `trigger_test.py --engine` can select an
  experimental scorer, and a run under anything but the pre-registered default
  prints EXPERIMENT in its header and sets `policy.pre_registered` false in its
  bundle. A pass under an experimental engine is not a pass.

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

**Record the bundle last, after the final edit to SKILL.md.** The recorded
result carries the sha256 of every skill file it judged, which is what makes it
a receipt for exactly that text, and the library page matches a receipt to a
skill by name and by that hash (site/lib/skill-provenance.js, PR #133). So a
run that records the bundle and then fixes one sentence has published a receipt
for text that no longer exists, and the page will say so. The order is: revise
the description until the suite is as green as it is going to get, make every
remaining edit to the body, then delete the bundle and re-run with `--json` as
the last thing before the commit. Re-checking costs one command:

```bash
python3 skills/_validation/trigger_test.py --json skills/_validation/results/<date>-lexical-2.1.json
python3 -c "import hashlib;print(hashlib.sha256(open('skills/<slug>/SKILL.md','rb').read()).hexdigest()[:16])"
```

and the second line must appear in the first line's bundle. Learned 2026-09-29,
where the bundle was recorded before a two-semicolon fix to the body.

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
- Never write a *Validation:* tag that reads as evidence when it is not.
  "Adopted by a consumer report" is adoption, "covered by an unrun eval task"
  is coverage, and neither is a trial. The 2026-09-30 retrofit pass found the
  reverse failure worth naming too: two skills had a section whose claim ids
  were attached to an eval task that tested none of it, which would have let a
  tag claim coverage the suite did not have. Check the task's own rubric
  criteria, not its claim list, before a tag cites it, and write the missing
  task rather than softening the tag.
- Never write outside skills/, this file, and docs/ideas.md — panel
  promotion, library rendering, and pipeline code are other seats' surface.
