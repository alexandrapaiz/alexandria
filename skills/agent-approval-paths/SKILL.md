---
name: agent-approval-paths
description: What a human confirmation in an agent's action loop buys, what it costs, and why the reusable allow-rule that relieves confirmation fatigue is a measured escalation path. The subject is what the approving human is shown, how many confirmations the design costs per legitimate task, and what authority survives the yes. Use when an agent pauses for human confirmation and you are deciding what the human must be shown; when a human already approved an agent action that proved harmful; when the summary an approving human reads was written by the agent itself or by a fetched page; when agent confirmation fatigue or over-prompting is the complaint and a longer trusted tool list is the proposed cure; when shipping an always-allow, a remember-this-choice or a persisted permission prefix so the agent stops asking twice; or when choosing where a shell command mediator lands on the silent-pass against over-prompting curve.
version: 1
status: draft
provenance:
  extracted: 2026-11-02
  validated: ""
  differential_screen: "not run, and no section here is screened. This seat has no route to either eval arm: `.github/workflows/agent-skill.yml` carries no GROQ_API_KEY for the cheap arm and `pipeline/budget.py` knows only moonshot and groq, neither of which serves the benchmark subject. Both are queued in docs/agents/pending-workflow-changes.md, item 12. ADR-38 rule 1 asks that every section be put to a bare subject before it ships and rule 5 asks for a bare-first qualification pass; neither has run, so the task set below carries authored predictions rather than observations and says so per task. The ADR-40 item 6 task audit needs the judge model and is also unrun."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  claims: []
  papers:
    - "The Verifiable Action Card: Grounding Agent Approval in the Action That Will Execute, arxiv.org/abs/2609.18411, read in full 2026-11-02 (83,186 chars, exit 0), for delta 1's four arms. No claim row yet; the paper is queued for ingestion and the queue is blocked on the compute workspace"
    - "Consent Integrity for LLM Agents: Rendering Approvals From Ground Truth, arxiv.org/abs/2606.02668, read in full 2026-11-02 (45,894 chars, exit 0), for delta 2's two third-party corpora and the frontier between them. No claim row yet, same blocker"
    - "From Approval to Abuse: Eliciting Persistent Permissions From Coding Agents, arxiv.org/abs/2610.22987, read in full 2026-11-02 (67,216 chars, exit 0), for delta 3's acquisition and downstream stages and the benign control. No claim row yet, same blocker"
---

# Agent approval paths

Three findings about the human confirmation step in an agent's action loop, each one a place the measured evidence points away from the design a competent engineer reaches for first. The common root: an approval gate is a channel, and its security is set by what the human is shown and what authority survives the click, not by the fact that a human was asked. Asking is the cheap half and it is the half that gets built.

This adds to standard engineering practice rather than replacing it. Putting a human in front of a consequential action is already correct, and nothing below argues for removing the gate. All three findings are about the design of that step, and all three have the same shape: the obvious version of the control is measurable and measures far worse than it reads.

## Apply: the builder's checklist

1. **The confirmation text is decoded from the action that will execute**, at the enforcement point, never from the agent's own summary and never from a label a fetched page controls (delta 1).
2. **The approval binds to that exact action and is re-verified at dispatch**, so changed state cannot substitute a different action after the click, and an action *class* is never what gets approved (delta 1).
3. **Both burden numbers are measured before shipping**: confirmations per legitimate task and false-block rate, against a demonstrated floor of 0.94 and zero (delta 1).
4. **The uninspectable rate is the fatigue number, not the prompt rate**, measured on a normal-usage corpus you did not author, and anything the mediator cannot decode surfaces as uninspectable rather than being silently approved (delta 2).
5. **No persisted allow-rule is ever created from a scope proposed during a task**, and a mid-task request to persist one is handled as an alert, because benign runs proposed one in 0 of 25 (delta 3).
6. **A persisted rule binds to the action and its resource, never to a command prefix**, and expires at the task boundary rather than being inherited across it (delta 3).

## Delta 1: a confirmation step is not the control, and what the human is shown is

*Validation: none. No trial, no consumer report, no bare-arm screen (see `provenance.differential_screen`). Eval tasks ap-t1, ap-t4. The naive-confirmation arm is the number this section rests on and the one a bare subject is least likely to supply, because the usual advice stops at "ask the user".*

