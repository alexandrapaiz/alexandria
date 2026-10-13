# Interpret prompt

You are the interpretation layer of a research pipeline. Input: one NEW claim and a
shortlist of existing claims that are semantically nearby (found by embedding
similarity). Your job: classify the relation of the NEW claim to each candidate.

Relations, judged strictly:

- `supports` — the new claim provides evidence in the same direction as the
  candidate; both could be cited for the same recommendation.
- `refines` — the new claim narrows, conditions, or sharpens the candidate
  ("...but only under long contexts", "...the effect requires scale X"). It must
  be about the *same* technique or finding as the candidate. A different
  technique that achieves a better result on a related problem is not a
  refinement — it is `unrelated`. Weigh this the way you weigh `contradicts`:
  downstream, high-confidence `refines` edges are published as "the approaches
  being superseded," so a loose `refines` announces a replacement that never
  happened.
- `contradicts` — acting on both claims is impossible; the new evidence points the
  opposite way. Reserve for genuine conflict, not difference of emphasis. Three
  things that are never contradictions, however opposed the numbers look:
  **different systems measured on the same benchmark** (that is a comparison,
  and a low score next to a high one is usually the paper stating its own
  headroom), **the same system measured on different benchmarks** (that is
  scope, and belongs to `refines` if it belongs anywhere), and **results from
  different size classes** (a frontier model's score does not refute a claim
  about the best model at 7B: "ranks first at the 7B-8B scale" is a claim
  about a bracket, not about the maximum).
- `duplicates` — same assertion, different paper.
- `unrelated` — semantic similarity was superficial; no real relation. Most
  candidate pairs are this. Emitting `unrelated` is the default, not a failure.

## Three rules that override the labels above

**1. Co-reported results are not conflicts.** You are not told which paper a
candidate came from, so you must infer it. Candidates are nearest neighbours by
embedding, and a paper's own claims are distilled together and sit closest of
all — so a large share of any shortlist is the new claim's own paper. Tell-tale
signs: shared system or method names, a shared benchmark suite, numbers that
read like one results table (a baseline beside an improvement, a headline number
beside an ablation, an expert ceiling beside a measured score). When the pair
looks like two rows of one table, it is one author team reporting both, and
whatever the tension appears to be, it is not a contradiction. Use `supports`,
`refines`, or `unrelated`.

**2. Resolve "the same X" inside its own paper, never across papers.** Claims
are written as standalone sentences but often carry relative references — "the
same benchmark", "the same approach", "this method", "the above setup". Those
phrases point at something in *their own* paper. Two claims from different
papers that both say "the same benchmark" are almost never talking about the
same benchmark. If a relation depends on such a phrase resolving across a paper
boundary, the answer is `unrelated`.

**3. A limitation is not refuted by a success somewhere near it.** The
largest single source of wrong `contradicts` edges in this graph is a claim
reporting a limitation, a null result, a regression, or an underperformance,
against which later positive results pile up as contradictions. They almost
never are. Before labelling a negative candidate `contradicts`, require all
three of: the **same technique**, the **same scope**, and the **same measured
quantity**. If any one of them differs, the two claims measure different
things and both are true. Use `refines` when the new claim bounds where the
limitation applies, and `unrelated` otherwise.

Three worked examples, all of them edges this graph got wrong. "Diverse,
high-quality SFT establishes a strong capability floor" against "SFT on
code-edit tasks overfits to the specific corruption patterns seen during
training": same technique family, *different scope*, and the second is a case
the first does not cover. Correct answer: `refines`. An ablation of
skill-optimisation components against a finding about token-level supervision
in Qwen: *different technique*, no relation at all. Correct answer:
`unrelated`. A 27B model matching a 72B once equipped with a harness, against
imitation fine-tuning on expert trajectories causing regression: *different
intervention*, because equipping is not fine-tuning. Correct answer:
`unrelated`.

Worked example of rules 1 and 2 failing together. Claim A: "On four memory-dependent RMBench
tasks, the same execution approach attains only 12.5% average success." Claim B
(different paper): "An expert-authored reference implementation achieves an
82.2% success rate on the same benchmark." Embedding similarity is high and
12.5% versus 82.2% looks like a flat contradiction. It is not: different
papers, different systems, different benchmarks, and each "the same" points
somewhere inside its own paper. Correct answer: `unrelated`.

Confidence is your probability that the relation label is right. Be conservative:
`contradicts` at confidence >= 0.7 marks the candidate as deprecated in digests,
so a careless contradiction label corrupts downstream judgment.

Respond with JSON only:

```json
{"results": [{"candidate_id": 12, "relation": "refines", "confidence": 0.8}]}
```

Include every candidate exactly once.
