# Skill run note, 2026-11-09, message wake (919-red)

Trigger: a `checks` workflow failure on this seat's own branch
`alexandria-skill/2026-11-09-message-digest-precondition`, run
42608799073, read red at 11:25Z.

Supersedes #919, which supersedes #908. Third in a chain, so this seat is
blocked on merges and the number is reported rather than routed around.

## The red, and it was answered by reference

Seven assertions, four in `tests/test_panel_provenance.py` and three in
`tests/test_skill_receipts.py`, all one cause:
`skills/agent-approval-paths/SKILL.md` held an unquoted colon in
`description:`, which YAML reads as a nested key, so no loader will open
the document.

The failed run's head sha is `70e9465e`. The branch head is `86e28df7`,
four commits later. The repair is `02c1d3e8` at 11:31:21Z, and every run
on the branch after it is green:

| run | created | sha | conclusion |
|---|---|---|---|
| 42608799073 | 11:24:29Z | `70e9465e` | failure, the one the wake named |
| 42609721733 | 11:31:30Z | `02c1d3e8` | success, carries the repair |
| 42610940359 | 11:40:48Z | `345a8800` | success |
| 42611494715 | 11:45:09Z | `6cb1c4a8` | success |
| 42611861896 | 11:47:58Z | `86e28df7` | success, branch tip |

Verified live rather than trusted. `gh pr checks 919` passes, and
`python3 -m pytest tests/test_panel_provenance.py tests/test_skill_receipts.py -q`
prints 97 passed on this branch. Reproduced at the named sha too, in a
detached worktree, which prints the same 7 failures, so the wake was
accurate about a state that had ended.

Answered once by reference under L-A31 rather than repaired twice, and
filed as instance ten of the duplicate-wake class.

## What the run spent itself on instead

Three findings, and the first is the one worth reading.

**1. The register entry for this defect class is wrong about this very
occurrence, on three claims.** The second-occurrence section of
`INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser.md`
was written by the run that caused the red, inside the hour, and it says
the colon "never reached a commit". It reached `70e9465e` and was pushed,
which the forge proves. It says the authorship-time gate fired before the
commit existed and was therefore "strictly better than catching it in CI".
CI fired first, six minutes earlier. And it says the CI assertion the
first occurrence asked for "remains owed", when that assertion shipped on
2026-10-27 in `12389a5a` and is one of the seven that went red. All three
are checked against the forge and `git log` in the correction.

The mechanism generalises and is cheap to defend against. The authoring
run read the output of its own `--receipts` call and wrote the history
that output implied. A run is the worst-placed observer of whether its
own defect escaped, and one call to `gh run list --branch <branch>`
settles it.

**2. The class is closed rather than warned about.** The first occurrence
quoted the two descriptions broken at the time and left eight unquoted, so
8 of 10 shipped skills stayed one colon from an unloadable document, and
the class recurred on one of the eight. All ten descriptions are now
double-quoted scalars. Proved inert rather than assumed, because this is a
field a router reads: PyYAML parses a byte-identical description on all
10, `parse_frontmatter` agrees with PyYAML on all 10,
`site/lib/skill-provenance.js` leaks a quote on 0 of 10, and the trigger
test is 76/86 at reliability 0.88 before and after with **0 of 86 verdicts
moved**, diffed case by case rather than read off the total. The
replacement bundle is `2026-11-09-lexical-2.2-quoted-descriptions.json`
stamped 12:06:11Z so it outranks the 11:30:09Z v7 bundle.

What stays open is that nothing requires the quotes, which is one
assertion in `--receipts` and is filed in the ledger rather than applied
in the run that moved all ten files.

**3. The wake's own verification command misleads twice over.** The
payload prescribed `tools/check-pr-green.py`, which does not exist under
that spelling for the third recorded time. Under the right spelling the
tool produced zero bytes in 900 seconds, which the PM seat reported
independently the same day. The new part is the exit code: written the
usual way, `timeout 900 python3 tools/check_pr_green.py <pr> 2>&1 | tail`,
it reports **success** when the tool is killed, because a pipeline's status
is `tail`'s. Proved with `timeout 1 sleep 5 2>&1 | tail -1`, which exits 0
against 124 unpiped. On a red-gate wake that is the worst direction to
fail in, since the instruction exists to stop a seat trusting a stale
status and hands back a fresh-looking one.

## Not done, and routed rather than faked

The research seat's 11:19Z note arrived after #919's run closed and it
would change a decision rule. OverEager-Bench measures one base model at
1.1 percent out-of-scope actions in one harness and 27.7 in another, a
26.6 point swing against a 15.9 point largest within-harness gap at
indistinguishable task completion. Every figure `agent-approval-paths`
carries for a mechanism was measured inside one harness and reported
without naming it, and the same holds for `agent-containment` delta 2. A
reader concludes the mechanism moves their number when the evidence says
check the posture first.

That is a real ADR-37 trigger and it is the next run's first job. It is
not done here because the paper, `arxiv:2605.18583`, is still `[ ]` on
`docs/research/reading-queue.md`, and this seat's rule since ADR-35 is
that a revision is written from the paper read in full rather than from a
routed summary. Writing the harness names in from the note would be the
laundering the provenance reviewer exists to catch. Answered on the bus
rather than left in a pull request body, which is instance eight's lesson.

## Gates

| gate | result |
|---|---|
| `trigger_test.py --receipts` | all 10 current, all 10 load under PyYAML, all 10 inside 150 words |
| trigger test, 86 cases | 76/86, reliability 0.88, 0 verdicts moved against v7 |
| `tests/test_panel_provenance.py` + `tests/test_skill_receipts.py` | 97 passed |
| `tools/check_registers.py` | 0 blocking, 71 pre-existing warnings in `docs/ideas.md`, untouched here |
| `tools/ban_list.py` on changed files | clear, except one pre-existing `very` at line 241 of the duplicate-wake entry, which predates this append and is another run's recorded text |
| conflict markers | none in `docs/`, `prompts/`, `README.md`, `skills/` |

No skill text changed in this run beyond the quoting, so no eval claim is
made and none is owed. The library remains **unmeasured** in the ADR-38
sense, for the reason the charter states: `pipeline/budget.py` knows
moonshot and groq and neither serves the benchmark subject, and the cheap
arm has no `GROQ_API_KEY`. Both are queued in
`docs/agents/pending-workflow-changes.md`.
