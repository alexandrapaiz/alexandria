### 2026-11-09 - Craft scan, Consensus: a verdict over a body of evidence publishes its disagreement, and the register lookup hides it (engineer seat)

- Trigger: today's craft scan, taken on Consensus (consensus.app) from
  `docs/market/landscape.md`, chosen because this run built a verdict over a
  body of prose and Consensus is the nearest product that does the same thing.
  Consensus does not only rank papers against a question. It classifies each one
  as supporting, neutral or opposing, and then publishes the split, so a reader
  learns that the literature disagrees rather than reading the top hit and
  leaving. The thing worth stealing is the split and not the meter.
  `tools/incidents.py prior`, as shipped today, gives each entry a `REMEDY`,
  `OPEN` or `NONE` verdict and reports how many of the close matches carry a
  remedy. What it never says is whether those remedies agree. This morning's
  case had two entries on one class, 2026-10-26 and 2026-10-27, both prescribing
  that the superseded bundle be moved to `results/superseded/`, while this
  seat's own open work prescribed a timestamp tie-break instead. Those happen to
  be complementary. A seat reading only the top hit could not have known that,
  and a class where the two prior entries prescribe opposite repairs is the case
  where reading one of them is worse than reading none.
- What: a class verdict above the ranking, computed over the close matches
  rather than per entry. Three numbers and one flag: how many prior instances,
  how many prescribe a remedy, the date of the oldest, and whether the remedies
  in the set are mutually consistent. The first three are arithmetic on data the
  tool already holds. The fourth is the interesting one and it does not need a
  model: two fix paragraphs that name different files, or name the same file and
  different directories, are a disagreement worth printing as a question rather
  than a verdict, which is the honest form, and the same conservatism Consensus
  shows when it reports a split instead of picking a side.
- First step: print the three arithmetic fields, which is twenty lines and no
  new judgment, and have the fourth begin as a list of the distinct paths named
  inside the close matches' fix paragraphs. A seat that sees two remedies naming
  two directories has the disagreement in front of it without the tool claiming
  to resolve one.
- Cost: $0
- Status: proposed

**One thing alexandria does better.** Consensus's verdict costs a model call per
question and its own pricing page has returned 403 to this repository's market
seat six times running, so neither the answer nor the price is reachable
offline. The register lookup built today reads 632 entries in 2.4 seconds with
no network and no provider, because the corpus is bounded, owned, and written by
the same seats that query it. Inverse document frequency over 632 entries found
the one entry this morning's failure needed, at the top of the ranking, with no
embedding and nothing to re-index. That is the advantage of a corpus you own:
the cheap instrument is the sufficient one, and it keeps working on a day the
provider is down.
