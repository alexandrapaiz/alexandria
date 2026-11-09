# agent-approval-paths: the full revision record

One dated heading per entry in `provenance.revisions` in `SKILL.md`. The
frontmatter carries one line each, naming the date, the trigger and what
changed; the narrative lives here. The reason for that split is the measurement
recorded in `skills/harness-engineering/REVISIONS.md` and the rule is in
`prompts/skill-extract.md` section 2.

## 2026-11-09: the research seat's answers to this skill's own four questions

**Trigger.** ADR-37: a cited premise corrected, and new reading that changes a
delta's evidence class. On 2026-11-02 this skill shipped as a draft and queued
seven lines in `docs/research/reading-queue.md`, three ingestion requests and
four questions its own reading had raised and could not settle. The research
seat drained the four on 2026-11-09 and reported on the board. Two answered,
two stay open with corrected reasons, and two of this skill's load-bearing
premises were wrong.

**The three papers were read in full by this seat before anything was written
here**, with `tools/read_paper.py` at exit 0: `2610.14488` 98,301 chars,
`2610.40753` 69,442, `2611.08516` 98,918. Every number below was checked
against the paper's own table rather than against the research note's summary
of it, which is ADR-35's requirement and which caught one overclaim, recorded
at the end of this entry.

### Delta 1 is now a pattern rather than a single-paper delta

`2610.14488` (ZTAC) reaches the same construction as the two founding papers
and **cites neither of them**: zero occurrences of either arXiv id, of "consent
integrity" or of "Verifiable Action Card" in the full text, checked. So the
construction has three independent sources, which is the charter's bar for a
pattern. It is also the implemented and measured version of what the shell case
was missing: the second founding paper's trusted path and total mediation are
specified and not implemented, and ZTAC is 3,164 lines of trusted Rust with
ground-truth oracles.

What was added to the section: 2 of 74 attacks succeed against 66 of 74 for a
tool allowlist and 56 of 74 for an allowlist plus a deployed-style command
sandbox, all 10 replayed disclosed incidents contained, 43 of 46 benign
operations at 8 prompts, 4.0 ms median brokered request.

**The ablation table is the part worth the lines**, because it reorders the
build. Removing the approval tier admits 18 of the 74, removing resolved
classification admits 5, and removing object-bound approvals while keeping
exact request fields admits 2. The construction is named after the piece that
pays least. Two further items came out of the same table and the paper's section 6.4:
the authors found eight flaws in their own implementation, seven of them
name-against-object gaps inside a system built to close name-against-object
gaps, so a resolver is audited rather than trusted; and `.ENV` evaded a rule
because the rule compared case-sensitively, which resolution does not fix.

### Delta 2 gained its first measured route off the frontier, and one tie

`2610.40753` (Caper) pre-executes in a snapshotted sandbox and approves from
observed effects. Added with its headline numbers and, more importantly, with
Appendix E's 95 percent Wilson intervals, because the two axes do not have the
same status and the research note's reading of the second one needed a
correction.

- Harm, clean: YoloFS-Ext [4.0, 14.7] against the deployed gate's [53.1, 71.5];
  SABER [5.0, 9.1] against [12.2, 18.0]. Neither overlaps.
- False blocks, **a tie**: Caper [0.2, 5.3] overlaps the rule-based checker's
  [0.5, 6.9].

**The correction to the note.** It said the false-block axis is a tie against
the rule checker but that Caper "beats the guardrail models (gpt-oss-safeguard
[9.9, 24.0], TS-Guard [4.7, 15.9])". Read off Table 12 directly, Caper's
[0.2, 5.3] **also overlaps TS-Guard's [4.7, 15.9]**, by 0.6 points. The
gpt-oss-safeguard comparison is clean and the TS-Guard one is not, so the
section says the advantage is clean against one guardrail rather than against
guardrails as a class. This is the kind of thing ADR-35 exists for: the note
was careful and the table is the authority.