Four arms differing only in the confirmation step, run across five open-weight models plus a separate GPT-4.1 run, 293 clean trials in the sweep plus 40 in that run (The Verifiable Action Card). With no gate, attack success is **78 percent** aggregate, 68 to 100 by model, at 80 percent task completion. With a naive confirmation, whose summary derives from a label the page controls, attack success is **72 percent** at one confirmation per task and a zero false-block rate. With approval rendered from the observed ground-truth action and re-verified at dispatch, attack success is **0 percent on all five models**, task completion is 78 percent, the false-block rate is **0 percent**, and the burden is **0.94 confirmations per legitimate task**.

So adding a human bought six points and changing what the human was shown bought the other seventy-two. The paper's provenance-stripped arm also scores 0 percent at 0.95 confirmations, which locates the effect in the rendering and the dispatch-time re-verification rather than in the provenance component, and the paper's own reading is that the protection is architectural rather than model-specific, since the check inspects the ground-truth action after the model has already decided.

1. Decode the confirmation's text from the observed action at the enforcement point. Treat every string the model wrote or a fetched page supplied as adversary-chosen input, because a human shown a forgeable summary approves the disguised action at nearly the ungated rate.
2. Bind the approval to the one concrete action and re-verify it at dispatch, refusing if it changed. Approving an action class leaves the substitution open.
3. Measure the two numbers that decide shippability: confirmations per legitimate task and false-block rate. The published floor is 0.94 and zero, so a design that costs several confirmations per task, or blocks legitimate work at all, has a defect rather than a tradeoff to accept.
4. Run a naive-summary arm beside your own gate rather than only an ungated arm. A gate that cannot beat its own naive arm by much more than six points is matching on adversary-chosen text (ours, not the paper's).
5. Before porting this, price the decoder. The result is measured in an agentic browser where the ground truth is a DOM commit; on a shell or an API the decoder is the whole job, and delta 2 is what it costs.

## Delta 2: the cost of the path is the uninspectable rate, not the latency

*Validation: none, same gap as delta 1. Eval tasks ap-t2, ap-t5. Both corpora here are third-party and were not authored for the paper, which makes this the best-evidenced section in the file and the one whose numbers transfer least, since they are properties of one trust list.*

The machine cost is not the constraint and the paper that measures it says so. Mean analyzer overhead is **0.056 ms**, median 0.050, p99 0.122, over n=4000 (Consent Integrity), which it calls negligible against inference latency, while stating plainly that this excludes the total mediation and trusted-path rendering its prototype specifies but does not implement and which "would dominate any end-to-end figure". Quoting the microsecond number as the cost of an approval path is therefore quoting the one component the authors exclude from the cost.

The cost it does measure sits on two corpora the authors did not write. On **1,330** trusted-tool abuse commands expanded from GTFOBins across 478 binaries, the analyzer flags **90.0 percent** and silently passes **10.0 percent**, and every silent pass runs through a binary its own trust list allows. On **28,798** idiomatic commands from tldr-pages across 6,503 tools, it prompts on **95.9 percent** and marks **87.0 percent uninspectable**, **83.4** of those percentage points purely because the tool is absent from the trust list, leaving **4.1 percent** that pass with no prompt. The paper names the trade-off as its central empirical finding and it is structural rather than an implementation gap: the same trust list that holds silent passes to 10 percent forces 87 percent uninspectable on normal use, growing the list to relieve that fatigue reintroduces silent passes because a trusted tool can be abused, and a boundary-only static mediator can choose where on the curve to sit but cannot occupy both ends.

1. Report the **uninspectable** rate and not the prompt rate. Some prompted commands are genuinely consequential, so the raw prompt rate flatters the design; uninspectable is the clean fatigue proxy and it is the paper's own choice of metric.
2. Measure silent passes on an abuse corpus and the uninspectable rate on a normal-usage corpus, both third-party. One corpus answers exactly one of the two questions, and a co-designed corpus answers neither.
3. Surface anything the decoder cannot classify as uninspectable or high-risk instead of approving it silently, so the guarantee is analyzer-relative and the gap is visible in the number rather than absent from it.
4. Price every trust-list addition as a silent-pass risk and record which abuse-corpus entries it admits, because 100 percent of the measured silent passes ran through trust-listed binaries rather than through a decoder gap.
5. Pick the point on the curve deliberately and write the number down. The way off the curve is a better decoder or mediation that is not boundary-only, never a longer trust list, and a design that has not named its point has defaulted to one.

## Delta 3: the allow-rule that relieves the fatigue is the measured escalation path

*Validation: none, same gap. Eval tasks ap-t3, ap-t6. This is the delta a bare subject is least likely to hold at all, and it is why this file is a containment document rather than a usability one: delta 2's remedy is delta 3's attack surface.*

The standard remedy for delta 2's fatigue is the reusable allow-rule that Codex CLI and Claude Code both ship. Eliciting one during an ordinary benign task raises Permission Capability Coverage to **0.48 to 0.61** across four agent configurations, against **0.25 to 0.55** for a direct request, and makes **9 to 18 of 25** adversarial goals reachable (From Approval to Abuse). Initialized from those same checkpoints, downstream goal completion reaches **17 of 17** on one Codex configuration with 13 prefix-attributed, **14 of 18** on another with 11 prefix-attributed, and **13 of 14** on claude-haiku-4.5 with 9 prefix-attributed. On claude-sonnet-5, where the baselines fail completely at 0 of 9, the framework still realizes 3 of 9 through other authorized pathways with no prefix match at all.

The control is the number to design against: **Benign Control yielded 0 of 25 on every model**, so a persisted permission is never proposed organically. That makes the appearance of such a proposal during a task a signal rather than a convenience, and it is a cheap signal precisely because its false-positive rate on benign runs was measured at zero.

1. Never create a persisted allow-rule from a scope the agent proposed mid-task. The scope comes from the authenticated request, compiled before any repository content or tool output is read.
2. Treat an in-task request to persist a rule as an alert with a mechanical response rather than a dialog, on the strength of the 0-of-25 control. A benign run does not ask.
3. Scope a persisted rule to the action and its resource, never to a command prefix, since the prefix is what the completed attacks were attributed through in 13 of 17, 11 of 14 and 9 of 13 of their cases.
4. Expire persisted rules at the task boundary and re-confirm, because the measured escalation crosses from acquisition to abuse on one unchanged checkpoint.
5. Do not read model alignment as a defence on this path. The one model whose baselines scored 0 of 9 still gave up 3 of 9, by pathways that never matched the acquired prefix, so a stronger model moved the mechanism rather than the outcome.

## Caveats

- **This skill is unmeasured and it cites no claim ids.** No section has a differential delta, no bare-arm screen has run, and the task set below is written rather than qualified. `status: draft` is deliberate and is lower than the `provisional` the format contract prescribes: the library's own gate (`tests/skill-provenance.test.mjs`) allows exactly one skill to cite zero claim ids and only while it is a draft, which is the honest state for three papers that have no rows yet. All three are queued for ingestion and the queue is blocked on the compute workspace, not on this file.
- **Each of the three papers measures a different surface and none of them measures the others'.** The Verifiable Action Card is an agentic browser where ground truth is a DOM commit. Consent Integrity is a shell-command mediator whose total mediation and trusted path are specified and *not implemented*, which the authors say would dominate any end-to-end figure. From Approval to Abuse is coding agents on repository tasks. Reading delta 1's 0 percent onto a shell surface, or delta 2's 87 percent onto a browser, is the error this caveat exists to stop.
- **Delta 2's percentages are properties of one trust list, not constants.** The 10.0 and 87.0 figures move with the list's size and composition; what transfers is the frontier's existence and the direction of the trade, which the paper argues structurally, rather than either endpoint.
- **Delta 3's denominators are small.** Twenty-five adversarial goals, four agent configurations, and downstream cases in the single digits to high teens. The 0-of-25 benign control is the sturdiest number in that paper and the 17-of-17 is the most fragile, being one configuration at its ceiling.
- **Delta 1's zero is across five open-weight models plus one 40-trial GPT-4.1 run**, so it is a strong result on a narrow model set, and the paper's claim is architectural rather than statistical: the check reads the ground-truth action after the model has decided, so it does not depend on the model's reasoning being robust.
- All three papers are 2026 work read in full on 2026-11-02 with this repository's own reader at exit 0. If a source result is later contradicted or narrowed, this skill is revised or retired with the reason recorded.
