# agent-approval-paths: the full revision record

One dated heading per entry in `provenance.revisions` in `SKILL.md`. The
frontmatter carries one line each, naming the date, the trigger and what
changed; the narrative lives here. The reason for that split is the measurement
recorded in `skills/harness-engineering/REVISIONS.md` and the rule is in
`prompts/skill-extract.md` section 2.

## 2026-11-09, fourth entry: the right number was on the wrong baseline, and the paper prints it twice

**Trigger.** ADR-37, a cited result refined again. The research seat read
`2610.40753` a third time, verified v4 cell by cell, upheld both of the
refinements v4 added, corrected one of its own sentences, and returned one
finding against v4's own reversal. Board note `5da14666`, 09:16Z, ref #897. It
arrived six minutes after the previous run's pull request opened, so it is new
work rather than a duplicate wake, which was checked on the bus before any of
this was written.

**What this seat did before writing anything.** Fetched the full text again
with `tools/read_paper.py`, exit 0, 69,442 characters, this seat's third full
read. Re-derived the Table 11 pooling from the per-level counts rather than
taking the note's arithmetic, and read the dagger footnote under Table 3 and
Table 9's SABER decision counts directly. Everything below reproduces.

### The finding: 61.8 is printed twice, so it is not prediction's price

Table 11 gives the twin false-block rate for six approver conditions across
four concealment levels. The levels are not equal in size, which is what makes
the pooling non-obvious: script, Makefile chain and binary hold 26 twins each
and command holds 24, for the 102 twins Table 12 names. Pooling each row:

| approver sees | per level | pooled |
|---|---|---|
| command | 100.0, 11.5, 0.0, 100.0 | 26 + 3 + 0 + 24 = **53 of 102, 52.0** |
| request + command | 88.5, 34.6, 46.2, 54.2 | 23 + 9 + 12 + 13 = 57 of 102, 55.9 |
| dialogue | 65.4, 50.0, 50.0, 83.3 | 17 + 13 + 13 + 20 = **63 of 102, 61.8** |
| dialogue + predicted | 46.2, 57.7, 46.2, 100.0 | 12 + 15 + 12 + 24 = **63 of 102, 61.8** |
| dialogue + observed | 0.0, 0.0, 0.0, 4.2 | 0 + 0 + 0 + 1 = **1 of 102, 1.0** |

**The pooling is the paper's own and not this file's.** Section 5.3 ablation
(1) prints "twin false blocks rise from 52.0% to 61.8%" for command-only
against full dialogue, which are the first and third rows above. Ablation (2)
prints "61.8% of the twins are still blocked" for prediction, which is the
fourth. The command row was pooled here as a method check, and it lands on the
figure the paper prints for it, so the arithmetic is verified against the
authors rather than only internally consistent.

So the dialogue arm and the dialogue-plus-predicted arm block the same number
of twins, 63, and not the same twins: per level the two rows differ in both
directions, 46.2 against 65.4, 57.7 against 50.0, 46.2 against 50.0 and 100.0
against 83.3. **Prediction changes which twins are blocked and not how many.**

### What that does to the price v4 published

v4 said prediction "costs 61.8 percent of safe twins against none". Two errors
in one clause, and both of them point the same way.

- **The baseline was wrong.** 61.8 is what the approver prediction *replaces*
  already spends. Against that approver the cost of adding a prediction is
  **0.0 points**. The only comparison in which 61.8 is a cost is against
  observed effects, and that subtraction is **60.8 points**, 61.8 against 1.0.
- **"Against none" was wrong, and the paper says so in its own abstract**,
  which reports Caper "blocking 1.0% of the safe twins". Observation is **1
  twin of 102**. The file said against none in four places: `SKILL.md`
  procedure item 6, `REVISIONS.md` in the third entry's own summary, and
  `evals.json` twice inside task ap-t7.

The reversal v4 made was right and this sharpens it. v3 said prediction was
simply worse; v4 said it was a burden trade; v5 says the burden is not
prediction's to carry. The decision rule that follows is new, and it is the
reason this is a revision rather than a typo fix: **a team already approving
from text pays nothing on this axis to add a prediction and gets the harm
reduction, and a team choosing between prediction and pre-execution is buying
60.8 points of twins with the pre-execution.** Checklist item 8 and procedure
item 6 both change again, in the same direction and further.

