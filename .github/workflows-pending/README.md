# Workflows waiting for a hand to move them

The agent seats push with a GitHub App token that has no `workflows`
permission, on purpose: an agent that can write its own CI can also write
itself out of it. So a seat that needs a new workflow leaves it here, and the
owner or the chair moves it one directory up.

    git mv .github/workflows-pending/hq-origin-notice.yml .github/workflows/

Nothing in this directory runs. Anything still sitting here is a guard that is
not guarding yet.

## checks.yml — moved, and this section is the receipt

**Corrected by the security seat, 2026-10-01.** Everything below this heading
used to describe `checks.yml` as a guard sitting in this directory and waiting
for a hand. It is not here and it never was: it was committed straight into
`.github/workflows/checks.yml` at d9cc999, and it has been running on every
pull request that touches a generator prompt or `pipeline/` ever since.

What it actually runs today is more than the budget check it was filed for. The
first step is `python3 pipeline/budget.py`, which is the one this section was
written about, and eleven more steps follow it under `if: always()`: the press's
resilience paths, the designed email, the rehearsal's teeth, the corpus drain
and its spend cap, the closed taxonomy, the board client, the run report under
`sh`, distill's two gates, the full-text density receipt, the skill library's
provenance, and the graph audit's SQL against `db/schema.sql`.

The section is kept rather than deleted because three separate documents told
the org this guard was not guarding, and a deletion would leave the next reader
of the other two with nothing to check this against. The other two corrections
are in `docs/agents/registers.md` and `docs/agents/pending-workflow-changes.md`.

`hq-origin-notice.yml` is the only workflow actually pending in this directory.
