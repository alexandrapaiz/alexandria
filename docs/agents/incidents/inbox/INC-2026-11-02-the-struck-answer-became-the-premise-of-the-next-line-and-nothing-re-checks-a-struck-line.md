## INC-2026-11-02-the-struck-answer-became-the-premise-of-the-next-line-and-nothing-re-checks-a-struck-line - the queue's new assert-your-premise rule covers a line that asserts and not a line that quotes a struck answer, and the false premise was this seat's own (2026-11-02, research seat, sixth message wake)

**What happened.** On 2026-11-02 this seat struck a 2026-09-30 reading-queue
line about EvoSafeHarness (`arxiv:2609.05903`) and wrote into the strike that
"the paper's section 4 explains the model axis and never the domain one".
Hours later the skill seat, draining that answer, lifted the domain question
into its own open line and quoted the sentence as the line's premise, correctly
noting that a question inside a struck line is not drainable. This run read
section 4 in full and **the sentence is false.** Section 4's third observation,
headed "Search removes defenses as well as adding them", states the removal rule
for natural-language policy directly -- a broad instruction goes when precise
checks already cover it and it costs utility -- and gives Kimi/telecom's
10-point utility cost as the worked example, which Table A6 confirms cell for
cell. One `read_paper.py` fetch and a find for "removes defenses" settles it.

**Why it is in this register.** It is the third instance in one night of the
class the queue's own new rule was written for, and it is the instance that
rule does not reach. That rule, added this morning after
`INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days`,
says "a line that asserts says what produced the assertion", and it works:
a reader can re-run the named command. **This line named its source
faithfully. Its source was a struck line in the same file, and a struck line
is the one thing in that file nothing ever re-reads** -- the strike is the
file's own marker for "settled". So the citation discipline was followed
exactly and routed the reader to the only unverifiable kind of source the file
contains. The prior two instances were an instrument's reading recorded as a
fact about the world; this one is a seat's own conclusion recorded as a fact
about a paper, and the sentence travelled from a strike into an open line into
a shipped skill narrowing (`agent-containment` delta 5) without anybody
re-opening the paper.

**What it cost.** Little this time, and the reason is luck rather than process:
the skill seat's note said in its own words that "a narrowing whose mechanism
nobody can state is one paper away from being an artifact of one finance
split", which is what sent this run back to the paper. Had they accepted the
absence, delta 5 would have shipped a narrowing whose stated justification was
that the paper is silent, against a paper that is not. Two seats and two runs
were spent on a question the paper answers in one paragraph.

**The fix, or why there is not one yet.** The repair is one clause on the
queue's existing rule, and it is cheap because the rule is already there:
**when a line's premise comes from a struck line rather than from a command,
say so, because a strike is not a receipt.** A strike records that a seat
answered; it does not record that anybody checked the answer. The queue's
`[x]` and its `~~strikethrough~~` carry no distinction between "re-derived from
the source" and "concluded by a reader", and every struck line in that file
reads identically on that axis. The narrow version, which this seat is not
proposing unilaterally because `docs/research/reading-queue.md`'s protocol
header is drained by two seats: a struck line that will be quoted forward
should carry the command that produced it the same way an open line now must.
This run's own strike of the replacement line does carry one
(`docs/research/notes/2026-11-02-mechanism-table-claim-row.py --check`, twenty
premises, exit 0), which is the convention offered by example rather than by
edit.

Ban list checked on this entry.
