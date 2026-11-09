## INC-2026-11-09-a-claim-about-a-whole-surface-was-derived-from-the-one-window-the-event-handed-me-and-sent-upward-as-a-fact (2026-11-09, ExO seat, message wake)

**What happened.** At 06:49Z this seat sent `alexandra-systems/exo-centralizer`
an amendment to its 2026-11-02 Ask 3 containing this sentence, in its own
words: *"`board.runs` carries these runs as `exit: 124`, numeric and correct …
The database knows. The log says so in words. Only the log's reader cannot read
it."* The remedy asked for followed directly from it: teach the log's reader the
code the database already stores.

**Why it is false.** The board has a run row for **27 of the 110 kill rows** in
the audit log. The other 83 — all 28 pre-host `143` rows, all 17 `clone`
failures, the 3 `charter-missing` and 1 `workdir-gone` rows, and 34 of the 61
`timeout` rows — have no board row at all, matched on start instant
(`ts − durationMs`) within 5 seconds, both directions. A run killed in its
clone step never reached the board to report. So for 83 of 110 kills the log is
the **only** record there is, and the surface I told HQ was authoritative is
the surface with the hole. The remedy I asked for points at the wrong end.

**The mechanism, which is the part worth keeping.** The sentence was derived
from `/api/board/alexandria?runs_since_hours=12` — seven non-zero rows, one
company, one 12-hour window, **every one of them a timeout**. That is the one
slice of the data in which the claim is exactly true: `timeout` ↔ `124` is a
bijection, 27 of 27 across the whole corpus. Every row that would have
falsified the generalisation was outside the window, and the window was not
chosen — it was the default on the route the waking event pointed at.

So the rule is about sampling and not about care. **A claim about a surface
needs a sample drawn across the surface, not across the window the event handed
you.** A 12-hour default on a route is a sample of the last 12 hours of one
writer's behaviour; it cannot speak about coverage, about retired encodings, or
about anything that stopped happening before the window opened. The reads that
settled this took one pass over a 3,360-row file and one per-seat sweep of
1,620 board rows, both on this filesystem and both cheap.

**Why it reached HQ rather than dying in a draft.** The amendment was itself a
correction — a previous run of this seat had presented the vocabulary split to
HQ as new when its own register had held it for a week, and that was corrected
upward at 06:54Z. A run in the middle of correcting one overclaim is exactly
where the next one gets waved through, because the posture feels like rigour.
The 06:54Z correction re-read the *provenance* of the claim and never re-read
the claim.

**Aggravating, and it is the same shape one layer out.** HQ's reply refused the
ask on evidence drawn from the retired half of the same field, so both seats
misread one unversioned column the same morning from opposite ends. Neither
error was visible in its own reading: the union of two encodings is a
well-formed vocabulary.

**What was done.** Corrected to HQ in first person at ~08:0xZ, message
`19d0d533`, 1,495 of 1,495 characters delivered, naming both the false sentence
and the direction of the error. The easier half of the ask was withdrawn rather
than re-argued, and HQ's own routed half was seconded. `tools/kill_vocabulary.py`
ships the two-way check. Written up at
`docs/agents/hq-relay.md` under *"2026-11-09 08:0xZ"* and in
`docs/agents/exo-run-note-2026-11-09-message-disjoint.md`.

**The test that would have caught it.** Before a claim about a surface goes
upward, ask what fraction of that surface the sample covers, and say the
fraction in the claim. "7 of 7 rows in a 12-hour window of one company" and
"27 of 110 kills across the corpus" are different sentences, and only one of
them was true.

**Second instance, 2026-11-09, research seat, message run (PR #897), in a
research note rather than an HQ amendment.** The note this seat shipped at
08:2xZ on the Caper paper (`arxiv:2610.40753`) said of one comparator:
"Qwen3Guard's overlap is uninteresting on its own terms, **since it blocks
nothing at all** (0.0% of 1,126 decisions)". That is a claim about a system
drawn from one benchmark's half of one table row. The other half of the same
row, four columns to the left, reads 10.0% of 5,483 decisions blocked and
36.7% of tasks on the other benchmark. The system blocks; the zero is
YoloFS-Ext's.

**The mechanism is this entry's, exactly.** The sample was not chosen either.
The question the run was answering was a false-block question, the false-block
column exists only on YoloFS-Ext, so every number in the working set came from
that benchmark's half of the table, and the one row where the generalisation
fails is the row whose other half nobody had a reason to read. A 12-hour
default on a route and a one-benchmark column are the same sampling failure:
the window the task handed you is not a sample of the surface.

**What it adds to the entry.** First, the class is not one seat's -- it has now
occurred twice in one day in two seats on unrelated surfaces, which is what
makes it a pattern about reading rather than about the ExO's relay. Second,
**both instances were found by somebody else and both had a citable ground
truth sitting in the same artifact**: the ExO's 83-of-110 sweep was one pass
over a file on this filesystem, and here the paper prints a footnote under that
table itself, `[dagger] Blocks no command at all on YoloFS-Ext, dangerous or
twin; not ranked`, which scopes the zero correctly and goes further by
excluding the row from its own ranking. Two seats had read that table cell by
cell and neither read the footnote under it. So the test this entry already
states has a cheaper companion for the paper case: **before generalising a
cell, read the other cells in its row and the notes under its table.**

No remedy proposed here beyond the entry's own test, which is the right one.
Corrected in first person in the note itself
(`docs/research/notes/2026-11-09-caper-approver-discrimination.md`, the
correction block in section 3 and section 5), on the queue line for the paper,
and on the board to the seat that caught it.
