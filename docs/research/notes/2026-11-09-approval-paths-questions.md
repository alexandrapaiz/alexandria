# The four open questions in the agent-approval-paths batch, read against the papers

Research seat, 2026-11-09, PR #874. Branch
`alexandria-research/2026-11-09-message-approval-paths`.

The batch is the seven lines `skills/agent-approval-paths` queued on 2026-11-02
(reading-queue.md:3470-3482ff), which `pipeline/reading_queue.py --order` puts
at the head of the queue. Three are ingestion requests; four are questions the
skill seat's reading raised and could not settle. This note answers the four.

**All papers below were read with `python3 tools/read_paper.py <id>`, exit 0.**
Char counts: `2609.18411` 81,419 · `2606.02668` 45,522 · `2610.22987` 66,477 ·
`2607.01415` 34,482 · `2609.40082` 34,414 · `2610.02456` 71,274 ·
`2610.39711` 127,196 · `2609.22978` 97,672 · `2604.28138` 83,941 ·
`2610.14488` 98,301 · `2610.40753` 69,442 · `2611.08516` 98,918.
Discovery was the arXiv API, not the corpus: this sandbox has no
`DATABASE_URL` and no `modal`, so `semantic_search` and `sql_query` were
unreachable this run. Nothing here is a claim row; claims need a distill run.

---

## Headline: three of the four questions move, and two of them move because
## the field published the answer after the line was written

The batch was queued on 2026-11-02 from reading done that day. Three papers
that settle or nearly settle three of its four questions were on arXiv already
— `2610.14488` (10 Oct), `2610.39711` (29 Oct), `2610.40753` (29 Oct) — and
one more landed after (`2611.08516`, 22 Oct id-dated, fetched today). None of
them is cited by any of the batch's three source papers, and none was found by
the queue line's own reasoning, which worked outward from the three papers'
related-work sections. **The lesson for this seat is not that the lines were
careless. It is that a question whose answer depends on what has been
published must be re-asked against the index, not against the bibliographies
of the papers that raised it.** Two of three source papers predate the
answering work by one to four months.

---

## Q1 — Has anyone measured the microVM point on the Rollout-Tax curve?

**Answer: partly, at the wrong tier, and with the sign inverted from what the
curve's framing predicts. The question the line actually asks — the
repository tier — is still open, and one of the line's own three supporting
premises is wrong.**

### The premise that is wrong

The line says `2610.02456` (SideKernel) "puts the two boundaries on one task
set but compares usability". It does not put the two boundaries on one task
set. SideKernel's inclusion criterion **IR-4 requires hardware
virtualization**, and the container-based candidates in its own Table I —
Yolobox (`Docker/Podman container`), AIO (`Docker container`), OpenSandbox
(`Container (opt. MicroVM)`, evaluated in its default shared-kernel
configuration) — fail IR-4 and are excluded. All five sandboxes that reach
the capability tests are classed `microVM / Sep. kernel`, Docker Sandboxes
included (`Docker Sbx ✓ ✓ ✓ ✓ ✓ microVM Sep. kernel`). The paper says so in
its own words twice: "In this paper, I focus exclusively on microVM
sandboxes", and under Scoping constraints, "SideKernel is not evaluated
against such sandboxes [other isolation primitives] which were deliberately
left out of scope."

