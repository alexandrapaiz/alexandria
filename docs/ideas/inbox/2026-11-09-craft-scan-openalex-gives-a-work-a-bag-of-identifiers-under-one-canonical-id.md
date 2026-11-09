### 2026-11-09 - Craft scan: OpenAlex, and the one thing worth stealing is the bag of identifiers (engineer seat)

- Trigger: the charter's one-product-a-day craft scan. Today's product is
  OpenAlex, picked because this run's whole subject was the opposite choice:
  `papers.id` is one string, that string is also the arXiv identifier, and the
  two routes that look a paper up in it had each picked a different spelling of
  it. OpenAlex is the same category as Semantic Scholar on
  `docs/market/landscape.md` and is not on that page yet.
- What is worth stealing: OpenAlex separates the key from the identifiers. A
  Work has one canonical `id` of its own minting, and an `ids` object carrying
  every external identifier it knows for the same work, documented as "all known
  external identifiers for this work, as URIs where possible", with keys
  `openalex`, `doi`, `mag`, `pmid` and `pmcid`. Read live at
  help.openalex.org/api-entities/works/work-object this run rather than from
  memory. The consequence is the part to steal: no caller ever has to guess
  which spelling of a paper the store used, because the store does not have a
  favourite. alexandria made the other choice and has now paid for it three
  times, counting today, and the cost is measured: 322 arXiv papers held twice,
  656 rows, 73 pairs triaged twice and given different decisions. A key that is
  also an identifier makes every lookup a normalisation problem, and the failure
  mode is the quiet one, because the wrong answer is an empty result and an
  empty result reads as "we do not have this paper".
  **What I did not verify and so do not claim:** whether OpenAlex redirects a
  request for a merged id to the surviving record. It is not on the work-object
  page and not on the merged-entities help page I checked.
- What alexandria does better: OpenAlex tells you that a work exists. It has no
  analogue for why this corpus holds it. Every `papers` row carries a `source`
  naming the route that fetched it, and every triage decision carries its
  `reasoning`, its `model` and the `prompt_sha` of the prompt that judged it, so
  a paper's presence is an auditable decision rather than a fact of the world.
  That is what let the question this run was asked be a real question at all:
  "absent or discarded" is only answerable in a store that records the
  discarding. OpenAlex could not be asked it.
- First step: not a migration. One column, `papers.canonical_id`, written by
  `pipeline/ingest.py` as the version-stripped id and backfilled by one update,
  with the primary key left exactly as it is. Every lookup then joins on it and
  the `shapes()` helper this run added becomes the thing it replaces rather than
  a permanent fixture. That is a day of work and it is the second card below,
  because the 656 rows already written make the ordering matter: the column has
  to exist before the duplicates can be collapsed, and collapsing them is the
  owner's.
- Cost: $0
- Status: proposed
