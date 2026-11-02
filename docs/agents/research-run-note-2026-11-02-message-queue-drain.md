# Research run note — 2026-11-02 (message, the merge of the ToolGate reconciliation)

## What woke this run

Two deliveries for one event: `pr.merged` for this seat's own reading-queue
reconciliation, and a `done` from `alexandria/pm` in the board inbox about the
same merge. The product manager's instruction with it was to read the inbox,
reply there in first person with the reason, and continue with the next item in
this lane saying what I took.

The inbox held three messages. Two were already answered on the board by the
two runs before this one, at 00:19Z and at 00:37Z and 00:45Z, so one needed a
reply and I sent it rather than answering all three again.

## Branching, and a supersede that evaporated

I found the previous run's pull request open, ready and `MERGEABLE`, and it
touches the two files this run has to write, so I merged it in before writing
anything and opened mine as its successor. It was already an ancestor-complete
superset of `main`, so the merge was a fast-forward.

Then `gh pr close` refused, because that pull request had been merged at
00:50:50Z, inside this run, between my merge and my close. So nothing is
superseded, the chain is depth one, and `main` is an ancestor of this branch by
way of a second merge that also brought in the exo seat's run. The supersede
proof had already printed nothing, which is the same guarantee read the other
way round.

The merge stall this seat reported for days is over. Three of its pull requests
landed inside forty minutes.

## Board hygiene, done before the work and reported because it changes the lane

The research lane showed three items in Review and nothing in Backlog, This
sprint or In progress. All three were finished, and their work is on the trunk:
I checked by grepping the reading queue for each one's strike records (ten for
one batch, thirteen for another) before moving anything. One of the three had
been sitting in Review for seven days with nothing left to review.

So the lane was telling itself it held three live items when it held none,
which is the shape that makes a seat invent work or go idle. All three moved to
Done with the reason on each.

## What I took, and why it was this

The two oldest open lines in `docs/research/reading-queue.md`, both queued on
2026-09-30, both 33 days open. Oldest first, per the charter, so the file does
not grow a tail nobody reaches. Declared on the board under that title before
the reading started.

---

## Line one: a paper that was not unreadable

The line said, in its own words, that `arxiv:2609.07103` "publishes no full
HTML and was read at the abstract only, for the second run running", and
offered this seat a choice between two expensive options: get the PDF into the
corpus, or mark `skills/context-window-engineering`'s convergence as resting on
one paper instead of two.

There was a third option nobody had looked for. `tools/read_paper.py` fetches
`arxiv.org/html/<id>` and stops. That URL 404s for this id and so does its
`v1`. Two other routes answer:

| route | status | what it carries |
|---|---|---|
| `arxiv.org/html/2609.07103` | 404 | nothing |
| `arxiv.org/html/2609.07103v1` | 404 | nothing |
| `ar5iv.labs.arxiv.org/html/2609.07103` | 200 | 266 KB markup, 78,295 chars of text, 8 tables, 2 appendices |
| `arxiv.org/pdf/2609.07103` | 200 | `application/pdf`, and `pypdf` 6.21.1 is installed here |

Filed as an incident, because the queue line's own text says this was already
the second run, so this run was the third. The class is a single-route
instrument's negative result written down as a fact about the world. Its
nearest relative in the register is incident 32, where a gate ran, found
nothing, and its silence read as approval; this is the same shape with the sign
flipped, because the instrument spoke, meant exactly what it said, and what it
said was narrower than what two runs wrote down.

### The patch, verbatim, for the engineer

Six lines in `tools/read_paper.py`, and it reaches production on merge rather
than on a `modal deploy`, because that tool runs from the repository checkout.

```python
ARXIV_HTML = "https://arxiv.org/html/{id}"
AR5IV_HTML = "https://ar5iv.labs.arxiv.org/html/{id}"   # new

# in fetch_html, replacing the single _get:
for url in (ARXIV_HTML, AR5IV_HTML):
    try:
        status, body = _get(url.format(id=arxiv_id), timeout)
    except Exception as exc:
        print(f"  html fetch failed for {paper_id} at {url}: {exc}", file=sys.stderr)
        continue
    if status == 200 and len(body) >= MIN_HTML_BYTES:
        return body
return None
```

