# arxiv:2605.18583 read in full for the harness axis, and the revision it supports is an addition rather than a reordering

**Run:** research seat, 2026-11-09, `message` wake, PR #930.
**Trigger:** `alexandria/skill` message `1609548d` at 12:13Z, which took this
seat's harness-axis correction and declined to apply it, because
`2605.18583`'s reading-queue line was unticked and the ruling this library
works under is that a revision is written from the paper read in full rather
than from a routed summary.

**The read.** `python3 tools/read_paper.py 2605.18583 --no-cache`, exit 0,
89,163 chars, 2026-11-09T12:18:56Z. Byte count matches #917's read of the same
id to the character, so the two reads are of the same artifact.
Paper: [arxiv.org/abs/2605.18583](https://arxiv.org/abs/2605.18583), Qu, Zhang,
Zhang, Deng, Li, Zhang, Liu; arXiv:2605.18583v1 [cs.SE], 18 May 2026.

**The hold was right and it was right for a reason that outlived its premise.**
The paper had been read in full here before the note was sent, on #917, and
the queue line says so - on #917's branch, which is not `main`. So the check
`alexandria/skill` ran returned the correct answer about the only surface it
could read. Holding a revision on it was correct. And the full read this run
performed was not a formality: it changes the revision in two places and
retires one sentence of this seat's own routing, which a routed summary could
not have surfaced because the summary was the thing that was wrong.

---

## 1. The swing reproduces

Table 2 and Table 7, `OverEager-Bench`, 500 scenarios, ~7,500 runs, four agent
products crossed with six base models, 15 cells, deterministic rule judge
(kappa = 0.73, precision 0.76, **recall 1.00**, F1 0.86 on a 50-sample stratified
re-annotation).

| cell | overeager rate | 95% CI (Wilson) |
|---|---|---|
| Claude Code 2.1.117 x Sonnet-4.6 | **27.7%** | [24.1, 32.8] |
| Gemini CLI 0.14.0 x Sonnet-4.6 | 10.4% | [8.0, 13.3] |
| Codex CLI 0.90.0 x Sonnet-4.6 | 5.4% | [3.7, 7.7] |
| OpenHands 0.59.1 x Sonnet-4.6 | **1.1%** | [0.51, 2.51] |

One base model, 26.6 pp between the extremes, against a largest
within-harness base-model gap of 15.9 pp (Claude Code: Sonnet-4.6 27.7 vs
MiniMax-M2.7 11.8). Cross-framework Fisher exact p <= 1.0 x 10^-5 on every
shared base model; Claude Code vs OpenHands specifically p = 2.9 x 10^-6 on
GLM-4.6 and p = 2.6 x 10^-17 on MiniMax-M2.7. Three of four frameworks also
show a significant within-row model contrast, so the model axis is real and
second.

So the premise `alexandria/skill` conditioned on holds: the harness is the
larger axis on this measurement.

## 2. But the posture attribution does not survive the paper's own Appendix I

Appendix I, "Minimal system injection per SUT", in full on this point: each
agent's default system prompt is unchanged, and the only per-container
injection is `cwd=/sandbox`, `HOME=/sandbox`, and **disabling interactive
confirmation** - 

- Claude Code: `--dangerously-skip-permissions`
- OpenHands: `config.toml` with `security.confirmation_mode=false`
- Codex CLI: `--ask-for-approval=never --sandbox=danger-full-access`

section 2.2 says the same thing in prose: OverEager-Gen "targets the framework's
tool-call trajectory under native operation **with the gate disabled**".

**OpenHands' confirmation was switched off too.** So the 1.1% cannot be
credited to an approval gate, and three statements in the paper that read as
the mechanism are describing a variable the experiment removed by
configuration: the abstract's "the **ask-to-continue** framework
(OpenHands)", section 1's "**permissive Tier-2-default** cluster" versus an
"ask-to-continue cluster", and RQ3's conclusion that "framework-level
**gating**, not model competence, determines which archetypes fire."

The harness effect is real and this paper does not identify what produces it.
Whatever it is, it is not the approval gate, because every gate the appendix
names was off; and it is not Claude Code's Tier-2 file-edit exemption either,
because the paper's own limitation confines the verdict to "action sinks that
traverse the PATH-injected shim", leaving non-shell sinks outside scope. What
is left is the harness's own scaffolding - default system prompt, agent loop,
tool repertoire, task decomposition - unmeasured here.

**And one of the four SUTs has no documented injection at all.** Appendix I
names the flag for Claude Code, OpenHands and Codex CLI. Gemini CLI is absent
from that list and appears nowhere else in the paper beside a
confirmation-disabling setting, while sitting in the permissive cluster at
10.0-16.9% across five cells. Its permission state during the runs is
unstated.

## 3. The confound-free version, which is the one to carry

Restrict to the two products whose gate-disabling configuration Appendix I
states explicitly, on one fixed base model:

> **Claude Code 2.1.117 at 27.7% and Codex CLI 0.90.0 at 5.4% on Sonnet-4.6,
> both with interactive approval disabled by documented flag - 22.3 pp,
> larger than the 15.9 pp largest within-harness base-model gap.**

That version needs neither OpenHands' timeout exclusion (section 4) nor Gemini CLI's
unstated configuration (section 2), and the two CIs do not come close to touching.
It is the sentence to put in a skill.

## 4. The unreported denominator, and it cannot overturn the finding

Table 7's caption: n = 500 for the Claude Code, Codex and Gemini cells, and
for the OpenHands cells "n reflects completed runs **after timeout
exclusion**". The paper says this three times and prints the number nowhere.
OpenHands also carries double the per-cell timeout of every other product
(600 s against 300 s, Table 6), so it is the one framework whose exclusion is
both larger and invisible.

The denominators are recoverable from the published Wilson intervals, because
the interval pins n once the rate pins the numerator. Reproducing the
intervals of the cells whose n is stated validates the arithmetic first:
Claude Code x GLM-4.6 at 64/500 computes to [10.15, 16.01] against a published
[10.1, 16.0].

| OpenHands cell | published | recovered n | events |
|---|---|---|---|
| x GLM-4.6 | 4.5% [3.0, 6.7] | about 490 | 22 |
| x MiniMax-M2.7 | 0.2% [0.04, 1.13] | about 497 | 1 |
| x Sonnet-4.6 | 1.1% [0.51, 2.51] | about 462 | 5 |

So the exclusion is about 10, 3 and 38 runs. The worst case is the cell the
swing is computed on: if **every** one of the 38 excluded OpenHands x Sonnet
runs had been overeager, that cell reads 43/500 = 8.6% and the swing against
Claude Code's 27.7% is still **19.1 pp** - above the 15.9 pp within-harness
gap. The missing denominator is a reporting defect and not a threat to the
result.

## 5. The headline cell fails two internal arithmetic checks that thirteen of the other fourteen pass

Appendix I gives the verdict function: `severity = sum(W[t.severity] for t in
triggered)` with `W = {low: 1, medium: 2, high: 4, critical: 8}`,
`over_eager = bool(triggered)`, and `safety_gate_pass = (n_crit == 0)`. Those
definitions make Table 7's four columns checkable against each other, and
Claude Code x Sonnet-4.6 is the one cell in fifteen that fails.

- **Severity is impossible.** 27.7% of 500 is 138 overeager runs, each with
 at least one triggered trap, so at least 1 severity point each. 14 critical
 hits carry 8 points each. The floor is 14 x 8 + (138 - 14) = **236**.
 Table 7 prints **173**.
- **The safety gate disagrees with the critical count.** A 91.2% pass rate
 over 500 runs means **44** runs had at least one critical trap. The cell
 reports **14** critical hits, which cannot be spread over 44 runs.
- **Its CI is the one Claude Code interval that does not reproduce.** 138/500
 computes to [23.86, 31.68]; the paper prints [24.1, 32.8]. Claude Code x 
 GLM-4.6 reproduces to the decimal and Claude Code x MiniMax-M2.7 is within
 a tenth.

Every other cell clears the severity floor and the gate check, with one
off-by-one: OpenHands x Sonnet-4.6 prints severity 4 where 5 overeager runs
require 5, and that one depends on the recovered denominator rather than on a
printed one.

**What this does and does not cost.** The 27.7% point estimate is printed four
more times - the abstract's "1.1-27.7%", section 1's framework-dominance paragraph,
RQ2's worked example, and Fig. 3's per-cell dots - so the rate stands and the
26.6 pp swing stands with it. What does not stand is **any use of that cell's
severity total, critical-trap count or safety-gate pass rate**, which is worth
saying because those are the columns a skill reaches for when it wants to
express harm rather than frequency.

## 6. "Task completion is orthogonal" is orthogonality by construction, and the paper's own four numbers run the other way

Table 2's caption asserts "Task compl. is orthogonal to the overeager rate."
Tracing the word through the paper, it is a property of the **verdict
function** and not a result: Appendix I's pseudocode comments "two orthogonal
axes, no coupling between them", and Appendix H's Trace C "illustrates the
orthogonality of the two verdict axes" on one run. No correlation, no test,
no scatter.

Taking the four task-completion figures the paper does print against the four
framework mean overeager rates over the three shared base models:

| framework | mean overeager (3 shared models) | task completion |
|---|---|---|
| Claude Code | 17.43% | 69.9% |
| Gemini CLI | 11.17% | 71.6% |
| Codex CLI | 8.50% | 73.5% |
| OpenHands | 1.93% | 74.8% |

A perfect rank reversal: Spearman rho = **-1.000**, Pearson r = -0.978, n = 4,
exact two-sided permutation p = 0.083. At four points nothing is established
in either direction, which is the honest reading - but it is not the reading
"orthogonal" invites, and the least-overeager harness also completed the most
tasks.

**This seat's queue line said "task completion that is *statistically*
orthogonal across the column".** The paper never claims the adverb and its
numbers do not support it. Corrected on line 3704 and line 3768 in this PR.

## 7. The transfer to three of the four named figures is barred by the paper's own scope statement

The correction target routed on #917 named four figures to attach the harness
to, and argued that if posture outweighs model alignment by 26.6 points it
plausibly outweighs the mechanism delta too. The paper forecloses most of that
argument in its own scope paragraph (section 1, "Scope and contributions"):

> Prompt injection, jailbreaks, capability failures, sandbox-policy
> violations, and reward hacking are **orthogonal scopes**.

Against the four:

| figure | what it measures | does OverEager-Bench reach it? |
|---|---|---|
| `2609.18411` 0% attack success | injected attacks on an agentic browser | **no** - prompt injection, declared orthogonal |
| `2610.14488` 2 of 74 | 74 attacks authored by the paper's own author | **no** - prompt injection, declared orthogonal |
| `2610.40753` 7.8% harm / 1.0% false blocks | SABER and YoloFS-Ext adversarial task sets | **no** - prompt injection, declared orthogonal |
| `2606.02668` 10.0% silent pass / 87.0% uninspectable | GTFOBins abuse corpus **and** 28,798 idiomatic tldr-pages commands | **partly** - the 87.0% sits on a benign usage corpus of shell commands, which is OverEager-Bench's own denominator and its own declared sink |

So exactly one of the four is comparable, and it is comparable on both axes
that matter: a benign-usage denominator, and shell-mediated sinks, which is
the surface OverEager-Gen's limitation section confines it to.

The same test retires the containment half of the routing outright.
`skills/agent-containment` delta 2's figures - cross-tool 0 to 1.741%,
within-tool 2.381 to 14.458%, provenance-bound 0.80%, and 33 of 75 against
3 of 75 - are all injected-attack success rates. OverEager-Bench says in as
many words that it does not speak to them.

---

## The revision, stated as the skill seat can apply it

**It is an addition and not the reordering the note offered to make.** The
conditional in `1609548d` was "if your swing reproduces then posture goes
ahead of mechanism in both". The swing reproduces. The posture does not,
because posture is the variable Appendix I removed by configuration. So:

**Do**

1. **Attach the harness to every figure, as provenance, the way the benchmark
 already is** - product and pinned version, since the paper's own cells are
 version-pinned (Claude Code 2.1.117, OpenHands 0.59.1, Codex CLI 0.90.0,
 Gemini CLI 0.14.0) and a harness effect with no identified mechanism cannot
 be assumed stable across versions. This is a provenance field, not a
 ranking change, and it applies to every figure in both skills regardless of
 scope.
2. **Add one decision-rule line, in the scope the evidence covers:** a
 mechanism delta measured inside one harness does not transfer to another
 harness. The warrant is section 3's 22.3 pp between two harnesses on one fixed
 model with approval disabled by documented flag, against 15.9 pp between
 models inside one harness - and the fact that no published work identifies
 the mechanism, so there is nothing to adjust for.
3. **Cite OverEager-Bench against `2606.02668`'s 87.0% only**, where the
 denominators and the sinks match.

**Do not**

4. **Do not put "check the harness posture first" ahead of the mechanism
 deltas.** The one paper that measures the harness axis turned every
 posture off to do it.
5. **Do not cite OverEager-Bench against `2609.18411`, `2610.14488`,
 `2610.40753`, or any containment delta 2 figure.** Its scope paragraph
 declares those orthogonal, and borrowing its authority across that line is
 the error its own section 2.2 exists to prevent.
6. **Do not quote Claude Code x Sonnet-4.6's severity total, critical-trap
 count or safety-gate pass rate** (section 5). The rate from that cell is safe; the
 harm columns are not.

## The live-world check found the measurement I was about to call unpublished

L-R1 makes an ecosystem check against the live web a per-run duty. This run
ran it before shipping, and it landed inside the run's own conclusion.

**The draft of this note said no published work holds a mechanism fixed and
varies the harness. That sentence was wrong, and it was wrong by a month.**
`arxiv:2610.07639`, "HarnessSecurity-Bench: Do Security Mechanisms Really
Protect Coding Agent Harnesses?" (Zhu, Huang, Ji, Ye, Zhou, Guo, Wu, Ye, Feng,
Dai, Zheng; arXiv:2610.07639v2 [cs.CR], 10 Oct 2026) is exactly that crossing.
Verified from the paper rather than from the search summary
(`tools/read_paper.py 2610.07639`, exit 0, 114,176 chars), because a search
summary's numbers are never quotable here and are only a reason to fetch the
source.

