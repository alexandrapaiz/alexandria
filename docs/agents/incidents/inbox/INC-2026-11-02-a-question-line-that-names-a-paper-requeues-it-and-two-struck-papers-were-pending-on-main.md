## INC-2026-11-02-a-question-line-that-names-a-paper-requeues-it-and-two-struck-papers-were-pending-on-main - the parser takes the first arxiv id anywhere in the line, and a precaution written in prose beside it has no reader (2026-11-02, research seat, message wake)

**What happened.** This run appended a question line to
`docs/research/reading-queue.md` that names the two routing papers it had just
read, and then ran `python3 pipeline/reading_queue.py` to check its own edit. The
pending list grew by one id: `arxiv:2609.15982`, a paper struck as read in full
twice. Running the same command against the merged trunk, with none of this run's
edits, returned `arxiv:2608.04828` as pending too, which is struck as read **and
distilled into the corpus**.

The cause is one regex. `pipeline/reading_queue.py` matches
`ITEM = ^\s*-\s*\[([ xX])\]\s*(.*)$` and then searches that whole body with
`ARXIV`, taking the first `arxiv:<id>` anywhere in it. The comment three lines
above says "Lines without an arXiv id are the questions the reading raised,
addressed to the research seat rather than to a fetcher, and they are skipped
here" - which is true of a question line that happens to name no paper, and is
the only kind of question line that existed when it was written. A question
about a paper names the paper, so the question lines most worth writing are
exactly the ones that requeue it.

Three lines were live in this state: the skill seat's two from 2026-11-02, both
naming `2608.04828`, and this run's one naming `2609.15982`. A fourth, line 122,
names a paper that genuinely is unread past its abstract, so its pending row is
correct and it was left alone.

**The sharpest part, and it is why this is filed rather than fixed quietly.** The
skill seat saw this coming and wrote the precaution into the file: its own
section preamble says `2608.04828` "is struck as read and distilled so only the
question is queued and not the paper." The sentence is right, the intent is
right, and the id was pending on the trunk anyway, because a parser does not read
a preamble. This is L-A9 exactly, recording a rule is not enforcing it, in a file
where the rule and the thing it governs are four lines apart.

**Why it is in this register.** Eighth instance of the duplicate-work class, after
the seven `INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`
counts. It is a distinct mechanism from all seven: those are about a strike the
checker cannot see, and this is about a strike that exists, is visible, is correct,
and is overridden by a later mention of the id in a sentence that says the
opposite. The sixth instance's remedy, grep the queue before appending an id,
would have passed all three of these lines, because the grep is what tells you the
paper is struck and the whole point of these lines is that they know it.

**What it cost.** Nothing yet, and the margin was one distill run. Six pending ids
go per distill run and `2608.04828` was eighth from the end of an 83-line pending
list, so the ordering is what saved it rather than any check. A requeued distilled
paper costs a fetch, a model call and a triage row, and lands a second set of
claims on a paper that already has them, which is the expensive half.

**The fix, and the half of it that is not this seat's.** Repaired in this pull
request, in the only place a seat without a deploy can repair it: all three
question lines now carry the bare id, `2608.04828` rather than `arxiv:2608.04828`,
which the regex does not match and a human reads identically. The pending list is
back to 81 with both struck papers out of it, verified by running the parser
before and after. Two of the three lines are the skill seat's text and the change
is a formatting repair that alters no disposition, which is why it was made rather
than routed; it is named on the board in this run's reply.

The real fix is three characters in `pipeline/reading_queue.py`: anchor `ARXIV` to
the start of the item body, so the documented format
`- [ ] arxiv:<id> - why - asked by skills/<slug> - YYYY-MM-DD` keeps working and a
mention inside a sentence stops being a fetch instruction. Not proposed here,
because `pipeline/*.py` is image-baked and a merge to main changes nothing in the
running pipeline until someone runs `modal deploy`, which is the engineer's. Until
it lands, the convention is the bare id in any line that is not a fetch request,
and the test is one command: `python3 pipeline/reading_queue.py` before and after
the edit, and the count must not go up.

Ban list checked on this entry.
