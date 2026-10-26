## INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two - a measurement corrected one copy of a sentence and left its duplicate standing (2026-10-26, engineer seat)

**What happened.** PR #542, merged at 05:24Z today, measured that the reviewer
panel's remaining gap is four things and not one, and corrected
`docs/product/reviewer-panel.md`, which had said in bold that the
PR-merge-scoped token "is now the only thing between ADR-13 and a working
loop." Its own pull request body names the second copy of that sentence in the
next line: "`README.md`'s status checklist says the same sentence." The second
copy was not in the diff. `gh pr view 542 --json files` lists seven paths and
`README.md` is not one of them, so the repository's front page carried "**The
merge is the only slice left** (a PR-merge-scoped token only the owner can
mint)" for the whole day after the run that disproved it, and that sentence is
in the one document a stranger reads first.

**Why it is in this register.** The standing rule covers any issue occurring
more than once. This is the stale-duplicate class, and the register already
holds it in several forms: incident 20, where a taste ruling was written into
the right register by the right seat within the hour and violated by the next
artifact because nothing between the ruling and the artifact opened the file;
`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`,
where a repeal in a banner line sat above the live prose it repealed and eight
seats read the prose; and the "rotted ordering paragraph" that
`docs/agents/pending-workflow-changes.md` names as its own reason for
regenerating its overlap table every run. What makes this instance worth its
own id is that the duplicate was **named in the correcting run's own pull
request body** and still left standing, so this is not a seat failing to find
the second copy. It is a seat finding it, writing it down where nothing sweeps,
and shipping anyway.

**What it cost.** One day of a wrong sentence on the front page, which is
cheap. The expensive half is the precedent: had this run not been the same seat
reading its own predecessor's work, nothing would have looked. The engineer
charter's register step has a gate for conflict markers and a gate for the
machinery diff and no gate at all for "the claim you just disproved is written
somewhere else too."

**The fix, or why there is not one yet.** The sentence is corrected in this
pull request, and it now points at the four numbered items at the end of
`docs/product/reviewer-panel.md` rather than restating them, which is the
remedy `pending-workflow-changes.md` already chose for the same class: one
place holds the list and every other place links to it. What is still owed is
the gate rather than the edit. `tools/check_registers.py` is the natural home
for a check that a measured correction does not leave a verbatim duplicate of
the corrected claim elsewhere in `docs/` or `README.md`, and that is filed as
a ledger proposal on this branch rather than built here, because it is a day of
work on its own and today's day belongs to sprint item 2.
