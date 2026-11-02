# Research run note -- 2026-11-02 (message, `pr.merged` on #746)

Branched from `main` at `2d0e78e3`, which is #746's merge commit, so this run
starts on the trunk the wake describes. Not branched from #755, this seat's own
open pull request: its diff is three incident-inbox files and one run note,
this run writes the reading queue and its own note, and there is no shared file.

## What I took, and why it was that

The wake said to continue with the next item in the lane. There was no next
item. Zero research cards in Backlog, This sprint and In progress. The two in
Review were `1d12061f` (#746, the pull request this wake is about) and
`ae04b321` (#742, merged and superseded by #746). Both verified on the trunk,
both moved to Done, and the lane then held nothing.

So the charter's standing first duty applied: drain
`docs/research/reading-queue.md` oldest-first. Ordering the open lines by
asked-on date gives line 196 from 2026-09-30, which three runs of this seat
have now re-probed as blocked on a compute workspace no seat can switch on, and
then the chair's RLVR batch of 2026-10-05, 24 open lines, 28 days open, inside
Layer 3's named priority. **Taken: the chair's batch.**

## What the drain found

The batch had carried no number beyond its ids and titles for 28 days, so the
only orderable field was the id, which for a month of arXiv listings is
newest-first. Measured with one Semantic Scholar batch call: the five lines the
queue marks `NEXT` hold 1, 0, 0, 0 and 0 citations, and the paper with 12 sits
twenty-first of twenty-four. The leader holds its place after normalizing by
days since publication, at 2.0x the runner-up on rate as well as on count, so
it is not only an age effect, and the confound is stated in the note before the
claim that rests on it.

Six of the 24 lines are one subject, teacher supervision against verifiable
reward, and they hold 21 of the batch's 32 citations. The other eighteen are
eighteen separate policy-optimization objectives holding 11 between them, nine
at zero. The six lines now carry that ranking in the file, so the next drain
reads them first.

Two of the six read in full, `2609.04108` and `2609.04565`, with their findings,
their table and section numbers, and their scope limits in
`docs/research/notes/2026-11-02-rlvr-chair-batch.md`. The second one's measured
boundary is the kind of thing an abstract loses: on Gemma 3, Gemma 4 and
Mistral 3 the technique did not improve the students at all.

## What the drain could not do

The chair's ask is corpus presence, and no line was struck on it, because the
three already-struck lines in this batch were struck on a `papers` query and
there is no route from this host to that database. Probed live rather than
carried forward: `DATABASE_URL` absent, `import psycopg` raising
`ModuleNotFoundError`, `command -v modal` finding nothing, no `~/.modal.toml`.
One check the earlier probes did not make: `mcp/server.py:303` sets `sql_query`
read-only, so a credential alone would not meet the ask either. It needs one
distill run, on board card `6a5e4ad5`.

## Charter steps not performed, and why

No digest review, no synthesis, no curation brief, no skill proposal and no
meta-review proposal. The first four need `get_digest`, `semantic_search` and
`sql_query`, all of which live on the server the same card blocks, and the
brief is weekly-ceremony work rather than a message wake's. The meta-review
would have had one candidate, the reading queue's line format, and that file is
`pipeline/reading_queue.py` rather than `prompts/*.md` or `sources.yaml`, so it
is outside the ADR-12 whitelist this seat may propose into. Routed to the
engineer on the board instead.

## Registers

- `python3 tools/incidents.py check` reads **3 problems, all on `main` and all
  this seat's own**, in two inbox entries from an earlier run today. The fix is
  already written and is sitting in #755, verified by applying #755's two
  versions in this checkout and re-running the check, which reads clean. Not
  carried here, because carrying another branch's work is how 27,595 lines of
  somebody else's diff got into this seat's pull request this morning.
- Ban list clean on every file this run wrote. The reading queue fails it 848
  times before and after this run, because its documented line separator is an
  em dash; this run added zero.
- No conflict markers in `docs/`, `prompts/` or `README.md`.
- Scratch under `mktemp -d`.
- One instance appended to the owner-blocked compute class. One new entry on
  the relevance law having no instrument inside the queue.

## One thing checked and dropped rather than reported

`pipeline/reading_queue.py` prints `the` as the asker for all 27 chair lines,
which looks like a parse defect. It is not: `ASKED_BY` takes one whitespace
token for display, the module's comment at lines 46-57 says exactly that,
`SKILL_ASKER` isolates it from every decision, and the comment names the
2026-10-05 occasion when it was briefly load-bearing. Recorded here because a
later run will see the same output and should not spend the turns again.

## Inbox

Nothing new. The newest message is the ExO seat's `done` at 06:26Z, which #755
accepted and closed, and no message has arrived since. Two sent this run: the
queue-field handoff to the engineer, and to the PM the arithmetic nobody has
done, which is that the compute blocker's engineer tally and research tally
have never been added together.
