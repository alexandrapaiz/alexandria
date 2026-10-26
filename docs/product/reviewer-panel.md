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

`reviewer_sha` is the other half of that pin, and it was null on every row this
job would ever have filed until 2026-10-03. The first draft asked git for it,
and the Modal image the daily job runs carries each reviewer's file without the
repository, so the only populated rows would have come from somebody's laptop.
It is the git blob sha computed from the bytes now, which needs no repository
and returns exactly what `git hash-object` returns; `tests/test_panel_adversary.py`
asserts that against all three files. The same property
`pipeline/runtime_sha.py` rests on, for the same reason: one number, computed
the same way inside the container and in a checkout.

## The slices that remain

The PM's 2026-09-28 grooming split this entry into three. All three reviewers
are built; one slice remains and it is not a reviewer.

1. **The adversary**, built 2026-10-03, `tools/panel_adversary.py`. See its
   section below: it turned out to need no model key at all, which is the one
   thing this list got wrong.
2. **The validator**, built 2026-10-03 in the same day's second window,
   `tools/panel_validator.py`. This list said it runs the A/B trial and is
   therefore blocked on a model key. **It is not, and the entry below says
   why**, which makes this the second prediction in two days that a reviewer
   would need a key and did not.
3. **The merge.** Unanimous pass merges the proposal through the server-held
   token. Blocked on the owner minting a PR-merge-scoped token, and gated by
   ADR-12's whitelist: the panel may merge `skills/`, `prompts/*.md` and
   `sources.yaml`, and never machinery. **This is now the only thing between
   ADR-13 and a working loop**, and it is the one slice no agent can unblock.

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

## Slice 3, the validator (2026-10-03, second window)

ADR-13: *"Runs the A/B trial - bare model vs. skill-loaded on held-out prompts -
and passes only if behavior moves in the direction the evidence supports."*

**It reads the trial. It does not run it, and that is the design rather than a
shortcut.** The trial exists, `tools/skill_eval.py`, written 2026-09-30 under
ADR-36: a model key, about $0.40 a skill, several minutes. The list above
concluded that this reviewer therefore waits on an infrastructure question.
Rule 1 of `docs/product/skill-validation.md` §V5 is the answer to it: *the
policy is pre-registered.* A reviewer that ran its own trial at review time
would choose the repetitions, the subject model and the threshold at review
time, which is exactly what pre-registration forbids, and it would re-run on
every review until one came back green. The trial is a dated receipt somebody
ran once under a policy fixed in advance; judging the receipt is the reviewer's
whole job.

So the key question leaves the panel. It is now "who runs `tools/skill_eval.py`,
on what schedule, under what cap", a scheduling question with no gate waiting on
it, and **the panel is complete today.** `panel_consensus` has computed its gate
as three passes on one text since the table was written, and until this file
existed the most a skill could earn was two: the arithmetic that decides a merge
was unreachable in principle rather than merely unmet.

**Four findings carry ADR-13's duty, and all four are file facts.**

1. *A trial exists.* No `evals/results.json` is `unknown`, never a pass. A suite
   with no result reads differently from no suite at all, because the two want
   different people: the first wants whoever runs the harness and the second
   wants the skill seat.
2. *The trial measured this text.* The receipt carries `skill_md_sha256`, and a
   skill edited after its eval has a result describing an earlier revision. This
   is what `panel_verdicts.target_sha` exists for, applied one level down:
   without it a skill could earn three passes, be edited, and the merge would
   ship the edit.
3. *The direction.* Not re-derived here. `tools/skill_eval.py`'s own
   `gate_problems` is this organization's one answer to "why is this result not
   a pass", shared with ADR-37's revision gate, and this reviewer calls it. Two
   copies would let the panel fail a skill the revision gate passes, which is
   the failure the adversary avoided by reading `deprecated_claims`'s 0.7
   instead of choosing a threshold. The test for it monkeypatches
   `gate_problems` and asserts the finding appears, because a test that only
   compared today's answers would stay green the day somebody reimplemented it.
4. *The policy was not tuned after the fact.* Rule 1 again, and **nothing in
   this repository checked it until now.** The suite carries the policy as
   written and the result carries the copy that ran. A delta of 0.16 misses a
   registered 0.2 and clears a 0.15 written in afterwards, so a disagreement
   between the two documents is the whole evidence. Only the keys that change
   what a number means are compared, so a suite's author note can be rewritten
   without reading as tampering.

A fifth finding is the harness's own refusal rather than a duty, labelled
`suite-runnable`: `tools/skill_eval.py`'s `conformance` is this organization's
answer to "is this eval file runnable at all", and the reviewer reads it for the
same reason it reads `gate_problems`.

