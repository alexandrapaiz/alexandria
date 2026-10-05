# Hacker News — Show HN (launch day, 2026-10-13)

Rewritten 2026-09-30. The 2026-09-18 version offered one skill and its twelve
claims as the library's whole receipt, which is now wrong by five skills, and
it did not have the retrieval measurement or the usage review to point at.
Every number has a row in `../claim-ledger.md`.

## The venue read, and what changed about it

Hacker News distrusts a pitch and rewards a thing that can be opened. It gave
a hand-curated skill marketplace a cold reception on 2026-09-17, and the top
comment on that thread is the pre-mortem for this post: "Why would I buy a
markdown file that someone most likely got an LLM to generate while I can just
simply get my own LLM to generate a similar one for me for free?"
(news.ycombinator.com/item?id=49743459). The founder conceded in the thread
that AI-generated skills "are usually pretty bad."

That comment is correct about the file and wrong about the product, and the
post has to answer it before anyone asks. The answer on 2026-09-18 was a
promise about an evidence trail. The answer today is two measurements and one
outside review, which is a different kind of answer and the reason this draft
is shorter than the one it replaces.

**One place this venue and the company standard pull against each other.** The
standing rule on public copy says sell the outcome and do not explain the
mechanism, and it was written from her line-by-line verdicts on landing-page
copy. On this venue the mechanism is the outcome, because a reader here buys
the method or nothing. This draft keeps the mechanism and obeys the two rules
that carry no venue exception, which are the serious register and the sentence
form. Flagged rather than decided: see the run note in this pull request.

**Post as Show HN**, weekday, mid-morning Eastern. There is a working repo and
shipped artifacts, which is what Show HN is for.

## Title, her call

```
Show HN: Alexandria - six agent skills, each citing the papers behind them
```

```
Show HN: An agent-run research library that publishes what it got wrong
```

The second is the title only if the Obsolescence Report runs, and in that case
it is much the better of the two, because it is the one claim on the front page
that day that nobody else can make. Use a plain hyphen in either, never a dash
character.

## Body

```
Alexandria reads AI research and turns the findings that hold up into skill
files an agent can load. It runs as a set of autonomous agents with written
charters, each opening pull requests against a public repository, and I merge
them or I do not.

Six skills are live. Each one lists the papers it was taken out of, with links
to the full text, so you can follow any recommendation in a skill back to the
work behind it and disagree with it on the evidence. Each also lists claim
numbers, and I should say plainly that those are internal references which only
resolve on a paid page, so the paper list is the part you can audit for free.

Two measurements, because I would rather hand you those than describe the
library.

A retrieval test on 2026-09-29 scored 40 of 43 cases, reliability 0.93 with a
95 percent interval from 0.81 to 0.99. It measures whether the right skill gets
picked for a question and whether the others stay quiet, against eight decoy
skills, with the scoring policy written down before the run. The three failures
are in the output with their prompts and their scores, in
skills/_validation/results/.

One of the six also carries a recorded trial from 2026-09-12 where loading the
skill changed the model's recommendation. Bare, it endorsed fine-tuning a
smaller model on a stronger one's trajectories. With the skill loaded it
refused, cited the regression the papers report, and prescribed a different
approach. The other five skills do not have that trial yet. That gap is real
and it is the next thing I am working on.

There is also one independent review of a skill in actual use, from a session
that was not mine, on a three-stage build plan. It records one design decision
changed, one procedure adopted, two decisions confirmed, and it records that
its own baseline was not clean because the reviewer had read the file four days
earlier. I left that caveat in the file rather than out of it.

On the market-a-markdown-file objection, which I think is the right objection:
you are right not to pay for the file. The file is not the product. What a
prompt cannot produce for you is a record of which claims later got
contradicted, because that is made of edges accumulated over months against
papers as they arrive. You can generate a skill today. You cannot generate the
part that tells you next March that one of its recommendations stopped being
supported.

The weekly digest is free and arrives in full, and I am not paywalling the
writing, because a written summary of the week is genuinely a commodity. What
costs money is the library, at $20 a month. The archive holds one issue today.
The pilot before it was pulled because it was not good enough to be the first
thing you read.

Repo: github.com/alexandrapaiz/alexandria
Site: [SITE_URL]

Happy to take the hard questions, including why you should trust a record
graded by the thing that built it. The repository is public so that you do not
have to take my word for any of it.
```

## Answers to prepare, hers to use or ignore

- **"Six skills is not a library."** Agree without softening it. Six files, one
  evidence standard applied to all of them, and a target of twelve by the end
  of the year that is a target rather than a fact. Judge the pipeline on
  whether it produces more.
- **"Only one has the A/B result, so the other five are unproven."** Correct,
  and it is in the post because of that. The retrieval score covers all six and
  measures a different thing. Do not blur the two under pressure; the blur is
  the only way this thread goes badly.
- **"An LLM wrote the evidence trail, so why trust it."** The claims cite real
  arXiv identifiers and the edges are checkable against the papers. Say that
  and stop. Do not oversell it, and do not claim outside verification, which
  the library does not have.
- **"Agents writing marketing copy about themselves."** True, and the charter
  saying the agent never sends anything is in the repository at
  prompts/sales-agent.md. The interesting part is not that an agent wrote it,
  it is that the charter is readable and you can check whether it was followed.
- **"How is this different from a paper-search tool."** Different job rather
  than a better one at theirs. Elicit and Consensus find papers. This decides
  which findings to act on and ships the acting procedure. Never claim to beat
  them at search.

## Never in this thread

No subscriber count and nothing that implies one. No paper count carrying the
verb "read" unless it is the full-read count beside the arriving count. No
"growing fast", no roadmap stated as present tense, and no comparison that
claims to beat a research tool at its own job.
