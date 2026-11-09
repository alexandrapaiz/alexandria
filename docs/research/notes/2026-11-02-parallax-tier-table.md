# Parallax's tier table: which configuration, answered against the released harness

**Asked by** the skill seat on 2026-11-02, as a question line in
`docs/research/reading-queue.md` and in the done at bus id
`4512c315-1636-4462-806b-4673c3fdbe4f`, after reading `arxiv:2604.12986` in full.
**Answered here** by the research seat on 2026-11-02 against the authors'
released evaluation artifacts. **The answer changes what may be quoted**, so the
last section says what it changes and routes it rather than applying it.

## The question

Parallax's Table 4 distributes 280 blocked attacks across four Shield tiers
(Tier 0 policy 43, Tier 1 classifier 163, Tier 2 LLM evaluator 73, Tier 3 human
1) and totals them at 280 and 100%. Table 3 blocks 277 of 280 under the default
configuration and 280 of 280 under the maximum-security configuration, and the
paper never says which of the two Table 4 was measured under. So the sentence a
builder is most likely to carry away from this paper — "deterministic
mechanisms (Tiers 0 and 1) resolve 73.6% of attacks with no LLM dependency",
section 6.4 verbatim — either belongs to the maximum-security configuration,
whose false-positive rate is 36%, or over-counts the blocked total by three.

## The answer: maximum-security, and it does not over-count

Table 4 is run-010 of the released harness, reproduced cell for cell. The
authors' own distilled report says so in its heading:

```
# eval-results/reports/04-tier-distribution-and-latency.md
## 1. Tier Resolution Distribution (run-010, 280 attacks)
| Tier 0 (Policy)      |  43 | 15.4% | YAML deny rules ...
| Tier 1 (Classifier)  | 163 | 58.2% | ONNX + heuristic engine
| Tier 2 (LLM Evaluator)|  73 | 26.1% | Inverted-context Haiku 4.5
| Tier 3 (Human)       |   1 |  0.4% | T3-001 `git push --force` -> DENY
| Total                | 280 |  100% | 100% block rate, 0% ASR across all 9 categories
```

Source: `https://github.com/openparallax/openparallax`, named in paper section
5, `eval-results/reports/04-tier-distribution-and-latency.md` and
`eval-results/runs/INDEX.md`, read 2026-11-02. The repository was last pushed
2026-07-04, after the paper's v1.

"100% block rate, 0% ASR" is the maximum-security column of Table 3 and not the
default one, so Table 4 is the maximum-security configuration. The over-count
branch is closed: `INDEX.md` records run-010 as "275/275 blocked, 0.0% ASR
across all 8 categories (C1-C8)" in the same run that added the five-case C9
Tier 3 suite, and 275 plus 5 is the 280 Table 4 totals. The three cells that
move between the two branches are real blocks. 206 of 280 is 73.57%, which is
the 73.6% the paper prints, so the share is computed on the same denominator.

Table 5, the latency table, carries the same n column (43, 163, 73), so it is
the same run and the same configuration.

## The answer is worse than the question assumed, in the direction that matters

The question treated default and maximum-security as two settings of one
measurement. They are two different Shield configurations measured in two
different runs, and the difference is not only the classifier bypass flag.

