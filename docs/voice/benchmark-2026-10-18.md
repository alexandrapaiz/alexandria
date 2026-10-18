# The blind prose benchmark, scored

**Headline: the rewritten lead beats the sent lead on every gate a count can
hold, eight to three, and ties it on the one axis the market actually wins on.
That tie is the finding, and it is not a prose problem.**

Writer seat, 2026-10-18. Board item `7e1841c0`, the one item in this seat's
lane, carried since 2026-10-05.

## What was missing, and what this page supplies

The board item asks for three things. A benchmark against TLDR AI, Import AI,
The Batch and the Morning Brew register rather than TLDR AI alone. A rewrite of
the first section side by side with the original. And a written score for both,
so the owner can pick one in a single read.

The second of the three was delivered on 2026-10-05 in
`docs/voice/enjoyability-benchmark-2026-10-05.md`. That page put the two
versions next to each other and then asked her to rule with nothing to rule
on, because it carried no score. Thirteen days later nobody has picked, and a
page that asks for a judgment without supplying the instrument is the reason
why. The run of 2026-10-16 reached for the first of the three, found that
`docs/market/newsletter-prose-guide.md` is still eleven lines of placeholder,
and correctly refused to invent the market seat's study.

This page supplies the score, and it supplies the market comparison from a
source that exists. The four registers were read live by this seat on
2026-09-19 and the passages are quoted and attributed in
`docs/voice/prose-benchmark-2026-09-19.md`. Those passages are the anchors
below. **No register was read live today**, so every letter in their rows is
carried from that read rather than re-earned, and the rows are here to place
our two versions on a scale rather than to update anybody's grade but ours.

## The subject

The opening and the first section of 2026-W40, the issue sent on 2026-10-05
and still the newest the press has produced. Two versions, both printed in
full in the 2026-10-05 page: the one a subscriber received, and the one this
seat rewrote from the same papers and the same numbers.

The two bodies were cut out of that page and measured on their own, at
`/tmp/as-sent.md` and `/tmp/rewritten.md`. They are not committed, because a
finished-looking issue sitting in this directory is how a worked rewrite became
the next morning's prose once already.

## Part one, the measured score

`docs/voice/check_voice.py` holds ten gates. Two of them cannot be measured on
an excerpt, because both count links against the reading list and neither
version contains one, so they are excluded rather than scored as failures. The
other eight:

| gate | target | as sent | rewritten |
|---|---|---|---|
| semicolons | 0 | 1 | 0 |
| em dashes | 0 | 0 | 0 |
| non-ASCII, no exception | 0 | 0 | 0 |
| shapes the writer added | 3 or more | 1 | 4 |
| paragraphs over 100 words | 0 | 1 | 0 |
| list blocks | 1 or more | 0 | 1 |
| sections over four paragraphs | 0 | 0 | 0 |
| headings carrying a colon | 0 | 1 | 0 |
| **passed** | | **3 of 8** | **8 of 8** |

`measure` adds the figures underneath the gates. The sent lead is 398 words in
7 paragraphs, the longest of them 109 words, in one kind of block. The rewrite
is 418 words in 15 paragraphs, the longest 60 words, in four kinds of block.
Twenty more words, and the reader meets them eight paragraphs further apart.

That is the whole of the measured difference, and it is one-sided. There is no
gate on which the sent version is the better one.

## Part two, the judged score

The five axes are the ones the 2026-09-19 benchmark defined off the canon, so
the two pages stack. A sixth is added here, because the owner's ruling of
2026-09-24 made shape a failing grade on its own and a counter now holds it.

| | Voice | Structure | Compression | Evidence | Warmth | Shape |
|---|---|---|---|---|---|---|
| Morning Brew (carried) | A | A | A | C | A | A |
| Import AI (carried) | A- | B+ | B- | A | B+ | B |
| The Batch (carried) | B | B- | A- | A | B | A- |
| TLDR AI (carried) | D | C | A | C- | F | C |
| **2026-W40 as sent** | **C** | **C** | **C-** | **B-** | **B-** | **F** |
| **2026-W40 rewritten** | **B** | **B+** | **B** | **B-** | **B** | **A-** |

One line of defence per row that is ours.

- **Voice, C to B.** The sent lead writes "You ship agents that improve
  themselves or you ship agents that stay safe", which is a person talking, and
  then spends the next nine sentences in the passive register of a summary. The
  rewrite holds the second person into the body, "what it changes for a builder
  is who does the tuning", and still nobody signs either one. An A on this axis
  belongs to newsletters with a name at the bottom, and we have made the
  decision not to have one.
- **Structure, C to B+.** Both open on a thesis and descend into results. The
  rewrite earns the step for two written turns that come from the day's own
  material rather than from a fixed set, which is the Morning Brew move and not
  The Batch's.
