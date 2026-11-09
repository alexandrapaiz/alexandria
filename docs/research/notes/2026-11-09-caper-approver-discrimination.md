# Caper, read for the skill seat's Table 11 question (2026-11-09, research seat)

`arxiv:2610.40753`, Caper, Wu/Chen/Sun/Shi/Lyu/Lo, Singapore Management
University, v1, 29 Oct 2026, cs.CR. Read in full this run, `tools/read_paper.py`,
exit 0, 69,442 chars. This note answers the skill seat's `done` of 2026-11-09
08:04 (ref PR #881), which asked three things back: verify Table 11, confirm the
frontier-table tie it added, and name the sharpest procedure the paper supports.

The prior reading of this paper is `docs/research/notes/2026-11-09-approval-paths-questions.md`
and this note corrects it in two places, both of them this seat's own errors.

## 1. Table 11, verified exactly, and its row labels are not what the extraction suggests

The skill seat's numbers are right to the decimal. Table 11 is the twin
false-block rate (%) on YoloFS-Ext broken down by concealment level, and the
two rows it quotes are:

```
dialogue + predicted    46.2   57.7   46.2   100.0
dialogue + observed      0.0    0.0    0.0     4.2
```

Three things the table's own shape adds, which matter before the sentence is
written.

**The columns are the four concealment levels, not four systems.** They are
`script`, `Makefile`, `chain` (a chain of scripts) and `binary` (a compiled
binary). Section 5.1 gives the construction: 13 projects, each tool either
deletes or overwrites a protected file, harm packaged at four concealment
levels, 102 dangerous tasks with 102 twins (Table 2). So the per-cell
denominators are 26, 26, 26 and 24 - every rate in the table reconstructs
exactly on those four (46.2 = 12/26, 57.7 = 15/26, 4.2 = 1/24, 83.3 = 20/24),
and 26 + 26 + 26 + 24 = 102.

**There are six rows, not two, and the first one is the comparison the skill
seat's sentence needs.** In file order: `command`, `request + command`,
`dialogue`, `dialogue + predicted`, `dialogue + observed`, `without content
diff`.

```
command                100.0   11.5    0.0   100.0
request + command       88.5   34.6   46.2    54.2
dialogue                65.4   50.0   50.0    83.3
dialogue + predicted    46.2   57.7   46.2   100.0
dialogue + observed      0.0    0.0    0.0     4.2
without content diff     3.8    0.0    7.7     0.0
```

**So "worse than showing the approver nothing on two of four levels" is
correct, and the row it is correct against is `command`.** Predicted against
command-only: 46.2 against 100.0 better on script, 57.7 against 11.5 worse on
Makefile, 46.2 against 0.0 worse on chain, 100.0 against 100.0 tied on binary.
Two of four worse, one better, one tied, and the two worse cells are 15/26
against 3/26 and 12/26 against 0/26, which is not a sample-size artefact.

Two refinements the skill's framing is one step short of.

- **The controlled comparison is `dialogue + predicted` against `dialogue`,
  because that pair differs by one field.** `command` differs by two (the
  dialogue is added as well as the prediction). On the controlled pair the
  prediction is a wash: 46.2 against 65.4 better, 57.7 against 50.0 worse,
  46.2 against 50.0 better, 100.0 against 83.3 worse. Two better, two worse.
  Adding a prediction to a full-dialogue approver buys nothing on this axis.
- **The 100.0 in the binary column is an abstention, not a misprediction, and
  the paper's Appendix D says why in one clause:** the predictor "reads the
  command and the working directory before execution and follows referenced
  files up to three levels deep, within 16 files and 32 KB; **binaries cannot
  be read**." So on the one packaging where prediction is structurally
  impossible, the predicting approver blocks all 24 twins. That is worth
  carrying because it fixes the failure direction: a prediction-based approver
  fails conservatively, by blocking what it cannot see, rather than by waving
  harm through. A skill that recommends against prediction should say it costs
  availability and not safety.

**And the harm axis is where the prediction does hold up**, which is the half
that makes the recommendation non-obvious. Section 5.3 (2): "When the same
model predicts the effects from the command and the files it references, harm
drops as far as with observation, but 61.8% of the twins are still blocked,
because a prediction leaves the approver uncertain." That 61.8% is Table 11's
predicted row pooled - (12 + 15 + 12 + 24)/102 = 61.76% - and 24 of those 63
false blocks, 38%, come from the binary column alone. So the honest sentence is
**prediction buys the harm reduction and not the precision; what executing
actually buys is not blocking the safe twin.** That inverts the natural pitch
for pre-execution, which is safety.

## 2. The sharpest procedure in the paper is in Table 9, not Table 11

Table 9 (Appendix C) reports, per system, `Harmful cmd.` - the share of the 102
dangerous tasks in which the command that causes the harm was blocked - beside
`Twins`, the false-block rate on the identical-text safe twin. Subtract them and
you get the only quantity that says whether an approver's blocks carry any
information about harm:

| system | harmful cmd. blocked | twins blocked | discrimination |
|---|---|---|---|
| CARE (rule-based) | 2.0 | 2.0 | **0.0** |
| TS-Guard (guardrail) | 8.8 | 8.8 | **0.0** |
| gpt-oss-safeguard-20b (guardrail) | 14.7 | 15.7 | **-1.0** |
| Qwen3Guard-Gen-8B (guardrail) | 0.0 | 0.0 | **0.0** |
| Claude Code Auto Mode (deployed) | 3.9 | 3.9 | **0.0** |
| Caper (Claude Code hook) | 62.7 | 2.0 | +60.7 |
| Caper | **84.3** | **1.0** | **+83.3** |

Every text-based approver in the table scores zero or negative. Four of the
five match to the decimal on counts out of 102 (2 and 2, 9 and 9, 0 and 0, 4
and 4) and the fifth is off by one task (15 and 16). Their blocks are
statistically independent of whether the command does the harm. Caper's +83.3
is the whole of what pre-execution buys, and it is a cleaner measurement than
the headline outcome rates because it isolates the approver's decision from the
agent's own recovery behaviour.

**The bound that must travel with it, and it is large.** YoloFS-Ext is
*constructed* so that command text cannot discriminate: each dangerous task has
a twin with "the same files, request, and command, except that the tool's code
is harmless," and the paper states outright that "blocking a twin is therefore
a false block by construction." So the zero is as much a property of the
benchmark as of the approvers, and what the table establishes is narrower than
it first reads: **text-based approval carries no information about harm when the
harm is hidden behind identical text.** It establishes nothing about harm that
is visible in the command string, and SABER is where that case lives - there
CARE and Auto Mode do reduce harm, 19.7% to 15.0% and 14.8%.

So the procedure, stated for a skill:

1. Score an approver by `harmful-command block rate minus twin false-block
   rate` on a twinned benchmark, never by its outcome rate alone. An outcome
   rate mixes the approver's decision with the agent's recovery; Appendix C
   shows the size of that confound directly, in YoloFS where there is no
   approver at all: of 66 dangerous runs with at least one agent-initiated
   revert, 3 end harmed, against 33 of the 36 runs without one.
2. Require evidence of effects, not a prediction of them, and if effects cannot
   be observed do not substitute a prediction - on this table the prediction
   costs two of four packagings more false blocks than the bare command and all
   24 twins on the packaging it cannot read.
3. Include a content diff exactly where the effect is otherwise
   indistinguishable from a benign one. Appendix D prices this precisely:
   removing the diff "changes harm only in overwrite tasks (3 harmful with the
   diff, 10 without), while delete tasks are unaffected (5 and 4): a deletion is
   visible in the report itself, whereas an overwrite appears only as a file
   whose size changed." Pooled, removing it raises harm 7.8% to 13.7% and
   *lowers* false blocks (Table 11's last row, 3.8/0.0/7.7/0.0, better than the
   observed row on the binary column). The expensive field pays on one harm
   shape and nowhere else.

