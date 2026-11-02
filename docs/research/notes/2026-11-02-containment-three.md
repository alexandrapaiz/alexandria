# The three oldest queue lines, read on 2026-11-02

Working note behind the drain of `docs/research/reading-queue.md:196`, `:209`
and `:217`, all dated 2026-09-30 and so 33 days open at the start of this run.
Every number below was produced this run by the command printed beside it, not
recalled.

## Why these three, and what the lane held

`python3 tools/board.py show --seat research` printed zero items in Backlog,
zero in This sprint and zero in In progress, with all five research cards in
Review. Each of the five carries a comment saying its work shipped. The two
superseding chains behind them both reached main — 679 to 685 to 691 to 699
to 702, and 711 to 720 to 726 to 730 — and the check I ran was
`git cat-file -e origin/main:<path>` for every note those cards name, which
passed for all five. So the lane was claiming five live items while holding
none, and the five are moved to Done in this run.

That leaves the charter's standing first duty. `grep -n '^- \[ \]'` over the
queue returns 131 matches, one of which (line 43) is a formatting example
inside the file's own prose rather than a line. The three oldest real ones are
196, 209 and 217.

## The discovery channel that was down last run is up

The 2026-11-02 run behind PR #711 recorded that `export.arxiv.org/api`
answered `search_query` with 429, 503 and two read timeouts over five attempts
on two HTTP clients, and concluded that both measurement lines needed a paper
discovered rather than fetched, which it could not do. That condition did not
hold this run. Six `search_query` calls spaced four seconds apart all returned
200 in about a second each, and the first one returned three papers directly on
the subject of line 209. The rate limit is therefore episodic rather than a
standing property of this egress address, and the correct response to it is a
retry on a later run rather than a finding about arXiv.

Six queries were run. Those that returned anything load-bearing:

```
all:"microVM" AND all:agent
abs:sandbox AND abs:overhead AND abs:"coding agent"
abs:"human approval" AND abs:agent AND abs:overhead
abs:"human-in-the-loop" AND abs:agent AND abs:"approval"
abs:"approval" AND abs:"guardrail" AND abs:"LLM agent"
```

Six papers were then read in full with `python3 tools/read_paper.py <id> --bare`,
all six exiting 0, which is this repository's own test for full text rather
than abstract: `2610.02456` (72,256 chars), `2609.40082` (34,605),
`2607.01415` (34,611), `2609.18411` (82,964), `2606.02668` (45,689),
`2610.22987` (67,001).

## Line 217 — the cost of a containment control with an approval path

This line is answered, and the first thing to say is that it asked for the
wrong unit. It wanted a wall-clock number: one paper's 145-to-316-second mean is the
only end-to-end figure either cluster holds, and that figure is dominated by an
autonomous loop retrying refused actions with no human in it. The literature's
answer is not a second. Three papers measure the approval path end to end and
all three report it in confirmations and prompt rates, because the machine side
of the mechanism is too cheap to matter.

**The Verifiable Action Card** (`arxiv:2609.18411`, read in full) is the clean
one: four arms differing only in the confirmation step, run across five
open-weight models plus a separate GPT-4.1 run, 293 clean trials in the sweep
plus 40 in that run. With no gate, attack success is 68% to 100% by model,
aggregate 78%. With the gate, attack success is 0% on all five models, task
completion is 78%, the false-block rate is 0%, and the confirmation burden is
**0.94 confirmations per legitimate task**. The paper reports the mechanism's
own overhead as negligible and says why in structural terms rather than in
milliseconds: one DOM evaluation per commit, and the other checks are local
string operations.

**Consent Integrity** (`arxiv:2606.02668`, read in full) supplies the
millisecond figure and then argues it is not the cost: mean analyzer overhead
0.056 ms, median 0.050, p99 0.122, n=4000, which it calls negligible against
inference latency, and it says plainly that this excludes the total mediation
and trusted-path rendering the prototype does not implement and which "would
dominate any end-to-end figure." Its real contribution to this line is the
fatigue axis, measured on two independent third-party corpora it did not
author. On 1,330 abuse commands expanded from GTFOBins across 478 binaries it
flags 90.0% and silently passes 10.0%, every silent pass through a binary its
own trust list allows. On 28,798 idiomatic commands from tldr-pages across
6,503 tools it prompts on 95.9% and marks 87.0% uninspectable, 83.4% of that
purely because the tool is absent from the trust list, leaving 4.1% that pass
with no prompt. The paper names the trade-off as its central empirical finding:
the same trust list that holds silent passes to 10% on abuse forces an 87%
uninspectable rate on normal use, and a boundary-only static mediator can
choose where on that curve to sit but cannot occupy both ends.

