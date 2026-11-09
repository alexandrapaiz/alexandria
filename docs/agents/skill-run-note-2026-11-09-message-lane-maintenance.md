# Skill seat run note, 2026-11-09, lane maintenance

Event: pull request #850 merged, with the instruction to continue with the next
item in this seat's lane on the board and say what was taken.

## What I took, and it is not the board item

The board's skill lane holds eleven items. Ten sit in `Review` awaiting merges.
The eleventh, `7e6cfb5d` "Package the before-and-after a stranger sees in their
first session", is the only one with a runway, and its effect half is blocked on
`GROQ_API_KEY`. The PM named that on 2026-11-02 as the owner's secret to write
and nobody else's. Four previous runs of this seat reported the same block, and
this run makes five. I did not re-take it and I did not narrow it into something
that looks like it.

So this run is maintenance, which the charter puts ahead of new work, and this
time the maintenance had a named owner and a named unblock rather than a search.

**The ban-list sweep, deferred twice, landed.** 48 U+2014 separators across 7
`SKILL.md` files. The deferral was never about the edit: the edit is one
character each and revises no claim, number or line of prose. It was about a
tripwire in `tests/test_skill_gate.py` that asserted this library carries a
non-empty ban-list backlog, so cleaning the library turned the suite red, and
the previous run reverted its own correct sweep rather than ship a red check.
The engineer shipped the other half on #864 this morning: `ban_list_clause` is
an absolute, the tripwire is a ratchet, and `tools/ban_list.py --fix` performs
the repair. This run stacked on that branch and the sweep now lands green.

## Numbers

| | before | after |
|---|---|---|
| `ban_list.py` over `skills/*/SKILL.md` | 48 findings, 8 of 10 files, exit 1 | **0 findings, 10 of 10, exit 0** |
| trigger suite, `lexical/2.2`, local | 74 of 84, reliability 0.881 | **74 of 84, reliability 0.881** |
| cases moving on verdict, winner, score or margin | | **0 of 84** |
| `--receipts` | 7 stale, exit 1 | **0 stale, exit 0** |
| `description` fields moved, by sha256 | | **0 of 10** |
| `node --test tests/skill-provenance.test.mjs` | 28 of 28 | 28 of 28 |

The diff over `skills/` is 48 insertions and 48 deletions and every changed line
is a quoted `provenance.papers` entry, checked by diffing with `-U0` and
filtering for lines that are not quoted list items, which returns nothing.

## The defect the measurement found, and it was this seat's own

The per-case comparison built to prove the sweep moved nothing held **83
entries for a suite that reports 84 cases**. `skills/agent-containment/triggers.json`
carried two different prompts under the id `ac-pos-5`, added by this seat's
commit `a3349aff` eight hours earlier on an id the 2026-11-02 revision already
held. One passes and one fails, so `by_kind.positive.failed` named an id rather
than a case, and the suite's own note said in bold "ac-pos-5 does not fire"
while a case with that id fired and passed.

The plan-integrity case is now `ac-pos-8`. The 2026-11-02 case keeps the id it
held first, which leaves every result bundle written before today correct as
recorded. The note is corrected rather than left standing. No measurement moves.

The class is the same one that turned `main` red this morning in a ledger entry
of this seat's: one key, two values, the first wins and the second is silently
absent rather than rejected. Found by luck, not by a gate, and no gate exists:
a grep for a uniqueness check over case ids across `tests/`,
`skills/_validation/` and `tools/skill_*.py` returns zero hits. That is filed
for the engineer.

## Honest limits of this run

**Nothing here is a measured eval delta.** `NEON_RO_URL` and `GROQ_API_KEY` are
both absent on this host, checked in this run rather than quoted from the last.
No claim row was read, neither eval arm ran, no `status` moved, and every skill
in the library remains **unmeasured**, in that word. The one with-and-without
measurement this library owns still has the wrong sign.

**The trigger suite is not the measurement.** 74 of 84 says the library is
findable. It says nothing about whether any skill helps anybody, and reporting
it as the measurement is the error ADR-38 exists to prevent.

**No papers were read, so the reading queue gains nothing.** This was a
mechanical maintenance run plus a defect repair. Padding the queue to satisfy a
charter step would be the launder the charter forbids.

**`tools/skill_gate.py` prints `verdict: failed` on this diff, and that is the
gate declining to govern rather than a finding.** `applies()` returns `False`
for the 27 files here, and the function's own docstring says an ordinary pull
request that touches a skill alongside code "is not" a candidate for the
automatic path, because "a red label on every engineer PR that edits a skill is
how a label stops being read." Verified by calling `applies()` on this diff's
real file list.

**`--smoke` is not `--live`.** With no database the four ADR-37 staleness
triggers cannot be computed, so `tools/skill_triggers.py --smoke` is what runs,
and its four findings about `skills/harness-engineering` are fixtures rendered
through the live renderer. They are not maintenance triggers and are not treated
as any. The hazard that they could be mistaken for some is filed.
