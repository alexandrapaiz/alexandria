### 2026-11-09 - Craft scan: git rerere records a resolution and replays it, where alexandria re-derives one every time (engineer seat)

- Trigger: today's craft scan, chosen because this run spent itself on
  `tools/resolve_register_conflict.py` and the nearest product to that tool is
  a feature of git itself. `git rerere` ("reuse recorded resolution") watches
  every conflict you resolve by hand, stores the pre-image and the resolution,
  and the next time the same conflict appears it replays your answer without
  asking. It is off by default and has been shipping since 2006.
- What is worth stealing: **it keeps the hand resolutions as data.** The ExO
  seat resolved two register conflicts by hand this morning and the only record
  of what it decided is prose in a pull request body, which nothing reads. Under
  rerere's model those two resolutions would be a pair of (pre-image,
  resolution) records, and the third instance would be answered from them rather
  than from a fresh judgment. For this repository the valuable half is not the
  replay, which the resolver now does by rule, but the corpus: a hand resolution
  that the tool refused is evidence about which refusals are worth turning into
  rules, and today there is nowhere to put it. The resolver refuses a file whose
  status column is edited in place, which the ExO seat confirmed is correct, and
  that refusal will be met again by somebody who does not know it was correct
  once.
- What alexandria does better: **rerere replays silently and proves nothing.**
  Its own documentation warns that a recorded resolution can be replayed into a
  context where it is wrong, and it offers no check that the replay preserved
  anything. The resolver's arithmetic is the half rerere lacks: every line of
  both sides present exactly once, plus, from today, the stamps not decreasing.
  A tool that answers and proves its answer is the better trade for a register
  nobody re-reads, and it is why the resolver refuses rather than guesses where
  rerere would have replayed.
- First step: a `--record` mode that writes the three stages and the hand
  resolution into one file under `docs/agents/` when a seat resolves something
  the tool refused. Data first, rules later, and the rules come from reading
  the first five records.
- Cost: $0
- Status: proposed
