### 2026-11-09 - the staleness tool's smoke mode prints fixture findings about a real skill through the live renderer (skill seat, for the engineer)

- Trigger: this run has no `NEON_RO_URL`, which is the fifth run in a row
  without one, so the charter's four maintenance triggers cannot be computed
  live. `python3 tools/skill_triggers.py --smoke` runs instead. Its output opens
  with "Every line below is a skill whose ground moved under it, found by the
  four triggers ADR-37 names" and then prints four `- [ ]` lines naming
  `skills/harness-engineering`, a real skill in this library, as having a
  deprecated claim 85, a claim 199 refined by claim 421 at confidence 0.82, a
  paper whose citations moved 4 to 40, and an eval delta that fell from +0.41 to
  +0.05. None of that is true. All of it is fixtures.
- What: `smoke()` at `tools/skill_triggers.py:763` builds its records from the
  module's `SMOKE` dict against a hardcoded `Row` whose `path` is the real
  `skills/harness-engineering`, then renders them through `render()` and
  `block()`, which are **the same two functions the live path uses**. So the
  output is not merely similar to a live finding, it is produced by the live
  renderer and is byte-indistinguishable in form, down to the
  `key: skills/harness-engineering#claim-85-deprecated` dedupe keys that
  `docs/research/reading-queue.md` lines carry. The giveaways are only in the
  content, and they are quiet: the claim text reads "the older result" and a
  paper is titled "A paper the field found". A seat that runs `--smoke`
  because `--live` is unavailable, which is every run of this seat since
  2026-11-02, is one paste away from appending four false maintenance findings
  about a real skill to the reading queue, where the research seat drains them
  and would spend a run reading a paper that does not exist.
  **This has not happened:** a grep for all four fixture keys across `docs/` and
  `skills/` returns zero, so this is a hazard and not an incident, and it is
  filed as the former on purpose.
- First step: one line in `smoke()`, and it is a prefix rather than a redesign.
  Either pass a flag through `render()` and `block()` that stamps every fixture
  line with `FIXTURE` and replaces the preamble, or change the fixture `Row.path`
  to a slug no skill has, such as `skills/_smoke-fixture`, which costs nothing
  because the path is never read off disk and makes the output self-labelling in
  the one field a reader keys on. The second is smaller and this seat would take
  it. The clause's own test names would then still read true, since all seven
  `ok:` checks assert arithmetic rather than paths.
- Cost: $0
- Status: proposed
