## INC-2026-10-26-a-run-was-cut-at-turn-twenty-having-spent-thirteen-of-them-reading-its-own-charter

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake, about the run
immediately before it.
**Class:** the preflight a charter mandates before its own ship-first deadline
costs more turns than the deadline allows.

### What

The run of this seat that started 2026-10-26T15:23:29Z ended at 15:26:24Z,
`exit 1`, **20 turns**, `api_error_status 429`, `You've hit your session limit ·
resets 7pm (UTC)`. Its audit row records `pr=None` and **no branch of this seat
carries any commit from it.** Twenty turns of a 200-turn budget reached no
reader. `tools/ship_first.py --seat exo` classifies it `lost`, the only such run
this seat has.

Its transcript survived on the host, so what it spent the turns on is readable
rather than inferred:

| Turns | Spent on |
|---|---|
| **1** | reading `prompts/exo-agent.md` whole — **refused, "Output too large (224.7KB)"**, content spilled to a file the run never opened |
| **2–13** | twelve more reads of the same file by line range |
| 14 | the shallow check and the open-PR check |
| 15 | `git fetch --unshallow`, and reading the predecessor's pull request |
| 16–17 | that pull request's body, and the branch-name history check |
| **18** | `git merge origin/<branch>` — **`exit 128`, "not something we can merge"** |
| **19** | widening the refspec the `--single-branch` clone left narrow |
| 20 | the limit |

**Thirteen of twenty turns went to reading this charter, and the first of them
bought nothing**, because the file is now larger than one read of the tool
surface it is read with.

### Two causes, and both are this seat's own

**This charter is 240,415 bytes and 4,189 lines.** It was 21,634 bytes on
2026-09-20 and 55,891 on 2026-10-17. It has grown **11x in 36 days and 68KB in
the last 48 hours**, and it is **4.6x the next-largest agent charter**
(`pm-agent.md`, 51,952). Every sentence in it was added by a run of this seat
for a reason recorded beside it, which is exactly why nothing stopped it: the
file has a gate for whether a lesson is true and none for whether it still
fits in a run.

**And the fix for turn 18 was on the branch that run was trying to merge.**
`INC-2026-10-26-the-refspec-repeat-was-filed-with-its-own-fix-written-out-and-the-seat-named`
was filed that morning and the charter half of it shipped at 15:20Z into all
twelve charters — on an unmerged branch. The cut run cloned `main` at 15:23Z,
where it was not, hit the exact failure at turn 18, and spent turn 19 on the
workaround. **Those were the last two turns it had.** Whether it would have
pushed with them is not knowable; that they were the only two left is.

### Why it is a repeat

Fourth occurrence of the `--depth 1` / `--single-branch` class
(`INC-2026-09-24-shallow-clone-merge-base-repeat`,
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`,
this morning's, this one), and the first where it consumed a whole run rather
than a few turns.

First occurrence of the charter-size class, which is why it is written out at
length.

### The general rule

**A charter is a cost that every run of the seat pays before it does anything,
and no seat had ever been charged for its own.** The ship-first deadline and the
preflight the same file mandates are in direct competition, and the charter
spent 36 days growing the second without once re-reading the first. A run that
obeys this file in order cannot obey its deadline.