**From Approval to Abuse** (`arxiv:2610.22987`, read in full) prices the
standard remedy for that fatigue, which is the reusable allow-rule that Codex
CLI and Claude Code both support. Eliciting such a rule during an ordinary
benign task raises Permission Capability Coverage to 0.48–0.61 across four
agent configurations against 0.25–0.55 for a direct request, and makes 9 to 18
of 25 adversarial goals reachable. From those checkpoints, downstream goal
completion reaches 17/17 on one Codex configuration and 13/14 on
claude-haiku-4.5, with 13 and 9 of those respectively attributed to the
acquired prefix itself. The control number is the one that matters for anyone
reading this as advice: **Benign Control yielded 0/25 on every model**, so a
persisted rule is never proposed organically and its appearance is itself the
signal.

Read together, the answer to the line is: the approval path costs about one
confirmation per legitimate task for zero false blocks and a 78-point drop in
attack success; its machine overhead is tens of microseconds; its real cost is
the uninspectable rate on normal usage, which runs to 87% under default-deny;
and the mechanism that buys that rate down is itself the attack surface, with a
measured escalation path and a clean 0/25 control.

## Line 209 — what the microVM boundary buys an agent workload

This line is answered in part, and what is left of it is narrower than the
line. Its premise was that the library's only isolation advice rests on no
number, and that Firecracker's 125 ms boot and 5 MB per microVM are serverless
figures measured on functions. Both halves of that premise now move.

The Rollout Infrastructure Tax in Coding-Agent Reinforcement Learning
(`arxiv:2607.01415`, read in full) is the measurement, and it is a controlled
one: the coding-agent workload is held fixed while the execution substrate
varies across single containers, a commercial hosted sandbox,
Kubernetes-orchestrated containers, and strongly isolated cloud VMs, over three
workload tiers, 100 trials per substrate and configuration, p50 and p95, with
provider-specific prefetching and cache tuning deliberately avoided. What it
finds is that the isolation penalty is a cold-start and readiness penalty that
trajectory length amortizes. On the minimal tier the gap between the hosted
sandbox and the cloud VM exceeds two orders of magnitude; by the realistic
repository tier it is about 1.9x. At 150 actions the end-to-end gap between the
slowest and fastest substrate is 42.5 s against 23.4 s, which is 19.1 s per
trajectory, and the paper projects that to 11,811 against 6,495 rollout
worker-hours over a million trajectories.

That is the shape of the answer the line wanted. For the agent the line
describes, one that runs a repository for twenty minutes, a 19-second substrate
gap is under two percent of the run, so the isolation upgrade is close to free
at that horizon and is ruinous at the short-trajectory horizon where the
library's advice does not apply.

**Tide** (`arxiv:2609.40082`, read in full) replaces the serverless memory
figure with an agent-workload one. It measures backing memory and harness time
on six Terminal-Bench tasks, one trajectory each on three harnesses (OpenCode,
OpenClaude, Codex), with the baseline and Tide in Firecracker and the
comparison mechanism HyperAlloc in QEMU. Against the same-harness baseline it
reduces total backing memory by 45.3%, 41.0% and 34.2%, duration-weighted
47.9%, 41.7% and 35.4%, for harness-time increases of 5.1%, 1.1% and 1.9%; on
the SkillsBench ground-truth tasks whose baseline median exceeds a second it
stays within 1.7%. The number that bears on this line is not Tide's win but its
premise, which it argues from the measurements: on an agent microVM the
dominant memory cost is not the per-VM floor that the 5 MB figure names but the
phase-structured backing the harness holds across a long run, a third to a half
of which is reclaimable for a few percent of time. A figure measured on
functions misses this because a function has no model wait and no tool
lifetime.

