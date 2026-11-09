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

**Update, 2026-11-09, later run of the same seat: this seat's half is done, and
the deferral's stated reason was half right.** The remaining 48 separators across
7 skills are replaced with the comma form the two newest skills already used, so
`python3 tools/ban_list.py skills/*/SKILL.md` is **0 findings over 10 of 10
files**, down from 59 over 8 of 10 when this entry was written. Safe for the
page because `site/lib/skill-provenance.js` returns `papers` verbatim and splits
nothing on the separator, and the compliant entries already carried commas
inside their quotes.

The deferral above gave two reasons and they did not survive equally.

*One skill per run* does not reach this, because the rule governs writing and
revising a skill, and a separator swap in a frontmatter list is neither. No
claim, number, prescription or line of prose moved in any of the seven.

*A reader-facing edit invalidates the trigger receipt and should be measured
rather than swept* was correct about the mechanism and wrong about the cost.
`skills/_validation/trigger_test.py --receipts` did go to exit 1 with seven
stale receipts, so the edit genuinely could not ship without a re-measurement.
But the measurement is local, it is the pre-registered `lexical/2.2` engine with
no network and no key, and it moved nothing: **74 of 84 at reliability 0.881
before and after, identical case sets, zero of 84 cases changing verdict**, and
exactly the seven edited shas differing. The thing that made this look expensive
was the receipt bookkeeping rather than the measurement, and that bookkeeping is
the same-day bundle tie recorded as
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`,
now at five occurrences.

**Step (1) is still open and still the engineer's**, which is why this entry
stays `proposed` rather than closing. Nothing yet runs `tools/ban_list.py` over
`skills/`, so the 0 of 10 measured today is a state and not a guarantee, and the
next seat to paste a title with an en dash in it reintroduces the class silently.
Folding the mechanical six into `tests/test_skill_receipts.py`, which already
opens every `SKILL.md`, is what makes today's number hold. This is incident 20's
class exactly: the gate that decides something gets written down exists, and the
gate that decides it gets checked before shipping does not.
