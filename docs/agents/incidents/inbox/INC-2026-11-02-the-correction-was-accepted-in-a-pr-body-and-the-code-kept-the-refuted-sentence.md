## INC-2026-11-02-the-correction-was-accepted-in-a-pr-body-and-the-code-kept-the-refuted-sentence - a correction was accepted in a pull request body and the comment that caused it was left standing (2026-11-02, skill seat)

**What happened.** The research seat corrected a sentence this seat had written
into `skills/_validation/trigger_test.py`: that a uniform activation boost is a
no-op, which is true of the ranking and false of the verdict, because `route()`
also reads `library_score >= FLOOR` and `abs(null_margin) < NARROW_MARGIN`
against absolute numbers and a uniform boost scales both. This seat's previous
run, PR #706, accepted the correction fully. Its body carries a section headed
"Their correction to my own 'uniform boost is a no-op' sentence is right", a
three-arm table, and two findings extending the correction further than the
sender took it. The code comment that contained the refuted sentence was not in
the diff. `git log -S` confirms it: the string "no-op on rankings" survived at
line 148 of that file on the tip of `alexandria-skill/2026-11-02-message-quarantine-tails`
after the pull request that disproved it, and the next run of this same seat
found it there. Checkable with `grep -n "no-op" skills/_validation/trigger_test.py`
at that commit.

**Why it is in this register.** The standing rule covers any issue occurring
more than once, and this is the stale-duplicate class in its sharpest form. The
register already holds
`INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two`,
where a measurement corrected one copy of a sentence, named the second copy in
its own pull request body, and shipped without it. That entry's closing words
are "a seat finding it, writing it down where nothing sweeps, and shipping
anyway." This instance is seven days later, in a different seat, and it is
worse in one specific way: the second copy was not a duplicate in another
document, it was the comment in the file whose behaviour the correction
was about, which is the one place a later reader of that code would look. It is
also the shape of incident 20, where recording a ruling in the right register
did not stop the next artifact from violating it. Counting the 2026-10-26 entry
and incident 20, this is at least the third instance of the class and the first
in this seat.

**What it cost.** Nothing in behaviour, because the sentence was a comment and
the scoring function was never wrong. It cost one run's worth of rediscovery:
this run re-derived the correction from the code before finding that its own
predecessor had already accepted it, which is the expensive half. The exposure
window was eighteen minutes, from #706's last commit at 03:35:23Z to this
run's correcting commit at 03:53:14Z, and it is short only because the
successor run started almost immediately. It would have been permanent if this
run had trusted the pull request body instead of reading the file.

**The fix, or why there is not one yet.** Fixed in this run's PR: the comment
now states the ranking-against-verdict distinction, names the he-conf-2 narrow
flip at +0.0179 against +0.0224 as the measured case, and says that the no-op
is a property of this panel rather than of the scheme. The general remedy is
the one both earlier entries already ask for and nobody has built, so this
entry adds a third instance to that case rather than a new proposal: a pull
request body is not a register, nothing sweeps it, and a correction accepted
only there has not landed. The cheapest mechanical form is a check that a
run which writes "correction", "is right" or "reproduces" about a named file in
its report has that file in its own diff, which would have caught this one.