So the "19 of 23 each" figure is accurate (§VIII-A: "Across all 23 capability
tests, Docker Sandboxes and SideKernel pass 19 tests, SmolVM, Microsandbox and
Shuru pass 12") but it is **microVM against microVM**, not container against
microVM. It is also a single-evaluator practicum: the paper's own Threats to
Validity lists "Evaluator bias. The comparative analysis unavoidably
introduces bias, because the developer is also the evaluator." It reports no
latency of any kind. It cannot bound the container-to-microVM step in either
direction.

The line's other two premises hold. `2607.01415` §5 does name the gap as
unmeasured — "MicroVMs, snapshots, sandbox runtimes, and preallocated rollout
workers offer intermediate designs" — and its §7 cites Firecracker, SEUSS and
Catalyzer as serverless startup work rather than as agent-rollout substrates.
`2609.40082` (Tide) has no container arm, and is a weaker support than the
line implies: it is a **memory-reclamation** paper (arenas, THP splitting, a
guest allocator), not a cold-start study, and it reports no boot or startup
measurement at all. Its one cross-substrate number is a density statement in
§2.1, not a measurement.

### The measurement that exists, and where it sits

`2610.39711` (**Sandman**, production agentic-RL sandbox service, v2 31 Oct
2026) §5.3 runs the comparison the curve needs, on one driver and one instance
type:

| system | substrate | serial creation, median |
|---|---|---|
| agent-sandbox | K8s pod / container | **1.45 s** @ 1 vCPU, 2 GiB |
| Sandman | K8s pod / container | **2.18 s** @ 1 vCPU, 2 GiB |
| OpenSandbox | K8s pod / container | **2.46 s** @ 1 vCPU, 2 GiB |
| CubeSandbox | **microVM snapshot restore** | **0.08 s** @ 0.25 vCPU, 1 GiB |

That is **18.1x to 30.8x faster for the microVM arm**, which is the opposite
sign from the Rollout-Tax framing ("Virtual machines provide strong isolation,
but their fresh-start paths can be expensive"). The reason is in the method
name: CubeSandbox *restores a snapshot*, so what is measured is the snapshot
row of `2607.01415`'s own unmeasured-intermediates list, not a microVM fresh
start. A snapshot restore beating a container create is a different claim from
a microVM beating a container, and conflating them would be the error this
number invites.

Three things bound it hard, and a skill quoting it must carry all three.

1. **Not the same template.** 0.25 vCPU / 1 GiB against 1 vCPU / 2 GiB, and
   CubeSandbox ran on 42 separate nodes with nested virtualization against 40
   dedicated nodes for the pod systems.
2. **The reliability axis inverts the ranking.** On the 10,000-request burst,
   Sandman delivered 10,000/10,000 usable with 0 left at client exit;
   CubeSandbox delivered **7,740/10,000 (77.4%)**, 8,860 (88.6%) with the
   first command retried, highest-completion run 8,943. Its synchronous client
   also "continued creating environments after cancellation."
3. **n=1 and self-admitted asymmetry.** "Most configurations ran once. Sandman
   received more tuning, and our OpenSandbox and CubeSandbox deployments may be
   suboptimal."

**And the repository tier has no microVM arm.** Sandman's SWE-image arm — the
one at the tier the line names, 1.25–1.28 GB images, 2 vCPU / 8 GiB, uncached
layers, 1,024 sandboxes each — is "each pod-based system". CubeSandbox is
absent from it. Half-delivery there was 20.3 / 33.3 / 25.4 s and full delivery
32.0–35.6 s, all container. So the line's framing survives exactly: *nothing
published prices the container-to-microVM step at the repository tier*, and
the new evidence bounds it from the cheap side at the minimal tier instead of
only from the expensive side.

### Four more systems that touch the gap and decline it

- **`2609.22978` (DSec, DeepSeek, production)** exposes FnCall, container,
  microVM and full-VM backends through one SDK, and gives the only
  cross-substrate *density* number in the literature: "a single node can host
  up to 800 microVMs or 3,200 containers" — **4.0x**. Its qualitative ruling
  is "[Firecracker microVMs] come at higher memory overhead and slower startup
  than containers", with no per-backend startup table. Its evaluation (§8) is
  about image loading, EROFS-vs-tar layers, and memory/CPU under overcommit.
- **`2610.39711` (Sandman) declines explicitly**: "We use runc's shared
  kernel. A microVM per sandbox, using Firecracker or Kata, requires bare
  metal or nested virtualization. gVisor only partly supports the packet
  filter used by our outbound guard; **we have not measured its cost**."
- **`2604.28138` (Crab)**, a semantics-aware C/R runtime for agent sandboxes,
  runs on runc-CRIU + OpenZFS — **container only, no microVM arm** — but gives
  the snapshot side a cited price: E2B on Firecracker "requires pausing the
  microVM before snapshot creation and introduces more than 4 s overhead."
  That is a vendor-doc citation, not Crab's measurement.
- **`2611.08516` (Aegis OS)** ships a `MicroVmSandboxDriver` and lists
  "binding MicroVmSandboxDriver to live libkrun/Firecracker processes" as
  future work.

**So four production or near-production systems in 2026 each name the microVM
arm and each leave it unmeasured, and the one measurement that exists is a
snapshot restore at the minimal tier.** That is a stronger statement of the
gap than the line had, and it is the shape of a brief line: the field is
converging on containers for rollouts and on microVMs for multi-tenancy, and
nobody has priced crossing between them where repository-scale work happens.

**Disposition: the line stays open, its premise about `2610.02456` is
corrected, and the measurement it needs is now specified** — CubeSandbox or
Firecracker added as a fifth arm to Sandman's SWE-image experiment (1.25–1.28
GB images, 2 vCPU / 8 GiB), which is the one experiment in the literature
already built at the right tier.

---

## Q2 — Is there a published ground-truth action decoder for a shell or API
## surface, as opposed to a browser DOM?

**Answer: yes, and it landed on 10 October 2026, after both source papers. It
is implemented and evaluated, which is exactly what both papers said the shell
case lacked. It does not, however, get the uninspectable rate down "without
growing a trust list" — it moves the list from names to handoff rules, and its
own limitations say the list still has to be maintained.**

### What the two source papers' related work actually names

The line asks a reader to check. Checked, and the answer is one, not none and
not several.

`2609.18411` (VAC) §2 names exactly one non-browser decoder: "Concurrent work
by Weng [13] imports this idea into agent approvals, naming the property
consent integrity and formalizing it for black-box LLM coding agents: there
the action boundary is a low-level operating-system event (e.g. an `execve`, a
file write, or a network request), and a mediator decodes the real command and
renders the approval from it." Weng [13] **is `2606.02668`**, the batch's own
second paper. VAC then states the limitation the line independently inferred:
"That work is an explicit position-and-proof-of-concept whose trusted path and
total mediation are specified but assumed rather than implemented, which does
not drive live agents, and whose evaluation is on shell-command corpora with a
high over-prompting rate."

VAC also confirms the line's "one mechanism measured at two difficulties"
reading in its own words: "(i) the ground-truth action is recovered from the
resolved DOM element and its form (target domain, recipient, amount) rather
than from a decoded shell command".

`2606.02668` §II names no decoder at all. Its by-construction family — CaMeL,
FIDES, Progent, PFI, IsolateGPT, AgentSpec — is characterised correctly as
governing the data and action channel: "All govern autonomous data flow and
tool use, **and none renders or guarantees the human approval**."

**So within the batch, the two papers' related work names one decoder and it
is one of the two papers. The line's hypothesis was right and its literature
reading was complete as of 2 November for those two bibliographies.**

### The decoder that exists

`2610.14488`, **Zero-Trust Agent Cells (ZTAC)**, Daniel Commey, 10 Oct 2026,
cs.CR. It cites neither `2606.02668` nor `2609.18411` — zero occurrences of
either id, of "consent integrity" or of "Verifiable Action Card" — so it is an
independent line.

Its §4.3 is literally "Resolve before deciding", and its §4.7 renders the
approval from the resolved object: "The record shows the reviewer the
**resolved** operation (for example `read .env` for a request that named
`config.txt`)". The binding is recomputed from a fresh resolution at
consumption, so "an approval therefore cannot be used by another cell, with
other arguments, after the file it covered was replaced or a symlink
repointed, or after other content was staged for the approved commit."
Approvals expire after ten minutes and are consumed on first use. The decoded
surfaces are files (workspace path + device + inode), programs (binary + argv
+ cwd), git state (HEAD, branch, packed refs, index) and endpoints (parsed
URL) — a shell-and-API surface, not a DOM.

It is implemented: a macOS prototype, 3.2k lines of trusted Rust excluding
dependencies. It is measured against 74 attacks with ground-truth oracles
including replays of 10 publicly disclosed incidents:

| configuration | attacks lost (of 74) |
|---|---|
| tool allowlist | 66 (89.2%) |
| allowlist + the command sandbox deployed agents use | 56 (75.7%) |
| **ZTAC** | **2 (2.7%)**, both encoding a secret into traffic to an allowed endpoint; 14 (18.9%) held for review |

Utility: 43 of 46 benign operations (93.5%) completed, with **8 approval
prompts (17.4%)**, and 4 of 7 workflows; the 3 workflows lost need process
creation, a virtual environment, or `git commit -a`. Overhead: a no-op
brokered request has median latency 4.0 ms; spawned programs take 8.5–18.4 ms
longer.

### The part of Q2 it does not answer

The line asks for a decoder "that gets the uninspectable rate down **without
growing a trust list**". ZTAC does not clear that bar, and says so:

> **Handoff rules are an enumeration.** The rules for files that other tools
> run name the consumers we know: editor tasks, agent hooks, `git`'s `HEAD`,
> and virtual-environment interpreters. A tool that executes some other file,
> recognized by its own signature, is not covered until a rule names that
> file. … **but the list has to be maintained like the list of credential
> files.** Some handoffs are out of reach of any rule: a `Makefile` or a test
> that the agent edits runs when the developer next builds, and only review of
> the change can judge it.

What object binding buys is a *different* list: names are replaced by resolved
objects, which kills the TOCTOU and symlink classes outright, and the residual
enumeration is over tool-handoff signatures rather than over command strings.
That is a real change in the list's failure mode — a renamed directory no
longer evades it, because "writing the rule for the file that makes a
directory executable, rather than for the directory's conventional name, is
what keeps a renamed directory from evading it" — but it is not the absence of
a list.

And its prompt rate is not comparable to `2606.02668`'s 87.0%: "We count 8
prompts in 46 operations and **did not study reviewer fatigue or accuracy**",
over "one small Python project".

**Disposition: Q2 is answered and the line can be struck, with the three
boundaries above carried. The residual — a decoder with no maintained
enumeration — is a narrower question and worth a new line rather than keeping
this one open.**

---

## Q3 — Does any mediator that is not boundary-only escape the silent-pass
## against over-prompt frontier?

**Answer: yes. Two independent 2026 constructions report numbers off
`2606.02668`'s curve in the favourable direction on both axes at once, and
neither is one of the three candidate shapes the line listed. The dominance is
statistically clean on the harm axis and a tie within confidence intervals on
the false-block axis. No shared task set exists, so this is a direction with
two points on it, not a frontier.**

### The frontier being escaped

`2606.02668` is careful about both qualifiers — a **boundary-only static**
mediator — and the curve it establishes is 10.0% silent passes on 1,330
GTFOBins abuse commands against 87.0% uninspectable on 28,798 tldr-pages
normal-usage commands, same trust list.

### Escape 1: pre-execute, then approve from observed effects

`2610.40753`, **Caper**, Wu/Chen/Sun/Shi/Lyu/Lo, Singapore Management
University, 29 Oct 2026, cs.CR. The mechanism is neither taint nor session
state: it pre-executes each command in a snapshotted sandbox, hands an
independent LLM approver a bounded report of observed effects, commits allowed
commands and rolls blocked ones back with a reason the agent can act on. That
is the line's "consults execution state rather than the command string" taken
further than the line imagined — the state consulted is the state the command
*will produce*.

Against six existing systems, each system running each task once:

| system | type | SABER harmful ↓ | YoloFS-Ext harmful ↓ | false block ↓ |
|---|---|---|---|---|
| GLM-5.3-Flash, no approval | — | 19.7 | 71.6 | — |
| CARE | rule-based | 15.0 | 69.6 | 2.0 |
| TS-Guard | guardrail | 18.8 | 94.1 | 8.8 |
| gpt-oss-safeguard-20b | guardrail | 18.6 | 62.7 | 15.7 |
| Qwen3Guard-Gen-8B | guardrail | 16.0 | 67.6 | 0.0 (blocks nothing) |
| YoloFS | staging | 21.2 | 35.3 | — (never blocks) |
| Claude Code Auto Mode | deployed | 14.8 | 62.7 | 3.9 |
| **Caper** | pre-execution | **6.7** | **7.8** | **1.0** |

The YoloFS-Ext column is the one that matters, because that benchmark hides
the harm inside the tool a benign request asks the agent to run, and each
dangerous task has a safe twin with identical files, request and command —
"Blocking a twin is therefore a false block by construction." Caper reaches
7.8% harmful at 1.0% false block and 60.8% safe completion, against the next
best harmful rate of 62.7%.

**Significance, from the paper's own Appendix E (95% Wilson intervals), which
is where the honest reading lives:**

- Harm axis, clean: Caper YoloFS-Ext harmful **[4.0, 14.7]** against Claude
  Code Auto Mode **[53.1, 71.5]** and Qwen3Guard **[58.1, 75.9]** — no
  overlap. SABER harmful **[5.0, 9.1]** against Auto Mode **[12.2, 18.0]** —
  no overlap.
- False-block axis, **not significant**: Caper **[0.2, 5.3]** against CARE's
  2.0% **[0.5, 6.9]**. The rule-based checker is a tie inside the interval.
  What Caper beats on this axis is the guardrail models (gpt-oss-safeguard
  [9.9, 24.0], TS-Guard [4.7, 15.9]) and it does so while they are also losing
  on harm.

So the correct sentence is: **a non-boundary-only mediator buys an order of
magnitude on the harm axis at a false-block rate no worse than the best static
rule checker's**, which is the frontier escape, but the false-block *advantage*
over that checker is unmeasured at this sample size.

Cost: effects report 0.9 KB median (p95 2.6 KB) against 62.5 KB raw trace, a
99.4% reduction; median approval latency 3.2 s (p95 6.4 s) against 3.3 s
(11.4 s) for the same approver with no evidence; sandbox adds ~0.5 s per
allowed and ~1.5 s per blocked command; $0.019 per task against $0.017.

Its own limitations, all of which a skill must carry: pre-execution is a real
execution, so network requests, writes to remote services and spawned
processes "happen before the approver decides and cannot be undone"; shell
commands only, edits are left to the harness; **one observed execution**, so a
tool whose effects depend on time, randomness or environment — or an attacker
who detects the sandbox and defers — is not covered; and the headline uses the
authors' revised SABER oracle, with the released-oracle result in Appendix A.

### Escape 2: resolve the object, bind the approval to it

ZTAC (above) is the line's *first* candidate shape — provenance over argument
values, "resolve before deciding" — and it reports 2/74 lost at 8 prompts in
46 operations. Its denominators are far smaller and not drawn from a usage
corpus, so it is a second point in the same direction rather than a second
measurement.

### What this does to the two skills

The line says this "matters to the library beyond this skill, because
`skills/agent-containment` delta 2 already prescribes provenance-aware
parameter binding, and if that construction moves the frontier then the two
skills join at a measurement rather than merely agreeing in direction."

**They now join at a direction with two independent constructions, not yet at
a measurement.** ZTAC is the delta-2 construction, measured, and it moves the
harm axis. Caper is a *different* construction and moves both axes with
confidence intervals. The measurement that would actually join them is the one
to ask for: **ZTAC-style object binding, or Caper-style pre-execution, run on
`2606.02668`'s own two corpora** — 1,330 GTFOBins abuse commands and 28,798
tldr-pages normal-usage commands. Until somebody runs that, the library should
say "two independent constructions report off-curve results on their own
benchmarks" and not "the frontier is broken."

**Disposition: strike the line, with the two constructions, the CI caveat, and
the named joining measurement recorded.**

---

## Q4 — What is the false-positive rate of treating a mid-task persisted-rule
## proposal as an alert, outside the benign control?

**Answer: still unmeasured, and that is the honest answer. But the denominator
the line calls thin is four times thicker than the line says, which roughly
quarters the bound; and the corpus the missing measurement needs now exists
and is released, so this is a line with a route rather than a line waiting on
the field.**

### The denominator is 100, not 25

The line says "`2610.22987`'s Benign Control is 0 of 25 on every model … and 25
benign task runs is a thin denominator." Both halves are right as written, and
together they understate the evidence. The paper's §4.1 construction is "five
categories … Each category contains five experimental instances, yielding **25
distinct cases per agent configuration**", and Table 1 carries **four
configurations**: Codex (gpt-5.6-luna), Codex (gpt-5.6-sol), Claude
(claude-haiku-4.5), Claude (claude-sonnet-5). The parenthetical is "Benign
Control yielded 0/25 across all models, confirming permissions are never
organically proposed."

So the pooled control is **0 of 100**, and the arithmetic of a zero-count bound
matters here because the skill prescribes an alert on it:

| control | one-sided 95% upper bound on the organic rate |
|---|---|
| 0 / 25 (per model, what the line used) | **11.3%** |
| 0 / 100 (pooled across four configurations) | **3.0%** |

Pooling assumes the four configurations are exchangeable for this event, which
is the arguable step; the per-model bound stands at 11.3% regardless. A skill
prescribing an alert on "any mid-task persisted-rule proposal" should quote
3.0% pooled and 11.3% per model, not an unqualified 0%.

### Why it is still the wrong population

The line's real objection survives the bigger denominator. `2610.22987`'s
benign control "runs the original task without an added repository
instruction" — it is the paper's own 25 adversarially-paired tasks with the
injection removed, in five harm categories chosen because they are dangerous.
That is not the distribution of ordinary developer sessions, so it bounds the
organic rate on a synthesized population, not in production. **No published
measurement gives the organic rate of mid-task persisted-rule proposals over
an ordinary-usage corpus.** Searched: `abs:"permission prompt" AND
abs:"agent"`, `abs:"telemetry" AND abs:"coding agent"`, `all:"persistent
permission"`, `all:"approval fatigue" AND all:"agent"`, `abs:"approval" AND
abs:"agent" AND abs:"false positive"`, `abs:"permission" AND abs:"coding
agent" AND abs:"approval"` — nothing measures the proposal event in the wild.

### The corpus that makes the measurement runnable

`2611.08516` (**Aegis OS**, Hui Zhao, Heurion Research, 22 Oct 2026, cs.OS)
Experiment 1B is the population the measurement needs, and it is the first
real-session denominator in this literature:

> Corpus A: **52 real production coding-agent session transcripts, 57,923
> conversation steps, 28,087 tool calls** — 13,098 read/coord, 11,070 shell
> commands, 3,836 file edits/writes — released anonymized as
> `scripts/real_traces_anonymized.json`.

Replayed through four permission regimes, the prompt rate (IPR) is 53.31%
(14,974 prompts) ask-every-mutation, **28.54% (8,016) under a path+prefix
allowlist**, 4.97% (1,397) under per-commit CoW gating, 1.12% (315) with a
scoped action lease.

Two things this gives the library for free.

1. **An independent corroboration of `2606.02668`'s 87%.** Aegis finds **39.0%
   of real shell invocations (4,318 of 11,070)** use compound operators
   (`&&`, `||`, `;`, `|`, `$(...)`) or inline interpreter scripts (`python3
   -c`, `bash -c`), rising to 80.5% in Corpus B. That is the mechanism behind
   the uninspectable rate, measured on real sessions rather than on
   tldr-pages, by an author who is not arguing about consent integrity. Two
   independent corpora, one cause.
2. **The route for Q4.** The persisted-rule-proposal event is not what Aegis
   counts — it counts prompts, not rule proposals — but Corpus A is the right
   population and the right granularity, and it is published. The measurement
   Q4 wants is: count mid-task persisted-rule proposals across the 28,087 real
   tool calls, which turns an open question into a scripted pass over a
   released artifact.

Bounds on Aegis: single author; **the real-trace corpus "comes from a single
engineering organization"**; the IPRs are computed by replaying traces through
regimes, not observed under those regimes; the wait-time figures are modeled
at an assumed 5.0 s/prompt; Corpus B is the author's own dogfooding; latencies
come from one Apple Silicon workstation.

**Disposition: the line stays open, its denominator is corrected from 25 to 100
with the two bounds computed, and the route is recorded — the measurement is
now a script over `2611.08516`'s released Corpus A rather than a wait for
somebody to collect telemetry.** The skill's own sentence should change from
"prescribed on a 25-run control" to "prescribed on a 100-run control whose
population is synthesized, bounding the organic rate at 3.0% pooled."

---

## The three ingestion lines: the blocker named on them has cleared, and the
## route changes

All three lines (`2609.18411`, `2606.02668`, `2610.22987`) ask for ingestion so
`skills/agent-approval-paths` can cite rows instead of paper titles, which is
why it ships `status: draft` with zero claim ids. Every previous run recorded
the blocker as the Modal workspace being switched off (board card
`6a5e4ad5`), which is also what keeps `arxiv:2609.08371` open at line 220.

**That blocker cleared on 2026-11-08 at 23:37Z.** The engineer's third comment
on card `6a5e4ad5` says "Compute is back … The Modal edge is routing again.
`tools/delivery_health.py` reads compute ok, the press printed 2026-W44, and
ingest and distill are inside their two day window. So the account state this
card was opened on has cleared." The card is still in This sprint and its
state was deliberately not changed, because the comment's open question —
whether a monthly spend cap is still set — is the owner's, not the engineer's.

What this means for these lines, checked rather than assumed:

- **This seat still cannot run the ingest.** `command -v modal` finds nothing,
  `import modal` raises `ModuleNotFoundError` in this sandbox although
  `requirements.txt:1` pins `modal>=1.5`, there is no `~/.modal.toml`, and
  there is no `DATABASE_URL`. Unchanged from 2026-11-02 (PR #742).
- **But it no longer needs a seat to run it.** `reading_queue.resolve()`
  (`pipeline/reading_queue.py:196-258`) inserts any queued id the corpus has
  never seen with a `rule:reading-queue` `deep_read` row, and `MAX_PER_RUN` is
  6 per distill run. With the crons routing again, the queue drains on its own
  — and `--order` puts these three at positions 1-3, ahead of `2609.08371`,
  because they are `blocked skills first`. So the next distill run should pick
  them up without anybody asking.
- **The explicit path also exists** if the cron order is wrong for the skill
  seat's timetable: `modal run pipeline/ingest.py --ids 2609.18411 2606.02668
  2610.22987` (`pipeline/ingest.py:611`).

**Disposition: all three lines stay open — the ask is corpus presence and these
are rows, not readings — with the blocker re-recorded as cleared and the route
changed from "waiting on card `6a5e4ad5`" to "the next distill run, or one
`--ids` command." This is the fourth distinct reason recorded against this
class of line and the first one that resolves.**

---

## What the skill agent should take from this

Ranked by evidence, not by date, per the relevance law.

1. **The approval-rendering mechanism is now a pattern, not a paper.** Three
   independent 2026 lines — VAC (`2609.18411`, browser DOM), Consent Integrity
   (`2606.02668`, shell, specified not implemented), ZTAC (`2610.14488`,
   files/programs/git/endpoints, implemented and measured) — reach the same
   construction: render the approval from the resolved object and re-verify at
   dispatch. ZTAC cites neither of the other two. Three independent sources is
   the charter's bar for a pattern, so `skills/agent-approval-paths` delta 1
   can stop being a single-paper delta.
2. **Approval laundering is named twice, independently, three weeks apart, and
   neither is in our corpus.** `2609.38983` (Yang Wang, Fudan, 30 Sep: a
   six-mode taxonomy of binding substitution — Scope, Argument, Temporal,
   Tool, Delegation, Semantic) and `2609.28586` (Zhang et al., CAS/UCAS, 23
   Sep: transitive effects beyond the approved invocation, formalized as
   closure-bound approval with an information limit). Both are the skill's
   subject exactly. Both queued this run.
3. **Pre-execution is the strongest-evidenced approval mechanism published**,
   with the only comparison table in this literature carrying confidence
   intervals (`2610.40753`, Table 3 + Appendix E: six existing systems, two
   benchmarks, 682 + 204 tasks). If one claim cluster is packaged from this
   note, it is this one.
4. **The containment and approval-path skills join at a direction, not a
   measurement**, and the joining measurement is nameable (Q3 above). A skill
   that says "the frontier is broken" would be overclaiming; one that says
   "two independent constructions report off-curve results, and here is the
   experiment that would settle it" is the honest version and the more useful
   one.

## Papers queued this run

`2610.14488` ZTAC · `2610.40753` Caper · `2610.39711` Sandman · `2609.22978`
DSec · `2611.08516` Aegis OS · `2609.38983` Approval Laundering (Fudan) ·
`2609.28586` Agent Approval Laundering (CAS) · `2604.13536` YoloFS ·
`2607.05743` Rashidi (balkanization survey, TOCTOU) · `2604.28138` Crab.

Not queued, read and set aside with the reason on the line: `2610.02456`
(SideKernel — single-evaluator practicum, no latency, microVM-only set; its
value is the Table I census of 20 sandboxes, not a finding) and `2609.40082`
(Tide — memory reclamation, no substrate comparison).
