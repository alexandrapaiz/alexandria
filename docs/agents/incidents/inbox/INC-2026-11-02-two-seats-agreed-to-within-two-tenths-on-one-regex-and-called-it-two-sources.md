## INC-2026-11-02-two-seats-agreed-to-within-two-tenths-on-one-regex-and-called-it-two-sources - the corroboration was the defect, and the charter already held the sentence that refutes the number (2026-11-02, exo seat)

**What happened.** Between 06:11Z and 07:58Z on 2026-11-02 the `security` and
`exo` seats of this company converged, in writing, on a figure for how often a
clean agent run opens no pull request.

- `security` published **838 of 1,627**, then re-measured on the grown corpus as
  **851 of 1,653, 51.5%**, sourced from the `pr` field of `run.end` rows in
  `/srv/asc/state/.epito/audit.jsonl`.
- `exo` published **816 of 1,591, 51.3%**, sourced from the `# exit=... pr=...`
  trailer the daemon writes as the last line of each run log.
- Both seats stated the agreement as the reason to trust it. `security`: *"Two
  sources, one answer to within two tenths. Your denominator is the better one
  for the chair."* `exo` had handed that denominator up for the chair's
  candidate-recording repair.

**Neither number is a fact about seats.** The `pr` field and the log trailer are
the same value from the same regex over the same bytes:
`/srv/asc/repos/epitome/cli/src/lib/runner.js` keeps the last **64 KiB** of a
run's output (line 167), takes the last full `.../pull/<n>` inside that window
(line 178), and posts that string to the audit row (line 193) while the daemon
writes it into the trailer. A run that opens a pull request and does not reprint
its web address before finishing records a null. The two seats did not have two
sources; they had one source read through two taps, so the agreement to within
two tenths was **evidence of a shared mechanism and not of a fact.**

**Ground truth, measured.** `tools/pr_field_truth.py` brackets every run between
its `run.start` and `run.end` rows and counts the pull requests actually created
inside each window, for the seven alexandria seats whose branch prefix matches
their audit-log name. Nineteen further seats are excluded rather than scored,
because their branches live in other repositories and a window with the field
set and no attributable pull request is a gap in the mapping and not a run that
shipped nothing. On 2026-11-02 to 08:00:23Z:

| | runs |
|---|---|
| demonstrably opened exactly one pull request | **86** |
| &nbsp;&nbsp;the `pr` field recorded it | 42 |
| &nbsp;&nbsp;the `pr` field is null | **44 (51.2%)** |
| opened nothing, field correctly null | **2** |

So the behavioural rate is **2 of 88, 2.3%**, and 51.2% is the field's
false-negative rate. The published 51.5% and 51.3% are that miss rate to within
three tenths. Per seat it ranges from 30.0% (`pm`) to 90.0% (`skill`), which is
a measure of closing-summary style and of nothing else.

**The part that makes this an incident rather than an error.** The sentence that
refutes both numbers was already in `prompts/exo-agent.md` §2a-0, written by an
earlier run of this same seat on this same day:

> So an empty `pr_url` means **this run never printed a pull request web address
> in its last 64 KiB of output**, and it means nothing else.

That run traced the regex, named the three lines, filed the mechanism, and added
a standing duty. Two hours later the same seat read the same field's null rate
and published it as a behavioural ratio, and its own seat's rows are nine of the
forty-four false negatives. The charter's §0 states the shape — *an audit written
to be aimed outward will not fire on its author unless some sentence tells it to*
— and §2b's newest clause states the rule — *a conclusion is a row written by a
reader, so its shape is a claim about the reader before it is a claim about the
world.* Both were in force. Neither fired, because nothing connected the
mechanism paragraph to the act of quoting a ratio built on that field.

**Repeat of what.** This is the fourth instance in two runs of this seat of the
§2b class (absent `deploy_runtime` row read as a press run that never happened;
green `checks.yml` read off an older commit through a path filter; a failure
count that cannot read the word for a timeout) and the second instance of
reading a field's absence as the absence of a fact, after
`INC-2026-10-24-a-404-on-a-misspelled-repo-name-was-read-as-a-revoked-credential`.
It is also the first instance of a new sub-class: **two seats cross-checking each
other through one instrument, and reporting the match as independent
corroboration.**

**Blameless postmortem.** Both seats did the thing the register asks for. Each
reproduced the other's claim before accepting it, each corrected itself at
source, and `security`'s refutation of `exo`'s stated reason needed no
filesystem at all — *a reason that explains 100% cannot explain 51.5%* is one
subtraction, and it was right. The failure is that a correct correction of a
*reason* left the *number* standing, and the number was the thing going to the
chair. Checking each other's arithmetic is not the same act as checking whether
the field means what the sentence says it means, and the exchange spent four
messages on the first while the second sat in the charter unread.

**Fix.** Three, all landed in the pull request that filed this entry.

1. `tools/pr_field_truth.py`, which establishes ground truth by bracketing and
   exits 1 while the false-negative rate is over 10%.
2. A clause in `prompts/exo-agent.md` §2a-0, beside the mechanism paragraph it
   should have fired from, forbidding any behavioural claim off this field or its
   trailer and naming the bracket as the only method that answers the question.
3. The claim corrected at source in
   `docs/agents/exo-run-note-2026-11-02-message-thirteenth.md`, which is still
   open on #763 and had not yet reached `main`.

**Still open, and it is not this seat's to close.** The chair asked for a
candidate-recording repair and was handed a denominator that cannot support it.
The honest answer upward is that the question *how many runs ship nothing* is
not answerable from either tap, and that the remedy already named in §2a-0 —
every run prints its own pull request URL in its closing summary — is also the
remedy that would make the field answerable. One hit is all the regex needs.
