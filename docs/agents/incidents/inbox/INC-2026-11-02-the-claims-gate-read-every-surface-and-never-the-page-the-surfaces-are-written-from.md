## INC-2026-11-02-the-claims-gate-read-every-surface-and-never-the-page-the-surfaces-are-written-from - fourth instance of the register-width class, and the first where the blind spot is upstream of the surfaces (2026-11-02, writer seat, run 63)

**The class is `INC-2026-11-01-a-register-is-only-as-wide-as-the-commands-that-reconfirm-it`**, stated in its general form yesterday after three
instances in nine days. This is the fourth, found the same way the other
three were, which is a seat happening to run a command against something
outside the union.

**What happened.** `docs/voice/value.md` is the page the writer charter calls
the target every line of site copy converges on, and the copy pipeline makes
it phase 0 of the whole process. Six of the sentences in it are claims the
quality-claims register marks `contradicted`, `queued`, `not built` or
"reports, does not replace". Its core sentence said the library keeps itself
correct and that a builder "does not go back and check whether what they
learned in January still holds, because that work is already done and
recorded". The register's verdict on the mechanism under that sentence is
"reports, does not replace": the weekly issue computes a deprecated section
and tells the reader, and nothing changes the finding in the corpus.

`check_voice.py claims` is the command the writer charter's step 1b hands this
seat for exactly this duty. Its `SURFACE_GLOBS` are `site/app/**`, `site/lib`,
`site/emails` and two `pipeline/` modules. The page was read by no pass of it,
ever, and the gate printed `reader-facing surfaces read 61` over it on every
run since it was written on 2026-10-18.

**Why this instance is worse than the three before it, and it is not the
count.** The first three instances were a live surface the union of commands
did not happen to cover. Here the artifact is not a surface at all. It is the
specification the surfaces are drafted from, so a claim with no machine under
it does not reach a reader through an unchecked page. It reaches them through
a *checked* page that was written to hit an unchecked target, and the gate
reports clean on the page because the claim arrived in the writer's own words
rather than the register's. The charter's own history says the shape outright:
ADR-36's sentence was untrue in public for eleven days with the writer's
approval and the frontend's correct setting, because no gate checked a claim
against a mechanism. This is that, moved one step upstream, where the gate now
exists and is pointed past it.

**L-A21's test, run concretely.** Name one change that would break what this
gate governs: a line in `value.md` promising that overturned findings are
pruned from the library. Would the gate have *seen* it? No. The round would
draft a candidate that hits the target, the artifact-side gate would score the
candidate against taste and voice and pass it, and the claim would reach a
reader as approved copy.

**Fixed in this pull request, on the half that is this seat's.**
`TARGET_GLOBS` adds `docs/voice/value.md` to the default scan, so the target
is now held against the register's own wording on every run of `all`. `claims`
takes a path, so a round can aim it at the candidate it is drafting, which is
the step-1b command that did not exist. The page itself was rewritten and now
carries a section naming each row that bears on it with its state and the
hedge it requires. Baseline checked rather than assumed: the gate reported 24
unhedged or unnamed over 61 surfaces before the change and 24 over 62 after,
so the target was added and nothing was reddened.

**What is not fixed, and it is the convention rather than the scope.** The
other ten copy-candidate files under `docs/voice/` are still outside the scan
and are deliberately left there. They quote the specimens she rejected and the
law that rejects them, which is the construction L-A23 names, and a
per-sentence hedge test cannot tell a candidate from the rejection printed
beside it as a warning. Reading them needs a convention marking which lines
are the candidate. No such convention exists, and inventing one in this run
would redden ten existing files over prose nobody can fix. Filed in
`docs/ideas.md` with the proposal.

**And one honest limit on the fix.** Aimed at the pre-rewrite page, the
widened gate catches one line of it and not the six. The claims in it were
paraphrases, and the matcher needs 60% of a row's content words with at least
three of them in common, so "New work lands in the library every day" against
the row "the library grows every day" shares two words and passes. The six
were found by reading the page against the register, which is the judgment the
command's own docstring already says it does not have. What the gate now
guarantees is that the target cannot carry the register's own wording
unhedged, and the reading is still owed every round.
