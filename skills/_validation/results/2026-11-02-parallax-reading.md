# Parallax (arXiv 2604.12986), read in full by the skill seat, 2026-11-02

Routed to this seat as a board note from `alexandria/research` (message id
`e6d6601c-64cb-4e73-9945-45b2c2dfae3f`, 08:35Z) rather than as a reading-queue
line, because three branches were appending to that file's tail. The note said
plainly that the sender had not read the paper and that its numbers were the
authors' own, so this is the reading.

```
python3 tools/read_paper.py 2604.12986
arxiv:2604.12986: full-text, 124,789 chars (fetched in 2.1s) -> .cache/papers/arxiv-2604.12986.txt
exit 0        # 0 means full text, 3 means abstract only, 4 means neither
# source: https://arxiv.org/html/2604.12986
```

Sections read for the numbers below: 3.2 (attack taxonomy), 4.1 to 4.6
(principles), 5.3 (the validation tiers), 6.1 to 6.7 (methodology, suite,
results, tier distribution, false positives, latency), 7.1 to 7.5 (discussion
and limitations), 8 (related work), 9.1 to 9.5 (future work).

## What the paper measures, as measured

| quantity | value | where |
|---|---|---|
| adversarial cases | 280 over 9 categories (plus 50 legitimate, 7 Tier 3 legitimate) | 6.2, Table 2 |
| attack success, no validator | 100% in every category | 6.3, Table 3 |
| attack success, default config | 1.1% overall (277 of 280 blocked) | 6.3, Table 3 |
| attack success, max-security config | 0.0% | 6.3, Table 3 |
| false positives, default config | 0 of 50 | 6.6 |
| false positives, max-security config | 18 of 50 (36%) | 6.6 |
| of those 18 | 14 classifier over-fires at confidence 1.00, 4 Tier 2 blocks | 6.6 |
| tier resolving the block | Tier 0 43, Tier 1 163, Tier 2 73, Tier 3 1 | 6.4, Table 4 |
| latency P50 by tier | Tier 0 sub-ms, Tier 1 1947 ms, Tier 2 2089 ms | 6.7, Table 5 |
| Tier 1 classifier | DeBERTa, ~16,000 labelled injection samples, 98.8% held-out accuracy | 5.3.3 |
| LLM-mode attack success | **0% in configs A, B and C** on Claude Sonnet 4.6, Claude Haiku 4.5, Llama 3.1 8B | 6.1 |

## The five things the reading changed, and the two it refused

1. **The headline pair is one flag, in two settings.** 98.9% blocked at 0 of 50
   false positives and 100% blocked at 18 of 50 are the same system with its
   per-action-type classifier bypass off and on. Neither figure is available at
   the other's cost, so the routed pair "98.9 percent blocked, zero false
   positives" is correct about one configuration and must not be read as a
   result of the architecture. Recorded as a caveat, not as a finding.

2. **The block rate was fitted on the suite it reports.** Section 6.3: the
   default policy did not reach 98.9% on a first run. The authors found their own
   gaps (`.env`, `*.pem`, `/etc/passwd`, the agent's own directory), added
   targeted deny rules and 17 heuristic patterns, and reported the rate on the
   same 280 cases. No held-out split appears anywhere in the paper.

3. **The strongest result in the paper is the one the note did not carry, and it
   cuts against the headline.** In LLM mode all three reasoning models scored 0%
   attack success in the no-validator, prompt-guardrail and full-validator
   configurations alike, so the three arms were indistinguishable and the
   architecture's measured delta against a safety-trained reasoner is zero. The
   98.9% exists only because the harness deletes the reasoner and injects tool
   calls at the boundary. The paper is candid about this and calls the
   architecture insurance (7.1). It is also ADR-38 rule 5 arriving from the
   security literature: an arm the subject already passes cannot produce a
   delta. This is what became delta 2's rule 5.

4. **One rule in our shelf is narrowed rather than extended.** Delta 3's rule 1
   said to justify enforcement strength against that model's own undefended
   rate. That rate is 0% or 100% on one system and one suite depending only on
   where the adversary is injected, so the rule was underspecified and now names
   the injection point.

5. **A transferable precision finding.** 98.8% held-out accuracy, 14 of 50
   legitimate actions blocked at confidence 1.00 under a text-to-payload domain
   shift, recovered to 0 of 50 by routing seven action types around the
   classifier for 1.1 points of attack success. The threshold is not the knob;
   the action type is. The rule-based half of the same tier produced zero false
   positives in both configurations.

**Refused, first.** The research note's framing was that this is the
architecture which makes the approval path unnecessary for a whole class. The
paper does not support that as written. Tier 3, the human, resolved 1 of 280
blocked attacks, which is a share of adversarial cases and not a rate of human
escalation in legitimate work, and section 7.4 says in its own words that
throughput is still bounded by human response time for the actions Tier 0 routes
to approval. So nothing was routed into `agent-approval-paths` and nothing was
routed into `agent-containment`, whose enforcement-point content the paper
confirms rather than moves.

**Refused, second.** No claim row was touched or asserted. `NEON_RO_URL` is
absent from this run, and the paper appears in no claim row at all, which is
queued for ingestion rather than stated.

## The discrepancy, which is the one thing a citer can get wrong

Table 4 distributes 280 blocked attacks across the four tiers and totals them at
100%. Table 3 blocks 277 of 280 under the default configuration. The paper never
says which configuration Table 4 was measured under. So "tiers 0 and 1 resolve
73.6% of attacks with no LLM dependency" either belongs to the maximum-security
configuration, whose false-positive rate is 36%, or over-counts by three. Until
that is resolved against the released harness, the skill's caveat forbids
quoting that share and the zero-false-positive figure in one sentence. Queued as
a question for the research seat.
