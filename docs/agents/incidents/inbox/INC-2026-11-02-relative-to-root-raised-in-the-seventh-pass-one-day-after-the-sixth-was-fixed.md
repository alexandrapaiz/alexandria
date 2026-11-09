## INC-2026-11-02-relative-to-root-raised-in-the-seventh-pass-one-day-after-the-sixth-was-fixed (2026-11-02, writer seat, run 63)

**Repeat of `INC-2026-11-01-relative-to-root-raised-on-a-served-edition-again`,
filed one day later under the standing rule.** That entry's fix added
`shown_path()` to `docs/voice/check_voice.py`, and its docstring states the
remaining exposure in its own words: "The idiom this replaces is inlined in
six passes."

This run made `claims` take a path, aimed it at the pre-rewrite `value.md`
dumped into a `mktemp -d` directory to prove the gate catches the page it was
replacing, and got `ValueError: '/tmp/.../value-before.md' is not in the
subpath of '/tmp/epito-alexandria-writer-eEIPYF'` from
`path.relative_to(ROOT)` at the line that reports a finding.

**The ordering is the same ordering yesterday's entry named as the defect
worth naming.** The pass printed its scope line, its row counts and its
sentence counts without complaint, and crashed only once it had something to
say about a row. A run that aimed it at an out-of-tree artifact and found
nothing would have seen a clean pass.

**Fixed here** by using `shown_path()` at that line and in the new scope line.
Five inlined copies remain in `measure`, `links` and three other passes, per
the helper's docstring, and they are not touched by this run because none of
them was aimed out of tree by it. The general lesson is already law as L-A70,
"the tool you ran is the copy you reached: resolve the path". The narrow one is
that a helper written to replace an idiom does not replace it, and the entry
that ships the helper should carry the list of call sites it did not convert
as work rather than as a docstring note.
