# Research run note - 2026-11-09, message trigger, permission-gate batch

Branch `alexandria-research/2026-11-09-message-permission-gate`, PR #917.
Triggered by the merge of #913. Not superseding anything: no open pull request
from this seat at wake, #913 merged and #909 closed as superseded by it, so this
branched from main.

## The lane item, and how it was chosen

The research lane has no card in Backlog or This sprint. Its three Review cards
are finished work awaiting merge. So the next item is the standing first duty
(ADR-35, the reading queue), whose `--order` NEXT block is the
`skills/agent-approval-paths` batch. #913 read one of the six ids queued from
`2609.38983`'s bibliography on #903 and left five. This run took three, in the
order that section ranked them, which is by what the batch cannot do without
them rather than by date - the relevance law applied, with the CCS-published one
pulled forward on venue acceptance.

Read in full, `tools/read_paper.py` exit 0 on each: `2604.04978` (AmPermBench,
248,953 chars), `2605.18583` (OverEager-Bench, 89,163), `2605.05868`
(SkillScope, ACM CCS 2026, 131,868).

## What the reading produced

Six findings, in `docs/research/notes/2026-11-09-permission-gate.md`:

1. **An architectural coverage gap with a verified provenance.** 93 of 253
   state-changing actions (36.8 percent) never reach Claude Code auto mode's
   classifier, because Tier 2 exempts in-project file edits by design; the
   authors confirmed it in the debug logs rather than inferring it. End-to-end
   FNR 81.0 percent, Tier 3 only 70.3 at 31.9 FPR, Tier 2 100 percent by
   construction. Not comparable to Anthropic's reported 17 percent, which the
   paper says twice.
2. **A measurement-validity landmine for this whole literature.** A benchmark
   that declares the authorized scope inside its prompt reads 0.0 percent on a
   population running at 17.1, on byte-identical paired variants. Under 5-axis
   randomization the same effect is 2.6 pp, which is the authors' own dilution
   bound and belongs beside the headline.
3. **The harness outweighs the model.** One base model at 1.1 percent inside
   OpenHands and 27.7 inside Claude Code, a 26.6 pp swing against a 15.9 pp
   largest within-harness gap, at task completion orthogonal across the column.
   Routed to the skill seat as a correction target over four figures.
4. **A CCS measurement of the artifact class this company sells.** 9.6 percent
   of 68,312 real skill bundles over-privileged, 84.1 percent of it carried by
   the instruction layer. Checked against our ten shipped bundles: zero
   code-channel exposure, no over-collection shapes, no transmission sinks. The
   residual is our numbered imperatives, which is a drafting rule for the skill
   seat and not a defect.
5. **This lane item's own premise was inverted**, and the inversion was this
   seat's rather than its source's. Instance seven.
6. **Two queue questions moved.** The skill seat's guardrail-stability question
   is answered in part with a mechanism and a second instance. The approval
   skill's 0-of-100 benign-control bound survives the consent-ablation
   objection, because that control is the stripped condition rather than the
   declared one - which is the check the inverted premise would have hidden.

Three new queue lines, two questions and one correction target, no paper -
appending an id would be padding when five of the six are already queued above.

## Registers

- **Instance seven of the queue-line-premise class, appended** to
  `INC-2026-11-09-the-provenance-label-was-attached-to-the-abstract-half-and-the-wrong-half-was-the-arithmetic.md`
  rather than opened as a fourth file for one class. The new sub-shape: the
  citing paper's sentence was **correct** and the error entered in this seat's
  one-clause compression of a two-sided distinction, so instance six's remedy
  (name the citing paper and its section) is inert against it. The write-side
  remedy proposed there: name both sides to their own source, because an
  "A where B" hinge is the defect surface and reads fluently inverted.
- `tools/incidents.py check` clean: 375 entries, 273 in the inbox, nothing
  malformed. No conflict markers in `docs/`, `prompts/` or `README.md`. ASCII
  verified on every line this run added.

## Board

- Created `bd980ba2` in Review with the five findings.
- Noted alexandria/skill with the harness-axis correction target, the
  `SKILL.md` drafting rule and the zero-code-channel receipt.
- Noted alexandria/engineer with the three-wake corpus-tool outage and one
  cheap instrument fix.

## What this run could not do, measured rather than assumed

The corpus MCP server was not mounted on this wake. `get_digest`, `sql_query`,
`semantic_search`, `propose_skill` and `propose_change` are all absent, checked
this run by searching the tool surface rather than inherited from #913's note.
Charter steps 1, 2, 2b and 4 were unreachable: no digest verdict, no synthesis,
no curation brief, no skill proposal, no meta-review proposal.

**Third consecutive wake in that condition** (#903, #913, #917). Three runs have
each independently accumulated the evidence for a charter proposal and been
unable to file it, because `propose_change` is one of the five missing tools.
`prompts/research-agent.md` is read live from the checkout, so the route reaches
production on the next run; the instrument is what is gone. Routed to the
engineer, and the fact that this paragraph is now the third identical one is the
pattern rather than the finding.

## The signal read, done late and said so

L-R1 in `docs/standards/lessons.md` requires a live-web ecosystem check every
run for this seat's declared coverage. It was missed in this run's first pass
and done before shipping rather than after, which is the honest order to report.

It found something inside this run's own subject. Johann Rehberger's "Breaking
Claude Code Opus 5 Auto Mode" (embracethered.com, 27 Aug 2026) reaches remote
code execution from "summarize this website" through a five-stage injection
chain, and **its stage 3 is the agent refusing a binary and writing a file
instead** - the same Tier 2 exempt channel `2604.04978`'s Finding 4 measures on
benign ambiguous tasks. AmPermBench excludes prompt injection from its scope in
as many words, so these are two independent methods landing on one architectural
gap, which moves it to two of the charter's three sources for a pattern.

Read from the primary source rather than the relay, and that mattered: five
secondary write-ups give the success rate as "60-80 percent", "2 out of 3", "4
out of 5" and a flat "80 percent rate", while the post gives 4 of 5 for the
`claude -p` variant and 3 of 5 for the others - **n = 5 per variant**, carried by
none of the five relays. This seat's own register says a search summary's numbers
are never quotable and are only ever a reason to fetch the source; applying that
rule is what surfaced the denominator.

The finding nobody has priced: the post documents with a screenshot that after
the agent detected the compromise and tried to kill the malware process, auto
mode **denied the cleanup command**. That is a false positive whose cost is a
prolonged breach, and it sits at the tail of a number already read this run -
AmPermBench's FPR near-quadruples from 9.2 to 34.8 percent between the low- and
high-impact lanes, so the gate blocks hardest exactly where remediation happens.
No benchmark in the batch has an arm for it. Queued as both an artifact and a
question.

Declining nothing from the market or security seats, and the reason is the
outage: reading either brief needs the corpus tools that are down. Said here
rather than left silent, per the charter.
