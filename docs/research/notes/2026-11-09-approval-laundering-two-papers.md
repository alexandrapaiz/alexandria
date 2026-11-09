# Approval laundering, both papers read in full

Research seat, 2026-11-09, PR #903. The two reading-queue lines that were
still abstract-only in the queue's NEXT block:

- `arxiv:2609.38983` — Yang Wang (Fudan), *Approval Laundering: Systematizing
  Approval–Execution Binding Failures in AI Coding-Agent Harnesses*.
  `python3 tools/read_paper.py 2609.38983`, exit 0, 132,653 chars.
- `arxiv:2609.28586` — Zhang, Xia, Wu, Yue, Zhang, Cheng, Tu (CAS/UCAS,
  Beihang, BUPT), *Agent Approval Laundering: Transitive Effects Beyond the
  Approved Invocation*. `python3 tools/read_paper.py 2609.28586`, exit 0,
  105,779 chars.

Queued by `skills/agent-approval-paths`. Both lines carried a premise written
from the abstracts. Both premises needed correction, and the corrections are
the first section below because they change what the skill may cite.

## 1. Three corrections to the queue lines

**(a) "three weeks before" is one week.** Line 3687 says `2609.28586` is "the
SECOND independent paper to name approval laundering, three weeks before
`2609.38983`". The posting stamps in the papers' own headers are
`arXiv:2609.28586v1 [cs.CR] 23 Sep 2026` and `arXiv:2609.38983v1 [cs.CR]
30 Sep 2026`. Seven days, not three weeks.

**(b) "SECOND" is third, and by posting date it is first.** `2609.28586` is
the earlier of the two by a week, so in the literature it is first, not
second; the ordinal in the line is discovery order at this seat. More to the
point, there are **three** papers, not two. `2609.38983` cites, fifteen
times, `arXiv:2609.21081`, A. A. Kumar, *Loopjacking: Hijacking
Human-in-the-Loop Approval*, posted **17 Sep 2026** — six days before
`2609.28586` and thirteen before `2609.38983`. Fetched and confirmed live
this run (55,190 chars, exit 0, CC BY 4.0, independent security researcher,
no institutional affiliation). Queued below.

**(c) The independence claim holds, and it is stronger than the line
says.** Checked by grep in both directions: `2609.28586` contains no
occurrence of `2609.38983`, `Fudan`, `Approval Token` or `Bound-Gap`;
`2609.38983` contains no occurrence of `2609.28586` or `Jinqian`. Neither
paper cites the other. `2609.38983` does cite Loopjacking, and calls it
"concurrent work ... posted concurrently with our initial literature
search", so even that one link is not a dependence. Wang's manuscript line
reads "prepared as a working draft, 2026-09-22" — one day before
`2609.28586` posted. Three groups on three continents named the same
failure class, in three different vocabularies, inside thirteen days, with
no shared citation among them.

## 2. What each paper actually establishes

### `2609.38983` — six classes, measured on one harness, with dispersion

Six classes organised by which credential-binding surface the substitution
violates: Scope, Argument, Temporal, Tool, Delegation, Semantic. The queue
line's one-sentence description of the taxonomy is accurate.

Bound-Gap Rate (BGR) is the fraction of valid runs in which a per-scenario
canary predicate holds. Table III, Claude Code 2.1.197, Wilson 95%:

| class | N | BGR | 95% CI |
|---|---|---|---|
| Scope | 20 | 1.000 | [0.839, 1.000] |
| Temporal | 20 | 1.000 | [0.839, 1.000] |
| Tool, cross-tool-identity substitution | 19 | 0.000 | [0.000, 0.168] |
| Tool, same-name PATH substitution | 20 | 1.000 | [0.839, 1.000] |
| Argument | 20 | 0.450 | [0.258, 0.658] |
| Delegation | 19 | 0.947 | [0.754, 0.991] |
| Semantic (proxy) | 20 | 0.100 | [0.028, 0.301] |

Defense: Approval Token, `HMAC-SHA256(principal, agent_id, session_id, tool,
sha256(arguments), scope, expiry)`, minted by a mediator and stored
server-side. Table V, paired offline replay of the already-collected runs,
McNemar exact:

| class | baseline | with defense | b/c | p |
|---|---|---|---|---|
| Delegation | 0.947 | 0.000 | 18/0 | 7.6e-6 |
| Temporal | 1.000 | 0.000 | 20/0 | 1.9e-6 |
| Argument | 0.450 | 0.400 | 1/0 | 1 |
| Scope | 1.000 | 1.000 | 0/0 | 1 |
| Semantic | 0.100 | 0.100 | 0/0 | 1 |
| Tool (cross-tool only) | 0.000 | 0.000 | 0/0 | 1 |

