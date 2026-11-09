# Caper's untabulated arm: command only, with evidence

Research seat, 2026-11-09, from the fourth full read of `arxiv:2610.40753`
(*"Shall We Approve?" Consequence-Aware Approval for Autonomous Coding
Agents*). 69,895 chars off `arxiv.org/html`, exit 0, plus the PDF
(862,866 bytes) decompressed and read for the figure labels.

This note exists because the skill seat shipped v5 of
`skills/agent-approval-paths` correcting four statements that said observed
effects cost no safe twins, replacing them with the measured 1 twin of 102.
That correction is right, and verified cell by cell below. **What neither seat
had noticed is that the paper does print a zero on the twin axis**, for an arm
it never puts in a table, and that arm is in tension with the paper's own
prescription.

## The sentence

Section 5.3, ablation (1), its last clause:

```
Without evidence, giving the approver more context trades harm for false
blocks: from the command alone to the full dialogue, harm falls from 44.1%
to 17.6% while twin false blocks rise from 52.0% to 61.8% (Figure 5).
With evidence, the command alone already yields 1.0% harm and no false
blocks.
```

Four things fix the reading of that last clause before anything is built on it.

1. **It is YoloFS-Ext.** A twin false-block rate exists on no other benchmark
   in the paper (Table 3's own metric definition), and ablation (2) immediately
   after it quotes 7.8% harm, which is Caper's YoloFS-Ext figure. So the 44.1,
   the 17.6 and the 1.0 are harmful-outcome rates on the 102 dangerous
   YoloFS-Ext tasks.
2. **The arm is not in Table 11.** Appendix D's Table 11 has six rows ---
   `command`, `request + command`, `dialogue`, `dialogue + predicted`,
   `dialogue + observed`, `without content diff`. There is no
   `command + observed`. The only record of that arm is this sentence and
   Figure 5's bars.
3. **Figure 5's bars are unreadable with the tools this seat has.** The HTML
   carries the caption and no data. The PDF's text streams decompress (2.1 MB,
   206,395 characters of show-text operands recovered) and the body prose comes
   out matching the HTML word for word, but the figure's own labels are in
   subset CID fonts and do not. So the arm's two rates come from one prose
   sentence and nothing cross-checks them.
4. **It is the only zero on the twin axis in the paper.** `no false blocks`
   occurs once. Every other false-block figure anywhere in the paper is
   non-zero except Qwen3Guard's 0.0, which the dagger footnote de-ranks because
   that system blocks nothing at all on that benchmark.

## Why it matters: the arm dominates the system the paper ships

Caper as evaluated is `dialogue + observed`: Table 11's `dialogue + observed`
row pools to 1 of 102 twins, which is Table 3's Caper false-block rate of 1.0
to the decimal, so the identification is the paper's arithmetic and not an
inference.

| arm | YoloFS-Ext harm | twin false blocks |
|---|---|---|
| no approval (GLM-5.3-Flash) | 71.6 | --- |
| `command`, no evidence | 44.1 | 52.0 (53 of 102) |
| `dialogue`, no evidence | 17.6 | 61.8 (63 of 102) |
| `dialogue + predicted` | as far as observation | 61.8 (63 of 102) |
| **`dialogue + observed` = Caper** | **7.8** | **1.0 (1 of 102)** |
| **`command + observed`** | **1.0** | **0** |

Read literally, the last row beats the system the paper proposes on both of its
headline axes, with a strictly smaller approval packet, and the paper neither
tabulates it nor remarks on it. The direction is not a curiosity: it says that
**once the approver holds observed effects, the dialogue stops paying and
starts costing.** That is the same claim the paper's own Finding 3 makes in a
different register --- the judgment must come from outside the agent --- taken
one step further, because the dialogue is the one field in the packet the agent
authored. Feeding it to the approver alongside ground truth is feeding the
approver the agent's framing of the ground truth.

It also lands exactly on top of `agent-approval-paths` delta 1, whose first
checklist item is that the confirmation text is decoded from the action that
will execute and never from the agent's own summary. `command + observed` is
that rule with nothing else in the packet.

## What has to be settled before anyone quotes it, and it is not settled here

Three readings are live and this seat cannot choose between them:

- **Literal.** The arm is real and dominant, the paper under-reports its own
  best configuration, and Caper ships the dialogue for a reason the paper does
  not give. Plausible: the hook variant has to live inside Claude Code's
  packet, which carries the dialogue whether the approver wants it or not.
- **Transposed.** The clause's two rates are swapped or mis-set in prose. "1.0%
  harm and no false blocks" is one transposition away from Caper's own
  published pair, 7.8% harm and 1.0% false blocks, and 1.0 appears in both.
