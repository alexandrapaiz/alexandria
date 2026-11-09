### 2026-11-09 - The trigger engine cannot tell two senses of one word apart, and that decided a case (engineer seat)

- Trigger: measured, not argued. `skills/agent-approval-paths/triggers.json`
  case `ap-pos-4` states delta 3's situation in an operator's words, the alert
  on a mid-task persisted-rule proposal and the rate to budget for it, and it
  routed to `agent-containment` at 0.357 against the right skill's 0.219.
  Scoring the prompt against both descriptions directly shows where the winning
  mass came from, and it is four same-spelling, different-sense matches:
  `alert` from "when an agent's alerts fire into a queue nobody acts on",
  `budget` from "an isolation architecture's published overhead is your capacity
  budget", `rule` from "when security rules in a system prompt are counted as
  enforcement", and `propos` from "tool filtering or injection detection is the
  proposed fix". Not one of the four is about alerting on a persisted-rule
  proposal. The case was lost to a sense collision rather than to a gap in
  coverage, and the skill's body had answered the question since its previous
  version.
- Why it is worth a line rather than a shrug. The library's differentiator is
  that a skill is found by the person who needs it, and 69 percent of public
  skills never fire. A seat looking at a failing positive case reads it as "my
  description under-covers my subject" and spends the run widening the
  description, which is the wrong repair and is actively harmful under a
  150-word editorial budget where every addition is a swap. This run nearly
  made that mistake and only avoided it by scoring the prompt against the two
  descriptions term by term. Nothing in the instrument does that for a reader:
  the failure line prints the top four skills and their scores, which says who
  won and never says on what.
- What: have the engine report, per case it decides, the terms that carried the
  winner's mass and the clause each came from. Then a sense collision is visible
  in the output instead of requiring a hand-written script, and a seat can tell
  the two diagnoses apart before it edits anything. This is instrumentation and
  not a scoring change, so it cannot move a single verdict.
- The harder half, offered and not asked for. Separating senses needs more than
  a stemmer, and the cheap approximations are worse than nothing: a stop list of
  "ambiguous" terms would have deleted `alert` from a description that legitimately
  means the alerting one. A per-clause match, where a prompt term scores only
  against the activation clause it plausibly belongs to, is the direction worth
  measuring, and the 85-case suite is the instrument that would say whether it
  helps. Worth noting that the engine is pre-registered, so a scoring change is
  a new engine version and a re-run of every bundle, not an edit.
- First step: the per-case term attribution in the existing report, which is
  additive, and one re-run of the suite to confirm no verdict moved. The
  measurement that motivates it is already recorded in that case's own note and
  in `skills/agent-approval-paths/REVISIONS.md`.
- Cost: $0
- Status: proposed
