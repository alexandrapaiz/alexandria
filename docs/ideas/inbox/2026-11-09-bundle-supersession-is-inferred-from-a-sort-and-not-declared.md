### 2026-11-09 - A bundle should say what it supersedes rather than leave a sort key to infer it (engineer seat)

- Trigger: today's break-fix, read against the craft scan below. `rank_bundles()`
  answers "which bundle is the library's result" by sorting, so supersession is
  something the reader infers from an order rather than something a run states.
  When the keys ran out, the inference silently became alphabetical. SkillsBench's
  `docs/dataset-versioning.md` states the opposite principle in four words,
  "supersession is annotated, never silent", and pins both a commit id and a
  content digest per task in `registry.json`.
- What: let a bundle carry `supersedes`, a list of the bundle filenames its run
  replaces, and have both rankers prefer a declared statement to an inferred one.
  A bundle naming another bundle is a fact a run knows at the moment it writes:
  the seat re-running the trigger test knows exactly which earlier bundle it is
  replacing, and today it throws that away and hopes a date comparison recovers
  it. The tie-break shipped today makes the inference deterministic, which is
  strictly better than an accident, but it is still an inference, and no sort key
  can know that a careful re-run supersedes a broad sweep recorded the same hour.
  The declared edge also gives the page something a date cannot: a bundle can be
  marked superseded and stay published, which is SkillsBench's "old leaderboards
  stay up, flagged, not deleted".
- First step: `supersedes` as an optional field, read by `rank_bundles()` and
  `rankBundles()` to drop a named bundle below the one naming it, with the
  existing date and pre-registration keys unchanged beneath it. The gate already
  built today reports a tie, so the first measurement is free: every tie it
  reports is a place a human would have known the answer.
- Cost: $0
- Status: proposed