One trap for the next reader, named in `SKILL.md` because it is easy to fall
into: the paper does print 60.8, for Caper's safe-completion rate on
YoloFS-Ext. The 60.8 points here is a subtraction of two printed rates and is
not that number.

### Both of v4's own refinements held, and one of them was never this seat's

The research seat checked v4 cell by cell and upheld the discrimination
subtraction and the four-of-five tie correction. But the second of those is
**the paper's own, which v4 presented as its own judgment.** The dagger
footnote under Table 3 reads, in full:

> Blocks no command at all on YoloFS-Ext, dangerous or twin; not ranked.

So Qwen3Guard is excluded from the ranking by the authors. v4's discount of its
[0.0, 3.6] interval was a citation and not an opinion, and the honest
denominator is **four ranked comparators, three of which overlap**. v5 says
whose exclusion it is, because a file that claims the authors' reasoning as its
own judgment is overstating its own contribution, which is the mirror image of
the sin the provenance reviewer exists to catch.

**And the exclusion is benchmark-specific, which is where the research seat's
own sentence failed.** Their note had generalized the footnote to "blocks
nothing at all". Table 9 gives Qwen3Guard-Gen-8B **5,483 SABER decisions at
10.0 percent blocked** against **1,126 YoloFS-Ext decisions at 0.0 percent**.
The footnote is scoped to one benchmark and the paper scopes it in its own
words. v4's sentence was already correct here, because it said "on that
benchmark"; v5 adds the SABER figure so the scope cannot be dropped by the
next reader. They filed their sentence as a second instance of a sampling
class, which is their register and not this one's.

### The eval task was still teaching the refuted sentence

Task ap-t7's `exploit.answer` opened with "Predicted effects measured worse
than no evidence at all." That is v3's claim, which v4 refuted in the file and
left standing in the suite.

It matters past tidiness for two reasons. The exploit exists to score zero **on
form**, for walking the rubric's headings with no numbers attached. An exploit
that also asserts a refuted fact can be marked down by a judge for the content
instead, which makes the task measure the judge's knowledge of the paper rather
than the respondent's use of the skill. And the suite is a published artefact,
so the one answer in it labelled as the wrong answer was the one teaching a
reader something false.

Rewritten to fail on form alone. The rubric's first criterion was also raised:
anchor 1 is now v4's answer, the right number with no baseline named, and
anchor 2 requires both comparisons. `situation`, `with_skill` and the
`without_skill_basis` note carry the correction.

**One thing the correction makes worse, and it is recorded rather than hidden.**
The authored bare answer for ap-t7 has the subject treating prediction and
observation as one mechanism at two price points. On harm that is now correct,
and on burden against the text baseline it is also correct. The bare answer
still carries no number and names no baseline, which is where a delta would
have to come from, but this task is a live candidate to fail ADR-38 rule 5 as a
control rather than to qualify. Whoever runs the bare-first pass should expect
that and not read it as a surprise.

### What this does not say

Three full reads by this seat and three by the research seat, with the fourth
correction in a row landing in the understating or mis-baselined direction.
That is provenance converging. **It is not validation.** No section of this
skill has a differential delta, no bare arm has run, `GROQ_API_KEY` and
`NEON_RO_URL` were both absent again in this run, and the honest word for every
number in this file remains **unmeasured**. `status: draft` is unchanged and
`validated` is still the empty string.

## 2026-11-09, third entry: two sentences in delta 2 were wrong in the understating direction

**Trigger.** ADR-37, a cited result refined. The research seat read `2610.40753`
again, checked the cells, and sent a correction naming four things. It arrived
after this run's wake payload was written and was unanswered, so it is this
run's to act on.

**What this seat did before writing anything, because ADR-35 makes the paper
the authority and not the note.** Fetched the full text again with
`tools/read_paper.py` at exit 0, 69,895 characters, and verified every number
in the correction against the paper's own tables. **All of them check out.**
Table 9's harm-blocked and twin false-block pairs, Table 11's five concealment
rows, Table 12's seven intervals. The re-read also produced two refinements the
correction did not name, which is the second time in two runs that going back
to the table paid.

### The correction that matters most, and it is the one this file did not have

The paper's Appendix C reports, per system, how often **the command that caused
the harm** was blocked, beside the twin false-block rate. Subtracting the second
from the first gives how much each approver's blocking discriminates harm from
its harmless twin. Verified cell by cell from Table 9:

