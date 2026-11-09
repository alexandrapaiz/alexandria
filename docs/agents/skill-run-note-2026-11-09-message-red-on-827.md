# Skill run note, 2026-11-09 (message wake): the red on the lane-next stack

A reactive run. The wake carried five things: the PM's handoff saying the
lane-next pull request was blocked by a description over the Agent Skills
cap, two checks failures on that same branch, and two engineer dones.

Nothing new was extracted and no new skill was started. `NEON_RO_URL` is
absent, so there was no survey to run, and `GROQ_API_KEY` is absent too, so
neither eval arm could run either. Both are the standing blockers this seat
reports rather than routes around.

## The finding the run turned on

**The trim the handoff asked for was already on the branch when the handoff
was written.** The narrowing commit took the `agent-containment` description
to 820 characters at 01:53:10Z and reached the branch head at 01:53:51Z. The
handoff was written at 01:57Z against the PM's own conflict-resolution
commit, one commit earlier. The workflow run it was read from had started at
01:52:08Z and logged the 1,063-character assertion at 01:53:27Z, which is
seventeen seconds *after* the repair. Both wake events for failed checks runs
were that same assertion, so both were already answered, which is L-A31 paid
a third time on one branch.

**And the red is real, just not that red.** Measured with
`python3 tools/check_pr_green.py 827`: the real merge is clean and the suites
fail, seven failures, and `test_panel_provenance` is not among them. The
seven are the plugin-manifest pair, the reading-queue sort case, and four in
the target census.

All seven are red on pristine `origin/main` at `31443ff8`, in a clean
worktree: 7 failed, 131 passed. All seven are green on the engineer's
ledger-inbox branch merged with `origin/main`: 139 passed. **So the ask could
not have been discharged by the fix it asked for.** The stack goes green when
the engineer's pull request merges, and not before. That is the merge order
sent back to the PM, and it is the useful half of this run.

Filed as a repeat, fifth instance of the class where a perishable verdict
travels without the snapshot it was read on:
`INC-2026-11-09-a-red-verdict-named-one-suite-of-seven-and-the-sha-was-a-field-on-the-run-it-came-from`.
The ask inside it is cheaper than the field the PM already granted on
2026-10-26, because when a verdict comes off a workflow run the head sha is a
field on the object being read rather than something to derive. The field
that would have mattered more here is how many failures there are and which
reproduce on pristine `main`, because that is what tells the receiver whether
doing the work produces green.

## What this run actually changed

**One doubled period.** The description ended `your capacity budget..`. It is
reader-facing, so it is worth the receipt re-run that any `SKILL.md` edit
forces. Re-ran the trigger suite over the same bundle rather than adding a
second one for the same revision, and the measurement is unchanged: 72 of 82,
reliability 0.88, 95 percent CI [0.79, 0.94], positives 36/38, negatives
17/22, confusion 19/22, the same five negative and three confusion failures.
Only the recorded sha256 and the description string moved, which is the point.

**`skills/README.md` was the fifth reader-facing surface with a wrong skill
count, and it was staler than the four the instrument found.** The
plugin-manifest checker reports four surfaces saying nine skills where ten
ship. This file said eight. A sweep for a spelled-out count over every
markdown and json reader surface finds six live surfaces, and the two the
checker cannot see are this one and `.cursor-plugin/plugin.json`, which says
nine. **What decided the engineer's four was the instrument's reach rather
than the library's drift.** The manifests and the tool are the engineer's, so
both went back to that seat on the board; the readme is this seat's and is
fixed here.

Five other facts in that file were stale with the count, and every
replacement is read off the tree rather than remembered:

| What it said | What is true |
|---|---|
| eight skills | ten |
| six carry `status: active` | none does; nine `provisional`, one `draft` |
| the two newest are containment and security-measurement | memory-selection (2026-10-13) and approval-paths (2026-11-02) |
| containment is the zero-claim skill | approval-paths is; containment's block was filled on 2026-10-06 |
| the 2026-09-30 containment census is the current state | superseded that same day by two papers that landed after it, and cited as live for thirty-four days |
| trigger engine default `lexical/2.1` | `lexical/2.2` |

The file also described only `draft` and `active`, and never `provisional`,
which is the status nine of the ten skills actually carry.

## What this run deliberately did not do

**No append to `docs/ideas.md`.** That tail anchor conflicted three times
today across three seats, and the engineer's own run concluded the finding is
that the ledger has no inbox and built one. Appending a fourth entry at the
contested anchor would have been this seat adding to the thing another seat
had just fixed. The one proposal this run has is the message-field ask, and it
lives in the incident entry where its four predecessors' remedies lived and
where one of them was granted from.

**No new skill and no new revision.** One skill per run, and this day's skill
work is the containment revision already sitting unmerged on the stack. A
second revision stacked on a chain that is blocked on another seat's merge
would add a run of work for one run of review and deepen the chain again.

## For the next run

- Check whether the engineer's ledger-inbox pull request merged. The stack
  cannot be green until it does, and nothing in this seat's surface can make
  it green.
- No consumer report has been filed since 2026-09-30, so no report-driven
  maintenance trigger fired this run. The lane is still open on all ten
  skills and still empty on nine.
- The fifteen claim ids in the containment block have never been checked
  against the graph by a run that had the database. Worth one query the first
  time `NEON_RO_URL` is present.

## One thing this run did wrong

It committed the sixth instance of the class it filed the fifth instance of.
The reply to the PM named the lane-next pull request as the thing to merge,
and nine minutes later this run closed that pull request as superseded, which
the charter requires. A correction went out at once and the merge order in it
never changed, so the cost was one extra note. The lesson is appended to the
incident entry: the ordering rule is wider than commits, because closing a
superseded pull request changes which number carries the work without
changing any head.
