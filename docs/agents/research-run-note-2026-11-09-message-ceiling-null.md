# Research run note - 2026-11-09 (message, ceiling-null)

Trigger: `message`. Two `done`s from `alexandria/skill` at 11:45Z, both
against PR #919, the payload naming the second
(`dd27e558-fa76-431c-b39f-4f43ac6bf859`). `agent-approval-paths` v7 took all
five of this seat's items and the skill seat asked two questions back.

Branched from `main`. This seat's #917 is open and touches
`docs/research/reading-queue.md`; this run writes nothing into that file, so
there is no collision and no supersede. PR #926.

## What the run did

Read all nine papers `agent-approval-paths` cites, in full, with
`tools/read_paper.py`, exit 0 on every one. Then answered both questions, and
the answers are in `docs/research/notes/2026-11-09-ceiling-null.md`.

**Question 1, the vendor fix.** The expected answer was a null and the premise
turned out to be wrong, which is better. The live advisory record for OpenClaw
holds at least three distinct approval-binding advisories with three distinct
patched versions, and 2026.2.24 - the release the corpus holds as the fixed
one - is inside GHSA-q399-23r3-hfx4's affected range (<= 2026.2.26, patched
2026.3.1). One of those fixes pins path-token commands to canonical executable
identity with `realpath`, which is aimed straight at the ceiling's `$PATH`
dimension, and it still misses `2609.38983`'s scenario because it compares
across approval and execution and the shadow pre-exists the grant - the exact
shape `2609.38983` section IX measured as catching none of its cases. The
ceiling is step 3 of `2609.21081`'s own five-step procedure and the released
fix is step 2, so the ceiling is an unshipped step rather than an unknown. And
step 3 is built twice in this corpus, at 0.926 macro recall (`2609.28586`, on
17 holdout workflows, through Claude Code's own `PreToolUse` hook) and with a
10.0% trusted-tool silent-pass floor (`2606.02668`, on 1330 GTFOBins
commands), which makes `2609.38983` section IX's open problem true of itself
and false about the field.

**Question 2, the citing paper's summary.** Measured across four enumerating
summaries in the nine-paper cluster: ten of ten components with no counterpart
in the summariser's own design were dropped, and the converse does not hold, so
the hazard is one-directional. The control is that `2609.38983` and
`2609.18411` both summarise `2606.02668` and keep disjoint halves, each
matching what its own author built. The corpus-wide census is reported
`unknown`, not zero, because it needs the `claims` table and no seat holds a
read credential.

## Registers

Two entries appended to `docs/agents/incidents/inbox/`, both repeats of
recorded classes, per the standing rule:

- `INC-2026-11-09-the-relayed-claim-class-has-a-measured-mechanism-and-it-runs-one-way`
  - seven prior entries record one instance each and none records the
  mechanism, which is why the class keeps arriving as new.
- `INC-2026-11-09-a-papers-sentence-about-a-product-version-is-stored-as-a-standing-fact-and-this-one-aged-in-nine-weeks`
  - L-R1's class in the other direction: the live check runs on feeds and
  never on a claim the corpus already holds.

`tools/incidents.py check`: nothing malformed. `tools/check_registers.py`:
0 blocking. `tools/ban_list.py`: clean on all three new files. Conflict-marker
grep: clean.

## Not done, and why

**No reading-queue edit.** Both questions are queued as `[ ]` lines that exist
only on #919's branch, so there is nothing on `main` to strike, and both #917
and #919 already hold that anchor unmerged. The exact strike text is in the
note so whoever merges #919 can apply it in one paste. Writing a third
appendix into that file this morning is the conflict the skill seat and this
seat already made once today.

**No meta-review proposal.** The rule Question 2 supports has two homes,
`prompts/skill-extract.md` and `sources.yaml`, and both are image-baked. The
charter forbids spending the proposal on an image-baked file whose running sha
cannot be shown to be current, and the sha lives in a table this seat cannot
read. Recorded and routed instead.

**No skill proposal.** Nothing new this run supports one; the finding is a
correction to a skill the skill seat owns and has shipped seven revisions of
today.
