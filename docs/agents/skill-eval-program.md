# The skill testing and refinement program (ADR-40)

Built by the engineer seat on 2026-10-05, on the owner's directive, from the
chair's ADR-40. Ten items, each citing a claim id in the corpus. This file says
which are built and where, so the next run does not have to read a diff to find
out, and so a reader can tell a built item from a documented one.

Every item below is exercised by a check that costs nothing: `python3
tools/skill_eval.py --smoke` (13 checks), `python3 tools/skill_gate.py --smoke`
(23 checks), `python3 tools/corrections.py --smoke` (11 checks), and the pytest
suites `tests/test_skill_eval.py`, `tests/test_skill_gate.py` and
`tests/test_corrections.py`.

## The harness, ADR-40 items 1 to 7

| Item | Where | State |
| --- | --- | --- |
| 1 matched ablation, pinned seed (C362, C1090) | `ablation_manifest`, `Subject.ask`, `pipeline/llm.py`'s optional `seed` | built |
| 2 differential tasks, bare-first pass (C412) | `bare_pass`, `differential_selection` | built |
| 3 repetitions, spread, pass@k (C248) | `stdev`, `spread_of`, `pass_at_k`, `pass_rates` | built |
| 4 executable tasks in a Docker sandbox (C858) | `sandbox_decision`, `docker_argv`, `run_in_sandbox`, `log_trajectory` | built |
| 5 certificate-faithful rubrics, exploit test (C476, C479) | `certificate_problems`, `run_exploits`, `gate_problems` | built |
| 6 judge separate and audited, length bias (C561, C934) | `run_audit`, `audit_problems`, `length_bias` | built |
| 7 credit to the section (C40, C1442) | `criterion_scores`, `criterion_sections`, `section_credit` | built |

## The maintenance loop, ADR-40 refinement items 1 to 4

| Item | Where | State |
| --- | --- | --- |
| 1 one section per revision, inputs pinned (C244) | `skill_gate.one_section_clause` | built |
| 2 held-out gating and a rejected-edit buffer (C865, C392) | `skill_eval.heldout_block`, `skill_gate.heldout_clause`, `skill_gate.rejected_clause`, `record_rejection` | built |
| 3 cluster the corrections before applying them (C244) | `tools/corrections.py`, mounted into `pipeline/skill_revision.py` | built, lexically |
| 4 at most three modules (C848, C850) | `skill_gate.modules_clause` | built |
| 5 survival as the second axis (ADR-39) | `section_deltas[*].survival`, `corrections.from_survival` | reserved, Ursa writes it |
| 6 the self-refinement trap (C965) | stated in the dispatch, not enforceable in code | documented |

## What is deliberately weaker than the ADR asks for

**Item 3 clusters lexically, not with embeddings.** The organization funds no
embedding endpoint and the engineer charter forbids this seat from creating a
recurring cost, so the clustering is Jaccard overlap on content words: free,
deterministic, and worse at the one thing embeddings are for. The tool reports
its own failure mode. When the cluster count equals the correction count it says
the clustering found nothing and that this is the raw pile with a label on it,
which is what it says today against the single real consumer report in the
library. The upgrade is a ledger proposal dated 2026-10-05, and the test that
decides it is free.

**Items 5 and 6 of the harness are findings, not errors, unless a suite opts
in.** The eight suites were written before the rules existed. A gate that failed
them all would block every revision on a debt no revision created, which is how
a check gets turned off. `policy.require_certificates` makes certificates and
exploit answers errors for a suite that has said it carries them.

**Item 2 of the refinement loop reports `unknown` on an old result.** A result
measured before contract 2 has no held-out block. Failing it would block every
revision on the absence of a field nothing had written yet; `unknown` already
counts as not passing, so the gate is no weaker for saying which it is.

## The one thing that blocks all of it

As of 2026-10-05 no suite in the library can be run: all eight are missing
`policy.repetitions`, and `harness-engineering` additionally names nine
`sections` that are not headings of its own SKILL.md. `tools/skill_eval.py
--check` exits 1 and `--skill <any>` exits 1 before sending a call. The suites
are `skills/`, which the engineer seat may not write, so this is filed in
docs/ideas.md as `urgent` with the exact four-line fix. Until a skill-seat run
registers those policies, everything above is an instrument with nothing it is
allowed to point at.
