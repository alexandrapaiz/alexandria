# Architecture, next: from newsletter-first to the mission

Owner's directive for this run (2026-09-18, dispatch instructions, binding):
the mission is fixed (vision.md §0: *Accelerate every builder to frontier
speed*) and today's architecture is preliminary, not binding. The newsletter
is how the system started, not what it is for. This document proposes how
the system grows past newsletter-first architecture toward the mission,
across three fronts the owner named directly: the pipeline as a **best-
information engine**, skills as a **first-class product line**, and **the
recursive element** — findings from our own claim graph applied back to our
own pipeline and agents, with a concrete mechanism, not a slogan.

Companion reading: [pipeline.md](pipeline.md) is the as-built presentation
(orchestration, harness, loop engineering, RAG) from two runs ago.
[source-discovery.md](source-discovery.md) designed the three discovery
signals this document builds on top of, not replaces. Nothing here
contradicts either; this document is what those two enable next.

## 0. What's actually fixed, one paragraph

Purpose, not shape. The mission is permanent; the pricing, the site, the
cron topology, and every file in this repo are means, and means get
replaced the moment a better one is evidenced. Reading the mission as
"newsletter, forever" was always a category error — vision.md §0 already
says the newsletter is the interface that keeps the human in the loop, not
the product. This document takes that literally: the product is the data
and orchestration layer; the newsletter, the skills, the claim graph API
(later), and the automations are all surfaces on top of one growing asset,
the claim graph, and the mission asks which surface serves a builder's
speed to the frontier, not which surface we happened to build first.

## 1. The pipeline as a best-information engine

**The bar, in the owner's words:** it should "reliably catch what is
genuinely gaining traction." Today's answer is three independent signals
(embedding-space novelty, rising authors/institutions, citation velocity
from an untrusted tier — source-discovery.md §3), each real, each cheap,
each still unconnected to the other and to a measurement of whether they're
actually right.

### 1.1 What's already true, stated plainly so this document doesn't repeat it

`discovery_report` (mcp/server.py) ships all three signals as one read-only
tool. `agent-weekly.yml` now runs `prompts/weekly-agent.md` on a Monday
cadence in the cloud with `NEON_RO_URL` — source-discovery.md's own Phase 1
gap ("nothing runs Step 4 on any cadence") is closed as of this run; that
document predates the workflow file that closes it. Phase 2's schema gaps
(a `category` column on `papers`, a `watchlist:` block in `sources.yaml`)
are proposed, not yet built. This document does not re-propose either; it
proposes what comes after they land.

### 1.2 One score, not three lists

Three separate signals are three separate things a human or the weekly
agent has to hold in their head and cross-reference by hand before judging
whether a candidate source is worth a `sources.yaml` diff. The fix is not
more signals — it's fusing the three into one ranked **traction-confidence
score** per candidate (paper, author, or institution), so `discovery_report`
returns a single ordered list instead of three, each row showing which
signals fired and by how much. A candidate that clears the novelty bar
*and* shows citation velocity from an untrusted tier is a stronger claim
than either alone — independent agreement across signals is exactly the
evidence bar source-discovery.md §5 already requires ("a pattern, not an
anecdote"); today that check is implicit in whoever reads three lists side
by side. Making it an explicit score is the difference between a judgment
a human does in their head and a judgment the system can defend with a
number in the PR rationale.

Ledger item: **Unified traction-confidence score for discovery_report.**

### 1.3 Measure the engine, don't just trust it

"Reliably catches" is a claim about precision, and nothing today measures
it. The fix, cheap and already in the house style (the distill bake-off,
`docs/evals/2026-09-07-distill-bakeoff.json`, is the precedent): every time
a `discovery_report` finding becomes an accepted `sources.yaml` diff via
`propose_change`, tag the `promotions` row; a few weeks later, check whether
that source's subsequent papers actually cleared triage at a materially
higher rate than the corpus baseline. A discovery signal that is right half
the time is still useful, but the number should exist, tracked the same way
OKR check-ins track everything else, so "reliably" stops being an adjective
and starts being a trendline.

Ledger item: **Discovery precision audit — track discovery→diff→outcome.**

### 1.4 The shape past Phase 3

Source-discovery.md's Phase 3 (widen the Semantic Scholar batch call for
venue centrality) is the last phase that document scoped. The next one past
it, once phases 1-3 are running and scored: institution-level trend
*forecasting*, not just detection — a rising-institution signal that has
cleared the bar three weeks running is a different, stronger claim than one
that just crossed it once. This is explicitly not scoped further here, for
the same reason source-discovery.md gave for not scoping its own Phase 3:
it changes the shape of a loop that hasn't finished proving out the simpler
version yet.

## 2. Skills as a first-class product line

The gold layer is one skill. All-hands decision 6 makes skills the current
sellable focus, and O2 (docs/okrs/okrs-2026-Q4.md) wants twelve of them,
validated, by year end. Getting from one to twelve *with the same rigor*
needs the production line's own engineering, not just more runs of the
skill agent. Four gaps, each concrete:

