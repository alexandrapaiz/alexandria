# Agent skill systems are splitting between retrieval and self-evolution

*What's new in AI research and what's gaining acceptance.*

If you run agents that fetch skills from a library, you are choosing between two architectures that used to look like one. This week the field drew a hard line: one camp treats skills as retrieved documents, the other as living code that evolves with the task. Both posted real numbers, and both have a catch a builder needs to know.

Two results stand out. A team from Evolvent AI and NUS showed that recursive self-improvement under a tight budget is now a measured practice, not a demo. Two separate groups found that the way you expose retrieved skills to an agent matters more than which retriever you use.

## Budget-constrained agents can now improve their own harnesses

The most concrete result this week comes from RSIGym, a platform for running recursive self-improvement experiments with real dollar caps. A team at Evolvent AI and the National University of Singapore gave six frontier research models a $500 service budget per run and asked them to improve their own tooling. Opus 5 won cleanly, lifting its own harness performance from a combined score of 0.2079 to 0.4809 on the RSI-Index, with gains on all five benchmarks: SWE-bench Verified rose from 17.7% to 50.3%, AIME from 31.7% to 97.8%, and GPQA Diamond from 51.3% to 83.3%.

The platform matters as much as the result. RSIGym exposes five reusable services, training through sandboxed fine-tuning, model serving, rollout generation, benchmark evaluation, and cloud execution, with shared budget and permission controls. The procedure is extractable: agents submit training configs, query checkpoints through an OpenAI-compatible gateway, generate data via LiteLLM, and evaluate through Harbor, all under a single authorization service that checks every call against remaining budget. This is the first time a recursive improvement loop has been run with public cost accounting and reproducible service boundaries.

**The $1,000 budget is not obviously better.** Doubling spend produced mixed results, with Opus 5 actually dropping 6 points on Terminal-Bench while spending twice as much. The grade: one platform, one model family, five benchmarks, no replication outside the group yet. The finding that matters for builders is that harness revision, rewriting the agent's own execution loop, outperformed data-only or training-only research by wide margins. Under fixed weights, Opus 5 improved Terminal-Bench from 30.3% to 40.8% by diagnosing three failure modes, truncation stops, unchecked completion claims, and background service termination, and patching the loop to continue execution, preserve services, and require verification commands.

*RSIGym: A Flexible Environment for Recursive Self-Improvement* - [full text](https://arxiv.org/html/2610.10310v1)

## How you show skills to an agent beats how you find them

Two papers this week converged on a finding that reshapes the retrieval stack. A Tsinghua and ByteDance team found that most agents load skills at the same rate whether the retrieved set contains a gold skill or not, and whether the task is one they can already solve or one they cannot. Llama-3.1-8B loads skills 72% of the time overall; Llama-3.3-70B loads them 11% of the time. The variation is by model personality, not by need.

Their fix is Progressive Disclosure: show the agent only skill names and descriptions, let it explicitly request the full content of the ones it wants, and stop it from drowning in distractors. Under heavy noise, eight hard-negative distractors added to the retrieved set, Full Skill Injection collapses while Progressive Disclosure holds steady. The procedure is clean: retrieve top-50 candidates, expose only metadata, allow LOAD_SKILL actions during reasoning up to ten rounds, and measure end-task accuracy.

A separate team at Fudan, NUS, and Cardinal AI Lab built SkillDAG, which goes further: skills live in a typed graph with edges for decomposition, temporal ordering, and functional dependency, and the graph evolves online as the agent commits edits with natural-language reasons. Plain cosine matching over typed embeddings scales across a 10x pool expansion where seeding-plus-diffusion degrades. Online edge edits persist, transferring to held-out episodes without degrading already-surfaced skills. The two contributions, typed structure and online editing, are separable: frozen typed graph alone adds 1.4 points on ALFWorld, online editing adds another 3.6.

**The retrieval benchmark itself is suspect.** A Korea University and ThakiCloud team released SkillRet, a large-scale skill retrieval benchmark, and found that MTEB Retrieval scores predict skill retrieval performance at only rho=0.70, with frequent ranking inversions. A model leading MTEB at 75.7 scores 59.0 on SkillRet; a 7B model at 54.0 on MTEB scores 57.0 on SkillRet, below a 270M model at 64.6. For builders, this means your embedding choice needs task-specific validation, not leaderboard faith.

*Skill Retrieval Augmentation for Agentic AI* - [full text](https://arxiv.org/abs/2604.24594)
*SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale* - [full text](https://arxiv.org/abs/2606.03056)
*SkillRet: A Large-Scale Benchmark for Skill Retrieval in LLM Agents* - [full text](https://arxiv.org/abs/2605.05726)

## Self-evolved skills beat human curation when the verifier is specific

A team at University of Illinois Chicago, MBZUAI, and McGill University built CoEvoSkills, where skills evolve through co-evolution with a surrogate verifier that generates test assertions rather than just passing or failing. The result is a 71.1% pass rate on SkillsBench with Claude Opus 4.6, up from 30.6% with no skills and 53.5% with human-curated ones. The human skills actually degrade performance in some domains, natural science among them, where human-machine cognitive misalignment produces instructions the agent misreads.

The verifier is the critical component. Removing it drops pass rate by 30 points, to 41.1%, worse than context-only evolution at 42.4%. The procedure runs: sample an initial skill bundle, execute in environment, initialize test suite from instruction and observable outputs if verifier is new, compute surrogate reward as assertion pass rate, and generate failure diagnostics for rounds below perfect score. Convergence averages 4.1 verification cycles and 2.4 ground-truth oracle rounds, with 40% of iterations resolved by surrogate alone.

Skills transfer across model families with gains of 35-44 points over no-skill baselines for six additional LLMs from five providers. GPT-5.2's own self-evolved skills outperform transferred ones by 4.8 points, so model-specific evolution still wins, but the gap is narrow enough that skill marketplaces are now plausible.

*CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification* - [full text](https://arxiv.org/abs/2604.01687)

## What to read

*Athanor: An Agent-Native System for Autonomous Post-Training Research* - [full text](https://arxiv.org/abs/2610.21055v1)

The first demonstration of frontier agents autonomously post-training a raw base model to match official instruct performance through a recursive self-improvement loop, with full sandboxed execution. One group, one model family, no external replication yet. Read this if you are building the training infrastructure for agent self-improvement and need to see what a closed loop looks like with real compute accounting.

*MLExpert: Towards a Generalist Agentic Model for Autonomous Machine Learning Engineering* - [full text](https://arxiv.org/abs/2610.22344)

A full post-training stack, hierarchical SFT and WIRL, for autonomous long-horizon ML engineering. The hierarchical supervision and world-model-informed reward learning are the parts most agents lack. One architecture, extensive ablations, no independent reproduction yet. Read this if your agents need to perform ML engineering tasks end-to-end rather than call APIs.

*Learning Self-Orchestration in Decentralized Agent Swarms* - [full text](https://arxiv.org/abs/2610.22322)

Market-based post-training for joint policy and self-orchestration learning in multi-agent systems. The coordination mechanism is novel: agents bid for task allocation and learn value functions for their own specialization. One framework, simulation evaluation, no real-world deployment yet. Read this if your multi-agent systems currently use fixed roles and you suspect that is the bottleneck.

---

69 papers read in full this week, from 2,161 that arrived. The rest of the field is still arguing about whether agents need heavier retrieval or lighter orchestration. These three papers suggest the answer depends on whether your skills are static documents or living code, and that the tooling to test either is now available with a budget cap attached.

**Accelerate every builder and agent to frontier speed.**
