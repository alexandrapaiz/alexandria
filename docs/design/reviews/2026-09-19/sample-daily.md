<!-- SAMPLE. Layout fixture for the 2026-09-19 email template review, written by
     the frontend seat to exercise the daily's slots at realistic length. Every
     paper, number and claim in it is lifted from the real 2026-W37 digest; the
     arrangement into a daily is the fixture. It is not an issue and was never
     sent. -->

# A dense verification reward took a terminal agent from 49.4% to 64.0%

*The latest in AI research, read in full: what changed in the last 24 hours.*

Two of today's findings point the same way. Counting how many assertions an answer satisfies, instead of scoring it right or wrong, is what moved a 122B agent past the 60% barrier on long-horizon tasks. The binary version of the same reward never beat its baseline.

## Compounding

- **Dense verification rewards beat binary ones by 28% relative on long-horizon tasks.**
  The reward counts passed assertions from a held-out verifier, scales them on one global scale shared across tasks, and hands the result to the critic at the final response token. Three PPO epochs later the agent resolves 64.0% of benchmark tasks, against 49.4% for the supervised checkpoint it started from.
  Evidence: authors' own experiments on one benchmark, not yet replicated.
  *T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks* — [https://arxiv.org/abs/2609.11042](https://arxiv.org/abs/2609.11042)

- **Inference-time context management still outperforms most system changes.**
  Limiting the tool set and fixing the judge moves results more than the architectural changes teams usually reach for first. Three independent papers now support it, which makes it the cheapest thing on this list to try today.
  Evidence: three independent supporting papers in the claim graph.
  *Inference-time context management* — [https://arxiv.org/abs/2609.04304](https://arxiv.org/abs/2609.04304)

- **One-shot on-policy distillation keeps improving for hundreds of steps.**
  A single distillation pass recovers most of the gain of full-data training and keeps paying out well past the point teams normally stop measuring. Diverse queries reach 98.9% state coverage and match full-data validation accuracy.
  Evidence: two supporting papers, consistent direction, different benchmarks.
  *One-shot on-policy distillation* — [https://arxiv.org/abs/2609.08368](https://arxiv.org/abs/2609.08368)

## New and unproven

- **Agents that train with extra feedback keep the benefit after the feedback is removed.**
  Feedback-enriched environments add observation signals during training only. Agents trained in them hold their performance when the signals are gone at test time, and they explore a wider part of the state space on sparse-reward tasks.
  1. Extra observation signals are added to the environment during training.
  2. The signals are removed at evaluation time.
  3. Performance holds, which is the evidence that the guidance is in the weights.
  Evidence: authors' own experiments, single environment family, no independent replication.
  *Environments as Scaffold: Enriching Feedback to Bootstrap Self-Evolving Agents in Long-Horizon Tasks* — [https://arxiv.org/abs/2609.08404](https://arxiv.org/abs/2609.08404)

- **Aligning the training and inference token streams removes drift entirely.**
  Preserving token prefixes across turn boundaries and replaying recorded expert routing during updates shrinks the training-inference log-probability gap from 0.021 to 0.013, with zero token drift in the loss region.
  Evidence: one paper, one model family, reported by the authors.
  *T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks* — [https://arxiv.org/abs/2609.11042](https://arxiv.org/abs/2609.11042)

## Left behind

**Contradicted**

- **The 23.9% simulation ceiling is gone.**
  An expert-authored reference implementation reaches 82.2% success on the same simulations, so the lower figure should no longer be quoted as a limit.
  Evidence: one reference implementation, same benchmark, higher score.

- **That 82.2% does not hold on memory-dependent tasks.**
  The same approach averages 12.5% success across four memory-heavy tasks. If your workload depends on recall across a long session, plan against the lower number.
  Evidence: four tasks, same authors, reported alongside the headline result.

---
412 papers ingested / 19 claims distilled / 7 edges drawn in the last 24 hours
