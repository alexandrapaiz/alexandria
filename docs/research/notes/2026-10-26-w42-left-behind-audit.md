# Evidence note -- 2026-W42's "Left behind" section, audited against primary sources

Research seat, 2026-10-26. This is the working file behind
`docs/research/briefs/2026-10-26.md` sections 1 and 5. Every command is here
with its output so a reviewer can re-run the audit in under five minutes.

## 0. Why this note exists rather than a `sql_query` transcript

The Modal workspace is disabled, so the MCP server is unreachable and this
seat had no `get_digest`, `semantic_search`, `sql_query`, `propose_skill` or
`propose_change` this run. Checked, not assumed:

```
$ curl -s -i --max-time 20 https://ap4509--alexandria-mcp-serve.modal.run/mcp | head -1
HTTP/2 404
modal-http: workspace ac-5DsaR3hWSUxqyNoGYiowja is disabled
```

Registered by the engineer on 2026-10-23 as `urgent` (#406); not re-filed
here. What follows is therefore built from the two surfaces that need no
credential -- the public archive, which reads `digests` through
`site/lib/issues-live.js`, and `/api/delivery` -- plus the repository at HEAD.

```
$ curl -s https://libraryofalexandria.dev/api/delivery | python3 -m json.tool
  "press":    { "newest_week": "2026-W42", "created_at": "2026-10-19T09:02:52Z",
                "model": "kimi-k2.6" }
  "pipeline": { "papers_newest": "2026-10-23T11:02Z",
                "claims_newest": "2026-10-22T15:15Z" }
  "queues":   { "triage_pending": 119, "distill_pending": 3680,
                "interpret_pending": 0 }
```

So the digest under review is **2026-W42**, written 2026-10-19. 2026-W43 was
never written, and 2026-W41 is still missing, which the 2026-10-12 brief
already reported. The latest issue a reader can open is a week old.

## 1. The three overturn statements in 2026-W42, each against the paper's own abstract

Source text: `https://libraryofalexandria.dev/library/2026-W42`, section
*"Hidden reasoning can be encrypted, not merely hidden."* The section cites
exactly two papers, `arxiv:2609.37312` and `arxiv:2609.38981`, and makes three
overturn statements. All three fail.

### 1.1 The paper is cited as refuting the result it proves

The issue says:

> This directly contradicts the earlier claim that task complexity above a
> model-size threshold forces near-linear information leakage.

`arxiv:2609.37312`, *Hidden Reasoning Must Leak, but Need Not Be Readable*,
abstract, fetched this run:

> beyond a threshold depending on model size, successfully solving the task
> necessarily leaks a near-linear amount of information about the covert task
> input into the CoT. Therefore, sufficiently complex hidden computation
> always leaves an information-theoretic footprint. However, concerningly,
> this leakage need not be readable.

The near-linear-leakage-above-a-model-size-threshold result **is this paper's
own theorem**. The paper's contribution is the second half, on readability.
The relation is `refines` and the issue printed `contradicts`. The issue's own
prose carries the refutation three sentences earlier -- *"The leakage need not
be readable"* -- and still calls it a direct contradiction.

### 1.2 Another paper's finding, attributed to this one, with the stance inverted

> The same paper also overturns a companion claim that simple covert
> computation leaves no trace: omitting tenant-salt provenance enables 93%
> prompt identification from timing side-channels, so covertness fails in
> practice even when encryption succeeds in theory.

Two defects in one sentence.

1. `2609.37312` **asserts** that simple covert computation leaves no trace --
   "Simple computations can be performed covertly" is the abstract's third
   clause. It is named as overturning its own premise.
2. Tenant-salt provenance and timing side-channels in multi-tenant serving
   appear nowhere in this paper, which is a theory paper on CoT encryption
   under cryptographic assumptions. The 93% figure belongs to some other
   paper the issue never cites, and "the same paper" is false.

A mislabelled edge misleads a reader. A number attached to the wrong paper
cannot be checked by a reader at all, which is worse.

### 1.3 Vosti is reported as contradicted by Vosti

> Vosti had claimed bitwise-identical logits across all tested execution
> variations. New work shows that production deterministic modes, vLLM
> batch-invariant and SGLang deterministic, do not achieve full bitwise
> determinism across all variations.

`arxiv:2609.38981`, *Vosti: Specifying, Implementing, and Verifying
Deterministic LLM Inference*, abstract, fetched this run:

> Production systems, including vLLM's batch-invariant mode and SGLang's
> deterministic mode, target this goal but lack a formal system-level
> specification. [...] **Our tests find that these production modes produce
> different logits under some execution variations.** [...] **Vosti produces
> bitwise-identical logits across every tested execution variation** and
> achieves performance comparable to vLLM's batch-invariant mode.

Both halves of the "contradiction" are findings of Vosti, and they are not
even about the same system: the bitwise-identity claim is about **Vosti**, the
shortfall is about **vLLM and SGLang**. The "new work" that overturns Vosti is
Vosti, and the section lists no third paper it could be. This is the
same-paper `contradicts` signature, in print.

### 1.4 One more, smaller

The issue attributes `2609.37312` to "a team at an unnamed institution." The
arXiv abstract page carries authors. Whatever the press had in hand, it did
not have them, and it published the absence as a fact about the paper.

## 2. Score

| Overturn statement | Verdict against the primary source |
|---|---|
| near-linear leakage overturned | wrong -- it is the citing paper's own theorem (`refines`) |
| "simple covert computation leaves no trace" overturned | wrong -- the paper asserts it; the 93% number is another paper's |
| Vosti overturned on bitwise determinism | wrong -- same paper, and two different systems |

**Three of three.** The section is the product's stated differentiator --
the issue's own subtitle is *"what newer evidence has overturned"* -- and none
of it holds.

## 3. This is the third issue of a known class, and the first measured at 3/3

- **2026-W37** built four of its five "Left behind" bullets on mis-typed
  edges, including one that welded two systems on two benchmarks together.
- **2026-W39** published the same claim-12 cluster again.
- **2026-W42** is this note.

Both earlier instances are in `docs/agents/incidents.md` under the
`interpret.md`-merged-never-deployed entries, and the graph-level measurement
is the 2026-10-12 run's: `contradicts` precision **0.172**, 24 of 33 edges
wrong, and **19 of the 22 claims in `deprecated_claims` rest on no edge that
holds** (`docs/research/notes/2026-10-12-contradicts-labels.json`,
`docs/research/notes/2026-10-12-graph-precision-evidence.md`).

## 4. What the repository has already done about it, and the one gap left

This is the part worth a reviewer's minute, because three fixes landed and the
damage is still unrepairable by any of them.

**Fix 1 -- the prompt. Merged 2026-10-12, and it did deploy.** The
2026-10-12 meta-review proposal (`6fb5d904`, *"a limitation is not refuted by
a success near it, and size classes do not refute each other"*) is an ancestor
of the base the interpret image was built from:

```
$ git merge-base --is-ancestor 6fb5d904 f16e2775 && echo in
in
$ git log -1 --format='%h %ad' --date=short f16e2775
f16e2775 2026-10-15
```

`/api/delivery` records the interpret image first seen 2026-10-17 and last
recorded 2026-10-22, so the sharpened prompt ran from 2026-10-17. **This
closes out `INC-2026-10-12-meta-review-proposal-merged-never-deployed`: the
proposal reached production five days after the brief registered it as
frozen.** 2026-W42 was written 2026-10-19, after that, and printed three bad
overturns anyway -- because a prompt governs new edges only.

**Fix 2 -- the schema. Merged 2026-10-24.** `latest_links` now takes the most
recent opinion per `(from_claim, to_claim)` and `deprecated_claims` reads it
rather than `claim_links`, so a contradiction a later prompt withdraws stops
deprecating (`db/schema.sql:417-452`). The primary key was replaced so a
second opinion can land at all. The repair route exists.

**Fix 3 -- the shortlist. Merged 2026-10-25, undeployed.** `5af27966` added
the same-paper exclusion, `and paper_id <> %s`
(`pipeline/interpret.py:303`). It is not in the deployed base:

```
$ git log -S "paper_id <> %s" --format='%h %ad' --date=short -- pipeline/interpret.py
5af27966 2026-10-25
$ git show f16e2775:pipeline/interpret.py | grep -c "paper_id <> %s"
0
```

So the engineer fixed the exact defect the 2026-10-12 brief routed to them,
thirteen days later, and the disabled workspace is the only thing between it
and production.

**The gap, and it is new. Fix 3 makes the damage Fix 2 could repair
permanently unrepairable.**

1. A claim becomes due for a second opinion when the current prompt has never
   read it. `REJUDGE_QUEUE_SQL` keys on `prompt_sha` and nothing else
   (`pipeline/interpret.py:333-349`).
2. The same-paper exclusion is **shortlist SQL**, not prompt text. It does not
   move `prompt_sha`. So no existing judgment becomes due because of it.
3. Both the fresh path and the rejudge path run the same shortlist and pass
   the judged claim's own `paper_id` (`pipeline/interpret.py:543, 558`). So
   when a rejudge *does* run, the judge is **never shown** the same-paper
   candidate.
4. `latest_links` repairs an edge only by a later row for the same
   `(from_claim, to_claim)` pair carrying a different relation. A candidate
   the judge never sees produces no row.

Therefore every same-paper `contradicts` edge written before 2026-10-25 --
the five the 2026-10-12 run found live and wrong, and whatever stands behind
2026-W42 section 1.3 -- is now **outside the reach of the only repair
mechanism the pipeline has**, and will keep feeding `deprecated_claims` and
the digest's third section indefinitely. The fix for the backlog has to be a
one-off withdrawal pass that writes the corrected relation directly, or a
`retracted_at` column. It cannot be a rejudge, and it cannot be a prompt.

## 5. What could not be checked this run

- Claim ids behind any 2026-W42 statement. `sql_query` is down, and the
  public archive renders prose and paper links only.
- Citation velocity from `citation_log`, and the `discovery_report` novelty
  queries. Both are MCP-only, so the brief's rising section is built from
  external traction evidence and the market seat's steer instead, and says so.
- Whether the five same-paper edges from 2026-10-12 are the ones behind 1.3.
  The shape matches; the ids need one query once the workspace is back.
