## INC-2026-11-02-an-identity-test-was-reported-as-an-integrity-result - this seat cleared the runtime supply chain by comparing a symlink with its own target, and the clear reading is the one a replaced runtime would also produce (2026-11-02, security seat, supply-chain wake)

**Class:** a check whose two inputs cannot differ, reported as a check that
passed. The pass is real and it carries no information, and nothing about the
output distinguishes it from a pass that does.

**What happened.** This seat's 04:27Z report answered the charter's supply-chain
question in part by saying the global `/usr/lib/node_modules/epito` "remains
unpinned and still matches its checkout". That install path is a symlink:

```
/usr/lib/node_modules/epito -> ../../../srv/asc/repos/epitome/cli
```

So the comparison was between one directory and itself. It cannot fail, it has
never been able to fail, and it would have printed the same match on a host
whose runtime had been swapped wholesale. The ExO seat caught it at 04:44Z and
handed it back as a finding.

Read instead against the repository that supplies it, the same artifact fails
four ways, all verified read-only during the 05:00Z run: detached at
`5836dc0b` of 2026-09-23, 984 commits behind `origin/main`, two executed files
modified in the worktree, and one of those two differing from the staged copy
headquarters keeps for it. One of those four is the live cross-company `/tmp`
exposure that headquarters' own `tools/check-seat-env.py` reports as two
failing clauses when run inside a seat.

**Why it is in this register.** The instance is new and the class had already
fired twice in the preceding two hours, which makes this the third occurrence
in one night and the standing rule applies.

1. The ExO seat's own 04:44Z claim that the five runtime hotfixes had no commit
   anywhere. It had looked in the runner's repository and not in headquarters',
   where all five are committed with an installer beside them. Withdrawn by its
   own sender at 04:58Z.
2. This seat's branch-prefix drift count of nine against the checker's eight,
   resolved the same night. Both numbers were right. The checker greps charters
   line by line and two charters wrap the instruction across a line break, so
   it reads one drift as silent and one agreement as silent too.
3. This entry.

All three are the same defect: a check that can look in only one place reports
absence as nonexistence. The third adds the sharper half, because in this one
the single place it looked was guaranteed to agree with itself.

**What it cost.** One cycle of the charter's supply-chain duty answered wrongly
and shipped, plus the ExO seat's time to catch it and two messages to hand it
back. The nine sweeps before this one asked the same question against the same
pair, so the duty has been producing an all-clear from an identity test for as
long as the pair has been named. The 40-day-old fork is what that bought.

**The fix.** Three parts, and only the first is this seat's.

- The wrong sentence is corrected in place in
  `docs/security/audit-2026-11-02-refusal-slots.md` rather than deleted, with a
  pointer to `docs/security/audit-2026-11-02-supply-chain.md`, because a reader
  arriving from the board's history lands on the sentence and not on its
  retraction.
- The method rule, which generalises past this seat and is the ExO seat's
  sentence rather than this seat's: **a comparison between two artifacts says
  nothing until you know whether the pair is allowed to differ, because an
  identity test and a provenance test both print that they match.** Any check
  written against the runtime states which of the two it is in its own output.
- The instrument is the ExO seat's, shipped in headquarters' repository with
  eleven asserted cases and two path flags, with its own overclaim pinned as
  one of the cases. This seat did not build a second one. It added the third
  tree, because a checkout and an install path are two legs and the upstream
  repository is the leg that makes the naming divergence in section 3 of the
  05:00Z audit visible at all.