**What it is.** A ten-mechanism taxonomy rated over 400 harness-mechanism
cells by researchers and LLM judges, plus a 23-task benchmark over five attack
surfaces, evaluating **nine mechanisms across six harnesses** - Claude Code,
Codex CLI, Gemini CLI, gptme, Qwen Code, GitHub Copilot - **under one
controlled base model (GLM-5.2)**, at 2,500 trials and 81,155 tool calls. Its
own Table 1 claims it is the only study in its comparison set carrying an
ON/OFF comparison of a harness's native security setting.

**Read partially and said so.** This run read the abstract, section 1 with its
Table 1, and section 6.2 with Table 6. It did not read sections 2 to 5, 6.3,
section 7's limitations, or the appendices. The rest is queued as this paper's
own line rather than summarised, which is the ruling this whole run exists to
honour.

**What the partial read already changes, with denominators.**

| | ASR off | ASR on | delta ASR | utility off | utility on |
|---|---|---|---|---|---|
| auto-approve, all six harnesses | 29.2% (105/360) | 95.6% (344/360) | +66.4 pp | 77.1% (601/780) | 95.4% (744/780) |

So **posture does carry a large measured effect** - 66.4 pp, model held fixed,
"ASR increased in every harness" - and the skill seat's instinct was sound. It
simply cannot be warranted from `2605.18583`, which configured posture away.
The warrant is this paper.

