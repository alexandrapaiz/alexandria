### 2026-11-09 - Without the database a new skill is impossible rather than merely unsourced, and the charter says the softer thing (skill seat, for the owner)

- Trigger: this run opened with `NEON_RO_URL` absent for the fourth run running
  and read its charter's instruction for that case, which is to "say so at the
  top of your PR, skip extraction, and spend the run on the parts that need no
  database." That reads as a quality constraint. It is a hard one, and the
  difference decides what a run can even attempt.
- What: a skill written with no database necessarily ships
  `provenance.claims: []`, because a claim id is a row this seat cannot read.
  `tests/skill-provenance.test.mjs` carries two gates on that case. The first
  requires `status: draft` when `claims` is empty. The second,
  `the claim ids still reach almost every skill, so the carve-out is not the rule`,
  asserts `citing.length >= LIBRARY.length - 1`, which permits **exactly one**
  zero-claim skill in the library at a time. `skills/agent-approval-paths`
  holds that slot as of 2026-11-02.
- So a new skill extracted without the database does not ship unsourced. It
  turns the suite red, and the only ways to green are to retire
  `agent-approval-paths` or to widen a gate that exists to stop exactly this.
  Both are wrong for the right reason, which is that the gate is correct: a
  library where most skills cite nothing is the state it was written to catch.
- Why it is worth writing down rather than discovering a fifth time: three runs
  have reported the absent secret and each described the consequence as thin
  provenance. The real consequence is that **the new-skill half of this seat's
  charter is switched off**, which is a different sentence to put in front of
  whoever decides whether to write the secret. Maintenance, retrofits and
  revisions of existing skills are unaffected, because those cite claim ids the
  library already holds.
- First step: one clause in `prompts/skill-agent.md` under Data access, saying
  that with `NEON_RO_URL` absent the run does maintenance only, and naming the
  gate as the reason. That is a charter edit and so the owner's, and this
  entry is the evidence for it rather than the edit.
- Cost: $0, and the unblock is one secret, which is hers alone.
- Status: proposed
