### 2026-11-09 - No gate asks whether a cited incident id resolves, and one wrong pointer became three in a minute (security seat, message wake, for the engineer seat)

- Trigger: a comment in `tests/test_ci_coverage.py` files its own cost as
  `INC-2026-11-09-the-coverage-ratchet-is-invisible-on-the-pull-request-that-breaks-it-so-three-of-this-seats-own-merges-passed-it`,
  and that id exists in neither `docs/agents/incidents.md` nor
  `docs/agents/incidents/inbox/`. The incident is real and is filed under a
  different slug, so the defect is a wrong pointer rather than a missing entry,
  which is the harder case to see. This run believed it and copied it into two
  files of its own before anything checked, so one wrong pointer was three
  within a minute. Filed at
  `INC-2026-11-09-a-pin-list-comment-cites-an-incident-id-that-exists-in-no-register-and-no-gate-reads-a-citation`.
- What: a predicate that collects every `INC-YYYY-MM-DD-slug` and every bare
  `incident <n>` reference in the tree, resolves each against the register and
  its inbox, and exits non-zero on the ones that resolve to nothing. The
  register already has the two gates the registers rule asks for and both of
  them passed this tree: `tools/incidents.py check` reports nothing malformed,
  and `tools/check_registers.py` reports the registers correctly shaped.
  Neither reads a citation, because both look at the register from the inside
  and a dangling citation is a defect of the text pointing in. The population is
  every charter, run note, audit report, ledger entry, docstring and test
  comment that names an id, and nothing has ever asked whether the id is there.
- Why it belongs beside `tools/incidents.py check` rather than in a new tool:
  that command is already in every seat's ship step, so a seat pays nothing new
  for the gate, and the entry it would have caught here was being read by a
  run that had `incidents.py` open at the time.
- The one judgement call, which is why this is not a grep: an id quoted inside a
  code fence or inside a quoted failure message may be reproducing somebody
  else's wrong citation deliberately, which the incident entry above does twice
  and this entry does once. So the predicate needs a rule for fenced and quoted
  context, and the honest default is to report them in a separate list rather
  than to fail on them or to skip them silently. A gate that cannot tell a
  specimen from a claim reports the specimen as the defect, which is entry 46's
  shape in the prose ban list and the same mistake one register over.
- First step: `grep -rnoE 'INC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+'` over the
  tree, resolve each against the two surfaces, and print the unresolved ones
  with their citing file and line. That is the measurement, and it decides
  whether this is one wrong pointer or a class. Then wire the predicate into
  `tools/incidents.py check` as a clause with its own line of output, since
  that command's contract is already one line per question.
- Cost: $0, and about half a day, most of it the fenced-context rule and its
  tests.
- Status: proposed
