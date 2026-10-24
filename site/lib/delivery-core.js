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

export const RECEIPT_VERSION = 6;

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

// Version 5 adds `payments` and removes nothing, so every version before it
// stays readable on the same rule. It exists because the till had no watch at
// all. Polar is the Merchant of Record, so this product's only knowledge that
// anybody paid arrives at /api/polar-webhook, and the two outcomes where a
// verified payment cannot be turned into access both ended in a function log
// that nothing in this org reads. `payment_exceptions` gives them a row and
// this block is how a seat with no credential counts the open ones.
//
// Counts, codes and timestamps only. The row itself holds the buyer's address
// and the Polar ids, because the owner needs them to invite the person or find
// the charge, and not one of them appears here: rule 2 above is why, and this
// is the first block on this receipt where breaking it would publish a
// customer rather than a number.
// Version 6 adds `unreadable` and removes nothing. It exists because version 5
// went live and answered `payments: null`, which is the right answer and not a
// usable one. Four blocks on this receipt fail soft, so each of them has two
// ways to be null: the table is not there yet, or the query broke. Those two
// send a reader to different places, and until now neither reader could tell
// them apart, so `tools/delivery_health.py` has reported the till as `unknown`
// in every standup since the block shipped and nobody could say what would
// close it. The answer was a hand step the whole time, `modal run
// pipeline/db_setup.py::apply_schema`, and the receipt knew and did not say.
//
// A closed vocabulary and never an error message. `UNREADABLE_REASONS` is the
// whole of it, three strings this codebase chose, so a Neon error carrying the
// host and the role it failed to authenticate cannot reach a public response
// through this field. That is rule 2 above applied to a diagnosis rather than
// to a row: the classification is metadata, the message it came from is not.
//
// Absent rather than empty when everything read, so the ordinary receipt does
// not grow a block of nulls and a reader can treat the field's presence as the
// finding it is.
export const UNREADABLE_REASONS = Object.freeze([
  // Postgres 42P01. The table or view is not in this database, which on this
  // project means `apply_schema` has not been run since the migration that
  // added it landed. One command closes it and the guard names the command.
  "no such table",
  // Postgres 42703. A column the query asks for is absent, so the schema is
  // behind in a narrower way than a missing table and the same hand fixes it.
  "no such column",
  // Everything else, which is the state where the first step is to read a log
  // rather than to run a migration.
  "query failed",
]);

function reason(value) {
  return UNREADABLE_REASONS.includes(value) ? value : "query failed";
}

export function buildReceipt({ digest, papers, distilled, claims, siblings,
                               queues, deploy, payments, unreadable, observedAt }) {
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
    // The till's open exceptions: verified payments that did not become
    // access. `null` means the query could not be run, which is the state a
    // site whose `payment_exceptions` table has not been applied yet is
    // really in, and it must not read as zero. Zero is the good news and it
    // is only good news when somebody looked.
    //
    // `needs_a_hand` is the half that decides the verdict. A deferred event
    // is one Polar will bring back by itself, so a few of those at any moment
    // is the system working. A refused one never clears on its own: nobody
    // holds that address at Clerk, or two accounts do, and either way a
    // person has paid and is waiting on the owner. Those two numbers want
    // different reactions, so they are published separately rather than
    // summed here and guessed at by the reader.
    payments: payments == null ? null : {
      unresolved: count(payments.unresolved),
      needs_a_hand: count(payments.needs_a_hand),
      // How long the oldest open one has been open, which is the number that
      // turns a count into an age. `min(occurred_at)`, so a row retried for a
      // day reports the day rather than the retry.
      oldest_unresolved_at: iso(payments.oldest),
      newest_unresolved_at: iso(payments.newest),
      // Which refusals they are, so the headline can name the job rather than
      // only the number. The codes are this codebase's own closed vocabulary
      // (polar-core.js EXCEPTION_CODES, checked by db/schema.sql), so they
      // name a category and never a customer.
      codes: Array.isArray(payments.codes)
        ? payments.codes
            .map((row) => ({ code: text(row.code, 32), n: count(row.n) }))
            .filter((row) => row.code !== null)
        : [],
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
    // Why any of the four blocks above is null, for the ones that are. Keyed by
    // the block's own name on this receipt, so a reader that finds
    // `payments: null` looks up `unreadable.payments` and gets the reason
    // rather than a guess.
    //
    // Only blocks that failed appear. An absent key means the block read, which
    // for `payments` means zero open exceptions is the good news it looks like.
    ...unreadableBlock(unreadable),
  };
}

// The reasons, filtered to the blocks this receipt actually publishes and to
// the vocabulary above, or nothing at all.
//
// Built by name like every other field here, so a caller that passes a whole
// error object, or a key for a block that does not exist, publishes neither.
function unreadableBlock(unreadable) {
  if (unreadable === null || unreadable === undefined) return {};
  const named = {};
  for (const block of ["siblings", "queues", "payments", "deploy"]) {
    const given = unreadable[block];
    if (given === null || given === undefined) continue;
    named[block] = reason(given);
  }
  return Object.keys(named).length === 0 ? {} : { unreadable: named };
}
