import { neon } from "@neondatabase/serverless";
import { buildReceipt } from "./delivery-core.js";

// Reads the facts the delivery receipt publishes.
//
// Fails closed, the same contract as lib/entitlement.js and lib/graph-live.js,
// and returns `{ receipt }` or `{ reason }`, never a receipt full of nulls. The
// route turns a reason into a 503, because "the press has printed nothing" and
// "this endpoint could not look" are different facts and the whole point of
// tools/delivery_health.py's third state is not to confuse them.
//
// The two failures are kept apart on purpose. A missing DATABASE_URL in this
// project's environment is one setting away from working and a query that
// throws is not, and a seat reading this from a sandbox cannot see the
// environment, so this field is its only diagnosis.
//
// Six queries, and no parameter from the request reaches any of them. Two are
// cheap by construction: `digests` is ordered on its unique `week` index and
// `deploy_runtime` has one row per scheduled job. The two `max()` reads over
// `papers` and `claims` have no index to use and scan, which is thousands of
// rows rather than millions today and is the same pair of queries
// `tools/delivery_health.py` has always run against this database. The route
// caches at the edge, so repeat traffic does not reach Neon at all. If either
// table grows enough for the scan to matter, the answer is an index on the two
// timestamps rather than a different endpoint.
//
// The queue depths are the most expensive one here, so it
// is worth saying what it costs. `distill_queue` joins `papers` to
// `latest_triage`, which is a `distinct on` over `triage_log`, and the triage
// backlog count is an anti-join over the same pair. That is two passes over
// thousands of rows rather than millions, once per five minutes per edge
// region, against a surface whose absence left a stalled pipeline undiagnosable
// for three days. It is one round trip and three scalars come back.
//
// The sixth is the sibling markers, added in version 4, and it is two more
// unindexed `max()` reads in one statement over two tables of the same size as
// the two above. Its own comment at the call site says what it buys.
export async function loadDeliveryReceipt() {
  const url = process.env.DATABASE_URL;
  if (!url) return { reason: "DATABASE_URL is not set in the site's environment" };

  try {
    const sql = neon(url);

    // `order by week desc` and not `created_at`, so this agrees with
    // tools/delivery_health.py's own query. A backfilled week would otherwise
    // make the two disagree about which issue is newest.
    const digests = await sql`
      select week, model, created_at
      from digests
      order by week desc
      limit 1
    `;
    // One statement over `papers` and two scalars back, rather than two scans
    // of the same table for two of its columns.
    //
    // `distilled_at` is the second half of the stall diagnosis. `distill_queue`
    // says how much was waiting; this says whether the stage read any of it.
    // pipeline/distill.py sets the marker on a paper in the same committed loop
    // that writes that paper's claims, so a `distilled_at` that moved while
    // `claims` stood still means the stage ran and extracted nothing, and one
    // that stood still with it means the stage never reached a paper at all.
    // Those two have different first steps and the depth alone cannot tell them
    // apart, which is where the 2026-10-10 reading of the queues ran out.
    const papers = await sql`
      select max(fetched_at) as newest, max(distilled_at) as distilled
      from papers
    `;
    const claims = await sql`select max(created_at) as newest from claims`;

    // The two sibling stages' output markers, which is the fact that says
    // whether the provider is answering anybody at all. Distill, triage and
    // interpret all call Kimi on one organization key and distill runs last,
    // so a triage row written after distill last worked rules out the account
    // and leaves this one job's cron, deploy and caps. Fail-soft for the same
    // reason the depths are, and nulls rather than an absent object: a reader
    // that cannot tell "no edge yet" from "could not look" would eventually
    // name the provider on no evidence.
    //
    // Two scalar subqueries in one statement, so this is one round trip over
    // two tables of thousands of rows rather than two. Neither column is
    // indexed, which is the same trade `papers` and `claims` already make
    // above, and the route's five-minute edge cache is what keeps it off Neon.
    let siblings = null;
    try {
      const rows = await sql`
        select (select max(created_at) from triage_log)  as triaged,
               (select max(created_at) from claim_links) as linked
      `;
      siblings = rows[0] ?? null;
    } catch {
      siblings = null;
    }

    // The queue depths: how many rows are waiting at each stage. Same
    // fail-soft contract as `deploy` below and for the same reason. These are
    // views in db/schema.sql, `apply_schema` is a hand step, and losing the
    // press and the corpus timestamps because a view is absent would be the
    // wrong trade. One statement so the three counts are one round trip.
    //
    // `latest_triage` rather than `triage_log` for the backlog, so a paper
    // triaged twice counts once, which is the same view `distill_queue` joins.
    let queues = null;
    try {
      const rows = await sql`
        select
          (select count(*) from papers p
            where not exists (
              select 1 from latest_triage t where t.paper_id = p.id
            )) as triage_pending,
          (select count(*) from distill_queue)   as distill_pending,
          (select count(*) from interpret_queue) as interpret_pending
      `;
      queues = rows[0] ?? null;
    } catch {
      // null, not zeroes. A queue of zero is a real and useful fact (the stage
      // has nothing to read), so a failed read must not be able to claim it.
      queues = null;
    }

    // deploy_runtime lands with the drift guard and `apply_schema` is a hand
    // step, so a missing table is a state this really meets. It is the one
    // query allowed to fail without failing the receipt: the press and the
    // pipeline are the surfaces the ledger calls urgent, and losing them
    // because a newer table is absent would be the wrong trade.
    let deploy = null;
    try {
      deploy = await sql`
        select app, runtime_sha, entrypoint, file_count,
               recorded_at, first_seen_at, notified_at
        from deploy_runtime
        order by app
      `;
    } catch {
      // null, not []: an empty array would tell the drift guard that every job
      // has failed to report, and it would raise the alarm this endpoint
      // exists to make readable.
      deploy = null;
    }

    return {
      receipt: buildReceipt({
        digest: digests[0] ?? null,
        papers: papers[0]?.newest ?? null,
        distilled: papers[0]?.distilled ?? null,
        claims: claims[0]?.newest ?? null,
        triaged: siblings?.triaged ?? null,
        linked: siblings?.linked ?? null,
        queues,
        deploy,
        observedAt: new Date(),
      }),
    };
  } catch (error) {
    // The error's class and nothing else. A Neon error's message carries the
    // host and the role it failed to authenticate, which is not for a public
    // response, and the reader of this field only needs to know that a query
    // failed rather than that a setting is absent.
    return { reason: `a query failed: ${error?.name ?? "Error"}` };
  }
}