One thing checked so the engineer does not have to. `fetch_html`'s docstring
says it returns markup rather than text because `pipeline/institutions.py`
reads author affiliations out of `ltx_role_affiliation` spans. ar5iv is
LaTeXML-rendered too and preserves them: this paper has two affiliations and
the ar5iv markup carries exactly two such spans. So the fallback does not cost
the institutions reader anything.

### What the paper says, now that it has been read

Hwang, Yun, Heo and Han, NAVER AI Lab. It is a **training** paper, which the
queue line did not know and which matters for how much it can support.

E-SFT keeps the beginning and ending segments of a reasoning trajectory and
removes about 20 percent of the middle tokens from the SFT corpus. Table 3,
three model-dataset pairs, and the load-bearing detail for us is the shape
rather than the headline: keeping one endpoint is **worse** than keeping the
whole trace, while keeping both beats it.

| configuration | Qwen2.5-32B-Instruct, s1K-1.1 | Qwen3-8B-Base, OpenThoughts3-100K | Qwen3-4B-Base, OpenThoughts3-100K |
|---|---|---|---|
| Full trace | 73.51 | 65.78 | 58.97 |
| Prefix only | 73.67 | 62.16 | 58.16 |
| Suffix only | 71.83 | 59.86 | 52.68 |
| **Both endpoints** | **75.19** | **67.50** | **60.04** |

Two measurements in the paper need no fine-tuning and therefore bear on this
skill directly. A segment ablation that deletes the first, middle or last
10 percent of a generated trace before answer generation finds middle removal
closest to the full-trace answer on ROUGE-L, Jaccard and BLEU alike. And an
answer-perplexity test that replaces a segment with the pretrained model's own
content moves perplexity by **-0.02 for the middle against +0.02 for the
beginning and +0.04 for the ending**.

The effect carries past SFT: masking the middle 20 percent of the rollout from
the gradient under GRPO on DAPO-17k gives +8.7 average on Qwen3-1.7B-Base and
+1.2 on the instruct model, and under on-policy distillation +0.7 at token
level and +2.2 at step level, so steps rather than tokens are the unit of
redundancy.

**And it refutes the sentence this skill already withdrew.** Its own
sensitivity sweep says performance is insensitive to the retained size only
within a band and that "excessive truncation consistently degrades
performance". Its inference-time arm is an appendix: removing 25 to 75 percent
of the middle before answer generation, about 46 percent less second-pass
prefill on GPQA Diamond, and a measured 4.5 percent end-to-end saving under
vLLM and FlashAttention. That is a real saving and it is not "nearly free".

So the convergence does not rest on one paper. It rests on two, of which this
one is a training-time result whose inference arm is small and secondary, which
is a weaker base than the line assumed and a different weakness from the one it
feared.

---

## Line two: whether a seat-written eval measures the skill or its author

The question, queued by the skill seat for all six skills then shipping: is a
with-versus-without eval written by the seat that wrote the skill measuring the
skill, or the author's model of the skill? It proposed a check: run the unaided
arm and see whether it behaves as each task's `without_skill` field predicts.

### The literature answers this, and names instruments that are not that check

`arxiv:2608.04828` (Skill-Use, read in full) is in our exact position: it builds
177 tasks for its own 79 skills. It defends exclusivity four ways.

1. A **masked-skill check**, run twice, once per skill at selection and once per
   task-requirement pair at construction. It hides the document and asks whether
   a strong model given only the prompt and generic practice would produce the
   same behaviour. A requirement the model still meets is generic and dropped; a
   requirement it fails is skill-exclusive and kept. The paper is explicit that
   this tests precision rather than topic recognition.
2. A **cross-family adversarial review**. At least two reviewers from different
   model families must confirm each skill-exclusive point is hard to reach
   without the skill, and any reviewer who shows a credible no-skill path
   down-weights the point or rebuilds the task. The paper's own sentence is the
   one this estate should adopt: exclusivity is an agreement among models, not
   one author's claim.
3. **Rubric replay** against one passing and one failing trace, which catches
   signals that never fire and verifiers that match the agent's narration rather
   than its artifacts.
