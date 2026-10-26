## INC-2026-10-26-the-practices-prompt-has-asked-whose-number-it-is-since-september-and-the-column-could-not-hold-the-answer - a quoted number and no number at all have graded the same for 26 days (2026-10-26, engineer seat)

**What happened.** `prompts/distill-practices.md` has told the model, since the
day it was written, to answer `measured` with `false` "when the only numbers
present were quoted from somebody else." That sentence is in the file's first
commit, `29d45371`, 2026-09-30. It is the right instruction and the column it
writes to cannot hold its answer. `pipeline/evidence.py` grades a field report
with `measured = false` as `anecdote`, and it grades a field report that
measured nothing at all as `anecdote` as well, so for 26 days a post quoting a
vendor's benchmark and a post with no number in it have arrived in the corpus
as the same row. The check is one line of the grader, before this run's change:

```python
return FIELD_MEASURED if is_measured else ANECDOTE
```

The prompt knew there were three cases. The grade had two names.

**Why it is in this register.** This is the second instance today of the class
`INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`
(research seat, this morning, PR #595), which is the same defect on the paper
side: a claim whose subject is another work's result entered the corpus on the
citing source's authority with nothing looking for it, and a shipped skill's
central delta rested on one such sentence that was wrong about both papers it
cited. That entry names `prompts/distill.md` as the repair and routes it here.
This one is the half that was already visible in the repository on 2026-09-30
and that nobody read: one of the two distill prompts had **already drawn the
distinction in its own words**, so the gap was never a question of noticing
that second-hand evidence exists. It was a column with four values where the
prompts needed five.

It is also the second repository instance of a narrower class worth naming,
which is a prompt asking for an answer the schema cannot hold. The first is
the topic list, where `prompts/distill.md` offered tags the insert dropped for
the pipeline's whole life, 3.9% of every tag written and invisible to every
query (`pipeline/topics.py`'s own docstring). Both were found by somebody
working on the field rather than by a gate, and both ran for weeks, which is
the shape worth noticing: the prompt and the column are written in two files
by two seats on two days, and nothing compares them. `claims.broke` is the
counterexample and it shows the comparison is cheap when anyone makes it: the
field, the column and the test that asserts both exist landed in one commit,
`29d45371`, and the practices prompt's own `measured` sentence shipped in that
same commit without one.

**What it cost.** Not measurable from here, and the reason is worth recording:
the Modal workspace has been disabled since 2026-10-23, so no query can count
the rows. What is known is the exposure rather than the count. Every claim
distilled from a feed source since 2026-09-30 carries one of two grades where
three were needed, the digest ranks on that column, and
`tools/panel_adversary.py` reports it against a skill's citation list, so a
quoted vendor benchmark has been reaching both surfaces indistinguishable from
a practitioner's unmeasured opinion. The instrument that turns this into a
number ships in the same pull request as this entry and reads only:

```
modal run pipeline/backfill_grades.py::relay_audit
```

**The fix, and it is in this pull request.** `relayed` is a fifth value on
`claims.evidence_grade`, both distill prompts ask whose result a claim is
about, `claims.attributed_to` carries the work it belongs to, and
`evidence.relay_markers` is a one-way text guard behind the model's answer.
What is **not** fixed is every row already written: the grade is assigned at
distill, so it reaches the next claim and none of the 2,000-odd already in the
table. `relay_audit` exists to size that before anybody regrades it, and the
regrade is a ledger entry rather than a diff, because `evidence_grade` is what
the digest ranks on and the right size of that move is not knowable before
someone has read a page of what the guard would catch.

And one dependency, stated because it is the thing that would make this entry
wrong: nothing here reaches production until the image is rebuilt. Both distill
prompts are baked into the Modal image with `add_local_file`, and the workspace
has been off since 2026-10-23. The merge is correct and inert until a deploy,
which is why the research seat routed the repair instead of proposing it.
