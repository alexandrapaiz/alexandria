### 2026-11-09 - The no-transfer rule's home is the measurement skill, and the trigger suite said so before I did (skill seat)

- Trigger: `ap-pos-7` was written against `agent-approval-paths` v9's new
  checklist item 3 and failed, routing to `agent-security-measurement` at
  0.2191 against this skill's 0.0543, a 0.165 margin and not narrow. Reading
  that skill's description settled it against the case rather than against the
  router: it already claims "when an injection detector's published accuracy is
  carried across to tool-call payloads", alongside reporting an attack success
  figure and a guardrail's utility cost. The case was mis-expected and is now
  recorded as `ap-conf-3`, a passing confusion case.
- What: the general rule that a mechanism's measured effect does not transfer
  across harnesses is a measurement-validity rule, and it has no home in the
  library today. `agent-approval-paths` v9 carries it only as a constraint on
  reading its own figures, which is the right scope for that page and the wrong
  scope for the rule. The evidence is now strong enough to be somebody's
  section: `2610.07639` holds the model fixed at GLM-5.2 and shows the same
  mechanism's own effect ranging **71.7 pp** across six harnesses, -5.0 pp in
  gptme against -76.7 pp in Claude Code, with utility under that mechanism flat
  inside a **5.5 pp** band across all six, 94.5 to 100.0, and Fisher on the two
  endpoint cells at 1.3e-13. It also carries the companion rule, which is that
  an attack-success column may not be read without the utility column beside it:
  in the approval-engaged arm the harness at 0.0 percent attack success
  completed 50.0 percent of the legitimate work against 95.4 percent at the
  other end, and the two columns rank together at Spearman 0.814 over the six,
  which this run computed and the paper does not report. One skill per run is
  the charter's limit, so this run did not open that page.
- First step: a `agent-security-measurement` revision run that reads
  `2610.07639` in full for itself, screens the rule against a bare subject the
  way ADR-38 rule 1 asks, and either takes the section or records why the bare
  answer already contains it. The paper, the derivations and the confound are
  written up in `skills/agent-approval-paths/REVISIONS.md`, eighth entry, so the
  reading is not owed twice. Note before starting that the sibling skill's
  description is already at the 150-word ceiling, so a trigger clause for this
  decision has to be traded in and the shared verdicts diffed case by case.
- Cost: $0
- Status: proposed
