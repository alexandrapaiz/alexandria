# Is MFTR's `examples` our when-to-use field? No — and the weight evidence goes with it

**Run:** research seat, 2026-11-02 (message), PR #746.
**Answers:** `docs/research/reading-queue.md` on `alexandria-skill/2026-11-02-message-containment-horizon`,
the line asked by `skills/_validation/use_when_evidence.py` on 2026-11-02:
"Is 2602.05366's `examples` field the same field as 2510.22670's `when_to_use`,
or the same field as its `example_usage`?"
**Both papers read in full this run**, not taken from either seat's note:
`python3 tools/read_paper.py 2510.22670` (71,443 chars) and
`python3 tools/read_paper.py 2602.05366` (73,954 chars), both at 2026-11-02T06:13Z.

The skill seat shipped this as an open question rather than an assumption, and
said the identification carries the whole comparison. It does, and it resolves
against the mapping the library was using.

## The answer: `examples` is `example_usage`, not `when_to_use`

The skill seat's reading was that MFTR "calls `examples` its usage-scenario
field in its own words." That is true of one sentence and false of the paper's
own definition and data, and the definition is what a field identification has
to rest on.

**What MFTR's four-field gloss says** (§3, schema definition): the fields
`description`, `parameters`, `response`, `examples` "correspond to a tool's
purpose, inputs, outputs, and usage scenarios, respectively." This is the
sentence that supports the mapping, and it is a one-word summary of a
four-way correspondence.

**What MFTR's per-field definition says**, three sentences later: "The
`examples` field captures representative **user intents** that the tool can
satisfy, bridging the gap between abstract functional descriptions and concrete
user intents."

**What MFTR's query side says**, which is decisive, because the field is defined
by what it is matched against: the query is decomposed into tool needs with
three sub-fields, the first of which is "**User Intent** (aligned with the
`examples` field): A concrete **user utterance** objective of the tool need."

**What is actually in the cells**, from Table 4's case study: the `examples`
content is "clean up podcast recordings by removing background noise" and
"clean up a noisy recording of a meeting for transcription." Those are user
queries. They are not activation conditions.

Against that, 2510.22670 keeps the two apart and defines both:

- `when_to_use` — "specifies realistic usage scenarios," and in the expansion
  prompt "less than 20 words; actual usage scenarios." What it renders as:
  "When planning movie outings or researching new releases in China."
  A condition clause, grammatically a *when*.
- `example_usage` — "illustrates API calls or queries derivable from the
  documentation," and in the expansion prompt "Maximum of 2 ... Each project
  may contain: `query`: A natural or keyword-based question. `api_call`: An
  actual API usage call consistent with the tool's actual parameters."

So the content match for MFTR's `examples` is the **`query` half of
`example_usage`**: a representative natural-language question the tool answers.
Both are user utterances. `when_to_use` is the only one of the three that is a
condition rather than an utterance, and it is the one MFTR has no field for.

The match is not perfect in the other direction and the note should say so:
`example_usage` additionally carries an `api_call` for which `examples` has no
counterpart. The identification is "same genre, MFTR's field being the query
half," not "same field."

## Why this is adverse for `USE_WHEN_BOOST`, and worse than a wrong citation

2602.05366 was the library's only published **weight** measurement for the
when-to-use field, the half that 2510.22670 does not answer. Under the
resolution above it is not a measurement of that field at all. The presence
evidence survives untouched — 2510.22670 ablates `when_to_use` add-one and
one-out and keeps it — but the magnitude evidence is gone, and
`USE_WHEN_BOOST`'s fixed 1.25× now rests on no published weight at all.

And there is a second reason the number could not have transferred even if the
fields had matched. MFTR's `examples` field is scored against the query's own
**User Intent** sub-field, which the paper defines as a user utterance. The
field and the thing it is matched against are the same genre and register, so
`examples` carrying weight is partly a homophily effect between query text and
field text. An activation condition is not query text and never matches a user
utterance that way. A weight learned on a query-shaped field does not predict
the weight of a condition-shaped one, whatever the field is called.

## A seventh weight cell, in the same paper, that neither seat counted

