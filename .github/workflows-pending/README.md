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

## Still pending as of 2026-09-26, and the cost is now larger

Filed by the engineer seat 2026-09-19. Seven days later it is still here,
which means the repository's 279 Python tests and 66 Node tests run in
exactly one place: a seat's own session, on the honour system. Every
sentence above about what CI holds is written in the future tense.

That mattered less when the only thing at stake was whether an editorial
merge broke the press, because the press refuses the call itself when the
sums do not work. It matters more as of today. `python3 pipeline/budget.py`
now also fails when a per-run spend cap is raised past the ceiling in
docs/finance/opex.md, and when two jobs that share Moonshot's
single-concurrency slot are scheduled into overlapping windows. Those two
guards exist to stop a change nobody is watching, and until this file moves
one directory up they stop it only for whoever remembers to run the command.

    git mv .github/workflows-pending/checks.yml .github/workflows/checks.yml

One command, and it is the owner's or the chair's: a seat's token has no
`workflows` permission, for the reason the top of this file gives.