- **Compression, C- to B.** 109 words in a block against 60. Morning Brew keeps
  an A here on four short paragraphs carrying a succession, and neither of ours
  is close to that.
- **Evidence, B- and B-, unchanged.** This is part three.
- **Warmth, B- to B.** The sent version greets the reader and the rewrite
  greets the reader, both under the same rule. The rewrite gets the step for
  following its result with a line that has no number in it, which is what
  being carried through feels like.
- **Shape, F to A-.** One kind of block against four. The canon calls one kind
  a failing issue outright, so the letter is the law's rather than this seat's.

## Part three, the tie, and why it is the finding

**Evidence is the only axis where the rewrite does not improve on the issue it
rewrites, and it is the axis the market wins on.**

The Batch, read 2026-09-19: "Meta says it evaluated Muse Spark 1.3's ability to
resist prompt injections using an unpublished dataset, and it has not provided
accuracy metrics for the classifiers that screen incoming data."

That sentence names a measurement the paper did not report. Here is every
evidence grade 2026-W40 printed, read off the stored body by the grade of
2026-10-05:

```
[4]  The authors' own experiments, not yet replicated outside the group.
[8]  The latency numbers are reproducible; the breach narrative is not
     independently verified.
[9]  The authors' own experiments on GUI agents; no replication yet.
[10] The authors' own traffic and benchmarks; no external replication.
[11] The authors' own experiments against their Meta-Harness baseline.
[17] One held-out backbone family, 24 test cells, no replication yet.
[18] Five rounds on real Adobe traffic, ablations included, no external
     benchmark.
```

Six of those seven say who ran the work or who has not repeated it. One of
them, the last, names a measurement that is absent. And the rewrite, written by
this seat with the rule in front of it, wrote "This is the group's own work and
nobody outside it has repeated the result", which is the sixth kind again.

The generator asks for both halves. `prompts/digest.md` says the grade is "how
strong the number is, and, where the payload supports it, say what the work did
not measure", and then, correctly, "never invent an omission". The second half
has a condition on it and the condition is never met. `pipeline/distill.py`
stores `claim`, `evidence`, `topics` and `procedure`. Every one of those four
records something the paper did, and nothing in the payload records anything
the paper left out. So the model is asked for an absence, handed only a list of
presences, and told not to make one up. The honest thing left in reach is who
ran it, and that is exactly what seven grades out of seven reached for.

**This is not a seventh wording of the rule, and this seat is not going to
write one.** It is a missing field, so it goes to the engineer in
`docs/ideas.md` under the charter's structure-watch clause. The one thing the
prompt can usefully do, and the only change this benchmark makes to it, is to
stop the substitution: when the payload holds no omission, the grade is the
first half alone and the second half does not get filled with provenance
wearing a limitation's clothes.

Note also what law 6 of the canon offers as its worked example of an in-line
grade: "authors' own experiments, not yet replicated". That is the first half,
and it is the right example of the first half. It is not the second half, and
nothing in the canon claims otherwise.

## The pick

**Forward the rewrite.** One candidate, which is the job.

It wins eight gates to three, it wins five of the six judged axes and loses
none, and the axis it ties on is tied because of a database column rather than
because of a sentence. There is no reading of the instrument in which the sent
version is the one to send.

The cost of picking it, stated plainly, because a pick with no cost is a pick
nobody needed. The devices in the rewrite stop being available and become the
shape of every issue. An issue with one kind of block fails from that day
rather than getting a note. A result that arrives without a plain line after it
fails. The generator already carries all six devices as rules, so the pick does
not add work to the machine. What the pick adds is that the next grade scores
their absence as a failure instead of a preference, and this seat stops asking.

And the honest caveat, which is the same one the 2026-09-19 page ended on and
has not aged a day. The rewrite was written by hand. The generator carries the
rules that would produce it, fifty-one anchored enforcements of them, and the
press has not printed an issue since 2026-10-05. **Nothing on this page is a
measurement of the generator. It is a measurement of two texts, one of which
the generator wrote.** The first issue the patched generator prints is the real
benchmark, and the thing standing between this seat and that number is a press
that has not run for thirteen days.

## Sources

- The two bodies: `docs/voice/enjoyability-benchmark-2026-10-05.md`, quoting
  the stored `digests` row for 2026-W40 at prompt sha `c48d09624161`.
- The grade inventory: `docs/voice/reviews/2026-10-05.md`.
- The four registers, read live 2026-09-19 and quoted with their issue dates:
  `docs/voice/prose-benchmark-2026-09-19.md`.
- The gates: `python3 docs/voice/check_voice.py measure <path>`, and `axes`
  for the targets, run on 2026-10-18.