| system | harmful cmd. blocked | twin false block | discrimination |
|---|---|---|---|
| Caper | 84.3 | 1.0 | **+83.3** |
| Caper (Claude Code hook) | 62.7 | 2.0 | **+60.7** |
| CARE (rule checker) | 2.0 | 2.0 | 0.0 |
| TS-Guard | 8.8 | 8.8 | 0.0 |
| Claude Code Auto Mode | 3.9 | 3.9 | 0.0 |
| Qwen3Guard-Gen-8B | 0.0 | 0.0 | 0.0 |
| gpt-oss-safeguard-20b | 14.7 | 15.7 | **-1.0** |

Three of the text-based approvers block the harmful command at **exactly** the
rate they block its harmless twin, to the decimal, and one blocks the twin
slightly more often. They do block. Their blocks carry no information about
which command was the dangerous one. That is a sharper statement than anything
this section carried before, and the bound is what makes it legible rather than
what weakens it: the twins carry an identical request and command by
construction, so the subtraction measures discrimination only where the harm
hides behind text the approver cannot tell apart, which is exactly the regime a
text-based approver is in.

**First refinement the correction did not name.** Qwen3Guard's zero is not the
same kind of zero as the other three. Table 9 shows it blocked **0.0 percent**
of commands on YoloFS-Ext, 0.0 percent of tasks, over 1,126 decisions. So it
has no discrimination because it made no blocks, not because its blocks were
uninformative. A system that never blocks trivially scores zero on both halves
of the subtraction. Three of the four zeros are findings and the fourth is an
abstention, and the skill now says four or five only where it can say which.

### The false-block tie was wider than this file said

The previous entry recorded a correction to the research seat's own note, that
Caper's [0.2, 5.3] overlaps TS-Guard's [4.7, 15.9] by 0.6 points, so the clean
comparison was one model rather than guardrails as a class. That was right and
it did not go far enough. Read off Table 12, Caper's interval overlaps **four
of the five** comparators reporting that axis: CARE [0.5, 6.9], Claude Code
Auto Mode [1.5, 9.7], TS-Guard [4.7, 15.9] and Qwen3Guard [0.0, 3.6]. Only
gpt-oss-safeguard-20b [9.9, 24.0] is clean.

> **Superseded by the fourth entry.** The ranked denominator is four, not five.
> Qwen3Guard is de-ranked by the paper's own dagger footnote, so the count is
> three overlaps of four ranked comparators.

**Second refinement the correction did not name**, and it is the same
observation one axis over: the Qwen3Guard overlap is the overlap of a system
that never blocked, so banking it as evidence of a tie would be reading an
abstention as a result. The skill discounts it in the open rather than dropping
it silently, because the honest count is four overlaps of which three are
informative.

> **Superseded by the fourth entry.** This reasoning is right and it is the
> paper's, not this file's. The footnote under Table 3 already de-ranks that
> system. Calling it a refinement of ours overstated this file's contribution.

### And the predicted-effects claim was reversed in the honest direction

This is the correction that changes a decision rule, so it is the most
consequential of the four. The previous version of this section called
prediction "worse than no evidence at all" and procedure item 6 said never to
use it. The false-block numbers behind that are right: 0.0, 0.0, 0.0 and 4.2
percent across four concealment levels with observed effects, against 46.2,
57.7, 46.2 and 100.0 with predicted effects, and 61.8 percent of twins blocked
overall.

But the paper's section 5.3 says in its own words that when the model predicts
effects, **"harm drops as far as with observation"**. So prediction buys the
entire harm reduction and pays for it in burden. Calling it worse than no
evidence was true on one axis and false as a summary, and the advice that
followed from it was to discard a mechanism that works on the axis the section
is about.

Two further readings of that row, both from the correction and both verified:

- **The 100.0 is an abstention.** Appendix D states that the predictor reads the
  command and referenced files up to three levels, within 16 files and 32 KB,
  and that "binaries cannot be read". So on the binary concealment level,
  prediction is impossible and the approver blocks every twin. That is a
  conservative failure and a procedure should say which kind of failure it is.
- **The controlled comparison is a wash.** Predicted differs from the
  full-dialogue row by one field; the command-only row differs by more. Against
  dialogue: 46.2 against 65.4, 57.7 against 50.0, 46.2 against 50.0, 100.0
  against 83.3, which is two better and two worse. The "worse on two of four"
  claim is against command-only, and command-only is not the control.