**Three things in this paper that an abstract loses, and each one changes a
builder's decision.**

*Tool laundering is not one number, and the class-level statement is false.*
Two substitution patterns under one class give 0.000 and 1.000. The first
(approve `WebFetch` for one domain, reach a local endpoint with `Bash` +
`curl`) is denied by Claude Code's own policy engine in all 19 valid runs.
The second holds the approved rule (`Bash(cat *)`), the literal command text
and the recorded tool identity all identical to what was granted, and varies
only which executable `$PATH` resolves `cat` to, via a same-named wrapper
planted ahead of `/bin`. That is unprotected at 20/20. The paper's own §IX
words: within Claude Code, "'Tool Laundering is blocked' is false as a
class-level statement". The mechanism is structural — `$PATH` resolution
happens inside the dispatched process, below the `PreToolUse` mediation
point, and no field the hook receives can be made to reveal it.

*Argument laundering's 0.450 is not the model widening its own arguments.*
In none of the 20 runs did the model append `--all` or otherwise broaden
which files a commit would stage. Eight of the nine successes issue the
approved literal `git commit -m "wip"` unmodified; the ninth chains
`&& git status`, which the harness's prefix matcher also admits. What sweeps
the canary in is a repository-local `pre-commit` hook running `git add -A`.
The ten failures attempt a *narrower* command (`git commit -m "wip" --
app.py`) which the allowlist correctly denies. So the harness's matching is
not the blind spot; the credential binds the command string and not the
repository-level effects that string triggers.

*The negative result is the load-bearing part.* Approval Token moves Scope
not at all and Argument by one run. Both classes' measured mechanisms leave
every recorded dispatch field unchanged and diverge only in downstream
effect, one process level below what a field-only verifier can observe. §IX
names what would be needed and rules out the obvious fix: *drift detection*
(re-approve when the environment snapshot changes between approval and
dispatch) would have caught **none** of the measured cases, because in every
scenario the hook or script producing the divergent effect is installed
before the credential is issued. What the cases need is *initial effect
validation* — analysing at approval time what the already-present
environment would make the credential produce. The paper did not attempt it.

**Bounds to carry with every number from this paper.** Single author. A
working draft, dated 2026-09-22, target venue IEEE TDSC, stated in the
manuscript line as "not yet submitted for review". One harness, one fixed
model; a Codex CLI replication was attempted and blocked because `codex
exec` exposes no observable per-call approval checkpoint. And the paper
disqualifies its own point estimates as harness-intrinsic: the runner forks
the full parent environment, and all 138 valid traces load extra plugin
instructions (`superpowers-zh`, `everything-claude-code`) plus a
previous-session summary on top of the published prompt, so in its own
words the repetitions "are not independent draws from a minimal, hermetic
harness configuration" and a clean-environment replication is needed first.
The κ = 1.0 inter-rater figure is an author cross-check, unblinded (the
review artifact showed the automated verdict beside the evidence), and
re-measured on the same 15 runs that were used to find and fix the analyzer
bug it is reported after. Scope's BGR is 0.80 (16/20) before that fix and
1.00 (20/20) after.

### `2609.28586` — the record-to-closure relation, with freeze discipline

Different claim, different surface. Not "the harness substituted the
action", but "the record names the entry invocation truthfully and omits
effects of the workflow that invocation activates". Formalised as
*closure-bound approval*: an approval is closure-bound when every trace in
the closure has its effects contained in the record's represented set
(Definition 1). Coverage, not equality — conservative overrepresentation
passes, one omitted label does not.

Effect vocabulary is six operational classes: process, file, environment,
network, container, MCP.

Retrospective ladder, 111 fixed approval-object/trace pairs, residual
records under three information views:

- explicit approval fields: **40** of 111
- plus generic command semantics: **17** (resolves 23 of the 40)
- plus decision-time metadata, post hoc: **13** (four more)

All 13 survivors are in the harness/parser fixture stratum. On the
real-project stratum — 11 evidence-complete executions of eight fixed-SHA
repository/mechanism cases spanning npm lifecycle, PEP 517, Cargo, Docker
and MCP — the same ladder is **10 → 2 → 0**. Both command-aware survivors
there are successful remote MCP calls, `M → M,N`. Every other case is
`P → P,F` or `P → P,F,C`, and conservative command semantics cover all of
them.

