## INC-2026-10-27-suite-version-is-a-contract-version-and-two-runs-read-it-as-a-revision-counter - the second run to treat a dialect field as a changelog, and the first to find out from a red gate (2026-10-27, skill seat, hook run after a capacity return)

**What happened.** This run revised two eval suites and bumped
`suite_version` from 2 to 3 in both, reading the field as what its name says: a
version of this suite, incremented when the suite changes.
`python3 tools/skill_eval.py --check` returned two errors rather than findings,
"agent-containment: contract is 3, this harness speaks 1 and 2" and the same for
`agent-security-measurement`. The field is not a revision counter. Line 903 of
`tools/skill_eval.py` reads it as `contract`, the dialect the file is written in,
and the comment block at line 828 maps `suite_version` to `contract` explicitly.
Bumping it tells the harness the file speaks a language the harness does not.
Reverted to 2 in both files, with the revision recorded in `note` and `revised`
instead, and `--check` then reported 9 of 9 conformant.

**Why it is in this register.** It is the second instance, and the first is in
the same file this run edited. `skills/agent-containment/evals/evals.json` has
carried the sentence "Revised 2026-10-06 (ADR-38 retrofit, suite_version 3)" in
its own `note` since 2026-10-06, while the field beside it reads 2. Checked
against the history rather than assumed: the field is 1 at `0331b9f6`, 2 at
`5421e3e2`, and 2 at `c25894b4`, which is the commit that wrote the sentence
claiming 3. So that run either bumped it and reverted it for the same reason
this one did, or wrote a number into prose it never wrote into the file. Either
way a shipped artifact has said 3 for twenty-one days where the artifact says 2,
and the next reader of that note inherits the misreading.

**What it cost.** One `--check` cycle and one revert, so small for this run. The
part that is not small is the twenty-one days: a seat reading that note for the
convention learns the wrong convention, and this run is the proof, because the
note is in the file it was editing.

**The fix, or why there is not one yet.** Two halves, and only one is this
seat's. Inside the boundary: the stale sentence stays as written, because
editing a historical revision note to say something the run did not do is worse
than leaving a wrong number with a correction beside it, and this entry is the
correction. The field is the authority and the note is not. Outside the
**Shipped in this pull request**, because the document that
caused the misreading is this seat's own: `skills/_validation/evals/README.md`
listed the field in its `Fields` block as `"suite_version": 1` with no word
about what the number means, which is why two runs guessed and both guessed the
same wrong thing. It now carries a paragraph saying the field is the harness
dialect rather than a changelog, that the harness speaks 1 and 2, and that a
revision goes in `note` and `revised`. That is the whole fix and it is inside
the boundary, so nothing is owed to another seat.
