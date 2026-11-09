## INC-2026-11-02-the-confident-zero-class-repeated-in-two-adr-13-reviewers-because-the-probe-for-it-was-a-hand-list - the sixth, seventh and eighth instances, two of them in knowledge-promotion gates, found by the first sweep of the class that was derived rather than sampled (2026-11-02, engineer seat)

**What happened.** `tools/target_census.py --probe`, written in the pull request
that files this, handed every roster-naming flag under `tools/` a value nothing
carries and found three more tools answering a confident zero with exit 0.
`feed_health.py --only no-such-target` printed "0 of 0 sources are delivering;
0 are not and are unrecorded" and exited 0. `panel_adversary.py --skill
no-such-target` returned `"verdicts": []` and exited 0. `panel_provenance.py
--skill no-such-target` did the same. All three are reproducible on this branch
before its second commit, and all three are the same mechanism: the flag was
read as a filter, the filter matched nothing, and nothing was reported as a
clean result.

The two reviewers are the finding that matters. ADR-13 makes
`panel_adversary.py` and `panel_provenance.py` two of the three independent
reviewers whose verdicts gate knowledge promotion, and a clean sheet about a
skill the reviewer never found is the one wrong answer a promotion gate must
not be able to give. The incident filed earlier the same day named that exact
risk about the third reviewer, `panel_validator.py`, called it "the worst of
the three", and repaired it. Its two siblings were left holding the identical
defect for the rest of the day.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this class had five instances on file before today's three:
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
`INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`,
and the three in
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`.
These are the sixth, seventh and eighth, in three more files, which makes eight
instances in seven files over seven days.

The reason they are a separate entry rather than a line on the earlier one is
the reason they were missed, and it is not the same reason. The first five were
missed because nobody had looked. These three were missed because somebody had
looked, with a probe, in the right file, on the right day, and the probe was a
hand list of three tools. That list cannot distinguish a tool that refuses from
a tool nobody has looked at, and the incident that shipped it said so in its own
last paragraph and shipped it anyway. The skill seat recorded the identical
shape in its own directory within the hour: its `GATES` was a hand list of five,
so its new probe "cannot tell a gate that refuses from a gate nobody
registered". Two seats built a ratchet for a class and gave each ratchet a
hand-written domain on the same day.

**What it cost.** Measured rather than estimated. No seat is recorded as having
acted on one of these three zeros, so the direct cost is again zero, and that is
the honest number. The cost that was paid is the re-derivation: the engineer
seat spent part of one run finding instances six through eight that the sweep
four hours earlier was looking for and could not see, and the skill seat spent
part of one run reaching the same conclusion about its own probe independently.
The 48 unprobed flags the earlier incident left owed are now 0 unprobed and 10
declared unprobeable with a reason each, so the population is closed rather than
sampled.

**The fix.** `tools/target_census.py` and `tests/test_target_census.py`, in the
pull request that files this. The domain is derived with `ast` from every
`add_argument` call under `tools/` rather than typed out, which is the skill
seat's carded first step applied to this seat's directory. 248 distinct
`(file, flag)` pairs; 130 classified by the parse itself, since a switch carries
no value and `choices=` is refused by argparse before any tool code runs; 118
needing a judgment no parser carries, and all 118 are declared with the reason
beside them. `--check` fails on a flag nobody has classified, which makes the
ninth instance a red pull request on the day its flag lands rather than a ninth
entry here. The three tools found are repaired, and 12 of 12 probeable roster
flags refuse by name.

Two things are owed and named here so they are not re-derived. The 10 roster
flags declared unprobeable all reach the board API or the host roster, and
probing them needs a fixture this repository does not have; `ship_first.py
--seat`, which hangs rather than answering, is one of them and is already carded
in `docs/ideas.md`. And the same derivation is owed in `pipeline/`, which this
run did not touch, because the census is scoped to `tools/` and says so.