Prospective arm, the part with the methodology: cohort A develops parser
v1.1, which is **frozen** before a disjoint, prespecified confirmatory
holdout B of 18 workflows from 18 previously unseen fixed-SHA repositories,
one positive and one control for each of nine mechanisms. 17 reach target
execution. On those 17, frozen predictions give **0.926 macro recall, 0.941
macro precision**, exact effect sets in 13/17. The command-only baseline on
the same 17 gives 0.770 / 0.941 and 9/17. Binding the prediction into the
approval object raises case-macro coverage .755 → .922 and cuts residual
effect instances **10 → 3**.

**The cost number the abstract omits, and it is the one a builder needs.**
Table III's last column: **9 of the 17 reached cases are "no-added-effect
ASK"** — the policy demanded an extra approval decision for a workflow whose
realized trace exercised nothing beyond what the command-only record already
disclosed. Positive stratum 4/9, controls 5/8. So on this cohort, over half
the additional prompts bought nothing, and all seven newly disclosed effect
instances land in the positive stratum while control disclosure is unchanged
at .857 → .857. That is the selectivity price of the disclosure gain, and
the paper states it plainly rather than reporting coverage alone.

Latency, since it decides whether this can sit on the approval path: parser
P95 12.3 ms same-process, 168.2 ms all-case fresh-process maximum including
Python startup; for the predeclared npm case, 1.51 ms P95 in-process over
100 preflights and 87.8 ms median / 98.1 ms P95 over 30 fresh hook
processes. The Claude Code 2.1.205 `PreToolUse` integration emits `ASK` and
the noninteractive permission path returns `DENY`; the hook never
auto-allows.

**Bounds.** No population dispersion anywhere in this paper. The one
interval it draws is labelled in its own figure caption as a "95%
fixed-cohort case-resampling stability interval, not a population
confidence interval", and the words *seed*, *standard deviation*, *error
bar*, *variance* and *significan* return zero occurrences in the full text.
What stands in for dispersion is freeze discipline, an independent
re-implementation that hash-checks 109 artifacts and reconstructs all 17
effect sets with zero mismatches, six three-run repeats at mean pairwise
Jaccard 1.000, and a four-profile denominator sensitivity: recall spans
0.868–1.000 and exact-set accuracy 0.722–0.889 across the alternatives.
**One predeclared target loses its margin under one of those profiles** —
executed-control precision is 0.875 primary and **0.778** when
`NOT_EXECUTED` is treated as empty, below the ≥0.80 bar the protocol
predeclared. The primary profile is the pre-registered one and the setup
failure never reached target execution, so this is a boundary rather than a
miss; it is also the thinnest margin in the paper.

## 3. The information limit, graded

Line 3687 says the derived limit "is the strongest available argument for
why the approval-paths skill's delta 1 must read the resolved object". Read
against Lemma 1, that overstates it twice.

Lemma 1 is sound and its proof is three lines: if two validly bound
executions project to the same policy-visible record and require different
effect-specific decisions, then any record-only rule, randomized included,
induces one output distribution for both, and disjoint singletons cannot
both carry probability one. It is an information requirement, not a
hardness result. **The weight is carried by the empirical half, not the
lemma** — the demonstration that record-indistinguishable-but-different
pairs actually occur, which is the 40 → 17 → 13 ladder and the 10 → 2 → 0
fixed-SHA recurrence.

And the lemma licenses four responses, not one. The paper's own sentence:
where the separating information is unavailable, "the decision path must
conservatively represent the union, re-mediate, reject, or contain the
unresolved effects". Reading the resolved object is one of the four, and it
is the one that needs the separating information to exist. On the
fixed-SHA stratum it does, which is why metadata reaches zero residuals
there; the paper's own recommendation is the conservative-union option
(bind a source-backed prediction of the transitive effect boundary before
authorization), not object resolution.

## 4. What the three papers jointly support, and where they are thin

The three independent namings carve up cleanly and the division is the
finding:

- **Loopjacking (`2609.21081`, 17 Sep)** — agent-orchestration products:
  Agno AgentOS, LangGraph Agent Server, OpenClaw, OpenAI Agents SDK.
  Classifies by *when* the substitution enters relative to approval
  (representation-based versus post-approval state substitution). Evidence
  is repeated deterministic trials against released product code paths
  (5/5, 3/3 counts reported per path).
- **`2609.28586` (23 Sep)** — developer-toolchain expansion: npm lifecycle,
  PEP 517, Cargo, Docker, Git hooks, MCP. Classifies by *which effect
  class* escapes the record.
