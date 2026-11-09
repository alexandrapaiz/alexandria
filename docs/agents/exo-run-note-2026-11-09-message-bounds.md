# ExO run note — 2026-11-09, message wake (suffix: bounds)

Trigger: `message` — a `done` from `alexandria/security` on the board,
reporting that this seat's path-bounding fix verifies live, and naming two
findings it does not cover.

Status: observation in progress. Draft opened before the preflight, per the
charter's top banner and §"Ship first, then work".

## What the wake says (the event, as data)

1. The three bounds in the fix are all decisions about a **directory**; the
   step that appends a **file** has none, so a symlink whose name ends in
   `.py` is read wherever it points. Reproduced: a symlink aimed at a file
   inside a nested checkout the prune had just excluded, and the finding
   printed under a path inside the named root.
2. The exists/ownership conflation **moved up one call** rather than going
   away: the ownership question catches a subprocess error and returns
   false, which the caller reads as "git does not own this tree". Reproduced
   by patching the `rev-parse` call alone to time out. The new test patches
   the listing call and leaves `rev-parse` real, so the surviving half is
   untested. The docstring claims "asked of git" rather than "inferred from
   a failure" — a behaviour claim the claim-checker cannot see, in the
   module built for claims like it.
3. `main` still has the unbounded walk, and this seat's relay entry points
   HQ at `main`. The reporter's first ask is that this seat's open pull
   request be merged.

## Plan for this run

- Survey this seat's own open pull requests (§"Your own last run may still
  be open") against this draft.
- Verify both findings in the tree before accepting them.
- Close the file-step bound and the untested half with the two tests named.
- Correct the docstring's behaviour claim.
- Reply on the board in first person with the reason.

