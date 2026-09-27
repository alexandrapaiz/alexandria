# Workflows waiting for a hand to move them

The agent seats push with a GitHub App token that has no `workflows`
permission, on purpose: an agent that can write its own CI can also write
itself out of it. So a seat that needs a new workflow leaves it here, and the
owner or the chair moves it one directory up.

    git mv .github/workflows-pending/checks.yml .github/workflows/checks.yml

Nothing in this directory runs. Anything still sitting here is a guard that is
not guarding yet.

## checks.yml — does the digest request fit the model's budget?

Filed by the engineer seat 2026-09-19 for incident 22. Runs
`python3 pipeline/budget.py` on every pull request that touches a generator
prompt or the pipeline, and fails the build with the arithmetic printed when
the prompt plus the worst-case payload plus the output reservation no longer
fits the model's per-request ceiling.

Until it is moved, the same check still runs in two places, so the press is
not unguarded in the meantime: `modal run pipeline/weekly.py` runs it locally
before it spends anything, and the digest run itself refuses to call Groq when
the sums do not work. What is missing without the workflow is the early
warning, at the moment an editorial merge is proposed rather than the next
time the press tries to print.

The same workflow has since grown three more steps, each `always()` so a
red budget step cannot hide them: the press's bad-day paths
(`tests/test_press_resilience.py`, incident 24), the designed email
(`tests/test_email_template.py`, the owner's 2026-09-24 ruling), and the
rehearsal print (`tests/test_press_rehearsal.py`,
INC-2026-09-24-press-provider-migration). None of them needs a key, a
network or a database.

The rehearsal step is worth one sentence of its own, because it is the
only one that guards a gate CI cannot run. The gate itself is `modal run
pipeline/weekly.py::rehearse`, a real call with a real key that costs
real money, and it belongs to the chair's deploy command
(docs/agents/runtime-changes.md). What CI holds is that the gate still
has teeth: that a rehearsal cannot write to `digests`, cannot mount a
mail credential, and cannot pass on a receipt naming a different model.

## hq-origin-notice.yml — was an HQ decision just merged?

Filed by the ExO seat 2026-09-27, queued as item 5 of
`docs/agents/pending-workflow-changes.md` since 2026-09-24. On every push to
main it greps the pushed commits for HQ markers and, on a hit, writes a job
summary naming them and pointing at `docs/agents/cross-repo-law.md`. It blocks
nothing and dispatches nobody.

    git mv .github/workflows-pending/hq-origin-notice.yml .github/workflows/hq-origin-notice.yml

Why it is worth the move now rather than at the ExO seat's convenience: the
duty it supports (`prompts/exo-agent.md` §3f) runs weekly and its trigger is a
merge. On 2026-09-25 commit `1baeb7f` changed how this repository deploys to
production, citing HQ Incident 5, and the whole record of that decision inside
alexandria was the commit subject plus nine lines of comment in the workflow it
added. `grep -rn "HQ Incident 5" docs/` returned nothing. This job would have
put it on screen the minute it landed.

## The house rule this directory now carries

**A new workflow file belongs here. An edit to an existing workflow does not.**
A full copy of a file the owner also edits applies cleanly and silently reverts
every change made to the live file since the copy was taken. A diff on the
queue page fails to match and announces itself. Incident 26 is what that
loudness is worth. The split is written up in
`docs/agents/pending-workflow-changes.md` under "Two lanes".
