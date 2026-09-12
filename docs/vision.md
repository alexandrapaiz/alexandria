# Vision — the declared end state

Recorded 2026-09-08. This is what the pipeline is being built *toward*; the
status checklist in the README tracks distance from it.

## 1. The weekly digest

The end product of the reading loops is a well-drafted weekly digest with three
kinds of findings:

- **Trailblazing** — new papers that could change how agents are built, caught
  the week they appear.
- **Matured** — papers and claims that have aged well and been accepted by the
  community (the slow loop's citation checks + accumulating `supports` edges in
  the claim graph are the evidence).
- **Left behind** — approaches abandoned, superseded, or deprecated
  (accumulating `contradicts` edges, the `deprecated_claims` view, and citation
  flatlines are the evidence).

The digest is a *judgment document*, not a feed: every item appears because the
claim graph and the retrospective evidence say it belongs, with the evidence
cited.

## 2. Claude skills as the terminal asset

What the system learns becomes **Claude skills** — procedure + judgment in
loadable files. The gold layer is a growing library of skills distilled from
the research: context-engineering patterns, harness patterns, loop designs,
serving and post-training know-how. A paper's highest terminal state is a
skill in use.

## 3. Full autonomy — human optional

The end state is a system that runs, improves itself, and publishes its digest
**without a human in the loop at all**; human review becomes optional, not
required.

This is a *graduation path*, not a day-one property. ADR-7 (the human merge as
the gate on self-modification) stays in force while the system earns trust:
the triage log, human verdicts, and golden sets are precisely the evidence that
will eventually justify removing the gate. The gate comes off when the
measured record says the system's judgment matches the human's — the same rule
as every other swap in this architecture: **change under evidence, not under
optimism.** Until then, autonomy below the gate, proposals above it.

## 4. The business — a subscription newsletter

Once the digest is consistently excellent, alexandria becomes a **paid
newsletter**:

- **$10/month — Digest tier.** The weekly digest: trailblazing, matured, and
  left-behind, with evidence.
- **$30/month — Digest + Skills tier.** The digest plus the skill library —
  subscribers get the operational assets, not just the reading.

The architecture was built for this from the start: the pipeline's marginal
cost is ~$0, so subscription revenue is nearly pure margin, and the
gold layer is the paywalled product.

Launch plan (decided 2026-09-11): **Buttondown** as the newsletter platform —
markdown-native with a REST API, so the Monday cron sends each issue
automatically (one HTTP call at the end of weekly.py); paid subscriptions via
Stripe with no platform revenue cut; friends get comped subscriptions in the
Buttondown UI. Mailchimp was rejected (no native paid subs). Substack was
rejected because it has no publishing API, which breaks full automation, and
it takes 10%. Ghost is the graduation platform when the $30 two-tier package
(digest + skills) needs native tier gating. Paywall mechanics: subscribers
get issues by email on publication, and the public repo's digests/ folder
becomes a ~4-week delayed archive, so the credibility engine keeps running
without giving the product away. Sequencing: quality first — the digest must
be worth $10 to a stranger before the paywall goes up; comp friends from day
one for feedback.
