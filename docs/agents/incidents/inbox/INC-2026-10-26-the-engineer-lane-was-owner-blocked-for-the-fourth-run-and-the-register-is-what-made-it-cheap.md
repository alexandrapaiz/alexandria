## INC-2026-10-26-the-engineer-lane-was-owner-blocked-for-the-fourth-run-and-the-register-is-what-made-it-cheap — the repeat, and the one line of evidence that the remedy is still owed (2026-10-26, engineer seat, message wake)

**One line, because the finding is already written.** This seat was woken with
"continue with the next item in your lane on the board" for the fourth time.
All four `This sprint` engineer cards are still owner-blocked, with the same
four hands named in
`INC-2026-10-25-the-engineer-lane-was-rediscovered-as-owner-blocked-for-the-second-run-running`,
and none of the four cards carries any sign that three runs have each stood in
front of it. The standing rule at the top of this file is why this is recorded
at all: the instance count is now four and that entry says two.

**What is different, and it is the reason this is worth four lines rather than
forty.** The rediscovery was cheap this time. This run read the incident
register before it read the card bodies, so establishing the block cost one
board fetch and one read of a filed entry rather than the several turns the
runs of 2026-10-24 and 2026-10-25 each spent. That is the register working as
designed, and it is also the measurement that says the remedy is still owed:
the register made the *rediscovery* cheap, where the remedy that entry asks for
would have made the rediscovery unnecessary. The remedy is a note on the card
itself, because the card is the thing a run told to go to the board actually
reads. It has now been owed for two days and across two more instances.

**Met again in the same run, already filed, so this is the repeat line and
nothing more.**
`INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`.
`git fetch --unshallow` succeeded and `git fetch origin <branch>` succeeded,
and `git show origin/<branch>:<path>` then answered
`fatal: invalid object name`, because this clone's refspec is still
single-branch so no remote-tracking ref is written for any branch but `main`.
The working form is `FETCH_HEAD`, which is what this run used to read the
unmerged sprint plan off the PM's branch. Ban list checked on this entry.
