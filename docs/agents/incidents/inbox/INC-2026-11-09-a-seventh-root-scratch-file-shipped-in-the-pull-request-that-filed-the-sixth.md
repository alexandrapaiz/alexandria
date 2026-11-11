## INC-2026-11-09-a-seventh-root-scratch-file-shipped-in-the-pull-request-that-filed-the-sixth - the pull request that documented the sixth root-scratch leak ships a seventh (2026-11-09, pm seat)

**What happened.** PR #809 (security, branch `sec/2026-11-08-message`, fifteenth
in the chain from #794) adds
`docs/agents/incidents/inbox/INC-2026-11-02-the-sixth-root-scratch-reached-a-pushed-public-branch-and-the-staging-command-is-the-surface-the-five-before-it-did-not-name.md`,
which records a `.board.json` dump landing at the checkout root via `git add
-A` and reaching a public branch. The same pull request's own diff also adds
`.board.json` at the checkout root, a single-line, 228-KB-class JSON dump of
board state (sprint `sprint-2026-10-05`, dated 2026-09-21 to 2026-09-27, long
superseded) with no entry in `.gitignore` and no reference anywhere in
`tools/`. Confirmed with `git show main:.board.json` (does not exist on
`main`) and `grep -rn '\.board\.json' tools/ *.py` (zero references outside
the file itself and the incident prose describing the earlier instance).
Found by reading the PR's full diff rather than trusting its body, which
states only "no severe finding" and does not mention this file.

**Why it is in this register.** The standing rule records any issue that
occurs more than once at the moment it repeats, with no exceptions. This is
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
and the pull request open right now is the **seventh** instance by this
class's own count, landing in the same pull request that filed the sixth.
The earlier instance's own finding was that an ignore list cannot stop the
next name and that `git add -A` is the surface; `git add -A` or an
equivalent broad stage is the only way `.board.json` reaches a diff whose
author never referenced the file in code or prose.

**What it cost.** Nothing shipped to `main` yet: found during PM review
before merge, so the file has not reached the mainline. It did reach a
pushed, public branch (#809), same as the sixth instance.

**The fix, or why there is not one yet.** Not this seat's commit to make.
PM is holding #809 rather than merging it and handing it back to the security
seat (board message plus a PR comment) to drop `.board.json` from the branch
and re-ship. The broader remedy, an explicit `git add <paths>` habit instead
of `git add -A`, was already proposed by the sixth instance and is unchanged
by this one; this entry is evidence that the proposed remedy has not yet been
adopted by the seat it would protect.
