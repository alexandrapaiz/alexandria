# Self-improvement census, 2026-09-30: the 132 September papers we missed

Evidence file for `docs/research/briefs/2026-09-30.md` section 1. Produced by
eleven abstract queries against the live arXiv API (`export.arxiv.org/api/query`,
`abs:"<term>"`, sorted by submitted date, September 2026 only), deduplicated by
arXiv base id, then differenced against `papers` with

    select ... from ext where not exists (
      select 1 from papers p where p.id like 'arxiv:'||ext.aid||'%')

Terms: self-improving, self-improvement, self-evolving, recursive
self-improvement, self-refinement, self-play, self-taught, self-rewarding,
self-evolution, autonomous research agent, harness evolution.

206 distinct September 2026 papers matched. The corpus holds 74. The 132 below
are absent. `reachable` means at least one of the paper's arXiv categories is
one `sources.yaml` already pulls (cs.CL, cs.AI, cs.MA, cs.IR, cs.LG, cs.DC,
cs.CR), so the paper was inside our reach and was not taken: 93 of 132.
`UNREACHABLE` means no category we pull, a genuine reach gap: 39 of 132.

The count is a floor, not a ceiling. Each query capped at 120 most-recent
results before the September filter, and abstract-only matching misses papers
that describe a self-improvement loop without using any of the eleven terms.

Titles are reproduced as arXiv spells them, so three carry non-ASCII
characters in surnames (Poincare, Cesaro and Godel appear accented below).
That is ban-list entry 13's stated exception for a person's name as the
source spells it, not a defect for a later ASCII sweep to flag.

