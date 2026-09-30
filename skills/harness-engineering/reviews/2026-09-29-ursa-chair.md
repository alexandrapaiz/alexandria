---
skill: harness-engineering
skill_version: 1
consumer: Ursa chair session (Claude Fable 5, Claude Code, the owner's machine)
date: 2026-09-29
task: three-stage build plan for Ursa's first deployed surfaces (GitHub Action resolving outcome records on merged PRs; local dashboard; overlay above Claude Code)
loaded: at the owner's request, after the plan was drafted, before code
baseline_caveat: the reviewer had read this SKILL.md four days earlier during a claims pull, so the bare baseline was not clean
sections_exercised: [3, 4]
sections_confirmatory: [1, 2]
decisions_changed: 1
procedures_adopted: 1
verdict: keep active; improvements are about measurement, not content
---

# Skill usage review: harness-engineering v1

**Bottom line.** It helped. Of the four substantive sections, one changed a
design decision, one changed a stated procedure the consumer will follow when
something breaks, and two confirmed decisions already made. For a five-minute
load, one real design change is a good return.

## Section by section

1. **Order of operations, harness before weights.** Not exercised; no
   fine-tuning was on the table. The sub-point on action interfaces (fewer,
   more semantic actions) confirmed an existing choice: the PR surface's whole
   user vocabulary is a thumbs-up and an ordinary review comment. Verdict:
   confirmatory.
2. **Never break model-harness fit.** The on-policy single-turn correction
   result (imitation trajectories regress 4 to 30 points, minimal correction
   recovers) is the most commercially important claim in the file for Ursa,
   whose product produces exactly that data shape, but that value was banked
   in the earlier claims pull. For the build task the section contributed a
   working principle (smallest local change over wholesale replacement).
   Verdict: strategically the strongest content, tactically confirmatory.
3. **Debugging a multi-agent harness (AgentGrad).** Changed the stated
   procedure. Two parts were non-obvious: the strict one-agent-at-a-time
   intervention with pinned inputs as a hard rule, and the correction-
   clustering procedure (embed accumulated fixes, group by similarity,
   abstract each cluster, apply the generalization, never the raw pile). The
   failure mode it prevents, one bloated prompt accreting unrelated fixes, is
   one the consumer has watched Ursa's own seat charters flirt with. Verdict:
   useful, adopted, untested in action.
4. **Test-time compute, sample-and-select over reflection.** The one concrete
   design change. The distiller's CI mode now specifies best-of-three parallel
   samples with medoid selection for the why-interpretation step, instead of
   single-sample-plus-self-revision. The decision was cheap because the skill
   supplied direction (parallel beats reflection), magnitude (2.2 to 9.7
   points for less compute), and the implementation caveat (medoid needs at
   least 3 samples and an embedding model). Verdict: direct design change.

## What the artifact does well, as a form

- The deltas framing ("this adds to standard practice, the findings below are
  the deltas") told the consumer exactly where to override defaults. Keep it
  in every skill.
- Scoped caveats enable honest transfer: naming the models and the task count
  let the consumer judge what transfers and what should not be quoted as
  universal.
- Provenance earns trust: claim ids, paper links, and the recorded A/B made
  the consumer willing to change a design on the skill's word.
- The trigger description matched the decision the consumer was in.

## What alexandria should improve

1. **Per-section validation status.** The `validated` field records one A/B
   trial that tests only the fine-tuning refusal; sections 3 and 4 carry the
   same implicit authority with no validation behind them. Mark each section
   validated or unvalidated.
2. **A builder's checklist.** The skill is written for advice-giving; a
   builder wants the same content as five checkable lines at the end
   (interface: few semantic actions? feedback: rich, stable shape? compute:
   parallel sample-and-select? fixes: smallest local change? debugging: one
   intervention, pinned inputs?).
3. **Name defaults in caveats.** "Needs an embedding model" is stronger as
   "needs an embedding model (MiniLM class is sufficient)".
4. **Record consumer reports.** A `reviews/` lane per skill, or a table of
   (consumer, task, sections exercised, decisions changed). Skills whose
   reviews show zero decision changes across several consumers are
   deprecation candidates. This file seeds the lane.

**Net:** 1 design change + 1 adopted procedure + 2 confirmations, from 135
lines.
