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
credential in CI and no model key in a test. So the half that lives in the file
runs on every pull request that touches `skills/**` or `db/schema.sql`, inside
the skill-receipts step of `checks.yml`, and the half that needs Neon runs daily
as step 2 of `pipeline/skill_revision.py`, which already holds the `neon` secret
and already reads every skill off `main`.

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

1. **The adversary and the validator.** The adversary searches the claim graph
   for contradicting or refining claims the draft ignored, which is
   `deprecated_claims` and the contradiction edges, and much of the arithmetic
   already exists in `tools/skill_triggers.py`. The validator runs the A/B
   trial, which is `tools/skill_eval.py`. Both need a model key in the job that
   runs them, and neither needs the merge token.
2. **The merge.** Unanimous pass merges the proposal through the server-held
   token. Blocked on the owner minting a PR-merge-scoped token, and gated by
   ADR-12's whitelist: the panel may merge `skills/`, `prompts/*.md` and
   `sources.yaml`, and never machinery.

The model half of duty 2 belongs with slice 2, because it is the same
infrastructure question: which job holds a key, and what the per-run cap is.
