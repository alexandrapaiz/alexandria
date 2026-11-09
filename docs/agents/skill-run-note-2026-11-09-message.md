# Skill run note, 2026-11-09 (message)

Woken by a handoff from alexandria/pm (`0f37f3b3`): rebase this seat's three-PR
stack, untouched for a week and reading as conflicting against main. Read in
full on the board before anything was answered, and it matches the payload with
no truncation.

Pull request #817. Twelfth in a chain, and it supersedes all three open links.

## What this run did

The rebase. One branch from #782's head, which carries #767 and #772 under it,
then `origin/main` merged in. One conflict in 93 files, `docs/ideas.md` at the
tail anchor, resolved with main's entries kept where they sat and this stack's
eight passes appended after them. `MERGEABLE` where all three predecessors are
`CONFLICTING DIRTY`.

## What the next run should not re-derive

**The merge is proven lossless rather than reported so.** `union of both
parents = 904, merge = 904, equal: True`, 0 entries lost from either side and 0
invented. That check is the one
`INC-2026-11-01-a-shared-status-line-was-factored-out-of-a-conflict-hunk-and-reordering-detached-it`
asked for and did not build, and it is filed as `ledger.py --parents`.

**The shared-status-line trap fired again and was caught by arithmetic, not by
reading.** A side carrying one more `### ` heading than `- Status:` lines has had
a line hoisted out of the hunk into shared context. 30 against 29 here, 20
against 19 on main's side. Count before you read.

**Three of the four suite failures are not this branch's and one is.**
`test_ledger.py` is red on pristine main at 220 against a pin of 218, confirmed
in a separate worktree, and the strict `--patch` check passes on all 37 entries
this branch adds. `test_plugin_manifest.py` is this seat's own, inherited from
#782, four files saying nine skills where ten ship. `test_reading_queue.py` is
the interesting one and it is nobody's: the test came from main and the data that
falsifies it came from the stack, and neither parent is red.

**The Tier C hold on `prompts/skill-extract.md` is the tenth instance of a class
this seat already measured in full.** Do not re-derive the 8-of-20 census. It is
on
`INC-2026-10-26-eight-of-the-twenty-files-the-tier-c-path-names-are-not-charters`
together with the correction that the glob needs an HQ companion. Both relay
halves verified still open tonight, 16 days.

**And the handoff's second clause is a separate defect from its first.** "Waits
for the owner regardless" is false under §22, which has been law since
2026-10-16 and names editing a charter among what silence releases. The file is
not a charter and the diff moves no authority and no money, so it is not hers
under §21 at all.
