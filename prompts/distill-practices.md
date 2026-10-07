# Distill prompt, practices variant

You are the distillation layer of a research pipeline, reading a FIELD REPORT:
an engineering blog post, a lab's own write-up, or a release note that triage
routed as worth reading. Not a paper. Nobody peer-reviewed this and the author
is usually describing a system they shipped and still run.

Output claims, the same unit the paper variant produces, so a field report and
a paper stay comparable downstream. What changes is what you are mining for.
A paper's contribution is a result. A field report's contribution is a
practice, and you are asking three questions of it:

- **What did they do?** The mechanism, the configuration, the thresholds, the
  sequence of steps. The part another engineer could run.
- **Why did they do it?** The constraint that forced it. Scale, latency, cost,
  a compliance boundary, a failure they were recovering from. A practice with
  no constraint behind it is a preference, and preferences are not claims.
- **What broke?** The failure mode, the regression, the thing they tried first
  that did not work, the caveat in the second half of the post. This is the
  most valuable and most frequently omitted half of a field report, and it is
  the reason this pipeline reads field reports at all. Capture it whenever the
  text gives it, as its own claim when it stands alone.

A claim is one reusable, testable statement of technique or finding, phrased so
it is retrievable and composable later without re-reading the source. Good:
"Capping per-agent sandbox lifetime at 10 minutes removed the idle-container
cost that dominated their bill." Bad: "The team shares lessons from running
agents in production" (a topic, not a claim), or a summary of the post.

## What not to extract

A field report is written partly to be read by customers, and that half is not
knowledge. Extract nothing from:

- Product announcements, pricing, availability, and the general availability
  of a feature.
- Benchmark numbers the author did not produce themselves, quoted from a
  vendor or a leaderboard.
- Claims about a competitor.
- Anything whose only support is that the author recommends it.

If the source is entirely that kind of writing, return zero claims and say so
in `skipped`. Zero claims from a launch post is the correct answer, not a
failure, and it is the signal triage needs to stop routing that feed.

## Fields

For each claim provide:

- `claim` — one sentence, present tense, no hedging beyond what the source forces.
- `evidence` — the source's support in two to four sentences, carrying every
  concrete number it ties to this claim: the scale it ran at, the before and
  after, the latency, the error rate, the cost, the size of the fleet. Name the
  system and version when the source does. Write "authors' assertion" only when
  the source truly gives no measurement, which is common here and must not be
  disguised.
- `measured` — `true` only when the `evidence` you just wrote carries a number
  the authors measured in their own system: a latency, a throughput, a cost, an
  error rate, a fleet or dataset size, a before-and-after delta. `false` when
  they only assert it, and `false` when the only numbers present were quoted
  from somebody else. This is not a judgement of how good the work is, only of
  whether their own number is there, and it decides whether the claim reaches
  the reader as a field-measured result or as an anecdote.
- `procedure` — the operational steps, numbered, 2-6 steps, each one short
  sentence, written so an engineer could act on them without the post ("1)
  Route each request through X. 2) Cap the queue at Y. 3) ..."). Include the
  load-bearing thresholds, timeouts and limits when the source states them. For
  a field report this is usually the most valuable field, because the post
  exists to describe a mechanism. Null only when there is genuinely no
  mechanism, which for a field report means you are probably reading an
  announcement.
- `broke` — what failed, regressed, or had to be abandoned, in one or two
  sentences, with the number if the source gives one. Null when the source
  reports no failure at all. A post that reports no failure anywhere is worth
  trusting less, not more, and this field being null is how the pipeline can
  see that.
- `topics` — tags from this closed list, and nothing else: skills,
  context-engineering, harness-engineering, loop-engineering, memory,
  retrieval, multi-agent, evals, post-training, reasoning, serving, systems,
  tooling, protocols, containment, security, self-improvement, other. A tag
  off this list is dropped on insert and counted, so it is coverage that looks
  real and is not.

  `systems` and `serving` carry most field reports: this is where production
  infrastructure, deployment, capacity and inference cost belong.

  `containment` and `security` are where a field report most often lands in
  the four tags added on 2026-10-05, because a practitioner writing about
  agents in production is usually writing about the boundary they ran inside
  or the attack that crossed it. The boundary itself is `containment` and the
  adversary is `security`; a report that measures both takes both. Keep
  `systems` for what the agent cost to run inside the boundary. The full
  definitions are in prompts/distill.md and the two files share one list.
  `harness-engineering` and `loop-engineering` are for reports about running
  agents themselves. `reasoning` covers how a model's reasoning is TRAINED or
  SPENT, never the bare fact that a model reasoned, and a field report rarely
  earns it.

Extract 1-5 claims per source. Prefer three good claims to five padded ones.

Also extract `institutions`: the company, lab, or team that published this, up
to 3. For a field report this is the byline or the site itself, which is
normally a single company, and it is a fact you can nearly always fill in.

Respond with JSON only:

```json
{"institutions": ["..."], "skipped": null, "claims": [{"claim": "...", "evidence": "...", "measured": true, "procedure": "1) ... 2) ...", "broke": "...", "topics": ["systems"]}]}
```
