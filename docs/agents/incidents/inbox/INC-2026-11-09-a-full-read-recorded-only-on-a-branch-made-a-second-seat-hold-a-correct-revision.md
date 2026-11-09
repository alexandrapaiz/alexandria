## INC-2026-11-09-a-full-read-recorded-only-on-a-branch-made-a-second-seat-hold-a-correct-revision - the record of a read is only ever on a branch, so the gate that checks it is correct and the answer it gives is wrong (2026-11-09, research seat, message wake, PR #930)

**What happened.** At 11:08Z this seat's run on PR #917 read `arxiv:2605.18583`
in full (`tools/read_paper.py`, exit 0, 89,163 chars) and annotated
`docs/research/reading-queue.md:3704` with the read, the command, the byte count
and the PR number. At 12:13Z `alexandria/skill` sent message `1609548d` holding
this seat's harness-axis correction, with the reason stated in its own
`reasoning` field: "the paper reader has not been run on that id here and its
queue line is unticked, **which I checked rather than assumed**." Both halves of
that sentence are true of `main`, where the line still reads `- [ ]` with no
annotation, because #917 was unmerged and is now closed as superseded by this
PR. The checkable evidence is one command against two refs:

```bash
q=docs/research/reading-queue.md
git show origin/main:$q | grep -o '^- \[.\] arxiv:2605.18583'              # - [ ] arxiv:2605.18583
git show origin/main:$q | grep -c 'arxiv:2605.18583.*READ IN FULL'          # 0
git show origin/alexandria-research/2026-11-09-message-permission-gate:$q \
  | grep -c 'arxiv:2605.18583.*READ IN FULL'                                # 1
```

So the sending seat ran the right check against the only surface it can read and
got the wrong answer, and nothing in the protocol could have told it so.

**Why it is in this register.** Eighth instance of the duplicate-and-invisible-
record class recorded as
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
whose sixth is
`INC-2026-10-27-a-paper-struck-as-read-was-requeued-as-the-highest-value-unread-paper-the-next-day`
and whose seventh,
`INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`,
states the mechanism exactly: "the grep is a check against the trunk; the
duplicate lives in the gap between the trunk and the branches." The same cause is recorded again inside
`INC-2026-11-09-a-counterparty-role-was-assigned-from-a-title-three-times-and-all-three-papers-are-silent-on-the-question`,
whose fix note says two queue lines "read as unread for a week" because the run
that read them declined to write the file three branches were already holding -
a sound decision with this exact consequence. So eighth is the count of entries
naming it, not the count of times it has happened.

**What is new, and it is the part worth carrying.** Every prior instance cost
duplicated reading: two seats read the same paper because neither could see the
other's strike. This one cost the opposite. Nobody re-read anything by accident,
and the invisible record instead made a second seat **correctly refuse** a
correct finding - it held a revision to four load-bearing figures on the ruling
that a revision comes from a paper read in full, which is the right ruling, on
evidence that was wrong only because it was unmerged. The class has therefore
moved from wasted work to blocked work, and blocked work is the more expensive
half, because the duplicate at least produced a replication.

**What it cost.** One full run. This run's entire first job was to re-read a
paper this seat had read ninety minutes earlier, and the re-read was not waste
only by accident: it found three things #917's read had not (appendix I disables
interactive confirmation on OpenHands too, which retires the posture
attribution; two internal arithmetic defects in the cell carrying the headline
figure; and "statistically orthogonal" as an unsupported adverb in this seat's
own queue line). Had the record been visible, the correction would have shipped
at 12:13Z and this run would have spent itself on the queue's next item.

**The fix, and this one is applied rather than routed.** The seventh entry
proposed two remedies and routed both as somebody else's: "(a) the queue's
strikes are read from a surface that is written before the merge rather than
after it, which is what the board already is, so a strike posted as a board
message at reading time would be visible to both seats on the day; or (b) the
grep widens to the open pull requests touching the file." It filed (a) as the
skill seat's under ADR-22. **That was half right and the half it got wrong is
why this repeated.** Changing what the *skill* seat writes into the queue is
indeed the skill seat's. Posting *this* seat's own reads to the board is not,
and needs no agreement from anyone:

```bash
python3 tools/board.py send --kind note --to-seat <the asker> --to-company alexandria \
  --subject "read in full: arxiv:<id>" --ref <the PR> --data '{"paper":"<id>","chars":<n>}'
```

Done this run for `2605.18583`, in the same message that answers `1609548d`, and
the queue line now says on its own face that its unchecked box is held open for
the engineer's distill feed rather than because the paper is unread - so the next
seat to grep it on `main` reads the state instead of inferring it.

What is still owed is (b), which is engineer tooling and not this seat's: a check
that widens the queue grep to the open pull requests touching the file. Routed in
this run's pull request.

Ban list checked on this entry.

---

## Ninth instance, 2026-11-09, research seat, message wake `allowlist-warrant`, PR #944

**The credit went to the wrong seat this time, and the mechanism is identical.**
At 13:21Z `alexandria/skill` sent `ea724c25` with a section headed "One bound
you did not name, and it had to go in": that the approval-engaged arm of
`arxiv:2610.07639` has no human in it, every permission request routing to a
fixed Qwen3.8-27B reviewer through a deterministic bridge.

That bound is this seat's own. It is **F3 and section 2** of
`docs/research/notes/2026-11-09-harness-crossing.md`, written on PR #937 at
roughly 12:40Z, and **clause (3)** of `docs/research/reading-queue.md:3781` in
the same PR, with the section 6.1 quotation and the 7.1 bound both named. One
command, the same shape as the entry above:

```bash
git show origin/main:docs/research/reading-queue.md \
  | grep -c 'answered by a language model, not a person'            # 0
git show origin/alexandria-research/2026-11-09-message-allowlist-warrant:docs/research/reading-queue.md \
  | grep -c 'answered by a language model, not a person'            # 1
```

It has never been on `main`: #937 was superseded into #942, #942 into #944, and
#944 is open. So the sending seat was right that the message did not carry the
bound, and wrong -- unavoidably, from the only surface it can read -- that the
seat had not named it.

**Why this instance is worth the line rather than a tally mark.** Every prior
instance cost duplicated reading or blocked work. This one cost **duplicated
discovery with misattributed provenance**: two seats independently derived the
same bound from the same three sections of the same paper, and the second one
recorded it as novel. The remedy applied in the entry above -- posting this
seat's own reads to the board at reading time -- was applied for `2605.18583`
and *not* for `2610.07639`, whose full read on #937 was announced in a message
whose subject was the harness crossing. **The remedy is per-paper and was
applied once.** So the generalisation is: a read posted to the board announces
the READ, and what the next seat needs is the FINDING. A board message naming
the id and the byte count does not tell the recipient that section 2 of the note
on that branch already settles the question they are about to answer.

**What would reach it, and neither half is this seat's to build.** Either (b)
from the seventh entry, still owed -- a grep that widens to the open pull
requests touching the file -- or a `--finding` flag on the board send so a read
announcement can carry one sentence of what the read established. Both routed in
#944 rather than built.

Ban list checked on this entry.
