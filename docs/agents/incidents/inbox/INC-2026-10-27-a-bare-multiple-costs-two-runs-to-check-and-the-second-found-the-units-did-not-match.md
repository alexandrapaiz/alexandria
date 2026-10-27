## INC-2026-10-27-a-bare-multiple-costs-two-runs-to-check-and-the-second-found-the-units-did-not-match - a shipped sentence put four multiples side by side with no unit and no backbone, and resolving it took one run from each of two seats (2026-10-27, skill seat, message run)

**What happened.** `skills/agent-containment/SKILL.md` delta 1 read "ToolFence
measured **1.63x** on Qwen3-max and **3.79x** on GPT-4o against **10.67x to
12.95x** for the CaMeL baseline (claim 1226)." Four multiples, no unit on any of
them, no backbone on two of them. The research seat drained CaMeL
(`arxiv:2503.18813`) on 2026-10-27, found its published overhead to be 2.82x
input and 2.73x output tokens, and routed the sentence here as "roughly four
times the primary source's figure for what the skill's sentence presents as the
same quantity." It said in the same breath that it could not tell whether
ToolFence was measuring latency rather than tokens, because ToolFence was not in
its batch.

This run fetched ToolFence (`arxiv:2609.37196`) in full and that is exactly what
the gap was. ToolFence's 10.67x and 12.95x are **mean end-to-end runtime per
evaluation sample**, 48.0 and 81.7 seconds over 50 clean tasks and 200 attacked
pairs, and its own 1.63x and 3.79x are the same quantity on the same figure. So
all four multiples in the sentence were comparable after all and the four-fold
disagreement never existed. The defect the correction named is real and is
narrower than it looked: not a wrong number, an uncheckable one. Both the unit
and the per-multiple backbone are now written in, and 10.67x is named as GPT-4o
and 12.95x as Qwen3-max.

The same reading turned up a second instance of the class inside CaMeL itself.
Its section 6.5 and Figure 13 say 2.82x input and 2.73x output for the median
AgentDojo task under attack, its Table 10 gives 2.73x input and 2.82x output
**not** under attack, and its Table 13 gives 2.02x input and 2.64x output
**under** attack. The caption matches the not-under-attack row with its two
columns transposed. And every median understates the distribution badly, since
not under attack the means are 7.24x and 6.23x with a standard deviation of
14.79, so a relayed "about three times" and a relayed "about seven times" can
both be sourced to one paper and one table.

**Why it is in this register.** The standing rule records any issue at the moment
it repeats, and this is the third instance in two days of a number in shipped
skill text that its own primary source cannot confirm as stated. The first is
`INC-2026-10-26-a-shipped-skill-carried-four-numbers-that-are-not-in-its-paper`
(skill seat, still open on #582), where four of six figures in
`recursive-harness-self-improvement` appeared nowhere in the paper. The second is
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`
(research seat, #628), where three of thirteen queue lines named a paper as the
source of a quantity that paper does not contain. This one is the variant that
is hardest to catch, because the number is **right** and unreadable, so no
re-reading of the citing paper ever flags it. A unit is what makes a quantity
falsifiable, and all three instances passed every gate this library runs.

**What it cost.** Two runs of two seats on one sentence. The research seat spent
a paper fetch and a drain-record section concluding that it could not resolve
the gap, and this seat spent a second paper fetch resolving it. The sentence had
been live for twenty-one days. The adjacent repair in
`agent-security-measurement`, the "twice the utility" multiple, cost the same
pattern a third fetch and had been live for twenty-seven days, and three
independent readings of that one baseline produced three different utility
numbers, 41.0, 41.2 and 53.60, none of them wrong and all of them measured
differently.

**The fix, or why there is not one yet.** Both sentences now carry the unit and
the backbone, and `agent-containment` gains a caveat holding CaMeL's three
published token values so that nobody reads a runtime multiple against a token
multiple again. What is **not** fixed is the gate: nothing in `tools/` checks
that a multiple in a skill names what it is a multiple of. The cheap version is
one lint over `skills/*/SKILL.md` for a bare `N.NNx` or `N times` with no unit
noun within the sentence, which would have fired on both of today's sentences
and is proposed in `docs/ideas.md` for the engineer. Until it exists this class
is caught only by a seat that happens to fetch the primary source, which is one
run's budget per sentence.
