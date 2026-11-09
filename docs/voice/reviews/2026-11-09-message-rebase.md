# Writer run 68, 2026-11-09 (message wake, rebase pass)

**The single biggest thing this run found: the instrument this seat built to
stop it wording a rule that is already fixed told it, this morning, to word a
rule that was fixed eight days ago.** `queued 8` reads `UNNAMED`, the review on
#816 concluded from it that law 8 owed a prompt diff and named it as the next
run's item, and law 8 stopped being a prompt rule on 2026-11-02. This run is
that next run. It wrote no prompt diff and fixed the instrument instead.

## What woke it, and what the handoff settled

A `handoff` from the PM seat on the board, `31f301e6`, carrying three things.

The section 22 reading on `docs/voice/awaiting-her-word.md` is confirmed:
neither reservation is one of the four the standard keeps for her regardless of
the clock, so both proceed as recommended. Nothing was left for this run there,
because #816's diff had already moved both rows to the resolved table with
their questions verbatim.

The two duplicate asks are withdrawn on the bus, by the seat that owns posting
and withdrawing them. Not this seat's, and not done here.

And #816 reads conflicting against `main`, because two security pull requests
that append to `docs/ideas.md` merged while it was open. That is this run's
first half.

The frontend follow-up named at the end of the handoff is correctly not a
today action: there is no approved candidate to set, so there is nothing for
the step 5b handoff to name. This run produced no reader-facing copy either, so
the copy pipeline, `value.md`, the preference file and the quality-claims
register bind nothing in it.

## The rebase, proved rather than asserted

`alexandria-writer/2026-11-09-message` branched from the merge of #812 and
`main` ran 218 commits ahead of it. One conflict, and it is the ledger's tail
anchor for the fourth time this week: both sides appended entries at the end of
`docs/ideas.md`.

Both appends kept, with all of 2026-11-09's entries together at the tail. The
resolution is checked three ways rather than eyeballed:

- `main`'s version of the file is a byte-exact prefix of the result.
- This seat's branch removed or changed no line of the merge base, so it is
  append-only and nothing of `main`'s can have been dropped by taking it.
- The single entry the branch added is byte-exact against its own commit.

932 ledger headings where `main` had 931. `ledger.py --check` reports 0
blocking and 71 warnings, at or under the recorded baseline, so the new entry
carries its contract fields. No conflict markers anywhere in `docs/`,
`prompts/` or `README.md`.

## Law 8: no prompt diff, and the reason is not a quiet day

Step 3 asks for the commit that fixes a failed law, a check that the commit is
not itself reverted, and the command this run asked. All three:

**The commit is `3cd597a4`, 2026-11-02, `pipeline/arxiv_html.py`.** It answers
the one question reading the artifact cannot: does arXiv serve the HTML for
this identifier. The answer is a HEAD request, the identifier is read out of
the url the pipeline already holds rather than composed, and an unreachable
arXiv is a third outcome instead of being folded into the fallback.

**It is not reverted, and this was checked at the end state rather than across
a pair.** `git show origin/main:pipeline/weekly.py` carries
`arxiv_html().resolve_payload(payload, probe=probe)` at line 562, before the
payload is returned to the generator. The pair the charter warns about,
`c5a32e4c` and `0251df0b`, is a different thing entirely: that was the fourth
prompt wording, written and struck inside one run on 2026-10-26, and its net
diff on `prompts/digest.md` is empty.

**The commands asked were `python3 docs/voice/check_voice.py queued 8` and
`python3 docs/voice/check_voice.py press`.** `press` reports the deployed
commit `f16e2775`, deployed 2026-10-15, carrying the generator as of
`9b6410ea`, 25.2 days old with 30 queued commits. The law 8 fix merged
eighteen days after that deploy, so it is queued behind it exactly as step 3
describes, and the deploy is the whole of what is owed.

**And no deletion either, which is the other prompt diff this run considered.**
The generator still carries sixteen lines instructing a model to rewrite `abs`
to `html`, and the pipeline now makes that decision before the model sees the
payload. The canon's own trimming rule settles it: an operative clause never
goes. `arxiv_html` has a fourth outcome, `UNREACHED`, where the `abs` url
stands because nobody could ask, and in that case the instruction to copy the
identifier character for character is the only thing standing between the
reader and a composed url. Ban list 100 is live on three of the four served
editions, so that clause is load-bearing today.

## What the live reading added, which #816 did not have

#816 reported 7 law 8 failures across the product and left them unexamined.
Read link by link, they are not spread:

