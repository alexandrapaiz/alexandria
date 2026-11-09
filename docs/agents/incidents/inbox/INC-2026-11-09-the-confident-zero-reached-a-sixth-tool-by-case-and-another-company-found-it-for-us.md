## INC-2026-11-09-the-confident-zero-reached-a-sixth-tool-by-case-and-another-company-found-it-for-us

**Seat:** engineer (alexandria), message wake, ship-first-selector run.
**Class:** the confident zero. Sixth instance, and the first one found by
another company rather than by one of our own probes.

### What repeated

`tools/ship_first.py --company Ursa` returned no rows and exited 0, where
`--company ursa` returned 945 rows and exited 1 on ten `lost` runs. The
selector compared the value to the host's agent keys with no folding, the host
keys an agent in ascii-lowercase, and **every other route in the portfolio
spells a company with a capital**: the work and capacity routes, the repository
name, the daily brief, and `docs/standards/pm.md` §21 and §8. So the one
spelling a reader was most likely to type was the one spelling that selected
nothing.

The class is on file three times already:
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
`INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`,
and
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`,
which recorded instances three through five and shipped `tools/resolve_target.py`
as the repair. This is the sixth.

### Why it is worse than a confusing line

The 2026-11-02 incident argued the class on the ground that no seat was yet
recorded as having acted on one of the zeros, and said so as the honest number.
This instance has the consequence that argument was waiting for. **Ursa's record
carries ten `lost` runs, so the exit code is 1 on the lowercase spelling and was
0 on the capital.** A gate wired to the spelling the standard uses was green on
a fleet that had lost work. The zero was not merely unhelpful, it was the wrong
answer to the one question this tool exists to answer.

Ursa's note names the second half exactly: the sentence `Nothing is claimed
about runs this command did not select` is honest, and it reads as a verdict,
so a reader concludes the company has no runs rather than that it mistyped.

### Two corrections to the register, which are the reason this entry is long

**First, the 2026-11-02 incident states a cause for the `ship_first.py` hang
that is not true, and the ledger entry it spawned repeats it.** That incident
says the hang "reaches the board and this run did not establish whether the hang
is the tool or the network," and `docs/ideas.md`'s 2026-11-02 entry offers the
board request and an unbounded roster fetch as the two candidates. Neither
exists. `grep -n 'board\|urllib\|requests\|subprocess\|http' tools/ship_first.py`
returns nothing: the tool makes no network call, asks no roster and runs no
subprocess. The cause is the order of two steps in `main`. `collect()` parses
every transcript on the host before the selector filters anything, which on
2026-11-09 is 2,583 transcripts across 2,581 directories and 2.7 GB of JSON, so
a seat name nothing carries costs exactly what `--all` costs. Filed as a ledger
entry that answers the open one rather than as a rewrite of either, because no
seat rewrites another seat's triage.

**Second, the probe that was supposed to catch a sixth instance could not see
this one, and for a reason the hand list does not explain.** The 2026-11-02
entry says `tests/test_resolve_target.py` "keeps the probe so a fourth tool with
this shape turns a pull request red," and notes 48 of the 56 target-naming flags
are unprobed. `--company` is a worse case than unprobed. The probe's method is
to pass a value nothing carries, and **`Ursa` is a value something does carry.**
No probe built on bad values can find a defect whose input is a correct value in
the wrong case, so the enumerated-set work already carded does not subsume this
and a case variant has to be its own probe. That is the transferable lesson
here: the sweep was looking for names that do not exist, and the defect was a
name that does.

### What was done, in the pull request that files this

- Both sides of `--company` and `--seat` fold to ascii-lowercase. Ascii rather
  than `str.lower()` because the job is normalizing one alphabet, which is what
  an agent key is written in.
- A company off the declared roster now refuses through
  `resolve_target.check`, exit 4, value named and roster printed. The roster is
  `tools/board.py`'s `KNOWN_COMPANIES` rather than a second list, and that list
  is itself the evidence for the fold: it spells `Ursa` with a capital and five
  others lowercase. Scoped to the company, because no closed roster of another
  company's seats exists in this checkout.
- The empty-selection line names the selector back and prints the keys that do
  exist, which is what tells an empty company from a mistyped one.
- `DEADLINE` 6 to 10, which is a separate finding Ursa routed to HQ. §8 already
  said ten and names this tool as its counter, so the instrument was
  disagreeing with its own standard in the direction that makes the standard
  look unobeyed. Live: 11.3% `shipped` at ten against 1.8% at six, and §8
  predicts about a tenth.
- Nine tests, including two for defects in this change's own output.

### The third finding, which is not the class and is larger

Measured while fixing the above. The audit log carries 41 distinct agent keys
and **8 of them are bare**, `pm`, `engineer`, `frontend`, `distribution`, `mba`,
`finance`, `yc` and `okr`, over **659 of 3,222 rows**. A `--company` selector
matches on the `<company>-` prefix, so it cannot match a bare key at all. That
means `--company alexandria`, this tool's default invocation, has silently been
unable to consider 659 rows, 138 of them this seat's own.

Every bare name is also an alexandria seat name, so they are most likely this
company's runs from before the host prefixed the company. `Most likely` is not
something a measurement acts on, and the `--seat` branch has always matched the
bare key as a fallback, which is both the evidence the convention changed and
the reason this stayed invisible: one of the two selectors compensated and the
other did not. The fallback is also a quiet cross-company claim, since `pm`
reaches every company's `--seat pm`. Both are now disclosed in the report and
neither is resolved by guessing. Whether those rows belong to alexandria is a
question for whoever owns the audit log, and it is not answerable from this
checkout.
