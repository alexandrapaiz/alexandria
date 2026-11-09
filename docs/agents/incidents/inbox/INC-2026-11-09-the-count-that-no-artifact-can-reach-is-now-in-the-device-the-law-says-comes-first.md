## INC-2026-11-09-the-count-that-no-artifact-can-reach-is-now-in-the-device-the-law-says-comes-first (2026-11-09, engineer seat, message run)

**Repeat of the class `docs/voice/check_voice.py` records against itself in
`ITEM_FURNITURE`'s own comment**, which is "every issue the press can produce
carries at least one item, so the one condition `measure` fails on could not be
reached by any artifact", and of
`INC-2026-11-08-the-sweep-for-ungated-rules-could-not-admit-the-rule-the-days-grade-turned-on`,
which is that class in the register built to find it. The class is an
instrument whose condition no artifact the press can write is able to satisfy,
so its verdict is structurally fixed and reads as a measurement. Recorded under
the standing rule at the top of the register rather than filed only as an idea,
because this is the third instance in nine days and the first two were each
written up as one-offs on the surface they were found on.

**What happened.** This run lifted canon law 14's shape count out of
`docs/voice/check_voice.py devices` and into `tools/check_digest_quality.py`,
so the law the owner has read and rejected twice could stop a send instead of
appearing in a grade written afterwards. The lift failed its own
satisfiability check on the first run: `GOOD` in
`tests/test_digest_quality.py`, this repository's one worked model of a correct
issue, tripped the new rule.

**Why, measured on three artifacts rather than argued.** `shapes` asks whether
EVERY row of a block matches the bullet pattern. The item shape
`prompts/digest.md` mandates is a short bold lead on the same line as its
sentence, wrapped over two or three lines, with prose and a citation under it,
so the rows after the first do not begin with a bullet and the whole block is
counted a paragraph.

```
GOOD fixture   {'heading': 3, 'standalone line': 1, 'paragraph': 3}   list 0, blocks opening on a bullet 2
2026-W37       {'heading': 5, 'paragraph': 9, 'list': 2, ...}         list 2, blocks opening on a bullet 4
2026-W39       {'heading': 5, 'paragraph': 14, ...}                   list 0, blocks opening on a bullet 0
```

So the `list` half of law 14's first count can be satisfied by nothing the
generator is instructed to write. `2026-W37` scores two only from two other
blocks that happen to be single-line bullets, and four of its real items are
counted prose.

**Why this instance is worse than the two before it, and the reason it gets an
entry rather than only a ledger row.** The two recorded instances were in a
count that was one of several and in a register's admission test. This one is
in the device `prompts/digest.md` says comes first: "Count the shapes first,
because the other counts below can all pass while this one fails." And it is
half-blind rather than blind, which is the quiet kind. `devices` prints `FAIL
no list and no written turn`, the `turn` half of that sentence is a true
reading, and the `list` half is an instrument that cannot see the shape it is
looking for. Every run that has read that line has read it as a statement about
the page. Nothing was wrong with any of those readings except the half nobody
could know about.

**What this run did about it, and what it did not.** The pre-send gate takes
the first row of a block, which is what Markdown means by a list item and what
the press's own renderer does, so law 14's rule is satisfiable at the send: the
worked tier-four issue passes and `2026-W39` is held. The two commands now
disagree on `GOOD` deliberately, and the divergence is pinned by
`test_a_wrapped_list_item_is_a_list_here_even_though_the_canon_scores_it_prose`,
which goes red the moment the canon is fixed so the gate may follow it again.
The canon's own half is not fixed here: `docs/voice/` is the writer seat's
surface and this seat does not write it, which is the same boundary in the
other direction that routed this work here in the first place. It is filed in
`docs/ideas.md` with the measurement above and a one-line repair.

**The general shape, for the ExO's weekly read.** All three instances were
found the same way, which is by somebody building a second consumer of the rule
and discovering the first consumer's condition was unreachable. None was found
by reading the instrument. A satisfiability check belongs next to a counting
gate: for each condition the gate can fail on, one artifact in the repository
that satisfies it. `tools/check_digest_quality.py` has had that check per rule
since it was written, as the `GOOD` fixture and the test that it stays clean,
and it is precisely the check that caught this one.

Ban list checked on this entry.
