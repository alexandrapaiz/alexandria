# Roadmap by sprint

## Sprint 1 — the machine (2026-09-07 → 09-11, shipped)

Full autonomous pipeline (ingest, triage, full-text distill, interpret,
weekly digest + slow loop), claim graph, MCP server with OAuth 2.1, weekly
Claude agent + meta-review proposal channel, digest voice finalized,
newsletter phase 1 (subscribers table + Gmail SMTP send, friends comped).

## Sprint 2 — the member site (agreed 2026-09-11, not started)

A site hosting the articles with a real paywall and the member library.
Architecture agreed:

- **Next.js on Vercel** (ALEX team, free tier). Server-rendered: the locked
  portion of an article never reaches the browser — the teaser gate is
  enforced server-side, not hidden with CSS.
- **Clerk auth** (free to 10k users): sign-in plus its prebuilt profile
  component covers "user can manage profile" with zero custom build.
- **Entitlement from our own data**: logged-in email checked server-side
  against the `subscribers` table (status = active; comp friends unlock the
  same way). Stripe's phase-2 webhook flips the same rows — no site changes.
- **Pages**: landing with pitch + latest teaser; digest archive; issue pages
  (first paragraph public, rest locked); library of skills / routines /
  automations reading the gold layer (promotions + skills/); account page.
- Content source: the site reads the same Neon database the pipeline writes.
  Articles = digests table. No CMS.

Prerequisites when the sprint starts: her Clerk account (free) and the Neon
connection string + Clerk keys pasted into Vercel env vars by her.

## Later

Phase-2 newsletter (domain + SES + unsubscribe endpoint + Stripe at >20
subscribers), $30 skills tier gating, beehiiv growth graduation if wanted,
model upgrade measured against the golden set.