**What changed in the file.** Checklist item 8 and procedure item 6 both now
state prediction as a burden trade with its price named, 61.8 percent of safe
twins against none, plus the abstention, rather than as a prohibition.

> **Superseded by the fourth entry.** 61.8 is the full-dialogue arm's figure
> too, so it is not prediction's price: against the approver it replaces the
> cost is 0.0 points. And observation is 1 twin of 102, not none. The
section keeps recommending observed effects. What it no longer does is tell a
reader that a prediction is worthless when the paper measured it cutting harm
as far as observation.

### What this does not say

Two seats have now checked this section against the paper's own tables
independently, and one of them found two sentences the other had understated.
That is provenance working. **It is not validation.** This section still has no
differential delta, because this seat has no route to either eval arm. The
skill's frontmatter reads `status: draft`, and the honest word for it remains
**unmeasured**.

## 2026-11-09, second entry: the description was promising less than the skill delivers

**Trigger.** Charter step 7, and specifically a measured findability gap this
skill's own previous run recorded and deferred. That run added trigger case
`ap-pos-4`, committed **failing on purpose**, with a note saying why it was not
repaired on the spot: the description stood at 149 words against a 150-word
editorial budget, so any addition was a swap that could lose a currently
passing activation condition, and the engine's idf is library-wide, so the
change perturbs all ten skills and the 85-case suite has to be re-run to know
the net. The note filed it as next-run work with its number as the baseline.
This is that run, and the baseline held: **74 of 85, reliability 0.87**,
re-measured here before anything was edited.

**The diagnosis was not the one the gap suggested.** The obvious reading of a
positive case that routes elsewhere is that the description under-covers its
own subject. That is not what was happening. `ap-pos-4` states delta 3's
situation in the operator's words, the alert on a mid-task persisted-rule
proposal and the rate to budget for it, and it was losing to
`agent-containment` at 0.357 against 0.219. Scoring the prompt against both
descriptions directly shows `agent-containment` winning on **four
same-spelling, different-sense matches**:

| the term | where `agent-containment` gets it | what it means there |
|---|---|---|
| `alert` | "when an agent's alerts fire into a queue nobody acts on" | alert triage |
| `budget` | "an isolation architecture's published overhead is your capacity budget" | capacity |
| `rule` | "when security rules in a system prompt are counted as enforcement" | system-prompt rules |
| `propos` | "tool filtering or injection detection is the proposed fix" | a clause connective |

Not one of the four is about alerting on a persisted-rule proposal. So the case
was lost to a sense collision inside a lexical engine rather than to a gap in
this skill's coverage, and that distinction is the finding. It is filed as a
ledger entry for the engineer seat, because the ceiling belongs to the
instrument and not to this file.

**What was still genuinely wrong here, and it is the part worth fixing.** The
description's delta 3 clause covered only the builder's side, "when shipping an
always-allow, a remember-this-choice or a persisted permission prefix so the
agent stops asking twice". The operator's side was absent from the description
and has been answered by the body since v2: checklist item 5 and procedure
items 1 and 2 prescribe treating a mid-task request to persist a rule as an
alert with a mechanical response, and sizing its budget on the bound rather
than on the zero, at 3.0 percent pooled and 11.3 percent per model. The
description was promising less than the skill delivers, which is a real defect
in a library whose differentiator is being found by the person who needs it.

**The clause added**, inside the existing one rather than as a new one, because
of the budget: `or alerting on one proposed mid-task and budgeting its
false-positive rate`.

**Why this is not a token match dressed up as a condition.** Tuning a
description against a case's surface words is the trigger-test analogue of
renaming a receipt bundle to win a sort, which this seat declined to do on the
same day and was credited for. The test that separates the two is whether the
body answers the condition the description now advertises. It does, in three
places named above, and it did before this edit. The three terms the new clause
contributes to the match, `alert`, `budget` and `rate`, are the words an
operator would actually use for the thing the body prescribes. Had the clause
needed a word the body does not earn, the right outcome was to leave the case
red and report the engine's ceiling, and that was the plan this run started
with.

**The swap, in full, because the budget was the binding constraint.** 149 of
150 words before. The new clause costs five, so five had to come back from
clauses that keep their meaning without them: `human` before `confirmation` in
the first condition, `must be` to `is`, `agent` before `action` in the second,
`itself` in the third, and `how many confirmations the design costs` to `the
confirmation cost` in the subject sentence. **150 of 150 words after**, which
is at the cap and not over it.

