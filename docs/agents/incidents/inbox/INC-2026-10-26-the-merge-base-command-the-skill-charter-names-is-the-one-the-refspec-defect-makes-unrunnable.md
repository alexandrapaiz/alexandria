## INC-2026-10-26-the-merge-base-command-the-skill-charter-names-is-the-one-the-refspec-defect-makes-unrunnable - third occurrence of the single-branch refspec, first in a seat whose charter names the command that cannot run (2026-10-26, skill seat, message run)

**What happened.** This run ran the skill charter's shallow-clone remedy at
turn three, before any comparison, exactly as the charter writes it:

    git rev-parse --is-shallow-repository    # printed true
    git fetch --unshallow                    # succeeded

The charter then says, in its own words, "two commands, always, before any
merge, `git merge-base`, `A...B` diff, or staleness check". The next command
this run needed was the first of the three it names, and it could not run:

    $ git merge-base origin/main origin/alexandria-skill/2026-10-24-message
    fatal: Not a valid object name origin/alexandria-skill/2026-10-24-message
    $ echo $?
    128
    $ git config --get-all remote.origin.fetch
    +refs/heads/main:refs/remotes/origin/main

The repair in the engineer seat's filing cleared it in one turn and the branch
count moved from 2 to 127.

**Why it is in this register.** The standing rule, and this is the third
occurrence of
`INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`,
whose own body already carries a second from the engineer seat the same day.
It is a separate file rather than an append to that one because the inbox is
one file per incident and one author, and appending to another seat's inbox
entry rebuilds the shared anchor the inbox was built to remove.

What is new, and the reason this is worth a file at all, is which command
failed. The first two occurrences surfaced as a failed `git push` and as a
branch count, and both filings called the quiet version luck rather than
design. This one landed on `git merge-base`, which is the first command the
skill charter names after the remedy it carries, so the charter's own remedy
and the charter's own next instruction disagree inside eight lines of each
other. The engineer charter was the one the earlier filing proposed to fix. The
skill charter carries the same two commands, the same "two commands, always"
sentence, and the same gap, and nothing swept the other eleven charters for
it when the first filing landed.

**What it cost.** One turn, and nothing beyond that, because `git merge-base`
fails loudly. The same state reached through the charter's containment proof,
`git log --oneline origin/<the-older-branch> ^HEAD`, prints nothing to stdout
and exits 128, which satisfies that instruction's literal text of "must print
nothing". This run had no predecessor branch to contain, so the silent path was
not reached a third time. That is still luck.

**The fix, or why there is not one yet.** No new ledger entry, because the
engineer seat's filing already names the exact repair, which is a third command
beside the two:

    git config --replace-all remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' \
      && git fetch origin

What this entry adds is the count and one scope correction: the fix belongs in
every charter that carries the two-command clause, not only
`prompts/engineer-agent.md`, and `prompts/skill-agent.md` is the second
confirmed instance. A charter is this seat's own authority, so it is not edited
here under `docs/standards/pm.md` section 21 and the charter's own boundary section.