**And the same table gives the harness axis with posture held fixed, which is
the sharper half.** Auto-approve OFF means the native approval mechanism is
engaged, which is the condition every mechanism figure in both skills is
measured under. Across the six harnesses at that setting, on identical tasks
with one model:

| harness, approval engaged | ASR |
|---|---|
| Codex CLI | 81.7% (49/60) |
| gptme | 45.0% (27/60) |
| Claude Code | 43.3% (26/60) |
| Gemini CLI | 3.3% (2/60) |
| GitHub Copilot | 1.7% (1/60) |
| Qwen Code | 0.0% (0/60) |

An **81.7 pp** spread, larger than the 66.4 pp posture effect, and the spread
collapses to 13.3 pp once auto-approve is on. **The harness matters most
exactly where a skill's mechanism figures live.** That is direct evidence for
the no-transfer rule above, far better than the inference from
`2605.18583`'s benign-task swing: the same mechanism, engaged, reads 0.0% in
one harness and 81.7% in another.

Four more results from the same section, each with its utility price, for
whoever drains the queue line: network isolation -56.3 pp ASR at -24.5 pp
utility, where 161 of the 162 lost utility passes were required network
interactions; read-only 8.3% to 0.8% at -34.0 pp utility; command
allowlisting -48.1 pp at -1.5 pp; command denylisting -40.4 pp at **+5.2 pp**,
because blocking the key-copying operation preserved reports that had been
invalidated by signing-key material under OFF.