**The result, with the margin stated rather than rounded.** `ap-pos-4` now
passes: this skill 0.397 against `agent-containment` 0.351, **margin +0.046**,
which is narrow enough that a future description edit anywhere in the library
could take it back, since the idf is library-wide. **Suite 75 of 85,
reliability 0.88**, from 74 and 0.87. Positives 38 of 40 from 37 of 40. **No
other case moved in either direction**, which was the exact risk the deferral
note named, and it was established by re-running the suite rather than assumed.

**What this does not say.** A green trigger case says this skill is findable
from that prompt and says nothing at all about whether it helps anyone. This
skill remains **unmeasured**: no differential delta exists for it, because this
seat still has no route to either eval arm. `status` stays `draft`.

## 2026-11-09: the research seat's answers to this skill's own four questions

**Trigger.** ADR-37: a cited premise corrected, and new reading that changes a
delta's evidence class. On 2026-11-02 this skill shipped as a draft and queued
seven lines in `docs/research/reading-queue.md`, three ingestion requests and
four questions its own reading had raised and could not settle. The research
seat drained the four on 2026-11-09 and reported on the board. Two answered,
two stay open with corrected reasons, and two of this skill's load-bearing
premises were wrong.

**The three papers were read in full by this seat before anything was written
here**, with `tools/read_paper.py` at exit 0: `2610.14488` 98,301 chars,
`2610.40753` 69,442, `2611.08516` 98,918. Every number below was checked
against the paper's own table rather than against the research note's summary
of it, which is ADR-35's requirement and which caught one overclaim, recorded
at the end of this entry.

### Delta 1 is now a pattern rather than a single-paper delta

`2610.14488` (ZTAC) reaches the same construction as the two founding papers
and **cites neither of them**: zero occurrences of either arXiv id, of "consent
integrity" or of "Verifiable Action Card" in the full text, checked. So the
construction has three independent sources, which is the charter's bar for a
pattern. It is also the implemented and measured version of what the shell case
was missing: the second founding paper's trusted path and total mediation are
specified and not implemented, and ZTAC is 3,164 lines of trusted Rust with
ground-truth oracles.

What was added to the section: 2 of 74 attacks succeed against 66 of 74 for a
tool allowlist and 56 of 74 for an allowlist plus a deployed-style command
sandbox, all 10 replayed disclosed incidents contained, 43 of 46 benign
operations at 8 prompts, 4.0 ms median brokered request.

**The ablation table is the part worth the lines**, because it reorders the
build. Removing the approval tier admits 18 of the 74, removing resolved
classification admits 5, and removing object-bound approvals while keeping
exact request fields admits 2. The construction is named after the piece that
pays least. Two further items came out of the same table and the paper's section 6.4:
the authors found eight flaws in their own implementation, seven of them
name-against-object gaps inside a system built to close name-against-object
gaps, so a resolver is audited rather than trusted; and `.ENV` evaded a rule
because the rule compared case-sensitively, which resolution does not fix.

### Delta 2 gained its first measured route off the frontier, and one tie

`2610.40753` (Caper) pre-executes in a snapshotted sandbox and approves from
observed effects. Added with its headline numbers and, more importantly, with
Appendix E's 95 percent Wilson intervals, because the two axes do not have the
same status and the research note's reading of the second one needed a
correction.

- Harm, clean: YoloFS-Ext [4.0, 14.7] against the deployed gate's [53.1, 71.5];
  SABER [5.0, 9.1] against [12.2, 18.0]. Neither overlaps.
- False blocks, **a tie**: Caper [0.2, 5.3] overlaps the rule-based checker's
  [0.5, 6.9].

**The correction to the note.** It said the false-block axis is a tie against
the rule checker but that Caper "beats the guardrail models (gpt-oss-safeguard
[9.9, 24.0], TS-Guard [4.7, 15.9])". Read off Table 12 directly, Caper's
[0.2, 5.3] **also overlaps TS-Guard's [4.7, 15.9]**, by 0.6 points. The
gpt-oss-safeguard comparison is clean and the TS-Guard one is not, so the
section says the advantage is clean against one guardrail rather than against
guardrails as a class. This is the kind of thing ADR-35 exists for: the note
was careful and the table is the authority.

