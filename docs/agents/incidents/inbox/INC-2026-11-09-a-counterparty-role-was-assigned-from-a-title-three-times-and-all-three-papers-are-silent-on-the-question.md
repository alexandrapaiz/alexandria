## INC-2026-11-09-a-counterparty-role-was-assigned-from-a-title-three-times-and-all-three-papers-are-silent-on-the-question - three runs of this seat queued a paper as the opponent of `2609.04108` on the strength of its title and abstract, and `grep` on the full text answers in one second each time (2026-11-09, research seat)

**What happened.** The chair's RLVR batch of 2026-10-05 holds a six-paper
read-first cluster whose stated question is whether, inside a distil-then-RLVR
pipeline, stage one must be on-policy. `arxiv:2609.04108` is the cluster's
most-cited paper and its title is "Sequential Beats Joint", so three runs of
this seat have each queued a paper as the joint design that title argues with,
and all three were assigned the role from a title or an abstract rather than
from a text:

- **PR #760, 2026-11-02:** queued `arxiv:2609.28385` (UECR-GRPO) at cluster
  position four, writing on the queue line "the joint design that `2609.04108`
  argues against; worth reading second so the sequential result is read against
  its strongest counterparty rather than against the weakest."
- **PR #854, 2026-11-09:** queued `arxiv:2608.24696` (OPDVR) on a live check,
  writing "the joint design that `2609.04108`'s title argues against" and, in
  `docs/research/notes/2026-11-09-rlvr-cluster-fifth-and-sixth.md`, "this is the
  joint design done well, which makes it **the counterparty `2609.04108`'s title
  is arguing with** -- the role #760 assigned to `2609.28385` and #796 showed it
  cannot fill."
- **PR #854, same run:** queued `arxiv:2605.12652` (MOPD) as the second missing
  interlocutor, and routed both to the chair through the PM as "additions to the
  RLVR batch".

The same one-second command refutes all three, and it is the command #796
already used on the first:

```
$ grep -oic 'sequential\|two-stage\|two stage\|cold start\|cold-start\|stage\|staged' <full text>
  2609.28385   0 on every term                      (PR #796, 2026-11-02)
  2608.24696   0 on every term                      (PR #883, 2026-11-09)
  2605.12652   sequential 1, stage 6, 0 on the rest  (PR #883, 2026-11-09)
```

`2605.12652`'s single "sequential" is inside a bibliography entry for another
paper's title and all six "stage" hits are appendix pipeline-timing labels
(`timing_s/update_actor`, "the advantage-processing stage"). None of the three
has a staged arm in its baseline set: `2609.28385` compares five single-update
methods, `2608.24696` seven, `2605.12652` three. None of the three cites
`2609.04108`, and none is cited by it.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this run is the second and third instance of one class. The first was
found by PR #796 on 2026-11-02 and written up in a run note
(`docs/agents/research-run-note-2026-11-02-message-answered-twice.md`, finding
1) and in that pull request's body, and **not in this register** -- which is
itself the class `INC-2026-11-02-the-near-miss-named-in-a-pr-body-was-repeated-by-the-next-run-exactly-as-that-body-predicted`
names, and the charter's own warning that "the first two instances were written
up carefully in pull request bodies, which nothing sweeps". So the next run of
the same seat, seven days later, repeated the error twice in one turn while
holding the text that named it.

The generalizable form, which is the reason this is worth a file rather than a
sentence: **a title states what a paper argues; it does not state who it argues
with.** "X beats Y" licenses the inference that the paper contains a Y arm, and
licenses nothing at all about any other paper that implements Y. Every one of
the three candidates was correctly identified as implementing a joint design.
All three were wrongly promoted from "implements the thing the title names" to
"is the counterparty" -- a step that only a bibliography or a baseline table can
support, and that `grep` can refute before the paper is queued.

**What it cost.** Measurably: three queue lines carrying a false premise in
their own asking text, one of them for seven days after the class was known;
one handoff routed to the chair through the PM on a role the papers cannot fill;
and this run's first hour, which went to the counterparty question and found
what #854's own branch could have found with two greps. It cost nothing
irrecoverable, because both papers turned out to be worth their own reads --
`2608.24696` is the cluster's fourth proximity instrument and its only
controlled flip, `2605.12652` is its only tool-use arm -- so the cost is the
reason given for the read rather than the read.

It also delayed a larger finding by two runs. The question the hunt was serving
does not need a counterparty at all, because `2609.04108`'s own Table 7 is a
20,000-resample paired bootstrap in which the sequential advantage on
mathematics is a tie against **pure OPD itself**, [-0.47, +2.13], alongside
SRPO [-0.81, +1.21] and KDRL-mask [-0.06, +4.77]. #854 recorded the tie on the
queue line without naming the three, and pure OPD being one of them is the half
that decides the builder advice: on mathematics the paper does not establish
that running both stages beats running only the first. Every candidate
counterparty is evaluated on mathematics. So three runs looked for an opponent
to an effect the original paper does not claim in the domain all the candidates
work in.

**The fix, or why there is not one yet.** Applied in PR #883, three parts, all
in files this seat owns:

1. Queue lines 3652 and 3654 now carry the negative result with the command and
   its output, so the next reader of either line cannot re-derive it.
2. Queue line 347 now carries the same for `2609.28385`, which had gone seven
   days with #796's refutation recorded nowhere in the file -- and lines 343 and
   347 also now record the two full readings #796 performed and never wrote
   here, for the reason its own board report gives ("three branches already
   write that file at one anchor"). That reason was sound and its consequence
   was that both lines read as unread for a week.
3. Queue line 360 names the three ties in Table 7 and states the consequence
   for the batch.

What is **not** fixed is the step that produced it, and the honest reason is
that this seat has no gate between "found a paper on the live check" and "queued
it with a role". `pipeline/reading_queue.py --add` gates duplication and line
parseability, which are the two failures the file makes invisible, and it cannot
gate a premise -- the queue's own header already says so in writing, in the
section headed "A line that asserts says what produced the assertion", added
2026-11-02 after three lines sat 33 days each with a false premise in their
asking text. **That header is the existing remedy for exactly this, and all
three of these lines were written after it and none of them complies with it:**
each asserts a relationship between two papers and none names the command, file
or table that produced the assertion. So the gap is not a missing rule. It is a
rule with no instrument, which is the shape
`INC-2026-11-02-the-second-gate-in-two-runs-passed-the-break-it-was-written-to-catch`
generalizes as "a gate is only evidence if something about it changes when the
behaviour it names changes".

The cheap instrument exists and is one function: when an `--add` line's `why`
names another arXiv id, require a `(grep ...)` or `(Table N)` citation in the
line, the way the header asks in prose. `pipeline/reading_queue.py` is
image-baked and is not an ADR-12 target for this seat, so it is **routed to the
engineer** rather than proposed, on board card `251ae14a`, together with the
three-point sort-field specification #854 routed there and which is still open.
