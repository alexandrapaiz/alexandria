// The delivery receipt: the few facts a seat needs to answer "did the product
// reach a reader", shaped for publication. Pure, and import-free so that
// tests/delivery.test.mjs can evaluate this source with no build step, the
// same way lib/account-core.js is tested.
//
// Why this file exists. `tools/delivery_health.py` answers five surfaces and
// three of them need `DATABASE_URL`: the press (the newest row in `digests`),
// the pipeline (the newest rows in `papers` and `claims`), and the deploy
// (the shas in `deploy_runtime`). No agent seat holds that credential, so
// three of five surfaces have read `unknown` in every sandbox since the
// command shipped, and the ledger has carried that as urgent since
// 2026-09-28. The site is the one place in this company where the database
// and a credential-free HTTP surface already meet: lib/graph-live.js,
// lib/entitlement.js and lib/account.js all read Neon from this app's
// environment. So the site publishes the facts and every seat can read them.
//
// Two rules decide what goes in, and both are about what must stay out.
//
// 1. **Facts, never verdicts.** This endpoint says the newest week is
//    2026-W39. It never says the press is broken. The judgement lives in
//    tools/delivery_health.py and stays there in one copy, so the
//    credential-free reader and the credentialled one cannot reach different
//    conclusions from the same rows. It also means a bad week reads as a date
//    to a passer-by rather than as an alarm.
// 2. **Metadata, never product.** Every field below is built by name into a
//    fresh object. Nothing is spread in from a row, so a column added to any
//    of these tables cannot appear here by accident. `digests.body` is the
//    issue itself and claim text is the paid product (lib/graph-live.js says
//    so in its own words); neither has a field here and neither is queried.

export const RECEIPT_VERSION = 1;

// A timestamp from Neon arrives as a Date, from a JSON round trip as a
// string, and from an empty table as null. One shape leaves here.
export function iso(value) {
  if (value === null || value === undefined) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function text(value, limit) {
  if (value === null || value === undefined) return null;
  return String(value).slice(0, limit);
}

function count(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

export function buildReceipt({ digest, papers, claims, deploy, observedAt }) {
  return {
    receipt: "alexandria-delivery",
    version: RECEIPT_VERSION,
    observed_at: iso(observedAt) ?? new Date().toISOString(),
    // `null` means the table is empty, which is a fact worth publishing and
    // is not the same as this endpoint being unable to read it. An endpoint
    // that cannot read answers 503 and never answers with nulls.
    press: digest
      ? {
          newest_week: text(digest.week, 16),
          created_at: iso(digest.created_at),
          model: text(digest.model, 120),
        }
      : null,
    pipeline: {
      papers_newest: iso(papers),
      claims_newest: iso(claims),
    },
    // One row per scheduled job, written by the job itself (pipeline/runtime_sha.py).
    // The sha is a digest of repository file contents, so it discloses no file
    // and is only comparable by someone who already holds the same checkout.
    // `null` here means the query could not be run at all, which the drift
    // guard must not read as "no job has reported". An empty array means the
    // table was read and is empty, which is a different and reportable fact.
    deploy: deploy == null ? null : deploy.map((row) => ({
      app: text(row.app, 32),
      runtime_sha: text(row.runtime_sha, 64),
      entrypoint: text(row.entrypoint, 120),
      file_count: count(row.file_count),
      recorded_at: iso(row.recorded_at),
      first_seen_at: iso(row.first_seen_at),
      notified_at: iso(row.notified_at),
    })),
  };
}
