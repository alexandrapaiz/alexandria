---
name: recursive-harness-self-improvement
description: Two measured findings about loops where an agent rewrites its own scaffold unattended, which a strong model does not give unprompted. Use when an unattended loop reports a win you have to judge or publish; when deciding what evidence would make a self-reported improvement believable; when attributing a failure to one function inside a very long execution log; or when choosing between a more expensive diagnostician model and more diagnostic passes over the same log.
version: 4
status: active
provenance:
  extracted: 2026-09-22
  revised: 2026-09-30
  validated: ""
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject, two rounds, 5 candidates for this skill (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 2 qualified, one of them the strongest bare failure in the library. rhsi-c1, rhsi-c2 and rhsi-c5 passed bare and their sections were cut."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 355 lines to under 120, nine sections to two. Cut on measurement: the freeze list, bounded edits, the three serial gates with rollback and the disjoint evolution set (rhsi-c1 and rhsi-c2, where the bare subject gave separated data pools with budgeted looks, a filesystem-enforced unwritable scorer, content-addressed lineage, auto-reject tripwires, the max-of-N upward bias and the retire-a-task-after-3-to-5-sightings rule); and the cost mechanisms (rhsi-c5, where it derived that a percentage compaction threshold is wrong, replaced it with absolute headroom against a projected worst case, and priced it against prompt-cache invalidation). Cut as under-evidenced rather than as non-differential: the Agora population section (claims 462, 465, 466), one 12-day run whose monoculture break is a single observed event with a human inside it. The challenger gate arrives here from evaluation-integrity, where the certification protocol was being carried twice."
    - "2026-09-30 (ADR-35, the paper wins): the protocol's third gate is optional and returned Inconclusive on both of its real-data audits; delta 1 says so."
  claims: [286, 288, 290, 593, 594, 597, 411, 412]
  papers:
    - "Scores Alone Do Not Prove Discovery: The Discovery Certification Protocol — arxiv.org/abs/2609.09219"
    - "Root-Cause Attribution Is a Search Problem — arxiv.org/abs/2609.13463"
    - "ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement — arxiv.org/abs/2609.14857"
---

# Recursive harness self-improvement

Two findings for the loop where the agent is the editor. Both are about evidence: what
would make its self-reported win believable, and how to find the thing that broke.

## Apply: the builder's checklist

1. **Before a self-reported gain is published, a matched challenger with the same
   starting knowledge and observations, but not the answer, has failed to reach the same
   result.** Statistics and a held-out set are not this gate (delta 1).
2. **Your challenger budget was derived from the bound you want to state**, not picked
   for convenience: a 5 percent upper bound at 1 percent error needs **90 episodes**
   (delta 1).
3. **The evidence bundle behind the verdict is frozen**, so a reader who does not trust
   your judge can replay the decision without a model (delta 1).
4. **Attribution over a long log gets more search turns before it gets a bigger judge**,
   with the turn count gated on log length rather than fixed (delta 2).

## Delta 1: the gate is a challenger, not a statistic

*Validation: no trial and no consumer report. Bare-arm screen rhsi-c4, 2026-09-30: **fail**. Asked what would make a 3-point self-reported gain believable, the bare subject gave paired designs, pre-registration, fixture hashing, cost normalisation, a stated mechanism and replication on a second eval, all of it good and none of it this. The absent idea is that someone else, equally equipped and not told the answer, should try and fail. Eval task rhsi-t10.*

The Discovery Certification Protocol audits a claimed outcome through three gates: a
significant improvement over baseline by a lower-confidence bound, **zero recoveries of
the same result by a matched challenger agent** within a finite-sample bound, and a
measured positive effect of truthful feedback against a calibrated neutral policy (claim
286). The middle gate is the one an ordinary review has no analogue for. A result a
fresh, equally equipped challenger reaches without your method is not evidence for your
method.

Take the gates in order and not as a set. The third is expensive, the protocol marks it
optional, and **on both of its own real-data audits it came back Inconclusive**:
truthful continuations reached the target in 9 of 30 and 16 of 30 paired trials against
0 of 30 for the neutral arms, and the intervals still straddled the required lower bound
of 0.30. The first two gates passed in the same audits. So budget for the feedback gate
to be inconclusive at 30 pairs rather than negative (ours, not the paper's).

1. Pre-register the analysis before the run. This is what the whole protocol rests on.
2. Gate 1: state the improvement over baseline as a lower-confidence bound.
3. Gate 2: run **matched challengers** given the starting information packet and the
   observed evidence, with the run history and any new measurements withheld. Derive the
   episode count from the bound you intend to report: **90 episodes for a 5 percent
   bound at 1 percent error**, and 96 were registered in the source work for a measured
   bound of 0.0468 (claim 288). Below that count, report the interval and never the zero.
4. Freeze the evidence bundle. The source protocol's decisions are reproducible by a
   **deterministic verifier with no model in it** (claim 290), which is what makes the
   verdict auditable by someone who does not trust your judge.
5. Gate 3 last, and only if you can afford it.

## Delta 2: attribution is a search, and search substitutes for judge scale

*Validation: no trial and no consumer report. Bare-arm screen rhsi-c3, 2026-09-30: partial. The bare subject said not to buy the expensive judge, which is the headline, and then offered oracle substitution over a replayed run at about six replays for forty candidates, which is a better method than this one where replay is faithful. What it did not have: the numbers, the fact that search turns buy what judge tier was supposed to buy, and the stop rule. Eval tasks rhsi-t3, rhsi-t4.*

Four turns of continual search over an execution log raised attribution F1 from **0.349
to 0.498** for one model and **0.478 to 0.620** for another, against **0.401 and 0.559**
for passively continuing to read (claim 593). And with continual search, **lower-tier
judges matched or surpassed higher-tier ones** (claim 594). The budget belongs in search
turns before it belongs in a better diagnostician.

There is a stop rule, and it is the part that gets skipped. On short trajectories the
extra turns did not help and sometimes hurt, because the first pass had already covered
the evidence and further turns pressured the judge into flipping correct labels (claim
597).

1. If the run replays faithfully, substitute a recorded-correct oracle for one candidate
   at a time and bisect. That is attribution by construction, and it beats reading.
2. Where replay is not faithful, search rather than read: give the judge multiple turns
   over the log, each conditioned on what the last one found.
3. **Gate the turn count on log length, not on a constant.** Four turns was the measured
   setting on logs with a median of hundreds of thousands of tokens. On a short
   trajectory, stop at one.
4. Spend on turns before tier. A lower-tier judge with search is the better buy.
5. Where you have K rollouts of the same task, pair a success against a failure and
   diagnose the contrast, which converts a task-level outcome into function-level
   evidence (claims 411, 412).

## Caveats

- The certification protocol is demonstrated on two audit cases. Its gates are a design
  to copy, not a validated pass rate, and Gate 2's floor is the 90 episodes above.
- Two senses of "recovery" appear in that protocol and support opposite conclusions.
  Gate 2 recovery is a challenger episode and vetoes a certificate. Gate 3 recovery is a
  paired feedback trial and measures only whether feedback helps. Our own claim graph
  deprecated a true claim by conflating them. Never write "recovered" unqualified.
- Attribution numbers come from LLM judges reading logs with a median of hundreds of
  thousands of tokens, and the stop rule was observed on two benchmarks. The
  diagnostician floor is the useful half: cheap model plus four search turns beats
  expensive model plus one pass.
- ModularRSI's transfer claim carries no numeric scores in the evidence alexandria
  holds, so treat "improves and transfers" as directional (claim 411).

## What this file no longer carries

Seven sections cut 2026-09-30: five because the bare subject gave them unprompted and in
better form, and two because one 12-day run with a human intervention inside it is not an
effect size. Receipts, with the bare answers and the section names, in
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md`.
