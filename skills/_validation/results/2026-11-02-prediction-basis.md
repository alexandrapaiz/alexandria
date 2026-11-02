# Prediction basis, 2026-11-02

Written by `skills/_validation/prediction_basis.py`, which reads the nine eval
suites and nothing else. It is a label audit, not a measurement of any skill.

```
   1 of 102 predictions: observed-bare-run
       harness-engineering/he-t1: the 2026-09-12 A/B trial of the unaided arm, recorded in this skill's provenance
   3 of 102 predictions: this-repository-history
       context-window-engineering/cwe-t2: the reason given is a change made to this suite on 2026-10-26, not anything about a subject model
       context-window-engineering/cwe-t8: the reason given is that this skill itself asserted the wrong thing until 2026-10-26
       context-window-engineering/cwe-t11: the reason given is that this suite's own skill asserted the wrong thing until 2026-10-26
  98 of 102 predictions: authored-judgement

1 of 102 predictions have ever been checked against a run of the unaided arm. Every delta this library reports rests on the other 101.

Every prediction says what it rests on. Exit 0 does not mean the predictions are right, only that none of them is pretending.
```
