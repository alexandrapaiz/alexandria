### 2026-11-09 - Craft scan: Elicit publishes a reason per dropped paper, which is one step past the rule this seat shipped today

- Trigger: today's work is alexandria/exo's rule that a composition claim must
  publish its residual, and `tools/sentinel.py --compose` publishes it as one
  number named by nothing. The craft scan went looking for who else publishes
  what they left out, and the strongest answer in this landscape is not a
  feature somebody invented. Elicit shipped its systematic review workflow
  against PRISMA 2020 and exports the flow diagram with the report, and PRISMA
  2020 requires both halves: a count at every stage from identified to
  included, and an exclusion reason for each record dropped at full text.
  Elicit's own words are that it captures "exclusion reasons and supporting
  quotes from the paper for every screening decision" and exports "the PRISMA
  flow diagram, search strategies, and characteristics of included studies
  with the report". Read live at elicit.com/blog/systematic-review-for-prisma-2020.
- What: the thing worth stealing is the per-item reason rather than the count.
  A residual of 18.1 GiB says a reader has not looked at 18.1 GiB. A PRISMA
  flow says 2,104 records were screened, 1,998 were excluded, and here is why
  each of the 106 full texts that were read and dropped was dropped. The
  digest's version is one line per paper the window held and the issue did not
  carry, with the reason it was dropped, which turns a count a reader cannot
  check into a list a reader can argue with. It also makes a stalled cron
  obvious in the one place a reader is already looking, because a quiet week
  and a dead feed produce one count and two unlike exclusion lists.
  And an exclusion reason is cheap here in a way it is not for a human reviewer,
  because the pipeline already decides each paper's fate in code.
- What alexandria does better: the counterpart is the cap. Elicit's final
  report carries the 80 highest-scoring papers by default and 200 at the top
  tier, so a reader cannot tell whether paper 81 was close, and the screening
  score that ranked them is not published per paper. Every claim in a digest
  here cites the paper it came from and a provenance gate refuses the ones
  that do not, so the thing a reader checks is the claim and not the ranking
  that produced it.
- First step: one function in the digest builder that returns the window's
  papers with a `kept` flag and a reason string, and a test that the reasons
  partition the window exactly, which is `--compose` applied to the digest's
  own composition.
- Cost: $0.
- Status: proposed
