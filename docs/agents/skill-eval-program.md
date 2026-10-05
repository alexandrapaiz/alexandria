# The skill testing and refinement program (ADR-40)

Working note for the engineer run of 2026-10-05. ADR-40 lists seven items
for the harness and three for the gate, each citing a claim id in the
corpus. This file tracks which are built, so the next run does not have to
read the diff to find out.

| ADR-40 item | Surface | State |
| --- | --- | --- |
| H1 matched ablation, pinned seed | tools/skill_eval.py | planned |
| H2 differential task selection, bare-first pass | tools/skill_eval.py | planned |
| H3 repetitions, spread, pass@k | tools/skill_eval.py | planned |
| H4 executable tasks in the Docker sandbox | tools/skill_eval.py | planned |
| H5 certificate-faithful rubrics, exploit test | tools/skill_eval.py | planned |
| H6 judge separate from subject, task audit, length bias | tools/skill_eval.py | planned |
| H7 per-section credit | tools/skill_eval.py | planned |
| G1 one section per revision, inputs pinned | tools/skill_gate.py | planned |
| G2 held-out gating, rejected-edit buffer | tools/skill_gate.py | planned |
| G3 correction clustering before an edit is proposed | tools/skill_gate.py | planned |
| G4 three-module cap | tools/skill_gate.py | planned |