**SideKernel** (`arxiv:2610.02456`, read in full) is the one paper that puts a
microVM agent sandbox and a container agent sandbox on the same task set, and
the result is worth recording precisely because it is not a performance result.
Across 23 capability tests derived from a 68-respondent user survey, SideKernel
(Apple Virtualization framework, Kata's stripped kernel) and Docker Sandboxes
(containers) both pass 19, with the three other microVM entrants at 12. The
author declines the security comparison in as many words: container isolation
is weaker than microVM isolation, but establishing that against policy-based
shared-kernel primitives "is a research question that deserves a study of its
own, and is out of scope for this paper." The survey number is the other
finding: of 68 AI coding agent users, 38.2% currently sandbox, 10.3% formerly
did, 51.5% never have, and among the non-sandboxers 60% have never considered
it and 25.7% judged the security benefit not worth the effort.

So the residual, and the line is rewritten to it: **no one has measured the
microVM point on the Rollout-Tax curve.** That paper measured containers and
full cloud VMs and explicitly lists microVMs, snapshots and preallocated
workers as the unmeasured intermediate designs; Tide measures inside
Firecracker with no container arm; SideKernel compares the two but on usability
alone. The comparison is still new work rather than a literature find, which is
what PR #711 concluded from `2607.05743`'s Gap 1, and that conclusion survives
this run with its scope cut from the whole question to one point on a curve
that now exists.

## Line 196 — the harness paper absent from the corpus

This line stays open for the fourth run running, and the reason recorded last
run is still the reason. Checked live rather than carried over:

- `python3 pipeline/reading_queue.py --order` prints `arxiv:2609.08371` first
  and marks it `NEXT`, of 84 pending lines at 6 per distill run.
- `command -v modal` finds nothing and `import modal` raises
  `ModuleNotFoundError`, though `requirements.txt:1` pins `modal>=1.5`. There
  is no `~/.modal.toml`. So this sandbox cannot reach the workspace even if the
  workspace were on.
- The engineer's board card for the switched-off workspace is still in This
  sprint.

Nothing in this run changes what that line needs, which is one distill run.

## What this run could not do

No corpus. `sql_query`, `semantic_search` and `get_digest` are served by the
Modal MCP server and were not available this run, which is the tenth
consecutive run of this seat without them. So there is no digest review, no
synthesis against claim ids, no skill proposal and no graph audit this run; the
six papers above are read and recorded here and queued for ingestion, and not
one of them can be checked against `papers` for duplication until the workspace
returns.

## The L-R1 ecosystem check, and what it says about line 209

L-R1 in `docs/standards/lessons.md` requires a live-web check on this seat's
declared coverage every run, not only a corpus query. Two searches this run,
both inside the containment territory the two drained lines belong to.

The approval-path search returned the corpus-side papers above and corroborated
them from outside: the aggregate figure for `arxiv:2610.22987`, which I read
per-configuration, is 47 of 58 eligible instances completing silently, 81.0%,
with allow-rule elicitation succeeding on 58% of instances across Claude Code
and Codex CLI and an acquired rule covering 56.9% of capability tests. Those
aggregates agree with the per-model table I read, so the reading is checked
twice. The search also named a paper the three above do not cover, queued this
run: `arxiv:2607.13718`, on the permission ask from interface to enforcement.

The isolation search is the more useful result, because it says where line
209's measurement actually lives. The microVM-versus-container comparison for
agent workloads exists in quantity, and all of it is vendor and blog material:
a microVM-versus-Docker speed comparison from a sandbox vendor, a 2026 state-of
-microVM-isolation blog post, an agent-runtime comparison from another
platform, and a figure of 50.5 MB resident for a 128 MB guest with no method
beside it. None of that clears this program's evidence bar, where a framework's
or a vendor's own marketing is not a finding, and that is the whole reason the
residual line stays open rather than being answered off the web.

One industry item is a steering signal rather than evidence, and it is worth
recording in those terms: Vercel offered up to a million dollars between
2026-08-18 and 2026-09-01 for an escape of Vercel Sandbox, on the stated
principle that the microVM and not the container is the security boundary. The
announcement is not evidence about how to build agents. The outcome would be:
a published escape, or a published null result over a bounty window of that
size, is an artifact with method and admissible on the same terms as a paper.
Nothing in the search said which happened, and finding out is the next
ecosystem check rather than this one.
