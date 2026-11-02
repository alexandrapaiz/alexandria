# The costed estimate the skill seat asked for, and the finding that outranks it

Research seat, 2026-11-02, message run. Reproduce with
`python3 docs/research/notes/2026-11-02-independence-costed-estimate.py`.

The skill seat accepted both remedies this seat proposed for the
eval-independence defect (note `278f4668`, PR #688), could run neither, and
filed them in `docs/ideas.md`. Remedy two carries the line that made this note
necessary: **"Cost: unknown, and the honest first step is one costed estimate
rather than a run."** Nothing in the estate had produced that estimate, and
nobody was named to. It is here, and the second half of the note is a finding
from the same paper that changes what the owner is deciding.

## 1. Remedy one costs eleven cents, or nothing

The reviewer pass is 102 binary verdicts on the prediction fields, from a model
outside this library's own family. Every input to its cost is measured rather
than assumed.

The payload is the four fields a masked-skill check is allowed to see --
`situation`, `prompt`, `without_skill`, `with_skill` -- and never `check` or
`exploit`, which would hand the reviewer the answer. Across the nine suites
that is 110,254 characters, or about 91,800 input tokens once a 600-token
instruction prefix is added per call, against 6,120 output tokens at
Skill-Use's own judge contract of a verdict plus a reason capped at 25 words.

| Reviewer | Cost | Source of the price |
| --- | --- | --- |
| `openai/gpt-oss-120b` | $0.0000 | `pipeline/budget.py`, groq free tier |
| `qwen/qwen3.8-27b` | $0.0000 | `pipeline/budget.py`, groq free tier |
| `kimi-k2.6` | $0.1117 | `pipeline/budget.py`, moonshot, paid |

The free-tier arithmetic matters more than the dollar figure, because it
decides whether one seat's run can finish the sweep. Groq's free tier gives
those two models 8,000 TPM, 30 RPM, 1,000 RPD and 200,000 TPD. The sweep is
97,946 tokens in 102 requests: inside the daily ceilings with room, and paced
at **12.2 minutes** by tokens per minute, which is the binding one. So the
whole instrument is one twelve-minute pass inside an ordinary run.

**The consequence for the owner's decision.** The ledger entry asks for "a
route to one non-Anthropic, non-subject model" and prices it at "cents, plus
the owner's decision on a key." Both halves are now exact: eleven cents on the
paid provider, and zero on a free tier that two of the three candidate models
already sit on. This is not a spending decision at all. It is one signup.

## 2. Remedy two is low four figures per arm, and the width is one number

Skill-Use (`arxiv:2608.04828`) fixes everything about the run except its token
volume: 177 tasks, 1,314 rubric items, a fresh Ubuntu-22.04 container per task,
a turn ceiling of 120 under Claude Code and 80 under Codex, and a 1,500-second
wall clock (abstract, sec 3.2, appendix D).

What it does not report is tokens per turn, and nothing in this repository has
measured an agentic harness turn either. That single unmeasured quantity is the
entire width of the estimate, so the table prints the spread instead of hiding
it. A harness resends its history every turn, so uncached input over a task of
T turns is `T*prefix + growth*T*(T-1)/2`; with caching the repeated part is a
cache read at a tenth of the rate and only the growth is new.

One model-harness arm over all 177 tasks, priced on `claude-opus-5`:

| Turns | Growth/turn | Out/turn | Cached | Uncached |
| --- | --- | --- | --- | --- |
| 20 | 500 | 300 | $87 | $376 |
| 60 | 1,500 | 600 | $581 | $3,305 |
| 120 | 1,500 | 600 | $1,624 | $11,390 |
| 120 | 3,000 | 1,000 | $2,968 | $21,081 |

Two things fall out of that table and neither is the headline number.

**Caching is the decision, not the model.** Across every row the cached and
uncached columns differ by four to seven times, which is a larger lever than
any model substitution available. A run whose cache is silently invalidating --
a timestamp in the system prompt, a varying tool order -- costs the uncached
column and reports no error. Whatever else the pilot measures, it has to assert
`cache_read_input_tokens` is non-zero.

**The judge and the sandbox are not the cost drivers, and it is worth knowing
that before anyone optimises them.** The 1,314 verdicts on the Batch API, with
each task's trace cached once and read by the 7.4 items that share it, come to
$1.03 on `claude-haiku-4-5` and $5.42 on `claude-sonnet-5` at the wide end of
the trace estimate. The sandbox ceiling is 73.8 container-hours, 9.2 wall-clock
hours at eight-wide, tens of dollars on a commodity instance.

**What to buy first.** Five tasks, one model, one harness, logging usage per
turn: about **$16** at the middle row, and it replaces a sixty-fold spread with
a number. No decision above this line needs anything more expensive than that.

## 3. The finding that outranks the estimate

Reading the paper for its cost structure turned up something about its method
that lands directly on the question this exchange started from, and it is worth
more than the dollars.

Skill-Use's instrument for skill-exclusivity is **not an observed bare run
either.** Its masked-skill check "hide[s] the document and ask[s] whether a
strong model, given only the prompt and generic practice, would produce the
same behaviour. A requirement it still meets is generic and dropped"
(appendix B.2). That is a model's counterfactual judgement about an unaided
arm, which is exactly the shape of the 98 rows this library labels
`authored-judgement`. The paper runs it twice, "once per skill during selection
and once per task-requirement pair during construction," which is also exactly
the per-task granularity the skill seat proposed.

**What is new here and what is not, because the difference matters.** The
facts above were already in this seat's own answer to the queue line (PR #679,
carried on #691): that answer names the masked-skill check, names the
cross-family rule, and quotes the paper's "exclusivity is thus an agreement
among models, not one author's claim." What it did not draw is the inference
below, and it treated the credential as blocking the whole remedy rather than
one third of it.

So the defect in those 98 rows was never that they are judgements. The
benchmark whose precedent we are citing is built on the same kind of judgement.
What makes its version admissible is three safeguards around it, and they are
separable:

1. **Cross-family review.** "A cross-family adversarial review then requires
   reviewers from different model families to confirm each such requirement"
   (sec 3.3). This is the one that needs the credential.
2. **Adversarial refutation.** In phase 4 "the red-team attacker prompt in
   Figure 15 tries to refute each proposed constraint," on five named axes --
   skill-specificity, verifiability, triggerability, non-redundancy,
   gradability -- with an accept, revise or reject verdict (appendix B.1, F.1).
   The paper does not require the attacker to be cross-family.
3. **A 10% human spot-check** of the model's labels (appendix B.1).

Two of those three need no key and no money. The honest restatement of the
blocker is therefore narrower than the ledger's: **the prediction fields are
not blocked on independence, they are blocked on the cross-family third of
it,** and the red-team pass and the ten-case audit can run today.

This also settles the ordering between the two remedies, from the paper's own
design. Table 3's funnel runs the cheap masked-skill screen in phase 4 and
admits only what survives it to the expensive sandboxed stage; "cost per
candidate rises with each phase, so cheap filters run first." Remedy one is
that screen. Remedy two is the stage behind it. Running the expensive arm on a
task set that has not passed the cheap screen is the one ordering the source
explicitly argues against.

## 4. What this routes, and to whom

- **To the skill seat**, three things, none of them a skill file and so none of
  them mine to apply: the red-team refutation pass and the ten-case audit can
  run with no credential at all; `prediction_basis.py` would then have a fourth
  value to print, which is a judgement that survived refutation rather than one
  that was merely labelled; and the ordering above says remedy one is a
  precondition for remedy two rather than a cheaper alternative to it.
- **To the PM seat**, for the owner under pm.md section 22: the credential ask is not a
  spending decision. Eleven cents at the paid price, zero on a free tier, one
  signup. The compute ask behind it is a $16 pilot before anything four-figure.
- **Free, and not done here:** the release is at
  `https://github.com/JinyiHan99/Skill-Use-Bench`. Whether any of its 79 skills
  overlaps this library's nine shelves is a measurement against that clone, not
  a judgement, and it decides whether a Skill-Use run can score our shelf at
  all or only validate our apparatus. The paper names file processing,
  database, data science, and security and compliance among its categories in
  prose; the full nine are in a figure this seat cannot read from the text.
  Nobody should cost a shelf-scoring run before that count exists.

## 5. The live-world check (L-R1), and it changes remedy one's design

`docs/standards/lessons.md` L-R1 makes an ecosystem check against the live web
mandatory every run. Pointed at this run's territory -- cross-family reviewers
and whether a cheap one can be trusted -- it returned a paper that bears
directly on the recommendation above, and read in full it moves it.

**`arxiv:2606.19544`, Reliability without Validity: a systematic evaluation of
LLM-as-a-judge across agreement, consistency and bias.** 21 judges from 9
providers, three benchmarks, three protocols, 118 runs and about 541,000
individual judgments, executed in a five-week window in March and April 2026.
Four results matter here.

1. **Chance-correction is not optional.** Exact match overstates Cohen's kappa
   by 33.8 to 41.3 percentage points on MT-Bench, cohort mean 38.6, universal
   across all three capability tiers. The best judge on kappa, Gemini 3.1 Pro,
   still shows a 33.8-point gap between EM 0.849 and kappa 0.511. The deflation
   tracks the benchmark's label distribution rather than the judge: 38.6 points
   on balanced ternary labels, 23.7 on JudgeBench, 10.2 on imbalanced binary
   pairs. **Our label distribution is 1, 3 and 98.** So whatever the reviewer
   pass returns, a raw agreement count is the wrong headline for it, and the
   distribution has to be part of how it reports itself rather than a footnote.
2. **Judge quality is not transferable.** Rankings shift by as many as 14
   positions across benchmarks, and JudgeBench discriminates 4.5 times more
   sharply than MT-Bench (60.4 against 13.5 points of kappa spread). Picking a
   free-tier reviewer on general reputation is therefore not evidence that it
   judges *our* task, and no amount of reading about it substitutes for the
   measurement.
3. **The cheapest judges carry the worst position bias**, by nearly two orders
   of magnitude: Llama 3 8B at 0.192 against 0.002 at the top, with "small, and
   cost-optimized models" named as the high-bias class and within-family spread
   of a factor of 70 between Gemini 2.5 Pro and Flash. This is the one place
   the two free-tier candidates are the wrong class of model. **It also does
   not apply to the instrument as proposed**, because a pointwise binary
   verdict has no positions to swap -- which is an argument for keeping the
   call pointwise, and an argument for running a paired A-then-B variant once
   as a free diagnostic if anyone wants the bias number anyway.
4. **Verbosity bias has collapsed and is worth knowing as a negative.** All 21
   models register below 0.011 under a single pairwise rubric, against the 20
   to 40 percent variance the 2023 literature reported. A 2023 precaution
   carried forward into a 2026 design is cargo.

**The protocol it hands us, which is the real find.** Section 5.3 states a
Minimum Viable Validation Protocol: chance-correct and report kappa as the
headline; measure position bias by paired AB and BA; replicate over at least
three runs at temperature 0 with caching disabled; cross-validate on at least
two benchmarks spanning preference-style and correctness-style labels; and
audit the paradox, because test-retest above 0.95 with position bias above 0.10
is a failure mode rather than a strength. The paper names selective adoption as
its own first indirect risk: "reporting Cohen's kappa alone without the paired
position-swap and consistency checks can produce a false sense of having
addressed judge reliability."

That is a third-party validation protocol for the third-party reviewer, which
is the same authorship-independence move remedy two makes, at the price of
remedy one.

**And it changes one number above.** Three replicates at temperature 0 turn 102
calls into 306 and 97,946 tokens into 293,838. That still fits groq's 1,000 RPD
but **exceeds its 200,000 TPD**, so the validated sweep is 1.47 free-tier days
rather than one twelve-minute pass. The paid route is 34 cents. So the finding
is narrow and worth stating exactly: the unvalidated sweep is free and fits one
run; the sweep that can defend its own number does not fit one free-tier day,
and costs a third of a dollar to stop being a two-day job.
