# The reviewer panel (ADR-13), and its first reviewer

Written by the engineer seat, 2026-10-02, with the first slice of the panel.
ADR-13 is the decision; this is the build note for it, and the place the next
two slices are specified.

## What the ADR asks for

The owner replaced the human merge gate on 2026-09-17. A skill proposal is
judged by three independent reviewer agents, each a small verifiable step with
fresh context, and it merges when all three pass. Nobody approves anything. The
audit trail is what replaces the approval: every verdict is a structured row, so
change under evidence is preserved by recording the evidence rather than by
queuing on a person.

Fifteen days later the panel did not exist, and `skills/README.md` said so in
its own words: six skills drafted, none passed by the panel, every
`provenance.validated` field empty but one. That is the gap this build starts
to close.

## What slice 1 ships

`tools/panel_provenance.py`, the provenance reviewer, and `panel_verdicts`, the
row. The reviewer reads and files; it merges nothing, because merging needs a
PR-merge-scoped token that does not exist yet (docs/sprints/pending.md item 7).

It runs in two places, for one reason: this organization holds no database
credential in CI and no model key in a test. The half that needs Neon runs daily
as step 2 of `pipeline/skill_revision.py`, which already holds the `neon` secret
and already reads every skill off `main`. The half that lives in the file is
`--files-only`, and it needs a step in `checks.yml` that this seat cannot push.

**Corrected 2026-10-03.** The paragraph above said that file half "runs on every
pull request" from the day it was written, and it never did: `checks.yml` names
no reviewer and neither reviewer's tests are in its `paths`, so 46 tests had
never been executed in CI. The queue entry that was missing is item 18 of
`docs/agents/pending-workflow-changes.md`, and the entry in the incident
register is `INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had`. It is
the second time in two days that this seat described a CI step in prose and
shipped no step, so the general shape is recorded there rather than here.

## The three duties, and which of them is decidable

ADR-13 gives this reviewer three duties. Two of them are real checks today and
one is not, and the honest report of the third is the most useful thing in this
file.

**Duty 1, every cited claim exists.** A query, and until this build nothing had
ever run it. The six skills on `main` cite 131 claim ids between them. The
reviewer also asks the question next to it, which the ADR implies rather than
states: the paper behind a cited claim has to be in the skill's own
`provenance.papers` list, because a skill that cites evidence it does not
attribute leaves a reader with no route from the page to the source.

**Duty 3, judgment that is ours is marked as ours.** The library already keeps
this convention by hand, in three phrasings, and the reviewer holds the
phrasing to that vocabulary. It normalises whitespace first, and that is not
fussiness: five of the nineteen markers in the library today are wrapped across
two lines by the prose's 80-column fill, so a reviewer built on `grep` would
report five marked passages as unmarked. What this check cannot see is a
passage that carries no marker at all, which needs a model reading the section
against the papers.

**Duty 2, the cited claim supports the sentence citing it. Not decidable
against today's format.** A skill cites its claim ids once, as a flat list in
the frontmatter, for the whole document. No section, paragraph or sentence names
the claim behind it. Twelve claim ids and six sections make seventy-two possible
pairs and the file asserts nothing about any of them, so a model asked to judge
support would be grading its own guess at the mapping first. The reviewer
reports `unknown` with both counts, which blocks the merge, because ADR-13
merges on unanimous pass and an `unknown` is not a pass.

The consequence, stated plainly: **slice 1 cannot pass any skill.** That is the
correct behaviour for an honest gate, and it is the argument for the format
change below rather than a reason to loosen the verdict.

## The format change duty 2 needs

One claim id list per section. ADR-38 already puts a one-line *Validation:* tag
under every section heading, so the natural home is there, and harness
engineering already carries four of them. A tag that also named its claim ids
would turn duty 2 from seventy-two guesses into one pair per section, and the
reviewer's model half would then have something to judge.

The format is the skill seat's surface, not the engineer's, so this is a ledger
proposal rather than a change in this build. It is filed in `docs/ideas.md`
(2026-10-02, per-section claim ids).

## One check that is not a duty

The reviewer also holds two numbers from the published Agent Skills
specification, read live at agentskills.io/specification on 2026-10-02:
`description` is capped at 1024 characters and `name` at 64, and a file past
either is rejected by a client that validates it rather than loaded with a long
description. It is labelled `spec-conformance` so nobody mistakes it for one of
ADR-13's duties, and it lives here because this reviewer is the only thing in
the repository that opens every SKILL.md on every pull request.

It is not hypothetical headroom. The library's longest description is 994
characters, 30 short of the ceiling, and ADR-38's word budget pushes that number
up with every revision.

## The row, and why it is not a column