### 2.1 A skill's provenance is a promise, not a fact once written

`skills/harness-engineering/SKILL.md` cites claim ids 199-203, 243-244,
102-103, 136, 140, 190. Nothing today checks whether the claim graph still
agrees with those citations after the day the skill was promoted — a claim
a skill rests on can be contradicted next month by newer research, and the
skill silently keeps selling the old answer. ADR-13's adversary reviewer
catches this **at promotion time**; nothing catches it **after**. This is
the same gap ADR-8 already solved for claims (`deprecated_claims`, a
standing view, not a one-time check) and this document proposes the
identical fix for skills, reusing the exact mechanism:

```sql
-- a promoted skill needs revision when a claim it cites has since been
-- contradicted by newer evidence (deprecated_claims already computes this
-- for claims; this view is the same check joined against what skills cite)
create or replace view skills_needing_revision as
    select distinct pr.id as promotion_id, pr.path as skill_path,
           pr.claim_ids, dc.id as deprecated_claim_id, dc.claim as deprecated_claim
    from promotions pr
    cross join lateral unnest(pr.claim_ids) as cited(claim_id)
    join deprecated_claims dc on dc.id = cited.claim_id
    where pr.kind = 'skill' and pr.status = 'approved';
```

**Shipped this run** (`db/schema.sql`) — additive, `create or replace`, no
existing behavior changes. Not yet run against a live database (this
session has no `NEON_RO_URL`); the skill agent or weekly agent's next run
with database access should confirm it returns rows correctly and, once it
does, check it at the top of every skill-agent run so a flagged skill is a
finding, not a silent drift.

### 2.2 A trigger test that is narrated is not a trigger test

ADR-22 already requires five prompts (three should fire, two shouldn't) in
every skill-agent PR body. That's evidence for a human reader, not a check
that runs. The market audit this whole requirement answers to (69% of
public skills "won't reliably trigger") is exactly the failure mode a PR
description cannot catch — a description can be true the day it's written
and silently stop being true the day the skill's `description:` frontmatter
gets edited. The fix is to make the five prompts an executable fixture
(`skills/<slug>/trigger-test.json`: prompt text, expected fire/no-fire) that
a small script checks activation-condition text against, run in CI on any
change under `skills/`.

Ledger item: **Executable trigger tests, not narrated ones, in CI.**

### 2.3 Skills compose; nothing today says how

"Agent packs" (docs/ideas.md, proposed) already names the shape: a skill
plus the activation prompt that drives the whole job, sold as a distinct
SKU. The missing piece is a manifest format so a pack is a structured
artifact (skill slug, activation prompt path, version of each, the claim
ids the *pairing* itself justifies) rather than two files a human bundles
by hand each time. This is a refinement of the existing proposal, not a new
one — folded into that entry rather than re-filed.

### 2.4 The engineering discipline, named

Put together, 2.1-2.3 are the skill library's own harness: state (the
`skills_needing_revision` view) instead of re-deriving revision status from
memory, small stable checks (the trigger-test fixture) instead of one
narrated claim, and a composition format (the pack manifest) instead of
hand-bundling. This is literally the harness-engineering skill's own
discipline — small stable steps, state outside the model, verifiable
checks — applied to the thing that skill teaches about. Section 3 makes
that application a standing mechanism instead of a coincidence.

## 3. The recursive element: the self-application loop

The owner's words, verbatim: *"the big things that we research, let's
build."* Findings in our own claim graph — harness patterns, loop designs,
orchestration techniques — should change our own pipeline and agents, not
just get written up as a skill someone else loads. Today that only happens
when a human (or this daily run) happens to notice the resemblance by
reading. That's not a mechanism; it's luck. Here is one, designed to cost
nothing new to run because it reuses plumbing that already exists.

### 3.1 The mechanism

Add a step to `prompts/weekly-agent.md`'s existing Step 4 (meta-review,
already live weekly via `agent-weekly.yml`, already holds `propose_change`
authority against the ADR-12 whitelist): after gathering the week's
evidence, ask one more question of every claim cluster that produced a
skill or a strong claim this week — **does this finding, applied to
alexandria's own prompts, pipeline, or agent design, predict a concrete,
nameable change?** The evidence bar matches the one Step 4 already holds
itself to: name the specific file and the specific current practice the
claim contradicts or improves, not a resemblance. Two routes, decided by
what the change touches:

- **Judgment surface** (a prompt under `prompts/*.md`, or `sources.yaml`):
  call `propose_change` directly, exactly as Step 4 already does for any
  other meta-review finding, citing the claim ids in the rationale. No new
  authority, no new tool — the self-application finding is just another
  input to a channel that already exists.
- **Machinery** (pipeline code, schema, a new capability): write a ledger
  entry tagged `self-application`, naming the file, the claim ids, and the
  predicted change, for the engineer's next run — the same handoff every
  other machinery proposal already takes (ADR-14's division of authority:
  the panel merges knowledge, the engineer proposes machinery, human gate
  stays on code).

