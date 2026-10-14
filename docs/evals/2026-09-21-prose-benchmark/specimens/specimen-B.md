This week the most active ideas revolve around two themes. First, feedback-enriched environments are shown to let agents absorb guidance during training and to explore harder state spaces without extra test-time tricks. Second, a set of training tricks - dense verification rewards, token-stream alignment, and a focused reinforcement-learning loop - lift a 122 B Mixture-of-Experts terminal agent to 64% resolved on Terminal-Bench 2.1, the strongest result in its size band. Both currents promise more reliable, self-sufficient agents that need less hand-crafted inference scaffolding.

## Trailblazing

Feedback-Enriched Environments let agents learn guidance and explore without test-time cues.
The paper introduces environments that add extra observation signals while training. Agents trained this way keep their performance even when those signals are removed at test time, showing that the guidance has been baked into the policy. They also visit broader parts of the state space and succeed more often on sparse-reward tasks.
  - Agents internalize environmental guidance into policy weights rather than relying on inference-time priors.
  - Exploration covers larger state regions, raising success rates on difficult tasks.
  - Training becomes more stable because intra-group feedback consistency reduces entropy volatility.
Environments as Scaffold: Enriching Feedback to Bootstrap Self-Evolving Agents in Long-Horizon Tasks - [link]
