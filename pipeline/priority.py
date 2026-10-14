"""Which papers go first. One list, shared by triage and distill.

The owner's standing threads, in her order of 2026-09-23 (reasoning), 2026-09-25
(reasoning to the front of the queue) and 2026-09-29 (four more: protocols,
containment, security, self-improvement). A paper whose TITLE matches one of
these terms is read before a paper that does not, at every stage that has a
queue.

## Why this is a module and not a constant in triage.py

It was a constant in `pipeline/triage.py` until 2026-09-30, and triage was the
only stage that honoured it. That is a priority with a hole in it: triage
decides WHICH papers are worth reading and distill decides WHEN each one is
actually read, so a thread could be promoted through triage in a morning and
then wait weeks behind the day's intake in the distill queue. The owner's
directive of 2026-09-29 asks for the order at the reading stage, which is this
stage, so the list has to be reachable from both jobs.

Two copies of a list like this drift, and the drift is silent: the threads
triage promotes stop being the threads distill reads first, and nothing prints
a disagreement. So there is one copy, here, and both jobs import it. Both Modal
images carry this file.

## Matching is on the title only, deliberately

Half the corpus mentions reasoning somewhere in an abstract, so an abstract
match would promote thousands of papers, and a priority that covers everything
is not a priority. The terms beyond the bare thread names are the named methods
the rubric in `prompts/triage.md` routes to `distill`, so a paper whose title
says GRPO and never says reasoning is still reasoning work and still goes first.
"""

from __future__ import annotations

#: The standing threads, as title substrings, lowercase. Adding a term here
#: changes what two scheduled jobs read first, which makes it a runtime change
#: under docs/agents/runtime-changes.md: both jobs need a redeploy before the
#: new term reaches a queue.
#: The same terms, grouped by the thread each one belongs to, because one
#: consumer needs to know WHICH thread a paper matched and not merely that it
#: matched something. `pipeline/retag_threads.py` is that consumer: the owner's
#: directive of 2026-10-05 asks it to retag the claims of papers matching these
#: threads, and the thread name is what it offers the model as a candidate tag.
#:
#: The keys are the topic names in `pipeline/topics.py`, exactly, so a thread
#: here with no tag there is a bug a test catches rather than a silent miss.
#: `reasoning` is in the table because it is one of these threads and leaving it
#: out would make the flat tuple below a different list.
THREAD_TERMS = {
    # Reasoning models. The owner's order of 2026-09-23, put at the front of
    # the queue by her directive of 2026-09-25. The count that produced it,
    # from Neon: 209 papers with "reasoning" in the title, 147 of them never
    # triaged at all.
    "reasoning": (
        "reasoning",
        "chain-of-thought",
        "chain of thought",
        "rlvr",
        "grpo",
        "verifiable reward",
        "test-time compute",
        "test time compute",
        "inference-time compute",
        "process reward",
        "long cot",
    ),
    # Owner's order of 2026-09-29: four more threads go first, because the
    # corpus held hundreds of their papers and had read almost none.
    "protocols": (
        "model context protocol", "mcp", "agent protocol", "agent-to-agent",
        "a2a", "agent interoperab", "agent identity",
    ),
    "containment": (
        "sandbox", "container", "isolation", "microvm", "firecracker",
        "gvisor", "containment",
    ),
    "security": (
        "prompt injection", "jailbreak", "tool poisoning", "agent security",
        "exfiltrat", "guardrail",
    ),
    "self-improvement": (
        "self-improv", "self-evolv", "recursive self", "harness evolution",
        "self-refin",
    ),
}

PRIORITY_TERMS = tuple(
    term for terms in THREAD_TERMS.values() for term in terms
)

#: The same predicate in the other language that needs it: `%term%` for
#: Postgres `ilike any`. Derived from the tuple above so the two cannot drift.
PRIORITY_PATTERNS = [f"%{term}%" for term in PRIORITY_TERMS]


def is_priority(title: str) -> bool:
    """Is this paper one of the standing threads, by its title? Mirrors the SQL."""
    low = (title or "").lower()
    return any(term in low for term in PRIORITY_TERMS)
