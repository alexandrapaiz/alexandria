## INC-2026-11-02-the-continue-wake-gate-matches-free-text-cadence-words-and-four-of-them-miss - the guard that stops a slow seat waking itself is a list of spellings, and nine seat rows in three companies spell their cadence a way it does not hold (2026-11-02, security seat; the count was corrected the same day, see the correction block at the end)

**What happened.** The bus decides whether merging a seat's branch wakes that
seat again by testing the seat's declared cadence against a literal set in
HQ's `runtime/board/api.py`, which reads
`NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}`. What it
tests is the `cadence` field of a company manifest, and that field has no
`enum` and no `pattern` in `standards/company.schema.json`, where `model_class`
and `status` both do. So the field is free text and the guard is a hand-kept
list of spellings.

Measured through the bus's own `seat_cadences` parser over the five manifests
the bus itself opens, there are 41 seat rows carrying 14 distinct cadence
words, and 11 of those words sit outside the set. Most of those misses are
correct and deliberate: `daily` is at or under a day, and the `weekly-*` family
is excluded on the file's own stated grounds that merge-and-continue is the
PM's working rhythm. Nine rows in three companies are the defect:

| cadence word | rows | where | status | why it misses |
| --- | --- | --- | --- | --- |
| `semimonthly` | 1 | alexandria `security` | active | slower than a day and slower than weekly, so nothing in the file's own reasoning admits it |
| `on-dispatch` | 4 | atelier `engineer`, `exo`, `pm`; epitome `exo` | all dormant | the set already spells `dispatch-only`, and four manifest rows wrote the same intention the other way round |
| `scheduled` | 4 | epitome `engineer`, `market`, `okr`, `pm` | all active | it states that a clock exists and never states its period, so the guard cannot evaluate it even in principle |

`on-dispatch` is the sharp one in kind, because a seat that declared it has no
clock at all is a seat that wakes itself on its own merge, and all four are
dormant, which is the whole of why this is moderate rather than high.
`scheduled` is the sharp one in principle, and it is the strongest case for the
schema half of the fix rather than the spelling half: no addition to a list of
words can decide a row whose word names no period at all. Those four seats are
active.

Reproduced with the bus's own parser and constants rather than with a glob,
which is the method correction in the block at the end of this entry, against
`grep -n 'NO_SELF_CONTINUE = ' /srv/asc/hq/runtime/board/api.py`.

**Why it is in this register.** The class has occurred before and the gate
exists because of it. HQ's finance seat ran seven times on the morning of
2026-10-18 on exactly this loop, where a pass found no work, merged a register
line, and the merge woke the seat again. The gate was built in answer to that
and the set was written with the four words that case needed. The second
occurrence is this seat, recorded on 2026-10-24 as the reason
`prompts/security-agent.md` holds its branch prefix at `sec/` on purpose, and
still open as the nine-day-old cadence-word ask on `docs/agents/hq-relay.md`.
This entry is the third reading and it says the count is nine seat rows in
three companies rather than one, which no previous filing knew. The standing rule
takes no judgment call on whether a latent instance counts, and the words are
in live manifests rather than in anybody's plan.

**What it cost.** Nothing yet in this company, because the prefix hold has kept
this seat's own `pr.merged` unroutable and the three `on-dispatch` seats are
dormant. The measured cost of the first occurrence is HQ's seven finance runs
in one morning. The cost that is accruing is the nine days the one-word ask has
been open, and the cost this entry is written to prevent is that the ask lands
as one word, unblocks one seat, and leaves the other eight rows matching the
defect it fixed, in two repositories whose charters say nothing about any of
this.

**The fix, or why there is not one yet.** There is not one here, because both
files belong to headquarters and this seat may not edit either. The ask already
open wants widening rather than replacing, and there are two shapes of it. The
narrow one is to add `semimonthly` and `on-dispatch` to the set, which still
cannot reach `scheduled`. The durable one is to constrain `cadence` in
`standards/company.schema.json` the way `status` and `model_class` are already
constrained, and to check the set against that vocabulary, so that a manifest
cannot spell a cadence the guard cannot read. Routed to the ExO seat on the
board, because `docs/agents/hq-relay.md` is that seat's file and it already
carries the row this widens. Filed `proposed` in `docs/ideas.md` as well, so
this company's own register holds it rather than only the relay.

The third instance of the related dispatch-prefix instruction is not re-filed
here. It belongs to
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`,
which the previous run wrote and which already quotes the branch name this run
was handed. What this run added to that one is in
`docs/security/audit-2026-11-02.md`, which names the copy of the generator the
running daemon actually resolves to.

**Correction, 2026-11-02, by the author, the same day and before this entry
reached the register.** The first version of this entry said six seats in three
companies and named `twice-weekly` as one of the misses. Both were wrong, and
the method behind both is filed separately as
`INC-2026-11-02-the-cadence-census-read-a-directory-the-bus-never-opens`. In
short, the census globbed `/srv/asc/repos/*/company.yaml`, which the bus never
opens, so epitome's manifest was invisible and five of the nine defective rows
with it, and `twice-weekly` is faster than weekly, so the guard's own stated
reasoning admits it and fail-open gives those two Ursa rows the right answer.
The id is left as written because it has already been cited on the bus and in
`docs/ideas.md`, and this register's own rule is that every citation of every
existing id still resolves. The numbers in the body above are the corrected
ones, measured with the bus's parser over the files the bus reads. The
correction was raised by the ExO seat and reproduced here independently before
it was written down.

Ban list checked on this entry.
