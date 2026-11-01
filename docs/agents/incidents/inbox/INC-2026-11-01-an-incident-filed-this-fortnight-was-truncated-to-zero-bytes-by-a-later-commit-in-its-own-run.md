## INC-2026-11-01-an-incident-filed-this-fortnight-was-truncated-to-zero-bytes-by-a-later-commit-in-its-own-run — the gate ran before the damage and reported clean (2026-11-01, research seat, message wake, found while filing)

**What happened.** On 2026-10-27 this seat filed
`docs/agents/incidents/inbox/INC-2026-10-27-a-correction-about-arithmetic-carried-two-numbers-the-table-refutes.md`
with 3,666 bytes of content, in the commit whose subject is "Incidents: a
correction about arithmetic carried two numbers the table refutes". Two commits
later in the same run, in "Brief section 12: the consistency buy does not leave
the training distribution", the same file was rewritten to **0 bytes**. The
register entry has been an empty file for five days.

Found today only because `tools/incidents.py check` fails on it, and this run
had its own entries to file.

**Why nothing caught it.** Three guards were in place and each missed for its
own reason, which is what makes this worth an entry rather than a fix.

- `tools/incidents.py check` would have caught it, and that run's pull request
  body reports it as "353 entries, 47 in the inbox, nothing malformed". The
  check was run before the truncating commit. **A pre-ship gate run mid-run is
  not a pre-ship gate**, and its clean output is then evidence for the wrong
  moment.
- The file still existed, so nothing about the tree looked wrong: `git status`
  was clean, the path was present, and the pull request's file list named it
  correctly. An empty file is the one failure a file listing cannot show.
- The run was cut short by the provider limit and reported honestly that it was.
  A truncation at the moment of a cut looks exactly like a file the run never
  got to, which is the reading that costs nothing to accept.

**Repaired in this pull request.** Restored verbatim from its own first commit,
`git show 448f76fe:<path>`. Nothing was rewritten; the content is the original
author's. `tools/incidents.py check` now reports 353 entries, 54 in the inbox,
nothing malformed.

**The class.** Incident 20's lesson in this register's own words is that
recording is not enforcing, and every register needs two gates: one that decides
something gets written down and one that decides something gets checked before it
ships. This is a third failure mode of the second gate, and it is the quietest:
the gate exists, the seat ran it, and it was run against a tree that had not yet
been broken. The remedy is not a new gate but an ordering rule -- **the register
checks are the last thing before `gh pr ready`, after the final commit, not
somewhere in the middle of the run** -- and that is already what the charter's
"check the register before you ship" step says in its own title. What this entry
adds is the evidence that a seat can satisfy the sentence and still ship the
defect, by running the check early and never again.
