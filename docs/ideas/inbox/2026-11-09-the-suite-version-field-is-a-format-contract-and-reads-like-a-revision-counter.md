### 2026-11-09 - suite_version is a format contract and reads like a revision counter (skill seat)

- Trigger: this seat added a twelfth task to
  `skills/agent-approval-paths/evals/evals.json` for `agent-approval-paths` v8
  and bumped `suite_version` from 2 to 3 the way a version number invites.
  `python3 tools/skill_eval.py --check` went red with "contract is 3, this
  harness speaks 1 and 2". The field is the FORMAT CONTRACT and not a count of
  this suite's revisions: `tools/skill_eval.py` reads it as `contract` and
  `SUITE_CONTRACTS` accepts only 1 or 2. The value was put back to 2 in the same
  run, so nothing shipped broken, and the gate behaved exactly as it should.
- What: the name is the defect, not the harness. `suite_version` sits beside
  `written`, `author` and `note` in a file whose own task count changes every
  revision, so every reviser has a reason to bump it and the only signal that
  this is wrong is a red check later. The comment in `tools/skill_eval.py` at
  line 99 already records that two seats write one format and that this was the
  skill seat's spelling of the harness's `contract`, so the harness accepts both
  names for one meaning. The repair is to accept `contract` as the canonical
  name in new suites, keep reading `suite_version` for the ones that have it,
  and have `--check` say in its own error that the field is a format contract
  rather than a suite revision. A one-line hint in the error message is most of
  the value, because the field will keep being bumped until the message says not
  to.
- First step: add the sentence to the failing branch of the contract check in
  `tools/skill_eval.py`, naming `contract` as the preferred key and pointing the
  reviser at the task count in `note` as the place a suite revision is recorded.
- Cost: $0
- Status: proposed