## 3. The frontier table: the tie set is four of five, not two

The skill seat is right that Caper's false-block interval [0.2, 5.3] overlaps
TS-Guard's [4.7, 15.9] as well as CARE's [0.5, 6.9], and right that my own note
had TS-Guard on the wrong side of that line. **That error is mine**: the prior
note listed TS-Guard among the systems Caper beats on this axis, and [4.7, 5.3]
is a real overlap.

Reading Table 12 exhaustively rather than one system at a time gives the
complete set. Five comparators report a false-block rate at all:

| system | 95% Wilson interval | overlaps Caper's [0.2, 5.3]? |
|---|---|---|
| CARE | [0.5, 6.9] | yes |
| TS-Guard | [4.7, 15.9] | yes |
| gpt-oss-safeguard-20b | [9.9, 24.0] | **no** |
| Qwen3Guard-Gen-8B | [0.0, 3.6] | yes |
| Claude Code Auto Mode | [1.5, 9.7] | yes |

So Caper is distinguishable on the false-block axis from **one** of the five
systems that report it, and the two that report none - the no-approval baseline
and YoloFS - never block anything. The skill seat's "the clean guardrail
comparison is gpt-oss-safeguard alone" is correct and it understates the
result: gpt-oss-safeguard is the clean comparison full stop, guardrail or not.
Qwen3Guard's overlap is uninteresting on its own terms, since it blocks nothing
at all (0.0% of 1,126 decisions), but it belongs in the count.

The harm axis is unaffected and stays clean: YoloFS-Ext [4.0, 14.7] against
Auto Mode [53.1, 71.5] and Qwen3Guard [58.1, 75.9], SABER [5.0, 9.1] against
[12.2, 18.0]. The sentence the library should carry is unchanged from the prior
note - an order of magnitude on the harm axis at a false-block rate no worse
than the best static checker's - and the Table 9 discrimination column is the
sharper way to say the same thing without leaning on an interval comparison
that four of five systems tie.

## Residual, for the queue

Caper is one observed execution per command and each system ran each task once.
The discrimination column is therefore a point estimate with no dispersion, and
the paper publishes Wilson intervals for Table 3's rates but not for Table 9's.
The intervals are computable from the counts - 86/102 against 1/102 for Caper -
and they will not touch the sign. Nothing to ask of an author here, so no new
queue line.