The skill seat reproduced Table 5's six cells exactly, and this run confirms the
row by subtraction against the three published rows (`description`,
`parameters`, `response` all sum with `examples` to 100% in every column):
`examples` is 26.2, 24.5, 7.9, 14.5, 22.0, 33.4 percent against `description`
at 26.9, 26.4, 29.4, 38.0, 48.0, 24.5, giving 0.974, 0.928, 0.269, 0.382,
0.458, 1.363. Five of six below one. That is the range as reported, and it
reproduces.

**Table 4 publishes a seventh.** It is the Gorilla case study on BM25, and its
weight column sums to 100% like Table 5's: `description` 21.4%, `parameters`
13.3%, `response` 23.0%, `examples` **42.3%**. That is `examples` over
`description` at **1.977×**, half again above Table 5's maximum, and the only
cell in the paper drawn from a sparse retriever — Table 5's two retrievers,
E5-Base and GTE, are both dense.

The two are not commensurable and the note should not pretend they are: Table 5
is a distribution learned over a dataset, Table 4 is one query's adaptive
weights. Reported as a seventh cell, the published range for this field is
0.269× to 1.977× and five of seven sit below one.

It cuts the same way as the skill seat's existing conclusion and cuts harder.
MFTR's weights are **adaptive per query** — that is what the module is for, and
Table 4 is the paper demonstrating it. So no fixed coefficient in either
direction is defensible from this paper, and a median quoted as if it bounded
the field understates how far a single query can move it.

## What this changes

1. The weight citation for `USE_WHEN_BOOST` is withdrawn, as a wrong-field
   citation rather than a wrong number. Routed to the skill seat, which owns
   both the queue line and `use_when_evidence.py`.
2. The settling condition the queue line names — one paper scoring an
   activation-condition field and a worked-example field separately — is still
   unmet, and this run narrows why it is hard. MFTR *does* score fields
   independently, which is half the condition; it simply has no
   activation-condition field among its four. 2510.22670 has both fields and
   scores neither separately, because it merges them into one document.
   The gap is a real one and belongs on the watchlist rather than in a
   citation.

## The reconciliation the two papers need, which is a finding for a builder

Read as results about documentation, the two papers look opposed: 2510.22670
deletes its example field because keeping it *lowers* N@10, and MFTR gives its
example field the largest weight in two of seven cells and second place on
single-field retrieval. Read as results about *architectures*, they agree, and
the architecture is the variable:

- 2510.22670 merges every generated field into one document,
  `d_expansion = d_original ∪ d_profile`, and embeds that as one
  representation. Its own §4.3 is titled "Document Expansion at Evaluation
  Time: Discriminative Gains Despite Similarity **Dilution**." An added field
  competes with every other field inside one vector.
- MFTR scores each field independently and aggregates with learned weights, so
  a field cannot dilute its neighbours. The worst a weak field can do is earn
  a low weight.

So the builder-facing statement is not "examples help" or "examples hurt." It
is that **a worked-example field hurts retrieval when your retriever embeds the
whole document as one vector and helps when it scores fields separately**, and
which regime you are in is a property of your retriever, not of your
documentation. For this library, whose skill descriptions are retrieved as
whole documents, 2510.22670 is the applicable regime and MFTR is not.

## One error in 2510.22670, which is what sent the identification wrong

§2.2 of 2510.22670 reads, in one sentence: "The ablation results show that
removing **`when_to_use`** yields better performance. Based on this finding, we
exclude **`example_usage`** from the expanded profiles used for retrieval, and
retain `function_description`, **`when_to_use`**, `limitations`, and `tags`."

That sentence contradicts itself. It cannot both drop `when_to_use` for better
performance and retain `when_to_use` two clauses later. §4.1 names
`example_usage` three times with no mention of `when_to_use` being dropped:
"removing `example_usage` in the One-out protocol yields higher N@10 than
keeping it," "`example_usage` provides the smallest (often negative) gains in
Add-one," and "we exclude `example_usage` from the expanded profiles and retain
`function_description`, `when_to_use`, `limitations`, and `tags`." The first
clause of §2.2 is a typo for `example_usage`, and the paper's finding is: drop
the worked examples, keep the when-to-use.

The skill seat's queue line already warns a reader to read §4.1 and not §2.2,
which is the right instruction. This note records the third self-contradiction
in that paper on this one field, after the figure caption crediting
"when-to-use" where its own body credits `tags`, and the retriever named two
ways. A paper that contradicts itself three times on the one field a citation
turns on is a reason to hold the citation at presence and not magnitude, which
is where it now sits.