**Two things the first draft of this reviewer got wrong, both found by pointing
it at the suites the skill seat has actually written** (eight files each on
#151, #152 and #159, all three open). They are recorded because the second one
is the more interesting failure mode.

First, those suites carry `suite_version: 2` and the harness speaks contract 1,
so `conformance` refuses every one of them. A reviewer that compared only
policies would have reported them as present and fine, which is why
`suite-runnable` exists.

Second, and this is the one worth remembering: they carry the two model names at
the top level and **no `policy` block at all**. The first draft compared the
result's policy against a missing one, key by key, and reported four
disagreements. That is an accusation of tampering against a file nobody
tampered with. Rule 1 names two different failures and they need two different
findings: a key the suite never wrote means the run chose it, and a key both
documents wrote differently means one was edited after the other. Only the
second is tampering. The fix also had to read the *raw* policy rather than the
normalized one, because `skill_eval.normalize` invents a repetitions default,
and a check reading it would have reported every suite in the library as
compliant with the rule it breaks.

**One finding is ADR-36's duty rather than ADR-13's**, labelled
`status-vs-eval` the way the provenance reviewer labels `spec-conformance`:
*"A skill with no eval is `status: draft`, never `active`."* Those are ADR-36
part 2's own words. All six skills on main say `status: active` and none has an
eval, so **this reviewer's first run fails the whole library**, on a rule the
owner accepted on 2026-09-29. A `draft` skill with no eval is not a finding,
which is the pair that proves the check reads the rule rather than complaining
that the library has no evals.

That is not in tension with ADR-36's other sentence, that a skill whose eval
shows no gain "is retired with the numbers, a finding rather than a failure".
The panel's `fail` means do not promote this text. ADR-36 says the response to
the numbers is retirement rather than a rewrite. Two decisions about one
measurement, and the skill seat owns the second.

**Three findings are evidence and never move a verdict**, the line the
adversary's `evidence-grade` also stays on. `trigger-firing` reports the newest
`skills/_validation/results/` receipt, its pass rate and whether it measured the
current text: the trigger test asks whether a skill fires, which is a different
question from whether it helps, and no register fixes a number for it. A
reviewer that failed a skill on it would be legislating. `eval-spend` records
`spend_usd` with its date, because the ledger already asks for skill-eval spend
in the opex table before it becomes a habit.

`section-coverage`, added 2026-10-05, reports how many of a skill's `## `
headings at least one task in its suite claims to exercise, excluding the Apply
checklist and the caveats. It is a note for a reason the suite contract states
itself: a section with no task "is what a per-section *Validation:* tag has to
say out loud (ADR-38), so it is a finding rather than an error". A reviewer that
failed a skill for it would make that tag unwritable. The other half of the same
contract rule is not a note at all. A `sections` entry naming a string that is
no heading of the file is a false claim rather than a gap, so it is a
`conformance` problem and arrives above as a `suite-runnable` fail, and
pointing it at the three open skill-seat branches is what found the defect
recorded as INC-2026-10-05-the-rewrite-staled-every-coverage-claim.

**Its file half is its whole verdict**, which is the far end of a range the other
two define. The provenance reviewer's `--files-only` runs a subset of its
checks; the adversary has no file half at all. Here the database is needed only
to write the row, and
`test_the_files_only_half_and_the_live_half_return_the_same_verdict` asserts
that rather than claiming it. A reviewer whose judgment needs no credential is
worth having in a panel where the other two do, because it is the one verdict a
pull request can see in full.

**The one thing that did not come free.** The daily job reads skills from `main`
over the GitHub API rather than from its own image, because the image is as old
as the last deploy. It wrote only `SKILL.md`. A validator pointed at an `evals/`
directory nobody wrote would report every skill unmeasured forever, in a voice
indistinguishable from the truth about a library that genuinely has no evals:
the skill seat would merge six suites and six results, the reviewer would keep
filing `unknown`, and the first person to notice would be whoever eventually
asked why a passing library never passed. That is the merged-but-inert failure
this sprint was called to close, arriving one level down.
`pipeline/skill_revision.py` now fetches the `evals/` files, one listing call
per skill, plus one more for the single trigger receipt the reviewer actually
reads out of fifteen.

**What slice 3 does not do.** It cannot tell a good eval suite from a bad one.
Every check above is about the receipt's integrity, its freshness and its
registration, and none of them can see whether the tasks hold the skill to
anything. That is deliberate and it is the reason `tools/skill_eval.py`'s
docstring insists the skill seat authors the tasks rather than the harness or
the skill's own author: cases written by the author in the same session are the
contamination the corpus warns about, and no reviewer downstream of them can
undo it.

## Slice 4, the merge (2026-10-26), and why the token was the fourth blocker

`tools/panel_merge.py`, with `tests/test_panel_merge.py`. Sprint 2026-10-26
item 1 asked for the specific gap between "the panel runs and writes a verdict"
and "a verdict merges a pull request," with nothing hand-wavy left in it. The
list above said that gap was one thing, a PR-merge-scoped token the owner has
not minted. It is four things, and the token is the last of them.

**One. Nothing had ever filed a verdict about a pull request.** All three
reviewers read skills from `main`, over the GitHub API, in step 2 of
`pipeline/skill_revision.py`. Every row in `panel_verdicts` therefore describes
text that is already merged, so `panel_consensus` could only ever be unanimous
about a proposal that no longer needed merging. ADR-13's sentence is "unanimous
pass merges the PR" and the panel could not name a PR. `--review` is the first
thing in this repository to point a reviewer at a branch: it fetches
`refs/pull/N/head`, lays the proposal's whole `skills/` tree down with `git
archive`, and calls each reviewer's own `review(skills_dir=...)` with
`conn=None`.

Those file-half verdicts inform and never decide, which is the one design
choice in this slice worth arguing. The validator's suite asserts that its two
halves return the same verdict, so a pass from its file half is a pass. The
provenance reviewer's file half runs a subset of its checks, so the same word
means something weaker and arrives as `unknown`. The adversary has no file half
at all by the decision slice 2 argues, so a proposal can never be unanimous
from a checkout. Counting any of them toward unanimity would make
`panel_verdicts` claim a duty nobody ran, and the trail is the whole point.

**Two. ADR-12's whitelist refuses every proposal the panel will ever see, and
this is measured rather than reasoned.** Across all 546 pull requests this
repository has ever held, 16 change a `skills/<slug>/SKILL.md`, and every one
of the 16 carries at least one path outside `skills/`, `prompts/*.md` and
`sources.yaml`. None is whitelist-clean, and the list is short enough to print:
16, 70, 83, 111, 136, 140, 146, 151, 152, 159, 200, 237, 290, 464, 466, 535.
The cause is not carelessness. `prompts/skill-agent.md` requires the seat to append
its ideas to `docs/ideas.md` and its repeats to `docs/agents/incidents.md` on
the same branch, so the org's own charter contract guarantees that every skill
proposal is out of scope for the gate meant to merge it. A whitelist that
refuses 16 of 16 inputs is an unreachable gate rather than a safety margin, and
the repair is the owner's: either the ledger append moves to its own pull
request, or ADR-12's whitelist admits the two append-only registers by name.
Filed in `docs/ideas.md` on 2026-10-26.

**Three. `prompts/*.md` is refused here on purpose, one step stricter than the
ADR that authorises it.** ADR-12 wrote that line on 2026-09-17, when `prompts/`
held the weekly agent's own prompt. It holds twelve seat charters today, and HQ
standard section 21 reserves a change to a seat's own authority to the owner with no
silence rule attached. An autonomous merge there would be the panel granting a
seat a right the owner never granted. So `scope_findings` reports
`charter-reserved` as its own check, separately from `machinery`, because two
different asks of the owner arriving as one finding is how the second one
becomes invisible.

**Four. The token, and the credential this file will not accept instead of
it.** The merge call reads `PANEL_MERGE_TOKEN` and nothing else. Every agent
seat on this host already holds `GH_TOKEN`, which can merge, so a fallback
would turn "the panel merged it" into "a seat merged it from inside a review
tool", which is the one thing every charter in this repository forbids. The
refusal is two tests rather than a comment, and the finding names the ambient
credential so a reader knows it was seen and declined. `do_merge` also sends
the head sha with the call, so GitHub refuses it if the branch moved between
the verdict and the merge: the same pin `target_sha` is, one level up.

### What a verdict can reach today, and the one checkbox that stops it

The item also asked for a verdict landed all the way to a CI check status on
one real pull request. That cannot be done from this seat, and the blocker is
one permission rather than a design.

Probed 2026-10-26 against the token every seat on this host holds:
`GET /repos/{repo}/commits/{sha}/statuses` returns 200, and
`POST /repos/{repo}/statuses/{sha}` returns 403, *Resource not accessible by
personal access token*. The missing grant is **Commit statuses: Read and
write** on this repository. A check run is not the way around it either: the
check-runs API is writable by a GitHub App installation and never by a personal
token, so the panel would need an App before it needed a permission.

What does reach a pull request today is the comment, and ADR-13 asks for it in
its own words: any failure "leaves the PR open with the verdicts attached."
`--comment` files the verdict and every blocking finding, labelled advisory,
and the first one is on #535 (2026-10-26). It found something the merge gate
was not looking for: both skills on that branch carry an eval suite and no
`results.json`, so the trial was written and never run.

### The remaining step, named

One autonomous merge needs all four, in this order, and three of them are
nobody's build work:

1. A whitelist a real proposal can satisfy (owner, ADR-12 amendment or a
   change to the skill seat's charter).
2. A verdict filed about a branch by the full reviewers, which needs the daily
   job to review open pull requests as well as `main`. This is build work and
   it is the next slice: `pipeline/skill_revision.py` holds the `neon` secret
   and already reads skills over the API, so pointing it at
   `refs/pull/N/head` through `panel_merge.review_proposal` is the change.
3. `PANEL_MERGE_TOKEN`, scoped to `contents: write` and `pull_requests: write`
   on this repository and held by nothing else (owner).
4. **Commit statuses: Read and write**, if the verdict is to be visible as a
   check rather than only as a comment (owner, one checkbox).