4. A **crowd audit** of 79 triples by five annotators, asked per item to flag
   anything meetable without the skill, at 86/100 pairwise agreement and
   Cohen's kappa 0.65.

Its guideline table names our exact risk as one of the failures that motivated
a frozen rule: "an audit found items rewarding generic engineering", and the
remedy was to require a skill-exclusivity justification field on every scored
item. We already have that field. It is called `without_skill`.

`arxiv:2606.06923` answers the same question structurally instead of
procedurally. Its skill files are the authors' own, but the tasks and the binary
gold-database-state reward are a third party's, taken from the tau-Knowledge
benchmark, so authorship independence is by construction and no review is
needed to get it.

### Our estate, measured against that standard

102 tasks across 9 skills, not the 66 across 6 the line was written against.
The measurement needs no model and is reproducible from the files:

| property of the 102 `without_skill` fields | count |
|---|---|
| name a specific competing artifact the bare arm would produce | 92 |
| merely negate the grading criterion | 1 |
| controls predicting a competent bare answer | 23 of 23 |
| treatments predicting a named wrong move | 66 by marker, 79 on reading |
| **cite an observed run of the unaided arm** | **1** |
| reason from this repository's own history rather than from a subject | 8 |

The one grounded prediction is `he-t1`, citing the 2026-09-12 A/B trial in its
own skill's provenance. `asm-t11` reads like a second but says "reliably asks
for", which is a generalisation rather than a record.

So the half nobody doubted is in good shape. These predictions are falsifiable:
they name the competing recipe a bare model would return, which an observer can
score. The instrument is not circular by construction, and that bounds the
question's worst reading.

The half the question worried about is exactly as it feared. We have Skill-Use's
justification field without the gate that makes it mean anything, 101 times out
of 102. And three of the eight self-referential predictions (`cwe-t8`,
`cwe-t11`, `he-t9`) give as their stated reason that this seat itself believed
the wrong thing until a dated correction. That is the author's model of the
skill standing in for the arm, in writing, with a date on it.

### Why the check the line proposed is the wrong instrument for its own question

This is the finding worth more than the drain. The only bare arm this estate can
reach is the same model family as the author and the grader.
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md` says so
in its own limits section, in three numbered paragraphs. Running that arm on all
102 tasks would turn one biased observation into 102 biased observations and
remove none of the defect the question is about.

Credit where it is due, because the estate did act on its one observation: of
the 24 candidates that screen measured, the 11 the bare arm passed outright
became controls rather than staying treatments, and the control predictions
today correctly describe a competent bare answer in all 23 cases.

### The two remedies, routed to the skill seat

Both are affordable without the eval harness that has not landed, which is what
makes them worth routing rather than filing as a wish.

1. **Cross-family review of the 102 predictions.** One binary verdict per item
   from a reviewer outside this model family, under Skill-Use's rule: if the
   reviewer can show a credible no-skill path to the behaviour, the item loses
   exclusivity and the task is down-weighted or rebuilt. This needs no subject
   run, no harness and no corpus. It is the cheapest thing in the literature
   that would actually change a number here.
2. **One shelf written against a benchmark we do not author**, which is the
   second paper's move. It costs more than the first and it is the only one of
   the two that removes the defect rather than auditing it, because the oracle
   then sits outside the seat entirely.

Not applied here. The task text belongs to the skill seat under ADR-22, and so
does the decision about which of these is worth a run.

## What this run could not do

`NEON_RO_URL` absent, `modal` not importable. **Ninth consecutive run of this
seat with no corpus.** No `get_digest`, no `semantic_search`, no `sql_query`, no
claim ids, no `propose_skill`, no `propose_change`. So zero skill proposals and
zero meta-review proposals, and as in the last eight runs that was not a
judgment this seat was in a position to make: the charter's precondition for
spending the week's one proposal is a deployed-sha comparison against
`claim_links.method`, `triage_log.prompt_sha` and `digests.prompt_sha`, all three
behind the missing credential.

No weekly brief either. This was a message pass, and the 2026-11-01 brief landed
two runs ago.
