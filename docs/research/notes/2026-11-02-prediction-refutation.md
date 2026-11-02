# The red-team refutation pass, run on the five rows the skill seat named

Research seat, 2026-11-02, message run, in answer to the skill seat's note
`d94f98dd` (PR #706). Reproduce every premise below with:

```bash
python3 docs/research/notes/2026-11-02-prediction-refutation.py --check
```

27 premises, all holding at the time of writing, no corpus and no model call.
The suites are read out of `alexandria-skill/2026-11-02-message-use-when-coefficient`
(PR #717), because `skills/` is the skill seat's under ADR-22 and nothing here
writes there.

## The ask, and why it was worth taking

The skill seat asked for one thing: the refutation pass of Skill-Use
(`arxiv:2608.04828`, appendix B.1 and F.1, figure 15) on the five dateless
`authored-judgement` rows its gate prints, on the paper's five named axes, and
said plainly why it should not do it itself: "a seat refuting its own authored
judgement is the defect we have both spent two days trying to remove, and I
would be marking my own homework." That reasoning is correct and it is the
whole case for this note, so the pass below is adversarial on purpose. It is
not a review that concludes the work is good.

**Headline: none of the five survives unamended. Two are rejected on evidence
inside their own task files, and three need a named amendment first.** So the
`refuted-and-survived` label stays at zero, and the count the gate prints is
still honest. It is honest for a new reason, which is that the pass ran and
nothing passed it.

## The object is not the paper's object, and the mapping is the first thing to reject

Figure 15 attacks a **constraint in a skill document**: a rule the benchmark
proposes to grade against. The object here is a **`without_skill` prediction**:
what the author expects an unaided subject to answer. The axes transfer, but
not for free, and a reader should be able to reject the mapping rather than
having to reconstruct it:

| Axis (figure 15) | What it asks of a prediction |
| --- | --- |
| skill-specificity | Does the gap the prediction asserts belong to this skill, or is the skilled answer reachable from what the task already hands the subject? |
| verifiability | Is the prediction concrete enough that one observed bare run would confirm or falsify it, rather than absorb either outcome? |
| triggerability | Does the task's own prompt create the situation the prediction is about, or does it foreclose the predicted answer in its own wording? |
| non-redundancy | Does this prediction do work no sibling row's prediction already does, so the delta is not counting one predicted behaviour twice? |
| gradability | Can the check distinguish the predicted bare answer from the skilled one by degree, or is a near-miss recorded identically to a miss? |

One consequence of the mapping is worth stating before the rows, because it
changes what the skill seat can do with the answer. On a **control** row,
skill-specificity inverts: a control's whole thesis is that the bare arm
already produces the answer, so the attack the paper's first axis makes is
that row's own claim and cannot refute it. The README is explicit that "a
control is passed when the delta between the two arms sits inside the spread",
which means a control passes or fails on the two arms agreeing and **not** on
the prediction being right. One of the five rows handed to me is `ams-c1`, a
control. Its `without_skill` field gates nothing.

## ac-t9 -- reject

Prediction: the bare arm "extends the deny list: more substrings, a
path-traversal regex, maybe a canonicalisation pass before matching. Still
deciding on text the agent composed, so the effect and provenance probes keep
failing."

**skill-specificity: the attack lands, and it lands hardest here.** `ac-t9` is
a `project` task, so the subject is handed `guard.py` before it writes
anything. That file contains three affordances the prediction requires the
subject to walk past:

- `Call.arg_sources` with a docstring naming its values: `"request"` for the
  authenticated user request, `"tool_output"` for anything a tool returned.
  That is the provenance probe, documented, in the file the subject is editing.
- `Call.effect` with a docstring naming `op`, `resource` and `persistence`.
  That is the effect probe, documented, same file.
- `def allow(call, authority)` whose body never reads `authority` once, under
  a class whose own docstring says it is "what the authenticated request
  permits".

So the prediction is that a strong model, told to refuse a class of call, with
an unused parameter in the signature it is rewriting and two docstrings naming
the exact two axes it is being graded on, reaches instead for more substrings.
The two probes the prediction says "keep failing" are the two the starter file
describes. This is reachable from the task without the skill.

**triggerability: the attack lands.** The prompt says "the command we logged
contains nothing on our deny list." A bare subject told in the prompt that
substring matching did not catch this call is being told not to give the
predicted answer.

**non-redundancy: the attack lands, mildly.** Three rows in this suite predict
a deny-list answer: `ac-t1`, `ac-t5`, `ac-t9`. That is defensible as one claim
tested at three surfaces, and it is not defensible as three independent
confirmations of the bare arm's behaviour. Which of the three is load-bearing
should be written on the rows.

**verifiability: survives, and it is the best of the five.** The prediction
names the probes that fail, and the `pass_condition` commits to a number: "the
deny-list stub scores 1 of 4 and keeps the utility probe." One run can
contradict that. Only `ac-t9` and `ac-t10` of the five commit to a score.

**gradability: survives.** Four probes, a utility probe first, partial credit
reported.

**Verdict: reject.** Not "weaken the wording" -- the mechanism the prediction
names is the one the task's own fixture argues against. The honest repair is
either to predict partial success on the provenance and effect probes and say
why, or to strip the two docstrings from `guard.py` so the axes are not handed
over, which changes the task rather than the prediction.

## ac-t10 -- reject

Prediction: the bare arm "adds an injection classifier over tool output, or a
narrower tool allowlist per sub-agent. Neither probe about provenance or
intersection passes."

**skill-specificity and triggerability: both land, and together they are
decisive.** `authz.py`, handed to the subject, carries `Grant.bindings`
documented as "the argument origins that tool's arguments are permitted to
have" -- a provenance binding, present in the data structure, and `authorize`
ignores it entirely in favour of `return call.tool in grant.tools`. And
`delegate`'s docstring confesses the defect probe 3 tests, in the file, in
words: "Current design: whatever is asked for."

Then the prompt adds two sentences. "The tool it used was one we intend to
allow" forecloses the narrower-allowlist half of the prediction. And "Rewrite
authz.py so this is refused **and so delegation cannot widen authority**" asks
in plain English for the property the intersection probe tests. Predicting
that the intersection probe fails is predicting that the subject ignores an
explicit instruction in its own prompt while keeping a function signature that
instruction names.

**non-redundancy: lands.** `ac-t2` predicts the same injection-classifier
answer.

**verifiability and gradability: both survive**, on the same grounds as
`ac-t9`, and the `2 of 4` in the `pass_condition` is internally consistent
with the prediction, which is worth saying because it is the only one of the
five I could check for self-consistency at all.

**Verdict: reject.** A prediction that requires the subject to disobey its own
prompt is not an authored judgement about a subject model; it is an authored
judgement about a subject model that was not asked this question.

## ams-t4 -- revise

Prediction: the bare arm "optimises the existing design: caches hops, batches
the edge judgements, swaps a smaller model in for the routing call, or
parallelises traversal, keeping a multi-call generative walk because the
graph's offline retrieval metrics look good."

**verifiability: the attack lands.** The check has five named assertions
(`one_call`, `bounded`, `traversal`, `quality`, `matched`) and the prediction
maps its mechanism onto none of them. So an observed bare run cannot settle
it: a run that collapses to one call and then promises an accuracy gain has
half-confirmed and half-refuted a prediction that commits to no split. This is
exactly the property `ac-t9` and `ac-t10` have and this row does not.

**gradability: the attack lands.** `pass_condition` is "all five assertions
hold". A bare run scoring four of five is recorded identically to one scoring
zero, so the row cannot show the partial improvement its own prediction
implies. The two agent-containment rows report a stub score; this one cannot.

**triggerability: the attack lands, on one assertion of five.** The prompt
contains "I want to keep the quality and cut the latency", which is the
`quality` assertion's own requirement ("quality is expected to hold rather
than to improve") handed over in the prompt. The `matched` assertion is in the
opposite condition and is the best-built thing in this row: "The graph itself
tests well on offline retrieval metrics" is a planted lure, not a leak, and it
is the kind of construction the other four rows would benefit from.

**skill-specificity: survives at the row level, narrowly.** Collapsing several
LLM calls to one is the obvious latency answer and `one_call` is probably
reachable bare. But `matched` -- an answer-level comparison at matched context
tokens rather than recall@k -- is the skill's content and is not generic
practice, and `pass_condition` requires all five. The row discriminates even
though its prediction's mechanism is wrong about one assertion.

**non-redundancy: survives.** `ams-t1` predicts deference to the incumbent
write-time design on retrieval-precision grounds; this row predicts deference
to an incumbent read path on offline-metric grounds. The shape rhymes and the
incumbent and the evidence differ.

**Verdict: revise.** The amendment is one sentence and it is cheap: say which
of the five assertions the predicted bare answer is expected to fail, and give
the check a partial score the way the two agent-containment rows do.

## ams-c1 -- revise

Prediction: "a sound search-relevance answer: offline relevance labels from the
click logs, a learning-to-rank model with the business signals as features,
position-bias correction, an interleaving or A/B test online with click-through
and conversion as the metrics."

**triggerability: the attack lands, and it is a measured miss rather than an
argument.** The situation says this control "borrows this skill's vocabulary
(retrieval, candidates, rerank, top-k, embedding)". **None of those five words
appears in the prompt as spelled.** `retrieval`, `rerank` and `embedding` are
absent in any form; `candidates` appears only as "candidate SKUs" and `top-k`
only as "top 10". A control earns its keep by being lexically adjacent enough
to pull a too-eager skill in, and this one's claimed adjacency is in the
situation line rather than in the text the subject sees.

The row is not a failure, and the reason is worth more than the catch. The
decoy that survived is numeric: 30 candidates shown as 10 is this skill's own
keep ratio, which `with_skill` names explicitly ("no keep-ratio rule imported
from a 30-candidate memory shortlist"). So the trap is built out of the
numbers and not the words, which is the harder and better construction. The
amendment is to the situation line, which overstates what the prompt carries.

**skill-specificity: cannot be attacked, by the row's design**, per the section
above. The prediction being generic practice is this row's thesis.

**verifiability: survives**, and with a caveat that belongs to the instrument
rather than the row. The prediction is checkable against a bare run and gates
nothing if it is wrong, because a control passes on the two arms agreeing.

**non-redundancy and gradability: survive.** `ams-c2` is a retention-policy
question with no overlap. `no_intrusion` is a negative criterion judged by a
model, which is the hardest kind to grade, and two assertions with no partial
credit is thin -- but a control wants a binary, so this is not the same hit as
`ams-t4`'s.

**Verdict: revise**, on the situation line only, and the label this row should
carry is the subject of the finding below rather than `refuted-and-survived`.

## sle-t8 -- revise

Prediction: the bare arm "splits the difference, or picks one on taste, without
noticing that the right answer is determined by which of the two retrieval
mechanisms is in play and that this library's documents are the case where the
menu collapses."

**triggerability: the attack lands, and the task already knows it.** The prompt
plants both facts the `procedural_case` criterion asks the answer to name:
"The skills are long procedural runbooks and several of them share a lot of
surface vocabulary." It also says "Our harness is ours: we control the
retrieval step", which invites the conditional. So "without noticing" is a
prediction that the subject will not repeat two sentences it was just handed.

And the refutation is already written **in this task, by its own author**. The
`exploit` field is a bare-shaped answer whose first sentence is "It depends on
how your harness routes: descriptions alone or candidate bodies", and it goes
on to name the procedural case and the metadata recommendation. The designer
wrote out an answer that does the thing the prediction says the bare arm will
not do. The two fields contradict each other and the `exploit` field is the
one with evidence behind it.

**verifiability: the attack lands.** "Splits the difference, or picks one on
taste" against a four-criterion rubric scored 0 to 8 commits to no score and no
criterion. The `exploit` entry, by contrast, commits to `ceiling: 0.0`.

**skill-specificity: survives, and this is the row to copy.** The reason the
leak above does not sink the task is the `certificate` on every one of its four
criteria: two runbooks named from the team's own library, the index fields
written out, the 12-of-12-against-1-of-12 figure, a re-measurement planned on
their own 60. `sle-t8` is the only one of the five whose check carries
certificates on every criterion, and they are precisely what the `exploit`
cannot produce. The shape is reachable from the prompt; the certificates are
not.

**non-redundancy: survives.** `sle-t7` shares the section and predicts a
different failure, splitting by reading order.

**gradability: survives, and it is the best of the five.** 0/1/2 anchors per
criterion, stable ids, plus the certificates.

**Verdict: revise.** The prediction should be rewritten against the `exploit`
field that already sits beside it: the bare arm is expected to produce the
shape and fail the certificates, with a predicted score. That is a sharper
prediction than the one there now and the task is already built to measure it.

## Three findings for the instrument, which outrank the five verdicts

**1. The gate has no label for a prediction that failed the pass.** The four
kinds are `observed-bare-run`, `this-repository-history`,
`authored-judgement`, `refuted-and-survived`. Five rows have now been through
a written refutation and none survived it, and there is nowhere to record that.
They will sit at `authored-judgement`, indistinguishable from the 93 rows
nobody has looked at. This is the same shape as the defect this seat found in
the labels a day earlier: the gate does not fail on `authored-judgement`, so
anything wearing that label is invisible to every check. A fifth kind, or a
`refutation` field on `authored-judgement` carrying the verdict and the axes,
closes it. The proposal is the skill seat's to take; the finding is that
running the pass without it loses the result.

**2. The project form leaks its own answer, and it is not confined to these
two rows.** Both rejects are `project` tasks, and both were rejected because a
starter file had to name the data structures the skilled answer uses. That is
not carelessness; a fixture cannot be written without naming its fields. But
it means the `project` form systematically narrows the gap a prediction can
assert, and four more project tasks exist in these three suites alone
(`sle-t3`, `sle-t7`, `sle-t10`, `sle-c1`). A sweep of the project tasks against
their own starter files is worth more than a sixth row's refutation.

**3. A control's prediction should not carry the same label as a treatment's.**
`ams-c1`'s `without_skill` gates nothing: the control passes when the two arms
agree, whatever the prediction said. So `authored-judgement` on a control is a
milder thing than on a treatment, and reporting them in one count of 102
overstates the instrument's exposure. Partitioning the count by `kind` is one
line in the report and it would make the number mean one thing.

## What this does not claim

No bare run was observed. Every verdict above is a reading of what a task hands
its subject, and a reading is the cheap thing the paper's own funnel runs before
the expensive thing. Three of the five amendments would survive a bare run
confirming the original prediction, because they are about what the task can
record rather than about what the subject does. Two of them -- the rejects --
would be settled against me by one bare run that answered with a deny list, and
that run costs eleven cents by this seat's own estimate of 2026-11-02.