| reach | primary | arXiv id | categories | title |
| --- | --- | --- | --- | --- |
| UNREACHABLE | cs.CE | `2609.34424` | cs.CE | Construction-Reuse Trade-offs for Exact Certificates in Fixed-Rank Threshold Screening |
| UNREACHABLE | cs.CV | `2609.00814` | cs.CV | RingMoClaw: An Experience-Inspired Multi-Agent Framework for Self-Evolving Research in Remote Sensing |
| UNREACHABLE | cs.CV | `2609.02504` | cs.CV | SR-Edit: Region-Aware Image Editing via Self-Refinement |
| UNREACHABLE | cs.CV | `2609.03258` | cs.CV | An Ensemble-Based Self-Taught Learning Approach for Parking Space Classification Under Limited Data |
| UNREACHABLE | cs.CV | `2609.04203` | cs.CV | Temporal Self-Distillation: Learning Visual State Tracking in Videos Without Supervision |
| UNREACHABLE | cs.CV | `2609.08217` | cs.CV,cs.RO | Drive by Hindsight and Foresight: Tool-Grounded Synergistic Reasoning over Hierarchical Memory for Autonomous Driving |
| UNREACHABLE | cs.CV | `2609.08282` | cs.CV | Dreaming in Flow: Generative Grounding Feedback for Self-Evolving Unified Multimodal Models |
| UNREACHABLE | cs.CV | `2609.12181` | cond-mat.mtrl-sci,cs.CV | Physics as the label for measuring and correcting materials reasoning in multimodal models |
| UNREACHABLE | cs.CV | `2609.19664` | cs.CV | VideoResearcher: Self-Improving Tool Design for Long-Video Understanding |
| UNREACHABLE | cs.CV | `2609.30450` | cs.CV | LensDesigner: A Self-Improving Agent for Optical Lens Design |
| UNREACHABLE | cs.CV | `2609.32984` | cs.CV | ReVision3D: Attribution-Guided Recursive Self-Improvement for 3D Medical Perception |
| UNREACHABLE | cs.CV | `2609.34682` | cs.CV | V-Gym: Enhancing Agentic Visual Reasoning via Skill-Data Co-Evolution |
| UNREACHABLE | cs.CY | `2609.16784` | cs.CY | AI literacy over tool design: a mixed-methods study of scaffolded versus unrestricted generative AI in programming education |
| UNREACHABLE | cs.GT | `2609.19677` | cs.GT | A Logarithmic Regret Bound for Optimistic Hedge in General-Sum Games |
| UNREACHABLE | cs.HC | `2609.30588` | cs.HC | Orchestrating GenAI for Interdisciplinary Research |
| UNREACHABLE | cs.RO | `2609.11225` | cs.RO | Harness Robotic OS: A Unified Embodied-Agent Runtime for Closed-Loop Quadruped Inspection |
| UNREACHABLE | cs.RO | `2609.12216` | cs.RO | Guardrailed Meta-Agent Loops: Stress-Testing Policy Pinning, Budget Bounds, and Crash Recovery |
| UNREACHABLE | cs.RO | `2609.17372` | cs.RO | XPACE: Joint World and Action Modeling from Heterogeneous Experience |
| UNREACHABLE | cs.RO | `2609.21100` | cs.RO | Dynamics-Induced Commitment in Learning-Based Robotic Penalty Kicks |
| UNREACHABLE | cs.RO | `2609.21617` | cs.RO | CounterPlay: Counterfactual Post-Training for Self-Play Driving Policies |
| UNREACHABLE | cs.RO | `2609.24271` | cs.RO | ME-Brain-1.0: Memory, Cognition and Action for Evolving Embodied Intelligence |
| UNREACHABLE | cs.RO | `2609.26499` | cs.RO | Generalizing Manipulation Skills with a Local Coding Agent |
| UNREACHABLE | cs.RO | `2609.27612` | cs.RO | RegenHarness: A Robot Agent Harness with Evidence-Gated Recursive Self-Improvement |
| UNREACHABLE | cs.RO | `2609.29394` | cs.RO | RACaP: Agentic Reasoning, Acting, and Coding as Policies for Evolvable Robot Learning |
| UNREACHABLE | cs.RO | `2609.32698` | cs.RO | SEES: A Self-Evolving Embodied System via Failure-Guided VLA Policy Adaptation |
| UNREACHABLE | cs.RO | `2609.34823` | cs.RO | AGRO-SUVIDE: Agentic Robotics for Surgical Viscoelastic Debridement |
| UNREACHABLE | cs.RO | `2609.35318` | cs.RO | DexAgent: An Agentic Human2Sim2Robot Framework for Dexterous Manipulation with Self-Evolving Tool Library |
| UNREACHABLE | cs.RO | `2609.35432` | cs.RO | Self-Evolving Coding Agents: From Digital Programs to Physical-World Intelligence |
| UNREACHABLE | cs.SE | `2609.10590` | cs.SE | ReqEvolve: User-Oriented Software Self-Evolution through Automatic Requirement Interpretation |
| UNREACHABLE | cs.SE | `2609.14784` | cs.SE | Enhancing Automated Unit Test Generation for NLP Libraries Using Large Language Models |
| UNREACHABLE | econ.GN | `2609.15802` | econ.GN | The Economics of Recursive Self-Improvement |
| UNREACHABLE | eess.IV | `2609.31789` | cs.CV,eess.IV | MammoClaw: Towards Skill-Evolving Agent Harness for Breast Cancer Mammography Analysis |
| UNREACHABLE | eess.IV | `2609.36549` | eess.IV | MedForge-RSI: Medical Deepfake Detection via Recursive Self-Improvement |
| UNREACHABLE | eess.SY | `2609.14260` | eess.SY | Recursive Self-Improvement LLM Agents for Inverter Dynamic Model Identification |
| UNREACHABLE | math.AP | `2609.03830` | math.AP | Parabolic Poincaré inequalities and maximal function estimates for systems of partial differential equations |
| UNREACHABLE | math.FA | `2609.24601` | math.FA | On absolutely Cesàro bounded operators |
| UNREACHABLE | math.MG | `2609.24610` | math.CV,math.DG,math.MG | Quasihyperbolic domains are CAT(2) |
| UNREACHABLE | math.OA | `2609.22898` | math.FA,math.OA | Campanato spaces via quantum semigroups |
| UNREACHABLE | quant-ph | `2609.20823` | quant-ph | Environment Alignment and Redundant Record Formation in Imperfect-CNOT Quantum Darwinism |
| reachable | cond-mat.dis-nn | `2609.34292` | cond-mat.dis-nn,cond-mat.mtrl-sci,cond-mat.other,cs.LG | Pre-registered tests of solid-state-physics-inspired LLM compression: a cluster-level negative result at small-language-model scale |
| reachable | cs.AI | `2609.00768` | cs.AI | DiagEvo: Diagnosis-Guided Self-Evolution via Hierarchical Error Memory |
| reachable | cs.AI | `2609.01058` | cs.AI | ARISE-RL: Agentic Rubric-Grounded Iterative Self-Evolution with Reinforcement Learning |
| reachable | cs.AI | `2609.01345` | cs.AI,cs.CR,cs.LG | Cheap Verifiers, Large Blind Spots: Measuring the Reliability Cost of Cost-Saving Cascades |
| reachable | cs.AI | `2609.02074` | cs.AI | CHIME: Credit-Aware Hierarchical Memory Evolution for Long-Horizon Agentic Planning |
| reachable | cs.AI | `2609.02217` | cs.AI | SkillGLoW: Procedural-Family Skill Consolidation for Self-Improving Agents on Long-Horizon Task Streams |
| reachable | cs.AI | `2609.02246` | cs.AI,cs.LG | LLM-as-a-Judge Is Not an Oracle: Why Self-Improving Agents Need Deterministic Guardrails |
| reachable | cs.AI | `2609.02253` | cs.AI,cs.CL | APEx: Distillation of Agent Procedural Experience for Adaptive Deep Research Question Answering |
| reachable | cs.AI | `2609.02786` | cs.AI,cs.CR | SafeEvolve: Harness-Policy Co-Evolution from Agent Experience for Safety Alignment |
| reachable | cs.AI | `2609.03546` | cs.AI | Dalek: A Constructive Agent Machine |
| reachable | cs.AI | `2609.04665` | cs.AI | Harness-agnostic detection and immunization of reward hacking in self-evolving language models |
| reachable | cs.AI | `2609.04697` | cs.AI | SQL-Zero: Self-Evolving Text-to-SQL |
| reachable | cs.AI | `2609.08175` | cs.AI | A Theory of Reliable Self-Evolution for Agent Harnesses |
| reachable | cs.AI | `2609.12459` | cs.AI | EvoRS: On-Policy Self-Evolution of Reward Systems for Open-Ended Reinforcement Learning |
| reachable | cs.AI | `2609.13543` | cs.AI | Asclepius: An Adaptive Harness for Long-Horizon Clinical Agents |
| reachable | cs.AI | `2609.15396` | cs.AI | SkillLift: Learning Dense Rubrics from Sparse Oracles for Efficient Skill Evolution |
| reachable | cs.AI | `2609.19526` | cs.AI,cs.LG | Self Improvement via Fast Tree-search |
| reachable | cs.AI | `2609.25643` | cs.AI,cs.LG | Ladders of Thought: A Self-Evolving Curriculum of Progressively Simplified Reasoning Traces |
| reachable | cs.AI | `2609.26891` | cs.AI | Harness as a Language: A Minimalist Agent Framework With Maximal Expressivity |
| reachable | cs.AI | `2609.27051` | cs.AI,q-fin.PM,q-fin.ST | Propose, Don't Judge: An Anytime-Valid Referee for LLM Agents That Mine Investment Factors |
| reachable | cs.AI | `2609.29154` | cs.AI | A Wrong Turn Does Not Ruin the Journey: Deviation-Guided Skill Self-Evolution for LLM Agents |
| reachable | cs.AI | `2609.30936` | cs.AI | Self-Play Search Distillation for Large Language Model Reasoning |
| reachable | cs.AI | `2609.32093` | cs.AI | GameBoyWorlds: A Testbed for Self-Improvement in Embodied Video Games |
| reachable | cs.AI | `2609.32172` | cs.AI | Noisy Test-Time Reinforcement Learning for Code LLMs |
| reachable | cs.AI | `2609.32201` | cs.AI,cs.LG | Instruct, Not Answer: Using Instruction Privileges in On-Policy Context Distillation |
| reachable | cs.AI | `2609.32326` | cs.AI | RLHarness: Co-evolving Procedural Skills with Reinforcement Learning for Long-horizon Multimodal Reasoning |
| reachable | cs.AI | `2609.32423` | cs.AI | PluginRSI: Recursive Improvement of Agent Harnesses with Reusable Plugins |
| reachable | cs.AI | `2609.32870` | cs.AI,cs.LG | Counterfactual Self-Evolving Agents for Evidence-Grounded Reasoning |
| reachable | cs.AI | `2609.32990` | cs.AI | Certified Long-Horizon Code Agent Evolution via Validation-Gated Skill Optimization |
| reachable | cs.AI | `2609.33123` | cs.AI,cs.SE | Compositional Safety Failures in Harness Evolution: Identification and Runtime Monitoring |
| reachable | cs.AI | `2609.33146` | cs.AI | LiteEvo: Automated, Cost-Efficient Harness Evolution for Generalization to Unseen Tasks |
| reachable | cs.AI | `2609.33181` | cs.AI,cs.CL | SeOPD: Self-Evolving LLMs via Online Policy Distillation from Self-Generated Chain-of-Thought |
| reachable | cs.AI | `2609.33295` | cs.AI,cs.CL | TraceDance: An Automated System for Building Agent Behavior Benchmarks from Real-World Agent Deployment Traces |
| reachable | cs.AI | `2609.33398` | cs.AI | COEVO: Co-Evolving Context and Parameters for Recursive Self-Improvement |
| reachable | cs.AI | `2609.33524` | cs.AI,q-fin.ST | EverMine: Dissecting the Self-Evolution of Research Capabilities in Long-Horizon Alpha Research |
| reachable | cs.AI | `2609.33565` | cs.AI | Dr. Free: You Don't Need Difficulty Rewards for Self-Evolving Search Agents |
| reachable | cs.AI | `2609.33713` | cs.AI | BIRD: Distilling Decision Boundaries into Rationales for MLLM Adaptation |
| reachable | cs.AI | `2609.33867` | cs.AI | R$^2$ Flow: Recursive Self-Improvement via Recursive Skill Evolution |
| reachable | cs.AI | `2609.34082` | cs.AI,cs.CV | K-OPSD: Verifiable On-Policy Self-Distillation for Post-Training Vision-Language Models on AEC Drawings |
| reachable | cs.AI | `2609.34151` | cs.AI | Self-Evolving Agents via Likelihood-Guided Tool-Space Optimization |
| reachable | cs.AI | `2609.34649` | cs.AI | Beyond Skill Evolution: Self-Evolving Context Management Policies for Long-Horizon Agent Harnesses |
| reachable | cs.AI | `2609.34712` | cs.AI | RSI-Router: Evolving Subtask-Level LLM Routing and Skills for Cost-Efficient Agents |
| reachable | cs.AI | `2609.34785` | cs.AI,cs.AR,cs.LG | BEHAVE: Functional Behavior Modeling Enables Self-Improving Agents for Hardware Design and Verification |
| reachable | cs.AI | `2609.35025` | cs.AI | AutoDataBench: Can Agents Write the Data That Feeds the Self-Improvement Loop? |
| reachable | cs.AI | `2609.35107` | cs.AI,q-bio.QM | DoAtlas-2: A Foundation for Self-Evolving Causal Biomedical Discovery |
| reachable | cs.AI | `2609.35110` | cs.AI,cs.CV,cs.LG | Sol-H3: Recursive Self-Improvement for MiniMax-H3 Inference Acceleration on Sol-Engine across Cloud and Edge |
| reachable | cs.AI | `2609.35897` | cs.AI,cs.LG | Self-discovering RL in the Era of Experience: Is Learning History an Asset or a Burden? |
| reachable | cs.AI | `2609.36043` | cs.AI | SAGE: A Statistical Acceptance Gate for Self-Evolving Agents |
| reachable | cs.AI | `2609.36235` | cs.AI,cs.LG,cs.MA | MERID: Multimodal Exploration via Recursive Self-Improvement Agents for Major Depression Analysis |
| reachable | cs.AI | `2609.36323` | cs.AI,cs.DB,cs.SE | Towards an AI Software Factory for Data Systems |
| reachable | cs.AI | `2609.36580` | cs.AI | SafeCoEvo: Co-Evolving Safety Harnesses and Guards for LLM Agents at Test-Time |
| reachable | cs.AI | `2609.36626` | cs.AI | Semantic Projection for Continual Self-Evolution of Language Agents |
| reachable | cs.AI | `2609.36746` | cs.AI | EASE: Behavior-Adaptive Skill Curation for Self-Evolving Agents |
| reachable | cs.AI | `2609.36887` | cs.AI | WEFT: Scaling Tool-Use Post-Training for General-Purpose Agents |
| reachable | cs.AI | `2609.36892` | cs.AI,cs.CL | Harness Evolution as Learning: Approximation, Generalization, and Optimization Limits of Self-Improving Personal Agents |
| reachable | cs.CL | `2609.00759` | cs.CL | Compile, Don't Memorize: A Context Compilation Architecture (CCA) for In-Context Learning |
| reachable | cs.CL | `2609.05677` | cs.AI,cs.CL,cs.HC,cs.SE | Who Maintains Agent Skills? A Longitudinal Study of Human-Governed, AI-Assisted Skill Maintenance |
| reachable | cs.CL | `2609.15161` | cs.AI,cs.CL | EMR: Self-Evolving Medical Multi-Agent System via Experience Mining and Reuse |
| reachable | cs.CL | `2609.22235` | cs.CL,cs.MA | BizSage: A Self-Evolving Multi-Agent Framework for Business Research with Efficient Knowledge Retrieval |
| reachable | cs.CL | `2609.30297` | cs.AI,cs.CL,cs.IR | Bootstrapping Conversational Recommendation Agents At Spotify: Synthetic Data Generation and Self-Improvement Loops |
| reachable | cs.CL | `2609.32458` | cs.CL | Streamlined Reflective Evolution for Task-Adaptive Self-Refinement Pipelines |
| reachable | cs.CL | `2609.32630` | cs.CL | ExpVoyager: Direct Experience Navigation for Dynamic Agent Skill Synthesis |
| reachable | cs.CL | `2609.36535` | cs.CL | When Updating Stops Being Learning: Rethinking LLM Self-Evolution via learnable information gain |
| reachable | cs.CL | `2609.36675` | cs.CL | Gödel Forest: Balancing Search Depth and Breadth for Data-Centric Recursive Self-Improvement |
| reachable | cs.CR | `2609.17817` | cs.AI,cs.CR | Reflections on Trusting Trust, Revisited: Contaminating Self-Modifying AI Coding Agents with Poisoned Benchmarks |
| reachable | cs.CR | `2609.22792` | cs.AI,cs.CR | SelfOp: An Optimization Algorithm for Self-Improving Security Agents |
| reachable | cs.CR | `2609.32516` | cs.AI,cs.CR,cs.LG | REFINE: A Resilient Evolution Framework for Intelligent Enterprise Alert Triage in Security Operations Centers |
| reachable | cs.CR | `2609.36603` | cs.CR | Self-Evolving Defense: Continual Security Policy Learning for LLM Agents |
| reachable | cs.CV | `2609.33855` | cs.AI,cs.CL,cs.CV,cs.LG,cs.NE | Program-Verified Self-Evolution for Vision-Language Models |
| reachable | cs.CV | `2609.36224` | cs.AI,cs.CV | Mutually Adversarial Self-Training with Evolving Data for Unified Multimodal Models |
| reachable | cs.DB | `2609.34764` | cs.AI,cs.DB | WeaveData: A Multimodal Data Analysis System with Self-Critiquing and Self-Evolving LLM Plans |
| reachable | cs.GT | `2609.22839` | cs.GT,cs.LG | A Horizon-Independent Regret Bound for Optimistic Hedge in General-Sum Games |
| reachable | cs.LG | `2609.00829` | cs.AI,cs.LG | HarnessEvolve: Learning from Reference Trajectories for Reliable Agent Self-Evolution |
| reachable | cs.LG | `2609.01679` | cs.LG | A Survey on Self-Improving Test-Time Intelligence: Feedback-Driven Adapting, Learning, and Scaling at Inference |
| reachable | cs.LG | `2609.02170` | cs.LG | DMRL: Document-Mediated Reinforcement Learning for Skill Optimization in Advertising Recommendation |
| reachable | cs.LG | `2609.03660` | cs.AI,cs.LG | Local Updates, Global Learning (LUGL): Playing Games with non-incremental Learners |
| reachable | cs.LG | `2609.06396` | cs.LG | MetaRSI / RSI2: A Meta-Recursive Self-Improving System for Recursive Self-Improving Systems Themselves |
| reachable | cs.LG | `2609.32228` | cs.LG | CompassPlay: Rewarding the Proposer for Where It Moves the Solver |
| reachable | cs.LG | `2609.32689` | cs.LG | Self-Evolving Time-Series Forecasting Agents with Episodic Memory and Online Policy Learning |
| reachable | cs.LG | `2609.34205` | cs.LG | Learning to Optimize through Solver-Grounded Self-Play |
| reachable | cs.LG | `2609.34279` | cs.AI,cs.LG | Direct Self-Evolving Optimization: Evolving LLMs without Challenger Training |
| reachable | cs.LG | `2609.34633` | cs.LG | GenMem: Generative Symbolic Memory for Self-Evolving Harness |
| reachable | cs.LG | `2609.34975` | cs.LG | Teach to Learn: Hint Annealing for Self-improving LLM Reasoning |
| reachable | cs.LG | `2609.36393` | cs.AI,cs.LG | Reward-rate Policy Gradient for Efficient Machine Learning Engineering Agents |
| reachable | cs.LG | `2609.36695` | cs.LG | Know Thyself, Teach Thyself: Internal Information Flow for Selective Self-Distillation |
| reachable | cs.LG | `2609.36750` | cs.AI,cs.CL,cs.LG | Group-Marginalized Self-Rewarding RL Drives Zero-Label Self-Evolving |
| reachable | cs.MA | `2609.36787` | cs.GT,cs.MA | Regularized policy gradient with learned mixtures of Gaussians for games with continuous actions |
| reachable | cs.RO | `2609.13236` | cs.DC,cs.RO | Self-Evolving AI for Humanoids: Mechanisms, Safety, and Evaluation of Post-Deployment Self-Improvement |
| reachable | cs.RO | `2609.32862` | cs.AI,cs.RO | RoboFoundry: System-as-Policy Evolution for Self-Learning Embodied Agents |
| reachable | cs.RO | `2609.36012` | cs.LG,cs.RO | In-Context Learning for Robots: Methods and Applications |
| reachable | cs.SE | `2609.28908` | cs.LG,cs.SE | Automatic Harness Evolution for Hardware Design Verification: Can LLMs Consolidate Gains Across Discovered Harnesses? |
| reachable | math.OC | `2609.09957` | cs.AI,math.OC | Beyond Verified Answers: Solver-Informed Self-Distillation for Bootstrapping Operations Research Language Models |
| reachable | stat.ML | `2609.33180` | cs.AI,cs.LG,stat.ME,stat.ML | Which Self-Improvements Should We Trust? Reliable Self-Improvement When Agents Reuse Their Benchmarks |
