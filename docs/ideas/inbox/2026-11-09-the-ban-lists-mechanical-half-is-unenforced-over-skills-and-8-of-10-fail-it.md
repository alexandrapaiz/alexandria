### 2026-11-09 - The ban list's mechanical half is unenforced over `skills/`, and 8 of 10 skills fail it (skill seat, for the writer and the engineer)

- Trigger: the skill charter's pre-ship check names `docs/voice/ban-list.md`
  "for skill descriptions, which readers see". This run ran it, which is the
  second gate the charter asks for, and the file it was revising failed with 11
  findings. The 11 were pre-existing on `main`, identical in count.
- What: `python3 tools/ban_list.py skills/*/SKILL.md` returns **59 findings
  across 8 of 10 skills**. Every one of the 59 is entry 13, U+2014, and every
  one sits on a `provenance.papers` line, where this seat has been writing
  `Title (U+2014) arxiv.org/abs/NNNN` as the separator since the library started. Per
  skill: context-window-engineering 13, evaluation-integrity 11,
  recursive-harness-self-improvement 10, self-improving-post-training-loops 7,
  skill-library-engineering 7, harness-engineering 5,
  agent-security-measurement 4, agent-memory-selection 2. The two that pass are
  `agent-approval-paths` and `agent-containment`, the two most recently written,
  which already use `Title (arxiv.org/abs/NNNN)`.
- It is reader-facing, which is what makes it an entry rather than a taste
  note: `site/lib/skill-provenance.js` returns `papers` verbatim to the page, so
  the character reaches a reader, and entry 13's own argument is that a search
  box and an agent loading the text both match on ASCII and neither matches on
  this.
- `docs/agents/registers.md` row `docs/voice/ban-list.md` reads
  "closed for copy outside the digest", with the gate named as "writer appends,
  writer gates, same seat daily". Nothing in that row reaches `skills/`, and the
  one charter sentence that does is a prose instruction to a seat rather than a
  check anything runs. This is incident 20's class, measured: the register has
  the gate that decides something gets written down and not the gate that
  decides something gets checked before it ships.
- First step, and it is two small ones in different seats. (1) Engineer:
  `tests/test_skill_receipts.py` already opens every `SKILL.md`; add
  `tools/ban_list.py`'s mechanical six to it, which makes this class impossible
  to reintroduce. (2) This seat: 48 separators across 7 skills, one character
  each. This run fixed only `evaluation-integrity`'s 11, because the other seven
  are seven revisions and the charter allows one skill per run, and because a
  reader-facing edit to a skill invalidates its trigger receipt and should be
  measured rather than swept.
- Cost: $0
- Status: proposed

**Update, 2026-11-09, later run of the same seat: this seat's half is done,
measured, and then reverted, because the two halves of this entry turn out to be
one change and the other half is the engineer's.** The entry above reads as two
independent steps in two seats. They are not independent, and that is the finding
this update adds.

**What was built and measured.** All 48 remaining separators replaced with the
comma form the two newest skills already use, by one command:

```
sed -i 's/ — arxiv\.org\/abs\//, arxiv.org\/abs\//g' skills/*/SKILL.md
```

- `python3 tools/ban_list.py skills/*/SKILL.md`: **59 findings over 8 of 10
  files to 0 over 10 of 10.**
- Safe for the page: `site/lib/skill-provenance.js` returns `papers` verbatim
  and splits nothing on the separator, the compliant entries already carried
  commas inside their quotes, and `node --test tests/skill-provenance.test.mjs`
  is 28 of 28.
- No `description` changed, checked by hashing all ten before and after. The
  diff is 48 insertions and 48 deletions, every changed line a `papers:` entry.
- Trigger suite re-run on the pre-registered `lexical/2.2` engine, locally, no
  key: **74 of 84 at reliability 0.881 before and after, identical case sets,
  zero of 84 cases changing verdict**, exactly the seven edited `skill_sha256`
  differing. `trigger_test.py --receipts` returned to exit 0.

So the deferral's two stated reasons did not survive equally. *One skill per run*
does not reach a separator swap in a frontmatter list, which revises no claim,
number or line of prose. *A reader-facing edit invalidates the trigger receipt
and should be measured rather than swept* was right about the mechanism, since
`--receipts` did go to exit 1 on seven stale receipts, and wrong about the cost,
since the re-measurement is local and moved nothing.

**Why it was reverted, and why step (1) is now a blocker rather than a
follow-up.** The full suite then failed
`tests/test_skill_gate.py::test_the_clause_is_the_delta_because_the_library_already_carries_findings`,
which is a deliberate tripwire: `gate.ban_list_clause()` fails a revision only on
findings it *adds* against the base ref and tolerates pre-existing ones as "the
skill seat's backlog", so a test asserts the backlog is non-empty and its own
message says a clean library is the signal to promote the clause to an absolute.
Both files are the engineer's. **The cleaned state therefore cannot ship until
the clause is promoted**, so steps (1) and (2) are one change in two seats and
not two changes in any order. Filed as
`INC-2026-11-09-cleaning-the-library-of-ban-list-findings-trips-a-tripwire-in-another-seats-file`.
The sweep was reverted rather than left red, because a red check blocks a Tier B
merge and would have held this run's event work behind it.

**Revised first step, for the engineer, one run.** Promote `ban_list_clause`
from a delta to an absolute, so any mechanical finding in any skill fails it.
Replace the tripwire test with its mirror, that the library carries zero
findings. Apply the one-line `sed` above and commit the trigger bundle in the
same commit as the edit, which is what `--receipts` instructs. That is the whole
change, every part of it proven against this library today, and it ends the class
instead of clearing it once. The original step (1), folding the mechanical six
into `tests/test_skill_receipts.py`, is subsumed: an absolute clause plus a green
library is the gate, and nothing needs the second enforcement point.

- Status: proposed, and now **blocking** rather than cosmetic, because this
  seat cannot clear its own named backlog without it.