No new cron (Modal's five slots are still full, source-discovery.md §6),
no new MCP tool, no new secret. The only new artifact is the question
itself, added to a step that already runs and already has the authority to
act on prompt-shaped findings, and already has a ledger to hand off
code-shaped ones.

This is a **charter amendment**, not something this PR can apply directly:
`prompts/weekly-agent.md` is an agent charter, and per ADR-19 charters are
the ExO's edit surface, gated by the owner's merge like every other charter
change — this document proposes the exact text; it does not commit it.
Ledger item below carries the proposed step verbatim for the owner or the
ExO's next run to apply.

### 3.2 Three worked examples, from the one skill that already exists

Not hypothetical — every example below cites claim ids already sitting in
`skills/harness-engineering/SKILL.md`'s own provenance block, so the
mechanism is demonstrated against real material already in gold.

**Example 1 — parallel sample-and-select, applied to distill.py.** The
skill's own headline finding (claim 203, "What Else Needs Fixing?"):
best-of-three parallel samples beat sequential reflection, 2.2-9.7% accuracy
gain for less compute. `distill.py` samples once per paper today. Applied
to itself: sample distillation 2-3 times per paper on the same free-tier
model (still $0), embed each candidate's claims, and select the medoid
before writing to silver. This is a machinery change — filed as a
`self-application` ledger item below, first step a bake-off against the
current single-sample baseline, the same measured-before-shipped method
ADR-5's own model swap already used.

**Example 2 — sequential single-variable intervention, applied to the
ExO's own practice.** The skill's debugging procedure (claims 199-201,
AgentGrad): when a multi-agent system fails, change one agent at a time and
observe before touching the next. The ExO's first-run learning log
independently adopted exactly this discipline — "kept to this one change
per the first-run instruction" — without deriving it from the claim graph.
The self-application step would make that derivation explicit next time
instead of coincidental, and generalize it: a charter sweep touching
multiple seats should default to sequential rollout with an observation
window between changes, unless the evidence says the failures are
independent.

**Example 3 — minimal on-policy correction over wholesale rewrite, applied
to prompt engineering itself.** The skill's clearest negative result
(claims 199-200): imitating a stronger model's full trajectory under a
harness evolved for a weaker model made things worse by 4-30 points; the
fix that worked was fixing only the single failing turn, not rewriting
everything. Applied to how *this system's own prompts* get revised: ADR-12
meta-review diffs, and this run's own revision of `prompts/digest.md`
(§4 below), should prefer the smallest targeted edit at the exact
mechanical failure point over a wholesale rewrite. This run's digest.md
change follows that rule on purpose — it edits the prompt's specific
redundant-instruction and fixed-quota failure points, not a rewrite from a
blank page. Named here so the discipline is visible as a rule, not
recognized only after the fact.

### 3.3 Why this, and not a more ambitious version

A "self-improving pipeline" framed as a new autonomous seat, a new model
that reads the claim graph and files diffs unsupervised, would be a second
recursive loop bolted onto the one ADR-7/ADR-12/ADR-13 already built and
already gated correctly. The self-application step is deliberately the
smallest version that closes the owner's actual ask: it is one more
question inside a step that already runs weekly, already has the right
authority for judgment-surface changes, and already hands off machinery
changes to the seat built for machinery. Ambition here is in what gets
found, not in growing the org another seat.

## 4. What this run built, versus what it proposes

| Item | State |
|---|---|
| `skills_needing_revision` view (db/schema.sql) | **Built**, this PR — untested against a live database, flagged above |
| Revised `prompts/digest.md` | **Built**, this PR — see the PR description for the before/after |
| Unified traction-confidence score | **Proposed**, ledger, day-sized |
| Discovery precision audit | **Proposed**, ledger, day-sized |
| Executable trigger tests in CI | **Proposed**, ledger, day-sized |
| Agent-pack manifest format | **Proposed**, refinement of the existing "Agent packs" ledger entry |
| Self-application step (weekly-agent.md charter text) | **Proposed**, ledger, for the owner/ExO to apply — this PR cannot edit a charter |
| Self-application example 1 (sample-and-select in distill.py) | **Proposed**, ledger, day-sized, needs a bake-off first |
| Repeatable prose benchmark for the digest | **Proposed**, ledger, day-sized — see the PR description |

## 5. Day-sized ledger proposals from this document

Full entries in [docs/ideas.md](../ideas.md), appended this run:

1. Unified traction-confidence score for `discovery_report`
2. Discovery precision audit (discovery → diff → outcome)
3. Executable trigger tests for skills, checked in CI
4. Self-application step for `prompts/weekly-agent.md` (charter-text proposal)
5. Self-application example: sample-and-select bake-off for `distill.py`
6. Repeatable prose benchmark: blind read test against that week's TLDR issue

Each names its trigger, its first step, and its cost, per the ledger
contract. Board cards for the six above are added to the GitHub Projects
board this run, per the all-hands's standing self-assign authorization
(decision 8, third addendum) — flagged in the PR for the PM's Monday
reconciliation in case any needs reordering against sprint priorities.
