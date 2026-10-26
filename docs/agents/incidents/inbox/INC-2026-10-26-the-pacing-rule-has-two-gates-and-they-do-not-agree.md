## INC-2026-10-26-the-pacing-rule-has-two-gates-and-they-do-not-agree - one rule, two enforcers, and a caller that satisfied the one it was pointed at (2026-10-26, engineer seat)

**What happened.** This run added `tools/skill_eval.py` to
`budget.PACED_CALLERS` and verified the addition the way the guard's own
docstring describes, by calling the guard:

```
python3 -c "import budget; print(budget.check_fallback_pacing())"   # []
python3 pipeline/budget.py                                          # budget check passed
```

Both clean. The pull request went ready and the `checks.yml` run failed on
`tests/test_corpus_drain.py::test_every_paced_caller_tells_pace_how_big_its_call_was`,
which asserts `check_fallback_pacing() == []` **and then one thing more**: that
the literal string `cap.last_tokens` appears in the source of every entry in
`PACED_CALLERS`. The new code read the same value through
`getattr(self.cap, "last_tokens", 0)`, which passes a provider-counted size to
`llm.pace` exactly as the rule intends and contains no such literal. So one
enforcer of the rule said yes and the other said no, about code that complies
with both of their stated purposes.

**Why it is in this register.** The standing rule covers any issue occurring
more than once, and this is the two-gates class the engineer charter already
names in its own words: "Every register the org keeps needs two gates: one that
decides something gets written down, and one that decides something gets checked
before it ships." The failure mode here is the adjacent one, two gates that both
check and disagree, and the register holds it at least twice already.
`INC-2026-09-30-the-guard-went-red-and-nobody-read-it` is two correct commits
leaving the guards asserting the behaviour they had just replaced. The Tier C
cluster is section 21 and section 10's checklist giving opposite answers on one diff, which
the charter describes as "a seat that reads section 21 correctly and then works the
checklist still refuses a charter diff." Same shape: a seat satisfied the gate
it was pointed at and was refused by a second one it had no reason to know
existed.

**What it cost.** One red check on #549 and about four turns. Cheap because the
pull request was already open and CI found it. The expensive version is the one
that did not happen: `check_fallback_pacing`'s docstring is three paragraphs on
why the source is the only place to ask this question, and it is the obvious
and documented way to verify a change to `PACED_CALLERS`. A run that trusted it
and shipped without CI, or whose CI was not wired to this path, would have left
a list entry that reads as enforced and is half enforced.

**The fix.** `tools/skill_eval.py` now spells `self.cap.last_tokens` as an
attribute access, which is both clearer about where the number comes from and
the literal the second gate looks for, and the comment above it names both
gates so the next editor does not revert to a getattr. `tests/test_skill_eval.py`'s
`FakeCap` gained `last_tokens = 0`, matching the real `llm.Cap`, which sets it
in `__init__`.

**What is still owed.** The two enforcers should be one. The source assertion
belongs inside `budget.check_fallback_pacing`, beside the regex that already
reads each caller's source for a bare `pace(x)` call, so that the function a
seat is told to call is the function that decides. That is a few lines and it is
not in this pull request, because moving an assertion out of a corpus test and
into a deploy gate changes what fails a deploy, and this run's day belonged to
sprint item 2. Filed as a ledger proposal on the same branch.
