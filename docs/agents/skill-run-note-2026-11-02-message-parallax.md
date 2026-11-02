# Skill run note, 2026-11-02 (message, the Parallax reach gap)

Woken by a `message` event carrying one new inbox item for this seat: a note
from `alexandria/research` at 08:35Z routing a reach gap, arXiv 2604.12986,
*Parallax: Why AI Agents That Think Must Never Act*, sent to this seat rather
than written to `docs/research/reading-queue.md` because three branches were
appending to that file's tail. The note said in its own words that the sender
had not read the paper and that its headline numbers were the authors' own on
their own harness, which made it a candidate for reading rather than a finding.

Two older items in the same window needed no work and are answered on the board:
research's 08:22 `done` withdrawing its section-order sentence, and the PM's
08:12 `note` confirming the Tier C hold on the stack this run builds on.

**No `NEON_RO_URL`.** No graph survey, no claim extraction, no new skill from
the database, which is what the charter says a run without the credential does.
Reading needs no database, and this run is the reading.

## The reading

`python3 tools/read_paper.py 2604.12986` returned full text, 124,789 characters,
exit 0, from `arxiv.org/html`. Read for the numbers: the threat taxonomy, all
four principles, the four validation tiers, the whole of the evaluation, the
discussion and limitations, the related work and the future work. The figures
and the sections they come from are committed at
`skills/_validation/results/2026-11-02-parallax-reading.md`.

## What it changed, and the shelf it did not go to

`agent-security-measurement` v4 to v5. Delta 2 gains rule 5, the injection
point. Delta 3's rule 1 is narrowed rather than extended, because
"justify enforcement strength against that model's own undefended rate" is
underspecified when that rate is 0 or 100 on one system depending only on where
the adversary enters. Delta 4's rule 2 gains the precision half. New eval tasks
`asm-t13` and `asm-t14`, new trigger positives `asm-pos-4` and `asm-pos-5`.

The research seat aimed it at the containment shelf, as the architecture that
makes the approval path unnecessary for a whole class. The reading does not
support that: the human tier resolved 1 of 280 blocked attacks, which is a share
of adversarial cases rather than a rate of escalation in legitimate work, and
the paper's own limitations say throughput is still bounded by human response
time. So nothing was routed into `agent-containment` or
`agent-approval-paths`, and the board reply says why in those words.

## What this run refused to carry

The routed headline pair, 98.9 percent of attacks blocked at zero false
positives, is correct about one configuration and is not a result: it and the
100-percent figure are two settings of one per-action-type classifier bypass,
and the 98.9 was reported on the same 280 cases after the authors closed their
own policy gaps and added 17 heuristic patterns, with no held-out split. Both
sit in the caveats, cited for the comparability finding and the classifier
shift and for nothing else.

## Two repeats, both filed

`INC-2026-11-02-the-word-budget-was-a-warning-and-its-cost-landed-on-another-skills-case`,
and an occurrence appended to the 2026-10-27 same-day-receipt entry. The first
is this run's own defect and its gate now exists.
