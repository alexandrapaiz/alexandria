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

Launch plan (final, 2026-09-11): **self-built**, in phases. The subscriber
list is a Neon table (email, tier, comp, status) and the Monday cron emails
each issue itself after publishing. No newsletter platform.

- Phase 1 (now, under ~20 subscribers): friends and family, all comped. The
  cron sends through the owner's own Gmail via authenticated SMTP, because at
  this scale Gmail's sender reputation IS the deliverability strategy. No
  domain, no services, $0.
- Phase 2 (past ~20): buy a domain (~$12/yr), send via Amazon SES with
  SPF/DKIM, add a real unsubscribe endpoint, and turn on payments: a Stripe
  Payment Link for $10/month plus a Modal webhook that activates and
  deactivates subscriber rows. Friends stay comped.
- Growth graduation, if wanted later: beehiiv (built by Morning Brew's product
  lead; Morning Brew itself runs on enterprise Sailthru) buys the referral
  and recommendation machinery. Migration is a CSV.

Rejected: Mailchimp (no native paid subs), Substack (no publishing API breaks
automation, and it takes 10%), managed platforms generally (the point is $0
and ownership). The only rented piece is the raw email pipe, since sender
reputation cannot be self-made at any price. That is the inverse of the
embedding-model decision, and the same right-size-ownership rule.

Paywall mechanics (her call): digests are email-only. The digests/ folder is
gitignored and never published to the repo. The public repo carries the code,
prompts, and ADRs as the credibility engine, and the newsletter is the
product. Sequencing: quality first. The digest must be worth $10 to a
stranger before the paywall goes up, and friends are comped from day one for
feedback.

## Sprint 2 — the member site (agreed 2026-09-11, not yet built)

A website hosting the digest archive and the library, with the paywall as a
real server-side gate. Architecture agreed in advance:

- Next.js on Vercel (ALEX team, free tier). Server-rendered, so locked
  content never reaches the browser: each article shows its first paragraph
  publicly and the rest only to entitled users.
- Clerk for auth (free to 10k users), chosen for its prebuilt profile
  management UI. Sign in with Google or email code.
- Entitlement stays in the Neon `subscribers` table: logged-in email checked
  server-side against status = active. Comped friends unlock like paying
  subscribers; the future Stripe webhook flips the same rows, so the site
  never changes when payments arrive.
- Pages: home (pitch + latest teaser), digest archive, issue pages with the
  teaser gate, library (skills / routines / automations from the gold
  layer), account (Clerk profile).