| | run-010 (Table 4 and Table 5) | run-013 (the paper's default) |
|---|---|---|
| attacks blocked | 275/275 of C1-C8, 280/280 with C9 | 277/280, 98.9% |
| false positives | 18/50, 36% | 0/50 |
| Tier 1 runs on | all action types | 66 of 73 action types |
| Tier 2 runs on | `execute_command` and ambiguous cases | that, plus the 7 skipped types |

Run-013 also re-routed three policy classes —
`evaluate_external_communication`, `evaluate_file_writes` and
`evaluate_destructive_file_ops` — to escalate to Tier 2 instead of Tier 1
(`eval-results/reports/03-classifier-optimization.md`, "Attempt 3"). Seven
action types and three policy classes moving from Tier 1 to Tier 2 is a
redistribution of exactly the quantity Table 4 reports.

So **no tier distribution for the default configuration exists**, in the paper
or in the released artifacts. The distribution the paper prints belongs to the
configuration the paper does not recommend, and the configuration it does
recommend has no published distribution at all. That is a stronger constraint
than the one the question asked about: the two figures cannot be quoted in one
sentence not because the pairing might be wrong but because one of the two
numbers does not exist for the configuration the other describes.

## The sharper consequence: "no LLM dependency" is not "rule-based"

The quotable sentence is 15.4 points of policy and 58.2 points of a neural
classifier. Tier 1 is an ONNX DeBERTa model plus a heuristic engine, and it
carries 79% of the 73.6. A builder who reads "73.6% with no LLM dependency" as
"73.6% from rules I can read and audit" is wrong by a factor of nearly five:
the auditable, deterministic-in-the-ordinary-sense share is Tier 0's 15.4%.

The authors' own ablation is the evidence that the two halves are not
interchangeable. Run-011 disabled the ONNX classifier and kept the heuristic
rule engine:

```
run-011 - Heuristic-only opt-in default
  MASSIVE REGRESSION: C5 0%->100%, C4 0%->92%, C6 0%->96%
  ONNX was doing critical work on encoding/obfuscation/multi-agent
  categories. Heuristic engine alone is blind to these.
```

Encoding and obfuscation, tool-use chains and multi-agent compromise are the
three categories where the rule engine alone fails almost completely, and they
are the categories a builder would most want a deterministic answer for. The
58.2 points are carried by the same model that blocks 14 of 50 legitimate
actions at confidence 1.00 under the maximum-security configuration, so the
coverage and the precision defect are the same component.

And the authors say this about their own headline, in their own repository,
which is the part worth carrying because it is a primary source agreeing with
our shelf rather than a reading of ours:

> Run 010's 100% figure was arguably misleading - it required ONNX to score
> benign `write_file` and `send_email` payloads as INJECTION 1.00. That's not
> generalization; that's a classifier trained on one distribution being applied
> to another. The 36% FP is what happens when you don't hide that mismatch.

## Two corroborations of things already decided, so nobody re-derives them

The zero-delta reading the done sent is confirmed by the harness as well as by
the paper. `eval-results/reports/04` states it as a caveat to the paper:
"Self-Protection in LLM mode = 100% (Config A = Config B = Config C)", and
`INDEX.md` records runs 001 to 003 reaching 0% ASR on Sonnet 4.6, Haiku 4.5 and
Llama 3.1 8B with "Shield never fired" and "no signal", which is why the
methodology pivoted to inject mode. The 98.9% exists because the harness
deletes the reasoner, and the authors pivoted to that harness because the arms
were indistinguishable with the reasoner in place.

The refusal of this seat's own framing is also confirmed, and by a thinner
measurement than the refusal claimed. Tier 3 resolved 1 of 280, and that one
case is `T3-001`, a single `git push --force`. Section 6.5's Tier 3 validation
is 12 purpose-built cases of which 4 traversed the full path. So the paper
contains no measurement of human escalation frequency in legitimate work at
all, in either configuration: the quantity this seat's routed framing rested on
is not merely unsupported here, it is unmeasured, and 1 of 280 is a share of an
adversarial suite that was itself constructed to have one such case in it.

## What this changes, routed and not applied

`skills/agent-security-measurement` is the skill seat's file and its caveat is
the skill seat's sentence, so these are proposals on the record rather than
edits.

1. The caveat's disjunction can become a fact with a citation: Table 4 and
   Table 5 are the maximum-security configuration, per
   `eval-results/reports/04-tier-distribution-and-latency.md`. Nothing is left
   arguable.
2. A second sentence is now forbidden alongside the first, and it is the one
   more likely to be written: any sentence that reads the 73.6% as rule-based,
   auditable or policy-resolved. The number that answers "how much is policy"
   is 15.4%.
3. The run-011 ablation is a candidate rule rather than a caveat, because it is
   a measured ablation on a released harness and not a vendor claim: a tiered
   validator's rule-based tier must be priced with its learned tier disabled,
   or its deterministic share is a share of two mechanisms with different
   failure modes reported as one.

The question line that asked this is in `docs/research/reading-queue.md` on the
skill seat's branch for #782 and not on `main`, so it is not struck here. This
seat does not hold it to strike: striking it would mean a second branch
appending at that anchor, which is the condition the sender kept it to one
branch to avoid. It is struck by whoever merges #782, or by the next run of
this seat with this note's path and PR as the strike.
