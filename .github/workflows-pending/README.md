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