| edition | arXiv links | form |
| --- | --- | --- |
| 2026-W39 | 6 | 6 html, 0 abs |
| 2026-W40 | 3 | 3 html, 0 abs |
| 2026-W42 | 10 | 1 html, 9 abs, 7 of them with HTML at arXiv |
| 2026-W44 | 5 | 5 html, 0 abs |

Every failure the product serves is in one edition, and the two editions
published after it are eight for eight. Inside `2026-W42` the shape is sharper
still: the lead item's link is `html/2610.10310v1` and every one of the nine
links written after it is an `abs`. The rule was not misunderstood. It was
applied once and then not applied again for the rest of the issue, which is
what a judgment call looks like when nothing checks it, and it is the reason
the decision belongs in a function. The engineer's module says the same thing
in its own words: "The rule was not ignored. It was applied by judgment, and
judgment went seven for nine."

This matters for the grade's honesty in both directions. It is not evidence
that the generator lacks the rule, and it is not evidence that law 8 is in
good shape either: `2026-W44` got it right the same way a coin can, under a
press that does not yet carry the fix.

## The instrument, which is what this run shipped

`queued`'s entire input is `git log deployed..origin/main -- prompts/digest.md`.
The question a grade brings to it is whether a law's fix is already merged. The
question it can answer is whether a commit to the generator touched that law's
span. Those come apart precisely when the charter's structure-watch step has
worked, because that step moves a twice-failed rule out of the generator, so
**the better a seat obeys step 4, the more laws arrive in the one state the
command misreads**, and the misreading always says the same thing, which
is that nothing is coming and the rule should be written again.

Two verdicts added, fifth and sixth:

- `MOVED`: the law is decided by code, the code is merged, and the call is
  still present on `main`. It is first, above every answer the queue can give,
  because once a law is decided by a function every wording of it is the tinker
  step 4 refuses. The sentence names the module, the commit, and whether the
  press has it, because the two answers ask for different things and neither
  one asks for a word in the generator.
- `UNWIRED`: a declared row whose call is not in the file on `main` any more.
  Built and then unwired is not a fix, and it must not read as one. That is the
  same defect `drop_reverted` fixes one storey down, where a patch and its own
  revert counted as two patches.

`MOVED_LAWS` is the declared table and `moved_fix` is the check. `MOVED_CASES`
pins three readings with a stub `show` so no case touches git, including the one
that matters, which is a declared row whose call has gone. `queued 8` now
reports `OK MOVED` and exits 0. Laws 1, 12a and 14 still read `UNNAMED` on 14,
19 and 3 commits, and law 12 still reads `OK QUEUED` on `97de5c8b`, so no other
verdict moved.

The table is hand-written and this run says so plainly rather than in a
docstring: a law the engineer moves tomorrow is invisible until this seat
writes the row, and the seat most likely to need the row is the one that does
not know the move happened. The general form reads the queue with no path
restriction, which depends on commit subjects citing their law across files
rather than on a convention that belongs to one file. Filed in `docs/ideas.md`
with a first step that costs one grep, and not imposed on `pipeline/` by a seat
that does not own it.

## Grade

No new issue was graded and this run says so rather than printing verdicts
that would look like work. The newest edition is `2026-W44`, recorded
2026-11-02T09:00:05Z, and it is the artifact #804, #812 and #816 have already
graded on a generator that has not changed since 2026-10-15. A fourth scoring
of one edition inside a day produces the same verdicts in different sentences.

What this run owes instead is the one law #816 left open, and law 8's reading
above is that verdict in full: present in the generator, decided in the
pipeline, merged, unreverted, undelivered. The deploy is the ask.

## Checks

`queued` 4/4, 6/6, 2/2, 3/3, 4/4 with `queued 8` at exit 0. `press` FAIL
BEHIND as expected, 4/4, 5/5, 7/7. `links --live` WHOLE, four editions, the
seven failures attributed above. `selfcheck`, `enforcements`, `doubles`,
`editions`, `candidates`, `deadlines`, `dispatch` and
`tests/test_voice_enforcements.py` are reported with their numbers in the pull
request. `ledger.py --check` 0 blocking. `tools/incidents.py check` nothing
malformed. No conflict markers. Every scratch path in this run came from one
`mktemp -d`, which is step 0b and the thing #816 broke.

One repeat filed: `INC-2026-11-09-the-queued-gate-was-wrong-about-law-8-a-second-time-and-in-the-opposite-direction`,
with the correction that the fix proposed by the day-before sibling reaches 56
of 161 ban list entries and not the one it was proposed for.

This pull request changes no seat's authority and spends no money, so it does
not wait on the owner.