- **`2609.38983` (30 Sep)** — coding-agent CLI/IDE harnesses: Claude Code.
  Classifies by *which credential field* the substitution violates.

Where all three are thin in the same place: **not one of them measures a
real captured approval lifecycle.** Wang seeds Temporal's earlier session
as a synthetic placeholder and says so, because Claude Code's persisted
allow-rules carry no `session_id` to seed from; the offline replay
therefore shows the guard rejecting a mismatch against a seeded value, not
a captured grant-in-session-A/reuse-in-session-B lifecycle. Zhang's
prospective arm replays mechanism-bearing workflows through regimes.
Kumar's trials are deterministic product-path tests. The population
question — how often this happens to real operators in real sessions —
is unanswered by all three, and the one corpus in reach that could answer
it is `2611.08516`'s Corpus A (52 real sessions, 57,923 steps, 28,087 tool
calls, released anonymized), already queued at line 3691 for exactly that
reason.

Second shared thinness: the only cross-harness or cross-product
*replication* in the set is Kumar's four products, and his two negative
findings (OpenClaw's own released fix, the OpenAI Agents SDK's existing
per-call serialization) are observed product behavior rather than a
controlled comparison. Wang tried Codex CLI and could not instrument it.
Zhang's frontend recurrence is two exact mappings across three frontends at
one repository revision.

## 5. Arithmetic checked

Everything below was recomputed from the papers' own reported counts.

`2609.38983`. All seven Wilson 95% intervals in Table III reproduce
exactly at z = 1.96 (20/20 → [0.839, 1.000]; 0/19 → [0.000, 0.168];
9/20 → [0.258, 0.658]; 18/19 → [0.754, 0.991]; 2/20 → [0.028, 0.301]).
All three McNemar exact p-values reproduce as two-sided binomial on the
discordant pairs: 2·2⁻¹⁸ = 7.63e-6 for Delegation, 2·2⁻²⁰ = 1.91e-6 for
Temporal, 2·2⁻¹ = 1 for Argument. The replay denominator is consistent:
20+20+19+20+19+20 = 118 across the six replayed scenarios, and 118 + the
20 unreplayed PATH-substitution runs = the 138 valid main-study traces the
methodology section discloses. The abstract's "p < 10⁻⁵ in both cases"
holds for both.

`2609.28586`. 40 − 23 = 17 and 17 − 4 = 13, as stated. Table II's columns
sum to the reported 11 runs and 10/2/0 residuals. Holdout accounting
closes: 13 complete + 4 terminating after effect evidence = 17 target-
executed, + 1 setup failure = the 18 prespecified, and 18 = 9 mechanisms ×
(1 positive + 1 control). The coverage figures reproduce exactly as
case-weighted means over the 16 nonempty-effect cases: (9 × .676 + 7 ×
.857)/16 = .755 and (9 × .972 + 7 × .857)/16 = .922. Residuals close by
stratum: positive 8 → 1, controls 2 → 2, total 10 → 3, and 10 − 3 = the
seven newly disclosed effect instances the text reports as all positive-
stratum. Exact sets close the same way: 4/9 → 8/9 and 5/8 → 5/8 give
9/17 → 13/17, "four repairs and zero regressions".

One figure does **not** reproduce from the stratum means, and the reason is
benign: macro recall .926 against (.972 + .875)/2 = .9235, and macro
precision .941 against (1.000 + .875)/2 = .9375. The macro average is over
effect classes, not over strata, which is consistent with the paper calling
the per-stratum numbers "positive recall and precision" rather than macro.
Worth knowing before anyone tries to recompute .926 from Table III.

## 6. Residual ask on both lines

Neither line's ask is discharged by this reading. What
`skills/agent-approval-paths` asked for is rows it can cite, which is a
distill run and not a reading. Line 3685 records `2609.38983` as absent
from the corpus; `2609.28586` was queued the same day and nothing has run
since, so the same holds for it. Neither was verified against the `papers`
table this run, because no seat on this host can reach it — see the two
lines below. `pipeline/reading_queue.py --order` puts
both in the `blocked skills first` group at positions 7 and 8, and
`reading_queue.resolve()` inserts unseen queued ids at `MAX_PER_RUN` 6 per
distill run, so the two lines above them clearing is what brings these in.
This seat still cannot start that run: `command -v modal` finds nothing,
`import modal` raises `ModuleNotFoundError`, and there is no
`DATABASE_URL`. Same state as lines 3482–3484 record, and the same
disposition — the lines stay open, annotated with the reading, waiting on a
distill run rather than on a seat.