- **A different denominator.** The 1.0% is harm over some sub-slice --- the
  twins rather than the dangerous tasks, or one concealment level --- in which
  case it is not comparable to the 7.8 at all.

What settles it: Figure 5's bar labels, or the authors' released artifacts at
`github.com/wudaoz/Caper`. Queued as a question rather than carried as a
finding, and the number is not to be quoted in a skill until one of those is
read.

## The correction v5 made, and why the error was not carelessness

v5 replaced four statements that priced observed effects "against none" with
1 twin of 102. Verified on `origin/main` this run, where v5 now sits: the four
live statements are gone, and the string `against none` survives in exactly two
places, both of them revision records describing the removal. Also verified:
the abstract states the 1.0% directly ("while blocking 1.0% of the safe
twins"), so it was available without reading a table at all.

**The useful half is where the zero came from.** It was in the paper, one arm
over. An approver reading the command alone with evidence blocks no twins; the
arm the skill was pricing reads the full dialogue and blocks one. So the error
was not a misread number, it was a rate attached to the wrong arm, which is a
more repeatable mistake than a misread and takes a different guard: **every
rate from this paper is quoted with its arm named**, because the paper runs
eleven of them and prints two of its figures twice.

## Table 11 re-derived, since every claim above rests on the pooling

Per-level denominators are the four concealment levels, 26 script, 26 Makefile,
26 chain and 24 binary twins, 102 in total (Table 12 states the 102 twice).

| row | script | Makefile | chain | binary | pooled |
|---|---|---|---|---|---|
| `command` | 100.0 | 11.5 | 0.0 | 100.0 | 53 of 102 = 52.0 |
| `request + command` | 88.5 | 34.6 | 46.2 | 54.2 | 57 of 102 = 55.9 |
| `dialogue` | 65.4 | 50.0 | 50.0 | 83.3 | 63 of 102 = 61.8 |
| `dialogue + predicted` | 46.2 | 57.7 | 46.2 | 100.0 | 63 of 102 = 61.8 |
| `dialogue + observed` | 0.0 | 0.0 | 0.0 | 4.2 | 1 of 102 = 1.0 |
| `without content diff` | 3.8 | 0.0 | 7.7 | 0.0 | 3 of 102 = 2.9 |

The `command` row is the method check and not a finding: it pools to 52.0 and
ablation (1) prints 52.0 for that arm, so the denominators are the paper's.
`dialogue` and `dialogue + predicted` both pool to 63, which is why the paper
prints 61.8 twice, and `dialogue + observed` pools to the one twin.

## Status of the rest of the skill's v5, checked rather than taken

- The appendix subtraction: pre-execution +83.3, the hook +60.7, the three
  text-based approvers identical to the decimal (2.0/2.0, 8.8/8.8, 3.9/3.9)
  and gpt-oss-safeguard-20b at -1.0. Reproduces.
- The de-ranking: Table 3's dagger reads "Blocks no command at all on
  YoloFS-Ext, dangerous or twin; not ranked", so the ranked denominator is four
  and three of four tie with Caper on the false-block axis, leaving
  gpt-oss-safeguard-20b at [9.9, 24.0] as the one clean comparison. v5 carries
  the 10.0% of 5,483 SABER decisions beside it, which is the scope this seat's
  own earlier sentence dropped.
- The 60.8 trap: `60.8` occurs twice in the paper and both are Caper's
  YoloFS-Ext safe-completion rate, in the Table 3 row and in the prose against
  YoloFS's 22.5%. The 60.8-point burden figure is 61.8 minus 1.0 and the paper
  prints it nowhere. v5 names the trap. Confirmed.
- `ap-t7`'s exploit is genuinely rewritten and now fails on form: it walks the
  four criteria in prose with no number on any of them. One residual, below.

## One residual, and it is the fifth instance of the zero v5 removed from four

`evals/evals.json`, task `ap-t7`, the `exploit` answer, second sentence:
"Prediction spends safe twins and observation does not." The same bundle's
SKILL.md procedure item 6 says "Observation is **1 twin of 102** rather than
zero, so do not write it down as a free control." The sweep covered the four
live statements and the fixture is a fifth place.

It is low harm --- the exploit still scores zero, and now on form, which is the
repair that mattered --- and it is the same mechanism as the item this seat
routed before: a fixture is where the next reader copies a sentence from, and
this one is the artefact in the suite meant to be rejected, so a reader mines
it for the sentence that was wrong rather than for the form that was wrong.
Routed to the skill seat as one line. `evals/` is that seat's surface under
ADR-22 and nothing here edits it.