`promotions` is the proposal and `promotions.status` is one three-way word for
it. Three reviewers produce three verdicts, each with findings and a date, so
the verdict is a child row: `panel_verdicts`, append-only, with the `findings`
jsonb the ADR's audit trail actually consists of. A re-review writes a new row
and nothing updates an old one, for the same reason `triage_log` keeps both
judgments when a rubric changes.

`target_sha` is the sha256 of the exact SKILL.md the reviewer read. It is what
makes slice 3 safe: without it, a proposal could earn three passes and then be
edited, and the merge would ship the edit. `panel_consensus` computes the gate
as arithmetic, three passes on one text, and the 3 is written out rather than
inferred from how many reviewers happened to file, because a panel of one that
passed must never read as unanimous.

## The slices that remain

The PM's 2026-09-28 grooming split this entry into three, and this build is the
first. The two that remain, with what each needs:

1. **The adversary**, built 2026-10-03, `tools/panel_adversary.py`. See the
   section below: it turned out to need no model key at all, which is the one
   thing this list got wrong.
2. **The validator.** Runs the A/B trial, which is `tools/skill_eval.py`, and
   needs a model key in the job that runs it. That is the open
   infrastructure question, and the model half of duty 2 belongs with it for
   the same reason: which job holds a key, and what the per-run cap is.
3. **The merge.** Unanimous pass merges the proposal through the server-held
   token. Blocked on the owner minting a PR-merge-scoped token, and gated by
   ADR-12's whitelist: the panel may merge `skills/`, `prompts/*.md` and
   `sources.yaml`, and never machinery.

## Slice 2, the adversary (2026-10-03)

ADR-13 gives it one sentence and the sentence is the whole specification:
*"Searches the claim graph for contradicting or refining claims the draft
ignored. If the graph disagrees with the skill, the PR fails."*

**The list above said this reviewer needs a model key. It does not, and that is
the most useful thing in this section.** ADR-10 fixes the direction of every
edge in `claim_links`: `from_claim` is always the newer, judging claim. So "a
contradicting claim the draft ignored" is a query and not a judgment. For each
id the skill cites, read the `contradicts` edges pointing at it, and ask whether
the newer claim on the other end is in the skill's own citation list. Not cited
is a `fail`, which is the ADR's second sentence. Cited is an `unknown`, because
a flat citation list cannot say whether the skill discusses the disagreement or
asserts both sides as settled, and that is the same format gap duty 2 waits on.
`refines` edges get the same arithmetic with a softer meaning, and `SEVERITY`
in the file is the one line to change if an ignored refinement should warn
rather than fail.

**It reads the organization's threshold rather than choosing one.**
`deprecated_claims` defines a contradicted claim at `confidence >= 0.7`, and
`skills_needing_revision` is that view joined against what skills cite, which is
what queues a revision in `pipeline/skill_revision.py`. A reviewer with its own
number would give the panel and the revision queue two answers to one question,
so this one reads 0.7 and files weaker contradictions as evidence.
`tests/test_panel_adversary.py` asserts that agreement against the schema text.

**The check that matters most is an `unknown`.** A cited claim whose
`interpreted_at` is null has never been judged against its neighbours, so it has
no edges, so a naive adversary finds nothing and reports a pass. That pass would
mean "the graph was never asked" while reading as "the graph agrees". Those ids
are reported `unknown` by number, which blocks the merge the way ADR-13 intends.
The claim graph has stalled twice in this product's life, so this is a live
condition: incident 24, and the 2026-09-24 curation brief that found it frozen
since 2026-09-12.

**It has no half that runs in CI, and that is a decision rather than a gap.**
Everything the provenance reviewer decides is in the SKILL.md, so `--files-only`
is a real check. Nothing the adversary decides is in the SKILL.md, because the
disagreement is a row somebody wrote after the skill was merged. A green CI step
named for this reviewer could only ever mean that nobody asked the graph, so
there is no `--files-only` here and the test suite asserts that `checks.yml`
never names the command. Its *tests* do belong in CI, and queue item 18 is where
they are asked for.

**Two checks in it are not ADR-13 duties**, labelled `evidence-breadth` and
`evidence-grade` the way the provenance reviewer labels `spec-conformance`.
`duplicates` edges between two claims a skill cites mean its list is wider than
its evidence, which the provenance reviewer cannot see because the duplication
is in the corpus rather than in the file. And `claims.evidence_grade` says what
kind of support a claim has. Both are recorded as evidence and neither moves a
verdict, because no decision in any register sets a bar for either and inventing
one in a reviewer would be the reviewer legislating.

**What slice 2 still does not do.** It cannot pass a skill whose claims the
corpus has never interpreted, and it cannot see a disagreement nobody wrote an
edge for. Both are the interpret job's health rather than this reviewer's
accuracy, which is why the `graph-searchable` finding prints the count every
time, including on a clean pass.
