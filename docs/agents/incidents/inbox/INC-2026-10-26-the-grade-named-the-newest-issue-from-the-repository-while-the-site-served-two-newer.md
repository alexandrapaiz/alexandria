## INC-2026-10-26-the-grade-named-the-newest-issue-from-the-repository-while-the-site-served-two-newer — the fourth time a grade read the artifact in front of it without asking whether that was the artifact (2026-10-26, writer seat)

**What happened.** Writer runs 49 and 50 each opened their graded review with
the sentence that `site/content/issues/2026-W39.md` was the newest issue the
runtime could reach. Run 50 went further and argued, correctly from that
premise, that re-deriving run 49's verdicts on it would be waste, so it graded
no artifact and spent the run upstream in the generator instead. The premise was
false. The archive directory holds two files and the live site was serving
three issues, newest `2026-W42`, which no run had graded.

```
curl -s https://libraryofalexandria.dev/library | grep -oE '2026-W[0-9]+'
2026-W39   2026-W40   2026-W42
python3 tools/delivery_health.py --surface press --no-notify
  ok  press  2026-W42 is written, by kimi-k2.6
```

Neither command needs a credential. `NEON_RO_URL` is unset in this runtime and
both runs recorded that fact, which is true and which says nothing about the
public site or about the public `/api/delivery` endpoint that
`delivery_health.py` reads. The writer charter's step 1 says to read "the
newest published issue in the repo **or site**". Both runs read the repo.

**Why it is in this register.** The standing rule, and this is the fourth
occurrence of one class rather than a new defect. The canon's own grading
procedure records the first three in its own words, each added after it
happened: which COPY of an issue to grade
(`INC-2026-09-30-standing-defect-unverified-for-three-grades`), which GENERATOR
wrote it, forwards, added 2026-10-10, and which EDITION the newest artifact is
(`INC-2026-10-12-the-grade-could-not-tell-an-edition-from-an-archive`). That
third entry's own closing sentence is the diagnosis of this one: "Each one was a
check that read the thing in front of it and never asked whether that thing was
the thing it was supposed to be reading." This is which SURFACE, and it is the
first of the four where the correct artifact was free to obtain and nobody
asked.

The reason the class survived three entries is worth one line, because it is not
inattention. Every remedy the three entries adopted is a question about the
artifact, and the procedure's first question is "which artifact, by path". A
path is a file, so the whole check reads as a question about the repository, and
a seat that answers it carefully is still answering it inside the repository.

**What it cost.** Two graded reviews, which is two of this seat's runs. Run 49
graded a 27-day-old print in full. Run 50 correctly declined to grade it again
and therefore graded nothing, so the product had no graded edition for two
consecutive runs while two ungraded editions were public. The findings in this
run's grade of `2026-W42` are the measure of what that cost: law 8 at three of
ten links against four of four on `2026-W39`, `shapes 1` against `shapes 2`,
and law 13 passing by command for the first time on any artifact, which is a
merged repair of this seat's own that nothing had been able to confirm was
working.

**The fix.** Ban list 141 in the same pull request, with the command as its
ending: `tools/delivery_health.py --surface press --no-notify` is the first step
of a grade from here on, ahead of the three shas and ahead of the edition
question, because it answers which surface in one line and needs nothing. The
canon's grading procedure names "the newest issue" in four places and the
command now sits above them in the order of work.

What is not fixed, and it belongs to another seat. The archive in the
repository is two issues behind the site, so `2026-W40` and `2026-W42` are
published to readers and absent from `site/content/issues/`. Every gate this
seat runs over the archive reads that directory, which means `measure`,
`devices`, `standalone` and `firstuse` all describe a product two editions
stale unless a path is passed by hand. That is the engineer's surface and it is
reported rather than filed here, because this run cannot tell whether the
directory is meant to be a mirror of the record or a build input.

**Fifth sighting, 2026-10-26, writer run 54, and the remedy above is why it is
here.** The entry closes with the sentence that the gates read the archive
directory, that `measure`, `devices`, `standalone` and `firstuse` therefore
"describe a product two editions stale unless a path is passed by hand", and
that this is "the engineer's surface and it is reported rather than filed here,
because this run cannot tell whether the directory is meant to be a mirror of
the record or a build input."

Three of those sentences are right and the conclusion does not follow from
them. The commands do not need the directory to change and they do not need
that question answered. They need a source, and the product publishes one with
no credential on it. Run 54 added `editions` and a `--live` flag that reads the
served pages and un-renders them to the markdown the press stored. The
un-renderer is proved rather than asserted: for every served week the
repository also holds, the gate diffs the un-rendered page against the file,
and `2026-W39` round-trips exactly.

What that cost, measured rather than estimated, in the four hours between the
fourth sighting and this one:

| the gate | what it says when it can finally read the editions |
| --- | --- |
| `links` | `2026-W42` prints ten paper links, nine of them to the abstract, and arXiv serves the full text for seven of those nine. Her ruling of 2026-09-19 in her own words, "you didn't show me the paper" |
| `measure` | `2026-W40` prints three headings in the shape canon law 12 forbids, which is the ruling she has given twice. The detector for it has existed since 2026-10-06 |
| `marks` | eleven semicolons across the three served editions against a target the generator states as zero with no budget |
| `devices` | all three served editions carry no list and no written turn |

So the entry's own framing is the thing that repeated. The first four sightings
were a grade reading the wrong artifact. The fifth is the REMEDY for that
reading stopping at the reading: a command was added to tell a run which
edition is newest, and nothing was pointed at it. The ruling she gave twice
printed to readers on 2026-10-05 with a working detector in the repository and
twenty-one days of grading in front of it.

The general form, and it is narrower than L-A9. When a scope defect is fixed by
telling the next reader where to look, ask which COMMANDS were looking in the
old place, because a reader can be instructed and a glob cannot.
