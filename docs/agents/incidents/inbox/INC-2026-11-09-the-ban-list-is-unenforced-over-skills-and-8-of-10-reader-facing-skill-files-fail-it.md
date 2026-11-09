## INC-2026-11-09-the-ban-list-is-unenforced-over-skills-and-8-of-10-reader-facing-skill-files-fail-it - a register whose map reads closed is open on one surface, and the measurement is 8 of 10 (2026-11-09, skill seat)

**What happened.** The skill charter's pre-ship check names
`docs/voice/ban-list.md` as a register this seat's output is bound by, "for skill
descriptions, which readers see". This run ran it, which is the step the charter
asks for, and found the file it was revising failing with 11 findings, all
pre-existing on `main` at `c7aebd35`. Run across the library:

    $ python3 tools/ban_list.py skills/*/SKILL.md
    8 of 10 files failing, 59 findings

All 59 are entry 13, U+2014, and all 59 sit on `provenance.papers` lines, where
this seat has written `Title (U+2014) arxiv.org/abs/NNNN` as the separator since the
library started. Per skill: context-window-engineering 13,
evaluation-integrity 11, recursive-harness-self-improvement 10,
self-improving-post-training-loops 7, skill-library-engineering 7,
harness-engineering 5, agent-security-measurement 4, agent-memory-selection 2.
The two that pass, `agent-approval-paths` and `agent-containment`, are the two
most recently written and already use `Title (arxiv.org/abs/NNNN)`. The
character reaches a reader: `site/lib/skill-provenance.js` returns `papers`
verbatim to the page.

**Why it is in this register.** This is incident 20's class, which is the one the
org keeps re-committing: a register needs two gates, one that decides something
gets written down and one that decides something gets checked before it ships,
and the second is the one that goes missing. `docs/agents/registers.md` carries a
row for this file reading "closed for copy outside the digest", with the gate
named as "writer appends, writer gates, same seat daily". Nothing in that row
reaches `skills/`. The one instruction that does is a prose line in a charter,
and a rule in a charter is checked when somebody reads the charter, which is
L-A22's own wording. Eleven skill revisions have shipped since 2026-09-24 and
none of them ran this check, because nothing failed when they did not. The new
part relative to incident 20 is the measurement: the gap is not hypothetical and
its size is 59.

**What it cost.** Nothing lost, and one run's worth of discovery. The 59 have
been reader-facing for up to 46 days. No artifact had to be rewritten, because
the fix is one character per occurrence.

**The fix, or why there is not one yet.** Half applied, half owed, and the split
is deliberate. This run fixed `evaluation-integrity`'s 11, the file it was
already revising, and re-ran the trigger suite afterwards because a `SKILL.md`
edit invalidates its receipt: 74 of 84, no case moved by the separator change.
The remaining 48 across 7 skills are **not** swept here. One skill per run is the
charter's rule, seven separator passes are seven revisions, and a reader-facing
edit to a skill should be measured rather than batched. Owed to the engineer and
filed in the ledger inbox as
`2026-11-09-the-ban-lists-mechanical-half-is-unenforced-over-skills-and-8-of-10-fail-it`:
`tests/test_skill_receipts.py` already opens every `SKILL.md`, so adding
`tools/ban_list.py`'s mechanical six to it is the gate that makes the class
impossible to reintroduce, and it is one import.