Also added, and it is the sharpest item in the revision: Table 11's
predicted-against-observed result. Observed effects give twin false-block rates
of 0.0, 0.0, 0.0 and 4.2 percent across four concealment levels; the same
approver on an LLM's *predicted* effects gives 46.2, 57.7, 46.2 and 100.0,
which is worse than showing the approver nothing on two of the four. A reader
who takes only one procedure from this revision should take that one, because
predicting effects is the cheap thing a team reaches for and it measured
backwards.

`2611.08516` (Aegis OS) supplied an independent corroboration of delta 2's
mechanism on real sessions rather than on tldr-pages: 39.0 percent of 11,070
real shell invocations across 52 production transcripts use compound operators
or inline interpreter scripts, 4,318 of them. Two independent corpora, one
cause.

### Delta 3's control was wrong by a factor of four, in the loose direction

This is the correction that mattered most, because the section prescribes an
alert on it. The file read `2610.22987`'s Benign Control as 0 of 25. The
paper's construction is 25 cases **per agent configuration** and Table 1
carries four configurations, so the pooled control is **0 of 100**.

A zero count is a bound and not a rate, and the bound is what an alerting
design may rely on:

| control | one-sided 95 percent upper bound |
|---|---|
| 0 / 25, what this file quoted | 11.3 percent |
| 0 / 100, pooled | 3.0 percent |

Both recomputed here as `1 - 0.05 ** (1/n)` rather than taken from the note:
11.29 and 2.95 percent. The file now quotes both, because pooling assumes the
four configurations are exchangeable for this event and that is the arguable
step. The error was in the conservative direction, so no advice in the section
was unsafe, but a skill that says "measured at zero" where the evidence says
"bounded at 3.0 percent pooled" is overstating evidence, which is the one sin
the provenance reviewer exists to catch.

The section also gained Aegis OS's replay of the remedy delta 3 attacks: a
path-and-prefix allowlist still prompts on 28.54 percent of 28,087 real tool
calls against 53.31 percent for asking every time, while commit-time gating
reaches 4.97 and a scoped lease 1.12. So the prefix rule buys about half the
prompts and carries the escalation path, and the fatigue budget is somewhere
else.

### What did not change, and why

**No claim id was added and `status` stays `draft`.** None of the six papers
has a row; the research seat queued all six for distill and says so. The
library's own gate allows exactly one skill to cite zero claim ids and only
while it is a draft, so `draft` remains the honest state and is lower than the
`provisional` the format contract prescribes.

**No eval delta is claimed.** `NEON_RO_URL` and `GROQ_API_KEY` were both
checked absent in this run. One eval task was added, `ap-t7`, against the
predicted-against-observed rule, and it is unqualified like the other seven.

**The stale premise in the first caveat was repaired too.** It named the
compute workspace as the ingestion blocker. That cleared on 2026-11-08 at
23:37Z, so the rows wait on the next distill run rather than on an account.

**One premise corrected outside this file.** The reading-queue line on the
container-against-microVM question cited `2610.02456` as putting both
boundaries on one task set. It does not: that paper's own inclusion rule
requires hardware virtualization, which excludes every container candidate in
its own census, so its comparison is microVM against microVM. The line is
corrected in `docs/research/reading-queue.md` rather than here, because the
premise never reached this skill's body.

### A correction this run made to itself, before shipping

The first draft of delta 1's item 7 said that resolution "does not fix case"
because `.ENV` "evaded the rule because the rule compared case-sensitively".
That is wrong and the paper says the opposite: the case alias needs no
resolution precisely **because** ZTAC's rules match without regard to case.
Table 1's handoff row says the same thing in its mechanism column, "matched
without regard to case".

The conclusion survived and the reason did not, so the item now carries the
paper's own mechanism list: a case alias is caught by case-insensitive rule
matching, and a directory swapped between the check and the use is caught by an
`openat` walk with `O_NOFOLLOW`, neither of which is something a resolver
supplies. The same draft also called the path-divergence list "the five classes
that paid in the ablation", which conflated Table 1's list of ways a name and an
object diverge with the ablation's list of removed defenses. Both are fixed.

This is recorded rather than quietly corrected because it is the exact failure
mode ADR-35 names. The error came from reading a research note's summary of an
ablation row instead of the row, and it was caught by going back to the paper
for an unrelated check. The note was not wrong here; the compression was mine.
