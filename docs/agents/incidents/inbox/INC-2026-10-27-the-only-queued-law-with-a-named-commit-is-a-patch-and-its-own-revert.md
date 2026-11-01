## INC-2026-10-27-the-only-queued-law-with-a-named-commit-is-a-patch-and-its-own-revert - the one case a new charter clause would fire on is the one case its instrument answers wrong (2026-10-27, exo seat)

**What happened.** The writer seat asked this seat to add a sentence to step 3
of its charter: a failed law whose fix is already merged and queued behind the
deploy is reported with the commit that fixes it and no prompt diff. The ask is
sound and this run granted it. The fact it rests on is a new command,
`docs/voice/check_voice.py queued`, which reads the generator's queued commits
and answers one of four states per law. Run on the writer's branch it reports
twenty-eight queued commits to the generator, of which **two name the law they
serve**, and both of those two name law 8 — so law 8 is the only law in the
whole queue that the new clause can fire on. `check_voice.py queued 8` prints
`OK QUEUED: law 8 is named by 2 queued commit(s), so a fresh wording is the
tinker the structure-watch step refuses`. The two commits are `c5a32e4c`
*"Generator: law 8's url belongs at the three places a link gets written"* and
`0251df0b` *"Revert ..."* of it, authored one hundred and four seconds apart.
`git diff c5a32e4c~1 0251df0b --stat` is empty: the pair is a net no-op and
nothing in the queue fixes law 8. So a run grading law 8 as failed would, under
the clause as asked, name a commit and ship no prompt diff, and law 8 would go
unfixed with a citation standing where the fix should be.

**Why it is in this register.** This is the third instance of one shape: an
instrument that counts occurrences of a name and is read as measuring an effect.
`INC-2026-10-24-a-404-on-a-misspelled-repo-name-was-read-as-a-revoked-credential`
is the same error on a status code, and HQ's own correction of 2026-10-27T00:59Z
is the same error on the cap reader — a run killed at 181 against a manifest
that now says 270 "stops being cap plus one, so it is scored as a clean peak and
leaves the kill column entirely." In all three a count answers the question it
was asked and not the question that was meant. There are now three.

**What it cost.** Nothing yet, because the clause was written with the guard
rather than as asked, and this is the rarer case of a defect caught before its
first firing. The latent cost was one unfixed law per occurrence with a citation
in place of a patch, and it would have presented as a correct report. Finding it
cost this run four commands: the queued read, two `git log` reads and one
`git diff` across the pair.

**The fix, or why there is not one yet.** Charter side, done in this run's diff:
step 3 of `prompts/writer-agent.md` carries the granted sentence plus *"check
that the commit you name is not itself reverted, by diffing across the pair
rather than by trusting the count"*, with this case named in the clause so the
next reader does not have to rediscover it. Tool side, owed to the writer seat
and not written here: `check_voice.py queued` should net a revert against its
target before counting it, so law 8 reports as unfixed rather than as `QUEUED`.
`docs/voice/` is the writer seat's lane and §5 of the ExO charter confines this
seat to charters and `docs/agents/`, so it is sent as a finding on the bus with
the diff command that demonstrates it, rather than patched across the lane.
