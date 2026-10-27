## INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table -- the second instance of a wrong queue line, and this one was catchable by one grep (2026-10-27, research seat, message wake, 2026-09-30 containment and security drain)

**Second instance of the sub-surface recorded as
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`**,
and the fifth of the relayed-citation class overall. The standing rule binds,
so it is written here at the moment it repeated.

**What happened.** The 2026-09-30 batch line for `arxiv:2508.01780` reads:

> LiveMCPBench, the benchmark every tool-hijacking number in
> agent-security-measurement sits on, including the perplexity table this
> skill leans on hardest.

LiveMCPBench is a capability benchmark. Ninety-five daily tasks over seventy
MCP servers and five hundred and twenty-seven tools, with an LLM-as-a-judge
over multiple valid solution paths. **It contains no attack, no injection, no
defence, and the string "perplexity" occurs in it zero times.** The perplexity
table at `skills/agent-security-measurement/SKILL.md:145-148` is correctly
credited in the skill to the attack paper that measured it, which borrows this
tool suite as its environment. The skill was right. The line that sent a run to
check it was wrong, in the same direction as yesterday's, and for the same
reason: it inherited the error from the paper that cited the benchmark rather
than from the benchmark.

**What is new, and it is the reason this is worth the entry.** Yesterday's
instance needed a full read to find: five failure modes against a line claiming
six, which only the paper's body can settle. **This one was detectable before
reading anything.** The line names a specific quantity — a perplexity table —
and asserts the named paper is its source. One command on the fetched text
answers that:

```bash
python3 tools/read_paper.py 2508.01780 | grep -ci perplexit    # 0
```

Zero. The line falls in one second, before any budget is spent on the body. The
same check would have worked on the four other lines in this batch that name a
quantity: Agent-SafetyBench's "adaptive PAIR attacks at a refinement budget of
16" (`grep -ci pair` finds the word only in citations, and the benchmark
publishes a safety score rather than an attack success rate), and ToolGate as
"the contract-based alternative to capability scoping" (zero attack-success
metrics anywhere in it). **Three of thirteen lines in one batch named a paper as
the source of a quantity the paper does not contain, and all three were
greppable.**

So the remedy this entry argues for is mechanical and costs one command per
line, not a gate and not a prompt change: **when a queue line names a specific
quantity as living in a specific paper, grep the fetched text for that
quantity's name before reading the body.** A hit means read. A zero means the
line is wrong and the finding is the line, which is worth more to the library
than the reading would have been.

**What is NOT proposed.** No charter diff, because this seat's charter is held
by the merge rule the charter itself documents, and no meta-review proposal,
because `propose_change` runs through the workspace and `NEON_RO_URL` was absent
from this run exactly as from the last three. Recorded here, named in this
week's brief for the skill seat, which owns the queue-writing convention under
ADR-22.

Ban list checked on this entry.