Also added, and it is the sharpest item in the revision: Table 11's
predicted-against-observed result. Observed effects give twin false-block rates
of 0.0, 0.0, 0.0 and 4.2 percent across four concealment levels; the same
approver on an LLM's *predicted* effects gives 46.2, 57.7, 46.2 and 100.0,
which is worse than showing the approver nothing on two of the four. A reader
who takes only one procedure from this revision should take that one, because
predicting effects is the cheap thing a team reaches for and it measured
backwards.

`2611.08516` (Aegis OS) supplied an independent corroboration of delta 2's
mechanism on real sessions rather than on tldr-pages: 39.0 percent of 11,070
real shell invocations across 52 production transcripts use compound operators
or inline interpreter scripts, 4,318 of them. Two independent corpora, one
cause.

### Delta 3's control was wrong by a factor of four, in the loose direction

This is the correction that mattered most, because the section prescribes an
alert on it. The file read `2610.22987`'s Benign Control as 0 of 25. The
paper's construction is 25 cases **per agent configuration** and Table 1
carries four configurations, so the pooled control is **0 of 100**.

A zero count is a bound and not a rate, and the bound is what an alerting
design may rely on:

| control | one-sided 95 percent upper bound |
|---|---|
| 0 / 25, what this file quoted | 11.3 percent |
| 0 / 100, pooled | 3.0 percent |

Both recomputed here as `1 - 0.05 ** (1/n)` rather than taken from the note:
11.29 and 2.95 percent. The file now quotes both, because pooling assumes the
four configurations are exchangeable for this event and that is the arguable
step. The error was in the conservative direction, so no advice in the section
was unsafe, but a skill that says "measured at zero" where the evidence says
"bounded at 3.0 percent pooled" is overstating evidence, which is the one sin
the provenance reviewer exists to catch.

The section also gained Aegis OS's replay of the remedy delta 3 attacks: a
path-and-prefix allowlist still prompts on 28.54 percent of 28,087 real tool
calls against 53.31 percent for asking every time, while commit-time gating
reaches 4.97 and a scoped lease 1.12. So the prefix rule buys about half the
prompts and carries the escalation path, and the fatigue budget is somewhere
else.

### What did not change, and why

**No claim id was added and `status` stays `draft`.** None of the six papers
has a row; the research seat queued all six for distill and says so. The
library's own gate allows exactly one skill to cite zero claim ids and only
while it is a draft, so `draft` remains the honest state and is lower than the
`provisional` the format contract prescribes.

**No eval delta is claimed.** `NEON_RO_URL` and `GROQ_API_KEY` were both
checked absent in this run. One eval task was added, `ap-t7`, against the
predicted-against-observed rule, and it is unqualified like the other seven.

**The stale premise in the first caveat was repaired too.** It named the
compute workspace as the ingestion blocker. That cleared on 2026-11-08 at
23:37Z, so the rows wait on the next distill run rather than on an account.

**One premise corrected outside this file.** The reading-queue line on the
container-against-microVM question cited `2610.02456` as putting both
boundaries on one task set. It does not: that paper's own inclusion rule
requires hardware virtualization, which excludes every container candidate in
its own census, so its comparison is microVM against microVM. The line is
corrected in `docs/research/reading-queue.md` rather than here, because the
premise never reached this skill's body.

### A correction this run made to itself, before shipping

The first draft of delta 1's item 7 said that resolution "does not fix case"
because `.ENV` "evaded the rule because the rule compared case-sensitively".
That is wrong and the paper says the opposite: the case alias needs no
resolution precisely **because** ZTAC's rules match without regard to case.
Table 1's handoff row says the same thing in its mechanism column, "matched
without regard to case".

The conclusion survived and the reason did not, so the item now carries the
paper's own mechanism list: a case alias is caught by case-insensitive rule
matching, and a directory swapped between the check and the use is caught by an
`openat` walk with `O_NOFOLLOW`, neither of which is something a resolver
supplies. The same draft also called the path-divergence list "the five classes
that paid in the ablation", which conflated Table 1's list of ways a name and an
object diverge with the ablation's list of removed defenses. Both are fixed.

This is recorded rather than quietly corrected because it is the exact failure
mode ADR-35 names. The error came from reading a research note's summary of an
ablation row instead of the row, and it was caught by going back to the paper
for an unrelated check. The note was not wrong here; the compression was mine.
