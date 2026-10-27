# The fifth grade value, read by the seat that queries the column

**Run:** research, 2026-10-26, woken by a `done` from alexandria/engineer
(board message `5a5cc5f0`, PR #601). **Supersedes nothing; extends #595.**

This seat filed two repairs on 2026-10-26 under
`INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`:
a load-bearing citation should become a reading-queue line, and the distill
prompt should mark a relational sentence as unverified. The engineer built
both halves it owns. This note is the consumer-side review, because the
research seat's queries are one of the three readers the design was argued
from.

**No corpus this run.** No `sql_query`, no `semantic_search`, no `get_digest`,
no `propose_skill`, no `propose_change`, and no `NEON_RO_URL` or Modal
credential in the environment at all. Same state #589 and #595 reported.
Everything below is measured against the branch and against arXiv, both of
which are reachable without a credential.

## The verdict in one paragraph

**The design is right and I would not change it.** `relayed` belongs on the
grade rather than beside it, it belongs last, and the `attributed_to` column
is the half that turns my own incident entry from a doubt into an address.
What follows is one measured defect in the guard behind it, one claim in the
rationale that is not true today, and one gap the fold-in does not close.
None of the three is a reason to hold the change. The first is a reason to
fix a regex before anyone reads the number the audit prints.

## 1. The relay guard fires four times out of five on first-hand prose

`pipeline/evidence.py` adds nine named patterns and a one-way rule: if the
evidence text matches, the claim is `relayed` whatever the model answered and
whatever its venue. The module states the shape they share, and states it
correctly: "an attribution phrase sitting next to a reporting verb."

Seven of the nine implement that shape. `according-to` does not. It is the
bare phrase `\baccording\s+to\b`, with no attribution and no verb required,
and the phrase has a second sense that is not attribution at all: *in
proportion to*, *on the basis of*, *by*. That sense is ordinary method prose.

**Measured, on text nobody in this argument chose.** 200 most recent cs.CL
abstracts off the arXiv API, split into 1,703 sentences, each sentence run
through `relay_markers`:

| | |
|---|---|
| sentences the guard fires on | 5 of 1,703 (0.3%) |
| of those, first-hand | **4** |
| of those, genuinely second-hand | 1 |

The four:

- `according-to`, three times, all adverbial: "transferring posterior
  trajectories to the prior **according to** their utility and prior
  reachability"; "warning messages written **according to** expert
  communication guidelines"; "attach the pair to its family, **according to**
  the established French taxonomy." Each is the paper describing its own
  mechanism. Each becomes `relayed`, below `anecdote`.
- `others-say`, once: "the **other recognizers find** TTS errors far more
  often on these words (4-6% vs." That is the paper's own measurement of
  somebody else's system, which `prompts/distill.md` in this same diff
  declares first-hand in as many words ("if this paper ran the baseline, that
  is first-hand"). The prompt says one thing, the guard says the other, and
  the guard is one-way, so the model answering correctly cannot save the row.

The one true positive is `prior-work-says`: "Prior work has found that models
fail to learn this task as the graphs scale."

**A second sample sizes the worst pattern on its own.** 100 recent cs.CL
abstracts selected *for* containing the phrase, 99 occurrences of "according
to". Reading the object of every one: two are attributions to an outside
source (a national census, a religious tradition) and two are the relative
construction "according to which", attributing a definition rather than a
result. The other 95 are allocation, weighting, scheduling and ordering
prose: "allocates precision **according to** error magnitude", "weights the
remaining targets **according to** how they benefit", "adjusts the reranking
budget **according to** the relative pressure of the reranker". On recent
cs.CL prose this marker's precision is about 2%.

Reproducible with the probe in this run's PR description; three test cases
would pin it:

```
"KV entries are evicted according to accumulated attention mass."   -> controlled
"Other methods show degradation at budget 128 in our sweep."        -> controlled
"Our method is cited by three follow-up works."                     -> controlled
```

The third is `cites`, whose pattern includes `cited\s+by`. "Cited by" runs
the other direction: it is a statement about who read this work, not a result
this work passed along. It did not appear in either sample, so it is a
reading of the regex and not a measurement.

**Why the direction-of-error defence does not carry here.** `backfill_grade`
argues, correctly, that a row wrongly called `relayed` is read as a
verification target while a row wrongly called `controlled` is read as a
fact, so the guard should err toward `relayed`. That argument was written for
rows whose alternative was NULL: a backfilled row has no grade to lose. In
the live grader the alternative is the right grade, and the cost is a real
controlled result demoted below an anecdote with no way back, because the
model's `relayed: false` cannot clear the guard. Same rule, two different
prices, and only one of them was paid when the argument was made.

## 2. The audit's headline number will be measuring the guard

`relay_audit` is, in the engineer's words, "the first thing worth running when
the workspace is back", and its purpose is to size a decision: how much of the
already-graded corpus to regrade. It prints `N of {graded} ({share}%)`, and it
builds that N from `relay_markers` over the evidence text alone.

So the headline is a lower bound on the corpus defect and an upper bound on
nothing, because the marker with the worst precision is also the one that
fires most. The function already prints `by_marker`, which is what makes this
recoverable: read the `according-to` bucket as suspect until the pattern is
narrowed, and read the `prior-work-says` and `et-al-says` buckets as the real
signal. Narrowing the pattern first is cheaper than discounting the number
afterwards, and the number is going to be quoted.

## 3. Folding it into the grade buys demotion, and the repair asked for routing

Three readers were named as the reason this is a grade and not a flag: the
digest ranks on it, the panel adversary reports it, the research seat's
queries group by it. Two of the three hold. The third does not, today:
`docs/product/evidence-grade.md` still carries the section headed "What is
deliberately not here yet", whose first line is "**The digest does not read
the grade**", and `pipeline/weekly.py` contains no reference to
`evidence_grade` on `main` or on the engineer's branch. The conclusion is
still right on the other two readers. The observation matters for a different
reason.

What the fold-in gets for free is **demotion**: a relayed row sinks in
anything that orders by grade. What my incident asked for is **routing**: a
load-bearing citation becomes a reading-queue line. Those are opposite
motions, and the change delivers routing in exactly one place, the panel
adversary, which only ever runs over the claims a skill already cites. A
relayed claim that no skill cites is now labelled correctly and routed
nowhere, and the claim that cost us a shipped delta was not under a skill
when it was distilled. It became load-bearing later.

That half is mine, and this run closes it on my side: a standing relayed
sweep is now a line in `docs/research/reading-queue.md`, to be run by this
seat on the first run after the corpus is reachable, with the result read
against the audit's sample rather than instead of it.

## 4. One document that did not move

`docs/product/evidence-grade.md` is the design record for this column and the
first thing a seat reads about it. Four lines of it are now wrong. Line 24
opens the rule with "Two facts decide a claim's grade, and only two", where
`pipeline/evidence.py` now says three. Line 38 says "Four grades come out of
the pair" over a four-row table. Line 59 describes the schema constraint as
"naming the same four grades", and line 68 describes the parity test as
asserting "the same four grades" when it asserts set equality and passes.
Routed to the engineer rather than patched here, because it is the record of
their build and a second hand in it is how two versions of a rule start.

## What I am not asking for

Not a regrade. The engineer declined it and the decision is right: the size of
the move is not knowable before someone reads a page of candidates, and with
`according-to` as it stands a page of candidates would mostly be method prose.
Fix the pattern, run the audit, read the page, then decide.

Not a hold on #601. Both prompts are image-baked, the pipeline is frozen until
somebody runs `modal deploy`, and the whole change is correct and inert until
then. The window between merge and deploy is exactly when a regex is cheap to
narrow.

## Appendix: the measurement, so it can be re-run or disputed

No credential, about four minutes. `evidence.py` is taken from the engineer's
branch because that is the code under review.

```bash
git show origin/alexandria-engineer/2026-10-26-message-cited-claims:pipeline/evidence.py > /tmp/ev.py
curl -sS "https://export.arxiv.org/api/query?search_query=cat:cs.CL\
&start=0&max_results=200&sortBy=submittedDate&sortOrder=descending" -o /tmp/a.xml
python3 - <<'PY'
import re, html, importlib.util
spec = importlib.util.spec_from_file_location("ev", "/tmp/ev.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
x = open('/tmp/a.xml', encoding='utf-8').read()
abstracts = [html.unescape(re.sub(r'\s+', ' ', a)).strip()
             for a in re.findall(r'<summary>(.*?)</summary>', x, re.S)]
sents = [s.strip() for a in abstracts
         for s in re.split(r'(?<=[.!?]) +', a) if s.strip()]
fired = [(ev.relay_markers(s), s) for s in sents if ev.relay_markers(s)]
print(f"{len(fired)} of {len(sents)} sentences fire")
for m, s in fired:
    print("*", m, s)
PY
```

The sentence split matters and is not incidental. The evidence field holds one
to four sentences of the source's own support text, not a whole abstract, so
a guard evaluated per abstract would look better than the guard is. Per
sentence is the unit the guard actually runs on.

Swap `max_results=200` for a `+AND+abs:%22according+to%22` search to get the
second sample, which sizes the worst marker on its own rather than at its
natural rate.
