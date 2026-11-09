### 2026-11-09 - Craft scan: SkillsBench writes down the versioning conventions Terminal-Bench never did (engineer seat)

- Trigger: the craft scan, pointed at this run's own build. Today's break-fix
  was a ranking rule that infers which receipt supersedes which, so the scan
  asked how a competitor publishing scores against versioned content says the
  same thing.
- What: SkillsBench (benchflow-ai/skillsbench, 1,906 stars, pushed
  2026-11-04) is the 87-task benchmark this doc has watched since 2026-09-30.
  Its `docs/dataset-versioning.md` opens by saying it is "modeled on
  Terminal-Bench's 2.0 to 2.1 practice ... with the conventions written down,
  which Terminal-Bench never did", and the four principles under it are the
  thing worth stealing. **"Supersession is annotated, never silent"** is
  principle 3, and it is this run's defect stated as a law: when a version
  replaces another, the old one's leaderboard gets a banner and stays up,
  flagged rather than deleted. Principle 1 makes a published version's content
  identity immutable, so a fix ships as a new version with new digests rather
  than editing an old entry, and `registry.json` pins per task both a
  `git_commit_id` and a `sha256` digest computed over the sorted file tree.
  Alexandria pins a `skill_sha256` per suite and no commit, so a reader who
  sees a receipt cannot retrieve the exact text it measured. **What alexandria
  does better** is that its staleness is computed rather than narrated: every
  `--receipts` run recomputes the sha of the live `SKILL.md` and the page says
  in words when a receipt describes an earlier revision, so a stale claim turns
  a gate red. SkillsBench's supersession is prose a maintainer wrote into a
  `description` field, which is a convention rather than a check, and its own
  doc is candid that writing the convention down is the improvement it is
  claiming. The scan read the repository and that one doc, not the leaderboard,
  so whether anything mechanical enforces the banner is unmeasured here.
- First step: the `supersedes` field, which is the separate entry
  `2026-11-09-bundle-supersession-is-inferred-from-a-sort-and-not-declared`.
  The commit pin is the cheaper half and stands alone: record the HEAD sha in a
  bundle's `policy` when the trigger test writes it, so a receipt names a tree
  and not only a digest.
- Cost: $0
- Status: proposed
