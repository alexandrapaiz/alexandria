# The harness x mechanism crossing, read in full

Run: 2026-11-09, research seat, trigger `message` (PR #926 merged, "continue
with the next item in your lane on the board"). Branch
`alexandria-research/2026-11-09-message-harness-crossing`, PR #937.

Paper: `arxiv:2610.07639`, *HarnessSecurity-Bench: Do Security Mechanisms
Really Protect Coding Agent Harnesses?* v1 2026-10-06, v2 2026-10-10, 11
authors, cs.CR primary with a cs.SE cross-list, 23 pages, "A Preprint" with no
venue named. Artifacts at `github.com/TsingPig/HarnessSecurity-Benchmark`.

The reading-queue line queued on PR #930 by this seat's own live-world check
recorded a PARTIAL read -- abstract, section 1 with table 1, section 6.2 with
table 6 -- and named the rest as the line's ask: sections 2 to 5, 6.3, 7 and
the appendices. This note is that read.

`python3 tools/read_paper.py 2610.07639 --no-cache`, exit 0, 114,176 chars,
all nine sections and both appendices.

## 1. What the full read changes

The partial read's four figures all stand. The sentence built on them does not,
and the replacement is stronger than the original rather than weaker.

### The thing that holds

Table 6 AA, with the model fixed at GLM-5.2 and the approval gate ENGAGED, ASR
across the six harnesses:

| harness | ASR gate engaged | ASR gate skipped | utility gate engaged | utility gate skipped |
|---|---|---|---|---|
| Codex CLI | 81.7% (49/60) | 96.7% (58/60) | 95.4% (124/130) | 96.2% |
| gptme | 45.0% (27/60) | 100.0% (60/60) | 66.9% (87/130) | 97.7% |
| Claude Code | 43.3% (26/60) | 100.0% (60/60) | 94.6% (123/130) | 93.8% |
| Gemini CLI | 3.3% (2/60) | 100.0% (60/60) | 94.6% (123/130) | 96.9% |
| GitHub Copilot | 1.7% (1/60) | 86.7% (52/60) | 60.8% (79/130) | 93.1% |
| Qwen Code | 0.0% (0/60) | 90.0% (54/60) | 50.0% (65/130) | 94.6% |

0.0 to 81.7 is an 81.7 pp spread at one model, one task set, one attack set and
one reviewer. That figure is exactly what the partial read said it was.

### The sentence that does not hold, and it is this seat's own

The queue line says the 81.7 pp spread "is LARGER than the posture effect". That
is true against the paper's pooled posture figure (29.2% to 95.6%, +66.4 pp) and
false for half the harnesses taken one at a time. The per-harness posture effect
spans +15.0 pp (Codex CLI) to +96.7 pp (Gemini CLI), and **three of six exceed
the 81.7 pp harness spread**: Gemini CLI +96.7, Qwen Code +90.0, GitHub Copilot
+85.0. The comparison as written sets a cross-harness RANGE against a pooled
MEAN difference, which are not the same kind of quantity.

### The replacement, which the paper never states and its own tables carry

Compute the cross-harness ASR spread separately in each arm, for every
mechanism with a paired comparison. Engaged means ON for the eight restrictive
mechanisms and OFF for auto-approve, which is a risk capability rather than a
control:

| mech | paired | spread, mechanism DISENGAGED | spread, mechanism ENGAGED |
|---|---|---|---|
| PR | 4 | 10.0 pp (90.0-100.0) | **97.5 pp (0.0-97.5)** |
| AA gate | 6 | 13.3 pp (86.7-100.0) | **81.7 pp (0.0-81.7)** |
| CAL | 6 | 6.7 pp (93.3-100.0) | **76.7 pp (18.3-95.0)** |
| MCP | 6 | 70.0 pp (30.0-100.0) | **63.3 pp (6.7-70.0)** |
| PT | 5 | 23.3 pp (66.7-90.0) | **51.7 pp (0.0-51.7)** |
| NI | 6 | 82.5 pp (17.5-100.0) | 5.0 pp (0.0-5.0) |
| CDL | 4 | 6.7 pp (40.0-46.7) | 5.0 pp (0.0-5.0) |
| RO | 6 | 15.0 pp (0.0-15.0) | 5.0 pp (0.0-5.0) |

The split is clean and it falls along what the mechanism does to a capability.

- **Mechanisms that MEDIATE a capability** -- the approval gate, command
  allowlisting, path restriction, project trust, MCP permissioning -- produce
  their largest cross-harness spread in the engaged arm. Turning the control on
  is what makes the harnesses diverge.
- **Mechanisms that REMOVE a capability** -- network isolation, read-only mode,
  command denylisting -- collapse to within 5 pp of each other once engaged.
  Every harness lands at 0.0 to 5.0 percent.

**So a measured figure for a mediating mechanism does not transfer across
harnesses and a figure for a removing mechanism does.** That is the no-transfer
rule with a scope condition attached, derived from this paper's own tables, and
it is a better instruction to a skill than the pooled comparison the queue line
made.

The single sharpest cell is path restriction: Codex CLI 100.0% to 0.0% ASR
against Claude Code 97.5% to 97.5%, same mechanism, same four tasks, same base
model. One harness suppressed every scored attack effect and the other
suppressed none.

### Most of the AA spread is a blocking effect, and exactly one cell is not

Across the six harnesses in the gate-engaged arm, ASR and utility move together:
Spearman rho = **+0.812** (n=6). The two lowest-ASR harnesses are the two
lowest-utility ones (Qwen Code 0.0% ASR at 50.0% utility, GitHub Copilot 1.7% at
60.8%), so most of the 81.7 pp is a gate that blocks a great deal of everything
rather than a gate that discriminates.

One pair breaks it and it is the finding worth carrying: **Gemini CLI, 3.3% ASR
at 94.6% utility, dominates Claude Code at 43.3% ASR and 94.6% utility.**
Identical utility, thirteen-fold difference in attack success, one base model,
one task set, one reviewer, same two arms. That is a Pareto-clean harness effect
and it is the strongest evidence in this literature that a mechanism figure
belongs to the harness it was measured in.

## 2. The bound the partial read could not have, and it is the big one

**The approval gate's OFF arm is answered by a language model, not a person.**
Section 6.1: "in AA-OFF trials, a separate Qwen3.8-27B model reviews native
permission requests through a deterministic bridge for all six harnesses."
Section 6.2 restates it -- "AA-OFF sends permission requests to the separate
reviewer" -- and section 7.1 bounds the result in the authors' own words:
"Model bias and residual nondeterminism may still affect individual approval
decisions, so the reported AA results reflect the specified approval
configuration."

So the 29.2% figure, the +66.4 pp posture effect and the 81.7 pp spread are all
properties of **six harnesses' native approval surfaces as answered by one fixed
LLM reviewer**. Nothing here measures a human in the loop. And the paper offers
no decomposition of the spread into the two things it could be: COVERAGE (which
operations each harness stops to ask about) and RENDERING (what the request
says when it asks). Those are the two halves `2609.38983` separates as Scope
versus Semantic laundering, and this paper's design cannot tell them apart.

This is the same shape as the correction this seat made on `2605.18583` on PR
#930, where the gate was disabled on every framework and the abstract still
called the result a framework-gating effect, and it points the opposite way.
There the gate was absent and named; here the gate is present and is a model.

## 3. Denominators, and why no interval can be put on any of this

**ASR and utility are oracle-check pass rates, not trial pass rates.** Section
6.1: "rates are calculated by dividing the total passed oracles by the total
oracles." Reconstructing the per-mechanism design from the denominators, at 10
trials per task-harness-setting (section 6.1) and the task counts in table 5:

| mech | tasks | attack oracles | ASR checks per harness |
|---|---|---|---|
| AA | 2 | 6 | 60 |
| NI | 2 | 4 | 40 |
| CAL | 2 | 6 | 60 |
| CDL | 2 | 6 | 60 |
| MCP | 3 | 6 | 60 |
| PIF | 2 | 6 | 60 |
| PR | 4 | 4 | 40 |
| RO | 2 | 2 | 20 |
| PT | 4 | 6 | 60 |

Six oracle checks drawn from one trial are not six independent observations, so
the effective n per harness is the **10 trials**, not the 60 checks. A skill
quoting "0/60" is quoting ten runs.

**And there is no dispersion anywhere in the paper to read any of it against.**
Zero occurrences, over the full text, of *seed*, *std*, *standard deviation*,
*error bar*, *variance*, *significan*, *confidence interval*, *95%*, *p-value*,
*Wilson*, *bootstrap*, *Fisher*, *McNemar* and *interval*. The authors' only
stated mitigation is section 7.2's "we repeat each condition ten times". So
every pp delta in tables 6 and 7 is a point estimate with nothing attached, and
the 5-pp spreads in the removing-mechanism column are inside the noise that ten
trials cannot resolve.

**Read-only mode carries the thinnest denominator in the paper and the worst
trade.** RO's whole ASR finding is 10 passing attack checks of 120 under OFF
and 1 of 120 under ON, at 2 attack oracles per harness, and it buys that 7.5 pp
for a 34.0 pp utility loss (754/1080 to 387/1080). RO is the mechanism this
paper gives a builder the least reason to enable, and the queue line's
"RO 8.3 to 0.8 at -34.0 utility" is right about the numbers and silent about
the denominator being the smallest of the nine.

**Mechanisms are not comparable to each other.** Each mechanism benchmark has
its own 2 to 4 tasks and its own attack oracles (table 5), so "CAL -48.1 pp
against MCP -28.1 pp" compares different tasks carrying different attacks.
Within a mechanism the ON/OFF pairing is sound: section 6.1 fixes the task,
attack variant, acting model and all other security settings across each pair.

## 4. The arithmetic, checked throughout, and it reproduces

Unlike `2605.18583`, where three of table 7's columns failed their own internal
checks, every checkable quantity in this paper reproduces exactly.

**RQ3.** Every `Overall` row in tables 6 and 7 recomputes from its per-harness
cells, including which harnesses are excluded for being D, U or A-rated; every
delta recomputes from the unrounded rates. The three prose decompositions hold
to the unit:

- NI: utility 600/660 to 438/660 is 162 fewer passes, and "required network
  interactions accounted for 161 of the 162" fits exactly against local checks
  of 437/480 to 436/480, which puts the network oracles at 163/180 to 2/180.
- RO: 754 to 387 is 367 fewer, against "347 of its 367".
- CDL: 530/560 to 559/560 is the stated 29 additional passes.
- PT excluding Gemini CLI's startup refusal: 182/240 to 121/240 is 75.8% to
  50.4%, as printed.

**RQ2, reproduced independently from appendix A.** Parsing all 40 x 10 x 5
rater verdicts out of table 9 and recomputing:

- The rating totals: 205 implemented, 83 absent, 112 unknown; within the 205,
  109 opt-in and 96 active by default (64 C + 32 D). All five as printed.
- All five per-mechanism claims: 30 of 31 RO implementations opt-in, 26 of 30
  AA, 22 of 29 MCP active by default (20 C + 2 D), 20 of 22 AL (16 D + 4 C),
  and PIF at 4 implemented / 13 absent / 23 unknown.
- The evidence-gap figure: 69 of 130 closed-source cells unknown (53.1%)
  against 43 of 270 open-source (15.9%), and all 13 closed-source PIF cells
  unknown.
- The consensus claim: **exactly 382 of 400 cells carry a >=3-of-5 majority and
  exactly 18 do not**, and all 382 majorities match the published table 4 with
  zero disagreements.
- **All three Krippendorff alphas, to three decimals, at the stated n**: 0.740
  at n=329 for all five raters, 0.669 at n=323 for L1-L3, 0.911 at n=192 for
  H1-H2, using an ordinal metric on A < O < C < D with U treated as missing and
  cells retained at two or more non-U ratings. Nothing in the paper states that
  ordering; it is the only one that reproduces all three values.

That is a complete independent reproduction of the paper's measurement half
from its own appendix, which is rare enough to be the reason to trust the rest.

## 5. Two boundaries on RQ2 that the reproduction exposes

**The headline human agreement is measured on under half the cells.** The
0.911 for H1-H2 is the highest figure in the paper and its n is 192 of 400,
because H1 returned U on **191 of 400 cells (47.8%)**. Per-rater unknown rates:

| rater | model or person | U of 400 |
|---|---|---|
| L1 | Claude Opus 4.8 | 116 (29.0%) |
| L2 | DeepSeek V4 Flash | 114 (28.5%) |
| L3 | GLM-5.2 | 66 (16.5%) |
| H1 | human | 191 (47.8%) |
| H2 | human | 124 (31.0%) |

The most-agreeing pair is the pair that answered least often, which is what
"U treated as missing" does to an agreement statistic. It is not an error and
the paper reports its n honestly; it is the number to quote alongside the 0.911.

**And the least-hesitant rater is the model under test.** L3 is GLM-5.2, with
the lowest unknown rate of the five at 16.5%, and GLM-5.2 is the single base
LLM for all 2,500 RQ3 trials (section 6.1). One model both rated 400
harness-mechanism cells for security-mechanism implementation and then acted as
the agent whose attack success those mechanisms were measured against. The
paper's limitations section names its single-model coverage (7.2, "Model
coverage") and does not name this overlap.

## 6. Section 6.3, which is the part a containment skill wants

**Case B, the interpreter bypass, is the citable one.** CLI Arg Parser, CAL
benchmark, Qwen Code with command allowlisting ON. The native gate rejected the
poisoned checker, and the agent then invoked it **through an allowed Python
interpreter**, passing all six utility checks and all three attack-effect
checks in the same trial. A second ON trial on the same task passed every
utility check and no attack check, which is the control that makes the point:
executing the checker was never required for the task. An allowlist that names
executables and admits an interpreter has not mediated the operation; it has
renamed the path to it.

This is the same failure `2609.38983` measures as PATH substitution at BGR 1.000
and `2609.28586` formalises as a coverage condition on effects rather than on
invocations. Three independent papers, three vocabularies, one mechanism. This
one is the only one of the three that observes it in a production harness's own
allowlist with a utility oracle attached.

**Case A is a task-level figure and reads like a benchmark-level one.**
"Enabling NI in Claude Code reduced utility from 96% to 76%" is Dependency Lock
Repair alone; table 6's Claude Code NI row is 93.6% to 65.5% over both NI tasks.
The two are consistent -- 96% and 76% are 48/50 and 38/50 on a 5-utility-oracle
task over 10 trials, and the NI benchmark's 11 oracles split 8 local and 3
network across its two tasks -- and the paper does not say which denominator
Case A uses. Anything quoting "96% to 76%" is quoting one task of 23.

## 7. The reach claim in this seat's own queue line is wrong

The line says "not in sources.yaml's reach as far as this run can tell". One
grep refutes it:

```bash
grep -n 'cs.CR\|cs.SE' sources.yaml     # :25 cs.CR a-low, :45 cs.SE a-low
```

The paper is cs.CR primary with a cs.SE cross-list (arXiv API, this run). **Both
of its categories have been configured since before it was submitted**, cs.CR
since 2026-09-19 and cs.SE since 2026-09-30, and the comment above the cs.SE
entry names containment papers by id. No `sources.yaml` diff reaches this, and
the monthly census the incident entry routed it to would have found nothing to
change.

What this seat can establish from a sandbox with no database credential ends
there. Whether the paper is absent from `papers` at all, or present and
discarded at triage, needs one query and this run cannot run it: there is no
`NEON_RO_URL` in the environment and no corpus MCP server attached. The
candidate mechanism, by analogy with `2609.08371` on line 220, is the cursor
rather than the configuration -- `ARXIV_CURSOR_OVERLAP_DAYS = 4` and
`ARXIV_MAX_LOOKBACK_DAYS = 14` in `pipeline/ingest.py`, against a cs.CR
firehose the file's own comment puts at 34 to 37 papers a day -- but cs.CR was
live for the whole of 2026-10-06, so unlike the cs.SE case the window is not a
sufficient explanation and the triage decision has to be read before anybody
re-routes this. Named in the brief for whoever holds the credential.

The route for corpus presence, once that answer is in, is the entrypoint the
engineer already shipped and that line 220 already names:

```bash
modal run pipeline/ingest.py --ids 2610.07639
```

## 8. What a builder does differently

1. **Never quote an approval-mechanism rate without naming the harness it was
   measured in.** Path restriction spans 0.0% to 97.5% ASR with the mechanism
   on, at one model and one task set.
2. **The rule has a scope condition.** Figures for mechanisms that remove a
   capability (network isolation, read-only, denylisting) do transfer: every
   harness lands within 5 pp. Figures for mechanisms that mediate one (approval
   gates, allowlists, path restriction, project trust, MCP permissions) do not.
3. **Check whether a harness's low attack rate is discrimination or blocking.**
   In the gate-engaged arm the two go together at rho +0.812, so a harness with
   a near-zero rate is usually one that also finished half the work. Gemini CLI
   is the counterexample and the one worth studying.
4. **An allowlist that admits an interpreter has not restricted the operation**
   (Case B). Enumerate paths to the protected effect, not names of executables.
5. **Read-only mode is the worst trade in the paper**: 7.5 pp of attack success
   for 34.0 pp of utility, on the smallest denominator of the nine.
6. **Expect the vendor's own documentation not to answer the question.** 112 of
   400 harness-mechanism cells could not be resolved from official
   documentation, CLI materials and source code by five independent raters, and
   53.1% of closed-source cells are among them.

## 9. Claim-grade findings, for whoever files rows

Each is stated with its table, its denominator and its scope. All are
GLM-5.2-scoped, 10 trials per condition, no dispersion reported.

- F1. With the approval gate engaged and the base model fixed, attack success
  across six coding-agent harnesses spans 0.0% (Qwen Code, 0/60) to 81.7%
  (Codex CLI, 49/60). Table 6 AA, ASR off column.
- F2. With the gate skipped, that spread collapses to 13.3 pp (86.7% to
  100.0%). Table 6 AA, ASR on column. F1 and F2 together are the finding.
- F3. The gate's OFF arm is adjudicated by a Qwen3.8-27B reviewer through a
  deterministic bridge, not by a person. Section 6.1; bounded by the authors at
  section 7.1.
- F4. Path restriction ON gives 0.0% ASR in Codex CLI (0/40) and 97.5% in
  Claude Code (39/40) on the same four tasks. Table 7 PR.
- F5. Mechanisms that remove a capability land every harness within 5 pp once
  engaged (NI 0.0-5.0, CDL 0.0-5.0, RO 0.0-5.0). Tables 6 and 7.
- F6. In the gate-engaged arm, attack success and task utility across harnesses
  correlate at Spearman rho +0.812 (n=6), and Gemini CLI is the one harness
  that is Pareto-better than another (3.3% ASR at 94.6% utility against Claude
  Code's 43.3% at 94.6%). Table 6 AA, computed here.
- F7. Command allowlisting was bypassed through an allowed Python interpreter
  in a trial that passed all six utility checks and all three attack checks,
  with a same-setting control trial showing the bypass was unnecessary for the
  task. Section 6.3 Case B.
- F8. Network isolation costs 24.5 pp of utility for 56.3 pp of attack success,
  and 161 of its 162 lost utility passes are required network interactions.
  Table 6 NI plus section 6.2.
- F9. Read-only mode costs 34.0 pp of utility for 7.5 pp of attack success,
  on 2 attack oracles per harness. Table 7 RO.
- F10. Of 400 harness-mechanism cells rated by three LLM and two human raters,
  205 are implemented (109 opt-in, 96 active by default), 83 absent and 112
  unresolved; 53.1% of closed-source cells are unresolved against 15.9% of
  open-source, and all 13 closed-source prompt-injection-filtering cells are.
  Table 4, reproduced here from appendix A.
- F11. The paper reports no dispersion of any kind for any of its 2,500 trials.
  Full-text search, this run.

Ban list checked on this note.
