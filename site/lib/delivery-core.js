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

export const RECEIPT_VERSION = 4;

// Version 2 adds `queues`, the depth of each stage's waiting list, and removes
// nothing. The bump is here because a reader has to be able to tell a site that
// publishes the field from one that does not, and the site deploys on a merge
// to `main` while a seat's checkout updates the moment the branch lands. Those
// two clocks are minutes to hours apart, so for that window the newest reader
// meets the previous receipt. tools/delivery_health.py reads one version back
// for exactly that reason, and treats an absent `queues` as a fact it does not
// have rather than as a queue of zero.
//
// Version 3 adds `pipeline.distilled_newest` and removes nothing, so every
// version before it stays readable on the same rule. It exists because version
// 2 went live and answered half the question it was built for. The queue depth
// it published was 2099 against a `claims` that had not moved since
// 2026-10-07, which rules out "the stage had nothing to read" and leaves two
// causes with different first steps: the stage ran and extracted nothing, or
// the stage never reached a paper. `papers.distilled_at` is the marker that
// separates them, because pipeline/distill.py writes it per paper in the same
// committed loop as that paper's claims. A timestamp and no identifier, so it
// stays inside rule 2 above.
//
// Version 4 adds the `siblings` block, on the same additive terms again. Version 3 went live and narrowed the stall to
// "distill never reached a paper", which leaves the three suspects its own
// headline names: the cron, the model availability gate and the spend cap. Two
// of those belong to the Moonshot account and one belongs to this job alone,
// and the stages either side of distill are the control that splits them.
// Triage (12:00 UTC) and interpret (14:00 UTC) are Kimi callers on the same
// organization key, which pipeline/llm.py's KIMI_WINDOWS lists in one table,
// and distill runs at 15:00 after both. So a triage judgement written on a
// Moonshot model since distill last worked is evidence the account was
// answering a caller, and a day on which all three stopped together is one
// shared cause rather than three separate ones.
//
// `triage_log.created_at` is the stronger of the two, because triage writes a
// row for every paper it judges, a discard included. `claim_links.created_at`
// is weaker on purpose and is published anyway: interpret writes an edge only
// when the model finds a relation, so a quiet run leaves no row and an absent
// edge is not an absent run. The judgement in tools/delivery_health.py takes
// either stage's freshness as enough and names which one it read, and the
// model each stage wrote on is published beside it, because every corpus stage
// falls back to Groq's free tier and a fallback that carried the small stages
// is a different finding from an account that answered them.

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

// One sibling stage's newest row: when it was written and what wrote it.
// `null` for the stage means the table is empty, which is a fact, and the
// whole `siblings` block is null when the query could not run at all.
//
// The model comes out of `triage_log.model` as it stands and out of
// `claim_links.method` with its prompt sha dropped, because `method` is
// `model@sha` and the sha is not this endpoint's to publish.
function stage(row) {
  if (row === null || row === undefined) return null;
  const wrote = iso(row.newest);
  const model = text(row.model, 120);
  return { newest: wrote, model: model === null ? null : model.split("@")[0] };
}

export function buildReceipt({ digest, papers, distilled, claims, siblings,
                               queues, deploy, observedAt }) {
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
      // When distill last marked a paper read, which is not the same question
      // as when it last wrote a claim. `null` means no paper carries the
      // marker, and the judgement treats that as a fact it does not have
      // rather than as a stage that never ran, because an absent field on an
      // older receipt arrives here as the same null.
      distilled_newest: iso(distilled),
    },
    // What the two stages either side of distill last wrote, and which model
    // wrote it. A block of its own rather than two more fields on `pipeline`,
    // the same shape `queues` has and for the same reason: these are a cause
    // rather than a clock, and `null` means the site could not run the query.
    //
    // The model is the half that makes this decisive. Every corpus stage calls
    // Kimi through pipeline/llm.py and every one of them falls back to Groq's
    // free tier when Moonshot refuses (ADR-39), so a sibling that wrote
    // something proves a model answered and does not by itself say which
    // account. `triage_log.model` and `claim_links.method` record the one that
    // did, and those two answers send a reader to different places: Moonshot
    // answering means distill's own cron, deploy or caps, and the Groq
    // fallback carrying the small stages means the shared account may be
    // refusing everybody, with distill the one stage whose 250,000-character
    // payload the free tier cannot take.
    //
    // `method` is `model@prompt_sha` and only the model half is published. The
    // sha is the same class of field as `digests.prompt_sha`, which this
    // endpoint has never published and tests/delivery.test.mjs holds it to.
    siblings: siblings == null ? null : {
      triage: stage(siblings.triage),
      interpret: stage(siblings.interpret),
    },
    // How many rows are waiting at each stage, which is the fact that turns
    // "claims has not moved in three days" into a cause. A stalled stage with
    // an empty queue has nothing to read and the gap is upstream of it. A
    // stalled stage with a deep queue has work and is not doing it, which is
    // the only one of the two that needs the owner's `modal app logs`. The
    // ledger carried that question as urgent on 2026-10-09 and closed it with
    // "narrowing it further is not a matter of trying harder from here",
    // because the depth was readable only with a credential no seat holds.
    //
    // Counts and no identifiers, so this stays metadata under rule 2 above: a
    // number of waiting papers names no paper. `null` means the query could not
    // be run, the same contract as `deploy`, and never zero. Zero is a queue
    // that was read and is empty, which is half of the diagnosis.
    queues: queues == null ? null : {
      triage_pending: count(queues.triage_pending),
      distill_pending: count(queues.distill_pending),
      interpret_pending: count(queues.interpret_pending),
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