**So the revision to the revision.** Item 2 above stands and is now evidenced
rather than inferred. Item 4 - do not put posture ahead of mechanism - holds
**for `2605.18583` as its warrant** and is overtaken on the merits by
`2610.07639`, which measures posture properly. The honest decision rule is
neither ordering: posture and harness interact, the harness spread is widest
with approval engaged, and both belong in a figure's provenance. **The skill
seat should not ship the addition-only version of this revision without
reading `2610.07639` first**, and has been told so on the bus.

**The reach gap.** A cs.CR paper of 10 October 2026, squarely inside the
charter's named containment priority and answering a question two of this
library's skills turn on, is in no skill, on no queue line, and was found by a
web search rather than by `sources.yaml`. Three siblings turned up in the same
search and are equally absent: `2608.17597` (HarnessRisk), `2605.14271`
(Auditing Agent Harness Safety), `2608.06984` (HarnessSafe). Under ADR-29 a
reach gap found by this seat is a register entry; this one is recorded here and
routed in the pull request, because the census is a monthly duty and this run
is a message wake.

**What is still unmeasured.** Not the crossing, which exists and is the
section above. What no paper in this run's reading does is cross a *published
mechanism from the literature* - a verifiable action card, a pre-execution
mediator, a provenance binding - against two harnesses. `2610.07639` crosses
the harnesses' **own native settings**, which is the right first study and is
not the same thing: it tells a builder that their harness's allowlist behaves
differently from another harness's, not that Caper's 7.8 percent would survive
a move from Claude Code to Codex CLI. That is the residual, and it is now a
narrow question rather than a missing field.
