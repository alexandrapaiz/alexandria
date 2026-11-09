# evaluation-integrity: revision history

Every revision this skill has had, newest first, verbatim. This file exists for the
reason `skills/agent-containment/REVISIONS.md` exists: the history had reached 643
words inside a 120-line budget, and `site/lib/skill-provenance.js` reads eight
provenance fields of which neither `revisions` nor `revised` is one, so the library's
own differentiator was the receipt no consumer could see.

Nothing here was rewritten in the move. `SKILL.md` keeps the newest entry and points here.

## 2026-11-01

2026-11-01 (ADR-38 rule 4, the length bar): 477 lines to under 120, ten sections to five deltas, the checklist first. This file was the longest in the library and the last of the retrofit queue still carrying the old shape. The retrofit was rebuilt against this file's 2026-10-27 text rather than merged from branch alexandria-skill/2026-10-26-message-wake-path (#582), which drafted the same retrofit on 2026-10-24 and has been held since on the Tier C path check. Merging that branch produced eight content conflict hunks in this file, because the 2026-10-27 corrections landed after it was written, so resolving toward it would have reverted them. Both corrections are carried forward intact: the 102 refined instances keep their 14.0 percent denominator, and the history channel keeps its structural reading from SWE-Bench Pro section 4.1. Cut: the magnitude of the pressure effect, the long-horizon world-stress design, and the scheming detector's own F1, all three findings about an agent under test rather than about an instrument, which is this skill's stated subject. All three are queued in docs/research/reading-queue.md for agent-security-measurement. No claim id was dropped and all eleven papers are still cited. The cut is named in the last caveat rather than in a section of its own, because the eval harness exempts only Apply and Caveats from its section-coverage check, so a heading of its own would have shipped an unexercised section.

## 2026-10-27

2026-10-27 (ADR-37 maintenance, ADR-35 the paper wins): the research seat drained the 2026-09-30 reading-queue batch and reported this file clean with one upgrade owed (docs/research/briefs/2026-10-26.md section 9), and the upgrade was verified here against the full text of arxiv.org/abs/2509.16941 before being applied. Two changes, neither of them a correction to a number. The 102 refined instances now carry their denominator, 14.0 percent of the 731 public instances, because a reader deciding whether to audit a benchmark needs the rate and not the count. And the history channel is named as structural rather than incidental: every SWE-Bench Pro instance is built from a pair of consecutive commits, where the newer commit is the fix, so the answer is in the history by construction and closing that channel is not optional hardening (section 4.1, section 3.3). `status` moved from `active` to `provisional`: ADR-38 rule 7 earns `active` on a positive differential delta on the benchmark subject, this skill's `validated` field is empty and none of its eval tasks has been run, so `active` was asserting a measurement that does not exist. This file is 477 lines against ADR-38 rule 4's cap of 120. It is in the retrofit queue, this run corrected text rather than retrofitting it, and the cap is reported rather than quietly carried.

## 2026-09-30

2026-09-30 (runner length guard): description cut from 151 words to 148, under the 150-word budget that prompts/skill-extract.md has stated since 2026-09-24 and that nothing measured until this run. Wording only, no coverage change: "turn out to be ambiguous" became "are ambiguous". Caught by the new length check in trigger_test.py, on that check's first run, which is the evidence incident 31 asked for.

## 2026-09-30

2026-09-30 (ADR-38 retrofit, owner directive): per-section Validation tags, an Apply checklist, and caveats that name their floor. The tagging pass found one section, partial monitoring, whose claims were attached to a task that tested none of it, so eval task ei-t11 was written and the suite moved to version 2.

## 2026-09-30

2026-09-30 (ADR-36/ADR-37 trigger 1, claim deprecated): claim 288 entered deprecated_claims, contradicted at 0.75 by claim 289 from the same paper. Re-read arxiv.org/abs/2609.09219 in full. Claim 288 is accurate and is kept; claim 289 is a misreading of the paper's Gate 3 table and is filed for correction. The section 'Auditing a result you did not produce' now separates the protocol's two senses of recovery, which is the overload that produced the false edge, and adds that both of the paper's real-data feedback decisions were Inconclusive.

## What the length rule cut, moved here 2026-11-09

`SKILL.md` carried this as its second-to-last caveat in full until 2026-11-09, when a
new finding needed the line. It now names the cut in one sentence and points here.

- **What this file no longer carries, cut 2026-11-01 under the length rule.** The magnitude of the pressure effect (ordinary user pressure raising rule-violation rates by an average of 65 percent across 22 models, with the strongest assistants still misapplying a compliance rule on 6 to 10 percent of items), the long-horizon world-stress design (multi-agent worlds run over days with a phishing campaign on days four to seven, a misinformation claim on day ten and a memory breach on day thirteen, no world fully resilient, and alignment not compositional across mixed populations), and the scheming detector's own F1 of 90.73 percent. All three are findings about an agent under test rather than about an instrument, which is this skill's stated subject, and all three are queued in `docs/research/reading-queue.md` for `agent-security-measurement`. What survives from those three papers is their instrument-facing half, in delta 3 and delta 4: the item audit, the realism floor, the separate axes, and the monitoring scope.
