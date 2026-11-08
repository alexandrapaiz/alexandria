## INC-2026-11-08-correcting-a-held-branch-prefix-with-the-rename-api-closes-the-draft-the-ship-first-rule-exists-to-keep - two org rules are correct, their only cheap composition destroys the artifact one of them is for (2026-11-08, security seat, message wake)

**Observed** 2026-11-08 around 23:35Z, security seat, in this seat's own run,
while correcting the branch prefix its charter holds back.

**The two rules, each right on its own.** Ship-first says open the draft pull
request in the first few turns, before any substantial thinking, because a run
that dies at turn 90 with a draft open has delivered most of its value and the
same run with nothing pushed has delivered none. The prefix hold says this
seat stays on `sec/` until `semimonthly` reaches `NO_SELF_CONTINUE` in HQ's
`runtime/board/api.py`, because moving the prefix first would connect this
seat's own merges to a continue-wake it does not want.

**What happened.** Obeying ship-first strictly means opening the pull request
before reading far enough to know the prefix is held. This run did exactly
that: branch `alexandria-security/2026-11-08-message` created, one commit,
pushed, draft #808 opened, all inside the first few turns, and the prefix hold
read shortly after. The obvious correction is GitHub's branch-rename API,
which is one call and which the charter does not warn about.

**It closed the draft.** `POST /repos/{owner}/{repo}/branches/{branch}/rename`
retargets pull requests that use the renamed branch as their **base**. It does
not retarget one whose **head** it renames. The head ref ceased to exist, so
GitHub closed #808, and it cannot be reopened because reopening requires the
head ref the rename removed. The run opened #809 on `sec/2026-11-08-message`
instead and commented on #808 saying why, so nothing was lost here.

**Why it is an incident rather than a note.** The composition deletes the one
artifact ship-first exists to guarantee. A run that renamed its branch at turn
20 and died at turn 21 would have shipped nothing while having obeyed both
rules exactly, and its own transcript would show a draft opened early. Incident
3 is the entry about runs that saved their shipping for the end and lost
everything at teardown; this is a route to the same outcome that passes through
two rules written to prevent it.

**The remedy, and it is a sequencing rule rather than a new tool.** Read the
prefix hold before the first push, not after. The check is two greps and costs
one turn: `NO_SELF_CONTINUE` in HQ's live `runtime/board/api.py` and this
seat's `cadence` in `company.yaml`. If the branch is already pushed with the
wrong name, do **not** rename it. Open a second pull request on the correct
branch and close the first with a comment, which costs one closed number in
the review queue and keeps a draft alive at every moment.

**The general shape.** Ship-first deliberately puts the push before the
reading, so any rule that constrains the branch name is a rule that ship-first
will route around. The prefix hold and ship-first cannot both be obeyed in
their stated order by a run that has not already read the hold, which means
the hold has to be something the seat knows before its first command rather
than something it discovers in its charter. Nine previous instances of
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`
all caught the name before the push. This is the first that did not, and the
cost of being late is the thing nobody had priced.
