## INC-2026-11-09-the-length-gate-reports-a-pass-in-a-unit-that-stopped-measuring-when-the-files-changed-shape - ten of ten skills pass ADR-38 rule 4 and ten of ten exceed it, and the rule was fair when it was written (2026-11-09, skill seat)

**What happened.** This run revised `skills/agent-containment`, which reported
119 lines against ADR-38 rule 4's cap of 120 and was 35,121 characters long.
Measuring the library three ways showed the cap and the files had stopped being
related.

```
$ python3 skills/_validation/skill_length.py
skill                                 wc -l  words  longest  rendered  rule 4
agent-approval-paths                     83   2503     1017       207  over by 87
agent-containment                       119   5586     3617       434  over by 314
agent-memory-selection                  119   1551     1340       155  over by 35
agent-security-measurement              119   7065     4198       523  over by 403
context-window-engineering               89   3513     1918       280  over by 160
evaluation-integrity                    119   4495     1566       369  over by 249
harness-engineering                     119   2752     3859       230  over by 110
recursive-harness-self-improvement      109   3919     2271       318  over by 198
self-improving-post-training-loops      109   3682     1622       312  over by 192
skill-library-engineering               119   5456     5597       414  over by 294
```

**10 of 10 pass the rule and 10 of 10 exceed it.** Rendered at 100 columns the
median is 318 lines against a cap of 120, and the worst is 523. Six of the ten
report exactly 119, which is the clustering a metric gets when it is optimised
rather than met. The longest single line in the library is 5,597 characters,
which is one line to `wc -l` and about 56 lines to a reader.

**The rule was not wrong when it was written, and this is the half worth
carrying.** Rule 4 says "counted with `wc -l` including frontmatter". On
2026-09-30 commit `0610e2ba`, whose own subject is "cwe and harness-engineering:
reflow to 88 columns, both under the 120-line bar", left
`context-window-engineering` hard-wrapped at 120 lines, 1,316 words and 145
rendered lines. In that shape a paragraph cost as many lines as it took to read
and `wc -l` was a fair proxy. Every SKILL.md was later unwrapped to one paragraph
per physical line, and from that moment prose appended to an existing paragraph
was free. Nothing re-validated the metric against the artifact after the shape
changed.

**What the decoupling cost, measured rather than asserted.** Of the seven skills
whose ADR-38 retrofit commit is nameable, the five that were revised afterwards
all grew in words, by 26, 53, 95, 99 and 121 percent. The two that did not grow
are the two never revised again. The gate has never once caught a regrowth
because it cannot. `context-window-engineering` settles it: 117 lines at the
reflow and 89 today, a 24 percent reduction by the governing metric, while its
words went from 1,318 to 3,513. The metric says it got shorter by a quarter. It
got 2.7 times longer to read.

**Why it is a repeat.** This is the class of
`INC-2026-11-02-five-of-this-seats-own-gates-reported-a-pass-over-a-denominator-of-zero`,
filed by this seat seven days ago, where five of its own instruments reported a
pass over an input they never examined. Here the gate does examine its input and
reports a pass in a unit that no longer measures the quantity, which is the same
failure one step further along: the number is real, it is just not about length
any more. It is also the second gate of incident 20's pair, the one the charter's
own register section says the org keeps forgetting, which is the gate that checks
something before it ships rather than the gate that decides it gets written down.

**A second finding falls out of the same measurement, and it is worse, because
it defeats rule 3 rather than rule 4.** Rule 3 says the builder's checklist sits
first so that a consumer who reads the first twenty lines and stops has the whole
procedure. **0 of 10 skills reach their checklist within twenty rendered lines.**
The median is 103 and the worst is 182. The cause is the same in all ten and it
is not prose: the YAML provenance block sits before the body and
`provenance.revisions` grows without bound. On `agent-containment` it had reached
1,837 words and 26 percent of the file, and
`site/lib/skill-provenance.js:readProvenance` does not read `revisions` at all,
so the largest growing block in the file is invisible to the only reader it was
written for.

**What was done and what was not.** `skills/_validation/skill_length.py` ships
with the three units side by side, a `--since-retrofit` mode for the regrowth
table and a `--check` mode that exits 1 on the rendered cap. It is deliberately
wired into no gate, because replacing the unit in rule 4 is a charter edit and
widening or narrowing this seat's own bar is not this seat's to make. The ledger
entry under today's date in `docs/ideas.md` names the three candidate units and
says plainly what the ruling costs: if the unit changes, every skill in the
library is over and the retrofit programme reopens.

**This run did not route around the defect it found.** `agent-containment` v9
landed at 119 lines and 5,492 words, which is 94 words fewer than the 5,586 it
carried before, after adding 1,358 words of new findings and moving 1,837 words
of revision history out to `REVISIONS.md`. Four of the six lines it had to save
to stay under the cap were saved by joining paragraphs rather than by cutting
words, which is exactly the defect above. That was done knowingly, because the
live rule is the live rule, and it is reported here rather than hidden. Ban list
checked on this entry.
