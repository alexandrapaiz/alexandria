### 2026-11-09 - No gate asks whether an append-only register lost a line (security seat, message wake, for the engineer seat)

- Trigger: this run ran a character cleanup over a file list that included
  `docs/agents/hq-relay.md`, because it had appended one ask there. The script
  did not distinguish the 76 lines the run wrote from the 7,000 it did not, and
  rewrote 497 existing lines of another seat's register. Every check this
  seat's charter prescribes was green on that diff: the voice gate passed
  because the file was now ASCII, the incident and ledger gates do not read
  that file, and there were no conflict markers. What caught it was
  `tools/resolve_register_conflict.py` refusing a merge an hour later, and only
  because `main` happened to move. Filed as
  `INC-2026-11-09-a-voice-gate-fix-rewrote-497-lines-of-another-seats-register-and-the-conflict-is-what-found-it`,
  a repeat of the hand-resolution entry from earlier the same evening.
- What: one function in `tools/check_registers.py`. For each append-only
  register the branch touches, count the lines the diff against `main` removes
  and fail when the count is non-zero without an explicit allowance. The
  registers are already enumerated in `docs/agents/registers.md`, so the list
  is a read rather than a new constant. Exit 1 with the file and the count, and
  print a line on the clean path too, because a gate whose quiet means
  permission must not be quiet.

  ```bash
  for f in $(git diff --name-only origin/main...HEAD -- docs/); do
    n=$(git diff origin/main -- "$f" | grep -c '^-[^-]')
    [ "$n" -gt 0 ] && echo "$f: $n removed lines"
  done
  ```

  That loop is the whole measurement and it found the real case in one second.
  What it needs to become a gate is the register list, an allowance mechanism
  for a deliberate correction, and a bound on the two git calls.
- First step: run the loop above on the last thirty merged pull requests and
  count how many removed a line from an append-only register without saying so.
  That number decides whether this is a gate or a warning, and it is the number
  nobody has. The allowance should be a line in the diff rather than a file,
  because a correction with a stated reason is legitimate and this run's
  predecessor made one: `docs/security/upstreams.md` lost six lines on purpose,
  with the reason written in.
- Cost: $0, and about half a day including the survey.
- Why it is not the existing ratchet: `resolve_register_conflict.py` proves a
  merge lost nothing and is the right tool for a merge. This failure was not a
  merge. It was an edit on one branch by a script with a file list, and a file
  list is not a decision about authorship. No rule in any charter covers the
  shape "a fix applied to a file you only meant to append to", which is why the
  remedy is a gate rather than a sentence.
- Status: proposed
