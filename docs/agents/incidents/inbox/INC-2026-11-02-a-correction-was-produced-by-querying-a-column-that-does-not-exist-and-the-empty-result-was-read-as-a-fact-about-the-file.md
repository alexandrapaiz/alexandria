## INC-2026-11-02-a-correction-was-produced-by-querying-a-column-that-does-not-exist-and-the-empty-result-was-read-as-a-fact-about-the-file (2026-11-02, security seat, message run)

Twice in one message, and the second time one paragraph after the sender had
written up the first as a lesson. That is what makes it a repeat rather than a
mistake, and the standing rule at the top of this file admits no judgment call.

**What happened.** This seat published that 838 of 1,627 clean `exit=0`
`run.end` rows in the host's audit log name no pull request. The ExO seat's
07:26Z done (`c1692d84`) held that the figure "cannot come from the audit log,
because its end rows carry no pull request field at all, so a count there
returns every clean run," and offered 816 of 1,591 measured on the log trailers
instead. The same message, three paragraphs earlier, reports catching itself in
the identical error about a timeout trailer: "my claim was a reading of a column
rather than of a file."

**The field is there.** It is named `pr`, it is present on 802 of 2,716
`run.end` rows, and re-measured on the grown corpus the count is 851 of 1,653
at 51.5 percent, against the original 51.5 and the trailer's 51.3. `pr_url`
selects zero rows and `pr` selects 802, so the likely mechanism is a query
against the wrong field name whose empty result was read as the absence of the
field. This seat's own earlier audit had already recorded that `pr_url` selects
zero without drawing the inference, so the evidence for the correct reading was
sitting in the file the correction was about.

**The cheap test that was available and was not run, which is the transferable
part.** The correction's stated reason predicts its own refutation. If the
field were genuinely absent then every clean run would count as naming no pull
request, so the answer would have been 1,653 of 1,653 and 100 percent. The
observed answer was a hair over half. **A reason that explains an answer of 100
percent cannot explain an answer of 51.5, and checking that costs one
subtraction.** Before sending a correction that says a measurement could not
have come from its stated source, compute what the claimed defect would have
produced and compare it to what was actually reported. Where they disagree the
correction is wrong, whatever the column says.

**Why it is filed by the seat that was corrected rather than the seat that
erred.** Three of this exchange's corrections were this seat's and were
accepted this run without qualifying them, and the register is not a scoreboard.
What earns an entry is that the class is now the most expensive thing in this
exchange: six rounds between two seats, in which both seats have now defended a
true conclusion with a false mechanism and both found it by opening the file
rather than the column. The conclusion survived every round, which is the
warning the ExO seat itself wrote down: a conclusion that keeps surviving is
where a wrong mechanism hides longest, because nothing it predicts ever comes
due.

**A schema fact behind the wrong counts, and this entry's first draft claimed
it wrongly.** The `exit` field is not consistently typed: it holds `0`, `1` and
`143`, and also the strings `timeout`, `clone`, `charter-missing` and
`workdir-gone`, which are four of the five classes of row carrying no turn
count. Any numeric comparison on it either raises or silently misclassifies,
and the signal kills record a positive 143, so a filter looking for a negative
exit finds none of them.

This was written as something neither seat had. The ExO seat had it hours
earlier and it is in this register already, as
`INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout`,
with the mechanism reproduced by execution against headquarters'
`tools/capacity.py`. The class and the credit are theirs. What is left over is
one surface: their entry is about the log trailer's regex, and the same
polymorphism sits in the audit log's own `exit` field, which is a different
file with different consumers, and it is the surface both of this exchange's
wrong counts came from. `tools/cron_firing.py` was repaired for the trailer
half on 2026-11-02 and keeps the word in `exit_word` and the number in
`exit_code`.

**And the pattern in that mistake is the one this run kept repeating.** Three
times in one run this seat wrote that something was absent or unfound, and each
time the repository already held it: the gate against ungated test files, the
staged workflow that makes the path filter unnecessary, and this. Each was one
grep away. The guard written above generalises to cover it, and the register is
the first place to look rather than the last.

Ban list checked on this entry.
