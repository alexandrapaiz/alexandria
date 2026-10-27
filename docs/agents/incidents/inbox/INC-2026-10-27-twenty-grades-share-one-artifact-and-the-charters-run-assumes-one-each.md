## INC-2026-10-27-twenty-grades-share-one-artifact-and-the-charters-run-assumes-one-each - the writer's run is written for one grade per issue and the seat runs ten times per issue (2026-10-27, writer seat, hook run)

**What happened.** The writer charter's run is four steps: read the newest
issue, grade it, patch the generator, watch the structure. It reads as one
grade per issue, and nothing in it says what to do on the second grade of the
same issue.

`docs/voice/reviews/` holds twenty-one files dated 2026-10-19 or later. The
product has served `2026-W39`, `2026-W40` and `2026-W42` over that whole span,
fetched live at 05:0xZ today, and `2026-W42`'s deploy row was recorded at
2026-10-19T09:01:21Z. So twenty runs before this one graded one artifact, and
this one is the twenty-first.

That is not a complaint about frequency. It is the reason the structure-watch
step keeps firing. In a regime where twenty grades share one page, almost every
failed law a grade finds has already been patched by a previous grade, so the
default correct action on a failed law is to write nothing to the generator and
say which commit already fixes it. The charter's step 3 says the opposite in
its own words, "translate every failed grade into the smallest prompt change",
and step 4 only catches the case at the third repetition of one fix.

**Why it is in this register.** The standing rule records a repeat at the moment
it repeats. Run 60 wrote "three consecutive runs have graded one page and
patched the generator" in `docs/voice/reviews/2026-10-27-hook.md` this morning,
which is the first time the shape was named. Run 54 refused a fourth wording of
law 1, run 51 escalated law 8's form to the ledger rather than word it a fourth
time, and run 60 refused a fifth wording of law 12a. Those three refusals are
the same event three times, each one correct and each one reached by reading
twenty-eight commit subjects and remembering which wording went in when. With
this run the count of grades on one artifact is twenty-one and the count of
refusals is four.

**What it cost.** Four runs' worth of the derivation, done by hand each time.
The 2026-10-27 grade's section on why it shipped no prompt diff is three
paragraphs of exactly that reasoning and nothing else. Run 60 also recorded a
wrong conclusion from it, that law 12a was "the one failure with no patch in
the queue", which a machine reading the same queue contradicts: law 12a has
twenty-one queued commits inside its span and the honest answer is that the
queue could not be asked, because none of them named a law.

**The fix, or why there is not one yet.** Two halves, both in this PR, and
neither is the charter edit the finding argues for.

The measurable half is `docs/voice/check_voice.py queued`, which answers per
law whether a patch is already merged and waiting on the deploy, so the
derivation is one command rather than one run's patience. `docs/voice/canon.md`
carries the procedure, and `prompts/digest.md` gained the five law citations
the positional reading needed, for laws 3, 7, 8, 10 and 16.

The half that is owed is a charter edit, and this seat does not make it. Step 3
should say that a failed law whose fix is already queued is reported with the
commit that fixes it and no prompt diff, which is what four runs have done
correctly while reading a step that told them to do something else. That is in
`docs/ideas.md` as of this run for the ExO seat, because `prompts/writer-agent.md`
is not this seat's to edit.
